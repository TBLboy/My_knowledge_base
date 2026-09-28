# TASK-097 工程说明（设计规格任务）

- **任务**：编写「自动理论科研 Agent」应用层设计规格集 00-08（仅设计）
- **Goal**：GOAL-006
- **分支**：`opencode-auto-research`（从 `opencode` 播种）
- **风险等级**：high（`vibe route`：多个文件 + 影响架构规划）
- **权威级别**：B（交付设计；C 级语义留在 open questions）

## 1. 任务目标与非目标

**目标**：把任务书 v0.1 转成可评审、可实现、可机器校验的设计规格。
**非目标**：不写实现代码、不搭骨架、不选型定稿、不修改 vibe 工作流运行时。

## 2. 相关业务原子与验收标准

本任务不直接实现业务原子；其验收以 `TASK-097.extensions.done_when` 与 GOAL-006 的 `SC-001..004` 为准：

- 交付 00-08 + 索引，且相互引用一致；
- Research State Schema 可机器校验；
- Agent Contracts 含输入/输出/权限/失败语义/对抗关系；
- Kill Criteria 与 Claim Ledger 可执行；
- MVP-0 状态机绑定状态/事件/产物并映射 vibe；
- C 级未决项登记为 open questions；
- 独立 reviewer GO。

## 3. 现有行为与证据

分支 `opencode-auto-research` 此前无 auto-research 设计文档（播种自 `opencode`）。既有可复用机制（`docs/OPENCODE-SEED.md`、`.project-log` 状态库（Project Log format 2，SQLite store schema 3）、subagent 角色）已核对。

## 4. 目标行为

交付如下文档（均在 `docs/auto-research/`）：

| 文件 | 作用 |
|---|---|
| `README.md` | 索引、术语契约、复用边界、非目标 |
| `00_vision.md` | 定位、质量向量、差异化、路线、成功度量 |
| `01_research_state_schema.md` | 实体/字段/关系/provenance/不变量 |
| `02_agent_contracts.md` | 23 个角色契约 + 权限矩阵 + 对抗图 |
| `03_innovation_operator_library.md` | 算子契约、族、初始 20 算子、pattern card |
| `04_idea_search_and_kill_criteria.md` | 生命周期、四类检查、KC-01..07、复活 |
| `05_theory_engine.md` | 证明流水线、独立性规则、定理状态机 |
| `06_experiment_engine.md` | claim-driven 实验、funnel、确定性裁决 |
| `07_evidence_and_provenance.md` | Claim Ledger、证据状态、失败记忆、Writer 门禁 |
| `08_mvp0_specification.md` | MVP-0 状态机 S0-S6、事件、产物、验收 |
| `OPEN_QUESTIONS.md` | OQ-01..OQ-26（含推荐与影响） |

## 5. 受影响文件/模块

新增：`docs/auto-research/**`（11 个 md）。  
不修改：仓库任何既有代码/文档（README.md 除外，未改动）。

## 6. 接口与 schema 变更

无代码接口变更。新增**设计层 schema**（Research State 实体、Claim/Evidence 状态机、算子契约），并给出与 vibe record/evidence 的映射；是否真正新增 record kind 留 `OQ-02`。

## 7. 状态/并发/生命周期

设计层定义状态机（Idea、Theory、Claim、Evidence、MVP-0 S0-S6）。未引入并发实现。

## 8. 校验/错误/重试/超时/幂等

定义 10 条机器可校验不变量（`01` 第 8 节）与 7 条 Kill Criteria（`04` 第 5 节）。实现层验证待人。

## 9. 安全/隐私

MVP-2 实验沙箱边界列为 `OQ-22`（C 级，需用户批准）。

## 10. 日志/度量/诊断

MVP-0 成功度量分项见 `00` 第 7 节；阈值留 `OQ-07`。

## 11. 兼容/迁移/回滚

纯新增文档，向后兼容；回滚 = 删除 `docs/auto-research/` 或回退分支。

## 12. 测试矩阵与验收证据

| 检查 | 方法 | 结果 |
|---|---|---|
| 文件齐全 | 目录列举（11 个 md） | 待复核 |
| 交叉引用一致 | OQ 引用/dangling link 扫描 | 通过（OQ-01..26 全部定义，无断链） |
| 索引一致 | README 文档地图 vs 实际文件 | 通过 |

## 13. 开放问题与权限

见 `docs/auto-research/OPEN_QUESTIONS.md`。C 级：OQ-01/07/09/16/22/26。
