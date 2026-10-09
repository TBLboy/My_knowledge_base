# 阶段② GPT 路线逐条验证报告 v1

> 日期：2026-10-05  
> 范围：对 GPT 报告中的 R1–R18 及 4 个组合，逐条给出**验证结论与反馈**。  
> 原则：**只做验证与反馈，不构思新路线**。  
> 证据分级：**L1** 标题/摘要/元数据；**L2** 摘要 + 正文片段（本次绝大多数）；**L3** 全文定理级比对（**未做**）。  
> 注意：所有 prior-art 结论均为 **L2**，不足以让任何路线通过项目的 §2 硬门槛；正式淘汰前需 L3 对拍。

---

## 1. 三项便宜测试结果（前提验证）

| 测试 | 对应路线 | 结果 | 前提是否成立 |
|---|---|---|---|
| **A gauge pathology** | R2 | 物理预测完全不变（1.5e-13）；固定 `Q` 的 LQR 在病态 gauge 下控制律/闭环显著改变（condT=1e2→跟踪差 0.66~0.83；condT=1e6→DARE 失败 3/4） | 现象**成立**；但见下方限定 |
| **B reference defect** | R1 | P2 约 **16~21%** 的 lifted 参考增量落在 `im(B)` 外（仅一阶） | **成立**（一阶） |
| **C residual AR** | R3 | P1 残差 AR(1) 一步改善 **17%~25%**，ACF 衰减慢 | **成立** |

细节见 `phase2_gpt_route_tests_abc_v0.1.md`。

---

## 2. 逐条路线判定

### 第一优先级

#### R1 Reachability-Aligned Koopman — **部分可行（delta 窄但实在）**
- **前提验证：** Test B 成立（16~21% 一阶缺陷）。
- **prior-art：** 参考不可达现象、`(I−BB†)` 投影、投影+regulation 控制**已被覆盖**（Korda–Mezić Automatica 2018 / arXiv:1611.03537；KTMPC arXiv:2208.12000；ScaRe-Kro arXiv:2601.01076；arXiv:2607.06459）。
- **残余 delta（生死线）：** 把不可达残差当作**表示学习损失**去训练字典 + **多步可达子空间对齐**（现有工作只把它用于前馈/证书，未见用于训练目标）。
- **反馈：** 可行，但必须（a）证明多步可达性（一阶为 0 ≠ 多步可达，是审稿致命点）；（b）做 L3 全文对拍 ScaRe-Kro / arXiv:2607.06459。
- **可行性评级：中**。

#### R2 Gauge-Invariant Koopman Control — **不可行作为主定理（新颖性高风险）**
- **前提验证：** Test A 现象成立，但 prior-art 表明：**LQR 在协变代价下相似不变是 1984 年已知结果**（Majumdar 1984；Al-Iedani & Gajić 2020）；固定 `Q=diag(Qx,αI)` 只是**选定一个 gauge**；物理输出代价 `CᵀQC` 是标准修法（KF-LQR arXiv:2201.11640）；KEEC arXiv:2312.01544 已做“等价 predictor → 等价控制”。
- **残余 delta：** 仅在受限 gauge 群（`C=[I 0]` 约束）下给出**新不变量或 gauge-equivariant 算法性质**时才成立。
- **反馈：** 若只写“固定 Q 不行、改用物理输出代价”，会被判为**已知事实重述**。**不建议作为主线**；可降为分析工具。
- **可行性评级：低**。

#### R3 Structured Residual-Dynamics Koopman — **部分可行（需补控制理论）**
- **前提验证：** Test C 成立（残差可预测 17~25%）。
- **prior-art：** 方法重叠 **DEKC arXiv:2506.08319**、discrepancy modeling **arXiv:2203.05164**、Sargsyan 2019、RK-MPC arXiv:2604.04221；“残差=动态子系统”是成熟的不确定性量化纲领。
- **残余 delta：** 面向控制的**联合可辨识性/闭环定理**；以 lag-1 自相关作为“augment vs 当噪声”的**可证伪判据**；相对 DOB/ESO 的**优势条件**。
- **反馈：** 可行，但若只主张“把残差当子状态联合建模再做 augmented 控制”，大概率被判与 DEKC/discrepancy 重叠。必须加定理。
- **可行性评级：中**。

### 第二优先级

| ID | 判定 | 最近先例（L2） | 反馈 |
|---|---|---|---|
| **R4** Output-Predictive/Markov | **换名（高）** | SPC（Favoreel'99）；DeePC（Coulson'19）；Koopman-SPC arXiv:2405.01292；condensed multi-step EDMD arXiv:2601.11901 | 直接学有限时域 I/O 映射 = SPC；2601.11901 已做 condensed 多步映射。仅当加“非不变字典的控制相关误差界/稳定性”才有缝 |
| **R5** Actuated/Transverse | **部分换名（高）** | 不变子空间 Brunton 2016；KCF arXiv:2307.15368；TFL Nielsen–Maggiore；arXiv:2403.16306 | `actuated/transverse` = 欠驱动/TFL 分解；且 P2 共模按设计不被激励（A9 已 kill），物理载体被削弱 |
| **R6** Gramian normalization | **换名（很高）** | **Yeung–Liu–Hodas arXiv:1709.08712**（Koopman Gramian + balanced truncation）；Moore'81 | 按可控 Gramian 归一化 = balancing，且已在 Koopman 实现。几乎无独立空间 |
| **R7** Balanced predictive-control | **部分换名（高）** | LQG balanced truncation（Jonckheere–Silverman'83）；Ren L4DC'23 | `predictive-control coordinates` ≈ LQG/闭环 balanced；仅“有限时域 condensed 预测器”的 balancing 有窄缝 |
| **R9** Physical-state-preserving metric | **部分换名（中高）** | Brunton 2016；Korda–Mezić arXiv:1810.08733；Proctor KIC 2018 | 状态入不变子空间 + latent 内积 = 相似变换的度量选择；残余在“坐标不变的控制相关度量” |
| **R10** Control-effect Jacobian reg | **辅助** | soft-robot controllability reg（Nature Comm 2026） | 单纯增强可控性已有先例；只能作辅助目标 |
| **R13** Finite-horizon realization | **换名（高）** | **arXiv:2602.14537**（N-step predictability ⇔ CAP）；Ho–Kalman'66；Qin'10 | 有限时域实现 ≈ Markov realization；仅“非 CAP 系统的近似实现 + 时域-误差权衡”有窄缝 |
| **R14** Control-relevant model error | **部分换名（高）** | control-relevant ID（Rivera–Morari'87）；ν-gap（Vinnicombe）；Uchida–Duraisamy arXiv:2209.08637；SafEDMD arXiv:2402.03145 | 概念被占；残余在“Koopman 专属、可计算的新控制相关度量” |
| **R15** Joint reference generator | **换名（高）** | reference/command governor（MERL TR2014-119；Garone 2017）；项目 **I2 已 kill** | 让参考落入 range(B) = reference governor。薄 |
| **R16** Dual-encoder control-sufficient | **部分换名（高）** | **BCPO arXiv:2507.19437**；ASR Huang ICML'22；empowerment arXiv:2605.30656 | observation vs control sufficiency 已是成熟二分；残余在“非奖励依赖地定义到 lifted 线性模型” |
| **R17** Cross-Platform | **叙事层** | — | 范围过大；建议只作统一叙事，不单独成路线 |
| **R18** Closed-loop defect decomposition | **换名（高，作独立贡献）** | invariance proximity arXiv:2311.13033；Nüske'23；SafEDMD Cor 3.2；项目自身 T1′ | 标准误差传播；项目已写过。仅“与 task cost 绑定 + 接口缺陷紧性/不可消除性”有窄缝 |

### 组合路线

| 组合 | 组成 | 判定 |
|---|---|---|
| **Combo A** | R1+R15+R18 | 只有 R1 有实在 delta；R15/R18 换名。混合，需剔除 R15/R18 的“独立贡献”定位 |
| **Combo B** | R2+R9+R4 | R2 高风险（已知事实）+ R4 换名；**不建议** |
| **Combo C** | R3+R12+R18 | R3 需补控制定理；R12（残差白化）是经典 innovation 思想；P1 契合 |
| **Combo D** | R4+R13+R2 | R4/R13 换名 + R2 高风险；**不建议** |

---

## 3. 反馈与优先级

1. **作为中心创新，R4、R6、R13、R15、R18（字面表述）基本是换名**，分别撞 SPC/DeePC、balanced truncation、Markov realization、reference governor、标准误差传播 → **不建议作主线**。
2. **R5、R7、R9、R14、R16 是“部分换名”**，只有补一个**新的、可检查的定理/度量/条件**才有缝。
3. **R2 新颖性最弱**（1984 已知结果）→ 不建议作主定理。
4. **R1 的 delta 最实在**（Test B 支持），但必须解决多步可达 + 全文对拍。
5. **R3 需补面向控制的理论**（Test C 支持动机）。
6. **两条子 Agent 一致指向同一处残余空间：**
   - 把不可达残差作为**表示学习损失** + 多步可达对齐（R1）；
   - **坐标不变的控制相关闭环界**（R7/R9/R14/R18 的交集），抓手是“控制相关性”本身。
7. **唯一相对未被覆盖的结构对象**是 P2 的执行器接口（2D 指令→4 绳差动的秩/核 + 量化/饱和），但共模/核方向按设计不被激励（A9 已 kill），且量化项贡献很小（`‖B‖e_max≈0.014`）→ 只剩“量化 + 前馈不可达 δ 的控制相关计入”。

---

## 4. 风险与未决

- **全部 prior-art 为 L2**（摘要+片段），未做 L3 全文定理对拍；正式淘汰前必须补。
- R1 的多步可达性未验证；一阶残差为 0 不代表多步参考可达。
- R2 是否只是 Majumdar 1984 的特例，需 L3 确认。
- R3 与 DEKC/RK-MPC 的方法重叠度需全文确认。
- 2026 年预印本（2601/2602/2605 等）未同行评审，需核实。

---

## 5. 建议的 L3 全文对拍优先级

1. arXiv:2601.11901（risks R4/R13）；2. arXiv:2602.14537（risks R13）；3. arXiv:2311.13033 + 2307.15368（risks R18/R9）；4. arXiv:1709.08712（risks R6/R7）；5. arXiv:2209.08637 + arXiv:2402.03145（risks R14）；6. arXiv:2507.19437 + 2605.30656（risks R16）；7. MERL TR2014-119（risks R15）；8. Rivera–Morari 1987 / Vinnicombe ν-gap。
