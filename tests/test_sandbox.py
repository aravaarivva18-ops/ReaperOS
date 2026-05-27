from tools.sandbox import ExecutionSandbox

def test_sandbox_local_execution():
    sandbox = ExecutionSandbox()
    code = "print('Hello from sandbox!')"
    
    res = sandbox.execute_code(code)
    assert res.returncode == 0
    assert "Hello from sandbox!" in res.stdout.strip()

def test_sandbox_timeout():
    sandbox = ExecutionSandbox()
    code = "import time; time.sleep(10)"
    
    res = sandbox.execute_code(code, timeout=0.1)
    assert res.returncode == -1
    assert "Timeout expired" in res.stderr
