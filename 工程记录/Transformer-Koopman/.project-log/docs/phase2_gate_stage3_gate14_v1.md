# 阶段③ Gate-14 报告：manifold defect / 稳定化救援 / 直接 NN / 控制代理 / 实时性

- 文档版本：v1
- 日期：2026-10-06
- 任务：TASK-004（strict）
- 输入：GPT 第十四轮 v1.3（裁定路线 (i) HC-RKMPC；要求 Gate-14A/B + Direct NN + 14C/D/E）
- 结论一句话：**manifold-consistency 根因被证实（14A）；单纯稳定化救不了传播（14B，GPT 预判正确），但"开环传播训练"能修好 scheduled 传播（本轮新发现）；Koopman 结构远胜直接 NN（5.9×）；然而建模增益→闭环控制增益只有约 3%，远低于 10% 门槛——这是本轮最重要的负结果。**

---

## 0. 决策表（GPT §71 要求的表）

| Gate | 指标 | 结果 | 判决 |
|---|---|---:|---|
| 14A manifold defect | d_M(H) 增长；corr(defect, RMSE) | 0.19→1.45 (H1→H20)；corr 0.49–0.57 | **PASS** |
| 14B spectral rescue | 恢复 reencode gap % | 稳定化后 R_prop 反而更差(0.368→1.568) | **stable 路线关闭**（GPT 预判正确） |
| 14B′ open-loop training | R_prop H20 | 0.368 → **0.041**（9×，≈重编码） | **新发现：开环训练可修复 scheduled 传播** |
| Direct NN baseline | H1/5/10/20 | 0.0240/0.0848/0.1426/**0.2596** | **Koopman 胜 5.9×**（同参数量） |
| 14C exact HC-RKMPC | tracking vs fixed MPC | C2 0.1360 vs C0 0.1367（+0.5%；plant 敏感 2.7–3.8%） | **NO-GO（<10%）** |
| 14C C1 frozen | tracking | 0.2135（差 56%） | **确认 frozen 传播不可用** |
| 14D RTI | — | 未做（oracle SLSQP 已太慢） | 待做 |
| 14E runtime | p50/p95 ms | oracle SLSQP med 2965 / p95 5502 ms | **FAIL（≫200ms）**；需 RTI |

---

## 1. Gate-14A：Manifold consistency defect（PASS）

定义 `d_M(i)=‖z̃_{k+i}−E(Ĥ_{k+i})‖/‖E(Ĥ_{k+i})‖`（传播 latent vs 同一预测 history 的重编码 latent）。

| 模型/预测器 | d_M(H1/H5/H10/H20) | 物理误差(H1/H5/H10/H20) | corr(d_M, err) |
|---|---|---|---|
| A_r2 + R_prop | 0.19/0.64/0.94/**1.45** | 0.008/0.042/0.107/0.287 | −0.04/**0.54/0.57/0.49** |
| A_r2 + F_prop | 0.19/0.63/0.92/1.33 | 0.008/0.212/0.528/1.273 | −0.04/0.06/0.08/−0.06 |
| A_openloop + R_prop | 0.12/0.41/0.60/0.97 | 0.010/0.020/0.026/**0.037** | 低 |
| A_openloop + F_prop | 0.12/0.41/0.60/0.93 | 0.010/0.203/0.484/1.046 | 低 |

**判读**：
- d_M(H) 随 horizon **单调增长**（R_prop：0.19→1.45），证实 **latent 离开 encoder manifold**（GPT 根因判断正确）。
- 对 **scheduled 预测器**（R_prop），d_M 与物理误差**正相关（0.49–0.57）** → 直接支持"失败源于 latent consistency loss"。
- **开环训练把 d_M 降低约 1/3，并把物理误差从 0.287 降到 0.037** → manifold 一致性可被训练改善。

## 2. Gate-14B：稳定化救援（FAIL）＋ 开环训练（新发现）

对 A-only 做 budgeted low-rank（δ_A=0.07，硬界）+ ρ≤0.99 谱约束 + 可选开环训练，跑满 100 epoch：

| 模型 | ρ median/max | ‖ΔA‖ max | R_reencode H20 | F_prop H20 | **R_prop H20** |
|---|---|---|---|---|---|
| baseline A_r2 | 1.032/1.043 | 0.068 | 0.0439 | 1.412 | 0.368 |
| one_step + ρ≤0.99 | 0.989/0.990 | 0.026 | 0.0486 | 1.817 | 1.568 |
| **openloop + ρ≤0.99** | 0.989/0.990 | 0.037 | **0.0403** | 1.138 | **0.0412** |
| **openloop（不压 ρ）** | 1.030/1.030 | 0.038 | **0.0430** | 1.129 | **0.0418** |

**判读**：
1. **单纯稳定化（one_step+ρ）不但没救传播，反而更差**（R_prop 0.368→1.568）→ **GPT §23 的预判成立，stable-latent 主路线关闭**。稳定矩阵 ≠ manifold-preserving（GPT §2.1 正确）。
2. **新发现：开环（scheduled 传播）训练把 R_prop 从 0.368 修到 0.041（9×），与重编码持平，且不损失重编码性能（0.043 vs 0.044）**。
   - 机制：开环训练直接优化"z 传播 + 每步由解码 history 重算 context"的自洽 rollout，使模型成为**有效的 scheduled-propagation 预测器**（无需每步跑 PatchTST）。
   - 不压 ρ 也能修好（ρ 仍在 1.03）→ **修复来自训练目标，不是稳定化**。
   - **F_prop（冻结 context）仍失败**（1.13）→ context 必须沿 horizon 更新（scheduled），与 GPT §13/§26 一致。
3. 含义：GPT 的 HC-RKMPC（每步重编码 PatchTST）**可行**；但**开环训练的 scheduled-propagation 版本更便宜**（每步只跑小 context-MLP，不跑 PatchTST），且性能相同。

## 3. Direct NN baseline（回答"为什么一定要 Koopman"）

同 PatchTST backbone、同参数量：

| 模型 | H1 | H5 | H10 | H20 | 参数量 |
|---|---|---|---|---|---|
| DirectNN `x_{k+1}=MLP([E(H_k);u_k])` | 0.0240 | 0.0848 | 0.1426 | **0.2596** | 6570 |
| **A-only Koopman** | 0.0088 | 0.0209 | 0.0305 | **0.0439** | 6714 |

**Koopman 结构好 5.9×（H20），参数量相当。** DirectNN 甚至比 fixed TK（0.169）还差 → Koopman factorization 的价值明确。GPT §64/§65 的 baseline 得到回答。

## 4. Gate-14C：控制代理（闭环，plant=DirectNN）—— 关键负结果

闭环 receding-horizon（N=8，SLSQP oracle，ref=记录 val 轨迹，plant=独立 DirectNN）：

| 控制器 | tracking RMSE | med_ms | p95_ms |
|---|---|---|---|
| C0 fixed + 重编码 MPC | 0.1367 | 2965 | 5502 |
| C2 A-only + 重编码 MPC | 0.1360 | 3533 | 4213 |
| C2b A-only(openloop) + scheduled MPC | 0.1411 | 2349 | 2818 |
| **C1 A-only + frozen 传播 MPC** | **0.2135（差 56%）** | 952 | 1273 |

Plant 敏感性（1 条轨迹，re-encoding MPC）：

| plant | C0 fixed | C2 A-only | C2 相对 |
|---|---|---|---|
| DirectNN | 0.1569 | 0.1526 | **+2.7%** |
| A-only | 0.1561 | 0.1501 | **+3.8%** |
| fixed | 0.1538 | 0.1669 | **−8.5%**（失配） |

**判读**：
1. **C1（frozen 传播）明确失败**（差 56%）→ 与 Gate-13 一致，naive latent-propagation MPC 不可用。
2. **C0≈C2：A-only 控制增益仅约 3%，远低于 GPT §40 的 10% 门槛**。原因：**闭环 receding-horizon + 每步重锚定**把多步预测优势大部分抵消——A-only 的优势在长 horizon 开环预测，而短 horizon + 反馈不吃这个优势。
3. plant 依赖明显（对 fixed plant 失配 −8.5%）→ 离线代理不可靠；**真正的控制增益只能在真机上判**。
4. **含义（重要）**：**建模增益（−74%）不能按比例转化为闭环控制增益（~3%）**。这与 GPT §50"大收益来自 model、controller 只再提升一点"方向一致，但更极端——连 10% 都没有。

## 5. Gate-14E：实时性（FAIL，需 RTI）

- SLSQP oracle：med **2965 ms** / p95 **5502 ms** ≫ 200 ms 周期 → **oracle 不可实时**。
- 该实现是 Python 循环 + 每步 GPU 同步，开销被放大；但即使优化，oracle 多迭代也难进 200 ms。
- **必须用 RTI-SQP（1 次迭代）**；C1（frozen）的 952 ms 说明单次 rollout 成本约百 ms 级，RTI 有希望但需实测。
- 结论：**GPT §18 实时性 Gate 目前 FAIL；RTI 实现是进入真机的前置项。**

## 6. 综合结论

1. **根因确认**：latent 离开 encoder manifold 是主因（14A），ρ>1 是放大器。
2. **路线裁定**：稳定化 latent **关闭**（14B）；GPT 的 **HC-RKMPC（重编码/调度）是唯一可行方向**。**新增选项**：开环训练后可用**更便宜的 scheduled-propagation 预测器**。
3. **建模价值确认**：Koopman 结构 vs DirectNN = 5.9×。
4. **最大风险兑现**：**建模增益→控制增益的转化率很低（~3% vs 预测 −74%）**。这是论文 control story 的核心风险，需要在真机或更好的控制代理上重新评估。
5. **实时性**：oracle 不可用，需 RTI。

## 7. 复现

- 脚本：`gate14_stabilize.py`（14B）、`gate14a_manifold.py`（14A）、`gate14_directnn.py`（DirectNN）、`gate14c_control.py`（14C）、`gate14c2_plantsens.py`（plant 敏感）。
- 结果：`gate14_result.json`、`gate14a_result.json`、`gate14_directnn_result.json`、`gate14c_result.json`。
- 权重：`gate_states/A_stab_*.pt`。
- 解释器：`D:\conda\envs\edmddl2\python.exe`。
