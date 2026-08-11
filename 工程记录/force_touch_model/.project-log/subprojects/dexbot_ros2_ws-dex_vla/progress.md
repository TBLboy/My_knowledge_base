# Progress

## 当前阶段：VLA 工程整体阅读与新模型接入准备

目标不是逐函数读完整个 `dexbot_vla`，而是建立一条可运行、可定位、可扩展的心智模型：

```text
launch → PolicyRuntimeNode → ExecuteVLA Action
       → RuntimeBundle → observation
       → Worker/model service → action chunk
       → adapter/retargeter → SafetyGate
       → robot backend/driver → ExecuteVLA.Result
```

已形成的阅读原则：

1. 先读真实运行场景，再读局部实现；
2. 先建立模块边界和数据契约，再看函数细节；
3. 以现有可用模型 `pickplace_bottle_lerobot_ACT_0715_10hz` 作为黄金样例；
4. 新模型优先走配置、contract 和 artifact 扩展，只有新增框架/协议时才改 backend/worker 源码；
5. 暂时跳过 telemetry、monitor、取消/重置细节以及 `RolloutCoordinator` 的完整状态机。

推荐阅读顺序：

```text
vla_task_bringup.launch.py
→ ExecuteVLA.action / send_vla_goal.py
→ policy_runtime_node.py 主入口
→ runtime_execution.yaml
→ policy_models.yaml
→ policy_templates.yaml
→ io_contracts.yaml
→ config_loader.py
→ RosInputAdapter / WorkerClient / action adapter / SafetyGate / robot backend
```

新 GR00T 模型接入前需要整理模型契约卡，至少确认 observation、action、机器人关节顺序和单位、夹爪编码、推理频率、chunk、坐标系、归一化以及服务协议。

下一步：建立默认 ACT 模型的启动图、配置解析图和输入输出数据流图。

## 2026-08-11 dex_vla 一次通读路径

用户决定先系统理解 `dex_vla` 工程。后续固定沿 `pickplace_bottle_lerobot_ACT_0715_10hz` 追踪一条真实链路：

```text
资料/README → launch/Action → PolicyRuntimeNode → RuntimeBundle 配置装配
→ observation → worker/model service → action adapter/retargeter
→ SafetyGate → robot backend/driver → RolloutCoordinator/scheduling
→ replay/acceptance → 新模型契约卡
```

每部分需要记录真实源码入口、输入字段、状态变化、输出消息、下游消费者和失败边界；完成整条链路前不开始新模型接入。未修改产品代码。
