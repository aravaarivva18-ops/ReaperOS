# -*- coding: utf-8 -*-
"""
Observability Telemetry Logger for ReaperOS.
Handles latency tracking, cost estimation, and triggers warnings for SLI breaches (>500ms).
"""

import time
import logging
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TelemetryLogger")

class TelemetryLogger:
    @staticmethod
    def log_call(api_name: str, start_time: float, details: str = "") -> float:
        """Calculates elapsed latency and logs standard warning if SLI threshold (>500ms) breached."""
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        if latency_ms > 500:
            logger.warning(
                f"⚠️ [SLI BREACH] API '{api_name}' exceeded latency threshold (500ms): "
                f"{latency_ms:.1f}ms. Details: {details}"
            )
        else:
            logger.info(f"API '{api_name}' processed in {latency_ms:.1f}ms")
            
        return latency_ms
