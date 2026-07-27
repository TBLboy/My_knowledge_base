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
