# -*- coding: utf-8 -*-
"""
Swarm / Handoff pattern for cooperative multi-agent execution in ReaperOS.
Allows agents to hand off executing tasks with context and history.
"""

from typing import Any, Dict, List

class TaskContext:
    def __init__(self, task_id: str, initial_payload: Any) -> None:
        self.task_id = task_id
        self.payload = initial_payload
        self.history: List[Dict[str, Any]] = []

    def record_transition(self, from_agent: str, to_agent: str, reason: str) -> None:
        self.history.append({
            "from": from_agent,
            "to": to_agent,
            "reason": reason,
            "payload_state": dict(self.payload) if isinstance(self.payload, dict) else self.payload
        })

class SwarmAgent:
    def __init__(self, name: str, role: str) -> None:
        self.name = name
        self.role = role

    def execute_task(self, context: TaskContext) -> Dict[str, Any]:
        """Override this method to perform actual task logic."""
        return {"status": "completed"}

    def handoff(self, to_agent: 'SwarmAgent', context: TaskContext, reason: str) -> None:
        context.record_transition(self.name, to_agent.name, reason)
