# Business Logic Edges

## Edge Template

```yaml
edge_id: <edge-id>
from: <start-node-id>
to: <target-node-id>
path: main | branch | archived
status: draft | stable | testing | validated | archived
method: <method summary>
execution_chain:
  - <step 1>
  - <step 2>
inputs:
  - <input>
outputs:
  - <output>
parameters:
  - name: <parameter-name>
    type: <data-type>
    default: <default-value>
    source: <config/code/user/hardware>
interfaces:
  - <topic/service/API/SDK/protocol>
error_handling:
  - <failure condition and response>
verification:
  - <verification method>
notes:
  - <notes>
```

## Edges

### Edge A -> B: handle_approach（抓刀）

```yaml
edge_id: A-B
from: A
to: B
path: main
status: stable
method: 视觉引导的 5 步接近 → O6 抓握 → TCP 回撤 → 关节归位
execution_chain:
  - 发布 SAM prompt "wooden cleaver handle"
  - 从 /cuttofu/perception/objects_with_pose 锁刀把位姿
  - 计算 5 步 TCP 接近航点
  - 逐段 MoveJ 接近刀把
  - O6 灵巧手闭合抓取
  - TCP 沿 +Y 方向回撤
  - 关节空间 MoveJ 回到 home
inputs:
  - /cuttofu/perception/objects_with_pose
  - profile: 'default'
outputs:
  - final_tcp_pose
parameters:
  - name: lock_timeout_s
    type: float64
    default: 30.0
    source: config/handle_approach_params.yaml
  - name: hand_o6_close_degrees_csv
    type: string
    default: '0,70,0,0,0,0'
    source: config
interfaces:
  - /handle_approach/execute (Action)
  - xCore SDK move_joint / move_cartesian
  - O6 hand CAN protocol
error_handling:
  - perception timeout: Report and abort
  - no detected handle: Retry with backoff
  - motion timeout: Report TIMEOUT error
```

### Edge A/C/E -> D/F: cut_round（水平圆切）

```yaml
edge_id: A-C-D
from: C
to: D
path: main
status: stable
method: 阻抗控制模式下的水平圆切，带返回和等待位姿
execution_chain:
  - 切换到阻抗控制模式 (stiffness ~3000)
  - 构建圆形切割航点（8 周期，flange_z 方向）
  - 逐点 MoveRCartesianPath (阻抗)
  - 每周期 step_z -0.0155m 向下步进
  - 切完回到预备位姿
  - 移动到等待位姿（waiting_for_resume=true）
inputs:
  - profile: round_1 / round_2 / cucumber
outputs:
  - executed_waypoints
  - feedback: waiting_for_resume, round_index
parameters:
  - name: cycles
    type: int
    default: 8
    source: config/tofu_cut_round_params.yaml
  - name: step_z_m
    type: float
    default: -0.0155
    source: config
  - name: stiffness
    type: int
    default: 3000
    source: config
  - name: return_to_prepare
    type: bool
    default: true
    source: config
interfaces:
  - /tofu_cut_round/execute (Action)
  - /tofu_cut_round/resume (Service)
  - xCore SDK RT impedance mode
```

### Edge A/E -> G/H: vertical_cut（垂直切割）

```yaml
edge_id: E-H
from: E
to: H
path: main
status: stable
method: 位置控制模式下的 base_y 方向垂直切割，带推力段
execution_chain:
  - 切换到位置控制模式
  - 构建垂直切割航点（11 周期，base_y 方向）
  - 每周期 step_z -0.006m 向下步进
  - 中段推力段：额外 step_z 下压
  - 尾部推力段：最终下压 + 回撤
  - 回到 home
inputs:
  - profile: default
outputs:
  - executed_waypoints
  - elapsed_s
parameters:
  - name: cycles
    type: int
    default: 11
    source: config/tofu_vertical_cut_params.yaml
  - name: step_z_m
    type: float
    default: -0.006
    source: config
interfaces:
  - /tofu_vertical_cut/execute (Action)
  - xCore SDK position mode
```

### Edge A -> B -> C -> D（阶段 1 自动流程）

```yaml
edge_id: phase1-auto
from: A
to: D
path: main
status: stable
method: 编排器按 steps 顺序执行，无操作员介入
execution_chain:
  - TofuTaskOrchestrator tick 循环
  - 依次 dispatch: handle_approach → prepare first_cut → cut_round round_1
  - 每个 action 等待 result
  - 完成后编排器退出
inputs:
  - tofu_workflow_params.yaml steps: phase1
parameters:
  - name: send_goal_timeout_sec
    type: float64
    default: 60.0
    source: config
interfaces:
  - Action clients for each skill
```

### Edge D -> E -> F -> G -> H（阶段 2-3 人工介入流程）

```yaml
edge_id: phase2-3
from: D
to: H
path: main
status: stable
method: 编排器在各阶段前等待操作员确认
execution_chain:
  - 阶段 2: wait_before (phase_after_round_1) → prepare first_cut → cut_round round_2
  - 阶段 3: wait_before (phase_after_round_2) → prepare after_rotation_1 → vertical_cut
inputs:
  - operator continue via /cuttofo_operator/continue service
parameters:
  - name: wait_profile
    type: string
    values: [phase_after_round_1, phase_after_round_2]
    source: config
  - name: settle_before_sec
    type: float64
    default: 2.0
    source: config
```

### Edge A -> I -> C' -> D' -> I': cucumber workflow

```yaml
edge_id: cucumber
from: A
to: I
path: branch
status: stable
method: 左臂夹持 → 右臂预备 → 圆切 → 左臂释放
execution_chain:
  - cucumber_hold default (左臂 xCore SDK 直连)
  - prepare cucumber (右臂 ROS service)
  - cut_round cucumber (右臂 ROS service)
  - cucumber_hold release (左臂归位)
inputs:
  - cucumber_workflow_params.yaml
interfaces:
  - /cucumber_hold/execute (Action)
  - /tofu_prepare/execute (Action)
  - /tofu_cut_round/execute (Action)
```

### Edge J -> K: 示教轨迹回放抓瓶

```yaml
edge_id: J-K
from: J
to: K
path: branch
status: draft
method: 示教轨迹回放 + O6 抓取
execution_chain:
  - 加载示教轨迹 JSON（XcoreDirectExecutor 下 xcore_data/ 目录）
  - 逐帧 MoveJ 沿示教轨迹从准备位姿到瓶口抓取位姿
  - O6 set_angles(grasp_angle) + set_torques(grasp_torque) 闭合抓瓶
  - TCP 在瓶口位置（不夹持刀，使用全零 TCP 或实际法兰 TCP）
inputs:
  - teach_joint_trajectory（n x 7 关节角度 JSON）
  - profile: 'default'
outputs:
  - grasped（O6 已抓住瓶子）
parameters:
  - name: grasp_angle_csv
    type: string
    default: 'X,X,X,X,X,X' (6 个 O6 关节)
    source: config/sauce_pour_params.yaml
  - name: grasp_torque_csv
    type: string
    default: 'X,X,X,X,X,X'
    source: config
interfaces:
  - /sauce_pour/execute (Action)
  - xCore SDK move_joint
  - O6 hand CAN protocol
error_handling:
  - 轨迹加载失败：Report file not found
  - MoveJ 超时：Report TIMEOUT
```

### Edge K -> L（含 K-a -> K-b 子阶段）：抬升 + 视觉引导倾倒

```yaml
edge_id: K-L
from: K
to: L
path: branch
status: draft
method: 沿 BASE Y- 抬升 → 视觉锁豆腐 → TCP目标→法兰目标数学换算 → IK 求法兰倾倒姿态 → MoveJ
sub_edges:
  - K-a: 抬升
  - K-b: 视觉 + 法兰目标换算 + IK
execution_chain:
  - K-a: 读取当前法兰位姿，沿 base 坐标系 Y 负方向移动 lift_distance_m（笛卡尔线性移动 CartesianMove，发送法兰位姿）
  - K-b:
    - VisionGeometryTracker 锁定 /cuttofu/perception/objects_with_pose 中豆腐中心 pose
    - TCP 目标位置 = 豆腐中心 + tcp_target_offset（可调）
    - **法兰目标换算**: flange_target_pos = tcp_target_pos - R_target @ tool_offset
      （不创建实际 TCP 坐标系，tool_offset 仅为数学参数）
    - IK 求解倾倒姿态（复用 solve_prepare_candidates，入参为 **法兰目标** 位姿）
    - MoveJ 到求解的关节角
inputs:
  - /cuttofu/perception/objects_with_pose（豆腐位姿）
  - sauce_pour_params.yaml
  - 当前法兰位姿（来自 K 执行结果）
outputs:
  - tofu_center_pose（视觉锁定值）
  - pour_tcp_pose（最终到达的瓶口 TCP 位姿）
parameters:
  - name: lift_distance_m
    type: float
    default: 0.15
    source: config
  - name: tool_offset_translation_m
    type: list[float]
    default: [0.0, 0.0, 0.15]
    source: config
    note: TCP(瓶口) 相对法兰的平移，仅用于 flange_target = tcp_target - R @ offset 数学换算
  - name: tool_offset_rotation_rpy_deg
    type: list[float]
    default: [0.0, 0.0, 0.0]
    source: config
    note: TCP(瓶口) 相对法兰的旋转（通常为零，纯平移 offset）
  - name: tcp_target_offset_translation_m
    type: list[float]
    default: [0.0, 0.0, 0.02]
    source: config
  - name: tcp_target_offset_rotation_rpy_deg
    type: list[float]
    default: [0.0, 0.0, 0.0]
    source: config
  - name: lock_timeout_s
    type: float
    default: 30.0
    source: config
  - name: num_pose_candidates
    type: int
    default: 36
    source: config
interfaces:
  - xCore SDK CartesianMove / move_joint
  - VisionGeometryTracker
  - PrepareSolver（IK 求解器）
  - FlangePoseCandidates（位姿候选筛选）
error_handling:
  - 视觉锁超时：Report and abort
  - IK 无解：扩大候选范围或 report failure
```

### Edge L -> M: 灵巧手周期性挤酱

```yaml
edge_id: L-M
from: L
to: M
path: branch
status: draft
method: O6 灵巧手周期性收紧 - 松开循环
execution_chain:
  - 循环 i = 1 到 squeeze_cycles:
    - set_angles(squeeze_angle_csv) + set_torques(squeeze_torque_csv)
    - sleep(squeeze_interval_s)
    - set_angles(release_angle_csv) + set_torques(release_torque_csv)
    - sleep(squeeze_interval_s)
  - 最终保持松开状态
inputs:
  - squeeze_cycles
outputs:
  - squeeze_count
parameters:
  - name: squeeze_cycles
    type: int
    default: 3
    source: config
  - name: squeeze_angle_csv
    type: string
    default: 'X,X,X,X,X,X'
    source: config
  - name: squeeze_torque_csv
    type: string
    default: 'X,X,X,X,X,X'
    source: config
  - name: release_angle_csv
    type: string
    default: 'X,X,X,X,X,X'
    source: config
  - name: release_torque_csv
    type: string
    default: 'X,X,X,X,X,X'
    source: config
  - name: squeeze_interval_s
    type: float
    default: 0.5
    source: config
interfaces:
  - O6 hand CAN protocol set_angles / set_torques
error_handling:
  - O6 通信超时：Retry or report DEVICE_ERROR
```

### Edge M -> N -> O: 放瓶回原位 + 归位

```yaml
edge_id: M-N-O
from: M
to: O
path: branch
status: draft
method: 先回抬升位姿 → 反向回放示教轨迹 → 松手 → 回 home
execution_chain:
  - MoveJ 回到 K-a 抬升后的位姿
  - 逆序逐帧回放 J->K 轨迹（从瓶口下降回瓶底到位）
  - O6 set_angles(release_angle_csv) + set_torques(0,0,0,0,0,0) 松手
  - MoveJ 回到 home_joint_angles
inputs:
  - K-a 抬升后位姿（内部状态）
  - teach_joint_trajectory（逆序）
outputs:
  - bottle_placed
parameters:
  - name: home_joint_angles
    type: list[float]
    default: [0.0, ...] (7 个关节)
    source: config
interfaces:
  - xCore SDK move_joint
  - O6 hand CAN protocol
error_handling:
  - MoveJ 超时：Report TIMEOUT
```
