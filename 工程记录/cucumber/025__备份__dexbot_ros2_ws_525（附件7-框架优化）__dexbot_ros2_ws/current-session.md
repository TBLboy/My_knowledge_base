# Current Session

## Last Updated

- 2026-06-01 17:00 Local Time

## Current Objectives

- [x] 架构调整：创建 `cuttofo_skill_cucumber_perception` 包，剥离黄瓜任务感知逻辑
- [x] 修复：感知包编译后 `lib/cuttofo_skill_cucumber_perception/` libexec 目录缺失导致 launch 崩溃
- [x] 修复：realsense 节点收到多层嵌套 launch arg 转发的 Warning 刷屏
- [x] 更新启动指南.md 适配新架构
- [ ] **新目标**：复活豆腐切块全流程工作流
      - 更新 `tofu_workflow_execute.launch.py`：设置 CUTTOFO_WORKFLOW_CONFIG + 集成 vision/perception
      - 编译验证 handle_approach + vertical_cut 包
      - 分步测试：prepare → cut_round → vertical_cut → handle_approach
      - 全流程一键启动测试

## Current Business Logic Position

- Main path: 黄瓜切割 4 步（A→B→C→D→E）— 已完成架构重构
- New path: 豆腐切割 7 步（handle_approach → prepare → cut_round → prepare → cut_round → prepare → vertical_cut）— 待复活
- Active branch: 暂无（即将开始 tofu 流程修改）

## Current Business Logic Position

- Main path: 黄瓜切割 4 步（A→B→C→D→E）— 已完成架构重构
- New path: 豆腐切割 7 步（handle_approach → prepare → cut_round → prepare → cut_round → prepare → vertical_cut）— 待复活
- Active branch: 暂无（即将开始 tofu 流程修改）

## 已完成的修改

## 待完成（豆腐复活计划）

### Existing infra（已存在，无需创建）
- `tofu_workflow_execute.launch.py` — 编排启动文件 ✓
- `skills_bringup.launch.py` — 含 5 个 skill server ✓
- `tofu_workflow_params.yaml` — 3 阶段 7 步配置 ✓
- `handle_approach_server.launch.py` ✓
- `tofu_vertical_cut_server.launch.py` ✓
- `tofu_prepare_server.launch.py` + `tofu_cut_round_server.launch.py` ✓（黄瓜共享）

### 需要修改
1. **`tofu_workflow_execute.launch.py`** — 需加：
   - `SetEnvironmentVariable(name="CUTTOFO_WORKFLOW_CONFIG", value=tofu_workflow_yaml)`
   - `include_perception` / `enable_vision` 参数
   - `IncludeLaunchDescription` 包含 tofu_perception.launch.py（待创建）
   - 参考 cucumber_workflow_execute.launch.py 的结构统一
2. **新建 `cuttofo_skill_tofu_perception` 包** — 填补感知缺口：
   - `tofu_perception_node.py`：订阅 `pose_raw`，多帧平均，发布 `objects_with_pose`（`class_id: "tofu"`）+ `tofu_state`
   - `tofu_visualizer_node.py`：消费 `tofu_state` → RViz MarkerArray
   - `package.xml`, `setup.py`, `config/`, `launch/` 模板
   - 注：TCP 目标点由下游 `VisionGeometryTracker` 从角点自动推导，感知节点只需做多帧平滑 + class_id 重标
3. **编译验证** — handle_approach + vertical_cut + orchestrator + 新感知包
4. **分步测试** — 各 skill 单独验证（先 prepare → cut_round → vertical_cut → handle_approach，需先有视觉数据）
5. **全流程测试** — tofu_workflow_execute.launch.py 一键启动

### 注意点
- handle_approach 是第一步，需 vision 检测到刀把（当前无物理刀把时可在 yaml 中注释此步）
- tofu 流程共 2 次人工旋转豆腐等待点（operator_wait）
- tofu 流程无左臂 hold，纯右臂操作

## Problems And Resolutions

- **Problem (已修复)**: 新包 `cuttofo_skill_cucumber_perception` 编译后 `install/<pkg>/lib/<pkg>/` 目录未生成，ROS 2 launch 因 libexec 缺失报错。
  - Root cause: setuptools 59.6 + colcon `--symlink-install` 偶发不创建 `lib/<pkg>/` wrapper 目录。
  - Resolution: 手动创建目录并复制 wrapper。已记入启动指南 5a。

- **Problem (待解决) — 豆腐感知缺**: 当前 vision 管线中无节点发布 `class_id: "tofu"` 到 `/cuttofu/perception/objects_with_pose`。
  - 现状：`pose_raw` → `cucumber_perception_node` → `objects_with_pose`（硬编码 `class_id: "cucumber"`）
  - 下游 `VisionGeometryTracker`（tofu_prepare 内）默认 `class_filter="tofu"`，永远筛不到数据，超时失败。
  - 方案：新建 `cuttofo_skill_tofu_perception` 包，包含 `tofu_perception_node` + `tofu_visualizer_node`。
  - 只需多帧平滑 + class_id 重标，TCP 目标点由下游从角点自动推导。

## Verification

- `colcon build --symlink-install --paths ...` 3 包编译通过
- `ros2 pkg prefix cuttofo_skill_cucumber_perception` 返回正常
- `get_package_share_directory('cuttofo_skill_cucumber_perception')` 解析通过
- `ros2 launch cuttofo_orchestrator cucumber_workflow_execute.launch.py enable_vision:=false` — 5 节点全部启动成功（cucumber_perception_node, cucumber_hold_node, tofu_prepare_node, tofu_cut_round_node, tofu_task_orchestrator），无 libexec 错误

## Files Changed

### 新包
- `cuttofu_skills/cuttofo_skill_cucumber_perception/` — 完整新包
  - `package.xml`, `setup.py`, `resource/`, `config/cucumber_perception_params.yaml`
  - `launch/cucumber_perception.launch.py`
  - `cuttofo_skill_cucumber_perception/cucumber_perception_node.py`
  - `cuttofo_skill_cucumber_perception/top_face_geometry.py`
  - `cuttofo_skill_cucumber_perception/topics.py`

### 修改
- `cuttofu_vision/setup.py` — 移除 `detect_cucumber_node` entry point
- `cuttofu_vision/config/vision_params.yaml` — 移除 `detect_cucumber` 参数段
- `cuttofu_vision/launch/vision_bringup.launch.py` — 移除 detect_cucumber_node
- `cuttofu_vision/cuttofu_vision/detect_cucumber_node.py` — 标记 DEPRECATED
- `cuttofo_orchestrator/launch/cucumber_workflow_execute.launch.py` — include perception launch
- `cuttofo_orchestrator/package.xml` — 加 exec_depend perception + vision
- `启动指南.md` — 全流程变两终端，右臂/左臂测试用 perception launch

## Current State

- 黄瓜架构已拆分：`cuttofu_vision`(raw) → `cuttofo_skill_cucumber_perception`(perception) → skills → orchestrator
- 黄瓜全流程一键启动：`cuttofo_orchestrator cucumber_workflow_execute.launch.py`
- 豆腐复活计划已记录详情：
  - infra 基本完整（launch + yaml + 5 skill servers）
  - **关键缺口：无 `class_id: "tofu"` 的感知节点**，导致 `VisionGeometryTracker` 收不到视觉数据
  - 需要新包 `cuttofo_skill_tofu_perception` 填补

## Next Steps

- [pending] 新建 `cuttofo_skill_tofu_perception` 包（感知节点 + 可视化节点）
- [pending] 更新 `tofu_workflow_execute.launch.py` — 加 CUTTOFO_WORKFLOW_CONFIG + vision 集成
- [pending] 编译验证
- [pending] 分步测试：prepare → cut_round → vertical_cut → handle_approach
- [pending] 全流程一键启动豆腐切块
