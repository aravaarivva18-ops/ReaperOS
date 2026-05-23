#!/bin/bash
echo "[Trinity] Shutting down..."
pkill -f "engine.daemon"
pkill -f "engine.main"
rm -f /Users/rus/Projects/ReaperOS/engine.sock /Users/rus/Projects/ReaperOS/.daemon_ready
git add .
git commit -m "Trinity-Shutdown-Snapshot: $(date)"
echo "[Trinity] Safe to shutdown."

