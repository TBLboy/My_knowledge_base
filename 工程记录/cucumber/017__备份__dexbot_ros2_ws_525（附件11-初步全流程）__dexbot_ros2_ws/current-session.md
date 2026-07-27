# Current Session

## Last Updated

- 2026-06-03 17:39 Local Time

## Current Objectives

- [x] 豆腐感知节点迁移（tofu_perception_node + constrained_obb + VisionGeometryTracker 适配）
- [x] 启动指南.md 简化更新
- [x] **豆腐 TCP offset 拆分**：黄瓜/豆腐各用独立 TCP 参数
- [x] **Phase6 Vision 参数覆写迁移**：竖切预备 `after_rotation_2` 使用独立视觉参数
- [ ] **全流程编排启动测试**：`tofu_workflow_execute.launch.py`
- [ ] 调优 `tofu_tcp_offset` 参数使豆腐放刀位置正确
- [ ] 黄瓜全流程实物切割测试

## Current Business Logic Position

- Main path: 多任务视觉架构（黄瓜 + 豆腐），共享上游 vision（SAM3 + pose_estimator），各自独立 perception 节点
- `prepare:after_rotation_2`（phase6 竖切预备）现在支持 `vision_override`，通过 `tofu_perception_node` 运行时参数 + reset 服务切换感知参数

## 已完成的工作（本次会话）

1. **全流程编排第一次启动日志分析**：
   - 确认 `realsense2_camera_node` 报 `No RealSense devices were found`（USB 连接问题）
   - SAM3 初始化后等待彩色图、hand_eye_static_tf_publisher 等待 camera_link TF 等竞态
   - `vision_timeout_s: 5.0` → 改为 15.0（已改 `tofu_workflow_params.yaml`）

2. **Phase6 Vision 参数覆写迁移**：
   - `tofu_prepare_params.yaml` → `after_rotation_2` 新增 `vision_override`（33 个视觉参数，分位数与老版 `phase6_vision` 一致）
   - `tofu_perception_node.py` → 新增 `add_on_set_parameters_callback` + `~/reset_state` Trigger 服务，支持动态切换参数并清空滑动窗口
   - 新建 `cuttofo_skill_common/perception/tofu_perception_override.py` → 封装覆写客户端（SetParameters + reset_state + 白名单过滤）
   - `tofu_prepare_workflow.py` → 在 `after_rotation_2` 视觉等待前自动应用 vision override
   - 3 包编译通过，运行时 `param set` + `reset_state` 验证成功

## 修改的文件

- `cuttofo_orchestrator/config/tofu_workflow_params.yaml` — `vision_timeout_s: 5.0 → 15.0`
- `cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml` — `after_rotation_2` 加 `vision_override`
- `cuttofo_skill_tofu_perception/tofu_perception_node.py` — 运行时参数 + reset 服务
- `cuttofo_skill_tofu_perception/package.xml` — 加 rcl_interfaces, std_srvs
- `cuttofo_skill_common/perception/tofu_perception_override.py` — **新建** helper
- `cuttofo_skill_common/perception/__init__.py` — 导出新符号
- `cuttofo_skill_common/package.xml` — 加 rcl_interfaces, std_srvs
- `cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py` — vision override 插入点

## Problems And Resolutions

- `perception_override.py` 最初用 `node.get_clock().now()` 超时，不适用于 sleep 循环 → 改为 `time.monotonic()` + `time.sleep(0.02)`
- colcon build 因 underlay 包 `cuttofo_skill_common` 已存在 → 加 `--allow-overriding` 参数

## Verification

- 3 包编译通过，Python 语法检查 0 错误
- `get_prepare_profile('after_rotation_2')` 加载 33 个 vision_override 参数
- `tofu_perception_node` 启动正常，`ros2 param set` 成功，`reset_state` 返回 success
- linter 通过，无新增错误

## Current State

- `after_rotation_2` vision override 已就绪，全流程编排第 5 步会自动触发
- 全流程 `vision_timeout_s` 已改为 15.0
- 刀已在右手中，豆腐横切（phase2-5）待实机验证，竖切（phase6-7）待实机验证

## Next Steps

- **全流程编排启动测试**：
  - T1: `dual_xcore_controllers.launch.py`
  - T2: `tofu_workflow_execute.launch.py`
  - 观察 step 1-2（first_cut → round_1）
  - touch continue 文件推进 step 3-6
- 调优 `tofu_tcp_offset`
- 黄瓜全流程切割测试
