import pytest
from tools.healing_agent import healing_agent
from tools.knowledge_brain import get_connection

@healing_agent(max_retries=2)
def failing_function(x):
    if x == 0:
        raise ValueError("Cannot divide by zero")
    return 10 / x

def test_healing_agent_success():
    assert failing_function(2) == 5.0

def test_healing_agent_failure_logs():
    # Make sure DB is initialized
    from tools.knowledge_brain import init_db
    init_db()
    
    with pytest.raises(ValueError):
        failing_function(0)
        
    # Check if DB has the logs
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dream_logs WHERE task = 'Self-Healing: failing_function'")
    rows = cursor.fetchall()
    conn.close()
    
    assert len(rows) > 0
    assert rows[0]["status"] == "HEALING_TRIGGERED"
    assert "Cannot divide by zero" in rows[0]["output"]
