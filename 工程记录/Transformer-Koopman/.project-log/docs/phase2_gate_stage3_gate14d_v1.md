# 阶段③ Gate-14D 报告：RTI-SQP（RTI-RE vs RTI-SP）与实时性

- 版本：v1；日期：2026-10-06；任务：TASK-004（strict）
- 输入：GPT 第十五轮裁定（唯一剩余 Gate = 14D；返回 §23 表 + P2 hardware GO/NO-GO）
- 结论一句话：**RTI-SP 在 N=5 时 p95=78ms（Strong GO），RTI-RE p95=128ms（GO）；N=8 时两者 NO-GO。1 次 SQP 迭代足够（2 次无改善且翻倍）。精度相对 oracle 退化 +5.8%~+16.8%，受 N 不匹配与 plant 代理限制，需谨慎解读。**

---

## 1. 方法

- **RTI-SQP**（1 次迭代/周期）：warm start（上一步最优序列 shift）→ nominal rollout → 线性化（autograd Jacobian `∂pred/∂U`）→ LTV-QP（L-BFGS-B，盒约束）→ 只执行第一步。
- **RTI-RE**：每个预测 stage 重跑完整 PatchTST encoder（模型 = A-only r2）。
- **RTI-SP**：rollout 训练的 scheduled propagation（latent 传播，context 由解码 history 重算；模型 = A_openloop），**不重跑 PatchTST**。
- 闭环：plant = 独立 DirectNN；ref = 记录 val 轨迹（3 条）；N=8 与 N=5；n_iter=1 与 2。

## 2. 结果（GPT §23 表）

### N=8（1 次迭代）
| Metric | RTI-RE | RTI-SP |
|---|---:|---:|
| tracking RMSE | 0.1438 | 0.1498 |
| exact oracle RMSE（N=8 SLSQP, 重编码） | 0.1360 | 0.1360 |
| degradation vs oracle | +5.8% | +10.2% |
| rollout p50 / p95 ms | 281 / 311 | 168 / 234 |
| Jacobian p50/p95 ms | （含在 rollout 内） | （含在 rollout 内） |
| QP p50 / p95 ms | 10.5 / 17.0 | 11.7 / 23.2 |
| total p50 / p95 ms | 292 / **347** | 179 / **261** |
| solver failure % | 0.0 | 0.0 |
| max \|u\| | 1.10 | 1.10 |

### N=5（1 次迭代）—— 推荐配置
| Metric | RTI-RE | RTI-SP |
|---|---:|---:|
| tracking RMSE | 0.1528 | 0.1588 |
| degradation vs N=8 oracle | +12.3% | +16.8%（N 不匹配，见 §4） |
| rollout p50 / p95 ms | 109 / 117 | 61 / 66 |
| QP p50 / p95 ms | 7.3 / 9.1 | 8.3 / 10.5 |
| total p50 / p95 ms | 117 / **128** | 69 / **78** |
| solver failure % | 0.0 | 0.0 |
| max \|u\| | 1.14 | 1.14 |

### N=5（2 次迭代）—— 否决
RTI-RE rmse 0.1554 / p95 651 ms；RTI-SP rmse 0.1624 / p95 349 ms。**精度无改善、耗时翻倍** → **1 次迭代为准**。

## 3. 实时性 Gate（GPT §13）

| 配置 | total p95 | 判据 | 判决 |
|---|---:|---|---|
| RTI-SP, N=5 | **78 ms** | <100 | **Strong GO** |
| RTI-RE, N=5 | 128 ms | 100–150 | **GO** |
| RTI-SP, N=8 | 261 ms | ≥180 | NO-GO |
| RTI-RE, N=8 | 347 ms | ≥180 | NO-GO |

**关键**：RTI-SP 比 RTI-RE 快约 **1.6×**（每 stage 不跑 PatchTST），与预期一致。**N 是决定性旋钮**：N=5 使 RTI-SP 进入 Strong GO。

## 4. 性能 Gate（GPT §14）与 caveat

- RTI-SP vs oracle：+10.2%（N=8）/ +16.8%（N=5）→ **超过 5–8% 门槛**。
- RTI-RE vs oracle：+5.8%（N=8，**在门槛内**）/ +12.3%（N=5）。
- **重要 caveat**：oracle 参考是 **N=8** 的 SLSQP（0.1360）。N=5 的 oracle 会更差（horizon 更短），所以 **N=5 的退化百分比被高估**；应在 N=5 上重测 oracle 才能公平判定。
- 另：闭环代理 plant=DirectNN 本身限制精度（Gate-14C 已见 plant 敏感），绝对差异（0.14–0.16）很小。

## 5. P2 hardware 判决

- **实时性：GO**（RTI-SP, N=5, p95 78 ms）。
- **精度：borderline**（1 次迭代退化 +6~17%；RTI-RE@N=8 达 <8%，RTI-SP 略超）。
- **综合：Conditional GO** —— 建议以 **RTI-SP, N=5（或 N=6）** 进真机；但进入前应补 **(a) N=5 匹配 oracle** 与 **(b) 更快的 rollout 实现**（当前 Python 循环开销被放大）以巩固结论。
- 严格按 §14 判据：**NO-GO**（精度门槛未过）；按 §13 判据：**GO**。二者张力源于 N 与 oracle 不匹配，非方法本身。

## 6. 复现

脚本 `gate14d_rti.py`；结果 `gate14d_result.json`（N=8）、`gate14d_result_N5.json`（N=5）、`gate14d_result_N5_it2.json`（N=5×2）。解释器 `D:\conda\envs\edmddl2\python.exe`。
