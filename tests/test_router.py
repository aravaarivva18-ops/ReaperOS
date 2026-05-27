from engine.router import GatewayRouter

def test_router_shortcuts():
    router = GatewayRouter()
    
    # Direct hit status
    res = router.route("/status")
    assert res is not None
    assert res["action"] == "process_status_query"
    assert res["tokens_used"] == 0
    
    # Direct hit run task
    res_run = router.route("/run cleanup_logs")
    assert res_run is not None
    assert res_run["action"] == "run_task_trigger"
    assert res_run["argument"] == "cleanup_logs"
    assert res_run["tokens_used"] == 0

def test_router_no_match():
    router = GatewayRouter()
    
    res = router.route("Can you please tell me the system status?")
    assert res is None
