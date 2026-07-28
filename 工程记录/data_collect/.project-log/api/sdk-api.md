# SDK API

## Linker Open TeleDex

调研阶段不直接调用 TeleDex SDK。以下为从项目记录中提取的**已知接口面**，完整 API 以平台官方文档为准。

### ROS2 话题（采集时）

| 接口 | 类型 | 说明 |
|------|------|------|
| `/{camera_name}/color/image_raw` | Topic | RGB 图像流 |
| `/{camera_name}/depth/image_raw` | Topic | 深度图像流 |
| `/left_arm_joint_state` | Topic | 左臂关节状态 |
| `/right_arm_joint_control` | Topic | 右臂关节控制 |
| `/cb_left_hand_state` | Topic | 左手状态 |
| `/cb_right_hand_control_cmd` | Topic | 右手控制指令 |

### 后处理文件 API（分析时）

| 接口 | 读取方式 | 说明 |
|------|----------|------|
| `telemetry.npz` | `numpy.load()` | 时间序列数组 |
| `camera_info.json` | `json.load()` | 相机标定 |
| `manifest.json` | `json.load()` | Episode 索引 |
| `metadata.json` | `json.load()` | 转换元信息 |

## TensorFlow Datasets (DROID 分析)

| 接口 | 用法 | 说明 |
|------|------|------|
| `tfds.builder('r2d2_faceblur', data_dir=...)` | Python API | 加载本地 DROID 数据 |
| `builder.as_dataset(split='train')` | Python API | 迭代 episode |

## Open Items

- TeleDex ROS2 消息类型未记录
- TeleDex Python SDK（如有）未在项目中使用或记录
