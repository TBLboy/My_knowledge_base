# Current Session

## Last Updated

- 2026-06-01 18:30 Local Time
- Update: 2026-06-01 — SAM3 prompt late-joiner fix: burst publish + safe default prompt

## Current Objectives

- [x] 架构调整：创建 `cuttofo_skill_cucumber_perception` 包，剥离黄瓜任务感知逻辑
- [x] 修复：感知包编译后 `lib/cuttofo_skill_cucumber_perception/` libexec 目录缺失导致 launch 崩溃
- [x] 修复：realsense 节点收到多层嵌套 launch arg 转发的 Warning 刷屏
- [x] 更新启动指南.md 适配新架构
- [x] **SAM3 动态 Prompt 重构**: skill 节点不再发布 prompt → 感知节点成为 prompt 的 sole publisher
  - `cucumber_perception_node` 在 startup 时 burst publish `text_prompt`（每100ms × 5s + 心跳每5s）
  - 从 `cucumber_hold_node`, `tofu_prepare_node`, `handle_approach_node` + workflow 移除 VisionPromptClient
  - `vision_params.yaml` 默认 prompt 从 `object` 改为 `__none__`（安全默认词，SAM3 检不出任何物体）
  - 实测验证通过：SAM3 正确收到 "cucumber" prompt，不再乱检测
- [ ] **新目标**：黄瓜全流程切割测试
      - 确认 cucumber_hold 左臂按压黄瓜
      - 确认 cucmber_workflow_execute 全流程各步正常

## Current Business Logic Position

- Main path: 黄瓜切割 4 步（A→B→C→D→E）— 已就绪，准备全流程测试
- Active branch: 暂无（即将开始黄瓜全流程测试）

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

- **Problem (已解决) — SAM3 prompt 硬编码**: vision 节点 `sam3_detector_node` 的 `text_prompt` 固定为 `cucumber`，且 prompt 发布散落在多个 skill 节点中（cucumber_hold, tofu_prepare, handle_approach），形成多对一混乱依赖。
  - Root cause: prompt 发布权散落在技能节点，导致任意技能的启停都可能互相干扰 prompt。
  - Resolution: 感知节点成为 sole prompt publisher：
    1. `cucumber_perception_node` 在 startup 时 burst publish prompt（每100ms × 5s + 心跳每5s）
    2. 从 `cucumber_hold_node`, `tofu_prepare_node`, `handle_approach_node` + `handle_approach_workflow.py` 移除全部 `VisionPromptClient` / `schedule_startup_prompt` / `publish_prompt` 代码和参数声明
    3. 各 config YAML 和 config.py 移除 prompt 相关字段
    4. `vision_params.yaml` 默认 prompt 从 `object` 改为 `__none__`（安全默认词，SAM3 检不出任何物体）
  - 实测验证：SAM3 正确收到 "cucumber" prompt，不再乱检测 ✓

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
- `cuttofu_vision/config/vision_params.yaml` — 移除 `detect_cucumber` 参数段；`text_prompt` 从 `cucumber` → `object`
- `cuttofu_vision/launch/vision_bringup.launch.py` — 移除 detect_cucumber_node
- `cuttofu_vision/cuttofu_vision/detect_cucumber_node.py` — 标记 DEPRECATED
- `cuttofo_orchestrator/launch/cucumber_workflow_execute.launch.py` — include perception launch
- `cuttofo_orchestrator/package.xml` — 加 exec_depend perception + vision
- `启动指南.md` — 全流程变两终端，右臂/左臂测试用 perception launch

### SAM3 动态 Prompt 重构 (2026-06-01)
- `cuttofo_skill_cucumber_perception/cucumber_perception_node.py` — startup 时 publish prompt
- `cuttofo_skill_cucumber_hold/cucumber_hold_node.py` — 移除 VisionPromptClient + publish_prompt
- `cuttofo_skill_cucumber_hold/cucumber_hold_config.py` — 移除 prompt 参数
- `cuttofo_skill_cucumber_hold/config/cucumber_hold_params.yaml` — 移除 prompt 字段
- `cuttofo_skill_tofu_prepare/tofu_prepare_node.py` — 移除 VisionPromptClient + publish_prompt
- `cuttofo_skill_tofu_prepare/tofu_prepare_config.py` — 移除 prompt 参数
- `cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml` — 移除 prompt 字段
- `cuttofo_skill_handle_approach/handle_approach_node.py` — 移除 VisionPromptClient
- `cuttofo_skill_handle_approach/handle_approach_workflow.py` — 移除 vision_prompt 参数 + publish_prompt
- `cuttofo_skill_handle_approach/handle_approach_config.py` — 移除 prompt 参数
- `cuttofo_skill_handle_approach/config/handle_approach_params.yaml` — 移除 prompt 字段（保留 perception 其他字段）

## Current State

- 黄瓜架构已拆分：`cuttofu_vision`(raw) → `cuttofo_skill_cucumber_perception`(perception) → skills → orchestrator
- 黄瓜全流程一键启动：`cuttofo_orchestrator cucumber_workflow_execute.launch.py`
- SAM3 prompt 机制已验证通过：burst publish → 正确切换检测目标
- 下一步：黄瓜全流程实物切割测试

## Next Steps

- [pending] 黄瓜全流程实物测试（左臂 hold + 右臂 cut）
