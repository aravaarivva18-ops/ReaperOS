#!/bin/bash
# Trinity Start Script
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$PROJECT_ROOT/.reaper_venv"

echo "[Trinity] Starting Monolith Engine..."
source "$VENV/bin/activate"

# Start Daemon
nohup env PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/engine" "$VENV/bin/python3" -m engine.daemon > "$HOME/.reaper_daemon.log" 2>&1 &
echo "[Trinity] Daemon started (PID: $!)"

# Start Orchestrator
nohup env PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/engine" "$VENV/bin/python3" -m engine.main start > "$HOME/.reaper_brain.log" 2>&1 &
echo "[Trinity] Heartbeat started (PID: $!)"

# Start Web Dashboard
nohup env PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/engine" "$VENV/bin/python3" -m engine.web_dashboard > "$HOME/.reaper_dashboard.log" 2>&1 &
echo "[Trinity] Web Dashboard started (PID: $!)"
