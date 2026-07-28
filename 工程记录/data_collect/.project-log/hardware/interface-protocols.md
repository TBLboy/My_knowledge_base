# Interface Protocols

## ROS2 (Linker TeleDex 采集阶段)

- 协议：ROS2 话题发布/订阅
- 录制格式：MCAP
- 中间件：Unknown（待确认 ROS2 distro，如 Humble / Iron）

### 已知话题模式

详见 `architecture/communication.md`。

### 待确认

- 完整话题列表
- 消息类型（`sensor_msgs/Image`、`sensor_msgs/JointState` 等具体类型）
- 采集频率（Hz）
- 时间戳来源（系统时钟 / 硬件同步）

## Processed Data Protocol (后处理产物)

### telemetry.npz

NumPy 压缩数组，完整 schema 见 `api/teledex-data-format.md`。

| 字段 | shape | QC 相关 |
|------|-------|---------|
| `timestamps` | (N,) float64 | 时间轴、帧率检查 |
| `qpos` | (N, D) float32 | idle 检测、范围检查、跟踪误差 |
| `qvel` | (N, D) float32 | 运动平滑性、spike |
| `effort` | (N, D) float32 | 力矩异常 |
| `actions` | (N, D) float32 | spike、saturation、jerk、跟踪误差 |
| `ee_poses_qpos_*` | (N, 7) | 末端轨迹质量 |
| `ee_poses_actions_*` | (N, 7) | 命令轨迹质量 |
| `imu_cam_*` | (N, 6) | IMU 一致性（若启用） |
| `sync_validation_is_valid` | (N,) bool | **硬性过滤** |
| `sync_validation_max_diff` | (N,) float64 ms | **同步阈值** |
| `tactile_*` | 可选 | 触觉完整性（若 collect_tactile） |

D = left_arm_dof + right_arm_dof + left_hand_dof + right_hand_dof。臂用 rad，手用 0~255。

### camera_info.json

相机标定信息（内参、外参）。用于：
- 重投影误差 QC
- 多视角几何一致性

### manifest.json

Episode 级快速索引。已知含 `sync_error` 字段。

### metadata.json

转换与对齐元信息。已知含 alignment 参数和 `sync_error`。

## DROID RLDS / TFRecord

- 格式：RLDS（通过 TFDS 加载）
- 注册名：`r2d2_faceblur`
- Episode 结构：`episode_metadata` + `steps`
- Step 字段：observation（3 路图像 + 状态）、action（7 维）、language_instruction

详见 `scripts/droid/README.md`。
