# Plan: Dynamic Spec Synthesis Implementation

## Phase 1: Specification Design
- [ ] Define JSON schema for `.task_tree.json`.
- [ ] Map `isa.md` markdown sections to JSON task structure.

## Phase 2: Tool Development (`tools/spec_synthesizer.py`)
- [ ] Implement parser logic using `markdown` and `pydantic`.
- [ ] Add validation logic to ensure tasks are atomic and verifiable.
- [ ] Create `synthesize` CLI entry point.

## Phase 3: Reaper Integration
- [ ] Update `reaper.py` to watch for `.task_tree.json` updates.
- [ ] Implement executor loop for tasks parsed from the tree.

## Phase 4: Verification
- [ ] Run synthesis on `frontier-y/isa.md`.
- [ ] Validate generated JSON against schema.
- [ ] Confirm Reaper OS parses tasks correctly.
