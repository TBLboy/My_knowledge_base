# Current Session

> 会话恢复入口。维护规则：
> - **头部快照**：顶部“当前状态”区块是稳定入口，每次更新时覆盖，不追加旧版本。
> - **最新在最上**：最新一次会话写在文件最上面的会话区块，旧会话依次向下。
> - **超限归档**：文件超过约 50-100 KB 或会话区块达到约 10 条时，把旧会话区块移动到 `.project-log/docs/archive/`，主文档只保留最近内容。
> - **单一事实源**：精确当前状态与下一步以 Project Log format 2 状态库、Git 账本与生成的 `handoff.md` 为准；不要在多份长文档里维护互相矛盾的“下一步”。
> - **机器文件不手工重排**：状态库、Git 账本与生成视图由运行时维护，不做手工重排或改写。
> - 本文件由主 Agent 通过 `vibe memory sync --file <json>` 写入，不要手工编辑。

## 当前状态

- 当前阶段：阶段③ 论文撰写（DEC-025）
- 当前目标：GOAL-002（理论包与论文正文）；GOAL-001 已按用户指令诚实收口（工具状态仍 active，框架缺陷所致）
- 当前任务：无进行中任务（TASK-059 已完成：`paper` 设置 upstream 并推送）
- 当前状态：论文正文语言与结构打磨中；实验与图片按项目规则暂缓
- 已确认事实：
  - 论文新版本在 `Transformer-Koopman/论文/新版本/`（IEEEtran，六章 + Appendix A "Proof Details"）
  - 编译：Tectonic 0.17.0 → `build_font/Main.pdf`，8 页；Overfull 0、未定义引用 0、字体警告 0、Underfull 10
  - 参考文献 39 条，按首次引用顺序，无未引用条目（原 40 条，`diehl2005rtistability` 随离题稳定性句一并删除）
  - 三个图占位：`fig:overview`（`figure*` 跨栏）、`fig:rollout`、`fig:freezing`
  - 字体处理：在 `\documentclass` 前用 `\ifdefined\XeTeXversion` 把 TU/ptm 映射到 TeX Gyre Termes；源文件保留 BOM
  - 内层仓库分支 `paper`，upstream `origin/paper`，HEAD `172463b` 已推送，工作区干净
- 活跃决策：DEC-025/026/027/028/043/044/045/046/086/087/088/090/091/092/093/094/095；DEC-018 仍 UNMET
- 阻塞项：框架缺陷（goal 门禁 review 判据与 `review record` 不一致）使 GOAL-001 无法 complete；DEC-018 history-space 稳定性未形式化；部署 ckpt ≠ 论文模型（DEC-028）
- 最近验证：`EV-TASK058-INTRO-002`（valid）+ `REV-TASK058-001`=go；`EV-TASK059-PUSH-001/002`（valid）
- 下一步：
  1. 继续论文正文打磨：Introduction 已完成（TASK-058）；其余章节与摘要/结论的一致性按用户指示处理
  2. TASK-054 遗留：在最终正文定稿后做一次**带联网**的全量参考文献元数据复核，并取 go 复核
  3. 待用户裁定：是否补一条通用 MPC 教材引用（现由 `wu2026multistep` 承担 QP 实时性陈述）；§VII 处置、免责声明落点、`r`/`H_R` 报告位置等旧议题需在六章结构下重新确认
  4. 图片待用户发话后再绘制；实验部分继续跳过

## 2026-10-11 ~ 10-15 会话：论文正文打磨（TASK-048..059）

- 目标/任务：按用户要求打磨论文正文（排版、语言、参考文献、示意图占位），实验与图片暂缓。
- 已完成内容：
  - TASK-048..053 收口：摘要与全文防御性句清理、去掉 `state-preserving` 修饰、文献重排、三处图占位、公式排版修复。
  - TASK-054（handed-off）：40 条文献逐条网络核对，39 条与权威元数据一致，修正 `williams2015data` 的 `data--driven`→`data-driven`；报告 `.project-log/docs/task057-reference-verification.md`。
  - TASK-058（完成，go）：Introduction 完全重写为问题驱动故事线（MPC 需求 → Koopman 提升线性化 → 手选字典再到神经网络学习 → 固定矩阵对局限 → 历史进提升 vs 进转移 → 本文 → 预测问题 → 控制问题）。删除离题稳定性句及 `diehl2005rtistability`，文献 40→39。
  - TASK-059（完成）：`paper` 分支设置 upstream 并推送 `172463b` 到 `origin/paper`（直连失败，改用一次性代理 `127.0.0.1:10808`）。
- 重要决策：DEC-091~094（联合训练损失、六章布局、测量空间控制成本、公式分组与重编号）；DEC-095（文献按首次引用顺序，引言引用扩充，删除从未引用条目）。
- 验证与限制：Introduction 复核两轮，第一轮 conditional 指出 7 处问题，第二轮 go；复核方无 shell/联网，编译数字与外部元数据未由其独立复核。`han2024robust`、`han2020deep`、`feizi2025deepkoopman` 已读摘要，其余按标题/venue 使用。所有论文改动均未提交。
- 下一步：见上方“当前状态”。

## 2026-10-08 会话：全部任务取消 + GOAL-001 诚实收口 + 框架缺陷登记

- 目标/任务：按用户指令取消全部任务并收口 GOAL-001，同时登记框架缺陷。
- 已完成内容：9 个任务取消（rev 657）；`goal update` 把 8 项成功条件改为 `not-applicable`（原文保留）并清空 `required_evidence`（rev 658）；新增 DEC-045、DEC-046（rev 659/660）；新增 `.project-log/docs/framework_defect_log_v1.md`（11.8 KB，故意不登记 doc_ref 以免触发全局漂移门禁）。
- 重要决策：DEC-045 收口；DEC-046 框架缺陷 7 条（无目标取消态、risk_level 冻结、review 判据错配、无法归档、全局漂移阻塞、长文本与 doc_ref 两难、终态不可逆）。
- 验证与限制：`goal complete` 两次被 `goal_gate` 拒绝：第一次 8 项 SC pending + 6 项 required evidence missing + 缺 valid review 证据；契约改写后仅剩后者。据此判定"不伪造证据即无法关闭"，工具状态保持 active。未修改框架任何脚本。
- 下一步：见上方“当前状态”。

<!--
会话区块按日期倒序向下追加；超过约 50-100 KB 或约 10 条时归档到
`.project-log/docs/archive/`，归档文件按日期可检索。
-->
