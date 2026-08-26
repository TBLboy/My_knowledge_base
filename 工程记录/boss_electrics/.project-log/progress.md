# Progress

倾倒入盘技术路线、V1 业务澄清和技术选型已完成；当前进入工程实施阶段。

## 2026-08-26 InitializeSkill 接入 PanPour

- PanPour 状态机接入 `initialize`：`set_tcp -> initialize -> wait_handle -> pick -> wait_plate -> pour -> place -> completed`。
- `InitializeSkill` 新增 `hand_angles` 手部模式和 `joints` 回家模式，已有 `gripper`/`cartesian` 模式保留。
- 已按用户提供值写入 home：左臂 `127.1/77.2/-89.3/123.2/-14.1/7.0/0` 度，转换为弧度 `[2.2183134793, 1.3473941825, -1.558579022, 2.1502456385, -0.2460914245, 0.1221730476, 0.0]`；手部复用 `预抓把手`（`[100,100,100,100,100,100]`）。
- 已启用 PanPour pick 的 `move_to_pick_initial`，当前值按 `77/35/-60/90/36/-7/17` 度换算为弧度：`[1.343903524, 0.6108652382, -1.0471975512, 1.5707963268, 0.6283185307, -0.1221730476, 0.2967059728]`。
- PanPour place 收尾调整：`move_to_place_retreat` 填充 `pick_initial` 关节角，`move_to_place_end` 填充回 `home`。
- 验证通过：两个仓库 compileall、对应包 colcon build、Policy 生成 initialize 步骤、Motion 转 `GRIPPER_ACTION + MOVE_JOINTS`、`hand_angles` 转 `SET_HAND_ANGLES + MOVE_JOINTS`。

## 2026-08-26 下午 全流程跑通（视觉感知 + 机械臂动作链）

### 已解决的问题
1. **perception task_name 缺失**：添加 `task_name: "boss_kitchen_scene_stir_frying"` 到 `perception_params.yaml`，激活后处理输出 `pot_inner_handle`/`pot_inner_tip`/`plate_center`
2. **左手 CAN 接口错误**：切换为正确 CAN 接口后手部动作正常执行
3. **倾倒阶段 IK 无解**：调整 `POUR_OFFSET_CENTER_M`(0.08→0.2)、`POUR_INITIAL_FLANGE_RPY`(改为与抓锅同姿态)、`TCP_PAN_TRANSLATION`(改为非零偏移)
4. **YOLO 模型路径**：创建 `local_models/yolo/` 并软链接 `yolo26x_obb.pt` → `boss_kitchen_scene_stir_frying_obb.pt`
5. **TCP 标定脚本迁移**：`tcp_calibration.py` 迁移到 `local_tcp_calibration/`，加入 `.git/info/exclude`

### 当前状态
- **视觉全流程跑通**：pick（抓锅）→ wait_plate → pour（倾倒）→ place，放开底盘占位
- 不带底盘，底盘步骤继续占位跳过
- 坐标系：中心坐标系，`toolset.ref.trans` 左臂 `[0, -0.0787, 0]` 右臂 `[0, +0.0787, 0]`
- `get_arm_pose` 返回 `flangeInBase`（BASE 坐标系），和 SDK 原生坐标系一致
- TCP 偏移量 xyz 定义在**法兰坐标系**自身
- 手眼标定已完成（左+右+中心坐标系）

### 关键参数（当前有效值）
- `TCP_GRASP_TRANSLATION = (-0.006, 0.012, 0.116)` 法兰坐标系
- `TCP_PAN_TRANSLATION = (-0.286, 0.012, 0.116)` 法兰坐标系
- `POUR_OFFSET_CENTER_M = (0, 0, 0.2)` 中心坐标系偏移
- `POUR_INITIAL_FLANGE_RPY = (-1.70, 0.076, -1.73)` 与抓锅姿态相同
- `ref.trans` 左臂 `[0, -0.0787, 0]` 右臂 `[0, +0.0787, 0]`

### 下一步
- 真机带底盘联调（底盘步骤打通后接入）
- 或继续优化倾倒轨迹回放

### 2026-08-26 code_integration 历史清理

- home 本地 `code_integration` 领先远端 6 个提交；motion 已合并远端王韵博的 `pickplace 力控触觉双闭环` 提交。
- 未推送历史里的大模型 `.pt` 和 `robot_params.yaml.bak` 已通过 `filter-branch` 从 Git 历史移除，仅重写本地提交，未重写 `origin/code_integration`。
- 本地模型文件和 `.bak` 已从备份分支恢复，加入 `.git/info/exclude` 不跟踪。
- 备份分支：`backup/code_integration_before_cleanup_0826`。

## 2026-08-26 中心坐标系生成并落盘

- 修正后的左臂标定（16 样本，`1.52 mm / 0.344°`）与当前右臂标定（11 样本，`1.99 mm / 0.865°`）已用于生成中心坐标系。
- 已写入 `src/dexbot_bringup/config/calibration/left_calibration_result.yaml`、`right_calibration_result.yaml`、`center_calibration_result.yaml`，并把 `toolset.ref.trans` 与 base frame 配置写入 `src/dexbot_bringup/config/robot_driver/robot_params.yaml`。

## 2026-08-24 PanPour 子 Policy 实现与验证

- 新增 `policy/robam/sub_policy_pan_pour.py` 与 `config/robam/sub_policy_pan_pour.yaml`，实现 wait_handle/pick/wait_plate/pour/place/completed 状态机。
- 使用现有 PickSkill、PourSkill、PlaceSkill 完成预抓取、抓取、抬锅、倾倒起点、增量轨迹回放、回正，放回、张开、回 home。
- PanPour 私有业务参数按 `PlatePourPolicy` 模式放在 `sub_policy_pan_pour.py` 顶层常量，YAML 只保存三个 manipulation skill 动作模板。
