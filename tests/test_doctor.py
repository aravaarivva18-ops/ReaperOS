from engine.swarm import TaskContext
from engine.doctor import DoctorAgent

def test_doctor_agent_diagnosis():
    doctor = DoctorAgent()
    ctx = TaskContext("crash_job", {
        "error_msg": "KeyError: 'database_url'",
        "traceback": "Traceback: line 12 inside main.py",
        "remedied": False
    })
    
    res = doctor.execute_task(ctx)
    assert res["status"] == "remedied"
    assert "KeyError" in res["diagnosis"]
    assert ctx.payload["remedied"] is True
