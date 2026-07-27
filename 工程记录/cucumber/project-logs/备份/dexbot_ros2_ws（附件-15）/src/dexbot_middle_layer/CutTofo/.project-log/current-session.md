# Current Session

## Last Updated

- 2026-06-07 17:35 CST

## Current Objective

- 在已完成启动职责收口、横切回撤回归、阶段 7 竖切迁移之后，继续完成 phase6/第三次放刀前的独立视觉参数迁移，让感知覆盖改为配置驱动。

## Current Business Logic Position

- Main path: `vision_bringup` -> `tofu_perception_node` -> `task_visualizer` / `tofu_prepare` / `tofu_cut_round` / `tofu_vertical_cut` -> `tofu_task_orchestrator`
- Current node: 豆腐主链路的启动装配与主要切割语义已收口，当前工作重心转到 phase6 prepare 前的独立视觉参数切换
- Current edge: orchestrator `APPLY_PARAMS` 在 `prepare:after_rotation_1` 前对 `/tofu_perception_node` 下发 phase6 override
- Active branch: None

## Completed This Session

1. `vision_bringup.launch.py` 已去掉内部 `task_visualizer` 启动职责，只保留 vision + 相机画面。
2. `tofu_perception.launch.py` 已收紧为只启动 `tofu_perception_node`。
3. `tofu_skills_bringup_no_approach.launch.py` 已改成显式装配 `vision + perception + task_visualizer + 下游 skills`。
4. `tofu_workflow_execute_no_approach.launch.py` 文案已更新为完整节点栈单入口。
5. `tofu_prepare_node.py` 与 `tofu_prepare_workflow.py` 已回退 `use_vision` 自动猜测逻辑，恢复显式 action 语义。
6. `启动指令.md` 已改为只保留两套启动方案，并在手动 prepare 指令里明确加入 `use_vision: true`。
7. `tofu_cut_round` 已恢复 legacy 风格的切后 cartesian return：先按 inverse-step + extra offset 清刀，再 MoveJ 到 wait pose。
8. `cut_round_path.py` 与 `tofu_cut_round_workflow.py` 已补齐回撤偏移 helper 和日志，便于现场确认回撤目标。
9. `tofu_vertical_cut_workflow.py` 已按 legacy `phase7_third_cut` 收紧为 `seg1 -> mid_push -> seg2 -> tail_push` 四段。
10. `tofu_vertical_cut_params.yaml` 默认 profile 已切回 legacy phase7 语义与参数。
11. `tofu_perception_params.yaml` 已恢复为纯 ROS 2 参数文件，只保留 `tofu_perception_node.ros__parameters`，避免 launch 传参解析失败。
12. phase6 override 已拆分到独立 `tofu_perception_overrides.yaml`，其中包含视觉参数以及 `offset_a` / `vertical_offset` 这类 prepare 目标点偏移。
13. `tofu_perception_config.py` 已改为默认参数读 `tofu_perception_params.yaml`、phase6 override 读 `tofu_perception_overrides.yaml`，继续保留 fallback 合并与 runtime 字段过滤。
14. `workflow_runner.py` 继续从 perception config 读取并下发 `SetParameters`。
15. `tofu_workflow_no_approach_params.yaml` 的第三次放刀 prepare 步骤已补齐 `vision_override: phase6`。
16. 相关 Python 文件已通过 `python3 -m py_compile`，`cuttofo_skill_tofu_perception` 与 `cuttofo_orchestrator` 已重建通过。

## Problems And Resolutions

- 问题: `vision_bringup` 与 `tofu_perception.launch.py` 都曾承担可视化或上游启动职责，导致职责边界混乱
  - 处理: 把 vision/perception/visualizer 启动职责全部上提到 orchestrator bringup 显式装配
- 问题: `tofu_prepare` 内部存在 `use_vision` fallback，会隐式覆盖调用方意图
  - 处理: 回退 fallback，恢复只按 action goal 显式字段执行
- 问题: 横切结束后曾因 `skip_return_anchor: true` 直接从左端终点 MoveJ 回 wait，缺失安全清刀回撤
  - 处理: 恢复 return 分支，回到 legacy 的 inverse-step + extra offset 回撤链路，并补足日志
- 问题: 当前阶段 7 竖切逻辑与 legacy phase7 存在段落和参数漂移
  - 处理: 直接按 legacy `_execute_phase7_cut()` 收紧 workflow 段落，并统一默认参数语义
- 问题: phase6 override 之前硬编码在 orchestrator 里，且 `tofu_perception_params.yaml` 没有独立参数区
  - 处理: 先在 perception config 中补出 `phase6_vision` 并将 orchestrator 改为“读取配置并下发”；在真机启动时发现 ROS 2 参数文件不允许顶层混入非节点参数后，改为拆分出独立 `tofu_perception_overrides.yaml` 承载 phase6 override，同时保留 `offset_a` / `vertical_offset`

## Verification

- `python3 -m py_compile` 已覆盖本轮修改的 Python 文件并通过
- `colcon build --base-paths /home/tbl/Project/cucumber/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo --packages-select cuttofo_skill_tofu_perception cuttofo_orchestrator --symlink-install` 通过
- 已确认 `tofu_perception_params.yaml` 顶层只剩 `tofu_perception_node`，`tofu_perception_overrides.yaml` 顶层只含 `phase6_vision`
- 尚未重新做真机级别的 full workflow 启动复验

## Files Changed

- `src/dexbot_middle_layer/CutTofo/cuttofu_vision/launch/vision_bringup.launch.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/launch/tofu_perception.launch.py`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_skills_bringup_no_approach.launch.py`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute_no_approach.launch.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_node.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_cut_round/config/tofu_cut_round_params.yaml`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/trajectory/cut_round_path.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_cut_round/cuttofo_skill_tofu_cut_round/tofu_cut_round_workflow.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_vertical_cut/cuttofo_skill_tofu_vertical_cut/tofu_vertical_cut_workflow.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_vertical_cut/config/tofu_vertical_cut_params.yaml`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_perception_params.yaml`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_perception_overrides.yaml`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_runner.py`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_no_approach_params.yaml`
- `src/dexbot_middle_layer/CutTofo/启动指令.md`

## Current State

- 启动职责边界、横切回撤和阶段 7 竖切都已在代码层回归 legacy 语义。
- phase6/第三次放刀前的视觉参数切换也已从 orchestrator 硬编码迁回 perception config。
- phase6 对应的 prepare 几何偏移 `offset_a` / `vertical_offset` 也已并入 perception override，一起驱动 TCP 目标点。
- 当前剩余工作集中为真机验证 phase6 参数下发是否与预期一致。

## Next Steps

- 启动 `ros2 launch cuttofo_orchestrator tofu_workflow_execute_no_approach.launch.py run_orchestrator:=false` 验证完整节点栈。
- 手动发送或驱动到 `prepare:after_rotation_1`，确认 `vision_override: phase6` 会在 prepare 前生效。
- 用 `ros2 param get /tofu_perception_node ...` 或日志确认 `phase6_vision` 中的 OBB 百分位、depth median、`offset_a`、`vertical_offset` 等参数已切换。
- 若 phase6 参数切换正常，再继续整栈 workflow 真机验证。
