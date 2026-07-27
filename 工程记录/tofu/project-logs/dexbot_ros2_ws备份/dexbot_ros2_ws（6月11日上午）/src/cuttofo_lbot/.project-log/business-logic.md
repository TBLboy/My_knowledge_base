# 切豆腐项目 - 完整业务逻辑文档

> 创建日期: 2026-05-09
> 最后更新: 2026-05-09
> 机械臂后端: Lbot (LKRS73-I2 / LKLS73-O1)

## 1. 系统总览

### 1.1 目标

**当前聚焦 Phase 2**：拔刀后 → 计算刀预备位 → Lbot 机械臂移刀到预备切割姿态。

Phase 2 是整个切豆腐流程中最核心的业务逻辑：视觉感知豆腐位置 → 几何构造 TCP 目标点 → 姿态约束构建 → IK 求解 → 驱动机械臂到位。后续的切割（Phase 3）、旋转（Phase 4）、重新就位（Phase 5）由外部代码或其他模块实现。

**本版本与 xCore 版本的关键区别**：

| 方面 | xCore 版本 | Lbot 版本 |
|------|-----------|----------|
| 机械臂控制 | ROS Service (move_rt_cartesian_segment) | Python API 直调 (LbotRobot) |
| IK 求解 | URDF + scipy least_squares 多候选 | **Lbot 内置 IK** (黑盒, 单候选) |
| 刀姿态约束 | IK 求解器中通过旋转矩阵约束 | 约束编码到目标 euler 角中预计算 |
| 到位确认 | Action result + Service | 轮询关节角 |
| 依赖 | dexbot_interfaces_low (Service) | dexbot_bottom_layer (Python SDK) + Lbot Robot |

### 1.2 坐标系约定

| 坐标系 | X+ | Y+ | Z+ | 说明 |
|--------|----|----|----|------|
| Base   | 前 | 上 | 右 | 机械臂基座坐标系 |
| 法兰(归零) | 前 | 上 | 右 | 与base一致 |
| TCP(归零)  | 前 | 上 | 右 | 与法兰一致 |

### 1.3 核心约束

| 约束 | 数学表达 | 说明 |
|------|---------|------|
| 刀脊方向(默认) | `tcp_y · base_x = 1` | TCP Y轴与Base X同向 |
| 刀脊方向(边对齐) | `tcp_y · edge_dir = 1` | TCP Y轴沿豆腐边方向 |
| 刀面倾斜 | `tcp_z` 与 XZ平面夹角 = `plane_angle` | joint_6 ±40°安全限位 → max ≈ 40-45° |
| 关节安全余量 | ≥15°硬约束 | IK求解时关节实际限位 ±15° |

---

## 2. 整体业务流程（状态机）

```
                    ┌─────────────────────┐
                    │  Phase 0: 系统初始化   │
                    │  启动感知+标定+机械臂  │
                    └──────────┬──────────┘
                               │ 所有节点就绪
                    ┌──────────▼──────────┐
                    │  Phase 1: 拿刀        │
                    │  (外部动作，本项目不负责)│
                    └──────────┬──────────┘
                               │ /knife_grabbed (Bool, True)
                     ┌──────────▼──────────┐
                     │  Phase 3: 切豆腐      │                       │
                     │  (外部代码实现切削)     │                       │
                     │  本包仅发送"开始切"信号  │                       │
                     │  如发布 /cutting_start (Bool)                 │
                     └──────────┬──────────┘                       │
                               │ Action Result: success            │
                    ┌──────────▼──────────┐                       │
                    │  Phase 3: 切豆腐      │                       │
                    │  RT Service 循环切削   │                       │
                    │  (demo_cut_tofu_xcore_ros 逻辑)             │
                    └──────────┬──────────┘                       │
                               │ 切削完成 (N刀切完)                 │
                    ┌──────────▼──────────┐                       │
                    │  Phase 4: 等待旋转豆腐  │                       │
                    │  (外部动作，本项目不负责)│                       │
                    └──────────┬──────────┘                       │
                               │ /tofu_rotated (Bool, True)        │
                    ┌──────────▼──────────┐                       │
                    │  Phase 5: 重新就位     ├──────────────────────┘
                    │  豆腐位姿已变化        │
                    │  重新计算 → 移刀到新预备位│
                    └──────────┬──────────┘
                               │ 切削轮次结束 / 用户终止
                    ┌──────────▼──────────┐
                    │  Phase 6: 归位/放刀    │
                    │  机械臂回到安全位      │
                    └─────────────────────┘
```

### 2.1 状态转换条件

| 转换 | 触发条件 | 说明 |
|------|---------|------|
| 0→1 | 系统初始化完成 | 所有节点 alive |
| 1→2 | 收到 `/knife_grabbed` = True | 外部确认刀已拿好 |
| 2→3 | Action `/move_to_prepare_pose` 返回 success | 刀已到达预备位 |
| 3→4 | 切削循环完成 (N刀切完) | 外部切削代码返回 /cutting_done 信号 |
| 4→5 | 收到 `/tofu_rotated` = True | 外部确认旋转完毕 |
| 5→2 | 需要继续切 | 回到Phase 2重新就位 |
| 5→6 | 无下一轮切削 | 流程结束 |

### 2.2 异常与容错

| 异常 | 处理 |
|------|------|
| 感知丢失(豆腐看不见) | 协调节点等待超时 → 状态机暂停 → 重试或报错 |
| IK 无解 | Action 返回 failed → 等待 tofu_state 更新重试 |
| 切削中途机械臂异常 | Lbot API 返回 error → 协调节点中止 → 回安全位 |
| Lbot 连接断开 | 协调节点尝试重连 → 重连失败则报错 |
| 旋转信号超时 | 协调节点超时 → 用户手动干预 |
| tofu_state 连续 N 帧无效 | Action 还未启动时继续等待; 已启动时使用最后一次有效值 |

---

## 3. ROS 节点架构

### 3.1 节点清单

| 节点名 | 类型 | 包 | 状态 | 说明 |
|--------|------|---|------|------|
| `sam3_detector_node` | 已有 | dexbot_middle_layer | ✅ | SAM3 分割 → /detected_objects |
| `pose_estimator_node` | 已有 | dexbot_middle_layer | ✅ | 6D姿态估计 → /objects_with_pose |
| `tofu_state_node` | **新建** | cuttofo_lbot | 🆕 | 豆腐状态持续发布 → /tofu_state |
| `knife_prepare_action_server` | **新建** | cuttofo_lbot | 🆕 | 刀预备位 Action Server（通过 LbotArmAdapter 控制机械臂） |
| `tofu_cut_coordinator_node` | **新建** | cuttofo_lbot | 🆕 | 整体状态机协调（通过 LbotArmAdapter 控制机械臂） |
| `LbotArmAdapter` | **新建** | cuttofo_lbot | 🆕 | Lbot 机械臂控制适配器（封装 LbotRobot Python API） |

**说明**：与 xCore 版本不同，Lbot 版本不使用 `xcore_controller_node` 的 ROS Service。机械臂控制通过 `LbotArmAdapter` 直接调用 Lbot Python API（`LbotRobot`），连接方式为 TCP 直连（IP 默认 `192.168.10.21`）。

### 3.2 话题/服务/Action 通信图

```
RealSense D435i
  ├── /camera/color/image_raw ──▶ sam3_detector_node ──▶ /detected_objects
  ├── /camera/depth/image_raw ─┐                              │
  └── /camera/color/camera_info ┘─▶ pose_estimator_node ──▶ /objects_with_pose
                                                                    │
                                                            tofu_state_node
                                                          (10Hz 持续发布)
                                                                    │
                                                             /tofu_state
                                                          (TofuState 自定义消息)
                                                                  │
                              ┌────────────────────────────────────┤
                              │                                    │
                 knife_prepare_action_server             tofu_cut_coordinator_node
                 Action: /move_to_prepare_pose            (状态机编排)
                 订阅: /tofu_state                        订阅: /knife_grabbed
                 订阅: /joint_states                             /tofu_rotated
                 发布: /joint_states_remapped                   /tofu_state
                              │                           调用 Action: /move_to_prepare_pose
                              │
                              ▼
                    ┌─────────────────────┐
                    │   LbotArmAdapter     │
                    │   (封装 LbotRobot)   │
                    │ TCP连接 192.168.10.21│
                    └─────────┬───────────┘
                              │ move_to_joint_target()
                              │ get_joint_positions()
                              │ get_cartesian_pose()
                              ▼
                    Lbot 机械臂 (LKRS73-I2)

                ── 外部信号 ──────────────────────────────────────
                /knife_grabbed (Bool)  ← 外部发布: 刀已拿好
                /tofu_rotated (Bool)   ← 外部发布: 豆腐旋转完毕
                /cutting_done (Bool)   ← 外部发布: 切削完成 (Phase 3结束)
```

---

## 4. 消息/Action/Service 定义

### 4.1 新增消息: TofuState.msg

```
# TofuState.msg - 豆腐状态（持续性话题，每帧发布）
# 文件位置: cuttofo_lbot/msg/TofuState.msg

std_msgs/Header header

# 基础位姿（来自 /objects_with_pose）
geometry_msgs/Pose pose             # 豆腐中心在 base 坐标系下的 6D 位姿
float32[3] extents                  # 豆腐 3D 尺寸 [extX, extY, extZ]（全尺寸，单位 m）
float32 confidence                  # 检测置信度

# 预计算的顶面几何
geometry_msgs/Point[] top_corners   # 顶面4顶点（base坐标系，Y最大，按Z排序）
geometry_msgs/Vector3 edge_dir     # 豆腐左边方向向量（归一化，Y=0）
geometry_msgs/Point tcp_target      # 预计算的 TCP 目标点（base坐标系）
float32 top_y                       # 豆腐顶面 Y 坐标

# 状态标记
bool is_valid                       # 当前帧检测是否有效
uint32 object_id                    # 物体 ID
```

**设计说明**：
- `top_corners`: 由 `pose + quaternion + extents → 重建8角点 → 取Y最大4个` 得到
- `edge_dir`: 由 `top_corners → A,B → v → cross(v,[0,1,0]) → 归一化 → Y强制为0` 得到
- `tcp_target`: 由 `top_corners + offset_a + vertical_offset → 7步几何算法` 得到
- 消费端无需重复计算，直接使用 `tcp_target` 和 `edge_dir` 即可

### 4.2 新增 Action: MoveToPreparePose.action

```
# MoveToPreparePose.action - 移动刀到预备位
# 文件位置: cuttofo_lbot/action/MoveToPreparePose.action

# Goal
float64 plane_angle_deg                   # 刀面倾斜角（默认 40°）
bool use_vision                            # True: 从 /tofu_state 获取目标; False: 手动目标
geometry_msgs/Pose manual_target_pose     # 手动目标（use_vision=false 时用）
float64 offset_a                           # 水平偏移量（覆盖 tofu_state 的值，默认 0.03m）
float64 vertical_offset                    # 垂直偏移量（覆盖 tofu_state 的值，默认 0.03m）
bool edge_align                            # 是否使用边对齐约束（默认 false）
float64 timeout_s                          # 等待有效豆腐状态超时（默认 5.0s）
---
# Result
bool success
geometry_msgs/Pose reached_tcp_pose        # 实际到达的 TCP 位姿
float64[] reached_joints                    # 到达的关节角 (7个, rad)
float64 position_error_mm                  # 位置误差 (mm)
string message
---
# Feedback
string current_phase                        # "waiting_tofu"/"computing_ik"/"moving"/"verifying"
float32 progress                            # 进度 0.0 ~ 1.0
float64 position_error_mm                   # 当前位置误差
float64[] current_joints                    # 当前关节角
```

### 4.3 已有接口（复用）

| 接口 | 类型 | 消息 | 说明 |
|------|------|------|------|
| `/objects_with_pose` | Topic | ObjectStateArray | 感知管线输出 |
| `/joint_states` | Topic | JointState | 机械臂关节角（RViz 显示用） |
| `/joint_states_remapped` | Topic | JointState | RViz 双臂显示 |
| `/knife_grabbed` | Topic | Bool | 外部发布：刀已拿好 |
| `/tofu_rotated` | Topic | Bool | 外部发布：豆腐旋转完毕 |
| `/cutting_done` | Topic | Bool | 外部发布：切削完成（可选） |
| `LbotArmAdapter` | Python API | — | 封装 LbotRobot TCP 连接，提供 `move_to_joints()`、`get_joints()`、`get_pose()` |

**与 xCore 版本的关键区别**：
- 不再使用 `/arm_r/robot/move_rt_cartesian_segment` Service（xCore RT 实时控制）
- 不再使用 `/arm_r/robot/get_state` Service
- 机械臂控制改为 `LbotArmAdapter` 直接调用 LbotPython API
- 新增可选的 `/cutting_done` 话题（Phase 3 完成的信号）

---

## 5. 各节点详细设计

### 5.1 tofu_state_node（豆腐状态节点）

**职责**: 持续监听视觉感知管线，提取豆腐目标，预计算顶面几何和 TCP 目标点，以固定频率发布。

**订阅**:
- `/objects_with_pose` (ObjectStateArray) — 感知管线输出

**发布**:
- `/tofu_state` (TofuState) — 10Hz 持续发布

**参数**:

| 参数 | 默认值 | 类型 | 说明 |
|------|--------|------|------|
| `class_filter` | `"tofu"` | string | 过滤的目标类别 |
| `offset_a` | `0.03` | double | 水平偏移（m） |
| `vertical_offset` | `0.03` | double | 垂直偏移（m） |
| `publish_rate` | `10.0` | double | 发布频率 (Hz) |
| `smoothing_alpha` | `0.4` | double | EMA 平滑系数（0=全平滑, 1=无平滑） |
| `valid_timeout` | `2.0` | double | 检测超时标记无效 (s) |

**说明**: 本节点与 xCore 版本完全一致，不涉及机械臂控制。因为：
- 感知管线（RealSense → SAM3 → PoseEstimator）是通用的
- TofuState 消息格式不变
- 豆腐信息的计算逻辑不受机械臂类型影响

**核心逻辑**:

```python
class TofuStateNode(Node):
    def __init__(self):
        self._subscription = self.create_subscription(
            ObjectStateArray, "/objects_with_pose", self._on_objects, 10)
        self._publisher = self.create_publisher(TofuState, "/tofu_state", 10)
        self._timer = self.create_timer(1.0 / publish_rate, self._publish_timer)
        self._latest_state = None       # 最新 TofuState
        self._last_update_time = 0.0    # 最后更新时间
        self._smoothed_data = {}         # EMA 平滑缓存

    def _on_objects(self, msg: ObjectStateArray):
        # 1. 过滤 class_id == class_filter 的目标
        # 2. 取第一个匹配目标
        # 3. 重建 8 角点: pose + quaternion + extents → corners_8
        # 4. 取 Y 最大的 4 个 = top_corners
        # 5. 计算 edge_dir: normalize(v), Y=0
        # 6. 计算 tcp_target: compute_tcp_target_from_corners(top_corners, offset_a, vertical_offset)
        # 7. EMA 平滑 (position, quaternion, extents, tcp_target)
        # 8. 保存到 self._latest_state

    def _publish_timer(self):
        # 构造 TofuState 消息
        # 若 self._latest_state 非空且未超时: is_valid = True
        # 若超时: is_valid = False
        # 发布
```

**关键计算函数**（复用 prepare_pose_selector.py 中已有算法）:

```python
def compute_tcp_target_from_corners(corners_4, offset_a, vertical_offset):
    """7步几何算法: 顶面4顶点 → TCP目标点"""
    # Step 1: top_y = mean(corners_4[:, 1])
    # Step 2: A, B = Z最小的2个顶点
    # Step 3: v = 从后指向前 (A→B or B→A, 取 X+侧)
    # Step 4: l = normalize(cross(v, [0,1,0])), Z+侧
    # Step 5: D = (A + B) / 2
    # Step 6: D_prime = D + offset_a * l
    # Step 7: tcp_target = [D_prime[0], top_y + vertical_offset, D_prime[2]]
    return tcp_target

def reconstruct_corners(pos, quat, extents):
    """pose + quaternion + extents → 8角点（base坐标系）"""
    half = np.array(extents) / 2.0
    corners_local = ...  # 8个 ±half 组合
    R = Rotation.from_quat(quat).as_matrix()
    return corners_local @ R.T + pos

def compute_edge_dir(corners_4):
    """顶面4顶点 → 左边方向向量（归一化，Y=0）"""
    # A, B = Z最小2个顶点
    # v = A→B (从后到前)
    # edge_dir = normalize([v_x, 0, v_z])
    return edge_dir
```

### 5.2 knife_prepare_action_server（刀预备位 Action 服务器）

**本节点是整个 Phase 2 的核心。** 负责接收 Action Goal，从 /tofu_state 获取目标（或手动目标），使用**纯数学计算**构造刀姿态，然后通过 **Lbot 内置 IK** 求解关节角，最后驱动 Lbot 机械臂到达预备切割位。

#### 关键设计原则

```
约束不通过 IK 求解器执行，而是在 IK 求解之前通过纯数学计算编码到目标 euler 角中
```

```
1. tofu_state.tcp_target → target_pos (米, 3D位置)
2. build_rotation(plane_angle, edge_dir) → target_R (3×3旋转矩阵)
3. Rotation.as_euler('xyz') → target_eul (弧度, 3个欧拉角)
   ↓ 此时 target_pos + target_eul 已经完整编码了"刀脊方向+刀面倾斜"约束
   ↓
4. Lbot IK 只做一件事: "给定完整6D位姿, 求关节角"
   Lbot 内置 IK 不需要知道任何约束, 它只需要到达这个目标位姿
```

#### 详细执行步骤

```
Step 1: 连接 Lbot 控制器
        robot = LbotRobot(host)
        robot.connect()
        → 若连接失败 → 直接返回 Result.fail

Step 2: 等待有效豆腐状态 (use_vision=True)
        订阅 /tofu_state, 等待 is_valid=True 且 tcp_target 非空
        → 超时 → 返回 Result.fail (message: "No tofu detected")
        → 获取 tcp_target (3D位置), edge_dir (边方向)

Step 3: 构建目标姿态
        target_pos = tofu_state.tcp_target

        if edge_align:
            R = build_rotation_with_edge_dir(plane_angle_deg, tofu_state.edge_dir)
        else:
            R = build_target_rotation_from_constraints(plane_angle_deg)

        target_eul = Rotation.from_matrix(R).as_euler('xyz')

Step 4: IK 求解 (Lbot 内置 IK)
        # 种子1: 当前关节角
        seed = robot.get_joint_positions(arm)
        joints = robot.compute_inverse_kinematics(arm, pos, eul, seed)

        # 若失败: 随机种子重试 × N 次
        if joints is None:
            for seed_k in random_seeds(count=20):
                joints = robot.compute_inverse_kinematics(arm, pos, eul, seed_k)
                if joints is not None: break

        # 若仍然失败 → 返回 Result.fail (message: "IK no solution")

Step 5: FK 验证 (可选, 校验 IK 结果)
        若需要, 调用 robot.compute_forward_kinematics(arm, joints)
        对比实际位姿与目标位姿, 确认误差 < 阈值
        → 误差过大 → 记录警告, 仍可使用此解

Step 6: 驱动机械臂
        robot.move_to_joint_target(arm, joints, speed=0.3, block=True)
        → block=True 意味着 Lbot 会阻塞直到运动完成

Step 7: 到位确认 (轮询验证)
        current = robot.get_joint_positions(arm)
        error_deg = max(|current - target_joints|) * 180/π

        if error_deg < tolerance:
            → 成功
        else:
            → 超时重试后仍失败 → 返回 Result.fail

Step 8: 返回 Result
        result.success = True
        result.reached_joints = joints
        result.reached_tcp_pose = (target_pos.x, target_pos.y, target_pos.z,
                                   target_eul.x, target_eul.y, target_eul.z)
        result.position_error_mm = error * 1000
```

#### 核心逻辑 (伪码)

```python
from cuttofo_lbot.lbot_arm_adapter import LbotArmAdapter

class KnifePrepareActionServer(Node):
    def __init__(self):
        self._action_server = ActionServer(
            self, MoveToPreparePose, "/move_to_prepare_pose",
            self.execute_callback)

    def execute_callback(self, goal_handle):
        # 初始化 Lbot 适配器 (每个 Goal 建立连接)
        arm = LbotArmAdapter(host=goal_handle.arm_host or "192.168.10.21")
        if not arm.connect():
            goal_handle.abort("Lbot connection failed")
            return

        try:
            # --- Step 2: 等待豆腐状态 ---
            if goal_handle.use_vision:
                tofu = self._wait_for_tofu_state(goal_handle.timeout_s)
                target_pos = tofu.tcp_target
                edge_dir = tofu.edge_dir if goal_handle.edge_align else None
            else:
                p = goal_handle.manual_target_pose.position
                target_pos = [p.x, p.y, p.z]
                edge_dir = None

            # --- Step 3: 构建目标姿态 ---
            target_R = build_target_rotation(
                goal_handle.plane_angle_deg, edge_dir)
            target_eul = Rotation.from_matrix(target_R).as_euler('xyz')

            # --- Step 4: IK 求解 ---
            joints = arm.solve_ik(
                target_pos, target_eul, num_retries=20)
            if joints is None:
                goal_handle.abort("IK no solution")
                return

            # --- Step 5: (可选) FK 验证 ---
            actual_pos, actual_eul = arm.compute_fk(joints)
            # 计算误差, 记录日志

            # --- Step 6: 驱动机械臂 ---
            feedback.current_phase = "moving"
            arm.move_to_joints(joints, speed=0.3, block=True)

            # --- Step 7: 到位确认 ---
            feedback.current_phase = "verifying"
            arrived, error_deg = arm.verify_arrival(
                joints, tolerance_deg=2.0)
            if not arrived:
                goal_handle.abort(f"Arrival timeout, error={error_deg:.2f}°")
                return

            # --- Step 8: 返回结果 ---
            result.success = True
            result.reached_joints = joints.tolist()
            goal_handle.succeed(result)

        finally:
            arm.disconnect()
```

#### 订阅/发布/Action

| 类型 | 接口 | 说明 |
|------|------|------|
| 订阅 | `/tofu_state` (TofuState) | 豆腐状态 (tcp_target, edge_dir, is_valid) |
| Action | `/move_to_prepare_pose` (MoveToPreparePose) | 接收 Goal, 返回 Result |
| 内部依赖 | `LbotArmAdapter.solve_ik()` | Lbot 内置 IK, 多种子重试 |
| 内部依赖 | `tofu_geometry.build_rotation()` | 纯数学约束计算 |

#### 参数

| 参数 | 默认值 | 类型 | 说明 |
|------|--------|------|------|
| `arm_host` | `"192.168.10.21"` | string | Lbot 控制器 IP |
| `arm_type` | `"right"` | string | left / right |
| `ik_retry_count` | `20` | int | IK 随机种子重试次数 |
| `arrival_tolerance_deg` | `2.0` | double | 到位容差（每关节 °） |
| `arrival_timeout_s` | `10.0` | double | 到位超时 (s) |
| `joint_speed` | `0.3` | double | 关节运动速度 |
| `joint_accel` | `0.5` | double | 关节运动加速度 |
| `fk_verify` | `False` | bool | 是否启用 FK 验证 |

#### 与 xCore 版本的关键区别

| 方面 | xCore 版本 | Lbot 版本 |
|------|-----------|----------|
| IK 求解器 | 离线 URDF FK + scipy least_squares, 240 候选 | **Lbot 内置 IK** (黑盒) |
| 多候选评分 | 240 候选 + preview 评分 + 排序 | 20 种子的随机重试, 取第一个有效解 |
| Preview 评分 | 模拟下切轨迹评测候选质量 | **不需要** (切削由外部负责) |
| URDF 依赖 | 需要 urdf 文件 + OfflineURDFKinematics | **不需要** (IK 求解在 Lbot 控制器内部完成) |
| 关节限位检查 | 脚本硬编码 ±15° 安全余量 | Lbot 控制器内置限位检查 |
| FK 验证 | `OfflineURDFKinematics.fk_matrix()` | `LbotRobot.compute_forward_kinematics()` |

### 5.3 tofu_cut_coordinator_node（协调节点，仅 Phase 2 相关）

**注意**: 本节只描述 *与 Phase 2 直接相关的* 状态机部分。Phase 3-6 仅做占位，未来由其他模块补全。

**职责**: 收到 `/knife_grabbed` 信号后，发送 Action Goal 到 `/move_to_prepare_pose`，等待机械臂就位。

**订阅**:
- `/knife_grabbed` (Bool) — 刀已拿好信号

**Action Client**:
- `/move_to_prepare_pose` (MoveToPreparePose) — 移刀到预备位

**参数** (仅 Phase 2 相关):

| 参数 | 默认值 | 类型 | 说明 |
|------|--------|------|------|
| `plane_angle_deg` | `40.0` | double | 刀面倾斜角 |
| `edge_align` | `false` | bool | 是否使用边对齐 |
| `offset_a` | `0.03` | double | 水平偏移 |
| `vertical_offset` | `0.03` | double | 垂直偏移 |
| `knife_grabbed_timeout` | `300.0` | double | 等待拿刀信号超时 (s) |

**核心逻辑**:

```python
class TofuCutCoordinator(Node):
    def __init__(self):
        self._action_client = ActionClient(
            self, MoveToPreparePose, "/move_to_prepare_pose")
        self.state = "IDLE"

    def run_phase_2(self):
        """Phase 2 完整的生命周期"""
        # 等待拿刀
        self._wait_for_knife_grabbed(timeout=knife_grabbed_timeout)
        if not knife_grabbed:
            self.state = "ERROR"
            return

        # 发送 Action Goal 移刀到预备位
        goal = MoveToPreparePose.Goal()
        goal.use_vision = True
        goal.plane_angle_deg = self.plane_angle_deg
        goal.edge_align = self.edge_align
        goal.offset_a = self.offset_a
        goal.vertical_offset = self.vertical_offset

        future = self._action_client.send_goal_async(goal)
        result = self._wait_for_action_result(future)

        if result.success:
            self.state = "PREPARE_DONE"
        else:
            self.state = "ERROR"
```

---

## 6. 数据流详解

### 6.1 Phase 2 数据流（移刀到预备位）

```
RealSense → sam3 → /detected_objects
                              │
                     pose_estimator_node
                              │
                      /objects_with_pose (ObjectStateArray)
                              │
                   tofu_state_node (10Hz 持续发布)
                   ┌────────────────────────┐
                   │ 重建8角点               │  (纯数学, 与机械臂无关)
                   │ 取Y最大4顶点=top_corners │
                   │ 计算edge_dir             │
                   │ 计算tcp_target           │
                   │ EMA平滑                  │
                   └────────────────────────┘
                              │
                       /tofu_state (TofuState)
                        │           │
                        ▼           ▼
                  tcp_target   edge_dir
                   (3D位置)    (边方向)
                        │           │
                        ▼           ▼
              ┌─── 纯数学计算 ─────────────────┐
              │ build_rotation(plane_angle,    │
              │   edge_dir) → 3×3旋转矩阵      │
              │ Rotation.as_euler('xyz')       │
              │ → target_eul (rx, ry, rz)     │
              └──────────────┬────────────────┘
                             │
                             ▼
                   target_pos + target_eul
                     (完整 6D 位姿, 约束已编码其中)
                             │
                             ▼
              knife_prepare_action_server
              ┌────────────────────────────────────┐
              │ LbotArmAdapter.solve_ik()           │
              │  ├─ seed=当前关节角                  │
              │  ├─ robot.compute_inverse_           │
              │  │   kinematics(pos, eul, seed)     │
              │  ├─ 失败? 随机种子×20重试            │
              │  └─ → joints (7个关节角)            │
              │                                     │
              │ LbotArmAdapter.move_to_joints()      │
              │  ├─ robot.move_to_joint_target()    │
              │  └─ block=True (阻塞到运动完成)      │
              │                                     │
              │ LbotArmAdapter.verify_arrival()      │
              │  ├─ get_joint_positions()           │
              │  └─ 对比 target_joints (误差<2°)    │
              └────────────────────────────────────┘
                              │
                              ▼
              Lbot 机械臂到达预备位
                TCP 位置 = 豆腐顶面上方 3cm
                TCP 姿态 = tcp_y∥base_x (或边对齐)
                            tcp_z 与 XZ 平面夹角 = plane_angle°

### 6.2 Phase 3 数据流（切豆腐）

```
                    ┌────────────────────────────┐
                    │ tofu_cut_coordinator_node   │
                    │ state = "CUTTING"           │
                    │                            │
                    │ 1. 发布 /cutting_start      │
                    │ 2. 等待 /cutting_done       │
                    │    (或超时)                  │
                    └────────────────────────────┘
                              │
                              ▼
             ┌─ 外部切削脚本 ───────────────────┐
             │ (由其他代码实现，不在本包范围内)    │
             │                                  │
             │ 可能的实现方式:                   │
             │ - 独立 ROS 节点                   │
             │ - 独立 Python 脚本                │
             │ - 复用 demo_cut_tofu*.py 逻辑     │
             └──────────────────────────────────┘
                              │
                              ▼
                     Lbot 完成 N 刀切削
                        发布 /cutting_done
```

### 6.3 Phase 5 数据流（旋转后重新就位）

```
/tofu_rotated = True
         │
         ▼
tofu_state_node 检测到豆腐位置/姿态变化 → 更新 /tofu_state
         │
         ▼
coordinator 发现 /tofu_rotated=True, 切换到 REPOSITIONING
         │
         ▼
coordinator 发送 Action Goal: /move_to_prepare_pose (use_vision=True)
         │
         ▼
knife_prepare_action_server 从 /tofu_state 获取新 tcp_target + edge_dir
         │
         ▼
IK求解 → Lbot 机械臂移动到新的预备位

---

## 7. 关键算法复用关系

### 7.1 已有算法 → 新模块映射

| 算法 | 来源 | 目标模块 | 说明 |
|------|------|----------|------|
| 双约束旋转矩阵 | `prepare_pose_selector.py:build_target_rotation_from_constraints()` | `tofu_geometry.py` | **纯数学**, 与机械臂无关 |
| 边对齐广义旋转矩阵 | `prepare_pose_selector.py` 中的广义公式 (e_x, e_z) | `tofu_geometry.py` | **纯数学**, 与机械臂无关 |
| TCP 目标几何 (7步) | `prepare_pose_selector.py:compute_tcp_target_from_corners()` | `tofu_geometry.py` | **纯数学**, 与机械臂无关 |
| OBB 8 角点重建 | `prepare_pose_selector.py:_reconstruct_corners()` | `tofu_geometry.py` | **纯数学**, 与机械臂无关 |
| 边方向计算 | `prepare_pose_selector.py:compute_edge_dir()` | `tofu_geometry.py` | **纯数学**, 与机械臂无关 |
| IK 求解 | scipy least_squares (离线) | **Lbot 内置 IK** (`robot.compute_inverse_kinematics()`) | **不再需要** URDF/scipy |
| Preview 评分 | `prepare_pose_selector.py:score_candidate()` | **不需要** | 切削由外部负责, 无需 preview |
| 离线 FK | `OfflineURDFKinematics` | **Lbot 内置 FK** (`robot.compute_forward_kinematics()`) | **不再需要** URDF |
| Lbot 控制 | 新建 | `lbot_arm_adapter.py` | 封装 LbotRobot + IK/FK |
| 约束→euler | 新建 | `tofu_geometry.py:build_target_euler()` | 旋转矩阵→euler 转换 (纯数学) |

### 7.2 新建代码文件结构

```
cuttofo_lbot/
├── msg/
│   └── TofuState.msg                    # 新增消息定义
├── action/
│   └── MoveToPreparePose.action          # 新增Action定义
│
├── cuttofo_lbot/
│   ├── tofu_geometry.py                  # 从 prepare_pose_selector.py 抽取
│   │   ├── reconstruct_corners()        #   (纯数学, 与机械臂无关)
│   │   ├── compute_tcp_target_from_corners()
│   │   ├── compute_edge_dir()
│   │   ├── build_target_rotation_from_constraints()
│   │   ├── build_rotation_with_edge_dir()
│   │   └── target_R_to_euler()          # 旋转矩阵 → euler 角
│   │
│   ├── lbot_arm_adapter.py              # 新建: Lbot 控制适配器
│   │   ├── connect() / disconnect()
│   │   ├── solve_ik()                   # 多种子 Lbot 内置 IK
│   │   ├── compute_fk()                 # Lbot 内置 FK
│   │   ├── move_to_joints()             # 关节空间运动
│   │   ├── get_joints() / get_pose()    # 状态查询
│   │   └── verify_arrival()             # 轮询到位确认
│   │
│   ├── tofu_state_node.py               # 新建: 豆腐状态持续发布
│   ├── knife_prepare_action_server.py    # 新建: 刀预备位 Action
│   ├── tofu_cut_coordinator_node.py      # 新建: Phase 2 状态机协调
│   │
│   ├── lbot_tool/                        # 保留 (Lbot 调试GUI)
│   ├── prepare_pose_selector.py          # 保留: 离线调试工具 (但不用于 Lbot IK)
│   └── demo_adjust_knife_pose_xcore.py   # 保留: 参考逻辑
│
│   └── [待删除] ——
│       ├── demo_cut_tofu_xcore_ros.py    # ❌ xCore 专用
│       ├── demo_cut_tofu_xcore.py        # ❌ xCore 专用
│       ├── demo_cut_tofu.py              # ❌ xCore 专用
│       ├── demo_cut_smooth_pro6.py       # ❌ (Phase 3 参考, 但 xCore 逻辑)
│       ├── offline_urdf_kinematics.py    # ❌ Lbot 内置 IK 替代
│       └── demo_offline_ik_to_rviz.py    # ❌ xCore 专用
```

**不再需要的模块**:
- `offline_urdf_kinematics.py` — Lbot 内置 IK 无需 URDF FK
- `ik_utils.py` — 不再使用 scipy least_squares 做 IK, 改用 `LbotArmAdapter.solve_ik()`
- `demo_offline_ik_to_rviz.py` — 不再需要离线 IK + RViz 预览

### 7.3 新增模块: lbot_arm_adapter.py 详细设计

```python
"""
LbotArmAdapter - Lbot 机械臂控制适配器

封装 LbotRobot Python API，提供给 ROS2 节点使用。
所有机械臂控制操作都通过此适配器完成，不直接调用 Lbot 原生 API。
"""

from lbot.lbot_robot import LbotRobot
from lbot.lbot_api import LbotArm, LbotPosition, LbotEuler
import numpy as np
import time


class LbotArmAdapter:
    def __init__(self, host="192.168.10.21"):
        self.robot = LbotRobot(host)
        self.arm = LbotArm.RIGHT_ARM
        self._connected = False

    def connect(self) -> bool:
        """连接 Lbot 控制器, 返回是否成功"""
        success = self.robot.connect()
        self._connected = success
        return success

    def disconnect(self):
        """断开连接"""
        self.robot.disconnect()
        self._connected = False

    # ---- IK 求解 (Phase 2 核心) ----

    def solve_ik(self, target_pos, target_eul,
                 seed_joints=None, num_retries=20) -> Optional[np.ndarray]:
        """
        调用 Lbot 内置 IK 求解关节角。

        参数:
            target_pos: [x, y, z] 目标位置 (米)
            target_eul: [rx, ry, rz] 目标欧拉角 (弧度)
            seed_joints: 初始关节角 (弧度, 7个), None 则使用当前关节角
            num_retries: 失败后随机种子重试次数

        返回:
            7 关节角 (rad) numpy array, 或 None (求解失败)
        """
        pos = LbotPosition(*target_pos)
        eul = LbotEuler(*target_eul)

        # 种子1: 使用指定种子或当前关节角
        if seed_joints is None:
            seed_joints = self.robot.get_joint_positions(self.arm)
        joints = self.robot.compute_inverse_kinematics(
            self.arm, pos, eul, list(seed_joints))

        if joints is not None:
            return np.array(joints)

        # 多次随机种子重试
        joint_limits = np.deg2rad(np.array([
            [-170, 170]] * 7))  # Lbot 关节限位
        for _ in range(num_retries):
            random_seed = np.random.uniform(
                joint_limits[:, 0], joint_limits[:, 1])
            joints = self.robot.compute_inverse_kinematics(
                self.arm, pos, eul, list(random_seed))
            if joints is not None:
                return np.array(joints)

        return None

    def compute_fk(self, joints) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """
        调用 Lbot 内置 FK 求解位姿。

        参数:
            joints: 7 关节角 (弧度)

        返回:
            (position: (x, y, z), euler: (rx, ry, rz))
        """
        result = self.robot.compute_forward_kinematics(
            self.arm, list(joints))
        if result is None:
            return None, None
        pos, eul = result
        return (pos.x, pos.y, pos.z), (eul.x, eul.y, eul.z)

    # ---- 运动控制 ----

    def move_to_joints(self, target_joints, speed=0.3, accel=0.5, block=True):
        """关节空间运动"""
        return self.robot.move_to_joint_target(
            self.arm, list(target_joints), speed, accel, block)

    # ---- 状态查询 ----

    def get_joints(self) -> np.ndarray:
        """获取当前 7 关节角 (rad)"""
        return np.array(self.robot.get_joint_positions(self.arm))

    def get_pose(self) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """获取当前笛卡尔位姿"""
        return self.compute_fk(self.get_joints())

    def verify_arrival(self, target_joints, tolerance_deg=2.0,
                       timeout_s=10.0) -> Tuple[bool, float]:
        """
        轮询关节角，确认已到达目标位。

        返回:
            (arrived: bool, max_error_deg: float)
        """
        start = time.time()
        while time.time() - start < timeout_s:
            current = self.get_joints()
            error_rad = np.max(np.abs(current - target_joints))
            error_deg = np.rad2deg(error_rad)
            if error_deg < tolerance_deg:
                return True, error_deg
            time.sleep(0.1)
        return False, error_deg
```

**设计说明**:
- `solve_ik()` 内置多种子重试机制，与 xCore 版本的 240 候选功能等价
- `compute_fk()` 封装 Lbot 内置 FK，用于校验 IK 结果
- `verify_arrival()` 封装到位轮询，避免 `move_to_joint_target(block=True)` 已返回但关节角偏差仍大的情况
- 所有关节角均为 7 元素 numpy array (弧度)，与 Lbot Python API 兼容

---

## 8. 启动与运行

### 8.1 完整系统启动顺序

```bash
# Step 1: 启动感知管线（通用）
ros2 launch ar5_dual_arm_bringup dual_display.launch.py \
  use_joint_gui:=false enable_realsense:=true enable_aruco:=false

# Step 2: 启动 SAM3 检测 (指定豆腐)
ros2 run dexbot_middle_layer sam3_detector_node --ros-args \
  -p text_prompt:=豆腐

# Step 3: 启动姿态估计
ros2 run dexbot_middle_layer pose_estimator_node --ros-args \
  -p calibration_file:=/home/tbl/Project/tofu/dexbot_ros2_ws/src/config/calibration_result.yaml

# Step 4: 启动豆腐状态节点（cuttofo_lbot 包）
ros2 run cuttofo_lbot tofu_state_node --ros-args \
  -p class_filter:=tofu \
  -p offset_a:=0.03 \
  -p vertical_offset:=0.03

# Step 5: 启动刀预备位 Action 服务器（连 Lbot）
ros2 run cuttofo_lbot knife_prepare_action_server --ros-args \
  -p arm_host:=192.168.10.21 \
  -p candidate_count:=240 \
  -p preview_steps:=15

# Step 6: 启动协调节点
ros2 run cuttofo_lbot tofu_cut_coordinator_node --ros-args \
  -p plane_angle_deg:=40.0

# Step 7: 确认 Lbot 机械臂已上电、TCP 可达
ping 192.168.10.21

# Step 8: 机械臂拿刀 (外部操作)
# ... 人或外部脚本控制 ...

# Step 9: 发送拿刀完成信号
ros2 topic pub --once /knife_grabbed std_msgs/msg/Bool '{data: true}'

# 切削完成后，发送旋转完成信号
ros2 topic pub --once /tofu_rotated std_msgs/msg/Bool '{data: true}'
```

### 8.2 调试模式（不连真实机械臂，RViz预览）

```bash
# 离线调试：手动指定目标位（不连 Lbot）
python3 src/cuttofo_lbot/cuttofo_lbot/prepare_pose_selector.py \
  --x 0.25 --y 0.0 --z 0.25 \
  --plane-angle-deg 40 \
  --publish-topic /joint_states_remapped

# ROS 视觉输入调试（不连 Lbot）
python3 src/cuttofo_lbot/cuttofo_lbot/prepare_pose_selector.py \
  --ros-input --ros-input-class tofu \
  --plane-angle-deg 40 \
  --publish-topic /joint_states_remapped

# 边对齐约束调试（不连 Lbot）
python3 src/cuttofo_lbot/cuttofo_lbot/prepare_pose_selector.py \
  --ros-input --ros-input-class tofu \
  --edge-align --plane-angle-deg 40 \
  --publish-topic /joint_states_remapped

# Lbot 连接测试
python3 -c "
from cuttofo_lbot.lbot_arm_adapter import LbotArmAdapter
adapter = LbotArmAdapter('192.168.10.21')
adapter.connect()
print('Joints:', adapter.get_joints())
adapter.disconnect()
"
```

---

## 9. 与现有代码的关系

### 9.1 现有脚本 → 新模块映射

| 现有脚本 | 功能 | 处理方式 |
|---------|------|---------|
| `prepare_pose_selector.py` | 离线IK+RViz预览 | **保留**为调试工具 |
| `demo_offline_ik_to_rviz.py` | 离线FK+IK | **保留**为调试工具 |
| `offline_urdf_kinematics.py` | URDF正运动学 | **保留**，共享模块 |
| `demo_adjust_knife_pose_xcore.py` | 刀姿态调整 | **保留**为参考 |
| `lbot_tool/` | Lbot调试GUI | **保留**（Lbot 原生工具，与本包互补） |
| `demo_cut_tofu_xcore_ros.py` | xCore RT切削 | **❌ 删除**（xCore专用） |
| `demo_cut_tofu_xcore.py` | xCore RT切削 | **❌ 删除**（xCore专用） |
| `demo_cut_tofu.py` | xCore RT切削 | **❌ 删除**（xCore专用） |
| `demo_cut_smooth_pro6.py` | xCore RT平滑 | **❌ 删除**（xCore专用） |

### 9.2 感知管线 → tofu_state_node 数据映射

| 感知管线输出 | 字段 | tofu_state_node 使用 |
|-------------|------|---------------------|
| `ObjectState.pose` | 6D位姿 | 重建8角点 → 4顶面顶点 |
| `ObjectState.geometric_features[5:8]` | extX, extY, extZ (全尺寸) | 重建8角点 |
| `ObjectState.class_id` | "tofu" | 过滤条件 |
| `ObjectState.confidence` | 置信度 | 直通 |
| `ObjectState.id` | 物体ID | 直通 |

### 9.3 关键参数适配

| 参数 | xCore 版本 | Lbot 版本 | 说明 |
|------|-----------|----------|------|
| 机械臂控制 | ROS Service | LbotArmAdapter Python API | 底层通信方式不同 |
| 关节限位 | URDF ±170° | config.py ±170° | 限位基本一致 |
| 关节数 | 7 DOF | 7 DOF | 相同 |
| URDF 来源 | ar5_07r_w4c1c1_description | **不需要 URDF** | Lbot 内置 IK 无需 URDF |
| 机械臂 IP | — | `192.168.10.21` | Lbot 控制器 IP |
| IK 求解 | OfflineURDFKinematics + scipy least_squares | **Lbot 内置 IK** (`robot.compute_inverse_kinematics()`) | 求解器完全不同 |
| IK 多候选 | 240 候选 + preview 评分 | 20 随机种子重试 (取首个有效解) | 多候选策略不同 |
| FK 验证 | OfflineURDFKinematics.fk_matrix() | `robot.compute_forward_kinematics()` | 验证接口不同 |
| 刀姿态约束 | 在 IK 求解器中通过旋转矩阵约束 | 约束编码到目标 euler 角中预计算 | 约束方式不同 |
| 关节安全余量 | 脚本硬编码 ±15° | Lbot 控制器内置限位检查 | 不再需要脚本级检查 |
| 几何算法 | tofu_geometry.py | 同左（复用） | 豆腐信息计算不变 |

---

## 10. 里程碑与优先级

### Phase 2 里程碑（当前聚焦）

| 阶段 | 内容 | 优先级 | 依赖 | 状态 |
|------|------|--------|------|------|
| **M0** | 包重命名：xcore→lbot（元数据+目录+内部引用） | P0 | 无 | ✅ 已完成 |
| **M1** | 定义 TofuState.msg + MoveToPreparePose.action | P0 | M0 | 📋 待实现 |
| **M2** | 实现 `tofu_geometry.py`（纯数学：约束→旋转矩阵→euler） | P0 | 无 | 📋 待实现 |
| **M3** | 实现 `lbot_arm_adapter.py`（含 solve_ik / compute_fk / verify_arrival） | P0 | 无 | 📋 待实现 |
| **M4** | 实现 `tofu_state_node`（订阅 /objects_with_pose → 发布 /tofu_state） | P0 | M1 | 📋 待实现 |
| **M5** | 实现 `knife_prepare_action_server`（Action + Lbot IK + 驱动到位） | P0 | M2, M3, M4 | 📋 待实现 |
| **M5.1** | **Lbot IK 实测验证**：确认 euler 约定、IK 收敛性、FK 对比 | P0 | M3 | 📋 待实现 |
| **M6** | 实现 `tofu_cut_coordinator_node`（Phase 2 状态机） | P1 | M5 | 📋 待实现 |

### Phase 2 验收标准

| 检查项 | 验收标准 |
|--------|---------|
| Lbot IK 能否解出刀预备位 | IK 返回 7 个关节角 (非 None), FK 验证误差 < 1mm / 1° |
| 机械臂到达预备位 | 关节角误差 < 2°, block=True 后 verify_arrival 返回 True |
| 刀姿态约束满足 | tcp_y · base_x ≈ 1 (误差 < 0.05), plane_angle 误差 < 3° |
| 边对齐约束满足 | tcp_y · edge_dir ≈ 1 (误差 < 0.05) |
| Action 完整闭环 | coordinator 发 Goal → action_server IK → 驱动到位 → 返回 success |
| 感知→就位端到端 | RealSense → SAM3 → tofu_state → Action → 机械臂到达 |

### 后续里程碑（Phase 2 完成后）

| 阶段 | 内容 | 状态 |
|------|------|------|
| **M7** | 实现外部切削脚本 (参考 demo_cut_smooth_pro6.py, 删掉 WeightedIK) | 待规划 |
| **M8** | 实现 Phase 5 重新就位 (同 Phase 2 Action, 触发条件不同) | 待规划 |
| **M9** | 端到端完整测试 | 待规划 |
| **M10** | 删除 xCore 专用文件 | 待规划 |

---

## 11. 风险与待决事项

### Phase 2 核心风险

| 风险 | 说明 | 影响 | 缓解措施 |
|------|------|------|---------|
| Lbot 内置 IK 不收敛 | 特定目标位姿下 IK 无解 | Phase 2 失败 | 20 随机种子重试; 若全部失败则 Action 报错 |
| Lbot 内置 IK 多解问题 | 同一位姿对应多组关节角, IK 不一定选"最优"解 | 机械臂到达预备位但关节姿态不理想 | 若需要优选, 后续可用 WeightedIK 作后处理 |
| Lbot Euler 角约定 | Lbot 内置 IK 使用的欧拉角约定(内旋/外旋) 未知 | `as_euler('xyz')` 的约定与 Lbot 不匹配 → 目标姿态错误 | 必须实测验证: 用 FK 验证 IK 结果 |
| Lbot IK 种子敏感 | 同一目标位姿, 不同种子 → 不同解, 有的解超出关节限位 | IK 返回超限解 | Lbot 控制器内置限位检查, 但需确认其行为 |
| Lbot API Euler 方向 | `LbotEuler(rx, ry, rz)` 的各轴含义(内旋XYZ/外旋ZYX)未完全确认 | 目标姿态传入 IK 后结果偏差 | 必须实测: 用 FK 对比 IK 输入/输出 |
| 感知管线精度 | SAM3 + PCA 的检测精度影响 TCP 目标位置 | IK 可能求解到不合适的关节角 | tofu_state_node EMA 平滑 + 超时容错 |
| Lbot 连接稳定性 | TCP 连接可能断开 | Action Server 失去对机械臂的控制 | LbotArmAdapter 添加重连机制 |
| 手眼标定精度 | 重新标定后 T_base_cam 的精度直接影响 TCP 目标位置 | 所有后续计算产生系统性偏差 | 标定时确保 RMSE < 5mm |

---

## 12. 附录：核心几何算法速查

### 12.1 TCP目标点计算（7步）

```
输入: corners_4 (顶面4顶点, base坐标系), offset_a, vertical_offset

Step 1: top_y = mean(corners_4[:, 1])
Step 2: A, B = Z最小的2个顶点 (左边那条边)
Step 3: v = 从后指向前 (确保 v.x > 0)
Step 4: l = normalize(cross(v, [0,1,0])), Z+侧
Step 5: D = (A + B) / 2
Step 6: D' = D + offset_a * l
Step 7: tcp_target = [D'.x, top_y + vertical_offset, D'.z]
```

### 12.2 边对齐旋转矩阵（广义公式）

```
输入: plane_angle=α, edge_dir=(e_x, 0, e_z)

tcp_y = edge_dir = [e_x, 0, e_z]
n = edge_dir × Y = [-e_z, 0, e_x]
tcp_z = cos(α)·n - sin(α)·Y = [-e_z·cos(α), -sin(α), e_x·cos(α)]
tcp_x = tcp_y × tcp_z = [e_z·sin(α), -cos(α), -e_x·sin(α)]

R = [tcp_x | tcp_y | tcp_z]
  = | e_z·sin(α)        e_x      -e_z·cos(α) |
    | -cos(α)           0        -sin(α)      |
    | -e_x·sin(α)       e_z       e_x·cos(α) |

退化: edge_dir=[1,0,0] → R = [[0,1,0],[-cos,-0,-sin],[0,0,0]] ... (e_z=0)
  即退化为默认约束 tcp_y = base_x
```

### 12.3 OBB 8角点重建

```
输入: pos (中心), quat (姿态四元数), extents (全尺寸 [extX, extY, extZ])

half = extents / 2
corners_local = [±half[0], ±half[1], ±half[2]] 的8种组合
R = Rotation.from_quat(quat).as_matrix()
corners_base = corners_local @ R.T + pos
top_corners = 取 Y 最大的4个（base坐标系下，Y 向上）
```