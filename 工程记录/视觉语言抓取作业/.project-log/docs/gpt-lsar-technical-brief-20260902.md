# LSAR 技术思路简报（给外部 GPT）

> 目的：把当前已经跑通的 baseline、官方代码真实结构、LSAR 技术方案和需要外部判断的问题打包，供 GPT 审阅。
> 日期：2026-09-02
> 状态：技术方向提案，未开始编码。

## 1. Goal & Exact Questions

**项目目标**：基于 Grasp-Anything++，实现 image + language instruction → 2D grasp rectangle \((x,y,w,h,\theta)\) 的可训练、可评估、可提交流水线，交付 GitHub + ≤2 页 CVPR 英文论文。

**目前实际状态**：
- 环境 self-contained 已通过。
- 10 个真实 stem 的 baseline engineering smoke 已通过：10/10 能走通 forward/loss/backward/post-process/IoU。
- Proposed Method 已确定为 LSAR（Language-conditioned Spatial Affordance Refinement）。
- 尚未开始 LSAR 编码。

**请 GPT 回答以下问题**：
1. 在“一周任务、非 SOTA、算法核心要作为 our contribution”的前提下，用官方仓库里当前可跑的 `lgrconvnet3` dense-map baseline 作为论文 baseline，把 LSAR 接在该模型上，是否足够？还是必须把官方 diffusion/LGD 链路真实跑通并接在 diffusion 上？
2. LSAR 的最佳插入方式、门控公式应该选哪一种？我倾向在 `x_fused = F_v + L` 之后生成空间 mask，并用残差门控，但需要你判断 `x_refined = x_fused + a * F_v`、`x_refined = x_fused * (1 + a)`、或 channel-wise 门控哪一个更合理、更容易论文解释。
3. 辅助损失用 `BCE(A_ref, M_grasp)`，其中 `M_grasp` 是 positive dense map 下采样到 56×56，是否合理？会不会因为最终四个 dense map 已经用同一 GT 监督，导致这条辅助损失没有独立价值？如果不是最优，最小的可解释替代监督是什么？
4. 最小可信实验应该怎么设计？我打算：100 sample sanity → 5k training/validation subset → Baseline vs Ours → with/without LSAR。是否需要增加“不同 instruction 长度 / 不同 positive N / unseen scene”分层，才能让 paper 的表格有说服力？
5. LSAR 是否足够算一个“meaningful contribution”？是的话论文卖点应怎么写：intermediate spatial affordance supervision、multi-scale grasp region prior、language-conditioned gate 中哪个最站得住？

## 2. 当前可执行 Baseline 的真实代码结构

我们正在使用的模型是 `LGD-main/inference/models/lgrconvnet3.py::GenerativeResnet`。

关键 forward 过程（已读取源码确认）：

```python
x = F.relu(self.bn1(self.conv1(x_in)))   # 224x224 -> ...
...
x = self.res5(x)                          # x: [B, C, 56, 56]

y_feats = self._encode_text(query, device=device)
y_feats = self.y_flatten(y_feats)         # [B, 56]
y_feats = y_feats.unsqueeze(2).expand(-1, -1, 56)
y_feats = y_feats.unsqueeze(1).expand(-1, 128, -1, -1)
# y_feats: [B, 128, 56, 56]

x = torch.clone(x).detach() + y_feats     # text-conditioned feature
# decoder: convT -> 224x224 -> pos/cos/sin/width heads
```

- 输入是 RGB 224×224（`input_channels=3`）。
- 文本用冻结 CLIP ViT-B/32 编码，`y_feats` 通过 broadcast-add 进视觉分支。
- 训练监督是四张 dense map：`pos / cos(2θ) / sin(2θ) / width`，loss 为四路 smooth L1 相加。
- 评估是 `post_process` + `detect_grasps` + `calculate_iou_match`，判定为 IoU > 0.25 且角度差 < 30°。

所以这里并不存在一个现成的“独立 attention map”；语言信息目前是 channel-wise 全图加性融入。LSAR 如果做在这里，实质是在 **56×56 融合特征上生成语言条件化的空间 gate，再进入 decoder**。

已确认的工程证据：
- 10 个不同 scene 的真实 stem，`batch_smoke.py` 输出 10/10 OK、0 FAIL。
- 每个 stem 的 instruction 都是 `.pkl` 中的字符串，例如 `Take fork by its handle.`。
- 每个 stem 的 positive GT 是 `[N,6] float32`，`N` 从 1 到 17 不等；GT 可转成 224×224/56×56 dense region map。

## 3. 我建议的 LSAR V1

我不建议第一版直接碰 diffusion。理由是当前能端到端训练/评估的最小边界是 `lgrconvnet3` dense-map 链路，而 diffusion 链路尚未跑通，也不一定在一个星期内能安全落地。

**V1 定位**：
- Baseline：`lgrconvnet3`（官方 LGD 仓库里的 CLIP-conditioned dense-map grasp network）。
- Ours：Baseline + LSAR。
- 论文中可措辞为“在官方 LGD-style baseline 的 conditioning 分支中加入 LSAR”，并明确 diffusion/flow matching 是未来扩展。

**模块插入点**：

```text
F_v = res5 output               # [B,128,56,56]
L   = expanded CLIP text feat   # [B,128,56,56]
x_fused = F_v.detach() + L      # 官方 baseline 原融合
a = LSAR(x_fused)               # [B,1,56,56] or [B,C,56,56]
x_refined = x_fused + a * F_v   # 残差空间门控
decoder(x_refined)
```

**LSAR-CNN（Option 1）**：

```python
class LSAR(nn.Module):
    def __init__(self, channels=128, hidden=64):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, hidden, 3, padding=1)
        self.conv2 = nn.Conv2d(hidden, 1, 3, padding=1)
    def forward(self, x):
        a = F.relu(self.conv1(x))
        a = torch.sigmoid(self.conv2(a))
        return a
```

如果选 channel-wise：`a` 变成 `[B,128,56,56]`，最后一层输出 128 通道。第一版建议先做单通道 spatial gate，代码和 ablation 最简单。

**辅助监督**：
- 把 positive dense map `pos_img`（224×224）下采样到 56×56 得到软目标 `M_grasp`。
- `L_aff = BCEWithLogits(A_logits, M_grasp)` 或对 sigmoid 后的 `a` 做 `BCE(a, M_grasp)`。
- 总 loss：
  ```text
  L = L_smooth_l1_maps + λ_aff * L_aff
  ```
- 建议 `λ_aff` 初始 0.1。

**为什么值得试**：
- 官方 baseline 的加性语言注入是 channel-wise、全空间一致的“语义偏置”，没有显式的“language → grasp region”空间定位。
- LSAR 把语言条件变成空间 gate，并显式监督到 grasp region，方向与任务一致。
- 模块很小，容易做 with/without LSAR ablation。

## 4. 训练与实验计划

**数据**：
- 现有本地数据：全部 `grasp_instructions` 和 `grasp_label_positive` 已解压；RGB 大 zip 还在 raw，目前只解压了 10 张 scene 图。
- 做 100/1000/5000 训练样本时，需要先写一个数据准备脚本，从 RGB split zip 中按需要的 stem 抽取 `<scene>.jpg`，而不是全量解压 60 GiB。
- 磁盘约束：`/mnt/data` 约 107 GiB 可用；raw 两个 RGB part 合计约 65 GiB。因此建议抽取时用“临时合并 → 选成员解压 → 删除临时合并文件”的方式，或者把临时合并放到项目盘空闲空间较多的分区。

**V1 sanity**：
- 100 samples，10 个 scene 左右，先验证 LSAR shape、forward、backward、loss 下降、checkpoint 保存/加载。
- 不要求正确率，只要求 pipeline 稳定。

**V1 小实验**：
- 5k samples 划分 train/val，固定 seed。
- 对比：
  - 官方 baseline（无 LSAR）
  - baseline + LSAR（spatial gate）
  - 可选：LSAR channel-wise gate
- 指标沿用 IoU > 0.25 + angle < 30° 的 success rate，再记录平均 loss、正确数量。
- 可视化：RGB + GT rectangles + predicted rectangles；最好包含同 scene 不同 instruction（例如 apple skin / apple stem）来体现 language conditioning。

**Ablation**：
1. Baseline vs +LSAR。
2. spatial gate vs channel-wise gate（如果时间允许）。
3. 不同 `λ_aff`（0 / 0.05 / 0.1）可作为附加表，但并非必要。

## 5. 已确认 / Assumption / Unknown

**已确认（code/file evidence）**：
- `lgrconvnet3` forward 使用 `F_v.detach() + CLIP-text-broadcast`；CLIP 冻结。
- dense map loss、post_process、IoU evaluation 都能在 10 个真实 stem 上跑通。
- 10 stem 的 instruction 是真实字符串，positive GT 是 `[N,6]`。
- env 已 self-contained，CUDA 可用。

**Assumption（我的设计假设，需要 GPT 审）**：
- 可以在 `F_v`（56×56）处插入 LSAR，并由 decoder 后续容量把空间 gate 传递到 224×224 输出。
- positive dense map 下采样成 56×56 是一条合理、可解释的 grasp affordance prior。
- `lgrconvnet3` dense-map baseline 可作为论文 baseline；diffusion 链路不是强制前提。

**Unknown / To Verify**：
- 官方训练里 `grasp_instructions` 是否直接 encode 成 CLIP text query，还是用 `queries[obj_id]` 等其他语义；当前我们直接 encode `.pkl` 字符串，尚未完成正式语义核对。
- LSAR 的辅助监督是否会和最终 dense map 监督冗余。
- 当前数据只解压了 10 张 scene 图，对 5k 训练需要重新抽取；抽取耗时/磁盘策略未实测。
- 官方 `lgdm` / diffusion 是否必须纳入论文 baseline，尚未决策。

## 6. 风险与约束

- 不能碰的：不修改官方 grasp 表示、评估协议；不下载完整 negative/part_mask；不搞多个创新点并行。
- 最大工程风险：5k 数据准备需要从 65 GiB RGB split 中抽取足够 scene 图，应该在写模型之前先做 100/500 张可重复抽取的小脚本验证。
- 最大方法风险：LSAR 可能只给 marginal gain；因此它需要配合明确的 ablation 和 qualitative 证据，不强求 SOTA。
- 时间控制：先 100 sanity + 5k，若 5k 训练成本高再降为 1k，但至少保证 Baseline vs Ours 同数据、同 seed。

## 7. 我期望 GPT 给的最简结论

请直接给一个“可执行判断”，不要展开成完整论文：
1. 接受 / 不接受 V1 使用 `lgrconvnet3 + LSAR` 作为 our method。
2. 如果接受，选一个推荐门控公式和辅助监督组合。
3. 如果不接受，指出最接近当前工程、一周内能做完的替代方案。
4. 给出 V1 的最小实验清单（不要超过 3~4 个对比项）。
