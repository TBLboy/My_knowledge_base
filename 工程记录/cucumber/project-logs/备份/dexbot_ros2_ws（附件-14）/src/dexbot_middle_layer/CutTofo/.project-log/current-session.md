# Current Session

## Last Updated

- 2026-06-07 16:05 CST

## Current Objective

- 完成豆腐无拔刀 workflow 的启动职责重构，确认现场现在只需两套入口：一键完整流程，或完整节点栈 + 手动单阶段 action 测试。

## Current Business Logic Position

- Main path: `vision_bringup` -> `tofu_perception_node` -> `task_visualizer` / `tofu_prepare` / `tofu_cut_round` / `tofu_vertical_cut` -> `tofu_task_orchestrator`
- Current node: 启动职责边界已经收口，workflow/skills bringup 成为唯一整栈装配入口
- Current edge: 等待真机验证新的单入口链路是否稳定拉起完整 vision/perception/visualizer/control 栈
- Active branch: None

## Completed This Session

1. `vision_bringup.launch.py` 已去掉内部 `task_visualizer` 启动职责，只保留 vision + 相机画面。
2. `tofu_perception.launch.py` 已收紧为只启动 `tofu_perception_node`。
3. `tofu_skills_bringup_no_approach.launch.py` 已改成显式装配 `vision + perception + task_visualizer + 下游 skills`。
4. `tofu_workflow_execute_no_approach.launch.py` 文案已更新为完整节点栈单入口。
5. `tofu_prepare_node.py` 与 `tofu_prepare_workflow.py` 已回退 `use_vision` 自动猜测逻辑，恢复显式 action 语义。
6. `启动指令.md` 已改为只保留两套启动方案，并在手动 prepare 指令里明确加入 `use_vision: true`。
7. 相关 launch/Python 文件已通过 `python3 -m py_compile`，相关 5 个 CutTofo 包已重建通过。

## Problems And Resolutions

- 问题: `vision_bringup` 与 `tofu_perception.launch.py` 都曾承担可视化或上游启动职责，导致职责边界混乱
  - 处理: 把 vision/perception/visualizer 启动职责全部上提到 orchestrator bringup 显式装配
- 问题: `tofu_prepare` 内部存在 `use_vision` fallback，会隐式覆盖调用方意图
  - 处理: 回退 fallback，恢复只按 action goal 显式字段执行

## Verification

- `python3 -m py_compile` 已覆盖本轮修改的 launch / Python 文件并通过
- `colcon build --base-paths ... --packages-select cuttofu_vision cuttofo_skill_tofu_perception cuttofo_task_visualizer cuttofo_skill_tofu_prepare cuttofo_orchestrator --symlink-install` 通过
- 尚未做真机级别整栈运行验证

## Files Changed

- `src/dexbot_middle_layer/CutTofo/cuttofu_vision/launch/vision_bringup.launch.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/launch/tofu_perception.launch.py`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_skills_bringup_no_approach.launch.py`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute_no_approach.launch.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_node.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py`
- `src/dexbot_middle_layer/CutTofo/启动指令.md`

## Current State

- 启动职责边界已按“vision / perception / visualizer / orchestrator 装配层”重新拆开。
- 手动 prepare 测试需要显式传 `use_vision: true`，文档已同步。
- 当前剩余工作从“改结构”切换为“按新结构做真机复测”。

## Next Steps

- 启动 `ros2 launch cuttofo_orchestrator tofu_workflow_execute_no_approach.launch.py run_orchestrator:=false` 验证完整节点栈。
- 手动发送 `prepare` action 验证视觉几何与 IK。
- 若通过，再跑默认 workflow 入口确认无拔刀全流程。
