# Current Session

> 会话恢复入口。维护规则：
> - **头部快照**：顶部“当前状态”区块是稳定入口，每次更新时覆盖，不追加旧版本。
> - **最新在最上**：最新一次会话写在文件最上面的会话区块，旧会话依次向下。
> - **超限归档**：文件超过约 50-100 KB 或会话区块达到约 10 条时，把旧会话区块移动到 `.project-log/docs/archive/`，主文档只保留最近内容。
> - **单一事实源**：精确当前状态与下一步以 `.project-log/loop/handoff.md`、`.project-log/loop/active-run.yaml` 为准；不要在多份长文档里维护互相矛盾的“下一步”。
> - **机器文件不手工重排**：`loop/events.jsonl`、`loop/active-run.yaml`、`loop/handoff.md`、`verification/evidence.yaml` 由运行时维护，不做手工重排或改写。

## 当前状态

- 当前阶段：implementation
- 当前目标：GOAL-001：完成 language-driven grasp detection 完整工程、2 页 CVPR 英文论文与 GitHub 仓库
- 当前任务：TASK-010/011（最终交付收尾）
- 当前状态：论文 2 页 PDF、GitHub 发布与最终命名 PDF 已完成
- 当前执行计划：`.project-log/docs/final-validation-execution-plan-20260903.md`
- 计划内容：10k 最终验证：LGDM baseline / LSAR-full / LSAR-no-aff、
  repeat eval、diffusion-step sensitivity、可视化、paper material
- 已确认事实：
  - `grasp-lgd` env 已 self-contained，`PYTHONNOUSERSITE=1` 生效，CUDA 可用
  - 阶段 0 完成：10 个不同 scene 的真实 RGB batch smoke 全链路 `10/10 OK`
  - 阶段 1 完成：官方 `LGDM` diffusion baseline 在 2 个真实 stem 上跑通
    dataset -> dense maps -> forward -> loss -> backward -> 10-step sample ->
    post-process -> IoU evaluation
  - Clean LGDM 100-sample sanity 完成：80 train / 20 val，20 epochs，
    checkpoint 可 resume，10-step eval `5/20 correct`
  - 官方 `train_network_diffusion.py` 计算 diffusion loss 但未对 diffusion
    loss 调 backward；实际更新用 dense-map loss
  - 官方 README 的 `--network lgd` 未在 `get_network` 注册，实际为 `lgdm`
  - tensor-flow 证据：`image_atts` 为全 1 mask；官方 `y` 分支无梯度；
    `y_view (8x19x19)` 注入 `conv3` 后文本分支梯度有限
  - LSAR V1 已实现，三条件 minimal 对比完成：none/plain-y/lsar 均 4/20
  - LSAR affordance auxiliary loss 已实现并通过 1-batch 验证：
    `affordance=0.0367` 非零并计入 total
  - 100-sample `lsar_aff` 20-epoch 实验完成：10-step eval 4/20；
    LSAR `scale=0.153`，`proj` / `aff_head` 权重非零，模块有学习信号
  - `research/smoke-data/train_subset_1000.tsv` 已生成：1000 stem /
    1000 unique scene；RGB 已提取 1000/1000
  - 1000-sample 正式三条件实验完成（800 train / 200 val / 20 epochs）：
    `none` 33/200，`plain-y` 37/200，`lsar`（可学习 scale）13/200，
    `lsar_tuned`（固定 scale=0.05）39/200
  - 同一 checkpoint 3 次 10-step 采样重复评估均值：
    `none` 37.0，`plain-y` 40.0，`lsar_tuned` 38.33
  - `lsar` 可学习 scale 涨到 0.224 导致退化；固定 scale 后恢复并略优于
    官方 baseline
  - 定性可视化已生成并复制到 `research/assets/qualitative_lsar_tuned.png`
  - Task A 固定 scale 扫描完成（800/200/20 epochs/10-step）：
    `0.01=43/200`，`0.02=38/200`，`0.05=39/200`，`0.10=31/200`
  - Task B affordance ablation 完成（scale=0.01 固定、同一训练配置）：
    LSAR-full 3 次重复 eval 45/38/42，均值 41.67；
    LSAR-no-aff 3 次重复 eval 21/17/18，均值 18.67
  - Task C affordance map 可视化完成：spoon handle / apple stem /
    fork handle 三个样本均已渲染 heatmap overlay
  - `research/smoke-data/train_subset_3k.tsv` 已生成：2968 stem /
    1010 unique scenes / 每 scene 最多 3 个 / RGB 100% 存在
  - Large-subset baseline（none，15 epochs）单次 eval 151/594；
    3 次 repeat eval 158/151/147，均值 152.0，std 5.57
  - Large-subset Ours（LSAR scale=0.01 + lambda_aff=0.1，15 epochs）
    单次 eval 185/594；3 次 repeat eval 180/177/180，均值 179.0，std 1.73
  - Large-subset Stage D 可视化完成：spoon handle / fork handle /
    apple stem，4 样本 affordance overlay 均渲染
  - 5k subset（5000 stems / 5000 unique scenes / 4000 train / 1000 val /
    15 epochs）完成：Baseline single 211/1000，repeat mean 202.7；
    LSAR-full single 299/1000，repeat mean 309.7
  - 5k subset 的可视化完成：apple stem、pen cap、highlighter cap、
    spoon handle 四个样本均渲染 affordance overlay
  - 10k subset 已准备：`research/smoke-data/train_subset_10k.tsv`，
    10000 stems / 10000 unique scenes，RGB 10000/10000
  - 10k LGDM baseline 完成：`outputs/lgdm_10k/none/last.pt`，
    single eval `449/2000 correct`
  - 10k LSAR-full 完成：`outputs/lgdm_10k/lsar_full/last.pt`，
    single eval `625/2000 correct`；输出文件完整
  - 10k repeat eval 完成：LGDM 3 次 `473/479/458`，mean `470.0`
    std `10.82`；LSAR-full 3 次 `601/626/589`，mean `605.3`
    std `18.88`
  - paired qualitative 可视化完成：
    `outputs/lgdm_10k/paired_visuals/paired_qualitative.png`；
    含 pen cap / apple stem / fork handle 等 baseline
    false 而 LSAR true 的 part-level 样本
  - sampling-step sensitivity（200-sample subset）完成：
    LGDM `39/200`（10-step）与 `44/200`（50-step）；
    LSAR-full `55/200`（10-step）与 `61/200`（50-step）；
    LSAR-no-aff `57/200`（10-step）与 `65/200`（50-step）
  - `lsar_no_aff` 10k 训练完成，single eval `643/2000`；
    repeat eval `647/660/654`，mean `653.7`，std `6.51`
  - 三模型 10k repeat mean 汇总：LGDM `470.0±10.8`，
    LSAR-full `605.3±18.9`，LSAR-no-aff `653.7±6.5`
  - `paired_visuals_no_aff` 已生成（与 baseline 对比）
  - 最终方法决策背景简报已写入
    `.project-log/docs/context-briefing-20260903-10k-method-decision.md`
  - 外部 GPT 回复已分析并记录：
    `.project-log/docs/gpt-review-20260903-method-and-lambda-sweep.md`；
    建议固定 `LSAR-no-aff` 并补 `lambda_aff` sweep / 第二训练 seed
  - `lambda_aff` sweep 已启动：bash PID `1985652`，
    `lambda_aff=0.01` Python PID `1985653`；
    日志 `outputs/logs/lambda_sweep_10k.log`
  - 训练顺序：`0.01` 完成后自动跑 `0.05`；
    输出 `outputs/lgdm_10k/lambda_aff_0.01` 和
    `outputs/lgdm_10k/lambda_aff_0.05`
  - 最近检查：`lambda_aff` sweep 完成；
    `0.05` 选定为最终配置
  - seed42（`split-seed=42`）：single `686/2000`，
    repeat mean `678.0`（`662/677/695`）
  - seed42 模型：`outputs/lgdm_10k/lambda_aff_0.05`
  - 第二训练 seed 修正完成：`seed=43, split-seed=42`，
    single `666/2000`，repeat mean `661.7`（`661/648/676`）
  - 第二 seed 模型：`outputs/lgdm_10k/lsar_final_lambda_0.05_seed43_split42`
  - 最终方法：LSAR + `lambda_aff=0.05`，fixed scale `0.01`
  - 最终方法 paired qualitative 图已生成：
    `outputs/lgdm_10k/paired_visuals_final_005/paired_qualitative.png`
    和 `research/assets/qualitative_10k_paired_lsar_0.05.png`
  - 最终实验结果已汇总至
    `research/results/final_method_summary.md`
  - 论文源文件完成：`research/paper/main.tex`、`main.bib`、`cvpr.sty`
  - 架构图完成：`research/paper/architecture.pdf`
  - 论文定性图裁剪完成：`research/paper/qualitative_paper.png`
  - 已安装 Tectonic 0.17.0 并编译 `research/paper/main.pdf`
  - `pdfinfo` 验证论文为 2 页，包含 Abstract / Introduction / Related
    Work / Method / Experiment / Conclusion / References
  - GitHub 仓库已发布：
    `https://github.com/TBLboy/language-driven-grasp-detection`
  - GitHub 可见性 PUBLIC，`curl -I` 返回 HTTP 200
  - 发布树 198 files / 约 33 MiB，不包含 outputs、checkpoint、大权重
  - 最终交付摘要：
    `research/results/paper_and_repo_summary.md`
  - 最终交付审计：
    `.project-log/docs/final-delivery-audit-20260904.md`
  - 顶层入口已补齐：`train.py` / `evaluate.py` / `inference.py`
  - 顶层入口已在干净发布树验证：三个 `--help` 均返回 0，
    `compileall` 通过
  - 发布仓库已推送最新提交 `9034f4a`，
    remote HEAD 已确认与本地发布树一致
  - 2026-09-04 复核：`pdfinfo` 仍为 2 页；
    GitHub repo / raw `main.pdf` / raw `main.tex` 均 HTTP 200；
    发布树 201 files，工作树干净
  - 最终交付背景简报已写入
    `.project-log/docs/context-briefing-20260904-final-delivery.md`
  - 用户已提供姓名：Bolin Tao
  - `research/paper/main.tex` 作者已替换为 Bolin Tao
  - 官方 CVPR 2026 模板已写入论文内容并编译验证为 2 页：
    `CVPR_2026_Submission_Template/main.tex`
  - `CVPR_2026_Submission_Template/main.tex` 已改为自包含完整正文，
    不再依赖 `sec/` 子文件
  - 优化版绘图脚本已加入：
    `research/scripts/render_architecture_optimized.py`
  - 新 architecture figure 已替换 `research/paper/architecture.pdf/png`
    与 `CVPR_2026_Submission_Template/figures/architecture.pdf/png`
  - 最终命名 PDF 已生成：
    `Bolin_Tao.pdf`
  - `Bolin_Tao.pdf`、官方模板 `main.pdf`、
    `research/paper/main.pdf` 均为 2 页且作者为 Bolin Tao
  - 2026-09-04 梯度累积实验已记录：
    `.project-log/docs/grad-accum-experiment-20260904.md`
  - 当前版本已备份 tag：
    `backup-final-before-grad-accum`（本地和 GitHub release）
  - 梯度累积代码已提交：`69234cb`
  - 代码冒烟验证通过：batch 2 / accum 4 / 9 micro-batches，
    得到 3 次 optimizer update，checkpoint 保存正常
  - 10k grad-accum LSAR 训练已在 detached tmux 中启动：
    session `grad_accum_lsar_15ep`，Python PID `2753134`
  - 训练日志：
    `outputs/logs/grad_accum_4_lsar_15ep.log`
  - 训练输出：
    `outputs/lgdm_10k/grad_accum_4/lsar_final/last.pt`
  - 自动评估 watcher 已启动：tmux session `grad_accum_eval_wait`，
    训练结束后自动执行 `evaluate.py --repeats 3`
  - watcher 日志：
    `outputs/logs/grad_accum_4_lsar_eval.log`
  - 梯度累积 10k 实验完成：repeat mean `655.3 ± 17.2`
    （`637/658/671`），低于当前 seed42 LSAR `678.0 ± 16.5`
  - 结论：梯度累积未显示训练收益；当前论文结果保持不变
  - Paper Revision V2 已完成：
    `.project-log/docs/paper-revision-v2-execution-20260904.md`
  - 论文改为 success rate 主表：`23.5 / 32.7 / 30.3 / 33.9 / 33.1`
  - sampling-mean 与 seed43 独立训练已分开表述
  - `research/paper/main.tex` 与
    `CVPR_2026_Submission_Template/main.tex` 均编译为 2 页
  - `Bolin_Tao.pdf` 已从修订版官方模板更新
  - GitHub 发布仓库已同步论文修订并推送：
    remote commit `bea378d`
  - README 与本机绝对 Python 路径已解耦，改用 `python` 通用命令
  - 曾出现两个进程写同一 `lsar_full` 目录的冲突；
    已停止后启动的 resume 进程，保留 seed 42 从头训练的
    原始进程并完成训练
  - `lsar_no_aff` 10k 训练已启动；
    LGDM 与 LSAR-full 的 3 次 repeat eval 已完成；
    10/50-step sampling sensitivity 正在 200-sample subset 上执行
  - 最终验证指南已修正并写入
    `.project-log/docs/final-validation-execution-plan-20260903.md`
- 活跃决策：
  - 个人仓库；git init；数据集固定为 Grasp-Anything++
  - DEC-002：仅在数据入口做最小 adapter，模型/评估保持官方
  - DEC-003：先环境自包含 → batch smoke → 语义核对 → Proposed Method
  - DEC-009：后续 Proposed Method 的 baseline 固定为 diffusion 版 `LGDM`，
    不再把 `lgrconvnet3` dense-map baseline 当作最终方法基线
- 阻塞项：无
- 最近验证：
  - EV-20260902-lsar-minimal（candidate）
  - EV-20260902-lsar-affordance-aux（candidate）
  - EV-20260902-subset-1000-ready（valid）
  - EV-20260902-subset-1000-experiments（candidate）
  - EV-20260902-clean-lgdm-train（candidate）
  - EV-20260902-lgdm-tensorflow（candidate）
  - EV-20260828-smoke-chain-runs（valid）
  - EV-20260828-env-self-contained（valid）
  - EV-20260902-diffusion-smoke（valid）
  - EV-20260902-lsar-scale-sweep（candidate）
  - EV-20260902-lsar-affordance-ablation（candidate）
  - EV-20260902-lsar-affordance-visual（candidate）
  - EV-20260902-larger-subset-3k-ready（valid）
  - EV-20260902-larger-subset-baseline（candidate）
  - EV-20260902-larger-subset-lsar（candidate）
- 下一步（gate）：
  1. 论文 PDF 已满足 2 页限制
  2. GitHub 仓库已创建、推送并检查 HTTP 200
  3. 最终命名 PDF `Bolin_Tao.pdf` 已生成并验证
  4. 官方 CVPR 2026 模板论文已编译为 2 页并推送 GitHub
- 显式不要做：
  - 不下载 Grasp-Anything++ / Grasp-Anything 完整 87 GB
  - 不枚举大 zip 全量 central directory
  - 不改评估协议，不重写 diffusion
  - 不并行多创新点
  - 不让单个 `Unknown` 阻塞主线
  - 不从 `full_image_atts` 做 LSAR（该张量为常量全 1）

## 2026-09-04 会话（梯度累积实验）

- 目标/任务：备份当前版本，并验证 `--grad-accum-steps 4` 是否影响
  LGDM + LSAR 10k 训练效果。
- 已完成：
  - 本地和 GitHub release 打 tag `backup-final-before-grad-accum`
  - `train_lgdm_clean.py` 增加 `--grad-accum-steps`
  - 提交 `69234cb`：`feat: add gradient accumulation to LGDM training`
  - 1000-stem smoke 通过
  - 启动 10k seed42 LSAR 15-epoch grad-accum-4 训练
  - 10k 训练完成：built-in eval `642/2000`
  - 3 次 repeat eval：`637/658/671`，mean `655.3`，std `17.2`
- 实验结果：grad accum 4 比当前 seed42 LSAR `678.0 ± 16.5` 低
  `22.7` 个 correct，std 相似；未显示梯度累积带来训练收益。
- 下一步：保持论文主结果不变；该实验作为 training-stability
  探索记录在
  `.project-log/docs/grad-accum-experiment-20260904.md`

## 2026-09-04 会话（Paper Revision V2）

- 目标/任务：按 `PAPER_REVISION_GUIDE_V2.md` 对论文做写作质量升级。
- 已完成：
  - Abstract / Introduction / Related Work 改为科研论文叙事
  - Method 中的 baseline、`y_view`、LSAR residual 与 loss 表述收紧
  - 主表改为 success rate，并明确 mean/std 是同一 checkpoint 的
    3 次 diffusion sampling
  - seed 43 表述为独立 LSAR 训练，不宣称 paired training robustness
  - affordance loss 表述为系数敏感：`0.05` 最好，`0.1` 退化
  - `research/paper/main.tex` 2 页编译通过
  - `CVPR_2026_Submission_Template/main.tex` 2 页编译通过
  - `Bolin_Tao.pdf` 已更新
- 验证：两版 PDF 均为 2 页，无 `??` / undefined reference / LaTeX Error。

## 2026-09-03 会话（外部 GPT 背景简报）

- 目标/任务：整理一份独立、可交给外部 GPT 的项目背景简报。
- 已完成内容：
  - 写入 `.project-log/docs/context-briefing-20260903.md`
  - 包含 1000 / 2968 / 5000 三个规模的结果
  - 包含 LSAR 实现位置、评估协议、环境限制和待决策问题
- 下一步：由用户将简报交给外部 GPT，再决定继续 10k 或进入最终训练/论文材料

## 2026-09-03 会话（5k subset Baseline vs Ours）

- 目标/任务：执行 5k/10k plan 的 5k 部分，确认 LSAR 在更大数据上是否保留。
- 已完成内容：
  - 从本地 RGB split 列出 994860 个可用 scene
  - `prepare_training_subset.py` 新增 `--scene-list`
  - 生成 `train_subset_5k.tsv`：5000 stems / 5000 unique scenes
  - 按需解压 5000 张 RGB，`missing=0`
  - Baseline 15 epochs，single eval 211/1000
  - LSAR-full 15 epochs，single eval 299/1000
  - 3 次 repeat eval：Baseline mean 202.7 / std 4.93；
    LSAR mean 309.7 / std 3.51
  - 生成 4 样本 affordance overlay 可视化
- 验证与限制：
  - LSAR 提高 repeat mean 约 107/1000，且 3 次采样全部更高
  - 仍是 5000 scene / 15 epochs 的实验，不作为最终论文性能声明
- 下一步：保留 LSAR；提交 5k 结果；可选继续 10k 或进入最终训练/论文材料

## 2026-09-02 会话（用户确认扩大 subset 并进入 5k/10k 验证）

- 目标/任务：提交 3k 实验，然后按 5k/10k plan 继续验证 LSAR。
- 已完成内容：
  - 确认本地 RGB split 完整可用，`/mnt/data/grasp-anything-lgd/data/raw/grasp-anything`
    存在 `image_part_aa` + `image_part_ab`
  - 确认 3k 训练耗时约 baseline 10 min / LSAR 22 min，5k/10k 计算量可控
  - 写入 5k/10k validation plan
- 下一步：
  1. 提交 3k Stage A-E 结果
  2. 合并 RGB split 并列出 scene 成员
  3. 生成 5k subset，按需解压 RGB
  4. 训练 Baseline vs Ours，重复评估

## 2026-09-02 会话（3k 大 subset Baseline vs Ours）

- 目标/任务：执行 large-subset validation plan，确认 LSAR 是否值得保留。
- 已完成内容：
  - Stage A：`prepare_training_subset.py` 新增 `--image-dir` 与
    `--allow-same-scene`，生成 2968 stem / 1010 scene 的
    `train_subset_3k.tsv`
  - Stage B：官方 LGDM baseline 15 epochs，单次 eval 151/594
  - Stage C：LSAR-full 15 epochs，单次 eval 185/594
  - Stage D：3 次 repeat eval：baseline mean 152.0 / std 5.57；
    LSAR mean 179.0 / std 1.73
  - Stage D：spoon handle、fork handle、apple stem 4 样本
    affordance overlay 可视化
- 验证与限制：
  - 2968 stem 全部有本地 RGB，scene 数 1010，每 scene 最多 3 个 prompt
  - Ours 提升约 27/594，且重复采样更稳定
  - 这不是最终性能声明，仍受 1010 scene / 15 epochs 限制
- 下一步：保留 LSAR，暂不优化结构；是否继续扩大 scene/样本由用户确认

## 2026-09-02 会话（LSAR scale sweep + affordance ablation + 可视化）

- 目标/任务：执行已批准的 LSAR experimental validation plan 的
  Task A/B/C/D。
- 已完成内容：
  - Task A：固定 scale=0.01/0.02/0.05/0.10 各跑 20 epochs，
    单次 eval 分别为 43/38/39/31
  - Task B：最优 scale=0.01 下对照 affordance loss；
    3 次 10-step 采样重复 eval，LSAR-full 均值 41.67，
    LSAR-no-aff 均值 18.67
  - Task C：新增 `--sample-stems` / `--show-affordance`，
    生成 spoon handle、apple stem、fork handle 三张 heatmap 叠加图
  - 新增 `research/scripts/eval_lgdm_checkpoint.py` 用于 checkpoint
    重复评估
- 验证与限制：
  - 单次 eval 有随机性；重复均值与单次趋势一致
  - LSAR-full 优于官方 baseline 但不构成显著结论；`std=3.51`
  - LSAR-no-aff 显著退化，说明空间监督是当前 LSAR 有效性的必要条件
  - 1000 样本 / 20 epochs 规模仍然很小，不作为最终性能声明
- 下一步：不冻结方法、不进入 LSAR V2；先用更大 subset 训练
  Baseline vs Ours，再评估是否采用当前 LSAR

## 2026-09-02 会话（1000 样本正式实验与 LSAR 调优）

- 目标/任务：在 1000 stem / 800 train / 200 val 上跑正式三条件实验，
  并给 LSAR 一个可解释的稳定性调优。
- 已完成内容：
  - `none` 33/200，`plain-y` 37/200，`lsar` 13/200
  - 诊断：`lsar.scale` 学到 0.224，残差注入过强
  - 新增 `--lsar-scale` / `--lsar-fixed-scale`，固定 scale=0.05 重训：
    `lsar_tuned` 39/200
  - 新增重复评估脚本，3 次采样均值：none 37.0 / plain-y 40.0 /
    lsar_tuned 38.33
  - 新增定性可视化脚本，输出 6 样本 GT/预测 grasp 图
- 验证与限制：
  - `lsar_tuned` 高于官方 baseline，但与 plain-y 注入非常接近；
    600 次采样评估仍不足以证明统计显著优势
  - 1000 样本规模小，结果不作为 SOTA 声明
- 下一步：整理 GitHub 仓库与论文材料

## 2026-09-02 会话（LSAR affordance 辅助监督与 1000 样本子集）

- 目标/任务：让 LSAR 有可验证的空间监督信号，并准备正式 subset 实验数据。
- 已完成内容：
  - `SpatialAffordanceRefinement` 新增 `proj` 与 `aff_head`
  - `LGDMWithConditioning.forward` 在 lsar 模式保存 `affordance_map`
    `(B,1,19,19)`
  - `train_lgdm_clean.py` 新增 `--lsar-affordance-weight 0.1`
  - 1-batch 验证：loss/backward 正常，affordance 非零
  - 100-sample `lsar_aff` 实验：20 epochs，4/20 correct
  - 1000 stem / 1000 unique scene 子集生成，1000 张 RGB 提取成功
- 验证与限制：
  - 100 样本新增辅助 loss 后精度仍 4/20，不能作性能结论
  - affordance MSE 稳定在约 0.021，未明显下降；需要更大数据量判断
  - 1000 样本实验尚未启动
- 下一步：启动 formal subset 三条件实验，并收集定量/可视化证据

## 2026-09-02 会话（LSAR V1 与最小三条件实验）

- 目标/任务：实现 LSAR V1，并在同一 Clean LGDM 训练/评估链上跑
  baseline、plain-y ablation、LSAR。
- 已完成内容：
  - 新增 `models/lgdm_lsar.py`
  - `train_lgdm_clean.py` 支持 `--condition-mode none|plain-y|lsar`
  - 100 stem / 80-20 split / 20 epochs / 10-step eval
- 验证与限制：
  - none 4/20，plain-y 4/20，lsar 4/20
  - `scale=0.1` 初始化，训练后 0.158；零 scale 初始化会 dead-start
  - 100 样本结果不作性能结论
- 下一步：决定是否加 affordance auxiliary loss，再进入正式实验

## 2026-09-02 会话（Clean LGDM 100-sample sanity 与 LSAR 插入点）

- 目标/任务：把 baseline 从“diffusion smoke”推进到“可训练、可加载、可评估”的
  Clean LGDM，并用 tensor-flow 证据固定 LSAR 插入点。
- 已完成内容：
  - `research/scripts/prepare_training_subset.py`：确定性采样 100 个不同 scene
    真实 stem，全部通过 instruction / positive `[N,6]` / finite 校验
  - `research/scripts/extract_rgb_subset.sh`：从 split zip 只解压 100 张
    `<scene>.jpg`，不展开完整图像归档
  - `research/scripts/train_lgdm_clean.py`：Clean objective 训练脚本
  - 80 train / 20 val，batch size 2，20 epochs，40 batches/epoch
  - `outputs/train_lgdm_clean_100/last.pt` 保存并可 `--resume`
  - 10-step respaced sampling eval：`5/20 correct`
  - `lgdm_tensorflow_debug.py`：official 与 inject-y 两种 forward 的 tensor/grad
    证据
- 重要发现：
  - ALBEF 返回的 `image_atts` 实际是 `torch.ones`，不是语言注意力图
  - 官方 `y` 分支没有接入 conv3，故文本特征无梯度
  - 将 `y_view (8x19x19)` 加入 `conv3` 后，`y` 与 ALBEF text 参数梯度均 finite
- 下一步：
  1. 实现 LSAR V1（`y -> y_flatten -> conv3` conditioning 分支）
  2. 跑最小 Baseline vs Ours 实验

## 2026-09-02 会话（Stage 1：LGDM diffusion baseline smoke 通过）

- 目标/任务：按用户要求落地阶段 0、阶段 1；阶段 1 重点确认当前 LGD 仓库的
  diffusion 版本能否跑通，作为后续 Proposed Method 的 baseline。
- 已完成内容：
  - 安装 diffusion 必需依赖到 `grasp-lgd`：`transformers==4.28.1`、
    `timm==0.6.13`、`ruamel.yaml==0.17.21`、`tensorboardX`、`torchsummary`
  - 下载 `bert-base-uncased` 到 HF 缓存；CLIP `ViT-B-32.pt` 本地已有
  - 新增 `research/scripts/diffusion_smoke.py`，用真实 stem 跑
    `LGDM` diffusion 链路
  - 结果：`2/2 OK, 0 FAIL`；`sample_shape=(1,1,224,224)`、sample finite、
    backward grad finite、峰值 GPU 约 2.51 GiB
  - 确认 `LGDM` 可实例化，参数约 573.6M
  - 更新 `environment.yml` / `env/requirements-freeze.txt` /
    `env/requirements-diffusion.txt` 等环境快照
- 重要发现：
  - `train_network_diffusion.py` 第 242-244 行把 diffusion loss 的 backward
    注释掉，实际只对 dense-map loss 做 backward；这会影响后续训练基线设计
  - `get_network` 未注册 README 中的 `lgd`，需使用 `lgdm`
  - smoke 的 `p_sample_loop` 使用 10 步 respaced cosine schedule，完整 1000
    步留给正式评估/训练
- 验证与限制：
  - 2 个 stem 来自不同 scene，证明不是单样本巧合
  - 未训练模型，`correct=False` 符合预期
  - 未跑完整 1000 步 sampling，未跑完整训练
  - instruction 直接使用 `.pkl` 字符串；官方历史 `queries[obj_id]` 语义仍
    `Unknown / To Verify`
- 下一步：
  1. 决定 diffusion baseline 训练脚本是否修正官方“diffusion loss 不 backward”
     的问题
  2. 选 1~2 个 LSAR 候选插入点
  3. 启动 100 sample 训练 sanity

## 2026-08-31 会话（gate ② 真 RGB batch smoke 通过）

- 目标/任务：在 image_part_ab 下载完成后，把 aa+ab 拼成完整 zip，挑 stems.txt 对应的 10 张 `<scene>.jpg` 解压出来，跑真 RGB pipeline 验证 gate ③ 完成。
- 已完成内容：
  - `image_part_aa`（34.36 GiB）+ `image_part_ab`（28.54 GiB）已下载完成（manifest `ok`）
  - `prepare_rgb_archive.sh --auto-merge` 走通：aa 是 `PK\x03\x04` 开头 zip、ab 是续段；合并后 `image_archive` 65.01 GiB，是合法 zip，目录结构 `image/<scene>.jpg`
  - 从合并 zip 中只挑 10 个 scene 的 `.jpg` 解压到 `processed/grasp-anything/images/`，总占用约 750 KiB
  - 删除中间 `image_archive`，`/mnt/data` 剩余 107 GiB
  - `research/scripts/batch_smoke.py --stems research/smoke-data/stems.txt --image-dir processed/grasp-anything/images --cpu` 跑通：
    - 10/10 OK, 0 SKIP-RGB, 0 FAIL
    - loss 范围 0.70 – 1.62；correct = True 仅 1 条（随机初始化 baseline），False 9 条；gate 只看 engineering correctness，未训练 baseline 的 0/10 correct 是允许的
  - `outputs/batch_smoke/{metrics.json, summary.txt, qualitative/<stem>.png}` 已写入
- 重要决策：
  - DEC-006：image_part_aa + ab 视为同一个 zip 的 split，需要 `cat` 后才能 `unzip`；不要把它们分别独立解压
  - DEC-007：合并后只挑 batch smoke 需要的 scene 文件解压，不展开 60 GiB 全部图像，避免吃光磁盘
- 验证与限制：
  - 全部 10 stem 都进入了 forward / loss / backward / post_process / IoU evaluation 流程
  - 网络是随机初始化，未训练；loss/correct 不构成模型质量证据，仅表明工程链路 OK
  - 仅解压了 10 张 `<scene>.jpg`；后续要做更大规模训练或评估时再展开完整 RGB
- 下一步：
  1. 即可宣布 baseline engineering landing 收口
  2. 进入 Proposed Method 设计阶段（按 DEC-003 路线）
  3. 同时可以基于 `outputs/batch_smoke/qualitative/` 写一份 visual sanity 报告放进 paper 附录

## 2026-08-31 会话（gate ② 非 RGB 部分前置）

- 目标/任务：把 batch smoke 拆成两部分——不需要 RGB 的全部前置，等 image_part_ab 完成后立即接 RGB 跑真实 batch smoke。
- 已完成内容：
  - `research/smoke-data/stems.txt` + `stems_meta.tsv`：固定 10 个跨 scene stem（10 个不同 scene，每条 stem 都过 instruction + positive shape/finite 校验）
  - `research/scripts/annotation_preflight.py`：基于 stems.txt 做 `str / [N,6] / N>0 / finite` 检查，10/10 OK，输出 `outputs/annotation_preflight/{report.tsv, summary.txt}`
  - `research/scripts/batch_smoke.py`：复用 `smoke_test.py` 风格，循环 10 stem；缺 RGB 时走 SKIP-RGB（不构造假图），输出 `outputs/batch_smoke/{metrics.json, summary.txt, qualitative/}`，当前在 SKIP-RGB 模式下全部 10 条通过
  - `research/scripts/prepare_rgb_archive.sh`：identify-only 模式跑通；当前发现：
    - `image_part_aa` 已落盘 34,359,738,368 bytes，与 DEC-001 记录一致
    - `image_part_aa` magic = `PK\x03\x04`（即 Zip archive data, compression method=store）
    - `image_part_ab` 当前仅 1,874,866,176 bytes，仍在下载
    - 脚本默认不 cat，仅当 `evidence_ok=1`（两个 part 字节数都与 DEC-001 一致）且显式传 `--auto-merge` 才合并
  - `env/environment-explicit.txt`、`env/conda-list.txt`、`env/requirements-freeze.txt`、`env/key-versions.txt`：记录 grasp-lgd 当前完整依赖快照；关键版本 torch 2.13.0+cu130 / torchvision 0.28.0+cu130 / numpy 2.2.6 / scipy 1.15.3 / skimage 0.25.2 / opencv 5.0.0
- 重要决策：
  - batch_smoke 在缺 RGB 时**不构造假图**，仅做 dense GT 生成与 shape/finite 校验；这与 DEC-002 / DEC-003 的 “gate ② 只检查 engineering correctness” 一致
  - `prepare_rgb_archive.sh` 默认拒绝合并；即使后续发现 aa/ab 其实是独立 zip（aa 已确认是 zip），也只会通过 `--auto-merge` 显式触发
- 验证与限制：
  - 10 stem 全部 SKIP-RGB 通过；metrics.json 已记录每条的 dense map shape / 矩形数
  - 未跑 forward/loss/backward/post_process/IoU，因为缺真实 RGB
  - `image_part_ab` 仍在下载；脚本仅做识别，未触发任何 cat
- 下一步：
  1. 等 `image_part_ab` 下载完成后立即跑 `prepare_rgb_archive.sh` 重新确认 evidence_ok
  2. 若 aa/ab 都是合法独立 zip，则不需要合并，直接分别 `unzip -d processed/grasp-anything/images/`，再按 `<scene>.jpg` 与 stems.txt 对齐
  3. 用 `batch_smoke.py --image-dir processed/grasp-anything/images/` 跑真实 RGB batch smoke；期望每条都进入 OK 状态（`correct` 可能是 False，因为是未训练 baseline，不影响 gate 通过）
  4. 完成后即可宣布 baseline engineering landing 收口，进入 Proposed Method 设计阶段

## 2026-08-31 会话（解压与对齐验证）

- 目标/任务：在 image_part_ab 仍在下载期间，先把已完成的 plusplus 注解解压并做 instruction ↔ positive 对齐验证。
- 已完成内容：
  - `unzip -tq` 校验两个 plusplus zip 完整性通过
  - 用 `unzip -qq -o` 把 `grasp_instructions.zip` 与 `grasp_label_positive.zip` 展开到 `/mnt/data/grasp-anything-lgd/data/processed/grasp-anything-pp/`；zip 内部自带同名顶层目录，实际文件落在 `.../grasp_instructions/grasp_instructions/` 与 `.../grasp_label_positive/grasp_label_positive/`
  - 编写 `research/scripts/verify_downloaded_dataset.py`，随机抽 5 个 stem 验证 `pkl` 为 Python 字符串、`pt` 为 `[N,6]` float32 张量，返回 `5/5 samples aligned`
- 重要决策：
  - DEC-005：保留 plusplus zip 自带的顶层目录，验证脚本指向子目录
  - `image_part_ab` 仍在下载（约 0.2%），当前工作未受阻塞
- 验证与限制：
  - 仅验证 5 个样本，未覆盖全量 zip 成员
  - 未加载 RGB 图像，依赖 aa/ab part 全部到位后做 batch smoke
- 下一步：等 `image_part_ab` 下载完成 → 合并 aa/ab → 解压 RGB → 跑 RGB 对齐和 batch smoke（gate ②）

## 2026-08-28 会话（Proposed Method LSAR 概念记录）

- 目标/任务：把外部给出的 Proposed Method（LSAR）落到 `.project-log`，供后续方案设计与论文写作使用。
- 已完成内容：
  - 将完整方案写入 [proposed-method-LSAR.md](/home/tbl/Project/视觉语言抓取作业/.project-log/docs/proposed-method-LSAR.md)（7912 字节）
  - 新增 `DEC-005`：确定 LSAR 为 Proposed Method
  - 新增 `TASK-005`：Proposed Method 设计（pending）
- 重要决策：
  - LSAR 作为本项目的 Proposed Method，遵循“只改 conditioning 分支，不动 grasp 表示、扩散过程、评估协议”
  - 实现优先级：轻量 CNN → Attention → Transformer 三选一，先 CNN
- 验证与限制：
  - 尚未写代码、未跑实验；后续需结合 batch smoke 与 instruction 语义核对结果再细化实现选择
- 下一步：继续 gate ② batch smoke → gate ③ 语义核对 → 进入 LSAR 编码与训练实验。

## 2026-08-28 会话（gate ① 环境自包含完成）

- 目标/任务：把 grasp-lgd 改造成真正 self-contained 的 conda env，禁用 user-site，使 `PYTHONNOUSERSITE=1` 条件下 smoke chain 仍能跑通。
- 已完成内容：
  - 持久化 `PYTHONNOUSERSITE=1`（`conda env config vars set -n grasp-lgd PYTHONNOUSERSITE=1`）
  - 用 `--ignore-installed` 把 numpy / scipy / matplotlib / Pillow / openai-clip / opencv-python-headless / scikit-image / tqdm / regex / ftfy 装进 env
  - 把 ~/.local 下的 torch / torchvision / nvidia_* / cuda_* / triton 目录拷进 env（cu126 轮子当前网络不可达）
  - 生成 `requirements.txt`（216 行）与 `environment.yml`（91 行）
  - 验证 `ENABLE_USER_SITE=False`，`sys.path` 不再含 `~/.local`，全部 12 个关键包都解析到 env，CUDA 可用（torch 2.13.0+cu130，device_count=1）
  - 重跑 `scripts/smoke_test.py`：`loss 1.656031 / correct: False`，forward/loss/backward/post-process/eval 全部通过
- 重要决策：
  - 采用“把 user-site 包拷进 env”作为 GPU torch 的短期方案，等网络恢复再替换为官方 wheel（DEC-004）
- 验证与限制：
  - env 已 self-contained；ROS 包仍出现在 `pip freeze`，因为 `PYTHONPATH=/opt/ros/humble/lib/python3.10/site-packages`
- 下一步：gate ② batch smoke（等 grasp_label_positive.zip 下载完成后启动）。

## 2026-08-28 会话（路线图记录）

- 目标/任务：把外部 GPT 推荐的“先修环境 → batch smoke → 语义核对 → Proposed Method”路线作为后续两天的执行计划。
- 已完成内容：
  - 在 `.project-log` 中记录路线图、gate 条件和显式不要做清单（DEC-003、TASK-003）
  - 更新 `current-session.md` 与 `progress.md` 的“当前状态”快照
- 重要决策：
  - 采纳三 gate：① 环境自包含 ② batch smoke ③ 官方 instruction 语义核对（≤1h）
  - 严格不动 `lgdm/diffusion`、不重查 zip CD、不追 `part_mask`
- 验证与限制：
  - 路线图已写入；尚未启动 gate ①
- 下一步：等待用户授权后开始 gate ① 环境自包含验证。

## 2026-08-28 会话（真实样本 smoke）

- 目标/任务：用一个真实 Grasp-Anything++ sample 跑通 image + instruction + GT -> dense maps -> lgrconvnet3 -> loss -> backward -> post-process -> IoU evaluation。
- 已完成内容：
  - 通过 HTTP Range 从 HF 提取真实 `scene.jpg`、instruction、positive/negative label，未下载完整数据
  - 建立 `research/smoke-data/` fixture 与 `scripts/inspect_sample.py`
  - 实现 `data_utils/grasp_anything_pp.py` 最小 adapter，复用官方 LGD dense-map pipeline
  - 修复 `LGD-main/inference/post_process.py` 对 requires-grad tensor 的 detach 问题
  - 实现 `scripts/smoke_test.py` 并跑通整条链
- 重要决策：
  - 不改官方 LGD pipeline，只在数据入口做 adapter
  - instruction 当前直接 encode `.pkl` 字符串；官方 reproduction 语义保留 Unknown/To Verify
  - 不碰 `lgdm`、`diffusion`，不进入完整训练
- 验证与限制：
  - `scripts/smoke_test.py` 输出四张 map 均为 `(1,1,224,224)`，loss 1.656，backward/post-process/eval 正常
  - 未训练，`correct: False` 符合预期
  - `part_mask` 未纳入 fixture，当前 baseline 不消费该文件
- 下一步：视用户/外部 GPT 决策扩展样本数或开始方法设计。

## 2026-08-28 会话（下载准备）

- 目标/任务：为 Grasp-Anything 下载准备脚本，确认 mirror 可下载后交用户手动执行。
- 已完成内容：
  - 使用本机 HF token 验证 hf-mirror 的 `/datasets/` 路径
  - 确认 4 个文件远程大小与调研记录一致
  - 确认 Range 请求返回 206，可断点续传
  - 创建 `research/scripts/download_grasp_anything_data.sh`，支持 `--check` / `--download`
- 重要决策：
  - 默认数据根目录为项目根下的 `data/`，已由 `.gitignore` 排除
  - 使用 `curl -C -` 续传，脚本不打印 token
- 验证与限制：
  - `--check` 4/4 通过，未下载完整数据文件
  - `image_part_aa/ab` 的真实封装格式仍需下载后由 `file` / header 判定
- 下一步：用户手动运行 `./research/scripts/download_grasp_anything_data.sh --download`。

## 2026-08-28 会话（续）

- 目标/任务：完成第一阶段 Technical Investigation Report
- 已完成内容：
  - 将论文、官方代码快照、数据样本、HF zip 证据归档到 `research/`
  - 确认 Grasp-Anything 与 Grasp-Anything++ 关系、HF 文件与体积
  - 确认 `.pt` GT 行格式、坐标/角度约定、positive/negative 语义
  - 追踪官方 DataLoader、preprocessing、model fusion、dense maps、post-process、evaluation
  - 记录官方代码与 HF 当前发布结构的不一致项
  - 输出 `docs/technical-investigation-report.md`
- 重要决策：
  - 不下载完整 plusplus/base
  - 不提出最终模型
  - 下一步先做 sample alignment 与 shape smoke test
- 验证与限制：
  - 实际读取了 plusplus instruction/positive/part-mask 与 base scene/negative samples
  - 未运行端到端训练，代码兼容性仍有 Unknown/To Verify
- 下一步：
  - plusplus zip sample index 对齐验证
  - 最小 subset dataset->forward->loss->eval smoke test

## 2026-08-28 会话（初始）

- 目标/任务：初始化工程，并把仓库标记为个人仓库
- 已完成内容：
  - 创建 `.project-log/`
  - `git init`，默认分支 `main`
  - 创建根目录 `AGENTS.md`，写入个人仓库规则
  - 建立 Project Goal `GOAL-001` 和首个 active run
- 重要决策：个人 Git 仓库；按任务说明固定 Grasp-Anything++ 与五参数抓取输出
- 验证与限制：已运行 `loopctl restore` 与 `loopctl start-run`；尚无数据集或实现证据
- 下一步：检查 Grasp-Anything++ 官方数据与评估细节

## YYYY-MM-DD 会话

- 目标/任务：
- 已完成内容：
- 重要决策：
- 验证与限制：
- 下一步：

<!--
会话区块按日期倒序向下追加；超过约 50-100 KB 或约 10 条时归档到
`.project-log/docs/archive/`，归档文件按日期可检索。
-->
