# Current Session

## Last Updated

- 2026-05-09

## Current Objective

- Phase 2 控制逻辑测试 — 验证 IK/FK/驱动正确性

## Completed This Session

- 发现 Euler 分量映射 BUG：`LbotEuler(eul[0],eul[1],eul[2])` → `LbotEuler(eul[2],eul[1],eul[0])`
- 修复 `solve_ik`、`compute_fk`、`get_pose` 三处 euler 分量映射
- 实机验证 `plane-angle=-80`：Rx(10°) 物理正确，FK 零误差 ✅
- 编写 `test_pose_constraint.py`：姿态约束/完整位姿两种模式
- 编写 `test_axis_move.py`：验证 base 坐标系轴向
- 确认 Lbot 坐标系：Z↑(上) X→(前) Y←(左)

## Problems And Resolutions

- Euler 分量映射错误 → `eul[0]↔eul[2]` 互换后修复
- M5.1 往返测试对称抵消了此 BUG → 全局修复后需重测
- `DEXBOT_ARM_BACKEND=lbot` 未设置时连接失败 → 需 export

## Verification

- `test_axis_move.py --axis x --dist 5` ✅ 轴向正确
- `test_pose_constraint.py --mode attitude --plane-angle -80` ✅ FK 零误差
- `colcon build` ✅
- `pytest` 17/17 ✅

## Files Changed

- `lbot_arm_adapter.py` — euler 分量映射修复 (3 处)
- `test_pose_constraint.py` — 新建
- `test_axis_move.py` — 新建
- `.project-log/progress.md` — 更新

## Current State

- Phase 2 核心逻辑（IK/FK/驱动/姿态约束）已验证通过
- 手眼标定暂未进行，跳过
- 标定 GUI 包 `cuttofo_calibration` 已完成（详见该包 project-log）

## Next Steps

- 用户还有细节调整要讨论
- 然后继续进行验证
