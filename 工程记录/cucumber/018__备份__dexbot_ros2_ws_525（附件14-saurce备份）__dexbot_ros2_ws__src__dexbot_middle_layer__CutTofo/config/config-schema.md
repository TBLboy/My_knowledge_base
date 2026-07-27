# Config Schema

## arms.yaml

| Parameter | Type | Default | Valid Range | Runtime Mapping | Used By | Notes |
|-----------|------|---------|-------------|-----------------|---------|-------|
| `arms.left.robot_ip` | string | 192.168.2.160 | IP addr | xCore SDK connect | All left-arm skills | — |
| `arms.right.robot_ip` | string | 192.168.2.161 | IP addr | xCore SDK connect | All right-arm skills | — |
| `arms.left.urdf_path` | string | — | file path | OfflineURDFKinematics | Left-arm IK | AR5-5_07L |
| `arms.right.urdf_path` | string | — | file path | OfflineURDFKinematics | Right-arm IK | AR5-5_07R |
| `arms.left.tcp_offset` | float[6] | [0,0,0,0,0,0] | — | TCP transform | Left-arm motion | Zero (no tool) |
| `arms.right.tcp_offset` | float[6] | [0.01089, 0.12506, 0.25620, 0,0,0] | — | TCP transform | Right-arm motion | Knife TCP |
| `arms.left.home_joints` | float[7] | — | rad | MoveJ home | All left-arm skills | — |
| `arms.right.home_joints` | float[7] | — | rad | MoveJ home | All right-arm skills | — |

## tofu_prepare_params.yaml

| Parameter | Type | Default | Profiles | Notes |
|-----------|------|---------|----------|-------|
| `profiles.first_cut.plane_angle_deg` | float | 135.0 | first_cut | 斜切平面角 |
| `profiles.after_rotation_1.plane_angle_deg` | float | 90.0 | after_rotation_1 | 竖切平面角 |
| `profiles.cucumber.plane_angle_deg` | float | 90.0 | cucumber | 黄瓜切割平面 |

## tofu_cut_round_params.yaml

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `profiles.round_1.cycles` | int | 8 | 切割周期数 |
| `profiles.round_1.step_z_m` | float | -0.0155 | 每周期 Z 步进 |
| `profiles.round_1.stiffness` | int | 3000 | 阻抗刚度 |
| `profiles.round_1.return_to_prepare` | bool | true | 是否回预备位姿 |
| `profiles.round_1.pause_at_wait_pose` | bool | true | 切割完在等待位姿暂停 |

## tofu_vertical_cut_params.yaml

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `profiles.default.cycles` | int | 11 | 切割周期数 |
| `profiles.default.step_z_m` | float | -0.006 | 每周期 Z 步进 |
| `profiles.default.cut_direction` | string | base_y | 切割方向 |

## handle_approach_params.yaml

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `robot_ip` | string | 192.168.2.161 | 右臂 IP |

## cucumber_hold_params.yaml

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `robot_ip` | string | 192.168.2.160 | 左臂 IP |
| `profiles.default.motion_mode` | string | NRT | 运动模式 |
| `profiles.default.tool_offset_xyz` | float[3] | [0,0,0] | 左臂 TCP 偏移 |
