# 阶段② 分支状态总表 v0.5（I/D/A 全池 + 本轮 prior-art）

> 目的：在 v0.4（I/D 池）与 v0.5 idea 池（A1–A8）基础上，加入本轮新增 prior-art，逐项给出可辩护判定。
> 规则：任何"通用形式已被覆盖"的方向一律降级或 kill；只有能给出**具体物理结构 + 可证定理**的路线才保留。

## 0. 本轮新增 prior-art 证据（2026-09-28，Crossref/OpenAlex 检索）

| 方向 | 关键工作 | DOI |
|---|---|---|
| Koopman 机器人学习综述 | Shi, Haseli, Mamakoukas, Bruder, Abraham, Murphey, Cortés, Karydis, T-RO 2026 | 10.1109/tro.2026.3654384 |
| 软体多段机器人 Koopman MPC | Lv et al., ICRA 2025 | 10.1109/icra55743.2025.11127925 |
| 软体机器人 Koopman 谱分析 | Komeno et al., SICE 2022 | 10.23919/sice56594.2022.9905758 |
| 软体机器人 Koopman 辨识（视觉光点型） | Palacios-Lazo et al., 2026 | 10.29057/icbi.v14iespecial.15510 |
| 蠕虫机器人 DMD-Koopman 控制 | Rahmani & Redkar, Biomimetics 2024 | 10.3390/biomimetics9110666 |
| switched Koopman 学习/预测控制 | Blischke & Hespanha CDC 2023；Peitz & Klus Automatica 2019；Ning et al. JSSC 2025；Ju et al. SCL 2026 | 10.1109/cdc49753.2023.10384106 / 10.1016/j.automatica.2019.05.016 / 10.1007/s11424-025-4546-0 / 10.1016/j.sysconle.2025.106340 |
| hierarchical Koopman MPC | Boyle & Stockar, JDSMC 2023 | 10.1115/1.4056703 |
| Koopman + 冗余机械臂约束跟踪 | IEEE RA-L 2024（Koopman-ZNN） | 10.1109/lra.2024.3349966 |
| 非参数控制 Koopman | Bevanda et al., TAC 2026 | 10.1109/tac.2026.3693027 |
| Koopman 逆动力学/显式模型跟随 | Hançoğlu & Efe, TII 2026 | 10.1109/tii.2026.3705896 |
| Koopman 预测跟踪控制 | Wang et al., EAAI 2025 | 10.1016/j.engappai.2025.111349 |

要点：软体机器人 Koopman 建模/MPC 已有多篇直接工作；switched / hierarchical / input-transformation / inverse-dynamics 的**通用形式均已被覆盖**。

## 1. A 池逐项判定

| ID | 判定 | 依据 |
|---|---|---|
| A1 actuation-factorized | **kill（通用形式）** | 通用 input transformation 已被 Cibulka/Korda/Haniš 2025（SIADS）覆盖；逆动力学/模型跟随见 Hançoğlu 2026。仅当得到**新的 actuator-realization 定理**且 `G_p` 非平凡才可重开。 |
| A2 relative-degree-preserving | **保留（需具体定理）** | "control-aware observable" 有先例（Uchida & Duraisamy 2023）；但"lifting 保留输入-输出相对阶并给出可检查 rank 条件"未见直接覆盖。软体视觉平台相对阶可验证性存疑。 |
| A3 quantized-delay | **降级/kill** | sampled-data/delay/quantized 为成熟理论，仅移植到 Koopman 创新不足。 |
| A4 mode-conditioned | **kill（通用形式）** | switched Koopman 学习与 MPC 已被 Blischke 2023 / Peitz 2019 / Ning 2025 / Ju 2026 覆盖；仅当引入**新的 mode-transition 或安全定理**才可重开。 |
| A5 task/actuator dual | **kill（通用形式）** | hierarchical Koopman MPC 已被 Boyle & Stockar 2023 覆盖；易退化为标准级联控制。 |
| A6 learned actuator authority | **暂缓** | 与 adaptive Koopman / unknown input gain 高度相邻，可辨识性困难。 |
| A7 control-relevant subspace | **保留（需具体定理）** | control-aware learning 有先例；"discarded subspace 对闭环 task error 的界"未见直接覆盖，但需形成数据可检验判据。 |
| A8 operator family / transfer | **暂缓** | 易变成多任务学习，理论定位不符。 |
| **A9（新）actuation-redundancy kernel gating** | **保留（最具体，但邻域拥挤）** | 软体平台 `v=(dx,dy)`∈R² 经差动映射到 4 绳，存在 2 维零空间（共模/张紧方向）；该方向不被 `v` 直接控制，却决定张紧/松弛模式、进而门控动力学。邻域：通用 nullspace control allocation（T-CST/L-CSS overactuated UAV）、Koopman-ZNN 冗余机械臂（RA-L 2024）。差异点：这里零空间方向是**物理隐藏模式且门控动力学**，而非运动学冗余。 |

## 2. 当前存续候选（shortlist）

```text
A2  relative-degree-preserving lifting        （理论强，可验证性存疑）
A7  control-relevant subspace selection       （理论中，判据待构造）
A9  actuation-redundancy kernel gating        （物理最具体，邻域拥挤）
```

共同的理论骨架（把三者串起来，并修复已验证缺陷）：

```text
闭环 task-tracking 界 =
  f( encoder/预测误差, 有限数据估计误差,
     history 截断误差（部分可观测, G4）,
     输入映射秩缺陷 / 零空间方向（G2/G9） )
```

该骨架直接修复 `Main34.tex` L719–737 的 Schur/‖·‖ 错误（改用 Lyapunov metric 或显式加权范数假设），并把 G1/G2/G4 统一进一个可验证界。

## 3. 诚实结论

- 通用 operator 方向（A1/A3/A4/A5）已全部被 prior-art 覆盖，**不能作为中心创新**。
- 目前**没有一个经完整 prior-art + 理论门禁的最终路线**；只有 A2/A7/A9 三条"具体结构 + 定理"候选。
- 论文核心创新主张（theory-pure 严谨性路线 vs 软体物理结构路线 vs 二者结合）属于 C 级方向决策，需用户确认后才能进入 Theory Construction（S6）与代码落地。

## 4. 下一步（待用户确认方向后执行）

1. 选定 shortlist 中的主线（或确认"以严谨闭环界为骨架、以某平台结构为载体"的组合）；
2. 对选定路线做 S6 Theory Construction：写出定理陈述、假设、证明骨架，并先做反例/边界检查（Proof Audit，S7）；
3. 用现有冻结代码的 smoke 数据做最小可行性验证（不重训、不改代码，仅离线用已存 checkpoint/数据检验假设）；
4. 通过后再解冻代码进入阶段③。
