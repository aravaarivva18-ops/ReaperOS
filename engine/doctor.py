# -*- coding: utf-8 -*-
"""
Doctor Agent for ReaperOS Swarm.
Specializes in localized debugging and autonomous trace troubleshooting.
"""

from typing import Dict, Any
from engine.swarm import SwarmAgent, TaskContext

class DoctorAgent(SwarmAgent):
    def __init__(self, name: str = "Doctor") -> None:
        super().__init__(name, "Debugger")

    def execute_task(self, context: TaskContext) -> Dict[str, Any]:
        """Inspects crash logs and generates localized diagnosis."""
        error_msg = context.payload.get("error_msg", "")
        traceback = context.payload.get("traceback", "")
        
        # Simple rule-based localized analysis
        if "keyerror" in error_msg.lower():
            diagnosis = "KeyError: Accessing missing dictionary keys. Solution: Use dict.get() fallback."
        elif "zerodivisionerror" in error_msg.lower():
            diagnosis = "ZeroDivisionError: Division by zero. Solution: Check denom is not zero before dividing."
        else:
            diagnosis = f"General failure: {error_msg}. Solution: Inspect trace and review Karpathy coding pitfall parameters."

        context.payload["diagnosis"] = diagnosis
        context.payload["remedied"] = True
        return {"status": "remedied", "diagnosis": diagnosis}
