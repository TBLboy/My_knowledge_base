# GPT 18 路线验证报告 v2 — L3 全文对拍 + R16 负面扫描

- 日期：2026-10-05
- 阶段：阶段②（论文理论路线重构，strict，代码/配置/论文冻结）
- 任务：TASK-004 / RUN-004
- 方法：对 GPT 路线报告（`C:\Users\12187\Downloads\Transformer_Koopman_技术路线研究报告_v0.1.md`）的 18 条路线做 **L3 全文级** prior-art 对拍，并做 R16（goal-conditioned / control-sufficient Koopman）**专项负面扫描**。
- 上游记录：`PHASE2-GPT-ROUTES-001`、`PHASE2-GPT-ROUTE-VALIDATION-001`、`PHASE2-GPT-ROUTE-VALIDATION-002`、`phase2_gpt_route_validation_v1.md`、`phase2_gpt_route_validation_addendum_r4r18_v0.1.md`、`phase2_gpt_route_tests_abc_v0.1.md`。
- 用户指令约束：本阶段**只做路线验证与反馈，不构思新路线**。

---

## 0. 执行摘要

1. **R1–R18 中，没有任何一条在 L3 全文对拍后仍可判为"新颖主结果"**。此前判为"最大残余"的 R1、R2、R16 在 L3 后全部进一步收窄：
   - **R1（多步可达）**：多步版本在本系统上对 H≥dim **平凡成立**（完全可控），H=1 版本≈标准隐空间一步一致性残差；多步 Koopman 学习已被 2601.11901、2606.02938、2405.01292 占满。
   - **R2（gauge 不变控制意义量）**：基/gauge 不变的、可作损失的 Koopman 控制精度量已由 2603.27548（CCI）建立。
   - **R16（control-sufficient Koopman）**：概念核心（observation vs control sufficiency、action sufficiency）已在 RL/VLA 2021–2026 充分建立（2507.19437、2601.22496、2110.05721、2605.24890、2605.01694）；"goal-conditioned Koopman" 精确短语 arXiv 0 命中（命名空间空，但概念不新）。
2. 结论不是"发现一条新路线"，而是**向 GPT 反馈：当前 18 条的创新空间已被 2025–2026 文献大幅占据，需在机制级而非命名级重新给出差异**。
3. 本报告不做新路线构思（遵守用户指令）。

---

## 1. 验证方法与证据强度

| 级别 | 含义 | 本报告覆盖 |
|---|---|---|
| L1 | 标题/关键词命中 | 全部 18 条 |
| L2 | 摘要/片段对拍 | 全部 18 条 |
| **L3** | **全文对拍（HTML 全文）** | R1/R4/R5/R16/R18 相关 6 篇 |
| 负面扫描 | arXiv API 精确短语查询 | R16（0 命中 Σ）+ action/control-sufficient（22 命中）|

**L3 全文已读**：
- `arXiv:2509.17010`（Singh et al., Generalized Momenta-Based Koopman）— 全文。
- `arXiv:2606.02938`（Lazar, Khatri-Rao GeKo kernel regression）— 全文。
- `arXiv:2603.27548`（Haseli–Cortés–Burdick, Control Forward-Backward Consistency）— 全文（尾部截断）。
- `arXiv:2601.11901`（Wu et al., Least-Squares Multi-Step Koopman for MPC）— 全文（尾部截断）。

**L2/L1（摘要级）**：`arXiv:2405.01292`、`arXiv:2507.19437`、`arXiv:2601.22496`、`arXiv:2605.24890`、`arXiv:2605.01694`、`arXiv:2110.05721` 等。

> 证据边界：`2606.02938/2603.27548/2601.11901` 均为 2026 年 arXiv 预印本，编号需在正式决策前二次核实（见 §7）。

---

## 2. L3 关键文献对拍

### 2.1 `arXiv:2603.27548` — Control Forward-Backward Consistency（Haseli–Cortés–Burdick）
- 为 KCF（Koopman Control Family）模型定义**控制前向-后向一致性矩阵** `M_CC = I − A_f A_b`。
- 性质：谱对**基（gauge）不变**（Prop IV.4）、特征值∈[0,1]（Prop IV.3）。
- 主定理：KCF 预测器的相对 RMSE **紧界为 `sqrt(CCI)`**，`CCI = λmax(M_CC)`；专门推广到 lifted linear / bilinear。
- 明确论述 CCI **可作优化建模的损失函数**，并给训练效率指南。
- 与 R16 直接相关：给出**控制模型专属的、基不变的精度度量**。
- **对 R2 的裁决性影响**：R2 的核心诉求"构造对基变换不变、且反映控制行为的量"已被 CCI 满足。

### 2.2 `arXiv:2601.11901` — Least-Squares Multi-Step Koopman for MPC（Wu et al., MIT/JHU）
- 直接学 condensed 多步映射 `(E,F)`（而非先学 `{A,B,C}` 再 condense），**保持凸最小二乘**。
- 识别问题可按 **prediction-horizon 与 state-coordinate 级并行分解**，支持行向 ℓ1 字典剪枝。
- 非渐近有限样本分析：单步 EDMD 误差按 `‖A‖^ℓ` **复利放大**；多步 EDMD 误差界**只依赖目标多步映射**，不复利。
- **对 R1 的裁决性影响**：R1"用多步信息改造辨识目标"的核心技术已被 2601.11901（及 2606.02938、2405.01292）占满。

### 2.3 `arXiv:2606.02938` — Khatri-Rao GeKo Kernel Regression（Lazar）
- GeKo（generalized Koopman operator，Lazar 2026, 2508.07494）：态与输入**独立 lifting**，`z_{t+1}=K(z_t ⊗ v_t)`，张量双线性。
- **time-sequenced multi-step Khatri–Rao regression**：暴露算子于沿轨迹演化的快照，显著减小复利误差 —— 与 R1/R4 完全重叠。
- kernel/input-agnostic **structured SVD reduction**，RFF 实例化，**多步 rollout 诊断指导 MPC 地平线选择**。
- 引用确认：【19】Wu et al. 2601.11901、【16】Haseli-Cortés KCF（不变性邻近）、【18】Conradie et al. 2603.15091（trustworthy Koopman）。
- **对 R5/R7 的影响**：输入独立 lifting（input-state separable）已被 GeKo 占据。

### 2.4 `arXiv:2509.17010` — Generalized Momenta-Based Koopman（Singh et al.）
- 隐式广义动量态 `x=[q; M(q)q̇]`，**因果解耦已知线性控制通道**，只学被动动力学（参数减少 N·m 与 N·m²）。
- 两种网络（actuated / unactuated 数据），线性 GESO 抗扰，线性 MPC，Franka 3 实验。
- **对 R5（actuated/unactuated 解耦）与 P1-only 打量**：R5 的机制被直接占位；P1（全观测 EL）主结构被此路线占据。

### 2.5 `arXiv:2507.19437` — BCPO（Gu, Cao, Caccamo, Hovakimyan）
- 明确区分 **observation sufficiency** 与 **control sufficiency** 及层级；context-based RL 的 ELBO 目标；双推断-控制。
- **对 R16**：control sufficiency 的形式化在 RL 侧已建立。

---

## 3. R16 专项负面扫描（arXiv API 精确短语）

| 查询 | 结果 |
|---|---|
| `all:"goal-conditioned Koopman"` | **0 命中** |
| `all:"action-sufficient" OR all:"control-sufficient"` | **22 命中** |

关键命中（R16 相关）：
- **`arXiv:2601.22496`《Action-Sufficient Goal Representations》**（2026-01，upd 2026-07）：offline GCRL；定义 **action sufficiency** 为最优动作预测所需的信息论条件；证明 **value sufficiency ⇏ action sufficiency**；actor-based 表示≈action-sufficient。**这是 R16 概念的直接占位**。
- `arXiv:2507.19437`（control sufficiency / BCPO）。
- `arXiv:2110.05721`《Action-Sufficient State Representation Learning》（ASR，2021）。
- `arXiv:2605.24890`《QuoVLA: Quotient Space for VLA》——**商空间/action-sufficient 压缩**（命中"quotient"类思路）。
- `arXiv:2605.01694`《Latent State Design for World Models under Sufficiency Constraints》——predictive vs control sufficiency 的 taxonomy。
- `arXiv:2606.09858`《Support sufficiency as action-sufficient compression》——按策略等价的商。

**R16 裁决**：概念空间（goal/action/control sufficiency、商空间压缩）已在 RL/VLA 侧充分建立；命名"goal-conditioned Koopman"未被占用（命名空间空）。**残余仅为 Koopman 专属控制充分性**（最近的 Koopman 侧证据是 2603.27548 CCI / 2603.15091 / KCF 不变性邻近），空间显著小于此前估计。

---

## 4. 逐路线裁决（更新版）

> 图例：**换名**=机制被已有工作覆盖；**降级**=创新空间收窄；**部分可行**=需附加定理/机制才可能成立；**高危**=与已知结果为同一定理。

| 路线 | 原判 | L3/R16 后 | 主要占位/依据 |
|---|---|---|---|
| R1 | 最大残余 | **降级（多步版本平凡）** | 2601.11901、2606.02938、2405.01292、Korda–Mezić；本系统完全可控 → H≥dim 缺陷=0 |
| R2 | 高危 | **不可行（作主结果）** | 2603.27548 CCI（基不变）、1984 Majumdar、2603.15091 |
| R3 | 部分可行 | **部分可行（需控制定理）** | 残差结构化（Test C）；须避开 2509.17010 |
| R4 | 换名 | **换名坐实** | 2606.02938、2405.01292 |
| R5 | 部分换名 | **换名坐实** | 2509.17010（解耦 + 只学被动） |
| R6 | 换名 | 换名 | 1709.08712；ICLR2026 Gramian |
| R7 | 部分换名 | 部分换名 | GeKo 输入 lifting |
| R9 | 换名 | 换名（经典） | 有限时域可观 Gramian |
| R10 | 换名 | 换名 | 2607.05718 |
| R13 | 换名 | 换名 | Ho-Kalman/ERA；2602.14537 |
| R14 | 部分换名 | 部分换名 | 输入变换类 |
| R15 | 换名 | **换名（概念侧）** | 2601.22496、2605.24890 quotient |
| R16 | 最大残余 | **残余收窄（Koopman 专属）** | 2507.19437、2601.22496、2110.05721、2603.27548 |
| R18 | 部分换名 | **换名坐实** | 2311.13033 不变性邻近；2603.27548 |
| R17 | 叙事 | 叙事 | — |

---

## 5. 组合方案评估

- **A（R1+R15+R18）**：混合。R1 多步版本平凡、R15/R18 概念被占 → 不建议。
- **B（R2+R9+R4）**：R2 不可行 + R9/R4 换名 → 不建议。
- **C（R3+R12+R18）**：最贴合 P1（全观测 EL）；R3 残差结构化 + R18 不变性邻近；仍需 P1 控制定理 → **残余最高但仍不足**。
- **D（R4+R13+R2）**：三重换名 → 不建议。

---

## 6. 给 GPT 的反馈意见（只反馈，不构思新路线）

1. **R1/R2/R4/R5/R6/R9/R10/R13/R15/R18 应降级或换名**，并给出机制级占位文献（见 §2、§4）。
2. **R16 是唯一仍有概念空间的路线**，但必须明确区分于：RL 侧 action/control sufficiency（2507.19437、2601.22496）与 Koopman 侧 CCI（2603.27548）。"goal-conditioned Koopman" 命名可用，但概念不新。
3. **R3** 需给出 P1 上的控制定理，且明确区别于 2509.17010 的动量路线。
4. **下次输出建议**：对每条候选路线给出"与已知 2026 工作的**机制级**差异（差在哪个可证命题/哪条假设）"，而非仅给名称与直觉。
5. **三项便宜测试复核**仍有效：Test A（gauge 病理）成立但 CCI 已使其非新颖；Test B（一阶不可达 16–21%）成立但多步后衰减；Test C（P1 残差 AR 可预测 17–25%）成立但需定理。

---

## 7. 证据与不确定性

**已核实（L3 全文）**：2509.17010、2606.02938、2603.27548、2601.11901。
**摘要级未核实**：2405.01292、2507.19437、2601.22496、2605.24890、2605.01694、2110.05721。
**未做 L3 的决策闸门**：ICLR2026-10007892、2603.17545、2607.05718、2602.14537、2311.13033、2307.15368、1709.08712、2209.08637、2402.03145。
**风险**：2026 arXiv 编号（2606.*、2603.*、2601.*）需二次核实；`2606.02938`/`2603.27548` 全文尾部被截断，个别细节未逐字确认。
**未验证项**：无任何路线被证明可作阶段② 主结果；DEC-018 未满足；GOAL-001 门禁仍拒绝完成。
