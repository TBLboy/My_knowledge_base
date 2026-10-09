# 阶段③ 交 GPT 独立 handoff v12 —— Gate-14 结果（含两个关键负结果）

- 日期：2026-10-06
- 输入：你的第十四轮 v1.3（裁定 HC-RKMPC；要求 Gate-14A/B + Direct NN + 14C/D/E）
- 状态：14A/B/DirectNN/14C/14E 完成（14D 未做）。
- 一句话：**manifold 根因证实（14A PASS）；稳定化救不了传播（14B，你预判对），但开环训练能修好 scheduled 传播（新发现）；Koopman 远胜 DirectNN（5.9×）；然而建模增益→闭环控制增益只有 ~3%，远低于你的 10% 门槛。**

---

## 0. 决策表（你的 §71）

| Gate | 指标 | 结果 | 判决 |
|---|---|---:|---|
| 14A manifold defect | d_M(H)↑；corr(defect,RMSE) | 0.19→1.45；corr 0.49–0.57 | **PASS** |
| 14B spectral rescue | 恢复 gap % | 稳定化后 R_prop 更差(0.368→1.568) | **stable 路线关闭** |
| 14B′ open-loop training | R_prop H20 | 0.368 → **0.041** | **新发现：可修复 scheduled 传播** |
| Direct NN | H20 | 0.2596 vs Koopman 0.0439 | **Koopman 胜 5.9×** |
| 14C exact HC-RKMPC | tracking vs fixed MPC | +0.5%（plant 敏感 +2.7~3.8%） | **NO-GO（<10%）** |
| 14C C1 frozen | tracking | 0.2135（差 56%） | frozen 传播确认不可用 |
| 14D RTI | — | 未做 | 待做 |
| 14E runtime | p50/p95 | oracle med 2965 / p95 5502 ms | **FAIL；需 RTI** |

## 1. 14A manifold defect（PASS）

`d_M(i)=‖z̃−E(Ĥ)‖/‖E(Ĥ)‖`：R_prop 下 0.19/0.64/0.94/**1.45**（H1/5/10/20），与物理误差正相关（**0.49–0.57**）。开环训练把 d_M 降约 1/3、误差 0.287→**0.037**。→ 证实你的 manifold-consistency 根因。

## 2. 14B 稳定化（FAIL）＋ 开环训练（新发现）

| 模型 | ρ | R_reencode H20 | F_prop H20 | **R_prop H20** |
|---|---|---|---|---|
| baseline A_r2 | 1.032 | 0.0439 | 1.412 | 0.368 |
| one_step + ρ≤0.99 | 0.989 | 0.0486 | 1.817 | 1.568 |
| **openloop + ρ≤0.99** | 0.989 | **0.0403** | 1.138 | **0.0412** |
| **openloop（不压 ρ）** | 1.030 | 0.0430 | 1.129 | **0.0418** |

- **稳定化单独救不了传播**（你的 §23 预判成立，stable 路线关闭；§2.1"稳定≠manifold-preserving"正确）。
- **开环（scheduled 传播）训练把 R_prop 从 0.368 修到 0.041（9×）**，与重编码持平，不损失重编码性能。**且不压 ρ 也能修好** → 修复来自**训练目标**，不是稳定化。
- **F_prop（冻结 context）仍失败** → context 必须沿 horizon 更新（scheduled），与你的 §13/§26 一致。
- **含义**：你的 HC-RKMPC（每步重编码 PatchTST）可行；但**开环训练的 scheduled-propagation 版本更便宜**（每步只跑小 context-MLP，不跑 PatchTST），性能相同。这可能是一个更优的控制实现。

## 3. Direct NN baseline（Koopman 5.9×）

同 backbone/参数量（6570 vs 6714）：DirectNN H20 **0.2596** vs A-only **0.0439**。DirectNN 甚至比 fixed TK(0.169) 更差 → Koopman factorization 价值明确。

## 4. 14C 控制代理 —— 关键负结果

闭环（N=8，SLSQP oracle，plant=独立 DirectNN）：

| 控制器 | tracking RMSE |
|---|---|
| C0 fixed + 重编码 | 0.1367 |
| C2 A-only + 重编码 | 0.1360 |
| C2b A-only(openloop) + scheduled | 0.1411 |
| **C1 A-only + frozen** | **0.2135（差 56%）** |

Plant 敏感：plant=DirectNN C2+2.7%；plant=A-only C2+3.8%；plant=fixed C2**−8.5%**（失配）。

**判读**：
1. C1（frozen 传播）明确失败 → 与 Gate-13 一致。
2. **A-only 控制增益仅 ~3%，远低于你的 10% 门槛**。原因：**闭环 receding-horizon + 每步重锚定抵消了多步预测优势**——A-only 的优势在长 horizon 开环预测，短 horizon+反馈不吃。
3. **建模增益（−74%）不能按比例转化为闭环控制增益（~3%）**。这是论文 control story 的核心风险。

## 5. 14E 实时性（FAIL）

SLSQP oracle：med **2965 ms** / p95 **5502 ms** ≫ 200 ms。实现是 Python 循环 + GPU 同步，开销被放大，但 oracle 多迭代难进 200 ms。**必须 RTI-SQP（1 迭代）**；C1 frozen 的 952 ms 说明单次 rollout 约百 ms 级，RTI 有希望但需实测。

## 6. 请 GPT 裁定

1. **控制增益只有 ~3%（<10%）**，你的 §40 Gate 未过。怎么处理？
   - (a) 接受"model 是第一创新、controller 增益小"，仍进真机（P2）；
   - (b) 先改进离线控制代理（换 plant / 换指标 / 更长 horizon）再判；
   - (c) 重新考虑 controller 的定位。
2. **是否采用"开环训练的 scheduled-propagation 预测器"**替代/补充"每步重编码"？（更便宜、性能相同）
3. **14D RTI** 是否现在实现（作为真机前置）？
4. 实时性：是否接受先用 Python 实现测 p95，再决定真机？还是必须先做 batched RTI？
5. 真机 E1–E5（用户执行）是否需要先等 controller 定稿？

## 7. 复现

报告：`.project-log/docs/phase2_gate_stage3_gate14_v1.md`；脚本：`gate14_stabilize.py`、`gate14a_manifold.py`、`gate14_directnn.py`、`gate14c_control.py`、`gate14c2_plantsens.py`；结果 JSON 同名。
