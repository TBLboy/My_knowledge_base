# 阶段② Idea Population v0.4：耗散结构约束的 Koopman 控制

## 1. 为什么继续换方向

前几轮候选均遇到直接或近似 prior-art：

- simulation preorder for Koopman-like lifted control systems；
- control-aware Koopman embedding；
- controllability preservation of Koopman surrogate；
- Mori–Zwanzig / memory Koopman closure；
- Koopman observer synthesis；
- robust tube MPC、CBF、adaptive/residual Koopman。

因此“新的 lifting + 标准 controller”或“标准 lifting + 新的 robust module”都不足以支撑强创新。

## 2. 新主候选 D1：Dissipativity-constrained Koopman lifting

### 核心问题

当前学习目标只要求：

```text
z+ ≈ A z + B u
```

但并不要求 `(A,B,C)` 保留真实机器人系统的能量/输入输出结构。于是：

- prediction loss 小不代表 closed-loop 可控；
- LQR 稳定只针对拟合矩阵；
- 建模误差、输入饱和、扰动下没有物理结构保证；
- Transformer latent coordinates 可以任意旋转/缩放，控制解释不稳定。

### 结构变换

用一个可学习的 storage function `V(z)` 和 supply rate `s(y,u)` 约束 lifted model 满足离散耗散不等式：

```text
V(Az+Bu) - V(z) ≤ s(Cz,u) - ρ||z||²
```

在线性 storage 特例 `V(z)=z^T P z` 下，可以写成 KYP/LMI 类矩阵约束；更一般时可使用参数化 quadratic storage + physical output map。

### 建模贡献

不是单纯学习一个预测最优 `(A,B)`，而是学习：

```text
(g_θ, A, B, C, P)
```

使其同时满足：

1. 物理状态/输出保持；
2. controlled Koopman prediction；
3. dissipativity/passivity constraint；
4. finite-horizon rollout consistency。

Transformer 只负责表示容量，理论对象是**结构约束的 lifted system**。

### 控制器贡献

控制器不再是普通 hierarchical LQR，而是：

- passivity-preserving feedback；或
- energy-shaping + damping injection；或
- dissipativity-based reference tracking。

控制器的目标不是简单让 `A-BK` Schur，而是保持一个物理输出相关的 storage inequality，并在输入限制下给出耗散/跟踪界。

### 预期理论命题

**T-D1：结构保持学习条件。** 若真实系统在给定区域满足某个 dissipativity inequality，且 lifting/approximation defect 不超过 `δ`, 则学习到的 lifted system 满足带 `δ` 的 approximate dissipativity inequality。

**T-D2：闭环耗散跟踪。** 若反馈满足 supply-rate shaping 和输入约束下的 feasible condition，则 physical output tracking error 为 practical asymptotic/ultimate bounded，并且界显式依赖 `δ` 与 reference supply mismatch。

**T-D3：结构约束优于普通 prediction fitting。** 在同等模型容量与数据下，结构约束模型对 closed-loop cost / disturbance amplification 有可解释上界；这必须通过 claim-driven experiment 验证。

### 与已有工作的差异要求

已有相邻方向包括：

- port-Hamiltonian modeling/control；
- passivity-preserving safety-critical control；
- passivity-preserving model reduction；
- Koopman-based control综述；
- 近期 structure-preserving Koopman MPC 预印本。

所以不能声称“passivity + Koopman”本身新。D1 只有在以下差异成立时才存活：

1. 物理输出保留的 temporal/Transformer lifting 与 dissipativity 联合构造；
2. 对 learned controlled Koopman model 给出近似耗散到真实 physical output 的误差传递；
3. 控制器理论处理有限输入约束，而不是只验证无约束 LQR；
4. 两类机器人/软体平台能展示结构约束带来的 closed-loop advantage，而非只改善 prediction。

### Kill criteria

D1 立即淘汰，如果：

- 只能把一个标准 KYP/LMI 加到现有模型，不能产生新的 physical-output theorem；
- storage function 完全是抽象 latent energy，与物理输出/输入没有可解释关系；
- passivity 约束导致模型无法表达数据中的非被动区域，只能依靠过强假设；
- 已有 Koopman structure-preserving control 工作已覆盖同样的 theorem；
- 实验只能显示 one-step error 变化，不能显示 closed-loop/safety/disturbance claim。

## 3. 保留的两个备用候选

### D2 — Dissipative control-aware observable selection

不是在固定 Transformer latent 上加约束，而是从 observable library 中选择能同时满足：

```text
physical output preservation
+ control-affine closure
+ dissipativity inequality
```

这更接近“结构制造”，但需要可解释 observables 或物理先验；对纯黑箱双平台数据风险较高。

### D3 — Task-conditioned dissipative Koopman model

lifting 依赖 reference/task descriptor，使同一个模型针对不同 tracking task 产生不同但共享 dissipativity certificate 的 representation。可能改善 reference feasibility，但 task-conditioned Koopman/goal-conditioned control 已有较大邻域，prior-art 风险高。

## 4. 当前筛选

| 分支 | 当前状态 | 判断 |
|---|---|---|
| I1 general simulation abstraction | killed | 直接有 simulation preorder prior art |
| I2 reference-compatible lifting | killed | 退化为 output controllability/reference governor + control-aware embedding |
| M6 finite-memory closure | deferred/killed as standalone | MZ/memory Koopman 先例充分，当前全状态可测又削弱新意 |
| D1 dissipativity-constrained lifting + controller | active candidate | 最有机会同时覆盖建模与控制器，但需严格 prior-art/theorem kill test |
| D2 dissipative observable selection | backup | 理论可能更强，实验/物理先验风险高 |
| D3 task-conditioned dissipative lifting | backup-low | prior-art 与复杂度风险高 |

## 5. 下一步最小理论任务

不写代码，先做 D1 的 T-D0：

1. 为当前机器人离散系统定义输入输出 dissipativity，而不是先假设 passivity；
2. 判断现有机械臂/软体平台数据是否可能支持统一 supply rate；
3. 写出线性 lifted model 的 KYP/LMI 条件；
4. 把模型误差 `δ` 纳入 approximate dissipativity inequality；
5. 检查是否能由该不等式推出 physical tracking/disturbance bound；
6. 与普通 LQR/UUB、robust Koopman MPC、passivity-preserving control 明确区分；
7. 若 D1 只剩标准 KYP 约束，则 kill，不进入代码。
