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
  - 若 GUI 手控继续报错，顺着本地 SDK 继续排查运行时依赖和 CAN/设备层通信。