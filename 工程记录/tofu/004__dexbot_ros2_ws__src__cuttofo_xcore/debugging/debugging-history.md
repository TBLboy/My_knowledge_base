# Debugging History

## 2026-05-20 — Phase3 Cut Start Twitch (TCP Coordinate Conflict)

- **Issue**: Arm twitches/jerks at Phase3 first cut start after Phase1 grab
- **Root cause**: Phase1 sets SDK tool frame to `cut_tofo_tcp` (offset 0.025, 0.0, 0.08); this persists into Phase3 RT Cartesian path, which interprets targets in the wrong tool frame
- **Fix**: Two-layer defense — (1) restore `tool0/wobj0` on Phase1 `move_abs_joints` success, (2) force-restore at Phase3 RT path entry step 3.5
- **Files**: `xcore_follow_tcp_chain_node_movej.py`, `lbot_robot_xcore.py`
- **Verification**: Hardware test passed, twitch eliminated

## 2026-05-17 — Phase7 Impedance Fallback Bug

- **Issue**: Push-forward motion failed in impedance mode; retry re-read flange pose from wrong position
- **Root cause**: `_execute_phase7_cut` not idempotent — outer `_execute_callback` retried entire function on failure
- **Fix**: Internal per-segment fallback in `_move_segment` — impedance→position retry + set `use_impedance=False`
- **Verification**: Log shows "retrying with position mode" only once, then all subsequent segments use position mode

## 2026-05-16 — Phase4 Logger Runtime Error

- **Issue**: `TypeError: RcutilsLogger.info() takes 2 positional arguments but 4 were given`
- **Root cause**: `rclpy` logger doesn't support printf-style extra args
- **Fix**: Replaced multi-arg log call with f-string
- **File**: `knife_cut_action_server.py`

## 2026-05-16 — Python Package Metadata Install Regression

- **Issue**: `importlib.metadata.PackageNotFoundError` for `cuttofo-xcore` and `dexbot-middle-layer`
- **Root cause**: `--symlink-install` created `egg-link` files instead of full `egg-info` directories
- **Fix**: Rebuilt without `--symlink-install` after cleaning build/install
- **File**: Build system

## 2026-05-16 — Phase4 Continue Trigger Not Working Under `ros2 launch`

- **Issue**: `input()` inside child process not reliable under `ros2 launch`
- **Root cause**: stdin not properly attached to child node
- **Fix**: Added `isatty()` detection; fallback to file-based trigger (`touch /tmp/cuttofo_phase4_continue`)
- **File**: `knife_cut_action_server.py`
