# 两段式安全运动 — 实现规划

**创建时间**: 2026-06-15
**状态**: 待实施
**触发背景**: `move_cartesian` 在 6-DOF 联合插值路径上刮蹭豆腐

---

## Context

真机测试发现：`move_cartesian` 可以正确到达目标，但 6-DOF 位姿联合同步插值导致刀尖在路径上刮蹭豆腐。

**解决方案**：在笛卡尔空间插入安全中间点，将一次 6-DOF 联合运动拆成两段无碰撞的独立运动：

```
Phase 1: 当前位置 ──→ 安全中间点（位置=target+基座系偏移，姿态=目标姿态）
Phase 2: 安全中间点 ──→ 目标位置（姿态不变，纯平移）
```

两段均使用控制器 `compute_ik`（硬件标定 FK + WeightedIK）求解 + `move_to_joints`（关节空间弧线）执行。完全不用离线 URDF。

---

## 关键资源（已有，直接复用）

| 资源 | 位置 | 状态 |
|------|------|------|
| `ComputeIK.srv` | `dexbot_interfaces_low/srv/ComputeIK.srv` | 已定义 |
| `/dexbot/motion/compute_ik` 服务 | `motion_planner_node.py:60` | 已运行，`pick_place_action_server` 已在用 |
| `WeightedIK` 求解器 | `lbot_catch/weighted_ik.py` | 已集成硬件 FK |
| `XcoreArmAdapter` | `xcore_arm_adapter.py` | 有 `move_to_joints`/`get_joints`/`get_tcp_pose`，缺 `compute_ik` |
| `RobotController.make_fk_func()` | `xcore_controller/` | 提供 SDK `calcFk` 校准后的 FK |

---

## 实现改动

### 1. `xcore_arm_adapter.py` — 新增 `compute_ik()` 方法

**文件路径**: `cuttofo_skill_common/cuttofo_skill_common/arm/xcore_arm_adapter.py`

**改动点**：

- 导入 `ComputeIK` from `dexbot_interfaces_low.srv`
- `__init__` 中创建 `_compute_ik_cli` → `/dexbot/motion/compute_ik`
- `connect()` 中等待 `compute_ik` 服务（设为可选，不可用时 warn 不 fail）
- 新增 `compute_ik(target_pos, target_R, seed_joints, pos_tolerance, ori_tolerance, timeout_s)` 方法：
  - 入参：target_pos (法兰位置, 3D), target_R (3x3 姿态矩阵), seed_joints (可选 7D), tolerances
  - 构建 `ComputeIK.Request`：position → Pose, 姿态 → quaternion, seed → float64[]
  - 调用服务，解析 response，返回 `(success, joints)`

---

### 2. `tofu_prepare_workflow.py` — 两段式编排

**文件路径**: `cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py`

**改动点**：

```
当前流程 (纯离线 URDF IK):
  vision → target_pos/target_R → solve_prepare_candidates (least_squares, 40 seeds)
  → rollout_cut_preview + scoring → move_to_joints → verify → return

新流程 (纯控制器 IK):
  vision → target_pos/target_R → flange_target_pos
    ↓
  Phase 1: 安全中间点对齐姿态
    safe_tcp = target_pos + [0, offset_y, offset_z]    ← 基座坐标系偏移
    safe_flange = safe_tcp - target_R @ tcp_offset
    compute_ik(safe_flange, target_R, seed=current_joints)
    → move_to_joints → verify
    ↓
  Phase 2: 锁定姿态纯平移
    compute_ik(flange_target_pos, target_R, seed=phase1_joints)  ← 热启动
    → move_to_joints → verify → return
```

**阶段详情**：

**Phase 1** — "安全中间点":
- `safe_waypoint_tcp = target_pos + np.array([0.0, offset_y, offset_z])`
  - offset_y: 沿 base Y 正方向（向上），如 0.05m
  - offset_z: 沿 base Z 正方向（向右/远离豆腐），如 0.05m
- 转换为 flange 坐标：`safe_flange = safe_waypoint_tcp - target_R @ tcp_offset`
- `compute_ik(safe_flange, target_R, seed=current_joints, pos_tol=0.005, ori_tol=0.003)`
- `move_to_joints(phase1_joints)` + `verify_arrival`
- 失败 → 直接 return fail（无 fallback，全走控制器）

**Phase 2** — "纯平移到目标":
- `compute_ik(flange_target_pos, target_R, seed=phase1_joints, pos_tol=0.003, ori_tol=0.003)`
  - 热启动：Phase 1 的解离目标只差平移，收敛极快
- `move_to_joints(phase2_joints)` + `verify_arrival`
- TCP 位姿验证：`get_tcp_pose()` → 位置误差检查 → 返回

**移除的内容**：
- 删除 `OfflineURDFKinematics` 创建（原第 134-139 行）
- 删除 `solve_prepare_candidates()` 调用（原第 159-167 行）
- 删除 preview rollout + scoring 循环（原第 175-199 行）
- 删除 `prepare_solver` 中所有函数的调用
- 删除 `candidate_count`、`preview_steps`、`ik_retry_count` 等离线 IK 参数的使用

---

### 3. `tofu_prepare_params.yaml` — 新增安全中间点偏移参数

**文件路径**: `cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml`

每个 profile 新增两个字段：

```yaml
profiles:
  first_cut:
    ...
    safe_waypoint_offset_y: 0.05    # base Y+ 方向偏移 (m)，向上
    safe_waypoint_offset_z: 0.05    # base Z+ 方向偏移 (m)，向右远离
```

不同 profile 可以独立设置偏移量。如 `after_rotation_1`（竖切）豆腐朝向不同，可能需要调整偏移方向/大小。

---

### 4. 不需要改动的文件

| 文件 | 原因 |
|------|------|
| `prepare_solver.py` | 不再使用，但保留作为离线参考 |
| `motion_planner_node.py` | 已有 `compute_ik` 服务，无需改动 |
| `xcore_controller_node.py` | 不需要在其上新增服务 |
| `OfflineURDFKinematics` | 不再使用 |
| `ExecuteTofuPrepare.action` | Goal 字段已够用（新增参数走 profile YAML） |

---

## 文件改动清单

| 文件 | 改动量 | 说明 |
|------|--------|------|
| `xcore_arm_adapter.py` | +55 行 | 新增 `compute_ik()` + 客户端 |
| `tofu_prepare_workflow.py` | +60 / -80 行 | 两段编排替换离线多候选 |
| `tofu_prepare_params.yaml` | +10 行 | 每个 profile 加 2 个偏移参数 |

---

## 安全性分析

| 风险 | 缓解 |
|------|------|
| Phase 1 IK 不收敛 | 多种子重试（current_joints, Q_HOME, joint_center, random），3 次失败则整体失败 |
| Phase 1 中间点仍碰到豆腐 | offset 参数按 profile 独立可调，可逐步增大直到安全 |
| Phase 2 IK 不收敛 | Phase 1 解热启动，收敛率极高 |
| 控制器 FK 标定误差 | 误差量级 1-2°，Phase 2 纯平移不依赖姿态变化，误差不会放大 |
| `compute_ik` 服务超时 | 单次调用 ~1-3s（WeightedIK 收敛快），timeout 设 10s 足够 |

---

## 验证步骤

1. 真机测试 `first_cut` profile：确认 Phase 1 刀在豆腐上方安全距离对齐姿态，Phase 2 直下不刮豆腐
2. 调整 `safe_waypoint_offset_y/z` 直到找到合适的安全距离
3. 测试 `after_rotation_1`（竖切）：确认 90° 平面角下偏移方向仍然安全
4. 对比 `move_cartesian` 原方案的 TCP 位姿精度

---

## 关联决策记录

- **Direct xCore SDK Control** (decision-records.md, 2026-06-06) — 使用 SDK 原生 FK 而非 ROS 2 control
- **两段式安全运动设计** (本次计划) — 拆分 6-DOF 联合运动避免笛卡尔轨迹刮蹭

---

## 下一步

用户指示：当前仅存档，后续修改时再实施。