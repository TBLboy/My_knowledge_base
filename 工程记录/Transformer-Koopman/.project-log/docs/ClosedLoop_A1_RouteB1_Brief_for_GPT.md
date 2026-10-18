# Transformer–Koopman / Frozen-LTV MPC
# Route B1 时变鲁棒终端内集：外部 GPT 咨询简报

日期：2026-10-17  
用途：请外部 GPT 独立审查理论路线，不实施任何代码/论文/控制器修改。  
项目范围：纯理论；不做数值验证、实验、checkpoint、求解器 benchmark 或物理 plant 稳定性宣称；P5 正式稳定性定理暂停。

---

## 1. 希望 GPT 回答的精确问题

请独立判断下面的 Route B1 理论设计是否已经形成**非循环、可构造的递归可行性充分条件**，以及还缺少什么：

1. 给定时变参考、历史条件调度、一次名义 rollout、一次冻结和一次凸 QP，是否可以用一个时变仿射终端反馈和一个非空鲁棒终端内集保证下一采样 Frozen QP 非空？
2. 下面的 T0–T17 条件哪些是真正的离线可验证证书，哪些只是把“下一步可行”换名字后的循环假设？
3. B1 的球形半径条件失败时，非球形多面体终端族 `Z_t` 是否可能绕开失败？
4. 在目前没有具体 `K_t`、统一扰动集合和闭环外包常数的情况下，最诚实的结论应是 `CONDITIONAL`、`OPEN/BLOCKED` 还是 `NO-GO`？
5. 是否存在一个比 B1 更小、仍保持一次名义 rollout + 一次冻结 + 一次凸 QP 的理论机制？

请特别区分：

- 研究设计模板在显式证书下逻辑成立；
- 当前 `Main.tex` 控制器已经具备该性质；
- 当前证书是否真的已经给出。

---

## 2. 已确认的项目背景

### 2.1 当前论文控制器（已从 `Main.tex` 核对）

文件：`Transformer-Koopman/论文/新版本/Main.tex`，主要位置约第 525–729 行。

当前结构：

1. 从测量历史初始化 lifted state `z_0=g_theta(X_k)`；
2. 选择一个名义输入序列 `bar U`；
3. 用完整 scheduled model 沿名义序列做一次 rollout；
4. 生成 `bar A_i=A(bar c_i)`、`bar B_i=B(C_x bar z_i)`；
5. 将矩阵冻结，得到 affine LTV prediction；
6. 求一次凸 QP，QP 当前只有逐时刻输入多面体约束；
7. 执行第一个输入，下一采样重新测量。

论文明确写出名义序列如何选择仍是 implementation choice，尚未定义 shift-tail 或终端可行性机制。

当前目标包含测量跟踪、输入参考和绝对输入增量成本；第一步输入增量使用实际上一输入缓存。

### 2.2 已有理论阶段

- P0–P3：理想完整调度时变 MPC 的条件性理论包；不是当前实现的无条件稳定性定理。
- P4：Frozen/full 静态桥接、终端收紧、终端成本差异和跨采样重新冻结门槛。
- Route B：比较 B1 shift-tail + 鲁棒终端内缩与 B2 可行候选保护。

核心事实：固定某个名义序列、同一候选输入下的 Frozen/full 界 `K_i`，不能自动推出下一采样重新冻结后的 QP 非空。

---

## 3. 本轮硬约束

以下内容均**禁止**：

- 修改论文正文；
- 修改代码或正式控制器；
- 修改实验、图片或数据；
- 数值验证、实验运行、checkpoint、求解器 benchmark；
- 声称物理 plant 稳定；
- 在 P4-R 未闭合前进入 P5 正式稳定性定理。

允许：纯数学定义、条件命题、反例、证明压力测试、控制器差异说明。

---

## 4. 统一状态与误差坐标

采用一致性流形上的联合状态：

\[
\eta_t=\operatorname{col}(z_t,X_t,U_t^{in}),
\qquad
\xi_t=\operatorname{col}(\eta_t,u_{t-1}).
\]

输入历史：

\[
U_t^{in}=\operatorname{col}(u_{t-P+1},\ldots,u_{t-1}),
\qquad u_{t-1}=E_uU_t^{in}.
\]

缓存递推：

\[
U_{t+1}^{in}=\operatorname{shift}(U_t^{in},u_t),
\qquad u_{last,t+1}=u_t,
\qquad u_{last,t+1}=E_uU_{t+1}^{in}.
\tag{T0/T0a}
\]

绝对时间参考下的联合误差：

\[
e_t=\xi_t-\xi_t^{ref}.
\]

缓存误差统一写成：

\[
e_{last}=E_{last}e.
\]

不能把 `u_last` 当成与输入历史独立的自由状态。

---

## 5. B1 的最小仿射终端反馈

候选 tail：

\[
u_t=\kappa_t(\xi_t)
=u_t^{ref}+K_tS_\eta e_t
+K_t^{last}(u_{t-1}-u_{t-1}^{ref}).
\]

等价地写为：

\[
\delta u_t=L_te_t.
\]

输入增量误差必须保留参考输入增量和上一缓存误差：

\[
u_t-u_{t-1}
=(u_t^{ref}-u_{t-1}^{ref})
+\delta u_t-e_{last}.
\]

`K_t,K_t^{last}` 必须离线给定；若在线重新优化反馈，则不再是原定的一次冻结+一次凸 QP 结构。

状态：`CONDITIONAL`，不是当前实现性质。

---

## 6. 三层误差与扰动排他账本

区分：

- `e_t^fr`：Frozen QP 预测误差；
- `e_t^full`：同一候选完整 scheduled model 误差；
- `e_t^act`：真实重新编码/闭环误差。

旧时刻同候选关系：

\[
e_t^{full}=e_t^{fr}+d_t^{fr},
\qquad d_t^{fr}\in\mathcal D_t^{fr}.
\]

在下一时刻采用自身名义输入序列并沿自身完整 rollout 冻结时，B-EXACT 只说明该名义候选自身的 Frozen/full 差异为零；它不消除旧 `d_fr` 对 tail 的影响。

总扰动外包写成：

\[
\mathcal D_t^{tot}
=\mathcal D_t^{fr,tail}
\oplus\mathcal D_t^{init}
\oplus\mathcal D_t^{ref}.
\]

禁止把新名义候选 Frozen/full 差异再次作为独立动态扰动加入。

---

## 7. 终端内集候选

一致性流形上的时变多面体候选：

\[
\mathcal X_{f,t}^{in}
=\{(e,e_{last}):G_te\le\alpha_t,
\ e_{last}=E_{last}e\}.
\]

一致性误差流形：

\[
\mathcal M_t=\{e:e_{last}=E_{last}e\}.
\]

要求：

1. `X_f,t^in` 包含于时变 Frozen 收紧终端集合；
2. tail 输入满足幅值约束；
3. tail 输入增量满足约束；
4. 集合保持在 `K_i`、Lipschitz、历史一致性和调度界适用的工作域。

---

## 8. 正半径非空证书 T11–T11c

要求存在一致性流形内中心和严格正半径：

\[
e_t^c\in\mathcal M_t,
\qquad r_t>0,
\qquad
\mathbb B_{r_t}^{\mathcal M_t}(e_t^c)
\subseteq\mathcal X_{f,t}^{in}.
\tag{T11}
\]

对各终端面、输入面、输入增量面和工作域面计算中心剩余裕量 `mu`，并使用限制到流形切空间的对偶范数：

\[
\|c^T\|_{\mathcal M_t}
:=\sup_{v\in\mathcal M_t-\mathcal M_t,\|v\|_2\le1}c^Tv.
\]

可直接取用的严格保守半径：

\[
r_t^{safe}=\frac12\min\left\{
\frac{\mu_f}{\|G\|_{\mathcal M}},
\frac{\mu_u}{\|a^TL\|_{\mathcal M}},
\frac{\mu_\Delta}{\|b^T(L-E_{last})\|_{\mathcal M}},
\frac{\mu_W}{\|W\|_{\mathcal M}}
\right\}.
\tag{T11c}
\]

该证书是充分而非必要；当前项目没有证明 `r_t^{safe}>0`。

---

## 9. 前向不变性支持函数条件

真实闭环从 Frozen 终端误差到实际下一误差必须有真实非线性集合外包：

\[
e_{t+1}^{act}
\in A_t^Fe_t^{fr}+B_t^F\delta u_t+d_t,
\qquad d_t\in\mathcal D_t^{tot}.
\]

代入 tail：

\[
e_{t+1}^{act}
\in A_t^{cl}e_t^{fr}+\mathcal D_t^{tot},
\qquad A_t^{cl}=A_t^F+B_t^FL_t.
\]

逐面终端传播条件：

\[
\sup_{e\in\mathcal X_{f,t}^{in}}
G_{t+1,q}A_t^{cl}e
+\sigma_{G_{t+1,q}}(\mathcal D_t^{tot})
\le\alpha_{t+1,q}.
\tag{T12}
\]

输入幅值、输入增量和工作域还需 T13–T15 类逐面条件。LP 对偶若保留流形等式，必须包含自由乘子：

\[
G_t^T\lambda+H_t^T\nu=c,
\qquad \lambda\ge0,
\quad \nu\text{ free},
\]

并要求终端 LP 非空且目标有限。

这些条件给定时，T-Inv 前向不变命题逻辑成立；但当前没有 `A_t^F,B_t^F`、统一 `D_tot` 或面证书。

---

## 10. 标量收缩—扰动兼容性压力测试

若存在

\[
\|A_t^{cl}v\|\le\lambda_t\|v\|,
\qquad\lambda_t<1,
\]

定义中心失配和扰动半径：

\[
q_t=\|A_t^{cl}e_t^c-e_{t+1}^c\|,
\qquad
d_t=\sup_{d\in\mathcal D_t^{tot}}\|d\|.
\]

半径传播需要：

\[
q_t+\lambda_tr_t+d_t\le r_{t+1}.
\]

统一上界下：

\[
\frac{q+d}{1-\lambda}
\le r
\le\inf_t r_t^{safe}.
\tag{T15d}
\]

左侧大于右侧时，只能否定当前球/范数/外包证书，不能否定所有形状的终端集。

---

## 11. 非球形多面体族与结构性反例

球形证书失败不等于所有内集失败。可定义：

\[
\mathcal Z_t=\{e\in\mathcal M_t:G_te\le\alpha_t\}
\]

并直接要求：

\[
\sup_{e\in\mathcal Z_t}
G_{t+1,q}A_t^{cl}e
+\sigma_{G_{t+1,q}}(\mathcal D_t^{tot})
\le\alpha_{t+1,q}.
\tag{T15f}
\]

若 `M_t` 写成 `H_te=0`，其 LP 对偶包含自由等式乘子；要求 `Z_t` 非空且目标有限。

但若存在一维无控制系统：

\[
e^+=e+d,
\qquad d\in[-\bar d,\bar d],\quad\bar d>0,
\]

则对任意非空闭有界集合取最大元素 `e_max`，扰动 `d=bar d` 后得到更大的状态，不可能保持在原集合内。因此没有非空有界鲁棒不变集。这是“无收缩/无控制作用”的结构性反例，不是球形证书失败的数值现象。

---

## 12. B1 递归可行性桥接

若：

1. 当前 Frozen 终端状态在 `X_f,t^in`；
2. T0/T0a 缓存一致性成立；
3. B-EXACT 接口契约成立；
4. T11 正半径非空证书成立；
5. T12–T15/T-Inv 成立；
6. 全时域阶段约束和工作域保持；
7. QP 全可行域证书 T17 成立；

则 `U_shift=bar U` 是下一 Frozen QP 的可行候选，并可归纳出 QP 非空。

这是**非循环条件性蕴含**，因为 T11–T15/T17 是独立离线证书，而不是直接假设“下一 QP 可行”。但当前项目尚未提供这些证书。

---

## 13. 当前裁决

| 对象 | 状态 |
|---|---|
| 仿射终端反馈 | `CONDITIONAL` |
| 球形正半径证书 | `OPEN / BLOCKED` |
| 非球形多面体终端族 | `CONDITIONAL` |
| 真实闭环外包 | `OPEN / BLOCKED` |
| 统一扰动集合 | `OPEN / BLOCKED` |
| 前向不变性 | `CONDITIONAL`（证书给定时） |
| B1 当前递归可行性 | `OPEN / BLOCKED` |
| 当前正式控制器 | `NO-GO` |
| P5 | `STOP` |

首要阻碍：没有非循环、非空、前向保持并满足输入幅值/输入增量/缓存一致性的鲁棒终端内集证书。即使球形证书失败，也不能据此断言所有多面体内集均失败；但当前也没有足够模型证据构造多面体证书。

---

## 14. 已有文件与证据

相关理论文件：

- `.project-log/docs/ClosedLoop_A1_P4_FrozenStability_Roadmap.md`
- `.project-log/docs/ClosedLoop_A1_P4R_RecursiveFeasibility_MinimalMechanism.md`
- `.project-log/docs/ClosedLoop_A1_RouteB_Design_Comparison.md`
- `.project-log/docs/ClosedLoop_A1_RouteB_RecursiveFeasibility_Proof.md`
- `.project-log/docs/ClosedLoop_A1_RouteB_Controller_Delta.md`
- `.project-log/docs/ClosedLoop_A1_RouteB1_TimeVarying_Robust_Terminal_Set.md`

当前主报告最新 SHA-256：

```text
52babf9e5c03db29afa7b4595709e140fd3203444f9a79cd5d0d9c81d631fb75
```

最新修订后应重新绑定证据；旧的 `EV-A1-RouteB1-Terminal-003` 已被标记 stale，不能代替最新证据。

已重新静态复核的结论：研究交付物 `GO`；B1 `OPEN/BLOCKED`；当前控制器 `NO-GO`；P5 `STOP`。未做数值验证。

---

## 15. 请 GPT 最终给出的建议格式

请按以下格式回答：

1. **结论先行：** B1 是否存在可构造的非循环终端机制？
2. **逐项审查：** T0/T0a、T2/T3、T4–T6、T11、T12–T15、T-Inv、T15d、T15f、T17。
3. **区分三种失败：**
   - 当前球形证书失败；
   - 当前多面体证书未构造；
   - 所有有界鲁棒内集结构性不存在。
4. **给出最小下一步：** 是继续纯理论构造证书，还是进入控制器规格决策？
5. **明确是否允许进入 P5：** 在什么证据下允许，当前为什么不允许？

请不要把“给定 T11–T17 时逻辑成立”误写成“当前模型已经满足 T11–T17”。
