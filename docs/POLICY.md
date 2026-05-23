# 🛡 Reaper Policy Engine (RPE) - POLICY.md (v12.3)

## 1. Modes
- **ALLOW**: Exec (Safe/Read-only).
- **DENY**: Block + report (Malicious/Destructive).
- **ESCALATE**: Ask user (High-risk/Config changes).

## 2. Tool Policies

### SURGICAL_DIFFS (Integrity)
- **MANDATE**: Minimal change. No unrelated format/comments/logic.
- **HEXAGONAL**: Separate Logic from I/O. Keep engine core clean.

### FS_ACCESS (Filesystem)
- **ALLOW**: `/Users/rus/Projects`, `/Users/rus/Documents/Knowledge-Brain`, `/Users/rus/.gemini/tmp`.
- **ESCALATE**: `.zshrc`, `.ssh/`, `.env`, system files.

### MCP_EXEC (Tools)
- **ALLOW**: Standard MCP servers (sqlite, github, filesystem, browser).
- **POLICY**: MCP servers must run via `stdio` and terminate immediately after tool call.

### SHELL_EXEC (Commands)
- **ALLOW**: `ls`, `grep`, `git`, `npm`, `python`, `npx`.
- **ESCALATE**: `rm -rf`, `sudo`, `kill`.

## 3. RPE Guard
Agent identifies risk, explains if `ESCALATE`.

## 4. KG (Knowledge Brain)
All insights must be distilled into `ColdMemory` weekly.

---
*Policy v12.3 | Reaper OS 12.3.0*
