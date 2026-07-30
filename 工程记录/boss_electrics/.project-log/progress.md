# Progress

倾倒入盘技术路线、V1 业务澄清和技术选型已完成；当前进入工程实施阶段，已完成 Planner 的动态等待调度基础能力。

- 推荐：示教轨迹基线 + 受限重量/力矩反馈局部修正。
- 回退：带安全限幅、超时、急停和人工确认的示教回放。
- V1：作为中间环节承接上游任务，订阅感知组锅把信息，沿锅把 PCA 主轴施加中心坐标系下的抓取偏置，使用参数化抓取 TCP 控制左臂；提锅后由底盘组协同移动，再以机器人中心坐标系下的餐盘中心点加 xyz 偏置计算倾倒点，通过参数化锅具 TCP 和其局部坐标系增量回放完成倾倒；放回/home、落料验收和异常处理后续补充，不考虑右手锅铲辅助。
- V2：V1 闭环稳定后，再评估右手锅铲抓取、放置、辅助动作和碰撞约束。
- 代码主链：`ScenePerception → TaskPlanner → ExecuteTask → MotionExecutor → RobotDriver`。
- 当前发现：代码具备通用 task/policy/skill/primitive 骨架，中心坐标系生成脚本和 `toolset.end/ref` 参数入口已存在，但尚未承载 V1 感知结果契约、锅具 TCP 转换、底盘保持姿态协同和锅具 TCP 增量倾倒回放。
- 当前完成：`TASK-010` 为 Planner 增加私有 `PolicyDecision` 语义。旧 Policy 的 `PlannedStep`/`BimanualStep` 仍执行、旧 `None` 仍完成；新动态 Policy 可返回 `WAIT`，等待期间保留任务上下文、维持 IDLE、不发送机械臂 Action，并通过 `GetTaskStatus.current_phase` 暴露等待阶段。
- 当前完成：`TASK-011` 已建立 `pan_pour_params.yaml` 独立占位模板、launch 注入、Planner 私有参数快照及纯 SE(3) 转换模块。抓取和锅具 TCP 都按 `T_B_F = T_B_C @ T_C_TCP @ inverse(T_F_TCP)` 转为左臂 base 下法兰目标；未标定配置由 `configured: false` 拒绝执行。
- 当前完成（局部）：`TASK-012` 已实现并注册单个动态 `PanPourPolicy`。它不预生成完整轨迹，而是按 `_phase` 产生抓取、闭手、准备倾倒、倾倒接近等现有左臂步骤；配置、锅把、底盘、餐盘和回放能力未就绪时返回可观测 `WAIT`，不结束任务也不发送伪造动作。28 个定向测试、3 个受影响包构建、编译检查和 diff 检查通过。
- 当前完成（局部）：`TASK-013` 已新增纯离线的 V1 法兰增量轨迹模块。它强制版本、`spatial_only`、`flangeInBase`、米/弧度和 `xyz` RPY 约定，验证首个增量为 identity，并按 `T_current @ Delta_i` 展开绝对法兰航点；10 个定向测试通过。它尚未注册为 MotionExecutor Skill，也没有访问 Driver 或硬件。
- 感知路径已确认：正式复用 `ScenePerception → TaskPlannerNode._on_scene() → WorldState → PanPourPolicy` 路径 A；不新增老板电器专用感知 topic、PerceptionBridge 或第二套缓存。感知组仍需提供锅把抓取点/PCA 主轴、餐盘中心、source frame、有效性和新鲜度契约。
- 当前 V1 最小闭环以倾倒动作完成结束；放回锅具、张开灵巧手和恢复 home 已明确为后续扩展，不作为当前完成条件。
- 下一步：完整集成仍被三项外部能力阻塞：感知组 V1 字段契约、底盘组 ROS 生命周期接口、目标 robot_driver deb 的运行时位姿/MoveCartesian 语义和真实倾倒轨迹资产。中心和两个 TCP 的现场标定完成后，才可将 `pan_pour.configured` 设为 `true`。
- 旧版完整记录：`.project-log-legacy-20260728/`。
旧版完整记录：`.project-log-legacy-20260728/`。

## 2026-07-30 技术选型源码确认：坐标与回放边界

- `Pose3D`、`CartesianWaypoint` 的源码文档均定义为 `base frame`；`MotionExecutorNode._execute_motion_primitive()` 将航点原样填入 `MoveCartesian.Request.position/orientation`，服务没有 `frame_id`，因此 Executor 当前不能识别或转换机器人中心坐标系。
- 当前推荐：PanPourPolicy 继续在中心坐标系 C 下计算；Planner 在构造现有 `TaskTarget` 前完成 C→左臂 base B 转换；发送给 Executor 的笛卡尔目标统一解释为 `flangeInBase`。不新增 `FlangeMotionTarget`、`PourTaskTarget` 或独立 Action。
- 本地 SDK 适配器 `lbot_robot_xcore.py` 的 `move_to_pose_target()` 将输入命名为 `target_flan`，再通过 `_flange_to_end_pose()` 结合 toolset 转换；`_query_cartesian_pose()` 读取 `flangeInBase`。但实际 Driver 由 `VERSIONS.yaml` 锁定为外部 deb，当前机器未安装该 deb，不能把 SDK 源码视为目标运行时的最终证据。
- `GetArmPose.srv` 已在主仓库接口包中，但当前 MotionExecutor 没有创建该客户端；其注释写的是 TCP，而不同 Driver/SDK 实现存在 `endInRef` 与 `flangeInBase` 两种语义，因此相对回放前必须在目标 deb 上确认返回点和参考系。
- 倾倒回放推荐最小接入：Policy 发送现有任务信号/轨迹引用；Executor 内部 Skill/Adapter 读取 `flangeInBase` 增量轨迹，获取当前左臂法兰起点，计算 `T_current * Delta_i`，再通过现有 RobotDriver `MoveCartesian` 链路执行。禁止 Skill 直连 xCore；若 Driver 没有可靠当前法兰位姿入口，先做固定绝对轨迹验证，不宣称相对回放已可用。
- 问题 4 已解决：允许在 `robot_motion_executor` 中新增本子任务专用 Skill，复用现有 `ExecuteTask`、`MotionPrimitive` 和 `MoveCartesian` 执行链路；不修改公共 ROS 2 消息，不绕过 `RobotDriver`。剩余的是实现前验证：目标 Driver 是否提供可用的当前法兰位姿入口，以及其返回语义是否与轨迹的 `flangeInBase` 一致。
- 当前三个接口问题已全部被源码确凿回答：`MoveCartesian` 输入为法兰（`flangeInBase`）、`toolset.ref` 定义 SDK 中 `endInRef` 的参考坐标系原点、`get_arm_pose` 存在且返回法兰（`flangeInBase`）。不需要问架构组。新增 Skill 已确认可行。详见 current-session.md 2026-07-30 源码确认部分。
- 详细决策：`DEC-013`；此前新增公共 `FlangeMotionTarget` 的提案 `DEC-012` 已标记为 superseded。

## 本轮会话（2026-07-28）更新

- 用户回顾今日任务记录，确认 V1/V2 两版本路线，完成新一轮业务逻辑澄清
- 用户详细描述了 V1 完整流程状态机（handoff → scene-check → perceive → calc-grasp → move-left → close-hand → grasp-check(预留) → lift → base-move → calc-pour → pan-tcp-translate → pour-replay → return(TBD) → open → home）
- 新增确认：
  - 倾倒点公式：`pour_point_C = plate_center_C + pour_offset_C`（中心坐标系 C 下 xyz 三向可调偏置）
  - 抓取偏置沿锅把 PCA 主轴方向，定义在中心坐标系 C 下
  - 抓取 TCP/锅具 TCP 位姿参数化，代码已有 `toolset.end/ref` 入口
  - 倾倒采用锅具 TCP 局部坐标系录制动回放
  - V1 不加落料验收、异常处理和抓取确认，只打通动作流程
  - 放回/张手/home 后续确定，具体参数不阻塞流程骨架
- 用户批量回答了全部开放问题，所有阻塞项均解除
- 用户确认进入技术选型阶段
- TASK-007：done ✅；TASK-008：in-progress
- DEC-008（类型化 PourTaskTarget 方案）proposed，待用户批准
- 产品代码仍未修改
- 当前阶段：solution-research（技术选型）

## 源码学习进度（2026-07-29）

- 已沿 `TaskPlannerNode` 的真实源码读通第一段主链：`StartTask.srv → _on_start_task() → _prepare_start_task_context() → _clear_runtime_state() → _on_tick() → _generate_goal_by_task_type()`。
- 已理解 `TaskPlannerNode` 的工程角色：持有任务上下文和 Policy 实例，由 1 秒定时器驱动，使用状态/忙标志门控，再委托 Policy 产生步骤。
- 已区分 Planner 的全局运行状态、任务上下文、Action 等待标志和 Policy 的步骤状态，未将它们笼统称为一个状态机。
- 已理解 `PlannedStep → TaskTarget → ExecuteTask.Goal` 的消息构建链，并具体追踪 `test_gripper` 的“张开右手”示例。
- 已确认 `ExecuteTask.Goal` 是 `ExecuteTask.action` 自动生成的 ROS 2 Action 请求对象，`task_type` 是执行端路由键，`target` 是动作参数载荷。
- 已确认执行端路由：`goal.task_type="gripper_action" → _apis["gripper_action"] → GripperActionApi`。
- 新增可复习笔记：`.project-log/docs/source-code-learning.md`。
- 后续源码讲解采用“概念落到类/方法/变量/调用/具体值/下游效果”的方式，不只描述流程步骤。
- 用户确认最有效的讲解格式：先用具体任务按时间线串起真实运行过程，再用状态变量变化表说明变量生命周期，最后提炼 Orchestrator/状态机等工程思路；抽象概念不能替代源码实现。

## 可复用学习资产（2026-07-29）

- 已创建全局 Skill：`/home/tbl/.codex/skills/b-source-code-tutoring/`，用于以真实源码调用链、具体输入、状态变量生命周期和下游消费为主线讲解陌生代码。
- Skill 明确为显式触发：只有用户要求深入读源码、逐行讲解、追踪调用链或理解状态变量时使用；简短术语问题不自动展开成长教程。
- Skill 结构校验通过；评测样例记录于 `.project-log/evals/source-code-tutoring.yaml`，蒸馏依据记录于 `.project-log/distillation/candidates.yaml`。
- 后续 TaskPlanner、MotionExecutor 及其他仓库源码学习统一采用该方法；产品代码未修改。

## 技术选型发现：Policy 多阶段动态生成模式（2026-07-29）

- 源码分析发现：现有 Policy（TestGripper/TestHeart/PeelApple）均使用预生成步骤列表模式，但 BasePolicy 接口不强制预生成。
- V1 业务存在两段时序约束：锅把在任务启动时可感知，餐盘在底盘移动后才进入视野 → 无法一次预生成全流程。
- 确认采用"单个 PanPourPolicy + 内部 _phase 两段式"模式：
  - Phase 1（预生成）：从感知锅把位置计算抓取→提锅→底盘移动步骤
  - Phase 2（动态生成）：底盘移动完成后从 WorldState 读取餐盘位置，计算倾倒接近和增量回放步骤
  - 两阶段之间通过 hold_step（保持当前位姿的笛卡尔空转）等待感知更新
- 该模式不需要修改 Planner 路由、task_type 列表或 _initialize_policy。
- 决策 DEC-009 已记录到 .project-log/decisions/；架构记录已更新。
- 下一步：确认 WorldState 中餐盘检测结果的字段契约和感知组输出 Topic。

## 本轮会话（2026-07-29 第二轮）

- 应用户要求，完成了从 `__init__` 到 `_on_result` 的完整 9 阶段时间线串讲，覆盖整个 TaskPlannerNode 主循环。
- 串讲形式：真实运行时间线 → 关键变量生命周期表 → 工程思路总结；每个阶段都追踪了具体源码行号和变量值。
- 完整串讲记录已追加至 `.project-log/docs/source-code-learning.md`（307→842行），包含 9 阶段代码路径、11 变量×5 时间点的生命周期总表、四个属性层面划分和源码路径索引。
- 当前状态：TASK-008 仍在进行中，产品代码未修改。
- 待用户确认下一步方向：继续读 MotionExecutor 端 ActionServer 路由，还是切换阅读方向。

## 技术选型发现：参数配置模式（2026-07-29）

- 调查了现有代码库的参数管理方式，确认项目使用标准的 ROS 2 参数系统：
  - 参数 YAML 文件集中在 `dexbot_bringup/config/`，按子系统分目录管理
  - 通过 launch 文件的 `parameters=[config_path]` 传递给节点
  - 节点内部通过 `declare_parameter()` + `get_parameter()` 读取
- 当前 `TaskPlannerNode` 是唯一一个没有加载参数文件的核心节点，在 dexrob_full.launch.py 中裸启动，所有值硬编码在属性中。
- V1 参数（抓取偏置、等待位置、倾倒偏置、锅具 TCP、home 位姿等）可遵循现有模式：
  - 创建 `dexbot_bringup/config/pan_pour/pan_pour_params.yaml`
  - 在 `TaskPlannerNode.__init__()` 中声明对应参数
  - 在 launch 文件中为 task_planner_node 添加 `parameters=[pan_pour_config]`
- 参数可设计为分层命名空间，如 `pan_pour.grasp_offset`、`pan_pour.lift_pose.position` 等，解析方法由 Policy 或 Node 内部负责，不影响现有 Node 架构。
- 当前发现已记录，待进入 engineering-landing 阶段后再实现，不修改产品代码。

## 技术选型初步确认（2026-07-29）

- 选型 2：采用单个 `PanPourPolicy` + 内部 `_phase`，根据 `WorldState` 动态生成阶段步骤。
- 选型 3：所有业务目标和中间位姿统一在机器人中心坐标系 C 下计算，执行适配层再转换到机械臂/RobotDriver 坐标系。
- 选型 4：单目标/单原子动作复用现有 API/MotionPrimitive；需要拆解多个原语的复杂动作才使用 Skill。
- 选型 5：底盘接口暂定，等待底盘组提供准确 action/service 消息后再定，不阻塞机械臂流程选型。
- 选型 6：技术参数采用 ROS 2 YAML 配置，通过 launch 注入，禁止在 Policy 内硬编码。
- 选型 1 的接口承载方案暂时搁置；选型 7 的锅具 TCP 局部增量轨迹回放方案下一步单独讨论。
- 已新增 `DEC-010`；当前仍处于 `solution-research`，产品代码未修改。

## 选型 7 初步分析（2026-07-29）

- 当前 `PathRecordSkill` 负责录制命名路径，`xcore_path_client` 调用控制器 `startRecordPath/stopRecordPath/saveRecordPath`，回放工具调用控制器 `replayPath(name, rate)`。
- 现有代码没有路径点、frame、TCP 引用和相对坐标语义，不能直接证明控制器保存的是锅具 TCP 局部增量轨迹。
- 选型 7 暂不定案；候选为控制器直接回放、显式锅具 TCP 相对轨迹文件 + 适配器、控制器原生相对回放适配器。
- 推荐先做最小 replay spike：用两个不同锅具 TCP/基准位姿验证同一路径是否随 TCP 变化，并验证 driver 占用、取消和反馈。

## 选型 7 现成方案评估（2026-07-29）

- 已检查 `/home/tbl/Project/cucumber/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo/scripts/flange_motion_editor` 的采集、处理、增量计算和回放源码。
- 该方案的核心是显式 YAML 空间轨迹和 `Delta_i = inverse(T0) @ Ti`、`T_current @ Delta_i` 的 SE(3) 增量回放，适合作为 V1 轨迹资产基础。
- 当前文件和代码明确使用 `flangeInBase`，局部原点是录制开始时的法兰；但锅具抓取后与法兰刚体连接，因此法兰增量轨迹可以直接复现锅具的刚体运动，不需要逐点转换成锅具 TCP 增量。
- 当前脚本通过 xCore/LbotRobot 直连并要求停止对应 xcore 控制节点，不能绕过在线 `robot_driver` 直接放进正式运行链路。
- 结论：选型 7 推荐“复用法兰增量算法和文件格式 + 在 `robot_motion_executor` 内新增相对轨迹回放适配器”，属于 `wrapper-adapter`，不是直接运行脚本或直接复用现有 `PathRecordSkill`。
- 适配器主要负责根据锅具 TCP 目标计算法兰起始位姿、中心坐标系 C 到执行坐标的转换、RobotDriver 路径调用、速度/加速度/限幅、取消、超时和结果反馈。
- 关键修正：锅具 TCP 不需要参与每个轨迹点的重新表达；只要法兰与锅具保持刚体连接，并把回放起点对齐到期望锅具 TCP 起点，法兰轨迹即可带动锅具完成预期动作。
- 已新增 `RES-003` 和 `DEC-011`；`DEC-011` 在用户批准前保持 `proposed`，产品代码未修改。
- 下一步：做最小 replay Spike，验证 TCP 变换、姿态/单位约定、路径接口和 driver 独占连接边界。

## 2026-07-30 toolset.end 冲突风险确认与 DEC-014

- 源码确认了 `toolset.end` 的完整传输链路：`robot_params.yaml` → `luoshi_arm.initialize()` → `setToolset()` → 物理机器人控制器 → `_sync_toolset_from_robot()` → `_flange_to_end_pose()` 转换
- 确认若其他子任务修改 `toolset.end` 为非 identity，会导致本子任务的 flange 目标被不正确转换
- 决策 DEC-014：`toolset.end` 保持 identity，本子任务的 TCP 参数自管理在 `pan_pour_params.yaml`，Planner 层完成 TCP→法兰反解
- 当前按单人任务模式推进，多人协作配置冲突风险已记录，后续评估
- TASK-008 仍在进行中；DEC-014 active；产品代码未修改

## 2026-07-30 技术选型完成

- 用户确认 DEC-013（复用 ExecuteTask，内部法兰约定）和 DEC-011（法兰增量轨迹适配复用路线）
- 全部 12 个决策已确认，技术选型阶段完成
- solution-research → engineering-landing 阶段切换
- 用户要求：技术参数留空占位，先不开始写代码
- TASK-008 完成 ✅
- 产品代码仍未修改
