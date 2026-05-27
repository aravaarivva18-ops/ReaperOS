# -*- coding: utf-8 -*-
"""
Self-Evolution Scaffolding for ReaperOS.
Dynamically modifies active system prompt profiles and strategies based on execution feedback.
"""

from typing import Dict, Any, List

class EvolutionScaffold:
    def __init__(self) -> None:
        self.active_strategies: List[str] = ["STANDARD"]
        self.error_count = 0

    def adapt_to_error(self, error_message: str) -> str:
        """Adapts systemic strategy when errors are encountered."""
        self.error_count += 1
        
        if "timeout" in error_message.lower():
            strategy = "AGGRESSIVE_TIMEOUT_GATING"
        elif "permission" in error_message.lower():
            strategy = "SAFE_SANDBOX_ISOLATION"
        else:
            strategy = "DEEP_TRACE_REFLECTION"

        if strategy not in self.active_strategies:
            self.active_strategies.append(strategy)

        return strategy

    def get_system_prompt_addition(self) -> str:
        """Returns extra instruction prompts based on currently active strategies."""
        additions = []
        if "AGGRESSIVE_TIMEOUT_GATING" in self.active_strategies:
            additions.append("CRITICAL: Code execution is timing out. Optimize operations or add early termination conditions.")
        if "SAFE_SANDBOX_ISOLATION" in self.active_strategies:
            additions.append("CRITICAL: Avoid accessing host files without staging/checking permissions. Run code in isolated sandboxes.")
        if "DEEP_TRACE_REFLECTION" in self.active_strategies:
            additions.append("CRITICAL: Deep trace inspection active. Write tracebacks to SQLite logs before any refactoring.")

        return "\n".join(additions)
