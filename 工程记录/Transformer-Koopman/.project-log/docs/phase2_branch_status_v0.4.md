# 阶段② 分支状态总表 v0.4

## 已淘汰

### I1：一般 approximate Koopman abstraction

- 原因：Aspeel & Özay 2024 已提出 Koopman-like lifted control systems 的 simulation preorder，并覆盖 open/closed-loop behavior。
- 不能再作为独立贡献：建立 lifted-to-physical relation 本身已被直接覆盖。

### I2：一般 reference-compatible controllable lifting

- 原因：最小问题退化为 output controllability / reference governor；Uchida & Duraisamy 2023 已有 control-aware Koopman embedding，Choi et al. 2024 已研究 Koopman bilinear surrogate controllability preservation。
- 只能作为普通控制工具或后续子模块，不能作为论文中心创新。

### I3：一般 actuator/history dynamic extension

- 原因：Asada 2024/2025 的 CCK / actuator pre-filtering / virtual dynamics 已覆盖核心结构制造模式。
- 只有在不同的物理障碍和不同定理下才可能重新打开。

### M6：一般 finite-memory / Mori–Zwanzig Koopman closure

- 原因：Lin et al. 2021、Gupta et al. 2025、Catalasan & He 2026 等已有 memory Koopman / MZ closure；项目当前还假设全状态可测，history 作为 memory 的理论必要性不够强。
- 当前 deferred；若不能证明控制专用的 memory theorem，将 kill。

## 受限候选

### D1：Dissipativity-constrained Koopman lifting + controller

- prior-art 风险：port-Hamiltonian、passivity-preserving control、structure-preserving Koopman work 均有相邻工作。
- 当前项目阻塞：只有 `x,u` 数据语义，尚未证明 P1/P2 存在统一且可验证的 physical supply rate。
- 状态：`exploratory-blocked`，不是主线，不进入代码。
- 继续条件：确认状态变量/输入端口的物理意义，并证明结构约束能带来非平凡 physical-output theorem；否则 kill。

## 当前真实结论

目前还没有一个经过 prior-art 与理论可行性门禁的“最终创新路线”。这是合法研究结果，不能用候选数量掩盖这一点。

## 下一步研究方向

优先级如下：

1. 读取原始数据/论文上下文，确认 P1/P2 的状态变量语义；
2. 若 D1 无法定义真实 supply rate，彻底 kill D1；
3. 回到 Innovation Operator Library，从“结构约束但不依赖未确认物理量”的方向重新生成候选；
4. 重点考虑：输入/输出物理维度固定的 operator factorization、task/reference-conditioned Koopman subspace、以及可检验的 control-relevant observables，而不是再加通用 robust/CBF/adaptive 模块。
