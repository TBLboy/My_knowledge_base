# -*- coding: utf-8 -*-
"""v2: apply reviewer-driven wording fixes to Introduction body (before the contributions)."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAPER = next(p for p in (ROOT / 'Transformer-Koopman' / '\u8bba\u6587').iterdir()
             if p.is_dir() and p.name != '\u8001\u7248\u672c')
src = PAPER / 'Main.tex'
raw = src.read_bytes()
bom = raw.startswith(b'\xef\xbb\xbf')
text = raw.decode('utf-8-sig')
crlf = '\r\n' in text
text = text.replace('\r\n', '\n')

START = "\\label{sec:introduction}\n% =========================================================\n\n"
END = "The contributions are as follows."
a = text.index(START) + len(START)
b = text.index(END)

NEW = r"""Model predictive control (MPC) chooses inputs by optimizing predicted behavior over a finite horizon subject to input constraints, so the prediction model determines both the quality and the computational cost of the controller. With a nonlinear model the optimization is a nonconvex program that must be solved at every sampling instant. With a linear model it is a convex quadratic program (QP), which admits fast solvers and predictable execution times \cite{wu2026multistep}. Linear identification methods \cite{ljung1999system,vanoverschee1994n4sid} supply such models but are limited in following nonlinear behavior over a wide operating range, whereas nonlinear black-box models \cite{nelles2020nonlinear,forgione2021dynonet} follow it at the price of a nonconvex control problem. A predictor that represents nonlinear dynamics and still propagates linearly would combine the two advantages.

Koopman operator theory provides a route to such a predictor \cite{koopman1931hamiltonian,mezic2005spectral}. Instead of the state, it evolves observables, that is, scalar functions of the state, and the operator that advances them is linear even when the state dynamics are not. Lifting the state into a vector of observables therefore represents nonlinear evolution as linear evolution in a higher-dimensional space; the representation is exact on a finite-dimensional invariant subspace and approximate otherwise. Extended dynamic mode decomposition (EDMD) fits such a finite-dimensional linear predictor from data \cite{williams2015data}, and dynamic mode decomposition with control and the controlled Koopman operator extend it to inputs \cite{proctor2016dmdc,proctor2018generalizing,korda2018linear}. Inside MPC, the lifted predictor yields a QP whose complexity is comparable to that of linear MPC \cite{korda2018linear}. Comprehensive accounts are given in \cite{brunton2022modern,otto2021koopman,duran2025control,strasser2026overview}.

The accuracy of the predictor depends on how the state is lifted. Early formulations fixed a dictionary of observables in advance, such as polynomials or radial basis functions, and fitted the linear matrices by least squares \cite{williams2015data,korda2018linear}. This is simple, but the representation capacity is limited and the result is sensitive to the dictionary \cite{wu2026multistep}. Neural networks later replaced the hand-chosen dictionary: the lifting and the linear dynamics are learned jointly from data \cite{lusch2018deep,takeishi2017koopman,otto2019linearly}, including for controlled systems \cite{han2020deep,feizi2025deepkoopman}. Both choices share one structure. A single pair $(\mA,\mB)$ advances the lifted state over the entire operating range, so every difference between operating conditions must be encoded in the lifted coordinates.

A single matrix pair is demanding when the measurement does not reveal the operating condition, for example with unmeasured states or varying friction and payload. A common remedy places recent history in the lifting. Time-delay observables retain past measurements as additional coordinates \cite{brunton2017chaos,kamb2020timedelay,arbabi2017ergodic,das2019delay}, and learned variants employ temporal encoders: recurrent or convolutional layers in Koopman-based MPC \cite{shenoy2025temporal,han2024robust} and Transformers in Koopman-based forecasting \cite{forootani2025deepkoopformer,forootani2026spectral}. History then enriches the lifted state, but after lifting every history is still propagated by the same transition matrix. A second remedy lets the transition itself depend on history. MamKO generates the Koopman matrices from recent data and keeps the MPC problem convex \cite{li2025mamko}, and Koopa pairs a time-invariant with a time-variant Koopman predictor for non-stationary time series \cite{liu2023koopa}.

This paper combines the two remedies. The lifted state keeps the current measurement and appends a Transformer encoding of a finite history. The transition is a shared nominal matrix plus a bounded low-rank correction generated from a history context, a feed-forward map of the recent measurements and inputs, and the input matrix is modulated by the current measurement. The history context and the current measurement act as scheduling signals, and we call the result a scheduled predictor. For fixed scheduling signals it is linear in the lifted state and input, which is the property that makes Koopman predictors usable in MPC, while the scheduling signals let the effective dynamics follow the operating condition.

Scheduling makes both prediction and control depend on history. For prediction, the history in one-step training consists of measured samples, whereas in deployment it is rebuilt from predicted measurements, so the scheduling signals are evaluated on histories that may differ from those seen in training. A one-step residual alone therefore does not determine the multi-step error: the recursion must also track the error in the history window. Error accumulation under recursive evaluation is already known for fixed-matrix Koopman predictors \cite{wu2026multistep}. We define the recursive window update explicitly and bound the open-loop prediction error over a finite horizon.

For control, recomputing the scheduling from the predicted trajectory makes the matrices depend on the decision variables, so the finite-horizon problem is in general nonconvex. Freezing the scheduling matrices along a nominal rollout gives a linear time-varying (LTV) model and a convex QP under polyhedral input constraints. This is related to gain scheduling and quasi-linear parameter-varying control, where a linear model is indexed by a scheduling signal \cite{rugh2000gain,leith1998velocity,cisneros2016qlmpc,cisneros2020qlpv}. It differs from real-time iteration, which performs a single sequential-quadratic-programming update on the nonlinear problem \cite{diehl2005realtime,gros2020rti}, and from advanced-step NMPC, which corrects a precomputed nonlinear solution by sensitivity updates \cite{zavala2009advancedstep}. Here the nominal rollout is itself history-aware, and we bound the deviation of the frozen trajectory from the complete scheduled trajectory for the same input sequence.

"""
text = text[:a] + NEW + text[b:]
if crlf:
    text = text.replace('\n', '\r\n')
src.write_bytes((b'\xef\xbb\xbf' if bom else b'') + text.encode('utf-8'))
print('ok')
