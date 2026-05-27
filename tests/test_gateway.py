from engine.gateway import ReaperGateway

def test_reaper_gateway_commands():
    gateway = ReaperGateway()
    
    # Test status
    res = gateway.handle_command("/status")
    assert res["status"] == "success"
    assert "ONLINE" in res["message"]
    
    # Test pulse
    res_pulse = gateway.handle_command("/pulse")
    assert res_pulse["status"] == "success"
    assert "Active Memory Nodes" in res_pulse["message"]
    
    # Test run
    res_run = gateway.handle_command("/run cleanup")
    assert res_run["status"] == "success"
    assert "cleanup" in res_run["message"]
    
    # Test error
    res_err = gateway.handle_command("/unknown")
    assert res_err["status"] == "error"
