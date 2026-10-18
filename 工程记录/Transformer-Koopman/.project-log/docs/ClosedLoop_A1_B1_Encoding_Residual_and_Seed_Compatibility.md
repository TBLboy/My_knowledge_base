# B1：重新编码残差的来源与实际种子兼容性

2026-10-18；TASK-B1-DERIV-20261018；纯理论、strict结论级。无论文/代码/实验改动，无checkpoint或数值验证，P5 STOP。
衔接D1/D8、J8与R1–R7。所有编码映射均指固定参数的确定性实数映射；若有dropout，须固定为确定性部署模式，不能把no_grad当作eval。

## E1. 一步编码残差的精确分解

令G(X)=col(x_last,psi(X))，q^E=col(G(X),a,v)，X=col(a,x_last)。给定实际施加u，令

    zhat+=f(q^E,u), xhat+=C_x zhat+,
    Xtilde+=shift(X,xhat+),
    nu=x_meas+ - xhat+,
    Xmeas+=Xtilde+ + E_X nu,
    kappa=psi(Xtilde+) - C_psi zhat+.

E_X仅把nu注入完整窗口的末槽，算子范数1；C_psi选择潜坐标。于是

    r=G(Xmeas+) - zhat+
     =col(nu, kappa+psi(Xmeas+)-psi(Xtilde+)).         (E1)

nu是实际下一测量相对模型输出的误差；kappa是模型自身一次传播后的编码一致性缺陷，两者不是同一量。即使nu=0，kappa也可非零。
若该窗口域上psi为Lpsi-Lipschitz，且统一有||nu||<=nu_bar、||kappa||<=kappa_bar，则

    ||r|| <= sqrt(nu_bar²+(kappa_bar+Lpsi nu_bar)²)
            =: wbar.                               (E2)

对D1非重复q，a+与v+缓存当前旧测量/本次输入，不受新测量nu注入，所以实际重新编码跃迁恰为

    q_next^E = F(q^E,u) + col(r,0,0).                (E3)

E2就是可代入D8/J2的wbar，不再把nu、kappa或首步r另加一次。假定输入精确执行、历史缓冲准确；传感器修正整个过去窗口、输入执行偏差或延迟不在此E3中自动覆盖。

## E2. 域条件先于Lipschitz使用

Lpsi必须覆盖Xmeas+与Xtilde+两点。可以独立选定紧窗口域D，限制所有允许当前编码状态/输入的预测窗口Xtilde+，并验证Xtilde+⊕E_X B(nu_bar)⊆D。若使用导数证明Lpsi，则相应连接线也需在认证域内。
这需要预测输出包络和测量误差包络，而非先假设未来真实轨迹无限期留在D。可与O/J逐步域证书衔接；没有独立nu_bar时不能用E2完成无限采样归纳。

若G及f连续、Omega_E为编码状态的独立紧集合、U紧且预测窗口在G定义域，则kappa连续，故有有限上界。显式粗界为

    kappa_bar <= Mpsi + MA MZ + MB MU,              (E4)

其中Mpsi覆盖预测窗口的特征、MB=||B0||+gB。E4只说明给定紧域上有限，通常很保守；不说明小到满足C2/J7。nu涉及外部测量/plant行为，不能仅由预测器的光滑性控制。

## E3. 有限训练损失与全域残差的逻辑差别

训练loss约束有限样本上的编码一致性/输出误差，不自动给出连续工作域上的统一上界。即使有限样本loss为零，也可在未覆盖点有残差。
一个可检验的补充证书是：允许窗口/输入/下一测量元组集合T紧，训练/验证点构成T的epsilon-net，残差映射在T为Lr-Lipschitz，网点最大残差<=delta_s，则

    sup_T ||r|| <= delta_s + Lr epsilon.            (E5)

证明：任意点选相距<=epsilon的网点，应用三角不等式。需要网点覆盖和残差Lipschitz双重证书；普通随机数据划分不等于epsilon-net。若改以未知plant映射参数化T，Lr还需plant正则性证书，不能从encoder光滑性推出。
本轮不读取数据或执行覆盖度验证，E5不是已完成的项目认证。

## E4. 模型可实现参考未必在编码像上

令q_ref=col(z_ref,a_ref,v_ref)为完整F的模型可实现轨道某时刻，x_ref=C_xz_ref，X_ref=col(a_ref,x_ref)，定义

    sigma_ref=||psi(X_ref)-C_psi z_ref||.            (E6)

固定相同参考测量窗口/输入历史重编码，q_Eref=col(G(X_ref),a_ref,v_ref)，则||q_Eref-q_ref||=sigma_ref。模型参考可实现只约束F递推，不蕴含sigma_ref=0。

令实际窗口X、过去输入v与参考的偏差分别为DeltaX、Deltav。对psi具有Lpsi的域，由欧氏直和与三角不等式有

    ||q^E-q_ref||
      <= sigma_ref + sqrt((1+Lpsi²)||DeltaX||²
                           + ||Deltav||²).          (E7)

原因：a与当前x在q中各出现一次，合在一起正好是完整X的欧氏偏差；psi再贡献Lpsi||DeltaX||，没有重复计算当前x。
若J8已生成初始半径eta，且右端<=eta，则这是实际初始化的充分证书。特别是sigma_ref<eta才允许以E7构造有正裕量的参考窗口邻域；此处只讨论信息窗口，未保证任意该窗口都可由物理plant实现。

## E5. 编码像距离的必要下界

在相同域定义不一致函数h(q)=C_psi z-psi(col(a,C_xz))。编码状态满足h(q^E)=0。令b=||(a-a_ref,C_x(z-z_ref))||、t=||C_psi(z-z_ref)||，则

    ||h(q)-h(q_ref)|| <= t+Lpsi b
                          <= sqrt(1+Lpsi²)||q-q_ref||.

所以任意该域内编码状态满足

    ||q^E-q_ref|| >= sigma_ref/sqrt(1+Lpsi²).        (E8)

若此下界>eta，则J8球与该域内编码像不相交，当前参考的这条种子分支不适用；不是原QP不可行，也不否定更大非球种子或另选参考。下界<=eta不是相交充分条件；E7给独立充分条件。
平衡参考与周期参考均可逐相位计算sigma_ref。S4/S5通过隐函数定理构造的传播轨道不自动满足E6为零；增加“周期编码像一致”是额外方程，不能在原IFT结论中隐含加入。

## E6. 光滑与稳定并不消除编码像间隙：结构内反例

取n=1、d=2、psi(X)恒为非零常量b，A(c)恒为diag(a,rho)，B恒为0，其中|a|<1、|rho|<1。令调度增益为0即可满足低秩模型结构；context可选光滑常量。原点q_ref=0（含历史/输入缓存）为完整F的稳定平衡点；所有模态都在单位圆内，故可稳定化条件成立，即使B=0。
然而编码像潜槽恒为b，sigma_ref=|b|，任何编码状态距原点至少|b|。在零测量/零输入编码状态，nu=0而kappa=(1-rho)b，可非零。任取J8半径eta<|b|，其球与编码像不交。
这不是实际训练模型的结论，只反驳“光滑+可稳定化+模型参考存在，便自动得到可实际初始化的种子/零重编码扰动”。严格衰减模型本身也不能补上编码一致性证书。

## 裁决与下一门槛

E1/E3为精确恒等式；E2/E7为显式充分界；E8给必要初始化下界；E5给全域残差的一种可认证路径。它们不是“假设残差小即可”的同义改写，而是分别暴露输出误差、内部编码缺陷、参考编码像距离三个不同对象。
当前项目仍缺统一nu_bar/kappa_bar及实际sigma_ref/eta比较。解析平滑性R7已解决实验context正则，不解决这些对象。具体B1仍OPEN；P5 STOP，无plant稳定性宣称。
