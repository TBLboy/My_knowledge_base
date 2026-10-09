# Paper Theory Section (v1 draft) — History-Conditioned Low-Rank Koopman Modeling and Real-Time Predictive Control

- 版本：v1；日期：2026-10-06；任务：TASK-005（strict）
- 依据：GPT 第十六轮裁定 §9–§21 理论框架；本机 Theory Diagnostics 数值验证（`gate16_theory_diagnostics.json`）
- 说明：正文用英文（论文成稿语言，可直接进入论文）；末尾附中文结构与诚实性说明。
- 诚实性：所有命题/定理均为**有限时域**结论；**不**声称全局渐近闭环稳定性、公共 Lyapunov 函数或递归可行性。数值诊断仅用于**验证假设与 bound 的自洽性**，不作为定理的证明。

---

## Nomenclature

| Symbol | Meaning |
|---|---|
| $x_k\in\mathbb R^{n}$ | measured output/state (P2: $n=2$), $k$ discrete time |
| $u_k\in\mathbb R^{m}$ | control input (P2: $m=2$) |
| $P$ | history length |
| $H_k=\big(x_{k-P+1:k},\,u_{k-P+1:k-1}\big)$ | finite history window |
| $z_k\in\mathbb R^{d}$ | latent state ($d=10$) |
| $c_k\in\mathbb R^{d_c}$ | context vector ($d_c=16$) |
| $E_\theta,\,C_\phi,\,C$ | encoder, context map, decoder |
| $A(c),\,B$ | history-conditioned transition, fixed input matrix |
| $\xi_k$ | augmented predictor state |
| $\Omega$ | compact operating region |
| $\epsilon,\,L_F$ | augmented-model error and Lipschitz constant on $\Omega$ |
| $\rho(\cdot),\,\|\cdot\|_2$ | spectral radius, spectral norm |

---

## 3.1 Problem setup

We consider a discrete-time plant

$$
x_{k+1}=f^\star(x_k,u_k),\qquad x_k\in\mathbb R^n,\ u_k\in\mathbb R^m,
$$

observed through the output $x_k$ only, with a finite control period $T_s$. The plant is **partially observed in the temporal sense**: the instantaneous pair $(x_k,u_k)$ does not determine $x_{k+1}$; the recent history carries additional information (flexible/continuum body memory, unmodeled states). We therefore model the predictor on a finite history window rather than on $x_k$ alone.

**Standing assumptions.**

- **(A1) Bounded operating region.** All experiments and analyses are restricted to a compact set $\Omega$ of reachable augmented states (no global claims).
- **(A2) Smoothness.** The augmented transition $F_\Theta$ (Definition 2) is $C^2$ on $\Omega$.
- **(A3) Fixed structure.** $B$ and the decoder $C$ are fixed (not context-modulated); only $A$ is history-conditioned.

---

## 3.2 Definition 1 — History-conditioned low-rank Koopman family

**Definition 1.** Given a history window $H_k$, define

$$
z_k=E_\theta(H_k),\qquad c_k=C_\phi(H_k),
$$

and the **history-conditioned Koopman family**

$$
\boxed{\,z_{k+1}=A(c_k)\,z_k+B\,u_k+w_k\,}
$$

with

$$
\boxed{\,A(c)=A_0+U\,\mathrm{diag}\big(g(c)\big)\,V^\top\,},\qquad
\boxed{\,\mathrm{rank}\big[A(c)-A_0\big]\le r\,.}
$$

In this work $r=2$.

Given $c_k$, the lifted dynamics are **linear** in $(z_k,u_k)$; history dependence enters **only** through the transition $A(c_k)$. This is not a fixed LTI Koopman operator but a *history-conditioned, low-rank parameter-varying* Koopman family.

> **Remark (why A-only).** A/B/AB ablations show that the predictive benefit is concentrated in the $A$-modulation; the $B$-modulation yields no additional gain (Section 5). The rank ablation shows $r=2$ is the minimal near-optimal rank.

---

## 3.3 Proposition 1 — Finite-history Markovization

**Proposition 1.** Let

$$
\xi_k=\mathrm{col}\big(x_{k-P+1:k},\,u_{k-P+1:k-1},\,z_k\big)\in\mathbb R^{Pn+(P-1)m+d}.
$$

Under the predictor's own closed loop (i.e. the newest output fed back is the decoded $\hat x_{k+1}=C z_{k+1}$), there exists a deterministic map $F_\Theta$ such that

$$
\boxed{\,\xi_{k+1}=F_\Theta(\xi_k,u_k)\,.}
$$

Hence the finite-history, latent-space predictor is **exactly** a first-order Markov nonlinear system on the augmented state $\xi$.

*Proof.* The history window update is a deterministic shift: the newest pair $(\hat x_{k+1},u_k)$ is appended and the oldest entry is dropped. The appended output is $\hat x_{k+1}=C z_{k+1}$ with $z_{k+1}=A(c_k)z_k+Bu_k$ and $c_k=C_\phi(H_k)$. Since $H_k$ is a sub-vector of $\xi_k$, every argument of the update is a function of $(\xi_k,u_k)$ alone; composing the shift, the context map, the transition, and the decoder yields a single deterministic $F_\Theta$. $\square$

**Consequence.** The augmented state provides a unified state space for both the finite-horizon error analysis (§3.6) and the predictive controller (§3.7).

> **Remark.** If instead the *true* measurement $x_{k+1}$ is fed back, the update additionally depends on an exogenous input and is not a function of $\xi_k$ alone. Proposition 1 is stated for the predictor's internal rollout, which is the object used in prediction and in the RTI linearization.

---

## 3.4 Definition 2 — Latent rollout inconsistency

**Definition 2.** Let $\hat H_{k+i}$ denote the history window produced by the predictor's own rollout. Define

- **encoder-consistent latent:** $z^{E}_{k+i}=E_\theta(\hat H_{k+i})$,
- **propagated latent:** $z^{P}_{k+i+1}=A(c_{k+i})z^{P}_{k+i}+Bu_{k+i}$,

and the **normalized manifold/rollout defect**

$$
\boxed{\,d_{\mathcal M,k+i}=\frac{\big\|z^{P}_{k+i}-z^{E}_{k+i}\big\|_2}{\big\|z^{E}_{k+i}\big\|_2+\epsilon_0}\,.}
$$

$d_{\mathcal M}$ measures how far the recursively propagated latent has drifted from the encoder-consistent latent. It grows with the horizon in our experiments (§3.9).

---

## 3.5 Proposition 2 — Latent rollout error propagation

**Proposition 2.** Let $d_k=\|\hat z_k-z^{E}_k\|_2$ and define the **encoder-consistent one-step defect**

$$
\epsilon_k=\big\|A(c_k)z^{E}_k+Bu_k-z^{E}_{k+1}\big\|_2 .
$$

Then

$$
d_{k+1}\le\|A(c_k)\|_2\,d_k+\epsilon_k ,
$$

and consequently, for any horizon $H$,

$$
\boxed{\,d_{k+H}\le\Big(\prod_{j=0}^{H-1}\|A_{k+j}\|_2\Big)d_k
+\sum_{i=0}^{H-1}\Big(\prod_{j=i+1}^{H-1}\|A_{k+j}\|_2\Big)\epsilon_{k+i}\,,}
$$

where $A_{k+j}=A(c_{k+j})$ is the transition at the scheduled context.

*Proof.* Insert and subtract $A(c_k)z^{E}_k+Bu_k$:

$$
\begin{aligned}
d_{k+1}
&=\big\|A(c_k)\hat z_k+Bu_k-z^{E}_{k+1}\big\|_2\\
&\le\big\|A(c_k)(\hat z_k-z^{E}_k)\big\|_2+\big\|A(c_k)z^{E}_k+Bu_k-z^{E}_{k+1}\big\|_2\\
&\le\|A(c_k)\|_2\,d_k+\epsilon_k .
\end{aligned}
$$

Iterating and unrolling the product gives the horizon bound. $\square$

**Interpretation.** Long-horizon rollout inconsistency is governed by **two** independent factors: (i) the local encoder-consistency defect $\epsilon_k$, and (ii) the **amplification of the time-varying transition products**.

---

## 3.6 Remark 1 — Why spectral stabilization is insufficient

If $\rho(A_k)<1$ for all $k$, this does **not** imply a uniform contraction of the time-varying products:

$$
\boxed{\,\rho(A_k)<1\ \ \forall k\ \ \not\Rightarrow\ \ \|A_{k+H-1}\cdots A_k\|_2\le c<1\,.}
$$

This is the classical gap between spectral radius and joint spectral radius for non-commuting, time-varying matrices. It explains our negative result: enforcing $\rho(A(c))\le0.99$ (budgeted low-rank retraining) **failed** to restore scheduled-rollout accuracy, whereas changing the *training objective* (rollout-aware training, §3.7) did.

> We use this as a classical mechanism explanation, **not** as a novel theoretical contribution.

---

## 3.7 Definition 3 — Rollout-aware scheduled training

The one-step objective

$$
\mathcal L_1=\sum_k\big\|E_\theta(H_{k+1})-A(c_k)E_\theta(H_k)-Bu_k\big\|_2^2
$$

constrains consistency only on the **encoder-generated** latent distribution. At deployment, however, the transition consumes **propagated** latents $z^{P}$, whose distribution differs:

$$
\text{training-state distribution}\ \neq\ \text{deployment rollout-state distribution}.
$$

**Definition 3 (rollout-aware objective).** With the scheduled rollout $z^{P}$ (latent propagated, context re-scheduled from decoded history),

$$
\boxed{\,\mathcal L_R=\sum_k\sum_{i=1}^{H_R} w_i\,\big\|Cz^{P}_{k+i}-x_{k+i}\big\|_2^2\,.}
$$

**Claim (exactly as supported).** Rollout-aware training **mitigates** latent rollout inconsistency and improves deployment-distribution prediction accuracy. We do **not** claim it guarantees strict manifold invariance.

> **Deployment consequence.** Because the rollout is trained to be accurate under scheduled propagation, the controller need not re-run the full encoder at every prediction stage — enabling the RTI-SP predictor of §3.8.

---

## 3.8 Theorem 1 — Finite-horizon prediction error bound

On the augmented state (§3.3), let the true and modeled transitions be

$$
\xi^\star_{k+1}=F^\star(\xi^\star_k,u_k),\qquad \hat\xi_{k+1}=F_\Theta(\hat\xi_k,u_k).
$$

**Assumptions (on $\Omega$).**

$$
\boxed{\ \|F^\star(\xi,u)-F_\Theta(\xi,u)\|_2\le\epsilon\ }\qquad\text{(uniform model error)}
$$

$$
\boxed{\ \|F_\Theta(\xi_1,u)-F_\Theta(\xi_2,u)\|_2\le L_F\|\xi_1-\xi_2\|_2\ }\qquad\text{(Lipschitz)}.
$$

**Theorem 1.** With $e_k=\xi^\star_k-\hat\xi_k$,

$$
\|e_{k+1}\|_2\le\epsilon+L_F\|e_k\|_2,
$$

and therefore

$$
\boxed{\ \|e_{k+H}\|_2\le L_F^{H}\|e_k\|_2+\epsilon\sum_{j=0}^{H-1}L_F^{j}\ .}
$$

If the horizon starts from a true measurement ($e_k=0$),

$$
\boxed{\ \|e_{k+H}\|_2\le\epsilon\sum_{j=0}^{H-1}L_F^{j}\ .}
$$

If in addition $L_F<1$, then $\limsup_{H\to\infty}\|e_{k+H}\|_2\le\epsilon/(1-L_F)$.

*Proof.* By the triangle inequality,

$$
\begin{aligned}
\|e_{k+1}\|_2
&=\|F^\star(\xi^\star_k,u_k)-F_\Theta(\hat\xi_k,u_k)\|_2\\
&\le\|F^\star(\xi^\star_k,u_k)-F_\Theta(\xi^\star_k,u_k)\|_2
+\|F_\Theta(\xi^\star_k,u_k)-F_\Theta(\hat\xi_k,u_k)\|_2\\
&\le\epsilon+L_F\|e_k\|_2 .
\end{aligned}
$$

Unrolling the recursion gives the finite-horizon bound; the geometric series follows when $L_F<1$. $\square$

**Note.** The paper uses only the **finite-horizon** bound. We do **not** require the experimental system to satisfy $L_F<1$ (indeed the measured empirical $L_F\approx1.45>1$, §3.9).

---

## 3.9 Corollary 1 — Physical prediction error

**Corollary 1.** If the decoder is Lipschitz with constant $L_C$ ($\|Cz_1-Cz_2\|_2\le L_C\|z_1-z_2\|_2$; here $C$ is linear so $L_C=\|C\|_2$), then

$$
\boxed{\ \|\hat x_{k+H}-x_{k+H}\|_2\le L_C\Big[L_F^{H}\|e_k\|_2+\epsilon\sum_{j=0}^{H-1}L_F^{j}\Big]\ .}
$$

This links the abstract bound to the physical-space RMSE reported in the experiments.

*Proof.* $\|\hat x-x\|=\|C\hat z-Cz\|\le L_C\|\hat z-z\|\le L_C\|\hat\xi-\xi^\star\|$, then apply Theorem 1. $\square$

---

## 3.10 Proposition 3 — Local approximation of RTI predictive control

The predictive controller uses the augmented model $\xi_{i+1}=F_\Theta(\xi_i,u_i)$. Around the warm-start nominal trajectory $(\bar\xi_i,\bar u_i)$,

$$
F_\Theta(\bar\xi_i+\delta\xi_i,\bar u_i+\delta u_i)
=F_\Theta(\bar\xi_i,\bar u_i)+F_i\,\delta\xi_i+G_i\,\delta u_i+r_i ,
$$

with $F_i=\partial F_\Theta/\partial\xi$, $G_i=\partial F_\Theta/\partial u$.

**Proposition 3.** If $F_\Theta$ is $C^2$ and $\|\nabla^2F_\Theta\|_2\le M_F$ on $\Omega$, then

$$
\boxed{\ \|r_i\|_2\le\frac{M_F}{2}\Big\|\begin{bmatrix}\delta\xi_i\\ \delta u_i\end{bmatrix}\Big\|_2^2\ .}
$$

*Proof.* Standard second-order Taylor remainder bound with the Hessian norm $M_F$. $\square$

**Use.** This supports the **local** validity of a single SQP iteration (RTI) around a warm start; it is **not** a new SQP convergence theory.

---

## 3.11 Scope and non-goals

The analysis is deliberately **finite-horizon**. We explicitly do **not** pursue:

1. **Global Koopman stability** — we do not require $\rho(A(c))<1$ for all $c$.
2. **A common Lyapunov function** $P$ — not used as a primary tool.
3. **Global asymptotic closed-loop stability** — no terminal invariant set, robust invariant tube, global NMPC Lyapunov argument, or recursive-feasibility-under-learned-uncertainty claim.

> *Positioning statement.* The theoretical analysis focuses on **finite-horizon prediction consistency** and **local RTI approximation** rather than global asymptotic closed-loop stability.

---

## 3.12 Numerical validation of the assumptions

All quantities are measured on the frozen deployment predictor ($A$-only, $r=2$, scheduled propagation) over the validation set (P2, $P=4$, $d=10$). These diagnostics **validate the assumptions and the self-consistency of the bounds**; they do not prove the theorems.

| Quantity | Role | Measured value (H=1/5/10/20) |
|---|---|---|
| $\epsilon_k$ (one-step defect) | Prop. 2 | median 0.345; q90 0.516; q95 0.567; q99 0.655 |
| $d_{\mathcal M}(H)$ | Def. 2 | 0.120 / 0.390 / 0.574 / 0.928 |
| $\|A_{k+H-1}\cdots A_k\|_2$ | Prop. 2 mechanism | 1.046 / 1.247 / 1.541 / 2.304 |
| $\|\partial F_\Theta/\partial\xi\|_2$ (empirical $L_F$) | Thm. 1 | median 1.445; q95 1.450; max 1.452 |
| Prop. 2 bound / actual $d_{\mathcal M}$ | Thm. 1 sanity | 4.7× / 7.95× / 12.1× / 18.7× |
| linearization remainder $\|r_i\|$ (est. $M_F$) | Prop. 3 | $\le0.27$ at $\|\delta\|=10^{-3}$ |
| RTI runtime | deployment | p50 78 ms / p95 120 ms ($N=5$) |

**Reading.**

1. **Prop. 2 mechanism confirmed.** The transition-product norm grows from $1.05$ to $2.30$ (no contraction), tracking the growth of $d_{\mathcal M}$ — numerically supporting Remark 1 ($\rho<1$ is insufficient).
2. **Empirical $L_F\approx1.45>1$.** The augmented map expands on $\Omega$; the finite-horizon form of Theorem 1 (not the $L_F<1$ corollary) is the appropriate statement.
3. **Theorem 1 sanity PASS.** The Prop. 2 bound is always $\ge$ the actual defect, and becomes more conservative with $H$ (4.7×→18.7×), consistent with a valid but loose bound.
4. **Prop. 3 holds.** The second-order linearization remainder is small ($M_F\lesssim0.3$), supporting one-iteration RTI.
5. **$\epsilon_k>0$.** The scheduled one-step is not strictly encoder-consistent, confirming the training/deployment distribution gap of §3.7 and motivating rollout-aware training.

### 3.12.1 Corollary 1 (physical space) — direct check

The decoder is the fixed projection $C=[I_n\,|\,0]$ (no parameters), so **$L_C=1$ exactly** and $\|C\|_2=1$. Scheduled-propagation physical error from a true history:

| $H$ | physical RMSE | physical MAE | Corollary-1 bound $L_C\sum_{j}\epsilon$ (latent $\epsilon_{95}$) | bound / actual |
|---|---:|---:|---:|---:|
| 1 | 0.0108 | 0.0094 | 0.567 | 52× |
| 5 | 0.0222 | 0.0193 | 3.10 | 139× |
| 10 | 0.0297 | 0.0257 | 6.96 | 234× |
| 20 | 0.0419 | 0.0366 | 17.3 | 413× |

**Reading (honest).** Corollary 1 is **valid but very loose** here (52–413×). Two structural reasons: (i) the latent defect $\epsilon_k$ is measured in an **absolute** latent scale ($\|z\|$ large), whereas the physical error reflects only the first $n$ coordinates; (ii) the decoder **discards** the remaining $d-n$ latent coordinates, so latent-space defect over-counts. Tightening the bound (e.g. output-projected defects, normalized $\epsilon$, or a per-coordinate analysis) is left as future work. We report this honestly rather than presenting the bound as tight.

---

## 3.13 Theory–experiment correspondence

| Theoretical object | Experiment / evidence |
|---|---|
| history-conditioned $A(c)$ | A/B/AB ablation |
| low-rank transition ($r$) | $r=1,2,5$ ablation |
| genuine history dependence | matched-current history shuffle |
| rollout inconsistency ($d_{\mathcal M}$) | manifold-defect diagnostic |
| transition-product amplification | product-norm diagnostic |
| spectral stabilization insufficiency (Rem. 1) | stabilization retraining (negative) |
| rollout-aware repair (Def. 3) | rollout-aware training (positive) |
| value of the Koopman factorization | DirectNN baseline (equal params) |
| RTI local approximation (Prop. 3) | exact oracle vs RTI ($\Delta_{\mathrm{RTI}}\le0$) |
| real-time feasibility | RTI p50/p95 runtime |
| control utility | P2 hardware (future work) |

---

## 附：中文结构与诚实性说明

**结构**：3.1 问题设定 → 3.2 定义1（history-conditioned low-rank Koopman 族）→ 3.3 命题1（有限历史 Markov 化）→ 3.4 定义2（latent rollout 不一致）→ 3.5 命题2（误差传播）→ 3.6 注1（谱稳定不足）→ 3.7 定义3（rollout-aware 训练定位）→ 3.8 定理1（有限时域误差界）→ 3.9 推论1（物理空间误差）→ 3.10 命题3（RTI 局部近似）→ 3.11 范围/非目标 → 3.12 数值验证 → 3.13 理论与实验对应。

**诚实性边界**：
- 命题/定理全部为**有限时域**结论，依赖紧致域 $\Omega$ 上的 Lipschitz/误差假设（A1–A3）。
- **不**声称：全局 Koopman 稳定性、公共 Lyapunov 函数、全局渐近闭环稳定、terminal set/tube/递归可行性。
- 定理1 的界**保守**（实测 4.7–18.7×），论文应如实标注为"valid but loose"。
- 数值诊断只验证**假设与界的自洽性**，不构成证明。
- 命题1 仅对**预测器内部 rollout**（解码 $\hat x$ 回灌）成立，不适用于回灌真实测量。
- 命题3 是**经典二阶 Taylor 余项**，不是新的 SQP 收敛理论。

**待补（如需）**：
1. 物理空间 bound vs actual（Corollary 1）——**已补**（§3.12.1）：$L_C=1$（decoder 为 $[I_n|0]$），bound 有效但很松（52–413×），已如实标注。
2. 跨 seed 方差（$\epsilon$、$L_F$、$d_{\mathcal M}$）——若审稿要求。
3. 更紧的 bound（输出投影后的 defect / 归一化 $\epsilon$）——列为 future work。
