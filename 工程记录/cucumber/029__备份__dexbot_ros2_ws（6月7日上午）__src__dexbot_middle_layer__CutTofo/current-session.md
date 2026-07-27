# Current Session

## Last Updated

- 2026-06-07 09:20 CST

## Current Objective

- 继续对 CutTofo 豆腐链路做真机联调，当前重点是验证 constrained_obb 参数向 legacy 收口后的效果，并在修正 SAM3 彩色图输入后确认 tofu marker 与角点检测是否恢复正常。

## Current Business Logic Position

- Main path: `cuttofu_vision` 通用输出 -> `tofu_perception_node` 独立豆腐感知 -> `tofu_prepare` / `tofu_cut_round` / `tofu_vertical_cut` / `cuttofo_task_visualizer`
- Current node: 完整测试链路可启动，但最近一次真机排查确认上游 `sam3_detector_node` 因彩色图话题订阅错误而未实际产出检测，导致 `tofu_state` 与 marker 为空
- Current edge: 修正 `tofu_vision_params.yaml` 的 `image_topic` 后，等待用户重新编译并重启完整链路做真机复验
- Active branch: None

## Completed This Session

1. 端到端对比当前 constrained_obb 与 legacy/xcore 豆腐视觉链路，确认主差异集中在 constrained_obb 参数而非话题结构
2. 将 `tofu_perception_params.yaml` 与 `tofu_vision_params.yaml` 中的 constrained_obb 参数向 legacy 收口
3. 明确统一的关键参数为：`obb_margin=0.003`、`obb_depth_median_frames=1`、`obb_bounds_top_keep_ratio=0.8`、`obb_bounds_u/v_percentile=2.0~98.0`
4. 指导用户启动完整链路 `ros2 launch cuttofo_skill_tofu_perception tofu_perception.launch.py`
5. 基于现场 `ros2 node list` / `ros2 node info` / `ros2 topic info -v` / `ros2 topic echo --once` / `ros2 param dump` 排查为何“有感知节点但没有检测和 marker”
6. 确认 `tofu_perception_node`、`task_visualizer_node`、`sam3_detector_node`、`pose_estimator_node` 均已运行，且 marker 话题存在
7. 确认 `tofu_state` 只有空对象、`task_visualization` 只发清空 marker，符合“上游零检测”的表现
8. 定位根因是 `sam3_detector_node` 订阅了无 publisher 的 `/camera/color/image_raw`，而不是现场 RealSense 正在发布的 `/camera/camera/color/image_raw`
9. 在 `tofu_vision_params.yaml` 中显式加入 `image_topic: /camera/camera/color/image_raw`，准备让用户重编译后复验
10. 确认 `/cuttofu/vision/text_prompt` 上的动态提示词已是 `ridged_tofu`，说明 prompt 链路正常，当前阻塞点不是提示词发布

## Problems And Resolutions

- 问题: RViz 中看不到豆腐 marker，用户怀疑 SAM3 没有开始检测
  - 处理: 逐层检查节点、话题、参数、消息内容，确认 marker 缺失是因为上游零检测
- 问题: `sam3_detector_node` 实际订阅 `/camera/color/image_raw`，但现场只有 `/camera/camera/color/image_raw` 有 publisher
  - 处理: 在 `tofu_vision_params.yaml` 中显式补充 `image_topic: /camera/camera/color/image_raw`
- 问题: 运行时仍保留 `text_prompt: cargo truck` 静态参数，容易与 tofu 动态 prompt 混淆
  - 处理: 已确认 `/cuttofu/vision/text_prompt` 动态值为 `ridged_tofu`，当前先聚焦修复图像输入；后续再决定是否清理静态默认 prompt

## Verification

- 已确认 `/camera/camera/color/image_raw` 有 publisher，而 `/camera/color/image_raw` 无 publisher
- 已确认 `/cuttofu/perception/tofu_state` 当前只发布空对象
- 已确认 `/cuttofu/perception/task_visualization` 当前只发布清空 marker
- 已确认 `/cuttofu/vision/text_prompt` 当前发布值为 `ridged_tofu`
- 已确认 `tofu_perception_params.yaml` 与 `tofu_vision_params.yaml` 中 constrained_obb 参数已对齐到本轮目标值
- 仍待用户在修正 `image_topic` 后重新编译并重启链路做真机复验

## Files Changed

- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_perception_params.yaml`
- `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml`

## Current State

- 豆腐独立感知链路结构本身已打通，本轮新增问题已收敛到 SAM3 彩色图输入配置错误。
- constrained_obb 参数已向 legacy 收口，但其实际效果仍需在修正图像输入后重新观察。
- prompt 发布链路正常，当前最可能阻塞检测的是 `image_topic` 订错而不是类别提示词未下发。

## Next Steps

- 让用户重新编译 `cuttofo_skill_tofu_perception` 与 `cuttofu_vision` 并重启完整链路
- 验证修正 `image_topic` 后 SAM3 检测、`tofu_state`、marker 是否恢复
- 若恢复后角点仍不理想，继续拆分“参数收口效果”和“双重 constrained_obb 计算影响”
- 根据真机结果，决定是否清理静态 `cargo truck` 默认 prompt
