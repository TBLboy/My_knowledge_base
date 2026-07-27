# Open Business Logic Questions

## Active Questions

### Q-20260606-001

- Related node: E（人工旋转豆腐）
- Related edge: D-E, G-H
- Question: 人工介入后如何精确恢复切割位置？operator 旋转豆腐后，豆腐位姿改变，prepare 重新视觉检测是否能可靠对齐？
- Why it matters: 若重新检测失败会导致切偏或碰撞。
- Options:
  1. 保持当前方案：prepare 重新视觉检测 → IK 求解。
  2. 增加额外的视觉验证步骤：检测后比较预期位姿。
- Current status: Open
- Answer: 未知

### Q-20260606-002

- Related node: D（水平切割）
- Related edge: C-D
- Question: 当前阻抗切割参数（stiffness、speed）是否对所有豆腐硬度和尺寸鲁棒？
- Why it matters: 不同硬度的豆腐可能需要不同的阻抗参数。
- Options:
  1. 保持固定参数。
  2. 根据视觉检测到的尺寸/类型动态调整参数。
- Current status: Open
- Answer: 未知

### Q-20260606-003

- Related node: 全局
- Question: 目前没有自动化异常恢复机制。一旦某个 Action 失败，orchestrator 如何处理？
- Why it matters: 工业生产需要自动或半自动恢复。
- Current status: Open
- Answer: 推测当前设计中，abort/kill 需要 operator 手动重启相关工作流。

### Q-20260606-004

- Related node: 黄瓜流程
- Question: 黄瓜握持 + 切割时，左右臂是否存在碰撞风险？协调机制是怎样的？
- Why it matters: 双臂近距离作业有碰撞可能。
- Current status: Open
- Answer: 未知

## Resolved Questions

- None yet.
