# ADR-001: Pydantic Validation for Core and MCP Layers

* **Status**: Accepted
* **Date**: 2026-05-21

## Context
AI agents interacting with APIs (such as VK API) and executing local tools via Model Context Protocol (MCP) frequently encounter unexpected or malformed inputs from Large Language Models (LLMs). Unvalidated dictionaries or string fields in Python code can lead to runtime crashes, silent parameter failures, and security vulnerabilities (e.g., empty tokens, out-of-range arguments).

We need a rigid, self-documenting data validation layer that guarantees absolute type safety, rejects bad payloads before execution, and remains fully backward-compatible with legacy dictionary interfaces in Trinity engine.

## Decision
We decided to adopt **Pydantic v2** across all critical boundary layers:
1. **VK Integration Layer (`vk_nexus.py`)**: Replaced raw class configurations and dict builders with Pydantic `BaseModel` classes (`VKAuth`, `VKPostPayload`, `VKPostItem`). All payload creation functions now validate schemas prior to returning standard dictionaries via `model_dump()`.
2. **MCP Server Interface (`mcp_server.py`)**: Defined formal Pydantic argument schemas (`RecallArguments`, `ArchiveArguments`) to validate JSON-RPC tool parameters before running internal database searches or archiving actions.

## Consequences
* **Absolute Safety**: The application immediately raises structured `ValidationError` exceptions upon invalid inputs, which are handled at boundaries.
* **Traceability**: All verification failures are cleanly logged with a clear traceback to standard error.
* **Compatibility**: Downstream clients calling `build_post_payload` continue to receive standard Python dictionary objects, preventing breaking client-side changes.
* **Dependency Lock**: Added a requirement on Pydantic v2.13+.
