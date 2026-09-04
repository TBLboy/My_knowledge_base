# LSAR Experimental Validation Plan

> 记录时间：2026-09-02
> 状态：已批准待执行
> 范围：只验证 LSAR 的 conditioning 是否有效，不推进论文、不改 diffusion、
>   不引入 Flow Matching、不扩大数据集、不并行多创新点。

## 1. 当前证据基线（confirmed）

1000 stem / 800 train / 200 val / 20 epochs / batch 2 / 10-step sampling：

| condition | 单次 eval | 3 次重复均值 |
| --- | ---: | ---: |
| `none`（官方 LGDM） | 33/200 | 37.00 |
| `plain-y` | 37/200 | 40.00 |
| `lsar`（可学习 scale） | 13/200 | 7 / 13 / 11 |
| `lsar_tuned`（固定 scale=0.05） | 39/200 | 41 / 35 / 39，均值 38.33 |

核心诊断：可学习 `scale` 涨到 0.224，残差过强导致 LSAR 退化；
固定 scale=0.05 后恢复稳定，但与 `plain-y` 接近，尚未证明显著优势。

## 2. 实验目标

回答三个问题：
1. LSAR 在正确残差量级下是否对空间语言 conditioning 有用？
2. affordance 辅助监督是否有贡献？
3. LSAR 是否学到有意义的空间区域（affordance map）？

## 3. 任务拆解

### Task A：固定 scale 扫描

只改 `--lsar-scale`，其余配置完全不变：

- `0.01`
- `0.02`
- `0.05`（已有 `lsar_tuned` 结果，可复用）
- `0.10`

命令模板：

```bash
TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 PYTHONNOUSERSITE=1 \
/home/tbl/miniforge3/envs/grasp-lgd/bin/python \
  research/scripts/train_lgdm_clean.py \
  --stems-tsv research/smoke-data/train_subset_1000.tsv \
  --out outputs/lgdm_scale_sweep/lsar_scale_0.01 \
  --epochs 20 --train-ratio 0.8 --batch-size 2 --eval-steps 10 \
  --log-every 50 --condition-mode lsar \
  --lsar-scale 0.01 --lsar-fixed-scale --lsar-affordance-weight 0.1 \
  --seed 42
```

输出表：

| scale | single correct/200 |
| --- | ---: |
| 0.01 | |
| 0.02 | |
| 0.05 | 39 |
| 0.10 | |

### Task B：Affordance Loss Ablation

用表现最好的 scale，同一架构跑两个变体：

| Model | lambda_aff |
| --- | ---: |
| LSAR-full | 0.1 |
| LSAR-no-aff | 0.0 |

如果 `LSAR-full > LSAR-no-aff`，则 affordance 监督有意义；
如果接近，则监督贡献不明确。

### Task C：Affordance Map 可视化

对验证样本输出：

```text
RGB + affordance heatmap + GT grasp + prediction grasp
```

检查语言指令是否引导 LSAR 高亮目标部位（例如把手而非物体主体/背景）。

### Task D：汇总与决策

汇总 scale sweep + ablation + 可视化，按决策树判断：

- LSAR 明显优于 baseline：冻结方法，进入 final training / 论文材料。
- LSAR ≈ baseline：诚实记录为“空间语言 conditioning 有挑战”，保留 ablation 与可视化。
- LSAR 更差：尝试 LSAR V2（空间门控 `F' = F * (1 + sigmoid(A))`），不立即放弃。

## 4. 不做的事

- 不加 Flow Matching。
- 不改 diffusion。
- 不扩大数据集规模。
- 不加第二个创新点。
- 不推进论文写作。

## 5. 成功标准

至少拿到：
- scale sweep 表（4 个 scale）。
- affordance loss ablation 表（2 行）。
- 若干张 affordance map 可视化图。
- 对 LSAR 是否值得继续给出基于证据的判断。

## 6. 执行结果（2026-09-02）

### Task A：scale sweep 完成

800 train / 200 val / 20 epochs / batch 2 / 10-step sampling，只改固定 scale：

| scale | single correct/200 |
| --- | ---: |
| 0.01 | 43 |
| 0.02 | 38 |
| 0.05 | 39 |
| 0.10 | 31 |

最优 scale=0.01。

### Task B：affordance loss ablation 完成

同一 scale=0.01、同一训练配置，3 次 10-step 采样重复 eval：

| Model | lambda_aff | per-seed | mean |
| --- | ---: | --- | ---: |
| LSAR-full | 0.1 | 45 / 38 / 42 | 41.67 |
| LSAR-no-aff | 0.0 | 21 / 17 / 18 | 18.67 |

结论：affordance supervision 是 LSAR 有效性必要条件；去掉后显著退化。

### Task C：affordance map 可视化完成

输出：

```text
outputs/lgdm_aff_ablation/visuals_affordance/qualitative.png
```

样本包含 spoon handle、apple stem、fork handle 三条语言指令，
summary 中 `affordance_rendered=true`。

### Task D：决策

- 不冻结方法：LSAR-full（mean 41.67）优于官方 baseline（mean 37.00）
  约 4.67/200，但 std 约 3.51，不足以称为显著提升。
- 不进入 LSAR V2：当前问题不是 LSAR 残差过强，而是缺少空间监督；
  scale=0.01 + affordance loss 已形成稳定有效条件。
- 下一步：更大 subset 上训练 Baseline vs Ours，再决定是否作为最终方法。
