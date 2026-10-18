# Transformer–Koopman 时变轨迹闭环理论重构简报

**用途：** 提供给外部 GPT 做理论路线评审。  
**日期：** 2026-10-17  
**当前阶段：** 理论路线重构与逻辑压力测试；不是数值验证阶段。  
**范围：** 只讨论理论对象、证明结构、假设边界和路线选择；不修改论文正文、代码、实验、图片或正式控制器。

---

## 1. 目标与请评审的问题

### 1.1 总目标

将历史条件 Transformer–Koopman 调度预测器与 Frozen-LTV MPC 的现有有限时域结果，重构为**时变参考轨迹跟踪**下的条件闭环实际稳定性/最终有界性理论。

首个理论对象限定为：

\[
\text{模型增广状态/测量历史的条件实际稳定性或最终有界跟踪}。
\]

暂不把结论升级为物理 plant 稳定性，也不把问题改成固定参考点调节。

### 1.2 请 GPT 重点回答

1. 当前 A1 证明树是否逻辑闭合，哪些条件是必要的，哪些只是过强的充分条件？
2. 时变价值函数、参考移位、输入增量成本和终端续接是否应采用另一种更简洁的统一定义？
3. Frozen/full 可行集不相等时，如何严谨表述 Frozen QP 的条件次优性？
4. 冻结误差、参考残差、重新编码残差和 plant 误差的分层是否正确，是否仍有重复计入？
5. 在不改变 Frozen QP 在线结构的前提下，A1 是否比 A0 更值得继续？
6. 哪些理论内容已经足以写成“条件模板”，哪些必须明确标注为未证明？
7. 是否存在比当前 A1 更小、更清晰、但仍保持时变轨迹跟踪的理论路线？

---

## 2. 事实来源与范围边界

### 已确认

- 工程根目录：`D:/Project/Transformer-Koopman`。
- 真实 Git 仓库：`Transformer-Koopman/`，当前分支为 `paper`，HEAD 记录为 `8d14a40`。
- 论文正文：`Transformer-Koopman/论文/新版本/Main.tex`。
- 当前工作区原本已有 `Main.tex` 未提交修改；本轮理论重构没有修改该文件。
- Phase A 报告：`.project-log/docs/ClosedLoop_Theory_Feasibility_A.md`。
- Phase B 报告：`.project-log/docs/ClosedLoop_Theory_Feasibility_B.md`。
- A1 终端候选报告：`.project-log/docs/ClosedLoop_Theory_Terminal_Candidate.md`。
- 本简报只服务于理论评审，不代表正式论文内容。

### 明确不做

- 不运行实验，不绑定 checkpoint，不计算具体 `K_t/P_{f,t}`。
- 不选择具体数值参考轨迹作为当前理论交付物。
- 不做 QP 非空性数值测试或矩阵数值验证。
- 不修改正式控制器定义。
- 不把任何候选条件写成已证明的闭环稳定性结论。

### 当前未知

- 是否存在满足全部 A1 条件的实际终端矩阵、反馈和终端集合。
- Frozen 收紧后的可行集是否始终非空并递归非空。
- 价值函数对完整增广状态是否正定、检测和连续。
- 物理 plant 到模型增广状态之间是否存在可验证的稳定性桥梁。

---

## 3. 当前系统理论对象

### 3.1 状态与历史

严格区分：

- 物理状态：`s`；
- 测量状态：`x=h(s)`；
- 提升状态：`z`；
- 真实/重新编码提升状态：`z^{enc}`；
- 递归预测提升状态：`z^P`；
- 测量历史窗口：`X`；
- 过去输入窗口：`U^{in}`。

当前采用最小模型增广状态：

\[
\eta=\operatorname{col}(z,X,U^{\mathrm{in}}),
\qquad
n_\eta=d+Pn+(P-1)m.
\]

上一实际输入不再作为独立状态重复存储，而由 `U^{in}` 的最后一个块提取：

\[
u_{\mathrm{last}}=E_uU^{\mathrm{in}}.
\]

### 3.2 完整调度模型

\[
\begin{aligned}
z^+&=A(C_\phi(X,U^{\mathrm{in}}))z+B(C_xz)u,\\
x^+&=C_xz^+,\\
X^+&=S_xX+b_xx^+,\\
(U^{\mathrm{in}})^+&=S_uU^{\mathrm{in}}+b_uu,\\
\eta^+&=\mathcal F_\eta(\eta,u).
\end{aligned}
\]

一致性流形至少包括：

\[
X[-1]=C_xz.
\]

理论不能把 `z`、`X` 和 `U^{in}` 当作完全独立的自由直积坐标而忽略该约束。

### 3.3 Frozen-LTV 结构

在每个采样时刻，以名义输入序列冻结调度矩阵，得到：

\[
Z^{\mathrm{fr}}=F_k+G_kU.
\]

因此当前 Frozen 在线问题是一次凸 QP：

- 状态预测对 `U` 仿射；
- 输入跟踪和输入增量成本为凸二次项；
- 输入约束为线性约束；
- 若增加 PSD 时变终端二次项，Hessian 仍增加 PSD 项；
- 若增加线性终端管束，约束仍保持线性。

这只证明 QP 结构，不证明闭环稳定性。

---

## 4. Phase A 已完成的理论判断

### 4.1 已保留的现有理论

当前论文已有或可继续使用：

1. 低秩调度矩阵的范数/Lipschitz 界；
2. 有限时域预测误差递推与预测界；
3. Frozen-LTV 名义 rollout；
4. `Z=F+GU` 的仿射凝结；
5. 首步冻结误差为零；
6. 多步 Frozen/full 状态冻结误差界 `K_i`；
7. Frozen/full 目标函数近似界 `epsilon_J`；
8. 在同一非空可行集上的条件次优性界 `2 epsilon_J + eta`。

### 4.2 这些结果不能直接推出的内容

它们不能单独推出：

- 递归可行性；
- 时变价值函数下降；
- 模型增广状态实际稳定或最终有界；
- 物理 plant 稳定；
- 渐近稳定性。

### 4.3 MAKO 的迁移边界

可以借鉴 MAKO 的证明树组织：

\[
\text{模型误差性质}
\rightarrow
\text{价值函数}
\rightarrow
\text{相邻采样时刻移位}
\rightarrow
\text{闭环结论}。
\]

不能直接迁移：

- 在线 Koopman 参数更新律；
- 参数收敛证明；
- 参数误差 Lyapunov 项；
- MAKO 的稳定性结论。

原因是本项目的 `A(c)`、`B(x)` 来自历史前向调度，单次 QP 内冻结、下一时刻重新生成，不存在 MAKO 同型的在线参数适应律。

---

## 5. 路线比较

### A0：保持现有 MPC，只增加强理论假设

保持现有 Frozen QP、成本和输入约束。需要显式假设：

- 对 Frozen 输出存在完整模型的时变移位续接序列；
- 终端/工作域前向不变；
- `V_{N,k}` 对目标增广误差正定或检测；
- `V_{N,k}` 对真实采样误差连续；
- 闭环可达域内预测/残差界统一有效；
- 参考序列、输入参考和输入增量项满足时变移位代数。

判断：

- 作为条件模板：**CONDITIONAL GO**；
- 作为当前算法已经具备稳定保证：**NO-GO**；
- 缺点：最困难的终端/可行性内容大多被封装为假设。

### A1：时变终端二次成本 + 线性收紧终端管束 + 局部终端反馈

这是当前优先路线。候选终端误差可定义为：

\[
e_t=\eta_t-\eta_t^{\mathrm{ref}}.
\]

终端成本：

\[
V_{f,t}(e_t)=e_t^\top P_{f,t}e_t,
\qquad P_{f,t}\succeq0
\]

或对完整一致性状态取正定矩阵。

终端辅助反馈只用于理论续接：

\[
u_t^+=u_t^{\mathrm{ref}}+K_te_t.
\]

它不是当前 Frozen QP 实际执行的最后一个输入。

判断：

- Frozen QP 凸性：**GO**；
- 终端设计接口：**CONDITIONAL GO**；
- 模型增广状态实际稳定/最终有界：**CONDITIONAL GO**；
- 当前是否已经证明：**NO-GO**。

### B：鲁棒/管束 MPC

直接把冻结误差、观测/plant 误差和动态扰动作为管束对象，集合语义更自然。但可能改变在线优化结构、约束传播或控制器定义，也不能自动解决检测性和物理 plant 桥梁。

当前定位：备选，不因 A1 尚未闭合而立即切换。

### C：完整非线性/调度在线优化

可以减少 Frozen/full 之间的错位，但通常失去单次凸 QP，并引入非凸在线求解和实时性问题。

当前定位：不推荐。

---

## 6. A1 已完成的核心推理

### 6.1 完整增广 Jacobian

对 `f_z(z,X,U^{in},u)` 的偏导块记为：

\[
F_z^z,\quad F_z^X,\quad F_z^U,\quad G_z.
\]

则完整时移 Jacobian 具有块结构：

\[
A_{\eta,t}=
\begin{bmatrix}
F_z^z&F_z^X&F_z^U\\
b_xC_xF_z^z&S_x+b_xC_xF_z^X&b_xC_xF_z^U\\
0&0&S_u
\end{bmatrix},
\]

\[
B_{\eta,t}=
\begin{bmatrix}
G_z\\
b_xC_xG_z\\
b_u
\end{bmatrix}.
\]

因此终端 Lyapunov/下降条件必须作用于完整增广动力学，不能只对 `z` 的局部线性化做结论。

### 6.2 局部二次下降条件

候选时变离散 Lyapunov 条件：

\[
(A_{\eta,t}+B_{\eta,t}K_t)^\top P_{f,t+1}
(A_{\eta,t}+B_{\eta,t}K_t)-P_{f,t}
\preceq-Q_{f,t}.
\]

这只是离线/理论条件，不进入在线 QP。

非线性余项、参考不可实现残差、重新编码残差和 plant 误差需要另行上界。

### 6.3 冻结界到联合终端误差

现有 `K_i` 直接约束的是：

\[
\|z_i^{\mathrm{full}}-z_i^{\mathrm{fr}}\|\le \bar K_i.
\]

在同一候选 `U`、同一参考窗口和同一共同初始历史下：

- 输入历史槽差异为零；
- 新测量槽由 `C_x z` 读出；
- `N<P` 时，终端窗口的前部槽位仍是共同真实历史；
- 只有预测槽贡献冻结差异。

因此联合终端冻结界候选为：

\[
\Delta_{f,k}^{\mathrm{fr}}
\le
\left(
\bar K_{N,k}^2+
\sum_{j=\max(1,N-P+1)}^N
\|C_x\|_2^2\bar K_{j,k}^2
\right)^{1/2}.
\]

这不是现实闭环误差界，也不适用于不同候选输入、理论续接序列或真实下一步缓存更新。

### 6.4 逐面收紧

若终端集合为：

\[
\mathcal E_{f,t}=\{e:H_{f,t}e\le h_{f,t}\},
\]

冻结/观测差异集合为 `D_term`，则 Frozen QP 应采用逐面支持函数：

\[
H_{f,t}e_t^{\mathrm{fr}}
\le h_{f,t}-s_t,
\]

\[
(s_t)_r=\sup_{d\in\mathcal D_t^{\mathrm{term}}}
(H_{f,t})_{r,:}d.
\]

总成本误差 `epsilon_J` 不能替代逐约束收紧量。

### 6.5 三类可行集

需要区分：

\[
\begin{aligned}
\mathcal U_k^{\mathrm{in}}&=\text{原输入可行集},\\
\mathcal U_k^{\mathrm{fr,shr}}&=\text{满足 Frozen 收紧终端约束的内集},\\
\mathcal U_k^{\mathrm{full,term}}&=\text{满足完整终端约束的集合}.
\end{aligned}
\]

通常只有：

\[
\mathcal U_k^{\mathrm{fr,shr}}
\subseteq
\mathcal U_k^{\mathrm{full,term}},
\]

而非等号。

所以原 `2 epsilon_J` 次优性不能无条件沿用。严格选择有两种：

1. 在同一 Frozen 收紧内集上重新定义完整理论价值；
2. 证明完整最优解属于收紧内集，或给出投影代价 `epsilon_set`。

### 6.6 递归可行性链

理论链条应为：

\[
\begin{aligned}
e_{k+N}^{\mathrm{fr}}&\in\mathcal E_{f,k+N}^{\mathrm{shr}},\\
e_{k+N}^{\mathrm{full}}&=e_{k+N}^{\mathrm{fr}}+d_{k+N}^{\mathrm{fr}}\in\mathcal E_{f,k+N},\\
e_{k+N}^{\mathrm{obs}}&=e_{k+N}^{\mathrm{full}}+d_{k+N}^{\mathrm{obs}},\\
e_{k+N+1}&\in\mathcal E_{f,k+N+1},\\
U_{k+1}^+&\in\mathcal U_{k+1}^{\mathrm{fr,shr}}.
\end{aligned}
\]

任何一步缺失，都不能声称递归可行。

---

## 7. 时变价值函数与移位代数

### 7.1 严格价值函数对象

由于参考序列随采样时刻移动，必须使用：

\[
V_{N,k}(\eta)
=\inf_{U\in\mathcal U_{k}^{\mathrm{feas}}(\eta)}J_{N,k}(\eta,U).
\]

不能把一般时变跟踪问题简写成固定的 `V_N`。

### 7.2 当前成本的移位

现有成本包含：

- 测量输出跟踪；
- 输入参考跟踪；
- 绝对输入增量 `\|u_i-u_{i-1}\|_S^2`。

下一时刻候选序列为：

\[
U^+=(u_1,\ldots,u_{N-1},u_N^+).
\]

严格移位时：

- 当前 `u_0` 的输入偏差成本被删除；
- 当前 `u_0-u_{-1}` 的输入增量成本被删除；
- 中间输入/参考项按绝对时间移位；
- 旧终端输出项变成下一问题的阶段输出项；
- 新的末端输入参考、末端输入增量和新终端成本必须由终端条件吸收。

候选终端条件为：

\[
\begin{aligned}
V_{f,k+N+1}(\eta_{N+1}^+)-V_{f,k+N}(\eta_N)
&+q_{k+N}(y_N)\\
&+r_{k+N}(u_N^+)
 +s_{k+N}(u_N^+,u_{N-1})
\le0.
\end{aligned}
\]

这只是条件接口，当前没有证明。

### 7.3 误差分层

必须区分：

1. `d_ref`：参考轨迹不满足模型增广递推的残差；
2. `d_model`：模型重新编码/真实采样与完整模型之间的误差；
3. `d_freeze`：同一候选输入下 Frozen/full 预测差异；
4. `d_plant`：物理 plant 与模型/测量之间的误差。

当前采用的唯一口径：

- `d_freeze` 只进入 Frozen/full 代价近似和终端约束收紧；
- `d_ref` 在误差映射 `Phi_t` 中显式体现；
- `D_dyn` 不再重复包含 `d_ref`；
- `d_model` 和 `d_plant` 仍需具体桥梁或强假设。

### 7.4 候选闭环下降式

目标形式是：

\[
\Delta V_{N,k}
\le-\ell_k
+2\varepsilon_{J,k}^{\mathrm{total}}
+\eta_k
+\omega_{V,k+1}(\bar d_k^{\mathrm{dyn}}).
\]

其中：

- `epsilon_J,total` 包含新增终端成本的 Frozen/full 差异；
- `eta_k` 是 Frozen QP 数值次优性；
- `omega_V` 是价值函数连续性误差；
- `d_freeze` 不应再次进入动态扰动项。

该式仍是候选模板，不是已证明定理。

---

## 8. 当前理论状态分类

### 结构上已成立 / 可直接从现有定义支持

- Frozen 仿射预测结构 `Z=F+GU`。
- PSD 终端二次项不会破坏 Frozen QP 凸性。
- 线性终端约束不会破坏 Frozen QP 凸性。
- 当前有限时域预测界、冻结界和同一可行集上的代价近似工具。
- 最小增广状态和完整历史移位 Jacobian 的形式。
- 时变价值函数必须带 `k` 索引。

### 可作为强假设 / 条件模板

- 完整增广终端动力学存在局部 Jacobian/包络。
- 存在时变 `K_t,P_{f,t}` 和终端集合。
- T9 二次下降条件成立。
- T32 鲁棒前向包含成立。
- T33/B12 时变终端成本移位下降成立。
- 收紧 Frozen 可行集非空且递归非空。
- `V_{N,k}` 对目标增广误差正定/检测且连续。
- 参考序列具备模型可实现性或有界残差。

### 当前待推导 / 未闭合

- 由现有 `K_i` 得到完整终端误差收紧后，如何保证所有终端面有足够裕量。
- 时变终端集合和 Frozen 收紧内集的递归非空。
- 共同可行集口径下的正确次优性界。
- `V_{N,k}` 在状态相关可行集下的连续性。
- 隐藏提升坐标、历史缓存和输入历史的有限窗口检测性。
- 非零误差项下从价值下降到最终有界半径的严格转换。

### 当前明确不可证 / NO-GO

- 仅凭现有 `2 epsilon_J + eta` 证明闭环稳定。
- 仅增加终端二次项就自动得到递归可行性。
- 从模型增广状态稳定直接推出物理状态 `s` 稳定。
- 直接移植 MAKO 的在线参数收敛和 Lyapunov 结论。
- 在没有 plant–model 误差、检测性和工作域不变性桥梁时声称物理 plant 稳定。

---

## 9. 当前最合理的理论路线

### 推荐主线：A1，但只作为理论候选

保持时变轨迹跟踪和 Frozen QP 在线结构，研究：

\[
\text{完整增广误差}
\rightarrow
\text{时变终端集合}
\rightarrow
\text{Frozen 逐面收紧}
\rightarrow
\text{共同可行}
\rightarrow
\text{B12/T33 价值下降}
\rightarrow
\text{条件实际稳定/最终有界}.
\]

### A0 的作用

作为不改变控制器的强假设基线，用来说明：如果不引入终端设计，理论需要把哪些内容直接假设进去。

### B/C 的作用

- B：作为鲁棒管束方向的备选；
- C：作为牺牲单次凸 QP 后的完整非线性方向；
- 当前都不应抢先替代 A1。

---

## 10. 给 GPT 的评审边界

请不要把下面内容当作已完成事实：

- A1 终端矩阵存在；
- T9/T32/T33 已成立；
- Frozen 收紧 QP 始终非空；
- `V_{N,k}` 已正定或 Lipschitz；
- 模型增广状态已实际稳定；
- 物理 plant 已稳定。

本阶段需要的是**纯理论路线评审和推理修正**，不是数值实验设计。若建议下一步，请优先建议：

1. 更小的理论对象；
2. 更清晰的假设分层；
3. 更严谨的时变移位/终端下降证明树；
4. 对 Frozen/full 可行集错位的正确表述；
5. 对模型增广层与物理 plant 层的边界表述。

---

## 11. 相关文件

- `.project-log/docs/ClosedLoop_Theory_Feasibility_A.md`：Phase A 路线与 MAKO 迁移边界。
- `.project-log/docs/ClosedLoop_Theory_Feasibility_B.md`：Phase B 的 `V_{N,k}`、时变成本移位、A0/A1 接口。
- `.project-log/docs/ClosedLoop_Theory_Terminal_Candidate.md`：A1 终端候选、T6–T47 和证明义务矩阵。
- `Transformer-Koopman/论文/新版本/Main.tex`：现行模型、预测界、Frozen QP、冻结界和有限时域次优性。

**交接结论：** 当前最重要的工作不是做数值验证，而是请外部评审判断上述 A1 理论路线是否值得继续，以及如何把它压缩成一个逻辑最小、假设透明、不会过度宣称的时变轨迹闭环理论。
