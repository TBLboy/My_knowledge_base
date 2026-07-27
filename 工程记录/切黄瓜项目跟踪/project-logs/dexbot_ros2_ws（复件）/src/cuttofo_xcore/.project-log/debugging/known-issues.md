# Known Issues

## Active Issues

- None.

## Resolved Issues

### Phase3 Cut Start Twitch — TCP Coordinate Conflict (2026-05-20)

- **Status**: Resolved
- **Symptom**: Repeatable arm twitch/jerk at Phase3 first cut start (and Phase5 second cut start) after running Phase1 visual knife-grab. Skipping Phase1 avoids the twitch.
- **Root cause**: Phase1 grab sets SDK tool frame to `cut_tofo_tcp` (offset `0.025, 0.0, 0.08`) for grasp-follow motions. This tool frame persists in the xCore SDK controller state after Phase1 subprocess exits. Phase2 joint-space MoveJ ignores it, but Phase3/Phase5 RT Cartesian path interprets target poses in the active tool frame, causing an instantaneous pose correction jerk when entering `RtCommandMode`.
- **Fix (two-layer defense)**:
  1. **Phase1 exit restoration**: `xcore_follow_tcp_chain_node_movej.py` calls `set_toolset_by_name("tool0", "wobj0")` immediately after final `move_abs_joints` succeeds, restoring default tool frame before subprocess exits.
  2. **Phase3 RT entry restoration**: `lbot_robot_xcore.py` `move_rt_cartesian_path()` step 3.5 calls `setToolset(tool0, wobj0)` before `setRtNetworkTolerance` and `setMotionControlMode(RtCommandMode)`, catching any external GUI state leakage.
- **Files**: `xcore_follow_tcp_chain_node_movej.py`, `lbot_robot_xcore.py`, `cuttofu_phase1_grab_internal.launch.py`
- **Verification**: Hardware test confirmed Phase3 cut starts smooth, no twitch. Logs show `move_abs_joints: restored default toolset tool0/wobj0` and `[RT_PATH] step 3.5: setToolset(tool0, wobj0)`.

---

### Phase7 Mid-Push Skipped on Impedance→Position Fallback Retry (2026-05-17)

- **Status**: Fixed (2026-05-17) — internal retry applied per-segment
- **Symptom**: `_execute_phase7_cut` not idempotent; impedance→position fallback re-reads flange pose from wrong position (cut_7 instead of anchor_0), causing incorrect waypoint regeneration.
- **Fix**: `_move_segment` in `_execute_phase7_cut` now handles impedance→position fallback internally per segment. After fallback, `use_impedance=False` for all subsequent segments. No longer relies on outer `_execute_callback` retry.
- **File**: `knife_cut_action_server.py:368-399`
- **Can Recur?**: Yes — if impedance mode fails mid-execution on a different robot/different arm state, the same fallback logic applies; the fix should prevent re-execution from wrong position.

## Resolved Issues

- None yet.
