# TASK-043 跨平台与 Git 上下文验收报告

## 1. 范围与版本绑定

- 验收对象：代码仓库 `vibe-coding/` 的当前工作树（本次提交）。
- 主机与运行时：Ubuntu/Linux，`git` 2.x，项目解释器 `/home/tbl/miniforge3/envs/vibe-coding/bin/python`（Python 3.11.15），
  经机器无关入口 `~/.config/opencode/bin/vibe-python` 调用。
- 覆盖范围：Linux/WSL 命令语义、分支与 linked worktree 上下文、Git 快照交换（中断 / 分歧 / 强杀）。
- **范围外（用户已决定延期）**：Windows PowerShell 5.1/7 实机矩阵。本报告**不**声称 Windows 语义一致已完成；
  `done_when` 中 Windows 与 Linux 合并表述的那一条，其 Windows 半边保持未验证。

## 2. 方法

- 测试驱动：`tests/test_exchange_scenarios.py`（12 用例）与 `tests/test_cross_platform_surface.py`（6 用例）。
- 反证：回退受守护的实现后，对应测试必须失败。原始输出见 `task-043-falsification.txt`。
- 独立复核：由独立 `verification-reviewer` 子代理在只读约束下复跑测试、复算哈希并逐条判定 `done_when`。
- 所有临时仓库与项目都建在 `tempfile.TemporaryDirectory()` 下；源码树在任何用例后 `git status --porcelain` 不变。

## 3. 结果

| 套件 | 用例 | 结果 |
|---|---|---|
| `test_exchange_scenarios.py` | 12 | OK |
| `test_cross_platform_surface.py` | 6（含 3 个 linked worktree） | OK |
| 仓库全量 `unittest discover` | 288 | OK（skipped=1，为源码发布工作区专有的 legacy 升级用例） |
| `validate_package.py --root .` | — | Package validation passed |

对抗拒绝均被真实驱动（错误码由实现给出，非断言了别的东西）：

- `snapshot_missing`：没有已发布指针就 import。
- `foreign_snapshot`：快照 `project_id` 与本项目不符。
- `snapshot_diverged`：记录的 `base_snapshot` 不在快照祖先链上。
- `unexported_changes`：本地命令未发布就 import。
- `ledger_diverged`：把一个 worktree 的账本 graft 到另一个。

中断与恢复：

- 中断的 export 窗口在 `exchange status` 中报出 `pending_kind="export"` 与 `pending_snapshot`，`abandon --reason` 可恢复。
- 「指针已写、bookkeeping 提交丢失」的半中断由 `exchange finish` 确认恢复。
- export 窗口内被 SIGKILL 后，store 与 `validate()` 保持一致，pending 可恢复。

## 4. 缺陷 D：快照对象发布不是原子的（本轮发现并修复）

**现象**：修复前 `_write_exclusive` 直接把字节写进最终对象名（`objects/<sha>.payload.json`）。
若 SIGKILL（或任何 `OSError`）落在写入与 fsync 之间，最终路径上会残留一个**截断的对象**：
指针从未写入，所以 `status`/`validate` 仍然自洽，但该孤儿无法解析，且后续对同一修订的 export
会以 `snapshot_conflict` 失败而不是忽略或修复它 —— 强杀后不可恢复。

**修复**：改为「写入同目录临时文件 → `fsync` → `os.link` 原子落位 → `finally` 清理临时文件」。
`os.link` 的原子性与排他性保证读者只会观察到「没有该对象」或「完整对象」，并保留原来的
exclusive-create 语义（同名不同内容仍然 `snapshot_conflict`）。

**附带处置**：SIGKILL 不会执行 `finally`，因此临时文件可能残留。对象写入与指针写入现在共用
同一临时文件命名（`*.tmp-*`），exchange 目录的一条 `.gitignore` 规则覆盖两者，避免孤儿被
用户项目的 `git add -A` 纳入索引；
`test_killed_publish_temporaries_stay_out_of_git_status` 验证的是该**效果**（孤儿不出现在
`git status`），而不只是规则存在。

**反证**：将 `_write_exclusive` 回退为直接写最终路径后，
`test_write_exclusive_never_exposes_a_partial_object` 必然失败（原始输出见 `task-043-falsification.txt`）。

## 5. worktree 行为（本轮验收发现，已文档化）

已写入 `skills/a-project-log-align/SKILL.md` 的「Git Worktrees Are Separate Work Folders」一节：

- **共享**：同一仓库的所有 worktree 共享 `project_id` 与 Git 跟踪的 `.project-log` 内容（含账本）。
- **不共享**：本地 SQLite 位于各自 git dir（`git rev-parse --absolute-git-dir` 逐 worktree），
  因此 `context_id` 不同；新 worktree 的 `vibe status` 报 `missing_store`，需 `vibe state-attach` 重建。
- **写入隔离**：每个 worktree 持有自己的账本工作副本，跨可见需要显式 attach/reconcile；
  互相 graft 账本会 fail-closed（`ledger_diverged`）。
- **交换锁不跨 worktree**：Git index lock 逐 worktree，各 worktree 各自发布指针，发布互不串行化。

这改变了「一个工作目录一个 `.project-log`，切换分支不会隐藏或分叉日志」在 worktree 场景下的外推：
worktree 是**独立工作目录**，不是分支切换。

## 6. 未验证项（不得据此宣称已验证）

- **Windows / PowerShell 5.1 / 7 实机矩阵**（用户决定延期），含 Windows 上 `os.link` 的可用性（需 NTFS 同卷）。
- **目录 fsync 缺失**：`_write_exclusive` 只 fsync 文件内容，不 fsync `objects/` 目录，因此**掉电**时
  新对象名本身不保证持久（内容永不部分）。对 SIGKILL 无影响。属已知边界。
- **真实 SIGKILL 落在写临界区内**的现场未单独采集；写中途的保证由 `os.link` 语义与
  `test_write_exclusive_never_exposes_a_partial_object` 的失败注入共同覆盖。
- worktree 的「成功 reconcile / merge」路径未验证；实现看起来有意 fail-closed。
- 网络/远端 Git 与真实跨机合并未覆盖（本轮往返均为本地文件系统克隆）。
