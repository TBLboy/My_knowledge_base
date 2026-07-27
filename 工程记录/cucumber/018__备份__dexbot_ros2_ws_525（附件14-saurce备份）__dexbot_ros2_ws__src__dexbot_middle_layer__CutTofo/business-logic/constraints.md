# Business Logic Constraints

## System Constraints

- ROS 2 Humble (rclpy)
- rmw_cyclonedds_cpp middleware
- ROS_DOMAIN_ID 须一致

## Hardware Constraints

- xCore AR5 机械臂（7-DOF）
  - 左臂 IP: 192.168.2.160
  - 右臂 IP: 192.168.2.161
  - xCore SDK Python v0.5.1.ar_12
- LinkerHand O6 灵巧手
  - 左：CAN1
  - 右：CAN0
  - bitrate: 1000000
- Intel RealSense D4xx
  - 深度对齐到彩色分辨率

## Software Constraints

- 左臂：XcoreDirectExecutor（SDK 直连）
- 右臂：XcoreArmAdapter（ROS service）
- SAM3 模型需 HuggingFace 格式本地目录（含 config.json）

## Real-Time / Threading Constraints

- 阻抗控制模式使用 RT 运动（阻抗模式下 MoveRCartesianPath）
- 位置控制模式使用 NRT 运动（MoveJ / MoveL）
- MultiThreadedExecutor 用于 Action server（skill 节点）
- SpinOnce 用于 Orchestrator（tick-driven）

## Safety Constraints

- 段间停顿（follow_batch_inter_sleep_sec）
- SDK 运动等待超时（sdk_motion_wait_timeout_sec: 60s）
- 关节收敛超时（sdk_joint_converge_timeout_sec: 25s）

## SDK / API Constraints

- xCore SDK 无类型化 ROS 接口，需通过 service 调用
- O6 手通过 CAN 发送原始字节帧（无高级 SDK）
- SAM3 推理在 GPU 上，需 nvidia_uvm 模块加载

## Configuration Constraints

- `arms.yaml`: 定义双臂参数（IP、URDF、TCP 偏移、home 位姿）
- YAML 配置支持环境变量覆盖（如 CUTTOFO_ARM_CONFIG）
- 校准文件通过 YAML 路径引用，不支持 ROS parameter server
