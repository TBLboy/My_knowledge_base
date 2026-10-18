# A1 P4：Frozen/full 理论桥接与递归可行性路线图

日期：2026-10-17  
范围：纯理论；不修改论文正文、代码、实验、图片或正式控制器。  
前提：P0–P3 已完成为 research-only conditional package；本报告不进入 P5 稳定性定理正文。

## 1. P4 的证明对象

P3 研究的是理想完整调度问题。P4 只处理当前一次名义 rollout、一次冻结和一次凸 QP 与理想完整问题之间的桥接：

1. 同一候选输入下 Frozen/full 终端状态差异；
2. 终端约束的逐面收紧；
3. 新增终端成本引起的成本近似误差；
4. Frozen 收紧内集与完整终端可行集不相等时的次优性口径；
5. 当前采样到下一采样重新冻结后的递归可行性。

P4 不改变时变参考轨迹对象，也不把冻结误差当成真实动力学扰动。

## 2. 四类可行集

### 2.1 原输入可行集

\[
\mathcal U_k^{in}
:=\{U=(u_{0|k},\ldots,u_{N-1|k}):
u_{i|k}\in\mathcal U_{k+i}\}.
\]

当前论文只有这一类输入约束；它不包含终端状态约束。

### 2.2 Frozen 收紧内集

给定当前真实增广初值、名义序列 `bar U`、Frozen 预测和终端面 `H_{f,k+N}e\le h_{f,k+N}`，定义：

\[
\mathcal U_k^{fr,shr}(\xi_k,\bar U_k)
:=\{U\in\mathcal U_k^{in}:
H_{f,k+N}e_{k+N}^{fr}(U;\bar U_k)
\le h_{f,k+N}-s_{k+N}^{fr}\}.
\]

该集合是 Frozen QP 实际能够直接施加的线性约束内集。它依赖 `bar U_k`，因此不同采样时刻的集合一般不同。

### 2.3 完整模型终端可行集

\[
\mathcal U_k^{full,term}(\xi_k)
:=\{U\in\mathcal U_k^{in}:
e_{k+N}^{full}(U)\in\mathcal E_{f,k+N}\}.
\]

完整轨迹的终端约束一般对 `U` 非线性，因此该集合不是当前 Frozen QP 直接优化的集合。

### 2.4 真实/观测鲁棒终端可行集

若真实观测层相对完整模型还有差异集合 `D_obs,k+N`，定义：

\[
\mathcal U_k^{obs,term}(\xi_k)
:=\{U\in\mathcal U_k^{in}:
e_{k+N}^{full}(U)+d\in\mathcal E_{f,k+N},
\ \forall d\in\mathcal D_{k+N}^{obs}\}.
\]

若 `0\in D_obs`，则：

\[
\mathcal U_k^{obs,term}
\subseteq
\mathcal U_k^{full,term}.
\]

## 3. 静态包含关系

若逐面收紧量满足：

\[
s_{k+N,r}^{fr}
\ge
\sup_{d\in\mathcal D_{k+N}^{fr}\oplus\mathcal D_{k+N}^{obs}}
(H_{f,k+N})_{r,:}d,
\]

并且该误差集合对**同一候选输入、同一名义序列、同一参考窗口和同一工作域**统一有效，则得到：

\[
\boxed{
\mathcal U_k^{fr,shr}(\xi_k,\bar U_k)
\subseteq
\mathcal U_k^{obs,term}(\xi_k)
\subseteq
\mathcal U_k^{full,term}(\xi_k).}
\tag{P4-1}
\]

P4-1 是静态集合包含，不是递归可行性。它不说明：

- `U_k^{fr,shr}` 非空；
- 下一时刻的名义序列如何选；
- 下一次重新冻结后的收紧集合仍非空；
- 真实执行首输入是否保持所有工作域假设。

**状态：`CONDITIONAL`。**

## 4. 与 `K_i` 的联合终端收紧

现有冻结界只给出同候选比较：

\[
\|z_{i|k}^{full}(U)-z_{i|k}^{fr}(U;\bar U_k)\|_2
\le \bar K_{i,k}(\bar U_k).
\]

若终端窗口包含最后 `P` 个测量槽，并且输入历史在同一候选比较中完全相同，则：

\[
\Delta_{f,k}^{fr}
\le
\left(
\bar K_{N,k}^2
+\sum_{j\in\mathcal I_{hist}(k,N)}
\|C_x\|_2^2\bar K_{j,k}^2
\right)^{1/2}.
\tag{P4-2}
\]

其中 `I_hist(k,N)` 是终端测量窗口中实际由预测轨迹替换的槽位集合；共同真实历史槽位不计入。只有明确窗口端点和索引约定后，才能化为连续整数区间。P4-2 不覆盖真实观测/plant 差异，也不覆盖不同采样时刻之间的名义序列变化。

严格的冻结误差集合定义为：

\[
\mathcal D_{k+N}^{fr}
:=\{d:d=\xi_{k+N}^{full}(U)-\xi_{k+N}^{fr}(U;\bar U_k),\ U\text{ 属于同一比较域}\}.
\]

若只掌握 P4-2，则使用外球

\[
\mathcal D_{k+N}^{fr}
\subseteq\{d:\|d\|_2\le\Delta_{f,k}^{fr}\}.
\]

因此支持函数链条是：

\[
K_i\to\Delta_{f,k}^{fr}\to\mathcal D_{k+N}^{fr}
\to(\mathcal D_{k+N}^{fr}\oplus\mathcal D_{k+N}^{obs})
\to s_{k+N}^{fr}.
\]

这里统一采用 P3 的状态层次：

\[
\eta_{k+N}=\operatorname{col}(z_{k+N},X_{k+N},U_{k+N}^{in}),
\qquad
\xi_{k+N}=\operatorname{col}(\eta_{k+N},u_{N-1|k}).
\]

在同一候选比较下，输入历史块差异为零；若 `I_hist(k,N)` 是实际被预测轨迹替换的测量槽位集合，则

\[
\eta_{k+N}^{full}-\eta_{k+N}^{fr}
=\operatorname{col}(z_{k+N}^{full}-z_{k+N}^{fr},
\Delta X_{k+N}^{full-fr},0),
\]

and the full joint difference is

\[
\xi_{k+N}^{full}-\xi_{k+N}^{fr}
=\operatorname{col}(\eta_{k+N}^{full}-\eta_{k+N}^{fr},0),
\]

because the same candidate input supplies the same terminal previous-input block.

\[
\|\Delta X_{k+N}^{full-fr}\|_2^2
\le\sum_{j\in\mathcal I_{hist}(k,N)}
\|C_x\|_2^2\bar K_{j,k}^2.
\]

若终端误差采用相对参考坐标，则定义

\[
e_{k+N}^{full/fr}:=\xi_{k+N}^{full/fr}-\xi_{k+N}^{ref},
\]

从而 `e^{full}-e^{fr}=xi^{full}-xi^{fr}`。这补齐了 `K_i -> Delta_f -> D_fr` 的维度和坐标接口。

当前仍需注意：P4-2 先给出 `eta` 块的外球界；由于输入历史块在同候选比较中为零，才可将同一半径嵌入完整 `xi` 块。该嵌入是条件映射，不是把 `K_i` 直接解释成独立上一输入误差界。

对终端面 `H_f e\le h_f`，逐面收紧为：

\[
(s_{k+N}^{fr})_r
=\sup_{d\in\mathcal D_{k+N}^{fr}\oplus\mathcal D_{k+N}^{obs}}
(H_{f,k+N})_{r,:}d.
\tag{P4-3}
\]

若只使用二范数球，则 P4-3 退化为逐行范数乘半径。总成本误差 `epsilon_J` 不能替代 P4-3。

## 5. 新终端成本下的近似界

设新增终端成本为：

\[
J_{f,k}(\xi)=\xi^\top P_{f,k+N}\xi,
\qquad P_{f,k+N}\succeq0.
\]

在同一候选和共同工作域内，若：

\[
\|\xi_{N,k}^{full}\|,
\|\xi_{N,k}^{fr}\|\le M_{f,k},
\qquad
\|\xi_{N,k}^{full}-\xi_{N,k}^{fr}\|
\le\Delta_{f,k}^{fr},
\]

则：

\[
|J_{f,k}^{full}-J_{f,k}^{fr}|
\le
2\|P_{f,k+N}\|_2M_{f,k}\Delta_{f,k}^{fr}.
\tag{P4-4}
\]

若原输出成本差异界为 `epsilon_J^{out}`，则候选总界为：

\[
\epsilon_{J,k}^{total}
:=\epsilon_{J,k}^{out}
+2\|P_{f,k+N}\|_2M_{f,k}\Delta_{f,k}^{fr}.
\tag{P4-5}
\]

P4-5 只有在完整/Frozen 使用同一终端成本、同一参考目标和同一比较集合时成立。它不处理可行集不相等。

### 5.1 误差项排他账本

- `epsilon_J^{out}` 只包含原输出跟踪成本的 full/fr 差异，不包含新增终端项；
- P4-4 只包含新增终端成本差异；
- `D_fr` 只进入终端状态收紧及其对应终端成本差异，不再进入真实动态扰动；
- `D_obs` 若已进入 P4-3，则不得在同一链条中再次作为独立终端观测误差加入；
- `epsilon_set` 只表示收紧可行集与完整终端可行集的最优值差异，不包含目标函数 full/fr 差异；
- `eta_solver` 只表示 QP 数值次优性，不是状态扰动。

因此 P4-7 中各项是互斥的比较接口，不能重复累加同一冻结或观测误差。

## 6. 可行集不相等时的次优性口径

Frozen QP 优化 `U_k^{fr,shr}`，而完整问题可能定义在 `U_k^{full,term}`。通常只有包含，不是等号。

### 6.1 共同内集价值

可将理论价值改定义为：

\[
V_{N,k}^{shr}(\xi_k)
:=\min_{U\in\mathcal U_k^{fr,shr}}
J_{N,k}^{full}(\xi_k,U).
\]

在同一 `U_k^{fr,shr}` 上，若 P4-5 成立且 QP 数值误差为 `eta_solver,k`，则候选近似界为：

\[
J_{N,k}^{full}(\xi_k,U_k^{fr})
-V_{N,k}^{shr}(\xi_k)
\le2\epsilon_{J,k}^{total}+\eta_{solver,k}.
\tag{P4-6}
\]

这是最干净的 Frozen/full 比较口径，但价值对象已经从完整终端全集改成 Frozen 收紧内集。

### 6.2 完整全集价值

若仍希望比较：

\[
V_{N,k}^{full}(\xi_k)
:=\min_{U\in\mathcal U_k^{full,term}}J_{N,k}^{full}(\xi_k,U),
\]

则需要集合损失：

\[
\epsilon_{set,k}
:=V_{N,k}^{shr}(\xi_k)-V_{N,k}^{full}(\xi_k)\ge0.
\]

于是：

\[
J_{N,k}^{full}(\xi_k,U_k^{fr})-V_{N,k}^{full}(\xi_k)
\le2\epsilon_{J,k}^{total}
+\eta_{solver,k}
+\epsilon_{set,k}.
\tag{P4-7}
\]

若 `epsilon_set` 没有可控上界，P4-7 形式正确但信息量可能为零。不能把它省略，也不能继续使用未修正的 `2 epsilon_J`。

## 7. 三个递归可行性关口

### Gate P4-S：静态包含

P4-1 至 P4-3 若成立，可得当前 Frozen 收紧解覆盖 full/obs 终端约束。状态：**CONDITIONAL**。

### Gate P4-T：理想完整终端续接

P3-C 已给出联合终端状态 `xi` 下的条件续接命题。若当前 Frozen 解属于 `U_k^{full,term}(xi_k)`，还需将 full 终端状态明确写成

\[
\xi_{k+N}^{full}
=\operatorname{col}(\eta_{k+N}^{full},u_{N-1|k}),
\]

并确认该 `u_{N-1|k}` 是 P3-C 所需的终端上一输入缓存；若 `D_obs` 未被 P4-3 吸收，还需单独证明真实观测终端状态与该 full 联合状态的桥接。满足这些条件后才能调用 P3-C。状态：**CONDITIONAL**。

此外，P4 终端误差集合必须与 P3-C 的联合终端集合使用同一坐标：

\[
e\in\mathcal E_{f,t}^{e}
\quad\Longleftrightarrow\quad
\xi_t=\xi_t^{ref}+e\in\mathcal X_{f,t}.
\]

只有证明上述对应关系（或至少一方包含另一方），才能把 P4-T 的终端包含传递给 P3-C；否则 P4-T 仍只是接口候选，不能视为已完成桥接。

### Gate P4-R：跨采样重新冻结

要得到下一次 Frozen QP 的可行性，必须证明：

\[
U_{k+1}^{+}
\in
\mathcal U_{k+1}^{fr,shr}(\xi_{k+1},\bar U_{k+1}).
\tag{P4-8}
\]

但现有 `K_i` 只比较固定 `bar U_k` 下同一候选的 full/fr 差异；它不提供：

- `bar U_{k+1}` 的选择规则；
- 新冻结矩阵与旧冻结矩阵的变化界；
- 真实新初值和历史重编码误差下的收紧裕量；
- 下一收紧内集的非空性。

因此 P4-8 不能由 P4-1 或 P3-C 自动推出。

**当前状态：`OPEN / BLOCKED`。**

## 8. P4 当前裁决

| 义务 | 状态 |
|---|---|
| Frozen QP 加终端收紧仍保持凸性 | `GO`（结构性） |
| 同候选 `K_i` 到联合终端收紧 | `CONDITIONAL` |
| 静态 Frozen/full/obs 集合包含 | `CONDITIONAL` |
| 同一收紧内集上的成本近似 | `CONDITIONAL` |
| 完整全集的 `epsilon_set` 比较 | `CONDITIONAL / 信息量依赖上界` |
| 理想完整终端续接 | `CONDITIONAL`（复用 P3-C） |
| 跨采样重新冻结递归可行 | `OPEN / BLOCKED` |
| 当前正式控制器已具备 P4 递归可行性 | `NO-GO` |

## 9. 最小调整建议

若要求在不改变正式控制器的条件下继续证明，只能把跨采样重新冻结递归可行性作为强假设，至少明确：

1. 名义序列 `bar U_{k+1}` 的确定性更新规则；
2. 相邻冻结矩阵/预测映射的统一变化界；
3. 收紧内集存在统一 Slater 裕量；
4. 真实首输入执行后 `xi_{k+1}` 仍在共同工作域；
5. P4-8 对所有闭环时刻成立。

这会是 A0/P4 型强假设模板，而不是当前算法自动性质。

若不接受这些强假设，最小实质性控制器调整是增加一个可证明的递归可行机制，例如固定/可行 warm-start 续接或显式鲁棒终端管束；这需要用户另行批准，本报告不实施。

**P4 总结：** 静态 Frozen/full 桥接可条件化；跨采样重新冻结是当前正式控制器的核心未闭合点。因此在没有额外强假设或控制器调整前，不进入 P5 稳定性定理正文。

## 10. P4-R 的非自动性命题

**命题 P4-R（结构性边界）。** 仅由以下事实不能推出跨采样递归可行性：

1. 当前 Frozen QP 是凸的；
2. 当前 `U_k^{fr,shr}` 满足 P4-1 的静态集合包含；
3. 当前完整终端状态满足 P3-C 的理想终端续接条件；
4. 固定当前名义序列 `bar U_k` 时存在 `K_i` 冻结界。

要推出 P4-8，还必须新增一个跨采样条件，至少包括：

\[
\bar U_{k+1}=\mathscr W(\xi_{k+1},U_k^{fr})
\]

的确定性名义更新规则，以及对该规则诱导的下一冻结映射满足：

\[
\mathcal U_{k+1}^{fr,shr}(\xi_{k+1},\bar U_{k+1})
\ne\varnothing
\]

并且移位续接序列属于该集合。

**理由。** P4-1 比较的是固定 `bar U_k` 下同一候选 `U` 的 full/fr 终端差异；P4-8 改变了初值、名义序列、冻结矩阵和收紧集合。没有相邻名义映射的变化界或显式可行 warm-start，前一个集合的包含关系对后一个集合没有逻辑约束。因此把 P4-1、P3-C 和 `K_i` 直接串成 P4-8 是跨越了一个未证明的映射。

**状态：** 当前正式控制器的 P4-R 为 `OPEN / BLOCKED`；若不增加跨采样强假设或可行性机制，则整体 P4 递归可行性为 `NO-GO`。

## 11. P4 交付裁决

- 静态 Frozen/full/obs 桥接：`CONDITIONAL`；
- 新终端成本与同一收紧内集次优性：`CONDITIONAL`；
- 完整全集比较：`CONDITIONAL`，但 `epsilon_set` 可能无信息；
- 理想完整终端续接：`CONDITIONAL`，复用 P3-C；
- 跨采样重新冻结递归可行：`OPEN / BLOCKED`；
- 当前正式控制器的递归可行性：`NO-GO`；
- P5 实际稳定性定理：**停止，不继续堆叠**。

若继续理论工作，下一份最小报告应只研究“跨采样名义更新 + 收紧内集保持”的强假设是否可被压缩为一个清晰的 A0/P4 条件模板；不得把它写成当前实现已经满足的性质。
