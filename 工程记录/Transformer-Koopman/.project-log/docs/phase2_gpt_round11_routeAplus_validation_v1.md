# 阶段② 第十一轮（A+ 结构 gate）验证报告 v1

- **日期**：2026-10-06
- **验证对象**：GPT 深度重规划 `阶段②深度重规划_Aplus_ResponseStructured_HistoryConditioned_TransformerKoopman_v1.1.md`
- **验证范围**：A+ 的两个核心新论断——(1) history 主要调制**控制通道** `B(c)`（而非 `A`）；(2) "相同 state+command、不同 history → 不同响应"的 matched-state 证据
- **数据**：现有 P2（train 70×300 / val 20×300），未新增观测
- **方法**：观测空间代理——在**加法式 context 基线**上分别叠加 A-mod / B-mod / AB-mod（低秩 r=3），自洽自由 rollout H=1/5/10/20；matched-state history test

---

## 0. 结论先行

**GPT 的 A+ 结构修正被明确证实：**
1. 历史对响应的作用**主要落在控制通道 `B(c)`**，不是 `A`（B-only 在 H=20 改善 67% vs A-only 42%）；
2. "同 state+command、不同 history → 响应差异放大 **3.24×**"成立 → 强动机；
3. AB 相对 B-only 仅再改善 7.6–9.4%（灰区）→ 结构选择 B-only vs AB 需权衡。

---

## 1. A/B/AB 结构消融

模型统一形式（`φ`=4 步历史）：
- base = `d = Wx x + Wu u + Wp φ + b`（**加法式 context**）；
- A-only = base + 低秩调制 `A(φ)x`；
- B-only = base + 低秩调制 `B(φ)u`；
- AB = 两者。

自洽 rollout val RMSE：

| 模式 | H=1 | H=5 | H=10 | H=20 | vs base (H=10/H=20) |
|---|---|---|---|---|---|
| base | 0.0590 | 0.4190 | 1.0622 | 2.0140 | — |
| **A-only** | 0.0451 | 0.2392 | 0.6126 | 1.1719 | −42.3% / −41.8% |
| **B-only** | 0.0415 | 0.2196 | **0.4191** | **0.6583** | **−60.5% / −67.3%** |
| **AB** | 0.0361 | 0.1933 | 0.3798 | 0.6081 | −64.2% / −69.8% |

**B vs AB 差距**：H=1/5/10/20 = 12.8% / 12.0% / 9.4% / 7.6%。

**读数**：
- **控制通道（B）是历史依赖的主要载体**：B-only ≫ A-only。
- AB 相对 B-only 的边际收益在长 horizon 落到 7.6%（H=20）——按 GPT 门槛（"AB 稳定 >8–10% 才采用"）处于**灰区**；B-only 更简洁、与 generic 时变 Koopman 区分更清楚、MPC 更易解释。

---

## 2. Matched-state history test（GPT §13）

在 (train+val) 中随机取 20 万对样本，筛选：`‖x_i−x_j‖` 处于最小 2%、`‖u_i−u_j‖` 处于最小 5%（≈相同当前状态与指令）；再按历史距离 `‖φ_i−φ_j‖` 分成相似/不同两组，比较下一步响应差 `‖d_i−d_j‖`：

| 指标 | 值 |
|---|---|
| 近邻对数 | 199 |
| 相似 history 的响应差 | 0.0892 |
| 不同 history 的响应差 | 0.2889 |
| **比值** | **3.24** |

**判定**：相同当前位置 + 相似指令 + 不同历史 → 下一步响应差异放大 **3.24×**。这直接支撑论文核心痛点——**部分观测不仅隐藏状态，还使"控制有效性"依赖历史**；也是 §53 的 motivation figure 证据。

---

## 3. Prior-art 核实

| GPT 引用 | 核实 | 备注 |
|---|---|---|
| arXiv:2606.23957 AFT-Koopman | ✅ 真实 | 已占 dynamic re-encoding（路线 C） |
| arXiv:2505.00354 Deep Koopman MPC 软体 | ✅ 真实 | 真机占位 |
| MamKO (ICLR 2025) | ⚠️ arXiv 未检索到 | 可能在 OpenReview；合理但未独立证实 |
| CAK-SMPC / LPV-Koopman / MAKO / Adaptive Koopman / MZ-Koopman / RA-L time-delay / KAT-Koopman | ⚠️ 多为期刊 DOI | 无法经 arXiv 独立核实；但方向合理，与 GPT"不主张机制级首创"的定位一致 |

**结论**：GPT 的 prior-art 地图与"收紧到 response-structured + control-channel + 物理几何"的策略**方向正确**；headline 若写成"history-conditioned control-channel Koopman"确有辨识度（其 Title D）。

---

## 4. 待用户裁定（延续前轮）

1. **novelty 门槛**：A+ 已是工程型定位，需正式更新 **DEC-021** 解读。
2. **阶段③范围**：重采 P2 数据 + 真机闭环；与代码/论文冻结、**DEC-022** 的边界需澄清。
3. **结构选择**：B-only vs AB（本报告给出证据，倾向 **B-only**，待 GPT/用户定）。
4. **本验证为观测空间代理**：需阶段③在真实 latent pipeline 复现（GPT §16 A+-Gate 概率中风险）。

---

## 5. 初步判决

- **A+ 的两大新论断均被现有数据支持。**
- 结构推荐：**优先 B-only**（B-only≈AB 的 90%，且更简洁/更易划界）；若 AB 在真实 pipeline 上稳定 >8–10%，再切 AB。
- 下一步应按 GPT §60：在**真实 latent pipeline** 上跑 fixed/A-only/B-only/AB 结构 gate + history-shuffle + modulation-nullification + matched-state，再决定是否进入阶段③。
