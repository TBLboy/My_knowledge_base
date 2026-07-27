# dexbot_ros2_ws 架构深度拆解与学习指南

> **分析对象**：`dexbot_ros2_ws-dev_715_cut_cucumbers`  
> **目标分支语义**：切黄瓜任务开发分支 `715_cut_cucumbers`  
> **分析方式**：源码静态审查、接口定义核对、启动文件核对、运行日志追踪、Python 语法级检查  
> **环境基线**：Ubuntu 22.04、ROS 2 Humble、Python 3.10  
> **结论适用范围**：本压缩包所包含的代码快照；不代表其他分支或后续版本  
> **验证边界**：已完成 `python3 -m compileall -q src`，结果通过；未在真实 ROS 2、厂商 SDK、相机和双臂硬件环境中执行 `colcon build` 或真机验证

---

## 目录

1. [结论摘要](#1-结论摘要)
2. [分析方法与阅读边界](#2-分析方法与阅读边界)
3. [系统总体架构](#3-系统总体架构)
4. [实际启动拓扑](#4-实际启动拓扑)
5. [ROS 2 接口总表](#5-ros-2-接口总表)
6. [核心数据结构与逐层转换](#6-核心数据结构与逐层转换)
7. [模块一：dexbot_interfaces](#7-模块一dexbot_interfaces)
8. [模块二：dexbot_camera_driver](#8-模块二dexbot_camera_driver)
9. [模块三：dexbot_perception](#9-模块三dexbot_perception)
10. [模块四：dexbot_task_planner](#10-模块四dexbot_task_planner)
11. [模块五：dexbot_motion_executor](#11-模块五dexbot_motion_executor)
12. [模块六：dexbot_robot_driver](#12-模块六dexbot_robot_driver)
13. [模块七：dexbot_safety](#13-模块七dexbot_safety)
14. [模块八：dexbot_watchdog](#14-模块八dexbot_watchdog)
15. [模块九：dexbot_web_api](#15-模块九dexbot_web_api)
16. [模块十：dexbot_vla](#16-模块十dexbot_vla)
17. [模块十一：dexbot_harness_api](#17-模块十一dexbot_harness_api)
18. [模块十二：bringup、utils 与 toolbox](#18-模块十二bringuputils-与-toolbox)
19. [核心设计模式深度分析](#19-核心设计模式深度分析)
20. [“切黄瓜”任务完整调用链](#20-切黄瓜任务完整调用链)
21. [切黄瓜分支的源码级问题](#21-切黄瓜分支的源码级问题)
22. [整体架构优点](#22-整体架构优点)
23. [整体架构薄弱点](#23-整体架构薄弱点)
24. [在其他项目中复用这套架构](#24-在其他项目中复用这套架构)
25. [推荐改造路线](#25-推荐改造路线)
26. [推荐学习顺序与练习](#26-推荐学习顺序与练习)
27. [需进一步确认的事项](#27-需进一步确认的事项)
28. [关键文件索引](#28-关键文件索引)
29. [最终评价](#29-最终评价)

---

# 1. 结论摘要

## 1.1 这套架构本质上是什么

`dexbot_ros2_ws` 不是一个单纯的机械臂驱动项目，也不是一个单纯的视觉识别项目，而是一套面向双臂操作任务的分层机器人应用框架。其主链路可以概括为：

```text
感知结果
  ↓
共享世界状态 WorldState
  ↓
任务策略 Policy
  ↓
任务步骤 PlannedStep
  ↓
ROS Action: ExecuteTask.Goal
  ↓
技能/API
  ↓
运动中间表示 MotionPrimitive
  ↓
RobotDriver ROS Service
  ↓
机器人抽象接口 / 复合机器人
  ↓
厂商 SDK
  ↓
真实机械臂与灵巧手
```

其中最关键、最值得复用的设计不是某个具体的切黄瓜算法，而是两个中间层：

1. **任务级中间表示 `PlannedStep`**
2. **运动级中间表示 `MotionPrimitive`**

这两个中间表示把“任务语义”“运动技能”和“硬件命令”分开，使任务开发者通常不需要直接操作厂商 SDK。

---

## 1.2 架构的主要优点

1. **任务层与硬件层基本解耦**  
   TaskPlanner 不直接调用络石、XCore 或 LinkerBot SDK，而是通过 `ExecuteTask` 和 RobotDriver 服务间接执行。

2. **新任务有明确扩展位置**  
   新任务优先在 `dexbot_task_planner/policy/<task_name>/` 中实现，总策略负责编排，子策略负责动作序列。

3. **运动原语提供了统一执行语义**  
   笛卡尔运动、关节运动、夹爪动作、实时阻抗、拖动与停止都可以统一表达为 `MotionPrimitive`。

4. **硬件组合可配置**  
   RobotFactory 配合 Arm/Hand/Robot 抽象接口，可以组合不同机械臂和灵巧手。

5. **感知任务适配器思路正确**  
   通用感知发布 `ScenePerception`，切黄瓜专用节点再将其压缩为 `CucumberShape`，避免把任务细节全部塞进通用感知节点。

---

## 1.3 当前最重要的问题

### 已由源码直接确认的问题

1. “斜切”配置被测试代码强制覆盖为“正切”配置。
2. 感知黄瓜长度的更新函数因赋值顺序错误而永远提前返回。
3. 右臂支撑位置的轮次累计偏移少乘了 `cut_step_mm`。
4. 右臂启用实时阻抗时默认仍使用左臂刚度和期望力参数。
5. 翻转后点云验证仍是占位实现。
6. `CheckPick` 当前是固定延时后直接返回成功，不是真实抓取验证。
7. 安全层只有 FakeSafetyCheck，且默认相机命名空间与当前实际启动相机不一致。
8. Watchdog 中存在硬编码特权凭据，属于严重安全问题。
9. 启动文件中“延迟启动运动执行器”的对象被定义但没有使用，实际是立即启动。
10. Web、MCP、VLA、TaskPlanner 存在多条可直接进入执行层的路径，但没有全局唯一的运动仲裁器。

### 已由运行日志直接确认的问题

切黄瓜执行到右臂翻转阶段时，策略生成了如下目标位姿：

```text
x ≈ 0.4404
y ≈ -0.3696
z ≈ -0.3981
```

随后 RobotDriver 报告：

```text
No feasible joint solution was found in the requested elbow range
```

任务在重试后失败。可以确认的是：

- 失败点是右臂翻转初始笛卡尔目标不可达；
- 目标 `z` 值高度可疑；
- 很可能与黄瓜端点计算、坐标系、局部轴约定或标定变换有关。

但仅凭静态源码和日志，**不能唯一断言具体是哪一个坐标变换步骤出错**，仍需通过 TF、原始感知消息和标定矩阵现场核对。

---

# 2. 分析方法与阅读边界

## 2.1 本次检查内容

本次分析覆盖：

- 工作区目录结构；
- `SKILL.md` 中的开发边界；
- `dexrob_full.launch.py` 的真实启动内容；
- ROS 2 的 msg、srv、action 定义；
- TaskPlanner 的状态机、Policy 注册和目标构造；
- MotionExecutor 的技能、API、控制器和运动原语；
- RobotDriver 的接口、工厂、复合机器人和安全入口；
- Perception 的流水线与黄瓜形状适配；
- Safety、Watchdog、Web API、VLA、Harness API；
- 切黄瓜策略全部主要文件；
- 随压缩包提供的运行日志；
- Python 语法级编译检查。

## 2.2 未完成的验证

以下内容未在本环境中完成：

- ROS 2 依赖解析；
- `colcon build`；
- launch 实际启动；
- DDS QoS 互操作验证；
- 相机图像和点云检查；
- TF 树检查；
- 厂商 SDK 联机；
- 真机 IK、实时阻抗与灵巧手动作验证；
- VLA 模型权重加载和真实推理；
- Web 前端联调。

因此，本文将结论分为：

- **源码确认**：可由当前代码直接证明；
- **日志确认**：可由随包日志证明；
- **风险推断**：基于代码结构做出的工程判断；
- **需进一步确认**：必须依赖运行环境或硬件验证。

---

# 3. 系统总体架构

## 3.1 主任务链

```text
┌─────────────────────────────────────────────────────────────┐
│ 外部入口                                                    │
│ Web API / ROS Service / MCP / VLA Action                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 任务规划层 dexbot_task_planner                              │
│ WorldState + Policy + PlannedStep + 任务状态机              │
└───────────────────────────┬─────────────────────────────────┘
                            │ ExecuteTask Action
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 运动执行层 dexbot_motion_executor                           │
│ Skill / API / Controller → MotionPrimitive                  │
└───────────────────────────┬─────────────────────────────────┘
                            │ ROS Service
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 硬件抽象层 dexbot_robot_driver                              │
│ RobotFactory + RobotInterface + Composite Robot             │
└───────────────────────────┬─────────────────────────────────┘
                            │ Python/C/C++ SDK
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 机械臂控制器、CAN 灵巧手、真实硬件                          │
└─────────────────────────────────────────────────────────────┘
```

## 3.2 感知链

```text
RGB / Depth / CameraInfo
        │
        ▼
dexbot_camera_driver
        │ ROS topics
        ▼
dexbot_perception
        │
        ├── 通用场景：ScenePerception
        │       └── TaskPlanner / MotionExecutor / Web API
        │
        └── 任务适配：CucumberShapeNode
                └── CucumberShape
                        └── TaskPlanner.WorldState
```

## 3.3 安全与监控链

```text
相机深度帧
   │
   ▼
dexbot_safety
   │ StopPolicy(HARD_STOP)
   ▼
RobotDriver
   │
   └── 统一执行真实硬件停止

SafetyHeartbeat ───────────────► RobotDriver
                                 当前仅告警，不触发自动停止

ROS graph / CAN status
   │
   ▼
dexbot_watchdog
   ├── 节点存在性监控
   └── CAN 接口恢复（默认关闭）
```

## 3.4 实际存在的旁路

项目不是只有一条严格的“Web → Planner → Executor → Driver”链。实际还有：

```text
Web API ───────────────► MotionExecutor
Web API ───────────────► RobotDriver.gripper_action
Harness MCP ───────────► MotionExecutor
VLA ───────────────────► RobotDriver
VLA 的夹爪动作 ────────► Harness MCP ─► MotionExecutor
```

这意味着系统当前是：

> **分层主链 + 多个直接执行旁路**

这种设计方便调试和快速接入，但如果没有全局运动仲裁，会产生并发目标冲突风险。

---

# 4. 实际启动拓扑

主启动文件：

```text
src/dexbot_bringup/launch/dexrob_full.launch.py
```

## 4.1 当前实际启用

```text
立即启动：
1. /camera1/camera_driver
2. perception_node
3. cucumber_shape_node
4. camera_viewer_node
5. web_api_node
6. motion_executor_node
7. task_planner_node
8. /watchdog/watchdog_node

延迟 2 秒：
9. safety_layer_node

延迟 4 秒：
10. robot_driver_node
```

## 4.2 当前被注释禁用

```text
- camera2 driver
- camera2 viewer
- harness_api_node
- vla_node
```

## 4.3 启动文件中的不一致

### 不一致一：运动执行器延迟对象未被使用

代码创建了：

```text
delayed_robot_executor_node = TimerAction(period=3.0, ...)
```

但 `LaunchDescription` 实际加入的是：

```text
robot_executor_node
```

因此 MotionExecutor 实际立即启动。

### 不一致二：安全注释仍假定 camera2

启动文件注释写的是：

```text
camera2 → safety_layer → robot_driver
```

但 `camera2` 已被注释掉，安全配置默认又订阅 `camera`，而实际相机是 `camera1`。

### 不一致三：固定延时不等于“依赖已就绪”

即使 Safety 延迟 2 秒、Driver 延迟 4 秒，也不能证明：

- 相机已经有帧；
- 感知模型已经完成 warmup；
- 安全层已经收到深度图；
- 机器人控制器已经建立 TCP 连接。

更合适的方式是生命周期节点、ready service 或健康状态门控。

---

# 5. ROS 2 接口总表

## 5.1 Topic

| Topic | 发布者 | 订阅者 | 作用 |
|---|---|---|---|
| `/camera1/color/image_raw` | camera_driver | perception、viewer、VLA（启用时） | RGB 图像 |
| `/camera1/depth/image_raw` | camera_driver | perception、viewer、VLA、安全层（配置正确时） | 深度图 |
| `/camera1/color/camera_info` | camera_driver | perception、viewer | 相机内参 |
| `perception/scene` | perception | TaskPlanner、MotionExecutor、Web API、CucumberShapeNode | 通用场景感知 |
| `/perception/cucumber_shape` | CucumberShapeNode | TaskPlanner | 黄瓜长度、宽度和右端点 |
| `task_planner/status` | TaskPlanner | Web API | 高层任务状态 |
| `/robot_driver/stop_policy` | Safety、MotionExecutor | RobotDriver | 统一安全停止策略 |
| `/robot_driver/safety_heartbeat` | Safety | RobotDriver | 安全节点在线心跳 |

注意：项目同时使用绝对名与相对名，例如：

```text
perception/scene
/perception/cucumber_shape
robot_driver/gripper_action
/robot_driver/move_cartesian
```

这会让 namespace 重用和多机器人部署更困难。

## 5.2 Service

| Service | 服务端 | 客户端 | 作用 |
|---|---|---|---|
| `/task_planner/start_task` | TaskPlanner | Web、CLI | 启动或恢复高层任务 |
| `/task_planner/pause_task` | TaskPlanner | Web | 暂停任务 |
| `/task_planner/check_pick` | TaskPlanner | MotionExecutor | 抓取检查，当前为占位 |
| `/robot_driver/move_cartesian` | RobotDriver | MotionExecutor、VLA | 普通笛卡尔运动 |
| `/robot_driver/move_linear_cartesian` | RobotDriver | MotionExecutor、VLA | 直线笛卡尔运动 |
| `/robot_driver/move_joints` | RobotDriver | MotionExecutor、VLA | 关节运动 |
| `/robot_driver/gripper_action` | RobotDriver | MotionExecutor、Web | 夹爪预定义动作 |
| `/robot_driver/get_arm_pose` | RobotDriver | Web | 查询机械臂位姿 |
| `/robot_driver/enable_drag` | RobotDriver | MotionExecutor、Web | 拖动模式 |
| `/robot_driver/is_drag_mode` | RobotDriver | 外部客户端 | 查询拖动状态 |
| `/robot_driver/stop_motion` | RobotDriver | Planner、Executor | 停止机械臂 |
| `/robot_driver/realtime/cartesian_impedance/enable` | RobotDriver | MotionExecutor | 开关实时阻抗 |
| `/robot_driver/realtime/cartesian_impedance/set_stiffness` | RobotDriver | MotionExecutor | 设置阻抗参数 |
| `/robot_driver/realtime/cartesian_impedance/move_offset` | RobotDriver | MotionExecutor | 实时阻抗偏移运动 |
| `/robot_driver/hand/get_angles` | RobotDriver | MotionExecutor/Web | 读取手关节角 |
| `/robot_driver/hand/set_angles` | RobotDriver | MotionExecutor | 设置手关节角 |
| `/robot_driver/hand/get_torques` | RobotDriver | MotionExecutor | 读取扭矩限制 |
| `/robot_driver/hand/set_torques` | RobotDriver | MotionExecutor | 设置扭矩限制 |
| `/robot_driver/hand/get_force_sensor` | RobotDriver | MotionExecutor | 读取手部力传感器 |

## 5.3 Action

| Action | 服务端 | 客户端 | 作用 |
|---|---|---|---|
| `motion_executor/execute_task` | MotionExecutor | TaskPlanner、Web、Harness | 执行一项技能/API |
| `/vla/execute` | VLA Node | 外部客户端 | 语言指令 → VLA 动作 |
| `FollowCartesianTrajectory` | 接口已定义 | 主链中未发现实际使用 | 预留轨迹 Action |

---

# 6. 核心数据结构与逐层转换

## 6.1 感知层数据

### `ObjectDetection`

```text
id
class_name
pose
confidence
size
```

### `ScenePerception`

```text
header
objects[]
scene_valid
scene_id
pointcloud
```

这是通用场景消息。

### `CucumberShape`

```text
width_m
length_m
right_endpoint_x_m
right_endpoint_z_m
endpoint_valid
```

这是切黄瓜任务的专用压缩消息。

## 6.2 TaskPlanner 内部数据

### `WorldState`

保存：

- 物体字典；
- picked/placed 集合；
- RobotStatus；
- 点云；
- 黄瓜长度、宽度；
- 黄瓜右端点；
- 黄瓜形状有效标记。

它是 Planner 内部的“黑板”或轻量世界模型。

### `PlannedStep`

`PlannedStep` 是任务层中间表示，包含：

- `plan_type`；
- `step_index`；
- 目标物体和动作名称；
- 抓取/放置位姿；
- 关节角；
- 轨迹点；
- 实时阻抗参数；
- 手臂编号；
- 执行状态。

当前它是一个较宽的“参数包”，不同 `plan_type` 只使用其中部分字段。

## 6.3 ROS Action 数据

TaskPlanner 将 `PlannedStep` 转成：

```text
ExecuteTask.Goal
├── task_id
├── task_type
├── TaskTarget target
├── drag_command
├── stop_motion_command
├── control
├── controller_name
└── resume_restart
```

`TaskTarget` 又承担：

- 单个位姿；
- 展平后的多航点轨迹；
- 关节目标；
- 手动作；
- 实时阻抗参数；
- 每个航点的肘部范围。

## 6.4 MotionExecutor 数据

Skill 或 API 将 `ExecuteTask.Goal` 转成一个或多个：

```text
MotionPrimitive
```

支持类型包括：

```text
MOVE_CARTESIAN
MOVE_LINEAR_CARTESIAN
MOVE_JOINTS
MOVE_JOINTS_BOTH
GRIPPER_ACTION
SET_HAND_ANGLES
SET_HAND_TORQUES
GET_HAND_ANGLES
GET_HAND_TORQUES
GET_HAND_FORCE_SENSOR
RT_CARTESIAN_IMPEDANCE_ENABLE
RT_CARTESIAN_IMPEDANCE_DISABLE
RT_CARTESIAN_IMPEDANCE_SET_STIFFNESS
RT_CARTESIAN_IMPEDANCE_MOVE_OFFSET
ARM_DRAG
STOP_MOTION
```

## 6.5 数据转换总览

```text
ObjectDetection / ScenePerception
              │
              ▼
WorldObject / WorldState
              │
              ▼
Policy.select_next_goal()
              │
              ▼
PlannedStep
              │ TaskPlanner builder
              ▼
ExecuteTask.Goal + TaskTarget
              │ Skill / API
              ▼
MotionPrimitive[]
              │ MotionExecutor dispatcher
              ▼
MoveCartesian / MoveJoints / GripperAction / RT services
              │ RobotDriver adapter
              ▼
RobotInterface / ArmInterface / HandInterface
              │
              ▼
厂商 SDK 参数与网络/CAN 命令
```

---

# 7. 模块一：dexbot_interfaces

## 7.1 职责边界

该包是整个系统的通信契约层，负责定义跨包使用的：

- ROS message；
- ROS service；
- ROS action。

它不应该包含业务逻辑，也不应该依赖具体机器人实现。

## 7.2 核心接口

### Action

- `ExecuteTask.action`
- `ExecuteVLA.action`
- `FollowCartesianTrajectory.action`

### Message

- `ScenePerception.msg`
- `ObjectDetection.msg`
- `CucumberShape.msg`
- `TaskTarget.msg`
- `StopPolicy.msg`
- `SafetyHeartbeat.msg`
- `TaskPlannerStatus.msg`
- 机械臂拖动、停止等命令消息。

### Service

- `StartTask.srv`
- `PauseTask.srv`
- `MoveCartesian.srv`
- `MoveJoints.srv`
- `GripperAction.srv`
- 实时阻抗系列接口；
- 灵巧手读写接口。

## 7.3 设计价值

它充当“反腐层”：

- Planner 不需要 import RobotDriver 的实现类；
- MotionExecutor 不需要 import 厂商 SDK；
- Safety 只需要发布 `StopPolicy`；
- Web 只需要调用稳定 ROS 接口。

## 7.4 薄弱点

1. `TaskTarget` 字段过多，已经成为通用参数包。
2. 同时存在 `geometry_msgs/Pose` 和数组形式的位姿，存在双重表达。
3. 轨迹用扁平数组表达，可读性和校验能力有限。
4. `CucumberShape` 没有 Header、frame_id、时间戳、置信度和协方差。
5. `task_type` 和 primitive kind 大量依赖字符串。
6. `StartTask.resume` 的默认语义较反直觉，容易把“恢复”和“重新开始”混淆。

## 7.5 推荐改法

- 按命令类型拆分目标消息；
- 引入 `CommandType`/常量包；
- 所有几何消息统一带 `Header`；
- 单位写入字段名或接口文档；
- 对轨迹使用结构化 waypoint 数组；
- 接口版本化，例如 `ExecuteTaskV2`。

---

# 8. 模块二：dexbot_camera_driver

## 8.1 职责边界

负责：

- 适配 Gemini335L、RealSense 等相机；
- 发布 RGB、Depth、CameraInfo；
- 提供相机状态；
- 隔离底层相机 SDK。

它不应该承担：

- 目标检测；
- 点云语义；
- 黄瓜形状推断；
- 任务策略。

## 8.2 对外接口

当前主启动通过 remap 生成：

```text
/camera1/color/image_raw
/camera1/depth/image_raw
/camera1/color/camera_info
```

相机节点放在 `camera1` namespace 下。

## 8.3 设计评价

相机驱动与感知分包是正确的。这样更换模型或感知方法时，不必修改硬件驱动。

## 8.4 风险

- 多相机命名空间在 Perception、Safety、Launch 中没有完全统一；
- 依靠固定启动延时，而不是显式 camera-ready；
- 需进一步确认不同相机的深度单位和对齐方式是否被统一。

---

# 9. 模块三：dexbot_perception

## 9.1 职责边界

负责：

1. 接收相机数据；
2. 执行分割/检测；
3. 利用深度和标定结果估算三维位姿；
4. 发布通用 `ScenePerception`；
5. 提供任务专用感知适配器。

不负责：

- 决定机械臂动作；
- 编排任务流程；
- 调用 RobotDriver。

## 9.2 主要结构

```text
dexbot_perception/
├── perception_node.py
├── pipeline/
│   ├── perception_pipeline.py
│   └── pose_estimator.py
├── task/
│   └── cut_cucumber/
│       ├── cucumber_shape_node.py
│       └── shape_estimator.py
├── utils/
│   └── calibration_manager.py
├── visualization/
└── config/
```

## 9.3 主节点

`PerceptionNode`：

- 声明 backend、模型路径、阈值、相机命名空间；
- 缓存 RGB、Depth 和 CameraInfo；
- 调用视觉处理器；
- 发布 `ScenePerception`；
- 可选发布可视化和点云。

当前配置：

```text
backend_type: yolo_seg
text_prompt: cucumber
camera_namespaces: ["camera1"]
enable_pointcloud_pipeline: false
publish_rate_hz: 15.0
```

模型路径当前是机器本地绝对路径，迁移性较差。

## 9.4 感知流水线

典型流程：

```text
RGB
  ↓
YOLO/SAM 分割
  ↓
mask
  + Depth
  + Camera Intrinsics
  + T_base_camera
  ↓
三维点/包围盒/姿态
  ↓
ObjectDetection
  ↓
ScenePerception
```

## 9.5 黄瓜任务适配器

`CucumberShapeNode` 订阅：

```text
perception/scene
```

发布：

```text
/perception/cucumber_shape
```

其估算逻辑为：

1. 从对象中选出类别名包含 cucumber 的候选；
2. 优先选择置信度高、体积大的对象；
3. 从 `size.x/y/z` 的正数中：
   - 最大值作为长度；
   - 最小值作为宽度；
4. 从物体四元数计算指定局部轴在世界坐标系中的方向；
5. 用中心点加半个长度得到右端点；
6. 只发布端点的 x、z。

## 9.6 优点

- 通用感知和任务专用感知解耦；
- 黄瓜逻辑没有侵入通用 PerceptionNode；
- TaskPlanner 不需要理解 YOLO mask；
- 允许未来替换黄瓜形状算法。

## 9.7 薄弱点

### 1. 宽度估算过于粗糙

取 `size.x/y/z` 中最小值作为宽度，有可能实际取到厚度、噪声维度或深度方向误差。

### 2. 长轴和局部轴的语义没有强绑定

长度取包围盒最大维度，但端点方向固定取四元数局部 `x` 轴。必须确保：

```text
“最大尺寸方向” == “局部 x 轴”
```

否则长度和方向可能不匹配。

### 3. 消息缺少坐标契约

`CucumberShape` 没有：

- frame_id；
- timestamp；
- 完整三维端点；
- 中心位姿；
- 置信度；
- 数据来源相机；
- 有效期。

### 4. 标定缺失的降级行为需警惕

若 CalibrationManager 在缺少标定时使用单位矩阵，系统可能继续运行，却生成看似合理、实则错误的机器人坐标。

### 5. 多相机融合语义不清

当前配置只使用 camera1。若启用多相机，需要明确：

- 重复目标如何融合；
- 置信度如何合并；
- frame_id 如何统一；
- 时间不同步如何处理。

---

# 10. 模块四：dexbot_task_planner

## 10.1 职责边界

TaskPlanner 负责：

- 接收高层任务；
- 保存世界状态；
- 选择 Policy；
- 管理任务状态机；
- 请求 Policy 生成下一步；
- 将 `PlannedStep` 转为 `ExecuteTask.Goal`；
- 接收动作反馈和结果；
- 进行重试、暂停和任务完成判定。

它不应该：

- 直接调用厂商 SDK；
- 在 Policy 内执行 ROS Service；
- 实现低层实时控制。

## 10.2 主要目录

```text
dexbot_task_planner/
├── task_planner_node.py
├── entities/
│   ├── plan.py
│   ├── pose3d.py
│   └── scene_state.py
└── policy/
    ├── base_policy.py
    ├── magic_cube/
    ├── cut_cucumber/
    ├── peel_apple_policy.py
    └── ...
```

## 10.3 TaskPlannerNode 的角色

它同时承担：

- ROS 适配器；
- 任务状态机；
- Policy 工厂；
- 执行调度器；
- 结果重试；
- WorldState 更新；
- Goal builder。

这使它成为系统中的“应用服务层”。

## 10.4 状态机

状态包括：

```text
IDLE
PREPARING_TASK
EXECUTING_TASK
PAUSED
ERROR
SUCCESS
```

简化流转：

```text
StartTask
   ↓
PREPARING_TASK
   ↓
IDLE
   ↓ tick
EXECUTING_TASK
   ├── 成功 → IDLE → 下一步
   ├── 失败可重试 → IDLE → 重发当前步
   ├── 超过重试 → ERROR
   └── Pause → PAUSED
```

这里的 `IDLE` 既表示“系统空闲”，又表示“当前步骤结束、准备发下一步”，语义稍显混合。

## 10.5 Policy 注册

当前通过硬编码 if/elif：

```text
test_heart
cube
peel_apple
peel_apple_ready
cut_cucumber
test_gripper
```

优点是直观，缺点是每加一个任务都需要修改核心节点。

## 10.6 Policy 合约

```python
select_next_goal(task_id, task_type, target_class) -> Optional[PlannedStep]
update_step_status(step_index, status, failure_reason="")
clear()
```

这是一个拉取式规划接口：

- Planner 每次只取一个步骤；
- 执行完成后回写状态；
- Policy 内部维护当前索引；
- 返回 `None` 表示任务完成。

## 10.7 WorldState

WorldState 是轻量黑板：

```text
objects
picked
placed
robot_status
pointcloud
cucumber_shape fields
```

其优点是 Policy 可共享感知结果，缺点是字段会随着任务增加而不断膨胀。当前黄瓜专用字段已经直接进入通用 WorldState。

## 10.8 PlannedStep → ExecuteTask.Goal

TaskPlanner 根据 `plan_type` 选择 builder：

```text
PLAN_PICK_AND_PLACE          → pick_and_place
PLAN_MOVE_JOINTS             → move_joints
PLAN_CARTESIAN               → cartesian
PLAN_CARTESIAN_TRAJECTORY    → cartesian_trajectory
PLAN_GRIPPER_ACTION          → gripper_action
RT enable/disable/offset     → 对应实时 API
```

这一层的意义是：

> Policy 只构造领域步骤，不直接操作 ROS Action 消息。

## 10.9 暂停与恢复

Pause：

- 请求双臂停止；
- 增加 `goal_epoch`；
- 取消当前 Action；
- 清理运行时状态；
- 保留任务上下文。

Resume：

- 当前语义更接近“重新初始化 Policy 并从头开始”；
- 不是精确从上一个 checkpoint 继续；
- `resume_restart` 用于下一条运动清除硬停锁存。

因此文档和 API 应明确使用“restart/resume from beginning”，避免用户误认为是断点续作。

## 10.10 重试机制

单步失败时最多重试三次，超过后：

- Policy 对当前步骤标记 FAILED；
- RobotState 进入 ERROR；
- 发布失败状态。

优点是具备最基本容错；不足是所有失败都用同一重试策略，没有区分：

- IK 无解；
- 服务超时；
- 碰撞；
- 网络断开；
- 感知失效；
- 安全停止。

---

# 11. 模块五：dexbot_motion_executor

## 11.1 职责边界

MotionExecutor 是任务层和驱动层之间的执行编译器：

```text
ExecuteTask.Goal
      ↓
Skill / API / Controller
      ↓
MotionPrimitive[]
      ↓
RobotDriver services
```

负责：

- 接收 ExecuteTask Action；
- 按 `task_type` 选择 Skill/API；
- 构造运动原语；
- 顺序执行原语；
- 发布 feedback；
- 处理取消；
- 将执行结果返回上层。

## 11.2 内部结构

```text
dexbot_motion_executor/
├── motion_executor_node.py
├── core/
│   ├── base_skill.py
│   ├── base_api.py
│   └── perception_receiver.py
├── skills/
├── api/
├── control/
└── entities/
    ├── motion_primitive.py
    ├── trajectory.py
    └── constraints.py
```

## 11.3 三种扩展机制

### Skill

适合一个任务目标展开成多步动作，例如：

```text
pick_and_place
pick_cucumber
place_cucumber
rotate_apple
arms_initial_ready
```

接口：

```python
build_primitives(execute_task) -> List[MotionPrimitive]
```

### API

适合一条 ExecuteTask 请求直接映射为一个基础命令，例如：

```text
move_joints
move_cartesian
gripper_action
arm_drag
stop_motion
rt_cartesian_impedance_enable
```

接口：

```python
execute(execute_task) -> MotionPrimitive
```

### Controller

`control=True` 时，控制器可读取控制点、关节目标和最新场景，再生成原语。它为未来在线控制、视觉伺服或外部轨迹控制预留了入口。

## 11.4 MotionPrimitive 的意义

MotionPrimitive 相当于执行层的 IR（Intermediate Representation，中间表示）。

它让：

- Skill 不需要知道 ROS Service 的具体调用方式；
- VLA 也可以输出相同类型的动作；
- 未来可添加仿真执行后端；
- 可以在执行前做统一校验、限速和安全过滤。

## 11.5 执行模型

MotionExecutor 对原语顺序执行：

```text
for primitive in primitives:
    validate required fields
    wait_for_service
    call_async
    await result
    optional sleep
    optional check_pick
```

成功全部执行后 Action 成功；任一 primitive 失败则整个 Goal 失败。

## 11.6 取消逻辑

取消时发布 HARD_STOP `StopPolicy`。但当前驱动服务可能处于阻塞执行中，取消检查主要发生在原语边界，因此：

- Action 被取消，不一定意味着当前底层调用瞬间中止；
- 真正的即时停止依赖 RobotDriver 和厂商 SDK 的 stop 实现。

## 11.7 优点

- 统一 Skill/API 入口；
- 执行层不包含高层任务状态；
- MotionPrimitive 可复用；
- 支持普通运动和实时阻抗；
- 支持感知控制器路径。

## 11.8 薄弱点

1. 所谓“插件化”目前是手工字典注册，不是运行时插件系统。
2. Skill、API 和 Controller 的职责边界有重叠。
3. primitive kind 是字符串，运行时才发现拼写错误。
4. `MotionPrimitive` 字段很多，类似宽参数包。
5. `BaseSkill` 与 `BaseApi` 重复实现位姿转换。
6. 同一 Skill 注册代码存在重复 import/重复键风险。
7. 多个 ExecuteTask 客户端可能并发发送 Goal，缺少全局单运动通道仲裁。
8. `time.sleep()` 出现在执行路径中，可能阻塞执行线程。
9. 每个 trajectory waypoint 都单独调用 service，开销和原子性较差。
10. 主接口已定义轨迹 Action，但主链没有真正使用。

---

# 12. 模块六：dexbot_robot_driver

## 12.1 职责边界

RobotDriver 负责：

- 将统一 ROS Service 转换为具体机器人调用；
- 创建机器人实例；
- 管理左右臂和灵巧手；
- 执行普通和实时运动；
- 接收安全停止；
- 屏蔽厂商 SDK 差异。

它不应该负责：

- 高层任务编排；
- 目标检测；
- HTTP 业务逻辑。

## 12.2 目录结构

```text
dexbot_robot_driver/
├── robot_driver_node.py
├── config/
│   └── robot_params.yaml
├── robot/
│   ├── robot_factory.py
│   ├── interface/
│   ├── composite_robot/
│   └── Integrate_robot/
└── sdk/
    ├── arm_api/
    ├── linkerbot/
    └── xcoresdk/
```

## 12.3 抽象接口

主要概念：

```text
ArmInterface
HandInterface
RobotInterface
RobotType
LbotArm
```

高层使用统一接口，不关心：

- 络石还是其他机械臂；
- O6、L25 或 L20lite 手；
- TCP 还是 CAN；
- 单臂还是组合机器人。

## 12.4 工厂模式

`RobotFactory.create_robot(robot_type, config)` 根据字符串创建：

```text
L25LuoshiRobot
O6LbotRobot
O6LuoshiRobot
L25O6LbotRobot
L25O6LuoshiRobot
L20liteLuoshiRobot
```

创建后调用 `initialize(config)`。

当前 `get_supported_robot_types()` 返回列表与实际 if/elif 支持项不完全一致，说明元数据有漂移。

## 12.5 复合模式

以双臂+双手机器人为例：

```text
CompositeRobot
├── left_arm: LuoshiArm
├── right_arm: LuoshiArm
├── left_hand: O6Hand / L25Hand
└── right_hand: O6Hand / L25Hand
```

对外仍暴露统一 Robot 接口。

这适合机器人硬件“臂”和“手”可组合的产品线。

## 12.6 安全停止

RobotDriver 订阅：

```text
/robot_driver/stop_policy
```

当收到 `HARD_STOP` 时：

- 根据 `stop_all` 选择一臂或双臂；
- 清空队列；
- 调用内部 stop；
- 将真实停止集中在 Driver 内执行。

这是正确的安全职责归属：安全层负责判断，Driver 负责真正停止硬件。

## 12.7 SafetyHeartbeat

Driver 监控 SafetyHeartbeat，但源码明确说明：

> 心跳丢失只打印告警，不改变 HARD_STOP 状态机。

这不是 fail-safe 设计。若安全进程崩溃，机器人不会仅因安全心跳丢失而停止。

## 12.8 薄弱点

1. 工厂是硬编码 if/elif。
2. SDK、机器人组合、ROS Adapter 都在一个较大的包中。
3. `Integrate_robot` 等目录命名风格不统一。
4. RobotType 元数据与实际实现存在漂移。
5. 驱动配置依赖具体现场 IP、CAN 和 frame 名。
6. 缺少严格配置 schema。
7. 轨迹通常被拆成多个 service 调用，缺少完整轨迹事务。
8. 心跳丢失不是 fail-safe。
9. 需进一步确认硬停锁存的清除权限是否过于宽松。
10. 真实实时性依赖 Python、ROS 2 和厂商 SDK 的协同，需硬件测量。

---

# 13. 模块七：dexbot_safety

## 13.1 职责边界

Safety 当前设计为：

```text
相机帧缓存
   ↓
SafetyCheck
   ↓
SafetyCheckResult
   ↓
StopPolicy
   ↓
RobotDriver
```

安全层判断是否危险，但不直接调用机械臂 SDK。

## 13.2 主要类

```text
SafetyLayerNode
SafetyCameraReceiver
BaseSafetyCheck
FakeSafetyCheck
SafetyCheckResult
CameraFrameSnapshot
```

## 13.3 检查工厂

SafetyLayerNode 通过 registry 按 `check_type` 创建检查器。

当前实际只有：

```text
fake
```

因此架构支持扩展，但生产级安全算法尚未加入。

## 13.4 FakeSafetyCheck

行为：

- 收到可用帧后计时；
- 每隔配置时间产生一次 HARD_STOP；
- 不判断真实障碍；
- HARD_STOP 无 TTL；
- 需要外部显式恢复。

它适合测试端到端安全链，不适合实际安全保护。

## 13.5 当前配置风险

安全配置：

```text
camera_namespaces: ["camera"]
```

实际启动相机：

```text
camera1
```

若没有其他 remap，SafetyCameraReceiver 可能一直收不到预期深度帧，FakeSafetyCheck 也不会进入正常帧驱动路径。

## 13.6 安全架构评价

正确点：

- StopPolicy 是统一停止协议；
- Driver 集中执行硬停；
- HARD_STOP 有锁存思想；
- 有 SafetyHeartbeat。

不足：

- 没有真实距离/碰撞/人体检测；
- 没有独立硬件急停；
- 没有安全 PLC；
- 心跳丢失不停车；
- 相机和安全算法不是独立安全等级设备；
- 安全配置与 launch 漂移；
- 没有对图像新鲜度、冻结帧、时间戳做强约束。

因此当前 Safety 应理解为：

> 软件安全链路原型，而不是经认证的机器安全系统。

---

# 14. 模块八：dexbot_watchdog

## 14.1 职责边界

Watchdog 由两个监控器组成：

```text
NodeMonitorNode
CanMonitorNode
```

Composition 默认：

```text
enable_can_monitor = false
enable_node_monitor = true
```

## 14.2 NodeMonitorNode

监控默认关键节点是否出现在 ROS graph 中，例如：

- camera_driver；
- perception_node；
- motion_executor_node；
- task_planner_node；
- robot_driver_node。

它检测的是“节点名称存在”，不是：

- 节点是否还能处理请求；
- topic 是否更新；
- 推理是否卡死；
- Driver 是否连接硬件；
- Action 是否有进展。

因此属于一级存活监控。

## 14.3 CanMonitorNode

可以：

- 检查 CAN 接口是否存在和健康；
- 检测 bus-off/error-passive；
- 通过 `ip link` 尝试恢复。

这个功能有实际价值，但当前默认关闭。

## 14.4 严重安全问题

代码中存在硬编码 sudo 凭据默认值。无论仓库是否私有，这都不应出现在源码中。

必须：

- 立即轮换该凭据；
- 从 Git 历史中清理；
- 改用最小权限 sudoers 规则；
- 或通过受限 helper/systemd service 完成 CAN 恢复；
- 禁止把密码经 stdin 传给 sudo。

## 14.5 其他薄弱点

- `publish_health_topic` 参数存在，但实际健康 topic 机制不完整；
- 节点异常时没有自动重启；
- 未将 Watchdog 结果接入 Safety；
- 仅看 ROS graph，不能发现假活；
- 日志节流实现可能在同一秒重复打印；
- Watchdog 自身退出时出现重复 shutdown 异常。

---

# 15. 模块九：dexbot_web_api

## 15.1 职责边界

Web API 使用 FastAPI 对外提供 HTTP 接口，并通过 RosBridge 调用 ROS。

主要端点：

```text
POST /api/robot/self-check
POST /api/task/start
GET  /api/task/current
POST /api/task/control
POST /api/robot/action
GET  /api/logs
GET  /api/system/status
```

## 15.2 RosBridge

RosBridge 封装：

- StartTask client；
- PauseTask client；
- ExecuteTask ActionClient；
- GetArmPose；
- Hand 状态；
- Gripper；
- Camera status；
- ScenePerception subscription；
- TaskPlannerStatus subscription。

这是典型 Adapter/Facade。

## 15.3 两种执行路径

### 高层任务

```text
HTTP recipeCode
  ↓ RECIPE_TASK_MAP
task_type
  ↓ StartTask service
TaskPlanner
```

### 直接机器人动作

Web 中部分命令直接调用：

```text
MotionExecutor.ExecuteTask
或
RobotDriver.gripper_action
```

例如：

- arms_initial_ready；
- pick_cucumber；
- place_cucumber；
- call_stuff；
- arm_drag；
- gripper action。

## 15.4 优点

- HTTP 与 ROS 代码隔离；
- recipeCode 到 task_type 有显式映射；
- 状态通过 TaskPlannerStatus 汇总；
- 便于前端和工装操作。

## 15.5 薄弱点

1. 存在绕过 TaskPlanner 的直接动作路径。
2. 多入口没有全局运动锁。
3. 状态主要在内存中，进程重启后丢失。
4. CORS 配置较宽松。
5. 未发现明确的认证、授权和 TLS 机制。
6. HTTP 线程通过等待事件同步 ROS 结果，需关注阻塞和超时。
7. self-check 主要是读取状态，并非完整安全自检。
8. API 与机器人安全权限边界不足。

---

# 16. 模块十：dexbot_vla

## 16.1 职责边界

VLA 模块将：

```text
语言指令 + 相机图像
            ↓
VLA 模型
            ↓
MotionPrimitive[]
            ↓
机器人执行
```

对外提供：

```text
/vla/execute
```

## 16.2 模型接口

抽象：

```text
BaseVLAModel
EmptyVLAModel
Pi0Model
```

VLANode 使用注册表按 `model_name` 获取模型。

## 16.3 Pi0 隔离设计

Pi0Model 不直接在 ROS 节点主 Python 环境加载 openpi，而是：

1. 启动单独 conda 环境；
2. 启动子进程；
3. 使用 stdin/stdout 逐行 JSON 通信；
4. 图像以 base64 PNG 传输；
5. 子进程首行返回 ready；
6. 主进程管理异常和重启。

这个设计的优点：

- 隔离依赖；
- ROS 环境不必与模型环境完全一致；
- 模型崩溃不一定拖垮整个 ROS 进程；
- 便于 mock backend。

缺点：

- base64 和 JSON 有额外开销；
- stdin/stdout 协议能力有限；
- 缺少成熟 RPC 的流控和可观测性；
- 模型服务器健康检查较弱。

## 16.4 执行路径不一致

VLA 的 RobotExecutor：

- 笛卡尔和关节动作直接调用 RobotDriver；
- 夹爪动作却通过 HarnessAPI MCP，再进入 MotionExecutor。

因此同一组 VLA 动作可能走两条执行路径：

```text
arm motion → RobotDriver
gripper → Harness → MotionExecutor → RobotDriver
```

这会导致：

- 安全过滤不一致；
- feedback 不一致；
- 运动仲裁不一致；
- Harness 未启动时夹爪失败。

## 16.5 当前启用状态

主 launch 中 VLA 被注释，默认不启动。

## 16.6 需进一步确认

- Pi0 真实 checkpoint 是否可用；
- 输出动作是否经过坐标、尺度、速度和工作空间校验；
- VLA 动作是否针对当前机器人训练；
- 是否做了视觉延迟和图像新鲜度检查；
- 真机执行前是否有人工确认或 dry-run 审核。

---

# 17. 模块十一：dexbot_harness_api

## 17.1 职责

Harness API 提供 MCP 工具，将外部工装/Agent 请求转换为 ROS Action。

核心路径：

```text
MCP execute_task
   ↓
ExecuteTask ActionClient
   ↓
MotionExecutor
```

## 17.2 优点

- 为 Agent/MCP 提供统一工具；
- 有请求状态缓存；
- 有进程级 guard，避免 MCP 路径内部重复占用；
- 可查看 feedback 和 result。

## 17.3 局限

guard 只保护：

```text
MCP → ExecuteTask
```

无法阻止：

- Web 同时发 Goal；
- TaskPlanner 同时发 Goal；
- VLA 直接调用 Driver；
- 其他 ROS 客户端直接调用 Driver。

所以它不是全局运动仲裁。

## 17.4 当前启用状态

主 launch 中 Harness 被注释。VLA 夹爪路径却依赖 Harness URL，因此启用 VLA 时必须同步确认 Harness 是否作为外部进程运行。

---

# 18. 模块十二：bringup、utils 与 toolbox

## 18.1 dexbot_bringup

职责：

- 聚合节点；
- 加载配置；
- 设定 remap；
- 控制启动顺序。

主要问题：

- 注释和实际启动内容漂移；
- 固定延迟代替 readiness；
- 可选节点靠注释开关；
- 各节点 namespace 规则不统一。

推荐使用 LaunchArgument：

```text
enable_camera2
enable_vla
enable_harness
enable_watchdog
enable_safety
use_fake_driver
```

## 18.2 dexbot_utils

提供：

- `DexbotLogger`；
- 配置读取；
- 通用辅助代码。

应保持轻量，避免变成所有包相互耦合的杂物箱。

## 18.3 dexbot_toolbox

面向：

- 标定；
- 可视化；
- metrics；
- 开发工具。

建议与运行时节点严格区分，避免生产部署引入不必要的大依赖。

---

# 19. 核心设计模式深度分析

## 19.1 策略模式

### 实现

```text
BasePolicy
├── TestHeartPolicy
├── MagicCubePolicy
├── PeelApplePolicy
└── CutCucumberPolicy
```

TaskPlanner 在运行时根据 task_type 选择策略。

### 优点

- 各任务算法独立；
- 任务可替换；
- Planner 只依赖统一接口；
- 有利于团队并行开发。

### 缺点

- 当前策略注册硬编码；
- Policy 状态保存在对象内部，不易持久化；
- 接口只返回单步，复杂并发任务表达有限；
- 错误恢复策略没有进入 Policy contract。

## 19.2 复合策略

`CutCucumberPolicy` 本身不直接生成全部动作，而是组合：

```text
CutCucumberDiagonallyPolicy
CutCucumberRollPolicy
CutCucumberDiagonallyPolicy("straight")
```

总策略负责：

- 模式选择；
- 子任务顺序；
- 状态转发；
- 感知参数注入。

子策略负责：

- 具体步骤生成；
- 内部索引；
- 动作参数。

这相当于：

> Strategy + Composite + 简化工作流编排

优点是清晰；不足是串行流程仍通过手写 for/if 表达，分支、回退、并行和补偿会迅速复杂。

## 19.3 工厂模式

RobotFactory 将 `robot_type` 转为具体 Robot 对象。

优点：

- 上层不依赖具体构造函数；
- 可配置选择机器人；
- 初始化流程集中。

不足：

- if/elif 不是真正开放扩展；
- 新机器人仍需改核心工厂；
- supported metadata 与实现会漂移。

推荐改为：

```python
ROBOT_REGISTRY = {}

def register_robot(name):
    ...

RobotFactory.create(name, config)
```

或使用 Python entry point/pluginlib。

## 19.4 复合模式

双臂机器人由多个 Arm 和 Hand 组合，对外作为一个 Robot。

适用于：

- 左右臂不同型号；
- 左右手不同型号；
- 单臂/双臂复用；
- 更换末端执行器。

这是本项目非常值得保留的设计。

## 19.5 技能插件化

当前为“插件式组织”，不是“动态插件系统”。

```text
BaseSkill
   ↑
ConcreteSkill

MotionExecutor._skills[task_type] = skill
```

优点：

- 新技能文件独立；
- 动作展开集中；
- 可复用 MotionPrimitive。

不足：

- 仍需改 MotionExecutor 注册函数；
- 没有 capability metadata；
- 没有版本、输入 schema、前置条件和资源声明。

## 19.6 Command / IR 模式

`PlannedStep` 和 `MotionPrimitive` 都可以理解为命令对象。

特别是 MotionPrimitive：

- 将“想做什么”封装为数据；
- 执行器统一解释；
- 可日志记录；
- 可回放；
- 可仿真；
- 可预校验。

这是整个项目最有价值的架构点之一。

## 19.7 Adapter 模式

典型 Adapter：

- CameraDriver：相机 SDK → ROS topics；
- Perception：模型输出 → ScenePerception；
- CucumberShapeNode：通用场景 → 任务专用形状；
- RobotDriver：ROS service → 厂商 SDK；
- RosBridge：HTTP → ROS；
- Harness：MCP → ROS；
- Pi0Model：子进程协议 → BaseVLAModel。

## 19.8 Facade 模式

RobotDriverNode 为复杂硬件提供统一 ROS Facade。

Web RosBridge 为多个 ROS 接口提供统一 Python Facade。

## 19.9 Observer / Pub-Sub

ROS Topic 实现：

- 感知场景广播；
- 任务状态广播；
- StopPolicy 广播；
- SafetyHeartbeat。

优点是发布者与订阅者解耦；风险是消息新鲜度、QoS 和坐标契约需要更严格。

## 19.10 状态机模式

TaskPlanner 使用 RobotState 管理高层状态，但仍是分散的 if/else 状态机。

若任务继续复杂化，可以考虑：

- 明确 StateMachine 类；
- hierarchical state machine；
- behavior tree；
- workflow engine。

---

# 20. “切黄瓜”任务完整调用链

## 20.1 阶段零：系统启动

```text
CameraDriver 发布 RGB/Depth/Info
             ↓
Perception 检测 cucumber
             ↓
ScenePerception
             ├── TaskPlanner 更新 WorldState.objects
             └── CucumberShapeNode
                       ↓
                 CucumberShape
                       ↓
          WorldState.cucumber_* fields
```

## 20.2 阶段一：用户发起任务

ROS 形式：

```bash
ros2 service call /task_planner/start_task \
  dexbot_interfaces/srv/StartTask \
  "{task_type: cut_cucumber, target_class: full, resume: false}"
```

Web 形式：

```text
POST /api/task/start
recipeCode → RECIPE_TASK_MAP → cut_cucumber
```

数据结构：

```text
StartTask.Request
├── task_id
├── task_type = "cut_cucumber"
├── target_class = "full"
├── scene_id
└── resume = false
```

## 20.3 阶段二：TaskPlanner 初始化策略

```text
TaskPlannerNode._on_start_task()
   ↓
_validate task_type
   ↓
_initialize_policy("cut_cucumber")
   ↓
CutCucumberPolicy(world=self._world)
   ↓
policy.clear()
   ↓
保存 active_task_id / task_type / target_class
```

## 20.4 阶段三：定时器请求下一步

TaskPlanner 每秒 tick：

```text
active task?
pending goal?
state == IDLE?
       ↓
_generate_goal_by_task_type()
       ↓
policy.select_next_goal(...)
```

## 20.5 阶段四：总策略选择子策略

`target_class="full"` 时：

```text
diagonally
   ↓ 完成
right_reverse
   ↓ 完成
straight
   ↓ 完成
return None
```

总策略内部：

```text
CutCucumberPolicy
├── current_action
├── sequence_mode
├── perception_applied
└── subpolicies
```

## 20.6 阶段五：感知数据注入

第一次调用 `select_next_goal()` 时：

```text
WorldState.cucumber_shape_valid?
        ↓
length_m × 1000
        ↓
configure_cucumber_length(length_mm)
```

但当前 `configure_cucumber_length()` 存在逻辑错误，感知长度实际上没有重建切割计划。

## 20.7 阶段六：切割子策略生成 PlannedStep

默认参数：

```text
cucumber_len_mm = 250
margin_mm = 100
cut_step_mm = 3
cuts_per_round = 10
```

总刀数：

```text
floor((250 - 100) / 3) = 50
```

轮次：

```text
ceil(50 / 10) = 5
```

子策略生成的步骤包括：

```text
视觉检查位姿
左臂准备位姿
右臂支撑准备
启用实时阻抗
右臂按压
左臂逐刀：
    切割步进
    下切
    回切/修正
    抬刀
右臂支撑移动
结束动作
```

每次只返回一个 `PlannedStep`。

## 20.8 阶段七：PlannedStep 转 ExecuteTask.Goal

例如笛卡尔步骤：

```text
PlannedStep
├── plan_type = PLAN_CARTESIAN
├── grasp_pose = Pose3D
├── arm_type
├── step_index
└── fruit_id
```

转换为：

```text
ExecuteTask.Goal
├── task_id
├── task_type = "cartesian"
└── target
    ├── object_id
    ├── grasp_position
    ├── grasp_orientation
    └── arm_type
```

实时阻抗步骤则把：

```text
stiffness
desired_wrench
direction
distance
duration
control_period
```

复制到 `TaskTarget`。

## 20.9 阶段八：发送 ExecuteTask Action

```text
TaskPlanner
  │ send_goal_async
  ▼
MotionExecutor ActionServer
```

TaskPlanner 保存：

```text
_current_step_index
_pending_goal
_active_goal_handle
_goal_epoch
```

## 20.10 阶段九：MotionExecutor 选择 API/Skill

切黄瓜 Policy 发出的 `task_type` 多数已经是基础执行类型，例如：

```text
cartesian
cartesian_trajectory
rt_cartesian_impedance_enable
rt_cartesian_impedance_move_offset
gripper_action
```

MotionExecutor 根据注册表选中对应 API 或 Skill。

例如：

```text
cartesian
   ↓
CartesianSkill/API
   ↓
MotionPrimitive(kind="MOVE_LINEAR_CARTESIAN" 或 "MOVE_CARTESIAN")
```

实时阻抗：

```text
rt_cartesian_impedance_move_offset
   ↓
RealtimeCartesianImpedanceMoveOffsetApi
   ↓
MotionPrimitive(kind="RT_CARTESIAN_IMPEDANCE_MOVE_OFFSET")
```

## 20.11 阶段十：MotionPrimitive 执行

例如：

```text
MOVE_LINEAR_CARTESIAN
   ↓
MoveCartesian.Request
├── position
├── orientation
├── speed
├── arm
├── elbow_min_deg
├── elbow_max_deg
└── clear_hard_stop
```

发送到：

```text
/robot_driver/move_linear_cartesian
```

## 20.12 阶段十一：RobotDriver 调用硬件

```text
RobotDriver callback
   ↓
检查 HARD_STOP latch
   ↓
选择 left/right arm
   ↓
RobotInterface
   ↓
O6LuoshiRobot / 其他复合机器人
   ↓
LuoshiArm
   ↓
IK / elbow range search
   ↓
厂商 TCP SDK
   ↓
机械臂控制器
```

灵巧手则经 Hand 实现和 CAN/对应 SDK。

## 20.13 阶段十二：结果回传

```text
RobotDriver Service.Response
   ↓
MotionExecutor primitive success/failure
   ↓
ExecuteTask.Result
   ↓
TaskPlanner result callback
```

成功：

```text
Policy.update_step_status(COMPLETED)
current step retry count = 0
RobotState → IDLE
下一个 tick 请求下一步
```

失败：

```text
retry < 3
  → 重发当前步

retry >= 3
  → Policy step FAILED
  → RobotState.ERROR
  → 发布 failed
```

## 20.14 完整 ASCII 调用图

```text
┌──────────┐
│ 用户/Web │
└────┬─────┘
     │ StartTask.Request
     ▼
┌──────────────────────┐
│ TaskPlannerNode      │
│ active task + state  │
└────┬─────────────────┘
     │ instantiate
     ▼
┌──────────────────────────────┐
│ CutCucumberPolicy            │
│ diagonally→reverse→straight  │
└────┬─────────────────────────┘
     │ delegate
     ▼
┌──────────────────────────────┐
│ 子 Policy                    │
│ build/select PlannedStep     │
└────┬─────────────────────────┘
     │ PlannedStep
     ▼
┌──────────────────────────────┐
│ TaskPlanner Goal Builder     │
│ PlannedStep→TaskTarget       │
└────┬─────────────────────────┘
     │ ExecuteTask.Goal
     ▼
┌──────────────────────────────┐
│ MotionExecutor ActionServer │
└────┬─────────────────────────┘
     │ task_type registry
     ▼
┌──────────────────────────────┐
│ Skill / API / Controller    │
└────┬─────────────────────────┘
     │ MotionPrimitive[]
     ▼
┌──────────────────────────────┐
│ Primitive Dispatcher        │
└────┬─────────────────────────┘
     │ MoveCartesian/RT/etc.
     ▼
┌──────────────────────────────┐
│ RobotDriver ROS Services    │◄──── StopPolicy
└────┬─────────────────────────┘
     │ unified Robot API
     ▼
┌──────────────────────────────┐
│ RobotFactory + Composite    │
└────┬─────────────────────────┘
     │ vendor SDK
     ▼
┌──────────────────────────────┐
│ 双臂 + 灵巧手               │
└────┬─────────────────────────┘
     │ result
     ▼
MotionExecutor Result
     │
     ▼
TaskPlanner update status/retry
```

## 20.15 感知支路

```text
Camera RGB/Depth
      ↓
PerceptionPipeline
      ↓
ObjectDetection(size, pose)
      ↓
ScenePerception
      ↓
CucumberShapeNode
      ↓
length / width / right endpoint
      ↓
TaskPlanner.WorldState
      ↓
CutCucumberPolicy
```

---

# 21. 切黄瓜分支的源码级问题

## 21.1 P0：斜切被强制替换为正切

文件：

```text
policy/cut_cucumber/cut_cucumber_diagonally_policy.py
```

逻辑先正确选择：

```python
if config_lower == "diagonal":
    base_cfg = DiagonalCutConfig()
elif config_lower == "straight":
    base_cfg = StraightCutConfig()
```

随后又无条件执行：

```python
base_cfg = StraightCutConfig()  # TEST PURPOSE ONLY
```

结果：

```text
diagonally → 实际 StraightCutConfig
straight   → 实际 StraightCutConfig
```

修复：

- 删除测试覆盖行；
- 为两种配置增加单元测试；
- 测试生成的第一组切割向量必须不同。

---

## 21.2 P0：黄瓜长度更新永远不生效

当前：

```python
self._cucumber_len_mm = float(cucumber_len_mm)
if abs(cucumber_len_mm - self._cucumber_len_mm) <= 1e-6:
    return
```

赋值后再比较，新旧值永远相等。

正确顺序：

```python
new_len = float(cucumber_len_mm)
if new_len <= 0:
    return
if abs(new_len - self._cucumber_len_mm) <= 1e-6:
    return
self._cucumber_len_mm = new_len
self.clear()
```

---

## 21.3 P0：右臂累计支撑偏移尺度错误

当前：

```python
current_pos[axis] += (
    current_round * cuts_per_round * direction / 1000.0
)
```

实际每轮推进应与：

```text
cuts_per_round × cut_step_mm
```

一致。

默认值：

```text
当前累计：10 mm/轮
实际切割：30 mm/轮
```

建议改为：

```python
current_pos[axis] += (
    current_round
    * cuts_per_round
    * cut_step_mm
    * direction
    / 1000.0
)
```

并统一以“已完成刀数”计算，避免最后一轮不足 10 刀时出错。

---

## 21.4 P0：右臂 RT 参数使用左臂配置

`_rt_enable_step()` 文档声明会按 arm_type 选择左右参数，但实际默认始终：

```python
cfg.rt_left_stiffness
cfg.rt_left_desired_wrench
```

右臂按压可能获得错误的刚度和目标力。

正确方式：

```python
if arm_type == LEFT_ARM:
    default_stiffness = cfg.rt_left_stiffness
    default_wrench = cfg.rt_left_desired_wrench
else:
    default_stiffness = cfg.rt_right_stiffness
    default_wrench = cfg.rt_right_desired_wrench
```

---

## 21.5 P0：翻转起点出现明显异常坐标

运行日志中：

```text
right_reverse_initial
z = -0.3981 m
```

随后 IK 无解。

需要逐项验证：

1. `ScenePerception.header.frame_id`；
2. ObjectDetection.pose 的实际坐标系；
3. 手眼标定矩阵方向是 `T_base_camera` 还是逆矩阵；
4. 是否重复应用变换；
5. 局部 x 轴是否真是黄瓜长度轴；
6. `endpoint_sign` 是否正确；
7. 机器人右臂可达空间；
8. 端点偏置是否在正确坐标系中应用。

推荐在发送目标前增加：

```text
frame_id
center pose
axis vector
length
raw endpoint
offset endpoint
workspace validation result
```

日志，并在 RViz 中同时显示。

---

## 21.6 P1：旋转偏移单位错误风险

`vision_offset` 文档写：

```text
位置：毫米
旋转：度
```

但 `_offset_mm()` 对六个分量全部除以 1000 后直接相加。

位姿旋转单位实际是弧度，因此旋转偏移不能按毫米方式除以 1000。应明确：

```text
xyz_mm
rpy_deg
```

并分别转换：

```python
xyz / 1000
rpy * pi / 180
```

---

## 21.7 P1：独立 Straight Policy 包装类不可用

`CutCucumberStraightPolicy` 将 `StraightCutConfig` 对象传给父类，但父类构造函数期望字符串并调用 `.lower()`。

当前主流程没有使用该类，所以问题暂未触发，但它属于死代码/潜在错误。

建议：

- 删除该包装类，统一使用字符串配置；
- 或修改父类接受 `CutConfigBase`；
- 不要同时保留两套 StraightConfig 定义。

---

## 21.8 P1：翻转验证是占位

`CucumberMotionTracker.verify_roll()` 固定返回：

```text
valid = false
warning = post-roll pointcloud verification is not implemented
```

当前翻转是开环动作。

真正闭环应至少验证：

- 黄瓜中心位移；
- 主轴方向变化；
- 滚动距离；
- 是否滑落；
- 是否仍在可切区域。

---

## 21.9 P1：CheckPick 是占位

TaskPlanner 的 CheckPick 当前延时后直接返回成功。

后续应替换为：

- 手部力传感器；
- 夹爪位置与目标差；
- 视觉目标是否随手移动；
- 多信号融合。

---

## 21.10 P1：感知只在策略第一次调用时注入

`_perception_applied` 使黄瓜长度只读取一次。

优点是任务执行期间参数稳定；问题是：

- 第一次调用时若感知无效，之后不会自动更新；
- 翻转后形状改变也不会重新采样；
- 任务执行前没有“等待有效感知”的门控。

建议引入：

```text
WAITING_FOR_PERCEPTION
PERCEPTION_SNAPSHOT_LOCKED
```

并保存 scene_id/timestamp。

---

## 21.11 P2：步骤命名大量使用 TODO

多个右臂按压步骤名称为 `"TODO"`。

影响：

- 日志无法区分步骤；
- 失败定位困难；
- 状态回放困难；
- 指标聚合困难。

步骤名应包含：

```text
task / phase / round / cut / arm / primitive
```

---

# 22. 整体架构优点

## 22.1 分层总体合理

从任务语义到硬件 SDK 有清晰下降路径：

```text
Policy
→ PlannedStep
→ ExecuteTask
→ MotionPrimitive
→ Driver Service
→ SDK
```

## 22.2 中间表示可复用

可以将同一个 MotionPrimitive 后端替换为：

- 真机 Driver；
- MuJoCo；
- Isaac Sim；
- FakeController；
- 离线轨迹检查器。

## 22.3 任务扩展规范明确

SKILL.md 已明确：

- 新任务独立目录；
- 总策略+子策略；
- Policy 不直接执行 ROS；
- 修改核心节点要谨慎；
- Camera/Driver/Perception 默认只读。

这对多人协作很有价值。

## 22.4 感知适配器设计正确

通用 ScenePerception 与任务特定 CucumberShape 分开，符合“通用核心 + 任务适配器”。

## 22.5 硬件抽象方向正确

RobotFactory + CompositeRobot 能支持产品线组合。

## 22.6 安全停止有统一入口

StopPolicy 统一进入 Driver，避免每个业务节点各自实现硬停。

## 22.7 VLA 模型环境隔离有工程价值

单独 conda 子进程解决了 ROS 与深度学习依赖冲突，是现实可行方案。

---

# 23. 整体架构薄弱点

## 23.1 缺少全局资源仲裁

当前至少有四类执行入口：

```text
TaskPlanner
Web direct action
Harness MCP
VLA direct driver
```

需要一个全局 `MotionCoordinator`：

```text
owner
priority
lease
preemption policy
arm resource
current goal
safety state
```

所有运动必须经过它。

## 23.2 分层被旁路破坏

VLA 直接调用 Driver，Web 直接调用 Driver 的夹爪，导致：

- 统一校验失效；
- feedback 不一致；
- 取消和审计不一致；
- 安全规则可能不一致。

建议所有动作统一进入 MotionExecutor，Driver 只接受 MotionExecutor 和 Safety 的调用，或至少加权限/token。

## 23.3 配置管理不成熟

存在：

- 本机绝对路径；
- IP/CAN/模型/标定混在多个位置；
- launch 注释开关；
- namespace 漂移；
- 无 schema；
- 可能含敏感凭据。

建议引入：

```text
deployment profile
robot profile
perception profile
task profile
secret provider
```

## 23.4 坐标系契约不足

几何数据经多个层转换，但很多消息缺少 Header/frame_id。

在机器人系统中，错误坐标往往不会抛异常，而是产生“合法但危险”的数值。

## 23.5 类型系统偏弱

很多核心选择依赖字符串：

```text
task_type
plan_type value
primitive kind
robot_type
controller_name
action_name
```

建议：

- 枚举；
- registry；
- schema 校验；
- 构造时验证；
- capability discovery。

## 23.6 状态和恢复不持久

TaskPlanner、Web、Harness 的运行状态主要在内存。进程重启后：

- active task 丢失；
- step index 丢失；
- 硬件可能停在中间状态；
- resume 无法精确恢复。

## 23.7 测试结构不平衡

很多包的测试主要是：

- copyright；
- flake8；
- pep257。

业务级测试较少，尤其缺：

- Policy 计划快照测试；
- Planner→Executor contract 测试；
- MotionPrimitive 执行测试；
- 坐标系测试；
- 故障注入；
- 多入口并发；
- 切黄瓜回归测试。

## 23.8 Safety 和 Watchdog 未闭环

- Safety 只有 fake；
- Safety 心跳丢失不停车；
- Watchdog 不接入 Safety；
- NodeMonitor 只看节点名；
- CAN 恢复默认关闭；
- 无安全状态总线。

## 23.9 可观测性不足

日志很多，但缺少结构化 trace：

```text
task_id
step_id
goal_id
primitive_id
driver_request_id
scene_id
frame_id
```

建议贯穿全链路。

## 23.10 退出清理不规范

日志中多个节点 Ctrl+C 后重复调用 `rclpy.shutdown()`，导致进程退出码 1。应统一使用：

```python
if rclpy.ok():
    rclpy.shutdown()
```

并避免 launch 和节点多处重复关闭同一 context。

---

# 24. 在其他项目中复用这套架构

## 24.1 建议保留的部分

### 必须保留思想

1. 接口包独立；
2. Task Policy 与 Motion Skill 分层；
3. PlannedStep；
4. MotionPrimitive；
5. Robot 抽象接口；
6. Driver 集中硬件访问；
7. StopPolicy；
8. 通用感知 + 任务适配器；
9. task_id 全链路传递。

### 可直接复用的组织方式

```text
my_robot_ws/
├── my_interfaces/
├── my_bringup/
├── my_perception/
├── my_task_planner/
│   └── policy/
├── my_motion_executor/
│   └── skills/
├── my_robot_driver/
├── my_safety/
└── my_web_api/
```

## 24.2 更换机器人时需要改什么

主要定制：

```text
RobotDriver
RobotFactory/registry
ArmInterface adapter
HandInterface adapter
robot config
URDF/frames
运动速度/工作空间
实时控制能力
```

尽量不改：

```text
TaskPlanner
Policy contract
ExecuteTask
MotionPrimitive
Web task API
```

前提是新机器人能实现相同能力。

## 24.3 更换任务时需要改什么

新增：

```text
policy/<new_task>/
├── new_task_policy.py
├── new_task_subtask_a_policy.py
└── new_task_subtask_b_policy.py
```

如果已有 primitive 足够，不必改 Driver。

若需要新技能：

```text
motion_executor/skills/new_skill.py
```

若需要新硬件能力：

```text
先扩 interfaces
再扩 MotionPrimitive
再扩 Driver
最后让 Skill 使用
```

不要让 Policy 直接调用 Driver。

## 24.4 更换感知模型时需要改什么

建议只替换：

```text
Perception backend
```

保持：

```text
ScenePerception contract
Task-specific adapter
WorldState ingestion
```

例如 YOLO 换成 SAM、GroundingDINO 或自研模型时，上层无需变化。

## 24.5 推荐的新任务开发流程

```text
1. 定义任务成功条件
2. 定义需要的世界状态
3. 定义子任务状态图
4. 检查已有 MotionPrimitive 是否足够
5. 实现子 Policy
6. 实现总编排 Policy
7. 注册 task_type
8. 写计划快照测试
9. 在 FakeDriver 执行
10. 在仿真执行
11. 低速真机执行
12. 故障注入与安全测试
```

## 24.6 建议的 Policy 目录模板

```text
policy/new_task/
├── __init__.py
├── new_task_policy.py
├── new_task_config.py
├── contracts.py
├── subtasks/
│   ├── acquire_target.py
│   ├── manipulate.py
│   └── verify.py
└── tests/
    ├── test_plan_sequence.py
    ├── test_failure_transition.py
    └── test_perception_gate.py
```

## 24.7 建议的能力注册

每个 Skill 声明：

```text
name
version
required_arms
required_sensors
required_driver_capabilities
input_schema
preconditions
cancel_mode
safety_class
```

MotionExecutor 启动时自动注册并验证。

---

# 25. 推荐改造路线

## 阶段 A：先修复会直接改变动作的错误

1. 删除斜切配置强制覆盖；
2. 修复黄瓜长度更新；
3. 修复右臂累计偏移；
4. 左右臂分别选择 RT 参数；
5. 修复 StraightPolicy 构造契约；
6. 分离 xyz 和 rpy 偏移单位；
7. 删除所有 `"TODO"` 步骤名；
8. 增加切黄瓜计划快照测试。

## 阶段 B：解决当前右臂 IK 失败

1. 为 CucumberShape 增加 Header；
2. 发布完整中心 Pose 和完整端点 Point；
3. 在 RViz 发布 Marker；
4. 记录 axis vector、frame_id 和标定矩阵；
5. 增加工作空间边界检查；
6. IK 预检放到发送动作之前；
7. 对异常 z 值直接拒绝；
8. 用固定标定板验证 base-camera 变换。

## 阶段 C：统一执行入口

引入：

```text
MotionCoordinator
```

职责：

- 单臂/双臂资源锁；
- Goal 优先级；
- 安全抢占；
- 任务 ownership；
- VLA/Web/MCP/Planner 仲裁；
- 当前动作查询；
- 统一取消。

VLA、Web、Harness 不再直接调用 Driver。

## 阶段 D：升级接口契约

- `CucumberShapeStamped`；
- 结构化 `TrajectoryWaypoint[]`；
- typed command；
- capability registry；
- 单位和 frame schema；
- API version；
- task/step/primitive trace id。

## 阶段 E：升级启动和配置

- launch arguments 代替注释；
- lifecycle nodes；
- ready service；
- 配置 schema；
- 移除绝对路径；
- secrets 从源码移除；
- robot/perception/deployment profile 分离。

## 阶段 F：升级安全与监控

- Safety 心跳丢失进入安全状态；
- 图像冻结检测；
- 帧新鲜度；
- 实际距离/人体/区域检测；
- Watchdog 健康 topic；
- 进程自动恢复；
- CAN 恢复使用最小权限 helper；
- 独立硬件急停。

## 阶段 G：升级测试体系

### 单元测试

- Policy 输出序列；
- 坐标转换；
- Shape estimator；
- Skill→Primitive；
- Factory registry。

### Contract 测试

- PlannedStep→ExecuteTask；
- ExecuteTask→MotionPrimitive；
- MotionPrimitive→Driver request。

### 集成测试

- FakeDriver；
- rosbag replay；
- Action cancel；
- Safety stop；
- 多入口争抢。

### 仿真测试

- 可达性；
- 碰撞；
- 执行时间；
- 失败恢复。

### 真机测试

- 低速；
- 单臂；
- 双臂；
- 力控；
- 安全触发；
- 网络故障；
- 相机故障。

---

# 26. 推荐学习顺序与练习

## 26.1 第一阶段：先理解接口

阅读：

```text
dexbot_interfaces/action/ExecuteTask.action
dexbot_interfaces/msg/TaskTarget.msg
dexbot_interfaces/msg/ScenePerception.msg
dexbot_interfaces/msg/StopPolicy.msg
dexbot_interfaces/srv/StartTask.srv
```

学习目标：

- 弄清每层传什么；
- 区分 service 和 action；
- 弄清取消、反馈、结果。

## 26.2 第二阶段：读 TaskPlanner

顺序：

```text
entities/plan.py
entities/scene_state.py
policy/base_policy.py
task_planner_node.py
```

练习：

- 手工追踪一个 `PLAN_CARTESIAN`；
- 画出状态变化；
- 修改一个 Fake Policy，输出三个步骤。

## 26.3 第三阶段：读 MotionExecutor

顺序：

```text
motion_primitive.py
base_skill.py
一个简单 API
一个简单 Skill
motion_executor_node.py
```

练习：

- 写一个只移动关节的 Skill；
- 用 Fake Driver 验证 primitive 顺序。

## 26.4 第四阶段：读 RobotDriver

顺序：

```text
interfaces.py
robot_factory.py
一个 CompositeRobot
robot_driver_node.py
一个具体 Arm adapter
```

学习目标：

- 分清 ROS Adapter、Robot 抽象和 SDK；
- 理解左右臂路由；
- 理解硬停锁存。

## 26.5 第五阶段：读 Perception

顺序：

```text
ScenePerception.msg
perception_pipeline.py
pose_estimator.py
shape_estimator.py
cucumber_shape_node.py
```

练习：

- 用录制消息离线计算黄瓜端点；
- 在 RViz 画出中心、轴和端点。

## 26.6 第六阶段：完整追踪切黄瓜

建议在每层打印同一个 trace：

```text
task_id
step_index
fruit_id
plan_type
primitive kind
arm
target pose
driver result
```

最终能回答：

1. 这个位置从哪里来的？
2. 当前是哪一刀？
3. 为什么用左臂/右臂？
4. 为什么进入 RT？
5. 当前失败属于哪一层？
6. 重试会不会改变目标？
7. 暂停后从哪里恢复？

---

# 27. 需进一步确认的事项

以下内容不能仅凭当前源码完全确认。

## 27.1 VLA

- Pi0 checkpoint 是否真实存在并匹配当前机器人；
- 模型输出动作的物理含义；
- 训练数据坐标系；
- 动作缩放和速度限制；
- 真机是否实际跑通。

## 27.2 Safety

- 是否另有未打包的生产安全算法；
- 是否有硬件急停；
- 是否有独立安全控制器；
- 实际部署时 camera namespace 是否被外部 remap；
- HARD_STOP 恢复是否经过人工确认。

## 27.3 Watchdog

- 生产环境是否启用 CAN monitor；
- 是否有 systemd/supervisor 外部进程恢复；
- 健康结果是否被其他系统消费。

## 27.4 Harness

- 外部 HarnessAPI 服务的完整通信协议；
- 主 launch 未启动时是否由 systemd/docker 单独启动；
- 工装实际控制范围。

## 27.5 坐标与标定

- ScenePerception.pose 的 frame；
- base frame 的真实定义；
- 左右臂是否共享中心坐标；
- 标定矩阵是否正确；
- 右端点异常的唯一根因。

## 27.6 厂商 SDK

- SDK 服务调用是否阻塞；
- 停止命令延迟；
- 实时阻抗循环实际运行在哪一层；
- 网络断开后的行为；
- IK 和 elbow range 的具体约束。

---

# 28. 关键文件索引

## 28.1 启动与配置

```text
src/dexbot_bringup/launch/dexrob_full.launch.py
src/dexbot_perception/dexbot_perception/config/perception_params.yaml
src/dexbot_robot_driver/dexbot_robot_driver/config/robot_params.yaml
src/dexbot_safety/dexbot_safety/config/safety_layer_params.yaml
.localconfig
SKILL.md
```

## 28.2 接口

```text
src/dexbot_interfaces/action/ExecuteTask.action
src/dexbot_interfaces/action/ExecuteVLA.action
src/dexbot_interfaces/msg/TaskTarget.msg
src/dexbot_interfaces/msg/ScenePerception.msg
src/dexbot_interfaces/msg/CucumberShape.msg
src/dexbot_interfaces/msg/StopPolicy.msg
src/dexbot_interfaces/srv/StartTask.srv
src/dexbot_interfaces/srv/MoveCartesian.srv
```

## 28.3 TaskPlanner

```text
src/dexbot_task_planner/dexbot_task_planner/task_planner_node.py
src/dexbot_task_planner/dexbot_task_planner/entities/plan.py
src/dexbot_task_planner/dexbot_task_planner/entities/scene_state.py
src/dexbot_task_planner/dexbot_task_planner/policy/base_policy.py
```

## 28.4 切黄瓜

```text
policy/cut_cucumber/cut_cucumber_policy.py
policy/cut_cucumber/cut_cucumber_diagonally_policy.py
policy/cut_cucumber/cut_cucumber_roll_policy.py
policy/cut_cucumber/cut_cucumber_straight_policy.py
policy/cut_cucumber/cucumber_reverse_contracts.py
policy/cut_cucumber/cucumber_reverse_interfaces.py
```

## 28.5 MotionExecutor

```text
src/dexbot_motion_executor/dexbot_motion_executor/motion_executor_node.py
src/dexbot_motion_executor/dexbot_motion_executor/core/base_skill.py
src/dexbot_motion_executor/dexbot_motion_executor/core/base_api.py
src/dexbot_motion_executor/dexbot_motion_executor/entities/motion_primitive.py
src/dexbot_motion_executor/dexbot_motion_executor/skills/
src/dexbot_motion_executor/dexbot_motion_executor/api/
```

## 28.6 Driver

```text
src/dexbot_robot_driver/dexbot_robot_driver/robot_driver_node.py
src/dexbot_robot_driver/dexbot_robot_driver/robot/robot_factory.py
src/dexbot_robot_driver/dexbot_robot_driver/robot/interface/interfaces.py
src/dexbot_robot_driver/dexbot_robot_driver/robot/composite_robot/
```

## 28.7 Perception

```text
src/dexbot_perception/dexbot_perception/perception_node.py
src/dexbot_perception/dexbot_perception/pipeline/perception_pipeline.py
src/dexbot_perception/dexbot_perception/pipeline/pose_estimator.py
src/dexbot_perception/dexbot_perception/task/cut_cucumber/cucumber_shape_node.py
src/dexbot_perception/dexbot_perception/task/cut_cucumber/shape_estimator.py
```

## 28.8 Safety、Watchdog、Web、VLA

```text
src/dexbot_safety/dexbot_safety/safety_layer_node.py
src/dexbot_safety/dexbot_safety/checks/fake_check.py
src/dexbot_watchdog/dexbot_watchdog/watchdog_composition.py
src/dexbot_watchdog/dexbot_watchdog/dog_node/node_monitor_node.py
src/dexbot_watchdog/dexbot_watchdog/dog_node/can_monitor_node.py
src/dexbot_web_api/dexbot_web_api/app.py
src/dexbot_web_api/dexbot_web_api/ros_bridge.py
src/dexbot_vla/dexbot_vla/vla_node.py
src/dexbot_vla/dexbot_vla/models/pi0_model.py
src/dexbot_vla/dexbot_vla/service/robot_executor.py
```

---

# 29. 最终评价

## 29.1 架构成熟度判断

| 维度 | 评价 | 说明 |
|---|---|---|
| 分层设计 | 较好 | Planner、Executor、Driver 边界总体清晰 |
| 任务扩展性 | 中上 | Policy 结构清楚，但注册仍硬编码 |
| 硬件复用性 | 中上 | 工厂+复合机器人思路正确 |
| 感知解耦 | 较好 | 通用场景与任务适配器分开 |
| 执行一致性 | 中等 | 多条旁路破坏统一执行链 |
| 配置可移植性 | 偏弱 | 绝对路径、namespace 和注释漂移 |
| 安全完整性 | 较弱 | 当前主要是 Fake 安全链原型 |
| 可观测性 | 中等偏弱 | 有日志，缺少统一 trace 和结构化指标 |
| 测试完整性 | 偏弱 | 业务回归和集成测试不足 |
| 切黄瓜分支稳定性 | 当前不足 | 存在多处会直接改变动作的源码问题 |

## 29.2 最重要的架构认识

这套工程不应被理解为：

> “一个切黄瓜程序”

而应理解为：

> “一个用 ROS 2 把感知、任务策略、运动技能、机器人抽象、安全和外部接口组织起来的双臂操作平台。”

其中最应学习和复用的是：

```text
领域任务步骤 PlannedStep
        ↓
跨进程执行协议 ExecuteTask
        ↓
设备无关动作 MotionPrimitive
        ↓
硬件适配 RobotDriver
```

最需要优先治理的是：

```text
坐标与单位契约
全局运动仲裁
配置与启动一致性
Safety fail-safe
任务/技能注册机制
真实业务测试
```

## 29.3 对当前切黄瓜任务的直接结论

当前代码已经具备完整的端到端框架和实际动作链，但在继续真机测试之前，至少应先完成：

1. 删除斜切测试覆盖；
2. 修复感知长度更新；
3. 修复右臂支撑累计偏移；
4. 修复左右臂阻抗参数选择；
5. 核对黄瓜端点 frame 和手眼标定；
6. 为目标位姿增加工作空间与 IK 预检；
7. 修复 Safety 相机 namespace；
8. 移除源码中的敏感凭据；
9. 增加单一运动仲裁；
10. 为切黄瓜建立可重复的计划级与仿真级回归测试。

完成这些后，这套架构才适合作为稳定的任务开发基线，而不是仅作为功能联调分支。
