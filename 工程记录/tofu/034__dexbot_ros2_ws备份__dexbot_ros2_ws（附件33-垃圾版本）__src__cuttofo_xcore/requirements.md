# Requirements

## Project Summary

- Goal: Build a robotic arm grasping pipeline using SAM3 segmentation + geometric 6D pose estimation for a tofu/food cutting task
- Users: TBL (operator)
- Current stage: **Perception pipeline COMPLETE; cutting motion planning in design phase**
- Workspace: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/cuttofo_xcore`

## Task Scope

- In scope:
  - SAM3 segmentation integration with RealSense camera ✅ (verified working)
  - Geometric 6D pose estimation from SAM3 mask + depth (PCA-based OBB) ✅ (verified working)
  - ROS2 pipeline: camera → SAM3 → pose_estimator → /objects_with_pose ✅ (verified)
  - 6D pose visualization overlay in camera_viewer_node ✅ (implemented)
  - EMA exponential smoothing for pose jitter reduction ✅ (implemented)
  - **Cutting motion planning** (implemented, Phase7 verified)
  - Integration with existing cuttofo_xcore motion control demos ✅ (implemented)
  - **Phase1 grab-knife migration**: Migrate classmate's grab-knife code into cuttofo_xcore (in design)
- Out of scope:
  - Hand-eye calibration: Existing calibration_result.yaml in use; re-calibration deferred
  - Deep learning 6D pose estimation (FoundationPose/Uni6D)
  - Force/impedance control details
  - Actual gripper hardware

## Constraints

- ROS2 / ament_python packages
- xCore/Lbot backend (NOT xbot backend)
- ROS_DOMAIN_ID=13
- RealSense D435I camera
- SAM3 model at `/home/tbl/Project/models/sam3`
- Camera topics: RealSense publishes under `/camera/camera/...` prefix
- Workspace path: `~/Project/dexbot_ros2_ws`
- Desktop workspace at `/home/tbl/桌面/dexbot_ros2_ws` contains full hand-eye calibration toolchain (separate copy)
- **Classmate's grab-knife workspace**: `/home/tbl/桌面/dexbot_ros2_ws` (latest version)
- **Demo deployment**: 3 terminals — (1) controller node, (2) Phase1 monitor, (3) classmate's grab-knife one-lifecycle

## Key Decisions

### Perception & Cutting
- 6D pose method: SAM3 mask + depth → PCA-based OBB (vision_utils.py)
- Text prompt for SAM3: supports Chinese natively — "豆腐", "tomato", "orange", "cup", or any text (configurable at runtime)
- Calibration file: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/config/calibration_result.yaml` (T_base_cam: translation=[0.125, -0.006, -0.076]m, RPY=[-16.87°, 88.71°, 39.53°])
- Camera mount: Eye-to-hand (fixed external camera) — confirmed
- Hand-eye calibration: Using existing calibration; re-calibration toolchain available in desktop workspace
- Mask/depth resolution mismatch: Fixed via cv2.resize in vision_utils.py (RGB 1280x720 vs Depth 848x480)
- camera_viewer_node overlay: Yellow OBB box + red principal axis arrow (PCA longest axis) + white size text; T_cam_base loaded from calibration_file param
- Pose smoothing: EMA exponential smoothing with slerp for quaternions; alpha=0.4 default; per-object cache by obj_id

### Phase1 Grab-Knife Migration (2026-05-19)
- **Migration source**: Classmate's workspace `/home/tbl/桌面/dexbot_ros2_ws` (latest version with full 3-phase logic)
- **Migration target**: `src/dexbot_middle_layer/CutTofo/` under `/home/tbl/Project/tofu/dexbot_ros2_ws`
- **Principle**: Code migration only, zero logic changes; classmate's code already verified working; independent runtime environment
- **Completion signal**: `/task/phase1_complete` (classmate's native topic), replaces `/knife_grabbed`
- **Lifecycle**: One-lifecycle wrapper node launches recognition + monitor + follow nodes → auto-executes grab → cleans up resources → broadcasts `/task/phase1_complete` → self-exits
- **Resource cleanup**: xCore SDK disconnect → O6 CAN close → ROS destroy_node + shutdown → process exit confirmation
- **Phase1 monitor**: Buffers 0.5s after receiving `/task/phase1_complete` before launching Phase2
- **Demo deployment**: 3 terminals — (1) controller node, (2) Phase1 monitor, (3) one-lifecycle grab-knife
- **SAM3 prompt handling — NO switching needed**:
  - Classmate's code may switch SAM3 prompts internally during grab (Phase1: "wooden cleaver handle", Phase2: "wooden knife box; ridged tofu"), but this only matters if classmate's lifecycle includes its own SAM3 node
  - After grab-knife lifecycle exits, `cuttofu_phase2.launch.py` launches a **brand-new** `sam3_detector_node` with `text_prompt="豆腐"` (hardcoded in launch file from config `class_filter`)
  - Process isolation guarantees clean state: classmate's subprocess death = all its nodes die = no residual prompt state
  - **Do NOT add prompt switching logic**: would require modifying classmate's verified code; our SAM3 node doesn't support multi-prompt syntax; adds unnecessary settle time and failure modes
  - **Terminal 1 (vision stack)**: If classmate's lifecycle includes launching vision_stack (RealSense + SAM3), it exits cleanly with the lifecycle. If Terminal 1 runs vision_stack independently, the SAM3 node persists but receives new prompt from Phase2's fresh launch — no conflict either way

## Cutting Task Design

### Overall Flow

```
阶段0: 右手拿刀 (假设已完成)
阶段1: 斜着切豆腐 (当前工作重点)
阶段2: 竖着切豆腐 (暂不考虑)
```

### Base Coordinate System Orientation (IMPORTANT)

| 轴 | 方向 | 说明 |
|---|---|---|
| base X | 左右 | 横向 |
| base Y | 上下（数值方向） | 垂直方向 |
| **base Z** | **前后（向前）** | **刀脊方向** |

### Stage 1: Oblique Cutting (斜切)

#### Knife Pose Constraints

**Constraint 1: Knife Spine Direction (刀脊方向)**
```
法兰盘 X轴正方向 · base Z轴正方向 = 1  (点积为1，同向)
```
- 法兰 X轴（刀脊）‖ base Z轴（向前）
- 刀脊"笔直向前"，沿 base Z 轴

**Constraint 2: Knife Tilt Angle (刀面倾斜角度)**
- 刀面法向量（法兰 Z轴）与 base XZ 平面之间的线面角
- **可调参数**：`knife_tilt_angle`（用户设定，范围 0° ~ 90°）
  - 0° = 刀面 ⊥ 案板（垂直，正常切菜姿态）
  - 90° = 刀面 ‖ 案板（平行，躺平）
- 倾斜旋转轴 = 法兰 Y轴（刀刃方向）

#### Knife Pose Description

**Normal cutting pose (0° 倾斜)**:
- 刀面 ⊥ 案板 (面面垂直)
- 刀脊 ‖ base Z轴 (向前)

**Oblique cutting pose (斜切)**:
- 刀面与案板之间的面面角 = `knife_tilt_angle`
- 刀脊依然 ‖ base Z轴 (向前)
- 整个刀绕着**刀刃方向（法兰 Y轴）**旋转了 `knife_tilt_angle`

#### Key Geometric Relationship

```
机械臂法兰坐标系 Z轴正方向 ‖ 刀面 (线面平行)
法兰坐标系 X轴正方向 ‖ base Z轴正方向 (向前)
```

这意味着:
- 法兰 Z轴 = 刀面法向量
- 法兰 X轴 = 刀脊方向 = base Z轴方向

#### Reference Implementation: demo_adjust_knife_pose_xcore.py

**文件**: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/cuttofo_xcore/cuttofo_xcore/demo_adjust_knife_pose_xcore.py`

**核心函数**: `build_target_rotation()` (第 340-447 行)

从两个约束构建目标法兰姿态：

**约束 1: 线面角 (line-plane angle)**
- `constraint_axis`: 参与约束的法兰轴 (x/y/z)
- `plane_angle_deg`: 该轴与基准平面的线面角（度）
- 基准平面 = base XZ 平面

**约束 2: 轴平行 (axis parallel)**
- `parallel_flange_axis`: 法兰坐标系中要平行的轴 (x/y/z)
- `parallel_base_axis`: base坐标系中要平行的轴 (x/y/z)

**默认参数**:
```python
DEFAULT_CONSTRAINT_AXIS = "z"           # 法兰 Z 轴参与线面角
DEFAULT_PLANE_AXIS_1 = "x"            # 基准平面由 x
DEFAULT_PLANE_AXIS_2 = "z"            # 和 z 组成
DEFAULT_PLANE_ANGLE_DEG = 20.0        # 20° 线面角

DEFAULT_PARALLEL_FLANGE_AXIS = "x"     # 法兰 X 轴
DEFAULT_PARALLEL_BASE_AXIS = "z"       # 必须平行于 base Z
```

**与需求映射**:
| 你的需求 | 脚本参数 | 值 |
|---------|---------|-----|
| 刀脊方向 ‖ base Z | `parallel_flange_axis="x"`, `parallel_base_axis="z"` | ✅ |
| 刀面倾斜角度 | `plane_angle_deg=knife_tilt_angle` | ✅ 可调 |
| 刀的位置 | **未包含** | 待定 |

#### Cutting Motion (from demo_cut_tofu.py)

**Oblique cutting mode**:
```bash
python3.10 demo_cut_tofu.py \
  --cut-direction flange_z \   # 沿法兰 +Z 在基座中的方向切
  --press-normal-mm 0 \        # 无法向进刀
  --cut-move-mm 25 \           # 主切削位移 25mm
  --cut-drag-x-mm 0 \         # 无切向拖拽
  --step-z-mm -3 \             # 每刀下移 3mm
  --cycles 1                   # 切几刀
```

**Vertical cutting mode**:
```bash
python3.10 demo_cut_tofu.py \
  --cut-direction base_y       # 沿基座 +Y 切
```

#### Core Geometry (from demo_cut_tofu.py:292-298)

```python
def _flange_z_unit_in_base(mat16: list[float]) -> tuple[float, float, float]:
    """法兰 +Z 轴在基坐标系中的单位向量 (行优先 4x4 旋转块第三列)"""
    zx, zy, zz = float(mat16[2]), float(mat16[6]), float(mat16[10])
    # mat16[2], mat16[6], mat16[10] = 法兰 Z 轴在 base 坐标系中的方向向量
    return (zx / ln, zy / ln, zz / ln)
```

**Key insight**:
- 法兰位姿矩阵 `mat16` 的第 3、7、11 元素 = 法兰 Z 轴在 base 坐标系中的方向向量
- 斜切时, `--cut-direction flange_z` 让刀沿这个方向移动
- **刀的姿态由启动脚本前的机械臂位置决定** (代码不关心刀的具体姿态)

#### Cutting Trajectory (from demo_cut_tofu.py:754-765)

```python
def _cut_target_mat(anchor_i: list[float]) -> list[float]:
    m = list(anchor_i)
    cut_move_m = args.cut_move_mm / 1000.0
    if args.cut_direction == "flange_z":
        nx, ny, nz = _flange_z_unit_in_base(anchor_i)
        m[3] = m[3] + nx * cut_move_m   # X 方向移动
        m[7] = m[7] + ny * cut_move_m   # Y 方向移动
        m[11] = m[11] + nz * cut_move_m # Z 方向移动
    return m
```

### Current Work Objective

**Input**:
- `/objects_with_pose`: 豆腐的 6D 位姿 (位置 + 朝向 + 尺寸 + 主轴方向)

**Output**:
- 刀的**正确位置和姿态** (法兰位姿)
- 使得 `demo_cut_tofu.py --cut-direction flange_z` 能正确执行斜切

**Missing link**:
```
感知输出:
  /objects_with_pose = {
    position: (x, y, z),           # 豆腐中心位置
    orientation: (qx, qy, qz, qw), # 豆腐朝向
    extents: (L, W, H),             # 豆腐尺寸
    principal_axis: (ax, ay, az)    # 主轴方向
  }

需要计算:
  - 刀的位置 (x_knife, y_knife, z_knife)  ← 待定
  - 刀的姿态 (qx_knife, qy_knife, qz_knife, qw_knife) ← 可复用 demo_adjust_knife_pose_xcore.py
  - 切割参数 (cut_move_mm, step_z_mm, cycles) ← 可调参数
```

## Open Questions

### Phase1 Migration
- Q-MIG-001: SAM3 multi-prompt compatibility — classmate's Phase2 uses `"wooden knife box; ridged tofu"` (multi-class); our SAM3 node only supports single prompt. Phase1 only uses single prompt `"wooden cleaver handle"`, so no conflict during grab. After grab-knife exits and Phase2 starts, our SAM3 restarts with "豆腐" — no conflict. **Status: Resolved (no conflict)**.
- Q-MIG-002: `_BUNDLED_XCORE_SDK_ROOT` path bug — classmate's code has `../../../../` which resolves to a path missing `src/`. However, the code has fallback logic (`DEFAULT_XCORE_SDK_ROOT`, `LEGACY_XCORE_SDK_ROOT`, env var `DEXBOT_XCORE_SDK_ROOT`). **Status: To verify at runtime**.
- Q-MIG-003: Missing message types — `ObstacleBox.msg` and `TableWorkspace.msg` exist in classmate's `dexbot_interfaces_mid` but not in ours. **Status: Must add and rebuild before migration**.
- Q-MIG-004: O6 CAN interface — classmate's code uses `can0` for O6 gripper. Must confirm `can0` is up and configured on demo machine. **Status: To confirm**.

### Knife Pose Calculation

1. **刀的倾斜角度**: `knife_tilt_angle` — 可调参数，用户设定，范围 0° ~ 90°

2. **刀的朝向**: 已确认
   - 法兰 X轴 ‖ base Z轴（向前），点积 = 1
   - 可复用 `demo_adjust_knife_pose_xcore.py` 的 `build_target_rotation()` 函数

3. **刀的位置**: 待定
   - 根据豆腐位置 + 偏移量计算
   - 用户可调参数

4. **切割参数**: 可调参数
   - `cut_move_mm`, `step_z_mm`, `cycles`
   - 可能需要根据豆腐尺寸动态调整

### Grasp Planning

- How to convert OBB pose to grasp candidates? Not yet designed
- Object texture: PCA may have ambiguity for symmetric objects; current implementation is placeholder-quality

## Acceptance Criteria

- ✅ RealSense camera publishes color + depth topics
- ✅ sam3_detector_node outputs /detected_objects with masks
- ✅ pose_estimator_node outputs /objects_with_pose with 6D poses in Body_Base_link frame
- ✅ /objects_with_pose verified: tomato detected (confidence~0.978), position≈(0.315, 0.166, -0.064)m, size≈(9cm, 4cm, 3cm)
- ✅ Mask/depth resolution mismatch fixed (cv2.resize mask to match depth)
- ✅ camera_viewer_node 6D pose overlay implemented (OBB + axis + size text)
- ✅ EMA smoothing for pose jitter reduction (pose_smoothing_alpha param)
- ✅ Knife orientation constraint confirmed: 法兰 X轴 ‖ base Z轴 (dot product = 1)
- ✅ Reference implementation found: demo_adjust_knife_pose_xcore.py with build_target_rotation()
- ✅ Phase1 grab-knife migration designed: lifecycle wrapper, resource cleanup, /task/phase1_complete signal
- ⬜ Phase1 grab-knife migration implemented and hardware-tested
- ⬜ Knife position calculation from tofu 6D pose
- ⬜ Arm can move to cutting pose (integration with cuttofo_xcore demos)
- ⬜ demo_cut_tofu.py executes correctly with calculated knife pose