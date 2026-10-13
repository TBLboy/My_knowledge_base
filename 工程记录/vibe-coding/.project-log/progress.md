# Progress

## 当前状态（2026-10-13 覆盖更新）

- **当前 Goal**：GOAL-008「框架修复吸收：goal.update 支持 implementer/owner + 消除 goal reducer 双实现」保持 **complete**；10-12/10-13 的框架修复属其后续续作，未新开 Goal。
- **当前 Task**：TASK-145「已安装插件/MCP 默认放行：主 Agent 权限策略 + 框架随包工具带 + 安装器受管 MCP」——实现与定向验证完成，全量逐文件验证进行中，待部署与独立复核。TASK-140（控制层刷新到 d21a3e0 并验证生效）**handed-off**，门禁阻塞。
- **正在做什么**：TASK-145 收尾（部署到已装控制层 → 实机验证 → 记录 → 独立复核 → 提交推送）。
- **阻塞**：TASK-140 需要 `go` 级独立复核，而复核者读不到安装层 `opencode.json`（含明文 apiKey）；其两条 `done_when`（配置内容、运行中服务行为）在「复核者不得读密钥」前提下无法独立验证。
- **需要用户决定**：① TASK-140 如何收口（推荐给受信入口加脱敏检视动作 / 或改口径 / 或先挂着）；② 三个 V1 时代插件（`opencode-background-agents`、`opencode-notify`、`@tarquinen/opencode-smart-title`）在 V2 下加载失败（ALIGN-FW-009），是否从用户 `opencode.json` 删除；③ `~/.config/opencode/opencode.json` 的明文 apiKey 建议改为 `{env:LLMCENTER_API_KEY}`。
- **验证与复核**：TASK-144（goal 工具放行）受信验证 5 文件全绿 + `validate_package` 通过；TASK-145 全量逐文件聚合 **27/27 文件全绿**，`validate_package` 通过，已装控制层部署后 89/89 受管文件与包逐字节一致；实机 `GET /api/agent` 生效规则：vibe-main 的 catch-all 只剩 base policy 的 allow（deny 已去除）、verification-reviewer 仍为 allow+deny。独立复核进行中。10-12 两轮复核 REV-REFRESH-140 / 142 均 **conditional**（载荷逐字转录，写入层面独立性缺口见 DEC-076/077/078）。
- **交付**：`origin/main` = **3bab1fd**（已推送）；本地 `main` = **83be137**（TASK-145，8 文件）**未推送**（直连 reset、代理 10808 不通，待重试）。已装控制层已更新到 83be137（89/89 受管文件一致）。
- **下一步**：① 全量验证转绿 → 部署 TASK-145 并实机验证（`/api/agent/vibe-main` 生效规则 + 重新加载会话确认插件/MCP 工具出现）；② 独立复核后 finish TASK-145、提交并推送；③ 等用户裁决 TASK-140 收口与三个 V1 插件的处理。

## 2026-10-13 已安装插件/MCP 默认放行（ALIGN-FW-009，DEC-087，TASK-145，进行中）

- 起因：用户「其他插件你也放行，然后再优化一下 vibe-coding 源码框架，凡是我安装的插件默认都放行。同时，把握现在安装的 MCP 和插件，都加入到 vibecoding 源码框架里面……你检查一下」。
- 盘点（实测 `GET /api/plugin`、`GET /api/mcp`）：插件 5 个——`vibe-workflow`(local, active)、`opencode-agent-memory@0.3.0`(active)、goal-plugin@0.1.60(active)，以及 **3 个 failed**：`opencode-background-agents`、`opencode-notify`、`@tarquinen/opencode-smart-title`（错误 `Plugin must export a default definition with an id and an effect or setup function`；npm 最新版 0.1.1 / 0.3.1 / 0.1.7 仍无 V2 构建）→ 记为 **ALIGN-FW-009**，**不纳入框架**。MCP 8 个全部 connected：`context7`、`document-loader`、`gh_grep`、`github`、`playwright`、`sequential-thinking`、`web-search`、`wikipedia`。
- 框架改动（7 文件）：① `vibe-main` 去掉 catch-all `* * deny`——V2 把解析为 deny 的动作从会话隐藏，这正是已安装插件/MCP 工具消失的机制；改为 OpenCode 文档化 base policy + 显式内置动作放行 + subagent 范围限制 + `execute` deny + 密钥 `read` deny（限制在后，最后匹配者生效）；② seed `runtime/opencode/opencode.json` 随包提供 plugin（goal 0.1.60 + opencode-agent-memory）与 8 个 MCP；③ 安装器新增**受管 MCP 合并**，与权限规则同一套归属契约（用户已有 / 改过 / 删过都不覆盖、不复活）；④ 测试：受管 MCP 归属测试、主 Agent 工具可见性断言（按 base policy 顺序解析）、补 `skip_unless_symlink` 守卫（该用例漏加守卫，本机 `os.symlink` 无特权）；⑤ 文档：`docs/USAGE.md` 两处 + `runtime/opencode/README.md` 同步（原文写「安装器不强制安装任何可选 MCP」，与用户要求相反，已按 DEC-087 改写）。
- 边界：子 Agent 保留 deny 基线（只读边界不变），需要某个 MCP 时按角色显式放行；扩展点已写入文档。
- 已知验证障碍：`verification_runner.py` 在**失败输出含非 ASCII 时崩溃**（`subprocess.run(text=True)` 未指定 encoding，GBK 解码失败、`output_bytes: 0`）——即 ALIGN-FW-004，本轮先用直连方式取失败清单。
- 记录时间：2026-10-13。

## 2026-10-13 /goal 工具缺失：根因与修复（ALIGN-FW-008，DEC-086，TASK-144）

- 现象：会话里没有 `get_goal` / `create_goal` / `update_goal*` 等工具，但系统提示里仍有 goal 插件注入的策略文字；`/goal` 无法启动自动续跑。
- 根因（证据链）：插件加载成功（日志）且 `dist/server.js` 用 `context.tool.transform(draft => draft.add(tool))` 注册 14 个工具；V2 里**插件工具名即权限动作名**，而 `d21a3e0` 引入的 `* * deny` 基线之后只放行内置动作 → 插件动作没有任何 allow → 被隐藏。旁证：`opencode-agent-memory` 同症状（`memory_set` 报 No tool named memory_set is currently available）；命令不受权限过滤（`/api/command` 里 `goal`/`pause_goal`/`resume_goal` 都在）。
- 修复：`vibe-main` 显式放行 `*goal*`（源模板 + 已装副本）+ 回归断言；受信验证 5 文件全绿 + `validate_package` 通过；提交 **3bab1fd**（已推送）。实测 `/api/agent/vibe-main` 生效规则已含该条（权限热加载生效），工具出现在会话需重新加载会话。
- 后续：TASK-145 以「去 catch-all deny」取代该单点放行，一次性覆盖所有已安装插件/MCP（DEC-087）。
- 记录时间：2026-10-13。

## 2026-10-12 本机控制层修复：闪窗、模型 pin、复核者能力（TASK-140..143）

- 用户指令序列：撤销已装层模型 pin → 修模板闪窗 → 模板去 pin → 「适当拓宽复核者能力，测试没问题之后推送」。
- 闪窗（DEC-084）：`plugins/vibe-workflow/index.ts` 两处 `spawn` 补 `windowsHide: true`，源模板加「spawn 调用数 == windowsHide 数」回归断言；提交 **3c3ca6a**；用户目视确认不再闪窗。
- 模型 pin（DEC-083 已装层 / DEC-085 源模板）：删除 9 个 agent 的 `model:`，子 agent 继承会话模型；两条要求 pin 的断言反转；提交 **bf6f211**。
- 复核者能力（ALIGN-FW-005 / 007）：`verification-reviewer`、`alignment-reviewer` 改为逐子目录放行 `external_directory` / `read` / `glob`（`~/.config/opencode/{agents,commands,plugins,skills,vibe-workflow}/*`）；移除 shell 的 `grep *` / `rg *` 放行（`grep` 的权限资源是模式而非路径）；deny `git diff --no-index*`；删除无效的字面文件条目并加「`external_directory` 必须以 `/*` 结尾」守卫断言。提交 **f6cc856 / d823225 / c23ed2a**。
- 复核：REV-REFRESH-140 / 142 均 conditional；实测密钥经 read / glob / grep / shell 四条路径全部 DENIED；载荷逐字转录，写入层面独立性缺口见 DEC-076/077/078。
- 推送：`d21a3e0..c23ed2a main -> main`（直连成功）；`3bab1fd` 随后亦已推送。
- 未收口：TASK-140（控制层刷新到 d21a3e0 + 生效验证）因「复核者读不到含密钥的 `opencode.json`」门禁阻塞 → handed-off。
- 记录时间：2026-10-12 / 13。

## 2026-10-11 主线吸收框架修复：goal.update 归属 + 单一 goal reducer（GOAL-008，TASK-137..139）

- 用户裁决（DEC-074）：不再处理 format 1 项目；要求把「主线吸收框架修复」**收口**。
- main 线（`8a30f63`）：`goal.update` 支持 `--implementer/--owner`（空白/非字符串拒绝、`risk_level` 仍冻结）；`GOAL_UPDATE_EXTENSION_KEYS` + `merge_goal_update_extensions` 收敛为**单一实现**，实时迁移与账本重放调用同一函数（消除 DEC-071 的 reducer 双实现静默失效）；回归测试覆盖 gate 解锁、空白/None/risk_level 拒绝、replay 保留归属，golden replay 账本携带 goal 归属以差分锁定两 reducer。
- codex 分支（`19cac55`）：共享核心与两处测试文件逐字节镜像，全量套件 302 tests / OK (skipped=3)。
- 部署刷新：控制层先恢复到 install-state 记录的 pristine 哈希（逐一校验），再经官方 `opencode_installer.py update` 刷新（直接覆盖会造成永久本地/包冲突），`preserved_local=[]`；实机 `~/.codex` 经 `global_installer.py update` 刷新；两处各 3 文件与源分支逐字节一致（复核者直接哈希）。
- 行为验证（两处各自复现 GOAL-007 场景）：高风险 Goal + 已通过 SC + 范围内 go 复核但无 implementer → `missing_implementer` 拒绝；`goal update --implementer` 后 → complete；空白 → `invalid_input`；`--risk-level` 被拒。
- 复核：REV-FIX-137 首轮 conditional → 补基线/逐文件聚合/environment 归因后 **137-FINAL、138、139 全部 go**，载荷逐字转录（DEC-076/077/078）。
- 规则 8 登记：DEC-075（整包运行在本机不是可靠绿信号，建议加能力探测守卫）、DEC-079（`goal.complete` 会关闭尚未 finish 的任务，顺序须先 finish）。
- 未验证项：整包的两个主机相关用例（隔离通过、归因 environment）；两处安装器执行属实现者报告。
- 记录时间：2026-10-11。

## 2026-10-11 实机 ~/.codex 更新到 0.6.0（用户授权，DEC-072 / REV-CODEXPORT-019）

- 用户裁决：把实机 `C:\Users\12187\.codex` 从 0.5.0 更新到 0.6.0（已知悉 format 1 项目不再被新核心读写）。
- 执行：codex 分支（e75976e）的 `scripts/global_installer.py --skills-root ~/.codex/skills --mcp vibe-toolbelt update`，
  update/verify 均 exit=0；`package_version` 0.5.0→0.6.0、`managed_files` 85、`doctor.blocking_failures=[]`。
- 保留：用户自有 config（`model_provider=custom`/`model`/`model_catalog_json`/`[features] goals`/
  `[model_providers.custom]`）与 `access_profile=keep-existing` 均未被改写；受管块唯一无重复。
- 验证：三 hook 以真实 payload 实测 exit=0；`codex plugin list` 显示 `vibe-toolbelt@vibe-global-toolbox
  installed, enabled 0.4.1`；复核者实测实机 `vibe-workflow` 的 24 个 hooks+scripts 文件与仓库逐字节一致。
- format 1 影响面：机器上 10+ 个 format 1 项目（`workflow.yaml` 存在、无 `state-format.json`）在 0.6.0 下
  不再被 vibe 命令读写；hook 对它们只读（抽查 my_lunwen / dexbot_ros2_ws-dex_vla / dex_app 三处均未新建
  `.state/`）。迁移路径：旧文件移入 `.project-log/legacy/` 后重新 `vibe init`。
- 已知残留（DEC-073）：`missing_implementer` 修复只在 OpenCode 控制层，codex 侧部署仍是未打补丁 `state_store.py`；
  应由主线吸收（DEC-071 follow-up）。
- 记录时间：2026-10-11。

## 2026-10-11 GOAL-007 收口：框架缺陷修复（DEC-071）

- 用户裁决：GOAL-007 的 `missing_implementer` 阻塞按「修框架后关闭」处理。
- 修复打在**已安装控制层**（`~/.config/opencode/vibe-workflow/scripts/`，非仓库分支）：`state_store.py` 的
  `goal.update` 白名单与校验、`vibe.py` 的 `--implementer/--owner`、`state_replay.py` 的重放键元组；
  备份在 `~/.config/opencode/backups/goal-implementer-20261011-195547/`。
- 根因（比字段本身更广）：同一状态迁移被实现两遍——实时应用在 `state_store.py`、账本重放在 `state_replay.py`；
  只改前者时投影表已有 implementer，而门禁读重放态仍报缺失（实测：直连投影 DB 检查无问题，CLI 仍拒绝）。
- 验证：空 implementer 被拒（`invalid_input`）；写入后投影表可见；`goal complete --id GOAL-007` exit=0
  （revision 1127），Goal=complete、SC-001..SC-007 全 passed、任务全部终态。
- 未触碰 `main`/`opencode-main` 检出与已推送的 codex 分支（e75976e）；因此主线必须吸收该修复与回归测试，
  否则下次安装会覆盖。
- 记录时间：2026-10-11。

## 2026-10-11 codex 分支全量对齐 main（GOAL-007，TASK-128..136）

- 用户裁决（DEC-056，C 级）：codex 分支全量对齐 main 当前能力，同时保留并适配 codex 交付面；接受 main 的破坏性退役（format 1 / exchange / migrate / 纯工作目录布局）。
- 交付内容：核心 runtime/scripts 取 main 版并退役 loop_state/loopctl/state_exchange/state_migrate（TASK-129）；模板树与初始化/校验面对齐（TASK-130）；45 个 skills 与 main 同名集合一致（逐字节相同 7 / 客户端差异 38 / 双方独有 0，TASK-131）；交付面（hooks/installer/MCP/cc-switch/插件）在新核心上重写适配（TASK-133）；文档与版本标识对齐（USAGE/RELEASE-NOTES 取 main 版并重贴 codex 客户端章节，新增 TERMINOLOGY/V3-PR-00-BASELINE/CI，版本 0.5.0→0.6.0，TASK-134）；测试树适配到 codex 面并首次全绿（TASK-136，承接取消的 TASK-132）；隔离 codex home 端到端验证与推送（TASK-135）。
- 验证：全量套件 300 tests / OK (skipped=3)；`validate_package.py` 通过；隔离 codex home 的 install/verify/update/uninstall、三个 hook 实测、已安装 runtime 的 vibe init/status/validate/render、真实 codex CLI 的 `codex mcp list`/`codex plugin list` 共 14 步全 exit=0；marketplace 源指向仓库根、vibe-toolbelt 0.4.1 installed+enabled。
- 复核：REV-CODEXPORT-128/129-FINAL/130/131-FINAL2/133/134-FINAL2/135-FINAL/136 全部 `go`；TASK-134 与 TASK-135 各经 conditional→go 两/三轮，复核者指出的问题（USAGE 的 OpenCode 漂移、AI_UPGRADE 不实表述、实机 sha256 非法 63 位、推送未执行）均已修复并复验。
- 框架缺陷登记（规则 8，DEC-070）：`goal.update` 白名单缺 implementer/owner 致高风险 Goal 无法过完成门禁；invalidate 后无法同 id 重录证据；`uninstall` 残留 `__pycache__`；隔离 home 的 doctor `auth.credentials` 阻断（按设计，用 `--skip-doctor`）。
- 记录时间：2026-10-11（会话内多轮委派与复核）。
