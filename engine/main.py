import asyncio
import sys
import os
import json
from datetime import datetime

from config import DASHBOARD_PATH, SOCKET_PATH
from memory import MemoryBrain
from guard import check_permission
from health import check_mcp_health

async def request_embedding(text):
    """Client-side call to the background daemon with retry/backoff."""
    backoff = 0.5
    for i in range(5):
        try:
            if not os.path.exists(SOCKET_PATH):
                raise FileNotFoundError("Socket not found")
            conn = asyncio.open_unix_connection(SOCKET_PATH)
            reader, writer = await asyncio.wait_for(conn, timeout=2.0)
            writer.write(json.dumps({"cmd": "encode", "text": text}).encode())
            await writer.drain()
            
            # Read chunks until EOF
            chunks = []
            while True:
                chunk = await reader.read(4096)
                if not chunk: break
                chunks.append(chunk)
            data = b''.join(chunks)
            
            writer.close()
            await writer.wait_closed()
            return json.loads(data.decode())["embedding"]
        except (asyncio.TimeoutError, ConnectionRefusedError, FileNotFoundError) as e:
            if i == 4:
                raise RuntimeError(f"Failed to connect to daemon after 5 attempts: {e}")
            print(f"Daemon not ready, retrying in {backoff}s...")
            await asyncio.sleep(backoff)
            backoff *= 2

async def get_system_health():
    # Example MCP servers from mcp.json
    servers = {
        # "context7": ["npx", "-y", "@upstash/context7-mcp"],
        # "stitch": ["npx", "-y", "@_davideast/stitch-mcp"]
    }
    status = {}
    for name, cmd in servers.items():
        status[name] = await check_mcp_health(cmd[0], cmd[1:])
    return status

async def reaper_heartbeat():
    """Persistent background maintenance loop."""
    iteration = 0
    try:
        while True:
            health = await get_system_health()
            s_count = await MemoryBrain.get_node_count()

            # Dashboard Sync with Health
            health_str = "\n".join([f"- **{k}**: {v}" for k, v in health.items()])
            dash = f"# 🔮 Reaper Pulse\n\n- **Memory Nodes**: {s_count}\n- **MCP Status**:\n{health_str}"
            with open(DASHBOARD_PATH, "w") as f: f.write(dash)

            if iteration >= 30:
                await MemoryBrain.distill_memory()
                iteration = 0
            iteration += 1
            await asyncio.sleep(60)
    finally:
        await MemoryBrain.close()

async def main():
    try:
        if len(sys.argv) < 2: return
        cmd = sys.argv[1]

        if not check_permission(cmd):
            return

        if cmd == "start":
            await reaper_heartbeat()
        elif cmd == "encode":
            text = sys.argv[2]
            emb = await request_embedding(text)
            print(json.dumps(emb))
        elif cmd == "pulse":
            health = await get_system_health()
            s_count = await MemoryBrain.get_node_count()
            print(json.dumps({"status": "🟢 ONLINE", "nodes": s_count, "mcp": health}))
        elif cmd == "setup":
            from web_dashboard import run_mcp_setup
            success, msg = run_mcp_setup()
            if success:
                print(f"\033[92m[Setup Successful]\033[0m {msg}")
            else:
                print(f"\033[91m[Setup Failed]\033[0m {msg}")
        elif cmd == "dashboard":
            print("Starting Bento Web Dashboard on http://127.0.0.1:8234 ...")
            from web_dashboard import app
            app.run(host='127.0.0.1', port=8234)
    finally:
        await MemoryBrain.close()

class SelfHealer:
    @staticmethod
    def heal_exception(exc_type, exc_value, exc_tb):
        import traceback
        import subprocess
        from config import DB_PATH
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        tb_text = "".join(tb_lines)
        sys.stderr.write(f"\033[91m[AI Self-Healer triggered] Capturing crash: {exc_value}\n{tb_text}\033[0m\n")
        sys.stderr.flush()
        
        # Write crash dump
        crash_log = os.path.join(BASE_DIR, "logs/crash_dump.log")
        os.makedirs(os.path.dirname(crash_log), exist_ok=True)
        with open(crash_log, "w", encoding="utf-8") as f:
            f.write(tb_text)
            
        # Log to telemetry
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO telemetry (metric_name, value, details) VALUES (?, ?, ?)",
                         ("self_healing_trigger", 1.0, f"Exception: {exc_value}"))
            conn.commit()
            conn.close()
        except: pass

        # Hot-healing auto-restart mechanism: spawn clean Conductor heartbeat back up!
        sys.stderr.write("[AI Self-Healer] Performing deterministic state recovery and auto-restarting Conductor...\n")
        sys.stderr.flush()
        
        # Spawn clean Conductor in background
        cmd = [sys.executable, "-m", "engine.main", "start"]
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{BASE_DIR}:{BASE_DIR}/engine"
        subprocess.Popen(cmd, cwd=BASE_DIR, start_new_session=True, env=env)

# Register AI Self-Healer as the global exception handler
sys.excepthook = SelfHealer.heal_exception

def cli_entrypoint():
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
