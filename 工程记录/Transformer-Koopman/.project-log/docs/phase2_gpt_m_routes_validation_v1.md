# 阶段② · GPT 第三轮路线（M1–M12 / C1–C4）本地验证报告 v1

- 日期：2026-10-05
- 输入：`第三轮自动科研路线头脑风暴报告_Defect_Geometry_and_Goal_Oriented_Koopman_v0.3.md`（外部 GPT）
- 任务：TASK-004（RUN-004）；决策：DEC-019（验证并回传，不构思）
- 方法：机制级 prior-art（L1/L2/L3）+ 负向扫描 + 廉价证伪实验 D1–D7
- 代码/配置/论文：冻结；本报告只做验证

---

## 0. 结论速览

| 路线 | 机制 | 经验判决 | prior-art 判决 | 综合 |
|---|---|---|---|---|
| M1 Defect-Coherent Koopman | 缺陷路由/屏蔽 | **D1 杀死 shielding 支路**（V\*=0） | 几何解耦经典；Ko proximity 占用 | ❌ |
| M2 Projected Harmful-Error Certificate | 投影有害误差证书 | **D3 仅 ~4×半径缩减** | 2603.15091 / 2608.11808 占用 | ⚠️ 降级 |
| M3 Dual-Weighted Goal-Oriented | 对偶加权目标导向 | **D4 权重=线性模型的精确伴随** | DWR 经典（PDE/ROM） | ⚠️ 降级（经典） |
| M4 KKT-Coherent MPC | KKT/活动集 | **D5 约束从不激活** | 参数化 QP 灵敏度经典 | ❌ |
| M5/M12 CAP-Core + Obstruction | 线性核 + 低维 obstruction | **D7 obstruction 低秩（秩 2–4）存活** | CAP 2602.14537 / PAD 2603.15091 / 2603.29001 / 2605.24666 | ⚠️ 仅存候选 |
| M6 almost decoupling | 近似解耦 | 未杀伤 | H∞+Koopman 残差=普通鲁棒 | ❌ |
| M7 matched virtual input | 匹配虚拟输入 | **D6 无预测增益** | 匹配补偿经典（D3 同源） | ⚠️ 降级 |
| M8 shielding horizon | 屏蔽时域 | 未杀伤 | 有限时域可观 Gramian | ❌ |
| M9 task-family envelope | 任务族包络 | **D2 秩 2→10** | — | ❌ |
| M10/M11 | 辅助 | 未杀伤 | 未评估 | 待定 |

**总排位（残余）**：C2（M5/M12，低秩 obstruction）> C3（M3，经典 DWR）> C1（M1+M2+M9；**D2 杀 M9、D1 杀 M1 shielding、M2 降为匹配补偿**，C1 实际塌缩为 M2 单条且经典）。

**诚实结论**：M 轮**没有任何路线同时通过机制级新颖性与物理锚点**。最强残余 M5/M12 在 P2 上有**低维 obstruction 结构（秩 2–4）**，但其“线性核 + 低维余项分解”被 PAD（2603.15091）、CAP（2602.14537）、principal-vector 剪枝（2603.29001）、PageRank（2605.24666）密集占据。

---

## 1. 机制级 prior-art（负向扫描证据）

扫描方式：arXiv 全文检索（`export.arxiv.org/api/query` 已 transport error；改用 `https://arxiv.org/search/?searchtype=all&query=...` HTML）。

| 查询 | 命中 | 关键结论 |
|---|---|---|
| `Koopman disturbance decoupling` | **4** | 无一条做几何 output-nulling / 干扰解耦；最近为 DNN 偏差补偿、KoopmanFlow 谱解耦 |
| `dual-weighted residual control` | **26** | **全部**在 PDE/ROM/有限元 goal-oriented 自适应；**无一条**在 Koopman/系统辨识 |
| `goal-oriented Koopman` | **0** | 交集无人占 |
| `Koopman output nulling invariant subspace` | **0** | 交集无人占 |
| `Koopman goal-oriented error certificate` | **0** | 交集无人占 |
| `Koopman invariant subspace control` | **28** | 见下方撞车清单 |

### 关键撞车清单（本轮新增，均需在 2603/2602 语境下判）
- **2608.11808**（math.OC, 2026-08）Data-Driven optimal control via Koopman + HJB：SSD+EDMD；给出 **不变/非不变字典空间的有限样本误差界**、Lyapunov–Perron 单调收敛、**闭环指数稳定 + optimality gap**。→ **直接压缩 M2/M3**（“误差界 + 最优性间隙 + 闭环稳定”已被覆盖）。
- **2603.29001**（eess.SY, 2026-03）子空间剪枝 via **principal vectors**：principal angle ↔ 一致性法的等价 + rank-one 更新。→ 压缩 M5 的“角度/分解”机制。
- **2605.24666**（math.DS, 2026-05）PageRank 检测 **Koopman 不变子空间**（零块结构，含近似不变与 $O(1/\sqrt M)$ 界）。→ 压缩 M5 的“不变核识别”。
- **2603.15091**（PAD，已录）：principal angle decomposition + 后验多步误差界 + 字典精修。→ 压缩 M2/M5。
- **2602.14537**（CAP，已录）：精确 Koopman 线性嵌入 ⇔ CAP 结构的充要条件。→ 封锁 M5 的“CAP 核”正当性。
- **2311.13033**（invariance proximity 闭式界，已录）、**2307.15368**（Koopman Control Family，已录）。

**判定**：三条“交集为 0”的查询说明**目标导向 Koopman 证书 / Koopman 输出零空间**这一具体交叉点确实空白；但**组成部件**（几何解耦、DWR、principal angle/CAP 分解、非不变字典误差界）全部成熟且近期被密集覆盖。空白来自“没人这么拼”，不自动等于“新机制”。

---

## 2. 廉价证伪实验 D1–D7（数据即证据）

平台：P2 部署模型 `platform2_full_model.pth`（A 10×10, B 10×2, ρ(A)=2.0878, rank(Ctrb)=10/10）；编码器由 `model_state_dict` 的 `encoder.*` 还原；归一化用 ckpt `normalization`。脚本：`D_P2.py`、`D_P1.py`、`D_P2_DWR.py`、`D_P2_D7.py`。

| 实验 | 度量 | 结果（train / val） | 判决 |
|---|---|---|---|
| **D1** | 最大 (A,B)-受控不变子空间 ⊂ kerC 维数 | **V\* = 0**；kerC=8, imB=2, benign=imB；ρ_V=0.0 | 无输出零空间/屏蔽支路 → **M1 shielding 死** |
| **D2** | 任务族策略零空间秩 vs 任务数 | 秩 @[1,10,50,200] = **[2,10,10,10]** | 10 步即满秩 10 → 无普适零方向 → **M9 死** |
| **D3** | 有害子空间 q95 半径缩减 + 匹配相干 | ρ_matched 0.848/0.931, ρ_harmful 0.152/0.069；q95 比 = **0.251** (train) / 0.237 (val)；V\*=0 ⇒ benign=imB | 仅 ~4× 缩减且 benign=匹配 → **M2 降为经典匹配补偿** |
| **D4** | corr(对偶加权残差, ΔJ) vs corr(原始缺陷, ΔJ) | **corr(DWR,ΔJ)=1.0000**；corr(raw,ΔJ)=0.1215（n=5220, H=10） | 线性标称模型下伴随**精确** → 权重=标准 LQR 协态 → **M3 降级为经典 goal-oriented** |
| **D5** | 数据 u 幅值 vs u_max | \|u\|max = **65.3** (train) / 59.2 (val)，u_max=300 | 约束从不激活 → **M4 无物理锚点，死** |
| **D6** | Δu=B†r 重构误差 / Δu 可预测性 | recon err **3.68e-12**；Δu std [0.607,1.807,0.824]；跨关节 corr(2,3)=0.785；可预测性≈raw | 无更低维/更可预测结构 → **M7 降级** |
| **D7** | 残差协方差谱 + 二步/一步误差比 | 归一键值 [0.517,0.423,0.031,0.023,0.004,0.002,3e-4,3e-4,7e-5,0]；有效秩 **90%=2, 99%=4**；二步/一步中位 **2.21** (q95 5.36)；n=26640 | obstruction **低维（秩 2–4）** → **M5/M12 经验存活** |

**实验小结**
- **经验存活**：仅 M5/M12（低秩 obstruction）与降级后的 M3（DWR）。
- **经验杀死**：M1（shielding）、M4、M9。
- **经验降级**：M2、M3、M7。
- D4 的 corr=1.0 是**线性模型伴随精确性**的必然而非新机制：对线性 (A,B)，一阶伴随给出的是精确成本扰动（无高阶项），故 DWR 权重 = 标准 LQR/伴随协态。它只证明“按成本相关方向加权优于原始范数”（0.12→1.0），这是经典结论。

---

## 3. 与硬门禁（`phase2_route_reset_v0.1.md`）逐条对拍

门禁要求：(1) 建模参数化/辨识目标改变；(2) 控制器结构改变；(3) 真实物理锚点 P1 & P2；(4) 新可验证定理；(5) 方法/定理级 prior-art；(6) 现有数据可实现或标注缺口。

| 路线 | (1) | (2) | (3) | (4) | (5) | (6) |
|---|---|---|---|---|---|---|
| M1 | ✔ 缺陷路由新损失 | ✖ 屏蔽支路无对象(V\*=0) | ✖ P2 无输出零空间 | 部分 | ✖ 经典 | ✔ |
| M2 | 部分（投影权重） | ✖ 匹配补偿寻常 | 部分 | 部分（几何界） | ✖ 2603.15091/2608.11808 | ✔ |
| M3 | ✖ 仅权重 | ✖ | 部分 | ✖（线性精确=平凡） | ✖ DWR 经典 | ✔ |
| M4 | ✔ | ✔ MPC | ✖ 约束不激活 | 部分 | ✖ 参数化QP | ✔ |
| M5/M12 | ✔ | 部分 | ✔ P2 低秩 obstruction | 部分（CAP/PAD 后） | ✖ CAP/PAD/pruning/PageRank 密集 | ✔ |
| M6/M8 | ✖ | ✖ | 部分 | 部分 | ✖ | ✔ |
| M7 | ✖ | 部分 | 部分 | ✖ | ✖ | ✔ |
| M9 | ✔ 任务族 | 部分 | ✖ | 部分 | — | ✔ |

**无一路线满足全部门禁。**

---

## 4. 残余与给 GPT 的约束

1. **经验上唯一有物理结构的残余**：P2 潜空间**缺陷集中在低维子空间（秩 2–4/10）**，P1 残差 100% 在 im(B)（r_n≈0）。若要走 obstruction 路线，必须给出**超越 PAD/CAP/principal-vector/PageRank 的机制**（例如：obstruction 的**闭环**几何随控制器变化，而 PAD 是开环诊断）。
2. **P2 的硬事实**：V\*=0（无输出零空间）；任务族秩迅速满 10；u 远离约束；匹配子空间即 imB。任何依赖“输出零空间 / 任务族不变 / 约束激活 / 低维匹配子空间”的构思在 P2 上无效。
3. **P1 的硬事实**：全观测 EL、无 ckpt、残差 100% 在 im(B) → 匹配补偿在 P1 平凡。
4. **DWR/certificate 类**已被 2608.11808（Koopman+HJB 误差界+最优性间隙+闭环稳定）大幅占位；需明确划界。
5. 请 GPT 下一轮**聚焦“闭环、随控制器变化”的机制**，并显式说明与 2602.14537 / 2603.15091 / 2603.29001 / 2605.24666 / 2608.11808 的差异，否则无法过门禁 (5)。

---

## 5. 溯源

- 决策：DEC-019（回传反馈，不构思）；DEC-018（阶段③ 硬前提，未满足）。
- 证据：`EV-PHASE2-GPT-M-ROUTES-001`（本报告 sha256 绑定）。
- 实验脚本：`D_P2.py`、`D_P1.py`、`D_P2_DWR.py`、`D_P2_D7.py`（`%TEMP%\opencode\`）。
- 前序：`phase2_gpt_n_routes_validation_v1.md`、`phase2_gpt_route_validation_v2_l3.md`。
- 独立交接稿：`phase2_gpt_handoff_v3.md`。
