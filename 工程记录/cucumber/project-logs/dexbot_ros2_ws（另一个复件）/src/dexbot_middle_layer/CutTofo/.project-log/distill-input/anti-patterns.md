# Anti-Patterns

## Anti-Pattern: 左臂 handoff 把 move_cartesian 输入当 TCP/grasp 直接下发

- Bad assumption or trap: IK 在 skill TCP 空间预检通过，就把同一数值直接发给 `move_cartesian`，或依赖全局 `tool_offset.yaml` 与 skill `left_handoff.tcp_offset` 隐式一致。
- Why it is tempting: 控制器文档称输入为「抓取工作点」，且右臂其它 skill 已有一套 offset 习惯。
- Consequence: 真机偏差可达 10–27 cm；日志 IK OK 但人眼看到明显不到示教点。
- Safer alternative: 与右臂 hook_lift 一致——**业务在 TCP 规划，下发前在 skill 内转 flange**；`FLANGE::` 标签让控制器按 flangeInBase 执行；offset 仅认 `left_handoff.tcp_offset`。
- Evidence refs:
  - `.project-log/progress.md`（2026-06-11 left handoff 条目）
  - `left_handoff_pose.py`, `xcore_arm_adapter.py`, `xcore_controller_node.py`

## Anti-Pattern: offset 采集存残差却当绝对值运行

- Bad assumption or trap: 采集时用 `left_actual - left_target(含配置 offset)` 得增量，却把样本均值当作 `right_flange_target_offset` 绝对值写入 params。
- Why it is tempting: 增量在单次采集中“看起来”能解释当前误差。
- Consequence: 多次采集中 config offset 变化时 mean 语义混乱；运行目标与示教点系统性偏差。
- Safer alternative: 使用 `derive_right_flange_target_offset_absolute`；重采前 params offset 清零；示教时右臂固定、左臂同刀点。
- Evidence refs:
  - `left_handoff_pose.py`, `capture_left_handoff_flange_pose.py`
  - `.project-log/progress.md`（2026-06-11 left handoff）
