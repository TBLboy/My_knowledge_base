# Hardware Architecture

## Collection Platform

数据采集平台：**Linker Open TeleDex**（灵心巧手）

## Robot System

| 组件 | 型号/规格 | 角色 |
|------|-----------|------|
| 机械臂 | Linker Arm LA7 | 双臂操作 |
| 灵巧手 | Linker Hand O6 / L6 / L20 / L25 | 末端执行器 |
| 遥操作 | Linker TA + TG / FFG / MCG 手套 | 数据采集控制 |
| 外部相机 | Orbbec Gemini 335L | RGB-D 外部视角 |
| 腕部相机 | Orbbec Gemini 2 | RGB-D 腕部视角 |

## Camera Configuration (Target)

参考 DROID 三视角配置，与 TeleDex 平台实际布置以采集文档为准：
- 外部视角 × 2（RGB-D）
- 腕部视角 × 1（RGB-D）

## Data Recording Pipeline

```text
ROS2 实时话题
    ↓
MCAP 原始录制（raw）
    ↓
后处理转换
    ↓
telemetry.npz + camera_info.json + manifest.json + metadata.json + videos
```

## Research vs Production

本调研项目不直接操作硬件。硬件信息用于：
1. 理解 TeleDex 数据格式的物理含义
2. 设计 QC 指标时考虑传感器能力（如同步、标定、触觉/力传感）
3. 对比公开数据集（DROID: Franka + 二指夹爪 vs 本公司: LA7 + 灵巧手）

## Open Items

- 实际部署的相机数量与命名需以采集样本或平台文档确认
- 灵巧手具体型号（O6/L6/L20/L25）在不同 episode 中可能不同，需从 metadata 读取
