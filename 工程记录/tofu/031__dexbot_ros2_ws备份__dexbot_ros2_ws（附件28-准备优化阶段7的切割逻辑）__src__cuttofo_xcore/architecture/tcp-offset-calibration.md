
---

## 13. TCP Offset 标定与补偿

### 13.1 概念定义

```
TCP offset = 法兰坐标系下，从法兰原点到刀刃中心的平移向量 [dx, dy, dz]

                法兰(link7)
                  │
                  │  tcp_offset = [dx, dy, dz]
                  │  (法兰坐标系下的固定向量)
                  ▼
            刀刃中心 (刀具TCP)
```

**关键性质**:
- 纯平移，无旋转：刀具 TCP 坐标系的 X/Y/Z 轴方向 = 法兰坐标系的 X/Y/Z 轴方向
- 在法兰坐标系中表达：不随机械臂姿态变化而变化
- 在 base 坐标系中的实际偏移 = `R_flange @ tcp_offset`（随法兰姿态旋转）

### 13.2 数学关系

```
已知:
  tcp_offset = [dx, dy, dz]        (法兰坐标系下，标定得到)
  R_flange                          (法兰在 base 系下的旋转矩阵)

正向 (FK → TCP 位姿):
  tcp_pos = flange_pos + R_flange @ tcp_offset
  tcp_eul = flange_eul              (姿态不变)

逆向 (TCP 目标 → 法兰目标，用于 IK):
  flange_target_pos = tcp_target_pos - R_target @ tcp_offset
  flange_target_eul = tcp_target_eul    (姿态不变)
```

### 13.3 在控制流程中的位置

```
视觉管线输出:
  tcp_target_pos = 刀刃中心应到达的位置 (base 坐标系)
  target_R = 法兰/TCP 的目标姿态 (由几何约束构建)

         ┌─────────────────────────────────────────────┐
         │  TCP→法兰位置补偿 (adapter 层统一处理)        │
         │                                              │
         │  flange_target = tcp_target - target_R @ tcp_offset │
         │                                              │
         │  tcp_offset = [0,0,0] 时: flange_target = tcp_target │
         │  (标定前等效于 TCP = 法兰原点)                │
         └─────────────────────────────────────────────┘
                              │
                              ▼
         IK 求解: 把 link7(法兰) 放到 flange_target, 姿态 = target_R
                              │
                              ▼
         运动执行: move_to_joints(best_q)
                              │
                              ▼
         结果验证 (FK):
           flange_pos = FK(best_q)[:3, 3]
           tcp_pos_actual = flange_pos + R_flange @ tcp_offset
           error = |tcp_pos_actual - tcp_target_pos|
```

### 13.4 切预览 (Preview Rollout) 中的 TCP offset

切预览生成一系列下切目标点（刀刃中心沿 -Y 方向逐步下移）。每个 preview 点同样需要 TCP→法兰补偿：

```python
for i, preview_tcp_pos in enumerate(cut_trajectory):
    # 每个 preview 点的目标姿态不变（切削过程中保持刀姿态）
    flange_preview_pos = preview_tcp_pos - target_R @ tcp_offset
    q_solution = IK(flange_preview_pos, target_eul, seed=上一个解)
```

preview 评分逻辑（path_cost, jump_cost, limit_cost 等）不受影响，因为它们评估的是关节空间的运动质量。

### 13.5 配置存储

```yaml
# cuttofo_config.yaml
arms:
  right:
    tcp_offset: [0.0, 0.0, 0.0]    # 标定前默认值
    # 标定后示例: [-0.003, 0.090, -0.209]
    urdf:
      tip_link: "AR5-5_07R-W4C1C1_link7"   # IK 目标 = 法兰
      ...
  left:
    tcp_offset: [0.0, 0.0, 0.0]    # 标定前默认值
    urdf:
      tip_link: "AR5-5_07L-W4C1C1_link7"   # IK 目标 = 法兰
      ...
```

### 13.6 加载与生效

- `xcore_arm_adapter.__init__()` 从 `cuttofo_config.yaml` 读取 `tcp_offset`
- 所有 FK/IK 操作在 adapter 内部自动补偿
- 上层代码（action_server、coordinator、视觉管线）无需感知 tcp_offset 的存在
- 切换左右臂时自动切换到对应的 tcp_offset

### 13.7 标定流程（后续实施）

**方法**: 多点标定法（如 4 点法 / 6 点法）

**原理**: 固定一个空间参考点（如针尖），用不同法兰姿态让刀刃中心触碰同一点。
由于 `tcp_pos = flange_pos + R_flange @ tcp_offset` 对所有姿态成立，
多组 `(flange_pos_i, R_flange_i)` 联立方程组求解 `tcp_offset`。

**输出**: `tcp_offset = [dx, dy, dz]`，写入 `cuttofo_config.yaml`

**生效**: 重启节点即自动加载，无需额外操作

### 13.8 标定前的默认行为

`tcp_offset = [0, 0, 0]` 时：

```
flange_target = tcp_target - R @ [0,0,0] = tcp_target
```

等价于：法兰原点直接到达视觉目标位置。

对比当前代码（IK 目标 = link_tcp = 法兰 + [0,0,0.097]）：
- 当前：法兰在目标位置后方 97mm（Z 方向），刀刃中心位置不可预测
- 修改后：法兰原点在目标位置，刀刃中心也在目标位置（因为 offset=0）
- 标定后：法兰在正确位置，刀刃中心精确到达视觉目标

### 13.9 与 xcore_controller 的关系

| 接口 | 返回/接收 | 说明 |
|------|----------|------|
| `/robot/get_state` → `cartesian_pose` | **法兰位姿** (flangeInBase) | 代码注释+测试确认 |
| `/robot/move_joints` | 关节角 | 不涉及笛卡尔坐标 |
| `OfflineURDFKinematics.fk_matrix(q)` | **法兰位姿** (tip_link=link7) | 修改后 |

adapter 层统一处理：
- `get_pose()` → 返回 TCP 位姿 = 法兰位姿 + R @ tcp_offset
- `solve_ik(tcp_target_pos, tcp_target_eul)` → 内部转换为法兰目标再求解
- `compute_fk(joints)` → 返回 TCP 位姿 = FK(法兰) + R @ tcp_offset

### 13.10 代码修改清单（待实施）

| # | 文件 | 修改内容 |
|---|------|---------|
| 1 | `cuttofo_config.yaml` | `arms.right/left` 新增 `tcp_offset: [0,0,0]`；`tip_link` 改为 `link7` |
| 2 | `xcore_arm_adapter.py` | 加载 `tcp_offset`；`solve_ik()` 内部做 TCP→法兰补偿；`compute_fk()` 和 `get_pose()` 返回 TCP 位姿 |
| 3 | `execute_prepare_pose.py` | 删除硬编码 `_FLANGE_TO_TCP`，改用 adapter 统一接口 |
| 4 | `prepare_pose_selector.py` | `tip_link` 改为 `link7`，preview 中加入 TCP offset 补偿 |
| 5 | `knife_prepare_action_server.py` | 无需修改（语义不变：传入的是"刀刃中心目标"，adapter 内部补偿） |
| 6 | `tofu_state_node.py` | 无需修改（输出的 tcp_target 语义不变） |
| 7 | `tofu_geometry.py` | Phase2右侧prepare逻辑需要修改：A/B改为Z最大两点，l选择base_Z-方向 |
