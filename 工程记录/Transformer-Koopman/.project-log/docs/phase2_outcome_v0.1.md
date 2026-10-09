# 阶段② 论文理论路线重构 — 结论与交接（v0.1）

> 目标回顾（用户重定义）：论文理论路线未定稿，代码非最终版；阶段② = 在保留 Koopman 的前提下，重设建模与控制器，经构思→prior-art/证伪筛选，找到更具创新性/理论性的路线。代码/论文正文冻结。

---

## 1. 最终路线（阶段②产出）

**组合路线**（DEC-016 + DEC-017）：

```text
理论骨架：修复后的闭环跟踪界 T1′（Lyapunov 形式）
        + 执行器接口量化/饱和项（P2 整数脉冲 Δ=1，|u|<=300；e_max≈0.707 步）
        + 张紧有效性域条件 Φ + 在线离域残差检测 r_k
物理载体：P1（Geomatric Touch 刚体臂，3-DOF）+ P2（四绳差动软臂，2-D 光点）
```

**定理 T1′.**

$$
\|e^z_k\|\le\sqrt{\tfrac{\lambda_{\max}(P)}{\lambda_{\min}(P)}}(1-\lambda)^{k/2}\|e^z_0\|
+\sqrt{\tfrac{\lambda_{\max}(P)}{\lambda_{\min}(P)}}\frac{D}{1-\sqrt{1-\lambda}},\quad
D=\varepsilon+\|B\|\tfrac{\Delta\sqrt m}{2}+\delta,
$$
$\lambda=\lambda_{\min}(Q+K_c^\top RK_c)/\lambda_{\max}(P)$，$\delta=\sup_k\|P_G(z^{\mathrm{ref}}_{k+1}-Az^{\mathrm{ref}}_k)\|$。

**定理 2.** 在有效域 $x_k\in\Phi$（张紧包络）内 T1′ 成立；$r_k=\|\hat z_{k+1}-(Az_k+Ba_k)\|>\varepsilon$ 或越出 $\Phi$ 则判定保证失效。

---

## 2. 分支淘汰记录（含本轮新增）

| 分支 | 判定 | 关键依据 |
|---|---|---|
| I1 一般 Koopman abstraction | killed | Aspeel & Özay 2024 simulation preorder |
| I2 一般 reference-compatible lifting | killed | output controllability/reference governor + Uchida & Duraisamy 2023 |
| I3 一般 actuator/history extension | killed | Asada CCK 2024/2025 |
| M6 finite-memory/MZ Koopman | deferred | Lin 2021 / Gupta 2025 / Catalasan & He 2026 |
| D1 dissipativity | exploratory-blocked→kill | 无确证 physical supply rate |
| A1 actuation-factorized | killed generic | Cibulka/Korda/Haniš 2025 SIADS |
| A3 quantized-delay | downgraded | 标准采样/延迟/量化理论 |
| A4 mode-conditioned | killed generic | Blischke 2023 / Peitz 2019 / Ning 2025 / Ju 2026 |
| A5 task/actuator dual | killed generic | Boyle & Stockar 2023 |
| A6/A8 | deferred | adaptive / multi-task |
| A2/A7 | kept | 需具体定理，未展开 |
| **A9 未指令张紧偏置** | **killed（S8 实证）** | P2 共模从不下发，$a_\perp=0$ 按设计 |

---

## 3. 已验证的论文缺陷（阶段③须修）

| 缺陷 | 位置 | 状态 |
|---|---|---|
| "Schur ⇒ $\|A_{cl}\|<1$" 非推论 | Main34.tex L737 | 已验证错误（C1/C2 反例）；T1′/T2 替换 |
| 误差动力学遗漏前馈不可达项 $P_G(\cdot)$ | L732–737 | 已验证（C3）；T1′ 纳入 |
| 界 $\varepsilon/(1-\|A_{cl}\|)$ 分母可 $\le0$ | L721 | 无意义；T1′ 修复 |
| 误差未分离（编码器/数据/history） | L594–599 | 推论 2 给出分离 |
| 稳定性约束未生效（$\rho=2.09$） | platform2.yaml `svd_clipping=false` | S8b 实证；DEC-018 定为阶段③硬前提 |

---

## 4. 证据索引

- 数值脚本：`s8_verify_t1.py`（C9：DARE 恒等、原界失效、T1 单调/成立、δ 必要、β 定价）、`s8b_p2_terms.py`（S8b：$\|B\|e_{\max}=0.019$、$\rho=2.09$、界空泛）。
- 记录：PHASE2-SCREEN-003/004、PHASE2-S6-001/002、PHASE2-S8-001/002；决策 DEC-015/016/017/018。
- 文档：`phase2_theory_construction_v0.1.md`、`…v0.2.md`、`phase2_branch_status_v0.5.md`、`phase2_platform_semantics_v0.1.md`。

---

## 5. 诚实评估（novelty 风险）

- rigor 骨架（T1′）本质是标准 Lyapunov-metric UUB 修正；量化项与有效域各自为已知概念。**本路线的整体新意偏"中等/增量"**，最强点是"对学习式 Koopman 控制给出一个自洽、可估、条件性的闭环界，并显式定价执行器接口与域条件"。
- 与 Strässer 2026 综述（error bounds→closed-loop guarantees）存在潜在重叠，需在阶段③明确 delta。
- 独立复核（strict 要求）进行中：delegation `keen-coral-owl`（verification-reviewer）。

---

## 6. 阶段③ 待办（前置条件）

1. **落实稳定化**（DEC-018）：启用 SVD clipping/谱约束，使 $\rho(A)$ 受控，验证 T1′ 非空泛。
2. 重建 P2 模型栈（部署 ckpt 的 `history_length=4` 与 config 8 不一致，ALN-010 残余），并统一训练/部署副本。
3. 用验证集估计 $\varepsilon$；用参考轨迹算 $\delta$；评估量化项。
4. P1 需重训以产出 checkpoint（当前无）。
5. 论文：把 T1′+定理2 写入 Sec. IV，补 Experiments（两平台闭环 + $r_k$ 离域监控）。
6. 未决：C11（离域阈值标定）、novelty delta 与 Strässer 2026 的明确区分。
