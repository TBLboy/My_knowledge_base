# 阶段② 第十轮（路线 A 核心 gate）验证报告 v1

- **日期**：2026-10-06
- **验证对象**：GPT 第十轮报告 `第十轮自动科研路线重构_务实创新_TransformerKoopman_ResponseCorrectedMPC_v1.0.md`，路线 A = **History-Conditioned Low-Rank Koopman + Response-Corrected MPC (HC-LRK-RCMPC)**
- **验证范围**：路线 A 自设的 **A-Gate 1（建模）**——"Transformer history 除构造 `z_k` 外，能否有效预测当前该用哪个 Koopman operator"
- **数据**：现有 P2 数据（train 70×300 / val 20×300），**未新增观测**
- **方法**：观测空间代理——比较 `d=f(u,x)`（noctx） / `d=f(u,x,φ)`（加法 context） / `d=J(φ)u+W[x;φ]+b`（低秩算子调制，路线 A），自洽自由 rollout

---

## 0. 结论先行

**路线 A 的核心建模假设在现有数据上被明确支持（A-Gate 1 大幅通过）。**
1. history/context 携带大量多步预测信息；
2. **低秩算子调制**优于加法式 context，且优势随 horizon 增大——这正是路线 A 想要区分的机制。

但需同时注意三个非技术问题（见 §4）：novelty 门槛被主动下调、需要重采数据 + P2 真机闭环（阶段③）、以及此为观测空间代理而非完整 latent pipeline。

---

## 1. 实验设置

- 状态 `x∈R²`，输入 `u∈R²`，响应 `d=x_{k+1}-x_k`。
- context `φ = [x_{k-3..k}, u_{k-3..k-1}]`（L=4 历史）。
- 三个模型：
  - **noctx**：`d = Θ[u;x]+b`（固定算子，含当前状态，无历史）；
  - **add**：`d = Θ[u;x;φ]+b`（加法式 context）；
  - **mult（路线 A）**：`d = (J0 + U diag(g(φ)) Vᵀ) u + W[x;φ] + b`，秩 r=3，`g` 为 2 层 MLP。
- 自洽自由 rollout：每一步用预测状态重建 context，H=1/5/10/20，比较轨迹位置 RMSE。

---

## 2. 结果

**一步 val RMSE**：noctx 0.1168 / add 0.0365 / mult 0.0271。

**自洽 rollout val RMSE**：

| H | noctx | add | **mult** | mult vs noctx | mult vs add |
|---|---|---|---|---|---|
| 1 | 0.1647 | 0.0514 | **0.0346** | **−79.0%** | −32.5% |
| 5 | 0.5048 | 0.2848 | **0.1799** | **−64.4%** | −36.8% |
| 10 | 0.6972 | 0.7605 | **0.3691** | **−47.1%** | −51.5% |
| 20 | 0.9820 | 1.4706 | **0.6051** | **−38.4%** | −58.9% |

**判定**：
- **context 有用**：noctx→mult 在 H=1 降 79%、H=20 仍降 38%。
- **算子调制（乘法）> 加法式 context**：mult vs add 33%→59%，且随 horizon 增大；加法式在 H≥10 开环发散，调制式全程稳定、单调收敛。
- **A-Gate 1 门槛（10–15%）大幅通过。**

---

## 3. Prior-art 抽查（L1）

| GPT 引用 | 核实 | 结论 |
|---|---|---|
| arXiv:2606.23957（AFT-Koopman） | 真实 | 已做 latent memory + dynamic re-encoding（**路线 C 核心被占**），但对象为 Duffing/Repressilator/IRMA 基准，非机器人 |
| arXiv:2505.00354（Deep Koopman MPC 软体机器人） | 真实 | "Deep Koopman + MPC + 软体机器人真机"确已占位 |

GPT 的文献图（LPV-Koopman / context-aware Koopman / mixture Koopman / 残差 Koopman / MZ-Koopman / time-delay Koopman）与其"不主张纯理论新颖、只做工程型组合"的定位**一致**。路线 A 的差异点（history Transformer context + **低秩**算子调制 + response-corrected MPC + 软体机器人）在 二区/三区工程论文层面可辩护；作为机制级原创则不强。

---

## 4. 需要注意的非技术问题（需用户裁定）

1. **novelty 门槛被主动下调**：第十轮明确"不再追求机制级原创"，与 **DEC-021（控制器设计创新为首要）**的严格读法冲突。若接受此重新定位，DEC-021 的解读需更新。
2. **需要重采数据 + P2 真机闭环**：路线 A/§17–§20 依赖重新采集 P2 数据与真机跟踪实验（属**阶段③**）。这与"代码/论文冻结"及 **DEC-022（禁止新增观测）**的边界需澄清——重采**相同观测**、以及真机闭环，是否为用户允许。**新增的是实验而非传感器**，但仍是显著的范围变化。
3. **本验证为观测空间代理**：非完整 latent Transformer-Koopman pipeline。结论需在阶段③用真实 pipeline 复现。
4. **控制器部分**：路线 A 的 response corrector `δu=α S0 ê^d` 正是已验证的常数增益响应反馈——与本项目 Z0（常数增益 minimax 最优）自洽，故控制器侧风险低、可辩护。

---

## 5. 初步判决

- **技术 gate：路线 A 通过（强证据）。**
- **可发表性：二区/三区工程论文可行**（建模改进清楚 + 控制结构变化 + P2 真机 + 简易 practical 理论）。
- **是否推进：取决于用户对"下调 novelty 目标 + 进入阶段③真机/重采数据"的拍板**（C 级）。
