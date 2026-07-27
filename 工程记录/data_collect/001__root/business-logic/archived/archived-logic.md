# Archived Business Logic

## Archive Template

```markdown
### YYYY-MM-DD - <Archived Logic Title>

- Original path: <path>
- Original status: <main / branch>
- Reason archived: <why it was archived>
- Failure / replacement details: <details>
- Evidence: <verification, logs, test results>
- Future reuse possibility: <yes/no/unknown>
```

## Archived Items

### 2026-06-16 - KitchenDex-Data v0.1 自定义数据格式方案

- Original path: A -> (自定义格式设计) -> B
- Original status: 早期调研草稿中的替代路径
- Reason archived: 用户确认实际采集平台为 Linker Open TeleDex，数据格式已固定，不改动采集系统
- Failure / replacement details: 早期调研报告（`doc/调研报告.txt`）设计了 KitchenDex-Data v0.1 canonical schema；该方案与现有平台不兼容，已被 Linker TeleDex 格式分析路径替代
- Evidence:
  - `business-logic/decision-records.md`：数据采集平台使用 Linker Open TeleDex
  - `distill-input/anti-patterns.md`：不要在采集前设计复杂的数据格式
- Future reuse possibility: yes（部分字段设计思路可迁移到 QC 指标和 metadata 建议中，但不作为数据格式标准）
