# 源码学习记录：TaskPlanner 主链

## 学习方法

后续讲解代码时，不能只描述抽象步骤或使用脱离源码的拟人类比。每个概念都必须落到具体代码：

1. 先指出类、方法、属性和调用位置。
2. 再解释输入、输出和状态变化。
3. 沿真实调用链说明谁调用它、它调用谁。
4. 用一个具体任务值代入，例如 `task_type="test_gripper"`、`action_name="张开"`、`arm_type=1`。
5. 区分源码事实、工程概念映射和推断，不能用示意代码替代实际代码而不标注。
6. 说明一个概念在代码中如何实现，而不仅是它“负责什么”。

推荐的解释结构是：

```text
概念 → 对应源码 → 运行时对象/变量 → 调用关系 → 具体值 → 下游效果
```

## 当前已读主链

```text
StartTask.srv
  → TaskPlannerNode._on_start_task()
  → _prepare_start_task_context()
  → _clear_runtime_state()
  → 定时器 _on_tick()
  → _generate_goal_by_task_type()
  → Policy.select_next_goal()
  → _build_gripper_action_goal()
  → ExecuteTask.Goal
  → _send_execute_task_goal()
  → MotionExecutor 的 ExecuteTask ActionServer
```

### 1. Orchestrator 在源码中的落点

`TaskPlannerNode` 可以用 Orchestrator（编排器）理解，但这个类比必须落回源码：

```text
TaskPlannerNode.__init__()
  ├─ self._active_task_id / _active_task_type / _target_class
  │    保存当前任务上下文
  ├─ self._policy
  │    保存当前任务对应的 Policy 对象实例
  ├─ self.create_timer(1.0, self._on_tick)
  │    每 1 秒触发一次调度循环
  ├─ self.create_service(..., self._on_start_task)
  │    接收外部启动任务请求
  └─ ActionClient(..., ExecuteTask, ...)
       向 MotionExecutor 发送具体执行目标
```

因此，Orchestrator 不是一个额外的类名，而是对现有 `TaskPlannerNode` 组织方式的工程概念映射：它持有上下文、驱动调度、委托策略决策、委托下游执行。

### 2. Planner 的状态、上下文和门控要分开

这些属性不应全部笼统地叫“状态机”：

| 源码对象 | 工程含义 |
|---|---|
| `self._active_task_id`、`self._active_task_type`、`self._target_class` | 当前任务上下文/元数据 |
| `self._policy` | 当前任务的策略对象 |
| `self._world.robot_status.state` | 明确的全局运行状态，如 `IDLE`、`PAUSED`、`SUCCESS`、`ERROR` |
| `self._pending_goal` | Action 是否仍在等待结果的忙标志 |
| `self._left_arm_busy`、`self._right_arm_busy` | 各机械臂是否被当前 goal 占用的并发门控标志 |
| `self._goal_epoch` | 区分当前任务和过期 Action 回调的代际标识 |

`_on_tick()` 将这些上下文、状态和忙标志组合成门控逻辑：

```text
没有 active_task_id       → 不调度
两臂都忙                  → 等待
pending_goal=True         → 等待上一个 Action 结果
SUCCESS                   → 不再调度
PAUSED                    → 不再调度
状态不是 IDLE             → 等待
全部通过                  → 向 Policy 请求下一步
```

这更准确地称为“编排器 + 显式运行状态 + 门控调度”，不是单一、纯粹的状态机实现。

### 3. 每个任务的内部步骤状态

任务级 Policy 具有自己的步骤推进状态。`TestGripperPolicy` 通过 `_cached_steps` 保存步骤列表，每个 `PlannedStep.status` 取 `PENDING`、`IN_PROGRESS`、`COMPLETED` 或 `FAILED`。

```text
select_next_goal()
  → 找到第一个仍可执行的 PlannedStep
  → 将它标记为 IN_PROGRESS
  → 返回这个 PlannedStep

MotionExecutor 返回结果
  → TaskPlanner 的结果回调调用 policy.update_step_status()
  → 将当前步骤标记为 COMPLETED 或 FAILED

所有步骤完成
  → Policy.select_next_goal() 返回 None
  → _on_tick() 将整个任务标记为 SUCCESS
```

因此可以区分两层：

```text
Planner 全局运行状态：机器人当前能否调度
Policy 步骤状态：当前任务已经执行到哪一个业务步骤
```

### 4. `ExecuteTask.Goal` 的实际含义

`ExecuteTask` 是 `dexbot_interfaces/action/ExecuteTask.action` 定义的 ROS 2 Action。`.action` 文件由三个区域组成：

```text
Goal     TaskPlanner 发给 MotionExecutor 的请求
Result   MotionExecutor 完成后返回的结果
Feedback 执行过程中的阶段和进度
```

ROS 2 根据该文件生成 Python 类型：

```python
from dexbot_interfaces.action import ExecuteTask

ExecuteTask.Goal
ExecuteTask.Result
ExecuteTask.Feedback
```

所以：

```python
goal_msg = ExecuteTask.Goal()
```

不是调用一个业务函数，而是在内存中创建一个 ROS Action Goal 消息对象，随后填充字段并交给 `ActionClient.send_goal_async()`。

当前 Goal 的核心字段是：

```text
goal_msg.task_id       当前任务编号
goal_msg.task_type     下游执行器的路由键
goal_msg.target        具体动作参数，类型为 TaskTarget
```

`task_type` 和 `target` 的职责不同：

```text
task_type = "gripper_action"
  → MotionExecutor 用它查找对应 API/Skill

target.action_name = "张开"
target.arm_type = 1
  → 被选中的 API/Skill 用这些字段确定具体动作参数
```

### 5. `_build_gripper_action_goal()` 的真实源码映射

源码位置：

`kitchen_robot_home/src/dexbot_task_planner/dexbot_task_planner/task_planner_node.py`

当前实现的关键代码是：

```python
def _build_gripper_action_goal(self, step) -> ExecuteTask.Goal:
    task_target = TaskTarget()
    task_target.arm_type = step.arm_type
    task_target.action_name = step.action_name

    goal_msg = ExecuteTask.Goal()
    goal_msg.task_id = self._active_task_id
    goal_msg.task_type = step.plan_type
    goal_msg.target = task_target

    self._current_step_index = step.step_index
    self._co_step_index = None
    return goal_msg
```

以 `TestGripperPolicy` 第一步为例：

```text
step.plan_type  = "gripper_action"
step.action_name = "张开"
step.arm_type   = 1
step.step_index = 0
```

函数执行后得到的消息关系是：

```text
ExecuteTask.Goal
├─ task_id = self._active_task_id，例如 "task_001"
├─ task_type = "gripper_action"
└─ target = TaskTarget
   ├─ arm_type = 1
   └─ action_name = "张开"
```

这里要纠正一个此前讲解中的不准确表述：当前这个函数没有给 `task_target.task_id`、`object_id` 或 `class_name` 赋值；它只给 `TaskTarget.arm_type` 和 `TaskTarget.action_name` 赋值。任务 ID 在外层 `ExecuteTask.Goal.task_id` 中设置。

### 6. 从 Goal 到执行端路由

TaskPlanner 通过 `_send_execute_task_goal()` 调用：

```python
self._execute_client.send_goal_async(goal_msg, feedback_callback=...)
```

MotionExecutor 收到 Goal 后，在 `motion_executor_node.py::_execute_task_cb()` 中读取：

```python
task_type = goal_handle.request.task_type.lower()
api_m = self._apis.get(task_type)
```

执行器初始化时注册：

```python
self._apis["gripper_action"] = GripperActionApi(constraints=constraints)
```

因此真实路由是：

```text
goal_msg.task_type = "gripper_action"
  → self._apis.get("gripper_action")
  → GripperActionApi.execute(goal)
  → MotionPrimitive
  → _execute_motion_primitive()
  → RobotDriver 服务
```

这就是“Planner 把动作交给 Worker”的代码实现，而不是只停留在拟人化描述。

## 后续讲解约定

以后解释任何模块，都按以下顺序：

1. 先给出概念在工程中的准确含义。
2. 指出它在源码中的类、方法和属性。
3. 按执行顺序逐行解释关键代码。
4. 用具体输入值追踪变量如何变化。
5. 解释返回对象如何被下游消费。
6. 最后再用 Orchestrator、Master-Worker 等类比帮助记忆，并明确类比不是源码本身。

## 用户确认的最佳讲解形式

用户明确认可“完整时间线 + 状态变量变化表 + 最后抽象思路”的方式。后续优先采用以下结构：

### 1. 先按真实运行时间串联

以一个具体任务和具体输入值为例，按照事件发生顺序说明：

```text
t=0     外部请求进入
         → 入口回调
         → 上下文创建
         → 状态初始化

t=1     定时器触发
         → 门控判断
         → Policy 返回具体步骤
         → 构建 Goal 消息
         → ActionClient 发送

t=1~N   定时器因 pending/busy/state 条件等待

t=N     下游 Action 返回
         → 结果回调清除等待状态
         → 更新 Policy 步骤状态

t=N+1   定时器再次触发
         → 获取下一个步骤，或确认任务结束
```

### 2. 再跟踪关键变量的生命周期

使用表格说明变量在不同阶段的值：

| 变量 | 初始化 | 任务启动后 | 发送 Goal 后 | 收到结果后 | 任务结束 |
|---|---|---|---|---|---|
| `_active_task_id` | `None` | 当前任务 ID | 不变 | 不变 | `None` |
| `_policy` | `None` | 当前 Policy 实例 | 不变 | 更新步骤状态 | 通常保留或由下次任务重置 |
| `_pending_goal` | `False` | `False` | `True` | `False` | `False` |
| `_left_arm_busy` / `_right_arm_busy` | `False` | 空闲 | 对应手臂为 `True` | 清除为 `False` | `False` |
| `robot_state` | `IDLE` | `IDLE` | `PREPARING_TASK`/`EXECUTING_TASK` | 回到 `IDLE` | `SUCCESS` |

重点不是只列变量名称，而是说明：哪个函数修改它、哪个条件读取它、它如何影响下一轮调度。

### 3. 最后再提炼工程思路

在源码时间线和状态表之后，再总结为：

```text
TaskPlannerNode 持有任务上下文
→ 定时器周期性调度
→ 状态和忙标志构成门控
→ Policy 产生下一步 PlannedStep
→ Planner 将其翻译成 ExecuteTask.Goal
→ ActionClient 发送给 MotionExecutor
→ 结果回调清除等待状态并更新步骤
→ 下一次定时器继续推进
```

抽象概念（如 Orchestrator、Master-Worker、状态机）必须放在具体源码链之后，作为记忆压缩，不能代替源码分析。


---

## 完整调用链串讲：从 `__init__` 到结果回调

### 阶段 0：节点初始化 (`__init__`)

节点启动时，`TaskPlannerNode.__init__()` 在内存中创建了这些东西：

```python
# task_planner_node.py, line ~56

self._world = WorldState()                      # 世界模型：objects, robot_status, 左右臂状态

self._active_task_id = None                     # 任务上下文
self._active_task_type = "None"
self._target_class = "None"

self._scene_sub = create_subscription(          # 订阅 /perception/scene
    ScenePerception, "perception/scene", self._on_scene, 10)

self._start_task_srv = create_service(          # 提供 StartTask 服务
    StartTask, "task_planner/start_task", self._on_start_task)

self._execute_client = ActionClient(            # 连接 MotionExecutor 的 ActionServer
    self, ExecuteTask, "motion_executor/execute_task")

self._tick_timer = self.create_timer(1.0, self._on_tick)  # 1秒定时器驱动

self._pending_goal = False                      # Action 忙标志
self._policy = None                             # 策略对象（任务启动后才创建）
self._goal_epoch = 0                            # 代际计数器
self._left_arm_busy = False                     # 双臂忙标志
self._right_arm_busy = False
```

到这里节点只是**等待**。没有 active task，没有 policy，没有 pending goal。

---

### 阶段 1：外部通过 `StartTask` 服务启动任务

外部调用 `StartTask.srv`，request 的字段大致是：

```python
request.task_type = "test_gripper"   # 任务类型
request.target_class = ""            # 目标类别
request.resume = False               # 是否恢复
```

进入 `_on_start_task()`，第 380 行：

```
第1步：验证 task_type
  valid_task_types = ["test_heart", "cube", ..., "test_gripper", ...]
  "test_gripper" ∈ valid_task_types → 通过

第2步：如果 PAUSED 且非 resume → 拒绝
  self._world.robot_status.state == RobotState.PAUSED → 不成立，通过

第3步：调用 _prepare_start_task_context()
```

进入到 `_prepare_start_task_context()`，第 215 行。因为 `resume=False`，走 new task 分支：

```python
task_id = self._generate_task_id()           # → 例如 "a1b2c3d4-..."
self._active_task_id = task_id               # 保存上下文
self._active_task_type = "test_gripper"
self._target_class = ""
self._initialize_policy("test_gripper")      # → 创建 Policy
self._resume_restart_requested = False
return task_id
```

进去看 `_initialize_policy("test_gripper")`，第 161 行：

```python
if task_type == "test_gripper":
    self._policy = TestGripperPolicy(max_loop=3)   # ← 创建！
if self._policy is not None:
    self._policy.clear()                           # 清空内部 _cached_steps
```

`TestGripperPolicy.__init__()` 做的事情：
- 保存 `self._max_loop = 3`
- `self._cached_steps = None`（预生成步骤列表为空）

回到 `_on_start_task()`，第 438 行：

```python
self._clear_runtime_state()    # 清空运行标志
self._update_robot_state(RobotState.IDLE)   # 状态设为 IDLE
self._set_task_phase("task_started", progress=0.0, last_error="")
self._goal_epoch += 1          # epoch 从 0 → 1

response.accepted = True
response.message = f"Task {task_id} started."
```

看 `_clear_runtime_state()`，第 97 行：

```python
if self._policy is not None:
    self._policy.clear()           # 又清了一遍 cached_steps
self._active_goal_handle = None
self._pending_goal = False         # ← False
self._left_arm_busy = False        # ← False
self._right_arm_busy = False       # ← False
self._current_step_index = None
self._co_step_index = None
self._current_step_retry_count = 0
self._arm_retry_counts = {"left": 0, "right": 0}
self._active_goal_task_type = ""
self._active_goal_execution_mode = 0
```

`_clear_runtime_state()` 的**特征**：只清空运行时标志，**不**清空 `_active_task_id`、`_active_task_type`、`_target_class` 和 `_policy`——这些属于"任务上下文"，不属于"运行时状态"。

StartTask 结束后的属性状态：

| 属性 | 值 |
|---|---|
| `_active_task_id` | `"a1b2c3d4-..."` |
| `_active_task_type` | `"test_gripper"` |
| `_policy` | `TestGripperPolicy(max_loop=3)` |
| `_policy._cached_steps` | `None` |
| `_pending_goal` | `False` |
| `_left_arm_busy` | `False` |
| `_right_arm_busy` | `False` |
| `_world.robot_status.state` | `RobotState.IDLE` |
| `_goal_epoch` | `1` |

---

### 阶段 2：定时器触发 → `_on_tick()` → 门控

节点主线程在 `rclpy.spin(node)` 里跑。1 秒后，`_tick_timer` 触发，进入 `_on_tick()`，第 455 行。

门控链条：

```python
# 门 0: 没有 active task → 直接 return
if self._active_task_id is None:    # "a1b2c3-..." ≠ None → 通过
    return

# 门 1: 双臂都忙 → return 等待
if self._left_arm_busy and self._right_arm_busy:
    # False and False = False → 通过
    return

# 门 2: _pending_goal 阻塞
if self._pending_goal:              # False → 通过
    return

# 门 3: SUCCESS 状态
if self._world.robot_status.state == RobotState.SUCCESS:  # 通过
    return

# 门 4: PAUSED 状态
if self._world.robot_status.state == RobotState.PAUSED:   # 通过
    return

# 门 5: 不是 IDLE
if self._world.robot_status.state != RobotState.IDLE:     # 通过
    return

# → 全部门控通过 → 进入 _generate_goal_by_task_type()
```

---

### 阶段 3：`_generate_goal_by_task_type()` → Policy 生成步骤

第 492 行：

```python
goal = self._policy.select_next_goal(
    task_id=self._active_task_id,        # "a1b2c3-..."
    task_type=self._active_task_type,     # "test_gripper"
    target_class=self._target_class,      # ""
)
```

**Planner 把决策权委托给了 Policy。**

进入 `TestGripperPolicy.select_next_goal()`。

第一次调用时 `_cached_steps is None`，先调用 `_create_steps()`：

```python
def _create_steps(self) -> List[PlannedStep]:
    steps = []
    for loop_index in range(3):           # max_loop=3
        for action_name in ["张开", "扎取"]:
            step = PlannedStep(
                plan_type=PlanType.PLAN_GRIPPER_ACTION,  # "gripper_action"
                step_index=len(steps),   # 0, 1, 2, 3, 4, 5
                fruit_id="",
                pattern_index=0,
                arm_type=1,              # 右臂
                action_name=action_name, # "张开" / "扎取"
                status=StepStatus.PENDING,
            )
            steps.append(step)
    return steps
```

生成了 6 个 `PlannedStep`：

| step_index | plan_type | action_name | arm_type | status |
|---|---|---|---|---|
| 0 | gripper_action | 张开 | 1 | PENDING |
| 1 | gripper_action | 扎取 | 1 | PENDING |
| 2 | gripper_action | 张开 | 1 | PENDING |
| 3 | gripper_action | 扎取 | 1 | PENDING |
| 4 | gripper_action | 张开 | 1 | PENDING |
| 5 | gripper_action | 扎取 | 1 | PENDING |

然后 `select_next_goal()` 遍历 `_cached_steps`：

```python
for step in self._cached_steps:
    if step.status in (StepStatus.PENDING, StepStatus.FAILED, StepStatus.IN_PROGRESS):
        if step.status != StepStatus.IN_PROGRESS:
            step.status = StepStatus.IN_PROGRESS    # 标记为"正在执行"
        return step                                  # 返回第 0 步
```

找到 step_index=0, action_name="张开"，标记为 `IN_PROGRESS`，返回。

---

### 阶段 4：路由到 `_build_gripper_action_goal()`

回到 `_generate_goal_by_task_type()`，第 510 行：

```python
if goal.plan_type == PlanType.PLAN_GRIPPER_ACTION:
    goal_msg = self._build_gripper_action_goal(goal)
```

进入 `_build_gripper_action_goal(step)`，第 640 行：

```python
task_target = TaskTarget()
task_target.arm_type = step.arm_type         # 1（右臂）
task_target.action_name = step.action_name   # "张开"

goal_msg = ExecuteTask.Goal()
goal_msg.task_id = self._active_task_id      # "a1b2c3-..."
goal_msg.task_type = step.plan_type          # "gripper_action"
goal_msg.target = task_target

self._current_step_index = step.step_index    # 0
self._co_step_index = None
return goal_msg
```

生成的 `ExecuteTask.Goal` 消息对象：

```python
ExecuteTask.Goal(
    task_id="a1b2c3-...",
    task_type="gripper_action",
    target=TaskTarget(
        arm_type=1,
        action_name="张开"
    )
)
```

回到 `_on_tick()`（第 486 行）：

```python
self._send_execute_task_goal(goal_msg)
```

---

### 阶段 5：`_send_execute_task_goal()` → 发送 + 注册回调

第 ~757 行 `_send_execute_task_goal()`：

```python
# 等待 ActionServer 就绪
self._execute_client.wait_for_server(timeout_sec=1.0)

# 更新机器人状态
self._update_robot_state(RobotState.PREPARING_TASK)

# 记录当前 goal 的任务类型和执行模式
self._active_goal_task_type = "gripper_action"
self._active_goal_execution_mode = 0

# 设置 pending 标志
self._pending_goal = True                     # ← 变 True，阻塞后续 tick

# resume 标志传递
goal_msg.resume_restart = False
self._resume_restart_requested = False

# 设置双臂忙标志
# goal_msg.execution_mode == 0 → 单臂
# target.arm_type == 1 → 右臂
self._right_arm_busy = True                   # ← 变 True

# 记录发送时间
self._goal_send_time = time.perf_counter()
```

最关键的部分——**使用闭包注册回调**：

```python
send_future = self._execute_client.send_goal_async(
    goal_msg,
    feedback_callback=_on_feedback
)
self._active_goal_handle = None
send_future.add_done_callback(
    lambda goal_future: self._on_goal_response(goal_future, _on_result, goal_epoch)
)
```

`_on_result` 是一个**闭包函数**（定义在 `_send_execute_task_goal` 内部），捕获了 `goal_epoch`、`goal_msg` 等局部变量。

---

### 阶段 6：`_on_goal_response()` → 确认 Goal Handle

MotionExecutor 的 ActionServer 收到 Goal 后，返回 `goal_handle`。

`_on_goal_response()` 第 800 行：

```python
# epoch 校验：epoch 变了就抛弃
if expected_epoch != self._goal_epoch:    # 1 == 1 → 通过
    ...
    return

# 保存 goal handle（供后续 cancel）
self._active_goal_handle = goal_handle

# 注册真正的 result 回调
goal_handle.get_result_async().add_done_callback(_on_result)
```

---

### 阶段 7：等待 → 定时器空转

MotionExecutor 执行 "张开右臂" 期间（假设 2.5 秒），`_on_tick` 每秒触发一次：

```
t=2: _pending_goal=True  → 门 2 阻塞，return
t=3: _pending_goal=True  → 门 2 阻塞，return
t=3.5: MotionExecutor 执行完毕，触发 _on_result 回调
```

---

### 阶段 8：`_on_result()` 闭包 → 结果处理

`_on_result(fut)`，第 ~790 行：

```python
# epoch 校验
if goal_epoch != self._goal_epoch:   # 1 == 1 → 通过
    return

# 清除等待标志
self._pending_goal = False           # ← 变 False
self._active_goal_handle = None
self._left_arm_busy = False
self._right_arm_busy = False         # ← 变 False

result = fut.result().result

# result.success == True → 单臂成功
self._update_robot_state(RobotState.IDLE)   # 状态回到 IDLE
self._policy.update_step_status(
    step_index=self._current_step_index,    # 0
    status=StepStatus.COMPLETED,            # 标记为 "completed"
)
self._current_step_retry_count = 0
```

`update_step_status(step_index=0, status="completed")` 去 `TestGripperPolicy.update_step_status()`：

```python
for step in self._cached_steps:
    if step.step_index == 0:                # 找到第 0 步
        step.status = "completed"           # 更新状态
        return True
```

步骤状态变化：

| step_index | action_name | 之前 | 之后 |
|---|---|---|---|
| 0 | 张开 | IN_PROGRESS | COMPLETED |
| 1 | 扎取 | PENDING | PENDING |
| 2 | 张开 | PENDING | PENDING |
| ... | ... | ... | ... |

下一次 tick → 门控通过 → `select_next_goal()` 找到 step_index=1（第一个 PENDING 的 "扎取"）→ 标记 IN_PROGRESS → 构建 Goal → 发送 → 循环。

重复 6 次，所有步骤变为 COMPLETED。

---

### 阶段 9：任务结束

第 6 步完成后，下一次 `_on_tick`：

```python
goal_msg = self._generate_goal_by_task_type()
# Policy.select_next_goal() → 所有步骤都不是 PENDING/FAILED/IN_PROGRESS → return None

if goal_msg is None:     # ← True
    self._update_robot_state(RobotState.SUCCESS)
    self._set_task_phase("task_completed", progress=1.0)
    self._active_goal_task_type = ""
    self._active_goal_execution_mode = 0
    self._active_task_id = None              # ← 清空任务上下文

    # 下一次 tick 门 0 不通过 → 不再调度
    return
```

`_active_task_id = None` 之后，所有后续 tick 在第一道门 `if self._active_task_id is None: return` 截断。

---

## 关键变量生命周期总表

| 变量 | __init__之后 | StartTask之后 | tick→发送goal后 | 收到结果后 | 所有步骤完成后 |
|---|---|---|---|---|---|
| `_active_task_id` | `None` | `"a1b2-..."` | 不变 | 不变 | `None` |
| `_active_task_type` | `"None"` | `"test_gripper"` | 不变 | 不变 | 不变 |
| `_policy` | `None` | `TestGripperPolicy` | 不变 | 不变 | 不变(不清除) |
| `_policy._cached_steps` | `None` | `None`(clear后) | 6个PlannedStep | 第0步→COMPLETED | 全部COMPLETED |
| `_pending_goal` | `False` | `False` | `True` | `False` | `False` |
| `_left_arm_busy` | `False` | `False` | `False` | `False` | `False` |
| `_right_arm_busy` | `False` | `False` | `True` | `False` | `False` |
| `robot_state` | `IDLE` | `IDLE` | `PREPARING_TASK` → `EXECUTING_TASK` | `IDLE` | `SUCCESS` |
| `_current_step_index` | `None` | `None`(clear后) | 当前step_index(0,1,2...) | 不变 | 最后一步index |
| `_goal_epoch` | `0` | `1` | 不变 | 不变 | 不变 |
| `_active_goal_handle` | `None` | `None` | ActionClient返回的handle | `None`(clear) | `None` |

---

## 工程思路总结

**一个 `TaskPlannerNode` 节点内部，四个层面的属性协作：**

1. **上下文层**（`_active_task_id`， `_active_task_type`， `_target_class`， `_policy`）
   - 保存"当前在做什么任务"
   - `_on_start_task` 设置，`_policy.select_next_goal()` 返回 `None` 时清除
   - 跨 tick 持久化

2. **运行状态层**（`_world.robot_status.state`）
   - `IDLE` / `PREPARING_TASK` / `EXECUTING_TASK` / `PAUSED` / `SUCCESS` / `ERROR`
   - 各函数在不同时机修改这个状态

3. **门控标志层**（`_pending_goal`， `_left_arm_busy`， `_right_arm_busy`）
   - `_pending_goal`：单臂模式下防止重复发送
   - `_left_arm_busy` / `_right_arm_busy`：双臂模式下各臂并发控制
   - `_send_execute_task_goal` 设置，`_on_result` 清除

4. **代际保护层**（`_goal_epoch`）
   - 每次 `_on_start_task` 或 `_on_pause_task` 时 `+= 1`
   - 闭包 `_on_result` 和 `_on_goal_response` 中校验 epoch
   - 防止过期回调错误地修改当前状态

**调度循环**：

```
create_timer(1.0， _on_tick)
  → 门控判断（上下文/状态/忙标志）
  → policy.select_next_goal()       委托决策
  → _build_*_goal()                翻译成 ExecuteTask.Goal
  → ActionClient.send_goal_async()  发送给 MotionExecutor
  → MotionExecutor 执行期间 tick 被 pending_goal 阻塞
  → _on_result 回调清除标志 + 更新 policy 步骤状态
  → 下一次 tick 继续
```

**Policy 的职责分界**：

```
TestGripperPolicy.select_next_goal():
  输入: task_id， task_type， target_class（当前任务上下文）
  输出: Optional[PlannedStep]           （下一步要做什么）
  副作用: 修改 step.status (PENDING → IN_PROGRESS)

Policy.update_step_status():
  输入: step_index， status， failure_reason
  副作用: 修改指定 step 的状态 (COMPLETED / FAILED)

Policy.clear():
  输入: 无
  副作用: 清空 _cached_steps（重启时重新生成）
```

---

## 源码路径索引

核心节点：
- `kitchen_robot_home/src/dexbot_task_planner/dexbot_task_planner/task_planner_node.py`
  - `__init__` ~line 56
  - `_initialize_policy` ~line 161
  - `_clear_runtime_state` ~line 97
  - `_prepare_start_task_context` ~line 215
  - `_on_start_task` ~line 380
  - `_on_tick` ~line 455
  - `_generate_goal_by_task_type` ~line 492
  - `_build_gripper_action_goal` ~line 640
  - `_send_execute_task_goal` ~line 757
  - `_on_goal_response` ~line 800
  - `_on_result` 闭包 ~line 790 (inside `_send_execute_task_goal`)
  - `_on_scene` ~line 260

实体类型：
- `kitchen_robot_home/src/dexbot_task_planner/dexbot_task_planner/entities/plan.py`
  - `PlanType`、`StepStatus`、`PlannedStep`、`BimanualStep`、`TaskPlan`
- `kitchen_robot_home/src/dexbot_task_planner/dexbot_task_planner/entities/scene_state.py`
  - `RobotState`、`RobotStatus`、`WorldObject`、`WorldState`

Policy 示例：
- `kitchen_robot_home/src/dexbot_task_planner/dexbot_task_planner/policy/base_policy.py`
  - `BasePolicy` 抽象类
- `kitchen_robot_home/src/dexbot_task_planner/dexbot_task_planner/policy/test_gripper_policy.py`
  - `TestGripperPolicy` 完整实现
