# Current Session

## Last Updated

- 2026-06-12 11:12 CST

## Current Objective

- 左臂 GUI 关节读数冻结问题 — **已解决**

## Current Business Logic Position

- Main path: A -> B -> C -> D -> E (stable)
- Dual-arm path: A -> DA -> DB -> DC -> DD -> E (stable)
- Active branch: None

## Completed This Session

- **左臂关节读数根因确认**：问题在 xcore 控制器 `get_joint_readout_rad()` 走 UDP 缓存，非 GUI 订阅/轮询。
- **控制器修复**：`query_joint_positions_for_readout()` + `get_joint_readout_rad()` 优先同步 `jointPos(ec)`；`dexbot_bottom_layer` 已 build。
- **GUI 防御性修正**（保留）：左右 bridge 分离、side 切换重建 service、`rclpy.shutdown` 生命周期、namespace 属性名修复。
- **用户验证通过**：重启控制器后 Dual Arm 左臂读数随真机更新。

## Problems And Resolutions

| 问题 | 结论 |
|------|------|
| 左臂 GUI J1–J7 冻结 ~19.7° | 根因在 `/arm_l/joint_states` 数据源 stale；控制器读数路径已修复 |
| 初期怀疑 GUI bridge 混用 | 已做防御性修正，但不是本次冻结的主因 |

## Verification

- 用户真机：左臂移动 → GUI 关节角正常更新 ✓
- 需重启 xcore 控制器后修复才生效（非仅重启 GUI）

## Files Changed

- `src/dexbot_bottom_layer/.../lbot_robot_xcore.py`
- `src/dexbot_bottom_layer/.../robot_controller_state.py`
- `src/gui/pages/arm_hand.py`, `src/gui/pages/dual_arm.py`, `src/gui/services/registry.py`
- `src/dexbot_toolbox/dexbot_toolbox/gui/arm_hand_gui.py`
- `src/gui/BUG_FIX_LOG_2026-06-12.md`（早期记录，最终以控制器修复为准）

## Current State

- 左臂关节 live readback 正常。CutTofo 左臂 handoff per-candidate offset 重构见 CutTofo `.project-log`。

## Next Steps

- 按 CutTofo 计划继续：`_DEBUG_STOP_AFTER_TRANSFER` 关闭后排完整 workflow 联调（若尚未做）。
