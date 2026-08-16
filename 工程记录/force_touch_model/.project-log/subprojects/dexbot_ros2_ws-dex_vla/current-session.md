# Current Session

- 当前阶段：code-reading
- 当前目标：快速掌握 VLA 生产部署总流程，并明确新增训练模型的最小改动范围
- 当前任务：TUTOR-VLA-READ-001
- 已确认事实：
  - ROS Action 外部入口为 `/vla/execute`，客户端通过 `ExecuteVLA` 发送 Goal。
  - `PolicyRuntimeNode` 负责 ROS 接口、Goal 生命周期和 rollout 对象装配；`RolloutCoordinator` 承担闭环执行。
  - `load_runtime_bundle(model_id)` 不只是返回参数，还会装配并校验 model/template、observation/action/robot contract、safety、worker service、artifact、retargeter 和 deployment contract。
  - 新模型优先通过 `config/policy_models.yaml`、`config/policy_templates.yaml`、`config/io_contracts.yaml` 与模型目录内的 `dexbot_policy_artifact.json` 接入。
  - 若复用已有框架、观测/动作 contract、模板和 worker service，通常不需要修改 runtime/action/backend 源码；新增框架或协议时才进入 backend/adapter 代码。
  - 当前最适合用作端到端阅读样例的是 `pickplace_bottle_lerobot_ACT_0715_10hz`，因为它已经贯通模型注册、模板、服务和 artifact 配置。
- 阅读方法决策：停止逐函数深读，改用“场景主线 + 配置链 + 数据契约 + 扩展差异”的阅读方法。
- 阅读主线：
  - 启动：`launch/vla_task_bringup.launch.py`
  - ROS 入口：`ExecuteVLA.action`、`scripts/send_vla_goal.py`
  - 任务控制：`nodes/policy_runtime_node.py` 的 `__init__`、`_goal_callback`、`_execute_cb`、`_load_bundle`、`_execute_rollout`
  - 配置装配：`config/runtime_execution.yaml` → `config/policy_models.yaml` → `config/policy_templates.yaml` → `config/io_contracts.yaml` → `runtime/config_loader.py`
  - 推理数据流：`RosInputAdapter` → `WorkerClient/model service` → action adapter/retargeter → `SafetyGate` → `GenericRobotBackend/RobotCommandExecutor` → robot driver
- 新 GR00T 模型接入原则：
  - 新 checkpoint 或复用现有协议时，优先修改模型注册、模板、artifact 和必要的 contract 配置。
  - 输入/输出契约不同，检查 observation/action/robot contract、adapter、coordinate profile 和 retargeter。
  - 只有新增模型框架或服务协议时，才进入 worker/backend/protocol 源码。
  - 接入前必须先建立模型契约卡：输入图像、语言字段、proprio、关节顺序/单位、动作维度/语义、频率、chunk、夹爪编码、坐标系和归一化方式。
- 活跃决策：停止逐函数深读，改用“一条现有模型配置链 + 一页式运行流程 + 新模型接入决策树”；每次阅读只追踪一个真实运行场景，并产出流程图、配置解析图、数据流图或差异表。
- 阻塞项：无
- 最近验证：已完成 Action 客户端、PolicyRuntimeNode 准入/执行入口和 RuntimeBundle 装配入口的静态阅读；确认逐函数阅读与用户目标不匹配，并完成阅读路线调整。
- 下一步：先阅读启动文件和默认 ACT 模型配置，建立“启动了什么、默认模型是谁、推理从哪里进入、动作从哪里出去”的一页式总图；随后追踪 `policy_models.yaml` → 模板/服务 → artifact → contract。

## 2026-08-11 阅读路径确认

- 用户下一步先系统了解 `dex_vla` 工程，再进入新模型接入或真机部署。
- 固定阅读样例：`pickplace_bottle_lerobot_ACT_0715_10hz`。
- 阅读顺序：工程/部署资料 → ROS Action 与 launch → `PolicyRuntimeNode` → 配置装配链 → observation → worker/model service → action postprocess/retarget → safety/backend → rollout/scheduling → replay/acceptance → 新模型契约卡。
- 每一阶段只回答输入、入口、状态、输出、下游消费者和失败边界；未完成当前阶段的通过条件前不扩展到全仓。
- 本轮未修改产品代码，仅确认阅读计划。

### Action 外部入口快速阅读完成

- `ExecuteVLA.action` 定义最小外部契约：Goal 为 `language_instruction/model_name/allow_without_image/dry_run`；Result 为 `success/message/actions_count/inference_time_ms/failed_action_index`；Feedback 为空。
- `send_vla_goal.py` 的运行链为：解析 CLI → 创建 `ActionClient` → 等待 `vla/execute` → 构造 Goal → 异步发送 → 接收 accepted/rejected → 异步等待 Result → 根据 `result.success` 设置进程退出码。
- 重要边界：脚本不做模型选择、观测采集、动作转换或机器人控制；`--server-timeout-s` 只限制等待 Action Server，不限制后续推理时长；当前客户端没有主动 cancel 流程。
- 下一步：阅读 `src/dexbot_vla/dexbot_vla/nodes/policy_runtime_node.py` 的初始化、Goal 准入和执行入口。

### 2026-08-11 Code Map 与数据流梳理完成

- 用户明确调整阅读方式：先掌握整体架构和关键数据流，不逐行读源码；后续进入模型部署研究时再按需回到对应源码。
- 已产出 `docs/CODE_MAP.md`（`src/dexbot_vla` 的目录职责、关键入口、默认 ACT 数据流、关键契约、后续细读清单）。
- 已确认的入口与数据流：
  - 用户入口：`send_vla_goal.py` → `/vla/execute`（`ExecuteVLA` action）→ `PolicyRuntimeNode`。
  - 数据入口：相机 topic（`cam_global`、`cam_right_wrist`）、`/robot_driver/get_arm_joints`、`/robot_driver/hand/get_angles`、`language_instruction`。
  - 推理链：`RosInputAdapter` → `InferenceScheduler` → `WorkerClient` → `PolicyServiceWorker` / `ModelServiceClient` → `LeRobotBackend`。
  - 动作链：`ActionAdapter` → chunk strategy（ACT = `latest_smooth`）→ `ScheduledActionBuffer` → postprocess → `SafetyGate` → `GenericRobotBackend`/`RobotCommandExecutor` → robot driver。
  - 配置链：`policy_models.yaml` → `policy_templates.yaml` → `io_contracts.yaml` → `safety_limits.yaml` → `config_loader.load_runtime_bundle()` → `RuntimeBundle`。
- 默认样例模型 `pickplace_bottle_lerobot_ACT_0715_10hz` 关键事实：13D absolute action、horizon 100、10 Hz、committed segment 10、模型服务 `ws://127.0.0.1:18071`。
- 记录位置：`/home/tbl/Project/force_touch_model/dexbot_ros2_ws-dex_vla/docs/CODE_MAP.md`。

### 2026-08-11 工程上手方法论调研（未安装）

- 用户想把这套“先 Code Map / 数据流 / 接口，再干活，最后按需读源码”的方法固化为 Skill，并要求先搜索市面现成方案。
- 核心方法论：Phase 1 构建工程地图（目录、模块边界、核心文件）；Phase 2 追踪一条真实主链路（用户入口、数据入口、接口契约、数据流动、输出出口）；Phase 3 开始实际工作，只按需深入对应源码。
- 本地已有 Skills：`a-codebase-onboarding` 覆盖“证据地图/入口/链路”的产出，`b-source-code-tutoring` 覆盖“按需源码级追踪”，但没有一个 Skill 同时把三阶段串成完整工作流。
- 官方 OpenAI curated skills（39 个）中没有直接的 codebase onboarding / code map 类 Skill。
- 检索到的社区候选：
  - `OthmanAdi/codebase-knowledge-builder`：四阶段侦察/深读/artifact 编写，输出架构、组件表、数据流、Mermaid 图；与目标最接近。
  - `natsu1211/deepwiki-skill`：wiki 风格文档、源码行级引用、Mermaid 图验证、增量更新；适合详细文档化。
  - `heyEdem/codebase-indexer`：一次性扫描生成 `docs/architecture.md` 等五类文档并自动维护；适合“living docs”。
  - `punit-labs/onboarding-copilot`：生成 onboarding brief、架构地图、read-first 列表、gotchas；适合新人上手。
  - `alexanderop/walkthrough`：交互式 HTML + Mermaid 解释单条数据流；适合后续按需讲解。
  - `Graphify-Labs/graphify`：知识图谱式代码地图，较重，作为可选增强。
- 结论：没有单一现成 Skill 完全等价于“地图 → 干活 → 按需读源码”的组合；建议优先直接采用 `codebase-knowledge-builder`，或将其与本地 `b-source-code-tutoring` 组合，再决定是否自研一个瘦 Skill。当前未安装任何候选。

### 2026-08-11 Code Map 优化完成

- 用户要求优化 `docs/CODE_MAP.md` 以便自行继续阅读；仅修改该文档，未修改产品代码、配置或现有用户改动。
- 新版地图以四层组织：系统/进程边界、配置与 contract 解析链、默认 ACT 的单 Goal 真实路径、模型接入决策与 GR00T 缺口。
- 关键纠正：ROS runtime 通过 `WorkerClient` 管理轻量 worker；worker 通过 WebSocket 调用模型服务；LeRobot/OpenPI/FTP1 backend 位于模型服务端，而非 `PolicyRuntimeNode` 进程。
- GR00T 被明确标为待接入验证：当前 backend registry 仅有 `lerobot`、`openpi`、`ftp1`；需要先验证是否可复用 LeRobot backend 的 processor/relative-action 支持，否则新增服务端 backend，不能在 ROS runtime 写模型特例。
- 验证：`git diff --check -- docs/CODE_MAP.md` 通过；文档中引用的核心路径和 ACT 配置项存在；未执行运行时测试，因为本次为只读结构文档变更。
- 推荐下一步：按新版第 10 节，从 `PolicyRuntimeNode` 和 ACT 配置解析链开始阅读；需要接入 GR00T 时先填写第 8 节的契约卡，再决定配置复用或 backend 扩展。

### 2026-08-11 自训练 GR00T 接入只读调研

- 调研目标：检查 `/mnt/data/gr00t-finetune/outputs/lerobot_qingdao_pouring_gr00t_n1_7_v2_2cam/checkpoints/014051/pretrained_model`，确定接入 DexBot 所需改动边界；未修改产品代码、部署配置或 `docs/CODE_MAP.md`。
- checkpoint 已确认是完整 GR00T N1.7 full checkpoint：`model.safetensors` 约 9.34 GB，`type=groot`，13D state/13D action，`chunk_size=n_action_steps=40`，`use_relative_actions=true`，训练数据为 30 Hz 的 `rokae_right_arm_o6`。
- 数据转换脚本证明输入/动作顺序和单位均为右臂 7D rad + O6 手 6D 0--100，顺序为 `thumb_flex/thumb_abd/index/middle/ring/pinky`；与 DexBot 的 `right_arm_o6_hand_13d`、`dexbot_right_arm_o6_v1` 维度和手部顺序一致。
- 不能复用当前 `lerobot_backend.py`：它加载 `lerobot.dexbot.eval.policy_backend.LinkerPolicyBackend`，并要求 `right_arm_target/right_hand_cmd_100` 等 Linker 专用输出；当前训练用 LeRobot 分支没有该模块，GR00T 也只输出单一 `(B, 40, 13)` action tensor。
- GR00T 正确推理路径必须是 `preprocessor -> GrootPolicy.predict_action_chunk -> postprocessor(full chunk)`。`select_action()` 对 relative action 会抛出 `NotImplementedError`；postprocessor 必须紧接同轮 preprocessor，以 cached raw state 将 native relative chunk 反解码为 absolute 13D chunk。
- 已运行实际 dataset state + 两张录制相机帧的离线 probe（无 ROS/机器人命令）：成功得到 native 和 decoded `(1, 40, 13)`，decoded 值均为有限数；热态总耗时约 63--64 ms，冷态约 584 ms，CUDA 峰值约 9.6 GB（RTX 4090）。
- checkpoint 的 `config.json` 只声明 `cam_top/cam_right_wrist`，但序列化 processor 还含 `cam_left_wrist`。两相机 probe 成功，缺左腕只产生 warning，并按 `cam_top -> cam_right_wrist` 编码两视角；仍需在接入实现测试中固定这一行为，避免未来 LeRobot 版本变化。
- 推荐架构：新增服务端 `policy_backends/groot_backend.py` 和 registry `backend_id=groot`；保留 ROS runtime、worker、WebSocket、RosInputAdapter、scheduler、SafetyGate 和 robot executor 的通用实现。backend 对 runtime 输出应声明为 absolute 13D（native relative 仅为 backend 内部细节），且首版 `supports_rtc=false`、`latest_smooth`。
- 预计修改范围：新增 GR00T backend、backend registry、GR00T artifact exporter 分支或专用 exporter、checkpoint-side `dexbot_policy_artifact.json`/`deployment_contract.json`、`io_contracts.yaml` 的两相机 GR00T contract、`policy_templates.yaml` 的 30Hz non-RTC shadow 模板、`policy_models.yaml` 的模型注册和相应 backend/artifact/model-service tests。现有 LeRobot export 校验器要求 checkpoint-side absolute action，需要按“backend decoded absolute”语义扩展，而不能把 native relative 动作声明给 scheduler。
- 已确认设备事实：本项目中 ROKAE 与 Luoshi 指同一台实体设备，不构成机器人身份或硬件兼容性风险。
- 高风险未决事实：尚无训练录制数据与当前部署 profile 在关节零位、状态/动作坐标约定及任务初始姿态上的一致性证据。因此首版推荐 `shadow_only=true`，在完成坐标、起始姿态和分级真机验证前不批准真机命令；该限制不因 ROKAE/Luoshi 名称不同而产生。

### 2026-08-11 GR00T 离线接入实施启动

- 用户已确认采用独立服务端 `groot_backend.py`，不将 GR00T 兼容逻辑混入现有 Linker 专用 `lerobot_backend.py`。
- 本次只落地无需真实设备的完整范围：checkpoint artifact/deployment contract、backend registry、两相机 I/O contract、30 Hz non-RTC shadow template、模型注册和离线 tests。
- 明确非目标：不启动 ROS/真机节点，不调用相机或 robot state service，不下发机器人命令；设备相关验证保留给后续 shadow rollout。
- 工作单元：`TASK-002`；工程说明：`.project-log/specs/TASK-002-groot-offline-deployment.md`；架构依据：`DEC-002`。

### 2026-08-11 GR00T 离线接入完成

- 已新增服务端 `backend/policy_backends/groot_backend.py` 并在 registry 注册 `backend_id=groot`；单次 infer 固定执行 `preprocessor -> predict_action_chunk -> postprocessor(full 40-step chunk)`，只向通用链返回 canonical absolute `[40,13]`，拒绝 RTC context。
- 已为 checkpoint `014051/pretrained_model` 写入并签名 `deployment_contract.json`，生成 `dexbot_policy_artifact.json` 和 `model_deployment_manifest.json`。artifact SHA256 为 `f46e78262f9b368fcc5433f13266c6cb06b67b88939e8e2d44c9e217e4fe733f`，contract SHA256 为 `836369bee181aa75ff42c46f5c517893b4e109640580dec6221274e119de4343`。
- 已注册 `right_arm_o6_13d_groot_n17_h40`、`groot_n17_single_arm_o6_13d_30hz`、`groot_qingdao_pouring_014051_local:18083` 和 `rokae_pour_lerobot_GROOT_N17_014051_30hz`。模型原生 `cam_top -> runtime cam_global` 映射由 model contract/artifact 明确声明。
- 首版强制 `shadow_only=true`、`supports_rtc=false`、`latest_smooth`、30 Hz、`return_horizon_steps=40`，并明确关闭 arm/hand command 与 start/safe motion；未修改 ROS runtime、scheduler、SafetyGate 或 robot executor。
- 离线验证：focused test suite 为 `60 passed, 2 deselected`；真实 checkpoint + dataset sample 返回有限 absolute `[40,13]`，native shape `[1,40,13]`，cold total `555.126 ms`、warm total `65.756 ms`、RTX 4090 peak `9.427 GiB`；localhost JSON WebSocket service roundtrip 和 reset 成功。
- 环境限制：`lerobot` env 缺少 ROS 生成包 `dexbot_interfaces`，不能收集 `test_deployment_contract.py`；两项旧测试依赖不存在的历史绝对路径 scene assets。二者均不阻断 GR00T 离线验证。
- 已知后续项：checkpoint processor sidecar 仍声明未使用 `cam_left_wrist`，两相机运行成功但会 warning。真机准备好后，只允许进行 shadow rollout 以验证相机视角、state/action零位、坐标约定、任务初始姿态和安全事件；不得移除 shadow 限制或开启命令。

### 2026-08-11 Shadow Rollout 操作手册

- 已新增 `docs/GR00T_SHADOW_ROLLOUT.md`，包含模型服务、ROS VLA 启动、shadow goal 发送、通过标准和禁止项。
- 手册路径：`/home/tbl/Project/force_touch_model/dexbot_ros2_ws-dex_vla/docs/GR00T_SHADOW_ROLLOUT.md`。

### 2026-08-13 GR00T 远端推理配置与 dex_vla 推送

- 用户要求先配置 GR00T 为远端模型推理，再提交并推送 dex_vla，供连接机器人的远端电脑拉取启动。
- 远端检查：fetch 后 `origin/dex_vla` 仍与本地 HEAD 同为 `c35ca8a`，没有需要先同步的新提交。
- 配置改动：`policy_templates.yaml` 中 `groot_qingdao_pouring_014051_local` 改为 `host=192.168.97.184:18083`、`artifact_residency=service_host`；未修改 worker preset 路径、artifact 路径或公共模型配置。
- 验证：GR00T 相关聚焦测试 `60 passed, 2 deselected`；实际 `load_runtime_bundle()` 确认 `policy_artifact=None`、worker `--service-host 192.168.97.184`，即远端模式下不强制读本地权重。
- 已提交 `b067c56`（“接入GR00T N1.7独立backend并配置远端推理服务”）并推送 `c35ca8a..b067c56` 到 `origin/dex_vla`。
- 远端待处理：拉取后按远端机器实际路径修改 `groot_policy_service` worker preset；模型服务端需以 `0.0.0.0:18083` 启动并确认机器人电脑可访问该地址。

### 2026-08-13 新增 GR00T 远端部署与测试手册

- 已新增 `docs/GR00T_REMOTE_DEPLOYMENT.md`，供远端机器人电脑拉取后直接按文档操作。
- 手册覆盖：拉取分支、修改 `groot_policy_service` 本地路径、检查远端模型服务、colcon build、shadow 启动、发送 goal、通过标准和禁止项。
- 已提交 `feee740` 并推送 `b067c56..feee740` 到 `origin/dex_vla`。

### 2026-08-13 GR00T 模型服务地址改为 192.168.20.147

- 用户指定模型端固定使用 `192.168.20.147`。
- 已更新 `policy_templates.yaml` 的 groot `host`，并同步远端部署手册和 shadow 手册的服务端绑定说明。
- 验证：`load_runtime_bundle()` 输出 `ws://192.168.20.147:18083`，worker `--service-host=192.168.20.147`。
- 已提交 `06edc9d` 并推送 `feee740..06edc9d` 到 `origin/dex_vla`。
