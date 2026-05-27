import aiosqlite
import sqlite3
import json
import os
import time
import sys
from datetime import datetime
from config import DB_PATH, BASE_DIR
import abc
import contextlib

class Command(abc.ABC):
    @abc.abstractmethod
    async def execute(self): pass
    @abc.abstractmethod
    async def undo(self): pass

class MemoryBrain:
    _undo_stack = []
    
    @classmethod
    @contextlib.asynccontextmanager
    async def get_db(cls):
        start_time = time.perf_counter()
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = sqlite3.Row
            await db.execute("PRAGMA journal_mode = WAL")
            await db.execute("PRAGMA synchronous = NORMAL")
            duration = time.perf_counter() - start_time
            if duration > 0.1:
                sys.stderr.write(f"\033[93m[TELEMETRY WARNING] DB Connection took {duration:.4f}s (SLI limit: 0.1s)\033[0m\n")
                sys.stderr.flush()
                try:
                    await db.execute("INSERT INTO telemetry (metric_name, value, details) VALUES (?, ?, ?)", 
                                     ("db_connection_latency", duration, f"DB Connection took {duration:.4f}s"))
                    await db.commit()
                except Exception as e:
                    sys.stderr.write(f"Failed to record db latency telemetry: {e}\n")
            yield db

    @classmethod
    async def close(cls):
        # Clean shutdown interface compatibility
        pass

    @classmethod
    async def push_undo(cls, command: Command):
        async with cls.get_db() as db:
            state = json.dumps(command.__dict__)
            await db.execute("INSERT INTO undo_log (cmd_class, state) VALUES (?, ?)", (command.__class__.__name__, state))
            await db.commit()

    @classmethod
    async def pop_undo(cls):
        async with cls.get_db() as db:
            async with db.execute("SELECT id, cmd_class, state FROM undo_log ORDER BY id DESC LIMIT 1") as cursor:
                row = await cursor.fetchone()
                if row:
                    cmd_id, cmd_class, state = row
                    await db.execute("DELETE FROM undo_log WHERE id = ?", (cmd_id,))
                    await db.commit()
                    return True
            return False

    @classmethod
    async def log_task(cls, action, outcome="DONE"):
        async with cls.get_db() as db:
            await db.execute("INSERT INTO task_log (action, outcome) VALUES (?, ?)", (action, outcome))
            await db.commit()

    @classmethod
    async def get_node_count(cls):
        async with cls.get_db() as db:
            async with db.execute("SELECT COUNT(*) FROM memory_pages") as cursor:
                row = await cursor.fetchone()
                return row[0]

    @classmethod
    async def distill_memory(cls):
        """Compacts context logs into a summary."""
        log_path = os.path.join(BASE_DIR, ".reaper_brain.log")
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                content = f.read()[-5000:]
            summary_path = os.path.join(BASE_DIR, ".reaper_context_summary")
            with open(summary_path, "w") as f:
                f.write(f"--- DISTILLED AT {datetime.now().isoformat()} ---\n{content[-2000:]}")
            print(f"[Distillation] Context compacted to {summary_path}")
