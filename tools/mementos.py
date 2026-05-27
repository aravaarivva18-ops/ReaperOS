# -*- coding: utf-8 -*-
"""
Reflective Mementos for ReaperOS.
Saves reflection logs and learning points to improve outcomes in subsequent sessions.
"""

import os
import json
from typing import List, Dict, Any, Optional

class ReflectiveMementos:
    def __init__(self, storage_path: Optional[str] = None) -> None:
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        self.storage_path = storage_path or os.path.join(tools_dir, "reflections.json")
        self.reflections: List[Dict[str, Any]] = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save(self) -> None:
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.reflections, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def add_reflection(self, problem: str, solution: str, score: float = 1.0) -> None:
        self.reflections.append({
            "problem": problem,
            "solution": solution,
            "score": score
        })
        self._save()

    def query_reflection(self, keyword: str) -> List[Dict[str, Any]]:
        keyword_lower = keyword.lower()
        return [
            r for r in self.reflections
            if keyword_lower in r["problem"].lower() or keyword_lower in r["solution"].lower()
        ]
