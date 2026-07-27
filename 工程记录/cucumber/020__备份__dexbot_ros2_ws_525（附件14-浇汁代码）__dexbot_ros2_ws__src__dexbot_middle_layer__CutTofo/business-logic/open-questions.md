# Open Business Logic Questions

## Active Questions

### Q-20260604-001 — 左臂切割技能的镜像参数配置

- **Related node**: B, C, D, F, G, H
- **Related edge**: A-B, A-C-D, E-H
- **Question**: 为左臂创建镜像的切割技能时，哪些参数需要从右臂配置镜像转换？
- **Why it matters**: 需要为左臂复制 prepare / cut_round / vertical_cut 等技能并做坐标镜像
- **Options**:
  - 左臂使用已有 `mirror_pos/rotmat/quat/corners` 函数变换参数
  - 左臂使用独立的 `calibration_result_left.yaml`
  - 需要为左臂定义独立的 TCP 工具偏移
- **Current status**: Open
- **Answer**: Unknown

### Q-20260604-004 — 双臂同时切割的协调

- **Related node**: All
- **Question**: 双臂是否需要在切割过程中协调（如防碰撞）？
- **Options**:
  - 臂交替工作，不会同时运动（当前模型）
  - 需要防碰撞检查
  - 需要同步控制
- **Current status**: Open
- **Answer**: Unknown

## Resolved Questions

### Q-20260604-002 — 左臂技能包命名（已解决）

- **Resolution**: 为浇酱任务创建独立包 `cuttofo_skill_sauce_pour`，不嵌入现有包
- **Reason**: 浇酱是独立的左臂任务，与切割技能无共享逻辑；独立包便于维护和调试
- **Date**: 2026-06-04

### Q-20260604-003 — 左臂 TCP 偏移（已解决）

- **Resolution**: 左臂浇酱时使用瓶口 TCP offset（瓶口相对法兰的平移旋转），在 `sauce_pour_params.yaml` 中设置 `tool_offset`；左臂不持刀，全零 TCP 偏移适用于非浇酱场景
- **Reason**: 瓶口 TCP 使视觉锁豆腐中心后可直接作为目标点，无需额外坐标变换
- **Date**: 2026-06-04
