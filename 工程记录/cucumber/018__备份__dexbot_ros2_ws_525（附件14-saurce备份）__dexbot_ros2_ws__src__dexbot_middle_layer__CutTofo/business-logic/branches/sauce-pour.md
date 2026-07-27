# Branch: sauce-pour — 左臂浇酱技能

## Status

- candidate

## Purpose

- 在切豆腐流程结束后，控制左臂执行浇酱动作：抓取酱料瓶 → 抬升 → 移动到豆腐上方并倾斜 → 挤酱 → 放回瓶子 → 归位

## Start Node

- J（左臂示教轨迹采集完成 —— 瓶前就绪位姿）

## Target Node

- O（左臂回 home 完成）

## Logic Path

```text
J -> K -> L -> M -> N -> O
```

其中 K-a -> K-b 存在并行：

```text
K(L: lift) → K-b(L: vision lock + IK pour pose) → L
```

## Execution Chain

### Symbols

`[回放点位 N]` 表示该处数据来自第 N 号预留回放点位，由用户后续采集填充。

### Edge J->K：示教轨迹回放抓瓶

1. 加载 [回放点位 1] 的关节角度 JSON 序列（`phase_a.arm_trajectory`）
2. 使用 `XcoreDirectExecutor` 逐点 MoveJ 回放
3. TCP 到达瓶口后，按 [回放点位 2] `O6 set_angles(grasp_angle) + set_torques(grasp_torque)` 抓取

### Edge K->(K-a->K-b)->L：抬升 + 视觉引导倾倒

K-a:
1. 读取当前 TCP 位姿
2. 沿 base 坐标系 Y 负方向移动 `lift_distance_m`（笛卡尔线性移动）

K-b（法兰求解模式，不创建实际 TCP 坐标系）:
1. VisionGeometryTracker 锁豆腐中心 — 暂存在右臂 base 坐标系
2. **坐标变换**：`right_base_point_to_left(tofu_center_right, calib_path=left_calib_file)` → 左臂 base 坐标系
   - 迁移自 `cucumber_hold_workflow.py:260-268`，底层 `dual_arm_transform.py`
   - 变换参数：`R_LR = diag(1, -1, -1)`, `t_LR = [0, 0, -0.20]`（默认）
   - 配置文件：`sauce_pour_params.yaml:transform.left_calibration_file`
3. 计算 TCP 目标 = 左臂 base 下的豆腐中心 + `tcp_target_offset`
4. **法兰目标换算**：`flange_target_pos = tcp_target_pos - R_target @ tool_offset`
5. `solve_prepare_candidates` 接收入参为 **法兰目标** 位姿（非 TCP 目标）
6. IK 求解倾倒姿态（多候选 + 评分筛选），求解的是法兰关节角
7. MoveJ 到目标关节角 → 法兰到达目标位置 → 瓶口 TCP 自动到达豆腐中心

### Edge L->M：灵巧手周期性挤酱

1. 循环 squeeze_cycles 次：
2. 按 [回放点位 3] set_angles(squeeze_angle) + set_torques(squeeze_torque) → 收紧挤酱
3. sleep + 按 [回放点位 4] set_angles(squeeze_release_angle) + set_torques(squeeze_release_torque) → 稍松让酱流出
4. sleep

### Edge M->N->O：放瓶回原位 + 归位

1. MoveJ 回到 K-a 抬升后位置
2. 逆序回放 [回放点位 1]（`phase_a.arm_trajectory` 逆序执行）
3. 按 [回放点位 5] O6 set_angles(place_release_angle) + set_torques(place_release_torque) → 完全松开
4. MoveJ 按 [回放点位 6] 回 home 位姿

## Inputs

- 阶段 A：采集的关节轨迹（JSON）
- 阶段 B-b：`/cuttofu/perception/objects_with_pose`（豆腐位姿）
- 全部可调参数来自 `sauce_pour_params.yaml`

## Outputs

- Action Result（success/message/stage_path）
- 阶段 C 完成后不可逆（酱已挤出）

## Assumptions

- 瓶子放在固定位置（示教轨迹由此位置采集）
- 豆腐由切豆腐流程后留在原处，视觉可识别
- O6 灵巧手在 can1（左）
- 左臂 SDK 直连（`XcoreDirectExecutor`）

## Risks

- 瓶子放置位置被碰移位 -> 需要重新采集示教轨迹
- 豆腐被切碎后视觉锁可能不稳定 -> 需要设置 fallback 位置
- 挤酱时瓶子可能滑落 -> 灵巧手力矩参数需调优

## Open Questions

- 无（已全部在规划中明确）

## 预留回放点位总览

以下 6 处数据由用户后续采集填充，代码中留有 `TODO: [待填充]` 标记：

| # | 点位用途 | 数据类型 | 阶段 | 对应 YAML 路径 | 采集方法 |
|---|---------|---------|------|---------------|---------|
| 7 | **左臂准备位姿** | 7关节角(deg) | 流程起始 | `phase_ready.joint_positions_deg` | 准备就绪后记录 |
| 1 | 机械臂抓瓶轨迹 | n×7 关节角(deg) | A(正序), D(逆序) | `phase_a.arm_trajectory` | 拖动示教实时采样 → JSON |
| 2 | 灵巧手抓瓶闭合 | 6角度+6力矩 | A 末端 | `hand.grasp_angle/torque` | 调 O6 到手位后记录 |
| 3 | 灵巧手挤酱收紧 | 6角度+6力矩 | C 收紧 | `hand.squeeze_angle/torque` | 调 O6 到挤酱位后记录 |
| 4 | 灵巧手挤酱循环松开 | 6角度+6力矩 | C 松开 | `hand.squeeze_release_angle/torque` | 在挤酱位稍松后记录 |
| 5 | 灵巧手放瓶后松开 | 6角度+6力矩 | D 末端 | `hand.place_release_angle/torque` | O6 完全张开后记录 |
| 6 | 左臂 home 位姿 | 7关节角(deg) | E | `phase_e.home_joint_positions_deg` | 准备就绪后记录 |

## Verification Plan

1. 编译新包无错误
2. 启动 Action Server，ros2 action list 可见 /sauce_pour/execute
3. 实物验证各阶段到位

## Verification Result

- Not verified yet.

## Merge Condition

- 用户确认功能正常后合并

## TCP Offset 法兰求解模式

**核心原则**：不调用机器人控制器的 "创建 TCP 坐标系" API，`tool_offset` 仅作为数学参数使用。

### 数学关系

- 法兰位姿 → TCP 位姿：`tcp_pos = flange_pos + R_flange @ tool_offset`
- TCP 目标 → 法兰目标：**`flange_target_pos = tcp_target_pos - R_target @ tool_offset`**
- 法兰目标姿态 = TCP 目标姿态（纯平移 offset 时等同）

### 实现流程

```text
vision(豆腐中心) → tcp_target → flange_target(数学换算) → IK求解(法兰) → MoveJ(法兰)
```

### 参考代码实现位置

- `xcore_arm_adapter.py:153`: `flange_target_pos = target_pos - target_R @ tcp_offset`
- `xcore_direct_executor.py:387-415`: `flange_pose6_from_tcp_goal()` — 完全相同数学
- `xcore_direct_executor.py:312-332`: `build_locked_flange_waypoints()` — 当 `tool_offset ≠ 0` 时做换算，否则直接透传
- `tofu_prepare_workflow.py:146-168`: `solve_prepare_candidates(kin, target_pos=flange_target_pos, ...)` — IK 入参是法兰目标，非 TCP 目标

### 鲁棒性优势

- 不依赖机器人控制器的 TCP 坐标系状态，避免因 TCP 切换/未定义导致控制失败
- `tool_offset` 为纯配置值，可通过 YAML 参数热调
- 与现有 `cucumber_hold`（左臂）和 `tofu_prepare`（右臂）采用完全一致的数学模式

## Notes

- 包名：`cuttofo_skill_sauce_pour`
- 参考迁移来源：`cucumber_hold`（法兰求解、SDK executor）、`prepare_solver`（IK 求解）、`tofu_prepare_workflow`（视觉+IK 全流程）、`VisionGeometryTracker`（视觉锁定）
