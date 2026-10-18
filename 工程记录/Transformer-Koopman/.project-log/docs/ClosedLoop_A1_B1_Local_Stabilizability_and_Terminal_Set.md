# A1-B1：局部可稳定化与终端集可构造性审查

日期：2026-10-17  
性质：纯理论审查；不修改论文、代码、实验、图片或正式控制器；不做数值验证。  
依据：B1 最新报告、Route B 报告、P3/P4 报告、附件 A0–A15 任务书及当前 `Main.tex`。

## 0. 结论先行

**本轮裁决：`CONDITIONAL GO` 仅适用于“若补齐离线证书，则逻辑可闭合”的设计模板；当前项目的 B1 可构造性为 `OPEN / BLOCKED`，正式控制器为 `NO-GO`，P5 不准入。**

原因不是已经证明终端集不存在，而是当前模型/论文没有给出完整增广闭环映射的局部可稳定化证据、非线性余项外包、统一扰动集合、非空终端集构造或保护所有 QP 最优解的硬约束接口。

---

## 1. A0：状态、参考与轨迹语义

### 命题

在一致性流形上应使用

\[
\eta_t=\operatorname{col}(z_t,X_t,U_t^{in}),\qquad
\xi_t=\operatorname{col}(\eta_t,u_{t-1}),
\]

其中

\[
U_t^{in}=\operatorname{col}(u_{t-P+1},\ldots,u_{t-1}),\qquad
u_{t-1}=E_uU_t^{in}.
\]

历史窗口和缓存递推为

\[
U_{t+1}^{in}=\operatorname{shift}(U_t^{in},u_t),
\qquad u_{last,t+1}=u_t.
\]

严格区分：Frozen 预测、完整学习模型轨迹和真实 plant 轨迹。

### 证明/边界

当前 `Main.tex` 明确了 `X_k`、`U_k^{in}`、`z_k=g_\theta(X_k)` 和 lifted scheduled recursion，但控制章节没有把 `X,U^{in},u_last` 组合成一个正式的 `F_t(\xi,u)`，也没有把 plant 失配纳入控制模型。

### 状态

`CONDITIONAL`：一致性接口可定义；完整增广转移尚未成为当前论文/控制器的正式对象。物理 plant 结论不在范围内。

## 2. A1：参考类别

选定最小可辩护类别 **R1：模型可实现、输入可行、历史窗口一致的参考**：存在 `xi_t^ref,u_t^ref` 满足完整增广学习模型和缓存递推，并满足输入幅值及实际硬约束。

若无法证明 R1，则只可退到 R2：参考残差 `d_ref,t` 有已知统一界；任意时变参考不能直接使用。周期 R3 可在有周期性数据和周期证书时作为后续特例，但当前没有周期数据/证书。

### 状态

`OPEN / BLOCKED`：当前材料允许任意时变参考符号，但没有给出参考可实现性、参考输入余量或 `d_ref,t` 的统一界。

## 3. A2：完整增广线性化

### 所需对象

在一致性流形上需要

\[
\xi_{t+1}=F_t(\xi_t,u_t)+w_t,
\]

并在参考点给出

\[
A_t^{lin}=\partial_\xi F_t(\xi_t^{ref},u_t^{ref}),
\qquad
B_t^{lin}=\partial_uF_t(\xi_t^{ref},u_t^{ref}).
\]

`F_t` 必须包含 `C_\phi(X,U^{in})`、`A(c)`、`B(C_xz)`、测量回填、输入窗口移位和缓存更新。

### 当前证据

`Main.tex` 只给出

\[
z_{i+1}=A(c_i)z_i+B(C_xz_i)u_i
\]

和有限时域误差递推；它没有给出完整 `F_t` 的 Jacobian 或在一致性流形上的等价最小坐标外包。

### 状态

`BLOCKED`：不能把 `z` 子系统 Jacobian 冒充完整增广 Jacobian，也不能从有限时域常数自动得到终端局部外包。

## 4. A3：局部可稳定化性

### 条件性命题

若 A2 给出完整增广 `A_t^{lin},B_t^{lin}`，并存在离线反馈 `K_t` 使

\[
A_t^{cl}=A_t^{lin}+B_t^{lin}K_t
\]

在一致性流形上满足统一收缩或时变 Lyapunov 不等式，则可进入终端集构造。

### 当前能否判断

不能。当前项目没有完整增广 `A_t^{lin},B_t^{lin}`，也没有 `K_t`、可稳定化性秩条件、缓存方向分析或闭环收缩界。缓存坐标可能包含冗余模式，但是否全部为可消除冗余必须由正式流形参数化证明。

### 状态

`OPEN / BLOCKED`；不是 `NO-GO`，因为缺失的是模型证据而非已构造的不可稳定反例。

## 5. A4：非线性余项

球形终端集需要在自身工作域内证明

\[
\|e_{t+1}-e_{t+1}^c\|
\le \lambda_t\|e_t-e_t^c\|+q_t+d_t+\rho_t(r_t).
\]

当前 `Main.tex` 的 A1–A4 是有限时域、共同工作域和 Lipschitz/残差条件；没有终端闭环局部余项 `rho_t(r)`，也没有二阶可微或 Lipschitz Jacobian 条件用于二阶余项。

### 状态

`OPEN / BLOCKED`：不能用名义 Jacobian 或有限时域 `L` 无条件替代终端非线性余项。

## 6. A5：扰动账本

必须分开：

- `D_fr`：旧时刻同候选 Frozen/full 差异；
- `D_enc`：真实重新编码首步偏差；
- `D_ref`：参考不可实现残差；
- `D_plant`：plant 与学习模型失配，本轮不纳入结论；
- `D_num`：求解误差，本轮不用于构造终端集。

新名义候选在 B-EXACT 契约下的 Frozen/full 差异为零，但旧 `D_fr` 对 tail 的影响仍保留。当前只知道有限时域 `K_i`，没有跨所有终端时刻的统一 `D_fr` 或 `D_enc` 外包。

记号统一：此前 Route B 报告中的首步重新编码误差记为 `D_enc`；本轮将其经过完整模型传播后的集合记为 `D_init`，即

\[
\mathcal D_t^{init}=\Phi_{t}(\mathcal D_t^{enc})
\]

或使用一个明确包含关系 `Phi_t(D_enc) subseteq D_init`。二者不是两份独立扰动，不得在总账本中重复相加。

### 状态

`CONDITIONAL`（账本规则）；实际统一集合为 `OPEN / BLOCKED`。

## 7. A6：终端集非空

### 球形尝试

一致性流形上的球

\[
\mathcal X_{f,t}=\{e\in\mathcal M_t:\|e-e_t^c\|\le r_t\}
\]

需要中心、正半径和所有面严格裕量。已有 `r_safe` 公式是条件性充分证书，不是当前已验证数值结果。

### 多面体尝试

\[
\mathcal Z_t=\{e\in\mathcal M_t:G_te\le\alpha_t\}.
\]

可用 LP 对偶证书

\[
G_t^T\lambda+H_t^T\nu=c,\quad \lambda\ge0,
\]

配合支持函数上界验证面传播。它要求 `G_t,alpha_t`、反馈、扰动集合和工作域均已构造；当前均未给出。

### 状态

球形：`OPEN / BLOCKED`；多面体：`CONDITIONAL` 模板但当前构造 `OPEN / BLOCKED`。

## 8. A7：鲁棒前向保持

给定真实闭环外包

\[
e_{t+1}^{act}\in A_t^{cl}e_t^{fr}\oplus\mathcal R_t(e_t^{fr})\oplus\mathcal D_t^{tot},
\]

多面体逐面证书为

\[
\sup_{e\in\mathcal Z_t}G_{t+1,q}A_t^{cl}e
+\sigma_{G_{t+1,q}}(\mathcal D_t^{tot})
\le\alpha_{t+1,q}.
\]

当前没有 `A_t^{cl}`、非线性余项 `R_t` 或统一 `D_tot`。

### 状态

`CONDITIONAL`（证书给定时）；当前 `OPEN / BLOCKED`。

## 9. A8：输入兼容

当前 `Main.tex` 的输入增量项 `S` 是成本项，不是硬约束。当前 QP 的硬约束仅为

\[
u_i\in\mathcal U.
\]

若未来新增硬增量约束，需明确记录为控制器语义变更。终端反馈还必须满足幅值约束、参考输入余量和缓存一致性。

### 状态

当前输入幅值：`CONDITIONAL`；输入增量硬约束兼容性：`OPEN`（当前并不存在该硬约束，不能假定已有）。

## 10. A9：工作域保持

必须证明终端集及其扰动后像均留在当前 `K_i`、context Lipschitz、矩阵界和历史一致性适用域。当前 A1/A4 只是假设固定有限时域轨迹在共同紧域内，不是终端族对所有闭环时刻的前向保持。

### 状态

`OPEN / BLOCKED`。

## 11. A10：B-EXACT

若新时刻从同一完整增广初值沿自身名义序列生成 `A,B`，并且 Frozen 同步更新测量窗口、输入窗口、缓存和参考索引，则归纳得到

\[
\xi_i^{fr}(\bar U;\bar U)=\xi_i^{full}(\bar U).
\]

当前论文冻结方程显式只写 lifted `z`，完整历史/缓存接口没有正式实现级定义。

### 状态

`CONDITIONAL`；完整接口契约下局部 `PROVED`，当前论文实现层面未证明。

## 12. A11：shift-tail

候选定义

\[
\bar U_{k+1}=U_{k+1}^{shift}
=\operatorname{shift}(U_k^{fr})\oplus u_{tail,k+N}.
\]

若旧终端属于鲁棒内集、tail 满足输入/缓存约束、扰动传播满足 A7、阶段工作域满足 A9，则候选可行。

### 状态

`CONDITIONAL`；当前因为 A3–A9 的关键对象缺失而 `OPEN / BLOCKED`。

## 13. A12：QP 硬约束接口

Frozen 预测 `Z=F+GU` 对输入和线性终端/工作域面仍是线性约束，因此 QP 凸性可保持。可是必须把终端/工作域面加入 QP，并证明它们保护**所有**最优解，而非只保护 warm-start 候选。

当前 QP 没有终端或工作域硬约束，只有输入约束；T17 尚未构造。

### 状态

结构保持：`CONDITIONAL GO`；当前接口：`OPEN / BLOCKED`。

## 14. A13：递归归纳

当前 baseline input-only QP 的非空性来自论文对 `\mathcal U` 非空的假设，即其输入可行集 `\mathcal U^N` 非空；这不等于新增终端/工作域硬约束后的 QP 非空。只有后者也有独立的 A6/A7/A8/A9/A12 证书时，才可由 shift-tail 归纳下一 QP 非空。把“每步非空”或“持续 Slater”直接写进假设属于循环。

### 状态

`OPEN / BLOCKED`；当前正式控制器 `NO-GO`。

## 15. A14：plant 与模型边界

当前所有理论对象最多针对学习模型闭环。`Main.tex` 明确学习于测量数据且无物理状态访问；没有 plant 与学习模型的闭环失配集合。因此不能声称真实 plant 稳定或真实 plant 递归可行。

### 状态

学习模型结论：`CONDITIONAL`；plant 结论：`OUT OF SCOPE / NO-GO`。

## 16. A15：P5 准入

当前不满足：完整增广局部可稳定化、非空终端集、统一扰动外包、工作域保持、QP 全域证书和递归归纳。

### 状态

`NO-GO`。即使未来 B1 递归可行闭合，仍需另行证明时变价值函数下降、终端成本条件和求解误差界。

## 17. 三个压力测试

### Test A：零扰动、可实现参考

在 `D=0` 且 B-EXACT 成立时，问题退化为完整增广模型的时变局部终端控制。当前仍缺完整 `A^{lin},B^{lin}` 和可稳定化反馈，因此只能 `CONDITIONAL`，不能作为当前模型 GO。

### Test B：非零 Frozen/full 与编码残差

终端每个面消耗 `D_fr + D_enc + D_ref` 的支持函数。有限时域 `K_i` 不能未经统一域/时间假设外推成无限时域扰动；当前为 `OPEN / BLOCKED`。

### Test C：QP 最优解偏离名义

即使 shift-tail 可行，没有终端/工作域硬约束时，最优解可能离开下一轮证书域。加入线性面可以保持凸性，但初始非空和全域归纳仍未证明。

## 18. 总裁决

| A义务 | 状态 |
|---|---|
| A0 状态一致性 | `CONDITIONAL` |
| A1 参考类别 | `OPEN / BLOCKED` |
| A2 完整增广线性化 | `BLOCKED` |
| A3 局部可稳定化 | `OPEN / BLOCKED` |
| A4 非线性余项 | `OPEN / BLOCKED` |
| A5 扰动账本 | `CONDITIONAL`；统一集合 `OPEN` |
| A6 终端集非空 | `OPEN / BLOCKED` |
| A7 鲁棒前向保持 | `CONDITIONAL`；当前 `OPEN` |
| A8 输入兼容 | `CONDITIONAL / OPEN` |
| A9 工作域保持 | `OPEN / BLOCKED` |
| A10 B-EXACT | `CONDITIONAL` |
| A11 shift-tail | `CONDITIONAL`；当前 `OPEN` |
| A12 QP硬约束接口 | `CONDITIONAL GO`结构性；当前 `OPEN` |
| A13 递归归纳 | `OPEN / BLOCKED` |
| A14 plant边界 | `OUT OF SCOPE / NO-GO` |
| A15 P5准入 | `NO-GO` |

**唯一首要阻碍：** 缺少当前完整增广模型在一致性流形上的可验证局部闭环外包/可稳定化证书；它使 `A2→A4→A6→A7` 无法非循环闭合。终端集合非空性、工作域保持和 QP 全域接口是由此派生但仍需分别验证的义务。
