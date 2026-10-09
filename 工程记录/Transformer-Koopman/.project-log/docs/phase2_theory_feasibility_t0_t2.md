# 阶段② I1+I2 最小理论可行性检查（v0.1）

## T0：伪逆前馈下的精确误差分解

考虑 nominal lifted dynamics：

```text
z_{k+1} = A z_k + B u_k + w_k
```

定义 lifted reference increment：

```text
d_k^ref = z_{k+1}^ref - A z_k^ref
```

控制律：

```text
u_k = B† d_k^ref - K e_k,
e_k = z_k - z_k^ref
```

令 `Π_B = B B†`，则：

```text
e_{k+1}
= A e_k + B(B† d_k^ref - K e_k) + w_k - d_k^ref
= (A-BK)e_k + w_k - (I-Π_B)d_k^ref.
```

因此总扰动不是论文当前使用的 `w_k`，而是：

```text
ν_k = w_k - (I-BB†)(z_{k+1}^ref - A z_k^ref).
```

结论：当前论文第 732–737 行的误差递推只有在以下至少一个条件成立时才成立：

1. `d_k^ref ∈ range(B)`；或
2. 把 projection defect 纳入扰动项；或
3. 通过 reference construction 保证 lifted reference 可行。

这不是新定理，但它明确暴露了当前控制器理论的结构缺口，是 I2 的必要入口。

## T1：可行 lifted reference 的构造问题

对物理参考 `r_k`，需要寻找 `z_k^ref` 满足：

```text
C z_k^ref = r_k,
z_{k+1}^ref - A z_k^ref ∈ range(B).
```

其中 `C=[I_n 0]`。这两个条件一般不能对任意 `r_k` 同时成立。

一个可检验的 finite-horizon 版本是求解：

```text
min_{z_0:N, u_0:N-1}
  Σ_k ||C z_k-r_k||_{W_x}²
  +     ||z_{k+1}-A z_k-Bu_k||_{W_z}²
  +     ||u_k||_R²
```

并根据最优值定义：

- `δ_ref`: physical reference representation defect；
- `δ_dyn`: lifted dynamic feasibility defect。

但仅仅提出这个优化问题不构成创新，因为它可能退化为普通 linear reference governor / trajectory projection。I2 只有在以下条件之一成立时才值得继续：

1. `C=[I 0]` 与 learned history lifting 产生了新的可行性结构；
2. 可以证明一个 Koopman-specific recursive feasibility 条件；
3. projection defect 能够被物理输出误差界严格分离并降低；
4. 该构造能处理当前标准 Koopman-MPC / CCK 没有覆盖的 reference class。

## T2：使用 Lyapunov metric 修正 UUB 证明

令 `A_cl=A-BK`，假设存在 `P=P^T>0` 与 `Q=Q^T>0` 满足：

```text
A_cl^T P A_cl - P = -Q.
```

定义 `||e||_P = sqrt(e^T P e)`。则存在：

```text
a = ||P^(1/2) A_cl P^(-1/2)||_2 < 1
```

并对 `e_{k+1}=A_cl e_k+ν_k` 有：

```text
||e_{k+1}||_P ≤ a ||e_k||_P + ||ν_k||_P.
```

若 `||ν_k||_P≤ε_ν`，则：

```text
limsup ||e_k||_P ≤ ε_ν/(1-a).
```

物理输出满足：

```text
||C e_k||_2 ≤ ||C P^(-1/2)||_2 ||e_k||_P.
```

因此可得到一个正确的 model-level bound：

```text
limsup ||C e_k||_2
≤ ||C P^(-1/2)||_2 · ε_ν/(1-a).
```

其中：

```text
ε_ν ≤ ε_model + ε_ref
ε_ref = sup_k ||(I-BB†)(z_{k+1}^ref-Az_k^ref)||_P.
```

这比当前的 `ε/(1-||A_cl||_2)` 正确，但本身仍不是论文创新，因为它是标准 Lyapunov/ISS 修正。创新必须来自：

1. `ε_model` 如何由 control-aware lifting 或有限数据得到；
2. `ε_ref` 如何由新的 reference-compatible lifting 消除或严格降低；
3. 该 lifted bound 如何传递到真实 nonlinear system 的 physical output。

## 当前判断

- **T0：通过**，确认现有定理有遗漏项。
- **T2：通过但仅为修正工具**，不能作为创新点。
- **T1：关键未决**，决定 I2 是否能从普通 reference projection 升级为真正的 Koopman 理论路线。

## 下一步 kill test

1. 构造低维系统和任意 `C=[I 0]`，检查 `Cz_ref=r` 与 `d_ref∈range(B)` 是否可同时满足。
2. 对比普通 linear reference governor 与 I2 的 projection：若数学形式完全相同，I2 淘汰。
3. 检查 CCK 2024/2025 是否已经覆盖同类 reference feasibility construction；若覆盖，必须转向 history-induced 或 physical-output-specific 未覆盖条件，否则淘汰。
4. 只有存在新的 feasibility condition 和 physical-output theorem，才进入完整 theory construction。
