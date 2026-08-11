# Engineering Spec - TASK-002

## Objective

接入自训练 GR00T N1.7 full checkpoint，使其可通过 DexBot 的统一 policy service 离线推理，并向通用 runtime 输出 absolute 13D action chunk。

## Non-goals

- 不启动 ROS 节点、不连接相机或机器人 service。
- 不执行 shadow rollout，不下发任何机器人命令。
- 不修改 `PolicyRuntimeNode`、`RolloutCoordinator`、`InferenceScheduler`、SafetyGate 或机器人执行模块。

## Current Behavior and Evidence

- 当前 `lerobot_backend.py` 固定依赖 `LinkerPolicyBackend` 的命名输出，不能加载 GR00T 原生 tensor checkpoint。
- checkpoint 位于 `/mnt/data/gr00t-finetune/outputs/lerobot_qingdao_pouring_gr00t_n1_7_v2_2cam/checkpoints/014051/pretrained_model`，为 30 Hz、40-step、13D relative-action GR00T。
- 离线 probe 已验证 `preprocessor -> predict_action_chunk -> postprocessor` 可将 native relative chunk 解码为有限的 absolute `(1, 40, 13)`。

## Target Behavior

- 新 `groot` 服务端 backend 在一次 infer 调用内完成 preprocessor、模型预测和完整 postprocessor 解码。
- 服务端仅返回 absolute 13D actions，声明 `raw_action_horizon=40`、`supports_rtc=false`。
- checkpoint sidecar 与模型注册描述两相机 `cam_top`/`cam_right_wrist`、30 Hz non-RTC `latest_smooth` shadow 配置。

## Affected Components

- `backend/policy_backends/groot_backend.py`
- backend registry、artifact migration、artifact/deployment sidecars
- `io_contracts.yaml`、`policy_templates.yaml`、`policy_models.yaml`
- backend、artifact、model-service tests

## Failure Handling

- checkpoint 结构、维度、相机映射、deployment contract 或 action 输出异常时 fail closed。
- GR00T processor 额外声明 `cam_left_wrist` 时，不静默忽略；只接受并测试已知的双相机兼容行为。
- 禁止 RTC native chunk reuse。

## Verification Matrix

| Check | Evidence | Hardware |
|---|---|---|
| artifact / contract schema | unit test + inspect tool | none |
| backend output shape / finite / semantics | focused backend test + recorded sample probe | GPU only |
| unified WebSocket service boundary | model-service integration test | localhost only |
| runtime bundle config | config loader test | none |
| camera/coordinate/pose agreement | later shadow rollout | real device required |

## Open Questions and Authority

- B decision `DEC-002` fixes the server-side backend boundary.
- ROKAE and Luoshi are confirmed as the same physical device.
- Joint zero, coordinate convention and initial pose remain unverified and prohibit command approval.
