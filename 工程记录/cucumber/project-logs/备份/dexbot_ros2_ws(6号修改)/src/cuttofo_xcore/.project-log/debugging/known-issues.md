# Known Issues

## Active Issues

### Phase3 SIGSEGV Crash on RT Cartesian Entry (2026-05-21)

- **Status**: Active — requires settling delay or idle-state check
- **Symptom**: `xcore_controller_node` crashes with exit code -11 (SIGSEGV) when RT Cartesian path is requested immediately after NRT staged prepare motion completes.
- **Error logs**: `开始运动失败 机器人运动中` followed by `运动控制模式错误`
- **Root cause hypothesis**: Controller state machine has not fully settled from NRT joint sequence to idle before RT Cartesian mode switch is requested. Race condition between `move_joint_sequence` completion and `move_rt_cartesian_path` entry.
- **Impact**: Phase3 cut cannot start; entire flow halts after Phase2 prepare.
- **Proposed fix**: Add settling delay (e.g., 1-2s) or explicit idle-state polling in Phase3 entry before initiating RT Cartesian path.
- **Files affected**: `xcore_controller_node.py`, `knife_cut_action_server.py`

### D435I Camera USB 2.1 Bandwidth Limitation (2026-05-21)

- **Status**: Active — requires hardware reconnection to USB 3.0 port
- **Symptom**: Camera configured for RGB 1920x1080x30 and Depth 1280x720x30 in launch files, but RealSense driver falls back to 640x480x15 due to USB 2.1 bandwidth limits.
- **Root cause**: D435I connected to USB 2.1 port (480 Mbps). 1080p RGB + 720p Depth at 30fps exceeds USB 2.0 bandwidth (~120-150 Mbps usable).
- **Impact**: Lower resolution reduces豆腐 detection accuracy and pose estimation precision.
- **Proposed fix**: Physically move D435I cable to USB 3.0 port (5 Gbps). No code change needed — launch files already set to max resolution.
- **Verification**: Check `rs-enumerate-devices` or `/camera/color/camera_info` topic after reconnection.

### Dual SDK Connection Conflict Risk (2026-05-21)

- **Status**: Active — requires hardware validation
- **Symptom**: `knife_prepare_action_server.py` opens a second independent xCore SDK connection for FK/IK search, while `xcore_controller_node.py` maintains its own SDK connection for motion execution.
- **Root cause**: Two simultaneous SDK connections to the same robot controller (`192.168.2.161`) may cause:
  - Controller state conflicts (both reading/writing robot state)
  - Network packet collisions or command queue interference
  - Controller-side session limit rejection
- **Impact**: Potential unpredictable behavior during Phase2 prepare search or motion execution.
- **Proposed fix options**:
  1. Share single SDK connection via ROS service/topic instead of direct connection in prepare server
  2. Use controller's existing FK service (if available) instead of separate SDK connection
  3. Validate that xCore SDK supports multiple concurrent connections safely
- **Files affected**: `knife_prepare_action_server.py`, `xcore_sdk_kinematics.py`, `xcore_controller_node.py`

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
