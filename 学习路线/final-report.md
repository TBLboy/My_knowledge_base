# 面向机器人职业的 VLA 与世界模型八周学习路线

## 执行摘要

### 结论

你的目标不是立刻训练一个通用机器人，而是能在工作讨论、面试和阅读新论文时正确判断一个系统属于什么路线、解决了什么瓶颈、其证据是否足以支持宣称。最有效的顺序不是从最新的 VLA 论文开始，而是：

1. **先理解控制问题**：状态、动力学、目标/奖励、策略、规划和闭环反馈的关系。
2. **再理解世界模型**：为何不直接预测像素，为什么要在潜变量中预测，以及“用模型规划”和“在模型中想象训练策略”是两条不同路径。
3. **随后理解机器人数据与行为克隆**：VLA 本质上首先是从大规模、多机器人示范学习的视觉-语言条件策略，而不是传统 MPC 的直接替代品。
4. **最后理解融合前沿**：VLA 的语义泛化能力与世界模型的预测/规划能力正在融合；截至 2026 年，这一方向尚未形成统一、已在真实接触丰富操作中被充分验证的标准范式。

建议以 **8 周、每周 6–8 小时**完成主线。精读 18 篇骨干论文，另保留 10 篇按兴趣选读。这样能形成结构化的理论链，而不是停留在“知道很多模型名字”。

### 当前判断（截至 2026-07）

- **VLA 主线**已经从 RT-2 的“把动作离散为语言 token”发展到 OpenVLA 的开放可微调基线，以及 $\pi_0$ 的连续 flow-matching 动作生成。动作表示、数据覆盖、推理延迟和跨本体对齐，是比单纯模型参数量更关键的工程/研究变量。[C8][C10][C13]
- **世界模型主线**可分为 latent dynamics（PlaNet/Dreamer/TD-MPC2）和生成式视觉世界模型两类。前者在高频控制、样本效率、MPC 上更成熟；后者更容易利用视频数据并提供可解释的“想象未来”，但接触、动作可控性、长期误差与实时性仍是核心难题。[C3][C4][C6][C17]
- **融合方向**常被称为 World Action Model（WAM），但它是新兴的概念框架而非稳定 SOTA 类别。可分为“先预测再选动作”的级联方案和“联合生成未来状态与动作”的联合方案；不要把漂亮的视频预测等同于可用于机器人规划的物理模型。[C18]
- 对职业准备而言，最值得建立的是四种判断能力：**模型表示什么、动作如何生成、训练数据来自哪里、闭环时如何处理不确定性和失败恢复**。

## 一张知识地图

```text
最优控制 / MPC
  已知动力学 f(s, a) -> 在有限时域滚动优化动作序列 -> 执行第一步并重规划
        |
        +-- 模型式强化学习（MBRL）
              学习 f_hat、奖励/价值、不确定性
              |
              +-- 显式状态模型：PETS、MBPO
              |
              +-- 潜变量世界模型：PlaNet -> Dreamer -> DreamerV3
              |     |                 |
              |     |                 +-- 在想象轨迹中训练 actor/critic
              |     +-- CEM/MPC 在 latent 中在线规划
              |
              +-- 控制导向隐式模型：TD-MPC -> TD-MPC2
              |
              +-- 视频/3D/生成式世界模型：预测可见未来、用于数据生成/评估/候选动作筛选

行为克隆 / 机器人基础策略
  观测 o + 指令 l -> 动作 a
       |
       +-- ACT / Diffusion Policy：解决长动作序列与多峰动作分布
       |
       +-- Open X-Embodiment / RT-X：多机器人数据标准化与跨本体预训练
       |
       +-- VLA：预训练 VLM + 机器人示范 -> 语言条件闭环策略
              RT-1 -> RT-2 -> OpenVLA -> pi_0 / OpenPI 等
       |
       +-- VLA + 世界模型（前沿）：利用预测未来验证、排序、规划或与动作联合生成
```

## 必须先统一的概念

| 概念 | 最小定义 | 不要混淆为 |
| --- | --- | --- |
| **状态** $s_t$ | 对决策足够的环境内部表示；真实机器人通常不可完全观测 | 原始相机图像本身 |
| **观测** $o_t$ | 相机、力觉、关节角等传感器读数 | 完整状态 |
| **动力学/世界模型** $p(s_{t+1}|s_t,a_t)$ | 给定动作预测环境如何演化的模型 | 单帧图像生成器、只做感知的 VLM |
| **策略** $\pi(a_t|o_{\le t},l)$ | 从观测/历史和指令输出动作的规则或网络 | 世界模型本身 |
| **MPC** | 有限预测时域内优化动作序列，只执行第一步，下一时刻重规划 | 一次性开环规划 |
| **行为克隆（BC）** | 用示范监督学习 $o,l \to a$ | 通过试错优化奖励的 RL |
| **VLA** | 把视觉、语言和机器人动作统一到同一策略中，直接输出控制命令 | 只用 LLM 选择预定义技能的系统 |
| **动作表示** | token、末端位姿增量、关节命令、action chunk、diffusion/flow 轨迹等 | 模型的“语言理解能力” |
| **跨本体（cross-embodiment）** | 在不同机械臂、传感器、动作空间之间复用数据/策略 | 不加适配就能控制任何机器人 |
| **世界动作模型（WAM）** | 联合或紧耦合地建模动作和动作引起的未来状态 | 已有统一的工业标准模型 |

## 八周路线

每周默认：2 小时概念材料、3–4 小时精读、1–2 小时整理。不要以“读完 PDF 页数”为指标；每篇主论文只需要能回答“问题、建模、训练、决策、证据、局限”六项。

### 第 1 周：控制问题与 MBRL 的语言

**目标**：先把 VLA 和世界模型放回控制论框架。读完后能说明 MPC 为什么每次只执行第一个动作，以及模型误差为什么会在长时域放大。

1. 学习：MDP/POMDP、状态转移、奖励、value/Q function、trajectory optimization、receding horizon、CEM。
2. 精读：[P1] *Probabilistic Ensembles with Trajectory Sampling for Robust Model-Based Deep RL*（PETS，2018）。
3. 精读：[P2] *When to Trust Your Model: Model-Based Policy Optimization*（MBPO，2019）。
4. 选读：[P3] *Model-Based Reinforcement Learning: A Survey*（Moerland et al., 2023）。

**产出**：画出 $o_t \to \hat{s}_t \to \hat{s}_{t+1}\to a_{t:t+H}$ 的 MPC 图；用自己的话解释 ensemble、aleatoric/epistemic uncertainty、model exploitation。

**自检**：如果学到的模型不是完美的，为什么 MPC 往往比长开环 rollout 更稳？MBPO 和在线 MPC 分别把模型用于哪里？

### 第 2 周：从像素到潜变量世界模型

**目标**：理解世界模型的核心压缩选择：不必预测所有像素，只需保留对控制有用的信息。

1. 精读：[P4] *World Models*（Ha & Schmidhuber，2018）。
2. 精读：[P5] *Learning Latent Dynamics for Planning from Pixels*（PlaNet，2019）。
3. 精读：[P6] *Dream to Control: Learning Behaviors by Latent Imagination*（Dreamer，2020）。

**必须看懂**：RSSM 的 deterministic state 与 stochastic state 各自负责什么；latent overshooting；PlaNet 在 latent 中 CEM 规划，而 Dreamer 如何通过 imagined rollouts 更新 actor/critic。

**自检**：PlaNet 和 Dreamer 都有世界模型，为什么一个以规划为核心，另一个以在模型内训练策略为核心？

### 第 3 周：可扩展的潜变量控制世界模型

**目标**：把 Dreamer 和控制导向模型并列比较，理解为什么“预测好图像”未必等于“控制好机器人”。

1. 精读：[P7] *Mastering Diverse Domains through World Models*（DreamerV3，2023/2025 Nature）。
2. 精读：[P8] *TD-MPC: Model Predictive Control for Vision-based Control*（2022）。
3. 精读：[P9] *TD-MPC2: Scalable, Robust World Models for Continuous Control*（ICLR 2024）。
4. 选读：[P10] *MAMBA: Model-Based RL with ...* 或同类近期控制导向 world-model 工作，仅为拓宽，不追求穷尽。

**比较表**：DreamerV3 是“world model + imagination actor-critic”；TD-MPC2 是“decoder-free control-oriented latent model + local trajectory optimization”。两者都不是 VLA。

**自检**：何时更偏向 Dreamer 的 imagined policy learning，何时更偏向 TD-MPC 的 decision-time planning？为什么 TD-MPC2 有意不做像素解码？

### 第 4 周：机器人策略基础，不跳过行为克隆

**目标**：理解 VLA 出现前机器人策略已经解决了什么，尤其是高维、多峰和时间相关动作生成。

1. 精读：[P11] *Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware*（ACT，2023）。
2. 精读：[P12] *Diffusion Policy: Visuomotor Policy Learning via Action Diffusion*（RSS 2023）。
3. 精读：[P13] *Open X-Embodiment: Robotic Learning Datasets and RT-X Models*（2023）。
4. 选读：*A Generalist Agent*（Gato，2022），只理解“统一序列建模”的历史意义。

**必须掌握**：action chunking 如何降低逐步 BC 的误差累积；diffusion/flow 为什么适合多峰连续动作；为什么 OXE 的数据标准化与跨本体 action representation 是 VLA 的必要基础。

**自检**：ACT、Diffusion Policy、VLA 三者的输入输出类似，关键差异却在哪里？为什么新的 VLA 论文常仍以 ACT/Diffusion Policy 作为强基线？

### 第 5 周：VLA 的诞生与第一代扩展

**目标**：明确 VLA 的独特价值是把 web-scale 语义先验接入低层动作，而非“让机器人会聊天”。

1. 精读：[P14] *RT-1: Robotics Transformer for Real-World Control at Scale*（2022）。
2. 精读：[P15] *PaLM-E: An Embodied Multimodal Language Model*（2023）。
3. 精读：[P16] *RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control*（2023）。
4. 选读：*VIMA: General Robot Manipulation with Multimodal Prompts*（2023）。

**必须掌握**：RT-2 的动作 token 化与 VLM 共微调；为何保留视觉语言任务可减少语义遗忘；RT-2 的 1–3 Hz 大模型闭环控制意味着什么；PaLM-E、RT-2 与“VLM 规划器 + 独立控制器”的区别。

**自检**：将连续控制动作离散成 token 的收益和代价分别是什么？“CoT 能输出”是否等同于“能可靠完成长时域物理任务”？

### 第 6 周：开放 VLA 与连续动作生成

**目标**：掌握 2024–2026 最重要的可讨论架构转折：开放、微调、数据、token action 对 flow action。

1. 精读：[P17] *Octo: An Open-Source Generalist Robot Policy*（2024）。
2. 精读：[P18] *OpenVLA: An Open-Source Vision-Language-Action Model*（2024）。
3. 精读：[P19] *$\pi_0$: A Vision-Language-Action Flow Model for General Robot Control*（RSS 2025）。
4. 跟踪阅读：[P20] NVIDIA *GR00T N1* technical report / project materials（2025），理解双系统/扩散式动作专家的设计趋势。

**比较重点**：

| 模型 | 要理解的贡献 | 主要代价 |
| --- | --- | --- |
| Octo | 开放、模块化 transformer + diffusion action head，适合多本体适配 | 不依赖大 VLM 的 web 语义能力有限 |
| OpenVLA | 开放 7B VLA、970k 实机轨迹、LoRA/量化适配 | 自回归离散动作的频率与精度受限 |
| $\pi_0$ | VLM backbone + flow matching 连续 action chunk，面向灵巧双臂任务 | 关键训练数据和完整可复现条件并非完全开放 |
| GR00T N1 | 快慢系统/动作专家视角，强调人形与跨本体数据 | 报告数据、基准与部署条件需要逐项核验 |

**自检**：为何 $\pi_0$ 的 flow matching 不是世界模型？为什么模型“开放权重”与“可在任意机器人上直接使用”是两件事？

### 第 7 周：VLA 与世界模型融合的前沿

**目标**：知道融合的真实问题，不把新名词误当成熟范式。

1. 精读：[P21] *World Model for Robot Learning: A Comprehensive Survey*（2026，综述，重点读 taxonomy、policy coupling、evaluation）。
2. 精读：[P22] *World Action Models: The Next Frontier in Embodied AI*（2026，综述/观点，重点读 cascaded vs joint taxonomy）。
3. 选读一篇具体方法：[P23] *IRASim*（2025，action-conditioned video world model）或 *3D-VLA*（2024，3D future-state generation），目的是看“预测未来”怎样接到规划，不以排行榜为结论。
4. 回看 [P9]、[P16]、[P19]，写出它们各自是否具备显式 action-conditioned future prediction。

**必须掌握**：

- **级联（cascaded）**：先给候选动作 rollout 未来，再用 reward/VLM/规则选择动作；优点是模块清楚，缺点是误差级联和延迟。
- **联合（joint）**：模型同时或共享表征预测未来状态与动作；优点是对齐潜力，缺点是训练目标冲突、可验证性弱。
- 视频真实感、物理一致性、控制有效性是三套不同指标。

**自检**：如果一个视频世界模型只生成“像真的”未来画面，但动作改变不了对象运动，它为何不能用于 MPC？

### 第 8 周：整合、SOTA 辨识与长期跟踪

**目标**：从论文消费者转为能持续判断进展的人。

1. 精读：[P24] *Vision-Language-Action Models for Robotics: A Review Towards Real-World Applications*（IEEE Access，2025）。
2. 精读：[P25] *Vision-Language-Action in Robotics: A Survey of Datasets, Benchmarks, and Data Engines*（2026，预印本）。
3. 按兴趣精读一篇：$\pi_{0.7}$（2026）或 MolmoAct 2（2026）等最新开放/半开放 generalist policy；只将其作为“追踪对象”，不要据单篇宣称断言全领域 SOTA。
4. 产出一页个人地图：对每个模型填写表示、动作头、数据、控制频率、是否显式 world model、评测设置、已知失败模式。

**自检**：面对“某模型达到 SOTA”的新闻，你能否先问：在哪个本体、哪些任务、是否零样本、是否同一数据、真实机器人试验多少次、闭环频率和失败恢复如何？

## 精读骨干论文清单

| ID | 论文 | 地位 | 只需抓住的一句话 |
| --- | --- | --- | --- |
| P1 | Chua et al., PETS, 2018 | MBRL/MPC 起点 | ensemble dynamics + trajectory sampling 处理模型不确定性 |
| P2 | Janner et al., MBPO, 2019 | MBRL 重要分支 | 在短 model rollouts 上扩充真实数据、训练 model-free policy |
| P4 | Ha & Schmidhuber, World Models, 2018 | 概念原型 | VAE + RNN + controller 说明可在压缩潜空间中控制 |
| P5 | Hafner et al., PlaNet, 2019 | latent planning | RSSM + latent CEM planning |
| P6 | Hafner et al., Dreamer, 2020 | imagination learning | 不必在真实环境频繁试错，在 latent imagination 中训练行为 |
| P7 | Hafner et al., DreamerV3, 2023 | 稳定可扩展世界模型 | 一组超参跨 150+ 任务，强调训练稳定性 |
| P8 | Hansen et al., TD-MPC, 2022 | 控制导向 latent world model | 不重建像素，学习服务局部规划的隐式 latent dynamics |
| P9 | Hansen et al., TD-MPC2, 2024 | 连续控制骨干 | 将控制导向 world model 扩到多任务/多本体规模 |
| P11 | Zhao et al., ACT, 2023 | 机器人 BC 基线 | action chunk + CVAE 解决时间对齐和多步控制 |
| P12 | Chi et al., Diffusion Policy, 2023 | 生成式动作策略 | diffusion 建模连续、多峰的 action sequence |
| P13 | OXE / RT-X, 2023 | 数据基础设施 | 多机构多本体机器人数据是 generalist policy 的关键资产 |
| P14 | Brohan et al., RT-1, 2022 | 大规模多任务机器人策略 | transformer 在真实机器人数据规模化后的可靠性基线 |
| P15 | Driess et al., PaLM-E, 2023 | embodied VLM 背景 | 将连续传感器输入接入语言模型的路线 |
| P16 | Brohan et al., RT-2, 2023 | VLA 命名与路线确立 | 把动作当 token，与 web VLM 数据共微调 |
| P17 | Octo, 2024 | 开放 generalist policy | 多机器人数据预训练和可适配 diffusion policy |
| P18 | Kim et al., OpenVLA, 2024 | 开放 VLA 基线 | 7B、970k 真实轨迹、VLM 特征与高效微调 |
| P19 | Black et al., $\pi_0$, 2025 | 连续动作 VLA 转折 | VLM 语义先验 + flow matching action chunks |
| P21 | Hou et al., World Model for Robot Learning, 2026 | 最新地图 | world model 作为 policy component、simulator、data engine 的三种角色 |
| P22 | Wang et al., World Action Models, 2026 | 融合概念地图 | cascaded 和 joint VLA-world-model 方案的边界 |

## 哪些内容暂时不必深挖

- 不必在八周内推导 Kalman filter、iLQR、PPO、diffusion/flow matching 的完整数学证明；需达到“知道它们优化的对象、假设与失败方式”的程度。
- 不必追逐每个 2025–2026 VLA 名称。很多论文的真正增量只是数据、tokenizer、视觉 encoder、速度优化或一个新 benchmark。
- 不要把自动驾驶的世界模型结果直接外推到灵巧操作。接触、遮挡、形变、力控和高自由度使 manipulation 的闭环验证更难。
- 不将“world model”与“数字孪生”混用。前者是由数据学得、可用于决策的预测模型；后者通常是工程化物理仿真与实时状态同步系统。

## 职业场景的阅读与表达模板

每读一篇论文，只写半页，回答：

1. **任务与输入输出**：机器人/仿真？视觉、语言、本体感觉、力觉？动作是关节、末端增量还是 chunk？
2. **问题**：数据效率、语义泛化、动作多峰性、长时域、跨本体、实时性、失败恢复中的哪一项？
3. **世界模型是否存在**：预测什么未来？是否 action-conditioned？预测是在像素、3D、token 还是 latent？
4. **决策如何发生**：MPC 搜索、actor-critic、行为克隆、diffusion/flow 采样、VLM planner，还是混合？
5. **证据是否可比**：真实机器人多少次？任务是否新？训练数据是否包含同类本体或对象？是否与同数据量基线比较？
6. **限制**：误差积累、接触动力学、频率、数据偏差、置信度、安全性、闭环恢复分别如何处理？

面试中一个稳健的概括可以是：

> VLA 解决的是从大规模视觉语言先验和多本体示范中学习具备语义泛化的条件策略；世界模型解决的是预测动作后果、支持规划、评估或想象学习。当前前沿不是简单把两者拼接，而是要让预测表征对控制有用、动作可控、延迟可接受，并在真实接触任务中验证闭环可靠性。

## 建议的长期信息源

- 每月查看一次 [C24] 的 VLA survey 项目页和 [C21] 的 robot world-model survey 项目页，优先看其数据集、基准和政策耦合部分更新。
- 定期关注 RSS、CoRL、ICRA、IROS、NeurIPS、ICLR 的 robotics/embodied/MBRL 论文，而不是只追公司博客。
- 将论文按“数据、表示、动作生成、决策、评测”五个标签保存。任何新模型都能被放入这五格，避免术语制造的混乱。

## 可信度与边界

- 对 PlaNet/Dreamer/TD-MPC2、RT-2/OpenVLA/$\pi_0$ 的定位为**高置信度**，来自原始论文和官方项目资料。
- 对 2026 年 WAM、视频世界模型和新 generalist policies 的“当前 SOTA”描述为**中等置信度**：大量工作仍是预印本，基准、数据混合、硬件和真实试验协议尚未统一，不适合做跨论文的绝对排名。
- 本报告以机械臂和移动操作为中心，不覆盖自动驾驶、纯导航或人形全身控制的全部独立文献。

## 参考来源

完整链接、证据与引用索引见 `research-materials/`。

- [C1] Chua et al., PETS, NeurIPS 2018
- [C2] Janner et al., MBPO, NeurIPS 2019
- [C3] Hafner et al., PlaNet, ICML 2019
- [C4] Hafner et al., Dreamer, ICLR 2020
- [C5] Hafner et al., DreamerV3, 2023 / Nature 2025
- [C6] Hansen et al., TD-MPC2, ICLR 2024
- [C7] Brohan et al., RT-1, 2022
- [C8] Brohan et al., RT-2, 2023
- [C9] Open X-Embodiment / RT-X, 2023
- [C10] Kim et al., OpenVLA, 2024
- [C11] Octo, 2024
- [C12] Zhao et al., ACT, 2023
- [C13] Black et al., $\pi_0$, RSS 2025
- [C14] Chi et al., Diffusion Policy, RSS 2023
- [C15] Driess et al., PaLM-E, ICML 2023
- [C16] Kawaharazuka et al., VLA Review, IEEE Access 2025
- [C17] Hou et al., World Model for Robot Learning Survey, 2026
- [C18] Wang et al., World Action Models Survey, 2026
