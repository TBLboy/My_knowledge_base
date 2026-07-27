# Progress Log

## 2026-05-21 19:10 CST (ChArUco calibration pipeline implemented and verified)

- Objective: Complete the code path for the ChArUco-based hand-eye calibration upgrade and verify it builds.
- Work completed:
  - Added `business/charuco_detector.py` for OpenCV 4.5.4-compatible ChArUco detection and pose estimation.
  - Added `scripts/camera_intrinsics_calibrator.py` for interactive RGB intrinsic calibration using ChArUco.
  - Added `scripts/charuco_capture_node.py` for interactive sample capture with robot TCP pose + multi-frame ChArUco observations.
  - Added `scripts/charuco_handeye_solver.py` for offline SE(3) baseline and pixel-level bundle adjustment.
  - Updated `setup.py` to install the new config file and expose three new ROS2 console entry points.
  - Added `cuttofo_calibration/scripts/__init__.py` so the new tools are importable.
  - Updated `config/board.yaml` to the compact hand-back ChArUco board configuration.
  - Verified detection on generated board image: 9 corners detected and pose estimation succeeded.
  - Verified package build and installed entry points.
- Business logic impact:
  - New parallel calibration pipeline added without removing the existing single-ArUco GUI baseline.
  - Existing GUI remains intact; new flow is available via dedicated console tools.
- Verification:
  - `python3 -m py_compile` passed for all new and modified Python files.
  - `colcon build --packages-select cuttofo_calibration` passed.
  - `ros2 pkg executables cuttofo_calibration` shows:
    - `calibration_gui`
    - `camera_intrinsics_calibrator`
    - `charuco_handeye_capture`
    - `charuco_handeye_solver`
  - Smoke test of `cuttofo_calibration.business.charuco_detector` passed on generated board image.
- Files changed:
  - `cuttofo_calibration/business/charuco_detector.py` (new)
  - `cuttofo_calibration/scripts/camera_intrinsics_calibrator.py` (new)
  - `cuttofo_calibration/scripts/charuco_capture_node.py` (new)
  - `cuttofo_calibration/scripts/charuco_handeye_solver.py` (new)
  - `cuttofo_calibration/scripts/__init__.py` (new)
  - `config/board.yaml`
  - `setup.py`
  - `.project-log/progress.md`
- Next steps:
  1. User mounts the printed board on the hand back and runs the intrinsics calibrator.
  2. Capture 20-30 hand-eye samples with the capture node.
  3. Run the offline solver on the generated run directory.

## 2026-05-21 18:40 CST (ChArUco precision branch & code skeleton created)

- Objective: Create the foundation modules for the ChArUco-based hand-eye calibration upgrade.
- Work completed:
  - Created branch document `.project-log/business-logic/branches/charuco-handeye-precision.md` with full execution chain.
  - Created `config/board.yaml` — ChArUco board template with nominal + measured fields.
  - Created `business/board_config.py` — BoardConfig dataclass with YAML load/save, effective/measured length logic, OpenCV CharucoBoard builder.
  - Created `business/run_manager.py` — RunManager with timestamped run directories, per-frame detection save, robot pose save, solution snapshots, board/intrinsics snapshots.
  - Created `business/observation_models.py` — FrameObservation, SampleEnvelope, AggregatedObservation data classes + observations.json load/save.
- Business logic impact: New data path parallel to existing single-ArUco pipeline; old pipeline preserved as baseline.
- Verification:
  - Syntax: `python3 -m py_compile` passed for all 3 new modules.
- Files changed:
  - `.project-log/business-logic/branches/charuco-handeye-precision.md` (new)
  - `config/board.yaml` (new)
  - `cuttofo_calibration/business/board_config.py` (new)
  - `cuttofo_calibration/business/run_manager.py` (new)
  - `cuttofo_calibration/business/observation_models.py` (new)
  - `.project-log/progress.md`
- Next steps:
  1. User prints ChArUco board and measures it.
  2. Implement `camera_intrinsics_calibrator` entry point (Phase 2).
  3. Implement ChArUco observer / frame capture (Phase 3).

## 2026-05-21 18:10 CST (Hand-Eye Precision Optimization Plan Established)

- Objective: Move hand-eye calibration from single ArUco baseline toward ChArUco-based high-precision calibration.
- Work completed:
  - Reviewed current calibration engine and sample manager.
  - Confirmed the current solver already uses Shah/Li initialization + MAD 3.5σ outlier rejection + Huber LM refinement.
  - Confirmed current data model still stores one averaged ArUco pose per sample, which is insufficient for pixel-level bundle adjustment.
  - Established the next-stage plan: run directory, board configuration, raw observation retention, SE(3) baseline, pixel-level BA, and leave-one-out validation.
- Business logic impact:
  - No code behavior changed yet.
  - The calibration workflow will be extended from single-pose samples to frame-level observation records.
- Problems encountered:
  - Current package has no run-scoped artifact structure for calibration experiments.
- Resolution:
  - Plan to add a timestamped `calibration_runs/` structure and preserve all raw observations for later optimization.
- Verification:
  - Code review only; no runtime verification run yet.
- Files changed:
  - `.project-log/current-session.md`
  - `.project-log/progress.md`
- Next steps:
  1. Add a run-scoped calibration output directory.
  2. Add board configuration and observation data structures.
  3. Prepare ChArUco capture/recording path.
  4. Then implement the SE(3) baseline and BA pipeline.

## 2026-05-09 — 包创建 + 完整代码实现

- Objective: 创建 cuttofo_calibration 包，实现手眼标定 GUI 工具
- Work completed:
  - 创建完整目录结构（business/ view/ launch/ config/ data/）
  - 编写 calibrator_design.md 详细设计文档（~1100 行）
  - 实现 4 个业务模块 + 4 个界面模块 + 1 个 launch
  - colcon build 通过，所有 import 验证通过
- Problems encountered: None
- Resolution: N/A
- Verification:
  - `colcon build --packages-select cuttofo_calibration` ✅
  - Python import 验证 ✅
  - launch --show-args ✅
- Files changed:
  - 新建 13 个源文件 + 3 个 skel 文件 + 1 个设计文档
- Files created:
  - `package.xml`, `setup.py`, `setup.cfg`
  - `calibrator_design.md`
  - `business/camera_stream.py`, `business/aruco_monitor.py`
  - `business/calibration_client.py`, `business/sample_manager.py`
  - `view/calibration_gui.py`, `view/camera_panel.py`
  - `view/control_panel.py`, `view/metrics_bar.py`
  - `launch/calibration_gui.launch.py`
  - `.project-log/requirements.md`, `.project-log/progress.md`, `.project-log/current-session.md`
- Next steps: 连接实机 (RealSense + Lbot) 验证 GUI 功能

## 2026-05-09 (续) — 适配 Lbot 上电/下电模式 + 代码审查修复

- Objective: 去掉 GUI 独立 SDK 连接，改用标定节点 `force_sdk_connect_on_manual_start` 单连接方案
- Work completed:
  - 多代理全面审查发现 21 个问题 (4 CRITICAL / 10 SEVERE / 7 MODERATE)
  - 修复双 executor 冲突：`_call_trigger` 改用 `rclpy.spin_until_future_complete(node, future)` 不创建临时 executor
  - 移除 GUI 中的 `LbotArmAdapter` 独立连接（避免与标定节点 SDK 连接冲突）
  - 移除 上电/下电 按钮（Lbot 通过控制器/硬件面板操作，不在 GUI 内控制）
  - 所有阻塞调用改用 `after()` 延迟执行，避免冻结 GUI
  - 修复操作顺序：先远程记录成功 → 再本地添加（delete 同理）
  - launch: 添加 `force_sdk_connect_on_manual_start:=true`
- Problems encountered: 标定节点 SDK 单连接读状态，GUI 不另连 SDK
- Resolution: GUI 纯展示+Service调用，标定节点直连 SDK 读关节/TCP
- Verification:
  - `colcon build` ✅
  - import ✅
  - launch --show-args ✅
- Files changed:
  - `business/calibration_client.py` — executor 修复
  - `view/control_panel.py` — 移除 SDK 连接、修复操作顺序
  - `view/calibration_gui.py` — 移除 arm_host 参数
  - `launch/calibration_gui.launch.py` — 添加 force_sdk_connect
  - `cuttofo_lbot/lbot_arm_adapter.py` — 添加 enable_arm 方法（备用）
- Next steps: 实机运行标定

## 2026-05-09 (续2) — 4 代理审查 + 10 项 BUG 修复

- Objective: 第二轮全面审查并修复所有问题
- Work completed:
  - 4 个并行代理全面审查（control_panel、calibration_client/gui、business 模块集成、launch 依赖）
  - 发现 4 项 CRITICAL + 6 项 HIGH + 10 项 MEDIUM/LOW
  - 修复 10 项核心问题
- Problems encountered:
  - CRITICAL: TCP 位姿硬编码 (0,0,0)、`_auto_cli` 未初始化会崩溃、`_eval_split` 死空壳
  - HIGH: 双线程 spin 冲突、`package.xml` 缺依赖、launch 硬编码 IP、`_on_status` YAML 解析失败
  - MEDIUM: 按钮状态混乱、numpy 线程不安全、标签误导
- Resolution:
  - TCP: `_do_record` 改为 `arm.get_pose()` 读取实际位姿
  - 双线程: `_call_trigger` 改用 `future.add_done_callback` + `Event.wait()`
  - `_auto_cli`: `__init__` 添加 `/calibration/auto_calibrate` client
  - `_eval_split`: 实现基本误差计算
  - 按钮: record/delete 初始 DISABLED，start→ENABLED，stop→DISABLED
  - 连接: label 改为 "已连接（已上电）"
- Verification:
  - `colcon build` ✅
  - import + `_auto_cli` 创建 ✅
- Files changed:
  - `business/calibration_client.py`, `business/sample_manager.py`
  - `view/control_panel.py`, `view/calibration_gui.py`, `view/camera_panel.py`
  - `launch/calibration_gui.launch.py`, `package.xml`
- Next steps: 第二轮审查完善

## 2026-05-09 (续3) — 3 代理第二轮审查 + 关键修复

- Objective: 第二轮审查边缘情况、死代码、逻辑完善
- Work completed:
  - 3 代理并行审查（端到端流程、边缘情况、死代码一致性）
  - 修复 `_on_status` YAML 解析：不再擦除之前的有效结果，扩大匹配键范围
  - 修复键盘快捷键：Ctrl+S/Ctrl+C 与终端冲突 → Alt+S/Alt+C
  - 修复 TCP/ArUco 丢失时静默记录垃圾数据 → 显示橙色警告
  - 清理死代码：移除 `self._camera`、`_result_raw`、`import yaml` 等
  - 移除 `compute_cross_validation` 和 `_eval_split` 死函数
- Problems resolved:
  - `_on_status` 每次非 YAML 消息都清空 `_result_data` → 已修复
  - Ctrl+S 冻结终端输出 → 已修复
  - ArUco/TCP 为 None 时静默记录 (0,0,0) → 显示警告标签
- Verification:
  - `colcon build` ✅
  - ControlPanel 签名验证 ✅
- Files changed:
  - `business/calibration_client.py`, `business/sample_manager.py`
  - `view/calibration_gui.py`, `view/control_panel.py`
- Next steps: 实机验证

---

## 2026-05-11 - xCore 适配改造

### 目标

移除 Lbot 依赖，适配 xCore 机械臂：上电/下电 → 拖动模式，支持左右臂选择和 IP 配置。

### 新增文件

| 文件 | 说明 |
|------|------|
| `business/xcore_drag_controller.py` | xCore SDK 直调封装：connect/enable_drag/disable_drag/get_pose/get_joints |

### 修改文件

| 文件 | 改动 |
|------|------|
| `view/control_panel.py` | 重写机械臂控制区: LbotArmAdapter → XcoreDragController；上电/下电 → 开启/关闭拖动；新增左右臂 RadioButton + IP 输入 + 重连按钮；新增"保存结果"按钮(filedialog)；CSV 导出支持路径选择 |
| `business/sample_manager.py` | `save_csv()` 支持绝对路径 |
| `view/calibration_gui.py` | 新增 `arm_side` ROS 参数 |
| `launch/calibration_gui.launch.py` | 新增 `arm_side`，输出路径改为 `calib_{side}/` |
| `package.xml` + `setup.py` | 移除 `cuttofo_lbot` 依赖 |

### 拖动模式实现

xCore SDK 的 `enableDrag`/`disableDrag` 无 ROS2 Service 封装，直接调用 SDK：
```
开启: NRT模式 → Manual → PowerOff → enableDrag(笛卡尔, 自由, 免按钮)
关闭: disableDrag → Auto → PowerOn
```
尝试 4 组合(笛卡尔/轴空间 × 免按钮/需按钮)直到成功。

### 编译: colcon build ✅ | py_compile 4/4 ✅

---

## 2026-05-12 — 代码审查 + Bug 修复

### 目标

对标定 GUI 全量代码进行系统审查，修复点位采集、标定计算逻辑中的关键 bug。

### 发现的 Bug

| # | 严重度 | 文件 | 问题 |
|---|--------|------|------|
| 1 | 🔴 Critical | `sample_manager.py` | `cv2.calibrateRobotWorldHandEye` 返回 4 个值但只解包 2 个 → `ValueError` 崩溃；即使修复，该函数是眼在手上算法，不适用于眼在手外场景 |
| 2 | 🔴 Critical | `sample_manager.py` | RMSE 将 TCP 位置与 ArUco 位置直接做差 — 两者物理位置不同（有 offset），均方根无意义 |
| 3 | 🟡 Medium | `sample_manager.py` | `tcp_orientation` 标注四元数类型但存 Euler 角，语义误导 |
| 4 | 🟡 Medium | `control_panel.py` | 按钮文本 `[Ctrl+C]` 但快捷键是 `<Alt-c>`，用户按 Ctrl+C 无反应 |
| 5 | 🟡 Medium | `metrics_bar.py` + `control_panel.py` | `set_rmse()` 定义了但从未被调用，底部 RMSE 栏始终显示 `"--"` |
| 6 | 🟡 Medium | `calibration_client.py` | 7 个 ROS2 Service Client 全部未使用（GUI 已自包含），死代码 |
| 7 | 🟡 Medium | `calibration_gui.launch.py` | `robot_ip` 参数声明但从未使用 |

### 修复内容

#### P0 — `sample_manager.py` 重写 `compute_hand_eye()`

手眼标定算法改为 `cv2.calibrateHandEye`（眼在手外公式）：

1. 输入：绝对位姿 `T_base2tcp`（正向运动学）+ **反转后的** marker 位姿 `T_marker2cam = inv(T_cam2marker)`
2. 输出：`T_gripper2marker`（marker 在 TCP 下的偏移）
3. 对每个采样计算 `T_cam2base = T_cam2marker_i * inv(T_gripper2marker) * inv(T_base2tcp_i)`
4. 均值化（旋转用 SVD 投影到 SO(3)），得最终 `T_base2cam = inv(mean T_cam2base)`
5. 重投影验证：用标定结果回代预测 marker 在相机坐标系下的位姿，与实际检测值比较

**数学验证**：合成数据测试通过，rmse=0.0，精确恢复 ground truth。

#### P1 — 界面修正

- `control_panel.py`: 按钮文本 `[Ctrl+C]` → `[Alt+C]`；`tcp_orientation` → `tcp_euler`；`_do_compute` 调用 `metrics.set_rmse()`
- `calibration_gui.py`: 创建 `MetricsBar` 后通过 `set_metrics_bar()` 注入到 `ControlPanel`
- `calibration_gui.launch.py`: 删除未使用的 `robot_ip` 参数
- `calibration_client.py`: 已删除（死代码，未被任何模块 import）

#### `SampleRecord` 字段改名

| 旧字段 | 新字段 | 类型 |
|--------|--------|------|
| `tcp_orientation` | `tcp_euler` | `tuple[float, float, float]` |

### 编译验证

```
colcon build --packages-select cuttofo_calibration cuttofo_xcore ✅
```

### 文件改动

| 文件 | 改动 |
|------|------|
| `business/sample_manager.py` | 自动保存/载入；全流程日志；`clear_saved()`；`to_dict/from_dict` 序列化 |
| `view/control_panel.py` | IP 交换；日志；`clear_saved` 按钮；启动时 `load()` |
| `view/calibration_gui.py` | IP 交换；`data_dir` 相对路径；`logging.basicConfig`；版本号 v1.1 |
| `launch/calibration_gui.launch.py` | IP 交换 |
| `.project-log/progress.md` | — |

### 编译

```
colcon build --packages-select cuttofo_calibration ✅
```

---

## 2026-05-12 — 标定算法深度审查及根因定位

### 问题

GUI 标定结果异常：pos_rmse=**197.7 mm**, rot_rmse=**61.5°**。采集 10 个稳定点，结果明显错误。

### 审查过程

对标定 GUI 的 `compute_hand_eye()` 与项目中已有且验证可用的参考实现 (`hand_eye_calibration_node.py`) 进行对比审查。

### 参考实现 (`hand_eye_calibration_node.py`)

路径: `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/dexbot_toolbox/dexbot_toolbox/calibration/hand_eye_calibration_node.py`

- **OpenCV 函数**: `cv2.calibrateRobotWorldHandEye` — 求解 `AX = YB`
- **输入**: `R_base_tcp, t_base_tcp` + `R_cam_marker, t_cam_marker` **直接传入，不反转**
- **输出**: `T_base_cam`（相机在基坐标系）+ `T_tcp_marker`（标记在 TCP 上）
- **后处理**: LM 优化 + Huber loss + MAD 异常值剔除
- **验证结果**: 4.6 mm / 1.37° (`config/calibration_result.yaml`)

### GUI 当前算法 (`sample_manager.py`)

- **OpenCV 函数**: `cv2.calibrateHandEye` — 求解 `AX = XB`（**眼在手上算法**）
- **输入**: 反转标记位姿 `T_marker2cam = inv(T_cam2marker)` 后再传入
- **输出**: 手工计算 T_base_cam（多次平均 + 求逆）
- **后处理**: 无优化，无异常值剔除

### 根因分析

#### 问题 1: 算法用错

| 场景 | 正确方程 | OpenCV 函数 |
|------|----------|-------------|
| 眼在手上（相机装机械臂上移动，标定板固定） | `AX = XB` | `calibrateHandEye` |
| **眼在手外**（相机固定胸口，标记装 TCP 上） | **`AX = YB`** | **`calibrateRobotWorldHandEye`** |

你的场景是**眼在手外**，但 GUI 用了**眼在手上**的 `calibrateHandEye`。两个方程在数学上不等价，有噪声时必然出垃圾结果。

#### 问题 2: 标记反转画蛇添足

```python
# GUI 当前做法:
R_m2c = R_cm.T          # 反转 T_cam2marker → T_marker2cam
t_m2c = -R_m2c @ t_cm
cv2.calibrateHandEye(R_base2tcp, R_marker2cam, ...)  # 求解 A*X = X*B_inv
```

参考实现直接传入不反转：
```python
cv2.calibrateRobotWorldHandEye(R_base2tcp, R_cam_marker, ...)  # 求解 A*X = Y*B
```

反转操作尝试将 `AX = YB` 问题强制映射到 `AX = XB`，但两者数学上不相等：
- `calibrateHandEye(A, B_inv)` 求解: `A * X = X * B_inv`
- 实际需要: `A * X = Y * B`
- 不等价，尤其在有噪声时

#### 问题 3: 缺后续优化

参考实现含 LM 优化器 + Huber loss + 异常值剔除。GUI 实现直接取 OpenCV 裸结果——当输入包含较大噪声时结果不稳定。

### 修复方向

1. 将 `cv2.calibrateHandEye` 替换为 `cv2.calibrateRobotWorldHandEye`
2. 取消标记位姿的手动反转，直接传入 `R_cam_marker, t_cam_marker`
3. 正确解包 4 个返回值：`R_base2cam, t_base2cam, R_tcp2marker, t_tcp2marker`
4. RMSE 用参考实现的重投影公式

### 为什么合成数据测试通过了

无噪声时任意方程组都能满足，有噪声时算法选择错误导致结果发散。这是假阳性验证，真实场景无法复现。

### 涉及文件

| 文件 | 操作 |
|------|------|
| `business/sample_manager.py` | 待修复 |
| `business/calibration_client.py` | 已删除（死代码） |
colcon build --packages-select cuttofo_calibration ✅
```

---

## 2026-05-12（后续）— 实时关节角度显示

### 目标

在 GUI 中实时显示机械臂 7 个关节角度（°），方便监控机械臂姿态。

### 改动

仅修改 `view/control_panel.py`：

1. **新增关节角度 LabelFrame** — 放在"机械臂选择"和"机械臂控制"之间，用 grid 排版 4+3 列显示 J1~J7
2. **`_refresh_joints()` 方法** — 每 33ms 调用 `self._arm.get_joints()`，弧度转角度实时更新
   - 已连接 → 黑色显示 `J1: -12.3°` 等
   - 未连接 → 灰色
   - 读取失败 → 橙色
3. **头部新增 `from __future__ import annotations`** 和 `import math`

### 编译

```
colcon build --packages-select cuttofo_calibration ✅
```
---

## 2026-05-12 — 代码审查 + Bug 修复

### 目标

对标定 GUI 全量代码进行系统审查，修复点位采集、标定计算逻辑中的关键 bug。

### 发现的 Bug

| # | 严重度 | 文件 | 问题 |
|---|--------|------|------|
| 1 | 🔴 Critical | `sample_manager.py` | `cv2.calibrateRobotWorldHandEye` 返回 4 个值但只解包 2 个 → `ValueError` 崩溃；即使修复，该函数是眼在手上算法，不适用于眼在手外场景 |
| 2 | 🔴 Critical | `sample_manager.py` | RMSE 将 TCP 位置与 ArUco 位置直接做差 — 两者物理位置不同（有 offset），均方根无意义 |
| 3 | 🟡 Medium | `sample_manager.py` | `tcp_orientation` 标注四元数类型但存 Euler 角，语义误导 |
| 4 | 🟡 Medium | `control_panel.py` | 按钮文本 `[Ctrl+C]` 但快捷键是 `<Alt-c>`，用户按 Ctrl+C 无反应 |
| 5 | 🟡 Medium | `metrics_bar.py` + `control_panel.py` | `set_rmse()` 定义了但从未被调用，底部 RMSE 栏始终显示 `"--"` |
| 6 | 🟡 Medium | `calibration_client.py` | 7 个 ROS2 Service Client 全部未使用（GUI 已自包含），死代码 |
| 7 | 🟡 Medium | `calibration_gui.launch.py` | `robot_ip` 参数声明但从未使用 |

### 修复内容

#### P0 — `sample_manager.py` 重写 `compute_hand_eye()`

手眼标定算法改为 `cv2.calibrateHandEye`（眼在手外公式）：

1. 输入：绝对位姿 `T_base2tcp`（正向运动学）+ **反转后的** marker 位姿 `T_marker2cam = inv(T_cam2marker)`
2. 输出：`T_gripper2marker`（marker 在 TCP 下的偏移）
3. 对每个采样计算 `T_cam2base = T_cam2marker_i * inv(T_gripper2marker) * inv(T_base2tcp_i)`
4. 均值化（旋转用 SVD 投影到 SO(3)），得最终 `T_base2cam = inv(mean T_cam2base)`
5. 重投影验证：用标定结果回代预测 marker 在相机坐标系下的位姿，与实际检测值比较

**数学验证**：合成数据测试通过，rmse=0.0，精确恢复 ground truth。

#### P1 — 界面修正

- `control_panel.py`: 按钮文本 `[Ctrl+C]` → `[Alt+C]`；`tcp_orientation` → `tcp_euler`；`_do_compute` 调用 `metrics.set_rmse()`
- `calibration_gui.py`: 创建 `MetricsBar` 后通过 `set_metrics_bar()` 注入到 `ControlPanel`
- `calibration_gui.launch.py`: 删除未使用的 `robot_ip` 参数
- `calibration_client.py`: 已删除（死代码，未被任何模块 import）

#### `SampleRecord` 字段改名

| 旧字段 | 新字段 | 类型 |
|--------|--------|------|
| `tcp_orientation` | `tcp_euler` | `tuple[float, float, float]` |

### 编译验证

```
colcon build --packages-select cuttofo_calibration cuttofo_xcore ✅
```

### 文件改动

| 文件 | 改动 |
|------|------|
| `business/sample_manager.py` | 完整重写 `compute_hand_eye()`；`tcp_orientation` → `tcp_euler`；CSV 字段同步 |
| `view/control_panel.py` | 按钮文本修复；`tcp_euler` 字段同步；注入 `metrics_bar`；`_do_compute` 更新 RMSE 栏 |
| `view/calibration_gui.py` | 创建 MetricsBar 后传给 ControlPanel |
| `launch/calibration_gui.launch.py` | 删除 `robot_ip` |
| `business/calibration_client.py` | 删除（死代码） |

---

## 2026-05-12 — 标定算法修复: calibrateHandEye → calibrateRobotWorldHandEye

### 背景

GUI 标定结果异常（pos_rmse≈200mm, rot_rmse≈61°）。经深度审查，根因是算法用错。

### 根因

`compute_hand_eye()` 使用了 `cv2.calibrateHandEye`（求解 AX=XB，眼在手上算法），但实际场景是眼在手外（相机固定胸口，ArUco 装 TCP 上），正确方程是 AX=YB，对应函数是 `calibrateRobotWorldHandEye`。

额外错误：手动反转了 ArUco 标记位姿 (`R_m2c = R_cm.T; t_m2c = -R_m2c @ t_cm`) 导致数学不一致。

### 修复

| 项 | 修改前 | 修改后 |
|------|--------|--------|
| OpenCV 函数 | `cv2.calibrateHandEye` (AX=XB) | `cv2.calibrateRobotWorldHandEye` (AX=YB) |
| 输入 | 反转后 `R_marker2cam` | 直接传入 `R_cam_marker` |
| 解包 | `R_g2m, t_g2m` (2 值) | `R_bc, t_bc, R_tm, t_tm` (4 值) |
| 输出计算 | 多次平均 + 求逆 | 直接 T_base_cam = [R_bc \| t_bc] |
| 重投影 | T_cb @ T_bt @ T_g2m vs T_cm | T_bt @ T_base_cam vs T_tm @ T_cm (AX=YB) |
| 输出字段 | rmse_max_mm | rmse_deg |
| 新增输出 | — | T_tcp_marker（标记在 TCP 上的偏移） |

### 验证

合成数据测试：
- 无噪声：RMSE=0.0mm, 0.0°，精确恢复 ground truth ✅
- 1mm 噪声：RMSE≈1.6mm, 0.0°，平移到误差≈0.6mm ✅
- <6 样本返回 None ✅

### 编译

```
colcon build --packages-select cuttofo_calibration ✅
```

### 文件改动

| 文件 | 改动 |
|------|------|
| `business/sample_manager.py` | 重写 `compute_hand_eye()` 算法 |

---

## 2026-05-12 — GUI 性能优化：线程架构重构

### 问题

- 标定 GUI 画面卡顿、ArUco 坐标轴滞后、整体响应慢
- 调试模式画面经常卡住

### 根因分析

| 问题 | 根因 | 影响 |
|------|------|------|
| **关节角度刷新阻塞 GUI** | `_refresh_joints()` 在主线程每 33ms 调用 xCore SDK `get_joints()` — 网络请求可能阻塞 50-100ms | GUI 事件循环被阻塞，画面冻结 |
| **工作线程固定 sleep** | `_worker_loop` 有固定 `time.sleep(0.03)`，即使 CPU 空闲也限制帧率 | 处理超时时帧率骤降 |
| **ROS 回调堆积** | 主线程被阻塞时，ROS 回调排队堆积 | ArUco 位姿更新滞后 |

### 修复内容

#### 1. control_panel.py — 关节角度后台线程化

```python
# 新增：
self._cached_joints: tuple[float, ...] | None = None
self._joints_run = True
self._joints_thread = threading.Thread(target=self._joints_worker, daemon=True)

# 后台线程：
def _joints_worker(self):
    while self._joints_run:
        if arm.connected:
            joints = arm.get_joints()    # SDK 调用在后台
            self._cached_joints = tuple(joints)
        else:
            self._cached_joints = None   # 断连时清缓存
        time.sleep(0.1)                  # 10Hz

# 主线程 refresh_joints：
def _refresh_joints(self):
    joints = self._cached_joints        # 直接读缓存，零阻塞
    ...
```

#### 2. camera_panel.py — 工作线程事件驱动

```python
# 之前：固定 sleep(0.03)，帧率上限 28fps
# 之后：无 sleep，有帧立即处理

def _worker_loop(self):
    while self._running:
        raw = self._camera.get_latest_frame()
        if raw is None:
            time.sleep(0.01)
            continue
        processed = self._process_frame(raw.copy())
        with self._frame_lock:
            self._processed_frame = processed
```

### 编译

```
colcon build --packages-select cuttofo_calibration ✅
```

### 文件改动

| 文件 | 改动 |
|------|------|
| `view/control_panel.py` | 新增 `_joints_worker` 线程 + `_cached_joints` 缓存；`_refresh_joints` 改为读缓存 |
| `view/camera_panel.py` | 移除 `time.sleep(0.03)`，工作线程事件驱动 |

---

## 2026-05-12 — 日志持久化 + Bug 修复

### 日志持久化

启动时自动在 `cuttofo_calibration/log/` 创建带时间戳的日志文件，与终端实时输出同步：

```
log/
└── calibration_2026-05-12_17-41-38.log
```

**改动**: `view/calibration_gui.py` — 在 `logging.basicConfig` 后添加 `FileHandler`，写入 `log/` 目录，格式含完整时间戳。

### Bug 修复

`_joints_worker` 中 `time.sleep(0.1)` 缺少 `import time`，线程启动即崩溃导致关节角度一直显示黄色 `--`。

**改动**: `view/control_panel.py` — 添加 `import time`。

### 涉及文件

| 文件 | 改动 |
|------|------|
| `view/calibration_gui.py` | 新增 `from datetime import datetime`；`logging.FileHandler` 写入 `log/` 目录 |
| `view/control_panel.py` | 添加 `import time` |
