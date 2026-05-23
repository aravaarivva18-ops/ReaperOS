#!/bin/bash
# Trinity Start Script
PROJECT_ROOT="/Users/rus/Projects/ReaperOS"
VENV="$PROJECT_ROOT/.reaper_venv"

echo "[Trinity] Starting Monolith Engine..."
source "$VENV/bin/activate"

# Start Daemon
nohup env PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/engine" python3 -m engine.daemon > /Users/rus/.reaper_daemon.log 2>&1 &
echo "[Trinity] Daemon started (PID: $!)"

# Start Orchestrator
nohup env PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/engine" python3 -m engine.main start > /Users/rus/.reaper_brain.log 2>&1 &
echo "[Trinity] Heartbeat started (PID: $!)"
