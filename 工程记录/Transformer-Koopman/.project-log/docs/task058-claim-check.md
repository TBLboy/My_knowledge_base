# TASK-058 Introduction claim-to-source check (main agent, network pages read 2026-10-13)

| Intro claim | Source | Evidence read |
|---|---|---|
| QP admits fast solvers / predictable execution times | wu2026multistep (arXiv 2601.11901 HTML, Sec.1) | "QPs admit fast numerical solution methods ... allow execution-time-certified computation" |
| fixed dictionary: limited capacity, sensitive to dictionary | wu2026multistep Sec.1.1 | "limited representation capacity and sensitivity to the choice of nonlinear observable dictionary" |
| error accumulation under recursive evaluation, fixed matrix | wu2026multistep Sec.1.1/3 | one-step EDMD accumulates error over horizon |
| lifted predictor gives QP comparable to linear MPC | korda2018linear (arXiv 1611.03537) | "computational complexity ... comparable to that of MPC for a linear dynamical system" |
| dictionary fixed in advance (polynomials, RBF), least squares | williams2015data, korda2018linear; wu2026 Sec.2.1 ("predefined basis, e.g. radial basis functions used in Korda") | read |
| MamKO generates Koopman matrices from historical data, MPC convex | li2025mamko (ICLR 2025 PDF text via search) | "generates Koopman operators from online data ... matrices generated from historical data ... MPC convex" |
| Koopa: time-invariant + time-variant Koopman predictor, non-stationary series | liu2023koopa (arXiv 2305.18803 abstract/TOC) | abstract read |
| DeepKoopFormer / Learnable: Transformers in Koopman forecasting | forootani2025deepkoopformer (arXiv 2508.02616), forootani2026spectral (2602.02592) | abstracts read: Transformer encoder + linear Koopman propagator; NOT described as history-dependent transition |
| temporal encoders in Koopman MPC (TCN/LSTM/GRU) | shenoy2025temporal (ACC 2025) | abstract: TCN, LSTM, GRU temporal layers in autoencoder, Koopman MPC |
| han2024robust recurrent Koopman, time-delay systems, control | title/venue (TII 2024); full text not read | title only |
| han2020deep / feizi2025deepkoopman controlled learned lifting | titles/venues; abstract of feizi not re-read | title only |

Removed from earlier text: Wu 2026 as "learned neural predictor" (not present); DeepKoopFormer as context-dependent transition (not present).
Unverified: full text of han2024robust, han2020deep, feizi2025deepkoopman, brunton/kamb/arbabi/das (classical, well known).
