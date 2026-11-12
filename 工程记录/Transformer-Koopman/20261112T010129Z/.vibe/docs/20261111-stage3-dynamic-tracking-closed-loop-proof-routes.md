# 第三阶段理论研究报告：动态参考 Frozen-LTV-MPC 的实际闭环跟踪

> **状态：推导完成的条件性结果 + 已确认的反例 + 下一步需要证明的模型专属条件。**
> **日期：2026-11-11。**
> **核对对象：** `Main9_Stage3_IEEE_Polished.tex`（第三章的 `eq:recursive_predictor`、`eq:reencoding_residual`、`prop:contractive_class`），`Stage1_ChapterIII_z_q_Structure_Audit_CN.md`，`Stage2_Dynamic_Reference_Frozen_LTV_MPC_Theory_Design_CN.md`，Baseline v2.2。
> **范围：**理论研究；不改论文、代码，不进行实验。此文所称“定理”均指本阶段可验证的**条件性数学命题**，并非已证明第三章学习模型自动满足其新增条件。

## 1. 本阶段的三个主要结论

1. **不能从第三章的公共收缩性、冻结 QP 的严格凸性和第一步模型一致性直接推出动态轨迹指数跟踪。** 缺少的是“优化控制律在动态参考下令跟踪误差减小”的定量联系。
2. **对当前不加终端/护栏的动态跟踪 QP，可以建立一条不改变控制器的条件性实用指数跟踪定理。** 核心条件是存在一条可行的比较输入序列，其冻结目标值能由当前跟踪误差及参考/输入历史兼容性扰动控制。控制器自己仍通过单次冻结 QP **直接优化输入**；并不要求预先计算参考输入。
3. **更贴合 Transformer 的证明状态应考虑最近 `P_h` 步的物理误差，而非只用当前 `x_k-x_k^r`。** 这不表示 MPC 必须跟踪整个 `q`，仅表示基于历史窗口的模型可能受到过去误差影响。建立了一个 `P_h` 步收缩的条件性证明，速率约为 `ρ^(1/P_h)`。

## 2. 与实际第三章一致的闭环对象

令 `P_h` 为测量历史长度。实际模型不是普通固定 Koopman 矩阵，而是

\[
 z_k^E=G_\theta(\mathcal X_k)=\operatorname{col}(x_k,\psi_\theta(\mathcal X_k)),
 \qquad q_k^E=\operatorname{col}(z_k^E,a_k,v_k),
\]

\[
 F(q,u)=\operatorname{col}\big(A(c(q))z+B(C_xz)u,\ S_xa+E_xC_xz,\ S_uv+E_uu\big),
 \quad q_{k+1}^E=F(q_k^E,u_k)+w_k,
\]

其中 `w_k=col(w_k^z,0,0)`，`C_x=[I_n\ 0]`。本阶段只跟踪 `x_k`，不强迫定义完整的 `q_k^r`。

在采样 `k`，完整模型沿标称序列仅展开一次，冻结未来 `\bar A_{i|k},\bar B_{i|k}`，在 QP 内预测

\[
 z_{0|k}=z_k^E,\qquad z_{i+1|k}=\bar A_{i|k}z_{i|k}+\bar B_{i|k}u_{i|k}.
\]

参考历史可编码为 `z_{k+i}^r=G_θ(\mathcal X_{k+i}^r)`，跟踪权重已由作者锁定：

\[
 Q=\operatorname{diag}(Q_x,0),\quad Q_x\succ0,
 \qquad \|z_{i|k}-z_{k+i}^r\|_Q^2
 =\|C_xz_{i|k}-x_{k+i}^r\|_{Q_x}^2.
\]

先以第二阶段严格凸的**候选**目标作为分析载体：

\[
 J_k^{\mathrm{fr}}(U)=\sum_{i=1}^{N}\|C_xz_{i|k}-x_{k+i}^r\|_{Q_x}^2
 +\sum_{i=0}^{N-1}\|\Delta u_{i|k}\|_S^2,\qquad S\succ0,
\]

`\Delta u_{0|k}=u_{0|k}-u_{k-1}`，其余为相邻预测输入之差；`u_{i|k}\in\mathcal U`，`\mathcal U` 非空紧凸。**输入增量惩罚不是最终固定设计**；本次推导也可对任何非负、使 QP 有适当解的控制正则项采用对应的比较代价条件。

由于第一步冻结系数在当前真实编码状态计算，对于实际施加的 `u_k=\hat u_{0|k}`，有**精确关系**

\[
 e_{k+1}:=x_{k+1}-x_{k+1}^r
 =\big(C_xz_{1|k}-x_{k+1}^r\big)+C_xw_k^z.
 \tag{1}
\]

定义 `E_k=\|e_k\|_{Q_x}`、`\omega_k=\|C_xw_k^z\|_{Q_x}`。若求解器返回原问题可行输入且冻结目标次优性至多 `\delta_k\ge0`，则对**任意可行**比较序列 `U_k^{\rm cmp}`，有

\[
 E_{k+1}\le \sqrt{J_k^{\rm fr}(\widehat U_k)}+\omega_k
 \le\sqrt{J_k^{\rm fr}(U_k^{\rm cmp})+\delta_k}+\omega_k.
 \tag{2}
\]

这才是后续稳定性结果的直接出发点；它不依赖旧的名义稳态选择器。

## 3. 必须首先说明的反例：物理误差为零未必下一步仍为零

即便是稳定的、精确的预测模型，输入增量惩罚仍可能让 `e_k=0` 的状态产生下一步误差。考虑**仅用于揭示数学机制的标量示例**（不是将本文实际模型替换为此模型）：

\[
 x_{k+1}=\tfrac12 x_k+u_k,\quad r_k\equiv0,\quad x_k=0,\quad u_{k-1}=1,
\]

令 `N=1, Q_x=S=1`，输入约束包含 `[0,1]`。QP 为

\[
 \min_{u\in\mathcal U}u^2+(u-1)^2,
 \qquad u_k^*=\tfrac12,
 \qquad x_{k+1}=\tfrac12.
\]

尽管 `e_k=0`，但 `e_{k+1}=1/2`。因此，不可能只根据 `e_k` 对**所有过去输入历史**宣称同质估计 `E_{k+1}\le\rho E_k`，即使 `|1/2|<1`、模型精确、QP 严格凸、冻结第一步准确。

**含义：**若正则项惩罚 `\Delta u`，过去输入是闭环控制器的内部状态。物理输出仍是唯一跟踪目标；但稳定性证明可能必须额外考虑输入历史失配，或把它归入可量化的外部/参考兼容性项。仅凭 `x_k=x_k^r`，既不能确定 Transformer 历史特征一致，也不能确定 MPC 下一步仍精确跟踪。

## 4. 定理候选 A：不修改 QP 的动态参考实用指数跟踪

### 4.1 可检验的比较序列充分条件

假设预测/实际状态始终在第三章允许的分析域内，且对于所有待分析时刻，存在**可行**的比较序列 `U_k^{\rm cmp}\in\mathcal U^N` 和**统一常数** `0\le\rho<1`，满足

\[
 \boxed{J_k^{\rm fr}(U_k^{\rm cmp})\le(\rho E_k+\beta_k)^2,\qquad \beta_k\ge0.}
 \tag{C1}
\]

这一条件衡量参考轨迹在现有预测模型、输入约束及输入正则项下的**有限时域代价可控性（cost controllability）**。它不是第三章现有公共收缩性的推论；必须通过可行候选构造、系统结构或后续验证来建立。

### 4.2 命题与完整证明

**命题 A（条件性动态轨迹实用指数跟踪）。** 假定 (1)–(2) 成立，求解器每步返回可行解，目标次优性至多 `\delta_k`，并满足 (C1)。则

\[
 \boxed{E_{k+1}\le\rho E_k+\beta_k+\sqrt{\delta_k}+\omega_k.}
 \tag{3}
\]

若 `\beta_k\le\bar\beta`、`\delta_k\le\bar\delta`、`\omega_k\le\bar\omega`，则

\[
 \boxed{E_k\le\rho^k E_0+
 \frac{1-\rho^k}{1-\rho}
 (\bar\beta+\sqrt{\bar\delta}+\bar\omega).}
 \tag{4}
\]

**证明。** 由 (2)、(C1) 及 `\sqrt{a^2+b^2}\le a+b`（`a,b\ge0`），

\[
 E_{k+1}\le\sqrt{(\rho E_k+\beta_k)^2+\delta_k}+\omega_k
 \le\rho E_k+\beta_k+\sqrt{\delta_k}+\omega_k.
\]

递推即得 (4)。证毕。

**严格解释：**这是动态参考的跟踪误差界，未引入逐时刻静态平衡点。若 `\beta_k=\delta_k=\omega_k=0` 且 (C1) 真正成立，则给出零误差的指数跟踪；若这些项仅趋零，可在有界条件下得到渐近收敛，但未给出收敛速率时不能声称指数收敛。对一般动态参考，本阶段支持的是 (4) 的**条件性实用指数跟踪**。

## 5. 定理候选 B（更推荐）：针对 Transformer 历史窗口的 `P_h` 步收缩

仅用 `E_k` 的条件 (C1) 可能过强：`z_k^E` 和调度上下文依赖 `\mathcal X_k` 的整个窗口。即使 `E_k=0`，最近的其他 `P_h-1` 个误差仍能改变下一步预测。

因此定义**历史物理跟踪误差**

\[
 H_k=\max_{0\le j<P_h} E_{k-j},
 \quad\text{假设初始参考历史窗口已给定。}
 \tag{5}
\]

这里 `H_k` 是**用于证明的误差量**，不是要求 MPC 跟踪增广状态 `q`，更不是将 Q 权重扩展到 Transformer 特征。

用以下较合理的候选代价条件替换 (C1)：

\[
 \boxed{\exists U_k^{\rm cmp}\in\mathcal U^N:\quad
 J_k^{\rm fr}(U_k^{\rm cmp})\le(\rho H_k+\beta_k)^2,
 \qquad0\le\rho<1.}
 \tag{C2}
\]

则第一步比较立即给出

\[
 \boxed{E_{k+1}\le\rho H_k+\beta_k+\sqrt{\delta_k}+\omega_k.}
 \tag{6}
\]

**命题 B（历史窗口实用指数跟踪）。** 进一步假定存在统一 `b\ge0`，使 `\beta_k+\sqrt{\delta_k}+\omega_k\le b`，令 `B=b/(1-\rho)`。则

\[
 \boxed{E_k\le H_k\le B+\rho^{\lfloor k/P_h\rfloor}(H_0-B)_+,\qquad k\ge0,}
 \tag{7}
\]

这里 `(t)_+=\max\{t,0\}`。特别地，`b=0` 时 `H_k\le\rho^{\lfloor k/P_h\rfloor}H_0`；对动态参考在此条件下实现**按历史窗口块递减的指数跟踪**。

**证明。** 置 `\widehat H_k=\max\{H_k,B\}`。由 (6)，

\[
 E_{k+1}\le\rho\widehat H_k+b\le\widehat H_k,
\]

且 `H_{k+1}` 的其余元素来自前一窗口，因此 `\widehat H_{k+1}\le\widehat H_k`。对接下来的 `P_h` 个采样，均有 `E_{k+j}\le\rho\widehat H_k+b`，`1\le j\le P_h`。在时刻 `k+P_h`，旧窗口已全部移出，于是

\[
 H_{k+P_h}\le\rho\widehat H_k+b,
 \quad\widehat H_{k+P_h}\le B+\rho(\widehat H_k-B).
\]

迭代每个 `P_h` 步，并利用中间时刻 `\widehat H` 单调不增，得到

\[
 \widehat H_k\le B+\rho^{\lfloor k/P_h\rfloor}(\widehat H_0-B)
 =B+\rho^{\lfloor k/P_h\rfloor}(H_0-B)_+.
\]

因 `E_k\le H_k\le\widehat H_k`，证毕。

**这个结果的意义：**历史模型可能先受到旧测量误差的影响，不能要求误差每一步都立即按 `\rho` 缩小；但如果每一步的最优预测代价都能由最近 `P_h` 步的误差压住，则旧误差移出窗口后，误差每个历史长度至少衰减一轮。它与作者想要的**物理状态轨迹跟踪**完全一致。

## 6. (C2) 是否空洞？一个利用实际历史调度结构的可构造情形

本节给出一个**明确的、但比较严格的充分情形**，说明 (C2) 不只是重复结论。先取 `N=1`，随后强调为什么不能把它当成一般机械臂模型的最终证明。

定义第三章模型的**一步物理预测映射**（缓存中的输入历史 `v` 与当前候选输入 `u` 区分开）：

\[
 p(\mathcal X,v,u)=
 C_x\{A(C_\phi(\mathcal X,v))G_\theta(\mathcal X)
 +B(x_{\rm last})u\}.
 \tag{8}
\]

它仍然使用真正的 Transformer 编码器与历史调度矩阵。设对固定合法 `(v,u)`，该映射关于完整测量窗口局部一致 Lipschitz：

\[
 \|p(\mathcal X,v,u)-p(\mathcal X',v,u)\|_2
 \le L_p\|\mathcal X-\mathcal X'\|_2.
 \tag{9}
\]

此条件可由 `G_θ`、`C_φ`、调度头在紧域上的导数界推导，但具体统一常数在本阶段**尚未计算**。令 `H_k^u=C_xB(x_k)\in\mathbb R^{n\times m}`。假定其满行秩，存在右逆 `R_k`，满足

\[
 H_k^u R_k=I_n,
 \qquad\|S^{1/2}R_k\|_2\le\mu.
 \tag{10}
\]

只使用**实际已有的历史输入** `u_{k-1}`，构造用于理论比较的输入

\[
 u_k^{\rm cmp}=u_{k-1}+
 R_k\big[x_{k+1}^r-p(\mathcal X_k,v_k,u_{k-1})\big].
 \tag{11}
\]

假设这一输入满足 `u_k^{\rm cmp}\in\mathcal U`。则直接由 (10) 得到

\[
 p(\mathcal X_k,v_k,u_k^{\rm cmp})=x_{k+1}^r.
\]

因此当 `N=1` 时该比较序列的下一步跟踪成本为**零**，总成本只剩输入增量项：

\[
 \sqrt{J_k^{\rm fr}(u_k^{\rm cmp})}
 =\|u_k^{\rm cmp}-u_{k-1}\|_S.
\]

定义**参考与当前输入历史的兼容性缺陷**

\[
 d_k=\|x_{k+1}^r-p(\mathcal X_k^r,v_k,u_{k-1})\|_2.
 \tag{12}
\]

`d_k` 的计算只需要期望测量窗口和**实际已知的**过去输入，无需先构造一条 `u^r` 参考输入轨迹。注意 `d_k` 不等于参考轨迹的物理不可实现性：它只衡量“当前保留的历史输入”与下一参考点是否兼容。

由 (9)、(11)–(12)、`\|\mathcal X_k-\mathcal X_k^r\|_2\le\sqrt{P_h/\lambda_{\min}(Q_x)}H_k`，有

\[
 \sqrt{J_k^{\rm fr}(u_k^{\rm cmp})}
 \le \underbrace{\frac{\mu L_p\sqrt{P_h}}{\sqrt{\lambda_{\min}(Q_x)}}}_{\rho}
 H_k+\underbrace{\mu d_k}_{\beta_k}.
 \tag{13}
\]

当 `\rho<1`、比较输入始终合法、`d_k` 有界时，(C2) 成立，命题 B 可以应用；这里的 `p` 包括第三章**完整历史依赖**，不是用固定常系数模型代替原文。

**关键限制必须直说：**这个构造使用 `C_xB(x_k)` 满行秩且当前一步就能控制全部物理测量分量。对于许多机械臂状态（例如把关节位置与速度一起测量、输入仅为关节力矩），通常 `m<n` 或离散化后控制输入对位置的一步直接作用不足，所以 (10) 不成立。`N=1` 也不体现真正的多步冻结近似。**因此 (13) 证明了该路线存在可构造的充分情形，却不是现有高维 Transformer–Koopman 模型已经满足 (C2) 的证据。** 下一步需要在 `N\ge2`、可能欠驱动/高相对阶的情形下，研究预测时域内的比较序列及多步可控性。

## 7. 为什么不直接照搬经典 MPC 的值函数平移证明？

一种经典轨迹跟踪证明尝试是把前次最优输入序列整体左移，并在末端补上一个控制输入，获得下一时刻的可行候选，再证明最优值函数下降。但本模型有三个额外难点：

1. **跨采样调度矩阵变化。** `k+1` 时需要从新的 `q_{k+1}^E` 完整展开并冻结，得到的新 `\bar A_{i|k+1},\bar B_{i|k+1}` 一般不等于 `k` 时冻结系数的平移。即使无重新编码误差，下一次重新求得的标称序列也可能与原最优预测轨迹不同。
2. **动态参考的相容性与尾部。** 平移候选涉及 `x_{k+N+1}^r` 及下一时刻的输入约束/终端可行性，必须明确完整的参考预览和尾部假设。
3. **`\Delta u` 正则导致零误差处的目标值不一定为零。** 即使整条物理参考能够准确实现，变化的维持输入也可能产生非零增量成本，普通 `V_k\simeq\|e_k\|^2` 的 Lyapunov 界不能不加处理地成立。上面的反例已经展示这一障碍。

目前有两条认真值得继续研究的方向：

- **路径 A（优先）：**保持当前基础 QP，建立适用于 `N\ge2`、历史窗口与输入约束的**比较序列代价界 (C2)**，得到条件性但尽可能可检验、非空洞的实际动态跟踪定理。
- **路径 B（备选）：**如果 A 的附加假设对机械臂等对象过强，再考虑增量可稳定性下的值函数/终端设计。只借用成熟轨迹跟踪 MPC 的证明思想，不将旧第四章名义稳态约束恢复为默认结构。

如果以后希望增加“下一步输出误差带”约束，冻结第一步的线性性确实允许保留 QP；但它可能因相对阶、输入维数和约束变紧而不可行，必须在作者认可且完成可行性分析后再考虑。

## 8. 与经典文献的关系（仅为理论路径参考，不替代本研究推导）

- **Korda and Mezić**, “Linear Predictors for Nonlinear Dynamical Systems: Koopman Operator Meets Model Predictive Control,” *Automatica* 93 (2018), 149–160. DOI: https://doi.org/10.1016/j.automatica.2018.03.046 。支持 Koopman 预测—凸 MPC 的基本控制结构，但其线性预测器的控制应用不能直接提供本模型的动态历史调度闭环证明。
- **Köhler, Müller and Allgöwer**, “Nonlinear Reference Tracking: An Economic Model Predictive Control Perspective,” *IEEE Transactions on Automatic Control* 64(1) (2019), 254–269. DOI: https://doi.org/10.1109/TAC.2018.2800789 。研究了可达参考轨迹和无终端成分的轨迹跟踪充分条件，表明这是一条成熟的理论路线；需要增量可稳定性、参考条件等，不能直接把结论套到冻结重编码模型。
- **Köhler, Müller and Allgöwer**, “A Nonlinear Model Predictive Control Framework Using Reference Generic Terminal Ingredients,” *IEEE Transactions on Automatic Control* 65 (2020), 3576–3583. DOI: https://doi.org/10.1109/TAC.2019.2949350 。研究动态可达参考及参考通用的终端成分，提供备选终端证明思路；其理论设置通常显式定义动力学可达状态–输入参考，因此与本文当前“无需预先提供参考输入的基本 MPC”应区分。

## 9. 本轮判断与下一阶段任务

### 本轮已经严格完成

- 明确了仅凭旧第三章收缩命题无法推出新 QP 的动态跟踪稳定性；给出在**稳定模型、准确预测、严格凸 QP**下仍可能离开零误差集的反例。
- 对**未经修改的动态参考 Frozen-LTV-QP**，证明了比较序列充分条件下的实用指数跟踪命题 A。
- 提出了更符合 Transformer 历史窗口的命题 B，证明了每 `P_h` 步的收缩界和明确的指数率。
- 给出保留第三章历史调度结构的 `N=1` 可构造比较输入充分情形；其限制（一步满行秩）已显式说明。

### 仍未证明、不能写成论文定理的关键环节

1. **对当前第三章高维模型和一般 `N\ge2` 构造比较输入序列，验证 (C2) 的统一 `\rho<1`。** 这是迈向可用于论文的主定理的首要缺口。
2. **检查一般机械臂的相对阶/输入维数：**很多机械系统不满足一步输出可逆条件，需要多步比较或不同 Lyapunov 工具。
3. **给出可估计的 `\beta_k` 上界**，明确参考动态变化、真实输入历史、潜在特征误差与受限可达性各自贡献，而不是将所有困难隐藏在一个常数里。
4. **确定输入正则项及终端机制。** `\Delta u` 的历史状态效应已经得到数学反例证实；后续要评估其与零误差轨迹跟踪定理的相容性。
5. **重新编码与冻结误差：**实际下一步显式只受 `w_k` 影响，但多步冻结对所选控制输入的影响隐含在成本/比较条件中，不能遗漏，也不能误称“冻结与闭环无关”。

**本轮决策建议：保留第二阶段的基础动态跟踪 QP 作为研究对象；首先研究可构造的 `N\ge2` 历史感知比较序列或增量可稳定性条件。暂不增加稳态输入选择器、输入护栏或新的终端等式。**

> **防偏离总结：**物理 `x` 是最终跟踪对象，`z` 是 Koopman 预测/跟踪代价的空间，历史缓存是完整调度预测的记忆，MPC 自己求输入。闭环定理必须对实际 `q^E\to F\to` 重新编码过程及未来**动态参考**成立，不能从静态工作点替代得到。
