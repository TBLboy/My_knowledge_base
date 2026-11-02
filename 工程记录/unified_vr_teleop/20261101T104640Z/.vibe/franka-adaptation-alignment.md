# Franka 与统一适配架构对齐审计

日期：2026-10-29。对象：当前 `feat/franka` / master `c9db3c4`。范围：只读核对 Franka、Piper、ARX5、UR7e 的配置、分派、控制入口、适配层和测试；未修改业务代码，未连接或运动真机。

## 目标架构

```text
PICO → 统一输入层 → 公共遥操作层 → 机器人适配层 → 驱动/通信 → 硬件
```

最终目标是：除机器人适配层和驱动/通信层外，其余模块公共复用，由 config 选择构型。

## 结论矩阵

| 构型 | config 选择 | 连接/遥测适配 | 控制/安全适配 | 公共 VR 控制链路 | 当前结论 |
| --- | --- | --- | --- | --- | --- |
| Piper | 有，`piper.yaml` | `robot/piper/telemetry.py`、CAN SDK | `controller/kinematics/motion/reset/recovery/settings` | `app.teleop.control_runtime` + `control_worker` | 最接近目标模型，但公共编排仍直接 import Piper |
| ARX5 | 有，`arx5.yaml` | `robot/arx5/transport.py`、ROS2、`ArxArmManager` | 独立 controller/IK/motion/reset/recovery/settings | 与 Piper 共用 `control_runtime`/worker，通过 registry 分派 | 结构基本符合适配层分离；配置仍有大量现场空值，未开放真机证据 |
| Franka | 有，`franka.yaml` | `robot/franka/manager.py`、client、独立 worker、FCI/网线 | `controller/motion/policy/runtime/worker/gripper` | 复用 XR receiver、Authority/Buttons、Journal/策略部分，但绕过公共 `control_runtime`/`control_worker` | 适配代码集中，但 VR 编排是独立 Franka runtime，不是目标中的完全公共链路 |
| UR7e | 有，`ur7e.yaml` | 仅 RTDE 草案；`PENDING_TYPES` 门控 | 无可部署控制实现 | 不开放 | 不满足当前目标，必须先完成适配再谈公共链路 |

## 已对齐部分

- `profiles.py` 按 `robot` 配置加载 profile，Franka 已从 pending 门控解除，`create_arm_manager()` 选择 `FrankaArmManager`。
- Franka 的 FCI/网线连接、七轴反馈、TCP 目标、夹爪、工作空间校验、复位目标、hold、控制租约/超时和错误停止均位于 `robot/franka/`，没有放入 Piper controller。
- Piper 和 ARX5 共享页面、XR 接收、控制权/DAgger、普通采集等公共模块；ARX5 通过 registry 选择自有 controller/IK/motion/recovery/transport。
- config 已能影响机械臂类型、左右臂选择、连接参数和对应 Web 页面。

## 关键偏差

### F1：Franka 没有走与 Piper/ARX5 相同的公共控制编排

`app/teleop/supervisor.py` 对 Franka 直接启动 `robot.franka.runtime`；Piper/ARX5 启动 `app.teleop.control_runtime`。Franka runtime 自己实现状态循环、Authority、PoseClutch、策略、复位和 worker 调度。

这意味着当前公共 VR 控制链路并非完全公共：输入接收和部分 DAgger 组件复用，但“控制编排/目标生成/生命周期”有两套实现。属于 **implementation-drift / major**，不是可凭配置消除的小差异。

### F2：公共编排层仍存在 Piper 硬编码

`control_runtime.py` 顶部直接导入 Piper 的 reset/motion/IK/settings，`control_worker.py` 也直接导入 Piper 的参数、恢复和映射；虽然后续对 ARX5 使用 registry，编排层仍不是纯公共接口。Franka 通过旁路 runtime 避开了这部分耦合，而不是证明目标边界已经实现。

属于 **architecture drift / major**。本轮 Franka 适配不应直接重构公共控制链，需单独做架构决策后再处理。

### F3：Franka 的“机器人适配层”内部包含独立 VR 编排逻辑

`robot/franka/runtime.py` 不只是机器人适配器：它还读取 Pico、处理按键、人工/策略控制权、DAgger journal、复位请求和目标循环。按目标模型，这些应属于公共输入/遥操作层；Franka 适配层应接收标准化目标并提供控制/反馈/生命周期。

属于 **implementation-drift / major**。但同事实现可能是为隔离七轴/TCP链路的过渡方案，不能未经确认直接拆分。

### F4：UR7e 目前不能作为已适配构型

`profiles.py` 的 `PENDING_TYPES` 仍包含 `ur7e`；master 的 `robot/ur7e/` 只有 transport 草案，配置也标明待开发。远端 `feat/ur7e-rlinf-bridge` 是外部 RLinf 执行端网页桥接，不等价于 master 的机器人适配层已完成。

属于 **missing-implementation**，不阻塞当前 Franka 工作，但阻止声称“四种构型均已符合目标模型”。

### F5：Franka 测试证据当前受环境阻塞

使用总工作区 `.venv` 执行 Franka/profile 测试时，收集阶段因缺少 `scipy` 无法导入 `robot.franka.worker`；本次依赖安装来自基础 `requirements.txt`，Franka 专用环境/依赖尚未安装。未获得通过测试证据。

属于 **missing-test / environment-blocked**。不代表实现失败，也不能声称测试通过。

## 当前建议

1. 本轮先完成 Franka 现有独立适配链路的功能验证，不立即把它拆进公共 `control_runtime`；拆分会同时影响 Piper/ARX5 公共控制编排，属于独立架构任务。
2. 明确将 F1/F2 记录为后续“公共控制编排去 Piper 化、Franka 接入同一 orchestrator”的架构任务。
3. 先补齐 Franka 专用依赖和离线测试环境，再验证 Franka worker、PoseClutch、控制租约、复位、故障停止、配置切换和 UI。
4. 当前能准确宣称的是：Franka 适配代码已配置化且集中在 `robot/franka/`，并部分复用了公共 XR/DAgger/页面能力；不能宣称已完全符合“只有适配层和驱动层不同”的最终架构。
