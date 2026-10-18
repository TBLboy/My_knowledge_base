# A1 P0–P2：状态、时变参考与一步误差审计

日期：2026-10-17  
范围：纯理论推导；不修改论文、代码、实验、图片或正式控制器。  
状态标识：`PROVED` 表示由定义和代数直接得到；`CONDITIONAL` 表示依赖明确前提；`OPEN` 表示尚未完成；`NO-GO` 表示当前表述不能成立。

## 1. P0 符号对象

### 1.1 四类轨迹

在采样时刻 `k`，定义当前真实测量层增广状态：

\[
\eta_k^{enc}=\operatorname{col}(z_k^{enc},X_k,U_k^{in}),
\qquad z_k^{enc}=g_\theta(X_k).
\]

给定候选输入序列 `U=(u_{0|k},\ldots,u_{N-1|k})`：

- `eta_{i|k}^{full}(U)`：从 `eta_k^{enc}` 出发，沿完整历史调度模型递归传播；
- `eta_{i|k}^{fr}(U;\bar U)`：由名义序列 `bar U` 生成冻结矩阵，再用候选 `U` 传播冻结增广状态；
- `eta_t^{ref}`：时变参考的增广轨迹，由参考测量窗口、参考过去输入窗口和参考编码目标组成。

三条预测轨迹共享当前初始历史，但只有 full/fr 在“同一候选 `U`、同一冻结名义 `bar U`”下可直接比较。真实下一采样状态不是 full 或 fr 的自动等同物。

### 1.2 最小增广状态

\[
\eta=\operatorname{col}(z,X,U^{in}),
\qquad n_\eta=d+Pn+(P-1)m.
\]

上一输入由过去输入窗口最后一个块提取：

\[
u_{last}=E_uU^{in}.
\]

不另加独立 `u_prev`，避免重复计数。

完整模型映射为：

\[
\begin{aligned}
z^+&=A(C_\phi(X,U^{in}))z+B(C_xz)u,\\
X^+&=S_xX+b_xC_xz^+,\\
(U^{in})^+&=S_uU^{in}+b_uu,\\
\mathcal F_\eta(\eta,u)&=\operatorname{col}(z^+,X^+,(U^{in})^+).
\end{aligned}
\]

### 1.3 两个不同的流形

**测量一致性流形：**

\[
\mathcal M_x=\{\eta:X[-1]=C_xz\}.
\]

在完整模型中，若初始状态属于 `M_x`，且新窗口最后一帧由 `C_xz^+` 注入，则 `M_x` 对模型映射保持。这是一个由历史移位定义产生的结构事实。

**编码器流形：**

\[
\mathcal M_g=\{\eta:z=g_\theta(X)\}.
\]

递归传播的 `z^+` 一般不等于 `g_theta(X^+)`。因此 `M_g` 不是自动不变的；若理论需要它，必须另加精确不变性或重新编码误差假设。不能把递归预测 `z^P` 和每步重新编码 `z^{enc}` 混用。

### 1.4 参考增广轨迹

参考测量和输入满足相同窗口规则：

\[
X_t^{ref}=\operatorname{col}(x_{t-P+1}^{ref},\ldots,x_t^{ref}),
\]

\[
U_t^{in,ref}=\operatorname{col}(u_{t-P+1}^{ref},\ldots,u_{t-1}^{ref}).
\]

参考提升目标可定义为 `z_t^{ref}=g_theta(X_t^{ref})`，但这只定义参考编码目标，不保证其满足完整模型动力学。于是：

\[
\eta_t^{ref}=\operatorname{col}(z_t^{ref},X_t^{ref},U_t^{in,ref}),
\]

\[
d_t^{ref}:=\eta_{t+1}^{ref}-\mathcal F_\eta(\eta_t^{ref},u_t^{ref}).
\]

`d_ref=0` 是理想可实现参考假设；一般时变参考不能默认满足它。

## 2. P2 一步残差恒等式

定义当前测量层一步提升残差：

\[
r_k=z_{k+1}^{enc}-A(c_k)z_k^{enc}-B(x_k)u_k,
\]

其中 `c_k=C_phi(X_k,U_k^{in})`，且所有量使用同一归一化/坐标系。

若满足以下前提：

1. `X_k` 最后一帧等于 `C_x z_k^{enc}`；
2. 真实输入窗口按 `U^{in}` 的定义移位；
3. 下一测量满足 `x_{k+1}=C_xz_{k+1}^{enc}`；
4. `F_eta` 的 `z` 分量使用同一个 `A(c_k),B(x_k)`；

则有精确恒等式：

\[
\boxed{
\eta_{k+1}^{enc}
=\mathcal F_\eta(\eta_k^{enc},u_k)
+w_k^\eta
}
\]

其中

\[
w_k^\eta=
\operatorname{col}(r_k,b_xC_xr_k,0).
\]

因此：

\[
\|w_k^\eta\|_2
\le c_\eta\|r_k\|_2,
\qquad
c_\eta=\sqrt{1+\|b_xC_x\|_2^2}.
\]

这只是测量/重新编码增广层的扰动映射，不是物理状态 `s` 的误差界。

**结论：`PROVED`（在上述同坐标、同移位和测量一致性前提下）。**

## 3. 误差账本

| 符号 | 含义 | 进入证明的位置 | 当前状态 |
|---|---|---|---|
| `d_ref` | 参考增广轨迹不满足完整模型的残差 | 跟踪误差动力学；或并入明确的参考项 | `CONDITIONAL` |
| `w_eta` | 真实重新编码一步传播相对完整模型的误差 | 真实闭环价值连续性/实际扰动 | `PROVED`（条件下） |
| `d_freeze` | 同候选、同名义冻结序列下 full/fr 预测差异 | 代价近似与终端收紧 | `CONDITIONAL` |
| `d_plant` | 物理 plant 与模型/测量层桥梁误差 | 仅物理层扩展 | `OPEN` |
| `eta_solver` | Frozen QP 数值求解次优性 | 成本次优性 | `CONDITIONAL` |

`d_freeze` 不能再次作为真实一步动力学扰动；`eta_solver` 也不是状态动力学扰动。

## 4. P0–P2 状态裁决

- 增广状态、full/fr/ref 对象：`PROVED`（按定义）。
- 测量一致性流形保持：`CONDITIONAL`，依赖初始化和同一读出规则。
- 编码器流形保持：`OPEN`；不能默认成立。
- 一步 `r_k -> w_k^eta` 恒等式：`PROVED`（列明前提后）。
- 参考残差定义：`PROVED`（定义层面）；其统一上界：`OPEN`。
- 物理 plant 误差桥梁：`OPEN/NO-GO`（当前没有足够对象和假设）。

P0–P2 的理论接口已足够进入 P1/P3；不需要任何数值验证或实验。
