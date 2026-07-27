# Config Schema

## cucumber_hold_params.yaml

| Parameter | Type | Default | Runtime Mapping | Used By | Notes |
|---|---|---|---|---|---|
| robot.ip | string | 192.168.2.160 | XcoreDirectExecutor._robot_ip | CucumberHoldNode | 左臂 IP |
| robot.arm_type | string | left | XcoreDirectExecutor._arm_type | CucumberHoldNode | |
| robot.tool_offset.[x,y,z] | float[3] | [0, 0.02, 0.19] | XcoreDirectExecutor._tcp_offset | CucumberHoldNode | |
| perception.text_prompt | string | cucumber | VisionPromptClient.publish_prompt() | CucumberHoldNode | SAM3 prompt |
| perception.lock_min_samples | int | 2 | CucumberHoldLock._lock_min_n | CucumberHoldNode | SAM ~1Hz |
| perception.lock_max_std_m | float | 0.03 | CucumberHoldLock._lock_max_std | CucumberHoldNode | 稳定性阈值 |
| perception.hold_along_axis_fraction | float | 1 | CucumberHoldLock.configure() | CucumberHoldLock | 沿主轴偏移比例 |
| perception.press_down_m | float | 0.0 | CucumberHoldLock.configure() | CucumberHoldLock | 按压偏移 |
| profiles.default.motion_mode | string | nrt | execute_cucumber_hold() | CucumberHoldWorkflow | nrt / rt |
| profiles.default.manual_offset_m | float[3] | [-0.03, 0, 0.05] | press_left = b_left + offset | CucumberHoldWorkflow | 左臂基座 |
| profiles.default.nrt_direct_to_press | bool | false | _nrt_tcp_targets() | CucumberHoldWorkflow | false=先 approach 再 press |
| profiles.default.nrt_approach_min_separation_m | float | 0.01 | _nrt_tcp_targets() | CucumberHoldWorkflow | 两段最小间距 |
| profiles.release.home_joint_positions_deg | float[7] | [-2.2, 45.3, ...] | executor.move_to_joints() | CucumberHoldWorkflow | |

## tofu_prepare_params.yaml

| Parameter | Type | Default | Runtime Mapping | Used By | Notes |
|---|---|---|---|---|---|
| profiles.cucumber.perception_text_prompt | string | cucumber | VisionPromptClient | TofuPrepareNode | 覆盖默认 prompt |
| profiles.cucumber.class_filter | string | cucumber | VisionGeometryTracker | TofuPrepareNode | 视觉过滤 |
| profiles.cucumber.use_shared_hold_geometry | bool | true | vision_tracker.wait_valid() | TofuPrepareNode | 复用 hold 几何 |
| profiles.cucumber.plane_angle_deg | float | 90 | build_target_rotation() | TofuPrepareWorkflow | 竖切 |
| profiles.cucumber.target_offset_m | float[3] | [-0.02, 0.03, 0] | apply_cucumber_prepare_target_offsets() | TofuPrepareWorkflow | |
| profiles.cucumber.ik_retry_count | int | 20 | solve_prepare_candidates() | TofuPrepareWorkflow | |

## tofu_cut_round_params.yaml

| Parameter | Type | Default | Runtime Mapping | Used By | Notes |
|---|---|---|---|---|---|
| profiles.cucumber.cut.cycles | int | 10 | build_cut_cycle_waypoints() | TofuCutRoundWorkflow | 切割次数 |
| profiles.cucumber.cut.cut_move | float | 0.085 | build_cut_cycle_waypoints() | TofuCutRoundWorkflow | 切割深度 m |
| profiles.cucumber.cut.step_z | float | -0.003 | build_cut_cycle_waypoints() | TofuCutRoundWorkflow | 每刀进给 |
| profiles.cucumber.cut.stiffness | float[6] | [3000]*6 | _run_rt() | TofuCutRoundWorkflow | 阻抗刚度 |
| profiles.cucumber.return.skip_return_anchor | bool | true | execute_cut_round() | TofuCutRoundWorkflow | |
| profiles.cucumber.human_wait.skip_human_wait | bool | true | execute_cut_round() | TofuCutRoundWorkflow | |

## cucumber_workflow_params.yaml

| Parameter | Type | Default | Used By | Notes |
|---|---|---|---|---|
| vision_timeout_s | float | 15.0 | orchestrator | SAM ~1Hz |
| steps | list | 4 steps | orchestrator.run() | hold→prepare→cut→release |

## arms.yaml

| Parameter | Type | Default | Used By | Notes |
|---|---|---|---|---|
| right.namespace | string | /arm_r | XcoreArmAdapter | ROS service 前缀 |
| right.tcp_offset | float[3] | [0.01089, 0.12506, 0.25620] | PrepareWorkflow | 右臂 TCP |
| right.urdf.path | string | .../AR5-5_07R-W4C1C1.urdf | OfflineURDFKinematics | IK 求解 |
