# -*- coding: utf-8 -*-
"""
0-Token Gateway Router for ReaperOS.
Intercepts dashboard/CLI command shortcuts to bypass probabilistic LLM calls.
"""

from typing import Dict, Any, Optional

class GatewayRouter:
    def __init__(self) -> None:
        self.shortcuts = {
            "/status": "process_status_query",
            "/pulse": "health_pulse_query",
            "/run": "run_task_trigger"
        }

    def route(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Routes the text. If it is a deterministic shortcut, returns the dispatch payload.
        Otherwise, returns None to indicate LLM processing is required.
        """
        clean_text = text.strip()
        for shortcut, action in self.shortcuts.items():
            if clean_text.startswith(shortcut):
                argument = clean_text[len(shortcut):].strip()
                return {
                    "action": action,
                    "argument": argument,
                    "tokens_used": 0,
                    "latency_ms": 0.0
                }
        return None
