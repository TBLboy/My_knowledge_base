# Open Business Logic Questions

## Active Questions

### Q-20260526-001

- Related node: CodeBaseCurrentState
- Related edge: Phase1_Cleanup
- Question: `CutTofo/sdk/` 下的 `demo_cut_smooth_pro.py`（3339行）、`xcore_cut_tofu_vertical.py`（1466行）、`xcore_cut_tofu.py`（1317行）等脚本是否仍在被 ros 节点调用？还是纯历史遗留？
- Why it matters: 决定这些文件是归档（删除/移走）还是保留
- Options: 
  1. 检查所有 ros 节点是否有 import 引用
  2. 检查 .launch.py 是否启动这些脚本
  3. 问用户确认
- Current status: Open
- Answer: Unknown

### Q-20260526-002

- Related node: CodeBaseCurrentState
- Related edge: Phase1_Cleanup
- Question: `dexbot_high_layer/` 的切黄瓜代码是否已完全废弃？
- Why it matters: 决定是否归档整个包
- Options:
  1. 搜索是否有其他模块 import 这些文件
  2. 搜索 launch 文件是否引用
- Current status: Open
- Answer: Unknown

### Q-20260526-003

- Related node: CodeBaseCurrentState
- Related edge: Phase1_Cleanup
- Question: `gui_backup/gui/` 和 `gui_backup/gui2/` 中是否有未被迁移到当前 `src/gui/` 的独特代码？
- Why it matters: 如果备份中有独特代码，删除前需要先迁移
- Options:
  1. diff 比较 `gui_backup/gui/` 和 `src/gui/` 的文件差异
  2. 问用户确认备份是否可以安全删除
- Current status: Open
- Answer: Unknown

### Q-20260526-004

- Related node: CodeBaseCurrentState
- Related edge: Phase2_ExtractShared
- Question: 多个切豆腐实现中（`cuttofo_xcore`、`cuttofo_lbot`、`CutTofo/`），哪一个应该作为"主实现"保留，其他改为适配层？
- Why it matters: 决定提取共享抽象时的基线和合并方向
- Current status: Open
- Answer: cuttofo_xcore 是当前主线（根据 PROJECT_OVERVIEW.md）

## Resolved Questions

- None yet.
