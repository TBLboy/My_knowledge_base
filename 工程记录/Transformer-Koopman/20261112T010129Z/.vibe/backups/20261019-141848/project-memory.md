---
description: >-
  The project block: Stores durable, high-signal information about this codebase: commands, architecture notes,
  conventions, and gotchas.
label: project
limit: 5000
read_only: false
---
# Transformer-Koopman (D:/Project/Transformer-Koopman)

## 布局与仓库
- 外层非 git；真仓库=内层 Transformer-Koopman/；分支 paper（tip 75a7b92 已推 origin）；main 空基线；backup/old-remote-main=ec90f2a。
- 事实源=外层 .project-log（format 2）；框架缺陷=.project-log/docs/framework-defects.md（D-010..D-019）。
- 目录：论文/{新版本,老版本}；代码部分/{新版本=正式代码路径（空）,老版本/训练代码}；杂项/{新版本=验证路径,老版本}；数据备份/；结果备份/。被删文件可从 95e60f8 取回。

## 命令
- Vibe CLI: D:/conda/envs/vibe-coding/python.exe C:/Users/12187/.config/opencode/vibe-workflow/scripts/vibe.py --root D:/Project/Transformer-Koopman <cmd>
- 项目解释器（torch2.6+cu124/CUDA、cvxpy+osqp、scipy、matplotlib）: D:/conda/envs/edmddl2/python.exe。缺 optuna/h5py/control。
- 控制台是 GBK：Python 打印非 GBK 字符会崩 → 输出写 UTF-8 文件再 read；脚本内 print 需 ascii-sanitize 或设 PYTHONIOENCODING=utf-8；传中文参数给 CLI 用 Python subprocess。
- state-apply 信封：{schema_version:1, command_id, expected_revision, expected_generation, action, payload}，一次一个 action；expected_revision=local_revision（每次写+1）。task.create payload 只允许 {id,title,goal_id,extensions}；goal.create {id,title,extensions}。
- record create --kind --id --title --status --payload @file；合法 kind=business-atom/requirement/decision/architecture/research/alignment/open-question/retrospective/distillation；decision 用 status=active。
- task begin --task-id --run-id --next-action；task finish --task-id --summary；evidence record --id --kind --subject --status --task-id --covers --version-binding；review record --id --task-id --reviewer --verdict --scope --evidence-ref；gate --task。task.update 只能改 implementer/owner。

## 论文约束（计划书为准，DEC-079）
- scheduled Koopman predictor + measurement-dependent input modulation，不声称 bilinear Koopman；次优性用条件形式；理论包完成前不动摘要/Intro/实验/标题。TASK-032 waiting-user（不自行开始）。
- Theory_Package/ 在 杂项/新版本/Theory_Package/（01..10）；GOAL-002 八阶段+SC-2 完成（TASK-034..042 全 go），SC-5=partially（plant 未定，DEC-082）。

## GOAL-003 软体平台实验（TASK-045，已完成收口）
- 目录 杂项/新版本/Temporary_Experiments/；计划书 Gate 0–5 全过；REV-TASK045-001=go。
- 核心发现：A(c) 收益大（H=25 rollout 0.0756→0.0265）；B(χ) 无可测量收益（→0.0258）；M4/M5 选中相同配置；ρ(A)=1.01–1.03>1；闭环多为 plant 外推且排序不稳健；M6 seed0 训练不可复现；u_limit=±100 未确认（Q3）。

## GOAL-004 机械臂实验（TASK-046，进行中）
- 数据：数据备份/机械臂数据/处理后的数据/{train,val,test}.npz；x=[q1,dq1,q2,dq2,q3,dq3]、u=[τ1,τ2,τ3]；dt=0.004 s（250 Hz）；20 条 20 s；划分 15/4/1（文件名串序，test 仅 data9）；审计=reports/data_audit_arm.md；速度列是位置差分，非独立观测。
- DEC-086 力矩盒=train 经验范围×1.05（用户确认）：物理 lower [-2.770553,-0.217663,-1.237823] upper [3.678861,5.994418,3.113232]；归一化 lower [-3.053656,-3.624193,-4.794951] upper [3.967189,3.138686,3.172559]；非对称（关节2重力偏置，均值3.11）。
- DEC-087 设备参数化：新增 models/device.py（soft_platform/arm_3link）；--device/-d 或 TK_DEVICE 选择，脚本首行 device.bootstrap_from_argv() 必须在 import protocol/library 之前；arm n=6,m=3,P=8,patch=2,d=14(=n+8),ctx=69；时域 {5,25,100,500,1000} 步={0.02,0.1,0.4,2,4} s；MPC N=50(0.2 s)，敏感性 {25,100}；输出 results/arm/、checkpoints/arm/、reports/arm_*。
- DEC-088 预算裁剪：场景 setpoint 400 步(1.6 s)/tracking 800(3.2 s)；敏感性用 2 场景子集（setpoint_0,slow_sinusoid，含 default 统一，run_gate4 --search-scenarios）；test stage 用 run_gate1 --test-from-checkpoint；实测 N=50 单步 66 ms、N=25 26.5 ms。
- 回归验证：scripts/regression_ab_soft.py = 同 checkpoint 旧码 vs 新码 → 0/1057 指标差异（results/modeling/regression_ab_soft.json）。注意 checkpoint-vs-ledger 不是回归测试（ledger test 数字来自进程内重训，M4/M5/M6 有差）。
- 驱动：scripts/run_arm_all.py（顺序、可续跑、逐步日志 results/arm/logs/）；报告生成 scripts/report_arm.py（arm_modeling_comparison/arm_control_comparison/arm_cross_device）。
- 环境：16 GB RAM 是瓶颈 → 逐模型独立进程。

## 长时域现象（RESEARCH-003，DEC-090）
- 软体平台：M4/M5 在 h=1/25 优于 GRU 1.9×/1.37×，h=32（6.4 s）交叉，h=100 劣 8.2×（0.8991 vs 0.1095）；相对 trivial 技能 11.6×→1.22×，GRU 8.5×→10×。
- **降级为非主因（不是「排除」）**：ρ>1（‖∏A‖₂ 100 步仅 2.8× vs 误差 86×；A0B0 29.5× 与其 ×27.6 吻合）、A-调度漂移（完美 A-context 只改 3%）、一步残差（无传播 rollout 平坦）。
- 机制：z=[x_k;ψ_k]（前 n 维精确=x，地板 0），一步残差 ~0.26 几乎全在 ψ（h=2 仅 4% 在观测维）；潜误差线性累积 ×32，观测 ×79。
- 术语（GPT 二轮修正）：用「隐藏坐标残差累积 + 交叉耦合介导泄漏」，**不写 unobservable**（CA(0,v)ᵀ=A_xψv≠0，ψ 经 A_xψ 可观）；**不写「GRU 无隐状态」**——GRU 有隐状态，区别是它直接在输出路径受多步损失约束。
- 口径陷阱：ledger 的 rollout.long 是**整段平均**（M4 H=100=0.3932），曲线表是**逐步**（0.8991）；tf_ctx 只冻结 A-context（χ 仍取传播态）→ 已加 tf_ctx_chi。
- 脚本 probe_transient_growth / probe_error_attribution（6 模式）/ probe_error_closure（GPT §4 精确分解+浮点闭合门槛）；报告 reports/long_horizon_phenomenon.md（§10 = GPT 二轮复核评估）。
- DEC-090：论文按原定路线（保留 A(c)+B(χ)）；不得声称 B(χ) 经验更好。
- 机械臂初步：M3(GRU) val_roll25 ≈0.11 优于 M0 0.35/M1 0.30/M2 0.33（M4–M6 未跑）。

## 陷阱（实测）
- 门禁读 extensions.risk 不是 risk_class（D-011）。
- evidence refresh 不重算绑定只标 stale；绑生成式 .md 会让证据一改就全 stale（D-018）。
- record create --payload 必须传裸内容对象（D-010）；payload 单字符串上限 4096 B；记录 append-only 不可删。
- verification-reviewer 无 shell：哈希/diff 由主 Agent 落盘并贴进 review scope（D-013）。
- 写 JSON 给 CLI 警惕 BOM；core.autocrlf=true 会改字节哈希。
- edit 工具在 newString 里写 \" 会落成字面反斜杠+引号（改用普通引号或 Python 按行改写）。
- 无 read_image；用 fitz 数值测排版。
- 用户会并行手改文件：动手前重算哈希/行数。
- PS 5.1 把无 BOM 的 .ps1 按 GBK 读 → 中文字面量路径的反斜杠被吞（Set-Location 静默失败、探针 rc=2）；.ps1 必须纯 ASCII（路径读 UTF-8 文件）或带 BOM；等待脚本的完成判据不得出现在自身日志里（会自我匹配立刻 break，用标记文件）。
