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
