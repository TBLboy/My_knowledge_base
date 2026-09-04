# Project Context Briefing 2026-09-03

> 用途：给外部 GPT 做下一阶段决策参考，不是新实验计划。
> 数据截至：2026-09-03，5k subset 的 Baseline vs LSAR 已完成。

## 1. Goal and Exact Question

**Project goal:** Language-driven grasp detection on Grasp-Anything++.
Input is RGB image + natural-language grasping prompt; output is a 2D grasp
rectangle `(x, y, w, h, theta)`. Final deliverables are a GitHub repository
and a 2-page CVPR-style English paper.

**Current phase:** Solution research / method validation. The main method
candidate is `LSAR` (Language-conditioned Spatial Affordance Refinement).

**Question for external GPT:**

1. Given the completed 5k result, should we run another 10k/20k validation,
   or should we stop scaling and move to final training + paper material?
2. If we move to final training: recommend subset size, split, epochs,
   sampling/eval protocol, and what should be reported in a 2-page paper.
3. How should we present `10-step diffusion sampling` honestly versus the
   official 1000-step diffusion process?
4. Is there a statistically defensible way to present the current
   Baseline vs Ours numbers without overclaiming?

## 2. System and Task Background

Confirmed facts:

- Dataset: Grasp-Anything++ annotations aligned with Grasp-Anything RGB.
- Image: `image/<scene>.jpg`, 416x416 RGB.
- Instruction: `grasp_instructions/<scene>_<obj>_<part>.pkl`, a plain string.
- Positive grasp labels: `grasp_label_positive/<scene>_<obj>_<part>.pt`,
  shape `[N,6]`.
- Task is not direct `(x,y,w,h,theta)` regression in the official LGD code;
  the model predicts dense quality / cos / sin / width maps, then decodes to
  grasp rectangles.
- Evaluation uses official `calculate_iou_match`; a grasp is correct when IoU
  with at least one GT is above 0.25 and angle difference is below 30 degrees.
- Current experiments use 10-step respaced cosine diffusion sampling for
  speed, not the full 1000-step schedule.

## 3. Implemented Method Changes

The implementation keeps the official LGDM architecture as the baseline and
adds LSAR only in the language conditioning branch.

Baseline:

- Official `LGDM` network, diffusion-based grasp generation.
- Official upstream code computes the diffusion loss but does not call
  `backward` on it. Our clean training loop uses:
  `total = dense_grasp_loss + diffusion_loss` and back-propagates both.
- Our baseline row is therefore a "cleanly trained official LGDM", not a
  one-to-one copy of the upstream historical training loop.

Proposed method:

- LSAR is inserted between ALBEF language/vision fusion and the GG-CNN
  decoder conditioning point.
- Final hyperparameters: `lsar_scale=0.01`, fixed, and
  `lsar_affordance_weight=0.1`.
- The auxiliary affordance loss supervises a 19x19 spatial map against
  downsampled positive grasp density.
- Removing the LSAR affordance loss previously degraded results sharply.

Code:

- `models/lgdm_lsar.py`
- `research/scripts/train_lgdm_clean.py`
- `research/scripts/eval_lgdm_checkpoint.py`
- `research/scripts/visualize_lgdm_samples.py`

## 4. Expected vs Actual

Expected before the larger subset:

- LSAR should remain at least competitive with the official LGDM baseline.
- If LSAR only wins on 1000 samples, it may be an artifact of small-scale
  tuning.

Actual:

- At 5000 unique scenes, LSAR improves over baseline in a single eval and in
  all three sampling repeats. The trend is consistent with the 1000 and 2968
  sample experiments.

## 5. Reproduction and Evidence

### 1000-sample diagnosis

800 train / 200 val / 20 epochs / 10-step eval.

| Method | single eval | repeat mean |
| --- | ---: | ---: |
| Official LGDM (`none`) | 33/200 | 37.0 |
| Raw y injection (`plain-y`) | 37/200 | 40.0 |
| LSAR fixed scale 0.05 | 39/200 | 38.3 |
| LSAR fixed scale 0.01 + affordance | 43/200 | 41.7 |
| LSAR 0.01 without affordance | 15/200 | 18.7 |

### 2968-sample large subset

2968 stems / 1010 unique scenes / 2374 train / 594 val / 15 epochs.

| Method | single eval | repeat mean | std |
| --- | ---: | ---: | ---: |
| Official LGDM | 151/594 | 152.0 | 5.57 |
| LSAR-full | 185/594 | 179.0 | 1.73 |

### 5000-sample current result

5000 stems / 5000 unique scenes / 4000 train / 1000 val / 15 epochs /
batch 2 / seed 42.

| Method | single eval | repeat seeds /1000 | mean | std |
| --- | ---: | --- | ---: | ---: |
| Official LGDM | 211 | 205, 197, 206 | 202.7 | 4.93 |
| LSAR-full | 299 | 313, 310, 306 | 309.7 | 3.51 |

This is a clear trend but not a final paper claim: only 15 epochs and 10-step
sampling were used, and there is no unseen-scene split yet.

### Visualization

`outputs/lgdm_5k/visuals_affordance/qualitative.png`

Four val samples are rendered with GT + prediction + LSAR affordance overlay:
apple stem, pen cap, highlighter cap, spoon handle. All four render correctly.

## 6. Environment and Constraints

- GPU: RTX 4090 24GB, CUDA available.
- Python env: `grasp-lgd`, `PYTHONNOUSERSITE=1`.
- Local data:
  - 4.4M Grasp-Anything++ instruction/positive pairs are extracted.
  - Local RGB archive has 994,860 available scene JPEGs.
  - 5000 scene JPEGs are currently extracted on demand; no full archive
    decompression was used.
- Measured training time on 5000-sample subset:
  - Baseline: about 20-22 minutes for 15 epochs.
  - LSAR: about 30-36 minutes for 15 epochs.
  - A 10k subset is feasible but roughly doubles that cost.
- Checkpoints are large: baseline about 2.1GB, LSAR about 3.7GB.
- `outputs/` is gitignored; checkpoints are not committed.
- No git remote is configured, so nothing has been pushed yet.

## 7. Attempts and Observed Results

Confirmed sequence:

1. Environment self-contained.
2. Real RGB + instruction + GT pipeline runs end to end.
3. Official diffusion LGDM smoke passes.
4. 100-sample sanity training passes with checkpoint save/load.
5. 1000-sample study selected fixed scale 0.01 + affordance loss.
6. 2968-sample subset confirmed LSAR > baseline.
7. 5000-sample subset confirmed LSAR > baseline in every repeat seed.
8. Current decision from our side: keep LSAR architecture unchanged.

## 8. Unknowns and Requested Help

Remaining unknowns:

- Whether 10k/20k would produce a materially different conclusion.
- Whether the 5000-scene split should be reused as the final train/val split
  or replaced by a larger split.
- Whether 10-step diffusion sampling is acceptable for the paper or whether
  a final eval with more steps is required.
- Whether the submission should include a separate unseen-scene split.
- Whether the reported numbers need statistical testing beyond 3 repeat seeds.
- The official repository's historical instruction encoding semantics remain
  partly unknown; our task definition directly uses the `grasp_instructions`
  string as text input.

Requested output from external GPT:

- A clear recommendation: 10k next vs final training now.
- If final training, a concrete minimal experiment plan that fits the
  remaining time and the 2-page paper budget.
- A recommendation for the paper table and figures that makes the strongest
  honest case for LSAR.
