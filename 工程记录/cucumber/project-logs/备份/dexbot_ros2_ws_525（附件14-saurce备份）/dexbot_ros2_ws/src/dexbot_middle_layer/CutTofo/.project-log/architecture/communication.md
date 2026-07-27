# Communication Architecture

## ROS 2 Topics

| Topic | Type | Pub | Sub | Notes |
|-------|------|-----|-----|-------|
| `/cuttofu/vision/text_prompt` | `std_msgs/String` | Skill | SAM3 Detector | 切换 SAM 识别目标 |
| `/cuttofu/perception/detected_objects` | `dexbot_interfaces/DetectedObjectArray` | SAM3 Detector | Pose Estimator | SAM 原始分割结果 |
| `/cuttofu/perception/objects_with_pose` | `dexbot_interfaces/DetectedObjectArray` | Pose Estimator | Skills | 含 6D 位姿 + 角点 |
| `/joint_states` | `sensor_msgs/JointState` | xCore SDK | Various | 双臂关节状态 |
| `/camera/color/image_raw` | `sensor_msgs/Image` | RealSense | SAM3 | 彩色图 |
| `/camera/aligned_depth_to_color/image_raw` | `sensor_msgs/Image` | RealSense | Pose Estimator | 对齐深度图 |
| `/camera/color/camera_info` | `sensor_msgs/CameraInfo` | RealSense | Pose Estimator | 相机内参 |

## ROS 2 Actions

| Action Server | Action Type | Skill Node | Profile |
|---------------|-------------|------------|---------|
| `/handle_approach/execute` | `ExecuteHandleApproach` | `handle_approach_node` | default |
| `/tofu_prepare/execute` | `ExecuteTofuPrepare` | `tofu_prepare_node` | first_cut, after_rotation_1, after_rotation_2, cucumber |
| `/tofu_cut_round/execute` | `ExecuteTofuCutRound` | `tofu_cut_round_node` | round_1, round_2, cucumber |
| `/tofu_vertical_cut/execute` | `ExecuteTofuVerticalCut` | `tofu_vertical_cut_node` | default |
| `/cucumber_hold/execute` | `ExecuteCucumberHold` | `cucumber_hold_node` | default, release |

## ROS 2 Services

| Service Server | Service Type | Provider | Notes |
|---------------|-------------|----------|-------|
| `/tofu_cut_round/resume` | `ResumeTofuCutRound` | cut_round node | 人工转豆腐后继续 |
| `/cuttofo_operator/continue` | `std_srvs/Trigger` | Orchestrator | 操作员确认继续 |

## External SDK / API

| SDK | Version | Usage | Communication |
|-----|---------|-------|---------------|
| xCore SDK Python | v0.5.1.ar_12 | 机械臂控制 | TCP/IP (proprietary protocol) |
| LinkerHand O6 | — | 灵巧手控制 | CAN bus raw frames |
| librealsense2 | — | RealSense 驱动 | USB3 |
