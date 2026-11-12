# 论文主理论：历史条件化模型、单次冻结 MPC 与实用轨迹跟踪

版本 v1.1，2026-11-12。**理论定稿材料，非已修改的论文。** 本文只有一个闭环主定理；推导、非空性证明和审查边界放在[内部推导](20261111-ieee-final-theory-route-and-proof.md)，不随正文展开。实际训练模型的区域证书尚未提供。

## 1. 历史条件化预测模型

对测量 $x_k\in\mathbb R^n$、输入 $u_k\in\mathbb R^m$，取历史长度 $P\ge2$，定义
\[
X_k=\operatorname{col}(x_{k-P+1},\ldots,x_k),\quad
a_k=\operatorname{col}(x_{k-P+1},\ldots,x_{k-1}),\quad
v_k=\operatorname{col}(u_{k-P+1},\ldots,u_{k-1}).
\]
测量保持升维为 $z_k^E=G_\theta(X_k)=\operatorname{col}(x_k,\psi_\theta(X_k))\in\mathbb R^d$，$C_x=[I_n\ 0]$。完整预测器以 $q=\operatorname{col}(z,a,v)$ 维护调度历史：
\[
c(q)=C_\phi(\operatorname{col}(a,C_xz),v),\qquad
F(q,u)=\begin{bmatrix}
A(c(q))z+B(C_xz)u\\ S_xa+E_xC_xz\\ S_uv+E_uu
\end{bmatrix}. \tag{1}
\]
$S_x,S_u$ 删除缓存最旧的一块并移位，$E_x,E_u$ 向末端插入当前测量、当前输入。$q$ 是递归包装，不是跟踪对象。第三章的低秩形式保留：
\[
A(c)=A_0+U_A\operatorname{diag}(\gamma_A(c))V_A^\top,\quad
B(x)=B_0+U_B\operatorname{diag}(\gamma_B(x))V_B^\top. \tag{2}
\]
在实际测量时重新编码 $q_k^E=\operatorname{col}(G_\theta(X_k),a_k,v_k)$；在预测时按 (1) 递归传播，不逐步重新调用 $G_\theta$。实际与模型之间的关系写成
\[
q_{k+1}^E=F(q_k^E,u_k)+\operatorname{col}(w_k^z,0,0),\qquad e_k^m=C_xw_k^z. \tag{3}
\]
式 (3) 定义物理一步预测残差，不假设有限历史可精确重构真实物理状态。

## 2. 动态参考的单次冻结 QP

用户提供完整测量坐标中的参考 $x_j^r$。在时刻 $k$，使用 $r_k=\operatorname{col}(x_{k+1}^r,\ldots,x_{k+N}^r)$，预测时域 $N\ge1$。单步输入集合 $\mathcal U\subset\mathbb R^m$ 为非空紧凸多面体，$K=\mathcal U^N$。

取初始可行种子 $\bar U_0\in K$；以后将上一拍返回的可行序列左移并重复其最后一项，得到 $\bar U_k\in K$。该种子在读取当前窗口之前已由过去数据确定。执行一次完整标称展开：
\[
\bar q_{0|k}=q_k^E,\quad \bar q_{i+1|k}=F(\bar q_{i|k},\bar u_{i|k}),\quad
\bar A_{i|k}=A(c(\bar q_{i|k})),\quad \bar B_{i|k}=B(C_x\bar z_{i|k}). \tag{4}
\]
冻结系数后，只优化 $U=\operatorname{col}(u_{0|k},\ldots,u_{N-1|k})$：
\[
\begin{aligned}
\min_{U\in K}\quad J_k(U)&=\sum_{i=1}^N\|C_xz_{i|k}-x_{k+i}^r\|_{Q_x}^2
 +\sum_{i=0}^{N-1}\|u_{i|k}\|_{R_u}^2,\\
z_{0|k}&=G_\theta(X_k),\\
z_{i+1|k}&=\bar A_{i|k}z_{i|k}+\bar B_{i|k}u_{i|k},\quad 0\le i<N,
\end{aligned} \tag{5}
\]
其中 $Q_x\succ0,R_u\succ0$。这等价于升维跟踪权重 $Q=\operatorname{diag}(Q_x,0_{d-n})$，不要求潜在特征跟踪参考，不需要 $q^r$ 或 $u^r$。实施唯一最优解的首输入 $u_k=\pi_k=e_0^\top U_k^\star$，其中 $e_0^\top=[I_m\ 0]$，下一拍重算 (4)–(5)。没有第二次冻结、稳态选择器、首输入护栏或硬终端条件。

冻结后缓存不再反馈到 $z$ 递推；因此 (5) 是完整冻结模型的等价第一分块，而不是另换一个固定 Koopman 模型。

## 3. 从 QP 得到实际反馈的区域证书

比较窗口时固定 $\vartheta_k=(v_k,\bar U_k,r_k)$。消元得到预测测量 $Y=S(X;\vartheta_k)U+t(X;\vartheta_k)$，以及
\[
J_k(U;X)=\tfrac12U^\top H(X)U+h(X)^\top U+c(X),\quad
H=2(S^\top\bar Q S+\bar R),\quad h=2S^\top\bar Q(t-r_k), \tag{6}
\]
其中 $\bar Q=I_N\otimes Q_x,\bar R=I_N\otimes R_u$。故 $H\succeq\mu I$，$\mu=2\lambda_{\min}(R_u)>0$。只要标称展开有定义，固定 $K$ 非空即保证 QP 可行且最优解唯一。

定义当前一步物理读出及由实际 QP 决定的反馈映射：
\[
\phi(X,u;v)=C_x[A(c(q^E(X,v)))G_\theta(X)+B(C_xG_\theta(X))u],\quad
T_k(X;\vartheta_k)=\phi(X,\pi_k(X;\vartheta_k);v_k). \tag{7}
\]
冻结首步使用同一个 $q^E$，所以对任何首输入都与 (1) 首步相同；由 (3)，实际闭环为 $x_{k+1}=T_k(X_k;\vartheta_k)+e_k^m$。后续冻结对优化首输入的影响已经包含在 $T_k$ 中。

取**仅用于证明**的固定度量 $W\in\mathbb R^{n\times n},W\succ0$，定义 $\|y\|_W=\sqrt{y^\top Wy}$ 和 $\|\Delta X\|_{h,W}=\max_j\|\Delta x_j\|_W$。$W$ 不改变 (5) 的 $Q_x$ 或控制律。

**引理 1（QP 反馈的区域灵敏度）。** 在凸窗口域上，设模型及有限次标称展开为 $C^1$，$H,h$ 关于历史范数的 Lipschitz 常数为 $L_H,L_h$（输出分别用谱范数和欧氏范数），且 $M_U=\max_{U\in K}\|U\|_2$。则
\[
\|U^\star(X)-U^\star(X')\|_2\le\frac{L_HM_U+L_h}{\mu}\|X-X'\|_{h,W}. \tag{8}
\]
进一步，对域内每条比较线段，假设存在有限分段，每段最优解由一个 $C^1$ 的固定活跃集 KKT 分支表示；所用活跃矩阵 $C_A$ 行满秩，边界使用分支的连续延拓。在每个分支上，由
\[
\begin{bmatrix}H&C_A^\top\\C_A&0\end{bmatrix}
\begin{bmatrix}D_XU^\star[\Delta X]\\D_X\lambda_A[\Delta X]\end{bmatrix}
=-\begin{bmatrix}DH[\Delta X]U^\star+Dh[\Delta X]\\0\end{bmatrix},\quad
\mathcal J=D_X\phi+D_u\phi\,e_0^\top D_XU^\star \tag{9}
\]
计算导数。其中 $D_X\phi$ 是固定 $u$ 的偏导，两项均在 $u=\pi_k(X;\vartheta_k)$ 处取值。若所有相关分支（含边界延拓）统一满足 $\|\mathcal J\|_{h,W\to W}\le\rho<1$，则
\[
\|T_k(X;\vartheta_k)-T_k(X';\vartheta_k)\|_W\le\rho\|X-X'\|_{h,W}. \tag{10}
\]

**证明。** 令 $U=U^\star(X),U'=U^\star(X')$。两组变分最优性条件相加，得到
\[
\mu\|U-U'\|_2^2\le
\langle[H(X')-H(X)]U'+h(X')-h(X),U-U'\rangle.
\]
使用 Lipschitz 界即得 (8)，特别保证跨活跃集连续性。$H\succ0$ 和 $C_A$ 行满秩使 KKT 矩阵可逆，分支微分得到 (9)。沿每段积分、利用边界连续性求和，得到 (10)。□

有限线段分段性是证书的显式条件，不仅由“约束条数有限”自动推出。所有界须覆盖整个指定域及允许的采样参数；只检查一个运行点不能认证 (10)。

## 4. 唯一主定理：移动参考管内的实用指数跟踪

给定有界参考序列（含 $P$ 个初始参考点），取半径 $r>0$，预先定义
\[
X_k^r=\operatorname{col}(x_{k-P+1}^r,\ldots,x_k^r),\quad
\mathcal D_k(r)=\{X:\|X-X_k^r\|_{h,W}\le r\}. \tag{11}
\]
这些管截面是凸集。证书在**整个截面**上建立，而不是先假设实际轨迹永远留在截面内。

**定理 1。** 对所有 $k$、$X\in\mathcal D_k(r)$、$v\in\mathcal U^{P-1}$、$\bar U\in K$，假设：

1. 编码器、调度器和完整模型在所需有限标称展开的紧致像集邻域内为 $C^1$；引理 1 的区域证书以同一个 $W,\rho<1$ 成立。
2. 对上述参数的参考中心，闭环偏差有统一上界
   $b_k(\vartheta)=\|T_k(X_k^r;\vartheta)-x_{k+1}^r\|_W\le\bar b$。
3. 对当前窗口在管内、输入在 $\mathcal U$ 内的真实转移，物理残差满足 $\omega_k:=\|e_k^m\|_W\le\bar\omega$。
4. 初始输入缓存可行，$E_0\le r$，且 $\bar b+\bar\omega\le(1-\rho)r$，其中 $E_k=\max_{0\le j<P}\|x_{k-j}-x_{k-j}^r\|_W$。

采用 (4)–(5) 的精确最优首输入时，每拍 QP 可行、输入可行，且 $X_k\in\mathcal D_k(r)$ 对所有 $k\ge0$ 成立。令 $\beta=(\bar b+\bar\omega)/(1-\rho)$，则
\[
\boxed{E_k\le\beta+\rho^{\lfloor k/P\rfloor}(E_0-\beta)_+.} \tag{12}
\]
在物理代价范数下，
\[
\|x_k-x_k^r\|_{Q_x}\le c_{QW}\,[\beta+\rho^{\lfloor k/P\rfloor}(E_0-\beta)_+],\quad
c_{QW}=\sqrt{\lambda_{\max}(W^{-1/2}Q_xW^{-1/2})}. \tag{13}
\]

**证明。** 若 $X_k\in\mathcal D_k(r)$，(6) 给出唯一最优解，首输入及移位种子保持输入约束。由 (7)、(10) 和参考中心偏差，
\[
\|x_{k+1}-x_{k+1}^r\|_W\le\rho E_k+b_k(\vartheta_k)+\omega_k\le\rho r+\bar b+\bar\omega\le r. \tag{14}
\]
其余 $P-1$ 块只是移位，仍与各自同一参考时间索引比较。因此归纳得到全部时刻的管不变性和良定性。令 $V_k=(E_k-\beta)_+$；(14) 给出每个新误差的正部不超过 $\rho V_k$，故 $V_{k+1}\le V_k$。经过 $P$ 步所有旧误差退出窗口，有 $V_{k+P}\le\rho V_k$，从而得到 (12)；范数等价给出 (13)。□

采用 $0^0=1$ 约定。当 $\bar b=\bar\omega=0$ 时，(12) 给出零误差指数收敛；当 $\rho=0$ 时对应至多一个历史窗口后进入最终界。一般动态参考下只主张实用跟踪，不默认中心偏差为零。

**数值求解扩展。** 若返回的序列 $\widehat U_k\in K$ 满足可认证目标差 $J_k(\widehat U_k)-J_k(U_k^\star)\le\delta_k\le\bar\delta$，则强凸性和约束最优性给出 $\|\widehat U_k-U_k^\star\|_2\le\sqrt{2\delta_k/\mu}$。令 $L_u=\sup\|W^{1/2}C_xB(x)\|_2$；将定理中的 $\bar b+\bar\omega$ 换成 $\bar b+\bar\omega+L_u\sqrt{2\bar\delta/\mu}$ 即得相同结论，包括管自洽条件。不可行解、无证书的超时输出不属于该扩展。

## 5. 写入论文的边界

正文保留 (1)–(14) 所表达的“建模—单次冻结控制—一个主定理”，可按已有章节局部排版；式号仅为本材料内部编号。QP 参数导数的展开、非空性算例和探索路线剪枝表留在内部推导，正文不讲 Stage 1–7。

输入幅值正则 $R_u\succ0$ 是本版明确选择的理论控制器，不是已实现控制器的认证。III-B 的全局同输入强收缩不再是主定理前提，可从正文主链移除。$W$ 仅是分析度量，**不改** $Q=\operatorname{diag}(Q_x,0)$，也不添加状态/终端约束或参考输入接口。

该结果是对真实首输入算法的**区域充分条件定理**。它不由强凸性自动推出稳定性，不保证真实隐状态安全，不认证任意训练权重，也不保证论文录用。实际网络的 $\rho,\bar b,\bar\omega$ 及区域大小尚未核验；没有这些证据时，只能按条件性定理表述。论文正文、代码、实验、图片均未修改。
