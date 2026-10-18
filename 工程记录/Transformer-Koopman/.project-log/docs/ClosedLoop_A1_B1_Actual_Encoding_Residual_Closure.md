# B1：实际编码状态的残差比较与自洽闭合

2026-10-18；TASK-B1-DERIV-20261018；strict（conclusion）。纯理论，无产品修改、checkpoint或数值验证，P5 STOP。
衔接D1/D8、E1–E8、N6及联合预算B13/B14。下文范数为非重复q坐标的欧氏范数。

## K1. 内部编码缺陷的精确恒等式

定义h(q)=C_psi z-psi(col(a,C_xz))。对任意当前合法q（不限于编码状态），D1给出的下一完整测量窗口正好是shift(col(a,C_xz),C_x f(q,u))，因此

    kappa(q,u)=-h(F(q,u)).                           (K1)

这把N6中只对参考写出的关系推广到任意当前状态。它不表示h(q)=0能推出h(F(q,u))=0；编码像仍非不变流形。
E1实际采样使用q=q^E，而传播参考q_ref一般不是编码状态。K1允许比较两者，但不能将它们认作同一状态。

## K2. 从参考到真实当前状态的显式比较

令参考满足q_ref,t+1=F(q_ref,t,u_ref,t)，记sigma_t+1=||h(q_ref,t+1)||。h在所需下一窗口域的Lipschitz常数可取Kh=sqrt(1+Lpsi²)。R2给当前域的同输入状态界Lq；固定同一q，输入导数为col(B(C_xz),0,E_u)，故可取

    Lu=sqrt(MB²+1), MB=||B0||+gB.

对q^E、q_ref及输入u、u_ref，只要各比较映射在共同认证域内，即有

    ||kappa(q^E,u)||
      <=sigma_t+1+Kh[Lq||q^E-q_ref,t||
                          +Lu||u-u_ref,t||].        (K2)

证明：对K1在下一状态应用h的Lipschitz界，再将F差沿状态与输入分解。若Lq仅对输入U成立，需u∈U；Lu用同一域/输入包络。h的域须覆盖F(q^E,u)、F(q_ref,u_ref)对应窗口；不能只认证当前窗口。也可以直接以较大窗口域包络预测点，不要求下一预测点已在较小QP安全域。

若所有允许当前编码状态和执行输入满足统一半径rho、upsilon，则取周期各相位最大值sigma，得到

    kappa_bar=sigma+Kh(Lq rho+Lu upsilon),
    w_req=sqrt(nu_bar²+(kappa_bar+Lpsi nu_bar)²).     (K3)

nu_bar为E1的测量输出误差界；它不来自K2，不得默认为0。Lpsi还须覆盖测量扰动后的窗口，如E2节域包含所要求。

## K3. 量词：不能把初始种子半径当作以后每次的状态管

rho必须覆盖每个采样时刻可能的q^E，upsilon必须覆盖每次实际执行的u0；只需当前点，不要求给所有预测位置套相同跟踪管。J8的xi只认证首轮可行种子，不保证每次q^E都留在xi邻域；终端集合约束也不约束当前状态到参考的距离。
一个不改变在线算法的保守来源是固定紧工作域Omega与输入盒U：

    rho=max_t sup_{q∈Omega}||q-q_ref,t||,
    upsilon=max_t sup_{u∈U}||u-u_ref,t||.             (K4)

有限周期与紧域使这些数有限。须用O/J阶段0归纳证明实际q^E始终在Omega，并且K2所需预测窗口域另有包络。证明顺序是：独立固定大认证域及其常数→对Omega×U的当前点统一残差认证→以该残差作移位证书→从初始种子归纳下一q^E合法。不预设未来轨迹合法。
K4常数可能过大以致B13失败；这说明当前全域包络证书不足，不是实际系统不可能。若改用更小rho，必须给覆盖所有执行解的独立集合证书；新增跟踪硬面会改变QP，未经批准不实施。

## K4. 把参考的二阶小间隙接到联合预算

N6给参考族sigma(epsilon)<=C_sigma epsilon²（充分小参数区间内的统一常数）。K3因而给

    kappa_bar(epsilon)
      <=C_sigma epsilon²+Kh(Lq rho+Lu upsilon).     (K5)

固定正rho/upsilon时，小激励仅消去第一项，不能消去邻域状态/输入比较项。即使某条参考精确编码兼容（sigma=0），也不等于邻域残差为0。
若以认证上界nu_bar=O(epsilon²)、rho=O(epsilon²)、upsilon=O(epsilon²)，才可由K3推出w_req=O(epsilon²)。这些缩域/执行输入性质是新证书要求，不能从S5小周期参考、稳定反馈或J8初始种子自动推出。尤其任意QP可行输入不等于参考生成辅助反馈。
已取得K3常数后，若存在B13中的r、xi、w使w_req<=w<Wjoint(r,xi)，并满足实际初始化和全部域/输入/线段条件，就完成这条残差预算接口。仍未取得实际参数与测量误差界时，仅为条件解析结论。

## K5. 允许域外包依赖预算时的自洽不等式

有些离线设计使用依赖候选预算w的允许域。只有独立认证对于每个试选w，所有相关当前状态/输入外包满足

    rho(w)<=rho0+rho1 w,
    upsilon(w)<=upsilon0+upsilon1 w,               (K6)

且Lq、Lu、Kh、Lpsi、sigma、nu_bar在整个设计族的较大认证域上固定，才可设置

    a=sigma+Kh(Lq rho0+Lu upsilon0)+Lpsi nu_bar,
    b=Kh(Lq rho1+Lu upsilon1), n=nu_bar,
    sqrt(n²+(a+bw)²)<=w.                           (K7)

a,b,n均非负。K6不是由K7反推的状态管；未证明K6时，求出w也不闭合证明。此处b是增益标量，不是多面体右端。

当0<=b<1，K7等价于

    w>=w_min=[a b+sqrt(a²+(1-b²)n²)]/(1-b²).       (K8)

证明：非负两边平方得(1-b²)w²-2ab w-(a²+n²)>=0；唯一非负阈值即K8。a=n=0时w_min=0，全部w>=0适用。
当b>=1且a>0或n>0，K7无非负解。当a=n=0，b=1时全部w>=0成立；b>1时仅w=0成立。这些是当前非负仿射上界的自洽判别，不是必要的真实动力学小增益条件。

因此在b<1的子类，联合问题变成寻找

    w_min<=w<Wjoint(r,xi),
    B10半径下限、r_cap、初值和域证书同时满足。      (K9)

当其余常数固定且K6已有独立证书时，K8给残差的下限，B12给容量上限，二者竞争可明确审计。设计w范围若有限，还须检查w_min落在K6的已认证范围内；不能外推。

## K6. 不可从当前结构消去的输入与物理信息

Kh/Lq等架构界和sigma参考界可解析推导；nu_bar需要测量/plant或允许元组集合证书。即使nu_bar=0，K2仍需当前编码状态/执行输入的范围或直接kappa包络。不能以训练loss、一次仿真或只对名义序列的界替代全部执行解的统一覆盖。
本增量完成的是精确K1、全域K2/K3比较和可解的K7自洽判别。具体模型仍无固定基点/PBH、参数范数、统一nu_bar与实际初始化认证；B1 OPEN，P5 STOP。没有修改正式控制器，也未证明plant稳定。
