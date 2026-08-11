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

## 2026-08-11 PanPourPolicy 等待阶段改为私有 wait 占位

- 背景：`PanPourPolicy` 在多处外部依赖未就绪时返回 `None`，`TaskPlannerNode` 将 `None` 视为任务完成并清空 active task，构成误判完成 BUG。
- 选择方向 2 而非恢复公共 `PolicyDecision/WAIT`：等待阶段返回任务私有 `pan_pour/wait` 动作；`PanPourSkill` 返回空原语，Planner 正常走一次 Action 往返后继续 tick。
- 约束：wait 动作成功不得推进阶段，真正推进仍由 `update_handle_detection` / `update_plate_center` / `update_base_positioned` 等外部数据变化触发。
- 验证：主线定向 21 passed；执行器定向 42 passed；两仓库 `compileall`、`colcon build` 均通过。
- 后续：底盘/视觉接口落地后可迁移到方向 1，将各等待占位替换为真实调用或动作。

## 2026-08-03 临时拖动示教路径工程规格

- 正式感知和底盘路径暂缓，新增 `TASK-016` 固定工位临时测试路径。
- 用户已确认：全程左臂；拿锅=移动轨迹+闭手；端锅、倾倒、放锅各自独立轨迹；灵巧手动作复用 `gripper_action`。
- 已完成工程规格：`.project-log/specs/TASK-016.md`。
- 计划链路：`StartTask(teach_pan_pour) → TeachPanPourPolicy → ExecuteTask(path_replay/gripper_action) → MotionExecutor → 控制器命名路径回放`。
- 回放能力当前通过 xCore 控制器接口实现，需单独新增 `PathReplaySkill` 和 `REPLAY_RECORDED_PATH` 执行分支；同一左臂不能与 `robot_driver` 并发控制。
- 当前不写产品代码；下一步先确认放锅后张手时序，然后进入 Mock/单元测试设计，再实施两个仓库的最小代码改动。

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
## 2026-08-03 手眼标定使用分析

- 已对照主仓库 `kitchen_robot_home/src/dexbot_bringup/launch/calibration.launch.py` 与 715 参考仓库的 `hand_eye_calibration_node.py`、`aruco_detector_node.py`，确认现有流程是：相机发布图像与内参 → ArUco 发布 `/aruco/pose` → 标定节点读取 `/robot_driver/get_arm_pose` 的末端位姿 → 自动移动到候选笛卡尔位姿 → 等待 ArUco 稳定 → 记录样本 → 计算并保存 `T_base_cam`。
- 已确认标定服务：`/calibration/start_calibration`、`/calibration/auto_calibrate`、`/calibration/stop_calibration`；推荐使用 `start_calibration`，其内部等价调用自动标定。
- 已确认标定节点依赖：ArUco 标记必须刚性安装在被标定机械臂末端，摄像头保持固定；算法求解的是 eye-on-base 约束 `T_base_tcp_i @ T_tcp_marker = T_base_cam @ T_cam_marker_i`。
- 已确认消息语义：`GetArmPose.srv` 注释写 TCP，但 715 Driver 实现最终调用 SDK `flangeInBase`；标定样本实际应视为法兰位姿，结果 `T_base_cam` 表示相机坐标到标定时机械臂 base 坐标的变换。
- 发现运行前风险：`calibration.launch.py` 将相机节点放入 `camera1` namespace，但 ArUco 节点仍硬编码订阅 `/camera/color/image_raw` 和 `/camera/color/camera_info`，未像 `dexrob_full.launch.py` 一样提供 remap；启动后必须用 `ros2 topic list/info` 验证，不能直接假设可用。
  - 后续修订（2026-08-07，CAL-02）：安装 1.0.0 后核对实际源码，`CameraDriverNode` 以绝对话题 `/camera/color/image_raw`、`/camera/color/camera_info` 发布，绝对话题不受 `camera1` namespace 影响，ArUco/viewer 默认订阅与之一致；此风险在 1.0.0 上实际不成立，无需改 remap。真机仍按 topic list/info 复核。
- 发现参数必须按实际标定板确认：主仓库默认 `marker_length=0.13`、`DICT_6X6_250`，715 默认 `0.038`、`DICT_4X4_50`，不能照抄。当前未启动真机标定、未修改产品代码。
- 下一步：先确认实际 ArUco 标定板边长/字典，并在真机启动后核对 `/camera.../image_raw`、`/camera.../camera_info`、`/aruco/pose` 与 Driver 服务，再执行单臂自动标定；双臂结果完成后再运行中心坐标系生成脚本。

## 2026-08-03 临时轨迹 ROS 链路确认

- 用户确认临时示教路径采用现有 ROS 链路：`Policy → ExecuteTask(task_type=path_replay) → MotionExecutor → PathReplaySkill → REPLAY_RECORDED_PATH → replayPath()`。
- 轨迹录制继续复用现有 `path_record` 与 `PathRecordSkill`；路径名称通过 `TaskTarget.object_id` 传递，轨迹实际保存于左臂控制器内部。
- 该方案不修改 `ExecuteTask.action`、`TaskTarget.msg` 或正式 `PanPourPolicy`；需要新增的范围仅限临时 Policy、回放 Skill 注册和 MotionExecutor 回放分支。
- 仍需保持同一左臂的 xCore/robot_driver 控制连接独占；当前尚未开始实现或真机验证。
- 决策已记录为 `DEC-018`。

## 2026-08-03 左臂调试连接参数

- 用户确认当前调试地址映射：左臂 `192.168.2.159`，右臂 `192.168.2.160`。
- 已同步修改 `kitchen_robot_home/src/dexbot_bringup/config/robot_driver/robot_params.yaml`、`robot_motion_executor/src/dexbot_motion_executor/dexbot_motion_executor/motion_executor_node.py` 和 `robot_motion_executor/src/dexbot_motion_executor/dexbot_motion_executor/skills/path_record.py`。
- YAML 解析校验通过；硬件网络与 ROS 启动验证待现场执行。

## 2026-08-03 最小拖动录制/回放 ROS 链路

- 已新增 `PathReplaySkill`，实现 `path_replay → REPLAY_RECORDED_PATH → xCore replayPath()`；`path_record` 继续复用既有 Skill。
- 本轮只通过现有 `ExecuteTask` Action 直接调用 MotionExecutor，未新增/修改公共 Action、消息、正式 `PanPourPolicy` 或感知/底盘链路。
- xCore 路径由控制器内部保存，路径名使用 `TaskTarget.object_id`；当前左臂控制器地址为 `192.168.2.159`。
- 执行器包构建通过；新增回放参数/原语单测 4 项通过。全量包测试被本机 pytest/anyio 版本冲突阻断，已记录为验证环境限制。
- 真机验证待执行，前提是停止 `robot_driver` 对左臂的占用，只运行 `motion_executor_node` 后再经 ROS Action 录制/回放。

## 2026-08-03 xCore SDK 路径定位修复

- 首次真机录制在 SDK 目录定位阶段失败，未建立控制器连接或下发运动。
- 根因是 `xcore_path_client.py` 只支持旧的 `src/dexbot_robot_driver/.../sdk` 布局，而当前 SDK 实际位于 `kitchen_robot_home/src/sdk/...`。
- 已扩展为兼容两种目录布局，并在当前工作区实际定位成功；执行器重新构建通过，相关定向测试 5 项通过。
- 下一步是重启 MotionExecutor 后重新发送同一条 `path_record` Action，继续真机最小闭环验证。

## 2026-08-03 左臂最小路径录制真机验证

- `path_record` 已经通过真实 ROS Action 链路完成验证：`ExecuteTask → MotionExecutor → PathRecordSkill → xCore`。
- 左臂控制器 `192.168.2.159` 内已保存路径 `pan_pour_smoke_001`；`queryPathLists` 可见该路径。
- 所有关键 SDK 操作均返回 `ec=0`，Action 返回 `success=true`、`SUCCEEDED`；单臂运行时 `dual_arm_result` 中的 false 字段不适用。
- 下一步为真机低风险回放该短路径，验证 `path_replay` 链路。

## 2026-08-03 replayPath 起点行为核查

- 应用代码和 SDK 示例均只执行 `replayPath(name, rate)` 后调用 `moveStart()`；没有显式“回到录制起点”的运动指令。
- SDK 声明未定义自动回起点语义，因此此行为目前只能标记为控制器固件未知项，不能作为流程假设。
- 需要通过空载短路径的真机观察确认回放是否自动过渡到起点；验证前始终保持急停可达和工作空间清空。

## 2026-08-03 replayPath 真机起点行为与速率配置

- 真机观察确认：当前左臂控制器执行回放时，会先自动回到录制路径起点，再进行轨迹回放；该项作为控制器固件观察记录，不扩展为未经验证的 SDK 通用保证。
- 新增 MotionExecutor 参数 `path_replay.rate` 和 `path_replay.wait_timeout_sec`，分别控制控制器回放倍率与等待超时；默认值为 `1.0`、`120.0`。
- SDK 规定速率范围 `(0, 3)`，其中 `1.0` 为原始录制速度；调试建议从 `0.5` 开始，避免使用大于 `1.0` 的速率。
- 执行器重新构建通过，定向测试 6 项通过。

## 2026-08-03 正规 launch 启动阻塞诊断

- `motion_executor_node` 已正常启动并注册 `path_record`、`path_replay` 等 Skills 以及灵巧手服务客户端。
- `task_planner_node` 启动失败：用户级 NumPy `2.2.6` 与系统/ROS OpenCV 二进制 ABI 不匹配，错误为 `_ARRAY_API not found` / `numpy.core.multiarray failed to import`。
- `robot_driver_node` 启动失败：工作空间根目录缺少 `.localconfig`，私有 Driver 需要 `lbot_sdk_path` 和 `xcoresdk_sdk_path`，因此所有 `/robot_driver/*` 服务均不可用。
- 灵巧手 Action 测试的 `GripperAction service not available` 是 Driver 崩溃后的级联错误，不是灵巧手控制参数错误。
- 当前优先级：配置并验证 `.localconfig` → 正规 launch 确认 `/robot_driver/hand/*` 和 `/robot_driver/gripper_action` → 再处理 Planner 的 NumPy/OpenCV 环境冲突。

## 2026-08-03 启动配置修复完成（剩余硬件阻塞）

- 已修复 `.localconfig`：Lbot SDK、xCore SDK、灵巧手动作配置目录均可被私有 Driver 读取。
- 已修复 xCore SDK 路径层级错误：配置指向 `Release/linux` 父目录后，Driver 成功导入 SDK、匹配 `xMateErProRobot`，并连接左右控制器。
- 已修复 Planner 的 NumPy/OpenCV ABI 冲突：正规 launch 为 Planner 设置 `PYTHONNOUSERSITE=1`；Planner 已正常初始化。
- 正规 launch 验证未发现节点崩溃；当前剩余问题为 CAN 硬件/接口状态：`can1` 不存在，`can0` 为 `DOWN/STOPPED`。灵巧手动作配置已加载，但尚未验证真实手部动作。

## 2026-08-03 CAN 左右手映射调整

- 已将左手 CAN 通道改为 `can0`，右手 CAN 通道改为 `can1`。
- `dexbot_bringup` 已重新构建，源配置与安装配置一致；待重新启动正规 launch 后验证 Driver 日志和灵巧手实际通信。

## 2026-08-03 灵巧手 Linkerbot SDK 配置修复

- `can0` 已确认正常拉起；新的 `hand对象为None` 根因是 `.localconfig` 缺少 `linkerbot_sdk_path`，不是 CAN bitrate 或接口 UP 状态。
- 已增加本地 Linkerbot SDK 路径并验证 `linkerbot.O6` 可导入、可构造；需要重启正规 launch 后重新测试左手。
- 当前仅左手 `can0` 进入测试范围；右手 `can1` 缺失仍为独立硬件问题。

## 2026-08-03 灵巧手角度与力矩控制验证完成

- 左手 `arm=0` 的角度设置、角度读取、力矩上限设置、力矩读取均测试成功。
- 已验证 ROS Service、RobotDriver、O6Hand、Linkerbot SDK、SocketCAN `can0` 到左手硬件的完整控制链路。
- 左手灵巧手基础控制验证完成；右手 `can1` 仍待独立硬件准备后测试。

## 2026-08-03 完整示教流程阶段启动

- 目标：采集左臂完整示教资产，并实现独立复合 Skill 串联机械臂路径与灵巧手动作。
- 计划路径资产：`pick_approach`、`carry_to_pour`、`pour`、`place`；必要时补充 `return_home`。
- 手部动作：抓取阶段闭合，放置阶段张开；优先复用已验证的 `gripper_action`/`set_angles` 服务，不把手部动作硬编码进机械臂轨迹文件。
- 当前阶段先冻结轨迹起止姿态和动作契约，再逐段录制、单段回放验证，最后实现串联 Skill 与完整真机验收。

## 2026-08-03 示教复合流程目标已记录并暂停

- 已记录完整示教流程的路径资产、灵巧手动作边界和复合 Skill 顺序。
- 用户要求暂不继续该路线，当前状态为 `planned / paused`；后续可从第一段 `pan_pick_approach_001` 的录制继续。

## 2026-08-05 相机调试进度与环境问题记录

- 设备已识别为 `Orbbec Gemini 336L`，序列号 `CPCAC53000FP`；`pyorbbecsdk2==2.0.18` 原始采集测试通过，ROS 相机驱动在隔离 Python 环境下能发布 `/camera1` 彩色、深度和相机内参话题。
- 已把 `camera1_params.yaml` 从 RealSense D435 切到 Orbbec `gemini335l`，填入当前设备内参占位值；该改动会影响默认 `camera1` 配置，上线/标定前需要复核。
- 环境阻塞已定位：用户目录 NumPy `2.2.6` 与 ROS OpenCV 所用 NumPy 不兼容；临时用 `PYTHONNOUSERSITE=1` + 隔离 Orbbec SDK 路径绕过，尚未固化为正规 launch/仓库级依赖。
- 下一步：等用户确认是否实施仓库内 SDK 依赖与 launch 环境隔离；随后复核 `camera1` 默认配置。

## 2026-08-05 本机 Orbbec 相机调试环境落地方案

- 已恢复团队默认 RealSense；Orbbec 使用 `/home/tbl/.local/bin/launch_orbbec_camera.sh` 本机脚本启动，所有环境隔离在仓库外。
- 已建立本机参数 `/home/tbl/.local/share/boss_electrics/camera1_orbbec_local.yaml`，不进入团队仓库提交。
- 验证通过：真实 Orbbec 相机可启动，发布 `/camera/color/image_raw`、`/camera/depth/image_raw`、`/camera/color/camera_info`，内参与之前实测一致。
- 后续本机相机测试统一走 `launch_orbbec_camera.sh`；如果团队决定默认换成 Orbbec，再另行作为团队配置变更处理。

## 2026-08-05 项目级 AGENTS.md 建立

- 已根据主线 `DEVELOPER_GUIDE.md`、`README.md` 和 `SKILL.md`，在项目根目录新增 `AGENTS.md`。
- 已固化当前项目规则：主线/执行器仓库边界、`.deb` 黑盒边界、ROS 环境加载规则、禁止 source 其他项目备份工作空间、相机配置和标定流程、Policy 开发规范、验证纪律及 Git 修改纪律。
- 未修改 `kitchen_robot_home` 或 `robot_motion_executor` 业务代码；两个仓库原有未提交改动保持不变。

## 2026-08-05 RobotDriver 连续轨迹与 RT 跟随能力核查

- 当前 ROS `robot_driver_node` 对外提供的机械臂关节接口仍是 `/robot_driver/move_joints`，对应 `MoveJoints.srv`；一次请求只携带一个 `target_joints`，Driver 回调调用 `control_arm_joint()` 并等待该点动作完成。
- `O6Luoshi` 当前实际走 `LuoshiArm.control_joint()`，内部固定切换到 `NrtCommandMode`，创建单个 `MoveAbsJCommand`，执行 `moveAppend()`、`moveStart()` 后等待完成；因此现有 ROS Driver 路径不支持按 JSON 时间序列连续流式回放，逐点调用会产生卡顿。
- 工作空间 SDK 适配器 `lbot_robot_xcore.py` 确实实现了 `joint_follow()`、`FollowPosition_7` 初始化和 `RtCommandMode` 切换；环境变量 `DEXBOT_XCORE_RT_FOLLOW=1` 才会尝试启用，且 `_is_rt_follow_robot_compatible()` 只对控制器型号包含 `xMate` 的设备放行，否则回退到非实时短 `MoveAbsJ` 指令。
- 该 SDK RT 跟随能力目前没有在当前 `/opt/ros/humble` 安装的 `dexbot_robot_driver` ROS 服务、Action 或 Topic 中暴露；当前 Driver 的 `O6Luoshi` 适配器也没有调用 `joint_follow()`。因此“底层 SDK 支持 RT”不能等同于“现有 robot_driver 节点支持 RT”。
- 结论：当前框架可以单点运动和控制器命名路径回放，但不能通过现有 `MoveJoints` 服务平滑连续回放 JSON 轨迹；RT 实时模式在底层 SDK 有实现，但在当前 ROS Driver 链路中尚未接入，尚未具备可直接调用的公共接口。
- 对 `TeachPanPourSkill` 的直接影响：不应逐点循环调用 `/robot_driver/move_joints` 作为正式连续轨迹方案。优先需要 Driver 提供批量关节轨迹或 RT follow 接口；在接口未提供前，保留控制器原生 `replayPath()` 或将直接 xCore 连接仅作为临时、单一控制权的测试回退。
- 证据范围：工作空间 SDK 源码和已安装 Driver Python 源码静态核查；未在当前机器人上打开 `DEXBOT_XCORE_RT_FOLLOW`，未完成 RT 真机安全验证。

## 2026-08-05 TeachPanPourSkill 本地轨迹与短生命周期 SDK 方案确认

- 用户确认不复用 `PathReplaySkill`：该 Skill 的语义是按路径名调用控制器内部保存的 `replayPath()`，而本任务的倾倒和放锅轨迹是随 `TeachPanPourSkill` 保存的本地 JSON 文件，两者资源语义不同。
- `TeachPanPourSkill` 对固定点位和灵巧手动作继续复用现有 `robot_driver` 接口；只有 `pour_replay`、`put_replay` 两个阶段读取 Skill 内部 JSON，并在 Skill 内建立短生命周期 xCore SDK 连接。
- 本地轨迹执行不逐点调用 `/robot_driver/move_joints`。Skill 一次性读取并校验轨迹，构造多个 `MoveAbsJCommand`，为中间点设置 blend zone、最后点设置 zone=0，通过 `moveAppend()` + `moveStart()` 批量执行，等待完成后在 `finally` 中断开 SDK。
- JSON 时间戳用于保持顺序、校验采样周期和记录轨迹时长；当前方案不承诺严格逐点复现原始时间，而是依赖批量 MoveAbsJ、速度参数和控制器内部平滑执行。
- 运行约束：回放期间不调用 `robot_driver` 的机械臂控制接口，不启动其他左臂动作；回放结束后释放 xCore 连接，再恢复 Driver 点位控制。当前不增加互斥锁，依靠固定阶段串行流程和运行纪律保证控制权不重叠。
- `TeachPanPourPolicy` 的技术参数（包括点位速度、轨迹速度、blend zone、超时等）继续放在 Policy 自有目录的参数文件中，由 Policy/同任务组件内部加载；不放入全局 `robot_params.yaml`，不依赖当前工作目录，也不散落到 Planner 或 Driver 配置中。
- 后续实现顺序：先完成 Skill 内部资源加载与批量 xCore 轨迹执行，再接入 `TeachPanPourPolicy` 阶段路由，最后做 Driver → xCore 回放 → Driver 的最小真机切换验证。

## 2026-08-05 TeachPanPourSkill 首轮代码落地

- 已实现临时固定工位流程 `teach_pan_pour`：`home_open → move_to_grasp_ready → close_gripper → move_to_lift → move_to_pour_ready → pour_replay → put_replay → open_gripper → return_home`。
- Planner 新增独立 `TeachPanPourPolicy`，按阶段一次只下发一个 `ExecuteTask.Goal`；阶段结果为 `COMPLETED` 后才推进，失败不会静默跳过。
- MotionExecutor 新增独立 `TeachPanPourSkill`，固定点位使用现有 `MoveJoints`，灵巧手使用现有角度/力矩服务，倾倒和放锅读取 Skill 内部 JSON 资源。
- 本地轨迹执行使用短生命周期 xCore：批量创建 `MoveAbsJCommand`，中间点使用 blend zone，最后点 zone 为 0，通过 `moveAppend()`、`moveStart()` 执行，轮询结束后在 `finally` 断开连接；不逐点调用 ROS `MoveJoints`。
- 已补充 xCore 批量执行 mock 测试，覆盖分批追加、最终点 zone、速度参数、`moveStart` 和异常断开；已修正 Skill 的标准 `json` 导入。
- 验证通过：执行器定向测试 5 项、Planner 定向测试 8 项；`dexbot_task_planner` 和 `dexbot_motion_executor` 分别构建通过；两仓库 `git diff --check` 通过。
- 测试期间发现本机系统 pytest 与用户目录 `anyio` 插件版本冲突，使用 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` 禁止无关插件；未修改项目 Python/ROS 环境，也未将摄像头环境问题引入本任务。
- 当前状态：`implemented-unverified`。尚未验证真实 Planner → MotionExecutor Action、Driver 与 xCore 控制权切换、两段轨迹真机安全性、灵巧手动作时序；未执行 commit 或 push。

## 2026-08-05 teach_pan_pour 灵巧手角度类型错误修复

- 真机日志确认机械臂第 0 个 `MOVE_JOINTS` 已成功，失败发生在第 1 个 `SET_HAND_ANGLES` 原语构造 ROS Service 请求时，与 CAN、机械臂连接和任务规划重试无关。
- 根因是 `hand_presets.yaml` 中存在整数角度/力矩值；`SetHandAngles` 和 `SetHandTorques` 的 ROS `float64[]` Python 消息 setter 要求每个元素必须是 Python `float`。
- 已在 `robot_motion_executor/src/dexbot_motion_executor/dexbot_motion_executor/motion_executor_node.py` 的 ROS 消息边界，将角度和力矩统一转换为 `float`。
- 验证通过：执行器 `compileall`、执行器包构建、直接 ROS 消息赋值和 `git diff --check`；`pytest` 因当前环境没有可用命令未执行。
- 尚未完成重启后的真实 `teach_pan_pour` 完整闭环，因此状态保持 `implemented-unverified`；复测前必须重新 source 执行器 `install/setup.bash`。

## 2026-08-05 TeachPanPourSkill 点位速度调整

- 按用户要求，将 `TeachPanPourSkill` 的固定点位 `point_speed` 从 `0.15` 调整为 `0.5`，对应 Driver 内部约 50% 速度。
- 本地 JSON 轨迹回放的 `trajectory_speed` 仍为 `0.4`，对应批量 xCore 轨迹执行的 `speed_scale=0.4`；本次未修改轨迹速度。
- 执行器包已重新构建通过；重启 launch 前必须重新 source 执行器安装空间，运行中的旧节点不会自动加载新参数。

## 2026-08-05 LOCAL_JOINT_TRAJECTORY 事件循环错误修复

- 真机日志显示固定点位和灵巧手阶段已成功，失败发生在 `pour_replay` 的 `LOCAL_JOINT_TRAJECTORY` 原语，错误为 `no running event loop`。
- 根因是 `MotionExecutorNode` 在 `rclpy` Action 异步回调中调用 `asyncio.to_thread()`；当前 `rclpy` 执行器不提供标准 `asyncio` 事件循环，而现有 `path_record` 已采用同步 xCore 调用模式。
- 已移除该处 `asyncio.to_thread()`，改为直接同步调用 `execute_local_joint_trajectory()`；异常仍由当前原语处理逻辑捕获并返回失败。
- 执行器 `compileall`、`colcon build --symlink-install --packages-select dexbot_motion_executor` 和 `git diff --check` 通过。
- 旧任务已经重试 3 次并进入 `error`，不能自动恢复；必须停止当前 launch、重新 source 执行器安装空间并重新启动后再发起任务。同步轨迹执行期间需保持急停可达。

## 2026-08-05 TeachPanPourSkill 点位速度调整为 1.0

- 按用户要求，将固定点位 `point_speed` 从 `0.5` 调整为 `1.0`，Driver 内部对应 `100%` 速度上限。
- 本地 JSON 轨迹 `trajectory_speed` 仍保持 `0.4`，本次未修改轨迹回放速度。
- 执行器包重新构建通过；重新启动前必须 source `/home/tbl/Project/boss_electrics/robot_motion_executor/install/setup.bash`，运行中的节点不会自动加载新值。
- `1.0` 已接近当前 Driver 的速度上限，实机测试必须保持急停可达并先观察第一段点位运动。

## 2026-08-05 TeachPanPourSkill 真机执行成功

- 用户反馈将固定点位速度调整为 `1.0` 后，`teach_pan_pour` 流程执行成功。
- 本次现场运行已覆盖此前失败点：灵巧手角度/力矩请求、固定点位运动和本地 JSON 轨迹回放均不再触发之前的类型错误或 `no running event loop` 错误。
- 已确认运行时需要重新构建并 source 执行器安装空间；当前固定点位速度为 `1.0`，本地 JSON 轨迹回放速度仍为 `0.4`。
- 真机成功证据来源为用户现场运行反馈；未取得完整逐阶段日志和独立安全验收记录，因此 `TASK-016` 保持 `in_progress`，完整闭环证据仍需后续整理。

## 2026-08-05 TeachPanPourSkill 抓锅拇指实际目标调整

- 真机日志显示抓锅时拇指目标 `0°` 受锅具实体阻挡，实际约停在 `31°`，超过 Driver 固定 `15°` 到位容差，导致 `SetHandAngles` 失败并触发任务重试。
- 已将 `robot_motion_executor/src/dexbot_motion_executor/dexbot_motion_executor/skills/teach_pan_pour/resources/hand_presets.yaml` 的 `grasp_pan.angles` 从 `[0, 88.5, 17, 14, 15, 16]` 调整为 `[30, 88.5, 17, 14, 15, 16]`；其余关节和 `torques=100` 保持不变。
- 执行器包重新构建和 `git diff --check` 通过。重新启动前需 source 执行器安装空间；首次抓锅测试必须保持急停可达并观察锅具是否稳定。

## 2026-08-05 倾倒轨迹提前返回与连续回放崩溃修复

- 用户现场观察确认：`pour_replay` 刚开始倾倒即停止，日志随后显示 `LOCAL_JOINT_TRAJECTORY completed`；不能据此认定 437 点、约 9.16 秒轨迹已完整执行。
- 根因是本地轨迹执行器把 `operationState()` 返回值转换成字符串后与错误的状态名比较，导致运动尚未完成时被误判为结束；随后立即建立 `put_replay` 的第二个 xCore 连接，控制器仍在运动时触发原生 SDK `terminate called without an active exception`，导致 MotionExecutor `SIGABRT`。
- 已修正 `local_joint_trajectory_client.py`：直接比较 SDK `OperationState.idle/unknown` 枚举；必须先观测到非 idle 运动状态，再接受 idle/unknown 作为完成；若启动后 2 秒未进入运动状态则报明确错误。
- 定向测试 `test_local_joint_trajectory_client.py` 通过（2 passed），执行器包构建、`compileall` 和 `git diff --check` 通过。
- 真机尚未复测修复后的完整倾倒/放锅连续流程；下一步必须重启执行器并低风险复测 `pour_replay`，确认约 9 秒后才进入 `put_replay`。

## 2026-08-05 倾倒轨迹中途停止的末点验收增强

- 用户再次确认：第一段 `pour_replay` 仍在倾倒开始后中途停止，不能依据 `LOCAL_JOINT_TRAJECTORY completed` 日志认定轨迹完整执行。
- 已在 `local_joint_trajectory_client.py` 增加末点关节验收：检测到控制器从运动状态回到 `idle/unknown` 后，读取 `jointPos()`，只有所有关节距 JSON 最后点最大误差不超过 `0.03 rad` 才返回成功。
- 若控制器中途停止，MotionExecutor 将返回 `trajectory stopped before final point` 并打印各关节误差，不再错误进入下一阶段；这一步用于获得真实失败证据，尚未证明控制器中途停止的硬件/SDK根因。
- 定向测试 2 passed，执行器包构建、`compileall` 和 `git diff --check` 通过；真机需重启后复测并提供新的末点误差日志。

## 2026-08-05 倾倒轨迹 6 秒停止原因取证

- 用户明确要求先查清 `pour_replay` 约 6 秒停止的控制器原因，不接受把现象归因于 `put_replay` 或继续盲改参数。
- 静态核查确认：倾倒 JSON 包含 437 个关节点，末点时间约 9.158 秒；执行器当前构造全部 437 个 `MoveAbsJCommand`，按每批 50 点调用 `moveAppend()`，且每批错误码为 0 才继续。旧日志没有队列容量、实际 waypoint、控制器错误备注，因此不足以判断是入队不完整还是控制器中止。
- xCore 官方示例确认 `moveExecution` 事件提供 `ID`、`ReachTarget`、`WaypointIndex`、`Error`、`Remark`；当前 SDK 日志只看到 `moveStart end (0)`，未记录这些事件字段。
- 已在执行器本地轨迹客户端增加诊断：注册/清理 `moveExecution` watcher，记录 waypoint/error/remark；逐批记录接受的点索引和 command id；记录 `operationState` 状态变化；控制器回 idle 时查询最终事件。未改变轨迹点、速度、批量大小或运动控制流程。
- 验证：执行器定向测试 `2 passed`；`python3 -m compileall -q src/dexbot_motion_executor` 和 `git diff --check` 通过。当前真机根因仍为 `implemented-unverified`，必须重启并采集带事件字段的新日志后定性。
- 现场判据：若最后事件 `WaypointIndex` 在约 6 秒对应中间点且 `Error/Remark` 非空，是控制器主动停止或安全/命令错误；若只记录到部分批次接受，则是入队问题；若 437 点均接受但事件在中间点停止且无错误，需要继续查队列或批量接口限制及 `MoveAbsJCommand` 参数语义。

## 2026-08-05 倾倒轨迹重复回放根因确认

- 用户现场确认：倾倒轨迹已经完整执行过，但随后又重复执行倾倒；重复不是 `put_replay` 轨迹映射导致，而是同一个 `pour_replay` 阶段被 Planner 重试。
- 直接证据：本次执行 437 点被分成 9 批，每批 50 点（末批 37 点），控制器事件最终停在 `cmdID=absj#5`、`wayPointIndex=49`，对应全局第 `5*50+49=299` 号点；`operationState` 已回到 idle，事件错误为 `ec=0`，但末点校验误差最大 `1.3251 rad`，因此执行器返回 `trajectory stopped before final point`。
- 同一任务随后在约 1 秒后再次发送 `pour_replay`，第二次仍停在 `absj#14`、`wayPointIndex=49`，再次返回相同末点误差；第三次同样进入 `pour_replay`。这与 Planner 的失败重试逻辑完全一致，不是 Policy 把 `put_replay` 错发成 `pour_replay`。
- 控制器实际只执行到第 300 个航点，虽然 9 次 `moveAppend` 都返回 `ec=0`；因此当前 xCore 批量入队接口存在约 300 个航点的有效执行上限或队列语义限制，超出部分未被执行。`moveAppend` 返回成功不等于所有追加航点最终执行。
- 根因分类：`technical-selection`/`implementation`。当前实现把 437 点一次性追加，超过控制器有效队列容量；Planner 的重试行为是对执行器失败结果的正常响应，但在轨迹只执行前缀的情况下会重复执行同一前缀。
- 未修改业务阶段顺序。正确修复方向是把 437 点拆成不超过控制器容量的连续段（例如 300+137），每段等待真实末点到位后再执行下一段；不能通过关闭末点校验或把失败伪装成成功解决。

## 2026-08-05 倾倒轨迹离线降采样处理

- 按用户确认采用离线降采样方案，未改动原始 `pour/segment_001.json`（437 点）。
- 新增 `robot_motion_executor/src/dexbot_motion_executor/dexbot_motion_executor/skills/teach_pan_pour/resources/trajectories/pour/segment_001_resampled_250.json`，通过原始时间范围上的关节线性插值生成 250 点。
- 新轨迹保留原始首点和末点，时间总长保持约 `9.157938 s`，时间戳严格递增；相邻点最大单关节变化约 `0.04519 rad`。
- `resource_manifest.yaml` 的 `pour` 映射已切换到 `segment_001_resampled_250.json`；`put` 轨迹保持不变。
- 新增可复用离线工具 `robot_motion_executor/tools/resample_joint_trajectory.py`，用于从原始轨迹重新生成指定点数版本。
- 验证：重采样完整性检查通过；执行器 `test_local_joint_trajectory_client.py` 为 `2 passed`；`colcon build --symlink-install --packages-select dexbot_motion_executor` 通过；`compileall` 和 `git diff --check` 通过。
- 尚未完成真实机器人复测；重启并重新 source 执行器安装空间后，需确认 `moveExecution` 最终 waypoint 为 `249`，且 `pour_replay` 成功后进入 `put_replay`。

## 2026-08-05 放锅轨迹队列容量检查

- 检查 `put/segment_001.json`：共 `182` 个关节点，轨迹时长约 `3.810766 s`。
- 已确认控制器此前的有效执行上限约为 `300` 个 waypoint；放锅轨迹 `182 < 300`，不会触发与原始倾倒轨迹相同的队列截断问题。
- 现有历史日志中该放锅轨迹曾完整执行并返回 `LOCAL_JOINT_TRAJECTORY completed`；当前不对放锅轨迹做降采样，保持原始点数和动作细节。
- 方案 1 实现后，`resource_manifest.yaml` 的 `pour` 和 `put` 均使用完整轨迹资源；不再使用 250 点离线重采样文件。
- NRT 滑动窗口实现已完成：单个 xCore 连接、首窗口启动、运动中按 `moveExecution` 进度追加下一窗口，避免控制器约 100 点队列边界导致轨迹中止和 Planner 重试。
- 软件验证通过：执行器相关定向测试 6 passed，compileall、diff check 和执行器 ROS 包构建通过；真实控制器连续追加仍待现场验证。

## 2026-08-05 NRT 滑动窗口现场失败归因与修复

- 现场首轮日志已排除“机械臂未启动”：`operationState` 明确进入 moving，且 `moveExecution` 连续推进到 `WaypointIndex=16`。
- 失败来源为 implementation：启动状态保护在 2 秒后未检查 `saw_motion`，把已经开始的正常轨迹错误报告为未进入 moving；这触发 Executor 失败并导致 Planner 对相同 `pour_replay` 重试。
- 已将条件修复为 `not saw_motion and now >= startup_deadline`，并新增慢速持续运动回归测试。验证结果更新为 7 passed；执行器编译、构建、差异检查均通过。
- 真机下一步：先确认修复后出现窗口续填日志 `[50,100)`，再判断控制器在运动中追加是否能够越过约 100 点边界；在此之前不将 NRT 连续回放标记为硬件通过。

## 2026-08-05 NRT 续填二次启动失败修复

- 现场已确认运动中 `moveAppend()` 能成功接受第二窗口：`WaypointIndex=25` 后出现 `[50,100)`，因此“控制器不支持运动中追加”的假设被证伪。
- 失败来源为 implementation：续填成功后错误调用 `moveStart()`，控制器正确拒绝为 `ec=-20, 机器人运动中`；Executor 将该拒绝错误传播给 Planner，导致对同一个 `pour_replay` 重试。
- 已改为连续运动只启动一次，运动中只 append；仅 idle/unknown 下的补窗口才重新 moveStart。新增针对性测试保证流式续填时 `moveStart()` 计数为 1。
- 软件验证：8 passed、compileall、diff check 和执行器包构建均通过。仍需真机确认控制器会连续消费第二及后续窗口并最终到达 437 点末端。

## 2026-08-05 NRT 完整轨迹真机验证成功

- 用户现场确认修复后的 NRT 滑动窗口已成功完整回放轨迹，并消除了由执行器错误导致的同一倾倒阶段重复重试。
- 结论更新：在该目标控制器上，单连接、首批启动、运动中分批 `moveAppend()` 的策略可以越过约 100 点有效队列边界；`pour` 保持完整 437 点资源，`put` 保持完整 182 点资源。
- 遗留问题：窗口之间存在短暂停顿，属于轨迹连续性/性能问题，而非功能正确性失败。后续优化应独立开展，候选为调整首批预填充量、补充阈值和窗口大小；在没有新的控制器时序证据前，不直接切换 RT 控制模式。
- 当前不再对已通过的完整回放链路继续改动；后续真机验收仍需覆盖急停、取消、连接独占及重复任务的恢复行为。

## 2026-08-05 robot_driver 启动配置发现修复

- 根因：`dexbot_robot_driver` 的 `ConfigReader` 使用 `os.getcwd()/.localconfig`；用户从 `robot_motion_executor` 目录运行 launch，Driver 因此查找错误工作空间中的 `.localconfig`，而有效配置位于主线工作空间根目录。
- 修复：在 `kitchen_robot_home/src/dexbot_bringup/launch/dexrob_full.launch.py` 为 `robot_driver_node` 设置 `cwd`，由已安装的 `dexbot_bringup` share 路径稳定反推主线工作空间根目录。
- 保持边界：未修改 `/opt/ros/humble` 下 Driver/SDK，未复制 `.localconfig`，未改变公共 SDK 路径配置。
- 验证：`colcon build --symlink-install --packages-select dexbot_bringup` 成功；launch cwd substitution 实际解析到 `/home/tbl/Project/boss_electrics/kitchen_robot_home`；`compileall` 和 `git diff --check` 成功。
- 未覆盖：真实机器人 Driver 启动、SDK 动态加载、CAN 和硬件服务验证待用户在急停可达条件下复测。

## 2026-08-05 完整轨迹执行方案重新评估

- 新日志将有效队列上限进一步确认到约 100 点：250 点 pour 轨迹只执行到第二批的 `WaypointIndex=49`，即全局约第 100 点，然后控制器回 `idle`。
- 分段追加可行性：SDK 的 `moveStart()` 文档语义为“开始或继续运动”，官方示例也在运动开始后继续调用运动 API；但当前实现必须改成运动期间的滑动窗口追加，不能把多个批次全部预加载后等待控制器执行。
- 推荐实现：保持单个 xCore 连接和 `NrtCommandMode`，先追加例如 60~80 点，启动后根据 `moveExecution` 的已执行 waypoint 或队列余量追加下一窗口，并在最后一个窗口使用 `zone=0`；全程不得调用 `moveReset()` 或等待队列回 idle。
- RT 可行性：SDK 提供 `RtCommandMode`、`FollowPosition_7` 和 `setControlLoopJoi()`；当前工作空间已有条件式 xCore 适配代码，但默认关闭且未在目标控制器上做真机验证。RT 需要独立控制周期、实时网络、控制器型号支持和更严格的安全/取消处理。
- 当前结论：先做 NRT 滑动窗口 Spike；只有在控制器运动中追加仍无法跨越 100 点限制时，再进入 RT 控制 Spike。完整 pour/put 资源暂不再降采样。

## 2026-08-05 记录机械臂关节限位

- 用户现场确认机械臂关节角度限位（单位：度），已新增 `.project-log/docs/robot_joint_limits.md`：
  - 关节 1：`-178 ~ 178`；关节 2：`-120 ~ 120`；关节 3：`-178 ~ 178`
  - 关节 4：`-60 ~ 145`；关节 5：`-178 ~ 178`；关节 6：`-50 ~ 50`；关节 7：`-50 ~ 50`
- 来源为用户确认，尚未通过 SDK/控制器/硬件交叉验证；后续轨迹生成或 IK 检查使用前应先与控制器实际限位核对。

## 2026-08-05 倾倒轨迹关节限位检查

- 对倾倒轨迹 `pour/segment_001.json` 的 437 个点位（弧度制）计算各关节最大/最小位置并换算为角度，与记录限位对比，全部在限位范围内。
- 各关节实际范围（度）：J1 41.90~71.52、J2 66.96~77.47、J3 -91.69~-68.14、J4 23.95~109.69、J5 81.84~147.78、J6 -20.43~21.31、J7 11.20~40.49。
- 距边界最近的关节：J7（约 10°）、J2（约 42°）、J4（约 35°）。该对比基于用户确认限位，未与 SDK/控制器实际限位交叉验证；结果已记录至 `.project-log/docs/robot_joint_limits.md`。

## 2026-08-05 GUI 增量轨迹业务澄清启动

- 新增范围：先在现有 GUI 集成增量法兰轨迹的录制和回放，暂不修改两个 ROS 工程的运行代码。
- 已确认录制语义：机械按钮按下开始、松开结束，结束后自动后处理并生成 `Delta_i = inverse(T0) @ Ti` 的增量轨迹文件。
- 已确认回放语义：选择增量文件后读取当前法兰位姿，按 `T_current @ Delta_i` 展开并执行。
- 已确认资产隔离：增量目录以 `delta` 开头；普通/增量轨迹文件都必须包含明确类型标签，回放前执行类型校验。
- 参考工程证据：`flange_motion_editor` 使用 raw → processed → delta 三阶段处理链；当前老板电器工程已有增量 schema 校验和展开模块，但尚无绝对法兰样本到 delta 文件的生成工具。
- 用户已确认 `Q-016`：raw、processed、delta 三类文件全部保留；GUI 默认回放列表只展示 delta，raw/processed 作为诊断和重新处理产物。
- 用户已确认 `Q-017`：增量回放复用普通轨迹的停止/取消/重新发起语义，停止或取消后请求安全停止，不自动重试。
- 当前状态：business-clarification；下一项最高优先级开放问题为 `Q-018`，暂不进入代码实现。

## 2026-08-05 GUI 增量轨迹业务澄清完成

- 用户确认历史无标签文件默认按普通轨迹处理；只有显式 `flange_delta` 标签并通过增量 schema 校验的文件才允许增量回放。
- 文件和数据规则确认：增量目录使用 `delta_` 前缀；普通/增量标签使用 `joint_absolute` / `flange_delta`；每次录制生成动作名+时间戳版本；raw、processed、delta 三类产物全部保留且关联；禁止静默覆盖。
- 默认后处理确认：`flangeInBase`、80 Hz、异常跳变剔除、位置/姿态平滑、去重和空间弧长重采样；录制失败保留 raw 及失败原因，不生成无效 delta。
- 回放规则确认：校验资产元数据、臂别、schema、当前法兰位姿、展开结果和非空轨迹；停止/取消复用普通回放的安全停止和人工显式重试语义。IK、关节限位和碰撞检查待真实执行接口接入后补充。
- GUI 布局确认：增量开始/停止录制按钮置于现有开启/关闭拖动栏目，紧邻普通录制按钮；独立增量回放区域放在普通轨迹回放区域下方。
- 本轮不改 GUI 或 ROS 产品代码；下一阶段为 GUI 代码接管、工程规格和实施，尚需核对现有机械按钮事件、去抖、异常松开和状态机细节。

## 2026-08-06 增量倾倒回放业务逻辑（confirmed）

- 用户确认新建独立 `teach_pan_pour_delta` policy + skills，保留现有 `teach_pan_pour` 普通轨迹版本不动。
- 倾倒阶段改用 GUI 录制的增量法兰轨迹 `候选2带增量轨迹.json`（103 点）：`move_to_pour_ready` → 读当前法兰位姿 → `T_current @ Delta_i` 展开 → IK → 关节回放；执行端采用短生命周期 xCore SDK 直连。
- 放锅阶段改为固定关节点 `put_fixed`，仅关节角度、无轨迹文件、无专用速度参数；实际关节角待用户提供，当前用现有 put 轨迹末点占位。
- 阶段序列已确认：`home_open → move_to_grasp_ready → close_gripper → move_to_lift → move_to_pour_ready → pour_delta_replay → put_fixed → open_gripper → return_home`。
- 记录：`.project-log/business-logic/pan_pour_delta_replay.md`。

## 2026-08-06 teach_pan_pour_delta policy + skills 实现

- 完成主线 `teach_pan_pour_delta` policy 及执行仓库 `TeachPanPourDeltaSkill` 的新建（不动现有 `teach_pan_pour`），任务类型 `teach_pan_pour_delta`。
- 倾倒使用 GUI 增量法兰轨迹 `pour_delta.json`（103 点）：先到 `move_to_pour_ready`，再读当前法兰位姿按 `T_current @ Delta_i` 展开，`model.getJointPos` 连续 IK + 关节限位校验，滑动窗口流式回放；执行端短生命周期 xCore SDK 直连。
- 放锅改为固定关节点 `put_fixed`，当前以现有 put 轨迹末点占位，待用户提供真实关节角替换。
- 增量轨迹文件复制为字节一致；新增 `FlangeDeltaTrajectory.from_gui_mapping` 兼容 GUI 格式；`execute_local_joint_trajectory` 拆分出内存点流式 `execute_joint_points`。
- 验证：主线 31 passed + 执行器 32 passed（均不含两条既有失败的其他 flake8/pep257 全仓库基线扫描）；两包构建、compileall、`git diff --check` 通过。
- 状态：`implemented-unverified`；真机验证前确认急停可达、同一左臂仅一条控制链、起点一致性、IK 全解、限位与末点到位。放锅关节角未提供前不做放锅真机验证。

## 2026-08-06 put_fixed 固定点确认（复用抓取点）

- 用户确认放锅点 `put_fixed` 关节角度与抓取点一致（`grasp_ready` preset `2`），实现上运行时复用 `grasp_ready` 位姿，避免复制数值导致漂移。
- 记录于 `.project-log/business-logic/pan_pour_delta_replay.md`；执行器定向测试与构建通过。

## 2026-08-06 teach_pan_pour_delta 增量倾倒回放真机验证成功

- 用户现场确认 `teach_pan_pour_delta` 全流程真机验证成功：`move_to_pour_ready → pour_delta_replay → put_fixed → open_gripper → return_home` 完整执行，增量倾倒回放不再退段重试。
- 增量回放链路（单 xCore 连接：读当前法兰位姿 → `T_current @ Delta_i` 展开 → IK 求解 → 滑动窗口关节流式回放）在目标左臂控制器（`192.168.2.159`，`xMateErProRobot`）上通过，IK 全解、未触关节限位、末点到位。
- `put_fixed` 运行时复用 `grasp_ready` 抓取点关节角，固定点放锅真机通过；现有 `teach_pan_pour` 普通轨迹版本未改动。
- 状态从实现时的初始 `implemented-unverified` 更新为真机口径 `implemented-verified`；证据级别 3（真机），但控制器逐窗口/姿态日志未全套归档，限制为日志完整性以及急停、取消、控制权竞争、重复任务恢复未覆盖。
- 下一步：按用户约定分别提交两个仓库（本地 `git commit`，不 push）。

## 2026-08-06 版本口径澄清（正式 V1 vs 临时测试版本）

- 用户指出此前把“V1 正式版本”与临时测试路径混淆；本轮先冻结版本口径，避免后续再次搞混。
- **正式 V1 版本**：主仓库 `pan_pour`（`PanPourPolicy`，TASK-011/012/013 基础已实现）＝感知组锅把结果 → 沿 PCA 主轴偏置的抓取 → 参数化抓取 TCP → 提锅至准备倾倒 → 底盘协同移动（左臂保持姿态）→ 餐盘定位 → `pour_point_C = plate_center_C + pour_offset_C` → 锅具 TCP 转换 → 锅具 TCP 坐标系下增量倾倒回放 → 预留放回/home；业务目标统一在机器人中心坐标系 C 表达。这是后续要完善的正式产品版本。
- **临时测试版本 1** = `teach_pan_pour`（TASK-016）：固定工位、无感知/无底盘/无中心 C 系，普通拖动示教轨迹回放，用于验证动作链路，真机已跑通。
- **临时测试版本 2** = `teach_pan_pour_delta`（TASK-016 增量改造）：同固定工位约束，倾倒改为 GUI 增量法兰轨迹回放、放锅固定点 `put_fixed`，真机已跑通。
- 两个正式外部路径的常见混用风险已记录；下一步工作转向完善正式 V1 版本（`pan_pour` / `PanPourPolicy`）。

## 2026-08-06 正式 V1 增量倾倒回放接入（TASK-018）

- 用户确认把临时版本 `teach_pan_pour_delta` 已真机跑通的增量倾倒回放完整迁移到正式 V1（`pan_pour` / `PanPourPolicy`），思路不变（短生命周期 xCore 直连 + 滑动窗口 append），V1 最小闭环到倾倒完成结束。
- 主仓库：新增 `PlanType.PLAN_PAN_POUR_DELTA_REPLAY`；`PanPourPolicy` 终态改为 `POUR_DELTA_REPLAY`，下发 `pour_delta_replay` 步骤并完成后 `COMPLETE`；Planner 路由接入 `_build_skill_goal`。
- 执行仓库：新增独立 `PanPourDeltaReplaySkill`（`pan_pour_delta_replay`）复用既有 `LOCAL_DELTA_FLANGE_REPLAY` 原语与 `delta_flange_replay_client`，`pour_delta.json` 独立副本（103 点，字节一致）；`motion_executor_node` 注册，`setup.py` 打包。
- 验证：主仓库定向 14 passed；执行仓库新增 4 passed；两仓库构建、compileall、`git diff --check` 通过；既有 flake8/pep257 全仓库基线仍失败（与本次无关）。本机测试需 `PYTHONNOUSERSITE=1` 隔离 `~/.local` 的 numpy 2.2.6/anyio 4.13。
- 状态：`implemented-unverified`；正式 V1 未标定（`pan_pour.configured=false`），真机验证待现场标定后进行。

## 2026-08-06 正式 V1 Skill 边界确认

- 用户确认：V1 只新增 1 个专用 Skill（`PanPourDeltaReplaySkill` / `pan_pour_delta_replay`），其余动作复用现有 `move_cartesian`、`gripper_action` API；感知走 Planner 侧 `WorldState`，不是执行器 Skill。
- 底盘协同视接口归属而定：经 MotionExecutor 下发则再新增底盘 Skill，否则底盘组自行控制、执行器侧不新增。
- 已记录至 `.project-log/business-logic/pan_pour_v1_skills.md`，并同步更新 ARCH-001 组件清单与 `skill_boundary` 小节。

## 2026-08-06 正式 V1 单一自包含 pan_pour Skill（TASK-018 收口）

- 用户最终确认：正式 V1 完整复刻测试版手部逻辑（`SET_HAND_ANGLES` + `SET_HAND_TORQUES`），参数全部收进单一自包含 skill 包，不依赖临时 teach 链路；角度/力矩直接用测试版已调好的值。
- 主仓库：`PLAN_PAN_POUR` 新 PlanType 取代 `PLAN_PAN_POUR_DELTA_REPLAY`；`PanPourPolicy` 阶段链补全 `PUT_FIXED → OPEN_HAND → RETURN_HOME → COMPLETE`；移除 `gripper.close_action_name` 参数与校验；Planner 路由 `PLAN_PAN_POUR → _build_skill_goal`。
- 执行仓库：新建自包含 `skills/pan_pour/`（`PanPourSkill`：close_hand/open_hand/pour_delta_replay/put_fixed/return_home），自带 arm 位姿、手部预设与 103 点 pour_delta.json；删除旧 `pan_pour_delta_replay`。
- 验证：主仓库 13 passed、执行仓 9 passed（自包含与 103 点资源校验）；两包构建、compileall、`git diff --check` 通过；新增文件 flake8 干净。状态 `implemented-unverified`。
- 决策记录：DEC-024（approved）取代 DEC-023；`.project-log/business-logic/pan_pour_v1_skills.md` 与 ARCH-001 `skill_boundary` 已同步。

## 2026-08-06 V1 底盘移动第二预留位（倾倒后回位）

- 用户确认：增量倾倒回放完成后、`put_fixed` 放锅前，底盘需要再移动一次回到原工位；本质复用同一个底盘移动接口，不做“反向”专用逻辑。
- `PanPourPolicy` 新增 `WAITING_FOR_BASE_RETURN` 阶段（`POUR_DELTA_REPLAY` 与 `PUT_FIXED` 之间），复用 `update_base_positioned`；第一次 `WAITING_FOR_BASE_POSITION` 消费后重置标志，两次底盘移动都需外部适配器确认。

## 2026-08-07 手眼标定启动问题清单冻结

- 用户要求做相机外参（手眼）自动标定，按“逐个解决问题”推进；本轮先冻结前置问题清单，未装包、未改产品代码。
- 已确认现有实现口径：固定相机 + 机械臂末端刚性装 ArUco 标记，解 `T_base_cam`；与 `calibration.launch.py` + `dexbot_toolbox` 一致。
- 冻结 6 条前置问题：`dexbot_toolbox` 未安装且未进 `VERSIONS.yaml`（CAL-01 ✅ 已解决）；相机 `camera1` 命名空间与 ArUco 硬编码 `/camera/color/*` 话题不匹配（CAL-02 ✅ 复核后确认 1.0.0 上不成立）；`camera1_ost.yaml`（1280x720）与 `camera1_params.yaml`（realsense 640x480）内参不一致（CAL-03 待解决）；标定板边长/字典需确认（CAL-04 待解决）；机器人 IP 未确认（CAL-05 待解决）；结果写盘与中心坐标统一链路待执行。
- 完整清单、启动命令和待用户提供项：`.project-log/docs/hand_eye_calibration.md`。

## 2026-08-10 kitchen SDK 排除与待推送状态

- 按用户口径，SDK 改动不提交、不推送。`kitchen_robot_home` 本地 4 个提交已重写，移除 `src/sdk/arm_api/Python/lbot/lbot_robot_xcore.py`（`ARM_JOINT_COUNT` / `joint_count` 改动），原提交备份在 `backup/robam_kitchen-before-sdk-exclusion-20260810`。
- 新提交：`51c148c`、`4089b40`、`2f4949e`、`7d8dd4d`；与远端无分叉，`origin/robam_kitchen..HEAD` 无 `/sdk/` 路径。
- 工作区仍保留 SDK 未提交改动（v0.5.1 删除 + v0.7.1 未跟踪），`stash@{0}` 未动。
- 验证：`git diff --check` 通过；`compileall` 通过；Kitchen 定向测试 31 passed。任务代码未改动，仅历史重写。
- 待办：尚未 push；待用户确认后执行 push，并接着处理 `robot_motion_executor` 仓库对应分支 review。


## 2026-08-11 主仓库 SDK 排除复核

- 主仓库 `kitchen_robot_home` 当前为 `robam_kitchen` / `a0aefce`，已与 `origin/robam_kitchen` 同步，工作区干净。
- SDK v0.7 迁移改动仍只在未应用的 `stash@{0}` 中；从任务基线 `9de887a` 到当前 HEAD 的提交不包含 `src/sdk` 路径改动，stash 未删除。
- 当前 HEAD 验证通过：compileall、定向测试 18 passed、`dexbot_bringup` 与 `dexbot_task_planner` colcon build、`git diff --check`。
- 当前没有主仓库待 push 增量；后续按用户指令转入 `robot_motion_executor`。


## 2026-08-11 执行仓库待 push 提交复核

- `robot_motion_executor` `robam_kitchen` 本地领先远端 1 个提交：`efa6b24 TBL出锅倾倒菜`；远端没有反向提交，`pull` 无必要。
- 三个个人 SDK 文件继续保持 `skip-worktree`，并已在仓库外完成 SHA-256 一致性备份。
- 待推送提交审查通过：41 个定向测试通过、compileall 通过、执行器包 colcon build 通过、提交 diff-check 通过、工作区无普通或 staged 改动。
- 注意：待推送提交本身包含公共路径回放功能对 `xcore_path_client.py` 的改动以及新增 `test_path_replay.py`；当前个人工作区版本不随 push 发送。
- 本轮停止在手动 push 前。

- 进一步使用 `efa6b24` 干净提交快照复验：定向测试 41 passed、compileall 和 colcon build 通过；`git push --dry-run origin robam_kitchen` 成功，确认可推送 `4635b3e..efa6b24`。
