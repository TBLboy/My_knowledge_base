# Current Session

## Last Updated

- 2026-06-11 CST

## Current Objective

- **已完成**：`second_cross_cut` per-cycle 左臂 handoff + 并行回位（代码合入）。
- **当前阻塞**：全流程真机在 **hook_lift IK 预检**（cycle 1 waypoint 2）失败，尚未进入 RT / handoff。

## Current Business Logic Position

- Main path (v2): `prepare:second_cut` → `second_cross_cut:round_2`（每刀：RT → live handoff → 并行回位）→ …
- Current edge: `second_cross_cut` / hook_lift IK 预检（规划阶段，真机未动）
- Active branch: `cut_to_fo_featrue`
- Entry 常用: `workflow_entry:=second_cut_prepare`

## Per-Cycle Workflow（已实现）

```text
每轮 cycle 1..8:
  右臂 RT: cut + hook + transfer + reorient → 停
  左臂: live TCP/法兰 → handoff (FLANGE::)
  并行: 左 → left_wait_joints；右 → next_anchor（末轮 → human_wait）
```

## Completed This Session

1. `tofu_second_cross_cut_workflow.py`：按轮 RT、`_execute_left_handoff_live`、`_parallel_cycle_return`。
2. YAML：`left_wait_joint_positions`、`left_wait_joint_speed: 0.3`；`safety_margin_deg: 3.0`。
3. `debug_left_handoff` 此前真机通过（offset `[0.286105, -0.29242, 0.180583]`）。

## Current Blocker (hook_lift IK)

| 运行 | safety_margin | waypoint 2 误差 | 结果 |
|------|---------------|-----------------|------|
| 1 | 5° | pos 7.63mm, rot 6.49° | fail |
| 2 | 3° | pos 2.85mm, rot 2.87° | fail |

- 阈值：`POS_TOL_M=0.1mm`，`ROT_TOL_RAD≈0.06°`（`hook_lift_solver.py`）。
- `prepare second_cut`：`valid=2/63` seeds，预备位偏紧。
- `_DEBUG_STOP_AFTER_TRANSFER = False`（handoff 路径已启用）。

## Verification Status

- 代码构建：✅
- `debug_left_handoff`：✅（早前）
- `second_cross_cut` 全流程：❌ hook_lift IK cycle 1

## Files Changed (recent)

- `tofu_second_cross_cut_workflow.py`
- `tofu_second_cross_cut_params.yaml`

## Next Steps

1. 调 hook：放宽 IK 容差和/或 `hook_target_plane_angle_deg`、`hook_dy_m`、`second_cut.target_offset_m`。
2. `ros2 run cuttofo_skill_tofu_second_cross_cut debug_hook_lift`（prepare 后）。
3. IK 通过后复测 `second_cross_cut`，日志应有 8× `left handoff target candidate=`。
