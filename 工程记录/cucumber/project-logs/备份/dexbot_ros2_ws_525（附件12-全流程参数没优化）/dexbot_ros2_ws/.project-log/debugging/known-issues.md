# Known Issues

## Active

### KI-001 — rosidl 适配器中文路径 bug

- Symptom: `rosidl_generate_interfaces` cmake 函数报错
  `list index: 1 out of range (-1, 0)`，生成的 .idl 文件不识别。
- Cause: ROS2 Humble `rosidl_adapter` 对含中文字符的 build 路径解析失败。
- Workaround: 工作空间路径必须为纯 ASCII 英文。
- Status: 已修复（迁移到 /home/tbl/Project/cucumber/）

### KI-002 — colcon 不自动发现 CutTofo 嵌套包

- Symptom: `cuttofu_vision`, `cuttofo_skill_*` 等包不在 colcon list 中。
- Cause: `src/dexbot_middle_layer/` 是一个已发现包，colcon 不递归寻找其内部嵌套包。
- Workaround: 用 `colcon build --paths src/dexbot_middle_layer/CutTofo/...` 显式指定。
- Status: 已解决（指南中已包含 --paths 步骤）

### KI-003 — 未连接硬件时启动报错

- Symptom: vision_bringup.launch.py 找不到 RealSense，xcore_controller 连接超时。
- Cause: 无实际硬件。
- Status: 预期行为，联机时自动解决。

### KI-004 — 左臂 hold press 段不执行（IK 不可达 + SDK 状态机）

- **Status**: **已定位根因，已实现预检，未完全修复运动本身**
- **Symptom**:
  - 左臂 hold 流程：第一段 MoveL 到 approach 正常到达。
  - 第二段 MoveL 到 press（80mm，纯 base Y+ 平移），SDK 返回 True 但机器人完全不动。
  - 误差持续 80mm 不变（last_err=80.0mm 20+s），press_speed=0.001 对应 50mm/s，理论上约 1.6s 应完成。
  - 第二段时间戳显示 0.17s 内返回（block=True 也类似），说明 SDK 内部 `_wait_motion_done()` 看到状态 idle 就返回，实际没启动。
- **Cause**: 尚未确定。主线怀疑：
  1. SDK `linear_move_to_pose()` 第二次调用时，`moveStart()` 或 `moveAppend()` 被内部状态机吞掉，没有真正发出命令。
  2. `_wait_motion_done()` 轮询 `operationState` 首次读到 idle 就返回成功，没有检查是否正在运动。
- **Attempted fixes**:
  1. `block=False` + 自己轮询真实 flange pose 直到到达 → 第一段有效，第二段 SDK 返回 True 但位置完全不动。
  2. 两条 MoveLCommand 一起 append + 一次 `moveStart()`（SDK 队列）→ 最终位置还是起点，队列未启动。
  3. `block=True` + 两段之间加 0.5s/1.0s sleep → 第二段 SDK 返回 True 但位置完全不动。
  4. 位置到达后加入 `_wait_motion_done()` 等待停稳 → 第一段正常，第二段 SDK 返回 `setOperateMode(automatic) 失败: 机器人运动中`（因第一段还在 motion 就发第二段，修后通过）。
  5. 当前最新：`block=True` + position 校验 + 两段间 1s settle → 第二段 SDK 返回 True 但位置完全不动。
- **Common symptom in all attempts**: 第二段 SDK `linear_move_to_pose()` 返回 True，但机器人 flange 位置完全不变，error = 80.0mm。
- **Press target**: `flange_pose6=[0.57858,0.33062,0.05602,2.90487,0.52786,-3.13704]` — 与 approach 的唯一区别是 Y 从 `0.25062` 变为 `0.33062`（+0.08m）。
- **Possible root causes (unconfirmed)**:
  1. SDK `linear_move_to_pose()` 对相同姿态、仅 Y 方向小步平移不执行（路径太短/太慢/同一姿态分段被优化掉）。
  2. SDK 底层 `moveStart()` 后，控制器认为距离太短或速度太低（`press_speed=0.001` 会被 clamp 到 50mm/s，但 SDK 内部可能不生效），直接进入 idle。
  3. xCore 控制器对 NRT 模式第二条命令的执行有状态机 bug/限制。
- **Log evidence** (last run):
  ```
  MoveL flange command: target=[0.57919,0.33062,0.05602,...] speed=0.001 dist=80.0mm timeout=60.0s
  MoveL flange waiting: actual=[0.57919,0.25062,0.05602] err=80.0mm elapsed=1.0s
  ... (20+s of same error=80.0mm)
  ```
- **Root cause confirmed (2026-05-31)**:
  - press 点在 `target_flange_quat_xyzw` 固定姿态约束下，IK 求解失败（code=-32）。
  - approach 完成后关节构型变化，再施加强制固定 quat + press 位置 = IK 不可达域。
  - SDK 返回 True 但不动，是因为内部先尝试 `move_to_pose_target`（MoveJ） 失败或忽略，fallback calcIk 也在同一问题上失败，最终没有实际下发运动指令。
  - **不是 SDK 吞命令，而是约束集（固定 pose）和当前构型不匹配**。
- **Current motion solution (基于 MoveJ 的两段方案)**:
  - 使用 `move_to_approach_with_orientation()`（MoveJ）做 approach + press 两段。
  - 两段之间加 `disconnect()` + `reconnect()` 重置 SDK session，绕过同一 session 第二条命令不执行的问题。
  - `press_speed: 0.03`（原 0.001 太慢，改为合理 MoveJ 速度）。
- **Insurance / pre-check (新增)**:
  - 在 approach 运动前，对 press 做一次 calcIk 预检（只算 IK，不运动）。
  - 预检失败时提前报错 `BIZ_CHOLD_IK_PRECHECK=3406`，输出中文可读提示（含 press 坐标、quat、SDK 错误、调整建议）。
  - 避免了先走 ~455mm approach 再空跑 fail 的情况。
- **Known limitation**: 当前 MoveJ 方案仍使用固定 `target_flange_quat_xyzw`，部分黄瓜位置 press 仍可能 IK 不可达。更稳健的方案是：
  - 恢复原始 `move_position_only` 控制链：锁当前 TCP 姿态 + 小步推进（≤8cm/step）+ 进度判定。
  - 参考备份版本 `备份/dexbot_ros2_ws_525（原始版本）/` 的 `_run_nrt_hold` + `move_position_only`。
- **Affected code files**:
  - `cuttofo_skill_common/arm/xcore_direct_executor.py`
  - `cuttofo_skill_cucumber_hold/cucumber_hold_workflow.py`
- **Affected hardware**: 左臂 xCore SDK（IP: 192.168.2.160）, `linear_move_to_pose` API
