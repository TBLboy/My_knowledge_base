# 阶段② S6 Theory Construction v0.2（组合路线；载体替换为量化/饱和接口 + 有效性域）

> 状态：**candidate theory**，未经验证；代码/论文正文未修改。
> 本文件替代 `phase2_theory_construction_v0.1.md` 的**物理载体**（A9 已证不成立）；v0.1 的 rigor 骨架与 S7 审查保留为审计轨迹。
> 取向（DEC-016 + DEC-017）：组合路线 = T1 rigor 骨架 + **量化/饱和执行器接口项** + **张紧有效性域条件** + P1/P2 两平台实验。

---

## 1. 相对 v0.1 的变更

| 项 | v0.1 | v0.2 |
|---|---|---|
| 物理载体 | A9：未指令张紧偏置 $a_\perp\in\operatorname{range}(G)^\perp$ | **证明不成立**（P2 共模从不下发，$a_\perp=0$ 按设计；见 S8 §8.3） |
| 新载体 | — | **执行器接口量化 + 饱和**（P2 整数脉冲，$\Delta=1$，$|u|\le300$）；**张紧有效性域** $\Phi$ |
| rigor 骨架 | T1（Lyapunov 形式） | **不变**（仍必要） |
| 新增定理 | — | **定理 2：有效域内条件性保证 + 离域检测** |

---

## 2. 模型（接口显式化，量化/饱和）

真实系统与接口：

$$
x_{k+1}=F(x_k,u_k),\qquad
a_k = \mathcal{Q}(v_k) \;=\; \operatorname{clip}_{[-a_{\max},a_{\max}]}\!\big(\Delta\cdot\operatorname{round}(v_k/\Delta)\big),
$$

其中 $v_k$ 为控制器计算的实值命令，$\mathcal{Q}$ 为**量化 + 饱和**复合。对 P2：$\Delta=1$ 步（整数脉冲），$a_{\max}=300$ 步；对 P1：$\Delta$ 为关节指令分辨率（可近似 0），$a_{\max}$ 为关节限幅。

写 $\mathcal{Q}(v)=v+e^Q$，则

$$
\|e^Q_k\|\;\le\;\frac{\Delta\sqrt{m}}{2}\;+\;\underbrace{\big\|\operatorname{clip}(v_k)-v_k\big\|}_{\text{饱和超限，若在域内则为 }0}.
$$

**设计选择（进入定理）**：控制器输出在送入执行器前先**主动限幅到 $[-a_{\max},a_{\max}]$**，故饱和项为 0，只剩量化项：

$$
\|e^Q_k\|\le e_{\max}:=\frac{\Delta\sqrt{m}}{2}\quad(\text{P2: }\Delta=1,m=2\Rightarrow e_{\max}=\tfrac{\sqrt2}{2}\approx0.707\text{ 步}).
$$

其余同 v0.1：$z_k=g_\theta(X_k)=[x_k;h_k]$，$z_{k+1}=Az_k+B a_k+w_k$。**记号说明（回应独立复核 C-5）**：已辨识模型的输入矩阵本身即以 2D 虚拟指令 $(dx,dy)$ 为输入（差动映射已并入模型），故本文件中 **$B\equiv B_G$**，量化通道数 **$m=2$** 指虚拟指令通道数（非 4 个电机通道）；$e_{\max}=\Delta\sqrt m/2=\sqrt2/2\approx0.707$ 步。

控制器（同 v0.1）：

$$
v_{\mathrm{ff},k}=B_G^\dagger\!\left(z^{\mathrm{ref}}_{k+1}-Az^{\mathrm{ref}}_k\right),\quad
v_{\mathrm{fb},k}=-K_c e^z_k,\quad
A_{cl}=A-B_GK_c .
$$

---

## 3. 假设

- **A1** 同 v0.1：$(\mA,\mB_G)$ 可稳、$(\mA,\mQ^{1/2})$ 可检，$Q\succeq0,R\succ0$，$P\succ0$ 来自 DARE，$K_c$ 为 LQR 增益；**且 $Q+K_c^\top RK_c\succ0$（等价条件：$Q\succ0$ 或 $B_G$ 满列秩），以保证 $\lambda>0$**。**不假设 $\|A_{cl}\|<1$**。（独立复核 C-4：若只允许 $Q\succeq0$ 且 $B_G$ 降秩，$\lambda=0$，T1′ 分母为 0、界无定义。）
- **A2** 同 v0.1：$\|w_k\|\le\varepsilon$。
- **A4** 同 v0.1：参考前馈不可达残差 $\|P_G(z^{\mathrm{ref}}_{k+1}-Az^{\mathrm{ref}}_k)\|\le\delta$。
- **A5** 同 v0.1：$\|e^z_0\|<\infty$。
- **A3′（新，替代 v0.1 的 A3）** 执行器接口量化误差有界：$\|e^Q_k\|\le e_{\max}=\Delta\sqrt m/2$（饱和已由主动限幅消除）。
- **A6（有效域）** 存在紧凑张紧域 $\Phi\subset\mathbb{R}^n$，在其内 Koopman 模型 (M) 与残差界 $A2$ 成立；有效域外不保证。

---

## 4. 定理 1′（修正的闭环跟踪界，量化接口）

**陈述.** 在 A1、A2、A3′、A4、A5、**A6** 下（A6 提供 A2 成立的有效域），

$$
\lambda=\frac{\lambda_{\min}(Q+K_c^\top RK_c)}{\lambda_{\max}(P)}\in(0,1],\qquad
D=\varepsilon+\|B\|\,e_{\max}+\delta=\varepsilon+\|B\|\frac{\Delta\sqrt m}{2}+\delta .
$$

则

$$
\|e^z_k\|\le\sqrt{\frac{\lambda_{\max}(P)}{\lambda_{\min}(P)}}\,(1-\lambda)^{k/2}\|e^z_0\|
+\sqrt{\frac{\lambda_{\max}(P)}{\lambda_{\min}(P)}}\,\frac{D}{1-\sqrt{1-\lambda}} .
\tag{T1'}
$$

**证明骨架.** 与 v0.1 相同，仅扰动项变化：将 $a_k=v_k+e^Q_k$ 代入得

$$
e^z_{k+1}=A_{cl}e^z_k+\underbrace{w_k+B e^Q_k-P_G(z^{\mathrm{ref}}_{k+1}-Az^{\mathrm{ref}}_k)}_{d_k},\qquad
\|d_k\|\le\varepsilon+\|B\|e_{\max}+\delta=D .
$$

DARE 恒等式 $A_{cl}^\top PA_{cl}=P-(Q+K_c^\top RK_c)\preceq(1-\lambda)P$、$P$-范数三角不等式与几何和迭代同 v0.1。$\square$

**与原论文的差异（不变）.** 原式 $\varepsilon/(1-\|A_{cl}\|)$ 依赖错误假设；T1′ 对任意 Schur $A_{cl}$ 成立。

---

## 5. 命题 1（有效域内的条件性保证与离域监控）

> 独立复核指出：原"定理 2"实质是 T1′ 在 $k<\tau$ 上的限定 + 一个残差监控规则，**不构成独立定理**，故降级为**命题**，并显式定义 $\Phi$。

**陈述.** 设有效域 $\Phi\subset\mathbb{R}^n$ 为**设计指定**集合（P2：由临界张紧标定确定的张紧工作包络；P1：关节/速度限位内的包络），$\tau:=\inf\{k:x_k\notin\Phi\}$。若在 $k<\tau$ 上 $x_k\in\Phi$，则 T1′ 成立。定义在线残差监控量

$$
r_k:=\big\|\,\hat z_{k+1}-(A z_k+B a_k)\,\big\|,\qquad \hat z_{k+1}=g_\theta(X_{k+1}),
$$

若 $r_k>\varepsilon$（验证集标定阈值）或 $x_k$ 越出 $\Phi$ 的名义包络，则**声明保证失效**并切换安全模式。

**说明（非定理级断言）.** (a) $k<\tau$ 部分是 T1′ 的直接限制；(b) $r_k=\|w_k\|$，故 $r_k>\varepsilon$ 表示 A2 在当前样本被违反——这是**充分但非必要**的离域判据（离域也可能在 $\|w_k\|\le\varepsilon$ 时发生）；(c) $\Phi$ 需在阶段③用标定/数据具体化，本阶段仅声明其存在。因此本命题应视为**适用范围声明 + 监控规则**，不是新的稳定性定理。

---

## 6. 各项可估性（对 S8 的回应）

| 项 | 来源 | 可估性 |
|---|---|---|
| $\Delta$ | P2：1 步（整数脉冲）；P1：指令分辨率 | 已知（规格） |
| $e_{\max}$ | $\Delta\sqrt m/2$；P2 $\approx0.707$ 步 | **可算** |
| $a_{\max}$ | $V_{\max}(T_s-0.05)=300$ 步（P2） | 已知（规格） |
| $\|B\|$ | 冻结 checkpoint 的 $\mB$ | 可算（P2 部署 ckpt 有 $\mB(10,2)$；P1 无 ckpt） |
| $\delta$ | 参考差分在 $\operatorname{range}(B_G)^\perp$ 的投影 | 可算（给定参考与 $\mB_G$） |
| $\varepsilon$ | 验证集一阶残差 $\max r_k$ | P2 需重建模型栈；P1 无 ckpt，暂不可估 |
| $\lambda$ | $(P,Q,R,K_c)$ 特征值 | 可算 |

---

## 7. 推论

- **推论 1（接口定价，修订）.** 界显式依赖量化接口 $\|B\|\Delta\sqrt m/2$ 与前馈不可达 $\delta$。推论 1(a)（$\delta=0$ 当参考可达）不变；v0.1 的推论 1(b)（零空间定价）**作废**，替换为"量化定价"。
- **推论 2（误差分离）.** 同 v0.1：$\varepsilon\le\varepsilon_{\text{enc}}+\varepsilon_{\text{data}}+\varepsilon_{\text{hist}}$（P2 的 $\varepsilon_{\text{hist}}$ 一般非零）。
- **推论 3（域条件）.** 若系统离开张紧域，保证作废；T1′ 是**条件性**的（限域内）。

---

## 8. S7 复审增补

- **C1/C2/C3/C5/C6/C7/C9**：v0.1 的数学与数值审查对 T1′ 仍成立（仅 $D$ 的构成由 $\|B\|a_{\max}$ 改为 $\|B\|e_{\max}$）。
- **C10（已评估）**：$e_{\max}=0.707$ 步，P2 $\|B\|_2\,e_{\max}=0.014$（谱范数）→ 量化项对 P2 可忽略。
- **C11（未决）**：命题 1 的离域检测阈值依赖 $\varepsilon$ 的验证集标定；分布漂移会误报/漏报。
- **C4（修订）**：v0.1 的"零空间耦合"边界作废；替换为"若 $\Delta\to0$ 且 $\delta\to0$，T1′ 退化为纯建模误差界"。

### 8.1 独立复核结论（verification-reviewer，2026-09-28）

- **CONFIRMED**：C-1（原定理为假，反例成立）、C-2（误差动力学须补 $P_G$ 项）、C-3（DARE 恒等式）、C-4（T1′ 常数与 $\lambda$ 正确、不需 $\|A_{cl}\|<1$）。
- **已修正的复核发现**：
  1. A1 补入 $\lambda>0$ 前提（$Q\succ0$ 或 $B_G$ 满列秩）；
  2. T1′ 假设列表补入 A6；
  3. "定理 2"降级为**命题 1**，显式定义 $\Phi$、说明检测是充分非必要；
  4. 记号统一 $B\equiv B_G$，$m=2$（虚拟指令通道）；
  5. 脚本改用**谱范数**（原 `np.linalg.norm` 对二维阵返回 Frobenius）：2×2 例 $\|\mA\|_2=2.3454$、P2 $\|\mA\|_2=25.52$、$\|\mB\|_2=0.0199$。
- **数值复算（本次已重跑）**：2×2 例 DARE 残差 $6.8\times10^{-15}$、$\|A_{cl}\|_2=1.1084$（原界分母 $-0.1084<0$）；P2 模型 $\rho(\mA)=2.0878$、PBH 秩 10（可稳）、$\rho(A_{cl})=0.999958<1$（勉强 Schur）、$\lambda=3.6\times10^{-11}$、$\text{cond}(P)=2.2\times10^{10}$、T1′ 常数 $\approx8.4\times10^{15}$（空泛）。
- **新发现（复核 C-5 缺陷 2）**：P2 上 `solve_discrete_are` 的 **DARE 残差 $\approx1.3\times10^{4}$（远非 ~0）** → 该病态模型的数值 LQR 解不可靠；进一步支持"必须先稳定化模型"（DEC-018）。
- **未完成**：数值证据尚未做 sha256 绑定归档；novelty delta（vs Strässer 2026 / Cibulka-Korda-Haniš 2025 / Nüske）仅元数据层检索，全文比对未做。
- **复核建议**：REVISE 后接受；TASK-004/GOAL-001 维持 implemented-unverified。

---

## 9. 与论文正文映射（阶段③）

| 论文位置 | v0.2 改动 |
|---|---|
| Sec. II | 增加执行器接口量化/饱和 $\mathcal{Q}$ |
| Sec. IV 控制器 | 控制器输出先限幅；$a_k=\mathcal{Q}(v_k)$ |
| Thm 1 | 替换为 T1′ + 定理 2（有效域 + 离域检测） |
| Sec. V 实验 | 两平台闭环跟踪 + $r_k$ 离域监控 + 量化/δ 项经验评估 |
