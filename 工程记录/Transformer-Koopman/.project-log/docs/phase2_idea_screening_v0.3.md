# 阶段② Idea Screening v0.3：淘汰一般抽象路线，保留受限记忆控制分支

## 1. 本轮结论

### I1 一般 approximate Koopman abstraction：KILL（作为独立创新）

已有 Aspeel & Özay, “A Simulation Preorder for Koopman-like Lifted Control Systems,” IFAC-PapersOnLine 2024, DOI `10.1016/j.ifacol.2024.07.420`：摘要明确提出对带输入的有限维 Koopman approximation 建立 simulation preorder，并证明该关系可包含 open-loop 与 closed-loop behaviors。

因此“建立 lifted-to-physical simulation relation”本身不能作为本项目新贡献。

### I2 一般 reference-compatible controllable lifting：KILL（作为独立创新）

其最小数学问题退化为标准 output controllability / reference governor：

```text
z+ = A z + B u,  y = C z
```

给定 `y_ref`，寻找 `z_ref,u_ref` 使 `C z_ref=y_ref` 且 `z_ref,+ = A z_ref+B u_ref`。这属于线性系统的输出可控性与参考生成问题。

同时已有：

- Uchida & Duraisamy, “Control-aware Learning of Koopman Embedding Models,” ACC 2023, DOI `10.23919/acc55779.2023.10156352`；
- Choi et al., “On The Controllability Preservation of Koopman Bilinear Surrogate Model,” CDC 2024, DOI `10.1109/cdc56724.2024.10886212`。

因此“让 embedding 更 control-aware”或“保持 surrogate controllability”也不能直接作为新点。

## 2. 新的可研究分支：受控有限记忆 Koopman closure

### M6 — Control-aware finite-memory Koopman closure

#### 结构障碍

当前 Transformer history lifting 使用历史窗口，但最后仍强行压缩成无记忆的：

```text
z_{k+1}=A z_k+B u_k+w_k.
```

如果 `h_k` 只是有限历史对未解析变量的压缩，则真实 reduced dynamics 更自然地具有 memory：

```text
x_{k+1}
 = A_0 z_k + B_0 u_k
```

把 memory 全部塞进一个瞬时 latent state，可能导致：

- `A,B` 对输入/历史变化不稳定；
- rollout 中误差积累；
- controller 看到的 lifted state 不是一个真正的 Markov state；
- 当前五项 loss 只能惩罚误差，不能说明 closure 为什么成立。

#### Innovation operator

`Latent-state Introduction` + `Finite-data Extension` + `Approximate Condition` + `Robustification`。

#### 可能的核心贡献

不是“使用 history”，而是构造一个**控制感知的有限记忆 closure**：

1. 将 history encoder 输出解释为 memory state，而非任意 feature；
2. 让 memory kernel 对输入显式条件化；
3. 给出 memory truncation defect `δ_P`；
4. 将控制器稳定性条件写成 memory system 的 companion/Lyapunov 条件，而不是错误地把无记忆 `A` 当成真实闭环矩阵；
5. 证明随着 `P` 增大，closure defect 在明确条件下下降，或至少物理输出误差界显式包含 `δ_P`。

#### 最小理论形式

令：

```text
z_{k+1}=A_0 z_k+B_0u_k+Σ_{j=1}^{P-1}M_j z_{k-j}+D_P ξ_k
```

将其写成 companion lifted state `\bar z_k=[z_k;z_{k-1};...;z_{k-P+1}]`，得到：

```text
\bar z_{k+1}=\bar A_P\bar z_k+\bar B_Pu_k+\bar D_Pξ_k.
```

控制器不再对 `A_0` 做普通 LQR，而是在 `\bar A_P,\bar B_P` 上设计，使 memory-aware closed loop 满足 Lyapunov contraction。物理输出误差界包含：

```text
model residual + memory truncation defect + reference defect.
```

#### 先例与风险

该方向不是空白：

- Lin et al., SIADS 2021, “Data-Driven Learning for the Mori–Zwanzig Formalism: A Generalization of the Koopman Learning Framework,” DOI `10.1137/21M1401759`；
- Gupta et al., Proc. R. Soc. A 2025, “Mori–Zwanzig latent space Koopman closure for nonlinear autoencoder,” DOI `10.1098/rspa.2024.0259`；
- Catalasan & He, *Nonlinear Dynamics* 2026, “Memory-dependent dynamic modeling of cable-driven soft robots using the Mori-Zwanzig Koopman operator,” DOI `10.1007/s11071-025-11934-2`；
- Shenoy et al., ACC 2025, “Temporal Autoencoder for Identification and Predictive Control of Nonlinear Dynamics based on Koopman Operator Theory”。

所以“memory Koopman modeling”单独也不够。真正可能的差异必须是：**控制感知的 memory closure + memory-aware closed-loop theorem + 物理输出保证**。

#### Kill criteria

M6 必须在最小理论检查中被淘汰，如果：

1. memory 项只是把 history state 重新堆叠，完全退化为普通 companion realization；
2. 不能证明 `δ_P` 与历史长度/closure 误差的关系；
3. 控制器定理只是对 companion matrix 使用普通 LQR，没有新的 memory-specific 条件；
4. 与 Catalasan/Gupta/Lin 的工作只剩换成机器人数据；
5. 训练得到的 memory kernel 对 closed-loop 输入分布不稳定。

## 3. 当前候选池

| 分支 | 状态 | 原因 |
|---|---|---|
| I1 一般 approximate abstraction | killed | simulation preorder prior art 已直接覆盖 |
| I2 一般 reference-compatible lifting | killed | 退化为 output controllability/reference governor，且 control-aware embedding 已有先例 |
| I3 actuator/history dynamic extension | killed unless distinct | CCK 2024/2025 已覆盖 virtual dynamics/pre-filtering |
| M6 control-aware finite-memory closure | exploratory | 建模先例存在，但控制闭环 theorem 可能仍有空间 |

## 4. 下一步最小验证

只对 M6 做 T3，不写代码、不训练：

1. 写出受控 Mori–Zwanzig / finite-memory discrete model 的精确定义；
2. 明确 memory kernel、truncation defect 与输入依赖；
3. 推导 companion closed-loop 的 Lyapunov 条件；
4. 比较该条件是否严格区别于普通 augmented-state LQR；
5. 构造 `P=1`、`P=2` 的最小反例，检查 memory truncation claim；
6. 若 T3 只得到普通 AR/companion realization，则 kill M6。
