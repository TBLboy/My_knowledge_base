# Business Logic Nodes

## Node Template

```yaml
id: <node-id>
name: <node-name>
status: draft | stable | deprecated
state:
  - <what has become true at this node>
inputs:
  - <required input data or signal>
outputs:
  - <available output data or signal>
data_format:
  - <data type, message type, file type, coordinate frame, etc.>
related_hardware:
  - <hardware if any>
related_interfaces:
  - <ROS topic/service/action, API, SDK, protocol, etc.>
verification:
  - <how to confirm this state is reached>
notes:
  - <notes>
```

## Nodes

### A: 双臂控制器就绪

```yaml
id: A
name: dual_arm_control_ready
status: stable
state:
  - 双臂 xCore 控制器已启动，关节反馈可用
  - RealSense 相机已启动，/camera/color/image_raw 有数据
  - SAM3 + pose_estimator 已启动，/cuttofu/perception/objects_with_pose 有数据
inputs:
  - 左臂 IP 192.168.2.160
  - 右臂 IP 192.168.2.161
  - hand-eye calibration files
outputs:
  - /joint_states (双臂)
  - /cuttofu/perception/objects_with_pose
  - /camera/color/image_raw
related_hardware:
  - xCore AR5 左臂 (192.168.2.160)
  - xCore AR5 右臂 (192.168.2.161)
  - Intel RealSense D4xx
related_interfaces:
  - ros2 launch dexbot_bringup dual_xcore_controllers.launch.py
  - ros2 launch cuttofu_vision vision_bringup.launch.py
verification:
  - ros2 topic echo /joint_states --once
  - ros2 topic echo /cuttofu/perception/objects_with_pose --once
```

### B: 刀把抓取完成

```yaml
id: B
name: handle_grasped
status: stable
state:
  - O6 灵巧手已抓取刀把
  - 刀把 TCP 已回撤到 home 位姿
inputs:
  - /handle_approach/execute action goal
  - /cuttofu/perception/objects_with_pose (刀把位姿)
outputs:
  - final_tcp_pose (抓取后的 TCP 位姿)
related_hardware:
  - LinkerHand O6 (CAN0, right side)
  - xCore 右臂 (192.168.2.161)
related_interfaces:
  - /handle_approach/execute (Action)
  - cuttofo_skill_interfaces/action/ExecuteHandleApproach
verification:
  - ros2 action send_goal /handle_approach/execute ...
```

### C: 切刀预备位姿到达

```yaml
id: C
name: prepare_pose_reached
status: stable
state:
  - 刀 TCP 已到达豆腐上方预备位姿
  - 切割轨迹经 IK 预览验证
inputs:
  - /tofu_prepare/execute action goal (profile, vision data)
  - /cuttofu/perception/objects_with_pose (豆腐位姿)
outputs:
  - reached_tcp_pose
  - reached_joints
related_hardware:
  - xCore 右臂 (192.168.2.161)
related_interfaces:
  - /tofu_prepare/execute (Action)
  - cuttofo_skill_interfaces/action/ExecuteTofuPrepare
verification:
  - ros2 action send_goal /tofu_prepare/execute "{profile: 'first_cut', use_vision: true}"
```

### D/F: 水平圆切完成

```yaml
id: D
name: round_cut_completed
status: stable
state:
  - 已完成指定周期数的阻抗圆切
  - 刀已回到等待位姿
  - (可选) waiting_for_resume = true
inputs:
  - /tofu_cut_round/execute action goal (profile)
outputs:
  - executed_waypoints count
  - feedback: waiting_for_resume, round_index
related_hardware:
  - xCore 右臂 (192.168.2.161)
related_interfaces:
  - /tofu_cut_round/execute (Action)
  - /tofu_cut_round/resume (Service)
  - cuttofo_skill_interfaces/action/ExecuteTofuCutRound
  - cuttofo_skill_interfaces/srv/ResumeTofuCutRound
verification:
  - ros2 action send_goal /tofu_cut_round/execute "{profile: 'round_1'}"
```

### E/G: 预备位姿到达（旋转后）

```yaml
id: E
name: prepare_pose_after_rotation
status: stable
state:
  - 豆腐已由人工旋转
  - 刀已到达新的预备位姿（first_cut 或 after_rotation_1）
inputs:
  - /tofu_prepare/execute action goal
  - operator continue signal (/cuttofo_operator/continue)
outputs:
  - reached_tcp_pose
related_interfaces:
  - /tofu_prepare/execute (Action)
  - /cuttofo_operator/continue (Trigger)
```

### H: 垂直切割完成

```yaml
id: H
name: vertical_cut_completed
status: stable
state:
  - 已完成指定周期数的垂直位置切割
  - 含中段推力和尾部推力段
inputs:
  - /tofu_vertical_cut/execute action goal
outputs:
  - executed_waypoints count
  - elapsed_s
related_hardware:
  - xCore 右臂 (192.168.2.161)
related_interfaces:
  - /tofu_vertical_cut/execute (Action)
  - cuttofo_skill_interfaces/action/ExecuteTofuVerticalCut
```

### I: 黄瓜夹持完成 / 左臂归位

```yaml
id: I
name: cucumber_hold_completed
status: stable
state:
  - cucumber_hold default: 左臂已夹持黄瓜
  - cucumber_hold release: 左臂已回到 home
inputs:
  - /cucumber_hold/execute action goal
outputs:
  - hold_point_right, hold_point_left
related_hardware:
  - xCore 左臂 (192.168.2.160)
  - LinkerHand O6 (CAN1, left side)
related_interfaces:
  - /cucumber_hold/execute (Action)
  - cuttofo_skill_interfaces/action/ExecuteCucumberHold
```

### J: 示教轨迹采集完成（瓶前就绪）

```yaml
id: J
name: sauce_pour_teach_traj_ready
status: draft
state:
  - 已通过拖动示教采集从准备位姿到瓶前抓取位姿的关节轨迹 JSON
  - 轨迹路径由 config 中 teach_traj_path 指定
  - 瓶子在固定位置未被移动
inputs:
  - 示教采集脚本运行完毕（capture_left_pour_pose.py）
  - 关节角度序列 JSON 文件存在
outputs:
  - teach_joint_trajectory（n x 7 关节角度序列）
related_hardware:
  - xCore 左臂 (192.168.2.160)
related_interfaces:
  - capture_left_pour_pose.py（采集脚本）
verification:
  - ls <teach_traj_path> 确认 JSON 文件存在
  - 以只读模式回放验证轨迹
```

### K: 抓瓶 + 抬升 + 视觉锁豆腐 + 倾倒

```yaml
id: K
name: bottle_grasped_and_poured
status: draft
state:
  - O6 灵巧手已抓住酱料瓶
  - 左臂已抬升 lift_distance_m
  - 视觉已锁定豆腐中心位姿
  - IK 求解获得最优倾倒姿态并已到达
substates:
  - K-a: 抬升完成（沿 base Y- 方向移动固定距离）
  - K-b: 倾倒位姿已到达（法兰经数学换算后到达目标，瓶口 TCP 自动对准豆腐中心 + offset）
inputs:
  - sauce_pour_params.yaml（所有可调参数，含 tool_offset）
  - teach_joint_trajectory（来自节点 J）
  - /cuttofu/perception/objects_with_pose（豆腐位姿）
  - tool_offset 仅用于数学换算 flange_target = tcp_target - R @ offset，不创建实际 TCP 坐标系
outputs:
  - poured_flange_pose（法兰到达的目标位姿）
  - tofu_center_pose（视觉锁定的豆腐中心）
related_hardware:
  - xCore 左臂 (192.168.2.160)
  - LinkerHand O6 (CAN1, left side)
related_interfaces:
  - /sauce_pour/execute (Action)
  - xCore SDK move_joint / move_cartesian（发送法兰位姿，非 TCP 位姿）
  - O6 hand CAN protocol
  - VisionGeometryTracker（视觉跟踪）
  - solve_prepare_candidates（IK 求解器，入参为法兰目标位姿）
verification:
  - ROS action send_goal /sauce_pour/execute
  - 视觉日志显示 tofu_center_pose
```

### L: 倾倒位姿到达（瓶口对准豆腐）

```yaml
id: L
name: pour_pose_reached
status: draft
state:
  - 瓶口 TCP 已到达豆腐中心 + offset 位置
  - 姿态为选定的最优倾倒姿态
inputs:
  - 来自节点 K-b 的执行结果
outputs:
  - current_tcp_pose（用于后续归位计算）
related_hardware:
  - xCore 左臂 (192.168.2.160)
verification:
  - 执行完 IK 求解的 MoveJ 后等待 reaching 确认
```

### M: 灵巧手周期性挤酱完成

```yaml
id: M
name: squeeze_completed
status: draft
state:
  - O6 已完成 squeeze_cycles 次收紧 - 松开循环
  - 灵巧手当前处于松开状态
inputs:
  - squeeze_cycles（可调参数）
  - squeeze_angle / squeeze_torque（可调参数）
  - release_angle / release_torque（可调参数）
  - squeeze_interval_s（可调参数）
outputs:
  - squeeze_count（实际执行次数）
related_hardware:
  - LinkerHand O6 (CAN1, left side)
related_interfaces:
  - O6 hand CAN protocol set_angles + set_torques
verification:
  - 现场观察酱汁是否挤出到豆腐上
```

### N: 瓶子放回原位 + 松开

```yaml
id: N
name: bottle_placed_back
status: draft
state:
  - 左臂已沿原路返回：先回 K-a 位置 → 逆序回放示教轨迹 → 瓶底接触桌面
  - O6 灵巧手已松开
  - 瓶子竖直稳定在桌面上
inputs:
  - teach_joint_trajectory（来自节点 J，逆序回放使用）
  - K-a lift_distance_m（先回到抬升位置）
outputs:
  - bottle_placed（布尔标志）
related_hardware:
  - xCore 左臂 (192.168.2.160)
  - LinkerHand O6 (CAN1, left side)
related_interfaces:
  - xCore SDK move_joint
  - O6 hand CAN protocol set_angles + set_torques
verification:
  - 视觉确认或人工确认瓶子竖直在桌面
```

### O: 左臂回 home 位姿

```yaml
id: O
name: left_arm_home
status: draft
state:
  - 左臂已回到预定义的 home 关节位姿
  - 动作结束，可执行后续其他任务
inputs:
  - home_joint_angles（可调参数，或使用左臂默认 home）
outputs:
  - 无（任务结束）
related_hardware:
  - xCore 左臂 (192.168.2.160)
related_interfaces:
  - xCore SDK move_joint
verification:
  - 确认关节角度与 home 一致
```
