# 阶段② · GPT 第四轮路线（Q0–Q6）本地验证报告 v1

- 日期：2026-10-05
- 输入：`第四轮自动科研路线头脑风暴报告_Feedback_Shaped_Koopman_Closure_v0.4.md`（外部 GPT）
- 任务：TASK-004（RUN-004）；决策：DEC-019（验证并回传，不构思）
- 方法：机制级 prior-art（L1/L2）+ 负向扫描 + 廉价证伪实验 T4-1…T4-6
- 代码/配置/论文：冻结；本报告只做验证

---

## 0. 结论速览

| 路线 | 机制 | 经验判决 | prior-art 判决 | 综合 |
|---|---|---|---|---|
| **Q0** Linear-Prefeedback Invariance | 线性 prefeedback 不改 LS closure error | **T4-1 精确成立（偏差 0.0）** | 平凡线性代数恒等式（row space） | ✅ 成立但**非贡献** |
| **Q1** FSAKC | 非线性 prefeedback 重塑闭合性 | **T4-2 P2 杀死**（连全秩非线性漂移仅降 0.25%，秩不变）；P1 降 31% 但=标准 input-channel 辨识 | **Fan 2401.08153**（smooth prefeedback + generalized feedback linearizability）+ 2509.02839 综述 | ❌ |
| **Q2** FSMO | 最小 obstruction 动态阶 | **T4-3 杀死**（残差 Hankel 秩 99%=**97/100**，无低阶动态） | minimal realization / subspace ID 成熟 | ❌ |
| **Q3** COMP | 闭环 obstruction 模态配置 | **T4-5 失败**（ρ_E 最优仅 0.9675，闭环 ρ=1.0） | 经典 eigenstructure assignment | ❌ |
| **Q4** FCH | 反馈复杂度层级 | Q0 给 J₁=J₀；但 Q1 杀死使 J₂<J₁ 在 P2 不成立 | feedback linearization / immersion 成熟 | ❌（P2） |
| **Q5** SNOK | 低维非线性 obstruction 核 | T4-4 子空间稳定（前 2–3 维 <1°），但 T4-3 无低阶动态 + T4-2 不可反馈重塑 | bilinear/LPV/structured reduction | ❌ |
| **Q6** CSKC (=Q1+Q2+Q3) | 内层压缩 + 外层配置 | 依赖 Q1/Q2/Q3，三者均在 P2 失败 | 组合撞车 | ❌ |

**总结论**：第四轮**主要路线在 P2 上被经验杀死**。Q0 是一个正确但平凡的线性代数事实，不构成理论贡献。P2 的闭合缺陷是**小的（归一化 RMSE≈0.008）、不可（后验）反馈重塑的、且全阶动态的**残余——不是可构造的 obstruction 几何。

---

## 1. 机制级 prior-art

| 工作 | 内容 | 压缩了哪条 |
|---|---|---|
| **Fan, Yi, Rye, Shi, Manchester, arXiv:2401.08153**（Automatica；2024/2025） | Learning Stable Koopman Embeddings：**明确允许 smooth prefeedback**，依赖 **generalized feedback linearizability**；证明稳定性/可镇定性与 Koopman embedding 的联系 | **Q1/Q4/Q6 的 exact 情形**（新报告 §7/§25 已自认） |
| **Strässer, Worthmann, Mezić, Berberich, Schaller, Allgöwer, arXiv:2509.02839**（Annual Reviews in Control 2026） | "An overview of Koopman-based control: From error bounds to closed-loop guarantees" —— 系统综述近似误差、控制器设计、**闭环保证** | **Q1 的 Theorem C / Q6 的闭环误差界** |
| **Ondogan, Jing, Sabelhaus, Tron, arXiv:2510.05359** | Koopman Control Factorization：控制-仿射系统 + 控制器（非线性测量线性组合），闭环 Koopman=双线性组合，SDP 凸设计 | Q3/Q6 的“控制器–模型联合设计” |
| **Morris, Ye, Tang, arXiv:2606.10344** | 状态与输入分别 lift 到 RKHS 时，非线性系统可**精确**表示为双线性 | Q1/Q5 的 exact/bilinear 情形 |
| **Zinage–Bakolas, arXiv:2201.05098** | Neural Koopman Lyapunov Control：同时学 bilinear Koopman embedding + CLF，保证可控仿射系统镇定 | Q3/Q5 |
| 2602.14537 / 2603.15091 / 2603.29001 / 2605.24666 / 2608.11808 | （第三轮已录）CAP / PAD / principal-vector / PageRank / Koopman+HJB | Q1–Q6 各处 |

**负向扫描**：`stabilizable Koopman embedding` = 2（含 Fan 2401.08153）；`Koopman feedback linearization` = 55（反馈线性化 + Koopman 已是成熟簇）。**没有查到“feedback-dependent minimal Koopman closure rank/order”这一精确机制**，但它被 Fan（exact）+ minimal realization（近似阶）从两侧夹住。

---

## 2. 廉价证伪实验 T4-1…T4-6

脚本：`Q_P2.py`、`Q_P1.py`。P2 用部署模型冻结编码器；P1 全观测 z=x 直接拟合。

### T4-1 线性 prefeedback 不变性（Q0）
- 20 组随机 K，`v=u-Kz`，重拟合 A_K,B_K。
- 残差范数与基线**偏差 = 0.0（数值精确）**，`std=0`。
- **判决：Q0 成立**（`row[Z;V]=row[Z;U]` 的线性代数恒等式）。但这是教科书级事实，**不构成新定理**。

### T4-2 反馈闭合（Q1/Q6 核心）
P2 冻结编码器，val（归一化单位）：

| α 类型 | val RMSE | 残差秩 90/99 | α 幅度 |
|---|---|---|---|
| baseline（α=0） | 0.008029 | 2 / 4 | — |
| linear α=Kz | 0.008031 | 2 / 4 | 0.100 |
| quadratic α | 0.008005 | 2 / 4 | 0.577 |
| MLP α（秩 m=2） | 0.008030 | 2 / 4 | 0.220 |
| **full 非线性漂移（秩 n=10）** | **0.008009** | 2 / 4 | — |

- 反馈（含 rank-10 全秩非线性项）**仅降 0.25%**，残差**有效秩完全不变**。
- **判决：Q1 在 P2 上杀死。** 在冻结 lifting 下，反馈无法重塑 obstruction；Q1 的唯一退路是 lifting+feedback 联合重训 = 被拒绝的原路线 + 被 Fan 占。

### T4-3 残差 Hankel 谱（Q2 核心）
- P2 残差块 Hankel（L=10）秩：**90%=78 / 99%=97（满 100）**；top-10 奇异值 ≈0.96–1.0（**平坦**）。
- **判决：残差无低阶动态实现** → D7 的“低秩 obstruction”仅是**瞬时协方差结构**，不是低阶动态。**Q2 杀死。**

### T4-4 obstruction 子空间可复现性（Q3/Q5 前提）
- P2 70 条训练轨迹各自 top-4 残差 PCA 基的主角度均值 [**0.08°, 0.2°, 0.75°, 7.03°**]，max [0.36°, 0.85°, 2.78°, 22.5°]。
- **判决：前 2–3 维子空间高度可复现**（非假象）。这一点支持 Q3/Q5 的前提，但被 T4-2/T4-3 否决。

### T4-5 obstruction 模态配置（Q3 核心）
- P2 r=4，baseline ρ(A)=1.001；优化后 **leakage=0.035，ρ_E=0.9675，闭环 ρ_cl=1.0**。
- **判决：无法在保持闭环稳定下让 obstruction 模态快衰减**（ρ_E 无法 <<1）→ **Q3 弱/失败**；且属经典 eigenstructure assignment。

### T4-6 P1 非线性 prefeedback
- P1 baseline RMSE 0.133，残差 **100% 在 im(B)**，谱 [0.698, 0.235, 0.068, 0, 0, 0]（秩 3）。
- nonlinear prefeedback RMSE 0.0917（**↓31%**）；full 漂移 0.0957（↓28%）；**残差仍 100% 在 im(B)，秩仍 3**。
- **判决：P1 上“反馈有效”只是学回 input-channel 的重力/科氏非线性（标准非线性辨识）**，无秩缩减、无新机制；且 full 漂移≈prefeedback 说明改进全部来自输入通道。

---

## 3. 与硬门禁逐条对拍

| 路线 | (1)建模改 | (2)控制器改 | (3)物理锚点 | (4)新定理 | (5)prior-art | (6)数据可实现 |
|---|---|---|---|---|---|---|
| Q0 | — | — | 通用 | 平凡恒等式 | 经典 | ✔ |
| Q1 | ✔ | ✔（两层） | P1 平凡 / P2 失败 | 部分 | ✖ Fan 2401.08153 | ✔ |
| Q2 | ✔ | 部分 | P2 失败 | 部分 | ✖ 最小实现 | ✔ |
| Q3 | ✔ | ✔ | P1 退化 | 部分 | ✖ 经典配置 | ✔ |
| Q4 | ✔ | ✔ | P2 失败 | 部分 | ✖ feedback linearization | ✔ |
| Q5 | ✔ | ✔ | P2 前提部分成立但动态全阶 | 部分 | ✖ 结构化降维 | ✔ |
| Q6 | ✔ | ✔ | 依赖 Q1–Q3 | 部分 | ✖ | ✔ |

**无一路线满足全部门禁。**

---

## 4. 元结论（跨四轮）

经过 **R 轮（18 条）→ N 轮（6 条）→ M 轮（12 条）→ Q 轮（7 条）**，在“机制级新 + P1/P2 物理锚点 + 可证定理 + prior-art 划界”的门禁下，**没有任何候选存活**。反复出现的模式：

1. P2 的闭合误差**小且不可后验重塑**（反馈/漂移增广无效）；
2. P2 的“低秩”只是**瞬时协方差**，其动态是**全阶**的；
3. P1 的残差**恒在 im(B)**，任何“反馈/补偿”都退化为标准输入通道辨识；
4. 剩余机制要么被 CAP/PAD/principal-vector/PageRank/error-bound 综述（2509.02839）/Fan（smooth prefeedback）密集占据，要么是经典控制（几何解耦、eigenstructure assignment、最小实现、反馈线性化）。

这提示：**继续在同一平台数据 + 同一门禁下迭代构思，收益已趋近零**。需要 C 级决策（见交接稿 v4 §7）。

---

## 5. 溯源

- 决策：DEC-019；DEC-018（未满足）。
- 证据：`EV-PHASE2-GPT-Q-ROUTES-001`。
- 脚本：`Q_P2.py`、`Q_P1.py`（`%TEMP%\opencode\`）。
- 前序：`phase2_gpt_m_routes_validation_v1.md`。
- 独立交接稿：`phase2_gpt_handoff_v4.md`。
