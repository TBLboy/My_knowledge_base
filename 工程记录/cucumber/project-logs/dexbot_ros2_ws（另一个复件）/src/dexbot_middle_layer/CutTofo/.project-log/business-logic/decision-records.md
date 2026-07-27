# Business Logic Decision Records

## Decisions

### 2026-06-06 - Architecture Decision: Tick-Driven Orchestrator

- Decision: 使用 tick 驱动状态机作为 orchestrator 模式（非 behavior tree，非 SMACH）。
- Context: 需要一个轻量、可控的工作流顺序执行器。
- Alternatives considered:
  - SMACH（ROS 1 状态机库）：ROS 2 支持有限，且较重。
  - Behavior Tree：更灵活但复杂度更高。
  - Tick-driven state machine（已实现）：简单直接，易调试。
- Reason: 当前工作流是顺序线性流程，无需复杂分支。Tick 驱动状态机在 20Hz 下能够满足 operator wait、Action goal 异步通信等需求。代码量少，易于理解和修改。
- Evidence / Verification: 成功跑通豆腐完整流程。
- Impacted nodes: 全局（A-N 所有节点由 orchestrator 驱动）。
- Impacted edges: 全部 main edges。
- Status: active

### 2026-06-06 - Architecture Decision: Action-Based Skill Interface

- Decision: 每个 skill 作为独立的 ROS 2 Action Server。
- Context: 需要统一的接口让 orchestrator 调用各 skill。
- Alternatives considered:
  - 直接 ROS 2 Service：无反馈机制，无法支持长时间执行。
  - 自定义 TCP/UDP 协议：失去 ROS 生态兼容性。
- Reason: ROS 2 Action 原生支持 goal、feedback、result 三阶段模型，适合机械臂长时间运动任务。统一接口便于 orchestrator 统一调度。
- Evidence / Verification: 7 个 Action 全部实现并集成。
- Impacted nodes: 全局。
- Impacted edges: 全部。
- Status: active

### 2026-06-06 - Architecture Decision: Impedance Control for Cut_Round

- Decision: 水平切割（cut_round）使用阻抗控制，垂直切割（vertical_cut）使用位置控制。
- Context: 切割豆腐需要力控适应以避免压碎，垂直切割需要精确位置。
- Alternatives considered:
  - 全部阻抗控制：垂直切割可能位置精度不足。
  - 全部位置控制：水平切割可能压碎豆腐。
- Reason: 阻抗控制在水平切割时能够自适应豆腐硬度变化，垂直切割使用位置控制保证切透。
- Evidence / Verification: 当前实现已验证可用。
- Impacted nodes: D, G, J, Q.
- Impacted edges: C-D, F-G, I-J.
- Status: active

### 2026-06-06 - Architecture Decision: Direct xCore SDK Control

- Decision: 绕过 ROS 2 control，使用 xCore 直连 SDK 控制手臂运动。
- Context: xCore 工业臂的 SDK 提供直接的运动控制接口。
- Alternatives considered:
  - ROS 2 control + joint_trajectory_controller：需要额外适配层，可能丢失 SDK 原生功能。
- Reason: xCore SDK 原生支持阻抗控制、笛卡尔路径规划等功能，比通过 ROS 2 control 桥接更可靠。
- Evidence / Verification: 全部运动都通过 xCore SDK 调用。
- Impacted nodes: 全局。
- Impacted edges: 全部。
- Status: active

### 2026-06-11 - Left Handoff: Skill TCP → Flange + FLANGE:: Move

- Decision: 左臂交接在 skill 内用 `left_handoff.tcp_offset` 将 TCP 目标转为法兰 pose6，经 `move_cartesian(label=FLANGE::...)` 下发；控制器见 `FLANGE::` 时跳过 `ToolOffsetConfig`；**不读取** `src/config/tool_offset.yaml`。
- Context: IK 预检通过但真机不到点；用户要求与右臂 hook_lift 一致的业务/控制分离。
- Alternatives considered:
  - 同步全局 `tool_offset.yaml` 与 skill offset：违背 skill 参数自足。
  - 改用 direct executor 运动（sauce_pour 路径）：用户要求保留 ROS move + 候选选择架构。
  - 直接发 TCP 给 move_cartesian：与控制器 grasp 语义冲突。
- Reason: 规划在 TCP、执行在法兰，offset 单一来源；避免双重换算。
- Evidence / Verification: 代码已落地；**真机到位未验证**（2026-06-11 会话结束时报未解决）。
- Impacted nodes: second_cross_cut left_handoff
- Impacted edges: transfer → left_handoff
- Status: experimental（待真机 `err<5mm` 后改为 active）
