# 阶段③ 结构 Gate 报告：Latent Koopman 上下文调制（A+ / RSHC-TK）

- 文档版本：v1
- 日期：2026-10-06
- 任务：TASK-004（阶段②→③ 衔接，strict）
- 依据决策：DEC-020 / DEC-021 / DEC-022 / DEC-023
- 结论一句话：**在真实 latent pipeline 上，控制/动力学调制的 locus 是 A（状态转移），不是 B（输入通道）；AB 相对 A-only 无增益。选择 A-only。**

---

## 1. 目的

在**真实训练/推理管线**（而非观测空间代理）上，检验 A+（RSHC-TK：Response-Structured History-Conditioned Transformer-Koopman）的核心结构问题：

> 历史/上下文调制应当施加在 latent Koopman 的哪个算子通道上？A（状态转移）、B（输入）、还是两者（AB）？

第八/十/十一轮 GPT 的推断（基于观测空间代理 `d = J(φ)·u`）认为 **B(c) 是 locus**。本 gate 在真实 latent 管线（`z=[x_t;h]`，`z'=A z + B u`，`decoder=前2维`）上直接检验该结论是否成立。

## 2. 方法

- 数据：P2 现有数据（`数据备份/软体平台数据/处理后的数据/{train,val,test}.npz`），与部署模型同源；train 19040 / val 5440 / test 2920 窗口。
- 模型：复用仓库 `PatchTSTEncoder`（输入 `x_history` `[B,P,n]` → `z=[x_t;h]`，d=10）、`LinearDecoder`（`C=[I_n|0]`，无参数）；**新增 context encoder**（MLP：`[x_history; u_history]` → `c∈R^16`）与**低秩调制**：
  - `A(c) = A0 + Ua·diag(ga(c))·Vaᵀ`，`Ua,Va ∈ R^{d×r}`，r=3
  - `B(c) = B0 + Ub·diag(gb(c))·Vbᵀ`，`Ub ∈ R^{d×r}`，`Vb ∈ R^{m×r}`
  - 模式：`fixed`（无调制）/ `A` / `B` / `AB`
- 训练：所有模式**同一流程**。先端到端训练 `fixed`（Adam, lr=1e-3, 100 epochs, bs=256, 早停选 val 1-step MSE 最优）；A/B/AB 从 fixed 权重初始化（`A0,B0,encoder` 继承，调制支路零初始化），再端到端微调（lr=5e-4, 100 epochs）。seed 0 与 seed 1 各跑一遍。
- 评估：**自由滚动 rollout**（每步重新编码历史 + 重新计算 c；用日志输入 `u` 前推），RMSE（欧氏，归一化空间）在 H=1/5/10/20，val 与 test。
- 证伪：
  - `modOFF`：推理时关闭调制（`A=A0,B=B0`，即去掉 `ΔA/ΔB`，保留该模式训练出的 encoder）。
  - `uhZERO`：推理时把 context 的输入历史 `u_history` 置零（保留 `x_history` 与真实控制输入 `u_t`）。
- 锚点：部署 EDMD 模型 `platform2_full_model.pth`（P=4, n_layers=3, d=10）用同一评估协议跑 rollout。

## 3. 结果

### 3.1 主结果（seed 0，val）

| 模式 | H=1 | H=5 | H=10 | H=20 |
|---|---|---|---|---|
| fixed | 0.0234 | 0.0728 | 0.1075 | 0.1689 |
| **A-only** | **0.0090** | **0.0209** | **0.0310** | **0.0444** |
| B-only | 0.0190 | 0.0688 | 0.1129 | 0.1824 |
| AB | 0.0089 | 0.0212 | 0.0309 | 0.0451 |

相对 fixed 的改善（%，val）：

| 模式 | H=1 | H=5 | H=10 | H=20 |
|---|---|---|---|---|
| A | 61.6 | 71.3 | 71.1 | **73.7** |
| B | 18.9 | 5.5 | **−5.0** | **−8.0** |
| AB | 61.8 | 70.8 | 71.2 | 73.3 |

### 3.2 第二 seed（seed 1，val）——稳健性

| 模式 | H=1 | H=5 | H=10 | H=20 |
|---|---|---|---|---|
| fixed | 0.0222 | 0.0727 | 0.1056 | 0.1603 |
| A | 0.0089 | 0.0203 | 0.0293 | 0.0412 |
| B | 0.0163 | 0.0614 | 0.1011 | 0.1541 |
| AB | 0.0090 | 0.0213 | 0.0310 | 0.0454 |

改善（%，val）：A = 59.8/72.0/72.2/**74.3**；B = 26.6/15.5/4.3/**3.8**；AB = 59.4/70.7/70.6/71.7。

### 3.3 test 集（seed 0）

| 模式 | H=1 | H=5 | H=10 | H=20 |
|---|---|---|---|---|
| fixed | 0.0224 | 0.0790 | 0.1117 | 0.1754 |
| A | 0.0088 | 0.0205 | 0.0295 | 0.0425 |
| B | 0.0183 | 0.0719 | 0.1176 | 0.2017 |
| AB | 0.0087 | 0.0203 | 0.0300 | 0.0456 |

### 3.4 部署模型锚点（EDMD, P=4）

val = 0.0229 / 0.0803 / 0.1109 / **0.1588**；test = 0.0230 / 0.0799 / 0.1139 / 0.1610。
与 end-to-end `fixed`（val H20=0.1689 / 0.1603）**基本一致** → gate 基线（fixed）与部署模型可比。

### 3.5 证伪

| 模式 | 条件 | H=1 | H=5 | H=10 | H=20 |
|---|---|---|---|---|---|
| A (seed0) | normal | 0.0090 | 0.0209 | 0.0310 | 0.0444 |
| A (seed0) | modOFF | 0.0580 | 0.2224 | 0.3429 | **0.5072** |
| A (seed0) | uhZERO | 0.0599 | 0.2244 | 0.3406 | 0.4927 |
| AB (seed0) | modOFF | 0.0634 | 0.2532 | 0.3978 | 0.6059 |
| AB (seed0) | uhZERO | 0.0583 | 0.2157 | 0.3269 | 0.4718 |

（seed 1 同型：A modOFF H20=0.5011、uhZERO=0.4979。）

- **modulation-off 使 H20 恶化约 11–13×** → 增益**确实来自上下文调制本身**，而非"多参数/更大容量"。
- **uh-history 置零同样使 H20 恶化约 11×** → 模型**确实依赖输入历史**构造上下文。

## 4. 结论

1. **在真实 latent pipeline 上，locus 是 A（状态转移），不是 B。**
   - A-only：H20 val 改善 **73.7%（seed0）/ 74.3%（seed1）**，远超 gate 阈值。
   - B-only：相对 fixed 几乎无增益，且在长时域（H≥10）**seed0 反而更差（−5%~−8%）**，seed1 仅 +3.8%。
2. **AB 相对 A-only 无增益**（H20：73.3% vs 73.7%；seed1：71.7% vs 74.3%）→ **选 A-only**（更简单、参数更少、性能持平或略优）。
3. **证伪通过**：增益来自调制（modOFF 崩溃）+ 依赖输入历史（uhZERO 崩溃）。
4. **修正 GPT 的推断**：第十/十一轮基于观测空间代理得出"B(c) 是 locus"的结论**不迁移到 latent 管线**。原因：代理里 `d = J(φ)·u` 结构上**只能**调制输入通道，无法表达状态转移调制；而 latent 的 `A` 作用在 `z=[x;h]` 上，`h` 编码历史，故 `A(c)` 才能表达"历史依赖的潜在动力学"，这正是 RSHC-TK 的表达力所在。

## 5. 影响与后续

- **结构决定（B 级，本报告记录）**：A+ 采用 **A-only 低秩上下文调制**（`A(c)=A0+Ua·diag(ga(c))·Vaᵀ`，r=3），`B` 保持 `B0`。
- 待办（gate 完整性 / GPT §60 剩余项）：
  - latent 管线的 **matched-state 测试**（同一 `x_k,u_k` + 不同历史 → 下一步响应差异）；
  - `CB(c)` 谱 / PD / `λmin(sym(S0·CB(c)))` 在 latent 管线上的复核；
  - `history-shuffle`（跨样本置换，比 uhZERO 更温和的证伪）；
  - 调制秩 `r` 的敏感性（r=1/2/3/5）与 `γ_max` 界（当前未加 tanh 界，需补有界性/稳定性约束，配合 DEC-018 稳定化）。
- 本 gate 只回答**结构问题**（A/B/AB），不构成 DEC-018（稳定化 + 非平凡 T1′ 界）的满足。

## 6. 证据与复现

- 脚本：`C:\Users\12187\AppData\Local\Temp\opencode\gate_context_koopman.py`（训练+证伪）、`eval_deployed.py`（部署锚点）。
- 结果 JSON：`gate_result.json`、`gate_result_s1.json`。
- 权重：`gate_states/{fixed,A,B,AB}{,_s1}.pt`。
- 解释器：`D:\conda\envs\edmddl2\python.exe`（torch 2.6.0+cu124, RTX4060）。
- 部署锚点：`deploy/algorithms/tk_assets/model_assets/platform2_full_model.pth`。
