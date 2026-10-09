# 阶段③ 论文理论部分：严谨性审计报告 v1

**日期**：2026-10-06
**对象**：`论文/新版本/Main.tex` 的理论文字（Def.1/2/3、Prop.1/2/3、Thm.1、Cor.1、Remark、Assumption、参考文献）
**目标**：确保理论**真严谨、闭合、完备**——证明是真证明，不是随笔生成；引用是真文献。
**本轮已完成**：逐条审计 + 修复 2 处真实缺陷 + 补齐 5 条真实引用。

---

## 0. 结论摘要

| 项 | 状态 |
|---|---|
| 6 项核心结果（Prop.1 / Def.1 / Prop.2 / Thm.1 / Cor.1 / Prop.3）陈述 | **齐备** |
| 5 个证明块（Prop.1 / Prop.2 / Thm.1 / Cor.1 / Prop.3） | **齐备，且逐条通过审计** |
| 本轮修复的真实缺陷 | **2 处**（Prop.3 中值形式不严格；Def.2 措辞错误） |
| 本轮补齐的引用 | **5 条**（全部经检索核实为真实文献） |
| 剩余待 GPT 确认项 | **5 条**（见 §4，均为"表述/定位"问题，非证明漏洞） |

---

## 1. 逐条审计（证明是否成立）

### Prop.1 Finite-History Markovization —— **通过**
- 构造：$\vxi_k=\mathrm{col}(\vx_{k-P+1:k},\vu_{k-P+1:k-1},\vz_k)$，$\vxi_{k+1}=\mF_\Theta(\vxi_k,\vu_k)$。
- 审计：窗口更新是确定性移位（追加 $(\hat\vx_{k+1},\vu_k)$、丢弃最旧项）；$\hat\vx_{k+1}=\mC\vz_{k+1}$，$\vz_{k+1}=\mA(\vc_k)\vz_k+\mB\vu_k$，$\vc_k=C_\phi(\mX_k)$，而 $\mX_k$ 是 $\vxi_k$ 的子向量 → 每个自变量都是 $(\vxi_k,\vu_k)$ 的函数 → 复合得到确定性的 $\mF_\Theta$。**每一步均有依据，无跳步。**
- 边界条件（仅在 decoded-feedback 闭环下成立）已由紧随其后的 Remark 明确，无遗漏。

### Prop.2 Latent Rollout Error Propagation —— **通过**
- 构造：$d_{k+1}=\|\hat\vz_{k+1}-\vz^E_{k+1}\|$，插入并减去 $\mA(\vc_k)\vz^E_k+\mB\vu_k$，三角不等式 → $d_{k+1}\le\|\mA(\vc_k)\|d_k+\epsilon_k$。
- 展开：空积在 $i=H-1$ 取 1，逐项展开正确。**证明成立。**
- 注：$d_k$ 与 $\vz^E$ 均在"rollout 生成的历史"上定义，$\vc_k$ 也是同一历史调度的上下文 → 前后一致，无偷换。

### Thm.1 Finite-Horizon Prediction Error Bound —— **通过（在 (A1)–(A3) 下）**
- 证明：$\|e_{k+1}\|\le\|\mF^\star-\mF_\Theta\|(\vxi^\star_k)+\|\mF_\Theta(\vxi^\star_k)-\mF_\Theta(\hat\vxi_k)\|\le\epsilon+\mLf\|e_k\|$，展开得界。**标准且成立。**
- 诚实性：因经验 $\mLf\approx1.45>1$，论文只用有限时域形式、不取渐近极限 $\epsilon/(1-\mLf)$。**处理正确。**

### Cor.1 Physical-Space Prediction Bound —— **通过（本轮补证明）**
- 本轮补上证明：$\hat\vx_{k+H}$ 与 $\vx_{k+H}$ 分别是 $\hat\vxi_{k+H}$ 与 $\vxi^\star_{k+H}$ **history 块的最后 $n$ 个坐标**，故差是坐标子向量 → 子向量范数 ≤ 全范数；再代入 Thm.1。
- **同时修正了一处真实错误**：原表述为 "the physical state is the first $n$ coordinates of $\vxi$"（错——那是窗口最旧一项），已改为"history 块的最后 $n$ 个坐标"。

### Prop.3 RTI Local Approximation —— **通过（本轮修复证明）**
- **发现的真实严谨性缺陷**：原证明用"中值形式"$\vr_i=\tfrac12\delta_i^\top\nabla^2\mF_\Theta(\bar\vxi_i+t\delta_i)\delta_i,\ \exists t\in(0,1)$。**该形式对向量值函数不严格**——逐分量的 $t_j$ 可能不同，不存在统一的 $t$。
- **修复**：改用积分型 Taylor 余项
  $\vr_i=\int_0^1(1-s)\,\mathrm{D}^2\mF_\Theta(\bar\vxi_i+s\delta_i)[\delta_i,\delta_i]\,\mathrm{d}s$，
  再由"向量积分的范数 ≤ 范数的积分"与二阶导数算子范数上界得
  $\|\vr_i\|\le\int_0^1(1-s)\|\mathrm{D}^2\mF_\Theta\|\|\delta_i\|^2\mathrm{d}s\le\tfrac{\mMF}{2}\|\delta_i\|^2$。
- 相应地把 Assumption A3 从"bounded Hessian $\|\nabla^2\mF_\Theta\|$"改写为"二阶导数算子范数 $\|\mathrm{D}^2\mF_\Theta\|_2\le\mMF$"，与新证明口径统一。**修复后证明严格闭合。**

### Remark（谱稳定不充分）—— **通过（本轮补引用）**
- 断言 $\rho(\mA_k)<1\ \forall k\not\Rightarrow\|\mA_{k+H-1}\cdots\mA_k\|\le c<1$ 是经典的非交换矩阵谱半径/联合谱半径缺口。
- **原缺引用**，本轮补上 3 条真实文献（Rota–Strang 1960 起源；Daubechies–Lagarias 1992；Jungers 2009 专著）。

---

## 2. 本轮修复清单（已写入 Main.tex）

| # | 位置 | 问题 | 修复 |
|---|---|---|---|
| 1 | Prop.3 证明 + 前置文字 + A3 | 向量值函数"中值形式"不严格 | 改为积分型 Taylor 余项 + 算子范数界；A3 改口径 |
| 2 | Def.2 末尾 | "the quantity bounded below"（措辞错误，Prop.2 给的是**上界**） | 改为 "the quantity for which Proposition 2 provides an upper bound" |
| 3 | Cor.1 | 缺 proof；且坐标措辞有误（first→last $n$） | 补 proof + 修正措辞 |
| 4 | Prop.3 | 缺 proof | 补 proof（见 #1） |
| 5 | Remark（谱稳定） | 无引用 | 补 \cite{daubechies1992sets, rota1960joint, jungers2009joint} |
| 6 | §Real-Time Predictive Control | RTI 无引用 | 补 \cite{diehl2005realtime, gros2020rti} |

---

## 3. 本轮补齐的引用（均已检索核实为真实文献）

1. G.-C. Rota and G. Strang, "A note on the joint spectral radius," *Nederl. Akad. Wetensch. Proc. Ser. A*, vol. 63 (Indag. Math., vol. 22), pp. 379–381, 1960.
2. I. Daubechies and J. C. Lagarias, "Sets of matrices all infinite products of which converge," *Linear Algebra Appl.*, vol. 161, pp. 227–263, 1992.
3. R. M. Jungers, *The Joint Spectral Radius: Theory and Applications*, LNCIS vol. 385. Springer, 2009.
4. M. Diehl, H. G. Bock, and J. P. Schlöder, "A real-time iteration scheme for nonlinear optimization in optimal feedback control," *SIAM J. Control Optim.*, vol. 43, no. 5, pp. 1714–1736, 2005.
5. S. Gros, M. Zanon, R. Quirynen, A. Bemporad, and M. Diehl, "From linear to nonlinear MPC: Bridging the gap via the real-time iteration," *Int. J. Control*, vol. 93, no. 1, pp. 62–80, 2020.

---

## 4. 待 GPT 确认项（表述/定位，非证明漏洞）

### Q1. $\epsilon$（Thm.1）与 $\epsilon_k$（Prop.2）的关系是否需显式说明？
- 现状：Thm.1 用统一模型误差 $\epsilon=\sup_\Omega\|\mF^\star-\mF_\Theta\|$；Prop.2 用一步缺陷 $\epsilon_k=\|\mA(\vc_k)\vz^E_k+\mB\vu_k-\vz^E_{k+1}\|$。
- 二者**不是同一个量**：$\epsilon$ 是"真映射 vs 学习映射"的一致上界，$\epsilon_k$ 是"传播 vs 重编码"的一步缺陷；诊断表只报了 $\epsilon_k$（median 0.347），**未报 $\epsilon$**。
- 待定：是否在 Thm.1 后加一条短 Remark 说明 $\epsilon\ge\sup\epsilon_k$（同口径下），并说明 $\epsilon$ 在验证集上的估计方式？还是维持现状（scope 已声明 $\epsilon$ 为经验估计）？

### Q2. $\mF^\star$ 的定义是否需更醒目？
- 现状：$\mF^\star$ 采用"真历史 + 真观测上的编码器、无解码器在环"的结构约定，而 $\mF_\Theta$ 是"传播 + 解码反馈"。
- 后果：两映射的 latent 更新规则不同（一个重编码、一个传播），(A1) 的 $\epsilon$ 因此**吸收了编码-传播缺口**。这在数学上没问题，但读者可能问"为何两映射结构不同"。
- 待定：是否加一句显式说明（"(A1) 的 $\epsilon$ 因而同时涵盖模型误差与编码/传播口径差"）？

### Q3. Def.1（HCLTK）位置
- 现状：Def.1 在 **Methodology 节**（定义模型族），而 GPT §7 冻结链写作 `Prop.1 → Def.1 → Prop.2`。
- 待定：Def.1 是否必须移入理论节开头？还是保持"方法节定义、理论节引用"（并用前向引用标注）即可？

### Q4. Assumption 编号
- 现状：单一 assumption 块，内部 (A1)(A2)(A3)。
- 待定：是否符合 GPT §16 "assumptions 编号统一"？还是希望拆成 Assumption 1/2/3 三个独立环境？

### Q5. Prop.2 记号 $\hat\vz_k$
- 现状：Prop.2 直接写 $d_k=\|\hat\vz_k-\vz^E_k\|$，未显式说明 $\hat\vz_k$ 即 Def.2 的 $\vz^P_k$（传播 latent）。
- 待定：是否补一句"$\hat\vz\equiv\vz^P$（传播 latent）"以消除歧义？

---

## 5. 未闭合项（与理论无关，仅记录）

- Experiments 章节为空 → 理论对 `\ref{sec:experiments}` 的交叉引用暂指空节（用户已推迟）。
- 图 1–3 未适配（用户已推迟）。
- 机制图已生成（`pictures/Figure_mechanism.pdf`），但按用户最新指示"绘图暂停"，暂不再改。
- 中英版本转换未开始。
- 本机无 LaTeX，未编译（静态检查通过：引用无缺失、无悬空引用、环境配对、5/5 证明块）。
