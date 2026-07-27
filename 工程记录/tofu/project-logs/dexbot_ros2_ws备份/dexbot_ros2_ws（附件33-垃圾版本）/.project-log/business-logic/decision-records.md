# Business Logic Decision Records

## 2026-05-26 - 采用分阶段重构策略

- Decision: 重构按 4 个阶段执行：Phase1 清理 -> Phase2 提取共享 -> Phase3 拆分大文件 -> Phase4 补充测试
- Context: 代码库有 540+ 源文件、131,000+ 行代码，包含大量冗余、大文件和重复代码，一次完成风险过高
- Alternatives considered:
  - 一次性大型重构：风险太高，无法验证
  - 只拆分最大文件：治标不治本，重复代码仍然存在
  - 只加测试不改代码：重构安全网不足
- Reason: 分阶段可逐段验证降低风险；先清理减少干扰项，再提取共享消除重复，再拆分降低复杂度，最后加测试夯实安全网
- Evidence / Verification: 未验证（策略决策阶段）
- Impacted nodes: CodeBaseCurrentState, Phase1_Cleanup, Phase2_ExtractShared, Phase3_SplitMonoliths, Phase4_AddTests
- Impacted edges: 所有重构相关的 edge
- Status: active (已被 grill-me 讨论细化，见下文)

## 2026-05-26 (grill-me) - 重构策略细化：清理→底层→中层→高层

- Decision: 重构按 4 个阶段执行，采用自底向上顺序：Phase0 清理 → Phase1 底层整理 → Phase2 中层拆分 → Phase3 高层合并
- Context: 初始 4 阶段规划（清理→提取共享→拆分→测试）经 grill-me 讨论后细化为更关注代码组织层次的新阶段划分。V3 深度规划（9 Phase）过于庞大，本次聚焦于最小可行重构
- Reason:
  - 先清理死代码减少干扰
  - 底层保持稳定（原子控制器封装硬件 SDK，接口已成熟）
  - 中层是重构重心（skills 拆分、纯计算模块提取）
  - 高层合并（orchestrator + domain skill 替换 phase_manager）
  - 全程保持切豆腐行为不变
- Status: active

## 2026-05-26 (grill-me) - 唯一主线：cuttofo_xcore

- Decision: `cuttofo_xcore` 是唯一的切豆腐实现，删除 `cuttofo_lbot/`、`dexbot_high_layer/` 等其他变体
- Context: 代码库存在 3 个以上的切豆腐/切黄瓜实现，造成维护混乱
- Evidence: grep 全仓确认 cuttofo_xcore 不 import cuttofo_lbot；Phase1 拔刀的 3 个 CutTofo 节点进入保留清单
- Status: active

## 2026-05-26 (grill-me) - 底层不做大改

- Decision: `dexbot_bottom_layer/` 保持稳定，只删 `lbot_controller/` 旧 Lbot 控制器，不改包名、不动其他原子控制器
- Context: 底层封装了 xCore SDK、Linkerbot SDK，接口通过 ROS service 暴露，切豆腐通过 service call 使用
- Reason: 原子控制器是硬件抽象层，稳定可靠，改动风险大于收益；且底层代码与框架重构无直接关系
- Status: active

## 2026-05-26 (grill-me) - 感知服务合并为一个自足节点

- Decision: `tofu_perception_service` 合并 SAM3 检测 + pose_estimator 位姿估计 + tofu_state 状态跟踪为一个自足的 Resource Service 节点
- Context: 当前这三个节点独立运行，互相通过 ROS topic 通信。合并后减少内部 topic 延迟，逻辑更自足
- Reason: 感知管线是切豆腐的数据核心，合并为一个节点可简化调用链、降低延迟，且符合 V3 架构中 Resource Service 常驻运行的设计
- Status: active

## 2026-05-26 (grill-me) - detect_knife_skill 专用于拔刀

- Decision: `detect_knife_skill` 仅针对拔刀场景，不做通用物体检测。后续豆腐检测等场景另起 skill
- Context: 拔刀需要的检测（木质刀柄）和豆腐检测（几何特征）差异较大，合在一起会耦合
- Status: active

## 2026-05-26 (grill-me) - 运动 skill 拆分为 NRT 和 RT 两类

- Decision: 通用运动按通信模式拆分为 `arm_movej_skill`（NRT: MoveJ, MoveCartesian）、`arm_movelinear_skill`（NRT: 直线运动）、`arm_rtpath_skill`（RT: RT路径/TCP链跟随）三个独立节点
- Context: NRT 和 RT 的通信模式、超时处理、错误恢复完全不同，合在一个 skill 里会导致条件分支泛滥
- Status: active

## 2026-05-26 (grill-me) - cut_cycle_skill 内部调用 IK 库，不拆 skill

- Decision: `cut_cycle_skill` 内部调用 `prepare_pose_selector` 纯计算库做 IK 求解，不拆成独立的 `solve_ik_skill`
- Context: IK 求解是 cut_cycle 的内部步骤，没有其他 skill 需要独立调用它
- Reason: 遵循"不拆太细，skill 逻辑自足"原则
- Status: active

## 2026-05-26 (grill-me) - 新增 Domain Skill: tofu_cut_skill

- Decision: 在 Logic Skills 最上层新增 Domain 级 `tofu_cut_skill`，作为完整切豆腐工艺的封装
- Context: 按 V3 架构，完整调用链应为 Orchestrator -> Domain Skill -> Composite -> Atomic。当前规划跳过 Domain 层直接从 Orchestrator 调 Composite
- Reason: Domain Skill 可单独 launch 测试；High 层只需要调一个 skill，更薄；后续其他领域可复用底层 skills
- Status: active

## 2026-05-26 (grill-me) - 每个 Skill 必须有独立测试能力

- Decision: 每个 skill 都有自己的 launch 文件和 test launch，可独立启动和调试
- Context: V3 要求每个 skill 可独立测试。当前 phase_manager 只能跑完整 7 阶段
- Reason: 独立测试 = 独立验证 = 重构安全网
- Status: active

## 2026-05-26 - 保留现有 .project-log 内容不覆盖

- Decision: 已有 `.project-log/` 中的 GUI 双臂工作记录保留不变，只追加重构相关的内容
- Context: `.project-log/business-logic/main.md`、`graph.md`、`nodes.md`、`edges.md` 已有 GUI 双臂协作面板的业务逻辑
- Alternatives considered:
  - 清空重写：会丢失之前的业务逻辑记录
  - 新建分支 logic：与当前重构主题无关
- Reason: 保留完整历史，同时追加新内容，两不相扰
- Status: active

## 2026-05-26 - 使用 project-log 系统跟踪重构过程

- Decision: 使用 project-log 工程记录系统作为重构全过程的管理工具
- Context: 重构涉及多个阶段、多个包、多个文件，需要一个系统化的跟踪机制
- Alternatives considered:
  - 仅靠 git commit message：不够结构化
  - 靠外部文档：容易与代码脱节
- Reason: project-log 系统与代码库共存，支持进度跟踪、问题记录、决策留档
- Status: active
