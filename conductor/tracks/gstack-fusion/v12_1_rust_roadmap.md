# Reaper OS v12.1: Rust-Native Evolution Plan

## Phase 1: Native Resident (Background Monitor)
- **Objective**: Move file monitoring from Python polling to native kqueue/notify.
- **Tools**: Rust `notify` crate.
- **Safety**: 
    - Keep Python script as `reaper-resident.py.bak`.
    - Verification: Monitor CPU usage using `top` during file changes.
- **Benefit**: 0% CPU idle usage.

## Phase 2: Binary GraphRAG Indexer (Speed)
- **Objective**: Replace Python-based graph building with Rust-based indexer.
- **Tools**: Rust `petgraph` + `rusqlite`.
- **Safety**:
    - Build index into a temporary table in `db.sqlite`.
    - Atomic swap of graph tables (`ALTER TABLE ... RENAME TO`).
- **Benefit**: Instant dependency mapping.

## Phase 3: High-Speed IPC (FlatBuffers)
- **Objective**: Eliminate JSON parsing overhead between Swarm nodes.
- **Tools**: Rust `flatbuffers` crate, `UnixStream`.
- **Safety**:
    - Implement a compatibility layer: if FlatBuffers read fails, fallback to JSON.
    - Incremental rollout starting with `Architect` -> `Builder`.
- **Benefit**: Sub-millisecond task coordination.

## Global Safety Protocols (The 'No-Conflict' Mandate)
1. **Shadow Deployments**: Every new binary (`-rs` suffix) runs in parallel with the Python original for 1 session.
2. **Atomic Swaps**: Use `mv` for binaries to ensure we never have a partially written binary in `~/.agents/bin/`.
3. **Rollback**: Every script has an automated restoration if the Rust binary exits with `Code != 0`.
EOF
