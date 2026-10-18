# B1：残差、终端半径与实际初始化的联合预算

2026-10-18；TASK-B1-DERIV-20261018；strict（conclusion）。纯解析；不改论文/代码/控制器，不做数值、checkpoint或plant验证，P5 STOP。
前置：D7–D10、C3–C5、O1–O7、J1–J8、R1–R7、E1–E8。本文消去其中可显式消去的误差递推，而不再分别假设各关口可行。

## B0. 固定设计与统一坐标

选择固定多面体工作域Omega={q:Hq<=b}，模型可实现周期参考q_ref,t；固定P范数，P正定，固定有限面网系数alpha=cos(theta)∈(0,1)。周期K_t允许变化；取统一收缩lambda<alpha、余项常数c>=0、完整Jacobian范数Abar及参考缺陷界bref>=0。对本模型可实现参考bref=0，保留该符号仅便于核对D9账本。
球形上界为B_P(r)，有限面终端集Z_t满足B_P(alpha r)⊆Z_t⊆B_P(r)。固定P/相同面网可取固定Z；不要求参考恒定。

令L为完整增广F在已认证域的统一欧氏同输入Lipschitz界，e0>=0为统一Frozen当前点缺陷界（R4的eta，为避免与种子半径混淆改名e0），w>=0为统一重新编码残差半径。定义

    S_i=sum_{j=0}^{i-1} L^j,  S_0=0,
    E_i=e0 S_i,
    T_i=sum_{l=1}^{i} E_l,
    g_j=L^j w,
    D=||P^{1/2}|| E_N, gamma=||P^{1/2}|| L^N.       (B1)

N>=1；以下采用R2给出的L>=1，故S_i>0(i>=1)、L^N>0。可以用更紧的正L代替；不在本文处理L=0的除零分支。e0,L等必须先在独立域上固定；若随r或w改变，须重新计算，不能沿用本文固定常数的极值结论。

## B1. J3深度收紧的闭式解

记h_r=||H_r||_2，取eps_{j,r}=h_r(E_{j+1}+L^j w)。J2安全下界s_{i,r}=h_r(E_i+L^{i-1}w)正好为eps_{i-1,r}。
由于m_i>=0，J3中的m_i+eps_i>=s_{i+1}，故可消去max：

    m_{i,r}=sum_{j=0}^{i-1} eps_{j,r}
           =h_r(T_i+w S_i).                         (B2)

这是选择上述球包络eps后的J3精确解，不是所有多面体设计中的最小保守收紧；更紧支持函数包络可能改善结果。
公式同时保留O5/O7安全域与W4移位要求。L=1时S_i=i、T_i=e0 i(i+1)/2，显示即使一步误差不增长，累积阶段收紧也可能随N平方增长。

## B2. 终端收缩允许的重编码残差

令

    V(r)=lambda r+c(r+D)^2+Abar D+bref.             (B3)

V是旧full延长误差的P范数上界，不含重新编码传播项。为将新候选像压入终端内球，足够要求

    V(r)+gamma w < alpha r,
    w < Wterm(r):=[(alpha-lambda)r-c(r+D)^2
                          -Abar D-bref]/gamma.      (B4)

这比C2的球像条件更直接：固定面网后，alpha不是事后任意接近1的自由参数。若Wterm(r)<=0，则这个固定球包络/面网分支连w=0也不能获得严格余量；不据此否定别的面网/形状或真实集合。

当c>0，Wterm对r严格凹，其无约束最大点及最大值为

    rstar=(alpha-lambda)/(2c)-D,
    Wterm(rstar)=[(alpha-lambda)^2/(4c)
                  -(alpha-lambda)D-Abar D-bref]/gamma. (B5)

若允许r区间为闭区间[rlow,rhigh]且0<rlow<=rhigh，最大点为rstar向该区间的投影。若取零下端且只允许r>0，投影可能为0，此时只给正半径域的上确界，不保证最大值可达。c=0时Wterm为正斜率仿射函数，在有限正上端取得最大值。
该极值只优化终端这一关口，未优化下面所有关口；不能用B5为正就宣告联合证书可行。

## B3. 终端集与最深工作域的竞争

对固定H、周期参考定义统一未收紧余量

    mu_r=inf_t [b_r-H_r q_ref,t],
    v_r=||H_r P^{-1/2}||_2.

因为Z⊆B_P(r)，J4由下式充分保证：

    v_r r+h_r(T_N+w S_N) <= mu_r.                  (B6)

对非零面H_r（h_r>0），可得

    w <= Wface,r(r):=(mu_r-v_r r-h_r T_N)/(h_r S_N). (B7)

所以增大r通常提高初始终端容量，却线性压缩工作域残差余量。零面只需检查0<=b_r，不能代入除法。若参考相位数有限，inf为有限相位最小值。

## B4. 独立的旧full延长球关口

J5/J6要求整个旧full延长误差球加编码传播球留在Omega。B3只包络旧延长点，不含w，故其充分条件为

    v_r V(r)+h_r L^N w <= mu_r,
    w <= Wext,r(r):=(mu_r-v_r V(r))/(h_r L^N).      (B8)

B8与B6不同：前者保护用于传播误差证明的整个球，后者保护下一QP最深收紧面。即使B4和B6成立，也不要在未检查范数差异与球外包关系时删去B8。
终端Taylor联合线段和tail输入余量仍由独立r_cap保护；r_cap须给D的潜在偏差留余量，不能仅限制r本身。

## B5. 实际初始化带来的半径下限

取一个明确xi>0，作为要认证的欧氏初始邻域半径，要求实际初值满足E7的上界

    sigma_ref+sqrt((1+Lpsi²)||DeltaX||²+||Deltav||²)
       <= xi.                                    (B9)

同时xi<=eta_domain。终端内球的欧氏半径可取rho=alpha r/||P^{1/2}||。参考输入下，初始误差传播至N步<=L^N xi，所以J8末端条件给出

    r >= rseed(xi):=||P^{1/2}|| L^N xi/alpha.       (B10)

并非E8下界本身即可充分保证初始化；B9是充分预算。E8还可独立排除xi<sigma_ref/sqrt(1+Lpsi²)的编码像相交。
对阶段1<=j<=N，用相位/初始时刻统一mu_{j,r}=inf_k[b_r-H_r q_ref,k+j]，必须

    h_r(T_j+w S_j)+h_r L^j xi <= mu_{j,r},
    w <= Wseed,j,r(xi):=
           (mu_{j,r}-h_r T_j-h_r L^j xi)/(h_r S_j). (B11)

阶段j=0另查h_r xi<=mu_{0,r}；其S_0=0，不通过B11除法。因为xi>0，h_r>0，B11即使取等号也使收紧后的阶段参考余量>=h_r L^j xi>0，可使用J8。
实际q^E若精确为参考（sigma_ref=0等），也可用任意认证的正xi覆盖它，不要求把xi设为0。

## B6. 联合容量与真正的相容性测试

对给定r、xi定义

    Wjoint(r,xi)=min{Wterm(r), min_rface Wface,rface(r),
                     min_rface Wext,rface(r),
                     min_{1<=j<=N,rface} Wseed,j,rface(xi)}. (B12)

面索引rface与终端半径r不同。B7/B8/B11所有容量比值和B12的面最小值均仅遍历h_rface>0的非零面；零面单独检查b_rface>=0，若没有非零面，相应最小值按+infinity处理。一个方便的统一严格证书是选择

    0<=w<Wjoint(r,xi),
    rseed(xi)<=r<=r_cap, xi<=eta_domain,
    h_rface xi<=mu_{0,rface},
    B9、合法Taylor联合域、tail输入证书。          (B13)

除Wterm外的关口原本允许等号；B13统一取严格值只是保守方便。若某关口恰为零，不能用B13，仍可逐条检查B4/B6/B8/B11而不误判所有证书失败。
剩余设计为至多(r,xi)的低维联合不等式；这里没有运行求解。增加xi会提高rseed并压低Wseed，不能分别最大化半径和残差后组合。若B9只知道未知sigma_ref，B13仍未认证。

## B7. 把允许残差容量反馈到测量/编码两类缺陷

若选定一个满足B13的试验预算w（不是数值实验），E2给实际适用的充分条件为

    nu_bar²+(kappa_bar+Lpsi nu_bar)² <= w².         (B14)

非负nu_bar/kappa_bar下，等价于

    0<=nu_bar<=w/sqrt(1+Lpsi²),
    0<=kappa_bar<=sqrt(w²-nu_bar²)-Lpsi nu_bar.     (B15)

这给出明确的“测量误差—内部编码缺陷”预算曲线。光滑不代表kappa_bar接近0；nu_bar=0时仍要求kappa_bar<=w，kappa_bar=0时仍要求nu_bar<=w/sqrt(1+Lpsi²)。
在固定其余证书下，B14/B15告诉后续认证需要达到的上界；它不提供真实plant误差界，不把平均训练loss等同于该认证。

## B8. 固定P子类中可消去延长球预算的重复检查

一般J证书仍须单列延长球。但本文固定P、相同Omega、同一周期最小余量时，对非零面有h_r<=v_r||P^{1/2}||。因此B4给（零面只检查b_r>=0，不使用严格链）

    v_r V(r)+h_r L^N w
       <=v_r[V(r)+||P^{1/2}|| L^N w]
       <v_r alpha r<=v_r r.

B6又给v_r r<=mu_r-m_N,r<=mu_r，所以B8自动成立。可在本固定P子类的B12中删去Wext关口，不损失已证明条件；若换成不同域/相位P或不同参考余量，须重新证明这一蕴含，不能从C5相关像包含直接推整个球。

## B9. 联合预算的凸性与小残差鲁棒余量

当所有常数固定，B4左端V(r)+gamma w-alpha r关于(r,w)凸；B6、B10、B11及r_cap/xi边界均为仿射不等式。对给定实际初始化充分上界d_init（E7右端的已认证值），再施加xi>=d_init，预算可行域为(r,w,xi)中的凸集（严格B4给相对开约束）。离线可用正裕量tau>0替换为V(r)+gamma w<=alpha r-tau；这是预算综合问题，不是在线控制器的额外QP，也不宣称是LP。
因此一旦指定有限常数，这一子分支无需对r、w、xi作非凸盲搜。尚未认证的d_init或参数不能作为已经知道的数输入。

若存在一组正r、xi使w=0时B4/B6/B11有严格余量，且同时满足B9实际初值上界、B10半径下限、阶段0面及r_cap/eta_domain/线段与输入条件，则因有限阶段/面数和表达式连续性，存在epsilon>0，使同一r、xi对0<=w<epsilon仍可行。epsilon可直接取B12各正容量的最小值。这里不能把实际w说成可任意调小；E2/E5仍须证明实际统一残差低于epsilon。

## 验收与边界

新增结果：B2消去安全/shift递推，B4/B5给终端残差容量及最优半径，B7/B8/B11给工作域/延长球/实际种子的竞争，B10给初始半径下限，B14/B15拆回输出与编码缺陷预算。
若整个允许区间的Wterm<=0，可否定当前严格终端上界分支；若rseed>r_cap，可否定当前J8内球种子分支；都不是物理不可能或所有多面体不存在的结论。
全部结论在固定已认证常数下是解析蕴含；当前模型的PBH、参数、nu_bar/kappa_bar、sigma_ref以及联合数值可行性仍OPEN。纯理论继续推进不等于实例认证，P5 STOP。
