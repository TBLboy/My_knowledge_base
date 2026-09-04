# Progress

> 面向人的阶段进度摘要。维护规则：
> - **最新在最上**：按日期倒序排列，最新阶段段落位于文件顶部，旧段落依次向下。
> - **头部快照**：顶部“当前状态”区块是稳定入口，每次更新时覆盖，不追加旧版本。
> - **超限归档**：文件超过约 50-100 KB 时，把旧段落移动到 `.project-log/docs/archive/`，主文档只保留最近内容。
> - **单一事实源**：本文件是快速摘要；精确当前状态与下一步以 `.project-log/loop/handoff.md`、`.project-log/loop/active-run.yaml` 为准。
> - **机器文件不手工重排**：`loop/events.jsonl`、`loop/active-run.yaml`、`loop/handoff.md`、`verification/evidence.yaml` 由运行时维护，不做手工重排或改写。

## 当前状态

- 当前阶段：implementation
- 当前任务：TASK-009/010（论文 PDF 与 GitHub 发布）
- 当前状态：论文 2 页 PDF 与 GitHub 发布已完成；最终 PDF 命名等待用户姓名
- 最近验证：
  - EV-20260904-lambda-sweep：candidate（0.0=653.7，
    0.01=662/single，0.05=678.0 repeat mean，0.1=605.3）
  - EV-20260904-lsar-final-second-seed：candidate
    （seed43 split42 single 666/2000；repeat mean 661.7）
  - EV-20260904-sampling-sensitivity-final-005：candidate
    （fixed 200 subset；10-step=65，50-step=67）
  - EV-20260904-final-005-paired-visual：candidate
    （6 samples，含 highlighter/marker cap/apple stem/keychain 等）
  - 最终实验汇总：`research/results/final_method_summary.md`
  - 论文源文件与 PDF：`research/paper/main.tex` /
    `research/paper/main.pdf`，`pdfinfo` 验证 2 页
  - 架构图：`research/paper/architecture.pdf`
  - 论文定性图：`research/paper/qualitative_paper.png`
  - GitHub 发布：<https://github.com/TBLboy/language-driven-grasp-detection>
  - 最终交付摘要：`research/results/paper_and_repo_summary.md`
  - 最终交付审计：`.project-log/docs/final-delivery-audit-20260904.md`
  - README 命令已改为 conda 激活后的通用 `python` 写法
  - EV-20260902-larger-subset-3k-ready：valid（2968 stem / 1010 scene / RGB 全存在）
  - EV-20260902-larger-subset-baseline：candidate（mean 152.0/594）
  - EV-20260902-larger-subset-lsar：candidate（mean 179.0/594）
  - EV-20260903-subset-5k-ready：valid（5000 stem / 5000 scene / RGB 5000/5000）
  - EV-20260903-larger-subset-baseline-5k：candidate（single 211/1000；
    repeat mean 202.7）
  - EV-20260903-larger-subset-lsar-5k：candidate（single 299/1000；
    repeat mean 309.7）
  - EV-20260903-subset-10k-ready：valid（10000 stem / 10000 scene /
    RGB 10000/10000）
  - EV-20260903-subset-10k-baseline：candidate（single 449/2000；
    repeat eval mean 470.0 / std 10.82）
  - EV-20260903-subset-10k-lsar-full：candidate（single 625/2000；
    repeat eval mean 605.3 / std 18.88）
  - EV-20260903-subset-10k-paired-visual：candidate（6 samples 含
    baseline fail / LSAR ok 的 part-level 案例）
  - EV-20260903-sampling-sensitivity：candidate（200-sample subset；
    LGDM 10/50 = 39/44，LSAR-full 10/50 = 55/61，
    LSAR-no-aff 10/50 = 57/65）
  - EV-20260903-subset-10k-lsar-no-aff：candidate（single 643；
    repeat mean 653.7 / std 6.51）
  - EV-20260903-subset-10k-paired-visual-no-aff：candidate
    （baseline vs LSAR-no-aff 6 samples）
  - EV-20260902-lsar-scale-sweep：candidate（0.01/0.02/0.05/0.10 完成）
  - EV-20260902-lsar-affordance-ablation：candidate（full 41.67 vs no-aff 18.67）
  - EV-20260902-lsar-affordance-visual：candidate（3 样本 heatmap overlay）
  - EV-20260902-lsar-minimal：candidate（none/plain-y/lsar 三条件可对比）
  - EV-20260902-subset-1000-experiments：candidate（正式三条件 + 调优 +
    重复评估 + 定性图完成）
  - EV-20260902-lsar-affordance-aux：candidate（1-batch 正向反向通过；
    `scale=0.153`，aff_head/proj 非零）
  - EV-20260902-subset-1000-ready：valid（1000 stem / 1000 scene；
    RGB 1000/1000）
  - EV-20260902-clean-lgdm-train：candidate（100 sample training/log/checkpoint/eval 完成）
  - EV-20260902-lgdm-tensorflow：candidate（official y 无梯度；inject-y 有有限梯度）
  - EV-20260902-diffusion-smoke：valid
  - EV-20260828-smoke-chain-runs：valid
  - EV-20260828-env-self-contained：valid
- 下一步（gate）：
  1. GitHub 仓库创建并推送
  2. 验证 paper URL 与 raw PDF HTTP 200
  3. 等待用户提供 FirstName / LastName 后生成最终命名 PDF

## 2026-09-03 Stage K-M：10k subset Baseline vs Ours 与后续实验

- 状态：进行中
- 完成内容：
  - `train_subset_10k.tsv`：10000 stems / 10000 unique scenes，
    RGB 10000/10000，scene-disjoint split by construction
  - LGDM baseline 15 epochs：single eval `449/2000 correct`
  - LSAR-full 15 epochs：single eval `625/2000 correct`
  - 修复同目录双进程冲突：停止后启动的 resume 进程，保留原始 seed 42
    训练进程直至完成；`args.json` / `eval_metrics.json` /
    `training_log.jsonl` / `last.pt` 均验证完整
  - `lsar_no_aff` 训练已启动（同一 10k split、15 epochs、seed 42）
  - LGDM 与 LSAR-full 各 3 次 repeat eval（seed 100/101/102）完成：
    LGDM `473/479/458`，mean 470.0，std 10.82；
    LSAR-full `601/626/589`，mean 605.3，std 18.88
  - paired qualitative 可视化完成：6 个 part-level validation 样本，
    含 pen cap / apple stem / fork handle 等 baseline fail / LSAR ok 案例
  - 10/50-step sampling sensitivity 完成（固定 200-sample subset）：
    LGDM 10=39 / 50=44；LSAR 10=55 / 50=61
  - `lsar_no_aff`（same config，lambda_aff=0）训练完成，
    single eval 643/2000；3 次 repeat eval `647/660/654`，
    mean 653.7，std 6.51
  - `lsar_no_aff` paired qualitative 可视化完成：
    `outputs/lgdm_10k/paired_visuals_no_aff/paired_qualitative.png`
  - sampling sensitivity：LGDM 10/50 = 39/44；
    LSAR-full 10/50 = 55/61；LSAR-no-aff 10/50 = 57/65
- 验证与限制：
  - 三模型 repeat mean 顺序：LSAR-no-aff > LSAR-full > LGDM；
    no-aff 高于 baseline 约 184/2000，也比 LSAR-full 高约 48/2000
  - 10k 上显式 affordance MSE 未带来稳定收益，甚至降低性能；
    与 1000-scale 的 no-aff 退化结论相反，需要按 10k 结果更新论文故事
  - 这是 10k unique scene / 15 epochs 的实验，仍不是全数据集最终声明
- 下一步：README 与 `research/results/10k_validation_summary.md`
  已汇总；候选方法决策为 LSAR-no-aff，保留 LSAR-full 作 ablation；
  已生成外部决策简报
  `.project-log/docs/context-briefing-20260903-10k-method-decision.md`；
  外部 GPT 回复已记录；当前执行 `lambda_aff` sweep：
  `lambda_aff` sweep 完成；最终配置 `lambda_aff=0.05`
  - seed42：single `686/2000`，repeat mean `678.0`
  - seed43（`split-seed=42`）：single `666/2000`，
    repeat mean `661.7`
  - 已新增 `--split-seed` 解耦数据切分与训练 seed

## 2026-09-03 External GPT review accepted and lambda sweep started

- 外部 GPT 建议固定 LSAR-no-aff 为最终方法。
- 同意不再改 LSAR 结构，不引入 Transformer / Flow Matching。
- 当前执行 Step 1：`lambda_aff={0.01,0.05}` 两个缺失 sweep 点。
- 后台任务：
  - bash PID：`1985652`
  - `lambda_aff=0.01` Python PID：`1985653`
  - 日志：`outputs/logs/lambda_sweep_10k.log`
  - 输出：`outputs/lgdm_10k/lambda_aff_0.01`、
    `outputs/lgdm_10k/lambda_aff_0.05`
- 后续：汇总 0 / 0.01 / 0.05 / 0.1，固定最优配置；
  补最终模型第二训练 seed，再进入论文材料。

## 2026-09-03 Stage G-J：5000 样本大 subset Baseline vs Ours

- 状态：完成（实验中，非最终论文性能）
- 完成内容：
  - 本地 RGB 归档列出 994860 个 scene
  - `prepare_training_subset.py` 新增 `--scene-list`
  - `train_subset_5k.tsv`：5000 stems / 5000 unique scenes / RGB 5000/5000
  - Baseline（none，15 epochs）：single 211/1000，
    repeat mean 202.7 / std 4.93
  - Ours（LSAR scale=0.01 + lambda_aff=0.1，15 epochs）：
    single 299/1000，repeat mean 309.7 / std 3.51
  - 可视化：`outputs/lgdm_5k/visuals_affordance/qualitative.png`
- 验证与限制：
  - Ours 比 baseline repeat mean 高约 107/1000，3 次采样均更高
  - 数据覆盖 5000 unique scene / 15 epochs，不是最终结论
- 下一步：保留 LSAR；提交 5k 结果；可选继续 10k 或进入最终训练/论文材料

## 2026-09-02 5k/10k subset plan 已写入

- 本地 RGB split 完整，无需重新下载
- 5k/10k plan：`docs/lsar-larger-subset-5k10k-plan-20260902.md`
- 先提交 3k Stage A-E，再准备更大 subset 并训练 Baseline vs Ours

## 2026-09-02 Stage 3：2968 样本大 subset Baseline vs Ours

- 状态：完成（实验中，非最终论文性能）
- 完成内容：
  - `prepare_training_subset.py` 新增 `--image-dir` 与 `--allow-same-scene`
  - 生成 `research/smoke-data/train_subset_3k.tsv`：2968 stem /
    1010 unique scenes / 每 scene 最多 3 个 / RGB 100% 存在
  - Baseline（none，15 epochs）：单次 eval 151/594，
    repeat eval mean 152.0，std 5.57
  - Ours（LSAR scale=0.01 + lambda_aff=0.1，15 epochs）：
    单次 eval 185/594，repeat eval mean 179.0，std 1.73
  - Stage D 可视化：spoon handle / fork handle / apple stem
    4 样本 affordance overlay 图
- 验证与限制：
  - Ours 比 baseline repeat mean 高约 27/594，且标准差不重叠
  - 数据仅覆盖 1010 scene / 2968 stem，15 epochs，不是最终结论
- 下一步：保留 LSAR，暂不优化结构；待用户确认是否继续扩 scene/subset

## 2026-09-02 Stage 2.5：LSAR scale sweep + affordance ablation + 可视化

- 状态：完成（诊断实验，非性能结论）
- 完成内容：
  - Task A：固定 scale 0.01/0.02/0.10 新跑，0.05 复用 lsar_tuned
  - 单次 eval：0.01=43，0.02=38，0.05=39，0.10=31
  - Task B：scale=0.01 固定，LSAR-full 与 LSAR-no-aff 对照
  - 3 次 10-step 重复 eval：full 45/38/42（mean 41.67），
    no-aff 21/17/18（mean 18.67）
  - Task C：`visualize_lgdm_samples.py` 支持 `--sample-stems` /
    `--show-affordance`，生成 spoon handle / apple stem / fork handle
    heatmap 叠加图
  - 新增 `research/scripts/eval_lgdm_checkpoint.py`
- 验证与限制：
  - LSAR-full 重复均值高于官方 baseline 约 4.67/200，但标准差约 3.51，
    不构成显著结论
  - 去掉 affordance loss 后 LSAR 明显退化，说明空间监督不可省略
  - 1000 样本 / 20 epochs 仅用于诊断
- 下一步：正式 subset 训练，Baseline vs Ours，再进入论文阶段

## 2026-09-02 Stage 2：1000 样本正式实验与 LSAR 调优

- 状态：完成（实验与可视化，非最终论文）
- 完成内容：
  - 800 train / 200 val / 20 epochs 三条件实验：
    `none` 33/200，`plain-y` 37/200，`lsar` 13/200
  - `lsar.scale` 学到 0.224 导致退化；新增固定 scale 支持
  - `lsar_tuned`（scale=0.05 固定）39/200
  - 3 次 10-step 采样重复评估均值：none 37.0 / plain-y 40.0 /
    lsar_tuned 38.33
  - 新增 `eval_lgdm_checkpoint.py`、`summarize_experiments.py`、
    `visualize_lgdm_samples.py`
  - 定性图 `research/assets/qualitative_lsar_tuned.png`
- 验证与限制：
  - `lsar_tuned` 高于官方 baseline，但与 plain-y 接近，未证明显著优势
  - 1000 样本、20 epochs、10-step sampling，不作性能结论
- 下一步：GitHub 仓库 + Paper

## 2026-09-02 Stage 1.6：LSAR affordance 辅助监督与 1000 样本子集

- 状态：工程完成，正式实验待跑
- 完成内容：
  - `models/lgdm_lsar.py`：LSAR 新增 `proj` + `aff_head`，保存
    `affordance_map (B,1,19,19)`
  - `research/scripts/train_lgdm_clean.py`：新增
    `--lsar-affordance-weight 0.1`
  - 1-batch verif：normal forward/backward，`affordance=0.0367`
  - 100-sample `lsar_aff`：20 epochs / 10-step eval 4/20
  - `research/smoke-data/train_subset_1000.tsv`：1000 unique scene，
    与 RGB 一一对应
- 验证与限制：
  - 100 样本上精度仍 4/20，不能作性能结论
  - affordance MSE 稳定在约 0.021；是否有实际收益需要 1000 样本实验验证
  - 1000 样本三条件实验未启动
- 下一步：跑 `none / plain-y / lsar` formal experiment，随后生成
  quantitative/qualitative 材料

## 2026-09-02 Stage 1.5：LSAR V1 实现与最小实验

- 状态：完成（工程实验，非性能结论）
- 完成内容：
  - 新增 `models/lgdm_lsar.py`：`SpatialAffordanceRefinement` +
    `LGDMWithConditioning`
  - `train_lgdm_clean.py` 新增 `--condition-mode none|plain-y|lsar`
  - 用同一 100 stem / 80-20 split / 20 epochs / 10-step eval 跑三条件
- 验证与限制：
  - none 4/20，plain-y 4/20，lsar 4/20
  - 零 scale 初始化导致模块不学习；改为 `scale=0.1`，训练后为 0.158
  - 100 样本结果不用于性能声明
- 下一步：决定是否加入 LSAR affordance auxiliary loss，再进入正式 subset 实验

## 2026-09-02 Stage 1：Clean LGDM 100-sample sanity 完成

- 状态：完成（工程 sanity，非性能实验）
- 完成内容：
  - `prepare_training_subset.py` 生成 100 个不同 scene 真实 stem 校验清单
  - `extract_rgb_subset.sh` 从 65GiB split zip 选样解压 100 张 RGB
  - `train_lgdm_clean.py` 实现 Clean LGDM objective，diffusion loss 真正
    backward，且不再重复 dense pos MSE
  - 80 train / 20 val，batch size 2，20 epochs，40 batches/epoch
  - 训练日志、checkpoint、10-step sampling eval 保存到
    `outputs/train_lgdm_clean_100/`
  - `--resume` 加载 checkpoint 通过
- 验证与限制：
  - eval `5/20 correct`；未训练足够数据，不是精度结论
  - checkpoint 含 optimizer state，约 2.1GB，不提交 Git
  - 官方 contrast 项主导 clean loss，后续实验需检查缩放
- 重要发现：
  - `image_atts` 实际为全 1 mask，不是语言注意力图
  - 官方 `y` 分支未接入视觉特征，无梯度
  - `--inject-y` probe 证明 `y_view (8x19x19)` 可加进 `conv3` 且梯度有限
- 下一步：实现 LSAR V1 于 `y -> y_flatten -> conv3` conditioning 分支

## 2026-09-02 Stage 1：LGDM diffusion baseline smoke 通过

- 状态：完成（`2/2 OK, 0 FAIL`）
- 完成内容：
  - `grasp-lgd` 安装 diffusion 依赖：transformers 4.28.1 / timm 0.6.13 /
    ruamel.yaml 0.17.21 / tensorboardX / torchsummary
  - 新增 `research/scripts/diffusion_smoke.py`
  - 真实 stem 跑通 LGDM：dataset -> dense maps -> forward -> loss ->
    backward -> 10-step sample -> post-process -> IoU evaluation
  - 更新 `environment.yml` 与环境快照
- 验证与限制：
  - 峰值 GPU 约 2.51 GiB；未训练，`correct=False` 符合预期
  - 未跑完整 1000 步 sampling，未跑完整训练
- 重要发现：
  - 官方训练代码只对 dense-map loss backward，diffusion loss 未 backward
  - 官方 README 的 `--network lgd` 未注册，实际名称为 `lgdm`
- 下一步：确认 diffusion baseline 训练入口，开始 100 sample sanity

## 2026-08-28 Proposed Method LSAR 概念记录

- 状态：方案已存档，尚未编码
- 完成内容：
  - 完整方法论已写入 [proposed-method-LSAR.md](/home/tbl/Project/视觉语言抓取作业/.project-log/docs/proposed-method-LSAR.md)
  - `DEC-005`：确定 LSAR 为 Proposed Method
- 验证与限制：
  - 暂无代码与实验数据；继续 batch smoke / 语义核对后再做实现选择
- 下一步：gate ② batch smoke → gate ③ 语义核对 → LSAR 编码实现

## 2026-08-28 gate ① 环境自包含完成

- 状态：完成（self-contained 验证通过）
- 完成内容：
  - 持久化 `PYTHONNOUSERSITE=1`，`ENABLE_USER_SITE=False`
  - 缺失包：numpy / scipy / matplotlib / Pillow / openai-clip / opencv-python-headless / scikit-image / tqdm / regex / ftfy 装进 env
  - torch / torchvision / nvidia_* / cuda_* / triton 从 ~/.local 拷入 env
  - 生成 `requirements.txt`（216 行）、`environment.yml`（91 行）
  - `PYTHONNOUSERSITE=1 scripts/smoke_test.py` 完整通过：`loss 1.656031 / correct: False`
  - CUDA 可用：torch 2.13.0+cu130，device_count=1
- 验证与限制：
  - env 真正独立；`sys.path` 不再含 `~/.local`
  - 当前 torch 是从 user-site 拷贝的二进制，等网络恢复再换官方 wheel
- 下一步：gate ② batch smoke（5~10 个不同 scene 真实 stem），等 grasp_label_positive.zip 下载完成后启动

## 2026-08-28 路线图记录

- 状态：路线图已记录，等待授权启动 gate ①
- 路线顺序：
  1. 环境自包含（C‑lite）：在 `PYTHONNOUSERSITE=1` 下让 `grasp-lgd` env 独立跑 smoke，导出 requirements
  2. batch smoke：本地 5~10 个不同 scene 真实 stem 跑 `scripts/batch_smoke.py`，输出 metrics + 可视化
  3. 官方 instruction 语义核对（≤1h）：paper / dataset card / 官方 train code
  4. 退出 solution-research，进入 Proposed Method 设计
  5. 最小训练 sanity → 正式 subset 训练 → table + 可视化
- 验证与限制：
  - 当前 smoke chain 仅证明单 stem 可执行，扩 stem 是工程验证，不追求 accuracy
- 下一步：用户授权后启动 gate ① 环境自包含验证

## 2026-08-28 真实样本 Smoke Test

- 状态：完成（链路执行证据为 valid）
- 完成内容：
  - 用 HTTP Range 提取真实 `scene.jpg` + instruction + positive/negative `.pt`
  - 将 fixture 放入 `research/smoke-data/`
  - 实现 `data_utils/grasp_anything_pp.py` 最小数据适配器
  - 跑通 `lgrconvnet3` forward、loss、backward、post-process、IoU evaluation
  - 修复官方 `post_process_output` 对 requires-grad tensor 的直接 `numpy()` 调用
- 验证与限制：
  - 真实 instruction：`Pick up apple by its flesh.`
  - positive `(5,6)`，negative `(7,6)`，四张 dense map 均为 `(1,1,224,224)`
  - 未训练，`correct: False` 符合预期；`part_mask` 未纳入 fixture
- 下一步：
  - 视用户/外部 GPT 决策扩样本或进入方法设计

## 2026-08-28 第一阶段技术调查

- 状态：完成（报告证据为 candidate）
- 完成内容：
  - 将论文、官方代码、数据样本和 HF zip 证据归档到 `research/`
  - 确认 Grasp-Anything++ 文件结构、体积、样本格式与 split
  - 确认 `.pt` GT 行格式、角度单位、正负标签用途
  - 追通官方 LGD DataLoader、模型、loss、decode、evaluation 主链
  - 标记官方代码与 HF 发布的目录/instruction 读取不一致
- 验证与限制：
  - 实际读样本文件与 HF API
  - 未下载完整数据，未跑端到端训练
- 下一步：
  - plusplus sample alignment smoke test
  - 最小 subset forward/loss/eval
  - 之后再设计 Proposed Method

## YYYY-MM-DD 阶段标题

- 状态：
- 完成内容：
- 验证与限制：
- 下一步：

<!--
旧段落按日期倒序向下追加；超过约 50-100 KB 时归档到
`.project-log/docs/archive/`，归档文件按日期可检索。
-->
