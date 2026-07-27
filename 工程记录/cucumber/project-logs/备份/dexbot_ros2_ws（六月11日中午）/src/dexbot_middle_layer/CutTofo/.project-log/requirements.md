# Requirements

## Project Summary

- Goal: 实现双臂机器人（xCore + LinkerHand）自动化食物处理流水线，包括取刀、切豆腐（水平/垂直）、握黄瓜、抓料摆放、倒酱料等技能编排与执行。
- Users / Operators: 实验室操作人员，通过 GUI 或命令行触发工作流，部分阶段需人工介入（如旋转豆腐）。
- Current stage: 总体能跑通，但仍需优化（见最新 commit 评语）。

## Requirements

1. 系统能按 YAML 配置文件定义的多步骤工作流顺序执行各 skill。
2. 支持豆腐切割完整流程：取刀 → 预备 → 水平切 → 人工旋转 → 预备 → 水平切 → 人工旋转 → 预备 → 垂直切。
3. 支持黄瓜切割流程：左臂握持 → 预备 → 水平切 → 释放。
4. 支持抓料摆放 + 倒酱料流程。
5. 每个 skill 作为独立的 ROS 2 Action Server 运行，通过 Action 通信。
6. Orchestrator 以 tick 驱动状态机方式顺序调用各 skill。
7. 关键阶段支持人工介入等待（operator wait），通过文件/服务/终端三种方式恢复。
8. 视觉依赖 RealSense + SAM3 分割 + pose 估计。
9. 支持阻抗控制切割（cut_round）和位置控制切割（vertical_cut）。
10. 支持左右双臂协调（右臂持刀，左臂握持/抓料/倒酱）。
11. 手臂控制基于 xCore SDK 直连执行器。
12. 中长期目标是逐步消除豆腐流程中的人工介入，优先替代第二次斜切后人工拨掉豆腐条的步骤。

## Task Scope

- In scope: 豆腐切割完整流程、黄瓜切割流程、抓料+倒酱流程、视觉引导、人工介入恢复。
- Out of scope: 未知。

## Constraints

- 硬件：两台 xCore AR5 系列 7-DOF 工业臂，右臂（192.168.2.161）持刀，左臂（192.168.2.160）辅助。
- 灵巧手：LinkerHand（CAN 总线通信，O6 夹爪）。
- 视觉：RealSense D415/D435 + SAM3 分割模型。
- SDK：xCore 直接 SDK 控制（非 ROS 标准 joint_trajectory_controller）。
- 框架：ROS 2 Humble（rclpy/rclcpp）。
- 手臂控制接口使用自定义低层 Action（非 standard ROS 2 control）。

## Acceptance Criteria

- 工作流 YAML 定义 → orchestrator 能正确顺序执行。
- 每个 skill Action server 能独立启动、接收 goal、执行、返回结果。
- 人工介入等待能可靠触发和恢复。
- 视觉检测能定位目标物（豆腐/黄瓜/刀柄）并计算切割位姿。
- 切割轨迹能完成完整切割周期且不碰撞。

## Decisions

- 见 `business-logic/decision-records.md`。

## Open Questions

- 见 `business-logic/open-questions.md`。
