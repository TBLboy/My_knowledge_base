# 正式 V1 Skill 边界（2026-08-06 用户确认，单自包含 Skill 方案）

## 结论

V1 正式版本（`pan_pour` / `PanPourPolicy`）**只使用 1 个专用 Skill**：

`PanPourSkill`（task_type=`pan_pour`，执行仓库 `skills/pan_pour/`，完全自包含）

该 Skill 覆盖完整 V1 运动链中所有“非普通笛卡尔/普通关节复用”的步骤，且不引用任何临时 teach 链路资源。

## 用户确认要点

1. 正式 V1 **不能依赖其他链路**（临时 `teach_pan_pour` / `teach_pan_pour_delta` 不会正式上传），正式 Skill 必须完全自包含。
2. 手部开/闭参数（角度/力矩）**直接使用现有测试链路的已调好值**，V1 不改数值。
3. V1 完整链路：回抓锅起始点并张手 → 抓取 → 闭手 → 提锅/准备倾倒 → 倾倒 → 放锅（固定点）→ 张手 → 回 home。

## V1 各阶段使用的能力

| 阶段 | 能力 | 类型 | 说明 |
|---|---|---|---|
| 回抓锅起始点并张手 | `pan_pour` skill `home_open` | 专用 Skill | `MOVE_JOINTS` 到 `home`（抓锅起始点）`1`，再按 `open` 预设张手 |
| 抓取 | `move_cartesian` | 复用 API | Planner 已完成 C→左臂 base 转换，发送法兰目标 |
| 闭手 | `pan_pour` skill `close_hand` | 专用 Skill | `SET_HAND_ANGLES` + `SET_HAND_TORQUES`，用 `grasp_pan` 预设 |
| 提锅到准备倾倒 | `move_cartesian` | 复用 API | 同上 |
| 倾倒接近 | `move_cartesian` | 复用 API | 同上 |
| 增量倾倒回放 | `pan_pour` skill `pour_delta_replay` | 专用 Skill | 复用既有 `LOCAL_DELTA_FLANGE_REPLAY` 原语（短生命周期 xCore 直连） |
| 放锅固定点 | `pan_pour` skill `put_fixed` | 专用 Skill | `MOVE_JOINTS` 到 `grasp_ready` preset `2` |
| 张手 | `pan_pour` skill `open_hand` | 专用 Skill | `SET_HAND_ANGLES` + `SET_HAND_TORQUES`，用 `open` 预设 |
| 回 home | `pan_pour` skill `return_home` | 专用 Skill | `MOVE_JOINTS` 到 `home` preset `1` |

## 手部逻辑（关键差异）

- 手部开合**不交给 driver 的 `gripper_action` 命名动作**，而是 Skill 直接下发角度和力矩：
  - `close_hand`：`angles=[30, 88.5, 17, 14, 15, 16]`，`torques=[100, 100, 100, 100, 100, 100]`
  - `open_hand`：`angles=[100, 100, 100, 100, 100, 100]`，`torques=[5, 5, 5, 5, 5, 5]`
- 数值来自测试版 `hand_presets.yaml`（用户已调好），复制进正式 Skill 资源目录。

## 自包含资源（正式 Skill 内）

```text
skills/pan_pour/resources/
├── resource_manifest.yaml        # 自身路径，不引用 teach 目录
├── arm_poses_left.json           # home "1" / grasp_ready "2" / lift "3" / pour_ready "4"
├── hand_presets.yaml             # open / grasp_pan 预设
└── delta_trajectories/pour_delta.json  # 103 点，字节一致副本
```

## 与旧 pan_pour_delta_replay 的关系

- 上一轮临时接入的 `pan_pour_delta_replay` Skill（只含 `pour_delta_replay`，资源软引用 teach 目录）**已删除**，由 `pan_pour` 取代。
- 正式链路不再保留 `PLAN_PAN_POUR_DELTA_REPLAY` 历史分支。

## 待定：底盘协同

- V1 流程有 `WAITING_FOR_BASE_POSITION` 阶段，底盘接口尚未就绪。
- 若底盘动作需要经 MotionExecutor 下发 → 再新增 1 个底盘相关 Skill；
- 若底盘组自行控制 → 执行器侧不新增。

## 底盘移动（两次预留位，同一接口）

- V1 底盘不区分“正/反向”：**只有一个底盘移动接口**（`update_base_positioned`），外部底盘适配器在每次底盘移动完成后上报；Policy 只等待，不主动发底盘目标，也不做反向专用逻辑。
- 底盘移动出现**两次**，均作为阶段屏障：
  1. `WAITING_FOR_BASE_POSITION`：提锅到准备倾倒后，底盘移动到倾倒工作位，再进入餐盘定位/倾倒。
  2. `WAITING_FOR_BASE_RETURN`：增量倾倒回放完成后，底盘回到原工位，才能 `put_fixed` 把锅放回灶台。
- 实现上两次等待复用同一个 `update_base_positioned` 状态位；第一次等待消费后重置为 False，保证两次移动都必须由外部底盘适配器确认完成，不伪完成。
