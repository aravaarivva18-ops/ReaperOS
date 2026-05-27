# -*- coding: utf-8 -*-
"""
State Checkpointer for ReaperOS.
Provides savepoints and rollback capabilities for complex multi-step workflows.
"""

import copy
from typing import Dict, Any, List

class StateCheckpointer:
    def __init__(self) -> None:
        self.checkpoints: Dict[str, Dict[str, Any]] = {}
        self.history: List[str] = []

    def create_checkpoint(self, checkpoint_id: str, state: Dict[str, Any]) -> None:
        """Saves a deep copy of the state as a checkpoint."""
        self.checkpoints[checkpoint_id] = copy.deepcopy(state)
        self.history.append(checkpoint_id)

    def rollback_to(self, checkpoint_id: str) -> Dict[str, Any]:
        """Restores and returns the state saved at checkpoint_id."""
        if checkpoint_id not in self.checkpoints:
            raise KeyError(f"Checkpoint not found: {checkpoint_id}")
            
        # Rewind history
        if checkpoint_id in self.history:
            idx = self.history.index(checkpoint_id)
            self.history = self.history[:idx+1]
            
        return copy.deepcopy(self.checkpoints[checkpoint_id])
