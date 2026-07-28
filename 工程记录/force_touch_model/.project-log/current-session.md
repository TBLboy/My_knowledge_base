# Current Session

- 当前阶段：verification
- 当前目标：从官方 NVIDIA GR00T N1.7 base 通过 LeRobot 启动统一微调，并将训练指标同步到 W&B
- 当前任务：TASK-019（进行中；正式 30000-step 训练监控与最终验收）；TASK-017 已完成官方 base → LeRobot 训练 → checkpoint/training_state 保存 → W&B 指标同步闭环验证
- 已完成事实：
  - 原始 v2.1 数据未修改；新建 `/mnt/data/gr00t-finetune/datasets/lerobot_dataset_right_o6_13d_v30`。
  - 新数据为 LeRobot v3.0，148 episodes、47250 frames、30 FPS，三路视频可读，13D state/action 和 `pouring` 任务正确。
  - `src/lerobot/policies/groot/processor_groot.py` 已改为优先读取 checkpoint `processor_kwargs.model_name`，自动使用本地 Cosmos backbone。
  - 当前 Processor 输出 `[1,1,132]` state、`[1,40,132]` action、正确的 16 步/13 维 action mask，postprocessor 输出 `[1,16,13]`。
  - 独立 checkpoint 可由 `GrootPolicy` 在 CPU 加载，最小 `predict_action_chunk` 输出 finite `[1,16,13]`。
  - 独立 GR00T 的关键微调参数已迁移到 LeRobot：batch size、梯度累积、学习率、warmup、constant scheduler、paged AdamW 8-bit、bf16、保存频率等。
  - LeRobot 已支持按 optimizer update 计数的 `gradient_accumulation_steps`，并新增 `paged_adamw_8bit` 延迟依赖注册。
  - 已生成默认只打印命令、不自动启动训练的 `examples/groot/finetune_right_o6_13d_lerobot.sh`；其实际执行入口统一为 LeRobot 的 `lerobot-train`。
  - 训练初始化路径已切换为本地官方 base `/mnt/data/gr00t-finetune/models/gr00t_n1_base`；这是 raw GR00T checkpoint，使用 `policy.base_model_path` 而不是 `policy.path`。
  - 真实 CUDA 最小测试通过：GrootPolicy(config) 加载 checkpoint-30000，forward loss=0.04111609607934952 finite；未恢复独立 optimizer/scheduler/RNG/step 状态。
  - 用户首次正式启动在 cfg.validate 阶段因默认 push_to_hub=true 且缺少 policy.repo_id 失败；已加入 `--policy.push_to_hub=false`，并用完整 lerobot-train 的 steps=0 初始化 smoke 验证通过。
  - 已通过最小配置解析、梯度累积 toy runtime、PagedAdamW8bit CUDA step、真实 GR00T GPU forward/backward、相关 pytest、ruff 和 shell 语法检查。
  - 用户正式训练在 step 5600 保存 checkpoint 时暴露两个 paged AdamW 保存问题：Python int step 无法直接写入 safetensors；修复后又发现 bitsandbytes qmap tensor 跨参数共享 storage。两者均已修复。
  - 修复后真实 3B GR00T 1-step checkpoint-save smoke 通过；training_state 中生成 optimizer_state.safetensors、optimizer_state_metadata.json、optimizer_param_groups.json、scheduler_state.json、rng_state.safetensors 和 training_step.json，读取到 537 个 optimizer state，step=[1]。
  - Ollama `ollama serve` 与 `llama-server` 已停止；没有杀其他 GPU 进程。
- 本轮新增事实：
  - 用户提供的 W&B API key 已通过 LeRobot 环境完成登录，凭据写入 `/home/tbl/.netrc`，文件权限为 600；未在日志中记录 key 内容。
  - `examples/groot/finetune_right_o6_13d_lerobot.sh` 默认从本地官方 base `/mnt/data/gr00t-finetune/models/gr00t_n1_base` 启动，不再默认使用旧的 checkpoint-30000。
  - 训练参数保持目标 RTX 4090 已验证的安全配置：batch=1、gradient accumulation=8、effective batch=8、lr=5e-5、warmup=1500、constant_with_warmup、paged AdamW 8-bit、BF16、gradient checkpointing、冻结 VLM/vision，仅训练 projector/action diffusion/VLLN。
  - 默认输出 `/mnt/data/gr00t-finetune/outputs/lerobot_right_o6_13d_from_official_n1_7`；默认保存本地 checkpoint，但关闭 W&B 大模型 artifact 上传。
  - W&B 默认 online，项目名 `lerobot-gr00t-right-o6-13d`；当前环境已完成登录，凭据写入 `/home/tbl/.netrc`，权限为 600，未将 API key 内容写入日志。
  - 修复了 `names` 为 LeRobot 分组字典时只返回组名、导致 GR00T relative-action 维度推断错误的问题；现在按组顺序展开为标量动作名。
  - 官方 base 1-step CUDA checkpoint-save smoke 通过；10-step W&B online smoke 通过并产生 loss、grad_norm、lr、吞吐和显存指标。
- 最近产物：
  - `GR00T_LEROBOT_MIGRATION_ASSESSMENT.md`
  - `examples/dataset/convert_gr00t_v21_to_v30.py`
  - `examples/groot/finetune_right_o6_13d_lerobot.sh`
  - `/mnt/data/gr00t-finetune/datasets/lerobot_dataset_right_o6_13d_v30`
- 验证：EV-013—EV-035；官方 base 1-step checkpoint-save、10-step W&B online、checkpoint safetensors 可读性、目标 Groot pytest、ruff 和 shell 语法检查通过。完整 `test_groot_lerobot.py` 集成测试受 Hugging Face snapshot 不完整且网络不可达影响，记录为 environment failed。
- 环境：Vibe Coding runtime 使用 `/home/tbl/miniforge3/envs/vibe-coding/bin/python`；LeRobot 开发环境使用 `/home/tbl/miniforge3/envs/lerobot/bin/python`；独立 GR00T 环境使用 `/home/tbl/miniforge3/envs/gr00t_n1/bin/python`。
- 正式 LeRobot 微调已由用户于 2026-07-27 19:09（Asia/Shanghai）启动，训练在 step 5600 保存 checkpoint 时失败；`005600/pretrained_model` 已保存，但 `training_state` 因 optimizer 序列化失败而不完整。训练进程已退出。
- 修复后已用 `005600/pretrained_model` 作为 `--policy.path` 完成 1-step 真实 GR00T checkpoint-save smoke；可从该模型权重启动新 optimizer 运行，但不能对原 step 5600 做完整 `--resume`。
- 未完成边界：尚未完成正式 30000 steps、最终 loss/吞吐统计、完整 checkpoint resume 和真实机器人 rollout；不能将 step 5600 的模型保存误报为可精确恢复。
- 下一步：可启动正式 30000 steps 训练；训练期间观察 W&B 的 `train/loss`、`train/grad_norm`、`train/lr`、`train/gpu_mem_gb`、吞吐和 checkpoint 保存日志。

## 2026-07-28 13:05 完成官方 base 全流程最小闭环

- 1-step smoke：从 `/mnt/data/gr00t-finetune/models/gr00t_n1_base` 完成真实 CUDA optimizer update，并保存 `checkpoints/000001`。
- 保存验证：模型权重、processor 配置、optimizer state、scheduler state、RNG state 和 `training_step.json` 均存在且 safetensors 可读，step=1。
- 10-step W&B smoke：保存 `checkpoints/000010`；W&B run `5jlg6v6b` 状态为 `finished`，summary 包含 `train/loss`、`train/grad_norm`、`train/lr`、吞吐和显存指标。
- 明确边界：这是链路验证，不代表模型收敛或真实机器人成功率；正式训练仍需单独监控。

## 2026-07-28 清理 smoke 输出

- 已删除本地 smoke 输出目录：
  - `/mnt/data/gr00t-finetune/outputs/lerobot_right_o6_13d_official_e2e_smoke_20260728`
  - `/mnt/data/gr00t-finetune/outputs/lerobot_right_o6_13d_official_wandb_smoke_20260728`
  - `/mnt/data/gr00t-finetune/outputs/lerobot_right_o6_13d_official_wandb_smoke_20260728_v2`
- 未删除 W&B 云端测试 run；云端记录仍可用于回溯验证。
- 清理后 `/mnt/data` 剩余约 97 GB；正式训练默认输出目录不存在，可直接使用。

## 2026-07-28 检查 /mnt/data checkpoint 库存

- 当前正式训练需要保留：`/mnt/data/gr00t-finetune/models/gr00t_n1_base`（官方 GR00T N1.7 base）和 `/mnt/data/gr00t-finetune/models/cosmos_reason2_2b`（GR00T 配置引用的 VLM backbone）。
- `/mnt/data/gr00t-finetune/outputs` 当前包含独立 GR00T 的 root 模型与 checkpoint-22400/28000/30000、旧 LeRobot continued-20k 的 005600、两个旧 checkpoint-save smoke 目录。
- 初步判断可清理：旧 smoke c/d、旧 continued-20k；独立 GR00T 的 22400/28000 是历史回滚点，如不做历史评估也可清理。`checkpoint-30000` 是旧独立训练的最新点，但当前正式训练从官方 base 开始，不是必需输入。
- 本次仅盘点，未删除模型或 checkpoint。

## 2026-07-28 清理 outputs，仅保留独立 GR00T 30000 步 checkpoint

- 已保留唯一模型：`/mnt/data/gr00t-finetune/outputs/gr00t_n1_right_o6_13d_retrain/gr00t_n1_right_o6_13d_full_20k/checkpoint-30000`，约 15 GB，包含模型分片、optimizer、scheduler、RNG、statistics、processor 和 trainer state。
- 已删除：checkpoint-22400、checkpoint-28000、独立训练根目录重复模型副本、`open_loop_eval`、两个旧 LeRobot checkpoint-save smoke、`lerobot_right_o6_13d_continued_20k`。
- 当前 `/mnt/data/gr00t-finetune/outputs` 下仅剩上述 checkpoint-30000；`models/gr00t_n1_base` 和 `models/cosmos_reason2_2b` 未删除。
- 清理后 `/mnt/data` 剩余约 168 GB。

## 2026-07-28 建立测试产物自动清理规则

- 已更新全局 `/home/tbl/.codex/AGENTS.md` 和项目 `AGENTS.md`：测试、smoke、dry-run、临时实验产生的 checkpoint、模型权重、日志、W&B 本地目录、缓存和临时数据，验证结束后必须清理。
- 测试结论、关键命令、失败原因、清理结果和最小必要线索统一记录在 `.project-log/`，不再用外部报告和测试输出目录堆积证据。
- 当前 outputs 已按用户要求清理，仅保留独立 GR00T `checkpoint-30000`；官方 base、Cosmos backbone 和数据集未删除。
- 工作流文件已创建备份：`/home/tbl/.codex/backups/vibe-global-update-20260728-132240-test-artifact-cleanup/`。
- 下一步：对项目规则变更做定向 Git commit；不纳入当前未完成的模型训练代码变更。

## 2026-07-28 13:30 正式训练启动

- 已由用户启动正式 LeRobot GR00T 训练：W&B run `7qfmd9v5`，项目 `lerobot-gr00t-right-o6-13d`。
- 初始模型：官方 `/mnt/data/gr00t-finetune/models/gr00t_n1_base`；数据集：`lerobot_dataset_right_o6_13d_v30`；目标 30000 steps；每 5600 steps 保存 checkpoint。
- 运行观察：截至 2026-07-28 16:31，正式训练进程仍在运行，约完成 step 9939/30000；近期 loss 约 0.034–0.052，grad_norm 约 0.084–0.119，lr 已达到 5e-5，单步约 1.10 秒，显存约 14.24 GiB，无 OOM、NaN 或 optimizer 初始化失败。
- 说明：`The exact optimizer requires bitsandbytes...` 是训练脚本的参数提示，不是失败；实际配置为 `paged_adamw_8bit`，且训练已进入正常 update。
- 当前边界：已完成第一次 checkpoint 保存点 5600；尚未完成正式训练、最终 checkpoint、收敛判断或真实机器人 rollout。

## 2026-07-28 16:31 工程巡检

- 当前正式训练进程 PID `300129` 仍在运行，W&B 子进程正常存在；GPU 为 RTX 4090，显存使用约 19121/24564 MiB。
- `/mnt/data/gr00t-finetune/outputs/lerobot_right_o6_13d_from_official_n1_7/checkpoints/005600` 已保存 `pretrained_model`、`training_state`、optimizer safetensors/JSON、scheduler 和 RNG 状态；`training_step.json` 为 5600。
- 代码仓库为 `lerobot_v1.0`，当前存在 GR00T、训练循环、优化器、Processor、测试和示例的未提交改动；本次巡检未修改产品代码，也未重新运行测试。
- 发现工作流状态漂移：`current-session.md` 与任务清单显示 `TASK-017` 已完成/正式训练进行中，但 `.project-log/loop/active-run.yaml` 仍为 `business-intent`、无任务且 native goal 未绑定；后续恢复前应先对齐 Loop 状态，不能直接据此判断项目未开始。
- 已确认仓库边界设计：项目日志故意放在外部项目根 `.project-log/`，代码仓库为内层 `lerobot_v1.0`；该布局不需要迁回或调整。本次归档以外部 `.project-log/` 为唯一工程记录源。
