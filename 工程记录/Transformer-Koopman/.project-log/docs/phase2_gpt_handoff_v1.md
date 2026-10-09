# 阶段② 路线验证反馈（完整版）——提交外部构思方 GPT

- 文件性质：自包含反馈报告，用于回传给外部路线构思方 GPT，作为其产出下一轮候选路线的依据。
- 来源：对上一轮《Transformer_Koopman_技术路线研究报告_v0.1.md》中 18 条路线（R1–R18）与 4 个组合的独立验证结果。
- 日期：2026-10-05
- 证据等级：L1（检索）/L2（摘要）/L3（全文对拍），逐条标注。
- 配套详版：`phase2_gpt_route_validation_v2_l3.md`（本文件是其超集与最终版）。

---

## 0. 任务背景与硬约束（供构思方对齐）

**工作对象（两套真实机器人数据）**
- **P1**：3-DOF 刚性机械臂。全观测 Euler–Lagrange 系统；状态 `x=[q1,dq1,q2,dq2,q3,dq3]`（6 维），输入为**关节力矩/电流指令**（3 维）；采样 250 Hz（dt=0.004 s）；关节 2 存在重力偏置（|力矩| 均值≈3.11）；速度与数值差分相对误差 6.8/11.3/16.2%。
- **P2**：4 绳欠驱动软体连续体平台。二维轻点状态 `x∈R²`，二维速度指令 `u∈R²`；差分映射 `(R,L,D,U)=(+dx,−dx,−dy,+dy)`，`Ts≈0.2 s`，`|u_max|=300` 步；**共模从未被驱动**；无张力/绳长/速度/模态可测。

**目标**：论文需要**建模与控制器同时**具有真正新意的 Koopman（或算子理论）路线，且保留与 Koopman/算子理论的联系；随后进入实现（阶段③）。

**"新颖闸门"（全部满足才算新路线）**
1. lifting 的参数化/辨识目标发生**结构性改变**（不能只是 history Transformer + 常值 (A,B)）；
2. 控制器结构发生**结构性改变**（不能只是 B† + 固定 LQR）；
3. 有 P1 与 P2 的真实物理锚点；
4. 有**可检验的新定理**；
5. 有**方法/定理级**（非元数据级）的先前工作比对；
6. 可在现有数据上实现，或明确标注为数据缺口。

**禁止的伪创新**：改损失权重；加注意力；延迟状态；泛化 CBF/tube/自适应/MPC；通用切换/量化/分层/输入变换包装；仅修补证明；把未测的张力/模态/能量当已知。

**本轮约束（委托方要求）**：验证方**只做路线验证与反馈，不构思新路线**。新路线由构思方（GPT）产出。

---

## 1. 验证方法与证据等级

| 级别 | 含义 | 覆盖 |
|---|---|---|
| L1 | 标题/关键词命中 | R1–R18 全覆盖 |
| L2 | 摘要/详细摘要对拍 | 全部关键引用 |
| L3 | **全文对拍** | 6 篇（见下） |
| 负面扫描 | arXiv API 精确短语查询 | R16 |

**L3 全文已读**：`arXiv:2509.17010`、`arXiv:2606.02938`、`arXiv:2603.27548`、`arXiv:2601.11901`、`arXiv:2601.22496`、（`arXiv:2606.02938` 尾部截断）。
**L2 详细摘要**：`2405.01292`、`2507.19437`、`2311.13033`、`2307.15368`、`2603.15091`、`2602.14537`、`2607.05718`、`2402.03145`、`2209.08637`、`2603.17545`、`1709.08712`、`2110.05721`、`2605.24890`、`2605.01694`、`2606.09858`、`2606.08431`。
**未证实**：早前线索中的 "ICLR 2026 Koopman controllability Gramian" 未能在 arXiv 找到对应条目（相关经典工作为 `1709.08712`，最近邻为 `2606.08431`）。

---

## 2. 便宜测试复现数据（现有数据/部署 checkpoint 上）

### Test A — R2 前提：gauge / 基变换
- 物理预测对基变换**不变**（残差 1.5e-13）。
- **固定** `Q=diag(Qx,αI)` 的 LQR 控制/闭环**随基变化**：
  - cond(T)=1e2 → 跟踪相对差 0.66–0.83；
  - cond(T)=1e4 → 1.3–2.8；
  - cond(T)=1e6 → DARE 3/4 失败。
- **判读**：现象成立；但固定 Q 的 LQR 协变不变性属 **1984 已知**，R2 把它当新问题不成立。

### Test B — R1 前提：一阶参考增量不可达（P2）
- 相对缺陷 median **0.167/0.162**、mean **0.216/0.213**（train/val）→ 约 16–21% 的 lifted 参考增量落在 `im(B)` 外。

### Test B′ — R1 多步可达（P2）
| H | train mean rel | train median rel | val mean rel |
|---|---|---|---|
| 1 | 0.216 | 0.167 | 0.213 |
| 2 | 0.0909 | 0.0706 | 0.0895 |
| 3 | 0.0326 | 0.0254 | 0.0311 |
| 4 | 0.00385 | 0.00247 | 0.00374 |
| 6 | ~1.9e-16 | ~1.9e-16 | ~1.9e-16 |
| 10 | ~1.8e-16 | ~1.8e-16 | ~1.8e-16 |
- **关键**：P2 部署模型可控秩 **10/10**（完全可控），多步可达子空间在 H≥dim 后张满全空间 → 缺陷**平凡趋于 0**；H=1 时 `R_H=im(B)`，该缺陷≈**标准隐空间一步一致性残差**，非结构性新发现。

### Test C — R3 前提：P1 残差可预测性
- 相对白噪声，AR(1) 改善 **24.3/19.4/17.0%**（关节 1/2/3），AR(4) 24.5/20.5/18.6%；ACF 慢衰减（lag-5 0.11–0.29）。
- **判读**：残差**结构化、可预测**（与 R16 文本所述"unmodeled dynamics, not noise"一致），但需配套控制定理。

---

## 3. 逐路线机制级占位（L1/L2/L3）

> 判定：**换名** = 机制/定理被已有工作覆盖；**降级** = 创新空间显著收窄；**部分可行** = 需附加机制/定理方可成立。

| 路线 | 判定 | 机制级占位（关键文献） |
|---|---|---|
| **R1** 参考可达/不可达作为表示学习损失 | **降级（多步版本对本系统平凡）** | `2601.11901`（Wu et al.）多步 EDMD 直学 condensed (E,F)，**凸最小二乘**、按 horizon/state 并行、ℓ1 剪枝；证明单步误差按 `‖A‖^ℓ` 复利、多步有界。`2606.02938`（Lazar）time-sequenced 多步 Khatri-Rao 回归。`2405.01292`（de Jong et al.）多步输出预测误差学习 observables + terminal set + ISS 正则。Korda–Mezić Automatica 2018 |
| **R2** 基/gauge 不变的"控制意义"度量 | **不可行（作主结果）** | `2603.27548`（Haseli–Cortés–Burdick）：控制前向-后向一致性矩阵 `M_CC=I−A_f A_b`，**谱对基不变（Prop IV.4）**、特征值∈[0,1]，主定理给出 KCF 预测器 RRMSE 的**紧界 `sqrt(CCI)`**，专门推广到 lifted linear/bilinear，并给出**作为损失**的用法。另见 `2603.15091`（主角度分解 PAD）、`2311.13033`、`2603.17545`（数据驱动 ν-gap）、1984 Majumdar |
| **R3** 结构化残差 + 控制 | 部分可行（需控制定理） | 残差结构化（Test C）；须与 `2509.17010` 的物理动量路线区分 |
| **R4** Koopman-SPC | **换名坐实** | `2606.02938`、`2405.01292` |
| **R5** actuated/unactuated 解耦、只学被动 | **换名坐实** | `2509.17010`（Singh et al.）：隐式广义动量态 `x=[q; M(q)q̇]`，因果解耦已知线性控制通道，只学被动动力学，参数减少 N·m 与 N·m²，线性 GESO + 线性 MPC + Franka 3 实验 |
| **R6** 可控/可观 Gramian 正则 | 换名 | `1709.08712`（Yeung，Koopman Gramians + balanced truncation）；`2606.08431`（neural ODE 控制论视角 Gramian） |
| **R7** 输入 lifting | 部分换名 | `2606.02938` GeKo 输入独立 lifting（input-state separable） |
| **R9** | 换名（经典） | 有限时域可观 Gramian |
| **R10** 输入-Jacobian / 收缩正则 | 换名 | `2607.05718`（ICNDM：输入收缩 + ISS） |
| **R13** 子空间辨识 / 精确线性嵌入 | 换名 | Ho-Kalman/ERA；`2602.14537`（Shang–Haseli–Cortés–Zheng：**精确 Koopman 线性嵌入 ⇔ CAP 结构**，给出存在性充要条件与符号判别） |
| **R14** 输入变换 | 部分换名 | GeKo / input lifting 类 |
| **R15** GCRL 双编码 | **换名（概念侧）** | `2601.22496`（Action-Sufficient Goal Representations）；`2605.24890`（QuoVLA 商空间） |
| **R16** control-sufficient Koopman | **残余收窄** | `2507.19437`（BCPO，observation vs control sufficiency）；`2601.22496`（action sufficiency 信息论条件，value suff ⇏ action suff）；`2110.05721`（ASR）；`2605.24890`；`2605.01694`（sufficiency taxonomy）；`2209.08637`（控制感知 Koopman 嵌入精化）；Koopman 侧最近为 `2603.27548` CCI、`2603.15091`、Haseli–Cortés KCF 不变性邻近 |
| **R18** 不变性邻近 | **换名坐实** | `2311.13033`（invariance proximity 闭式，Jordan 主角度）；`2307.15368`（KCF 通用形式 + subspace invariance proximity）；`2603.27548` |
| **R17** | 叙事 | — |

**补充关键结果（新）**
- `2603.15091`（Conradie–Boullé–Loiseau–Brunton–Colbrook，Trustworthy Koopman）：用**主角度**量化不变性，提出 **principal angle decomposition (PAD)** 作为**动态信息驱动的 SVD 截断替代**，给多步误差界、字典/核精化、GP 误差代理。——同时命中 **R1（表示精化）** 与 **R2/R18（子空间不变性度量）**。
- `2602.14537`：**精确有限维 Koopman 线性嵌入存在 ⇔ CAP（control-affine preserved）结构**；把非线性隔离到自治子系统，并证明该子系统需有足够丰富的 Koopman 不变子空间；给出符号判别流程。→ 对任何声称"精确线性表示"的路线构成理论约束。
- `2209.08637`（Uchida–Duraisamy）：**控制感知**地精化已训 Koopman 模型以改善闭环行为（保状态预测精度的同时改残差）。→ 命中 R16 与"控制感知 lifting"。
- `2603.17545`：**数据驱动、免辨识**估计 Vinnicombe ν-gap。→ 命中"控制相关模型失配度量"（R2 的替代占位）。

---

## 4. R16 专项负面扫描（arXiv API 精确短语）

| 查询 | 命中 |
|---|---|
| `all:"goal-conditioned Koopman"` | **0** |
| `all:"action-sufficient" OR all:"control-sufficient"` | **22** |

**直接命中**：`2601.22496`（action sufficiency 信息论定义；证明 value sufficiency ⇏ action sufficiency；actor-based 表示≈action-sufficient）。
**其他命中**：`2507.19437`、`2110.05721`、`2605.24890`、`2605.01694`、`2606.09858`。

**含义**：R16 的概念核心（goal/action/control sufficiency、商空间压缩）已在 RL/VLA 侧充分建立；`goal-conditioned Koopman` 仅**命名**未被占用。若继续 R16，必须给出 **Koopman/算子理论专属**的可证命题，而非把 RL 侧 sufficiency 换名词搬过来。

---

## 5. 组合方案评估

- **A（R1+R15+R18）**：混合。R1 多步版本对本系统平凡、R15/R18 概念被占 → 不建议。
- **B（R2+R9+R4）**：R2 不可行 + R9/R4 换名 → 不建议。
- **C（R3+R12+R18）**：最贴 P1（全观测 EL）；R3 残差结构化 + R18 不变性邻近；仍需 P1 控制定理 → **残余最高但仍不足**。
- **D（R4+R13+R2）**：三重换名 → 不建议。

---

## 6. 残余空间排序（更新）

**结论**：18 条路线经 L3 后**无任何一条可作阶段② 主结果**。残余空间排序：

> **R16（Koopman 专属控制充分性）> R3（P1 残差 + 控制定理）> 其余（换名/降级）**

两者都必须由构思方给出**机制级重述**才可能成立。

---

## 7. 对下一轮构思的具体要求（关键）

1. **逐条给出机制级差异**：不是路线名称或直觉，而是"与已占位工作相比，差在**哪条可证命题/哪条假设**"。
2. **对 R1/R2/R4/R5/R6/R9/R10/R13/R15/R18**：若保留，须说明如何**绕开已占位的机制**（非改名字/换数据集）。
3. **对 R16**：须给出 Koopman/算子理论**专属**的控制充分性判据与定理，并明确区别于 `2507.19437`、`2601.22496`、`2603.27548`、`2209.08637`。
4. **对 R3**：给出 P1 上可证的控制定理，并明确区别于 `2509.17010`。
5. **物理锚点**：每条候选路线需说明在 **P1 / P2** 上"改变的是哪个可观测、哪个可证界、哪种控制结构"。
6. **可检验性**：给出**廉价证伪实验**（能在现有数据/checkpoint 上跑，并给出预期观测量）。
7. **承认平凡风险**：若某路线在完全可控系统（如 P2 秩 10/10）上会平凡成立，请提前声明。
8. **存在性约束**：任何"精确线性表示"主张须与 `2602.14537`（CAP 结构充要条件）自洽。

---

## 8. 证据附录（引用清单与等级）

**L3 全文**
- `arXiv:2509.17010` — Generalized Momenta-Based Koopman Formalism（Singh et al.）
- `arXiv:2606.02938` — Koopman operator learning for predictive control via Khatri-Rao kernel regression（Lazar）
- `arXiv:2603.27548` — Control Forward-Backward Consistency: Quantifying the Accuracy of KCF Models（Haseli, Cortés, Burdick）
- `arXiv:2601.11901` — A Least-Squares Multi-Step Koopman Operator for MPC（Wu, Tan, Zhou, Braatz, Drgoňa）
- `arXiv:2601.22496` — Action-Sufficient Goal Representations（Hyeon et al.）

**L2 详细摘要**
- `arXiv:2405.01292` de Jong et al.（Koopman DPC, robust stability + recursive feasibility）
- `arXiv:2507.19437` Gu et al.（BCPO, control sufficiency）
- `arXiv:2311.13033` Haseli–Cortés（Invariance Proximity 闭式）
- `arXiv:2307.15368` Haseli–Cortés（KCF universal forms + subspace invariance proximity）
- `arXiv:2603.15091` Conradie et al.（Trustworthy Koopman, PAD）
- `arXiv:2602.14537` Shang–Haseli–Cortés–Zheng（Koopman linear embedding existence ⇔ CAP）
- `arXiv:2607.05718` Pouladi（ICNDM, input-contraction）
- `arXiv:2402.03145` Strässer et al.（SafEDMD, Automatica 2026）
- `arXiv:2209.08637` Uchida–Duraisamy（control-aware Koopman embedding）
- `arXiv:2603.17545` Guerrero–Sandberg–Rojas（data-driven Vinnicombe metric）
- `arXiv:1709.08712` Yeung et al.（Koopman Gramians）
- `arXiv:2110.05721` Huang et al.（Action-Sufficient State Representation）
- `arXiv:2605.24890` QuoVLA（quotient space）
- `arXiv:2605.01694` Latent State Design under Sufficiency Constraints
- `arXiv:2606.09858` Support sufficiency as action-sufficient compression
- `arXiv:2606.08431` Control-Theoretic View of Neural ODEs (empirical controllability/observability)
- Korda & Mezić, Automatica 93:149–160, 2018（线性预测器 / Koopman-MPC）

---

## 9. 不确定性与边界

- 2026 年 arXiv 编号需在正式决策前二次核实；`2606.02938`/`2603.27548` 全文尾部截断，个别细节未逐字确认。
- 部分条目为 L2（详细摘要）而非全文逐字。
- 早前线索中的 "ICLR 2026 Gramian" 未能定位到 arXiv 条目。
- **未验证项**：无任何路线被证明可作阶段② 主结果；DEC-018（P2 模型稳定化）未满足；GOAL-001 门禁拒绝完成。
- 代码/配置/论文在本阶段保持**冻结**。
