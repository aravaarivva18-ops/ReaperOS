# Advanced Roadmap: Reaper OS v11.3.1 (High-Tech Phase)

## Phase 1: Semantic Privacy (Security)
- [ ] **Objective**: Zero leakage of credentials or real paths in logs.
- [ ] **Task**: Upgrade `PrivacyLayer` in `reaper-brain.py`.
- [ ] **Patterns**: Add regex for AWS keys, GitHub tokens, Bearer tokens, and user-home paths.
- [ ] **Integration**: Wrap all `Builder` output in `reaper-auto.py` with this layer.

## Phase 2: Live Pulse (Monitoring)
- [ ] **Objective**: Full infrastructure visibility in one command.
- [ ] **Task**: Refactor `PulseDashboard` in `reaper-brain.py`.
- [ ] **Features**: Add socket checks for ports 8080/5001, RAM usage for MLX process, and log-tailing for errors.

## Phase 3: Recursive Memory (GraphRAG v2)
- [ ] **Objective**: 100% context accuracy via relational jumps.
- [ ] **Task**: Implement `RecursiveRetriever` in `NeuralStore`.
- [ ] **Logic**: If a result has `link:symbol` tags, automatically perform a secondary search for those symbols and merge contexts.

## Execution Order
1. **Security first** (Phase 1).
2. **Observability** (Phase 2).
3. **Intelligence** (Phase 3).
