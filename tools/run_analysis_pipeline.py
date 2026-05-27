#!/usr/bin/env python3
"""
run_analysis_pipeline.py — Параллельная оркестрация аналитиков ReaperOS.

Запускает параллельно:
  - seo_analyst      → анализ SEO-карточек
  - logistic_analyst → анализ складских остатков
  - secrets_analyzer → сканер утечек ключей/токенов

Каждый результат пишет в knowledge_brain (dream_logs).
Latency > 500ms → WARNING в лог.
Возвращает: dict {analyst_name: result_dict}
"""

import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

# ---------------------------------------------------------------------------
# Logging setup (Observability First)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
log = logging.getLogger("run_analysis_pipeline")

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

SCRATCH_DIR = os.getenv("SCRATCH_DIR") or os.path.join(PROJECT_ROOT, "scratch")

# ---------------------------------------------------------------------------
# Imports from project modules
# ---------------------------------------------------------------------------
from tools.knowledge_brain import add_dream_log  # noqa: E402

# ---------------------------------------------------------------------------
# Per-analyst runner wrappers
# Each returns a dict with at minimum {"status": "ok" | "error"}.
# ---------------------------------------------------------------------------

def run_seo_analyst() -> dict:
    """Запускает seo_analyst.main() и читает результирующий JSON."""
    t0 = time.perf_counter()
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "seo_analyst",
            os.path.join(PROJECT_ROOT, "tools", "seo_analyst.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()

        report_path = os.path.join(SCRATCH_DIR, "seo_report.json")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cards = data.get("cards", [])
            return {
                "status": "ok",
                "cards_audited": len(cards),
                "avg_seo_score": round(
                    sum(c.get("seo_score", 0) for c in cards) / len(cards), 2
                ) if cards else 0.0
            }
        return {"status": "ok", "note": "no report file (empty scratch)"}

    except Exception as exc:
        log.error("seo_analyst failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
    finally:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        if elapsed_ms > 500:
            log.warning("seo_analyst latency=%.1fms (>500ms threshold)", elapsed_ms)
        else:
            log.info("seo_analyst latency=%.1fms", elapsed_ms)


def run_logistic_analyst() -> dict:
    """Запускает logistic_analyst.main() и читает результирующий JSON."""
    t0 = time.perf_counter()
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "logistic_analyst",
            os.path.join(PROJECT_ROOT, "tools", "logistic_analyst.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.main()

        report_path = os.path.join(SCRATCH_DIR, "logistic_report.json")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("items", {})
            out_of_stock = sum(
                1 for v in items.values() if v.get("status") == "OUT_OF_STOCK"
            )
            return {
                "status": "ok",
                "items_analyzed": len(items),
                "out_of_stock_count": out_of_stock
            }
        return {"status": "ok", "note": "no report file (empty scratch)"}

    except Exception as exc:
        log.error("logistic_analyst failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
    finally:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        if elapsed_ms > 500:
            log.warning("logistic_analyst latency=%.1fms (>500ms threshold)", elapsed_ms)
        else:
            log.info("logistic_analyst latency=%.1fms", elapsed_ms)


def run_secrets_analyzer() -> dict:
    """Запускает secrets_analyzer.scan() и возвращает сводку."""
    t0 = time.perf_counter()
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "secrets_analyzer",
            os.path.join(PROJECT_ROOT, "tools", "secrets_analyzer.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # secrets_analyzer может иметь scan() или main()
        # ВАЖНО: secrets_analyzer.main() вызывает sys.exit() — перехватываем
        if hasattr(module, "scan"):
            findings = module.scan(PROJECT_ROOT)
            return {
                "status": "ok",
                "secrets_found": len(findings) if isinstance(findings, list) else 0
            }
        elif hasattr(module, "main"):
            try:
                module.main()
                return {"status": "ok", "secrets_found": 0}
            except SystemExit as se:
                # secrets_analyzer завершается через sys.exit(0/1)
                code = se.code if se.code is not None else 0
                if code == 0:
                    return {"status": "ok", "secrets_found": 0}
                else:
                    log.warning("secrets_analyzer exited with code %s (secrets found!)", code)
                    return {"status": "warning", "secrets_found": -1, "exit_code": code}
        return {"status": "ok", "note": "no entry point found"}

    except Exception as exc:
        log.error("secrets_analyzer failed: %s", exc, exc_info=True)
        return {"status": "error", "error": str(exc)}
    finally:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        if elapsed_ms > 500:
            log.warning("secrets_analyzer latency=%.1fms (>500ms threshold)", elapsed_ms)
        else:
            log.info("secrets_analyzer latency=%.1fms", elapsed_ms)


# ---------------------------------------------------------------------------
# Registry — позволяет легко добавлять аналитиков
# ---------------------------------------------------------------------------
ANALYSTS = {
    "seo_analyst": run_seo_analyst,
    "logistic_analyst": run_logistic_analyst,
    "secrets_analyzer": run_secrets_analyzer,
}

PIPELINE_TIMEOUT_S = 120  # макс. время ожидания всех аналитиков


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_pipeline(analysts: dict | None = None) -> dict:
    """
    Параллельно запускает всех аналитиков через ThreadPoolExecutor.
    Пишет каждый результат в knowledge_brain.dream_logs.
    Возвращает: {analyst_name: result_dict}

    ВАЖНО: если analysts=None, функции берутся из текущего состояния модуля
    (не из статического ANALYSTS dict) — это позволяет pytest-mock патчить их.
    """
    import sys as _sys
    _self = _sys.modules[__name__]

    if analysts is None:
        # Динамически читаем из текущего состояния модуля — мок-friendly
        registry = {
            name: getattr(_self, fn_name)
            for name, fn_name in [
                ("seo_analyst",       "run_seo_analyst"),
                ("logistic_analyst",  "run_logistic_analyst"),
                ("secrets_analyzer",  "run_secrets_analyzer"),
            ]
        }
    else:
        registry = analysts

    results: dict = {}

    pipeline_start = time.perf_counter()
    log.info("Pipeline start: running %d analysts in parallel", len(registry))

    with ThreadPoolExecutor(max_workers=len(registry)) as executor:
        future_to_name = {
            executor.submit(fn): name
            for name, fn in registry.items()
        }


        for future in as_completed(future_to_name, timeout=PIPELINE_TIMEOUT_S):
            name = future_to_name[future]
            try:
                result = future.result()
                results[name] = result
                status = result.get("status", "unknown")
                log.info("Analyst '%s' finished: status=%s", name, status)

                # Observability: пишем в dream_logs
                add_dream_log(
                    task=f"pipeline:{name}",
                    status=status,
                    output=json.dumps(result, ensure_ascii=False)
                )

            except TimeoutError:
                log.error("Analyst '%s' timed out after %ss", name, PIPELINE_TIMEOUT_S)
                results[name] = {"status": "timeout"}
                add_dream_log(
                    task=f"pipeline:{name}",
                    status="timeout",
                    output=f"Timeout after {PIPELINE_TIMEOUT_S}s"
                )
            except Exception as exc:
                log.error("Analyst '%s' raised exception: %s", name, exc, exc_info=True)
                results[name] = {"status": "error", "error": str(exc)}
                add_dream_log(
                    task=f"pipeline:{name}",
                    status="error",
                    output=str(exc)
                )

    pipeline_elapsed_ms = (time.perf_counter() - pipeline_start) * 1000
    if pipeline_elapsed_ms > 500:
        log.warning("Pipeline total latency=%.1fms (>500ms threshold)", pipeline_elapsed_ms)
    else:
        log.info("Pipeline total latency=%.1fms", pipeline_elapsed_ms)

    log.info("Pipeline complete: %s", {k: v.get("status") for k, v in results.items()})
    return results


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    output = run_pipeline()
    print("\n=== Pipeline Results ===")
    for name, result in output.items():
        print(f"  {name}: {result}")
