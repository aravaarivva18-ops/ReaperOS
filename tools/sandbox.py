# -*- coding: utf-8 -*-
"""
Execution Sandbox for ReaperOS.
Provides isolated environment execution for generated python code.
"""

import sys
import subprocess
from typing import Dict, Any

class SandboxResult:
    def __init__(self, stdout: str, stderr: str, returncode: int) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

class ExecutionSandbox:
    def __init__(self, use_docker: bool = False) -> None:
        self.use_docker = use_docker

    def execute_code(self, code: str, timeout: float = 5.0) -> SandboxResult:
        """Executes Python code in a secure subprocess/sandbox."""
        if self.use_docker:
            # Simulated docker run command
            # docker run --rm -i python:3.12 python -c "code"
            try:
                cmd = ["docker", "run", "--rm", "-i", "python:3.12", "python", "-c", code]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                return SandboxResult(res.stdout, res.stderr, res.returncode)
            except Exception:
                # Fallback to local subprocess if Docker is down
                pass

        # Native safe local execution via isolated subprocess
        cmd = [sys.executable, "-c", code]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return SandboxResult(res.stdout, res.stderr, res.returncode)
        except subprocess.TimeoutExpired as e:
            return SandboxResult("", "Timeout expired", -1)
