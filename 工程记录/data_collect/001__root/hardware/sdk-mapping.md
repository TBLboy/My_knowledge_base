# SDK Mapping

| Hardware | Model | SDK / Driver | Version | API / Interface | Purpose | Notes |
|----------|-------|--------------|---------|-----------------|---------|-------|
| Linker Arm LA7 | LA7 | Linker Open TeleDex (ROS2) | Unknown | `/left_arm_joint_state` 等 | 臂状态/控制采集 | 版本待确认 |
| Linker Hand | O6/L6/L20/L25 | Linker Open TeleDex (ROS2) | Unknown | `/cb_left_hand_state` 等 | 手状态/控制采集 | 型号因 episode 而异 |
| Orbbec Gemini 335L | 335L | Orbbec SDK (via TeleDex) | Unknown | `/{camera_name}/color/image_raw` | 外部 RGB-D | 通过 TeleDex 集成 |
| Orbbec Gemini 2 | Gemini 2 | Orbbec SDK (via TeleDex) | Unknown | `/{camera_name}/depth/image_raw` | 腕部 RGB-D | 通过 TeleDex 集成 |
| 遥操作手套 | TA+TG/FFG/MCG | Linker Open TeleDex | Unknown | 遥操作接口（待确认具体话题） | 动作采集 | 话题名待确认 |

## Analysis Tools (DROID Research)

| Tool | Package | Version | Purpose |
|------|---------|---------|---------|
| TensorFlow Datasets | `tensorflow-datasets` | Unknown | 加载 DROID TFRecord |
| TensorFlow | `tensorflow` | Unknown | TFRecord 解析 |
| Matplotlib | `matplotlib` | Unknown | 可视化 |
| NumPy | `numpy` | Unknown | 数值分析 |

环境由 `scripts/droid/setup_droid_env.sh` 管理，具体版本未锁定记录。

## Notes

- TeleDex SDK 版本号未在项目中记录，实施阶段需向平台方确认
- DROID 分析工具版本不影响调研结论，但复现分析时需记录环境
