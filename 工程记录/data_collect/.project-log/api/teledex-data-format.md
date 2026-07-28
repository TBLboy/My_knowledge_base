# Linker Open TeleDex 数据格式参考

> 来源：`doc/Linker Open TeleDex数据采集系统-数据说明文档 .pdf`（V3.0）
> 本文档为 QC 调研的工程记忆摘要，完整细节以官方 PDF 为准。

## 系统架构

```text
ROS2 实时采集 → raw/ (MCAP) → 前端触发转换 → processed/
```

- 原始数据：`raw/episode_XXXXXX/raw/raw_0.mcap`（可重复转换）
- 处理数据：`processed/<episode_dir>/`（三种转换：基础 / D2C / 彩色点云）
- 任务根目录：`collection_data/<task_name_YYYY-MM-DD_HH-mm-ss>/`

## 硬件配置（文档 V3.0）

| 组件 | 型号 |
|------|------|
| 机械臂 | Linker Arm LA7-01 / LA7-02（左右各 7-DOF） |
| 灵巧手 | O6 / L6 / L20 Lite / L20 / L25 |
| 遥操臂 | Linker TA |
| 手套 | TG / FFG / MCG |
| 头部相机 | Orbbec Gemini 335L |
| 腕部相机 | Orbbec Gemini 2 × 2 |
| RGB 分辨率 | 640×480 |
| 深度分辨率 | 640×400（D2C 后对齐到 640×480） |

## 相机命名

| camera_name | 处理后文件名前缀 |
|-------------|------------------|
| `top` | `cam_top` |
| `left_wrist` | `cam_left_wrist` |
| `right_wrist` | `cam_right_wrist` |

## processed 核心文件

每个 episode 处理结果包含：

| 文件 | 用途 |
|------|------|
| `telemetry.npz` | 对齐后遥测（QC 主数据源） |
| `camera_info.json` | RGB/深度/IMU 标定 |
| `manifest.json` | Episode 索引、fps、sync_error 汇总 |
| `metadata.json` | 对齐策略、转换配置、设备/录制汇总 |
| `cameras/*.mp4` | 三路 RGB 视频（H.264 CFR） |
| `cameras/*.timestamps.npy` | 视频帧 Unix 时间戳 |
| `cameras/*_depth/*.png` | 深度 PNG（uint16, mm, 0=无效） |

## telemetry.npz 完整字段

| 字段 | shape | dtype | 单位/含义 |
|------|-------|-------|-----------|
| `timestamps` | (N,) | float64 | Unix epoch 秒 |
| `qpos` | (N, D) | float32 | 关节位置（混合单位） |
| `qvel` | (N, D) | float32 | 关节速度 |
| `effort` | (N, D) | float32 | 力矩/力 |
| `actions` | (N, D) | float32 | 遥操控制指令 |
| `ee_poses_qpos_left/right` | (N, 7) | float32/64 | 基于 qpos 的末端位姿 [x,y,z,qx,qy,qz,qw] |
| `ee_poses_actions_left/right` | (N, 7) | float32/64 | 基于 actions 的末端位姿 |
| `imu_cam_top/left_wrist/right_wrist` | (N, 6) | float32 | [ax,ay,az,gx,gy,gz] |
| `sync_validation_is_valid` | (N,) | bool | 每帧同步有效性 |
| `sync_validation_max_diff` | (N,) | float64 | 每帧最大跨传感器时差 (ms) |
| `tactile_*` | 可选 | float32 | 触觉矩阵 (N,12,6) 或合力 (N,) g |

**D = left_arm_dof + right_arm_dof + left_hand_dof + right_hand_dof**

示例（双臂 7+7、双手 6+6，D=26）：
- `0:7` 左臂，`7:14` 右臂，`14:20` 左手，`20:26` 右手

### 单位语义（QC 必须区分）

| 子系统 | qpos/actions | qvel | effort |
|--------|--------------|------|--------|
| 机械臂 | rad | rad/s | N·m |
| 灵巧手 | 0~255 | 来自状态消息 | 来自状态消息 |

## 对齐参数（平台内置，metadata.json）

| 参数 | 值 | QC 含义 |
|------|-----|---------|
| `alignment.method` | `depth_anchored_fixed_fps` | 深度锚定固定帧率对齐 |
| `alignment.reference` | `synthetic_fixed_fps` | 合成固定帧率参考 |
| `alignment.max_time_diff_ms` | 22 | 同步容差上限 |
| `alignment.skip_initial_frames` | 0 | 不裁开头 |
| `alignment.skip_final_frames` | 30 | **平台已裁结尾 30 帧** |
| `manifest.sync_error` | avg_ms / max_ms / p95_ms | Episode 级同步误差统计 |
| `manifest.format_version` | 1.4 | 数据格式版本 |

## raw 话题清单

### 相机（每相机最多 7 话题）
- `/{camera_name}/color/image_raw` (sensor_msgs/Image, rgb8)
- `/{camera_name}/color/camera_info`
- `/{camera_name}/depth/image_raw` (16UC1, mm)
- `/{camera_name}/depth/camera_info`
- `/{camera_name}/gyro_accel/sample` (sensor_msgs/Imu)
- `/{camera_name}/accel/imu_info`
- `/{camera_name}/gyro/imu_info`

### 机械臂
- `/left_arm_joint_state`, `/right_arm_joint_state` → qpos/qvel/effort
- `/left_arm_joint_control`, `/right_arm_joint_control` → actions 臂段

### 灵巧手
- `/cb_left_hand_state`, `/cb_right_hand_state` → qpos/qvel/effort
- `/cb_left_hand_control_cmd`, `/cb_right_hand_control_cmd` → actions 手段

### 触觉（可选，collect_tactile 控制）
- `/cb_*_hand_matrix_touch` (12×6 矩阵, 0~255)
- `/cb_*_hand_matrix_touch_mass` (合力, g)

## 三种转换结果差异

| 转换类型 | 额外产物 |
|----------|----------|
| 基础转换 | RGB 视频 + 原始分辨率深度 PNG |
| D2C 转换 | 深度对齐到 RGB 坐标系（640×480） |
| 彩色点云 | D2C + `*_pointcloud/*.ply` |

QC 方案需明确针对哪种 processed 输出（建议默认 D2C 或基础转换）。

## QC 工作起点（平台已有能力）

平台**已内置**的基础 QC / 预处理：
1. 多模态时间对齐（depth_anchored_fixed_fps）
2. 每帧同步校验（`sync_validation_is_valid`, `sync_validation_max_diff`）
3. Episode 级同步误差统计（`manifest.sync_error`）
4. 结尾帧裁剪（`skip_final_frames=30`）
5. 原始话题消息量统计（`recording_info.json.topics_summary`）
6. 深度无效值标记（PNG 像素值 0）

**待补充的 QC**（调研目标）：
1. 开头/中间 idle frame 检测与裁剪
2. Action spike / jerk / saturation 检测（需分臂/手子系统）
3. qpos vs actions 跟踪误差
4. 视觉质量（模糊、遮挡、手部可见率）
5. 标定质量验证（重投影误差）
6. Episode 长度 / 成功率 / 任务语义标注
7. 触觉数据完整性（若启用）
