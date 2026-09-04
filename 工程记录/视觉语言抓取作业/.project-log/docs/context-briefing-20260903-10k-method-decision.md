# Context Briefing: 10k Validation and Final Method Decision

> 生成时间：2026-09-03
> 用途：交给外部 GPT 判断下一步，不替代继续实施。

## 1. Goal and Exact Question

项目目标：基于 Grasp-Anything++，完成
`RGB image + language instruction -> 2D grasp rectangle (x, y, w, h, theta)`
的完整研究工程，最终交付 GitHub 仓库和最多 2 页 CVPR 风格英文论文。
当前已完成 10k scene-disjoint subset 的 Baseline / LSAR-full / LSAR-no-aff
三模型训练、3 次 repeat eval、10/50-step sensitivity 和 paired
qualitative visualization。

需要外部 GPT 判断的问题：

1. 10k 结果显示显式 affordance loss（`lambda_aff=0.1`）反而弱于
   `lambda_aff=0`，并且与 1000-sample 阶段的结论相反。是否应把
   LSAR-no-aff 固定为最终方法并进入论文？
2. 如果不直接固定，还有哪些低风险、可解释的补充实验最有价值？
3. 对这组结果，论文里最诚实、最有说服力的 Method / Ablation 讲述方式
   应该是什么？

## 2. Relevant System and Project Background

- Baseline 是官方 `LGDM` diffusion-based grasp detection。
- 官方训练代码计算了 diffusion loss，但没有对它调用 `backward`；
  本仓库的 `train_lgdm_clean.py` 修复为 diffusion loss 和 dense loss
  共同参与训练，作为干净 baseline。
- Proposed method 是 `LSAR`：
  `Language-conditioned Spatial Affordance Refinement`。
- LSAR 插入位置：ALBEF 的 `y` 分支和 GG-CNN `conv3` 之间。
- LSAR 实际结构：

```text
input = concat(visual_conv3_feature, ALBEF y_view)
hidden = ReLU(Conv3x3(GroupNorm(ReLU(Conv3x3(input)))))
residual = scale * Conv1x1(hidden)
F' = ReLU(F_conv3 + residual)
affordance_map = aff_head(hidden)  # (B, 1, 19, 19)
```

- `scale=0.01` 固定，不学习。
- LSAR-full 额外使用
  `lambda_aff * MSE(affordance_map, adaptive_avg_pool2d(pos_gt, 19))`，
  其中 `lambda_aff=0.1`。
- LSAR-no-aff 只保留 LSAR 残差注入，`lambda_aff=0.0`。
- 评估协议：每个 sample 做 10-step diffusion sampling，使用官方
  `calculate_iou_match(..., threshold=0.25)` 判断 correct。

## 3. Expected versus Actual Behavior

### Expected

在 1000-sample 实验中，LSAR + affordance loss 明显优于 LSAR-no-aff：

- LSAR-full repeat mean：41.67/200
- LSAR-no-aff repeat mean：18.67/200

因此之前的判断是：affordance 空间监督对 LSAR 必要，最终方法固定为
LSAR-full。

### Actual

10k 结果反转：

- LGDM baseline：mean 470.0/2000
- LSAR-full：mean 605.3/2000
- LSAR-no-aff：mean 653.7/2000

即 LSAR 残差注入本身仍然有效，但额外加入 `lambda_aff=0.1` 的显式
affordance MSE 在 10k 上降低了性能。

## 4. Reproduction and Exact Evidence

### Data

- `research/smoke-data/train_subset_10k.tsv`
- 10000 stems / 10000 unique scenes
- split：8000 train / 2000 val，seed 42
- 因每个 stem 是一个 unique scene，sample split 自动是
  scene-disjoint split。
- RGB：Grasp-Anything `<scene>.jpg`，10000/10000 存在。

### Training Command

统一配置：

```bash
research/scripts/train_lgdm_clean.py \
  --stems-tsv research/smoke-data/train_subset_10k.tsv \
  --epochs 15 --train-ratio 0.8 --batch-size 2 \
  --eval-steps 10 --log-every 200 --seed 42
```

三模型仅 condition/loss 不同：

```text
LGDM        : --condition-mode none
LSAR-full   : --condition-mode lsar --lsar-scale 0.01 --lsar-fixed-scale \
              --lsar-affordance-weight 0.1
LSAR-no-aff : --condition-mode lsar --lsar-scale 0.01 --lsar-fixed-scale \
              --lsar-affordance-weight 0.0
```

### Repeated Evaluation

每个 checkpoint 使用 3 次 10-step sampling，seed 100/101/102。

| Method | Seeds | Mean /2000 | Std |
| --- | --- | ---: | ---: |
| LGDM baseline | 473, 479, 458 | 470.0 | 10.82 |
| LSAR-full | 601, 626, 589 | 605.3 | 18.88 |
| LSAR-no-aff | 647, 660, 654 | 653.7 | 6.51 |

单次训练 loop eval：

| Method | Single Eval /2000 |
| --- | ---: |
| LGDM baseline | 449 |
| LSAR-full | 625 |
| LSAR-no-aff | 643 |

### Sampling-Step Sensitivity

固定 200-sample validation subset，`subsample_seed=7`，sampling seed 200。

| Method | 10 steps | 50 steps |
| --- | ---: | ---: |
| LGDM baseline | 39 | 44 |
| LSAR-full | 55 | 61 |
| LSAR-no-aff | 57 | 65 |

### Qualitative Visualization

- `outputs/lgdm_10k/paired_visuals/paired_qualitative.png`
- `outputs/lgdm_10k/paired_visuals_no_aff/paired_qualitative.png`
- 已复制供仓库使用：
  `research/assets/qualitative_10k_paired_lsar_no_aff.png`

### Results File

- `research/results/10k_validation_summary.md`
- `outputs/lgdm_10k/{none,lsar_full,lsar_no_aff}/repeated_eval.json`
- `outputs/lgdm_10k/sensitivity/*.json`

## 5. Environment, Dependencies, Interfaces, and Constraints

- Conda env：`grasp-lgd`
- GPU：NVIDIA GeForce RTX 4090，24 GiB
- Python 命令统一使用：

```bash
PYTHONNOUSERSITE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 \
/home/tbl/miniforge3/envs/grasp-lgd/bin/python ...
```

- 数据路径：

```text
instructions: /mnt/data/grasp-anything-lgd/data/processed/grasp-anything-pp/grasp_instructions/grasp_instructions
positive:     /mnt/data/grasp-anything-lgd/data/processed/grasp-anything-pp/grasp_label_positive/grasp_label_positive
images:       /mnt/data/grasp-anything-lgd/data/processed/grasp-anything/images
```

- 当前 Git 干净，最新提交：
  `15a5d18 feat: finalize 10k three-model results and LSAR-no-aff selection`
- 没有配置 GitHub remote，当前未 push。

## 6. Attempts and Observed Results

### Previous Scales

| Scale | LGDM baseline | LSAR-full | LSAR-no-aff |
| --- | ---: | ---: | ---: |
| 1000 samples | 37.0/200 | 41.67/200 | 18.67/200 |
| 2968 stems | 152.0/594 | 179.0/594 | not trained |
| 5000 stems | 202.7/1000 | 309.7/1000 | not trained |
| 10000 stems | 470.0/2000 | 605.3/2000 | 653.7/2000 |

需要注意：10k subset 与 5k subset 有约 5000 个 scene 重叠，10k 是规模
扩展验证，不是完全独立的第二组数据。

### What Was Changed This Round

- 没有改变 LSAR 网络结构。
- 没有改变 diffusion backbone。
- 只对比是否加入 affordance auxiliary loss。
- 已加入 `--max-samples` / `--subsample-seed` 支持，方便做
  sampling sensitivity subset。
- 已新增 `visualize_lgdm_paired.py`，生成 Baseline vs LSAR 的 paired
  qualitative figure。

### Incidents

- 曾有两个进程写同一 `lsar_full` 输出目录，已停止后启动的 resume 进程，
  保留原 seed 42 训练进程直至完成。
- 最终 `lsar_full` 的 checkpoint 和 eval 输出已验证有效。

## 7. Unknowns and Requested Help

### Confirmed

- 10k 三个配置、训练配置、repeat eval 和 sensitivity 结果已确认。
- LSAR-no-aff repeat mean 高于 LSAR-full 和 LGDM baseline。
- 10/50-step sensitivity 保持同样排序。
- scale=0.01 固定、lambda_aff 是唯一对照变量。

### Assumptions

- 3 次 repeat eval 只覆盖 diffusion sampling 随机性，不覆盖不同训练
  seed 的模型初始化随机性。
- 10k 结果足以作为当前阶段的方法选择依据，但不等同于全数据集结果。

### Unknown

- 为什么 1000-sample 中 no-aff 明显退化，而 10k 中 no-aff 反而最好。
- 是否 LSAR 的 `aff_head` / affordance MSE 在与 diffusion loss 联合训练时
  产生冲突，或只是小规模上优化不稳定。
- 当前没有第二组训练 seed 的三模型重复训练，无法评估训练随机性影响。
- 未跑 full 1000-step sampling。
- 未跑 LSAR-no-aff 的 2968/5000 两个规模对照，无法判断从多少规模开始
  发生反转。
- 未采用更大数据量或不同 `lambda_aff` 扫描。

### Requested Help

请基于以上证据给出一个可执行判断：

1. 是否固定 LSAR-no-aff 为最终方法？
2. 如果要补实验，补什么最划算且不影响 2 页论文截止？
3. 论文的 Method / Ablation 应如何写，才能让
   `1000-scale no-aff 差` 与 `10k-scale no-aff 好` 的反差不成为明显
   审稿风险？
