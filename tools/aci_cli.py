# -*- coding: utf-8 -*-
"""
Agent-Computer Interface (ACI) for ReaperOS.
Provides ultra-low overhead repository navigation and file-editing primitives.
"""

import os
from typing import List

class ACIEngine:
    def __init__(self, workspace_root: str) -> None:
        self.root = workspace_root

    def list_files(self) -> List[str]:
        """Lists files under root, ignoring virtualenvs and git directories."""
        file_list = []
        for root_dir, dirs, files in os.walk(self.root):
            # Ignore binary/venv directories
            dirs[:] = [d for d in dirs if d not in {".git", ".reaper_venv", "__pycache__", "node_modules"}]
            for f in files:
                abs_p = os.path.join(root_dir, f)
                rel_p = os.path.relpath(abs_p, self.root)
                file_list.append(rel_p)
        return sorted(file_list)

    def read_file_lines(self, rel_path: str, start: int, end: int) -> List[str]:
        """Reads specific line range (1-indexed, inclusive) from a file."""
        abs_path = os.path.join(self.root, rel_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {rel_path}")
            
        lines = []
        with open(abs_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                if start <= idx <= end:
                    lines.append(line)
                if idx > end:
                    break
        return lines
