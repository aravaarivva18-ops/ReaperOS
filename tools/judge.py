# -*- coding: utf-8 -*-
"""
LLM-as-a-Judge Code Critic for ReaperOS.
Critiques modifications against Karpathy and cybersecurity standards before committing.
"""

from typing import Dict, Any

class CodeJudge:
    def __init__(self) -> None:
        pass

    def evaluate_code(self, filename: str, code: str) -> Dict[str, Any]:
        """Critiques code changes based on systemic and safety policies."""
        score = 100
        critical_violations = []

        # Karpathy-mode check: NO speculative placeholders or simple pass/todo comments
        if "TODO" in code or "placeholder" in code.lower() or "pass" in code:
            score -= 30
            critical_violations.append("Violation: Contains speculative placeholders, TODOs, or empty PASS statements.")

        # Cybersecurity check: NO hardcoded secrets or passwords
        if "password =" in code.lower() or "api_key =" in code.lower() or "secret =" in code.lower():
            score -= 40
            critical_violations.append("Violation: Contains potential hardcoded secrets or access tokens.")

        # Complexity check: Prefer direct, single-variable simple implementations
        if code.count("class ") > 2:
            score -= 10
            critical_violations.append("Refactoring Suggestion: High class count, prefer simple direct structures.")

        is_passed = score >= 70
        return {
            "score": score,
            "passed": is_passed,
            "violations": critical_violations
        }
