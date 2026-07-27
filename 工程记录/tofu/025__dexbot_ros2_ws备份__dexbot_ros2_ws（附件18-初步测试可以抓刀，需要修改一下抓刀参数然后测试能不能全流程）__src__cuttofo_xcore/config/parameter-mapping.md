# Config Schema

## Phase1 Migration Parameters

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
