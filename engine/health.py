import asyncio
import json
import time
import sys

async def check_mcp_health(command: str, args: list = None):
    proc = None
    start_time = time.perf_counter()
    status = "🔴 OFFLINE"
    try:
        proc = await asyncio.create_subprocess_exec(
            command, *(args or []),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        # Send initialization/ping
        writer = proc.stdin
        writer.write(json.dumps({"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1}).encode())
        await writer.drain()
        
        # Expect response within 2s
        data = await asyncio.wait_for(proc.stdout.read(1024), timeout=2.0)
        status = "🟢 OK" if data else "🔴 ERROR"
    except Exception:
        status = "🔴 OFFLINE"
    finally:
        duration = time.perf_counter() - start_time
        if duration > 2.0:
            sys.stderr.write(f"\033[93m[TELEMETRY WARNING] MCP health check '{command}' took {duration:.4f}s (SLI limit: 2.0s)\033[0m\n")
            sys.stderr.flush()
            
        if proc:
            try:
                proc.terminate()
                await asyncio.wait_for(proc.wait(), timeout=1.0)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
    return status

