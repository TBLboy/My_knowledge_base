# Requirements

## Project Summary

- Goal: 使用双机械臂（xCore）协同完成黄瓜/豆腐的自动化切割操作。左臂按住食材，右臂进行切割。
- Users / Operators: 实验室操作人员
- Current stage: 新 Skill 架构开发与验证阶段

## Requirements

1. 左臂（cucumber_hold skill）感知并按住黄瓜，右臂（prepare + cut_round）执行切割。
2. 支持单步测试（每个 skill 可独立启动）+ 全流程编排。
3. 右臂通过 ROS service 接口控制（xcore_controller_node）。
4. 左臂通过直接 SDK 连接控制（XcoreDirectExecutor）。
5. 视觉管线：RealSense D435 → SAM3 分割 → 6D 位姿估计。
6. 双工作流：豆腐（3 阶段 6 步）+ 黄瓜（4 步：hold → prepare → cut_round → release）。
7. 新架构模块化，skill 包为 Action Server，orchestrator 为 Action Client。

## Task Scope

- In scope: 黄瓜切割全流程（左臂 hold + 右臂 prepare + cut_round + 左臂 release）
- In scope: 豆腐切割全流程（handle_approach → prepare → cut_round x2 → vertical_cut）
- In scope: 每个 skill 的单独测试
- Out of scope: MuJoCo 仿真（可跳过编译）
- Out of scope: 遗留架构（ros/ 和 sdk/ 目录，已由新 skill 架构替代）
- Out of scope: GUI 应用

## Constraints

1. 工作空间路径不能含中文字符（ROS2 Humble rosidl 适配器 bug）。
2. 嵌套在 dexbot_middle_layer/CutTofo/ 下的 skill 包需用 --paths 显式编译。
3. 右臂依赖 xcore_controller_node 提供 ROS service 接口。
4. 左臂 cucumber_hold node 使用 MultiThreadedExecutor + 独立感知线程。

## Acceptance Criteria

- 黄瓜 workflow 4 步均可成功执行，无超时/连接报错。
- 每个 skill 可通过手动发 action goal 单独测试。
- 编译命令可在新工作空间一行完成。

## Decisions

1. 2026-05-30: 从旧工作空间（含中文路径）迁移到 /home/tbl/Project/cucumber/ 解决 rosidl 编译 bug。
2. 2026-05-30: 采用新 skill 架构（ActionServer + ActionClient）替代遗留 ros/ 节点。
3. 2026-05-30: 跳过 MuJoCo 仿真包，不依赖仿真环境。

## Open Questions

- 实际硬件 IP 是否与配置一致（左臂 192.168.2.160，右臂 192.168.2.161）？
- O6 手爪是否接入 CAN 总线？左侧 can0，右侧 can1？
- SAM3 模型路径在目标机器上是否存在？
- 手眼标定文件（calibration_result_left.yaml / calibration_result_right.yaml）是否已标定？
