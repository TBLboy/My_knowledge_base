# 视觉引导预备姿势选择器 - 任务规格书

## 阶段目标

在已有的 `prepare_pose_selector.py` 基础上，增加 ROS 视觉输入模式，使其能够：
1. 订阅视觉感知话题 `/objects_with_pose`
2. 从检测到的豆腐目标中提取 3D 位置
3. 计算 TCP 刀刃中心的预备位置（豆腐上方 surface + 0.05m）
4. 结合已有的双约束姿态求解，找到最优预备关节角
5. 发布到 `/joint_states_remapped`，驱动 RViz 机械臂到达目标姿态

后续切豆腐动作由别的脚本处理，本模块只负责让刀到达正确的预备姿势。

---

## 背景：当前 prepare_pose_selector.py 状态

### 已有功能

| 功能 | 现状 |
|------|------|
| 双约束姿态求解 | ✅ 已完成（tcp_y·base_x=1 + tcp_z 与 XZ 平面夹角） |
| IK 多候选求解 | ✅ 已完成（240 candidates, scipy least_squares） |
| future preview 评分 | ✅ 已完成（path_cost, jump_cost, margin 等） |
| 手部关节发布 | ✅ 已完成（拇指张开/四指折叠） |
| 关节安全限位 | ✅ 已完成（joint_6 ±40° 约束决定了 max plane_angle≈40°） |
| RViz 关节发布 | ✅ 已完成（7 arm + 6 hand joints） |

### 已有参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--x`, `--y`, `--z` | 0.35, 0.10, 0.40 | 目标 TCP 位置 (m) |
| `--plane-angle-deg` | 90.0 | tcp_z 与 XZ 平面夹角 |
| `--candidate-count` | 80 | IK 候选数量 |
| `--preview-steps` | 8 | 下切 preview 步数 |
| `--safety-margin-deg` | 15.0 | 关节安全余量 |
| `--publish-topic` | `/joint_states` | 发布目标关节 topic |
| `--no-rviz` | false | 只计算不发布 |
| `--publish-once` | false | 发布一次后退出 |

### 已有约束

| 约束 | 数学表达 | 说明 |
|------|---------|------|
| 约束1 | `tcp_y · base_x = 1` | TCP Y 轴与 Base X 轴同向（指向"前"） |
| 约束2 | `tcp_z` 与 XZ 平面夹角 = `plane_angle` | tcp_z 与水平面夹角控制下切角度 |

### URDF 链（7 DOF + TCP）

```
world → base → joint_1 → ... → joint_7 → link7 → joint_tcp → link_tcp
                                                           (xyz=0,0,0.097, rpy=0,0,0)
```

### 当前坐标系（双臂版本，Y+ 向上）

| 轴 | 方向 |
|----|------|
| Base X+ | 向前 |
| Base Y+ | 向上 |
| Base Z+ | 向右 |

---

## 视觉感知管线现状

### 数据流

```
RealSense D435i
  ├─ /camera/color/image_raw  →  sam3_detector_node  →  /detected_objects
  │                                                      (ObjectStateArray, 2D masks, frame: camera_optical)
  ├─ /camera/depth/image_raw  ──────────────────────→  pose_estimator_node  →  /objects_with_pose
  │   (CameraInfo)                                                        (ObjectStateArray, 6D pose, frame: base)
  └─ /camera/color/camera_info
```

### /objects_with_pose 消息格式（dexbot_interfaces_mid/ObjectStateArray）

| 字段 | 类型 | 说明 |
|------|------|------|
| `objects[].class_id` | string | 目标类别，如 "tofu" |
| `objects[].pose.position` | geometry_msgs/Point | 目标中心在 base 坐标系下的位置 (m) |
| `objects[].geometric_features` | float[8] | [x, y, w, h, area_px, extX, extY, extZ] — 后3个为 3D 尺寸 (m) |

### 标定结果

- 标定文件：`/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/config1/calibration_result.yaml`
- `T_base_cam`：base → camera_color_optical_frame 变换矩阵
- 输出 pose 已在 base 坐标系下（无需额外 TF 变换）

---

## 任务需求分析

### 用户需求

1. **预备姿势**：刀到达豆腐上方 surface + 0.05m 处，姿势满足双约束
2. **预备姿势驱动 RViz**：发布关节角到 `/joint_states_remapped`，RSP 驱动机械臂
3. **后续切豆腐**：由别的脚本处理，不在本模块范围内

### 关键设计决策（已确认）

| 决策项 | 确认选择 |
|--------|---------|
| 代码组织 | 单文件 + 模式切换（不拆分新节点） |
| 目标点计算 | 基于顶面4顶点几何构造（详见下方"TCP目标点几何算法"） |
| 水平偏移 | `offset_a = 0.03`（3cm，沿顶面内从左到右） |
| 垂直偏移 | `vertical_offset = 0.03`（3cm，高于豆腐顶面） |
| 位置来源 | 订阅 `/objects_with_pose`，取第一个匹配 `class_id` 的目标 |
| 向后兼容 | 无 `--ros-input` 时保持现有 CLI `--x --y --z` 模式 |

---

## 方案设计

### 模式切换逻辑

```python
if args.ros_input:
    # ROS 视觉输入模式
    # 订阅 /objects_with_pose，等待目标，计算 target_xyz
else:
    # CLI 手动输入模式
    # 使用 args.x, args.y, args.z
```

### 新增 CLI 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--ros-input` | store_true | false | 启用 ROS 视觉输入模式 |
| `--ros-input-topic` | str | `/objects_with_pose` | ObjectStateArray 订阅 topic |
| `--ros-input-class` | str | `"tofu"` | 目标类别过滤 |
| `--ros-input-timeout` | float | 5.0 | 等待目标检测超时 (s) |
| `--ros-input-offset-a` | float | 0.03 | 水平偏移量：沿顶面内从左到右偏移 (m) |
| `--ros-input-vertical-offset` | float | 0.03 | 垂直偏移量：高于豆腐顶面的安全间距 (m) |

### VisionTargetReader 类设计

```python
class VisionTargetReader(Node):
    def __init__(self, class_filter: str, offset_a: float, vertical_offset: float):
        super().__init__("vision_target_reader")
        self.class_filter = class_filter
        self.offset_a = offset_a
        self.vertical_offset = vertical_offset
        self.tcp_target = None          # 最终 TCP 目标 (3,)
        self.corners_4 = None           # 顶面4顶点 (4×3)
        self.tofu_extents = None        # 3D 尺寸 (3,)

        self.create_subscription(
            ObjectStateArray,
            "/objects_with_pose",
            self._on_objects,
            qos_profile=10
        )

    def _on_objects(self, msg: ObjectStateArray):
        for obj in msg.objects:
            if obj.class_id == self.class_filter:
                pos = obj.pose.position
                quat = obj.pose.orientation
                ext = obj.geometric_features[5:8]   # (extX, extY, extZ)

                # 重建 OBB 8角点
                corners_8 = self._reconstruct_corners(pos, quat, ext)

                # 取 Y 最大的4个顶点 = 上表面
                sorted_y_idx = np.argsort(corners_8[:, 1])
                self.corners_4 = corners_8[sorted_y_idx[-4:]]

                # 几何算法计算 TCP 目标点
                self.tcp_target = compute_tcp_target_from_corners(
                    self.corners_4,
                    self.offset_a,
                    self.vertical_offset
                )
                self.tofu_extents = np.array(ext)
                break

    def _reconstruct_corners(self, pos, quat, ext):
        """从 pose + extent 重建 OBB 8角点（base坐标系）"""
        extent = np.array(ext)
        half = extent / 2.0
        corners_local = np.array([
            [-half[0], -half[1], -half[2]],
            [+half[0], -half[1], -half[2]],
            [+half[0], +half[1], -half[2]],
            [-half[0], +half[1], -half[2]],
            [-half[0], -half[1], +half[2]],
            [+half[0], -half[1], +half[2]],
            [+half[0], +half[1], +half[2]],
            [-half[0], +half[1], +half[2]],
        ])
        R = R.from_quat([quat.x, quat.y, quat.z, quat.w]).as_matrix()
        position = np.array([pos.x, pos.y, pos.z])
        return corners_local @ R.T + position


def compute_tcp_target_from_corners(corners_4, offset_a=0.03, vertical_offset=0.03):
    """TCP 目标点几何算法（详见上方章节）"""
    top_y = np.mean(corners_4[:, 1])

    sorted_idx = np.argsort(corners_4[:, 2])
    A = corners_4[sorted_idx[0]]
    B = corners_4[sorted_idx[1]]

    if A[0] > B[0]:
        v = A - B
    else:
        v = B - A

    l_raw = np.cross(v, np.array([0.0, 1.0, 0.0]))
    if l_raw[2] < 0:
        l_raw = -l_raw
    l = l_raw / np.linalg.norm(l_raw)

    D = (A + B) / 2.0
    D_prime = D + offset_a * l

    return np.array([D_prime[0], top_y + vertical_offset, D_prime[2]])

### VisionTargetReader 类设计

> 详见上方 `VisionTargetReader` 类完整实现（已在上方章节给出）。

### main() 修改

```python
def main():
    args = parse_args()

    if args.ros_input:
        rclpy.init()
        reader = VisionTargetReader(
            args.ros_input_class,
            args.ros_input_offset_a,
            args.ros_input_vertical_offset
        )
        deadline = time.time() + args.ros_input_timeout
        while time.time() < deadline and reader.tcp_target is None:
            rclpy.spin_once(reader, timeout_sec=0.1)
        if reader.tcp_target is None:
            reader.destroy_node()
            rclpy.shutdown()
            raise RuntimeError(
                f"No '{args.ros_input_class}' detected within "
                f"{args.ros_input_timeout}s on {args.ros_input_topic}"
            )
        target_pos = reader.tcp_target
        reader.destroy_node()
        rclpy.shutdown()
        print(f"[Vision] Detected {args.ros_input_class}")
        print(f"[Vision] top_corners_4 (base): {reader.corners_4.tolist()}")
        print(f"[Vision] tcp_target (base): {target_pos.tolist()}")
    else:
        target_pos = np.array([args.x, args.y, args.z])

    kin = OfflineURDFKinematics(...)
    target_R = build_target_rotation_from_constraints(args.plane_angle_deg)
    # ... 求解、评分、发布
```

### 约束检查输出（ROS 模式）

```python
if args.ros_input:
    print(f"[Vision] tofu_extents: [{ext[0]:.4f}, {ext[1]:.4f}, {ext[2]:.4f}] m")
    print(f"[Vision] top_corners_4 (base): {reader.corners_4.tolist()}")
    print(f"[Vision] left_edge_mid (D): {((A+B)/2).tolist()}")
    print(f"[Vision] tcp_target (base): {target_pos.tolist()}")
```

---

## TCP 目标点几何算法

### 目标

从豆腐上表面4顶点出发，通过几何构造得到 TCP 目标点。最终输出一个 `(x, y, z)` 坐标传入 IK 求解器。

### 算法步骤

**输入**：
- `corners_4`：豆腐上表面4顶点，base 坐标系下 4×3 numpy array
- `offset_a = 0.03`：水平偏移量（m），默认 3cm
- `vertical_offset = 0.03`：垂直偏移量（m），默认 3cm

**步骤 1 - 确定顶面高度**：
```
top_y = mean([p.y for p in corners_4])
```
由于4顶点 Y 坐标理论相等或相差极小，取均值作为顶面高度。

**步骤 2 - 选出左边两个顶点**：
```
sorted_by_z = corners_4[np.argsort(corners_4[:, 2])]
A = sorted_by_z[0]   # Z 最小的点
B = sorted_by_z[1]   # Z 次小的点
```
注意：Z 最小的两个点构成豆腐上表面"左边"那条边（A 在前，B 在后）。

**步骤 3 - 判断 A/B 前后关系，确定方向向量 v**：
```
if A.x > B.x:
    v = A - B    # A 靠前，B 靠后，v 从 B 指向 A
else:
    v = B - A    # B 靠前，A 靠后，v 从 A 指向 B
```
确保 v 是"从后指向前"（即"从豆腐后方向前方向"）。

**步骤 4 - 求顶面内垂直于 v 的方向向量 l**：
```
l_raw = cross(v, [0, 1, 0])   # 右手定则：Y 轴 × v
if l_raw[2] < 0:
    l_raw = -l_raw             # 确保 l 的 Z 分量为正（指向 +Z = 从左到右）
l = normalize(l_raw)
```
几何含义：l 在豆腐上表面平面内（与 base Y 垂直），垂直于左边那条边，方向为从左到右（base Z+）。

**步骤 5 - 求 AB 中点 D**：
```
D = (A + B) / 2.0
```

**步骤 6 - 沿 l 偏移得到 D'**：
```
D_prime = D + offset_a * l
```

**步骤 7 - 确定 TCP 目标坐标**：
```
tcp_target = [D_prime.x, top_y + vertical_offset, D_prime.z]
```
注意：Y 坐标使用 `top_y + vertical_offset`（顶面高度 + 垂直安全间距），而不是 D_prime 的 Y。

### 算法图示（俯视图，Y 轴向上）

```
                    +Z (右)
                     │
                     │
        A(前) ───────┼────────→ l (从左到右)
        │            │          │
        │    D ·───→│D'        │
        │            │  ↑3cm   │
        B(后) ───────┼──────────┘
                     │
                     ▼
                  +X (前)
                  
    刀在 D' 正上方 3cm 处
```

### 完整伪代码

```python
def compute_tcp_target_from_corners(corners_4, offset_a=0.03, vertical_offset=0.03):
    """
    corners_4: 4×3 numpy array, base 坐标系下上表面4顶点
    返回: tcp_target (3,) numpy array
    """
    # 1. 顶面高度
    top_y = np.mean(corners_4[:, 1])

    # 2. Z 最小的两个顶点 = 左边那条边
    sorted_idx = np.argsort(corners_4[:, 2])
    A = corners_4[sorted_idx[0]]
    B = corners_4[sorted_idx[1]]

    # 3. 确定从后向前的方向向量 v（A 靠前）
    if A[0] > B[0]:
        v = A - B   # A 在前
    else:
        v = B - A   # B 在前

    # 4. 求顶面内垂直于 v 的方向 l（右手定则，确保 Z+）
    l_raw = np.cross(v, np.array([0.0, 1.0, 0.0]))
    if l_raw[2] < 0:
        l_raw = -l_raw
    l = l_raw / np.linalg.norm(l_raw)

    # 5. AB 中点
    D = (A + B) / 2.0

    # 6. 沿 l 偏移
    D_prime = D + offset_a * l

    # 7. TCP 目标点（Y = 顶面 + 垂直偏移）
    tcp_target = np.array([
        D_prime[0],
        top_y + vertical_offset,
        D_prime[2]
    ])
    return tcp_target
```

### 特殊情况处理

| 情况 | 处理方式 |
|------|---------|
| 4顶点 Y 坐标相差 > 1cm | 警告，仍取均值 |
| A.x == B.x（v 平行于 Z 轴） | v = `[0, 0, dz]`，cross 后 l = `[±1, 0, 0]`，取 Z+ 侧 |
| `offset_a = 0` | D_prime = D，TCP 在左边线段中点正上方 |
| `vertical_offset = 0` | TCP 落在豆腐顶面上（刀尖接触） |

### 与旧方案对比

| 项目 | 旧方案 | 新方案 |
|------|--------|--------|
| Y 计算 | `tofu_y + extY + offset` | `top_y(来自4顶点) + vertical_offset` |
| XZ 计算 | 直接用 `tofu_x, tofu_z` | 从4顶点几何构造偏左中点 |
| 偏移动作 | 无 | 沿顶面内垂线方向偏移 |

---

## 预备姿势几何关系

### 坐标系

```
base_X (前), base_Y (上), base_Z (右)
```

### 刀刃预备位置示意（侧视图）

```
              刀刃 (tcp)
                 │
                 │ vertical_offset = 0.03m
                 ▼
    ┌─────────────────────┐  ← 豆腐上表面 (top_y)
    │                     │
    │      豆腐块         │
    │                     │
    └─────────────────────┘  ← 豆腐下表面
```

### 计算公式

```
tcp_x = D_prime.x
tcp_y = top_y + vertical_offset
tcp_z = D_prime.z
```

---

## 不在本阶段范围内的内容

| 事项 | 说明 |
|------|------|
| SAM3 prompt 修改 | 需改为 "tofu" 或对应中文，将在 launch 或参数中处理 |
| 切豆腐动作执行 | 由别的脚本处理（demo_cut_tofu_xcore_ros.py 等） |
| 多目标选择 | 先只取第一个匹配目标 |
| 实时跟随 | 当前为单次检测，非连续跟踪 |
| 抓取规划 | 不在本模块 |

---

## 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `prepare_pose_selector.py` | 新增 `VisionTargetReader` 类、5个 CLI 参数、`main()` ros-input 分支 |

---

## 验证计划

### 1. 编译检查
```bash
python3 -m py_compile src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py
```

### 2. ROS 模式单元测试（模拟 /objects_with_pose）

启动 RViz：
```bash
ros2 launch ar5_dual_arm_bringup dual_display.launch.py \
  use_joint_gui:=false enable_realsense:=false enable_aruco:=false \
  right_hand_mount_xyz:="0 0 0" \
  right_hand_mount_roll:=0 right_hand_mount_pitch:=0 right_hand_mount_yaw:=0
```

模拟目标检测（使用 `ros2 topic pub` 或测试脚本）：
```bash
# 使用 ROS2 topic pub 模拟发送 /objects_with_pose
ros2 topic pub /objects_with_pose dexbot_interfaces_mid/ObjectStateArray '{objects: [{class_id: "tofu", pose: {position: {x: 0.3, y: 0.0, z: 0.3}}, geometric_features: [0, 0, 0, 0, 0, 0.08, 0.03, 0.08]}]}'
```

### 3. 端到端验证

启动 RealSense + SAM3 + PoseEstimator：
```bash
ros2 launch ar5_dual_arm_bringup dual_display.launch.py \
  use_joint_gui:=false enable_realsense:=true enable_aruco:=false
```

运行脚本：
```bash
python3 src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py \
  --ros-input \
  --ros-input-class tofu \
  --ros-input-timeout 10.0 \
  --plane-angle-deg 40 \
  --candidate-count 240 \
  --preview-steps 15 \
  --publish-topic /joint_states_remapped
```

验证：
- RViz 中机械臂到达豆腐上方预备位置
- 法兰 Z 轴朝向正确（tcp_z 与 XZ 平面夹角 = plane_angle）
- 手部拇指张开/四指折叠
- 关节未超出安全限位

---

## 风险与限制

| 风险 | 影响 | 缓解 |
|------|------|------|
| geometric_features 单位不确定（m vs mm） | OBB 角点重建错误 | 在打印中确认 extent 数值合理性（豆腐应约 0.08×0.04×0.08m） |
| 豆腐检测不到 | 脚本超时退出 | `--ros-input-timeout` 可调 |
| 偏移量不合适 | 刀偏左/偏高/偏低 | 通过 `--ros-input-offset-a` 和 `--ros-input-vertical-offset` 调整 |
| 4顶点 Y 坐标相差大 | 顶面高度计算不准确 | 警告仍取均值，需确认豆腐放置水平 |
| SAM3 prompt 非 "tofu" | 检测不到目标 | 需在 launch 或 sam3_detector_node 参数中设置 |
| 豆腐放置歪斜（不轴对齐） | l 方向有微小偏差 | 算法有兜底处理，但仍应尽量水平放置 |

---

## 边对齐约束（Edge-Aligned Constraint）

### 动机

默认约束1 `tcp_y · base_x = 1` 假设豆腐放置得完全轴对齐，即豆腐左边 AB 平行于 base X 轴。实际豆腐很难放置得如此端正。此功能允许 TCP Y 轴方向跟随豆腐实际放置方向，使刀脊平行于豆腐边。

### 触发方式

新增 CLI 参数 `--edge-align`（store_true），仅在 `--ros-input` 模式下有效。

| 条件 | 行为 |
|------|------|
| `--ros-input --edge-align` | 使用豆腐左边 AB 方向作为 tcp_y 方向 |
| `--ros-input` 无 `--edge-align` | 使用默认约束 `tcp_y = base_x = [1,0,0]` |
| `--edge-align` 无 `--ros-input` | 警告并回退到默认约束 |

### edge_dir 向量定义

```
edge_dir = normalize(v)
v = A - B (当 A.x > B.x 时) 或 v = B - A (当 B.x > A.x 时)
```

其中 A 和 B 是豆腐上表面 Z 最小的两个顶点（左边那条边），v 方向从后指向前。edge_dir 的 Y 分量强制设为 0（豆腐上表面是水平面，左边在其上，方向向量 Y 应为 0）。

```
edge_dir = (e_x, 0, e_z),  |edge_dir| = 1
```

### 广义旋转矩阵推导

设 `edge_dir = (e_x, 0, e_z)`，定义水平垂线 `n = edge_dir × Y = (-e_z, 0, e_x)`。

```
tcp_y = edge_dir = [e_x, 0, e_z]
tcp_z = cos(α)·n - sin(α)·Y = [-e_z·cos(α), -sin(α), e_x·cos(α)]
tcp_x = tcp_y × tcp_z = [e_z·sin(α), -cos(α), -e_x·sin(α)]
```

旋转矩阵 `R = [tcp_x | tcp_y | tcp_z]`：

```
    | e_z·sin(α)        e_x      -e_z·cos(α) |
R = | -cos(α)           0        -sin(α)      |
    | -e_x·sin(α)       e_z       e_x·cos(α) |
```

**验证**：
- 行列式：`sin²(α)·(e_x²+e_z²) + cos²(α) = 1` ✓
- 正交性：`tcp_x × tcp_y = tcp_z` ✓
- 退化检查：当 `edge_dir = [1,0,0]`（e_x=1, e_z=0），退化为默认矩阵 `[0,-cos,-sin; 1,0,0; 0,-sin,cos]` ✓

### 数据流

```
VisionTargetReader._on_objects()
  ├─ compute_tcp_target_from_corners() → (tcp_target, edge_dir_norm)
  │                                      edge_dir_norm = normalize(v), Y=0
  │
  └─ 存储 self.tcp_target, self.edge_dir

main()
  ├─ if --edge-align and --ros-input:
  │     edge_dir = reader.edge_dir
  ├─ else:
  │     edge_dir = None
  │
  └─ target_R = build_target_rotation_from_constraints(plane_angle_deg, edge_dir)
```

### 代码改动清单（prepare_pose_selector.py）

| # | 函数/位置 | 改动 |
|---|----------|------|
| 1 | `build_target_rotation_from_constraints()` 第74行 | 增加 `edge_dir=None` 参数。非 None 时使用广义公式 `R = [e_z*s, e_x, -e_z*c; -c, 0, -s; -e_x*s, e_z, e_x*c]`；为 None 时使用默认 |
| 2 | `compute_tcp_target_from_corners()` 第202行 | 返回值改为 `(tcp_target, edge_dir_norm)`：v_norm = v/|v|，强制 Y=0 后重新归一化 |
| 3 | `VisionTargetReader._on_objects()` | 解包 `tcp_target, edge_dir = compute_tcp_target_from_corners(...)`，存储 `self.edge_dir` |
| 4 | `parse_args()` | 新增 `--edge-align`（store_true） |
| 5 | `main()` 第473-474行 | 根据 `args.edge_align` 和 `args.ros_input` 组合决定 pass `edge_dir` 或 `None` |
| 6 | `print_final_report()` 第427-429行 | 当 `edge_dir is not None` 时，打印 `tcp_y dot edge_dir` 代替 `tcp_y dot base_X` |

### 验证输出示例

```
[Vision] edge_dir (base): [0.999, 0.000, 0.043]  ← 豆腐有微小旋转
constraint check:
  tcp_y dot edge_dir: 0.99999998   ← 刀脊与豆腐边平行 ✓
  actual plane angle deg: 40.000
```
