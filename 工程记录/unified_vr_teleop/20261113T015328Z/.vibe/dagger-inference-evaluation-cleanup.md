# DAgger、推理与评测功能清理清单

日期：2026-10-29。范围：`unified_vr_teleop_franka/Dagger_web` 当前 master 快照。目标是仅保留普通 VR 遥操作数据采集；本轮只读盘点，不删除代码。

## 清理原则

- 保留 PICO/XR 接收、普通 VR 遥操作、机器人控制、相机/音频/机器人状态采集、录制、上传和采集数据回放质检。
- 删除 DAgger 人工接管/策略交互、规则推理、远程策略、轨迹策略执行、评测/RL 模式及其专属页面和测试。
- `ui_playback.py`、`app/storage/` 的采集文件回放、HDF5 转换和上传不能因“replay”字样误删；删除的是“用历史轨迹驱动机器人”的策略 replay。
- 本清单不把普通录制的成功/废弃结果标记误判为 DAgger；需要保留普通 episode 结束流程。

## 建议删除：纯功能模块

| 路径 | 原因 | 处理 |
| --- | --- | --- |
| `app/inference/__init__.py` | 推理包入口 | 删除 |
| `app/inference/rule.py` | 规则策略配置/动作 | 删除 |
| `app/inference/worker.py` | 独立规则推理进程 | 删除 |
| `app/teleop/dagger/backend.py` | 未接入的策略后端占位协议 | 删除 |
| `app/teleop/dagger/journal.py` | DAgger/策略步骤 journal | 删除 |
| `app/teleop/dagger/local_policy.py` | 本地规则推理客户端 | 删除 |
| `app/teleop/dagger/remote.py` | 远程策略接入 | 删除 |
| `app/teleop/dagger/replay.py` | 轨迹策略执行回放 | 删除 |
| `app/teleop/dagger/smoke.py` | DAgger/策略 smoke test | 删除 |
| `app/teleop/dagger/episodes.py` | DAgger/evaluate/rl 模式、策略 episode 标记 | 删除或重构后删除；普通录制停止逻辑不能一并删除 |
| `app/teleop/dagger/__init__.py` | 删除后无用途 | 删除 |
| `robot/franka/policy.py` | Franka TCP 策略输入校验 | 删除 |
| `robot/franka/remote.py` | Franka 远程策略 HTTP 客户端 | 删除 |
| `tools/deploy/install-inference.sh` | 独立推理环境安装 | 删除 |

## 建议删除：纯 DAgger/策略 UI 和入口

| 路径/位置 | 原因 | 处理 |
| --- | --- | --- |
| `app/ui/ui_capture_modes.py` | DAgger、模型评测、RL、规则运动 tab 和按钮 | 删除，并从 `ui_record.py` 移除调用 |
| `main.py` `/api/policy/observation` | 仅供远程策略取观测 | 删除 |
| `main.py` `Episodes` 创建、关闭和生命周期注册 | 依赖 DAgger episode 服务 | 删除；改回普通录制生命周期 |
| `config/config.yaml` `policy:` 整段 | replay/rule/remote 策略配置 | 删除 |
| `config/config.yaml` DAgger 运行目录/策略专属键 | 仅供策略或 DAgger | 删除，逐项核对 |

## 必须保留但需要编辑

| 路径 | 保留内容 | 删除/修改内容 |
| --- | --- | --- |
| `app/teleop/control_runtime.py` | 公共 XR、普通人工 VR、hold、reset、退出、控制目标 | 删除 policy imports、策略轮询、Authority 的策略分支、journal 和 policy command；保留普通 collect 路径 |
| `app/teleop/control_worker.py` | 通用/机器人写入、反馈、超时、hold、reset | 删除 policy_generation 和策略专属目标门控；保留通用目标新鲜度检查 |
| `app/teleop/control.py` | 普通控制命令 IPC | 删除 `policy-start`、`policy-stop` 及策略队列 |
| `app/teleop/capture_workflow.py` | VR 启动/停止和普通录制流程 | 删除 `rule-start`、`rule-stop`、模式切换和 DAgger 条件 |
| `app/teleop/supervisor.py` | 启动/停止控制进程 | 删除 policy command、dagger mode 读取和策略专属状态；保留普通控制启动 |
| `app/teleop/input.py` 或现有 `dagger/input.py` | PICO 按键、Grip、普通使能/暂停 | 保留公共 Buttons/普通人工控制所需部分；删除 takeover/policy 状态，必要时迁移到公共模块后删除 dagger 目录 |
| `app/teleop/session.py` / `integration.py` | 普通会话和 manager | 删除 Episodes 注入、模式状态和 pending 策略结果 |
| `app/ui/ui_teleop.py` | 普通 VR 连接、启动、停止、录制按钮和状态 | 删除任务模式选择、策略按钮、DAgger 状态刷新和策略文案 |
| `app/ui/teleop_guidance.py` | 若仍显示普通 VR 操作指导则保留 | 删除 policy/takeover 文案和按钮，只保留普通人工遥操作指导 |
| `app/ui/ui_record.py` | 普通录制、任务、回放入口 | 删除 `build_capture_modes` 调用及 DAgger-only 控件；保留 recording/playback/quality actions |
| `app/teleop/recording.py` | 录制元数据和机器人数据格式 | 保留；删除仅供 DAgger 的字段/逻辑前先核对普通录制依赖 |
| `app/storage/recorder.py` | 普通视频、音频和机器人状态写入 | 保留；删除 DAgger 标记只在确认不影响普通 episode 后进行 |
| `app/storage/h5_export.py` | 采集数据 HDF5 导出 | 保留；不是策略 replay |
| `robot/franka/runtime.py` | 当前 Franka 普通人工控制的过渡入口 | 删除 policy/remote 分支，保留普通 VR 控制；后续再按已批准架构收敛为公共 runtime/worker + adapter |
| `robot/franka/recording.py` | Franka 遥测、普通采集回放/导出 | 保留；这是 recording，不是策略回放 |

## 测试清单

### 删除

- `tools/tests/test_dagger.py`
- `tools/tests/test_local_policy.py`
- `tools/tests/test_replay_policy.py`
- 仅验证 DAgger/策略按钮、规则推理、远程策略的测试用例

### 保留并改写

- `test_capture_workflow.py`：保留普通 `vr-start` / `vr-stop` / recording 流程，删除 rule/policy 场景。
- `test_record_page_actions.py`、`test_recording.py`、`test_capture_integration.py`：保留普通采集和录制验证。
- `test_teleop_guidance.py`、`test_teleop_readiness.py`、`test_ui_runtime.py`：删除 DAgger 文案和策略状态断言，保留普通 VR/UI 行为。
- `test_franka.py`：保留 Franka 普通控制/反馈/复位/worker/页面测试，删除 remote policy 相关测试。
- `test_robot_profiles.py`：保留 config/adapter/profile 测试，删除 replay/policy 相关断言。

## 暂不删除

- `app/ui/ui_playback.py`、`app/storage/sessions.py`、`app/storage/h5_export.py`：它们承担采集数据回放、质检、转换和上传，不等于策略回放。
- `app/teleop/recording.py`、`robot/franka/recording.py`：承担普通采集数据记录/导出。
- `app/teleop/input.py` 中普通 Grip/按钮逻辑：需要先迁移/裁剪，不能按目录名直接删除。
- `app/teleop/control_runtime.py` 和 `control_worker.py`：它们虽包含策略代码，但仍承担普通 VR 控制，必须裁剪而不是整体删除。

## 删除顺序

1. 先裁剪 UI/入口和配置，默认系统只能进入普通 VR 采集。
2. 再删除 inference、policy、remote、strategy replay 纯模块。
3. 裁剪公共 control runtime/worker/session，保留普通人工控制。
4. 清理测试和依赖/脚本。
5. 运行静态引用检查、普通 VR 离线测试和 Franka 离线测试。
6. 最后检查 `git diff`，确认没有误删 recording、playback、上传和机器人控制代码。

## 需要用户确认的边界

- 普通采集的成功/失败/废弃按钮和 episode 元数据是否保留：本清单按“保留”处理。
- 采集数据回放质检是否保留：本清单按“保留”处理。
- RLinf 适配代码是否当前仓库已有实际调用：本清单按“删除本地策略/DAgger功能，但不删除外部接口未来需要的公共 VR/observation 基础”处理；具体接口删除前再核对姜灏当前分支。
