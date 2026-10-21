# Vibe Workflow 框架缺陷：活动 Run 全局独占，阻塞并行任务

## 状态

- 发现日期：2026-10-18
- 项目：`RLinf-Franka`
- 影响范围：Project Log v2 任务生命周期 / 多 Agent 协作
- 严重性：高；会阻塞无关任务的正常启动
- 当前状态：待框架维护者修复

## 现象

项目中存在一个由其他 Agent 创建并正在执行的任务：

- Task：`T-021-smooth-reset-ab`
- Run：`R-021`
- 主题：隔离 Reset 可选平滑轨迹对照
- 范围：`杂项/reset_lab`

当前主 Agent 需要推进另一个完全独立的任务：

- Task：`T-021-v3-engineering-spec`
- 主题：未来采集与 LeRobot v3 转换
- 范围：raw 采集、跨传感器时间轴、v3 转换和 QC

两个任务的代码范围、业务目标、风险边界和负责 Agent 都不相同，但尝试启动第二个任务时，运行时返回：

```text
state_conflict: Another run is active; wait, hand off, finish or cancel it first
```

## 复现步骤

在项目根目录执行：

```bash
VIBE_CONFIG="${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}"
VIBE_RUNTIME="${VIBE_RUNTIME:-$VIBE_CONFIG/vibe-workflow}"
VIBE_PYTHON="${VIBE_PYTHON:-$(cat "$VIBE_CONFIG/vibe-python") }"
"$VIBE_PYTHON" "$VIBE_RUNTIME/scripts/vibe.py" --root . task begin \
  --task-id T-021-v3-engineering-spec \
  --run-id R-022 \
  --next-action '开始 LeRobot v3 工程规格'
```

前置状态中 `R-021` 属于另一个 Agent，且仍为 active。命令不会检查任务是否独立、写入范围是否互斥、负责人是否不同，而是直接拒绝。

## 期望行为

运行时至少应支持以下一种明确模型：

### 推荐模型：按任务/写入范围并发

允许多个 active Run 同时存在，但要求：

1. 每个 Run 绑定一个 Task、Agent/session 和明确写入范围；
2. 只有写入范围重叠、共享资源冲突或同一任务重复执行时才拒绝；
3. 不同目录/模块、不同业务目标、不同 Agent 的任务可以并发；
4. Project Log 的 SQLite projection、ledger 和 generation 写入仍必须原子化；
5. 并发记录冲突应通过 revision/generation CAS 处理，而不是用全局单活动 Run 锁代替；
6. `status` 应展示多个 active Run 及其 owner、scope、阻塞和下一步。

### 可接受的临时模型：显式 session 隔离

如果暂时无法实现范围锁，可允许不同 OpenCode session 的 Run 并存，并在同一任务或共享范围发生冲突时拒绝。主 Agent 不应被另一个 session 的无关任务阻塞。

## 当前绕过方式的问题

不应让当前 Agent 直接执行以下操作：

- handoff 其他 Agent 的 active Run；
- cancel 其他 Agent 的任务；
- 复用其他 Agent 的 Run ID；
- 假设任务已完成并强制 finish；
- 手工修改 SQLite、ledger 或生成视图。

这些做法会破坏任务所有权、验证证据和审计链。

## 初步根因假设

`task begin` 或其底层状态机把“项目存在 active Run”当成全局互斥条件，而没有按 Task/owner/scope 进行冲突判定。需要维护者检查：

- active run 查询和唯一性约束；
- task begin 的冲突检测；
- SQLite schema/index/trigger；
- ledger append 与 projection rebuild 的并发安全；
- workspace generation 与跨 session CAS；
- plugin goal/session 与 Project Log Run 的边界。

## 建议验收测试

1. Session A 启动 `T-A`，范围 `module_a`。
2. Session B 启动 `T-B`，范围 `module_b`，应成功。
3. Session B 再启动与 `T-A` 写入范围重叠的任务，应明确报告 scope conflict。
4. 两个 session 并发写不同记录，ledger 不丢记录、不破坏 hash 链，projection 可恢复。
5. 同一 Task 被两个 Agent 同时 begin，应拒绝或创建明确的受控 attempt，不能静默双写。
6. 一个 Agent handoff/finish 自己的 Run，不得改变另一个 Agent 的 Run。
7. `status` 能列出所有 active Run，而不是只暴露一个 current Run。

## 影响

- 无法并行推进独立业务任务；
- 主 Agent 被迫等待其他 Agent，或面临越权结束他人任务的选择；
- 违背 Vibe Workflow 的子 Agent 并行协作设计；
- 在 strict 任务中可能诱发不安全的“强行释放锁”操作；
- 当前 LeRobot v3 落地任务因此暂时无法通过正式 `task begin` 启动。

## 修复完成标准

修复后应提供：

- 变更说明和兼容/迁移说明；
- 上述并发与冲突检测测试；
- 至少一个跨 session 的实际复现验证；
- 不改变已有任务、Run、ledger 和历史证据；
- 明确说明旧版“全局单 active Run”数据如何兼容读取。
