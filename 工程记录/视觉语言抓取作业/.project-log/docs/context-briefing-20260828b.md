# 项目上下文简报（阶段二：真实样本 baseline smoke chain 已跑通）

> 用途：把当前工程状态交给另一侧 GPT，请它判断下一步最小可执行方案。
> 时间：2026-08-28
> 关联 commit：`0c6c2a9`（phase‑1 调查） → `ea46d18`（smoke chain） → `7c3acf4`（loop evidence 刷新）

## 给 GPT 的请求

请在以下三条候选路线中给出推荐，并明确推荐的影响 / 风险 / 下一步具体动作：

1. **把 smoke fixture 扩到 5~10 个真实 stem**：在不下载全量 Grasp‑Anything++ / Grasp‑Anything 的前提下，再多抓几组 `<scene>_<obj>_<part>`，跑批量 forward + IoU evaluation，生成可视化，作为论文的定性证据。
2. **直接进入 Proposed Method 设计**：基于现有 `lgrconvnet3` + CLIP fusion，确定一个范围可控、可以解释的改动（fusion / attention / loss / prompt conditioning 等），并准备最小训练实验。
3. **先重建一个真正独立的 Python 环境**：把 `torch/torchvision/numpy/matplotlib/scipy` 等锁版本装进 `grasp-lgd` env，禁用 user‑site，保证 GitHub 可复现，再继续。

请回答：

- 在当前资源（无 GPU/Colab 受限、无全量数据、时间约 1 周）下，哪条路线最合适？
- 对应路线下，第一条可执行的命令或脚本改动应该是什么？
- 是否还有其他更小成本的验证（例如快速确认 `grasp_instructions` 的官方用法）值得先做？
- 哪些点应保持 `Unknown / To Verify`，不要自行补全？

## 项目一句话

`Grasp‑Anything++` 上 language‑driven grasp detection；输入 RGB + 语言 prompt，输出 `(x,y,w,h,θ)`；目标交付 GitHub 仓库 + ≤2 页 CVPR 英文论文。Goal：`GOAL-001`，phase `solution-research`。

## 当前项目背景

- 项目目录：`/home/tbl/Project/视觉语言抓取作业`
- 当前分支：`main`，未配置远端，无 GitHub push
- 工作全部在 conda env `grasp-lgd`（Python 3.10.21）中进行
- 网络代理：本机 `127.0.0.1:10808`
- 项目状态机：active run，task_id `TASK-001`，next_action `"Await user/GPT decision: expand smoke fixture to 5-10 real stems or start Proposed Method design."`

## 已确认事实（带证据状态）

### Phase‑1 调查报告（candidate）
- HF plusplus = `grasp_instructions/.pkl` + `grasp_label_positive/.pt` + `grasp_label_negative/.pt` + `part_mask/.npy`；每行 GT = `[quality, x, y, w, h, theta_deg]`，代码内部 `[y, x]`、角度取负转弧度；一个 instruction → 多 positive grasps；negative 主流 baseline 未消费；`part_mask` 主流 baseline 未消费。
- LGD baseline 主链：`utils/data/grasp_anywhere_data.py` + `utils/data/language_grasp_data.py::LanguageGraspDatasetBase` → models `lgrconvnet3 / lggcnn / lgdm` → loss/dense‑map → `inference/post_process.py` + `utils/dataset_processing/evaluation.py::calculate_iou_match`（IoU>0.25 且 |Δθ|<30°）。
- 官方代码期望 `positive_grasp/*.pt` + `prompt/*.pkl`，且 `get_prompts` 实际 encode `queries[obj_id]`，与 HF 当前 plusplus 文件名不直接对齐。
- 详细证据见 `docs/technical-investigation-report.md` 与 `research/hf-zip-evidence/*.bin`。

### Smoke chain（valid，`EV-20260828-smoke-chain-runs`）
- 真实样本 stem：`805944ac6070b2c8f52a2ef228c9b660e116af1221284245dfa4930c8be865a6_0_1`
  - `image/<scene>.jpg`：416×416 RGB
  - `grasp_instructions/<stem>.pkl`：字符串 `"Pick up apple by its flesh."`
  - `grasp_label_positive/<stem>.pt`：`(5,6) float32`
  - `grasp_label_negative/<stem>.pt`：`(7,6) float32`
  - `part_mask/<stem>.npy`：未获取（该 stem 不在已有 tail index，且 baseline 不消费）
- Adapter：`data_utils/grasp_anything_pp.py::GraspAnythingPPSampleDataset`，只改数据入口，官方模型/评估不动。
- Smoke 输出（CPU，`scripts/smoke_test.py`）：
  - input `(1,3,224,224)`
  - GT dense maps `[(1,1,224,224)] ×4`
  - forward 四张 `(1,1,224,224)`
  - loss `1.656027`、backward 成功
  - post‑process `q=(224,224) angle=(224,224) width=(224,224)`
  - 评估 `correct: False`（未训练，符合预期）
- 修复：官方 `LGD-main/inference/post_process.py` 对 requires‑grad tensor 直接 `.numpy()` → 改为 `.detach().cpu().numpy()`。
- LGD 官方代码 + numpy 2 兼容补丁：`np.float → float`、`np.int → int`，影响 6 个文件。
- 决策记录：`DEC-002`（仅在数据入口做 adapter，模型/评估不污染，baseline / proposed method 区分清晰）。
- 任务记录：`TASK-002` 已 `done`，handoff `next_action` 指向“扩 5~10 个 stem 还是进入 method 设计”。

## 期望行为 vs 实际行为

- 期望：smoke chain 全绿；shape 与 dense‑map 假设一致；adapter 不污染官方管线。实际：全部一致，pass。
- 期望：conda env 是独立的可复现环境。实际：**不是**；`grasp-lgd` env 缺少 `numpy/torch/torchvision/scipy/matplotlib/PIL`，它们来自用户目录 `~/.local/lib/python3.10/site-packages`（INSTALLER=`pip`，安装时间 2026‑05‑30 / 06‑09 / 07‑23，远早于 env 创建）。`site.ENABLE_USER_SITE=True`，`sys.path` 中 user‑site 顺序在 env site‑packages 之前。
- 期望：`part_mask` 已取回。实际：未取回，本链路不依赖，不阻塞。

## 复现 / 验证命令

```bash
# 1) 复跑 smoke chain
/home/tbl/miniforge3/envs/grasp-lgd/bin/python scripts/smoke_test.py

# 2) 复看样本字段
/home/tbl/miniforge3/envs/grasp-lgd/bin/python scripts/inspect_sample.py

# 3) 关键证据
cat .project-log/loop/evidence-index.yaml
cat .project-log/loop/handoff.md
git log --oneline -n 5
```

执行后预期打印：四张 dense map `(1,1,224,224)`、loss ≈ 1.656、`correct: False`、part_mask 路径返回 `None`。

## 环境 / 依赖 / 接口约束

- Python：`/home/tbl/miniforge3/envs/grasp-lgd/bin/python`（3.10.21）
- conda env 包：`openai-clip / opencv-python-headless / scikit-image / ftfy / imageio / setuptools / pip / wheel / packaging` 等
- 用户目录包：`numpy 2.2.6 / torch 2.12.0+cu126 / torchvision 0.27.0+cu126 / scipy 1.15.3 / matplotlib 3.10.9 / Pillow 12.2.0`
- ROS 干扰：`PYTHONPATH=/opt/ros/humble/lib/python3.10/site-packages:…`
- 对外网络：`https://hf-mirror.com/datasets/...` 可用，需 Bearer token（`HF_TOKEN` 或 `~/.cache/huggingface/token`）
- 代理：`127.0.0.1:10808`；`git push` 失败时使用该代理重试
- 依赖大小：torch/torchvision wheel 约 ~3 GB，全套 Grasp-Anything++/base 约 87 GB，本机测试样仅需 <1 MB

## 已尝试 / 已观察

- 用 HTTP Range 抓单个真实样本：`scene.jpg` 与 `instructions/positive/negative` 成功；`part_mask` 因 stem 不在 tail index 跳过。
- 单样本 dense map → `lgrconvnet3` → loss → backward → post_process → `calculate_iou_match` 全链路 `OK`；`correct=False` 来自未训练模型。
- 官方 `post_process.py` 的 detach 修复后回归成功。
- LGD-main + numpy 2 兼容补丁后 import/运行无 `np.float` / `np.int` 错误。

## 仍未确认 / 需要 GPT 判断的点

- **`grasp_instructions` 是否直接 encode 为模型 query**。当前 adapter 把 `.pkl` 字符串同时作为 `prompt` 与 `query`；官方 reproduction 语义仍是 `Unknown / To Verify`。
- 是否应该让 baseline 在 smoke 中走“`scene_description` + `object name`”而非直接 `.pkl` 字符串。
- 官方 train 时是否真正使用 `lgrconvnet3` 224×224，还是用了 332×332（涉及 `lggcnn / lgdm`）。
- `part_mask` 在 plusplus 训练里是否被另一条网络（如 `grasp_det_seg`）消费；如果仅本任务不消费，是否需要忽略。

## 推荐的最小下一步（请 GPT 校正）

候选 A（扩 stem）：
1. 选定另外 4–9 个 stem（建议延续同 scene 内或换 scene，但避免 65 GB image_part）；
2. 对每个 stem 抓 `<scene>.jpg` + instruction + positive；
3. 把 `smoke-data` 改为 `stems.txt` 列表，批量跑 `scripts/smoke_test.py` 并保存可视化；
4. 写出 `scripts/batch_smoke.py`，生成 `outputs/qualitative/` 与 `metrics.json`。

候选 B（method）：
1. 在 `data_utils/grasp_anything_pp.py` 与 `inference/models/lgrconvnet3.py` 之间插入 “language‑conditioned fusion” 改动；
2. 在 `models/loss` 增加一项语言对齐 loss；
3. 准备一个 `configs/ours.yaml` 与 `train.py`，跑 1–2 个 epoch 验证 pipeline；
4. 在论文里明确标出“Baseline / Ours / Ablation”。

候选 C（环境）：
1. 新建 `conda create -n grasp-lgd-clean python=3.10 -y`；
2. `python -m pip install torch==2.12.0+cu126 torchvision==0.27.0+cu126 numpy==2.2.6 matplotlib==3.10.9 scipy==1.15.3 pillow==12.2.0`；
3. `pip install openai-clip opencv-python-headless scikit-image`；
4. 用 `PYTHONNOUSERSITE=1` 或 `python -s` 禁用 user‑site；
5. 在新 env 中重新跑 `scripts/smoke_test.py`，确认与当前输出一致。

## 风险与说明

- 当前 smoke chain 只证明 1 个 stem 可执行，未证明 stem 之间的分布差异；扩 stem 能提高 qualitative 可信度但不会显著改进 evaluation 数字。
- 直接进入 method 设计风险较高（small dataset + short time），但论文 story 可能更强（明确 baseline vs ours）。
- 环境重建最稳妥，可能影响 local workflow 一两天，但能保证 GitHub 复现与 future 实验一致。
- 用户当前已声明工作全部在 `grasp-lgd` env 中；任何环境切换都需要用户同意。

## 不要做的事（避免反复）

- 不下载 Grasp‑Anything++ / Grasp‑Anything 完整 87 GB；
- 不枚举大 zip 全量 central directory；
- 不进入 `lgdm` / `diffusion` 的端到端训练；
- 不把 `grasp_instructions` 字符串用法“替作者解释”成事实；
- 不修改官方 LGD 模型或评估链路（已通过 adapter 隔离）。
