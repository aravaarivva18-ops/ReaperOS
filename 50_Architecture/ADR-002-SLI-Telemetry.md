# ADR-002: Adaptive Performance Telemetry and SLI Metrics

* **Status**: Accepted
* **Date**: 2026-05-21

## Context
High-performance agentic systems like ReaperOS and Antigravity CLI rely on fast local operations, local embeddings, and subsecond tool execution. Subtle bottlenecks—such as slow disk writes (due to IO contention), sluggish MCP server communication, or hanging subprocesses—can drastically degrade user experience and consume excessive CPU/tokens. 

To maintain high responsiveness, we need defensive telemetry layers that continuously profile critical operations and alarm immediately when latency exceeds acceptable bounds, without affecting application logic.

## Decision
We decided to implement a standard, microsecond-accurate profiling layer across three key execution bottlenecks:
1. **Subprocess MCP Checks (`health.py`)**: Wrap process invocation and initialization stream reading inside a latency profiling block. Emit warning log to `sys.stderr` if execution exceeds **2.0s**. Ensure measurements occur inside a guaranteed `finally` block to capture timeouts/failures.
2. **Dashboard File Write (`reaper.py`)**: Wrap SSD markdown file generation inside a performance checker. Emit warning log if writing `Dashboard.md` exceeds **200ms**.
3. **MCP Tool Execution (`mcp_server.py`)**: Wrap search (`recall`), storage (`archive`), and diagnostics (`pulse`) inside a telemetry block. Alert in standard error if tool execution exceeds **500ms**.

## Consequences
* **Real-time Observability**: System latency warnings are flushed directly to `sys.stderr`, allowing terminal UI daemons to instantly notify the user or log metrics.
* **Resilience**: Telemetry checks are non-blocking and wrap execution safely in `try...finally` boundaries to ensure zero interference with core functions.
* **Fail-Safe Logging**: Complete validation and latency warnings are captured, guaranteeing that system degradation never occurs silently.
