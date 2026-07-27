# Current Session

## Last Updated

- 2026-06-16 (续接上一 session)

## Current Objective

- 两段式安全运动 — **已实现完成，待真机验证**

## Current Business Logic Position

- prepare workflow 新增 `ik_mode` 分支：
  - `online`（默认）：两段式控制器 IK（Phase 1 安全中间点 + Phase 2 纯平移）
  - `offline`（回退）：原有离线 URDF 多候选选优逻辑保留不变
- Active branch: CutTofu_Release (commit 1d64bb10)

## Completed This Session

### 上次 session (2026-06-15)

1. **代码库恢复**: 重置到 f7211746（六月12日晚上）
2. **问题诊断**: `move_cartesian` 刮蹭豆腐
3. **方案设计**: 两段式安全运动
4. **实现规划存档**: `prepare-two-phase-online-ik-plan.md`

### 本次 session (2026-06-16)

1. **xcore_arm_adapter.py — 新增 `compute_ik()` 方法**
   - 新增 `ComputeIK` 服务客户端 → `/dexbot/motion/compute_ik`
   - `connect()` 等待服务（可选，不可用时 warn）
   - `compute_ik(target_pos, target_R, seed_joints, ...)` 方法 (~50 行)

2. **tofu_prepare_workflow.py — 双路径编排**
   - 新增 `ik_mode` / `safe_waypoint_offset_y` / `safe_waypoint_offset_z` 参数读取
   - **offline 分支**: 原有离线 URDF IK 多候选逻辑完全保留
   - **online 分支**:
     - Phase 1: 安全中间点 `compute_ik` → `move_to_joints` → `verify_arrival`
     - Phase 2: 目标点热启动 `compute_ik` → `move_to_joints` → `verify_arrival`

3. **tofu_prepare_params.yaml — 配置参数**
   - 顶层新增: `ik_mode: online`, `safe_waypoint_offset_y: 0.05`, `safe_waypoint_offset_z: 0.05`

4. **编译验证**: `colcon build` 成功 ✓

## Files Modified

| 文件 | 改动 |
|---|---|
| `cuttofu_skills/cuttofo_skill_common/.../xcore_arm_adapter.py` | +55 行：ComputeIK 客户端 + compute_ik() 方法 |
| `cuttofu_skills/cuttofo_skill_tofu_prepare/.../tofu_prepare_workflow.py` | +55 行：online IK 两段式分支，保留 offline 回退 |
| `cuttofu_skills/cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml` | +3 行：ik_mode + offset 默认值 |

## Verification

- 编译成功 ✓
- 代码结构：offline 路径完全保留，online 路径新增（默认激活）

## Next Steps

1. **真机验证 first_cut**：确认 Phase 1 刀在豆腐上方对齐姿态 → Phase 2 直下到位不刮豆腐
2. **调整 safe_waypoint_offset_y/z**：根据实际效果微调安全距离
3. **验证 after_rotation_1**：竖切 profile 下偏移方向仍安全
4. **回退测试**：设置 `ik_mode: offline`，确认离线多候选路径仍正常工作

## Usage

切换 IK 模式（在 profile 中设置）：
```yaml
# 使用 online 两段式 IK（默认）
ik_mode: online

# 回退到 offline 离线 URDF IK
ik_mode: offline
```