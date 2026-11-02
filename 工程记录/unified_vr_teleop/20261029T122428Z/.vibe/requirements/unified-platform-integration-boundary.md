# 统一 VR 平台分工与适配边界

- **ID**：`unified-platform-integration-boundary`
- **版本**：1.2
- **状态**：active
- **目标**：让 Franka、ARX5、UR7e、Piper 共用一个统一 VR 平台版本，并明确人员分工与构型适配边界。
- **关联 Task**：`unified-platform-integration-boundary`
- **批准日期**：2026-10-29
- **证据**：用户确认的当前 VR 平台工作安排与统一平台目标。

## 参与者与分工

- 柏霖：负责 Franka 构型适配；负责统一 recording 新数据保存格式。
- 小航：负责 ARX5 控制代码适配并合入 `unified_vr_teleop`。
- 桉池：负责 UR7e 控制代码适配并合入 `unified_vr_teleop`。
- 姜灏：负责 VR 逻辑到 `rlinf_pipe` 的适配。
- 各构型代码合入后，在 Franka 等对应机械臂工控机上拉取同一版本，检查现场适配问题；发现问题通过 `feat` 或 `fix` 分支提交。

**验收条件**：每个构型有明确负责人；现场问题回到统一仓库的分支协作流程；不通过复制整套平台维护型号版本。

## 统一遥操作架构

目标链路：

```text
PICO → 统一输入层 → 公共遥操作层 / runtime
     → 统一 TeleopTarget → 通用控制 worker
     → RobotAdapter → 驱动与通信 → 机器人硬件
```

### 公共输入层与 runtime

统一输入层负责接收 PICO 数据、时间戳、有效性、新鲜度和连接恢复，不包含具体机器人通信、运动学或控制算法。

公共 runtime 负责手柄输入处理、Grip 锚定、按键、使能、人工/策略控制权、公共策略切换和统一目标生成。runtime 的输出是统一 `TeleopTarget`，至少包含 EEF pose、gripper target、timestamp/sequence、source 和 frame/TCP/单位约定。

runtime 不得知道当前是 Piper、ARX5、Franka 还是 UR7e，也不得知道下层使用 IK、笛卡尔阻抗控制或哪种厂商通信协议。

### 通用控制 worker

worker 是公共硬件执行边界，不实现具体机器人算法。它负责根据 config 选择并初始化 RobotAdapter，接收 `TeleopTarget`，执行通用的时间戳、序列号、控制租约和心跳检查，转发标准化反馈与诊断，并在目标过期、心跳超时或异常时调用 adapter 的 hold/stop。

worker 不需要了解 adapter 内部是 IK、笛卡尔阻抗还是其他控制实现，但需要稳定的 `connect`、`feedback`、`apply_target`、`hold`、`reset`、`release`、`close` 等生命周期接口。

### RobotAdapter

机器人差异集中在 RobotAdapter 和驱动通信边界。每个 adapter 负责坐标转换、EEF/关节目标转换、IK 或其他运动学、夹爪转换、限位/工作空间、控制器参数、状态标准化、hold、复位和故障恢复。

```text
PiperAdapter  : EEF → IK/关节限位 → CAN
Arx5Adapter   : EEF → IK/夹爪换算 → ROS2
FrankaAdapter : EEF → 工作空间校验/Cartesian 控制 → FCI
UR7eAdapter   : EEF → RTDE servo/cartesian 控制 → RTDE
```

**验收条件**：新增机器人只需要新增 adapter、驱动通信实现和 config；PICO、统一输入层、公共 runtime、通用 worker、采集和上传链路不因新增构型而复制机器人专属分支。

### 构型专属设备状态检查

每种机械臂还必须在 `robot/<type>/` 内提供自己的设备状态检查逻辑。状态检查不是公共层根据型号拼接的一组条件，因为不同机械臂在遥操作前、遥操作中和退出时可能需要不同的检查内容，例如连接状态、控制权、驱动模式、反馈新鲜度、故障/急停、夹爪状态、实时控制条件和通信健康度。

公共平台只提供统一的设备检查入口和结果展示协议：

```text
Web 统一“设备检查”按钮
  → 根据当前 config 选择 RobotAdapter / RobotDiagnostics
  → 执行当前机械臂的专属检查逻辑
  → 返回统一结构的通过/失败/警告、摘要、明细和下一步建议
```

不同机械臂的检查逻辑、检查顺序、设备字段和故障解释放在对应的 `robot/<type>/` 模块中；公共 Web 页面不直接访问 CAN、FCI、ROS2、RTDE 或厂商 SDK。检查结果必须明确区分“可发现”“可连接”“反馈有效”“可遥操作”和“已获得控制权”，不能用单一设备枚举结果代替完整就绪判断。

**验收条件**：同一 Web 设备检查入口可随 config 调用不同构型的检查逻辑；新增机械臂只新增其 robot 模块和 config 检查实现，不修改公共页面流程；检查失败不会被静默忽略或自动猜测为可用。

## 公共平台能力

不同型号机械臂共用同一套：

- 设备发现；
- VR 一键启动；
- VR 输入接收和控制逻辑；
- recording、任务、导出和上传公共链路；
- 统一的采集数据接口和落盘格式。

**验收条件**：更换机械臂构型不复制公共 VR 和采集流程；同一版本可在不同构型工控机部署和运行适配检查。

## 按型号适配的能力

以下内容必须由对应机械臂适配实现：

- 机械臂连接与通信：例如 Piper 使用 CAN，Franka 使用网线/FCI；
- 机器人控制器和控制指令下发；
- 机器人状态读取与遥测标准化；
- 运动学、坐标映射、夹爪、限位、复位和故障恢复；
- 该型号的配置文件和现场参数。

适配代码不得把型号差异扩散到公共输入层、公共 runtime、通用 worker、公共 recorder 或上传流程中。

**验收条件**：型号差异集中在 RobotAdapter、驱动通信和配置；公共层只通过标准接口消费输入、目标、状态、控制参考和事件。

## 配置与 Web 页面

- 不同机械臂的连接和现场参数放入对应 config 文件。
- Web 页面提供加载不同机械臂 config 的入口。
- 加载 config 后，页面根据型号呈现对应的连接、设置和操作内容。
- config 选择不等于维护独立平台版本；仍使用同一套公共平台代码。
- config 负责构型选择、通信方式、现场参数和控制模式声明，不承载复杂控制算法；adapter registry 根据 config 创建实际适配模块。

**验收条件**：切换 config 能选择对应构型；页面不展示与当前构型无关的连接和控制选项；未知或不完整配置应明确报错，不猜测硬件参数。

## VR 到 RLinf 接口边界

- 姜灏的工作是把统一 VR 逻辑适配到 `rlinf_pipe`。
- `rlinf_pipe` 消费统一的 VR observation/action 语义。
- 不为 Franka、ARX5、UR7e、Piper 分别创建一套平台或专属 recording 格式。
- 机器人具体通信和控制仍由统一平台的机器人适配层负责。

**验收条件**：RLinf 接口与机器人型号解耦；VR 公共输入和控制语义不因接入 RLinf 而复制成型号专属实现。

## 当前实现的迁移要求

- 当前 Piper/ARX5 的公共编排仍存在 Piper 硬编码，后续应逐步收敛为公共 runtime + 通用 worker + RobotAdapter，不把现状误认为最终结构。
- 当前 Franka 的独立 runtime/worker 可以作为过渡实现，但最终应将其中的公共 VR 控制行为收敛到公共 runtime，将 Franka 专属逻辑保留在 FrankaAdapter 和 FCI 驱动边界。本项目当前公共 runtime/worker 代码位于 `app/teleop/`；`Dagger_web/` 下没有独立的 `runtime/` 代码目录，不新增同名运行目录。
- 迁移必须保持控制安全、生命周期和故障处理语义；不得为了抽象而修改 Franka 控制算法、增益、限位或安全参数。
- 任何真实机器人运动验证都必须在获得用户确认后分阶段执行。

## 范围外

- 本 baseline 不定义 HDF5 字段细节；详见 `hdf5-recording-format.md`。
- 不修改具体机械臂控制算法、增益、限位或安全参数。
- 不在本 baseline 中规定现场真机验收结果。

## 未决事项

- 各构型合入 master 的具体顺序和验收负责人排期：不阻塞边界固化，属于项目执行计划。
- `rlinf_pipe` 的具体协议字段和版本：阻塞接口技术设计，不改变本 baseline 的解耦原则。

## 变更控制

新增或改变公共/适配边界时，必须说明影响的构型、公共模块、配置、部署和测试；确认后递增本 baseline 版本，不直接覆盖已批准规则。

## 版本历史

### v1.0（已 supersede，2026-10-29）

固化人员分工、公共设备发现/VR 启动/控制/采集能力、按型号连接与控制适配、config 页面切换和 RLinf 解耦边界。

### v1.1（当前，2026-10-29）

用户批准并新增统一遥操作架构：PICO → 统一输入层 → 公共 runtime 输出统一 `TeleopTarget` → 通用 worker → RobotAdapter → 驱动通信 → 硬件。明确 worker 只负责通用执行生命周期和安全协议，运动学、EEF/关节转换、夹爪、限位、复位和故障恢复属于 RobotAdapter；当前 Franka 独立 runtime 是过渡实现，后续逐步收敛，不在本轮直接重构。

### v1.2（当前，2026-10-29）

用户确认先在 `feat/franka` 分支把 Franka 构型收敛到上述架构，再合并回 master；其他构型在后续工作中按该形态对齐。当前代码组织中，公共 runtime/worker 保持在 `app/teleop/`，不创建 `Dagger_web/runtime/` 代码目录；机器人适配实现放在 `robot/franka/`，构型控制参数集中在 `config/robots/franka.yaml`。

### v1.3（当前，2026-10-29）

补充构型专属设备状态检查：统一 Web 入口根据 config 选择 `robot/<type>/` 的检查逻辑，返回统一结果；检查实现和厂商协议访问不得扩散到公共页面。检查必须覆盖与该构型相关的连接、反馈、控制权和遥操作就绪条件。
