# -*- coding: utf-8 -*-
"""Append D-023 / D-024 observations from the 2026-10-13 TASK-054 session."""
import pathlib

p = pathlib.Path(r"D:/Project/Transformer-Koopman/.project-log/docs/framework-defects.md")
text = p.read_text(encoding="utf-8")

addendum = """

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
"""

p.write_text(text + addendum, encoding="utf-8")
print("appended", len(addendum))
