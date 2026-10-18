# B1：从严格收缩预算显式构造纯 QP 终端多面体

2026-10-18。纯理论；不修改论文或控制器，不做数值验证，不进入P5。
前置：Explicit_Dynamics_Jacobian_Derivation.md 的D7–D10与Reduced_PBH_and_Periodic_Reference.md。

## 1. 前提与量化目标

在非重复q坐标和模型可实现参考上，记e为旧Frozen终端误差，tail=u_ref+K_t e。新采样名义shift候选的完整终端误差记为T_t(e,d,w)。它不是未来plant真实终端状态。
已通过D7及重新编码初值传播取得统一外包

\[
\|T_t(e,d,w)\|_{P_{t+1}}
\le\lambda\|e\|_{P_t}+c(\|e\|_{P_t}+\Delta)^2+d_0,
\quad\lambda<1.
\tag{C1}
\]

d_0含A_t d_fr、参考缺陷与传播后的D_init，不能再额外加首步编码误差。这里所有常数均为待独立认证的统一上界，不因给出构造就成为当前实例事实。

明确要求P_t为实对称正定矩阵，使用其正定平方根，且0<=lambda<1、c>=0、Delta>=0、d_0>=0；所有范数等价因子已纳入C1。原QP目标Hessian仍须半正定，新增线性面本身不替代这个凸性前提。

选择r>0使

\[
\lambda r+c(r+\Delta)^2+d_0<r.
\tag{C2}
\]

严格不等式比D10的非严格可行更强。以下构造需要严格余量；等号成立时不声称存在有限面逼近证书。

## 2. 选定面方向，而不假设存在合适多面体

在s维单位球面选有限对称theta-net V={v_l}，0<theta<pi/2：每个单位方向与某个v_l夹角不超过theta。紧致性保证有限网存在，可通过确定性球面网格/有限覆盖生成；本轮不运行网格。
令alpha=cos(theta)>0，定义

\[
Z_t=\{e:v_l^TP_t^{1/2}e\le\alpha r,\ \forall l\}.
\tag{C3}
\]

则

\[
\mathbb B_{P_t}(\alpha r)\subseteq Z_t
\subseteq\mathbb B_{P_t}(r).
\tag{C4}
\]

证明：内包含由Cauchy不等式。外包含取y=P_t^{1/2}e，选与y方向夹角<=theta的面，有alpha||y||<=v_l^Ty<=alpha r。因此||y||<=r。对称有限网给有界中心对称多面体，含正半径球，故非空且有正内点。

## 3. 用严格预算选择有限网精度

令beta=[lambda r+c(r+Delta)^2+d0]/r。由C2有beta<1且beta>=0。选择0<theta<arccos(beta)，即alpha>beta。
对任何e∈Z_t，C1及C4给

\[
\|T_t(e,d,w)\|_{P_{t+1}}\le\beta r<\alpha r.
\]

因此

\[
T_t(Z_t,D_{fr},W_{enc})\subseteq
\mathbb B_{P_{t+1}}(\alpha r)\subseteq Z_{t+1}.
\tag{C5}
\]

这不是“球内多面体自动不变”的错误推理：面网精度明确由严格收缩余量选择，再用内外夹逼重新证明包含。
若P_t周期，直接沿用同一组V，生成有限周期多面体族；若P固定，仅需同一Z。

**条件性构造命题：** 给定C1、满足C2的r及合法邻域，可按C3显式生成一个鲁棒候选终端包含族；无需再假设某个未知G/alpha存在。

## 4. 输入、局部域与QP

若完整外球B_P(r)满足u_ref+K_t e∈U及余项线段域约束，则Z_t作为子集继承它们。对输入面a_u与正余量mu_t：

\[
r\|a_uK_tP_t^{-1/2}\|_2\le\mu_t
\]

即为充分条件。输入增量目前仅是成本，不新增硬约束；若未来批准硬增量面则另验(K_t-E_last)和参考输入差。

Frozen e_N对输入序列仿射，C3全是线性面，所以在线仍为凸QP，不是QCQP。K_t、P_t、r、V均离线固定；高精度V可能面数很大，有限存在不等于实时可用，不宣称实时性。

## 5. 接回实际QP最优解

把C3作为所有QP可行输入的终端硬约束，统一D_fr界覆盖整个候选域，则任一新最优解的Frozen终端均在Z_t，可重复C5。下一名义序列取shift-tail，B-EXACT使该名义候选的Frozen/full轨迹相等，C5遂提供下一终端硬约束可行性。

这只闭合终端关口：阶段工作域shift保持及初始新增QP可行种子仍需独立证明。若C1仅局部有效，必须保证预测与扰动线段都在该域；不能靠终端Z约束整条预测路径。

## 6. 与球形判别式的联系及失败边界

若c>0，D10判别式严格正且r可选在两个根之间，并满足r<=r_cap，则C2成立；若c=0且d0/(1-lambda)<r<=r_cap，也有C2。
若只有等号或可行区间仅一个点，本文有限网构造不适用；不据此断言其他多面体不存在。
若C1常数只是保守上界，C2失败也只表示该构造证书失败。

## 7. 状态

- C3–C5集合几何与推导：PROVED under C1/C2。
- 保持纯QP的有限面终端构造：CONDITIONAL，已给明确面生成规则。
- 当前具体学习模型C1/C2是否满足：OPEN，未选定/认证参数与参考。
- 阶段域、初始种子、实际plant：未由本文证明；P5 STOP。
