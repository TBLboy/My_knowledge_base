# Communication Architecture

## Linker TeleDex (ROS2)

数据采集阶段使用 ROS2 话题通信，录制为 MCAP 格式。

### 相机话题

| 话题模式 | 说明 |
|----------|------|
| `/{camera_name}/color/image_raw` | RGB 图像 |
| `/{camera_name}/depth/image_raw` | 深度图像 |

`camera_name` 具体值需从实际采集配置或 `camera_info.json` 确认。

### 机械臂话题

| 话题 | 方向 | 说明 |
|------|------|------|
| `/left_arm_joint_state` | 状态 | 左臂关节状态 |
| `/right_arm_joint_control` | 控制 | 右臂关节控制（示例，以实际文档为准） |

### 灵巧手话题

| 话题 | 方向 | 说明 |
|------|------|------|
| `/cb_left_hand_state` | 状态 | 左手状态 |
| `/cb_right_hand_control_cmd` | 控制 | 右手控制指令 |

## Processed Data Files (Post-Recording)

后处理产物不通过 ROS 通信，以文件形式存储：

| 文件 | 格式 | 用途 |
|------|------|------|
| `telemetry.npz` | NumPy 压缩数组 | 时间序列：关节、速度、动作等 |
| `camera_info.json` | JSON | 相机内参/外参标定 |
| `manifest.json` | JSON | Episode 快速索引、同步误差摘要 |
| `metadata.json` | JSON | 转换信息、对齐参数 |
| videos | 视频文件 | 各相机录制视频 |

## DROID Analysis (Local)

DROID 分析脚本不依赖 ROS，直接读取本地 TFRecord（TFDS / RLDS 格式）：
- 数据路径：`data/droid/droid_100/`
- TFDS 注册名：`r2d2_faceblur`

## Notes

- ROS2 话题完整列表以 Linker Open TeleDex 数据说明文档为准
- 调研阶段仅记录已知话题模式，不维护实时通信代码
