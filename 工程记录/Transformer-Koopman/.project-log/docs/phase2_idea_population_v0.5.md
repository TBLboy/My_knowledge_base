# 阶段② Idea Population v0.5：基于两平台输入语义的路线池

> 目的：使用 Innovation Operator Library 生成候选，不代表任何路线已通过 prior-art 或理论门禁。

## 1. 共同入口

两个平台不共享同一物理状态，但都存在“控制命令 → 执行器 → 任务空间响应”的接口层。候选路线围绕这一接口层生成，而不是强行统一机器人动力学。

## 2. 候选路线

### A1：Actuation-factorized Koopman model

**operators：** Input Transformation + Factorization + Assumption Engineering。

将模型写为：

```text
z+ = A z + B_p G_p(s_p) v + w
```

其中 `v` 是平台无关的虚拟/任务输入，`G_p` 是平台相关 actuator/interface map，`s_p` 是平台状态或执行器上下文。

- Geomatric Touch：`v` 可为关节级命令，`G_p` 可为执行器/关节接口；
- 软体平台：`v=(dx,dy)`，`G_p` 至少包含固定的四绳差动映射，以及脉冲/延迟/饱和接口。

**理论目标：** 若 `G_p` 满足秩、界和可逆/右逆条件，则证明虚拟输入闭环性质在 actuator realization 后如何传递，并把 interface defect 纳入误差界。

**主要风险：** 可能只是 control-aware Koopman / input transformation 的重写；若 `G_p` 只是已知矩阵左乘，创新不足。

**kill：** 不能得到新的 actuator-realization theorem，或 `G_p` 与平台无关地退化为恒等矩阵。

---

### A2：Relative-degree-preserving Koopman lifting

**operators：** Decomposition + Approximate Condition + Control-relevant Observable。

不要求两个平台共享状态，而要求 lifting 保留“输入到任务输出”的有效响应阶数：

```text
task output y
→ first input-sensitive lifted coordinate
→ control channel
```

Geomatric Touch 的交替位置/速度状态天然提供二阶机械结构线索；软体平台则通过视觉输出历史和脉冲响应估计有效相对阶数，而不直接假设完整机械状态。

**理论目标：** 构造 input-output Koopman representation，使控制输入不会被 encoder 压进不可控 latent block；给出 output tracking 的相对阶数/高频增益或有限步可控性条件。

**主要风险：** 相对阶数理论对软体视觉系统可能不可验证；“control-aware observable”已有先例。

**kill：** 只能依靠经验选择 observables，无法给出可检查的 rank/relative-degree 条件。

---

### A3：Quantized-delay Koopman control

**operators：** Approximate Condition + Robustification + Hybrid/Switched Extension。

把软体系统的视觉延迟、通信延迟、步进脉冲量化和执行时间窗口显式加入：

```text
z_{k+1}=A z_k+B u_{k-d}+w_k+q_k
```

Geomatric Touch 也可纳入数字控制周期、低层执行延迟和输入饱和。

**理论目标：** 给出含离散延迟与量化扰动的 lifted closed-loop stability/tracking condition，而不是把所有误差塞进一个无结构 `w_k`。

**主要风险：** sampled-data/delay/quantized control 是成熟理论；仅把它应用到 Koopman 可能不够创新。

**kill：** 新模型只增加标准 delay state，定理只复述 delay-system stability。

---

### A4：Mode-conditioned Koopman with tension/actuation regimes

**operators：** Decomposition + Switched Reformulation + Robustification。

软体平台至少存在：

```text
张紧 / 临界张紧 / 松弛风险 / 安全停止
```

Geomatric Touch 可对应：

```text
正常运动 / 关节限位 / 饱和 / 摩擦或死区
```

建立 mode-conditioned Koopman family：

```text
z+ = A_m z+B_m u+w_m,  m∈M
```

并让 mode transition 受 actuator/interface 条件约束。

**理论目标：** dwell-time / multiple-Lyapunov / common certificate 下的闭环保证，以及 mode mismatch 对物理输出的影响。

**主要风险：** switched Koopman 已有大量邻域；软体 mode label 目前未确认；模式识别错误会破坏保证。

**kill：** 只有多模型拟合，没有新的 mode transition 或 safety theorem。

---

### A5：Task-space / actuator-space dual Koopman model

**operators：** Decomposition + Dual Formulation + Coordinate Transformation。

同时学习两个相关模型：

```text
actuator-space:  a+ = F_a(a,v)
task-space:     y+ = F_y(y,a)
```

控制器在 task space 规划，在 actuator space 检查可实现性和约束。软体平台的四绳差动映射天然适合这种分解；Geomatric Touch 可把 joint actuation 与 task output 分开。

**理论目标：** 证明两空间模型一致时的 tracking/feasibility 传递，并把 actuator saturation/quantization 单独隔离。

**主要风险：** 可能退化为标准 cascade system / hierarchical control；需要证明 Koopman dual factorization 不是普通级联模型换名。

**kill：** 没有新的 factorization consistency condition 或闭环定理。

---

### A6：Virtual-input Koopman with learned actuator authority

**operators：** Latent State Introduction + Input Transformation + Error-bound。

对每个时刻学习一个 actuator authority/availability quantity：

```text
v_eff = Γ_θ(history, actuator context) v
z+ = A z+B v_eff+w
```

软体平台可以表达绳索松弛、视觉/脉冲执行能力变化；刚体平台可以表达关节饱和、摩擦或有效力矩变化。

**理论目标：** 若 `Γ_θ` 的最小奇异值和变化率有界，则给出 input authority degradation 下的 tracking bound 或 graceful degradation theorem。

**主要风险：** 与 adaptive Koopman、residual/adaptive control、unknown input gain estimation 高度相邻；`Γ_θ` 可辨识性困难。

**kill：** authority 只是神经网络 attention 权重，没有独立可验证物理含义。

---

### A7：Control-relevant Koopman subspace selection

**operators：** Relax Assumption + Control-relevant Observable + Approximate Condition。

不再追求全状态 prediction 最优，而是选择一个子空间，使：

```text
物理任务输出可恢复
+ 输入作用方向可辨识
+ 闭环性能敏感方向被保留
```

Geomatric Touch 的关节位置/速度和软体平台的视觉位置可以有不同 observable，但共享“输出/输入相关子空间”的选择准则。

**理论目标：** 给出 discarded subspace 对 closed-loop task error 的界，而不是仅给全 latent prediction error。

**主要风险：** control-aware learning 已有先例；必须形成新的 output/input sensitivity theorem 或数据驱动可检验判据。

**kill：** 只是改变 loss 权重，不能产生新的子空间条件。

---

### A8：Actuation-aware Koopman data augmentation / operator family

**operators：** Decomposition + Distributed/Multiple Models + Finite-data Extension。

利用两平台执行接口差异，构造平台特定 `G_p`，但在 operator family 层共享结构参数：

```text
K_p = K_shared ∘ G_p + K_private,p
```

目标不是跨平台迁移性能，而是研究 actuator realization 改变时 Koopman operator 如何变化。

**理论目标：** 参数化 actuator map 下的 operator perturbation bound 或 transfer condition。

**主要风险：** 两平台状态/任务不同，数据量可能不足；容易变成多任务学习，不适合当前论文的理论定位。

**kill：** 只有共享网络权重和经验迁移，没有 operator-level theorem。

## 3. 第一轮评分

| ID | 创新潜力 | 理论强度 | 可证性 | 与两平台契合 | prior-art 风险 | 状态 |
|---|---:|---:|---:|---:|---:|---|
| A1 | 4 | 4 | 3 | 5 | 高 | 保留待杀检 |
| A2 | 5 | 4 | 2 | 4 | 中高 | 保留待杀检 |
| A3 | 3 | 4 | 4 | 4 | 高 | 备选 |
| A4 | 4 | 4 | 3 | 4 | 中高 | 保留待杀检 |
| A5 | 4 | 4 | 3 | 5 | 中高 | 保留待杀检 |
| A6 | 4 | 4 | 2 | 5 | 高 | 暂缓 |
| A7 | 4 | 4 | 3 | 4 | 高 | 保留待杀检 |
| A8 | 3 | 3 | 2 | 3 | 中 | 暂缓 |

## 4. 当前优先组合

暂不选择单一最终路线，优先检查：

```text
A1 actuation-factorized
+ A2 relative-degree-preserving
```

若 A2 对软体视觉输出无法建立 rank/relative-degree 条件，则退回：

```text
A1 actuation-factorized
+ A4 mode-conditioned
```

若 A1 仅退化为已知输入矩阵变换，则 kill A1/A5，并转向 A4 或 A7 的结构性路线。
