# Vibe-Coding 框架缺陷记录

> **用途**：按项目 `AGENTS.md` 的规则（2026-10-10 新增）——「过程中发现什么 vibe-coding 框架缺陷及时记录，方便后续我优化框架」——把工作过程中**实测**到的框架缺陷就地记录，便于后续单独修复。
>
> **位置**：`D:\Project\Transformer-Koopman\.project-log\docs\framework-defects.md`（随事实源保存；本文件**不被**内层论文仓库跟踪）。
>
> **编号**：`D-010` 起。`D-001`–`D-009` 见桌面 `Vibe-Workflow-框架缺陷清单-v2.md`（`DEC-065` 整合）与 `DEC-046`（7 条）；本文件**不重复**它们，只做增量登记，并在末尾给出对照索引。
>
> **记录要求**（每条必须有）：现象 / 复现 / 代码位置（文件:行）/ 影响 / 建议修法 / 状态。**未核实的推断必须显式标为「推断」**，不得与实测事实混写。

---

## D-010 `record create --payload` 静默接受 state-apply 信封

**现象**：把 `state-apply` 用的完整信封（含 `action`/`command_id`/`expected_revision`/`payload`）当作 `record create --payload` 的内容对象传入时，CLI **不报错**，把整个信封存成记录内容；真实内容被嵌到 `payload.payload` 里。

**复现**：`vibe record create --kind decision --id DEC-X --payload @envelope.json`，其中 `envelope.json` 是 state-apply 信封 → 记录建成，内容错位。

**影响**：记录是 append-only（无法删除），只能事后用 `record update --payload` 把内容合并到顶层。本会话 5 条记录中招；本项目 191 条历史记录均为 bare 形式。

**建议修法**：`record create` 对 `--payload` 做形状校验——顶层若出现 `action`/`expected_revision`/`command_id`/`expected_generation` 等信封键即报错并提示「这看起来是 state-apply 信封」；或另设 `--envelope` 参数以区分两种用法。

**状态**：已登记（`DEC-077`），**未修**。

---

## D-011 门禁读 `extensions.risk`，框架自己的路由/实践写 `risk_class` → 高风险任务被静默降级（fail-open）

**现象（2026-10-10 本次实测）**：新建 `TASK-034`，其 `extensions.risk_class = "high"`（按本项目 33/41 个任务的既有写法）；随后 `vibe gate --task TASK-034` 返回

```json
{"task_id":"TASK-034","decision":"allowed","blocking":[],"notes":[]}
```

**未要求独立复核**，也没有任何提示说明风险等级未被识别。同一任务若把键写成 `extensions.risk = "high"`，按代码路径应当被当作 strict 并要求 go 复核（**推断**，未构造对照任务实测）。

**代码位置（已逐行核对）**：

| 位置 | 内容 |
|---|---|
| `scripts/state_store.py:75` | `STRICT_RISKS = ("strict", "high", "critical")` |
| `scripts/state_store.py:1197-1203` | `_is_strict(extensions)`，docstring 写 *"Whether a task counts as strict, in either risk vocabulary"*，但函数体只读 **`extensions.get("risk")`**（或 `verification.level >= 3`）。所谓 "either vocabulary" 指的是**取值**同时接受路由词表（`strict`）与目标词表（`high`/`critical`），**不是**键名兼容 |
| `scripts/state_store.py:1764,1767` | `risk = extensions.get("risk")` / `strict = Store._is_strict(extensions)`（位于 `_task_completion_problems`，即任务级完成检查） |
| `scripts/state_store.py:1238-1250` | `gate_task()` 调用上面的检查并返回 `decision` |
| `scripts/vibe.py:491-492` | `elif args.command == "gate": result = open_store(root, heal=True).gate_task(args.task)` —— 即 `vibe gate --task` 的实现 |
| `scripts/state_routing.py:144-153` | 路由函数的返回键是 **`class`**；任务扩展里普遍写的键是 **`risk_class`** |

**实测分布（全项目 41 个任务的 `extensions`）**：`risk_class` 出现 41 次、`risk` 6 次、`risk_note` 9 次、`implementer` 41 次、`owner` 9 次。取值：`risk_class=strict` 20、`risk_class=high` 7、`risk_class=standard` 9、`risk_class=quick` 4、`risk_class=medium` 1、`risk=high` 6。

**影响（fail-open，最严重的一条）**：**只写 `risk_class` 的任务（35/41）在门禁里从未被当作 strict/high** → strict 才会强制的三项要求（独立 go 复核、证据版本绑定、strict 证据覆盖）都不会被触发。这与 `state_gate.py:204` 的设计目标 *"never silently passes"* 直接相反，而且**没有任何告警**。

**附加影响（无法补正）**：`task.update` 只接受 `--implementer` / `--owner`（`scripts/vibe.py:42-49`；`state_store.py:2119` 注释 *"Only attribution is mutable here"*）→ 任务建成后**无法**补写或修正风险键，只能重建任务或放弃强制。

**建议修法**：
1. `_is_strict` 同时接受 `risk` 与 `risk_class`；或在 `task.create` 时把 `risk_class` 规范化写入 `risk`。
2. `vibe gate --task` 在调用方未显式给出风险等级时，**默认取任务自身的 extensions**，而不是当作无风险。
3. 任务**未声明任何风险键**时 **fail-closed**（与 `state_routing.py:143` 的立场一致：*"no signals were declared, so low risk was not assumed"*）。
4. 允许 `task.update` 修正 extensions 中的风险键（至少在键名拼错时）。
5. 至少给一条 warning：任务声明了 `risk_class` 但门禁未识别。

**状态**：本次实测登记，**未修**。规避手段（当前会话采用）：不依赖门禁强制，**自愿**执行独立复核并手动记录 verdict。

---

## D-012 schema 报错不指名缺哪个字段，允许键集合无文档

**现象**：
- `state-apply` 漏 `schema_version` / `expected_generation` 时报 `Operation envelope has missing or unknown fields`（**不指名**缺哪个）；
- `task.create` 的 `payload` 多带 `next_action` 或 extensions 多带自定义键时报 `task.create payload has missing or unknown fields`（**不指名**允许哪些）。

**复现**：手写一个只含 `action`/`command_id`/`expected_revision`/`payload` 的信封 → 第一条报错；把 done_when 等自定义键放进 `task.create` 的 extensions → 第二条报错。

**影响**：每次手写信封都要靠回读 `commands.request_json` 反推形状（本次为建 8 个任务，先失败 10 次才探明）。CLI 无法自描述。

**建议修法**：报错指名键名（`missing: schema_version`、`unknown: next_action`）；`--help` 或 `framework-info` 输出各 action 的**允许键集合**与必填项。

**状态**：本次登记，**未修**。

---

## D-013 记录内容对只读复核者不可达（单行超长 JSONL + 二进制 SQLite）

**现象（由 `verification-reviewer` 在 `TASK-034` 复核中实测报告）**：事实源把完整记录 payload 存为**单行 JSONL**（`ledger.jsonl`），`read`/`grep` 对超长行**截断到 2000 字符**；`state.sqlite3` 对 ripgrep 报 `Invalid ripgrep match output`（二进制文件）。

**后果**：只读复核者**无法取回 `ARCH-002` 里 `TASK-034` 的完整 `done_when` 契约**，只能读到前两项 → 复核矩阵被迫退化为「对照计划书」而不是「对照验收契约」。这是**每个 strict 任务都会遇到的系统性缺口**，且复核者没有任何办法绕过（它没有 shell）。

**建议修法**：
1. 增加 `vibe record show --id <id>`（把 payload 落到独立文件）或 `vibe record export`；
2. 生成视图（`generated/`）里对长记录额外产出一个可 `read` 的独立文件；
3. 至少在 `vibe context <task>` 里把当前任务的 `done_when` 契约展开成可读文本。

**状态**：本次登记，**未修**。

**附（2026-10-11 本轮追加佐证，`TASK-035`/`TASK-040`/`TASK-041`）**：本轮共发起 **6 次**独立复核（`REV-TASK035-001/002/003`、`REV-TASK040-001/002`、`REV-TASK041-001`），**每一次都报告无法执行 shell**，措辞分别为 `permission.rejected: shell` 与「本会话 shell 被拒」。因此只读复核者**不仅**读不到长记录（原记录的现象），**还完全无法运行任何核验命令**：

- 无法复算 `sha256` / 字节数 → 只能把交付物里写的哈希**与账本既往证据对拍**（`TASK-041` 的复核者正是这样做的，并如实标注「非本机重算」）；
- 无法跑 `git` → 「本阶段未改 `论文/`」这类结论**只能由主 Agent 把原始输出写进证据**；
- 无法运行验证脚本 → `TASK-040` 的复核者明确写下「『数值可复现』这一条我未能独立确认，只确认了『产生这些数值的公式正确且自洽』」。对**以数值为证据**的 strict 任务，这是实质性的复核能力缺口。

**补充观察（新）**：复核者的 shell 能力**不稳定**。`TASK-035` 第二轮的复核者报告「首个哈希命令成功，其余被 allowlist 拒绝」——即同一会话内**部分命令可用**。这比「完全没有 shell」更难预判：主 Agent 无法假定复核者能或不能跑某条命令。

**本轮采用的规避**（供框架参考）：主 Agent 主动把**原始输出**写进 evidence 的 subject —— 交付物的全量哈希、`git rev-parse`/`git status --porcelain` 的逐字输出、验证脚本的运行结果与自检数值；并在复核 prompt 里**贴入契约原文**（`done_when`）与**能力边界声明**，让复核者不把「做不到」误判为 `no-go`。

**建议修法（在原 3 条之外新增）**：
4. 给 `verification-reviewer` 一条**受限但确定**的命令白名单（例如 `git status`/`git diff --stat`、`certutil -hashfile` 或 `sha256sum`、以及**指定**的验证脚本），而不是全有或全无；
5. 提供 `vibe verify --task <id>` 形式的**统一复核入口**：由框架自己跑版本绑定核对与指定验证脚本，把结果以文本形式交给复核者，从而不依赖它的 shell 权限；
6. 复核者的能力（有无 shell、白名单内容）应当**在 prompt 里由框架自动声明**，避免主 Agent 每次手工交代。

**状态（附）**：本轮实测登记，**未修**。

---

## D-014 `evidence refresh` 的语义与名字不符，且作用域是全项目

**现象（2026-10-10 实测）**：`vibe evidence refresh --reason "..."`（`--help` 显示只有 `--reason`，**没有 `--id`**）**不重算版本绑定**，而是扫描**整个项目**、把已 stale 的证据批量标记。本次一条命令扫出并 invalidate 了 13 条（含 `EV-TASK034-MODEL-001`、`EV-TASK029-CLARIFY-001`、`EV-TASK031-DELMAIN-001`、`EV-ALN014-001` 等）。事后查库：`EV-TASK034-MODEL-001` 状态为 `stale`，其 `version_binding.file_hashes` **仍是旧哈希**。

**后果**：
1. 名字暗示「刷新绑定」，实际是「失效清扫」→ 使用者会以为绑定已更新，**实际没有**；
2. 无法只针对一条证据操作（无 `--id`）；
3. **无法把证据重新绑定到新字节** → 唯一可行路径是**新建一条证据**（本次用 `EV-TASK034-MODEL-002` 绑定修改后的字节）；旧证据永久留在 `stale`（不可删除，这是设计，非缺陷）。

**建议修法**：
1. 把该命令改名（如 `evidence sweep-stale`），或让它接受 `--id` 并语义化为「重算该证据的 file_hashes」；
2. 增加 `evidence rebind --id --file-hashes`；
3. `--help` 里写明它作用于**整个项目**而非单条。

**状态**：本次实测登记，**未修**。

**附（同一次实测）**：`vibe record show` **不存在**（`record` 只有 `create/update/link`）→ `D-013` 的建议 1 是「**新增**」命令而非「修复既有」。

---

## D-015 CLI 参数形态不一致 + `expected_revision` 语义无文档

**现象（2026-10-11 本轮实测，三次踩坑）**：

1. **`state-apply` 的 `--file` 要裸路径，其它命令要 `@file`**。`vibe state-apply --file @x.json` 报
   `[Errno 22] Invalid argument: '@C:\\...\\x.json'`；而 `evidence record --covers @x.json`、`review record --scope @x.json`、
   `goal update --success-conditions @x.json`、`record create --payload @x.json` **都**用 `@file`。同类参数两种约定，无提示。
2. **`state-apply` 信封的 `expected_revision` 语义与直觉相反**：实测必须填**写入前的当前** `metadata.local_revision`，
   填「当前 +1」会被拒（`stale_revision: Expected revision 991; current is 990`）。命令名 `expected_*` 暗示「预期当前值」，
   但项目内笔记与常识容易写成「+1」，报错信息也不解释语义。
3. **`goal` 没有只读状态子命令**：`vibe goal --help` 只有 `create/update/complete/cancel`，无法直接读回成功条件状态；
   本轮只能直接查 SQLite（`SELECT extensions FROM goals WHERE id=...`）来核对 `goal update` 是否生效。
4. 附带：`record create` 实际还需要 `--title` 与 `--status`（help 里没在错误信息中提示到「缺哪些」以外的东西，
   首次调用只报 `the following arguments are required: --title, --status`，属于可用但需试错）。

**影响**：每次踩坑都要重跑一次外部进程；`expected_revision` 的错误语义尤其危险——若某次「+1」恰好等于当前值，
写入会被静默接受，而执行者对语义的理解仍是错的。

**建议修法**：
1. 统一 `@file` 约定（或两种都接受），并在 `--help` 里写明；
2. 把 `expected_revision` 的语义写进 `--help` 与错误信息（例如 `Expected revision 991 (the revision you read before writing); current is 990`）；
3. 给 `goal` 加只读的 `status`（或让 `vibe status` 输出成功条件状态）；
4. 错误信息列出**全部**必需参数（D-012 的同类问题）。

**状态**：本轮实测登记，**未修**。

---

## D-016 `evidence record` 的 `--covers` / `--version-binding` schema 无文档，`file_hashes` 的路径基准靠试错

**现象（2026-10-11 本轮实测，连续 3 次被拒才成功）**：`evidence record --help` 对两个参数只写
`JSON object; @file reads from disk`，不说明必需键。实测逐次暴露：

1. 第一次（内容对象形状）：`covers must be an object with files/requirements/tasks`；
2. 第二次（版本绑定形状）：`version_binding must be an object with git_commit/diff_hash/file_hashes`；
3. 第三次（路径基准）：`version_binding.file_hashes keys must name existing files, given as an absolute path or relative to the project root; unresolvable: controllers/ltv_mpc.py, ...`
   —— 即键必须写成**相对项目根**（`Transformer-Koopman/杂项/…/controllers/ltv_mpc.py`），而不是相对该文件所在目录或实验根。

**影响**：每次都要多跑一次外部进程；路径基准只能从报错文案反推，`--help` 完全没提。这与 D-012（schema 报错不指名）同源，但更具体：**报错文案本身是对的，缺的是前置文档**。

**建议修法**：把 `covers` / `version_binding` 的 schema 与路径基准写进 `--help`（或提供 `vibe evidence schema` 子命令）；`--covers` 与 `--version-binding` 支持一次 `--help` 输出示例 JSON。

**状态**：本轮实测登记，**未修**。

---

## D-017 框架没有「工作留痕」记录种类，`a-work-trace` 的产物无处安放

**现象（2026-10-11 本轮实测）**：按 `a-work-trace` 的契约整理 Context–Hypothesis–Decision–Action–Observation–Result–Lesson 链条后，用
`vibe record create --kind work_trace` 写入，被拒：`unsupported_record_kind: Unsupported record kind: 'work_trace'`。
逐行核对 `state_store.py` 的 `RECORD_KINDS`，实际只有 `business-atom / requirement / decision / architecture / research / alignment / open-question / retrospective / distillation`。
本轮只能把留痕塞进 `research`（`RESEARCH-001`），语义不完全匹配。

**说明（推断）**：Skill 描述未规定应使用哪个 kind，因此**不能断定**这是实现与契约的直接冲突；可以确定的是「工作留痕」在记录种类表里**没有一等公民**，而 Skill 层把它当作应记录的产物。标为推断的部分：设计者可能有意让留痕走 `research` 或生成视图。

**建议修法**：要么在 `RECORD_KINDS` 增加 `work-trace`（状态可用 `active`/`archived`），要么在 `a-work-trace` 与 CLI `--help` 中明确「留痕使用 `research`（或指定 kind）」，避免每个执行者各自试错。

**状态**：本轮实测登记，**未修**。

---

## D-018 生成式报告一旦被 evidence 绑定，重新生成即让**全部**证据 stale（证据链自我干扰）

**现象（2026-10-11 会话实测，连续两次）**：`reports/modeling_comparison.md` 与
`reports/control_comparison.md` 是脚本从 `results/**` 生成的视图。把它们写进 `--covers` 后，
任何一次重跑报告生成器（例如仅修正一处措辞、或补一段新的 gate 小节）都会改变这些文件的字节，
于是 `evidence refresh` 把**覆盖同一份报告的所有证据**一次性标为 `stale`——本轮第一次让
`EV-GATE1-MODELS-001` / `EV-GATE3-QP-001` 失效，第二次（仅 3 处措辞修正）又让刚刚重建的
`EV-GATE1-MODELS-002` / `EV-GATE2-DIAG-001` / `EV-GATE3-QP-002` / `EV-GATE4-CONTROL-001` /
`EV-GATE5-FREEZE-001` 全部失效，必须再建 5 条新证据（`-003` / `-002` 系列）才能重新过门禁。

**说明（推断）**：这是「证据绑定不可变字节」与「报告是派生产物」之间的结构性冲突，不是执行错误。
派生产物天然会随生成器/上游数据演进而变化，把它当作验收证据的稳定锚点，会把**任何**上游微调
放大成一次完整的证据重建。两次重建合计消耗约 6 条证据记录与 2 轮复核确认。

**建议修复（任一）**：
1. 证据绑定支持「生成式派生对象」语义：记录生成器脚本 + 上游输入的哈希，而非产物字节；
   产物变化时只要生成器与输入未变即不判 stale。
2. `evidence record` 增加 `--derive-from`（生成命令）字段，`refresh` 据此区分
   「派生对象被重新生成」与「实质内容变化」。
3. 至少在文档/`--help` 中明确建议：**只绑定稳定输入（结果 JSON、代码、配置），
   不绑定生成式报告**；报告由复核者按契约逐条核对。

**状态**：本轮实测登记，**未修**。

---

## D-019 `record create` 要求 `--title`/`--status`，但每个 kind 的合法 status 无任何文档

**现象（2026-10-11 会话实测）**：`vibe record create --help` 只列出
`--kind/--id/--title/--status/--payload`，不给出合法值。
按 `a-work-trace` / `a-project-log` 的写法填 `--status active` 时被拒：
`Status 'active' is not valid for record kind 'research'`。依次试 `recorded`、`final`、`open`
同样被拒，试到第 5 个 `draft` 才成功；`--help` 全程未提供任何候选值，错误信息也不列出合法集合。

**说明（推断）**：合法 status 集合按 kind 不同而不同（至少 `research` 不接受 `active`），
但该映射既不在 `--help`，也不在错误信息里，也不在 Skill 中。执行者只能靠试错，且**无法判断**
某个被接受的 status 是否语义正确（例如 `research` 的 `draft` 是否意味着「未完成」）。

**建议修复**：
1. `record create --help` 按 `--kind` 列出合法 `--status` 取值；
2. 校验失败的错误信息中回显合法集合（当前只说「不合法」）；
3. 若 `draft` 表示未定稿，应在 `vibe status` / `render` 中体现，避免记录实际已完备却被标为草稿。

**状态**：本轮实测登记，**未修**。

---

## D-020 `write` 工具落盘的 `.ps1` 无 BOM，而 PowerShell 5.1 按 ANSI/GBK 读取 → 中文字面量路径被静默损坏（本项目路径**全部**含中文）

**现象（2026-10-11 本轮实测，直接毁掉一个后台等待器）**：用 `write` 工具生成的 `wait_transient_arm.ps1` 内含一行
`$exp = "D:\Project\Transformer-Koopman\Transformer-Koopman\杂项\新版本\Temporary_Experiments"`。
执行后 PowerShell 报
`Set-Location : 找不到路径"D:\Project\Transformer-Koopman\Transformer-Koopman\杂项\新版本\Temporary_Experiments"，因为该路径不存在。`
——**报错文案里的路径看起来完全正确，目录也确实存在**，但解析结果实际是错的。

**根因（已逐字节核实）**：两个 `.ps1` 的前 4 字节均为 `23 20 57 61`（`# Wa`）→ **无 BOM**。
PowerShell 5.1 对**无 BOM** 的脚本按**系统 ANSI 代码页**（本机 936/GBK）解码，而文件实际是 UTF-8，于是
`杂项\新版本` 的字节序列 `E6 9D 82 E9 A1 B9 5C E6 96 B0 …` 被按 GBK 双字节切分，
**GBK 前导字节把紧随其后的 `\`（0x5C）当成尾字节吞掉** → 路径中的反斜杠消失 → 路径不存在。
错误信息之所以「看起来对」，是「UTF-8 字节 → 按 GBK 误解 → 再按 GBK 输出到控制台」的**双重转换恰好还原**了原字符
（复核方式：用 `[char]0x6742` 等码点**运行时构造**同一路径，`Test-Path` 才给出可信答案）。

**后果**：`Set-Location` 失败后脚本**继续执行**（`$ErrorActionPreference="Continue"`），
探针以调用方默认 CWD 运行 → `scripts\probe_*.py` 找不到 → Python `rc=2`，
重试 4 次全部失败，等待器**静默空转 15 分钟后退出**，而唯一的日志线索只是那行误导性的中文报错。
同一缺陷**同时存在于当时正在运行的另一个等待器**（`wait_and_probe.ps1`，同样无 BOM），
即：会在数小时后真正需要它时失效——属于**延迟引爆**类缺陷。

**影响面（本项目特有）**：本项目的**实验目录路径本身含中文**（`杂项\新版本\Temporary_Experiments`），
因此**每一个**引用该路径的 `.ps1` 都会中招；而框架鼓励「把脚本落盘后执行」（`a-*` 系列 Skill 与项目约定均如此），
却没有对 PowerShell 的编码行为给出任何提示。

**规避手段（本轮已采用，已验证）**：
1. `.ps1` **一律纯 ASCII**（本轮核对：`wait_and_probe2.ps1` 非 ASCII 字节数 = 0），
   中文路径改从 UTF-8 文本文件读取：`(Get-Content -LiteralPath $p -Encoding UTF8 -Raw).Trim()`
   —— 显式 `-Encoding UTF8` 可正确解码**无 BOM** 的 UTF-8，绕开脚本自身的解码问题；
2. 或者把 `.ps1` 落盘为 **UTF-8 with BOM**（`utf-8-sig`）；
3. 脚本启动时**自证**：打印 `exp=[...]; exists=True/False`，并在 `False` 时 `exit 1`，不静默继续；
4. 用**绝对脚本路径**调用，不依赖 CWD。

**建议修法**：
1. `write` 工具对 `.ps1`/`.bat`/`.cmd` 扩展名**默认写入 UTF-8 with BOM**（或提供 `bom: true` 选项）；
2. 框架文档/`b-*` Skill 增补一条「Windows PowerShell 脚本落盘编码」检查项；
3. 通用原则：**任何「落盘后由另一解释器执行」的产物，都要显式声明编码**，不要假定解释器会用 UTF-8。

**附（非框架缺陷，执行者自身错误，一并记录以免复现）**：同一等待器还有一处**自我匹配**缺陷——
它在启动日志里写了 `waiting for 'waiter v2 done'`，而等待循环正是用
`Select-String -Path $log -Pattern "waiter v2 done" -Quiet` 探测该字符串 → **第一条日志就让循环立刻 break**，
等待器在 1 秒内「完成」。修法：哨兵不要出现在自己的日志里，或改用**标记文件**握手（本轮已改为标记文件）。
教训：**等待器的完成判据必须与它自己的输出不相交**。

**状态**：本轮实测登记，**未修**（规避手段已生效）。

---

## D-021 后台 shell 无管理能力；进程被外部杀死后条目变「僵尸」，且工具不回收

**现象（2026-10-11 本轮实测）**：以 `background: true` 启动的两个后台 shell（机械臂驱动 `run_arm_all.py` 的启动 shell、探针等待器 `wait_and_probe2.ps1`）在系统虚拟内存耗尽事件中被静默杀死。此后：

1. **UI/工具侧仍显示它们「在运行」**——主 Agent 从未收到这两条 shell 的完成通知；
2. 主 Agent 逐一核查：`Get-CimInstance Win32_Process` 全量扫描（不限进程名）确认**没有任何**相关进程存活，`arm_all.log` / `leak_wait.log` 的最后写入时间分别冻结在 `17:18:53` / `17:20:43`（即死亡时刻）；
3. **无法主动清理**：`search` 全量检索工具目录后确认，**不存在**列出/终止/清理后台 shell 的工具（`tools.opencode` 仅有 `session_move`、`session_rename`、`models`、`list_mcp_resources`、`read_mcp_resource`）。唯一的"停止"手段是杀进程，而对已死进程无效。

**影响**：用户与主 Agent 对「当前是否有后台任务在跑」的判断**出现分歧**，且主 Agent 无法用工具自证清白——只能靠 `Get-CimInstance` + 日志时间戳间接举证。若用户据此等待"后台任务结束"，会造成无谓的长时间空等（本轮用户即提出「先停止后台的两个 shell 任务」，而它们其实早已死亡）。

**建议修法**：
1. 增加只读的 `shell list`（含 pid、启动时间、最后输出时间、存活状态），以及 `shell kill <id>`；
2. 后台 shell 的宿主进程应被**主动监视**：宿主消失即标记为 `terminated`（携带退出码或"被外部终止"），而不是等管道 EOF——本次管道可能被子进程句柄持有，导致永不 EOF；
3. 完成/失败通知应区分 `completed` / `killed` / `lost`，并在 `lost` 时提示「进程已不存在，条目为陈旧记录」。

**状态**：本轮实测登记，**未修**。

---

## D-022 角色模型不可用在委派后才报错，缺少可用性预检

- **观察（2026-10-12 / TASK-048）**：委派implementation-builder返回`Model unavailable: llmcenter/claude-opus-5`，子任务未启动、未产生写入。主Agent按相同边界采用`serial-role-fallback`，独立alignment-reviewer角色仍可运行。
- **边界**：只确认该次配置/运行时失败；未判定是模型下架、配置过期或provider暂时不可用，不把原因猜测成事实。
- **影响**：批准的并行切片被打断，若误将“已委派”当作执行成功会丢失任务；实现与复核模型的可用性必须分别判断。
- **建议候选**：任务开始前做角色模型可用性预检，失败明确返回可选角色或串行回退；不自动换未经许可模型，不放宽复核权限。本轮不修改全局配置。
- **证据**：子会话`ses_ecf681fdeffeJYqXHwzVKdO4II`错误返回；原理论基线hash检查仍一致，随后由主Agent编辑。

## 对照索引（与既有缺陷文档的关系）

| 来源 | 覆盖范围 | 本文件是否重复 |
|---|---|---|
| `DEC-046` | 任务与目标不可取消/删除；goal 门禁 review 判据不一致（7 条） | 否（`D-001`–`D-009` 见该记录与桌面清单） |
| 桌面 `Vibe-Workflow-框架缺陷清单-v2.md`（`DEC-065`） | 整合版 v2，每条已复核 | 否 |
| 桌面 `2026-10-10-工具链缺陷报告-高风险任务无法闭合.md` | 高风险任务无法闭合 | **部分相关**：`D-011` 从门禁代码层面给出其根因（风险键名不匹配），两者应合并阅读 |
| 本文件 | `D-010`–`D-014`（2026-10-10 会话实测；`D-013` 于 2026-10-11 追加复核者无 shell 的佐证）；`D-015`–`D-019`（2026-10-11 本轮实测）；`D-020`（`write` 无 BOM + PowerShell 按 GBK 读 → 中文字面量路径损坏）；`D-021`（后台 shell 无管理能力、外部杀死后条目变僵尸） | — |

> 注：`D-010` 与 `D-011` 的**完整证据**同时保存在状态库的记录里（`DEC-077` / 本文件），`D-013` 的原始观察来自 `verification-reviewer` 的复核报告（`REV-TASK034-*`）。


---

## D-023 strict 任务 `task finish` 被门禁拒绝时，错误里不含「下一步该做什么」

- **观察（2026-10-13 / TASK-054 实测）**：`evidence record` 成功（revision 1148）后调用 `task finish`，
  返回 `{"error":{"code":"task_gate","message":"Task completion rejected: high-risk task TASK-054 lacks an
  independent review"}}`（消息被截断）。单独运行 `vibe gate --task TASK-054` 才得到结构化的
  `{"decision":"blocked","blocking":["high-risk task TASK-054 lacks an independent review"]}`。
- **影响**：错误只说明「缺什么」，不说明「怎么补」。Agent 需要自己推断是跑 `vibe gate`、补 `review record`
  还是补证据；截断的消息更容易被误读成证据问题而重复记录证据。
- **建议**：`task_gate` 错误体里带 `next_commands`（例如 `vibe gate --task <id>`、
  `vibe review record --task-id <id> ...`）与 `required_evidence_kinds`；至少不要把消息截断到看不见原因。
- **状态**：本次实测登记；未修。

---

## D-024 `evidence invalidate` 无法把已 `stale` 的证据转为 `invalidated`，且报错措辞与状态不符

- **观察（2026-10-13 / TASK-054 实测）**：编辑了一个被证据绑定的 `.md` 后，框架自动把
  `EV-TASK054-PAPER-001` 置为 `stale`（receipt：`evidence.invalidate`，
  reason = `tool edit modified .project-log/docs/task057-reference-verification.md`，revision 1149）。
  随后手动执行 `vibe evidence invalidate --id EV-TASK054-PAPER-001 --reason ...`，返回
  `{"error":{"code":"state_conflict","message":"Evidence is already invalidated: EV-TASK054-PAPER-001"}}`，
  而该证据的实际状态是 `stale` 而非 `invalidated`。
- **影响**：想显式作废并写明理由时无法操作，只能换新 ID 重新记录（本次改用 `EV-TASK054-PAPER-002`），
  于是「stale 的证据」与「invalidated 的证据」在账本里无法区分意图；报错措辞也会让人以为状态已经变了。
- **建议**：允许 `stale -> invalidated` 的显式转换（保留原 stale 理由并追加新理由）；或让报错返回当前
  `status` 与「如需作废请用哪个命令」，避免状态名与消息互相矛盾。
- **状态**：本次实测登记；未修。

---

> 覆盖范围更新：本文件已记录 `D-010`–`D-024`（`D-023`、`D-024` 为 2026-10-13 会话实测）。
