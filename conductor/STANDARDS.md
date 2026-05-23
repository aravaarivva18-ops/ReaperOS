# Conductor: Trinity Synchronization Standards (v1.0.0)

## 1. Directory Structure Standards
All tasks must reside in `conductor/tracks/`.
Each track MUST contain:
- `isa.md`: Ideal State Artifact (Success criteria).
- `plan.md`: Step-by-step execution path.
- `metadata.json`: Auto-generated status tracking.

## 2. ISA-First Enforcement
- No task initiates without an approved `isa.md` in the track directory.
- `isa.md` must follow `/Users/rus/ISA_TEMPLATE.md`.

## 3. Automation Hook
- Any change to `plan.md` triggers an automated task tree update for the Reaper.
- Reaper will monitor `conductor/tracks/*/plan.md` for changes.

## 4. Verification Protocol
- Success = ISA criteria met.
- Verification must be recorded in `task_log` via Reaper.
