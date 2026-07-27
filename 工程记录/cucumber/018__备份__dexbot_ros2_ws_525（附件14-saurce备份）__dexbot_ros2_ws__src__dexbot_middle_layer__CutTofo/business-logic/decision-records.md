# Business Logic Decision Records

## Decisions

### 2024-Q2 — 从单体重构为 Skill 包架构

- **Decision**: 将原来 `cuttofo_xcore` 单体的功能拆分为独立的 ROS2 skill 包
- **Context**: 原有单包架构难维护、难扩展、Action 接口不清晰
- **Alternatives considered**:
  - 保持单体：维护成本高
  - behavior tree：增加复杂度
- **Reason**: 每个技能独立为 ROS2 包 + Action 接口，封装清晰，可独立调试
- **Evidence / Verification**: Skills 可独立编译运行，Orchestrator 通过 Action client 编排
- **Impacted nodes**: All
- **Impacted edges**: All
- **Status**: active

### 2024-Q2 — 左臂使用 xCore SDK 直连

- **Decision**: 左臂控制使用 xCore SDK 直接调用（XcoreDirectExecutor），右臂使用 ROS service（XcoreArmAdapter）
- **Context**: 右臂需要给多个节点共享控制权，左臂只需一个节点控制
- **Alternatives considered**:
  - ROS service 封装：增加延迟和依赖
  - 统一使用 SDK 直连：右臂多节点场景复杂
- **Reason**: 简左臂控制路径，减少 ROS 中间层延迟
- **Status**: active

### 2024-Q2 — 视觉几何追踪 in-process 化

- **Decision**: Skills 内使用 in-process VisionGeometryTracker，替代独立的 tofu_state_node
- **Context**: tofu_state_node 通过 ROS topic 交互增加了延迟和同步问题
- **Reason**: 减少 ROS 通信开销，几何追踪更实时
- **Status**: active

### 2024-Q2 — 工作流使用 tick-driven 状态机

- **Decision**: TofuTaskOrchestrator 使用 tick-driven 状态机（workflow_runner.py），非 behavior tree
- **Context**: 工作流顺序固定（3 阶段 6 步骤），条件分支少
- **Reason**: 轻量、直观、易于调试
- **Status**: active
