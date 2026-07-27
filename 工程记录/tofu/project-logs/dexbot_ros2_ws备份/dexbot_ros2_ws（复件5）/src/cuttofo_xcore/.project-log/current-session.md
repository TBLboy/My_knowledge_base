# Current Session

## Last Updated

- 2026-05-15 Local Time (after visualization launch bug discovery)

## Current Objective

- Fix `cuttofu_phase2.launch.py` missing visualization infrastructure so RViz shows RobotModel + point cloud + tofu markers.
- Revert `viz_display.launch.py` `enable_vision` default to `true` so standalone viz shows tofu markers by default.

## Bugs Discovered

1. **`cuttofu_phase2.launch.py` missing all visualization infrastructure**:
   - No `robot_state_publisher` → `/robot_description` topic not published → RViz RobotModel display empty
   - No `viz_hand_joint_bridge` → `/joint_states_full` not published → arm joints not visible
   - No `world_display` → `world` static TF → RViz fixed frame chain broken
   - RViz launched without `-d` config file → blank window with no displays configured
   - Business nodes (SAM3, pose_estimator, tofu_state, knife_prepare, knife_cut, phase_manager) ARE present and work correctly

2. **`viz_display.launch.py` `enable_vision` default set to `false`** (our earlier change):
   - User's default command `ros2 launch cuttofo_xcore viz_display.launch.py enable_realsense:=true` no longer shows tofu markers
   - Root cause: SAM3 + pose_estimator + tofu_state only start when `enable_vision:=true`
   - `tofu_visualizer_node` IS always started, but receives no `/tofu_state` data

## Fix Plan

1. Add to `cuttofu_phase2.launch.py`:
   - `robot_state_publisher` node (build xacro, publish `/robot_description`, remap to `/joint_states_full`)
   - `viz_hand_joint_bridge` node
   - `world_display` → `world` static TF
   - RViz `-d dual_display.rviz -f world_display` argument

2. Revert `viz_display.launch.py` `enable_vision` default from `false` → `true`

## Files To Change

- `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`
- `src/cuttofo_xcore/launch/viz_display.launch.py`
- `src/cuttofo_xcore/README_PHASE_FRAMEWORK.md`

## Verification

- `python3 -m py_compile` for all modified Python files
- Confirm `enable_rviz:=true` with `cuttofu_phase2.launch.py` opens RViz with RobotModel + TF + Grid + point cloud + tofu markers
- Confirm `viz_display.launch.py enable_realsense:=true` shows tofu markers by default without extra `enable_vision:=true`
