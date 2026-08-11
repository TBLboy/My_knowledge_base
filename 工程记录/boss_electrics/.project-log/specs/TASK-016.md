# Engineering Spec — TASK-016

## Objective

为老板电器建立一条与正式 `PanPourPolicy` 隔离的固定工位临时测试路径：全程使用左臂，通过普通拖动示教录制控制器命名轨迹，再按固定阶段回放，验证拿锅、端锅、倾倒和放锅动作链路。

本任务只解决“动作链路能否快速跑通”，不引入视觉感知、底盘协同、中心坐标计算或正式 V1 的动态目标计算。

## Non-goals

- 不修改正式 `PanPourPolicy` 的业务阶段和感知路径。
- 不依赖感知组接口、`ScenePerception` 或 `WorldState.objects`。
- 不依赖底盘接口。
- 不修改 `ExecuteTask.action`、`TaskTarget.msg` 或其他公共 ROS 消息。
- 不实现锅具 TCP 反解、中心坐标系转换或跨工位泛化。
- 不把控制器命名路径误认为可迁移的相对轨迹资产。
- 不在本任务中实现抓取确认、异常自动恢复、重试和生产级取消语义。

## Related business logic

- `BL-GRASP-001`：左臂移动到固定抓取位置后闭合灵巧手。
- `BL-PLATING-001`：左臂持锅完成端锅、倾倒和放锅动作。
- `DEC-017`：临时测试路径采用左臂独立示教回放 Policy。

## Current behavior and evidence

当前代码已经具备普通拖动示教录制入口：

- `robot_motion_executor/src/dexbot_motion_executor/dexbot_motion_executor/skills/path_record.py`
- `MotionExecutorNode._initialize_skills()` 注册 `path_record`。
- `PathRecordSkill` 从 `TaskTarget.arm_type` 选择机械臂，从 `TaskTarget.object_id` 取得路径名。
- 底层 `xcore_path_client.record_path_on_robot()` 调用 `enableDrag`、`startRecordPath`、`stopRecordPath` 和 `saveRecordPath`。

当前代码也有独立控制器回放工具：

- `robot_motion_executor/src/dexbot_motion_executor/dexbot_motion_executor/utils/smoothie_path_record_replay.py`
- `replay_path()` 调用 `robot.replayPath(name, rate, ec)`、`robot.moveStart(ec)` 并轮询 `operationState()`。

但 Planner 到通用 Executor 的回放链路尚未闭合：

- `MotionPrimitiveKind` 没有正式包含 `REPLAY_RECORDED_PATH`。
- `MotionExecutorNode._execute_motion_primitive()` 没有回放分支。
- `MotionExecutorNode._initialize_skills()` 没有注册回放 Skill。
- `SmoothieDispenseSkill` 中虽构造过同名回放原语，但该字段和执行分支并不能作为当前通用能力的证据。

## Target behavior

新增独立临时任务类型：

```text
teach_pan_pour
```

新增独立策略：

```text
TeachPanPourPolicy
```

固定阶段顺序：

```text
home_open
→ move_to_grasp_ready
→ close_gripper
→ move_to_lift
→ move_to_pour_ready
→ pour_replay
→ put_replay
→ open_gripper
→ return_home
→ complete
```

其中：

- `home_open` 将左臂和灵巧手移动到固定初始关节目标；
- `move_to_grasp_ready` 将左臂移动到固定准备抓取关节目标；
- `close_gripper` 将灵巧手移动到固定闭合关节目标并设置对应力矩；
- `move_to_lift` 将左臂移动到固定抬起关节目标；
- `move_to_pour_ready` 将左臂移动到固定准备倾倒关节目标；
- `pour_replay` 读取 Skill 内置 JSON 关节轨迹并按轨迹点执行；
- `put_replay` 读取 Skill 内置 JSON 关节轨迹并按轨迹点执行；
- `open_gripper` 在 `put_replay` 成功完成后立即执行；
- `return_home` 将左臂重新移动到固定初始关节目标。

上述动作由一个独立 `TeachPanPourSkill` 承载。Skill 目录内维护资源文件：一个固定点位文件，以及倾倒和放锅两段 JSON 轨迹文件。固定点位文件同时保存机械臂关节点位、灵巧手关节点位和灵巧手力矩目标；轨迹文件保存对应的关节轨迹数据。Policy 只负责阶段推进，不直接读取资源文件或调用 Driver。Skill 根据当前阶段按需加载固定点位或轨迹文件，再通过现有 Driver 关节接口执行。

每个阶段只在前一个 `ExecuteTask` 成功回调后推进。Policy 不一次生成完整 ROS Goal 列表，而是根据自身 `_phase` 每次返回一个 `PlannedStep`。

## Affected components

### 主仓库 `kitchen_robot_home`

- `dexbot_task_planner/task_planner_node.py`
  - 注册 `teach_pan_pour` 任务类型；
  - 初始化 `TeachPanPourPolicy`；
  - 为回放步骤增加内部 Builder 路由；
  - 不改变正式 `pan_pour` 路由。
- `dexbot_task_planner/policy/teach_pan_pour/teach_pan_pour_policy.py`
  - 新增独立阶段 Policy；
  - 只产出回放步骤和 `gripper_action` 步骤；
  - 全部步骤固定 `arm_type=0`。
- `dexbot_task_planner/entities/plan.py`
  - 增加 Planner 内部的路径回放 `PlanType` 常量，不改变 ROS 消息。
- 可选：`dexbot_bringup/config/teach_pan_pour/teach_pan_pour_params.yaml`
  - 保存路径名、回放速率、超时和灵巧手动作等待参数；
  - 不把这些临时参数写入共享 `robot_params.yaml`。

### 执行仓库 `robot_motion_executor`

- `entities/motion_primitive.py`
  - 增加 `REPLAY_RECORDED_PATH` 原语及路径名、速率、超时字段。
- `skills/teach_pan_pour.py`
  - 新增独立 `TeachPanPourSkill`，按相对资源路径加载固定点位文件、倾倒轨迹文件和放锅轨迹文件；
  - 根据 `target.action_name` 选择当前阶段并构造对应关节执行原语；
  - 不依赖控制器命名路径回放，不使用 `PathReplaySkill`。

Skill 资源目录约定：

```text
skills/teach_pan_pour/
├── teach_pan_pour.py
├── teach_pan_pour_points.yaml       # 机械臂点位、手部关节和力矩
├── pour_trajectory.json             # 倾倒关节轨迹
└── put_trajectory.json              # 放锅关节轨迹
```

实际文件名可以在实现时确定，但资源必须跟随 Skill 一起维护，并通过稳定的相对路径加载；禁止依赖当前工作目录或用户机器上的临时绝对路径。
- `utils/xcore_path_client.py`
  - 提取/复用控制器回放逻辑，统一连接、准备自动模式、`replayPath`、`moveStart`、状态等待和断开流程。
- `motion_executor_node.py`
  - 注册 `teach_pan_pour` Skill；
  - 复用现有的关节运动和灵巧手执行原语/Driver 接口。

## Interfaces and schemas

不修改跨仓库公共 ROS 接口。数据承载约定如下：

```text
Planner PlannedStep
  plan_type = PLAN_TEACH_PAN_POUR
  action_name = "pour_replay"  # 当前阶段
  arm_type = 0
       ↓
ExecuteTask.Goal
  task_type = "teach_pan_pour"
  target.arm_type = 0
  target.action_name = "pour_replay"
       ↓
MotionExecutor TeachPanPourSkill
  MotionPrimitive(kind="MOVE_JOINTS"/"GRIPPER_ACTION", arm=LEFT_ARM, ...)
```

固定点位文件和两段轨迹文件必须作为 `TeachPanPourSkill` 的资源集中维护，禁止把具体数值散落在 Policy、Planner 和 Executor 多处硬编码。Skill 只在进入对应阶段时加载需要的资源，并对字段、关节数量、单位、顺序和数值范围进行校验。

## State, concurrency and lifecycle

### Planner 状态

`TeachPanPourPolicy` 至少维护：

- `_phase`：当前阶段；
- `_step_index`：当前步骤编号；
- `_steps` 或等价的当前阶段状态；
- `_last_emitted_step`：避免同一阶段重复发 Goal。

Planner 仍复用现有 `_pending_goal`、`_left_arm_busy`、`robot_status.state` 门控。每次只允许一个左臂 Goal 在途：

```text
_on_tick
  → Policy 返回当前阶段步骤
  → Builder 构造 ExecuteTask.Goal
  → _send_execute_task_goal()
  → _pending_goal=True / _left_arm_busy=True
  → 等待 _on_result()
  → policy.update_step_status(COMPLETED)
  → Policy 推进 _phase
```

### Executor 所有权

当前回放实现通过 xCore SDK 直接连接机器人控制器，而不是通过已有 `robot_driver` 服务。因此这是临时测试路径的显式运行约束：

- 回放时同一左臂必须由单一控制链路持有；
- 不能让 `robot_driver` 同时向左臂发送运动命令；
- 录制和回放前必须明确 Driver 的停止/暂停方式；
- 这条直接 xCore 回放路径不作为正式 V1 的长期架构承诺。

### 任务生命周期

- `StartTask(task_type="teach_pan_pour")` 创建独立 Policy。
- Path replay 或 gripper action 成功后才推进阶段。
- 任一 Goal 失败，任务进入现有错误结果路径，不自动重试。
- 所有固定路径成功后，Policy 返回 `COMPLETE`，Planner 清理任务上下文。
- 取消、急停和硬件保护仍由现有 Executor/Driver 机制负责；回放中途取消能力必须在真机前单独验证。

## Failure handling

本任务不增加业务级自动恢复，但必须显式失败：

- 路径名为空：Skill 构建失败；
- `arm_type != 0`：Skill 拒绝执行；
- 控制器连接失败：Action 返回失败；
- `replayPath`、`moveStart` 或 `operationState` 失败：Action 返回失败；
- 回放超时：Action 返回失败；
- Driver/xCore 并发占用：记录为环境/运行时失败，不静默判定成功。

## Security and privacy

该路径直接控制真实机械臂，不能在未知路径名或未知机械臂编号下执行。默认只允许左臂和明确配置的路径名。实现和真机验证必须保留急停、低速和人工监护条件。

## Observability

Planner 日志至少包含：

- task id；
- `_phase`；
- 路径名或 gripper action 名；
- 左臂绑定信息；
- Goal 发送、结果和失败原因。

Executor 日志至少包含：

- IP、左臂、路径名；
- replay rate 和 timeout；
- 控制器准备、开始、完成/失败阶段；
- Driver 独占约束提示。

## Compatibility, migration, rollout and rollback

- 正式 `pan_pour` 任务不受影响。
- 不修改 `ExecuteTask.action`、`TaskTarget.msg` 或已有任务类型的字段语义。
- `TeachPanPourPolicy` 和 `TeachPanPourSkill` 仅在新任务类型和新路由键下生效。
- 回滚只需移除新任务类型、Policy、Builder 分支、Skill 注册和临时参数，不需要消息迁移。
- 在真机验证前，先用假的 xCore 客户端/Mock 验证路径名、阶段顺序和失败传播。

## Verification matrix

| Case | Expected evidence |
|---|---|
| `teach_pan_pour` 启动 | 创建 `TeachPanPourPolicy`，不创建正式 `PanPourPolicy` |
| 第一阶段 | 发送 `home_open` 阶段 Goal |
| 初始位完成 | 发送 `move_to_grasp_ready` 阶段 Goal |
| 到达抓取准备位 | 发送 `close_gripper` 阶段 Goal |
| 闭手完成 | 依次发送 `move_to_lift`、`move_to_pour_ready`、`pour_replay`、`put_replay` |
| 放锅完成 | 发送 `open_gripper`，再发送 `return_home` |
| 任一阶段失败 | 不跳到下一阶段，不静默完成任务 |
| 空路径名 | Skill 在执行前拒绝 |
| 右臂请求 | Skill 拒绝 |
| 回放超时 | Action 失败并回传错误原因 |
| 正式 `pan_pour` | 现有 Policy 路由和行为不变 |
| 真机回放 | 低速、单一控制链路、人工急停条件下逐条验证 |

## Open questions and authority

以下问题不阻塞骨架设计，但阻塞完整真机闭环验收：

1. Driver 是否提供或允许增加批量关节轨迹接口；当前单点 `MoveJoints` 服务不足以支撑平滑回放。
2. 固定点位文件和 JSON 轨迹的字段格式、单位、点间时间和关节顺序。
3. 批量轨迹执行的停止/取消语义，以及 `robot_driver` 的正式安全入口。

### 轨迹平滑执行结论

当前 `MoveJoints.srv` 一次只承载一个 7 关节目标，`MotionExecutorNode` 对每个目标都发起一次 ROS Service 调用并等待 Driver 返回；用它逐点回放 20 ms 采样轨迹会产生服务往返、单点规划和停稳等待，因此会出现卡顿。

GUI 已有平滑执行证据：一次性构造全部 xCore `MoveAbsJCommand`，通过 `moveAppend` 批量下发，设置中间点 blend zone，最后一点保持精确停稳，再调用一次 `moveStart`。因此 `TeachPanPourSkill` 若要保持现有 Driver 架构，必须由 Driver 提供等价的批量关节轨迹入口；Skill 不应在 Python 层逐点调用 `MoveJoints`。

直接在 Skill 内连接 xCore 可以复用 GUI 的批量方法，但会绕过 `robot_driver`，重新引入控制连接竞争和 `.deb` 黑盒边界问题，只能作为临时实验回退，不能作为当前正式实现默认方案。

上述问题属于轨迹资产、Driver 接口和真机/执行组验证。当前规格已固定左臂、动作拆分、放锅后立即张手、资源随 Skill 管理和任务隔离边界。
