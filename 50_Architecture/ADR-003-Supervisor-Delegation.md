# ADR-003: Supervisor Subagent Delegation Mandate

* **Status**: Accepted
* **Date**: 2026-05-21

## Context
Long-running AI terminal sessions (such as Claude Code or Antigravity CLI conversations) suffer from rapid context window expansion. Standard CLI actions like running massive project-wide regex grep searches, parsing third-party documentation, compiling modules, or looping unit tests in the main conversation block quickly consume tokens, driving up costs and slowing down model responsiveness.

To combat context bloat, we need to enforce a rigid split of labor between the main coordinating agent (Supervisor) and specialized background workers.

## Decision
We decided to integrate the **Supervisor Subagent Delegation Mandate** directly into the core agent constitution ([GEMINI_ANTIGRAVITY.md](file:///Users/rus/.gemini/GEMINI_ANTIGRAVITY.md)):
1. **Delegation Rule**: The main coordination loop must never execute heavy, isolated, or routine tasks (e.g. broad file reads, documentation analysis, or multi-step unit-testing runs) directly in the main conversation block.
2. **Subagent Spawning**: All such tasks must be delegated via `invoke_subagent` to highly specialized background subprocesses (`research` for read-only codebase navigation, or `self` for test executions).
3. **Context Economy**: The main conversation keeps context slim (under the 70% threshold) by only accepting high-level JSON/Markdown summaries of the results returned by subagents.

## Consequences
* **Extreme Token Savings**: The main conversation maintains minimal token usage, drastically reducing latency and operational costs in long-running projects.
* **Asynchronous Speed**: Multi-agent swarms operate concurrently in the background, allowing the user and Supervisor to plan next steps while subagents compile or run tests.
* **Isolated Environments**: Workspaces and command outputs remain modularized, preventing dependency pollution in the primary workspace.
