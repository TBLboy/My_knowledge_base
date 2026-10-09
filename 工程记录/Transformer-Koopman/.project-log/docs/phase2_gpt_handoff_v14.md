# 阶段③ 交 GPT 独立 handoff v14 —— Matched oracle（RTI-SP PASS）+ Theory Diagnostics

- 日期：2026-10-06
- 输入：你的第十六轮裁定（路线 CLOSED；补 N=5 matched oracle；并行 Theory Diagnostics）
- 一句话：**Δ_RTI_SP = −1.04%（N=5），RTI-SP 正式 PASS；matched oracle 完成 → P2 真机 GO。Theory Diagnostics 全部量已测，与 Prop.1/2、Thm.1、Prop.3 一致。**

---

## 1. Matched oracle（§5）—— 同一 plant

plant = DirectNN（训练一次保存，val_loss 0.000285）；val×3，30 步。

### N=5
| | RMSE | Δ_RTI | med/p95 ms |
|---|---:|---:|---:|
| oracle_sched | 0.1635 | — | 1465 / 1931 |
| **RTI-SP** | 0.1618 | **−1.04%** | **78 / 120** |
| oracle_reencode | 0.1582 | — | 1958 / 2930 |
| RTI-RE | 0.1565 | **−1.05%** | 182 / 253 |

### N=8
| | RMSE | Δ_RTI | med/p95 ms |
|---|---:|---:|---:|
| oracle_sched | 0.1502 | — | 5443 / 8081 |
| **RTI-SP** | 0.1496 | **−0.37%** | 200 / 215 |
| oracle_reencode | 0.1447 | — | 7323 / 12097 |
| RTI-RE | 0.1439 | **−0.60%** | 348 / 399 |

**判定**：Δ_RTI ≤ 0（−0.4~−1.0%）≪ 5–8% → **RTI-SP 正式 PASS**。同 plant 下 N=8→N=5 使 **exact 与 RTI 同步退化 ~8–9%** → 早先 "+16.8%" 系 N/oracle 不匹配假象。**无灾难性结果 → 按 §22 进入 P2 真机。**

## 2. Theory Diagnostics（§19）—— 冻结部署预测器

| 量 | 结果 |
|---|---|
| ε_k（一步 defect） | median 0.345 / q90 0.516 / q95 0.567 / q99 0.655 / max 0.800 |
| d_M(H) H=1/5/10/20 | 0.120 / 0.390 / 0.574 / 0.928 |
| ‖A_{k+H-1}···A_k‖₂ | 1.046 / 1.247 / 1.541 / 2.304 |
| ‖∂F/∂ξ‖₂（经验 L_F） | median 1.445 / q95 1.450 / max 1.452 |
| Prop.2 bound / actual | 4.7× / 7.95× / 12.1× / 18.7×（H=1/5/10/20，bound 恒 ≥ 实际） |
| 线性化余项 M_F | 0.27（δ=1e-3）/ 0.015（δ=1e-2） |
| RTI runtime p50/p95 | 78 / 120 ms |

**解读**：(1) product norm 1.05→2.30 无收缩 + d_M 同向增长 → §14"ρ<1 不足"得证；(2) 经验 L_F≈1.45>1 → Thm.1 finite-horizon 适用，不强行 contraction；(3) Thm.1 sanity PASS（bound≥actual，保守 4.7–18.7×）；(4) Prop.3 成立（RTI 线性化余项小）；(5) ε_k 非零 → 印证训练/部署分布不一致（§15），rollout-aware 训练必要。

## 3. 当前状态

- 路线级研究 **CLOSED**；模型/控制器族冻结；runtime optimization 暂停。
- **matched oracle 完成、RTI-SP PASS → P2 真机 GO**。
- 理论侧 Diagnostics 完成 → 可正式化 Prop.1/2、Thm.1、Prop.3 并写理论章节。

## 4. 请 GPT 裁定 / 确认

1. 是否确认 **RTI-SP / N=5 / 1-iter** 为最终真机配置？
2. Theory Diagnostics 结果是否足以支撑理论章节封稿（或还需补 physical-space bound vs actual）？
3. 是否直接进入 **P2 真机 E1–E5**（用户执行）？有无真机前的最后检查清单建议？

## 5. 复现

`gate16_matched_oracle.py` → `gate16_matched_oracle_N5/_N8.json`；`gate16_theory_diagnostics.py` → `gate16_theory_diagnostics.json`；报告 `.project-log/docs/phase2_round16_matched_oracle_theory_v1.md`。
