# Current Session

## Last Updated

- 2026-05-14 Local Time

## Current Objective

修复 `tofu_state_node` 崩溃问题，实现 RViz 中豆腐可视化 marker 正常显示

## Completed This Session

### Bug #1：参数类型不匹配（tofu_state_node exit code 1）
- **根因**：`LaunchConfiguration('offset_a').perform()` 返回字符串 `"0.03"`，YAML 参数文件中变成 `offset_a: '0.03'`（字符串），与节点声明的 `float` 类型冲突
- **修复**：
  - viz_display.launch.py：`float(LaunchConfiguration(...).perform(context))`
  - cuttofu_phase2.launch.py：`ParameterValue(LaunchConfiguration(...), value_type=float)`
  - 涉及参数：`offset_a`, `vertical_offset`, `buffer_size`, `jump_threshold`, `min_buffer_frames`, `valid_timeout`

### Bug #2：RcutilsLogger C 扩展不支持 % 格式化多参数
- **根因**：ROS2 Humble `RcutilsLogger.debug/info` C 扩展只接受 `(self, msg)`，不接受 variadic `*args`
- **崩溃点**：tofu_state_node.py 第 168 行 `_on_objects` 回调首次触发（buffer 不足 min_frames 时）
- **修复**：3 处 debug/info 调用改为 f-string
  - Line 168: `"Buffer accumulating: %d/%d frames", len, min` → `f"Buffer accumulating: {len}/{min} frames"`
  - Line 154: `"Frame discarded: jump=%.3fm > threshold=%.3fm (#%d)"` → f-string
  - Line 145: `"Sustained position change detected (%d consecutive discards)"` → f-string

### 实机验证结果
- SAM3 检测 tofu ✅：`Detection #N: Found 1 objects for prompt "tofu"`
- pose_estimator 发布 ✅：`Published 1 objects with poses (total: N)`
- tofu_state_node INFO 日志正常：`TofuStateNode: arm=right, buffer_size=15, jump_threshold=0.050`
- tofu_visualizer_node 启动成功 ✅：`/tofu_state -> /tofu_visualization (frame=world)`
- **待验证**：RViz 中 marker 显示（bug #2 修复后需重新启动）

## Files Changed

- `src/cuttofo_xcore/launch/viz_display.launch.py`: float() 类型转换修复
- `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`: ParameterValue 类型转换修复
- `src/cuttofo_xcore/cuttofo_xcore/tofu_state_node.py`: f-string 格式化修复（3处）

## Current State

- 视觉链路已通：SAM3 → pose_estimator → /objects_with_pose
- tofu_state_node 修复后重新启动即可（colcon build 已通过）
- tofu_visualizer_node 始终运行，订阅 /tofu_state
- pose_estimator 使用 PLACEHOLDER 算法（非生产级）

## Next Steps

1. `ros2 launch cuttofo_xcore viz_display.launch.py enable_realsense:=true` 重新启动
2. 验证 RViz 中豆腐 marker（A/B/C/D 彩色角点球 + TCP 目标品红球 + 刀面法线箭头）
3. 确认 /tofu_state 在 buffer 积累足够帧后输出有效数据
4. 完成 TCP 标定（tcp_offset=[0,0,0] 当前为 0）
