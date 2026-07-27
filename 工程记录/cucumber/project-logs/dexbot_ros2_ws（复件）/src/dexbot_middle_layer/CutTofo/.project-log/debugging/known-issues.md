# Debugging Records

## Known Issues

### 2026-06-11 - second_cross_cut hook_lift IK 预检失败（阻塞全流程）

- Related: `cuttofo_skill_tofu_second_cross_cut` / `hook_lift_solver.py` / `entry=second_cut_prepare`
- 症状：`prepare:second_cut` 成功；`second_cross_cut` 在 cycle 1/8 **真机未动** 即 abort。
- 报错：`hook_lift_ik_failed_cycle_1: waypoint 2: IK failed pos_err=2.85mm rot_err=2.865deg min_margin=0.00deg`
- 对比（裕度 5° 时）：`pos_err=7.63mm rot_err=6.49deg`
- 根因（当前判断）：
  - orient 段第 3 点（朝 `hook_target_plane_angle_deg=170°`）离线 IK 达不到 `hook_lift_solver` 硬阈值（0.1mm / 0.06°）。
  - `prepare second_cut` 仅 `valid=2/63` IK seeds，起始位姿偏紧。
  - 与左臂 handoff、碗检测、per-cycle workflow **无关**（未执行到）。
- 已尝试：`safety_margin_deg` 5°→3°（误差下降仍失败）。
- 当前状态：**未解决**，阻塞 per-cycle handoff 真机验证。
- 下一步：放宽 `POS_TOL`/`ROT_TOL` 或调 hook/prepare 参数；`debug_hook_lift` 复现。

### 2026-06-11 - 左臂交接 handoff（已解决）

- Related: `debug_left_handoff` / `left_handoff_pose.py` / `FLANGE::`
- 症状：曾出现 IK 0mm 但真机不到位、workflow 时序错误等。
- 当前状态：**debug_left_handoff 真机通过**；workflow 已改为 per-cycle live-pose handoff（待 IK 通过后联调）。

### 2026-06-06 - 整体情况

- Source: 最新 commit 评语 "总体能跑通,但仍需优化"
- 描述：整个流程可以运行完成，但存在多个待优化点。具体优化项尚未明确记录。
- 当前状态：已知但不明确

### 2026-06-06 - 切黄瓜待优化

- Source: commit 92215ac2 "切黄瓜待优化"
- 描述：黄瓜切割流程存在需要优化的问题。
- 当前状态：已知但不明确

## Debugging History

- 2026-06-11：`second_cut_prepare` → `second_cross_cut` 两次运行均在 hook_lift waypoint 2 IK 预检失败；裕度 3° 改善误差但未过阈值。
