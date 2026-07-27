# Anti-Patterns

## Anti-Pattern: 不要在采集前设计复杂的数据格式

- Bad assumption or trap: 调研开始时设计新的数据格式（如KitchenDex），但实际采集平台已确定
- Why it is tempting: 想要设计"理想"的数据格式
- Consequence: 设计工作浪费，需要重新适配实际数据格式
- Safer alternative: 先调研现有平台数据格式，基于现有格式设计QC方案
- Evidence refs:
  - 项目最初调研报告设计了KitchenDex-Data格式
  - 用户说明实际使用Linker TeleDex平台
  - decision-records.md中记录了数据平台已确定的决策

## Anti-Pattern: 不要在调研阶段直接开始方案实施

- Bad assumption or trap: 调研过程中直接开始编写QC代码或设计完整系统
- Why it is tempting: 想要快速推进工作
- Consequence: 调研不完整，方案可能有遗漏或错误
- Safer alternative: 完成调研，形成方案建议，等待领导决策后再实施
- Evidence refs:
  - 用户明确说明现阶段是调研阶段
  - decision-records.md中记录了项目定位决策