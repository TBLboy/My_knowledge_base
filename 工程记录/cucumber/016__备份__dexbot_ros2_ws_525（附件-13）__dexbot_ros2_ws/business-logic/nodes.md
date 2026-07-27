# Business Logic Nodes

## Node A — Idle

```yaml
id: A
name: Idle
status: stable
state:
  - 视觉管线运行中（RealSense + SAM3 + pose_estimator）
  - 左右臂 controller 节点运行中（xcore_controller_node x2）
  - 所有 skill Action Server 运行中
  - orchestrator 等待触发
inputs: []
outputs:
  - /cuttofu/perception/objects_with_pose
  - /arm_r/robot/get_state, move_joints, move_rt_cartesian_path, etc.
  - 左臂 SDK 连接（IP 192.168.2.160）
data_format:
  - 视觉: ObjectStateArray
  - 右臂控制: dexbot_interfaces_low 定义的 ROS services
related_hardware:
  - RealSense D435
  - 左臂 xCore 机械臂（连接 IP 192.168.2.160）
  - 右臂 xCore 机械臂（连接 IP 192.168.2.161）
  - O6 手爪（左臂 CAN0，右臂 CAN1）
related_interfaces:
  - /cuttofu/vision/text_prompt (发布 SAM3 prompt)
  - /cuttofu/perception/objects_with_pose (订阅检测结果)
  - /arm_r/robot/* (ROS service 控制右臂)
  - 左臂: XCoreLbotRobot (SDK 直连)
verification:
  - 各 node 进程无异常退出
  - source install/setup.bash 后 ros2 pkg prefix 可见所有包
notes:
  - 终端 1: vision_bringup.launch.py
  - 终端 2: dual_xcore_controllers.launch.py
  - 终端 3: cucumber_workflow_execute.launch.py
```

## Node B — Cucumber Held

```yaml
id: B
name: Cucumber Held
status: stable
state:
  - left 臂已移动到 press_left 位姿（按住黄瓜）
  - shared_cucumber_geometry 已发布（供 prepare skill 复用）
inputs:
  - /cuttofu/perception/objects_with_pose (cucumber 锁定)
  - right_base_point_to_left 变换（手眼标定）
outputs:
  - /cuttofu/perception/shared_cucumber_geometry
data_format:
  - 黄瓜锁定: (x, y, z) 右臂基坐标系 → 左臂基坐标系
  - shared_geometry: 自定义消息
related_hardware:
  - 左臂 xCore + SDK 直连
related_interfaces:
  - /cucumber_hold/execute (Action Server)
  - CucumberHoldLock (独立线程订阅 objects_with_pose)
verification:
  - hold_point_right / hold_point_left 无误
  - 左臂实际移动到位
notes:
  - motion_mode: nrt (MoveJ segments, step 0.08m)
  - manual_offset_m: [-0.03, 0.00, 0.05] 左臂基座偏移
  - hold_along_axis_fraction: 1（黄瓜沿主轴偏移到末端）
  - press_down_m: 0.0（不下压）
```

## Node C — Knife Ready at Cut Pose

```yaml
id: C
name: Knife Ready at Cut Pose
status: stable
state:
  - 右臂已通过 IK 求解到达预备切姿
  - TCP 工具坐标系对准黄瓜切割位置
inputs:
  - shared_cucumber_geometry (复用 hold 锁定结果)
  - vision_geometry_tracker (视觉几何追踪)
outputs:
  - 右臂当前关节角: joint positions
data_format:
  - joint_positions: float64[7]
  - TCP target: Pose (base frame)
related_hardware:
  - 右臂 xCore（通过 ROS services 控制）
related_interfaces:
  - /tofu_prepare/execute (Action Server)
  - /arm_r/robot/move_joints (MoveJ)
  - /arm_r/robot/enable_arm
  - OfflineURDFKinematics (IK 求解)
verification:
  - IK 求解成功（valid candidates > 0）
  - 关节角到达误差 < 2°
  - cut_preview 检查无越界
notes:
  - profile: cucumber
  - use_shared_hold_geometry: true (避免左臂遮挡后重识别)
  - plane_angle_deg: 90° (竖切)
  - target_offset_m: [-0.02, 0.03, 0.00]
```

## Node D — Cutting Complete

```yaml
id: D
name: Cutting Complete
status: stable
state:
  - 右臂已完成 10 次竖切
  - 每次切割 8.5mm 深度，-3mm/刀 进给
  - skip_return_anchor: true (切完不走 TCP 回撤)
  - skip_human_wait: true (无人力等待)
inputs:
  - 右臂 flange pose (切割起点)
  - cut profile 参数
outputs: []
data_format:
  - waypoints: RT 笛卡尔路径点列表
  - executed_steps: int
related_hardware:
  - 右臂 xCore RT 控制 (move_rt_cartesian_path)
related_interfaces:
  - /tofu_cut_round/execute (Action Server)
  - /arm_r/robot/move_rt_cartesian_path
verification:
  - 返回 success = true
  - 无超时/中断
notes:
  - impedance: prefer_impedance=true, fallback_to_rt_position=true
  - stiffness: [3000, 3000, 3000, 300, 300, 300]
```

## Node E — Initial State Restored

```yaml
id: E
name: Initial State Restored
status: stable
state:
  - 左臂回到 home 关节角
  - 工作流执行完毕，orchestrator 退出
inputs:
  - home_joint_positions_deg (配置)
outputs: []
data_format:
  - home_joint_positions_deg: [-2.2, 45.3, 53.31, 39.54, 12.35, 50.08, 30.19]
related_hardware:
  - 左臂 xCore SDK
related_interfaces:
  - /cucumber_hold/execute (profile: release)
verification:
  - move_to_joints 成功返回 true
notes:
  - 释放完成后 orchestrator 进程自动退出
  - 视觉和 controller 节点仍需手动关闭
```
