# -*- coding: utf-8 -*-
"""
Healing Agent decorator for ReaperOS.
Interceptors exceptions, logs failure context, and coordinates autonomous healing routines.
"""

import sys
import traceback
import functools
from typing import Any, Callable, Dict
from tools.knowledge_brain import add_dream_log, add_telemetry

def healing_agent(max_retries: int = 3):
    """
    Decorator to protect critical functions. 
    If a crash occurs, gathers full runtime traceback, registers telemetry, 
    and notifies SQLite knowledge brain for self-healing scheduling.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
                    
                    # Log failure to SQLite Knowledge Brain
                    log_msg = (
                        f"Function '{func.__name__}' failed (Attempt {retries}/{max_retries}).\n"
                        f"Arguments: args={args}, kwargs={kwargs}\n"
                        f"Exception: {e}\n"
                        f"Traceback:\n{tb_str}"
                    )
                    
                    try:
                        add_dream_log(
                            task=f"Self-Healing: {func.__name__}",
                            status="HEALING_TRIGGERED" if retries < max_retries else "HEALING_FAILED",
                            output=log_msg
                        )
                        add_telemetry(
                            metric_name=f"healing_trigger_{func.__name__}",
                            value=1.0,
                            details=str(e)
                        )
                    except Exception as db_err:
                        print(f"Failed to log self-healing event to database: {db_err}", file=sys.stderr)
                    
                    if retries >= max_retries:
                        raise e
        return wrapper
    return decorator
