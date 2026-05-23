import os
import json
import asyncio
from config import MCP_SERVERS

async def run_mcp_tool(server_name, tool_name, args_json):
    if server_name not in MCP_SERVERS:
        print(f"\033[91m[MCP Error]\033[0m Unknown server '{server_name}'. Available: {list(MCP_SERVERS.keys())}")
        return

    cmd = MCP_SERVERS[server_name]
    
    try:
        args = json.loads(args_json)
    except json.JSONDecodeError:
        print("\033[91m[MCP Error]\033[0m args_json is not valid JSON")
        return

    print(f"\033[96m[MCP Execution]\033[0m Starting {server_name} -> {tool_name}")
    
    # Start the MCP server subprocess
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # 1. Initialize request
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "reaper-os", "version": "12.3"}
        }
    }
    
    # 2. Tool call request
    call_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": args
        }
    }
    
    async def read_responses():
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            line_str = line.decode('utf-8').strip()
            if not line_str:
                continue
                
            try:
                msg = json.loads(line_str)
                if msg.get("id") == 1:
                    # Received initialize response, now send initialized notification and tool call
                    init_notif = {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized"
                    }
                    process.stdin.write((json.dumps(init_notif) + "\n").encode())
                    process.stdin.write((json.dumps(call_req) + "\n").encode())
                    await process.stdin.drain()
                    
                elif msg.get("id") == 2:
                    # Received tool response
                    if "error" in msg:
                        print(f"\033[91m[MCP Tool Error]\033[0m {json.dumps(msg['error'], indent=2)}")
                    else:
                        res = msg.get("result", {})
                        if res.get("isError"):
                            print(f"\033[91m[MCP Tool Reported Error]\033[0m")
                        for content in res.get("content", []):
                            if content.get("type") == "text":
                                print(content.get("text", ""))
                    break # We are done after receiving the tool response
            except json.JSONDecodeError:
                # Some servers might print non-JSON logs to stdout, though MCP spec says it should be stderr.
                pass
                
    # Send initialization request
    process.stdin.write((json.dumps(init_req) + "\n").encode())
    await process.stdin.drain()
    
    try:
        await asyncio.wait_for(read_responses(), timeout=15.0)
    except asyncio.TimeoutError:
        print("\033[91m[MCP Error]\033[0m Timeout waiting for server response.")
    except Exception as e:
        print(f"\033[91m[MCP Error]\033[0m {e}")
    finally:
        # Cleanup
        if process.returncode is None:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                process.kill()
