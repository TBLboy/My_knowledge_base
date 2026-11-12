# 输出跟踪 Single-Freeze MPC：控制器设计与证明路线

日期：2026-11-10。状态：**当前设计记录；尚未写入论文或控制代码。**

后续完整数学证明见[独立理论材料](../theory/20261110-output-tracking-complete-proof.md)。控制器未变；完整证明进一步得到精确缓存的移位预算缩紧，并确认本记录给出的全域粗常数下，Route 1的平均界和逐时刻半径必不优于已有域界。最终结论强度与证明细节以后续材料为准。

本轮仅记录，不修改 `Main.tex`、PDF、代码、实验或图片，不提交推送。后续改稿须另获授权。本文件替代[旧重构方案](../chapter4-output-tracking-rewrite-plan-20261110.md)中的控制器建议与证明路线。

## 1. 已定范围

- 参考接口只接受期望测量输出轨迹；不要求参考输入、参考增广状态，也不构造参考潜变量。
- 保留历史条件化 Transformer–Koopman 预测器、一次完整标称 rollout、一次系数冻结、一个凸 QP、施加首输入与移位。
- 代价直接写成**输出跟踪 + 输入增量惩罚**；终端使用相同输出权重。不保留带零权重的输入幅值项，不增加“为什么没有该项”的解释段。
- 证明主线：**Route 0 作有界性引理，Route 1 作基于移位值函数的主结果**；给长期平均平方输出误差界，另给逐时刻最终界。
- 不增加迭代 SQP、Jacobian 线性化、状态/输出硬约束、终端控制律或人工参考优化层。Route 2/3 不属于当前方案，也不自动加入正文或 future work。

这是对当前讨论结果的记录，不是已认证模型/plant 的结论；具体数值权重与求解器实施细节不在本轮决定。

## 2. 控制器契约

### 2.1 已有模型和输入

沿用第三章模型。测量维数为 $n$，输入维数为 $m$，提升维数为 $d$；历史长度 $P_h\ge2$，增广维数 $s_q=d+(P_h-1)(n+m)$。

\[
q_k^E=\operatorname{col}(z_k,a_k,v_k),\qquad
z_k=G_\theta(\mathcal X_k),\qquad x_k=C_mq_k^E,
\quad C_m=C_xE_z^\top\in\mathbb R^{n\times s_q}.
\]

$a_k$ 保存过去 $P_h-1$ 个测量，$v_k$ 保存过去 $P_h-1$ 个实际输入；$E_z$ 注入提升块。$E_{\rm prev}\in\mathbb R^{m\times s_q}$ 提取输入缓存最后一格，故 $E_{\rm prev}q_k^E=u_{k-1}$。

完整递推保持为
\[
F(q,u)=\operatorname{col}\bigl(A(c(q))z+B(C_xz)u,\ S_xa+E_xC_xz,\ S_uv+E_uu\bigr).
\]

在线给定：当前测量历史和已施加输入历史、输出参考窗口 $x^r_{k:k+N}$、固定部署模型、$N\ge1$、权重及输入可行集。**“只接受输出参考”仅限定参考接口，不删除实际输入历史。**

参考为同一条绝对时间序列 $\{x_t^r\}_{t\ge0}\subset\mathbb R^n$；相邻窗口对重叠时刻使用同一参考值。当前 QP 不需要 $x^r_{k+N+1}$，该值在下一时刻窗口和证明中的尾部项使用。不隐含“每次重新预测并修改重叠参考”的机制。

### 2.2 单次 rollout 与冻结

从可行标称序列 $\bar U_k\in\mathcal U^N$ 出发：
\[
\bar q_{0|k}=q_k^E,\qquad
\bar q_{i+1|k}=F(\bar q_{i|k},\bar u_{i|k}),\quad 0\le i<N.
\]

沿该轨迹计算 $\bar A_{i|k}=A(c(\bar q_{i|k}))$ 和 $\bar B_{i|k}=B(C_m\bar q_{i|k})$，并冻结
\[
M_{i|k}=\begin{bmatrix}\bar A_{i|k}&0&0\\E_xC_x&S_x&0\\0&0&S_u\end{bmatrix},\qquad
D_{i|k}=\operatorname{col}(\bar B_{i|k},0,E_u).
\]

QP 内使用 $p_{i+1|k}=M_{i|k}p_{i|k}+D_{i|k}u_{i|k}$，$p_{0|k}=q_k^E$，不随候选输入重新冻结。沿预测历史递归传播 latent/cache，不把 latent 每步重编码成新的 $G_\theta(\mathcal X)$。

沿标称输入有 $p_{i|k}(\bar U_k)=\bar q_{i|k}$；对任意首输入有 $p_{1|k}=F(q_k^E,u_{0|k})$。这两条是后续移位证明的接口。

### 2.3 代价与 QP

令 $Q\in\mathbb R^{n\times n}\succ0$、$S\in\mathbb R^{m\times m}\succ0$，定义
\[
\boxed{\ell_t(p,u)=\|C_mp-x_t^r\|_Q^2+\|u-E_{\rm prev}p\|_S^2,\qquad
V_f(t,p)=\|C_mp-x_t^r\|_Q^2.}
\]

终端与阶段输出权重相同，不再使用旧的 $\beta\Pi$ 终端项。$\Pi$ 仍是模型收缩与分析域的度量，不是新跟踪代价的权重。

\[
\begin{aligned}
\min_U\quad &J_k^{\rm fr}(U;\bar U_k)
=\sum_{i=0}^{N-1}\ell_{k+i}(p_{i|k},u_{i|k})+V_f(k+N,p_{N|k})\\
\text{s.t.}\quad &p_{0|k}=q_k^E,\\
&p_{i+1|k}=M_{i|k}p_{i|k}+D_{i|k}u_{i|k},\\
&u_{i|k}\in\mathcal U,\qquad 0\le i<N.
\end{aligned}
\]

$U=\operatorname{col}(u_{0|k},\ldots,u_{N-1|k})\in\mathbb R^{Nm}$ 是唯一独立决策变量；$p$ 由递推确定。沿用非空紧凸多面体 $\mathcal U=\{u:H_uu\le h_u\}$。没有新增状态或输入增量硬约束；$S$ 项是增量的**软惩罚**，$\mathcal U$ 是输入幅值的**硬约束**，$\mathcal Q$ 仅为分析域。

### 2.4 严格凸性与求解返回条件

缓存递推给出 $E_{\rm prev}p_{i+1|k}=u_{i|k}$，因此
\[
\Delta\mathbf u=\mathcal D_\Delta U-b_k,\quad
b_k=\operatorname{col}(u_{k-1},0,\ldots,0),\quad
\mathcal D_\Delta=\begin{bmatrix}I_m&0&\cdots&0\\-I_m&I_m&\cdots&0\\&\ddots&\ddots&\vdots\\0&\cdots&-I_m&I_m\end{bmatrix}.
\]

当 $N=1$ 时，$\mathcal D_\Delta=I_m$。此仿射映射的线性部分可逆，故
$\mathcal D_\Delta^\top(I_N\otimes S)\mathcal D_\Delta\succ0$；其他二次项半正定，凝聚 Hessian 正定。连续目标在非空紧可行集上取到最小值，严格凸性保证最优序列唯一。

令 $W_k=\min_{U\in\mathcal U^N}J_k^{\rm fr}(U;\bar U_k)$。返回序列 $\widehat U_k$ 必须原始可行；Route 1 还要求
\[
0\le J_k^{\rm fr}(\widehat U_k;\bar U_k)-W_k\le\delta_k\le\bar\delta.
\]

$W_k$ 依赖本次 $q_k^E$、$\bar U_k$ 和参考窗口，不能省略控制器的标称序列记忆而视为仅由 $q_k^E$ 决定。值函数定义及移位比较本身不依赖最优序列的唯一性；这里唯一性由所选权重另行保证。

### 2.5 执行与下一时刻标称序列

\[
\boxed{u_k=\widehat u_{0|k},\qquad
\bar U_{k+1}=(\widehat u_{1|k},\ldots,\widehat u_{N-1|k},\widehat u_{N-1|k}).}
\]

当 $N=1$ 时，$\bar U_{k+1}=(\widehat u_{0|k})$。初始化使用已知可行的 $u_{-1}\in\mathcal U$、一致的实际历史和任意 $\bar U_0\in\mathcal U^N$。移位基于**实际返回序列**，而非假想的精确最优序列；不混合另一条 warm start。原始可行序列的移位/重复仍可行；此事实本身不证明稳定性。

## 3. 证明条件

沿用原 Assumption 1 的统一模型条件，不因更换代价而假定它们自动成立：
\[
\begin{gathered}
\mathcal Q=\{q:\|q\|_\Pi\le M\},\quad\Pi\succ0,\quad q_0^E\in\mathcal Q,\\
\|F(q,u)-F(q',u)\|_\Pi\le\lambda\|q-q'\|_\Pi,\\
\|F^{\rm fr}(q,u)-F^{\rm fr}(q',u)\|_\Pi\le\lambda_{\rm fr}\|q-q'\|_\Pi,\\
\|F(0,u)\|_\Pi,\ \|F^{\rm fr}(0,u)\|_\Pi\le b_u,\qquad
\|F(q,u)-F^{\rm fr}(q,u)\|_\Pi\le\bar\eta,\\
q_{k+1}^E=F(q_k^E,u_k)+w_k,\qquad\|w_k\|_\Pi\le\bar w,\\
0\le\lambda,\lambda_{\rm fr}<1,\qquad
\lambda M+b_u+\bar w\le M,\quad\lambda_{\rm fr}M+b_u\le M.
\end{gathered}
\]

量词：所有 $q,q'\in\mathcal Q$、$u\in\mathcal U$，以及由 $\mathcal Q$ 内标称点产生的所有冻结映射，常数对时间统一。残差条件适用于当前编码状态在域内的实际测量转移；输入按返回首项准确施加。先由半径条件归纳域不变，再使用域内比较，不能预先假定所有未来预测都在域内。

新增参考条件：$\sup_{t\ge0}\|x_t^r\|_2\le\bar r<\infty$。不假设存在参考增广状态/输入见证对，不使用单时刻输出反推整个提升状态的 A3′。

## 4. Route 0：基础有界性引理

置 $c_m=\|C_m\Pi^{-1/2}\|_2$。同输入收缩给出
\[
\|q_{k+1}^E\|_\Pi\le\lambda\|q_k^E\|_\Pi+b_u+\bar w,
\]
从而
\[
\|q_k^E\|_\Pi\le\lambda^k\|q_0^E\|_\Pi+
\frac{1-\lambda^k}{1-\lambda}(b_u+\bar w).
\]

定义 $e_k^x=x_k-x_k^r$，则
\[
\|e_k^x\|_2\le c_m\|q_k^E\|_\Pi+\bar r,\qquad
\limsup_{k\to\infty}\|e_k^x\|_2\le
r_0:=c_m\frac{b_u+\bar w}{1-\lambda}+\bar r.
\]

另有全时刻域界 $\|e_k^x\|_2\le c_mM+\bar r$。该引理对任意可行输入序列成立，不使用 MPC 最优性，不能作为“优化保证精确跟踪”的证据。

## 5. Route 1：移位值比较与平均性能主结果

### 5.1 尾部精确记账

令 $p_i=p_{i|k}(\widehat U_k)$、$u_\ell=\widehat u_{N-1|k}$。缓存满足 $E_{\rm prev}p_N=u_\ell$，故
\[
\ell_{k+N}(p_N,u_\ell)=\|C_mp_N-x^r_{k+N}\|_Q^2=V_f(k+N,p_N).
\]

定义尾部缺陷
\[
\boxed{\tau_k=\|C_mF(p_N,u_\ell)-x^r_{k+N+1}\|_Q^2.}
\]

因此
\[
\ell_{k+N}(p_N,u_\ell)+V_f(k+N+1,F(p_N,u_\ell))-V_f(k+N,p_N)=\tau_k.
\]

旧端点使用 $x^r_{k+N}$，推进后的端点使用 $x^r_{k+N+1}$，两者不能混写。$\tau_k$ 是尾部跟踪代价，不是模型残差；即使模型/求解误差为零，也不能将它置零。

### 5.2 跨采样重冻结比较

令 $U^+=\bar U_{k+1}$；$\widetilde q_j$ 为从 $q_{k+1}^E$ 沿 $U^+$ 的完整递推。首步一致性给出 $q_{k+1}^E=p_1+w_k$。对 $0\le j<N$：
\[
d_j=\lambda^j\bar w+\bar\eta\sum_{s=0}^{j-1}\lambda^s,\qquad
\|\widetilde q_j-p_{j+1}\|_\Pi\le d_j.
\]

末步两边都使用完整映射和同一 $u_\ell$，故
\[
\|\widetilde q_N-F(p_N,u_\ell)\|_\Pi\le\lambda d_{N-1}.
\]

由于 $U^+$ 正是下一 QP 的标称序列，其冻结预测等于 $\widetilde q$。设
$c_p=\|E_{\rm prev}\Pi^{-1/2}\|_2$、$\bar u=\max_{u\in\mathcal U}\|u\|_2$，可取
\[
\begin{aligned}
L_f&=2\|Q\|_2(c_mM+\bar r)c_m,\\
L_\ell&=L_f+2\|S\|_2(\bar u+c_pM)c_p,\\
\varepsilon_{\rm sh}&=L_\ell\sum_{j=0}^{N-1}d_j+L_f\lambda d_{N-1}.
\end{aligned}
\]

这些是相同绝对时刻、相同输入下对状态的代价连续性界。空和为零，$\lambda^0=1$；$N=1$ 时 $\varepsilon_{\rm sh}=(L_\ell+\lambda L_f)\bar w$。

### 5.3 核心值函数关系

先用下一 QP 的可行候选 $U^+$ 上界其最优值，再比较匹配时刻的阶段/终端代价：
\[
\begin{aligned}
W_{k+1}&\le J_{k+1}^{\rm fr}(U^+;U^+)\\
&\le J_k^{\rm fr}(\widehat U_k;\bar U_k)-\ell_k(q_k^E,u_k)+\tau_k+\varepsilon_{\rm sh}\\
&\le W_k-\ell_k(q_k^E,u_k)+\tau_k+\varepsilon_{\rm sh}+\delta_k.
\end{aligned}
\]

这里仅加 $\delta_k$，不加 $\delta_{k+1}$。该关系不声称 $W_k$ 单调下降。

### 5.4 主结论：长期平均平方输出误差界

时间求和并用 $W_T\ge0$、$\ell_k\ge\lambda_{\min}(Q)\|e_k^x\|_2^2$，得
\[
\frac1T\sum_{k=0}^{T-1}\|e_k^x\|_2^2\le
\frac{W_0+\sum_{k=0}^{T-1}(\tau_k+\varepsilon_{\rm sh}+\delta_k)}{T\lambda_{\min}(Q)}.
\]

因为 $F(p_N,u_\ell)\in\mathcal Q$，可取
$\bar\tau=\|Q\|_2(c_mM+\bar r)^2$，于是
\[
\boxed{\limsup_{T\to\infty}\frac1T\sum_{k=0}^{T-1}\|e_k^x\|_2^2
\le\frac{\bar\tau+\varepsilon_{\rm sh}+\bar\delta}{\lambda_{\min}(Q)}.}
\]

同一求和式还给出平均输入增量能量界
$\limsup_{T\to\infty}T^{-1}\sum_{k=0}^{T-1}\|u_k-u_{k-1}\|_S^2\le\bar\tau+\varepsilon_{\rm sh}+\bar\delta$。

### 5.5 附加推论：逐时刻最终界

取可行常值候选 $U_k^c=(u_{k-1},\ldots,u_{k-1})$。其所有增量为零，后续 $N-1$ 个阶段输出项和一个终端输出项一共 $N$ 项，故
\[
\|e_k^x\|_Q^2\le W_k\le\|e_k^x\|_Q^2+\bar B,\qquad
\bar B=N\|Q\|_2(c_mM+\bar r)^2.
\]

代入值比较：$W_{k+1}\le\bar B+\tau_k+\varepsilon_{\rm sh}+\delta_k$，因此
\[
\boxed{\limsup_{k\to\infty}\|e_k^x\|_2\le
r_1:=\sqrt{\frac{\bar B+\bar\tau+\varepsilon_{\rm sh}+\bar\delta}{\lambda_{\min}(Q)}}.}
\]

在统一界从 $k=0$ 成立时，此平方根界实际上对所有 $k\ge1$ 成立。最终可取已证明界的较小者；$r_1$ 不保证优于 $r_0$，全域常数可能很保守。平均界不能当作逐时刻误差小，以上结论均不自动构成 ISS、指数跟踪到零或隐藏物理状态 $s_k$ 的稳定性证明。

## 6. 明确撤回的旧内容

| 旧内容 | 当前处理 |
|---|---|
| 外部参考对、参考编码、可选输入幅值项 | 不进入当前控制器；直接使用 $x^r$ 与两项阶段代价 |
| A3′、参考/见证对、由它们接回 ISS 的路线 | 不采用，不从当前输出反推潜变量/历史 |
| 旧终端权重下界、参考输入终端下降及 $\tau_{\rm ref}$ | 由同权终端代价与显式 $\tau_k$ 记账替代 |
| “没有参考输入就只能采用某一种代价”及删项辩护段 | 不写；不是数学必然命题 |
| “没有增量惩罚就一定不唯一/尾部消去失败” | 撤回：输出预测也可能提供正定 Hessian，尾部消去本身不要求保留增量项；当前设计仍选 $S\succ0$ |
| “值函数定义或移位证明必须依赖最优序列唯一” | 撤回：最优值与可行返回序列足以开展比较 |
| “有紧集却不能用其证明解存在” | 撤回：连续目标在非空紧集上取到最小值是有效证明 |
| Route 2 一步收缩约束 / Route 3 终端控制律 | 均未纳入；不保留先前“终端不等式自动等价于 Riccati/LMI、自动恢复指数结论”的说法 |

上述纠正供后续恢复任务时防止复用错误，不要求把这些讨论写进论文。

## 7. 后续实施边界与验收

### 7.1 影响位置（本轮不实施）

| 位置 | 后续必要工作 |
|---|---|
| IV-A：参考、代价、QP、凸性、移位及 Algorithm 1 | 按 §2 对齐；保留当前章节结构与单次冻结机制 |
| IV-B | 保留统一模型条件；参考假设改为输出有界；按 Route 0 引理 + Route 1 主结果 + 最终界推论重建 |
| Appendix B | 新输出/增量代价对应的 Hessian、$L_\ell,L_f,\varepsilon_{\rm sh}$；保留有效预测/移位误差结构 |
| Appendix C | 尾部消去、跨轮值比较、时间求和与常值输入候选；保留可认证求解器误差接口 |
| 摘要/引言/结论的理论声称 | 正式改稿时仅同步被新定理影响的句子；不增加实验结论 |
| 第三章、附录 A、训练/控制代码、实验/图片 | 本轮不改；实现与理论不一致记为后续待对齐，不迁就暂时代码 |

删除旧条件/公式后重新核查编号和引用，不承诺仍保留原来的 61 个公式。后续若改稿，旧蓝恢复黑色、新修改标蓝，执行真实编译及版面检查。

### 7.2 运行与异常边界

- 控制器每拍只更新测量编码和标称输入记忆；部署参数不在线训练，无新增并发、事务或持久化机制。
- 原始可行性与次优差距必须由实际求解器可靠保证/认证；“success”标志不是差距证书。现有可行解/对偶下界证书框架可保留，但未验证具体求解器实现。
- 本轮不设计失败回退、超时、重试或执行器后处理。改变输入、改写标称序列、参考重叠窗口变更，均可能超出上述证明；不能默认覆盖。
- 不新增依赖、网络接口、费用、安全/隐私处理或日志/监控模块；未来数值核验所需量为可行性、求解差距及模型/冻结/尾部误差预算，不新建遥测系统。
- 本轮仅新增设计记录并更新旧入口，无部署、迁移、feature flag 或产品回滚需求。兼容性变化仅记录为将来的参考接口与控制代价替换，不提供未请求的双控制器兼容层。

### 7.3 验收与证据状态

| 检查 | 本轮状态 / 后续要求 |
|---|---|
| 控制器参考接口、两项代价、单次 QP 与移位 | 已对照当前论文和用户讨论进行静态核查 |
| 时间索引、缓存恒等式、差分仿射项、尾部消去 | 已逐式核查；旧端点为 $k+N$，新端点为 $k+N+1$ |
| $N=1$、空和、常值候选计数 | 已静态核查；一项终端误差、一次重复输入，预算为 $(L_\ell+\lambda L_f)\bar w$ |
| 证明主线与假设 | 记录的是条件推导；不是目标模型/plant 的数值认证 |
| 原稿与 PDF | 本轮只读；不编译、不写回 |
| 正式改稿及编译 | 未实施，待用户授权 |
| 实验/训练/实时性 | 未运行、未认证，不据此声称性能提升 |

未决项：目标实例是否满足统一收缩/残差界、实际 $Q,S$ 数值、求解器证书与截止时间。当前以完整测量输出参考 $x^r\in\mathbb R^n$ 记录；如以后仅跟踪部分测量，需明确输出选择矩阵，不擅自补全参考。上述项目不阻止本次记录交付，但不能被视为已验证。

## 8. 依据与基线

- 用户本轮指示：先不改论文，记录最终控制器部分与理论证明路线；此前明确直接删掉输入幅值项，不附冗余解释。
- 当前源码：`Transformer-Koopman/论文/新版本/Main.tex`，IV-A/IV-B 与附录 B/C（仍是旧参考对控制器）；相关标签 `eq:nominal_rollout`、`eq:frozen_model`、`eq:stage_cost`、`eq:quadratic_template`、`eq:nominal_shift`、`ass:domain`、`eq:solver_gap`、`eq:shift_error`。
- 外部分析报告：`C:/Users/12187/Downloads/第四章输出跟踪MPC_稳定性证明链路分析与修改建议.md`，§4–6、§8–10；本记录已包含当前采用路线的公式，不依赖 Downloads 附件才能恢复。
- 记录时内层仓库分支 `paper`，HEAD `003b679`，与 `origin/paper` 对齐；现有未跟踪第三方 PDF 保留。
- `Main.tex` SHA256：`B5FA8EF6D21F84BDBA8FE83FEA27FC7DE7D0F502963AD929A85D6AF276A8CFC1`。
- `Main.pdf` SHA256：`F38CAA223713D8A2EEE3B375ACB6F07B79830CDE980C85B316825DE5880C1966`。
