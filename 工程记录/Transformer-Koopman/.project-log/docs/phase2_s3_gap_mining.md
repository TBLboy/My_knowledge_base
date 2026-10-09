# 阶段② S3 Gap / Assumption Mining（v0.1）

## 结论摘要

在生成更多新 idea 之前，必须先修正或淘汰现有理论中的基础缺陷。当前最重要的不是 idea 数量，而是：

1. 现有 UUB 定理的证明条件不成立；
2. 模型级误差没有传导为真实系统级保证；
3. 前馈伪逆的参考轨迹可行性没有写入假设；
4. 建模误差 `ε` 没有认证路径；
5. temporal lifting 的理论收益没有不变量/误差界；
6. 候选控制路线尚未经过系统 prior-art 与 kill criteria 检查。

## S2 当前理论结构

### 建模

- 系统：`x_{k+1}=F(x_k,u_k)`。
- 历史窗口：`X_k`。
- lifting：`z_k=g_θ(X_k)=[x_k;h_k]`。
- 受控 Koopman 近似：`z_{k+1}=Az_k+Bu_k+w_k`。
- 当前论文通过 Transformer、Stage 0/1/2 训练和五项损失获得 `(A,B)`。

### 控制器

- 前馈：`u_ff=B^†(z^ref_{k+1}-Az^ref_k)`。
- 反馈：`u_fb=-K_c e_k^z`。
- `K_c` 来自 lifted model 上的 LQR。
- 当前 theorem 试图从 `‖w_k‖≤ε` 推出 `‖e_k^z‖≤ε/(1-‖A_cl‖)`。

## 明确假设

- 全状态可测、控制输入已知；
- lifting 为有限维；
- `(A,B)` 可稳；
- `(A,Q^{1/2})` 可检测；
- `‖w_k‖≤ε` 对所有未来时刻成立；
- 参考历史窗口和闭环历史窗口可被同一 encoder 有效表示。

## 隐含假设

- `‖A_cl‖<1`，而不仅是谱半径小于 1；
- `z^ref_{k+1}-Az^ref_k∈range(B)`；
- 验证集残差可以作为未来轨迹上的统一误差界；
- 控制输入没有饱和、死区或其他实现偏差；
- temporal lifting 近似产生 Koopman 不变子空间；
- `x` 与 latent `h` 的分块结构在闭环和参考轨迹上保持一致。

## 已验证的基础反例

当前论文 `Main34.tex` 第 719–737 行使用：

> Schur stable with `‖A_cl‖<1`

但令

```text
A_cl = [[0.95, 3.0],
        [0.00, 0.95]]
```

则：

- 谱半径 `ρ(A_cl)=0.95<1`，所以矩阵 Schur 稳定；
- 2-范数 `‖A_cl‖₂≈3.2755>1`。

因此“Schur 稳定 ⇒ 2-范数小于 1”不成立。现有几何级数证明不能直接支持论文中的界。

## Gap 分类

### G1：模型级保证与真实系统级保证断裂

当前 theorem 实际分析的是识别模型上的误差动力学。它没有把真实系统的 lifting/模型误差传导到闭环系统，因此不能直接宣称真实机器人闭环跟踪保证。

**候选 operator：** Approximate Condition + Error-bound + Robustification。

### G2：前馈伪逆可行性缺失

当 `B` 不是满行秩时，`B^†` 只能实现投影。一般存在：

```text
(I - B B†)(z_ref_{k+1} - A z_ref_k) != 0
```

该项在当前误差证明中没有出现。

**候选 operator：** Feasibility Reformulation + Projection Residual + Reference Governor。

### G3：误差界 `ε` 没有认证路径

验证集上的残差统计不等于未来闭环可达域上的统一界。对控制器而言，需要概率覆盖、可达集界、鲁棒辨识界或明确的保守假设。

**候选 operator：** Finite-data Extension + Uncertainty Set + Conformal/Distribution-free Bound。

### G4：temporal lifting 的收益没有理论刻画

论文没有说明历史长度、观测窗口、latent 维度与近似不变性/模型误差之间的关系。

**候选 operator：** Approximate Invariant Subspace + Delay/History Embedding + Error-bound Addition。

### G5：控制器所谓 hierarchical 没有结构性定理

`Q=diag(Q_x,αI)` 目前只是 LQR 权重选择，没有两时间尺度、分离原理或物理块/latent 块之间的非平凡结论。

**候选 operator：** Structure Manufacturing + Decomposition + Physical-state Certificate。

### G6：候选路线的 novelty 尚未证明

“残差驱动控制”“Koopman + CBF”“Conformal Koopman”等都存在明显 prior-art 风险。当前只能标记为 candidate，不得称为创新点。

**候选 operator：** Prior-art Adversary + Novelty Check + Branch Kill Criteria。

## 当前 kill criteria

一个候选路线在以下任一条件成立时暂时淘汰：

1. 核心 theorem 只是在已有“有界扰动 + 稳定闭环 ⇒ UUB”上换符号；
2. 关键假设无法从数据、结构或实验中检查；
3. 能构造低维反例直接破坏 claim；
4. 无法设计区分强 baseline 的最小实验；
5. prior-art 检索发现等价方法，且没有新的结构/保证/应用边界；
6. 理论 claim 依赖尚未解决的 `ε`，但路线本身没有提供 `ε` 的认证机制。

## 下一步

先对候选方向开展 S1 literature mapping：

- robust Koopman control / Koopman MPC；
- Koopman + CBF / safety；
- finite-sample or distribution-free learned-model control；
- residual/adaptive Koopman control；
- delay/history lifting and approximate invariant subspaces；
- input-dependent/bilinear Koopman structures。

每类只抽取 `Problem / Assumptions / Main Theorem / Limitation / Unresolved Gap`，然后再生成第二版 Idea Population。
