# Roadmap: Reaper OS v12.0 (Frontier-X)

## Phase 1: Infra & Speed (The Rust/SSD Layer)
1. **OMLX Integration**:
    - Update `reaper-daemon` to use **OMLX** as the primary backend.
    - Enable SSD-caching to support 7B-14B models on 8GB RAM without kernel panics.
2. **Rust Orchestrator (OpenHuman Inspiration)**:
    - Prototype a Rust-based `reaper-heart` to replace the Python orchestrator for sub-millisecond process management and reduced overhead.

## Phase 2: Sensory & Tooling (The Firecrawl/Agent-Skills Layer)
3. **Firecrawl MCP Deployment**:
    - Install `firecrawl-mcp-server`.
    - Replace the legacy `defuddle` logic with Firecrawl for high-fidelity Markdown scraping.
4. **Agent-Skills Factory**:
    - Build an automated sync tool to pull 1.4k+ skills from `agent-skills` into our local registry.
    - Map these skills to our **Graph-Core** for autonomous discovery.
5. **Ghidra Security Suite**:
    - Integrate `ghidramcp` as a specialized skill for the `LEAD` and `SENTRY` roles to perform binary audits.

## Phase 3: Cognitive Evolution (The Letta/Self-Learning Layer)
6. **Letta Stateful Memory**:
    - Wrap `Mem0 v3` with **Letta's** state management.
    - Implement "infinite context" through streaming state (MemGPT-style context swapping).
7. **Self-Iterative Swarm (CrewAI/Dify Upgrade)**:
    - Upgrade `reaper-auto.py` (LangGraph) with a **Self-Correction Loop**.
    - Agents will now store "failure patterns" in the DB and avoid them in subsequent iterations without user input.

## Phase 4: Verification & Release
8. **Reaper Pulse 2.0**:
    - Add OMLX cache metrics and Letta state health to the dashboard.
9. **Final Distillation**:
    - Version bump to **v12.0.0 (Frontier-X)**.
