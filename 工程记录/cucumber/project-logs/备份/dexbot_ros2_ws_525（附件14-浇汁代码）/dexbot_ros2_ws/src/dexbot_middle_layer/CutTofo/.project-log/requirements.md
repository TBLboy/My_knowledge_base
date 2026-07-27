# Requirements

## Project Summary

- **Goal**: 使用双珞石（xCore）AR5 机械臂实现自动化切豆腐（CutTofu）系统，支持视觉引导的圆形阻抗切割和垂直位置切割，含人工协作工作流。
- **Users / Operators**: 机器人操作员（需人工转豆腐）
- **Current stage**: Code migrated to skill-based architecture; left-arm skills under development

## Requirements

- 双臂协作：右臂持刀切割，左臂夹持黄瓜/豆腐
- 视觉感知：RealSense 深度相机 + SAM3 分割 + 6D 位姿估计
- 7 阶段切割工作流（抓刀 → 预备 → 圆切 × 2 → 人工转豆腐 → 竖切）
- 阻抗控制切割（水平圆切）+ 位置控制切割（垂直切割 + 推力）
- LinkerHand O6 灵巧手抓取刀把
- 人工协作等待（转豆腐后继续）
- MuJoCo 仿真支持

## Task Scope

### In scope
- 右臂切割技能（handle_approach / prepare / cut_round / vertical_cut）
- 左臂夹持技能（cucumber_hold）
- 工作流编排（tofu_orchestrator）
- 视觉感知堆叠（SAM3 + 位姿估计）
- 手眼标定工具
- MuJoCo 仿真验证

### Out of scope
- SAM 模型训练（使用现成 SAM3）
- 底层机械臂固件开发（使用 xCore SDK）

## Constraints

- ROS 2 Humble
- xCore SDK (Python, v0.5.1.ar_12)
- 双臂 IP 固定：左 192.168.2.160，右 192.168.2.161
- 通信协议：rmw_cyclonedds_cpp
- LinkerHand O6 通过 CAN 总线控制

## Acceptance Criteria

- [ ] 双臂启动后可完成全自动抓刀 → 切豆腐流程
- [ ] 视觉可稳定识别刀把和豆腐位置
- [ ] 圆形阻抗切割可切透豆腐（8 周期，step_z -0.0155m）
- [ ] 垂直切割可切透豆腐（11 周期，step_z -0.006m）
- [ ] 人工转豆腐后工作流可继续
- [ ] 左臂夹持技能可稳定夹持黄瓜

## Decisions

- Skill 包架构：每个技能独立 ROS2 包 + Action 接口 + YAML 配置
- 左臂使用 xCore SDK 直连（非 ROS service），右臂通过 ROS service 控制
- 视觉几何追踪使用 in-process VisionGeometryTracker（替代独立的 tofu_state_node）
- 工作流使用 tick-driven 状态机（非 behavior tree）
