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
