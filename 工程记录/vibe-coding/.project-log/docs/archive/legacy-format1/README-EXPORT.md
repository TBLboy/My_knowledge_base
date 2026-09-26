# Format 1 存档导出留档

## 这是什么

这是本项目 **format 1 时代**的 `.project-log/` 完整存档，从 `.project-log/legacy/`
**原样复制**而来，作为一个独立于 `legacy/` 目录的副本长期保留。

- **导出时间**：2026-09-24
- **来源**：`.project-log/legacy/`（65 个文件，约 1.7 MB）
- **原始格式**：format 1（文件式日志：`workflow.yaml`、`task-list.yaml`、
  `business-logic/atoms.yaml`、`loop/active-run.yaml` 等）

## 为什么导出

框架即将**退役 format 1 兼容层**（决策：`format` 轴只保留 format 2）。
退役后：

- `vibe` CLI、`loopctl` 与 `validate_project.py` **不再解析** format 1 结构；
- 这些文件**不会被自动删除**，但**工具不再读取**它们。

因此这里保留一份可人工查阅的副本，并把它排除在"退役清理"范围之外。

## 内容

| 目录/文件 | 说明 |
|---|---|
| `workflow.yaml` | format 1 的工作流状态（phase、active_goal 等） |
| `business-logic/` | 业务原子、开放问题、澄清记录 |
| `requirements/`、`requirements.md` | 需求基线与契约 |
| `decisions/` | 决策日志 |
| `research/`、`architecture/` | 技术研究与架构 |
| `tasks/` | 任务列表与状态 |
| `goals/` | Project Goal |
| `loop/` | Loop Core 的 active-run 与 evidence-index |
| `verification/` | 验证证据索引 |
| `alignment/`、`retrospective/`、`distillation/` | 对齐、复盘、蒸馏 |
| `specs/`、`schemas/`、`templates/` | 规格、schema、模板 |
| `new-writes/` | 迁移期间的临时产物（`bundle.json` + `state/`） |
| `current-session.md`、`progress.md` | 会话与进展快照 |

## 注意

- 这些是 **format 1** 的文件，**不要**把它们的结构当作当前 format 2 的参考。
- format 2 的精确事实源是 `.project-log/.state/`（本地 SQLite 投影）与
  `.project-log/ledger/v1/ledger.jsonl`（Git 账本）。
- 本目录是**只读留档**：保留原样即可，不需要迁移或改写。
