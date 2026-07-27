# 路线比较矩阵

| 路线 | 预测/生成的核心对象 | 决策方式 | 强项 | 关键限制 | 骨干论文 |
| --- | --- | --- | --- | --- | --- |
| 显式 MBRL / PETS | 状态转移分布与不确定性 | CEM/MPC 轨迹优化 | 样本效率、原理直接 | 长时域模型误差、状态/观测建模成本 | PETS |
| MBPO | 短 model rollout | model-free policy 更新 | 数据效率、避免长 rollout | 仍会受模型偏差影响 | MBPO |
| latent planning | RSSM/latent dynamics | latent CEM/MPC | 从像素控制、避免高维规划 | latent 是否保留控制充分信息 | PlaNet |
| latent imagination | latent dynamics、reward/value | actor-critic imagined rollout | 不必逐次在线搜索 | policy 受 imagined model bias 影响 | Dreamer / DreamerV3 |
| 控制导向 world model | decoder-free latent dynamics、value | 局部轨迹优化 | 连续控制、实时规划、控制相关表征 | 语义/开放世界泛化不足 | TD-MPC2 |
| 行为克隆 / ACT | action chunk | 直接监督策略 | 稳定、适合示范任务 | OOD 与错误恢复弱 | ACT |
| Diffusion Policy | 多步连续 action distribution | diffusion sampling | 多峰动作、轨迹平滑 | 采样延迟、语义先验有限 | Diffusion Policy |
| VLA token policy | 视觉、语言、离散 action token | 自回归动作生成 | web-scale 语义泛化、语言接地 | 低频、量化误差、数据对齐 | RT-2 / OpenVLA |
| Flow VLA | 连续 action chunk | flow matching | 连续高维动作、灵巧操作 | 数据/算力要求高、不是 dynamics model | $\pi_0$ |
| VLA + world model / WAM | future state + action 或级联 rollout | 验证、排序、MPC、联合生成 | 物理前瞻、利用视频数据的潜力 | 可控性、接触、长期误差、实时评测 | WAM survey / IRASim / 3D-VLA |
