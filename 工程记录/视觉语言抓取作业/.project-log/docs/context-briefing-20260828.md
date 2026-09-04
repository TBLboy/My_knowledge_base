# 项目上下文简报：Language-driven Grasp Detection

> 用途：把当前工程状态交给另一侧 GPT，请它判断最小可执行的下一步。
> 时间：2026-08-28

## 给 GPT 的请求

请基于下面“已确认”和“未确认”的信息，给出当前阶段的最小可执行方案。当前优先级是：

1. 不下载全量 Grasp-Anything++ / Grasp-Anything 数据；
2. 不提出最终 Proposed Method；
3. 不做大规模训练；
4. 先完成真实数据 sample alignment 验证；
5. 再完成一个 `dataset -> forward -> loss -> post_process -> evaluation` 的 subset smoke test。

请具体回答：

- 下一步先执行哪个脚本/命令？
- 在不读取整个远程 zip 中央目录的前提下，如何验证 `grasp_instructions`、`grasp_label_positive`、`grasp_label_negative`、`part_mask` 的 sample stem 对齐？
- 如何只取少量真实 plusplus sample？其中 RGB image 从哪里拿？
- 如何最小修复 LGD 官方 loader，让它能读取 HF 当前发布的 plusplus 文件结构？
- 用 `lgrconvnet3` 跑通 smoke test 需要安装哪些依赖、需要改哪些 shape？
- 哪些事实在本阶段无法从源码/文件确认，应该继续标 `Unknown / To Verify`？

## 当前状态一句话

第一阶段技术调查已完成，数据格式、官方 baseline 主链和评估协议已基本确认；当前卡在“用真实 plusplus 数据证明 sample 对齐并跑通最小 smoke test”，且官方 LGD 代码与 HF 当前发布的目录结构存在多处不一致。

## 工程背景

- 项目目录：`/home/tbl/Project/视觉语言抓取作业`
- 任务：Language-driven Grasp Detection Programming Test
- 输入：RGB image + natural-language grasp prompt
- 期望输出：2D grasp rectangle `(x, y, w, h, theta)`
- 数据集：Grasp-Anything++
- 最终交付：GitHub 仓库 + 不超过 2 页的 CVPR-style 英文论文
- 当前阶段：`solution-research`
- Git：个人仓库已初始化，`main` 分支，尚无 commit

## 已确认事实（证据状态：candidate）

### 数据集结构

Grasp-Anything++（`airvlab/Grasp-Anything-pp`）通过 HF zips 发布：

| 文件 | 大小 | 内容 |
| --- | ---: | --- |
| `grasp_instructions.zip` | 1,544,210,262 B | `<scene>_<obj>_<part>.pkl`，实测为纯字符串 |
| `grasp_label_positive.zip` | 3,949,367,278 B | 同名 `.pt`，shape `[N,6]` float32 |
| `grasp_label_negative.zip` | 5,124,021,498 B | 同名 `.pt`，shape `[N,6]` float32 |
| `part_mask.zip` | 4,793,595,253 B | 同名 `.npy`，shape `(416,416)` uint8 |

Grasp-Anything（`airvlab/Grasp-Anything`）提供基础图像和 object-level 数据：

- `image_part_aa` + `image_part_ab`：合并约 65 GB，内含 `<scene>.jpg`
- `scene_description.zip`：`<scene>.pkl`，实测 `(scene_text, [object_names])`
- `mask.zip`：`<scene>_<obj>.npy`
- `grasp_label_positive.zip` / `grasp_label_negative.zip`：object-level labels

### GT 格式

- `.pt` 每行是 `[quality, x, y, w, h, theta_deg]`
- 代码内部使用 `[y, x]` 坐标；角度取负并转弧度
- 一个 instruction 对应 `[N,6]` positive grasps，可能存在多个合法 grasp
- `negative` 第一列质量分数为负，当前官方 baseline 主链不消费 negative
- `part_mask` 不进入当前官方训练/评估主链

### 官方 LGD baseline 主链

代码快照位于 `LGD-main/`：

- Dataset: `utils/data/grasp_anywhere_data.py::GraspAnywhereDataset`
- Common sample: `utils/data/language_grasp_data.py::LanguageGraspDatasetBase.__getitem__`
- Models: `lgrconvnet3`、`lggcnn`、`lgdm`
- Loss + decode + eval:
  - `train_network.py` / `train_network_diffusion.py`
  - `inference/post_process.py`
  - `utils/dataset_processing/grasp.py::detect_grasps`
  - `utils/dataset_processing/evaluation.py::calculate_iou_match`

官方 baseline 不直接回归五参数，而是输出 dense maps：

```text
pos_output, cos_output, sin_output, width_output
```

监督目标也是 dense maps：

```text
pos map, cos(2*angle) map, sin(2*angle) map, normalized width map
```

decode：

```text
angle = atan2(sin, cos) / 2
width = width_map * 150
detect_grasps: peak_local_max(min_distance=20, threshold_abs=0.2, num_peaks=1)
```

evaluation：

```text
success_rate = correct / (correct + failed)
correct: predicted grasp has IoU > 0.25 with at least one GT and angle diff < 30 degrees
```

论文主结果：LGD + CLIP `Seen 0.48 / Unseen 0.42 / H 0.45`。

## 当前卡点

1. **sample alignment 尚未用全量证据证明。** 我们手上有少量真实样本，但四类 zip 是否对每个 `<scene>_<obj>_<part>` 完全对齐，尚未通过完整索引验证。
2. **官方 LGD 代码与 HF plusplus 结构不一致。**
   - HF 是 `grasp_label_positive/*.pt` + `grasp_instructions/*.pkl`；
   - LGD 代码期望 `positive_grasp/*.pt` + `prompt/*.pkl`；
   - 并且 `get_prompts` 实际 encode `queries[obj_id]`，不 encode `grasp_instructions`。
3. **RGB image 的来源仍需确认。** plusplus 自身不含 image，按 Dataset Card 应使用 Grasp-Anything base image，但我们没有验证某个 plusplus stem 的 scene hash 能对应到具体 `<scene>.jpg`。
4. **模型 shape 是否端到端可跑尚未验证。** 静态估算 `lgrconvnet3` 输出应为 `224x224`；`lggcnn` / `lgdm` 按当前代码可能输出 `332x332`，与 GT `224x224` 不匹配。需要 smoke test 确认。
5. **依赖不完整。** 当前 `grasp-lgd` 环境缺少 `clip`、`cv2`、`skimage`、`tensorboardX`、`torchsummary` 等。

## 最近一次尝试

曾尝试通过 HTTP Range 只读取远程 zip 中央目录，避免下载全量数据：

1. 第一次用 `zipfile.ZipFile` 包一个 range reader，运行超过 4 分钟，未拿到结果；
2. 第二次写了 `research/scripts/list_remote_zip.py`，只请求 EOCD + central directory，但实际传输量偏大，随后被中止，没有成功输出；
3. 没有产生任何样本对齐结果文件。

结论：当前不该继续用这种方式枚举超大 zip 的全量中央目录，除非先证明其请求范围正确且下载量可控。

## 环境

- Python：`/home/tbl/miniforge3/envs/grasp-lgd/bin/python`，Python 3.10.21
- torch：2.12.0+cu126
- numpy：2.2.6
- 已装：`requests`、`PIL`、`matplotlib`、`scipy`、`transformers`、`ruamel.yaml`
- 缺：`clip`、`opencv-python`、`scikit-image`、`tensorboardX`、`torchsummary` 等
- 网络：Hugging Face 官方域名不可达；`https://hf-mirror.com/...` 可访问

## 主要本地资料

- 技术调查报告：`docs/technical-investigation-report.md`
- 官方 LGD 代码：`LGD-main/`
- 论文 PDF/text：`research/paper/`
- 已抓真实样本：`research/data-samples/`
- HF zip 尾部证据：`research/hf-zip-evidence/`
- 远程 zip 枚举尝试脚本：`research/scripts/list_remote_zip.py`（目前未完成，可替换或删除）

## 未确认 / 需要外部判断

- 四个 plusplus zip 的成员名是否完全一一对应；
- `grasp_instructions` 纯字符串最终应该作为 model text input，还是应配合 base 的 `scene_description` / object query 组合；
- 是否必须下载 base image 才能完成最小 smoke test；是否有无需 65 GB 的方式拿到少量真实图像；
- `lgrconvnet3` 在当前环境、真实数据、默认 224 尺寸下能否直接 forward/loss/eval；
- 官方论文 checkpoint 是否真由当前 `train_network_diffusion.py` 训练得到；
- 当前 HF 发布是否与论文训练时使用的预整理目录结构不同。

以上未确认点在没有新的官方文档、代码或实测证据前，不应被自行补全为事实。
