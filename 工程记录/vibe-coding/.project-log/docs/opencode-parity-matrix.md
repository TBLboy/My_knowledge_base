# OpenCode Vibe Coding 能力对齐矩阵

> 基线：codex 分支 `ad51501`；目标客户端：OpenCode `1.18.31`；研究日期：2026-09-22。
>
> 本文是 TASK-068 的研究产物。它描述“如何迁移”，不替代需求基线
> `REQ-OPENCODE-001` 和业务原子 `BL-OPENCODE-001..006`。

## 1. 结论

采用 **直接复用成熟原语 + 薄适配层** 的迁移策略：

- OpenCode 原生提供 primary/subagent、Skills、Commands、插件 hooks 和权限模型。
- format 2 状态库、format 3 Git 账本和 `vibe` CLI 保持原样，两个客户端读写同一份
  `.project-log`。
- Goal/自动续跑复用 `@prevalentware/opencode-goal-plugin`，把它当作会话运行时控制器；
  Project Goal 与完成门禁仍由 `vibe` 状态库负责。
- 新增一个 OpenCode 集成插件，负责会话上下文、压缩上下文和工具后的证据失效。
- 新增 OpenCode 安装器，管理 `~/.config/opencode` 下的 agents、commands、skills、plugins
  和运行时，同时保护用户配置与项目日志。

## 2. 能力映射

图例：`supported` 原生直接支持；`adapted` 需要适配；`deferred` 首版明确不做。
本文统一使用 `deferred`；它对应 TASK-068 早期验收文字中的 `omitted`，不代表能力缺失或
永久排除，只表示不进入首版 Linux/WSL 迁移范围。

| Codex 能力 | OpenCode 原语 | 迁移结论 | 说明 |
|---|---|---|---|
| 全局主 Agent 规则 | `~/.config/opencode/AGENTS.md` | adapted | 把 Codex 全局规则转换为 OpenCode 全局规则；移除 Codex 专有接口描述 |
| 专门主 Agent | `agents/vibe-main.md`，`mode: primary` | adapted | 新增 `vibe-main`；设置 `default_agent`；保留 Build/Plan 内置主 Agent |
| 8 个角色子 Agent | `agents/*.md`，`mode: subagent` | adapted | 角色模板转换为 OpenCode Markdown Agent；reviewer 使用只读权限 |
| 子 Agent 委派 | 原生 `task` 工具 + `permission.task` | adapted | 主 Agent 通过 task 调用子 Agent；限制可调用角色；记录角色与复核身份 |
| Skills | `~/.config/opencode/skills/<name>/SKILL.md` | supported | 现有 Skills 结构兼容；校验 name/description；`compatibility` 标记迁移为 opencode |
| 自然语言生命周期触发 | 全局规则 + Skills | supported | Codex 主要依赖自然语言和 Skills，OpenCode 同样可用 |
| Slash commands | `~/.config/opencode/commands/*.md` | adapted | 可作为薄入口保留；命令 frontmatter 指向 `vibe-main` |
| SessionStart 恢复 | plugin `event` + `experimental.chat.system.transform` | adapted | 首条消息/会话创建时注入有界状态；恢复不等于完成 |
| PreCompact 恢复 | `experimental.session.compacting` | supported | 注入 `.project-log` 摘要并刷新 handoff/views |
| PostToolUse 证据失效 | `tool.execute.after` | adapted | 从工具参数提取变更路径，调用 `vibe` 运行时使覆盖证据失效 |
| Goal/自动续跑 | `@prevalentware/opencode-goal-plugin` | adapted | 复用成熟插件；pin 版本；作为会话运行时控制器 |
| Project Goal 与完成门禁 | `vibe goal` + format 2/3 状态库 | supported | 不改变既有状态契约；插件状态不替代业务事实源 |
| 证据、复核、风险分流 | `vibe` CLI + reviewer subagent | supported | 高风险任务仍要求有效证据和独立复核 |
| 长文档归档 / KB 对齐 | 现有 Skills + Python 脚本 | supported | 与客户端无关，保持原实现 |
| MCP 可选 catalog | OpenCode `mcp` 配置 | adapted | 把 Codex MCP 声明转换为 OpenCode MCP 条目；默认不覆盖用户配置 |
| `codegraph` 可选 MCP | OpenCode `mcp` 配置 | adapted | 保留 codegraph 的 MCP 能力；命令/参数按 OpenCode schema 写入，不依赖 Codex marketplace |
| `vibe-toolbelt` 可选工具集 | OpenCode MCP 配置 | adapted | 只迁移其可用 MCP 能力；不迁移 Codex marketplace/plugin 机制 |
| Codex marketplace/plugin 机制 | 无直接等价物 | deferred | 首版不迁移 Codex 的 marketplace、plugin manifest 和插件安装流程；OpenCode 使用自身 plugin/MCP 配置 |
| `cc-switch` 通用配置生成 | 无直接等价物 | deferred | 首版不生成 Codex TOML 的 cc-switch 片段；OpenCode provider 配置另行处理，避免把 Codex 专用格式带过来 |
| Codex TOML Hooks | OpenCode TypeScript plugin hooks | adapted | 不再写 TOML hook 配置；由 OpenCode 插件承载 |
| 全局安装/升级/卸载 | 新的 OpenCode 安装器 | adapted | 管理 `~/.config/opencode`，逐文件状态、备份、冲突保护、幂等 |
| 工作目录 `.project-log` 外置 | 不变 | supported | 一个工作目录一个 Project Log，覆盖其下仓库和分支 |
| Linux/WSL | OpenCode CLI/plugin | supported | 首版验收平台 |
| Windows PowerShell | OpenCode CLI/plugin | deferred | 沿用既有延期决定，首版不纳入验收 |

## 3. 关键技术选择

### 3.1 主 Agent 与子 Agent

- 新增 `vibe-main`：`mode: primary`，作为 OpenCode 默认主 Agent。
- 保留 8 个角色：`business-analyst`、`codebase-onboarder`、
  `solution-researcher`、`implementation-builder`、`verification-reviewer`、
  `alignment-reviewer`、`paper-reader`、`workflow-distiller`。
- reviewer 角色使用 `permission.edit: deny`、`permission.bash: ask` 或等价只读边界。
- 主 Agent 保留用户沟通、C 级决策、任务状态、跨角色整合和最终完成判断。

### 3.2 Goal / Loop

候选：

1. **直接使用 `@prevalentware/opencode-goal-plugin`（推荐）**：MIT、`engines.opencode >=1.17.1`；
   registry 元数据与 README 声明其实现 `/goal`、持久状态、idle continuation、
   compaction context、Plan 安全和预算。当前研究阶段未在本机安装验证，真实运行行为
   由 TASK-072/TASK-075 验收。
2. 自研 Goal 插件：控制力最高，但重复实现成熟的会话生命周期、恢复和预算逻辑。
3. 放弃自动续跑：不符合“功能不变”。

选择候选 1。需要明确两个状态层次：

- **Session Goal**：插件的会话运行时状态，位于
  `~/.local/share/opencode-goal-plugin/goals.json`。
- **Project Goal**：format 2/3 中的业务完成契约，位于 `.project-log`，由 `vibe goal`
  读写和门禁裁决。

主 Agent 必须把 `/goal` 作为运行时入口，同时把业务完成事实写回 Project Goal；不能用插件
状态替代 `vibe goal complete` 的证据门禁。

**2026-09-22 修订（DEC-020）**：本节候选 1 的“等价”表述过强。OpenCode 无平台级原生 Goal，
必须区分两层：

| 层 | Codex | OpenCode | 可达性 |
|---|---|---|---|
| Project Goal（业务完成契约） | `.project-log` + `vibe goal` + `evaluate goal` | 同左，与客户端无关 | **完全等价** |
| Session Goal（线程续跑控制器） | 应用层原生 `/goal` | 需插件模拟 | **仅可观察行为近似** |

关键事实：Codex 侧 `loopctl goal-sync` 只是**观察**应用层状态，完成出口始终是 `vibe goal`
的证据门禁，因此业务正确性不依赖 Session Goal。差距来自平台层 vs 插件层：Codex 的续跑是
运行时保证，插件续跑依赖 `experimental.*` hooks，是尽力而为的模拟，且预算只能近似、
暂停/恢复无应用级可见面。

因此 **TASK-072 的验收口径修订为“可观察行为对齐 + 明确降级语义”**，并要求 **TASK-078 先完成**
（用真实运行证据决定复用现成插件还是自研）。硬约束：Session Goal 状态永不作为完成依据；
续跑失效必须显式告警，禁止静默停住。规则修订（“原生 Goal 是唯一线程控制器”在 OpenCode 侧的
归属）是 C 级事项，见 `ALIGN-OPENCODE-002`，待用户授权。

### 3.3 插件 hooks

新增 OpenCode 插件，至少承载：

- `event` / `experimental.chat.system.transform`：会话启动或首次消息时注入有界项目状态。
- `experimental.session.compacting`：压缩前注入状态并刷新 handoff/views。
- `tool.execute.after`：写入类工具完成后调用 `vibe` 运行时使覆盖证据失效。

实现原则：

- 插件不直接改写业务逻辑、不推进阶段门、不标记任务完成。
- 插件调用现有 `vibe` CLI，避免在 TypeScript 中复制状态机。
- 插件失败时 fail-closed 或明确降级，不静默跳过证据失效。

### 3.4 安装与运行时

- OpenCode 全局配置根：`~/.config/opencode`（可通过环境变量覆盖，便于测试）。
- 受管资产：`AGENTS.md` 标记块、`agents/`、`commands/`、`skills/`、`plugins/`、
  `vibe-workflow/` 运行时、`opencode.json` / `tui.json` 中的受管插件项。
- Python 运行时与 format 2/3 代码不复制业务状态机；继续使用同一个 `vibe` CLI。
- 安装器维护逐文件状态、备份、升级冲突保护和幂等；卸载不得删除项目 `.project-log`。
- 首版平台为 Linux/WSL。

实现落点（TASK-073）：

- 入口：`runtime/opencode/install.sh`（薄包装，解析 Python 3.11+）→
  `scripts/opencode_installer.py`，动作 `install | update | verify | preflight | uninstall`。
- 目标根：`${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}`，可用 `--opencode-home` 覆盖；
  测试用 `--skip-preflight` / `--skip-plugin-install` 隔离。
- `opencode.json` 只做合并，不整写：设置 `default_agent=vibe-main`、注册
  `./plugins/vibe-workflow.ts`、补入来源 permission 规则，同时保留用户的
  `plugin`/`mcp`/`model`/`permission` 及其它键；卸载只移除自身写入的受管项。
- `AGENTS.md` 以 `<!-- VIBE-OPENCODE-GLOBAL:BEGIN/END -->` 标记块合并，用户已有规则保留；
  卸载只摘除该块（块外内容为空时才删除文件）。标记缺失、重复或顺序错误时拒绝改动该文件，
  绝不按 `BEGIN` 位置截断，避免静默删除块外用户内容。
- 逐文件哈希状态写入 `<home>/.vibe-opencode-installation-state.json`；被替换文件备份到
  `<home>/backups/<action>-<stamp>/`。
- 冲突保护分两级：① 安装前若目标已存在且与包内不一致（或用户与包双方都改过），
  在写入任何文件之前报冲突并中止，不做静默覆盖、也不提供 `--force`；② 安装后用户改过的
  托管文件（含 `skills/**`、`vibe-workflow/**`）在 update 时打印
  `PRESERVED local modification` 并跳过覆盖；卸载只删除哈希仍与安装时一致的文件。
- `opencode.json` 的所有权单独记录：`default_agent`、受管 permission 规则记录安装前的
  原值，卸载时恢复原值而不是一律删除；若用户在安装后改过安装器添加的 permission 规则，
  该规则的所有权交还用户，update 不再重置、uninstall 也不再删除。
- permission 所有权遍历“包内规则 ∪ 上次受管规则”：包内删除某规则时，未被用户改动的受管
  规则会从配置中移除并清理所有权；用户删除受管规则时 update 不静默恢复，而是打印
  `managed rule removed by the user`。若 `opencode.json` 由安装器创建且卸载后已无其它键，
  则删除该文件而不是留下只含 `$schema` 的残壳。
- 插件依赖 `@opencode-ai/plugin@1.18.4` 由 npm/bun 安装，除非 `--skip-plugin-install`；
  `--no-audit`/`--no-fund` 只传给 npm。卸载会还原安装器改动过的 `package.json` 依赖项
  （`node_modules/` 交由包管理器处理）。
- install/update/uninstall 对自身触碰的文件是事务性的：任一步骤（含包管理器）失败时，
  按安装前的字节快照回滚 `opencode.json`、`AGENTS.md`、assets、runtime、`package.json`、
  `vibe-python` 与 state，并清理本次失败新建的 `node_modules/`、`package-lock.json` 与目录，
  不留半安装状态；uninstall 在删除任何文件前先校验上述 JSON、state 结构（`created_dirs` /
  `managed_files` / `permissions_added`）与 AGENTS 标记块结构，损坏时零删除退出。
- `created_dirs` 精确记录安装器创建的每一级目录；卸载自深向浅仅删除仍为空的这些目录，
  用户自己创建或填充的目录保留。
- 来自 state 的路径（`managed_files`、`created_dirs`）一律校验为停留在 OpenCode home 内的
  相对路径；绝对路径与 `..` 段被拒绝（`unsafe installation path in installation state`），
  损坏或恶意 state 不能删除 home 之外的文件。
- 所有安装器触碰的路径都经同一安全函数解析（受管资产、`AGENTS.md`、`opencode.json`、
  `package.json`、`vibe-python`、state、锁文件、备份目录与回滚目标）：home 内指向外部的
  符号链接会被拒绝（`refusing to touch a path outside the OpenCode home`），不做越界写入或删除；
  因此这些文件不支持用符号链接外置。
- 边界声明（不阻塞的已知限制）：`node_modules/` 由 npm/bun 自行创建的内部 symlink 与
  `.npmrc` 等包管理器自有配置文件不在安装器审计范围；安装器不创建或修改它们。检查与写入
  之间被并发替换父目录的 TOCTOU 亦不在本次单用户安装器范围内。
- 事务快照额外覆盖锁文件（`package-lock.json`、`bun.lock`、`bun.lockb`、`yarn.lock`、
  `pnpm-lock.yaml`）：已存在的锁文件在回滚时按字节还原；已存在的 `node_modules/` 不会被删除。
- `$schema` 与 permission 采用同一所有权规则：用户改过或删除后交还用户，update 不覆盖、
  uninstall 不恢复也不删除。
- 任何动作都不触碰 `.project-log/`，包括位于 OpenCode home 内部的 `.project-log/`。

## 4. 已知风险与验证要求

| 风险 | 影响 | 处理 |
|---|---|---|
| Goal 插件状态与 Project Goal 混淆 | 可能把会话状态误当业务完成 | 文档和主 Agent 规则明确两层状态；完成仍走 `vibe goal` 门禁 |
| OpenCode `experimental.*` hooks 变化 | 插件升级后失效 | pin OpenCode 与插件版本；端到端回归 |
| `tool.execute.after` 路径信息不足 | 证据可能未及时失效 | 实现路径提取适配器；失败时显式告警 |
| 权限模型与 Codex 不同 | reviewer 可能意外获得写权限 | 子 Agent 显式 `permission.edit: deny`，并在验收中验证 |
| 用户 `opencode.json` 已有 MCP/插件 | 安装可能覆盖用户配置 | 逐文件状态、受管标记、合并而非整写 |
| `debug config` 在本机 smoke 中超时 | 尚未证明完整插件生命周期 | TASK-071/TASK-075 做真实 TUI/CLI 验收 |

## 5. 证据

- OpenCode Agents: <https://opencode.ai/docs/agents/>
- OpenCode Skills: <https://opencode.ai/docs/skills/>
- OpenCode Commands: <https://opencode.ai/docs/commands/>
- OpenCode Plugins: <https://opencode.ai/docs/plugins/>
- OpenCode Permissions: <https://opencode.ai/docs/permissions/>
- OpenCode Rules / `AGENTS.md`: <https://opencode.ai/docs/rules/>
- OpenCode config schema: <https://opencode.ai/config.json>
- 本地版本：`opencode --version` = `1.18.31`
- 目标版本插件类型：从 npm registry 拉取 `@opencode-ai/plugin@1.18.31` 的
  `package/dist/index.d.ts`，确认 `event`、`experimental.chat.system.transform`、
  `experimental.session.compacting`、`tool.execute.after`、`permission.ask` 均存在。
- 本地 `~/.config/opencode/node_modules/@opencode-ai/plugin` 是 `1.18.4`，仅作为本机已安装
  OpenCode 生态的辅助观察，不作为 1.18.31 的类型证据。
- Goal 插件：`@prevalentware/opencode-goal-plugin` `0.1.51`，MIT，
  `engines.opencode >=1.17.1`。当前本机未安装；本矩阵只把它作为候选推荐，不声称已在本机可用。
- 旧 OpenCode 主 Agent 备份：
  `/home/tbl/.local/share/vibe-workflow-backups/opencode-v0.2-uninstall-20260922-150535/agents/vibe-goal.md`

## 6. 未完成验证

- 尚未在真实 OpenCode TUI 中验证 `vibe-main`、8 个子 Agent、Skills 和 commands 的完整加载。
- 尚未验证 Goal 插件的 idle continuation、compaction context 和 Task 子会话 defer 行为。
- 尚未验证自研插件对 `tool.execute.after` 路径提取和证据失效的端到端行为。

这些项目分别由 TASK-071、TASK-072 和 TASK-075 承担。
