# Known Issues

## Active Issues

### KI-20260616-001: RH20T QC 文档未获取

- Symptom: RH20T 调研无法深入，节点 B 部分阻塞
- Related node: B
- Related edge: A->B
- Reproduction: 访问 https://rh20t.github.io/ 尚未提取 QC 流程细节
- Status: Open
- Impact: 多模态同步、接触操作 QC 参考缺失

### KI-20260616-002: TeleDex 实际数据样本不可用

- Symptom: 无法在真实 TeleDex 数据上验证 QC 指标提取方法
- Related node: C, D
- Related question: Q-20260616-004
- Status: Open
- Impact: QC 适配方案仅能基于文档推导，无法实证验证

### KI-20260616-003: TeleDex telemetry.npz 完整 schema 未归档

- Symptom: 项目记录仅包含部分已知字段，完整字段列表未写入工程记录
- Related node: C
- Status: **Resolved**（2026-06-16，TeleDex 官方数据说明文档 V3.0 已完整记录）
- Resolution: 完整 schema 写入 `api/teledex-data-format.md` 和 `hardware/interface-protocols.md`

## Resolved Issues

### KI-20260616-R001: PDF 文本提取失败

- Symptom: PDF 读取工具无法提取 Linker TeleDex 文档文本
- Resolution: 使用 `pdftotext` 命令行工具成功提取
- Verification: PDF 内容已阅读并记录到 nodes.md / candidate-insights.md
- Related progress: `progress.md` 2026-06-16 Earlier 条目

## Notes

- 调研项目的 "issues" 主要是信息缺口，不是代码 bug
