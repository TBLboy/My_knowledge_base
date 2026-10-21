# Vibe Coding 框架问题记录

> 用途：按根 `AGENTS.md` 项目级规则要求，记录使用 vibe-coding 框架过程中发现的**问题或缺陷**，供框架作者后续优化。
> 记录约定：每条含 现象 / 复现证据 / 影响 / 建议；证据须可定位，不写推测为事实。
> 起始日期：2026-10-11

## FI-001：`a-project-init` skill 与 format 2 工作区契约自相矛盾

- **现象**：skill 的 Workflow 第 2 步要求用 `git rev-parse` 判断 Git 状态，并「在 Git 仓库中时询问用户该仓库属于个人仓库还是团队协作仓库」；但按此指引 `git init` 之后，format 2 的状态库初始化必然失败。
- **复现证据**：在工作区 `D:\Project\VR数采调研` 执行 `git init` 后再运行初始化脚本：
  ```
  & "D:\conda\envs\vibe-coding\python.exe" "C:\Users\12187\.config\opencode\skills\a-project-init\scripts\init_project_agents.py" --target "D:\Project\VR数采调研" --json
  ```
  报错：
  ```
  state_store.StateError: Project Log must live in a plain work folder: the work folder itself must not be a Git worktree root,
  and it must not sit inside another Git worktree.
  ```
  抛出位置 `vibe-workflow\scripts\state_context.py:132 git_context()`，来自 `init_project.py:44 _initialize_format_two()`。
- **影响**：按 skill 指引操作会 100% 失败；且失败点在 `initialize()` 内的 `init_project.initialize_project()`，在 `ensure_agents_md()` **之前**抛出，导致 `AGENTS.md` 也一并未建立（脚本非原子，前半失败后半不回滚也不继续）。
- **建议**：
  1. skill 应在询问 Git 之前先声明「工作区必须为纯目录，代码仓库只能建在工作区**之下**」；
  2. 或让 `initialize()` 把 `.project-log` 创建与 `AGENTS.md` 创建解耦，前者失败不阻断后者。

## FI-002：`verification-reviewer` subagent 无 `shell` 权限，独立验证能力降级

- **现象**：独立复核 subagent 报 `Permission denied: shell`，无法运行 `vibe status` / `validate` / `portability-status` 等只读命令，只能做磁盘静态核查。
- **证据**：reviewer 报告明确声明「本会话对 `shell` 的调用被拒」，并将 `store_schema=4`、CLI 无报错列为**无法判定**，最终裁决由 `go` 降为 `partial`。
- **影响**：`verification_capability_missing` 会成为常态；strict 任务的独立 `go` 裁决长期依赖主 Agent 代跑并转述，削弱独立性。
- **建议**：为 `verification-reviewer` 开放**只读命令白名单**（如 `vibe status|validate|context|portability-status|ledger`、`git status/log/show/diff`、`ls`）。

## FI-003：任务终态 `implemented-unverified` 与 `verification_state` 的命名歧义（**已澄清：不是逻辑缺陷**）

- **原始怀疑**：同一任务对象同时呈现 `status = "implemented-unverified"` 与 `verification_state = "passed"`，看似自相矛盾。
- **复现证据**：`vibe --root D:\Project\VR数采调研 status` 输出，`latest_task` 字段：
  ```json
  { "status": "implemented-unverified", "execution_state": "finished",
    "verification_state": "passed", "review_verdict": "missing" }
  ```
- **源码结论（经独立复核阅读 `vibe-workflow\scripts\state_store.py:885-916 _derived_states()`）**：三者是**正交的显示投影**，并非冲突。
  - `execution_state` = `tasks.status` 的投影（`implemented-unverified → "finished"`）。
  - `verification_state` = **证据行状态**的投影：存在覆盖该任务的 `valid` 证据行即 `"passed"`；**不等于**「验收通过」。
  - `review_verdict` = `reviews` 表最新行，无行则 `"missing"`（review 仅对 strict/高风险任务强制）。
- **另一个重要澄清**：`task.finish` **恒定**把任务置为 `implemented-unverified`（`state_store.py:2225-2229`），CLI 中**没有**把独立任务置为 `complete` 的路径；即 `implemented-unverified` 就是独立任务的**正常终态**，不是「未完成」或「缺陷」。
- **仍成立的命名风险**：`verification_state="passed"` 字面像「已验证通过」，实际上只等于「有一条覆盖该任务的 `valid` 证据」；且该 `status` 由记录方自评传入（见 FI-006），可在无任何独立复核时显示 `passed`。
- **建议**：不改逻辑，仅改善表达——在该字段旁输出定义，或改名为更中性的名称（如 `evidence_state`）。
- **记录诚实性说明**：本条最初由主 Agent 记为「疑似语义冲突」；经独立复核读源码后**证实不是冲突**。保留此条与澄清过程，作为「未读源码前不得把推测写成结论」的实例。

## FI-004：初始化后人读摘要仍是模板占位

- **现象**：`.project-log/current-session.md` 与 `.project-log/progress.md` 顶部的「当前状态」快照与 `YYYY-MM-DD` 段落仍为初始模板内容，未反映已发生的任务。
- **证据**：reviewer 静态复核结论；生成视图 `views/8/current-session.md` 的 “Recently updated tasks (bounded)” 段为空。
- **影响**：面向人读的入口失效，与「工作留痕」目标存在落差；不影响机器事实源。
- **建议**：`init` 或首次 `task.create` 后由 `render` 生成一致的初始人读视图，避免留下占位符。

## FI-005：Windows PowerShell 控制台中文输出乱码（环境层）

- **现象**：所有含中文的路径与命令输出在控制台显示为乱码，例如 `D:\Project\VR���ɵ���`、`"status": "implemented-unverified"` 的中文摘要字段。
- **证据**：本会话多次 `& $py $vibe ...` 输出均为乱码，但同一文件用 UTF-8 显式读取内容完全正确（`AGENTS.md` 标记与中文规则行均可正常回读）。
- **影响**：排查困难，容易被误判为「文件损坏」或「编码写坏」。
- **建议**：脚本已调用 `stream.reconfigure(encoding="utf-8")`，但 Windows 控制台代码页未随之切换。可在文档中提示调用方先执行 `chcp 65001` 并设置 `[Console]::OutputEncoding`，或由运行时统一处理。

## FI-006：证据状态由记录方自评，可无独立复核即驱动 `verification_state="passed"`

- **现象**：`vibe evidence record` 允许直接传入 `--status valid`，而 `verification_state` 正是「存在 `valid` 证据行」的投影（`state_store.py:899-900`）。因此**任何**证据只要自评为 `valid`，任务的 `verification_state` 就显示 `passed`，不要求存在独立 reviewer。
- **复现证据**：本次 `EV-INIT-001`（`kind:"command"`）、`EV-INIT-002`（`kind:"check"`）均由**实现方**（主 Agent）自评 `--status valid`，`vibe status` 随即显示 `verification_state: "passed"`；此时 `reviews` 表实际为空（`review_verdict: "missing"`）。补录 `review record` 后才变为 `go`。
- **影响**：`verification_state="passed"` 容易被当作「已通过独立验证」的通行证，但实际上不构成任何独立性保证；对非 strict 任务该弱点**静默通过**。
- **建议**：
  1. 区分数值：为「自评证据」与「独立复核证据」输出不同字段或前缀（如 `self_assessed` / `independent`）；
  2. 或在输出中提示「`verification_state` 仅表示存在自评证据，独立结论请读 `review_verdict`」；
  3. 对 strict 任务可考虑强制要求 `review_verdict` 非 `missing` 才允许 `state-gate` 通过。
- **附带观察**：无 `version_binding.file_hashes` 的证据 applicability 恒为 `unknown`（`state_store.py:1109-1131`），无法被机械重算；本项目**故意不绑定 `AGENTS.md` 哈希**，因为该文件会被用户持续编辑，绑定会立刻产生 stale 噪声——这是一处「可重算性 vs 日常可用性」的框架取舍，建议文档化。

## FI-007：`init` 不建立 Project Goal，但规则把 Project Goal 称为「唯一完成契约」

- **现象**：全局规则写明「Project Goal 是唯一完成契约」「宣布项目完成前必须运行 `vibe goal complete` 的验收门禁」，但 `vibe init` 完成后 **`vibe status` 显示 `goal_id: null`**，即**不存在任何 Goal**。`goal.create` 是一个需要人工显式调用的独立子命令，不会在初始化链路中被触发。
- **证据**：本项目在 `goal_id: null` 状态下已正常运行 `INIT-001~004`、`R-001`、`DOC-001~006` 共 11 个任务（revision 55），期间**没有任何门禁或警告提示缺少 Goal**。源码层面 `goal.create`（`vibe.py:184-187`、`state_store.py:454`）与 `init` 是两条独立路径。
- **影响**：完成门禁可以长期形同虚设——直到有人宣布「项目完成」时，才发现在校验一个**从未建立**的契约。对以「证据门禁」为卖点的流程，这是**反直觉的静默缺口**，且属于全局规则与运行时行为不一致。
- **建议**：
  1. `init` 时创建 Goal 占位（`status: draft`）或至少打印「尚未建立 Project Goal」的提示；
  2. 或让 `task create` 在无 `active` Goal 时输出 warning；
  3. 或让 `state-gate` / `status` 显式报告 `goal_missing`，使缺口可见。
- **校准说明**：本条基于「`status` 输出 + 源码路径」判定；**未复核 `init` 的完整 stdout**。若 `init` 实际打印过相关提示而未被 Agent 遵守，本条应降级为「Agent 纪律问题」而非框架缺陷。

---

## FI-008：`next_action` 不可更新 + `review` 接口四处摩擦（**本轮实际造成返工**）

- **现象**（4 项，均本轮实测）：
  1. **`task update` 只能改 `implementer` / `owner`，无法更新 `next_action`** → 任务创建时写入的 `next_action` **永久停留在初始值**，与真实进展脱节。本轮 `R-002` 的 `status` 至今显示「克隆 IsaacTeleop 与 XRoboToolkit PC-Service，做结构普查」，而该步骤早已完成。
  2. **`review record --scope` 要求 JSON 对象**，但 `--help` 只写 `JSON object; @file reads from disk`，**未给字段结构**；传纯文本时报 `scope must be valid JSON`，**不提示期望结构**（本轮试错 2 次）。
  3. **`review record --verdict` 只接受 `go` / `no-go` / `conditional`**（`state_store.py:70` `REVIEW_VERDICTS = ("go", "no-go", "conditional")`），而实际复核结论**常用 `partial`**——`AGENTS.md`、`a-verification`、`a-loop-control` 等技能文档中均以 `partial` 描述复核结论 → **术语不一致**。
  4. **review 不可重录**（`state_conflict: Review already exists`），且 **`review_verdict` 由最后写入的一条 review 决定** → 「先记中间轮（`conditional`）、后记最终裁决（`go`）」时，若最终裁决先录、中间轮后录，**裁决会被中间轮覆盖**。本轮**实际发生**（`REV-R002-FINAL` = `go` 被 `REV-R002-3` = `conditional` 覆盖），只能用**新 ID** `REV-R002-GO` 绕开。
- **证据**：`vibe.py task update --help`（仅 `--task-id` / `--implementer` / `--owner`）；`review record --help`；`state_store.py:70`；本轮实际错误输出 `scope must be valid JSON` / `Unsupported review verdict: partial` / `Review already exists: REV-R002-FINAL`。
- **影响**：
  - `next_action` 陈旧会**误导恢复会话的 Agent**（`status` 正是恢复入口，`AGENTS.md` 要求以它为准）。
  - 复核术语不一致会**诱导 Agent 用非法枚举**；叠加「不可重录 + 排序语义不明确」，**可能记录出与实际不符的最终裁决**——这是**高风险**项（本轮差点以 `conditional` 收尾）。
- **建议**：
  1. 给 `task update` 增加 `--next-action`（或提供独立的 `task.next-action` 动作）。
  2. `--scope` 在 `--help` 中给出最小示例；错误信息附带期望结构。
  3. 把 `partial` 纳入 `REVIEW_VERDICTS`，或统一技能文档措辞为 `conditional`。
  4. review 支持**按 ID 覆盖**或显式 `supersedes`；并让 `review_verdict` 按 review 的 **`created_sequence`**（而非写入顺序）确定，或提供显式的裁决设定入口。
- **校准说明**：第 3 点属「术语不一致」，第 4 点属「排序语义不明确」。两者都可被谨慎的 Agent 绕过（本轮已绕过），但**都应修复**以免后续误判。

---

## FI-009：`evidence record` 的 `--covers` / `--version-binding` 内部结构无文档，纯试错（**本轮实际造成 3 次失败**）

- **现象**（2 项，均本轮实测）：
  1. **`--covers` 的真实结构未文档化**。`--help` 只写 `JSON object; @file reads from disk`。实际要求是**恰好**含 `files` / `requirements` / `tasks` 之一的对象；传入任意其它键（如直接给 `{"covers":{...}}` 或加业务字段）会报 `covers must be an object with files/requirements/tasks`。**该报错虽指出了键名，但 `--help` 完全没有示例。**
  2. **`--version-binding` 的真实结构未文档化**。`--help` 同样只写 `JSON object; @file reads from disk`。实际要求含 `git_commit` / `diff_hash` / `file_hashes`（报错原文 `version_binding must be an object with git_commit/diff_hash/file_hashes`）。
- **复现证据**（本轮实际错误输出）：
  - `{"error":{"code":"invalid_input","message":"covers must be an object with files/requirements/tasks"}}`（试错 2 次）
  - `{"error":{"code":"invalid_input","message":"version_binding must be an object with git_commit/diff_hash/file_hashes"}}`
  - 最终可用形态（本轮实测成功）：`--covers @covers.json` 其中 `covers.json` = `{"tasks":["R-002"]}`；`--version-binding @binding.json` 其中含 `git_commit` + `file_hashes`。
  - 附带发现：`covers.files` 传**字符串数组**（路径）也会被拒——**其正确元素结构同样无文档**，本轮改用只传 `tasks` 绕开。
- **影响**：与 `FI-008` 第 2 点（`--scope` 无结构说明）**同类**，但更严重：证据是 format 2 的**核心事实源写入路径**，而它的两个关键参数**只能靠错误信息反推**。这会**系统性地劝退**「绑定版本哈希」这一最佳实践（本项目首次绑定 sha256 即因此卡住），使 `applicability` 长期停留在 `unknown`（见 `FI-006` 附带观察）。
- **建议**：
  1. `--covers` / `--version-binding` 的 `--help` 各给一个**最小可复制示例**；
  2. 报错信息附上期望结构的 JSON Schema 或示例；
  3. 若 `covers.files` 需要结构化元素（而非路径字符串），在文档中写明；
  4. 可考虑提供 `vibe evidence record --covers-tasks R-002 --git-commit <sha> --file-hash <path>=<sha>` 之类的**扁平参数**，避免用户手写嵌套 JSON。
- **校准说明**：本条**不是**逻辑缺陷（错误信息本身是准确的、可诊断的），属**可用性/文档缺陷**。之所以记录，是因为它**在本轮实际造成了 3 次失败**，且落在最核心的写入路径上。

---

## FI-010：`vibe validate` 不校验人读摘要，`current-session.md` 出现孤儿列表与两个互相矛盾的「下一步」

- **现象**：`.project-log/current-session.md` 的「当前状态」区块内，字段列表（`- 当前阶段` / `- 当前任务` / … / `- 下一步`）之后**混入一段没有字段名的孤儿列表**（`- DOC-003：…` / `- R-002（第二轮已完成）：…` / `- 重要决策：…` / `- 下一步：2026-10-12 按该方法论开始正式工作；用户当日汇报。`），使同一文件内出现**两个内容不同的「下一步」**。
- **复现证据**：`D:\Project\VR数采调研\.project-log\current-session.md`（**修正前**）—— 正式「下一步」字段位于**第 31–35 行**（4 条）；孤儿列表位于**第 37–44 行**，其末条为「下一步：2026-10-12 按该方法论开始正式工作；用户当日汇报」。而同一文件**第 7 行**的维护规则明确要求「不要在多份长文档里维护互相矛盾的『下一步』」。
  - 孤儿列表原文（8 项）：`- DOC-003：组合式技术路线方法论落盘…` / `- DOC-004：…` / `- DOC-005：…` / `- DOC-006：…` / `- DOC-007：…` / `- R-002（第二轮已完成）：…` / `- 重要决策：确认"按接口契约组合"替代"整项目选型"…` / `- 下一步：2026-10-12 按该方法论开始正式工作；用户当日汇报。`
  - **已于同日修正**：该孤儿列表已提取为独立会话区块「2026-10-11 第二阶段源码深挖与文档收口」，故上述行号在现场已不存在；缺陷描述与原文引用保留作为证据。
- **同时**：对该文件执行 `vibe validate` 返回 `{"errors": []}` —— **人读摘要的结构漂移完全不在校验范围内**。
- **影响**：
  - `current-session.md` 是恢复会话的第一入口；矛盾内容会让后续 Agent 读到**过期的下一步**（第 44 行那条与真实计划已不一致，本轮恢复时即需人工辨别）。
  - 规则要求一致性、工具却不校验人读文件 → 「靠纪律维持」的一致性会随会话累积而漂移，且漂移不可见。
- **建议**：
  1. `vibe validate` 增加对 `current-session.md`「当前状态」区块的**字段白名单校验**（只允许 `- <已知字段名>：`，出现无字段名的顶层列表项即报警）；
  2. 或把「当前状态」区块改为 `vibe render` 生成（机器维护），人手只写下面的会话区块；
  3. 至少在 `status` / `validate` 输出中提示「人读摘要未纳入校验」。
- **校准说明**：漂移内容由 Agent 手写产生（非工具写入），但**「规则要求一致性 vs 工具不校验」的落差**属框架问题，故记录。

---

## FI-011：框架没有「交付物形态 / 读者对象」维度，导致把证据台账当成对外交付物（**本轮被用户连续否决 2 次**）

- **现象**：本轮交付物是「给 mentor 单独阅读的调研汇报文档」。Agent 第一次沿用已有的 `调研汇报提纲.md` 结构（证据分级标记、文件行号引用、「每条判断 + 依据」），被用户否决——「不够面向人类，不够 human-made-like，里边不需要什么证据」；第二次改成口语版，但仍保留「开场建议这样说」「可能被追问的问题与备答」，再被否决——「更像是一个幕后的准备稿，汇报的时候用不到，我要的是能让 mentor 也直接看的汇报稿」；第三次把读者换成 mentor 重写才通过。
- **根因**：框架的任务/证据模型围绕**结论正确性**建模（`kind`、`applicability`、`review_verdict`、`strict` 门禁），但**缺少「交付物读者是谁」这一维度**：
  - 任务分流（quick / standard / strict）只按风险判，不按读者判；
  - Skill 路由表中没有「面向人类读者的交付文档」入口；`a-project-context-briefing` 的定位是「为另一个 AI / 队友 / 供应商整理背景」，未明确覆盖「向上汇报文档」；
  - 于是 Agent 会把「对内可追溯的证据台账」直接当成「对外可读的交付物」，且**框架在任何环节都不会提示这个错位**。
- **证据**：本轮 2 次用户否决原话（见上）；最终版 `调研汇报稿.md`（248 行）与旧版 `调研汇报提纲.md`（305 行）的结构对照——前者摘要先行、备答内容溶入正文、附录改为「候选项目一览」。
- **影响**：交付物返工 2 轮；若无人及时否决，会把内部证据台账直接交给外部读者。
- **建议**：
  1. 在交付环节增加一步**「交付物读者判定」**（内部留痕 / 上级汇报 / 外部评审 / 公众文档），据此决定是否剥离证据标记与过程语言；
  2. 新增或扩展现有 Skill：**「面向人类读者的交付文档撰写」**（读者优先、结论先行、去过程语言、局限如实披露），并纳入 Skill 路由表；
  3. 项目级 `AGENTS.md` 模板增加「交付物形态」约定位。

---

## FI-012：Windows PowerShell 文本工具的两个坑（环境层）

- **现象**（2 项，本轮实测）：
  1. **`(Get-Content $f).Count` 对 LF-only UTF-8 文件返回的行数偏小**：同一文件 `调研汇报提纲.md`，`Get-Content` 计得 **226**，而按 LF 字节计数为 **305**（`[IO.File]::ReadAllText` + 统计 `` `n ``）。另一文件同样偏小（**154 vs 220**）。
  2. **`[IO.File]::ReadAllText("相对路径")` 在 PowerShell 中失效**：`cd` 只改变 PowerShell 的位置，**不改变 .NET 的当前目录**，因此相对路径报 `FileNotFoundException`（本轮实际发生一次）。
- **影响**：第 1 项会**直接产出错误的行数/规模结论**（本轮差点把 305 行的文件报成 226 行）；第 2 项会造成「文件不存在」的误判。
- **建议**：文档中提示——统计行数改用 `(Select-String -Path $f -Pattern '').Count` 或按 `` `n `` 字节统计；调用 .NET API 一律传**绝对路径**。
- **校准说明**：属环境层（同 `FI-005`），非框架逻辑缺陷；因本轮实际造成错误数值，故记录。

---

## 记录状态

| 编号 | 状态 | 证据强度 |
| --- | --- | --- |
| FI-001 | 确定（运行时确定性报错，可复现） | 强 |
| FI-002 | 确定（subagent 自报权限拒绝；**本轮再次复现 5 次**——5 个 `codebase-onboarder` 均无 `shell`） | 强 |
| FI-003 | **已澄清：非逻辑缺陷，属命名歧义** | 强（源码级） |
| FI-004 | 确定（静态复核） | 中 |
| FI-005 | 确定（本会话多次复现） | 强 |
| FI-006 | 确定（源码 + 本会话实际观测） | 强 |
| FI-007 | 确定（`status` 输出 `goal_id: null` + 源码路径；未复核 init stdout） | 中 |
| FI-008 | 确定（4 项：`next_action` 不可写 / `--scope` JSON 无说明 / `partial` 非合法枚举 / review 不可重录且裁决被覆盖） | 强（本轮实际错误输出） |
| FI-009 | 确定（2 项：`--covers` 结构无文档 / `--version-binding` 结构无文档；本轮 3 次实际失败） | 强（本轮实际错误输出） |
| FI-010 | 确定（`current-session.md` 第 31–35 行 vs 第 37–44 行两个「下一步」并存；`validate` 返回 `{"errors": []}`） | 强（文件可定位） |
| FI-011 | 确定（本轮 2 次用户否决原话 + 两版交付物结构对照） | 中（属能力/路由缺口，非运行时缺陷） |
| FI-012 | 确定（2 项：`Get-Content` 行数偏小 226/305 与 154/220；`ReadAllText` 相对路径失效） | 强（本轮实际复现） |
