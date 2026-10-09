# 阶段② S6 Theory Construction v0.1（组合路线）＋ S7 Proof Audit

> 状态：**candidate theory**，未经验证；代码/论文正文未修改。本文件是 S6 的定理声明、假设、证明骨架与 S7 反例审查。
> 取向（DEC-016，用户 C 级确认）：**组合路线** = 「可验证闭环 task-tracking 界」为理论骨架 + A9（执行器冗余/零空间门控）为物理载体 + P1/P2 两平台实机验证。

---

## 1. 定位与相对前作的新增贡献

已有工作边界（不得重述为核心创新）：

- 有限数据 Koopman 误差界（Nüske 等）、闭环保证综述（Strässer et al., Annu. Rev. Control 2026，论文已引用 `strasser2026overview`）——**因此"给出闭环界"本身不是新贡献**。
- input transformation Koopman MPC（Cibulka/Korda/Haniš 2025）、control-aware embedding（Uchida & Duraisamy 2023）。

**本路线的可辩护新增点（试点，待 S7 后仍成立才保留）：**

1. **显式执行器接口分解**：把"上位机虚拟输入 $v$"与"实际执行器指令 $a=Gv$"分离，并**显式保留 $G$ 的零空间分量 $a_\perp\in\ker G$**（其物理含义为共模/张紧模式，不被 $v$ 直接控制但门控动力学）。
2. **闭环界对接口缺陷定价**：界显式依赖
   `δ = 前馈不可达残差`（G2）、`β = 零空间/冗余执行影响`（A9）。这是现有 Koopman 跟踪界未显式给出的项。
3. **误差项分离**（G1/G4）：$\varepsilon\le\varepsilon_{\text{enc}}+\varepsilon_{\text{data}}+\varepsilon_{\text{hist}}$，其中 $\varepsilon_{\text{hist}}$ 对应部分可观测下的 history 截断误差。
4. **修复已验证缺陷**：用 Lyapunov metric 取代错误的"Schur ⇒ $\|A_{cl}\|<1$"推理（Main34.tex L719–737）。

> 若 S7 后发现第 1–3 点中任一项可与已有工作一一对应，则该点降级为"已知"，仅保留第 4 点作为 rigor 修正；届时回到 S4/S5 重新生成。

---

## 2. 设定与记号

真实系统（两平台共享接口层，但不共享机械结构）：

$$
x_{k+1}=F(x_k,u_k),\qquad a_k = G v_k + a_{\perp,k}\in\mathbb{R}^{m_a},\qquad u_k = a_k,\qquad a_{\perp,k}\in\operatorname{range}(G)^\perp .
$$

- P1（Geomatric Touch，3-DOF 刚体臂）：$v=u\in\mathbb{R}^3$，$G=I_3$，$\operatorname{range}(G)^\perp=\{0\}$，故 $a_\perp=0$。
- P2（四绳欠驱动软臂）：$v=(dx,dy)\in\mathbb{R}^2$，$G\in\mathbb{R}^{4\times2}$ 为固定差动映射 $(R,L,D,U)=(+dx,-dx,-dy,+dy)$，$\operatorname{rank}G=2$（**满列秩，$\ker G=\{0\}$**）；未被 $v$ 指令的张紧/共模偏置 $a_\perp$ 落在 $\operatorname{range}(G)^\perp\subset\mathbb{R}^{4}$（维数 $m_a-m=2$），由下位机设定并承载张紧/松弛模式。

History 与 lifting（论文现有）：

$$
X_k=[x_{k-P+1}^\top,\dots,x_k^\top]^\top,\quad z_k=g_\theta(X_k)=[x_k;h_k]\in\mathbb{R}^d,\quad h_k\in\mathbb{R}^{d-n}.
$$

提升线性模型（接口显式化）：

$$
z_{k+1}=A z_k + B\,G\,v_k + B\,a_{\perp,k} + w_k,\qquad
w_k := z_{k+1}-(Az_k+B a_k).
\tag{M}
$$

记 $B_G := B G\in\mathbb{R}^{d\times m}$（P2 时 $m=2$）。$B_G^\dagger$ 为 Moore–Penrose 伪逆，$P_{G}:=I-B_G B_G^\dagger$ 为到 $\operatorname{range}(B_G)^\perp$ 的正交投影。

参考轨迹 $\{z_k^{\mathrm{ref}}\}$ 由同一编码器作用于参考 history 窗口得到（论文现有）。

控制器（论文现有，接口显式化后）：

$$
v_k=v_{\mathrm{ff},k}+v_{\mathrm{fb},k},\qquad
v_{\mathrm{ff},k}=B_G^\dagger\!\left(z^{\mathrm{ref}}_{k+1}-A z^{\mathrm{ref}}_k\right),\qquad
v_{\mathrm{fb},k}=-K_c\,e^z_k,
$$
$e^z_k:=z_k-z^{\mathrm{ref}}_k$，$A_{cl}:=A-B_G K_c$，$K_c=K_c^\top\!$-由 $(\mA,\mB_G)$ 的 DARE 得到。

---

## 3. 假设

**A1（可控性）** $(\mA,\mB_G)$ 可稳，$(\mA,\mQ^{1/2})$ 可检，$Q\succeq0$，$R\succ0$。由此 DARE 有唯一解 $P\succ0$，且 $K_c=(\mR+\mB_G^\top \mP \mB_G)^{-1}\mB_G^\top \mP \mA$ 使 $A_{cl}$ Schur 稳定（**注意：不假设 $\|A_{cl}\|<1$**）。

**A2（有界建模残差）** $\|w_k\|\le\varepsilon$ 对所有 $k\ge0$（korda2018linear；可由验证集估计）。

**A3（有界未指令执行分量）** $\|a_{\perp,k}\|\le a_{\max}$ 对所有 $k$。P1 取 $a_{\max}=0$。（P2 中该量对应张紧模式偏离，可为慢变化或受下位机限幅约束。）

**A4（参考前馈可达性）** 存在有限 $\delta\ge0$ 使 $\big\|P_G\,(z^{\mathrm{ref}}_{k+1}-A z^{\mathrm{ref}}_k)\big\|\le\delta$ 对所有 $k$。$\delta=0$ 当且仅当参考差分落在 $\operatorname{range}(B_G)$ 内（可达参考）。

**A5（有界初值）** $\|e^z_0\|<\infty$。

> 说明：A3/A4 是本路线相对标准 UUB 的**新增结构假设**，分别对应 A9（未指令执行分量）与 G2（前馈不可达）。A1 移除了原定理中错误的 $\|A_{cl}\|<1$ 附加假设。

---

## 4. 定理 1（修正的闭环跟踪界，Lyapunov 形式）

**陈述.** 在 A1–A5 下，对由 (M) 与上述控制律构成的闭环，定义

$$
\lambda \;=\; \frac{\lambda_{\min}\!\big(Q+K_c^\top R K_c\big)}{\lambda_{\max}(P)}\;\in(0,1],
\qquad
D \;=\; \varepsilon+\|B\|\,a_{\max}+\delta .
$$

则闭环 lifted 跟踪误差满足

$$
\|e^z_k\|\;\le\;
\sqrt{\frac{\lambda_{\max}(P)}{\lambda_{\min}(P)}}\;\big(1-\lambda\big)^{k/2}\|e^z_0\|
\;+\;
\sqrt{\frac{\lambda_{\max}(P)}{\lambda_{\min}(P)}}\;\frac{D}{1-\sqrt{1-\lambda}} .
\tag{T1}
$$

进而物理状态跟踪误差满足 $\|x_k-x^{\mathrm{ref}}_k\|=\|\mC e^z_k\|\le\|e^z_k\|$（$\|\mC\|=1$），故

$$
\limsup_{k\to\infty}\|x_k-x^{\mathrm{ref}}_k\|
\;\le\;
\sqrt{\frac{\lambda_{\max}(P)}{\lambda_{\min}(P)}}\;\frac{\varepsilon+\|B\|a_{\max}+\delta}{1-\sqrt{1-\lambda}} .
\tag{T1'}
$$

**证明骨架.**

1. **误差动力学.** 将 $v_k$ 代入 (M)，用 $B_G=B G$，并记 $e^z_k=z_k-z^{\mathrm{ref}}_k$：
   $$
   e^z_{k+1}
   = A_{cl} e^z_k
     \underbrace{+\,w_k}_{\text{建模残差}}
     \underbrace{+\,B\,a_{\perp,k}}_{(\text{i})\ \text{未指令执行}}
     \underbrace{-\,P_G\,(z^{\mathrm{ref}}_{k+1}-A z^{\mathrm{ref}}_k)}_{(\text{ii})\ \text{前馈不可达残差}} .
   \tag{E}
   $$
   （推导：$B_G B_G^\dagger$ 是到 $\operatorname{range}(B_G)$ 的正交投影，故 $B_G B_G^\dagger d = d - P_G d$；参考项 $Az^{\mathrm{ref}}_k-z^{\mathrm{ref}}_{k+1}$ 与 $B_G B_G^\dagger(z^{\mathrm{ref}}_{k+1}-Az^{\mathrm{ref}}_k)$ 合并即得 $(ii)$。**注意：原论文 (L732–737) 遗漏了 $(ii)$。**）

2. **DARE 恒等式.** 由 $A_{cl}=A-B_G K_c$ 与 DARE（$K_c=(\mR+\mB_G^\top \mP\mB_G)^{-1}\mB_G^\top\mP\mA$）可得精确恒等式
   $$
   A_{cl}^\top P A_{cl}=P-\big(Q+K_c^\top R K_c\big)\;\preceq\;(1-\lambda)\,P .
   \tag{†}
   $$
   （展开 $P-(A-B_GK_c)^\top P(A-B_GK_c)$ 并用 $K_c^\top(R+B_G^\top P B_G)K_c=K_c^\top B_G^\top P A$ 即得；已代数核对。）

3. **Lyapunov 递推.** 取 $V_k=(e^z_k)^\top P e^z_k$。由 (E)、(†) 及 $P$-范数的三角不等式
   $\sqrt{(u+v)^\top P(u+v)}\le\sqrt{u^\top P u}+\sqrt{v^\top P v}$：
   $$
   V_{k+1}^{1/2}\le \sqrt{1-\lambda}\,V_k^{1/2}+\sqrt{\lambda_{\max}(P)}\,\|d_k\|,\qquad \|d_k\|\le D .
   $$

4. **迭代.** 递推 $V_k^{1/2}\le(1-\lambda)^{k/2}V_0^{1/2}+\sqrt{\lambda_{\max}(P)}\,D\sum_{i=0}^{k-1}(1-\lambda)^{i/2}$，几何和收敛；再用
   $\sqrt{\lambda_{\min}(P)}\,\|e^z_k\|\le V_k^{1/2}\le\sqrt{\lambda_{\max}(P)}\,\|e^z_k\|$ 得 (T1)，(T1') 取 $\limsup$ 得上界。$\square$

**与原定理的差异.** 原式 $\varepsilon/(1-\|A_{cl}\|)$ 依赖错误附加假设且量为负时无意义；T1 对任意 Schur $A_{cl}$ 成立，常数由 $(P,Q,R,K_c)$ 决定，永不出现 $1-\|A_{cl}\|$ 这种可能 $\le0$ 的分母。

---

## 5. 推论

**推论 1（接口/冗余定价）.** 在 T1 中：
- (a) 若 $G$ 满列秩且参考差分落在 $\operatorname{range}(B_G)$，则 $\delta=0$，前馈项消失；
- (b) 若存在未被指令的执行器偏置 $a_\perp\in\operatorname{range}(G)^\perp$（维数 $m_a-m$）且其对动力学有影响（$B a_\perp\neq0$），则该项以 $\|B\|a_{\max}$ 进入界——**未指令执行冗余被显式计价**；
- (c) 物理状态界与 lifted 界常数比为 $\sqrt{\lambda_{\max}/\lambda_{\min}}$，度量了 lifting 的"各向异性"。

推论 1(b) 是本路线的物理结构落点：P2 的共模/张紧方向不被 $v$ 控制，却以 $a_{\max}$ 上界进入闭环界；若张紧模式可由下位机稳定锁定（$a_{\max}\to0$），界相应收紧。

**推论 2（误差项分离，G1/G4）.** 若 $\|w_k\|\le\varepsilon_{\text{enc}}+\varepsilon_{\text{data}}+\varepsilon_{\text{hist}}$，其中
$\varepsilon_{\text{enc}}$ 为编码器逼近误差、
$\varepsilon_{\text{data}}$ 为有限样本 EDMD/ridge 估计误差（Nüske 类）、
$\varepsilon_{\text{hist}}$ 为部分可观测下 history 截断（memory）误差，
则 T1/T1' 中的 $\varepsilon$ 应替换为该和。$\varepsilon_{\text{hist}}$ 对 P2（仅 2D 光点、非全状态）一般非零，对 P1（全状态）可近似为 0。

---

## 6. S7 Proof Audit（反例与边界检查）

**C1（原定理反例，已验证）.** $\mA=\begin{bmatrix}0.95&3\\0&0.95\end{bmatrix}$：$\rho(\mA)=0.95<1$ 但 $\|\mA\|_2\approx3.2755>1$。原 (L721) 界 $\varepsilon/(1-3.2755)$ 为负，无意义。**结论：原定理不成立；T1 修复。**

**C2（Schur ⇏ 范数<1，一般性）.** 任一非正规 Schur 矩阵（如 Jordan 块 $\lambda I+N$，$|\lambda|<1$，$\|N\|>\sqrt{1-|\lambda|^2}$）均构成反例。$\|A_{cl}\|<1$ 是比 Schur 更强的、且对 LQR 一般不成立的假设。

**C3（前馈不可达不可忽略，G2）.** 取 $B_G=\begin{bmatrix}1\\0\end{bmatrix}$，参考差分 $d_k=\begin{bmatrix}0\\1\end{bmatrix}$（正交于 $\operatorname{range}B_G$），则 $P_G d_k=d_k$，$\delta=1$。若忽略 $(ii)$，误差动力学缺一常值激励，闭环无法收敛到参考；T1 的 $\delta$ 项正确给出非零 UUB 半径。

**C4（未指令方向影响边界）.** 若 $B a_\perp=0$（偏置方向不影响动力学），则 $\beta=0$，即使 $a_\perp\neq0$ 也不进入界——与推论 1(b) 一致；说明定价的是"未指令执行偏置 × 动力学耦合"，而非单纯执行器冗余。

**C9（数值验证，S8 已完成）.** 以非正规 $\mA$（$\rho=0.9$、$\|\mA\|_2=2.37$）与 LQR 闭环 $A_{cl}$（$\rho=0.32$、$\|A_{cl}\|_2=1.1123$）验证：(1) DARE 恒等式残差 $\approx6.8\times10^{-15}$；(2) 原界分母 $1-\|A_{cl}\|=-0.1123<0$（原式无意义）；(3) 仿真最坏 $\|e^z\|=0.225\le$ T1 半径 $1.130$；(4) T1 半径随 $D$ 严格单调；(5) 省略前馈不可达项得到假零稳态、保留则稳态偏移 $10.6$（$\delta$ 项必要）；(6) P2 型 $G$（注入、$\ker G=\{0\}$）下未指令偏置 $a_\perp\in\operatorname{range}(G)^\perp$ 满足 $G^\top a_\perp\approx1.1\times10^{-16}$，且 $B a_\perp\ne0$ 时 $\beta$ 进入界、$B a_\perp=0$ 时 $\beta=0$。脚本：`C:\Users\12187\AppData\Local\Temp\opencode\s8_verify_t1.py`（项目解释器 `edmddl2`）。

**C5（退化一致性）.** $\varepsilon=\beta=\delta=0$ 时 (T1') 给 0，退化为渐近精确跟踪；与标准结果一致。$Q\to0$ 时 $\lambda\to0$，界 $\to\infty$，与"无状态惩罚"一致（预期且非缺陷）。

**C6（常数有效区间）.** $\lambda\in(0,1]\Rightarrow\sqrt{1-\lambda}\in[0,1)$，分母 $1-\sqrt{1-\lambda}>0$ 恒成立；无除零风险。

**C7（守恒/单位）.** $D$ 与 $e^z$ 同量纲（均为 lifted 状态单位）；$\sqrt{\lambda_{\max}/\lambda_{\min}}$ 无量纲；T1' 与 $x$ 同量纲（因 $\mC$ 为选择矩阵）。✓

**C8（未决）.** A3 的 $a_{\max}$ 对 P2 的可辨识/可界性尚未从数据确认；$\varepsilon_{\text{hist}}$ 的显式界尚未构造；$P$ 的保守性（$\lambda$ 可能很小）未评估。→ 进入 S8 需数据侧最小验证。

---

## 7. S7 结论与下一步

- 修正定理（T1/T1'）在数学上自洽，修复了已验证的 Schur 缺陷，并把 G2/A9 显式纳入。
- **尚不能宣称创新成立**：C8 未决项（尤其 A3 的物理可界性与 $\varepsilon_{\text{hist}}$ 界）决定组合路线能否成立。
- 下一步（S8，最小数据验证，代码仍冻结）：
  1. 用 P1/P2 已有冻结 checkpoint / 验证数据估计 $\varepsilon_{\text{data}},\varepsilon_{\text{enc}}$ 经验值；
  2. 检查 P2 数据中是否存在张紧/松弛模式代理量，用于界定 $a_{\max}$ 是否可估；
  3. ~~最小数值仿真验证 T1~~ **已完成**（见 C9）：T1 随 $D$ 单调、比原式有意义，且原式在 $\|A_{cl}\|>1$ 时失效已复现；
  4. 若 A3 不可界且 $\|B a_\perp\|=0$（C4），则组合路线的 A9 载体失效，回退为"纯 rigor 修正 + A2/A7"。

---

## 8. S8 数据侧发现（2026-09-28）与对 A9 载体的修正

> 本节是对 §3（A3）与 §5（推论 1b）的**追加修订**，不改写上文以保留审计轨迹。

### 8.1 数据与模型盘点（`数据备份/` 与 `deploy/`）

| 项 | 事实 |
|---|---|
| P1 处理数据 | `x` (74655/19909/4976, **6**)，`u` (…, **3**)，全状态（位置+速度）；范围 $x\in[-16.6,11.6]$，$u\in[-2.6,5.7]$ |
| P1 checkpoint | **不存在**（`结果备份/` 为空，`results/` 不存在）→ P1 的 $\varepsilon$ 无法从既有 checkpoint 估计 |
| P2 处理数据 | `x` (21000/6000/3000, **2**)，`u` (…, **2**)；`x` **仅 2D 光点**，**无速度、无张力、无模式标签**；原始 npz 同样仅 `t,x(2),u(2)` |
| P2 部署 checkpoint（唯一可用） | `koopman_A`(10,10)、`koopman_B`(10,2)、**`spectral_radius=2.0878>1`**（模型本身不稳定，复现 INV1 分叉违规）；`metadata.history_length=4` 与 `config=8` 不一致（ALN-010 残余） |

### 8.2 平台2物理接口（`软控逻辑.txt` V3.6）关键事实

- 输入为**整数脉冲** `(dx,dy)`，$|u_{\max}|=V_{\max}\times(T_s-0.05)=2000\times0.15=\mathbf{300}$ 步；数据 $u\in[-68,61]$ 在其内。
- 四绳为两对差动（L/R、U/D），下位机**只执行差动动作**；**共模（R+L、U+D 同向）从不下发**。
- 张紧由**初始标定（临界张紧法）保证**，工作空间内**假设**绳索始终张紧；**无张力传感器、无运行时模式标签**。

### 8.3 对 A9 载体的直接后果（关键）

- 原 A9 假设"存在未被 $v$ 指令的执行器偏置 $a_\perp\in\operatorname{range}(G)^\perp$"。但在 P2 中，**共模方向根本不被驱动，故 $a_\perp=0$（按设计）**。
- 因此 §3 的 **A3（有界未指令偏置）既不可从数据估计，也无独立物理驱动源**；$\beta=\|B\|a_{\max}$ 退化为 0（C4 的"无影响"分支）。
- 张紧实质是**有效性域（taut regime）条件**，而非有界输入扰动：模型仅在张紧域有效，松弛→模型失配（是域外失效，不是有界 $a_\perp$）。
- **结论：组合路线中 A9 的"未指令张紧偏置定价"载体不成立。**

### 8.4 可保留 / 可替换的接口结构

- (i) **输入量化 + 饱和**：$q(v)=v+\varepsilon_q$，$|\varepsilon_q|\le \Delta/2=0.5$ 步，$\|B\varepsilon_q\|\le\|B\|\sqrt{m}/2$，且 $|v|\le300$。**可估、可界**，可直接进入 $D$。但属 A3（已因"标准量化理论"降级），单独作创新不足。
- (ii) **有效性域 / 张紧 regime 条件**：把定理改为"在张紧域 $\Phi$ 内成立，并给出离开 $\Phi$ 的检测条件"。物理真实，但邻接 A4（switched/mode，已因通用形式被 kill）；**只有给出非 switched 模型的"界 + 域"结构才算新**。
- (iii) **回退**：保留 rigor 骨架（T1 仍成立且必要），A9 从"物理载体"降级为"量化/饱和接口项 + 有效性域注记"；物理载体改用 A2/A7。

### 8.5 S8 判定

- C8 的"$a_{\max}$ 可界性"判定为 **否**（A9 原载体失效）。
- "$\varepsilon$ 经验估计"：P1 不可行（无 checkpoint）；P2 仅部署 checkpoint（且 $\rho>1$、$history$ 不一致），需重建模型栈后方可尝试。
- 组合路线需要**局部调整**：rigor 骨架保留；A9 载体替换为 (i)+(ii) 或改用 A2/A7。这是一个需用户确认的方向微调（C 级）。

---

## 附：与论文正文的映射（供阶段③落地，不在本阶段改正文）

| 论文位置 | 现状 | 本路线改动（阶段③） |
|---|---|---|
| Sec. II 系统 (L154–203) | $x_{k+1}=F(x_k,u_k)$ | 引入接口 $a=Gv+a_\perp$ |
| Sec. IV 控制器 (L639–699) | 直接对 $u$；$B^\dagger$ | 改为 $v$ 与 $B_G$，前馈用 $B_G^\dagger$ |
| Thm 1 (L717–738) | 错误 Schur/范数 | 替换为 T1（Lyapunov 形式）+ 推论 1/2 |
| Sec. V 实验 (L743) | 空 | 两平台闭环跟踪 + 界验证 |
