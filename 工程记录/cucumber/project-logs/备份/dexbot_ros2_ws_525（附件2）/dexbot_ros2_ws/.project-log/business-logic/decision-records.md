# Business Logic Decision Records

### 2026-05-30 — 新 Skill 架构替代遗留 ROS 节点

- Decision: 采用 ActionServer + ActionClient 模块化 Skill 架构替代遗留的
  recognition → monitor → follow 三节点串联模式。
- Context: 遗留架构节点耦合严重，单节点 2000+ 行，难以测试和维护。
- Alternatives considered:
  - 留在旧架构上修修补补。
  - 用行为树 (BehaviorTree.CPP) 重写。
  - 当前 Skill + Orchestrator 方案。
- Reason: Skill 架构保持 ROS Action 原生接口，模块职责单一，每个 skill 可独立
  debug，orchestrator 仅为薄层编排。
- Evidence: cucumber hold / prepare / cut_round 独立编译和测试通过。
- Impacted nodes: A, B, C, D, E
- Impacted edges: A→B, B→C, C→D, D→E
- Status: active

### 2026-05-30 — 迁移工作空间到纯英文路径

- Decision: 从 /home/tbl/Project/切黄瓜项目跟踪/ 迁移到
  /home/tbl/Project/cucumber/。
- Context: ROS2 Humble rosidl 适配器对含中文字符的编译路径解析失败，导致所有
  使用 rosidl_generate_interfaces 的包无法编译。
- Alternatives considered:
  - 每次编译用 --build-base /tmp/dexbot_build 绕过（临时方案）。
  - 在路径中使用软链接。
  - 改名目录。
- Reason: 改名是最彻底的修复，不影响 cmake 路径解析。
- Evidence: 迁移后 colcon build 无需 --build-base，所有包编译通过。
- Impacted nodes: 全部
- Impacted edges: 全部
- Status: active

### 2026-05-30 — 左臂 SDK 直连 vs ROS 控制

- Decision: 左臂 cucumber_hold 使用 XcoreDirectExecutor 直连 SDK，不走
  xcore_controller_node。
- Context: 在遗留架构中，左臂的控制节点（follow_node）同样直连 SDK。新架构中
  prepare / cut_round 使用 ROS services。
- Alternatives considered:
  - 统一用 ROS services。
  - 统一用 SDK 直连。
- Reason: 左臂的 hold 运动简单（NRT MoveJ 到固定 TCP 点），直连 SDK 延迟更低
  且不需要额外启动 ROS controller 节点。右臂切割需要 RT 笛卡尔路径，ROS
  service 封装更合适。
- Impacted nodes: A, B, E
- Impacted edges: A→B, D→E
- Status: active
