from engine.swarm import SwarmAgent, TaskContext

class ConductorAgent(SwarmAgent):
    def execute_task(self, context: TaskContext):
        context.payload["conductor_processed"] = True
        return {"status": "handoff"}

class ReaperAgent(SwarmAgent):
    def execute_task(self, context: TaskContext):
        context.payload["reaper_processed"] = True
        return {"status": "done"}

def test_swarm_handoff_flow():
    conductor = ConductorAgent("Conductor", "Orchestrator")
    reaper = ReaperAgent("Reaper", "Coder")
    
    ctx = TaskContext("task_123", {"input": "test_code", "conductor_processed": False, "reaper_processed": False})
    
    # Conductor runs
    res = conductor.execute_task(ctx)
    assert ctx.payload["conductor_processed"] is True
    assert res["status"] == "handoff"
    
    # Handoff to Reaper
    conductor.handoff(reaper, ctx, reason="Need coding expertise")
    
    # Reaper runs
    res_reaper = reaper.execute_task(ctx)
    assert ctx.payload["reaper_processed"] is True
    assert res_reaper["status"] == "done"
    
    # Verify handoff history
    assert len(ctx.history) == 1
    assert ctx.history[0]["from"] == "Conductor"
    assert ctx.history[0]["to"] == "Reaper"
    assert ctx.history[0]["reason"] == "Need coding expertise"
