# Config Schema

| Parameter | Type | Default | Valid Range | Runtime Mapping | Used By | Requires Restart | Notes |
|---|---|---|---|---|---|---|---|
| side | str | "right" | "left", "right" | `ArmHandPage._side_var` | GUI, ServiceRegistry | No | Left/right arm selection |
| hand_model | str | "o6" | "o6", "l25", "l20lite" | `ArmHandPage._hand_model_var` | HandControlService | No | Hand model determines DOF |
| can_iface | str | "can0" | any valid CAN iface | `ArmHandPage._hand_iface_var` | HandControlService | No | CAN interface name |
| arm_ip_right | str | "192.168.2.161" | valid IPv4 | `ArmHandPage._robot_ip_var`, web DB | RosServiceBridge (indirect) | No | Right arm IP |
| arm_ip_left | str | "192.168.2.160" | valid IPv4 | web DB | RosServiceBridge (indirect) | No | Left arm IP |
| robot_class | str | "xMateErProRobot" | "xMateErProRobot", "xMateRobot", "xMateCr5Robot" | `ArmHandPage._robot_class_var` | xCore SDK | No | Robot class for Drag |
| jog_step_mm | float | 2.0 | > 0.1 | `ArmHandPage._step_mm_var` | world_jog | No | World jog step size |
| jog_speed_scale | float | 0.35 | 0.05 - 3.0 | `ArmHandPage._speed_scale_var` | world_jog | No | World jog speed |
| jog_max_lin_v | float | 0.06 | >= 0.0 | `ArmHandPage._max_linear_velocity_var` | world_jog | No | Max linear velocity (m/s) |
| jog_max_ang_v | float | 0.30 | >= 0.0 | `ArmHandPage._max_angular_velocity_var` | world_jog | No | Max angular velocity (rad/s) |
| jog_use_impedance | bool | False | True/False | `ArmHandPage._use_impedance_var` | world_jog | No | Impedance mode toggle |
| hand_timeout_ms | float | 1500.0 | > 1.0 | `ArmHandPage._timeout_ms_var` | readback_angles | No | Readback timeout |
| hand_settle_ms | float | 120.0 | >= 0.0 | `ArmHandPage._settle_ms_var` | apply_angles | No | Settle time after apply |
| hand_torque_limit | float | 5.0 | 0-100 | `ArmHandPage._torque_limit_var` | apply_angles | No | Torque limit |
| hand_send_torque_first | bool | True | True/False | `ArmHandPage._send_torque_before_apply_var` | apply_angles | No | Send torque before apply |
| servo_speed | float | 0.55 | 0.05 - 3.0 | `ArmHandPage._servo_speed_var` | servo_move_segment | No | Servo speed scale |
| servo_max_lin_v | float | 0.10 | >= 0.0 | `ArmHandPage._servo_max_lin_v_var` | servo_move_segment | No | Max linear velocity |
| servo_max_ang_v | float | 0.45 | >= 0.0 | `ArmHandPage._servo_max_ang_v_var` | servo_move_segment | No | Max angular velocity |
| servo_max_accel | float | 0.22 | >= 0.0 | `ArmHandPage._servo_max_accel_var` | servo_move_path | No | Max acceleration |
| servo_use_impedance | bool | False | True/False | `ArmHandPage._servo_use_imp_var` | servo_move_segment | No | Servo impedance toggle |
| rtfollow_hz | float | 200.0 | 1.0 - 500.0 | `ArmHandPage._rtfollow_hz_var` | rt_follow_start | No | RT follow frequency |
| rtfollow_seg_s | float | 0.6 | 0.05 - 5.0 | `ArmHandPage._rtfollow_seg_s_var` | rt_follow_start | No | Segment duration |
| rtfollow_state_ms | float | 200.0 | 10.0 - 2000.0 | `ArmHandPage._rtfollow_state_ms_var` | rt_follow_start | No | State update interval |
| web_session_max_age | int | 604800 | > 0 | `auth.COOKIE_MAX_AGE` | web auth | Yes | 7 days in seconds |
