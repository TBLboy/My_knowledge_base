# Communication Architecture

## 右臂控制接口 (ROS Services)

XcoreArmAdapter 通过以下 ROS services 控制右臂（namespace: /arm_r）：

| Service | Type | Purpose |
|---------|------|---------|
| /arm_r/robot/get_state | GetRobotState | 读取关节角、法兰位姿 |
| /arm_r/robot/move_joints | MoveJoints | 关节空间运动 |
| /arm_r/robot/move_joint_sequence | MoveJointSequence | 多段关节运动 |
| /arm_r/robot/move_cartesian | MoveCartesian | 笛卡尔运动 |
| /arm_r/robot/move_rt_cartesian_path | MoveRtCartesianPath | RT 笛卡尔路径 |
| /arm_r/robot/enable_arm | EnableArm | 使能/失能机械臂 |

这些由 `dexbot_bottom_layer/xcore_controller_node.py` 提供，
`dual_xcore_controllers.launch.py` 使用 PushRosNamespace + remap 映射到 /arm_r/ 前缀。

## 左臂控制接口 (SDK Direct)

XcoreDirectExecutor 通过 TCP/IP 直连左臂 SDK：

| 功能 | SDK 方法 |
|------|---------|
| 连接 | robot.connect() |
| TCP 位置运动 | move_tcp_fixed_orientation() |
| 关节运动 | robot.move_to_joint_target() |
| RT 笛卡尔路径 | robot.move_rt_cartesian_path() |
| 状态读取 | robot.get_joint_positions(), robot.get_cartesian_pose() |

## 视觉 Topic 映射 (cuttofu 命名空间)

| Canonical Topic | Legacy Topic | Type |
|----------------|-------------|------|
| /cuttofu/vision/text_prompt | /sam3/text_prompt | String |
| /cuttofu/perception/detected_objects | /detected_objects | ObjectStateArray |
| /cuttofu/perception/objects_with_pose | /objects_with_pose | ObjectStateArray |
| /cuttofu/perception/segmentation_result | /sam3/segmentation_result | SegmentationResult |

## Skill Action / Service 接口

| Action/Service | Type | Purpose |
|---------------|------|---------|
| /cucumber_hold/execute | ExecuteCucumberHold | 左臂按住/释放黄瓜 |
| /tofu_prepare/execute | ExecuteTofuPrepare | 右臂预备切姿 |
| /tofu_cut_round/execute | ExecuteTofuCutRound | 右臂切割 |
| /tofu_vertical_cut/execute | ExecuteTofuVerticalCut | 右臂垂直切割 |
| /handle_approach/execute | ExecuteHandleApproach | 刀柄接近抓取 |
| /tofu_cut_round/resume | ResumeTofuCutRound | 切割恢复服务 |

## 双机械臂坐标变换

右臂基座检测到的黄瓜点 p_R → T_base_left_right @ p_R → p_L

```
T = [ diag(1, -1, -1)  |  t_calib ]
    [ 0 0 0            |  1      ]
```

t_calib 从 calibration_result_left.yaml 读取，默认兜底 [0, 0, -0.20]。
