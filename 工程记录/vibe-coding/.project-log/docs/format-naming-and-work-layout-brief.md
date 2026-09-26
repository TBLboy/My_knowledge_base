# 背景简报：Vibe Coding 框架的「Format 命名」与「工作目录布局」不一致

> 用途：提交给外部模型（GPT）做方案评估。每条材料标注 **已确认 / 假设 / 未知 / 需要帮助**。
> 本机路径为本地信息，外发前请按需脱敏。未核实项一律显式标注，不用推测补空。

---

## 一、目标与确切问题

我维护一套个人自用的 AI 编码工作流框架 **Vibe Coding**（0.6.0）。它把工程日志（Project Log）作为事实源，围绕它做任务、证据、复核门禁。现在有两处设计不一致，想听你的判断。

**问题 A（命名不一致）**：框架里同时出现 `format 1 / format 2 / format 3`。我自己的冻结设计文档把这一代设计命名为 **Format 3**，但机器契约里只有 `format 1/2`（`state-format.json` 写 `{"format": 2}`）。请判断根因，并给出统一命名方案。

**问题 B（布局不唯一）**：冻结设计规定"工作目录与 `.project-log` 都是普通目录，不是 Git 仓库，远端载体是知识库（KB）"。但**代码仍同时支持"Git 仓库内"布局**，且 `vibe init` 不拒绝。我希望只保留普通目录这一种，并让 AI Agent 不再提出另一种。请判断：该"只在策略/文档层锁死"，还是"加代码守卫"，还是"彻底删除另一种模式"。

**需要的具体产出**：(1) 根因判断对错；(2) 命名统一方案（含是否把 format 3 正式注册）；(3) 问题 B 的推荐强度与风险排序。

---

## 二、系统与项目背景

### 是什么

**已确认**：框架版本 0.6.0，CLI 为 `vibe.py`。数据分两层：

- **账本（ledger）**：追加写、带 SHA-256 哈希链的 JSONL，是唯一持久事实源。
- **SQLite 投影**：本机缓存，可删除、可由账本重放重建。

**已确认**：一个"工作目录（work folder）"可容纳多个代码仓库作为子目录；`.project-log/` 放在工作目录根，覆盖其下所有仓库与分支。

### 已冻结的设计文档（关键，之前被忽略）

**已确认**：`.project-log/docs/format3-final-plan.md`（2026-09-22 定稿）是这一代的冻结设计，标题就叫 **「Format 3 最终方案」**。其目标架构图原文：

```text
work/                              # 普通目录，本身不是 Git 仓库
├── .project-log/                  # 普通目录，本身不是 Git 仓库
│   ├── ledger/                    # 追加式账本，Git 跟踪（经 KB）
│   ├── docs/                      # 长文档正文，Git 跟踪（经 KB）
│   ├── state-format.json          # 格式标记
│   ├── .gitignore                 # 忽略 .state/
│   └── .state/                    # 本机 SQLite 缓存，永不归档
├── AGENTS.md
├── repo-a/                        # 独立代码仓库
└── repo-b/                        # 独立代码仓库
```

其六条设计决定的前两条（原文）：

1. **`.project-log` 是普通目录，不是 Git 仓库。** 做成仓库会引入归档时的 gitlink 陷阱，且本地无远端仓库不提供任何耐久性。
2. **日志的远端载体是知识库（KB）仓库。** 归档时把 `.project-log` 内容复制进 `<kb>/工程记录/<work文件夹名>/.project-log/`，由 KB 提交推送。

其"明确不做"一节原文包含：**不把 `.project-log` 做成 Git 仓库**、不把 SQLite 或 checkpoint 提交进 Git。

**已确认**：该文档第七节已实测记录：`exchange export` 在非 Git 目录直接报 `git_context_error`，现有快照机制在 work 布局下不可用。

**已确认**：另有一份更早的背景简报 `.project-log/docs/git-tracked-log-storage-brief.md`（0.5.0 时代），是催生 Format 3 的输入，记录了"format 2 把事实源搬进本机 SQLite，日志从随仓库走退化为只在本机"这一回退。

---

## 三、期望行为 vs 实际行为

### 问题 A：命名

**期望（已确认，来自冻结设计）**：这一代设计叫 Format 3；`.project-log` 是普通目录；远端靠 KB。

**实际（已确认，来自代码）**：

```json
$ vibe version
{"framework_version":"0.6.0","default_format":2,"store_schema":3,
 "supported_formats":[1,2]}
```

- 代码只注册 `format 1`（legacy）与 `format 2`（事务性，默认）；**没有 format 3**。
- 持久化标记 `.project-log/state-format.json` 为 `{"format": 2, "project_id": "..."}`。
- 但 `store_schema = 3`（SQLite `metadata.store_schema`，CHECK 约束）。
- 而文档/注释里"Format 3"出现 9 处，把它当作**整代设计的名字**在用。

**五条互相独立的版本轴（已确认）**：

| 轴 | 值 | 持久化位置 | 含义 |
|---|---|---|---|
| Project Log 格式 | 1=legacy，2=默认 | `state-format.json` 的 `format`；`DEFAULT_FORMAT=2`、`SUPPORTED_FORMATS=(1,2)` | 日志整体格式 |
| SQLite 存储 schema | 3 | SQLite `metadata.store_schema`；`STORE_SCHEMA=3` | 状态库表结构 |
| 命令信封 schema | 1 | 每条命令 `schema_version`；`SCHEMA_VERSION=1` | 写入信封 |
| 账本 schema | 1 | 每个 ledger event `schema_version`；`LEDGER_SCHEMA_VERSION=1` | 账本事件 |
| 快照/视图 schema | 1 | exchange/view 指针 `schema_version` | — |

**连锁后果（已确认）**：我另一个项目的 AI Agent 读到"账本由 Git 跟踪"后，把 `format 2` 理解成"账本被 Git 跟踪的模式"，并建议我把日志放进一个 Git 仓库——与冻结设计正好相反。命名混乱直接导致 Agent 误判。

**"Format 3" 出现的 9 处（已确认，全是文字，无持久化值）**：
`runtime/scripts/state_ledger.py:1`、`runtime/scripts/vibe.py:240`（CLI help）、`runtime/scripts/state_migrate.py:835`（注释）、`docs/RELEASE-NOTES.md:3`（0.6.0 标题）、`docs/USAGE.md:700`（小节标题）、`tests/test_state_replay.py:3,53`、`tests/test_state_ledger.py:1`、`tests/test_archive_skill.py:178`、`README.md:11`（"format 2/3"）。

### 问题 B：布局

**期望（已确认，来自冻结设计）**：唯一布局 = 工作目录与 `.project-log` 均为普通目录，非 Git 仓库，远端走 KB。

**实际（已确认，来自代码）**：代码同时支持两种，判据是"工作目录本身是不是 Git worktree 根"：

- `runtime/scripts/state_context.py:81-129` `git_context()`：向上找 `.git`。找到 → 身份 `{root, git_dir}`、SQLite 存进 Git 管理目录；找不到 → 身份 `{root, branch:"local"}`、SQLite 存 `.project-log/.state`。
- `runtime/scripts/state_ledger.py:490-518` `portability_status()`：在仓库内 → 检查 `ledger_tracked/uncommitted/unpushed`；不在仓库 → 只报账本新鲜度（`:514-517`）。
- `runtime/scripts/init_project.py:74-90` → `state_context.initialize()`：**无守卫**，在仓库根 `vibe init` 会静默创建"Git 模式"。
- `runtime/scripts/state_exchange.py:70-75`：快照交换硬依赖 Git worktree 根。
- `docs/USAGE.md:708,734`、`docs/RELEASE-NOTES.md` 0.6.0：直接写"Git 跟踪的账本"，**未限定布局**。
- `skills/a-project-init/SKILL.md:27-30`：只让 Agent"判断是否在 Git 里、问个人/团队仓库"，**没有布局契约**。
- 全局规则 `runtime/opencode/AGENTS.md`、`prompts/vibe-global-agent.md`：**完全没有工作目录布局条款**。

**自相矛盾点（已确认）**：`state_context.py:90-96` 的 docstring 明确把"普通工作目录"写成受支持布局：

> A plain work directory is the supported layout for a Project Log that owns several nested repositories: the log sits beside them and reaches Git through the knowledge-base archive.

即：冻结设计只要普通目录，但代码把两种都当"官方支持"，文档又只重点讲 Git 那种。

---

## 四、复现与确切证据

**问题 A**：

```bash
python ~/.config/opencode/vibe-workflow/scripts/vibe.py version
# → default_format: 2, store_schema: 3, supported_formats: [1,2]   （无 format 3）
grep -rn "format 3\|Format 3" ~/Project/vibe-coding/vibe-coding \
  --include=*.py --include=*.md | grep -v __pycache__   # → 9 处
cat ~/Project/vibe-coding/.project-log/state-format.json
# → {"format": 2, "project_id": "c15166f6f14948aa85604021638f0b1a"}
```

**问题 B**（在实际工作目录）：

```bash
cd ~/Project/vibe-coding
git rev-parse --show-toplevel
# → fatal: 不是 git 仓库（或任何父目录）：.git      （外层确实非仓库）
python ~/.config/opencode/vibe-workflow/scripts/vibe.py --root . portability-status
# → {"ledger_events":482,"store_revision":482,"unexported_commands":0,
#    "history_rewritten":false,"in_sync":true,"git":null,"portable":true}
#   非 Git 工作目录下 git=null，portable 只看账本新鲜度
```

**持久化契约（已确认，改动代价高）**：`state-format.json` 的 `format=2`、SQLite `store_schema=3`（CHECK 约束）、各 `schema_version=1`。改这些需要迁移，且会打断账本哈希链。

---

## 五、环境、依赖、接口与约束

- **已确认（环境）**：Linux；Python 3.11（路径记于 `~/.config/opencode/vibe-python`）；运行时 `~/.config/opencode/vibe-workflow`；仓库根 `~/Project/vibe-coding/vibe-coding`（Git，HEAD `7c4ee56`）；安装态与源码逐文件一致（diff 仅 `__pycache__`）。
- **已确认（接口）**：`vibe` 子命令 `init/status/validate/task/record/evidence/review/gate/route/context/render/migrate/exchange/ledger/portability-status/goal/version`。
- **已确认（约束）**：不引入第二个结构化事实源；账本哈希链使持久化值不可随意改；已有真实项目日志（另一项目，format 1，日志目前在 Git 仓库内）待迁移。
- **假设**：我要求唯一布局 = 普通非仓库工作目录；可移植性只靠知识库归档（`a-project-log-archive` / `a-project-log-align` 两个 Skill）。
- **已确认（框架自身设计原则）**：单人使用、日志单向增长、无多人并发写同一工程。

---

## 六、已尝试与观察结果

- **已确认**：对比安装态与源码，确认框架不是"没更新"，而是**设计文档与代码注册表不一致** + 布局支持面比设计宽。
- **已确认**：`format 3` 无持久化表示（`state-format.json` 仍是 2），因此"改名"在技术上安全（不动数据）；但"把 format 3 正式注册"则要动持久化值 + 迁移。
- **已确认**：快照交换（`state-exchange*`）硬依赖 Git；冻结设计第七节已认定它在 work 布局下不可用。
- **未做**：尚未改任何代码或文档（只读调研）。
- **初步方案（待评估）**：
  - 问题 A（两种候选）：
    - **A1 收敛命名**：`format N` 只留给 Project Log；把"Format 3"从文档/注释/CLI 全部删除，改称"Git 账本（ledger schema v1）"；持久化值不动。
    - **A2 正式注册**：把这一代正式定为 `format 3`——`state-format.json` 写 3、`SUPPORTED_FORMATS` 加 3、并迁移存量 format 2 项目；同时把 `store_schema` 与 `format` 两个数字的语义在术语表里讲清。
  - 问题 B（三层，逐步加强）：(1) 全局规则 + `a-project-init` skill 写死唯一布局；(2) `vibe init`/`vibe validate` 对"仓库根"fail closed；(3) `git_context()` 只保留普通目录分支，`state-exchange` 从 CLI 表面移除或明确报错。

---

## 七、未知与请求帮助

**未知（确实不知道）**：
- 除已知两个项目外，是否还有别的项目把 format 2 日志放在 Git worktree 根（若有，改布局语义会让它们失配，需先 `state-attach` 重建）。
- 快照交换是否还有保留价值——在"只靠 KB 归档搬运"的世界里它可能是死代码。

**需要帮助（请给判断）**：
1. **根因**：我判断"设计文档把整代叫 Format 3、代码只注册 format 1/2，是命名撞车根因"——这个判断对吗？还有没有我没想到的层面？
2. **命名**：选 A1（收敛命名、format 只给 Project Log）还是 A2（正式注册 format 3）？还是第三种（彻底弃用 `format` 一词，改用 `log generation` / `log version` + `schema` 系列）？请给推荐与理由。
3. **强度**：问题 B 选哪种——(A) 只改文档/规则；(B) 文档 + `init`/`validate` 守卫；(C) 连 `state_exchange` 一起删？请给理由与风险排序。
4. **迁移**：若改成唯一布局，对"日志在仓库根"的存量项目，应强制迁移，还是允许并存但只读？
5. **风险盲点**：我的方案里有没有你看到的、我没想到的破坏面（尤其哈希链、证据绑定、跨机归档、框架自身回归）？

**期望的回答形式**：对第 1–5 问逐条给结论；命名方案给出最终命名表（每条版本轴的推荐叫法）；布局方案给出推荐强度、实施步骤与失败模式。
