# 当前需求摘要

- 当前目标：Robam `pan_pour` 倾倒菜品子 Policy 第一版
- 当前基线：`REQ-002` revision 7，状态 `active`
- 版本策略：不替换现有 `food` 子 Policy；只新建自己的 PanPour 子 Policy，只做编排，不开发新 Motion Skill

## REQ-002 范围

- 新建 Home 侧 `policy/robam/sub_policy_pan_pour.py` 与 `config/robam/sub_policy_pan_pour.yaml`，FullPolicy 键为 `pan_pour`
- 动作链使用现有 `PickSkill`、`PourSkill`、`PlaceSkill`、`local_delta_replay` 和 `MoveCartesianApi`
- 流程：等待锅把 → 预抓取/抓取/闭合/抬锅 → 底盘占位 → 等待餐盘 → 视觉引导到倾倒起点 → 增量轨迹回放 → 回到抬锅点 → 底盘返回占位 → 放回/张开/回 home
- 预抓取点由视觉抓取点沿中心坐标系 Z 轴正方向、按 `approach_distance_m` 外推
- 抬锅固定点位可直接写 7 个弧度关节角，`move_to_pick_retreat` 使用 `mode: joints` 走 `MOVE_JOINTS`；也可沿用 `linear_cartesian`
- YAML 保存 pick/pour/place 三个 skill 动作模板，包括 `plan_type`、`arm_type`、`profile`、`mode`、`speed`、`accel`、`wait_time`、`hand_action_name` 和 `replay_file`；Policy 私有计算参数和固定臂姿按现有 `PlatePourPolicy` 模式放 Python 顶层常量
- Policy 只做工具点转法兰点，下发法兰目标点在中心坐标系下的表示
- 底盘和正式工具坐标切换只保留接口占位，当前不执行、不等待、不阻塞

## 范围外

- 不修改 Motion Skill、`manipulation.py`、执行器原语和 FullPolicy
- 不实现正式底盘导航和工具坐标切换
- 不修改或替换现有 `food` 子 Policy
- 不实现抓取确认、失败重试、落料完整性和复杂异常回退

## 待实现前确认

- 左臂 O6 抓取/松开的 `ACTION_NAME + POSITION`
- 真机联调确认固定关节角、手部角度、倾倒起点一致性和回放路径解析

## 已确定实现细节

- 视觉引导到倾倒起点使用 `MoveCartesianApi`
- 视觉盘子字段：新版感知包 `dexbot-perception 1.0.19` 的 `scene_stir_frying` 后处理输出 `class_name=plate_center`，坐标在 `ScenePerception.objects[].pose.position`
- 抓取接近方向固定为中心坐标系 Z 轴；预抓取点 = 抓取点 + [0, 0, approach_distance_m]，位于抓取点正上方，抓取运动沿 -Z 下降到抓取点
- 抬锅 `move_to_pick_retreat` 支持 `mode: joints`，固定关节角直接写 7 个弧度角，经 `/robot_driver/move_joints` 执行；当前 food 参考实现是 `linear_cartesian`
- 抬锅完成后直接进入底盘占位，不执行 `move_to_pick_end`，不保留旧 teach 的 `POUR_READY_JOINTS`
- 倾倒轨迹回放完成后 `upright_action` 以 joints 回到 `LIFT_JOINTS` 抬锅点，再进入底盘返回占位
- TCP：抓锅 `TCP_GRASP`（旧 `tcp_grasp`）、倾倒 `TCP_PAN`（旧 `tcp_pan`）做 Policy 内 TCP→法兰换算；任务开头已接入 `set_tcp(left_default)`，使用 `tcp_profiles.yaml` 中全 0 profile，不额外定义 `SET_TCP_ZERO_*`
- 增量轨迹文件：`robot_motion_executor/src/dexbot_motion_executor/dexbot_motion_executor/skills/robam/trajectories/pour_delta.json`，已从备份复制，103 点，`arm_side=left`
- 左臂手部开合参考旧版 `hand_presets.yaml` 的 `open` / `grasp_pan` 角度和力矩参数
- 锅把视觉字段参考旧版 `perception_adapter.py`：`pot_handle_center` / `pot_inner_handle`，由两者位置计算 PCA 轴；新版感知包已输出 `plate_center`，真机复测待做
- PanPour 视觉只消费 `pot_handle_center`、`pot_inner_handle` 和 `plate_center`，不使用原始 `pot_handle`/`plate`；抓取位置按 `pot_handle_center + GRASP_OFFSET_ALONG_HANDLE_M * normalize(pot_handle_center - pot_inner_handle) + GRASP_OFFSET_CENTER_M` 计算，抓取姿态仍固定

## 假视觉真机验证方案（已澄清）

- 真实机械臂 + 假视觉：在手眼标定和真实感知暂不可用时，不阻塞 PanPour 动作链验证
- 假视觉节点一次发布 `pot_handle_center`、`pot_inner_handle`、`plate_center`，全部中心坐标系，`scene_valid=true`；不做分阶段切换发布对象
- 点位采集：用户手动把左臂摆到抓锅点和倾倒轨迹回放起始位，读取 `/robot_driver/get_arm_pose` 的中心坐标系位置；`pot_inner_handle` 根据转换后点位手动填写
- 测试阶段 `TCP_GRASP/PAN` 和 `GRASP_OFFSET_ALONG_HANDLE_M` 临时为 0；Policy 下发中心坐标系法兰目标，Driver 负责转换到左臂 base
- 全链：`set_tcp -> wait_handle -> pick -> wait_plate -> pour -> place -> completed`；底盘移动继续占位跳过
- 假视觉代码：本机私有包 `kitchen_robot_home/src/dexbot_fake_vision/`，通过 `.git/info/exclude` 排除 Git 跟踪；`config/fake_scene.yaml` 未填点前禁止启动

历史基线 `REQ-001` 已标记为 superseded，保留在 `.project-log/requirements/baseline.yaml`。

机器可读事实源：`.project-log/goals/active-goal.yaml`、`.project-log/business-logic/atoms.yaml`、`.project-log/requirements/baseline.yaml`。
