# Progress

倾倒入盘技术路线调研和 V1 业务澄清已完成，用户已确认 V1/V2 两版本方案；当前进入两个仓库的技术选型阶段。

- 推荐：示教轨迹基线 + 受限重量/力矩反馈局部修正。
- 回退：带安全限幅、超时、急停和人工确认的示教回放。
- V1：作为中间环节承接上游任务，订阅感知组锅把信息，沿锅把 PCA 主轴施加中心坐标系下的抓取偏置，使用参数化抓取 TCP 控制左臂；提锅后由底盘组协同移动，再以机器人中心坐标系下的餐盘中心点加 xyz 偏置计算倾倒点，通过参数化锅具 TCP 和其局部坐标系增量回放完成倾倒；放回/home、落料验收和异常处理后续补充，不考虑右手锅铲辅助。
- V2：V1 闭环稳定后，再评估右手锅铲抓取、放置、辅助动作和碰撞约束。
- 代码主链：`ScenePerception → TaskPlanner → ExecuteTask → MotionExecutor → RobotDriver`。
- 当前发现：代码具备通用 task/policy/skill/primitive 骨架，中心坐标系生成脚本和 `toolset.end/ref` 参数入口已存在，但尚未承载 V1 感知结果契约、锅具 TCP 转换、底盘保持姿态协同和锅具 TCP 增量倾倒回放。
- 下一步：执行 `TASK-008`，比较两仓库中感知消息、TaskTarget/ExecuteTask、Skill/Primitive、中心坐标转换、底盘协同和轨迹回放的承载方案；批准前不改产品代码。
- 旧版完整记录：`.project-log-legacy-20260728/`。
 旧版完整记录：`.project-log-legacy-20260728/`。

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
