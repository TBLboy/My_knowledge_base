## 当前会话（2026-07-28 第二轮）

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
