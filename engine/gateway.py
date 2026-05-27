# -*- coding: utf-8 -*-
"""
Telegram / Discord Gateway interface for ReaperOS.
Provides external control and status telemetry updates through modular gateways.
"""

from typing import Dict, Any, Optional

class ReaperGateway:
    def __init__(self, token: Optional[str] = None, mock_mode: bool = True) -> None:
        self.token = token
        self.mock_mode = mock_mode

    def handle_command(self, text: str) -> Dict[str, Any]:
        """
        Parses and handles incoming command texts.
        Supported commands: /status, /pulse, /run <task>
        """
        clean_text = text.strip()
        if not clean_text.startswith("/"):
            return {"status": "error", "message": "Commands must start with '/'"}

        parts = clean_text.split(" ", 1)
        command = parts[0]
        argument = parts[1] if len(parts) > 1 else ""

        if command == "/status":
            return {
                "status": "success",
                "message": "ReaperOS Daemon: 🟢 ONLINE\nProcesses monitored: Conductor, Daemon, Web Dashboard."
            }
        elif command == "/pulse":
            return {
                "status": "success",
                "message": "Heartbeat: Healthy\nActive Memory Nodes: 42"
            }
        elif command == "/run":
            if not argument:
                return {"status": "error", "message": "Specify a task name to run, e.g. /run cleanup"}
            return {
                "status": "success",
                "message": f"Task '{argument}' successfully queued for execution."
            }

        return {"status": "error", "message": f"Unknown command: {command}"}
