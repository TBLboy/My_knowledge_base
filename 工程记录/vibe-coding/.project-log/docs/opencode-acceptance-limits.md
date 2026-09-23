# TASK-075 OpenCode 端到端验收：范围、结果与未验证项

## 1. 验收对象与版本绑定

- 客户端：`opencode-ai@1.18.31`（本机 `/home/tbl/.local/npm-global/bin/opencode`）
- 解释器：`/home/tbl/miniforge3/envs/vibe-coding/bin/python`（Python 3.11.15）
- 会话 Goal 控制器：`@prevalentware/opencode-goal-plugin@0.1.51`
- 被测代码提交：代码仓库 `vibe-coding/`，分支 `opencode`，提交 `613ba44`，工作区干净
- 模型：`opencode-go/glm-5.3-flash`
- 探针：`.project-log/docs/opencode-acceptance-probe.py`
- 原始输出：`.project-log/docs/opencode-acceptance-output.txt`
- 哈希绑定：`.project-log/docs/task-075-version-binding.json`

## 2. 方法

每次运行都在**临时 XDG 根**中通过 `opencode_installer.py install` 安装随包交付面，
然后用真实的 `opencode serve` 拉起服务，通过会话 API 驱动真实模型回合。
用户本机的 `~/.config/opencode`、`~/.codex` 不被读写。

这不是静态文件检查：每个 `CHECK` 行都来自一次真实会话的可观察结果
（会话消息计数、子会话列表、目标插件状态文件、项目账本行数、工作目录文件是否出现）。

## 3. 结果（单次完整运行，10 项检查全 PASS）

| 场景 | 检查 | 结果 | 观察 |
|---|---|---|---|
| S1 生命周期 | `s1.reads_authoritative_state` | PASS | Agent 报出的 `project_id` 与本地 `vibe status` 完全一致 |
| S1 生命周期 | `s1.write_grows_ledger` | PASS | 账本 `ledger.jsonl` 由 0 行增长到 1 行 |
| S2 会话 Goal | `s2.auto_continuation` | PASS | 单次 `/goal` 后自主续跑，assistant 回合=8，status=active |
| S2 会话 Goal | `s2.pause_stops_continuation` | PASS | `/pause_goal` 后会话静默且 status=paused |
| S2 会话 Goal | `s2.resume_restarts_continuation` | PASS | `/resume_goal` 后回合数继续增长，status=active |
| S3 压缩存活 | `s3.compaction_keeps_goal` | PASS | summarize 后目标 objective 保持不变，status=active（断言口径：**插件状态在 summarize 后未变**，不等价于“上下文确实被压缩且目标仍被正确恢复”） |
| S4 委派权限 | `s4.disallowed_role_blocked` | PASS | 委派未授权角色 `build`：子会话=0 且出现拒绝措辞 |
| S5 只读复核 | `s5.reviewer_cannot_edit` | PASS | `verification-reviewer` 会话未创建目标文件且声明拒绝 |
| S6 降级路径 | `s6.no_subagent_when_task_disabled` | PASS | `task` 工具无可用子 Agent 时子会话=0 |
| S6 降级路径 | `s6.serial_fallback_declared` | PASS | 主 Agent 串行完成工作并标出 `serial-role-fallback` |

四个 `done_when` 的对应关系：

1. **真实 OpenCode 会话可完成端到端流程** —— S1（真实读取 + 真实写入增长账本）。
2. **关键客户端能力可用** —— S2/S3/S4/S5/S6。
3. **证据绑定到提交与版本** —— 本节第 1 节 + `task-075-version-binding.json`（7 个文件哈希）。
4. **未验证项明确记录** —— 本节第 5 节。

## 4. 关键实现事实（复核时可直接验证）

- 安装器把 `permission.task` 白名单写进**每个 agent 的 frontmatter**；
  agent 级权限合并覆盖全局 `opencode.json`。仅改全局 `tools.task=false`
  **不足以**关闭委派——这是 S6 前两次运行失败、第三次通过的原因。
- `/pause_goal` 不会取消“已经在途”的续跑回合。正确断言是“先等会话静默，
  再确认计数稳定且 status=paused”，而把在途回合数记为观察值而非通过条件。
- `/session/<id>/command` 在目标活跃时可能长时间不返回（请求挂住）。
  探针因此对命令派发采用“容忍超时 + 轮询观察结果”，而不是把返回值当成功信号。

## 5. 未验证 / 范围外（不得据此宣称已验证）

- **TUI 交互路径未实测。** 验收走的是 `opencode serve` 的会话 API 与真实模型回合，
  与 TUI 共享同一命令/工具/权限实现，但“在 TUI 里手敲 `/goal`”这一步本身未执行。
- **`TASK-075` 的 `depends_on` 含 `TASK-074`（状态 `ready`，从未开始）。** 依据是账本
  中 TASK-074 只有 `task.create`、没有 `task.begin`；它不在 `vibe status` 的
  10 条任务投影窗口内（投影有界），不是“任务不存在”。本次验收没有等待 074 收敛，
  依赖不满足这一点是事实记录，不能视为已满足。
- **其余前置任务同样处于 `implemented-unverified`**（TASK-069/070/071/072/073/078/079）。
  本次验收为其中 070/071/072/073 的端到端行为提供了运行时证据，但本报告不据此
  宣布这些任务自身完成。
- **`max_auto_turns` 上限未验证。** 续跑观测只覆盖到 16 个 assistant 回合，未触顶。
- **多模型未交叉验证。** 全部结论基于 `opencode-go/glm-5.3-flash` 单一模型。
- **Windows 路径未验证**（用户已明确暂不需要）。
- **长会话性能与体积未验证**：未测量长时间 Goal 运行下的上下文增长与压缩代价。
- **归档 Skill 在 OpenCode 端的完整链路**未纳入本次验收（属于其他任务范围）。
- **压缩的语义级存活未证**：只证明了 `summarize` 后插件磁盘状态未变，未证明
  上下文真的被压缩且目标语义仍被正确恢复。
- **断言判据偏松（复核 B1–B4）**：S4/S5/S6 的通过条件可被“模型没有尝试”满足；
  复核已用强制工具调用独立确证机制真实生效（`task` 被权限拒绝、reviewer 写工具
  缺失且 `bash` 被拒），但这些断言本身待加固，已记录为后续任务。

## 6. 可复现命令

```bash
cd /home/tbl/Project/vibe-coding
"$(cat ~/.codex/vibe-python)" .project-log/docs/opencode-acceptance-probe.py \
  --phases s1,s2,s3,s4,s5,s6 --model opencode-go/glm-5.3-flash --seconds 150
```

单场景重跑（例如只验降级路径）：把 `--phases` 换成 `s6`。
