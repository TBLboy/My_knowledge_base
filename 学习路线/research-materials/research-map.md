# 研究地图

## 工作定义与边界

| 术语 | 工作定义 | 相邻概念 | 纳入规则 | 排除规则 |
| --- | --- | --- | --- | --- |
| 基于模型控制 | 用已知或学习到的动力学预测动作后果，再用于规划或策略学习 | MPC、MBRL、system identification | 模型显式影响决策/训练 | 仅有感知模型、纯规则控制 |
| 世界模型 | action-conditioned 的预测性状态表示或生成器 | RSSM、latent dynamics、video model、learned simulator | 预测未来状态/观测/奖励/终止之一 | 只输出动作的 VLA/BC policy |
| VLA | 视觉和语言条件下直接产生机器人控制动作的策略 | VLM planner、robot foundation model | 输出低层/连续控制命令或 action chunk | 仅选择预定义 skill 的 LLM planner |
| WAM | 对未来状态和动作紧耦合建模的 VLA-world-model 方案 | video policy、joint state-action model | 世界预测与动作生成在同一决策链 | 给 VLA 添加文本记忆但不预测未来 |

## 问题树

1. 机器人为何需要预测模型？
   - 已知模型下，MPC 如何运行？
   - 学习模型时，误差和不确定性如何影响控制？
2. 世界模型为什么能从像素学习控制？
   - 什么是对控制充分的 latent state？
   - 在线规划和 imagined policy learning 的差异？
3. VLA 解决了什么不同问题？
   - web-scale 语义先验如何接地为动作？
   - 多机器人数据与 action representation 如何影响泛化？
4. 为什么要融合 VLA 和世界模型？
   - VLA 的反应式 mapping 缺什么？
   - 预测视频/3D/latent future 怎样才真能支持闭环控制？
5. 如何评判新论文？
   - 预测是否 action-controllable、物理一致、长时稳定？
   - 真实机器人、OOD、频率、安全和失败恢复证据是否充分？

## 候选路径

| 路径 | 解决的问题 | 核心机制 | 需要理解的前置知识 | 初始证据 |
| --- | --- | --- | --- | --- |
| latent MBRL | 从高维观测学习控制 | RSSM/latent transition + planning 或 imagination | POMDP、VAE、actor-critic/MPC | PlaNet、Dreamer、DreamerV3 |
| control-oriented MBRL | 实时连续控制 | implicit latent model + local planning | TD learning、MPC、value learning | TD-MPC2 |
| robot BC / generative policy | 从示范学精细动作 | action chunks、CVAE、diffusion | imitation learning、sequence models | ACT、Diffusion Policy |
| VLA | 语义泛化与语言接地 | VLM backbone + robot action head + heterogeneous data | VLM、tokenization、OXE | RT-2、OpenVLA、$\pi_0$ |
| WAM | 在动作前瞻中规划/验证 | cascaded rollout 或 joint prediction-action | 上述两条主线 | WAM/WM surveys、IRASim、3D-VLA |

## 比较维度

| 维度 | 定义 | 应查看的证据 |
| --- | --- | --- |
| 表示 | 像素、3D、token、latent，及是否含不确定性 | 模型结构和训练目标 |
| 动作 | 离散 token、连续控制、chunk、diffusion/flow | action head、频率、延迟 |
| 决策 | MPC、actor-critic、BC、planner-policy hierarchy | rollout 是否影响 action selection |
| 数据 | 真实示范、仿真、人类视频、web data | 数据规模、相机/本体多样性、动作标注 |
| 泛化 | 新对象、任务、环境、本体、语言组合 | 数据泄漏控制和 OOD protocol |
| 可靠性 | 接触、遮挡、长期误差、失败恢复、安全 | 闭环真实试验、风险与不确定性分析 |

## 筛选策略

- 论文以原始论文、公开项目和同行评审综述为主；2026 新工作以“路线信号”而非绝对排行榜对待。
- 每条主线选择一个概念原型、一个成熟骨干、一个最新扩展，避免同类论文堆叠。
- 将 VLA 与 world model 分开理解后，再读融合论文，避免将所有 foundation policy 误标为 world model。
