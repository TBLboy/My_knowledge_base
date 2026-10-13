# Vibe Workflow V3 工程改造实施方案（供实施 Agent 执行）

> **文档性质**：源码审计结论 + 设计决策 + 分阶段实施任务书。**本次未修改任何 Vibe Workflow 工程代码。** 方案中的新命令、事件及数据结构是**拟议接口，不是现有能力**。  
> **制定日期**：2026-10-10  
> **代码基线**：用户提交的 `vibe-coding.zip`；`runtime/scripts/state_store.py` SHA-256 `2190101de1dc51cb0904fc80ea57b4d9c330d86c56258196035e86f6f1e611d6`，`runtime/scripts/vibe.py` SHA-256 `2a3842adf74590d7e35e3357d47901ea4e2da5e03e46cff6d84b1070b1a68365`。与缺陷清单 v2 中的指纹一致。  
> **需求依据**：`Vibe-Workflow-框架缺陷清单-v2.md`、`2026-10-10-工具链缺陷报告-高风险任务无法闭合.md`，以及用户在本次对话明确确认的使用偏好。  
> **解释原则**：以下明确区分【源码确认】、【隔离复现】、【现场报告，待环境复现】、【设计建议】；不能将后者写成已实现或已验证的事实。

---

## 0. 给执行 Agent 的最高优先级指令

1. **先完成业务逻辑澄清，再进行正式工程实施**。保留 `business-intent → business-clarification → requirement-baseline → solution-research → architecture-decision → task-decomposition → engineering-spec → implementation → verification → alignment → retrospective → distillation` 的既有生命周期，**不要重新发明业务澄清框架**。
2. 本项目的改造目标是**改善生命周期、可靠性、闭环与用户体验**，不是取消验证纪律。`complete` / `finish` 仍须通过适用门禁；**用户明确要求的 `cancel` / `clear` 不走完成门禁**，也不得被伪装为完成。
3. **用户可随时主动取消单个 Goal/Task，或清空当前活动工作区；默认保留全部历史**。AI 自行批量取消或清空需要用户对本次操作的明确授权，不能仅凭“流程卡住”代替用户决定。
4. 保留单一事实源：**Git 事件账本是持久事实源，SQLite 是可回放投影**。任何新写操作必须贯通命令校验、状态转换、回放、快照、导入、审计、生成视图、CLI 与测试。禁止仅通过直接 `UPDATE SQLite` 修补状态。
5. **先解决已复现的错误放行/错误阻塞，再优化提示词**。绝不可通过宽松 Shell 通配符、伪造复核或降低风险字段来换取绿灯。
6. 执行时拆分为小 PR/小提交；每个阶段按本文 DoD 验收。遇到与本文不一致的最新源码，先记录差异、复核证据，再调整实施，不得机械套补丁。
7. 本文列出的示意 Schema 与命令是建议契约，可在保持语义和兼容约束的前提下细化命名；更改关键契约要先提交设计说明。

## 1. 用户已确认的产品需求（不得偏离）

| 需求编号 | 明确需求 | 必须体现的行为 |
|---|---|---|
| U-01 | 新的业务开发先进入**业务逻辑澄清** | Agent 读项目已有事实，逐轮询问关键细节；先澄清业务规则再确定实现。 |
| U-02 | Goal/Task 太多、过时、状态不准确时希望能管理 | 减少冗余创建；提供真实的取消、归档、重开与清晰视图。 |
| U-03 | 异常处理按风险自主选择 | 可安全重试的失败自主修复；高风险/权限不足/关键业务决策才找用户。 |
| U-04 | **执行阶段安静，关键节点与最终结果汇报** | 不刷屏；澄清阶段仍须主动向用户提问。 |
| U-05 | 用户明确要求“清空全部 Goal/Task 重新开始” | **活动区清零、历史全部保留**，包括旧证据、Review、决策和事件。 |
| U-06 | 用户手动关闭因“不值得继续”而终止的任务/目标 | 走 `cancel`/`archive`，**不走 `complete`/`finish` 证据门禁**。 |

**业务边界**：`取消 ≠ 完成`；`清空活动视图 ≠ 永久删除历史`；`澄清中的业务意向 ≠ 必须立即创建正式 Goal/Task`；`测试通过 ≠ 独立复核通过`；`既往完成事实 ≠ 当前证据仍适用`。

## 2. 实际源码基线与已确认问题

### 2.1 已实现的良好基础（必须复用）

- `runtime/opencode/AGENTS.md:60-78` 定义了完整、可回退的生命周期及功能业务逻辑/技术业务逻辑/双向对齐；`skills/a-business-clarify/SKILL.md` 已有**每轮一个高价值问题**、事实来源分级、原子化行为、业务澄清完成门禁。
- `runtime/opencode/AGENTS.md` 已定义 `quick/standard/strict` 风险路由及 A/B/C 决策权。V3 的自主处置不要创造与之竞争的新词表。
- `runtime/scripts/state_store.py` 定义命令 envelope、revision 并发约束、SQLite 事务、Task/Goal/evidence/review；`state_ledger.py` 保持哈希链及账本先于投影提交；`state_replay.py` 重建实体；`state_views.py` 生成只读摘要。
- `runtime/opencode/plugins/vibe-workflow.ts` 已做状态注入、压缩前状态保存、写入后证据刷新；应以增强为主，不整体替换。

### 2.2 原缺陷清单复核

| ID | 结论 | 源码/依据 | 处理结论 |
|---|---|---|---|
| D01 Goal 无取消路径 | 【源码确认】 | `state_store.py:356-358,517-521,1359-1399` | P0：新增用户可控 Goal 取消。 |
| D02 风险等级不可修改 | 【源码确认】（本身也具有防绕过价值） | `state_store.py:357,1365-1386` | P1：保留不可静默降风险，另设正式契约版本变更；取消不需要变更风险。 |
| D03 Goal Review 与 evidence 双表耦合 | 【源码确认】 | `state_store.py:1187-1213` | P0：修正归属/独立性语义后再统一事实源。 |
| D04 Task 无归档 | 【源码确认】 | `state_store.py:524-525,359-366` | P1：活动视图与历史分离，提供软归档。 |
| D05 全局 doc_ref 漂移阻塞 | 【源码确认】 | `state_store.py:1227-1248`；Goal/Task gate 调用 | P0：按真实依赖作用域检查，仍保留相关依赖的 fail-closed。 |
| D06 长文本/文档引用困境 | 【源码确认】 | `state_store.py:23,159-177,242-279` | P1：信息性引用/受控快照双语义。 |
| D07 Task 终态难重开 | 【源码确认】 | `state_store.py:1560-1564` | P1：重开须保留已有 Run 审计，不应粗暴回写旧 Run。 |
| D08 无 Shell reviewer 难闭合 | 【默认配置确认；特定现场待复现】 | `runtime/opencode/agents/verification-reviewer.md` 默认许可；第二份报告 | P0：验证能力预检与隔离执行入口。不可断言“任何高风险任务必然无法结束”。 |
| D09 `task.finish` 一律写 `implemented-unverified` | 【源码确认】 | `state_store.py:1600-1605`、`state_replay.py:170-176` | P1：执行/验证/复核分别呈现；兼容旧终态。 |

### 2.3 本次增加的源码级发现（重要）

**N01：高风险 Goal 可能被无关 Goal 的 Review 证据放行。严重程度 P0。**

- 【源码确认】`_goal_completion_problems` 先读取**全表** evidence；对 `kind='review'` 的有效证据没有校验其 `covers.goals` 或归属当前 `goal_id`，再全表遍历 reviews；如果 Goal 未登记 implementer，独立性判定分支甚至**不会追加失败**（`state_store.py:1187-1213`）。
- 【隔离复现】在临时 SQLite Store 建立高风险 `G-A`（没有 implementer）、另一 Goal `G-B`、属于 `G-B` 的 `T-B`、与 `T-B` 关联的有效 `kind=review` 证据和 `go` review；给 `G-A` 一个带理由的 `not-applicable` 成功条件、不要求其他证据。调用 `evaluate_goal('G-A')` 返回 `{'passed': True, 'reasons': []}`。**这证明当前 Goal 门禁存在跨目标误放行路径**，与原报告中的“重复登记证据”问题不同。
- **修复必须**：明确 Review 的目标归属、实现者归属、覆盖范围、版本和证据关联。高风险 Goal 没有合法独立性信息应 fail-closed；不得使用任意任务的 Review 满足其他 Goal 门禁。
- **必须新增反例测试**：`test_high_risk_goal_rejects_foreign_task_review`、`test_high_risk_goal_without_implementer_fails_closed`。

**N02：业务澄清 Skill 的命令/记录类型与真实 CLI 不一致。P1。**

- 【源码确认】`skills/a-business-clarify/SKILL.md` 规定 `vibe task create`，然而 `runtime/scripts/vibe.py` 的 `task` 子命令只有 begin/update/wait/resume/handoff/finish/cancel，**没有 task create**；底层 `state-apply` 支持 `task.create`。`goal.create` 同样只有底层命令，没有公开 `vibe goal create`。
- Skill 写到 `open-question` record kind，但 `state_store.py:37-46` 的 `RECORD_KINDS` **没有 `open-question`**；不能按 Skill 字面调用对应 `record create`。
- Skill 要更新 `.project-log/current-session.md`，但 `state_views.py` 生成的文件明确为只读视图，直接写会被覆盖或形成漂移。应改成更新权威记录并使用 `vibe render` 更新摘要。
- **修复必须**：公开 `goal create` / `task create`（与 `state-apply` 一致），或统一将 Skill 指向可用的正式命令；明确开放问题的持久化载体（推荐单独结构化 `open-question` 记录类型，需配套事件/记录校验和模板）；禁止手工写生成摘要。

**N03：Task 重开无法只改状态字符串。P1。**

- 【源码确认】`runs.task_id TEXT NOT NULL UNIQUE`，`tasks.run_id` 指向唯一 Run（`state_store.py:522-534`）；`task.begin` 只允许 `ready`，`task.resume` 只允许等待/阻塞/交接（`state_store.py:1560-1584`）。同一个 Task 若重开后需要**新一轮独立 Run**，必须调整“一任务一 Run”的数据约束和回放模型，或者显式创建有前驱关联的新 Task。绝不能将旧 finished/cancelled Run 改写为 active 以抹掉历史。

**N04：证据的“未绑定”与“未过期”并非同义。P1。**

- 【源码确认】`evidence_applicability()` 对缺失 `version_binding.file_hashes` 返回 `unknown`，而 `_stale_reasons()` 只对 `stale` 返回失败理由；部分门禁会把未绑定、但状态为 `valid` 的证据当成有效（`state_store.py:850+`, `1104+`, `1282+`）。
- **修复建议**：按证据类型定义机器可重放、人工验收、研究论证等不同绑定策略；对 strict 必需的机械验证证据，`unknown` 不能悄然视作已独立复现。已有历史记录按兼容策略处理、显示其证据置信度，不直接篡改旧记录。

**N05：现有 `status` 的“最近任务”列表默认没有活动区过滤。P1。**

- 【源码确认】`_snapshot()` 使用 `SELECT id FROM tasks ORDER BY updated_sequence DESC LIMIT ?`，包含 cancelled/旧任务；`state_views._render()` 直接展示该列表（`state_store.py:1043-1064`、`state_views.py:60-105`）。这与用户希望的“清空后活动区为空”直接冲突。需要正式工作区投影与默认列表策略，不能只修改 UI 文案。

### 2.4 已执行的最小基线验证

在用户压缩包解压的副本中，仅执行测试，未修改源码：

```text
python -m unittest discover -s tests -p 'test_state_gates.py' -q    # 21 tests, OK
python -m unittest discover -s tests -p 'test_state_replay.py' -q   #  5 tests, OK
python -m unittest discover -s tests -p 'test_command_surface.py' -q # 7 tests, OK
```

**范围限制**：以上不代表全量测试、Windows/OpenCode 集成测试或第二份现场业务项目测试已通过。用户报告的现场权限拒绝、`pytest`、真机端到端结果仍需要在对应环境执行复现。本文不会伪称已验证这些环境。

---

## 3. 目标架构：增量演进，不重写

```text
用户自然语言
  ├─ 业务开发意向 → 事实检索 → 双域澄清（一轮一个最高价值问题）→ 需求基线
  ├─ 已确认的小型工程操作 → 风险路由 → 必要 Task/Run → 实施/验证
  ├─ 已有任务继续 → 只恢复当前工作区、执行检查点和证据版本
  └─ 用户工作区管理指令 → 预览操作范围 → 取消/归档/清空（不走完成门禁）
                                  |
                         Command Envelope / 权限来源
                                  |
                    Append-only Ledger（不可改旧事件）
                                  |
          Store 转换 ── Replay ── Snapshot/Import ── Audit/Views
                                  |
                      Scope-bound Evidence / Review
                                  |
                        Gate / Status / Handoff
```

### 3.1 建议分层

- **命令层**：`vibe.py`、OpenCode 命令与主 Agent。区分“用户主动管理”和“AI 自动完成声明”；命令不直接更新 SQLite 表。
- **领域状态层**：Goal/Task、Run、Blocker、Clarification、Workspace、Evidence、Review。每种实体只表达自己职责。
- **持久化层**：`state_store.py` 作为事务投影、`state_ledger.py` 作为不可变账本、`state_replay.py` 作为确定性重建。新表和新事件需三者同步。
- **策略层**：用户授权、风险路由、依赖门禁、验证能力预检。业务规范与执行策略分别版本化。
- **交互层**：业务澄清主动提问，执行阶段安静自动处理，默认简洁的活动视图。

### 3.2 明确不做的事

- 不废弃现有 `a-business-clarify`、`quick/standard/strict` 或 A/B/C 矩阵。
- 不改写历史事件和 Review；不批量伪造过往完成状态。
- 不通过 `bash: allow`、`*pytest*` 或模糊通配符解决独立执行权限。
- 不把 OpenCode 会话 Goal 控制插件视为 Project Goal 完成事实源。
- 不在 V3 初期建设过重的分布式调度器或真实权限服务；该框架仍以单人本地工作流为基本部署边界。

---

## 4. 具体领域设计与事件契约

### 4.1 Goal：取消与完成严格区分（P0）

**保留**现有 `draft | active | waiting-user | blocked | complete` 的历史语义；**新增** `cancelled`（注：当前创建路径直接生成 active；不强制本阶段实现 Goal 草稿创建）。

建议新增动作：

```json
{
  "action": "goal.cancel",
  "payload": {
    "id": "GOAL-001",
    "reason": "用户确认本阶段不再需要",
    "child_policy": "cancel_open"
  }
}
```

约束：

1. 仅对存在且未结束的 Goal 生效。已 `complete` 或 `cancelled` 的 Goal 不再标记成“取消”，如要从主视图隐藏，使用 `archive` 或 `workspace.clear`。
2. `goal.cancel` **不运行 `_goal_completion_problems`**；但仍校验命令合法性、关联对象、事务和权限来源。
3. 必须在同一逻辑操作中处理关联的 `ready/in-progress/waiting-user/blocked/handed-off` 子任务；默认 `cancel_open`，`implemented-unverified` 属于已完成实现的历史，不篡改其已发生的执行事实，按活动区规则隐藏。
4. 对正在执行的 Run，先要求执行协调层停止/隔离，再执行账本事件；若不能停止，应返回可解释的 `execution_still_active`，或将旧代次标记失效使其不能再次提交新工作区变更。**DB 事务不能原子停止外部 Shell/Agent**。
5. 必须附 `reason`，审计记录实际影响的 Task IDs 与当前 revision。取消后这些 Goal 不参与 `active_goal_ids()` 和完成门禁。
6. `goal.complete` 仍严格检查成功条件；**不允许新增 `force_complete`**。

**同时设计**契约变更：现有 `goal.update` 可直接改成功条件列表却保留高风险等级。V3.2 建议 `goal.contract.revise` 或 `goal.rebaseline` 事件，包含前序契约版本、差异、变更理由、审批关联、影响证据；旧契约不可被静默覆盖。取消不依赖此功能。

### 4.2 Task：取消、归档与重开（P1；取消入口现有）

- `task.cancel` 已有且不经过 `task.finish` 门禁；保留其现有语义。
- 新增**活动视图归档**（推荐动作 `task.archive` 或 `workspace.hide-task`），对已取消或已实现的任务从活动列表移出，不从审计账本删除。
- **重开必须决定 Run 模型**：
  - **优先的低风险过渡方案**：为已经存在 Run 的已终结 Task 创建一个**新的 Task ID**，记录 `reopens` / `supersedes` 关系，复制经用户确认仍适用的上下文，旧 Task/Run 完全不可变；通过 CLI 提供 `task reopen --task-id OLD --new-task-id NEW --reason ...` 的易用接口，内部使用单个原子领域事件或受控复合操作。
  - **长期规范方案**：允许同一 Task 多次 Run（删除 `runs.task_id UNIQUE`，保留 `tasks.run_id` 为当前 Run 指针，增加 `attempt_no`/相应索引），并升级 replay、snapshot、import、blockers 与审计；改动显著更大，**只有实际需要保留同一 Task ID 跨多次执行时再做**。
- 不能简单允许 `task.resume` 从 `implemented-unverified` 或 `cancelled` 回到 `in-progress`，否则覆盖旧执行史且破坏单 Run 不变量。
- 后续状态显示由两种派生维度组成：`execution_state`（not-started/active/paused/finished/cancelled）与 `verification_state`（pending/passed/failed/stale/not-applicable）；`review_verdict`（go/conditional/no-go/missing）单独显示。**兼容期不直接改写所有旧 `implemented-unverified` 记录**。

### 4.3 Workspace：活动工作区清零、历史完整（P0）

**推荐语义**：`workspace.clear` = **归档当前活动视图 + 取消开放中的工作**，不得将旧活动 Goal 默认为 complete；不做永久删除。工作区代次用来防止旧会话、旧执行器继续写入。

建议两阶段 CLI：

```text
vibe workspace clear --scope active --dry-run
  → 输出 affected_goal_ids、affected_task_ids、active_run_ids、revision、plan_digest、warnings

vibe workspace clear --scope active --expected-revision <N> --plan-digest <DIGEST> --reason "重新规划"
  → 一次受控提交，返回 generation_before/after 与实际影响对象

vibe workspace status [--all]
vibe workspace history [--generation N]
```

- **一次性用户确认**：主 Agent 向用户说明数量和执行影响；用户明确说“全部清空”即可视为当前目标范围的授权，不逐项反复确认。执行器可以防重复问，但批量危险操作必须有可验证的当前会话授权来源。
- **不要信任伪造的 `actor: user` JSON 字符串**。仅 CLI 参数不能区分真实用户与拥有 Shell 权限的 AI；短期以 OpenCode 的显式问答/工具调用承载确认、避免 AI 自主触发；如果以后需要硬安全边界，应引入受信任宿主颁发的一次性受限授权令牌。不要宣称 prompt 可以提供密码学级权限隔离。
- **工作区 generation/epoch**：在投影里维护 `current_generation`、`last_clear_sequence`（可做独立 workspace 表或投影字段）；新 Goal/Task 属于新代次，旧对象和历史事件始终可查询。`status`、`active_goal_ids()`、handoff、compact context 和插件注入默认只读取当前代次中的活动实体。
- **逻辑原子性**：将目标与关联任务的取消/归档操作做成**单条 `workspace.clear` 命令对应的确定性批处理 transition 和 replay**，避免 N 个单独 `task.cancel` 成功一半。事件的 payload 要确定性记录策略与对象范围，receipt 包含实际受影响的 ID；在同 revision 下验证计划摘要，避免 TOCTOU。
- **持久化边界**：现有系统先追加账本再提交 SQLite；不能声称两个介质物理上拥有一个 SQL 原子事务。应利用已有 ledger-heal 恢复机制保证**故障后最终一致**，并测试“账本 fsync 后 SQLite 提交前崩溃”的工作区切换重放。
- **执行隔离**：执行器/主 Agent 在写入时携带 workspace generation 或等价 fencing token；清空后旧 token 的新写入被拒绝，防止旧会话复活任务。已有 `expected_revision` 不能完全替代清空后的长期代次校验。
- **投影过滤**：`_snapshot()` 当前无差别取最近任务，应改为默认当前活动工作区；`--all` 或 history 查看全历史。已取消、归档、旧代次记录不会占用默认 Top-N。
- **再次清空**：对已经空的工作区要保持逻辑幂等；重复的 `command_id` 不得产生重复效果，新的 clear 请求在无活动工作时可返回 no-op。

建议先实现一个经过 replay 验证的 `workspace` 投影，不在单独 Markdown 文件存第二份权威工作区状态。

### 4.4 业务澄清：保留既有体系，补齐接口（P1）

1. **明确入口分流**：业务开发意向进入 `a-business-clarify`；查询/阅读不生成正式 Task；用户管理命令直接进入 workspace 管理；已经明确、影响可控的工程命令按既有风险矩阵执行。
2. **事实优先**：先检索代码、测试、business atom、decision、需求文档；仅问项目事实不能回答的关键业务问题。
3. **每轮一个最高价值问题**：沿用现有 `impact × uncertainty × future rework cost` 排序；说明为什么问、推荐答案、影响，允许用户自由纠正。
4. **澄清出口**：沿用现有 Completion Gate（正常流、异常/权限、冲突、验收条件、无阻塞 C 级未知）；剩余低影响、可逆未知可显式记录为 deferred，避免无限循环。
5. **草稿与正式目标解耦**：需求澄清过程中可以只存业务草稿/open question/decision；除非需要正式追踪，不强迫每轮新建 Goal/Task。转成正式基线时再复用/创建 Goal 和 Task。
6. **真实命令补齐**：提供 CLI 的 `goal create`、`task create`，或用一致的正式封装；为 `open-question` 制定真实的持久化类型和生命周期，或删除 Skill 中虚构的类型声明并改用已支持的结构化载体；生成摘要必须通过 `render` 更新。
7. **防重复**：Task 创建前检查相同 scope/acceptance/goal 的活动任务；只能建议合并，不能凭相似标题强合并不同业务行为。

### 4.5 风险自适应和安静执行（P1）

**只采用已有 `quick / standard / strict` 与 A/B/C 权限词表**：

| 路由 | 实现与错误恢复 | 用户可见消息 |
|---|---|---|
| quick | 针对性验证；安全、幂等失败可自主处理 | 关键变化或结果时汇报 |
| standard | 定向与邻近回归；按失败签名有限次尝试不同的诊断假设 | 重复同签名且无新 delta，或需要业务选择时询问 |
| strict | 预检复核能力、可重放证据和用户验收；绝不偷偷放宽门禁 | C 级决策、不可逆范围变更、必需能力缺失时询问 |

- 复用现有 `a-loop-control` 的 Retry Contract：失败归因、hypothesis、delta、expected evidence。**禁止同错误同输入无限重试**。
- 子 Agent 向主 Agent 报告，主 Agent 统一面向用户沟通。**澄清阶段主动对话，工程执行阶段尽量安静**。
- `status` 默认输出：当前 Goal / 当前 Task、正在做什么、阻塞、需要用户决定什么、验证/复核结果、下一步；历史及细节可通过 `--all`/`history` 查看。
- 历史完成事实与当前有效性拆开：completed_at 不变，适用性可能变成 stale，需要后续再验证，不回写历史事实。

---

## 5. 证据与复核门禁的正确设计（P0）

### 5.1 统一规范化模型

推荐三个分立对象：

```text
VerificationRun（测试/构建/探针执行事实）
  id, action_id, task_id, goal_id?, source_revision,
  environment, command_spec_version, started_at, finished_at,
  exit_code, output_digest, artifact_refs, coverage_claims

Evidence（输入产物、测试运行、人工确认、审计等支撑）
  id, kind, subject, covers.tasks, covers.goals,
  binding_policy, artifact_digest?, verification_run_id?, status

Review（独立裁决）
  id, target_type, target_id, target_contract_revision,
  reviewer_identity, implementer_identity, verdict,
  evidence_refs, reviewed_source_revision, limitations
```

字段名称可细化，但**必须显式指明被评对象、版本、覆盖和绑定方式**。Reviewer 不是代码/测试运行者的同义词。`go` 是在明示范围和适用证据上的裁决，不是“测试都跑过”的替代品。

### 5.2 Goal 高风险门禁修复（最先）

最小不变量：

1. Review 必须适用于**当前 Goal**（直接 Goal Review 或经定义允许的 Goal 下属 Task Review 汇总），不能使用无关 Task/Goal 的 Review。
2. high/critical Goal 的 implementer 缺失时**不得跳过独立性判据**；应返回 `missing_implementer`。
3. Review 的 `reviewer` 必须与被审核实现身份区分；长期增加结构化身份/执行上下文，而非仅凭不同的字符串假定真实独立。
4. Review 的 `evidence_refs` 必须指向当前目标范围内的适用证据，版本应覆盖被审核契约/产物。只有证据 status 为 `valid` 不足以证明归属。
5. 对现有 `evidence.kind='review'` 和 `reviews` 的双表耦合：**先写兼容适配层**，旧数据仍可显示；新记录以 Review 为裁决事实源，Evidence 为支持材料，不需要“为了凑锚点”制造同名空壳记录。
6. `required_evidence` 无明确 evidence_refs 时不能通过无关项目相同 kind/subject 的证据冒名满足；必须满足 covers/goal lineage 与绑定策略。

**反例测试必备**：跨 Goal Review、不存在 implementer、reviewer=implementer、证据过期、Review 绑定了无关证据、旧证据来自其他源码版本、已撤销/替换契约。

### 5.3 文档引用漂移：依赖感知，不全局阻塞

- 把 `doc_ref` 的识别从“任意包含 `path` 和 `sha256` 的对象”迁移到**明确的类型**：

```json
{"type":"informational_ref","path":".project-log/docs/notes.md","description":"背景阅读"}
{"type":"bound_document","path":".project-log/docs/spec.md","sha256":"...","subject":{"kind":"task","id":"TASK-155"},"binding":"required"}
```

- 信息性引用：不存在/变更会产生诊断提示，但不会阻塞不依赖它的任务。
- 受控文档：如果属于当前 Task/Goal 的显式依赖且 hash 不匹配，应 fail-closed，要求重新绑定或重新验证。
- 兼容旧 `doc_ref`：保留原始 JSON，迁移时根据可溯源关联生成映射；**无法确定关联时不要偷偷当作受控依赖，也不能偷偷当作已验证**，在 `validate --all` 中给出待分类提示，制定明确默认处置策略并记录决策。
- `validate`（数据完整性/全局诊断）与 `gate`（当前目标适用性）应分别计算，避免全局文档编辑阻塞无关收口；更新 `audit_gates` 的历史语义，区分“历史完成当时合规”和“当前证据已失效”。
- 关联证据建议统一为 `depends_on` 关系或适用范围索引，尽量避免每次门禁全表扫描；可在投影上建立索引，但引用关系的事实仍记录于账本。

### 5.4 Verification Runner：受控执行，不开无限制 Bash

第二份报告指出，OpenCode 默认 reviewer 白名单和真实项目 `python.exe -m pytest`、Shell 探针不匹配。**只验证了压缩包的默认配置；具体 Windows 安装后的实际权限需现场复现。**

建议的可实施顺序：

1. 在任务规划时建立 `verification_plan`：需要的检查、平台、入口、依赖、是否必须由独立执行身份重新运行、是否需要人工验收。
2. 高风险任务开始或进入验证前执行 `verification preflight`：检查命令、解释器、权限策略、运行环境、网络、真机与外部依赖。缺能力明确报 `verification_capability_missing`，并建议合法替代或向用户请求环境。
3. 优先用**受信任的受控验证动作清单**执行项目测试：命令以结构化 argv、固定工作目录、环境变量白名单、超时、资源限制和输出位置定义；不允许模型随意拼接 Shell 字符串。测试代码可能执行副作用，Runner 须使用受限工作树/容器等隔离方式。
4. Runner 生成独立的 VerificationRun 和完整日志/哈希；Reviewer 审查证据与结果，必要时亲自发起同一受控 Runner 的复跑。
5. Gate 校验 review 的独立性、适用证据、源版本和必需 VerificationRun，而不是仅校验 `go` 字符串。
6. 在无法复现的环境中允许诚实登记 `conditional`、`blocked`、`needs-user-acceptance`；**不允许用无证据的 go 换取完成**。

**严禁**以 `bash: allow` 或宽泛的 `*python.exe -m pytest*`/`*run_license_probe.sh*` 通配符作为通用“最优方案”。`edit: deny` 不等于测试进程不会写文件。临时项目级命令许可只能作为明确标记的过渡策略，并配合 sandbox、作用域和能力检查。

---

## 6. 版本、迁移与兼容设计（必须作为独立工作包）

### 6.1 版本现状与危险点

- `state_store.py:14-16` 目前 `SCHEMA_VERSION = 1`、`STORE_SCHEMA = 3`；`metadata` 表的 CHECK 直接限定版本；`_request()` 仅接受 schema_version 1。
- `_DDL` 的 Goal/Task 状态 CHECK 固定，新增 `cancelled` 等状态要迁移 SQLite 表约束。
- `_BUNDLE_COLUMNS`、`_BUNDLE_FIELDS`、`_validate_bundle()` 严格校验导入包字段，新增 workspace / Run 元数据不能忽视它们。
- `state_replay.reduce_ledger()` 根据 action 还原全部逻辑状态；`Store._verify_ledger()` 比对回放结果、收据和各表；历史 request/receipt 的字节形态不能被替换。
- `state_ledger.py` 的 `LEDGER_SCHEMA_VERSION=1` 是哈希链事件外壳格式，**不等于**新 Store DDL 版本；切勿仅为了添加新 action 就重写旧 `.project-log/ledger/v1/ledger.jsonl`。
- `state_context.read_marker()` 读取 `.project-log/state-format.json` 中 format 2；它代表 Project Log 格式，不应因内部数据库 DDL 升级而擅自改成 format 3。

### 6.2 推荐兼容路径

1. **明确分离版本概念**：Project Log format、command envelope schema、SQLite store schema、portable snapshot schema、ledger event wrapper。不要继续让一个全局整数同时承担所有职责。
2. 小规模新增事件可保持 envelope v1 **前提**是旧记录仍按旧校验、旧 receipt 回放，且消费者有安全的版本/能力探测。引入结构不兼容字段时增加 v2 envelope/schema，并提供**按事件版本分派的回放/验证**。
3. 将 SQLite 迁移为下一 store schema（例如 `STORE_SCHEMA=4`）；使用 staging/备份、独占锁、完整性检查和可回滚切换。SQLite 原有 CHECK/UNIQUE 约束变更需要正确重建相关表并恢复索引/FK，不能直接假定 `ALTER TABLE ADD` 足够。
4. 历史 ledger v1 只读回放，绝不追溯重写老 receipt；新事件在旧快照中要么被版本明确拒绝，要么通过专门兼容适配，不得静默丢字段。
5. Snapshots：导出新版本；导入旧版本时经显式适配迁移；旧客户端遇到更高版本**明确拒绝写入**，避免低版本误写坏数据。
6. `state_context.open_store()`、`reconcile_with_ledger()`、`apply_import()`、`_entity_rows()`、`_translate_entities()`、`_verify_ledger()`、`state_views` 必须共同升级。
7. 先做**在旧账本副本上的迁移演练**，比较迁移前后的原始事件 ID、哈希链、Goal/Task/Run/Blocker/Evidence/Review 可查询性，确保数据无损。
8. 对崩溃边界做故障注入：账本已持久化但 SQLite 未提交、迁移中断、snapshot import 中断、投影生成失败；必须能够恢复或明确 fail-closed，不得出现悄然丢历史。

### 6.3 运行时与安装兼容

- OpenCode 权限配置：`runtime/opencode/agents/verification-reviewer.md`、`runtime/opencode/agents/vibe-main.md`；运行时角色描述：`runtime/agents/verification-reviewer.md`、`runtime/agents/roles.json`，变更必须同步。
- OpenCode 插件 `runtime/opencode/plugins/vibe-workflow.ts` 和 commands 的默认状态注入及恢复路径要识别清空后的 current generation，不要从历史 task 复活旧执行。
- 安装器 `runtime/opencode/install.sh`、升级/验证脚本需要检测全局与项目级角色配置冲突、Python 路径/PowerShell 与 Bash 差异、验证 Runner 能力；保留安装器的备份与冲突处理语义。
- 旧 Codex 面和 OpenCode 面存在历史兼容资产；若本次只针对 OpenCode，须给出明确影响清单与不支持声明，并通过现有跨平台/发布测试，防止打包引入破损。不能无依据地断言另一个客户端已经兼容。

---

## 7. 文件修改清单（按职责划分）

| 文件/目录 | 预期修改 | 优先级 |
|---|---|---|
| `runtime/scripts/state_store.py` | 新增 goal.cancel、workspace.clear、归档/重开事件；调整投影/表约束；修 Goal Review 归属、文档依赖门禁；清晰的错误码 | P0 |
| `runtime/scripts/state_replay.py` | 对每个新 action 实现确定性重放及精确 receipt；旧事件行为保持 | P0 |
| `runtime/scripts/state_ledger.py` | 保持旧哈希链不变；更新新动作兼容检查、回放与快照测试（必要时） | P0 |
| `runtime/scripts/vibe.py` | CLI：goal/task create、goal cancel、workspace clear dry-run/commit、status history、task archive/reopen；结构化错误输出 | P0/P1 |
| `runtime/scripts/state_context.py` | 工作区代次的上下文恢复、格式迁移、旧会话隔离 | P0/P1 |
| `runtime/scripts/state_views.py` | 默认只显示活动工作区；展示验证状态/复核；历史按需展开 | P1 |
| `runtime/scripts/state_gate.py`、`state_evidence.py` | 明确证据类型、版本适用性、校验能力；不引入与 Store gate 矛盾的第二套逻辑 | P0/P1 |
| `runtime/opencode/agents/verification-reviewer.md` | 改为受控验证入口和能力预检，不直接扩展宽泛 Shell 权限 | P0 |
| `runtime/opencode/agents/vibe-main.md` | 用户授权优先、阶段区分、低打扰交互、清空/取消安全操作 | P1 |
| `runtime/agents/verification-reviewer.md`、`roles.json` | 与 OpenCode agent 的职责和能力矩阵一致 | P1 |
| `skills/a-business-clarify/SKILL.md` | 修不存在的命令/record kind/手工生成文件要求；澄清出口和复用行为 | P1 |
| `skills/a-loop-control/SKILL.md`、`skills/a-session-handoff/SKILL.md`、`skills/a-project-log/SKILL.md` | Retry Contract、当前工作区恢复、历史/活动分离 | P1 |
| `runtime/opencode/AGENTS.md` | 增补用户管理权、安静执行、工作区清空与澄清/执行边界，**保持原生命周期** | P1 |
| `runtime/opencode/commands/vibe-start.md`、`vibe-resume.md`、`vibe-status.md` 等 | 使用真实 CLI；不强迫业务澄清每轮创建正式 Task；清空后不复活旧目标 | P1 |
| `runtime/opencode/plugins/vibe-workflow.ts` | 状态注入只用当前工作区；旧代次写入防护、清空后 context 刷新 | P1 |
| `runtime/opencode/install.sh`、`runtime/scripts/validate_package.py` | 安装校验、权限/入口一致性与迁移兼容 | P1 |
| `tests/test_state_gates.py` | 错误放行/错误阻塞、跨 Goal Review、证据版本、漂移作用域 | P0 |
| `tests/test_state_ledger.py`、`test_state_replay.py`、`test_ledger_recovery.py` | 新事件、Crash/Heal、Replay、导出导入 | P0 |
| `tests/test_state_records.py`、`test_command_surface.py` | 新命令、record 类型、Task 生命周期、活动区过滤 | P0/P1 |
| `tests/test_opencode_surface.py`、`test_opencode_installer.py`、`test_cross_platform_surface.py` | 角色权限、平台路径、插件命令一致性 | P1 |
| `docs/USAGE.md`、`runtime/opencode/README.md`、发布说明 | 新概念、用户指令、兼容说明、迁移/回滚说明 | P1 |

> `skills/` 位于仓库根目录，不是 `runtime/skills/`；OpenCode 运行时 Agent/Commands 位于 `runtime/opencode/`。实施 Agent 请以实际目录结构为准。

---

## 8. 分 PR / 分阶段实施计划（可直接作为 Agent 任务清单）

### PR-00：冻结基线、编写反例与迁移测试夹具（**先做，不改行为**）

- 校验源码指纹；列出受影响模块、当前 `SCHEMA_VERSION`/`STORE_SCHEMA`、导入包字段。
- 复制旧账本/SQLite 快照到仅用于测试的夹具，不得改用户真实项目。
- 补充 N01 跨 Goal Review 漏洞测试、全局 doc_ref 漂移反例、命令/Skill 契约一致性检查。
- 保持新测试初始失败（红），提交可复现材料、预期行为和证据。
- **DoD**：能够证明至少 N01、D05 的问题路径；既有测试基线可重现。

### PR-01：立即封堵高风险 Goal 误放行（P0）

- 拒绝未登记可核实 implementer 的高风险 Goal 独立复核；Review 必须绑定当前 Goal/合法的相关任务和对应 evidence。
- 处理旧双表 Review/evidence 兼容；不能为通过测试“补造” Review。
- Gate 错误码应区分 `missing_implementer`、`review_scope_mismatch`、`review_evidence_stale`、`review_missing` 等。
- **DoD**：N01 所有反例转绿；已有合法 Goal/Task gate 测试维持通过。

### PR-02：Goal 取消 + 工作区清空最小闭环（P0）

- 设计版本化事件及 store 投影；实现 `goal.cancel` 和 `workspace.clear` 的计划/提交两阶段接口。
- 单事件处理当前活动 Goal 和其未结束 Task；保护 `expected_revision`/plan 摘要；恢复后不复活旧任务。
- 更新 replay、bundle、import、views、context、CLI、ledger crash/heal 测试。
- **DoD**：一句用户明确指令可以取消单目标或清空当前活动区；操作后 `status` 的活动列表为空，`history --all` 保留完整旧记录，`ledger verify` 和 `validate` 一致；取消不需要完成门禁。

### PR-03：局部依赖门禁 + 文档引用类型（P0/P1）

- 引入 explicit informational/bound 引用，按当前目标/任务依赖收集漂移；全局扫描仅用于诊断。
- 为旧 doc_ref 提供透明适配/待分类输出，不造成隐性“全部通过”。
- **DoD**：无关文档修改不挡当前任务；相关受控文档修改会阻塞；历史记录的合规完成事实不倒写。

### PR-04：复核 Runner / 能力预检（P0/P1）

- 明确验证计划 Schema 与受控动作配置，先做一个最小 Runner 支持 `python -m unittest`、`python -m pytest` 和只读检查的**明确 argv 路由**；环境隔离与审计输出必须可测。
- 改 reviewer 角色调用方式；规划阶段输出缺少能力的错误及恢复建议。
- **DoD**：在模拟 Windows/Linux 入口的测试环境中，预检准确发现路径/权限缺失；不靠全开 bash 达到“go”；记录可追溯 VerificationRun。

### PR-05：Task 体验与业务澄清契约对齐（P1）

- 完成 status 的执行/验证/review 派生状态；Task archive；采用“新任务继承旧任务关系”的低风险 reopen 方案。
- 给 CLI 增补 goal/task create 或修正所有 Skill/Command 至合法入口；消除 `open-question` 与只读摘要写入冲突。
- 澄清阶段保留单问模式与完结判据，减少不必要的任务创建和重复追问。
- **DoD**：业务澄清 Skill 中每个可执行命令有真实入口及 CLI 契约测试；取消/归档任务不充斥活动视图；重开保留旧 Run。

### PR-06：低打扰体验、会话恢复与打包（P1/P2）

- 更新主 Agent 和插件注入规则，按当前工作区代次恢复，显式 fencing 防止旧执行写入。
- 主 Agent 只在关键决策或最终结果主动对用户汇报；Retry Contract 保持风险分级。
- 执行安装/升级/回滚、快照兼容和跨平台模拟测试；同步使用指南与发布说明。
- **DoD**：新会话恢复不复活清空前 Goal/Task；文档与所有 CLI 能力一致；升级失败可恢复旧账本/SQLite。

> 推荐合并依赖：`PR-00 → PR-01 → PR-02 → PR-03 → PR-04 → PR-05 → PR-06`。若实际依赖要求，PR-03 与 PR-04 可在 PR-02 的状态接口稳定后并行开发，但**不能同时修改同一状态 Schema/回放文件而缺少协调**。

---

## 9. 完整验收测试矩阵

建议实现为 `unittest`，沿用当前仓库现有测试风格，必要时另增 CLI/插件端到端脚本。下表至少一项对应一条自动化测试。

| 测试编号 | Given | When | Then |
|---|---|---|---|
| T01 | High Goal A + 不相关 Goal B 的 go Review | 评估 A | A 不得通过；报归属不符。 |
| T02 | High Goal 缺 implementer | 评估完成 | fail-closed，不因已有 review 类 evidence 放行。 |
| T03 | Review 与 implementer 同身份 | 严格门禁 | 拒绝。 |
| T04 | Goal Review 指向已过期/不适用证据 | 评估门禁 | 拒绝并指出失效原因。 |
| T05 | Goal active 且成功条件未满足 | 用户主动 cancel | 取消成功；不走 goal.complete 门禁。 |
| T06 | Goal 带多个 ready/waiting/blocked Task | 取消 Goal | 一次完整处置子任务并有审计记录。 |
| T07 | Goal 已 complete | 用户取消 | 拒绝改写 complete，建议仅归档/清空视图。 |
| T08 | N 个活动 Task/Goal | dry-run workspace.clear | 只读返回完整集合、revision、plan_digest，无写入。 |
| T09 | dry-run 后其他写入改变 revision | 提交原计划 | 拒绝过期计划，不产生部分效果。 |
| T10 | 活动 Goal/Task | workspace.clear commit | 当前活动区为空；全部历史仍在。 |
| T11 | 有 cancelled、complete、verified 历史任务 | workspace.clear | 当前活动视图不显示旧终态，history 可查。 |
| T12 | 同一清空命令重复提交 | 重放/重试 | 不重复取消或损坏历史。 |
| T13 | 清空前旧 Session/Run 持旧 generation token | 尝试写入 | 被 fencing 拒绝，不复活旧任务。 |
| T14 | 账本已 fsync、SQLite 未提交 | 崩溃并恢复 | 重放得到相同逻辑工作区状态，校验通过。 |
| T15 | 独立 Run 已 finished 的 Task | reopen | 旧 Run 不被修改，新 Task/Run 可关联追踪。 |
| T16 | 已完成 Task，有 Review go | 读取 status | 显示实现、验证、复核的各自状态，不仅 unverified。 |
| T17 | 已完成 Task 的代码依赖变更 | 重算适用性 | 历史完成事实保留，当前适用性 stale。 |
| T18 | 与当前 Task 无关 doc_ref 改变 | 任务 Gate | 不受阻塞；全局 validate 可提示。 |
| T19 | 当前 Task 依赖的 bound_document 改变 | 任务 Gate | fail-closed，要求重新验证。 |
| T20 | 信息性引用改变 | 任务 Gate | 不阻塞。 |
| T21 | 旧格式 doc_ref | 升级/导入 | 原始记录不丢失，显式报告待分类/兼容状态。 |
| T22 | strict 任务仅有适用性 unknown 的必需机械证据 | 评估门禁 | 不得错误标记为机械验证已确认。 |
| T23 | Reviewer 配置不具备项目 pytest 入口 | 预检 | 在实施后期前发现能力不足；提供清晰错误。 |
| T24 | 受控 Runner 使用指定 argv | 执行测试 | 产出结果、stdout/stderr 摘要、版本/环境绑定。 |
| T25 | 不安全宽泛 Shell 命令 | Runner 提交 | 拒绝不在信任动作清单中的动作。 |
| T26 | 新业务意图且逻辑不清 | 启动 Vibe | 先进入 business clarification，不直接编码。 |
| T27 | 用户已回答上一澄清问题 | 恢复会话 | 不重复问已确认事实，继续最高价值问题。 |
| T28 | Skill 写到 goal/task create / open-question | CLI 契约检查 | 每条命令和记录类型都可真实执行。 |
| T29 | 使用旧 ledger v1 快照 | V3 迁移 | 旧事件和哈希保持，状态无损；新旧版本能力明确。 |
| T30 | 项目安装/升级/回滚 | OpenCode + 平台模拟 | 权限/命令/Skill/版本一致，不覆盖用户独立配置。 |
| T31 | 有多个 Goal 存在 | 活动工作区读取 | 仅识别当前 generation；存在多个当前代次活动 Goal 时仍按规则拒绝隐式猜测。 |
| T32 | 无用户授权的 Agent 请求批量清空 | 执行管理动作 | 按当前平台的授权机制拒绝/要求用户明确指令；不能仅凭伪造 actor 字段放行。 |

### 9.1 每阶段最低必须执行的已有测试

```bash
python -m unittest discover -s tests -p 'test_state_gates.py' -q
python -m unittest discover -s tests -p 'test_state_replay.py' -q
python -m unittest discover -s tests -p 'test_state_ledger.py' -q
python -m unittest discover -s tests -p 'test_ledger_recovery.py' -q
python -m unittest discover -s tests -p 'test_command_surface.py' -q
python -m unittest discover -s tests -p 'test_opencode_surface.py' -q
python -m unittest discover -s tests -p 'test_cross_platform_surface.py' -q
```

发布前再运行项目完整测试与包校验；报告**测试数量、环境、耗时、失败原因、未运行原因**。Linux CI 通过不得冒充 PowerShell 真实机器验证。

### 9.2 交付证据格式（每个 PR）

```yaml
change_id: PR-02
source_revision: <commit-hash>
implemented_actions: [goal.cancel, workspace.clear]
changed_files: []
tests:
  - command: python -m unittest ...
    result: passed | failed | not-run
    environment: <OS/Python/OpenCode>
ledger_replay_verified: true | false
snapshot_import_verified: true | false
remaining_risks: []
user_decisions_required: []
```

---

## 10. 兼容/回滚发布门禁（发布前不得跳过）

- [ ] 备份现有 `.project-log/.state/`、事件账本和相关长文档；备份可还原、路径清楚。
- [ ] 旧状态库可迁移，任何错误都能恢复到升级前可读状态。
- [ ] 新 schema 的所有实体可通过完整旧账本 + 新增事件确定性重放。
- [ ] 新版本 `ledger verify`、`validate`、snapshot export/import 全通过；不改历史事件哈希。
- [ ] 不存在已 `cancelled` Goal 在默认 `active_goal_ids` 中被选中的情况。
- [ ] `workspace.clear` 后活动视图为空，但 `history --all` 可查询全部旧 Goal/Task/Review/Evidence。
- [ ] 旧代次中的悬挂 Run、阻塞和恢复检查点不会被误当成新代次的活动任务。
- [ ] `goal.complete`、`task.finish` 对高风险的合法严格性没有下降；修复 N01 并覆盖回归。
- [ ] 文档漂移只阻塞当前有关联的受控文档；全局诊断仍可发现历史漂移。
- [ ] 已安装的角色/命令/Skills 不会与新 CLI 自相矛盾。
- [ ] 证据不足时诚实显示 conditional / blocked / stale；不使用测试成功的文本声称独立验证已通过。
- [ ] 项目内新增状态与 OpenCode 插件、压缩/恢复 Hook 完全对齐。
- [ ] 默认呈现简洁，历史通过显式命令查看；重要错误和用户 C 级决策不被“安静执行”吞掉。

## 11. 尚需现场验证、不可假设的事项

1. **业务项目真实环境**：第二份报告提到 Windows PowerShell、`python.exe -m pytest`、`run_license_probe.sh`、真机/浏览器/WSL 验证；这些不在提交的框架压缩包内。本方案能指出默认策略冲突，但不能断言当前业务项目最新运行结果。
2. **OpenCode 的真实授权能力**：仅看本仓库 Agent Frontmatter 无法保证 CLI 调用是“用户亲自发起”；若要做强制鉴权，需要确认宿主可提供可信身份/批准 token。
3. **插件对 Session Goal 的实际取消/暂停接口**：框架文档记录 `@prevalentware/opencode-goal-plugin@0.1.51`；不能凭源码推测它能够安全终止外部进程。工作区清空前要验证会话 Goal 控制层的协同方式。
4. **跨客户端覆盖**：仓库存在 Codex 遗留资产，V3 的优先目标是当前 OpenCode 路径；其余面是否同步升级需要由负责 Agent 列出精确支持矩阵并验证。
5. **业务澄清的 `open-question` 存储契约**：需要选择新增合法 record kind 还是正式结构化的澄清文件事实源，并确认与现有状态账本原则一致。推荐前者，但以不损害历史兼容为前提。

---

## 12. 交给执行 Agent 的启动指令（可直接复制）

> 请以 `Vibe-Workflow-V3-工程改造实施方案.md` 为本次改造任务书，**先读取当前仓库和两份缺陷报告**，校验源码 SHA-256 与文件结构。严格区分现有事实和拟议设计，不要立即大范围修改代码。
>
> 先执行 **PR-00**，建立 N01 高风险 Goal 跨目标误放行、D05 全局文档漂移错误阻塞、CLI/Skill 命令不一致的失败测试及迁移测试夹具，提交可重复复现的报告。然后按 **PR-01 → PR-02 → PR-03 → PR-04 → PR-05 → PR-06** 小批次实施，每个 PR 独立验收。
>
> 绝不重写或删除旧账本，绝不以假复核、全开 Bash、静默降风险解决门禁，也不将用户明确取消解释为完成。业务需求仍从 `a-business-clarify` 开始，每轮一个最高价值问题；实施阶段按 quick/standard/strict 自主执行、低打扰汇报。
>
> 所有新增操作必须端到端同步 `state_store.py`、`state_replay.py`、CLI、bundle/import、上下文恢复、生成视图、审计和测试。**特别验证 workspace.clear 的崩溃恢复、generation 防旧会话写回，以及跨 Goal Review 的禁止错误放行。**
>
> 每个 PR 返回：改动摘要、真实修改文件、迁移/回滚情况、命令与测试结果、存在的风险、与本文不同的实现决策；如有必须由用户决定的 C 级产品问题，先处理能自主完成的部分，然后只问当前影响最大的一个问题。

---

## 13. 一句话验收目标

**业务澄清时 Agent 会认真追问真正需要澄清的问题；工程执行时尽量安静且能自主恢复；用户一句话可以取消或清空当前工作；所有历史和证据完整可追溯；严格完成门禁既不被无关记录误阻塞，也不被无关 Review 错误放行。**
