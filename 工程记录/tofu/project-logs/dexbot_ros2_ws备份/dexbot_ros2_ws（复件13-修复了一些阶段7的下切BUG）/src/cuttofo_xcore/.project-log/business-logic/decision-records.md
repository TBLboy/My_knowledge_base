# Business Logic Decision Records

## 2026-05-17 Local Time (规划最终定稿 — 用户画框方案)

- **Decision**: 用户拖拽画框 → BOX MODE / 删框 → TEXT MODE
- **问题**: 豆腐切割后形态改变，文本提示可能检测失败
- **方案**: 用户在相机画面拖拽画框，框存在期间 SAM3 用该框做分割，框删除后回退文本自动检测
- **核心变化 vs 旧点→BBox 方案**:
  - 用户操作: 拖拽画框 (非固定40px)
  - 无推理锁: 单一 auto_detect_callback 统一处理 BOX/TEXT 切换
  - 模式切换: 框存在=BOX, 框删除=TEXT (用户手动右键删除)
  - 无自动恢复: BOX 检测失败保持框，用户决定何时删
- **ROS Topic**: `/sam3/user_box` (sensor_msgs/RegionOfInterest)
- **可视化**: 用户框=黄色, SAM3结果=绿色 (不变)
- **Interaction**:
  - 左键拖拽 → 画框 (BOX MODE)
  - 右键点击 → 删框 (回退 TEXT MODE)
  - 拖拽太小(<5px) → 忽略
- **Plan file**: `sam3-point-prompt-research.md` 章节 8 (完整代码模板)
- **Status**: **planned** (规划完成，待实现)
