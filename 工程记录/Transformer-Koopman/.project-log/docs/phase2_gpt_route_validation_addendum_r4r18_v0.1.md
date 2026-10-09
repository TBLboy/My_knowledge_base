# 阶段② GPT 路线验证：R4–R18 prior-art 补充（第二遍）v0.1

> 日期：2026-10-05  
> 说明：本条为独立第二轮 R4–R18 prior-art 复核，用于补充/校准 `phase2_gpt_route_validation_v1.md`。  
> 证据分级：`[经典]` 奠基/教科书；`[全文级-片段]` 读到正文公式/定理片段；`[摘要级]` 仅摘要/片段；未做 L3 逐定理对拍。

## 1. 与第一遍一致的主结论

- R4、R6、R7、R9、R10、R13 基本属**经典方法换名**或**已被 Koopman 特例直接占用**。
- R5、R14、R18 为**部分换名**，需新定理/度量。
- R15 在 GCRL 侧是标准双编码。

## 2. 第二遍的重要细化（新增/加强）

| 路线 | 新增先例（第二遍） | 性质 |
|---|---|---|
| R4 | Koopman-SPC arXiv:2405.01292；Khatri–Rao 多步输出预测 arXiv:2606.02938；Korda–Mezić 2018 condensed I/O | 撞车**加强**（学有限时域 I/O 映射 = SPC） |
| R5 | arXiv:2509.17010 **显式解耦已知线性 actuation 通道与 unactuated 动力学**；CCK；input–state separable 综述 arXiv:2408.04200 | 撞车**加强**（actuated/unactuated 已有直接先例） |
| R6 | ICLR 2026（Miao 等）Koopman **controllability-preserving 参数化 + Gramian 正则**；arXiv:2507.04188 generalized-SVD Gramian | 撞车**加强** |
| R7 | Enns 1984；Ren PMLR v211(2023) LQG 控制器降阶界；B-NODE arXiv:2410.10174 | 撞车加强 |
| R9 | **`M_h=Σ (A^j)^T C^T Q_x C A^j` 就是有限时域可观测 Gramian（带输出权重）** | **经典**；"physical-state-preserving" 只来自 C 设计选择 |
| R10 | arXiv:2607.05718 输入 Jacobian Frobenius 正则 + ISS/contraction 界；Finlay 2020 | 撞车**加强**（几乎逐字对应） |
| R13 | Ho–Kalman/ERA；Oymak–Ozay arXiv:1806.05722；Arbabi–Mezić **DMD≡ERA 等价定理** | 撞车**加强** |
| R14 | ν-gap（Vinnicombe 1993）；数据驱动 ν-gap arXiv:2603.17545；LQG-BT 本身=Riccati 加权 | 撞车加强 |
| R15 | GCRL 双编码：Dual Goal Representations arXiv:2510.06714；GRIF CoRL 2023；Contrastive RL | 换名（GCRL 侧） |
| **R16** | 充分性理论：Lamb NeurIPS 2021；Huang ICML 2022 ASR；**arXiv:2507.19437** observation vs control sufficiency；arXiv:2601.22496 | **Koopman 版未检索到直接先例 → 残余空间最大** |
| R18 | ν-gap / coprime factor / MPM 定位 / discrepancy arXiv:2203.05164 | 换名高风险 |

## 3. 残余新颖空间排序（第二遍）

```text
R16 > R15 ≈ R18 > R14 > R5 > R4/R7/R13 > R6/R9/R10
```

- **R16**：把 control-sufficiency 定义**移植到 Koopman 线性 latent**（如 `I(A; future | φ(x), u)=0`）、证明“控制充分 Koopman ⇒ latent 线性 MPC 近似最优”、双编码器架构与可辨识性——未检索到直接先例。
- **R15**：把 reference/task encoder 嵌入**线性 Koopman 框架**并强制 `ψ` 与 `φ` 在算子作用下一致（甚至共用 `A`）——小块可守。
- **R18**：**正交/可加且逐项有界并绑定闭环性能**的缺陷分解——否则与 ν-gap + discrepancy 重叠。

## 4. 两遍复核的一致与分歧

- **一致：** R4/R6/R9/R10/R13 换名；R5/R14/R18 部分换名；R15 GCRL 换名。
- **分歧（R16）：** 第一遍判“部分换名、残余中”；第二遍判“残余空间最大”。差异源于负向检索（Koopman 侧是否已有 control-sufficient 双编码）不可完全证实。
- **与 R1–R3 复核的合流：** 结合第一份报告（R1 “delta 窄但实在”、R3 “需补控制定理”），**全局残余空间最大的三个是 R1、R3、R16**（分别对应 Test B、Test C 的前提，以及充分性理论移植）。

## 5. 待做 L3 全文对拍（合并两遍清单）

1. arXiv:2405.01292、2606.02938（R4）；2. 2509.17010（R5/R13）；3. ICLR 2026 poster 10007892（R6/R7/R9）；4. arXiv:2507.19437、2601.22496（R16）；5. arXiv:2603.17545 + Vinnicombe 1993（R14/R18）；6. arXiv:2607.05718（R10）；7. arXiv:2602.14537（R13）；8. arXiv:2311.13033 + 2307.15368（R18/R9）；9. arXiv:1709.08712（R6/R7）；10. arXiv:2209.08637 + 2402.03145（R14）。

## 6. 未决

- R16 的“残余最大”依赖负向检索，需专门再扫一轮（关键词：goal-conditioned Koopman、control-sufficient Koopman、action-sufficient latent dynamics）。
- 全部为 L2/片段级，未做 L3；2026 预印本未同行评审。
