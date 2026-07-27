# Open Knowledge Questions

## KQ-20260616-001

- Observation: Linker TeleDex的manifest.json和metadata.json已包含sync_error字段
- Why it might matter: 表明Linker TeleDex系统可能已经内置基础QC功能
- Missing evidence: 不确定Linker TeleDex是否还有其他QC功能（如自动idle裁剪、spike检测等）
- Current status: open
- Related refs:
  - Linker Open TeleDex数据说明文档PDF第15-17页

## KQ-20260616-002

- Observation: DROID完整版提供keep_ranges文件标注有效片段，但样本中未见
- Why it might matter: 说明DROID原始数据确实有idle，预处理时裁掉，但预处理方法未公开
- Missing evidence: DROID如何自动识别idle frame并裁剪的方法未公开
- Current status: open
- Related refs:
  - doc/droid_qc_research/DROID_QC调研报告.md
  - DROID论文可能有预处理章节

## KQ-20260616-003

- Observation: RH20T数据集强调多模态同步和接触操作质检
- Why it might matter: 对灵巧手接触操作质检有重要参考价值
- Missing evidence: RH20T具体的QC流程文档未获取
- Current status: open
- Related refs:
  - https://rh20t.github.io/