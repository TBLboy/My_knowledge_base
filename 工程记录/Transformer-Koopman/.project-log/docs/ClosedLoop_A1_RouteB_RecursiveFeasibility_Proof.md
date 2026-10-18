# A1 Route B：递归可行性证明与压力测试

日期：2026-10-17  
范围：research-only；不修改论文、代码、实验、图片或正式控制器；不做数值验证。  
对象：时变参考、历史条件调度、一次名义 rollout、一次冻结、一次凸 QP。  
结论标签：`PROVED`、`CONDITIONAL`、`OPEN`、`BLOCKED`、`NO-GO`。

## 0. 总结裁决

- **B-EXACT：`CONDITIONAL / PROVED under an explicit interface contract`。** 对下一时刻从真实重新编码初值出发、沿自身名义输入序列生成完整 rollout 并冻结其逐步矩阵时，候选取为该名义序列，Frozen 与 nominal/full 轨迹逐步相等；该结论依赖历史移位、测量回填和输入缓存递推完全一致。当前 `Main.tex` 的冻结递推只显式写出 lifted state，因此完整增广版本仍需接口契约，不能直接称为现行实现已证明。
- **B1 shift-tail + 鲁棒终端内缩：`CONDITIONAL`。** B-EXACT 消除了该候选自身的 Frozen/full 误差，但不能自动提供旧完整延长轨迹的终端内缩；非零重新编码残差、时变参考和 tail 约束仍需一个可离线验证的鲁棒终端设计。
- **B2 可行候选保护：执行层保护可行；QP 非空的递归证明仍 `CONDITIONAL / OPEN`。** 显式备份候选不能凭自身保证下一 Frozen QP 非空；若备份证书直接假设每步存在，则循环。只有离线构造的时变鲁棒不变终端集合或等价非循环证书才可能闭合。
- **当前正式控制器：`NO-GO`。** 它没有终端收紧、确定性名义更新、tail 约束或可行性证书。
- **P5：停止。** 本报告不提供闭环稳定性结论。

---

## B-0：增广状态、参考与缓存一致性

定义最小增广状态

\[
\eta_t=\operatorname{col}(z_t,X_t,U_t^{in}),\qquad
\xi_t=\operatorname{col}(\eta_t,u_{t-1}),
\]

其中

\[
U_t^{in}=\operatorname{col}(u_{t-P+1},\ldots,u_{t-1}),
\qquad u_{t-1}=E_uU_t^{in}.
\]

完整映射写成

\[
\xi_{t+1}=F_t(\xi_t,u_t),
\qquad e_t=\xi_t-\xi_t^{ref}.
\]

参考、终端面、输入约束和 tail 均用绝对时间索引。若参考不可由输入完全实现，定义显式残差 `d_ref,t`，不能把它并入重新编码扰动。

**命题：** 在输入历史按真实执行输入移位、测量历史由同一 `C_xz` 回填、上一输入缓存取实际执行首输入的条件下，`eta` 与 `xi` 的递推在一致性流形上闭合。  
**状态：`CONDITIONAL`。** 这是接口条件，不是当前仅写 lifted-state Frozen 方程自动给出的完整增广证明。

---

## B-1：B-EXACT 名义自洽恒等式

在时刻 `k+1`，从同一个真实重新编码增广初值 `xi_{k+1}` 出发，给定名义输入

\[
\bar U=(\bar u_0,\ldots,\bar u_{N-1}).
\]

完整名义 rollout 为

\[
\bar\xi_0=\xi_{k+1},\qquad
\bar\xi_{i+1}=F_{k+1+i}(\bar\xi_i,\bar u_i).
\]

冻结模型定义为沿该名义 rollout 取

\[
\bar A_i=A(\bar c_i),\qquad
\bar B_i=B(\bar x_i),
\]

并使用同一初值、同一候选输入：

\[
\xi^{fr}_{0}=\bar\xi_0,
\qquad
\xi^{fr}_{i+1}=F^{fr}_{i}(\xi^{fr}_i,\bar u_i).
\]

若 `F_i^{fr}` 在名义点的 lifted、测量、输入历史和缓存块与 `F_{k+1+i}` 完全一致，则归纳假设 `xi_i^{fr}=bar xi_i` 给出相同调度量和相同下一状态，因此

\[
\boxed{
\xi_{i|k+1}^{fr}(\bar U;\bar U)
=\bar\xi_{i|k+1}
=\xi_{i|k+1}^{full}(\bar U),
\quad 0\le i\le N.
}
\tag{B-EXACT}
\]

**证明：** `i=0` 由同初值成立；若第 `i` 步相等，则 `x_i=C_xz_i`、测量窗口、过去输入窗口和 context 相等，故 `A,B` 相等；同一 `u_i` 下第 `i+1` 步相等。输入缓存由同一候选递推，测量窗口由同一 readout 回填，归纳闭合。

**边界：** 若 Frozen 只定义 `z_{i+1}=\bar A_i z_i+\bar B_i u_i`，则上式首先只证明 `z` 块。要提升为 `xi` 恒等式，必须额外规定并验证历史和缓存更新；否则失效差异为

\[
\Delta\xi_{i+1}
=\operatorname{col}(\Delta z_{i+1},\Delta X_{i+1},\Delta U_{i+1}^{in},\Delta u_i),
\]

其中后三块不由 lifted-state 等式自动消失。  
**状态：`CONDITIONAL`；在上述显式接口契约下为 `PROVED`。**

---

## B-2：旧 full 延长轨迹与新 full 名义轨迹

令时刻 `k` 的实际执行输入为 `u_{0|k}`，真实下一状态为

\[
\xi_{k+1}^{enc}=\xi_{1|k}^{full}+w_k^\xi,
\qquad \|w_k^\xi\|\le\bar w_k.
\]

旧序列求得 tail 后定义

\[
U_{k+1}^{shift}
=\operatorname{shift}(U_k^{fr})\oplus u_{tail,k+N},
\qquad \bar U_{k+1}=U_{k+1}^{shift}.
\]

旧完整延长轨迹从 `xi_{1|k}^{full}` 出发，新完整名义轨迹从 `xi_{k+1}^{enc}` 出发；它们使用同一 shifted inputs 和同一绝对时刻参考。若完整映射在工作域内对状态具有时变 Lipschitz 常数 `L_{F,t}`，则逐步差异满足

\[
\Gamma_{0,k}=\|w_k^\xi\|,
\qquad
\Gamma_{j+1,k}\le L_{F,k+j+1}\Gamma_{j,k},
\]

从而

\[
\Gamma_{j,k}
\le\left(\prod_{\ell=1}^{j}L_{F,k+\ell}\right)\bar w_k.
\tag{B2-G}
\]

若 tail 本身由两条轨迹不同的终端状态计算，则还须加上 tail 差异项；不能把它隐藏进 `w_k^xi`。时变参考不改变状态差异递推，但改变误差比较的绝对参考索引。

**状态：`CONDITIONAL`。** 需要明确工作域、输入 tail 一致性、半群索引和所有阶段约束；它不是现有 `K_i` 的直接跨采样延伸。

---

## B-3：旧 Frozen/full 终端误差集合

对旧时刻同一候选 `U_k^{fr}`，定义

\[
d_{fr,k}=\xi_{N|k}^{full}(U_k^{fr})-\xi_{N|k}^{fr}(U_k^{fr};\bar U_k),
\qquad d_{fr,k}\in\mathcal D_{fr,k}.
\]

已有 `K_i` 可在共同候选、共同名义序列和共同工作域内给出 `D_fr,k` 的外界。若终端 tail 为 `\kappa_{k+N}(e_{N|k}^{fr},u_{N-1|k})`，则真实旧终端使用的是 `e_N^{fr}+d_{fr,k}`；tail 的鲁棒条件必须对所有 `d_{fr,k}\in D_fr,k` 成立。

**状态：`CONDITIONAL`。** 该集合只处理旧时刻同候选 Frozen/full 差异；不能替代 B-2 的跨采样 `w_k^xi` 传播。

---

## B-4：Frozen 终端估计下的鲁棒 tail 内缩

定义时变终端外集合与收紧集合：

\[
\mathcal E_t=\{e:H_te\le h_t\},
\qquad
\mathcal E_t^{shr}=\{e:H_te\le h_t-s_t\}.
\]

B1 需要离线构造一个终端域 `X_{f,t}^{inner}`、tail `kappa_t` 和扰动集合 `D_{fr,t}`，使对每个允许的 Frozen 终端误差 `e` 及每个 `d\in D_{fr,t}`：

\[
F_t^\xi(e+d,\kappa_t(e,u_{last}))-e_{t+1}^{ref}
\in
\mathcal E_{t+1}^{shr}\ominus\mathcal D_{init,t}.
\tag{B4-T}
\]

逐面充分条件是

\[
H_{t+1,r}e_{t+1}^{ext}(e,d)
\le h_{t+1,r}-s_{t+1,r}
-\sigma_{H_{t+1,r}}(\mathcal D_{init,t}).
\tag{B4-S}
\]

若 `F_t^xi` 和 `kappa_t` 是线性/仿射且 `D_fr,t,D_init,t` 为多面体或外多面体，则可通过离线鲁棒线性不等式验证；若它们依赖未约束历史 context 或时变参考集合，非空性仍需单独证明。终端误差使用 `e_N^{fr}` 计算 tail 时，`d_fr` 必须在 B4-S 中量化，不能把 `e_N^{fr}` 当成真实 full 终端。

**状态：`OPEN / BLOCKED`。** 当前模型没有给出局部收缩终端反馈、非空时变鲁棒终端域或统一扰动半径；直接把 B4-T 当假设会封装递归可行结论。

---

## B-5：全时域保持

除终端外，对每个预测时刻 `j` 和每个阶段面 `r`，需要旧移位完整轨迹余量 `\rho_{j,r}` 满足

\[
H_{j,r}e_{j|k}^{shift,full}
 +\|H_{j,r}\|_2\Gamma_{j,k}
\le h_{j,r}-s_{j,r}.
\tag{B5-S}
\]

输入历史和输入增量还必须满足

\[
u_{j|k+1}^{shift}\in\mathcal U_{k+1+j},
\qquad
u_{j|k+1}^{shift}-u_{j-1|k+1}^{shift}
\in\Delta\mathcal U_{k+1+j},
\]

并保持 `u_{-1|k+1}=u_{0|k}`。若原控制器只有输入幅值约束，第二式是拟议增量/终端机制的新约束，不是现有 QP 的既有保证。

**状态：`CONDITIONAL`。** 公式是充分接口；持续余量与初始非空性尚未由当前结构产生。

---

## B-6：下一 Frozen QP 中 shift 候选可行

在 B-EXACT 成立且 `bar U_{k+1}=U_{k+1}^{shift}` 时，新候选自身的 Frozen/full 差异为零。因此新候选满足下一收紧终端约束的关键不再是新 `K_i`，而是：

1. B-2 的真实初值偏差传播；
2. B-4 的旧 full 延长终端内缩；
3. B-5 的全时域输入、阶段、工作域和缓存一致性。

若这三组条件均成立，则

\[
U_{k+1}^{shift}=\bar U_{k+1}
\in\mathcal U_{k+1}^{fr,shr}(\xi_{k+1}^{enc},\bar U_{k+1}),
\]

从而下一 QP 非空。  
**状态：`CONDITIONAL`；在当前控制器下为 `NO-GO`。** B-EXACT 只消除冻结误差，不创造终端内缩。

---

## B-7：初始性与严格归纳

若存在初始收紧可行序列，且 B-4 的时变鲁棒终端域、B-5 的全时域余量在每个绝对时间均由同一离线构造保持，则 B-6 可归纳推出每个下一 QP 非空。

但“每个时刻余量保持”若只是写入假设，等价于把递归可行性藏入假设。非循环版本必须提供一个前向不变的时变终端管束/收缩域：

\[
(e_t,u_{t-1})\in\mathcal X_{f,t}^{inner}
\Longrightarrow
(F_t^\xi(e,u),u)\in\mathcal X_{f,t+1}^{inner}
\]

对所有允许残差、冻结误差、参考残差和输入约束成立，并证明初始终端状态属于该域。

**状态：`CONDITIONAL / weak explanatory value`。** 当前没有该不变域；若将“下一 QP 非空”直接作为前提则 `NO-GO`。

---

## B-8：新 QP 最优解偏离名义

B-EXACT 只保护 `U_{k+1}=\bar U_{k+1}` 这条候选。凸 QP 的最优解通常是另一条 `U_{k+1}^{fr,*}`。要继续归纳，必须保证 QP 的整个可行域都落在 `K_i`、Lipschitz 和终端误差界适用域内，并对任意 QP 可行解重新应用 P4-S/B-3/B-4；或者把终端不变域约束直接作为 QP 硬约束。

因此“名义候选可行”不等于“最优解保留下一轮证书”。若新增终端约束只保证候选，不保证任意最优解，B-8 失败。

**状态：`OPEN / BLOCKED`。** 需要全可行域终端证书，或显式候选保护/备份切换。

---

## B-9：在线复杂度、凸性与修改边界

若 `bar U_{k+1}=shift(U_k^{fr})+tail`，tail 直接由已有 Frozen 终端预测的仿射反馈得到，在线流程可保持：

1. 一次完整名义 rollout；
2. 沿名义轨迹一次冻结；
3. 一次凸 QP。

新增终端集合若为线性面、tail 若为固定仿射/线性规则，则 QP 仍凸。若为非线性 tail、在线鲁棒优化、失败后修复求解或重新冻结迭代，则不能继续声称原始单次结构。

**状态：`CONDITIONAL`。** 结构可保留，但递归可行性证书尚未得到；当前 `Main.tex` 未实现这些修改。

---

## 压力测试

### Test 1：零扰动、零冻结误差

若 `w=0`、B-EXACT 成立且 tail 满足时变终端不变性，B1 退化为标准时变 MPC 的 shift-tail 续接，证明可为 `CONDITIONAL GO`。若仍需额外正裕量，来源是拟议 Frozen 收紧约束，而不是冻结误差。  
**结论：** 该极限不暴露 B-EXACT 问题，但暴露终端集合设计是否非空。

### Test 2：非零一步残差与冻结误差

若 `\|w_k^xi\|\le\bar w`、`d_fr\in D_fr`，终端面至少需要

\[
\sigma_{H_{t+1,r}}(D_{init,t})
+\sigma_{H_{t+1,r}}(D_{fr,t}^{tail})
\le h_{t+1,r}-s_{t+1,r}-\text{nominal margin}_{r}.
\]

当右侧不足时，鲁棒终端内集为空或 shift 候选不满足收紧面。  
**结论：** B1 的真实阻塞是非空鲁棒终端域，不是 QP 凸性。

### Test 3：候选自洽但 QP 最优解偏离名义

即使 `bar U=U_shift` 可行，QP 最优解也可能偏离它；若 QP 可行域允许进入 `K_i` 之外或不保留终端证书，下一轮 B-EXACT 仅保护 warm-start 名义而不保护实际闭环解。  
**结论：** B8 要求全可行域证书或显式可行候选保护；普通 warm-start 不足。

---

## 最终证明裁决

| 义务 | 状态 |
|---|---|
| B-0 状态/缓存一致性 | `CONDITIONAL` |
| B-1 B-EXACT | `CONDITIONAL`（接口完整时局部 `PROVED`） |
| B-2 跨采样 `Gamma` | `CONDITIONAL` |
| B-3 旧 `D_fr` | `CONDITIONAL` |
| B-4 鲁棒终端内缩 | `OPEN / BLOCKED` |
| B-5 全时域保持 | `CONDITIONAL` |
| B-6 下一 Frozen QP 非空 | `CONDITIONAL`；当前控制器 `NO-GO` |
| B-7 严格归纳 | `CONDITIONAL / weak explanatory value` |
| B-8 最优解偏离名义 | `OPEN / BLOCKED` |
| B-9 复杂度与凸性 | `CONDITIONAL` |

**首要阻碍：** 在非零重新编码/冻结误差和时变参考下，尚未构造出非空、可前向保持、与输入缓存一致的鲁棒终端内缩/不变域。B-EXACT 只能消除名义候选上的新冻结误差，不能替代该域。独立未闭合义务还包括跨采样 `Gamma` 的可计算界、全路径工作域保持和 QP 全可行域的下一轮证书；因此“终端内缩/不变域”是首要阻碍而非唯一缺失条件。

因此当前不能批准进入 P5。
