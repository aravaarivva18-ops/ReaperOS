# Reaper OS: Frontier-Y (v12.3)

## Architecture Overview
Reaper OS is a modular, offline-first autonomous agent ecosystem running under the Trinity Protocol.

- **Conductor**: Strategic Layer. Manages dynamic DAG-based task trees (`add-task` / `update-task`) and Ideation.
- **Reaper**: Operational Engine (`engine/main.py`). Handles DB I/O, Context Hydration, Matrix-based Vector Search (NumPy), and MCP Client communication.
- **Ruflo**: Lead Agent. Orchestrates GSD-T workflow (Discussion -> Plan -> Execute -> Verify).
- **Inference**: Strictly local using `MLX` framework. Models (Qwen2.5-0.5B, all-MiniLM) are pinned to `/local_models/weights/`. No API reliance.
- **Intelligence Core**: DAG-aware execution loop that validates task dependencies before processing and allows runtime self-correction via MCP tool calling.

## Directory Map
- `/engine/` - Core Python modular scripts (incl. `mcp_client.py`).
- `/conductor/` - Active tracks, plans (ISA/Plan), and DAG task trees.
- `/docs/` - System mandates (POLICY, CONSTITUTION).
- `/local_models/` - Pinned MLX models and inference bridge.
- `/.reaper_venv/` - Isolated Python 3.12 environment.
- `/Users/rus/Documents/Knowledge-Brain/` - External database storage (`db.sqlite`).

## Operational Guidelines
1. **Never Clutter**: All temporary caches purged on shutdown via `trinity-down`. MCP servers execute via `stdio` and terminate immediately.
2. **Offline First**: Logic defaults to local inference. External tools accessed strictly via standard MCP protocol.
3. **Trinity Protocol**: Obey GSD-T strictly. All tasks follow: Strategy (Conductor) -> Ops (Reaper) -> Execution (Ruflo).
4. **Dependency Integrity**: All automated plans must be DAG-validated via `execute-tree` with runtime adjustment capabilities.
