# Reusable Patterns

## Pattern: 真实场景采集应在预处理阶段裁剪idle frame

- Scope: workflow
- Status: validated
- Rule: 真实机器人数据采集系统应在预处理阶段实现idle frame自动裁剪，而不是仅在训练前QC
- When to use: 大规模真实场景机器人数据采集
- When not to use: 仿真数据采集（无需idle frame）
- Evidence refs:
  - doc/droid_qc_research/DROID_QC调研报告.md
  - DROID数据集100条episode样本0%idle
- Notes:
  - DROID官方提供keep_ranges文件标注有效片段，说明原始数据确实有idle但预处理时裁掉了

## Pattern: QC指标应量化并设置明确阈值

- Scope: workflow
- Status: validated
- Rule: 数据质量指标应可量化计算，并设置明确阈值（如spike>3σ、saturation>15%等）
- When to use: 设计数据质检体系时
- When not to use: 定性评估或人工复核阶段
- Evidence refs:
  - DROID QC调研报告中所有指标都有具体数值和阈值建议
- Notes:
  - 量化指标便于自动化实施和阈值调整