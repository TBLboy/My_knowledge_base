# Project Log Migration

- Migration date: 2026-07-28
- Source: `.project-log-legacy-20260728/` (legacy v0.2)
- Target: `.project-log/` (runtime template v0.4)
- Policy: old directory retained unchanged; active records use new ID patterns and schemas.
- ID mappings: `atom-*` → `BL-*`, `task-*` → `TASK-*`, `decision-*` → `DEC-*`, research study → `RES-001`.
- Empty legacy architecture, verification, alignment, retrospective and distillation records remain empty in the new log.
- The full research details and original session narrative remain available in the legacy directory.
- Validation: `validate_project.py` and `validate_workflow.py` both passed on 2026-07-28.
- Goal evaluation intentionally remains pending because user approval, C-level answers, independent evidence index entries, and real-device Spike evidence do not yet exist.
