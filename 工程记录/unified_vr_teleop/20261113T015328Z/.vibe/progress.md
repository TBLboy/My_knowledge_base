# 项目进度

## 已确认方向

- 统一平台承载多构型的 VR 遥操作采集、DAgger 等功能；目标是在新工位使用同一版本，通过适配与现场配置运行，不按机械臂维护平台分叉。
- 当前工作对象为 `unified_vr_teleop_franka/` 的 `feat/franka`，基于 master `374410f`；原 `robot_capture_franka/` 为参考，不修改其业务链路。
- 所有子仓库和 worktree 共用本根目录 `.vibe/`。

## 双平台两层架构（2026-11-02 澄清收口，基线 draft）

- mentor 新方向：平台拆两层。第一层 = Web 操作台 + 数据来源硬件端点（XR + 三路相机，未来音频；后续新增 Meta/SpaceMouse 操作设备）+ ZMQ + 中间层（防腐层），是公司对外提供的标准数据来源产品；第二层 = 可插拔控制调度层（自研后端 / RLinf / 第三方同等待遇走 A/B/C 接口）。
- 澄清 Task `dual-platform-boundary-clarification` 已完成（31 条原子，六组）：A 分层归属 / B 硬件边界与启动阶段契约 / C 操作命令与状态词典 / D 压力测试裁决（按臂建模、任务统计扩展类）/ E 输入设备三件套（双订阅面、operator_engaged 统一语义）/ F Web MVVM（纯 Python ViewModel、词典贯通到像素）。
- 关键裁决：相机等一切非机械臂硬件归第一层；机械臂本体归第二层；B/C 词典第一层定死一套（启动/关闭/使能/暂停/复位/录制控制/健康检查/异常恢复/控制权切换），状态集按臂建模；机器人参数设置下沉第二层；操作意图目录同源（VR 按键与 Web 按钮同一词典）；A 流连续控制双订阅面（设备信号流+派生目标流）；operator_engaged 第一层统一判定（安全行为设备无关）；MVVM 目标结构+新页渐进。
- 产出：基线 `.vibe/requirements/dual-platform-boundary.md` v1.0 draft（待 mentor 评审转 active）；mentor 评审版 `mentor-review-two-layer-architecture.md`（项目根目录）；《双平台开发约束》原文存 `.vibe/docs/双平台开发约束.md`，整体降格为 RLinf 实例对接规范。
- 现有资产不推翻只搬家：相机驱动/同步流/主时间轴留第一层；runtime/worker/adapter 链路下沉第二层①；HDF5 基线 v1.0 不动；FlowRunner 阶段协议搬到第一↔二层；teleop_target 契约升为派生目标流协议雏形。
- 六场景压力测试（DAgger/推理评测/多任务/多臂/操作台离线/远程监控）无撞墙项；未测性能维度（A 流双订阅面带宽）与组织维度（拆仓后代码所有权），属架构决策阶段。
- 未决（不阻塞评审）：统一语义事件集映射表（独立工作项）；数据管理归属（C6 暂缓）；旧链路退役时间点；§14-2/§14-4 推论待 mentor 确认。

## 输入坐标语义澄清（2026-11-02，进行中）

- 已决定设备信号流采用「统一语义信号 + 保留运动模式」：Pico/Meta 的 VR 输入归一为 `operator_frame` 下的 `pose_delta`，SpaceMouse 归一为同一 `operator_frame` 下的 `velocity`；不把两种物理范式伪装成同一种数据。
- 每个输入硬件端点必须声明手性、轴方向、单位、旋转表示、输入类型、死区/范围和按键语义；第一层负责厂商坐标 → `operator_frame`，第二层不得依赖设备厂商坐标。原始数据可作诊断，不作为正式控制契约。
- 机械臂坐标描述由第二层通过 C 发布 `robot_frame_descriptor`（base/EEF/TCP 语义、单位、四元数顺序、operator_frame→robot_base 映射、版本）；第一层缓存消费，不复制维护；EEF 状态/目标引用版本，描述变化使旧目标失效。
- 缺少有效坐标描述或版本不匹配时采用 fail closed：第一层可继续发设备信号/诊断流，但不得生成派生 EEF 目标，第二层不得用零值、上一帧或默认坐标猜测。
- VR 手柄-机械臂映射为自然规则（左控左、右控右，非配置项，不提供跨侧映射）；SpaceMouse 分配规则留到实际接入时定。
- 相机侧（H1）：沿用现有 camera/core 驱动注册表 + 能力对象 + 业务层零型号依赖抽象，整体归第一层；对外视频流只承诺契约（帧/时间戳/能力声明），能力不足明示不支持，不降级伪装。
- 当前 Task：`input-coordinate-semantics-clarification` 已完成；基线共 39 原子，待 mentor 评审。

## 已批准的统一平台标准（2026-10-29）

以下为用户确认的目标标准，不表示当前代码已实现；后续按增量逐步靠拢，不据此直接启动整体重构或修改公共模块。

- **公共流程统一**：PICO → 统一输入层（接收、时间戳、有效性、连接恢复）→ 公共遥操作层（按键、使能、Grip 锚定、人工/策略控制权）→ 机器人适配层 → 驱动通信 → 硬件。公共流程复用；机型/工位参数可以不同。
- **差异集中到适配层与配置**：坐标映射、关节/笛卡尔目标转换、六轴/七轴运动学、限位/工作空间、夹爪、保持、复位及故障恢复由机器人适配实现，不在公共页面、控制权和采集流程中散布机型判断。
- **采集是旁挂链路**：相机/音频、标准化机器人状态、控制参考和事件进入公共同步、录制、回放、导出与上传；采集存储不得成为运动控制关键路径，不直接依赖具体机械臂 SDK。允许读取标准机器人描述，不要求所有机器人硬件能力相同。
- **动作与状态语义明确**：分别表达遥操作/策略请求目标、经约束后实际提交给驱动的控制参考以及硬件实测状态；提交参考不等于物理执行完成确认。记录控制来源、接管事件及数据有效性，不能将反馈冒充控制命令。
- **统一数据契约，而非按机型各建一套**：统一文件结构、字段命名、版本规则、时间戳、单位、坐标系、四元数顺序、状态/动作语义、控制来源、有效性与缺失标记，以及机器人/传感器描述。六轴/七轴、单臂/双臂的数据维度允许不同，由描述信息明确表达；不截断第七轴，不把夹爪混作机械臂关节。
- **尚未冻结具体技术规格**：字段路径、格式版本、历史数据兼容/迁移策略、缺失设备业务规则以及是否统一为 TCP 策略动作，仍需后续分别澄清确认；不能仅凭此标准宣称跨机型策略或历史数据已兼容。

## HDF5 新数据落盘业务基线（2026-10-29）

- 用户提供的《Robot Capture HDF5 输出业务基线》已作为本项目新数据落盘的业务约束；附件《自采数据 HDF5 落盘规范》作为格式参考，原文已保存至 `.vibe/docs/自采数据 HDF5 落盘规范.md`。只改新采集数据，不自动迁移历史 HDF5；不改 Franka 控制算法、安全参数或 `cam_dup`。
- 新 episode 统一写主时间轴、JPEG、本体状态、EEF action、任务元数据；缺失数据不写、不补零、不伪造，真实零值必须保留。
- Franka `robot_id` 固定为 `Franka Research 3`；单臂使用 `main`，双臂使用 `left/right`；EEF action 为 `action/<side>/eef_pose (T,7)` 与 `gripper (T,1)`，姿态 `[x,y,z,qx,qy,qz,qw]`，不得把实测 EEF 冒充 action。
- HDF5、task、batch、episode、manifest、MD5、原子写入和 `_SUCCESS` 按基线实施；未封口 batch 不视为完整交付。废弃 episode 保留文件和编号，异常 episode 待人工质检后再上传。
- 基线明确覆盖参考规范中的冲突：不实现 `cam_dup`；不使用 joint action；字段具体版本、历史兼容、缺失帧业务处理、质检拒收对 batch 封口的规则仍需技术设计或后续澄清。
- 用户进一步确认：禁止的是用全 0 **伪造/占位**缺失数据，不是禁止真实 action 或状态出现全 0；真实采集到的全 0 必须原样保留，不能用“整列全 0”作为缺失判断。此前关于“每帧必须有有效 action、否则拒收”的建议撤回，不能据此固化业务规则；action 的逐帧缺失语义需基于实际采集流程继续设计。
- 业务基线已按当前框架规则迁移到 `.vibe/requirements/README.md` 与 `.vibe/requirements/hdf5-recording-format.md`；不再使用错误的根级 `.vibe/requirements.md`。当前 baseline v1.1 只保留 HDF5 与统一采集语义，人员分工、实施顺序和完整架构计划不混入业务 baseline。录制期间一段时间无 action 的处理暂不解决；整条 episode 无 action 时 `has_action=false` 且不创建 `/action/`。
- 2026-10-30 汇报讨论稿已保存到根目录 `framework-architecture-discussion.md`，记录目标 HDF5 键树、字段来源、任务配置、落盘封口、action 间歇缺失未决方案及现行 Franka schema v3 与目标契约的差异；`observation/state` 子字段等仍未冻结，本次未改 active baseline 或业务代码。
- 新增独立 baseline `.vibe/requirements/unified-platform-integration-boundary.md` v1.0，记录柏霖/小航/桉池/姜灏分工、公共设备发现/VR 启动/控制/采集边界、按型号适配连接与控制、config 驱动 Web 页面，以及 VR 到 `rlinf_pipe` 的解耦边界。
- `unified-platform-integration-boundary` 已升级为 v1.1：用户批准 PICO → 统一输入层 → 公共 runtime 输出统一 TeleopTarget → 通用 worker → RobotAdapter → 驱动通信 → 硬件的目标架构。worker 只负责通用执行生命周期/安全协议；运动学、EEF/关节转换、夹爪、限位、复位和故障恢复属于 RobotAdapter。当前 Franka 独立 runtime 明确为过渡实现，后续再收敛，不在当前 Franka 功能适配阶段直接重构公共编排。
- 已确认当前 `unified_vr_teleop*/Dagger_web/` 下没有独立 `runtime/` 代码目录，公共 runtime/worker 代码实际位于 `app/teleop/`。先在 `feat/franka` 分支将 Franka 收敛为公共 `app/teleop` runtime/worker + `robot/franka` adapter + `config/robots/franka.yaml`，再合并 master，其他构型后续按该形态对齐。
- DAgger/推理/评测清理已按清单落地：删除纯策略模块、策略 UI/脚本/测试和策略配置，裁剪公共控制、工作流、页面与 Franka 过渡 runtime；保留普通 VR 采集、录制、上传、采集数据回放质检和机器人控制。清理相关静态引用审计、编译和离线测试已通过。
- `unified-platform-integration-boundary` 升级为 v1.3：每个 `robot/<type>/` 还需提供构型专属设备状态检查逻辑；公共 Web 只提供统一检查入口和结果展示，按 config 选择检查实现，公共页面不得直接访问厂商协议。

## 当前状态（2026-11-02 收尾）

**代码基线**：`feat/franka@93638aa`，本地与工控机 `192.168.10.38` 同版本。

**本日提交链**（均已推送 `origin/feat/franka`）：

| 提交 | 内容 |
|---|---|
| `71268ed` | 修复采集只录到 1 秒：`gripper` 未登记进 action 白名单导致每帧抛错、整帧被丢 |
| `1be0398` | 相机 dataset 改用元文档命名；root `arms` 与文件内实际侧名一致 |
| `c1bbf79` | 相机改原生 HD720（1280×720 零缩放）+ 固定 5000K 白平衡 |
| `2982642` | 曝光改用 `brightness`/`contrast`（固件无曝光控件，`gain`/`gamma` 实测无效） |
| `683ef2e` | 播放页 500：`_task_configs` 被当成任务名 |
| `b68da6d` | 五项格式差异：六位补零文件名、标准 `sensors`、`tcp`/`tcp_offset`、`base_extrinsics`、相机身份 |
| `0b515a9` | TCP 改为声明实际末端点、不做换算 |
| `0b19d2c` | 末端点校验抽到 `robot/core/tcp.py`，任何机型复用、无硬编码偏移 |
| `383af2d` | 新增 `project` 任务字段，只写 manifest |
| `93638aa` | 更新 `docs/robot-adapter-integration-guide.md` 到当前基线 |

**测试**：本地与工控机均 **470 passed / 46 subtests**，compileall 与 `git diff --check` 通过。

**已验证的真实链路**（工控机，右臂只读、未下发运动指令）：
- 三路 ZED 真实身份：`cam_wrist_left` ZED-M 12989796、`cam_head` ZED 2i 39897211、`cam_wrist_right` ZED-M 13482374；
- 4 条真机轨迹（episode 000010–000013）逐项审计通过：六位文件名、`sensors` 与图像 dataset 身份一致、1280×720、`tcp=fingertip_center`/`tcp_offset=0.16`、三路视频零重复帧、时间戳严格递增、夹爪指令 0 为真实闭合（存在多个中间值）、manifest 的 md5/字节数/帧数与磁盘一一对应；
- 记录位姿与机器人 `O_T_EE` 逐行相等（零换算）。

**工控机现状**：测试数据已清空（`runtime/recordings` 720M→8K，hdf5 归零，索引库与批次状态一并重置），任务列表为空，采集服务未启动。站点 `config.yaml`/`franka.yaml` 保持现场值（UVC 三路、brightness 2/contrast 4/5000K、tcp fingertip_center/0.16、两臂 reset 姿态）。

**下一步（未开始）**：新建任务时填 `project` 后从头采集一批正式数据；`left` 腕部相机对着天花板、`right` 视野几乎全是台面，需现场调整机位。

## 平台摸底（2026-10-29）

- 主线控制、遥测分派支持 Piper 和 ARX5；UR7e、Franka 被代码门控为待开发。ARX5 配置尚缺型号、URDF、末端、关节名与夹爪标定；不能据源码声称现场可直接使用。
- 公共链路包含 NiceGUI 页面、设备预检、XR 输入、控制进程编排、控制权、episode、相机同步、录制、回放、HDF5 和上传。ARX5 独立实现控制/运动学/映射/复位/恢复，经 ROS2 transport 接入共享六轴采集格式。
- DAgger 有控制权切换和记录实现，本地策略为规则而非训练模型；轨迹执行回放仅 Piper 开放。RL 是流程联调，无训练更新。
- 重要：`origin/feat/piper-modechange`（8807476）不止 Piper 改动，已有 `robot/franka/`、七轴 schema v3、UVC、公共采集改造和 Franka 测试；尚未合入 master。后续应先确认其来源与是否团队认可，避免重复实现。
- `origin/feat/ur7e-rlinf-bridge`（32c4d93）通过独立网页/UNIX socket 对接外部 RLinf，由外部执行端负责控制、采集、DAgger 与数据保存，并非主线 registry 控制器适配。
- 详细依据与下一步建议见 `.vibe/platform-onboarding.md`。本轮只读源码，未运行硬件或测试套件；系统 Python 缺 pytest。

## 已知限制

- Skill 触发词与用户语言不匹配的漏路由风险（2026-11-02 实证）：用户说「归档一下这个过程，记得 push」，意图与路由表中「Archive a V2 project memory snapshot → a-project-archive」几乎逐字对应（含 push 语义），但触发条件为英文、用户表达为中文，Agent 未查路由表而是自造了"复制三份文档进业务仓库"的平行流程（无 manifest/校验/全量），后经用户提醒才加载 skill 补做正规归档（快照 20261102T111008Z）。复现：任何中文口语触发词（归档/备份/存档）都可能绕过英文触发表。期望：Agent 收到疑似 skill 意图时先查路由表再行动；建议框架为 skill 触发条件补充中文别名或要求 Agent 在动名词性动作（归档、初始化、评审等）前先扫一遍路由表。涉及：系统提示的 V2 capability Skill routing 表、a-project-archive skill 描述。
- 采集端自检与拒收、`_SUCCESS` 批次封口、`language/` 音频、action 在 hold/失控时的缺失、不完整帧的正式策略，均**未实现**（已批准基线声明暂缓）。当前只走临时安全策略：导出时裁掉首次 action 之前的 state-only 前缀，之后的空档与已声明字段缺帧则拒绝导出。
- 录制链路上的 Franka 过渡分支仍在（`recorder.py` 固定 `robot.type="franka"`、`franka_telemetry.npz` 命名、`sessions.py` 回放回退），只影响旧 schema 的原始遥测；v2 记录走 `recording_frames.json`，与机型名无关。接入新构型前需按 `docs/robot-adapter-integration-guide.md` §3.5 审计。
- 两臂基座未标定，`base_extrinsics` 写 `unknown`。
- 相机身份依赖 pyzed：SDK 缺失或被占用时写 `unknown` 并告警，不伪造序列号。
- 待讨论需求（2026-10-29）：采集数据时记录相机内参和外参，已在 `requirements/hdf5-recording-format.md` 的变更候选中记录。可行性、参数来源、外参参考系和缺失处理尚未确认；不改变 active v1.1、不新增当前强制验收项，暂不实施。

- 三方差异见 `.vibe/franka-adaptation-comparison.md`：归一化导入后17个原驱动文件中15个AST一致；同事适配重接了输入/生命周期/采集。主动重标定与当前姿态设为复位目标的旧入口未接入；按键、复位夹爪行为、缺失数据策略和HDF5字段有差异。左侧复位Z与当前原rig相差约16cm，不自动迁移标定。用户表示代码可能由同事参考原工程完成，待沟通处理，不合并或重复实现。

- Vibe 多仓库记忆根目录解析：Session 移到 `unified_vr_teleop_franka/` 后，在总根目录 `.vibe/tasks/platform-onboarding.json` 写入 Task，再调用 `vibe_task_control(start)`，实际返回 persisted Task file could not be read；期望按根 AGENTS 第 9 条读取共享 Task。涉及根 AGENTS、根 Task 文件及框架 Task 路径解析。临时将 Session 工作目录恢复到总根后 start 成功；业务读取仍明确定位 Franka worktree。未改框架代码，未在子目录建立 .vibe。
- Franka 架构对齐审计见 `.vibe/franka-adaptation-alignment.md`：Franka 的连接/控制代码已配置化并集中在 `robot/franka/`，但通过独立 `robot.franka.runtime` 绕过 Piper/ARX5 使用的公共 `control_runtime`/`control_worker`；公共编排层仍有 Piper 硬编码。UR7e 在 master 仍是 pending。当前总 `.venv` 测试因缺少 scipy 在收集阶段阻塞，未取得通过证据。
- 清理后的完整测试套件收集到 324 项；清理相关选择集为 67 passed、9 subtests passed。完整套件剩余 3 个既有失败：Piper fake 未提供 `MotionCtrl_2`、上传脚本目的路径断言漂移、human 速度上限断言不符；未将其误归因于本次清理。

## Franka 控制语义对齐与架构规范化（2026-10-30，feat/franka 未合 master）

- Franka 控制链路已收敛为：`robot/xr/receiver`（含摇杆按下）→ `app/teleop/eef_runtime.py`（公共：ReleaseButtons 按键状态机、使能/暂停、Grip 锚定、标定、复位/退出请求、按键事件流）→ `app/teleop/adapter_worker.py`（公共：租约 500ms、目标看门狗 200ms、序号/时效、复位编排）→ `robot/franka/adapter.py`（FrankaAdapter：参考版复位序列 hold→闭爪→插值→开爪、保存复位姿态、诊断）。`robot/franka/runtime.py`、`worker.py` 仅兼容再导出。
- 按键语义与 `robot_capture_franka` 一致（随机 80000 步 0 差异）：左菜单长按使能/短按暂停；右摇杆标定；左摇杆开始录制；Y 保存；X 丢弃；A+X 录制中丢弃、空闲复位。退出只保持不复位。复位姿态为可调参数（`config/robots/franka.yaml`），UI 提供「保存当前姿态为复位目标」并自动重载配置。
- 按键事件经 `runtime/data/control-events.jsonl` 到 `RecordingSession`（web 进程），控制进程不接触存储；Piper `control_runtime` 同样发 record_start/success/discard。
- 离线验证：全套 309 passed / 3 既有失败。**未做真机验证**，现场验收需用户授权。

## Franka 工控机 uv 环境（2026-10-30）

- 远端 `/home/embody/Project/robot_capture_franka/unified_vr_teleop` 为 `feat/franka@2e29e35`。`Dagger_web/runtime/.venv-ui` 已用 uv 0.13.5 + Python 3.12.3 创建，清华镜像安装并生成未提交的 `Dagger_web/pyproject.toml`、`Dagger_web/uv.lock`；25 项直接依赖与现有默认依赖选择一致。
- `verify_env.py` 全部通过；完整测试 309 passed / 14 skipped / 3 个既有失败。未启动真实设备。
- 原生 `xrobotoolkit_sdk` 已编译，但不属于 uv.lock；`uv sync --locked` 会卸载它，重同步后需重建。干净机编译还需 `nlohmann-json3-dev` 和 PC Service SDK include 头文件；现有 install.sh 未完整覆盖这两点。Franka 环境随后已合并，见下节。

## Franka 统一 Python 环境（2026-10-30）

- 远端 Franka 依赖已并入主 `requirements.txt` / `pyproject.toml` / `uv.lock`，与 Web、XR、采集共用 `runtime/.venv-ui`（Python 3.12、NumPy 2.3.5、SciPy 1.18.1）。旧 `robot/franka/requirements.txt` 已删除，配置与诊断不再引用 `.venv-franka`；`install-franka.sh` 仅为统一安装兼容入口。
- 统一环境中 Franky、Robotiq 串口依赖和重建后的 XR 绑定均导入通过；`robot.core.check franka` 通过。完整测试仍为 309 passed / 14 skipped / 3 个既有失败。未连接真实设备；远端改动尚未提交或推送。

## 操作员体验重构基线（2026-10-30）

- 真机首测后完成业务澄清，`.vibe/requirements/teleop-startup-shutdown.md` v1.0 active：采集页两组独立按钮；单一“启动遥操作”按构型注册流程、阶段弹窗、可取消；关闭三选（复位后关闭/不复位/取消）且关闭整条链路含 XR；全局机型上下文驱动共享 URDF 显示（回放按录制元数据）；单一设置页 4 标签；全局唯一健康检查；异常/复位统一为 adapter 注册的 5 类流程 + 全局控制状态；分支卫生清理 DAgger 遗留。
- 已定位缺陷：Franka 复位期间夹爪阻塞 I/O 触发公共 250ms 夹爪新鲜度判定 → worker hold 取消复位、VR 失去使能（ux-02）。
- 实施顺序 ux-01 卫生 → ux-02 复位修复 → ux-03 流程执行器+Franka 流程+采集页 → ux-04 机型上下文/共享 viewer → ux-05 单设置页 → ux-06 Piper/ARX 接入。
- 2026-10-30 根目录 `framework-architecture-discussion.md` 已补充界面信息架构、按构型注册的一键启动、关闭/复位/故障恢复、四标签单设置页、只读健康检查、共享 URDF viewer 与全局控制状态；内容来源于 active `teleop-startup-shutdown` v1.0，并与 ux-03…06 的实施状态分开。
- 2026-10-30 已生成正式 mentor 汇报稿 `framework-mentor-report.md`，压缩为系统架构、数据落盘链路、业务逻辑和代码架构优化三章；保留当前验证证据、未合 master、真机未验收、HDF5 迁移与 action 未决等边界。
- 2026-10-30 基于 `feat/franka@26d3055` 新增 `Dagger_web/tools/docs/robot-adapter-integration-guide.md` 并加入文档索引，面向后续 feat 构型开发者说明公共 EEF 链路、DeviceWorker  duck-typed adapter 契约、profile/registry/flows/telemetry/viewer 接入点、采集与 HDF5 过渡债务、测试和真机验收；文档明确禁止复制机型私有 runtime/HDF5 分支。

## 操作员体验重构落地（2026-10-30，ux-01..ux-06 完成）

- feat/franka 六个提交全部推送：c09f2db(卫生) e4f2c9a(复位夹爪修复) 45f99a7(流程执行器+Franka流程+采集页) 9526cc4(机型上下文/共享viewer) 356cfc1(单设置页) 26d3055(Piper/ARX注册)。
- 新公共层：app/teleop/flows.py(FlowRunner) + flow_stages.py(阶段库) + control_state.py(统一控制状态) + flow_service.py(TeleopFlows)；app/ui/flow_dialog.py(统一阶段弹窗/关闭三选/故障三选)。
- 流程注册：robot.core.registry.flows_for → robot.franka.flows / robot.piper.flows / robot.arx5.flows（各注册 startup/shutdown/health_check/reset/recover）。viewer 模型：registry.VIEWER_MODELS + robot_context；arm_viewer.mjs 单一 resolveModel。
- 设置页合并为 通用/头显/机械臂/采集参数；删除 ui_devices.py/ui_teleop.py；导航五项。
- 离线回归 325 passed / 14 skipped / 1 failed（既有 test_source_velocity_limit_reaches_requested_speed[human-4.0]，未动）。
- 待用户真机验收：Franka 启动/关闭/复位(A+X不再VR锁定)/健康检查/共享 fr3 模型/单臂单 pane；工控机 git pull 后 uv sync --locked 并重建 XR 绑定。

## 后续工作顺序（2026-10-30）

- 另一工作线正在执行 `robot-adapter-abc-contract`：只固化 RobotAdapter ABC、Franka 继承模板、契约测试与接入文档，不改变运行语义，也不改 HDF5、录制、上传或公共 UI。
- 用户确认：本 Session 现在即可**假设该 ABC 任务已完成**，并行澄清数据采集链路业务逻辑，避免等待；该假设不修改 ABC 任务实际状态。采集代码实现仍以 ABC 任务实际完成（R1～R5 验收并提交推送）为前置，澄清阶段不提前改业务代码。
- 采集澄清已确认相机同步帧组驱动主时间轴、真实 60fps 可配置且不得伪造扩帧；action 间歇缺失与不完整候选帧处理由用户明确要求暂缓。完整未决清单见 `.vibe/docs/数据采集链路业务待澄清清单.md`。

## RobotAdapter ABC 模板固化（2026-10-30）

- 基线 `.vibe/requirements/robot-adapter-abc-contract.md` v1.0 active；提交 `d33d03e` 已推送 `origin/feat/franka`。
- `robot/core/adapter.py` 从 Protocol 改为 ABC；`FrankaAdapter` 显式继承，registry 返回统一类型。设备契约与 flows 保持分离，Piper/ARX 控制路径未动。
- 新增 `tools/tests/test_robot_adapter_contract.py` 与 `tools/docs/robot-adapter-integration-guide.md`：不完整实现实例化即 TypeError，Franka 反馈/校验/保持/复位/关闭契约通过。完整离线 339 passed / 14 skipped / 1 既有失败。

## 头显省电版兼容修复（2026-10-30）

- 真机启动报“USB 头显：ADB 执行失败”根因：USB/ADB 正常，但头显安装的是 `com.modelbest.xrlink.powersave`，上位机只探测旧 `com.modelbest.daggercontrol`；新版协议身份为 `ModelBest XR Link`。
- 提交 `fd94f41` 已推送：`xr_link.py` 同时探测两个包并按实际包校验协议身份，保留旧 APK 兼容。真机只读验证应用启动与 state 通道成功（app=ModelBest XR Link、focused=True、send=False）；未启动 XR 数据发送或机械臂运动。离线 341 passed / 14 skipped / 1 既有失败。

## FCI 预检头显位姿修复（2026-10-30）

- 真机启动在 FCI 预检 45s 超时：机械臂反馈、手柄 fresh、Grip 松开均正常，但 `calibrated=false`；头显 `head=False` 导致没有有效头显位姿完成基座标定。
- 提交 `7f5abe1` 已推送：启动链路自动开启并验证 `head + controller + send`，避免只有手柄数据时永久等待标定。已在头显验证 `set head=True` 成功；离线 341 passed / 14 skipped / 1 既有失败。

## Franka 真机录制与复位修复（2026-10-30）

- 提交 `247c12a` 已推送：录制按钮定时跟随真实 recorder 状态；复位成功统一恢复 VR 使能（仍松开再握 Grip）；Y 保存/X 丢弃后自动复位；丢弃录制跳过 H5 转换，修复删除 MP4 与转换线程竞态导致的 `missing left.mp4`。
- `teleop-startup-shutdown` 基线升级 v1.1。完整离线 347 passed / 14 skipped / 1 既有失败；真机验收待用户。

## 配置单一来源重构（2026-11-01，来自用户提交）

- 已拉取 `origin/feat/franka@3d50d18`：config/config.yaml 收敛为现场可切换层（机器人型号、全局 cameras 块、teleop.arms、arms.enabled、audio、upload），机型硬件参数（CAN/IP/夹爪/采样率）只留在 config/robots/<type>.yaml。
- 新增 app/core/config_writer.py 唯一 YAML 写入器、robot/core/config_fields.py 声明式字段契约与 app/ui/robot_panel.py 通用设置渲染；设置页不再含机型分支。
- **破坏性变更**：旧 config.yaml 旧键（camera_backend、robot.selections、arms 的 CAN 字段等）在启动时直接拒绝，不自动迁移。工控机仍是 247c12a + 未提交旧格式 config.yaml，拉取前必须先备份并按新格式重写，否则启动失败。
- 本地验证：定向 47 passed；完整 364 passed / 14 skipped / 1 既有速度测试失败。

## 操作员体验基线 P1 收尾（2026-11-01）

- 提交 `97b6feb`（已推送 `origin/feat/franka`）：G2–G7 与 F4′ 全部落地。
- 采集页不再含任何设置：设置模块、接收端下拉、保存偏好、CAN 交换、连接诊断全部移除或迁移到设置页。
- 设置页：机型/操纵选中即生效并受执行门控；通用操作卡放「重新标定手柄」；机械臂页由机型声明渲染字段与操作（Franka 可编辑夹爪行程、含保存复位目标）；采集参数页承载帧率/同步/曝光/画面映射/音频/遥测。
- 头显：单滑块 + 三开关，启动走 6 阶段幂等流程并复用阶段弹窗；`xr_link` 增加 ensure_* 幂等接口。
- 布局：相机固定 3 pane、URDF 固定 2 pane，缺数据只显示「无信号 / 相机信号缺失」，不改变布局。
- 验证：375 passed / 14 skipped / 1 既有失败；演示模式 Playwright 实测三页无错误。
- 未验证：真机头显幂等重入、Franka 机械臂页真机切换、回放缺文件占位。

## 任务与代码卫生（2026-11-01）

- 任务卫生：关闭 `remove-unused-dagger-inference-evaluation`（实际清理由 ux-01 完成）、`franka-adaptation`（两个子任务完成且真机已跑通）；`unified-platform-integration-boundary.md` 版本头修正为 1.3，与索引一致。剩余唯一非完成任务：`data-collection-business-clarification`（HDF5 前置）。
- 代码卫生：删除 71 个 P1 页面清理后无引用的 `rec.*` i18n 键（136→65）；修复清理引入的 `机型` 卡 `current` 变量 NameError（曾导致 /record、/settings 500）。提交 `084f76c` 已推送。
- 卫生检查方法：compileall + i18n 孤儿键双向扫描（孤儿=0，缺失=0）+ 完整 pytest + 演示模式三页 200。

## 代码卫生尾巴清理（2026-11-01）

- 提交 `0ec8900`（已推送）：删除 `save_record_preferences`、`set_arm_sides_swapped`、`arm_sides_swapped` 状态字段、`swap_piper_arm_mapping`（UI 入口已不存在，Piper 换 CAN 走设置页字段）；`teleop_guidance.py` 从 208 行收缩到 48 行，只保留仍有消费方的 `is_reset_deviation`、`recovery_hint`、`runtime_errors`。
- 验证：372 passed / 14 skipped / 1 既有失败；演示模式三页 200 无错误。

## Franka 单主线收敛（2026-11-01）

- 提交 `b194aa1`（已推送）：删除 robot/piper、robot/arx5、robot/ur7e、旧控制链路 control_runtime/control_worker、CAN 时代脚本与 Piper legacy 录制 schema（净删 ~33k 行）。feat/franka 只保留 Franka 主线，其他构型由适配者按 robot/franka 模板（adapter+flows+config_fields+registry 注册）从 git 历史恢复重接。
- 分发点（registry/profiles/check/discovery/config）全部 Franka-only，未知机型显式报「参照 robot/franka 模板适配」；config/config.yaml 默认 robot.type=franka。
- 导出收敛：recorder 只写 franka_telemetry.npz；export_session_to_h5 直接委托 robot.franka.recording（零填充 legacy 分支删除）；视频-only 无 robot_spec 时明确报错。
- 验证：266 passed / 49 subtests；演示模式五页 200；设置页机型下拉仅 Franka。真机验收待用户。
- 注意：HDF5 统一基线（v1.1）仍未实施，且本提交删除了 legacy Piper 数据的导出兼容路径。

## 分层清理与多机型注册表语义修正（2026-11-01）

- 提交 `4becc73`（已推送）：
  - `tools/docs` → `docs`；`robot/xr` → `app/xr`（XR 属公共资源层）；`robot/common` 并入 `robot/core`（samples/telemetry 迁移，device_state/validation 零引用删除）；删除 `robot/core/contracts.py`、`kinematics.py` 转发壳。
  - 注册表语义修正：`RobotNotRegistered(capability, type)` 取代「仅支持 franka」措辞——Franka 只是当前唯一已注册机型，不是代码里的架构约束；新构型 = 实现 adapter/flows/config_fields 并在 `robot/core/registry.py` 注册。
  - 顺带：39 个孤儿 can./dev. i18n 键、requirements/pyproject 的 piper-sdk/python-can/placo/mujoco/pin/meshcat/tyro 与 ur7e extra、dependencies.py 的 --ur7e。
- 验证：266 passed / 49 subtests；演示模式五页 200。

## 工控机部署同步（2026-11-01）

- 工控机 `192.168.10.38:~/Project/robot_capture_franka/unified_vr_teleop` 已推进到 `2e42c55`（含 `4becc73` 分层清理）。
- 站点 `Dagger_web/config/config.yaml` 已迁到新格式：`cameras.backend: uvc` + 三路 `/dev/v4l/by-path/...`（8.3 / 8.2.1 / 8.4.1）、`teleop.arms: right`、`upload local → /mnt/nas/forge/piper2/raw`、`robot_name: piper2`、曝光 30 / 增益 8 保留；`robot.type: franka`。旧文件备份在 `~/config-config-old-2026-11-01-141200.yaml`，站点副本在 `~/station-config.yaml`。
- 站点配置是 tracked 文件，之后每次 pull 都会冲突。固定做法：先备份 `config.yaml` → `git checkout -- Dagger_web/config/config.yaml` → `git pull --ff-only` → 写回站点配置 → 用 `runtime/.venv-ui/bin/python -c "from app.core.config import load_config; load_config()"` 校验。
- 清理了 pull 后残留的 `Dagger_web/robot/xr`（旧构建产物，26M）、`robot/{piper,arx5,ur7e,common}` 与全树 `__pycache__`；确认 `robot.piper` 等模块已不可导入。
- 该机验证：`load_config()` 通过；离线测试 266 passed / 46 subtests；演示模式五页（record/settings/playback/stats/events）全 200，无 traceback。
- 服务未启动：该机没有 systemd unit（`tools/scripts/robot-capture.service` 只是模板），8088 端口当前空闲；启动方式为前台 `bash run.sh`，需用户确认后再启。
- 顺带修掉 `4becc73` 遗留的真实缺陷（提交 `2e42c55`）：supervisor 仍拼已删除的 `app.teleop.control_runtime` 命令、`_signature` 读 CAN/夹爪 mm 旧设置、recorder 用 `arms.controlled_arms` + `poll_hz: 200`（单臂工位会按双臂 200Hz 生成 robot_spec）；现改为 `control_entry()` + `teleop.arms` + 机型 `poll_hz`。

## 真机启动链路修复（2026-11-01，工控机）

- `c9266c9`：`robot/core/profiles.create_arm_manager()` 残留死导入（registry 已不 export 各机型 manager），真机 `bash run.sh` 在构造 CaptureService 时 ImportError；演示模式不经过该分支所以离线测试全绿。补两个回归测试：真机模式构造 manager + AST 审计 registry 符号。
- `19c8781`：启动流程 stage 调用已删除的 `service.start_can()`，连接机械臂时报 AttributeError。整条链路改成机械臂链路语义：`arms_link_states()`、`disconnect_arms()`、`link_states()/close_link()/ensure_link_ready()`；devices payload `arms.can` → `arms.arm_link`。补测试：用真实 demo CaptureService 跑 `robot_connect`/`robot_disconnect`（Mock service 接受任意属性名，掩盖了此问题）。
- `885f149`：集成测试注释保留断言依赖 `host: 172.16.0.3` 的字面格式，工控机保存过设置后变成 `host: "172.16.0.3"` 导致两处失败；改为在文件头插入标记，与格式无关。
- 已知限制：演示模式测试会写项目根 `runtime/data/processes.json`，工控机上真实模式 app 正在运行（真实 XR service 记录存活）时，`test_shutdown` 等会因「service 进程仍在另一运行模式中」失败——是保护逻辑生效，不是代码缺陷；如需在工控机上跑全量测试，先停真实 app。
- 站点 `config/robots/franka.yaml` 被设置页保存过一次（字符串加了引号），已 `git checkout` 还原成主干格式。

## 遗留命名/旧逻辑清扫（2026-11-01，`e720c39`）

- 删除死代码：`devices.enumerate_can_ports`/`CanPort`、`TelemetryBuffer.set_swap_sides`/`swap_sides`（含 Franka 覆盖）、`teleop_guidance.recovery_hint`/`runtime_errors`、`profiles.gripper_max_mm` 与 `teleop.gripper_max_mm` 镜像、`discovery.inspect_hardware(can_scan=)`、`tools/deploy/install-arx-env.sh`。
- 公共层去掉机型分支：`CaptureService` 演示模式改走 `registry.create_demo_arm_manager`；预检文案、锁定提示、XR 接收器文案不再提 CAN/Franka；`doctor.py` 用注册表 LABELS 校验机型。
- UI 文案与机型解耦：删 `app/ui/franka.py` 文本改写层，i18n 改为中性措辞（"机械臂链路"），清 16 个无引用键与 4 条 CAN 文案；`arm_viewer.mjs` 默认模型改为 Franka。
- 其它：`upload.normalize_upload_cfg` 兜底不再指向 `piper4`；安装器去掉同级 `PiperXR` 缓存回退；supervisor 去掉同级 checkout 回退，环境变量优先 `PTR_UI_PYTHON`（保留 `PIPER_PYTHON` 兼容）；`upload-piper1.sh` 排除 `/docs/`。
- 有意保留：历史日志/会话名（`legacy`、`can_start` 别名）、模板配置里的站点桶名 `piper2`、`upload-piper1.sh` 的个人目标路径（需用户决定部署约定）。
- 已知问题：工控机上 `config/robots/franka.yaml` 被设置页保存后会被重写（字符串加引号），成为本地修改；与 `config.yaml` 一样属于“tracked 站点文件”，以后 pull 前同样要 checkout/写回。
- 验证：269 passed / 46 subtests；演示模式五页 200；工控机拉取后定向测试 98 passed。

## 复位姿态保存导致配置指纹不一致（2026-11-01，`398e3f0`）

- 现象：遥操执行中在设置页保存复位姿态后，页面跳回「通用」；随后启动遥操报「FCI 预检失败：Franka worker 配置不同」。
- 根因 1：复位姿态只能由持有 FCI 反馈的 worker 读取并落盘（`FrankaAdapter.set_reset_pose` → `save_reset_pose`），worker 会更新自己内存里的 profile；web 进程仍保留启动时的旧 profile。`refresh_profile()` 只被 `RecordingSession.handle('reset_pose_saved')` 调用，即只在录制会话存在时才生效，非录制时保存就留下陈旧副本。之后 `Client.request`/预览按指纹比较，直接拒绝。
- 根因 2：`main.py` 的 1 秒 `refresh_changed_robot` 用**整份 profile 指纹**判断，任何参数变化都触发 `ui.navigate.reload()`，页面重建后回到默认「通用」标签。
- 修复：`TeleopManager.action()` 在 `set-reset-pose` 成功后调用 `refresh_profile()`；页面重建改为只在**机型类型**变化时触发；`robot_panel` 保存字段后原地刷新输入框，不再整页 reload。
- 证据：`runtime/logs/events.jsonl` 中没有任何 `flow_health_check` 记录——健康检查并未自动启动，用户看到的是启动失败弹窗里的「运行健康检查」按钮。
- 运维提醒：`config/robots/franka.yaml` 与 `config/config.yaml` 一样是 tracked 站点文件；**不要**在工控机上对它执行 `git checkout --`，那会抹掉操作员保存的复位姿态（本次同步中发生过一次，已按原值 7 个数恢复）。
- 验证：270 passed / 46 subtests；演示模式五页 200；Playwright 实页验证保存后仍停留在「机械臂」标签。

## 采集页 URDF 视图可交互（2026-11-01，`9d27910`）

- 现象：点击采集页机械臂模型视图变成"已暂停"。
- 原因：两套行为冲突——`arm_canvas(interactive=False)` 关掉了 OrbitControls 并把 canvas 设为 `pointer-events:none`；同时 `.dg-armsec` 上有 click 监听，切换 `dg-paused` 覆盖层并通过 `window.__dgArmPaused` 停掉关节刷新。
- 修复：采集页 arm pane 改为 interactive（与回放一致）；删除暂停覆盖层/CSS/点击监听/`__dgArmPaused` 全部读写；渲染循环改为按需（关节更新或 OrbitControls 的 change 事件才 render），空闲时不再每帧渲染。缓存版本号升到 `?v=13`。
- 验证：271 passed / 46 subtests；演示模式五页 200；Playwright 实页验证拖拽旋转、滚轮缩放生效且无 dg-paused。工控机已拉取 9d27910（`franka.yaml` 的复位姿态保留）。

## 配置副本一致性与头显面板回显（2026-11-01，`4a43186` / `5170086` / `e199a84`）

- 现象 A：保存复位姿态后遥操能启动，但左上角机械臂一直显示「已断开」，随后重启又报「Franka worker 配置不同」。
- 根因 A：同一份 `config/robots/<type>.yaml` 在运行时有四份副本（磁盘、worker、web `capture_config['_robot_profile']`、`CaptureService.arms`）。`FrankaArmManager` 自己 `deepcopy` 了 profile 并自持 IPC `Client`，公共层没有任何"配置已变"的通知入口，于是采集侧每 1/30 秒轮询都被指纹校验拒绝，`link_ok/data_ok` 恒为 False。
- 修复 A（`4a43186`）：`FrankaArmManager.update_profile()` 同步管理器与 client 的副本；`TeleopManager.refresh_profile()`/`save_robot_fields()` 通过 `_adopt_profile_in_devices()` 推给采集侧；`start()` 遇到"配置不同"重读 worker 写下的 YAML 并重试一次；`Client.request()` 在指纹不一致时放行 `status`/`stop`（否则操作员连断开都做不到）。
- 修复 B（`5170086`，公共层）：`robot/core/telemetry.py` 增加文档化的 `TelemetryBuffer.update_profile()` 空实现（缓存 profile 的机型必须覆盖）；动作后的刷新改为按机型 `FieldSet.actions` 声明触发，不再硬编码 `set-reset-pose`；`docs/robot-adapter-integration-guide.md` 新增 3.3.1「配置副本与指纹」四条规则。
- 现象 C：一键启动 → 健康检查通过 → 点黄色「确定」后自动弹出「启动头显」并报错「请先结束 VR 测试／遥操执行并停止录制，再修改头显配置」。
- 根因 C：`app/ui/ui_xr_link.py` 每 3 秒 `render()` 把链路状态镜像到 switch，`set_value()` 会执行与操作员相同的 `on_value_change`；`state['syncing']` 抑制无效，因为 NiceGUI 把 async 处理器排成后台任务，函数体在 `render()` 返回、标志已复位之后才运行。启动流程把 XR 服务与位姿发送拉起后，下一次轮询镜像 `ready=True` 被当成新的操作意图 → `flows.headset_startup()` → 守卫报错。三个位姿开关同样每次回显都发一次 `set` 写。
- 修复 C（`e199a84`）：处理器改为与面板正在显示的链路真值比较（`state['ready']` / `state['poses']`）——操作员的改动一定与显示值不同，程序镜像的回显一定相同，据此丢弃回显；删掉无效的 `syncing` 标志。回归测试用复现 NiceGUI 延迟处理器语义的假 UI：旧的实现下两条断言失败，新的实现下通过。
- 遗留验证：工控机（`192.168.10.38`）从开发机无法访问其 8088（curl 连接超时），实页点击验证只能在工控机浏览器上由操作员完成；同机已同步到 `e199a84`，定向测试 46 passed / 12 subtests，五页 200，无 traceback，复位姿态 `right.reset_ee_pose[0]=0.5469371676445007` 保留。
- 通用教训：NiceGUI 的 `on_value_change` 无法区分操作员操作与程序写值，异步处理器也不能用布尔标志抑制；需要"显示镜像"与"操作意图"分离，或按显示真值比较。

## 相机业务层与型号驱动分层（2026-11-01，`51b559e`）

- 现象根因：相机业务层认识型号——`MultiCameraManager` 用 `{"orbbec": ...}` 字典选驱动、只对 orbbec 传曝光/增益、用 `if backend != "orbbec"` 拒绝曝光、用 `getattr(stream,"exposure_range",...)` 猜能力。三个对外承诺因此是假的：UVC 工位的曝光滑块必然失败（`video.exposure/gain` 对 UVC 完全不生效）、`orbbec_hw_sync` 在配置和设置页显示为开而代码里硬编码关闭、UVC 把主机墙钟写进 `device_ts_ms` 导致设备级同步探针"通过"。
- 新结构（与 `robot/` 对称）：`camera/core/{driver,registry,ring,stream,image}.py` 提供契约与注册表；`camera/{orbbec,realsense,uvc}/driver.py` 各实现一种相机并自注册；`app/capture/cameras.py` 只剩三路编排、缓冲、能力门控与错误上报。
- 硬规则（有测试守着）：业务层不得出现型号字面量、不得 `if backend ==`、不得 `getattr` 猜能力；能力用对象存在与否表达（`capabilities.exposure is None` 即不支持）；`capabilities.clock` 必填，host-clock 相机不允许设备级同步；缓冲 age/span 只能来自 `FrameRing`。
- 行为变化：未绑定/构造失败的角色改为 `UnavailableDriver`（不再是"假 UVC 流 + 空 start"）；删除了不生效的 `video.orbbec_hw_sync` 配置键与设置页「硬件同步/自动曝光」两行；UVC 工位设置页不再出现曝光控件；设备级同步开关在无设备时钟时禁用；曝光控件只在相机已启动且拿到设备范围时出现（旧实现是显示后报错）。
- 枚举归位：`enumerate_uvc` 移到 `camera/uvc/devices.py`，`app/capture/devices.py` 只保留扫描/绑定业务流程；`app/capture/uvc.py` 删除。
- 文档：新增 `docs/camera-driver-integration-guide.md`（契约、能力语义、新增相机清单、能力矩阵、取舍）；README 与 docs/README 更新。
- 验证：本机 290 passed / 46 subtests，演示五页 200 无 traceback；工控机拉取后定向 25 passed，`/api/devices/cameras/start` → online=3/3、三路预览有效 JPEG、`/settings` 中曝光与硬件同步假值消失、设备级同步 toggle 为 disable。
- 已知限制：Orbbec/RealSense 无真机验证（只有构造级测试）；UVC 仍无在线曝光/增益；硬件同步能力已声明但策略未启用；掉线不自动重连；工控机站点 config 仍保留无害的 `orbbec_hw_sync: true`。

## 机型接入指南对齐（2026-11-01，`52b79f3`）

- `docs/robot-adapter-integration-guide.md` 原基线 `26d3055`，本次逐条核对到 `51b559e`：修正了已不存在的 `create_controller/create_kinematics/motion_for/recovery_for`、`validate()` 抽象方法、`sides/warnings/controllers` 形态、profile 携带相机键、supervisor 预检"CANN/host"描述、存储层 Franka 硬编码、`robot.core.check` 依赖检查、以及不存在的测试文件名。
- 补充新事实：worker op 白名单、`FieldSet.actions` → `_declared_action_keys()` → `refresh_profile()` → `TelemetryBuffer.update_profile()` 的完整链路、`camera/` 相机驱动分层、profile 真实键列表、`allowed_arm_modes/fingerprint/config_fields_for/sides_for/robot_context`、demo manager 回退。
- 顺带代码对齐（不改行为）：删除 `robot/core/registry.py` 里两个永远抛 `RobotNotRegistered` 的死占位入口 `create_controller`/`create_kinematics`；`tools/scripts/test_all.sh` 的 compileall 增加 `camera`，让新包进入文档所述的检查口径。
- 验证：指南中 45 个代码路径全部存在；290 passed / 46 subtests。

## 相机能力对齐阶段 1：契约 + UVC（2026-11-01，`7138501` / `f774288`）

- 契约新增 `GainControl` / `WhiteBalanceControl`（与 `ExposureControl` 同构）：能力对象存在即支持，数值范围由设备实时提供；`Capabilities` 现为 clock + exposure + gain + white_balance + hardware_sync + reconnect。
- UVC 驱动直连 V4L2 ioctl（`camera/uvc/controls.py`，不依赖工控机未安装的 `v4l2-ctl`）：VIDIOC_QUERYCTRL/G_CTRL/S_CTRL；DISABLED/GRABBED 视为不存在，READ_ONLY 不提供写入，**INACTIVE 保留范围**（自动白平衡开启时色温控件就是 INACTIVE，这是实测踩到的坑）。启动时应用 `video.gain`。
- 业务层 `MultiCameraManager` 提供 supports_gain/gain_range/get_gain/set_gain 与白平衡等价方法（三路都声明才启用，范围取交集）；`CaptureService` 加 guard、录制中拒绝修改、写回 `video.gain` 等；设置页按能力渲染增益滑块与白平衡（自动开关 + 色温滑块）。
- 工控机实测：三路 gain range=(0,8) 当前 4，写入 8 读回 8 并恢复；白平衡 range=(2800,6500)，手动 4000K 与自动可切换；`/settings` 出现增益/白平衡、不出现曝光；相机 3/3 启动正常。该硬件（ZED-M/2i 的 UVC 固件）确实没有曝光控件。
- ZED SDK 获取受阻：官方安装包与 pyzed wheel 均 403（账号门禁）；工控机 sudo/磁盘/Docker 均可用，待用户决定获取方式。已确认 ZED-M 与 ZED 2i 都在最新 SDK 支持列表，RTX 5090 需 CUDA 12.8+。

## 相机厂商资源与离线部署（2026-11-01，`509bcd7`）

- 新增 `camera/<type>/vendor/manifest.json`（orbbec / realsense / uvc / zed）：声明 Python SDK（发行包名、import 名、缓存 wheel 通配）、原生安装包（通配、校验路径、静默安装命令）、`system_files`（仓库路径 → `/etc` 目标）与 `reload`（udev / sysctl），并记录 `provenance`（来自哪个 wheel/安装包的哪个版本）。
- 规则入库并逐字复制：`99-obsensor-libusb.rules`（pyorbbecsdk2 2.1.2 wheel）、`99-realsense-libusb.rules`（librealsense，PyPI wheel 不带）、`99-slabs.rules` + `60-zed-buffers.conf`（ZED SDK 5.5.1 安装包）。工控机此前**一条相机 udev 规则都没装**（非 root 访问一直靠假设的 0666）。
- `tools/deploy/camera_deps.py`：状态报告（缺项退出 1）、`--print-commands` 打印 `sudo install -D`/`udevadm`/`sysctl` 命令而不自行提权（沿用 install.sh 全程不用 sudo 的约定）、`--install-python` 优先 `--no-index` 用 `tools/deploy/downloads` 缓存 wheel，缺才回落 PyPI。判断"已就位"用**逐字节比较**，规则漂移或手改会重新报出。`tools/deploy/downloads/` 已 gitignore，原生 SDK 与 wheel 不进仓库。
- `install.sh` 在 pip check 之后接入 `--install-python` 与 `--print-commands`；顺手修掉 `e720c39` 遗留的多余 `fi`——`tools/deploy/install.sh` 此前是整体语法错误（`bash -n` 报 line 70），安装脚本跑到该行即中断，这是本轮实测发现的历史缺陷。
- 文档：`docs/camera-driver-integration-guide.md` 新增第 7 节「厂商资源与离线部署」，能力矩阵补 gain/white_balance 列与 ZED 行（待验证），第 5 节新增相机清单加入 manifest 步骤，删掉已失效的"UVC 曝光/增益只能靠相机工具"条目。
- 验证：本机 320 passed / 46 subtests；`tools/deploy` 与 `tools/scripts` 下所有 shell 脚本 `bash -n` 通过；`camera_deps.py` 在开发机如实报出四项缺失。
- 遗留：ZED SDK 安装中（安装器自装 `cuda-toolkit-12`，实际拉 12.9）；pyzed 官方 wheel 仍 403，计划用公开 `zed-python-api v5.4.0` 源码对 5.5 SDK 编译。

## 依赖安装路径收敛：requirements.txt 单一源 + uv 优先（2026-11-01，`19d3d8f`）

- 事实：`pyproject.toml` + `uv.lock` 是 `41cb8f7`（10-30）加的"镜像清单"，之后 `4becc73`（11-01）改了 `requirements.txt`/`pyproject.toml`（删掉 piper-sdk、python-can、placo、mujoco、pin、meshcat、tyro），`uv.lock` 没跟着改 → `uv lock --check` 至今报需要更新，按锁装会装回 7 个已删包。仓库内没有任何脚本/文档引用 uv，`install.sh` 一直走 `python -m pip`。
- 同时发现：工控机 `runtime/.venv-ui/pyvenv.cfg` 有 `uv = 0.13.5` → 环境是 `uv venv` 建的，**自带 venv 里没有 pip 模块**，`install.sh` 的 `-m pip install --upgrade pip` 在它上面必然失败。即"实际安装路径"早已悄悄换成 uv，但文档写的还是 install.sh。
- 决策（用户选定）：`requirements.txt` 是唯一依赖源；`install.sh` 有 uv 时用 uv（`uv venv --python`、`uv pip install --python <venv> -r <(dependencies.py)`、`uv pip check`、`uv pip freeze`），没有 uv 时回落原 pip 路径；**删除** `uv.lock` 与 `pyproject.toml`（镜像清单必然漂移，已有一次实证）。README 与机型适配指南第 5.6 节同步改为"只加 requirements.txt，不要再引入镜像清单"。
- 验证：本机 323 passed / 46 subtests，其中新增 `tools/tests/test_install_script.py` 在临时根目录里用打桩的 `python`/`uv` 跑真实脚本，断言 uv 参数与 pip 回落两条路径；工控机上用 `uv venv` 建的无 pip 临时环境实测 `uv pip install -r <(…)`、`uv pip check`、`uv pip freeze` 三条命令均可用。

## ZED SDK 安装（工控机，2026-11-01）

- 安装包 `ZED_SDK_Ubuntu24_cuda12.8_tensorrt10.9_v5.5.1.zstd.run`（sha256 `0c282d59…`）`--noexec` 解包到 `/tmp/zed-installer`。
- **坑 1：完整 `cuda-toolkit-12` 不需要，且会卡死。** 首次静默安装让安装器自装 CUDA，`apt-get install cuda-toolkit-12` 在 `libcublas`（459MB）上挂死 18 分钟：日志停在 17:07 不动、apt 的 `write_bytes` 3 秒 0 KiB、socket 一个都没有（非 tty 下 apt 不打印进度，日志停住不能当成"还在下"）。
- **坑 2：`libsl_zed.so` 只要 CUDA 运行时。** `ldd` 只有 `libcuda.so.1`；`libcudart.so.12`、`libnvinfer.so.10` 是运行时 dlopen，`DEPTH_MODE.NONE` 不用 TensorRT。只装 `cuda-cudart-12-9`（170KB）即可。
- **坑 3：`/usr/local/zed` 是 `root:zed 0770`。** 普通用户 `ls` 报"权限不够"会被误读成"没装上"（我第一次就误判了）；要 `sudo usermod -aG zed embody`，并用 `ldconfig -p | grep sl_zed` 或 `sudo ls` 核实。
- 最终可用流程：`sudo apt-get install -y --no-install-recommends cuda-cudart-12-9` → `sudo ./linux_install_release.sh --silent --skip_tools --skip_od_module --skip_python --skip_cuda`（10 秒装完；`--skip_cuda` 在第 1172 行真的跳过版本检查）→ 得到 `/usr/local/zed` 198MB、`libsl_zed.so` 163MB、`/etc/udev/rules.d/99-slabs.rules`、`/etc/ld.so.conf.d/001-zed.conf`。
- pyzed：官方 wheel 与 `/py/`、`/zedsdk/…/whl/` 全部 403；PyPI 的 `pyzed` 是无关同名包（1.3.0，依赖 durationpy）；Docker 只有 Jetson 的 py 镜像。改用公开源码 `zed-python-api v5.4.0` 对已装 5.5 SDK 编译（`setup.py` 从已装头文件读版本号，产出 5.5；5.5 新增 API 缺失但探测脚本 getattr 容错）。
- 清理：`/var/cache/apt/archives` 留着 733MB 之前下一半的 CUDA deb（纯缓存，可删）。安装器解包目录 `/tmp/zed-installer`（2.6GB）也在，装完可删。

## ZED 驱动真机验证（2026-11-01，`2511336` / `909db74`）

- `camera/zed/driver.py` 落地：左眼取图、帧环、能力对象（曝光/增益/白平衡），`clock="host"`。**刻意不进 `_DETECT_ORDER`**：ZED 相机同时会以 UVC 出现，auto 探测会把工位从已验证的 UVC 路径悄悄换走，所以只认显式 `backend: zed`。
- 实测结论（2×ZED-M + 1×ZED 2i，SDK 5.5.1，pyzed 由公开 5.4 源码编译）：
  - 三路同时开流 HD720@30，各 60/60 帧、30.9 fps；单帧左眼 720×1280 BGRA；
  - `EXPOSURE`/`GAIN` 接受 0–100（101 被拒），`WHITEBALANCE_TEMPERATURE` 2800–6500，`WHITEBALANCE_AUTO` 0/1；
  - `EXPOSURE_TIME`/`ANALOG_GAIN`/`DIGITAL_GAIN` 在 USB 机型返回 INVALID FUNCTION PARAMETERS（GMSL 专用）；
  - `get_camera_settings` 返回 `(ERROR_CODE, value)`，`set_camera_settings` 只返回 ERROR_CODE（这个不对称踩过两次）；
  - `AEC_AGC` 是曝光+增益的自动档：写手动值前必须先关，否则自动模式会盖回去；写手动色温会关 `WHITEBALANCE_AUTO`；
  - `TIME_REFERENCE.IMAGE` 是**主机 epoch 纳秒**（与 `time.time_ns()` 差 0.04 s，量级 1.79e18 而非开机计数）→ USB ZED 没有设备时钟，SDK 只提供更精确的到达时刻。
- 业务层实测（`MultiCameraManager` + `backend: zed`）：三路 ZedDriver、clock 集合 `{'host'}`、`device_clock_available=False`、三控件均支持；范围 (0,100)/(0,100)/(2800,6500)；曝光 67→20→67、增益 50→90→50、白平衡 3200 手动与自动切换均成功，写控件期间三路继续出帧。
- 绑定缺范围查询 → 驱动用文档值加边界实测的常量，并在有 `get_camera_settings_range` 时优先用 SDK 返回值（已在指南第 6 节说明这个例外）。
- 站台侧：`/etc/udev/rules.d/99-slabs.rules` 由 SDK 安装器写入；Orbbec/RealSense 的规则仍未安装（本机没有这两家的相机）。
- 待决：工位 `config/config.yaml` 仍 `backend: uvc`，是否切换由用户决定（切换需把三路绑定从 V4L2 设备路径改成 ZED 序列号）。

## HDF5 落盘业务基线 v1.2–v1.3（2026-11-01）

- `.vibe/requirements/hdf5-recording-format.md` active v1.3：实际相机同步帧组驱动主时间轴；支持真实同步 60fps，禁止复制/插值/伪造时间戳扩帧。
- 普通松 Grip 后，只要 adapter 仍实际保持上一已发送目标，该 action 持续有效并可跨帧重复记录；这不是 recorder 复制伪造。真正 hold、暂停、失去控制权后的间歇缺失仍暂缓。
- action 扩为两个可选字段：`action/<side>/eef_pose (T,7)` 与 `action/<side>/joint_position (T,J)`，各构型按需只提供其一或并存；两者都未提供时 `has_action=false`、不建 `/action`。未创建的数据集即表示不支持，不额外写声明 attrs。
- `robot_id` 改为由机器人描述提供（具体机器编号），不再固定为 `Franka Research 3`；`robot_model` 才是型号。
- manifest 按用户同步的元文档删减：`episodes[].success`、`episodes[].discarded`、批次级 `n_discarded` 不写，episode 结果只由 HDF5 root attrs 表达；`<cam>_dup` 及复制上一帧供插值的用途整体废弃（基线 v1.4）。
- `spec_version` 裁定为 `inhouse-hdf5-v2`（manifest 与 episode 统一）；`collect_mode` 固定 `teleop`；`project` 只写 manifest（基线 v1.5）。采集端自检与「拒收」逻辑暂不考虑。
- 相机内外参本阶段不采集、不写入；图像只写 mount/serial/decoded_shape，未标定不影响录制（基线 v1.6）。
- 采集中间层定为抽象基类 + 封闭字段白名单（action 白名单为 eef_pose / joint_position，另有伴随字段 gripper），适配器只能继承声明子集，越界启动期失败（platform boundary v1.5）。
- 观测字段白名单已在 R7 明示：joint_position / joint_velocity(可选) / joint_effort(可选) / gripper / eef_pose；观测 eef_pose 与 action 对齐为 (T,7)+xyzw（基线 v1.7）。
- 任务元数据已确认：采集页“新建任务”弹窗必须填写 `task_id`、`task`、`scene`，另有任务名称供人查看；保存为 YAML，历史任务可查看但只读不可修改，只支持删除；采集时从所选 YAML 写入 episode attrs，任务名称不写 HDF5，删除不改历史数据（基线 v1.9）。
- 机器人配置新增模板约束：模板列明新增构型必填字段；`robot_type`/`robot_model` 只读，`robot_id` 可修改；左右臂 `frame_axes` 来自机器人 YAML，设置页只读并写入对应 EEF pose attrs（platform boundary v1.6）。
- 2026-11-02 数据采集业务澄清已收口：最终唯一实施基线为 `.vibe/requirements/hdf5-recording-final-baseline.md` v1.0；旧 `hdf5-recording-format` v1.9 标记 superseded。用户要求暂不修改代码，已拆分 architecture、middleware contract、robot config、task lifecycle、HDF5 export 五个后续任务。

## project 归属字段（2026-11-02，`383af2d`）

- 现象：manifest 的 `project` 一直是空字符串。元文档 §2.1 示例为 `forge_v1`，且 `obs://.../<project>/<robot_id>/...` 是路径层级，缺了就无法按项目归类；代码里 `write_manifest(project='')` 的默认值从未被赋值。
- 决定：`project` 按任务填写，与 `task_id`/`task`/`scene` 同级，放在 `_task_configs/<task_id>.yaml`。理由：batch 只允许一套任务元数据，project 是项目归属而不是每集属性。
- 落点：新建任务弹窗新增「项目」输入；`TaskConfig.project` 并进 `as_snapshot()`/`as_record()`；`CaptureService.create_task_config` 透传；`hdf5_v2._update_manifest` 从 `task_meta` 取 `project` 写入 manifest。
- **不写进 HDF5 root attrs**：元文档未在该处定义 project，基线也明确「project 只写 manifest」。导出器已断言 `'project' not in h5.attrs`。
- 校验：`project` 必须匹配 `^[a-z0-9][a-z0-9_]{0,63}$`（因为它会成为 obs 路径的一段）；新建任务必填。旧任务 YAML 无该字段仍可加载、可选、可录制，manifest 保持空字符串而不猜测。
- 验证：本地 **470 passed / 46 subtests**；工控机部署 `383af2d`，受影响的 52 项（task_config/task_delete/manifest_integration/hdf5_v2/batch_manifest）全通过；工控机实机核查 task YAML、snapshot、root attrs 不含 project、manifest 写入 `forge_v1`、旧 YAML 兼容。
- 工控机有 3 个与本次无关的失败（`test_capture_arm_manager_builds_for_the_registered_robot`、`test_shutdown` 两项）。已在改动前提交 `0b19d2c` 上复现同样失败，根因是工控机上另有前台实例占用 Franka IPC（`请先结束运控会话`）与 8088 端口，属环境冲突，不是回归。**用户停止应用后重跑，工控机 470 passed / 46 subtests，与本地一致，确认是环境占用**。
- 用户明确：现有已创建任务与已录数据均为测试内容，不迁移、不回填 project。
- 清理（2026-11-02）：用户确认本地测试数据从未上传（NAS `/mnt/nas/forge/piper2/raw` 有 77 个他人任务目录、11996 个文件，但无 `test_1`/`TEST`/`20261102`），授权清理。已删除 `runtime/recordings/test_1`（12 个 hdf5）、`runtime/recordings/TEST`（4 个 hdf5）、`_task_configs/*.yaml`、`_batches.json`、`runtime/logs/index.db*`。存储 720M→8K，hdf5 归零，只留下空的 `_task_configs/`。验证：任务列表/配置/批次/会话数全为空；PTR_PORT=8199 临时起应用，`/`、`/record`、`/playback`、`/settings` 均 200、无 traceback，进程已退出、端口释放。
- 站点配置未动：`config.yaml` 与 `robots/franka.yaml` 保持 staff 现场值（UVC 三路、brightness 2/contrast 4/5000K、tcp=fingertip_center/0.16、reset 姿态）。

## HDF5 元数据收尾（2026-11-02，`b68da6d`）

- 用户批准方案 A 五项差异全部修复；未特别指定的数据均为测试数据，不重导、不迁移。
- 新 episode 名六位补零。root sensors 统一标准相机名，写 model/serial/width/height/mount；图像 dataset 保留 decoded_shape，serial/mount 与 root 一致。双臂 base_extrinsics 从机型快照读取，缺标定写 unknown；单臂省略。
- `camera/core/identity.py` 在 MultiCameraManager.start 开任何流之前查询，缓存归本次相机启动所有，重启刷新；capture_service 按物理→显示映射交给 recorder。pyzed 可选，不改变 UVC 后端、不新增依赖；SDK 缺失或返回 serial=0 写 unknown，不能拿 /dev 路径冒充。
- 真机 ZED 真实序列号：left ZED-M=12989796、center ZED 2i=39897211、right ZED-M=13482374。USB 视频接口的空值/OV0001 不是真实相机序列号；SDK DeviceProperties.path 可可靠匹配 /dev/videoN。UVC 占用后 SDK 可能返回 0，因此必须开流前查。
- **TCP 最终方案（用户决定，修订早先做法）**：记录**不做坐标换算**，落盘就是机器人自身 `O_T_EE`。真机右臂只读实测 `F_T_EE` 平移 0.16 m、单位旋转，说明 `O_T_EE` 是法兰前 0.16 m 的末端点，不是法兰。故配置声明 `tcp=fingertip_center`、`tcp_offset=[0,0,0.16]`，与数据一致，且不需要任何变换。
- 生产 controller 每帧用实时 `F_T_EE` 核对配置声明：声明 `flange` 而机器人有偏移、`tcp_offset` 与实时偏移差 >1 mm、`tcp` 未声明、或缺少实时变换，一律拒绝反馈（等于拒绝录制）。宁可录不了，也不写出与数据不符的声明。驱动仅为该校验携带实时 F_T_EE，不参与控制。
- 校验已抽到 `robot/core/tcp.py::declared_point_problem`，任何机型复用：**没有任何硬编码偏移**，读的是该机实时 flange→EE，所以 0 m / 0.06 / 0.1034 / 0.31 m 等任意几何，只要配置如实声明就通过；照抄别的机械臂数值会被拒。另外新增两条拒绝：末端相对法兰**有旋转**（规范只有 `tcp_offset` 位置，无法完整描述该点）、`tcp` 名不在规范定义内（`flange` / `fingertip_center`）。新增机型只需在 `config/robots/<type>.yaml` 的每臂 `kinematics` 写 `tcp` + `tcp_offset`，模板已说明未确认就写 `unknown`（录制会拒绝而不是猜）。
- 本地与工控机完整 pytest：换算版曾 463 passed；改为「声明实际末端点、不换算」后，本地与工控机均 **464 passed / 46 subtests**。
- 工控机真实复验（`0b515a9`，右臂只读、不下发动作）：45 帧临时导出通过；`tcp=fingertip_center`、`tcp_offset=[0,0,0.16]`；**文件里的 45 行位姿与机器人上报的 `O_T_EE` 逐行相等**（无任何换算）；四条拒绝/接受路径全部符合预期（声明 flange→拒、offset 差 60 mm→拒、正确→接受、tcp 未声明→拒）。
- `b68da6d`→`0b515a9` 已推送 origin/feat/franka 并部署。备份 `~/hdf5-metadata-backup-20261102-131438/`、`~/tcp-verify-backup-20261102-132706/`；站点 config 完整恢复，franka.yaml 只合并新元数据，操作员 reset right[0]=0.5422013998031616、left[0]=0.5631575584411621 保留。服务原 inactive，验证后仍不启动实控服务。
- 部署教训：不要用 `yaml.safe_dump` 重写站点 `franka.yaml`，它会丢掉文件头注释并让 `test_set_reset_pose_persists_yaml_and_memory` 失败；按文本精确插入。另外旧版残留的 `tcp: flange` 同名 key 会覆盖新值（YAML 取最后一个），插入前要先清掉旧行。
- 本次仅关闭批准的五项格式差异，不代表原文档所有运行流程均实现：既有暂缓的采集自检、_SUCCESS 封口、language/音频与缺失帧正式策略仍按已批准基线处理。此前“6/6 通过”仅覆盖当时校验器项目，不代表整份元文档完整合规。

## HDF5 格式审计：6 条真机轨迹（2026-11-02，`1be0398`）

审计对象：`test_1` 下连续 6 条（episode 4–9，日期 12:10–12:36），逐条比对基线 v1.0 + 元文档《自采数据 HDF5 落盘规范》。

**完全合规的部分**：root attrs 20 项齐全且非空；`spec_version=inhouse-hdf5-v2`、`collect_mode=teleop`、`timezone=Asia/Shanghai`；时间轴严格递增、实测 29.99–30.01 fps（与标称 30 一致）；observation 五字段齐全且行数=T（`joint_position/joint_velocity/joint_effort (T,7)`、`gripper (T,1)`、`eef_pose (T,7)`）；eef_pose 的 8 项 attrs 齐全（`quat_order=xyzw`、`frame_axes`、`source=adapter_feedback/command`）；action 白名单干净（仅 `eef_pose` + `gripper`）；三路视频行数=T、`mount/serial/decoded_shape` 齐全、首帧是合法 JPEG；manifest 在 `batch_20261102_01/manifest.json` 且登记全 8 条、无 `success/discarded/n_discarded`、episode 行含 `file/episode_id/num_frames/bytes/md5`；无 `cam_dup`；无全 0 占位列。
- 顺带确认：**1 秒 bug 彻底消失**——413/284/289/294/291/266 帧，`has_action=true`，action 覆盖全程。

**发现并修复的两项不符**：

1. **相机 dataset 命名不符元文档**：写的是旧 schema 的 `cam_high` / `cam_left_wrist` / `cam_right_wrist`，而基线 §2 明确「字段名、键树、形状、单位和 attrs 以元文档为准」，元文档固定为 `cam_head` / `cam_wrist_left` / `cam_wrist_right`。带 `inhouse-hdf5-v2` 标记的文件用了旧词汇，会让下游按元文档读取时找不到相机。修 `app/storage/h5_export.py::CAM_MAP`，同步 `app/teleop/recording.py`（该处是死代码）与 config 注释。
2. **root `arms` 与文件内实际侧名矛盾**：attr 写操作员选的 `right`，但所有数据集都写在 `main` 下。改为由导出实际写出的侧名推导（单臂 `main`、双臂 `left,right`），这也是基线「单臂写 main」的本意。

**查证后否定的一项**：某条 take 的 `action/main/gripper` 有 127/266 帧为 `0.0`，初看像禁用零占位。但原始帧序列是连续夹爪轨迹（`0.085 → 0.0173 → 0.0 → … → 0.0077 → 0.0757 → 0.085`），同期实测值同步从 0.033 变到 0.084，说明这些 0 是真实的「完全闭合」指令，不是填充。判定规则改为「整列全 0 才算占位」；同时给 controller 加防御性兜底（读回值为 None 时回落到已校验的下发宽度，而不是写 0）。

**验证**：本地 455 passed / 46 subtests。工控机用修复后的代码从原始会话重新导出同一批 6 条 → **6/6 通过**，`arms=main`、相机名 `cam_head/cam_wrist_left/cam_wrist_right`、action 行数正确。
- 修复是**向前生效**：已录 episode 保留原有命名，重新导出原始会话才会得到修正后的文件。

## 相机曝光：brightness/contrast 才是有效档位（2026-11-02，`2982642`）

- 用户反馈 HD720 + 固定色温后颜色正常了，但画面仍然过亮，问 UVC 后端为什么不能调曝光、参考版是怎么处理的。
- **逐项枚举三路全部 V4L2 控件**（user / camera / codec 三个 class）的结论：
  - **完全没有曝光或自动曝光控件**——`auto_exposure` / `exposure` 配置对 UVC 完全无效，不是代码没接，是固件没有；
  - **`gain` 无效**：0~8 全量程画面统计完全一致（gray 206、clip 42.2%），此前 `gain: 8` 从来不影响画面；
  - **`gamma` 无效**：1 与 500 输出完全相同；
  - **`brightness` 是唯一真正影响曝光的档位**：0→gray144/0% 过曝，2→gray179/0%，4→gray206/42%，8→gray232/56%；
  - `contrast` 效果类似（2→0% 过曝，5→40.7%）。
- **参考版为什么"不过曝"：它其实也过曝。** 参考版从不写任何 V4L2 控件，用的是设备默认 `brightness=4`，同机同刻实测它的俯视图也是 42% 像素过曝（我之前那轮对比里 center 的 clip 就是 37~42%）。所以这不是两套实现的差异。
- 改动：
  - `camera/core/driver.py`：新增 `BrightnessSpec`/`BrightnessControl`、`ContrastSpec`/`ContrastControl`，并加入 `Capabilities` 与 `CameraSettings`（`brightness`、`contrast`，`None` 表示不动设备）。
  - `camera/uvc/controls.py`：新增 `V4L2_CID_BRIGHTNESS`、`V4L2_CID_CONTRAST`。
  - `camera/uvc/driver.py`：两个能力代理；`_apply_settings` 顺序改为 **亮度/对比度 → 白平衡 → gain**（前两者决定曝光，后者只决定颜色）。
  - `app/capture/cameras.py`：抽出 `_read_all`/`_write_all` 复用多路读写，新增 supports/range/get/set。
  - `app/capture/capture_service.py`：`set_brightness`/`set_contrast`（录制中拒绝），写回 `video.*`。
  - `app/ui/ui_settings.py`：设置页新增「亮度」「对比度」滑杆。
  - `config/config.yaml`：`brightness: 2`、`contrast: 4`。
- 验证：本地与工控机 **450 passed / 46 subtests**；工控机用真实 `config.yaml` 起 `MultiCameraManager`：三路 1280×720 @30.3fps，**clip245 全部 0.0%**（此前 center 42.2%、right 11.0%），设备状态 `bright=2 contrast=4 awb=0 temp=5000` 与配置一致。
- 遗留（机位问题，非软件）：`left` 腕部相机现在对着天花板/远处，画面大面积高亮天棚、主体反而缺失；`right` 视野几乎全是台面。这两路需要现场调整朝向——固件没有曝光控件，无法靠软件补光。

## 播放页 500：内部目录被当成任务（2026-11-02，`683ef2e`）

- 现象：打开播放页（`/`、`/playback`）直接 500，日志 `ValueError: Task name: start with letter/digit; use A–Z, a–z, 0–9, ._- (max 64 chars)`，整页不可用。
- 根因：`_task_configs`（任务 YAML 所在目录）与任务文件夹同级。`index_db._rebuild_sessions` 在启动对账时把存储根下**每个**子目录都登记成任务，于是 `_task_configs` 进了 `tasks` 表；`sanitize_task_name` 拒绝下划线开头，而播放页会对当前任务名做校验 → 首次渲染就抛错。工控机索引里实际是 `['_task_configs', 'TEST', 'test_1']`。
- 修复（四处，避免只堵一种情形）：
  - `index_db.RESERVED_DIRS = {'_task_configs'}`，`_rebuild_sessions` 跳过；
  - 新增 `_is_task_dir`，同时跳过**名字不合法**的目录（用户手建文件夹不能搞崩页面）；
  - `list_task_names` 也过滤保留名 → 旧版本已写坏的索引自愈，不需要迁移数据库；
  - `count_sessions` 对非法任务名返回 0 而不抛错（`sanitize_folder_name` 提供不抛异常的判定）。
- 验证：本地与工控机均 **445 passed / 46 subtests**；新增 `test_reserved_storage_dirs.py`（含工控机同构目录、旧索引已污染、非法目录名参数化）；工控机实起应用，`/`、`/record`、`/playback`、`/settings` 全部 200，日志中 `Task name` 报错 0 次、500 响应 0 次；`list_tasks` 返回 `['TEST', 'test_1']`（`TEST` 10 条、`test_1` 2 条），`count_sessions('_task_configs')` 返回 0。
- 注意：用 curl 直接请求页面会在日志里留下 `The parent slot of the element has been deleted` 与 `JavaScript did not respond within 1.0 s` 之类噪声，那是无浏览器客户端的副产物，不是故障。

## 相机画质修复：HD720 + 固定白平衡（2026-11-02，`c1bbf79`）

- 用户报「画面偏黄、曝光不正常，而且很模糊」，要求参考 `~/Project/robot_capture_franka/robot_capture_franka` 那套 UVC。
- 关键结论：**两套的 UVC 驱动逻辑逐行等价**（同样 1344×376/2560×720 选档、左眼裁切、letterbox、JPEG 95）。同机同刻对比，两套在 640×480 和 1280×720 下的 RGB 均值完全相同、清晰度差 <0.1%。所以问题不在驱动实现，而在**配置**。
- **模糊 + 黑边根因**：`video.width/height = 640×480` 会落入 ZED 的 VGA 双目档 1344×376，左眼只有 672×376，再缩放到 640×360 塞进 640×480 画布 → 垂直只剩 360 行 + 上下黑边。参考版 `config/workbench.yaml` 明确写了 `# Preserve the native HD720 left eye instead of downsampling to VGA.` 并用 1280×720。HD720 = 2560×720 双目 = 左眼正好 1280×720，**零缩放零黑边**。
  - 实测：统一到 640×480 比较 Laplacian 方差，center 由 534 → 1116（约 2.1 倍）；三路 HD720 并行各 30.2~30.3 fps，USB 带宽不是瓶颈（本机 usb-0:8.2/8.3/8.4 三个独立口）。
- **偏黄根因**：该固件的自动白平衡会停到区间端点——两次测量分别读到 6500K（R-B +89，偏黄）和 2800K 端（偏青）。手动固定色温后稳定：4200K 偏青、5000K 中性（R-B −8~−9）、5400K 偏黄；且手动值跨流重开保持。
- **`gain` 在这批 ZED 上是无效的**：0~8 全量程画面完全不变（逐档实测 gray/clip 一致）。所以此前 `gain: 8` 从来不是曝光问题的原因，也不必再调。
- `left` 相机在 HD720 下仍 96% 过曝：它正对强反光面，而该固件**完全没有曝光控件**（VIDIOC 全量枚举确认），属现场补光/机位问题，软件无法解决。
- 改动：
  - `camera/core/driver.py`：`CameraSettings` 新增 `auto_white_balance`、`white_balance_temperature`。
  - `camera/uvc/driver.py`：抽 `_stereo_mode(width, height)` 承载选档规则（可测）；`_apply_settings` 先应用白平衡再应用 gain（避免 AWB 覆盖），失败只告警不致命。
  - `app/capture/cameras.py`：把 `video.auto_white_balance`／`video.white_balance_temperature` 传入 CameraSettings。
  - `config/config.yaml`：`1280×720`、`auto_white_balance: false`、`white_balance_temperature: 5000`。
  - 测试：`test_uvc.py` 钉住选档（1280×720→2560×720、640×480→1344×376）并断言提交的 config 必须是 HD720 且色温在合法区间；`test_uvc_controls.py` 覆盖固定色温、`None` 不写设备、自动模式不写温度、白平衡失败不致命。
- 验证：本地与工控机均 **436 passed / 46 subtests**；工控机用真实 `config.yaml` 起 `MultiCameraManager`，三路 1280×720 @30.3fps、`errors: none`、设备状态 `awb=0 temp=5000 gain=8` 与配置一致。
- 部署按备份-写回流程：备份 `~/backup-config-20261102-115930.yaml`、`~/backup-franka-20261102-115930.yaml`；站点 `config.yaml` 原本没有白平衡两项，用一次性脚本精确插入（`width/height` 覆盖，两个白平衡键插在 `gain` 后），`franka.yaml` 直接写回。`load_config()` 复核：1280×720、awb=False、temp=5000、arms=right、backend=uvc、复位姿态 right 0.5422 / left 0.5632 完好。

## 数据采集 1 秒录制故障修复（2026-11-02，真机发现）

- 现象：工控机录制两条数据都只有约 1 秒（34 帧 / 0.77 s、34 帧 / 1.14 s），日志每帧刷 `ValueError: right: 未声明的记录字段 gripper`。
- 根因：基线 §2.1 明确有 `action/<side>/gripper (T,1)`，`recording_contract.py` 也定义了 `ACTION_SIDECAR_FIELDS={'gripper'}`，但该常量**全项目零引用**：`validate_declaration` 与 `RecordingTelemetry._clean` 只认 `ACTION_FIELDS`（仅 eef_pose/joint_position），而 `FrankaAdapter.recording_report()` 与 `FrankaSample.recording_view()` 都把 `gripper` 放进 action 字典。于是 `build()` 对**每一帧**抛错 → `standard=None` → 临时策略整帧丢弃 → 首次 action 之后一帧都写不进去。
- 失败是**静默**的：丢弃计数 `skipped_incomplete` 从不写进 `meta.json`，产出的 HDF5 有 34 帧且 `has_action=False`，看起来像一条干净的 state-only 数据。该 take 的真实同步帧数是 181，`sync_recorded=34`。
- 修复：
  - `recording_contract.py` 新增 `ACTION_NAME_SPACE = {**ACTION_FIELDS, **ACTION_SIDECAR_FIELDS}`，白名单仍是封闭集合，越界仍在启动期失败；`validate_declaration` 与 `_clean` 改用它。
  - `FrankaAdapter.RECORDED_ACTION_FIELDS` 改为 `('eef_pose', 'gripper')`（与基线一致），并让 action 的 gripper 优先取实际下发的 `gripper_sent`，而不是夹爪实测位置。
  - `capture_service._on_synced` 的记录判定抽成 `_standard_packet(arm) -> (packet, verdict)`，verdict 四态：`write` / `drop_frame` / `video_only` / `no_arm`。契约违规（代码 bug）现在保留视频与时间戳、不写标准遥测，**不再整帧丢弃**，避免"丢掉大部分帧后仍导出一个看起来正常的短文件"。
  - 可见性：`sync_skipped_incomplete`、`telemetry_errors` 写入 `meta.json`；有契约违规时写 `telemetry_warning`。
  - 导出侧新增 `hdf5_v2.require_standard_coverage`：`telemetry_errors > 0` 或帧数与时间轴不符时抛 `ExportError`，绝不让视频长于数据集的会话静默导出。
- 验证：本地完整 pytest **430 passed / 46 subtests**；新增 `test_recording_action_gate.py`（含 181 帧端到端重放）与 `test_take_metadata.py`；用故障 take 的真实 `franka_telemetry.npz` 重放，确认新代码 34 帧全部 `build` 成功、无契约错误。
- 提交 `71268ed` 已推送 `origin/feat/franka`，工控机按备份-写回流程更新（备份 `~/backup-config-20261102-114443.yaml`、`~/backup-franka-20261102-114443.yaml`），站点配置与操作员复位姿态（right 0.5422 / left 0.5632）完好。
- 工控机完整 pytest **430 passed / 46 subtests**。
- 工控机端到端真机验证（真实 UVC 三路 + 机械臂只读反馈 + 脚本化 action，**未下发任何机械臂指令**）：150 帧 / 8.0 s，`sync_synced=150`、`sync_recorded=150`、`sync_skipped_incomplete=0`、`telemetry_errors` 缺失（即 0），其中 143 帧带 action；导出 `inhouse-hdf5-v2` 成功，`arms=right`→`main`、`has_action=True`、`action/main/{eef_pose (143,7), gripper (143,1)}`、`num_frames=143`（裁掉首次 action 前 7 帧 state-only 前缀，符合临时策略）。这次 150 帧全部写入，证明截断已消除。

## 数据采集链路 v2 落地（2026-11-02，已提交 `186d6cc`）

- 五个任务全部完成：`recording-pipeline-architecture`（设计文档 `.vibe/docs/采集管线架构设计.md`）、`recording-contract-and-middleware`、`robot-config-template-and-settings`、`task-config-lifecycle`、`hdf5-schema-and-export-v2`。
- 新增公共契约：`robot/core/recording_contract.py`（action 白名单 eef_pose/joint_position + gripper 伴随字段，observation 白名单 5 项，形状/单位校验）与 `robot/core/recording_layer.py`（RecordingTelemetry 按声明接收、拒绝未声明字段）。`RobotAdapter` 新增抽象方法 `recording_fields()`；`FrankaAdapter` 声明 `eef_pose`+`gripper` action，并提供 `recording_report()`。
- 机器人配置：新增 `config/robots/_template.yaml` 必填字段模板；`load_profile` 强制 `robot_id` 与每臂 `frame_axes`；`franka.yaml` 补 `robot_id: franka_01` 与左右臂 `frame_axes`；设置页 type/model/frame_axes 只读、robot_id 可改。
- 任务配置：新增 `app/storage/task_config.py`，采集页新建任务弹窗改为 任务名称 + task_id + task(多行) + scene，保存为 `_task_configs/<task_id>.yaml`；无修改接口；删除只删配置，不删已录 episode。
- 录制：`recorder` 新增 `_standard_buffers`/`recording_frames.json`，按中间层声明记录标准字段；`meta.json` 增加 `task_meta`、`robot_identity`、`joint_names`、`sensor_info`、`batch_id`。
- 导出：新增 `app/storage/hdf5_v2.py`（`inhouse-hdf5-v2` 键树、root attrs、相机 attrs、eef_pose 四元数 attrs、单臂 `main`）；`h5_export.export_session_to_h5` 优先走 v2，旧 schema v3 仅服务历史会话。新增 `app/storage/batch.py`（批次编号 `YYYYMMDD_NN`、manifest，不写 success/discarded，不写 `_SUCCESS`）。
- 播放页适配：`sessions.load_arm_follower_series` 优先读 `recording_frames.json`（`playback_series`，joint_position+gripper），失败再回退旧 `franka_telemetry.npz`；旧的 v3 HDF5 会话仍可回放。
- 2026-11-02 临时安全策略（正式策略未定，见 `.vibe/docs/已知未决-action缺失与不完整帧.md`）：
  - 导出时裁掉首次 action 之前的 state-only 前缀（时间轴与解码图像一并裁），`/action` 每行都有真实值；
  - 首次 action 之后的空档、以及任意已声明观测字段缺帧，仍拒绝导出（`h5_status=failed`）并保留原始会话；
  - 录制侧 `recording.require_complete_frames` 默认 true，缺帧整帧丢弃并计入 `skipped_incomplete`；
  - 整条无 action 的 episode 正常导出为 state-only，`has_action=false`。
- 验证：完整 pytest 410 passed / 46 subtests；compileall 通过；PTR_DEMO 五页 200 无 traceback。**未提交、未推送、未做真机验证**。
- 提交 `186d6cc` 已推送 `origin/feat/franka`（31 文件，+2158/−36），并设置 upstream。
- 工控机 `192.168.10.38` 已更新到 `186d6cc`：先备份站点配置（`~/backup-config-20261102-104905.yaml`、`~/backup-franka-20261102-104905.yaml`）→ `git checkout` 两个 tracked 站点文件 → `git pull --ff-only` → 写回站点配置。`config.yaml` 保留 UVC 三路与 `arms: right`、去掉已废弃的 `orbbec_hw_sync`；`franka.yaml` 保留操作员复位姿态（right[0]=0.5422、left[0]=0.5632），并从新版本继承 `robot_id: franka_01` 与左右臂 `frame_axes`。
- 工控机 `load_config()` 通过：robot_id=franka_01、arms=right、左右 frame_axes 正常、复位姿态未丢。
- 工控机验证：完整 pytest **410 passed / 46 subtests**；演示模式五页 200、无 traceback。**真机录制与运动尚未验证**。
- 登录注意：AGENTS.md 记录的密码曾写错为 `E1mobdy.23`，实际为 `E1mbody.23`（已由用户更正）。
- 已知未实现（基线已声明暂缓）：采集端自检与拒收、`_SUCCESS` 封口判据、音频/language、action 在 hold/失控时的缺失策略、不完整帧策略、历史 HDF5 兼容；播放页对新 v2 键树的读取尚未验证。

- `.vibe/requirements/unified-platform-integration-boundary.md` 升 v1.4：新增采集中间层，采集进程不直接调用 `RobotAdapter`；适配器声明能力并按 HDF5 标准字段名上报，中间层归一化，采集层按声明落盘。中间层形态（进程/接口）留给技术设计。
- 当前代码的 `idle → tracking 保持 → last_action` 与松 Grip 规则一致；但仍是 schema v3、无声明机制，新结构未实施。本轮只改业务文档并梳理拓扑。
