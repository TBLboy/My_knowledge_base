# Gradient Accumulation Experiment 2026-09-04

## Purpose

Evaluate whether gradient accumulation changes LGDM + LSAR training stability and
final 10k validation performance.

This is an exploratory training-recipe experiment. It is not a paper method claim
until we decide to retrain the final table under one shared recipe.

## Backup

- Local tag: `backup-final-before-grad-accum` at `44de537`
- GitHub release tag: `backup-final-before-grad-accum` on
  `TBLboy/language-driven-grasp-detection`
- Gradient accumulation code committed as `69234cb`

## Smoke Test

Command used 1000 stems, batch 2, accum 4, 9 micro-batches, no final eval.

Verified:

- backward works with scaled loss
- optimizer updates once per 4 micro-batches
- final partial accumulation period is flushed
- checkpoint and `args.json` save `grad_accum_steps=4`

## Real Run

Fixed recipe:

```text
10k stems, 8000 train / 2000 val
batch size 2
grad accum steps 4
15 epochs
lr 1e-3
weight decay 1e-4
grad clip 1.0
eval steps 10
condition-mode lsar
lsar-scale 0.01
lsar-fixed-scale
lsar-affordance-weight 0.05
seed 42
split-seed 42
```

Output:

```text
outputs/lgdm_10k/grad_accum_4/lsar_final/last.pt
```

Baseline comparison:

| Recipe | Repeat mean /2000 |
|---|---:|
| Current LSAR seed42 | 678.0 ± 16.5 |
| Grad accum 4 LSAR seed42 | 655.3 ± 17.2 |

## Result

Grad-accum training completed with 15 epochs / 10k stems. The built-in single
eval was `642/2000`. Three-repeat eval:

| Repeat | Correct /2000 |
|---|---:|
| seed 100 | 637 |
| seed 101 | 658 |
| seed 102 | 671 |

Mean: `655.3`, sample std: `17.2`.

Compared with the current final seed42 LSAR (`678.0 ± 16.5`), grad accum 4 is
about `22.7` points lower on mean correct with a similar repeat std. The run
does not provide evidence that gradient accumulation improves training quality.

## Conclusion

Keep the current paper results unchanged. Report this run as an exploratory
training-stability experiment. If we ever need a same-update-count comparison,
the fair setting would require 60 epochs with accum 4 and retraining both the
LGDM baseline and LSAR under that recipe.

## Fairness Note

Gradient accumulation changes optimizer update frequency. At 15 epochs:

- current recipe: 60,000 optimizer updates
- accum 4 recipe: 15,000 optimizer updates

This comparison therefore tests the recipe as usually used in model training,
not an equal-update-count ablation. If the grad-accum result enters the paper main
table, both LGDM baseline and LSAR must be retrained with the same recipe.

## Decision Rule

- If grad accum clearly improves mean or reduces repeat variance, record it as a
  training-stability result and discuss whether to retrain the main table.
- If it is close or worse, keep the current paper results unchanged and report
  this run as an exploratory stability experiment.
