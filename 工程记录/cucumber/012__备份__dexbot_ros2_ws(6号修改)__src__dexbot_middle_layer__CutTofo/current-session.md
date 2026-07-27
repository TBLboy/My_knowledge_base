# Current Session

## Last Updated

- 2026-06-06 21:25 CST

## Current Objective

- 继续对 CutTofo 豆腐链路做真机联调，当前重点是验证独立 tofu_perception 感知层、visualizer 风格收口，以及 GUI 灵巧手页在本地 SDK 源码模式下的可用性。

## Current Business Logic Position

- Main path: `cuttofu_vision` 通用输出 -> `tofu_perception_node` 独立豆腐感知 -> `tofu_prepare` / `tofu_cut_round` / `tofu_vertical_cut` / `cuttofo_task_visualizer`
- Current node: 独立 tofu perception 测试链路可启动，visualizer 风格已接近 xcore 参考，GUI 已改为优先加载本地 linkerbot SDK 源码
- Current edge: 真机验证完整 tofu workflow 与 GUI 手控后续运行时表现
- Active branch: None

## Completed This Session

1. 恢复并接入 `cuttofo_skill_tofu_perception`，让豆腐几何计算回到 dedicated perception 层
2. 实现 orchestrator 在 `handle_approach` 成功后自动启动 tofu perception，并在退出时清理子进程
3. 收口 tofu prompt ownership：只有 `tofu_perception_node` 负责 tofu prompt，`tofu_prepare` 不再发布 tofu prompt
4. 打通独立测试链路：vision + tofu_perception + task_visualizer
5. 修复 `cuttofo_skill_tofu_perception` / `cuttofo_task_visualizer` 的包发现与显式构建问题
6. 修复 SAM3 camera viewer 不显示绿色 mask 的问题
7. 调整 RViz tofu marker 风格，靠拢 xcore 参考样式，并加深顶面四角连线可见度
8. 将测试视觉默认 prompt 改为 `cargo truck`，豆腐默认 prompt/class_filter 改为 `ridged_tofu`
9. 对照附件32正确版本核对 constrained_obb，确认主链路和 phase6 override 参数已对齐
10. 将 `tofu_vision_params.yaml` 的独立测试视觉链路也切到 `constrained_obb` 并补齐整套 OBB 参数
11. 修复 `src/gui/main.py`，启动 GUI 时自动加载本地 `linkerbot-python-sdk/src`

## Problems And Resolutions

- 问题: tofu perception / task visualizer 包 `package not found`
  - 处理: 使用 CutTofo skills base path 显式构建并重新 source
- 问题: camera viewer 打开但不显示 SAM3 绿色 mask
  - 处理: `tofu_vision_params.yaml` 中恢复 `publish_visualization: true`
- 问题: 当前 RViz marker 风格与 xcore 参考不一致
  - 处理: 去掉顶面填充、恢复 outline 和 arrow 配色，并加深轮廓透明度
- 问题: GUI 手控页报 `No module named 'linkerbot'`
  - 处理: 启动 GUI 时把工作区内 `linkerbot-python-sdk/src` 注入 `sys.path`

## Verification

- `colcon build --base-paths ...cuttofo_skill_tofu_perception ...cuttofo_task_visualizer ...cuttofo_orchestrator --symlink-install` 通过
- `colcon build --base-paths ...cuttofo_skill_tofu_perception --symlink-install` 在视觉参数收口后再次通过
- 用户已完成一轮真机测试，确认 camera viewer 和 RViz 效果有明显改善
- `python3 -c "... import linkerbot; print(linkerbot.__file__)"` 已确认 GUI 导入命中本地 SDK 源码

## Files Changed

- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_runner.py`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_config.py`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/tofu_task_orchestrator.py`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_params.yaml`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_no_approach_params.yaml`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/skills_bringup.launch.py`
- `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute.launch.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_node.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_config.py`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/**`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_task_visualizer/cuttofo_task_visualizer/task_visualizer_node.py`
- `src/gui/main.py`

## Current State

- 豆腐独立感知链路已迁回并进入真机调参/联调阶段。
- 独立测试视觉链路和主 workflow 链路的 constrained_obb 参数已基本收口到附件32正确版本。
- GUI 已不再依赖外部安装的 linkerbot Python 包，改为优先使用工作区内 SDK 源码。

## Next Steps

- 继续验证完整 tofu workflow，重点看 `handle_approach` 后自动启动 tofu perception、phase6 override、生效后的 prepare/cut 稳定性
- 若 GUI 连接灵巧手后仍有后续异常，继续排查 SDK 运行时依赖、CAN 配置和设备通信层
- 根据真机表现继续细调 perception / visualizer 参数