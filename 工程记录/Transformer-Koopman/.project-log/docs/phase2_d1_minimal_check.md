# 阶段② D1 最小可行性检查（v0.1）

## 1. 当前判断

D1（dissipativity-constrained Koopman lifting）暂时保留为 exploratory candidate，但尚未通过路线门禁。

关键风险不是 KYP/LMI 能否写出，而是 supply rate 是否具有真实物理意义。当前项目事实只确认存在 `x,u` 数据，尚未确认：

- `x` 是否包含位置与速度等完整机械能变量；
- `u` 是否是物理功率端口或与功率存在已知映射；
- 两个平台能否共享同一个 supply rate；
- 是否有摩擦、柔性、滞后或外部扰动，使 passivity 只在局部成立。

如果这些条件无法确认，D1 很容易退化为：对任意学习到的 `(A,B)` 人为寻找 `P,Q,S,R` 使 KYP 不等式成立。那不是物理结构保持，而是后验稳定性拟合，必须 kill。

## 2. 线性 lifted 模型的标准检查对象

考虑：

```text
z+ = A z + B u
y  = C z
```

给定 supply rate：

```text
s(y,u) = [y;u]^T Π [y;u]
```

可用 storage `V(z)=z^T P z` 检查离散耗散不等式：

```text
V(z+) - V(z) <= s(y,u) - rho ||z||^2.
```

这会产生标准 KYP/LMI 约束。它本身不构成创新。

## 3. 必须新增的 Koopman/物理内容

D1 只有在下列内容同时成立时才可继续：

1. `C=[I 0]` 的物理输出保持结构进入 storage/supply 设计，而不是只作为普通输出矩阵；
2. latent 部分的 storage 权重受到物理输出或输入功率约束，不能任意缩放；
3. encoder/model residual `w_k` 被纳入 approximate dissipativity inequality；
4. 控制器证明从该结构推出 physical tracking/disturbance bound，而不仅是 `A-BK` 稳定；
5. supply rate 可以由两类平台各自的测量量定义或明确说明只针对一个物理平台；
6. 实验能区分：相同 prediction accuracy 下，D1 的 closed-loop energy/dissipation/ disturbance behavior 优于普通 Koopman-LQR 或 robust Koopman-MPC。

## 4. 低成本 kill tests

### K-D1-1：物理 supply 可定义性

对每个平台回答：

- `x` 的哪些分量是 position/velocity/force/pressure？
- `u` 的单位和作用端口是什么？
- 是否能定义 `u^T y` 或等价功率项？
- 能量函数是否可由现有数据或机械结构计算？

若不能回答，D1 不得作为双平台统一理论路线；最多作为单平台 physics-informed 分支。

### K-D1-2：非平凡性

在任意稳定 `(A,B,C)` 上搜索 KYP certificate。如果只要调小 `P` 或改变 supply rate 就总能满足，那么该 certificate 没有物理含义，D1 kill。

### K-D1-3：误差传递

加入 `z+=Az+Bu+w` 后，必须得到显式 `delta` 项，并证明它如何影响 storage growth、physical output tracking 或 disturbance amplification。若只能得到普通 ISS 界，D1 只能作为约束组件，不是主创新。

## 5. 当前路线状态

```text
I1 general simulation relation       killed
I2 reference-compatible lifting      killed
M6 finite-memory closure             deferred / likely killed standalone
D1 dissipativity-constrained lift    exploratory, pending K-D1-1..3
```

## 6. 下一步

先不改代码。读取/核实两平台数据语义与论文物理变量定义；若无法建立真实 supply rate，则立即淘汰 D1，继续寻找不依赖未确认物理量、但仍能制造控制结构的新路线。
