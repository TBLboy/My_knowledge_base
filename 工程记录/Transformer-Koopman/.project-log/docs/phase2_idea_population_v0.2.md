# 阶段② Idea Population v0.2：结构性路线候选

> 本文档是候选池，不是最终论文方案。候选必须继续经过 prior-art、反例、定理可证性和 claim-driven experiment 检查。

## 1. 本轮研究输入

已确认的 prior-art 边界：

- tube-based robust Koopman MPC 已有 Zhang et al., *Automatica*, 2022；
- Koopman-CBF 安全控制已有 Folkestad et al., *IEEE Control Systems Letters*, 2021；
- neural Koopman-CBF 已有 Zinage & Bakolas, ACC 2023；
- adaptive Koopman embedding for robust robotic control 已有 Singh et al., *IJRR*, 2025；
- robust dual-loop finite-dimensional Koopman control 已有 Pal & He, ACC 2023；
- CCK / actuator pre-filtering / virtual dynamics 已有 Asada, CDC 2024 与 L-CSS 2025。

因此以下内容均不把“加鲁棒项、加 CBF、在线残差修正、加 Transformer、改 bilinear”本身视为贡献。

## 2. 统一结构障碍

当前 lifted controller 同时遇到三个相互关联的问题：

1. `z_ref` 不一定是 lifted model 的可行轨迹；
2. `B†(z_ref_{k+1}-Az_ref_k)` 存在投影残差；
3. 当前 theorem 没有建立真实系统与 lifted closed loop 之间的 simulation/abstraction relation。

这比“残差大”更基础：即使 `w_k=0`，若 reference 不在可控方向中，当前前馈结构也不能实现所声称的跟踪。

## 3. Candidate ideas

### I1 — Control-aware approximate Koopman abstraction

#### Gap

当前 lifting 只优化预测误差，没有证明它是一个可以把控制性质传回物理系统的近似抽象。

#### Innovation operator

`Approximate Condition` + `Error-bound` + `Structure-aware lifting`。

#### Core idea

不把 `z_{k+1}=Az_k+Bu_k+w_k` 当作最终模型，而是定义一个带物理输出映射 `x=Cz` 的 **approximate controlled simulation relation**：

```text
真实系统 x+ = F(x,u)
        ↕  relation/error δ
lifted system z+ = Az+Bu
```

建模目标从“平均预测准确”改为“使关系误差 δ 可认证”。

#### Expected theorem

若 lifted feedback 在某个 Lyapunov metric 下具有 contraction，且真实系统与 lifted system 满足一步 simulation defect `δ`，则物理输出误差满足一个由 `δ`、参考可行性残差和 contraction factor 决定的界。

核心不是普通 `w`-UUB，而是：

```text
lifted closed-loop property
→ physical closed-loop property
```

#### Main risk

近似 bisimulation / simulation relation 和 Koopman error-bound 文献存在交叉。必须证明本路线的关系是控制输入一致、物理输出可读出、并能处理 history lifting 的特殊结构，而不是重新命名标准模型误差界。

#### Kill criterion

- 无法写出区别于普通 bounded-disturbance UUB 的 relation theorem；或
- δ 只能依靠验证集经验估计，不能在明确 domain 内定义/验证；或
- prior-art 已有等价 Koopman simulation relation。

---

### I2 — Reference-compatible controllable lifting

#### Gap

当前 `B` 的列空间可能无法覆盖任意 lifted reference increment，导致伪逆前馈留下 projection residual。

#### Innovation operator

`Structure Manufacturing` + `Decomposition` + `Reference Reformulation`。

#### Core idea

重新设计 lifting，使 lifted state 显式分为：

```text
z = [z_c ; z_a ; x]
```

其中：

- `z_c`：与输入可达/可控的 Koopman coordinate；
- `z_a`：自主或不可控 latent dynamics；
- `x`：物理输出，必须由 lifting 保留。

参考轨迹不再直接指定完整 `z_ref`，而是通过一个 reference governor / reference lifting map 生成满足：

```text
z_ref,+ - A z_ref ∈ range(B)
```

或者显式保留不可避免的 projection residual，并把它纳入 theorem。

#### Expected theorem

在可控块上实现精确或近似参考推进；在不可控块上给出一致性条件或 residual bound；证明物理输出 tracking bound 和 lifted reference recursive feasibility。

#### Main risk

“reference governor + Koopman”已有研究信号；“controllability decomposition”本身是线性系统标准工具。创新必须来自**学习 lifting 与参考可行性共同设计**，而不是单独使用 Kalman decomposition。

#### Kill criterion

- 只能得到标准 controllability decomposition；
- reference governor 只是外接模块，没有改变 lifting 或 theorem；
- 物理参考任务无法构造可行 lifted reference。

---

### I3 — History-induced dynamic extension for control coherence

#### Gap

历史窗口可以提供记忆，但当前论文只将 history 用于预测，没有说明它如何修复 input structure 或 actuator dynamics。

#### Innovation operator

`Dynamic Extension` + `Latent-state Introduction` + `Structure Manufacturing`。

#### Core idea

不是直接复制 CCK 的 physical actuator pre-filter，而是研究：在只拥有状态/输入历史、未知 actuator dynamics 的机器人系统中，能否由 history lifting 构造一个 virtual actuator coordinate，使外部控制在 lifted space 中具有可识别、稳定的输入通道。

#### Expected theorem

在 actuator dynamics 可观测/可逆或满足有限记忆条件时，历史增广系统存在 control-coherent representation；证明其与原系统输入输出行为等价或近似等价。

#### Main risk

这是最接近 CCK 的方向，prior-art 风险最高；若只是把 actuator state 放进 latent vector，则应直接 kill。

#### Kill criterion

- 不能明确区别于 Asada 2024/2025 的 virtual dynamics / actuator pre-filter；
- 需要不可验证的 actuator observability 假设；
- history encoder 只是黑盒近似，没有可写的结构定理。

---

### I4 — Stabilizable-output Koopman control

#### Gap

当前所有 lifted coordinates 被统一放进 LQR，但部分 latent modes 可能不可控、不可观或只对内部 prediction 有用，导致控制器理论过强且不必要。

#### Innovation operator

`Decomposition` + `Physical-state Certificate` + `Approximate Condition`。

#### Core idea

只要求物理输出相关的 Koopman subspace 是 stabilizable，而不是要求整个 latent model 具有理想性质。对 lifted system 做 output-relevant stabilizability decomposition：

```text
physical-output relevant controllable block
        +
internal latent residual block
```

控制器只稳定与物理输出相关的 block，并给出 latent residual 对物理输出的界。

#### Expected theorem

若 `(A,B,C)` 的 output-relevant subspace 满足稳定化条件，且不可控 latent block 对物理输出的增益有界，则物理 tracking 可保证，即使完整 `(A,B)` 不可稳定。

#### Main risk

可能退化为标准 output stabilization / Kalman decomposition。需要证明 learned Koopman lifting 下的“output-relevant subspace”可识别、可估计，并对真实 nonlinear system 有意义。

#### Kill criterion

- theorem 只是在重新陈述线性系统 output stabilization；
- `C=[I 0]` 没有产生实质性新结论；
- 不可控 latent block 对 physical output 的影响无法界定。

---

### I5 — Koopman controller with certified reference projection

#### Gap

当前论文默认 reference 是可实现的，却没有处理 lifted reference 不在 `range(B)` 的情形。

#### Innovation operator

`Reference Reformulation` + `Error-bound` + `Constraint Incorporation`。

#### Core idea

设计一个 Koopman-specific reference projection operator：给定任意物理参考 `r_k`，求一个最接近且动力学可行的 lifted reference `\tilde z_k^{ref}`，并显式最小化：

```text
physical projection error
+ lifted dynamic feasibility residual
+ control effort
```

控制器跟踪 `\tilde z^{ref}`，而不是假设任意 `z^{ref}` 可实现。

#### Expected theorem

证明 projection operator 的递归可行性，并将原始 physical reference 与可行 lifted reference 的差异加入 tracking bound。

#### Main risk

这可能只是 reference governor / constrained tracking 的 Koopman 重写；必须依赖 lifting 的特殊物理-latent结构，才能避免成为已有工具的应用。

#### Kill criterion

- 与普通 linear reference governor 完全等价；
- 没有新的 Koopman-specific feasibility condition；
- projection 计算成本不适合机器人实时控制。

## 4. 第一轮筛选

| Candidate | 创新潜力 | 理论强度 | 可证性 | prior-art 风险 | 当前状态 |
|---|---:|---:|---:|---:|---|
| I1 approximate abstraction | 高 | 高 | 中 | 中 | 保留 |
| I2 controllable lifting | 高 | 高 | 中 | 中高 | 保留 |
| I3 history actuator extension | 高 | 高 | 低 | 高 | 暂缓，先做 CCK 对照 |
| I4 stabilizable-output control | 中高 | 中高 | 中 | 中高 | 保留为 I1/I2 子路线 |
| I5 certified reference projection | 中高 | 中高 | 高 | 高 | 保留为 I2 控制器实现 |

## 5. 当前推荐组合（暂定）

不是旧的“M4+C2”，而是：

```text
I1 + I2
```

即：

> **Control-aware, reference-compatible Koopman abstraction**

建模和控制器不是分开拼接：

1. 建模端学习一个保留物理输出的、控制可分解的 lifting；
2. 控制端只在可行/可控 lifted reference 上设计控制律；
3. 理论端证明 lifted closed-loop 性质如何传回 physical output；
4. 误差界中同时出现 simulation defect 与 reference projection defect。

暂定核心误差结构：

```text
physical tracking error
≤ abstraction defect
  + reference feasibility defect
  + closed-loop contraction term
```

这比当前论文的单一 `ε` 更有内容，也比单纯添加 robust MPC/CBF 更容易形成自己的理论主线。

## 6. 下一轮必须做的定理可行性检查

对 I1+I2 先不写完整论文，而只检查三个最小命题：

### T0：前馈缺陷分解

严格推导 `B†` 前馈下的误差动力学，确认 projection defect 的精确位置。

### T1：可行 lifted reference 的构造

给定离散线性 lifted model，定义最小条件使 `z_ref,+ - A z_ref ∈ range(B)`，并验证 physical reference 是否能通过 `C z_ref=r` 表示。

### T2：近似抽象到物理输出的误差传递

在不使用错误的 `Schur ⇒ ||A||<1` 推理下，用 Lyapunov metric 或加权范数证明：若 abstraction defect 和 reference defect 有界，物理输出误差如何有界。

任一命题出现以下情况则杀掉对应分支：

- 只能得到标准线性代数恒等式；
- 需要把所有关键难题重新假设掉；
- 不能连接回真实物理输出；
- 与已有 Koopman-MPC/reference governor 论文没有实质差异。
