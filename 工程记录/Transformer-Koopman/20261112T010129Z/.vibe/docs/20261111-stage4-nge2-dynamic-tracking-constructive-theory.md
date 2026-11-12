# 第四阶段理论研究报告：一般预测时域下的可构造比较序列与动态参考闭环界

**日期：2026-11-11**  
**版本：Stage 4 / 研究稿，非论文正文**  
**核对基础：** `Main9_Stage3_IEEE_Polished.tex`（特别是 `eq:state_preserving_lifting`、`eq:augmented_state`、`eq:recursive_context`、`eq:recursive_predictor`、`eq:reencoding_residual`、`prop:contractive_class`）、Stage 1–3 研究报告、Baseline v2.3。  
**实施范围：**只进行理论推导；不修改第三/第四章，不做实验或数值认证。

> **本阶段的核心进展：**对于任意有限预测时域 **\(N\ge2\)**，利用第三章原有历史调度递归及公共同输入收缩性质，**显式构造**一个可行比较序列（即生成冻结矩阵时采用的标称输入序列），并给出由编码器 Lipschitz 常数、历史窗口长度、模型收缩率、参考动力学残差以及控制正则项构成的**可计算充分条件**。这填补了 Stage 3 中“假设某条比较序列有足够小的目标值”尚未由模型结构支持的缺口，但条件可能保守，**不代表任意机械臂和任意动态轨迹都已经获得指数跟踪保证**。

## 1. 不得改变的研究边界

- **实际预测模型不变：**第三章历史条件化 Transformer–Koopman 预测器，\(z=G_\theta(\mathcal X)=\operatorname{col}(x,\psi_\theta(\mathcal X))\)，历史记忆 \((a,v)\)，完整递归 \(q^+=F(q,u)\)。
- **研究目标不变：**跟踪真实动态参考轨迹 \(x_k^{\rm r}\)；参考编码 \(z_k^{\rm r}=G_\theta(\mathcal X_k^{\rm r})\)；不得转化为静态平衡点调节。
- **跟踪权重已锁定：**\(Q=\operatorname{diag}(Q_x,0)\)、\(Q_x\succ0\)，只惩罚前 \(n\) 个物理测量分量。
- **控制器仍直接优化输入：**无需预先求解 \(u^{\rm r}\)；旧第四章 \(u^b,q^b\) 及首输入稳态护栏不再作为前提。
- **内部状态分层：**完整模型展开可使用 \(q=(z,a,v)\)，冻结 QP 的预测和跟踪仅需 \(z\)；数学证明可使用缓存，但不强制跟踪 \(q^{\rm r}\)。
- **控制正则项依然开放：**以下以正定输入增量成本说明严格凸性，但比较论证对非负控制成本也适用，不能因此把 \(\Delta u\) 锁定为最终设计。

## 2. 本轮关键引理：沿标称输入，完整预测与冻结预测在整个时域精确一致

在时刻 \(k\)，任取符合输入约束的标称序列

\[
\bar U_k=\operatorname{col}(\bar u_{0|k},\ldots,\bar u_{N-1|k})\in\mathcal U^N.
\]

完整模型执行**一次**标称展开：

\[
\bar q_{0|k}=q_k^E,\qquad
\bar q_{i+1|k}=F(\bar q_{i|k},\bar u_{i|k}),
\]

\[
\bar A_{i|k}=A(c(\bar q_{i|k})),\quad
\bar B_{i|k}=B(C_x\bar z_{i|k}),\quad i=0,\ldots,N-1.
\]

这些矩阵冻结后，QP 使用

\[
z_{0|k}^{\rm fr}=z_k^E,\qquad
z_{i+1|k}^{\rm fr}=\bar A_{i|k}z_{i|k}^{\rm fr}+\bar B_{i|k}u_{i|k}.
\]

**引理 1（整条标称序列的精确一致性）。** 将 \(U=\bar U_k\) 代入冻结模型，则

\[
\boxed{z_{i|k}^{\rm fr}(\bar U_k)=\bar z_{i|k},\qquad i=0,\ldots,N.}
\]

**证明：**初值相同。若第 \(i\) 步相同，冻结模型在该步使用的矩阵正好由完整模型的标称状态 \(\bar q_{i|k}\) 计算，且输入同为 \(\bar u_{i|k}\)，所以两者 \(z\) 分块在第 \(i+1\) 步仍相同。归纳即得。**注意：**此结论只对选定的 \(\bar U_k\) 逐步精确一致，并非冻结模型对所有候选序列均与完整模型一致。

因此，对任意相同的升维参考轨迹以及仅依赖候选输入的控制正则项，

\[
\boxed{J_k^{\rm fr}(\bar U_k)=J_k^F(\bar U_k).}\tag{1}
\]

**重要意义：**\(\bar U_k\) 本来就在 \(\mathcal U^N\) 内，所以它自动是一条合法的比较序列；不需要先知道一条参考输入轨迹，也不需要一步物理输入矩阵满行秩。与上一阶段抽象的“存在比较序列”相比，这是直接从第三章和实际冻结算法导出的**具体构造**。

## 3. 定义参考历史一致性残差：只用动态参考和已知的输入历史

设历史窗口长度为 \(P_h\ge2\)，时刻 \(k\) 的参考测量历史是

\[
\mathcal X_k^{\rm r}=\operatorname{col}(x_{k-P_h+1}^{\rm r},\ldots,x_k^{\rm r}).
\]

对应参考升维坐标

\[
z_{k+i}^{\rm r}=G_\theta(\mathcal X_{k+i}^{\rm r}),\qquad i=0,\ldots,N.
\]

**用于理论比较、而非 MPC 跟踪目标的辅助历史状态：**在 \(k\) 时刻，输入缓存直接取实际已知的 \(v_k\)；未来输入缓存由同一标称序列 \(\bar U_k\) 递推：

\[
v_{0|k}^{\rm r}=v_k,\qquad
v_{i+1|k}^{\rm r}=S_uv_{i|k}^{\rm r}+E_u\bar u_{i|k}.
\]

测量缓存取参考轨迹自然产生的前 \(P_h-1\) 个参考测量 \(a_{i|k}^{\rm r}\)，并定义

\[
q_{i|k}^{\rm r}=\operatorname{col}\bigl(z_{k+i}^{\rm r},a_{i|k}^{\rm r},v_{i|k}^{\rm r}\bigr).
\]

**澄清：**\(q_{i|k}^{\rm r}\) 是证明用的比较对象，既不要求在 QP 内增加对它的跟踪代价，也不要求用户提供一条 \(u^{\rm r}\)。它的输入缓存取实际过去输入与既有标称候选的组合，而非假设已知某个真实参考输入序列。

定义逐步**参考动力学一致性残差**

\[
\boxed{d_{i|k}^{\rm r}
=q_{i+1|k}^{\rm r}-F(q_{i|k}^{\rm r},\bar u_{i|k}),\quad
\eta_{i|k}=\|d_{i|k}^{\rm r}\|_\Pi.}\tag{2}
\]

由于参考测量缓存按时间移位、输入缓存按 \(\bar u\) 移位，\(d_{i|k}^{\rm r}\) 的缓存分量实际上为零；不一致性进入升维 \(z\) 分块。这一残差同时衡量：给定参考轨迹是否符合模型、所选标称输入与参考运动是否匹配、以及参考历史编码与模型递推是否一致。

**特别重要：**\(d_{i|k}^{\rm r}\) 小不代表“已知参考输入”，它只说明我们已经有的**某条合法输入候选**使参考轨迹与模型比较相容。它通常对快速运动和大幅变换输入的机械臂参考不小；必须如实保留。

## 4. 模型专属的显式多步比较代价上界

### 4.1 需要明确核查的充分条件

在所分析区间内假定：

**A1.** 参考 \(x^\mathrm r\) 提供了编码器所需的全部测量分量和足够的历史；候选输入集合 \(\mathcal U\) 非空，\(\bar U_k\in\mathcal U^N\)。

**A2.** 所有参与比较的状态以及相应线段均在第三章的共同收缩域 \(\mathcal Q\) 内。\(F\) 对**相同输入**在 \(\Pi\)-范数下满足

\[
\|F(q,u)-F(\tilde q,u)\|_\Pi\le\lambda\|q-\tilde q\|_\Pi,\qquad 0\le\lambda<1.
\]

**A3.** 编码器在相关测量历史集合上一致 Lipschitz：

\[
\|G_\theta(X)-G_\theta(\tilde X)\|_2\le L_G\|X-\tilde X\|_2.
\]

**A4.** QP 包含所有 \(i=1,\ldots,N\) 的非负跟踪成本 \(\|z_{i|k}-z_{k+i}^{\rm r}\|_Q^2\)，控制成本 \(J_{\rm control}(U)\ge0\)，且求解器的可行解 \(\widehat U_k\) 满足相对冻结最优值的次优性差不超过 \(\delta_k\ge0\)。除输入限制以外暂不引入可能排除 \(\bar U_k\) 的额外约束。

**A5.** 实际重新编码更新保持第三章的形式 \(q_{k+1}^E=F(q_k^E,u_k)+w_k\)，且其物理残差 \(\omega_k=\|C_xw_k^z\|_{Q_x}\) 有界。

以上所有额外条件均需针对最终训练模型检查，不能因为本报告写出了它们就视为已经验证。

### 4.2 历史误差及显式常数

定义当前和历史的物理状态误差

\[
E_k=\|x_k-x_k^{\rm r}\|_{Q_x},\qquad
H_k=\max_{0\le j<P_h} E_{k-j}.
\]

记 \(E_z^\top q=z\)；采用第三章的 \(\Pi\succ0\)，定义

\[
b_y=\|Q_x^{1/2}C_x E_z^\top\Pi^{-1/2}\|_2,
\]

\[
\boxed{L_X=\sqrt{\lambda_{\max}(\Pi)}
\sqrt{\frac{P_h L_G^2+(P_h-1)}{\lambda_{\min}(Q_x)}}.}\tag{3}
\]

初始比较状态采用**相同实际输入历史**，因此输入缓存的初始差异为零；结合 \(G_\theta\) 的 Lipschitz 界及 \(a\) 为参考测量历史的移位分块，有

\[
\boxed{\|q_k^E-q_{0|k}^{\rm r}\|_\Pi\le L_XH_k.}\tag{4}
\]

参考完整状态不被要求是平衡点；它是一条随 \(i\) 变化的动态参考编码序列。

### 4.3 主引理：显式比较代价不等式

由完整标称递推、同输入收缩性及参考残差定义，

\[
\begin{aligned}
\|\bar q_{i+1|k}-q_{i+1|k}^{\rm r}\|_\Pi
&\le \lambda\|\bar q_{i|k}-q_{i|k}^{\rm r}\|_\Pi+\eta_{i|k},\\
\|\bar q_{i|k}-q_{i|k}^{\rm r}\|_\Pi
&\le \lambda^i L_XH_k+\sum_{j=0}^{i-1}\lambda^{i-1-j}\eta_{j|k}.
\end{aligned}
\tag{5}
\]

令

\[
D_{N,k}=\left[\sum_{i=1}^N
\left(\sum_{j=0}^{i-1}\lambda^{i-1-j}\eta_{j|k}\right)^2\right]^{1/2},
\]

\[
c_{U,k}=\sqrt{J_{\rm control}(\bar U_k)},\qquad
\boxed{\rho_N=b_yL_X\left(\sum_{i=1}^N\lambda^{2i}\right)^{1/2},}
\]

\[
\boxed{\beta_{N,k}=b_yD_{N,k}+c_{U,k}.}\tag{6}
\]

由于 \(C_x z_{k+i}^{\rm r}=x_{k+i}^{\rm r}\)，对整条标称输出轨迹有

\[
\left[\sum_{i=1}^N\|C_x\bar z_{i|k}-x_{k+i}^{\rm r}\|_{Q_x}^2\right]^{1/2}
\le\rho_N H_k+b_yD_{N,k}.
\]

结合 \(\sqrt{s^2+t^2}\le s+t\) 和引理 1，**对任意 \(N\ge1\)** 严格成立

\[
\boxed{\sqrt{J_k^{\rm fr}(\bar U_k)}
=\sqrt{J_k^{F}(\bar U_k)}
\le\rho_N H_k+\beta_{N,k}.}\tag{7}
\]

**这就是 Stage 3 缺失的显式 \(N\)-步比较输入序列构造**：比较输入是已选定的 \(\bar U_k\)，\(\rho_N\) 和 \(\beta_{N,k}\) 均由第三章模型性质、参考序列和标称控制正则项直接定义，不再无依据地假设“存在一条成本很小的神秘候选序列”。

### 4.4 主要定理：真实动态轨迹的条件性实用指数跟踪

**定理 1（显式比较序列下的动态参考跟踪界）。** 在 A1–A5 下，假设同一个 \(\rho_N\) 对所有采样成立且

\[
\boxed{\rho_N<1.}\tag{8}
\]

令 \(\widehat U_k\) 为 QP 可行返回，且 \(u_k=\widehat u_{0|k}\)。则

\[
\boxed{E_{k+1}\le\rho_NH_k+\beta_{N,k}+\sqrt{\delta_k}+\omega_k.}\tag{9}
\]

若存在统一上界 \(\beta_{N,k}\le\bar\beta_N\)、\(\delta_k\le\bar\delta\)、\(\omega_k\le\bar\omega\)，记

\[
b=\bar\beta_N+\sqrt{\bar\delta}+\bar\omega,\qquad B=\frac{b}{1-\rho_N},
\]

则对所有 \(k\ge0\)，

\[
\boxed{E_k\le H_k\le
B+\rho_N^{\lfloor k/P_h\rfloor}(H_0-B)_+.}\tag{10}
\]

**证明：**引理 1 使 \(\bar U_k\) 成为 QP 的合法比较输入且其完整/冻结目标完全相同。QP 最优性与次优性给出 \(J_k^{\rm fr}(\widehat U_k)\le J_k^{\rm fr}(\bar U_k)+\delta_k\)。由于跟踪目标包含第一步，且冻结第一步与完整模型在实际当前状态完全一致，

\[
E_{k+1}\le\sqrt{J_k^{\rm fr}(\widehat U_k)}+\omega_k
\le\sqrt{(\rho_NH_k+\beta_{N,k})^2+\delta_k}+\omega_k,
\]

再用 \(\sqrt{a^2+c^2}\le a+c\) 得到 (9)。对 \(H_k=\max_{0\le j<P_h}E_{k-j}\) 用 \(P_h\) 步最大值递推，即得 (10)：置 \(\widehat H_k=\max(H_k,B)\)，可证 \(\widehat H_{k+1}\le\widehat H_k\) 且 \(\widehat H_{k+P_h}\le B+\rho_N(\widehat H_k-B)\)，迭代即可。□

**精确解释：**这是一条对实际实施的动态参考 Frozen-LTV-QP 的**有条件、具体可检验的实用指数跟踪定理**。其正则项与参考动态缺陷经 \(\beta_{N,k}\) 显式进入误差下界。仅当全部扰动项为零且 (8) 等持续成立时，(10) 才退化为零误差指数收敛。对持续变化的动态参考，\(\beta\) 不应被默认置零。

### 4.5 精度要求可以直接转换为条件

如果需要理论上把最终历史误差压到 \(\varepsilon_{\rm tol}>0\) 内，充分条件是

\[
\boxed{\bar\beta_N+\sqrt{\bar\delta}+\bar\omega
\le(1-\rho_N)\varepsilon_{\rm tol}.}\tag{11}
\]

这使条件不再只是一句“扰动有界”：\(\beta\) 实际由参考动态残差和标称序列控制成本组成，允许判断该证明是否给出**有信息量**的跟踪精度。若误差邻域与参考幅值同量级，则虽然不等式正确，论文中仍不宜把它包装成强性能保证。

## 5. \(\rho_N\) 过于保守时：从实际模型雅可比获得更紧的检验量

式 (8) 是一个**充分条件而非必要条件**。它对整条 \(q\) 使用统一收缩率，又用编码器 Lipschitz 常数估计历史扰动，可能远大于真实输出敏感度。特别是 \(P_h\)、\(N\) 较大、\(\lambda\) 接近 1 时，\(\rho_N\) 很容易不小于 1，不能据此判定实际 MPC 不稳定。

可以直接考虑由第三章完整模型定义的**标称输出映射**：

\[
\mathscr Y_k(X;v_k,\bar U_k)
=\operatorname{col}(C_x\bar z_1(X),\ldots,C_x\bar z_N(X)),
\]

其中初值为 \(\operatorname{col}(G_\theta(X),a(X),v_k)\)，且保持 \(v_k,\bar U_k\) 不变。用窗口范数 \(\|\Delta X\|_{\rm hist}=\max_j\|\Delta x_j\|_{Q_x}\)、输出栈范数 \(\|\Delta Y\|_{\rm out}^2=\sum_{i=1}^N\|\Delta y_i\|_{Q_x}^2\)，定义沿真实参考窗口连线的雅可比上界

\[
\boxed{\rho_{N,k}^{\rm sens}=
\sup_{0\le t\le1}
\big\|D_X\mathscr Y_k(\mathcal X_k^{\rm r}+t(\mathcal X_k-\mathcal X_k^{\rm r});v_k,\bar U_k)
\big\|_{\rm hist\to out}.}\tag{12}
\]

由积分形式的中值定理，

\[
\|\mathscr Y_k(\mathcal X_k)-\mathscr Y_k(\mathcal X_k^{\rm r})\|_{\rm out}
\le\rho_{N,k}^{\rm sens}H_k.
\]

因此可以用 \(\rho_{N,k}^{\rm sens}\) 替换 (7)–(9) 的 \(\rho_N\)，如果能**严格证明** \(\sup_k\rho_{N,k}^{\rm sens}<1\) 即可得到相同形式的跟踪界。这项界可以通过 \(D_XG_\theta\) 与连乘 \(D_qF\) 构造，利用第三章完整调度的雅可比，通常比全局标量界更紧；但**只在单个采样点测到雅可比小于 1，不足以证明所有时刻与整条连线一致小于 1**。

这是后续需要检验的更有潜力的路径，特别适用于\(\lambda\) 较接近 1 的机械系统。

## 6. 当 \(m<n\) 时的多步可达性：一个独立且不混淆的结果

阶段 3 的 \(N=1\) 比较输入构造要求一步映射 \(C_xB(x_k)\) 满行秩，对许多机械臂不现实。但**本阶段定理 1 不需要这个条件**：它通过标称比较输入和参考残差得到界。

如果想进一步降低比较代价，还可以利用冻结模型的真正**多步可达性**。令冻结第 \(N\) 步物理预测

\[
C_xz_{N|k}(U)=\bar y_{N|k}+\mathcal G_{N,k}(U-\bar U_k),
\]

其中

\[
\mathcal G_{N,k}=
\big[\ C_x\bar A_{N-1|k}\cdots\bar A_{1|k}\bar B_{0|k},
\ldots,\ C_x\bar B_{N-1|k}\ \big]\in\mathbb R^{n\times Nm}.
\]

**引理 2（多步末端可达性）。** 若 \(\operatorname{rank}\mathcal G_{N,k}=n\)，且下面修正仍属于 \(\mathcal U^N\)，则

\[
\boxed{U_k^{\rm end}=\bar U_k+
\mathcal G_{N,k}^\dagger(x_{k+N}^{\rm r}-\bar y_{N|k})}
\tag{13}
\]

是一个显式可行序列，并在冻结模型下满足 \(C_xz_{N|k}(U_k^{\rm end})=x_{k+N}^{\rm r}\)。证明是 \(\mathcal G_{N,k}\mathcal G_{N,k}^\dagger=I_n\)。**可以有 \(m<n\) 而 \(Nm\ge n\)**；例如两步可控的双状态单输入结构并不要求一步输入矩阵满行秩。对非零小幅调度，合适的多步满秩性质也可由连续性保持。

**关键限制：**末端可以准确达到，不代表 \(1,\ldots,N-1\) 每步都准确跟踪，更不代表滚动实施的**第一个**输入一定使当前跟踪误差收缩。因此 (13) 是改进比较序列和分析可达性的工具，**不能单独升级为闭环稳定性定理**。

对所有冻结中间步，还可以**精确**写出

\[
C_xz_{i|k}(U_k^{\rm end})-x_{k+i}^{\rm r}
=\bar e_{i|k}-\mathcal G_{i,k}\mathcal G_{N,k}^\dagger\bar e_{N|k},
\]

其中 \(\bar e_{i|k}=C_x\bar z_{i|k}-x_{k+i}^{\rm r}\)，\(\mathcal G_{i,k}\) 为从整个控制向量 \(U\) 到第 \(i\) 步物理输出的冻结预测映射；在可行时可以直接评估该序列的真实 QP 比较代价，再与标称输入序列的代价取更小者。

## 6.1 小增益条件不是数学空集：一个保留历史调度且 \(m<n\) 的非空构造

为了避免出现“\(\rho_N<1\) 事实上不可能成立”的疑问，这里给出**数学结构的非空性说明**，不是对某个训练后机械臂的数值认证。

取 \(n=2,m=1,P_h=2,d=3\)，编码一致的升维为

\[
z=(x_1,x_2,\psi),\qquad \psi=\varepsilon x_{1,\mathrm{past}},
\]

测量缓存 \(a=(a_1,a_2)\)，输入缓存 \(v=u_{\mathrm{past}}\)，上下文 \(c=a_1+v\)，令

\[
A(c)=\begin{bmatrix}
\alpha+g_A\tanh(c)&0&0\\
0&\alpha_2&0\\
\varepsilon&0&0
\end{bmatrix},\qquad
B(x)=\begin{bmatrix}b+g_B\tanh(x_1)\\0\\0\end{bmatrix},
\]

并继续采用第三章的 \(a^+=x\)、\(v^+=u\)。两个非零增益 \(g_A,g_B>0\) 分别给出真正的历史依赖与测量依赖低秩调度。\(\psi^+=\varepsilon x_1=\varepsilon a_1^+\)，所以升维编码与历史移位递推相容。第一物理分量受一个输入控制，第二物理分量由稳定动态 \(x_2^+=\alpha_2x_2\) 自主演化，因此 \(m<n\)。

选正定权重 \(\Pi=\operatorname{diag}(I_3,\tau^2I_2,\tau^2)\)，其中 \(\tau>0\) 很小。在有界状态、输入域内，\(D_qF\) 的加权算子范数受到下列类型的项控制：

\[
\|D_qF\|_\Pi
\le c\bigl(|\alpha|+|\alpha_2|+\varepsilon+\tau
+g_A+g_A M/\tau+g_B M_u\bigr),
\]

其中 \(c\) 取决于固定的维数与有界域，\(M,M_u\) 是状态和输入界。选择 \(|\alpha|,|\alpha_2|,\varepsilon,g_A,g_B\) 与 \(\tau^2\) 同阶且**严格非零**，则右侧随 \(\tau\to0\) 趋零。可在足够小的有界输入集合与相容初值域内选取 \(0<\lambda<1/4\)，并维持共同不变域。

取 \(Q_x=I_2\)，\(L_G=1\)（当 \(\varepsilon\le1\) 时该线性历史 lift 的欧氏 Lipschitz 常数），\(b_y=1\)，\(L_X=\sqrt3\)。于是对**任意有限** \(N\ge2\)，

\[
\rho_N\le\sqrt3\,\frac{\lambda}{\sqrt{1-\lambda^2}}<1
\qquad(\lambda<1/4).
\]

这说明本阶段的小增益条件可与 \(N\ge2\)、\(m<n\) 和**非零历史调度**共存，并不是形式上自相矛盾的假设。然而，这一构造属于强收缩、第二状态自主稳定的数学特例，**绝不能据此推断一般机械臂或任意快速动态轨迹都满足该条件**。对于实际机械臂，仍需要更精细的历史输出敏感度或多步稳定性分析。

## 7. 不应掩盖的反例：\(N=2\)、完美可行的动态参考也不一定零误差跟踪

考虑**仅用于检验普遍性**的简单精确预测模型（不是替换论文第三章的实际模型）

\[
x_{k+1}=u_k,\qquad x_k^{\rm r}=(-1)^k,
\]

每个参考点均可由 \(u_k^{\rm r}=x_{k+1}^{\rm r}\) 实现；预测模型精确，同输入状态收缩率为 0。令 \(N=2\)，输入限制 \([-2,2]\)，\(Q_x=S=1\)，QP 采用两步物理跟踪和输入增量惩罚。记 \(s=x_{k+1}^{\rm r}\)（于是 \(x_{k+2}^{\rm r}=-s\)）以及 \(p=u_{k-1}\)，则

\[
J=(u_0-s)^2+(u_1+s)^2+(u_0-p)^2+(u_1-u_0)^2.
\]

一阶最优条件给出（该 QP 严格凸）

\[
\boxed{u_k^*=u_0^*=\frac{s+2u_{k-1}}5.}
\]

对于交替变化的参考，稳态两周期响应满足 \(u_k^*=a s\)，而 \(u_{k-1}=-a s\)，故 \(a=(1-2a)/5=1/7\)。最终

\[
\boxed{|x_{k+1}-x_{k+1}^{\rm r}|\longrightarrow\frac67\neq0.}
\]

这个分析性反例清楚表明：**即使轨迹完全可实现、预测完全准确、\(N=2\)、QP 严格凸、系统对状态天然收缩，只要输入增量惩罚与动态参考运动竞争，就不能一般性保证零误差轨迹跟踪。** 这不是否定输入增量惩罚，而是提醒论文的稳定性定理必须包含相应兼容性条件或明确非零跟踪误差界。

## 8. 本阶段得到了什么，仍缺什么？

### 已经完成的、可独立核验的数学结论

1. **任意 \(N\) 的整条标称轨迹精确一致**：\(z^{\rm fr}(\bar U_k)\equiv\bar z\)，从而 \(J^{\rm fr}(\bar U_k)=J^F(\bar U_k)\)。
2. **任意 \(N\ge2\) 的显式比较序列构造**：无需 \(C_xB\) 一步满行秩，比较输入直接选实际标称序列，误差上界由 (3)、(6) 给出。
3. **有明确常数与残差的动态参考实用指数跟踪充分条件**：(8)–(10)，针对真实重编码闭环，非旧静态平衡点分析。
4. **可提高可检验性但尚需认证的参考历史输出雅可比敏感度条件**：(12)，指明针对现有神经调度模型的具体下一步。
5. **\(m<n\) 仍可能具有 \(N\)-步末端可达性**；给出冻结模型的显式末端纠正输入及其可行性要求。
6. **严格的 \(N=2\) 反例**：展示为什么不能把本阶段的充分条件删去，直接宣称零误差指数跟踪。

### 不能宣称已完成的部分

1. 尚未对**用户实际训练出的模型参数**认证 \(L_G,\lambda,\rho_N\) 或 \(\rho_{N,k}^{\rm sens}\) 的统一数值界；因此不能断言所给机械臂对象满足 \(\rho_N<1\)。
2. 尚未证明对用户计划使用的全部动态参考轨迹都能获得足够小的 \(d_{i|k}^{\rm r}\)。若动态参考与可施加控制不匹配，这个残差可能很大。
3. 还未确定输入增量、输入幅值或两者组合的最终选择，以及是否需要终端机制或参考兼容性机制；不能把数学上可构造的充分条件误写成已经确认的最终控制器。
4. 多步末端可达性本身**不足以证明首输入滚动闭环稳定性**。若对实际参数无法认证 (8)/(12)，应转向适当的增量可稳定性 / Lyapunov / 终端设计，而不是沿用旧的名义稳态护栏。

### 下一阶段建议

**第一优先：**对第三章的完整 \(D_qF\)、\(D_XG_\theta\) 建立一个更紧的参考历史到预测输出的可认证雅可比界，而不是继续堆叠抽象假设。  
**第二优先：**分析输入增量惩罚是否满足目标动态轨迹的跟踪精度要求；尤其是参考变化较快、控制输入必须持续变化时的偏差。  
**第三优先：**如 \(\rho_N<1\) 过于严格，再根据实际系统的多步可控性研究终端设计或增量稳定性证明，但仍需尊重动态参考轨迹和第三章模型身份。

**正文修改状态：**没有改动论文；Section V 继续保持只有标题与标签。

## 9. 相关文献定位（参考，不构成本报告数学证明）

- Korda and Mezić, *Linear Predictors for Nonlinear Dynamical Systems: Koopman Operator Meets Model Predictive Control*, *Automatica* 93 (2018): 149–160. https://doi.org/10.1016/j.automatica.2018.03.046
- Köhler, Müller and Allgöwer, *Nonlinear Reference Tracking: An Economic Model Predictive Control Perspective*, *IEEE TAC* 64(1) (2019): 254–269. https://doi.org/10.1109/TAC.2018.2800789  （不修改基础跟踪 MPC 而研究可达参考的理论路线。）
- Köhler, Müller and Allgöwer, *Constrained Nonlinear Output Regulation Using Model Predictive Control*, arXiv:2005.12413 (2020). https://arxiv.org/abs/2005.12413  （不以求解离线调节器方程为控制器的必要前提；需要增量可稳定性、可检测性等额外条件。）
- Kessler and Fagiano, *On the Design of Linear Time Varying Model Predictive Control for Trajectory Stabilization*, *Automatica* 183 (2026), article 112577. https://doi.org/10.1016/j.automatica.2025.112577  （冻结/线性化轨迹 MPC 的当代相关方向；本文不能直接套用其证明。）

---

**一句话结论：**我们已经把“\(N\ge2\) 存在一条好比较序列”的抽象前提具体化为“**直接使用标称序列，并用原模型的历史窗口收缩与参考动力学一致性残差显式界定其代价**”；这是有条件但非空泛的真实动态轨迹跟踪证明路线，其实用性最终取决于能否对第三章实际模型核查小增益条件和参考兼容性缺陷。
