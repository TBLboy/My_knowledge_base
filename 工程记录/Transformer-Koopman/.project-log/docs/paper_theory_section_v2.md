# Paper Theory Section (v2) — History-Conditioned Low-Rank Koopman Modeling and Real-Time Predictive Control

- 版本：v2.1（v2 按独立复核 9 项意见修订；v2.1 追加 GPT 第十七轮 §10 措辞约束 + v2 复检 N1/N2/N3 编辑性修正）；日期：2026-10-06；任务：TASK-005（strict）
- **复检状态**：v2 针对性复检 = **PASS（4 项 HIGH 全部闭合）**，仅 N1/N2/N3 三项 LOW 编辑性修正，已应用。
- 依据：GPT 第十六轮 §9–§21；本机 Theory Diagnostics（`gate16_theory_diagnostics.json`、`gate16_diag_fix.json`、`gate16_corollary.json`）
- 配置（与**诊断用模型**一致）：$P=8,\ n=2,\ m=2,\ d=10,\ r=2$，A-only，scheduled propagation。**注意：实际部署 ckpt 不同源（$P=4$），见末节。**
- 说明：正文英文；末尾附中文结构与诚实性说明。
- **v1→v2 变更**：修正 $P$（4→8）；bound/actual 改为**同口径**（绝对 $\epsilon$ vs 绝对 $d$）；Cor.1 改用正确的 augmented-map $L_F$；Prop.3 余项重测（$\delta^2$ 标度验证，$M_F\approx0.007$）；修正 §3.13 RTI 行；定义 $F^\star$；补充"经验估计 vs 认证界"披露；定义 $\epsilon_0$、删除 $w_k$、补中值形式。

---

## Nomenclature

| Symbol | Meaning |
|---|---|
| $x_k\in\mathbb R^{n}$ | measured output (P2: $n=2$) |
| $u_k\in\mathbb R^{m}$ | control input (P2: $m=2$) |
| $P=8$ | history length |
| $H_k=\big(x_{k-P+1:k},\,u_{k-P+1:k-1}\big)$ | finite history window |
| $z_k\in\mathbb R^{d}$ | latent state ($d=10$) |
| $c_k\in\mathbb R^{d_c}$ | context ($d_c=16$) |
| $E_\theta,\,C_\phi,\,C=[I_n\,|\,0]$ | encoder, context map, fixed decoder |
| $A(c),\,B$ | history-conditioned transition, fixed input matrix |
| $\xi_k$ | augmented predictor state |
| $\Omega$ | compact operating region |
| $\epsilon,\,L_F,\,M_F$ | augmented-map error / Lipschitz / Hessian bound on $\Omega$ |
| $L_C=\|C\|_2=1$ | decoder Lipschitz constant |

---

## 3.1 Problem setup

Discrete-time plant

$$
x_{k+1}=f^\star(x_k,u_k),\qquad x_k\in\mathbb R^n,\ u_k\in\mathbb R^m,
$$

observed through $x_k$ only, with control period $T_s$. The plant is **partially observed in the temporal sense**: the instantaneous pair $(x_k,u_k)$ does not determine $x_{k+1}$; recent history carries additional information (continuum/flexible-body memory, unmodeled states). We therefore model the predictor on a finite history window.

**Standing assumptions.**

- **(A1) Bounded operating region.** All analysis is restricted to a compact set $\Omega$ of reachable augmented states.
- **(A2) Smoothness.** The augmented transition $F_\Theta$ is $C^2$ on $\Omega$.
- **(A3) Fixed structure.** $B$ and the decoder $C$ are fixed; only $A$ is history-conditioned.
- **(A4) Empirical-vs-certified.** The constants $\epsilon$, $L_F$, $M_F$ appearing in §3.12 are **empirical estimates on the validation distribution**, not worst-case certificates over $\Omega$. The theorems are stated with worst-case constants; the diagnostics only check their *plausibility and self-consistency*.

---

## 3.2 Definition 1 — History-conditioned low-rank Koopman family

**Definition 1.** With $z_k=E_\theta(H_k)$, $c_k=C_\phi(H_k)$,

$$
\boxed{\,z_{k+1}=A(c_k)\,z_k+B\,u_k\,}
$$

$$
\boxed{\,A(c)=A_0+U\,\mathrm{diag}\big(g(c)\big)\,V^\top\,},\qquad
\boxed{\,\mathrm{rank}\big[A(c)-A_0\big]\le r=2\,.}
$$

Given $c_k$, the lifted dynamics are linear in $(z_k,u_k)$; history dependence enters only through $A(c_k)$. This is a *history-conditioned, low-rank parameter-varying* Koopman family — **not** an exact Koopman invariant-subspace operator (see §3.11). A process-noise term $w_k$ is deliberately **omitted**; the model is deterministic and all stochasticity is treated as model error $\epsilon$ in Theorem 1.

> **Remark (why A-only, $r=2$).** A/B/AB ablations show the predictive benefit concentrates in the $A$-modulation ($B$-modulation adds no gain); rank ablation shows $r=2$ is the minimal near-optimal rank.

---

## 3.3 Proposition 1 — Finite-history Markovization

**Proposition 1.** Let

$$
\xi_k=\mathrm{col}\big(x_{k-P+1:k},\,u_{k-P+1:k-1},\,z_k\big)\in\mathbb R^{Pn+(P-1)m+d}.
$$

Under the predictor's **internal** closed loop (the newest fed-back output is the decoded $\hat x_{k+1}=C z_{k+1}$), there exists a deterministic map $F_\Theta$ such that

$$
\boxed{\,\xi_{k+1}=F_\Theta(\xi_k,u_k)\,.}
$$

*Proof.* The window update is a deterministic shift: append $(\hat x_{k+1},u_k)$, drop the oldest entry. The appended output is $\hat x_{k+1}=C z_{k+1}$ with $z_{k+1}=A(c_k)z_k+Bu_k$ and $c_k=C_\phi(H_k)$. Since $H_k$ is a sub-vector of $\xi_k$, every argument of the update is a function of $(\xi_k,u_k)$ alone; composing shift, context map, transition and decoder gives a single deterministic $F_\Theta$. $\square$

> **Remark (scope of "Markov").** The Markov property holds **only** for the internal rollout with decoded feedback. If the *true* measurement $x_{k+1}$ is fed back, the update additionally depends on an exogenous input and is **not** a function of $\xi_k$ alone. The word "Markov" must never travel beyond this internal-rollout qualifier.

---

## 3.4 Definition 2 — Latent rollout inconsistency

**Definition 2.** Let $\hat H_{k+i}$ be the history produced by the predictor's own rollout. Define

$$
z^{E}_{k+i}=E_\theta(\hat H_{k+i}),\qquad
z^{P}_{k+i+1}=A(c_{k+i})z^{P}_{k+i}+Bu_{k+i},
$$

and the **normalized** rollout defect

$$
\boxed{\,d_{\mathcal M,k+i}=\frac{\big\|z^{P}_{k+i}-z^{E}_{k+i}\big\|_2}{\big\|z^{E}_{k+i}\big\|_2+\epsilon_0}\,,}\qquad \epsilon_0=10^{-6}\ \text{(a fixed numerical floor, units of }\|z\|\text{)}.
$$

We also use the **absolute** defect $d^{\mathrm{abs}}_{k+i}=\|z^{P}_{k+i}-z^{E}_{k+i}\|_2$, which is the quantity bounded by Proposition 2.

> **Remark (rollout-coupled reference).** $z^{E}_{k+i}$ is computed on $\hat H_{k+i}$, which itself contains the decoded $\hat x$; the reference is therefore **rollout-coupled**, not independent of the propagated state. The inequality below remains valid, but $d$ measures a rolled-out latent defect, **not** true-plant error.

---

## 3.5 Proposition 2 — Latent rollout error propagation

**Proposition 2.** Let $d_k=\|\hat z_k-z^{E}_k\|_2$ and

$$
\epsilon_k=\big\|A(c_k)z^{E}_k+Bu_k-z^{E}_{k+1}\big\|_2 .
$$

Then $d_{k+1}\le\|A(c_k)\|_2\,d_k+\epsilon_k$, and for any horizon $H$,

$$
\boxed{\,d_{k+H}\le\Big(\prod_{j=0}^{H-1}\|A_{k+j}\|_2\Big)d_k
+\sum_{i=0}^{H-1}\Big(\prod_{j=i+1}^{H-1}\|A_{k+j}\|_2\Big)\epsilon_{k+i}\,,}
$$

where $A_{k+j}=A(c_{k+j})$ is the transition at the **scheduled** context.

*Proof.* Subtract $A(c_k)z^{E}_k+Bu_k$:

$$
d_{k+1}=\big\|A(c_k)\hat z_k+Bu_k-z^{E}_{k+1}\big\|_2
\le\|A(c_k)\|_2\,d_k+\epsilon_k .
$$

Unrolling (empty product $=1$ at $i=H-1$) gives the horizon bound. $\square$

**Consistency with scheduled propagation.** $z^{P}$ and $z^{E}$ share the same rolled-out history $\hat H$, and $\epsilon_k$ uses the same scheduled $c_k$ as the propagated recursion; the subtraction of $A(c_k)z^{E}_k$ is therefore legitimate. The bound concerns the **rolled-out latent** defect, not true-plant error.

**Interpretation.** Long-horizon inconsistency is governed by (i) the local defect $\epsilon_k$ and (ii) the **amplification of time-varying transition products**.

---

## 3.6 Remark 1 — Why spectral stabilization is insufficient

$$
\boxed{\,\rho(A_k)<1\ \ \forall k\ \ \not\Rightarrow\ \ \|A_{k+H-1}\cdots A_k\|_2\le c<1\,.}
$$

This is the classical spectral-radius / joint-spectral-radius gap for non-commuting time-varying matrices. It explains our negative result: enforcing $\rho(A(c))\le0.99$ failed to restore scheduled-rollout accuracy, whereas changing the *training objective* (§3.7) succeeded. Used as a classical mechanism explanation, **not** a novel contribution.

---

## 3.7 Definition 3 — Rollout-aware scheduled training

The one-step objective

$$
\mathcal L_1=\sum_k\big\|E_\theta(H_{k+1})-A(c_k)E_\theta(H_k)-Bu_k\big\|_2^2
$$

constrains consistency only on the encoder-generated latent distribution, whereas deployment feeds **propagated** latents $z^{P}$:

$$
\text{training-state distribution}\ \neq\ \text{deployment rollout-state distribution}.
$$

**Definition 3.** With the scheduled rollout $z^{P}$,

$$
\boxed{\,\mathcal L_R=\sum_k\sum_{i=1}^{H_R} w_i\,\big\|Cz^{P}_{k+i}-x_{k+i}\big\|_2^2\,.}
$$

**Claim (exactly as supported).** Rollout-aware training **mitigates** latent rollout inconsistency and improves deployment-distribution prediction accuracy. We do **not** claim it guarantees strict manifold invariance.

> **Evidence chain (rigor requirement).** The claim that "one-step training does not sufficiently constrain the recursively generated rollout distribution" must be supported by the **conjunction** of four observations — $\epsilon_k>0$ (nonzero one-step defect), $d_{\mathcal M}(H)$ increasing with $H$, naive latent propagation failure, and rollout-aware training recovery. No single one of these is sufficient on its own.

---

## 3.8 Theorem 1 — Finite-horizon prediction error bound

**Convention for $F^\star$.** The true plant has no latent component. To place $F^\star$ and $F_\Theta$ on the same space, we define the true augmented map by the **same structural convention** as the predictor: the true latent and true history evolve with the *true* one-step plant and the *true* encoder on true observations,

$$
\xi^\star_{k+1}=F^\star(\xi^\star_k,u_k),\qquad
\xi^\star_k=\mathrm{col}\big(x_{k-P+1:k},\,u_{k-P+1:k-1},\,E_\theta(H_k)\big),
$$

i.e. $F^\star$ = (true plant step) ∘ (true-history shift) ∘ ($E_\theta$ on true observations), with no decoder in the loop. Then $F^\star$ and $F_\Theta$ are maps on the same augmented space.

**Assumptions (on $\Omega$).**

$$
\boxed{\ \|F^\star(\xi,u)-F_\Theta(\xi,u)\|_2\le\epsilon\ }\quad\text{(uniform model error)},\qquad
\boxed{\ \|F_\Theta(\xi_1,u)-F_\Theta(\xi_2,u)\|_2\le L_F\|\xi_1-\xi_2\|_2\ }.
$$

**Theorem 1.** With $e_k=\xi^\star_k-\hat\xi_k$, $\|e_{k+1}\|_2\le\epsilon+L_F\|e_k\|_2$, hence

$$
\boxed{\ \|e_{k+H}\|_2\le L_F^{H}\|e_k\|_2+\epsilon\sum_{j=0}^{H-1}L_F^{j}\ .}
$$

If $e_k=0$, $\|e_{k+H}\|_2\le\epsilon\sum_{j=0}^{H-1}L_F^{j}$. If additionally $L_F<1$, $\limsup_{H\to\infty}\|e_{k+H}\|_2\le\epsilon/(1-L_F)$.

*Proof.* $\|e_{k+1}\|_2=\|F^\star(\xi^\star_k,u_k)-F_\Theta(\hat\xi_k,u_k)\|_2\le\|F^\star-F_\Theta\|_2(\xi^\star_k)+\|F_\Theta(\xi^\star_k)-F_\Theta(\hat\xi_k)\|_2\le\epsilon+L_F\|e_k\|_2$. Unroll. $\square$

**Note.** Only the **finite-horizon** form is used; we do **not** require $L_F<1$ (measured empirical $L_F\approx1.45>1$).

---

## 3.9 Corollary 1 — Physical prediction error

**Corollary 1.** Since $x$ is the first $n$ coordinates of $\xi$ and $\hat x=C\hat z$,

$$
\|\hat x_{k+H}-x_{k+H}\|_2\le\|\hat\xi_{k+H}-\xi^\star_{k+H}\|_2
\le L_F^{H}\|e_k\|_2+\epsilon\sum_{j=0}^{H-1}L_F^{j},
$$

and, using the decoder bound $\|\hat x-x^\star\|_2\le L_C\|\hat z-z^\star\|_2$ with $L_C=\|C\|_2=1$,

$$
\boxed{\ \|\hat x_{k+H}-x_{k+H}\|_2\le L_C\Big[L_F^{H}\|e_k\|_2+\epsilon\sum_{j=0}^{H-1}L_F^{j}\Big]\ .}
$$

*Proof.* $x$ is a coordinate sub-vector of $\xi$, so the norm is non-increasing; the $L_C$ form follows from the decoder bound. $\square$

> **Note.** Using the direct sub-vector route avoids the convention $x=Cz$ for the true latent; $L_C=1$ is exact because $C=[I_n\,|\,0]$.

---

## 3.10 Proposition 3 — Local approximation of RTI predictive control

Around the warm-start nominal trajectory $(\bar\xi_i,\bar u_i)$,

$$
F_\Theta(\bar\xi_i+\delta\xi_i,\bar u_i+\delta u_i)=F_\Theta(\bar\xi_i,\bar u_i)+F_i\,\delta\xi_i+G_i\,\delta u_i+r_i ,
$$

with $F_i=\partial F_\Theta/\partial\xi$, $G_i=\partial F_\Theta/\partial u$. By the mean-value form,

$$
r_i=\tfrac12\,\delta_i^\top\nabla^2F_\Theta(\bar\xi_i+t\,\delta_i)\,\delta_i,\qquad \delta_i=\mathrm{col}(\delta\xi_i,\delta u_i),\ t\in(0,1).
$$

**Proposition 3.** If $F_\Theta$ is $C^2$ and $\|\nabla^2F_\Theta\|_2\le M_F$ on $\Omega$, then

$$
\boxed{\ \|r_i\|_2\le\frac{M_F}{2}\Big\|\begin{bmatrix}\delta\xi_i\\ \delta u_i\end{bmatrix}\Big\|_2^2\ .}
$$

**Use.** Supports the **local** validity of a single SQP iteration around a warm start; **not** a new SQP convergence theory.

---

## 3.11 Scope and non-goals

Deliberately **finite-horizon**. We do **not** pursue:

1. **Global Koopman stability** — no requirement $\rho(A(c))<1\ \forall c$.
2. **A common Lyapunov function** $P$.
3. **Global asymptotic closed-loop stability** — no terminal invariant set, robust invariant tube, global NMPC Lyapunov argument, or recursive-feasibility-under-learned-uncertainty claim.

Additional explicit disclaimers:

4. **Empirical vs certified.** $\epsilon,L_F,M_F$ in §3.12 are sample estimates on the validation distribution, not worst-case certificates over $\Omega$ (assumption A4).
5. **Latent, not plant.** All bounds concern the rolled-out latent predictor; they do not bound true-plant tracking error.
6. **Not an exact Koopman operator.** $A(c)$ is a latent linearization parameterization; there is no eigenfunction/spectral guarantee (no invariant-subspace claim).

> *Positioning statement.* The analysis focuses on **finite-horizon prediction consistency** and **local RTI approximation**, not global asymptotic closed-loop stability.

---

## 3.12 Numerical validation of the assumptions

Frozen **diagnostic** predictor ($A$-only, $r=2$, scheduled propagation), P2 validation set, $P=8,\ n=2,\ m=2,\ d=10$. (This is the diagnostic model, not the deployed ckpt — see the closing note.)

| Quantity | Role | Measured value (H=1/5/10/20) |
|---|---|---|
| $\epsilon_k$ (absolute one-step defect) | Prop. 2 | median 0.347; q95 0.575 (from the fixed run, `gate16_diag_fix.json`); q90 0.516; q99 0.655 (from the stride-1 run, `gate16_theory_diagnostics.json`; median there 0.345 — slight sampling difference) |
| $d^{\mathrm{abs}}(H)$ (absolute latent defect) | Prop. 2 | 0.347 / 1.114 / 1.673 / 2.678 |
| $d_{\mathcal M}(H)$ (normalized) | Def. 2 | 0.120 / 0.390 / 0.574 / 0.928 |
| $\|A_{k+H-1}\cdots A_k\|_2$ | Prop. 2 mechanism | 1.046 / 1.247 / 1.541 / 2.304 |
| $\|\partial F_\Theta/\partial\xi\|_2$ (empirical $L_F$) | Thm. 1 | median 1.445; q95 1.450; max 1.452 |
| **Prop. 2 bound / actual (like-for-like, absolute)** | **Prop. 2 sanity** | **1.65 / 2.82 / 4.21 / 6.57** |
| linearization $M_F$ (fitted, $\delta^2$-scaled) | Prop. 3 | $\approx0.007$ |
| RTI runtime | deployment | p50 78 ms / p95 120 ms ($N=5$) |

**Reading.**

1. **Prop. 2 mechanism confirmed.** Transition-product norm grows 1.05→2.30 (no contraction), tracking $d$ growth — numerically supporting Remark 1.
2. **Empirical $L_F\approx1.45>1$.** The augmented map expands on $\Omega$; the finite-horizon form of Theorem 1 is the appropriate statement.
3. **Prop. 2 sanity PASS (like-for-like).** With **absolute** $\epsilon$ vs **absolute** $d$, the bound is always $\ge$ actual and only 1.65–6.57× conservative — a *reasonable* bound. (The earlier 4.7–18.7× figure mixed a normalized $d$ with an absolute $\epsilon$ and is superseded.)
4. **Prop. 3 supported.** With $\delta\in\{10^{-2},3\cdot10^{-2},10^{-1}\}$ the remainder scales as $\delta^2$ and the fitted $M_F\approx0.007$ is stable across $\delta$ — the earlier "0.27" was a numerical-noise artifact at $\delta=10^{-3}$ and is superseded.
5. **$\epsilon_k>0$.** The scheduled one-step is not strictly encoder-consistent: the finite-dimensional model has a **nonzero one-step consistency/modeling defect**. **This alone does not imply a train/deploy distribution mismatch.** The distribution-gap claim rests on the *conjunction*: $\epsilon_k>0$ **and** $d_{\mathcal M}(H)$ increasing **and** naive-propagation failure **and** rollout-aware training recovery (see §3.7).

### 3.12.1 Corollary 1 (physical space)

$L_C=\|C\|_2=1$ exactly ($C=[I_n|0]$). Scheduled-propagation physical error from a true history:

| $H$ | physical RMSE | physical MAE | Cor.1 bound with $L_F=1.445$ | bound / actual |
|---|---:|---:|---:|---:|
| 1 | 0.0108 | 0.0094 | 0.575 | 53× |
| 5 | 0.0222 | 0.0193 | 6.84 | 309× |
| 10 | 0.0297 | 0.0257 | 49.9 | 1679× |
| 20 | 0.0419 | 0.0366 | 2025 | 48 374× |

**Reading (honest).** Corollary 1 with the augmented-map $L_F$ is **valid but extremely loose** (53–48 000×), because $L_F^H$ grows geometrically with $H$ while the true error saturates (the decoder discards $d-n$ latent coordinates and the plant is contractive on the output). We report this honestly. A tighter output-projected bound is future work. (Note: an earlier version quoted 52–413× by mistakenly using the per-step transition-product constant $\approx1.045$ in place of $L_F$; corrected here.)

---

## 3.13 Theory–experiment correspondence

| Theoretical object | Experiment / evidence |
|---|---|
| history-conditioned $A(c)$ | A/B/AB ablation |
| low-rank transition ($r$) | $r=1,2,5$ ablation |
| genuine history dependence | matched-current history shuffle |
| rollout inconsistency ($d_{\mathcal M}$, $d^{\mathrm{abs}}$) | manifold-defect diagnostic |
| transition-product amplification | product-norm diagnostic |
| spectral stabilization insufficiency (Rem. 1) | stabilization retraining (negative) |
| rollout-aware repair (Def. 3) | rollout-aware training (positive) |
| value of the Koopman factorization | DirectNN baseline (equal params) |
| real-time feasibility | RTI p50/p95 runtime |
| RTI vs exact-oracle tracking (deployment; **not** a Prop.3 validation) | exact scheduled oracle vs RTI-SP: $\Delta_{\mathrm{RTI}}=-1.04\%$ ($N{=}5$), $-0.37\%$ ($N{=}8$) |
| control utility | P2 hardware (**future work**) |

> **Correction (v1→v2).** Proposition 3 is **not** validated by the oracle-vs-RTI comparison — that comparison measures closed-loop tracking RMSE, whereas Prop. 3 bounds a second-order Taylor remainder. The two are different objects. The observed $\Delta_{\mathrm{RTI}}<0$ additionally shows the SLSQP "oracle" is **not** an RMSE upper bound (different objective / seeds / noise), which should be reported honestly rather than presented as an approximation-error signature.

---

## 附：中文结构与诚实性说明

**结构**：3.1 问题设定（含 A1–A4）→ 3.2 定义1 → 3.3 命题1（限定内部 rollout）→ 3.4 定义2（归一化 $d_{\mathcal M}$ + 绝对 $d^{\mathrm{abs}}$）→ 3.5 命题2 → 3.6 注1 → 3.7 定义3 → 3.8 定理1（含 $F^\star$ 约定）→ 3.9 推论1 → 3.10 命题3（中值形式）→ 3.11 范围/非目标（6 条）→ 3.12 数值验证（同口径）→ 3.13 理论与实验对应。

**诚实性边界**：
- 全部为**有限时域**结论，依赖 A1–A4。
- **不**声称：全局 Koopman 稳定性、公共 Lyapunov、全局渐近闭环稳定、terminal set/tube/递归可行性、精确 Koopman 不变子空间。
- 界**保守**且已如实标注：Prop.2 bound 1.65–6.57×（合理）；Cor.1 53–48 374×（极松）。
- $\epsilon,L_F,M_F$ 为**经验估计**，非 $\Omega$ 上的认证界。
- Prop.1 仅对**内部 rollout**成立；Prop.3 为**经典** Taylor 余项。
- §3.13 已修正：Prop.3 不由 oracle 对比验证。

**已知的配置不一致（另记，非本文理论内容）**：部署 ckpt `platform2_full_model.pth` 的 config 为 $P=4,\ \text{n\_layers}=3$（旧 experiment_006），与当前 `platform2.yaml`（$P=8,\ \text{n\_layers}=1$）不同源——属部署侧模型栈一致性（ALN 类型）问题，已单独登记，不影响本文诊断（诊断统一用 $P=8$）。
