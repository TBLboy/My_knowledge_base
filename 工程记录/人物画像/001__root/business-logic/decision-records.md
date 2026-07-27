# Business Logic Decision Records

### 2026-07-20 - Separate Personal Growth Records From Project Records

- Decision: 在 `人物画像/` 下建立独立 `.project-log`，只记录人物画像维护和个人 AI 工作架构；不将其混入具体机器人项目的工程日志。
- Context: 本人希望先把人物画像作为后续长期工作基础，再优先讨论 AI 工作架构/Skills。
- Alternatives considered:
  - 直接将个人目标写入任一机器人项目的 `.project-log`。
  - 只维护一份非结构化人物画像文档。
- Reason: 个人职业系统跨越多个项目，需要独立的事实、决策和时间线；同时不污染各项目的业务逻辑。
- Evidence / Verification: 已存在 `人物画像-v1.md`，该目录此前无工程记录。
- Impacted nodes: P0-P6.
- Impacted edges: E-P0-P1 through E-P5-P6.
- Status: active.

### 2026-07-20 - Defer Resume Packaging Until Evidence Is Collected

- Decision: 项目成果凝练和简历表述作为 B3 延后分支，不在当前 AI 架构设计阶段执行。
- Context: 候选项目来源和个人真实贡献尚未逐项确认。
- Alternatives considered:
  - 立即根据工作区内容包装项目。
  - 放弃全部历史项目，只做新个人项目。
- Reason: 先建立诚信的事实边界，后续才能产出经得起技术追问的项目叙事。
- Evidence / Verification: 本人明确表示后续会补充项目材料；已确认工作区项目存在本人参与、学习和他人来源的混合情况。
- Impacted nodes: P5, P6.
- Impacted edges: E-P5-P6.
- Status: active.
