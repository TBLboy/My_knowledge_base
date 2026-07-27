# Current Session

## Last Updated

- 2026-05-16 12:35 CST

## Current Objective

- Add depth image Bilateral filter to reduce point cloud noise and improve top-corner stability.

## Current Business Logic Position

- Main path: Phase1 grab knife → Phase2 prepare from tofu right edge → Phase3 right-to-left cut → Phase4 return-to-prepare → Phase5 second cut → DONE.
- Active node: Phase3 relative cutting from current flange pose.
- Active edge: current flange pose → flange Z+ cut → retract → base step.
- Active branch: None.

## Completed This Session

- Implemented right-side A/B selection in `tofu_geometry.py`.
- Implemented leftward/base-Z- `l` selection for TCP offset.
- Updated Phase2 preview to use target flange Z+ instead of hardcoded base Y-.
- Updated visualizer to respect `edge_align` for knife normal visualization.
- Passed `edge_align` into visualizer from both launch files.
- Changed Phase3 `step_z` to `-0.015` for right-to-left cutting.
- Synced modified files to `install/cuttofo_xcore`.
- Fixed `/tofu_state.top_corners` canonical order so RViz A/B uses the right edge even when pose estimator provides `gf[8:20]`.
- Changed `/robot/get_state` to prefer SDK native `flangeInBase` pose, matching RT Cartesian path anchor source.
- Added Phase3/5 waypoint sanity logging for first waypoint distance and rotation delta.
- Guarded core node shutdown with `if rclpy.ok()` to suppress Ctrl-C RCLError noise.
- Replaced visual top-corner estimation with top-plane RANSAC plus XZ `cv2.minAreaRect`, but found results worse than original; fully reverted.
- Reverted `tofu_geometry.py` canonical ordering back to original two-largest-Z-points A/B selection.
- Added `cv2.bilateralFilter` on depth image (`d=5, sigmaColor=20, sigmaSpace=20`) before 3D projection to reduce sensor noise while preserving tofu edges.

## Problems And Resolutions

- Found Phase2 preview still used hardcoded base Y- direction, inconsistent with current Phase3 flange-Z cutting. Fixed to use `target_R[:, 2]`.
- Found visualizer ignored `edge_align` for knife normal display. Fixed by using `build_rotation_with_edge_dir()` when `edge_align=true`.
- Found RViz A/B still used old order because `tofu_state_node.py` trusted pose estimator `gf[8:20]` ordering. Fixed by reordering all top-corner sources after source/mirror handling.
- Found Phase3 first segment could jump because `/robot/get_state` used FK pose while RT path internally anchors on SDK `posture(flangeInBase)`. Fixed `/get_state` to prefer SDK native pose.
- Found rotated tofu breaks the old AABB corner estimator. Attempted RANSAC+minAreaRect but real depth clouds proved too noisy; reverted to original axis-aligned AABB.

## Verification

- `python3 -m py_compile` passed for changed Python and launch files.
- YAML load/assertion passed: `phase3_first_cut.step_z < 0`.
- Lightweight geometry test passed: A/B selected from max-Z edge, edge direction points base X+, positive `offset_a` shifts TCP toward lower Z.
- Lightweight Phase3 path test passed: generated 15 waypoints for 5 cycles, first segment equals `cut_move=0.04m`, first waypoint has no rotation delta, and `step_z=-0.015` is applied.
- `colcon build --packages-select dexbot_middle_layer cuttofo_xcore` succeeded (0.73s, no errors).

## Files Changed

- `cuttofo_xcore/tofu_geometry.py`
- `cuttofo_xcore/prepare_pose_selector.py`
- `cuttofo_xcore/tofu_visualizer_node.py`
- `cuttofo_xcore/knife_cut_action_server.py`
- `cuttofo_xcore/knife_prepare_action_server.py`
- `cuttofo_xcore/phase_manager_node.py`
- `dexbot_bottom_layer/xcore_controller_node.py`
- `launch/cuttofu_phase2.launch.py`
- `launch/viz_display.launch.py`
- `config/cuttofo_config.yaml`
- `dexbot_middle_layer/vision/pipeline/vision_utils.py`
- `.project-log/progress.md`
- `.project-log/current-session.md`
- Install copies under `install/cuttofo_xcore/`

## Current State

- Source code is now fully reverted to original axis-aligned top-corner detection.
- `vision_utils.py` and `tofu_geometry.py` restored to pre-12:20 state.
- `colcon build` passed; install copies are aligned.

## Next Steps

1. Relaunch and confirm RViz A/B markers are on the tofu right edge.
2. Confirm `waypoint sanity` log reports `first_dist≈0.0400m` and `first_rot_delta≈0deg`.
3. Run Phase2→3 and confirm Phase3 starts cutting from prepare without a large reposition segment.
