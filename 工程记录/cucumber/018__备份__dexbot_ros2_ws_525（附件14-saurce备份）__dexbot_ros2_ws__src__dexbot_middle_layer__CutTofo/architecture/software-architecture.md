# Software Architecture

## Overview

CutTofo 采用 ROS 2 多包分层架构：

```
┌──────────────────────────────────────────────────────┐
│                    Orchestrator                       │
│              (tofu_task_orchestrator)                  │
│   Tick-driven state machine, Action clients only      │
└──────────────────────┬───────────────────────────────┘
                       │ Action calls
                       ▼
┌──────────────────────────────────────────────────────┐
│                   Skills Layer                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ prepare  │ │cut_round │ │vert_cut  │ │handle  │ │
│  │ Action   │ │Action    │ │Action    │ │Action  │ │
│  │ Server   │ │Server    │ │Server    │ │Server  │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ │
│       │             │             │            │      │
│  ┌────┴─────────────┴─────────────┴────────────┴──┐  │
│  │            Skill Common Library                  │  │
│  │  ArmAdapter │ IK │ Geometry │ Trajectory │ Err │  │
│  └──────────────────────────┬─────────────────────┘  │
│                             │                         │
│  ┌──────────────────────────┴─────────────────────┐  │
│  │            Skill Interfaces                     │  │
│  │           (Action/Service msg defs)             │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────┘
                       │ ROS service / SDK
                       ▼
┌──────────────────────────────────────────────────────┐
│                   Bottom Layer                         │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────┐  │
│  │ xCore SDK    │  │ Arm API ROS   │  │LinkerHand │  │
│  │ (Python)     │  │ Service Node  │  │ O6 CAN    │  │
│  └──────────────┘  └───────────────┘  └───────────┘  │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                  Perception Layer                      │
│  ┌─────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │RealSense│  │ SAM3 Detector│  │Pose Estimator    │ │
│  │Camera   │  │ (GPU)        │  │(6D pose + depth) │ │
│  └─────────┘  └──────────────┘  └──────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## Skill Package Responsibilities

| Package | Type | Node Name | Role |
|---------|------|-----------|------|
| `cuttofo_skill_interfaces` | Interface | — | Action/Service 消息定义 |
| `cuttofo_skill_common` | Library | — | Arm 适配器、IK、几何、轨迹、错误码 |
| `cuttofo_skill_tofu_prepare` | Action Server | `tofu_prepare_node` | 视觉引导切割预备位姿 |
| `cuttofo_skill_tofu_cut_round` | Action Server | `tofu_cut_round_node` | 阻抗模式水平圆切 |
| `cuttofo_skill_tofu_vertical_cut` | Action Server | `tofu_vertical_cut_node` | 位置模式垂直切割 |
| `cuttofo_skill_handle_approach` | Action Server | `handle_approach_node` | 视觉引导抓刀把 |
| `cuttofo_skill_cucumber_hold` | Action Server | `cucumber_hold_node` | 左臂夹持黄瓜 |

## Orchestrator

| Package | Executable | Role |
|---------|------------|------|
| `cuttofo_orchestrator` | `tofu_task_orchestrator` | Tick-driven 状态机，只调用 Action 客户端 |
| `cuttofo_orchestrator` | `workflow_runner.py` | Tick 主循环驱动 |

## Module Boundaries

- **Skills**: 只实现 Action server，不包含工作流逻辑
- **Orchestrator**: 只调用 Action client，不包含运动/IH/视觉
- **Vision**: 独立包，通过 ROS topic 通信
- **Common**: 技能间的共享库，不包含节点

## Threading Model

- Skill 节点：MultiThreadedExecutor (Action server)
- Orchestrator：Single thread, spin_once tick-driven
- Vision 节点：各自独立的单线程节点
