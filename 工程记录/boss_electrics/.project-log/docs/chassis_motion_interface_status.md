# 底盘运动接口现状

检查时间：2026-08-15

## 结论

底盘运动控制 ROS 接口已经由 `dexbot_robot_driver` 暴露，但当前 `robot_type=O6Luoshi` 不是带底盘能力的机器人类型，因此这些 service 注册后会返回 `active robot does not provide chassis control`。

## 已存在的底盘接口

- `/robot_driver/chassis/initialize`
- `/robot_driver/chassis/control`
- `/robot_driver/chassis/mark_current_pose`
- `/robot_driver/chassis/navigate_to_marker`
- `/robot_driver/chassis/get_navigation_status`

接口消息定义位于 `kitchen_robot_home/src/dexbot_interfaces/srv/`，service 注册位于 `/opt/ros/humble/lib/python3.10/site-packages/dexbot_robot_driver/robot_driver_node.py`。

## 当前限制

- 主仓库 `src/dexbot_bringup/config/robot_driver/robot_params.yaml` 使用 `robot_type: O6Luoshi`。
- `O6Luoshi` 不实现 `ChassisRobotInterface`。
- 带底盘能力的类型是 `O6LuoshiYunji`（云迹）和 `O6LuoshiDaka`（大咖）。
- 主仓库 robot 参数中没有 `chassis:` 配置段。
- `robot_motion_executor` 没有底盘 Skill/Primitive。
- `PanPourPolicy` 目前仍通过 `update_base_positioned()` 等待外部底盘完成上报，没有直接调用底盘 service。

## 后续接入前置条件

1. 确认实际底盘厂商是云迹还是大咖。
2. 将 `robot_type` 改为对应类型。
3. 在 `robot_params.yaml` 补全 `chassis` 参数。
4. 验证底盘 service 可用后，再决定由 Planner 客户端还是 MotionExecutor Skill 发起移动。
5. 接入后更新本记录状态并补充真机验证证据。
