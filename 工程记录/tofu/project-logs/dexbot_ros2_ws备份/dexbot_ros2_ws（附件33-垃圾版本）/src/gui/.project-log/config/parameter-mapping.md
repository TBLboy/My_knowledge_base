# Parameter Mapping

## World Jog Parameters

| GUI Variable | Service Config Field | Type | Default | Notes |
|---|---|---|---|---|
| `_step_mm_var` | `WorldJogConfig.step_mm` | float | 2.0 | Converted to meters in service |
| `_speed_scale_var` | `WorldJogConfig.speed_scale` | float | 0.35 | Clamped 0.05-3.0 |
| `_max_linear_velocity_var` | `WorldJogConfig.max_linear_velocity` | float | 0.06 | m/s |
| `_max_angular_velocity_var` | `WorldJogConfig.max_angular_velocity` | float | 0.30 | rad/s |
| `_use_impedance_var` | `WorldJogConfig.use_impedance` | bool | False | Enables stiffness array |

## Servo Mode Parameters

| GUI Variable | Service Config Field | Type | Default | Notes |
|---|---|---|---|---|
| `_servo_speed_var` | `ServoConfig.speed_scale` | float | 0.55 | Clamped 0.05-3.0 |
| `_servo_max_lin_v_var` | `ServoConfig.max_linear_velocity` | float | 0.10 | m/s |
| `_servo_max_ang_v_var` | `ServoConfig.max_angular_velocity` | float | 0.45 | rad/s |
| `_servo_max_accel_var` | `ServoConfig.max_acceleration` | float | 0.22 | m/s² |
| `_servo_use_imp_var` | `ServoConfig.use_impedance` | bool | False | Stiffness: [3000,3000,1500,200,200,200] |

## Comfort Parameters

| GUI Variable | Service Config Field | Type | Default | Notes |
|---|---|---|---|---|
| `_comfort_margin_vars[0-6]` | `ComfortParams.margins_deg` | list[float] | [10.0]*7 | Per-joint safety margin |
| `_comfort_max_iter_var` | `ComfortParams.max_iterations` | int | 100 | Max optimization iterations |
| `_comfort_lr_var` | `ComfortParams.learning_rate` | float | 0.1 | Gradient descent step |
| `_comfort_wlimit_var` | `ComfortParams.weight_limit` | float | 100.0 | Weight for joint limits |
| `_comfort_wmid_var` | `ComfortParams.weight_mid` | float | 0.1 | Weight for mid-range |
| `_comfort_wsmooth_var` | `ComfortParams.weight_smooth` | float | 0.05 | Weight for smoothness |
| `_comfort_tol_m_var` | `ComfortParams.pose_tolerance_m` | float | 0.0001 | Position tolerance |
| `_comfort_tol_rad_var` | `ComfortParams.pose_tolerance_rad` | float | 0.001 | Orientation tolerance |
| `_comfort_speed_var` | `ComfortParams.speed` | float | 100.0 | Speed percentage (0-100) |
| `_comfort_zone_var` | `ComfortParams.zone_mm` | float | 10.0 | Comfort zone size |

## Hand Parameters

| GUI Variable | Service Config Field | Type | Default | Notes |
|---|---|---|---|---|
| `_timeout_ms_var` | `HandConfig.timeout_ms` | float | 1500.0 | Readback blocking timeout |
| `_settle_ms_var` | `HandConfig.settle_ms` | float | 120.0 | Sleep after apply |
| `_torque_limit_var` | `HandConfig.torque_limit` | float | 5.0 | Torque preset value |
| `_send_torque_before_apply_var` | `HandConfig.send_torque_before_apply` | bool | True | Send torque before angles |
| `_nudge_step_var` | UI only | float | 1.0 | Slider nudge step |

## RT Follow Parameters

| GUI Variable | Service Method Argument | Type | Default | Notes |
|---|---|---|---|---|
| `_arm_seq_var` | `seq` | str | "" | Preset sequence |
| `_rtfollow_hz_var` | `hz` | float | 200.0 | Frequency (1-500) |
| `_rtfollow_seg_s_var` | `segment_s` | float | 0.6 | Segment duration (0.05-5.0) |
| `_rtfollow_state_ms_var` | `state_ms` | float | 200.0 | State interval (10-2000) |
| `_arm_speed_var` | `speed` | float | 0.4 | Speed (0-1, normalized from %) |
