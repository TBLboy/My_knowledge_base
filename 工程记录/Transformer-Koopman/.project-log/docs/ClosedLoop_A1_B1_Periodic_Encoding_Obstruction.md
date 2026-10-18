# B1：小周期参考的编码兼容障碍与一阶筛选

2026-10-18；TASK-B1-DERIV-20261018；strict结论级。纯解析，无论文/代码/控制器改动，无checkpoint或数值验证；不进入P5。
前置：Reduced_PBH_and_Periodic_Reference S4–S6，Encoding_Residual_and_Seed_Compatibility E6–E8，以及Joint_Residual_Radius_Budget B9–B13。

## P1. 基点编码间隙不会因小激励自动消失

在输入内点可稳定化平衡点(q*,u*)，取S4的辅助反馈K0，令A_c=F_q+F_u K0为Schur。固定周期T>=2及周期激励方向vbar_t；v_t=epsilon vbar_t。S5的隐函数分支给出q_t(epsilon)，q_t(0)=q*，定义

    h(q)=C_psi z-psi(col(a,C_xz)),
    sigma*=||h(q*)||, sigma_t(epsilon)=||h(q_t(epsilon))||.

假设psi在这些窗口上Lpsi-Lipschitz，Kh=sqrt(1+Lpsi²)。由E8的同一正交坐标证明，h在域内Kh-Lipschitz。若已认证

    max_{0<=t<T} ||q_t(epsilon)-q*|| <= M |epsilon|,

则对每个相位有

    sigma_t(epsilon) >= max(0,sigma*-Kh M |epsilon|).   (P1)

S5为C1分支时，在充分小紧参数区间上可取有限M为各相位导数范数的统一上界；它不是未知训练模型的已认证数值。
若sigma*>0，则足够小激励下所有相位仍有正间隙；令epsilon趋零不能令sigma_t趋零。这是连续性障碍，不是PBH失败，也不否定某个较大激励分支或其他平衡点可能编码兼容。

## P2. 对初始种子球与半径上限的排除证书

E8对任何处于同一认证窗口域的编码状态给出

    ||q^E-q_t(epsilon)|| >= sigma_t(epsilon)/Kh
                         >= sigma*/Kh-M|epsilon|.  (P2)

若J8给定可用欧氏初始球半径eta_seed，而右端>eta_seed，则该相位的种子球与域内编码像不交；这比只说参考不是编码状态更强。若证明需覆盖所有初始相位，P1统一下界可以同时排除全部相位。

在固定P、同输入传播界L>=1的B10内球种子分支中，给定终端半径上限r_cap，所认证xi还必须满足

    xi <= alpha r_cap/(||P^{1/2}|| L^N) =: xi_cap.

结合任何实际编码初值都要在xi球内，得到该分支的必要条件

    sigma*/Kh-M|epsilon| <= xi_cap.                 (P3)

若sigma*/Kh>xi_cap且M>0，则所有

    |epsilon| < (sigma*/Kh-xi_cap)/M

都不能通过这一域内、内球种子证书。M=0且sigma*/Kh>xi_cap时整条已认证常值分支均被排除。
这是J8/B10球证书不适用的充分排除条件，不是新增QP真实不可行，也不否定偏心/非球可行种子；r_cap本身也只需是当前证书的上限。

## P3. 零间隙基点的一阶兼容性

现在另取sigma*=0，并额外假设h可微、S5周期分支可微。令

    s_t = d q_t(epsilon)/d epsilon at 0,
    A=F_q(q*,u*), B=F_u(q*,u*), A_c=A+B K0.

微分S4给出唯一周期线性响应

    s_{t+1}=A_c s_t+B vbar_t, s_T=s_0,
    s_0=(I-A_c^T)^{-1} sum_{j=0}^{T-1} A_c^{T-1-j}B vbar_j. (P4)

上标T是周期次数幂，不是转置。Schur保证I-A_c^T可逆。按有限相位，

    h(q_t(epsilon))=epsilon Hh s_t+o(|epsilon|),
    Hh=Dh(q*).                                     (P5)

因此使所有相位编码间隙为o(|epsilon|)的必要且充分的一阶条件是

    Hh s_t=0 for t=0,...,T-1.                       (P6)

若某相位Hh s_t!=0，则该相位sigma_t/|epsilon|趋于||Hh s_t||>0。若F、h及隐函数分支具有连续二阶导，则满足P6可进一步给sigma_t=O(epsilon²)；在仅C1假设下只写o(|epsilon|)。P6不保证有限非零幅值上h恰为零，高阶项仍可使精确编码兼容失败。

## P4. 保留非恒定输出的一阶方向筛选

将所有周期激励堆为vbar∈R^{Tm}。P4定义线性响应算子R_t，使s_t=R_t vbar。定义

    Lenc=col(Hh R_0,...,Hh R_{T-1}),
    Lobs=col(Cobs(R_1-R_0),...,Cobs(R_{T-1}-R_0)).    (P7)

Cobs选择当前测量；Lobs不为零的响应即一阶周期观测不是常量，不要求最小周期恰为T。
存在同时满足一阶编码兼容、非恒定输出的方向，当且仅当

    ker Lenc is not a subset of ker Lobs,
    equivalently rank(col(Lenc,Lobs))>rank(Lenc).    (P8)

证明：存在vbar满足Lenc vbar=0但Lobs vbar!=0，正是核包含失败；核包含与Lobs行空间包含于Lenc行空间等价。该条件允许测试全部周期方向，若另限固定谐波/零均值/输入子空间vbar=Jv，则把两算子右乘J重新测试。
若P8失败，则不存在同时满足这两个一阶要求的方向；不排除输出只在二阶才非恒定，或容许一阶编码偏差的参考。因此不能把P8失败叫作所有非恒定周期参考不存在。
S6只保证某激励有非恒定输出，不包含Lenc=0条件；不能直接用S6证明编码兼容。P8同样不替代S2可稳定化与输入内点证书。

## P5. 精确编码周期轨道的额外方程

模型周期边界Psi_T(q0,v)-q0=0通过S5仅消去周期初值。若还要求每个相位精确编码一致，须解新增方程

    H(v)=col(h(q_0(v)),...,h(q_{T-1}(v)))=0.          (P9)

当h(q*)=0，DH(0)=Lenc。仅有Lenc的非零核不保证存在非零解曲线，例如标量H(v)=v²有DH(0)=0但零点局部只有v=0。不能由维数计数或一阶消元宣告P9已解。
若H在开放激励邻域为C1（例如h与S5分支均在邻域C1），且DH(0)=Lenc为满行秩，则正则值/隐函数定理给出局部零点流形，其切空间为ker Lenc。若另有P8，则可沿其中一个vbar方向取曲线v(epsilon)=epsilon vbar+o(|epsilon|)，其模型周期参考精确编码兼容，且充分小非零epsilon下输出非恒定。输入内点与连续性保留幅值余量。
这是一般维数下比S5更强的局部充分条件，但在本项目两个实验平台的原始堆叠方程上，满行秩条件结构性不可能：设p=d-n为潜特征维数，H:R^{Tm}->R^{Tp}，所以rank Lenc<=Tm。`Transformer-Koopman/杂项/新版本/Temporary_Experiments/models/device.py` 中两平台p=8，软体平台m=2、机械臂m=3，均有Tp>Tm；任何周期长度T均不能使原始Lenc满行秩。该结论不读取checkpoint，也不依赖数值秩。
被排除的是这个满行秩充分构造，不是P9解本身；过定约束可能存在依赖或特定解。若改用独立约束或常秩定理，必须证明其与原始全部非线性方程局部等价，不能只删选Jacobian行。历史移位不会增加独立的Tm个激励自由度。本文不改变训练或参考定义来绕过此障碍。
即使P9精确解存在，也只说明模型轨道在编码像上；物理plant能否实现、当前测量输出误差和邻域内统一重新编码残差仍须独立证明。

## 状态与下一实质门槛

P1–P3给出非零基点编码间隙对小幅周期参考的定量障碍；P4–P8给出零间隙基点上的一阶兼容方向判据；P9区分切空间兼容与真实非线性可解性，并给满行秩下的局部充分构造。
结构类本身既允许兼容也允许不兼容，实际sigma*、Hh、R_t与Lenc秩未认证。此分支不重复假设终端集存在，而把下一对象明确收敛到“固定基点的编码间隙及周期约束Jacobian”。
全部为条件静态解析结论；具体模型/参考/实际初始化仍OPEN，P5正式稳定性阶段STOP。
