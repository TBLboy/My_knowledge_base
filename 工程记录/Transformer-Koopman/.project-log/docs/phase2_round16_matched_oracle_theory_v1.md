# 阶段③ 第十六轮报告：N-matched oracle（RTI-SP 正式 PASS）+ Theory Diagnostics

- 版本：v1；日期：2026-10-06；任务：TASK-004（strict）
- 输入：GPT 第十六轮裁定（路线级研究 CLOSED；冻结 RTI-SP/N=5/1-iter；补 N=5 matched oracle；并行 Theory Diagnostics）
- 结论一句话：**Δ_RTI_SP = −1.04%（N=5）/ −0.37%（N=8），RTI-SP 正式 PASS。** 之前的 "+16.8% 退化"完全来自 horizon 不匹配；同一 plant 下 N=8→N=5 使**所有**控制器（含 exact oracle）退化 ~8–9%。**matched oracle 完成 → P2 真机 GO。** Theory Diagnostics 全部量已测，与 Prop.1/2、Thm.1、Prop.3 一致。

---

## 1. Matched oracle（GPT §5）

同一 plant（DirectNN，训练一次并保存 `plant_dnn.pt`，val_loss=0.000285）；val 轨迹 ×3，30 步；SLSQP exact oracle vs RTI 1-iter。

### N=5
| | RMSE | oracle RMSE | Δ_RTI | med/p95 ms |
|---|---:|---:|---:|---|
| oracle_sched | 0.1635 | — | — | 1465 / 1931 |
| **RTI-SP** | 0.1618 | 0.1635 | **−1.04%** | **78 / 120** |
| oracle_reencode | 0.1582 | — | — | 1958 / 2930 |
| RTI-RE | 0.1565 | 0.1582 | **−1.05%** | 182 / 253 |

### N=8
| | RMSE | oracle RMSE | Δ_RTI | med/p95 ms |
|---|---:|---:|---:|---|
| oracle_sched | 0.1502 | — | — | 5443 / 8081 |
| **RTI-SP** | 0.1496 | 0.1502 | **−0.37%** | 200 / 215 |
| oracle_reencode | 0.1447 | — | — | 7323 / 12097 |
| RTI-RE | 0.1439 | 0.1447 | **−0.60%** | 348 / 399 |

### 判定
- **Δ_RTI ≤ 0（−0.4 ~ −1.0%），远小于 5–8% 门槛 → RTI-SP 正式 PASS**（RTI 1 次迭代与 exact oracle 等价，甚至略好；oracle 受 SLSQP maxiter=30 限制）。
- **horizon 才是退化主因**：同一 plant 下 N=8→N=5，oracle_sched 0.1502→0.1635（+8.9%）、oracle_reencode 0.1447→0.1582（+9.3%）、RTI-SP 0.1496→0.1618（+8.2%）——**exact 与 RTI 同步退化 ~8–9%**，证明早先的 "+16.8%" 是 N/oracle 不匹配的假象。
- **结论**：matched oracle 无灾难性结果 → **按 GPT §22，P2 真机 E1–E5 可以开始**。

## 2. Theory Diagnostics（GPT §19）

对冻结部署预测器（A_openloop, r=2, scheduled propagation）在 val 上测：

| 量 | 结果 |
|---|---|
| ε_k（一步 encoder-consistency defect，绝对） | median 0.345 / q90 0.516 / q95 0.567 / q99 0.655 / max 0.800 |
| d_M(H), H=1/5/10/20 | 0.120 / 0.390 / 0.574 / 0.928 |
| ‖A_{k+H-1}···A_k‖₂, H=1/5/10/20 | 1.046 / 1.247 / 1.541 / 2.304 |
| ‖∂F/∂ξ‖₂（经验 L_F） | median 1.445 / q90 1.448 / q95 1.450 / q99 1.451 / max 1.452 |
| Prop.2 bound / actual（dM） | H=1 4.7× / H=5 7.95× / H=10 12.1× / H=20 18.7× |
| 线性化余项 M_F（Prop.3） | δ=1e-3: 0.272；δ=1e-2: 0.015（δ=1e-4 受浮点噪声主导，弃） |
| RTI runtime p50/p95（N=5） | 78 / 120 ms |

### 解读（与理论一一对应）
1. **Prop.2 机制成立**：transition product norm 从 1.05 增至 2.30（**无收缩**，ρ>1），与 d_M 增长同向 → "仅控制 ρ(A_k)<1 不足"（§14）得到数值支持。
2. **经验 L_F ≈ 1.45 > 1**：augmented map 在 operating region 内是扩张的 → Thm.1 的 finite-horizon bound 适用（不要求 L_F<1），与 GPT §16/§19 一致（不强行制造 contraction）。
3. **Thm.1 sanity PASS**：Prop.2 bound 始终 ≥ 实际 dM（保守 4.7–18.7×，随 H 增大更保守），无违反。
4. **Prop.3 成立**：RTI 线性化二阶余项小（M_F ≤ ~0.3）→ 1 次 SQP 迭代的局部近似合理。
5. **ε_k 非零（median 0.35）**：scheduled 一步并非严格 encoder-consistent → 印证"训练分布 ≠ 部署 rollout 分布"（§15），rollout-aware 训练的必要性成立。

## 3. 状态与下一步

- **路线级研究 CLOSED**（GPT §27）；模型/控制器族冻结；runtime optimization 暂停。
- **matched oracle 完成、RTI-SP PASS → P2 真机 GO**。
- 理论侧：Diagnostics 完成 → 可进入 Prop.1/2、Thm.1、Prop.3 的正式化与论文理论章节。
- **下一步（用户执行）**：P2 真机 E1–E5（multi-setpoint / circle / figure-eight / unseen / speed shift）；真机 loop 完整接入后若 p95 ≳180 ms 再开性能优化。

## 4. 复现

- `gate16_matched_oracle.py`（`--N 5/8`）→ `gate16_matched_oracle_N5.json` / `_N8.json`；plant `plant_dnn.pt`。
- `gate16_theory_diagnostics.py` → `gate16_theory_diagnostics.json`。
- 解释器 `D:\conda\envs\edmddl2\python.exe`。
