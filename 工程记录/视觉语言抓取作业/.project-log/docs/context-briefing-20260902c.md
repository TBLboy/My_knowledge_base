# Language-Driven Grasp Detection 项目简报（2026-09-02）

## 1. Goal & Exact Question

- **项目总目标**：基于 Grasp-Anything++ 实现图像 + 自然语言指令 → 5 参数抓取矩形
  `(x, y, w, h, theta)` 的可训练、可评估、可提交流水线，并交付 GitHub 仓库和
  2 页 CVPR 风格英文论文。
- **当前阶段**：solution-research；阶段 0 与阶段 1 已落地，尚未开始训练。
- **请你回答的问题**：
  1. 官方 `train_network_diffusion.py` 只对 dense-map loss 做 backward，diffusion
     loss 的 backward 是注释掉的。下一步应封装一个真正训练 diffusion objective
     的训练入口，还是先沿用官方 dense-map 更新跑通训练？
  2. LSAR 的插入点和监督目标应如何定义，才能与官方 `LGDM` conditioning 分支区分？
  3. 在 RTX 4090 24GB 上，100 sample 训练 sanity 的 batch size、epochs、单卡显存
     与预计时间应如何设计？

## 2. System & Project Background

- 仓库：`/home/tbl/Project/视觉语言抓取作业`，个人仓库，分支 `main`。
- 所有工作统一在 `grasp-lgd` env 中；`PYTHONNOUSERSITE=1` 已持久化。
- 官方 baseline 代码快照：根目录 `LGD-main/`。
- Proposed Method 已初定为 **LSAR（Language-conditioned Spatial Affordance
  Refinement）**，保存在
  [proposed-method-LSAR.md](/home/tbl/Project/视觉语言抓取作业/.project-log/docs/proposed-method-LSAR.md)。
- `DEC-009` 已确定：后续基线必须是 diffusion 版 `LGDM`，不是 `lgrconvnet3`。

当前主要 pipeline：

```text
RGB image 224x224 + grasp_instruction string
  -> positive [N,6] -> dense pos/cos/sin/width maps
  -> LGDM (ALBEF vision-text fusion + GG-CNN-like grasp head)
  -> GaussianDiffusion (cosine, official 1000 steps)
  -> pos/cos/sin/width
  -> post_process_output -> detect_grasps -> IoU evaluation
```

## 3. Expected vs Actual Behavior

| 维度 | 期望 | 实际 |
| --- | --- | --- |
| 环境 | `grasp-lgd` 独立、CUDA 可用 | 已确认：Python 3.10，torch 2.13.0+cu130，RTX 4090 |
| 阶段 0 | 10 个不同 scene 真 RGB 跑通工程链路 | `10/10 OK, 0 SKIP-RGB, 0 FAIL` |
| 阶段 1 | 官方 diffusion 版 LGDM 能跑通 | 2 个真实 stem `2/2 OK, 0 FAIL` |
| 官方训练代码 | 应训练 diffusion 目标 | `train_network_diffusion.py` 第 242-244 行把 diffusion loss backward 注释掉，只向后更新 dense-map loss |
| 官方 README | 命令可复现 | README 的 `--network lgd` 未注册；实际注册名是 `lgdm` |

## 4. Reproduction & Exact Evidence

Diffusion smoke 命令：

```bash
HF_ENDPOINT=https://hf-mirror.com \
PYTHONNOUSERSITE=1 \
/home/tbl/miniforge3/envs/grasp-lgd/bin/python \
  research/scripts/diffusion_smoke.py \
  --max-stems 2 --sample-steps 10 \
  --out outputs/diffusion_smoke_2
```

结果（来自
`outputs/diffusion_smoke_2/metrics.json`）：

- device：CUDA
- official diffusion steps：1000
- smoke sampling steps：10（respaced cosine）
- stem 1：`Take fork by its handle.`，GT 14 rectangles
- stem 2：`Pick up note by its writing.`，GT 8 rectangles
- sample shape：`(1,1,224,224)`，sample finite：true
- backward grad finite：true；`grad_nonfinite_count=0`
- 未训练模型 `correct=false`，**不是失败**，预期如此
- 峰值 GPU：约 `2.51 GiB`

阶段 0 证据：

- `outputs/batch_smoke/summary.txt`：`total: 10, ok: 10, skip_rgb: 0, fail: 0`
- loss 范围约 `0.70 - 1.62`；1 条 `correct=True`，其余 False（随机初始化）

项目日志证据：

- `EV-20260828-env-self-contained`
- `EV-20260902-batch-smoke`
- `EV-20260902-diffusion-smoke`
- 证据摘要在 `.project-log/verification/` 下。

## 5. Environment, Dependencies, Interfaces, Constraints

- conda env：`grasp-lgd`
- Python：3.10.21
- torch：2.13.0+cu130；CUDA 可用；GPU：RTX 4090 24GB
- 新增 diffusion 依赖：`transformers==4.28.1`、`timm==0.6.13`、
  `ruamel.yaml==0.17.21`、`tensorboardX`、`torchsummary`
- BERT：`bert-base-uncased` 已下载到本机 HF 缓存；CLIP `ViT-B-32.pt` 已有
- 外网：huggingface.co 不可直连；使用 `HF_ENDPOINT=https://hf-mirror.com`
- 数据：只本地保存了少量真实样本和 10 张 scene jpg，不依赖完整 87 GB 数据
- 约束：不改官方模型/评估链路；不下载全量数据；LSAR 原则上只改 conditioning 分支

## 6. Attempts & Observed Results

已完成的尝试：

1. 环境 self-contained：通过。
2. 10 stem 真 RGB batch smoke：通过。
3. `LGDM(input_channels=3)` 实例化：通过，约 573.6M 参数。
4. 真实 instruction 直接作为文本 query：通过。
5. `training_losses` / dense-map loss / backward / 10-step `p_sample_loop` /
   post-process / IoU evaluation：2/2 通过。
6. `train_network_diffusion.py` 和 `evaluate_diffusion.py` import：通过。
7. `get_network('lgdm')`：通过；`get_network('lgd')`：失败。

关键观察：

- 官方 diffusion training loss 被计算但未反向传播，导致“diffusion baseline”的
  正式训练语义仍不明确。
- `grad_missing_trainable_count=418`，主要是 ALBEF 中未参与 forward 的辅助头，
  例如 `itm_head`；实际参与路径的梯度均 finite。

## 7. Unknowns / Need Help

- **need help**：是否修正/封装官方训练代码，使 diffusion loss 参与 backward；
  若修正，如何与“复用官方 baseline”的边界写清楚。
- **need help**：LSAR 应接在 `full_image_atts`、`guiding_point` 还是
  `pos_output_str`，以及训练监督是 dense pos map、part mask 还是自定义 affordance
  target。
- **need help**：100 sample training sanity 的规模、batch size、epochs、
  optimizer、预计时间和显存策略。
- **unknown**：官方 `grasp_instructions/<stem>.pkl` 与官方训练中
  `queries[obj_id]` 的语义关系仍未确认。
- **unknown**：完整 1000 步 sampling 的性能尚未测量。
- **unknown**：当前只解压了 10 张 scene jpg；训练前需要决定是否展开更大的 RGB
  subset。

---
**写作目的**：供外部 AI 判断下一步，重点回答“diffusion 训练入口”和“LSAR 插入点”，
不要重复已完成事实。
