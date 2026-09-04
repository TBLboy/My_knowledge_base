# Context Briefing 2026-09-04: Final Delivery State

> 用途：给另一个 AI、协作者或评审人提供自包含的项目背景，用于判断当前
> 是否已满足提交条件，以及“用户提供姓名后”的最后几步应该怎么做。

## 1. Goal and Exact Question

**Goal**

完成一个基于 Grasp-Anything++ 的 Language-driven Grasp Detection 项目：

- 输入：RGB image + natural-language grasping instruction
- 输出：2D grasp rectangle \((x,y,w,h,\theta)\)
- 交付：GitHub 代码仓库 + 不超过 2 页的 CVPR-style 英文论文
- 最终 PDF 文件名必须为 `FirstName_LastName.pdf`

**Exact question for the reader**

基于当前证据，除“论文作者姓名 / 最终命名 PDF”外，是否还存在任何必须
修复、补做或重新验证的事项？如果用户提供 first/last name，最后交付应如何
按顺序完成并验证？

## 2. Project and System Background

**Dataset**

- Grasp-Anything++
- 实验使用 10,000 stems / 10,000 unique scenes
- RGB source: Grasp-Anything `<scene>.jpg`
- Ground truth: positive grasp files, format `[N, 6]`
- Task representation: dense maps `pos`, `cos(2theta)`, `sin(2theta)`, normalized width

**Baseline**

- Official diffusion-based LGDM
- Clean baseline restores diffusion loss backward; upstream code computes
  diffusion loss but does not optimize it
- Evaluation unchanged: prediction matches any GT with IoU `> 0.25` and
  angle error `< 30°`

**Proposed method**

- `LGDM + LSAR` (Language-conditioned Spatial Affordance Refinement)
- Input: decoder visual feature + ALBEF `y_view`
- LSAR residual is injected before GG-CNN decoding
- Residual scale fixed to `0.01`
- Final auxiliary affordance loss weight: `lambda_aff = 0.05`
- Two training seeds: `seed=42, split-seed=42` and `seed=43, split-seed=42`

## 3. Expected vs Actual

**Expected**

- All engineering stages run: dataset -> train -> checkpoint -> evaluate ->
  inference -> visualization
- Paper compiles in English within 2 pages
- GitHub repo is public and reproducible
- Final PDF named `FirstName_LastName.pdf`

**Actual**

- Engineering and experiments are complete
- Paper source and compiled PDF exist
- Paper is exactly 2 pages
- GitHub repo is public and reachable
- Top-level `train.py`, `evaluate.py`, and `inference.py` exist
- Final `FirstName_LastName.pdf` does not exist
- `main.tex` author line still contains placeholder `FirstName LastName`

## 4. Reproduction and Exact Evidence

**Environment**

```bash
PYTHONNOUSERSITE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 \
/home/tbl/miniforge3/envs/grasp-lgd/bin/python ...
```

Data paths used by checkpoints/config:

```text
/mnt/data/grasp-anything-lgd/data/processed/grasp-anything-pp/grasp_instructions/grasp_instructions
/mnt/data/grasp-anything-lgd/data/processed/grasp-anything-pp/grasp_label_positive/grasp_label_positive
/mnt/data/grasp-anything-lgd/data/processed/grasp-anything/images
```

**Top-level commands**

```bash
PYTHONNOUSERSITE=1 python train.py --help
PYTHONNOUSERSITE=1 python evaluate.py --help
PYTHONNOUSERSITE=1 python inference.py --help
```

Verified in clean release tree: all return 0, `compileall` passes.

**Paper**

- Source: `research/paper/main.tex`
- Compiled PDF: `research/paper/main.pdf`
- `pdfinfo research/paper/main.pdf` reports `Pages: 2`
- Required sections confirmed: Abstract, Introduction, Related Work, Method,
  Experiments, Conclusion, References

**GitHub**

- Repository: `https://github.com/TBLboy/language-driven-grasp-detection`
- Visibility: PUBLIC
- Latest published commit: `4fd824d`
- Raw `README.md`, raw `main.pdf`, raw `main.tex` all return HTTP 200
- Clean published tree contains 201 files, does not include `outputs/`,
  checkpoints, large model weights, or temporary experiment data

## 5. Experimental Results

**Training**

- 10k stems / 10k unique scenes
- 8,000 train / 2,000 validation, seed 42
- Scene-disjoint by construction
- 15 epochs, batch size 2, learning rate `1e-3`, weight decay `1e-4`
- Evaluation uses 10-step respaced diffusion sampling

**Main table**

| Method | `lambda_aff` | Single eval /2000 | Repeat mean /2000 |
|---|---:|---:|---:|
| LGDM baseline | --- | 449 | `470.0 +/- 10.8` |
| LSAR-no-aff | 0.0 | 643 | `653.7 +/- 6.5` |
| LSAR-full | 0.1 | 625 | `605.3 +/- 18.9` |
| LSAR final seed42 | 0.05 | 686 | `678.0 +/- 16.5` |
| LSAR final seed43 | 0.05 | 666 | `661.7 +/- 14.0` |

Conclusion: LSAR improves the baseline mean from `470.0` to `678.0` /
`661.7` across two training seeds.

**Sampling-step sensitivity (fixed 200 validation subset)**

| Method | 10 steps | 50 steps |
|---|---:|---:|
| LGDM baseline | 39 | 44 |
| LSAR-full | 55 | 61 |
| LSAR-no-aff | 57 | 65 |
| LSAR final | 65 | 67 |

**Qualitative evidence**

- `research/assets/qualitative_10k_paired_lsar_0.05.png`
- Six validation samples: pen, highlighter, marker cap, duck bill,
  apple stem, keychain keys

## 6. Attempts and Observed Results

- Official LGD smoke chain passed with real data
- Clean LGDM diffusion baseline passed on real stems
- 1000 / 2968 / 5000 subset experiments informed final scaling
- 10k final experiment completed
- `lambda_aff` sweep completed: `0.0`, `0.01`, `0.05`, `0.1`
- Final method uses `0.05`
- Two training seeds completed
- Repeated evaluation and diffusion-step sensitivity completed
- Paper compiled and GitHub published
- Top-level entrypoints added after the first publication and pushed as
  `4fd824d`

## 7. Unknowns and Requested Help

**Unknown / blocked**

- User's real First Name / Last Name is not available
- Final named PDF cannot be generated without this input
- Final `main.tex` author line remains a placeholder

**Known but intentionally out of current scope**

- Not full-scale Grasp-Anything++ training
- Not full 1000-step diffusion evaluation
- Not real-robot validation
- These are documented limitations in the paper, not blockers

**Requested help**

请判断：

1. 除作者姓名和命名 PDF 外，是否还有任何必须补做的失败项？
2. 用户提供姓名后，完成顺序是否应为：
   replace author -> recompile -> create `FirstName_LastName.pdf` ->
   push GitHub -> update delivery audit?
3. 是否建议在收到姓名前做任何额外验证或文档调整？
