# Communication

> Aligned with code as of 2026-05-17

## ROS2 Topics

### Perception Pipeline

| Topic | Type | Publisher | Subscriber | Rate | QoS | Notes |
|-------|------|-----------|------------|------|-----|-------|
| `/camera/camera/color/image_raw` | sensor_msgs/Image | realsense2_camera | sam3_detector_node | 30Hz | Default | RGB input for SAM3 |
| `/camera/camera/aligned_depth_to_color/image_raw` | sensor_msgs/Image | realsense2_camera | pose_estimator_node | 30Hz | Default | Aligned depth for pose estimation |
| `/camera/camera/aligned_depth_to_color/camera_info` | sensor_msgs/CameraInfo | realsense2_camera | pose_estimator_node | 30Hz | Default | Camera intrinsics |
| `/objects_with_pose` | dexbot_interfaces_mid/ObjectStateArray | pose_estimator_node | tofu_state_node | ~5-10Hz | BEST_EFFORT, depth=10 | SAM3 detection + 6D pose |

### Tofu State

| Topic | Type | Publisher | Subscriber | Rate | QoS | Notes |
|-------|------|-----------|------------|------|-----|-------|
| `/tofu_state` | cuttofo_lbot_interfaces/TofuState | tofu_state_node | phase_manager_node, knife_prepare_action_server | 10Hz | Default | Filtered tofu state with health |

### Phase Management

| Topic | Type | Publisher | Subscriber | Rate | QoS | Notes |
|-------|------|-----------|------------|------|-----|-------|
| `/phase_state` | std_msgs/String | phase_manager_node | External (monitoring) | 0.5Hz | Default | Current phase name |
| `/phase_status` | std_msgs/String | phase_manager_node | External (monitoring) | 0.5Hz | Default | Full status string |
| `/cutting_start` | std_msgs/Bool | phase_manager_node | External | Event-based | Default | Published when Phase2→Phase3 |
| `/knife_grabbed` | std_msgs/Bool | External | phase_manager_node | Event-based | Default | Knife grab signal |
| `/tofu_rotated` | std_msgs/Bool | External | phase_manager_node | Event-based | Default | Tofu rotation signal |
| `/phase_jump` | std_msgs/String | External | phase_manager_node | Event-based | Default | Manual phase jump command |

### Visualization

| Topic | Type | Publisher | Subscriber | Rate | QoS | Notes |
|-------|------|-----------|------------|------|-----|-------|
| `/joint_states_full` | sensor_msgs/JointState | viz_hand_joint_bridge | robot_state_publisher | ~50Hz | Default | Merged joint states for RViz |
| `/arm_r/joint_states` | sensor_msgs/JointState | xCore controller | viz_hand_joint_bridge | ~50Hz | Default | Right arm joint states |
| `/arm_l/joint_states` | sensor_msgs/JointState | xCore controller | viz_hand_joint_bridge | ~50Hz | Default | Left arm joint states |

### TF Tree

| Transform | Parent | Child | Type | Notes |
|-----------|--------|-------|------|-------|
| `world_display` → `world` | world_display | world | Static | RViz reference frame, rotated -90° roll, 180° pitch |
| `world` → `camera_link` | world | camera_link | Static | From hand-eye calibration |
| `world` → `AR5-5_07R-W4C1C1_base` | world | right_arm_base | Static | Right arm at origin |
| `world` → `AR5-5_07L-W4C1C1_base` | world | left_arm_base | Static | Left arm at [0,0,-0.158] with 180° roll |
| `link6` → `link7` | link6 | link7 | Dynamic | Last joint, published by robot_state_publisher |

## ROS2 Actions

### Prepare Pose

| Field | Value | Notes |
|-------|-------|-------|
| Action name | `/move_to_prepare_pose` | |
| Type | cuttofo_lbot_interfaces/MoveToPreparePose | |
| Server | knife_prepare_action_server | |
| Client | phase_manager_node | |

**Goal fields**:
- `use_vision` (bool): Use vision-guided target computation
- `plane_angle_deg` (float): Knife plane tilt angle
- `edge_align` (bool): Align knife spine with tofu edge
- `offset_a` (float): Horizontal offset from tofu corner
- `vertical_offset` (float): Height offset above tofu surface
- `timeout_s` (float): Max wait time for tofu state
- `candidate_count` (int): IK candidate count
- `preview_steps` (int): Cut preview steps for scoring
- `cut_depth` (float): Preview cut depth
- `safety_margin_deg` (float): Joint limit safety margin
- `joint_speed` (float): Joint move speed
- `arrival_tolerance_deg` (float): Arrival verification tolerance
- `arrival_timeout_s` (float): Arrival verification timeout
- `manual_target_pose` (geometry_msgs/Pose): Manual target (if use_vision=false)

**Feedback fields**:
- `current_phase` (string): Current execution phase
- `progress` (float): 0.0-1.0 progress
- `current_joints` (float[7]): Current joint angles

**Result fields**:
- `success` (bool): Operation success
- `message` (string): Status message
- `reached_joints` (float[7]): Final joint angles
- `reached_tcp_pose` (geometry_msgs/Pose): Final TCP pose
- `position_error_mm` (float): FK verification error

### Knife Cut

| Field | Value | Notes |
|-------|-------|-------|
| Action name | `/execute_knife_cut` | |
| Type | cuttofo_lbot_interfaces/ExecuteKnifeCut | |
| Server | knife_cut_action_server | |
| Client | phase_manager_node | |

**Goal fields**:
- `phase_name` (string): Phase identifier (PHASE_3_FIRST_CUT, PHASE_4_ROTATE_TOFU, PHASE_5_SECOND_CUT, PHASE_6_ROTATE_TOFU, PHASE_7_THIRD_CUT)

**Feedback fields**:
- `current_phase` (string): Current execution phase
- `progress` (float): 0.0-1.0 progress
- `waypoint_index` (uint32): Current waypoint index
- `waypoint_count` (uint32): Total waypoint count

**Result fields**:
- `success` (bool): Operation success
- `message` (string): Status message
- `executed_waypoints` (uint32): Number of executed waypoints
- `elapsed_s` (float): Execution time

## ROS2 Services (xCore Controller)

All services under arm namespace (`/arm_r` or `/arm_l`):

| Service | Type | Direction | Notes |
|---------|------|-----------|-------|
| `{ns}/robot/get_state` | dexbot_interfaces_low/GetRobotState | Client → Server | Returns flange pose + joint angles |
| `{ns}/robot/move_joints` | dexbot_interfaces_low/MoveJoints | Client → Server | Joint space motion |
| `{ns}/robot/move_rt_cartesian_path` | dexbot_interfaces_low/MoveRtCartesianPath | Client → Server | Cartesian path (impedance or position) |
| `{ns}/robot/enable_arm` | dexbot_interfaces_low/EnableArm | Client → Server | Enable/disable arm control |

### GetRobotState

**Request**: Empty
**Response**:
- `success` (bool)
- `message` (string)
- `cartesian_pose` (geometry_msgs/Pose): Flange pose in base frame
- `joint_positions` (float[7]): Current joint angles

### MoveJoints

**Request**:
- `target_joints` (float[7]): Target joint angles
- `speed` (float): Speed scale (0-1)
- `label` (string): Motion label

**Response**:
- `success` (bool)
- `message` (string)

### MoveRtCartesianPath

**Request**:
- `waypoints` (geometry_msgs/Pose[]): Cartesian waypoints
- `duration_s` (float): Path duration (0 = auto-compute)
- `speed_scale` (float): Speed scale
- `max_linear_velocity` (float): Max linear velocity (m/s)
- `max_acceleration` (float): Max linear acceleration (m/s²)
- `max_angular_velocity` (float): Max angular velocity (rad/s)
- `use_impedance` (bool): Use impedance mode
- `stiffness` (float[6]): Impedance stiffness [Kx, Ky, Kz, Krx, Kry, Krz]

**Response**:
- `success` (bool)
- `message` (string)
- `executed_steps` (uint32): Number of executed waypoints

### EnableArm

**Request**:
- `enable` (bool): Enable or disable

**Response**:
- `success` (bool)
- `message` (string)

## Communication Patterns

### Publisher-Subscriber (Async)
- Perception pipeline: RealSense → SAM3 → pose_estimator → tofu_state_node (continuous streaming)
- Phase manager: Subscribes to state signals, publishes phase state (0.5Hz timer)

### Action Client-Server (Goal-based)
- Phase manager → Prepare/Cut action servers (goal → feedback → result)
- Non-blocking: phase_manager sends goal async, continues ticking, handles result in callback

### Service Client-Server (Request-Response)
- XcoreArmAdapter → xCore services (synchronous calls with timeout)
- Used for: state queries, joint moves, cartesian paths, arm enable

## Message Formats

### TofuState (cuttofo_lbot_interfaces/TofuState)

| Field | Type | Notes |
|-------|------|-------|
| `header` | std_msgs/Header | frame_id="world" |
| `pose` | geometry_msgs/Pose | Tofu center pose |
| `extents` | float[3] | Tofu dimensions [x, y, z] |
| `confidence` | float | Detection confidence |
| `top_corners` | geometry_msgs/Point[4] | Top face corners (A,B,C,D order) |
| `edge_dir` | geometry_msgs/Vector3 | Right edge direction (A→B) |
| `tcp_target` | geometry_msgs/Point | TCP target position |
| `top_y` | float | Average Y of top corners |
| `is_valid` | bool | State validity flag |
| `object_id` | int | Detection ID |
| `health_state` | uint8 | HEALTH_TRACKING=0, HEALTH_STALE=1, HEALTH_LOST=2 |
| `stable_frames` | int | Consecutive stable frames |
| `last_update_age` | float | Seconds since last update |
| `source_status` | string | "tracking", "stale", "lost" |
| `lost_reason` | string | Reason for lost state |

### ObjectStateArray (dexbot_interfaces_mid/ObjectStateArray)

| Field | Type | Notes |
|-------|------|-------|
| `header` | std_msgs/Header | |
| `objects` | ObjectState[] | Detected objects |

### ObjectState (dexbot_interfaces_mid/ObjectState)

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Object ID |
| `class_id` | string | Class name ("tofu", "cutted_tofu") |
| `pose` | geometry_msgs/Pose | 6D pose |
| `confidence` | float | Detection confidence |
| `geometric_features` | float[] | [center(3), quat(4), extents(3), top_corners(12), ...] |
