# 阶段②理论研究 Brief（v0.1）

> 该文档只固化研究流程输入，不代表最终论文路线、定理或代码方案。
> 研究模式参考：`automated_theory_research_agent_initial_design.md`。

## 1. Research Brief

### Domain

- Koopman operator theory
- nonlinear robotic systems
- data-driven system identification
- Koopman-based control
- stability, robustness, constraints and tracking

### Research style

- theory-first
- literature- and assumption-grounded
- candidate-branch exploration rather than single-route commitment
- adversarial falsification before implementation

### Current scope

- 保留 Koopman 框架。
- 建模/lifting 方式可以重设。
- 控制器形式与理论分析可以重设；控制器是优先攻坚部分。
- 代码、配置、现有训练模型暂时冻结。
- 理论路线确定后，再重构代码并重新训练全部模型。

### Target positioning

- 机器人/应用方向期刊或会议（RA-L / T-RO / related robotics venues）。
- 目标不是控制理论顶刊级别的完整基础理论，而是：有明确结构创新、非平凡理论保证、机器人意义和可区分实验。

### Current seed

现有论文包含两块：

1. 建模：基于历史窗口的 Transformer lifting，形成 `z=[x;h]`，并拟合 Koopman 线性受控动力学。
2. 控制器：在 lifted model 上使用 hierarchical LQR，并以建模残差给出 UUB 形式结论。

该 seed 仅作为问题起点，不是已批准路线。

## 2. 暂定研究目标

找到一条同时满足以下条件的 Koopman 理论路线：

1. 比“神经 lifting + 标准 LQR/UUB”有更清晰的结构创新；
2. 控制器理论不是标准结论的直接套用；
3. 假设能够被明确、检查或通过实验压力测试；
4. 至少包含一个可独立陈述和验证的非平凡 claim；
5. 对机器人控制中的扰动、约束、安全、样本有限或实时性问题有实际意义；
6. 能够形成 claim-driven experiments，而不是只展示单一 demo。

## 3. 研究排除项

- 当前阶段不做代码—论文逐项对齐。
- 当前阶段不冻结损失权重、训练流程或部署接口。
- 当前阶段不把上一轮提出的“可测物理残差驱动的认证 Koopman 控制”视为结论；它只是待筛选候选分支。
- 不以“暂时没有检索到相关论文”作为创新性证明。
- 不接受只有经验性能、没有明确理论 claim 的路线作为最终路线。

## 4. 必须建立的研究对象

后续候选分支至少记录：

- `idea_id` 与父分支；
- target gap / restrictive assumption；
- 使用的 innovation operator；
- core claim；
- required assumptions；
- expected theorem / lemma；
- prior-art risk；
- minimal counterexample / falsification test；
- claim-driven experiment；
- status：`proposed | screening | active | refined | killed | validated`。

## 5. 当前状态机位置

```text
S0 Problem Initialization       DONE（本 brief）
S1 Literature Mapping           NEXT
S2 Structured Knowledge         NEXT
S3 Gap / Assumption Mining      NEXT
S4 Idea Generation              AFTER S1-S3
S5 Screening / Falsification    AFTER S4
S6 Theory Construction          ONLY for surviving branches
```

## 6. 当前下一步

先建立与本项目直接相关的文献/理论结构表，至少覆盖：

- Koopman lifting 与 delay/history embedding；
- controlled Koopman、bilinear Koopman、state-dependent input structure；
- robust Koopman control / Koopman MPC；
- safety-critical Koopman control；
- data-driven / finite-sample control guarantees；
- residual, adaptive and uncertainty-aware Koopman models。

每类不先写泛泛综述，而是抽取：`Problem / Assumptions / Definitions / Main Theorems / Method / Limitations / Unresolved Gap`。
