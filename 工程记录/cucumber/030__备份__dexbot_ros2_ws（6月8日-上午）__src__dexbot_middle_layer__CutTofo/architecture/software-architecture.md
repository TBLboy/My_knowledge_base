# Software Architecture

## System Overview

CutTofo 系统采用分层 ROS 2 架构，从下到上：

1. **底层：** xCore 直连 SDK（手臂控制）+ CAN（灵巧手控制）
2. **中间层：** 7 个独立 Skill Action Server + vision 管线
3. **上层：** Tick 驱动 Orchestrator 工作流编排器

## Node Structure

每个 skill 是一个独立的 ROS 2 node（Python rclpy），作为 Action Server 运行。
Orchestrator 是另一个独立 node，包含多个 Action Client。

## Communication Paths

```
Orchestrator (tofu_task_orchestrator)
  │  Action Client (x7)
  ├── /handle_approach/execute  → handle_approach_node
  ├── /tofu_prepare/execute     → tofu_prepare_node
  ├── /tofu_cut_round/execute   → tofu_cut_round_node
  ├── /tofu_vertical_cut/execute → tofu_vertical_cut_node
  ├── /cucumber_hold/execute    → cucumber_hold_node
  ├── /pick_place/execute       → pick_place_node
  └── /sauce_pour/execute       → sauce_pour_node

Vision Pipeline:
  RealSense → /camera/color/image_raw + /camera/aligned_depth_to_color/image_raw
    → SAM3 detector → /cuttofu/perception/detected_objects
    → pose_estimator → /cuttofu/perception/objects_with_pose
    ← Skills publish text_prompt to /cuttofu/vision/text_prompt

Operator Interaction:
  Orchestrator writes → /tmp/cuttofo_operator_wait.json (GUI polls)
  Operator triggers → /cuttofo_operator/continue (Trigger.srv)
                    or touch /tmp/cuttofo_phase_after_round*_continue
                    or terminal Enter
```

## Threading Model

- 每个 node 运行在独立进程（ROS 2 多进程架构）
- Orchestrator 单线程 tick 循环（20Hz），使用 `executor.spin_once()`
- Action Server 内部：rclpy spin 处理 goal/result/feedback

## GUI / Business Logic Separation

- 工作流 GUI：`toolbox/GUI/cuttofo_workflow_gui.py`（PyQt/PySide）
- GUI 仅轮询 `/tmp/cuttofo_operator_wait.json` 显示状态
- 业务逻辑完全在 orchestrator + skill nodes 中
- GUI 只负责展示和 operator continue 触发
