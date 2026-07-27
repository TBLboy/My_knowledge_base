# Business Logic Decision Records

## 2026-05-23 - Constrained OBB Objective Is Top ABCD Footprint, Not Full 3D Box

- **Decision**: Treat constrained OBB as a top-surface footprint estimator for tofu ABCD corners, not as a strict full-body 3D bounding-box estimator.
- **Context**:
  - Current constrained OBB uses cleaned eroded points for yaw, but full-mask uncleaned bounds points for final box dimensions.
  - User clarified that the task does not need the box to enclose the entire tofu body. The critical output is accurate top ABCD corners for Phase2 prepare and cutting alignment.
  - Truncating lower tofu points is acceptable if the top footprint and long-edge direction are improved.
- **Candidate refinement recorded**:
  - Keep yaw estimation unchanged: cleaned eroded fit points -> XZ exhaustive yaw search.
  - For final bounds, filter full-mask `bounds_points_base` by base Y and keep the highest portion of points.
  - Initial candidate parameter: `obb_bounds_top_keep_ratio = 0.8`.
  - Estimate top height from retained points with `obb_top_y_percentile = 99.0`.
  - Use retained top-footprint points for OBB length/width, while treating lower box height as secondary.
- **Alternatives considered**:
  - Keep full-mask bounds for full-body enclosure - rejected as the primary objective because lower/side/noisy points can expand top ABCD and Phase2 does not require full-body enclosure.
  - Reintroduce previous top-surface percentile bounds experiment - rejected as-is because it caused jitter/non-rectangular-looking RViz behavior; any new attempt must keep yaw estimation unchanged and avoid UV percentiles initially.
- **Risks / Notes**:
  - If edge/top points have lower Y due to depth noise or calibration tilt, an aggressive top ratio may shrink the footprint.
  - The ratio must be configurable and verified in RViz/hardware; this is not yet implemented.
- **Evidence / Verification**: Business logic recorded only; no code changes or tests run.
- **Impacted nodes**: PHASE_2_MOVE_TO_PREPARE
- **Impacted edges**: edge_2_prepare perception subchain
- **Status**: candidate, not implemented, not validated

## 2026-05-20 - Phase2/Phase6 Prepare Search Uses Real xCore SDK Kinematics Instead of URDF

- **Decision**: Replace Phase2/Phase6 prepare search kinematics backend from `OfflineURDFKinematics` to a real xCore SDK-backed adapter (`XcoreSdkKinematics`).
- **Context**:
  - User has the real arm and matching SDK and wants search to use the real mechanical-arm model instead of URDF.
  - Existing prepare logic already has valuable behavior: multi-seed candidate search, future cut preview, 15° joint-margin filtering, and scoring.
  - The desired change is backend fidelity, not a change to search priorities.
- **Implementation**:
  - Added `cuttofo_xcore/xcore_sdk_kinematics.py`.
  - `fk_matrix(q)` calls xCore SDK FK through `XCoreLbotRobot.compute_forward_kinematics()`.
  - `joint_bounds()` reads controller soft limits when possible; falls back to xMate Er Pro joint limits if unavailable.
  - `knife_prepare_action_server.py` now constructs `XcoreSdkKinematics` and passes it into the existing `solve_prepare_candidates()` / `rollout_cut_preview()` / `score_preview_trajectory()` pipeline.
  - `execute_prepare_pose.py` uses the same SDK backend for standalone prepare-search debugging.
- **Alternatives considered**:
  - Keep URDF backend — rejected by user preference for real SDK model.
  - Replace the entire search with SDK single-shot `calcIk()` — rejected because it would lose current multi-candidate preview scoring.
  - Add a ROS service for every FK/IK call — deferred because thousands of FK calls through services would be slow; direct SDK model adapter is smaller and preserves the existing optimizer.
- **Risks / Notes**:
  - Current implementation opens an SDK connection for kinematics in the prepare server; hardware testing must confirm this does not conflict with the running xCore controller process.
  - The SDK backend is syntax-verified but not yet hardware-verified in Phase2/Phase6.
- **Evidence / Verification**: `python3 -m py_compile` passed for modified files.
- **Impacted nodes**: PHASE_2_MOVE_TO_PREPARE
- **Impacted edges**: edge_2_prepare
- **Status**: active, hardware verification pending

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

---

## 2026-05-28 - Vision Pipeline Improvement Branch: Constrained OBB

- **Decision**: Create exploratory branch `feature-constrained-obb-vision` to design and validate a new pose estimation pipeline that fits a yaw-only oriented bounding box (OBB) to tofu point cloud, improving stability and tightness compared to current AABB/PCA approach.
- **Context**:
  - Current vision pipeline uses AABB or full 6DoF PCA, leading to jittery or loose bounding boxes.
  - Physical prior: tofu rests flat on a plate; its top surface is approximately parallel to base_xz plane. This constraint allows reducing pose自由度 from 6 to 4 (yaw-only rotation + 3D center).
  - Goal: more stable `top_corners` and `edge_dir` for Phase2 prepare, without changing downstream consumption.
- **Implementation**:
  - Modify `dexbot_middle_layer/vision/pipeline/vision_utils.py`:
    - Add `clean_point_cloud()` (Open3D or numpy) with Voxel, SOR, ROR, DBSCAN (largest cluster).
    - Add `fit_constrained_obb_xz()` (exhaustive yaw search on XZ projections to minimize area).
    - Extend `get_pose_from_mask()` with parameters: `mask_erode_px`, `obb_margin`, `obb_angle_step_deg`, cleaning parameters, and depth preprocessing parameters.
    - When `corner_mode="constrained_obb"`, execute erosion, depth preprocessing, cleaning, OBB fit, then return derived `top_corners` and `edge_dir`.
  - Modify `dexbot_middle_layer/pose_estimator_node.py`:
    - Declare and store new OBB-related parameters.
    - Pass them through to `get_pose_from_mask`.
    - Maintain an optional synchronized depth median buffer for the OBB path.
  - Modify launch/config wiring:
    - Add OBB parameters under `vision:` in `cuttofo_config.yaml`.
    - Forward all OBB/depth parameters through `cuttofu_phase2.launch.py` and `viz_display.launch.py`.
  - Keep `corner_mode` default `"aabb"` in main to preserve existing behavior; branch-specific config will set `"constrained_obb"`.
- **Alternatives considered**:
  - (a) Continue using AABB — rejected: larger volume, less accurate alignment when tofu tilted slightly.
  - (b) Full 6DoF PCA OBB — rejected: jittery, may violate flat assumption, output unstable.
  - (c) Constrained OBB with exhaustive search — **selected**: respects physical prior, yields stable yaw-only orientation, computationally manageable.
  - (d) Use RANSAC plane+OBB — not pursued due to additional complexity and potential instability on partial views.
- **Risks**:
  - Performance: OBB search ~360 iterations per frame may exceed 200ms on target hardware; may need larger `angle_step_deg` or vectorized optimization.
  - Cleaning may over-filter; fallback to AABB must be robust.
  - Tofu not perfectly flat; OBB top surface may deviate > threshold; may need fallback to PCA if residual pitch/roll > 5°.
- **Verification**:
  - Offline unit tests: volume reduction ≥20%, point inclusion ≥0.98, top surface normal error <5°.
  - Hardware integration: Phase2 prepare success rate ≥95% over 20 runs; `edge_dir` jitter <0.05 rad; Phase3 cuts collision-free.
- **Merge conditions**:
  - Offline and hardware tests passed.
  - Performance <200ms average on target PC.
  - Fallback validated (AABB works if OBB fails).
  - All parameters documented in `config/config-schema.md`.
  - No undefined business logic remains.
- **Impacted nodes**: PHASE_2_MOVE_TO_PREPARE (internal implementation of `edge_2_prepare`'s perception step)
- **Impacted edges**: edge_2_prepare
- **Status**: implemented, build-checked, awaiting offline/hardware validation


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

## 2026-05-21 — Tofu Detection Precision Error Budget: 10-30mm Total at Blade

- **Decision**: Three systemic error sources identified and prioritized. Static scene confirmed — optimize for per-frame absolute accuracy, not dynamic tracking.
- **Context**:
  - Hand-eye calibration: 2.73mm / 2.13° RMSE (8 samples). Historical best: 1.5mm / 1.13° (10 samples).
  - TCP calibration: offset `[0.023, 0.15, 0.292]`, RMSE unknown, not saved to config.
  - Tofu vertex detection: SAM3 threshold 0.005 (too low), AABB z_percentile 99.0% vs X 99.9% (asymmetric), double smoothing ~2s lag (irrelevant for static scene).
  - Estimated total blade uncertainty: 10-30mm RSS.
- **Fix priority**:
  - **P0**: Redo hand-eye calibration (15+ samples, target RMSE < 2mm / < 1.5°)
  - **P0**: Redo TCP calibration with RMSE tracking (target < 2mm)
  - **P1**: Raise SAM3 threshold from 0.005 to ~0.3 (cross-check: Phase1 grab uses 0.3)
  - **P1**: Fix AABB z_percentile_high from 99.0% to 99.9% (match X edges)
  - **P2**: Reduce tofu_state buffer from 15 to 5 frames
  - **P3**: Auto-save TCP calibration RMSE to config
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

## 2026-05-21 — Right-Arm Calibration File Switched to New Format

- **Decision**: Replace active right-arm hand-eye calibration from `config/calib_right/calibration_result_right.yaml` (old, 8 samples, 2.73mm/2.13°) to `config/calib_right/calibration_result.yaml` (new, 10 samples, 0.00318m/1.19°).
- **Context**: New calibration was produced by improved solver (Shah/Li init + MAD 3.5σ + Huber LM) and has better RMSE and more samples. New YAML output format differs from old format, requiring all calibration loaders across the workspace to support 4 format variants.
- **Approach**: Rather than converting the new file to the old format, added multi-format `_extract_T_base_cam()` parser to every calibration loader in the workspace. The new file is the default; old format still loads for backward compatibility.
- **Format variants supported**:
  1. `T_base_cam: [[4×4]]` (top-level)
  2. `T_base_cam: {matrix: [[4×4]]}` (top-level dict)
  3. `calibration_result.T_base_cam` (nested list)
  4. `calibration_result.rotation_matrix + translation_vector` (legacy)
- **Files parsed**: 7 launch/nodes across `cuttofo_xcore`, `dexbot_middle_layer/CutTofo`, `dexbot_middle_layer/`, `dexbot_toolbox/visualization/`, `dexbot_toolbox/calibration/`
- **Alternatives considered**: Convert new file to old format — rejected because the new format is more structured and the solver already emits it natively.
- **Evidence / Verification**: Multi-format parser test against all 4 variants passed; `colcon build` passed for all 3 modified packages; workspace grep for old filename path: 0 hits in runtime code.
- **Impacted nodes**: PHASE_1_GRAB, PHASE_2_MOVE_TO_PREPARE, perception sub-nodes
- **Impacted edges**: edge_1_grab, edge_2_prepare, perception pipeline edges
- **Status**: active, hardware verification pending (Note: later found original comparison was against a backup that was also old; see next decision)

## 2026-05-21 — Phase1 Follow Node Replaced with Optimized (1) Version

- **Decision**: Full replacement of `xcore_follow_tcp_chain_node_movej.py` with the student's actual optimized (1) version. Previous hash-based match was against an outdated backup — not the student's real optimized copy.
- **Context**:
  - Hardware test showed each of 5 approach waypoints taking 6-11s, with the total grab sequence lasting ~110s.
  - The root cause was that the old follow node did not have `sequence_skip_joint_converge_wait`, `target_pose_skip_joint_converge_wait`, or `move_abs_joints_skip_joint_converge_wait` — every waypoint waited for extra joint convergence after SDK idle.
  - Student's (1) version also includes `_follow_dir_as_source`, `resolve_linkerbot_sdk_src`, `set_joint_converge_skip_override`, `set_joint_converge_tol_override`, `_log_move_block_timing`, and improved `_wait_motion_done` → these were all missing from the old version.
- **Implementation**:
  - Copied full (1) file from `/home/tbl/Project/xcore_follow_tcp_chain_node_movej(1).py`.
  - Added back Phase1 cleanup logic in `_XCoreNrtDirect.disconnect()` (toolset restore → stop → NrtCommandMode) to preserve the Phase3 twitch fix.
  - Aligned all monitor/config/launch/lifecycle parameter defaults to student's tuned values (y_before=0.13, y_step=0.11, O6=0,0,80, target_y=-0.02).
  - Removed extraneous follow params from internal launch: `tail_approach_enabled`, `lock_joint6_during_move`.
- **Evidence / Verification**: `python3 -m py_compile` passed; `colcon build` passed.
- **Impacted nodes**: PHASE_1_GRAB_KNIFE
- **Impacted edges**: phase1-grab-migration execution chain
- **Status**: active, hardware verification pending — expect 5 waypoints in ~10s total, not ~110s
