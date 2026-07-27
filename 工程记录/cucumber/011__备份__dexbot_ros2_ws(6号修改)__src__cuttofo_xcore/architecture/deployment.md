# Deployment

> Aligned with code as of 2026-05-17

## Launch File

### Primary Launch: `cuttofu_phase2.launch.py`

**Purpose**: Launches the complete tofu cutting demo system.

**Location**: `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`

### Launch Arguments

| Argument | Default | Choices | Description |
|----------|---------|---------|-------------|
| `log_dir` | `/tmp/ros/log` | - | ROS log directory |
| `arm` | `""` (use config) | `""`, `right`, `left` | Override active arm |
| `cuttofo_config` | `""` (use default) | - | Override config file path |
| `text_prompt` | `vision.class_filter` ("豆腐") | - | SAM3 text prompt for detection |
| `calibration_file` | `vision.calibration_file_right/left` | - | Hand-eye calibration file |
| `plane_angle_deg` | `phase2_prepare.plane_angle_deg` (135.0) | - | Knife plane tilt angle |
| `edge_align` | `phase2_prepare.edge_align` (true) | - | Align knife spine with edge |
| `offset_a` | `phase2_prepare.offset_a` (-0.005) | - | Horizontal offset from corner |
| `vertical_offset` | `phase2_prepare.vertical_offset` (0.015) | - | Height offset above surface |
| `candidate_count` | `phase2_prepare.candidate_count` (40) | - | IK candidate count |
| `preview_steps` | `phase2_prepare.preview_steps` (15) | - | Cut preview steps |
| `cut_depth` | `phase2_prepare.cut_depth` (0.017) | - | Preview cut depth |
| `safety_margin_deg` | `phase2_prepare.safety_margin_deg` (15.0) | - | Joint limit safety margin |
| `start_phase` | `phases.start_phase` (PHASE_1_GRAB_KNIFE) | - | Initial phase |
| `manual_phase_override` | `phases.manual_phase_override` (false) | - | Enable manual phase jump |
| `manual_jump_phase` | `phases.manual_jump_phase` (IDLE) | - | Target phase for manual jump |
| `auto_advance` | `phases.auto_advance` (true) | - | Enable automatic phase advance |
| `enable_legacy_coordinator` | `false` | - | Enable legacy coordinator (deprecated) |
| `phase2_timeout_s` | `5.0` | - | Phase2 tofu state timeout |
| `enable_rviz` | `false` | - | Enable RViz visualization |

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `DEXBOT_WS_ROOT` | Workspace root path | `~/Project/dexbot_ros2_ws` |
| `CUTTOFO_ACTIVE_ARM` | Active arm selection | `right` (from config) |
| `CUTTOFO_CONFIG` | Config file override | `src/cuttofo_xcore/config/cuttofo_config.yaml` |
| `ROS_LOG_DIR` | ROS log directory | `/tmp/ros/log` |

## Node Launch Order

```text
1. RealSense camera (realsense2_camera/rs_launch.py)
   └─ Topics: /camera/camera/color/image_raw, /camera/camera/aligned_depth_to_color/image_raw

2. SAM3 detector (dexbot_middle_layer/sam3_detector_node)
   └─ Subscribes: /camera/camera/color/image_raw
   └─ Publishes: Detection results (internal to pose_estimator)

3. Pose estimator (dexbot_middle_layer/pose_estimator_node)
   └─ Subscribes: /camera/camera/aligned_depth_to_color/image_raw, camera_info
   └─ Publishes: /objects_with_pose

4. Tofu state node (cuttofo_xcore/tofu_state_node)
   └─ Subscribes: /objects_with_pose
   └─ Publishes: /tofu_state

5. Knife prepare action server (cuttofo_xcore/knife_prepare_action_server)
   └─ Subscribes: /tofu_state
   └─ Action: /move_to_prepare_pose

6. Knife cut action server (cuttofo_xcore/knife_cut_action_server)
   └─ Action: /execute_knife_cut

7. (Optional) Legacy coordinator (cuttofo_xcore/tofu_cut_coordinator_node)
   └─ Condition: enable_legacy_coordinator=true (deprecated, use phase_manager_node)

8. Phase manager node (cuttofo_xcore/phase_manager_node)
   └─ Subscribes: /knife_grabbed, /tofu_state, /tofu_rotated, /phase_jump
   └─ Publishes: /phase_state, /phase_status, /cutting_start
   └─ Actions: /move_to_prepare_pose, /execute_knife_cut

9. Tofu visualizer node (cuttofo_xcore/tofu_visualizer_node)
   └─ Publishes: Visualization markers

10. (Optional) RViz2
    └─ Condition: enable_rviz=true
    └─ Config: ar5_dual_arm_bringup/rviz/dual_display.rviz
    └─ Fixed frame: world_display

11. Visualization infrastructure (OpaqueFunction: _viz_setup)
    ├─ robot_state_publisher (with robot_description from xacro)
    ├─ viz_hand_joint_bridge (merges joint states)
    └─ static_transform_publisher (world_display→world, world→camera_link)
```

## Configuration Loading

### Config File: `cuttofo_config.yaml`

**Location**: `src/cuttofo_xcore/config/cuttofo_config.yaml`

**Loading mechanism** (`config_loader.py`):
```python
config_path = os.environ.get("CUTTOFO_CONFIG", "") or _resolve_path("config/cuttofo_config.yaml")
with open(config_path, "r") as f:
    return yaml.safe_load(f)
```

**Priority**:
1. `CUTTOFO_CONFIG` environment variable (if set)
2. Default path: `src/cuttofo_xcore/config/cuttofo_config.yaml`

### Parameter Wiring

Launch file reads config and wires to nodes:

| Config Path | Launch Argument | Node Parameter | Notes |
|-------------|-----------------|----------------|-------|
| `vision.class_filter` | `text_prompt` | sam3_detector_node.text_prompt | SAM3 detection class |
| `vision.detection_threshold` | - | sam3_detector_node.detection_threshold | Detection confidence threshold |
| `vision.corner_mode` | - | pose_estimator_node.corner_mode | AABB vs PCA corner detection |
| `vision.y_filter_percentile` | - | pose_estimator_node.y_filter_percentile | Y-axis percentile filter |
| `vision.x_percentile_low/high` | - | pose_estimator_node.x_percentile_low/high | X-axis percentile filter |
| `vision.z_percentile_low/high` | - | pose_estimator_node.z_percentile_low/high | Z-axis percentile filter |
| `vision.top_y_percentile` | - | pose_estimator_node.top_y_percentile | Top Y percentile |
| `vision.calibration_file_right/left` | `calibration_file` | pose_estimator_node.calibration_file | Hand-eye calibration |
| `vision.buffer_size` | - | tofu_state_node.buffer_size | Sliding window size |
| `vision.jump_threshold` | - | tofu_state_node.jump_threshold | Jump detection threshold |
| `vision.min_buffer_frames` | - | tofu_state_node.min_buffer_frames | Min frames before publish |
| `vision.valid_timeout` | - | tofu_state_node.valid_timeout | State validity timeout |
| `cutting.phase2_prepare.*` | Various | phase_manager_node, knife_prepare_action_server | Phase2 prepare config |
| `cutting.phase6_prepare.*` | - | phase_manager_node (via _prepare_cfg_for_current_step) | Phase6 prepare config |
| `cutting.phase3_first_cut.*` | - | knife_cut_action_server | Phase3 cut config |
| `cutting.phase4_return_to_prepare.*` | - | knife_cut_action_server | Phase4 return config |
| `cutting.phase5_second_cut.*` | - | knife_cut_action_server | Phase5 cut config |
| `cutting.phase6_return_to_prepare.*` | - | knife_cut_action_server | Phase6 return config |
| `cutting.phase7_third_cut.*` | - | knife_cut_action_server | Phase7 cut config |
| `phases.start_phase` | `start_phase` | phase_manager_node.start_phase | Initial phase |
| `phases.manual_phase_override` | `manual_phase_override` | phase_manager_node.manual_phase_override | Manual override flag |
| `phases.manual_jump_phase` | `manual_jump_phase` | phase_manager_node.manual_jump_phase | Manual jump target |
| `phases.auto_advance` | `auto_advance` | phase_manager_node.auto_advance | Auto advance flag |

## Deployment Checklist

### Pre-Launch

- [ ] xCore controller running and accessible
- [ ] RealSense D435I connected and powered
- [ ] Robot arm powered and homed
- [ ] Knife end-effector mounted and secure
- [ ] Hand-eye calibration file exists and valid
- [ ] `cuttofo_config.yaml` configured for current setup
- [ ] Tofu placed within camera FOV
- [ ] Workspace clear of obstacles

### Launch Command

```bash
# Standard launch (right arm)
ros2 launch cuttofo_xcore cuttofu_phase2.launch.py

# Launch with RViz
ros2 launch cuttofo_xcore cuttofu_phase2.launch.py enable_rviz:=true

# Launch with left arm
CUTTOFO_ACTIVE_ARM=left ros2 launch cuttofo_xcore cuttofu_phase2.launch.py

# Launch with custom config
CUTTOFO_CONFIG=/path/to/custom_config.yaml ros2 launch cuttofo_xcore cuttofu_phase2.launch.py

# Launch from specific phase
ros2 launch cuttofo_xcore cuttofu_phase2.launch.py start_phase:=PHASE_2_MOVE_TO_PREPARE
```

### Post-Launch Verification

1. Check all nodes running: `ros2 node list`
2. Check topics: `ros2 topic list`
3. Check tofu detection: `ros2 topic echo /tofu_state`
4. Check phase state: `ros2 topic echo /phase_state`
5. Verify TF tree: `ros2 run tf2_tools view_frames`

## Process Management

### Node Lifecycle

All nodes run continuously until shutdown (Ctrl+C):

```text
rclpy.init()
  → Create node
  → rclpy.spin(node)  # Blocks until shutdown
  → node.destroy_node()
  → rclpy.shutdown()
```

### Error Recovery

| Failure Mode | Recovery | Notes |
|--------------|----------|-------|
| xCore services unavailable | Action server returns failure, phase_manager enters ERROR | Requires manual restart |
| Tofu detection lost | tofu_state_node publishes HEALTH_LOST, phase_manager waits | Auto-recovers if detection returns |
| IK fails (no candidates) | Prepare action returns failure, phase_manager enters ERROR | Adjust config or reposition tofu |
| Impedance mode fails | Fallback to position mode (Phase3/5/7) | Handled automatically |
| Phase4/6 user wait timeout | No timeout (indefinite wait) | User must signal continue |

## Logging

### Log Directory

Default: `/tmp/ros/log`

Override: `log_dir` launch argument or `ROS_LOG_DIR` environment variable.

### Log Levels

| Node | Default Level | Notes |
|------|---------------|-------|
| phase_manager_node | INFO | Phase transitions, goal sending |
| knife_prepare_action_server | INFO | IK results, preview scoring, move status |
| knife_cut_action_server | INFO | Cut execution, fallback events |
| tofu_state_node | DEBUG | Buffer status, health state changes |
| sam3_detector_node | INFO | Detection results |
| pose_estimator_node | INFO | Pose estimation results |

### Key Log Messages

| Message | Source | Meaning |
|---------|--------|---------|
| `Phase transition: X -> Y` | phase_manager_node | Phase change occurred |
| `Phase2 sending prepare goal` | phase_manager_node | Prepare action goal sent |
| `IK candidates: seeds=X valid=Y` | knife_prepare_action_server | IK solving results |
| `Selected preview candidate` | knife_prepare_action_server | Best IK candidate chosen |
| `Phase7 seg1 pre-mid+mid-cut` | knife_cut_action_server | Phase7 segment execution |
| `Phase7 failed in impedance mode, retrying with position mode` | knife_cut_action_server | Impedance fallback triggered |
| `Tofu detection timeout` | tofu_state_node | Tofu state expired |
