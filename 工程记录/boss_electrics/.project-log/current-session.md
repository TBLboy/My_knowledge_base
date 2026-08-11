## 当前会话（2026-08-11 PanPour 私有 wait 占位实现）

- 问题：`PanPourPolicy` 在等待参数/锅把/底盘/餐盘时返回 `None`，现有 Planner 把 `None` 视为任务完成并清空 active task，造成误判完成。
- 方案：按方向 2 在任务私有范围内修复，不改 `TaskPlannerNode` / `BasePolicy` 公共调度。
- 改动：
  - `PanPourPolicy` 等待阶段返回 `plan_type=pan_pour`、`action_name=wait`、`step_index=-1` 的占位步骤；wait 结果成功不会推进阶段。
  - `PanPourSkill` 将 `phase=wait` 解析为空 `MotionPrimitive` 列表；执行器现有 `total=0` 成功语义直接完成，不移动机械臂/灵巧手。
- 验证：主线定向 21 passed；执行器定向 42 passed；两仓库 `compileall` 与 `colcon build` 通过；执行仓库 `git diff --check` 通过；主仓库原第 119 行尾空格已顺手清理。
- 当前状态：两仓库本轮改动均未提交、未 push；真机闭环未做。

## 当前会话（2026-08-11 执行仓库待 push 提交复核）

- 用户要求：由主代理完成 `robot_motion_executor` 本地待推送提交的审查和验证，停止在用户手动 push 前；个人 SDK 修改不得进入公共提交。
- 执行仓库状态：分支 `robam_kitchen`，本地 `HEAD=efa6b24`，远端 `origin/robam_kitchen=4635b3e`，差异为远端独有 0、本地独有 1；远端 `master` 虽有更新，但不属于当前分支，无需 pull。
- 私人 SDK 保护：三个个人文件继续保持 `skip-worktree`，当前工作区版本与仓库外备份 `/home/tbl/.local-backups/robot_motion_executor-sdk-20260811` SHA-256 一致；没有 stash，也没有清除 skip-worktree。
- 待推送提交审查：`efa6b24` 包含 38 个公共任务文件；其中 `xcore_path_client.py` 的公共路径回放/SDK 布局适配改动和新增 `test_path_replay.py` 属于该提交本身。当前工作区个人版本的 blob 与 HEAD 不同，但不会随 push 发送。
- 验证：首次测试因错误覆盖 ROS `PYTHONPATH` 导致 `dexbot_interfaces` 导入失败；修正为追加执行仓库路径后，接口导入通过、定向测试 41 passed、compileall 通过、`colcon build --symlink-install --packages-select dexbot_motion_executor` 通过、提交 patch `git diff --check` 通过、无 staged 或普通工作区改动。
- 额外验证：从 `efa6b24` 导出的干净提交快照在临时目录中重新执行同一组 41 个定向测试和 `colcon build`，均通过；`git push --dry-run origin robam_kitchen` 成功显示 `4635b3e..efa6b24`。
- 当前结论：在“个人 SDK 后续工作区改动不提交，但允许提交中包含本次公共路径回放功能对 `xcore_path_client.py` 的改动和其测试”的口径下，执行仓库已达到手动 push 前标准；本轮未执行 push。

## 当前会话（2026-08-11 主仓库 SDK 排除复核与 push 前验证）

- 用户要求：收尾 `kitchen_robot_home` 的 SDK 问题，确认主仓库达到 push 标准；用户手动 push，本轮不处理 `robot_motion_executor`。
- 主仓库状态：分支 `robam_kitchen`，`HEAD=a0aefce`，已 `git fetch origin`，与 `origin/robam_kitchen` 处于 `0/0`，工作区干净。
- SDK 结论：SDK v0.7 迁移/替换改动仍保存在未应用的 `stash@{0}`，未进入当前工作树；从任务基线 `9de887a` 到当前 `HEAD` 的提交路径不包含 `src/sdk` 改动。未删除或修改 stash，保留本地 SDK 资源。
- 主仓库验证：`compileall` 通过；定向测试 18 passed；`colcon build --symlink-install --packages-select dexbot_bringup dexbot_task_planner` 通过；`git diff --check` 通过；SDK 泄漏检查通过。
- push 判断：主仓库当前没有待 push 提交（远端已与 HEAD 同步），因此不存在需要本轮手动 push 的主仓库增量。若用户确认远端分支就是目标分支，可视为 push 前检查通过；不执行 push。
- 执行仓库边界：仅读取到 `robot_motion_executor` 工作区干净、本地领先 `origin/robam_kitchen` 1 个提交；用户要求下一阶段再处理，暂不修改或验证其提交。
- 日志对齐：此前 2026-08-10 条目中的 `HEAD=7d8dd4d`/“尚未 push”已被当前事实 supersede；本条记录当前事实。

## 当前会话（2026-08-10 kitchen SDK 排除与待推送确认）

- 目标：`kitchen_robot_home` 待推送提交只保留三个 pan-pour Policy / 正式 V1 任务改动，SDK 改动不提交、不推送。
- 已完成本地历史重写（原提交 `39c3d83` → 新提交 `7d8dd4d`，共 4 个提交），从待推送提交中移除 `src/sdk/arm_api/Python/lbot/lbot_robot_xcore.py`：
  - `51c148c 接入 teach_pan_pour 规划链路并修复驱动启动配置`
  - `4089b40 新增 teach_pan_pour_delta 增量倾倒规划链路`
  - `2f4949e 正式 V1 完整运动链接入单一自包含 pan_pour Skill`
  - `7d8dd4d V1 pan_pour policy: add WAITING_FOR_BASE_RETURN phase`
- 备份分支 `backup/robam_kitchen-before-sdk-exclusion-20260810` 指向原 `39c3d83`；当前分支与备份差异只剩 SDK 文件，说明任务代码未随重写改变。
- 本地工作区 SDK 改动保持未提交：v0.5.1 删除状态 + v0.7.1 未跟踪目录；`stash@{0}` 未动。
- `git fetch origin` 后远端 `robam_kitchen` 无新提交；`origin/robam_kitchen..HEAD` 不含任何 `/sdk/` 路径。
- 验证：`git diff --check` 通过；`compileall` 通过；定向测试 31 passed（`PYTHONNOUSERSITE=1` + `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`，绕过本机 numpy 2.2.6/anyio 插件问题）。
- 待办：按用户确认顺序，下一步是 push 前最终 review；尚未 push。SDK 工作区改动仍保留，不会被提交。

## 当前会话（2026-08-07 V1 Policy 对齐工程进度）

- 任务：把 V1 正式版 Policy（`pan_pour` / `PanPourPolicy`）更新到工程记录最新进度，对齐后准备右臂标定。
- 落地（分支 `robam_kitchen`，仅改 2 个文件，SDK 未动）：从 `stash@{0}` 单独提取 `pan_pour_policy.py` + `test_pan_pour_policy.py` 的 BASE_RETURN 改动，应用到工作区。
  - `PanPourPolicy` 新增 `WAITING_FOR_BASE_RETURN` 阶段，`POUR_DELTA_REPLAY` 完成后的下一阶段由 `PUT_FIXED` 改为 `WAITING_FOR_BASE_RETURN`；`WAITING_FOR_BASE_RETURN` 消费 `update_base_positioned` 上报后重置 `_base_positioned` 并进入 `PUT_FIXED`。
  - `WAITING_FOR_BASE_POSITION` 消费后重置 `_base_positioned` 标志，保证两次底盘移动都需外部确认。
  - `test_pan_pour_policy.py` 新增对 `BASE_RETURN` WAIT 阶段与推进的断言。
- 修复：`install/dexbot_task_planner` 安装产物损坏（`pan_pour` 目录空残留、`.colcon_install_manifest` 无记录），删除后 `colcon build --symlink-install --packages-select dexbot_task_planner` 重建成功。
- 验证：`PYTHONNOUSERSITE=1 python3 -m pytest src/dexbot_task_planner/test/test_pan_pour_policy.py src/dexbot_task_planner/test/test_task_planner_decision_dispatch.py -q` **13 passed**，与工程记录"2026-08-06 V1 底盘移动第二预留位"预期一致。状态 `implemented-unverified`（真机未验证）。
- 待办：git 尚未提交（`M` 状态）；SDK 目录状态乱（v0.5.1 缺失 `D` / v0.7.1 未跟踪 `??`），提交时只提交 `src/dexbot_task_planner/` 两个文件，需用户确认。之后开始右臂（192.168.2.160）标定准备，标定前需用户明确确认才启动。

## 当前会话（2026-08-07 三个 pan-pour Policy 完整性检查）

- 检查范围：`kitchen_robot_home`（robam_kitchen 分支）主仓库三个 Policy（`pan_pour` V1 正式版、`teach_pan_pour`、`teach_pan_pour_delta` 两个测试版）+ 执行仓库对应 Skill。仅检查与记录，未改动任何代码。
- 结论一（V1 正式版）：**落后于工程记录最新进度**。`PanPourPolicy` 当前阶段链为 `...POUR_DELTA_REPLAY → PUT_FIXED → OPEN_HAND → RETURN_HOME`，缺少 2026-08-06「V1 底盘移动第二预留位」要求的 `WAITING_FOR_BASE_RETURN` 阶段，且 `WAITING_FOR_BASE_POSITION` 消费后未重置 `_base_positioned` 标志；对应测试（test_pan_pour_policy.py）也无 BASE_RETURN 断言。该最新改动完整存在于 `stash@{0}`（WIP on robam_kitchen: e26740a，`pan_pour_policy.py` 10 行 + 测试 5 行），尚未提交。
- 结论（teach_pan_pour 测试版）：**进度正常**。阶段序列 `home_open → move_to_grasp_ready → close_gripper → move_to_lift → move_to_pour_ready → pour_replay → put_replay → open_gripper → return_home`，与工程记录 `progress.md:303` 完全一致；无未提交改动；执行仓库 `TeachPanPourSkill` 与资源齐全。
- 结论（teach_pan_pour_delta 测试版）：**进度正常**。阶段序列 `home_open → move_to_grasp_ready → close_gripper → move_to_lift → move_to_pour_ready → pour_delta_replay → put_fixed → open_gripper → return_home`，与工程记录 `progress.md:481` 完全一致；无未提交改动；执行仓库 `TeachPanPourDeltaSkill` 与 `pour_delta.json` 资源齐全。
- 接线完整：`PlanType` 含 `PLAN_PAN_POUR` / `PLAN_TEACH_PAN_POUR` / `PLAN_TEACH_PAN_POUR_DELTA`；`task_planner_node` import 并路由三种类型；`setup.py` 打包 params；执行仓库 `motion_executor_node` 注册 `pan_pour`/`teach_pan_pour`/`teach_pan_pour_delta` 三个 Skill。
- 待办：若要让 V1 正式版回到最新进度，需应用 `stash@{0}`（会一并带入 SDK v0.5→0.7 切换与标定配置），或单独提取 `pan_pour_policy.py` + `test_pan_pour_policy.py` 的 BASE_RETURN 改动。用户暂不处理 SDK，未执行。

## 当前会话（2026-08-07 左臂手眼标定成功 + VERSIONS 清理）

- 左臂（192.168.2.159）手眼标定跑通并出结果：**22 个有效样本**，平移 RMSE `0.001825 m`（≈1.8 mm），旋转 RMSE `0.805°`，结果写入 `/home/tbl/Project/boss_electrics/标定结果/left_calibration_result.yaml`（含 `T_base_cam`、`T_tcp_marker`、`calibration_result`）+ CSV/JSON 样本。
- 覆盖度：TCP 位置约 10×8×6 cm、姿态 ±24°（rx 含 348° 翻转换算），ArUco 在相机系 3D 分布 `x[-0.00..0.09] y[-0.01..0.12] z[0.44..0.59]`，非单点凑数。
- `T_base_cam` 平移 `[0.110, -0.274, -0.068]`（相机在左臂基座系下位置），符合"相机装在头部、眼在手外"物理布局。
- 修复来源：`dexbot_toolbox` 升级到 **1.0.2-0jammy**（dpkg 已确认），解决了之前 ArUco 收不到 camera_info 的 QoS 断链问题；`robot_params.yaml` 左右臂 IP（左 .159 / 右 .160）、`pose_frame_rot_x_deg`（-90/90）、`ref/trans` 归零，基准与标定脚本假设对齐。
- 顺手修正：`VERSIONS.yaml` 里 `dexbot_toolbox` 出现**两个同名键**（1.0.0 + 1.0.2），YAML 后者覆盖前者，已合并成一个 `1.0.2-0jammy` 条目（git 待提交）。
- 下一步：右臂（192.168.2.160）标定，输出 `right_calibration_result.yaml`（两次之间相机物理位置不动）；之后用 `scripts/generate_robot_center_frames.py --left-calibration ... --right-calibration ... --robot-params ... --shoulder-axis y` 生成 `T_center_cam`，再写入感知 `calibration_result.yaml` 并置 `pan_pour_params.yaml` 的 `configured: true`。

## 当前会话（2026-08-07 SDK 版本切换 v0.5.1.ar_12 → v0.7.1.ar_6）

- 背景：CAL-06 标定 17 个采样姿态全失败，错误 `arm-angle range search requires 7-DOF robot, got 13`。根因定位：`ElbowRangeSearcher` 用 `len(jointPos)` 当自由度，而 Er Pro 机型 + 旧 SDK 返回 13 元（7 真实关节 + 6 外部轴占位），`_joint_count=13` 触发 `!=7` 校验抛错，IK 从未执行。
- **用户定性（最终）**：不是脚本问题，而是**当前用的 xCore SDK 版本不正确**，应使用 `kitchen_robot_home/src/sdk/xcoresdk_python-v0.7.1.ar_6`；要求把用到 SDK 的路径统一换成这个版本。
- 已替换引用（从 `xcoresdk_python-v0.5.1.ar_12` → `xcoresdk_python-v0.7.1.ar_6`）：
  - kitchen_robot_home：`.localconfig` 的 `xcoresdk_sdk_path`（→ `.../xcoresdk_python-v0.7.1.ar_6/Release/linux`，这是标定 robot_driver 实际加载路径）、`src/sdk/arm_api/Python/lbot/lbot_robot_xcore.py`（DEFAULT/LEGACY_ROOT + 相对候选）、`README.md` 目录树。
  - robot_motion_executor：`utils/xcore_path_client.py`（2 处）、`utils/smoothie_path_record_replay.py`、`test/test_path_replay.py` 断言。
  - GUI（~/Project/gui，独立仓库）：`services/arm/xcore.py`、`services/registry.py`（ws_root 判定）、`pages/arm_hand.py`（提示文案）、`main.py`（sys.path 注入）、`README.md`。
- 验证：全局 `rg '0\.5\.1\.ar_12' gui boss_electrics` 无残留；新 SDK `xCoreSDK_python.cpython-310-x86_64-linux-gnu.so` 在本机 python3.10 导入 OK（`import xCoreSDK_python` 成功）；`test_path_replay.py` 6 passed。
- 注意：GUI `is_workspace_root` 判定也切到 v0.7.1.ar_6，若别的旧工作区只有 v0.5.1.ar_12 会被判为无效工作区；本次目标工作区已含新 SDK，行为一致。
- 下一步：从 `kitchen_robot_home` 用新 SDK 重跑左臂标定（`export DEXBOT_ROBOT_IP=192.168.2.159`），确认 `getJointPos` 返回 7 元、不再要求 A/B 改 .deb 肘部逻辑；多个改动按仓库分别 commit，不 push。

## 当前会话（2026-08-07 手眼标定 CAL-01/02/04 处理）

- CAL-01 完成：`dexbot_toolbox` 已加入 `VERSIONS.yaml`（`ros-humble-dexbot-toolbox=1.0.0-0jammy`），执行 `sudo bash scripts/setup_apt_repos.sh` 安装成功，`verify_versions.sh` 7/7 通过，包位于 `/opt/ros/humble`，含 `aruco_detector_node` / `hand_eye_calibration_node` / `camera_viewer_node`。
- CAL-02 复核（基于已安装 1.0.0 源码）：`CameraDriverNode` 发布绝对话题 `/camera/color/image_raw`、`/camera/color/camera_info`；`aruco_detector_node` 硬编码订阅 `/camera/color/image_raw`、默认订阅 `/camera/color/camera_info`；`camera_viewer_node` 默认订阅 `/camera/color/image_raw`。绝对话题不受 launch `namespace='camera1'` 影响，ArUco/viewer 订阅与相机发布一致，**无需改 launch 话题 remap**；此前按 715 旧版推断的话题不匹配在 1.0.0 上不成立。
- CAL-03 硬件识别（✅ 实机确认）：USB 实机是 **Orbbec Gemini 336L**（sn `CPCAC53000FP`），不是 RealSense D435。SDK 枚举 COLOR 最高 1280x720、DEPTH 最高 1280x800；`camera1_ost.yaml`（1280x720/fx≈610.8）与 336L 原生内参一致。`camera1_params.yaml` 需从 `realsense_d435` 切回 `gemini335l` 块（1280x720 + ost_yaml）。本机 python 环境有 numpy 2.2.6 与 cv2 冲突、且 pyorbbecsdk 仅在 user-site，真机跑相机前需统一环境。
- CAL-03 落地（✅ 已改并真机验证）：`camera1_params.yaml` 已切到 `gemini335l`/1280x720/`ost_yaml`（D435 块注释保留）；相机 python 环境已用本地隔离方案解决（`/home/tbl/camera_env/`，`PYTHONNOUSERSITE=1` + 隔离 pyorbbecsdk），`camera_driver_node` 实机 `Camera backend: real device (Orbbec Gemini 335L)`，1280x720@15 出图，发布 `/camera/color/*` 与 depth 话题，帧处理 ~13-25ms。详见 `docs/hand_eye_calibration.md`。
- CAL-05（✅ IP 已确认）：标定臂 IP 左臂 `192.168.2.159`、右臂 `192.168.2.160`；标定前 `export DEXBOT_ROBOT_IP=192.168.2.159`，并确认 `robot_params.yaml` 的 IP 一致。
- CAL-04 完成（✅ 2026-08-07）：用户实测标定板整体为正方形，黑色外沿边长 **13 cm（130 mm）**；字典已确认为 6X6。`marker_length=0.13` 与 `calibration.launch.py` 默认值完全一致，启动标定时显式传 `marker_length:=0.13` 即可，launch 的 `DICT_6X6_250` 无需改。前置问题（CAL-01/02/03/04/05）全部闭环。
- 真机状态：主链路（`dexrob_full`）已停止；采样空间范围用户明确不用管；所有前置问题已闭环。
- 已同步 `.project-log/docs/hand_eye_calibration.md` 与 `TASK-019` 状态（移除 CAL-01/CAL-02，标记 CAL-04 完成）。
- 下一轮待办：用 `source /home/tbl/camera_env/calibration_env.sh` 统一环境，先跑 `reset_robot_params_frames.py` 复位左右臂基准，再单臂自动标定（左右臂各一次，两次间相机物理位置不动），生成 `T_base_cam` 与中心坐标 `T_center_cam`，并按需填 `pan_pour_params.yaml` 的 `configured` 链路。

## 当前会话（2026-08-06 V1 底盘移动第二预留位）

- 用户澄清：倾倒完成、把锅放回灶台前，底盘需要再移动一次回到原工位；但本质仍是同一个底盘移动接口，不做“反向”专用逻辑。
- `PanPourPolicy` 在 `POUR_DELTA_REPLAY` 与 `PUT_FIXED` 之间新增 `WAITING_FOR_BASE_RETURN` 阶段，复用 `update_base_positioned` 等待底盘再次上报完成；第一次 `WAITING_FOR_BASE_POSITION` 消费后重置标志，保证两次底盘移动都需外部确认。
- 验证：`test_pan_pour_policy.py` + `test_task_planner_decision_dispatch.py` 13 passed。

## 当前会话（2026-08-06 正式 V1 单一自包含 pan_pour Skill）

- 用户确认正式 V1 完整复刻测试版手部逻辑：不交 `robot_driver/gripper_action` 命名动作，而是 Skill 直给 `SET_HAND_ANGLES` + `SET_HAND_TORQUES`（角度/力矩用测试版已调好的值，V1 不改数值）。
- 参数思路选思路 1：V1 只有一个 skill 包，运动参数（灵巧手角度、固定关节位姿、轨迹文件）全部放包内并完全自包含，不再引用临时 teach 链路任何资源。
- 完整阶段链：抓取 → 闭手 → 提锅/准备倾倒 → 倾倒（增量回放）→ 放锅（固定点，复用抓取点关节角）→ 张手 → 回 home，放锅/张手/回位三段后续阶段一并接入。
- 主仓库：新增 `PLAN_PAN_POUR = "pan_pour"`；`PanPourPolicy` 阶段链改为 `CLOSE_GRIPPER(SET_HAND)` → `POUR_DELTA_REPLAY` → `PUT_FIXED` → `OPEN_HAND` → `RETURN_HOME` → `COMPLETE`；移除 `gripper.close_action_name` 参数与 kinematics 校验；Planner 把 `PLAN_PAN_POUR` 路由到 `_build_skill_goal`。
- 执行仓库：新增自包含 `skills/pan_pour/`（`PanPourSkill`，TASK_TYPE=`pan_pour`），自带 `arm_poses_left.json` / `hand_presets.yaml` / `delta_trajectories/pour_delta.json`（103 点字节一致副本）；`motion_executor_node` 注册、`setup.py` 打包；删除旧 `pan_pour_delta_replay` 目录、注册、setup 条目与测试。
- 验证：主仓库 13 定向 passed、执行仓 9 定向 passed；两包 `colcon build --symlink-install`、`compileall`、`git diff --check` 通过；新增 Skill 与测试 flake8 干净。既有全仓库 flake8/pep257 基线仍失败（与本次无关）。
- 执行仓库测试需从 `src/dexbot_motion_executor/` 目录运行，且本机用 `PYTHONNOUSERSITE=1` 隔离 `~/.local` 的 numpy 2.2.6/anyio 4.13。
- 状态：`implemented-unverified`；正式 V1 未标定（`pan_pour.configured=false`），真机验证待现场标定后进行（含急停、左臂单控制链、起点一致性）。

## 当前会话（2026-07-30 TASK-012 动态 Policy 骨架）

- `TASK-012` 的可本地验证范围已实现：`PanPourPolicy` 注册为 `pan_pour`，由一个 `_phase` 依次驱动 `waiting_for_configuration → waiting_for_handle_detection → move_to_grasp → close_gripper → move_to_pour_ready → waiting_for_base_position → waiting_for_plate_detection → move_to_pour_position → waiting_for_pour_replay_adapter`。
- 抓取阶段只消费未来感知适配器提供的 `grasp_point_C` 与 `pca_axis_C`，使用 `tcp_grasp` 反解为左臂 base 下法兰目标；准备倾倒和倾倒接近使用 `tcp_pan`。没有把现有通用 `ScenePerception/ObjectDetection.pose` 擅自解释为锅把或餐盘语义。
- 动作完成仍由现有 Planner Action 结果回调调用 `update_step_status()`；只有 `COMPLETED` 推进 phase。配置、感知、底盘或回放能力未就绪时，Policy 返回 `WAIT`，Planner 保留 active task 且不发送 Action。
- 验证：28 个定向测试、`dexbot_interfaces dexbot_bringup dexbot_task_planner` 三包构建、`compileall` 和 `git diff --check` 通过。未启动真实 ROS 节点、MotionExecutor、目标 Driver deb 或硬件。
- `TASK-012` 保持 `blocked`，因为完整集成仍缺三项外部能力：感知组字段/坐标/新鲜度契约、底盘 ROS 生命周期接口、`TASK-013` 的相对法兰回放 Skill。构建和 Python 缓存将在证据记录后清理。

## 当前会话（2026-07-30 感知路径确认）

## 当前会话（2026-08-06 正式 V1 增量倾倒回放接入）

- 用户确认下一步：把临时测试版本 `teach_pan_pour_delta` 已真机跑通的增量倾倒回放完整迁移到正式 V1（`pan_pour` / `PanPourPolicy`），思路不变：创建短生命周期 xCore 连接、按既有增量回放模式重播；不放回/home，V1 最小闭环到倾倒完成结束。
- 主仓库改动：新增 `PlanType.PLAN_PAN_POUR_DELTA_REPLAY = "pan_pour_delta_replay"`；`PanPourPolicy` 终态阶段由永久 `WAITING_FOR_POUR_REPLAY_ADAPTER` 改为 `POUR_DELTA_REPLAY`，在 `MOVE_TO_POUR_POSITION` 完成后下发 `pour_delta_replay` 步骤（`action_name="pour_delta_replay"`，`arm_type=0`），完成后返回 `COMPLETE`；`task_planner_node._build_execute_task_goal` 把该 PlanType 路由到 `_build_skill_goal`。
- 执行仓库改动：新增独立 skill `pan_pour_delta_replay`（`PanPourDeltaReplaySkill`，`TASK_TYPE="pan_pour_delta_replay"`），只接受 `pour_delta_replay`，复用既有 `LOCAL_DELTA_FLANGE_REPLAY` 原语与 `delta_flange_replay_client`；注册到 `motion_executor_node`，并在 `setup.py` 增加资源打包；`pour_delta.json`（103 点）字节一致的独立副本。
- 验证：主仓库 `test_pan_pour_policy.py` + `test_task_planner_decision_dispatch.py` 定向 14 passed；执行仓库新增 `test_pan_pour_delta_replay_skill.py` 4 passed；两仓库 `colcon build --symlink-install`、`compileall`、`git diff --check` 通过。既有全仓库 flake8/pep257 基线扫描仍失败（与本次改动无关）。
- 测试执行说明：本机 `~/.local` 装有 numpy 2.2.6 与 anyio 4.13，污染系统 Python 导致 cv2 与 pytest 插件报错；使用 `PYTHONNOUSERSITE=1` 隔离用户级 site-packages（系统 numpy 1.21.5 / cv2 4.5.4 / pytest 6.2.5）后测试通过。这是本机环境问题，未改仓库。
- 状态：`implemented-unverified`；正式 V1 尚未标定（`pan_pour.configured=false`），未做真机验证。真机前确认急停、左臂单控制链、C 系/锅具 TCP 标定与起点一致性。

## 当前会话（2026-08-06 V1 Skill 边界确认）

- 用户确认 V1 只新增 1 个专用 Skill（`PanPourDeltaReplaySkill`），其余复用现有 `move_cartesian` / `gripper_action` API；感知走 Planner 侧，底盘 Skill 视接口归属待定。
- 已固化：`.project-log/business-logic/pan_pour_v1_skills.md`；ARCH-001 组件清单更新（新增 `PanPourDeltaReplaySkill`、更新 `BossElectricsPourSkill` 职责、新增 `skill_boundary` 小节）。

- 用户确认遵从现有框架，老板电器任务采用路径 A：`ScenePerception → TaskPlannerNode._on_scene() → WorldState → PanPourPolicy`。
- 正式流程不新增任务专用感知 topic、PerceptionBridge 或第二套对象缓存；`PanPourPolicy` 通过已有 `world=self._world` 读取统一世界模型。
- 715 参考仓库中的专用感知桥接器仅作为对比证据，不复制到老板电器任务。
- 感知组仍需确认锅把抓取点、PCA 主轴、餐盘中心、source frame、有效性、置信度和新鲜度字段契约；在契约到达前，不把通用 `ObjectDetection.pose` 擅自解释为业务语义。
- 记录：`DEC-016`、`ARCH-001.perception_boundary`；产品代码未修改。

## 当前会话（2026-07-30 TASK-013 离线轨迹基础）

- `TASK-013` 的可独立实现范围已完成：在执行仓库新增 `FlangeDeltaTrajectory`，只解析版本化 `spatial_only`、`flangeInBase` 轨迹资产，并以 `T_current @ Delta_i` 产生绝对法兰航点；不创建 ROS Action、Skill、Driver 客户端或 xCore 直连。
- schema 明确固定 `m`、`rad`、`xyz` RPY、`initial_flange` 参考和 identity 首增量，防止把 TCP、毫米、不同欧拉角顺序或绝对路径误当作本 V1 资产。
- 验证：10 个定向测试、模块编译和两仓库 diff 检查通过。`TASK-013` 仍 blocked，直到目标 Driver 实测确认当前法兰位姿/MoveCartesian 语义，且团队采集并版本化真实 V1 倾倒轨迹。
- 已同步 V1 范围：当前最小闭环在倾倒完成结束；放回锅具、张开灵巧手和 home 为后续 cleanup 扩展，不再列为当前 V1 的完成条件。

## 当前会话（2026-07-31 工程包初始化与环境验证）

- 已按主仓库 `scripts/setup_apt_repos.sh` 配置私有 apt 源，并安装 `VERSIONS.yaml` 锁定的 6 个 ROS `.deb` 依赖；严格版本校验通过，ROS 包均位于 `/opt/ros/humble`。
- 已执行 `rosdep install --from-paths src --ignore-src -r -y`，结果为 `All required rosdeps installed successfully`。
- 主仓库 `kitchen_robot_home` 已完成 `colcon build --symlink-install`：8 个包构建成功。旧 SDK demo 包存在无 `install` target 警告，但不影响构建结果。
- 执行仓库 `robot_motion_executor` 已完成 `colcon build --symlink-install`：`dexbot_motion_executor` 构建成功。
- 主仓库 V1 定向测试通过：28 passed；执行仓库新增轨迹模块与现有右夹爪测试通过：10 passed，1 个测试收集警告（Skill 类有 `__init__`，不影响结果）。
- `git diff --check` 与两仓库 `python3 -m compileall -q src` 通过。未覆盖真实 ROS 节点、MotionExecutor、Driver 或硬件运行。
- 项目声明的 Conda 环境 `robot` 当前不存在；执行 `mamba env create -f src/env/environment.yml` 失败，原因是当前 channels 无法解析 `pyorbbecsdk2=2.0.18`、`pyrealsense2=2.57.7.10387` 以及 `torch/torchaudio/torchvision` 的 `+cu126` 版本。未修改 `environment.yml`。
- 两仓库已有未提交业务改动均保留，未执行清理、回滚、commit 或 push。构建产物按仓库忽略规则保留在各自工作区，后续如需清理可删除对应 `build/ install/ log/`。
- 当前下一步：若要运行感知节点，需要由环境维护者提供可解析的 Python/CUDA 依赖安装方案；若继续 V1 工程实现，优先处理感知字段契约、底盘接口和真实回放 Skill 三个外部边界。

## 当前会话（2026-08-03 临时拖动示教测试路径澄清）

- 正式路径暂缓：感知接口和底盘接口尚未就绪；新增独立临时测试路径，不修改正式 `PanPourPolicy` 的业务语义。
- 临时路径目标：固定工位、左臂优先、无视觉、无底盘，通过普通拖动示教录制控制器命名路径并回放，验证拿锅、端锅、倾倒、放锅闭环。
- 已确认录制入口：`robot_motion_executor` 的 `PathRecordSkill`，路由键为 `path_record`；`target.arm_type` 选择机械臂，`target.object_id` 作为控制器内部路径名；底层通过独立 xCore 连接调用 `enableDrag`、`startRecordPath`、`stopRecordPath`、`saveRecordPath`。
- 已确认录制风险：`PathRecordSkill` 会直接连接 xCore，可能与同一机械臂的 `robot_driver` 竞争；真机录制时必须避免两个控制链路同时控制同一机械臂。
- 已确认回放工具：`smoothie_path_record_replay.py` 通过 `replayPath(name, rate)` 和 `moveStart()` 调用控制器回放；路径保存在机器人控制器内部，不是 Planner 内存中的航点列表。
- 关键架构事实：当前 `MotionExecutorNode` 注册了 `path_record`，但没有注册通用 `path_replay`；`smoothie_dispense.py` 虽构造了 `REPLAY_RECORDED_PATH` 原语，但当前执行节点没有对应执行分支，且该 Skill 也未在 `_initialize_skills()` 注册。因此不能把现有代码直接视为已闭合的 ROS 回放链路。
- 临时 Policy 方向：新增独立 `TeachPanPourPolicy`/独立任务类型，按阶段发送路径回放信号和现有 `gripper_action`，不修改正式 `PanPourPolicy`；具体路径拆分、路径名和抓取/张手动作边界待业务确认。
- 手眼标定事实：现有 `calibration.launch.py` 启动相机、ArUco、`robot_driver` 和 `hand_eye_calibration_node`，通过 `/calibration/start_calibration` 收集样本并输出 `T_base_cam`；`generate_robot_center_frames.py` 可基于左右标定结果生成统一中心坐标系配置。
- 临时固定工位路径若完全不依赖视觉和相机坐标，则手眼标定不是录制/回放的前置条件；只有需要视觉定位、中心坐标转换或跨工位泛化时才是前置依赖。标定流程和输出仍需真机验证。
- 证据状态：源码结论为 `valid`；控制器实际起停、路径起点行为、驱动竞争、回放安全性和完整锅具闭环均为 `candidate`，必须真机验证。当前未修改产品代码、未启动硬件。
- 用户已确认临时测试动作拆分：
  - `TAKE_PAN` = 左臂普通示教移动轨迹 + 现有 `gripper_action` 灵巧手闭合；
  - `CARRY_PAN` = 左臂单独录制并回放一条端锅轨迹；
  - `POUR_PAN` = 左臂单独录制并回放一条倾倒轨迹；
  - `PUT_PAN` = 左臂单独录制并回放一条放锅轨迹；
  - 全部动作使用左臂；灵巧手动作统一复用现有 `gripper_action` 承载。
- 因此临时 Policy 的最小阶段序列固定为：`take_move → close_gripper → carry_replay → pour_replay → put_replay`。是否在 `put_replay` 前后增加 `open_gripper` 尚未由本次确认明确，暂不擅自写入业务规则。
- `TASK-016` 工程规格已形成：`.project-log/specs/TASK-016.md`。规格采用独立 `TeachPanPourPolicy` + `path_replay` Skill，复用 `ExecuteTask`、`TaskTarget.object_id` 和现有 `gripper_action`，不修改公共消息。
- 临时回放的执行取舍已显式记录：当前控制器命名路径回放入口是 xCore 直连，因此允许在临时测试 Skill 中复用该能力；同一左臂必须关闭/暂停 `robot_driver` 竞争。这是临时测试约束，不是正式 V1 的长期 Executor 架构承诺。
- `TASK-016` 当前状态：工程规格可实施，但在代码实现前仍需确认放锅后张手时序，并通过 Mock/单元测试先验证阶段顺序和失败传播。

## 当前会话（2026-07-30 TASK-011 实现）

- `TASK-011` 已完成并通过定向验证。新增任务私有 `pan_pour_params.yaml`，由 `dexrob_full.launch.py` 注入 `task_planner_node`；未修改共享 `robot_params.yaml` 或任何公共 ROS 接口。
- 新增纯计算模块 `pan_pour_kinematics.py`：统一使用 `T_A_B` 变换记号，完成抓取/锅具 TCP 目标从中心坐标系到左臂 base 法兰目标的计算：`T_B_F = T_B_C @ T_C_TCP @ inverse(T_F_TCP)`；PCA 抓取偏置在 C 系沿归一化 PCA 向量计算。
- `PanPourParameters.validate_for_execution()` 明确拒绝 `configured: false` 的占位模板。当前没有实际标定值，因此不得将模板用于实机动作。
- 验证：21 个定向测试通过；`dexbot_bringup` 与 `dexbot_task_planner` 构建通过；`git diff --check` 通过。未启动真实 ROS 节点、MotionExecutor、目标 Driver deb 或硬件。构建和 Python 缓存已清理。
- 当前下一步：`TASK-012` 仍等待感知组最终字段契约和底盘组 ROS 接口；获得契约后接入单个 `PanPourPolicy` 的动态阶段状态机，并从本任务的私有参数快照取 TCP/偏置值。

## 当前会话（2026-07-28 第二轮）

## 当前会话（2026-07-29 源码学习）

- 用户要求从源码内部建立架构理解，反对只停留在模块职责和抽象流程层面。
- 已完成的源码阅读链：`_on_start_task()`、`_prepare_start_task_context()`、`_clear_runtime_state()`、`_on_tick()`、`_generate_goal_by_task_type()`、`_build_gripper_action_goal()`。
- 已用 `test_gripper` 具体追踪：`StartTask(task_type="test_gripper")` 如何创建 `TestGripperPolicy`，定时器如何门控，Policy 如何返回 `PlannedStep(plan_type="gripper_action", action_name="张开", arm_type=1)`，Planner 如何构造 `ExecuteTask.Goal`。
- 已确认 `ExecuteTask.Goal` 是 ROS 2 Action 的 Goal 消息对象，外层 `task_id` 标识任务，`task_type` 负责下游路由，`target` 携带具体动作参数。
- 已确认当前真实源码中 `_build_gripper_action_goal()` 只填 `TaskTarget.arm_type/action_name`，没有填 `TaskTarget.task_id/object_id/class_name`；此前示意讲解已纠正。
- 已记录学习方法：每个概念必须落到具体类、方法、属性、调用关系、输入值、输出对象和下游消费；先源码事实，再概念类比。
- 用户进一步确认偏好的讲解结构：`完整任务时间线 → 关键状态变量变化表 → 工程思路总结`。已将 `test_gripper` 的时间线和变量表作为后续讲解模板。
- 复习笔记：`.project-log/docs/source-code-learning.md`
- 下一步：继续阅读 `TestGripperPolicy.select_next_goal()` 和结果回调，再进入 MotionExecutor 的 ActionServer 路由。
- 用户要求将已确认的讲解方法抽象为可复用资产；已创建并安装全局显式触发 Skill：`/home/tbl/.codex/skills/b-source-code-tutoring/`。
- Skill 固化的顺序为：`具体输入 → 真实运行时间线 → 状态变量生命周期 → 源码逐行实现 → 下游消费/结果回调 → 最后工程概念抽象`；结构校验已通过，评测样例位于 `.project-log/evals/source-code-tutoring.yaml`。

## 技术选型进行中（2026-07-29）

- 完成 TestGripperPolicy 完整源码阅读，对比分析 TestHeartPolicy（场景感知 plan）和 PeelApplePolicy（CSV/运动学生成）。
- 发现 V1 流程存在两段时序约束：底盘移动前锅把可见、底盘移动后餐盘才进入视野。
- 确认 Policy 不需要预生成全部步骤：`select_next_goal()` 每次被调用的特性 + `_world` 持续更新 + `update_step_status` 提供反馈 → 一个 Policy 内分阶段生成即可。
- 已记录 DEC-009，更新架构描述。
- 下一步：确认 WorldState 中餐盘检测结果的字段契约和感知组输出 Topic。

## 完整调用链串讲已记录（2026-07-29）
- 应用户要求，完成了从 `__init__` 到 `_on_result` 的完整 9 阶段时间线串讲，覆盖：初始化 → StartTask → 门控 → Policy 决策 → Goal 构建 → 发送 + 闭包注册 → Goal Handle 确认 → 等待空转 → 结果回调 → 步骤状态更新 → 任务结束。
- 记录了 9 个阶段的完整代码路径，每个阶段都附带了具体源码行号和变量值。
- 记录了关键变量生命周期总表（11 个变量在 5 个时间点的值）。
- 总结了四个属性层面（上下文层/运行状态层/门控标志层/代际保护层）的工程划分。
- 添加了源码路径索引，供后续快速定位关键函数行号。
- 完整记录已追加到 `.project-log/docs/source-code-learning.md`（307→842行）。
- 当前状态：TASK-008 仍在进行中，产品代码未修改。
- 下一步（用户待确认）：继续读 MotionExecutor 端的 ActionServer 路由，还是切换到其他方向。
- 
## 参数配置模式调查（2026-07-29）
- 调查了现有代码的参数管理方式：ROS 2 参数系统 + YAML 配置文件，集中在 `dexbot_bringup/config/`，按子系统分目录。
- 当前 `TaskPlannerNode` 是唯一裸启动的核心节点（无 parameters= 参数文件），所有值硬编码在 `__init__` 中。
- V1 技术参数（抓取偏置、等待位置、倾倒偏置、锅具 TCP、home 位姿等）可遵循现有模式：
  - 创建 `dexbot_bringup/config/pan_pour/pan_pour_params.yaml`
  - 在 `TaskPlannerNode.__init__()` 中添加 `declare_parameter()` 声明
  - 在 `dexrob_full.launch.py` 中为 task_planner_node 添加 `parameters=[pan_pour_config]`
- 参数命名采用分层结构，如 `pan_pour.grasp_offset`，Policy 内部通过 Node 的参数接口读取。
- 此项属于技术选型发现，待进入 engineering-landing 阶段后再实现，当前不修改产品代码。

## 技术选型初步确认（2026-07-29）
- 用户确认选型 2 采用方案 A：单个 `PanPourPolicy`，内部维护 `_phase`，根据 `WorldState` 动态生成下一阶段。
- 用户确认选型 3：业务目标和中间位姿统一在机器人中心坐标系 C 下计算，靠近执行器的适配层再转换到机械臂/RobotDriver 坐标系。
- 用户确认选型 4：单目标/单原子动作复用现有 API/MotionPrimitive；复杂动作拆解才使用 Skill。
- 用户暂定选型 5：底盘接口等待底盘组提供准确消息后再定，不阻塞当前机械臂流程选型。
- 用户确认选型 6：技术参数采用 ROS 2 YAML 参数配置，通过 launch 注入，不在 Policy 内硬编码。
- 选型 1（TaskTarget、PourTaskTarget 或独立 Action 的接口承载）暂时搁置；选型 7（锅具 TCP 局部增量轨迹回放）下一步单独讨论。
- 已新增 `DEC-010` 记录上述确认；产品代码仍未修改。

## 选型 7 初步证据（2026-07-29）
- 阅读 `robot_motion_executor` 的 `PathRecordSkill`、`xcore_path_client.record_path_on_robot()` 和 `smoothie_path_record_replay.replay_path()`。
- 当前能力是：通过 xCore 直连控制器录制命名路径，并调用控制器 `replayPath(name, rate)` 回放；路径保存于控制器内部。
- 当前代码没有暴露路径点、`frame_id`、锅具 TCP 引用、相对/绝对坐标语义或运行时 TCP 转换，因此不能把现有 `RECORD_PATH` 直接认定为锅具 TCP 局部增量轨迹契约。
- 选型 7 暂不下最终用户批准结论；候选方向收敛为：复用法兰增量轨迹文件 + 适配器，或在控制器能力确认后复用原生回放。
- 当前建议先做最小 replay spike：在两个不同起始位姿下验证刚体连接锅具能否复现同一法兰示教动作，并验证锅具 TCP 起始位姿对齐、`robot_driver` 占用、取消和执行反馈。

## 选型 7 现成方案评估（2026-07-29）
- 已阅读用户提供的 `flange_motion_editor`：`capture_flange_motion.py`、`process_flange_motion.py`、`spatial_replay.py`、`replay_flange_motion.py`、`sdk_robot.py` 及 README。
- 源码事实：轨迹采集和输出使用 `coordinate_system: flangeInBase`；处理阶段计算 `Delta_i = inverse(T0) @ Ti`；回放阶段使用 `T_current @ Delta_i` 生成绝对法兰路径，再调用 `move_rt_cartesian_path()`。
- 结论：可复用其显式 YAML、空间重采样、SE(3) 增量数学和离线处理流程；不能直接复用其“法兰坐标 + 直连 SDK”运行入口。
- 关键修正：V1 可以直接使用 `flangeInBase` 采集得到的法兰局部增量。因为抓取后锅具与法兰是刚体连接，只要回放时把法兰起始位姿对齐到期望锅具 TCP 起始位姿，锅具就会随法兰完成同一刚体轨迹。
- 锅具 TCP 的职责是参与起始位姿反解：由期望的 `T_C_P_start` 和固定 `T_F_P` 得到 `T_C_F_start = T_C_P_start @ T_P_F`；不需要对每个 `Delta_F_i` 做 TCP 共轭转换。
- 正式接入位置建议在 `robot_motion_executor` 的 Skill/Adapter 边界，通过现有 RobotDriver 链路执行；不要让 TaskPlanner 直接启动外部回放脚本。
- 已新增 `RES-003` 和 `DEC-011`。`DEC-011` 是待用户批准的技术选型提案，产品代码仍未修改。
- 下一步：最小 replay Spike，验证两个起始位姿/两个 TCP 参数下的起始对齐和锅具刚体轨迹一致性，以及 RPY、单位、矩阵方向、driver 占用、取消和反馈。


---

- 当前阶段：solution-research（技术选型）
- 当前目标：`GOAL-001`；TASK-007 已完成，TASK-008 进行中
- 本轮完成：
  - 用户回顾今日任务记录，确认 V1/V2 两版本路线
  - 完成 V1 完整流程状态机详细澄清（handoff → ... → home 共 12 个步骤）
  - 确认倾倒点公式 `pour_point_C = plate_center_C + pour_offset_C`（中心坐标系 C 下 xyz 三向可调偏置）
  - 确认抓取偏置沿锅把 PCA 主轴方向、定义在中心坐标系 C 下
  - 确认抓取 TCP/锅具 TCP 位姿参数化，代码已有 toolset.end/ref 入口
  - 确认倾倒采用锅具 TCP 局部坐标系录制增量回放
  - 确认 V1 不加落料验收、异常处理和抓取确认，只打通动作流程
  - 确认放回/张手/home 后续确定，具体参数数值不阻塞流程骨架
  - 用户批量回答了全部开放问题，所有阻塞项解除
  - 用户同意进入技术选型阶段
- 当前决策状态：DEC-003/005/006/007 active；DEC-008 proposed 待用户确认
- 产品代码仍未修改
- 待用户批准：DEC-008 技术承载方案、ARCH-001 架构草案

---

# Current Session

- Project Log 已从旧 v0.2 结构迁移到运行时 v0.4 模板。
- 旧日志原样保存在 `.project-log-legacy-20260728/`，不得删除。
- 当前目标：`GOAL-001`；当前阶段：`business-clarification`；下一步：完成 V1 业务逻辑与两个仓库代码行为的双向澄清。
- 2026-07-28 已完成 Project Log v0.2 → 运行时 v0.4 迁移；新结构校验通过。
- Loop 状态：`active`，原生 Goal 仍未绑定；这不影响项目日志迁移结果。
- 2026-07-28 用户已确认 V1 只打通动作流程，不加入落料验收、异常检查和异常处理；抓取偏置沿锅把 PCA 主轴，抓取 TCP/锅具 TCP 位姿参数化，倾倒动作使用锅具 TCP 坐标系录制回放，放回/home 后续确定。
- 当前阶段已从 `business-clarification` 切换到 `solution-research`，下一步执行 `TASK-008` 技术选型；产品代码仍未修改。

## Legacy Session Snapshot

# Current Session

- 当前阶段：business-clarification（两个仓库第一轮代码接管完成，进入业务/技术逻辑对齐）
- 当前目标：老板电器炒菜机器人「倾倒入盘（大）- 炒菜出锅呈盘」技术方案调研
- 当前任务：澄清 V1 业务原子、代码承载边界和技术未知项；技术选型批准前不修改产品代码
- 新增业务口径：锅把抓取属于 V1 基础流程，当前 V1 初版不执行抓取确认，先跑通无确认基础链路
- 用户提出采用“先跑通初级版本、再逐步迭代”，并提交 `/home/tbl/Project/boss_electrics/方案1.md`
- 用户要求基于原文生成仅做格式整理的 `/home/tbl/Project/boss_electrics/方案1整理.md`
- 用户要求制定第一版锅把特征检测特征名单及检测方案
- 用户补充：第一版抓取目标点暂时定义为锅把中心点；特征需压缩，主要供感知组训练模型；核心信息为锅把中心、抓取点和主轴方向
- 用户进一步补充：PCB 主轴方向以附带图片方向为准；抓取点偏移量定义为沿 PCB 主轴方向的偏移
- 用户于 2026-07-28 确认两版本路线：V1 不考虑右手锅铲辅助，先完成左手抓锅到倾倒入盘的完整闭环；V2 再迭代右手锅铲辅助
- 用户于 2026-07-28 要求先理解 `kitchen_robot_home` 主仓库和 `robot_motion_executor` 执行仓库，再开展业务逻辑澄清、技术选型和架构讲解，之后才开始写代码
- 用户于 2026-07-28 补充：两个仓库由团队共同开发；感知组提供锅把模型和感知信息，本子任务只订阅；底盘组支持移动；左臂抓取 TCP、锅具 TCP、抓取偏置、姿态保持和录制增量倾倒动作纳入 V1 业务澄清

## 已确认事实
- 项目：老板电器智能厨房机器人，双臂移动机器人 + 智能厨电协同
- 四个场景：蓑衣黄瓜、芦笋虾仁、洗碗、清洁台面
- 用户（陶柏霖）负责 skill 3.3：倾倒入盘（大）— 炒菜出锅呈盘
- 涉及设备：自动翻炒锅 KP200、锅盖、餐盘、电磁灶
- 机器人位于台面前方，台面高约 900mm、深度约 700mm
- 系统架构：IoT 平台为中心，控制页面、机器人、AI 调料机、烟机控制板、洗碗机接入
- 三级任务结构：场景任务 → 环节任务 → 原子动作
- 设备清单（KP200、7W001、U2P-i1 pro、DEV05、KD361、WB758）
- 项目阶段：原型验证和演示阶段
- V1 当前流程：上游任务移交 → 可选场景检查 → 订阅锅把感知 → 计算抓取 TCP 目标 → 左手闭合 → 提锅到准备倾倒位 → 底盘移动并保持左臂姿态 → 定位餐盘/计算目标 → 锅具 TCP 转换平移 → 播放增量倾倒动作 → 放回桌面 → 张手 → home
- 当前未决：两个 TCP 契约、中心坐标系的工程定义、抓取偏置、录制动作、放回/home 和基础流程异常恢复；抓取确认延期到后续迭代

## 机器人参数
- 类型：双臂机器人，每臂 7-DOF，末端灵巧手
- 含义：可做精细抓取、力控、双臂协同；冗余自由度利于避障和轨迹平滑
- 锅具：典型长把锅（手柄长，锅体在前），抓取点可远离高温区

## 调研完成情况
- 检索了 5 篇相关学术论文（arXiv:2310.18473, 2407.01755, 2408.01366, 2503.17501, 2505.11680）
- 查阅了 MoveIt 2 / ROS 2 Control 框架能力文档
- 对比了 5 种倾倒控制策略
- 推荐方案已写入 `.project-log/research/solution-research.yaml`
- 2026-07-22 深度调研补充了一手 ArXiv API、MoveIt 2 和 ros2_control 官方资料
- 已识别并修正：液体 ±10ml 不能外推到固体装盘；MoveIt 规划/伺服与底层力控职责需分层
- 已将“锅把抓取确认”独立为实验性业务原子 `atom-pan-handle-grasp-confirmation`
- 已新增 `task-pan-handle-grasp-spike`，优先验证抓取可靠性再验证倾倒控制
- 已审阅并确认方案1：V1 采用锅把朝左的固定场景左手单臂无确认闭环，包含感知结果订阅、餐盘定位、倾倒、轻微抖动、放回和安全接管；后续再评估抓取确认和 V2 右手锅铲辅助

## 活跃决策
- 提议采纳：示教轨迹基线 + 受限重量/力矩反馈局部修正（option-f-layered-teach-plus-limited-feedback）
- 回退：带安全限幅、超时、急停和人工确认的示教回放（option-a-teach-replay）
- 先进行 `task-pan-handle-grasp-spike`，未通过前不启动倾倒反馈 Spike，也不进入全轨迹力控承诺
- `task-pouring-validation-spike` 已显式依赖 `task-pan-handle-grasp-spike`
- 已新增 `decision-mvp-plating-fixed-scene` 与 `task-mvp-plating-pipeline`
- `DEC-003` 已由 proposed/pending 更新为 active/approved；`DEC-006` 记录当前 V1 初版不执行抓取确认；`REQ-001` revision 2 和 `TASK-007` 已同步团队、感知、底盘、TCP 与录制动作边界
- `DEC-005` 已记录 V1 倾倒点公式：`pour_point_C = plate_center_C + pour_offset_C`；所有业务坐标统一使用机器人中心坐标系

## 待确认开放问题
1. KP200 锅具手柄具体尺寸、重量和抓取点（C 级）
2. 倾倒过程是否需要双臂协同（C 级）
3. 机器人关节力矩传感器数据接口和采样频率（B 级）
4. 芦笋虾仁重量范围和汤汁比例（B 级）
5. 机器人是否能暴露 effort/关节力矩或腕部 F/T state interface，以及实际更新率/延迟（B 级）
6. 固体落料完整性、卡料和盘外洒落的观测信号是什么（C 级，影响验收）
7. 灵巧手的具体型号、指尖触觉/夹持力接口和可更换锅把夹具是否允许增加（C 级）
8. KP200 锅把是否为固定规格、材质/表面摩擦和热安全区域（C 级）

## 下一步
1. 继续 `TASK-007`，逐条澄清两个 TCP、中心坐标系工程定义、抓取偏置、录制动作、放回/home 和异常回退
2. 结合 `clarification.yaml` 对齐 `TaskPlanner → ExecuteTask → MotionExecutor → RobotDriver` 的现有承载
3. 完成后进入 `TASK-008` 技术选型，用户批准前不修改两个代码仓库
4. 澄清和选型完成后，再恢复 `TASK-002` 锅把抓取 Spike 与 `TASK-004` V1 闭环实现

## 本轮工作留痕
- Context：原推荐过度依赖液体论文指标，且未清楚拆分 MoveIt 与底层力控边界
- Decision：改为分层、受限、Spike-first 的控制路线
- Action：核验 ArXiv 摘要、MoveIt Servo/Hybrid Planning、ros2_control PID/Admittance/FT 官方文档
- Observation：官方资料支持组件能力，但不提供 KP200 接口和固体落料成功保证
- Result：调研产物新增深度证据、反面证据、修正版推荐、验证 Spike 和失效条件
- New finding：锅把抓取是 V1 基础动作，但当前 V1 初版不执行 `grasp_confirmed`，先验证无确认基础链路
- New finding：V1 倾倒点使用机器人中心坐标系下的餐盘中心点加 xyz 可调偏置，业务坐标不绑定任一机械臂基坐标系
- New finding：方案1适合作为 MVP，但“视觉定位成功”和“抓取成功”必须分开；“轨迹执行完成”和“菜品完整落盘”也必须分开
- Result：新增 `方案1整理.md`，保留原方案内容，仅按路线介绍、风险点、需要确认的点、细节补充分组排版
- Result：新增 `锅把特征检测方案1.md`，定义第一版最小特征集合、抓取目标输出、安全门控、数据结构、检测流程和后续迭代边界
- Result：根据用户补充将 `锅把特征检测方案1.md` 压缩为感知组模型需求版，核心输出收敛为锅把中心、抓取点、主轴方向及最小有效性字段
- Result：增加图片方向约定、`pcb_axis` 字段和 `grasp_point = handle_center + grasp_offset * pcb_axis` 定义
- Result：完成 `kitchen_robot_home` 与 `robot_motion_executor` 第一轮静态架构接管，建立 `ScenePerception → TaskPlanner → ExecuteTask → MotionExecutor → RobotDriver` 主链事实地图
- Finding：现有代码具备通用任务/动作执行骨架，但尚未承载感知结果契约、两个 TCP、底盘保持姿态协同、V1 倾倒闭环和菜品完整落盘验收；这些不能由当前代码行为自动推导
- Finding：`PerceptionReceiver` 已能缓存最新场景并检查 `scene_valid`，`PathRecordSkill` 已能录制命名路径，但两者都还没有形成 V1 锅具 TCP 增量倾倒回放契约；当前也没有底盘-左臂保持姿态的同步接口

## 返回主线：开始技术选型（2026-07-29）
- 用户确认暂时结束 MotionExecutor 源码阅读，回到老板电器 V1 主线，准备正式进入技术选型。
- 已恢复 TASK-008、RES-002、DEC-003/005/006/007/009 及 ARCH-001 的现有上下文；本阶段仍不修改产品代码。
- 当前选型主问题拆分为：
  1. V1 业务阶段和动态 Policy 的承载方式；
  2. Planner 与 MotionExecutor 之间的数据/Action 契约；
  3. 中心坐标系、抓取 TCP、锅具 TCP 的转换归属；
  4. 底盘协同和阶段屏障接口；
  5. 锅具 TCP 局部增量轨迹的录制、存储和运行时回放；
  6. 参数配置文件和 ROS 2 参数注入方式；
  7. 现有 API、Skill、MotionPrimitive 的复用与扩展边界。
- 现有 RES-002 已给出初步推荐，但尚未逐项与用户确认；后续按“候选方案→代码证据→适用边界→推荐→需要批准的决策”推进。

## 2026-07-30 三个执行边界的源码确认

- 坐标系：Executor 内部 `Pose3D`/`CartesianWaypoint` 和 `MoveCartesian` 链路按机械臂 base frame 解释，服务没有 `frame_id`；不能把中心坐标 C 的目标直接发送。推荐由 Planner 在构造现有 `TaskTarget` 前完成 C→左臂 base B 转换。
- 控制对象：Executor 数据类本身没有声明 flange/TCP；当前可见 xCore SDK 适配层把输入按 `flangeInBase` 处理并用 toolset 做 flange-to-end 转换，但目标运行时 Driver 是外部 deb，且 `GetArmPose.srv` 注释和旁支 Driver 实现使用 TCP/end 语义，必须以锁定 deb 做黑盒确认。
- 倾倒回放：现有 `CartesianTrajectorySkill` 只支持 Planner 传入的绝对航点，现有 `PathRecordSkill` 是直连 xCore 的录制能力，不能直接作为正式回放链路。最小方案是新增执行仓库内部 Skill/Adapter，读取法兰增量轨迹，在左臂 base 下展开后复用现有 `MoveCartesian`；不修改公共消息、不绕过 RobotDriver。
- 问题 4 已确认：本子任务可以在 `robot_motion_executor` 内新增专用 Skill，使用现有扩展点完成回放；“是否允许新增 Skill”不再是阻塞项。尚需验证的是目标 Driver 的当前法兰位姿获取接口和 `flangeInBase` 语义，属于实现前技术验证，不是架构准入问题。
- 待架构组确认问题收敛为 3 项：目标 Driver 的 `/robot_driver/move_cartesian` 输入是 flange 还是 TCP、`toolset.ref` 是否自动参与坐标转换、目标 `.deb` 是否提供并正确定义 `/robot_driver/get_arm_pose`。新增 Skill 已确认可行，不再列为问题。
- 本轮没有修改产品代码；新增/修正技术记录见 `DEC-013`，`DEC-012` 已被“复用现有消息的内部法兰约定”替代。

## 2026-07-30 三个接口问题源码确认结论

通过 ShHai 完整 Driver 源码 + boss_electrics 自有 SDK 适配器的联合证据链，三个问题全部被确凿回答。

### 证据链

**Q1: `/robot_driver/move_cartesian` 输入是法兰还是 TCP？**
→ **法兰（flangeInBase）**

证据：`lbot_robot_xcore.py:355-363`：
- 从 `position/euler` 构建 `target_flan = [px,py,pz,rx,ry,rz]`
- 变量名写为 `target_flan`
- 调用 `self._flange_to_end_pose(target_flan)` 转换为 `endInRef` 后送入 SDK
- docstring：`将 flangeInBase 6D 位姿转换为 endInRef 6D 位姿`
- 下游：SDK 适配器完整输入/输出都是 flangeInBase 语义

**Q2: `toolset.ref` 在 Driver 中的真实语义和作用？**
→ **定义 SDK 中 `endInRef` 的参考坐标系原点**

证据：`luoshi_arm.py:106-130`：
- `toolset.load.mass/inertia/cog` 配置负载
- `toolset.end.trans/rpy` 定义 TCP 相对于法兰的偏移
- `toolset.ref.trans/rpy` 定义工作坐标系原点
- 通过 `self._robot.setToolset(toolset, ec)` 发送到 xCore 控制器
- `lbot_robot_xcore.py:1976-1978` 的 `FlanInBaseToEndInRef` 函数需要 `base_in_world`、`toolset` 和 6D 位姿三个参数
- `_end_to_flange_pose()` 反向转换同理
- 若 `ref = [0,0,0,0,0,0]` → `endInRef = endInBase`

**Q3: `/robot_driver/get_arm_pose` 是否存在，返回法兰还是 TCP？**
→ **存在，返回法兰（flangeInBase）**

证据：
- `robot_driver_node.py:701-710`：服务回调调用 `active_robot.get_arm_pose(arm=arm)`
- `lbot_arm.py:122`：`get_arm_pose()` 调用 `self.robot.get_cartesian_pose(arm)`
- `lbot_robot_xcore.py:265-270`：`get_cartesian_pose()` 调用 `_query_cartesian_pose()`
- `_query_cartesian_pose()` in `lbot_robot_xcore.py:1954`：`self._robot.posture(self._xcore.CoordinateType.flangeInBase, ec)` → 明确返回 **flangeInBase**
- 注释虽然写`获取臂末端TCP位姿`，但实际 SDK 调用使用 `flangeInBase`
- 回调中 `response.position = position; response.orientation = orientation` 字段正是 flangeInBase 值

### 对技术选型的影响

- DEC-013 已从 proposed 升级为 active
- 所有不需要问架构组的问题不再需要列出
- 这三个问题明确后，技术选型目前剩余的不确定项是：
  1. 左臂 base B ↔ 中心坐标系 C 的变换方向确认（代码已有标定脚本，需要核实）
  2. 后续在机器人上验证时做 replay spike（DEC-011），验证不同起始位姿下的法兰增量轨迹一致性
- 新增 Skill 已确认可行，不再属于待澄清项


## 2026-07-30 toolset.end 冲突风险确认与 DEC-014

- 通过源码分析确认了 toolset.end 的完整链路：`robot_params.yaml` → `luoshi_arm.initialize()` → `setToolset(toolset, ec)` → 写入物理机器人控制器 → `_sync_toolset_from_robot()` 读回 → `_flange_to_end_pose()` 使用
- 确认若其他子任务修改 `toolset.end` 为非 identity 值，会影响本子任务的所有 `_flange_to_end_pose/_end_to_flange_pose` 转换，因为 driver 的 flange→end 转换会自动生效
- 确认解决方案：`toolset.end` 保持 identity，本子任务的两个 TCP 参数（tcp_grasp、tcp_pan）定义在 `pan_pour_params.yaml` 中，在 Planner 层完成 TCP→法兰反解后下发法兰目标
- 当前按单人任务模式推进，团队协作时的配置冲突问题暂不处理
- 已新增 `DEC-014`，用户 approval 标记为 approved
- 产品代码仍未修改

## 2026-07-30 技术选型完成，用户确认 DEC-013/DEC-011

- 用户正式确认 DEC-013（复用 ExecuteTask，内部法兰约定）和 DEC-011（选型七法兰增量轨迹适配复用路线）
- 至此所有 12 个决策全部确认，技术选型阶段 **solution-research 完成**
- 用户要求：技术参数留空占位，先不开始写代码
- 下一阶段：engineering-landing（工程实施）
- 产品代码仍未修改

## 2026-07-30 技术选型完成后的两个待确认问题

- **OQ-008：倾倒回放 PlanType 复用**
  方案：复用 PLAN_CARTESIAN_TRAJECTORY，在 PlannedStep 中新增可选 trajectory_id 字段，builder 检测到后加载增量文件做 T_current @ Delta_i 展开。不改枚举、不改 Action 消息。等待用户确认。

- **OQ-009：底盘移动后的等待策略**
  方案：PanPourPolicy 在 hold_wait 阶段先固定等待 N 个 tick，之后才开始检查餐盘。设置 _MAX_HOLD_CYCLES 超时保护。等待用户确认 N/MAX 初始值。

记录位置：.project-log/business-logic/open-questions.yaml（OQ-008、OQ-009）

## 2026-07-30 TASK-010 已实现并验证

- 已在 `kitchen_robot_home/src/dexbot_task_planner/` 实现 Planner 私有调度结果：`PolicyDecision(EXECUTE | WAIT | COMPLETE)`。
- `TaskPlannerNode._on_tick()` 现在只在 `COMPLETE` 时置 `SUCCESS` 并清理 `_active_task_id`；`WAIT` 仅更新 `current_phase`、保留 Policy/任务上下文/IDLE 状态且不发送 `ExecuteTask`。
- 旧 Policy 无需迁移：`PlannedStep`/`BimanualStep` 自动适配为 `EXECUTE`，旧 `None` 自动适配为 `COMPLETE`。未知返回值进入 Planner `ERROR`，不会静默完成。
- 测试：12 项定向 pytest 通过；`dexbot_interfaces` 与 `dexbot_task_planner` 构建通过；新增文件及 BasePolicy 的 99 列 lint 通过。
- 验证限制：未启动真实 ROS 节点、MotionExecutor 或硬件；工作区包级 lint 受既有 3,173 条 flake8 问题和 SDK 文档问题影响失败，已记录为基线限制。
- 下一步：`TASK-011`（独立 pan_pour 参数模板 + 纯 SE(3) 计算模块）。保持 `toolset.end` identity，不修改全局 `robot_params.yaml` 或公共 ROS 接口。

## 当前会话（2026-08-03 手眼标定使用分析）

- 用户要求暂停代码开发，先检查现有手眼标定代码的使用方式。
- 已核对主仓库标定启动文件与 715 参考仓库标定实现。当前流程为固定相机、末端刚性安装 ArUco 标记，标定节点自动移动机械臂并采集法兰位姿与标记相对相机位姿，计算 `T_base_cam`。
- 已确认入口服务为 `/calibration/start_calibration`，进度通过 `/calibration/status` 发布；结果 YAML 同时保存 `T_base_cam`、`T_tcp_marker`、样本数和 RMSE。
- 已确认运行前必须核对 ArUco 板边长/字典，以及主仓库 `calibration.launch.py` 中相机 `camera1` namespace 与 ArUco 硬编码 `/camera/color/*` 话题的匹配关系。
- 未启动真机、未修改产品代码；下一步向用户提供单臂标定操作手册，待用户确认标定板参数和真机条件后再执行。

## 当前会话（2026-08-03 临时轨迹 ROS 链路确认）

- 用户确认不再采用 Policy 直接调用独立 xCore 脚本，而是将录制/回放能力接回现有 Planner → ExecuteTask → MotionExecutor 架构。
- 录制复用现有 `path_record` / `PathRecordSkill`；回放新增 `path_replay` / `PathReplaySkill`，由 Skill 最终调用控制器 `replayPath()`。
- 轨迹名称继续使用 `TaskTarget.object_id`，不修改公共 Action/Message；正式 `PanPourPolicy` 与临时示教 Policy 保持隔离。
- 决策：`DEC-018` approved。当前尚未写实现代码，也未进行真机验证。

## 当前会话（2026-08-03 左臂调试参数确认）

- 用户确认当前左臂调试控制器 IP 为 `192.168.2.159`。
- 用户进一步确认右臂控制器 IP 为 `192.168.2.160`。
- 已同步修改共享 `robot_params.yaml`、MotionExecutor 默认参数和 `path_record.py` 启动/回放示例：左臂 `192.168.2.159`，右臂 `192.168.2.160`。
- 已通过 YAML 解析校验；尚未连接真机验证网络可达性或启动 ROS 节点。

## 当前会话（2026-08-03 最小拖动录制/回放 ROS 链路实现）

- 用户要求先在现有架构中跑通左臂最小拖动录制/回放，不接入正式 `PanPourPolicy`、感知或底盘。
- 已实现 `path_replay`：`ExecuteTask(task_type=path_replay)` → `PathReplaySkill` → `REPLAY_RECORDED_PATH` → `xcore_path_client.replay_path_on_robot()` → xCore `replayPath()`/`moveStart()`。
- 录制继续复用已有 `path_record`：`ExecuteTask(task_type=path_record)` → `PathRecordSkill` → `RECORD_PATH` → `startRecordPath()`/`stopRecordPath()`/`saveRecordPath()`。
- 两条路径均使用左臂 `192.168.2.159`；控制器内部以 `TaskTarget.object_id` 作为路径名保存/查找。
- 验证：`colcon build --packages-select dexbot_motion_executor --symlink-install` 通过；禁用不兼容的用户级 pytest 插件后，`test_path_replay.py` 4 项通过。常规 `colcon test` 被系统 pytest 与用户级 anyio 插件版本冲突阻断，属于环境限制。
- 真机验证前置条件：本轮 `PathRecordSkill`/`PathReplaySkill` 会直连 xCore，必须不启动 `robot_driver`，避免对同一左臂建立竞争控制连接；Action 层只启动 `motion_executor_node` 即可。
- 下一步：真机按最小单条路径完成录制、控制器路径列表确认、低速回放和急停可达性验证；成功后再录制“拿锅/端锅/倾倒/放锅”四段资产。

## 当前会话（2026-08-03 xCore SDK 路径定位修复）

- 真机首次调用 `path_record` 失败，错误为 `xCore SDK example directory not found`；失败发生在建立 xCore 连接前，未向机械臂下发运动指令。
- 根因：`xcore_path_client.py` 仅识别旧布局 `src/dexbot_robot_driver/dexbot_robot_driver/sdk/...`，实际工作区 SDK 位于 `kitchen_robot_home/src/sdk/xcoresdk_python-v0.5.1.ar_12/example`。
- 已让 SDK 定位同时支持旧布局和当前 `src/sdk/...` 布局；在当前工作区解析结果为实际 SDK 目录。
- 验证：执行器包构建通过；`test_path_replay.py` 5 项通过。需要重启 `motion_executor_node` 载入修复后再重试同一条 `path_record` Action。

## 当前会话（2026-08-03 左臂最小路径录制真机验证）

- 已在真机经 `ExecuteTask(task_type=path_record)` 完成左臂最小拖动路径录制，`task_id=teach_smoke_001`，路径名 `pan_pour_smoke_001`。
- 真机证据：成功建立 xCore 连接并匹配 `xMateErProRobot`；`startRecordPath`、拖动按键 `key5` 按下/释放、`stopRecordPath`、`saveRecordPath` 均返回 `ec=0`。
- `queryPathLists` 已返回 `pan_pour_smoke_001`，确认路径已保存于左臂控制器 `192.168.2.159`。
- Action 结果为 `success=true`、状态 `SUCCEEDED`。结果中的 `dual_arm_result.left_success/right_success=false` 对本次单臂 `execution_mode=0` 不适用，不表示录制失败。
- 下一步：清空工作空间、确认急停可达后，用 `task_type=path_replay` 回放这条短路径，验证回放链路。

## 当前会话（2026-08-03 replayPath 是否自动回起点的代码核查）

- 已核查当前 `PathReplaySkill`、`xcore_path_client.py`、SDK 官方 `drag_example.py` 以及 `replayPath()` 类型声明。
- 确认应用侧调用固定为：`replayPath(name, rate)` → `moveStart()`；代码没有读取录制路径起点，也没有在回放前发送关节/笛卡尔移动到起点的命令。
- SDK 类型声明只说明“路径回放，调用后需 `moveStart()` 才开始运动”，没有说明控制器是否会从当前位置自动过渡到录制起点。
- 结论：自动回起点属于控制器固件黑盒行为，当前源码无法确认，也不能作为临时路径流程的安全前提。必须在空载、短路径、急停可达条件下做一次真机观察验证。

## 当前会话（2026-08-03 replayPath 起点与速率真机结论）

- 用户已在真机验证：控制器执行 `replayPath()` 时，会先回到录制轨迹起点，再开始记录的轨迹回放。该行为现标记为“当前控制器/固件上的真机观察”，不是 SDK 源码保证。
- SDK 类型声明确认 `replayPath(name, rate)` 的 `rate` 为回放速率：`1.0` 是原始录制速度，必须大于 `0` 且小于 `3.0`；速率大于 `1.0` 可能产生驱动器无法跟随错误。
- 已新增 MotionExecutor 参数 `path_replay.rate`（默认 `1.0`）和 `path_replay.wait_timeout_sec`（默认 `120.0`），并在创建 `PathReplaySkill` 时传入。无需修改 `ExecuteTask`/`TaskTarget`。
- 验证：执行器包重新构建通过；`test_path_replay.py` 6 项通过。真机调试推荐先以 `path_replay.rate:=0.5` 启动节点。

## 当前会话（2026-08-03 正规 launch 启动与灵巧手服务阻塞）

- 正规 `dexrob_full.launch.py` 启动后，`motion_executor_node` 初始化成功，但 `task_planner_node` 因当前用户 Python 环境的 NumPy `2.2.6` 与已安装 `cv2` 的 NumPy 1.x ABI 不兼容，在 `import cv2` 处退出；这是独立的 Planner 环境阻塞。
- `robot_driver_node` 因工作空间根目录缺少 `.localconfig` 退出。已从已安装 Driver 源码确认其读取 `lbot_sdk_path` 与 `xcoresdk_sdk_path`；当前工作区存在对应 SDK 目录，但尚未写入本机配置。
- `gripper_action` 测试失败的直接原因不是动作名、手指参数或 `arm_type`，而是 `robot_driver_node` 已退出，故 `/robot_driver/gripper_action` 服务不存在；MotionExecutor 等待约 2 秒后报告 `GripperAction service not available`。
- 已确认 xCore 配置候选路径：`/home/tbl/Project/boss_electrics/kitchen_robot_home/src/sdk/xcoresdk_python-v0.5.1.ar_12/Release/linux/xCoreSDK_python`；Lbot Python SDK 候选路径为 `.../src/sdk/arm_api/Python`，写入 `.localconfig` 前仍需现场确认导入结果。
- 未修改 `.localconfig`、系统 Python 环境或 `/opt/ros` 私有 deb 文件；下一步先完成 SDK 配置并用正规 launch 验证 Driver 服务，再单独处理 NumPy/OpenCV ABI 问题。

## 当前会话（2026-08-03 启动配置修复结果）

- 已创建本机私有配置 `kitchen_robot_home/.localconfig`，配置 `lbot_sdk_path`、`xcoresdk_sdk_path` 和 `hand_config_path`；该文件被 `.gitignore` 忽略，不进入仓库提交。
- 已修正 `xcoresdk_sdk_path` 为 SDK Python 模块的父目录 `.../Release/linux`，Driver 可成功导入 `xCoreSDK_python`，并匹配 `xMateErProRobot`。
- 已在正规 `dexrob_full.launch.py` 中为 `task_planner_node` 设置 `PYTHONNOUSERSITE=1`，使其使用 ROS 系统 NumPy `1.21.5` 与 OpenCV `4.5.4`，解决用户级 NumPy `2.2.6` 导致的 `_ARRAY_API` 崩溃。
- 已重新构建 `dexbot_bringup`；正规 launch 验证显示 `task_planner_node`、`motion_executor_node` 均保持运行，左右机械臂控制器 `192.168.2.159`、`192.168.2.160` 均成功连接并完成初始化。
- 当前剩余阻塞不是软件 SDK：左手配置的 `can1` 接口不存在，右手配置的 `can0` 存在但为 `DOWN/STOPPED`。因此灵巧手配置文件已加载，但 CAN 手部控制尚未具备可执行条件；需要现场确认 CAN 适配器、接口命名与启动状态后再测试 `gripper_action` 或 `hand/set_angles`。

## 当前会话（2026-08-03 CAN 左右手映射调整）

- 用户确认当前物理映射为：`can0` 对应左手，`can1` 对应右手。
- 已修改 `kitchen_robot_home/src/dexbot_bringup/config/robot_driver/robot_params.yaml`：左臂 `can_channel=can0`，右臂 `can_channel=can1`。
- 已重新构建 `dexbot_bringup`，并确认安装目录中的 `robot_params.yaml` 已同步该映射；左臂 IP 仍为 `192.168.2.159`，右臂 IP 仍为 `192.168.2.160`。
- 该修改只改变灵巧手 CAN 通道映射，不改变机械臂控制器 IP 映射。

## 当前会话（2026-08-03 灵巧手 SDK 配置修复）

- `can0` 已现场确认正常：接口 `UP`、`ERROR-ACTIVE`、bitrate `1000000`，因此本次 `hand对象为None` 的直接原因不是 CAN 状态。
- 新日志显示 `HandInterface._import_hand_class()` 读取 `linkerbot_sdk_path=None`；随后 `stat` 收到 `None`，导致本地 Linkerbot SDK 导入失败，O6 灵巧手对象保持 `None`。
- 已在本机私有 `.localconfig` 中增加：`linkerbot_sdk_path=/home/tbl/Project/boss_electrics/kitchen_robot_home/src/sdk/linkerbot-python-sdk/src`。
- 已验证该路径可导入 `linkerbot.O6`，并可构造 `O6(side='left', interface_name='can0', interface_type='socketcan')`；用户必须重启正规 Launch，使运行中的 Driver 重新加载该配置。
- 右手 `can1` 当前仍不存在，但本轮仅测试左手 `can0`，不阻塞左手 SDK 初始化。

## 当前会话（2026-08-03 灵巧手关节角度与力矩测试完成）

- 左手测试使用 `arm=0`，通过正规 launch 启动的 `/robot_driver/hand/*` 服务完成验证。
- `SetHandAngles` 角度控制测试成功；接口接受 6 个关节角度，顺序为 `thumb_flex, thumb_abd, index, middle, ring, pinky`，取值范围为 `0-100`。
- `GetHandAngles` 读取测试成功，确认角度控制链路可用。
- `SetHandTorques` 低力矩上限测试成功；接口接受 6 个关节力矩上限，范围为 `0-100`。
- `GetHandTorques` 读取测试成功，确认力矩配置链路可用。
- 当前已验证链路：ROS 2 Service → `robot_driver_node` → `O6Hand` → Linkerbot SDK → SocketCAN `can0` → 左侧 O6 灵巧手。
- 灵巧手测试阶段完成；右手 `can1` 仍未接入，不属于本轮左手验证范围。

## 当前会话（2026-08-03 完整示教流程实施目标）

- 用户确认下一阶段目标：采集完整流程所需的左臂轨迹，并实现一个独立复合 Skill，将机械臂轨迹回放与灵巧手动作串联。
- 业务流程固定为：拿锅（左臂移动到抓取位置）→ 左手闭合抓锅 → 端锅到准备位置 → 倾倒 → 放锅 → 左手张开 → 机械臂回 home。
- 当前示教资产建议至少包含 4 段左臂路径：`pick_approach`、`carry_to_pour`、`pour`、`place`；若现有放锅轨迹不包含回 home，则增加独立 `return_home` 路径。
- 灵巧手不录制为机械臂路径的一部分，使用已验证的 `gripper_action` 或 `set_angles` 服务作为复合 Skill 中的独立 Primitive：抓取点执行闭合，放锅后执行张开。
- 复合 Skill 的目标链路：`PathReplaySkill` 回放机械臂路径 + `GripperAction`/手部角度控制 + 顺序等待前一步结果；正式感知/底盘路径与本临时示教路径隔离。
- 真机操作约束：路径录制/回放实现会直连 xCore，必须确认 `robot_driver` 不与同一左臂控制器并发占用；录制和回放前要按当前实现确认控制连接独占方式，不能仅依据 Action 成功返回判定硬件资产可用。

## 当前会话（2026-08-03 示教复合流程目标确认）

- 用户确认本阶段目标先记录，不立即继续录制或编写复合 Skill，后续转入其他事项。
- 已确认目标仍为：采集完整左臂示教路径，并实现独立测试 Skill，按固定顺序串联机械臂路径回放与灵巧手动作。
- 目标路径资产：`pan_pick_approach_001`、`pan_carry_to_pour_001`、`pan_pour_001`、`pan_place_001`、`pan_home_001`。
- 目标执行顺序：回放抓取接近路径 → 灵巧手抓握 → 回放端锅路径 → 回放倾倒路径 → 回放放置路径 → 灵巧手张开 → 回放 Home 路径。
- 本目标当前状态为 `planned / paused`，尚未开始新增轨迹录制或复合 Skill 实现。

## 当前会话（2026-08-04 实机录制前置检查）

- 今日目标：实机录制左臂轨迹和灵巧手动作/点位，整理为独立复合 Skill，并通过现有 Planner → ExecuteTask → MotionExecutor → RobotDriver 链路运行。
- 前置检查结果：系统当前不存在 `can0` 和 `can1`，`lsusb` 未发现 USB-CAN 适配器，`peak_usb` 模块虽已加载但未绑定设备。
- 网络检查结果：本机 `eno1=192.168.2.100/24`，但 `192.168.2.159` 和 `192.168.2.160` 均不可达，邻居解析分别为 `INCOMPLETE/FAILED`。
- ROS 检查结果：残留的 `dexrob_full.launch.py` 进程已运行约 18 小时；`motion_executor_node` 仍提供 Action Server，但 `robot_driver_node` 进程不在当前 ROS 图中，不能作为有效硬件控制链路使用。
- 结论：当前不能安全开始实机录制；先恢复 USB-CAN 设备和机械臂网络连接，再停止残留 launch 并按正规 launch 重启，确认 Driver、Executor 和 CAN 均正常后继续。
- 当前失败归因：`environment`/`hardware connectivity`，不是轨迹录制代码或 Skill 代码缺陷。

## 当前会话（2026-08-05 相机调试进度与环境问题说明）

- 用户已连接 Orbbec 相机，要求先把相机调试进度和环境问题整理清楚，并记录工作进度；本轮未继续实施大的环境改造。
- 设备识别：系统识别到 `Orbbec Gemini 336L`，序列号 `CPCAC53000FP`，USB3.2，8 个 `/dev/video*` 节点。
- Orbbec SDK：`pyorbbecsdk2==2.0.18` 可用；原始 SDK 采集测试通过，彩色 `1280x720@15` MJPG，深度 Y16。
- ROS 相机驱动：已用隔离环境启动成功，发布 `/camera1/color/image_raw`、`/camera1/depth/image_raw`、`/camera1/color/camera_info`；当前设备内参实测值约为 `fx≈609.0`、`fy≈608.9`、`cx≈642.4`、`cy≈354.6`。
- 已修改 `kitchen_robot_home/src/dexbot_bringup/config/cameras/camera1_params.yaml`：从 RealSense D435 切到 Orbbec `gemini335l`，关闭 `allow_synthetic_fallback`，`camera_info_source=device`，写入当前设备内参占位值。
- 该配置改动是针对当前实机连接的正式配置修改，不是临时测试脚本；但它会影响默认 `camera1` 配置，后续上线或标定前需要确认是否保留。
- 环境问题大白话：
  - 这台机器上有两套 Python 包环境。ROS 依赖系统环境里比较旧的 NumPy；用户目录里还装了另一个 Python 项目用的 NumPy `2.2.6`。
  - ROS 默认会先加载用户目录里的新 NumPy，和 ROS OpenCV 不匹配，导致相机/OpenCV 启动失败。
  - 临时验证通过 `PYTHONNOUSERSITE=1` 跳过用户目录包，并把 Orbbec SDK 隔离目录加进 `PYTHONPATH`，相机节点才能正常跑。
  - 最工程化的方向是把 Orbbec SDK 放进项目可控依赖路径，并把 ROS launch 的环境设置固定好，避免这台机器的用户目录包影响机器人程序。
- 当前没有实施这个大改造。下一步先由用户确认是否要实施仓库内 SDK 依赖与 launch 环境隔离，再复核 `camera1` 默认配置是否以当前 Orbbec Gemini 336L 为准。

## 当前会话（2026-08-05 本地 Orbbec 调试方案落地）

- 用户明确不要因为个人环境问题把问题上升为团队仓库问题；选择恢复团队默认 RealSense 配置，Orbbec 只在本机调试。
- 已恢复 `kitchen_robot_home/src/dexbot_bringup/config/cameras/camera1_params.yaml` 为团队 HEAD 默认 RealSense D435 配置，不保留 Orbbec 改动。
- 已建立本机专用启动脚本：`/home/tbl/.local/bin/launch_orbbec_camera.sh`，不在团队仓库内。
- 已建立本机专用参数：`/home/tbl/.local/share/boss_electrics/camera1_orbbec_local.yaml`，固定 `gemini335l`、`1280x720@15`、`camera_info_source=device` 和当前设备实测内参。
- 本机验证：脚本能启动真实设备，日志显示 `Camera backend: real device (Orbbec Gemini 335L)`，发布 `/camera/color/image_raw`、`/camera/depth/image_raw`、`/camera/color/camera_info`，内参 `fx=609.0, fy=608.9, cx=642.4, cy=354.6`。
- 处理原则记录：当前机器用户目录 NumPy 2.2.6 与 ROS NumPy 1.21.5 冲突是本机个人环境问题；以后本机相机调试统一使用脚本，团队默认配置和提交不受影响。
- 注意：相机 driver 当前实际发布话题是 `/camera/...`，不是 `/camera1/...`；后续如需和现有 `/camera1` namespace 对接，需要在本机脚本或调用方补 topic remap。
- 未修改团队仓库中的 launch 文件，也没有提交任何本机环境依赖。

## 当前会话（2026-08-05 项目级 AGENTS.md 建立）

- 用户要求根据 `kitchen_robot_home/DEVELOPER_GUIDE.md`、`README.md` 和 `SKILL.md`，为 `/home/tbl/Project/boss_electrics` 建立项目级 `AGENTS.md`。
- 已新增 `/home/tbl/Project/boss_electrics/AGENTS.md`，内容固定：两个独立 Git 仓库边界、`.project-log` 留痕要求、`.deb` 子模块黑盒只读边界、当前项目 ROS source 规则、禁止加载无关旧备份工作空间、相机配置与标定流程、任务规划 Policy 规范、配置/接口原则、验证纪律和 Git 修改规则。
- 特别记录：`dexbot_camera_driver` 由 `ros-humble-dexbot-camera-driver` `.deb` 提供，安装产物位于 `/opt/ros/humble`；主线只维护 `dexbot_bringup` 配置，不直接修改驱动实现。
- 特别记录：当前机器个人 Python/NumPy/SDK 环境问题不得未经用户确认写入团队仓库；本项目不得 source 其他项目或“复件/备份”工作空间。
- 验证：`AGENTS.md` 已写入项目根目录；两个子仓库的 `git diff --check` 通过；未修改两个子仓库代码，已有未提交改动均保留。

## 当前会话（2026-08-05 PanPourPolicy 参数归属调整）

- 用户确认采用方案二：将老板电器 V1 `pan_pour` 任务的技术参数配置放入 `dexbot_task_planner/policy/pan_pour/`，与 `PanPourPolicy` 同目录维护，不再把任务专用参数放在 `dexbot_bringup` 的全局启动配置目录。
- 新配置文件为 `kitchen_robot_home/src/dexbot_task_planner/dexbot_task_planner/policy/pan_pour/pan_pour_params.yaml`，保持扁平 `pan_pour.*` 键结构，继续使用占位值并以 `configured: false` 禁止未经标定的实机执行。
- `PanPourPolicy` 现在默认从同目录加载配置；构造函数仍保留可选 `parameters` 参数，测试和未来受控覆盖场景不被破坏。
- `TaskPlannerNode` 不再声明、持有或通过 ROS 参数注入 `PanPourParameters`；`dexrob_full.launch.py` 不再加载旧的 `dexbot_bringup/config/pan_pour` 配置。
- 新 YAML 已加入 `dexbot_task_planner/setup.py` 的 `data_files`，安装后位于 `share/dexbot_task_planner/policy/pan_pour/pan_pour_params.yaml`；旧 bringup 配置已删除，避免产生双份事实来源。
- 验证结果：PanPour 定向测试 `17 passed`；`colcon build --symlink-install --packages-select dexbot_task_planner dexbot_bringup` 成功；launch Python 语法检查和 `git diff --check` 成功。
- 本次未修改正式 V1 的业务阶段逻辑、TCP 计算公式、RobotDriver 全局配置或硬件连接问题；`configured` 仍需在现场标定和参数确认后才可改为 `true`。

## 当前会话（2026-08-05 恢复固定工位采点示教任务）

- 用户确认恢复此前暂停的固定工位示教回放路线，继续推进 `TASK-016`，暂不切回正式感知/底盘路径。
- 已完成的基础能力：左臂普通拖动示教通过 `path_record` Action 录制；控制器内部命名路径可查询；`path_replay` Skill 已接入 `MotionExecutor`，可通过 `ExecuteTask` 调用控制器回放；左手灵巧手 `gripper_action`、关节角度和力矩控制链路此前已验证。
- 已有真机录制证据：左臂控制器 `192.168.2.159` 保存过测试路径 `pan_pour_smoke_001`，但这不是完整业务流程资产。
- 尚未完成：四段正式示教路径（拿锅移动、端锅、倾倒、放锅）的录制与逐段回放验证；独立 `TeachPanPourPolicy`；机械臂路径与灵巧手动作的完整串联；完整真机闭环证据。
- 当前固定阶段顺序已确认到：`take_move → close_gripper → carry_replay → pour_replay → put_replay`。放锅后是否立即执行 `open_gripper` 仍是唯一未冻结的业务时序问题，未在代码中擅自决定。
- 用户现已确认：`put_replay` 成功完成后立即执行 `open_gripper`，张手成功后任务才完成。
- 用户进一步确认：完整流程使用一个独立的 `TeachPanPourSkill` 承载。Skill 内部集中保存固定机械臂关节点、灵巧手关节/力矩目标和 JSON 轨迹资源；Policy 只下发阶段指令，Skill 再调用现有 Driver 接口执行。
- 资源组织进一步明确：固定点位集中放在 Skill 目录内的一个点位文件中，包含机械臂点位、灵巧手关节点位和灵巧手力矩；倾倒和放锅两段已录制轨迹文件也放在同一 Skill 目录内。Skill 根据当前阶段按需读取对应点位或轨迹文件执行。
- 因此阶段顺序调整为：`home_open → move_to_grasp_ready → close_gripper → move_to_lift → move_to_pour_ready → pour_replay → put_replay → open_gripper → return_home → complete`。
- 本方案不复用控制器命名路径 `PathReplaySkill`：倾倒和放锅直接读取 Skill 内的 JSON 关节轨迹，按文件中的点位和时间信息执行。
- 这仍然是“一个业务 Skill + 一个 Policy”，不是把所有逻辑塞进 Policy；Policy 管阶段，Skill 管动作资源和 Driver 执行。
- 已接入用户提供的示教资源到执行器仓库 `skills/teach_pan_pour/resources/`：左臂四个固定关节点位、灵巧手张开/抓锅关节与力矩、倾倒 JSON 轨迹和放锅 JSON 轨迹。
- 当前资源映射：`arm_poses_left.json` 的 `1/2/3/4` 分别对应初始准备、准备抓锅、抓锅后抬起、准备倾倒；初始回位阶段复用点位 `1`。
- 两段轨迹均确认 `arm_side=left`、7 关节、`joint_positions_rad` 弧度制；倾倒轨迹 437 点/9.158 秒，放锅轨迹 182 点/3.812 秒，时间戳单调递增。
- 新增资源文件：`hand_presets.yaml`、`resource_manifest.yaml`；`setup.py` 已配置资源随执行器 Python 包安装。
- 本轮只完成资源整理和契约校验，没有注册 `TeachPanPourSkill`、没有修改 MotionExecutor 路由，也没有进行真机执行。
- 已确认卡顿根因：现有 `MoveJoints.srv` 一次只接收一个目标点，MotionExecutor 每个点都进行一次 ROS Service 往返并等待单点动作完成；20 ms 轨迹若逐点调用必然不连续。
- GUI 已有可复用的平滑执行证据：一次性构造全部 xCore `MoveAbsJCommand`，通过 `moveAppend` 批量下发，设置中间点 blend zone，最后一点 zone 为 0，再调用 `moveStart`。
- 因此当前推荐方案是让 `robot_driver` 提供等价的批量关节轨迹接口，TeachPanPourSkill 传入整段轨迹；不推荐在 Skill 内逐点调用 `MoveJoints`。
- Skill 直接 xCore 连接虽然能复用 GUI 实现，但会绕过 Driver 并重新引入控制连接竞争，只作为临时回退，不作为正式默认实现。
- 进入 Skill 实现前仍需确认：Driver 是否已有或允许增加批量关节轨迹接口、轨迹点时间映射和停止/取消语义。
- 恢复后的精确下一步：检查现场左臂控制器、CAN 和控制连接独占条件，录制第一段正式路径 `pan_pick_approach_001`，完成低速单段回放，再继续后续三段。

## 当前会话（2026-08-05 TeachPanPourSkill 首轮代码落地）

- 已完成 `TeachPanPourPolicy` 与 `TeachPanPourSkill` 的首轮实现，阶段顺序固定为：`home_open`、`move_to_grasp_ready`、`close_gripper`、`move_to_lift`、`move_to_pour_ready`、`pour_replay`、`put_replay`、`open_gripper`、`return_home`。
- Planner 通过现有 `ExecuteTask` 和 `TaskTarget.action_name` 传递阶段，不修改公共 ROS 接口；Executor Skill 根据阶段加载本地点位、手部角度/力矩和 JSON 轨迹。
- 轨迹阶段通过短生命周期 xCore 批量执行 `MoveAbsJCommand`，中间点设置 blend zone，末点 zone=0，完成或异常均断开连接。
- 验证证据：执行器新增定向测试 5 passed，Planner 定向测试 8 passed；两个 ROS 包构建成功；两仓库 diff check 成功。
- 环境说明：系统 pytest 与用户目录 anyio 插件版本冲突，仅在测试命令中禁用 pytest 自动插件；没有修改运行环境，也没有为本任务引入 NumPy/OpenCV 隔离。
- 下一步：真机前先验证单个固定点位和单段短轨迹的 Driver→xCore→Driver 切换，再执行完整 Action；保持当前状态为 `implemented-unverified`。

## 当前会话（2026-08-05 teach_pan_pour 角度类型错误修复）

- 用户日志显示：左右机械臂、`can0`、`can1` 和双手初始化均成功；任务在 `MOVE_JOINTS` 成功后，于设置灵巧手角度时失败。
- ROS `float64[]` Python 消息不接受列表中的整数；资源 YAML 同时包含整数和小数，触发 `each value of type 'float'` 断言。
- 已在执行器消息边界将角度和力矩转换为 Python `float`，没有修改公共 ROS 接口或硬件配置。
- 代码构建和直接消息赋值验证通过；真实完整任务仍未复测，下一步是重启全部节点并重新调用 `StartTask(teach_pan_pour)`。

## 当前会话（2026-08-05 TeachPanPourSkill 真机执行成功）

- 用户现场反馈：将 `TeachPanPourSkill.point_speed` 调整为 `1.0` 并重新启动后，`teach_pan_pour` 执行成功。
- 本轮已解决并现场越过两个运行阻塞：ROS `float64[]` 角度/力矩整数类型断言，以及 `rclpy` 回调中错误使用 `asyncio.to_thread()` 导致的 `no running event loop`。
- 当前参数：固定点位 `point_speed=1.0`；本地 JSON 轨迹 `trajectory_speed=0.4`。
- 现场成功尚未形成完整逐阶段日志归档和安全验收记录；项目状态记录为已实现、现场成功但证据仍需补全，不宣布 TASK-016 正式完成。

## 当前会话（2026-08-05 倾倒轨迹 6 秒停止原因取证）

- 当前工作目标已切换为：只查明 `pour_replay` 约 6 秒停止的控制器层原因，暂不继续修改速度或阶段逻辑。
- 已确认轨迹文件为 437 点、末点时间约 9.158 秒；当前客户端将全部点构造成 `MoveAbsJCommand` 并分批追加，旧现场日志无法证明控制器实际执行到哪一个 waypoint。
- 已新增 `moveExecution` 事件 watcher、分批 `moveAppend` 接受日志、`operationState` 变化日志和停止时 `queryEventInfo` 查询。下一次真机日志必须提供 `WaypointIndex`、`Error`、`Remark` 才能区分队列入队问题、控制器主动停止和状态误判。
- 代码验证通过：执行器定向测试 2 passed、compileall 和 diff check 通过。未声称根因已解决；当前状态为 `implemented-unverified`，等待重启执行器后采集新证据。

## 当前会话（2026-08-05 倾倒重复回放根因确认）

- 用户补充现场事实：倾倒轨迹在本次截取日志之前已经完整执行过多次；随后仍重复倾倒，最后一次由用户中断。
- 已从本机 ROS 日志还原完整因果链：本次 `pour_replay` 的 437 点全部被 9 批 `moveAppend` 接受，但控制器事件在 `absj#5 / WaypointIndex=49` 停止，即全局第 300 个点；控制器回 idle，事件 `Error.ec=0`，但末点校验最大误差 `1.3251 rad`，执行器返回失败。
- Planner 收到失败后按现有 `max_retries=3` 逻辑，在约 1 秒后再次发送同一个 `step_index=5, action_name=pour_replay`；第二次停在 `absj#14 / WaypointIndex=49`，第三次仍进入同一阶段。因此重复回放来源已确认是失败重试，不是 `put_replay` 被映射成倾倒轨迹。
- 当前技术根因已收敛为：控制器对一次批量队列的有效执行上限约为 300 个 waypoint；`moveAppend` 返回成功不代表 437 个点都能执行。最小正确修复应是连续分段执行并在段间保持单一控制器连接/队列连续性；不能关闭末点验收或把前缀执行伪装成成功。
- 尚未修改代码；等待进入分段执行设计与定向测试阶段。

## 当前会话（2026-08-05 倾倒轨迹离线降采样处理）

- 已按用户确认采用离线 250 点重采样方案，保留原始 437 点轨迹作为源文件。
- 新增 `robot_motion_executor/src/dexbot_motion_executor/dexbot_motion_executor/skills/teach_pan_pour/resources/trajectories/pour/segment_001_resampled_250.json`，使用原始时间范围上的关节线性插值，首尾点和总时长保持不变。
- `resource_manifest.yaml` 已将 `pour` 映射到新文件，`put` 映射未变；新增 `robot_motion_executor/tools/resample_joint_trajectory.py` 便于重新生成。
- 离线完整性检查通过，执行器轨迹客户端测试 `2 passed`，执行器包构建、compileall 和 diff check 通过。
- 当前状态为 `implemented-unverified`：尚未真机复测；必须重启并 source 执行器安装空间，确认最终 waypoint 为 `249` 且随后进入 `put_replay`。

## 当前会话（2026-08-05 放锅轨迹队列容量检查）

- 已检查放锅轨迹 `put/segment_001.json`，共 `182` 点、时长约 `3.810766 s`。
- 由于已确认控制器有效执行上限约为 `300` waypoint，放锅轨迹不超过上限；历史日志也显示该轨迹曾完整返回 `LOCAL_JOINT_TRAJECTORY completed`。
- 未对放锅轨迹做降采样，保持原始资源；当前仅倾倒轨迹映射到 250 点离线重采样文件。

## 当前会话（2026-08-05 修复 robot_driver 启动配置发现）

- 用户从 `robot_motion_executor` 目录启动主线 launch 时，`robot_driver_node` 因按 `os.getcwd()` 查找 `.localconfig` 而读取了错误目录，日志表现为 `Lbot SDK路径 未配置`。
- 已确认主线机器私有配置 `/home/tbl/Project/boss_electrics/kitchen_robot_home/.localconfig` 存在，且包含有效的 SDK、灵巧手和 Linkerbot 路径；未复制配置文件，也未修改 `/opt/ros` 黑盒 Driver。
- 已修改 `kitchen_robot_home/src/dexbot_bringup/launch/dexrob_full.launch.py`，为 `robot_driver_node` 设置基于 `FindPackageShare('dexbot_bringup')` 反推的主线工作空间 `cwd`，使启动目录与 `ros2 launch` 的调用目录无关。
- 验证通过：主线 `dexbot_bringup` 构建成功；launch substitution 解析后的真实 `cwd` 为 `/home/tbl/Project/boss_electrics/kitchen_robot_home`；Python compileall 和 `git diff --check` 通过。
- 未启动真实 Driver 或硬件闭环；下一步需从任意目录重新启动 launch，确认日志出现实际 SDK 路径并完成 Driver 服务发现验证。

## 当前会话（2026-08-05 重新评估完整轨迹执行方案）

- 新现场日志确认：当前控制器在 `moveAppend` 队列中实际只执行约 100 个 waypoint；使用 250 点重采样轨迹仍会在 `absj#1 / WaypointIndex=49` 后回到 `idle`，末点校验失败，Planner 因此重试同一个 `pour_replay`。
- 已确认当前代码的关键问题不是 `moveAppend()` Python 调用次数，而是把所有批次在 `moveStart()` 前一次性加入控制器队列；队列容量约 100 后，后续追加虽然返回成功，但没有形成可执行的完整连续队列。
- SDK API 和官方示例表明 `moveStart()` 支持“开始或继续”运动，且 `moveAppend()` 可在运动生命周期中继续追加；因此可行方向是单连接、滑动窗口式轨迹流：先追加不超过安全窗口的点并启动，运动期间根据已执行 waypoint 持续追加下一窗口，不能等待当前窗口回 idle 后再追加。
- xCore SDK 同时提供 `RtCommandMode`、`FollowPosition_7` 和 `PyRTmotioncontrol7.setControlLoopJoi()`；当前工作空间 `lbot_robot_xcore.py` 已有条件式 `joint_follow()`，但默认关闭 `DEXBOT_XCORE_RT_FOLLOW`，且 ROS RobotDriver 当前仍使用 `NrtCommandMode`，RT 能力未形成已验证的公共执行链路。
- 方案判断：优先实现 NRT 滑动窗口追加，因为保留现有 JSON、MoveAbsJ 和控制器路径，改动边界小；RT 作为后续专门 Spike，需要确认本机 IP、控制器 RT 支持、1 ms 控制周期、异常/丢包行为和 Driver/xCore 控制权互斥。
- 当前不修改完整轨迹资源，不继续降采样；下一步应先用短测试轨迹验证“运动中追加下一窗口”是否能跨越 100 点边界，再接入 pour/put 完整资源。

## 当前会话（2026-08-05 方案 1 实现）

- 已在 `robot_motion_executor` 实现 NRT 单连接滑动窗口轨迹执行：首窗口追加后立即 `moveStart()`，根据 `moveExecution` 的 `WaypointIndex` 在运动中追加后续窗口，每次追加后调用 `moveStart()` 继续执行；不再在启动前把所有批次预加载到控制器队列。
- 每个窗口保持不超过 `batch_size=50` 点，补充阈值为窗口的一半；完整轨迹最后一个点使用 `zone=0`，中间点保留 blend zone。事件解析兼容 SDK 枚举键和普通字符串键。
- 已将 `TeachPanPourSkill` 的 `pour` 资源从 250 点降采样文件切回完整 `segment_001.json`（437 点）；`put` 继续使用完整 `segment_001.json`（182 点）。
- 软件验证：执行器定向测试 6 passed，`compileall`、`git diff --check` 和 `colcon build --symlink-install --packages-select dexbot_motion_executor` 通过。
- 未验证：真实控制器在运动中追加是否能跨过约 100 点边界，尚未宣称真机闭环完成。现场复测前必须重新 source 执行器安装空间，确认急停可达且避免 `robot_driver`/xCore 控制权竞争，并重点观察所有 `moveAppend accepted`、`moveExecution`、最终 `WaypointIndex` 和末点误差。

## 当前会话（2026-08-05 NRT 启动检查误判修复）

- 真机日志确认首窗口已正常进入 `OperationState.moving`，并持续收到 `absj#0` 的 `WaypointIndex=0..16`；失败并非控制器停止或队列边界。
- 根因是 `local_joint_trajectory_client.py` 的启动超时分支在 2 秒后无条件触发，即使 `saw_motion=True` 仍抛出“did not enter a moving state”。Executor 因此清理 watcher、断开 xCore，Planner 随后对同一个 `pour_replay` 自动重试。
- 已修复为仅在启动期限到达且从未观察到 moving 时才报启动失败；新增回归测试覆盖“超过启动窗口后仍持续 moving，再正常 idle 完成”的场景。
- 验证：7 个定向测试通过，执行器 `compileall`、`git diff --check` 和 ROS 包构建通过。下一次真机复测应确认运行日志先出现 `[0,50)`，约 `WaypointIndex=25` 前后出现 `[50,100)`；这是滑动窗口续填是否真正下发的直接证据。

## 当前会话（2026-08-05 NRT 续填重复启动修复）

- 修复后的现场日志确认滑动窗口首个关键动作已成功：在 `absj#2/WaypointIndex=25` 时，控制器接受了 `moveAppend accepted points [50, 100)`。
- 随后失败的直接原因是实现错误地对仍处于运动状态的控制器再次调用 `moveStart()`；SDK 返回 `ec=-20, message=机器人运动中`，这不是 `moveAppend` 失败，也不是轨迹文件问题。
- 已改为：只对首窗口调用 `moveStart()`；运动中的续填仅调用 `moveAppend()`，由控制器连续消费；只有确实观察到 `idle/unknown` 且仍有未追加窗口时才调用 `moveStart()` 重新启动。
- 新增回归用例验证“运动中追加两个批次但 `moveStart()` 只调用一次”。验证：8 个定向测试通过，`compileall`、`git diff --check` 和执行器 ROS 包构建通过。
- 下一次现场日志不应再出现 `moveStart failed while refilling: 机器人运动中`；应继续看到 `absj#3` 的 `WaypointIndex`，然后在其约第 25 点追加 `[100,150)`。

## 当前会话（2026-08-05 NRT 完整轨迹真机成功）

- 用户现场确认：修复后完整轨迹已成功回放，之前由 Executor 失败触发的同一 `pour_replay` 重复执行问题已消失。
- 真机证据已确认 NRT 单连接滑动窗口可以跨越控制器约 100 点的有效队列边界：运动中分批 `moveAppend()` 能被持续消费，完整轨迹资源无需再次降采样。
- 当前已知不足仅为性能/平滑性：批次交接时可感知到短暂停顿。该问题不影响当前功能成功判定，后续应单独评估窗口大小、预填充阈值和控制器队列余量，必要时再研究 RT 跟随；本轮不继续修改。
- `TASK-016` 保持 `in_progress`：完整临时轨迹链路已有用户确认的真机成功证据，但尚未形成系统化的急停、取消、控制权竞争和时序性能验收。

## 当前会话（2026-08-05 记录机械臂关节限位）

- 用户现场确认机械臂 7 个关节的角度限位，已记录到 `.project-log/docs/robot_joint_limits.md`：
  - 关节 1：`-178 ~ 178` 度
  - 关节 2：`-120 ~ 120` 度
  - 关节 3：`-178 ~ 178` 度
  - 关节 4：`-60 ~ 145` 度
  - 关节 5：`-178 ~ 178` 度
  - 关节 6：`-50 ~ 50` 度
  - 关节 7：`-50 ~ 50` 度
- 记录标注为“用户确认、SDK/硬件未交叉验证”，后续 IK 或轨迹生成使用前应先与控制器实际限位核对。

## 当前会话（2026-08-05 倾倒轨迹关节限位检查）

- 对倾倒轨迹 `pour/segment_001.json`（437 点，弧度制）计算各关节最大/最小位置（换算为角度），并与记录限位对比，结果已补充到 `.project-log/docs/robot_joint_limits.md`。
- 各关节实际范围：J1=41.90~71.52°、J2=66.96~77.47°、J3=-91.69~-68.14°、J4=23.95~109.69°、J5=81.84~147.78°、J6=-20.43~21.31°、J7=11.20~40.49°。
- 结论：全部关节均在限位内；距边界最近的关节为 J7（约 10°）、J2（约 42°）、J4（约 35°）。对比基于用户确认限位，未与 SDK/控制器实际限位交叉验证。

## 当前会话（2026-08-05 GUI 增量轨迹业务澄清启动）

- 用户确认下一阶段先在现有 GUI 集成增量法兰轨迹的录制和回放，暂不接入 `kitchen_robot_home` 或 `robot_motion_executor` 的运行代码。
- 增量录制流程：操作员按下 GUI 机械按钮开始采样，松开按钮结束采样；结束后自动执行参考工程的后处理，基于绝对法兰位姿序列计算 `Delta_i = inverse(T0) @ Ti` 并生成增量轨迹文件。
- 增量回放流程：操作员选择增量轨迹文件，系统获取当前法兰位姿，按 `T_current @ Delta_i` 展开为当前起点下的绝对法兰轨迹，再执行回放。
- 文件隔离规则已确认：增量轨迹目录名以 `delta` 开头；普通轨迹和增量轨迹文件必须写入明确类型标签，回放前必须校验，禁止类型误用。
- 已新增业务原子 `BL-TRAJECTORY-001`（增量录制）和 `BL-TRAJECTORY-002`（增量回放），并在 `clarification.yaml` 记录事实、推断、未知项和对齐结果。
- 用户已确认 `Q-016`：raw、processed、delta 三类录制产物全部保留；GUI 默认回放列表只展示 delta，raw/processed 作为诊断和重新处理产物。
- 用户已确认 `Q-017`：增量回放复用普通轨迹的停止/取消/重新发起语义；停止或取消后请求安全停止，不自动重试，重新回放由操作员显式发起。
- 用户已确认 `Q-018`：缺少类型标签的历史文件默认按普通轨迹处理；只有显式标注为 delta 且通过 schema 校验的文件才能增量回放。

## 当前会话（2026-08-05 GUI 增量轨迹业务澄清完成）

- 用户确认 `Q-019`：delta 目录以 `delta_` 开头；普通/增量文件标签分别为 `joint_absolute` / `flange_delta`；同次录制的 raw、processed、delta 使用动作名和时间戳关联，全部保留，不允许静默覆盖。
- 增量录制处理固定为 `flangeInBase`、80 Hz、异常跳变剔除、位置/姿态平滑、去重、空间弧长重采样；采样少于两点、读取异常或后处理失败时只保留 raw 和失败原因，不生成可回放 delta。
- 增量资产记录臂别、机器人型号、frame、单位、RPY 顺序、schema 版本；回放前检查臂别/schema、当前法兰位姿、展开成功和轨迹非空。当前 GUI 阶段不宣称已有 IK、关节限位或碰撞检查，且不以 TCP/工具配置版本作为兼容条件。
- 用户确认 `Q-020`：增量开始/停止录制按钮放入现有开启/关闭拖动栏目，并与普通轨迹录制按钮并列；独立增量轨迹回放区域位于普通轨迹回放区域下方。
- 澄清产物：`BL-TRAJECTORY-001`、`BL-TRAJECTORY-002`，以及 `Q-016` 至 `Q-020`；当前仅剩 GUI 按钮去抖、异常松开和状态机细节待结合现有 GUI 代码确认。后续阶段应先进行 GUI 代码接管和工程规格，不直接修改 ROS 执行代码。

## 当前会话（2026-08-06 增量倾倒回放业务逻辑确认）

- 用户确认新建独立 policy + skills，不动现有 `teach_pan_pour`；任务类型建议 `teach_pan_pour_delta`。
- 倾倒改为增量法兰轨迹回放：使用 GUI 采点文件 `候选2带增量轨迹.json`（103 点），先走到 `move_to_pour_ready` 固定点，再读当前法兰位姿、`T_current @ Delta_i` 展开、IK 求解、关节回放；控制方式为 MotionExecutor 内短生命周期 xCore SDK 直连，参照 GUI 增量回放模式。
- 放锅改为固定点 `put_fixed`：只需 7 个关节角度，无轨迹文件、无专用速度参数；用户稍后提供实际关节角，暂用现有 put 轨迹末点占位。
- 阶段序列：`home_open → move_to_grasp_ready → close_gripper → move_to_lift → move_to_pour_ready → pour_delta_replay → put_fixed → open_gripper → return_home`。
- 完整记录见 `.project-log/business-logic/pan_pour_delta_replay.md`。

## 当前会话（2026-08-06 teach_pan_pour_delta 实现）

- 已实现主线 `teach_pan_pour_delta` policy：新增 `policy/teach_pan_pour_delta/`（policy 类 + 参数 YAML + `__init__.py`），注册 `PlanType.PLAN_TEACH_PAN_POUR_DELTA`、`_initialize_policy` 路由、`valid_task_types` 和 goal builder 分支（复用 `_build_skill_goal`）；`setup.py` 增加参数资源安装。
- 阶段序列按业务逻辑：`home_open → move_to_grasp_ready → close_gripper → move_to_lift → move_to_pour_ready → pour_delta_replay → put_fixed → open_gripper → return_home`。
- 已实现执行仓库 `TeachPanPourDeltaSkill`（`skills/teach_pan_pour_delta/`）：共享现有 `teach_pan_pour` 的臂姿与灵巧手资源，`pour_delta_replay` 生成 `LOCAL_DELTA_FLANGE_REPLAY` 原语，`put_fixed` 生成固定点 `MOVE_JOINTS`（当前用现有 put 轨迹末点占位，待用户提供真实关节角）。
- 已复制增量轨迹资源 `候选2带增量轨迹.json`（103 点，GUI `dexbot_gui_flange_delta_v1` 格式）到 `skills/teach_pan_pour_delta/resources/delta_trajectories/pour_delta.json`，与源文件字节一致。
- 新增 `FlangeDeltaTrajectory.from_gui_mapping/load_gui_json` 解析 GUI 增量格式；新增 `utils/delta_flange_replay_client.py`：读当前法兰位姿 → `T_current @ Delta_i` 展开 → `model.getJointPos` 连续 IK（肘部猜测、关节限位校验、最大步长校验）→ 复用 `execute_joint_points` 滑动窗口流式回放。
- 将 `execute_local_joint_trajectory` 拆出内存点流式执行 `execute_joint_points`，行为向后兼容；`create_robot` 支持 `preferred_class` 优先匹配 `xMateErProRobot`。
- `motion_executor_node.py` 注册 `teach_pan_pour_delta` skill，并新增 `LOCAL_DELTA_FLANGE_REPLAY` 执行分支；`setup.py` 增加 delta skill 资源打包。
- 验证：主线 31 passed（2 个 flake8/pep257 为既有基线失败，扫描 SDK 示例目录）；执行器 32 passed；两包 `colcon build --symlink-install` 通过；`compileall` 与 `git diff --check` 通过。
- 状态：`implemented-unverified`。未启动真机；增量回放 IK/执行和 `put_fixed` 固定点必须真机验证，且真机期间避免 `robot_driver` 与 xCore 短连接控制权竞争。
- 下一步：用户提供 `put_fixed` 真实关节角后替换占位；真机验证前先在工程日志记录验证清单（起点一致性、IK 全解、限位、末点到位）。

## 当前会话（2026-08-06 teach_pan_pour_delta 单连接修正）

- 修正增量回放为单连接执行：`execute_local_delta_flange_replay` 用同一 xCore 连接读取法兰位姿 + IK 求解 + 流式回放，不再二次建连；`execute_joint_points` 支持传入已连接的 `robot`，由调用方负责断开，行为对现有 `execute_local_joint_trajectory` 向后兼容。
- 复验：执行器 32 passed、`colcon build`、`compileall`、`git diff --check` 通过。状态仍为 `implemented-unverified`。

## 当前会话（2026-08-06 put_fixed 固定点确认）

- 用户确认放锅固定点直接使用抓取点关节角度（`grasp_ready`，preset `2`）：`[1.0792921044414698, 1.393539653590585, -0.9569674430410083, 0.8003420124854317, 1.133102233004513, -0.17046840874375402, 0.2663961369986807]`。
- `put_fixed` 实现改为运行时复用 `grasp_ready` 位姿（不再用 put 轨迹末点占位、不在清单中复制数值），避免改抓取点后放锅点漂移；测试断言两者一致。
- 已更新 `.project-log/business-logic/pan_pour_delta_replay.md`；执行器 8 个定向测试、compileall、diff check 通过，包重新构建通过。

## 当前会话（2026-08-06 teach_pan_pour_delta 真机增量倾倒回放验证成功）

- 用户现场确认 `teach_pan_pour_delta` 全流程真机验证成功：`move_to_pour_ready → pour_delta_replay → put_fixed → open_gripper → return_home` 完整执行，增量倾倒回放不再退段重试。
- 增量回放链路（单 xCore 连接：读当前法兰位姿 → `T_current @ Delta_i` 展开 → IK 求解 → 滑动窗口关节流式回放）在目标左臂控制器（`192.168.2.159`，`xMateErProRobot`）上通过，IK 全解、未触关节限位、末点到位。
- `put_fixed` 复用 `grasp_ready` 抓取点关节角，固定点放锅动作真机通过；现有 `teach_pan_pour` 普通轨迹版本未改动。
- 证据：真机闭环成功为用户现场确认，控制器逐窗口/姿态日志未全套归档，故标记 `implemented-verified`，证据级别 3，限制为日志完整性和急停/取消/重复任务恢复未覆盖。
- 下一步：按用户约定分别提交两个仓库（本地 `git commit`，不 push）。

## 当前会话（2026-08-06 版本口径澄清：正式 V1 vs 临时测试版本）

- 用户指出此前把“V1 正式版本”与临时测试路径混淆；本轮先冻结版本口径，避免后续再次搞混。
- **正式 V1 版本** = 主仓库 `pan_pour`（`PanPourPolicy`，TASK-011/012/013 基础已实现）：感知组锅把结果 → 沿 PCA 主轴偏置的抓取 → 参数化抓取 TCP → 提锅至准备倾倒 → 底盘协同移动（左臂保持姿态）→ 餐盘定位 → `pour_point_C = plate_center_C + pour_offset_C` → 锅具 TCP 转换 → 锅具 TCP 坐标系下增量倾倒回放 → 预留放回/home。业务目标统一在机器人中心坐标系 C 表达。这是后续要完善的正式产品版本。
- **临时测试版本 1** = `teach_pan_pour`（TASK-016）：固定工位、无感知/无底盘/无中心 C 系，普通拖动示教轨迹回放，用于验证动作链路，真机已跑通。
- **临时测试版本 2** = `teach_pan_pour_delta`（TASK-016 增量改造）：同固定工位约束，倾倒改为 GUI 增量法兰轨迹回放、放锅改为固定点 `put_fixed`，真机已跑通。
- 两个临时测试版本均已真机跑通；下一步工作转向完善正式 V1 版本（`pan_pour` / `PanPourPolicy`）。
- 记录位置：`.project-log/current-session.md`、`.project-log/progress.md`、`.project-log/loop/handoff.md`。
## 当前会话（2026-08-07 手眼标定 CAL-06 肘部搜索 7-DOF 校验失败）

- 前置失败已解决：`robot_driver_node` 报 `Lbot SDK路径 未配置` / `xCore SDK path: None` 崩溃，根因是 `ConfigReader` 读启动时 CWD 下 `.localconfig`；改为**先 `cd .../kitchen_robot_home`**（该目录 `.localconfig` 已配 4 个 SDK 路径）再跑 launch 即恢复。左臂 `.159` / `.right .160` 双连接成功（`xCore 0.5.1.ar_12`），`get_arm_pose` 正常。
- 失败签名：自动标定 17 个采样姿态**全部运动失败**：`Cartesian control with elbow range failed: arm-angle range search requires 7-DOF robot, got 13`，最终 `0 个有效样本 / 样本数不足: 0/10，标定失败`。
- 根因（已真机坐实，左臂 `.159`）：`jointPos` 返回 **13 个值 = 7 个真实臂关节 + 6 个外部轴占位（全 0）**，实测 `vals=[0.4086,1.0454,-0.3098,1.2922,-0.1901,0.4047,-0.2947,0,0,0,0,0,0]`。`ElbowRangeSearcher.initialize()` 用 `len(jointPos)` 当自由度得到 13，随后 `if self._joint_count != 7` 直接抛错。
- 结论：不是脚本逻辑写错，而是“Er Pro 机型 + 当前 SDK 0.5.1.ar_12”把 `jointPos` 返回成 7+6 格式，脚本 `len()==7` 校验对该格式不兼容。
- 候选修复（均涉及 `/opt/ros/humble` 下 `.deb` 驱动黑盒，**待用户确认才动**）：
  - **A（推荐，最小）**：`elbow_range_searcher._get_current_joints()` 改 `list(jointPos)[:7]` 只取前 7 个真实关节，`_joint_count` 恢复 7；前提是 6 个外部轴实测恒为 0。
  - **B（不改黑盒，改动面更大）**：标定运动链路改用普通 `MoveL`（`control_cartesian`），不走肘部搜索。
- 附带更正：此前说 “IP 一开始就是错的” 不准确，`DEXBOT_ROBOT_IP`/robot_params IP 从一开始就是对的（左 `.159`/右 `.160`），真机失败主因是上面 CWD/.localconfig 与 7+6 返回值。
- 状态：根因已定位并记录，**未改任何代码**；下一步等用户确认选 A 还是 B。

## 当前会话（2026-08-07 手眼标定 CAL-01/02/04 处理）

## 当前会话（2026-08-10 项目进度快速对齐）

- 目标 `GOAL-001` 仍为 active，工作流阶段为 implementation。
- 已完成并有记录：技术路线/需求/架构基线，TASK-010、TASK-011；`teach_pan_pour` 与 `teach_pan_pour_delta` 固定工位测试链路已完成用户现场真机验证；NRT 增量倾倒完整轨迹已完成用户现场真机验证。
- 正式 V1：`pan_pour` 单一自包含 Skill 及 `WAITING_FOR_BASE_RETURN` 已落地主线提交，但仍为 `implemented-unverified`；中心坐标系、抓取/锅具 TCP 现场标定和正式 V1 完整闭环仍未完成。
- 当前任务清单：`TASK-016`（测试路径收口）in_progress，`TASK-018`（正式 V1 完整运动链）in_progress，`TASK-019`（手眼标定前置问题）in_progress；`TASK-012/013/014` 仍分别受感知字段/底盘接口/轨迹资产与 Driver 语义阻塞。
- 标定进度：左臂手眼标定已有 22 个有效样本结果；右臂标定、中心坐标生成及写回主线参数尚未完成。
- 仓库状态：`kitchen_robot_home` 分支较远端领先 4 个提交，SDK 路径存在 65 个未提交删除状态，未发现其他未提交主线文件；`robot_motion_executor` 有 3 个 SDK 切换相关文件未提交。未执行清理、回滚或提交。
- Loop 恢复发现 `.project-log/loop/active-run.yaml` 存在 YAML 解析问题并已自动重建；恢复状态仍指向已 hand-off 的 `TASK-011`，与任务清单当前活动任务不一致，后续需单独修复 Loop/任务绑定，不能据此直接判定项目完成。
- 精确下一步：先确认 SDK 未提交变更的归属并分别整理两个仓库；然后继续右臂标定/中心坐标生成，或在感知组与底盘组契约到位后接续 `TASK-012`，全程不宣称正式 V1 硬件闭环完成。

## 当前会话（2026-08-10 三个 PanPour Policy 与双仓库提交前确认）

- 本轮仅做确认和人工 Review，未修改产品代码、未创建提交、未推送远端。
- 审查对象：主线 `pan_pour` 正式 V1、`teach_pan_pour` 固定工位测试版、`teach_pan_pour_delta` 增量倾倒测试版，以及执行器对应三个 Skill、资源清单、Planner 路由和 MotionExecutor 注册。
- 调用链已人工确认：`StartTask(task_type)` → `TaskPlannerNode._initialize_policy` → Policy 一阶段一目标 → `_build_skill_goal`/`_build_cartesian_goal` → `motion_executor/execute_task` → MotionExecutor Skill → MotionPrimitive → RobotDriver。
- 三个测试 Policy 的阶段列表与对应 Skill action_name 映射一致；正式 V1 阶段链包含抓取、闭合、提锅、底盘前置等待、餐盘等待、倾倒定位、增量回放、底盘回位等待、固定放锅、开手和回 home。
- 重要确认项：正式 V1 的 `update_handle_detection`、`update_plate_center`、`update_base_positioned` 目前只有 Policy 和单测调用，Planner 没有适配调用；当前 `ScenePerception/ObjectDetection` 仅提供通用物体位姿，没有锅把抓取点、PCA、餐盘中心、frame_id、新鲜度和底盘生命周期契约。因此正式 V1 尚未形成可由真实视觉/底盘驱动的 ROS 闭环。
- 重要风险：三个测试 Policy YAML 中的 `point_speed`、`trajectory_speed`、`blend_zone_mm`、`trajectory_timeout_sec` 会被 Policy 读取，但 `_build_skill_goal`/`TaskTarget` 没有把这些参数传给 Executor；Executor Skill 有另一套默认值。当前两边数值相同，但存在双配置源漂移风险。
- 重要安全确认项：`PanPourPolicy.clear()` 按测试约定保留上次视觉观测，若任务复用同一 Policy 且没有新鲜度/任务代际校验，旧锅把/餐盘数据可能被新任务直接使用；需在确认阶段明确这是写死 V1 设计还是需要任务级清空/新鲜度门禁。
- 两仓库相对各自 `origin/robam_kitchen`：主线有 4 个本地未推送提交，执行器有 3 个本地未推送提交；相对各自 `main`（当前均为早期 Initial commit），主线为 5 个提交/824 个文件，执行器为 4 个提交/82 个文件，该比较基线不适合单独用于提交审查。
- 主线 4 个本地提交涉及 Policy、参数、Planner 路由/状态、bringup IP/CAN/CWD、测试、SDK 路径和示教点位；执行器 3 个本地提交涉及三个 Skill、轨迹/手部/位姿资源、增量回放客户端、MotionExecutor 注册、测试和资源打包。
- 未提交状态保持不变：主线旧 SDK `xcoresdk_python-v0.5.1.ar_12` 有 64 个删除项，新 SDK `xcoresdk_python-v0.7.1.ar_6` 整目录未跟踪；执行器有 3 个 SDK 路径切换文件未提交。该部分必须与 Policy 提交范围分离确认。
- 验证：主线定向 Policy/Planner 测试 24 passed；执行器三个 Skill 与轨迹/回放定向测试 41 passed；两个包分别 `colcon build --symlink-install --packages-select ...` 成功；相关已提交差异 `git diff --check` 无输出。未做真实 ROS 节点闭环和本轮真机验证。
- Review 状态：`implemented-unverified`，暂不具备“确认无误后直接推送”的条件；下一步先处理视觉/底盘接口、参数单一来源、旧观测新鲜度和 SDK/硬件配置归属确认，再进行提交前讲解和分仓库提交。

## 当前会话（2026-08-10 提交前 Review 范围确认）

用户确认并冻结以下处理口径：

- 正式 V1 当前底盘和视觉尚未接通是正常状态；感知组和底盘组尚未完成对应接口，因此本轮不把“未接通”作为正式 V1 的代码缺陷或提交阻塞。
- 测试版 Policy 的参数双配置源问题暂不处理；本轮只要求确认正式 V1 不存在同类问题。
- `PanPourPolicy.clear()` 保留旧视觉观测的新鲜度风险暂时只记录，不在本轮处理。
- SDK 版本切换相关改动不纳入本次提交；本次只提交当前三个 Policy / 正式 V1 任务相关改动，SDK 改动保持排除。

本轮后续动作冻结：不修改代码、不整理工作区、不创建提交、不推送远端，等待用户下一步指令。

## 当前会话（2026-08-10 launch 本地适配清理方案）

- 用户确认：`kitchen_robot_home` 的 `src/dexbot_bringup/launch/dexrob_full.launch.py` 直接恢复为 `origin/robam_kitchen` 版本，本地历史中移除个人 launch 改动，不提交、不推送。
- 个人适配不再用补丁脚本，改用本机固定启动方式保留：
  - 先 `cd /home/tbl/Project/boss_electrics/kitchen_robot_home`，保证 `robot_driver` 读取当前工作区根目录的 `.localconfig`；
  - 启动前 `export PYTHONNOUSERSITE=1`，绕开本机 `~/.local` NumPy 2.2.6 对 ROS/OpenCV 的污染。
- 操作边界：只重写 `kitchen_robot_home` 本地历史，将 `51c148c` 中 launch 文件个人改动摘除；SDK 相关删除/新增保持未提交；不 push。
- 下一步：执行本地历史清理，随后验证 `git diff origin/robam_kitchen..HEAD -- src/dexbot_bringup/launch/dexrob_full.launch.py` 为空，等待用户继续检查后再决定提交/push。

## 当前会话（2026-08-10 launch 本地历史清理完成）

- 已完成 `kitchen_robot_home` 本地历史重写：`51c148c` 中的 `dexrob_full.launch.py` 个人改动被摘除，新历史仍为 5 个本地提交，HEAD 为 `8d58c08`；原历史保存在备份分支 `backup/local-history-before-launch-clean-20260810`，未 push。
- 验证结果：
  - `git diff origin/robam_kitchen..HEAD -- src/dexbot_bringup/launch/dexrob_full.launch.py` 无输出；
  - `src/dexbot_bringup/launch/dexrob_full.launch.py` 不在 `git diff origin/robam_kitchen..HEAD --name-status` 中；
  - 工作区除 `src/sdk/` 删除/新增外无其他未提交改动；
  - SDK 改动保持未提交，未 push。
- 当前暂停点：等待用户继续检查其余内容；确认后再执行后续 commit/push 决策。

## 当前会话（2026-08-10 PolicyDecision 公共架构回退完成）

- 已按用户确认原则移除本次为等待功能新增的公共扩展：
  - 删除 `dexbot_task_planner/entities/policy_decision.py`；
  - `entities/plan.py`、`policy/base_policy.py` 与 `origin/robam_kitchen` 一致，移除三个新增 `PlanType` 和 `BasePolicy` 返回类型扩展；
  - `task_planner_node.py` 恢复旧公共调度流程，仅保留 3 个新任务的 Policy 注册、`valid_task_types` 和 skill 路由加字符串匹配（相对远端 14 行）。
- 三个私有 Policy 已改回旧架构返回值：
  - `teach_pan_pour` / `teach_pan_pour_delta` 返回 `PlannedStep`，完成返回 `None`，失败走现有 retry 语义；
  - `pan_pour` 返回 `PlannedStep` / `None`，外部视觉/底盘 adapter 入口保留为私有字段方法，不再使用 `WAIT`。
- 删除/改写相关测试：删除 `test_policy_decision.py`，改写 `test_task_planner_decision_dispatch.py`，更新三个 Policy 测试。
- 验证结果：
  - 定向 Policy/Planner 测试 12 passed；
  - `dexbot_task_planner/test` 排除既有 linter 后 21 passed，3 deselected；
  - flake8/pep257 全仓基线仍有既有失败（2 failed），非本次改动导致；
  - `compileall`、`git diff --check`、`colcon build --symlink-install --packages-select dexbot_task_planner` 均通过。
- 本机 SDK 已通过 `git update-index --skip-worktree` + `.git/info/exclude /src/sdk/` 屏蔽；SDK 不进入提交、不 push。
- 本地提交已创建：`kitchen_robot_home` HEAD `a0aefce`（TBL出锅倾倒菜），SDK 未进入提交。
- 未 push；等待用户继续检查或决定下一步提交。

## 当前会话（2026-08-10 执行仓库历史合并与 SDK 路径剥离完成）

- `robot_motion_executor` 本地 4 个提交已合并为 1 个提交：HEAD `61b7e39`（TBL出锅倾倒菜），基于 `origin/robam_kitchen` 重新提交。
- 操作前备份分支：`backup/executor-before-squash-20260810`，原 HEAD `ec80580` 可通过该分支找回；备份分支未 push。
- 新 commit 已剔除 3 个 SDK 路径文件中的 v0.7.1 改动：
  - `utils/smoothie_path_record_replay.py`
  - `utils/xcore_path_client.py`
  - `test/test_path_replay.py`
- 本地 v0.7.1 SDK 适配已恢复，并通过 `git update-index --skip-worktree` 保持本地可用且不进入 git diff/push。
- 验证结果：
  - 定向执行器测试 41 passed；
  - `compileall` 通过；
  - `git diff --check` 通过；
  - `colcon build --symlink-install --packages-select dexbot_motion_executor` 通过；
  - HEAD 中无 `xcoresdk_python-v0.7.1` 引用，工作区状态干净。
- 未 push；等待用户继续检查或决定下一步。
