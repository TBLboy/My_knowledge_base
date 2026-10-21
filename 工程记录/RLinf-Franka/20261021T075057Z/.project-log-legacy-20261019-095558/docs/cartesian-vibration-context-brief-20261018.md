# Franka Pico 遥操作 Cartesian 震动问题简报

## 1. 目标与当前问题

目标是实现平顺、可用的 Pico → Franka 单臂真机遥操作。

当前主要问题：

> Cartesian impedance 模式跟踪较流畅，但整臂震动；需要确定震动根因并设计下一项最小单变量实验。

连续 IK → joint impedance 路线已停止作为 Pico 主路线：震动有所减轻，但跟踪卡顿，不适合当前遥操作体验。

## 2. 当前 Cartesian 控制链路

```text
Pico 手柄
  ↓
XRoboToolkit IPC
  ↓
PicoExpert 生成位姿增量
  ↓
FrankaEnv.step()
  ↓
当前 TCP pose + action_scale × 增量
  ↓
FrankaEnv._move_action()
  ↓
RemoteFrankyArm.send_action({"tcp_pose": target})
  ↓ RPC
FrankyArmWorker
  ↓
CartesianImpedanceTracker.set_target()
  ↓
libfranka 100Hz torque 控制
```

主要配置：

- `action_scale = [0.04, 0.3, 1.0]`
- Cartesian 外层环境频率历史上约为 10Hz
- 平移刚度 `K_t = 1200 N/m`
- 平移 clip 约 `0.02m`
- 旋转刚度 `K_r = 80 Nm/rad`
- 旋转 clip 当前约 `0.15rad`
- `max_step = 0.08m`
- `max_step_rad = 0.20rad`
- 未修改 Desk SLS-C、SLP-C、碰撞阈值或安全限制

## 3. 已确认事实

### 3.1 震动不只来自 Pico

隔离 Cartesian Reset 轨迹时也出现震动。Reset 不依赖 Pico 输入，因此 Pico 数据到达问题不是当前首要根因。

已观察到：

- Cartesian 遥操作时会震动；
- 隔离 Cartesian Reset 移动时也会震动；
- 固定目标停留时明显更安静；
- 移动目标时整臂震动；
- 当前应按“整臂震动”处理，不采用早期“只有 J7 明显”的说法。

### 3.2 Cartesian 与 joint impedance 对比

- Cartesian impedance：跟踪流畅，但震动；
- joint impedance reset：相对平稳；
- joint_ik → joint impedance：震动减轻，但 Pico 跟踪卡顿，因此停止作为 Pico 主路线。

## 4. 已完成的相关实验

### RESET-004：固定目标停留

- 固定目标期间整体较安静；
- 个别段仍有继续收敛；
- 说明移动目标下的动态响应值得重点关注；
- 不能据此证明静态控制完全无问题。

### RESET-005：目标更新频率 10Hz → 50Hz

- 未改善整体震动；
- 日志实际目标频率约 45Hz；
- 不能简单把根因归因于 10Hz 更新频率。

### RESET-008：Cartesian 单遍连续目标轨迹

- 用户反馈仍然严重整臂震动；
- 不能归因于重复发送、自动重试或段间跳变；
- 日志中实际跟踪误差仍有数度级别；
- 目标轨迹本身尚未证明是唯一根因。

### RESET-009：Cartesian 速度前馈

- 用户反馈震动加重；
- 方案停止，不再推荐；
- 默认保持关闭；
- 该实验未完整跑完，不能据此确定精确控制公式是根因。

## 5. 负载与坐标系只读检查

READ-010 快照显示：

- `m_ee = 1kg`
- `m_load = 0`
- 总质心法兰坐标约 `[0.05, 0, 0.057]m`
- TCP 相对法兰约沿 z 轴 `+0.16m`
- `NE_T_EE`、`EE_T_K` 为单位阵
- Idle 时 `errors=[]`

Idle 下 `control_command_success_rate=0` 不能推断运动丢包或实时性故障。

这些是控制器配置值，不是物理称量或标定结果。尚未确认：

- 1kg 是否包含 Robotiq、支架、腕部相机等全部附件；
- TCP `+0.16m` 是否与实际被控点完全一致。

因此暂不能把负载或坐标系问题认定为根因。

## 6. 建议的下一步

下一步不再排查 Pico 输入，也不先盲调刚度、力矩或 Desk 参数。

建议做一次**不改控制参数的 Cartesian Reset 被动遥测对照**：

1. 复用 A → B → C → D → E → A 轨迹；
2. 记录移动段；
3. 每个点固定停留几秒作为对照；
4. 对比移动目标与固定目标。

建议记录：

- Cartesian target；
- target 发送时间与间隔；
- 实际 TCP pose；
- TCP 位置/姿态误差；
- 关节位置 `q`；
- 关节速度 `dq`；
- 如果可获得，记录 torque、`dtau` 或控制器跟踪状态；
- target 发送、机器人读取和整步耗时。

### 需要区分的候选原因

| 现象 | 候选解释 |
|---|---|
| target 自身阶梯或跳变 | Reset 目标生成、限幅或插值问题 |
| target 平滑但 q/dq 周期振荡 | Cartesian impedance 动态响应或零空间耦合 |
| TCP 误差周期性放大 | 刚度、阻尼、滤波或 torque slew 耦合 |
| 固定目标安静、移动目标震动 | 移动目标下的动态响应问题 |
| 某些姿态或方向明显更严重 | 负载、TCP 杠杆、姿态耦合或零空间问题 |

## 7. 当前未知项

1. 震动主频与 Cartesian tracker、目标更新和 libfranka torque loop 的关系；
2. 实际 target 是否平滑；
3. target 与实际 TCP 的相位延迟；
4. q/dq 是否在震动频率上出现同步尖峰；
5. 零空间目标保持当前 q 是否造成整臂耦合；
6. 当前负载/TCP 配置是否与真实夹具、相机和支架一致；
7. `max_delta_tau`、内部滤波和 Cartesian tracker 动态参数的实际贡献；
8. 震动是否集中发生于特定姿态、方向或速度区间。

## 8. 约束

- 主目标是平顺、可用遥操作，不追求零跟踪误差；
- 不新增“误差超阈值暂停/重新握持”门禁；
- 不提高旋转力矩、角速度、全局 dynamics factor、torque slew 或 Desk 限制；
- 真机实验只能由操作者执行；
- 每次只改一个变量；
- 先取得被动证据，再决定参数或控制结构改动；
- 默认 Cartesian 模式保持不变；
- joint_ik 代码保留为 opt-in 实验记录，但停止作为 Pico 主路线继续优化。

## 9. 相关文件

- `.project-log/current-session.md`
- `杂项/reset_lab/EXPERIMENT_LOG.md`
- `TELEOP_TUNING_LOG.md`
- `RLinf/rlinf/robotics/parts/arms/franky.py`
- `RLinf/rlinf/envs/real/franka/base.py`
- `RLinf-Franks/rlinf_ext/collection.py`
- `RLinf-Franks/run_pico_session.sh`
