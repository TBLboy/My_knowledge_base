# Current Session

## Last Updated

- 2026-05-19 21:05 CST

## Current Objective

- Phase1 grab-knife migration: SDK path, vision_utils, robot IP, parameter centralization, and subprocess-tree cleanup are complete. Ready for rerun with corrected right-arm IP `192.168.2.161`, YAML-sourced parameters, and full resource teardown.
- Previous: Architecture refactored for two-process isolation

## Current Business Logic Position

- Main path: Phase1→2→3→4→2→5→6→2→7→DONE
- Phase1 migration branch: `testing` — code written, compiled, full Phase1 run succeeded once, cleanup bug fixed, install artifacts rebuilt
- Two-process architecture confirmed working (vision pipeline, recognition, monitor all OK)
- Active branch: `business-logic/branches/tofu-fall-detection.md` (draft)

## Completed This Session

### Phase1 Grab Cleanup Fixed (2026-05-19 21:05)

- Root cause found: lifecycle wrapper only killed the `ros2 launch` parent PID, not the whole child process tree
- `phase1_grab_lifecycle_node.py` now launches grab subprocess with `start_new_session=True`
- Cleanup now kills the entire process group with `SIGINT` → `SIGTERM` → `SIGKILL`
- Rebuilt `cuttofo_xcore` and `dexbot_middle_layer`
- Confirmed earlier `80` O6 close value came from stale `install/` artifacts, not current `src/`

### Phase1 Grab Parameters Centralized to YAML (2026-05-19 20:30)

- Added `phase1_grab` section to `cuttofo_config.yaml` with 34 parameters in 4 sub-groups (robot, lifecycle, perception, monitor, follow)
- Updated `cuttofu_phase1_grab.launch.py`, `phase1_grab_lifecycle_node.py`, `cuttofu_phase1_grab_internal.launch.py` to read defaults from YAML
- All parameters still support CLI `:=` overrides
- Python syntax verified for all 3 modified files

### O6 Gripper Parameter Tuned (2026-05-19 20:15)

- Changed `hand_o6_close_degrees_csv` from `0,0,80,0,0,0` to `0,0,70,0,0,0` across 4 files

### SDK Path + vision_utils + Robot IP Fixes (2026-05-19)

- Fixed Q-MIG-002: SDK path missing `src/` in lifecycle wrapper and external launch file
- Fixed ImportError: added `_mask_to_bool` and `_align_mask_to_depth` to vision_utils.py
- Added DEXBOT_XCORE_SDK_ROOT env var in lifecycle wrapper subprocess
- Fixed Phase1 grab default `robot_ip`: `192.168.10.21` → `192.168.2.161`
- Runtime test confirmed: RealSense, SAM3, pose_est, recognition, monitor all work
- Follow node crash causes identified: first SDK path, then wrong robot IP; both fixed

## Problems And Resolutions

- **SDK path wrong**: lifecycle wrapper's `_pkg_root()` returned workspace root but path concatenation missed `src/`. Fixed.
- **External launch file SDK default**: computed from install dir, not workspace. Replaced with `_find_ws_root()` search.
- **vision_utils missing functions**: classmate's code needs `_mask_to_bool` and `_align_mask_to_depth`. Copied from classmate's version.
- **Follow node crash → monitor "no TCP pose"**: follow node crash caused monitor to fail, not a separate bug.
- **Wrong robot IP**: grab follow node defaulted to `192.168.10.21`; user confirmed right arm is `192.168.2.161`. Updated all active Phase1 grab-chain defaults.
- **Cleanup bug**: lifecycle wrapper exited, but child nodes remained alive. Fixed by isolating subprocess in its own process group and killing the full process tree.
- **Stale install artifacts**: source tree had `hand_o6_close_degrees_csv=70`, but `install/` still had `80`; rebuild required for runtime to pick up new value.

## Verification

- Build: ✅ `cuttofo_xcore` + `dexbot_middle_layer` rebuilt successfully after cleanup fix
- SDK path: ✅ Resolves correctly to `.../src/dexbot_bottom_layer/.../xcoresdk_python-v0.5.1.ar_12`
- Robot IP default: ✅ `ros2 launch ... --show-args` now shows `192.168.2.161`
- Runtime test (no hardware): ✅ All nodes except follow node work
- Follow node: ⏳ Needs hardware (robot at `192.168.2.161`) to verify
- Parameter YAML: ✅ Python syntax passed; parameter chain verified via grep
- Cleanup fix: ✅ Python syntax passed; stale residual processes manually cleared
- Full cleanup rerun: ⏳ Still needs one more hardware rerun to confirm zero residual nodes after normal completion

## Files Changed

- `config/cuttofo_config.yaml`
- `launch/cuttofu_phase1_grab.launch.py`
- `launch/cuttofu_phase1_grab_internal.launch.py`
- `cuttofo_xcore/phase1_grab_lifecycle_node.py`
- `src/dexbot_middle_layer/CutTofo/ros/xcore_follow_tcp_chain_node_movej.py`
- `src/dexbot_middle_layer/dexbot_middle_layer/vision/pipeline/vision_utils.py`
- `.project-log/progress.md`
- `.project-log/current-session.md`
- `.project-log/config/parameter-mapping.md`

## Current State

- All code fixes applied and verified. SDK path, right-arm IP, parameter centralization, and cleanup logic are complete. Need one rerun to confirm O6=70 and zero residual nodes.

## Next Steps

1. `source /home/tbl/Project/dexbot_ros2_ws/install/setup.bash`
2. Hardware test: 2-terminal demo flow
   - Terminal G: `ros2 launch cuttofo_xcore cuttofu_phase1_grab.launch.py`
   - Terminal M: `ros2 launch cuttofo_xcore cuttofu_phase1_monitor.launch.py`
3. Verify follow node connects to robot `192.168.2.161` and publishes `/follow/current_tcp_pose`
4. Verify full 5-waypoint approach + O6 grasp sequence with `hand_o6_close_degrees_csv=0,0,70,0,0,0`
5. After lifecycle exits, run `ros2 node list` and verify no Phase1 nodes remain (`/camera/camera`, `/sam3_detector_grab`, `/pose_estimator_grab`, `/cut_tofu_object_recognition_node`, `/xcore_monitor_handle_sequence_node`, `/xcore_follow_tcp_chain_node_movej`)
6. If successful, merge migration branch into main logic
