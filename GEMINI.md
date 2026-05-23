# Reaper OS v12.3 (Frontier-Y) — Technical Specification

- **Root**: `/Users/rus/Projects/ReaperOS`
- **Trinity Engine**: `main.py` (Orchestrator) + `daemon.py` (ML-Daemon).
- **Communication**: UNIX Socket (`engine.sock`).
- **Memory/Brain**: `db.sqlite` in `/Users/rus/Documents/Knowledge-Brain/`.
- **Infrastructure**: `.reaper_venv` (Python 3.12).

## Quick Start
- **Start**: `./trinity-start.sh`
- **Monitor**: `tail -f ~/.reaper_brain.log`
- **Stop**: `./trinity-down.sh`

## Integration Points
- **Local Embedder**: `engine/daemon.py` (all-MiniLM-L6-v2).
- **External Storage**: Knowledge Brain SQLite.
- **Tasks**: `conductor/tracks/frontier-y/task_tree.json`.
