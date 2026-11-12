# 第五阶段理论研究：冻结 LTV-QP 的闭环灵敏度与动态参考跟踪证书

**日期：2026-11-11**  
**状态：严格的条件性理论推导 / 待真实网络参数认证；非最终论文正文。**  
**依据：**`Main9_Stage3_IEEE_Polished.tex` 第三章、Stage 1–4 研究报告、Baseline v2.4。  
**研究边界：**真实目标为动态物理轨迹跟踪；第三章的历史调度 Transformer–Koopman 预测器不可偷换为普通 Koopman 模型；跟踪权重固定为 `Q=diag(Q_x,0)`，`Q_x≻0`；MPC 在线直接优化输入；本阶段不改论文、不做实验。

> **本阶段的新增贡献：**建立了一个**直接针对实际冻结 LTV-QP 首输入反馈**的闭环历史灵敏度证书。利用强凸 QP 在**固定、非空凸输入可行域**上的变分不等式，得到控制输入对测量历史的全局 Lipschitz 界，**不要求活跃约束集合固定或求解器可微**。将其代入第三章**完整非线性历史调度模型的真实第一步**，导出动态参考下的窗口型 ISS / 实用指数跟踪界。该路线不以模型开环收缩率必须足够小为前提，可以与第三章已有收缩性理论并行使用。更紧的局部 KKT 雅可比公式给出后续实际可认证的研究方向。

## 1. 研究问题与精确的被分析闭环

令历史长度 `P=P_h≥2`，当前测量窗口与已施加输入缓存分别为

\[
X_k=\operatorname{col}(x_{k-P+1},\ldots,x_k),\qquad
v_k=\operatorname{col}(u_{k-P+1},\ldots,u_{k-1}).
\]

第三章模型严格使用

\[
z_k^E=G_\theta(X_k)=\operatorname{col}(x_k,\psi_\theta(X_k)),\quad C_x=[I_n\;0],\quad
q_k^E=\operatorname{col}(z_k^E,a(X_k),v_k),
\]

\[
F(q,u)=\operatorname{col}\big(A(c(q))z+B(C_xz)u,\; S_xa+E_xC_xz,\;S_uv+E_uu\big),
\]

\[
q_{k+1}^E=F(q_k^E,u_k)+w_k,
\qquad w_k=\operatorname{col}(w_k^z,0,0).
\]

参考轨迹 `x_j^r` 给出窗口 `X_k^r`、未来预览 `r_k=(x_{k+1}^r,...,x_{k+N}^r)`。参考升维 `z_j^r=G_\theta(X_j^r)` 可以构造，**但因 `Q=diag(Q_x,0)`，QP 的参考项代数上仅依赖物理 `x_j^r`**。

控制器在采样时刻获得 `X_k,v_k`，选定一个**已知且本次冻结不变**的输入标称种子 `\bar U_k∈\mathcal U^N`（例如上一时刻最优序列移位），使用第三章 `F` **完整递推一次**生成冻结系数 `\bar A_{i|k},\bar B_{i|k}`，然后优化

\[
\min_{U∈\mathcal K=\mathcal U^N}
J_k(U;X_k,v_k,\bar U_k,r_k)
=\sum_{i=1}^N\|z_{i|k}-z_{k+i}^r\|_Q^2+J_{\rm control}(U),
\]

\[
z_{0|k}=G_\theta(X_k),\qquad
z_{i+1|k}=\bar A_{i|k}z_{i|k}+\bar B_{i|k}u_{i|k}.
\]

**本报告的灵敏度比较固定相同的 `v_k`、`\bar U_k` 和 `r_k`，只改变被编码的测量窗口 `X`。** 这与实际算法一致：在采样 `k` 时，输入历史和本次标称种子已确定；对一个假想测量窗口计算同一算法的输出时，应保持其他采样参数不变。若将来把标称种子设计为当前 `X` 的函数，则必须把 `D_X\bar U` 纳入灵敏度分析，不能直接套用本报告。

## 2. 完整模型的一步闭环映射：不再只分析开环预测收缩

对固定的采样参数 `\vartheta_k=(v_k,\bar U_k,r_k)`，用符号

\[
\pi_k(X;\vartheta_k)=e_0^\top U_k^\star(X;\vartheta_k)
\]

表示冻结 QP 返回的第一个最优输入，其中 `e_0^\top=[I_m\;0\;\cdots\;0]`。定义**完整模型首步输出映射**

\[
\boxed{
\mathcal T_k(X;\vartheta_k)
=C_x\left[A(c(q^E(X,v_k)))G_\theta(X)
+B(C_xG_\theta(X))\pi_k(X;\vartheta_k)\right].
}\tag{S5.1}
\]

注意此处 `A,B` 来自第三章**非线性完整模型**；使用 QP 首输入，但**并没有把真实被控对象改成冻结 LTV 预测器**。因为冻结第一步系数来自同一 `q_k^E`，实际闭环严格满足

\[
\boxed{x_{k+1}=\mathcal T_k(X_k;\vartheta_k)+e_{k}^{\rm model},\qquad
e_k^{\rm model}=C_xw_k^z.}\tag{S5.2}
\]

目标：直接计算/约束 `\mathcal T_k` 关于 `X` 的灵敏度，而不是只要求 `F` 开环具有极小的全维收缩常数。

## 3. 可证明的 QP 输入灵敏度：允许约束活跃集切换

### 3.1 Condensed QP 及数学条件

每个冻结预测器都有已知矩阵 `\mathscr T(X),\mathscr S(X)`：

\[
Z=\mathscr T(X)G_\theta(X)+\mathscr S(X)U,
\quad Z=\operatorname{col}(z_1,\ldots,z_N).
\]

例如，采用**候选**输入增量成本 `J_control=\|\mathcal DU-d(v_k)\|_{\mathbf S}^2`、`\mathbf S\succ0`，且 `\mathbf Q=I_N\otimes Q`，得到

\[
J_k(U;X)=\tfrac12 U^\top H_k(X)U+h_k(X)^\top U+c_k(X),
\]

\[
\boxed{H_k(X)=2\big[\mathscr S(X)^\top\mathbf Q\mathscr S(X)+\mathcal D^\top\mathbf S\mathcal D\big],}\tag{S5.3}
\]

\[
\boxed{h_k(X)=2\big[\mathscr S(X)^\top\mathbf Q(\mathscr T(X)G_\theta(X)-Z_k^r)-\mathcal D^\top\mathbf S d(v_k)\big].}\tag{S5.4}
\]

`\mathcal D` 为单位对角的输入差分矩阵，可逆。这里选择 `\Delta u` 只是证明强凸性的便利例子；若选输入幅值惩罚或组合惩罚，只需令其在决策变量空间提供统一正定 Hessian。**控制正则项尚未最终选定。**

在与测量及参考有关的紧致分析域中，设满足：

- **H1.** `\mathcal K=\mathcal U^N` 为**固定**、非空、紧致、凸的输入集合，所有比较 `X` 的可行集合一致；本阶段没有额外的状态依赖约束。
- **H2.** `H_k(X)\succeq\mu I` 对所有被考虑的 `k,X` 成立，某个 `\mu>0`。例如 `\mu\ge2\lambda_{\min}(\mathcal D^\top\mathbf S\mathcal D)>0`。
- **H3.** 在历史窗口范数 `\|\Delta X\|_{\rm hist}=\max_{0\le j<P}\|\Delta x_j\|_{Q_x}` 下，
  \[
  \|H_k(X)-H_k(X')\|_2\le L_H\|X-X'\|_{\rm hist},\quad
  \|h_k(X)-h_k(X')\|_2\le L_h\|X-X'\|_{\rm hist}.
  \]
  常数必须对相关参考预览、输入历史和标称种子统一成立（或在明确的局部区间内成立）。
- **H4.** `M_U:=\max_{U∈\mathcal K}\|U\|_2<\infty`。若 `G_\theta`、调度网络及完整标称展开在紧致域上连续可微且导数有界，则 H3 可从第三章的实际模型链式求导获得，而不需要人为假设 QP 系数不受测量影响。

### 3.2 引理：强凸参数 QP 的输入 Lipschitz 界

**引理 5.1（固定凸输入集合下，QP 首输入连续性）。** 在 H1–H4 下，唯一最优解 `U_k^\star(X)` 对历史测量满足

\[
\boxed{
\|U_k^\star(X)-U_k^\star(X')\|_2
\le L_\pi\|X-X'\|_{\rm hist},\qquad
L_\pi=\frac{L_HM_U+L_h}{\mu}.}\tag{S5.5}
\]

此结论**允许最优解的活跃输入约束发生切换**，并不要求 `U^\star` 处处可微或其活跃集局部恒定。

**证明。** 最优性条件是 `0∈H(X)U+h(X)+N_{\mathcal K}(U)`。记两组参数最优解为 `U,U'`，法锥的单调性给出

\[
\langle H(X)(U-U'),U-U'\rangle
\le \left\langle [H(X')-H(X)]U'+h(X')-h(X),\;U-U'\right\rangle.
\]

左侧不小于 `\mu\|U-U'\|_2^2`，右侧不大于 `(L_HM_U+L_h)\|X-X'\|_{\rm hist}\|U-U'\|_2`。约去非零项即得；两个解相同的情况自明。□

**限制：**如果将来引入随 `X` 改变的状态/终端约束，上述固定可行集论证不再直接适用；如果只有半正定 Hessian，则唯一最优解和该界亦未自动成立。

## 4. 从第三章完整模型导出可检验的闭环 Lipschitz 常数

固定 `u` 定义完整模型一步物理读出

\[
\phi(X,u;v)=C_x\big[A(c(q^E(X,v)))G_\theta(X)
+B(C_xG_\theta(X))u\big].
\]

在考察域上令

\[
\boxed{\|\phi(X,u;v)-\phi(X',u;v)\|_{Q_x}
\le L_x\|X-X'\|_{\rm hist},\ \forall u∈\mathcal U,}\tag{S5.6}
\]

\[
\boxed{\|\phi(X,u;v)-\phi(X,u';v)\|_{Q_x}
\le L_u\|u-u'\|_2,\qquad
L_u\le \sup_X\|Q_x^{1/2}C_xB(C_xG_\theta(X))\|_2.}\tag{S5.7}
\]

组合 (S5.1)、(S5.5)–(S5.7) 得到**控制器感知的闭环增益**

\[
\boxed{
\|\mathcal T_k(X;\vartheta)-\mathcal T_k(X';\vartheta)\|_{Q_x}
\le \rho_{\rm cl}\|X-X'\|_{\rm hist},\qquad
\rho_{\rm cl}:=L_x+L_u\frac{L_HM_U+L_h}{\mu}.}\tag{S5.8}
\]

**注意：**(S5.8) 是严格的*充分上界*，但三角不等式可能忽略 MPC 反馈恰好抵消开环灵敏度的作用，因此可能仍偏保守。第 6 节给出更紧的局部闭环雅可比计算式。即使 (S5.8) 不小于 1，**也不能据此断言 MPC 不稳定**。

## 5. 主定理：实际动态参考下的窗口型实用指数跟踪

以下定义参考窗口 `X_k^r`，输入历史 `v_k`、标称种子 `\bar U_k` 与未来预览 `r_k` 均取该采样时刻的**真实已知值**；在与真实窗口比较时保持这些量相同。

定义对应参考窗口的**闭环一步偏差**

\[
\boxed{b_k:=\|\mathcal T_k(X_k^r;v_k,\bar U_k,r_k)-x_{k+1}^r\|_{Q_x}.}\tag{S5.9}
\]

`b_k` 衡量“采用同一控制器及实际输入记忆，在参考历史窗口上是否能够给出下一步期望输出”，不是从一条预先给定的参考输入中计算的量。它可能因为参考轨迹不可达、控制正则项和输入历史、冻结近似、控制约束或模型偏差而不为零。**这不是 MPC 在线算法需要额外计算的输入；在证明或离线证书中可以评估。**

定义 `E_k=\|x_k-x_k^r\|_{Q_x}`，`H_k=\max_{0\le j<P}E_{k-j}` 和 `\omega_k=\|C_xw_k^z\|_{Q_x}`。

**定理 5.2（冻结 LTV-QP 的闭环灵敏度充分条件）。** 假设 H1–H4、(S5.6)–(S5.7) 在每个真实窗口 `X_k` 与参考窗口 `X_k^r` 的线段上以及相应完整标称预测域内成立，QP 每个采样精确求得唯一最优解，并且

\[
\rho_{\rm cl}<1,\qquad b_k\le\bar b<\infty,\qquad\omega_k\le\bar\omega<\infty.
\]

则**实际实施**的动态参考跟踪闭环满足

\[
\boxed{E_{k+1}\le\rho_{\rm cl}H_k+b_k+\omega_k,}\tag{S5.10}
\]

并且令 `B=(\bar b+\bar\omega)/(1-\rho_{\rm cl})`，有

\[
\boxed{H_k\le B+\rho_{\rm cl}^{\lfloor k/P\rfloor}(H_0-B)_+,\qquad k\ge0.}\tag{S5.11}
\]

如果在所有被考虑的时刻 `b_k=0` 且 `\omega_k=0`，则 `H_k\le\rho_{\rm cl}^{\lfloor k/P\rfloor}H_0`，从而物理跟踪误差指数趋于零。**但对持续变化的参考，不能默认 `b_k=0`，尤其是存在输入正则化与过去输入历史时。**

**证明。** 由 (S5.2) 和三角不等式，

\[
\begin{aligned}
E_{k+1}
&\le\|\mathcal T_k(X_k;\vartheta_k)-\mathcal T_k(X_k^r;\vartheta_k)\|_{Q_x}\\
&\quad+\|\mathcal T_k(X_k^r;\vartheta_k)-x_{k+1}^r\|_{Q_x}+\omega_k\\
&\le\rho_{\rm cl}H_k+b_k+\omega_k.
\end{aligned}
\]

设 `b=\bar b+\bar\omega` 和 `B=b/(1-\rho_{\rm cl})`。当历史窗口中的误差大于 `B` 时，下一步误差至多为 `B+\rho_{\rm cl}(H_k-B)`；该上界在随后不超过 `P` 步的窗口移位中保持，直到原来的 `P` 个误差全部移出。因此

\[
H_{k+P}\le B+\rho_{\rm cl}(H_k-B)_+,
\]

在中间步有 `H_{k+1}\le\max\{H_k,B\}`。按每 `P` 步递推即得 (S5.11)。□

**若使用数值求解器：**上定理针对**精确最优解**；如果实际输入与最优首输入的偏差为 `\|\widehat u_{0|k}-u_{0|k}^\star\|_2\le\epsilon_{u,k}`，则右端另加 `L_u\epsilon_{u,k}`。如只有 QP 目标次优性差 `\delta_k`，在 `H\succeq\mu I` 和凸可行域下可用 `\|\widehat U-U^\star\|_2\le\sqrt{2\delta_k/\mu}`，因此增加 `L_u\sqrt{2\delta_k/\mu}`。这与 Stage 4 中利用总目标值的 `\sqrt\delta_k` 传播方式不同，条件需分别解释。

### 5.1 此定理与 Stage 4 的关系

| 对比 | Stage 4：标称比较输入代价 | Stage 5：实际控制律闭环灵敏度 |
|---|---|---|
| 主要对象 | 对某条可行标称输入的**整段预测代价** | **最优首输入反馈及其实际一步物理输出** |
| 收缩充分条件 | `\rho_N` 来自 `F` 的开环同输入收缩与历史编码增益 | `\rho_cl` 来自 QP 反馈灵敏度与 `F` 的一步读出 |
| 参考偏差项 | 多步参考动力学残差与标称输入成本 | `b_k`：参考窗口上的**闭环一步偏差** |
| 是否允许约束活跃集切换 | 允许 | 允许（全局强凸 QP 界），局部导数另行分区 |
| 是否需要先求 `u^r` | 不需要 | 不需要 |
| 可能的困难 | 多步代价和开环全维收缩率过于保守 | 全局 `L_x+L_uL_\pi` 可能忽略负反馈抵消，`b_k` 需要明确可检验上界 |

两条路线**互不排斥**；对每个阶段应选择条件更强、但更可检验且非空的一个，而非叠加成冗长的多个主定理。

## 6. 更紧的、真正包含反馈抵消的闭环雅可比

(S5.8) 中的 `L_x+L_uL_\pi` 将开环影响与控制修正影响的**方向全部取绝对值**，可能把实际上稳定的负反馈判断为“无法认证”。若 `G_\theta,C_\phi,\gamma_A,\gamma_B` 光滑、QP 活跃集局部固定且满足 LICQ（及通常的局部正规性），可通过隐函数/KKT 计算**实际** `D_X\mathcal T_k`。

### 6.1 第三章模型的真实雅可比：低秩调度不能漏掉

令 `x=C_xz`，`c=c(q)`，定义

\[
T_A(q):=U_A\operatorname{diag}(V_A^\top z)D_c\gamma_A(c),\qquad
T_B(q,u):=U_B\operatorname{diag}(V_B^\top u)D_x\gamma_B(x).
\]

记 `P_z=[I_d\;0\;0]` 与 `P_x=[C_x\;0\;0]`。则完整递归对状态的雅可比为

\[
\boxed{
D_qF(q,u)=
\begin{bmatrix}
A(c)P_z+T_A(q)D_qc(q)+T_B(q,u)P_x\\
E_xC_xP_z+S_xP_a\\
S_uP_v
\end{bmatrix}.}\tag{S5.12}
\]

`P_a,P_v` 为从 `q` 提取相应缓存的常数矩阵（第二、三块中未标注的零块隐含在此表达中）。特别地，**不能**错误地把 `D_qF` 写成单纯的 `A(c)`：`D_qc`、`D_c\gamma_A` 以及输入系数的 `D_x\gamma_B` 都对动态参考闭环灵敏度有贡献。

编码初始化的测量窗口导数

\[
R_X(X)=D_Xq^E(X,v)=\operatorname{col}\big(D_XG_\theta(X),P_a^{X},0\big),
\]

其中 `P_a^X` 选出窗口的前 `P-1` 个测量块，且 `C_xD_XG_\theta` 等于最后一个测量块的提取矩阵。对标称轨迹（固定 `\bar U`）的导数按链式法则递推：

\[
P_0=R_X(X),\qquad
\boxed{P_{i+1}=D_qF(\bar q_i,\bar u_i)P_i.}\tag{S5.13}
\]

从而可求出 `D_X\bar A_i`、`D_X\bar B_i`，再求出 `D_XH`、`D_Xh`。

### 6.2 KKT 灵敏度与闭环导数

在固定活跃集区域内，令活跃输入不等式写作 `C_AU=d_A`。站立性条件为

\[
H(X)U^\star+h(X)+C_A^\top\lambda_A=0,
\quad C_AU^\star=d_A.
\]

沿测量窗口变化方向微分，得到

\[
\boxed{
\begin{bmatrix}H&C_A^\top\\ C_A&0\end{bmatrix}
\begin{bmatrix}D_XU^\star\\D_X\lambda_A\end{bmatrix}
=-\begin{bmatrix}(D_XH)U^\star+D_Xh\\0\end{bmatrix}.}\tag{S5.14}
\]

在 LICQ 下 KKT 矩阵可逆。设 `\phi(X,u;v)` 为完整模型一步物理读出，则

\[
\boxed{
D_X\mathcal T_k
=D_X\phi(X,u;v)\big|_{u=\pi_k(X)}
+D_u\phi(X,u;v)\big|_{u=\pi_k(X)}\,e_0^\top D_XU^\star.}\tag{S5.15}
\]

式 (S5.15) **保留了 MPC 负反馈的符号及方向**，因而通常比 (S5.8) 更有希望得到 `\|D_X\mathcal T_k\|<1`。跨活跃集边界可用分区包络/广义雅可比及分段 Lipschitz 论证；只检查一个标称点的雅可比小于 1，**不构成**整个历史窗口或时间区间内的稳定性证明。

可采用范数

\[
\|D_X\mathcal T_k\|_{\rm hist\to Q_x}
:=\sup_{\|\Delta X\|_{\rm hist}\le1}\|D_X\mathcal T_k\Delta X\|_{Q_x}
\]

并在实际与参考窗口连线上取一致上界。若

\[
\sup_{k,\,t∈[0,1]}
\|D_X\mathcal T_k(X_k^r+t(X_k-X_k^r);\vartheta_k)\|_{\rm hist\to Q_x}
<1,
\]

同样可把该上界代入定理 5.2；需要对切换点采用适当的分段 Lipschitz / 几乎处处导数的积分解释。**这一步是下一阶段的主要认证目标，而不是本报告已完成的实际网络验证。**

## 7. 理论条件不是空集：一个可完全手算的两步示例

本例只作为数学结构的非空性核查，**不代表把第三章替换成线性 Koopman 模型，也不是机械臂实验**。

设一维模型 `x^+=a x+u`，`a=1.2>1`（开环不收缩），预测时域 `N=2`、无活跃输入约束，代价

\[
J=(x_1-r_1)^2+(x_2-r_2)^2+R(u_0^2+u_1^2),\quad R>0.
\]

将 `x_1=ax+u_0`、`x_2=ax_1+u_1` 代入并解析求解，得到**闭环第一步物理状态**

\[
\boxed{
\mathcal T(x;r_1,r_2)=
\frac{R(R+1)a\,x+R a\,r_2+(R+1)r_1}{(R+1)^2+R a^2}.}\tag{S5.16}
\]

因此

\[
\boxed{\frac{\partial\mathcal T}{\partial x}
=\frac{aR(R+1)}{(R+1)^2+Ra^2}.}\tag{S5.17}
\]

若取 `R=0.1`、`a=1.2`，则绝对灵敏度约 `0.09749<1`，**尽管开环 `a=1.2>1`**。对于一般动态参考，仍有偏差

\[
b_k=\left|\mathcal T(r_k;r_{k+1},r_{k+2})-r_{k+1}\right|,
\]

因此示例**只说明 MPC 反馈可能显著改善闭环收缩性**，不能借此宣称任意动态参考必定零误差。输入权重 `R` 越大，通常越不愿为快速参考运动施加大输入，偏差可能变大；这也支持继续保留正则项选择的研究自由度。

## 8. 认证步骤：如何从真实第三章网络得到最终可用的定理条件

1. **确认模型实现与定义一致：**编码历史 `G_\theta`、`C_\phi`、低秩因子、`\gamma_A,\gamma_B`、缓存移位与 `F`，以及输入约束 `\mathcal U`，不得只对简化 `z^+=Az+Bu` 认证。
2. **先确定真实 MPC 的控制正则项：**保证统一强凸模量 `\mu>0`；若不采用 `\Delta u`，则根据实际 Hessian 重新验证。
3. **确定闭环分析域：**参考轨迹类别、可能的历史误差半径、输入缓存与种子范围、编码初始化与完整标称展开保持有效的区域；必要时使用第三章现有不变域理论。
4. **计算完整递归雅可比：**用 (S5.12)–(S5.13) 取得 `D_X\bar A_i,D_X\bar B_i`，最终取得 QP 的 `H,h` 导数与统一下界 `\mu`。
5. **第一层（不依赖活跃集）：**认证 `L_x,L_u,L_H,L_h,M_U`；若 (S5.8) `\rho_cl<1`，则定理 5.2 直接适用。
6. **第二层（更紧）：**若第一层不通过，用 (S5.14)–(S5.15) 分区或使用广义雅可比认证真正的 `D_X\mathcal T`；需要**区间上界、区域覆盖和活跃集切换处理**，单点自动微分数值不够。
7. **参考匹配检验：**独立控制 `b_k` 的统一上界与实际重新编码误差 `\omega_k`；不能用“参考可编码”替代“参考可实现/闭环偏差小”的条件。
8. **核实非空性与精度：**误差邻域 `B=(\bar b+\bar\omega)/(1-\rho)` 必须与目标控制精度比较；若 `B` 很大，数学不等式即使正确也不应作为强性能结论。
9. **若仍无法认证：**转向增量可稳定性、可检测性或合理的终端设计；**不得重新引入旧的移动稳态点首输入护栏，只为套用旧收缩证明。**

## 9. 核心限制与本文定位

- **已经证明：**QP 强凸 + 固定凸输入集合 ⇒ 优化解对历史测量的 Lipschitz 界；可与第三章完整第一步组合成闭环灵敏度充分条件，进而严格得到动态参考的窗口型实用指数界。
- **尚未证明：**用户实际训练的 Transformer–Koopman 模型及机械臂轨迹满足 `\rho_cl<1`；参考偏差 `\bar b` 是否足够小；对所有约束活跃集和窗口是否能给出严格包络。
- **不主张：**只因论文写了新的定理，就认为实际闭环已获得参数化认证；也不主张一般动态参考总能零误差跟踪。
- **与第三章关系：**现有公共同输入收缩命题可以保留作为模型学习/不变域性质，但新的闭环定理不必从它推断强开环状态收缩；以真实控制器闭环为分析对象更适合机械系统。
- **与 Section V 关系：**仍然不引入任何实验数据；正文 Section V 继续保持空标题。

## 10. 参考文献与核对

1. Köhler, Müller and Allgöwer, **Nonlinear Reference Tracking: An Economic Model Predictive Control Perspective**, *IEEE Transactions on Automatic Control*, 64(1):254–269, 2019, DOI: 10.1109/TAC.2018.2800789. 研究一般动态参考的无人工参考/无终端项跟踪 MPC，在增量可稳定性等条件下给出跟踪保证。https://ieeexplore.ieee.org/document/8278210
2. Köhler, Müller and Allgöwer, **A Nonlinear Model Predictive Control Framework Using Reference Generic Terminal Ingredients**, *IEEE Transactions on Automatic Control*, 65(8):3576–3583, 2020, DOI: 10.1109/TAC.2019.2949350. 给出适用于一般可达参考轨迹的增量稳定性终端方案，若本报告的直接闭环小增益条件不可验证，可作为理论替代方向。https://arxiv.org/abs/1909.12765
3. Köhler, Müller and Allgöwer, **A Nonlinear Tracking Model Predictive Control Scheme for Dynamic Target Signals**, *Automatica*, 118 (2020), 109030, DOI: 10.1016/j.automatica.2020.109030. 强调动态参考与可达轨迹之间的区别。https://doi.org/10.1016/j.automatica.2020.109030

---

**本阶段结论：**比单纯用第三章开环收缩性约束比较代价更直接的路线，是把一次冻结 LTV-QP 当作真实闭环反馈映射的一部分，利用参数强凸 QP 的灵敏度推导历史窗口收缩。当前得到的是**具体、严格、可认证的充分条件与证明程序**，而不是对实际模型已认证成功的断言。后续是否能用于 IEEE 论文主定理，取决于在第三章实际网络及参考类别上能否验证闭环灵敏度、参考偏差和模型残差界。
