# Current Session

## Last Updated

- 2026-05-24 16:00 CST

## Current Objective

- Phase7 push_lift_speed: lift 和 push 速度解耦——lift 独立参数 + 独立 SDK 调用（避免梯形速度第一段加速慢）。

## Current Business Logic Position

- Main path: PHASE_1 -> PHASE_2 -> PHASE_3 -> PHASE_4 -> PHASE_2(re-entry) -> PHASE_5 -> PHASE_6 -> PHASE_2(re-entry) -> PHASE_7 -> DONE
- Current node: PHASE_7_THIRD_CUT (simplified to pure RT position mode, segments merged)
- Active branch: `feature-constrained-obb-vision` (implemented, hardware-validated for Phase6→Phase2 path)
- Active branch purpose: Replace vision pipeline within PHASE_2 with constrained OBB to improve stability and tightness of `top_corners` and `edge_dir`; clarified objective is top-surface ABCD footprint accuracy, not full-body 3D enclosure.

## Completed This Session

- **push_lift_speed 独立参数 + lift 拆分为独立 SDK 调用**:
  - 发现根因: SDK 的 `move_rt_cartesian_path` 对多 waypoint 路径只做**一次梯形速度**——第一个 waypoint 从零加速（感觉慢），中间段匀速巡航（感觉快）。
  - 合并后的中段推 6-waypoint 调用中，lift 是第一个 waypoint（加速段），push 在中间段（巡航段）——同一 `max_linear_velocity` 但 lift 慢、push 快。
  - 新增 `push_lift_speed: 0.05` config 参数
  - 中段推拆为 2 段:
    - `[lift]` → `push_lift_speed`（独立梯形，单独加减速）
    - `[fwd, ret, bwd, ret, drop]` → `max(push_forward, push_backward)`
  - 尾段推拆为 2 段:
    - `[tail-lift]` → `push_lift_speed`
    - `[tail-push, ret, retract]` → `push_tail_speed`
  - SDK calls 从 ~5 增加到 ~7，lift 和 push 速度完全解耦
  - 语法和 build 通过
- Phase7 segment merging 和 position-only simplification（上一轮完成）

## Problems And Resolutions

- **合并调用中 lift 慢但 push 快**: 即使共用一个 `max_linear_velocity`，合并多 waypoint 调用的第一个 waypoint（lift）从零开始加速，大部分时间在加速段、平均速度低于 v_max；中间 waypoint（push）在巡航段、全速运行。用户观察到的是物理行为差异。方案：将 lift 拆为独立 `_move_segment` 调用 + 独立 `push_lift_speed` 参数，独立加减速梯形。
- **SDK power cycling**: 每个 `move_rt_cartesian_path` 内部触发 stop→setOperateMode→setPowerState。通过合并相邻子段从 ~15 降到 ~5 调用，本次 lift 拆分增加到 ~7，仍远好于原版。
- `mid_cut_mat` defined after use during tail merge — fixed in previous session.

## Verification

- Syntax check: `python3 -m py_compile` on `knife_cut_action_server.py` passed.
- Build: `colcon build --packages-select cuttofo_xcore dexbot_middle_layer` passed.
- Config: `push_lift_speed: 0.05` in `phase7_third_cut`.

## Files Changed

- `src/cuttofo_xcore/cuttofo_xcore/knife_cut_action_server.py`
- `src/cuttofo_xcore/config/cuttofo_config.yaml`
- `.project-log/progress.md`
- `.project-log/current-session.md`

## Current State

- **push_lift_speed** 解耦 lift 速度：中段推 lift 和尾段推 lift 各自独立调用，`push_lift_speed` 默认 0.05 m/s
- Phase7: pure RT position mode, no impedance
- Phase7 SDK calls: ~7（合并 ~5 + lift 拆分 +2）
- Guard condition fix: inverted U/V percentiles auto-swap
- U/V axes visualization active when `corner_mode: constrained_obb`
- Phase6 vision override: hardware-verified
- Phase2 tofu debounce (0.5s), IK joint margin 10°
- Full pipeline hardware test pending

## Next Steps

1. Hardware test: verify push_lift_speed=0.05 上抬速度快
2. 如需要，调高 `push_lift_speed` 或调整 `max_acceleration`
3. Full pipeline hardware test: Phase1→Phase7
