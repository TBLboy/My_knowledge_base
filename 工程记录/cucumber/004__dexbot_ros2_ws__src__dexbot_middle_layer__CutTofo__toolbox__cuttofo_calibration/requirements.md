# Requirements

## Project Summary

- Goal: 手眼标定 + TCP 标定 GUI 工具，支持手动/自动模式，实时相机画面
- Users: tbl (切豆腐项目)
- Current stage: 代码框架完成，待实机验证

## Requirements

- 实时显示相机画面（640×480，等比例缩放铺满）
- ArUco 标记检测叠加 + 位姿 HUD
- 手动模式：逐点记录采样
- 自动模式：自动移动机械臂 + 采样
- 采样列表实时显示（TCP 位置、稳定状态）
- 标定结果计算（RMSE 评估）
- 采样数据本地保存（CSV）
- 业务逻辑与界面代码文件级分离
- 一键启动（ROS2 launch）
- 支持 Lbot 机械臂（DEXBOT_ARM_BACKEND=lbot）

## Task Scope

- In scope:
  - 手眼标定 GUI 前端（Tkinter）
  - 与现有 `hand_eye_calibration_node` 的后端通信（ROS2 Service/Topic）
  - 实时相机画面渲染
  - ArUco 位姿监控 + 稳定判定
  - 采样数据本地管理 + CSV 导出
- Out of scope:
  - 修改现有 `hand_eye_calibration_node` 核心逻辑
  - TCP 偏移标定算法（预留接口，暂不实现）
  - 标定板自动识别

## Constraints

- GUI 框架: Tkinter（工作空间已有先例）
- 图像嵌入: cv2 → PIL → Tkinter Canvas
- ROS2 通信: Service + Topic，不修改现有标定节点
- 画面比例: 75% 相机 : 25% 控件
- 平台: Linux (Ubuntu 22.04 + ROS2 Humble)
- Lbot IP: 192.168.10.21

## Acceptance Criteria

- [ ] 启动后实时显示相机画面（>15fps）
- [ ] ArUco 位姿 HUD 叠加正确
- [ ] 手动模式下 Enter 记录采样
- [ ] 采样列表实时更新
- [ ] 标定计算后显示 RMSE
- [ ] 一键 launch 启动完整环境

## Decisions

| 决策 | 方案 | 理由 |
|------|------|------|
| GUI 框架 | Tkinter | workspace 已有 `hand_eye_replay_gui.py` 先例 |
| 业务/界面分离 | 文件级（`business/` `view/`） | 可单测业务逻辑，可替换 UI 框架 |
| ROS2 线程 | MultiThreadedExecutor | 不阻塞 Tkinter 主循环 |
| 刷新率 | 30fps (33ms) | 平衡流畅度与 CPU |

## Open Questions

- TCP 偏移标定是否需要集成到同一 GUI？
- 是否需要标定结果的可视化对比（投影误差热力图）？
- 是否需要支持多摄像头切换？
