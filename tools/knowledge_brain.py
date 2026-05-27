#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime

# Load dotenv manually
def load_db_path():
    # default path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db.sqlite")
    # check .env in parent dir
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.strip().startswith("REAPER_DB_PATH="):
                    val = line.strip().split("=", 1)[1].strip().strip("'").strip('"')
                    if val:
                        db_path = os.path.expanduser(val)
    return db_path

DB_PATH = load_db_path()

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Таблица логов дрим-циклов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dream_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        task TEXT NOT NULL,
        status TEXT NOT NULL,
        output TEXT
    )
    """)
    
    # Таблица телеметрии
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        metric_name TEXT NOT NULL,
        value REAL NOT NULL,
        details TEXT
    )
    """)
    
    # Таблица статуса процессов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watchdog_status (
        process_name TEXT PRIMARY KEY,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        is_alive INTEGER NOT NULL,
        restarts_count INTEGER DEFAULT 0
    )
    """)
    
    conn.commit()
    conn.close()

def add_dream_log(task, status, output):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO dream_logs (task, status, output) VALUES (?, ?, ?)",
        (task, status, output)
    )
    conn.commit()
    conn.close()

def add_telemetry(metric_name, value, details=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO telemetry (metric_name, value, details) VALUES (?, ?, ?)",
        (metric_name, value, details)
    )
    conn.commit()
    conn.close()

def update_process_status(process_name, is_alive, restarts_count):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO watchdog_status (process_name, is_alive, restarts_count, timestamp)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(process_name) DO UPDATE SET
        is_alive = excluded.is_alive,
        restarts_count = excluded.restarts_count,
        timestamp = CURRENT_TIMESTAMP
    """, (process_name, 1 if is_alive else 0, restarts_count))
    conn.commit()
    conn.close()

def get_process_status():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT process_name, is_alive, restarts_count, timestamp FROM watchdog_status")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_latest_telemetry(metric_name=None, limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    if metric_name:
        cursor.execute(
            "SELECT timestamp, value, details FROM telemetry WHERE metric_name = ? ORDER BY id DESC LIMIT ?",
            (metric_name, limit)
        )
    else:
        cursor.execute(
            "SELECT timestamp, metric_name, value, details FROM telemetry ORDER BY id DESC LIMIT ?",
            (limit,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Инициализируем базу данных при первом импорте
init_db()

if __name__ == "__main__":
    print("Инициализация базы данных SQLite...")
    init_db()
    print("Успешно.")
