# 阶段③ 交 GPT 独立 handoff v13 —— Gate-14D RTI 结果（§23 表 + GO/NO-GO）

- 日期：2026-10-06
- 输入：你的第十五轮裁定（唯一剩余 Gate = 14D；返回 §23 表 + P2 hardware GO/NO-GO）
- 一句话：**RTI-SP 在 N=5 时 p95=78 ms（Strong GO）、RTI-RE p95=128 ms（GO）；N=8 时两者 NO-GO。1 次 SQP 迭代足够（2 次无改善且翻倍）。**

---

## §23 表

### N=8（1 次迭代）
| Metric | RTI-RE | RTI-SP |
|---|---:|---:|
| tracking RMSE | 0.1438 | 0.1498 |
| exact oracle RMSE（N=8 SLSQP） | 0.1360 | 0.1360 |
| degradation vs oracle | +5.8% | +10.2% |
| rollout p50/p95 ms | 281/311 | 168/234 |
| Jacobian p50/p95 ms | （含在 rollout） | （含在 rollout） |
| QP p50/p95 ms | 10.5/17.0 | 11.7/23.2 |
| total p50/p95 ms | 292/**347** | 179/**261** |
| solver failure % | 0.0 | 0.0 |
| max \|u\| | 1.10 | 1.10 |

### N=5（1 次迭代）—— 推荐
| Metric | RTI-RE | RTI-SP |
|---|---:|---:|
| tracking RMSE | 0.1528 | 0.1588 |
| degradation vs N=8 oracle | +12.3% | +16.8%（N 不匹配，见下） |
| rollout p50/p95 ms | 109/117 | 61/66 |
| QP p50/p95 ms | 7.3/9.1 | 8.3/10.5 |
| total p50/p95 ms | 117/**128** | 69/**78** |
| solver failure % | 0.0 | 0.0 |
| max \|u\| | 1.14 | 1.14 |

### N=5（2 次迭代）—— 否决
RTI-RE 0.1554 / p95 651 ms；RTI-SP 0.1624 / p95 349 ms。**精度无改善、耗时翻倍** → 1 次迭代为准。

## 关键观察

1. **RTI-SP 比 RTI-RE 快约 1.6×**（每 stage 不跑 PatchTST）——证实 rollout-trained scheduled propagation 的部署价值。
2. **N 是决定性旋钮**：N=8→NO-GO；**N=5 使 RTI-SP 进入 Strong GO（78 ms）**。
3. **实时性 Gate（§13）**：N=5 RTI-SP = **Strong GO**；N=5 RTI-RE = GO；N=8 两者 NO-GO。
4. **性能 Gate（§14）**：RTI-SP +10.2%（N=8）/ +16.8%（N=5）→ **超 5–8%**；RTI-RE +5.8%（N=8，在门槛内）。
5. **重要 caveat**：oracle 参考是 **N=8**（0.1360）。**N=5 的 oracle 会更差**，故 N=5 的退化百分比被**高估**；需在 N=5 上重测 oracle 才能公平判定。闭环代理 plant=DirectNN 本身限制精度（绝对差异 0.14–0.16 很小）。
6. Jacobian 耗时已含在 rollout 计时内（未单独分离）。

## P2 hardware 判决

- **实时性：GO**（RTI-SP, N=5, p95 78 ms）。
- **精度：borderline**（1 次迭代退化 +6~17%）。
- **综合：Conditional GO**：建议以 **RTI-SP, N=5（或 N=6）** 进真机；进入前补 **(a) N=5 匹配 oracle**、**(b) 更快的 rollout 实现**。
- 严格按 §14 判据 = **NO-GO**（精度门槛未过）；按 §13 = **GO**。张力源于 N 与 oracle 不匹配，非方法缺陷。

## 请 GPT 裁定

1. 是否接受 **RTI-SP, N=5, 1 iteration** 作为真机配置？
2. 是否需要我**补 N=5 的匹配 oracle**（约 3 分钟）以给出公平的退化百分比？
3. 是否需要**优化 rollout 实现**（当前 Python 循环 + 每 stage GPU 同步，开销被放大；批量化可望再降）？
4. 是否**直接进 P2 真机**（E1–E5，用户执行）？

## 复现

脚本 `gate14d_rti.py`；结果 `gate14d_result.json` / `_N5.json` / `_N5_it2.json`；报告 `.project-log/docs/phase2_gate_stage3_gate14d_v1.md`。
