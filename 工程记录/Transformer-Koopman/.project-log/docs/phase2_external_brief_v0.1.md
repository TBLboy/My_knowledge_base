# 阶段② 外部咨询简报：为一篇 Koopman 控制论文寻找真正有创新的理论路线

> 用途：交给外部 AI（GPT）协助攻克“找到一个真正改变建模与控制器的理论路线”这一开放问题。
> 本文档是**问题打包**，不是结论。所有陈述已标注 **【确认】/【假设】/【未知】/【待助】**。
> 不含密钥与个人信息。

---

## 1. 目标与确切问题

### 1.1 项目目标
- **论文**：一篇机器人方向的 Koopman 控制论文（目标期刊 RA-L / T-RO 或机器人会议）。
- **论文现状**：已有方法 = 时序 Transformer lifting + 线性 Koopman 模型 + LQR 跟踪控制器；**实验章节为空，理论证明有错**。
- **阶段目标**：不是在旧方法上补证明，而是要找到一条**同时改变建模参数化/辨识目标与控制器结构**的新理论路线，并能在现有两个平台上验证。

### 1.2 请求 GPT 回答的确切问题
> 在下面给出的两平台、数据、约束下，是否存在一条**可被现有数据识别、且真正改变建模与控制器结构、并导出一个非平凡可验证定理**的 Koopman（或 operator-learning）路线？
> 如果没有，请明确指出必须补采什么数据、或应把论文范围缩小成什么样（例如只做 P1 或只做 P2）。
> 请对每个候选给出：模型方程、辨识目标、控制器合成形式、适用平台、定理目标、最近 prior art、可证伪实验、kill 条件。

### 1.3 什么算“合格”的路线（硬门槛）【确认】
候选必须同时满足：
1. **建模改变**：不能只是“history Transformer 编码 + 拟合常数 (A,B)”。
2. **控制器改变**：不能只是“B† 前馈 + 固定 LQR”。
3. **物理锚点**：P1 二阶机械动力学、P2 部分可观测视觉 + 执行器层，至少各有明确角色；不得假设未测的张力/能量。
4. **新定理**：不能是标准 ISS/UUB/LQR/robust-MPC 定理换记号。
5. **prior-art 门禁**：需方法/定理级对比，元数据检索不算通过。
6. **可落地**：能用现有数据测；若需新传感器需明确声明为缺口。

---

## 2. 相关系统与项目背景

### 2.1 代码仓库
- 路径：`D:\Project\Transformer-Koopman\Transformer-Koopman\`
  - `训练代码/`（源代码、config、scripts、tests、deploy）
  - `数据备份/机械臂数据/`（P1：20 个 .mat 原始 + 处理后的 train/val/test.npz）
  - `数据备份/软体平台数据/`（P2：100 个 .npz 原始 + 处理后的 train/val/test.npz）
  - `论文/草稿/Main34.tex`（最新论文草稿，895 行）
  - `软控逻辑.txt`（P2 软体平台全栈规格书 V3.6）
- 项目事实源：`.project-log/`（Vibe Workflow format 2，SQLite + ledger）。

### 2.2 论文现有方法（= 当前被否定为无创新的方法）【确认】

**建模（时序 lifting + 线性 Koopman）：**
- 历史窗口 $X_k=[x_{k-P+1}^\top,\dots,x_k^\top]^\top\in\mathbb{R}^{P\times n}$（P=8）。
- patch（p=2，N=4 token）→ 共享线性嵌入 + 正弦位置编码 → L 层自注意力 → **mean pooling** → 投影得 $h_k\in\mathbb{R}^{d-n}$。
- 提升状态 $z_k=[x_k;h_k]\in\mathbb{R}^d$；固定解码 $x_k=Cz_k,\ C=[I_n\ 0]$。
- 线性 Koopman 动力学（**常数矩阵**）：$z_{k+1}=Az_k+Bu_k$。
- 三阶段训练：Stage0 EDMD ridge 热启动 $\Theta=(Z^+)^\top\Omega(\Omega^\top\Omega+\lambda I)^{-1}$；Stage1 五项损失联合优化（$L_x,L_z,L_c,L_{multi,x},L_{multi,z}$）；Stage2 固定编码器 ridge 重拟合。

**控制器（线性跟踪）：**
- $u_k=u_{ff,k}+u_{fb,k}$；
- 前馈 $u_{ff,k}=B^\dagger(z^{ref}_{k+1}-Az^{ref}_k)$；
- 反馈 $u_{fb,k}=-K_c e^z_k$，$e^z_k=z_k-z^{ref}_k$；
- $K_c=(R+B^\top PB)^{-1}B^\top PA$，离散 LQR，$Q=\mathrm{diag}(Q_x,\alpha I)$。

**这篇论文的已知错误【确认】：**
- 定理 1（Main34.tex 约 L717–738）声称 "Schur 稳定 ⇒ $\|A_{cl}\|<1$"，**这是伪推理**（反例 $A=\begin{bmatrix}0.95&3\\0&0.95\end{bmatrix}$，$\rho=0.95$ 但 $\|A\|_2=3.2755$）。
- 误差动力学**遗漏前馈不可达项** $-(I-BB^\dagger)(z^{ref}_{k+1}-Az^{ref}_k)$。
- 界 $\varepsilon/(1-\|A_{cl}\|)$ 分母可为负。

### 2.3 两个平台的物理与数据

#### P1：Geomatric Touch（3-DOF 刚体机械臂）
- **【确认】** 状态 $x=[q_1,\dot q_1,q_2,\dot q_2,q_3,\dot q_3]$（6 维，位置/速度交替）；3 个关节输入通道。
- **【确认】** 数据：train 15 条（74655×6）/ val 4 条（19909×6）/ test 1 条（4976×6）；x=(N,6)，u=(N,3)；密钥 `x,u,t,trajectory_id`。
- **【未知】** 输入到底是不是力矩、还是速度/位置增量；是否有饱和、摩擦、传动比。
- **【确认】** 无 P1 训练 checkpoint（结果备份为空）。

#### P2：柔性绳驱光点系统（欠驱动连续体）
- **【确认】** 是被牵引的四绳欠驱动柔性连续体；视觉反馈只测投影平面上的 2D 光点位置。
- **【确认】** 上位机命令 $v=(dx,dy)$（2 维）；下位机用**固定差动映射**执行 4 根绳：$R=+dx,\ L=-dx,\ D=-dy,\ U=+dy$。
- **【确认】** 控制周期 $T_s\approx0.2\,s$；$|u_{\max}|=V_{\max}(T_s-0.05)=2000\times0.15=300$ 步；张紧由初始“临界张紧”标定保证；**共模（R+L、U+D 同向）从不下发**。
- **【确认】** **无张力传感器、无绳长、无速度、无 mode 标签**。
- **【确认】** 数据：train 70 / val 20 / test 10 条轨迹，每条 300 点，$\Delta t\approx0.2s$；x=(N,2)，u=(N,2)。
- **【确认】** 唯一可用 checkpoint 是部署侧 `platform2_full_model.pth`：A(10,10)、B(10,2)，**谱半径 $\rho(A)=2.0878>1$（模型本身不稳定）**，metadata history_length=4 与 config 8 不一致。

### 2.4 目标论文的定位取向
- **【确认】** 保留 Koopman 框架；建模（lifting）与控制器（控制律/分析）都可重设。
- **【确认】** 目标 = 机器人/应用期刊，理论够用即可，重创新与实验验证。

---

## 3. 期望行为 vs 实际行为

| 期望 | 实际 |
|---|---|
| 找到一条同时改变建模与控制器、且有非平凡定理的 Koopman 路线 | 目前**没有**选定路线；多个候选被淘汰 |
| 新路线能在现有两平台数据上验证 | 现有 P2 数据结构严重限制可辨识性（见 §4） |
| 论文有可发表的理论贡献 | 旧路线仅“补证明”，被判定无创新 |

---

## 4. 复现与确切证据

### 4.1 P2 数据审计（已运行，脚本 `audit_p2_psr.py`）【确认】
- 训练动作样本 **30000**，**唯一动作向量 = 30000（全部唯一）**。
- 动作**不是整数**：精确整数比例 **0%**，距最近整数最大误差约 **0.5**。
- 长度 1 / 2 / 3 的 action prefix 重复次数全部为 **0**。
- 结论：现有 P2 数据**无法支撑**“action-conditioned PSR + 离散 pulse sequence planning”，因为没有动作前缀支持、无法从离线数据估计条件未来分布。

### 4.2 P2 最小建模 spike：affine vs bilinear（脚本 `spike_p2_bilinear.py`）【确认】
- affine：$x_{k+1}=Ax_k+Bu_k+c$ → val RMSE **0.116112**，val MAE 0.094027。
- 一阶 bilinear：$x_{k+1}=Ax_k+Bu_k+\sum_i u_{k,i}N_i x_k+c$ → val RMSE **0.116048**，val MAE 0.094062。
- 结论：bilinear 相对 affine **几乎无收益**（RMSE 改善 ~6e-5，MAE 更差），不足以升格为路线。

### 4.3 旧理论修正（脚本 `s8_verify_t1.py`, `s8b_p2_terms.py`）【确认】
- 已构造修正界 $T1'$（Lyapunov 形式）：$\|e^z_k\|\le\sqrt{\lambda_{\max}/\lambda_{\min}}(1-\lambda)^{k/2}\|e^z_0\|+\sqrt{\lambda_{\max}/\lambda_{\min}}\cdot D/(1-\sqrt{1-\lambda})$，$D=\varepsilon+\|B\|\Delta\sqrt m/2+\delta$，$\lambda=\lambda_{\min}(Q+K_c^\top RK_c)/\lambda_{\max}(P)$。
- 独立复核确认数学核心正确，但认定：**这只是纠错，不是创新**；且 P2 部署模型上界数值空泛（cond(P)~2e10，常数 ~8e15）。

---

## 5. 环境、依赖、接口与约束

- **OS**：Windows，PowerShell 5.1。
- **项目解释器**：`D:\conda\envs\edmddl2\python.exe`（py3.9, numpy 1.26.3, scipy 1.13.1, torch 2.6.0+cu124）。
- **数据契约**：`x[N, state_dim]`、`u[N, control_dim]`、`t[N]`、`trajectory_id[N]`；history 窗口不跨 trajectory。
- **P2 接口**：命令是 2D；部署侧模型输入就是 2D，差动映射已在执行层。
- **约束（不得违反）**：
  - 不得假设 P2 有张力/速度/mode/能量变量。
  - 不得把处理后的连续浮点 `u` 静默当作整数 pulse。
  - 不得用“P1/P2 共享机械能”这类未证实假设。
  - 不得把标准 switched/delay/quantization/CBF/tube/adaptive/hierarchy **换名字**当创新。
  - 不得只修正旧证明。
- **实时预算**：P2 控制回路 ~0.2s（可用约 0.15s）；在线 Schrödinger/混合整数规划可行性存疑。

---

## 6. 已尝试的路线与观察结果（淘汰/降级记录）

| 路线 | 判定 | 依据 |
|---|---|---|
| 旧 T1′ 修正（旧方法 + 修证明） | **降级为纠错基线** | 未改变建模/控制器结构；用户明确否定创新 |
| I1 一般 Koopman abstraction | 淘汰 | Aspeel & Özay 2024 simulation preorder (10.1016/j.ifacol.2024.07.420) |
| I2 reference-compatible lifting | 淘汰 | 退化为 output controllability/reference governor + control-aware embedding (Uchida & Duraisamy 2023, 10.23919/acc55779.2023.10156352) |
| I3 actuator/history extension | 淘汰 | Asada CCK 2024/2025 (10.1109/cdc56724.2024.10886771; 10.1109/lcsys.2025.3582608) |
| M6 memory/Mori-Zwanzig Koopman | 暂缓 | Lin 2021 (10.1137/21M1401759)、Gupta 2025、Catalasan & He 2026 |
| D1 dissipativity/passivity | 淘汰 | 无确证 physical supply rate |
| A1 actuation-factorized | 淘汰（通用形式） | Cibulka/Korda/Haniš 2025 SIADS (10.1137/23m1597174) |
| A3 quantized-delay | 降级 | 标准 sampled-data/delay/quantized 理论 |
| A4 mode-conditioned | 淘汰（通用形式） | Blischke CDC 2023、Peitz 2019、Ning 2025、Ju 2026 |
| A5 task/actuator dual | 淘汰（通用形式） | Boyle & Stockar 2023 (10.1115/1.4056703) |
| A9 未指令张紧偏置 | 淘汰（物理不成立） | P2 共模从不下发，$a_\perp=0$ 按设计 |
| 随机 transfer operator + Schrödinger bridge | 不采纳（当前） | 过宽、理论缺口大、无分布辨识数据 |
| PSR/预测状态 + 离散 pulse planning | **数据否证淘汰** | 30000 动作全唯一、prefix 无重复（§4.1） |
| 一阶 bilinear Koopman | 不升格（低优先备选） | 最小 spike 无收益（§4.2） |
| input-conditioned operator family / LPV-Koopman | 邻域拥挤 | Haseli/Mezić/Cortés CDC 2025 (10.1109/cdc57313.2025.11312881)；Cisneros IFAC 2020；Chen CDC 2024 |
| Koopman generator feedback linearization | 已有直接先例 | Gadginmath/Krishnan/Pasqualetti TAC 2024 (10.1109/tac.2024.3417188) |

**结论【确认】：目前没有经 prior-art + 数据门禁的最终理论路线。**

---

## 7. 未知与被请求的帮助

### 7.1 仍未解决的关键未知
1. **【未知】** P1 的输入到底是什么（力矩/速度/位置增量），是否量化——决定了哪些控制器可做。
2. **【未知】** P2 的 2D 光点是否足以支撑“有控制意义的隐状态”推断；历史窗口是否提供可辨识的未来信息。
3. **【未知】** 现有连续、几乎不重复的控制数据，能否支撑任何需要条件分布/干预的路线，还是只能做普通连续输入回归。
4. **【未知】** 是否存在一个共同 operator/observer/controller 抽象，能在不假设共享物理量的前提下同时覆盖 P1 与 P2。
5. **【待助】** 是否有一个**只有 Koopman/operator 结构才能给出、且非标准最优控制重述**的定理目标。

### 7.2 请求 GPT 的具体帮助
请在如下约束下给出候选与判断：
- 输入是**连续浮点**、单轨迹内动作近乎唯一、无重复 action-prefix；
- P2 只有 2D observation，无张力/速度/mode；
- P1 输入语义未定；
- 必须**同时改变建模与控制器**，且不能是已列出的拥挤方向换名；
- 需给出可被现有数据证伪的最小实验。

**并请明确回答：**
1. 是否有一条真正可行的新路线？还是已证明现有数据不足以支撑创新，应转向补采数据/缩小范围？
2. 如果补数据，**最小补采方案**是什么（补什么量、补多少、如何保证可辨识）？
3. 如果缩小范围，**哪种缩小**最可能仍构成可发表的理论贡献（P1-only 物理结构？P2-only 部分可观测与执行器结构？）？

### 7.3 不要把下列当作已知事实
- P2 有张力/绳长/速度/能量/supply rate；
- P2 的处理后动作是整数脉冲；
- P1 与 P2 共享同一天然能量或物理结构；
- 旧 T1′/量化项本身具有创新性。

---

## 附：可供 GPT 直接查看的关键文件路径
- 论文草稿：`Transformer-Koopman/论文/草稿/Main34.tex`
- P2 规格：`Transformer-Koopman/软控逻辑.txt`
- 路线重置：`.project-log/docs/phase2_route_reset_v0.1.md`
- PSR 审计：`.project-log/docs/phase2_psr_audit_v0.1.md`
- 旧理论构造（纠错基线）：`.project-log/docs/phase2_theory_construction_v0.1.md`、`…v0.2.md`
- 分支淘汰总表：`.project-log/docs/phase2_branch_status_v0.5.md`
- 平台语义：`.project-log/docs/phase2_platform_semantics_v0.1.md`
