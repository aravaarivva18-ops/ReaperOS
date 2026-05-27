import pytest
import time
from engine.zero_rpc import ZeroRPCServer, ZeroRPCClient

def test_zero_rpc_happy_path():
    server = ZeroRPCServer(port=8991)
    
    # Register mock method
    def add(a: int, b: int) -> int:
        return a + b
        
    server.register_method("add", add)
    server.start()
    
    time.sleep(0.1) # Wait for server to bind
    
    try:
        client = ZeroRPCClient(port=8991)
        res = client.call("add", {"a": 10, "b": 20})
        assert res == 30
    finally:
        server.stop()
