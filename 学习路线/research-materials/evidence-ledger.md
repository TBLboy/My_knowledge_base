# 证据总账

| ID | 主张 | 立场 | 等级 | 来源 | 日期 | 条件与限制 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E-001 | PlaNet 从像素学习含确定和随机成分的 latent dynamics，并以在线 latent planning 控制 | 支持 | A | [C3] | 2019 | 主要是视觉连续控制基准，不等同真实通用机器人 | Verified |
| E-002 | Dreamer 在世界模型的 latent imagination 中训练行为，而非对每一步做在线规划 | 支持 | A | [C4] | 2020 | 代表一类 actor-critic world model 方法 | Verified |
| E-003 | DreamerV3 用单一配置跨 150+ 任务，强调 world-model RL 的训练鲁棒性与泛化配置 | 支持 | A | [C5] | 2023/2025 | 广泛领域结果不能直接证明真实接触操作能力 | Verified |
| E-004 | TD-MPC2 是 decoder-free、控制导向的 latent world model，使用局部轨迹优化，可扩展至多任务多本体连续控制 | 支持 | A | [C6] | 2024 | 317M/80-task 结果依赖指定训练数据和基准 | Verified |
| E-005 | RT-2 通过动作 token 化和 web VLM + robot data 共微调，把 VLM 变为闭环 VLA | 支持 | A | [C8] | 2023 | 最大模型实际控制频率 1–3 Hz；不是高频全身控制方案 | Verified |
| E-006 | OXE/RT-X 证明多机器人数据集与动作标准化是 cross-embodiment generalist policy 的重要基础 | 支持 | A | [C9] | 2023 | 数据异质并不消除动作空间、相机和采样偏差 | Verified |
| E-007 | OpenVLA 是开放 7B VLA，基于 970k 真实机器人示范并提供高效微调路径 | 支持 | A | [C10] | 2024 | 相对性能应在其 29 任务、多本体评测协议内解读 | Verified |
| E-008 | $\pi_0$ 用 VLM backbone + flow matching 生成连续 action chunk，面向多平台灵巧操作 | 支持 | A | [C13] | 2024/2025 | 不应把 flow action head 误称为 world model | Verified |
| E-009 | 世界模型在机器人学习中可作为 policy component、learned simulator、数据生成和评估工具 | 支持 | B | [C17] | 2026 | 综述而非单一实验；大量近期工作为预印本 | Verified |
| E-010 | WAM 可按 cascaded（预测后动作）与 joint（状态-动作联合）分类 | 支持 | B | [C18] | 2026 | 是新提出的分类框架，术语尚未行业标准化 | Verified |
| E-011 | 视频质量不能单独验证模型可用于控制或规划 | 支持 | A | [C17], [C18] | 2026 | 需评估动作条件性、长期物理一致性和闭环 task utility | Verified |
| E-012 | 截至 2026，VLA+world-model 尚不存在跨数据、本体和真实任务统一可比的绝对 SOTA | 支持 | B | [C16]-[C18] | 2025-2026 | 结论基于综述指出的基准与数据不一致 | Verified |
