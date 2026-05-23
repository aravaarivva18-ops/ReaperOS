# Plan: Reaper OS v8.8.0 Expansion (Genesis-Singularity)

## Objective
Enhance Reaper OS with Agent-Native control, local Knowledge Graphs, and autonomous security while maintaining **Zero-Clutter**.

## Phase 1: Context Efficiency (Codegraph)
- **Goal**: Reduce token usage in `reaper recall`.
- **Action**: 
    1. Install `codegraph` in `.reaper_venv`.
    2. Map `reaper-brain.py` indexer to use Codegraph logic.
    3. Target: 40% reduction in RAG tokens.

## Phase 2: Agent-Native Control (CLI-Anything)
- **Goal**: Enable `reaper control <app>`.
- **Action**:
    1. Bridge `CLI-Anything` with `reaper-browser`.
    2. Implement dynamic tool synthesis for GUI apps (e.g., Slack, Obsidian).
    3. Containment: Isolated browser context per app.

## Phase 3: Autonomous Shield (Shannon)
- **Goal**: Evidence-based security audits.
- **Action**:
    1. Integrate `Shannon` logic into `reaper audit`.
    2. Automate PoC generation for found vulnerabilities.
    3. Storage: `.gemini_security/poc/`.

## Phase 4: Memory Infusion (Production Patterns)
- **Goal**: Populate `PROCEDURAL_PATTERNS.md`.
- **Action**:
    1. Scrape `agents-towards-production`.
    2. Distill top 10 algorithms for agentic workflows.
    3. Update `reaper-brain.py` to trigger these patterns.

## Zero-Clutter Protocol
- **Deps**: All in `/Users/rus/.reaper_venv`.
- **Binaries**: Symbolic links in `bin/reaper-expansion/` (managed by `reaper link`).
- **Cleanup**: `reaper gc` must remove all temporary expansion artifacts.

---
*Status: Awaiting Principal Approval.*
