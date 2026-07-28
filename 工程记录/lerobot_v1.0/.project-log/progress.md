# Progress

## 2026-07-27 Vibe Coding 框架健康检查

- 状态：已完成（框架核心正常）。
- Project Log：此前缺失，已按 runtime 模板初始化；`validate_project.py`、`vibe validate` 通过。
- Loop Core：`restore`、`status`、`validate` 通过；当前为空项目初始状态：`business-intent`、无 Goal、无任务。
- 框架包：`validate_package.py` 通过；Python 3.12 下测试为 `16 passed, 1 skipped, 4 subtests passed`；8 个注册角色提示词均渲染成功。
- 已安装状态：`global_installer.py verify` 通过。
- 环境限制：系统 `/usr/bin/python3` 是 Python 3.10.12，低于框架要求的 Python 3.11+；使用 Python 3.12 隔离环境完成相关检查。
- 变更：仅生成 `.project-log/`，未修改框架源代码。

## 2026-07-27T10:41:43+08:00 LeRobot v1.0 环境切换

- 状态：已完成核心安装与验证。
- 旧版：Miniforge `lerobot` 环境中的 `lerobot 0.5.1` 已卸载。
- 当前版：仓库 `lerobot 0.6.1` 已以 editable 模式安装，导入路径指向 `src/lerobot`。
- 依赖：安装 `dev,test,wallx` extras；`transformers` 从 5.3.0 升级到 5.5.4。
- 验证：`lerobot-train --help` 成功；`tests/configs/test_default.py` 为 5 passed；Torch 2.10.0/CUDA 12.8 可用。
- 限制：`pip check` 报告无关包 `generate-parameter-library-py` 缺少 `typeguard`；未将其作为 LeRobot 阻塞项处理。组合测试跑到 69 passed 后因耗时手动中止。

## 2026-07-27T10:45:00+08:00 修复 typeguard 缺失依赖

- 状态：已完成。
- 操作：在 `/home/tbl/miniforge3/envs/lerobot` 中安装 `typeguard 4.6.0`。
- 原因：满足 ROS 提供的 `generate-parameter-library-py 0.7.1` 依赖声明。
- 验证：`pip check` 返回 `No broken requirements found`；`lerobot-train --help` 通过；配置测试 `5 passed`。
- 边界：未修改 `/opt/ros/humble` 系统目录。

## 2026-07-27T11:03:15+08:00 建立 LeRobot 代码地图

- 状态：已完成。
- 产物：根目录 `CODE_MAP.md`，共 667 行。
- 覆盖：项目定位、总体架构、24 个顶层模块、20 个策略目录、13 个机器人适配目录、16 个遥操作目录、配置/注册机制、Dataset v3 数据结构、Processor 数据流、CLI、测试、文档、示例和推荐阅读路径。
- 证据：EV-008；关键路径存在；`lerobot 0.6.1` 导入路径指向当前仓库；`lerobot-train --help` 与 `lerobot-record --help` 通过；Project Log 校验通过。
- 边界：未连接真实硬件、未运行训练、未执行完整测试和仿真 benchmark；地图不替代端到端运行验证。

## 2026-07-27T11:48:34+08:00 CodeGraph 工程图谱

- 状态：已完成。
- CodeGraph 1.5.0 已安装为 Codex MCP，LeRobot 索引为 `804 files / 17,512 nodes / 46,134 edges`，状态 up to date。
- `.codegraph/` 已加入根 `.gitignore`；未安装进 `/home/tbl/miniforge3/envs/lerobot`。
- 证据：EV-009；Codex MCP 列表与 CodeGraph status 通过。
- 下一步：重启 Codex/Zed ACP 后执行一次 MCP 查询 smoke test。

## 2026-07-27T14:00:00+08:00 整理 LeRobot 与 GR00T 学习记录

- 状态：已完成。
- 目标文件：`/home/tbl/Project/工作经历汇总/学习记录/2026.07.27/今日任务.md`。
- 产物：按老板电器、LeRobot 五层架构、硬件/数据/Feature/Mask、GR00T 配置与模型层、action horizon、兼容性和实验顺序重新组织的 Markdown 学习记录，共 1421 行。
- 新增重点：Feature 定义；`state_mask`、`action_mask`、`attention_mask`；132 维 state/action 容器；padding 与 mask 原理；`GrootConfig`；`GrootPolicy`、`GR00TN17` 与 Transformer 组件的关系；action horizon 与控制频率的深入解释。
- action horizon 说明包含：20/30/50/100 Hz 时间换算、训练帧率与部署频率不一致的后果、滚动时域、chunk 执行、重采样/插值/hold 以及触觉多频率控制分层。
- 备份：`今日任务.md.bak`。
- 验证：Markdown 代码围栏 184 个且成对闭合；关键标题和章节存在；未修改 LeRobot 产品代码。
- 边界：未运行专用 Markdown 渲染器；目标文件位于 LeRobot 仓库之外。

## 2026-07-27T16:00:00+08:00 独立 GR00T 微调结果迁移评估

- 状态：评估完成，未进入实现。
- 结论：独立 GR00T N1.7 checkpoint、Cosmos-Reason2-2B backbone、new_embodiment、13D state/action、三路相机和当前 LeRobot Processor 基本兼容；现有 v2.1 数据不能直接被当前 LeRobot v3 Dataset 使用。
- 验证：单样本 Processor 生成 `state [1,1,132]`、`action [1,40,132]`、`action_mask [1,40,132]`，前 16 个时间步和前 13 个动作维度有效；Postprocessor 解码为 `[1,16,13]`；本地 backbone 路径可读；LeRobotDatasetMetadata 对 v2.1 数据抛出 BackwardCompatibilityError。
- 产物：`GR00T_LEROBOT_MIGRATION_ASSESSMENT.md`；新增 EV-011、EV-012。
- 边界：未执行全量 v2.1→v3.0 转换、完整 GPU forward、LeRobot 实际训练和真实机器人部署；未修改产品源码或原始数据。
- 推荐下一步：用户确认后只转换 1 个 episode 为 v3，完成 LeRobotDataset/Processor/model forward smoke test，再决定全量转换和训练；同时将 Processor 的本地 backbone 路径参数化。

## 2026-07-27T20:00:00+08:00 GR00T 迁移实现与训练前闭环

- 状态：已完成训练前迁移验证，未启动正式微调。
- 数据：新增 `examples/dataset/convert_gr00t_v21_to_v30.py`，将原始 v2.1 数据只读重建为 `/mnt/data/gr00t-finetune/datasets/lerobot_dataset_right_o6_13d_v30`；结果为 v3.0、148 episodes、47250 frames、30 FPS，三路 H.264 视频可读。
- Processor：修改 `src/lerobot/policies/groot/processor_groot.py`，raw checkpoint 优先读取 `processor_kwargs.model_name`，自动使用本地 Cosmos backbone；相对动作资产同步继承该路径。
- 模型：独立 checkpoint 在 CPU 由 `GrootPolicy` 成功加载，唯一缺失为未使用的 `backbone.model.lm_head.weight`；从 v3 数据经过 Processor 后 `predict_action_chunk` 成功输出 finite `[1,16,13]`。
- 证据：EV-013、EV-014、EV-015；Project Log 校验通过；ruff 通过。
- 边界：未执行正式训练、GPU forward/显存吞吐、checkpoint resume 或真实机器人 rollout。
- 下一步：用户手动运行短训练 smoke test；释放 GPU 后补充 GPU 验证。
