# -*- coding: utf-8 -*-
"""
Autonomous Task Curriculum Creator for ReaperOS.
Generates structured subtasks out of high-level project goals.
"""

from typing import List, Dict, Any

class CurriculumCreator:
    def __init__(self, goal: str) -> None:
        self.goal = goal
        self.subtasks: List[Dict[str, Any]] = []

    def generate_curriculum(self) -> List[Dict[str, Any]]:
        """Deconstructs high-level goal into structured micro-actions."""
        clean_goal = self.goal.lower()
        
        if "refactor" in clean_goal:
            self.subtasks = [
                {"id": "step_1", "description": "Locate duplicate resources in the workspace", "status": "pending"},
                {"id": "step_2", "description": "Draft central refactored shared file", "status": "pending"},
                {"id": "step_3", "description": "Replace occurrences surgical precision style", "status": "pending"},
                {"id": "step_4", "description": "Run TDD validation loop", "status": "pending"}
            ]
        elif "test" in clean_goal:
            self.subtasks = [
                {"id": "step_1", "description": "Identify untested target modules", "status": "pending"},
                {"id": "step_2", "description": "Draft unit test fixtures", "status": "pending"},
                {"id": "step_3", "description": "Execute pytest pipeline to prove green", "status": "pending"}
            ]
        else:
            self.subtasks = [
                {"id": "step_1", "description": "Gather general repository architectural constraints", "status": "pending"},
                {"id": "step_2", "description": "Formulate technical assumptions", "status": "pending"},
                {"id": "step_3", "description": "Execute implementation plan", "status": "pending"}
            ]
            
        return self.subtasks
