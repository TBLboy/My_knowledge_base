## 当前会话（2026-07-30 TASK-012 动态 Policy 骨架）

- `TASK-012` 的可本地验证范围已实现：`PanPourPolicy` 注册为 `pan_pour`，由一个 `_phase` 依次驱动 `waiting_for_configuration → waiting_for_handle_detection → move_to_grasp → close_gripper → move_to_pour_ready → waiting_for_base_position → waiting_for_plate_detection → move_to_pour_position → waiting_for_pour_replay_adapter`。
- 抓取阶段只消费未来感知适配器提供的 `grasp_point_C` 与 `pca_axis_C`，使用 `tcp_grasp` 反解为左臂 base 下法兰目标；准备倾倒和倾倒接近使用 `tcp_pan`。没有把现有通用 `ScenePerception/ObjectDetection.pose` 擅自解释为锅把或餐盘语义。
- 动作完成仍由现有 Planner Action 结果回调调用 `update_step_status()`；只有 `COMPLETED` 推进 phase。配置、感知、底盘或回放能力未就绪时，Policy 返回 `WAIT`，Planner 保留 active task 且不发送 Action。
- 验证：28 个定向测试、`dexbot_interfaces dexbot_bringup dexbot_task_planner` 三包构建、`compileall` 和 `git diff --check` 通过。未启动真实 ROS 节点、MotionExecutor、目标 Driver deb 或硬件。
- `TASK-012` 保持 `blocked`，因为完整集成仍缺三项外部能力：感知组字段/坐标/新鲜度契约、底盘 ROS 生命周期接口、`TASK-013` 的相对法兰回放 Skill。构建和 Python 缓存将在证据记录后清理。

## 当前会话（2026-07-30 感知路径确认）

- 用户确认遵从现有框架，老板电器任务采用路径 A：`ScenePerception → TaskPlannerNode._on_scene() → WorldState → PanPourPolicy`。
- 正式流程不新增任务专用感知 topic、PerceptionBridge 或第二套对象缓存；`PanPourPolicy` 通过已有 `world=self._world` 读取统一世界模型。
- 715 参考仓库中的专用感知桥接器仅作为对比证据，不复制到老板电器任务。
- 感知组仍需确认锅把抓取点、PCA 主轴、餐盘中心、source frame、有效性、置信度和新鲜度字段契约；在契约到达前，不把通用 `ObjectDetection.pose` 擅自解释为业务语义。
- 记录：`DEC-016`、`ARCH-001.perception_boundary`；产品代码未修改。

## 当前会话（2026-07-30 TASK-013 离线轨迹基础）

- `TASK-013` 的可独立实现范围已完成：在执行仓库新增 `FlangeDeltaTrajectory`，只解析版本化 `spatial_only`、`flangeInBase` 轨迹资产，并以 `T_current @ Delta_i` 产生绝对法兰航点；不创建 ROS Action、Skill、Driver 客户端或 xCore 直连。
- schema 明确固定 `m`、`rad`、`xyz` RPY、`initial_flange` 参考和 identity 首增量，防止把 TCP、毫米、不同欧拉角顺序或绝对路径误当作本 V1 资产。
- 验证：10 个定向测试、模块编译和两仓库 diff 检查通过。`TASK-013` 仍 blocked，直到目标 Driver 实测确认当前法兰位姿/MoveCartesian 语义，且团队采集并版本化真实 V1 倾倒轨迹。
- 已同步 V1 范围：当前最小闭环在倾倒完成结束；放回锅具、张开灵巧手和 home 为后续 cleanup 扩展，不再列为当前 V1 的完成条件。

## 当前会话（2026-07-30 TASK-011 实现）

- `TASK-011` 已完成并通过定向验证。新增任务私有 `pan_pour_params.yaml`，由 `dexrob_full.launch.py` 注入 `task_planner_node`；未修改共享 `robot_params.yaml` 或任何公共 ROS 接口。
- 新增纯计算模块 `pan_pour_kinematics.py`：统一使用 `T_A_B` 变换记号，完成抓取/锅具 TCP 目标从中心坐标系到左臂 base 法兰目标的计算：`T_B_F = T_B_C @ T_C_TCP @ inverse(T_F_TCP)`；PCA 抓取偏置在 C 系沿归一化 PCA 向量计算。
- `PanPourParameters.validate_for_execution()` 明确拒绝 `configured: false` 的占位模板。当前没有实际标定值，因此不得将模板用于实机动作。
- 验证：21 个定向测试通过；`dexbot_bringup` 与 `dexbot_task_planner` 构建通过；`git diff --check` 通过。未启动真实 ROS 节点、MotionExecutor、目标 Driver deb 或硬件。构建和 Python 缓存已清理。
- 当前下一步：`TASK-012` 仍等待感知组最终字段契约和底盘组 ROS 接口；获得契约后接入单个 `PanPourPolicy` 的动态阶段状态机，并从本任务的私有参数快照取 TCP/偏置值。

## 当前会话（2026-07-28 第二轮）

## 当前会话（2026-07-29 源码学习）

- 用户要求从源码内部建立架构理解，反对只停留在模块职责和抽象流程层面。
- 已完成的源码阅读链：`_on_start_task()`、`_prepare_start_task_context()`、`_clear_runtime_state()`、`_on_tick()`、`_generate_goal_by_task_type()`、`_build_gripper_action_goal()`。
- 已用 `test_gripper` 具体追踪：`StartTask(task_type="test_gripper")` 如何创建 `TestGripperPolicy`，定时器如何门控，Policy 如何返回 `PlannedStep(plan_type="gripper_action", action_name="张开", arm_type=1)`，Planner 如何构造 `ExecuteTask.Goal`。
- 已确认 `ExecuteTask.Goal` 是 ROS 2 Action 的 Goal 消息对象，外层 `task_id` 标识任务，`task_type` 负责下游路由，`target` 携带具体动作参数。
- 已确认当前真实源码中 `_build_gripper_action_goal()` 只填 `TaskTarget.arm_type/action_name`，没有填 `TaskTarget.task_id/object_id/class_name`；此前示意讲解已纠正。
- 已记录学习方法：每个概念必须落到具体类、方法、属性、调用关系、输入值、输出对象和下游消费；先源码事实，再概念类比。
- 用户进一步确认偏好的讲解结构：`完整任务时间线 → 关键状态变量变化表 → 工程思路总结`。已将 `test_gripper` 的时间线和变量表作为后续讲解模板。
- 复习笔记：`.project-log/docs/source-code-learning.md`
- 下一步：继续阅读 `TestGripperPolicy.select_next_goal()` 和结果回调，再进入 MotionExecutor 的 ActionServer 路由。
- 用户要求将已确认的讲解方法抽象为可复用资产；已创建并安装全局显式触发 Skill：`/home/tbl/.codex/skills/b-source-code-tutoring/`。
- Skill 固化的顺序为：`具体输入 → 真实运行时间线 → 状态变量生命周期 → 源码逐行实现 → 下游消费/结果回调 → 最后工程概念抽象`；结构校验已通过，评测样例位于 `.project-log/evals/source-code-tutoring.yaml`。

## 技术选型进行中（2026-07-29）

- 完成 TestGripperPolicy 完整源码阅读，对比分析 TestHeartPolicy（场景感知 plan）和 PeelApplePolicy（CSV/运动学生成）。
- 发现 V1 流程存在两段时序约束：底盘移动前锅把可见、底盘移动后餐盘才进入视野。
- 确认 Policy 不需要预生成全部步骤：`select_next_goal()` 每次被调用的特性 + `_world` 持续更新 + `update_step_status` 提供反馈 → 一个 Policy 内分阶段生成即可。
- 已记录 DEC-009，更新架构描述。
- 下一步：确认 WorldState 中餐盘检测结果的字段契约和感知组输出 Topic。

## 完整调用链串讲已记录（2026-07-29）
- 应用户要求，完成了从 `__init__` 到 `_on_result` 的完整 9 阶段时间线串讲，覆盖：初始化 → StartTask → 门控 → Policy 决策 → Goal 构建 → 发送 + 闭包注册 → Goal Handle 确认 → 等待空转 → 结果回调 → 步骤状态更新 → 任务结束。
- 记录了 9 个阶段的完整代码路径，每个阶段都附带了具体源码行号和变量值。
- 记录了关键变量生命周期总表（11 个变量在 5 个时间点的值）。
- 总结了四个属性层面（上下文层/运行状态层/门控标志层/代际保护层）的工程划分。
- 添加了源码路径索引，供后续快速定位关键函数行号。
- 完整记录已追加到 `.project-log/docs/source-code-learning.md`（307→842行）。
- 当前状态：TASK-008 仍在进行中，产品代码未修改。
- 下一步（用户待确认）：继续读 MotionExecutor 端的 ActionServer 路由，还是切换到其他方向。
- 
## 参数配置模式调查（2026-07-29）
- 调查了现有代码的参数管理方式：ROS 2 参数系统 + YAML 配置文件，集中在 `dexbot_bringup/config/`，按子系统分目录。
- 当前 `TaskPlannerNode` 是唯一裸启动的核心节点（无 parameters= 参数文件），所有值硬编码在 `__init__` 中。
- V1 技术参数（抓取偏置、等待位置、倾倒偏置、锅具 TCP、home 位姿等）可遵循现有模式：
  - 创建 `dexbot_bringup/config/pan_pour/pan_pour_params.yaml`
  - 在 `TaskPlannerNode.__init__()` 中添加 `declare_parameter()` 声明
  - 在 `dexrob_full.launch.py` 中为 task_planner_node 添加 `parameters=[pan_pour_config]`
- 参数命名采用分层结构，如 `pan_pour.grasp_offset`，Policy 内部通过 Node 的参数接口读取。
- 此项属于技术选型发现，待进入 engineering-landing 阶段后再实现，当前不修改产品代码。

## 技术选型初步确认（2026-07-29）
- 用户确认选型 2 采用方案 A：单个 `PanPourPolicy`，内部维护 `_phase`，根据 `WorldState` 动态生成下一阶段。
- 用户确认选型 3：业务目标和中间位姿统一在机器人中心坐标系 C 下计算，靠近执行器的适配层再转换到机械臂/RobotDriver 坐标系。
- 用户确认选型 4：单目标/单原子动作复用现有 API/MotionPrimitive；复杂动作拆解才使用 Skill。
- 用户暂定选型 5：底盘接口等待底盘组提供准确消息后再定，不阻塞当前机械臂流程选型。
- 用户确认选型 6：技术参数采用 ROS 2 YAML 参数配置，通过 launch 注入，不在 Policy 内硬编码。
- 选型 1（TaskTarget、PourTaskTarget 或独立 Action 的接口承载）暂时搁置；选型 7（锅具 TCP 局部增量轨迹回放）下一步单独讨论。
- 已新增 `DEC-010` 记录上述确认；产品代码仍未修改。

## 选型 7 初步证据（2026-07-29）
- 阅读 `robot_motion_executor` 的 `PathRecordSkill`、`xcore_path_client.record_path_on_robot()` 和 `smoothie_path_record_replay.replay_path()`。
- 当前能力是：通过 xCore 直连控制器录制命名路径，并调用控制器 `replayPath(name, rate)` 回放；路径保存于控制器内部。
- 当前代码没有暴露路径点、`frame_id`、锅具 TCP 引用、相对/绝对坐标语义或运行时 TCP 转换，因此不能把现有 `RECORD_PATH` 直接认定为锅具 TCP 局部增量轨迹契约。
- 选型 7 暂不下最终用户批准结论；候选方向收敛为：复用法兰增量轨迹文件 + 适配器，或在控制器能力确认后复用原生回放。
- 当前建议先做最小 replay spike：在两个不同起始位姿下验证刚体连接锅具能否复现同一法兰示教动作，并验证锅具 TCP 起始位姿对齐、`robot_driver` 占用、取消和执行反馈。

## 选型 7 现成方案评估（2026-07-29）
- 已阅读用户提供的 `flange_motion_editor`：`capture_flange_motion.py`、`process_flange_motion.py`、`spatial_replay.py`、`replay_flange_motion.py`、`sdk_robot.py` 及 README。
- 源码事实：轨迹采集和输出使用 `coordinate_system: flangeInBase`；处理阶段计算 `Delta_i = inverse(T0) @ Ti`；回放阶段使用 `T_current @ Delta_i` 生成绝对法兰路径，再调用 `move_rt_cartesian_path()`。
- 结论：可复用其显式 YAML、空间重采样、SE(3) 增量数学和离线处理流程；不能直接复用其“法兰坐标 + 直连 SDK”运行入口。
- 关键修正：V1 可以直接使用 `flangeInBase` 采集得到的法兰局部增量。因为抓取后锅具与法兰是刚体连接，只要回放时把法兰起始位姿对齐到期望锅具 TCP 起始位姿，锅具就会随法兰完成同一刚体轨迹。
- 锅具 TCP 的职责是参与起始位姿反解：由期望的 `T_C_P_start` 和固定 `T_F_P` 得到 `T_C_F_start = T_C_P_start @ T_P_F`；不需要对每个 `Delta_F_i` 做 TCP 共轭转换。
- 正式接入位置建议在 `robot_motion_executor` 的 Skill/Adapter 边界，通过现有 RobotDriver 链路执行；不要让 TaskPlanner 直接启动外部回放脚本。
- 已新增 `RES-003` 和 `DEC-011`。`DEC-011` 是待用户批准的技术选型提案，产品代码仍未修改。
- 下一步：最小 replay Spike，验证两个起始位姿/两个 TCP 参数下的起始对齐和锅具刚体轨迹一致性，以及 RPY、单位、矩阵方向、driver 占用、取消和反馈。


---

- 当前阶段：solution-research（技术选型）
- 当前目标：`GOAL-001`；TASK-007 已完成，TASK-008 进行中
- 本轮完成：
  - 用户回顾今日任务记录，确认 V1/V2 两版本路线
  - 完成 V1 完整流程状态机详细澄清（handoff → ... → home 共 12 个步骤）
  - 确认倾倒点公式 `pour_point_C = plate_center_C + pour_offset_C`（中心坐标系 C 下 xyz 三向可调偏置）
  - 确认抓取偏置沿锅把 PCA 主轴方向、定义在中心坐标系 C 下
  - 确认抓取 TCP/锅具 TCP 位姿参数化，代码已有 toolset.end/ref 入口
  - 确认倾倒采用锅具 TCP 局部坐标系录制增量回放
  - 确认 V1 不加落料验收、异常处理和抓取确认，只打通动作流程
  - 确认放回/张手/home 后续确定，具体参数数值不阻塞流程骨架
  - 用户批量回答了全部开放问题，所有阻塞项解除
  - 用户同意进入技术选型阶段
- 当前决策状态：DEC-003/005/006/007 active；DEC-008 proposed 待用户确认
- 产品代码仍未修改
- 待用户批准：DEC-008 技术承载方案、ARCH-001 架构草案

---

# Current Session

- Project Log 已从旧 v0.2 结构迁移到运行时 v0.4 模板。
- 旧日志原样保存在 `.project-log-legacy-20260728/`，不得删除。
- 当前目标：`GOAL-001`；当前阶段：`business-clarification`；下一步：完成 V1 业务逻辑与两个仓库代码行为的双向澄清。
- 2026-07-28 已完成 Project Log v0.2 → 运行时 v0.4 迁移；新结构校验通过。
- Loop 状态：`active`，原生 Goal 仍未绑定；这不影响项目日志迁移结果。
- 2026-07-28 用户已确认 V1 只打通动作流程，不加入落料验收、异常检查和异常处理；抓取偏置沿锅把 PCA 主轴，抓取 TCP/锅具 TCP 位姿参数化，倾倒动作使用锅具 TCP 坐标系录制回放，放回/home 后续确定。
- 当前阶段已从 `business-clarification` 切换到 `solution-research`，下一步执行 `TASK-008` 技术选型；产品代码仍未修改。

## Legacy Session Snapshot

# Current Session

- 当前阶段：business-clarification（两个仓库第一轮代码接管完成，进入业务/技术逻辑对齐）
- 当前目标：老板电器炒菜机器人「倾倒入盘（大）- 炒菜出锅呈盘」技术方案调研
- 当前任务：澄清 V1 业务原子、代码承载边界和技术未知项；技术选型批准前不修改产品代码
- 新增业务口径：锅把抓取属于 V1 基础流程，当前 V1 初版不执行抓取确认，先跑通无确认基础链路
- 用户提出采用“先跑通初级版本、再逐步迭代”，并提交 `/home/tbl/Project/boss_electrics/方案1.md`
- 用户要求基于原文生成仅做格式整理的 `/home/tbl/Project/boss_electrics/方案1整理.md`
- 用户要求制定第一版锅把特征检测特征名单及检测方案
- 用户补充：第一版抓取目标点暂时定义为锅把中心点；特征需压缩，主要供感知组训练模型；核心信息为锅把中心、抓取点和主轴方向
- 用户进一步补充：PCB 主轴方向以附带图片方向为准；抓取点偏移量定义为沿 PCB 主轴方向的偏移
- 用户于 2026-07-28 确认两版本路线：V1 不考虑右手锅铲辅助，先完成左手抓锅到倾倒入盘的完整闭环；V2 再迭代右手锅铲辅助
- 用户于 2026-07-28 要求先理解 `kitchen_robot_home` 主仓库和 `robot_motion_executor` 执行仓库，再开展业务逻辑澄清、技术选型和架构讲解，之后才开始写代码
- 用户于 2026-07-28 补充：两个仓库由团队共同开发；感知组提供锅把模型和感知信息，本子任务只订阅；底盘组支持移动；左臂抓取 TCP、锅具 TCP、抓取偏置、姿态保持和录制增量倾倒动作纳入 V1 业务澄清

## 已确认事实
- 项目：老板电器智能厨房机器人，双臂移动机器人 + 智能厨电协同
- 四个场景：蓑衣黄瓜、芦笋虾仁、洗碗、清洁台面
- 用户（陶柏霖）负责 skill 3.3：倾倒入盘（大）— 炒菜出锅呈盘
- 涉及设备：自动翻炒锅 KP200、锅盖、餐盘、电磁灶
- 机器人位于台面前方，台面高约 900mm、深度约 700mm
- 系统架构：IoT 平台为中心，控制页面、机器人、AI 调料机、烟机控制板、洗碗机接入
- 三级任务结构：场景任务 → 环节任务 → 原子动作
- 设备清单（KP200、7W001、U2P-i1 pro、DEV05、KD361、WB758）
- 项目阶段：原型验证和演示阶段
- V1 当前流程：上游任务移交 → 可选场景检查 → 订阅锅把感知 → 计算抓取 TCP 目标 → 左手闭合 → 提锅到准备倾倒位 → 底盘移动并保持左臂姿态 → 定位餐盘/计算目标 → 锅具 TCP 转换平移 → 播放增量倾倒动作 → 放回桌面 → 张手 → home
- 当前未决：两个 TCP 契约、中心坐标系的工程定义、抓取偏置、录制动作、放回/home 和基础流程异常恢复；抓取确认延期到后续迭代

## 机器人参数
- 类型：双臂机器人，每臂 7-DOF，末端灵巧手
- 含义：可做精细抓取、力控、双臂协同；冗余自由度利于避障和轨迹平滑
- 锅具：典型长把锅（手柄长，锅体在前），抓取点可远离高温区

## 调研完成情况
- 检索了 5 篇相关学术论文（arXiv:2310.18473, 2407.01755, 2408.01366, 2503.17501, 2505.11680）
- 查阅了 MoveIt 2 / ROS 2 Control 框架能力文档
- 对比了 5 种倾倒控制策略
- 推荐方案已写入 `.project-log/research/solution-research.yaml`
- 2026-07-22 深度调研补充了一手 ArXiv API、MoveIt 2 和 ros2_control 官方资料
- 已识别并修正：液体 ±10ml 不能外推到固体装盘；MoveIt 规划/伺服与底层力控职责需分层
- 已将“锅把抓取确认”独立为实验性业务原子 `atom-pan-handle-grasp-confirmation`
- 已新增 `task-pan-handle-grasp-spike`，优先验证抓取可靠性再验证倾倒控制
- 已审阅并确认方案1：V1 采用锅把朝左的固定场景左手单臂无确认闭环，包含感知结果订阅、餐盘定位、倾倒、轻微抖动、放回和安全接管；后续再评估抓取确认和 V2 右手锅铲辅助

## 活跃决策
- 提议采纳：示教轨迹基线 + 受限重量/力矩反馈局部修正（option-f-layered-teach-plus-limited-feedback）
- 回退：带安全限幅、超时、急停和人工确认的示教回放（option-a-teach-replay）
- 先进行 `task-pan-handle-grasp-spike`，未通过前不启动倾倒反馈 Spike，也不进入全轨迹力控承诺
- `task-pouring-validation-spike` 已显式依赖 `task-pan-handle-grasp-spike`
- 已新增 `decision-mvp-plating-fixed-scene` 与 `task-mvp-plating-pipeline`
- `DEC-003` 已由 proposed/pending 更新为 active/approved；`DEC-006` 记录当前 V1 初版不执行抓取确认；`REQ-001` revision 2 和 `TASK-007` 已同步团队、感知、底盘、TCP 与录制动作边界
- `DEC-005` 已记录 V1 倾倒点公式：`pour_point_C = plate_center_C + pour_offset_C`；所有业务坐标统一使用机器人中心坐标系

## 待确认开放问题
1. KP200 锅具手柄具体尺寸、重量和抓取点（C 级）
2. 倾倒过程是否需要双臂协同（C 级）
3. 机器人关节力矩传感器数据接口和采样频率（B 级）
4. 芦笋虾仁重量范围和汤汁比例（B 级）
5. 机器人是否能暴露 effort/关节力矩或腕部 F/T state interface，以及实际更新率/延迟（B 级）
6. 固体落料完整性、卡料和盘外洒落的观测信号是什么（C 级，影响验收）
7. 灵巧手的具体型号、指尖触觉/夹持力接口和可更换锅把夹具是否允许增加（C 级）
8. KP200 锅把是否为固定规格、材质/表面摩擦和热安全区域（C 级）

## 下一步
1. 继续 `TASK-007`，逐条澄清两个 TCP、中心坐标系工程定义、抓取偏置、录制动作、放回/home 和异常回退
2. 结合 `clarification.yaml` 对齐 `TaskPlanner → ExecuteTask → MotionExecutor → RobotDriver` 的现有承载
3. 完成后进入 `TASK-008` 技术选型，用户批准前不修改两个代码仓库
4. 澄清和选型完成后，再恢复 `TASK-002` 锅把抓取 Spike 与 `TASK-004` V1 闭环实现

## 本轮工作留痕
- Context：原推荐过度依赖液体论文指标，且未清楚拆分 MoveIt 与底层力控边界
- Decision：改为分层、受限、Spike-first 的控制路线
- Action：核验 ArXiv 摘要、MoveIt Servo/Hybrid Planning、ros2_control PID/Admittance/FT 官方文档
- Observation：官方资料支持组件能力，但不提供 KP200 接口和固体落料成功保证
- Result：调研产物新增深度证据、反面证据、修正版推荐、验证 Spike 和失效条件
- New finding：锅把抓取是 V1 基础动作，但当前 V1 初版不执行 `grasp_confirmed`，先验证无确认基础链路
- New finding：V1 倾倒点使用机器人中心坐标系下的餐盘中心点加 xyz 可调偏置，业务坐标不绑定任一机械臂基坐标系
- New finding：方案1适合作为 MVP，但“视觉定位成功”和“抓取成功”必须分开；“轨迹执行完成”和“菜品完整落盘”也必须分开
- Result：新增 `方案1整理.md`，保留原方案内容，仅按路线介绍、风险点、需要确认的点、细节补充分组排版
- Result：新增 `锅把特征检测方案1.md`，定义第一版最小特征集合、抓取目标输出、安全门控、数据结构、检测流程和后续迭代边界
- Result：根据用户补充将 `锅把特征检测方案1.md` 压缩为感知组模型需求版，核心输出收敛为锅把中心、抓取点、主轴方向及最小有效性字段
- Result：增加图片方向约定、`pcb_axis` 字段和 `grasp_point = handle_center + grasp_offset * pcb_axis` 定义
- Result：完成 `kitchen_robot_home` 与 `robot_motion_executor` 第一轮静态架构接管，建立 `ScenePerception → TaskPlanner → ExecuteTask → MotionExecutor → RobotDriver` 主链事实地图
- Finding：现有代码具备通用任务/动作执行骨架，但尚未承载感知结果契约、两个 TCP、底盘保持姿态协同、V1 倾倒闭环和菜品完整落盘验收；这些不能由当前代码行为自动推导
- Finding：`PerceptionReceiver` 已能缓存最新场景并检查 `scene_valid`，`PathRecordSkill` 已能录制命名路径，但两者都还没有形成 V1 锅具 TCP 增量倾倒回放契约；当前也没有底盘-左臂保持姿态的同步接口

## 返回主线：开始技术选型（2026-07-29）
- 用户确认暂时结束 MotionExecutor 源码阅读，回到老板电器 V1 主线，准备正式进入技术选型。
- 已恢复 TASK-008、RES-002、DEC-003/005/006/007/009 及 ARCH-001 的现有上下文；本阶段仍不修改产品代码。
- 当前选型主问题拆分为：
  1. V1 业务阶段和动态 Policy 的承载方式；
  2. Planner 与 MotionExecutor 之间的数据/Action 契约；
  3. 中心坐标系、抓取 TCP、锅具 TCP 的转换归属；
  4. 底盘协同和阶段屏障接口；
  5. 锅具 TCP 局部增量轨迹的录制、存储和运行时回放；
  6. 参数配置文件和 ROS 2 参数注入方式；
  7. 现有 API、Skill、MotionPrimitive 的复用与扩展边界。
- 现有 RES-002 已给出初步推荐，但尚未逐项与用户确认；后续按“候选方案→代码证据→适用边界→推荐→需要批准的决策”推进。

## 2026-07-30 三个执行边界的源码确认

- 坐标系：Executor 内部 `Pose3D`/`CartesianWaypoint` 和 `MoveCartesian` 链路按机械臂 base frame 解释，服务没有 `frame_id`；不能把中心坐标 C 的目标直接发送。推荐由 Planner 在构造现有 `TaskTarget` 前完成 C→左臂 base B 转换。
- 控制对象：Executor 数据类本身没有声明 flange/TCP；当前可见 xCore SDK 适配层把输入按 `flangeInBase` 处理并用 toolset 做 flange-to-end 转换，但目标运行时 Driver 是外部 deb，且 `GetArmPose.srv` 注释和旁支 Driver 实现使用 TCP/end 语义，必须以锁定 deb 做黑盒确认。
- 倾倒回放：现有 `CartesianTrajectorySkill` 只支持 Planner 传入的绝对航点，现有 `PathRecordSkill` 是直连 xCore 的录制能力，不能直接作为正式回放链路。最小方案是新增执行仓库内部 Skill/Adapter，读取法兰增量轨迹，在左臂 base 下展开后复用现有 `MoveCartesian`；不修改公共消息、不绕过 RobotDriver。
- 问题 4 已确认：本子任务可以在 `robot_motion_executor` 内新增专用 Skill，使用现有扩展点完成回放；“是否允许新增 Skill”不再是阻塞项。尚需验证的是目标 Driver 的当前法兰位姿获取接口和 `flangeInBase` 语义，属于实现前技术验证，不是架构准入问题。
- 待架构组确认问题收敛为 3 项：目标 Driver 的 `/robot_driver/move_cartesian` 输入是 flange 还是 TCP、`toolset.ref` 是否自动参与坐标转换、目标 `.deb` 是否提供并正确定义 `/robot_driver/get_arm_pose`。新增 Skill 已确认可行，不再列为问题。
- 本轮没有修改产品代码；新增/修正技术记录见 `DEC-013`，`DEC-012` 已被“复用现有消息的内部法兰约定”替代。

## 2026-07-30 三个接口问题源码确认结论

通过 ShHai 完整 Driver 源码 + boss_electrics 自有 SDK 适配器的联合证据链，三个问题全部被确凿回答。

### 证据链

**Q1: `/robot_driver/move_cartesian` 输入是法兰还是 TCP？**
→ **法兰（flangeInBase）**

证据：`lbot_robot_xcore.py:355-363`：
- 从 `position/euler` 构建 `target_flan = [px,py,pz,rx,ry,rz]`
- 变量名写为 `target_flan`
- 调用 `self._flange_to_end_pose(target_flan)` 转换为 `endInRef` 后送入 SDK
- docstring：`将 flangeInBase 6D 位姿转换为 endInRef 6D 位姿`
- 下游：SDK 适配器完整输入/输出都是 flangeInBase 语义

**Q2: `toolset.ref` 在 Driver 中的真实语义和作用？**
→ **定义 SDK 中 `endInRef` 的参考坐标系原点**

证据：`luoshi_arm.py:106-130`：
- `toolset.load.mass/inertia/cog` 配置负载
- `toolset.end.trans/rpy` 定义 TCP 相对于法兰的偏移
- `toolset.ref.trans/rpy` 定义工作坐标系原点
- 通过 `self._robot.setToolset(toolset, ec)` 发送到 xCore 控制器
- `lbot_robot_xcore.py:1976-1978` 的 `FlanInBaseToEndInRef` 函数需要 `base_in_world`、`toolset` 和 6D 位姿三个参数
- `_end_to_flange_pose()` 反向转换同理
- 若 `ref = [0,0,0,0,0,0]` → `endInRef = endInBase`

**Q3: `/robot_driver/get_arm_pose` 是否存在，返回法兰还是 TCP？**
→ **存在，返回法兰（flangeInBase）**

证据：
- `robot_driver_node.py:701-710`：服务回调调用 `active_robot.get_arm_pose(arm=arm)`
- `lbot_arm.py:122`：`get_arm_pose()` 调用 `self.robot.get_cartesian_pose(arm)`
- `lbot_robot_xcore.py:265-270`：`get_cartesian_pose()` 调用 `_query_cartesian_pose()`
- `_query_cartesian_pose()` in `lbot_robot_xcore.py:1954`：`self._robot.posture(self._xcore.CoordinateType.flangeInBase, ec)` → 明确返回 **flangeInBase**
- 注释虽然写`获取臂末端TCP位姿`，但实际 SDK 调用使用 `flangeInBase`
- 回调中 `response.position = position; response.orientation = orientation` 字段正是 flangeInBase 值

### 对技术选型的影响

- DEC-013 已从 proposed 升级为 active
- 所有不需要问架构组的问题不再需要列出
- 这三个问题明确后，技术选型目前剩余的不确定项是：
  1. 左臂 base B ↔ 中心坐标系 C 的变换方向确认（代码已有标定脚本，需要核实）
  2. 后续在机器人上验证时做 replay spike（DEC-011），验证不同起始位姿下的法兰增量轨迹一致性
- 新增 Skill 已确认可行，不再属于待澄清项


## 2026-07-30 toolset.end 冲突风险确认与 DEC-014

- 通过源码分析确认了 toolset.end 的完整链路：`robot_params.yaml` → `luoshi_arm.initialize()` → `setToolset(toolset, ec)` → 写入物理机器人控制器 → `_sync_toolset_from_robot()` 读回 → `_flange_to_end_pose()` 使用
- 确认若其他子任务修改 `toolset.end` 为非 identity 值，会影响本子任务的所有 `_flange_to_end_pose/_end_to_flange_pose` 转换，因为 driver 的 flange→end 转换会自动生效
- 确认解决方案：`toolset.end` 保持 identity，本子任务的两个 TCP 参数（tcp_grasp、tcp_pan）定义在 `pan_pour_params.yaml` 中，在 Planner 层完成 TCP→法兰反解后下发法兰目标
- 当前按单人任务模式推进，团队协作时的配置冲突问题暂不处理
- 已新增 `DEC-014`，用户 approval 标记为 approved
- 产品代码仍未修改

## 2026-07-30 技术选型完成，用户确认 DEC-013/DEC-011

- 用户正式确认 DEC-013（复用 ExecuteTask，内部法兰约定）和 DEC-011（选型七法兰增量轨迹适配复用路线）
- 至此所有 12 个决策全部确认，技术选型阶段 **solution-research 完成**
- 用户要求：技术参数留空占位，先不开始写代码
- 下一阶段：engineering-landing（工程实施）
- 产品代码仍未修改

## 2026-07-30 技术选型完成后的两个待确认问题

- **OQ-008：倾倒回放 PlanType 复用**
  方案：复用 PLAN_CARTESIAN_TRAJECTORY，在 PlannedStep 中新增可选 trajectory_id 字段，builder 检测到后加载增量文件做 T_current @ Delta_i 展开。不改枚举、不改 Action 消息。等待用户确认。

- **OQ-009：底盘移动后的等待策略**
  方案：PanPourPolicy 在 hold_wait 阶段先固定等待 N 个 tick，之后才开始检查餐盘。设置 _MAX_HOLD_CYCLES 超时保护。等待用户确认 N/MAX 初始值。

记录位置：.project-log/business-logic/open-questions.yaml（OQ-008、OQ-009）

## 2026-07-30 TASK-010 已实现并验证

- 已在 `kitchen_robot_home/src/dexbot_task_planner/` 实现 Planner 私有调度结果：`PolicyDecision(EXECUTE | WAIT | COMPLETE)`。
- `TaskPlannerNode._on_tick()` 现在只在 `COMPLETE` 时置 `SUCCESS` 并清理 `_active_task_id`；`WAIT` 仅更新 `current_phase`、保留 Policy/任务上下文/IDLE 状态且不发送 `ExecuteTask`。
- 旧 Policy 无需迁移：`PlannedStep`/`BimanualStep` 自动适配为 `EXECUTE`，旧 `None` 自动适配为 `COMPLETE`。未知返回值进入 Planner `ERROR`，不会静默完成。
- 测试：12 项定向 pytest 通过；`dexbot_interfaces` 与 `dexbot_task_planner` 构建通过；新增文件及 BasePolicy 的 99 列 lint 通过。
- 验证限制：未启动真实 ROS 节点、MotionExecutor 或硬件；工作区包级 lint 受既有 3,173 条 flake8 问题和 SDK 文档问题影响失败，已记录为基线限制。
- 下一步：`TASK-011`（独立 pan_pour 参数模板 + 纯 SE(3) 计算模块）。保持 `toolset.end` identity，不修改全局 `robot_params.yaml` 或公共 ROS 接口。
