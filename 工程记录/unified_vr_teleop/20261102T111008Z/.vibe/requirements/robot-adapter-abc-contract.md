# RobotAdapter 抽象契约与 Franka 模板固化

- ID：`robot-adapter-abc-contract`
- 状态：active
- 版本：1.0
- 批准日期：2026-10-30
- 关联 Task：`robot-adapter-abc-contract`

## 目标

把 Franka 当前已经被 `DeviceWorker` 真实使用的设备适配接口，从仅有 `Protocol` 文本约定固化为显式抽象基类模板，供后续新 EEF 构型继承和实现；本次不改变任何机器人运行行为。

## 参与者

- 平台维护者：维护公共设备契约与公共 worker。
- 构型开发者：继承 `RobotAdapter` 实现自己的 `xxxAdapter`，并注册到 registry。
- 操作员：不因本次接口改造看到任何控制语义变化。

## 范围内

1. 公共 `robot/core/adapter.py` 定义设备控制抽象契约。
2. `FrankaAdapter` 显式继承该契约，保持现有实现与控制语义。
3. registry、接入文档与契约测试同步，形成后续构型可复用模板。
4. 离线验证契约缺失能提前失败、Franka 契约完整、现有回归无新增失败。

## 范围外

- Piper / ARX5 的控制链路迁移或强制继承；它们仍保留现有 `control_runtime` 路径。
- 将启动、关闭、健康检查、故障恢复等操作流程并入 `RobotAdapter`；这些仍由 `robot/<type>/flows.py` 注册。
- 控制算法、增益、坐标映射、限位、看门狗时长、夹爪或复位行为变化。
- HDF5、录制、上传和公共 UI 行为变化。
- 真实机械臂运动；真机验收由用户显式操作。

## 业务规则与验收标准

### R1 设备契约显式且可提前校验

`RobotAdapter` 是抽象基类，声明公共 worker 所需的设备生命周期接口：`connect`、`feedback`、`apply_targets`、`hold`、`start_reset`、`reset_running`、`reset_outcome`、`set_reset_pose`、`close`，以及 `sides`、`warnings`、`controllers` 的必要约定。

**验收**：缺少任一抽象方法的测试 Adapter 在实例化时立即抛出 `TypeError`，不要等到设备运行中途才失败。

### R2 Franka 成为可继承参考模板

`FrankaAdapter` 显式继承 `RobotAdapter`；`create_adapter()` 返回该统一类型；现有方法只调整接口声明所需的签名或类型标注，不改变实现行为。

**验收**：`issubclass(FrankaAdapter, RobotAdapter)` 为真；Franka 现有 adapter/worker 测试全部通过。

### R3 设备契约与操作流程保持分离

`RobotAdapter` 只管设备会话、标准化反馈、目标校验与下发、保持和复位；启动、关闭、健康检查、恢复等操作员流程继续由 flows 注册。

**验收**：ABC 不包含 UI/流程执行器职责；`flows_for()` 分发和现有流程测试不受影响。

### R4 模板包含行为契约，而不只是方法名

提供可复用的契约测试，覆盖抽象方法缺失和 Franka 的基本反馈、目标校验、保持、复位结果与关闭语义；接入文档说明新构型需实现 Adapter、注册 registry、提供 flows 并运行契约测试。

**验收**：契约测试对不完整实现失败、对 Franka 通过；接入文档不再把 Adapter 描述为无继承约束的 duck typing 模板。

### R5 不改变现有运行语义

本次仅固化接口，不借机重构控制器或统一 Piper/ARX5。

**验收**：编译检查通过；完整离线测试套件无新增失败；提交只包含本任务相关的契约、Franka 声明、测试与文档。

## 约束与质量属性

- 最小改动、向后兼容现有 `DeviceWorker` 调用。
- 契约文档必须区分“ABC 保证方法存在”和“测试保证行为正确”。
- 任何后续新构型必须同时提供设备 Adapter 与 flows，不能只复制类名。

## 假设与失效条件

- 假设后续新 EEF 构型会复用公共 `eef_runtime + DeviceWorker`；若某构型继续使用独立 runtime，则不得为迎合本模板制造未使用的空壳 Adapter。
- 若公共 worker 的设备调用发生变化，必须同步升级本契约、Franka 模板和契约测试。

## 未决项

无阻塞未决项。

## 批准与变更记录

- v1.0（2026-10-30）：用户确认先固化 Franka，Piper/ARX 后续再按模板迁移；批准开始实现。
