# Known Issues

## Active Issues

### Phase7 Mid-Push Skipped on Impedance→Position Fallback Retry (2026-05-17)

- **Status**: Fixed (2026-05-17) — internal retry applied per-segment
- **Symptom**: `_execute_phase7_cut` not idempotent; impedance→position fallback re-reads flange pose from wrong position (cut_7 instead of anchor_0), causing incorrect waypoint regeneration.
- **Fix**: `_move_segment` in `_execute_phase7_cut` now handles impedance→position fallback internally per segment. After fallback, `use_impedance=False` for all subsequent segments. No longer relies on outer `_execute_callback` retry.
- **File**: `knife_cut_action_server.py:368-399`
- **Can Recur?**: Yes — if impedance mode fails mid-execution on a different robot/different arm state, the same fallback logic applies; the fix should prevent re-execution from wrong position.

## Resolved Issues

- None yet.
