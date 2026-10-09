# Vibe Workflow 框架缺陷登记 v1

- **记录日期**：2026-10-08
- **记录现场**：`D:\Project\Transformer-Koopman`（首次记录现场，缺陷本身为跨项目性质）
- **用户指令**：记录"目前我们这个框架的缺陷：创建的任务和 goal 不能取消，即便用户主动要求删除取消也很麻烦"
- **机器记录**：`DEC-046`（decision，status=active，rev 660）；本文件是它的可读版本
- **触发场景**：用户要求把 9 个任务"全部取消"，并"诚实收口" GOAL-001
- **复现环境**：Vibe python `D:\conda\envs\vibe-coding\python.exe`；CLI `C:\Users\12187\.config\opencode\vibe-workflow\scripts\vibe.py`
- **范围声明**：本文只**登记**缺陷，**未修改**框架任何脚本、模板、Agent 或 Skill；未伪造、转写或删除任何证据与复核记录。
- **注意**：本文件**故意不登记 `doc_ref`**。一旦登记，文件后续任何编辑都会使该记录"漂移"并阻塞全局完成门禁（即下文缺陷 5 描述的两难）。

---

## 0. 结论摘要

| # | 缺陷 | 严重度 | 后果 |
|---|---|---|---|
| 1 | 目标没有取消/终止状态 | 高 | 目标无法被用户主动取消，只能 active 或 complete |
| 2 | 完成门禁不可绕过，`risk_level` 被冻结 | 高 | 路线变更后无法通过"重写契约"合法关闭目标 |
| 3 | 门禁的 review 判据与 `review record` 命令不一致 | 高（本轮实际阻塞点） | 高风险管理目标在不制造证据的前提下**永远无法 complete** |
| 4 | 任务取消后不可删除/归档，列表只增不减 | 中 | 用户看到的"乱"无法清理 |
| 5 | 完成门禁是全局的，无关文档漂移会阻塞目标 | 中 | 任一份被引用长文档被编辑 → 目标无法完成 |
| 6 | 长文本与 `doc_ref` 两难 | 中 | 要么内容不成体系，要么给未来埋阻塞 |
| 7 | 终态不可逆的组合效应 | 中 | 一次误操作无法用命令回退 |

---

## 1. 目标无法取消或终止

**现象**：`goals.status` 只有 `active` / `complete` 两个取值，没有任何终止态，也没有 `goal cancel` 命令。

**证据**（`state_store.py`）：

- L1361 `INSERT INTO goals VALUES (?, ?, 'active', ?, ?, ?)` —— 创建时写死 `'active'`。
- L1394-1396 `UPDATE goals SET status = 'complete', ...` —— 唯一的状态跃迁目标是 `'complete'`。
- L1385-1398 动作分派只有 `goal.create` / `goal.update` / `goal.complete` 三个 goal 动作（`goal.update` 见 L1365）。
- `state_replay.py` L90 写入 `"status": "active"`，L104-106 写入 `"status": "complete"` —— 回放层同样只有这两个状态。

**影响**：用户主动要求"取消这个目标"时，框架层面没有对应动作。我在本轮只能把 9 个任务 `cancel`，目标本身只能通过重写条件（见缺陷 2）来"事实上作废"，其 `status` 仍是 `active`。

**建议**：为 `goals.status` 增加 `unmet` / `abandoned` 终态，并提供 `goal cancel --id --reason`；被取消的目标不应再参与 `_active_goal` 与完成门禁检查。

---

## 2. 完成门禁不可绕过，`risk_level` 被显式冻结

**现象**：`goal.update` 只能修改 `success_conditions` 与 `required_evidence` 两个字段，`risk_level` 改不掉，因此不能通过"把契约改简单"来合法关闭目标。

**证据**（`state_store.py` L1365-1384）：

```python
if action == "goal.update":
    ...
    for key in ("success_conditions", "required_evidence"):
        if key in payload:
            # Only the fields that legitimately accrue evidence over the
            # goal's life may change; risk_level stays frozen so this
            # action cannot drop the independent-review requirement.
            extensions[key] = payload[key]
```

**门禁要求**（`_goal_completion_problems`，L1104 起）：

- L1129-1155：每个 `success_condition` 必须是 `passed`（须绑定**至少一条 valid 证据**）或 `not-applicable`（须写明 `reason`）；`passed` 但无证据引用 → 阻塞。
- L1157-1186：`required_evidence` 每项若只给标签，须能按其 `kind` / `subject` 匹配到 valid 证据，否则报 `required evidence missing`。
- L1187-1194：`risk_level` 为 `high` / `critical` 时，必须存在 `kind == "review"` 且有效状态为 `valid` 的**证据行**，否则报 `high-risk goal lacks a valid independent review`。

**实测**：`goal complete --id GOAL-001` 第一次返回

```
Goal completion rejected: SC-1..SC-8: success condition is 'pending';
required evidence missing: <6 项>; high-risk goal lacks a valid independent review
```

**影响**：当技术路线变更导致旧契约失效（本项目：DEC-020/024/025/026 取代了原路线）时，唯一合法的收口路径被冻结字段堵住。

**建议**：允许在有正当理由（附证据与用户裁定记录）时重写或废弃整个契约；或增设 `goal abandon`。

---

## 3. 门禁的 review 判据与 `review record` 命令不一致（本轮实际阻塞点）

**现象**（本轮唯一剩余的拒绝原因）：

```
{"error": {"code": "goal_gate",
 "message": "Goal completion rejected: high-risk goal lacks a valid independent review"}}
```

**根因**：

- 目标门禁查的是 **`evidence` 表中 `kind = "review"` 且有效状态为 `valid`** 的行（L1189-1194）。
- 而独立复核是通过 `review record` 写入 **`reviews` 表**（动作分派 L1521 `review.record`；每任务的门禁在 L1339-1355 读的是 `reviews` 表的 `reviewer` / `verdict` / `evidence_refs`）。两张表、两套判据。
- 当前库内：`reviews` 表有真实复核记录（含 `REV-PHASE2-ABLATION-001` verdict=conditional、`REV-THEORY-002` verdict=go），但 `evidence` 表中 `kind="review"` 的只有 **1 条**（`EV-CLARIFY-REVIEW-001`），且其状态为 **stale**。

**影响**：high-risk 目标即使做完了全部真实独立复核，只要没人手工再补一条 `kind="review"` 的证据行，就**永远无法 complete**。这使"独立复核"这一安全机制在目标层面事实上失效（正确的做法无效，绕过的做法有效）。

**建议**：把目标门禁的 review 判据改为读取 `reviews` 表（与任务门禁一致），或明确提供 review 类 evidence 的创建路径并在文档中说明二者关系。

---

## 4. 任务取消后不可删除或归档，列表只增不减

**现象**：`task cancel` 工作正常（本轮 9/9 成功），但没有任何动作能把任务从列表里去掉。

**证据**：

- `state_store.py` L531：`status TEXT NOT NULL CHECK(status IN ('active','waiting-user','blocked','handed-off','finished','cancelled'))` —— 没有 `deleted`。
- 动作分派（L1359-1620）中任务侧只有 `task.create` / `task.update` / `task.begin` / `task.wait` / `task.handoff` / `task.finish` / `task.cancel`（校验表 L1564 允许从除 `finished`/`cancelled` 外的状态取消）。
- 无 `task.delete` / `task.archive`；`status` 输出仍列出全部 `cancelled` 任务。

**影响**：用户感知的"太乱了"无法通过清理消除；任务列表单调增长，最终只靠人的记忆区分"有效历史"和"噪声"。

**建议**：提供 `task archive`（软删除，保留账本）或让 `status` 视图默认过滤 `cancelled` / `finished`，并把"全部历史"放到显式开关后面。

---

## 5. 完成门禁是全局的，无关文档漂移会阻塞目标

**现象**：`_goal_completion_problems` 的第一行就是 `Store._document_drift_problems(connection, root)`；该检查遍历**全部** record 的 `doc_ref`，任一哈希不匹配即 `fail-closed`。

**证据**：`_iter_doc_refs`（L177-186）按结构识别 `doc_ref`——**任何同时含 `path` 与 `sha256` 两个键的字典**都被当作文档引用；`_doc_ref_issues`（L242-278）在文件读不到或哈希变化时报 `doc_ref changed`。

**影响**：一份与当前目标毫无关系的长文档被编辑过，就可能让目标无法完成。这会把"记录纪律"变成"谁都不敢改文档"。

**建议**：把漂移检查限定到与目标/任务相关的记录（例如只检查被该 goal 的 `required_evidence` 或相关任务证据引用的 `doc_ref`）。

---

## 6. 长文本与 `doc_ref` 的两难

**现象**：record payload 的单个字符串上限为 `MAX_DOCUMENT_BODY_CHARS = 4096` 字节（L23；校验在 `_reject_long_form_text`，L151-174），超限报 `document_body_not_allowed` 并提示"store a doc_ref instead"。而 `doc_ref` 一旦登记就带来缺陷 5 的永久漂移风险。

**影响**：高信息量的记录只能被切成多个短字段（因此本文这类长内容被迫游离在账本之外，或必须以"无引用附件"形式存在，不成体系）。

**建议**：为附件提供不参与哈希门禁的引用类型（例如 `attachment` / `see_also`，仅记录路径与说明），或把漂移检查改为"提示 + 显式刷新"而非门禁阻塞。

---

## 7. 终态不可逆的组合效应

**现象**：多个状态约束叠加后，误操作无法用命令回退。

**证据（本轮实测）**：

- `task.resume` 对 `implemented-unverified` 返回 `state_conflict`（即该终态无法再变更状态）。
- 对 `handed-off` 的任务直接 `task.handoff` 返回 `state_conflict`，必须先 `resume` 再 `handoff`。
- `task.cancel` 是终态（L1564 的允许集合不含 `cancelled` / `finished`）。
- 没有 `--dry-run`，也没有通用回退动作。

**影响**：一次误取消 / 误 finish 后，只能新建任务并重写全部上下文，成本高且容易丢信息。

**建议**：提供 `task.reopen`（带理由与审计），或为破坏性动作提供 `--dry-run` / 二次确认。

---

## 附 A：本轮实测命令与原始输出

```text
# 1) 契约改写（成功后 rev 658）
goal update --id GOAL-001 --success-conditions @goal_sc_closed.json --required-evidence "[]"
  -> {"goal_id": "GOAL-001", "updated": true}

# 2) 完成门禁（被拒）
goal complete --id GOAL-001
  -> {"error": {"code": "goal_gate",
       "message": "Goal completion rejected: high-risk goal lacks a valid independent review"}}

# 3) 缺陷登记（rev 659 / 660）
record create --kind decision --id DEC-045 ...   -> active
record create --kind decision --id DEC-046 ...   -> active

# 4) 终态
status -> revision=660, 9 个任务全部 cancelled
```

第一次调用（契约改写前）的拒绝信息更完整，包含 `SC-1..SC-8: success condition is 'pending'` 与 6 项 `required evidence missing`；改写后仅剩第 3 条缺陷。

---

## 附 B：本轮"诚实收口"实际做法（供审计）

1. 保留 8 项成功条件的**原文**，逐条把 `status` 改为 `not-applicable` 并附收口理由，`required_evidence` 清空 → 契约不再声称任何待完成要求。改写历史留在 append-only 账本中，可对照。
2. `GOAL-001` 的 `status` **仍为 `active`**：因为缺陷 2/3，不伪造证据就无法 `complete`。
3. 未做的事：未创建任何"补充证据"、未把既有复核转写为 review 类证据、未修改框架代码。用户在选项 2（授权转写证据以关闭工具状态）与选项 1（仅诚实改写契约）之间选择了后者。

---

## 附 C：建议的修复优先级

1. **缺陷 3**（门禁判据错配）—— 它使一个安全机制事实上失效，且修复成本最低（改判据或补文档）。
2. **缺陷 1 / 2**（无终止态 + 冻结字段）—— 决定"用户能否体面地终止一个目标"。
3. **缺陷 4**（无法归档）—— 直接决定日常可用性与用户的"乱"的感受。
4. **缺陷 5 / 6**（漂移与长文本）—— 影响长期可持续性。
5. **缺陷 7**（不可逆）—— 影响容错。

（在缺陷 1/2/3 修复前，本项目不再建立 evidence-gated 的 goal。）
