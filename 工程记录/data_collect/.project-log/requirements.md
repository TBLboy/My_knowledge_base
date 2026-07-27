# Requirements

## Project Summary

- **Goal**: 调研机器人操作数据集质检与清洗方法，形成质检方案建议
- **Users / Operators**: 数据采集团队、质检团队
- **Current stage**: 调研阶段（不是实施阶段）

## Requirements

### 调研目标
1. 研究公开机器人数据集的数据质检流程
2. 提取可量化的数据质量指标
3. 分析基于Linker TeleDex采集数据如何实施质检
4. 形成数据质检与清洗方案建议

### 调研范围
- 公开数据集调研：DROID、RH20T、RoboCasa、Open X-Embodiment等
- 数据质量评估论文调研：DQAF、Consistency Matters等
- Linker TeleDex数据格式深度理解
- 现有采集数据质量分析

## Task Scope

### In scope
- 公开数据集QC文献调研
- Linker TeleDex数据格式解读
- 从telemetry.npz等文件提取QC指标的方法研究
- 数据清洗策略建议
- 调研报告撰写

### Out of scope（现阶段）
- 具体质检系统代码实施
- 数据清洗工具开发
- 自动化QC系统部署
- 模型训练相关工作

## Constraints

- 数据采集平台已确定：Linker Open TeleDex系统
- 数据格式已固定：telemetry.npz、camera_info.json、manifest.json等
- 调研周期：有限时间内完成调研，形成方案建议

## Acceptance Criteria

- 完成三份深入调研报告：
  - 报告 01：公开数据集的隐式 QC 策略
  - 报告 02：数据质量检测框架
  - 报告 03：数据筛选 / 数据策展框架
- 完成 Linker TeleDex 数据格式 QC 适配方案（汇总报告 §4）
- 形成可交付给领导的汇总调研报告（`doc/reports/04_teledex_qc_summary.md`）
- 提出可行的质检与清洗实施建议

## Decisions

- 2026-06-16: 项目定位为调研阶段，不直接开始方案实施
- 2026-06-16: 数据采集平台使用Linker Open TeleDex，数据格式已确定
- 2026-06-16: 调研交付物拆分为三份深入报告 + 一份 TeleDex 汇总报告（基于 `robot_dataset_qc_curation_survey.md` 三个方向）

## Open Questions

- Linker TeleDex系统是否已有部分QC功能？需要进一步确认
- 是否可以获取实际采集的数据样本进行QC指标测试？需要确认
- 质检方案是否需要考虑后续自动化实施？需要确认优先级