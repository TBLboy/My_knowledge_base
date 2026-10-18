# Transformer–Koopman：理论先行的 Frozen-LTV MPC 闭环稳定性证明（研究稿 V2：整合外部审查）

**日期：2026-10-18**  
**修订说明：** V2 采纳外部独立静态审查的可核验补强：固定绝对时间参考、紧输入集、缓存扰动措辞、阶段 Lipschitz 常数、开环骨架联合选参、显式两周期参考和输入误差推论。新增细节均为对新模型类的条件性论证，不是当前 checkpoint 或实际 plant 的认证。  
**任务定位：** 从当前论文及 Agent 的 B1 原始证书出发，提出一个**新的、可构造的充分条件模型类**，直接贯通增广动力学、真实编码误差、单次 Frozen QP、跨采样价值下降和最终有界性。  
**结论等级：** 文中主定理是**在逐条写明的假设下完成证明的数学定理**；这些假设**尚未在现有训练模型/真实 plant 上联合认证**，也**未实施**于当前论文或控制代码。理论设计与现有论文的区别见 §10。  
**特别提醒：** 新主线要求完整增广模型对相同输入统一收缩；这是比 Agent 先前的“局部可稳定化 + 终端反馈”更强的模型类，不适用于所有需要不稳定开环模式的物理系统。它是有意选择的 *theory-first* 充分条件，并非声称现有模型自动满足。

## 0. 本轮最重要的研究裁决

原 B1 主线加入终端与工作域硬约束，因此必须逐层构造鲁棒终端多面体、阶段收紧和初始化证书。该路线有效但重，且现有模型实例证书未闭合。这里提出更短的新主线：

\[
\boxed{\begin{array}{c}
\text{收缩型历史条件完整增广模型 + 有界编码残差}\\
\Downarrow\\
\text{输入约束下的自动递归可行性 + 一次冻结凸 QP}\\
\Downarrow\\
\text{显式终端成本下降 + B-EXACT 移位候选}\\
\Downarrow\\
\text{直接 Frozen-QP 最优值下降}\\
\Downarrow\\
\text{时变参考的实际指数跟踪 / 最终有界性}
\end{array}}
\]

**与 B1 的根本区别：** 新设计**不添加状态/终端硬约束**，以结构性收缩保证一个共同紧工作域对所有允许输入不变；只需保留原输入约束。因此无须证明 B1 的终端收紧集合跨采样非空。B1 作为不具备增广开环收缩性时的备选，不宣告其错误。

## 1. 模型：保留原稿的历史条件调度，并采用非重复增广状态

令历史长度为 \(P_h\ge2\)，过去测量、输入分别为
\[
a_k=\operatorname{col}(x_{k-P_h+1},\ldots,x_{k-1}),\quad
v_k=\operatorname{col}(u_{k-P_h+1},\ldots,u_{k-1}).
\]
提升状态 \(z_k\in\mathbb R^d\)，\(x_k=C_xz_k\)，定义
\[
q_k=\operatorname{col}(z_k,a_k,v_k),\quad
X(q)=\operatorname{col}(a,C_xz),\quad
c(q)=C_\phi(X(q),v).
\]
完整调度增广映射为
\[
F(q,u)=\begin{bmatrix}
A(c(q))z+B(C_xz)u\\ S_xa+E_xC_xz\\ S_uv+E_uu
\end{bmatrix}.
\tag{1}
\]
注意过去测量窗口的下一次更新追加的是**当前** \(C_xz\)，而不是 \(C_xz^+\)；这与 Agent 非重复状态 D1 及原论文完整历史移位一致。当前输入不属于过去输入窗口，而独立进入 (1)。

在实际采样时用测量历史重新编码 \(z_k=g_\theta(X_k)\)。定义真实重新编码的增广状态 \(q_k^E\)，并明确以**实际测量层假设**描述建模残差：
\[
q_{k+1}^E=F(q_k^E,u_k)+w_k,\qquad \|w_k\|_\Pi\le\bar w.
\tag{2}
\]
其中 \(\Pi\succ0\)，\(\|e\|_\Pi=\sqrt{e^\top\Pi e}\)。对于 (1) 的非重复缓存，在无额外历史测量错位时，\(w_k=\operatorname{col}(r_k,0,0)\)，\(r_k\) 为原稿的一步编码残差。**这个界需要对实际闭环可能访问的历史和输入统一成立；训练平均 loss 不提供这个保证。** 若包含真实 plant 对测量的影响，它可以在测量残差中体现；结论仍不能推出未观测物理状态 \(s\) 的稳定性。

## 2. 冻结模型、参考和拟议控制器（算法定义）

**统一量词与时间约定。** 固定整数预测步长 \(N\ge1\)。输入集合 \(\mathcal U\subset\mathbb R^m\) 是非空、**紧**、凸的多面体（且下文参考使用的每个 \(u_t^{ref}\in\mathcal U\)）。设参考 \(\{(q_t^{ref},u_t^{ref})\}\) 是事先确定、按绝对时间索引的序列；每个时刻对同一未来绝对时刻的参考值不被重新修订。过去输入窗口与参考 \(q_t^{ref}\) 的缓存分量完全一致。若在线修改已计划的未来参考，本版定理不直接适用，必须加入参考修订误差。该时变参考既可以是非恒定模型轨道，也可具有 (5) 中统一有界的动力学缺陷。

在采样时刻 \(k\)，给定可行名义序列 \(\bar U_k\in\mathcal U^N\)，从 \(q_k^E\) 用 (1) 完整 rollout 得到 \(\bar q_{i|k}\) 与冻结系数
\[
\bar A_{i|k}=A(c(\bar q_{i|k})),\quad
\bar B_{i|k}=B(C_x\bar z_{i|k}).
\]
候选 \(U=(u_0,\ldots,u_{N-1})\) 的 Frozen 增广预测为
\[
p_{0|k}=q_k^E,\quad
p_{i+1|k}=F_{i|k}^{fr}(p_{i|k},u_i)
=\begin{bmatrix}
\bar A_{i|k}z_i+\bar B_{i|k}u_i\\
S_xa_i+E_xC_xz_i\\ S_uv_i+E_uu_i
\end{bmatrix}.
\tag{3}
\]
对固定冻结矩阵，整个 \(p_{i|k}\) 关于 \(U\) **仿射**。新名义序列严格采用
\[
\boxed{\bar U_{k+1}=(u_{1|k}^*,\ldots,u_{N-1|k}^*,u_{k+N}^{ref})},
\tag{4}
\]
初始名义可取当前参考输入序列。这里尾输入**只取参考输入**，不需要未知终端反馈或非线性 tail 求解。采样时仍是一次名义 full rollout、一次冻结、一次凸 QP。

### 2.1 时变参考与缺陷

允许 \(q_t^{ref},u_t^{ref}\) 随绝对时刻变化，且参考测量、历史输入窗口一致；\(u_t^{ref}\in\mathcal U\)。设
\[
\|F(q_t^{ref},u_t^{ref})-q_{t+1}^{ref}\|_\Pi\le\bar d_{ref}.
\tag{5}
\]
**模型可实现的时变参考**对应 \(\bar d_{ref}=0\)；近似可实现的测量参考允许 \(\bar d_{ref}>0\)。不将参考残差当成植物模型残差重复计数。参考序列要求留在下面定义的公共工作域中。

### 2.2 理论优先的阶段代价改造

从 \(q\) 的历史输入缓存提取上一输入 \(u_{prev}(q)=E_{prev}q\)，使参考上一步输入 \(u_{t-1}^{ref}=E_{prev}q_t^{ref}\)。定义
\[
\begin{aligned}
\ell_t(q,u)={}&\|q-q_t^{ref}\|_\Pi^2
 +\|u-u_t^{ref}\|_R^2\\
 &+\|(u-u_{prev}(q))-(u_t^{ref}-u_{t-1}^{ref})\|_S^2,
\end{aligned}
\tag{6}
\]
其中 \(R,S\succeq0\)。与原论文不同，这里**完整增广误差被正定惩罚**，且把绝对输入增量改为“相对参考增量”，使精确时变跟踪时代价为零。它是**设计建议，尚未改论文或代码**。该代价对 Frozen 预测和优化输入是凸二次型。

定义
\[
J_k^{fr}(U;\bar U_k)
=\sum_{i=0}^{N-1}\ell_{k+i}(p_{i|k},u_i)
+\beta\|p_{N|k}-q_{k+N}^{ref}\|_\Pi^2,
\tag{7}
\]
\[
W_k=W_k(q_k^E,\bar U_k):=
\min_{U\in\mathcal U^N}J_k^{fr}(U;\bar U_k).
\tag{8}
\]
只施加原输入多面体约束 \(u_i\in\mathcal U\)。因此只要 \(\mathcal U\ne\emptyset\)，每个 QP 非空；它的 Hessian PSD，若 \(R\succ0\) 则唯一最优解。状态预测对 U 仿射，包括缓存和输入增量，因此 (7) 仍是**单次凸 QP**。

## 3. 核心结构性假设：可验证的统一收缩工作域

存在 \(\Pi\succ0\)、\(\mathcal Q=\{q:\|q\|_\Pi\le M\}\)、\(0\le\lambda,\lambda_{fr}<1\)、\(b_u\ge0\)，使：

**C1（完整模型收缩）。** 对所有 \(q,\tilde q\in\mathcal Q\)、\(u\in\mathcal U\)，
\[
\|F(q,u)-F(\tilde q,u)\|_\Pi
\le\lambda\|q-\tilde q\|_\Pi.
\tag{9}
\]
**C2（冻结模型统一收缩）。** 对所有允许的冻结 \(\bar A,\bar B\) 以及 \(q,\tilde q\in\mathcal Q\)，
\[
\|F^{fr}_{\bar A,\bar B}(q,u)-F^{fr}_{\bar A,\bar B}(\tilde q,u)\|_\Pi
\le\lambda_{fr}\|q-\tilde q\|_\Pi.
\tag{10}
\]
**C3（统一驱动与残差）。** 对所有允许的 \(u\) 和名义调度矩阵，
\[
\|F(0,u)\|_\Pi,\quad
\|F^{fr}_{\bar A,\bar B}(0,u)\|_\Pi\le b_u,
\quad \|w_k\|_\Pi\le\bar w.
\]
选择工作域半径满足
\[
\boxed{M\ge\max\left\{
\frac{b_u+\bar w}{1-\lambda},\frac{b_u}{1-\lambda_{fr}}
\right\}.}
\tag{11}
\]
初始重新编码状态和参考均在 \(\mathcal Q\)，参考输入序列 admissible，参考本身留在 \(\mathcal Q\)。由于球凸，(9) 既可由 Jacobian 的统一算子范数界推出，也支持下文的跨输入序列逐步比较。

**推论 1（无循环的公共域保持）。** 对任意合法输入序列，真实重新编码状态、完整模型的任意候选轨迹、Frozen 任意候选和名义轨迹均位于 \(\mathcal Q\)。证明：分别由 (9)/(10) 与驱动界得 \(\|F(q,u)\|_\Pi\le\lambda M+b_u\)、\(\|F^{fr}(q,u)\|_\Pi\le\lambda_{fr}M+b_u\)，真实下一状态再加 \(\bar w\)；(11) 逐步归纳。**无需新增工作域硬约束或事先假设未来轨迹已合法。**

**C4（冻结缺陷统一界）。** 在 \(\mathcal Q\) 内，对于任意允许候选状态、输入及任意名义冻结矩阵，
\[
\|F(q,u)-F^{fr}_{\bar A,\bar B}(q,u)\|_\Pi\le\bar\eta.
\tag{12}
\]
例如，原稿低秩调度满足 \(\|A(c)-A_0\|\le g_A\)、\(\|B(x)-B_0\|\le g_B\)。令 \(E_z\) 为把 z 注入 q 的块算子，\(M_z=\sup_{q\in\mathcal Q}\|z\|_2\)，\(M_u=\sup_{u\in\mathcal U}\|u\|_2\)，则可取
\[
\boxed{\bar\eta
=\|\Pi^{1/2}E_z\|_2(2g_A M_z+2g_BM_u).}
\tag{13}
\]
这是保守但**显式、全候选统一**的界。它不是从单条名义轨迹外推的误差。冻结首步例外：同初值条件下 \(F(q,u)=F^{fr}_{0|k}(q,u)\) 对该采样时刻所有候选首输入精确成立。

### 3.1 该收缩模型类如何从架构中构造，而非假设某个未知 K

写出无调度增广骨架
\[
M_0=\begin{bmatrix}
A_0&0&0\\E_xC_x&S_x&0\\0&0&S_u
\end{bmatrix}.
\tag{14}
\]
若 \(A_0\) Schur，则由于 \(S_x,S_u\) 幂零，\(M_0\) 也 Schur。令 \(\Pi\succ0\) 是明确可由离散 Lyapunov 方程
\[
M_0^\top\Pi M_0-\Pi=-I
\tag{15}
\]
构造的解，于是 \(\lambda_0:=\|M_0\|_\Pi<1\)。这是**存在性和计算方法明确**的模型骨架设计，不要求在线搜索 K。

冻结增广线性部分
\[
M_{fr}(c)=\begin{bmatrix}
A(c)&0&0\\E_xC_x&S_x&0\\0&0&S_u
\end{bmatrix},
\]
满足
\[
\|M_{fr}(c)\|_\Pi\le\lambda_0+
\|\Pi^{1/2}E_z\|_2\,g_A\,\|E_z^\top\Pi^{-1/2}\|_2.
\tag{16}
\]
因此把右端限制为小于 1 即获得 C2。对完整模型，Jacobian 在 z 方向还包含
\[
DA(c(q))[Dc(q)\,\Delta q]z,
\qquad DB(C_xz)[C_x\Delta z]u.
\tag{17}
\]
若固定球 \(\mathcal Q\) 上有已知 \(L_A,L_B,\|Dc\|\) 界，(17) 给出 \(\|DF(q,u)-M_0\|_\Pi\) 的有限显式界；通过缩小低秩调度幅值/导数和限制 context 的谱范数，使
\[
\sup_{q\in\mathcal Q,u\in\mathcal U}\|DF(q,u)\|_\Pi
\le\lambda_0+\nu<1
\tag{18}
\]
即可得到 C1。设计时应先选择半径 M、骨架及输入边界，再联合检查 (11)、(16)、(18)，**不能先假设球 invariant 来证明它 invariant**。平滑 Transformer 或 MLP 均可使用，只要其实际参数化具有规定的统一导数界；网络名称本身不是证明。

**显式完整增广导数裕量。** 记 \(E_z\) 将 \(z\) 块嵌入 \(q\)，并定义
\[
 a_z=\|\Pi^{1/2}E_z\|_2,\quad
 b_z=\|E_z^\top\Pi^{-1/2}\|_2,\quad
 b_q=\|\Pi^{-1/2}\|_2,\quad
 b_x=\|C_xE_z^\top\Pi^{-1/2}\|_2.
\]
令 \(L_A,L_B\) 分别为矩阵值调度 \(A,B\) 的欧氏导数算子界，\(L_c\) 为 \(Dc(q)\) 的欧氏范数上界，\(M_z=\sup_{q\in\mathcal Q}\|z\|_2\)，\(M_u=\sup_{u\in\mathcal U}\|u\|_2\)。如果所需 Jacobian 在凸工作域及其连接线段上存在，利用 (17) 可明确取
\[
 \boxed{\nu_{\mathrm{bd}}=a_z\Big(g_A b_z+L_A L_cM_zb_q+L_BM_ub_x\Big),\quad
 \sup_{\mathcal Q\times\mathcal U}\|D_qF-M_0\|_\Pi\le\nu_{\mathrm{bd}}.}
 \tag{18a}
\]
因此 \(\lambda_0+\nu_{\mathrm{bd}}<1\) 足以推出 C1；\(\lambda_0+a_zg_Ab_z<1\) 足以推出 C2。这里的范数界须由**选定的网络类及参数限制**实际保证，不能仅由网络可微性保证。两条收缩界与 (11) 应**联合检查**。在非可微情形，须以直接差商／Lipschitz 外包替代此导数版本。

非空性可通过 \(g_A,g_B\) 的**足够小但非零**选择和有界输入/残差来保证（见 §9 的非平凡具体模型）。这条模型类牺牲对非收缩/开环不稳定系统的通用性，换取了闭环数学链条的可构造性。

## 4. 三个基础引理

### 引理 1：首步精确、有限时域冻结缺陷

在任意采样时刻，从共同 \(q_k^E\) 用同一候选输入序列 \(U\) 产生的 full 轨迹 \(q_i^{full}\) 与旧 Frozen 轨迹 \(p_i\) 满足
\[
q_0^{full}=p_0,\quad q_1^{full}=p_1,
\quad\|q_i^{full}-p_i\|_\Pi\le D_i,
\tag{19}
\]
其中
\[
D_0=D_1=0,\qquad
D_i=\bar\eta\sum_{s=0}^{i-2}\lambda^s\quad(i\ge2).
\tag{20}
\]
**证明。** 首步的 context 和测量完全相同，冻结 \(\bar A_0,\bar B_0\) 恰等于 full 的首步系数，故任意首输入均精确；其后
\[
\begin{aligned}
\|q_{i+1}^{full}-p_{i+1}\|_\Pi
&\le\|F(q_i^{full},u_i)-F(p_i,u_i)\|_\Pi\\
&\quad+\|F(p_i,u_i)-F_{i}^{fr}(p_i,u_i)\|_\Pi\\
&\le\lambda\|q_i^{full}-p_i\|_\Pi+\bar\eta.
\end{aligned}
\]
迭代即 (20)。因为公共域已经由推论 1 独立建立，整个比较无域假设循环。证毕。

### 引理 2：B-EXACT（本次可直接使用）

若从同一初值、沿同一个名义输入 \(\bar U\) 用完整 F 生成名义轨迹，然后按 (3) 冻结，则
\[
\boxed{p_i(\bar U;\bar U)=q_i^{full}(\bar U),\quad 0\le i\le N.}
\tag{21}
\]
**证明。** 在第零步两轨迹相同；若第 i 步状态和历史相同，则冻结矩阵恰由该名义点生成，输入也等于名义输入，所以下一步 z 更新及两个历史移位完全相同。归纳。证毕。

### 引理 3：参考尾输入的终端下降（含参考缺陷）

令
\[
c_S:=1+\|S^{1/2}E_{prev}\Pi^{-1/2}\|_2^2.
\tag{22}
\]
当 \(u=u_t^{ref}\) 时，历史上一输入偏差全部由 q 的误差表示，故
\(\ell_t(q,u_t^{ref})\le c_S\|q-q_t^{ref}\|_\Pi^2\)。

任选 \(\vartheta>0\) 满足 \((1+\vartheta)\lambda^2<1\)，并选择
\[
\boxed{\beta\ge\frac{c_S}{1-(1+\vartheta)\lambda^2}.}
\tag{23}
\]
则对任意 \(q\in\mathcal Q\) 及绝对时间 t，
\[
\begin{aligned}
&\ell_t(q,u_t^{ref})
+\beta\|F(q,u_t^{ref})-q_{t+1}^{ref}\|_\Pi^2\\
&\hspace{28mm}-\beta\|q-q_t^{ref}\|_\Pi^2
\le \underbrace{\beta(1+1/\vartheta)\bar d_{ref}^2}_{=:\tau_{ref}}.
\end{aligned}
\tag{24}
\]
**证明。** 将下一误差拆为
\(F(q,u^{ref})-F(q_t^{ref},u^{ref})+[F(q_t^{ref},u^{ref})-q_{t+1}^{ref}]\)，按 (9)、(5) 和 Young 不等式，平方上界为 \((1+\vartheta)\lambda^2\|e\|_\Pi^2+(1+1/\vartheta)\bar d_{ref}^2\)。代入 (22)、(23) 消去二次项。证毕。

**备注。** 对精确模型轨道 \(\bar d_{ref}=0\)，可以直接取 \(\beta\ge c_S/(1-\lambda^2)\)，没有参考扰动项。实际在线 QP 仍然只使用一个固定的二次终端成本，并不在线执行终端反馈；理论续接输入为时变参考输入。

## 5. 主引理：实际 Frozen QP 最优值的跨采样下降

**引理 4（直接 Frozen 值函数下降）。** 满足 §1–§3 与引理 3，QP 每次精确求全局最优。记
\(e_k=q_k^E-q_k^{ref}\)，并取同一紧域上的常数 \(L_\ell,L_f\)，使对相同绝对时间与相同输入，
\[
|\ell_t(q,u)-\ell_t(\tilde q,u)|\le L_\ell\|q-\tilde q\|_\Pi,
\quad |V_{f,t}(q)-V_{f,t}(\tilde q)|\le L_f\|q-\tilde q\|_\Pi.
\tag{25}
\]
其中 \(V_{f,t}(q)=\beta\|q-q_t^{ref}\|_\Pi^2\)，可取 \(L_f=4\beta M\)。定义
\[
 H_S:=S^{1/2}E_{prev}\Pi^{-1/2},\quad
 D_u^S:=\sup_{u,v\in\mathcal U}\|S^{1/2}(u-v)\|_2,\quad
 T_\Delta:=D_u^S+2M\|H_S\|_2.
\]
由于阶段跟踪向量 \(q-q_t^{ref}\) 的 \(\Pi\) 范数至多 \(2M\)，以及在相同绝对时间、相同输入条件下 \(R\) 项抵消，**可以显式取**
\[
 \boxed{L_\ell=4M+2T_\Delta\|H_S\|_2,\qquad L_f=4\beta M.}\tag{25a}
\]
此界的第二项来自相对参考输入增量，其与上一输入缓存相关的差异已计入 \(H_S\)。这些系数**不对应原论文的绝对输入增量代价**；若恢复原代价，须重新计算。定义
\[
d_j=\lambda^j\bar w+\bar\eta\sum_{s=0}^{j-1}\lambda^s,
\quad j=0,\ldots,N-1
\quad(\text{空和}=0),
\tag{26}
\]
\[
\boxed{\varepsilon
=\tau_{ref}+L_\ell\sum_{j=0}^{N-1}d_j
+L_f\lambda d_{N-1}.}
\tag{27}
\]
则
\[
\boxed{W_{k+1}-W_k
\le-\ell_k(q_k^E,u_{0|k}^*)+\varepsilon
\le-\|e_k\|_\Pi^2+\varepsilon.}
\tag{28}
\]

**完整证明。** 固定 k，令旧 Frozen 最优输入 \(U^*=(u_0^*,\ldots,u_{N-1}^*)\)，旧 Frozen 增广轨迹 \(p_0,\ldots,p_N\)，故 \(W_k=J_k^{fr}(U^*;\bar U_k)\)。实际下一重新编码初值满足
\[
q_{k+1}^E=F(q_k^E,u_0^*)+w_k=p_1+w_k.
\tag{29}
\]
构造下一名义/候选序列 \(U^+=(u_1^*,\ldots,u_{N-1}^*,u_{k+N}^{ref})\)。记从 (29) 用 **full F** 沿此序列生成的轨迹为 \(\tilde q_0,\ldots,\tilde q_N\)，其中 \(\tilde q_0=q_{k+1}^E\)。由于下一名义序列恰为 \(U^+\)，由引理 2，**新 Frozen 在该候选上的轨迹正好是 \(\tilde q\)**。

比较其前 N 个点与旧 Frozen 移位点。由 (29)，\(\|\tilde q_0-p_1\|_\Pi\le\bar w=d_0\)。对 \(j=0,\ldots,N-2\)，旧 Frozen \(p_{j+2}=F_{j+1|k}^{fr}(p_{j+1},u_{j+1}^*)\)，新 full \(\tilde q_{j+1}=F(\tilde q_j,u_{j+1}^*)\)，从 (9)、(12) 得
\[
\|\tilde q_{j+1}-p_{j+2}\|_\Pi
\le\lambda\|\tilde q_j-p_{j+1}\|_\Pi+\bar\eta,
\]
故对 \(j=0,\ldots,N-1\)：
\[
\|\tilde q_j-p_{j+1}\|_\Pi\le d_j.
\tag{30}
\]
在尾步使用相同的**参考尾输入**，置 \(p_{N+1}^{aux}=F(p_N,u_{k+N}^{ref})\)，则
\[
\|\tilde q_N-p_{N+1}^{aux}\|_\Pi\le\lambda d_{N-1}.
\tag{31}
\]
(30) 和 (31) 不需要计算旧最优序列的第二次 full rollout；它们只用于理论比较。

由于新输入候选全在 \(\mathcal U\)，新 QP 非空、且其最优值不超过该候选代价。利用 B-EXACT、(25)、(30)、(31) 和绝对时间对齐，有
\[
\begin{aligned}
W_{k+1}\le{}&J_{k+1}^{fr}(U^+;U^+)\\
={}&J_{k+1}^{full}(q_{k+1}^E,U^+)\\
\le{}&\sum_{i=1}^{N-1}\ell_{k+i}(p_i,u_i^*)
+\ell_{k+N}(p_N,u_{k+N}^{ref})\\
&+\beta\|F(p_N,u_{k+N}^{ref})-q_{k+N+1}^{ref}\|_\Pi^2\\
&+L_\ell\sum_{j=0}^{N-1}d_j+L_f\lambda d_{N-1}.
\end{aligned}
\tag{32}
\]
(32) 中的阶段输入及绝对时间对应一致。**不能在一般扰动模型 (2) 下无条件声称新旧上一输入缓存严格相同**；它们的差异作为增广状态差统一由 (25) 控制。若附加 \(w_k=\operatorname{col}(r_k,0,0)\)，则缓存块在相同输入移位下确实一致。用 (24) 在 \(p_N\) 处消去追加阶段成本与终端成本，得到
\[
W_{k+1}\le\sum_{i=1}^{N-1}\ell_{k+i}(p_i,u_i^*)
+\beta\|p_N-q_{k+N}^{ref}\|_\Pi^2
+\varepsilon.
\]
与旧 \(W_k\) 比较恰好删除 \(\ell_k(p_0,u_0^*)\)，故 (28) 成立。证毕。

**说明：** 此证明没有比较 Frozen 解与 full 非凸 MPC 的最优值，因此**根本不需要**原 B1 的 \(\varepsilon_{set}\) 或“共同终端可行集合”。代价是新模型类具备 C1/C2 收缩且仅有输入硬约束。对于非零优化器次优性 \(\eta_{solver,k}\)，上述最后一行可以额外加入它的统一上界；此时须明确求解器的可行输出和次优值定义。

## 6. 主定理：测量增广状态的条件实际指数跟踪 / 最终有界性

为避免一个容易被忽略的漏洞，仅有 (28) 还不足以推出逐时刻最终有界；需要给 \(W_k\) 建立两边比较界。这里上界也能显式构造，而不假设价值函数正定/连续。

对所有 \(i\ge0\) 令
\[
S_i^\lambda=\sum_{s=0}^{i-1}\lambda^s,\qquad
b_i=\bar d_{ref}S_i^\lambda+D_i,
\tag{33}
\]
\(D_i\) 由 (20) 给出。定义可显式计算的统一常数
\[
\boxed{\begin{aligned}
A&=2\Big(\sum_{i=0}^{N-1}\lambda^{2i}+\beta\lambda^{2N}\Big)
+\|S^{1/2}E_{prev}\Pi^{-1/2}\|_2^2,\\
B&=2\Big(\sum_{i=0}^{N-1}b_i^2+\beta b_N^2\Big),\\
\rho&=1-\frac1A\in[0,1).
\end{aligned}}
\tag{34}
\]
其中 \(A\ge2\)。

**引理 5（比较界）。** 在上述条件下，对于所有采样时刻和所有允许名义序列，
\[
\boxed{\|e_k\|_\Pi^2\le W_k\le A\|e_k\|_\Pi^2+B.}
\tag{35}
\]
**证明。** (6) 在第零步含有当前状态正定项，故每条候选代价不少于 \(\|e_k\|_\Pi^2\)，最小值亦如此。为得上界，使用可行的**整段参考输入** \(U^{ref}=(u_k^{ref},\ldots,u_{k+N-1}^{ref})\) 作候选。由 (9)、(5)，该输入下的 full 轨迹相对参考满足
\(\|q_i^{full}-q_{k+i}^{ref}\|_\Pi\le\lambda^i\|e_k\|_\Pi+\bar d_{ref}S_i^\lambda\)。再用引理 1 的 Frozen/full 差得
\(\|p_i^{fr}(U^{ref})-q_{k+i}^{ref}\|_\Pi\le\lambda^i\|e_k\|_\Pi+b_i\)。使用 \((a+b)^2\le2a^2+2b^2\) 处理每个阶段状态成本和终端成本。参考输入偏差为零；输入增量偏差在 \(i\ge1\) 时为零（本候选前一输入就是前一参考输入），第零步仅为初始上一输入历史偏差，大小不超过 \(\|S^{1/2}E_{prev}\Pi^{-1/2}\|^2\|e_k\|_\Pi^2\)。代入 (7) 得 (35)。证毕。

**定理 1（Frozen-QP 闭环实际指数跟踪）。** 设 (1)–(13)、(23) 成立，参考和初值满足共同域条件，在线严格执行 (3)、(4)、(7)，每步求解一次凸 QP 并精确执行其首输入，真实重新编码演化满足 (2)。则对所有 \(k\ge0\)，
\[
\boxed{\|q_k^E-q_k^{ref}\|_\Pi
\le\sqrt A\,\rho^{k/2}\|q_0^E-q_0^{ref}\|_\Pi
+\sqrt{B+A\varepsilon}.}
\tag{36}
\]
特别地，
\[
\boxed{\limsup_{k\to\infty}\|q_k^E-q_k^{ref}\|_\Pi
\le\sqrt{B+A\varepsilon}.}
\tag{37}
\]
如果 \(\bar\eta=\bar w=\bar d_{ref}=0\)，则 \(B=\varepsilon=0\)，跟踪误差指数收敛到零。对非零扰动，这是**条件实际指数稳定/最终有界**的明确半径，而不是无条件渐近稳定。

**证明。** 由引理 4 和 \(\ell_k\ge\|e_k\|_\Pi^2\)，
\[
W_{k+1}\le W_k-\|e_k\|_\Pi^2+\varepsilon.
\]
由 (35) 上界，\(\|e_k\|_\Pi^2\ge(W_k-B)/A\)，因此
\[
W_{k+1}\le\left(1-\frac1A\right)W_k+\frac BA+\varepsilon
=\rho W_k+(1-\rho)B+\varepsilon.
\]
迭代得
\[
W_k\le\rho^kW_0+(B+A\varepsilon)(1-\rho^k).
\]
再用 \(W_0\le A\|e_0\|_\Pi^2+B\) 与 \(\|e_k\|_\Pi^2\le W_k\)，得到
\[
\|e_k\|_\Pi^2\le A\rho^k\|e_0\|_\Pi^2+B+A\varepsilon(1-\rho^k),
\]
使用 \(\sqrt{x+y}\le\sqrt x+\sqrt y\) 得 (36)；取上极限得 (37)。证毕。

**测量跟踪结论。** \(x_k=C_xz_k\) 为 q 的线性投影，故
\[
\|x_k-x_k^{ref}\|_2
\le\|C_xE_z^\top\Pi^{-1/2}\|_2\,\|q_k^E-q_k^{ref}\|_\Pi.
\tag{38}
\]
这个证明针对**实际测量重新编码的闭环增广状态**，前提是实际采样确实满足统一残差 (2)。如果物理状态 \(s\) 未观测，不能仅由 (38) 推出 \(s\) 稳定。**输入跟踪补充推论。** 若 \(R\succ0\)，令 \(r_{\min}=\lambda_{\min}(R)>0\)，由最优首输入对应的阶段成本及上述平方界，
\[
 r_{\min}\|u_k^*-u_k^{ref}\|_2^2\le \ell_k(q_k^E,u_k^*)\le W_k,
\]
从而
\[
 \boxed{\|u_k^*-u_k^{ref}\|_2
 \le \sqrt{\frac{A\rho^k\|e_0\|_\Pi^2+B+A\varepsilon(1-\rho^k)}{r_{\min}}},\qquad
 \limsup_{k\to\infty}\|u_k^*-u_k^{ref}\|_2\le\sqrt{\frac{B+A\varepsilon}{r_{\min}}}.}\tag{38a}
\]
若 \(R\succeq0\) 非正定，则仅控制 \(R\) 加权误差，不能推断 \(R\) 的零空间方向上的欧氏输入误差。

## 7. 为什么这不是“把稳定性藏在假设里”

关键稳定性假设 C1/C2 的确较强，但它们**不是“假设 MPC 闭环稳定”或“假设最优值下降”**：它们只约束学习预测器的明确矩阵及导数，能够由 (14)–(18) 直接设计与检查；终端成本 β、Frozen/full 误差 \(\bar\eta\)、价值上下界 A/B、漂移余量 ε、最终半径均由显式公式构造。

对真实 plant 与学习模型之间的统一一步残差 (2) 则无法纯靠网络参数化证明，必须通过额外的系统假设、认证覆盖或物理机理给出。数学定理对任意满足该残差界的实际测量演化成立；**这就是控制论文所需且不能伪造的模型—plant 接口**。

## 8. 审查：限制、边界与可能的失败点

1. **适用对象限制：** 若真实系统包含无法被开环收缩预测器准确表示的不稳定开环动力学，强行选 \(A_0\) Schur、缩小调度增益可能使模型残差 \(\bar w\) 变大，以至 (37) 没有有效精度意义。此时需要返回带终端反馈的 B1，不能用一个较漂亮的定理取代模型真实性。
2. **共同域要求：** C1/C2/\(\bar w\) 都必须覆盖真实闭环、所有允许候选输入和所有冻结名义轨迹；(11) 提供域不变的归纳，但导数界与输入驱动界须在选定域上独立核查。
3. **参考真实性：** 模型可实现的动态参考可通过约束内参考输入生成；给定外部期望测量轨迹时只能在明确 \(\bar d_{ref}\) 和潜状态/缓存参考定义后使用。若参考不在编码图上，\(\bar w\) 或参考缺陷项一般会产生不可消除的实际误差下界。
4. **误差界保守：** (13) 用全域 \(2g_A,2g_B\)，即使实际上最佳解接近名义，理论半径也可能保守；不能把该保守界的正值解释为实际误差必然非零。
5. **终端成本与输入增量：** 若保持原论文的**绝对输入增量**，时变参考处代价未必为零，上述 β/正定比较界需要重新证明；本主定理采用理论先行的新成本 (6)。
6. **未证当前实例：** 本文件不证明当前训练 checkpoint 满足 C1/C2/统一残差，也没有生成/验证与既有实验一致的新模型；这份证明是针对**拟议模型类和拟议 MPC**的完成定理，而不是当前项目的实验认证。
7. **凸性/计算：** 冻结以后 q 关于 U 仿射、目标凸二次、输入多面体；没有额外在线优化、终端 QCQP 或鲁棒 tube。这里不证明计算时间满足实时约束。
8. **非精确优化：** 上述证明默认为每步求得 QP 全局最优；凸 QP 的数值容差可按当前/下次值比较加入统一 \(\bar\eta_{solver}\)；实际求解可行性和容差需要单独说明。

## 9. 显式非平凡的历史调度模型实例：证明这个模型类不是空定义

选择历史长度 \(P_h=2\)，测量/输入均为标量，提升状态 \(z=(x,\gamma x_{k-1})\)，过去测量 \(a=x_{k-1}\)、过去输入 \(v=u_{k-1}\)，编码器
\[
G(X)=\operatorname{col}(x_k,\gamma x_{k-1}).
\]
取 \(|a_0|<1\)，\(b_0\ne0\)，\(\gamma\ne0\)，非零但足够小的 \(\epsilon_A,\epsilon_B\)，定义
\[
\begin{aligned}
c(q)&=a+v,\\
A(c)&=\begin{bmatrix}a_0+\epsilon_A\tanh(c)&0\\\gamma&0\end{bmatrix},\\
B(x)&=\begin{bmatrix}b_0+\epsilon_B\tanh(x)\\0\end{bmatrix}.
\end{aligned}
\tag{39}
\]
这是**非平凡历史条件的秩一 A 调度 + 当前测量依赖的 B 调度**；完整递推在测量层是
\[
x_{k+1}=(a_0+\epsilon_A\tanh(x_{k-1}+u_{k-1}))x_k
+(b_0+\epsilon_B\tanh(x_k))u_k.
\tag{40}
\]
并有 \(z_{latent,k+1}=\gamma x_k\)、\(a_{k+1}=x_k\)、\(v_{k+1}=u_k\)。因此从编码图出发，**完整模型严格保持编码一致性**（无扰动时 \(\bar w=0\)）；加入幅度有界的真实测量转移噪声，\(w=\operatorname{col}(\nu,0,0,0)\)，其 \(\Pi\) 范数有明确上界。

当 \(\epsilon_A=\epsilon_B=0\)，完整增广骨架 (14) 的特征值为 \(a_0\) 和其余零，故可由 (15) 计算 \(\Pi\)。在任一**预先固定**的有界球与有界输入集合上，\(DF-M_0\) 连续地随 \(\epsilon_A,\epsilon_B\to0\) 趋零。更严格的联合构造次序如下。

1. 固定非空紧输入集 \(\mathcal U\)（为下述两周期示例，额外要求 \(0\in\operatorname{int}\mathcal U\)）、固定噪声残差上界 \(\bar w\)、固定 Schur 骨架 \(M_0\)、其 Lyapunov 矩阵 \(\Pi\) 与 \(\lambda_0<1\)。令零调度驱动上界为 \(b_{\mathrm{drv},0}\)。
2. **先**选择 \(M\) 包含所需真实初值和参考集合，且具有严格余量
\[
 \Delta:=(1-\lambda_0)M-b_{\mathrm{drv},0}-\bar w>0.\tag{41}
\]
3. **固定这个 \(M\)**，然后取足够小、但不为零的 \(\epsilon_A,\epsilon_B\)。设由调度造成的完整／Frozen 收缩率增量为 \(\delta_\lambda,\delta_{\lambda,fr}\)，驱动界增量为 \(\delta_b\)，要求
\[
 \delta_\lambda M+\delta_b<\Delta,\qquad
 \delta_{\lambda,fr}M+\delta_b<\Delta,\tag{42}
\]
并要求 \(\lambda_0+\delta_\lambda<1\)、\(\lambda_0+\delta_{\lambda,fr}<1\)。由于固定紧球上的导数与驱动对调度增益连续，此类严格选择在上述零调度余量为正的条件下存在。

因此不是先假设 \(\mathcal Q\) 不变再选择参数，而是利用 (41)–(42) **联合构造并验证** (11)。这只证明示例模型类非空；对一般拟训练模型，\(\bar w\) 可能随网络约束改变，不能被视为任意独立固定的小参数。

**明确的非恒定两周期参考。** 进一步取 \(0\in\operatorname{int}\mathcal U\)，选择足够小的非零 \(h\)，令 \(u_t^{ref}=h(-1)^t\)。由统一收缩性与周期输入，二步组合映射在紧不变球内存在唯一两周期轨道（Banach 不动点定理）。在 \(h=0\) 的原点附近，调度项在一阶近似中消失，测量线性化为 \(x_{t+1}=a_0x_t+b_0u_t\)，故
\[
 x_t^{ref}= -\frac{b_0}{1+a_0}h(-1)^t+o(h).\tag{43}
\]
由于 \(|a_0|<1\)、\(b_0\ne0\)，充分小但非零的 \(h\) 确保该参考测量轨道并非常值。又因为模型满足 \(z_{\mathrm{latent},t+1}=\gamma x_t\)、\(a_{t+1}=x_t\)，周期模型轨道满足编码图关系 \(z_{\mathrm{latent},t}=\gamma a_t\)，即与所选**解析延迟编码器**精确兼容。这个构造不能证明任意 Transformer encoder 具有相同不变性；对实际学习编码器须另给残差或近似证书。此实例只证明**理论模型类非空**，不证明现有训练数据对应的物理平台满足该类模型。

## 10. 原论文、先前 B1 与新收缩路线的三方区分

| 设计维度 | 当前 Main.tex 原控制器 | 先前 B1 拟议设计（研究性） | 本次新收缩路线（研究性 V2） |
|---|---|---|---|
| 输入硬约束 | 多面体输入约束 | 保留输入，拟新增阶段工作域与终端硬面 | **仅输入**，不新增终端硬面 |
| 模型条件 | 历史条件低秩调度，未保证收缩 | 局部可稳定化 + 鲁棒终端反馈/集合 | 完整模型及所有冻结映射在公共范数下同输入收缩 |
| 阶段成本 | 测量跟踪 + 输入参考 + **绝对输入增量** | 曾拟保留原绝对输入增量语义 | **完整增广正定** + **相对参考增量** |
| 终端成本 | 测量终端二次项 | 拟议终端二次/多面体 | \(\beta\Pi\) 完整增广终端成本 |
| 终端续接 | 无正式设计 | Frozen 终端估计上的局部反馈 | 直接使用下一参考输入 \(K=0\) |
| 名义更新 | 原论文尚保留实现选择 | 研究中指定 shift-tail | 强制用已解移位 + 参考 tail |
| 递归可行性 | 输入非空即可保证原 QP 非空 | 需终端鲁棒性与跨采样移位证书 | 输入非空即可保证**修改版无状态硬约束** QP 非空 |
| 证明对象 | 有限时域预测与成本比较 | 带终端收紧的条件递归可行性 | 修改版 Frozen-QP 的直接最优值下降与最终有界性 |

V2 是**并行的独立候选路线**，不是 B1 已失败的证明，不得将 B1 的拟议阶段/终端硬面误写成原论文已实现约束。上述改动都属于理论设计建议，不表示已获许可修改 Main.tex、训练或控制器。

## 11. 论文级写作建议和接下来的最小验证清单

建议将理论章节重组为：

1. **Model design and regularity:** 非重复增广 F、统一收缩与历史调度低秩的可验证设计条件；
2. **Prediction and encoder residual:** 保留现有有限时域预测误差，独立引入统一一步真实重新编码残差；
3. **Frozen-LTV MPC:** 改用全增广/相对增量成本，终端 βΠ，仍为一次凸 QP；
4. **Finite-horizon freezing lemma:** 引理 1、2；
5. **Recursive feasibility and terminal decrease:** 输入可行集合 + 引理 3；
6. **Direct frozen value decrease:** 引理 4；
7. **Conditional robust practical exponential tracking:** 引理 5 与定理 1；
8. **Limitations:** 开环收缩模型类限制、实际 plant 残差条件、模型参数/实际实现未认证。

下一步不应再发散探索十余个 B1 分支，而应要求独立 reviewer 对本文**所有量词、参考时移、输入增量、全域一致性和数值因子**逐项复核。之后再决定把这套新模型/成本规定写回 \(Main.tex\)。如要证明现有具体学习模型符合它，仍需固定模型参数和可认证的 uniform residual 证据。

---

### V2 修订完成后的精确状态与仍需闭合的接口

**数学结论（本文件范围内）：** 在非空紧输入多面体、固定绝对时间参考、一致性增广状态、统一 C1/C2/C3/C4、公域不变、统一测量重编码残差、参考缺陷、精确可行 QP 求解和强制 shift-reference-tail 更新这些明确前提下，引理 1–5 与定理 1 的**条件性证明链保持成立**。外部审查给出的评语为 `CONDITIONAL GO`，V2 仅对其修补建议作解析整合，不代替一次新的独立复核。

**结构性可构造性：** Schur 骨架 + Lyapunov 矩阵 + 显式 \(\nu_{\mathrm{bd}}\) + 联合半径预算 (41)–(42) 形成可检查的模型设计方法；§9 的非零历史调度示例和显式两周期参考证明抽象模型类并非空定义。它**不**意味着当前 Transformer、其他实验平台或训练模型已经满足这些条件。

**仍需区别的三件事：**
1. 条件定理可在研究稿内部陈述为“理论闭合”，但实际模型/训练/编码器及其全域误差界没有被认证；
2. 论文原始控制器与新设计控制器不同，尚未获得改写/实施授权；
3. 统一的物理测量残差是把学习预测器连接到真实实验数据的独立证据，不能由训练平均误差或模型结构自动推出。未观测物理状态稳定性仍不在定理结论内。

**特别声明：** 即使得到 \(\bar\eta,\bar w,\bar d_{ref}\) 对应的有限最终半径，若半径大于任务要求的跟踪容差，则仍不构成有实际意义的性能保证；设计阶段必须评估证书的保守性和模型精度损失。

---

### 来源/标注边界

**直接核对的原始来源：** 用户上传的 `B1_Original_Materials_Combined_for_GPT_20261018.md` 中六份原文，尤其 `Main.tex` 的历史输入、QP 及原始成本，Agent 的 `Integrated_Certificate_Map`、`Joint_Safety_Shift_Certificate`、`Joint_Residual_Radius_Budget`、`Explicit_Dynamics_Jacobian_Derivation` 和 `Direct_Encoded_Defect_Certificate`。此前 B1 的数学事实与本次**新设计建议**已在文内明确区分。本次没有读取 checkpoint、运行实验、改写现有论文或者修改控制代码。
