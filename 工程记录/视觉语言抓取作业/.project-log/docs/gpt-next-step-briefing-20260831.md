# Language-Driven Grasp Detection 项目简报（2026-08-31）

## 1. Goal & Exact Question

- 项目总目标（GOAL-001）：基于 Grasp-Anything++ 实现图像 + 自然语言指令 → 2D 抓取矩形的可训练、可评估、可提交流水线，并产出 2 页 CVPR 英文论文和 GitHub 仓库。
- 当前阶段：solution-research → engineering-landing 的边界，环境自包含已通过 gate ①，等待数据就绪后进入 batch smoke（gate ②）。
- **请你回答的具体问题**：
  1. 在 `image_part_ab`（剩余 ~28 GiB / 28.5 GiB，仍在下载）尚未完成时，哪些与 RGB无关的工作可以现在并行推进？优先级如何？
  2. 当 `image_part_ab` 完成后，最安全的合并、识别与对齐流程应该是怎样的（合并 → file判定 → 解压 → scene抽样验证）？有什么常见坑要避免？
  3. 在不修改官方 LGD 模型/评估链路的前提下，gate ② batch smoke（5~10 个真实 stem）应当包含哪些最小检查项？instruction+positive 部分可以提前跑吗？

## 2. System & Project Background

- 仓库：`/home/tbl/Project/视觉语言抓取作业`，个人仓库（`git init`），分支 `main`。
- AGENTS.md 提示所有工作统一在 conda env `grasp-lgd` 中完成，外网可走 10808 代理；环境已经 self-contained（DEC-004，`PYTHONNOUSERSITE=1`）。
- 关键决策（来自 `.project-log/decisions/decision-log.yaml`）：
  - **DEC-001**：数据集从 `hf-mirror.com/datasets/airvlab/.../resolve/main`拉取，本机 HF token 放在 `~/.cache/huggingface/token`，脚本不把 token 写到命令行参数。
  - **DEC-002**：只在数据入口做最小 adapter，模型/评估保持官方。
  - **DEC-003**：路线 = 环境自包含 → batch smoke → 语义核对 → 退出 solution-research → Proposed Method。
  - **DEC-004**：env 已 self-contained；后续只补官方 wheel。
  - **DEC-005**：plusplus zip 自带同名顶层目录，验证脚本与后续 loader 指向嵌套子目录。
- 数据范围（DEC-001 锁定）：只下载 `grasp_instructions.zip`、`grasp_label_positive.zip`、基础 RGB 两个 part。**不下载** negative labels、part mask、scene description、object-level mask、object-level grasp labels。
- 当前数据目录（`/mnt/data/grasp-anything-lgd/data/`）：

```text
raw/
  download-manifest.tsv
  grasp-anything-pp/
    grasp_instructions.zip    #1,544,210,262 B  ok
    grasp_label_positive.zip  # 3,949,367,278 B  ok
  grasp-anything/
    image_part_aa             # 34,359,738,368 B ok
    image_part_ab             # 1.3 GiB / 28.5 GiB download-interrupted（manifest 多次记录 0 字节中断）
processed/
  grasp-anything-pp/
    grasp_instructions/grasp_instructions/*.pkl     # ~1.4M 文件, ~17 GiB
    grasp_label_positive/grasp_label_positive/*.pt  # ~1.4M 文件, ~18 GiB
```

- 已存在的脚本（`research/scripts/` 与 `scripts/`）：
  - `download_grasp_anything_data.sh`（`--check` / `--download`），使用 `curl -C -` 续传；预检通过 `4/4 OK`。
  - `verify_downloaded_dataset.py`，5样本 instruction ↔ positive 对齐脚本，最新运行 `5/5 samples aligned`。
  - `inspect_sample.py`、`list_remote_zip.py`、`remote_zip.py`（不下载 zip即可列举成员的 Range工具），都已存在。
  - `smoke_test.py`（DEC-003 gate ① 后已能跑通单样本 forward/loss/backward/post-process/eval）。

## 3. Expected vs Actual Behavior

| 维度 | 期望 | 实际 |
| --- | --- | --- |
| 环境 | `PYTHONNOUSERSITE=1` 下仍可运行官方 loader | 已 self-contained；`grasp-lgd` env 中 torch 2.13.0+cu130 可用 |
| 数据 |4 个核心文件按 DEC-001 完整下载 | 3/4 完成，`image_part_ab` 仍0.2% |
| Annotation 对齐 | 随机5 个 stem 的 instruction 与 positive GT 一一对应 | `5/5 aligned`，pkl 是 str、pt 是 `[N,6] float32` |
| 下载策略 | 断点续传 + 字节数校验 | 脚本使用 `curl -C -` + `record_manifest`，中断后写 `download-interrupted` 条目 |

## 4. Reproduction & Exact Evidence

- `download-manifest.tsv` 节选（截取最近 4 行）：

  ```text
  2026-08-31T06:08:35Z  image_part_aa 34359738368  34359738368  already-complete
  2026-08-31T06:08:35Z  grasp_label_positive.zip  3949367278   3949367278   already-complete
  2026-08-31T06:08:35Z  grasp_instructions.zip    1544210262   1544210262   already-complete
  ```

  （`image_part_ab` 最近一次 `download-interrupted`，actual=0；当前又有新进程在拉，文件大小已在 1.3 GiB+。）

- `verify_downloaded_dataset.py --n 5 --seed 0 --print-instruction` 输出（已记入 DEC-005）：
  - `Lift keychain by its attachments.` → `positive.shape = (5, 6)`，`dtype = float32`
  - `Take hold of comb on its material.` → `(3, 6)`
  - `Grab pencil on its eraser.` → `(4, 6)`
  - `Hold block at its material.` → `(9, 6)`
  - `Hold apple at its seeds.` → `(3, 6)`
  - 汇总：`5/5 samples aligned`

- `download_grasp_anything_data.sh --check` 输出（已记录）：
  - `mirror=https://hf-mirror.com`
  - `[OK] grasp_instructions.zip size=1544210262 bytes; resume supported (range=206)`
  - `[OK] grasp_label_positive.zip size=3949367278 bytes; resume supported (range=206)`
  - `[OK] image_part_aa size=34359738368 bytes; resume supported (range=206)`
  - `[OK] image_part_ab size=30653099134 bytes; resume supported (range=206)`

## 5. Environment, Dependencies, Interfaces, Constraints

- 操作系统：Linux，`/dev/nvme0n1p2`（`/mnt/data`，剩余 ~170 GiB），项目盘 `/dev/nvme0n1p3`（剩余 ~203 GiB）。
- 工具：`wget 1.21.2`、`curl 7.81`、`unzip`、`file`、`torch2.12 (system python) / 2.13 (grasp-lgd env)`、`python3.10`。
- conda env：`grasp-lgd`；`PYTHONNOUSERSITE=1`，已 self-contained，CUDA 可用（单卡）。
- 网络：官方 `huggingface.co` 不可达，`hf-mirror.com` 可达，已确认 mirror 必须走 `/datasets/.../resolve/main/...` 且带 token。
- 约束（AGENTS.md / DEC-002 / DEC-003 / DEC-005）：
  - 不下载 `grasp_label_negative.zip` / `part_mask.zip` / `scene_description.zip` / `mask.zip` 等额外数据。
  - 不修改 LGD 官方模型 /评估链路，只在数据入口做最小 adapter。
  - 不枚举87 GB zip 全量 central directory；要用 `list_remote_zip.py` 或 `remote_zip.py` 局部读取。
  - 数据目录默认放 `/mnt/data/grasp-anything-lgd/data/`（项目内 `data/` 也可用，但已被 `.gitignore` 排除）。

## 6. Attempts & Observed Results

- 预检 → 解压 → 5 样本对齐脚本全部跑通（DEC-001/DEC-005 已记录）。
- `unzip -o` 对 `grasp_instructions.zip` 与 `grasp_label_positive.zip` 完整解压，校验 `unzip -tq` 无错误。
- `image_part_ab` 历史上两次中断（manifest 中 `actual=0`），已手动用脚本重启；最新一次下载刚开始，已落盘 ~1.3 GiB，进程仍存活（PID 2672635）。
- 通过 `list_remote_zip.py` 与 `remote_zip.py`工具，可以在不下载整包的情况下提取中央目录元数据（已用于调研阶段）。
- gate ① 环境自包含已完成；`smoke_test.py` 单样本全链路通过（loss=1.656031），但还在等 gate ② 的 batch 数据。

## 7. Unknowns / Need Help

- **unknown**：`image_part_ab` 仍以<1 MiB/s 的速度拉（此前2 次中断），是否需要主动改走 `wget -c` 或后台 `nohup` 会话以提高稳定性？
- **unknown**：plusplus 与基础 RGB 的合并方式——image_part_aa + ab 是同一个 zip 的分段（`cat image_part_aa image_part_ab > image.zip`）还是分别打包？脚本 `download_grasp_anything_data.sh` 目前各自下载，但下载完后我们需要决定合并/解压策略。
- **need help**：gate ② batch smoke 在仅有 instruction + positive 时，能否先用占位 RGB（比如随机张量或 PIL `Image.new`）跑一遍 forward/loss/backward + post-process + IoU eval，提前暴露 shape / 数值问题？是否建议现在就做，而不是等 ab？
- **need help**：基于当前进度，下一步推荐顺序：写 `merge_image_parts.sh` + `align_rgb.py`，还是先写 `instruction_positive_smoke.py`？哪个更适合 gate ② 的最小可执行版本？

---
**写作目的**：本简报用于外部 AI 一次性消化项目状态并给出下一步建议。请按“推荐顺序 / 风险点 / 可以并行项”三类答复，不要重复事实。
