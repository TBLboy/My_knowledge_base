# Progress Log

## 2026-06-06 19:44 Local Time

- Objective: 为 CutTofo 项目初始化 `.project-log` 工程记录。
- Work completed: 创建了完整的 `.project-log/` 目录结构和初始化文件，包括：
  - `requirements.md` — 项目目标、需求、约束
  - `business-logic/main.md` — 三条主路径（豆腐、黄瓜、抓料倒酱）
  - `business-logic/graph.md` — 节点图和映射
  - `business-logic/nodes.md` — 每个动作节点的状态定义
  - `business-logic/edges.md` — 每个执行链的详细描述
  - `business-logic/open-questions.md` — 4 个待明确问题
  - `business-logic/decision-records.md` — 4 个架构决策记录
  - `business-logic/constraints.md` — 系统、硬件、软件约束
  - `hardware/sdk-mapping.md` — 硬件和 SDK 映射
  - `config/config-schema.md` — 配置参数 schema
  - `architecture/software-architecture.md` — 系统架构概述
  - `debugging/known-issues.md` — 已知问题记录
  - `progress.md` — 初始进度记录
  - `current-session.md` — 当前会话状态
- Business logic impact: 初始化业务逻辑记录（与现有实现对齐）。
- Problems encountered: 无。
- Resolution: N/A。
- Verification: 文件已创建并通过审查。
- Unverified items: 无。
- Files changed: 全部 `.project-log/` 文件。
- Next steps: 根据用户需要继续优化工作。

## 2026-06-06 20:50 Local Time

- Objective: 深入梳理豆腐切割业务流程，重点分析视觉检测管线。
- Work completed:
  1. 完整阅读 orchestrator 工作流编排器（workflow_runner.py、tofu_workflow_params.yaml）
  2. 完整阅读 prepare 技能（tofu_prepare_workflow.py、tofu_prepare_node.py、tofu_prepare_params.yaml）
  3. 完整阅读 cut_round 技能（tofu_cut_round_workflow.py、tofu_cut_round_node.py、tofu_cut_round_params.yaml）
  4. 完整阅读视觉管线（pose_estimator_node.py、vision_params.yaml、vision_bringup.launch.py）
  5. 完整阅读视觉跟踪器（vision_geometry_tracker.py、prepare_vision_state.py）
  6. 完整阅读几何计算（tofu_geometry.py、cut_round_path.py）
  7. 深入分析 PCA OBB 核心算法（vision_utils.py 中 get_pose_from_mask）
  8. 深入分析 `corner_mode: aabb` 导致的顶面角点丢失旋转信息问题
- Business logic impact: 无（仅在代码阅读分析层面）。
- Problems encountered:
  - 当前 `corner_mode: aabb`（vision_params.yaml）导致 geometric_features[8:19] 中的顶面角点是 Base 系轴对齐矩形，不包含豆腐旋转信息。
  - 结果是 `compute_edge_dir()` 始终回退到 `[1,0,0]`（base_X），`edge_align: true` 无法真正对齐棱边。
- Resolution: 待后续讨论优化方案。
- Verification: 代码逻辑追踪确认，与 `vision_params.yaml` 配置一致。
- Unverified items: 无。
- Files changed: 无代码改动。
- Next steps: 与用户讨论视觉检测管线优化方向（aabb → pca_constrained 或其他方案）。

## 2026-06-06 21:30 Local Time

- Objective: 修复 workspace 中所有老旧硬编码路径，完成完整编译验证。
- Work completed:
  1. 清理 workspace 所有编译产物（src/build/, src/install/, src/log/）
  2. 完整编译全部 26 个 ROS 包
  3. 全量扫描并修复 30+ 处老旧硬编码路径，涉及：
     - `dexbot_ros2_ws_525`（已删除的旧版）→ 当前 workspace
     - `/home/kim/projects/...`（另一开发者）→ 动态 `find_ws_root()` 或 `os.path.expanduser`
     - `/home/a/Desktop/...` 和 `/home/a/projects/...`（另一开发者）→ 同上
     - SAM3 模型路径 `/home/a/models/sam3` → `/home/tbl/Project/models/sam3`
     - `AR5_dual_scene.xml` 中 16 处硬编码 mesh 路径 → `package://` URI
  4. 修复 README.md / README_CUTTOFU.md / GUI/README.md / cuttofo_graph_check.sh
  5. 修复 `.bashrc` 中旧的 ros workspace source 路径
  6. 修复后完整编译验证通过（26 包，0 错误）
- Business logic impact: 无。
- Problems encountered:
  1. 路径来源复杂：涉及 3 个不同开发者的机器路径和被删除的 `_525` 旧版本
  2. 部分 Python 代码中有 `os.path.expanduser("/home/kim/...")` 形式硬编码，转换为相对路径或 `find_ws_root()` 动态查找
- Resolution: 采用 `find_ws_root()` 动态发现 + `os.path.expanduser("~/Project/cucumber/...")` 统一路径。
- Verification: 完整编译 26 包通过，grep 确认无残留老旧路径。
- Unverified items: 无。
- Files changed: 涉及 dexbot_bottom_layer、dexbot_bringup、dexbot_middle_layer、dexbot_toolbox、cuttofo_xcore、CutTofo 内多个子包，共 20+ 文件。
- Next steps: 等待用户确定下一步优化方向（视觉检测管线优化等）。

## 2026-06-06 23:45 Local Time

- Objective: 真机测试 constrained_obb 视觉管线，排查 SAM3 检测问题。
- Work completed:
  1. 配置 `corner_mode: constrained_obb` 并启动完整视觉管线（RealSense + SAM3 + pose_estimator + camera_viewer）
  2. 排查 SAM3 零检测问题，定位两个根本原因：
     - **QoS 不匹配**：SAM3 用 BEST_EFFORT 订阅 RealSense RGB（实际发布 RELIABLE），DDS 不兼容导致 image_callback 永不触发
     - **代码架构缺陷**：新版 SAM3 节点通过 `camera_backend` 自动检测 + `_setup_color_image_subscription()` 多层间接创建订阅，旧版直接 `create_subscription(Image, topic, cb, 10)` 简单可靠
  3. 修复方案：YAML 显式设置 `image_topic` 跳过自动检测，QoS 改为 RELIABLE
  4. 同学工程 `dexbot_ros2_ws-cut_to_fo_featrue` 复现了完全相同的问题，确认是 skills 架构迁移（commit `951221a6`）时引入的代码问题，非个别环境问题
  5. 完整编译 26 包验证修复
- Business logic impact: 视觉管线 `corner_mode: constrained_obb` 已可用。
- Problems encountered:
  1. SAM3 模型启动后完全不产生检测（话题存在但无消息）
  2. 根因诊断耗时较长（QoS 修改、调试日志插入、对比旧代码）
  3. 同学代码中存在同样问题（git blame 确认来自 commit `951221a6`）
- Resolution:
  - `sam3_detector_node.py`：图像订阅从 `qos_profile_sensor_data`（BEST_EFFORT）改为 RELIABLE QoS
  - `vision_params.yaml`：增加 `image_topic: /camera/camera/color/image_raw` 绕过自动检测分支
- Verification: 重启后确认图像回调触发，SAM3 正常检测。
- Files changed: `sam3_detector_node.py`（QoS）、`vision_params.yaml`（image_topic）
- Next steps: 验证 constrained_obb 顶面角点输出是否包含旋转信息。


## 2026-06-07 02:10 Local Time

- Objective: 创建可视化节点包 cuttofo_skill_visualizer。
- Work completed:
  1. 包目录结构搭建完成
  2. 28 个网格文件已复制（arm_r:8 + arm_l:8 + hand:12）
  3. package.xml / CMakeLists.txt / setup.py / setup.cfg 已完成
  4. 双臂 xacro 已创建（mesh 路径改为自引用 package://cuttofo_skill_visualizer）
  5. hand xacro 已创建（同样自引用 mesh 路径）
  6. viz_hand_joint_bridge.py 已完成（关节名重映射+虚拟手合成）
  7. task_visualizer_node.py 已完成约 70%（一半代码写入，_callback 方法待写入）
- Business logic impact: 无。
- Problems encountered:
  1. Haiku 4.5 工具调用问题持续——Bash/Write/Edit 频繁出现空参数调用，导致写入中断
  2. task_visualizer_node.py 的 _callback 方法和 main() 函数已写到聊天中但未写入文件
  3. 剩余文件未创建：viz_hand_joint_bridge.py、launch、rviz、config
- Resolution: 暂停任务等待工具调用问题修复后继续。
- Verification: N/A。
- Next steps: 解决工具调用问题后继续完成可视化包剩余文件。

## 2026-06-06 16:04 CST

- Objective: 在现有 CutTofo skills 结构下落地新的自足可视化包，并完成构建接入与 live 联调。
- Work completed:
  1. 新增 `cuttofo_skill_scene_visualization` 包，目录位于 `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_scene_visualization`
  2. 完成包骨架与元数据：`package.xml`、`setup.py`、`setup.cfg`、`resource/`、`config/`、`launch/`、`rviz/`、Python package
  3. 迁移并适配旧 `cuttofo_xcore` 可视化代码：`scene_visualization_node.py`、`viz_hand_joint_bridge.py`、`tofu_geometry.py`
  4. 新增配置与 launch 组装逻辑：`scene_visualization_config.py`、`display_launch_helpers.py`、`scene_visualization_node.launch.py`、`scene_visualization_display.launch.py`
  5. vendoring 双臂 AR5 模型、LinkerHand O6 模型、meshes、RViz 配置到新包 `description/` / `rviz/` 下，并把活动资源的 `package://` 路径改为新包自引用
  6. 将新包接入 `CutTofo/scripts/build_skills.sh` 与 `CutTofo/scripts/build_cuttofo.sh` 的显式 `--paths` 构建链
  7. 清理 vendored `.bak` 备份文件，并修复因 setuptools 缓存 `SOURCES.txt` 导致的重建失败
  8. live 联调完成：
     - 使用现场已有 `/cuttofu/perception/objects_with_pose`、相机话题、双臂 joint states
     - 启动 `cuttofo_xcore tofu_state_node` 并 remap 到 `/cuttofu/perception/objects_with_pose`
     - 启动 `cuttofo_skill_scene_visualization scene_visualization_node`
     - 确认 `/tofu_state` 正常发布，`health_state=tracking`
     - 确认 `/tofu_visualization` 正常发布，类型为 `visualization_msgs/msg/MarkerArray`
- Business logic impact: 新增一个纯消费型可视化技能包，不改变现有豆腐/黄瓜/抓料主业务逻辑，仅新增观测与调试能力。
- Problems encountered:
  1. 新包未被 `colcon list` 自动发现，原因是当前 CutTofo skills 依赖 `build_skills.sh` / `build_cuttofo.sh` 的 `--paths` 显式构建机制
  2. vendored `xacro:include` 在批量替换时被写坏，导致 full display launch 初次启动失败
  3. 删除 `.bak` 后首次重建失败，原因是 build 目录里缓存了旧 `SOURCES.txt`
  4. live 抓取 `/tofu_visualization --once` 时拿到过 `DELETEALL` 清空帧，说明启动/丢失状态下有清理逻辑，尚未直接在 RViz 中确认持续 marker 表现
- Resolution:
  - 将新包显式加入两个构建脚本
  - 手工修正 `AR5_dual_W4C1C1.urdf.xacro` 中的 hand include 路径
  - 清理 `build/cuttofo_skill_scene_visualization` 与对应 install 缓存后重建
  - 完成 live 话题级验证，确认 `/tofu_state` 与 `/tofu_visualization` 链路打通
- Verification:
  - `bash src/dexbot_middle_layer/CutTofo/scripts/build_skills.sh --packages-select cuttofo_skill_scene_visualization`
  - `ros2 pkg executables cuttofo_skill_scene_visualization`
  - `ros2 launch cuttofo_skill_scene_visualization scene_visualization_node.launch.py -s`
  - `ros2 launch cuttofo_skill_scene_visualization scene_visualization_display.launch.py -s`
  - `timeout 12s ros2 launch cuttofo_skill_scene_visualization scene_visualization_display.launch.py enable_realsense:=false`
  - `ros2 topic echo /tofu_state --once`
  - `ros2 topic info /tofu_visualization`
- Unverified items:
  - 尚未在 RViz 中人工确认 marker 是否持续稳定显示
  - 尚未完成机器人模型、点云、marker 的空间对齐检查
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_scene_visualization/**`
  - `src/dexbot_middle_layer/CutTofo/scripts/build_skills.sh`
  - `src/dexbot_middle_layer/CutTofo/scripts/build_cuttofo.sh`
- Next steps:
  - 使用“视觉检测管线 + tofu_state_node + scene_visualization_display.launch.py”进行 RViz 真机观察
  - 确认 marker 持续显示是否正常
  - 联调机器人模型、点云、marker 的空间对齐，并针对 calibration / TF / mount pose 做优化

## 2026-06-06 21:25 CST

- Objective: 完成 525 版本豆腐独立感知层向当前 CutTofo skills 架构的迁移，打通 vision → tofu_perception → prepare/visualizer 的测试链路，并修复 GUI 对灵巧手 SDK 的源码依赖。
- Work completed:
  1. 恢复并接入 `cuttofo_skill_tofu_perception`，让豆腐任务几何计算回到独立感知节点，保持通用 `cuttofu_vision` 输出契约不变。
  2. 调整 orchestrator：`handle_approach` 成功后自动启动 `tofu_perception_node`，并在退出时清理子进程。
  3. 调整 prompt ownership：保留 `handle_approach_node` 管刀柄提示词，移除 `tofu_prepare` 对 tofu prompt 的发布，改为只有 `tofu_perception_node` 负责 tofu prompt。
  4. 接入 dedicated tofu 话题链路：`/cuttofu/perception/tofu_objects_with_pose`、`/cuttofu/perception/tofu_state`，下游 prepare 和 visualizer 直接消费 dedicated tofu 感知输出。
  5. phase6 override 已接入 orchestrator，对 `tofu_perception_node` 下发竖切专用 OBB percentile 覆盖参数，并与旧版本 phase6 行为保持一致。
  6. 修复测试链路包发现问题：确认 `cuttofo_skill_tofu_perception` 与 `cuttofo_task_visualizer` 需要通过 CutTofo skills base path 显式构建，已完成构建验证。
  7. 修复 SAM3 camera viewer 无绿色 mask 的问题：`tofu_vision_params.yaml` 中 `publish_visualization` 改为 `true`。
  8. 调整 RViz tofu marker 风格以贴近 xcore 参考：去掉顶面填充，仅保留 top outline；恢复 knife spine 青色箭头；加深顶面四角连线透明度。
  9. 更新默认提示词：测试视觉默认 `text_prompt` 改为 `cargo truck`，避免 `_none_` 或空词误检；豆腐默认 prompt/class_filter 改为 `ridged_tofu`。
  10. 对比正确参考版本 `dexbot_ros2_ws备份/dexbot_ros2_ws（附件32-准备重构框架）/src/cuttofo_xcore`，确认当前豆腐主链路 `constrained_obb` 参数与 phase6 覆盖参数基本对齐。
  11. 将 `tofu_vision_params.yaml` 的独立测试视觉链路也切到 `constrained_obb`，并补齐整套 OBB 参数，使独立测试链路与附件32参考版本收口。
  12. 修复 GUI 灵巧手 SDK 导入问题：`src/gui/main.py` 启动时自动把本地 `linkerbot-python-sdk/src` 注入 `sys.path`，让 GUI 直接使用仓库中的 SDK 源码而不是外部安装包。
- Business logic impact:
  - 豆腐切割主路径已切回“通用 vision → dedicated tofu_perception → 下游控制/可视化”的 525/附件32 风格分层。
  - tofu prompt ownership 已明确收口到 `tofu_perception_node`，控制链路不再切换 tofu prompt。
  - phase6 竖切视觉覆盖逻辑恢复，与旧版本约定一致。
  - GUI 对灵巧手的依赖方式变更为“优先使用工作区源码 SDK”。
- Problems encountered:
  1. `cuttofo_skill_tofu_perception` / `cuttofo_task_visualizer` 初始 `package not found`，根因是当前构建方式依赖 CutTofo skills base path，而不是根工作区自动发现。
  2. 初始独立测试视觉参数 `tofu_vision_params.yaml` 中 `publish_visualization=false`，导致 camera viewer 打开但不画 SAM3 绿色 mask。
  3. 初始 task visualizer 虽声明对齐 xcore，但视觉风格仍有偏差（额外顶面填充、颜色/透明度不一致）。
  4. GUI 手控页在源码树直接启动时无法导入 `linkerbot`，根因是 Python 未自动包含本地 SDK `src` 目录。
- Resolution:
  - 使用 CutTofo skills `--base-paths` 显式构建缺失包并重新 source。
  - 调整 `tofu_vision_params.yaml`、`tofu_perception_params.yaml`、`task_visualizer_node.py`、`workflow_runner.py`、`main.py` 完成链路收口。
  - 通过对比附件32 的 `cuttofo_config.yaml` 和 phase6 逻辑，核对并对齐 constrained_obb 参数与默认 prompt/class_filter。
- Verification:
  - `colcon build --base-paths ...cuttofo_skill_tofu_perception ...cuttofo_task_visualizer ...cuttofo_orchestrator --symlink-install` 通过。
  - `ros2 launch cuttofu_vision vision_bringup.launch.py ...`、`ros2 launch cuttofo_skill_tofu_perception tofu_perception.launch.py ...`、`ros2 launch cuttofo_task_visualizer task_visualizer.launch.py ...` 已能进入用户真机测试阶段。
  - `python3 -c "... import linkerbot; print(linkerbot.__file__)"` 已确认 GUI 命中本地 SDK 源码路径。
- Unverified items:
  - 尚未完成用户驱动下的完整 tofu workflow 真机闭环验证（handle_approach → auto-start tofu_perception → prepare → cut_round → vertical_cut）。
  - GUI 已修复导入路径，但尚未继续验证后续 CAN / 设备通信层是否还有运行时问题。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_runner.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/tofu_task_orchestrator.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_no_approach_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/skills_bringup.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_node.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/**`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_task_visualizer/cuttofo_task_visualizer/task_visualizer_node.py`
  - `src/gui/main.py`
- Next steps:
  - 继续真机验证完整 tofu workflow，重点观察 auto-start tofu_perception、phase6 override、prepare/cut 对 dedicated tofu perception 的消费是否稳定。

## 2026-06-07 16:40 CST

- Objective: 修复豆腐横切结束后的回撤链路，恢复 legacy 的“先清刀再回 wait/prepare”行为。
- Work completed:
  1. 对照 legacy `cuttofo_xcore` 的 `knife_cut_action_server._return_to_prepare_waypoints()`，确认当前 CutTofo 已有等价的 inverse-step 回撤几何。
  2. 将 `tofu_cut_round_params.yaml` 中 `round_1.return.skip_return_anchor` 与 `round_2.return.skip_return_anchor` 改为 `false`，恢复切后 cartesian return。
  3. 在 `cut_round_path.py` 中抽出 `return_to_prepare_offsets()`，让回撤偏移可直接复用并用于诊断。
  4. 在 `tofu_cut_round_workflow.py` 中补充 return 分支日志，打印 cut end pose、offset、extra offset、return target，便于现场判断是否先清刀后再 MoveJ。
  5. 完成 `cuttofo_skill_common` 与 `cuttofo_skill_tofu_cut_round` 定向构建验证。
- Business logic impact:
  - 豆腐横切第 1/2 轮结束后的控制顺序恢复为：切完停左侧末端 -> 先按 inverse-step + extra offset 做右移清刀 -> 再 MoveJ 到 wait pose -> 后续由下一次 prepare 回到 prepare 位。
- Problems encountered:
  1. 当前配置曾因 `setFcCoor(world)` 网络错误把 `skip_return_anchor` 临时设为 `true`，导致整段安全回撤被跳过。
  2. 现场仅凭机械臂运动观察，很难区分“直接回 wait”还是“先做过短回撤再回 wait”。
- Resolution:
  - 恢复 return 分支并补足日志可观测性；若后续 RT return 再触发同类网络错误，后手方案是切换到已有 `use_nrt_cartesian`，而不是再次跳过回撤。
- Verification:
  - `python3 -m py_compile` 覆盖相关 Python 文件通过。
  - `colcon build --base-paths ... --packages-select cuttofo_skill_common cuttofo_skill_tofu_cut_round --symlink-install` 通过。
- Unverified items:
  - 尚未完成真机验证，仍需确认 RT cartesian return 在现场是否稳定。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_cut_round/config/tofu_cut_round_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/trajectory/cut_round_path.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_cut_round/cuttofo_skill_tofu_cut_round/tofu_cut_round_workflow.py`
- Next steps:
  - 真机单阶段执行 `prepare:first_cut -> cut_round:round_1`，确认先右移清刀再回 wait pose。
  - 若 RT return 失败，切到 `return.use_nrt_cartesian: true` 继续验证，而不是回退到 `skip_return_anchor: true`。

## 2026-06-07 17:10 CST

- Objective: 将豆腐阶段 7 竖切逻辑完整迁移到当前 CutTofo vertical-cut skill，对齐 legacy `phase7_third_cut`。
- Work completed:
  1. 梳理 current orchestrator -> `/tofu_vertical_cut/execute` -> `tofu_vertical_cut_workflow.execute_vertical_cut()` 的调用链，确认无需改 action 契约与阶段编排。
  2. 对照 legacy `knife_cut_action_server._execute_phase7_cut()`，将当前 vertical-cut workflow 收紧为四段：`seg1 upper cuts -> mid_push -> seg2 lower cuts + last retract -> tail_push`。
  3. 保留 `build_vertical_cut_waypoints()` 负责基础 `cut -> retract -> next_anchor` 骨架，把中段推刀与尾推继续留在 workflow 层显式下发 RT motion。
  4. 将默认 profile 参数切回 legacy phase7 语义：`force_rt_position: true`、`cycles: 11`、`cut_move: 0.058`、`step_z: -0.005`、`push_lift_speed`、`mid_push_speed`、`push_tail_speed`、`tail_move_cut_speed` 等。
  5. 在 workflow 中补充阶段日志，方便现场区分 seg1 / mid_push / seg2 / tail_push 的执行进度。
  6. 完成 `cuttofo_skill_tofu_vertical_cut` 定向语法检查与构建验证。
- Business logic impact:
  - 豆腐阶段 7 竖切不再维护一套“近似 phase7”的新逻辑，而是正式回到 legacy 语义：上半段竖切、中段推刀、下半段竖切+末次 retract、尾推，且默认全程走 RT Cartesian position 模式。
- Problems encountered:
  1. 当前 vertical-cut 配置字段名与 legacy 存在漂移，容易造成现场调参时“名字相近但语义不一致”。
  2. 原 workflow 的中段/尾推拆分方式与 legacy 不完全一致，存在维护第二套 phase7 语义的风险。
- Resolution:
  - 收紧 workflow 段落顺序并统一默认配置命名/数值，直接以 legacy phase7 为准。
- Verification:
  - `python3 -m py_compile` 检查 `tofu_vertical_cut_workflow.py`、`tofu_vertical_cut_config.py`、`tofu_vertical_cut_node.py` 通过。
  - `colcon build --base-paths ... --packages-select cuttofo_skill_tofu_vertical_cut --symlink-install` 通过。
- Unverified items:
  - 尚未做真机竖切验证，仍需确认 mid push 与 tail push 的现场效果与 legacy 一致。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_vertical_cut/cuttofo_skill_tofu_vertical_cut/tofu_vertical_cut_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_vertical_cut/config/tofu_vertical_cut_params.yaml`
- Next steps:
  - 真机手动执行 `prepare:after_rotation_1 -> vertical_cut:default`，确认阶段 7 的四段动作与 legacy 一致。
  - 若现场仍出现 phase7 行为偏差，优先比较 legacy `_execute_phase7_cut()` 的段落顺序与当前参数，而不是先改 orchestrator。

## 2026-06-07 17:35 CST

- Objective: 迁移 phase6 独立视觉参数覆盖能力，让第三次放刀前的感知参数改为 perception config 驱动而不是 orchestrator 硬编码。
- Work completed:
  1. 在 `tofu_perception_params.yaml` 中新增顶层 `phase6_vision` 配置区，语义对齐 legacy `cutting.phase6_vision`，并注明“未指定字段回退到默认 `tofu_perception_node.ros__parameters`”。
  2. 新增 `tofu_perception_config.py`，集中读取 perception YAML，并提供 `runtime_override("phase6")`，负责默认参数合并与可运行时下发字段过滤。
  3. 改造 `workflow_runner.py` 的 `_begin_perception_override()`，移除 `vision_override == "phase6"` 的硬编码参数列表，改为从 perception config 读取 override 后组装 `SetParameters` 请求。
  4. 将 `tofu_workflow_no_approach_params.yaml` 的第三次放刀 prepare 步骤补齐 `vision_override: phase6`，与默认 workflow 保持一致。
  5. 完成 `python3 -m py_compile` 与 `colcon build --base-paths ... --packages-select cuttofo_skill_tofu_perception cuttofo_orchestrator --symlink-install` 验证。
- Business logic impact:
  - phase6/第三次放刀前的视觉参数切换仍通过 orchestrator 的 `APPLY_PARAMS -> SetParameters(/tofu_perception_node)` 时序执行，但 override 数据源已从 Python 常量迁回 perception YAML。
  - phase1/phase2 继续使用默认 `tofu_perception_node.ros__parameters`；只有 `vision_override: phase6` 的 prepare 步骤会切到独立 phase6 视觉参数集合。
- Problems encountered:
  1. 当前 CutTofo 已有 phase6 override 语义，但来源分散在 orchestrator Python 内，现场调参不可见。
  2. `tofu_perception_params.yaml` 原先没有 phase6 独立参数区，也没有显式 fallback 语义。
- Resolution:
  - 把 phase6 参数维护入口收口到 perception config，并在 orchestrator 侧只保留“读取配置并下发”的职责。
- Verification:
  - `python3 -m py_compile` 覆盖 `workflow_runner.py` 与 `tofu_perception_config.py` 通过。
  - `colcon build --base-paths /home/tbl/Project/cucumber/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo --packages-select cuttofo_skill_tofu_perception cuttofo_orchestrator --symlink-install` 通过。
- Unverified items:
  - 尚未在真机/运行中的 ROS graph 上确认 phase6 prepare 前 `SetParameters` 的实际下发值与 `tofu_perception_node` 当前参数状态完全一致。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_perception_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/cuttofo_skill_tofu_perception/tofu_perception_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_runner.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_no_approach_params.yaml`
- Next steps:
  - 启动节点栈后执行 phase6 对应的 `prepare:after_rotation_1`，确认日志里显示 config-driven `vision_override='phase6'(... params)`。
  - 用 `ros2 param get /tofu_perception_node ...` 或日志确认 phase6 的 OBB 百分位与 depth/median 等参数已切换。

- Follow-up:
  - 复查 legacy `phase6_prepare` 后，确认 phase6 不只是视觉过滤参数不同，prepare 目标点偏移 `offset_a` / `vertical_offset` 也应一并切换；当前已将这两个字段补入 phase6 override，由 `tofu_perception_node` 运行时更新并驱动 `tcp_target`。
  - 真机全流程启动时发现 `tofu_perception_params.yaml` 被 ROS 2 当作 `--params-file` 直接加载，因此顶层不能混入 `phase6_vision` 这类非节点参数；现已将 override 拆到独立 `tofu_perception_overrides.yaml`，恢复 launch 可解析性。

## 2026-06-07 14:35 CST

- Objective: 清理 cucumber 工作区的环境卫生问题，切断旧 tofu 工作区污染，并把运行时 SDK / 模型路径收敛到当前工作区。
- Work completed:
  1. 清理 `~/.bashrc` 中 FishROS 初始化块，删除对 `/home/tbl/Project/tofu/dexbot_ros2_ws/install/setup.bash` 的自动 overlay，只保留 `/opt/ros/humble/setup.bash`。
  2. 在 `dexbot_bottom_layer/ws_paths.py` 新增 `linkerbot_sdk_src_dir()`，作为 linkerbot SDK 源码目录的统一解析入口。
  3. 收紧 `lbot_api.py` 的 `.so` fallback 搜索逻辑，移除从任意 `build/` / `install/` 推导其他工作区源码树的兜底行为，仅保留当前工作区 `ws_paths.lbot_python_dir()`。
  4. 将 `src/gui/main.py`、`dexbot_toolbox/gui/arm_hand_gui.py`、`cuttofo_skill_common/arm/xcore_sdk_paths.py`、`CutTofo/ros/xcore_phase1_paths.py`、`CutTofo/ros/xcore_follow_tcp_chain_node_movej.py` 统一改为复用 `dexbot_bottom_layer.ws_paths` 解析当前工作区内的 linkerbot / xCore SDK 路径。
  5. 将 `sam3_detector_node.py` 的 `model_path` 默认值改为当前工作区内的 `~/Project/cucumber/dexbot_ros2_ws/models/sam3`，并支持 `DEXBOT_SAM3_MODEL_PATH` 显式覆盖。
  6. 将 `cuttofu_vision/config/vision_params.yaml`、`cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml`、`dexbot_bottom_layer/config/perception_params.yaml` 中的 SAM3 模型路径从 `/home/tbl/Project/models/sam3...` 改为当前 cucumber 工作区路径。
  7. 顺手清理 GUI 文档/服务中的旧工作区引用：修正 `src/gui/README.md` 与 `src/gui/web/dexbot-web.service` 中残留的 `/home/tbl/Project/tofu/dexbot_ros2_ws`。
  8. 在纯净 ROS 环境下重新构建 `dexbot_bottom_layer`、`dexbot_middle_layer`、`dexbot_toolbox` 以及 CutTofo skills / orchestrator / vision 相关包，刷新 install/setup 产物。
- Business logic impact: 无主业务逻辑变更；此次修改只影响运行环境与资源解析策略。业务上的含义是：cucumber 工作区恢复为默认不依赖外部 tofu 工作区的自足运行形态。
- Problems encountered:
  1. 直接在当前污染 shell 中重编译时，colcon 会把旧 tofu underlay 链进新的 install/setup 产物，导致即使 `~/.bashrc` 已清理，`source install/setup.bash` 仍继续把 tofu 路径注回环境。
  2. CutTofo skills / orchestrator / vision 这些包不是根工作区自动发现构建，必须继续走 `CutTofo/scripts/build_skills.sh` 与 `build_cuttofo.sh` 的 `--paths` 显式构建链。
- Resolution:
  - 改为在 `env -i` 的纯净 shell 中，只 source `/opt/ros/humble/setup.bash` 后执行重编译，确保新的 install/setup 不再记录 tofu underlay。
  - 对 skills 相关包继续使用仓内已有的显式构建脚本，而不是依赖根级 `--packages-select`。
- Verification:
  - `env -i ... bash --rcfile ~/.bashrc -ic 'source install/setup.bash && ...'` 检查环境变量后，`AMENT_PREFIX_PATH`、`COLCON_PREFIX_PATH`、`CMAKE_PREFIX_PATH`、`PYTHONPATH`、`LD_LIBRARY_PATH` 已不再包含 `/home/tbl/Project/tofu/dexbot_ros2_ws`。
  - `python3` 验证 `dexbot_bottom_layer.__file__`、`linkerbot_sdk_src_dir()`、`xcore_sdk_root()`、`lbot_api.LibraryLoader.get_library_path()` 均命中 cucumber 工作区路径；`liblbot_api.so` 当前从 `cucumber/build/.../liblbot_api.so` 加载，不再来自 tofu。
  - `rg -n "/home/tbl/Project/tofu/dexbot_ros2_ws|/home/tbl/Project/models/sam3" src ~/.bashrc` 已无运行时相关残留；仅剩少量已同步修正的 GUI 文档/服务引用。
  - 纯净环境重建通过：`dexbot_bottom_layer`、`dexbot_middle_layer`、`dexbot_toolbox`、CutTofo skills、`cuttofu_vision`、`cuttofo_orchestrator`。
- Unverified items:
  - 尚未在真机上重新验证 `skills_bringup` / `tofu_perception.launch.py` / `prepare` / `cut_round`，因此还不能确认此前 `setFcCoor(world)` 网络错误是否已因环境收口而消失。
  - 当前默认 SAM3 模型路径已改为工作区内 `models/sam3`；若本地实际模型尚未放入该目录，则运行前仍需显式提供 `DEXBOT_SAM3_MODEL_PATH` 或补齐仓内模型目录。
- Files changed:
  - `/home/tbl/.bashrc`
  - `src/dexbot_bottom_layer/dexbot_bottom_layer/ws_paths.py`
  - `src/dexbot_bottom_layer/dexbot_bottom_layer/lbot_catch/arm_api/Python/lbot/lbot_api.py`
  - `src/dexbot_middle_layer/dexbot_middle_layer/sam3_detector_node.py`
  - `src/dexbot_middle_layer/dexbot_middle_layer/vision/pipeline/sam3_detector.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_vision/config/vision_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml`
  - `src/dexbot_bottom_layer/config/perception_params.yaml`
  - `src/gui/main.py`
  - `src/dexbot_toolbox/dexbot_toolbox/gui/arm_hand_gui.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/arm/xcore_sdk_paths.py`
  - `src/dexbot_middle_layer/CutTofo/ros/xcore_phase1_paths.py`
  - `src/dexbot_middle_layer/CutTofo/ros/xcore_follow_tcp_chain_node_movej.py`
  - `src/gui/README.md`
  - `src/gui/web/dexbot-web.service`
- Next steps:
  - 在新终端中只执行 `source /opt/ros/humble/setup.bash` 和 `source /home/tbl/Project/cucumber/dexbot_ros2_ws/install/setup.bash`，再跑真机链路复验。
  - 优先复测 `skills_bringup`、`tofu_perception.launch.py`、`ExecuteTofuPrepare`、`ExecuteTofuCutRound`，观察 `setFcCoor(world)` 是否仍报连接错误。
  - 若用户坚持“资源自足”包含模型文件本体，则下一步需要决定是否将 `models/sam3` 正式 vendoring 到仓内，或改成统一的外部模型配置入口。

## 2026-06-07 12:43 CST

- Objective: 收敛 CutTofo 豆腐视觉几何职责边界，消除 prepare/visualizer/tracker 对 perception 已发布 tofu 几何的重复计算与重复参数面。
- Work completed:
  1. `tofu_prepare_workflow.py` 改为在 `use_vision=true` 时直接消费 perception 发布的 `tofu.tcp_target`，不再从 `top_corners` 本地重算 tofu TCP。
  2. `VisionGeometryTracker` 去掉 `offset_a`、`vertical_offset`、`offset_x` 的本地几何所有权，`configure()` 仅保留非几何等待/筛选配置；当消息缺失 `tcp_target` 时不再本地补算而是视为无效输入。
  3. `task_visualizer_node.py` 去掉从 corners fallback 重算 TCP 的逻辑，改为缺失 perception TCP 时仅告警并跳过 TCP/edge 相关 marker。
  4. `capture_tofu_sauce_target.py` 中的 `VisionGeometryTracker` 构造移除 tofu 视觉 offset 注入，保持 sauce pour 仅基于豆腐几何派生任务目标。
  5. `tofu_prepare_node.py`、`tofu_prepare_config.py`、`tofu_prepare_params.yaml` 删除 prepare 侧 `vision_offset_a`、`vision_vertical_offset`、`vision_offset_x` 及相关 profile 覆盖，视觉几何参数收敛到 perception 配置。
  6. `ExecuteTofuPrepare.action` 删除 `offset_a`、`vertical_offset` 字段，prepare action 不再暴露豆腐视觉几何覆盖入口。
  7. 清理 `vision_geometry_tracker.py` 中已失效的几何 helper import，并同步修正文档 `启动指令.md` 中旧 prepare action 示例，移除已删除字段。
  8. 重新构建并通过验证以下包：`cuttofo_skill_interfaces`、`cuttofo_skill_tofu_prepare`、`cuttofo_skill_tofu_perception`、`cuttofo_task_visualizer`、`cuttofo_skill_sauce_pour`。
- Business logic impact: 豆腐主链路进一步固化为“通用/独立 vision 输出 -> `tofu_perception_node` 负责 tofu 视觉几何 -> prepare / visualizer / sauce-pour 等下游只消费感知结果或派生任务几何”；prepare 不再是第二个 tofu TCP 几何计算器。
- Problems encountered:
  1. prepare、shared tracker、task visualizer 之间长期存在“消费 perception 输出后再次从 corners 重算 tofu TCP”的职责外泄。
  2. prepare 配置与 action 接口仍保留一套重复的视觉 offset 参数，造成视觉几何来源分裂。
  3. 文档和少量调用示例仍引用旧 action 字段。
- Resolution:
  - 将 tofu 视觉 TCP/edge/corners 的所有权统一收敛到 perception 发布契约；下游只读取，不再重算。
  - 删除 prepare 侧重复视觉 offset 参数和 action 字段，并同步修正文档示例。
- Verification:
  - `bash src/dexbot_middle_layer/CutTofo/scripts/build_skills.sh --paths src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_interfaces src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_task_visualizer src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_sauce_pour`
  - 构建结果：5 个受影响包全部通过。
  - 静态搜索确认 prepare 路径与 task visualizer 路径已不再持有旧的 tofu TCP fallback 入口。
- Unverified items:
  - 尚未做真机/RViz 运行验证，仍需确认 perception 发布的 `tcp_target` 与 prepare / visualizer 实际消费结果完全一致。
  - 尚未继续处理旧 `cuttofo_xcore` 路径中的同类 prepare 重算模式；当前仅完成 CutTofo skills 主链路收敛。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/perception/vision_geometry_tracker.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_node.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_task_visualizer/cuttofo_task_visualizer/task_visualizer_node.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_sauce_pour/cuttofo_skill_sauce_pour/capture_tofu_sauce_target.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_interfaces/action/ExecuteTofuPrepare.action`
  - `src/dexbot_middle_layer/CutTofo/启动指令.md`
- Next steps:
  - 启动 perception + prepare + visualizer 真机链路，确认下游显示/执行与 perception 发布的 `tcp_target` 完全一致。
  - 如需继续收敛历史路径，再处理 `cuttofo_xcore` 中 prepare 侧同类重算与重复参数问题。
  - 若 GUI 手控继续报错，顺着本地 SDK 继续排查运行时依赖和 CAN/设备层通信。

## 2026-06-07 09:20 CST

- Objective: 对比当前 constrained_obb 与 legacy/xcore 视觉链路，收口参数并排查真机启动后 SAM3 与 tofu marker 不显示的问题。
- Work completed:
  1. 端到端对比当前 workspace 与 legacy/xcore 的豆腐视觉链路，确认两边都在使用 `corner_mode: constrained_obb`，但 constrained_obb 参数存在明显偏差。
  2. 将当前测试链路中的 constrained_obb 参数向 legacy 收口，在 `tofu_perception_params.yaml` 与 `tofu_vision_params.yaml` 中统一修改：
     - `obb_margin: 0.003`
     - `obb_depth_median_frames: 1`
     - `obb_bounds_top_keep_ratio: 0.8`
     - `obb_bounds_u_percentile_low/high: 2.0 / 98.0`
     - `obb_bounds_v_percentile_low/high: 2.0 / 98.0`
  3. 指导用户启动完整链路 `cuttofo_skill_tofu_perception/tofu_perception.launch.py`，并基于现场 `ros2 node list` / `ros2 topic` / `ros2 param` 输出排查为何无检测、无 marker。
  4. 确认 `tofu_perception_node`、`task_visualizer_node`、`sam3_detector_node`、`pose_estimator_node` 都已启动，`/cuttofu/perception/task_visualization` 与 `/cuttofu/perception/tofu_state` 也都存在，但 `tofu_state` 内容为空对象、marker 只在发 `DELETEALL` 清空帧。
  5. 进一步定位根因：`sam3_detector_node` 实际订阅的是 `/camera/color/image_raw`，而现场 RealSense 真正发布的是 `/camera/camera/color/image_raw`；因此 SAM3 拿不到彩色图像，后续 `detected_objects -> tofu_state -> marker` 全链路都为空。
  6. 在 `tofu_vision_params.yaml` 中显式补充 `image_topic: /camera/camera/color/image_raw`，强制绕过错误的旧参数继承/默认分支，避免 SAM3 继续订阅无发布者的话题。
  7. 同时确认现场 prompt 链路状态：`/cuttofu/vision/text_prompt` 上已经是 `ridged_tofu`，但 `sam3_detector_node` 的静态参数仍保留 `text_prompt: cargo truck`；说明提示词动态发布链路是通的，真正阻断点是彩色图订阅错误，而不是 tofu_perception 没发 prompt。
- Business logic impact:
  - 豆腐独立感知测试链路的 constrained_obb 参数已进一步向 legacy 版本收口，便于做同口径真机效果比较。
  - 当前链路仍保持 `cuttofu_vision -> tofu_perception_node -> task_visualizer_node` 的分层；这次排查确认“无检测/无 marker”不是感知层逻辑错误，而是 SAM3 输入彩色图话题配置错误导致上游空转。
- Problems encountered:
  1. 用户启动完整链路后，RViz 中看不到豆腐 marker，主观上认为 SAM3 没有开始检测。
  2. 现场同时存在 `/camera/color/image_raw` 与 `/camera/camera/color/image_raw` 两套命名历史，但当前这次启动里只有后者有 publisher。
  3. `sam3_detector_node` 运行时仍带有旧的 `image_topic: /camera/color/image_raw`，覆盖了 `camera_backend: realsense` 的预期行为，导致 SAM3 订错话题却没有显式崩溃。
- Resolution:
  - 通过 `ros2 node info`、`ros2 topic info -v`、`ros2 param dump/get`、`ros2 topic echo --once` 逐层排查，确认上游空检测是因为 SAM3 未收到 RealSense 彩色图。
  - 在 `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml` 中显式加上 `image_topic: /camera/camera/color/image_raw`，要求重编译并重启链路。
- Verification:
  - 已确认 `/camera/camera/color/image_raw` 有 publisher，而 `/camera/color/image_raw` 无 publisher。
  - 已确认 `/cuttofu/perception/tofu_state` 当前只发布空对象，`/cuttofu/perception/task_visualization` 当前只发布清空 marker，符合“上游无检测”的表现。
  - 已确认 `/cuttofu/vision/text_prompt` 上的动态提示词为 `ridged_tofu`，说明 prompt 发布链路本身正常。
  - 仍待用户按新 `image_topic` 配置重编译、重启后做真机复验。
- Unverified items:
  - 尚未拿到用户在修正 `image_topic` 后的新一轮真机结果，无法确认 marker 是否恢复、角点贴合是否随参数收口而改善。
  - 尚未决定是否要进一步清理 `cargo truck` 这一静态默认 `text_prompt`，避免启动早期短暂误检。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_perception_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml`
- Next steps:
  - 让用户按修正后的 `image_topic` 重新编译并重启完整链路，验证 SAM3 检测、tofu_state、marker 是否恢复。
  - 若恢复后角点仍不理想，继续拆分“参数收口效果”和“双重 constrained_obb 计算影响”两个因素。
  - 根据真机结果，决定是否顺手清理静态 `cargo truck` 默认 prompt，避免启动阶段的类别抖动。

## 2026-06-07 14:35 CST

- Objective: 彻底清理 cucumber 工作区的环境卫生，确保运行时不再依赖外部工作区或硬编码绝对路径，并修复 GUI 直接运行引导。
- Work completed:
  1. 移除 `~/.bashrc` 中 tofu 工作区自动 source，改为按需在当前 shell 手动 source cucumber workspace。
  2. 在 `dexbot_bottom_layer/ws_paths.py` 中新增 `linkerbot_sdk_src_dir()` 共享辅助函数。
  3. 将 `lbot_api.py` 中的 `.so` fallback 搜索逻辑大幅收紧，只保留通过 `dexbot_bottom_layer.ws_paths` 的显式路径，移除广泛扫描 `build/install` 祖先目录导致意外加载 tofu 工作区 `.so` 的漏洞。
  4. 统一 GUI、toolbox、xCore 路径辅助函数，全部改为引用 `dexbot_bottom_layer.ws_paths` 中的 `find_ws_root()`、`xcore_sdk_root()`、`linkerbot_sdk_src_dir()`，移除各处独立实现的重复查找逻辑。
  5. 清理所有 SAM3 模型路径配置，将外部 `/home/tbl/Project/models/sam3` 改为 cucumber 本地 `~/Project/cucumber/dexbot_ros2_ws/models/sam3`，同时新增 `DEXBOT_SAM3_MODEL_PATH` 环境变量显式覆盖路径。
  6. 修复 `src/gui/main.py` 直接运行引导，在导入 `dexbot_bottom_layer.ws_paths` 之前先用 `pathlib.Path` 自举将本地 `src/gui`、`src/dexbot_bottom_layer`、`src/` 加入 `sys.path`，保证 `python3 main.py` 在未 source ROS 环境时也能正常启动。
  7. 修正 `src/gui/web/dexbot-web.service` 与 `src/gui/README.md` 中残留的 tofu 工作区路径，统一改为 cucumber 工作区。
  8. 清理 `cuttofu_phase2.launch.py` 与 `viz_display.launch.py` 中的硬编码左臂标定 fallback 路径 `/home/tbl/Project/dexbot_ros2_ws/...`，改为 `find_ws_root() + "src/config/calib_left/..."`。
  9. 清理 `src/config1/calibration_result.yaml` 与 `src/config1/calibration_result_samples.json` 中残留的异地机器工作区路径 `/home/yishui/Yiping/dexbot_ros2_ws`，改为 cucumber 工作区本地路径。
  10. 清理 `src/gui/services/logger.py` 文档注释中的 tofu 工作区引用。
  11. 在干净 shell（`env -i` + 仅 `/opt/ros/humble/setup.bash` + cucumber `install/setup.bash`）中重新编译 `dexbot_bottom_layer`、`dexbot_middle_layer`、`dexbot_toolbox` 和全部 CutTofo 包，重新生成 `install/setup.bash` 使其不再链接 tofu 工作区。
  12. 验证干净 shell 环境变量 `AMENT_PREFIX_PATH`、`COLCON_PREFIX_PATH`、`CMAKE_PREFIX_PATH`、`PYTHONPATH`、`LD_LIBRARY_PATH` 不再包含 tofu 工作区路径。
  13. 验证 Python import `dexbot_bottom_layer.ws_paths` 与 `liblbot_api.so` 加载均指向 cucumber 本地路径，无 tofu 残留。
  14. 验证 GUI `main.py` 直接 `python3 main.py` 能正常完成全部导入（未启动 Tk 主循环，仅做导入链路验证）。
- Business logic impact: 无，纯环境卫生清理。
- Problems encountered:
  1. 初次在干净 shell 验证环境时，发现 `install/setup.bash` 仍带 tofu underlay 前缀链，根因是之前构建时 shell 已 source 过 tofu 工作区。
  2. GUI `main.py` 在直接源码树执行时，导入 `dexbot_bottom_layer.ws_paths` 失败，需要在导入前自举将工作区 `src/` 加入 `sys.path`。
  3. `cuttofu_phase2.launch.py` 与 `viz_display.launch.py` 中左臂标定文件 fallback 仍有硬编码绝对路径 `/home/tbl/Project/dexbot_ros2_ws/src/config/calib_left/...`。
  4. `src/config1/` 下校准元数据残留异地机器路径 `/home/yishui/Yiping/dexbot_ros2_ws/...`。
- Resolution:
  - 清空当前 shell 的 tofu underlay，在 `env -i` 纯净环境下重新编译 cucumber 工作区。
  - 在 `src/gui/main.py` 最开头加入 `_bootstrap_workspace_sources()` 自举，先把本地 `src/gui`、`src/dexbot_bottom_layer`、`src/` 加入 `sys.path` 再导入 `dexbot_bottom_layer.ws_paths`。
  - 将两个 launch 文件的左臂标定 fallback 改为 `find_ws_root() + "src/config/calib_left/calibration_result_left.yaml"`。
  - 将 `src/config1/` 元数据路径改为 cucumber 本地等效路径。
- Verification:
  - 在干净 shell 执行 `source /opt/ros/humble/setup.bash && source install/setup.bash`，环境变量不再包含 tofu 路径。
  - Python 导入 `dexbot_bottom_layer.ws_paths` 与加载 `liblbot_api.so` 均指向 cucumber 本地路径。
  - `python3 -c 'import runpy; runpy.run_path("src/gui/main.py", run_name="__not_main__"); print("main.py import ok")'` 成功输出 `main.py import ok`。
  - `python3 -m py_compile` 对 `main.py`、`cuttofu_phase2.launch.py`、`viz_display.launch.py` 无语法错误。
  - CutTofo 包重编译成功（13 个包，0 错误）。
- Unverified items:
  - GUI `python3 main.py` 启动完整 Tk 主循环（当前仅验证导入链路）。
  - 真机启动 `skills_bringup`、`tofu_perception.launch.py`、`ExecuteTofuPrepare`、`ExecuteTofuCutRound` 验证 `setFcCoor(world)` 连接错误是否随环境清理而消失。
  - SAM3 模型文件实际位置（若 `~/Project/cucumber/dexbot_ros2_ws/models/sam3` 不存在，需放置模型文件或设置 `DEXBOT_SAM3_MODEL_PATH`）。
- Files changed:
  - `~/.bashrc`
  - `src/dexbot_bottom_layer/dexbot_bottom_layer/ws_paths.py`
  - `src/dexbot_bottom_layer/dexbot_bottom_layer/lbot_catch/arm_api/Python/lbot/lbot_api.py`
  - `src/dexbot_middle_layer/dexbot_middle_layer/sam3_detector_node.py`
  - `src/dexbot_middle_layer/dexbot_middle_layer/vision/pipeline/sam3_detector.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_vision/config/vision_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml`
  - `src/dexbot_bottom_layer/config/perception_params.yaml`
  - `src/gui/main.py`
  - `src/gui/web/dexbot-web.service`
  - `src/gui/README.md`
  - `src/gui/services/logger.py`
  - `src/dexbot_toolbox/dexbot_toolbox/gui/arm_hand_gui.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/arm/xcore_sdk_paths.py`
  - `src/dexbot_middle_layer/CutTofo/ros/xcore_phase1_paths.py`
  - `src/dexbot_middle_layer/CutTofo/ros/xcore_follow_tcp_chain_node_movej.py`
  - `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`
  - `src/cuttofo_xcore/launch/viz_display.launch.py`
  - `src/config1/calibration_result.yaml`
  - `src/config1/calibration_result_samples.json`
## 2026-06-07 16:05 CST

- Objective: 收口豆腐无拔刀工作流的启动职责边界，让 workflow 成为单入口完整装配点，并整理现场可直接执行的测试指令。
- Work completed:
  1. 将 `cuttofu_vision/launch/vision_bringup.launch.py` 收紧为纯 vision 入口，只保留 RealSense、SAM3、pose_estimator、legacy relay、`tofu_state_node`、相机画面，不再内部启动 `task_visualizer`。
  2. 将 `cuttofo_skill_tofu_perception/launch/tofu_perception.launch.py` 收紧为纯 perception 入口，只启动 `tofu_perception_node`，移除其中对 vision、RViz、marker-only visualizer 的嵌套启动职责。
  3. 重组 `cuttofo_orchestrator/launch/tofu_skills_bringup_no_approach.launch.py`，改为显式装配 `vision + tofu_perception + task_visualizer + tofu_prepare + tofu_cut_round + tofu_vertical_cut`，不再通过 perception launch 间接带起上游和可视化。
  4. 更新 `cuttofo_orchestrator/launch/tofu_workflow_execute_no_approach.launch.py` 说明，使其语义明确为“一键装配完整节点栈，并可选自动执行 orchestrator”。
  5. 回退 `tofu_prepare_node.py` 与 `tofu_prepare_workflow.py` 中此前加入的 `use_vision` 自动猜测逻辑，恢复为只按 action goal 显式字段执行，避免 skill server 越权替调用方决定视觉模式。
  6. 更新 `启动指令.md`，只保留两套现场入口：一套一键完整 workflow，一套 `run_orchestrator:=false` 的完整节点栈 + 手动 action 单阶段测试，并在 prepare 示例中显式加入 `use_vision: true`。
  7. 对上述改动执行 `python3 -m py_compile` 语法检查，并重新构建 `cuttofu_vision`、`cuttofo_skill_tofu_perception`、`cuttofo_task_visualizer`、`cuttofo_skill_tofu_prepare`、`cuttofo_orchestrator`，构建通过。
- Business logic impact:
  - 豆腐链路职责边界重新收口为：`vision_bringup` 只管上游视觉与相机画面，`tofu_perception.launch.py` 只管几何感知，`task_visualizer.launch.py` 只管可视化，`tofu_workflow_execute_no_approach.launch.py` / `tofu_skills_bringup_no_approach.launch.py` 作为唯一的整栈装配层。
  - `tofu_prepare` 的视觉使用权重新回到 orchestrator / 手动 action 调用方手中，prepare skill 不再依据 profile 和零位姿隐式改写调用语义。
- Problems encountered:
  1. 之前的中间态改动把 `tofu_perception.launch.py` 变成了 vision/RViz 的嵌套装配点，破坏了“感知节点只做感知”的职责边界。
  2. `tofu_prepare` 内部存在两层 `use_vision` fallback，会在调用方未显式给出 manual pose 时偷偷切回视觉模式，和当前架构目标冲突。
- Resolution:
  - 通过拆分 launch ownership、回退 prepare fallback、把完整装配显式上提到 orchestrator bringup，恢复单一职责边界。
- Verification:
  - `python3 -m py_compile` 已覆盖 6 个改动 Python/launch 文件，语法通过。
  - `colcon build --base-paths ... --packages-select cuttofu_vision cuttofo_skill_tofu_perception cuttofo_task_visualizer cuttofo_skill_tofu_prepare cuttofo_orchestrator --symlink-install` 通过，5 个包全部成功构建。
- Unverified items:
  - 尚未做真机级别的整栈启动验证，尚未确认 `run_orchestrator:=false` 下是否稳定同时出现相机画面、`tofu_perception_node`、`task_visualizer_node`、`rviz2` 与下游 skill servers。
  - 尚未再次执行手动 `prepare` action 验证当前日志是否明确显示 `use_vision=True` 并顺利进入 `waiting_tofu` / `computing_ik`。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_vision/launch/vision_bringup.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/launch/tofu_perception.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_skills_bringup_no_approach.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute_no_approach.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_node.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/启动指令.md`
- Next steps:
  - 在新终端中只 source ROS base + cucumber install，执行 `ros2 launch cuttofo_orchestrator tofu_workflow_execute_no_approach.launch.py run_orchestrator:=false`，确认完整节点栈是否按预期一次性拉起。
  - 手动发送 `prepare` action（显式 `use_vision: true`）验证视觉感知与 IK 链路。
  - 若整栈启动稳定，再执行默认 workflow 入口确认无拔刀全流程可直接复测。
