# GPT 第二轮路线（N1–N6）验证报告 v1

- 日期：2026-10-05
- 阶段：阶段②（strict；代码/配置/论文冻结）
- 任务：TASK-004 / RUN-004
- 对象：GPT 第二轮报告《从预测等价到控制等价的 Koopman 表示》中的 N1–N6 + 4 个平台映射组合。
- 方法：L1/L2/L3 prior-art 对拍 + arXiv API 负面扫描 + 廉价证伪实验（P2 policy-null 投影、P1 残差控制敏感性）。
- 用户约束：只验证 + 反馈，不构思新路线。

---

## 0. 一句话结论

N1–N6 的**概念核心（policy/control equivalence、policy-null quotient、weaker-than-exact linearization、control-relevant residual、closed-loop linearization）在控制理论与 RL/算子理论中均已有对应机制**；本轮实验给出两条硬数据：(a) P2 上"不可达缺陷"约 **97% 是 policy-null**（支持 N1 的再定位，但归因于经典闭环降维）；(b) P1 上残差 **100% 在 im(B)**，N4 的 `r=r_c+r_n` 拆分退化。**无路线可作主结果**。

---

## 1. Prior-art 机制级对拍（L1/L2）

| N 路线 | 判定 | 机制级占位 |
|---|---|---|
| **N1** Policy-Equivalent Approximate Koopman（policy-null defect；`Δu=Γ_Hδ`） | **部分可行，概念被占** | `2603.27677`（Kounatidis–Malikopoulos）：证明"**保留控制相关 Hamiltonian 结构而非辨识完整动力学即可恢复最优性**"，并给出 **constrained model-plant control equivalence** 条件。`2209.08645`（Kramer et al.）：**closed-loop balanced truncation**（开/闭环可控/可观能量函数，经典闭环降维）。`2209.08637`（Uchida–Duraisamy）：**control-aware Koopman** 精化闭环行为 |
| **N2** Riccati Quotient（`Z/∼_π`，`N_π=Ker(K)`，`N_{π,H}=∩_t Ker(K_tΦ_t)`） | **换名（bisimulation / 闭环降维）+ 平凡化风险** | `2606.09858`（Walsh）："最粗的 action-sufficient 压缩 = **按 policy equivalence 对 support space 取商**；两状态可合并当且仅当最优动作相同"。`2509.19266`（Stamouli et al.）：**bisimulation 函数**用于 LQR 闭环，界 cost gradient 距离。RL 侧 **bisimulation / state aggregation / behavioral equivalence** 为成熟领域；控制侧对应 **closed-loop balanced reduction**（Enns 1984；Mustafa–Glover 1990） |
| **N3** Policy-Neutral CAP Violation（`ε_PCAP=‖Π_πδ‖`；`Exact ⊊ PolicyLinearizable`） | **部分可行，需与反馈线性化区分** | `2602.14537`（Shang–Haseli–Cortés–Zheng）：精确 Koopman 嵌入 ⇔ **CAP 结构**。`2210.05046`（Gadginmath et al.）：**反馈线性化弱于精确线性化**（involutive 条件下 Koopman generator 有限维局部幂零）。`2211.07112`（Zhang–Li）：Koopman **feedback linearization**"**绕开经典反馈线性化的可控性要求**" |
| **N4** Policy-Relevant Residual（`r=r_c+r_n`） | **在 P1 上退化** | 控制相关模型降维（`2209.08645`、`2209.08637`）。实验：P1 残差 **100% 在 im(B)** → `r_n≈0`（见 §2） |
| **N5** CAP Obstruction Rank（输入曲率 `C_H=∇_U²F_H`，`rank(C_H)=r≪n`） | **部分可行，未验证** | 经典"非线性度/曲率秩"度量；`2602.14537` 的 CAP 符号判别。P1/P2 上 `rank(C_H)` 尚未测量 |
| **N6** Closed-loop Koopman Policy Embedding（只要求 `z^+=K_πz` 闭环线性） | **换名（Koopman 反馈线性化已被占）** | `2211.07112`（Koopman bilinearization / feedback linearization）、`2210.05046`（data-driven Koopman-generator feedback linearization）、`2504.11959`（Deutscher–Enderes：**闭式闭环 Koopman 特征函数 ↔ 反馈线性化**）、`2604.01730`（Koopman feedback linearization controller 应用） |

**负面扫描**（arXiv API）：
- `all:"policy-equivalent" OR all:"control-equivalent"`：30 命中（多为无关领域；相关：`2603.27677`、`2606.09487`、`2606.23828`）。
- `all:"bisimulation" AND all:"optimal control"`：2 命中（`2509.19266` LQR bisimulation；`2103.14264`）。
- `all:"closed-loop model reduction" OR all:"closed-loop balancing"`：1 命中（`2209.07645`）——但经典文献（Enns、Mustafa–Glover）为其奠基。
- `all:"feedback linearization" AND all:"Koopman"`：6 命中（`2211.07112`、`2210.05046`、`2504.11959`、`2604.01730` 等）。

---

## 2. 廉价证伪实验

### 2.1 P2 — policy-null 子空间与缺陷投影（检验 N1/N2）
部署模型：latent n=10，input m=2。LQR(Q=I,R=I) → K 秩 **2**，**policy-null 维数 = 8**；σ(K)=[61678, 9215]。

| 指标 | train | val |
|---|---|---|
| 可达缺陷能量占比 **policy-relevant (row K)** | mean 0.0267 / median 0.0157 | mean 0.0255 / median 0.0153 |
| 可达缺陷能量占比 **policy-null (ker K)** | mean **0.973** / median **0.984** | mean **0.974** / median **0.985** |
| 缺陷控制敏感度 `‖Kδ‖/(σmax‖δ‖)` | mean 0.020 / median 0.0147 | mean 0.020 / median 0.0144 |

**时间不变性检验**（缺陷经 `A^t`（开环）与 `(A−BK)^t`（闭环）传播后的控制敏感度）：

| t | 开环 `A^t`（mean） | 闭环 `(A−BK)^t`（mean） |
|---|---|---|
| 0 | 0.104 | 0.104 |
| 1 | 0.268 | 0.083 |
| 2 | 0.624 | 0.095 |
| 3 | **1.309** | 0.058 |
| 4 | 2.508 | 0.033 |
| 5 | 4.301 | 0.011 |

**判读**：
1. **一步病灶**：P2 的不可达缺陷约 **97% 落在 ker(K)**，即对静态 LQR 几乎"不可见" → `prediction error ≠ 0` 但 `policy defect ≈ 0`（支持 N1 的再定位）。
2. **但 `ker(K)` 不是 A-不变的**：开环传播到 t=3 时敏感度已 >1 → **一步 policy-null ≠ 轨迹 policy-null**，N2 的 `N_{π,H}=∩_t Ker(K_tΦ_t)` 是必需的（否则平凡错误）。
3. **闭环下有界/衰减**：因为闭环稳定（ρ≈0.99996）。这说明"闭环等价"更像**稳定性/反馈掩盖**的产物，而非表示本身的性质 → N1 的 `Γ_H` 必须显式含闭环。

### 2.2 P1 — 残差控制敏感性（检验 N4）
辨识 LTI（train LS）：ρ(A)=0.9855，rank(B)=3（完全驱动）。

| 指标 | 值 |
|---|---|
| 位置维残差能量（dim 0/2/4 合计） | 5.03e-6（≈0） |
| 速度维残差能量（dim 1/3/5 合计） | **0.3145（全部）** |
| 残差能量落在 **im(B)** 的比例 | mean/median/p95 = **1.000** |
| 残差能量正交于 B 的比例 | ~1e-16 |
| 残差对 LQR K 的控制敏感度 | mean 0.573 |

**判读**：P1 完全驱动且运动学精确 → 位置残差≈0，全部残差落在速度/加速度方向，而 `im(B)` 恰为该子空间 → **`r_n≈0`，N4 的 `r=r_c+r_n` 拆分在 P1 上退化为 `r_c=r`**。N4 在 P1 上无可用结构。

---

## 3. 平台映射组合评估

- **P1 推荐 N4+N2**：N4 在 P1 退化（残差全为控制相关）；N2 的 policy-null 维数=3，但一步 ker(K) 非轨迹不变 → **不建议**，除非改为轨迹级 bisimulation（会趋于平凡）。
- **P2 推荐 N1+N2**：N1 得 97% policy-null 的量化支持；N2 的 policy-null 维数=8，但必须用**闭环/多步**定义，且本质是经典闭环降维 → **可作可复现的实证贡献，但非新理论**。

---

## 4. 残余与建议（只反馈，不构思）

1. **N1 是 N 系列中无法被单一文献完全覆盖的一条**，但其"控制等价"核心已由 `2603.27677`（Hamiltonian 结构保持的最优性）与经典闭环降维奠基；若保留，须给出**Koopman 专属的 Γ_H 与可证定量界**。
2. **N2 必须升级为轨迹级（bisimulation）商空间**，否则对静态反馈是 `Z/ker K ≅ R^m` 的平凡事实；且须说明与 closed-loop balanced reduction 的机制差异。
3. **N3** 有理论空间（`Exact ⊊ PolicyLinearizable`），但必须与反馈线性化理论（`2210.05046`、`2211.07112`）划清边界。
4. **N4 在 P1 退化**；若保留需换系统或换残差定义。
5. **N5 未验证**：需先测 P1/P2 的 `rank(C_H)`。
6. **N6 已被 Koopman 反馈线性化占满**。
7. 下一轮仍须**逐条给机制级差异（可证命题/假设）**。

---

## 5. 证据等级与不确定性

- L2（详细摘要）：`2603.27677`、`2606.09858`、`2509.19266`、`2209.07645`、`2209.08637`、`2602.14537`、`2210.05046`、`2211.07112`、`2504.11959`、`2604.01730`。
- 实验为**廉价证伪**（现有数据/checkpoint），非正式验收；P1 的 (A,B) 为 LS 辨识，受速度数值差分误差（6.8–16.2%）影响。
- 2026 年 arXiv 编号需二次核实。
- 未验证项：N5 的 `rank(C_H)`；N3 的具体定理；无路线被证明可作阶段② 主结果；DEC-018 未满足；GOAL-001 门禁拒绝完成。
