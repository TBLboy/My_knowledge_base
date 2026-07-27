# Business Logic Decision Records

## 2026-05-20 - Phase2 Prepare Uses Two-Stage Queued MoveAbsJ Instead of Single-Step MoveAbsJ

- **Decision**: Replace Phase2/Phase6 single-step `MoveAbsJ` prepare execution with a two-stage queued `MoveAbsJ` sequence: current → via(70%) → final.
- **Context**:
  - Current Phase2 computes a valid final TCP pose and IK solution, then directly executes one NRT `MoveAbsJ` to the final joints.
  - During this single-step joint-space motion, the knife posture and position change simultaneously, which can scrape tofu while approaching the final target.
  - User requirement: first complete most posture adjustment, then perform the last approach segment with the knife already near final orientation.
  - User explicitly prefers the second stage to remain `MoveAbsJ`, not RT Cartesian or MoveL.
- **Implementation**:
  - Build a via pose at 70% of current_TCP → target_TCP translation.
  - Interpolate via orientation toward the final orientation (slerp ratio 0.70 by default).
  - Solve IK for the via pose using current joints as seed.
  - Queue `q_via` and `q_prepare` in one SDK command sequence (`moveAppend([cmd1, cmd2])` + single `moveStart()`).
  - Apply same logic to `phase2_prepare` and `phase6_prepare`, so Phase4 and Phase6 re-entry both use staged prepare automatically.
- **Alternatives considered**:
  - (a) Keep single-step `MoveAbsJ` — rejected: posture changes too late, scraping risk remains.
  - (b) Use RT Cartesian prepare — rejected: unnecessary complexity for free-space pre-cut approach.
  - (c) Use second-stage MoveL — rejected per user preference; joint-space approach appears more natural.
  - (d) Two-stage queued `MoveAbsJ` — **selected**: minimal architecture change, continuous motion, better approach safety.
- **Evidence / Verification**: SDK examples confirm multi-command `MoveAbsJ` queueing and available zone/blend control.
- **Impacted nodes**: PHASE_2_MOVE_TO_PREPARE
- **Impacted edges**: edge_2_prepare
- **Status**: active

## 2026-05-20 - Phase3 Twitch Root Cause: TCP Coordinate Conflict, Not Force Sensor

- **Decision**: Phase3 cut start twitch root cause is tool frame (`cut_tofo_tcp`) leakage from Phase1 grab, not force sensor zero drift. Fix with two-layer tool frame restoration.
- **Context**:
  - Initial hypothesis was force sensor calibration (Phase1 grab changes force/torque bias)
  - Added `calibrateForceSensor(True, 0)` before RT path — helped but did not fully eliminate twitch
  - User confirmed: "主要问题就是TCP坐标冲突" — grab TCP and cutting TCP conflict
  - Phase1 uses `cut_tofo_tcp` with offset `(0.025, 0.0, 0.08)` for grasp-follow
  - Phase3 RT Cartesian path reads active tool frame from SDK controller state; stale frame causes instantaneous pose correction
- **Implementation**:
  - Layer 1: `xcore_follow_tcp_chain_node_movej.py` restores `tool0/wobj0` after `move_abs_joints` success
  - Layer 2: `lbot_robot_xcore.py` `move_rt_cartesian_path()` step 3.5 forces `setToolset(tool0, wobj0)` before `RtCommandMode`
  - Launch wiring: `cuttofu_phase1_grab_internal.launch.py` passes `restore_default_toolset_after_move_abs_joints:=true`
- **Alternatives considered**:
  - (a) Force sensor calibration only — rejected: helped but did not fully resolve
  - (b) SDK controller reset between Phase1 and Phase2 — rejected: would require disconnect/reconnect, too slow
  - (c) Two-layer tool frame restoration — **selected**: covers both normal exit and GUI state leakage
- **Evidence / Verification**: Hardware test confirmed smooth Phase3 cut start; logs show both restoration markers
- **Impacted nodes**: PHASE_1_GRAB_KNIFE, PHASE_3_FIRST_CUT, PHASE_5_SECOND_CUT
- **Impacted edges**: edge_3_to_4, edge_5_to_6
- **Status**: active

## 2026-05-19 - Calibration Format Compatibility and Hardcoded Paths Fixed

- **Decision**: Modify `_load_calibration()` in both migrated nodes to support both calibration YAML formats; replace all hardcoded absolute paths with `__file__`-relative paths
- **Context**:
  - Classmate's code expects `T_base_cam: {matrix: [[...], ...]}` format
  - User's calibration files use `T_base_cam: [[...], ...]` direct 4x4 matrix format
  - Classmate's code had hardcoded paths like `/home/a/Desktop/dexbot_ros2_ws/src/config1/...`
  - `_BUNDLED_XCORE_SDK_ROOT` and `_LINKERBOT_SDK_SRC` relative paths were off by 1-2 levels
- **Changes made**:
  - `xcore_monitor_handle_sequence_node.py`:
    - `_load_calibration()`: Added format detection — tries `tbc["matrix"]` first (classmate format), falls back to `tbc` directly (user format)
    - Added `_default_calibration_file()` using `__file__` relative path → `config/calib_right/calibration_result_right.yaml`
  - `cut_tofu_object_recognition_node.py`:
    - Same `_load_calibration()` format compatibility fix
    - Same `_default_calibration_file()` relative path
  - `xcore_follow_tcp_chain_node_movej.py`:
    - Fixed `_BUNDLED_XCORE_SDK_ROOT`: `../../../../` → `../../../` (from `CutTofo/ros/` to `src/dexbot_bottom_layer/`)
    - Fixed `_LINKERBOT_SDK_SRC`: `../../../` → `../../../` (already correct after fix)
    - Fixed `xcore_sdk_root` parameter default: hardcoded → `_BUNDLED_XCORE_SDK_ROOT`
- **Path verification**: All 3 paths confirmed resolving correctly:
  - SDK: `/home/tbl/Project/dexbot_ros2_ws/src/dexbot_bottom_layer/dexbot_bottom_layer/xcoresdk_python-v0.5.1.ar_12` ✅
  - Linkerbot: `/home/tbl/Project/dexbot_ros2_ws/src/dexbot_bottom_layer/dexbot_bottom_layer/linkerbot-python-sdk/src` ✅
  - Calibration: `/home/tbl/Project/dexbot_ros2_ws/src/config/calib_right/calibration_result_right.yaml` ✅
- **Evidence / Verification**: `colcon build --packages-select dexbot_middle_layer` succeeded; path resolution verified via Python script
- **Impacted nodes**: All 3 migrated CutTofo nodes
- **Status**: active

## 2026-05-19 - dexbot_middle_layer setup.py Merged with CutTofo Entry Points

- **Decision**: Merge all CutTofo console_scripts from classmate's setup.py into user's setup.py
- **Context**: User's `dexbot_middle_layer/setup.py` had only 4 base entry points; classmate's had 24+ including all CutTofo nodes
- **Changes made**:
  - Copied entire `CutTofo/` directory from classmate's workspace to user's `dexbot_middle_layer/`
  - Added all 20 CutTofo entry points to `setup.py` (follow nodes, monitor nodes, demo nodes)
  - Added `data_files` entry for `CutTofo/config/cut_tofu_phase3_sequence.json`
  - `colcon build --packages-select dexbot_middle_layer` succeeded
- **Entry points added**:
  - Execution: `object_follow_tcp_node`, `xcore_follow_tcp_node`, `xcore_follow_tcp_chain_node`, `xcore_follow_tcp_chain_node_new`, `xcore_follow_tcp_chain_node_movej`, `xcore_follow_tcp_chain_node_parallel`
  - Monitor: `object_monitor_node`, `xcore_monitor_node`, `xcore_monitor_handle_chain_node`, `xcore_monitor_handle_sequence_node`, `cut_tofu_object_recognition_node`, `xcore_monitor_handle_sequence_node_parallel`
  - Demo/Utility: `demo_xcore_movel`, `demo_xcore_movej`, `demo_xcore_rotate_pos_y_tcp`, `demo_xcore_rotate_elbow_range`, `read_xcore_current_pose_6d`, `demo_ar5_left_tcp_y_ground_angle`
- **Evidence / Verification**: Build passed; `CutTofo/ros/` directory verified with all 4 critical files present
- **Impacted nodes**: All CutTofo nodes now accessible via `ros2 run dexbot_middle_layer <node_name>`
- **Status**: active

## 2026-05-19 - dexbot_interfaces_mid Extended with ObstacleBox and TableWorkspace

- **Decision**: Copy `ObstacleBox.msg` and `TableWorkspace.msg` from classmate's workspace and rebuild
- **Context**: User's `dexbot_interfaces_mid` was missing these two message types required by classmate's Phase2 forwarding logic
- **Source**: `/home/tbl/桌面/dexbot_ros2_ws/src/dexbot_interfaces/dexbot_interfaces_mid/msg/`
- **Target**: `/home/tbl/Project/dexbot_ros2_ws/src/dexbot_interfaces/dexbot_interfaces_mid/msg/`
- **Changes made**:
  - Copied `ObstacleBox.msg` and `TableWorkspace.msg`
  - Updated `CMakeLists.txt`: added messages to `rosidl_generate_interfaces`, added `builtin_interfaces` dependency
  - Updated `package.xml`: added `<depend>builtin_interfaces</depend>`
  - `colcon build --packages-select dexbot_interfaces_mid` succeeded
- **Evidence / Verification**: Build passed; `ros2 interface show dexbot_interfaces_mid/msg/ObstacleBox` confirmed working
- **Impacted nodes**: `xcore_monitor_handle_sequence_node.py`, `xcore_follow_tcp_chain_node_movej.py`
- **Status**: active

## 2026-05-19 - xCore SDK Binary Copied from Classmate's Workspace

- **Decision**: Copy `xcoresdk_python-v0.5.1.ar_12/` directory from classmate's workspace to user's workspace
- **Context**: User's workspace lacks the xCore SDK binary (`xCoreSDK_python.cpython-310-x86_64-linux-gnu.so`), which is required by `xcore_follow_tcp_chain_node_movej.py` for NRT direct arm control
- **Source**: `/home/tbl/桌面/dexbot_ros2_ws/src/dexbot_bottom_layer/dexbot_bottom_layer/xcoresdk_python-v0.5.1.ar_12/`
- **Target**: `/home/tbl/Project/dexbot_ros2_ws/src/dexbot_bottom_layer/dexbot_bottom_layer/xcoresdk_python-v0.5.1.ar_12/`
- **Reason**: Classmate's SDK is verified working; copying is faster and more reliable than downloading or rebuilding
- **Compatibility**: Both workspaces use Python 3.10; SDK binary is `cpython-310-x86_64-linux-gnu.so` — compatible
- **Evidence / Verification**: Binary files confirmed identical via recursive diff of `Release/` and `example/` directories
- **Impacted nodes**: `xcore_follow_tcp_chain_node_movej.py`
- **Impacted edges**: phase1-grab-migration execution chain
- **Status**: active

## 2026-05-19 - Hardcoded Paths Replaced with Relative Paths

- **Decision**: All hardcoded absolute paths in migrated classmate code will be replaced with relative paths based on package location
- **Context**: Classmate's code contains hardcoded paths like `/home/a/Desktop/dexbot_ros2_ws/src/config1/calibration_result.yaml` and `/home/kim/projects/dexbot_ros2_ws/...` which are specific to their machine
- **Implementation approach**:
  - Use `os.path.dirname(os.path.abspath(__file__))` to get current file's directory
  - Navigate relative to package root: `os.path.join(PKG_DIR, '..', '..', '..', 'config', 'calib_right', 'calibration_result_right.yaml')`
  - For calibration files: resolve relative to `dexbot_middle_layer` package root, then to user's `config/calib_right/`
  - For xCore SDK: resolve relative to `dexbot_bottom_layer` package root
- **Affected files**:
  - `cut_tofu_object_recognition_node.py`: default calibration file path
  - `xcore_monitor_handle_sequence_node.py`: default calibration file path
  - `xcore_follow_tcp_chain_node_movej.py`: default xCore SDK root path
  - `README.md`: launch command examples (documentation only)
- **Alternatives considered**:
  - (a) Hardcode user's paths — rejected: fragile, breaks if workspace moves
  - (b) Pass all paths via launch file parameters — rejected: too many parameters, error-prone
  - (c) Relative paths based on `__file__` — **selected**: robust, self-contained, works across machines
- **Evidence / Verification**: Path resolution tested at runtime; fallback to launch file parameters if relative path fails
- **Impacted nodes**: All 3 migrated classmate nodes
- **Impacted edges**: phase1-grab-migration execution chain
- **Status**: active

## 2026-05-17 Local Time (规划最终定稿 — 用户画框方案)

- **Decision**: 用户拖拽画框 → BOX MODE / 删框 → TEXT MODE
- **问题**: 豆腐切割后形态改变，文本提示可能检测失败
- **方案**: 用户在相机画面拖拽画框，框存在期间 SAM3 用该框做分割，框删除后回退文本自动检测
- **核心变化 vs 旧点→BBox 方案**:
  - 用户操作: 拖拽画框 (非固定40px)
  - 无推理锁: 单一 auto_detect_callback 统一处理 BOX/TEXT 切换
  - 模式切换: 框存在=BOX, 框删除=TEXT (用户手动右键删除)
  - 无自动恢复: BOX 检测失败保持框，用户决定何时删
- **ROS Topic**: `/sam3/user_box` (sensor_msgs/RegionOfInterest)
- **可视化**: 用户框=黄色, SAM3结果=绿色 (不变)
- **Interaction**:
  - 左键拖拽 → 画框 (BOX MODE)
  - 右键点击 → 删框 (回退 TEXT MODE)
  - 拖拽太小(<5px) → 忽略
- **Plan file**: `sam3-point-prompt-research.md` 章节 8 (完整代码模板)
- **Status**: **planned** (规划完成，待实现)
