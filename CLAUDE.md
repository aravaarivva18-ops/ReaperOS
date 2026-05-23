# Ruflo — Claude Code Configuration (Frontier-Y)

## Rules
- **Workspace**: Strictly limited to `/Users/rus/Projects/ReaperOS`.
- **Master Protocol**: Trinity Protocol (Conolith Engine).
- **Inference Mode**: LOCAL-ONLY (In-process ML).
- **Python Environment**: Forced Python 3.12 (Strict) via `.reaper_venv`.
- **Workflow**: GSD-T (Discussion -> Plan -> Execute -> Verify).
- **Core Engine (v12.3)**: `python3 engine/main.py [start|encode|...]`.
  - Background processes: `python3 engine/main.py start`.
- No hardcoded paths. No external ML services.
