# Candidate Insights

## 2026-06-16 - DROID数据集无idle frame问题

- Type: insight
- Status: validated
- Importance: high
- Reusable: yes
- Summary: DROID数据集在预处理阶段已经裁掉了开头和结尾的idle frame，100条episode样本中0%idle
- Evidence refs:
  - doc/droid_qc_research/DROID_QC调研报告.md
  - scripts/droid/droid_qc_deep_research.py运行结果
- Why it may matter later: 真实场景采集数据应在预处理阶段实现idle frame自动裁剪，而不是仅在训练前QC
- Next decision: copy to reusable-patterns

## 2026-06-16 - Linker TeleDex数据格式完整且结构清晰

- Type: architecture
- Status: validated
- Importance: medium
- Reusable: yes
- Summary: Linker TeleDex使用三层架构（raw MCAP -> processed telemetry.npz + JSON + videos），提供完整的时间戳、相机标定、同步校验字段
- Evidence refs:
  - Linker Open TeleDex数据说明文档PDF（全19页）
  - telemetry.npz包含sync_validation_is_valid、sync_validation_max_diff字段
- Why it may matter later: Linker TeleDex格式已经具备基础QC能力（同步校验），后续QC方案可以基于这些字段增强
- Next decision: keep watching

## 2026-06-16 - 公开数据集QC规则可量化迁移

- Type: workflow
- Status: validated
- Importance: high
- Reusable: yes
- Summary: 从DROID提取的7条QC规则（idle frame、spike、saturation、language instruction等）可以量化计算并设置阈值
- Evidence refs:
  - doc/droid_qc_research/DROID_QC调研报告.md（第4章）
  - DROID spike比例2.14%，saturation比例9.555%，均有具体阈值
- Why it may matter later: 这些规则可以直接用于Linker TeleDex数据的QC实施
- Next decision: copy to reusable-patterns