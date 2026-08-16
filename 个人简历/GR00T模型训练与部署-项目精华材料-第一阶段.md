# GR00T / LeRobot 模型训练与部署项目精华材料（第一阶段）

- **项目状态：**第一阶段精华材料，非最终简历文案
- **用户确认身份：**小组探索经历
- **主要来源：**
  - `工程记录/gr00t-finetune/.project-log/progress.md`
  - `工程记录/gr00t-finetune/.project-log/current-session.md`
  - `工程记录/gr00t-finetune/.project-log/requirements.md`
  - `工程记录/force_touch_model/.project-log/progress.md`
  - `工程记录/force_touch_model/.project-log/current-session.md`

## 1. 项目定位

围绕 GR00T N1.7 / LeRobot 具身智能策略模型，探索从机器人示范数据转换、embodiment 配置、模型微调、训练评估到远端策略部署的完整链路，并将实验结果映射到真实机器人右臂 + O6 灵巧手场景。

该项目属于小组探索，不按个人独立项目处理。最终简历重点写用户实际负责的实验闭环和工程贡献。

## 2. 用户可突出贡献方向

当前记录支持后续重点确认以下模块：

- v2.1 → LeRobot v3.0 数据集转换和格式兼容验证。
- 右臂 + O6 13D embodiment 配置。
- normalization stats 计算和训练输入准备。
- 低显存训练参数配置、训练启动和 checkpoint 管理。
- 训练结果分析、open-loop 评估和基线对比。
- GR00T 代码工程地图和训练/推理/评估/部署入口整理。
- GR00T runtime bundle / service_host 远端部署准备。

需要后续确认：这些模块中哪些由用户实际编码、运行、调参或独立排查，哪些是组内共同完成。

## 3. 数据与 embodiment

记录确认的数据规模：

- 148 个有效 episode。
- 47,250 帧。
- 30 FPS。
- 3 路相机。
- 右臂 7D + O6 灵巧手 6D，共 13D 状态/动作。
- 数据从原始 v2.1 结构转换为 LeRobot v3.0。
- 生成 13D normalization stats 并用于训练。

处理链路：

```text
原始示范数据
  → v2.1 → v3.0 结构转换
  → LeRobot DatasetMetadata 校验
  → 13D embodiment 配置
  → normalization stats
  → GR00T Trainer
```

## 4. 训练工程

### 4.1 环境和基础模型

- GR00T N1.7 基础模型，约 3B 发布口径。
- PyTorch 2.9.0 + CUDA 12.8。
- flash-attn 2.8.3。
- RTX 4090 环境。
- 官方 base checkpoint 已下载并验证可读。
- 接入 W&B 记录训练实验。

### 4.2 低显存配置

为适应显存和训练稳定性，记录中使用：

- batch size = 1。
- gradient accumulation = 8。
- paged AdamW 8-bit。
- gradient checkpointing。
- workers = 0。
- constant learning rate = 5e-5。
- warmup steps = 1500。

### 4.3 正式训练

- 完成约 30,000 steps 正式重训。
- 约 5.3 次全量数据 pass。
- final loss 约 0.038。
- 保留 checkpoint-22400、checkpoint-28000、checkpoint-30000。
- 记录中判断此前失败的主要原因是训练暴露量不足，旧实验约 0.44 pass，本次增加到约 5.3 pass 后动作预测能力明显改善。

## 5. 评估与结果

使用训练集 open-loop 评估验证动作预测能力：

- 评估 4 条轨迹。
- 平均 MSE = 23.62。
- 平均 MAE = 1.15。
- 单轨迹对比：
  - 旧 20k checkpoint：MSE = 717.38。
  - current-state baseline：MSE = 82.91。
  - checkpoint-30000：MSE = 13.73。
- 单轨迹相对旧 checkpoint MSE 下降约 98%，相对 baseline 下降约 83%。

当前证据支持的结论：

- 训练集 open-loop 动作预测效果显著改善。
- 训练链路和评估脚本已形成可复现闭环。
- 未见轨迹泛化和真机闭环仍需单独验证。

不能直接写成：模型已经完成生产级真机部署或泛化能力已被证明。

## 6. 部署与工程地图

- 梳理 GR00T 工程目录、模型/Processor、训练、策略推理、评估、部署和扩展入口。
- 明确 `Gr00tPolicy` 输出 action chunk，不替代外部 robot adapter 的控制和安全职责。
- 完成 runtime bundle / service_host 模式的远端部署准备。
- 记录远端服务不读取本地权重的运行边界。
- 编写远端部署手册，明确模型、服务、客户端和机器人适配器之间的职责。

## 7. 关键工程难点与解决方向

| 难点 | 解决方向 |
| --- | --- |
| 原始 v2.1 数据不能直接被 v3 Dataset 使用 | 编写只读转换脚本并验证 148 episode / 47,250 frames 数据 |
| 机器人 embodiment 与模型输入维度不一致 | 自定义右臂 7D + O6 6D 配置，统一 13D state/action |
| 训练显存和吞吐受限 | batch=1、梯度累积、8-bit optimizer、gradient checkpointing |
| 训练 loss 下降但动作能力不足 | 增加数据 pass，并用 open-loop 与 current-state baseline 对比 |
| 大型仓库入口复杂 | 创建 GR00T 代码工程地图，按任务路径整理入口和边界 |
| 模型输出不能直接控制机器人 | 保留外部 robot adapter、控制器和安全责任边界 |
| 真机/未见轨迹证据不足 | 将训练集 open-loop、泛化和真机闭环分开记录 |

## 8. 可用于简历的价值标签

- GR00T N1.7 / LeRobot
- 具身智能策略模型微调
- LeRobot v3.0 数据集转换
- 自定义 embodiment
- 13D state/action
- normalization stats
- 低显存训练
- open-loop evaluation
- checkpoint 管理
- W&B 实验记录
- service_host / remote deployment
- 模型与机器人 adapter 边界

## 9. 第一版简历表达方向（非最终文案）

### 稳健版方向

> 作为小组成员参与 GR00T N1.7 具身智能策略模型训练与部署探索，完成机器人示范数据向 LeRobot v3.0 的转换、右臂+O6 13D embodiment 配置、低显存训练和 open-loop 评估；基于 148 个 episode、47,250 帧数据完成 30,000-step 微调，4 条轨迹平均 MSE=23.62、MAE=1.15，并参与远端推理服务部署准备。

### 强表达版方向

> 参与 GR00T N1.7 机器人策略模型从数据适配到远端部署的工程闭环，负责 v2.1→LeRobot v3.0 转换、13D embodiment/归一化配置、低显存训练和 checkpoint 评估；在 148 episodes、47,250 frames 上完成 30,000-step 微调，训练集 open-loop MSE 从旧 checkpoint 的 717.38 降至 13.73，并完成 service_host 远端推理链路梳理。

最终需根据用户实际分工决定使用“参与”“负责”“主导”中的哪一级强度。

## 10. 待用户补充的信息

1. 用户在小组中具体负责数据转换、训练、调参、评估、部署的哪些模块。
2. 30,000-step 训练是否由用户亲自启动、监控和结果分析。
3. 是否参与过未见轨迹评估、仿真 rollout 或真实机器人闭环。
4. 远端部署是否真实运行过，用户负责服务端、客户端还是 adapter。
5. 指标是否允许公开，以及目标岗位更偏模型训练还是机器人部署。
