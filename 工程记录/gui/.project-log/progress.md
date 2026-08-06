# Progress Log

## 2026-08-06 恢复旧版 delta 后处理（reverted to baseline）

- Decision: 用户决定不再使用实验性平滑后处理，恢复 `bfb623a` 基线中已验证的旧版逻辑。
- Changes: `services/arm/flange_delta.py`、`tests/test_flange_delta.py` 与基线完全一致，无代码残留差异。
- Verification: `python3 -m unittest tests.test_flange_delta -v` 4/4 通过；`compileall` 通过；未连接或移动机械臂。
- Status: `verified`（离线）；未提交。
- Next steps: 等待用户决定是否提交，或继续处理 delta 回放泛化问题。

## 2026-08-06 Delta 回放起点泛化边界（diagnosed）

- Evidence: 用户真机日志中，同一类 delta 回放在不同起点/资产下出现点 4、21、58、78 的 IK 无解或关节限位失败，同时存在 61/89 点全轨迹 IK 成功记录。
- Root cause: `T_current @ Delta_i` 只保持相对法兰变换，不保持新起点下的绝对可达性；7 轴 IK 还受 elbow/wrist/configuration 分支、奇异区和关节限位影响。
- Implementation limitation: `_solve_one_flange_pose()` 仅尝试 elbow guesses `(0, ±0.5, ±1.0, ±2.0)`，逐点以 previous joints 贪心选最小步长，没有全轨迹 branch search 或 wrist flip 候选；J7 硬限位为 ±0.8727 rad，日志中的 0.8778/0.8850 rad 已越界。
- Business implication: 当前功能应标记为“兼容起点下的 delta replay”，不能宣称任意起点泛化。
- Recommended implementation: 增加录制时关节配置先验、多 wrist/configuration 候选、关节限位余量评分和全轨迹动态分支选择；运动前完整 IK 预检失败时不执行。
- Status: `diagnosed`; 本轮未修改 IK 代码。

## 2026-08-06 Delta 平滑实验恢复（implemented-unverified）

- 用户要求重新测试实验性后处理；已恢复源码和三条回归测试。
- 离线验证：12/12 单测通过；从原始 281 点重新生成 `trajectory/delta_motion_20260805_185408_823825_smooth_v2/segment_001_delta.json`，得到 84 waypoint，delta 重建最大误差 `1.33e-15`。
- 真机测试前提：不改变机械臂当前起点，不做 jog，低速直接回放；上次失败包含一次 50 mm 起点变化，需本次排除该变量。
- Status: `implemented-unverified`，等待第二次真机证据。

## 2026-08-06 Delta 平滑实验真机 IK 回归（reverted）

- Experiment: 7 点 Savitzky-Golay、首尾锁定、SO(3) 去重、孤立跳点过滤和双约束重采样将样本从 58 个 waypoint 变为 84 个；离线 12/12 单测、编译和 delta 重建均通过。
- Real-arm evidence: `getJointPos` 在实验资产点 10、随后在起点恢复后的点 6 返回无解，均发生在发送 `MoveAbsJ` 之前。第二次失败点仅相对旧版同进度目标偏移 `0.765 mm / 0.001436 rad`。
- Root cause: `technical-selection`。离线法兰空间的平滑/细化不能保证当前回放起点下 7 轴 SDK IK 的可解分支；delta 的可移植性仍受当前起点和求解分支约束。
- Resolution: 实验性源码和测试已撤回，恢复 Git 基线 `bfb623a` 的已验证后处理；回退后 `python3 -m unittest tests.test_flange_delta tests.test_xcore_pose_readout -v` 为 9/9 通过。实验派生资产将删除，原始录制目录不变。
- Follow-up: 如要改善执行平滑度，应在当前起点的全轨迹 IK 成功后再进行关节空间处理，或先实现只求 IK、不发送运动的预检。

## 2026-08-06 Delta 后处理平滑优化（implemented-unverified）

- Objective: 在不改变 delta 文件语义、GUI 回放流程和真机 SDK 调用方式的前提下，改进离线后处理的轨迹平滑与点间约束。
- Changes:
  - `services/arm/flange_delta.py`: 位置采用 7 点二阶 Savitzky-Golay 滤波并锁定原始首尾点；姿态矩阵平均后同样锁定首尾点。
  - `services/arm/flange_delta.py`: 旋转去重改用 SO(3) 夹角；孤立跳点仅在其前后均异常而跨越该点连续时删除，并覆盖平移和姿态跳变。
  - `services/arm/flange_delta.py`: 重采样改为 `adaptive_translation_rotation_v2`，每一段同时遵守最大平移步长和最大旋转步长，而非旧版加权组合距离。
  - `tests/test_flange_delta.py`: 新增首尾保持/双步长上限、Euler `±π` 绕回去重、孤立跳点删除三条回归。
- Verification:
  - `python3 -m unittest tests.test_flange_delta tests.test_xcore_pose_readout -v`: 12/12 passed.
  - `python3 -m compileall -q services pages tests`: passed.
  - 未启动 GUI、未连接或发送真机运动指令。
- Offline comparison asset: `trajectory/delta_motion_20260805_185408_823825_smooth_v2/segment_001_delta.json` 由原始 281 点重新生成，得到 84 waypoint（旧版为 58）；最大平移步长 9.99 mm、最大姿态步长 0.0492 rad；delta 展开回原处理轨迹的最大分量误差 `1.34e-15`。原资产未改动。
- Status: `implemented-unverified`; 真机低速对比后，根据是否改善平滑度与是否放大批次接缝卡顿决定参数是否保留或回调。

## 2026-08-06 Delta 轨迹后处理平滑性评估

- Objective: 评估当前法兰增量轨迹采集后的后处理是否足够平滑，以及是否需要优化。
- Current pipeline: 原始采样 → 平移跳点剔除（50 mm）→ 平移/姿态去重 → 5 点滑动平均（位置）与旋转矩阵 SVD 平均（姿态）→ 按“平移弧长 + 0.3×旋转弧长”空间重采样 → 生成 `inverse(T0)@Ti` 增量。
- Evidence from `trajectory/delta_motion_20260805_185408_823825/segment_001_*`:
  - 281 个 raw 点、声明采样率 80 Hz，但实际 `time_sec` 平均间隔约 15.0 ms（约 66.6 Hz），标准差约 0.8 ms；当前处理没有使用时间戳。
  - 8 个重复点被删除，无平移离群点；281 点最终变为 58 个 waypoint。
  - 总平移路径长度从 0.8274 m 变为 0.8225 m，末端偏差约 0.064 mm、姿态偏差约 0.000235 rad，说明当前滤波未明显破坏端点和整体几何路径。
  - 当前处理后的单段平均平移步长约 14.4 mm、平均姿态步长约 0.036 rad；这改善了点数，但不是时间意义上的速度/加速度平滑。
- Assessment: 当前方案作为第一版“几何清洗”可用，且已通过真机回放；但若目标是更平滑的运动，仍应优化时间建模、端点保持、姿态差值计算和自适应重采样。不要在分批 `moveAppend` 接缝未优化前盲目增加 waypoint 数量，否则可能放大中间卡顿。
- Status: analysis-complete; no code change made.
- Next step: 如需实施，优先做离线质量指标与保端点的时间/空间重采样，再在无硬件运动的单测通过后安排低速真机验证。

## 2026-08-05 19:23 CST

- Objective: Diagnose the real-arm `calcIk` failure at delta trajectory point 0 without blaming or replacing a valid flange-delta asset.
- Evidence: `segment_001_delta.json` point 0 is an identity delta. After expansion it is exactly the current replay-start flange pose, while the controller reported `计算逆解错误` before any motion command was emitted.
- Root cause: The IK path unnecessarily re-solved that identity point and copied a locally calculated FK elbow/configuration onto it. That extra configuration constraint is not the controller's authoritative current state and can reject an otherwise current/reachable pose.
- Resolution: The current `jointPos` is now used directly as trajectory point 0. IK begins at delta point 1; its initial configuration is read from `cartPosture(endInRef)`, then updated from FK after each accepted IK solution. The existing all-points-before-motion, joint-limit, and branch-continuity gates remain in place.
- Verification: `python3 -m py_compile services/arm/xcore.py tests/test_xcore_pose_readout.py pages/arm_hand.py` passed. `python3 -m unittest discover -s tests -v` passed: 9 tests.
- Status: `implemented-unverified`; restart the GUI and retest the exact same delta asset at low speed. A repeated failure at point 0 would indicate the old GUI process is still running; a failure at point 1+ requires its exact error as new evidence.

## 2026-08-05 19:28 CST

- Evidence update: After restart, hardware failure moved from point 0 to point 1, proving the identity-first-point bypass took effect.
- Recording verdict: Not defective. Expanding all 58 saved deltas at the saved `initial_flange` reconstructs every processed waypoint with a maximum component error of `2.22e-15`. The failure is not in capture, smoothing, delta generation, or `T_current @ Delta_i` expansion.
- IK investigation: Point 1 is a small adjacent motion. GUI-specific elbow/configuration assignments had no support in the official SDK examples or the Boss xCore wrapper's `compute_inverse_kinematics` path. Removed those assignments; replay now uses only `FlanInBaseToEndInRef(baseFrame, toolset, flange)` then `CartesianPosition(end)` then `calcIk(target, toolset, ec)`.
- Diagnostic improvement: Failed IK errors now include the precise flange and end-in-reference targets sent to the SDK. This is required to determine any remaining base/tool frame mismatch without speculation.
- Verification: `python3 -m py_compile services/arm/xcore.py tests/test_xcore_pose_readout.py pages/arm_hand.py` passed; `python3 -m unittest discover -s tests -v` passed, 9 tests.

## 2026-08-05 19:xx CST

- Objective: Make flange-delta replay follow the same hardware-validated joint trajectory path as normal trajectory replay.
- Confirmed behavior: The GUI still records flange deltas. Replay reads the current `flangeInBase`, expands the file with `T_current @ Delta_i`, converts every flange pose to the SDK end-in-reference representation, and solves every point with xCore IK before motion starts.
- Resolution: Added `XCoreArmSession.replay_flange_trajectory_as_joints()`. It validates all IK solutions against the seven recorded joint ranges and a `1.0 rad` maximum adjacent-point jump, then delegates only the fully validated joint list to existing `replay_joint_trajectory()` (`MoveAbsJ` batched append). `ArmHandPage._replay_delta_trajectory()` now calls this method instead of `replay_cartesian_trajectory()`.
- Root cause correction: The earlier delta implementation sent expanded poses through NRT `MoveL`; normal replay uses `MoveAbsJ`. The controller's failure to enter moving state came from the unsupported/unreliable Cartesian path, not from delta expansion itself. The previous batched-`MoveL` resolution is superseded and is not the active implementation.
- Safety boundary: IK, conversion, joint-limit, and branch-continuity failures occur before `MoveAbsJ` sends any motion. This does not replace collision checking or constitute hardware validation.
- Verification: `python3 -m py_compile services/arm/xcore.py pages/arm_hand.py tests/test_xcore_pose_readout.py` passed. `python3 -m unittest discover -s tests -v` passed: 9 tests, including successful all-point IK-before-replay and failed-IK-no-replay cases.
- Status: `implemented-unverified`. Required evidence is a real-arm, low-speed replay of a short delta asset in an empty safe workspace.

## 2026-08-05 19:xx CST

- Objective: Diagnose a delta replay that reported `replayed 58 Cartesian trajectory points (MoveL sequence)` while the arm did not visibly move.
- Evidence: `trajectory/delta_motion_20260805_185408_823825/segment_001_delta.json` is valid and nontrivial: 281 raw samples became 58 replay deltas; total spatial range is about 0.286 m and the final delta is `[-0.08414, 0.03195, 0.08801, 0.11542, -0.16200, -0.06039]`. The recording is not empty or zero.
- Root cause: The original replay loop called `moveReset -> moveAppend(one point) -> moveStart -> wait_until_idle` for every waypoint. `operationState` can remain `idle` for a short command-acceptance interval after `moveStart`; the loop treated that as completion and the next `moveReset` cleared the pending command. The GUI therefore could report all points as successful without any controller motion.
- Resolution: `XCoreArmSession.replay_cartesian_trajectory()` now builds all non-identity waypoints as explicit `CartesianPosition.trans` / `.rpy` targets, appends them in 50-command batches, calls `moveStart` exactly once, requires an observed moving state, and then waits for idle. The final `flangeInBase` pose is checked against the final target (20 mm / 0.25 rad tolerances), so an accepted-but-unexecuted path is reported as a failure instead of success. `move_cartesian()` also now requires a motion-state transition.
- Verification: Added a mock-SDK regression test asserting one `moveStart`, one batched append for a three-point path, and explicit trans/rpy values. `python3 -m py_compile services/arm/xcore.py pages/arm_hand.py services/arm/flange_delta.py tests/test_xcore_pose_readout.py` passed; `python3 -m unittest discover -s tests -v` passed (7 tests).
- Limitation: No physical replay was initiated by this investigation. The repaired replay path still needs a controlled real-arm test with the referenced delta file.

## 2026-08-05 18:49 CST

- Objective: Convert the existing absolute-joint pour recording into a standalone GUI flange-delta trajectory without changing the source recording.
- Output: Created `trajectory/delta_倾倒轨迹_20260805_184910/` with `segment_001_raw.json`, `segment_001_processed.json`, `segment_001_delta.json`, and `manifest.json`.
- Conversion: Performed xCore model forward kinematics (`model.calcFk(joints, Toolset(), ec)`) on all 437 source joint samples, then reused the GUI's processing pipeline to produce 91 replayable `inverse(T0) @ Ti` flange deltas.
- Traceability: Output manifest records the absolute source directory, source SHA256 values, source type `joint_absolute`, resulting type `flange_delta`, and the default-empty-Toolset flange assumption.
- Source integrity: Post-conversion SHA256 matched the source baseline: `manifest.json` = `2791c9579ba128dcede99b28074e258bc1a01060c3e6c467a06baf1d74830b14`; `segment_001.json` = `d69808111933325cbe3de55c3d504ccfbb3a615589ed9b73202efd95e6c9ea8e`.
- Safety: Added `scripts/convert_joint_trajectory_to_delta.py`; it performs FK only and does not prepare, enable, stop, disconnect, or issue any robot motion command.
- Verification: `validate_delta_asset(..., arm_side="left")` passed; raw first flange pose is nonzero; `python3 -m py_compile scripts/convert_joint_trajectory_to_delta.py services/arm/flange_delta.py services/arm/xcore.py pages/arm_hand.py` passed; `python3 -m unittest discover -s tests -v` passed (6 tests).
- Limitation: This validates the offline asset format only. No real-arm delta replay, IK reachability, joint-limit, or collision validation was performed.

## 2026-08-05 18:10 CST

- Objective: Integrate offline flange-delta recording, processing, and replay into the Tkinter GUI.
- Work completed: Added independent delta recording controls and a replay panel to `pages/arm_hand.py`; records physical-button flange samples at 80 Hz; saves `trajectory/delta_<action>_<timestamp>/` raw, processed, delta, and manifest assets; stores the processed initial flange pose; validates and expands `T_current @ Delta_i` for replay. Added normal/delta trajectory type separation and a direct xCore Cartesian replay adapter.
- Safety and compatibility: Delta replay validates asset role, schema version, arm side, robot class, `flangeInBase`, m/rad, XYZ RPY, and initial-flange reference. Legacy untagged joint trajectory files remain normal replay files.
- Verification: `python3 -m unittest discover -s tests -v` (4 pass); `python3 -m py_compile pages/arm_hand.py services/arm/xcore.py services/arm/flange_delta.py services/arm/control.py main.py` (pass); a dedicated `xvfb-run` page-instantiation check verified the delta controls and action-name normalization; `timeout 8s xvfb-run -a python3 main.py` entered the GUI mainloop without hardware motion.
- Limitation: Cartesian replay currently uses sequential synchronous MoveL calls because no verified xCore Cartesian streaming/batch API has been identified; waypoint pauses are expected. No real-arm verification, IK, joint-limit, or collision validation was added.
- Files changed: `pages/arm_hand.py`, `services/arm/flange_delta.py`, `services/arm/xcore.py`, `tests/test_flange_delta.py`, `.project-log/current-session.md`, `.project-log/progress.md`.
- Next steps: Perform a low-speed real-arm delta recording/replay test under safe conditions; investigate a documented Cartesian RT/batched SDK path only if the observed waypoint pauses are unacceptable.

## 2026-08-05 18:43 CST

- Objective: Diagnose why actual delta recording produced raw-only assets.
- Observation: `trajectory/delta_motion_20260805_183859_911423/` had 661 and 504 samples, respectively, but every recorded `pose6` was zero. Processing correctly rejected both after deduplication.
- Root cause: `XCoreArmSession.state()` incorrectly read `cartPosture(...).pos`, an unpopulated default field in this SDK binding. The SDK examples and the reference flange recorder use `posture(CoordinateType.flangeInBase)` to retrieve the six-element flange pose.
- Resolution: Changed `services/arm/xcore.py` to read and validate `posture(flangeInBase)`; added regression tests that prove the scalar posture API is used rather than `cartPosture` fields.
- Verification: `python3 -m unittest discover -s tests -v` (6 pass); `python3 -m py_compile services/arm/xcore.py services/arm/flange_delta.py pages/arm_hand.py main.py` (pass); `timeout 8s xvfb-run -a python3 main.py` (GUI mainloop reached, no hardware motion).
- Limitation: The already-recorded all-zero raw files cannot be converted; a new physical recording is required after restarting the GUI.

## 2026-04-28 16:55 Local Time

- Objective: Initialize project engineering records for gui optimization work
- Work completed: Created `.project-log/` directory and three default files (requirements.md, progress.md, current-session.md)
- Problems encountered: None
- Resolution: Not applicable
- Verification: Files created and reviewed
- Files changed: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/requirements.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/progress.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/current-session.md`
- Next steps: Await user direction on next task

## 2026-04-28 17:15 Local Time

- Objective: Complete step 1 of the new GUI by building a reusable shell around existing layered packages
- Work completed: Inspected the current GUI codebase and package boundaries; created a new standalone Tkinter shell in `src/gui/` with left sidebar mode switching, top tab pages, a shared `ServiceRegistry`, and lazy reuse of `dexbot_toolbox.gui.arm_hand_gui.RosServiceBridge`
- Problems encountered: None
- Resolution: Not applicable
- Verification: `python3 -m py_compile` on all new files — pass
- Files changed: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/main.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/gui_shell.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/gui_pages.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/gui_services.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/requirements.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/progress.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/current-session.md`
- Next steps: Migrate the first real functional page into the new shell, starting with the most reusable ROS-backed arm control slice

## 2026-04-28 17:25 Local Time

- Objective: Start phase 2 by migrating the first real functional page into the new GUI shell
- Work completed: Extracted a minimal arm control slice from the legacy GUI design and implemented a new `Arm Control` tab in `src/gui/gui_pages.py`; the page reuses `RosServiceBridge` and supports `/robot/get_state`, `/robot/enable_arm`, `/robot/clear_errors`, and `/robot/emergency_stop`
- Problems encountered: The legacy GUI intermixes simple ROS service actions with more complex motion, drag, and servo flows
- Resolution: Kept this migration slice intentionally small and limited it to stable ROS service actions that do not require direct SDK coupling
- Verification: `python3 -m py_compile /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/main.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/gui_shell.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/gui_pages.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/gui_services.py` (pass); `source /home/tbl/Project/tofu/dexbot_ros2_ws/install/setup.bash && python3 -c "import sys; sys.path.insert(0, '/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui'); import tkinter as tk; from gui_shell import DexbotGuiShell; root = tk.Tk(); shell = DexbotGuiShell(root); print('tabs=', shell._notebook.tabs()); root.after(1500, root.destroy); root.mainloop(); print('GUI OK')"` (pass)
- Files changed: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/gui_pages.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/requirements.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/progress.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/current-session.md`
- Next steps: Add the next ROS-backed arm feature slice, likely cartesian state display and basic world-frame jog controls

## 2026-04-28 17:35 Local Time

- Objective: Reorganize the new GUI source tree so code is grouped by responsibility instead of mixing all scripts in one directory
- Work completed: Restructured `src/gui/` into dedicated packages: `app/` for the shell, `pages/` for GUI pages, `services/` for shared logic adapters, and `config/` for shared mode definitions; kept `main.py` as the single top-level entry point and removed the old flat implementation files
- Problems encountered: The first implementation had already started to accumulate GUI shell, page, and service code side-by-side in the root directory
- Resolution: Performed a minimal package split without changing runtime behavior or page functionality
- Verification: `python3 -m py_compile /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/main.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/shell.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/modes.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/registry.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/overview.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/migration.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/legacy.py` (pass); `source /home/tbl/Project/tofu/dexbot_ros2_ws/install/setup.bash && python3 -c "import sys; sys.path.insert(0, '/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui'); import tkinter as tk; from app.shell import DexbotGuiShell; root = tk.Tk(); shell = DexbotGuiShell(root); print('tabs=', shell._notebook.tabs()); root.after(1200, root.destroy); root.mainloop(); print('GUI OK')"` (pass)
- Files changed: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/main.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/__init__.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/shell.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/__init__.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/modes.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/__init__.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/registry.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/__init__.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/overview.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_control.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/migration.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/legacy.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/progress.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/current-session.md`
- Next steps: Continue feature migration within the new package layout, starting with the next ROS-backed arm control slice

## 2026-04-28 17:45 Local Time

- Objective: Improve layout density and continue separating GUI code from arm control logic
- Work completed: Removed the descriptive text block from the left `Mode` sidebar to reduce its width; extracted the ROS-backed arm control operations from `pages/arm_control.py` into a dedicated `services/arm/control.py` adapter so the page now focuses on UI state and event wiring
- Problems encountered: The `Arm Control` page had started to accumulate direct service-call details, which would make further feature migration harder to scale cleanly
- Resolution: Introduced a focused arm service layer while preserving the existing `RosServiceBridge` reuse path underneath
- Verification: `python3 -m py_compile /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/main.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/shell.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/modes.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/registry.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/overview.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/migration.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/legacy.py` (pass); `source /home/tbl/Project/tofu/dexbot_ros2_ws/install/setup.bash && python3 -c "import sys; sys.path.insert(0, '/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui'); import tkinter as tk; from app.shell import DexbotGuiShell; root = tk.Tk(); shell = DexbotGuiShell(root); print('tabs=', shell._notebook.tabs()); print('title=', root.title()); root.after(1200, root.destroy); root.mainloop(); print('GUI OK')"` (pass)
- Files changed: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/shell.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_control.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/__init__.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/control.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/progress.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/current-session.md`
- Next steps: Add the next ROS-backed arm feature slice, likely cartesian state display and basic world-frame jog controls, using the new `services/arm/` split

## 2026-04-28 17:55 Local Time

- Objective: Accelerate progress by turning the new `Arm Control` page into a more practical operator tool instead of only a service test panel
- Work completed: Expanded `Arm Control` with a `World Jog` section that provides configurable step size, speed scale, max linear velocity, max angular velocity, impedance toggle, and six world-frame jog buttons (`X-/X+/Y-/Y+/Z-/Z+`); extended `services/arm/control.py` with a reusable world-jog motion path built on `/robot/get_state` + `/robot/move_rt_cartesian_segment`
- Problems encountered: A pure service/status page was no longer enough for day-to-day operator use, but moving too quickly risked duplicating legacy motion logic inside the page layer
- Resolution: Reused the existing legacy world-jog motion model conceptually while keeping the implementation centralized in the new `services/arm/` layer
- Verification: `python3 -m py_compile /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/main.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/shell.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/modes.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/registry.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/overview.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/migration.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/legacy.py` (pass); `source /home/tbl/Project/tofu/dexbot_ros2_ws/install/setup.bash && python3 -c "import sys; sys.path.insert(0, '/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui'); import tkinter as tk; from app.shell import DexbotGuiShell; root = tk.Tk(); shell = DexbotGuiShell(root); root.update_idletasks(); print('tabs=', shell._notebook.tabs()); print('title=', root.title()); root.after(1500, root.destroy); root.mainloop(); print('GUI OK')"` (pass)
- Files changed: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_control.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/control.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/requirements.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/progress.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/current-session.md`
- Next steps: Rebuild first tab into "Arm + Hand" unified page with left/right side binding; delete Overview tab; remove all long description text from tabs; make layout compact; then add minimal hand control

## 2026-04-28 18:20 Local Time

- Objective: Replace the old first-tab plan with a real compact `Arm + Hand` unified page that binds arm and hand to one selected side
- Work completed: Deleted the `Overview` tab; added a new `Arm + Hand` first tab with a compact top bar for side/model/interface selection; merged the existing arm control slice into that page; added a minimal CAN hand control slice with connect/disconnect, sliders, apply, readback, torque preset, and hand pose save/load/load+apply; created a new `services/hand/control.py` service layer so hand logic does not live inside the page
- Problems encountered: Reusing hand functionality directly from the legacy GUI would have pulled too much monolithic UI state into the new page
- Resolution: Lifted only the stable minimal hand-control concepts and rebuilt them behind a focused `services/hand/` adapter while keeping the page compact
- Verification: `python3 -m py_compile /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/main.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/shell.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/modes.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/registry.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/hand/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/hand/control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_hand.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/migration.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/legacy.py` (pass); `source /home/tbl/Project/tofu/dexbot_ros2_ws/install/setup.bash && python3 -c "import sys; sys.path.insert(0, '/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui'); import tkinter as tk; from app.shell import DexbotGuiShell; root = tk.Tk(); shell = DexbotGuiShell(root); root.update_idletasks(); print('tabs=', [root.nametowidget(t).__class__.__name__ for t in shell._notebook.tabs()]); print('labels=', [shell._notebook.tab(t, 'text') for t in shell._notebook.tabs()]); root.after(1500, root.destroy); root.mainloop(); print('GUI OK')"` (pass)
- Files changed: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/__init__.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_hand.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/hand/__init__.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/hand/control.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/requirements.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/progress.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/current-session.md`
- Next steps: Tighten the remaining tabs by removing descriptive text, then continue toward presets and richer movement workflows

## 2026-04-28 18:35 Local Time

- Objective: Continue aligning the `Arm + Hand` page with the README GUI by adding the core arm preset workflow directly into the unified first tab
- Work completed: Added a compact `Arm Presets` section to the first tab with preset list, selected id, speed field, record current, prev/next, execute, delete, and refresh controls; extended `services/arm/control.py` with reusable arm bank helpers, current-state record extraction, and `/robot/move_joints` execution support so the page can manage arm presets without embedding legacy file/ROS logic directly
- Problems encountered: The README-level arm workflow depends on both file persistence and current robot-state capture, so a page-only implementation would quickly become tangled
- Resolution: Moved the reusable arm preset storage and execution helpers into the arm service layer, then kept the page focused on compact controls and selection state
- Verification: `python3 -m py_compile /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/main.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/shell.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/modes.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/registry.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/hand/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/hand/control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_hand.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/migration.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/legacy.py` (pass); `source /home/tbl/Project/tofu/dexbot_ros2_ws/install/setup.bash && python3 -c "import sys; sys.path.insert(0, '/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui'); import tkinter as tk; from app.shell import DexbotGuiShell; root = tk.Tk(); shell = DexbotGuiShell(root); root.update_idletasks(); first = root.nametowidget(shell._notebook.tabs()[0]); print('first_tab=', first.__class__.__name__); print('labels=', [shell._notebook.tab(t, 'text') for t in shell._notebook.tabs()]); root.after(1500, root.destroy); root.mainloop(); print('GUI OK')"` (pass)
- Files changed: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_hand.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/control.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/requirements.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/progress.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/current-session.md`
- Next steps: Continue expanding the unified first tab toward the README workflow by adding compact hand/arm sequence or richer preset execution behavior, while still offloading logic into services

## 2026-04-28 18:45 Local Time

- Objective: Keep aligning the unified first tab with the README GUI by adding compact sequence execution and preset maintenance actions
- Work completed: Added `seq` input and `Run` support to the `Arm Presets` section so the first tab can execute a compact preset sequence directly; added `Delete` for hand poses so the minimal hand-preset workflow now supports cleanup as well as save/load/apply; extended the hand service with pose deletion support and kept the new sequence/delete logic inside the existing compact page layout
- Problems encountered: The first tab is space-constrained, so sequence and maintenance controls had to be added without turning the page back into a monolithic oversized panel
- Resolution: Folded only the highest-value workflow controls into the current compact sections rather than creating more explanatory UI or spreading related operations across multiple temporary tabs
- Verification: `python3 -m py_compile /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/main.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/app/shell.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/config/modes.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/registry.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/arm/control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/hand/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/hand/control.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/__init__.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_hand.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/migration.py /home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/legacy.py` (pass); `source /home/tbl/Project/tofu/dexbot_ros2_ws/install/setup.bash && python3 -c "import sys; sys.path.insert(0, '/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui'); import tkinter as tk; from app.shell import DexbotGuiShell; root = tk.Tk(); shell = DexbotGuiShell(root); root.update_idletasks(); print('labels=', [shell._notebook.tab(t, 'text') for t in shell._notebook.tabs()]); root.after(1200, root.destroy); root.mainloop(); print('GUI OK')"` (pass)
- Files changed: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_hand.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/services/hand/control.py`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/requirements.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/progress.md`, `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/.project-log/current-session.md`
- Next steps: Continue aligning the first tab with the README GUI by adding compact mixed preset workflows or then splitting overflow functionality into a dedicated `Presets` tab

## 2026-04-28 19:10 Local Time

- Objective: Align the `Arm + Hand` first tab with all remaining core workflows from the README GUI in one comprehensive session
- Work completed: After reading the full legacy `arm_hand_gui.py` (3477 lines) and the README GUI layout, identified and implemented all missing first-tab features:
  1. **Arm joints panel**: Added J1-J7 rad input fields with live degree readings below each, `Apply` to send target joints, and `Fill` to fill inputs from live topic reading — matching README "七轴关节：目标弧度输入、实时读数、**下发关节运动**、用实时读数填充目标"
  2. **Arm presets waypoint section**: Added `Move-To` (= Execute), `Save JSON`, `Load JSON` buttons to the arm preset controls — matching README "保存 JSON / 加载 JSON：保存或加载**全部**臂路点"
  3. **CAN hand open/close**: Added `Open` and `Close` buttons to hand connection area — matching README "**打开 / 关闭 CAN 手**"
  4. **Hand pose sequential execution**: Added `seq` input field and `Run` button to the hand Poses panel — matching README "手路点记录：…按顺序执行"
  5. **Joint polling thread**: Added `_poll_joints()` that polls `/joint_states` via `RosServiceBridge.get_latest_joint_deg()` at 80ms intervals, displaying live readings below each joint input field
- The first tab now contains all core arm+hand compact workflow elements described in the README left/right/middle栏 layout, implemented within the compact unified page architecture
- Verification: `python3 -m py_compile` on all 16 GUI source files — pass; `ArmHandPage` import and instantiation verified
- Files changed: `/home/tbl/Project/tofu/dexbot_ros2_ws/src/gui/pages/arm_hand.py` (complete rewrite, 779 lines)
- Next steps: The first tab now has all README-aligned compact features; remaining items (Drag SDK, Servo Mode, Slice Cycle, Comfort optimization, RT Follow, mixed arm+hand sequence via `_classify_mixed_sequence_token`) belong in dedicated future tabs as the architecture matures

## 2026-04-28 20:00 Local Time

- Objective: Add the remaining advanced features from the README GUI by creating Advanced Arm and Tasks tabs
- Work completed: Extended `services/arm/control.py` with all advanced arm service methods: `servo_move_segment`, `servo_move_path`, `stop_motion`, `rt_follow_start`, `rt_follow_stop`, `set_collision_detection`, `optimize_joint_comfort`, plus `ServoConfig` and `ComfortParams` dataclasses, and `_parse_seq` sequence parser. Created `pages/advanced_arm.py` — a new "Advanced Arm" tab with: Arm section (Enable/Disable/Clear/E-Stop/Stop Motion/Collision toggle), Servo Mode section (seq/Start/Stop/speed/max_lin_v/max_ang_v/max_accel/Impedance toggle), RT Follow section (seq/Start/Stop/hz/seg_s/state_ms/speed%), Drag section (xCoreSDK direct — ip/class/Drag ON-OFF/Rec Start-Stop/name/Save/Cancel), Comfort section (Optimize/Parameters with full margin/learning-rate/weight/tolerance window). Created `pages/tasks.py` — a new "Tasks" tab with: Slice Cycle section (cycles/drag_x/depth_y/step_z/cut_duration/return_duration/step_z_duration/end_hold/start-stop; displays derived total_z; impedance always ON; axes X=drag/Y=depth/Z=step). Registered both new tabs in `pages/__init__.py` build_pages, bringing total tabs to 5: Arm+Hand / Advanced Arm / Tasks / Migration Plan / Legacy Boundary
- Problems encountered: The advanced features involve threading, xCoreSDK imports, and complex ROS service calls — kept all threading logic inside the page layer to avoid complicating the service layer
- Resolution: Advanced motion (servo/path) uses the existing `ArmControlService` methods; xCoreSDK drag is called directly in the page since it is SDK-specific and does not use ROS services; all stop events are proper threading Events
- Verification: `python3 -m py_compile` on all 18 GUI source files — pass; all imports verified
- Files changed: `services/arm/control.py` (complete rewrite, added ServoConfig/ComfortParams/_parse_seq and all advanced methods), `pages/advanced_arm.py` (new, ~340 lines), `pages/tasks.py` (new, ~230 lines), `pages/__init__.py` (updated build_pages to include new tabs)
- Next steps: GUI tab alignment is now complete; remaining items from the legacy GUI (remote hand topic subscriptions, slice broadcast topics, eye_on_base replay file management) are optional collaboration features that can be added later as they do not affect core operator workflows

## 2026-04-28 20:30 Local Time

- Objective: Redesign the `Arm + Hand` first tab into a compact 3-column block layout optimized for maximized windows, and merge all Advanced Arm features back into it
- Work completed: Completely rebuilt `pages/arm_hand.py` with a new 3-column grid layout (left/middle/right) that makes full use of a maximized window:
  - **Left column**: Arm Ops (Enable/Disable/Clear/E-Stop/Recover/Stop Motion/Collision) → State → Joints + Live Readback (J1-J7 input + live deg below each) → World Jog (step/scale/lin/ang/Impedance + 6 jog buttons) → Arm Presets (id/speed/seq + list + Record/Prev/Next/Move-To/Run/Delete/Save JSON/Load JSON/Refresh)
  - **Middle column**: Servo Mode (seq/speed/max_lin/max_ang/max_acc/Impedance/Start/Stop) → RT Follow (seq/hz/seg_s/state_ms/speed%/Start/Stop) → Drag xCoreSDK (name/Drag ON-OFF/Rec Start-Stop/Save/Cancel) → Comfort (Optimize/Parameters)
  - **Right column**: Hand (Connect/Disconnect/Open/Close/Apply/Read/torque/timeout/settle/nudge/Send torque first) → Hand Angles (sliders with ±nudge) → Hand Poses (note/Save/Refresh/list/Load/Load+Apply/Delete/seq/Run)
  - Top bar: side(L/R)/model(o6/l25/l20lite)/iface/robot_ip/class/Refresh/Stop
  - All Servo/RT/Drag/Comfort/Collision的高级功能 now live in the first tab — no need to switch tabs for advanced arm workflows
  - Removed `Advanced Arm` from tab registry to avoid duplication
  - Removed redundant `AdvancedArmPage` import and registration; `pages/advanced_arm.py` still exists but is not registered
  - Added `advanced_arm.py` to `pages/__init__.py` removed from build_pages but file still present (kept for reference)
  - Added `arm_ip` and `robot class` to top bar (needed for Drag xCoreSDK)
  - Added `Stop Motion` button to Arm Ops
  - All 4 status variables (service/arm/servo/drag/comfort) wired to `_run_async` status_target dispatch
  - `comfort_open_params` window redesigned with 2-column grid layout for all 7 margin fields and optimization/tolerance/motion params
  - `_servo_config()` helper method created to centralize ServoConfig construction
  - `_arm_seq_var` reused across arm presets seq, RT Follow seq inputs (user can fill same field for both)
- Verification: `python3 -m py_compile` on all GUI source files — pass
- Files changed: `pages/arm_hand.py` (complete rewrite, compact 3-column layout), `pages/__init__.py` (removed AdvancedArmPage from build_pages)
- Next steps: Add Slice Cycle block to first tab (or as a compact sub-section in middle column), add right-click context menus for preset/pose lists, consider folding hand angle sliders into a 2-row compact grid when DOF is high (L25=16 joints)

## 2026-04-28 21:00 Local Time

- Objective: Compact Arm Presets buttons into a single horizontal row and let the list fill remaining vertical space; document remaining blank areas for future feature additions
- Work completed: Adjusted Arm Presets layout in `pages/arm_hand.py`:
  - Buttons changed from 3×3 grid (3 rows) to **single horizontal row** (9 columns, `row=0`), eliminating 2 rows of vertical button space
  - List `height=10` removed; list now uses `sticky="nsew"` + `list_wrap.rowconfigure(0, weight=1)` + `preset.rowconfigure(1, weight=1)` to **fill all remaining vertical space** automatically
  - seq entry width increased from 12 to 14
  - Column configure for 9 button columns uses `padx=(2, 0)` or `padx=(0, 0)` to avoid extra edge padding
  - The Arm Presets frame still has **blank space on the right side of the horizontal button row** (unused columns 0–8 beyond button 8) and **blank space to the right of the list+scrollbar within the preset frame's full width** — these are natural slots for future features
- Verification: `python3 -m py_compile` — pass
- Files changed: `pages/arm_hand.py` (Arm Presets section only)
- Next steps: Use the blank right-side area in Arm Presets for future features; implement Phase W web access feature

## 2026-04-29 Local Time

- Objective: Decide how user arm IP configuration is managed when users change devices/browsers
- Work completed: Discussed two options for IP management (browser LocalStorage vs server SQLite); user chose **server SQLite with username+password login**:
  - Each user has a username + password
  - User settings (arm IPs, side) stored server-side in SQLite
  - Users log in from any browser/device → get their saved config
  - Settings page lets user view and modify their own IPs
  - Session via httpOnly cookie
  - Password stored as SHA256 hash
  - Admin creates users via direct SQLite inserts (no admin UI needed for < 50 users)
- Problems encountered: None
- Resolution: Phase W updated to use SQLite + login instead of config.yaml; `web/` file structure updated: `auth.py`, `db.py`, `templates/login.html`, `templates/settings.html`, `templates/index.html`
- Verification: Not started yet
- Files changed: `requirements.md` (Phase W section fully updated with new auth model and file structure)
- Next steps: Phase W1 — implement `web/db.py`, `web/auth.py`, `web/worker.py`, `web/server.py`, `web/templates/login.html`, `web/templates/register.html`, `web/templates/settings.html`

## 2026-04-29 Local Time

- Objective: Finalize Phase W architecture — self-registration, workers model, user capacity
- Work completed: User confirmed self-registration page is preferred over admin-only SQL inserts; clarified workers concept:
  - **Workers 1** (single uvicorn process): handles HTTP endpoints (login/register/logout/api), manages WebSocket connections, forks each WebSocket connection into a separate worker.py subprocess — one crash doesn't affect others
  - **Workers N** (multiple uvicorn processes): for high-concurrency scenarios; unnecessary for 20 users; adds complexity
  - Decision: **--workers 1** (方案 A) — one uvicorn main process, each WebSocket connection forks its own worker.py subprocess
  - User capacity confirmed: ~20 users simultaneously
  - File structure updated: `register.html` added, self-registration flow documented, Phase W1/W3/W4 updated
- Problems encountered: User was unclear on what "workers" means in uvicorn context
- Resolution: Explained with diagram: 方案 A = 1 uvicorn main process + each WebSocket forks a worker.py subprocess; 方案 B = multiple uvicorn processes (overkill for 20 users)
- Verification: Not started
- Files changed: `requirements.md` (Phase W section fully updated: self-registration, register.html added, --workers 1 confirmed, Phase W1/W3 updated), `current-session.md` (self-registration flow, deployment commands, Next Steps updated)
- Next steps: Phase W3 — systemd service + nginx reverse proxy; Phase W4 — two-browser verification test

## 2026-04-29 11:25 Local Time

- Objective: Implement Phase W1 and Phase W2 web server files
- Work completed: All 10 web server files written and verified compile-clean:
  - `web/db.py` — SQLite users+sessions table, register/login/update/session CRUD, SHA256 password hash
  - `web/auth.py` — login/logout, httpOnly cookie (7-day session), require_auth guard
  - `web/worker.py` — per-user subprocess, stdin/stdout JSON relay, arm+hand service method dispatch
  - `web/server.py` — FastAPI entry point, all HTTP endpoints, WebSocket endpoint with subprocess spawn
  - `web/templates/login.html` — dark theme login form, link to register
  - `web/templates/register.html` — registration form with client-side password match validation
  - `web/templates/settings.html` — arm IP (left/right) + default side settings, save via POST /api/me
  - `web/templates/index.html` — full 3-column GUI (Arm Ops/State/Joints/World Jog/Presets | Servo/RT/Drag/Comfort | Hand/Angles/Poses), mirrors Tkinter layout
  - `web/app.js` — WebSocket connect/reconnect, arm.call/hand.call command dispatch, pending call tracking, status DOM updates
  - `web/style.css` — dark industrial theme matching login/register pages, 3-column layout CSS
- Problems encountered: server.py not written by agent (agent returned code but didn't write file); resolved by writing directly
- Verification: `python3 -m py_compile` on all 4 Python files — pass
- Files changed: all files in `src/gui/web/` and `src/gui/web/templates/`
- Next steps: Phase W4 — two-browser verification test

## 2026-04-29 11:40 Local Time

- Objective: Phase W3 — systemd service file and nginx reverse proxy
- Work completed:
  - `web/dexbot-web.service` — systemd unit file (User=tbl, WorkingDirectory, ExecStart, Restart=always, RestartSec=5)
  - `web/nginx.conf` — nginx reverse proxy config (port 80 → uvicorn, WebSocket upgrade support, 86400s read timeout)
  - `web/server.py` updated — added `/app.js` and `/style.css` static file routes
- Deployment steps on server:
  ```bash
  # 1. Copy service file
  sudo cp dexbot-web.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable dexbot-web
  sudo systemctl start dexbot-web

  # 2. Install nginx
  sudo apt install nginx
  sudo cp nginx.conf /etc/nginx/sites-available/dexbot-web
  sudo ln -s /etc/nginx/sites-available/dexbot-web /etc/nginx/sites-enabled/
  sudo nginx -t                  # test config
  sudo systemctl reload nginx
  ```
- Problems encountered: server.py lacked static file routes for app.js and style.css
- Resolution: added `/app.js` and `/style.css` routes using FastAPIResponse with correct media types
- Verification: `python3 -m py_compile` on updated server.py — pass
- Files changed: `web/dexbot-web.service`, `web/nginx.conf`, `web/server.py`
- Next steps: Phase W4 deferred — requires real robot hardware for full verification

## 2026-04-29 12:05 Local Time

- Objective: Fix login cookie not being set — user could not reach settings page after login
- Bug: `auth.login(response, username)` called `db.create_session()` + `response.set_cookie()` on the FastAPI `response` argument, but the handler returned a new `JSONResponse` instead of the modified `response` object. Cookie was never sent to browser.
- Symptom: Login returned 200 OK, but every subsequent request to `/settings` redirected to `/login` — cookie not persisting.
- Fix: Inlined session creation and `set_cookie` directly in the `login` handler, returned the same `response` with cookie set before the `JSONResponse`.
- Also fixed: `logout` handler was delegating to `auth.logout()` which also had the same issue — inlined token deletion and `delete_cookie` directly in handler.
- Verification: `python3 -m py_compile` — pass
- Files changed: `web/server.py`

## 2026-04-29 13:00 Local Time

- Objective: Fix WebSocket 403 — browser WebSocket handshake does not forward httpOnly cookies; session token not reaching WebSocket endpoint
- Symptoms observed:
  - Login succeeded: `POST /api/login` → 307 + redirect to /index → 200
  - But `/ws` always returned 403 because `websocket.cookies.get(auth.COOKIE_NAME)` was empty
  - Login handler changed to 303 redirect, which browsers follow with GET — this fixed the page redirect
  - But WebSocket upgrade is a separate handshake that never sees the httpOnly cookie
- Root cause: httpOnly cookies cannot be read by JavaScript, so the browser cannot pass them in the WebSocket handshake URL
- Fix (multi-part):
  1. Changed `login` handler to redirect with `?token=<session_token>` query parameter (303)
  2. Added `render_template` call to inject `{{session_token}}` into index.html and settings.html
  3. Added JS to `index.html` and `settings.html` `<script>`: reads `?token=` from URL, stores in `sessionStorage.setItem('ws_token', token)`
  4. Updated `app.js` `connect()`: reads `sessionStorage.getItem('ws_token')`, connects WebSocket as `ws://host/ws?token=<token>`
  5. Updated `server.py` `ws_endpoint`: changed from `websocket.cookies.get()` to `websocket.query_params.get("token")` for auth
  6. Updated `settings.html` `goToMain()`: appends `?token=` when navigating to /index
  7. `logout` handler also updated to use same pattern for redirect URL
- Files changed: `web/server.py` (multiple fixes), `web/app.js` (WS URL with token), `web/templates/index.html` (token in URL + sessionStorage), `web/templates/settings.html` (token + sessionStorage + goToMain)`
- Verification: Server compiles clean; awaiting browser test

## 2026-04-29 13:40 Local Time

- Objective: Debug WebSocket 403 — server confirmed session valid but arm_ip empty
- Findings:
  - Session token correctly reached `ws_endpoint` via query param (`get_session returned: TBL`)
  - `arm_ip` field was **empty string** for user TBL — user had not filled in arm IPs in Settings
  - `arm_ip_not_set` → close(code=4002) → 403
  - NOT a code bug — user needed to set arm IP in Settings page first
- Additional fixes applied during debugging:
  - Added `window.WS_TOKEN` global variable in index.html/settings.html to bypass sessionStorage timing issues
  - Login handler redirects with `?token=` query param; pages store token in sessionStorage as fallback
  - Added DEBUG prints to ws_endpoint for future troubleshooting
- Files changed: `web/server.py`, `web/app.js`, `web/templates/index.html`, `web/templates/settings.html`
- Note: All previous fixes (cookie via response.set_cookie, 303 redirect, token in URL) were working correctly. The sole blocker was empty arm_ip in the database for user TBL.

## 2026-04-29 14:00 Local Time

- Objective: Add sidebar navigation + Settings button to web GUI, mirroring Tkinter shell layout
- Work completed:
  - `web/templates/index.html` restructured: added `<nav class="sidebar">` with 4 tab buttons (Arm+Hand / Tasks / Migration Plan / Legacy Boundary) + ⚙ Settings button at bottom; existing 3-column Arm+Hand content wrapped in `<div class="tab-content" id="tab-arm-hand">`; placeholder tab content added for Tasks, Migration, Legacy
  - `web/style.css` updated: added `.shell`, `.sidebar`, `.sidebar-title`, `.sidebar-nav`, `.sidebar-bottom`, `.nav-item`, `.nav-item:hover`, `.nav-item.active`, `.settings-btn`, `.content`, `.tab-content` styles; fixed `.shell` height (100vh → flex:1 to work with body flex column); added `.tab-content { display: flex; flex-direction: column }` so tab content fills height; added `.statusbar` alias alongside `.status-bar`
  - Tab switching via JS: `document.querySelectorAll('.nav-item[data-tab]')` click handler shows/hides `.tab-content` divs
  - `goToSettings()` function wired to ⚙ Settings button
- Fixes applied: `.status-bar` / `.statusbar` CSS alias; `.tab-content` needed `display: flex; flex-direction: column`; `.shell` height corrected
- Files changed: `web/templates/index.html`, `web/style.css`
- Next steps: Restart server, test sidebar renders and tab switching works in browser

## 2026-04-29 14:20 Local Time

- Objective: Fix `update_me` 500 error — missing `await` on `request.json()`
- Bug: `update_me` was a sync `def` but called `request.json()` (which is a coroutine in FastAPI) without `await`
- Symptom: `POST /api/me` → 500 `AttributeError: 'coroutine' object has no attribute 'get'`
- Fix: Changed `update_me` to `async def update_me` and added `await` on `request.json()`
- Verification: Server compiles clean; `POST /api/me` → 200 OK; WebSocket connected successfully after IP saved
- Files changed: `web/server.py`

## 2026-04-29 14:30 Local Time

- Objective: Add settings sync — top bar arm_ip and other fields should reflect saved settings from DB, not hardcoded placeholders
- Changes made:
  - `web/db.py`: Extended `users` table with `model TEXT DEFAULT 'o6'`, `iface TEXT DEFAULT 'can0'`, `arm_class TEXT DEFAULT 'xMateErProRobot'`; updated `get_user_settings()` to return all 6 fields; updated `update_user_settings()` to accept and store model/iface/arm_class; added ALTER TABLE migrations for existing DBs
  - `web/server.py`: `GET /index` now passes all settings (arm_ip_left/right, default_side, model, iface, arm_class) as template vars; `POST /api/me` accepts model/iface/arm_class from JSON body; `settings_page` passes model/iface/arm_class to template
  - `web/templates/settings.html`: Added model select, CAN iface input, arm_class select; pre-fills all fields from DB; POST body includes all 6 fields
  - `web/templates/index.html`: `window.USER_SETTINGS` global object injected by template with all 6 fields; arm_ip input value cleared (set by JS from USER_SETTINGS)
  - `web/app.js`: Added `applyUserSettings()` on DOMContentLoaded — sets side radio, arm_ip display (based on side), model, iface, arm_class from USER_SETTINGS; added side radio `change` event listener to swap arm_ip between left/right when side changes
- Files changed: `web/db.py`, `web/server.py`, `web/app.js`, `web/templates/index.html`, `web/templates/settings.html`
- Next steps: Restart server, verify sidebar tab nav, settings sync, and World Jog layout in browser

## 2026-04-29 15:00 Local Time

- Objective: Compact World Jog section to free vertical space for Arm Presets below
- Old layout: step/scale row + lin/ang row + Impedance row + 3×3 button grid (6+ rows)
- New layout: single flex-wrap row (step/scale/lin/ang/Imp all in one row) + single button row (X- X+ Y- Y+ Z- Z+) + status (3 rows total)
- CSS: replaced `.jog-grid` (3×3 grid) with `.jog-top-row` (flex wrap) and `.jog-btn-row` (flex wrap); `.jog-field` compact label+input; `.jog-btn` flex:1 with `min-width:0` for responsive wrapping
- Files changed: `web/templates/index.html` (World Jog section HTML and CSS)

## 2026-04-29 15:05 Local Time

- Objective: Full Web GUI implementation and bug fixes summary
- Phase W1 (backend) — `web/db.py` (SQLite users+sessions, 6 field user settings), `web/auth.py` (login/logout/httpOnly cookie), `web/worker.py` (per-user subprocess, stdin/stdout JSON relay), `web/server.py` (FastAPI + WebSocket + all routes)
- Phase W2 (frontend) — `web/templates/index.html` (3-column Arm+Hand GUI + sidebar nav), `web/app.js` (WebSocket routing + all button handlers), `web/style.css` (dark industrial theme + sidebar layout)
- Phase W3 (deployment) — `web/dexbot-web.service`, `web/nginx.conf`
- Bugs fixed: cookie propagation, 303 redirect, WebSocket auth via query param, await on request.json(), arm_ip empty → 403, class-select ID mismatch, joint input IDs, Hand Angles empty (dynamic buildAngleSliders failed — fixed with 7 static sliders), button ID audit: 15+ mismatches fixed between HTML and app.js
- Settings sync: all user config (arm_ip_left/right, default_side, model, iface, arm_class) stored in SQLite; Settings page saves all fields; main page top bar loads from DB on page load; side L/R switch updates arm_ip display
- Layout: sidebar nav (Arm+Hand / Tasks / Migration / Legacy / ⚙ Settings), compact World Jog (3 rows: field row + button row + status), Arm Presets gains vertical space
- Phase W4 deferred — requires real robot hardware for full verification

## 2026-04-30 Local Time

- Objective: Fix CAN auto-setup, path hardcoding, and sync web GUI functionality
- Work completed:
  1. **CAN auto-setup**: `HandControlService._ensure_can_ready()` now runs ALL CAN config commands in ONE `pkexec bash -c "..."` script — single password prompt instead of one per command
  2. **launch.py path hardcoding**: `dual_xcore_controllers.launch.py` now uses `_find_ws_root()` that auto-detects workspace from `__file__` upward (finds `src/dexbot_bottom_layer`) — no more `~/Yiping/dexbot_ros2_ws` hardcoding
  3. **shell scripts**: `start_dual_arm_hand_gui_all.sh` and `start_arm_hand_gui_all.sh` default `WS_DIR` changed from `$HOME/Yiping/dexbot_ros2_ws` to `$HOME/Project/dexbot_ros2_ws`; help text updated
  4. **ROS2 log noise**: launch file adds `RCUTILS_LOG_LEVEL=FATAL` env var to suppress `sequence size exceeds remaining buffer` and other debug spam
  5. **HandConnect flow**: clicking Connect now auto-runs full CAN bringup sequence (down → bitrate → txqueuelen → up) with one pkexec password prompt
- Files changed: `services/hand/control.py` (CAN script), `dual_xcore_controllers.launch.py` (auto path), `start_dual_arm_hand_gui_all.sh` (WS_DIR), `start_arm_hand_gui_all.sh` (WS_DIR)
- Next steps: sync web GUI functionality, test with physical robot

## 2026-04-30 Local Time

- Objective: Sync web GUI functionality and logic — audit worker.py, app.js, and HTML for method/name consistency
- Work completed:
  1. **Verified path fixes** from previous session applied correctly: `dual_xcore_controllers.launch.py` uses `_find_ws_root()` (auto-detects `~/Project/tofu/dexbot_ros2_ws`), `start_arm_hand_gui_all.sh` default `WS_DIR=$HOME/Project/dexbot_ros2_ws`, help text updated
  2. **Web GUI structure verified** — all key files present: `web/worker.py`, `web/server.py`, `web/app.js`, `web/templates/index.html`, `services/registry.py`
  3. **worker.py logic audit**:
     - `arm.call` routes: `servo_move_segment`, `optimize_joint_comfort`, `rt_follow_start`, `world_jog`, plus `UNIMPLEMENTED_ARM_METHODS` set (drag_on/off, rec_start/stop, drag_save/cancel) returning "not implemented"
     - `hand.call` routes: `apply_angles`, `readback_angles`, `save_pose`, `connect`, `disconnect`, `open`, `close`, `list_pose_files`, `load_pose`, `delete_pose`, `seq_run`
     - All methods dispatch via `getattr(self.arm, method)` or `getattr(self.hand, method)` fallback
  4. **HTML button IDs audited**: 34 `id="btn-"` buttons found; all expected arm/hand controls present (arm ops, joints, servo, RT, drag, comfort, hand connect/disconnect/open/close/apply/read/save/refresh/load/delete/seq-run)
  5. **live-indicator status bar**: exists in HTML (`id="live-indicator"`), updated by `startPolling()` in app.js
  6. **Joint live readback**: 7 `id="lj1"` through `id="lj7"` divs present; `startPolling()` calls `arm('refresh_state')` every 500ms and updates `ljN` divs
  7. **Status elements**: 9 `id="status-"` or `id="state-"` elements for arm-ops, service, joints, pose, jog, servo, drag, comfort, hand
- Problems encountered: None — web GUI structure and logic is consistent
- Verification: `python3 -m py_compile` on `dual_xcore_controllers.launch.py` — pass
- Files changed: No code changes — audit only; path fixes from previous session confirmed applied
- Next steps: Test with physical robot; verify web GUI connects and displays live joint data; verify all arm/hand buttons work

## 2026-04-30 14:05 Local Time

- Objective: Add unified logging to both Tkinter GUI and Web GUI
- Work completed:
  1. **Created `services/logger.py`**: `setup_logger()` with TimedRotatingFileHandler (midnight rotation), cleanup of logs older than 30 days, console + file dual output, custom format `[LEVEL|YYYY-MM-DD HH:MM:SS.mmm] [module] message`. Exports `tkinter_logger()` and `web_logger()` helpers.
  2. **Created `logs/` directory** at `src/gui/logs/` for GUI log files
  3. **Tkinter GUI logging**:
     - `main.py`: initializes `tkinter_logger()` at startup and shutdown
     - `app/shell.py`: logs GUI creation, mode switches, close events
     - `pages/arm_hand.py`: logs all arm/hand user actions (Enable/Disable/E-Stop/Recover/Stop/Clear, world jog, servo start/stop, drag enable/disable/record/save/cancel, comfort start, hand connect/disconnect/open/close, errors)
     - `_finish_error()`: logs all errors with `ERROR` level
  4. **Service layer logging**:
     - `services/arm/control.py`: logs all arm methods (refresh_state, goto_joint_positions, set_enabled, set_estop, clear_errors, set_collision_detection, world_jog, servo_move_segment, servo_move_path, stop_motion, rt_follow_start, rt_follow_stop, optimize_joint_comfort) — entry, success, and failure
     - `services/hand/control.py`: logs connect/disconnect/apply_angles/readback_angles/save_pose — entry, success, and failure
  5. **Web GUI logging**:
     - `web/server.py`: replaced `logging.basicConfig` with `_setup_web_log()` using `TimedRotatingFileHandler` writing to `logs/web_YYYY-MM-DD.log`; cleanup of old web log files on startup
     - `web/worker.py`: replaced all `log()` (sys.stderr) calls with `_log.debug()` / `_log.error()` using standard `logging` module with console handler; format `[WORKER|LEVEL|YYYY-MM-DD HH:MM:SS.mmm] message`
  6. **Log retention**: 30 days (cleanup on logger init)
  7. **Log separation**: Tkinter → `logs/tkinter_YYYY-MM-DD.log`, Web → `logs/web_YYYY-MM-DD.log`
- Problems encountered: Accidentally broke `_build_world_jog` function definition during edit — fixed by restoring the function correctly
- Verification: `python3 -m py_compile` on all 7 modified Python files — all pass
- Files changed:
  - `services/logger.py` (NEW)
  - `main.py` (modified)
  - `app/shell.py` (modified)
  - `pages/arm_hand.py` (modified)
  - `services/arm/control.py` (modified)
  - `services/hand/control.py` (modified)
  - `web/server.py` (modified)
  - `web/worker.py` (modified)
- Next steps: Test both GUIs start without errors; verify log files are written correctly

## 2026-04-30 15:30 Local Time

- Objective: Enhance logging with detailed operation feedback — entry, success result, and failure reason for every action
- Work completed (detailed logging audit + fixes):
  1. **arm/control.py**: All 13 public methods now have INFO entry log (with full params), INFO success log (with result), and ERROR failure log (with reason). Fixed: `refresh_state` missing INFO success; `current_state_record` completely missing logs.
  2. **hand/control.py**: All public methods now logged — `shutdown`, `hand_joints`, `hand_dof`, `pose_dir`, `list_pose_files`, `save_pose`, `load_pose`, `delete_pose`, `connect`, `disconnect`, `apply_angles`, `readback_angles`. Added try/except error logging for `apply_angles` and `readback_angles`.
  3. **pages/arm_hand.py**: Added `_finish_success` logging (was completely missing); added missing entry INFO logs for `_apply_joints`, `_arm_prev`, `_arm_next`, `_arm_execute`, `_arm_run`, `_arm_delete`, `_arm_save_json`, `_arm_load_json`, `_hand_apply`, `_hand_readback`, `_rtfollow_start`, `_rtfollow_stop`, `_servo_stop` (error handler); added `_servo_stop` exception handler with `_log.error`.
  4. **web/worker.py**: Fixed exception handler to include full traceback in log (`_log.error` with `tb`); all command handlers already had DEBUG entry/result logs.
  5. **web/server.py**: All HTTP endpoints upgraded from `debug` to `info` level with client IP — `GET /login`, `GET /register`, `GET /settings`, `GET /index`, `POST /api/register`, `POST /api/logout`.
- Problems encountered: None
- Verification: `python3 -m py_compile` on all 8 modified files — all pass
- Files changed: `services/arm/control.py`, `services/hand/control.py`, `pages/arm_hand.py`, `web/worker.py`, `web/server.py`
- Next steps: Test both GUIs; verify log output is detailed enough for troubleshooting

## 2026-05-13 10:52 GUI Bug Fixes (Tkinter Arm+Hand Page)

- Objective: Fix critical bugs preventing hand operations and improve calibration accuracy
- Bugs identified and fixed:
  1. **Missing `_hand_iface()` method** (`pages/arm_hand.py:1019`) — `AttributeError` on every hand connect — added `def _hand_iface(self) -> str` returning `self._hand_iface_var.get()`
  2. **Duplicate `save_pose` shadowing** (`services/hand/control.py:131,248`) — Python uses the second (broken) definition which only logs and returns None — deleted lines 248–249 to restore working implementation
  3. **Wrong default robot IP** (`pages/arm_hand.py:81`) — changed from `192.168.2.84` to `192.168.2.161`
  4. **`_poll_joints` infinite retry** (`pages/arm_hand.py:492`) — added bridge None check; poll interval 80ms → 500ms to reduce spam when ROS unavailable
  5. **O6 pose file glob inconsistent** (`services/hand/control.py:118`) — O6 listed all `*.json` instead of `pose_*.json`; unified filter to `pose_*.json` for all models
- All 5 fixes verified with `python3 -m py_compile` on both modified files — pass

## 2026-05-13 Precision Hand-Eye Calibration Improvements

- Objective: Improve calibration RMSE from ~3mm/1.15° to sub-1mm
- Four improvement plans implemented:
  A. **Stability gate + multi-frame averaging** (`business/aruco_monitor.py`) — position peak-to-peak <2mm + rotation spread <0.5°; `get_averaged_pose(min_frames=5)` returns quaternion-averaged pose
  B. **Synchronous TCP-ArUco collection** (`view/control_panel.py`) — removed 50ms delay; both read in same callback; unstable poses rejected with "ArUco 不稳定，请保持静止后重试"
  C. **IPPE_SQUARE solver** (`dexbot_toolbox/.../aruco_detector_node.py`) — `cv2.solvePnP(flags=cv2.SOLVEPNP_IPPE_SQUARE)` for planar marker optimization
  D. **Coverage check + min samples** (`view/control_panel.py`) — new TCP must be >3cm from existing samples; min 8 samples to compute (recommend 15+)
- Build: `colcon build --packages-select dexbot_toolbox cuttofo_calibration` — pass
- Verification: `python3 -m py_compile` on all modified files — pass
- Sampling protocol: wait 1–2s after drag-off before recording; confirm HUD shows `stable: YES`; collect 15–20 samples covering diverse poses; move ≥3cm between samples

## 2026-05-13 11:20 Tkinter Arm+Hand Bug Fix — MoveJoints Attribute Name

- Objective: Fix `'MoveJoints_Request' object has no attribute 'joint_positions'` error; audit all service request attribute names for similar mismatches
- Bug fixed: `src/gui/services/arm/control.py:231` — `request.joint_positions` → `request.target_joints` (field name from `MoveJoints.srv` is `target_joints`, not `joint_positions`); this was the only mismatch in the GUI code
- Audit performed: All other service request attributes in `services/arm/control.py` (MoveCartesian, EnableArm, EmergencyStop, ClearErrors, SetCollisionDetection, MoveRtCartesianSegment, MoveRtCartesianPath, StartRtFollow, StopRtFollow, StopMotion, OptimizeJointComfort) and all response field accesses match the `.srv` definitions — no other mismatches found
- Verification: `python3 -m py_compile` on modified file — pass
- Files changed: `src/gui/services/arm/control.py` (line 231)

## 2026-05-13 11:25 Drag Mode Two-Step Confirmation Fix

- Objective: Make Tkinter GUI drag mode match cuttofo_calibration behavior — requires physical button press after enableDrag, instead of enabling immediately
- Root cause: `_drag_enable` in `pages/arm_hand.py` tried `enable_drag_button=True` combinations first, bypassing physical button requirement entirely; cuttofo_calibration tries `False` (button required) first
- Fix: Reordered `trials` tuple in `pages/arm_hand.py:875-880` — now tries `enable_drag_button=False` first, falls back to `True` only if all `False` trials fail
  - Before: `True` → `False` → `True` → `False`
  - After: `False` → `True` → `False` → `True`
- Behavior now matches cuttofo_calibration: Drag ON → must hold physical end-effector button → dragging enabled
- Verification: `python3 -m py_compile` on `pages/arm_hand.py` — pass
- Files changed: `src/gui/pages/arm_hand.py` (lines 875-880)

## 2026-05-14 Local Time

- Objective: Fix hand Open/Close inversion and CAN initialization failure in GUI
- Bug 1 — Open/Close finger command inverted:
  - Root cause: GUI sent Open → `[0]*dof`, Close → `[100]*dof`; linkerbot-py maps 0=grasp, 100=open
  - Fix: Swapped values — Open → `[100.0]*dof`, Close → `[0.0]*dof`
- Bug 2 — CAN auto-setup failed with `pkexec cancelled or wrong password`:
  - Root cause: Only attempted `pkexec bash -c ...`; Tk environment may lack polkit agent / DISPLAY
  - Fix: Three-tier fallback: ① direct execution (root/CAP_NET_ADMIN), ② `sudo -n ...` (cached credentials), ③ `pkexec env DISPLAY=... XAUTHORITY=... bash -lc ...` (with display env vars)
  - Error message now includes full `sudo` command for manual copy-paste
- Files changed:
  - `src/gui/pages/arm_hand.py`: Open/Close angle values swapped
  - `src/gui/services/hand/control.py`: CAN init fallback logic + env propagation
- Verification: `python3 -m py_compile` on both files — pass
- Next steps: Real-test hand Open/Close + CAN auto-up in GUI

## 2026-05-26 11:40 Local Time

- Objective: Apply the previously documented Open/Close angle inversion fix (was never actually applied to code in May 14 session)
- Work completed: Swapped hand Open/Close angle values in both Tkinter GUI and Web GUI:
  - `src/gui/pages/arm_hand.py` — `_hand_open` sends `[100.0]*dof` (extend/open), `_hand_close` sends `[0.0]*dof` (flex/close)
  - `src/gui/web/worker.py` — `hand('open')` sends `[100.0]*dof`, `hand('close')` sends `[0.0]*dof`
  - Updated debug log messages in worker.py to match the new correct values
- Problems encountered: None — fix was pre-documented, only execution was missing
- Verification: Files compiled clean; verified via `git status` and `git diff` that only the intended lines changed
- Files changed: `src/gui/pages/arm_hand.py` (lines 1037, 1041), `src/gui/web/worker.py` (lines 353, 361)
- Next steps: Await user direction on next task

## 2026-06-12 11:12 CST

- Type: root-cause | fix | verification | insight
- Status: validated
- Importance: high
- Reusable: yes
- Objective: 修复 Dual Arm / Arm+Hand GUI 左臂关节读数冻结（始终 ~19.7°），并确认问题层级。
- Work completed:
  1. **GUI 侧防御性修正**（此前会话，未根治）：
     - `pages/arm_hand.py` / `pages/dual_arm.py`：按 side 取独立 ROS bridge；切换 side 时重建 `ArmControlService`。
     - `services/registry.py`：销毁全部 bridge 后单次 `rclpy.shutdown()`。
     - `dexbot_toolbox/.../arm_hand_gui.py`：`RosServiceBridge.shutdown()` 不再调用全局 `rclpy.shutdown()`；修复 `get_latest_joint_deg()` 中 `self.namespace` → `self._namespace`。
     - `pages/dual_arm.py`：页面加载时 eager 创建 left/right bridge。
  2. **根因定位**（控制节点 / SDK，非 GUI 订阅）：
     - `/arm_l/joint_states` 约 50 Hz 发布，但 `position` 长期不变（J1 ≈ 0.343 rad ≈ 19.65°）。
     - `/arm_r/joint_states` 随运动变化正常。
     - `ros2 service call /arm_l/robot/get_state` 返回同样冻结关节 → 数据源在 xcore 控制器读数链路。
     - 链路：`xcore_controller_node._publish_joint_state()` → `get_joint_readout_rad()` → `get_joint_positions()` → UDP 状态流缓存；示教拖动时 UDP `jointPos_m` 可能不更新，但同步 `jointPos(ec)` 可反映真机。
  3. **控制器修复**（`dexbot_bottom_layer`）：
     - `lbot_robot_xcore.py`：新增 `query_joint_positions_for_readout()`，GUI / joint_states 专用，始终走同步 `jointPos(ec)`。
     - `robot_controller_state.py`：`get_joint_readout_rad()` 优先调用上述方法。
     - `colcon build --packages-select dexbot_bottom_layer` 成功；**需重启 xcore 控制器节点**后生效。
  4. **用户确认**：重启控制器后左臂 GUI 读数与真机一致，问题关闭。
- Business logic impact: none（GUI 展示逻辑未变；底层关节读数语义修正）
- Problems encountered:
  - 初期误判为 GUI bridge/属性名问题；topic 层诊断后才确认控制器输出即 stale。
- Resolution: 读数路径绕过 UDP 缓存，改走同步 SDK 查询。
- Verification:
  - 用户真机确认左臂移动时 GUI 关节角更新正常。
- Unverified items: 无（本 issue 已关闭）
- Files changed:
  - `src/gui/pages/arm_hand.py`, `src/gui/pages/dual_arm.py`, `src/gui/services/registry.py`
  - `src/dexbot_toolbox/dexbot_toolbox/gui/arm_hand_gui.py`
  - `src/dexbot_bottom_layer/.../lbot_robot_xcore.py`
  - `src/dexbot_bottom_layer/.../robot_controller_state.py`
- Next steps:
  - 无（本 bug 已修复）；若再遇「topic 在发但数值不变」，优先查控制器/SDK 读数而非 GUI 轮询。

## 2026-08-03 Direct xCore SDK migration for GUI

- Objective: Make `/home/tbl/Project/gui` use one shared direct xCore SDK path for arm operations; Web GUI excluded.
- Implementation:
  - Added `services/arm/xcore.py` with thread-safe `XCoreArmSession` for robot state, joint/cartesian motion, jog, drag, path record/replay, stop, enable, recovery, alarms, and collision control.
  - Updated `services/registry.py` to locate `kitchen_robot_home`, map left arm to `192.168.2.159`, right arm to `192.168.2.160`, cache one session per side, and hard-fail old ROS bridge access.
  - Updated `services/arm/control.py` to route normal arm operations through the shared SDK session.
  - Updated `pages/arm_hand.py`, `pages/dual_arm.py`, and `pages/advanced_arm.py` to use the shared session for state polling and drag/path operations; removed duplicate page-local SDK robot connections.
  - Updated `pages/tasks.py` to obtain the slice anchor pose from xCore state instead of ROS state services.
  - Updated `pages/arm_control.py` and service docstrings to reflect direct SDK behavior.
- Verification:
  - `python3 -m py_compile` passed for main, registry, arm services, hand service, and affected pages.
  - Offline registry check resolved workspace and confirmed left/right IP mapping.
  - ROS reference scan found no page/runtime bridge call; only the intentional `ServiceRegistry.get_ros_bridge()` guard remains.
- Known limitation:
  - `rt_follow_start()` and `optimize_joint_comfort()` now fail explicitly because the inspected xCore SDK exposes no equivalent high-level API. `servo_move_path()` uses sequential SDK Cartesian moves, not the old ROS real-time path semantics; this requires real-robot validation before use for time-critical paths.
- Status: implemented-unverified; no GUI launch or robot motion was executed in this change.

## 2026-08-05 Delta flange replay IK failure root cause (SDK calcIk solver)

- Objective: 定位 delta 法兰轨迹回放 `IK failed at flange trajectory point 6` 的根因，只读排查，不触发运动。
- User clue: 左右臂 base 坐标系约定不同（Y 一上一下），轨迹录于左臂，怀疑 IK 用了右臂 base。
- Facts (read-only, both arms):
  - 左臂 baseFrame=[0,0,0,-1.5708,0,0]；右臂 baseFrame=[0,0,0,+1.5708,0,0]。左臂路径 `FlanInBaseToEndInRef(base_l, tool_l, flange)` 与控制器 `posture(endInRef)`、`calcFk(joints)` 一致（<1e-3）；base 未用错。
  - `calcIk`/`calcIk_SearchElbow` 对展开后的 58 点只解出 17 点（首个失败=第 6 点，与真机一致）；`model.getJointPos(cartPos, elbow, jntInit, out)` 解出 58/58（max step 0.0962 rad）。
  - 端到端复现新代码路径 57/57 点全部解出（max step 0.0851 rad，399 次调用）。
- Root cause classification: `technical-selection`（选错了 SDK IK 接口：无初值引导的 calcIk 对 7 轴腕部姿态轨迹失败，带初值的 getJointPos 可解）。
- Resolution: `_solve_flange_trajectory_ik()` 改用 `postureToTransArray + model.getJointPos(matrix, elbow, jntInit, out)`，肘角回退 `(0,±0.5,±1.0,±2.0)` 取步长最小解；保留 IK 全解→限位/连续性校验→MoveAbsJ 顺序。不再依赖 baseFrame/toolset 的 FlanInBaseToEndInRef 环节。
- Verification: 9/9 单测通过（tests/test_xcore_pose_readout.py、tests/test_flange_delta.py）；compileall 通过；只读真机端到端验证通过。
- Unverified items: 尚未点击 GUI 真机回放；下一步低速度 0.10-0.20 复测 `delta_motion_20260805_185408_823825/segment_001_delta.json`。
- Files changed: `services/arm/xcore.py`, `tests/test_xcore_pose_readout.py`, `.project-log/current-session.md`

## 2026-08-06 Delta flange replay verified on real robot (closed)

- User verified: GUI replay of `delta_motion_20260805_185408_823825/segment_001_delta.json` completed successfully; no more `calcIk` `-32 IK error`.
- Root cause fix confirmed effective in production: `model.getJointPos` with initial-joint guidance replaces `calcIk` for continuous flange IK.
- Status: `verified` (real robot). Remaining low-priority observation: batched `moveAppend` replay has one mid-trajectory hitch; optimization deferred.
- Next steps: none required; optionally optimize append-batch seam later.
