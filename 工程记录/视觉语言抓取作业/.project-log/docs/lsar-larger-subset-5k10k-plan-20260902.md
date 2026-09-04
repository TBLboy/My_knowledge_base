# Larger-Subset LSAR Validation Plan (5k/10k)

> 记录时间：2026-09-02
> 状态：已由用户确认继续推进，待执行
> 上一阶段：3k subset（2968 stems / 1010 scenes）完成，
>   LSAR-full repeat mean 179.0/594 vs baseline 152.0/594，
>   Stage E 结论为保留当前 LSAR。

## 1. 目标

在更大但仍是 subset 的数据上重新验证 Baseline vs Ours，回答 LSAR
提升是否在更多 scene / prompt 上保持。本阶段不优化 LSAR 结构，
不修改 diffusion，不引入第二个创新点。

本阶段目标规模为 5k 起，若数据提取与训练时间允许，再扩到 10k。

## 2. 数据前提

- 本地已有完整 RGB split：`image_part_aa` + `image_part_ab`。
- 已有解压的 Grasp-Anything++ instructions / positive tensors。
- 不需要重新下载网络数据，也不需要展开全量 RGB archive。

## 3. 任务拆解

### Stage F：生成 RGB scene 可用索引

1. 临时合并 `image_part_aa` + `image_part_ab` 为完整 zip；
2. 只列出 `image/<scene>.jpg` 成员名，写入 scene 列表；
3. 不展开压缩成员，仅保留一个 65GiB 临时 archive 用于后续按需解压。

### Stage G：准备 5k subset

1. 给 `prepare_training_subset.py` 增加 `--scene-list` 可选输入；
2. 用确定性 rank 从本地 4.4M stem 中采样；
3. 生成 `research/smoke-data/train_subset_5k.tsv`；
4. 校验 instruction / positive / scene 均可加载。

### Stage H：按需提取 5k RGB

复用 `extract_rgb_subset.sh`，只解压 `train_subset_5k.tsv` 中的
unique scene 到 `processed/grasp-anything/images`。

### Stage I：训练 Baseline 与 Ours

- Baseline：`--condition-mode none`
- Ours：`--condition-mode lsar --lsar-scale 0.01 --lsar-fixed-scale
  --lsar-affordance-weight 0.1`
- 其余配置与 3k 实验保持一致（15 epochs / batch 2 / 10-step eval）。

### Stage J：重复评估与可视化

每个 checkpoint 至少 3 次 10-step sampling eval，汇总 mean/std；
生成定性图与 affordance overlay。

### Stage K：决策

- Ours 优势保持：冻结 LSAR，准备最终训练/论文材料。
- Ours 与 baseline 无明显差异：记录 honest ablation，暂不扩模型。
- Ours 更差：进入 LSAR V2 空间门控或 conditioning 位置分析。

## 4. 成功标准

- `train_subset_5k.tsv` 可复现生成且全部 scene 本地 RGB 存在。
- Baseline / Ours 均训练完成并保存 checkpoint。
- 每个模型至少 3 次重复 eval。
- 输出明确的“保留 / 优化 / 放弃 LSAR”建议。

## 7. 执行结果（2026-09-03）

### Stage F/G/H：5k subset 完成

- `image_scenes_full.txt`：994860 个可用 RGB scene
- `research/smoke-data/train_subset_5k.tsv`：5000 stems / 5000 unique scenes
- 5000 张 RGB 从本地 split archive 按需解压，`extracted=5000 missing=0`

### Stage I/J：训练与重复评估完成

配置与 3k 实验保持一致：5000 stems / 4000 train / 1000 val / 15 epochs /
batch 2 / 10-step sampling / seed 42。

| Method | single eval /1000 | 3-repeat mean /1000 | std |
| --- | ---: | ---: | ---: |
| Baseline (`none`) | 211 | 202.7 | 4.93 |
| Ours (LSAR-full) | 299 | 309.7 | 3.51 |

Ours 重复均值高约 107/1000，且 3 次采样全部高于 baseline，支持保留当前
LSAR 结构。

### Stage J 可视化

- `outputs/lgdm_5k/visuals_affordance/qualitative.png`
- 4 个验证样本：apple stem、pen cap、highlighter cap、spoon handle
- 全部正确且 `affordance_rendered=true`

### Stage K：决策

- 保留当前 LSAR（scale=0.01 + lambda_aff=0.1），暂不优化网络结构。
- 5k/10k plan 的 5k 已执行；是否继续 10k 由用户按时间和资源决定。

## 5. 不做的事

- 不下载新数据。
- 不重新设计 diffusion。
- 不做 Flow Matching。
- 不推进论文。
- 不引入第二个创新点。
