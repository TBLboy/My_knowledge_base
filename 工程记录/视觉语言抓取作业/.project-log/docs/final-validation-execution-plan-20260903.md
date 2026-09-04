# Final Validation Execution Plan (10k + Paper Material)

> 记录时间：2026-09-03
> 状态：已修正并批准执行
> 来源：外部 GPT 行动指南 + 本机实现核对

> 2026-09-04 更新：`lambda_aff` sweep 完成后，最终方法固定为
> `lambda_aff=0.05`。10k 上最终方法 seed42 repeat mean `678.0`
>（`662/677/695`），seed43（`split-seed=42`）repeat mean `661.7`
>（`661/648/676`）；LSAR-no-aff `653.7`，LSAR-full `605.3`，
> LGDM `470.0`。`no-aff` 与 `full` 保留为 ablation。

## 1. 当前阶段

项目从方法探索进入最终验证/论文准备。架构冻结，不再做新的模型设计。

## 2. 冻结范围

- LSAR 当前实现保持不变。
- 不更换 LSAR backbone。
- 不引入 Transformer LSAR。
- 不修改 diffusion。
- 不引入 Flow Matching。
- 不增加第二个创新点。

## 3. 当前实现必须写进论文

实现文件：`models/lgdm_lsar.py`

LSAR 实际结构：

```text
input = concat(visual_conv3_feature, ALBEF y_view)
hidden = ReLU(Conv3x3(GroupNorm(ReLU(Conv3x3(input)))))
residual = scale * Conv1x1(hidden)
F' = ReLU(F_conv3 + residual)
affordance_map = aff_head(hidden)   # shape (B, 1, 19, 19)
```

最终训练 objective：

```text
L =
diffusion_loss
+ dense_cos
+ dense_sin
+ dense_width
+ lambda_aff * MSE(affordance_map, adaptive_avg_pool2d(pos_gt, 19))
```

其中 `scale=0.01` 固定，`lambda_aff=0.05`。

论文不采用 `F' = F * (1 + A)` 的替代公式，因为与代码不符。

## 4. 数据定义

### 10k subset

- `research/smoke-data/train_subset_10k.tsv`
- 10000 unique scenes / 每 scene 1 stem
- 使用本地 RGB scene 索引，不重新下载数据
- seed 42，确定性采样
- 10k 的采样算法与 5k 相同，文档中说明“前 5k 与 `train_subset_5k.tsv` 高度重合”
  或直接说明“10k 独立读取 `train_subset_10k.tsv` 为最终结果来源”。

### Split

- 80% train / 20% val
- 因为每 scene 只有 1 stem，sample-level split 自动是 scene-disjoint split
- 论文直接报告“scene-disjoint split by construction”
- 不额外跑一个无意义的 Random vs Unseen 重复对照

## 5. 训练实验

### Model A：LGDM baseline

```bash
--condition-mode none
```

### Model B：LSAR-full

```bash
--condition-mode lsar \
--lsar-scale 0.01 \
--lsar-fixed-scale \
--lsar-affordance-weight 0.1
```

### Model B2：最终 LSAR（paper main method）

```bash
--condition-mode lsar \
--lsar-scale 0.01 \
--lsar-fixed-scale \
--lsar-affordance-weight 0.05 \
--seed 42 --split-seed 42
```

第二训练 seed 使用 `--seed 43 --split-seed 42`，与 seed 42 共用同一验证集。

### Model C：LSAR-no-aff（ablation）

```bash
--condition-mode lsar \
--lsar-scale 0.01 \
--lsar-fixed-scale \
--lsar-affordance-weight 0.0
```

统一配置：

- epochs = 15
- batch size = 2
- lr = 1e-3
- weight decay = 1e-4
- eval steps = 10
- seed = 42

输出：

```text
outputs/lgdm_10k/none
outputs/lgdm_10k/lsar_full
outputs/lgdm_10k/lsar_no_aff
```

## 6. Evaluation

### Repeat eval

- 每个 checkpoint 至少 3 次 10-step sampling eval
- seed 100/101/102
- 输出 mean / std

### Diffusion-step sensitivity

- 同一 checkpoint，不重新训练
- eval steps = 10 / 50
- 如果时间允许，再加 100
- 论文表述为“sampling-step sensitivity”，不是 full 1000-step claim

## 7. Visualization

生成 paired qualitative figure：

```text
image + instruction
GT grasp
LGDM prediction
LSAR prediction
LSAR affordance map
```

- 4-6 个验证样本
- 优先包含 part-level：spoon handle、pen cap、apple stem、highlighter cap

## 8. Paper Material

最终准备好：

- Architecture figure：ALBEF -> LSAR -> diffusion decoder
- Main results table：LGDM / LSAR-full / LSAR-no-aff
- Sampling-step table：10 / 50 steps
- Qualitative figure
- Limitation：10k subset、15 epochs、10-step sampling、未覆盖全部 Grasp-Anything++

## 9. 任务顺序

1. 写入本指南并 commit
2. 生成 `train_subset_10k.tsv`
3. 按需解压 10k RGB
4. 训练 LGDM baseline
5. 训练 LSAR-full
6. 训练 LSAR-no-aff
7. 3 个 checkpoint 的 3 次 repeat eval
8. 10/50-step sensitivity（时间允许加 100）
9. paired visualization
10. paper table/skeleton 与项目记录，最终 commit

## 10. 禁止事项

- 不改模型架构。
- 不无限扩大数据量，10k 足够当前目标。
- 不追 SOTA。
- 不以 5k 单独结果充当最终论文主结论。
