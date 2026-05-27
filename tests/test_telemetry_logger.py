import time
import pytest
from tools.telemetry_logger import TelemetryLogger

def test_telemetry_logger_fast_call(caplog):
    start = time.perf_counter()
    time.sleep(0.01)
    
    latency = TelemetryLogger.log_call("mock_api_fast", start)
    assert latency > 0
    # No warnings in caplog
    for record in caplog.records:
        assert record.levelname != "WARNING"

def test_telemetry_logger_slow_call_warning(caplog):
    start = time.perf_counter()
    # Simulate a slow action
    time.sleep(0.55)
    
    latency = TelemetryLogger.log_call("mock_api_slow", start, "testing slow trigger")
    assert latency > 500
    
    # Verify warning got logged
    warnings = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warnings) == 1
    assert "SLI BREACH" in warnings[0].message
