# 阶段② S1 文献结构化映射（v0.1）

> 目的：为 Idea Population 提供 prior-art 与 gap 输入；不是最终文献综述，也不代表已完成穷尽检索。
> 检索时间：2026-09-28。检索工具部分结果质量不稳定，因此每条结论区分“已核实元数据”和“待阅读全文”。

## 1. Robust Koopman control / MPC

### Zhang et al., 2022, Automatica

- **Identity**: X. Zhang, W. Pan, R. Scattolini, S. Yu, X. Xu, “Robust tube-based model predictive control with Koopman operators,” *Automatica*, 137, 110114. DOI: `10.1016/j.automatica.2021.110114`.
- **Problem**: finite-dimensional Koopman model mismatch makes nominal Koopman-MPC fragile.
- **Assumptions / structure**: a finite-dimensional lifted model plus a bounded modeling-error/tube description; robust tube MPC machinery is used around the Koopman predictor.
- **Main contribution visible from metadata/title and open bibliographic record**: robust tube-based MPC specifically for Koopman operators, with robust constraint/tracking treatment.
- **Limitation relevant here**: “add tube robustness to a Koopman predictor” is already established and cannot be our sole controller novelty. Exact assumptions and theorem scope require L2 reading of arXiv:2108.13011.
- **Status for our branches**: pure C2/tube-MPC branch is **not novel enough as stated**; only survives if coupled to a genuinely new structure/obstruction and a different guarantee.

### Wang et al., 2022, CCTA

- **Identity**: “Robust Tracking Model Predictive Control with Koopman Operators,” DOI: `10.1109/ccta49430.2022.9966058`.
- **Implication**: robust tracking with Koopman models is also prior art; tracking alone is not a sufficient differentiator.

## 2. Koopman + CBF / safety

### Folkestad et al., 2021, IEEE Control Systems Letters

- **Identity**: C. Folkestad, Y. Chen, A. D. Ames, J. W. Burdick, “Data-Driven Safety-Critical Control: Synthesizing Control Barrier Functions With Koopman Operators,” *IEEE Control Systems Letters*, 5(6), 2012–2017. DOI: `10.1109/lcsys.2020.3046159`.
- **Problem**: construct safety-critical control when the system is unknown and CBF invariant-set computation is difficult.
- **Method**: learn discrete-time Koopman closed-loop dynamics, replace expensive online forward integration with lifted linear propagation, derive an error bound for unmodeled dynamics, and robustify the CBF controller.
- **Main theorem/claim visible in abstract**: safety can be guaranteed through a Koopman-based CBF construction under an error-bound treatment; demonstrated on collision avoidance for wheeled robots and quadrotors.
- **Limitation relevant here**: “Koopman + CBF + model-error bound” is directly occupied. A new paper would need a different structural source of the bound or a materially different safety theorem.
- **Status for our branches**: pure C4 is **screened out as primary novelty**; it may remain only as a downstream application of a new modeling/control structure.

### Zinage & Bakolas, 2023, ACC

- **Identity**: “Neural Koopman Control Barrier Functions for Safety-Critical Control of Unknown Nonlinear Systems,” DOI: `10.23919/acc55779.2023.10156243`.
- **Implication**: neural Koopman + CBF is also established, further increasing prior-art risk for a generic neural/Transformer Koopman-CBF combination.

## 3. Adaptive / residual Koopman control

### Singh et al., 2025, IJRR

- **Identity**: R. Singh, C. K. Sah, J. Keshavan, “Adaptive Koopman embedding for robust control of nonlinear dynamical systems,” *International Journal of Robotics Research*, 44(13), 2235–2261. DOI: `10.1177/02783649251341907`.
- **Problem**: learned Koopman embeddings generalize poorly outside training distributions and are not robust to changing dynamics/disturbances.
- **Method**: learn a nominal Koopman embedding offline, then augment it with an online neural architecture that modifies nominal dynamics from predicted/observed lifted-state deviations.
- **Main claim**: theoretical convergence guarantees for the adaptive scheme, with MPC tracking simulations across multiple robotic platforms.
- **Limitation relevant here**: online residual correction/adaptation is already a strong and recent robotics contribution. “Use observed-vs-predicted residual to adapt Koopman dynamics” is not a safe primary idea for us.
- **Status for our branches**: generic C2/C6 residual-driven adaptation is **high prior-art risk** and must be narrowed to a distinct structural theorem or killed.

### Pal & He, 2023, ACC

- **Identity**: “A Robust Dual-loop Control for Finite-dimensional Koopman Model of Nonlinear Dynamical Systems,” DOI: `10.23919/acc55779.2023.10156006`.
- **Problem**: finite-dimensional approximation and imperfect/noisy data create model mismatch.
- **Method**: robust dual-loop control with an observer-based state-feedback loop and an additional robust loop; evaluated on a bilinear motor.
- **Implication**: robust residual compensation and dual-loop ideas are also prior art. Our “physical residual loop” must not be presented as novel without a new structural obstruction and theorem.

## 4. Learned-model uncertainty / finite-data direction

### Current mapping result

- The direct search did not yet yield a verified Koopman-specific conformal-control paper with enough primary detail to support a novelty claim.
- However, conformal prediction itself has established finite-sample marginal coverage, while closed-loop use introduces distribution-shift/exchangeability questions.
- Therefore “Conformal Koopman control” remains **unknown**, not “novel”. It requires a targeted literature search and a theorem audit before surviving screening.

### Relevant adjacent signal

- “Conformant Synthesis for Koopman Operator Linearized Control Systems,” DOI: `10.1109/cdc51059.2022.9992324`, shows that formal/conformant synthesis around Koopman-linearized control systems already exists as a direction.
- This increases the need to distinguish statistical conformal coverage, formal conformant synthesis, and robust invariant-set guarantees rather than merging them under one label.

## 5. History / delay lifting

### Current mapping result

- Main34.tex cites delay/history intuition but does not yet give a theorem connecting history length `P`, latent dimension, approximate invariance, and closed-loop error.
- Existing delay-coordinate and recurrent/Koopman literature makes “use history instead of instantaneous state” a weak standalone novelty claim.
- The surviving opportunity is not history itself, but a specific **structural consequence** of history lifting that enables a new controller theorem or removes a restrictive control assumption.

## 6. Bilinear / input-dependent Koopman structures

### Current mapping result

- Input-dependent and bilinear Koopman formulations are established alternatives to constant-`B` lifted models; the current paper already cites input-aware Koopman work.
- A route that simply changes `z_{k+1}=Az_k+Bu_k` to a bilinear model is therefore not sufficient.
- The open question is whether a CCK-style structure-manufacturing transformation can make an input-dependent physical system compatible with a controller theorem that is otherwise unavailable under constant `B`.

## 7. First screening decisions

### Killed as standalone primary contributions

1. “Add robust tube MPC to Koopman.”
2. “Add CBF to Koopman.”
3. “Use residuals for adaptive Koopman.”
4. “Use history/Transformer lifting instead of instantaneous lifting.”
5. “Use bilinear Koopman instead of constant-B Koopman.”

These may be components, baselines, or implementation choices, but not the central novelty without an additional structural theorem.

### Surviving research question

The CCK-inspired pattern remains promising only in the following sharpened form:

> Identify a restrictive condition required by a useful Koopman controller theorem, show why the current physical/data-driven system violates it, construct an augmented or transformed representation that satisfies it, and prove the relation between the transformed controller and the original physical system.

Candidate obstruction to investigate first:

```text
constant-B / lifted-reference feasibility / exact tracking structure
        ↓
        reference trajectory generally outside range(B)
        ↓
        pseudoinverse feedforward leaves projection residual
        ↓
        current UUB theorem is incomplete
        ↓
        construct reference-compatible augmentation, governor, or dynamic extension
```

This is only a research hypothesis. It must pass prior-art and counterexample checks before becoming an idea node.

## 8. Next S1 action

Read the primary papers most relevant to the surviving obstruction, beginning with:

1. Zhang et al. 2022 robust tube-based Koopman MPC (arXiv:2108.13011);
2. Folkestad et al. 2021 Koopman-CBF;
3. Singh et al. 2025 adaptive Koopman embedding;
4. CCK / virtual-dynamics source paper from the project design document;
5. Korda & Mezić 2018 Koopman MPC and input-dependent/bilinear Koopman references.

For each paper, perform L2/L4 extraction and explicitly record: what theorem already covers, what it does not cover, and whether the candidate obstruction is genuinely unresolved.
