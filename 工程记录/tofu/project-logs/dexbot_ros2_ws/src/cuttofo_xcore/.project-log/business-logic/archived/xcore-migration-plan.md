# xCore 迁移方案

> 创建日期: 2026-05-11
> 状态: 已完成分析，待实施
> 基于: Lbot Phase 2 框架 (cuttofo_lbot) → xCore (cuttofo_xcore)

---

## 1. 概述

将 Lbot 机械臂上的 Phase 2 视觉引导切豆腐框架迁移到 xCore 机械臂。Lbot Phase 2 已完成端到端实测验证（2026-05-10），xCore 需复用其核心逻辑并适配差异。

### 核心差异概览

| 方面 | Lbot | xCore |
|------|------|-------|
| 坐标系 | Z↑(上), X→(前), Y←(左) | Y↑(上), X→(前), Z→(右) |
| 欧拉角约定 | ZYX 外旋（需 swap） | XYZ 内旋（直接对应） |
| 控制方式 | TCP SDK 直调 (`LbotRobot`) | ROS2 Service (`xcore_controller_node`) |
| IK 求解 | SDK 内置（黑盒，单候选） | URDF + scipy `least_squares`（多候选） |
| 到位确认 | 轮询关节角 | Action Result + 可选 Service |
| 关节数量 | 7 DOF | 7 DOF (AR5-5_07R-W4C1C1) |

---

## 2. 坐标系映射

### 2.1 轴映射关系

```
Lbot → xCore:
  X_l (前) → X_x (前)      [直接对应]
  Y_l (左) → -Z_x (左)     [方向反转]
  Z_l (上) → Y_x (上)      [轴名互换]

矩阵映射:
  R_lbot_to_xcore = [[1,  0,  0],
                     [0,  0, -1],
                     [0,  1,  0]]
```

### 2.2 对 tofu_geometry.py 各函数的影响

| 函数 | Lbot (Z↑) | xCore (Y↑) |
|------|-----------|-------------|
| `extract_top_corners` | `corners_8[:, 2]` 取最大 | `corners_8[:, 1]` 取最大 |
| `compute_edge_dir` | `sorted_idx = argsort(corners_4[:, 1])` | `sorted_idx = argsort(corners_4[:, 2])` |
| `compute_tcp_target_from_corners` | `top_z = corners_4[:, 2]` | `top_y = corners_4[:, 1]` |
| | cross(v, [0,0,1]) 垂直到 XY | cross(v, [0,1,0]) 垂直到 XZ |
| `build_target_rotation_from_constraints` | 见 3.1 | 见 3.2 |
| `build_rotation_with_edge_dir` | 基于 Z↑ 构建 | 基于 Y↑ 重构 |

---

## 3. 欧拉角约定

### 3.1 Lbot: ZYX 外旋

- scipy: `R.from_euler("ZYX", [rz, ry, rx]).as_euler("ZYX")` → `[rz, ry, rx]`
- LbotEuler: `LbotEuler(x=roll, y=pitch, z=yaw)`
- **映射 bug**: Lbot SDK 返回 `[rz, ry, rx]`，需 swap 为 `[rx, ry, rz]` 才能给 `LbotEuler(x, y, z)`
- 代码: `LbotEuler(eul[2], eul[1], eul[0])`

### 3.2 xCore: XYZ 内旋（等价 ZYX 外旋）

- scipy: `R.from_euler("xyz", [rx, ry, rz]).as_euler("xyz")` → `[rx, ry, rz]`
- `LbotEuler.x` = roll, `LbotEuler.y` = pitch, `LbotEuler.z` = yaw
- **直接对应，无需 swap**
- 整个 xCore 代码库统一使用 `from_euler("xyz")` / `as_euler("xyz")`
- 证明: `math_utils.py` 注释 "LBot API 使用 XYZ 内旋欧拉角（等价于 ZYX 外旋）"

### 3.3 `rotation_to_euler` 函数

```python
# Lbot (需 swap)
def rotation_to_euler(R_mat, convention="ZYX"):
    eul = Rotation.from_matrix(R_mat).as_euler(convention)
    return np.array([eul[2], eul[1], eul[0]])  # swap!

# xCore (直接)
def rotation_to_euler(R_mat, convention="xyz"):
    return Rotation.from_matrix(R_mat).as_euler(convention)  # 无需 swap
```

---

## 4. 旋转矩阵差异

### 4.1 `build_target_rotation_from_constraints`

**Lbot** (`tofu_geometry.py:77`):
```python
def build_target_rotation_from_constraints(plane_angle_deg: float = 40.0) -> np.ndarray:
    alpha = np.deg2rad(plane_angle_deg)
    flange_x = np.array([1.0, 0.0, 0.0])           # 刀脊 = base X
    flange_y = np.array([0.0, np.sin(alpha), np.cos(alpha)])
    flange_z = np.array([0.0, -np.cos(alpha), np.sin(alpha)])  # Z轴与XY平面夹角
    return np.column_stack([flange_x, flange_y, flange_z])
```

**xCore** (`prepare_pose_selector.py:74`，经多轮修正验证):
```python
def build_target_rotation_from_constraints(plane_angle_deg=90.0):
    alpha = np.deg2rad(plane_angle_deg)
    x_axis = np.array([0.0, -np.cos(alpha), -np.sin(alpha)])
    y_axis = np.array([1.0, 0.0, 0.0])            # 刀脊 = base X
    z_axis = np.array([0.0, -np.sin(alpha), np.cos(alpha)])  # Z轴与XZ平面夹角
    return np.column_stack([x_axis, y_axis, z_axis])
```

**约束含义**:
- `tcp_y · base_x = 1`（刀脊沿 base X 方向）
- `tcp_z` 与 base YZ 平面夹角 = `plane_angle`
- joint_6 安全限位 ±40° → plane_angle 最大 ≈ 40-45°

### 4.2 `build_rotation_with_edge_dir`

xCore 版本需用 edge_dir 重构旋转矩阵：
```python
def build_rotation_with_edge_dir(plane_angle_deg: float, edge_dir: np.ndarray) -> np.ndarray:
    # edge_dir: 豆腐边缘方向向量（归一化，Y=0 in xCore base）
    # 构建 tcp_y = edge_dir, tcp_z 满足 plane_angle 约束
    ...
```

---

## 5. ROS 架构

### 5.1 控制接口对比

| 功能 | Lbot | xCore |
|------|------|-------|
| 连接 | `LbotRobot(ip).connect()` | ROS2 Service (`xcore_controller_node`) |
| 获取状态 | `robot.get_cartesian_pose()` | `/arm_r/robot/get_state` → `GetRobotState` |
| 关节运动 | `robot.move_to_joint_target()` | `/arm_r/robot/move_joints` → `MoveJoints` |
| 直线运动 | `robot.linear_move_to_pose()` | `/robot/move_cartesian` → `MoveCartesian` |
| IK 求解 | `robot.compute_inverse_kinematics()` | URDF + scipy `least_squares` |
| FK | `robot.compute_forward_kinematics()` | `OfflineURDFKinematics.fk_matrix()` |
| RT 切削 | 无 | `/arm_r/robot/move_rt_cartesian_segment` |

### 5.2 xCore ROS Service 接口

```
Namespace: /arm_r (右臂)

/arm_r/robot/get_state          (GetRobotState)
    Request:  empty
    Response: success, message, cartesian_pose (Pose)

/arm_r/robot/move_joints       (MoveJoints)
    Request:  target_joints[7], speed, accel, block
    Response: success, message

/arm_r/robot/move_rt_cartesian_segment  (MoveRtCartesianSegment)
    Request:  target_pose (Pose), duration_s, speed_scale, ...
    Response: success, message, executed_steps, elapsed_s

/robot/move_cartesian          (MoveCartesian) — 注意无 namespace 前缀
    Request:  target_pose (Pose), speed, accel
    Response: success, message
```

### 5.3 命名空间注意事项

- xCore demo 使用 `DEFAULT_NAMESPACE = "/arm_r"`
- RViz 双臂启动时 joint_states 话题为 `/joint_states_remapped`
- 单臂调试时为 `/joint_states`

---

## 6. 模块迁移分类

### 6.1 可直接复用（平台无关）

| 源文件 | 目标 | 说明 |
|--------|------|------|
| `cuttofo_lbot_interfaces/msg/TofuState.msg` | 复用 | 平台无关的消息定义 |
| `cuttofo_lbot_interfaces/action/MoveToPreparePose.action` | 复用 | 平台无关的 Action 定义 |
| `cuttofo_lbot/cuttofo_lbot/tofu_state_node.py` | `cuttofo_xcore/cuttofo_xcore/tofu_state_node.py` | 订阅+发布逻辑通用，需适配 tofu_geometry 调用 |
| `cuttofo_lbot/cuttofo_lbot/tofu_cut_coordinator_node.py` | 同名 | 状态机逻辑通用，需改 Action/Service 调用 |

### 6.2 需新建（xCore 特有）

| 新文件 | 说明 | 参考 |
|--------|------|------|
| `cuttofo_xcore/cuttofo_xcore/tofu_geometry.py` | 几何函数 Y↑ 适配版 | Lbot `tofu_geometry.py` + xCore `prepare_pose_selector.py` |
| `cuttofo_xcore/cuttofo_xcore/xcore_arm_adapter.py` | ROS2 Service 封装 | Lbot `lbot_arm_adapter.py` + `demo_cut_tofu_xcore_ros.py` |
| `cuttofo_xcore/cuttofo_xcore/knife_prepare_action_server.py` | Action Server | Lbot 同名文件，替换 arm_adapter + IK 逻辑 |
| `cuttofo_xcore/launch/cuttofo_phase2.launch.py` | 启动文件 | Lbot `cuttofo_phase2.launch.py` |

### 6.3 xCore 已有，保留不动

| 文件 | 说明 |
|------|------|
| `cuttofo_xcore/cuttofo_xcore/offline_urdf_kinematics.py` | URDF FK 引擎 ✅ |
| `cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py` | 离线 IK 调试工具 ✅ |
| `cuttofo_xcore/cuttofo_xcore/demo_cut_tofu_xcore_ros.py` | RT 切削核心逻辑参考 ✅ |

### 6.4 Lbot 特有，迁移后归档

| 文件 | 说明 |
|------|------|
| `cuttofo_lbot/cuttofo_lbot/lbot_arm_adapter.py` | 迁移后不再使用 |
| `cuttofo_lbot/cuttofo_lbot/m51_test_euler_convention.py` | 仅用于 Lbot 验证 |
| `cuttofo_lbot/cuttofo_lbot/test_axis_move.py` | 仅用于 Lbot 验证 |
| `cuttofo_lbot/cuttofo_lbot/test_pose_constraint.py` | 仅用于 Lbot 验证 |

---

## 7. 迁移步骤

### M1: 创建 xCore 版 tofu_geometry.py

**输入**: Lbot `tofu_geometry.py` + xCore `prepare_pose_selector.py:74-82`

**改动**:
1. `extract_top_corners`: `[:, 2]` → `[:, 1]`
2. `compute_edge_dir`: `[:, 1]` → `[:, 2]`，cross 参考轴 `[0,1,0]` → `[0,1,0]`（xCore Y-up）
3. `compute_tcp_target_from_corners`: `top_z` → `top_y`，cross 参考轴 `[0,0,1]` → `[0,1,0]`
4. `build_target_rotation_from_constraints`: **完全替换**为 xCore 版本
5. `build_rotation_with_edge_dir`: 基于 xCore Y-up 重新推导
6. `rotation_to_euler`: 默认 convention `"xyz"`（无需 swap）

**验证**: 单元测试，坐标映射正确性。

### M2: 创建 xcore_arm_adapter.py

**输入**: Lbot `lbot_arm_adapter.py` + `demo_cut_tofu_xcore_ros.py` + `xcore_controller_node.py` Service 定义

**接口设计**:
```python
class XcoreArmAdapter:
    def __init__(self, namespace: str = "/arm_r"):
        self._namespace = namespace
        # 创建 ROS2 Service clients: GetRobotState, MoveJoints, MoveCartesian
        ...

    def connect(self, timeout: float) -> bool:
        # xCore 无需 connect，Service 自动可用
        # 验证 Service 可用性
        ...

    def solve_ik(self, target_pos, target_eul, seed_joints, num_retries) -> Optional[np.ndarray]:
        # 使用 OfflineURDFKinematics + scipy least_squares
        # 参考 prepare_pose_selector.py 的多候选 IK 逻辑
        ...

    def compute_fk(self, joints) -> Optional[Tuple]:
        # 使用 OfflineURDFKinematics.fk_matrix()
        ...

    def move_to_joints(self, target_joints, speed, accel, block) -> bool:
        # 调用 /arm_r/robot/move_joints Service
        ...

    def get_joints(self) -> Optional[np.ndarray]:
        # 调用 /arm_r/robot/get_state → 解析关节角
        ...

    def get_pose(self) -> Optional[Tuple[Tuple, Tuple]]:
        # 调用 /arm_r/robot/get_state → 解析 cartesian_pose
        # 返回 (pos, eul_xyz)
        ...

    def verify_arrival(self, target_joints, tolerance_deg, timeout_s) -> Tuple[bool, float]:
        # 轮询 get_joints() 直到误差 < tolerance 或超时
        ...
```

**关键实现细节**:
- `target_eul` 输入为 `[rx, ry, rz]`（scipy XYZ convention），直接构建 `LbotEuler(rx, ry, rz)` 给 Service
- `get_pose` 返回的 euler 已是 `[rx, ry, rz]` 格式（xCore Service 返回值）
- Service 调用使用 `rclpy` 同步方式

### M3: 创建 knife_prepare_action_server.py（xCore 版）

**输入**: Lbot `knife_prepare_action_server.py`

**改动点**:
1. `from cuttofo_lbot.lbot_arm_adapter import LbotArmAdapter` → `from cuttofo_xcore.xcore_arm_adapter import XcoreArmAdapter`
2. `tofu_geometry` import 改为 xCore 版
3. IK 调用: `arm.solve_ik()` — xCore 版使用 URDF+scipy，接口相同
4. 运动调用: `arm.move_to_joints()` — xCore 版使用 ROS Service
5. 参数命名可保持兼容

**步骤逻辑（8步）**: 连接 → 等待 tofu_state → 构建目标 → IK → FK验证 → 移动 → 到位验证 → 返回

### M4: 创建 tofu_state_node.py（xCore 版）

**输入**: Lbot `tofu_state_node.py`

**改动点**:
1. import `tofu_geometry` 改为 xCore 版
2. 几何计算使用 Y↑ 坐标轴（已在 tofu_geometry.py 中适配）
3. 其他逻辑（订阅 `/objects_with_pose`、EMA 平滑、发布 `/tofu_state`）完全不变

### M5: 创建 tofu_cut_coordinator_node.py（xCore 版）

**输入**: Lbot `tofu_cut_coordinator_node.py`

**改动点**:
1. Action 类型 import 保持不变（`cuttofo_lbot_interfaces` 复用）
2. Action Client 目标话题: `/move_to_prepare_pose`（同 Lbot）
3. Phase 3 RT 切削集成: 调用 `/arm_r/robot/move_rt_cartesian_segment` Service
   - 参考 `demo_cut_tofu_xcore_ros.py` 的 `TofuCutRosClient` 逻辑
4. 参数保持兼容

### M6: 创建 launch 文件

**输入**: Lbot `launch/cuttofo_phase2.launch.py`

**改动点**:
1. 包名: `cuttofo_lbot` → `cuttofo_xcore`
2. 节点:
   - `tofu_state_node`
   - `knife_prepare_action_server`
   - `tofu_cut_coordinator_node`
3. 参数配置兼容
4. log 分离设置保留

---

## 8. 文件映射表

| Lbot 源文件 | xCore 目标文件 | 操作 |
|------------|----------------|------|
| `cuttofo_lbot_interfaces/msg/TofuState.msg` | `cuttofo_lbot_interfaces/msg/TofuState.msg` | **复用**（不动） |
| `cuttofo_lbot_interfaces/action/MoveToPreparePose.action` | `cuttofo_lbot_interfaces/action/MoveToPreparePose.action` | **复用**（不动） |
| `cuttofo_lbot/cuttofo_lbot/tofu_geometry.py` | `cuttofo_xcore/cuttofo_xcore/tofu_geometry.py` | **重写**（坐标轴适配） |
| `cuttofo_lbot/cuttofo_lbot/lbot_arm_adapter.py` | `cuttofo_xcore/cuttofo_xcore/xcore_arm_adapter.py` | **新建**（ROS Service 封装） |
| `cuttofo_lbot/cuttofo_lbot/knife_prepare_action_server.py` | `cuttofo_xcore/cuttofo_xcore/knife_prepare_action_server.py` | **重写**（基于 xcore_arm_adapter） |
| `cuttofo_lbot/cuttofo_lbot/tofu_state_node.py` | `cuttofo_xcore/cuttofo_xcore/tofu_state_node.py` | **重写**（import 路径改） |
| `cuttofo_lbot/cuttofo_lbot/tofu_cut_coordinator_node.py` | `cuttofo_xcore/cuttofo_xcore/tofu_cut_coordinator_node.py` | **重写**（RT Service 集成） |
| `cuttofo_lbot/launch/cuttofo_phase2.launch.py` | `cuttofo_xcore/launch/cuttofo_phase2.launch.py` | **新建**（包名+节点路径改） |
| `cuttofo_xcore/cuttofo_xcore/offline_urdf_kinematics.py` | 同上 | **保留不动** |
| `cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py` | 同上 | **保留不动**（离线调试） |
| `cuttofo_xcore/cuttofo_xcore/demo_cut_tofu_xcore_ros.py` | 同上 | **保留不动**（RT 参考） |

---

## 9. 关键技术细节

### 9.1 xCore 欧拉角字段映射

```
LbotEuler.x = roll  (rx, 绕 X 轴旋转)
LbotEuler.y = pitch (ry, 绕 Y 轴旋转)
LbotEuler.z = yaw   (rz, 绕 Z 轴旋转)

scipy: R.from_euler("xyz", [rx, ry, rz]) → R = Rz(rz) * Ry(ry) * Rx(rx)
```

### 9.2 plane_angle 与 joint_6 限位

| plane_angle | tcp_z 在 base 中的方向 | joint_6 需求 |
|-------------|----------------------|--------------|
| 30° | 向下倾斜 30° | ✅ 安全 |
| 40° | 向下倾斜 40° | ✅ 边界可解 |
| 50° | 向下倾斜 50° | ❌ 超限 |
| 90° | 垂直向下 | ❌ 绝对超限 |

**最大可行 plane_angle ≈ 40-45°**（joint_6 安全限位 ±40°）

### 9.3 URDF 关键参数

```
URDF: ar5_07r_w4c1c1_description/urdf/AR5-5_07R-W4C1C1.urdf
base_link: AR5-5_07R-W4C1C1_base
tip_link:  AR5-5_07R-W4C1C1_link_tcp
关节名:    AR5-5_07R-W4C1C1_joint_1 ~ joint_7
TCP 偏移:  joint_tcp (fixed, xyz=0,0,0.097)
```

---

## 10. 风险与待确认

| 风险 | 影响 | 缓解 |
|------|------|------|
| xCore URDF 与实际机械手安装可能存在微小差异 | IK 精度 | 端到端验证测试 |
| `/joint_states_remapped` 在无机械臂时无发布源 | 离线调试时 prepare_pose_selector 无法获取当前关节角 | 使用 q_home fallback |
| hand-eye calibration 未完成 | 相机-to-base 变换未知 | 使用已有标定结果 `calibration_result.yaml` |
| 迁移后关节运动速度/加减速参数需调优 | 运动平滑性 | launch 参数可配 |

---

## 11. 实施优先级

```
P0 (核心): M1 → M2 → M3 → M6  (tofu_geometry → arm_adapter → action_server → launch)
P1 (节点): M4 → M5              (tofu_state_node → coordinator)
P2 (验证): 端到端测试            (感知 → 就位 → 切削)
```
