# Debugging History

## 2026-06-16 - PDF 文本提取工具失败

- Symptom: 内置 PDF 读取工具无法提取 Linker Open TeleDex 数据说明文档文本
- Reproduction: 尝试读取 TeleDex PDF 文档
- Affected area: 节点 C（Linker TeleDex 数据格式分析）
- Hardware state: N/A（文档处理问题）
- Attempted fixes:
  1. 内置 PDF 读取工具 — 失败，无法提取文本
- Final resolution: 使用 `pdftotext` 命令行工具成功提取 PDF 内容
- Verification: PDF 全 19 页内容已阅读，核心结构已记录
- Reusable lesson: 对于中文/复杂排版 PDF，优先尝试 `pdftotext` 而非 IDE 内置 PDF 阅读器
- Evidence refs:
  - `progress.md` 2026-06-16 Earlier 条目

## Notes

- 本项目为调研工程，调试记录以文档处理和数据分析问题为主
- DROID 分析脚本运行未记录重大故障
