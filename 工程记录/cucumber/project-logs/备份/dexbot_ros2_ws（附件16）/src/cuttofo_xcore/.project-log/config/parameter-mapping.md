# Config Schema

## Phase1 Grab Parameters (YAML-sourced via cuttofo_config.yaml)

| Parameter | Type | Default | Valid Range | Runtime Mapping | Used By | Requires Restart | Notes |
|---|---|---|---|---|---|---|---|
| `phase1_grab.robot.right_ip` | string | 192.168.2.161 | Valid IP | `cuttofu_phase1_grab.launch.py → robot_ip` | follow node | No | Right arm controller IP |
| `phase1_grab.robot.left_ip` | string | 192.168.2.160 | Valid IP | `cuttofu_phase1_grab.launch.py → robot_ip` | follow node | No | Left arm controller IP |
| `phase1_grab.lifecycle.wait_before_broadcast_s` | float | 0.5 | ≥0.0 | `phase1_grab_lifecycle_node._wait_s` | lifecycle node | No | Buffer after /task/phase1_complete before broadcast |
| `phase1_grab.lifecycle.broadcast_duration_s` | float | 5.0 | >0.0 | `phase1_grab_lifecycle_node._broadcast_dur` | lifecycle node | No | Duration to broadcast /task/phase1_complete |
| `phase1_grab.perception.sam3_text_prompt` | string | wooden cleaver handle | Any text | `sam3_detector_node.text_prompt` | SAM3 node | No | SAM3 text prompt for knife handle |
| `phase1_grab.perception.sam3_detection_rate` | float | 5.0 | >0.0 | `sam3_detector_node.detection_rate` | SAM3 node | No | SAM3 detection rate (Hz) |
| `phase1_grab.perception.sam3_detection_threshold` | float | 0.3 | 0.0-1.0 | `sam3_detector_node.detection_threshold` | SAM3 node | No | SAM3 confidence threshold |
| `phase1_grab.perception.pose_smoothing_alpha` | float | 0.5 | 0.0-1.0 | `pose_estimator_node.pose_smoothing_alpha` | pose estimator | No | Exponential smoothing factor |
| `phase1_grab.perception.recognition_auto_start_delay_sec` | float | 1.0 | ≥0.0 | `cut_tofu_object_recognition_node.auto_start_delay_sec` | recognition node | No | Delay before recognition auto-start |
| `phase1_grab.perception.handle_keywords` | string | wooden cleaver handle,handle,cleaver handle | Comma-separated | `cut_tofu_object_recognition_node.handle_keywords` | recognition node | No | Keywords for handle recognition |
| `phase1_grab.perception.lock_min_samples` | int | 6 | ≥1 | `cut_tofu_object_recognition_node.lock_min_samples` | recognition node | No | Min samples before locking handle pose |
| `phase1_grab.monitor.hand_o6_close_degrees_csv` | string | 0,0,70,0,0,0 | 6 values 0-100 | `xcore_monitor_handle_sequence_node._hand_o6_close_csv` | monitor node | No | O6 gripper close angles |
| `phase1_grab.monitor.post_grasp_tcp_plus_y_m` | float | 0.35 | ≥0.0 | `xcore_monitor_handle_sequence_node._post_grasp_tcp_plus_y_m` | monitor node | No | TCP retract after O6 grasp |
| `phase1_grab.monitor.post_grasp_joint_home_rad_csv` | string | 7 comma-separated floats | 7 valid radians | `xcore_monitor_handle_sequence_node._post_grasp_joint_home_rad_csv` | monitor node | No | MoveAbsJ joint positions after grasp |
| `phase1_grab.monitor.target_x_compensation_m` | float | -0.03 | Any | `xcore_monitor_handle_sequence_node._target_x_compensation_m` | monitor node | No | X compensation for target pose |
| `phase1_grab.monitor.target_y_compensation_m` | float | -0.02 | Any | `xcore_monitor_handle_sequence_node._target_y_compensation_m` | monitor node | No | Y compensation for target pose |
| `phase1_grab.monitor.target_z_compensation_m` | float | 0.01 | Any | `xcore_monitor_handle_sequence_node._target_z_compensation_m` | monitor node | No | Z compensation for target pose |
| `phase1_grab.monitor.y_before_handle_m` | float | 0.15 | >0.0 | `xcore_monitor_handle_sequence_node._y_before` | monitor node | No | Y offset before handle approach |
| `phase1_grab.monitor.z_before_handle_m` | float | 0.05 | >0.0 | `xcore_monitor_handle_sequence_node._z_before` | monitor node | No | Z offset before handle approach |
| `phase1_grab.monitor.y_step_after_z_m` | float | 0.13 | >0.0 | `xcore_monitor_handle_sequence_node._y_step` | monitor node | No | Y step after Z alignment |
| `phase1_grab.monitor.follow_min_interval_sec` | float | 1.6 | ≥0.2 | `xcore_monitor_handle_sequence_node._follow_min_int` | monitor node | No | Min publish interval between targets |
| `phase1_grab.monitor.post_reach_sleep_before_next_target_sec` | float | 1.55 | ≥0.0 | `xcore_monitor_handle_sequence_node._post_reach_next_gap` | monitor node | No | Extra wait after reached target |
| `phase1_grab.monitor.follow_batch_inter_sleep_sec` | float | 0.05 | ≥0.0 | `xcore_monitor_handle_sequence_node._follow_batch_inter_sleep` | monitor node | No | Sleep between batch waypoints |
| `phase1_grab.monitor.sequence_start_tcp_wait_sec` | float | 3.0 | ≥0.0 | `xcore_monitor_handle_sequence_node._sequence_start_tcp_wait_sec` | monitor node | No | Wait before first TCP read |
| `phase1_grab.monitor.wait_follow_segment_done_timeout_sec` | float | 180.0 | >0.0 | `xcore_monitor_handle_sequence_node._wait_done_timeout` | monitor node | No | Timeout waiting segment-done |
| `phase1_grab.monitor.wait_follow_segment_done_max_retries` | int | 80 | ≥1 | `xcore_monitor_handle_sequence_node._wait_done_max_retries` | monitor node | No | Max retries for segment-done |
| `phase1_grab.monitor.post_sequence_o6_grasp_enable` | bool | true | true/false | `xcore_monitor_handle_sequence_node._post_sequence_o6_grasp_enable` | monitor node | No | Enable O6 close after waypoints |
| `phase1_grab.follow.vel_scale` | float | 0.1 | 0.05-1.0 | `xcore_follow_tcp_chain_node_movej._vel_scale` | follow node | No | Joint speed scaling |
| `phase1_grab.follow.accel_scale` | float | 0.1 | 0.05-1.0 | `xcore_follow_tcp_chain_node_movej._accel_scale` | follow node | No | Joint acceleration scaling |
| `phase1_grab.follow.min_move_interval_sec` | float | 1.5 | ≥0.2 | `xcore_follow_tcp_chain_node_movej._min_interval` | follow node | No | Min time between moves |
| `phase1_grab.follow.hand_o6_settle_sec` | float | 0.45 | ≥0.0 | `xcore_follow_tcp_chain_node_movej._hand_o6_settle_sec` | follow node | No | Settle time after O6 command |
| `phase1_grab.follow.sequence_inter_waypoint_sleep_sec` | float | 0.05 | ≥0.0 | `xcore_follow_tcp_chain_node_movej._sequence_inter_sleep` | follow node | No | Sleep between follow waypoints |
| `phase1_grab.follow.cartesian_interp_steps` | int | 12 | 2-24 | `xcore_follow_tcp_chain_node_movej._interp_steps` | follow node | No | Cartesian interpolation steps |
| `phase1_grab.follow.sdk_ik_pos_tol_m` | float | 0.005 | >0.0 | `xcore_follow_tcp_chain_node_movej._ik_pos_tol` | follow node | No | IK position tolerance |

## Phase1 Migration Parameters (legacy, superseded by YAML-sourced above)

| Parameter | Type | Default | Valid Range | Runtime Mapping | Used By | Requires Restart | Notes |
|---|---|---|---|---|---|---|---|
| `wait_before_launch_s` | float | 0.5 | ≥0.0 | `phase1_monitor_node.wait_s` | phase1_monitor_node | No | Buffer time after receiving /task/phase1_complete before launching Phase2 |
| `phase2_start_phase` | string | PHASE_2_MOVE_TO_PREPARE | Any valid phase name | `phase1_monitor_node.start_phase` | phase1_monitor_node | No | Phase to start after Phase1 complete |
| `handle_class_keywords` | string | "wooden cleaver handle,handle,cleaver handle" | Comma-separated | `xcore_monitor_handle_sequence_node` | monitor node | No | SAM3 keywords for knife handle detection |
| `y_before_handle_m` | float | 0.15 | >0.0 | `xcore_monitor_handle_sequence_node._y_before` | monitor node | No | Y offset before handle center for approach waypoint |
| `z_before_handle_m` | float | 0.05 | >0.0 | `xcore_monitor_handle_sequence_node._z_before` | monitor node | No | Z offset before handle center for approach waypoint |
| `y_step_after_z_m` | float | 0.13 | >0.0 | `xcore_monitor_handle_sequence_node._y_step` | monitor node | No | Y step after Z descent in approach sequence |
| `post_grasp_tcp_plus_y_m` | float | 0.35 | ≥0.0 | `xcore_monitor_handle_sequence_node._post_grasp_tcp_plus_y_m` | monitor node | No | TCP retract distance after O6 grasp (left=+Y, right=-Y) |
| `post_grasp_joint_home_rad_csv` | string | 7 comma-separated floats | 7 valid radians | `xcore_monitor_handle_sequence_node._post_grasp_joint_home_rad_csv` | monitor node | No | Joint positions after grasp retract (MoveAbsJ) |
| `hand_o6_close_degrees_csv` | string | "0,0,80,0,0,0" | 6 values 0-100 | `xcore_monitor_handle_sequence_node._hand_o6_close_csv` | follow node | No | O6 gripper close angles |
| `arm_type` | string | "right" | "left" or "right" | `xcore_monitor_handle_sequence_node._arm_type` | monitor + follow nodes | No | Determines Y approach direction and TCP retract axis |
| `vel_scale` | float | 0.10 | 0.05-1.0 | `xcore_follow_tcp_chain_node_movej._vel_scale` | follow node | No | Joint speed scaling |
| `accel_scale` | float | 0.10 | 0.05-1.0 | `xcore_follow_tcp_chain_node_movej._accel_scale` | follow node | No | Joint acceleration scaling |
| `min_move_interval_sec` | float | 1.5 | ≥0.2 | `xcore_follow_tcp_chain_node_movej._min_interval` | follow node | No | Minimum time between consecutive moves |
| `follow_batch_sequence_enable` | bool | true | true/false | `xcore_monitor_handle_sequence_node._follow_batch_sequence_enable` | monitor node | No | Whether to send approach waypoints as batch JSON |
| `post_sequence_o6_grasp_enable` | bool | true | true/false | `xcore_monitor_handle_sequence_node._post_sequence_o6_grasp_enable` | monitor node | No | Whether to execute O6 grasp after approach sequence |
| `post_grasp_joint_home_enable` | bool | true | true/false | `xcore_monitor_handle_sequence_node._post_grasp_joint_home_enable` | monitor node | No | Whether to MoveAbsJ to home after grasp retract |
| `handle_sequence_single_shot_enable` | bool | true | true/false | `xcore_monitor_handle_sequence_node._single_shot_enabled` | monitor node | No | Whether to stop responding to handle after first grab |
| `calibration_file` | string | /home/a/.../config1/calibration_result.yaml | Valid path | `xcore_monitor_handle_sequence_node._T_base_cam` | monitor node | No | Hand-eye calibration file (T_base_cam) |

## Notes

- All classmate's parameters are ROS2 node parameters, not YAML config files
- Parameters are passed via `--ros-args -p name:=value` in launch files
- No restart required for parameter changes (nodes read at startup only)
- User's workspace calibration file path differs from classmate's: `/home/tbl/Project/dexbot_ros2_ws/src/config/calibration_result.yaml` vs `/home/a/Desktop/dexbot_ros2_ws/src/config1/calibration_result.yaml`

## Phase4/Phase6 Return-to-Prepare Parameters

| Parameter | Type | Default | Valid Range | Runtime Mapping | Used By | Requires Restart | Notes |
|---|---|---|---|---|---|---|---|
| `cutting.phase4_return_to_prepare.return_extra_offset_m` | float | 0.04 | ≥0.0 | `knife_cut_action_server._return_to_prepare_waypoints()` | knife_cut_action_server | No | Extra Z+ offset on return-to-prepare to avoid blade scraping tofu |
| `cutting.phase6_return_to_prepare.return_extra_offset_m` | float | 0.04 | ≥0.0 | `knife_cut_action_server._return_to_prepare_waypoints()` | knife_cut_action_server | No | Same as Phase4, for Phase6 return |

## Phase2/Phase6 Staged Prepare Parameters

| Parameter | Type | Default | Valid Range | Runtime Mapping | Used By | Requires Restart | Notes |
|---|---|---|---|---|---|---|---|
| `cutting.phase2_prepare.staged_motion_enable` | bool | true | true/false | `knife_prepare_action_server` staged execute path | knife_prepare_action_server | No | Enable two-stage queued joint motion for Phase2 prepare |
| `cutting.phase2_prepare.staged_via_progress` | float | 0.70 | 0.5-0.95 | `knife_prepare_action_server` via-point interpolation ratio | knife_prepare_action_server | No | Via-point position ratio from current pose toward final pose |
| `cutting.phase2_prepare.staged_orientation_slerp` | float | 0.70 | 0.5-0.95 | `knife_prepare_action_server` via-point orientation ratio | knife_prepare_action_server | No | Orientation interpolation ratio for via pose |
| `cutting.phase2_prepare.staged_zone_mm` | int | 10 | 0-100 | `lbot_robot_xcore.set_default_zone()` or MoveAbsJ queue zone | knife_prepare_action_server | No | Blend/transition zone for queued joint sequence |
| `cutting.phase6_prepare.staged_motion_enable` | bool | true | true/false | `knife_prepare_action_server` staged execute path | knife_prepare_action_server | No | Same staged prepare behavior on Phase6 re-entry |
| `cutting.phase6_prepare.staged_via_progress` | float | 0.70 | 0.5-0.95 | `knife_prepare_action_server` via-point interpolation ratio | knife_prepare_action_server | No | Same as Phase2 |
| `cutting.phase6_prepare.staged_orientation_slerp` | float | 0.70 | 0.5-0.95 | `knife_prepare_action_server` via-point orientation ratio | knife_prepare_action_server | No | Same as Phase2 |
| `cutting.phase6_prepare.staged_zone_mm` | int | 10 | 0-100 | `lbot_robot_xcore.set_default_zone()` or MoveAbsJ queue zone | knife_prepare_action_server | No | Same as Phase2 |
