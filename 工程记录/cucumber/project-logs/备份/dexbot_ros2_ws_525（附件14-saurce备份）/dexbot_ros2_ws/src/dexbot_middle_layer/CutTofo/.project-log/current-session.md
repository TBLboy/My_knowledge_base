# Current Session

## Last Updated

- 2026-06-04 15:15 Local Time

## Current Objective

- 全部代码工作已完成（视觉集成 V-1~V-7 + 编排器集成），待标定参数填充后实机联调

## Current Business Logic Position

- Main path: A -> B -> C -> D -> E -> F -> G -> H -> I (豆腐全流程)
- Current edge: 左臂浇酱分支（新创建）
- Active branch: `sauce-pour` — 左臂浇酱技能（已实现包，未联调）

## Completed This Session

- ✓ 全部 7 项实现了多候选法兰姿态方案迁移
- ✓ 确认 `calibration_result_left.yaml` 默认平移 `[0,0,-0.20]` 符合实际双臂间距
- ✓ **视觉集成 V-1~V-7 已实施**：SHARED_TOFU_GEOMETRY_TOPIC、tofu_prepare first_cut 发布上表面中心、sauce_pour 读取共享坐标（移除 VisionGeometryTracker/SAM）
- ✓ **编排器集成已实施**：sauce_pour 作为第 8 步加入 tofu_workflow（vertical_cut 后），修改了 workflow_runner、workflow_config、tofu_orchestrator 参数、skills_bringup launch 和 package.xml
- ✓ 所有包编译通过：`cuttofo_skill_common`、`cuttofo_skill_tofu_prepare`、`cuttofo_skill_sauce_pour`、`cuttofo_orchestrator`

## 已知待办（Issue List）

### 代码层小修复
| # | 问题 | 文件 | 说明 | 状态 |
|---|------|------|------|------|
| I-1 | B-b `class_filter` 硬编码 | `sauce_pour_workflow.py` | 已移除 VisionGeometryTracker | ✅ 已解决 |
| I-2 | B-b 前未重新发 SAM prompt | `sauce_pour_node.py` | 已移除 SAM 提示 | ✅ 已解决 |
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
| I-9 | **视觉集成** | 共享 topic 模式已实施 | ✅ 已实施 |
| I-10 | **编排器集成** | sauce_pour 已加入 tofu_workflow 第 8 步（vertical_cut 后） | ✅ 已实施 |
| I-11 | **实物联调** | 所有参数配齐后需实机逐阶段验证 |

## Problems And Resolutions

- 阶段 A 抓取后立即力矩 20 → 修正：力矩 20 在浇汁位姿才施加
- B-a 用 `move_cartesian()` 不存在 → 改为 `move_position_only()`
- B-b 用 `verify_arrival()` 不存在 → 直接 MoveJ 不验证
- 阶段 C 缺 squeeze 独立参数 → 复用 grasp/pour 参数
- `executor.connect()` 缺失 → 在 node:117 添加
- `tool_offset` 从 `arm_cfg` 读取 → 改为从 `sauce_pour_params.yaml` 读取
- SAM prompt 未发送 → 添加 `schedule_startup_prompt` 节点启动时发 "tofu"

## Verification

- `colcon build` 编译成功（4 个包）
- 视觉集成 + 编排器集成全部通过编译

## Vision Integration Plan (I-9)

### 现状分析

- **编排器已存在**：`cuttofu_orchestrator/cuttofu_orchestrator/tofu_task_orchestrator.py` + `workflow_runner.py`
- **切豆腐工作流步骤**：`handle_approach → prepare(first_cut) → cut_round → ... → vertical_cut`
- **核心约束**：豆腐**完整时**（即 prepare/first_cut 之前）测量中心点最准确。切碎后（vertical_cut 后）再测量不准确。

### 选定方案：共享 topic 模式

豆腐上表面中心点由 `tofu_prepare`（first_cut profile）在第一次检测时锁定并发布到 `SHARED_TOFU_GEOMETRY_TOPIC`（TRANSIENT_LOCAL）。sauce_pour 作为后续节点，启动时读取缓存即可。

```
时间线:

[豆腐完整]                     [开始切]                     [切完]
    |                            |                            |
    ▼                            ▼                            ▼
tofu_prepare（first_cut）      cut_round × 2 → vertical_cut   sauce_pour
    ↓                                                            ↑
  发布 tofu_center ────→ SHARED_TOFU_GEOMETRY_TOPIC ────────── 读取
（OBB 中心 + 上表面修正）     （TRANSIENT_LOCAL，持久缓存）
```

**数据格式**（右臂 base 坐标系，单位 m）：
```
tofu_center_right = [x, y, z]   # z 已调整到上表面
```
即 `ObjectState.pose.position` 的 x, y，z = `position.z + OBB_z_extent / 2`。等价于 4 个 `top_corners` 的均值。

### 改动清单

| # | 文件 | 改动 |
|---|------|------|
| V-1 | `cuttofu_skill_common/perception/topics.py` | 新增 `SHARED_TOFU_GEOMETRY_TOPIC = "/cuttofu/perception/shared_tofu_geometry"` |
| V-2 | `cuttofu_skill_common/perception/shared_tofu_geometry.py` | 新建，参考 `shared_cucumber_geometry.py`，定义 `publish_shared_tofu_geometry()` + `create_shared_tofu_geometry_publisher()` |
| V-3 | `tofu_prepare_node.py` | 创建 `shared_tofu_geometry_pub`（同 cucumber_hold_node.py:119 模式） |
| V-4 | `tofu_prepare_workflow.py` | first_cut profile 检测成功后，计算上表面中心 = top_corners.mean(axis=0)，通过 shared publisher 发布 |
| V-5 | `sauce_pour_node.py` | 移除 `VisionGeometryTracker`、`VisionPromptClient`、SAM 提示；不再传入 `vision_tracker` 给 workflow |
| V-6 | `sauce_pour_workflow.py` | `__init__` 移除 `vision_tracker` 参数；`stage_b_b_pour_pose` 从共享 topic 读取 tofu_center（或由 node 直接传入），不再调用 `wait_valid()` |
| V-7 | `sauce_pour_params.yaml` | 移除 `perception` 段（class_filter, text_prompt 等） |

### 实施顺序

1. V-1 ~ V-2：基础设施（新增 topic + 发布器辅助函数）
2. V-3 ~ V-4：tofu_prepare 在 first_cut 检测时发布 tofu_center
3. V-5 ~ V-7：sauce_pour 移除视觉依赖，从共享 topic 读取

**I-1、I-2 消解**：V-5 移除了 VisionGeometryTracker 和 VisionPromptClient，I-1（class_filter 硬编码）和 I-2（SAM prompt 重发）自然消解。

## Current State

- 全部代码实现完成，4 个包均编译通过
- 视觉集成（共享 topic）+ 编排器集成已就绪
- 标定参数待用户填充（I-5 ~ I-7）
- 未实机联调

## Next Steps

> I-11 实机联调：填入标定参数后，用 `tofu_workflow_execute.launch.py` 完整跑一遍切豆腐+浇汁流程。

