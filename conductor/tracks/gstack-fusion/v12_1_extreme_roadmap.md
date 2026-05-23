# Roadmap: Reaper OS v12.1 (Extreme Performance)

## Phase 1: Native Vector Intelligence (SQLite-Vec)
*   **Goal**: Replace manual cosine calculations in Rust/Python with native SQL vector operations.
*   **Steps**:
    1.  Compile/install `sqlite-vec` extension for the system SQLite.
    2.  Migrate `knowledge_nodes` table schema to support `vec` types.
    3.  Refactor `reaper-brain.py` to use SQL `distance` queries.
    4.  Verify search performance and precision vs the current Rust binary.

## Phase 2: Embedder Daemon Migration (Rust)
*   **Goal**: Remove the Python bottleneck from embedding generation.
*   **Steps**:
    1.  Refactor `embedding_daemon.py` to a Rust-based binary using `tokenizers` and `ort` (ONNX Runtime).
    2.  Implement an IPC listener using Unix Domain Sockets.
    3.  Benchmark latency of embedding generation.
    4.  Update `reaper-brain.py` client to talk to the new socket.

## Phase 3: Binary IPC (Unix Sockets + FlatBuffers)
*   **Goal**: Eliminate JSON serialization overhead between Swarm nodes.
*   **Steps**:
    1.  Define a shared schema for agent messages using FlatBuffers.
    2.  Implement a Unix Socket server in the `reaper-orchestrator` (in Rust).
    3.  Replace all `subprocess` JSON-passing logic with socket-based binary streaming.
    4.  Verify sub-millisecond task coordination.

## Verification
- Performance benchmarking of `/recall` before and after each phase.
- Load testing the swarm with 10+ simultaneous tasks to ensure zero resource contention.
- Final distillation of experience into `MEMORY.md`.
EOF
