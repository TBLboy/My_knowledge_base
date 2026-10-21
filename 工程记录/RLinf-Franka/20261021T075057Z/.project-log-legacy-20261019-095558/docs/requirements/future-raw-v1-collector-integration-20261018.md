# future-raw-v1 真实采集接入边界

## 目的

为现有 Pico/Franka 采集链增加 opt-in 的封存 raw 输出，不改变控制语义、legacy pickle、RLinf 核心或硬件配置。真实采集前必须先完成离线 fixture 与 dry-run 验证。

## 已确认来源

| future-raw 字段 | 当前来源 | 结论 |
|---|---|---|
| `measured_joint_position[7]` | `infos[*].passive_franka_step.measured_joint_position` | 仅 passive telemetry 可用 |
| `measured_eef_pose[7]` | `infos[*].passive_franka_step.measured_tcp_pose` | 仅 passive telemetry 为明确来源 |
| `final_post_guard_target[7]` | `infos[*].passive_franka_step.final_franka_target` | 作为 action 的权威来源 |
| gripper | `observations[*].gripper_position` 或明确 observation 字段 | 接入时必须显式抽取，不从扁平 state 猜测 |
| action samples | 每个 transition 的 `passive_franka_step` | 缺失即封存失败 |
| Pico/camera timestamps | 当前 pickle 无完整 per-sensor 时间轴 | 必须由新 recorder 采集并记录 |
| camera frames | `observations[*].main_images` / `extra_view_images` | 需绑定稳定 sensor key、frame ref 和 batch-relative timestamp |
| terminal outcome | keyboard event、success、terminated/truncated | 新 recorder 必须生成单一 terminal provenance |

## 不允许的替代

- 不使用 pickle 顶层 `actions` 作为 teleoperation action；该字段已知可能恒为零。
- 不使用 `intervene_action` 冒充 absolute post-guard EEF target。
- 不从旧 pickle 猜统一起点、相机时间戳或 terminal 精确时刻。
- 缺少 passive telemetry、相机时间戳或封存完整性时 fail-closed，不补零、不导出。

## 接入边界

新 recorder 应在 `RLinf-Franks/rlinf_ext` 中 opt-in 接入现有 wrapper 生命周期；控制代码和 `CollectEpisode` legacy pickle 保持不变。它必须写临时 batch，完成 manifest/schema/hash 校验后原子封存为 sealed `future-raw-v1`。未封存或校验失败的目录不得作为 converter 输入。

真实采集启动前，用户必须确认：新 recorder dry-run 通过、两路相机均有时间戳与 frame ref、每个动作步有 measured q/TCP/final target、episode outcome 可追溯。当前不自动连接或操作硬件。
