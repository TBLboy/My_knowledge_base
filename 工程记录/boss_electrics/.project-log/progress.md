# Progress

倾倒入盘技术路线、V1 业务澄清和技术选型已完成；当前进入工程实施阶段。

## 2026-09-02 跳过模式真机测试后回滚临时改动

- 用户确认跳过模式真机测试通过，要求回到上一次提交。已将临时 `SET_TCP_ENABLED=False`、`CHASSIS_NAVIGATION_ENABLED=False` 及配套测试改动全部回滚到 HEAD `f332c3e 跳过抓锅阶段`。
- home 工作区 clean；`colcon build --symlink-install --packages-select dexbot_task_planner` 通过。
- 注意：HEAD 上 `SKIP_MODE=1`，但 `test_skip_mode_disabled_keeps_initialize_flow` 未把 `_skip_mode` 设为 0，因此该既有 unittest 在 HEAD 上失败；本次按要求未修改 HEAD 内容。

## 2026-09-02 迁移当前 PourServe skip_mode 到新仓库

- 已把 home 当前 `sub_policy_pour_serve.py` / `sub_policy_pour_serve.yaml` / `test_pour_serve_navigation_policy.py` 状态对齐到 `/home/tbl/桌面/111/kitchen_robot_home`。
- 目标仓库此前已迁移大部分内容，本次实质改动为 `SKIP_MODE = SKIP_MODE_PRE_GRASPED`；YAML 与测试文件与 home 一致。
- 验证：目标仓库 compileall 通过；单测与 home HEAD 一致，仍仅有既有 `test_skip_mode_disabled_keeps_initialize_flow` 不一致。未提交。

## 2026-09-02 临时跳过 set_tcp 以便真机测试

- 背景：driver `ros-humble-dexbot-robot-driver 1.0.9` 在 `ArmServer` 中没有注册 `/robot_driver/set_tcp` service server；`ros2 service list` 里出现的是 `motion_executor_node` 的 service client，因此 `SetTcp service not available`。
- 修改：`PourServePolicy` 新增临时开关 `SET_TCP_ENABLED=False`；关闭时 skip 模式首步为 `CAPTURE_HANDLE -> move_joints(lift)`，非 skip 模式首步为 `initialize`。原 set_tcp 构造代码保留，`True` 即恢复。
- 验证：`compileall`、`colcon build --symlink-install --packages-select dexbot_task_planner`、7/7 unittest 通过；未提交，按真机测试结果回滚/保留。

## 2026-09-02 临时跳过两次底盘导航

- 用户当前不开底盘，`PourServePolicy` 新增 `CHASSIS_NAVIGATION_ENABLED=False`；PICK/LIFT 完成后直接进入 `WAIT_PLATE`，POUR 完成后直接进入 `PLACE`，不再生成 `chassis_control`。
- 原 serve/cook 导航生成逻辑保留；`True` 即恢复。测试默认验证无底盘链路，并保留开启开关时 serve/cook 导航生成的覆盖。
- 当前待真机流程：`CAPTURE_HANDLE -> move_joints(lift) -> wait_plate -> pour -> place -> completed`。
- 验证：`compileall`、`colcon build --symlink-install --packages-select dexbot_task_planner`、9/9 unittest 通过；未提交。

## 2026-09-02 PourServe 增加已抓锅 skip_mode

- 新增顶层 `SKIP_MODE`：`1` 表示进入 Policy 时上游已把锅把交给左臂，跳过 `initialize`、`wait_handle` 和 `pick`，从 `set_tcp -> get_arm_pose -> move_joints(lift)` 直接进入导航/倾倒/放锅流程。
- Policy 内部在 `SET_TCP` 完成后调用 `/robot_driver/get_arm_pose(arm=0)` 记录已抓锅位姿；因 default TCP 全 0，该 `endInRef` 返回值直接作为中心坐标系下 flange 快照，供 place 使用，不再叠加 `TCP_GRASP_TRANSLATION`。
- 代码改动：`sub_policy_pour_serve.py` 新增 `CAPTURE_HANDLE`/`LIFT` 阶段、`_build_lift_step()`、`_capture_pre_grasped_pose()`；测试新增 skip 分支和 FullPolicy skip 全链。
- 验证：源码仓库 compileall、`colcon build --packages-select dexbot_task_planner`、7/7 unittest 通过；两个改动文件已同步到 `/home/tbl/桌面/111/kitchen_robot_home`，目标仓库 compileall 通过。
- 待办：真机验证 skip 模式读取位姿、抬锅和后续导航/倾倒/放锅；未提交、未推送。

## 2026-09-02 PourServe 接入两次底盘导航

- 已把底盘导航从占位改为正式 `PLAN_CHASSIS_CONTROL` 步骤：pick 完成后导航到 `serve`，等待餐盘感知；pour 完成后导航回 `cook`，再执行现有 place。
- 接入方式仿 Gather：`action_name=move_to_point`，通过 `fruit_id` 传 marker，`control_positions=[navigation_timeout_sec, poll_period_sec]`。
- `sub_policy_pour_serve.yaml` 新增 `navigate_to_serve` / `navigate_to_cook`，marker 分别为 `serve` / `cook`；Pick/Pour/Place 原参数与数据来源未改。
- 新增 `test_pour_serve_navigation_policy.py`，验证 PICK 完成 -> serve 导航 -> WAIT_PLATE、POUR 完成 -> cook 导航 -> PLACE。
- 验证通过：`compileall`、2 个 unittest、`colcon build --packages-select dexbot_task_planner`、FullPolicy 全链路冒烟。
- 待办：底盘端确认 `serve` / `cook` marker，真机验证导航与全链路，获负责人同意后提交/推送。
- 已把本轮三个文件同步到新仓库 `/home/tbl/桌面/111/kitchen_robot_home`；定向 unittest 与新仓库 FullPolicy 冒烟通过，新仓库仍为未提交状态。

## 2026-09-01 PourServe initialize 改用 skill 默认 home

- 用户撤销了此前对 `InitializeSkill` 的擅自修改，motion 仓库保持无改动。
- 仅在 `sub_policy_pour_serve.yaml` 将 `initialize.move_home` 清空为 `{}`，改用 `InitializeSkill` 默认 home；`move_home_intermediate` 同步恢复为空配置。
- 验证：`colcon build --symlink-install --packages-select dexbot_task_planner` 通过；`InitializeSkill.build_primitives()` 输出默认中间点 + 默认 home，默认 home 对应 `[57, -90, -94, 115, -13, 22, -5]` 度。

## 2026-09-01 从 home 历史移除 src/sdk

- 用户确认把整个 `src/sdk/` 从历史提交中移除；本机 SDK 文件必须保留。
- `.git/info/exclude` 已忽略 `/src/sdk/`，SDK 不再进入新提交。
- 使用 `git filter-branch` 从本地 `code_integration` 和 `backup/code_integration_before_cleanup_0826` 历史移除 `src/sdk`；主分支不包含该目录，无需重写。
- 重写前备份：`/tmp/kitchen_robot_home_pre_sdk_remove_20260901.bundle`、`/tmp/kitchen_robot_home_src_sdk_20260901.tar.gz`、`/tmp/kitchen_robot_home_uncommitted_20260901.patch`。
- 重写后本地验证：三个本地分支 `git log -- src/sdk` 均为 0，`git ls-files src/sdk` 为 0，`refs/original` 已清除，SDK 本地文件完整恢复。
- 待办：远端 `origin/*` 仍保留旧历史；如需远端也移除，必须协调后在对应分支执行 force push，并同步所有协作者。

## 2026-09-01 PourServe 移除 hold_or_not

- 用户确认当前流程不需要抓取判定，已删除 `PourServePolicy` 中的 `hold_or_not` 和拆分后的 `pick_grasp` / `pick_retreat` 两个 pick 子步骤。
- 流程恢复为单次 `pour_serve_pick`：`set_tcp -> initialize -> pick -> pour -> place -> completed`；配置 `sequence` 同步为 `['initialize', 'pour_serve_pick', 'pour_serve_pour', 'pour_serve_place']`。
- `move_to_pick_retreat` 恢复为 PickSkill 的一部分，运行时由 Policy 填充抬锅 `LIFT_JOINTS`；初始化 home 动作保留。
- 验证通过：compileall、YAML 解析、`colcon build --packages-select dexbot_task_planner`、完整状态机冒烟、Motion `Pick/Pour/PlaceSkill` primitive 构造校验。
- 未提交、未推送。

## 2026-09-01 PanPour 迁移到 PourServe

- 迁移前已备份提交 `083960f`，覆盖当前 PanPour 实现、感知配置和 `pour_delta.json`。
- 新建/替换 `sub_policy_pour_serve.py` 与 `sub_policy_pour_serve.yaml`，类名改为 `PourServePolicy`，内部步骤与 profile 统一为 `pour_serve_*`。
- FullPolicy 注册改为 `"pour_serve": PourServePolicy(...)`；旧 `sub_policy_pan_pour.py/yaml` 已删除。
- 保留：hold_or_not 参数通过 `action_name` 传递、`pour_delta.json` home 资源路径、`set_tcp` 使用 `default` profile。
- 验证：compileall、YAML sequence、colcon build、`target_class="pour_serve"` 全状态机均通过。
- 未提交、未推送。

## 2026-09-01 hold_or_not 参数链路修正

- 背景：PanPour 已把 PICK 阶段拆为 `pan_pick_grasp -> hold_or_not -> pan_pick_retreat`，但 Motion `HoldOrNotSkill` 只从 `target.action_name` 读取 key:value 参数，不读取 `skill_params_json`。
- 修正：`sub_policy_pan_pour.yaml` 的 `hold_or_not` 参数从 `skill_params.actions` 移到顶层 `parameters`；`sub_policy_pan_pour.py` 仿照 `GatherPolicy._build_bowl_verify_step()` 直接生成 `PLAN_HOLD_OR_NOT` step，并把 `fail_if_not_holding` / `hold_threshold` / `required_joints` 编码进 `action_name`。
- 验证：`compileall`、`colcon build --packages-select dexbot_task_planner`、状态机步骤序列、hold step 参数串、Motion `HOLD_OR_NOT` primitive 参数解析均通过。
- 待办：真机前确认左臂空载 baseline / torque 阈值；hold 失败后的恢复策略仍按之前记录后续解决。

## 2026-09-01 合并、感知配置与 PanPour 轨迹路径切换

- home `code_integration` 合并完成，提交 `36d53ad`；`tcp_profiles.yaml` 与 PanPour Policy 统一使用 `default` profile。
- 感知配置恢复 `task_name: boss_kitchen_scene_stir_frying`；`.localconfig` 修正 `yolo_model_dir` 并恢复 `yolo26l_obb.pt`。
- PanPour `pour_action.replay_file` 改为 `pour_delta.json`，由 `dexbot_task_planner/resources/trajectories` 提供；`_resolve_replay_file()` 已改为解析本包安装资源。
- 验证：`colcon build --symlink-install --packages-select dexbot_task_planner` 通过，安装空间资源和 Policy 解析均通过。

## 2026-08-28 感知 deb 1.0.23 与场景 task_name 检查

- `VERSIONS.yaml` 与已安装包均为 `ros-humble-dexbot-perception 1.0.23-0jammy`，`verify_versions.sh` 7/7 通过。
- apt 候选已出现 `1.0.24-0jammy`，当前主线仍按 1.0.23 锁定，暂未升级。
- 1.0.23 的 `dexbot_perception.tasks.registry` 支持：
  - `boss_kitchen_cut_cucumber`
  - `boss_kitchen_scene_cutting`
  - `boss_kitchen_scene_stir_frying`
  - `none` / `general` / 空字符串（passthrough）
- 当前主线 `perception_params.yaml` 仍为 `task_name: "boss_kitchen_scene_stir_frying"`；`perception2_params.yaml` 未配置 task_name，走 passthrough。
- 风险：`dexrob_full.launch.py` 硬编码加载 `perception_params.yaml`，不同场景同学仍需手动改同一文件。建议后续按场景拆分 YAML 或加 launch 参数，等用户确认后实施。

## 2026-08-26 InitializeSkill 接入 PanPour

- PanPour 状态机接入 `initialize`：`set_tcp -> initialize -> wait_handle -> pick -> wait_plate -> pour -> place -> completed`。
- `InitializeSkill` 新增 `hand_angles` 手部模式和 `joints` 回家模式，已有 `gripper`/`cartesian` 模式保留。
- 已按用户提供值写入 home：左臂 `127.1/77.2/-89.3/123.2/-14.1/7.0/0` 度，转换为弧度 `[2.2183134793, 1.3473941825, -1.558579022, 2.1502456385, -0.2460914245, 0.1221730476, 0.0]`；手部复用 `预抓把手`（`[100,100,100,100,100,100]`）。
- 已启用 PanPour pick 的 `move_to_pick_initial`，当前值按 `77/35/-60/90/36/-7/17` 度换算为弧度：`[1.343903524, 0.6108652382, -1.0471975512, 1.5707963268, 0.6283185307, -0.1221730476, 0.2967059728]`。
- PanPour place 收尾调整：`move_to_place_retreat` 填充 `pick_initial` 关节角，`move_to_place_end` 填充回 `home`。
- 验证通过：两个仓库 compileall、对应包 colcon build、Policy 生成 initialize 步骤、Motion 转 `GRIPPER_ACTION + MOVE_JOINTS`、`hand_angles` 转 `SET_HAND_ANGLES + MOVE_JOINTS`。

## 2026-08-28 PICK 阶段拆分为 pan_pick_grasp / hold_or_not / pan_pick_retreat

- 背景：`motion_executor` 仓库合并了 `hold_or_not` 和 `hold_monitor` 两个 skill，用于抓取后判定是否抓稳以及搬运时检测掉落。
- 改动：
  - `planstep_factory.py` 把 `hold_or_not` / `hold_monitor` 加入 `PLAN_TYPE_BY_NAME`，schema 共用 `hold_params_v1`。
  - `sub_policy_pan_pour.py` 引入 `_pick_substep` 计数器，把 PICK 阶段拆为三个连续 step：`pan_pick_grasp`（仅启用到 `pick_gesture`）→ `hold_or_not`（单次判定）→ `pan_pick_retreat`（仅启用 `move_to_pick_retreat`）。第 3 个 substep 完成时同步把 phase 推进到 `WAIT_PLATE`。
  - `sub_policy_pan_pour.yaml` 删除原来的全链路 `pan_pick`，新增 `pan_pick_grasp` / `pan_pick_retreat` 两个拆分模板和 `hold_or_not` 模板；`sequence` 同步更新。
  - `_populate_pick_actions` 拆为 `_populate_pick_grasp_actions` 与 `_populate_pick_retreat_actions`。
- 验证：`compileall` 通过；`colcon build --packages-select dexbot_task_planner` 通过；状态机全链路冒烟（set_tcp → initialize → pan_pick_grasp → hold_or_not → pan_pick_retreat → pan_pour → pan_place → completed）通过。
- 未验证：真机运行；hold_or_not 参数标定（baseline_torques / hold_threshold / required_joints）。
- 未提交。

## 2026-08-28 InitializeSkill 改用远端默认值

- 背景：远端 `InitializeSkill` 重新设计了参数体系，左右臂默认 home 角和 home_intermediate 都内置在 skill 里，policy 可以通过 JSON 浅合并覆盖。
- 改动：
  - `sub_policy_pan_pour.yaml` 把 `initialize.actions` 收成 `{ open_gesture: { hand_action_name: 预抓把手 }, move_home_intermediate: {}, move_home: {} }`，skill 用 `_actions_for_arm` 浅合并填充默认值。
  - `sub_policy_pan_pour.py` `_build_initialize_step` 删除手动覆盖 home 关节的代码，直接透传 step_config。
- 验证：冒烟通过，policy 生成的 `skill_params_json` 是空 actions，Motion skill 收到后用内置 home 角。

## 2026-08-26 下午 全流程跑通（视觉感知 + 机械臂动作链）

### 已解决的问题
1. **perception task_name 缺失**：添加 `task_name: "boss_kitchen_scene_stir_frying"` 到 `perception_params.yaml`，激活后处理输出 `pot_inner_handle`/`pot_inner_tip`/`plate_center`
2. **左手 CAN 接口错误**：切换为正确 CAN 接口后手部动作正常执行
3. **倾倒阶段 IK 无解**：调整 `POUR_OFFSET_CENTER_M`(0.08→0.2)、`POUR_INITIAL_FLANGE_RPY`(改为与抓锅同姿态)、`TCP_PAN_TRANSLATION`(改为非零偏移)
4. **YOLO 模型路径**：创建 `local_models/yolo/` 并软链接 `yolo26x_obb.pt` → `boss_kitchen_scene_stir_frying_obb.pt`
5. **TCP 标定脚本迁移**：`tcp_calibration.py` 迁移到 `local_tcp_calibration/`，加入 `.git/info/exclude`

### 当前状态
- **视觉全流程跑通**：pick（抓锅）→ wait_plate → pour（倾倒）→ place，放开底盘占位
- 不带底盘，底盘步骤继续占位跳过
- 坐标系：中心坐标系，`toolset.ref.trans` 左臂 `[0, -0.0787, 0]` 右臂 `[0, +0.0787, 0]`
- `get_arm_pose` 返回 `flangeInBase`（BASE 坐标系），和 SDK 原生坐标系一致
- TCP 偏移量 xyz 定义在**法兰坐标系**自身
- 手眼标定已完成（左+右+中心坐标系）

### 关键参数（当前有效值）
- `TCP_GRASP_TRANSLATION = (-0.006, 0.012, 0.116)` 法兰坐标系
- `TCP_PAN_TRANSLATION = (-0.286, 0.012, 0.116)` 法兰坐标系
- `POUR_OFFSET_CENTER_M = (0, 0, 0.2)` 中心坐标系偏移
- `POUR_INITIAL_FLANGE_RPY = (-1.70, 0.076, -1.73)` 与抓锅姿态相同
- `ref.trans` 左臂 `[0, -0.0787, 0]` 右臂 `[0, +0.0787, 0]`

### 下一步
- 真机带底盘联调（底盘步骤打通后接入）
- 或继续优化倾倒轨迹回放

### 2026-08-26 code_integration 历史清理

- home 本地 `code_integration` 领先远端 6 个提交；motion 已合并远端王韵博的 `pickplace 力控触觉双闭环` 提交。
- 未推送历史里的大模型 `.pt` 和 `robot_params.yaml.bak` 已通过 `filter-branch` 从 Git 历史移除，仅重写本地提交，未重写 `origin/code_integration`。
- 本地模型文件和 `.bak` 已从备份分支恢复，加入 `.git/info/exclude` 不跟踪。
- 备份分支：`backup/code_integration_before_cleanup_0826`。

## 2026-08-26 中心坐标系生成并落盘

- 修正后的左臂标定（16 样本，`1.52 mm / 0.344°`）与当前右臂标定（11 样本，`1.99 mm / 0.865°`）已用于生成中心坐标系。
- 已写入 `src/dexbot_bringup/config/calibration/left_calibration_result.yaml`、`right_calibration_result.yaml`、`center_calibration_result.yaml`，并把 `toolset.ref.trans` 与 base frame 配置写入 `src/dexbot_bringup/config/robot_driver/robot_params.yaml`。

## 2026-08-24 PanPour 子 Policy 实现与验证

- 新增 `policy/robam/sub_policy_pan_pour.py` 与 `config/robam/sub_policy_pan_pour.yaml`，实现 wait_handle/pick/wait_plate/pour/place/completed 状态机。
- 使用现有 PickSkill、PourSkill、PlaceSkill 完成预抓取、抓取、抬锅、倾倒起点、增量轨迹回放、回正，放回、张开、回 home。
- PanPour 私有业务参数按 `PlatePourPolicy` 模式放在 `sub_policy_pan_pour.py` 顶层常量，YAML 只保存三个 manipulation skill 动作模板。
