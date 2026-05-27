# -*- coding: utf-8 -*-
"""
Dynamic Skill Registry for ReaperOS.
Standardizes listing, metadata mapping, and loading of generated skills.
"""

import os
import json
from typing import Dict, Any, Optional

class SkillRegistry:
    def __init__(self, registry_path: Optional[str] = None) -> None:
        tools_dir = os.path.dirname(os.path.abspath(__file__))
        self.registry_path = registry_path or os.path.join(tools_dir, "skills_registry.json")
        self.skills: Dict[str, Dict[str, Any]] = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self) -> None:
        try:
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(self.skills, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def register_skill(self, name: str, description: str, file_path: str) -> None:
        self.skills[name] = {
            "description": description,
            "file_path": file_path,
            "registered_at": os.path.getmtime(file_path) if os.path.exists(file_path) else 0.0
        }
        self._save()

    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        return self.skills.get(name)
