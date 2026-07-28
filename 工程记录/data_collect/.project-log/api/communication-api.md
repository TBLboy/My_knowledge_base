# Communication API

## Linker TeleDex 数据文件通信

Episode 级数据以目录 + 文件形式组织（具体目录结构以 TeleDex 文档为准）：

```text
<episode_dir>/
├── telemetry.npz
├── camera_info.json
├── manifest.json
├── metadata.json
└── videos/
    └── <camera_name>.mp4  (或类似命名，待确认)
```

## 跨系统数据对照

调研需建立的映射关系（B->C 和 C->D 的核心工作）：

| DROID 字段 | Linker TeleDex 对应 | QC 用途 |
|------------|---------------------|---------|
| `steps.action` [7] | `telemetry.npz` actions | spike、saturation、jerk |
| `steps.observation.joint_position` | `telemetry.npz` qpos | idle 检测、范围检查 |
| `steps.observation.joint_velocity` | `telemetry.npz` qvel | 运动平滑性 |
| `language_instruction` | metadata 中任务描述（待确认字段名） | 语义完整性 |
| 3 路相机图像 | videos + camera_info.json | 视觉质量、标定 |
| episode 边界标记 | manifest.json（待确认） | 长度、idle 裁剪 |
| 同步质量 | sync_validation_* / sync_error | 硬性过滤 |

## DROID RLDS Step Schema

```text
step:
  observation:
    exterior_image_1_left: [180, 320, 3] uint8
    exterior_image_2_left: [180, 320, 3] uint8
    wrist_image_left:      [180, 320, 3] uint8
    cartesian_position:    [6]
    joint_position:        [7]
    gripper_position:      [1]
  action:                  [7]
  language_instruction:    string
  is_first / is_last / is_terminal: bool
```

## Notes

- TeleDex 与 DROID 的动作空间维度不同（灵巧手 vs 7-DOF 臂+夹爪），QC 规则迁移时需调整维度和阈值
- 部分 DROID QC 规则（如夹爪 saturation）需重新定义为灵巧手关节 saturation
