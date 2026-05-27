#!/usr/bin/env python3
"""
tdd_pipeline_runner.py — Red-Green-Refactor цикл для ReaperOS.

Принимает список тест-файлов, запускает pytest и определяет фазу:
  RED    → есть FAILED тесты
  GREEN  → все тесты PASSED
  REFACTOR → все GREEN + проверяет coverage (pytest-cov)

Результат пишется в knowledge_brain (dream_logs).
Возвращает: {"phase": "GREEN"|"RED", "passed": N, "failed": N, "coverage": float|None}
"""

import json
import logging
import os
import re
import subprocess
import sys
import time
from typing import Optional

# ---------------------------------------------------------------------------
# Logging setup (Observability First)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
log = logging.getLogger("tdd_pipeline_runner")

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

VENV_PYTEST = os.path.join(PROJECT_ROOT, ".reaper_venv", "bin", "pytest")
# Fallback: системный pytest
PYTEST_BIN = VENV_PYTEST if os.path.exists(VENV_PYTEST) else "pytest"

from tools.knowledge_brain import add_dream_log  # noqa: E402


# ---------------------------------------------------------------------------
# Parse pytest output
# ---------------------------------------------------------------------------

def _parse_pytest_output(stdout: str, stderr: str) -> dict:
    """Извлекает N passed / N failed из вывода pytest."""
    passed = 0
    failed = 0
    errors = 0

    # Ищем строку вида: "5 passed, 2 failed in 1.23s" или "3 passed in 0.45s"
    summary_pattern = re.compile(
        r"(?:(\d+) passed)?.*?(?:(\d+) failed)?.*?(?:(\d+) error)?"
    )
    for line in stdout.splitlines():
        if "passed" in line or "failed" in line or "error" in line:
            m = re.search(r"(\d+) passed", line)
            if m:
                passed = int(m.group(1))
            m = re.search(r"(\d+) failed", line)
            if m:
                failed = int(m.group(1))
            m = re.search(r"(\d+) error", line)
            if m:
                errors += int(m.group(1))

    return {"passed": passed, "failed": failed + errors}


def _parse_coverage(stdout: str) -> Optional[float]:
    """Извлекает общий процент покрытия из вывода pytest-cov."""
    # Ищем строку "TOTAL ... 87%"
    m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", stdout)
    if m:
        return float(m.group(1))
    return None


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------

def run_tdd_cycle(
    test_files: list[str],
    check_coverage: bool = True,
    coverage_threshold: float = 60.0
) -> dict:
    """
    Запускает RED → GREEN → REFACTOR цикл для переданных тест-файлов.

    Args:
        test_files: список путей к тест-файлам (абсолютные или относительные к PROJECT_ROOT)
        check_coverage: включить проверку покрытия (фаза REFACTOR)
        coverage_threshold: минимальный % покрытия для признания REFACTOR успешным

    Returns:
        {
          "phase": "GREEN" | "RED",
          "passed": int,
          "failed": int,
          "coverage": float | None,
          "coverage_ok": bool | None,
          "output": str
        }
    """
    if not test_files:
        log.error("tdd_pipeline_runner: no test files provided")
        return {"phase": "RED", "passed": 0, "failed": 0, "error": "no test files"}

    t0 = time.perf_counter()

    # Резолвим пути
    resolved = []
    for tf in test_files:
        p = tf if os.path.isabs(tf) else os.path.join(PROJECT_ROOT, tf)
        if not os.path.exists(p):
            log.warning("Test file not found: %s", p)
        resolved.append(p)

    # ---------------------------------------------------------------------------
    # RED / GREEN phase: запуск pytest
    # ---------------------------------------------------------------------------
    log.info("TDD Runner [RED/GREEN]: running pytest on %d file(s)", len(resolved))

    cmd_run = [PYTEST_BIN, "-v", "--tb=short"] + resolved
    proc = subprocess.run(
        cmd_run,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    stdout_run = proc.stdout
    stderr_run = proc.stderr

    counts = _parse_pytest_output(stdout_run, stderr_run)
    passed = counts["passed"]
    failed = counts["failed"]

    phase = "GREEN" if failed == 0 and proc.returncode == 0 else "RED"

    elapsed_ms = (time.perf_counter() - t0) * 1000
    if elapsed_ms > 500:
        log.warning("pytest latency=%.1fms (>500ms)", elapsed_ms)

    log.info("TDD Runner phase=%s passed=%d failed=%d latency=%.1fms",
             phase, passed, failed, elapsed_ms)

    # Вывод в лог (Observability)
    if proc.returncode != 0:
        log.error("pytest stderr: %s", stderr_run[:500] if stderr_run else "—")

    result: dict = {
        "phase": phase,
        "passed": passed,
        "failed": failed,
        "coverage": None,
        "coverage_ok": None,
        "output": stdout_run[-2000:] if len(stdout_run) > 2000 else stdout_run
    }

    # ---------------------------------------------------------------------------
    # REFACTOR phase: coverage (только если GREEN)
    # ---------------------------------------------------------------------------
    if phase == "GREEN" and check_coverage:
        log.info("TDD Runner [REFACTOR]: checking coverage (threshold=%.0f%%)", coverage_threshold)

        t_cov = time.perf_counter()
        cmd_cov = [
            PYTEST_BIN,
            "--cov=tools",
            "--cov-report=term-missing",
            "--tb=no",
            "-q"
        ] + resolved

        proc_cov = subprocess.run(
            cmd_cov,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        cov_elapsed_ms = (time.perf_counter() - t_cov) * 1000
        if cov_elapsed_ms > 500:
            log.warning("coverage check latency=%.1fms (>500ms)", cov_elapsed_ms)

        coverage = _parse_coverage(proc_cov.stdout)
        coverage_ok = (coverage is not None and coverage >= coverage_threshold)

        result["coverage"] = coverage
        result["coverage_ok"] = coverage_ok

        if coverage is not None:
            log.info("Coverage: %.0f%% (threshold=%.0f%%, ok=%s)",
                     coverage, coverage_threshold, coverage_ok)
        else:
            log.warning("Could not parse coverage from pytest-cov output")

    # ---------------------------------------------------------------------------
    # Запись в knowledge_brain (dream_logs)
    # ---------------------------------------------------------------------------
    log_status = "GREEN" if phase == "GREEN" else "RED"
    add_dream_log(
        task="tdd_pipeline_runner",
        status=log_status,
        output=json.dumps({
            "phase": phase,
            "passed": passed,
            "failed": failed,
            "coverage": result["coverage"],
            "coverage_ok": result["coverage_ok"],
            "test_files": test_files
        }, ensure_ascii=False)
    )

    return result


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TDD Pipeline Runner — Red/Green/Refactor")
    parser.add_argument(
        "test_files",
        nargs="+",
        help="Пути к тест-файлам (например: tests/test_pipeline_output.py)"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Пропустить проверку coverage (только RED/GREEN)"
    )
    parser.add_argument(
        "--coverage-threshold",
        type=float,
        default=60.0,
        help="Минимальный %% покрытия для REFACTOR-фазы (default: 60)"
    )
    args = parser.parse_args()

    output = run_tdd_cycle(
        test_files=args.test_files,
        check_coverage=not args.no_coverage,
        coverage_threshold=args.coverage_threshold
    )

    print("\n=== TDD Pipeline Runner Results ===")
    print(f"  Phase:    {output['phase']}")
    print(f"  Passed:   {output['passed']}")
    print(f"  Failed:   {output['failed']}")
    if output.get("coverage") is not None:
        cov_ok = "✅" if output.get("coverage_ok") else "❌"
        print(f"  Coverage: {output['coverage']}% {cov_ok}")
    print("\n--- Output tail ---")
    print(output.get("output", "")[-500:])

    sys.exit(0 if output["phase"] == "GREEN" else 1)
