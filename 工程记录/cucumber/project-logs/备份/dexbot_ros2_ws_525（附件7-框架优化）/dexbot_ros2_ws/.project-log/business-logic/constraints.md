# Business Logic Constraints

## System Constraints

- ROS2 Humble
- 编译路径不能含中文字符（rosidl 适配器 bug）
- 嵌套在 dexbot_middle_layer/CutTofo/ 下的包需用 --paths 显式编译

## Hardware Constraints

- 左臂 xCore 机械臂 IP: 192.168.2.160
- 右臂 xCore 机械臂 IP: 192.168.2.161
- O6 手爪: 左臂 CAN0, 右臂 CAN1（需确认）
- RealSense D435: USB 3.0

## Software Constraints

- xCore SDK: xcoresdk_python-v0.5.1.ar_12
- SAM3 模型: 需指定 model_path（默认在 vision_params.yaml）
- 视觉 topic 使用 cuttofu 命名空间 (/cuttofu/perception/*, /cuttofu/vision/*)
- 可启用 legacy topic relay 桥接到 /objects_with_pose

## Real-Time / Threading Constraints

- cucumber_hold node: MultiThreadedExecutor + 独立线程订阅感知（CucumberHoldLock）
- 右臂 RT 运动: 通过 xcore_controller_node 的 MoveRtCartesianPath service
- NRT 运动: MoveJ + calcIk 循环（0.08m 步长）

## Safety Constraints

- RT 运动尝试阻抗控制失败时 fallback 到位置控制（确保不丢失控制权）
- 左臂 NRT 运动后验证实际移动（_verify_arm_moved）
- 右臂到达验证: tolerance 2°, timeout 10s

## SDK / API Constraints

- 左臂: XCoreLbotRobot（SDK 直连，不需要 ROS 控制节点）
- 右臂: XcoreArmAdapter → ROS services（依赖 xcore_controller_node）
- ROS service 列表: get_state, move_joints, move_rt_cartesian_path, move_cartesian, enable_arm

## Configuration Constraints

- cucumber_hold_params.yaml: 左臂 IP, tool offset, motion params
- tofu_prepare_params.yaml: 右臂切割 profile, vision params
- tofu_cut_round_params.yaml: 切割参数, RT stiffness
- cucumber_workflow_params.yaml: orchestrator 工作流步骤
- arms.yaml: 双臂 URDF, namespace, joint names, TCP offset
