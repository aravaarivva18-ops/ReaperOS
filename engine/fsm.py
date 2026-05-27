# -*- coding: utf-8 -*-
"""
Finite State Machine (FSM) protection system for ReaperOS.
Prevents infinite AI execution loops (Analyzing -> Coding -> Verifying -> Analyzing).
"""

from typing import Dict, Set, Optional

class FSMError(Exception):
    pass

class InfiniteLoopError(FSMError):
    pass

class ReaperFSM:
    def __init__(self, max_loops: int = 3) -> None:
        self.max_loops = max_loops
        self.state = "IDLE"
        self.loop_count = 0
        
        # Valid states
        self.states = {"IDLE", "ANALYZING", "CODING", "VERIFYING", "STABLE", "ESCALATED"}
        
        # Valid transitions: state -> set of next states
        self.transitions: Dict[str, Set[str]] = {
            "IDLE": {"ANALYZING"},
            "ANALYZING": {"CODING", "ESCALATED"},
            "CODING": {"VERIFYING", "ESCALATED"},
            "VERIFYING": {"STABLE", "ANALYZING", "ESCALATED"},
            "STABLE": {"IDLE"},
            "ESCALATED": set()
        }

    def transition_to(self, new_state: str) -> str:
        if new_state not in self.states:
            raise FSMError(f"Invalid state: {new_state}")
            
        if new_state not in self.transitions[self.state]:
            raise FSMError(f"Invalid transition: {self.state} -> {new_state}")
            
        # Loop tracking
        if self.state == "VERIFYING" and new_state == "ANALYZING":
            self.loop_count += 1
            if self.loop_count >= self.max_loops:
                self.state = "ESCALATED"
                raise InfiniteLoopError(f"Infinite loop detected: exceeded max loops ({self.max_loops})")
                
        self.state = new_state
        return self.state

    def reset(self) -> None:
        self.state = "IDLE"
        self.loop_count = 0
