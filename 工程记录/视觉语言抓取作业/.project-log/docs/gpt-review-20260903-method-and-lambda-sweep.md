# External GPT Review: Final Method and Next Experiments

> 记录时间：2026-09-03
> 来源：外部 GPT 对
> `.project-log/docs/context-briefing-20260903-10k-method-decision.md`
> 的回复。

## 1. External recommendation

外部 GPT 的结论是：

1. 固定 `LSAR-no-aff` 为最终方法。
2. 论文主方法命名为 `LSAR`，不再叫 `no-aff`。
3. 旧 `LSAR-full` 改称 `LSAR + Auxiliary Affordance Supervision`。
4. 补 `lambda_aff` sweep：
   `{0, 0.01, 0.05, 0.1}`，保持 10k、15 epochs、单 seed。
5. 补 `LSAR-no-aff` 第二个训练 seed。
6. 可选补 5000-sample `LSAR-no-aff`，用于解释 scale-dependent reversal。
7. 不继续 Transformer、Flow Matching 或扩大数据。

## 2. Project assessment

同意主要判断：

- 10k 证据已经足够证明 LSAR residual conditioning 有效。
- `lambda_aff=0.1` 不是稳定增益来源；
  当前只能确认 “0.1 不适合”，不能直接证明所有权重都不适合。
- `lambda_aff` sweep 是论文风险最低、解释力最高的补充实验。
- 第二个训练 seed 只补最终候选模型即可，不需要三模型重跑。
- paper 不再写
  `affordance supervision improves grasp`，
  而是写
  `language-conditioned spatial representation refinement helps diffusion-based grasp generation`。

## 3. Code-level caveat

`models/lgdm_lsar.py` 的 LSAR 模块无论是否使用 aux loss 都会通过
`aff_head` 计算 `affordance_map`。

最终方法使用：

```text
--condition-mode lsar \
--lsar-scale 0.01 \
--lsar-fixed-scale \
--lsar-affordance-weight 0.0
```

旧 LSAR-full ablation 使用：

```text
--lsar-affordance-weight 0.1
```

论文不要把 `affordance_map` 描述成“监督出来的空间图”；它只是模块的
可解释副产品，final method 不优化它。

## 4. Proposed execution order

1. `lambda_aff=0.01` 训练 + 单次 eval
2. `lambda_aff=0.05` 训练 + 单次 eval
3. 汇总 sweep：0 已是 `653.7`（repeat mean），0.1 已是 `605.3`
   （repeat mean）
4. 若 0.01/0.05 未超过 0，固定 `0` 为最终方法；
   若超过，换最优 `lambda` 并补 repeat eval
5. `LSAR-no-aff` 第二训练 seed（seed 43）
6. 可选：5000-sample `LSAR-no-aff`
7. 更新 paper narrative 和最终表格

## 5. Decision status

- 外部建议已记录。
- 用户已确认执行，当前开始 Step 1：lambda sweep。
- `lambda_aff=0.01` 已启动；
  完成后继续 `lambda_aff=0.05`。
