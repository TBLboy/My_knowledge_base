# 关键一手来源笔记

## PlaNet — Learning Latent Dynamics for Planning from Pixels

- URL: https://arxiv.org/abs/1811.04551
- 来源类型：A，原始研究论文
- 核心：从像素学习 deterministic + stochastic latent dynamics，并在潜空间做快速在线 planning；提出 latent overshooting。
- 关联：解释“world model 不必显式预测高维像素”。
- 限制：并非语言条件机器人策略，也不是跨本体系统。

## Dreamer — Dream to Control

- URL: https://arxiv.org/abs/1912.01603
- 来源类型：A，原始研究论文
- 核心：在学得的 compact latent state 里 imagined rollout，通过 value gradients 学习行为。
- 关联：与 PlaNet 的主要差异是从在线规划转为在模型中训练 actor/critic。
- 限制：模型内训练会遭受模型偏差；该论文不能替代真实机器人闭环证据。

## TD-MPC2 — Scalable, Robust World Models for Continuous Control

- URL: https://arxiv.org/abs/2310.16828
- 来源类型：A，ICLR 2024 原始研究论文
- 核心：decoder-free、隐式、控制导向的 latent world model；局部 trajectory optimization；317M 模型在 80 多任务和多 action space 上训练。
- 关联：模型式连续控制的现代骨干，不可与 VLA 混为一谈。
- 限制：不以 web-scale semantic generalization 或语言接地为目标。

## RT-2 — Vision-Language-Action Models Transfer Web Knowledge to Robotic Control

- URL: https://arxiv.org/abs/2307.15818
- 来源类型：A，原始研究论文与官方项目
- 核心：把机器人动作离散成文本 token，与 web vision-language task 和机器人轨迹共微调，保留 VLM 的新对象、符号与简单推理泛化。
- 关键数字：5B 模型约 5 Hz；55B 模型约 1–3 Hz，采用远程 TPU 服务。
- 限制：输出 action token 并不预测动作后果，因此不是显式 world model。

## OpenVLA — An Open-Source Vision-Language-Action Model

- URL: https://arxiv.org/abs/2406.09246
- 来源类型：A，原始开放研究论文
- 核心：7B 参数，DINOv2 + SigLIP + Llama 2，970k 实机轨迹；提出面向新场景的高效 LoRA 微调和量化部署。
- 原文报告：在作者的 29 项任务、多本体评测中，绝对任务成功率比 RT-2-X 高 16.5%，使用 7 倍更少参数。
- 限制：上述比较只能在该论文数据、任务和实现内成立；不要泛化成普遍排名。

## $\pi_0$ — A Vision-Language-Action Flow Model for General Robot Control

- URL: https://arxiv.org/abs/2410.24164
- 来源类型：A，RSS 2025 原始研究论文
- 核心：在预训练 VLM 上以 flow matching 生成连续动作序列，混合单臂、双臂和移动操作数据，面向高灵巧任务。
- 关联：动作生成从自回归离散 token 向连续 flow/diffusion 发展的代表。
- 限制：它建模的是动作条件分布，并非状态转移动力学；不是世界模型。

## World Model for Robot Learning Survey

- URL: https://ntumars.github.io/wm-robot-survey/
- 来源类型：B，2026 预印本综述，含公开维护项目页
- 核心：按 world models for policy、world models as learned simulators、robotic video generation 组织；强调 action-controllability、长期 rollout 和 task utility。
- 关联：用于理解生成式世界模型如何进入 policy 学习、评估、数据生成和计划。
- 限制：前沿部分多为预印本，术语和评测尚未标准化。

## World Action Models: The Next Frontier in Embodied AI

- URL: https://arxiv.org/abs/2605.12090
- 来源类型：B，2026 预印本综述/框架论文
- 核心：提出 WAM，区分 cascaded（先预测状态后导出动作）和 joint（联合预测状态与动作）架构。
- 关联：帮助组织 VLA-world-model 融合文献。
- 限制：WAM 是新术语和分类法，不应误认为已被所有研究者采用或对应单一 SOTA。
