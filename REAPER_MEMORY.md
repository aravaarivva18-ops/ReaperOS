# 🧠 REAPER_MEMORY (Self-Healing Project Memory)

## 📌 Project Overview
- **Name**: ReaperOS
- **Stack**: Python 3.12, SQLite (WAL mode), Pydantic v2, SentenceTransformers (local embeddings)

## ⚡ Active Design Decisions (ADRs)
- **ADR-001**: Pydantic validation on VK API and MCP layers.
- **ADR-002**: SLI performance monitoring (disk writes <200ms, MCP processes <2s, tools <500ms).
- **ADR-003**: Constitutional Supervisor subagent delegation mandate.

## 🛠️ Verified Core Components
- [vk_nexus.py](file:///Users/rus/Projects/ReaperOS/engine/vk_nexus.py) — Strict validation of VK parameters via BaseModel.
- [health.py](file:///Users/rus/Projects/ReaperOS/engine/health.py) — Safe subprocess health checks with latency tracking.
- [reaper.py](file:///Users/rus/Projects/ReaperOS/engine/reaper.py) — DB access, context hydration, and self-learning loop.
- [mcp_server.py](file:///Users/rus/Projects/ReaperOS/engine/mcp_server.py) — JSON-RPC protocol with strict Pydantic argument parsing.

## 🧬 Self-Learning Fixes (JIT Debug Ledger)
*No fixes recorded yet.*
