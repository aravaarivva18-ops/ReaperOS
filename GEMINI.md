# Reaper OS v12.3 (Frontier-Y) — Technical Specification

- **Root**: Динамический (расположение репозитория проекта).
- **Trinity Engine**: `main.py` (Orchestrator) + `daemon.py` (ML-Daemon).
- **Communication**: UNIX Socket (`engine.sock`).
- **Memory/Brain**: `db.sqlite` в корне проекта (управляется `knowledge_brain.py`).
- **Infrastructure**: `.reaper_venv` (Python 3.14+).

## Quick Start
- **Start**: `./trinity-start.sh`
- **Monitor**: `tail -f ~/reaper_brain.log` (или через Bento Dashboard на порту 8080)
- **Stop**: `./trinity-down.sh`

## Integration Points
- **Local Embedder**: `tools/embedder_server.py` (работает на порту 5001).
- **External Storage**: Local SQLite database `db.sqlite`.
- **Tasks**: `conductor/tracks/frontier-y/task_tree.json`.
