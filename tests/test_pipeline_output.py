#!/usr/bin/env python3
"""
TDD-тесты для tools/run_analysis_pipeline.py
Покрывает: ключи результата, запись в dream_logs, latency < 10s
"""
import sys
import os
import time
import sqlite3
import pytest

# Убеждаемся, что project root в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_analysts(mocker):
    """Подменяем реальные аналитики — они I/O-bound и требуют scratch-файлов."""
    # seo_analyst.main() → ничего не возвращает, но пишет JSON
    mocker.patch("tools.run_analysis_pipeline.run_seo_analyst", return_value={
        "status": "ok",
        "cards_audited": 5,
        "avg_seo_score": 7.2
    })
    mocker.patch("tools.run_analysis_pipeline.run_logistic_analyst", return_value={
        "status": "ok",
        "items_analyzed": 10,
        "out_of_stock_count": 2
    })
    mocker.patch("tools.run_analysis_pipeline.run_secrets_analyzer", return_value={
        "status": "ok",
        "secrets_found": 0
    })


@pytest.fixture
def clean_db(tmp_path, mocker):
    """Направляем knowledge_brain на временную БД."""
    test_db = str(tmp_path / "test.db")
    mocker.patch("tools.knowledge_brain.DB_PATH", test_db)
    # Переинициализируем схему в тестовой БД
    import tools.knowledge_brain as kb
    mocker.patch.object(kb, "DB_PATH", test_db)
    # Создаём схему вручную
    conn = sqlite3.connect(test_db)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dream_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            task TEXT NOT NULL,
            status TEXT NOT NULL,
            output TEXT
        )
    """)
    conn.commit()
    conn.close()
    return test_db


# ---------------------------------------------------------------------------
# Тест 1: Результат содержит все 3 аналитика
# ---------------------------------------------------------------------------

def test_pipeline_returns_all_keys(mock_analysts):
    """DAMP: pipeline должен вернуть словарь с ключами всех трёх аналитиков."""
    from tools.run_analysis_pipeline import run_pipeline

    result = run_pipeline()

    assert isinstance(result, dict), "Результат должен быть dict"
    assert "seo_analyst" in result, "Ключ 'seo_analyst' отсутствует в результате"
    assert "logistic_analyst" in result, "Ключ 'logistic_analyst' отсутствует в результате"
    assert "secrets_analyzer" in result, "Ключ 'secrets_analyzer' отсутствует в результате"


# ---------------------------------------------------------------------------
# Тест 2: Pipeline пишет записи в dream_logs
# ---------------------------------------------------------------------------

def test_pipeline_writes_to_db(mock_analysts, clean_db, mocker):
    """DAMP: после run_pipeline() таблица dream_logs содержит записи."""
    import tools.knowledge_brain as kb
    mocker.patch.object(kb, "DB_PATH", clean_db)

    from tools import run_analysis_pipeline
    mocker.patch.object(run_analysis_pipeline, "add_dream_log",
                        side_effect=lambda task, status, output: _insert_log(clean_db, task, status, output))

    from tools.run_analysis_pipeline import run_pipeline
    run_pipeline()

    conn = sqlite3.connect(clean_db)
    rows = conn.execute("SELECT * FROM dream_logs").fetchall()
    conn.close()

    assert len(rows) > 0, "dream_logs пуст после run_pipeline() — запись не произошла"


def _insert_log(db_path, task, status, output):
    """Вспомогательная вставка для тестовой БД."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO dream_logs (task, status, output) VALUES (?, ?, ?)",
        (task, status, output)
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Тест 3: Latency < 10 секунд (с моками)
# ---------------------------------------------------------------------------

def test_pipeline_latency(mock_analysts):
    """DAMP: pipeline с моками должен завершиться менее чем за 10 секунд."""
    from tools.run_analysis_pipeline import run_pipeline

    start = time.perf_counter()
    run_pipeline()
    elapsed = time.perf_counter() - start

    assert elapsed < 10.0, (
        f"Pipeline занял {elapsed:.2f}s — превышен лимит 10s. "
        "Возможна блокировка потоков."
    )
