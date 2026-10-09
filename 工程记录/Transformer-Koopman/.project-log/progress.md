# Progress

> 面向人的阶段进度摘要。维护规则：
> - **最新在最上**：按日期倒序排列，最新阶段段落位于文件顶部，旧段落依次向下。
> - **头部快照**：顶部“当前状态”区块是稳定入口，每次更新时覆盖，不追加旧版本。
> - **超限归档**：文件超过约 50-100 KB 时，把旧段落移动到 `.project-log/docs/archive/`，主文档只保留最近内容。
> - **单一事实源**：本文件是快速摘要；精确当前状态与下一步以 Project Log format 2 状态库、Git 账本与生成的 `handoff.md` 为准。
> - **机器文件不手工重排**：状态库、Git 账本与生成视图由运行时维护，不做手工重排或改写。

## 当前状态

- 当前阶段：阶段③ 论文撰写（DEC-025：理论路线优先，真机暂缓）
- 当前目标：GOAL-001 已按用户指令诚实收口（工具状态仍为 active；原因与缺陷见 DEC-045 / DEC-046）
- 当前任务：无（9 个任务全部 cancelled，状态库 rev 660）
- 当前状态：收口完成；论文修订清单已就绪但未开工
- 最近验证：`EV-GIT-REMOTE-SYNC-001`（远端 main = 25e400d，valid）；`EV-PHASE2-REVIEW-D1D4-001`（Main.tex `82855BACF1C9` / build/Main.pdf `8DFFC77A29FD`，12 页、0 overfull，valid）；`EV-PHASE2-ABLATION-STAGE01-001`（12 runs 消融，valid）
- 下一步：
  1. 论文修订按 `Transformer-Koopman/论文/新版本/GPT审查报告_独立核对与代码验证.md` §5 的 6 批 36 项执行，入口为批次 1（技术风险 T1/T2/T3/T5/T6/T7），不依赖任何实验。
  2. 待用户裁定：§VII 在 .tex 中的处置方式、免责声明唯一落点、`r` 与 `H_R` 的报告位置。
  3. 已登记框架缺陷 7 条（DEC-046 + `.project-log/docs/framework_defect_log_v1.md`）；在缺陷 1/2/3 修复前，本项目不再建立 evidence-gated 的 goal。

## 2026-10-08 阶段③ 收口与框架缺陷登记

- 状态：完成（用户裁定）
- 完成内容：9 个任务全部取消（TASK-001..TASK-009）；GOAL-001 诚实收口（8 项成功条件保留原文并逐条标记 `not-applicable`、`required_evidence` 清空）；新增 DEC-045（收口记录）、DEC-046（框架缺陷 7 条）与 `.project-log/docs/framework_defect_log_v1.md`。
- 验证与限制：`goal complete --id GOAL-001` 前后两次实测均被 `goal_gate` 拒绝；契约改写后仅剩 `high-risk goal lacks a valid independent review`，判定在不伪造/转写证据的前提下无法关闭，故工具状态保持 `active`。未伪造、未删除任何证据。
- 下一步：见上方“当前状态”。

<!--
旧段落按日期倒序向下追加；超过约 50-100 KB 时归档到
`.project-log/docs/archive/`，归档文件按日期可检索。
-->
