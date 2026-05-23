# Implementation Plan: SPARC-DAG State Machine

## Objective
Transform the text-based SPARC protocol into a rigid Directed Acyclic Graph (DAG) state machine within the `reaper-orchestrator.py` engine. Introduce Traceability (Opik/LangSmith pattern) to log all state transitions.

## Phase 1: Architecture & Configuration (Current)
- [x] Create Track directory and ISA.
- [ ] Update `reaper-version.json` to **v11.5.0 (Graph-Core)**.
- [x] Update `PROCEDURAL_PATTERNS.md` and `GEMINI.md` to define the DAG strict transition rules.

## Phase 2: Orchestrator Code Modification
- [x] Refactor `reaper-orchestrator.py` to implement a `StateMachine` class.
- [ ] Define Nodes: `INIT`, `SPEC`, `PSEUDOCODE`, `ARCH`, `REFINE`, `CODE`, `VERIFY`, `END`.
- [ ] Define Edges: Valid transitions only (e.g., `PSEUDOCODE` -> `ARCH`). Block direct `INIT` -> `CODE` jumps.

## Phase 3: Traceability & Observability
- [x] Implement `TraceLogger` to record every state transition into `.reaper_traces/`.
- [ ] Update SONA integration to consume Traces instead of raw logs.

## Phase 4: Validation
- [ ] Run `reaper pulse`.
- [ ] Execute a test workflow to confirm state enforcement.
