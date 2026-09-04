# Task List

Active goal: GOAL-001

## TASK-001 - 完成 Grasp-Anything++ 与官方 LGD baseline 技术调查报告

- Status: `done`
- Phase: `solution-research`
- Output: [docs/technical-investigation-report.md](../docs/technical-investigation-report.md)
- Verification: `partial`
- Next:
  1. 对真实 plusplus zip 做 sample index 对齐 smoke test。
  2. 跑最小 subset forward/loss/eval，检查网络输出 shape。

## TASK-002 - 用真实 Grasp-Anything++ 样本跑通完整 baseline smoke chain

- Status: `done`
- Phase: `solution-research`
- Output:
  - `research/smoke-data/`
  - `data_utils/grasp_anything_pp.py`
  - `scripts/smoke_test.py`
- Verification: `passed`
- Evidence: `EV-20260828-smoke-chain-runs`
- Limitation: 仅 1 个真实 stem；`part_mask` 未纳入；instruction 官方语义未确认
- Next:
  1. 视用户/外部 GPT 决策扩到 5~10 个真实 stem。
  2. 确认 instruction encoding 官方 reproduction 语义。

## TASK-003 - 路线图 gate ① 环境自包含 + ② batch smoke + ③ 官方 instruction 语义核对

- Status: `done`
- Phase: `solution-research`
- Related: `DEC-003`
- Plan:
  1. gate ① `PYTHONNOUSERSITE=1` smoke，缺什么装什么，导出 `requirements.txt` / `environment.yml`
  2. gate ② 本地 5~10 个不同 scene 真实 stem 跑 `scripts/batch_smoke.py`
  3. gate ③ ≤1h 检查 paper / dataset card / 官方 train code
  4. 三 gate 通过后退出 solution-research，进入 Proposed Method 设计
  5. 最小训练 sanity → 正式 subset 训练 → table + 可视化
- Verification: `passed`
- Evidence:
  - `EV-20260828-env-self-contained`
  - `EV-20260902-batch-smoke`
- Limitation: gate ③ 的官方 training instruction encoding 语义仍标记为
  `Unknown / To Verify`；本实现的最终任务定义直接使用数据集中提供的
  `grasp_instructions` 字符串作为 language input
- Next:
  1. 已完成，进入 LSAR 设计与正式实验

## TASK-004 - gate ② batch smoke：5~10 个不同 scene 真实 stem 跑完整 pipeline

- Status: `done`
- Phase: `solution-research`
- Related: `DEC-003`, `DEC-004`
- Plan:
  1. 等 `grasp_label_positive.zip` 下载完成后挑选 5~10 个不同 scene 的 stem
  2. 抓对应 `scene.jpg` / instruction / positive
  3. `scripts/batch_smoke.py` 跑 forward / loss / post-process / IoU eval
  4. 输出 `outputs/batch_smoke/{metrics.json, sample_*.png, summary.txt}`
- Verification: `passed`
- Evidence: `EV-20260902-batch-smoke`
- Limitation: 随机初始化 `lgrconvnet3`，结果不构成质量证据
- Next:
  1. 进入 diffusion baseline smoke（TASK-006）

## TASK-006 - 核对当前 LGD 仓库的 diffusion 版 LGDM baseline 能否在真实样本上跑通

- Status: `done`
- Phase: `solution-research`
- Related: `DEC-009`
- Verification: `passed`
- Evidence: `EV-20260902-diffusion-smoke`
- Output:
  - `research/scripts/diffusion_smoke.py`
  - `outputs/diffusion_smoke_2/metrics.json`
  - `env/requirements-diffusion.txt`
- Result:
  - 2/2 个不同 scene 的真实 stem 跑通
  - sample shape `(1,1,224,224)`、sample finite
  - 官方训练代码只对 dense-map loss backward，diffusion loss 未 backward
  - README `--network lgd` 未注册，实际使用 `lgdm`
- Limitation: 10 步 respaced sample，未跑完整 1000 步和完整训练；未训练模型 accuracy 不评价
- Next:
  1. 确定 diffusion baseline 训练入口与 diffusion objective 的 backward 策略
  2. 确认 LSAR 插入点
  3. 100 sample training sanity

## TASK-005 - Proposed Method (LSAR) 设计：模块实现、训练与 ablation

- Status: `done`
- Phase: `architecture-decision`
- Related: `DEC-005`
- Spec: [.project-log/docs/proposed-method-LSAR.md](docs/proposed-method-LSAR.md)
- Plan:
  1. 基于 Option 1（轻量 CNN）实现 LSAR
  2. 在 LGD baseline conditioning 分支接入 A_vl 与 F_v
  3. 加入 L_aff（BCE(A_ref, M_grasp)）
  4. 100 sample sanity → 5k subset → 20k+ final
  5. ablation：with/without LSAR、CNN vs Attention vs Transformer
- Verification: `candidate`
- Evidence:
  - `research/results/final_method_summary.md`
  - `research/results/10k_validation_summary.md`
  - `research/results/lambda_aff_sweep.md`
- Output:
  - `models/lgdm_lsar.py`
  - `research/scripts/train_lgdm_clean.py`
  - `research/scripts/eval_lgdm_checkpoint.py`
  - `research/scripts/visualize_lgdm_paired.py`
- Limitation: 结果基于 10000 unique scene / 15 epochs / 10-step diffusion
  sampling subset，不是全 Grasp-Anything++ 或完整 1000-step 采样声明
- Next:
  1. 已完成最终方法冻结；后续为 paper/GitHub 组织

## TASK-007 - 10k final validation：LGDM vs LSAR、lambda sweep、seed 与可视化

- Status: `done`
- Phase: `verification`
- Related: `DEC-009`
- Output:
  - `research/results/final_method_summary.md`
  - `research/results/10k_validation_summary.md`
  - `research/results/lambda_aff_sweep.md`
  - `research/assets/qualitative_10k_paired_lsar_0.05.png`
- Verification: `candidate`
- Evidence:
  - `EV-20260904-lambda-sweep`
  - `EV-20260904-lsar-final-second-seed`
  - `EV-20260904-sampling-sensitivity-final-005`
  - `EV-20260904-final-005-paired-visual`
- Result:
  - Final method: LSAR with `scale=0.01` fixed and
    `lambda_aff=0.05`
  - Repeat mean /2000: LGDM 470.0, LSAR-full 605.3, LSAR-no-aff 653.7,
    LSAR final seed42 678.0, seed43 661.7
- Next:
  1. 实验证据冻结
  2. 在用户确认后整理论文材料与 GitHub 发布信息

## TASK-008 - 编写 2 页 CVPR 风格英文论文源文件

- Status: `done`
- Phase: `engineering-spec`
- Related: GOAL-001, TASK-007
- Output:
  - `research/paper/main.tex`
  - `research/paper/paper-figure-architecture.pdf`
  - `research/assets/qualitative_10k_paired_lsar_0.05.png`
  - `research/paper/cvpr.sty` / CVPR 模板文件
- Acceptance:
  1. 包含 Abstract / Introduction / Related Work / Method / Experiment /
     Conclusion / References
  2. 英文写作
  3. 包含架构图、定性可视化、主结果表、ablation 表与公式
  4. 总长度不超过 2 页
  5. GitHub repository link 预留为可替换占位符
- Next:
  1. 准备架构图
  2. 写 LaTeX 源文件
  3. 安装/验证编译工具链

## TASK-009 - 编译并验证论文 PDF

- Status: `done`
- Phase: `verification`
- Related: TASK-008
- Output: `research/paper/main.pdf`
- Acceptance:
  1. `pdflatex`/等价 LaTeX 编译成功
  2. 编译后 PDF 正好不超过 2 页
  3. 图表与公式均正常渲染
  4. 引用列表在页面限制内
- Next:
  1. 编译
  2. 用 PDF 信息或渲染页数检查页数

## TASK-010 - GitHub 仓库整理与发布

- Status: `done`
- Phase: `implementation`
- Related: GOAL-001, TASK-008, TASK-009
- Output:
  - GitHub personal repository
  - README / environment / data preparation / train / eval / inference /
    visualization 命令
  - paper 中替换为真实 GitHub URL 并重新编译
- Acceptance:
  1. `gh auth status` 可用
  2. repository 已在用户 GitHub 账号下创建并可见
  3. 不包含 98 GB `outputs/`、checkpoint、大 zip 或临时文件
  4. paper 中的 GitHub URL 指向真实 repository
- Evidence:
  - `https://github.com/TBLboy/language-driven-grasp-detection`
  - `gh repo view` 返回 PUBLIC
  - `curl -I https://github.com/TBLboy/language-driven-grasp-detection`
    返回 HTTP 200
  - release repo: 198 files, 33 MiB, 不含 checkpoint / outputs / 大 zip
- Next:
  1. 确认仓库可见性与命名
  2. 清理 `.gitignore` 和跟踪文件
  3. push 代码并替换 paper URL

## TASK-011 - 最终交付审计

- Status: `done`
- Phase: `alignment`
- Related: GOAL-001
- Acceptance:
  1. 对照任务规格逐项核对
  2. 确认论文 PDF 文件名符合 `Bolin_Tao.pdf`
  3. 确认 GitHub URL 与代码可复现性
  4. 记录最终验证证据
- Evidence:
  - `Bolin_Tao.pdf` 2 pages, author `Bolin Tao`
  - `CVPR_2026_Submission_Template/main.pdf` 2 pages
  - GitHub raw final PDF, official `main.pdf`, and `main.tex` HTTP 200
- Next:
  1. 已完成最终交付审计
