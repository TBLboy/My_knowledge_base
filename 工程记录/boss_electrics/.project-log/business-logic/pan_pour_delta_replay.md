# 增量倾倒回放业务逻辑（2026-08-06 用户确认）

## 目标

- 在现有临时 `teach_pan_pour` 套件之外，新建一套独立 policy + skills（任务类型建议 `teach_pan_pour_delta`）。
- 现有 `teach_pan_pour` 普通轨迹版本保持不动，作为已跑通基线保留。
- 全程左臂、固定工位、无视觉/底盘依赖，与现有临时测试路径一致。

## 与现有套件的差异

1. 倾倒阶段：
   - 由普通关节轨迹回放 `pour_replay` 改为增量法兰轨迹回放 `pour_delta_replay`。
   - 使用 GUI 采点录制的增量轨迹文件：`/home/tbl/Project/boss_electrics/倾倒增量轨迹候选/候选2带增量轨迹.json`（103 点）。
   - 文件格式为 `dexbot_gui_flange_delta_v1`，坐标语义 `flangeInBase`，单位 m/rad，RPY 顺序 xyz，左臂 `192.168.2.159`，robot_class=`xMateErProRobot`。
   - 回放顺序：先走到现有 `move_to_pour_ready` 固定点 → 读取当前法兰位姿 → 按 `T_current @ Delta_i` 展开完整法兰轨迹 → IK 求解 → 关节轨迹回放。
   - 控制方式：MotionExecutor 内创建短生命周期 xCore SDK 直连完成 IK 求解和回放，参照 GUI 增量轨迹回放模式。
2. 放锅阶段：
   - 由普通轨迹回放 `put_replay` 改为固定点 `put_fixed`。
   - 只提供 7 个关节角度，不使用轨迹文件，不新增专用速度参数；移动速度沿用固定点位速度。
   - 用户已确认：放锅点直接复用抓取点（`grasp_ready`）关节角度，即 `arm_poses_left.json` preset `2`：
     `[1.0792921044414698, 1.393539653590585, -0.9569674430410083, 0.8003420124854317, 1.133102233004513, -0.17046840874375402, 0.2663961369986807]`。
   - 实现上 `put_fixed` 运行时复用 `grasp_ready` 位姿，避免数值漂移；若后续要独立放锅点，再新增单独位姿。

## 阶段序列（沿用现有，仅替换两个阶段）

```text
home_open → move_to_grasp_ready → close_gripper → move_to_lift
→ move_to_pour_ready → pour_delta_replay → put_fixed → open_gripper → return_home
```

## 约束

- 不修改现有 `teach_pan_pour` 的 policy、skill 和资源。
- 不新增/修改公共 ROS 消息接口，沿用 `ExecuteTask` / `TaskTarget`。
- 短生命周期 SDK 连接可能与 `robot_driver` 竞争；临时测试期间同一左臂只能有一个控制链。
- 放锅关节角未提供前不做真机验证。

## 验证状态（2026-08-06 真机）

- `teach_pan_pour_delta` 全流程真机验证成功（操作员现场确认）：`move_to_pour_ready → pour_delta_replay → put_fixed → open_gripper → return_home` 完整执行，增量倾倒回放不复段重试。
- 增量回放链路（单 xCore 连接：读当前法兰位姿 → `T_current @ Delta_i` 展开 → IK 求解 → 滑动窗口关节流式回放）在目标左臂控制器（`192.168.2.159`，`xMateErProRobot`）上通过，IK 全解、未触关节限位、末点到位。
- `put_fixed` 复用 `grasp_ready` 抓取点关节角，固定点放锅真机通过。
- 证据：`EVID-TASK-016-DELTA-HW-001`（级别 3，操作员现场确认；控制器逐窗口/姿态日志未全套归档）。
- 未覆盖：急停、取消、xCore/robot_driver 控制权竞争和重复任务恢复的系统化验收。
