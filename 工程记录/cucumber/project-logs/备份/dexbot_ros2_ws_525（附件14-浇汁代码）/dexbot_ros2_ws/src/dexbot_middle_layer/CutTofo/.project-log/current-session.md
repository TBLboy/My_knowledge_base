# Current Session

## Last Updated

- 2026-06-04 19:39 Local Time

## Current Objective

- Plate Vision 方案已实施：sauce 阶段实时检测 plate 拿最新目标点，原共享 tofu 锁定方案废弃

## Current Business Logic Position

- Main path: A -> B -> C -> D -> E -> F -> G -> H -> I (豆腐全流程)
- Current edge: 左臂浇酱分支（新创建）
- Active branch: `sauce-pour` — 左臂浇酱技能（已实现包，未联调）

## Completed This Session

- ✓ 全部 7 项实现了多候选法兰姿态方案迁移
- ✓ 确认 `calibration_result_left.yaml` 默认平移 `[0,0,-0.20]` 符合实际双臂间距
- ✓ **Plate Vision 方案已实施**（P-1~P-3）：sauce_pour 实时检测 plate 获取目标点；废弃原共享 tofu 锁定方案（V-1~V-7 废弃）
- ✓ **编排器集成已实施**：sauce_pour 作为第 8 步加入 tofu_workflow（vertical_cut 后）
- ✓ 所有包编译通过：`cuttofo_skill_common`、`cuttofo_skill_tofu_prepare`、`cuttofo_skill_sauce_pour`、`cuttofo_orchestrator`
- ✓ `capture_tofu_sauce_target` 脚本：检测真实豆腐 → 计算 sauce TCP 目标 → 保存 JSON，用于后续虚拟测试
- ✓ **B-a 抬升改用 `move_to_pose_target`**：纠正 `move_position_only` 的 TCP 语义不匹配问题，直接使用 flangeInBase 控制，消除 tool_offset 非零时的偏差

## 已知待办（Issue List）

### 代码层小修复
| # | 问题 | 文件 | 说明 | 状态 |
|---|------|------|------|------|
| I-3 | `arrival_tolerance_deg` / `arrival_timeout_s` 未使用 | `sauce_pour_params.yaml` | 已删除 | ✅ 已解决 |
| I-4 | 采集脚本格式 | 已由 `capture_left_flange_pose.py` 替代 | ✅ 已解决 |

### 标定参数（待用户填入/确认）
| # | 参数 | 位置 | 状态 |
|---|------|------|------|
| I-5 | `robot.tool_offset` | `sauce_pour_params.yaml:14-20` | 用户自行测量后填入 |
| I-6 | `phase_b_b.tcp_target_offset` | `sauce_pour_params.yaml:71-74` | 用户后调 |
| I-7 | `phase_b_b.flange_pose_candidates` | `sauce_pour_params.yaml:75` | 用 `capture_left_flange_pose` 脚本采集后自动写入 |
| I-8 | `transform.left_calibration_file` | `sauce_pour_params.yaml:31` | 默认平移 `[0,0,-0.20]` 有效 | ✅ 已确认 |

### 集成 & 联调
| # | 问题 | 说明 |
|---|------|------|
| I-9 | **视觉集成** | plate 实时检测方案已实施，原共享 tofu 方案废弃 | ✅ 已实施 |
| I-10 | **编排器集成** | sauce_pour 已加入 tofu_workflow 第 8 步（vertical_cut 后） | ✅ 已实施 |
| I-11 | **实物联调** | 所有参数配齐后需实机逐阶段验证 |

## Problems And Resolutions

- 阶段 A 抓取后立即力矩 20 → 修正：力矩 20 在浇汁位姿才施加
- B-a 用 `move_cartesian()` 不存在 → 改为 `move_position_only()` → 后又改为 `move_to_pose_target`（flangeInBase 直接控制，消除 TCP 语义不匹配）
- B-b 用 `verify_arrival()` 不存在 → 直接 MoveJ 不验证
- 阶段 C 缺 squeeze 独立参数 → 复用 grasp/pour 参数
- `executor.connect()` 缺失 → 在 node:117 添加
- `tool_offset` 从 `arm_cfg` 读取 → 改为从 `sauce_pour_params.yaml` 读取
- SAM prompt 未发送 → 添加 `schedule_startup_prompt` 节点启动时发 "tofu" → 后又改为 sauce 节点收到 goal 后发 "plate"
- 共享 tofu 坐标锁定方案废弃 → plate 实时检测（切豆腐过程中豆腐位置变化，锁定坐标不可靠）

## Verification

- `colcon build` 编译成功（4 个包）
- 视觉集成 + 编排器集成全部通过编译

## Vision Integration Plan (I-9) — 已废弃，被 Plate Vision 方案取代

### 原方案（废弃原因）

原方案让 `tofu_prepare（first_cut）`锁定完整豆腐上表面中心到 `SHARED_TOFU_GEOMETRY_TOPIC`，sauce_pour 读取缓存。

**废弃原因**：切豆腐流程中豆腐经过多次旋转/切割，等 sauce 阶段执行时，豆腐位置已变化，共享锁定的坐标不准确。

---

## Plate Vision 方案（已实施）

### 改动逻辑

```
时序:
                                     [Sauce 阶段开始]
                                           │
            ┌──────────────────────────────┐
            │  sauce_pour_node 收到 goal    │
            │     ↓                         │
            │  VisionPromptClient           │
            │    发 SAM prompt "plate"      │
            │     ↓                         │
            │  VisionGeometryTracker        │
            │    检测 plate（盘子）OBB       │
            │     ↓                         │
            │  compute_top_surface_center   │
            │  = 4 个 top_corners 均值       │
            │    → plate_center_right       │
            │     ↓                         │
            │  right_base_point_to_left     │
            │    → plate_center_left         │
            │     ↓                         │
            │  + tcp_target_offset           │
            │    → tcp_target                │
            │     ↓                         │
            │  flange_pose_candidates IK    │
            │    → MoveJ 到浇汁位姿          │
            └──────────────────────────────┘
```

检测盘子而非豆腐的优势：
- 盘子不参与切割，位置完全固定
- 盘子是完整物体（圆/方形），OBB 检测比碎豆腐稳定
- 豆腐在盘子上 → 盘子中心 = 豆腐放置区域的中心

### 改动清单（3 个文件）

| # | 文件 | 改动 |
|---|------|------|
| P-1 | `sauce_pour_params.yaml` | 加 `perception` 段（text_prompt: "plate", class_filter: "plate"） |
| P-2 | `sauce_pour_node.py` | 加回 `VisionGeometryTracker + VisionPromptClient`（实际是 3 个文件的循环：V-5 移除它，现在加回）；移除 `SharedTofuGeometryReader` |
| P-3 | `sauce_pour_workflow.py` | `__init__` 参数 `vision_tracker` 替代 `shared_tofu_reader`；`stage_b_b_pour_pose` 实时检测 plate |

### 影响范围

- **零改动**：`tofu_prepare` / `orchestrator` / `flange_pose_candidates` / A/B-a/C/D/E 各阶段
- **保留**：`shared_tofu_geometry.py` / `topics.py`（tofu_prepare 可能复用）

## Current State

- Plate Vision 方案 P-1~P-3 已实施并编译通过
- sauce_pour B-b 消费 `VisionGeometryTracker` 实时 plate 检测结果，不再使用共享 tofu 坐标
- SharedTofuGeometryReader 已从 sauce_pour 移除
- 编排器集成不变（sauce_pour 接口不改）
- 待联调参数：`robot.tool_offset`、`flange_pose_candidates`、`tcp_target_offset`

## Next Steps

> 实机联调：填入 `robot.tool_offset` 和 `flange_pose_candidates` 后，用 `replay_only=true` 先测抓瓶+抬升，再逐步测完整流程。

