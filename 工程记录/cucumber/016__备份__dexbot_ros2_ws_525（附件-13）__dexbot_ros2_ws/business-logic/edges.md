# Business Logic Edges

## Edge A→B — cucumber_hold:default

```yaml
edge_id: A->B
from: A
to: B
path: main
status: stable
method: 左臂直连 SDK，NRT MoveJ 分段移动到黄瓜按压位姿
execution_chain:
  - 发布 SAM text prompt "cucumber" 到 /cuttofu/vision/text_prompt
  - CucumberHoldLock 配置 hold_along_axis_fraction=1（末端）+ press_down_m=0
  - CucumberHoldLock 订阅 /cuttofu/perception/objects_with_pose，锁定稳定黄瓜位姿（lock_min_samples=2, std<0.03m）
  - right_base_point_to_left(locked_point) 通过手眼标定转换到左臂基坐标系
  - XcoreDirectExecutor.connect() 直连左臂 SDK
  - 计算 press_left = b_left + manual_offset_m[-0.03, 0, 0.05]
  - 计算 approach_left = press_left + approach_offset_m[0, -0.08, 0.08]
  - nrt_direct_to_press=false → 先走 approach_left 再走 press_left（两段 MoveJ）
  - NRT MoveJ 分段走到 approach_left → press_left（子步骤 0.08m/step）
  - 左臂到位后发布 shared_cucumber_geometry
inputs:
  - /cuttofu/perception/objects_with_pose (ObjectStateArray)
  - calibration_result_left.yaml (手眼标定)
outputs:
  - /cuttofu/perception/shared_cucumber_geometry
  - hold_point_right, hold_point_left (Action result)
parameters:
  - name: lock_min_samples
    type: int
    default: 2
    source: cucumber_hold_params.yaml
  - name: motion_mode
    type: string
    default: nrt
    source: cucumber_hold_params.yaml/profiles/default
  - name: manual_offset_m
    type: float[3]
    default: [-0.03, 0.00, 0.05]
    source: cucumber_hold_params.yaml/profiles/default
  - name: approach_offset_m
    type: float[3]
    default: [0.0, -0.08, 0.08]
    source: cucumber_hold_params.yaml/profiles/default
  - name: hold_along_axis_fraction
    type: float
    default: 1
    source: cucumber_hold_params.yaml/profiles/default
  - name: press_down_m
    type: float
    default: 0.0
    source: cucumber_hold_params.yaml/profiles/default
  - name: nrt_direct_to_press
    type: bool
    default: false
    source: cucumber_hold_params.yaml/profiles/default
  - name: nrt_approach_min_separation_m
    type: float
    default: 0.01
    source: cucumber_hold_params.yaml/profiles/default
interfaces:
  - /cucumber_hold/execute (Action, ExecuteCucumberHold)
  - /cuttofu/perception/objects_with_pose (Subscription)
  - 左臂 SDK: XCoreLbotRobot (TCP/IP)
error_handling:
  - 视觉超时: 返回错误代码 + diagnostics summary
  - SDK 连接失败: 返回 connecting 阶段错误
  - NRT MoveJ 失败: 缩小 step 重试 press_left，失败则返回详细错误
verification:
  - _verify_arm_moved() 检查关节/法兰实际移动
  - 返回 success = true + hold_point_left
notes:
  - 左臂直连 SDK，不需要 xcore_controller_node
  - vision_timeout_s: 15s (SAM ~1Hz, lock_min_samples=2)
```

## Edge B→C — prepare:cucumber

```yaml
edge_id: B->C
from: B
to: C
path: main
status: stable
method: 右臂 IK 求解预备切姿，MoveJ 移动到目标关节角
execution_chain:
  - TofuPrepareNode 收到 ExecuteTofuPrepare Goal (profile: cucumber)
  - XcoreArmAdapter.connect() 连接右臂 controller ROS services
  - XcoreArmAdapter.enable_arm(True) 使能右臂
  - 配置 VisionGeometryTracker（class_filter: cucumber）
  - 检测 use_shared_hold_geometry = true，复用 hold 发布的 shared geometry
  - 从 vision geometry 获取黄瓜 top_corners + edge_dir
  - 调用 apply_cucumber_prepare_target_offsets() 应用偏移
  - IK 求解: OfflineURDFKinematics + solve_prepare_candidates (40 candidates)
  - cut_preview 检查轨迹安全性
  - 评分排序，选择最优 IK 解
  - XcoreArmAdapter.move_to_joints() 发送 MoveJ 请求到 /arm_r/robot/move_joints
  - verify_arrival 确认到达（tolerance 2°）
inputs:
  - shared_cucumber_geometry (从 Node B 发布)
  - vision_geometry_tracker (视觉追踪)
  - arms.yaml (右臂 URDF/TCP offset)
outputs:
  - reached_joints (float64[7])
  - reached_tcp_pose (Pose)
parameters:
  - name: plane_angle_deg
    type: float
    default: 90.0
    source: tofu_prepare_params.yaml/profiles/cucumber
  - name: target_offset_m
    type: float[3]
    default: [-0.02, 0.03, 0.00]
    source: tofu_prepare_params.yaml/profiles/cucumber
  - name: hold_along_axis_fraction
    type: float
    default: -1
    source: tofu_prepare_params.yaml/profiles/cucumber
  - name: joint_speed
    type: float
    default: 0.3
    source: tofu_prepare_params.yaml/profiles/cucumber
  - name: ik_retry_count
    type: int
    default: 20
    source: tofu_prepare_params.yaml/profiles/cucumber
interfaces:
  - /tofu_prepare/execute (Action, ExecuteTofuPrepare)
  - /arm_r/robot/move_joints (Service, MoveJoints)
  - /arm_r/robot/enable_arm (Service, EnableArm)
  - /arm_r/robot/get_state (Service, GetRobotState)
error_handling:
  - IK 无解: 返回 ik_no_solution / no_candidate_passed_cut_preview
  - MoveJ 失败: 返回 move_to_joints_failed
  - 到达超时: 返回 arrival_verification_failed
verification:
  - IK 求解成功且有经过 cut_preview 检查的解
  - move_to_joints 返回 success
  - verify_arrival 误差 < 2°
notes:
  - 右臂依赖 xcore_controller_node（/arm_r/namespace）
  - settle_before_sec: 1.0s (hold 后等待手臂静止)
```

## Edge C→D — cut_round:cucumber

```yaml
edge_id: C->D
from: C
to: D
path: main
status: stable
method: 右臂 RT 笛卡尔路径竖切
execution_chain:
  - TofuCutRoundNode 收到 ExecuteTofuCutRound Goal (profile: cucumber)
  - XcoreArmAdapter.connect() 连接到右臂 controller
  - XcoreArmAdapter.enable_arm(True) 使能右臂
  - rt_settle_delay_s 等待（默认 1.0s），确保手臂静止
  - flange_matrix_from_arm() 读取当前法兰位姿
  - build_cut_cycle_waypoints() 生成切割路径点 (10 cycles)
  - move_rt_cartesian_path() 执行 RT 切割（每刀 flange_z 方向 8.5mm，step_z -0.003mm）
  - skip_return_anchor: true (不执行 TCP 回撤)
  - skip_human_wait: true (不等人按回车)
  - wait_joint_positions 移动到等待位姿
inputs:
  - 右臂当前 flange pose
  - cut profile 参数
outputs:
  - executed_waypoints (int)
  - elapsed_s (float)
parameters:
  - name: cycles
    type: int
    default: 10
    source: tofu_cut_round_params.yaml/profiles/cucumber/cut
  - name: cut_move
    type: float
    default: 0.085
    source: tofu_cut_round_params.yaml/profiles/cucumber/cut
  - name: step_z
    type: float
    default: -0.003
    source: tofu_cut_round_params.yaml/profiles/cucumber/cut
  - name: cut_direction
    type: string
    default: flange_z
    source: tofu_cut_round_params.yaml/profiles/cucumber/cut
  - name: max_linear_velocity
    type: float
    default: 0.04
    source: tofu_cut_round_params.yaml/profiles/cucumber/cut
  - name: stiffness
    type: float[6]
    default: [3000, 3000, 3000, 300, 300, 300]
    source: tofu_cut_round_params.yaml/profiles/cucumber/cut
interfaces:
  - /tofu_cut_round/execute (Action, ExecuteTofuCutRound)
  - /arm_r/robot/move_rt_cartesian_path (Service, MoveRtCartesianPath)
  - /arm_r/robot/get_state (Service, GetRobotState)
error_handling:
  - RT 运动失败: 尝试 fallback mode (impedance → position)
  - 超时: 返回 timeout error
verification:
  - 返回 success = true
  - executed_waypoints > 0
notes:
  - 黄瓜切割使用阻抗控制 (stiffness 3000)
  - 10 刀，每刀进给 3mm，切割深度 8.5mm
```

## Edge D→E — cucumber_hold:release

```yaml
edge_id: D->E
from: D
to: E
path: main
status: stable
method: 左臂 MoveAbsJ 回到 home 关节角
execution_chain:
  - CucumberHoldNode 收到 ExecuteCucumberHold Goal (profile: release)
  - XcoreDirectExecutor.connect() 直连左臂 SDK
  - 读取 home_joint_positions_deg 配置
  - np.deg2rad() 转为弧度
  - executor.move_to_joints() 发送 MoveAbsJ 指令
  - executor.disconnect()
inputs:
  - home_joint_positions_deg (配置)
outputs:
  - result.success = true / false
parameters:
  - name: joint_speed
    type: float
    default: 0.3
    source: cucumber_hold_params.yaml/profiles/release
  - name: home_joint_positions_deg
    type: float[7]
    default: [-2.2, 45.3, 53.31, 39.54, 12.35, 50.08, 30.19]
    source: cucumber_hold_params.yaml/profiles/release
interfaces:
  - /cucumber_hold/execute (Action, ExecuteCucumberHold)
  - 左臂 SDK: XCoreLbotRobot (TCP/IP)
error_handling:
  - SDK 连接失败: 返回 connecting 错误
  - move_to_joints 失败: 返回 move_to_home_failed
verification:
  - move_to_joints 返回 true
notes:
  - 不需要视觉、不需要 xcore_controller_node
```
