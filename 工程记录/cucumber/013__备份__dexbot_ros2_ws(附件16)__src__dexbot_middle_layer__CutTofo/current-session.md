# Current Session

## Last Updated

- 2026-06-10 CST

## Current Objective

- 优化切豆腐端到端自动化效果，逐步减少人工介入；当前优先消除“第二次斜切后人工拨掉豆腐条”的步骤。

## Current Business Logic Position

- Main path: `tofu_workflow_params.yaml` orchestrator -> `handle_approach:default` -> `prepare:first_cut` -> `cut_round:round_1` -> `operator rotate board` -> `prepare:first_cut` -> `cut_round:round_2` -> `operator remove tofu strips` -> `operator rotate tofu upright` -> `prepare:after_rotation_1` -> `vertical_cut:default`
- Current node: 开始把“人工拨条”从 operator step 变成机器人自主动作，作为减少人工介入的第一优先级。
- Active branch: `cut_to_fo_featrue`

## Completed This Session

1. 新建 `cuttofo_skill_tofu_second_cross_cut` 包骨架，加入独立 `debug_hook_lift` 调试入口。
2. 修复独立调试脚本的 ROS service 调用模型：为节点挂载 `MultiThreadedExecutor` 并后台 spin，解决 `enable_arm(True)` future 无人处理导致的超时。
3. 完成 hook-lift 真机闭环首轮验证：
   - `--dry-run` 可正确打印 waypoint。
   - 实机执行成功返回 `hook_lift execution complete`。
4. 将 hook-lift 姿态参数语义从“欧拉角单轴增量”重构为与 `prepare.plane_angle_deg` 一致的绝对刀面倾角语义：
   - 新参数为 `hook_target_plane_angle_deg`
   - 含义为右臂法兰 `+Z` 与 base `XZ` 平面的线面夹角
   - 复用 `build_rotation_with_edge_dir(...)` 生成姿态
5. 将调试脚本的全部可调参数收敛到脚本开头 `DEBUG_CONFIG`，便于现场直接改数值调试。
6. 定位运行时参数不生效的原因：普通 `colcon build` 产生 install 副本，`ros2 run` 读取旧安装代码；已改为 `--symlink-install` 重新构建，后续源码改值可直接反映到运行时。

## Problems And Resolutions

1. **SAM3 提示词冲突**：`cucumber_hold_node` 发布 "cucumber" 与 `handle_approach_node` 发布 "wooden cleaver handle" 互相覆盖。修复：从 `skills_bringup.launch.py` 移除 cucumber_hold_server include（豆腐工作流不涉及黄瓜对象，cucumber 有自己独立的 bringup 文件）。
2. **相机画面不显示**：`tofu_workflow_execute.launch.py` 中 `show_camera_display` 默认值写成了 `"false"`，覆盖了 vision_bringup 自身的 `true` 默认值。修复：改为 `"true"`。
3. **RealSense 分辨率默认值错误**：`rs_color_profile` 和 `rs_depth_profile` 默认值写成 `1280,720,30`，与 vision_bringup 的 `424x240x15` / `640x480x15` 不匹配。修复：改为与 vision_bringup 一致的默认值。
4. **colcon 无法发现 CutTofo 包**：`colcon list` 只发现 workspace 根目录下 11 个包，`src/dexbot_middle_layer/CutTofo/` 下 17 个包全部缺失。原因未深究。绕过方案：由于 install 用 egg-link 指向 build 目录，手动同步源码 Python 到 build；launch 文件本身是 symlink 链，源码编辑直接生效。

## Verification

- `python3 -m py_compile` 两只修改文件均通过
- `ros2 launch ... --show-args` 确认参数声明正确
- launch 文件 symlink 链确认生效（install → build → source）
- Python 模块手动同步到 build 目录确认一致

## Files Changed

- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute.launch.py`（修改）
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/skills_bringup.launch.py`（修改：移除 cucumber_hold）
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_runner.py`（修改）
- `src/dexbot_middle_layer/CutTofo/启动指令.md`（追记）

## Current State

- 第二次横切新包 `cuttofo_skill_tofu_second_cross_cut` 已创建，可独立承载后续 `hook_lift -> transfer -> scrape -> return` 链路。
- 首个原子动作 `debug_hook_lift` 已可在 ROS 控制节点上独立执行，当前支持：
  - `translate_only`
  - `translate_plus_tilt`
- `translate_plus_tilt` 的姿态控制语义已与 `prepare.plane_angle_deg` 对齐，不再使用欧拉角单轴增量。
- 调试脚本当前默认从脚本开头 `DEBUG_CONFIG` 读取现场调试参数，适合高频小步试参。
- 当前已确认：
  1. ROS service 链路通。
  2. hook-lift 可执行成功。
  3. waypoint 日志能打印位置、RPY 和 `plane_angle_deg`。
- 当前未确认：
  1. `hook_target_plane_angle_deg=150` 的物理效果是否优于 `140`。
  2. 主平移方向当前使用 base `+Y` 是否就是最优“挑条”方向。
  3. 2 个 waypoint 是否足够平顺，还是需要 3 个 waypoint。

## Next Steps

- 继续围绕 `debug_hook_lift` 做真机参数收敛：重点比较 `hook_target_plane_angle_deg=140/145/150` 的效果。
- 验证 base `+Y` 平移是否等价于现场期望的“上挑”方向；若不一致，改主平移方向语义而不是继续硬调数值。
- 比较 `hook_waypoint_count=2` 与 `3` 的动作平顺性和带条稳定性。
- hook-lift 参数定型后，再进入下一原子动作 `transfer_to_drop_zone` 调试。
