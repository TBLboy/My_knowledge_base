# Business Logic Edges

## Edge Template

```yaml
edge_id: <edge-id>
from: <start-node-id>
to: <target-node-id>
path: main | branch | archived
status: draft | stable | testing | validated | archived
method: <method summary>
execution_chain:
  - <step 1>
  - <step 2>
  - <step 3>
inputs:
  - <input>
outputs:
  - <output>
parameters:
  - name: <parameter-name>
    type: <data-type>
    default: <default-value>
    source: <config/code/user/hardware>
interfaces:
  - <topic/service/API/SDK/protocol>
error_handling:
  - <failure condition and response>
verification:
  - <verification method>
notes:
  - <notes>
```

## Edges

### A -> B: handle_approach

```yaml
edge_id: A-B
from: A
to: B
path: main
status: stable
method: 视觉锁定刀柄 → 5 步笛卡尔逼近 → O6 夹爪闭合 → 抽出 → 回 home
execution_chain:
  - vision: 发送 text_prompt "wooden cleaver handle" 到 SAM3
  - lock: 锁定刀柄位姿
  - approach: 执行 5 步笛卡尔空间逼近序列
  - grasp: O6 夹爪闭合（0,70,0,0,0,0 度）
  - retract: 沿 TCP +Y 方向抽出
  - home: 回到 joint home
inputs:
  - 视觉检测刀柄位姿
outputs:
  - 刀已持握
parameters:
  - name: profile
    type: string
    default: default
    source: workflow YAML
  - name: 5-step approach distances
    type: array[float]
    source: handle_approach_params.yaml
  - name: O6 close degrees
    type: float
    source: handle_approach_params.yaml
interfaces:
  - /handle_approach/execute (Action)
  - /cuttofu/vision/text_prompt (topic)
  - /cuttofu/perception/objects_with_pose (topic)
  - xCore SDK: move_rt_cartesian_path
error_handling:
  - 视觉锁定失败：Action abort
  - 逼近超时或碰撞：Action abort
verification:
  - Action 返回 success
```

### B -> C: prepare first_cut

```yaml
edge_id: B-C
from: B
to: C
path: main
status: stable
method: 视觉检测 → IK 求解 → 离线预览 → joint move 到预备位姿
execution_chain:
  - vision: 发送 text_prompt 检测豆腐位姿
  - solve_ik: 根据 profile "first_cut" 参数求解 IK
  - preview: 离线验证无碰撞
  - move: joint move 到目标位姿
inputs:
  - 豆腐视觉位姿
  - profile: first_cut（plane_angle_deg=135 等）
outputs:
  - 右臂在 first_cut 预备位姿
parameters:
  - name: plane_angle_deg
    type: float
    default: 135
    source: tofu_prepare_params.yaml
  - name: offset_a
    type: float
    source: tofu_prepare_params.yaml
  - name: vertical_offset
    type: float
    source: tofu_prepare_params.yaml
interfaces:
  - /tofu_prepare/execute (Action)
  - /cuttofu/perception/objects_with_pose (topic)
  - xCore SDK: move_joint
error_handling:
  - IK 失败：abort，提示 operator 调整
  - 检测到多个目标：class_filter 过滤
verification:
  - Action 返回 success
```

### C -> D: cut_round round_1

```yaml
edge_id: C-D
from: C
to: D
path: main
status: stable
method: N 次阻抗控制水平切割循环 → 回 wait 位姿
execution_chain:
  - for cycle in 1..N:
    - 沿 flange Z 方向阻抗切割
    - 按 step_z 步进
  - 回到 prepare 位姿（或 wait 位姿）
inputs:
  - 预备位姿
  - profile: round_1（cycles=8, step_z=0.003, stiffness 等）
outputs:
  - 切割完成
parameters:
  - name: cycles
    type: int
    default: 8
    source: tofu_cut_round_params.yaml
  - name: step_z
    type: float
    default: 0.003
    source: tofu_cut_round_params.yaml
  - name: stiffness
    type: dict
    source: tofu_cut_round_params.yaml
  - name: speed
    type: dict
    source: tofu_cut_round_params.yaml
interfaces:
  - /tofu_cut_round/execute (Action)
  - xCore SDK: move_rt_cartesian_path（阻抗模式）
error_handling:
  - 每 cycle 超时：abort
  - 阻抗异常：abort
verification:
  - Action 返回 success
  - feedback 确认到达 N cycles
```

### D -> U: second_cross_cut hook_lift

```yaml
edge_id: D-U
from: D
to: U
path: branch
status: draft
method: 第二次横切完成后，右臂不沿原 45 度回撤，而是以刀刃中心为工作 TCP 执行抬刀/挑条动作，把豆腐条从切缝中带出；默认采用 translate_only，增强模式为 translate_plus_tilt；达到 clearance 后本轮动作直接衔接进入 transfer_to_container，而不是在 hook_lift 结束后额外发起独立控制请求
execution_chain:
  - diagonal_cut: 完成第二次 45 度斜切并交汇
  - hook_lift: 默认按单段抬升/挑条方式脱离主体
  - if translate_plus_tilt: 通过短 RT waypoint 复合段同步完成上抬与姿态变平
  - handoff_to_transfer: 将 hook_lift 终点作为本轮 transfer_to_container 的起点继续拼接 RT 轨迹
inputs:
  - 第二次横切交汇切口
  - second_cross_cut profile
outputs:
  - 豆腐条被带离切缝
  - 达到 clearance 后可直接衔接本轮 transfer 阶段
parameters:
  - name: hook_motion_mode
    type: enum[translate_only, translate_plus_tilt]
    default: translate_only
    source: tofu_second_cross_cut_params.yaml
  - name: hook_pitch_delta_deg
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: hook_lift_clearance_m
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: lift_dz_m
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: hook_dx_m
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: hook_dy_m
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: hook_waypoint_count
    type: int
    default: 2
    source: tofu_second_cross_cut_params.yaml
  - name: hook_motion_segments
    type: int
    default: 1
    source: tofu_second_cross_cut_params.yaml
interfaces:
  - /tofu_second_cross_cut/execute (Action)
  - xCore SDK: move_rt_cartesian_path
error_handling:
  - 抬刀时碰板或回插：abort
  - 复合段姿态变化过大导致轨迹异常：abort
verification:
  - 日志确认进入 hook_lift stage
  - 刀未按原 45 度原路退回
  - 达到 hook_lift_clearance_m 后直接衔接 transfer_to_container
```

### U -> V: second_cross_cut transfer_to_drop_zone

```yaml
edge_id: U-V
from: U
to: V
path: branch
status: draft
method: 每次 hook_lift 完成后，右臂将该轮挂条立即转运到桌面容器中心上方；容器检测与提示词切换直接封装在 `second_cross_cut` skill 包内部：该 skill 在第二次横切开始时覆盖提示词为容器，结束时统一切回豆腐提示词；容器位置可持续更新，但每一轮只在生成该轮转运轨迹前读取一次目标，优先使用 latest，若 latest 不可用则回退 skill 内 cached；转运过程采用 RT 笛卡尔平移，保持 TCP 姿态不变，本质上将右臂刀刃中心 TCP 原点移动到容器中心 + offset 后的目标点
execution_chain:
  - keep_tracking_container: 新分支执行期间持续订阅最新容器检测结果
  - read_latest_or_cached_once: 生成本轮 transfer 段前读取一次 latest/cached 容器中心
  - apply_container_offset: 对本轮容器中心施加右臂转运阶段 offset 微调
  - build_tcp_target: 以 hook_lift 结束时的 TCP 姿态为固定姿态，构造容器目标 TCP 原点
  - convert_to_flange_waypoints: 通过 tcp_offset 反算 RT 笛卡尔轨迹中的法兰 waypoint
  - move_to_container_center: 平移到容器中心上方
  - hold_above_container: 在容器上方静止等待左臂
inputs:
  - U 节点输出
  - 现有 vision 节点输出的 latest/cached 容器检测结果
outputs:
  - 右臂停在容器上方安全位
  - 右臂目标 TCP 可作为左臂目标转换基准
parameters:
  - name: container_detection_prompt
    type: string
    source: vision prompt config
  - name: container_center_topic_or_cache
    type: string
    source: existing vision node
  - name: container_tcp_offset
    type: vector3
    source: tofu_second_cross_cut_params.yaml
  - name: container_min_confidence
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: prompt_settle_sec
    type: float
    source: tofu_second_cross_cut_params.yaml
interfaces:
  - /tofu_second_cross_cut/execute (Action)
  - /cuttofu/vision/text_prompt
  - /cuttofu/perception/objects_with_pose
  - xCore SDK: move_rt_cartesian_path
error_handling:
  - 当前无 latest 且 cached 不存在：abort 或 fallback 到旧 round_2
  - RT 转运段轨迹不可达或异常：abort
verification:
  - 日志确认进入 transfer_to_drop_zone stage
  - 右臂稳定保持在容器上方
  - 本轮 transfer 仅在入段前读取一次容器目标，运动中不重规划
```
    source: tofu_second_cross_cut_params.yaml
  - name: transfer_keep_orientation
    type: bool
    default: true
    source: tofu_second_cross_cut_params.yaml
  - name: transfer_motion_mode
    type: enum[rt_cartesian_translate]
    default: rt_cartesian_translate
    source: tofu_second_cross_cut_params.yaml
  - name: transfer_motion_segments
    type: int
    default: 1
    source: tofu_second_cross_cut_params.yaml
interfaces:
  - /tofu_second_cross_cut/execute (Action)
  - existing vision node output
  - /cuttofu/vision/text_prompt (topic or equivalent prompt switch interface)
  - xCore SDK: move_rt_cartesian_path
error_handling:
  - 容器中心未检测到：fallback 到现有老版本第二次横切逻辑
  - 提示词切换成功但 vision 输出未更新：fallback 到现有老版本第二次横切逻辑
  - 运条时掉条或撞击：abort 或进入安全停靠位
verification:
  - 日志确认第一次横切 continue 后才触发容器检测
  - 日志确认检测失败时回退到老版本 round_2
  - 日志确认新分支期间持续使用最新容器检测结果
  - 转运过程中右臂姿态保持不变
  - 右臂在容器上方静止后才进入左臂拨落阶段
```

### V -> W: second_cross_cut left_scrape_drop

```yaml
edge_id: V-W
from: V
to: W
path: branch
status: draft
method: 左臂 + O6 在容器上方靠近右手刀刃，把条状残料拨落；左臂目标在右臂静止后由右臂目标 TCP 经过双臂坐标转换得到，第一版仅由左臂执行拨落轨迹。左臂法兰姿态选择复用 sauce_pour 的候选姿态 + IK 预检机制
execution_chain:
  - wait_right_static: 确认右臂在容器上方静止
  - transform_target: 将右臂目标 TCP 转换到左臂 base 坐标系
  - load_flange_candidates: 读取通过人工拖动采集得到的左臂法兰姿态候选库
  - select_flange_candidate: 对左臂法兰姿态候选逐个做 IK 预检
  - choose_nearest_valid: 若多个候选可达，选择记录法兰位置与当前目标法兰位置距离最近者
  - left_approach: 左臂按默认单段方式进入预拨落位
  - o6_pose: 默认使用 O6 手型，不把手型绑定在候选姿态里
  - scrape_drop: 左臂沿拨落轨迹运动，把豆腐条从刀上拨下
  - retreat: 左臂退回安全位
inputs:
  - 右臂容器上方安全位
  - 左臂预拨落位
outputs:
  - 豆腐条已拨落
parameters:
  - name: left_target_offset
    type: vector3
    source: tofu_second_cross_cut_params.yaml
  - name: left_flange_pose_candidates_file
    type: path
    source: tofu_second_cross_cut_params.yaml
  - name: left_scrape_path_mode
    type: enum[left_only_scrape]
    default: left_only_scrape
    source: tofu_second_cross_cut_params.yaml
  - name: o6_pose_scrape
    type: string
    source: tofu_second_cross_cut_params.yaml
  - name: left_speed
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: scrape_motion_segments
    type: int
    default: 1
    source: tofu_second_cross_cut_params.yaml
interfaces:
  - /tofu_second_cross_cut/execute (Action)
  - dual_arm_transform.right_base_point_to_left
  - sauce_pour flange_pose_candidates capture pattern
  - sauce_pour flange_pose_candidates selection pattern
  - xCore SDK: move_rt_cartesian_path
  - xCore SDK: set_o6_pose
error_handling:
  - 左臂逼近右臂工具过近：abort
  - 所有左臂法兰姿态候选均不可达：abort
verification:
  - 日志确认进入 left_scrape_drop stage
  - 候选姿态经过 IK 预检后再执行
  - 拨落期间右臂保持静止
  - 左臂完成拨落并退开
```

### W -> X: second_cross_cut return_to_next_cut_anchor

```yaml
edge_id: W-X
from: W
to: X
path: branch
status: draft
method: 拨落完成后，左臂回准备位与右臂回下一刀起点同步进行，作为同一收尾阶段完成；右臂目标不取本次挑条脱离点，而是严格复用现有第二次横切 cycle 中“回刀后再按既有步进规则平移一次”得到的 next anchor；默认一步到位回位，但保留多段回位扩展空间
execution_chain:
  - start_parallel_retreat: 拨落完成后同步启动左右臂回位
  - left_return_prepare: 左臂回准备位
  - resolve_next_anchor: 按现有第二次横切回刀 + step 逻辑求出下一刀起始位姿
  - right_return_anchor: 右臂回到下一刀 anchor
  - join_dual_arm_return: 等待左右臂都完成回位
inputs:
  - 左臂拨落完成
  - 现有第二次横切 cycle 的 next anchor 定义
outputs:
  - 左臂回到准备位
  - 右臂回到下一次第二次横切起点
parameters:
  - name: safe_return_height_m
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: next_anchor_offset_x
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: next_anchor_offset_y
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: next_anchor_offset_z
    type: float
    source: tofu_second_cross_cut_params.yaml
  - name: return_motion_segments
    type: int
    default: 1
    source: tofu_second_cross_cut_params.yaml
interfaces:
  - /tofu_second_cross_cut/execute (Action)
  - current round_2 next-anchor logic
  - xCore SDK: move_cartesian / move_position_only
error_handling:
  - next anchor 求解结果与现有步进逻辑不一致：abort
  - 任一手臂回位失败：abort
verification:
  - 日志确认进入 return_to_next_cut_anchor stage
  - 左右臂回位阶段同步启动并完成
  - 返回目标与现有第二次横切回刀后步进一步的结果一致
  - 第二次横切整轮结束后切回豆腐检测并恢复 / override Phase6 视觉参数
  - 下一 cycle 可继续执行
```

### D -> F: prepare first_cut（第二次）

```yaml
edge_id: D-F
from: D
to: F
path: main
status: stable
method: 同 B->C，operator 旋转后重新对刀
execution_chain:
  - 同 B->C
notes:
  - operator 介入发生在 D 和 F 之间，通过 operator_wait 机制
  - 实际状态转移 D -> E -> F
```

### F -> G: cut_round round_2

```yaml
edge_id: F-G
from: F
to: G
path: main
status: stable
method: 同 C->D，profile=round_2
parameters:
  - profile: round_2（cycles=8, 参数可能不同于 round_1）
```

### G -> I: prepare after_rotation_1

```yaml
edge_id: G-I
from: G
to: I
path: main
status: stable
method: 同 prepare，profile=after_rotation_1（plane_angle_deg=90 垂直）
parameters:
  - name: plane_angle_deg
    type: float
    default: 90
    source: tofu_prepare_params.yaml
notes:
  - operator 介入发生在 G 和 I 之间
  - 实际状态转移 G -> H -> I
```

### I -> J: vertical_cut

```yaml
edge_id: I-J
from: I
to: J
path: main
status: stable
method: 垂直切割（mid-cycle + tail push），位置控制
execution_chain:
  - 执行垂直切割
  - mid-cycle 切割段
  - tail push 段
inputs:
  - 垂直切割预备位姿
  - profile: default
interfaces:
  - /tofu_vertical_cut/execute (Action)
  - xCore SDK: move_rt_cartesian_path（位置模式）
error_handling:
  - 位置超限：abort
verification:
  - Action 返回 success
```

### A -> O: cucumber_hold

```yaml
edge_id: A-O
from: A
to: O
path: main
status: stable
method: 左臂视觉锁定黄瓜 → 阻抗控制握持
execution_chain:
  - 视觉检测黄瓜位姿
  - 左臂移到握持位姿
  - 阻抗控制保持握持
interfaces:
  - /cucumber_hold/execute (Action)
  - /cuttofu/perception/objects_with_pose
```

### O -> P -> Q -> R: 黄瓜切割链

```yaml
edge_id: O-R
from: O
to: R
path: main
status: stable
method: prepare:cucumber → cut_round:cucumber(10 cycles) → release
notes:
  - 黄瓜流程中 cut_round 使用 10 cycles（比豆腐多）
  - release 调用 cucumber_hold 的 release profile
```

### A -> S -> T: 抓料倒酱链

```yaml
edge_id: A-T
from: A
to: T
path: main
status: stable
method: pick_place:default → sauce_pour:default
notes:
  - sauce_pour 支持 replay_only 和 use_vision 模式
  - 从 flange_pose_candidates.yaml 选择最优抓取位姿
```
