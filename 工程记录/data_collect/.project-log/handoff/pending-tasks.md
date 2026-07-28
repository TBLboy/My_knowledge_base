# Pending Tasks

## 当前第一任务（P0）

- [ ] **DQAF 精读** → 写入 `doc/reports/02_data_quality_assessment_frameworks.md` §1
- [ ] **TeleDex QC 指标映射表 v0.1** → 写入 `doc/reports/04_teledex_qc_summary.md` §7
- [ ] 指标分 A/B/C 类：现在能做 / 需样本标定 / 需额外标签

## 本周排期（Week 1）

| Day | 任务 | 交付物 |
|-----|------|--------|
| Day 1 | DQAF 精读，提取 episode-level 指标 | `02` §1 DQAF 章节 + 指标对照表 |
| Day 2 | TeleDex QC 指标映射表 v0.1 | `04` §7 |
| Day 3 | RH20T 调研（接触/多模态） | `01` §2 RH20T 章节 |
| Day 4 | score_lerobot_episodes 文档调研（不复现） | `02` §2 |
| Day 5 | 更新汇总报告 | `04` §6–§8 初稿（§6 70%、§7 70%、§8 50%） |

## 下周排期（Week 2）

| Day | 任务 | 交付物 |
|-----|------|--------|
| Day 1 | 补报告 01（RoboMimic/OXE/LeRobot/RoboCasa） | `01` 80% 初稿 |
| Day 2 | 补报告 02（Green-VLA/Consistency/PSD） | `02` 90% 初稿 |
| Day 3 | 报告 03 轻量版（远期方向） | `03` 60–70% 初稿 |
| Day 4 | 汇总报告 v0.2 | `04` 可给领导看 |
| Day 5 | 内部 Review | `review_notes.md` 或更新 open-questions |

## 第 3 周（收敛）

- 三报告 v0.2 + `04` v1.0 领导版
- 完善 §8 reason codes、§9 实施路线图

## 需向团队/平台方确认（P0）

- [ ] **P0-1**：TeleDex 是否有 success/failure 标签？
- [ ] **P0-2**：是否有 task/language instruction 字段？
- [ ] **P0-3**：能否获取 5–10 条实际 TeleDex 样本？
- [ ] **P0-4**：LA7 / Linker Hand 关节上下限、安全范围正式表？
- [ ] **P1-5**：collect_tactile 是否实际启用？

## 明确不做（当前阶段）

- QoQ / DemInf / SCIZOR 深入调研
- score_lerobot_episodes 代码复现
- RoboCasa / OXE 优先投入（放 Week 2）
- QC 系统代码实施

## 核心交付物（本周结束目标）

一张表：**QC 指标 → TeleDex 字段 → 是否可计算 → 是否需确认 → 优先级 → 处理策略**

写入 `doc/reports/04_teledex_qc_summary.md` §7
