# B1 理论先行数学设计：原始资料合订本

## 1. 目标与精确问题

[确认] 按用户要求，将当前磁盘最新版Main.tex及指定五份原始报告全文合并成一个Markdown，供外部GPT逐行推导完整定理和证明。不是另一份进展摘要，不需要另上传ZIP。

## 2. 背景与阅读顺序

[确认] 外部GPT已读此前简报，本合订本不从零介绍项目。建议先读Main.tex，再读总证书图；然后核对联合安全/移位、联合残差预算、完整动力学及直接编码缺陷。

[确认] Main.tex来自生成时的当前工作目录，含原有未提交修改，不是从10月15日历史提交提取。其源文件修改时间可能早于今天，“最新版”不表示理论报告已全部写回论文。

## 3. 预期与实际状态

[确认] 当前目标为理论先行数学设计：先确立模型需满足的条件，再讨论网络架构、训练约束与控制实现。现有报告给出了条件递归可行性构造与解析判据，并非某个训练模型全部前提的联合认证。

[未知] 固定模型平衡点、PBH、实际初始化、统一输出误差及全域预算尚未认证。B1整体OPEN，P5正式稳定性阶段STOP；没有物理plant稳定性或实时性结论。论文旧实验文字/数字不是本次核验结果。

## 4. 原始证据与快照清单

[确认] 下表给来源相对路径、原始字节SHA256、行数及源文件本地修改时间。附录逐份完整收录，只统一CRLF/LF换行，不改写正文、不插入行号。哈希对应原始字节；同时另做LF规范化后的全文一致性和源文件未变检查。

生成时间：2026-10-18T21:44:45.995440+08:00

|序号|来源|行数|原始字节SHA256|源文件本地修改时间|
|---|---|---:|---|---|
|1|`Transformer-Koopman/论文/新版本/Main.tex`|932|`1ee01187dfdad058746fe9fb3e2489c467b96de09ead0ef67be7a3f2855aee69`|2026-10-16T21:57:36.520097+08:00|
|2|`.project-log/docs/ClosedLoop_A1_B1_Integrated_Certificate_Map.md`|107|`4c57695eaab475dc90b1b2f95d18e4628e9a596c1b8deabca1f3997b5be47574`|2026-10-18T20:23:46.207167+08:00|
|3|`.project-log/docs/ClosedLoop_A1_B1_Joint_Safety_Shift_Certificate.md`|124|`c73d1142d540472778ee66fea11f44182f92a326c2a79e85ec43c2af0fadd5cb`|2026-10-18T20:18:33.098791+08:00|
|4|`.project-log/docs/ClosedLoop_A1_B1_Joint_Residual_Radius_Budget.md`|156|`0ec2c65d36e929ec4e754950f7bb30677d1cfc3cb60301128958ea24154cf919`|2026-10-18T20:46:17.446537+08:00|
|5|`.project-log/docs/ClosedLoop_A1_B1_Explicit_Dynamics_Jacobian_Derivation.md`|303|`da4c738d058865054e8089773e358f0afa5bcd6812d434e944ede776353800e8`|2026-10-18T19:49:45.158803+08:00|
|6|`.project-log/docs/ClosedLoop_A1_B1_Direct_Encoded_Defect_Certificate.md`|111|`3d3ab217ea47098025bb80966804ec57930548d4c3328bb54a306cfa37d3a000`|2026-10-18T21:02:34.879087+08:00|

## 5. 环境、接口与允许修改的范围

[确认] 本次仅整理UTF-8文本，不编译LaTeX、不读取checkpoint、不跑数值实验、不附现有控制器代码或数据。保留一次名义full rollout、一次冻结、一次凸QP的研究边界。当前输入独立于过去输入窗口；绝对输入增量成本不是硬增量约束。

**哪些公式允许修改？** 本次没有批准改动任何论文公式或原始报告。外部GPT可在独立答复中提出理论设计、模型条件及公式替换建议，须标为“设计建议”，注明原label、修改理由、影响和代价，不得说成已获批准或已实施。论文、代码、控制器原件均保持不动；实验与图片继续冻结。不擅自更改章节、编号和引用接口。

## 6. 已有工作与观察结果

[确认] 总证书图整理条件递归可行性主链；联合安全报告处理域、阶段shift及种子；联合预算比较残差、终端半径与初始化；完整动力学报告保留context及B(x)的状态导数；直接缺陷报告保留编码图导数抵消。

[条件] 各报告PROVED/CONDITIONAL/go限其明确前提和文档范围。原文保留历史状态，“下一门槛”可能已被后续材料部分推进；冲突应指出而非默默合并。本次不重新背书全部历史证据绑定。

## 7. 未知与请求外部GPT解决的问题

[求助] 请逐行检查模型、成本、理论边界及证明量词：Frozen-tail误差入口、非循环域闭合、任意新QP可行解保护、实际编码初始化和统一残差是否有遗漏。随后给完整定理证明或精确障碍，区分已推出性质、必要模型条件、设计选择与需要外部误差证据的量。

不需要从零介绍项目，不需要checkpoint、数值实验或现有控制器代码。不能把“存在终端集/每步可行/持续Slater”作为未构造前提完成证明。模型可稳定化不等于物理plant稳定。架构/训练/成本/实现变更先作为方案，不把当前实验代码自动视为不可改变的理论规范。

本次只包含指定六份材料；其中引用的其他报告未全部展开，若某一步依赖缺失原文，请明确索取，不虚构引用内容。

---
# 附录：六份原始材料全文

## 原始材料 1：Main.tex

来源：`Transformer-Koopman/论文/新版本/Main.tex`

````latex
% XeTeX/Tectonic has no TU/ptm definition; map IEEEtran's Times (ptm) to TeX Gyre Termes.
% Must precede \documentclass because IEEEtran selects its font while loading.
\ifdefined\XeTeXversion
  \DeclareFontFamily{TU}{ptm}{}
  \DeclareFontShape{TU}{ptm}{m}{n}{<->"[texgyretermes-regular.otf]:mapping=tex-text"}{}
  \DeclareFontShape{TU}{ptm}{m}{it}{<->"[texgyretermes-italic.otf]:mapping=tex-text"}{}
  \DeclareFontShape{TU}{ptm}{bx}{n}{<->"[texgyretermes-bold.otf]:mapping=tex-text"}{}
  \DeclareFontShape{TU}{ptm}{bx}{it}{<->"[texgyretermes-bolditalic.otf]:mapping=tex-text"}{}
  \DeclareFontShape{TU}{ptm}{b}{n}{<->ssub*ptm/bx/n}{}
  \DeclareFontShape{TU}{ptm}{b}{it}{<->ssub*ptm/bx/it}{}
  \DeclareFontShape{TU}{ptm}{m}{sl}{<->ssub*ptm/m/it}{}
  \DeclareFontShape{TU}{ptm}{bx}{sl}{<->ssub*ptm/bx/it}{}
  \DeclareFontShape{TU}{ptm}{m}{sc}{<->"[texgyretermes-regular.otf]:mapping=tex-text;+smcp"}{}
\fi
\documentclass[journal]{IEEEtran}

\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\usepackage{booktabs}
\usepackage{multirow}
\ifdefined\XeTeXversion\else
  \usepackage[utf8]{inputenc}
  \usepackage[T1]{fontenc}
\fi
\usepackage{microtype}
\usepackage{array}
\usepackage{amsthm}
\usepackage{algorithm}
\usepackage{float}
\usepackage{algorithmic}
\usepackage[hidelinks]{hyperref}

\newtheorem{assumption}{Assumption}
\newtheorem{definition}{Definition}
\newtheorem{theorem}{Theorem}
\newtheorem{proposition}{Proposition}
\newtheorem{corollary}{Corollary}
\newtheorem{lemma}{Lemma}
\newtheorem{remark}{Remark}

\interdisplaylinepenalty=2500
\emergencystretch=2em

\newcommand{\vq}{\mathbf{q}}
\newcommand{\vphi}{\boldsymbol{\phi}}
\newcommand{\vp}{\mathbf{p}}
\newcommand{\vb}{\mathbf{b}}
\newcommand{\vrho}{\mathbf{r}}
\newcommand{\vpout}{\mathbf{p}}
\newcommand{\vx}{\mathbf{x}}
\newcommand{\vu}{\mathbf{u}}
\newcommand{\vs}{\mathbf{s}}
\newcommand{\vz}{\mathbf{z}}
\newcommand{\vc}{\mathbf{c}}
\newcommand{\ve}{\mathbf{e}}
\newcommand{\vr}{\mathbf{r}}
\newcommand{\vg}{\mathbf{g}}
\newcommand{\mH}{\mathbf{H}}
\newcommand{\mA}{\mathbf{A}}
\newcommand{\mB}{\mathbf{B}}
\newcommand{\mC}{\mathbf{C}}
\newcommand{\mD}{\mathbf{D}}
\newcommand{\mF}{\mathbf{F}}
\newcommand{\mG}{\mathbf{G}}
\newcommand{\mQ}{\mathbf{Q}}
\newcommand{\mR}{\mathbf{R}}
\newcommand{\mP}{\mathbf{P}}
\newcommand{\mU}{\mathbf{U}}
\newcommand{\mV}{\mathbf{V}}
\newcommand{\mW}{\mathbf{W}}
\newcommand{\mX}{\mathbf{X}}
\newcommand{\mZ}{\mathbf{Z}}
\newcommand{\mI}{\mathbf{I}}
\newcommand{\mTheta}{\boldsymbol{\Theta}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\norm}[1]{\left\lVert #1\right\rVert}
\newcommand{\argmin}{\mathop{\mathrm{arg\,min}}}
% Placeholder frame for a figure to be drawn later: \figph{width}{height}{description}
\newcommand{\figph}[3]{\fbox{\parbox[c][#2][c]{\dimexpr#1-2\fboxsep-2\fboxrule\relax}{\centering\small #3}}}

\begin{document}

\title{Transformer--Koopman: History-Conditioned Scheduled Prediction and Frozen-LTV Model Predictive Control}
\author{Bolin Tao}
\markboth{IEEE Journal Draft}{Tao: Transformer--Koopman}
\maketitle

\begin{abstract}
Koopman-inspired predictors provide a structured representation of nonlinear dynamics by evolving observables through finite-dimensional linear maps. A fixed lifted transition, however, can be restrictive when the measured state does not determine the relevant operating condition. This paper develops a history-conditioned scheduled predictor in which a temporal lifting map is complemented by a context-dependent low-rank transition and a measurement-dependent input modulation. The transition and input matrices are bounded functions of a history context and the current lifted measurement, respectively. For fixed scheduling signals the predictor is linear in the lifted state and input, while recursive scheduling remains generally nonlinear. Under common-history, work-domain, Lipschitz, and one-step residual conditions, we derive a finite-horizon open-loop prediction bound. For control, a nominal rollout supplies scheduling matrices that are frozen over the horizon, yielding an LTV prediction model and a convex quadratic program under polyhedral input constraints. We further derive a finite-horizon bound between the complete scheduled model and its frozen approximation, and state a conditional cost-suboptimality result relative to the global optimum of the complete problem.
\end{abstract}

\begin{IEEEkeywords}
Koopman modeling, temporal lifting, scheduled prediction, low-rank modulation, LTV-MPC, model predictive control.
\end{IEEEkeywords}

% =========================================================
\section{Introduction}
\label{sec:introduction}
% =========================================================

Accurate multi-step prediction is central to model-based control of nonlinear dynamical systems. In many applications, however, the available measurements do not uniquely determine the underlying physical state. Similar measurements can therefore be followed by different responses to the same control input, depending on the preceding evolution of the system. Using a history of measurements and inputs can help distinguish these situations. For model predictive control (MPC), the resulting predictor must also support repeated rollouts and optimization over a finite horizon \cite{ljung1999system,nelles2020nonlinear,forgione2021dynonet}.

Koopman-based modeling offers a way to combine nonlinear system representations with structured prediction. The Koopman operator describes the evolution of functions of the system state, known as observables, through a linear action, even when the underlying dynamics are nonlinear \cite{koopman1931hamiltonian,mezic2005spectral,brunton2022modern}. Because this representation is generally infinite-dimensional, practical methods approximate it in a finite set of lifted coordinates. Examples include extended dynamic mode decomposition and lifted predictors incorporating control inputs \cite{williams2015data,proctor2016dmdc,korda2018linear}. Neural Koopman approaches further learn the lifted coordinates from data \cite{takeishi2017koopman,lusch2018deep,otto2019linearly,han2020deep}. Their usefulness for multi-step prediction depends on how well the lifted coordinates capture the relevant dynamics and how accurately the finite-dimensional evolution model propagates them.

One line of research incorporates temporal information into the lifted representation. Delay-coordinate methods use past measurements to construct observables \cite{kamb2020timedelay,das2019delay}, while recurrent encoders and Transformer-based models learn features from observation histories \cite{han2024robust,shenoy2025temporal,forootani2025deepkoopformer}. A complementary line adapts the evolution model to the observed context. Koopa employs context-dependent operators for time-series forecasting \cite{liu2023koopa}, and MamKO generates Koopman matrices from recent data for prediction and control \cite{li2025mamko}. These developments make it possible to use history both to represent the system and to adjust its predicted dynamics. In a controlled recursive rollout, however, future histories contain predicted measurements and candidate inputs. The evolution matrices can then change with the trajectory being predicted. This coupling affects the propagation of prediction errors and makes direct MPC optimization with the fully scheduled model generally nonlinear. The central problem considered here is how to retain history-dependent dynamics while obtaining an analyzable multi-step predictor and a tractable MPC formulation.

We address this problem with a history-conditioned, Koopman-inspired predictor and a frozen linear time-varying (LTV) MPC formulation. A temporal Transformer extracts lifted features from a finite measurement history, while the current measurement is retained explicitly in the lifted state. A separate network uses past measurements and inputs to schedule the lifted transition matrix; the input matrix is modulated by the current measured coordinates. Both matrices are expressed as nominal matrices with bounded low-rank corrections. We analyze recursive prediction with histories updated from the model outputs and derive a finite-horizon error bound that accounts for history-dependent scheduling. For control, scheduling matrices are evaluated along a nominal rollout and held fixed during each optimization. This produces an LTV prediction model whose quadratic tracking objective and polyhedral input constraints lead to a convex quadratic program. We also bound the discrepancy introduced by freezing the matrices and derive a conditional bound on the resulting control-cost suboptimality.

The main contributions are as follows:
\begin{enumerate}
    \item \emph{History-conditioned lifted prediction:} We construct a measurement-preserving temporal lifting and a scheduled predictor with bounded low-rank modulation of the transition and input matrices.
    \item \emph{Finite-horizon prediction analysis:} We define a recursive rollout with updated measurement and input histories and derive an error bound that incorporates the effect of prediction errors on subsequent matrix scheduling.
    \item \emph{Frozen-LTV predictive control:} We formulate a nominal-trajectory-based convex QP for MPC and establish bounds on the frozen-schedule prediction discrepancy and conditional control-cost suboptimality.
\end{enumerate}

The remainder of this paper is organized as follows. Section~\ref{sec:prelim} states the prediction and control problems. Section~\ref{sec:model} presents the predictor and its error analysis. Section~\ref{sec:control} develops frozen-LTV MPC and the associated approximation bounds. Sections~\ref{sec:experiments} and~\ref{sec:conclusion} present the experimental protocol and conclusions, respectively. Fig.~\ref{fig:overview} shows the overall framework.

\begin{figure*}[!t]
\centering
\figph{\textwidth}{5.6cm}{\textbf{[Placeholder] Overall framework.}\\[2pt]
Left to right: measurement window $\mX_k$ and past-input window $\mU_k^{\mathrm{in}}$ $\rightarrow$ Transformer lifting $g_\theta$ and context map $C_\phi$ $\rightarrow$ lifted state $\vz_k$ and history context $\vc_k$ $\rightarrow$ scheduled matrices $\mA(\vc_k)$, $\mB(\vx_k)$ with nominal $\mA_0$, $\mB_0$ and low-rank corrections $\rightarrow$ $\vz_{k+1}=\mA(\vc_k)\vz_k+\mB(\vx_k)\vu_k$ and readout $\vx=C_x\vz$.\\[2pt]
Lower branch: nominal rollout $\rightarrow$ frozen $\bar\mA_i$, $\bar\mB_i$ $\rightarrow$ convex QP in measurement space $\rightarrow$ input sequence $U$.}
\caption{Overall framework of the history-conditioned scheduled predictor and the frozen-LTV controller. (Placeholder; figure to be drawn.)}
\label{fig:overview}
\end{figure*}

% =========================================================
\section{Preliminaries and Problem Formulation}
\label{sec:prelim}
% =========================================================

In this section, we introduce the controlled Koopman representation and formulate the finite-history prediction problem.

% ---------------------------------------------------------
\subsection{Koopman Modeling and Temporal Lifting}
\label{subsec:koopman_prelim}
% ---------------------------------------------------------

Consider a discrete-time nonlinear controlled system
\begin{equation}
    \vs_{k+1} = f(\vs_k, \vu_k),
    \label{eq:nonlinear_system}
\end{equation}
where $\vs_k \in \mathcal S\subseteq\mathbb{R}^{n_s}$ is the physical state, $f:\mathcal S\times\mathbb R^m\to\mathcal S$ is the state transition, and $\vu_k \in \mathbb{R}^{m}$ is the control input. The available measurement is
\begin{equation}
    \vx_k = h(\vs_k) \in \mathbb{R}^{n},
    \label{eq:measurement_map}
\end{equation}
where $h:\mathcal S\to\mathbb R^n$ is the measurement map. The predictor is learned from measured input--output data without access to the physical state.

For a fixed input $\vu$, the controlled Koopman operator acts on an observable $\varphi:\mathcal S\to\mathbb R$ as \cite{koopman1931hamiltonian,mezic2005spectral,brunton2022modern}
\begin{equation}
    (\mathcal{K}_{\vu}\varphi)(\vs) = \varphi(f(\vs,\vu)).
    \label{eq:koopman_operator}
\end{equation}
The operator is linear with respect to observables:
\begin{equation}
    \mathcal{K}_{\vu}(\alpha \varphi + \beta \psi)
    = \alpha \mathcal{K}_{\vu}\varphi + \beta \mathcal{K}_{\vu}\psi.
    \label{eq:koopman_linearity}
\end{equation}

Finite-dimensional Koopman models approximate this evolution using a selected set of observables. Since only $\vx=h(\vs)$ is measured, we construct instantaneous observables from $\vx$; each component $g_j(\vx)$ corresponds to the physical-state observable $g_j\circ h$. An instantaneous lifting map takes the form
\begin{equation}
    \vz_k = g(\vx_k) = [g_1(\vx_k),\ldots,g_d(\vx_k)]^\top\in\mathbb R^d,
    \label{eq:instantaneous_lifting}
\end{equation}
with the input-affine lifted approximation
\begin{equation}
    \vz_{k+1}\approx\mA\vz_k+\mB\vu_k.
    \label{eq:linear_lifted}
\end{equation}
Here $\mA\in\mathbb R^{d\times d}$ approximates the evolution of the selected observables, and $\mB\in\mathbb R^{d\times m}$ represents the control-input contribution. Together they define a finite-dimensional controlled prediction model in the chosen lifted coordinates.

To incorporate temporal information, we define the measurement-history window
\begin{equation}
    \mX_k = [\vx_{k-P+1}^\top,\ldots,\vx_k^\top]^\top\in\mathbb R^{Pn},\qquad P\ge2,
    \label{eq:measurement_window}
\end{equation}
and extend the lifting map to
\begin{equation}
    \vz_k=g_\theta(\mX_k)=
    \begin{bmatrix}\vx_k\\\psi_\theta(\mX_k)\end{bmatrix}
    \in\mathbb R^d,\qquad d=n+n_\psi,
    \label{eq:state_preserving_lifting}
\end{equation}
where $\psi_\theta:\mathbb R^{Pn}\to\mathbb R^{n_\psi}$ learns history-dependent lifted features. Retaining the current measurement gives the fixed readout
\begin{equation}
    \vx_k=C_x\vz_k,\qquad C_x=[I_n\;0]\in\mathbb R^{n\times d}.
    \label{eq:state_readout}
\end{equation}
This representation incorporates recent measurements into the lifted state. The transition model is scheduled by recent input--output history, while the input matrix is modulated by the current measurement, as developed in Section~\ref{sec:model}.

% ---------------------------------------------------------
\subsection{Learning Problem and Design Objectives}
\label{sec:problem}
% ---------------------------------------------------------

The available training data comprise measured input--output trajectories
\begin{equation}
    \mathcal{D}=\{\tau^{(j)}\}_{j=1}^{N_{\mathrm{tr}}},\qquad
    \tau^{(j)}=\{(\vx_t^{(j)},\vu_t^{(j)})\}_{t=0}^{T_j}.
    \label{eq:trajectory_dataset}
\end{equation}
Here $N_{\mathrm{tr}}$ is the number of training trajectories, $j$ indexes the trajectories, and $T_j$ is the final recorded time index of trajectory $j$. For each admissible index $k$, the measurement history $\mX_k$ is defined in \eqref{eq:measurement_window}, and the past-input history is
\begin{equation}
    \mU_k^{\mathrm{in}}=[\vu_{k-P+1}^\top,\ldots,\vu_{k-1}^\top]^\top
    \in\mathbb R^{(P-1)m}.
    \label{eq:history_windows}
\end{equation}
The current input $\vu_k$ is applied after the observed history window and enters the one-step predictor separately.

Given the measured history $\mX_k$, the past-input history $\mU_k^{\mathrm{in}}$, and a future control sequence $\vu_{k:k+H-1}$, the objective is to predict the future measurements $\vx_{k+1},\ldots,\vx_{k+H}$ over a horizon of $H$ steps. The predictor should capture temporal information from the observed history, account for history-dependent variations in the lifted dynamics, and maintain prediction accuracy during recursive multi-step rollout.

The proposed model and its training procedure are developed in Section~\ref{sec:model}.

% =========================================================

\section{Scheduled Koopman Modeling}
\label{sec:model}

In this section, we construct the history-conditioned predictor using a temporal lifting and scheduled low-rank dynamics, describe its two-stage training procedure, and establish a finite-horizon prediction-error bound.

\subsection{Temporal Lifting and Scheduled Low-Rank Dynamics}
\label{sec:temporal_lifting}

Given the measurement history $\mX_k\in\R^{Pn}$ in \eqref{eq:measurement_window}, we reshape it into a $P\times n$ array and divide it into $N_p=P/p$ non-overlapping patches of length $p$, assuming that $p$ divides $P$. The $j$th patch is vectorized and mapped to a token through a shared linear embedding:
\begin{align}
    \vq_k^{(j)}&=\operatorname{vec}(\mX_k^{(j)})\in\R^{pn},
    \label{eq:patch_vec}\\
    \vphi_k^{(j)}&=\mW_p\vq_k^{(j)}+\vb_p,
    \label{eq:patch_embedding}
\end{align}
where $\mW_p\in\R^{d_{\mathrm{model}}\times pn}$ and $\vb_p\in\R^{d_{\mathrm{model}}}$. The resulting $N_p$ tokens retain the local measurements while reducing the sequence length from $P$ to $N_p$.

Sinusoidal positional encodings \cite{vaswani2017attention} are added before the tokens pass through an $L_T$-layer Transformer encoder:
\begin{equation}
    \mH_k=\operatorname{TransformerEncoder}\!\left(
        \{\vphi_k^{(j)}+\vp^{(j)}\}_{j=1}^{N_p}\right).
    \label{eq:transformer_enc}
\end{equation}
The output $\mH_k\in\R^{N_p\times d_{\mathrm{model}}}$ contains the contextualized patch features, with $\mH_k^{(j)}\in\R^{d_{\mathrm{model}}}$ denoting its $j$th row. The vector $\vp^{(j)}\in\R^{d_{\mathrm{model}}}$ is the positional encoding of patch $j$. Mean pooling followed by a linear projection gives
\begin{equation}
    \boldsymbol{\rho}_k=\frac{1}{N_p}\sum_{j=1}^{N_p}\mH_k^{(j)}.
    \label{eq:history_pooling}
\end{equation}
\begin{equation}
    \psi_\theta(\mX_k)=\mW_h\boldsymbol{\rho}_k+\vb_h.
    \label{eq:history_feature}
\end{equation}
where $\boldsymbol{\rho}_k\in\R^{d_{\mathrm{model}}}$, $\mW_h\in\R^{n_\psi\times d_{\mathrm{model}}}$, and $\vb_h\in\R^{n_\psi}$. The measurement-preserving lifted state is then given by \eqref{eq:state_preserving_lifting}, with $\psi_\theta(\mX_k)$ as its history feature and $C_x$ as the fixed readout in \eqref{eq:state_readout}.

\begin{definition}[History-Conditioned Scheduled Koopman Predictor]
\label{def:scheduled_lowrank_predictor}
For the histories $(\mX_k,\mU_k^{\mathrm{in}})$, let
\begin{equation}
    \vc_k=C_\phi(\mX_k,\mU_k^{\mathrm{in}})\in\R^{d_c},
    \label{eq:history_context}
\end{equation}
where $C_\phi:\R^{Pn+(P-1)m}\to\R^{d_c}$ maps the measurement and past-input histories to a context vector. The lifted predictor is
\begin{equation}
    \vz_{k+1}=\mA(\vc_k)\vz_k+\mB(\vx_k)\vu_k,
    \label{eq:scheduled_predictor}
\end{equation}
with scheduled matrices
\begin{align}
    \mA(\vc)&=\mA_0+\mU_A\operatorname{diag}(\gamma_A(\vc))\mV_A^\top,
    \label{eq:transition_schedule}\\
    \mB(\vx)&=\mB_0+\mU_B\operatorname{diag}(\gamma_B(\vx))\mV_B^\top.
    \label{eq:low_rank_schedules}
\end{align}
Here $\mA_0\in\R^{d\times d}$ and $\mB_0\in\R^{d\times m}$ are the nominal transition and input matrices. The factor pairs $(\mU_A,\mV_A)$ and $(\mU_B,\mV_B)$ specify the directions of their respective low-rank corrections, while $\gamma_A:\R^{d_c}\to\R^{r_A}$ and $\gamma_B:\R^n\to\R^{r_B}$ determine the correction coefficients. Specifically, $\mU_A,\mV_A\in\R^{d\times r_A}$, $\mU_B\in\R^{d\times r_B}$, and $\mV_B\in\R^{m\times r_B}$, so that $\operatorname{rank}[\mA(\vc)-\mA_0]\le r_A$ and $\operatorname{rank}[\mB(\vx)-\mB_0]\le r_B$.
\end{definition}

The low-rank factors define the correction directions, and the coefficient maps assign their strengths for each scheduling signal. We parameterize these coefficients using bounded signed activations and normalized weights:
\begin{align}
    \pi_A(\vc)&=\operatorname{softmax}(W_A^\pi\vc+b_A^\pi),
    \label{eq:A_modulation}\\
    \gamma_{A,j}(\vc)&=g_A\pi_{A,j}(\vc)\tanh([W_A\vc+b_A]_j),
    \label{eq:A_modulation_coefficients}\\
    \pi_B(\vx)&=\operatorname{softmax}(W_B^\pi\vx+b_B^\pi),\\
    \gamma_{B,j}(\vx)&=g_B\pi_{B,j}(\vx)\tanh([W_B\vx+b_B]_j).
\end{align}
Here $j=1,\ldots,r_A$ for the $A$-schedule and $j=1,\ldots,r_B$ for the $B$-schedule. The gains $g_A,g_B\ge0$ bound the total coefficient magnitudes; the softmax weights distribute each gain across the low-rank directions, and $\tanh$ allows signed adjustments. The modulation parameters satisfy $W_A,W_A^\pi\in\R^{r_A\times d_c}$, $W_B,W_B^\pi\in\R^{r_B\times n}$, with biases $b_A,b_A^\pi\in\R^{r_A}$ and $b_B,b_B^\pi\in\R^{r_B}$.

To establish bounds on these scheduled matrices, let $u_{A,j},v_{A,j},u_{B,j},v_{B,j}$ denote the respective columns of $\mU_A,\mV_A,\mU_B,\mV_B$ and assume
\begin{equation}
    \norm{u_{A,j}}_2,\ \norm{v_{A,j}}_2,\
    \norm{u_{B,j}}_2,\ \norm{v_{B,j}}_2\le1.
    \label{eq:factor_norm_assumption}
\end{equation}
This factor condition and the bounded coefficients give the following uniform matrix bounds, which are used in the finite-horizon prediction and freezing analyses.
\begin{proposition}[Uniform Modulation Bounds]
\label{prop:modulation_bound}
For all $\vc\in\R^{d_c}$ and $\vx\in\R^n$,
\begin{equation}
    \norm{\mA(\vc)-\mA_0}_2\le g_A,\qquad
    \norm{\mB(\vx)-\mB_0}_2\le g_B.
    \label{eq:modulation_bound}
\end{equation}
\end{proposition}
\begin{proof}
By the rank-one decomposition and the factor bounds,
$\norm{\mA(\vc)-\mA_0}_2\le\sum_j|\gamma_{A,j}(\vc)|\le g_A$,
since $\sum_j\pi_{A,j}(\vc)=1$ and $|\tanh(\cdot)|\le1$. The proof for $\mB$ is identical.
\end{proof}

The variation of the matrices with their scheduling arguments is also bounded. For finite modulation-layer weights, define
\begin{align}
    L_A&=g_A\left(\norm{W_A}_2+\frac{\sqrt{r_A}}{2}\norm{W_A^\pi}_2\right),
    \label{eq:transition_Lipschitz_constant}\\
    L_B&=g_B\left(\norm{W_B}_2+\frac{\sqrt{r_B}}{2}\norm{W_B^\pi}_2\right).
    \label{eq:Lipschitz_constants}
\end{align}
Using the $1$-Lipschitz property of $\tanh$ and the Euclidean $1/2$-Lipschitz bound for softmax yields
\begin{equation}
    \begin{aligned}
    \norm{\mA(\vc)-\mA(\vc')}_2&\le L_A\norm{\vc-\vc'}_2,\\
    \norm{\mB(\vx)-\mB(\vx')}_2&\le L_B\norm{\vx-\vx'}_2.
    \end{aligned}
    \label{eq:schedule_lipschitz}
\end{equation}
These constants quantify the schedule variations that enter the recursive prediction-error bound.

\subsection{Two-Stage Training and Recursive Prediction}
\label{sec:training}

The predictor consists of the lifting encoder $g_\theta$, the context map $C_\phi$, and the dynamics parameters $(\mA_0,\mB_0,\mU_A,\mV_A,\mU_B,\mV_B,\gamma_A,\gamma_B)$, with the fixed projection $C_x$. Training proceeds in two stages: nominal one-step pretraining followed by scheduled-rollout fine-tuning, which accounts for the shift from measured-history conditioning during initialization to predicted-history conditioning during recursive deployment.

For a rollout horizon $H_R$, each training sample comprises the measured histories $(\mX_k,\mU_k^{\mathrm{in}})$, the future input sequence $(\vu_k,\ldots,\vu_{k+H_R-1})$, and the corresponding measured-state targets $(\vx_{k+1},\ldots,\vx_{k+H_R})$, all drawn from the same trajectory.

For each available measured window, define the reference lifted state $\vz_t^{\mathrm{enc}}=g_\theta(\mX_t)$. Stage~0 uses $t=k+1$ for $k\in\mathcal I_1$; Stage~1 uses $t=k+i$ for $k\in\mathcal I_R$ and $i=1,\ldots,H_R$, within the same trajectory. At each parameter update, the shared encoder recomputes these references from measured histories, and their values are held fixed during that update. The predictive branch remains trainable.

\textbf{Stage~0 (nominal one-step pretraining).} We initialize the encoder $g_\theta$ and the time-invariant base matrices $(\mA_0,\mB_0)$ using the nominal prediction $\tilde\vz_{k+1}^{0}=\mA_0\vz_k+\mB_0\vu_k$, where $\vz_k=g_\theta(\mX_k)$, by minimizing the joint one-step measurement and lifted-state prediction error,
\begin{equation}
    \begin{aligned}
    \mathcal L_{\mathrm{init}}
    &=\sum_{k\in\mathcal I_1}\bigl[
    \norm{C_x\tilde\vz_{k+1}^{0}-\vx_{k+1}}_2^2\\
    &\qquad+\lambda_0\norm{\tilde\vz_{k+1}^{0}-\vz_{k+1}^{\mathrm{enc}}}_2^2\bigr],
    \end{aligned}
    \label{eq:training_one_step_objects}
\end{equation}
where $\lambda_0>0$ and $\mathcal I_1$ indexes the available one-step training pairs. This loss jointly initializes $g_\theta$, $\mA_0$, and $\mB_0$ by supervising both the measurement and the complete lifted state.

\begin{definition}[Rollout-Aware Scheduled Objective]
\label{def:rollout_aware}
Starting from $\vz_{k|k}^{P}=g_\theta(\mX_k)$ and the observed histories $\hat{\mX}_{k|k}=\mX_k$, $\hat{\mU}_{k|k}^{\mathrm{in}}=\mU_k^{\mathrm{in}}$, the scheduled rollout is generated for $i=0,\ldots,H_R-1$ by
\begin{align}
    \vc_{k+i|k}^{P}&=C_\phi(\hat{\mX}_{k+i|k},\hat{\mU}_{k+i|k}^{\mathrm{in}}),
    \label{eq:training_context_update}\\
    \vz_{k+i+1|k}^{P}&=\mA(\vc_{k+i|k}^{P})\vz_{k+i|k}^{P}
      +\mB(C_x\vz_{k+i|k}^{P})\vu_{k+i},
    \label{eq:recursive_prediction}\\
    \hat\vx_{k+i+1|k}&=C_x\vz_{k+i+1|k}^{P}.
    \label{eq:training_rollout_update}
\end{align}
The measurement and input histories are shifted by appending $\hat\vx_{k+i+1|k}$ and $\vu_{k+i}$, respectively, and dropping the oldest samples:
\begin{equation}
    \hat{\mX}_{k+i+1|k}=\operatorname{shift}
    (\hat{\mX}_{k+i|k},\hat\vx_{k+i+1|k}).
    \label{eq:rollout_shift}
\end{equation}
\begin{equation}
    \hat{\mU}_{k+i+1|k}^{\mathrm{in}}=\operatorname{shift}
    (\hat{\mU}_{k+i|k}^{\mathrm{in}},\vu_{k+i}).
    \label{eq:rollout_input_shift}
\end{equation}
In the predictive branch, the lifting encoder is evaluated only at the start of the rollout, while both scheduling matrices are updated from the model-propagated state and histories. With uniform weights $w_i=1/H_R$, the scheduled objective is
\begin{equation}
    \begin{aligned}
    \mathcal L_R
    &=\sum_{k\in\mathcal I_R}\sum_{i=1}^{H_R}w_i\bigl[
    \norm{C_x\vz_{k+i|k}^{P}-\vx_{k+i}}_2^2\\
    &\qquad+\lambda_R\norm{\vz_{k+i|k}^{P}-\vz_{k+i}^{\mathrm{enc}}}_2^2\bigr],
    \end{aligned}
    \label{eq:joint_training_loss}
\end{equation}
where $\lambda_R>0$ and $\mathcal I_R$ indexes valid rollout segments.
\end{definition}

\textbf{Stage~1 (scheduled-rollout fine-tuning).} We activate the scheduled transition and input matrices in \eqref{eq:transition_schedule}--\eqref{eq:low_rank_schedules} and jointly optimize the encoder, context map, nominal matrices, low-rank factors, and modulation networks by minimizing \eqref{eq:joint_training_loss}. The encoder initializes each rollout once; subsequent steps propagate the lifted state and update the scheduling variables using predicted histories according to \eqref{eq:training_context_update}--\eqref{eq:rollout_input_shift}. The projection $C_x$ remains fixed. The complete procedure is summarized in Algorithm~\ref{alg:training}.

\begin{algorithm}[H]
\caption{Two-Stage Transformer--Koopman Training}
\label{alg:training}
\begin{algorithmic}[1]
\STATE \textbf{Input:} Trajectory dataset $\mathcal D$; history length $P$; rollout horizon $H_R$; training epochs $E_0,E_1$.
\STATE \textbf{Stage 0:} Initialize $(\theta,\mA_0,\mB_0)$ by minimizing \eqref{eq:training_one_step_objects} for $E_0$ epochs, refreshing $\vz_{k+1}^{\mathrm{enc}}=g_\theta(\mX_{k+1})$ from measured histories at each update and holding it fixed during that update.
\STATE \textbf{Stage 1:} Activate both scheduled matrices \eqref{eq:transition_schedule}--\eqref{eq:low_rank_schedules}.
\FOR{$\ell=1$ \TO $E_1$}
    \FOR{each mini-batch of length-$H_R$ segments}
        \STATE Compute references $\vz_{k+i}^{\mathrm{enc}}=g_\theta(\mX_{k+i})$, $i=1,\ldots,H_R$, from measured histories.
        \STATE Set $\vz_{k|k}^{P}=g_\theta(\mX_k)$, $\hat{\mX}_{k|k}=\mX_k$, and $\hat{\mU}_{k|k}^{\mathrm{in}}=\mU_k^{\mathrm{in}}$.
        \FOR{$i=0$ \TO $H_R-1$}
            \STATE Evaluate $\vc_{k+i|k}^{P}=C_\phi(\hat{\mX}_{k+i|k},\hat{\mU}_{k+i|k}^{\mathrm{in}})$.
            \STATE Propagate $\vz_{k+i+1|k}^{P}$ using $\mA(\vc_{k+i|k}^{P})$ and $\mB(C_x\vz_{k+i|k}^{P})$.
            \STATE Read out $\hat\vx_{k+i+1|k}=C_x\vz_{k+i+1|k}^{P}$ and shift both histories.
        \ENDFOR
        \STATE Update the full predictor by minimizing \eqref{eq:joint_training_loss}, holding the references fixed during this update.
    \ENDFOR
\ENDFOR
\STATE \textbf{Return:} Trained encoder, context network, and dynamics parameters.
\end{algorithmic}
\end{algorithm}

\begin{figure}[H]
\centering
\figph{\columnwidth}{4.2cm}{\textbf{[Placeholder] Recursive window update.}\\[2pt]
Sliding windows $\mX_k$, $\mU_k^{\mathrm{in}}$: measured past samples (known) and predicted samples $C_x\vz_{i+1}$ (model output) entering the window step by step; oldest slot dropped; $\vz_i^{\mathrm{enc}}$ vs.\ $\vz_i^{\mathrm{prop}}$.}
\caption{Common-history convention and recursive window update. (Placeholder; figure to be drawn.)}
\label{fig:rollout}
\end{figure}

\subsection{Finite-Horizon Prediction Analysis}

We analyze the difference between the lifted states obtained by re-encoding measured histories and those propagated recursively from the same initial history and input sequence. Let $\vz_{k+i}^{\mathrm{enc}}=g_\theta(\mX_{k+i})$ and denote the propagated state by $\hat\vz_i$. Define
\begin{equation}
    \ve_i=\vz_{k+i}^{\mathrm{enc}}-\hat\vz_i,
    \qquad \ve_0=0.
    \label{eq:prediction_error}
\end{equation}
The corresponding one-step latent residual is
\begin{equation}
    \vr_{k}=\vz_{k+1}^{\mathrm{enc}}-\mA(\vc_k)\vz_k^{\mathrm{enc}}-\mB(\vx_k)\vu_k.
    \label{eq:residual_definition}
\end{equation}
For the two trajectories, write $\vc_{k+i}^{\mathrm{enc}}$ and $\vc_i^{\mathrm{prop}}$ for the context vectors computed from the measured and propagated histories, respectively. The same prescribed inputs are used in both history windows.

The following assumptions specify the finite-horizon comparison.
\begin{assumption}[A1: common finite work domain]
\label{ass:a1}
For fixed initial measured histories, parameters, horizon $H$, and future input sequence, there are compact sets $\mathcal Z\subset\R^d$ and $\mathcal C\subset\R^{d_c}$ and a compact input set $\mathcal U\subset\R^m$ such that the truth-encoded and propagated trajectories remain in $\mathcal Z$, their context outputs remain in $\mathcal C$, and their joint windows remain in a common domain $\mathcal D_{\rm win}\subset\R^{Pn+(P-1)m}$. Let $M_Z=\sup_{z\in\mathcal Z}\norm{z}_2$ and $M_U=\sup_{u\in\mathcal U}\norm{u}_2$.
\end{assumption}
\begin{assumption}[A2: common-window context regularity]
\label{ass:a2}
On $\mathcal D_{\rm win}$, the context map $C_\phi$ is Lipschitz with constant $L_\phi$:
\begin{equation}
\begin{aligned}
&\norm{C_\phi(W,V)-C_\phi(W',V')}_2\\
&\quad\le L_\phi\norm{(W,V)-(W',V')}_2
\end{aligned}
\end{equation}
for any two joint windows in this domain.
\end{assumption}
\begin{assumption}[A3: uniform one-step residual]
\label{ass:a3}
The residual in \eqref{eq:residual_definition} satisfies $\norm{\vr_{k+i}}_2\le\delta$ for $i=0,\ldots,H-1$, with a common $\delta\ge0$.
\end{assumption}

Using Proposition~\ref{prop:modulation_bound}, define
\begin{align}
    M_A&=\norm{\mA_0}_2+g_A,
    \label{eq:transition_norm_bound}\\
    L&=M_A+L_BM_U+L_AL_\phi\sqrt{P}M_Z.
    \label{eq:prediction_L}
\end{align}
Here $M_A$ bounds the scheduled transition norm, while $L$ collects the state-propagation, input-modulation, and history-scheduling contributions to the error recurrence.

\begin{proposition}[One-step prediction recurrence]
\label{prop:prediction_recurrence}
For every $0\le i\le H-1$, define $E_i=\max_{\max\{0,i-P+1\}\le j\le i}\norm{\ve_j}_2$. Then
\begin{equation}
\begin{aligned}
\norm{\ve_{i+1}}_2\le{}& \delta+(M_A+L_BM_U)\norm{\ve_i}_2\\
 &+L_AL_\phi\sqrt{P}M_Z
  E_i,
\end{aligned}
\label{eq:prediction_recurrence}
\end{equation}
Here $\norm{C_x}_2=1$ because $C_x=[I_n\;0]$.
\end{proposition}

\begin{proof}
Subtract the propagated update from the encoder update and add and subtract the encoder-scheduled terms:
\begin{equation}
\begin{aligned}
\ve_{i+1}={}&\vr_{k+i}\\
&+\left[\mA(\vc_{k+i}^{\mathrm{enc}})\vz_{k+i}^{\mathrm{enc}}-\mA(\vc_i^{\mathrm{prop}})\hat\vz_i\right]\\
&+\left[\mB(\vx_{k+i})-\mB(C_x\hat\vz_i)\right]\vu_{k+i}.
\end{aligned}
\end{equation}
The residual is bounded by Assumption~\ref{ass:a3}. For the transition term, use
\begin{align*}
 &\mA(\vc_{k+i}^{\mathrm{enc}})\vz_{k+i}^{\mathrm{enc}}-
 \mA(\vc_i^{\mathrm{prop}})\hat\vz_i\\
 &=\mA(\vc_{k+i}^{\mathrm{enc}})\ve_i+
 [\mA(\vc_{k+i}^{\mathrm{enc}})-\mA(\vc_i^{\mathrm{prop}})]\hat\vz_i.
\end{align*}
The two terms are bounded by $M_A\norm{\ve_i}_2$ and $L_AM_Z\norm{\vc_{k+i}^{\mathrm{enc}}-\vc_i^{\mathrm{prop}}}_2$, respectively. The input histories agree, and the measurement windows differ only in the predicted slots, each by $C_x\ve_j$. Hence their joint-window difference is at most $\sqrt{P}E_i$, and Assumption~\ref{ass:a2} bounds the context difference by $L_\phi\sqrt{P}E_i$. For the input term, \eqref{eq:schedule_lipschitz} gives $L_B\norm{C_x\ve_i}_2\norm{\vu_{k+i}}_2\le L_BM_U\norm{\ve_i}_2$. These bounds establish \eqref{eq:prediction_recurrence}.
\end{proof}

\begin{theorem}[Finite-horizon open-loop prediction bound]
\label{thm:prediction_bound}
Under Assumptions~\ref{ass:a1}--\ref{ass:a3} and the structural conditions above, define $W_i=\max_{0\le j\le i}\norm{\ve_j}_2$, so that $W_0=0$. Then, for every $0\le i\le H$,
\begin{equation}
    \norm{\ve_i}_2\le W_i\le \delta\sum_{t=0}^{i-1}L^t.
    \label{eq:prediction_bound}
\end{equation}
Thus, for $L\ne1$, $\norm{\ve_H}_2\le\delta(L^H-1)/(L-1)$, and for $L=1$, $\norm{\ve_H}_2\le H\delta$.
\end{theorem}
\begin{proof}
The residual, state-propagation, schedule-difference, and measurement-dependent input terms give \eqref{eq:prediction_recurrence}. Since $E_i\le W_i$, one obtains $\norm{\ve_{i+1}}_2\le\delta+LW_i$. Let $S_0=0$ and $S_{i+1}=\delta+LS_i$. The sequence $S_i=\delta\sum_{t=0}^{i-1}L^t$ is nondecreasing for $L\ge0$, since $S_{i+1}-S_i=\delta L^i$. Induction in $W_{i+1}=\max(W_i,\norm{\ve_{i+1}}_2)$ yields $W_i\le S_i$.
\end{proof}

This finite-horizon bound holds for any $L\ge0$, although it can grow with the horizon. Since the lift preserves the measured coordinates, the measurement-space error also satisfies
\begin{equation}
 \norm{\vx_{k+i}-C_x\hat\vz_i}_2
 =\norm{C_x\ve_i}_2\le\norm{C_x}_2\norm{\ve_i}_2.
 \label{eq:measurement_prediction_bound}
\end{equation}

% =========================================================
\section{Frozen-LTV Model Predictive Control}
\label{sec:control}
% =========================================================

In this section, we incorporate the scheduled predictor into a receding-horizon controller by freezing its dynamics along a nominal rollout. We formulate the resulting convex quadratic program (QP) and bound the approximation error and cost suboptimality introduced by freezing.

\subsection{Scheduled Prediction and Frozen-LTV Approximation}

At control instant $k$, initialize the lifted state as $\vz_0=g_\theta(\mX_k)$ and consider the input sequence $U=(\vu_0,\ldots,\vu_{N-1})$. Let $\mathcal U\subset\R^m$ be a nonempty, compact admissible input set and $\mathcal U_{\mathrm{feas}}=\mathcal U^N$. The complete scheduled rollout follows
\begin{equation}
    \vz_{i+1}=\mA(\vc_i)\vz_i+\mB(C_x\vz_i)\vu_i,
    \label{eq:complete_control_model}
\end{equation}
where $\vc_i$ is evaluated from the recursively updated measurement and past-input histories, as in Section~\ref{sec:training}. For measurement references $\vx_i^{\mathrm{ref}}$, input references $\vu_i^{\mathrm{ref}}$, and the previously applied input $\vu_{-1}$, consider the tracking objective
\begin{equation}
\begin{aligned}
J_{\mathrm{full}}(U)={}&\sum_{i=1}^{N-1}\norm{C_x\vz_i-\vx_i^{\mathrm{ref}}}_{Q_x}^2
+\norm{C_x\vz_N-\vx_N^{\mathrm{ref}}}_{P_x}^2\\
&+\sum_{i=0}^{N-1}\norm{\vu_i-\vu_i^{\mathrm{ref}}}_{R}^2
+\sum_{i=0}^{N-1}\norm{\vu_i-\vu_{i-1}}_{S}^2,
\end{aligned}
\label{eq:full_cost}
\end{equation}
where $Q_x,P_x,R,S\succeq0$. Tracking is specified in measured coordinates. Because future scheduling matrices depend on the candidate input sequence through the predicted histories, minimizing $J_{\mathrm{full}}$ is generally nonconvex.

Choose a feasible nominal sequence $\bar U=(\bar\vu_0,\ldots,\bar\vu_{N-1})$ and initialize its rollout from the same measured histories and lifted state. At each prediction step, evaluate $\bar\vc_i=C_\phi(\bar\mX_i,\bar U_i^{\mathrm{in}})$ and compute
\begin{equation}
    \bar\vz_{i+1}=\mA(\bar\vc_i)\bar\vz_i+\mB(C_x\bar\vz_i)\bar\vu_i.
    \label{eq:nominal_rollout}
\end{equation}
The matrices
\begin{align}
    \bar\mA_i&=\mA(\bar\vc_i),
    \label{eq:frozen_transition_matrix}\\
    \bar\mB_i&=\mB(C_x\bar\vz_i)
    \label{eq:frozen_matrices}
\end{align}
are held fixed when optimizing $U$, giving the linear time-varying model
\begin{equation}
    \vz_{i+1}^{\mathrm{fr}}=\bar\mA_i\vz_i^{\mathrm{fr}}+\bar\mB_i\vu_i,
    \qquad \vz_0^{\mathrm{fr}}=\vz_0.
    \label{eq:frozen_model}
\end{equation}
Thus the nominal rollout generates the matrices, whereas the candidate inputs determine the frozen trajectory. Fig.~\ref{fig:freezing} illustrates the distinction from the fully scheduled trajectory.

\begin{figure}[!t]
\centering
\figph{\columnwidth}{4.6cm}{\textbf{[Placeholder] Freezing construction.}\\[2pt]
Three trajectories over the horizon: nominal $\bar\vz_i$ (input $\bar U$), complete $\vz_i^{\mathrm{full}}$ (scheduling recomputed along the trajectory), frozen $\vz_i^{\mathrm{fr}}$ (matrices $\bar\mA_i$, $\bar\mB_i$ fixed). Gaps $\vg_i$ (nominal drift) and $\ve_i$ (complete vs.\ frozen).}
\caption{Nominal, complete, and frozen trajectories in the frozen-LTV construction. (Placeholder; figure to be drawn.)}
\label{fig:freezing}
\end{figure}

\begin{assumption}[A4: Uniform Control Comparison Domain]
\label{ass:a4}
For fixed $\bar U\in\mathcal U_{\mathrm{feas}}$ and every $U\in\mathcal U_{\mathrm{feas}}$, the nominal, complete, and frozen trajectories lie in common compact lifted-state and context domains, and their history windows lie in $\mathcal D_{\rm win}$. The bounds $M_Z,M_U$ and context Lipschitz constant $L_\phi$ in Assumptions~\ref{ass:a1}--\ref{ass:a2} hold uniformly on these domains.
\end{assumption}

\subsection{Condensed Prediction and Convex QP}

Stack the frozen states and inputs as
\begin{align}
    \mZ&=[(\vz_1^{\mathrm{fr}})^\top,\ldots,(\vz_N^{\mathrm{fr}})^\top]^\top,
    \label{eq:stacked_frozen_states}\\
    \mU&=[\vu_0^\top,\ldots,\vu_{N-1}^\top]^\top.
    \label{eq:stacked_inputs}
\end{align}
The frozen recursion gives the affine prediction relation
\begin{equation}
    \mZ=\mF+\mG\mU,
    \label{eq:frozen_prediction_matrices}
\end{equation}
where $\mF\in\R^{Nd}$ and $\mG\in\R^{Nd\times Nm}$ have block entries
\begin{align}
    F_i&=\bar\mA_{i-1}\cdots\bar\mA_0\vz_0,
    \label{eq:F_blocks}\\
    G_{i,t}&=\begin{cases}
    \bar\mA_{i-1}\cdots\bar\mA_{t+1}\bar\mB_t,&t<i,\\
    0,&t\ge i,
    \end{cases}
    \label{eq:F_G_blocks}
\end{align}
with empty products equal to identity matrices. Let $\bar C_x=I_N\otimes C_x$, $Y^{\mathrm{ref}}=[(\vx_1^{\mathrm{ref}})^\top,\ldots,(\vx_N^{\mathrm{ref}})^\top]^\top$, and $\bar Q_x=\operatorname{blkdiag}(Q_x,\ldots,Q_x,P_x)$. Define $\bar R=I_N\otimes R$, $\bar S=I_N\otimes S$, and $\mU^{\mathrm{ref}}=\operatorname{col}(\vu_0^{\mathrm{ref}},\ldots,\vu_{N-1}^{\mathrm{ref}})$. The block first-difference matrix $\hat D\in\R^{Nm\times Nm}$ has $I_m$ on its diagonal and $-I_m$ immediately below it. With $\hat{\mathbf c}=\operatorname{col}(-\vu_{-1},0,\ldots,0)$, the frozen cost is
\begin{equation}
\begin{aligned}
J_{\mathrm{fr}}(U;\bar U)={}&\norm{\bar C_x\mZ-Y^{\mathrm{ref}}}_{\bar Q_x}^2\\
&+\norm{\mU-\mU^{\mathrm{ref}}}_{\bar R}^2
+\norm{\hat D\mU+\hat{\mathbf c}}_{\bar S}^2.
\end{aligned}
\label{eq:frozen_cost}
\end{equation}
For polyhedral input constraints $\mathcal U=\{\vu:A_u\vu\le b_u\}$, substitution of \eqref{eq:frozen_prediction_matrices} yields the QP
\begin{equation}
\begin{aligned}
\min_{\mU}\quad &\frac12\mU^\top\mathcal H\mU+q^\top\mU\\
\text{s.t.}\quad &(I_N\otimes A_u)\mU\le\mathbf1_N\otimes b_u,
\end{aligned}
\label{eq:quadratic_template}
\end{equation}
where
\begin{align}
 \mathcal H&=2\left(\begin{aligned}
 &\mG^\top\bar C_x^\top\bar Q_x\bar C_x\mG\\
 &+\bar R+\hat D^\top\bar S\hat D
 \end{aligned}\right),
 \label{eq:QP_Hessian}\\
 q&=2\left(\begin{aligned}
 &\mG^\top\bar C_x^\top\bar Q_x(\bar C_x\mF-Y^{\mathrm{ref}})\\
 &-\bar R\mU^{\mathrm{ref}}+\hat D^\top\bar S\hat{\mathbf c}
 \end{aligned}\right).
 \label{eq:QP_coefficients}
\end{align}
Since $\mathcal H\succeq0$, this QP is convex. A positive-definite Hessian, for instance when $\bar R\succ0$, further ensures a unique minimizer.

At each sampling instant, the measured histories initialize a nominal rollout; the resulting matrices are frozen for one QP, whose first optimal input is applied before the next measurement update. The analysis below holds for any feasible $\bar U$ fixed during that QP; specifying how $\bar U$ is selected remains an implementation choice.

\subsection{Freezing Error and Conditional Suboptimality}

The frozen model approximates the complete scheduled model with the same candidate input sequence. Let $\vz_i^{\mathrm{full}}$, $\vz_i^{\mathrm{fr}}$, and $\bar\vz_i$ denote the complete, frozen, and nominal trajectories, respectively, and define their differences as
\begin{equation}
    \ve_i=\vz_i^{\mathrm{full}}-\vz_i^{\mathrm{fr}},\qquad
    \vg_i=\vz_i^{\mathrm{fr}}-\bar\vz_i.
    \label{eq:freezing_errors}
\end{equation}
All three trajectories have the same initial state and histories. Consequently, the complete and frozen predictions use identical matrices at the first step, so
\begin{equation}
    \vz_1^{\mathrm{full}}=\vz_1^{\mathrm{fr}},\qquad \ve_0=\ve_1=0.
    \label{eq:first_step_freezing_exact}
\end{equation}
Freezing error therefore arises only as the subsequent scheduling histories diverge.

For fixed $\bar U$, define bounds over the common feasible set:
\begin{align}
\bar\delta_u&:=\sup_{U\in\mathcal U_{\mathrm{feas}}}\max_{0\le i<N}\norm{\vu_i-\bar\vu_i}_2,
\label{eq:uniform_pointwise_input_deviation}\\
\bar\Delta_u&:=\sup_{U\in\mathcal U_{\mathrm{feas}}}\max_{0\le i<N}
\norm{U_i^{\mathrm{in}}-\bar U_i^{\mathrm{in}}}_2,
\label{eq:uniform_input_deviation}
\end{align}
where $U_i^{\mathrm{in}}$ and $\bar U_i^{\mathrm{in}}$ are the past-input windows corresponding to $U$ and $\bar U$. They share the measured prehistory, so $\bar\Delta_u\le\sqrt{P-1}\,\bar\delta_u$. With $M_B=\norm{\mB_0}_2+g_B$ and $M_A$ from \eqref{eq:prediction_L}, set
\begin{align}
\bar G_N&:=M_B\bar\delta_u\sum_{t=0}^{N-1}M_A^t,
\label{eq:uniform_nominal_drift}\\
\bar\delta_{\mathrm{frz}}&:=\begin{aligned}
 &L_AL_\phi M_Z\bar\Delta_u\\
 &+\big(L_AL_\phi\sqrt P\,M_Z+L_BM_U\big)\bar G_N,
\end{aligned}
\label{eq:uniform_freezing_driver}
\end{align}
and define
\begin{equation}
\bar K_i:=\begin{cases}
0,&i=0,1,\\
\displaystyle\bar\delta_{\mathrm{frz}}\sum_{t=0}^{i-2}L^t,&2\le i\le N,
\end{cases}
\label{eq:uniform_freezing_bound}
\end{equation}
where $L$ is given by \eqref{eq:prediction_L}. These constants give a uniform finite-horizon freezing error estimate.

\begin{proposition}[Uniform Frozen-Trajectory Error]
\label{prop:uniform_freezing_bound}
Under Assumptions~\ref{ass:a2} and \ref{ass:a4}, for every $U\in\mathcal U_{\mathrm{feas}}$ and $0\le i\le N$,
\begin{equation}
    \norm{\vz_i^{\mathrm{full}}-\vz_i^{\mathrm{fr}}}_2\le\bar K_i.
    \label{eq:freezing_bound}
\end{equation}
\end{proposition}
The proof, given in Appendix~\ref{app:proofs}, separates the input-induced nominal drift from the change in scheduling matrices. In particular, \eqref{eq:first_step_freezing_exact} is retained in the bound instead of assigning a nonzero error to the first prediction step.

To quantify the resulting cost error, let $M_Y=\norm{C_x}_2M_Z$, $M_{\mathrm{ref}}=\max_{1\le i\le N}\norm{\vx_i^{\mathrm{ref}}}_2$, and $\bar K_i^x=\norm{C_x}_2\bar K_i$. Define
\begin{equation}
\begin{aligned}
\varepsilon_J={}&2(M_Y+M_{\mathrm{ref}})
 \left(\norm{Q_x}_2\sum_{i=1}^{N-1}\bar K_i^x
 +\norm{P_x}_2\bar K_N^x\right)\\
&+\norm{Q_x}_2\sum_{i=1}^{N-1}(\bar K_i^x)^2
 +\norm{P_x}_2(\bar K_N^x)^2.
\end{aligned}
\label{eq:epsilon_cost}
\end{equation}
\begin{proposition}[Uniform Objective Approximation]
\label{prop:uniform_cost_certificate}
Under Assumptions~\ref{ass:a2} and \ref{ass:a4},
\begin{equation}
 \sup_{U\in\mathcal U_{\mathrm{feas}}}
 \left|J_{\mathrm{full}}(U)-J_{\mathrm{fr}}(U;\bar U)\right|\le\varepsilon_J.
 \label{eq:uniform_cost_certificate}
\end{equation}
\end{proposition}
\begin{proof}
The input and input-increment costs coincide for a fixed $U$. For $y_i^{\mathrm{full}}=C_x\vz_i^{\mathrm{full}}$ and $y_i^{\mathrm{fr}}=C_x\vz_i^{\mathrm{fr}}$, Proposition~\ref{prop:uniform_freezing_bound} gives $\norm{y_i^{\mathrm{full}}-y_i^{\mathrm{fr}}}_2\le\bar K_i^x$. Moreover, $\norm{y_i^{\mathrm{full}}}_2\le M_Y$ and $\norm{y_i^{\mathrm{fr}}}_2\le M_Y+\bar K_i^x$. Expanding the difference of squared weighted tracking errors and summing over the horizon yields \eqref{eq:epsilon_cost}.
\end{proof}

\begin{theorem}[Conditional Cost Suboptimality]
\label{thm:suboptimality}
Let $U^{\mathrm{fr}}$ and $U^\star$ be global minimizers of the frozen and complete problems on the same nonempty feasible set $\mathcal U_{\mathrm{feas}}$, respectively. Under Assumptions~\ref{ass:a2} and \ref{ass:a4},
\begin{equation}
    0\le J_{\mathrm{full}}(U^{\mathrm{fr}})-J_{\mathrm{full}}(U^\star)
    \le2\varepsilon_J.
    \label{eq:suboptimality_bound}
\end{equation}
\end{theorem}
\begin{proof}
By optimality and Proposition~\ref{prop:uniform_cost_certificate},
\begin{align*}
J_{\mathrm{full}}(U^{\mathrm{fr}})
&\le J_{\mathrm{fr}}(U^{\mathrm{fr}};\bar U)+\varepsilon_J\\
&\le J_{\mathrm{fr}}(U^\star;\bar U)+\varepsilon_J\\
&\le J_{\mathrm{full}}(U^\star)+2\varepsilon_J.
\end{align*}
The lower bound follows from the global optimality of $U^\star$.
\end{proof}
If a QP solver returns $\widetilde U$ with $J_{\mathrm{fr}}(\widetilde U;\bar U)\le J_{\mathrm{fr}}(U^{\mathrm{fr}};\bar U)+\eta$, the bound becomes $J_{\mathrm{full}}(\widetilde U)-J_{\mathrm{full}}(U^\star)\le2\varepsilon_J+\eta$. These are per-instant, finite-horizon cost comparisons, not closed-loop stability or recursive-feasibility guarantees.

% =========================================================
\section{Experiments}
\label{sec:experiments}
% =========================================================

This section is intentionally a manuscript placeholder. Experimental results, figures, and numerical claims are omitted in the present draft and must be inserted only after the corresponding data, code version, and evidence have been independently checked. No statement in Sections~\ref{sec:introduction}--\ref{sec:control} relies on an unreported experimental result.

\subsection{Data and protocol}

The final version will specify the data source, sampling interval, state and input coordinates, history length, train/validation/test split, normalization, input constraints, and random seeds. The protocol must distinguish measurement coordinates from lifted coordinates and must report prediction horizon in both steps and physical time when the sampling interval is relevant.

\subsection{Modeling evaluation}

The final version will report one-step and multi-step measurement-space prediction errors, together with the joint training objective in \eqref{eq:joint_training_loss}. Any comparison among architectures or loss choices requires a fixed data split, fixed evaluation horizons, and an explicitly stated scope. The present theory does not claim that the lifted-state term improves empirical performance.

\subsection{Control evaluation}

The final version will describe the nominal-sequence policy, horizon, weights, input constraints, solver status, and whether each result is an offline simulation or a physical experiment. Offline closed-loop simulation must not be described as hardware validation. Timing measurements, if later reported, must be measured independently rather than inferred from the convex-QP formulation.

% =========================================================
\section{Conclusion}
\label{sec:conclusion}
% =========================================================

This paper formulated a history-conditioned scheduled predictor with a temporal lifting, a bounded low-rank history-conditioned transition, and a measurement-dependent input modulation. The scheduled form preserves linear propagation when the scheduling signals are fixed, while its recursive use remains generally nonlinear. The finite-horizon prediction result makes the history-window coupling explicit and gives a conditional open-loop bound under common-history, work-domain, Lipschitz, and residual conditions.

For control, freezing the scheduling matrices along a nominal rollout produces an LTV prediction model and a convex QP with measurement-space tracking costs. The freezing analysis separates nominal drift from the complete-versus-frozen trajectory error. Under a uniform cost approximation and a common feasible set, the frozen global optimizer satisfies a conditional $2\varepsilon_J$ cost bound relative to the global optimizer of the complete scheduled problem.

The results are finite-horizon and open-loop; the uniform work-domain and residual conditions require certification for a concrete system.

\appendices
\section{Proof Details}
\label{app:proofs}

\subsection*{Scheduling bounds}
For completeness, the softmax Jacobian is $J(\pi)=\operatorname{diag}(\pi)-\pi\pi^\top$. It is positive semidefinite and, by the variance bound, satisfies $\norm{J(\pi)}_2\le1/2$. Integrating the Jacobian along the line segment between two logits gives $\norm{\operatorname{softmax}(a)-\operatorname{softmax}(b)}_2\le\frac12\norm{a-b}_2$. Combining this inequality with the $\tanh$ Lipschitz property, $\norm{\cdot}_1\le\sqrt r\norm{\cdot}_2$, and the rank-one factor normalization gives \eqref{eq:schedule_lipschitz}.

\subsection*{Frozen error bound}
For a fixed feasible $\bar U$ and any $U\in\mathcal U_{\mathrm{feas}}$, the nominal and frozen trajectories satisfy
\begin{equation}
    \vg_{i+1}=\bar\mA_i\vg_i+\bar\mB_i(\vu_i-\bar\vu_i).
    \label{eq:appendix_nominal_drift_recursion}
\end{equation}
Since $\norm{\bar\mA_i}_2\le M_A$ and $\norm{\bar\mB_i}_2\le M_B$, $\norm{\vg_i}_2\le\bar G_N$ for all $0\le i\le N$. Let $\vc_i^{\mathrm{full}}=C_\phi(\mX_i^{\mathrm{full}},U_i^{\mathrm{in}})$ and $\bar\vc_i=C_\phi(\bar\mX_i,\bar U_i^{\mathrm{in}})$. Subtraction of the complete and frozen recursions gives
\begin{equation}
\begin{aligned}
 \ve_{i+1}={}&\bar\mA_i\ve_i
 +[\mA(\vc_i^{\mathrm{full}})-\bar\mA_i]\vz_i^{\mathrm{full}}\\
 &+[\mB(C_x\vz_i^{\mathrm{full}})-\bar\mB_i]\vu_i.
\end{aligned}
\label{eq:appendix_three_trajectory_recursions}
\end{equation}
Define $W_i^{\mathrm{fr}}=\max_{0\le j\le i}\norm{\ve_j}_2$. Because initial histories agree, the measurement-window difference is bounded by $\sqrt P(W_i^{\mathrm{fr}}+\bar G_N)$, whereas the past-input-window difference is bounded by $\bar\Delta_u$. Hence
\begin{equation*}
\begin{aligned}
 \norm{\vc_i^{\mathrm{full}}-\bar\vc_i}_2
 &\le L_\phi\left[\sqrt P(W_i^{\mathrm{fr}}+\bar G_N)+\bar\Delta_u\right],\\
 \norm{C_x\vz_i^{\mathrm{full}}-C_x\bar\vz_i}_2
 &\le W_i^{\mathrm{fr}}+\bar G_N,
\end{aligned}
\end{equation*}
where $\norm{C_x}_2=1$. By the matrix bounds and schedule Lipschitz constants,
\begin{equation*}
 \norm{\ve_{i+1}}_2\le L W_i^{\mathrm{fr}}+\bar\delta_{\mathrm{frz}}.
\end{equation*}
The common initial state and histories give $\ve_0=\ve_1=0$. Starting from $W_1^{\mathrm{fr}}=0$, comparison with the nondecreasing sequence $\bar K_1=0$ and $\bar K_{i+1}=L\bar K_i+\bar\delta_{\mathrm{frz}}$ for $i\ge1$ proves \eqref{eq:freezing_bound}, including the exact first step.

\subsection*{Quadratic program}
Let $\mG_x=\bar C_x\mG$ and $\mW=\bar C_x\mF-Y^{\mathrm{ref}}$. The output term expands as
\begin{equation}
    \begin{aligned}
    &(\mW+\mG_x\mU)^\top\bar Q_x(\mW+\mG_x\mU)\\
    &\quad=\mU^\top\mG_x^\top\bar Q_x\mG_x\mU\\
    &\qquad+2(\mG_x^\top\bar Q_x\mW)^\top\mU+\mathrm{const}.
    \end{aligned}
\end{equation}
The input and input-increment terms expand analogously. Their sum yields the Hessian and linear coefficient in \eqref{eq:QP_Hessian}--\eqref{eq:QP_coefficients}. Positive semidefiniteness follows because each quadratic coefficient has the form $T^\top MT$ with $M\succeq0$.



\begin{thebibliography}{99}

\bibitem{wu2026multistep}
L. Wu, W. G. Y. Tan, L. Zhou, R. D. Braatz, and J. Drgo\v{n}a, ``Least-squares multi-step Koopman operator learning for model predictive control,'' arXiv:2601.11901, 2026.

\bibitem{ljung1999system}
L. Ljung, \emph{System Identification: Theory for the User}, 2nd ed. Upper Saddle River, NJ, USA: Prentice Hall PTR, 1999.

\bibitem{vanoverschee1994n4sid}
P. Van Overschee and B. De Moor, ``N4SID: Subspace algorithms for the identification of combined deterministic-stochastic systems,'' \emph{Automatica}, vol. 30, no. 1, pp. 75--93, 1994.

\bibitem{nelles2020nonlinear}
O. Nelles, \emph{Nonlinear System Identification: From Classical Approaches to Neural Networks, Fuzzy Models, and Gaussian Processes}, 2nd ed. Cham, Switzerland: Springer, 2020.

\bibitem{forgione2021dynonet}
M. Forgione and D. Piga, ``dynoNet: A neural network architecture for learning dynamical systems,'' \emph{Int. J. Adapt. Control Signal Process.}, vol. 35, no. 4, pp. 612--626, 2021.

\bibitem{koopman1931hamiltonian}
B. O. Koopman, ``Hamiltonian systems and transformation in Hilbert space,'' \emph{Proc. Natl. Acad. Sci. USA}, vol. 17, no. 5, pp. 315--318, 1931.

\bibitem{mezic2005spectral}
I. Mezi\'c, ``Spectral properties of dynamical systems, model reduction and decompositions,'' \emph{Nonlinear Dyn.}, vol. 41, no. 1--3, pp. 309--325, 2005.

\bibitem{williams2015data}
M. O. Williams, I. G. Kevrekidis, and C. W. Rowley, ``A data-driven approximation of the Koopman operator: Extending dynamic mode decomposition,'' \emph{J. Nonlinear Sci.}, vol. 25, no. 6, pp. 1307--1346, 2015.

\bibitem{proctor2016dmdc}
J. L. Proctor, S. L. Brunton, and J. N. Kutz, ``Dynamic mode decomposition with control,'' \emph{SIAM J. Appl. Dyn. Syst.}, vol. 15, no. 1, pp. 142--161, 2016.

\bibitem{proctor2018generalizing}
J. L. Proctor, S. L. Brunton, and J. N. Kutz, ``Generalizing Koopman theory to allow for inputs and control,'' \emph{SIAM J. Appl. Dyn. Syst.}, vol. 17, no. 1, pp. 909--930, 2018.

\bibitem{korda2018linear}
M. Korda and I. Mezi\'c, ``Linear predictors for nonlinear dynamical systems: Koopman operator meets model predictive control,'' \emph{Automatica}, vol. 93, pp. 149--160, 2018.

\bibitem{brunton2022modern}
S. L. Brunton, M. Budi\v{s}i\'c, E. Kaiser, and J. N. Kutz, ``Modern Koopman theory for dynamical systems,'' \emph{SIAM Rev.}, vol. 64, no. 2, pp. 229--340, 2022.

\bibitem{otto2021koopman}
S. E. Otto and C. W. Rowley, ``Koopman operators for estimation and control of dynamical systems,'' \emph{Annu. Rev. Control Robot. Auton. Syst.}, vol. 4, no. 1, pp. 59--87, 2021.

\bibitem{duran2025control}
J. F. Dur\'an-Sig\"uenza, L. I. Minchala, L. E. Garza-Casta\~n\'on, and H. Zhang, ``Control based on the Koopman operator: A comprehensive review,'' \emph{J. Franklin Inst.}, vol. 362, no. 18, art. 108256, 2025.

\bibitem{strasser2026overview}
R. Str\"asser, K. Worthmann, I. Mezi\'c, J. Berberich, M. Schaller, and F. Allg\"ower, ``An overview of Koopman-based control: From error bounds to closed-loop guarantees,'' \emph{Annu. Rev. Control}, vol. 61, art. 101035, 2026.

\bibitem{lusch2018deep}
B. Lusch, J. N. Kutz, and S. L. Brunton, ``Deep learning for universal linear embeddings of nonlinear dynamics,'' \emph{Nat. Commun.}, vol. 9, no. 1, p. 4950, 2018.

\bibitem{takeishi2017koopman}
N. Takeishi, Y. Kawahara, and T. Yairi, ``Learning Koopman invariant subspaces for dynamic mode decomposition,'' in \emph{Proc. NeurIPS}, 2017, pp. 1130--1140.

\bibitem{otto2019linearly}
S. E. Otto and C. W. Rowley, ``Linearly-recurrent autoencoder networks for learning dynamics,'' \emph{SIAM J. Appl. Dyn. Syst.}, vol. 18, no. 1, pp. 558--593, 2019.

\bibitem{han2020deep}
Y. Han, W. Hao, and U. Vaidya, ``Deep learning of Koopman representation for control,'' in \emph{Proc. IEEE Conf. Decision Control (CDC)}, 2020, pp. 1890--1895.

\bibitem{feizi2025deepkoopman}
N. Feizi, F. C. Pedrosa, J. Jayender, and R. V. Patel, ``Deep Koopman approach for nonlinear dynamics and control of tendon-driven continuum robots,'' \emph{IEEE Robot. Autom. Lett.}, vol. 10, no. 3, pp. 2926--2933, 2025.

\bibitem{brunton2017chaos}
S. L. Brunton, B. W. Brunton, J. L. Proctor, E. Kaiser, and J. N. Kutz, ``Chaos as an intermittently forced linear system,'' \emph{Nat. Commun.}, vol. 8, art. 19, 2017.

\bibitem{kamb2020timedelay}
M. Kamb, E. Kaiser, S. L. Brunton, and J. N. Kutz, ``Time-delay observables for Koopman: Theory and applications,'' \emph{SIAM J. Appl. Dyn. Syst.}, vol. 19, no. 2, pp. 886--917, 2020.

\bibitem{arbabi2017ergodic}
H. Arbabi and I. Mezi\'c, ``Ergodic theory, dynamic mode decomposition, and computation of spectral properties of the Koopman operator,'' \emph{SIAM J. Appl. Dyn. Syst.}, vol. 16, no. 4, pp. 2096--2126, 2017.

\bibitem{das2019delay}
S. Das and D. Giannakis, ``Delay-coordinate maps and the spectra of Koopman operators,'' \emph{J. Stat. Phys.}, vol. 175, no. 6, pp. 1107--1145, 2019.

\bibitem{shenoy2025temporal}
S. Shenoy, B. Sharan, and H. Werner, ``Temporal autoencoder for identification and predictive control of nonlinear dynamics based on Koopman operator theory,'' in \emph{Proc. American Control Conf. (ACC)}, 2025, pp. 1795--1800.

\bibitem{han2024robust}
M. Han, Z. Li, Xiang Yin, and Xunyuan Yin, ``Robust learning and control of time-delay nonlinear systems with deep recurrent Koopman operators,'' \emph{IEEE Trans. Ind. Informat.}, vol. 20, no. 3, pp. 4675--4684, Mar. 2024.

\bibitem{forootani2025deepkoopformer}
A. Forootani, M. Khosravi, and M. Barati, ``DeepKoopFormer: A Koopman enhanced Transformer based architecture for time series forecasting,'' arXiv:2508.02616, 2025.

\bibitem{forootani2026spectral}
A. Forootani and R. Iervolino, ``Learnable Koopman-enhanced Transformer-based time series forecasting with spectral control,'' arXiv:2602.02592, 2026.

\bibitem{li2025mamko}
Z. Li, M. Han, and X. Yin, ``MamKO: Mamba-based Koopman operator for modeling and predictive control,'' in \emph{Proc. ICLR}, 2025.

\bibitem{liu2023koopa}
Y. Liu, C. Li, J. Wang, and M. Long, ``Koopa: Learning non-stationary time series dynamics with Koopman predictors,'' in \emph{Proc. NeurIPS}, 2023.

\bibitem{rugh2000gain}
W. J. Rugh and J. S. Shamma, ``Research on gain scheduling,'' \emph{Automatica}, vol. 36, no. 10, pp. 1401--1425, 2000.

\bibitem{leith1998velocity}
D. J. Leith and W. E. Leithead, ``Gain-scheduled and nonlinear systems: Dynamic analysis by velocity-based linearization families,'' \emph{Int. J. Control}, vol. 70, no. 2, pp. 289--317, 1998.

\bibitem{cisneros2016qlmpc}
P. S. G. Cisneros, S. Voss, and H. Werner, ``Efficient nonlinear model predictive control via quasi-LPV representation,'' in \emph{Proc. 55th IEEE Conf. Decision Control (CDC)}, 2016, pp. 3216--3221.

\bibitem{cisneros2020qlpv}
P. S. G. Cisneros and H. Werner, ``Nonlinear model predictive control for models in quasi-linear parameter varying form,'' \emph{Int. J. Robust Nonlinear Control}, vol. 30, no. 10, pp. 3945--3959, 2020.

\bibitem{diehl2005realtime}
M. Diehl, H. G. Bock, and J. P. Schl\"oder, ``A real-time iteration scheme for nonlinear optimization in optimal feedback control,'' \emph{SIAM J. Control Optim.}, vol. 43, no. 5, pp. 1714--1736, 2005.

\bibitem{gros2020rti}
S. Gros, M. Zanon, R. Quirynen, A. Bemporad, and M. Diehl, ``From linear to nonlinear MPC: Bridging the gap via the real-time iteration,'' \emph{Int. J. Control}, vol. 93, no. 1, pp. 62--80, 2020.

\bibitem{zavala2009advancedstep}
V. M. Zavala and L. T. Biegler, ``The advanced-step NMPC controller: Optimality, stability and robustness,'' \emph{Automatica}, vol. 45, no. 1, pp. 86--93, 2009.

\bibitem{vaswani2017attention}
A. Vaswani \emph{et al.}, ``Attention is all you need,'' in \emph{Proc. NeurIPS}, 2017, pp. 5998--6008.

\bibitem{nie2023time}
Y. Nie, N. H. Nguyen, P. Sinthong, and J. Kalagnanam, ``A time series is worth 64 words: Long-term forecasting with Transformers,'' in \emph{Proc. ICLR}, 2023.

\end{thebibliography}

\end{document}
````

## 原始材料 2：ClosedLoop_A1_B1_Integrated_Certificate_Map.md

来源：`.project-log/docs/ClosedLoop_A1_B1_Integrated_Certificate_Map.md`

````markdown
# B1 理论树集成：证书输入、证明顺序与失败门槛

2026-10-18。研究性条件结果，不修改论文/控制器，不做数值验证，P5 STOP。

## 1. 三个不能混同的结论

1. 解析层：已给出完整F/Jacobian、PBH消元、周期参考局部构造和终端/域/种子条件命题。
2. 拟议B1算法层：只有下述全部证书共同成立，新增线性硬约束QP才有条件递归可行性。
3. 项目实例层：尚未认证某个具体模型参数、参考和实际重新编码初值；不能称当前控制器已通过。

原input-only QP在输入集合非空时非空。本文不否定这一性质；研究的是增加终端/工作域约束后的新问题。

## 2. 事实与独立证书输入

| 输入 | 必须提供的对象 | 当前状态 |
|---|---|---|
| 模型与坐标 | D1的q=(z,a,v)，窗口顺序、读出、固定参数 | 解析定义完成；实例参数未选 |
| 参考与反馈 | 输入有余量的平衡点及S2；或直接周期可实现参考与反馈证书 | OPEN；S4/S5是局部构造而非已找到参考 |
| 正则域 | 固定紧凸Omega×U，当前点Lipschitz；Taylor联合线段的DF正则界 | OPEN |
| 冻结缺陷 | O1的eta_i覆盖所有允许名义系数/候选点/输入组合 | OPEN；不能只绑定某条名义 |
| 编码扰动 | 每次采样同一适用域内的W_enc | OPEN；不直接外推单次有限数据 |
| 终端预算 | D7的A*d_fr、余项、参考缺陷及传播D_init，C1统一上界 | 公式完成，预算OPEN |
| 约束余量 | 输入面、联合安全面、终端域面和J4/J5 | OPEN |
| 初始化 | 实际q0与选定参考误差位于J8邻域 | OPEN；参考潜状态可能不在编码像 |

这些输入不得包含“每次新QP已经可行”或“未来轨迹已经合法”作为前提。未知必须保持OPEN，不能把条件命题变成当前实例结论。

## 3. 一次性离线构造顺序

**I1** 固定q坐标，选定模型和参考类别；用完整Jacobain检查S2或周期证书。若只存在不可稳定方向S3，则该参考/线性化分支失败，不再假设可取K。

**I2** 独立固定较大认证域Omega及U，认证当前点可用的L、名义冻结系数集合和缺陷eta_i；再递推O2得到E_i，递推D8得到g_j。不要用以全轨迹合法为前提的旧K_i反过来证明合法。

**I3** 用完整D7构造终端余项与误差预算。Frozen估计控制对应旧d_fr系数A，而非A+BK；编码误差只通过D_init计一次。检查Taylor线段整体在认证域。

**I4** 在D10可行区间选具有严格C2余量的r，生成有限对称theta-net；由C3–C5构造含正半径内球的Z_t。若严格余量不足，此构造不适用；可另试固定模板/乘子多面体LP，不把失败升级为普遍不存在。

**I5** 用J2/J3同时生成安全和shift收紧m_i。验证J4的终端到最深阶段域包含，以及J5/J6旧full延长点的整个g_N球；C5的相关新候选像包含不能替代整个球包含。

**I6** 合并所有新增面后重算J7/J8，确认严格阶段余量和原点中心终端内球；实际q0需落入所得邻域。没有正余量时，不能沿用加入安全面之前的旧种子。

注意I3–I6可能形成设计上的迭代依赖，例如增大r改变余项、m_N挤压终端域；允许离线更换域/模板并重验全部证书，但不能把联合不等式可解性作为已经完成的事实。本报告提供验证和构造程序，不保证任意模型输入下都成功。

## 4. 条件命题：拟议B1的递归可行性

假设I1–I6返回相互兼容的证书，均跨采样统一（周期情形检查全部相位）；QP采用固定的线性输入约束、J1工作域面和Z终端面；首轮名义输入为已认证参考输入，之后严格采用上一执行解的shift-tail；每次从实际重新编码初值生成一次名义完整rollout，冻结一次，再求一次QP。

此外，QP返回并精确执行可行解、参数不变、残差属于已认证集合、参考按绝对时间索引一致更新。不把未建模数值或执行误差隐含为已覆盖扰动。

凸性前提另行明确：原冻结目标的Hessian半正定，参考、冻结矩阵、收紧量及终端面在该次优化中固定。新增工作域和终端约束是仿射面；因此仍为凸QP。若改用球/椭球硬终端约束则不再属于本纯QP命题。

则在实际初值满足I6的条件下，每次新增约束QP至少存在一条可行候选。

证明顺序：
1. J8从真实初值与参考输入提供初始候选。用当前合法参考/名义点的逐步Lipschitz界认证首轮名义，不预设未来名义合法。
2. 任意当前QP可行解的Frozen路径满足全部J1和Z硬面。O1–O5通过当前点缺陷递推认证其full路径和误差管。
3. tail由已有Frozen终端状态计算，不在线另跑旧最优序列的full轨迹。旧full及其延长仅是证明对象。
4. 新full shift轨迹先由O6/O7、J2及J5得到合法域；比较中只使用同一tail。终端D7/C5的传播预算在上述合法域证明之后使用，不用其结论反证适用域。
5. J3使下一前N个阶段约束可行；C5给新终端Z包含，J4给最后阶段工作域面。输入由原约束移位与tail证书保持。
6. 该shift序列即下一名义，B-EXACT使候选自身新Frozen/full相同。故新QP有可行候选。
7. 新优化解不必等于候选；由于相同硬面保护所有可行解且缺陷界覆盖全部候选域，重复步骤2–6即可归纳。

**结论等级：CONDITIONAL，静态解析命题；不是实际B1认证，也不是P5价值下降或plant稳定性。**

## 5. 一次rollout/冻结/QP的准确范围

在线步骤包括从新初值的N步名义rollout、固定矩阵构建、一次QP、从其Frozen终端计算仿射tail和输入执行。没有额外在线非凸优化或二次冻结。
初始邻域检查、域/余项/半径/多面体证书为离线认证对象。若实际部署用失败后恢复求解、额外full验证或备份切换，必须另记复杂度与语义，不能仍称这份算法。
有限面数不保证实时性；不声明任何时延或物理截止时间。

## 6. 明确可证伪的失败门槛

| 门槛 | 失败能说明什么 | 不能说明什么 |
|---|---|---|
| S2秩条件失败 | 指定平衡点完整线性化不可稳定化 | 所有其他参考都失败 |
| C2/D10或多面体LP无解 | 当前反馈/包络/形状证书失败 | 所有真实鲁棒集都不存在 |
| J4/J5/J7不成立 | 联合安全收紧与终端/初始预算不兼容 | 原input-only QP不可行 |
| 实际q0不在J8邻域 | 当前局部初始化证书不适用 | 不存在其他可行初始化 |
| Frozen矩阵更新不一致 | B-EXACT及本文shift证明不适用 | 可以添加新误差常数后自动补救 |
| 残差/模型参数超出证书 | 证书必须重做或结论停止适用 | 旧静态复核仍认证新实例 |

## 7. 产物映射与验收

| 分支 | 主要产物 | 证据/复核 |
|---|---|---|
| F/Jacobian/余项/半径 | ClosedLoop_A1_B1_Explicit_Dynamics_Jacobian_Derivation.md D1–D10 | EV/REV-B1-DERIV-001 |
| 可稳定化与周期参考 | ClosedLoop_A1_B1_Reduced_PBH_and_Periodic_Reference.md S1–S6 | EV/REV-B1-DERIV-002 |
| 纯QP终端多面体 | ClosedLoop_A1_B1_Constructive_Polytope_From_Contraction.md C1–C5 | EV/REV-B1-DERIV-003 |
| 阶段shift与种子 | ClosedLoop_A1_B1_Stage_Shift_and_Initial_Seed.md W2–W9 | EV/REV-B1-DERIV-004 |
| 非循环域闭合 | ClosedLoop_A1_B1_Noncircular_Domain_Closure.md O1–O7 | EV/REV-B1-DERIV-005 |
| 联合安全/shift | ClosedLoop_A1_B1_Joint_Safety_Shift_Certificate.md J1–J8 | EV/REV-B1-DERIV-006 |

所有路径均位于.project-log/docs，证据属于静态解析范围；哈希只绑定版本，不证明数学结论。
新增理论分支已接到F/Jacobian/PBH；终端构造给出明确有限面规则；阶段域和种子已单列并联合；当前实例认证未完成。后续不能继续重复“文档GO”当作实例进展。

下一实质门槛是I1–I6中的模型/参考/域/扰动证书数据能否得到。本轮既不读取checkpoint做隐式数值认证，也不开始P5；若继续纯理论，应优先填具体缺失的解析常数/结构条件，而非再次假设终端集存在。

## 8. 本会话计划完成契约映射（不代替Project Goal）

| 本次计划标准 | 可检查产物 | 裁决与未完成项 |
|---|---|---|
| 新增分支与F/Jacobian、PBH、周期参考衔接 | §2–§4、D/S/C/W/O/J依赖链 | 解析衔接完成；实际参考及PBH认证OPEN |
| 非循环多面体构造及非空、输入和鲁棒包含条件 | C3–C5有限面网及严格预算；§3 I3/I4 | 条件构造完成；不是当前实例已满足C1/C2 |
| 分离终端、阶段shift、种子、具体模型 | O1–O7、J3/J4/J5/J8、§2证书输入 | 分离及联合条件证明完成；实际初值和统一界OPEN |
| 独立复核、版本证据与记忆 | 各EV/REV及本集成文档独立复核 | 限静态解析；产物变化后须重新绑定，不代表数值验证 |

TASK-B1-DERIV-20261018当前结构化记录仅列任务标题与next_action，未提供独立done_when字段；不得虚构其权威完成标准。标题中的显式F/Jacobian与可稳定化判据已给出，next_action要求的无数值理论表征已推进；是否关闭该任务须另经任务门禁。GOAL-002论文整体契约未在本增量中验收，不能宣告项目完成。
````

## 原始材料 3：ClosedLoop_A1_B1_Joint_Safety_Shift_Certificate.md

来源：`.project-log/docs/ClosedLoop_A1_B1_Joint_Safety_Shift_Certificate.md`

````markdown
# B1：安全域、移位收紧与初始种子的联合证书

2026-10-18；TASK-B1-DERIV-20261018。纯理论，不改产品、不做数值验证、P5 STOP。
依赖：Explicit_Dynamics_Jacobian_Derivation、Constructive_Polytope_From_Contraction、Stage_Shift_and_Initial_Seed、Noncircular_Domain_Closure。

## 1. 先固定认证域，不让常数依赖求解结果

本分支选择一个明确子类：工作域 Omega={q:Hq<=b} 具有固定面方向和右端；参考可以时变/周期，但所有误差界跨采样统一。时变Omega须另构造绝对时间/周期面族，不能直接套以下标量递推。
假设已经在该独立域及输入U上认证状态Lipschitz常数、当前点Frozen缺陷包络、编码残差界和终端Taylor联合线段域。此处不假设所有未来轨迹已经在域内，而是把“当前合法点可用的常数”作为模型正则性证书。

令E_i由O2生成，E_0=0；g_j由编码残差及同输入传播生成。全部取预先固定的非负统一上界。本文不会从有限时域单次观测外推这些上界。

## 2. 同一工作域面上的两种需求

对旧Frozen阶段p_i，施加

\[
Hp_i\le b-m_i,\quad i=0,\ldots,N.
\tag{J1}
\]

令逐面行范数组成向量 h=(||H_r||_2)_r。非循环域证明O5/O7在每个深度的充分安全下界为

\[
s_0=0,\qquad s_i=h(E_i+g_{i-1}),\quad i=1,\ldots,N.
\tag{J2}
\]

这同时覆盖旧full_i的E_i误差球，以及新shift full_{i-1}相对旧full_i的g_{i-1}球。g非负，故也覆盖O5。
跨采样阶段比较W2给逐面统一上界eps_j>=support_H(Dfr_{j+1}⊕G_j)，并要求eps_j>=0。此处可直接取eps_j=h(E_{j+1}+g_j)，无需先使用以合法域为前提的旧K_i。

## 3. 显式最小联合递推

定义逐面最大值递推

\[
m_0=0,\qquad
m_{j+1}=\max\{s_{j+1},m_j+\epsilon_j\},
\quad j=0,\ldots,N-1.
\tag{J3}
\]

证明：任何满足m_i>=s_i及W4的非负收紧序列，归纳必不小于J3；J3本身满足两种不等式，因此是这组下界的逐面最小解。
它不是最优控制问题的最小保守解，也不保证非空；仅是在给定包络和固定H下满足安全及shift预算的最小收紧向量。

O1–O5由当前点递推保证旧full合法；J2保证O7覆盖新shift的前N个点；J3使下一候选阶段j<N满足J1。相应下一名义full轨迹即shift候选，先证合法再冻结。
最后点j=N使用终端证书而不是越界使用旧p_{N+1}。

## 4. 终端末点与Taylor域必须一起检查

令多面体终端族Z_t由C3生成且C5成立。对每个终端绝对时间t=k+N，需验证

\[
H_r q_t^{ref}+\sigma_{H_r}(Z_t)\le b_r-m_{N,r}.
\tag{J4}
\]

这使新终端候选进入Z_{t+1}后满足新阶段N的全部联合面（对所有t验证）。它也使旧full终端加上相应误差球受J2覆盖。

另需独立覆盖旧延长点的整个编码误差传播球：

\[
\mathcal X_{ext,t+1}\oplus\mathbb B_2(g_N)\subseteq\Omega,
\tag{J5}
\]

其中X_ext,t+1是D7对e∈Z_t及d_fr的旧full延长状态外包，不含D_init。不能从“每个相关新终端点在Omega”倒推这个更大的球包含。
若有单独半径beta_ext,t，使旧full延长误差P_{t+1}范数<=beta_ext,t，则J5可由

\[
H_rq_{t+1}^{ref}
+\beta_{ext,t}\|H_rP_{t+1}^{-1/2}\|_2
+g_N\|H_r\|_2\le b_r
\tag{J6}
\]

检验。beta_ext,t从D7取得，不再加一次已计入g_N的编码误差。J6不成立只表示这个球外包证书失败。
终端Taylor联合线段还需(q_ref+tau(e+d_fr),u_ref+tau Ke)整体包含于已认证正则域；J4/J5是状态包含，不能替代该联合域条件。

## 5. 初始种子重算，而不继承旧W9

在每个阶段用新的m_j重新计算

\[
\mu_{j,r}=b_r-m_{j,r}-H_rq_{k+j}^{ref}.
\tag{J7}
\]

若所有必要面mu>0、参考输入可行且B_2(0,rho_N)⊆Z_{k+N}，则新的初始种子邻域可取

\[
0<\eta\le\min\left\{
\min_{j,r}\frac{\mu_{j,r}}{\|H_r\|_2\ell_j},
\frac{\rho_N}{\ell_N},\eta_{domain}\right\}.
\tag{J8}
\]

ell_j是欧氏状态Lipschitz乘积；零分母按W9约定处理。eta_domain可由参考路径到认证域边界的余量逐步构造，或独立给出。
固定参考输入、从新初值生成名义full rollout，B-EXACT提供该输入自身的Frozen轨迹，J8使它满足所有J1与终端面。由当前合法点到下一球包含的归纳证明这一名义合法性，不预先假设该名义安全。
实际重新编码初值是否属于此邻域仍待证；传播潜坐标参考不必属于编码像，所以不能保证实际初始化误差可任意小。

## 6. 条件递归可行命题及证明顺序

独立证书清单：
0. 参考为模型可实现轨道；首轮名义序列恰为J8认证的参考输入。所有QP候选输入均以硬约束限制在U，参考/移位/tail分别满足相同绝对时刻的输入约束。若首轮另选名义，必须独立认证其完整rollout。
1. 当前点可用的Omega×U Lipschitz/缺陷界和统一编码残差；
2. 由J2/J3生成的有限收紧序列；
3. 由严格预算C1/C2和有限面网构造的Z_t与合法Taylor线段；
4. J4、J5（或J6）、终端tail输入约束；
5. J7严格余量、J8正半径及实际初值属于该邻域；
6. 规定每轮shift-tail名义更新，QP返回并精确执行可行解。

其中缺陷包络须覆盖所有允许名义冻结系数与所有候选当前点/输入的组合，而不只是单条固定名义轨迹；跨采样统一性是独立的包络认证义务，不从Omega内点合法性自动推出。Taylor联合域条件也不从J4/J5自动推出。

则：初始种子可行→任意本轮QP解受J1/Z硬面保护→O1–O5认证其full轨迹→J2/O6/O7认证新名义前N点与终端域→C5及J4认证新终端→B-EXACT认证下一Frozen候选→下一QP非空。每步使用当前合法点；新增J1面的shift由J3显式覆盖，不再继承未覆盖的旧W4。

命题为CONDITIONAL，证明是独立几何/代数证书的蕴含，不是假设每步QP可行。
对当前项目，所有数值/统一域常数和实际初值适用性未认证，不能称为当前控制器性质；新增J1/Z硬约束也尚未实施。

## 7. 可失败位置与结论

J3总可递推生成有限向量（界有限时），但J4或J7可能因此无余量；C2也可能无可行半径。此时报告具体证书分支失败，不推断所有终端集不存在。
此分支把“新增安全面如何一起shift且保持种子”明确化为J3/J4/J7/J8，并补上独立终端延长球J5。
终端几何、阶段域和初始种子在显式条件下可联合闭合；具体模型、参考、正则性、扰动和实际初始化仍OPEN。P5继续STOP，不证明plant稳定性。
````

## 原始材料 4：ClosedLoop_A1_B1_Joint_Residual_Radius_Budget.md

来源：`.project-log/docs/ClosedLoop_A1_B1_Joint_Residual_Radius_Budget.md`

````markdown
# B1：残差、终端半径与实际初始化的联合预算

2026-10-18；TASK-B1-DERIV-20261018；strict（conclusion）。纯解析；不改论文/代码/控制器，不做数值、checkpoint或plant验证，P5 STOP。
前置：D7–D10、C3–C5、O1–O7、J1–J8、R1–R7、E1–E8。本文消去其中可显式消去的误差递推，而不再分别假设各关口可行。

## B0. 固定设计与统一坐标

选择固定多面体工作域Omega={q:Hq<=b}，模型可实现周期参考q_ref,t；固定P范数，P正定，固定有限面网系数alpha=cos(theta)∈(0,1)。周期K_t允许变化；取统一收缩lambda<alpha、余项常数c>=0、完整Jacobian范数Abar及参考缺陷界bref>=0。对本模型可实现参考bref=0，保留该符号仅便于核对D9账本。
球形上界为B_P(r)，有限面终端集Z_t满足B_P(alpha r)⊆Z_t⊆B_P(r)。固定P/相同面网可取固定Z；不要求参考恒定。

令L为完整增广F在已认证域的统一欧氏同输入Lipschitz界，e0>=0为统一Frozen当前点缺陷界（R4的eta，为避免与种子半径混淆改名e0），w>=0为统一重新编码残差半径。定义

    S_i=sum_{j=0}^{i-1} L^j,  S_0=0,
    E_i=e0 S_i,
    T_i=sum_{l=1}^{i} E_l,
    g_j=L^j w,
    D=||P^{1/2}|| E_N, gamma=||P^{1/2}|| L^N.       (B1)

N>=1；以下采用R2给出的L>=1，故S_i>0(i>=1)、L^N>0。可以用更紧的正L代替；不在本文处理L=0的除零分支。e0,L等必须先在独立域上固定；若随r或w改变，须重新计算，不能沿用本文固定常数的极值结论。

## B1. J3深度收紧的闭式解

记h_r=||H_r||_2，取eps_{j,r}=h_r(E_{j+1}+L^j w)。J2安全下界s_{i,r}=h_r(E_i+L^{i-1}w)正好为eps_{i-1,r}。
由于m_i>=0，J3中的m_i+eps_i>=s_{i+1}，故可消去max：

    m_{i,r}=sum_{j=0}^{i-1} eps_{j,r}
           =h_r(T_i+w S_i).                         (B2)

这是选择上述球包络eps后的J3精确解，不是所有多面体设计中的最小保守收紧；更紧支持函数包络可能改善结果。
公式同时保留O5/O7安全域与W4移位要求。L=1时S_i=i、T_i=e0 i(i+1)/2，显示即使一步误差不增长，累积阶段收紧也可能随N平方增长。

## B2. 终端收缩允许的重编码残差

令

    V(r)=lambda r+c(r+D)^2+Abar D+bref.             (B3)

V是旧full延长误差的P范数上界，不含重新编码传播项。为将新候选像压入终端内球，足够要求

    V(r)+gamma w < alpha r,
    w < Wterm(r):=[(alpha-lambda)r-c(r+D)^2
                          -Abar D-bref]/gamma.      (B4)

这比C2的球像条件更直接：固定面网后，alpha不是事后任意接近1的自由参数。若Wterm(r)<=0，则这个固定球包络/面网分支连w=0也不能获得严格余量；不据此否定别的面网/形状或真实集合。

当c>0，Wterm对r严格凹，其无约束最大点及最大值为

    rstar=(alpha-lambda)/(2c)-D,
    Wterm(rstar)=[(alpha-lambda)^2/(4c)
                  -(alpha-lambda)D-Abar D-bref]/gamma. (B5)

若允许r区间为闭区间[rlow,rhigh]且0<rlow<=rhigh，最大点为rstar向该区间的投影。若取零下端且只允许r>0，投影可能为0，此时只给正半径域的上确界，不保证最大值可达。c=0时Wterm为正斜率仿射函数，在有限正上端取得最大值。
该极值只优化终端这一关口，未优化下面所有关口；不能用B5为正就宣告联合证书可行。

## B3. 终端集与最深工作域的竞争

对固定H、周期参考定义统一未收紧余量

    mu_r=inf_t [b_r-H_r q_ref,t],
    v_r=||H_r P^{-1/2}||_2.

因为Z⊆B_P(r)，J4由下式充分保证：

    v_r r+h_r(T_N+w S_N) <= mu_r.                  (B6)

对非零面H_r（h_r>0），可得

    w <= Wface,r(r):=(mu_r-v_r r-h_r T_N)/(h_r S_N). (B7)

所以增大r通常提高初始终端容量，却线性压缩工作域残差余量。零面只需检查0<=b_r，不能代入除法。若参考相位数有限，inf为有限相位最小值。

## B4. 独立的旧full延长球关口

J5/J6要求整个旧full延长误差球加编码传播球留在Omega。B3只包络旧延长点，不含w，故其充分条件为

    v_r V(r)+h_r L^N w <= mu_r,
    w <= Wext,r(r):=(mu_r-v_r V(r))/(h_r L^N).      (B8)

B8与B6不同：前者保护用于传播误差证明的整个球，后者保护下一QP最深收紧面。即使B4和B6成立，也不要在未检查范数差异与球外包关系时删去B8。
终端Taylor联合线段和tail输入余量仍由独立r_cap保护；r_cap须给D的潜在偏差留余量，不能仅限制r本身。

## B5. 实际初始化带来的半径下限

取一个明确xi>0，作为要认证的欧氏初始邻域半径，要求实际初值满足E7的上界

    sigma_ref+sqrt((1+Lpsi²)||DeltaX||²+||Deltav||²)
       <= xi.                                    (B9)

同时xi<=eta_domain。终端内球的欧氏半径可取rho=alpha r/||P^{1/2}||。参考输入下，初始误差传播至N步<=L^N xi，所以J8末端条件给出

    r >= rseed(xi):=||P^{1/2}|| L^N xi/alpha.       (B10)

并非E8下界本身即可充分保证初始化；B9是充分预算。E8还可独立排除xi<sigma_ref/sqrt(1+Lpsi²)的编码像相交。
对阶段1<=j<=N，用相位/初始时刻统一mu_{j,r}=inf_k[b_r-H_r q_ref,k+j]，必须

    h_r(T_j+w S_j)+h_r L^j xi <= mu_{j,r},
    w <= Wseed,j,r(xi):=
           (mu_{j,r}-h_r T_j-h_r L^j xi)/(h_r S_j). (B11)

阶段j=0另查h_r xi<=mu_{0,r}；其S_0=0，不通过B11除法。因为xi>0，h_r>0，B11即使取等号也使收紧后的阶段参考余量>=h_r L^j xi>0，可使用J8。
实际q^E若精确为参考（sigma_ref=0等），也可用任意认证的正xi覆盖它，不要求把xi设为0。

## B6. 联合容量与真正的相容性测试

对给定r、xi定义

    Wjoint(r,xi)=min{Wterm(r), min_rface Wface,rface(r),
                     min_rface Wext,rface(r),
                     min_{1<=j<=N,rface} Wseed,j,rface(xi)}. (B12)

面索引rface与终端半径r不同。B7/B8/B11所有容量比值和B12的面最小值均仅遍历h_rface>0的非零面；零面单独检查b_rface>=0，若没有非零面，相应最小值按+infinity处理。一个方便的统一严格证书是选择

    0<=w<Wjoint(r,xi),
    rseed(xi)<=r<=r_cap, xi<=eta_domain,
    h_rface xi<=mu_{0,rface},
    B9、合法Taylor联合域、tail输入证书。          (B13)

除Wterm外的关口原本允许等号；B13统一取严格值只是保守方便。若某关口恰为零，不能用B13，仍可逐条检查B4/B6/B8/B11而不误判所有证书失败。
剩余设计为至多(r,xi)的低维联合不等式；这里没有运行求解。增加xi会提高rseed并压低Wseed，不能分别最大化半径和残差后组合。若B9只知道未知sigma_ref，B13仍未认证。

## B7. 把允许残差容量反馈到测量/编码两类缺陷

若选定一个满足B13的试验预算w（不是数值实验），E2给实际适用的充分条件为

    nu_bar²+(kappa_bar+Lpsi nu_bar)² <= w².         (B14)

非负nu_bar/kappa_bar下，等价于

    0<=nu_bar<=w/sqrt(1+Lpsi²),
    0<=kappa_bar<=sqrt(w²-nu_bar²)-Lpsi nu_bar.     (B15)

这给出明确的“测量误差—内部编码缺陷”预算曲线。光滑不代表kappa_bar接近0；nu_bar=0时仍要求kappa_bar<=w，kappa_bar=0时仍要求nu_bar<=w/sqrt(1+Lpsi²)。
在固定其余证书下，B14/B15告诉后续认证需要达到的上界；它不提供真实plant误差界，不把平均训练loss等同于该认证。

## B8. 固定P子类中可消去延长球预算的重复检查

一般J证书仍须单列延长球。但本文固定P、相同Omega、同一周期最小余量时，对非零面有h_r<=v_r||P^{1/2}||。因此B4给（零面只检查b_r>=0，不使用严格链）

    v_r V(r)+h_r L^N w
       <=v_r[V(r)+||P^{1/2}|| L^N w]
       <v_r alpha r<=v_r r.

B6又给v_r r<=mu_r-m_N,r<=mu_r，所以B8自动成立。可在本固定P子类的B12中删去Wext关口，不损失已证明条件；若换成不同域/相位P或不同参考余量，须重新证明这一蕴含，不能从C5相关像包含直接推整个球。

## B9. 联合预算的凸性与小残差鲁棒余量

当所有常数固定，B4左端V(r)+gamma w-alpha r关于(r,w)凸；B6、B10、B11及r_cap/xi边界均为仿射不等式。对给定实际初始化充分上界d_init（E7右端的已认证值），再施加xi>=d_init，预算可行域为(r,w,xi)中的凸集（严格B4给相对开约束）。离线可用正裕量tau>0替换为V(r)+gamma w<=alpha r-tau；这是预算综合问题，不是在线控制器的额外QP，也不宣称是LP。
因此一旦指定有限常数，这一子分支无需对r、w、xi作非凸盲搜。尚未认证的d_init或参数不能作为已经知道的数输入。

若存在一组正r、xi使w=0时B4/B6/B11有严格余量，且同时满足B9实际初值上界、B10半径下限、阶段0面及r_cap/eta_domain/线段与输入条件，则因有限阶段/面数和表达式连续性，存在epsilon>0，使同一r、xi对0<=w<epsilon仍可行。epsilon可直接取B12各正容量的最小值。这里不能把实际w说成可任意调小；E2/E5仍须证明实际统一残差低于epsilon。

## 验收与边界

新增结果：B2消去安全/shift递推，B4/B5给终端残差容量及最优半径，B7/B8/B11给工作域/延长球/实际种子的竞争，B10给初始半径下限，B14/B15拆回输出与编码缺陷预算。
若整个允许区间的Wterm<=0，可否定当前严格终端上界分支；若rseed>r_cap，可否定当前J8内球种子分支；都不是物理不可能或所有多面体不存在的结论。
全部结论在固定已认证常数下是解析蕴含；当前模型的PBH、参数、nu_bar/kappa_bar、sigma_ref以及联合数值可行性仍OPEN。纯理论继续推进不等于实例认证，P5 STOP。
````

## 原始材料 5：ClosedLoop_A1_B1_Explicit_Dynamics_Jacobian_Derivation.md

来源：`.project-log/docs/ClosedLoop_A1_B1_Explicit_Dynamics_Jacobian_Derivation.md`

````markdown
# B1：无重复增广递推、完整 Jacobian 与终端构造

日期：2026-10-18。任务：TASK-B1-DERIV-20261018。
范围：纯解析推导；不修改论文、代码、实验或正式控制器，不运行数值验证，不进入 P5。
依据：Main.tex 的 eq:state_readout、eq:history_windows、eq:recursive_prediction、eq:rollout_shift、eq:rollout_input_shift、eq:complete_control_model、eq:frozen_model。

## 1. 本轮新结果与对旧判断的修正

旧报告将“没有写出完整增广 F/Jacobian”标为阻塞。本轮从现有模型明确推导它们；**缺少已写公式不是不能解析推导的理由**。

得到：

1. 消除当前测量和上一输入重复存储的完整递推 F（D1）；
2. 包含 context 和测量相关 B 的链式导数的 Jacobian（D4）；
3. 可稳定化性的 PBH/周期反馈检查，以及结构无法决定答案的反例；
4. tail 使用 Frozen 估计时的非线性外包（D7）；
5. 反馈与导数证书给定后，显式的正半径存在区间（D10），以及固定多面体面下的离线 LP 构造。

上述结构公式为 PROVED（可微结论以可微为前提）。当前模型具体参考上的可稳定化性与非空终端证书仍 OPEN；不把必要数据缺失称为数学不可能。旧 input-only QP 的非空性仍由 U 非空保证；下文针对拟议加入终端约束的 B1，而非否定原 QP 可行。

## 2. 第一步：非重复状态与完整 F

令 r=P-1>=1，按由旧到新排列历史：

\[
a_t=\operatorname{col}(x_{t-r},\ldots,x_{t-1})\in\mathbb R^{rn},
\quad v_t=\operatorname{col}(u_{t-r},\ldots,u_{t-1})\in\mathbb R^{rm},
\quad q_t=\operatorname{col}(z_t,a_t,v_t).
\]

维数 s=d+rn+rm。这里“非重复”仅指消除确定性重复存储，不宣称是输入输出意义下最小实现。
定义 S_x,S_u 为删除最旧块后向前移的方阵，E_x,E_u 为末槽注入矩阵。
对 r=1，S_x=S_u=0。

\[
X(q)=\operatorname{col}(a,C_xz),\quad
c(q)=C_\phi(X(q),v),\quad
f(q,u)=A(c(q))z+B(C_xz)u.
\]

完整模型为

\[
\boxed{F(q,u)=\operatorname{col}
\bigl(f(q,u),\ S_xa+E_xC_xz,\ S_uv+E_uu\bigr).}
\tag{D1}
\]

**测量历史 a 的下一槽追加当前 x=C_xz，不是下一测量 C_xf。** 因为 a 不含当前测量；下一完整窗口为 col(a^+,C_xf)，它才等于原完整 X 删除首槽并追加 C_xf。
由此 D1 与论文的完整窗口 shift 完全等价。

用重构映射

\[
\eta(q)=\operatorname{col}(z,a,C_xz,v),\qquad
\xi(q)=\operatorname{col}(\eta(q),E_{last}v)
\tag{D2}
\]

恢复旧 eta/xi，E_last 取 v 的末输入块。故当前测量重复槽、额外 u_last 块都可删除，输入增量项仍可准确用 E_last v 计算。
同一候选 Frozen/full 的 v 差恒为零，不可另加一个上一输入独立误差球。

### 编码流形不是递归状态空间

初始化 q^E 满足 z=g_theta(col(a,C_xz))。但预测后 z 递归传播而不重新编码；编码一致性损失不保证 F 保持该等式。
因此不能强行令潜特征 psi=psi_theta(X) 以进一步消除潜坐标，也不能只在编码流形切空间检查控制模态。
D1 的状态空间保留传播潜坐标；实际重新编码状态作为新的初值，并由残差与预测连接。

## 3. 第二步：链式导数与完整线性化

在可微点 (q,u) 记

\[
C_a=\partial_aC_\phi,\quad C_0=\partial_xC_\phi,\quad C_v=\partial_vC_\phi,
\]

定义线性映射 T_A、T_B：

\[
T_Ah=(DA(c)[h])z,\qquad T_Bh=(DB(x)[h])u.
\]

则

\[
\begin{aligned}
J_z&=A(c)+T_AC_0C_x+T_BC_x,\\
J_a&=T_AC_a,\qquad J_v=T_AC_v,\qquad J_u=B(x).
\end{aligned}
\tag{D3}
\]

由于当前输入 u 不进入 context，偏导 J_u 无当前输入 context 链式项；但 u 经 v^+ 影响后续 context。

\[
\boxed{
\mathsf A(q,u)=D_qF=
\begin{bmatrix}
J_z&J_a&J_v\\ E_xC_x&S_x&0\\0&0&S_u
\end{bmatrix},\qquad
\mathsf B(q,u)=D_uF=
\begin{bmatrix}B(x)\\0\\E_u\end{bmatrix}.}
\tag{D4}
\]

证明：对 f 的乘积项分别求导；历史与缓存块为线性移位，直接微分即得。各块维数分别匹配 z、rn、rm。

低秩结构也有显式导数：

\[
DA(c)[h]=U_A\operatorname{diag}(D\gamma_A(c)h)V_A^T,
\quad DB(x)[h]=U_B\operatorname{diag}(D\gamma_B(x)h)V_B^T.
\tag{D5}
\]

对 gamma_j=g pi_j tanh(l_j)，其方向导数为

\[
D\gamma_j[h]=g\bigl(D\pi_j[h]\tanh(l_j)
+\pi_j(1-\tanh^2(l_j))Dl_j[h]\bigr),
\quad D\pi[h]=(\operatorname{diag}\pi-\pi\pi^T)W^\pi h.
\]

该公式避免“只分析名义 A_0,B_0”的错误。完整 Jacobian 不是 Frozen 矩阵序列；即便 u_ref=0 使 T_B=0，context 导数一般仍非零。

正则性边界：论文只给出 context Lipschitz 假设，不足以保证处处可微或二阶光滑。在不可微点不能使用一个任选 Jacobian 替代实际映射；可用直接差商/Lipschitz集合外包，若采用广义 Jacobian则必须覆盖所有适用矩阵并给共同收缩证书。

## 4. 第三步：明确参考类别和可稳定化性

### 4.1 选定的理论类别

优先研究有限周期 T 的 R1∩R3：

\[
q_{t+T}^{ref}=q_t^{ref},\quad u_{t+T}^{ref}=u_t^{ref},\quad
q_{t+1}^{ref}=F(q_t^{ref},u_t^{ref}).
\]

要求参考输入在 U 各有效面有严格余量、参考历史由同一序列构造。不是断言当前项目已经找到该周期轨迹。
传播潜坐标的参考不要求每一步等于重新编码参考；若额外要求二者相同，需再证明编码一致性。
一般近似参考用 b_t=F(q_t^ref,u_t^ref)-q_{t+1}^ref 显式计入；本类别 b_t=0。

### 4.2 固定点与周期检查

在固定点，取 A*=mathsf A(q*,u*)、B*=mathsf B(q*,u*)。离散线性化可稳定化的必要充分条件是

\[
\operatorname{rank}[\zeta I-\mathsf A_*,\mathsf B_*]=s
\quad\forall |\zeta|\ge1.
\tag{D6}
\]

对周期参考，应构造 A_t,B_t 的周期线性系统。一个直接的反馈证书是找到周期 K_t、P_t>0 和 Q_t>0，满足

\[
(A_t+B_tK_t)^TP_{t+1}(A_t+B_tK_t)-P_t\preceq-Q_t,
\quad P_{t+T}=P_t.
\]

这等价地提供跨时刻 P-范数收缩率；不能仅检查各时刻谱半径。
可定义离线综合问题：以周期 X_t>0,Y_t 为变量，求

\[
\begin{bmatrix}X_{t+1}&A_tX_t+B_tY_t\\
(A_tX_t+B_tY_t)^T&X_t\end{bmatrix}\succ0,
\quad X_{t+T}=X_t,
\qquad K_t=Y_tX_t^{-1}.
\]

该 Schur 补保证 P_t=X_t^{-1} 下严格下降；本轮不求解此问题，不伪称得到具体 K_t。若限制 K 的稀疏/测量结构，须加相应约束，不能直接使用无结构可行解。

### 4.3 缓存不能单独决定可稳定化性

- 输入缓存对 (S_u,E_u) 是可控移位寄存器。
- 测量缓存虽无直接输入行，仍经 u→z^+→a^{++} 可受控。
- 独立移位块幂零，不意味着全部增广模态为稳定；J_a 与 E_xC_x 构成耦合回路。
- 删除重复坐标只能删除真实代数重复，不能删去不受控的传播潜变量。

结构不能决定答案：令 A 常量、B=0，所有调度修正为零，context 任意。若 A=a I 且 |a|>1，则 z 存在不稳定不可控模态，D6失败；若 A=a I 且 |a|<1，同样结构的缓存与 z 组合为稳定，线性化可稳定化（K=0即可）。两者均可满足有限工作域比较；有限时域界不排除前者。
因此仅凭低秩界/历史结构既不能证明可稳定化，也不能证明不可稳定化。

## 5. 第四步：Frozen tail 的准确非线性外包

在旧终端绝对时刻 t=k+N，用 q^fr=q_ref+e、q^full=q_ref+e+d_fr 和同一个
u_tail=u_ref+K_t e。旧 full 延长误差为

\[
\begin{aligned}
e_{ext}
&=F(q_t^{ref}+e+d_{fr},u_t^{ref}+K_te)-q_{t+1}^{ref}\\
&=(A_t+B_tK_t)e+A_td_{fr}+b_t
+R_t(e+d_{fr},K_te).
\end{aligned}
\tag{D7}
\]

关键是 d_fr 的一阶系数为 **A_t**，不是 A_t+B_tK_t：tail 由 Frozen e 计算，未对 d_fr 提供 K_t d_fr 的反馈。

若 DF 在整个参考邻域及所用线段上 H_t-Lipschitz，则

\[
\|R_t(h,l)\|_2\le\tfrac12H_t\|(h,l)\|_2^2.
\]

若只知 F Lipschitz，则不声称二阶余项，可直接用真实闭环映射差商界，代价是可能无法得到收缩。

重新编码首步偏差在 q 坐标为 col(r_k,0,0)：a^+缓存的是旧当前测量，故该块无首步残差注入。恢复到完整 X 坐标时，另定义 E_X=col(0_{rn×n},I_n)，维数为 Pn×n（不同于D1的E_x），完整eta残差为 col(r_k,E_X C_x r_k,0_{rm})；两种写法通过 D2 重构一致，不能重复计入。

新初值 q_{k+1}^E=F(q_k^E,u_0)+w_k，w_k属于W_enc。新完整 shift rollout与旧 full延长轨迹使用完全相同的剩余输入和同一个tail，故

\[
\|\Delta q_{j|k+1}\|\le
\left(\prod_{\ell=1}^{j}L_{F,k+\ell}\right)\bar w_k,
\quad j=0,\ldots,N.
\tag{D8}
\]

这定义传播集合 D_init；不再把 W_enc 与 D_init在同一终端相加。
旧full延长状态和新完整候选终端差属于 D_init,N,k，而不是未来plant的N步真实状态误差。

总终端候选外包为 D7 加 D_init,N,k；b_t只计一次。plant未建模失配不在这里默认为零；本轮仅讨论学习模型或满足显式重新编码残差界的测量增广层。

## 6. 第五步：给出一个可构造的正半径区间

选定固定或周期 K_t 和 P_t后，在跨时刻 P-范数中设闭环收缩率<=lambda<1。令旧d_fr半径<=Delta，终端D_init半径<=g，参考缺陷半径<=b。
所有常数需统一覆盖所选参考族、候选域与每次采样，不得由单次有限时域界直接外推。
由D7得到保守标量外包（统一范数等价因子吸收入常数）：

\[
\|e_{new,N}\|_{P_{t+1}}
\le\lambda r+c(r+\Delta)^2+d_0,
\quad
d_0=\bar A\Delta+b+g.
\tag{D9}
\]

例如联合扰动线段欧氏范数不超过 (1+||K_t||)r+Delta，余项界可取 H/2 乘该量平方，再用P范数等价常数转为 c(r+Delta)^2。需在该线段整体落于已认证域时才能使用。

令 a=1-lambda-2c Delta、b0=d0+c Delta^2，则正半径需满足

\[
cr^2-ar+b_0\le0,\qquad 0<r\le r_{cap}.
\tag{D10}
\]

若 c>0、a>0、a^2-4cb0>=0，则

\[
r_-={a-\sqrt{a^2-4cb_0}\over2c},\quad
r_+={a+\sqrt{a^2-4cb_0}\over2c},\quad
r\in[r_-,\min(r_+,r_{cap})]\cap(0,\infty).
\]

交集非空时，任选其中一个r即给出实际的参数化终端球构造；无需再假设“存在某个合适r”。c=0时用 d0/(1-lambda)<=r<=r_cap。零扰动且c>0时有0<r<=min((1-lambda)/c,r_cap)。

r_cap由输入面、局部域、外终端面和扰动后线段域的包含约束计算。例如对 a_u u<=b_u，中心输入u_ref的余量mu_u给出 r<=mu_u/||a_u K P_t^{-1/2}||；对工作域面同理，同时给 d_fr 留裕量。
输入增量目前仅为成本，不额外假设硬约束；若另行批准硬增量面，则使用a_delta(K-E_last)及参考输入差计算额外r_cap。

**重要限定：** D9为上界；D10无解仅说明此上界证书失败，不证明真实终端集不存在。r_cap可以是保守安全半径，不能把它视为最大允许半径。
圆球/椭球若直接作为QP二次约束会变为QCQP，而非纯QP；若坚持线性约束，须用下面的多面体证书，不能只取球内多面体却不重验不变性。

## 7. 球证书失败后的多面体离线构造

在q独立坐标取一个固定有界模板 Z={e:G e<=alpha}（周期时取G_t）。以下提供可执行的证书综合形式，不运行求解：

1. 选定K_t及紧局部盒W_t，独立包络R_t为紧集合Rbar_t，d_fr在Dfr_t；把A_t Dfr_t、b_t及D_init加入同一个Dbar_t。
2. 在固定G_t、A_cl,t下，对每个下一面求非负lambda_{t,q}满足 G_t^T lambda=(A_cl,t)^T G_{t+1,q}^T。q已非重复，若额外保留线性等式则加入自由等式乘子。
3. 固定这些lambda，建立关于alpha_t、r及中心e_c,t的离线LP：
   - lambda^T alpha_t+support(Dbar_t,G_{t+1,q})<=alpha_{t+1,q}；
   - G_t e_c,t+r||G_{t,q}||<=alpha_t，r>=epsilon>0；
   - Z_t包含于已认证W_t和输入/外终端面，用相同的固定非负乘子证书；
   - 周期端点alpha_{t+T}=alpha_t；最大化r。
4. LP可行解直接给出正相对内点与多面体终端族；不可行只否定这组G/K/外包/乘子，不否定所有多面体。

Rbar_t必须覆盖整个W_t内 e+d_fr与Ke对应的余项；不能先假设LP解所在域安全再倒推余项。G、K或乘子与alpha同时作为变量通常会产生双线性项，因此此离线构造采用先固定模板/增益/乘子的保守分步法，不伪称全部综合为一个LP。

## 8. 接回B1而不进入P5

令已构造的多面体终端内集为Z_t，QP硬约束是 G_t e_N^fr<=alpha_t。tail从已有QP的Frozen终端点直接计算，在线不额外计算U*的full rollout。
旧full轨迹仅用于分析；D7+D8和证书确保新初值的full shift候选终端属于Z_{t+1}。下一名义输入正是该shift序列，B-EXACT由D1与相同冻结/窗口更新逐步归纳成立，因此该候选的新Frozen终端等于新full终端，满足同一硬约束。
任意新QP可行解均满足同一个终端硬约束；统一Dfr界覆盖整个QP候选域，故下一轮可以从该解重做同样tail构造，不要求最优解等于名义。

阶段工作域是独立义务：仅需要适用界的阶段留在W，不要求所有阶段都在终端Z。可用Frozen线性工作域面及对full/fr差的支持收紧，但必须另外验证shift后这些阶段收紧面的可行性；终端证书不能替代它。若在整个输入可行集已取得统一预测工作域，则无需新增阶段面；否则未证明这些面shift保持时，整体递归可行性仍OPEN。

初始新增终端QP需一个独立可行种子；例如已证明名义参考从q0=qref出发可行，零误差属于Z且0属于各误差外包，则提供一个理想初始种子。真实重新编码q0是否等于/接近qref须另证，不能假定。输入-only非空不保证此种子存在。

## 9. 结论与精确下一步

| 项目 | 本轮结果 |
|---|---|
| 非重复F、历史回填、缓存重构 | D1-D2解析PROVED |
| 完整Jacobian与低秩导数 | D3-D5在可微条件下PROVED |
| 当前模型是否可稳定化 | OPEN：缺具体参考及其导数证书，非“F无法推导” |
| 仅凭模型结构能否决定 | 不能；稳定/不可稳定两类常量反例已给出 |
| 非线性Frozen-tail外包 | D7解析成立，定量界CONDITIONAL |
| 正半径球构造 | D10显式区间，当前实例待证；失败不等于不存在 |
| 纯QP多面体构造 | 离线固定模板/增益/乘子LP可执行定义，当前未运行 |
| 整体B1递归可行 | CONDITIONAL；当前实例OPEN，阶段域/初始种子仍待证 |
| 原控制器QP非空 | U非空时成立；不应笼统NO-GO |
| 当前论文/plant稳定性、P5 | 未证明，P5 STOP |

本轮已把“没有F和Jacobian”推进为明确公式；首要未解项变为**指定可实现参考上的完整线性化可稳定化与统一余项/扰动预算是否满足D10或多面体证书**。
下一阶段若保持纯理论，可进一步研究这些导数的可稳定化充分条件或不可能反例；若要判断某个已训练模型是否满足，则需要获准选定模型参数/参考和后续验证范围，不能靠本报告声称已验证。
````

## 原始材料 6：ClosedLoop_A1_B1_Direct_Encoded_Defect_Certificate.md

来源：`.project-log/docs/ClosedLoop_A1_B1_Direct_Encoded_Defect_Certificate.md`

````markdown
# B1：编码坐标上的直接缺陷证书与一阶抵消

2026-10-18；TASK-B1-DERIV-20261018；strict（conclusion）。纯理论，无产品修改、checkpoint或数值验证；P5 STOP。
依赖D1、E1、K1及N6。目标是保留当前编码状态的代数关系，避免K2逐项取范数时丢失抵消；不是再假设一个未知的小残差。

## M1. 当前编码坐标与完整测量窗口

写y=col(X,v)，X=col(a,x)，v为过去输入。定义编码图

    Q(y)=col(G(X),a,v), G(X)=col(x,psi(X)).

定义模型预测的下一完整测量窗口

    W(y,u)=col(S_x a+E_x x, C_x f(Q(y),u)),

及直接编码缺陷

    D(y,u)=psi(W(y,u))-C_psi f(Q(y),u)
          =-h(F(Q(y),u)).                            (M1)

因此对实际当前编码信息y，E1的kappa恰为D(y,u)。y包含所有当前可用信息而非未来测量；Q不是完整传播F的不变坐标变换，不能用它删除递归传播中的潜状态。

令s=col(y,u)，映射J(s)=col(Q(y),u)，使M(s)=F(J(s))。M1也写为D=-h∘M。以下仅在独立认证的紧凸s域及所需像域上求导；确定性encoder、F及h须C²，不能由context光滑性代替encoder正则。

## M2. 保留抵消的直接Jacobian

在基点s0处，记q0=Q(y0)、q1=F(q0,u0)、J0=DJ(s0)、F0=DF(q0,u0)（联合状态/输入导数），H1=Dh(q1)。则

    DD(s0) = -H1 F0 J0.                             (M2)

编码图导数为

    DQ[DeltaX,Deltav]
      =col(col(Deltax,Dpsi(X)DeltaX), Deltaa,Deltav).

若Lpsi界有效，||DQ||<=sqrt(1+Lpsi²)，故||J0||<=sqrt(1+Lpsi²)。但应先精确乘H1 F0 J0，再取范数；把三个范数分别相乘会回到K2类型的保守上界。
输入列也包含在J0中，故M2测试允许所有输入扰动。只对参考生成反馈方向有抵消，不代表对原QP任意执行输入有抵消。

## M3. 一个可解析求出的二阶常数

在整个认证s域，设

    ||DJ||<=j1, ||D²J||<=j2,
    ||DF||<=f1, ||D²F||<=f2,
    ||Dh||<=h1, ||D²h||<=h2.

由复合二阶链式法则，

    ||D²D|| <= h2(f1 j1)²+h1(f2 j1²+f1 j2)
             =: HD.                               (M3)

可取j1=sqrt(1+Lpsi²)、j2=Hpsi、h1=sqrt(1+Lpsi²)、h2=Hpsi，前提是同一Lpsi/Hpsi覆盖当前窗口和所有下一预测窗口。F的f2可用R3；联合一阶界可由R2与Lu取f1<=sqrt(Lq²+Lu²)。
M3只是方便的保守Hessian界；M2仍保留精确抵消。h的线性潜坐标槽与Q的线性缓存槽没有二阶项，故Hpsi没有额外窗口长度因子。

对||s-s0||<=R且整条连接线在认证s域内，定义d0=||D(s0)||、d1=||DD(s0)||，可取

    ||D(s)|| <= d0+d1 R+(HD/2)R².                 (M4)

与E2合并得到实际一步重新编码残差上界

    w_req<=sqrt(nu_bar²+
            [d0+d1 R+(HD/2)R²+Lpsi nu_bar]²).      (M5)

这个R是当前信息窗口/过去输入/执行输入的联合半径，不是终端r或初始化xi；不能擅自等同。周期基点逐相位取统一上界，并认证每次实际s属于相应集合。

## M4. 从一阶到二阶：真正所需的切向条件

若d0=0且DD(s0)=0，则M4给邻域内D=O(R²)。若D可微且在某个完整开邻域具有||D(s0+v)||<=C||v||²，则必有D(s0)=0且DD(s0)=0。故“二阶小缺陷”不仅要求参考编码一致，还要求

    Dh(F(q0,u0)) DF(q0,u0) DJ(s0)=0.              (M6)

当q0和q1均编码一致时，M6表示F把所有编码图状态/输入切方向送入下一编码图切空间。这是点上的一阶条件，不保证有限邻域的精确不变性。
如果DD(s0)非零，存在单位方向v使||D(s0+t v)||/|t|趋于||DD(s0)v||>0，因此完整开邻域上不可能有统一O(R²)缺陷。若可行信息域仅是低维集合，只需检查其可实现切方向；不能用开邻域必要性排除受限集合上的二阶性质。

## M5. 参考编码一致与点切向条件不同

取psi(X)=0、d=2、n=m=1、任意历史长度。令常量模型

    z_next = diag(a,rho) z + col(0,b) u,
    |a|<1, |rho|<1, b!=0.

原点（含零历史）为编码一致模型平衡点；完整Jacobian所有模态稳定，故可稳定化，且调度增益取零满足原结构。对任意当前编码状态潜槽为0，D(y,u)=-b u。
所以d0=0而输入方向DD=-b不为0：参考精确编码兼容且模型稳定，仍不提供原QP所有输入方向的二阶残差。若把u限制为0才有精确兼容，但这是额外执行限制，不是现有QP的自动性质。
此例无需改变论文规定的保测量提升，常量零特征可由编码头实现；它是结构反例，不描述训练结果。

## M6. 低维可实现方向与隐含执行约束

若允许域局部可由C²参数化s=s0+Jpar eta+O(||eta||²)，则直接缺陷的一阶导数为DD(s0)Jpar，必要的一阶抵消条件相应为0。但参数化必须覆盖所有可能执行解的信息/输入组合，不是只覆盖参考或shift名义。
若Jpar来自额外反馈u=k(y)，需要明确这是所分析控制律；不能把参考生成S4的辅助反馈强加到原QP最优输入上。若来自真实plant可实现窗口，则又需要独立plant/数据流证书。本报告不新增限制、不修改控制器。

## M7. 用已知残差容量反求允许的直接缺陷半径

设已通过B13得到某个预算w>=0，且nu_bar独立认证。E2要求内部缺陷容量

    Kcap=sqrt(w²-nu_bar²)-Lpsi nu_bar >=0,

其等价前提为nu_bar<=w/sqrt(1+Lpsi²)。若已知d0<=Kcap，M4的充分半径条件为

    d1 R+(HD/2)R² <= Kcap-d0.                     (M7)

HD>0时，明确可取

    0<=R<= [sqrt(d1²+2HD(Kcap-d0))-d1]/HD.         (M8)

HD=0、d1>0时用R<=(Kcap-d0)/d1；两者均零且d0<=Kcap时，任何已认证域半径都满足缺陷条件。若d0=Kcap且d1或HD正，M7只认证R=0；不能据此否定真实缺陷的更宽集合。
M8只解决残差这一关口。必须独立证明每个当前实际s位于该信息半径球，并同时保留B13的阶段域、终端、输入及初始化证书；J8首轮种子半径不能替代该永久覆盖。

## 验收与剩余门槛

M1提供当前编码图上的精确缺陷映射，M2保留抵消，M3给Hessian常数，M6给完整邻域二阶残差的必要一阶条件，M8把已知残差容量反解为信息域半径。
当前项目没有固定模型上的d0、DD、Hpsi/域证书、nu_bar及永久执行信息域覆盖。结构反例表明不能仅靠平滑/可稳定化/模型参考存在补出它们。下一步须实例证据或更具体的解析结构，不把本报告当作实际认证；B1 OPEN，P5 STOP。
````
