# Config Schema

## Skill 参数（每个 skill 自己的 params.yaml）

| Parameter | Type | Default | Valid Range | Runtime Mapping | Used By | Requires Restart | Notes |
|---|---|---|---|---|---|---|---|
| plane_angle_deg | float | 135 | 0-180 | prepare IK 平面角度 | tofu_prepare | Y | first_cut=135, after_rotation_1=90, cucumber=90 |
| offset_a | float | per-profile | — | prepare 偏移量 | tofu_prepare | Y | 在 tofu_prepare_params.yaml 中 |
| vertical_offset | float | per-profile | — | prepare 垂直偏移 | tofu_prepare | Y | — |
| cycles | int | 8(豆腐)/10(黄瓜) | >= 1 | cut_round 切割周期数 | tofu_cut_round | Y | — |
| step_z | float | 0.003 | > 0 | 每 cycle Z 向步进 | tofu_cut_round | Y | — |
| stiffness.trans | float | 未知 | — | 阻抗控制平动刚度 | tofu_cut_round | Y | — |
| stiffness.rot | float | 未知 | — | 阻抗控制转动刚度 | tofu_cut_round | Y | — |
| speed.trans | float | 未知 | — | 最大平动速度 | tofu_cut_round | Y | — |
| speed.rot | float | 未知 | — | 最大转动速度 | tofu_cut_round | Y | — |

## 手臂参数（arms.yaml）

| Parameter | Type | Default | Valid Range | Runtime Mapping | Used By | Requires Restart | Notes |
|---|---|---|---|---|---|---|---|
| active_arm | string | right | left/right | 当前活跃臂 | skill_common | Y | — |
| arm_r.tcp_offset | float[3] | [0.01089, 0.12506, 0.25620] | — | 右臂 TCP 平移偏移 | skill_common | Y | — |
| arm_l.tcp_offset | float[3] | [0, 0, 0] | — | 左臂 TCP 平移偏移 | skill_common | Y | — |
| arm_r.home | float[7] | [0, -30, 0, 60, 0, 45, 0] | — | 右臂 home 关节角度（度） | skill_common | Y | — |
| arm_l.home | float[7] | [0, 30, 0, -60, 0, -45, 0] | — | 左臂 home 关节角度（度） | skill_common | Y | — |

## 工作流参数（tofu_workflow_params.yaml）

| Parameter | Type | Default | Notes |
|---|---|---|---|
| steps | array[dict] | — | 步骤列表，每个 step 包含 skill、profile、wait_before 等 |
| settle_before_sec | float | 0 | 发送 goal 前的等待时间 |
| wait_before | bool | false | 是否在步骤前等待 operator |
| class_filter | string | null | 视觉 class filter（通过 tofu_state_node） |

## 视觉参数（vision_params.yaml）

| Parameter | Type | Default | Notes |
|---|---|---|---|
| sam3_model_path | string | — | SAM3 模型权重路径 |
| detection_threshold | float | — | 检测阈值 |
| depth_sync | bool | — | 深度图像同步开关 |
| smoothing | dict | — | 位姿平滑参数 |
| filtering | dict | — | 滤波参数 |
