# 阶段③ 交 GPT 独立 handoff v16 —— 理论包第四轮（冻结前）复核通过 + 实现一致性审计三项结论

- 日期：2026-10-06
- 输入：审阅方第四轮冻结前审阅意见（对象 `Main(3).tex`；判定 CORE THEORY=COMPLETE、PROOF AUDIT=PASS、METHOD–THEORY CONSISTENCY=PASS、THEORY PACKAGE=COMPLETE；仅剩 NUMERICAL/IMPLEMENTATION CONSISTENCY AUDIT）
- 一句话：**理论包已按第四轮意见收口；3 项实现一致性审计中 Check 1/2 通过，Check 3 对"论文/配置/诊断"成立（=8）、对"部署控制器"待 TASK-007 重训补齐（旧路线 P=4）。理论文本本身无需再改。**

---

## 1. 本轮做了什么（对应你 §2–§24 的 PASS 项）

前几轮已修正并在本轮保持：Problem Formulation 切换到 A(c) 路线；Stage 0/1 职责分离；损失记号三分 `L_init / L_con / L_R`；`B` 语义（Stage 0 学习、Stage 1 冻结，`B(c)≡B`）；"stable base operator" → "data-fitted nominal base operator"；投影兼容性区分**结构性恒等式** `C z^E_{k+1}=x_{k+1}` 与**近似传播一致性**；Prop.2 升级为 matrix-product 形式并重写证明；Assumption 1 限定到 operating set 内的 reference augmented states；Thm.1 初始化收紧为 `e_k=0`；`ε` 与 `ε_k` 严格区分；Prop.3 不再过度解释 one-iteration RTI。

**本轮新增（你 §24 可选润色）**：Stage 0 句改为

> it is the only training stage optimized exclusively on the encoder-consistent one-step latent distribution.

## 2. 实现一致性审计（你 §23 / §27 的 3 项）

**Check 1 — Prop.2 数值 bound：PASS。**
单一口径 `gate16_diag_final.json`（stride-1）：transition-product norm `‖A_{k+H-1}···A_k‖₂` = **1.046 / 1.247 / 1.541 / 2.304**；bound/actual = **1.64 / 2.77 / 4.22 / 6.52×**。脚本 `gate16_diag_final.py`（L70–73）确以**矩阵乘积的范数**计算 → 与改写后的 matrix-product Prop.2 **同口径**，非旧 product-of-norms 输出。

**Check 2 — context 输入：PASS。**
训练/部署代码 `c = ctx(cat([xh, uh]))`，维度 `P·n + (P−1)·m` → 输入 = `(X_k, U^in_k)`，与论文 Def.1 一致。

**Check 3 — P=8：部分通过（唯一缺口，且非理论问题）。**
`P_paper = P_config(platform2.yaml history_length) = P_diagnostics = 8`（json 中 `P=8`）。
**缺口**：当前**部署控制器**仍是**旧路线**（固定 A + LQR）的 `P=4 / n_layers=3` 模型（源自旧项目 `论文4/code_project`，DEC-028 已作废）→ 待 **TASK-007**（移植 gate14 新路线训练代码、重训并导出 P=8 模型、更新部署栈）后补齐。**与论文文本无关。**

## 3. ⚠️ 数值口径统一（请以本节为准）

v15 中曾给出 bound/actual = **1.65/2.82/4.21/6.57×**、Cor.1 = 53–**48 374**× —— 这些来自 stride-4 的旧脚本 `gate16_diag_fix.json`。论文最终采用**单一口径 stride-1** 的 `gate16_diag_final.json`：

| 量 | **论文采用值** |
|---|---|
| Prop.2 bound / actual | **1.64 / 2.77 / 4.22 / 6.52×** |
| Cor.1 physical bound | **53 – 47 750×**（用 `L_F=1.445`） |

其余不变：`ε_k` median 0.345（q90 0.516 / q95 0.567 / q99 0.655 / max 0.800）；`d_abs` 0.346/1.122/1.645/2.663；`d_M(H)` 0.120/0.390/0.574/0.928；`L_F≈1.445`（q95 1.450 / max 1.452）；`M_F≈0.007`；physical RMSE 0.0108/0.0222/0.0297/0.0419；RTI p50 78 / p95 120 ms。

## 4. 交付物

- `论文/新版本/Main.tex` — sha256 `a31dc60b78ecae6ddcea058c10bc1fb780725481c0f944be65f7d29c27b7d011`（81399 B）
- `论文/新版本/build/Main.pdf` — sha256 `35972277255cdadc8d3c462057ded6473967ac7bd86f0d038c2b25d08cbdc8a5`（304487 B，**12 页**）；仅剩旧有 **0.87 pt overfull**（Cor.1 式），无 undefined reference。
- 诊断单一口径：`gate16_diag_final.json`（stride-1）。

## 4b. 贡献②定位重构（本轮新增，`PHASE2-CONTRIB-REFRAME-001`）

按《多步预测误差贡献定位修改建议》重构贡献②，**不再把 multi-step / rollout loss 本身当作 novelty**，改为"机制识别 + 部署一致训练"：

- **L124 贡献②标题** → **"Scheduled-rollout inconsistency and deployment-consistent training"**，正文改为：识别 one-step 训练的 history-conditioned Koopman 在**递归调度传播**下的 training–deployment inconsistency（latent→预测 history→context→算子漂移），**谱稳定 ρ(A)<1 修不好**，故在**与部署一致的递归调度传播**下训练（让模型经历自生成的 latent/history/context），恢复长时域精度至接近 recurrent re-encoding。
- **L117 Introduction**、**L99 Abstract**、**L859 Conclusion** 同步该措辞。
- **未改**：Methodology（§IV-B 本就"先讲为何 rollout、再给多步目标"，无 "novel multi-step loss" 类表述）；Stage-1/子节/定义名保留为方法名。
- **§10 红线核查**：论文中**不存在**那 4 条被劝退的过度声明（novel multi-step loss / key innovation is a rollout loss / unlike existing methods / first to address）。
- **待定**：论文标题（L90）仍含 "with Rollout-Aware Training"，审阅方未提及，暂未改。


## 5. 遗留（均非理论）

- **Fig.2** 示意图重绘（改为 Stage 1：`A(c)` + scheduled rollout）—— 用户已裁定**重绘**，但**推迟**（绘图暂停 DEC-025）；重绘前示意图与 caption 暂不一致。
- 颜色标记（`\textcolor{red/blue}`）暂留。
- **§VII 实验章节**待实验整理后撰写；中英转换待定稿后。
- **TASK-007**：新路线训练代码移植进 `训练代码/` + P=8 部署模型重训（补齐 Check 3）。
- **P2 真机 E1–E5**（用户执行；DEC-025 暂缓）。

## 6. 请 GPT 确认

1. 是否确认 Check 1/2/3 判定，以及 Check 3 的"论文/配置/诊断=8、部署控制器=4（待重训）"处理方式？
2. 理论包是否正式标记 **THEORY PACKAGE = COMPLETE / FROZEN** 并**停止全面理论审计**？
3. 数值口径统一（**1.64–6.52×** / **53–47 750×**）是否为论文采用值？
4. 下一步是否按你的建议顺序执行：`final config audit → experiment consolidation → P2 hardware validation → manuscript finalization`？
5. 贡献②定位重构（§4b：scheduled-rollout inconsistency + deployment-consistent training）是否认可？论文标题（L90）是否同步去掉 "Rollout-Aware Training"？

## 7. 复现

- 诊断：`gate16_diag_final.py` → `gate16_diag_final.json`（stride-1，单一口径）；`gate16_diag_fix.py` → `gate16_diag_fix.json`（stride-4，仅供对照）。
- 理论章节：`.project-log/docs/paper_theory_section_v2.md`。
- 论文：`论文/新版本/Main.tex`。
