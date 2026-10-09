# 阶段② P1-only 物理路线评估 v0.1

> 日期：2026-09-29  
> 背景：用户确认 P1 输入为**关节力矩/电流指令**，并选择先评估 P1-only 物理路线。  
> 结论：P1-only 结构清晰，但 prior art 拥挤，且最小结构化 lifting spike 未显示明显优势；尚不能直接定为路线。

## 1. 已确认事实

- **P1 输入语义（用户确认）：** 关节力矩/电流指令（不是速度或位置增量）。
- **P1 状态：** `x=[q1,dq1,q2,dq2,q3,dq3]`，全状态可测；`q1∈[-0.87,0.87]`、`q2∈[0.36,1.64]`、`q3∈[-0.05,0.64]` rad。
- **重力偏置证据：** 第 2 关节力矩有明显正偏置（`absmean≈3.11`，范围 `-0.21~5.71`），与“含重力补偿的力矩指令”一致。
- **速度一致性：** `dq` 与位置数值微分的相对误差 6.8%/11.3%/16.2%，说明 `dq` 是真实速度而非严格数值微分。
- **数据：** train 15 条（74655×6）、val 4 条（19909×6）、test 1 条（4976×6）；`u` 3 维。**无 P1 训练 checkpoint。**
- 诊断脚本：`C:/Users/12187/AppData/Local/Temp/opencode/profile_p1_data.py`；结果 `p1_data_profile.json`。

因此 P1 是一个**全状态可测、力矩输入、二阶 Euler-Lagrange（EL）结构**的系统。

## 2. prior art（P1-only Koopman / EL）

| 工作 | 内容 | 威胁 |
|---|---|---|
| Singh, Singh, Kashyap, Keshavan, arXiv:2509.17010（2025-09 投稿，2026-02 v2） | 广义动量 Koopman：解耦已知线性驱动通道、只学未驱动动力学、GESO 鲁棒控制，机械臂实验验证 | **直接占位**：正是 P1 力矩输入的动量结构 |
| Zheng, Shi, Li, Shi, CDC 2024（10.1109/cdc56724.2024.10886671） | Euler-Lagrange 系统的 Koopman 事件触发学习 | 同族 EL-Koopman |
| Hançoğlu & Efe, IEEE Access 2026（10.1109/access.2026.3652500） | 机械臂 Koopman 显式模型跟随控制 | 机械臂 Koopman 控制 |
| Gadginmath, Krishnan, Pasqualetti, TAC 2024（10.1109/tac.2024.3417188） | 基于 Koopman 生成元的数据驱动反馈线性化 | 数据驱动 FL |
| Asada CCK 2024/2025；Bruder T-RO 2020；Mamakoukas T-RO 2021 | 机械臂/软体 Koopman 控制 | 邻域拥挤 |

要点：**“EL + 力矩输入 + 动量结构 + Koopman + 鲁棒控制”这一 P1 主线已被 2509.17010 直接占据。** P1-only 若只是重构该结构，不能构成中心创新。

## 3. 最小结构化 lifting spike

比较 P1 一步预测（ridge）：

| 特征集 | 维数 | train RMSE | val RMSE |
|---|---:|---:|---:|
| 原始 affine `[1,x,u]` | 10 | 0.24044 | 0.22556 |
| 物理结构化 `[1,x,sin q,cos q,dq²,u]` | 19 | 0.23676 | 0.22293 |

多步（结构化）：

| horizon | val RMSE |
|---:|---:|
| 2 | 0.36782 |
| 3 | 0.48206 |

结论：手工物理特征相对原始 affine **几乎没有明显收益**（val RMSE 仅低约 0.0026）。因此“加物理特征做结构化 lifting”本身**不构成路线**；若 P1-only 要成立，必须来自**结构化的辨识目标/控制器/定理**，而不是特征工程。

脚本：`spike_p1_structured_lifting.py`；结果：`spike_p1_structured_lifting.json`。

## 4. 仍然可能存在的 P1-only delta（需自行构造并防守）

以下都不是已批准路线，只是**尚未被直接占据、但必须证明非平凡且可数据检验**的候选构造：

1. **有限数据闭环界（理论型）：** 对动量结构化的力矩驱动机械臂，给出“未驱动模型近似误差 + 力矩界 → 闭环跟踪误差”的显式有限数据界。  
   - delta vs 2509.17010：后者主打 GESO 鲁棒补偿，未给出该显式有限数据界。  
   - 风险：Strässer/Korda 的 finite-data→closed-loop 框架已覆盖一般情形。
2. **保无源性/保正定性的数据驱动 lifting：** 用数据辨识 `M(q)≻0` 并保持 port-Hamiltonian/passivity 结构，再用无源控制器闭环。  
   - delta：结构保持 + 无源证书。  
   - 风险：physics-informed / port-Hamiltonian Koopman 领域拥挤。
3. **历史窗口作为观测器 + 全状态特例的统一界：** 把 P1（全状态，观测误差=0）与 P2（部分可观测）统一在一个“未驱动模型误差 + 观测/历史截断误差 + 输入通道条件”的闭环界里。  
   - delta：统一框架 + 显式分解界。  
   - 风险：Park & Hwang CDC 2024（Koopman 观测性 + output-canonical EDMD）等已触及观测性方向。

## 5. 当前判定

- **确认：** P1-only 主结构已被 2509.17010 占据；手工结构化 lifting 无数据优势。
- **未批准：** 上述三个 delta 均**尚未**证明“非平凡 + 数据可检验 + 相对 prior art 有明确 delta”。
- **下一步：** 从上述 delta 中选一个，写出可证伪的最小版本；若无法在最小版本上同时给出“非平凡定理 + 可数据检验 + prior-art delta”，则 P1-only 也不成立，应转入补采数据或缩小范围的 C 级决策。

脚本汇总：
- `profile_p1_data.py` / `p1_data_profile.json`
- `spike_p1_structured_lifting.py` / `spike_p1_structured_lifting.json`
