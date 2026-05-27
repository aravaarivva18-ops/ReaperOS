# -*- coding: utf-8 -*-
"""
Pygtail-style Log Tailer for ReaperOS.
Robust log tailing that persists read offset and handles log rotations gracefully.
"""

import os
from typing import Generator, List, Optional, Tuple

class LogTailer:
    def __init__(self, log_path: str, offset_path: Optional[str] = None) -> None:
        self.log_path = log_path
        self.offset_path = offset_path or f"{log_path}.offset"

    def _get_inode(self) -> int:
        try:
            return os.stat(self.log_path).st_ino
        except Exception:
            return 0

    def _get_offset_state(self) -> Tuple[int, int]:
        """Returns tuple of (inode, offset)."""
        if os.path.exists(self.offset_path):
            try:
                with open(self.offset_path, "r") as f:
                    parts = f.read().strip().split(",")
                    if len(parts) == 2:
                        return int(parts[0]), int(parts[1])
                    return 0, int(parts[0])
            except Exception:
                return 0, 0
        return 0, 0

    def _save_offset_state(self, inode: int, offset: int) -> None:
        try:
            with open(self.offset_path, "w") as f:
                f.write(f"{inode},{offset}")
        except Exception:
            pass

    def tail(self) -> Generator[str, None, None]:
        """Tails the log file, handles rotation, and updates offset."""
        if not os.path.exists(self.log_path):
            return

        current_inode = self._get_inode()
        saved_inode, current_offset = self._get_offset_state()
        file_size = os.path.getsize(self.log_path)

        # Detect log rotation or truncation (file shrunk or inode changed)
        if file_size < current_offset or current_inode != saved_inode:
            current_offset = 0

        with open(self.log_path, "r") as f:
            f.seek(current_offset)
            while True:
                line = f.readline()
                if not line:
                    break
                yield line
            
            # Save the new offset state
            self._save_offset_state(current_inode, f.tell())

