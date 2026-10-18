# B1：调度公式的显式正则常数与统一冻结缺陷

2026-10-18；TASK-B1-DERIV-20261018；strict（conclusion）。纯符号推导，不读取参数/checkpoint，不运行数值验证，不修改论文/控制器；P5 STOP。

依据：Main.tex 256–325行的低秩softmax–tanh调度、434–451行的域/Lipschitz/残差假设，以及D1完整增广递推。以下常数为可从参数范数计算的公式，不是当前训练模型的已认证数值。

## R1. 调度矩阵的一阶、二阶全局界

统一写S(y)=S0+sum_{j=1}^r u_j v_j^T gamma_j(y)，gamma_j=g p_j(y)t_j(y)，p=softmax(Wpi y+bpi)，t_j=tanh(w_j^Ty+b_j)。假定各因子列范数不超过1（论文明确的假设，未核实当前实现是否满足）。令a=||W||_2、pbar=||Wpi||_2。

论文已经给出MS=||S0||+g、LS=g(a+sqrt(r)pbar/2)，满足||DS(y)[h]||<=LS||h||。LS可由向量系数的1范数控制矩阵和得到，不把低秩因子矩阵的整体谱范数错当成1。

给出一个保守但显式的二阶界。对softmax的logit方向alpha,beta，

    Dp_j[alpha]=p_j(alpha_j-E_p alpha),
    D²p_j[alpha,beta]
      =p_j[(alpha_j-E_p alpha)(beta_j-E_p beta)-Cov_p(alpha,beta)].

因为|alpha_j-Ealpha|<=2||alpha||_2且|Cov(alpha,beta)|<=||alpha||_2||beta||_2，故|D²p_j[alpha,beta]|<=5||alpha||||beta||，以下放宽为6。又||Dp_j||<=1/2、|tanh'|<=1、|tanh''|<=2，因此

    ||D² gamma_j|| <= g(6 pbar² + pbar a + 2 a²),
    HS := r g(6 pbar² + pbar a + 2 a²),
    ||D²S(y)[h,l]||_2 <= HS ||h||_2 ||l||_2.             (R1)

两个交叉乘积各贡献(pbar/2)a，故合计pbar a。此界无须输入有界；bias不影响这些导数上界。r=0时调度恒定，直接取LS=HS=0。对A/B分别得到HA、HB；矩阵值双线性导数使用欧氏输入/谱输出的算子范数。

## R2. 完整F的状态Lipschitz常数（不需要二阶正则）

令Tq=col(a,C_xz,v)为context输入，C_x为坐标读出；在q=(z,a,v)的欧氏范数中||T||=1。设Omega为独立给定的紧凸域，||z||<=MZ，输入||u||<=MU，且C_phi在T(Omega)的Lipschitz常数为Lc。则c(q)=C_phi(Tq)的常数同为Lc。

固定同一输入u，对两个当前合法点，z更新的差不超过

    Lf ||q-q'||,
    Lf = MA + MZ LA Lc + MU LB.

历史更新的线性状态算子为col(S_x da+E_x C_x dz,S_u dv)，各槽选择互不重复，算子范数<=1。因此

    LF := sqrt(Lf²+1),
    ||F(q,u)-F(q',u)|| <= LF ||q-q'||.                 (R2)

这是增广q的界，不照搬论文对最大滑窗误差的L，也不额外插入sqrt(P)。若选用非欧氏范数或含重复槽的旧坐标，须重新换算。R2适用于O2的当前点传播和D8的同输入传播，不证明LF<1或可稳定化。

## R3. 需要context导数证书时的完整二阶界

若额外证明C_phi在包含所需线段的窗口域上C²，||DC_phi||<=Lc、||D²C_phi||<=Hc，则组合A(c(q))满足

    ||D_q A||<=LA Lc,
    ||D_q² A||<=HA Lc²+LA Hc.

对联合变量(q,u)，F的历史块为仿射，Hessian只来自z块的A(c(q))z+B(C_xz)u。逐项乘积法则给出

    HF = MZ(HA Lc²+LA Hc) + 2 LA Lc
         + MU HB + 2 LB.                              (R3)

于是沿联合状态/输入线段在认证域内时，||R(h,l)||<=HF/2 *||(h,l)||²，直接给D7所需常数。此处MU必须覆盖线段上的输入，MZ覆盖线段上的z；不能只覆盖参考点或QP输出端点。
R3是方便的C²充分条件；C^{1,1}及直接DF Lipschitz认证亦可，不要求模型必为C²。论文仅声明context Lipschitz，不能据此自动填Hc。

## R4. 覆盖所有合法冻结名义的缺陷上界

令Omega直径DOmega，z半径MZ，输入半径MU；候选p与用于冻结的名义bar q均在Omega。O1的缺陷仅有z块：

    delta = [A(c(p))-A(c(bar q))]z_p
            +[B(C_xz_p)-B(C_xz_bar)]u.

由有界调制和Lipschitz两种界取较小者，得到

    aDelta = min(2gA, LA Lc DOmega),
    bDelta = min(2gB, LB DOmega),
    eta = aDelta MZ + bDelta MU.                      (R4)

R4覆盖所有(p,bar q,u)∈Omega×Omega×U组合，不只覆盖某条名义轨迹。若还没有Lc证书，仅取aDelta=2gA、bDelta=2gB仍成立；这条粗缺陷界只需调度幅值和当前点合法。若逐深度有更小认证域，可逐层计算eta_i，但必须覆盖全部允许名义系数。

固定LF与eta时，O2给

    E_i = eta sum_{h=0}^{i-1} LF^h,
    g_j = LF^j wbar,
    eps_j = hrow(E_{j+1}+g_j),                        (R5)

其中hrow=(||H_r||_2)_r，不是Taylor扰动h；E0=0。LF=1时E_i=i eta；零次幂按空乘积1。代入J2/J3可直接得到有限收紧序列，无须再假设一组未知E_i存在。
eta粗上界可能令J4/J7失败，不能据此判定真实系统不可能。R4并未证明名义rollout合法；O/J的逐点域包含/初始种子证书仍须先后使用。

## R5. 由HF到D9的一个显式范数转换

设||e||_{P_t}<=r，||d_fr||_{P_t}<=Delta，alpha_t=||P_t^{-1/2}||，beta_{t+1}=||P_{t+1}^{1/2}||。则

    ||(e+d_fr,K_t e)||_2²
       <= alpha_t²[(r+Delta)²+||K_t||² r²]
       <= alpha_t²(1+||K_t||²)(r+Delta)².

故D9可用

    c = sup_t beta_{t+1} HF,t alpha_t²(1+||K_t||²)/2,
    Abar = sup_t ||P_{t+1}^{1/2} A_t P_t^{-1/2}||,
    d0 = Abar Delta + bref + sup_k beta_{k+N+1} LF^N wbar.   (R6)

A_t为完整增广Jacobian D_qF，而非低秩名义A0或A(c)。bref为参考缺陷的跨时刻P范数；模型可实现参考时为0。编码误差终端只计LF^N wbar一次。常数取跨时刻统一上界，周期情形可取有限相位最大值。
若E_N来自R5，可取Delta>=sup_t ||P_t^{1/2}|| E_N。以上sup必须独立证明有限：仅有逐时刻P_t正定不足以保证统一范数等价；有限周期正定族可直接取各相位最大值。闭环lambda<1仍须独立证书，不能由R2推出。该转换保守，但将低秩调度参数、context正则、Omega、P/K与D10的判别式明确连接。

## R6. 为什么现有Lipschitz假设不能完成二阶认证

结构内反例：d=n=1，任意合法历史长度，C_phi(Tq)=|z-1|（忽略历史）；rank-one调度取gA=1、rA=1、softmax恒为1、tanh权重1、A0=1、B=0。则

    f(z)= [1+tanh(|z-1|)]z.

在z*=1、a*=col(1,...,1)、v*=0、u*=0有完整D1模型平衡点，C_phi为1-Lipschitz，所有因子满足论文范数约束；但f在1的左导数为0、右导数为2，不存在Jacobian，更不可能对某个单一线性化给统一O(|h|²)余项。缓存块不消除该不可微性。
这不声称项目真实context采用绝对值，也不否定平滑Transformer的可能性；仅证明论文目前抽象C_phi的Lipschitz假设不足以推出D7的二阶版本。论文的encoder Transformer描述不能当成context网络的C²证书。

## R7. 当前实验context的可用光滑实例（只读源码证据）

实际文件 `Transformer-Koopman/杂项/新版本/Temporary_Experiments/models/library.py` 100–110行明确实现

    C_phi(w) = tanh(W2 tanh(W1 w+b1)+b2),
    w=col(vec X,vec Uin).

155–156行将encoder与ctx作为独立模块；ctx路径无attention、LayerNorm或dropout。参数固定时，对实数输入该映射实解析。设a1=||W1||_2、a2=||W2||_2，利用分量tanh二阶双线性范数<=2，链式法则可取

    Lc = a1 a2,
    Hc = 2 a1²(a2²+a2).                              (R7)

证明：内层导数<=a1、二阶<=2a1²；外层导数<=a2、二阶<=2a2²，复合二阶<=2a2² a1²+2a2 a1²。若输入还有固定仿射归一化w=Rw_phys+b，则物理坐标导数界分别乘||R||与||R||²。本文件使用模型自身坐标，不假定标准化尺度为1。

126–129行列归一化也使固定参数下的因子列范数<=1，故R1因子假设对该数学实现成立；这是输入方向正则性，不声称原始因子参数在零列处也可二阶求导。
因此对这一具体代码架构，context的抽象正则缺口可由R7解析补上，无需数值求Hessian；R3提供任意给定紧联合域上的HF公式。仍未读取W1/W2的实际参数、认证其幅值与预算，也未认证编码残差或PBH。

限定：Main.tex 258–263行未固定context网络，438–447行仅假设Lipschitz；正式代码新路径为空，不能将实验MLP擅自写成论文规范。R6反例针对抽象Lipschitz类别，R7针对实验MLP子类，两者不矛盾。encoder初始化的Transformer正则性不用于递归F的context证书；真实初始化/编码残差仍独立。

## 验收与精确剩余项

| 对象 | 解析结果 | 仍未认证 |
|---|---|---|
| A/B导数 | R1由现有softmax/tanh与因子假设推出；实验列归一化保证该假设 | 实际权重范数量值；论文一般实现的因子假设适用性 |
| 完整F状态传播 | R2，已区分完整q与最大窗范数 | Lc、Omega和余量实例 |
| 所有冻结系数缺陷 | R4，不需要下一full点合法 | 实际域非空及安全/shift兼容 |
| 二阶余项 | R3/R6显式参数公式及R6反例；实验Tanh MLP由R7给出证书 | 论文抽象context未固定；实际权重/域/预算未认证 |
| 重新编码扰动 | 只传播已给wbar，不从训练损失推出 | 无限采样统一残差上界 |
| 正终端半径和参考 | 可将R6代入D10 | PBH/反馈/具体参考/初值、判别式与约束余量 |

结果不是再次假设未知常数存在：调度二阶界和全候选冻结缺陷已有公式；论文抽象context的二阶正则仍未保证，实验MLP已有R7解析界，但实际权重对应的定量常数及预算未认证。统一重编码残差仍是独立缺口。未认证具体模型，不进入P5。
