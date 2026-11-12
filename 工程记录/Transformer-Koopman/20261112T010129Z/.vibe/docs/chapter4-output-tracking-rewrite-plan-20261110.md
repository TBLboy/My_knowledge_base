# 第四章重构方案：从"参考对跟踪"改为"输出跟踪 MPC"

日期：2026-11-10
对象：`Transformer-Koopman/论文/新版本/Main.tex` 第四章 `Frozen-LTV Model Predictive Control`（IV-A / IV-B）及其附录 B、C。
状态：**历史草案，已被替代；不可作为当前实施依据。**

> 当前设计与证明路线见 [输出跟踪 Single-Freeze MPC 记录](specs/20261110-output-tracking-controller-proof-record.md)。下文保留历史内容；其中 A3′、见证参考对、参考编码、可选幅值项及 ISS 路线均不再采用。当前为输出跟踪 + 输入增量惩罚、同权终端代价、重复末端输入，证明采用 Route 0 有界性引理 + Route 1 移位值比较/平均性能界。论文尚未据此修改。

---

## 0. 一页摘要

**问题：** 当前 IV-A 的代价函数要求外部提供完整参考对 \((q_t^r,u_t^r)\)，其中 \(q_t^r\) 含历史输入缓存。但论文的任务定位是"给定期望轨迹、动力学未知、数据驱动控制"。真实场景（如机械臂）只给期望输出轨迹 \(x^r_t\)，既没有 \(u^r\)，也无法据此构造输入缓存参考。因此控制器输入接口与论文立论不一致，这是审稿人一定会抓住的硬伤。

**方案：** 控制器改为只吃 \(x^r_t\) 的输出跟踪 MPC：参考升维状态由同一编码器对参考窗口编码得到，代价只惩罚物理输出块（纯特征块权重置零），输入侧只保留增量惩罚与可选幅值惩罚。

**结论：** IV-A 改动局部、干净；**IV-B 不能靠符号替换沿用**——旧证明的 Lyapunov 函数本质是"全增广状态的 \(\Pi\)-范数误差"，新代价只约束输出，值函数不再支配状态误差，链条在终端下降和值比较两环断开。要闭合必须新增一个**提升可观测性假设**，并把结论降级为**输出误差的实用 ISS 界**。

---

## 1. 现状：模型与控制器（供无原文时对照）

### 1.1 历史条件化预测器（第三章，本次不改）

- 测量窗口：\(\mathcal X_k=\col(x_{k-P_h+1},\dots,x_k)\)
- 测量缓存：\(a_k=\col(x_{k-P_h+1},\dots,x_{k-1})\)
- 输入缓存：\(v_k=\col(u_{k-P_h+1},\dots,u_{k-1})\)
- 提升状态：\(z_k=G_\theta(\mathcal X_k)=\col(x_k,\ \psi_\theta(\mathcal X_k))\)，且 \(C_xz_k=x_k\)
- 增广状态：\(q_k=\col(z_k,a_k,v_k)\in\mathbb R^{s_q}\)，\(s_q=d+(P_h-1)(n+m)\)
- 递归预测器：

\[
F(q,u)=\col\Bigl(\mA(\vc(q))z+\mB(C_xz)u,\ \ S_xa+E_xC_xz,\ \ S_uv+E_uu\Bigr)
\]

- 冻结模型（\(\bar q\) 处系数）：

\[
p_{i+1|k}=M_{i|k}p_{i|k}+D_{i|k}u_{i|k},\quad
M_{i|k}=\begin{bmatrix}\bar\mA_{i|k}&0&0\\ E_xC_x&S_x&0\\ 0&0&S_u\end{bmatrix},\quad
D_{i|k}=\col(\bar\mB_{i|k},0,E_u)
\]

- 记号：\(E_z=\col(I_d,0,0)\) 取提升块；\(E_{\rm prev}\) 取输入缓存最后一格，因此 **\(E_{\rm prev}p_{i+1|k}=u_{i|k}\)**。
- 域与常数：\(\mathcal Q=\{q:\|q\|_\Pi\le M\}\)，\(\|w_k\|_\Pi\le\bar w\)，\(\|F(q,u)-F^{\rm fr}(q,u)\|_\Pi\le\bar\eta\)，\(\lambda M+b_u+\bar w\le M\)，\(\lambda_{\rm fr}M+b_u\le M\)。

### 1.2 当前控制器（待改）

代价：

\[
\ell_t(q,u)=\|q-q_t^r\|_\Pi^2+\|u-u_t^r\|_R^2+\bigl\|(u-E_{\rm prev}q)-(u_t^r-u_{t-1}^r)\bigr\|_S^2 \tag{30}
\]

参考假设（Assumption 2）：

\[
q_t^r\in\mathcal Q,\quad u_t^r\in\mathcal U,\quad E_{\rm prev}q_t^r=u_{t-1}^r,\quad \|F(q_t^r,u_t^r)-q_{t+1}^r\|_\Pi\le\bar d_{\rm ref} \tag{37}
\]

终端权重（由参考输入处的下降性推出，\(H_S=S^{1/2}E_{\rm prev}\Pi^{-1/2}\)，\(c_S=1+\|H_S\|_2^2\)）：

\[
\beta\ \ge\ \frac{c_S}{1-(1+\vartheta)\lambda^2},\qquad (1+\vartheta)\lambda^2<1 \tag{38}
\]

闭环结论（Theorem 1）：\(\|e_k\|_\Pi^2\le W_k\le\Xi_k\)，
\(\Xi_k=\mathsf A\rho^k\|e_0\|_\Pi^2+\mathsf B+\sum_{t=0}^{k-1}\rho^{k-1-t}(\varepsilon+\delta_t)\)，\(\rho=1-1/\mathsf A\)，最终得到全增广状态的实际指数跟踪半径。

### 1.3 为什么必须改

1. \(q^r_t\) 含输入缓存 \(v^r_t\)，没有 \(u^r\) 就无法构造；仅给 \(x^r\) 时 \(q^r_t\) 不是"给定数据"。
2. 若 \(u^r\) 又由同一个 Koopman 模型反解，则方法实际多了一层未声明的逆模型前馈，架构变成"期望轨迹 → 逆模型 → 参考输入 → 冻结 MPC"，与论文宣称的单层结构不符。
3. 审稿人必问：*How are the augmented-state and input references generated from the prescribed trajectory?* 现稿无答案。

---

## 2. 重构后的控制器（IV-A 目标形态）

### 2.1 参考构造（只用期望输出）

给定期望测量轨迹 \(x^r_{0:T}\)：

\[
\mathcal X_t^r=\col(x^r_{t-P_h+1},\dots,x^r_t),\qquad
z_t^r=G_\theta(\mathcal X_t^r),\qquad
C_xz_t^r=x^r_t
\]

- 不需要 \(u^r\)，不需要 \(v^r\)，不需要 \(q^r\)。
- 若只给部分输出（例如只有关节位置），把 \(C_x\) 换成输出选择矩阵 \(C_y\)，并对未给定的分量采用参考补全或直接输出跟踪（见 §6 待决问题 Q2）。

### 2.2 阶段代价

\[
\boxed{
\ell_t(p,u)=\|C_xE_z^\top p-x_t^r\|_{Q_x}^2+\|u-E_{\rm prev}p\|_S^2+\|u\|_R^2
}
\]

- 第一项：物理输出跟踪；等价写法 \(\|E_z^\top p-z_t^r\|_{\bar Q_z}^2\)，\(\bar Q_z=\operatorname{diag}(Q_x,0)\)，即**纯特征块权重置零**。
- 第二项：输入增量（在当前模型下等于 \(u_{i|k}-u_{i-1|k}\)，首步用实测上一输入）。
- 第三项：可选输入幅值正则。
- 建议权重：\(Q_x\succeq0,\ S\succ0,\ R\succeq0\)。\(R\) 取小或零，避免惩罚重力补偿类必需的非零维持输入。

### 2.3 优化问题

\[
\begin{aligned}
\min_{U}\quad
&\sum_{i=0}^{N-1}\ell_{k+i}(p_{i|k},u_{i|k})
+\|C_xE_z^\top p_{N|k}-x^r_{k+N}\|_{Q_f}^2\\
\text{s.t.}\quad
&p_{0|k}=q_k^E,\\
&p_{i+1|k}=M_{i|k}p_{i|k}+D_{i|k}u_{i|k},\\
&u_{i|k}\in\mathcal U,\quad i=0,\dots,N-1
\end{aligned}
\]

结构与原 (31) 相同，只有代价与终端项变化。

### 2.4 滚动实施与标称序列

\[
u_k=\hat u_{0|k},\qquad
\bar U_{k+1}=(\hat u_{1|k},\dots,\hat u_{N-1|k},\hat u_{N-1|k})
\]

尾部**重复最后输入**（不再接 \(u^r\)）。该移位保证可行性（\(\mathcal U\) 凸，重复元素仍在 \(\mathcal U\)），但**不自动给出稳定性**。

### 2.5 严格凸性（新的论证）

不再是"\(\Pi\) 罚输入缓存"，改为输入增量项：

\[
\Delta u_{i|k}=u_{i|k}-E_{\rm prev}p_{i|k}=u_{i|k}-u_{i-1|k}
\]

\(U\mapsto\{\Delta u_{i}\}_{i=0}^{N-1}\) 是单位对角下三角线性映射，故 \(S\succ0\) 时对任意非零 \(\Delta U\) 二次型严格正；配合 \(Q_x\succeq0,R\succeq0\) 得凝聚 Hessian 正定。

**必须注意：** 若 \(S=0\) 且 \(R=0\)，输出代价一般不能保证 Hessian 正定（输入可能有零代价方向）。

### 2.6 明确删除的条目

| 条目 | 处置 |
|---|---|
| \(q_t^r\)、\(u_t^r\)、\(v_t^r\) | 删除 |
| Assumption 2 的 \(E_{\rm prev}q_t^r=u^r_{t-1}\) | 删除 |
| \(c_S\)、式 (38) 的参考输入下降性 | 替换 |
| \(\tau_{\rm ref}\)、\(\bar d_{\rm ref}\) 的"给定参考对"语义 | 改为"见证对"，见 §3.3 |
| 附录 C 全部值比较构造 | 重建 |

---

## 3. 理论链条分析

### 3.1 旧证明的五环（环环相扣）

1. **域不变**：由 \(\lambda M+b_u+\bar w\le M\) 得 \(q_{k+1}^E\in\mathcal Q\)。
2. **首次更新一致 + 名义全程复现**：\(p_{i|k}(\bar U_k)=\bar q_{i|k}\)。
3. **移位比较**：\(\|\tilde q_j-p_{j+1}\|_\Pi\le d_j\)，\(d_j=\lambda^j\bar w+\bar\eta\sum\lambda^s\)（**与参考无关**）。
4. **终端下降**：在 \(u=u^r_t\) 处

\[
\ell_t(q,u_t^r)+\beta\|F(q,u_t^r)-q_{t+1}^r\|_\Pi^2-\beta\|q-q_t^r\|_\Pi^2\le\tau_{\rm ref}
\]

5. **值下降 + 值比较**：
\(W_{k+1}\le W_k-\|e_k\|_\Pi^2+\varepsilon+\delta_k\)，
\(W_k\le\mathsf A\|e_k\|_\Pi^2+\mathsf B\)。

### 3.2 换代价后哪里断

| 环 | 依赖 | 新方案下 | 判定 |
|---|---|---|---|
| 1 域不变 | 仅需 \(\lambda M+b_u+\bar w\le M\) | 不变 | **活** |
| 2 名义复现 | 仅需冻结构造 | 不变 | **活** |
| 3 移位比较 | 仅需模型常数 | 不变 | **活** |
| 4 终端下降 | 需要 \(u^r_t\) 处取值 + 沿参考流的耗散 | 无 \(u^r\) | **死** |
| 5 值下降/比较 | 需要 \(\ell\ge\|q-q^r\|^2_\Pi\) 提供状态误差下界 | 代价只含输出 | **死** |

**根本原因（一句话）：**

> 旧证明的 Lyapunov 函数是"全增广状态的 \(\Pi\)-范数误差"。新代价只惩罚输出的投影，而输出误差小并不意味着提升状态误差、缓存误差小；值函数不再支配收缩性论证所需的那个误差。

由此产生三处连锁失效：

- **(i) 下界缺失**：无法从 \(W_k\) 反推 \(\|e_k\|_\Pi\)，于是 §3.1 第 1 环失去来源（域不变不再由代价保证）。
- **(ii) 终端项失效**：\(\Pi\)-收缩不能直接转成"输出误差的收缩"，因为 \(\|C e\|\le\|C\Pi^{-1/2}\|\,\|e\|_\Pi\) 只是一侧不等式，反方向不成立。
- **(iii) 上界失效**：\(W_k\le\mathsf A\|e_k\|^2+\mathsf B\) 的构造需要一条**可行比较序列**，旧版正是参考输入序列。

### 3.3 补哪两块才能闭合

**A2′（见证对，仅用于证明，控制器不用）**
存在可行对 \((q_t^\dagger,u_t^\dagger)\)（\(u_t^\dagger\in\mathcal U,\ q_t^\dagger\in\mathcal Q\)）满足

\[
C_xE_z^\top q_t^\dagger=x_t^r,\qquad
\|F(q_t^\dagger,u_t^\dagger)-q_{t+1}^\dagger\|_\Pi\le\bar d_{\rm ref}
\]

即"参考输出是模型意义下近似可实现的"。\(\bar d_{\rm ref}\) 沿参考轨迹离线可算，是**可检验量**，不是外部输入。

**A3′（提升可观测性，新增，最关键）**
在分析域上，提升误差被输出误差控制：

\[
\|E_z^\top e\|_{\Pi_z}\le\gamma\,\|C_xE_z^\top e\|_2,\qquad \Pi_z=E_z^\top\Pi E_z
\]

含义：在 \(\mathcal Q\) 上，从测量输出可以"看见"提升状态。可在数据上核验：对编码器 Jacobian 在 \(\mathcal Q\) 上的最小奇异值取样，得到 \(\gamma\) 的一个有效上界。

**为什么要它：** 输出误差 →（A3′）提升误差；缓存误差由 \(u\in\mathcal U\) 与有界输出自动有界（缓存只是记账：\(a\) 存测量、\(v\) 存输入，二者都由信号本身界定）。三者合并才得到全状态误差，从而接回 \(\Pi\)-收缩。

### 3.4 闭合后的结论形态

设新代价下最优值 \(W_k\)，\(\rho=1-1/\mathsf A\)：

\[
W_{k+1}\le \rho W_k+\frac{\mathsf B}{\mathsf A}+\varepsilon+\delta_k
\]

配合 \(W_k\ge\lambda_{\min}(Q_x)\|x_k-x^r_k\|_2^2\)（取 \(i=0\) 步，\(p_{0|k}=q_k^E\)）：

\[
\boxed{
\limsup_{k\to\infty}\|x_k-x^r_k\|_2^2
\;\le\;
\frac{\mathsf B/\mathsf A+\varepsilon+\bar\delta}{(1-\rho)\,\lambda_{\min}(Q_x)}
}
\]

其中 \(\varepsilon\) 汇总重编码残差 \(\bar w\)、冻结偏差 \(\bar\eta\)、参考可实现性缺陷 \(\bar d_{\rm ref}\) 与输入增量预算。

**性质对照：**

| 项 | 旧结论 | 新结论 |
|---|---|---|
| 收敛对象 | 全增广状态 \(q_k^E\to q^r_t\) | **测量输出** \(x_k\to x^r_k\) |
| 收敛形式 | 实际指数跟踪（含速率 \(\rho\)） | **实用 ISS 界**（无速率声明） |
| 半径依赖 | 模型误差、冻结误差、参考缺陷 | 同左，另加可观测常数 \(\gamma\) |
| 零误差特例 | \(\bar w=\bar\eta=\bar d_{\rm ref}=0\) 时指数到零 | 同样成立，但只对输出 |
| 输入界（Cor. 1） | \(\|\hat u_{0|k}-u^r_k\|\) 有界（用 \(R\succ0\) 与 \(u^r\)） | 只能给 \(\|\hat u_{0|k}\|\) 或增量界，**不能给相对 \(u^r\) 的界** |

> **核心权衡：** 想要"全增广状态指数跟踪"，就必须把 \((q^r,u^r)\) 留在控制器接口里；想要"只给输出参考"，就只能得到输出层面的实用界。二者不可兼得。

---

## 4. 三条可选路线

| 路线 | 内容 | 理论强度 | 改动量 | 风险 |
|---|---|---|---|---|
| **A（推荐）** | 输出跟踪 + A2′见证 + A3′可观测性 | 实用 ISS（输出） | 中 | A3′ 可能不成立，需数据核验 \(\gamma\) |
| B | 保留 \((q^r,u^r)\)，只改措辞 | 保留指数跟踪 | 极小 | 与论文数据驱动定位冲突，审稿人不买 |
| C | 输出跟踪 + 在线稳态决策变量（人工参考 MPC） | ISS 到可达稳态邻域，理论最成熟 | 大 | 新增决策变量、终端等式约束，QP 结构变动 |

路线 C 的参照实现见 Wang–Yang–Pu–Manzie (arXiv:2208.12000) 的 KTMPC：在线优化可达稳态 \((z_s,u_s,y_s)\)，终端等式 \(\bar z(N)=z_s\)，配合约束收缩与两个 Lyapunov 函数给出递归可行性与 ISS。

---

## 5. 修改清单（文件级 / 公式级）

### 5.1 IV-A

| 位置 | 动作 |
|---|---|
| 参考段（现 "prescribed reference ... \(u^r_{-1}\) given"） | 重写为"给定 \(x^r_t\)，编码得 \(z^r_t\)" |
| (30) | 换为新阶段代价 |
| (31) | 换代价与终端项，其余不变 |
| (32)(33) | (33) 尾部改为重复最后输入 |
| Algorithm 1 | `Given` 去掉 reference input；移位行同步 |
| 凸性段 | 改为 \(S\succ0\) + 下三角论证 |

### 5.2 IV-B

| 位置 | 动作 |
|---|---|
| Assumption 1（域/模型） | **不动** |
| Assumption 2（参考一致性） | 替换为 A2′（见证对）+ 输出有界 |
| 新增 A3′ | 提升可观测性（放在 Assumption 2 之后） |
| \(c_S\) 与 (38) | 删除；给出新的终端权重条件（依赖 \(\lambda,\gamma,Q_f\)） |
| Theorem 1 | 重述：输出误差的实用 ISS + 递归可行；删除指数速率 |
| 证明 阶段 1–3 | **保留** |
| 证明 阶段 4（(43)） | 用 A2′ 见证对重写终端下降 |
| 证明 阶段 5（(44)(45)） | 用 \(\ell\ge\lambda_{\min}(Q_x)\|C e\|^2\) 重建值下降与上界 |
| Corollary 1 | (46) 变为定理的直接推论；(47) 改为 \(\|\hat u_{0|k}\|\) 或增量界 |

### 5.3 附录 B

| 编号 | 动作 |
|---|---|
| (56) Hessian | 按新代价（\(Q_x,S,R\)）重组 |
| (57) 冻结半径 \(D_i\) | 保留 |
| (58) \(d_j\) | 保留 |
| (59) \(\varepsilon\) 预算 | 保留主体，去掉 \(\tau_{\rm ref}\) 的旧定义 |
| (60) 代价连续性常数 \(L_\ell,L_f\) | 按新代价重算 |

### 5.4 附录 C

整体重建：\(b_i,\mathsf A,\mathsf B\) 与"值比较"链全部依赖"参考输入可行序列"，需改为基于见证对与输出代价的版本。

### 5.5 不需要动的部分

- 第三章全部（预测器、训练、收缩命题、附录 A）；
- 冻结机制、单次 nominal rollout、QP 结构；
- 域不变、名义复现、移位比较三环；
- 求解器次优性 \((\delta_k)\) 的处理框架。

---

## 6. 待决问题（需要拍板）

- **Q1 路线选择**：A（推荐）/ B / C。
- **Q2 参考是完整测量向量还是部分输出**：`x^r_t` 是否等于第三章编码所需的全部测量量？若只有关节位置，则需 \(C_y\) 选择矩阵，并决定未给定分量如何处理（补全 / 只跟踪可测部分）。这直接决定 A3′ 的形式。
- **Q3 权重取值约束**：是否接受 \(S\succ0,\ R=0\)（机械臂常见选择）？若 \(S=0\) 且 \(R=0\)，需另行保证 Hessian 正定。
- **Q4 是否加状态约束**：\(\mathcal Q\) 目前是分析域而非在线约束。新证明仍需"状态留在 \(\mathcal Q\)"（A3′ 依赖它）。是保持"假设 + 可检验充分条件"，还是显式加输出状态约束？
- **Q5 结论强度**：是否接受把 Theorem 1 从"全状态指数跟踪"降级为"输出实用 ISS"？

---

## 7. 参考文献

1. Z. M. Manaa, A. M. Abdallah, M. A. Abido, S. S. A. Ali, "Koopman-LQR Controller for Quadrotor UAVs from Data," IEEE Int. Conf. on Smart Mobility, 2024.（升维代价用 \(\bar Q=\operatorname{diag}(Q,0)\)，只罚物理状态块；输入不升维）
2. S. S. K. S. Narayanan, D. Tellez-Castro, S. Sutavani, U. Vaidya, "SE(3) Koopman-MPC: Data-driven Learning and Control of Quadrotor UAVs," arXiv:2305.03868, Sec. 2.4, Eqs. (5)–(9).（\(z_{k+1}=Az_k+Bu_k\)，\(x_k=\mathcal C z_k\)，参考轨迹提升，\(\bar Q=\operatorname{diag}(Q,0)\)，QP 只含输入）
3. Y. Wang, Y. Yang, Y. Pu, C. Manzie, "Data-driven Predictive Tracking Control based on Koopman Operators," arXiv:2208.12000v2, Secs. III-B–III-C, IV.（在线可达稳态决策变量 + 终端等式 + 约束收缩 + ISS，不需外部参考输入）
4. M. Korda, I. Mezić, "Linear predictors for nonlinear dynamical systems: Koopman operator meets model predictive control," Automatica, 93:149–160, 2018.（Koopman MPC 基本形式，输入不升维）
5. 本仓库 `.vibe/docs/papers/koopman-lifted-tracking-review-20261109/reading-note.md`（上述文献的转移结论记录）

---

## 8. 风险与检查点

**风险**

1. A3′（提升可观测性）可能不成立：潜在特征对输出非单射时 \(\gamma\) 无穷。需在训练后于 \(\mathcal Q\) 上数值核验。
2. 输出代价下 QP 对潜变量"无感"，长时域预测可能漂移（SE(3) Koopman-MPC 亦报告约 1 s 后偏离）。
3. 附录 C 是全篇最容易出错的一块，重建后必须逐式核对常数与量词。
4. 若最终结论降级，摘要/引言中任何"指数跟踪""全状态稳定"表述都要同步核对，不能保留旧口径。

**检查点**

- CP1：IV-A 改完，编译通过，公式编号不变，代价与移位自洽。
- CP2：A3′ 在数据上给出有限 \(\gamma\)。
- CP3：IV-B 五环重新接通，量词与半径表达式逐项可追溯。
- CP4：附录 B/C 与新代价一致，无悬空引用。
- CP5：全文编译、编号核对、版面核查。
