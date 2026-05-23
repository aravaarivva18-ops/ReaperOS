# Implementation Plan: Reaper OS 8.6.0 (Genesis)

## Background & Motivation
Reaper OS 8.5.0 (AURA) established a robust baseline with the Semantic Router, Safeguard Protocol, and Memoir 2.0 (versioned global chronicles). However, as projects grow and AI agents handle more complex, multi-session tasks, three critical weaknesses remain:
1.  **Context Rot**: Long-lived sessions accumulate irrelevant data. Current AST-pruning only handles code, not conversational history or obsolete conclusions.
2.  **Procedural Amnesia**: The system remembers *facts* (Semantic Memory in `GLOBAL_CHRONICLE.md`), but it does not formally remember *how* to solve specific types of recurring problems (Procedural Memory).
3.  **Static Tooling Bound**: New MCP servers require manual configuration or hardcoded scripts. The system cannot dynamically synthesize tools for novel local APIs.

The "Genesis" upgrade aims to transition Reaper OS from a reactive assistant to a self-evolving cognitive entity by implementing active memory governance (AgeMem) and dynamic tool synthesis.

## Scope & Impact
- **Impacted Areas**: `reaper-orchestrator`, `reaper-autonome` scripts, `Knowledge-Brain/02_Wiki/Chronicles`, and the `.agents/skills` directory.
- **Out of Scope**: No new persistent background processes will be introduced. All implementations will adhere to the "Zero-Clutter" and "On-Demand" philosophy.

## Proposed Solution: The "Genesis" Architecture

The upgrade is divided into three logical pillars.

### Pillar 1: Cognitive Memory Governance (AgeMem Pattern)
We will introduce a new skill, `reaper-cognitive-memory`, which provides the agent with active verbs to manage its own context and long-term storage.
- **`distill`**: Compresses raw session trajectories into concise, abstract rules.
- **`consolidate`**: Moves distilled rules from temporary session memory into long-term storage.
- **`forget_junk`**: Explicitly instructs the agent to drop irrelevant context during the 'Discover' phase to prevent context rot.

### Pillar 2: Procedural Pattern Registry (Hermes Logger)
We will split the long-term memory into Semantic (facts) and Procedural (skills/algorithms).
- **`PROCEDURAL_PATTERNS.md`**: A new file in the `Chronicles` directory.
- **Mechanism**: When a task finishes successfully, the Orchestrator will analyze the trajectory. If a novel, reusable sequence of actions is detected (e.g., "How to debug a Vite config error"), it is logged here as a reusable algorithm.

### Pillar 3: Dynamic Tool Synthesizer (FastMCP Integration)
We will enable the agent to generate temporary MCP servers on the fly.
- **Skill**: `dynamic-tool-forge`.
- **Mechanism**: If the agent encounters a local API or script it cannot directly query efficiently, it will write a temporary Python `FastMCP` script, run it via `npx`, execute the needed queries, and then terminate the server.

## Phased Implementation Plan

### Phase 1: Procedural Memory Foundation
1.  Create `PROCEDURAL_PATTERNS.md` in `/Users/rus/Documents/Knowledge-Brain/02_Wiki/Chronicles/`.
2.  Update the `reaper-autonome finish` command to stage and commit `PROCEDURAL_PATTERNS.md` alongside `GLOBAL_CHRONICLE.md`.

### Phase 2: Cognitive Memory Skill (AgeMem)
1.  Create `.agents/skills/reaper-cognitive-memory/SKILL.md`.
2.  Define the protocols for `distill` and `consolidate`.
3.  Integrate the skill into the `reaper-orchestrator`'s 'Deliver' phase. The Orchestrator must use this skill to decide what goes into Semantic memory and what goes into Procedural memory.

### Phase 3: Dynamic Tool Synthesizer
1.  Create `.agents/skills/dynamic-tool-forge/SKILL.md`.
2.  Provide a template for a minimal `FastMCP` Python server within the skill.
3.  Define the trigger: "If data is inaccessible via `read_file` or existing MCPs, synthesize a temporary tool."

### Phase 4: Integration & System Upgrade
1.  Update `GEMINI.md` to reflect version 8.6.0 (Genesis Singularity).
2.  Include "Cognitive Governance" and "Dynamic Tooling" in the core philosophy.
3.  Run a complete test cycle using `reaper-autonome finish` to verify the git commits and Safeguard protocol.

## Alternatives Considered
- **Vector Database (Chroma/Milvus)**: Rejected due to violation of the "Zero-Clutter" rule. Markdown-based memory (`Wyrm`/`Memoir` pattern) is human-readable, easily versioned via Git, and requires no persistent daemon.
- **Continuous Background Server (agentmemory)**: Rejected. We maintain the "On-Demand" philosophy. The agent should only load memory when actively orchestrating a task.

## Verification
- Run a dummy task to trigger the new `reaper-autonome finish`.
- Verify that `PROCEDURAL_PATTERNS.md` is successfully committed to the Memoir Git repository.
- Use `sequential_thinking` to simulate the `reaper-cognitive-memory` logic and ensure it correctly identifies "junk" vs "valuable patterns".

## Migration & Rollback
- **Rollback**: Because Memory is versioned via Git, rolling back involves a simple `git checkout HEAD~1` in the `Chronicles` directory and reverting the `GEMINI.md` and `reaper-autonome` scripts to their previous state. No database migrations are necessary.