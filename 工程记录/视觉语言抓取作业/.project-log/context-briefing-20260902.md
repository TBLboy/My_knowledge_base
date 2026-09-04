# Context Briefing - Language-driven Grasp Detection（供外部 GPT 判断用）

> 生成时间：2026-09-02
> 用途：给另一个 AI/协作者提供自包含背景，重点判断“LSAR 这个方法是否值得继续，以及下一步实验最该做什么”。
> 证据状态：已区分 `confirmed` / `assumption` / `unknown`；不虚构未验证内容。

## 1. Goal 与需要你回答的问题

**项目目标（confirmed）**：基于 Grasp-Anything++，完成
`RGB image + language grasping instruction -> 5D grasp rectangle (x,y,w,h,theta)`
的完整 research/engineering 项目，最终交付 GitHub 代码仓库 + 最多 2 页 CVPR-style 英文论文 + 实验证据。
题目不要求 SOTA，要求“idea / coding / writing”完整、可复现、可解释。

**用户当前明确指令（confirmed）**：先不要推进论文，继续做实验。

**需要你回答的核心问题**：
1. 基于下面的证据，`LSAR` 这个 proposed method 是否值得继续投入？
2. 如果继续，下一步最应该做哪个实验：调整 LSAR 残差 scale、去掉/增强 affordance loss、
   换 LSAR 插入位置、加数据/epoch、还是换 conditioning 设计？
3. 如果 LSAR 无法和 baseline 拉开差距，如何把现有结果写成诚实、可辩护的实验和论文？

## 2. 项目背景

### 2.1 任务定义（confirmed）
- 输入：一张 RGB 图像 + 一条自然语言抓取指令。
- 输出：2D 矩形 grasp，参数化 `(x,y,w,h,theta)`。
- 同一个图可因语言指令不同而指向不同目标/部位，语言不是辅助标签而是决定目标的关键输入。

### 2.2 使用的基线（confirmed）
- 官方 baseline 固定为 **LGDM（diffusion 版）**，不是 `lgrconvnet3`。
- LGDM 输出不是直接回归 5 参数，而是生成 dense maps：
  `pos / cos / sin / width`（全分辨率 224x224 输出），
  再经 `post_process_output` -> `detect_grasps` -> `(x,y,w,h,theta)`。
- 评估协议：预测 grasp 与任一 GT rectangle 的 IoU > 0.25 且 angle 差 < 30° 判为 correct。

### 2.3 数据集（confirmed 的范围）
- 使用 Grasp-Anything++ 的真实样本：`grasp_instructions/<stem>.pkl`（纯字符串）、
  `grasp_label_positive/<stem>.pt`（`[N,6]` 的正样本 grasp）。
- RGB 来自 Grasp-Anything 的 `<scene>.jpg`，++ 本身不含图像。
- 当前实验只用子集，没有下载完整 87 GB。

## 3. 对网络做了哪些改动（confirmed，代码在仓库中）

**官方问题（confirmed）**
- 官方 `train_network_diffusion.py` 计算了 diffusion loss，但 `backward` 被注释，
  实际只更新 dense-map loss。
- 官方 `LGDM.forward` 里 ALBEF 的 `y` 分支有“注入视觉特征”的代码但被注释，
  所以官方语言分支实际上没有梯度。
- `image_atts` 实测为全 1 mask，不是语言注意力图。

**我们的改动（confirmed）**
文件：[models/lgdm_lsar.py](/home/tbl/Project/视觉语言抓取作业/models/lgdm_lsar.py)

1. 新增 `LGDMWithConditioning`，继承官方 `LGDM`，不改 `LGD-main/` 源码。
2. 把 ALBEF 输出 `y` 转成 `y_view (8,19,19)`，接入 GG-CNN 的 `conv3` 输出位置。
3. 提供三种可复现 conditioning 模式：
   - `none`：官方 LGDM，不注入 `y`。
   - `plain-y`：直接 `img = ReLU(img + y_view)`。
   - `lsar`：先经过 `SpatialAffordanceRefinement` 再注入。
4. 新增 `SpatialAffordanceRefinement`：
   - 输入 = concat(conv3 视觉特征, y_view)，shape 均为 `(8,19,19)`。
   - 结构：`Conv3x3(16) + GroupNorm + ReLU -> Conv3x3(16) + ReLU -> proj Conv1x1(8)`。
   - 输出 `residual = scale * proj(hidden)`，再 `img = ReLU(img + residual)`。
5. 新增辅助头 `aff_head`，输出 `affordance_map (B,1,19,19)`，用来做辅助空间监督。
6. `scale` 默认可学习（初始 0.1）；新增 `--lsar-scale` 和 `--lsar-fixed-scale`
   以支持固定 scale。

**训练目标改动（confirmed）**
文件：[research/scripts/train_lgdm_clean.py](/home/tbl/Project/视觉语言抓取作业/research/scripts/train_lgdm_clean.py)

```text
total = diffusion_mse + 1e-3 * diffusion_contrastive
      + MSE(cos) + MSE(sin) + MSE(width)
      + lambda_aff * MSE(affordance_map, adaptive_avg_pool2d(pos_gt, 19))
total.backward()
```

这修正了官方“diffusion loss 不回传”的问题，并可选加 affordance 辅助 loss。

## 4. 预期 vs 实际

### 预期
- `plain-y` / `lsar` 应比 `none` 好，证明语言条件注入有效。
- LSAR 通过空间精修应该比直接注入 `y` 更稳/更好。

### 实际（confirmed，见第 6 节）
- `plain-y` 并没有稳定超过 `none`（重复评估均值 40.0 vs 37.0，很接近）。
- 可学习 `scale` 的 LSAR 明显退化（13/200）。
- 固定 `scale=0.05` 的 `lsar_tuned` 恢复稳定（重复均值 38.33），
  略高于 `none`，但低于/接近 `plain-y`，统计上无法确认显著优势。

## 5. Reproduction 与 Evidence 位置

### 子集与数据
- 1000 stem 清单：`research/smoke-data/train_subset_1000.tsv`
- RGB 提取目录：`/mnt/data/grasp-anything-lgd/data/processed/grasp-anything/images`
- instruction：`/mnt/data/grasp-anything-lgd/data/processed/grasp-anything-pp/grasp_instructions/grasp_instructions`
- positive：`/mnt/data/grasp-anything-lgd/data/processed/grasp-anything-pp/grasp_label_positive/grasp_label_positive`

### 实验输出（`outputs/` 被 .gitignore，仅本机）
- `outputs/lgdm_exp1000/none/`
- `outputs/lgdm_exp1000/plain_y/`
- `outputs/lgdm_exp1000/lsar/`
- `outputs/lgdm_exp1000/lsar_tuned/`
- 每个目录含 `args.json`、`training_log.jsonl`、`last.pt`、`eval_metrics.json`。
- 重复评估：
  - `outputs/lgdm_exp1000/none_repeat_eval/`
  - `outputs/lgdm_exp1000/plain_y_repeat_eval/`
  - `outputs/lgdm_exp1000/lsar_repeat_eval/`
  - `outputs/lgdm_exp1000/lsar_tuned_repeat_eval/`

### 关键脚本
- 训练：[train_lgdm_clean.py](/home/tbl/Project/视觉语言抓取作业/research/scripts/train_lgdm_clean.py)
- 重复评估：[eval_lgdm_checkpoint.py](/home/tbl/Project/视觉语言抓取作业/research/scripts/eval_lgdm_checkpoint.py)
- 汇总：[summarize_experiments.py](/home/tbl/Project/视觉语言抓取作业/research/scripts/summarize_experiments.py)
- 可视化：[visualize_lgdm_samples.py](/home/tbl/Project/视觉语言抓取作业/research/scripts/visualize_lgdm_samples.py)
- 定性图：`research/assets/qualitative_lsar_tuned.png`

### 复现命令（confirmed 可用）
已在根目录 [README.md](/home/tbl/Project/视觉语言抓取作业/README.md) 记录，
包括 prepare subset / extract RGB / train / repeat eval / visualize / summarize。

## 6. Attempts 与 Observed Results

### 6.1 阶段 0：工程 smoke（confirmed）
- 10 个不同 scene 真实样本，`dataset -> dense maps -> forward -> loss -> backward ->
  post-process -> IoU eval` 全链路 `10/10 OK`。

### 6.2 100-sample sanity（confirmed）
- 80 train / 20 val / 20 epochs，Clean LGDM `5/20 correct`。
- 证明 checkpoint 可保存、可 `--resume`、评估可跑。

### 6.3 1000-sample 正式实验（confirmed）
800 train / 200 val / 20 epochs / batch 2 / 10-step diffusion sampling：

| condition | 单次 eval | 3 次采样重复均值 |
| --- | ---: | ---: |
| `none`（官方 LGDM） | 33/200 | 37.00 |
| `plain-y` | 37/200 | 40.00 |
| `lsar`（可学习 scale） | 13/200 | 7 / 13 / 11 |
| `lsar_tuned`（固定 scale=0.05） | 39/200 | 41 / 35 / 39，均值 38.33 |

### 6.4 关键诊断（confirmed）
- `lsar.scale` 训练后涨到 **0.224**，残差注入过强导致退化。
- 固定 scale=0.05 后稳定性恢复。
- 重复评估用同一 checkpoint 不同 RNG seed 跑 3 次，`lsar` 仍为 7/13/11，
  说明不是单次采样噪声。
- `none` 重复 42/33/36，`plain-y` 重复 38/43/39，
  `lsar_tuned` 重复 41/35/39，三者在 600 次采样评估上非常接近。

### 6.5 定性图（confirmed）
- 6 个验证样本，绿色=GT，红色=预测。
- 多数样本预测并不准确，只有 1 个 correct，这与 39/200 的低准确率一致。

## 7. Environment、依赖与约束

### 环境（confirmed）
- GPU：NVIDIA GeForce RTX 4090（24 GiB）。
- Python：miniforge conda env `grasp-lgd`，Python 3.10。
- 所有关键命令带 `PYTHONNOUSERSITE=1`，避免 `~/.local` 干扰。
- 训练/评估命令带 `TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1`，
  因为 BERT 离线加载会访问 huggingface.co 导致超时。
- LGDM 约 573.6M 参数，trainable 约 213.1M。
- 1000 样本 20 epochs 单条件训练约 10-12 分钟；一次 200 样本 10-step 评估约 1-2 分钟。

### 依赖（confirmed 存在）
- `env/requirements-project.txt`：numpy/scipy/pillow/matplotlib/opencv/scikit-image/
  openai-clip/transformers==4.28.1/timm==0.6.13/ruamel.yaml/tensorboardX/torchsummary。
- torch/torchvision 单独按 CUDA wheel 安装。

### 用户/项目约束（confirmed）
- 不做完整 87 GB 数据下载。
- 不重写 diffusion，不改评估协议。
- baseline 固定为 diffusion 版 LGDM，不回到 `lgrconvnet3`。
- 论文暂不推进，继续做实验。
- 只允许一个清晰的原创新点，不并行多个创新点。

## 8. Unknown / To Verify

- 官方指令语义：`.pkl` 里的字符串是否就是应该直接 encode 的 query，
  还是官方训练内部用的是 scene description / object query，尚未完全确认。
  （我们当前实现按 assignment 定义直接 encode `grasp_instruction`。）
- 全数据集 100% stem 对齐是否成立：只验证了 1000 个子集，未验证全量 zip。
- 官方 diffusion 的完整 1000-step sampling 结果：我们只用了 10-step respaced。
- `plain-y` 与 `none` 的差异是否来自语言注入还是评估随机性，尚未定论。
- 20 epochs / 1000 样本是否足够 LSAR 收敛，尚未验证。
- 固定 scale=0.05 是经验选择，不是来自理论或搜索。

## 9. 请外部 GPT 给出的建议

请基于以上证据回答：
1. LSAR 是否值得继续，还是应换一个更可控的 language conditioning 设计？
2. 若要继续，下一组实验最优先做什么（给 1-3 个具体、可复现的实验）？
3. 若要证明“language 真正进入网络并起作用”，当前证据链是否足够？
4. 如果最终结果就是“baseline 与我们的方法几乎持平”，怎么把它写成一个
   诚实、可辩护的 ablation/paper 而不造假？
