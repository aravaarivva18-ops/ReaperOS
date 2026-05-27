import os
import sys
import sqlite3
import pytest
import aiosqlite

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))

from engine.memory import MemoryBrain, Command

class MockCommand(Command):
    def __init__(self, key, value):
        self.key = key
        self.value = value
    async def execute(self):
        pass
    async def undo(self):
        pass

@pytest.fixture
def test_db(tmp_path, mocker):
    db_file = str(tmp_path / "test_memory.db")
    mocker.patch("engine.memory.DB_PATH", db_file)
    
    # Initialize schema
    conn = sqlite3.connect(db_file)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS memory_pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        tier TEXT NOT NULL,
        payload TEXT NOT NULL,
        embedding BLOB
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS undo_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        cmd_class TEXT NOT NULL,
        state TEXT NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS task_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        action TEXT NOT NULL,
        outcome TEXT NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        metric_name TEXT NOT NULL,
        value REAL NOT NULL,
        details TEXT
    )
    """)
    conn.commit()
    conn.close()
    return db_file

@pytest.mark.anyio
async def test_get_node_count_initially_zero(test_db):
    count = await MemoryBrain.get_node_count()
    assert count == 0

@pytest.mark.anyio
async def test_log_task_writes_entry(test_db):
    await MemoryBrain.log_task("run_cleanup", "SUCCESS")
    
    async with aiosqlite.connect(test_db) as db:
        db.row_factory = sqlite3.Row
        async with db.execute("SELECT * FROM task_log") as cursor:
            rows = await cursor.fetchall()
            assert len(rows) == 1
            assert rows[0]["action"] == "run_cleanup"
            assert rows[0]["outcome"] == "SUCCESS"

@pytest.mark.anyio
async def test_push_and_pop_undo_stack(test_db):
    cmd = MockCommand("session_id", "42")
    await MemoryBrain.push_undo(cmd)
    
    # Verify it exists in DB
    async with aiosqlite.connect(test_db) as db:
        db.row_factory = sqlite3.Row
        async with db.execute("SELECT * FROM undo_log") as cursor:
            rows = await cursor.fetchall()
            assert len(rows) == 1
            assert rows[0]["cmd_class"] == "MockCommand"
            assert "42" in rows[0]["state"]
            
    # Pop the command
    popped = await MemoryBrain.pop_undo()
    assert popped is True
    
    # Confirm it is removed
    async with aiosqlite.connect(test_db) as db:
        async with db.execute("SELECT COUNT(*) FROM undo_log") as cursor:
            row = await cursor.fetchone()
            assert row[0] == 0
