# Language-Driven Grasp Detection 项目简报（2026-09-01）

## 1. Goal & Exact Question

- **项目总目标**（GOAL-001）：基于 Grasp-Anything++ 实现图像 + 自然语言指令 → 2D 抓取矩形的可训练、可评估、可提交流水线，并产出 2 页 CVPR 风格英文论文和 GitHub 仓库。
- **当前阶段**：solution-research → engineering-landing 已完成 gate ①、gate ②、gate ③，正在退出 solution-research，准备进入 Proposed Method 设计。
- **请你回答的具体问题**：
  1. Proposed Method 的方向应该选哪一类？给出 2-3 个候选方向，附权衡与论文卖点。
  2. 在 10 个真实 stem 的 baseline 已经能跑通的情况下，下一步实验设计（最小 subset 训练 → 正式 subset 训练 → table + 可视化）应该取什么规模？是否需要先扩到 100 / 1000 个 stem 跑 sanity 再扩大？
  3. 是否需要现在就并行做“官方 instruction 语义核对（≤1h）”（DEC-003 的 gate ③）？这一项之前一直挂着。

## 2. System & Project Background

- 仓库：`/home/tbl/Project/视觉语言抓取作业`（个人仓库，`git init`，分支 `main`）。
- AGENTS.md 锁定：所有工作统一在 conda env `grasp-lgd`；外网可走 10808 代理；个人仓库不会污染协作公共仓库。
- 关键决策（来自 `.project-log/decisions/decision-log.yaml`，共 7 条）：
  - **DEC-001**：数据集从 `hf-mirror.com/datasets/airvlab/.../resolve/main` 拉取，token 放在 `~/.cache/huggingface/token`，脚本里用临时 `curl --config` 读，不把 token 写进进程参数。
  - **DEC-002**：只在数据入口做最小 adapter，模型/评估保持官方 LGD 链路不动。
  - **DEC-003**：路线 = 环境自包含 → batch smoke → 语义核对 → 退出 solution-research → Proposed Method。
  - **DEC-004**：env 已 self-contained；后续只补官方 wheel。
  - **DEC-005**：plusplus zip 自带同名顶层目录，验证脚本和 loader 指向嵌套子目录。
  - **DEC-006**：`image_part_aa` + `image_part_ab` 是同一 zip 的 split，必须 `cat` 后再 `unzip`，不能分别解压。
  - **DEC-007**：合并后只挑 batch smoke 需要的 scene jpg 解压，避免展开 60 GiB 全部图像吃光磁盘。
- 数据范围（DEC-001 锁定）：只下载 `grasp_instructions.zip`、`grasp_label_positive.zip`、基础 RGB 两个 part。**不下载** negative labels、part mask、scene description、object-level mask、object-level grasp labels。
- 当前数据目录（`/mnt/data/grasp-anything-lgd/data/`）：

```text
raw/
├── grasp-anything-pp/
│   ├── grasp_instructions.zip   1,544,210,262 B  ok
│   └── grasp_label_positive.zip 3,949,367,278 B  ok
└── grasp-anything/
    ├── image_part_aa            34,359,738,368 B ok
    └── image_part_ab            30,653,099,134 B ok
processed/
├── grasp-anything-pp/
│   ├── grasp_instructions/grasp_instructions/*.pkl
│   └── grasp_label_positive/grasp_label_positive/*.pt
└── grasp-anything/
    └── images/<scene>.jpg       10 files, ~750 KiB
```

- 关键脚本（`research/scripts/` 与 `scripts/`）：
  - `download_grasp_anything_data.sh`（`--check` / `--download`，`curl -C -` 续传）
  - `verify_downloaded_dataset.py`（5 样本 annotation 对齐）
  - `annotation_preflight.py`（10 stem：str / [N,6] / N>0 / finite）
  - `batch_smoke.py`（10 stem：dense GT + 可选 forward/loss/backward/post-process/IoU）
  - `prepare_rgb_archive.sh`（identify-only 默认；`--auto-merge` 才 cat）
  - `smoke_test.py`（单样本全链路）

## 3. Expected vs Actual Behavior

| 维度 | 期望 | 实际 |
| --- | --- | --- |
| 环境 self-contained | `PYTHONNOUSERSITE=1` 下仍能跑官方 loader | env freeze 已落到 `env/`，torch 2.13.0+cu130 / torchvision 0.28.0+cu130 / numpy 2.2.6 / skimage 0.25.2 / opencv 5.0.0 |
| 数据完整 | 4 个核心文件按 DEC-001 完整下载 | 4/4 都 ok；`download-manifest.tsv` 最后一行 `image_part_ab ... ok` |
| annotation 对齐 | instruction 是非空 str，positive GT = `[N,6]` | 10/10 OK，`5/5` 早期版本也通过 |
| RGB 拼接 | aa + ab 合并后是合法 zip，member 为 `image/<scene>.jpg` | `prepare_rgb_archive.sh --auto-merge` 合并出 65.01 GiB 的 zip，`unzip -l` 正常 |
| 真实 batch smoke | 10 stem 全部进入 forward/loss/backward/post-process/IoU | `10/10 OK, 0 SKIP-RGB, 0 FAIL` |
| disk 预算 | 不写满 `/mnt/data` | 抽出后剩余 `107 GiB`，合并文件已删 |

## 4. Reproduction & Exact Evidence

- `batch_smoke.py --stems research/smoke-data/stems.txt --image-dir processed/grasp-anything/images --cpu` 输出（节选）：

  ```text
  device: cpu, stems: 10
  [0] 8006a8dd..._1_1 -> OK loss=1.6221849918365479 correct=True
  [1] fb490f49..._1_1 -> OK loss=1.1829684972763062 correct=False
  ...
  [9] 9e323d9d..._0_1 -> OK loss=0.9163167476654053 correct=False
  summary: 10/10 OK, 0 SKIP-RGB, 0 FAIL
  ```

- `annotation_preflight.py --stems research/smoke-data/stems.txt`：10/10 OK，输出 `outputs/annotation_preflight/{report.tsv, summary.txt}`。
- `verify_downloaded_dataset.py --n 5 --seed 0 --print-instruction`：5/5 aligned（早期版本）。
- `download_grasp_anything_data.sh --check`：4/4 OK，HEAD 大小匹配 DEC-001，Range 206。
- `download-manifest.tsv` 最后一条：
  `2026-08-31T12:19:39Z image_part_ab 30653099134 30653099134 ok`
- `prepare_rgb_archive.sh --auto-merge` 输出（关键行）：

  ```text
  [prepare_rgb] AA size = 34359738368 (expected 34359738368)
  [prepare_rgb] AB size = 30653099134 (expected 30653099134)
  [prepare_rgb] evidence_ok=1 (sizes match expected, no magic header required)
  [prepare_rgb] MERGED first 32 bytes: 504b 0304 0a00 ...   (PK header)
  [prepare_rgb] MERGED listing (first 8 entries):
    image/
    image/58ca775e...jpg
    image/de1e67ba...jpg
    ...
  ```

## 5. Environment, Dependencies, Interfaces, Constraints

- 操作系统：Linux，`/dev/nvme0n1p2`（`/mnt/data`）当前 142 G used / 107 G free；项目盘 `/dev/nvme0n1p3`（root）剩约 200 G。
- 工具：`wget 1.21.2`、`curl 7.81`、`unzip`、`file`、`torch 2.13.0+cu130 / 2.12.0+cu126`、`python3.10`。
- conda env：`grasp-lgd`；`PYTHONNOUSERSITE=1`，CUDA 可用；env 已 freeze 到 `env/{environment-explicit.txt, conda-list.txt, requirements-freeze.txt, key-versions.txt}`。
- 网络：`huggingface.co` 不可直连，`hf-mirror.com` 可用；token 走 `~/.cache/huggingface/token`。
- 约束（AGENTS.md / DEC-002 / DEC-003 / DEC-005 / DEC-006 / DEC-007）：
  - 不下载 negative / part mask / scene desc / object-level mask / object-level grasp labels
  - 不修改官方 LGD 模型/评估链路，只在数据入口做最小 adapter
  - 不枚举 87 GB zip 全量 central directory；用 `list_remote_zip.py` / `remote_zip.py` Range 工具
  - 数据放在 `/mnt/data/grasp-anything-lgd/data/`，不写入项目根的 `data/`（已被 `.gitignore` 排除）
  - batch smoke 不使用假 RGB；缺 RGB 时只做 dense GT + shape/finite 检查

## 6. Attempts & Observed Results

- 4 个核心文件逐个下载：`grasp_instructions.zip` / `grasp_label_positive.zip` 各 1 轮 ok；`image_part_aa` 1 轮 ok；`image_part_ab` 多次 `download-interrupted` 后最终 `ok`。
- 用 `unzip -tq` 校验两个 plusplus zip 完整性通过。
- `image_part_aa` 是 `PK\x03\x04` 开头的 zip，`image_part_ab` 是 raw 续段；`cat aa ab > image_archive` 恢复成 65 GiB 的合法 zip，`unzip -l` 看到 `image/<scene>.jpg`。
- 只挑 stems.txt 10 个 scene 的 jpg 解压到 `processed/grasp-anything/images`，其余保留在 raw zip 内。
- batch smoke 10/10 全部进入 forward / loss / backward / post_process / IoU 流程；网络是随机初始化 baseline，loss/correct 不构成模型质量证据，但说明 engineering chain OK。
- 10 张 jpg 解压后删除 `image_archive`，`/mnt/data` 剩余 107 GiB。

## 7. Unknowns / Need Help

- **need help**：Proposed Method 候选方向与权衡（见 §1 问题 1）。
- **need help**：batch smoke 已经通过后，下一步实验规模（100 / 1000 / 全量）的策略。
- **need help**：DEC-003 的 gate ③ “官方 instruction 语义核对（≤1h）” 是否现在做。
- **unknown**：当前 baseline 在更细的 IoU/角度阈值（IoU > 0.25 且角度差 < 30°）下的真实 success rate 还没统计；`correct` 是按阈值判定的，未来要给出论文表格还需要写评估脚本汇总。
- **unknown**：是否要把 stems.txt 从 10 扩成 50 / 100，再跑一次 batch smoke 拿更稳的 baseline 数字。

---
**写作目的**：把当前状态打包给外部 AI，帮你定 Proposed Method 的下一步。请按“推荐方向 / 实验规模 / 语义核对优先级”三类答复，不要重复事实。
