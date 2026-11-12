# 输出跟踪 Single-Freeze Transformer–Koopman MPC：完整条件数学证明

日期：2026-11-10。用途：独立理论材料，供后续数学复核及论文写作使用；**不是论文修订稿**。

## 0. 证明对象与最终结论

本文固定如下控制器：历史初始化、一次完整标称 rollout、一次系数冻结、一个输出跟踪/输入增量 QP、施加返回序列首输入、移位并重复末端输入。参考数据只有期望测量输出，不引入参考输入或参考增广状态。

在明确的统一模型、残差、输入和参考条件下，完整证明：

1. 每拍 QP 存在唯一最优解；原始可行性递归保持，实际编码状态及所有相关预测保持在分析域。
2. **Route 0：**编码状态有界，测量输出误差一致最终有界；这不依赖 MPC 最优性。
3. **Route 1：**建立相邻冻结 QP 的值比较，显式保留尾部代价；由此得到有限时间性能不等式、长期平均误差界及逐时刻界。

“证明闭合”指结论由所列条件逐步推出，不代表任意训练模型或真实系统已满足这些条件。特别是，统一残差界不能由训练损失自动推出。本文不主张 ISS、无条件指数跟踪或隐藏物理状态稳定性。

全文不改变论文/代码，不讨论新增控制机制。主要依赖链为：

> 定义与条件 → 缓存/冻结恒等式 → QP 良定性与域归纳 → Route 0；
> 域归纳 + 代价连续性 + 移位轨迹比较 → 尾部记账 → 值比较 → Route 1。

§10给出模型条件的结构性充分条件，§11给出求解差距证书，§12集中检查边界与可宣称范围。它们不作为未展开的黑箱代替主证明。

## 1. 对象、维度与预测模型

### 1.1 历史与编码状态

测量为 $x_k\in\mathbb R^n$，输入为 $u_k\in\mathbb R^m$，历史长度 $P_h\ge2$，提升维数 $d\ge n$。令 $L=P_h-1$，并定义
\[
\begin{aligned}
\mathcal X_k&=\operatorname{col}(x_{k-L},\ldots,x_k)\in\mathbb R^{(L+1)n},\\
a_k&=\operatorname{col}(x_{k-L},\ldots,x_{k-1})\in\mathbb R^{Ln},\\
v_k&=\operatorname{col}(u_{k-L},\ldots,u_{k-1})\in\mathbb R^{Lm},\\
z_k^E&=G_\theta(\mathcal X_k)
=\operatorname{col}(x_k,\psi_\theta(\mathcal X_k))\in\mathbb R^d,\\
q_k^E&=\operatorname{col}(z_k^E,a_k,v_k)\in\mathbb R^{s_q},
\qquad s_q=d+L(n+m).
\end{aligned} \tag{D1}
\]

上标 $E$ 表示实际测量历史重新编码后的状态。预测状态不要求落在编码器像集上。

令 $C_x=[I_n\ 0]\in\mathbb R^{n\times d}$、$E_z=\operatorname{col}(I_d,0,0)\in\mathbb R^{s_q\times d}$，以及
\[
C_m=C_xE_z^\top,\qquad x_k=C_mq_k^E. \tag{D2}
\]

$E_{\rm prev}\in\mathbb R^{m\times s_q}$ 提取 $v$ 的最后一个输入块，故 $E_{\rm prev}q_k^E=u_{k-1}$。实际输入历史是已知数据，不是参考输入。

### 1.2 完整递推与冻结族

$S_x,S_u$ 为丢弃最早一块的左移矩阵，$E_x,E_u$ 分别向缓存末尾注入测量和输入。因此 $S_x\in\mathbb R^{Ln\times Ln}$、$E_x\in\mathbb R^{Ln\times n}$，输入侧维数相应为 $Lm$；$L=1$ 时两个移位矩阵均为零。

对于 $q=\operatorname{col}(z,a,v)$，context映射为 $C_\phi:\mathbb R^{(L+1)n+Lm}\to\mathbb R^{d_c}$，令
\[
c(q)=C_\phi(\operatorname{col}(a,C_xz),v),\qquad
F(q,u)=\operatorname{col}\bigl(A(c(q))z+B(C_xz)u,\ S_xa+E_xC_xz,\ S_uv+E_uu\bigr).
\tag{D3}
\]

$A(c)\in\mathbb R^{d\times d}$，$B(x)\in\mathbb R^{d\times m}$。固定部署模型是确定性的；每个采样时刻只对实际历史调用 $G_\theta$，完整预测通过 $F$ 递归更新历史和 context，不在预测每一步重编码 latent。

对冻结点 $\bar q$，定义
\[
\begin{aligned}
M(\bar q)&=\begin{bmatrix}A(c(\bar q))&0&0\\ E_xC_x&S_x&0\\0&0&S_u\end{bmatrix},\\
D(\bar q)&=\operatorname{col}(B(C_m\bar q),0,E_u),\\
F_{\bar q}^{\rm fr}(q,u)&=M(\bar q)q+D(\bar q)u.
\end{aligned} \tag{D4}
\]

这是系数冻结，不是 $F$ 的 Jacobian 线性化。$F(q,u)$ 对固定 $q$ 的当前输入仿射；但候选输入会改变后续调度，完整多步优化一般非线性。

### 1.3 范数

对 $\Pi\succ0$，记 $\|q\|_\Pi=(q^\top\Pi q)^{1/2}$，同空间线性映射的诱导范数为 $\|T\|_\Pi=\|\Pi^{1/2}T\Pi^{-1/2}\|_2$。无下标的矩阵二范数均为谱范数。$\Pi$ 仅用于模型分析，不是下面的输出跟踪权重。

## 2. 固定的在线控制器

### 2.1 参考与代价

参考为绝对时间序列 $\{x_t^r\}_{t\ge0}\subset\mathbb R^n$。第 $k$ 次优化使用窗口 $x^r_{k:k+N}$；相邻窗口对同一绝对时刻的参考值一致。下一时刻新增的 $x^r_{k+N+1}$ 不要求提前用于当前 QP。

取整数 $N\ge1$、$Q\in\mathbb R^{n\times n}\succ0$、$S\in\mathbb R^{m\times m}\succ0$。定义
\[
\ell_t(p,u)=\|C_mp-x_t^r\|_Q^2+\|u-E_{\rm prev}p\|_S^2,
\qquad V_f(t,p)=\|C_mp-x_t^r\|_Q^2. \tag{C1}
\]

阶段输出与终端输出使用同一权重。输入增量项为软惩罚；唯一在线硬约束是 $u\in\mathcal U$。

### 2.2 单次标称展开及 QP

持有标称输入序列 $\bar U_k\in\mathcal U^N$，一次计算
\[
\bar q_{0|k}=q_k^E,\quad
\bar q_{i+1|k}=F(\bar q_{i|k},\bar u_{i|k}),\quad
M_{i|k}=M(\bar q_{i|k}),\quad D_{i|k}=D(\bar q_{i|k}),\quad 0\le i<N.
\tag{C2}
\]

对所有候选 $U=\operatorname{col}(u_{0|k},\ldots,u_{N-1|k})$，保持这些矩阵固定：
\[
\begin{aligned}
\min_U\quad &J_k^{\rm fr}(U;\bar U_k)
=\sum_{i=0}^{N-1}\ell_{k+i}(p_{i|k},u_{i|k})+V_f(k+N,p_{N|k})\\
\text{s.t.}\quad &p_{0|k}=q_k^E,\\
&p_{i+1|k}=M_{i|k}p_{i|k}+D_{i|k}u_{i|k},\quad 0\le i<N,\\
&u_{i|k}\in\mathcal U,\quad 0\le i<N.
\end{aligned} \tag{C3}
\]

$p$ 由 $U$ 唯一确定，不是额外独立决策变量；不施加 $p\in\mathcal Q$ 约束。记该 QP 的真实最优值为 $W_k$。

### 2.3 实施及记忆更新

求解器返回原始可行的 $\widehat U_k$，执行
\[
u_k=\widehat u_{0|k},\qquad
\bar U_{k+1}=\operatorname{col}(\widehat u_{1|k},\ldots,\widehat u_{N-1|k},\widehat u_{N-1|k}).
\tag{C4}
\]

$N=1$ 时右侧仅为 $\widehat u_{0|k}$。下一次冻结点必须由这条实际返回序列的规定移位生成，不混入另一条 warm start。

初始化使用真实、一致的测量/输入历史，$u_{-1}\in\mathcal U$，及任意 $\bar U_0\in\mathcal U^N$。所有所需过去输入均为已实施的可行输入。

严格说 $W_k=W(q_k^E,\bar U_k,x^r_{k:k+N})$。省略参数只为排版，不把带标称序列记忆的闭环误写成仅以 $q_k^E$ 为状态的自治控制律。

## 3. 条件与量词

**H1（数据与权重）。** $\mathcal U=\{u:H_uu\le h_u\}$ 是非空紧凸多面体；权重与初始化如§2。存在 $\bar r<\infty$ 使 $\|x_t^r\|_2\le\bar r$ 对所有 $t\ge0$ 成立。不要求参考在模型或真实系统中可实现。

**H2（公共模型界）。** 固定 $\Pi\succ0$、$M>0$ 和 $\mathcal Q=\{q:\|q\|_\Pi\le M\}$，$F$ 在该域和所需输入上有定义。存在时间无关常数 $0\le\lambda,\lambda_{\rm fr}<1$、$b_u,\bar\eta\ge0$，对所有 $q,q',\bar q\in\mathcal Q$ 与 $u\in\mathcal U$，
\[
\begin{aligned}
\|F(q,u)-F(q',u)\|_\Pi&\le\lambda\|q-q'\|_\Pi,\\
\|F_{\bar q}^{\rm fr}(q,u)-F_{\bar q}^{\rm fr}(q',u)\|_\Pi&\le\lambda_{\rm fr}\|q-q'\|_\Pi,\\
\|F(0,u)\|_\Pi,\quad\|F_{\bar q}^{\rm fr}(0,u)\|_\Pi&\le b_u,\\
\|F(q,u)-F_{\bar q}^{\rm fr}(q,u)\|_\Pi&\le\bar\eta.
\end{aligned} \tag{H2}
\]

这里的冻结界覆盖**整个**由 $\mathcal Q$ 生成的冻结族，不能只检查当前一次 rollout。

**H3（测量转移与残差）。** 对当前 $q_k^E\in\mathcal Q$ 和任意实际施加的可行输入，测量转移存在，且
\[
q_{k+1}^E=F(q_k^E,u_k)+w_k,\qquad
w_k=\operatorname{col}(r_k,0,0),\qquad\|w_k\|_\Pi\le\bar w.
\tag{H3}
\]

输入准确施加，缓存按实际测量和已施加输入准确更新。零缓存残差来自记账结构，并非假定编码器像集在 $F$ 下不变。$r_k$ 可同时包含测量预测误差及潜变量重编码误差。

**H4（初值与半径）。**
\[
q_0^E\in\mathcal Q,\qquad
\lambda M+b_u+\bar w\le M,\qquad
\lambda_{\rm fr}M+b_u\le M. \tag{H4}
\]

残差界须对上述完整域内的实际转移有效；不能先在小域估计残差，再任意扩大 $M$。

**H5（可行返回及目标差距）。** 返回序列属于 $\mathcal U^N$，并使用有效上界
\[
0\le J_k^{\rm fr}(\widehat U_k;\bar U_k)-W_k\le\delta_k\le\bar\delta<\infty.
\tag{H5}
\]

精确最优返回可取 $\delta_k=0$。§11证明任何可行返回都有一个粗的统一差距上界，也给出更有用的原始/对偶证书；不把数值求解器的“成功”标志等同于给定精度证书。

Route 0只使用H1的输入/参考界及H2–H4、可行执行，不使用目标差距。Route 1进一步使用(C1)–(C4)的完整规定和(H5)。

## 4. 结构恒等式、QP 良定性与域不变

### 引理1：缓存与冻结一致性

对完整映射及任意冻结映射，都有
\[
E_{\rm prev}F(q,u)=E_{\rm prev}F_{\bar q}^{\rm fr}(q,u)=u.
\tag{L1a}
\]
因此任意候选预测满足
\[
u_{i|k}-E_{\rm prev}p_{i|k}
=\begin{cases}u_{0|k}-u_{k-1},&i=0,\\u_{i|k}-u_{i-1|k},&1\le i<N.\end{cases}
\tag{L1b}
\]

此外，对任意首输入以及整条标称序列，分别有
\[
p_{1|k}=F(q_k^E,u_{0|k}),\qquad
p_{i|k}(\bar U_k)=\bar q_{i|k},\quad0\le i\le N.
\tag{L1c}
\]

**证明。** 两种递推的输入缓存都是 $S_uv+E_uu$，最后一格恰为 $u$，得到(L1a)，再从 $p_{0|k}=q_k^E$ 得(L1b)。第一对冻结系数在 $q_k^E$ 计算，因而首步与完整映射相同。对标称序列，$i=0$ 时两条轨迹一致；若第 $i$ 步相同，则该步的冻结系数也在同一状态生成，施加同一 $\bar u_{i|k}$ 得到相同下一状态。归纳证明(L1c)。证毕。

### 引理2：凝聚 QP、存在唯一性与统一强凸常数

对于已确定的冻结矩阵，堆叠 $P=\operatorname{col}(p_{0|k},\ldots,p_{N|k})=P_k^0+\mathcal T_kU$。令
\[
\begin{gathered}
\mathcal C=I_{N+1}\otimes C_m,\quad
Q_N=I_{N+1}\otimes Q,\quad S_N=I_N\otimes S,\\
\mathcal G_k=\mathcal C\mathcal T_k,\quad
a_k^{\rm out}=\mathcal C P_k^0-\operatorname{col}(x_k^r,\ldots,x_{k+N}^r),\\
b_k^\Delta=\operatorname{col}(u_{k-1},0,\ldots,0),\quad
\mathcal D_\Delta=D_N\otimes I_m,
\end{gathered} \tag{L2a}
\]
其中 $D_N$ 的主对角线为1、次对角线为$-1$，其他元素为0；$D_1=[1]$。于是
\[
J_k^{\rm fr}(U;\bar U_k)
=\|\mathcal G_kU+a_k^{\rm out}\|_{Q_N}^2+
\|\mathcal D_\Delta U-b_k^\Delta\|_{S_N}^2,
\tag{L2b}
\]
凝聚 Hessian 为
\[
\mathcal H_k=2\bigl(\mathcal G_k^\top Q_N\mathcal G_k+
\mathcal D_\Delta^\top S_N\mathcal D_\Delta\bigr)
\succeq\mu_N I,\qquad
\mu_N=\frac{4\lambda_{\min}(S)}{N(N+1)}>0.
\tag{L2c}
\]

**证明。** 仿射形式由固定线性递推逐步消元得到；(L1b)给出增量项，故(L2b)成立。设 $h=\operatorname{col}(h_0,\ldots,h_{N-1})$，$d=\mathcal D_\Delta h$，则 $h_i=\sum_{j=0}^id_j$。由Cauchy–Schwarz，
\[
\|h\|_2^2\le\sum_{i=0}^{N-1}(i+1)\sum_{j=0}^{i}\|d_j\|_2^2
\le\frac{N(N+1)}2\|d\|_2^2.
\tag{L2d}
\]
因此 $h^\top\mathcal H_kh\ge2\lambda_{\min}(S)\|d\|_2^2\ge\mu_N\|h\|_2^2$。该下界不依赖冻结系数或输出可控性。目标连续，$\mathcal U^N$ 非空紧，故最小值存在；可行集凸且目标严格凸，故最优解唯一。证毕。

唯一性不是下面定义最优值或使用可行返回序列比较的必要条件；它是当前权重选择额外给出的良定性结果。

### 定理1：域不变与递归可行性

在H1–H4及可行返回/准确执行条件下，(C2)–(C4)可对所有 $k\ge0$ 递归构造；每个 QP 有唯一最优解，所有实际编码状态、标称预测和所有可行候选的完整/冻结预测均在 $\mathcal Q$ 内。

**证明。** 对采样时刻归纳。初始时 $q_0^E\in\mathcal Q$、$\bar U_0\in\mathcal U^N$。假设第 $k$ 拍这两条成立。

1. 对任意 $q\in\mathcal Q,u\in\mathcal U$，因 $0\in\mathcal Q$，H2–H4给出 $\|F(q,u)\|_\Pi\le\lambda M+b_u\le M$。逐步归纳先保证整个标称 rollout 在域内，因此它生成的每一对冻结系数都属于H2覆盖的族；同理任何可行完整预测也在域内。
2. 对这些已合法生成的冻结系数，$\|F_{\bar q}^{\rm fr}(q,u)\|_\Pi\le\lambda_{\rm fr}M+b_u\le M$。从同一域内初值出发，所有可行候选的冻结状态都在域内。
3. 无状态/终端硬约束，任意 $U\in\mathcal U^N$ 配合其递推状态都可行。引理2给出存在唯一最优解。返回序列可行，故 $u_k\in\mathcal U$。
4. H3适用于当前域内状态，故 $\|q_{k+1}^E\|_\Pi\le\lambda M+b_u+\bar w\le M$。按(C4)移位并重复一个已可行输入，得到 $\bar U_{k+1}\in\mathcal U^N$。

这恢复了下一拍归纳前提，证明完成。没有在第1–2步预先假设未来实际状态已在域内。证毕。

这里递归可行性针对(C3)的输入约束；并未证明未设置的状态安全约束或某个具体数值求解器永不失败。

## 5. Route 0：基础输出误差有界性

令
\[
e_k^x=x_k-x_k^r,\qquad
c_m=\|C_m\Pi^{-1/2}\|_2,\qquad E=c_mM+\bar r.
\tag{B1}
\]

### 引理3：任意可行输入下的有界性

在定理1的域/残差条件下，对于任意可行输入序列，
\[
\|q_k^E\|_\Pi\le\lambda^k\|q_0^E\|_\Pi+
\frac{1-\lambda^k}{1-\lambda}(b_u+\bar w),
\tag{B2}
\]
并有
\[
\begin{aligned}
\|e_k^x\|_2&\le c_m\lambda^k\|q_0^E\|_\Pi+
c_m\frac{1-\lambda^k}{1-\lambda}(b_u+\bar w)+\bar r,\\
\|e_k^x\|_2&\le E,\\
\limsup_{k\to\infty}\|e_k^x\|_2&\le
r_0:=c_m\frac{b_u+\bar w}{1-\lambda}+\bar r\le E.
\end{aligned} \tag{B3}
\]

**证明。** H2–H3及域不变性给出
\[
\|q_{k+1}^E\|_\Pi
\le\|F(q_k^E,u_k)-F(0,u_k)\|_\Pi+\|F(0,u_k)\|_\Pi+\|w_k\|_\Pi
\le\lambda\|q_k^E\|_\Pi+b_u+\bar w.
\tag{B4}
\]
迭代并求几何和得(B2)。利用 $\|C_mq\|_2\le c_m\|q\|_\Pi$ 和参考界得(B3)的第一行；用域界得第二行；取上极限得第三行。H4蕴含 $(b_u+\bar w)/(1-\lambda)\le M$，证明 $r_0\le E$。证毕。

这说明误差不发散，不说明优化使误差趋零。衰减项乘的是初始编码状态范数，不是相对可实现参考平衡点的误差；不能仅凭它改称指数跟踪。

## 6. Route 1 的比较工具

### 引理4：统一代价连续性

置
\[
\begin{gathered}
\bar u=\max_{u\in\mathcal U}\|u\|_2,\quad
c_p=\|E_{\rm prev}\Pi^{-1/2}\|_2,\quad
E_Q=\|Q\|_2E^2,\\
L_f=2\|Q\|_2E c_m,\qquad
L_\ell=L_f+2\|S\|_2(\bar u+c_pM)c_p.
\end{gathered} \tag{K1}
\]
对任意相同绝对时刻 $t$、相同 $u\in\mathcal U$ 及 $p,p'\in\mathcal Q$，
\[
|V_f(t,p)-V_f(t,p')|\le L_f\|p-p'\|_\Pi,\qquad
|\ell_t(p,u)-\ell_t(p',u)|\le L_\ell\|p-p'\|_\Pi.
\tag{K2}
\]

**证明。** 令 $e=C_mp-x_t^r$、$e'=C_mp'-x_t^r$。两者范数至多为 $E$，且 $\|e-e'\|_2\le c_m\|p-p'\|_\Pi$。于是
\[
|e^\top Qe-e'^\top Qe'|
=|(e-e')^\top Q(e+e')|
\le2\|Q\|_2E c_m\|p-p'\|_\Pi.
\tag{K3}
\]
对 $h=u-E_{\rm prev}p$、$h'=u-E_{\rm prev}p'$，有 $\|h\|_2,\|h'\|_2\le\bar u+c_pM$，$\|h-h'\|_2\le c_p\|p-p'\|_\Pi$。应用同一二次型差分恒等式，得到增量项的连续性常数。两项相加即(K2)。证毕。

### 引理5：跨采样移位预测误差

固定采样时刻 $k$。以下 $p_i=p_{i|k}(\widehat U_k)$，$\widehat u_i=\widehat u_{i|k}$，$u_\ell=\widehat u_{N-1}$。将(C4)中的下一标称序列记为 $U^+$，其分量为
\[
u_j^+=\begin{cases}\widehat u_{j+1},&0\le j<N-1,\\u_\ell,&j=N-1.\end{cases}
\tag{S1}
\]
从下一真实初值沿它计算完整轨迹：
\[
\widetilde q_0=q_{k+1}^E,\qquad
\widetilde q_{j+1}=F(\widetilde q_j,u_j^+),\quad0\le j<N.
\tag{S2}
\]
定义
\[
d_j=\lambda^j\bar w+\bar\eta\sum_{s=0}^{j-1}\lambda^s,\quad0\le j<N,
\qquad d_0=\bar w.
\tag{S3}
\]
则
\[
\|\widetilde q_j-p_{j+1}\|_\Pi\le d_j\quad(0\le j<N),\qquad
\|\widetilde q_N-F(p_N,u_\ell)\|_\Pi\le\lambda d_{N-1}.
\tag{S4}
\]

**证明。** 引理1的首步一致性和(H3)给出 $q_{k+1}^E=p_1+w_k$，故起点距离至多为 $\bar w$。对 $0\le j<N-1$，
\[
\begin{aligned}
\|\widetilde q_{j+1}-p_{j+2}\|_\Pi
&=\|F(\widetilde q_j,\widehat u_{j+1})-
F_{\bar q_{j+1|k}}^{\rm fr}(p_{j+1},\widehat u_{j+1})\|_\Pi\\
&\le\|F(\widetilde q_j,\widehat u_{j+1})-F(p_{j+1},\widehat u_{j+1})\|_\Pi\\
&\quad+\|F(p_{j+1},\widehat u_{j+1})-
F_{\bar q_{j+1|k}}^{\rm fr}(p_{j+1},\widehat u_{j+1})\|_\Pi\\
&\le\lambda\|\widetilde q_j-p_{j+1}\|_\Pi+\bar\eta.
\end{aligned} \tag{S5}
\]
所有状态和冻结点的域成员资格已由定理1保证。递推 $d_{j+1}=\lambda d_j+\bar\eta$ 得(S3)及(S4)第一部分。最后一步两边都施加同一 $u_\ell$ 并使用完整映射，故仅有 $\lambda d_{N-1}$，不再多加一次冻结误差。证毕。

### 引理6：下一冻结候选与代价预算

下一 QP 的标称序列恰为 $U^+$，由引理1，其在候选 $U^+$ 上的冻结状态就是 $\widetilde q_j$。令
\[
\varepsilon_{\rm sh}=L_\ell\sum_{j=0}^{N-1}d_j+L_f\lambda d_{N-1}.
\tag{S6}
\]
则
\[
\begin{aligned}
J_{k+1}^{\rm fr}(U^+;U^+)
&\le\sum_{i=1}^{N-1}\ell_{k+i}(p_i,\widehat u_i)
+\ell_{k+N}(p_N,u_\ell)\\
&\quad+V_f(k+N+1,F(p_N,u_\ell))+\varepsilon_{\rm sh}.
\end{aligned} \tag{S7}
\]

**证明。** 下一 QP 的第 $j$ 个阶段使用绝对时刻 $k+1+j$、状态 $\widetilde q_j$ 和输入 $u_j^+$。与旧轨迹状态 $p_{j+1}$ 在**同一绝对时刻和同一输入**处比较，分别应用(K2)和(S4)，阶段预算合计为 $L_\ell\sum_{j=0}^{N-1}d_j$。新终端时刻为 $k+N+1$，参照状态取 $F(p_N,u_\ell)$，终端预算为 $L_f\lambda d_{N-1}$。重排阶段索引得到(S7)。证毕。

**当前精确缓存结构下的缩紧。** 实际上，对 $0\le j<N$，
\[
E_{\rm prev}\widetilde q_j=E_{\rm prev}p_{j+1}=\widehat u_j.
\tag{S8}
\]
当 $j=0$ 时，两者都缓存刚施加的 $\widehat u_0$；当 $j\ge1$ 时，两者缓存同一前序输入 $\widehat u_j$。因此每个匹配阶段的增量惩罚**完全相等**，不是仅仅相差一个 Lipschitz 上界。故(S7)还可使用更小预算
\[
\varepsilon_{\rm sh}^{\rm cache}
=L_f\left(\sum_{j=0}^{N-1}d_j+\lambda d_{N-1}\right)
\le\varepsilon_{\rm sh}.
\tag{S9}
\]
主结果先沿用原路线的(S6)；其每一处 $\varepsilon_{\rm sh}$ 都可一致替换为(S9)。这只利用现有记账结构，不修改控制器。不能因此删掉目标中的增量项。

## 7. Route 1 主定理：值比较与平均性能

### 引理7：尾部恒等式

定义
\[
\tau_k=V_f(k+N+1,F(p_N,u_\ell))
=\|C_mF(p_N,u_\ell)-x_{k+N+1}^r\|_Q^2.
\tag{T1}
\]
则
\[
\ell_{k+N}(p_N,u_\ell)=V_f(k+N,p_N),\qquad
0\le\tau_k\le\bar\tau:=E_Q,
\tag{T2}
\]
并且
\[
\ell_{k+N}(p_N,u_\ell)+V_f(k+N+1,F(p_N,u_\ell))-V_f(k+N,p_N)=\tau_k.
\tag{T3}
\]

**证明。** $E_{\rm prev}p_N=u_\ell$，所以该尾部阶段的增量为零；它的输出项恰为同一时刻、同一权重的旧终端项，得到第一式。(T3)随后直接相消。由定理1和完整模型的一步不变性，$F(p_N,u_\ell)\in\mathcal Q$，故输出误差范数至多为 $E$，二次型至多为 $E_Q$。证毕。

注意旧终端参考是 $x_{k+N}^r$，推进后是 $x_{k+N+1}^r$。$\tau_k$ 用于分析，不是当前QP必需输入或新增在线步骤。恒等式没有声称两个参考相等，也没有声称 $\tau_k$ 很小。

### 定理2：单次冻结 MPC 的值比较与累计性能

在H1–H5下执行(C1)–(C4)，则对每个 $k\ge0$，
\[
\boxed{W_{k+1}\le W_k-\ell_k(q_k^E,u_k)+\tau_k+\varepsilon_{\rm sh}+\delta_k.}
\tag{T4}
\]
对每个整数 $T\ge1$，
\[
\begin{aligned}
\sum_{k=0}^{T-1}\bigl(\|e_k^x\|_Q^2+\|u_k-u_{k-1}\|_S^2\bigr)
&\le W_0-W_T+\sum_{k=0}^{T-1}(\tau_k+\varepsilon_{\rm sh}+\delta_k)\\
&\le W_0+\sum_{k=0}^{T-1}(\tau_k+\varepsilon_{\rm sh}+\delta_k).
\end{aligned} \tag{T5}
\]

**证明。** $U^+\in\mathcal U^N$ 是下一 QP 的可行候选，故
\[
\begin{aligned}
W_{k+1}&\le J_{k+1}^{\rm fr}(U^+;U^+)\\
&\le\sum_{i=1}^{N-1}\ell_{k+i}(p_i,\widehat u_i)+\ell_{k+N}(p_N,u_\ell)
+V_f(k+N+1,F(p_N,u_\ell))+\varepsilon_{\rm sh}\\
&=J_k^{\rm fr}(\widehat U_k;\bar U_k)-\ell_k(p_0,\widehat u_0)+\tau_k+\varepsilon_{\rm sh}\\
&\le W_k-\ell_k(q_k^E,u_k)+\tau_k+\varepsilon_{\rm sh}+\delta_k.
\end{aligned} \tag{T6}
\]
第二行使用(S7)，第三行使用(T3)，最后一行使用(H5)和实际执行关系。下个时刻比较的是真实最优值 $W_{k+1}$，所以不出现 $\delta_{k+1}$。将(T4)移项后从0加到$T-1$，值函数项望远镜相消。由 $C_mq_k^E=x_k$、$E_{\rm prev}q_k^E=u_{k-1}$ 识别实际阶段代价，得到(T5)第一行；目标非负给出 $W_T\ge0$，得到第二行。证毕。

### 推论1：平均误差与输入变化能量

对所有 $T\ge1$，
\[
\frac1T\sum_{k=0}^{T-1}\|e_k^x\|_2^2
\le\frac{W_0}{T\lambda_{\min}(Q)}+
\frac{\sum_{k=0}^{T-1}(\tau_k+\varepsilon_{\rm sh}+\delta_k)}{T\lambda_{\min}(Q)}.
\tag{T7}
\]
保留尾部和求解差距的实际时间平均可得
\[
\limsup_{T\to\infty}\frac1T\sum_{k=0}^{T-1}\|e_k^x\|_2^2
\le\frac{\varepsilon_{\rm sh}+
\limsup_{T\to\infty}T^{-1}\sum_{k=0}^{T-1}(\tau_k+\delta_k)}{\lambda_{\min}(Q)}.
\tag{T8}
\]
进一步使用统一上界，则
\[
\boxed{\limsup_{T\to\infty}\frac1T\sum_{k=0}^{T-1}\|e_k^x\|_2^2
\le\frac{\bar\tau+\varepsilon_{\rm sh}+\bar\delta}{\lambda_{\min}(Q)},}
\tag{T9}
\]
\[
\limsup_{T\to\infty}\frac1T\sum_{k=0}^{T-1}\|u_k-u_{k-1}\|_S^2
\le\bar\tau+\varepsilon_{\rm sh}+\bar\delta.
\tag{T10}
\]

**证明。** (T5)左侧输出项至少为 $\lambda_{\min}(Q)\sum\|e_k^x\|_2^2$，舍去非负增量项并除以 $T\lambda_{\min}(Q)$ 得(T7)。$W_0$ 有限，故 $W_0/T\to0$；取上极限得(T8)，再用 $\tau_k\le\bar\tau$、$\delta_k\le\bar\delta$ 得(T9)。相反舍去(T5)的输出项，除以 $T$ 后同理得到(T10)。证毕。

(T4)不是无误差Lyapunov下降式；尾部项可使值函数上升。平均结论也不等于每个时刻均有小误差。

## 8. 逐时刻界及输入增量推论

### 引理8：常值输入候选的值比较

令 $U_k^c=\operatorname{col}(u_{k-1},\ldots,u_{k-1})$，并记它在**当前同一冻结 QP**中的预测为 $p_{i|k}^c$。设
\[
B_k=\sum_{i=1}^{N-1}\|C_mp_{i|k}^c-x_{k+i}^r\|_Q^2+
\|C_mp_{N|k}^c-x_{k+N}^r\|_Q^2,
\qquad\bar B=NE_Q.
\tag{V1}
\]
则
\[
\|e_k^x\|_Q^2\le W_k\le\|e_k^x\|_Q^2+B_k,\qquad0\le B_k\le\bar B.
\tag{V2}
\]

**证明。** $u_{k-1}\in\mathcal U$，故该候选可行。初始上一输入也是 $u_{k-1}$；由缓存递推，候选每个增量均为零。因此候选代价恰为初始输出项加 $B_k$，给出上界。其余所有可行候选也共有同一初始输出项，其他项非负，给出下界。域不变和参考有界使每个后续输出二次项不超过 $E_Q$；后续阶段有 $N-1$ 项，终端有一项，一共 $N$ 项，得到 $B_k\le NE_Q$。证毕。

这个候选只用于证明，不额外运行第二次优化，也不替换下一次实际标称序列。

### 推论2：逐时刻最终界

对每个 $k\ge0$，
\[
\lambda_{\min}(Q)\|e_{k+1}^x\|_2^2\le W_{k+1}
\le B_k+\tau_k+\varepsilon_{\rm sh}+\delta_k.
\tag{V3}
\]
因而对所有 $k\ge1$，
\[
\|e_k^x\|_2\le r_1:=
\sqrt{\frac{\bar B+\bar\tau+\varepsilon_{\rm sh}+\bar\delta}{\lambda_{\min}(Q)}},
\qquad
\limsup_{k\to\infty}\|e_k^x\|_2\le\min\{r_0,r_1\}.
\tag{V4}
\]

**证明。** 实际阶段代价满足 $\ell_k(q_k^E,u_k)\ge\|e_k^x\|_Q^2\ge W_k-B_k$。代入(T4)得(V3)的上界；下界由下一拍的(V2)和正定权重给出。使用统一上界、除以 $\lambda_{\min}(Q)$ 并开方得到(V4)第一式；与(B3)结合得第二式。证毕。

### 推论3：逐时刻输入增量界

\[
\|u_k-u_{k-1}\|_S^2\le B_k+\delta_k\le\bar B+\bar\delta,
\qquad
\|u_k-u_{k-1}\|_2^2\le\frac{\bar B+\bar\delta}{\lambda_{\min}(S)}.
\tag{V5}
\]

**证明。** 返回代价包含初始输出项和首步增量项，其他项非负。因此
$\|u_k-u_{k-1}\|_S^2\le J_k^{\rm fr}(\widehat U_k;\bar U_k)-\|e_k^x\|_Q^2\le W_k+\delta_k-\|e_k^x\|_Q^2\le B_k+\delta_k$。除以最小特征值得欧氏界。证毕。

输入幅值本身始终满足 $u_k\in\mathcal U$，无需参考输入来定义此结论。

## 9. 误差预算的含义与粗界的信息量

三类量必须区分：

| 量 | 来源 | 模型/求解精确时是否自动为零 |
|---|---|---|
| $\bar w,\bar\eta$ 及其产生的 $\varepsilon_{\rm sh}$ | 真实重编码、完整/冻结多步差异 | 两个误差预算均为零时，是 |
| $\delta_k$ | 当前 QP 的返回目标与真实最优值差距 | 精确求解时，是 |
| $\tau_k$ | 重复末端输入后的下一步输出跟踪代价 | 否 |

**重要的定量核查。** 对本文明确给出的全域粗常数 $\bar\tau=E_Q=\|Q\|_2E^2$、$\bar B=NE_Q$，不是仅仅“可能不够紧”，而是必有
\[
\frac{\bar\tau+\varepsilon_{\rm sh}+\bar\delta}{\lambda_{\min}(Q)}\ge E^2,
\qquad
r_1^2\ge(N+1)E^2\ge E^2\ge r_0^2.
\tag{I1}
\]

**证明。** $\|Q\|_2/\lambda_{\min}(Q)\ge1$，误差预算非负，且(B3)已证明 $r_0\le E$。直接代入即可。证毕。

所以：

- (T9)使用这些全域粗常数时，不优于已知全时刻域界所蕴含的平均界 $E^2$；(V4)中的粗 $r_1$ 也不提供更小的最终半径。
- Route 1真正新增的结构性结果是(T4)–(T8)：它把实际累计输出/增量成本与尾部代价、冻结/重编码预算及求解误差联系起来。若有更紧的尾部或候选轨迹界，可代入这些公式；本材料不假装已经获得这样的实例证据。
- 对现有粗常数，最终输出半径应使用 $r_0$，而不能把 $r_1$ 宣传为更强的精度保证。缓存缩紧(S9)不会改变(I1)的这一基本比较。

这一发现不破坏证明，也不需要修改控制器；它限制的是理论结论的性能解释。

## 10. 公共模型条件的结构性充分条件

本节回答H2/H4可如何由已采用的模型结构得到，而不是把它们归因于“神经网络已经训练好”。对模型部分，主定理使用H2–H4；本节给出这些条件的一组结构性充分条件，不将其视为必要条件。H1及H5仍按主定理要求保留。

### 10.1 Schur 骨架与公共度量

设 $A_0$ 为 Schur 矩阵，$B_0$ 固定，定义
\[
M_0=\begin{bmatrix}A_0&0&0\\E_xC_x&S_x&0\\0&0&S_u\end{bmatrix}.
\tag{A1}
\]
其特征值为 $A_0$ 的特征值及缓存移位的零特征值，故 $M_0$ Schur。存在 $C<\infty,0<\alpha<1$ 使 $\|M_0^j\|_2\le C\alpha^j$，从而级数
\[
\Pi=\sum_{j=0}^{\infty}(M_0^\top)^jM_0^j
\tag{A2}
\]
收敛，且 $\Pi\succeq I$。逐项移位得到 $M_0^\top\Pi M_0-\Pi=-I$。若有另一解，差矩阵 $X$ 满足 $X=(M_0^\top)^jXM_0^j$ 对所有$j$成立，令$j\to\infty$得$X=0$，故解唯一。

因此
\[
\lambda_0^2:=\|M_0\|_\Pi^2
=\lambda_{\max}(I-\Pi^{-1})
=1-\frac1{\lambda_{\max}(\Pi)}<1.
\tag{A3}
\]
这里只对固定骨架构造度量，未把逐步谱半径条件误当作时变乘积收缩条件。

### 10.2 低秩调度的幅值与 Lipschitz 常数

取 $g_\chi\ge0$、整数秩上界 $r_\chi\ge1$，沿用模型参数化
\[
\begin{aligned}
A(c)&=A_0+\sum_{j=1}^{r_A}\gamma_{A,j}(c)\xi_{A,j}\upsilon_{A,j}^\top,\\
B(x)&=B_0+\sum_{j=1}^{r_B}\gamma_{B,j}(x)\xi_{B,j}\upsilon_{B,j}^\top,\\
\gamma_{\chi,j}(y)&=g_\chi\pi_{\chi,j}(y)\tanh([W_\chi y+b_\chi]_j),\\
\pi_\chi(y)&=\operatorname{softmax}(W_\chi^\pi y+b_\chi^\pi),\qquad\chi\in\{A,B\}.
\end{aligned} \tag{A4}
\]
因子列向量的欧氏范数至多为1；$A$侧因子属于$\mathbb R^d$，$B$侧左右因子分别属于$\mathbb R^d,\mathbb R^m$。

因为 $\pi_j\ge0$、$\sum_j\pi_j=1$ 和 $|\tanh|\le1$，
\[
\|A(c)-A_0\|_2\le g_A,\qquad\|B(x)-B_0\|_2\le g_B.
\tag{A5}
\]

再令
\[
\kappa_\chi=\|W_\chi\|_2+\tfrac12\sqrt{r_\chi}\|W_\chi^\pi\|_2,
\qquad L_A=g_A\kappa_A,\quad L_B=g_B\kappa_B.
\tag{A6}
\]
则 $\|A(c)-A(c')\|_2\le L_A\|c-c'\|_2$，$B$也满足对应界。

**证明。** softmax Jacobian 为 $J=\operatorname{diag}(\pi)-\pi\pi^\top$，它对称半正定。第$i$行对角元与非对角绝对值之和为 $2\pi_i(1-\pi_i)\le1/2$，故谱范数至多为 $1/2$。将每个 $\pi_j(y)\tanh([W_\chi y+b_\chi]_j)$ 的差分拆成“固定概率的激活差”与“固定激活的概率差”。第一部分的绝对值之和不超过 $\|W_\chi\|_2\|y-y'\|_2$：用tanh的1-Lipschitz性，再用概率加权Cauchy–Schwarz。第二部分不超过 $\|\pi(y)-\pi(y')\|_1\le\sqrt{r_\chi}\|W_\chi^\pi\|_2\|y-y'\|_2/2$。各秩一因子范数至多为1，求和后得到(A6)。证毕。

### 10.3 完整/冻结映射的统一界

假设 $c:\mathcal Q\to\mathbb R^{d_c}$ 满足 $\|c(q)-c(q')\|_2\le L_c\|q-q'\|_2$。该常数指从**增广状态**到context的完整映射，已经包含窗口提取与输入缓存拼接，不漏掉前置映射。定义
\[
\begin{gathered}
a_z=\|\Pi^{1/2}E_z\|_2,\quad b_z=\|E_z^\top\Pi^{-1/2}\|_2,
\quad b_q=\|\Pi^{-1/2}\|_2,\quad M_z=b_zM,\\
\nu_F=a_z(g_A b_z+L_A L_cM_zb_q+L_B\bar u c_m),
\qquad\nu_{\rm fr}=a_zg_A b_z,\\
b_0^{\rm drv}=\max_{u\in\mathcal U}\|\operatorname{col}(B_0u,0,E_uu)\|_\Pi.
\end{gathered} \tag{A7}
\]
可取
\[
\begin{aligned}
\lambda&=\lambda_0+\nu_F,&
\lambda_{\rm fr}&=\lambda_0+\nu_{\rm fr},\\
b_u&=b_0^{\rm drv}+a_zg_B\bar u,&
\bar\eta&=2a_z(g_AM_z+g_B\bar u).
\end{aligned} \tag{A8}
\]
只要这些上界满足 $\lambda,\lambda_{\rm fr}<1$ 及H4，即得到H2/H4。

**证明。** 写 $\Delta A(q)=A(c(q))-A_0$。同一输入下，$F(q,u)-F(q',u)-M_0(q-q')$ 仅在提升块非零，其提升块为
\[
\Delta A(q)(z-z')+[A(c(q))-A(c(q'))]z'
+[B(C_mq)-B(C_mq')]u.
\tag{A9}
\]
利用 $\|z'\|_2\le M_z$、$\|z-z'\|_2\le b_z\|q-q'\|_\Pi$、$\|q-q'\|_2\le b_q\|q-q'\|_\Pi$ 以及(A5)–(A6)，乘提升块注入范数$a_z$，得到 $\nu_F\|q-q'\|_\Pi$。加上骨架收缩率得完整界。对固定冻结点，系数变化项消失，只剩 $\Delta A(\bar q)(z-z')$，得到 $\nu_{\rm fr}$。

在被传播状态$q=0$处，完整/冻结映射都只有 $\operatorname{col}(B(\cdot)u,0,E_uu)$，其相对名义输入驱动的差不超过$a_zg_B\bar u$，给出$b_u$。最后在相同$q,u$处比较完整与冻结模型：提升块差为 $[A(c(q))-A(c(\bar q))]z+[B(C_mq)-B(C_m\bar q)]u$。用幅值三角不等式分别界为$2g_AM_z$和$2g_B\bar u$，得到$\bar\eta$。证毕。

这一证明仅用 Lipschitz 差分，不要求在线求导。若以导数估计$L_c$，该界必须覆盖凸球$\mathcal Q$及其线段；有限点的Jacobian采样不是统一上界证明。

### 命题1：保留非零调度的充分增益选择

固定骨架、$B_0$、输入集、试探球及覆盖该球实际转移的残差包络。设
\[
\Delta_0=(1-\lambda_0)M-b_0^{\rm drv}-\bar w>0.
\tag{A10}
\]
固定允许模型族的统一界 $\kappa_\chi\le\bar\kappa_\chi$、$L_c\le\bar L_c$，以及正数$\widehat g_A,\widehat g_B$。令$g_A=\zeta\widehat g_A$、$g_B=\zeta\widehat g_B$，并定义
\[
\begin{aligned}
K_F&=a_z(\widehat g_A b_z+\widehat g_A\bar\kappa_A\bar L_cM_zb_q
+\widehat g_B\bar\kappa_B\bar u c_m),\\
K_{\rm fr}&=a_z\widehat g_A b_z,\qquad
K_b=a_z\widehat g_B\bar u,\qquad K_* =\max\{K_F,K_{\rm fr}\}.
\end{aligned} \tag{A11}
\]
任何
\[
0<\zeta<\min\left\{1,\frac{1-\lambda_0}{2K_*},
\frac{\Delta_0}{2(K_*M+K_b)}\right\}
\tag{A12}
\]
均给出严格收缩率和严格半径余量，零分母对应的限制项省略。

**证明。** (A7)–(A8)给出 $\lambda\le\lambda_0+\zeta K_F$、$\lambda_{\rm fr}\le\lambda_0+\zeta K_{\rm fr}$，两者均小于 $\lambda_0+(1-\lambda_0)/2<1$。且
\[
\lambda M+b_u+\bar w
\le\lambda_0M+b_0^{\rm drv}+\bar w+\zeta(K_FM+K_b)
<M-\Delta_0/2<M.
\tag{A13}
\]
同理 $\lambda_{\rm fr}M+b_u<M-\Delta_0/2-\bar w\le M$。两个调度增益均可为正。证毕。

**残差量词不能遗漏。** 若将命题用于“选择增益前证明整个模型族可用”，$\bar w$ 必须对该候选族统一有效，因为改变调度也改变预测残差。若只掌握最终部署模型的残差界，则(A8)/(H4)是对该模型的条件检查，不能反向宣称任意小增益一定使真实系统满足条件。试探球覆盖初值及残差有效域也是命题前提，不由增益选择自动获得。

### 10.4 一个非零历史调度、精确重编码的数学实例

为证明这些条件不强迫所有调度为零，取$n=m=1$、$P_h=2$，$z=(x,\alpha_{\rm d}a)$，其中$a=x_{k-1}$、$\alpha_{\rm d}\ne0$，并定义
\[
c=a+v,\qquad
A(c)=\begin{bmatrix}a_0+g_A\tanh c&0\\\alpha_{\rm d}&0\end{bmatrix},\qquad
B(x)=\begin{bmatrix}b_0+g_B\tanh x\\0\end{bmatrix},
\quad |a_0|<1,\ b_0\ne0.
\tag{A14}
\]
这属于秩一调度形式，两个头的softmax均为1；$c$确实依赖过去测量和输入。取测量系统
$x_{k+1}=(a_0+g_A\tanh(x_{k-1}+u_{k-1}))x_k+(b_0+g_B\tanh x_k)u_k$，以及$G_\theta(x_{k-1},x_k)=(x_k,\alpha_{\rm d}x_{k-1})$。

预测的第二提升分量为$\alpha_{\rm d}x_k$，下一测量缓存为$x_k$，故下一真实编码与预测完全一致，$w_k=0$。骨架Schur，紧输入集给出有限名义驱动；可先选足够大的$M$使(A10)成立并覆盖所选初值，再按(A12)选择两个正增益。context是线性的，调度头界全局有效，故本例满足全部模型条件且保留真正的历史调度。

此处是解析构造，用于证明模型类非空；不是对现有Transformer权重、机械臂或实验系统的认证。

### 10.5 实际重编码残差的分解

在实际编码初值上预测下一提升状态$\widehat z$，令$\widehat x=C_x\widehat z$，$\widetilde{\mathcal X}=\operatorname{shift}(\mathcal X,\widehat x)$，$E_X$向窗口末尾注入一个测量块，$C_\psi$提取特征块。定义
\[
\nu=x^+-\widehat x,\qquad
\kappa=\psi_\theta(\widetilde{\mathcal X})-C_\psi\widehat z.
\tag{A15}
\]
真实下一窗口为$\widetilde{\mathcal X}+E_X\nu$，因此精确恒等式为
\[
r=\operatorname{col}\bigl(\nu,
\kappa+\psi_\theta(\widetilde{\mathcal X}+E_X\nu)-\psi_\theta(\widetilde{\mathcal X})\bigr),
\qquad w=E_zr.
\tag{A16}
\]
若在从当前域产生的全部所需真实/预测窗口上，有$\|\nu\|_2\le\bar\nu$、$\|\kappa\|_2\le\bar\kappa$，且特征映射Lipschitz常数为$L_\psi$，则由于$\|E_X\|_2=1$，
\[
\|w\|_\Pi\le a_z\sqrt{\bar\nu^2+(\bar\kappa+L_\psi\bar\nu)^2}.
\tag{A17}
\]
这给出H3的一个充分残差预算，证明只需(A16)和三角不等式。所需窗口覆盖由**当前域内状态及实际测量转移**定义，不能以尚未证明的下一状态域成员资格为前提。$\bar\nu$衡量测量预测误差，$\bar\kappa$衡量编码图缺陷；公共收缩构造不自动给出它们的数值。

## 11. 求解器目标差距的完整接口

### 11.1 任意可行返回的粗统一差距

令
\[
D_{\mathcal U,S}=\max_{u,v\in\mathcal U}\|u-v\|_S<\infty.
\tag{G1}
\]
任意可行返回的$N$个增量项均不超过$D_{\mathcal U,S}^2$，初始输出以外的$N$个输出项均不超过$E_Q$。又$W_k\ge\|e_k^x\|_Q^2$，故
\[
0\le J_k^{\rm fr}(\widehat U_k;\bar U_k)-W_k
\le N(E_Q+D_{\mathcal U,S}^2).
\tag{G2}
\]
因此在既有紧域条件下，有限统一差距的**存在性**不需要额外认证算法；但用(G2)作为$\bar\delta$通常很粗。若要声称某个小的$\delta_k$，则需要实际有效证书，而不能任意指定。

### 命题2：原始/对偶残差证书

将当前QP写成$J(U)=\tfrac12U^\top\mathcal HU+g^\top U+c_0$、$GU\le h$，其中$G=I_N\otimes H_u$、$h=\mathbf1_N\otimes h_u$。取任意原始可行$\widehat U$、任意$y\ge0$，以及可靠的强凸下界$\mathcal H\succeq\mu I\succ0$，例如(L2c)的$\mu_N$。令
\[
r_{\rm stat}=\mathcal H\widehat U+g+G^\top y.
\tag{G3}
\]
则
\[
0\le J(\widehat U)-W\le
\frac{\|r_{\rm stat}\|_2^2}{2\mu}+y^\top(h-G\widehat U).
\tag{G4}
\]

**证明。** 拉格朗日函数为$\mathcal L(U,y)=J(U)+y^\top(GU-h)$，Hessian仍为$\mathcal H$。强凸性给出对任意$V$：
\[
\mathcal L(V,y)\ge\mathcal L(\widehat U,y)
+r_{\rm stat}^\top(V-\widehat U)+\frac\mu2\|V-\widehat U\|_2^2.
\tag{G5}
\]
将右侧对自由$V$最小化，得到
$\inf_V\mathcal L(V,y)\ge\mathcal L(\widehat U,y)-\|r_{\rm stat}\|_2^2/(2\mu)$。
对每个原始可行$V$，$\mathcal L(V,y)\le J(V)$，所以弱对偶给出$\inf_V\mathcal L(V,y)\le W$。结合两式并从$J(\widehat U)$中减去下界，得到(G4)。证毕。

本证书不要求Slater条件或可行集有内点，也不需要第二个QP。实际数值使用时，原始/对偶可行性、强凸下界和残差计算均须在采用的浮点/误差模型下有效。未分析的不可行回退、输入截断或超时返回，不自动包含在定理范围内。

## 12. 边界、反例与闭合性核对

### 12.1 $N=1$ 与零系数边界

$N=1$时，$U^+=(\widehat u_0)$，旧末端$p_1$缓存$\widehat u_0$，所有中间移位和为空。具体地，
\[
d_0=\bar w,\quad
\varepsilon_{\rm sh}=(L_\ell+\lambda L_f)\bar w,\quad
\varepsilon_{\rm sh}^{\rm cache}=(1+\lambda)L_f\bar w,\quad
\bar B=E_Q,\quad\mu_1=2\lambda_{\min}(S).
\tag{E1}
\]
尾部缺陷使用$x_{k+2}^r$；当前QP仍只使用$x_k^r,x_{k+1}^r$。公式没有丢失或重复计算终端项。

空和定义为0，$\lambda^0=1$。若代数边界取$\lambda=0$，(S3)仍无歧义：$d_0=\bar w$，$d_j=\bar\eta$对$j\ge1$，终端比较项$\lambda d_{N-1}=0$；不通过可能出现$0/0$的替代表达求值。本检查不声称当前非零缓存映射能实现零诱导收缩率。

### 12.2 解析反例：零模型与求解误差不保证跟踪到零

取$n=m=d=1$、$P_h=2$、$G_\theta(x_{k-1},x_k)=x_k$，$q=(x,a,v)$，以及
\[
F(q,u)=(0,x,u),\qquad x_{k+1}=0,\qquad
\mathcal U=[-1,1],\quad Q=S=1,\quad x_k^r=1.
\tag{E2}
\]
初始历史和$\bar U_0$全零。模型不随调度变化，完整/冻结完全相同；实际重编码精确，故$\bar w=\bar\eta=0$。取
\[
M_0=\begin{bmatrix}0&0&0\\1&0&0\\0&0&0\end{bmatrix},\qquad
\Pi=\operatorname{diag}(2,1,1),\quad
\lambda=\lambda_{\rm fr}=1/\sqrt2,\quad b_u=1,\quad M=4.
\tag{E3}
\]
直接计算$M_0^\top\Pi M_0-\Pi=-I$，且$\lambda M+b_u=2\sqrt2+1<4$，H2–H4成立。对任意$N\ge1$，预测输出始终为0，目标为
\[
J_k(U)=(N+1)+u_0^2+\sum_{i=1}^{N-1}(u_i-u_{i-1})^2.
\tag{E4}
\]
唯一最优返回为全零，故实际闭环保持全零并有
\[
W_k=N+1,\qquad\delta_k=0,\qquad
e_k^x=-1,\qquad\ell_k=1,\qquad\tau_k=1.
\tag{E5}
\]
(T4)以等号成立：$N+1=(N+1)-1+1$，但跟踪误差永不趋零。这不是算法失败的仿真实验，而是满足所列条件的精确数学反例。原因是当前理论不要求参考可实现，也没有假设输入具有输出调节能力。

因此不能删去$\tau_k$，也不能从$\bar w=\bar\eta=\bar\delta=0$推出精确跟踪。即使另有可实现性，也仍需独立论证才能给出更强结论，本文不额外加入该路线。

### 12.3 依赖与结论边界表

| 结论 | 必要输入/依赖 | 没有暗含的结论 |
|---|---|---|
| 缓存恒等式/首步一致/标称复现 | 精确缓存，沿当前标称点冻结 | 任意候选完整多步与冻结多步相同 |
| QP存在唯一 | 固定系数，非空紧凸输入集，$S\succ0$ | 数值求解器必在截止时间返回 |
| 域不变 | 先域内模型界，再半径条件，再真实残差 | 仅靠输入饱和就能稳定任意plant |
| Route 0最终有界 | 同输入收缩、驱动/残差/参考有界 | MPC优化贡献或误差到零 |
| 移位比较 | 原始可行返回、规定移位、下一冻结的标称复现 | 任意warm start都可复用该预算 |
| 尾部恒等式 | 缓存末格、重复末输入、同权阶段/终端输出代价 | 尾部下降或$\tau_k=0$ |
| Route 1累计/平均关系 | 上述工具及有效目标差距上界 | 逐时刻小误差、ISS或指数到零 |
| 最终半径/增量界 | 常值可行比较序列及同一QP值比较 | 更紧的实际性能或参考输入跟踪 |
| 非零调度构造 | Schur骨架、统一调度/context界、有效残差包络与半径余量 | 任意训练实例都满足上述条件 |

另外，所有跟踪结论针对测量$x_k$，并不凭空控制未观测物理状态$s_k$。滚动修改重叠参考、在线改变部署模型、额外输入后处理、增加硬约束，都会改变某条比较前提，需要重新分析。

## 13. 交付给后续写作者的准确结论

可以围绕下列已证明结果组织论文，但本材料不替代用户对改稿的授权：

1. **控制器良定性与可行性：**引理1–2及定理1。
2. **基础有界性引理：**(B2)–(B3)，不将它单独包装成MPC的性能贡献。
3. **MPC主性能关系：**(T4)–(T8)，明确尾部项；全域版本(T9)作为保守推论，不能声称改善已有域界。
4. **辅助结果：**(V3)–(V5)、精确缓存预算(S9)、实例可用的求解差距证书(G4)。
5. **条件来源：**§10提供结构性充分条件与残差接口；目标实例是否满足条件仍须后续认证，不写成已完成实验。

不迁回旧的参考输入终端下降、见证对、单时刻提升可观测性或零误差指数跟踪结论。也不添加关于删去某代价项的辩护段。

## 14. 验证与材料基线

本材料已完成逐式检查和确定性代数一致性检查。自动检查使用Python标准库整数/有理数及符号系数，不运行控制仿真；它们辅助发现符号、索引和消去错误，不等同于形式化证明助手认证或实机验证。一般性结论由正文证明给出，不由有限测试用例替代。

| 检查 | 状态 |
|---|---|
| 假设量词、域归纳顺序、QP强凸与可行性 | 已逐式核查；特别区分部署模型残差条件与模型族统一残差包络 |
| 相邻时刻索引、尾部消去、预算与望远镜求和 | 已逐式核查；$N=1,\ldots,16$的符号消去、时间匹配、缓存匹配及求和检查通过 |
| 差分算子与强凸下界 | $N=1,\ldots,16$的精确逆矩阵、Frobenius范数和有理数LDL检查通过；全$N$证明为(L2d) |
| 移位误差递推 | $N=1,\ldots,16$、$\lambda\in\{0,1/3,9/10\}$的有理数递推与显式式一致 |
| 代价连续性、粗界比较及反例 | 对称二次型差分的符号系数检查通过；粗界差的非负系数、反例Lyapunov恒等式/收缩率平方/值恒等式精确检查通过 |
| 数学结构及论文不变性 | 78个显示公式的编号唯一、引用可解析、环境/括号配对通过；Main.tex/PDF哈希与下列基线一致，内层已跟踪文件无差异 |

依据与源文件：

- 已定控制器规格：`.vibe/docs/specs/20261110-output-tracking-controller-proof-record.md`。本材料已独立定义所有所用控制器对象与证明条件，不要求读者另取该文件。
- 原稿：`Transformer-Koopman/论文/新版本/Main.tex` 的第三章、IV-A/IV-B、附录A–C；其第四章仍为旧参考对控制器，本轮未编辑。
- 外部报告：`第四章输出跟踪MPC_稳定性证明链路分析与修改建议.md`，2026-11-10，Route 0/1。本文补齐证明细节，并新增缓存预算缩紧、强凸下界、粗界支配关系及解析边界反例的核查。
- 内层仓库基线：分支`paper`，提交`003b679`。
- `Main.tex` SHA256：`B5FA8EF6D21F84BDBA8FE83FEA27FC7DE7D0F502963AD929A85D6AF276A8CFC1`。
- `Main.pdf` SHA256：`F38CAA223713D8A2EEE3B375ACB6F07B79830CDE980C85B316825DE5880C1966`。

未运行训练、控制仿真、checkpoint认证、硬件实验或论文编译；未修改论文、PDF、代码、实验或图片。
