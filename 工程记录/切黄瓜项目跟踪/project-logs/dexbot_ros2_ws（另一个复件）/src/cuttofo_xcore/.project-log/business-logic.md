---
# OLD REFERENCE - Superseded by split files
# Content has been restructured into business-logic/ (graph.md, nodes.md, edges.md, main.md, constraints.md, open-questions.md)
# Keep this file as historical reference only
---

# 切豆腐项目 - 完整业务逻辑文档

> 创建日期: 2026-05-09
> 最后更新: 2026-05-16 (更新 Phase2 右侧 prepare 逻辑；更新 Phase3/5 三原子动作切割逻辑)

## 1. 系统总览

### 1.1 目标

实现"视觉引导切豆腐"全流程：从相机检测豆腐 → 计算刀预备位 → 机械臂移刀到预备位 → 执行切削 → 旋转豆腐 → 重新就位 → 循环切削。

### 1.2 坐标系约定

| 坐标系 | X+ | Y+ | Z+ | 说明 |
|--------|----|----|----|------|
| Base   | 前 | 上 | 右 | 机械臂基座坐标系 |
| 法兰(link7) | 前 | 上 | 右 | 与base一致（归零时） |
| URDF TCP(link_tcp) | 前 | 上 | 右 | 法兰 + [0, 0, 0.097]，**已废弃，不再作为 IK 目标** |
| 刀具 TCP | 前 | 上 | 右 | 法兰 + tcp_offset（标定值），姿态与法兰一致 |

**坐标系链路**:
```
base → joint_1~7 → link7(法兰) → [tcp_offset 纯平移] → 刀具TCP(刀刃中心)
```

**关键说明**:
- 刀具 TCP 坐标系与法兰坐标系**姿态完全一致**，仅原点不同
- `tcp_offset` 是法兰坐标系下的固定向量，表示法兰原点到刀刃中心的平移
- 标定前 `tcp_offset = [0, 0, 0]`，等效于 TCP = 法兰原点
- URDF 中的 `link_tcp`（法兰 + 97mm Z）不再用于 IK 目标，仅保留 URDF 兼容性

### 1.3 核心约束

| 约束 | 数学表达 | 说明 |
|------|---------|------|
| 刀脊方向(默认) | `tcp_Y · base_X = 1` | TCP Y轴与Base X同向（edge_align=false） |
| 刀脊方向(边对齐) | `tcp_Y · v = 1` | TCP Y轴沿豆腐右边棱边方向（edge_align=true） |
| 刀面倾斜 | `tcp_Z` 与 XZ平面夹角 = `plane_angle` | joint_6 ±40°安全限位 → max ≈ 40-45° |
| v 方向约束 | v 在 XZ 平面内，v · base_X+ > 0 | v 与 base_X+ 保持锐角 |
| l 方向约束 | l ⊥ v，l ∥ base XZ 平面，l · base_Z- > 0 | l 是 AB 的水平垂线，选择朝左的方向 |
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
                    │  Phase 2: 移刀到预备位  │◄──────────────────┐
                    │  Action: /move_to_prepare_pose             │ │
                    │  订阅 /tofu_state → 计算 TCP 目标           │ │
                    │  IK求解 → 发布关节角 → 驱动机械臂到达       │ │
                    └──────────┬──────────┘                       │
                               │ Action Result: success            │
                    ┌──────────▼──────────┐                       │
                    │  Phase 3: 切豆腐      │                       │
                    │  RT Service 循环切削   │                       │
                    │  (demo_cut_tofu_xcore_ros 逻辑)             │
                    └──────────┬──────────┘                       │
                               │ 切削完成 (N刀切完)                 │
                    ┌──────────▼──────────┐                       │
                    │  Phase 4: 回到Prepare位 │                       │
                    │  沿base Z反向回退累计step │                       │
                    └──────────┬──────────┘                       │
                               │ Return action success             │
                    ┌──────────▼──────────┐                       │
                    │  Phase 5: 第二次切割    ├──────────────────────┘
                    │  复用Phase3切割参数     │
                    │  切入→回刀→base Z平移   │
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
| 3→4 | Phase3切削循环完成 (N刀切完) | `/execute_knife_cut` 返回 success |
| 4→5 | Phase4回到Prepare成功 | `/execute_knife_cut` 返回 success |
| 5→DONE | Phase5第二次切割完成 | `/execute_knife_cut` 返回 success |

### 2.2 异常与容错

| 异常 | 处理 |
|------|------|
| 感知丢失(豆腐看不见) | 协调节点等待超时 → 状态机暂停 → 重试或报错 |
| IK 无解 | Action 返回 failed → 等待 tofu_state 更新重试 |
| 切削中途机械臂异常 | RT Service 返回 error → 协调节点中止 → 回安全位 |
| 旋转信号超时 | 协调节点超时 → 用户手动干预 |
| tofu_state 连续 N 帧无效 | Action 还未启动时继续等待; 已启动时使用最后一次有效值 |

---

## 3. ROS 节点架构

### 3.1 节点清单

| 节点名 | 类型 | 包 | 状态 | 说明 |
|--------|------|---|------|------|
| `sam3_detector_node` | 已有 | dexbot_middle_layer | ✅ | SAM3 分割 → /detected_objects |
| `pose_estimator_node` | 已有 | dexbot_middle_layer | ✅ | 6D姿态估计 → /objects_with_pose |
| `tofu_state_node` | **新建** | cuttofo_xcore | ✅ | 豆腐状态持续发布 → /tofu_state |
| `knife_prepare_action_server` | **新建** | cuttofo_xcore | ✅ | 刀预备位 Action Server (Phase2) |
| `knife_cut_action_server` | **新建** | cuttofo_xcore | ✅ | 切割 Action Server (Phase3/5); Action: /execute_knife_cut |
| `phase_manager_node` | **新建** | cuttofo_xcore | ✅ | 完整5相状态机协调 (Phase1→2→3→4→5→DONE) |
| `xcore_controller_node` | 已有 | dexbot_bottom_layer | ✅ | 机械臂低层控制 (RT Service) |

### 3.2 话题/服务/Action 通信图

```
RealSense D435i
  ├── /camera/color/image_raw ──▶ sam3_detector_node ──▶ /detected_objects
  ├── /camera/depth/image_raw ┐                              │
  └── /camera/color/camera_info ┘─▶ pose_estimator_node ──▶ /objects_with_pose
                                                                     │
                                                             tofu_state_node
                                                           (10Hz 持续发布)
                                                                     │
                                                              /tofu_state
                                                           (TofuState 自定义消息)
                                                                   │
                   ┌──────────────────────────────────────────────┤
                   │                                              │
       phase_manager_node                            knife_prepare_action_server
       (状态机编排)                                    Action: /move_to_prepare_pose (Phase2)
       订阅: /knife_grabbed                              订阅: /tofu_state
       订阅: /tofu_state                                  订阅: /joint_states
        订阅: /cutting_start                               发布: /joint_states_remapped
       订阅: /phase_jump
       发布: /phase_state
       发布: /phase_status
                   │                                     机械臂到达预备位
                   │
       knife_cut_action_server
       Action: /execute_knife_cut (Phase3/5)
       调用 Service: /arm_r/robot/move_rt_cartesian_path (RT阻抗优先，失败后RT位置)

           ── 外部信号 ──────────────────────────────────────
           /knife_grabbed (Bool)  ← 外部发布: 刀已拿好
           /tofu_rotated (Bool)   ← legacy接口；当前Phase4测试逻辑不依赖
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
                              ┌─────────────────────────────────────┤
                              │                                     │
                 knife_prepare_action_server              tofu_cut_coordinator_node
                 Action: /move_to_prepare_pose             (状态机编排)
                 订阅: /tofu_state                         订阅: /knife_grabbed
                  订阅: /joint_states                              /tofu_rotated (legacy)
                 发布: /joint_states_remapped                    /tofu_state
                              │                            调用 Action: /move_to_prepare_pose
                              │                            调用 Service: /arm_r/robot/move_rt_*
                              ▼
                    机械臂到达预备位

                ── 外部信号 ──────────────────────────────────────
                /knife_grabbed (Bool)  ← 外部发布: 刀已拿好
                /tofu_rotated (Bool)   ← legacy接口；当前Phase4测试逻辑不依赖
```

---

## 4. 消息/Action/Service 定义

### 4.1 新增消息: TofuState.msg

```
# TofuState.msg - 豆腐状态（持续性话题，每帧发布）
# 文件位置: cuttofo_lbot_interfaces/msg/TofuState.msg

std_msgs/Header header

# 基础位姿（来自 /objects_with_pose）
geometry_msgs/Pose pose             # 豆腐中心在 base 坐标系下的 6D 位姿
float32[3] extents                  # 豆腐 3D 尺寸 [extX, extY, extZ]（全尺寸，单位 m）
float32 confidence                  # 检测置信度

# 预计算的顶面几何
geometry_msgs/Point[] top_corners   # 顶面4顶点（base坐标系，Y最大的4个）
geometry_msgs/Vector3 edge_dir     # 豆腐右边棱边方向向量（归一化，在XZ平面内，与base_X+锐角）
geometry_msgs/Point tcp_target      # 预计算的 TCP 目标点（base坐标系）
float32 top_y                       # 豆腐顶面 Y 坐标（4角点平均Y）

# 状态标记
bool is_valid                       # 当前帧检测是否有效
uint32 object_id                    # 物体 ID
```

**设计说明**：
- `top_corners`: 由 `pose + quaternion + extents → 重建8角点 → 取Y最大4个` 得到
- `edge_dir`: 由 `top_corners → A,B(Z最大2个) → v(AB方向,XZ投影,锐角约束) → 归一化` 得到
- `tcp_target`: 由 `top_corners + offset_a + vertical_offset → 7步几何算法` 得到
- 消费端无需重复计算，直接使用 `tcp_target` 和 `edge_dir` 即可

### 4.2 新增 Action: MoveToPreparePose.action

```
# MoveToPreparePose.action - 移动刀到预备位
# 文件位置: cuttofo_xcore/action/MoveToPreparePose.action

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

### 4.3 新增 Action: ExecuteKnifeCut.action

```
# ExecuteKnifeCut.action - Phase3/5 RT 切削执行
# 文件位置: cuttofo_lbot_interfaces/action/ExecuteKnifeCut.action

# Goal
string phase_name              # "PHASE_3_FIRST_CUT" 或 "PHASE_5_SECOND_CUT"
---
# Result
bool success
string message                # 成功/失败原因
int32 executed_waypoints      # 实际执行路点数
float64 elapsed_s             # 总耗时
---
# Feedback
string current_phase          # 当前阶段标签
float32 progress               # 进度 0.0 ~ 1.0
int32 waypoint_index          # 当前路点索引
int32 waypoint_count          # 总路点数
```

### 4.4 已有接口（复用）

| 接口 | 类型 | 消息 | 说明 |
|------|------|------|------|
| `/objects_with_pose` | Topic | ObjectStateArray | 感知管线输出 |
| `/joint_states` | Topic | JointState | 机械臂关节角 |
| `/joint_states_remapped` | Topic | JointState | RViz 显示用（双臂合并） |
| `/arm_r/robot/move_rt_cartesian_path` | Service | MoveRtCartesianPath | RT 笛卡尔路径（阻抗/位置） |
| `/arm_r/robot/get_state` | Service | GetRobotState | 获取当前位姿 |
| `/knife_grabbed` | Topic | Bool | 外部发布：刀已拿好 |
| `/tofu_rotated` | Topic | Bool | legacy接口；当前Phase4测试逻辑不依赖 |
| `/execute_knife_cut` | Action | ExecuteKnifeCut | Phase3/5 切削执行 |

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
| `buffer_size` | `15` | int | 滑动窗口帧数（多帧平均抑制噪声） |
| `jump_threshold` | `0.05` | double | 跳变检测阈值 (m)，超过则清空 buffer |
| `min_buffer_frames` | `3` | int | buffer 最少帧数才输出有效结果 |
| `valid_timeout` | `2.0` | double | 检测超时标记无效 (s) |

**噪声抑制策略 — 滑动窗口多帧平均**:

由于豆腐和相机在切削准备阶段都是静止的，深度噪声和 SAM3 分割边缘波动会导致
角点坐标帧间抖动。采用滑动窗口对 `top_corners` 做多帧平均，在几何计算**之前**
抑制噪声，使 `edge_dir` 和 `tcp_target` 输出稳定。

```
帧 t-14 ─┐
帧 t-13 ─┤
...      ─┼─→ buffer[15帧] ──→ mean(top_corners) ──→ 几何计算 ──→ 输出
帧 t-1  ─┤
帧 t    ─┘
```

**滑动窗口工作流程**:
1. 每帧：`ObjectState → reconstruct_corners → extract_top_corners → 4个3D点`
2. 将新帧 `top_corners` 推入 buffer（FIFO，满时弹出最老帧）
3. 跳变检测：若新帧角点中心与 buffer 最后一帧中心距离 > `jump_threshold`，清空 buffer
4. 若 buffer 帧数 ≥ `min_buffer_frames`：对 buffer 内所有帧的角点取均值
5. 从平均后的角点计算 `edge_dir` 和 `tcp_target`
6. 若 buffer 帧数 < `min_buffer_frames`：不输出（`is_valid=False`）

**边界情况处理**:

| 情况 | 处理 |
|------|------|
| buffer 未满（< buffer_size 帧） | 只要 ≥ min_buffer_frames 就正常输出 |
| 豆腐消失（无检测） | 不推入新帧，buffer 保持不变，超时后 is_valid=False |
| 豆腐位置突变（旋转后） | 跳变检测触发 → 清空 buffer → 重新积累 |
| 首次启动 | buffer 为空，等待积累到 min_buffer_frames 后才输出 |

**核心逻辑**:

```python
class TofuStateNode(Node):
    def __init__(self):
        self._subscription = self.create_subscription(
            ObjectStateArray, "/objects_with_pose", self._on_objects, 10)
        self._publisher = self.create_publisher(TofuState, "/tofu_state", 10)
        self._timer = self.create_timer(1.0 / publish_rate, self._publish_timer)
        self._buffer = []                # 滑动窗口: list of top_corners (4×3 ndarray)
        self._latest_state = None        # 最新 TofuState
        self._last_update_time = 0.0     # 最后更新时间

    def _on_objects(self, msg: ObjectStateArray):
        # 1. 过滤 class_id == class_filter 的目标
        # 2. 取第一个匹配目标
        # 3. 重建 8 角点: pose + quaternion + extents → corners_8
        # 4. 取 Y 最大的 4 个 = top_corners (4×3)
        # 5. 跳变检测: 若 buffer 非空且新帧中心偏移 > jump_threshold → 清空 buffer
        # 6. 推入 buffer，弹出最老帧（若满）
        # 7. 若 len(buffer) < min_buffer_frames → 不计算，等待积累
        # 8. avg_corners = mean(buffer, axis=0)  ← 多帧平均
        # 9. edge_dir = compute_edge_dir(avg_corners)
        # 10. tcp_target = compute_tcp_target_from_corners(avg_corners, offset_a, vertical_offset)
        # 11. 保存到 self._latest_state

    def _publish_timer(self):
        # 构造 TofuState 消息
        # 若 self._latest_state 非空且未超时: is_valid = True
        # 若超时: is_valid = False
        # 发布
```

**关键计算函数**（位于 `tofu_geometry.py`）:

```python
def compute_tcp_target_from_corners(corners_4, offset_a, vertical_offset, edge_align=True):
    """7步几何算法: 顶面4顶点 → TCP目标点
    
    Args:
        corners_4: 顶面4角点 (base坐标系)
        offset_a: 沿 l 方向偏移量 (m)
        vertical_offset: 垂直偏移量 (m)
        edge_align: True=用实际AB方向, False=假设AB平行于base_X
    """
    # Step 1: top_y = mean(corners_4[:, 1])
    # Step 2: A, B = Z最大的2个顶点（右边棱边）
    #          sorted_idx = argsort(corners_4[:, 2])
    #          A = corners_4[sorted_idx[-2]], B = corners_4[sorted_idx[-1]]
    # Step 3: v = AB方向，投影XZ平面，保证 v.x > 0
    #          edge_align=false 时 v = [1, 0, 0]
    #          edge_align=true 时 v = normalize([v_raw.x, 0, v_raw.z])
    # Step 4: l 为 AB 在 XZ 平面内的垂线，选择 l.z < 0 的方向（朝 base_Z- / 左）
    # Step 5: D = (A + B) / 2
    # Step 6: D_prime = D + offset_a * l
    # Step 7: tcp_target = [D_prime[0], top_y + vertical_offset, D_prime[2]]
    return tcp_target

def compute_edge_dir(corners_4, edge_align=True):
    """顶面4顶点 → 右边棱边方向向量（归一化，XZ平面内，与base_X+锐角）
    
    Args:
        corners_4: 顶面4角点 (base坐标系)
        edge_align: True=用实际AB方向, False=返回[1,0,0]
    """
    # A, B = Z最大的2个顶点
    # v_raw = B - A 或 A - B（取 X 分量 > 0 的）
    # edge_dir = normalize([v_raw.x, 0, v_raw.z])
    # edge_align=false 时直接返回 [1, 0, 0]
    return edge_dir

def reconstruct_corners(pos, quat, extents):
    """pose + quaternion + extents → 8角点（base坐标系）"""
    half = np.array(extents) / 2.0
    corners_local = ...  # 8个 ±half 组合
    R = Rotation.from_quat(quat).as_matrix()
    return corners_local @ R.T + pos
```

### 5.2 knife_prepare_action_server（刀预备位 Action 服务器）

**职责**: 接收 Action Goal，从 /tofu_state 获取目标（或使用手动目标），IK 求解最优预备关节角，发布关节状态驱动机械臂到位。

**订阅**:
- `/tofu_state` (TofuState) — 豆腐状态（获取 tcp_target, edge_dir）
- `/joint_states` (JointState) — 当前关节角

**Action**:
- `/move_to_prepare_pose` (MoveToPreparePose)

**发布**:
- `/joint_states_remapped` (JointState) — 预备位关节角

**参数**:

| 参数 | 默认值 | 类型 | 说明 |
|------|--------|------|------|
| `candidate_count` | `240` | int | IK 候选数量 |
| `preview_steps` | `15` | int | preview 步数 |
| `safety_margin_deg` | `15.0` | double | 关节安全余量 |
| `position_tolerance_mm` | `1.0` | double | 到位位置容差 (mm) |
| `arrival_timeout_s` | `10.0` | double | 到位超时 (s) |

**核心逻辑**:

```python
class KnifePrepareActionServer(Node):
    def __init__(self):
        self._kin = OfflineURDFKinematics(URDF_PATH)
        self._action_server = ActionServer(
            self, MoveToPreparePose, "/move_to_prepare_pose",
            self.execute_callback)

    def execute_callback(self, goal_handle):
        # 1. 获取目标位置和姿态
        if goal_handle.use_vision:
            # 等待有效的 /tofu_state
            tofu_state = self._wait_for_tofu_state(goal_handle.timeout_s)
            target_pos = tofu_state.tcp_target
            edge_dir = tofu_state.edge_dir if goal_handle.edge_align else None
        else:
            target_pos = [goal_handle.manual_target_pose.position.x, ...]
            edge_dir = None

        # 2. 构建目标旋转矩阵
        target_R = build_rotation(plane_angle, edge_dir)

        # 3. TCP→法兰位置补偿 (adapter 内部自动处理)
        #    adapter.solve_ik() 接收的是 TCP 目标位姿
        #    内部执行: flange_target = target_pos - target_R @ tcp_offset
        #    然后对法兰求解 IK

        # 4. IK 多候选求解 + preview 评分
        best_q = arm.solve_ik(target_pos, target_eul)

        # 5. 发布关节角
        # 若有 xCore RT 控制: 通过 Service 指令机械臂移动
        # 若离线调试: 发布到 /joint_states_remapped 驱动 RViz

        # 6. 等待到位
        # 监测关节角与目标差 < threshold 或超时

        # 7. 返回 Result
        goal_handle.succeed(result)
```

**与 prepare_pose_selector.py 的关系**:
- `prepare_pose_selector.py` 保留为**离线调试工具**
- `knife_prepare_action_server` 复用其核心算法（IK求解、评分、约束构建）
- 核心函数抽取到共享模块 `ik_utils.py` 和 `tofu_geometry.py`

### 5.3 tofu_cut_coordinator_node（协调节点，状态机）

**职责**: 管理整体切削流程状态机，协调各节点按序执行。

**订阅**:
- `/knife_grabbed` (Bool) — 刀已拿好信号
- `/tofu_rotated` (Bool) — legacy豆腐旋转完毕信号；当前Phase4回prepare测试逻辑不依赖
- `/tofu_state` (TofuState) — 豆腐状态监控（仅监控，不用于计算）

**Action Client**:
- `/move_to_prepare_pose` (MoveToPreparePose) — 移刀到预备位

**Service Client**:
- `/arm_r/robot/move_rt_cartesian_segment` — RT 切削运动
- `/arm_r/robot/get_state` — 获取当前位姿

**发布**:
- `/tofu_cut/task_state` (TaskState) — 任务状态广播

**参数**:

| 参数 | 默认值 | 类型 | 说明 |
|------|--------|------|------|
| `plane_angle_deg` | `40.0` | double | 刀面倾斜角 |
| `cut_cycles` | `3` | int | 每轮切削刀数 |
| `cut_flange_axis` | `"z"` | string | 切削方向（法兰坐标系轴）|
| `cut_flange_distance` | `-0.017` | double | 单次切深 (m) |
| `shift_axis` | `"y"` | string | 切间横移轴 |
| `shift_distance` | `0.015` | double | 切间横移距离 (m) |
| `speed_scale` | `0.12` | double | RT 速度缩放 |
| `edge_align` | `false` | bool | 是否使用边对齐 |
| `offset_a` | `0.03` | double | 水平偏移 |
| `vertical_offset` | `0.03` | double | 垂直偏移 |

**状态机详细设计**:

```python
class PhaseManagerNode(Node):
    STATES = [
        "PHASE_1_GRAB_KNIFE",        # 等待拿刀信号
        "PHASE_2_MOVE_TO_PREPARE",   # 移刀到预备位
        "PHASE_3_FIRST_CUT",         # 第一次切割
        "PHASE_4_ROTATE_TOFU",       # 当前测试逻辑：回到prepare位
        "PHASE_5_SECOND_CUT",        # 第二次切割，复用Phase3配置
        "DONE",
        "ERROR",
    ]

    def run_state_machine(self):
        while self.state not in ("IDLE", "ERROR"):
            if self.state == "WAITING_KNIFE":
                self._wait_for_knife_grabbed()
            elif self.state == "MOVING_TO_PREPARE":
                self._move_to_prepare()
            elif self.state == "PHASE_3_FIRST_CUT":
                self._execute_cutting()
            elif self.state == "PHASE_4_ROTATE_TOFU":
                self._send_execute_knife_cut("PHASE_4_ROTATE_TOFU")
            elif self.state == "PHASE_5_SECOND_CUT":
                self._send_execute_knife_cut("PHASE_5_SECOND_CUT")

    def _move_to_prepare(self):
        """Phase 2: 调用 Action 移刀到预备位"""
        goal = MoveToPreparePose.Goal()
        goal.use_vision = True
        goal.plane_angle_deg = self.plane_angle_deg
        goal.edge_align = self.edge_align
        goal.offset_a = self.offset_a
        goal.vertical_offset = self.vertical_offset

        future = self._action_client.send_goal_async(goal)
        # 等待 Action 完成
        result = self._wait_for_action_result(future)

        if result.success:
            self.state = self._next_state_after_prepare()
        else:
            self.state = "ERROR"

    def _next_state_after_prepare(self):
        """从预备位状态转换到下一状态"""
        if self._is_first_prepare:
            return "PHASE_3_FIRST_CUT" # Phase 2 → Phase 3
        else:
            return "ERROR"

    def _execute_cutting(self):
        """Phase 3: 循环调用 RT Service 执行切削"""
        for cycle in range(cut_cycles):
            # 1. 获取当前位姿
            current_pos, current_ori = self._get_robot_state()

            # 2. 沿法兰Z+切入 (cut_move)
            down_pos, down_ori = build_target_pose_along_flange_axis(
                current_pos, current_ori, flange_axis, flange_distance)
            self._move_segment(down_pos, down_ori, speed_scale)

            # 3. 沿法兰Z-回刀 (cut_move，回到本cycle锚点)
            up_pos, up_ori = build_target_pose_along_flange_axis(
                current_pos, current_ori, flange_axis, -flange_distance)
            self._move_segment(up_pos, up_ori, speed_scale)

            # 4. 沿base坐标系配置step轴平移（非最后一刀）
            if cycle < cut_cycles - 1:
                shift_pos, shift_ori = build_target_pose_in_base(
                    current_pos, current_ori, shift_axis, shift_distance)
                self._move_segment(shift_pos, shift_ori, speed_scale)

        # Phase3完成 → Phase4回prepare；Phase5完成 → DONE
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
                   ┌─────────────────────────────────┐
                   │ 重建8角点                         │
                   │ 取Y最大4顶点 = top_corners        │
                   │ A,B = Z最大2个（右边棱边）         │
                   │ v = AB方向(XZ投影,锐角约束)        │
                   │ edge_dir = v                      │
                   │ l = AB水平垂线，选择朝base Z-方向 │
                   │ D = (A+B)/2, D' = D + offset*l   │
                   │ tcp_target = [D'.x, top_y+off, D'.z] │
                   │ 滑动窗口多帧平均                   │
                   └─────────────────────────────────┘
                              │
                       /tofu_state (TofuState)
                        │           │           │
                        ▼           ▼           ▼
                  tcp_target   edge_dir   top_corners
                        │           │
                        ▼           ▼
              knife_prepare_action_server
              ┌──────────────────────────────────────┐
              │ 1. target_pos = tcp_target             │
              │    (语义: 刀刃中心应到达的位置)         │
              │                                        │
              │ 2. if edge_align:                      │
              │      target_R = build_rotation_with_edge_dir(α, edge_dir) │
              │    else:                               │
              │      target_R = build_target_rotation_from_constraints(α) │
              │    (语义: 法兰/TCP 的目标姿态)          │
              │                                        │
              │ 3. TCP→法兰位置补偿:                    │
              │      flange_target = target_pos - target_R @ tcp_offset │
              │    (语义: 法兰原点应到达的位置)          │
              │                                        │
              │ 4. IK multi-candidate solve (240 candidates) │
              │    目标: 把 link7(法兰) 放到 flange_target │
              │    姿态: target_R                       │
              │                                        │
              │ 5. Preview评分 → best_q                │
              │    (每个 preview 点同样做 TCP→法兰补偿)  │
              │                                        │
              │ 6. 关节安全检查 (±15° margin)          │
              │ 7. 发布关节角 → 机械臂运动             │
              └──────────────────────────────────────┘
                              │
                              ▼
               机械臂到达预备位:
               - 法兰在 flange_target 位置
               - 刀刃中心在 tcp_target 位置 (= flange + R @ tcp_offset)
               - 姿态: tcp_Y 沿 v 方向(刀脊), tcp_Z 倾斜 α°(刀面法线)
```

### 6.2 Phase 3 数据流（切豆腐）

```
当前位姿 (get_state) → 计算切削轨迹

                    ┌────────────────────────────┐
                    │ for cycle in range(N):       │
                    │   1. 沿法兰Z+切入 cut_move    │
                    │   2. 沿法兰Z-回刀 cut_move    │
                    │   3. 沿base坐标系step轴平移   │
                    └────────────────────────────┘
                              │
                              ▼
                    xCore RT Cartesian Path 执行
                              │
                              ▼
                    机械臂完成N刀切削；净位移只来自step_x/y/z累计
```

### 6.3 Phase 4/5 数据流（回到Prepare后第二次切割）

```
Phase3完成，当前法兰位姿 = Phase2 prepare + (cycles-1) * [step_x, step_y, step_z]
         │
         ▼
Phase4发送 /execute_knife_cut goal: PHASE_4_ROTATE_TOFU
         │
         ▼
knife_cut_action_server 读取 phase3_first_cut 的 cycles/step_x/step_y/step_z
         │
         ▼
计算 return_offset = -(cycles-1) * [step_x, step_y, step_z]
         │
         ▼
move_rt_cartesian_path 单路点平移回 Phase2 prepare anchor
         │
         ▼
Phase5发送 /execute_knife_cut goal: PHASE_5_SECOND_CUT
         │
         ▼
Phase5 通过 reuse_phase: phase3_first_cut 复用 Phase3 切割参数
         │
         ▼
执行第二次切割：切入 → 回刀 → base step 平移
```

---

## 7. 关键算法复用关系

### 7.1 已有算法 → 新模块映射

| 算法 | 来源 (prepare_pose_selector.py) | 目标模块 |
|------|--------------------------------|----------|
| 双约束旋转矩阵 | `build_target_rotation_from_constraints()` | `ik_utils.py` |
| 边对齐广义旋转矩阵 | 广义公式 (e_x, e_z) | `ik_utils.py` |
| IK 多候选求解 | `solve_ik_multi_candidate()` | `ik_utils.py` |
| Preview 评分 | `score_candidate()` | `ik_utils.py` |
| TCP 目标几何 | `compute_tcp_target_from_corners()` | `tofu_geometry.py` |
| OBB 8 角点重建 | `_reconstruct_corners()` | `tofu_geometry.py` |
| 边方向计算 | `compute_edge_dir()` | `tofu_geometry.py` |
| 离线 FK | `OfflineURDFKinematics` | `offline_urdf_kinematics.py` (保留) |
| 静态关节发布 | `StaticJointStatePublisher` | 仅调试用，不抽取 |

### 7.2 新建代码文件结构

```
cuttofo_xcore/
├── msg/
│   └── TofuState.msg                    # 新增消息定义
├── action/
│   └── MoveToPreparePose.action          # 新增Action定义
│
├── cuttofo_xcore/
│   ├── tofu_geometry.py                  # 从 prepare_pose_selector.py 抽取
│   │   ├── reconstruct_corners()
│   │   ├── compute_tcp_target_from_corners()
│   │   └── compute_edge_dir()
│   │
│   ├── ik_utils.py                       # 从 prepare_pose_selector.py 抽取
│   │   ├── build_target_rotation_from_constraints()
│   │   ├── build_rotation_with_edge_dir()
│   │   ├── solve_ik_with_preview()
│   │   └── score_candidate()
│   │
│   ├── offline_urdf_kinematics.py        # 保留不动
│   ├── tofu_state_node.py                # 新建: 豆腐状态持续发布
│   ├── knife_prepare_action_server.py     # 新建: 刀预备位Action
│   ├── tofu_cut_coordinator_node.py       # 新建: 整体状态机协调
│   ├── prepare_pose_selector.py           # 保留: 离线调试工具
│   ├── demo_offline_ik_to_rviz.py         # 保留: 离线调试
│   ├── demo_cut_tofu_xcore_ros.py         # 保留: RT切削核心逻辑参考
│   └── ...
```

---

## 8. 启动与运行

### 8.1 完整系统启动顺序

```bash
# Step 1: 启动机械臂 + RViz
ros2 launch ar5_dual_arm_bringup dual_display.launch.py \
  use_joint_gui:=false enable_realsense:=true enable_aruco:=false

# Step 2: 启动 SAM3 检测 (指定豆腐)
ros2 run dexbot_middle_layer sam3_detector_node --ros-args \
  -p text_prompt:=豆腐

# Step 3: 启动姿态估计
ros2 run dexbot_middle_layer pose_estimator_node --ros-args \
  -p calibration_file:=/home/tbl/Project/dexbot_ros2_ws/src/config/calibration_result.yaml

# Step 4: 启动豆腐状态节点
ros2 run cuttofo_xcore tofu_state_node --ros-args \
  -p class_filter:=tofu \
  -p offset_a:=0.03 \
  -p vertical_offset:=0.03

# Step 5: 启动刀预备位 Action 服务器
ros2 run cuttofo_xcore knife_prepare_action_server --ros-args \
  -p candidate_count:=240 \
  -p preview_steps:=15

# Step 6: 启动协调节点
ros2 run cuttofo_xcore tofu_cut_coordinator_node --ros-args \
  -p plane_angle_deg:=40.0 \
  -p cut_cycles:=3

# Step 7: 机械臂拿刀 (外部操作)
# ... 人或外部脚本控制 ...

# Step 8: 发送拿刀完成信号
ros2 topic pub --once /knife_grabbed std_msgs/msg/Bool '{data: true}'

# legacy：真实豆腐旋转流程恢复后才需要发送旋转完成信号
ros2 topic pub --once /tofu_rotated std_msgs/msg/Bool '{data: true}'
```

### 8.2 调试模式（不连机械臂，RViz预览）

```bash
# 离线调试：手动指定目标位
python3 src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py \
  --x 0.25 --y 0.0 --z 0.25 \
  --plane-angle-deg 40 \
  --publish-topic /joint_states_remapped

# ROS 视觉输入调试
python3 src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py \
  --ros-input --ros-input-class tofu \
  --plane-angle-deg 40 \
  --publish-topic /joint_states_remapped

# 边对齐约束调试
python3 src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py \
  --ros-input --ros-input-class tofu \
  --edge-align --plane-angle-deg 40 \
  --publish-topic /joint_states_remapped
```

---

## 9. 与现有代码的关系

### 9.1 现有脚本 → 新模块映射

| 现有脚本 | 功能 | 新模块中对应 | 处理方式 |
|---------|------|------------|---------|
| `prepare_pose_selector.py` | 离线IK+RViz预览 | 核心算法抽入 `ik_utils.py` | **保留**为调试工具 |
| `demo_offline_ik_to_rviz.py` | 离线FK+IK | 被新模块取代 | **保留**为调试工具 |
| `offline_urdf_kinematics.py` | URDF正运动学 | 被 `ik_utils.py` 引用 | **保留**，共享模块 |
| `demo_cut_tofu_xcore_ros.py` | RT切削执行 | 核心逻辑抽入 coordinator | **保留**为参考 |
| `demo_adjust_knife_pose_xcore.py` | 刀姿态调整 | 参考逻辑 | **保留**，不再单独使用 |

### 9.2 感知管线 → tofu_state_node 数据映射

| 感知管线输出 | 字段 | tofu_state_node 使用 |
|-------------|------|---------------------|
| `ObjectState.pose` | 6D位姿 | 重建8角点 → 4顶面顶点 |
| `ObjectState.geometric_features[5:8]` | extX, extY, extZ (全尺寸) | 重建8角点 |
| `ObjectState.class_id` | "tofu" | 过滤条件 |
| `ObjectState.confidence` | 置信度 | 直通 |
| `ObjectState.id` | 物体ID | 直通 |

### 9.3 关键参数适配

| 参数 | 单臂版本(旧) | 双臂版本(当前) | 说明 |
|------|------------|--------------|------|
| base Y+ 方向 | 向下 | **向上** | `base_y = [0, -1, 0]` 已修正 |
| 法兰坐标系 | 与base一致 | 与base一致 | 归零时完全相同 |
| 刀脊约束 | `tcp_x·base_x=1` | **`tcp_Y·v=1`** | 刀脊=TCP Y轴=v方向 |
| v 方向约束 | — | v·base_X+ > 0 | v 在 XZ 平面内，与 base_X+ 锐角 |
| l 方向约束 | — | l⊥v, l∥XZ, l.z<0 | 选择与 base_Z- 夹角为锐角的水平垂线 |
| plane_angle max | 90° | **40-45°** | joint_6 ±40°安全限位 |
| 关节安全余量 | — | **15°** | IK求解硬约束 |
| A,B 选取 | — | Z最大的2个顶点 | 右边棱边端点 |
| edge_align | — | false(默认)/true | false=v固定base_X, true=v跟随实际AB |

---

## 10. 里程碑与优先级

| 阶段 | 内容 | 优先级 | 依赖 | 状态 |
|------|------|--------|------|------|
| **M0** | 定义 TofuState.msg + MoveToPreparePose.action | P0 | 无 | 📋 待实现 |
| **M1** | 抽取共享模块 `ik_utils.py` + `tofu_geometry.py` | P0 | 无 | 📋 待实现 |
| **M2** | 实现 `tofu_state_node`（订阅+计算+持续发布） | P0 | M0 | 📋 待实现 |
| **M3** | 实现 `knife_prepare_action_server`（Action+IK+评分） | P0 | M0, M1 | 📋 待实现 |
| **M4** | 实现 `tofu_cut_coordinator_node`（状态机+协调） | P1 | M2, M3 | 📋 待实现 |
| **M5** | 端到端测试：感知→就位→切削→旋转→再就位 | P2 | M4 | 📋 待实现 |

---

## 11. 风险与待决事项

| 风险/待决 | 说明 | 影响 | 缓解措施 |
|----------|------|------|---------|
| 豆腐检测稳定性 | SAM3+PCA对豆腐的检测稳定性未充分验证 | tofu_state_node 可能频繁 `is_valid=False` | EMA平滑 + 超时容错 + 手动目标回退 |
| 切削轨迹参数 | 切深、速度、横移距离需现场调试 | 影响切削质量和效率 | 参数可配（launch args） |
| 机械臂到位确认 | 如何判断已到达预备位？ | Action 结果可靠性 | 关节角阈值（±2°）+ 时间超时（10s） |
| 旋转豆腐精度 | 旋转后豆腐位置变化幅度不确定 | edge_align 约束重要性凸显 | 旋转后重新检测+重新IK求解 |
| EMA平滑参数 | 平滑系数需要平衡响应速度与稳定性 | 过渡平滑 vs 响应延迟 | 默认0.4，可通过参数调节 |
| 多豆腐目标 | 当前只取第一个 tofu 目标 | 误选或漏选 | 未来可加手动选择或最近目标策略 |
| Action Server 中断 | Action 执行中收到新 Goal 如何处理？ | 状态机混乱 | 策略：抢占（Preempt）当前 Goal |
| 协调节点重启恢复 | 协调节点崩溃后如何恢复状态？ | 流程中断 | 状态机持久化 + 参数化初始状态 |

---

## 12. 附录：核心几何算法速查

### 12.1 坐标系约定

```
       Y(上)
       ↑
       │         arm 在 +Z 侧（右侧）
       │
       └──────→ X(前)
      ╱
     ╱
    ↙
   Z(右)
```

- Base X+ = 前（forward）
- Base Y+ = 上（up）
- Base Z+ = 右（right）—— arm 在此侧
- 法兰归零时与 base 同向

### 12.2 核心约束表

| 约束 | 数学表达 | 说明 |
|------|---------|------|
| 刀脊方向 | `tcp_Y · v = 1` | TCP Y轴单位向量 = v 方向单位向量（刀脊沿棱边） |
| 刀面倾斜 | `tcp_Z` 与 XZ 平面夹角 = α | α = plane_angle_deg，受 joint_6 ±40° 限制 |
| v 方向约束 | v 在 XZ 平面内，v · base_X+ > 0 | v 与 base_X+ 保持锐角 |
| l 方向约束 | l ⊥ v，l 在 XZ 平面内，l · base_Z- > 0 | l 与 base_Z- 保持锐角，作为从右边缘朝左偏移方向 |
| 关节安全余量 | ≥15° 硬约束 | IK 求解时关节实际限位收缩 15° |

### 12.3 A, B 点定义

```
输入: top_corners (顶面4角点, base坐标系, Y最大的4个)

sorted_by_Z = argsort(top_corners[:, 2])    ← 按 Z 从小到大排序

A = top_corners[sorted_by_Z[-2]]            ← Z 第二大（次右侧）
B = top_corners[sorted_by_Z[-1]]            ← Z 最大（最右侧）

A, B 构成豆腐顶面的【右边棱边】的两个端点
```

几何含义：在 base 坐标系中，Z 越大越靠右。取 Z 最大的两个角点，
它们是顶面矩形右侧那条边的两个端点。Phase2 prepare 目标从豆腐右侧开始计算。

```
俯视图 (Y 轴朝上，看不见):

              Z(右, arm侧)
              ↑
              │
    A ●───────────● B        ← Z 最大的两个点（右边棱边）
      │           │
      │   豆腐    │
      │   顶面    │
    C ●───────────● D        ← Z 较小的两个点（左边棱边）
              │
              └──────────→ X(前)
```

### 12.4 v 向量（棱边方向）

**定义**: v = 豆腐右边棱边 AB 的方向向量，投影到 XZ 平面，与 base_X+ 保持锐角。

```
v_raw = B - A  或  A - B，取使 X 分量 > 0 的那个
v = normalize([v_raw.x, 0, v_raw.z])
```

**约束**:
- v 在 XZ 平面内（Y 分量 = 0）
- v · base_X+ > 0（与前方保持锐角）
- |v| = 1（单位向量）

**两种模式**:

| 模式 | v 的值 | 说明 |
|------|--------|------|
| edge_align=false | [1, 0, 0]（固定） | 假设豆腐平放，AB 边平行于 base_X |
| edge_align=true | 实际 AB 方向 | 根据检测到的角点计算，跟随豆腐实际朝向 |

**edge_align=false 是理想情况的简化**：假设豆腐完美平放，AB 边严格平行于 base_X，
此时 v 直接取 [1,0,0]，无需计算。

**edge_align=true 是真实情况**：豆腐放置不完美，AB 边可能与 base_X 有夹角，
此时 v 根据实际检测到的 A、B 角点计算，刀脊跟随豆腐实际棱边方向。

### 12.5 l 向量（接近方向 = AB 的垂线）

**定义**: l = v 在 XZ 平面内的垂线方向，选择朝左（base Z-）的那个方向。

```
l_candidate = cross(v, [0, 1, 0]) = [-vz, 0, vx]
if l_candidate.z > 0:
    l = -l_candidate
else:
    l = l_candidate
```

**性质验证**:
- l ⊥ v ✓（候选垂线与 v 正交，取反后仍正交）
- l 在 XZ 平面 ✓（Y 分量 = 0）
- l · base_Z- > 0 ✓（等价于 l.z < 0）

**结论：需要选择垂线方向。v.x > 0 只确定 AB 朝前，不再自动决定 l 的朝向；Phase2 prepare 要从右侧向左偏移，所以必须选择 l.z < 0 的方向。**

**示例**:
| v | l_candidate = [-vz, 0, vx] | 最终 l | l.z |
|---|---|---|---|
| [1, 0, 0] | [0, 0, 1] | [0, 0, -1] | < 0 ✓ |
| [0.9, 0, 0.4] | [-0.4, 0, 0.9] | [0.4, 0, -0.9] | < 0 ✓ |
| [0.9, 0, -0.4] | [0.4, 0, 0.9] | [-0.4, 0, -0.9] | < 0 ✓ |
| [0.7, 0, 0.7] | [-0.7, 0, 0.7] | [0.7, 0, -0.7] | < 0 ✓ |

### 12.6 TCP 目标点计算（7步）

```
输入: corners_4 (顶面4顶点, base坐标系), offset_a=0.03, vertical_offset=0.03

Step 1: top_y = mean(corners_4[:, 1])
        → 顶面平均高度

Step 2: A, B = Z 最大的 2 个顶点（右边棱边的两个端点）
        → sorted_idx = argsort(corners_4[:, 2])
        → A = corners_4[sorted_idx[-2]], B = corners_4[sorted_idx[-1]]

Step 3: v = AB 方向，投影到 XZ 平面，保证 v.x > 0
        → v_raw = B - A 或 A - B（取 X 分量 > 0 的）
        → v = normalize([v_raw.x, 0, v_raw.z])
        → edge_align=false 时直接取 v = [1, 0, 0]

Step 4: l_candidate = cross(v, [0, 1, 0]) = [-vz, 0, vx]
        → 若 l_candidate.z > 0，则 l = -l_candidate
        → 最终满足 l.z < 0，即 l 与 base_Z- 夹角为锐角
        → l 已经是单位向量（因为 v 是单位向量且在 XZ 平面内）

Step 5: D = (A + B) / 2
        → 右边棱边中点

Step 6: D' = D + offset_a * l
        → 沿 l 方向（朝左/base_Z-）偏移 offset_a

Step 7: TCP = [D'.x, top_y + vertical_offset, D'.z]
        → X, Z 在 D' 位置，Y 比顶面高 vertical_offset
```

**几何含义**: TCP 在豆腐右边棱边中点，沿 AB 的水平垂线朝左（base_Z-）偏移 `offset_a`，并抬高 `vertical_offset`。
刀从豆腐右侧 prepare，后续 Phase3/5 通过负 `step_z` 可从右往左完成多刀切割。

```
俯视图:

              Z(右, arm侧)
              ↑
              │
              │
              │     A ●───────● D ──────● B     ← 右边棱边
              │       │       (中点)  ← l 朝左/base_Z-
              │       │           ● TCP (D' 位置)
              │       │
              │     C ●───────────────● D2
              │
              └──────────→ X(前)
                    → v (棱边方向)
```

### 12.7 刀姿态旋转矩阵

**输入**: plane_angle = α, v = [ex, 0, ez]（edge_dir，单位向量）

**推导**:
```
tcp_Y = v = [ex, 0, ez]                              ← 刀脊 = 棱边方向
n_pose = cross(v, Y_up) = [-ez, 0, ex]               ← 姿态构造用水平法向；不等同于右侧prepare偏移用的l
tcp_Z = cos(α)·n_pose - sin(α)·Y_up                  ← 刀面法线，从水平面倾斜 α 度
      = [-ez·cos(α), -sin(α), ex·cos(α)]
tcp_X = cross(tcp_Y, tcp_Z)                           ← 右手系叉积保证正交
      = [ez·sin(α), -cos(α), -ex·sin(α)]
```

**旋转矩阵** (列向量 = tcp 各轴在 base 系下的表达):
```
R = [tcp_X | tcp_Y | tcp_Z]

    | ez·sinα      ex       -ez·cosα  |
R = | -cosα        0        -sinα     |
    | -ex·sinα     ez        ex·cosα  |
```

**验证 det(R) = 1**:
```
det = ex·(0·ex·cosα - (-sinα)·ez) + 0 + (-ez·cosα)·((-cosα)·ez - 0)
    = ex·(sinα·ez) + (-ez·cosα)·(-cosα·ez)
    = ex·ez·sinα + ez²·cos²α
    ... (展开后 = ex² + ez² = 1) ✓
```

**退化验证** (edge_align=false, v=[1,0,0], ex=1, ez=0):
```
tcp_X = [0, -cosα, -sinα]
tcp_Y = [1, 0, 0]              ← 刀脊 = base_X ✓
tcp_Z = [0, -sinα, cosα]

R = | 0       1       0     |
    | -cosα   0      -sinα  |
    | -sinα   0       cosα  |
```

与 `build_target_rotation_from_constraints(α)` 完全一致 ✓

### 12.8 edge_align=false vs edge_align=true 完整对比

| | edge_align=false（理想/默认） | edge_align=true（真实/自适应） |
|---|---|---|
| **假设** | 豆腐完美平放，AB ‖ base_X | 豆腐放置不完美，AB 有偏角 |
| **v** | [1, 0, 0]（固定） | 实际 AB 方向（投影 XZ，锐角约束） |
| **l_offset** | [0, 0, -1]（固定 = base_Z-） | AB 的水平垂线，选择 l.z < 0 的方向 |
| **edge_dir** | [1, 0, 0] | 实际 AB 方向 |
| **刀脊 tcp_Y** | [1, 0, 0] = base_X | = v = 实际 AB 方向 |
| **TCP 偏移方向** | 纯 -Z（左） | 沿 l_offset（⊥AB，指向 base_Z-） |
| **旋转矩阵** | `build_target_rotation_from_constraints(α)` | `build_rotation_with_edge_dir(α, v)` |
| **适用场景** | 快速测试、豆腐放置精确时 | 生产环境、豆腐放置有偏差时 |

### 12.9 OBB 8角点重建

```
输入: pos (OBB中心, base坐标系), quat (姿态四元数), extents (全尺寸 [extX, extY, extZ])

half = extents / 2
corners_local = [±half[0], ±half[1], ±half[2]] 的 8 种组合 (2³=8)
R = Rotation.from_quat(quat).as_matrix()
corners_base = corners_local @ R.T + pos       ← 旋转 + 平移到 base 系

top_corners = corners_base 中 Y 最大的 4 个    ← 顶面（Y 向上）
```

### 12.10 完整数据流（Phase 2 几何计算）

```
/objects_with_pose (ObjectStateArray)
        │
        ├─ pos, quat, extents
        │
        ▼
reconstruct_corners(pos, quat, extents)  →  8 个 base 系角点
        │
        ▼
extract_top_corners(corners_8)  →  Y 最大的 4 个 = 顶面角点
        │
        ├──────────────────────────────────────────┐
        │                                          │
        ▼                                          ▼
compute_edge_dir(corners_4)              compute_tcp_target_from_corners(corners_4)
  │                                        │
  │ Step 2: A,B = Z最大2个                  │ Step 2: A,B = Z最大2个
  │ Step 3: v = AB方向(XZ投影,锐角)         │ Step 3: v = AB方向(XZ投影,锐角)
  │ → edge_dir = v                         │ Step 4: l=AB水平垂线, 选l.z<0
  │                                        │ Step 5: D = (A+B)/2
  │                                        │ Step 6: D' = D + offset_a * l
  │                                        │ Step 7: TCP = [D'.x, top_y+offset, D'.z]
  │                                        │
  ▼                                        ▼
TofuState.edge_dir                    TofuState.tcp_target
        │                                   │
        └───────────┬───────────────────────┘
                    │
                    ▼
        knife_prepare_action_server
          │
          ├─ target_pos = tcp_target
          │
          ├─ if edge_align:
          │     target_R = build_rotation_with_edge_dir(α, edge_dir)
          │  else:
          │     target_R = build_target_rotation_from_constraints(α)
          │
          ├─ TCP→法兰: flange_target = target_pos - target_R @ tcp_offset
          │
          ├─ IK 求解(对法兰) → best_q
          │
          └─ 驱动机械臂到达预备位
```

---

## 13. TCP Offset 标定与补偿

### 13.1 概念定义

```
TCP offset = 法兰坐标系下，从法兰原点到刀刃中心的平移向量 [dx, dy, dz]

                法兰(link7)
                  │
                  │  tcp_offset = [dx, dy, dz]
                  │  (法兰坐标系下的固定向量)
                  ▼
            刀刃中心 (刀具TCP)
```

**关键性质**:
- 纯平移，无旋转：刀具 TCP 坐标系的 X/Y/Z 轴方向 = 法兰坐标系的 X/Y/Z 轴方向
- 在法兰坐标系中表达：不随机械臂姿态变化而变化
- 在 base 坐标系中的实际偏移 = `R_flange @ tcp_offset`（随法兰姿态旋转）

### 13.2 数学关系

```
已知:
  tcp_offset = [dx, dy, dz]        (法兰坐标系下，标定得到)
  R_flange                          (法兰在 base 系下的旋转矩阵)

正向 (FK → TCP 位姿):
  tcp_pos = flange_pos + R_flange @ tcp_offset
  tcp_eul = flange_eul              (姿态不变)

逆向 (TCP 目标 → 法兰目标，用于 IK):
  flange_target_pos = tcp_target_pos - R_target @ tcp_offset
  flange_target_eul = tcp_target_eul    (姿态不变)
```

### 13.3 在控制流程中的位置

```
视觉管线输出:
  tcp_target_pos = 刀刃中心应到达的位置 (base 坐标系)
  target_R = 法兰/TCP 的目标姿态 (由几何约束构建)

         ┌─────────────────────────────────────────────┐
         │  TCP→法兰位置补偿 (adapter 层统一处理)        │
         │                                              │
         │  flange_target = tcp_target - target_R @ tcp_offset │
         │                                              │
         │  tcp_offset = [0,0,0] 时: flange_target = tcp_target │
         │  (标定前等效于 TCP = 法兰原点)                │
         └─────────────────────────────────────────────┘
                              │
                              ▼
         IK 求解: 把 link7(法兰) 放到 flange_target, 姿态 = target_R
                              │
                              ▼
         运动执行: move_to_joints(best_q)
                              │
                              ▼
         结果验证 (FK):
           flange_pos = FK(best_q)[:3, 3]
           tcp_pos_actual = flange_pos + R_flange @ tcp_offset
           error = |tcp_pos_actual - tcp_target_pos|
```

### 13.4 切预览 (Preview Rollout) 中的 TCP offset

切预览生成一系列下切目标点（刀刃中心沿 -Y 方向逐步下移）。每个 preview 点同样需要 TCP→法兰补偿：

```python
for i, preview_tcp_pos in enumerate(cut_trajectory):
    # 每个 preview 点的目标姿态不变（切削过程中保持刀姿态）
    flange_preview_pos = preview_tcp_pos - target_R @ tcp_offset
    q_solution = IK(flange_preview_pos, target_eul, seed=上一个解)
```

preview 评分逻辑（path_cost, jump_cost, limit_cost 等）不受影响，因为它们评估的是关节空间的运动质量。

### 13.5 配置存储

```yaml
# cuttofo_config.yaml
arms:
  right:
    tcp_offset: [0.0, 0.0, 0.0]    # 标定前默认值
    # 标定后示例: [-0.003, 0.090, -0.209]
    urdf:
      tip_link: "AR5-5_07R-W4C1C1_link7"   # IK 目标 = 法兰
      ...
  left:
    tcp_offset: [0.0, 0.0, 0.0]    # 标定前默认值
    urdf:
      tip_link: "AR5-5_07L-W4C1C1_link7"   # IK 目标 = 法兰
      ...
```

### 13.6 加载与生效

- `xcore_arm_adapter.__init__()` 从 `cuttofo_config.yaml` 读取 `tcp_offset`
- 所有 FK/IK 操作在 adapter 内部自动补偿
- 上层代码（action_server、coordinator、视觉管线）无需感知 tcp_offset 的存在
- 切换左右臂时自动切换到对应的 tcp_offset

### 13.7 标定流程（后续实施）

**方法**: 多点标定法（如 4 点法 / 6 点法）

**原理**: 固定一个空间参考点（如针尖），用不同法兰姿态让刀刃中心触碰同一点。
由于 `tcp_pos = flange_pos + R_flange @ tcp_offset` 对所有姿态成立，
多组 `(flange_pos_i, R_flange_i)` 联立方程组求解 `tcp_offset`。

**输出**: `tcp_offset = [dx, dy, dz]`，写入 `cuttofo_config.yaml`

**生效**: 重启节点即自动加载，无需额外操作

### 13.8 标定前的默认行为

`tcp_offset = [0, 0, 0]` 时：

```
flange_target = tcp_target - R @ [0,0,0] = tcp_target
```

等价于：法兰原点直接到达视觉目标位置。

对比当前代码（IK 目标 = link_tcp = 法兰 + [0,0,0.097]）：
- 当前：法兰在目标位置后方 97mm（Z 方向），刀刃中心位置不可预测
- 修改后：法兰原点在目标位置，刀刃中心也在目标位置（因为 offset=0）
- 标定后：法兰在正确位置，刀刃中心精确到达视觉目标

### 13.9 与 xcore_controller 的关系

| 接口 | 返回/接收 | 说明 |
|------|----------|------|
| `/robot/get_state` → `cartesian_pose` | **法兰位姿** (flangeInBase) | 代码注释+测试确认 |
| `/robot/move_joints` | 关节角 | 不涉及笛卡尔坐标 |
| `OfflineURDFKinematics.fk_matrix(q)` | **法兰位姿** (tip_link=link7) | 修改后 |

adapter 层统一处理：
- `get_pose()` → 返回 TCP 位姿 = 法兰位姿 + R @ tcp_offset
- `solve_ik(tcp_target_pos, tcp_target_eul)` → 内部转换为法兰目标再求解
- `compute_fk(joints)` → 返回 TCP 位姿 = FK(法兰) + R @ tcp_offset

### 13.10 代码修改清单（待实施）

| # | 文件 | 修改内容 |
|---|------|---------|
| 1 | `cuttofo_config.yaml` | `arms.right/left` 新增 `tcp_offset: [0,0,0]`；`tip_link` 改为 `link7` |
| 2 | `xcore_arm_adapter.py` | 加载 `tcp_offset`；`solve_ik()` 内部做 TCP→法兰补偿；`compute_fk()` 和 `get_pose()` 返回 TCP 位姿 |
| 3 | `execute_prepare_pose.py` | 删除硬编码 `_FLANGE_TO_TCP`，改用 adapter 统一接口 |
| 4 | `prepare_pose_selector.py` | `tip_link` 改为 `link7`，preview 中加入 TCP offset 补偿 |
| 5 | `knife_prepare_action_server.py` | 无需修改（语义不变：传入的是"刀刃中心目标"，adapter 内部补偿） |
| 6 | `tofu_state_node.py` | 无需修改（输出的 tcp_target 语义不变） |
| 7 | `tofu_geometry.py` | Phase2右侧prepare逻辑需要修改：A/B改为Z最大两点，l选择base_Z-方向 |
