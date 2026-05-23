# Architecture RFC: Frontier-Y (v12.3)

## Goal
Evolve the Trinity Protocol from a manual operational standard to an automated cognitive engine.

## 1. Conductor: Dynamic Spec Synthesis
- **Current State**: Manual `plan.md` creation.
- **Goal**: Auto-generate task trees in JSON from `isa.md`.
- **Implementation**:
    - Build `tools/spec_synthesizer.py`.
    - Input: `isa.md` (Success Criteria).
    - Output: `.task_tree.json`.
    - Reaper OS will parse this JSON to execute tasks without manual plan interpretation.

## 2. Reaper OS: Cognitive & Memory Upgrade
### 2.1 Tiered Context (Dynamic Routing)
- **Implementation**: `reaper.py` will route queries:
    - Simple Ops (snapshot, log, pulse) -> `gpt-4o-mini`.
    - Reasoning Tasks (recall, audit, heal, plan) -> `o3-mini`.
- **Logic**: Header-based switching in `reaper.py` API calls.

### 2.2 Semantic Search
- **Implementation**: Integrate `sqlite-vec`.
- **Flow**: Generate embeddings for all `task_log` entries and `PROCEDURAL_PATTERNS.md` on write. Use similarity search for `recall`.

## 3. Ruflo: Recursive Distillation
- **Goal**: Prevent context rot.
- **Implementation**:
    - New Phase 4 routine: `reaper.py distill`.
    - Aggregates session facts.
    - Updates `GLOBAL_CHRONICLE.md`.
    - Clears temp session context.

## Integration Path
1. **Pillar 1 (Conductor)**: High impact on operator speed.
2. **Pillar 2 (Reaper)**: High impact on task quality.
3. **Pillar 3 (Ruflo)**: Essential for long-term consistency.
