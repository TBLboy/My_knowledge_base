# LGDM Baseline Training Objective Review 2026-09-02

## 结论

外部 GPT 建议的方向正确：先建立“diffusion objective 真正参与训练”的 Clean LGDM
Baseline，再插入 LSAR，不碰 Flow Matching，不回到 lgrconvnet3。

但按当前官方代码事实，两个地方需要调整后才能直接执行：

1. 不能简单写 `dense_loss + lambda * diffusion_loss`。
2. LSAR 插入点必须先根据 LGDM 实际 condition 张量流确定，不能只按概念图接。

## 1. LGDM 当前 loss 事实

官方 `diffusion/training_losses()` 返回：

```text
loss = mse + 1e-3 * contr
```

其中：

- `mse`：模型预测与 `x_start` 的 MSE，shape 为 `(B,1,H,W)`
- `contr`：`NCELoss(x_t, guiding_point, model_output)`

真实 smoke 观察：

- `mse` 约 `0.61`
- `contr` 约 `31000-32000`
- `diffusion loss` 约 `31.9`
- dense-map `compute_loss` 约 `1.5`

关键点：`LGDM.compute_loss` 里的 `p_loss` 与 `training_losses` 里的 pos
MSE 是同一个量。因为在 `LGDM.forward` 中：

```text
pos_output = x + pos_output
self.pos_output_str = pos_output
```

所以官方 dense loss 和 diffusion loss 并不完全正交。直接相加会重复计算
pos 损失，也会让 contrast 项在当前规模下主导 total loss。

建议的 Clean LGDM loss：

```text
total = diffusion.loss (pos mse + 1e-3 * contr)
      + MSE(cos_pred, cos_gt)
      + MSE(sin_pred, sin_gt)
      + MSE(width_pred, width_gt)
```

即：

- diffusion loss 负责抓取位置与 contrast/alignment
- cos/sin/width 损失负责姿态和宽度
- 不再重复加 `p_loss`

训练时应分别记录：

```text
mse / contr / pos / cos / sin / width / total
```

## 2. LGDM 当前 conditioning 事实

`LGDM.forward` 中 ALBEF 返回两个量：

```text
image_atts, y = self.albef(img, text_input, alpha, idx)
```

当前真正使用的方式：

- `image_atts` 会上采样为 `full_image_atts (B,224,224)`，再乘到 RGB 上
- `y` 会经过 `y_flatten -> y.view(-1,8,19,19)`
- 但代码里 `img = torch.clone(img).detach() + y` 是注释掉的

因此官方当前实现里，文本 conditioning 的实际入口主要是
`full_image_atts -> RGB gate`；`y` 的 text feature 当前没有真正注入视觉
feature 分支。

这对 LSAR 的影响：

- 不能假设“ALBEF output 直接进入 diffusion”
- 要先确认 LSAR 到底 refine：
  1. `full_image_atts`（224x224 空间 gate）
  2. 还是 `y`（文本融合 feature，需要同时恢复官方的 `+ y` 注入）
  3. 还是两者

## 3. LSAR V2 建议调整

保留外部 GPT 的主方向：接在 conditioning branch，放在 ALBEF 后、diffusion
denoiser 前。

实现前先做一次“tensor-flow debug”：

- 打印 `image_atts.shape`、`full_image_atts.shape`
- 打印 `y.shape`、`y_flatten(y).shape`
- 打印当前 text feature 是否影响了 gradient
- 选择一个可量化、可 ablation 的插入位置

推荐优先候选：

```text
image_atts -> full_image_atts -> LSAR -> gated RGB -> GG-CNN
```

如果希望 LSAR 更接近文本条件融合，则第二个候选：

```text
ALBEF text/vision fusion -> y -> LSAR -> y_flatten -> 8x19x19 condition
```

两个候选都可以写同一个 smoke abstraction，但不要在第一次实现里同时做。

## 4. 100 Sample Sanity 的准备工作

当前本地只有 10 张真实 RGB `<scene>.jpg`。要训练 100 sample，需要：

1. 从已下载的 `grasp_instructions` / `grasp_label_positive` 生成 100 个 stem
2. 从 65 GiB image zip 中只解压这 100 个对应 `<scene>.jpg`
3. 固定 train/val split
4. 写训练脚本、checkpoint、日志、evaluation

建议初始参数：

- batch size：2，验证稳定后再试 4
- epochs：30-50
- 训练时不跑完整 1000 步 sampling
- 评估时选 1-5 个样本跑少量步数或完整采样，验证 decode 和 checkpoint

## 5. 后续实验

最小实验矩阵：

```text
LGDM baseline
LGDM + LSAR
LGDM + LSAR (without affordance loss)   # optional ablation
```

不允许：

- Flow Matching
- 重设计 diffusion
- 回到 lgrconvnet3

## 6. Tensor-flow verification 2026-09-02

新增证据来自 `research/scripts/lgdm_tensorflow_debug.py`，使用真实 stem
`0b5a946368b49b87460c5b6ce1f69c2f93cb236f3f8f572a094de58634d1d9ed_1_1`。

### 6.1 Official forward

```text
image_atts            (1, 197)
full_image_atts       (1, 224, 224), min=1, max=1, unique=[1.0]
albef_y               (1, 10, 768)
y0                    (1, 1, 768)
y_flatten             (1, 1, 2888)
y_view                (1, 8, 19, 19)
conv3                 (1, 8, 19, 19)
pos/cos/sin/width     (1, 1, 224, 224)
```

梯度结论：

- `full_image_atts` 不是语言注意力图，而是 ALBEF 直接返回的全 1 mask，
  RGB gate 不携带语言信息。
- `y0` 与 ALBEF text 参数在官方 forward 中 grad 均为 `None`，因为
  `img = torch.clone(img).detach() + y` 被注释，文本分支不连接 grasp 输出。

### 6.2 Inject-y probe

在同一 debug 脚本中把 `y_view` 加到 GG-CNN `conv3` 后：

```text
y_view shape                    (1, 8, 19, 19)
conv3 shape                     (1, 8, 19, 19)
y_flatten input grad shape      (1, 1, 768), finite=True
ALBEF text parameter grad       finite=True
```

这证明文本融合特征 `y` 有明确、可训练的条件注入路径。LSAR V1 的
插入点因此固定为：

```text
ALBEF y -> LSAR -> y_flatten -> y_view (8x19x19) -> conv3
```

不再选择 `full_image_atts` 路线，因为该张量当前是常量全 1，没有可学习
空间语义。

## 7. Clean LGDM 100-sample sanity 2026-09-02

### 7.1 数据集

- `research/scripts/prepare_training_subset.py`：确定性采样 100 个真实 stem，
  100 个不同 scene，全部通过 instruction str / positive `[N,6]` / finite 校验。
- `research/smoke-data/train_subset_100.tsv`：固定 train/val 数据清单。
- `research/scripts/extract_rgb_subset.sh`：只解压对应的 100 张
  `<scene>.jpg`，不展开完整 image zip。

### 7.2 训练

- `research/scripts/train_lgdm_clean.py`：Clean LGDM objective：

```text
total = diffusion.loss (pos mse + 1e-3 * contr)
      + MSE(cos) + MSE(sin) + MSE(width)
```

- 80 train / 20 val，batch size 2，20 epochs，AdamW lr 1e-3。
- 训练 40 batches/epoch，约 1.3-2.7 秒/epoch。
- `outputs/train_lgdm_clean_100/last.pt` 可被 `--resume` 成功加载。
- 10-step respaced sampling 评估：`5/20 correct`。

限制：

- 100 sample 是工程 sanity，不是性能实验；loss 未收敛到可用精度。
- 官方 contrast 项很大，当前 clean loss 总量主要由 `1e-3 * contr` 主导；
  后续 baseline vs LSAR 实验需再检查是否需要缩放。

## 8. LSAR V1 implementation and minimal experiment 2026-09-02

### 8.1 Module

新增 `models/lgdm_lsar.py`：

- `SpatialAffordanceRefinement`：输入 GG-CNN `conv3 (8x19x19)` 与
  ALBEF `y_view (8x19x19)`，输出残差，使用可学习 `scale`。
- `LGDMWithConditioning`：继承官方 `LGDM`，不改上游文件；支持
  `none` / `plain-y` / `lsar` 三种 conditioning mode。

`train_lgdm_clean.py` 新增 `--condition-mode`，三种条件共用同一数据、
loss、checkpoint 和 evaluation 链路。

### 8.2 Stability finding

第一版把残差初始化为 0 并令 `scale=0`，20 epochs 后 `scale` 仍为 0：
零 scale 让残差分支梯度也为 0，模块实际未训练。

修正为 `scale=0.1` 初始化后，20 epochs 训练结束 `scale=0.158`，
LSAR 输出开始参与 forward。

### 8.3 Minimal results

100 个真实 stem，80 train / 20 val，batch size 2，20 epochs，
10-step respaced sampling：

| condition | eval correct |
| --- | --- |
| none (official LGDM) | 4/20 |
| plain-y (no LSAR) | 4/20 |
| lsar | 4/20 |

限制：100 样本 20 epochs 的结果不具备统计意义，不用于论文性能声明；
当前价值是 Baseline、plain-y、LSAR 三者的代码和评估协议已对齐。
