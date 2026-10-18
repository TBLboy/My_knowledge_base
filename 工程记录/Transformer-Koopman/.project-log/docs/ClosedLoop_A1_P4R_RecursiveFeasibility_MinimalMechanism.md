# A1 P4-R：跨采样重新冻结递归可行性的最小机制研究

日期：2026-10-17  
范围：纯理论研究；不修改论文、代码、实验、图片或正式控制器；不做数值验证。  
前置：P0–P3 条件理论、P4 Frozen/full 静态桥接路线图。  
状态标签：`PROVED`、`CONDITIONAL`、`OPEN`、`BLOCKED`、`NO-GO`。

## 1. Executive verdict

### Route A：完全不改当前 Frozen 控制器

**裁决：`CONDITIONAL / weak explanatory value`。**

可以把跨采样名义更新规则、冻结变化界、统一 Slater 裕量、逐面持续裕量和闭环工作域保持列为强假设，得到条件递归可行模板。但若这些假设直接包含

\[
\mathcal U_{k+1}^{fr,shr}(\xi_{k+1},\bar U_{k+1})\ne\varnothing
\]

或“移位候选属于下一收紧集合”，它们实际上封装了递归可行结论，解释力弱，不能称为由当前算法推出的定理。

### Route B：最小可行性机制候选

**裁决：`CONDITIONAL / requires user approval before controller change`。**

最小候选是：保留一次名义 rollout、一次冻结和一次凸 QP，规定确定性 shift-tail 名义更新，并把一个可行终端续接候选与逐面终端裕量纳入 QP/可行性接口。它可能保留 Frozen QP 结构，但是否仍保持当前正式控制器语义，取决于是否新增硬终端约束、备份候选或可行性恢复机制。

### 当前正式控制器

**P4-R：`OPEN / BLOCKED`。**  
仅凭固定名义序列下同候选 `K_i` 冻结界、P4-S 静态包含和 P3-C 理想完整续接，不能推出下一采样重新冻结后的可行性。  
**当前正式控制器递归可行性：`NO-GO`，在没有新增跨采样假设或机制前停止 P5。**

---

## 2. Precise definitions

### 2.1 状态、参考与缓存

\[
\eta_k=\operatorname{col}(z_k,X_k,U_k^{in}),
\qquad
\xi_k=\operatorname{col}(\eta_k,u_{k-1}).
\]

若 `U_k^{in}` 已含 `u_{k-1}`，则要求一致性：

\[
u_{k-1}=E_uU_k^{in}.
\]

终端误差必须是相对于同一绝对参考时刻的联合误差：

\[
e_{t}=\xi_t-\xi_t^{ref}.
\]

终端集合、终端反馈、终端成本和约束面均带绝对时间索引 `t`。

### 2.2 当前时刻的 Frozen QP

给定当前真实联合初值 `xi_k`、可行名义序列 `bar U_k`：

1. 沿完整调度模型生成一次名义 rollout；
2. 生成 `bar A_{i|k},bar B_{i|k}`；
3. 固定该矩阵序列；
4. 求解一次凸 QP，得到 `U_k^{fr}`；
5. 执行 `u_{0|k}^{fr}`。

当前收紧可行集记为：

\[
\mathcal U_k^{fr,shr}(\xi_k,\bar U_k).
\]

### 2.3 候选名义更新

候选确定性更新规则为：

\[
\bar U_{k+1}
=\mathscr W(\xi_{k+1},U_k^{fr},\bar U_k).
\tag{R1}
\]

最小 shift-tail 候选：

\[
U_{k+1}^{shift}
=\operatorname{shift}(U_k^{fr})\oplus u_{term,k+N}.
\tag{R2}
\]

这里 `u_term,k+N` 由理论终端反馈或一个事先定义的可行 tail 生成。`warm-start` 只是初值/候选，不自动等于 QP 可行性保证。

### 2.4 两条需要比较的轨迹

- 旧时刻完整移位轨迹：旧完整模型候选在执行首输入后，删除首输入并追加理论终端 tail；
- 新时刻 Frozen 轨迹：从真实重新编码 `xi_{k+1}` 出发，以 `bar U_{k+1}` 重新名义 rollout、重新冻结，再用 `U_{k+1}^{shift}` 作为候选。

二者必须使用同一绝对时间参考、同一输入历史更新和一致的终端坐标。差异不是旧 `K_i` 的同候选误差，因为新轨迹改变了初值、名义序列和冻结矩阵。

---

## 3. Lemma 1：真实首步重新编码扰动

沿用 P2 的一步残差：

\[
r_k=z_{k+1}^{enc}-A(c_k)z_k^{enc}-B(x_k)u_k.
\]

在测量窗口尾部一致、输入历史按同一规则移位、`x_{k+1}=C_xz_{k+1}^{enc}` 且完整映射使用同一 `A(c_k),B(x_k)` 的前提下：

\[
\eta_{k+1}^{enc}
=\mathcal F_\eta(\eta_k^{enc},u_k)
+w_k^\eta,
\]

\[
w_k^\eta=\operatorname{col}(r_k,b_xC_xr_k,0).
\tag{R3}
\]

因而：

\[
\|w_k^\eta\|_2
\le\sqrt{1+\|b_xC_x\|_2^2}\,\|r_k\|_2.
\tag{R4}
\]

**状态：`PROVED`（在明确前提下）。**  
这只是测量/重新编码增广层扰动，不是物理 plant 全状态误差界。

---

## 4. Lemma 2：跨采样偏差 `Gamma_k`

### 4.1 目标

希望比较：

\[
e_{k+N+1|k+1}^{fr,+}
\quad\text{与}\quad
e_{k+N+1|k}^{shift,full}.
\]

目标形式：

\[
\|e_{k+N+1|k+1}^{fr,+}
-e_{k+N+1|k}^{shift,full}\|_2
\le\Gamma_k.
\tag{R5}
\]

### 4.2 可分解的误差来源

在相同绝对参考坐标下，可形式分解为：

\[
\Gamma_k
\le
\Gamma_k^{init}
+\Gamma_k^{nom}
+\Gamma_k^{freeze}
+\Gamma_k^{tail}
+\Gamma_k^{ref}.
\tag{R6}
\]

其中：

1. `Gamma_init`：真实重新编码初值与旧完整预测首状态的差异，可由 R4 传播到增广状态；
2. `Gamma_nom`：`bar U_{k+1}` 与旧移位名义序列的差异，经上下文和调度矩阵 Lipschitz 界传播；
3. `Gamma_freeze`：新 Frozen 矩阵与对应完整/旧移位传播的差异；
4. `Gamma_tail`：旧终端 tail 与新 Frozen 候选尾部的输入/状态差异；
5. `Gamma_ref`：参考窗口、终端目标和时变终端坐标的移位差异。

### 4.3 为什么当前不能得到有限可用的 `Gamma_k`

现有 `K_i` 只能提供：

\[
\|z_{i|k}^{full}(U)-z_{i|k}^{fr}(U;\bar U_k)\|
\le\bar K_{i,k}(\bar U_k),
\]

它不提供：

- `bar U_{k+1}` 的更新规则；
- `\|bar U_{k+1}-shift(bar U_k)\|` 的界；
- 新旧冻结矩阵的统一差异界；
- 新 Frozen 轨迹在真实初值下的工作域保持；
- `u_term` 对新旧尾部的兼容界。

因此当前只能写出结构性模板：

\[
\Gamma_k
\le
\mathcal G_N\bigl(
\|w_k^\eta\|,
\|\bar U_{k+1}-\mathscr S(U_k^{fr})\|,
\|\bar A_{k+1}-\bar A_k^{shift}\|,
\|\bar B_{k+1}-\bar B_k^{shift}\|,
\|u_{term}-u_{tail}^{shift}\|,
\Delta_{ref,k}
\bigr),
\tag{R7}
\]

其中 `G_N` 必须由完整增广传播的 Lipschitz/有界常数构造；它不能被定义成一个未推导的未知常数。当前 R7 只是待证明的结构模板，不是已获得的跨采样界。

但当前缺少 R7 的第二至第五项的前提，因此：

**Lemma 2 状态：`OPEN / BLOCKED`。**

这不是“还没算常数”，而是跨采样名义更新和新冻结映射尚未被当前控制器定义为可控对象。

---

## 5. Lemma 3：逐面裕量蕴含下一 Frozen 候选可行

设旧移位完整轨迹在下一时刻终端面满足：

\[
H_{f,k+N+1}e_{k+N+1|k}^{shift,full}
\le h_{f,k+N+1}-s_{k+N+1}-\rho_k.
\tag{R8}
\]

若 R5 成立，并对每个面 `r`：

\[
\|H_{f,k+N+1,r,:}\|_2\Gamma_k
\le(\rho_k)_r,
\tag{R9}
\]

则：

\[
\begin{aligned}
H_{f,r}e_{k+N+1|k+1}^{fr,+}
&\le H_{f,r}e_{k+N+1|k}^{shift,full}
+\|H_{f,r,:}\|_2\Gamma_k\\
&\le h_{f,r}-s_r.
\end{aligned}
\]

因此新 Frozen 候选满足收紧终端面。若同时满足下列**全时域**条件：

1. 前移输入仍满足下一时刻输入约束；
2. 新真实初值属于下一 Frozen 模型的工作域；
3. `u_term` 的输入约束和缓存更新满足联合终端定义；
4. 前移轨迹的每个中间状态和输入均满足下一问题的所有阶段约束、工作域和调度域条件；
5. `Gamma_k` 对整个预测路径提供相应的逐时刻界，而非只对终端状态有界；
6. 新名义序列与新冻结矩阵确实按 R1 生成；

则该候选属于下一收紧集合：

\[
U_{k+1}^{shift}
\in\mathcal U_{k+1}^{fr,shr}(\xi_{k+1},\bar U_{k+1}).
\tag{R10}
\]

**Lemma 3 状态：`CONDITIONAL`。**  
终端面的三角不等式本身成立；把它扩展为 R10 还必须验证上述全时域条件。真正困难在 R8、R9、R5 以及中间路径裕量是否由控制器结构持续提供。

---

## 6. 可持续裕量与递归命题

### 6.1 最小强假设模板 `H-R`

对所有闭环采样时刻 `k`，假设：

1. `xi_k` 属于统一紧一致性工作域；
2. 名义更新规则 R1 已固定且满足可计算的跨采样偏差界；
3. R7 给出统一 `Gamma_k<=bar Gamma_k`；
4. 终端面存在统一裕量 `rho_k>=rho_min>0`，并满足 R9；
5. 移位阶段输入、终端输入和缓存更新均满足约束；
6. 新名义序列和 Frozen 映射保持在同一 Lipschitz/误差工作域；
7. 初始时刻存在一个收紧可行序列。

若进一步假设每一时刻的移位完整轨迹都保留 R8 的终端裕量、全时域收紧裕量和工作域裕量，则由 Lemma 3 归纳得到：

\[
\mathcal U_k^{fr,shr}(\xi_k,\bar U_k)\ne\varnothing
\quad\forall k\ge k_0.
\tag{R11}
\]

**命题状态：`CONDITIONAL`；若把“每一时刻保留上述裕量”本身作为结论依据，则属于 `assumption-based / weak explanatory value`。**

### 6.2 `H-R` 是否循环

`H-R` 中第 2–4 项不是当前模型结构自动推出的事实：

- R1 的名义更新规则当前未被正式控制器定义；
- `Gamma` 的统一界需要新旧冻结映射变化界；
- 统一正终端裕量需要 QP 解被设计/约束为保留裕量。

若将第 2–4 项改写成“下一时刻收紧集合非空且移位候选可行”，则只是把 P4-R 结论改名，属于循环假设。

因此 H-R 是**强假设模板**，不是当前控制器的非循环证明。

---

## 7. Route A / Route B 真实裁决

### Route A：不改当前控制器

- 纯算法自动推出 P4-R：`NO-GO`；
- 加 H-R 后的条件模板：`CONDITIONAL / weak explanatory value`；
- 解释风险：H-R 若包含持续裕量和每步名义更新可行性，接近封装结论；
- 可作为论文限制性理论模板，但不能写成当前实现已保证递归可行。

### Route B：最小机制候选

可研究但未获批准实施的最小机制：

1. 固定确定性 `bar U_{k+1}=W(xi_{k+1},U_k^{fr},bar U_k)`；
2. 采用已知可行的 shift-tail 作为显式候选，而不把普通 warm-start 当可行性保证；
3. 在 QP 中增加线性终端收紧和持续裕量约束；
4. 必要时保留一个可行备份候选/终端管束机制。

它可以保留一次名义 rollout、一次冻结和一次凸 QP，但可能改变正式控制器的约束/目标语义，需用户批准。若不增加这些机制或同等强假设，R11 无法从现有结构推出。

**Route B 状态：`CONDITIONAL / requires controller-design decision`。**

---

## 8. Failure analysis

当前证明不能闭合的最小原因不是 P4-S 静态包含方向错误，而是：

1. 旧时刻的冻结界绑定 `bar U_k` 和同一候选 `U`；
2. 下一时刻改变了真实初值、参考窗口、名义序列和冻结矩阵；
3. 没有结构条件把这些变化限制在旧终端裕量内；
4. 当前 QP 即便某一步可行，也不保证解保留下一步所需的终端面裕量；
5. 因而不能构造不循环的 R5/R7 统一界和 R11 归纳。

这给出正式边界：

\[
\boxed{
\text{static Frozen/full inclusion}
\not\Rightarrow
\text{cross-sampling recursive feasibility}.}
\]

---

## 9. Decision table

| 条件/机制 | 当前结构自动推出 | 可作为强假设 | 是否改变正式控制器 | P4-R 状态 |
|---|---:|---:|---:|---|
| 同候选 `K_i` 冻结界 | 是（原假设域内） | 不需要 | 否 | `PROVED/CONDITIONAL` |
| 静态逐面收紧包含 | 否 | 是 | 可能新增终端面 | `CONDITIONAL` |
| 确定性名义 shift 更新 | 否 | 是 | 可能改变 warm-start 语义 | `OPEN` |
| 新旧冻结映射变化界 | 否 | 是 | 可不改结构但需新增理论条件 | `OPEN` |
| 持续终端 Slater 裕量 | 否 | 是 | 通常需新增约束/机制 | `OPEN` |
| 下一次收紧集合非空 | 否 | 直接假设则循环 | 需机制或证明 | `BLOCKED` |
| P4-R 递归可行 | 否 | H-R 下条件成立 | Route B 可能改变 | 当前 `NO-GO` |

## 10. Next gate

在当前正式控制器不变的前提下，P4-R 最多得到 H-R 条件模板，不能得到自动递归可行定理。进入 P5 前必须满足：

1. 用户批准 Route B 的最小可行性机制，或明确接受 H-R 强假设；
2. 给出非循环的 R1 名义更新、R7 跨采样界和持续裕量机制；
3. 证明 R10 对下一 Frozen 收紧集合成立，并可归纳到 R11。

上述门槛的可检查展开如下；任一项缺失都不能把 P4-R 标为 `PROVED`：

| 检查项 | 必须给出的非循环证据 |
|---|---|
| 名义更新 | 明确的 `W`/shift 规则，以及 `bar U_{k+1}` 与旧移位序列的可计算界；不能只说“采用 warm-start” |
| 跨采样偏差 | 对预测路径每个时刻给出 `Gamma_{j,k}`，并由初值、名义、冻结、tail、参考变化的结构常数推出统一上界；不能把 `Gamma_k` 当作未定义常数 |
| 阶段约束 | 对每个中间时刻、每个状态/输入/工作域/调度域面给出旧移位轨迹的裕量，以及相应 `||H_{j,r,:}|| Gamma_{j,k}` 的收紧不等式 |
| 终端约束 | 给出 R8–R9 的逐面不等式，并说明 `rho_k` 如何由终端约束、终端反馈或备份候选持续产生 |
| tail 与缓存 | 证明 `u_term` 满足时变输入约束、联合状态上一输入缓存一致性和下一终端坐标定义 |
| 工作域 | 证明真实重新编码初值及全预测路径始终留在 `K_i`、Lipschitz 和调度界适用域内 |
| 初始性与归纳 | 证明至少一个初始收紧可行序列存在，并证明同一套裕量在每次 shift/re-freeze 后仍成立；不得把“下一次可行”作为前提 |
| 凸性与在线结构 | 说明新增条件仍是线性/凸 QP，且每个采样时刻仍只执行一次名义 rollout、一次冻结和一次 QP |

在此之前，停止 P5 正式稳定性证明；不声称当前 Frozen-LTV 控制器递归可行或物理 plant 稳定。
