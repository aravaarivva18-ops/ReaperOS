import os
import sys
import json
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine"))

from engine.web_dashboard import app

@pytest.fixture
def client(tmp_path, mocker):
    db_file = str(tmp_path / "test_dash.db")
    mocker.patch("engine.web_dashboard.DB_PATH", db_file)
    
    # Setup test tables
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
    CREATE TABLE IF NOT EXISTS system_health (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        metric_name TEXT NOT NULL,
        value REAL NOT NULL,
        status TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()
    
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = json.loads(res.data.decode())
    assert data["status"] == "healthy"

def test_api_status_fallback(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    data = json.loads(res.data.decode())
    assert data["status"] == "success"
    # Fallback list must contain conductor and embedder_server
    names = [proc["process_name"] for proc in data["data"]]
    assert "conductor" in names or "embedder_server" in names

def test_api_telemetry_fallback(client):
    res = client.get("/api/telemetry")
    assert res.status_code == 200
    data = json.loads(res.data.decode())
    assert data["status"] == "success"
    assert len(data["data"]) > 0

def test_api_stats_endpoint(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = json.loads(res.data.decode())
    assert "node_count" in data
    assert "recent_memories" in data
    assert "health_logs" in data
