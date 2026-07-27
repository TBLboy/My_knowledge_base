# Business Logic Constraints

## System Constraints

- ROS 2 Humble（rclpy）
- 手臂控制使用 xCore 直连 SDK（非标准 ROS 2 control）
- 所有 skill 通过 ROS 2 Action 接口暴露
- Orchestrator 以 20Hz tick 驱动状态机运行
- 工作流步骤定义在 YAML 配置文件中

## Hardware Constraints

- 右臂 IP: 192.168.2.161
- 左臂 IP: 192.168.2.160
- 右臂 TCP 偏移: [0.01089, 0.12506, 0.25620]
- 左臂 TCP 偏移: [0, 0, 0]
- LinkerHand 通过 CAN 总线控制
- 手臂为 7-DOF AR5 系列

## Software Constraints

- Python 3（rclpy）为主要实现语言
- 视觉依赖 RealSense + SAM3 + pose estimator
- SAM3 text prompt 作为视觉目标指定方式

## Real-Time / Threading Constraints

- Orchestrator 单线程 tick 循环（阻塞式等待 Action result）
- 每个 Action server 独立节点/进程，无多线程竞争
- 视觉处理管线可能影响运动控制实时性（需关注）

## Safety Constraints

- 人工介入等待机制防止自动运动伤害操作人员
- 无自动化防碰撞检测（依赖离线预览和操作人员注意）

## SDK / API Constraints

- xCore 直连 SDK：TCP socket 通信
- 无 ROS 2 standard joint_trajectory_controller
- 自定义 Action 接口（非 standard ROS 2 control messages）

## Configuration Constraints

- 手臂参数：arms.yaml（TCP offset、URDF、home 位置）
- 技能参数：每个 skill 独立的 params.yaml
- 工作流参数：tofu_workflow_params.yaml（步骤列表与 profile 映射）
- 视觉参数：vision_params.yaml（SAM3 模型路径、检测阈值等）
- 手眼标定：calibration_result_left.yaml / calibration_result_right.yaml
