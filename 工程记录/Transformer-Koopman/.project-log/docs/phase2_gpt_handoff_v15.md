# 阶段③ 交 GPT 独立 handoff v15 —— 理论章节 v2.1 完成 + 第十七轮数字修正说明

- 日期：2026-10-06
- 输入：GPT 第十七轮裁定（理论路线 CLOSED；RTI-SP/N=5/1-iter 冻结；P2 HARDWARE GO；§13 理论结构固定；§10 ε_k 措辞约束；§12 physical-space bound 非 Gate）
- 一句话：**理论章节 v2.1 已完成并通过独立复核（verdict=go）。但必须提醒：你 §5/§9 引用的 bound/actual 4.7–18.7× 与余项 0.27 是复核前旧数字，已修正为 1.65–6.57× 与 M_F≈0.007。**

---

## 1. ⚠️ 数字修正（最重要，请以本节为准）

你第十七轮 §5 表格与 §9 引用的下列数值，来自我上一份 handoff 中**复核前**的初版诊断，随后被独立复核（verification-reviewer）判定有误：

| 项目 | 你引用的旧值 | **修正值** | 原因 |
|---|---|---|---|
| Prop.2 bound / actual | 4.7 / 7.95 / 12.1 / 18.7× | **1.65 / 2.82 / 4.21 / 6.57×** | 旧值把**归一化** $d_{\mathcal M}$ 与**绝对** $\epsilon$ 混用；已改同口径（绝对 vs 绝对） |
| linearization remainder | 0.27 (δ=1e-3) / 0.015 (δ=1e-2) | **M_F ≈ 0.007** | δ=1e-3 时余项落在浮点噪声底（非二次标度）；改用 δ∈{1e-2,3e-2,1e-1}，δ² 标度稳定 |
| Cor.1 physical bound | （未提） | **53 / 309 / 1679 / 48 374×**，用 augmented-map $L_F=1.445$ | 若误用每步乘积常数 ≈1.045 会得到 52–413×（错） |
| history length | P（未提） | **P = 8** | `platform2.yaml` history_length=8；部署 ckpt 为 P=4/n_layers=3 旧 experiment_006（另记 ALN 类问题） |

**未变**（你引用的这些是对的）：$\epsilon_k$ median 0.345；$d_{\mathcal M}(H)$ 0.120/0.390/0.574/0.928；乘积范数 1.046/1.247/1.541/2.304；$L_F$ median 1.445/q95 1.450/max 1.452；RTI p50 78/p95 120 ms。

**§9 "bound ≥ actual" 结论仍成立**（修正后 bound 依然 ≥ actual，只是保守倍数从 4.7–18.7× 收紧到 1.65–6.57×，反而更可信）。

## 2. 理论章节 v2.1（已按你 §10/§13 更新）

文件：`.project-log/docs/paper_theory_section_v2.md`。结构已固定为你的 §13：

**Prop.1（Finite-History Markovization）→ Def.1（History-Conditioned Low-Rank Koopman Family, $r=2$）→ Prop.2（Latent Rollout Inconsistency Propagation）→ Thm.1（Finite-Horizon Prediction Error Bound）→ Cor.1（Physical-Space Prediction Bound）→ Prop.3（RTI Local Approximation）**，另含 §3.11 范围/非目标、§3.12 数值验证、§3.13 理论与实验对应。

**已按你 §10 收紧措辞**：$\epsilon_k>0$ 仅表示有限维模型有**非零一步一致性缺陷**，**不能单独**推出训练/部署分布不一致；分布缺口结论须由**四元合取**支撑：$\epsilon_k>0 \wedge d_{\mathcal M}(H)\uparrow \wedge$ naive propagation failure $\wedge$ rollout-aware recovery。

**你 §12 的 physical-space bound 已补**（§3.12.1）：$L_C=\|C\|_2=1$，报告 physical RMSE 0.0108/0.0222/0.0297/0.0419 与 Cor.1 bound，**如实标注为 valid-but-extremely-loose（53–48 374×）**——因为 $L_F^H$ 几何增长而真实误差饱和（decoder 丢弃 $d-n$ 维、输出方向收缩）。未作为 Gate。

## 3. 独立复核

- **REV-THEORY-001 = conditional**（v1：数学正确，4 项 HIGH 证据绑定问题）。
- **REV-THEORY-002 = go**（v2 针对性复检：4 项 HIGH **全部闭合**，逐项数值独立重算通过，未破坏任何数学结论）。
- 记录：`PHASE2-THEORY-SECTION-REVIEW-001` / `REV-THEORY-001` / `REV-THEORY-002` / `EV-PHASE2-THEORY-SECTION-003`。

## 4. 状态

- **DEC-026**：理论路线 CLOSED、RTI-SP/N=5/1-iter 冻结、P2 HARDWARE GO（已记录）。
- 用户 **DEC-025**：优先完成论文理论章节，**真机暂缓**（GO 保留）。
- 项目状态：Route Exploration → **Hardware Validation + Manuscript Consolidation**（当前活跃 = Track B 论文理论）。

## 5. 请 GPT 确认

1. 是否确认上述**数字修正**（1.65–6.57× / M_F≈0.007 / $L_F$=1.445 / P=8）为论文采用值？
2. 理论章节 v2.1 是否可进入**成稿/翻译**，或还需补：(a) 跨 seed 方差；(b) 更紧的 output-projected bound；(c) 机制图（product norm vs $d_{\mathcal M}$ vs $H$）？
3. §3.11 非目标清单（含"经验估计 vs 认证界"、"latent 非 plant"、"非精确 Koopman 算子"）是否已足够？

## 6. 复现

诊断：`gate16_theory_diagnostics.py` / `gate16_diag_fix.py` / `gate16_corollary.py`；结果 JSON 同名。报告：`paper_theory_section_v2.md`。
