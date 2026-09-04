# Large-Subset LSAR Validation Plan

> 记录时间：2026-09-02
> 状态：已批准待执行
> 上一阶段结论：LSAR `scale=0.01` + `lambda_aff=0.1` 是当前最优条件，
>   repeat eval 均值 `41.67/200`，高于官方 baseline `37.0/200`，
>   no-aff 降到 `18.67/200`；需要更大 subset 做 Baseline vs Ours。

## 1. 本阶段目标

验证当前 LSAR 配置在大 subset 上是否仍优于官方 LGDM，并基于结果决定：
继续冻结 LSAR、优化 LSAR 结构，还是转向其他方向。

## 2. 数据与配置

不再从 65GB RGB zip 新提取图片，现有 1010 个 RGB scene 可复用。

- subset：`research/smoke-data/train_subset_3k.tsv`
- 采样：2968 个真实 stem（现有 RGB + 每 scene 最多 3 个约束下的全部可用样本）
- split：80% train / 20% val = 2374 / 594
- epochs：15
- batch size：2
- eval：10-step diffusion sampling，3 次重复取 mean/std
- seed：42

两个对照，训练配置完全一致：

| Model | command condition |
| --- | --- |
| Baseline | `--condition-mode none` |
| Ours | `--condition-mode lsar --lsar-scale 0.01 --lsar-fixed-scale --lsar-affordance-weight 0.1` |

输出目录：

```text
outputs/lgdm_larger_subset/none
outputs/lgdm_larger_subset/lsar_full
```

## 3. 任务拆解

### Stage A：准备 3000-sample subset

1. 给 `prepare_training_subset.py` 增加 `--allow-same-scene`，
   保留现有 unique-scene 行为。
2. 生成 `train_subset_3000.tsv`。
3. 验证：
   - 2968 个合法 stem
   - unique scenes <= 1010
   - 每个 scene 不超过 3 个样本
   - instruction / positive 均可加载

### Stage B：训练官方 LGDM baseline

- `--condition-mode none`
- 其余配置与 Ours 完全一致

### Stage C：训练 Ours（LSAR-full）

- `--condition-mode lsar --lsar-scale 0.01 --lsar-fixed-scale
  --lsar-affordance-weight 0.1`

### Stage D：重复评估与可视化

- 两个 checkpoint 各 3 次 10-step eval
- 汇总单次 eval 与 repeat mean/std
- 保存 qualitative 图，含 affordance overlay

### Stage E：决策

- Ours 明显优于 Baseline：冻结 LSAR，整理最终训练/论文材料。
- Ours ≈ Baseline：不扩模型，改为审视 data/fusion/loss/head 等方向，
  把 LSAR 作为可解释 ablation 报告。
- Ours 更差：进入 LSAR 结构优化，优先尝试空间门控
  `F' = F * (1 + sigmoid(A))` 或换 conditioning 位置。

## 4. 成功标准

- `train_subset_3000.tsv` 可复现生成且加载通过。
- Baseline / Ours 两个训练都能跑完并保存 checkpoint。
- 每个模型至少 3 次重复 eval 结果。
- 给出“保留 LSAR / 优化 LSAR / 换方向”的明确建议。

## 5. 不做的事

- 不下载新增 RGB。
- 不改 diffusion。
- 不做 Flow Matching。
- 不推进论文。
- 不引入第二个创新点。

## 6. 执行结果

### Stage A：subset 完成

`research/smoke-data/train_subset_3k.tsv`：

- 2968 stems
- 1010 unique scenes
- 每 scene 最多 3 个 stem
- 所有 scene 本地 RGB 存在

### Stage B/C：训练完成

| Model | single eval | 3-repeat mean | std |
| --- | ---: | ---: | ---: |
| Baseline (`none`) | 151 / 594 | 152.0 / 594 | 5.57 |
| Ours (LSAR-full) | 185 / 594 | 179.0 / 594 | 1.73 |

两者配置完全一致：2968 stems、2374 train / 594 val、15 epochs、
batch 2、10-step sampling。

### Stage D：可视化完成

- `outputs/lgdm_larger_subset/visuals_affordance/qualitative.png`
- 4 个样本：spoon handle、fork handle、apple stem
- summary 中 `affordance_rendered=true`

### Stage E：决策

- 保留当前 LSAR（scale=0.01 + lambda_aff=0.1），暂不优化网络结构。
- Ours 重复评估均值提高约 27/594，且 std 更小，趋势与 1000 样本一致。
- 数据仍受限于 1010 scene / 2968 stem，不作为最终论文性能结论。
- 下一步由用户确认：继续 5k/10k subset、提取更多 scene 的 RGB，
  或进入最终训练/论文材料。
