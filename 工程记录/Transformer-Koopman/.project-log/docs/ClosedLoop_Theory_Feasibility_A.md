# Closed-loop theory feasibility analysis A

日期：2026-10-17；任务：TASK-063。范围：只读分析，未修改 `Main.tex`、代码、实验或图片。

## 1. 结论

### 总裁决：CONDITIONAL GO（只推荐进入 Phase B，不推荐现在重写正文）

可以借鉴 MAKO 的证明树组织方式，但当前 Frozen-LTV MPC 还不能直接新增闭环稳定性定理。推荐目标分层为：

1. 先对完整调度模型建立条件有限时域价值下降不等式；
2. 在终端、可行性、检测性和局部误差条件下，争取模型增广状态的条件实际稳定性/最终有界性；
3. 只有残差、冻结近似误差和求解误差以状态相关方式消失，或在理想零误差特例下，才讨论渐近稳定性；
4. 当前不建议直接声称物理状态 `s` 稳定，因为 `s`、测量 `x`、提升代理 `z` 和历史增广状态不是同一对象。

当前最成熟的主结论仍是有限时域预测界、冻结轨迹界、统一代价近似界和条件 Frozen 优化次优性。闭环稳定性必须先通过 Phase B 闸门。若最终目标是物理 plant 的闭环稳定性，还必须补充 plant--模型误差界、闭环可达域上的统一有效性、工作域不变性，以及历史测量到物理状态的检测性/等价性条件。

## 2. 现行版本核对

- 工程：`D:/Project/Transformer-Koopman`；内层仓库：`Transformer-Koopman/`。
- 分支：`paper`；HEAD：`8d14a40`。
- 工作区：仅 `论文/新版本/Main.tex` 有 TASK-062 未提交改动；本报告未修改它。
- 当前论文文件：`Transformer-Koopman/论文/新版本/Main.tex`。
- 现有接口：模型 `eq:scheduled_predictor`；调度 `eq:transition_schedule`、`eq:low_rank_schedules`；残差 `eq:residual_definition`；假设 A1–A4；预测界 `thm:prediction_bound`；完整控制模型 `eq:complete_control_model`；成本 `eq:full_cost`；Frozen QP `eq:quadratic_template`；冻结界 `eq:freezing_bound`；代价界 `eq:uniform_cost_certificate`；次优性 `thm:suboptimality`。
- 本报告使用本机 fitz 提取用户 PDF，并定位 MAKO p.4–p.7 的 Section 3.3、Theorem 1/2、Section 4.1、价值函数比较、Theorem 3/Corollary 1。PDF 文本部分字符存在提取乱码，故不把乱码当作精确公式证据；MAKO 的逐条定理—假设—公式映射仍需在 Phase B 补齐。

## 3. 建议的闭环分析对象

控制器每次采样都更新历史、重新编码和重新调度；只使用当前 `x_k` 通常不足。建议定义模型增广状态

\[
\zeta=(z,X,U^{\rm in}),
\qquad \zeta_k^{\rm obs}=(g_\theta(X_k),X_k,U_k^{\rm in}).
\]

完整调度的一步映射应为

\[
\begin{aligned}
z^+&=A(C_\phi(X,U^{\rm in}))z+B(C_xz)u,\\
x^+&=C_xz^+,\\
X^+&=\operatorname{shift}(X,x^+),\\
(U^{\rm in})^+&=\operatorname{shift}(U^{\rm in},u),\\
\zeta^+&=\mathcal F(\zeta,u).
\end{aligned}
\]

当前一步残差

\[
r_k=z_{k+1}^{\rm enc}-A(c_k)z_k^{\rm enc}-B(x_k)u_k
\]

可作为真实重新编码状态与完整调度模型第一步之间的接口误差。若无额外观测噪声且历史旧槽位一致，可候选建立

\[
\|\zeta_{k+1}^{\rm obs}-\mathcal F(\zeta_k^{\rm obs},u_k)\|
\le c_\zeta\|r_k\|,
\]

但 `c_zeta` 必须按实际增广范数逐坐标推导，当前不能直接写成定理；A3 目前只是有限预测比较中的统一残差假设，不能未经扩域证明直接当作闭环所有可达历史和真实 plant 轨迹上的误差保证。

必须避免偷用

\[
g_\theta(\hat X_{i+1})\equiv z^P_{i+1}.
\]

递归传播状态不自动等于对预测窗口重新编码的状态。

## 4. 可保留的现有理论

以下内容建议保留：

1. 低秩调度矩阵的范数界和 Lipschitz 界；
2. A1–A3 与 `eq:prediction_recurrence`；
3. `thm:prediction_bound` 有限时域开放环预测界；
4. Frozen-LTV 名义 rollout、固定矩阵、`Z=F+GU` 和凸 QP；
5. `eq:first_step_freezing_exact` 的首步精确性；
6. `prop:uniform_freezing_bound`、`prop:uniform_cost_certificate` 和 `thm:suboptimality`。

但后三项应定位为控制误差工具和有限时域近似优化结果，不能单独升级为闭环稳定性或递归可行性证明。

## 5. MAKO 可借鉴与不可借鉴之处

MAKO 的组织方式是“模型误差性质 → MPC 价值函数 → 相邻采样时刻移位比较 → 闭环结论”。这正是当前论文缺少的连接。

但 MAKO p.4–p.5 的 Theorem 1/2 依赖在线 Koopman 参数梯度更新律和特定学习率，并用参数误差迹构造 Lyapunov 函数。我们的 `A(c)`、`B(x)` 是历史前向调度；单次 QP 内冻结，下一时刻重新生成，不能假设矩阵变化趋零，也不能移植 MAKO 的参数收敛证明。

MAKO p.5–p.6 的闭环证明还依赖终端等式约束、移位序列、终端控制/终端项、特定价值函数以及模型更新误差趋零。当前 Frozen-LTV 论文没有完整提供这些条件。

## 6. 三条路线比较

| 路线 | 主要新增条件 | 算法变化 | 凸 QP | 可达层级 | 判断 |
|---|---|---|---|---|---|
| A：完整模型价值函数 + Frozen 近似 | 终端下降、移位可行、完整模型可行域、价值函数正定/连续、增广域保持、成本检测性 | 保持 Frozen QP；完整模型只用于理论 | 保留 | 条件实际稳定/最终有界；零误差特例可谈渐近 | **优先，CONDITIONAL GO** |
| B：直接比较相邻 Frozen QP | 控制两次冻结矩阵、历史重编码、nominal 序列、可行域和移位误差 | 在线算法可不变，但证明更长 | 保留 | 理论上可达，但误差项更多 | 备选，不优先 |
| C：鲁棒/管状/收紧 MPC | 鲁棒正不变集、辅助反馈、终端集、收紧后递归可行 | 可能改变约束和控制器 | 需逐式确认 | 条件鲁棒实际稳定 | 当前不建议，需用户另行授权 |

路线 A 的目标桥梁是：

\[
V_N(\mathcal F(\zeta,u_0))
\le J_N^{\rm full}(\zeta,U)-\ell(\zeta,u_0),
\]

\[
J_N^{\rm full}(\zeta,U^{\rm fr})
\le V_N(\zeta)+2\varepsilon_J(\zeta,\bar U)+\eta,
\]

再结合

\[
|V_N(\zeta)-V_N(\zeta')|
\le\omega_V(\|\zeta-\zeta'\|),
\qquad
\|\zeta_{k+1}^{\rm obs}-\mathcal F(\zeta_k^{\rm obs},u_k)\|
\le c_\zeta\delta,
\]

才可能得到

\[
V_N(\zeta_{k+1}^{\rm obs})-V_N(\zeta_k^{\rm obs})
\le-\ell(\zeta_k^{\rm obs},u_k)
+2\varepsilon_J+\eta+\omega_V(c_\zeta\delta).
\]

当前论文已有第二项的有限时域版本，但尚未证明第一项、价值函数连续性和真实闭环工作域保持。

## 7. 当前成本的硬缺口

当前 `eq:full_cost` 只惩罚测量跟踪、输入偏差和输入增量；可行集是 `U^N` 的逐步输入约束，没有终端约束、终端控制律或状态约束。

因此：

- QP 凸性没有问题；
- 但价值函数未必对完整 \(\zeta=(z,X,U^{\rm in})\) 正定；
- 隐藏提升坐标和历史槽位可能不被成本检测；
- 仅输入约束不能自动保证下一次真实采样仍在可求解且 A1–A4 有效的区域；
- 没有终端条件，不能直接套用经典 MPC 移位下降证明；
- 若新增终端成本/约束，必须重新核对 Frozen QP 凸性和完整/Frozen 共同可行集。

## 8. 当前阻塞与推荐用户决策

已确认：可以借鉴 MAKO 的证明树；不复制其在线适应律和结论；优先研究路线 A；不预先承诺渐近稳定；TASK-061 的联合训练保留但不证明 A3。

Phase B 被以下问题阻塞：

1. 稳定性对象是否限定为模型增广状态/测量历史，而非物理状态 `s`？
2. 是否只研究恒定平衡点调节，不处理一般时变跟踪？
3. 是否允许增加保持凸 QP 的终端二次项/线性终端条件？
4. 若不改在线控制器，是否接受把终端下降、工作域不变性和检测性作为强假设？
5. 当前 `J_full` 是否继续作为闭环理论成本，还是允许定义一个理论辅助成本？
6. 若目标是物理 plant 稳定，plant--模型误差、可达域不变性和测量历史检测性分别采用什么可验证条件？

**推荐先确认第 3 项。** 这决定路线 A 是只增加强假设，还是调整 MPC 正式数学定义后建立更标准的实际稳定性证明。在用户确认前不改第四章、不写稳定性定理。

## 9. Phase A 结论

**CONDITIONAL GO：** 可以进入 Phase B 严格推导，但必须分别检查：

- A0：保持当前成本/约束，仅增加显式终端、检测性、前向不变性和误差条件；
- A1：增加不改变 Frozen QP 凸性的终端设计，再重新核对共同可行集和 `2\varepsilon_J`。

若两个分支都只能依赖不可验证的精确模型或冻结误差为零，则最终应回到现有预测界 + 冻结性能界主线，不把闭环稳定性作为已证明主结论。
