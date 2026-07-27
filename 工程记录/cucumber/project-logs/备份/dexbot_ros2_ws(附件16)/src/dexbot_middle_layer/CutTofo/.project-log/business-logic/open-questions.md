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

### Q-20260609-005

- Related node: 第二次斜切后 / 竖切前过渡阶段
- Question: 第二次横切后，机器人应如何自主移除挂在刀刃或留在豆腐表面的条状残料？
- Why it matters: 这是当前切豆腐 workflow 中最直接、最高频的人工介入点，也是提升端到端自治度的第一优先级。
- Current consensus:
  1. 容器检测直接消费现有 vision 节点输出，不新增独立感知节点；容器中心由检测结果直接提供，并允许通过该阶段 offset 做微调；同时通过提示词切换完成豆腐/容器/豆腐的顺序检测。
  2. 容器检测插入在第一次横切完成、用户下发继续指令且豆腐位置已送入 IK 之后；若容器检测失败，则 fallback 回现有老版本第二次横切逻辑。
  3. 新第二次横切分支执行期间持续检测容器位置；右臂每次朝容器区移动都基于最新容器检测结果执行。
  4. 右臂该阶段工作 TCP 定义为刀刃中心。
  5. 左臂目标在右臂到达容器上方并静止后，再由右臂目标 TCP 通过双臂坐标转换派生。
  6. 每个定位阶段单独保留 offset 微调参数。
  7. 动作默认单段执行，但 skill 框架需预留两段/多段扩展。
  8. hook_lift 阶段保留两种模式：默认 `translate_plus_tilt`，保留 `translate_only` 作为对照调试模式。
  9. hook_lift 的主姿态参数已收敛为 `hook_target_plane_angle_deg`，其语义与 `prepare.plane_angle_deg` 完全一致：右臂法兰 `+Z` 与 base `XZ` 平面的线面夹角。
  10. `translate_plus_tilt` 优先通过短 RT waypoint 复合段实现，不单独引入复杂连续曲线规划。
  11. transfer 阶段默认采用 RT 笛卡尔平移，且右臂在运条过程中保持刀姿不变。
  12. 到达容器上方后，第一版由右臂静止、左臂单独完成拨落动作。
  13. 左臂法兰姿态候选选择机制复用 `sauce_pour`：先做候选 IK 预检，再在所有可达候选中按法兰位置与当前目标法兰位置的距离最近原则选取。
  14. 左臂拨落候选库的采集流程也复用 `sauce_pour` 法兰姿态采集脚本：右臂先进入容器上方准备拨落状态，再人工拖动左臂采集多个候选姿态。
  15. 左臂候选姿态当前明确只约束左臂法兰坐标系姿态，手型默认直接使用 O6，不把手型是否绑定候选作为开放问题。
  16. 第二次横切整轮结束、右臂回到等待位后，检测对象切回豆腐，并同时恢复 / override Phase6 视觉参数；后续业务链与现有老流程完全一致。
- Remaining options:
  1. `hook_target_plane_angle_deg` 第一版默认标定为 `140 / 145 / 150` 哪个更合适。
  2. `translate_plus_tilt` 是采用 2 个 waypoint 还是 3 个 waypoint 更容易把豆腐条稳定带出。
  3. 左臂实际拨动轨迹的方向、形状和分段方式仍待拖动实验确认。
- Current status: Open
- Answer: 容器检测时机、失败 fallback、持续跟踪、单一容器区位姿与并行回位链路已形成共识；当前主要剩余左臂拨动轨迹。

## Resolved Questions

- None yet.
