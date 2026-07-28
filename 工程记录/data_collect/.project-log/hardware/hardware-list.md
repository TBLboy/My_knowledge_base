# Hardware List

| ID | 组件 | 型号 | 数量 | 用途 | 状态 |
|----|------|------|------|------|------|
| HW-001 | 机械臂 | Linker Arm LA7 | 双臂 | 厨房操作采集 | 已确定（平台标配） |
| HW-002 | 灵巧手 | Linker Hand O6 / L6 / L20 / L25 | 按需 | 灵巧操作采集 | 已确定（多型号可选） |
| HW-003 | 外部相机 | Orbbec Gemini 335L | ≥2 | RGB-D 外部视角 | 已确定 |
| HW-004 | 腕部相机 | Orbbec Gemini 2 | ≥1 | RGB-D 腕部视角 | 已确定 |
| HW-005 | 遥操作手套 | Linker TA + TG / FFG / MCG | 按需 | 遥操作采集 | 已确定 |

## Reference Dataset Hardware (DROID)

| 组件 | 型号 | 用途 |
|------|------|------|
| 机械臂 | Franka Panda | DROID 调研对比参考 |
| 末端执行器 | 二指夹爪 | DROID 调研对比参考 |
| 相机 | ZED 2 × 2 + ZED-Mini × 1 | DROID 三视角参考 |

## Notes

- 本公司硬件与 DROID 差异显著（灵巧手 vs 夹爪），QC 规则迁移时需考虑末端执行器差异
- RH20T 参考价值在于多模态传感（力、音频），本公司当前硬件列表未包含力传感器
