#!/bin/bash
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "[Trinity] Shutting down..."
pkill -f "engine.daemon"
pkill -f "engine.main"
rm -f "$PROJECT_ROOT/engine.sock" "$PROJECT_ROOT/.daemon_ready"
git add .
git commit -m "Trinity-Shutdown-Snapshot: $(date)"
echo "[Trinity] Safe to shutdown."

