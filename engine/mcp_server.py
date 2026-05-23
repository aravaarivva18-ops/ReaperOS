import sys
import os
import json
import asyncio
import time
import traceback
from pydantic import BaseModel, Field, ValidationError

class RecallArguments(BaseModel):
    query: str = Field(..., min_length=1, description="The search query")
    limit: int = Field(5, ge=1, le=50, description="Max memories to return")

class ArchiveArguments(BaseModel):
    text: str = Field(..., min_length=1, description="The text content to archive")

# Save original stdout for clean JSON-RPC protocol communication
mcp_stdout = sys.stdout
# Redirect standard stdout to stderr to prevent print() statements in imported modules from contaminating the protocol stream
sys.stdout = sys.stderr

# Ensure engine path is searchable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from reaper import ColdMemory, sync_dashboard

async def main_loop():
    while True:
        # Read a line from stdin asynchronously to avoid blocking the loop
        line = await asyncio.to_thread(sys.stdin.readline)
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            sys.stderr.write(f"[MCP Server Error] Failed to parse input line: {e}\n")
            sys.stderr.flush()
            continue

        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "reaper-os-mcp",
                        "version": "1.0.0"
                    }
                }
            }
            mcp_stdout.write(json.dumps(resp) + "\n")
            mcp_stdout.flush()

        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "recall",
                            "description": "Recall knowledge/memories from the ReaperOS SQLite & vector database using a semantic query.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "The search query (e.g. 'how does trinity protocol work')."
                                    },
                                    "limit": {
                                        "type": "integer",
                                        "description": "Maximum number of memories to return (default 5).",
                                        "default": 5
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "archive",
                            "description": "Archive a new knowledge node or thought into ReaperOS long-term memory.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "type": "string",
                                        "description": "The text content to archive in SQLite and the vector store."
                                    }
                                },
                                "required": ["text"]
                            }
                        },
                        {
                            "name": "pulse",
                            "description": "Get current health, disk status, context usage, and database state of ReaperOS.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                }
            }
            mcp_stdout.write(json.dumps(resp) + "\n")
            mcp_stdout.flush()

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            result_text = ""
            is_error = False
            start_time = time.perf_counter()

            try:
                if name == "recall":
                    validated_args = RecallArguments(**args)
                    query = validated_args.query
                    limit = validated_args.limit
                    memories = await ColdMemory.search(query, limit=limit)
                    if memories:
                        result_text = "\n".join([f"- {m}" for m in memories])
                    else:
                        result_text = "No relevant memories found."
                elif name == "archive":
                    validated_args = ArchiveArguments(**args)
                    text = validated_args.text
                    await ColdMemory.archive(text)
                    result_text = f"Successfully archived memory: '{text[:60]}...'"
                elif name == "pulse":
                    # Run sync_dashboard to refresh stats, then read DASHBOARD_PATH
                    sync_dashboard()
                    from reaper import DASHBOARD_PATH
                    with open(DASHBOARD_PATH, "r") as f:
                        result_text = f.read()
                else:
                    result_text = f"Unknown tool: {name}"
                    is_error = True
            except ValidationError as ve:
                result_text = f"Validation Error: {ve}"
                is_error = True
                sys.stderr.write(f"\033[91m[MCP Validation Error] Inbound tool parameters rejected for '{name}': {ve}\033[0m\n")
                sys.stderr.flush()
            except Exception as e:
                result_text = f"Error executing tool: {e}"
                is_error = True
                sys.stderr.write(f"\033[91m[MCP Runtime Error] in tool '{name}': {e}\n{traceback.format_exc()}\033[0m\n")
                sys.stderr.flush()
            finally:
                duration = time.perf_counter() - start_time
                if duration > 0.5:
                    sys.stderr.write(f"\033[93m[TELEMETRY WARNING] MCP tool '{name}' execution took {duration:.4f}s (SLI limit: 0.5s)\033[0m\n")
                    sys.stderr.flush()


            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ],
                    "isError": is_error
                }
            }
            mcp_stdout.write(json.dumps(resp) + "\n")
            mcp_stdout.flush()

        elif method == "notifications/initialized":
            # Initialized notification from client, no response required
            continue

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass
