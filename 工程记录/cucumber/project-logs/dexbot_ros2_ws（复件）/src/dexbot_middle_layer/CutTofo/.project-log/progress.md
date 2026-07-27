# Progress Log

## 2026-06-11 CST (left handoff — 根因定位：构建产物过期 + from_euler bug 确认)

- Type: debug | fix
- Status: complete
- Importance: critical
- Objective: 用户运行 debug_left_handoff 后左手仍不到示教点位，排查根因。

**根因：构建产物 (build/lib/**/*.py) 是旧版代码，未随源码更新。**

| 文件 | 构建产物 (旧) | 源码 (新) |
|------|-------------|----------|
| debug_left_handoff.py | `R.from_quat(tcp_quat)` — 用 TCP 四元数 | `R.from_euler("xyz", flange_eul)` — 用法兰欧拉角 |
| debug_left_handoff.py | 不调用 `get_flange_pose()` | 调用 `get_flange_pose()` |
| capture_left_handoff_flange_pose.py | `R.from_quat(tcp_quat)` | `R.from_euler("xyz", flange_eul)` |
| capture_left_handoff_flange_pose.py | `derive_right_flange_target_offset_sample` (deprecated) | `derive_right_flange_target_offset_absolute` |
| capture_left_handoff_flange_pose.py | 存储 TCP quat 为 flange_quat | 存储正确的 flange quat |

- **原因：** egg-link 模式 + colcon build 未刷新 build/lib/ 下的 .py 文件。
- **修复：** `colcon build` + 手动 `cp` 覆写 6 个关键 .py 文件。
- **验证：** 构建产物中 `from_euler` 全部为 `from_euler("xyz", array)` ✓。

**连带发现：标定数据 left_flange_pose_candidates.yaml 是用旧采集代码（TCP quat 当法兰旋转）采集的，6 组 derived_offset 完全不可信。**

- **清理：**
  - `right_flange_target_offset` → `[0.0, 0.0, 0.0]`
  - `left_flange_pose_candidates.yaml` → 清空
- **下一步：** 双臂到位后运行 `capture_left_handoff_flange_pose` 重采 5-6 组，复制 mean 到 params YAML，再跑 `debug_left_handoff` 验证。

## 2026-06-11 CST (left handoff — 全链路数学公式审计，代码逻辑正确，待真机复验)

- Type: audit | analysis
- Status: complete
- Importance: high
- Reusable: yes
- Objective: 用户反馈左臂 handoff "完全没达到想要的效果"，要求逐文件排查代码是否符合其业务思路。
- Work completed:
  1. **需求复述与确认**：
     - 右臂 TCP = 刀尖中心点，左臂 TCP = 灵巧手中指指尖
     - 右臂在容器中心保持不动；offset 定义在**右臂法兰坐标系**下（右法兰姿态 = 右 TCP 姿态）
     - `handoff_point = right_tcp + R_right_flange @ offset` → T_lr → left_tcp_target
     - 左臂 TCP 目标 + 候选法兰 quat（示教姿态）→ 反算 flange pose6 → FLANGE:: move_cartesian
     - 标定：offset=0 名义目标 vs left_actual 偏差 → 反推全量 offset
  2. **数学公式全链路验证（全部正确）**：
     - `compute_left_handoff_tcp_target()`: `left_target = T_lr @ (right_tcp + R_flange @ offset)` ✓
     - `derive_right_flange_target_offset_absolute()`: `offset = R_flange^T @ (T_rl @ left_actual - right_tcp)` ✓
     - 可逆验证：offset_new 代回 compute_ → 恒等于 left_actual ✓
     - `left_handoff_tcp_to_flange_pose6()`: `flange = tcp - R(quat) @ tcp_offset` ✓
     - `_candidate_flange_target()`: 同公式计算目标法兰位置用于候选选择 ✓
     - 基座变换 T_lr = [diag(1,-1,-1), [0,0,-0.20]] 自逆，方向正确 ✓
  3. **控制器 FLANGE:: 链路验证（正确）**：
     - `xcore_controller_node.py`: FLANGE:: 前缀 → `input_is_flange=True`
     - `robot_controller_motion.py`: `ToolOffsetConfig.ENABLED and not input_is_flange` 时跳过
     - 法兰坐标直送 SDK IK ✓
  4. **采集链路 `capture_left_handoff_flange_pose.py`（公式正确）**：
     - cfg_zero_offset → left_nominal = T_lr @ right_tcp ✓
     - `derive_right_flange_target_offset_absolute()` → 全量 offset ✓
     - 6 组样本均值 [0.306, -0.303, 0.115] 写入 candidates yaml ✓
  5. **候选选择链路 `left_flange_pose_candidates.py`（正确）**：
     - `precheck_tcp_fixed_orientation()`: flange quat → TCP quat → SDK IK ✓
     - 最近邻选优：`distance(taught_flange, computed_flange)` ✓
  6. **workflow 执行链路 `tofu_second_cross_cut_workflow.py`**：
     - `_left_handoff_pose()` → `select_` → `ros_move_pose_from_selection` → `move_cartesian(FLANGE::)` ✓
     - **CRITICAL**: `_DEBUG_STOP_AFTER_TRANSFER = True` → 第 586/613/624 行跳过 handoff，**workflow 内永远不执行**
  7. **`debug_left_handoff.py`**：
     - `from_euler("xyz", ...)` 参数顺序已修正，当前正确 ✓
     - 此前崩溃原因是 `from_euler(np_array, "xyz")` 参数反了
- Problems encountered:
  1. **`_DEBUG_STOP_AFTER_TRANSFER = True`（CRITICAL）**：workflow 内 left handoff 被 guard block `not _DEBUG_STOP_AFTER_TRANSFER`（第 586 行）跳过目标计算，第 613 行 break + 第 624 行 return → 左臂运动代码（668-713 行）永不可达。**只能用 `debug_left_handoff.py` 测试。**
  2. **`from_euler` 参数 bug（可能根因）**：此前 `R.from_euler(np_array, "xyz")` → 右法兰旋转矩阵错误 → offset 方向错误 → 左臂飞到错误位置 → 用户 "完全没达到效果"。已修复，未复验。
  3. **标定数据分散 ~5-7cm**：6 组 left_actual_tcp_base 不收敛（X 0.180-0.231, Y 0.039-0.111, Z 0.242-0.291），示教可能非同刀点。
  4. **无自动化 offset 回写**：采集脚本只写 candidates yaml，用户需手动复制 mean 到 params yaml。
- Resolution:
  - 所有数学公式与用户需求一致，**无需修改代码逻辑**。
  - 改 `_DEBUG_STOP_AFTER_TRANSFER = False` 即可在 workflow 内执行 handoff。
  - `from_euler` 已修复，真机复验后可确认是否到位。
- Files audited:
  - `left_handoff_pose.py` — 公式 ✓
  - `left_handoff_transform.py` — 基座变换 ✓
  - `left_flange_pose_candidates.py` — 候选选择 ✓
  - `capture_left_handoff_flange_pose.py` — 标定 ✓
  - `debug_left_handoff.py` — 独立调试 ✓
  - `tofu_second_cross_cut_workflow.py` — 执行链路 ✓（debug flag 阻塞）
  - `xcore_controller_node.py` — FLANGE:: 前缀处理 ✓
  - `robot_controller_motion.py` — ToolOffsetConfig 跳过 ✓
  - `xcore_direct_executor.py` — IK 预检 ✓
- Next steps:
  1. `colcon build --symlink-install --packages-select dexbot_bottom_layer cuttofo_skill_tofu_second_cross_cut` → 重启控制器
  2. 真机 `debug_left_handoff` → 看 `err=XX.Xmm`（from_euler 修复后首次复验）
  3. 若 err > 5mm → offset 清零重采 → 同刀点、只变姿态
  4. 到位确认 → `_DEBUG_STOP_AFTER_TRANSFER = False` → 接完整 workflow

## 2026-06-11 CST (left handoff — 全链路排查与运动语义修正，**问题未解决**)

- Type: workflow | root-cause | fix | follow-up
- Status: partial
- Importance: high
- Reusable: yes
- Objective: 修复 `second_cross_cut` 左臂交接（right TCP + 右臂法兰系 offset → 左臂 TCP 目标 + 候选姿态），使 `debug_left_handoff` 真机到达拖动示教点。
- Work completed:
  1. **全链路语义对齐（用户确认的设计）**
     - 右臂：刀刃 TCP 在容器中心作为锚点；`handoff_right = right_tcp + R_右法兰 @ offset`；经 `T_lr` 得左臂 TCP 目标。
     - 左臂：候选只负责**姿态**（示教法兰 quat）；`left_handoff.tcp_offset` 为 skill 内唯一 TCP 定义。
     - 运动：skill 内 **TCP → 法兰** 再下发；**不读** `src/config/tool_offset.yaml`。
  2. **`left_handoff_pose.py`**
     - `compute_left_handoff_tcp_target`：offset 在右臂法兰系。
     - `derive_right_flange_target_offset_absolute`：绝对 offset 反解（替代旧残差公式）。
     - `left_handoff_tcp_to_flange_pose6` / `left_handoff_ros_move_pose_from_selection`：仅用 `left_handoff.tcp_offset` 转法兰 pose6。
  3. **采集 `capture_left_handoff_flange_pose.py`**
     - 读右臂 `get_flange_pose()` 作 offset 旋转系；`left_target_tcp_base` 存零 offset 名义目标；绝对 offset 写入 yaml。
     - 修复 ROS executor spin（此前会话）；修复 `R.from_euler("xyz", angles)` 参数顺序（曾导致 `debug_left_handoff` 崩溃）。
  4. **运动下发（与右臂 hook_lift 同思路）**
     - `XcoreArmAdapter.move_cartesian(..., target_is_flange=True)` → label 前缀 `FLANGE::`。
     - `xcore_controller_node` + `robot_controller_motion.py`：`FLANGE::` 时跳过 `ToolOffsetConfig`，输入按 **flangeInBase** 执行。
  5. **其它同分支改动**
     - `_DEBUG_STOP_AFTER_TRANSFER = False`；hook_lift `pre_lift_neg_base_x` 可选分支；`transfer_reorient_frame: flange` 默认。
     - `arms.yaml` 左臂 `tcp_offset` 与 `left_handoff.tcp_offset` 对齐。
- Problems encountered:
  1. **IK 预检 OK 但真机不到点**：根因是运动链坐标系混用（曾发 grasp/TCP/法兰混用；控制器 `tool_offset.yaml` 与 skill offset 不一致曾差 ~10–27 cm）。
  2. **offset 采集旧数据**：yaml 中 6 组 `derived_offset` 按旧残差公式、且各组 `left_actual` 相差 ~4–5 cm（示教可能非同一刀点）。
  3. **`debug_left_handoff` 运行时崩溃**：`R.from_euler(np_array, "xyz")` 参数反了 → 已改为 `R.from_euler("xyz", np_array)`。
- Resolution:
  - 运动语义与 FLANGE:: 通路：**代码已改，真机到达误差未复验**。
  - 交接位置不准：**未解决**（用户确认暂停时仍不到示教点）。
- Verification:
  - `python3 -m py_compile` 相关模块通过。
  - 用户曾跑通 IK 日志（`TCP err 0.0mm`）但反馈仍不到位；修复 `from_euler` 后 **未再跑完整真机闭环**。
  - `err=XX.Xmm` 到达日志已加在 `debug_left_handoff`，尚未有有效读数。
- Unverified items:
  - `FLANGE::` 控制器改动是否已 `colcon build dexbot_bottom_layer` 并重启 dual controllers。
  - 现有 `right_flange_target_offset: [0.306476, -0.302685, 0.114752]` 是否仍适用（建议重采绝对 offset）。
  - 6 组候选是否满足「同刀点、只变姿态」。
- Files changed (left handoff 相关):
  - `cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/left_handoff_pose.py`
  - `.../left_flange_pose_candidates.py`（既有）
  - `.../capture_left_handoff_flange_pose.py`
  - `.../debug_left_handoff.py`
  - `.../tofu_second_cross_cut_workflow.py`
  - `.../config/tofu_second_cross_cut_params.yaml`
  - `.../config/left_flange_pose_candidates.yaml`（历史采集数据，可能需重采）
  - `cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/arm/xcore_arm_adapter.py`
  - `dexbot_bottom_layer/dexbot_bottom_layer/xcore_controller_node.py`
  - `dexbot_bottom_layer/dexbot_bottom_layer/xcore_controller/robot_controller_motion.py`
  - `cuttofu_skills/cuttofo_skill_common/config/arms.yaml`
- Next steps:
  1. `colcon build --symlink-install --packages-select dexbot_bottom_layer cuttofo_skill_tofu_second_cross_cut cuttofo_skill_common` → 重启双臂控制器。
  2. `ros2 run cuttofo_skill_tofu_second_cross_cut debug_left_handoff` → 看 `err=XX.Xmm` 与控制器日志 `[flangeInBase]`。
  3. params 中 `right_flange_target_offset: [0,0,0]` 后重跑 `capture_left_handoff_flange_pose`，更新 mean 到 params。
  4. 若 err 仍大：核对示教是否同刀点；必要时仅重采 offset、保留候选姿态。

## 2026-06-11 CST (reorient frame)

- Objective: transfer 到达容器上方后的 reorient（刀面微倾）段增加参考系可配置，允许在右臂法兰坐标系与 TCP 坐标系之间切换；默认改为法兰固定。
- Work completed:
  1. 在 `config/tofu_second_cross_cut_params.yaml` 的 `hook_lift:` 段新增 `transfer_reorient_frame: flange`，并附注释说明 `flange | tcp` 语义。
  2. 在 `tofu_second_cross_cut_workflow.py` 中：
     - 新增 `_flange_pos_from_pose(...)`，从 Pose waypoint 提取法兰位置。
     - 新增 `_build_transfer_reorient_waypoints(...)`，统一构建 reorient 段 waypoint。
     - `flange` 模式：固定 transfer 线性段末点法兰位置，仅插值 `plane_angle_deg` 改变 `target_rot`；transfer 为空时 fallback 到 hook_end 法兰位置。
     - `tcp` 模式：保留原有行为，固定 `transfer_end_tcp`，反算 `flange_pos = tcp_pos - R @ tcp_offset`。
     - `execute_second_cross_cut()` 读取 `transfer_reorient_frame`、非法值 fail fast，并打印 `reorient frame=... start=... end=... count=...` 日志。
  3. 静态验证通过：`python3 -m py_compile`、`yaml.safe_load`、`colcon build --paths cuttofo_skill_tofu_second_cross_cut --symlink-install`。
- Business logic impact:
  - reorient 默认语义从“TCP 原点固定、法兰补偿移动”改为“法兰原点固定、TCP 随刀面倾角变化”。
  - 若需保持旧行为，需在 YAML 显式设置 `transfer_reorient_frame: tcp`。
  - 左臂 handoff 仍消费 reorient 末姿态；切换 frame 会改变最终 TCP 位置，属预期行为。
- Unverified items:
  - `flange` / `tcp` 两种模式在真机上的物理效果差异尚未对比。
  - `transfer_end_plane_angle_deg` 在 `flange` 默认模式下是否更易让豆腐条滑落，待现场验证。
- Files changed:
  - `cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/tofu_second_cross_cut_params.yaml`
  - `cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_workflow.py`
  - `.project-log/progress.md`
  - `.project-log/current-session.md`
- Next steps:
  - 真机对比 `transfer_reorient_frame: flange`（默认）与 `tcp` 的停位与滑落效果。
  - 可配合 `_DEBUG_STOP_AFTER_TRANSFER = True` 观察容器上方最终姿态差异。

## 2026-06-11 CST (continued)

- Objective: 右臂转运链扩充 —— transfer 到达容器中心上方后，新增一步刀面倾角微调（plane_angle: 170° → 160°），TCP 位置不动，模拟人拿刀到达容器上方后微倾让豆腐条滑落的动作。
- Work completed:
  1. 在 `config/tofu_second_cross_cut_params.yaml` 的 `hook_lift:` 段末尾添加 `transfer_end_plane_angle_deg: 160.0`，与 `hook_target_plane_angle_deg: 170.0` 放在一起便于对照。
  2. 在工作流文件中：
     - 新增 import: `_current_edge_dir` from `debug_hook_lift`，`build_rotation_with_edge_dir` / `rotation_to_euler` from `tofu_geometry`
     - 定义缺失的 `_pose_from_flange_rot_and_pos(flange_pos, flange_rot)` helper（原本在 `_transfer_waypoints` 中被调用但未定义，依赖 `rotation_to_euler` + `pose6_to_matrix16` + `matrix16_to_pose`）
     - 在 `HookArgs` 类中添加 `transfer_end_plane_angle_deg` 参数读取
     - 在 transfer waypoints 之后追加 reorient waypoints：从当前 plane_angle 线性插值到 transfer_end_plane_angle_deg，TCP 位置保持 transfer 终点不变，核心公式 `flange_pos = tcp_pos - R(angle) @ tcp_offset`
     - reorient waypoints 直接追加到 `transfer_waypoints` 列表，最终 `all_waypoints` 中的右臂轨迹自动包含 reorient 段
  3. `py_compile` 与 `colcon build` 均通过。
- Business logic impact:
  - 右臂完整执行链变为：cut_down → hook_lift → transfer → reorient（新增）→ return_next_anchor
  - reorient 段仅改变刀面倾角，TCP 位置不动；左臂交接计算使用 reorient 后的最终姿态
- Files changed:
  - `config/tofu_second_cross_cut_params.yaml`
  - `cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_workflow.py`
  - `.project-log/progress.md`

## 2026-06-11 CST

- Objective: 修复 `capture_left_handoff_flange_pose` 采集脚本"无法读取右臂 TCP 姿态"的运行时问题。
- Work completed:
  1. 定位根因：`capture_left_handoff_flange_pose.py` 的 `main(...)` 直接创建节点后调用 `node.run()`，没有挂载 ROS executor 或 spin 线程；而 `XcoreArmAdapter` 的 `get_tcp_pose()` 内部走 `call_async()` + `_wait_node_future(...)`，依赖有执行线程持续 `spin` 才能完成异步 service future。对比 `debug_left_handoff.py` 已有 `MultiThreadedExecutor + spin thread` 模式。
  2. 在 `capture_left_handoff_flange_pose.py` 的 `main(...)` 中补齐：创建 `MultiThreadedExecutor`，`executor.add_node(node)`，后台守护线程 `executor.spin()`，退出时 `executor.remove_node / shutdown / join`。
  3. 完成 `py_compile` 与 `colcon build` 验证，用户真机运行确认通过。
- Business logic impact:
  - 采集脚本现在能正确读取右臂和左臂的 TCP/法兰位姿，`--once` 和交互模式均可正常采样。
  - 这是采集脚本升级后的遗留运行时问题，纯粹是 ROS 异步 service 调用缺少 executor 驱动。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/capture_left_handoff_flange_pose.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 继续用采集脚本录入多组左臂候选法兰姿态 + offset 标定样本。
  - 连续采多组后对比 `derived_right_flange_target_offset_mean` 是否符合现场直觉，再由你决定是否把均值写回 `left_handoff.right_flange_target_offset`。

## 2026-06-10 CST

- Objective: 升级 `capture_left_handoff_flange_pose`，使其在采集左臂候选法兰姿态时，同步记录每次交接样本反解出的 `right_flange_target_offset`，并在 skill-local 文件内直接维护多组样本均值。
- Work completed:
  1. 扩展 `left_handoff_transform.py`，补齐左右臂 base 间的点/向量双向变换 helper，使“左 base 下 TCP 误差 -> 右 base -> 右法兰坐标系 offset”这条反解链路在 second_cross_cut 包内闭合。
  2. 在 `left_handoff_pose.py` 中新增 `derive_right_flange_target_offset_sample(...)`，统一实现：
     - 读取当次无微调目标 `left_target_tcp_base`
     - 读取左臂实际 TCP `left_actual_tcp_base`
     - 先得到 `delta_left`
     - 再转为 `delta_right_base`
     - 最后用 `R_right^T @ delta_right_base` 反解出 `derived_right_flange_target_offset`
     其语义严格保持为“右臂法兰坐标系下的偏移”。
  3. 扩展 `left_flange_pose_candidates.py` 的 `LeftFlangePoseCandidate` 数据结构，使候选文件现在除 `flange_pos_base` / `flange_quat_xyzw` 外，还可携带：
     - `left_target_tcp_base`
     - `left_actual_tcp_base`
     - `right_tcp_in_right_base`
     - `right_flange_quat_xyzw`
     - `derived_right_flange_target_offset`
     同时保持旧格式兼容，正式候选选择逻辑仍只依赖 `flange_pos_base` 最近原则，不改变运行时排序准则。
  4. 升级 `left_flange_pose_candidates.yaml` 顶层结构，新增：
     - `right_flange_target_offset_samples`
     - `derived_right_flange_target_offset_mean`
     让候选姿态采集文件同时承担 offset 标定样本容器角色。
  5. 重写 `capture_left_handoff_flange_pose.py`：
     - 保留 `--list / --remove / --once / --label`
     - 新增右臂/左臂 `XcoreArmAdapter` 接线读取当前 TCP
     - 保留原始 `XCoreLbotRobot` 读取左臂当前法兰位姿
     - 每次 Enter 采样时同时记录：
       - 左臂法兰位姿与法兰位置
       - 左臂目标 TCP
       - 左臂实际 TCP
       - 右臂当前 TCP
       - 右臂当前法兰四元数
       - 当次反解出的 `derived_right_flange_target_offset`
     - 每次追加样本后立即重算并落盘 `derived_right_flange_target_offset_mean`
     - 交互输出同步打印本次样本与当前均值，便于现场判断样本是否收敛。
  6. 在 `tofu_second_cross_cut_config.py` 中新增 `left_handoff_offset_mean()` helper，便于后续从 skill-local 候选文件直接读取当前样本均值；这一步仍不自动回写主 `tofu_second_cross_cut_params.yaml`，保持 `right_flange_target_offset` 由人工确认后再填入运行配置。
- Business logic impact:
  - 现在一次采样不再只是采“姿态候选”，而是同时采“姿态候选 + offset 标定样本”。
  - 候选选择依然使用 `flange_pos_base` 和目标法兰位置最近原则；新增字段主要服务标定和复盘，不干扰正式 workflow 选姿逻辑。
  - offset 的最终语义已经明确收敛为右臂法兰坐标系下解释，避免把左 base 下误差直接误当成运行参数。
- Unverified items:
  - 还未做真机采样验证多组 `derived_right_flange_target_offset` 是否稳定收敛。
  - 主运行配置 `left_handoff.right_flange_target_offset` 仍保持你之前要求的人工确认后再写入，不会由采集脚本自动覆盖。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/left_flange_pose_candidates.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/left_handoff_transform.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/left_handoff_pose.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/left_flange_pose_candidates.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/capture_left_handoff_flange_pose.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_config.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 先跑 `ros2 run cuttofo_skill_tofu_second_cross_cut capture_left_handoff_flange_pose --once --label test_pose` 检查单次采样字段与均值落盘是否正确。
  - 连续采多组后，对比 `derived_right_flange_target_offset_mean` 是否符合现场直觉，再由你决定是否把均值写回 `left_handoff.right_flange_target_offset`。

## 2026-06-10 CST

- Objective: 将 `second_cross_cut` 左臂交接姿态从“复制右臂姿态”改为“左臂候选法兰姿态库选择”，并补齐 skill-local 候选库与采集脚本。
- Work completed:
  1. 在 `cuttofo_skill_tofu_second_cross_cut/config/` 下新增 `left_flange_pose_candidates.yaml`，把左臂交接候选姿态库严格收口在当前 skill 本地配置目录。
  2. 在 `tofu_second_cross_cut_config.py` 中新增候选文件路径 helper，并把 `left_handoff` 扩展为候选库 / direct-executor / IK 容差等配置入口；旧的 `use_right_target_orientation` 语义停止使用。
  3. 新增 `left_flange_pose_candidates.py`，复用 `sauce_pour` 模式完成：候选解析、`precheck_tcp_fixed_orientation(...)` 预检、基于 `tcp_offset` 反算目标法兰点、再按“候选记录法兰位置距离目标法兰位置最近”选优。
  4. 新增 `left_handoff_pose.py`，把“右臂当前 TCP + 右法兰 offset -> 左臂 base 下目标 TCP 点 -> 候选姿态选择”链路集中封装，供正式 workflow 和独立调试脚本共用。
  5. 重写 `tofu_second_cross_cut_workflow.py` 左臂交接分支：
     - 增加左臂 `XcoreDirectExecutor` 仅用于候选 IK 预检
     - 正式执行时仍保留 `XcoreArmAdapter.move_cartesian(...)`
     - 日志输出改为 candidate label / quat / left flange target / diag
     - 若所有候选都不可达，则直接失败，不再回退到复制右臂姿态
  6. 重写 `debug_left_handoff.py`，使独立测试脚本与正式 workflow 完全复用同一套候选选择逻辑，不再残留旧的姿态复制路径。
  7. 新增 `capture_left_handoff_flange_pose.py`，复用现有姿态采集交互模式，默认把左臂候选法兰姿态写入 `config/left_flange_pose_candidates.yaml`，并支持 `--list / --remove / --once / --label`。
  8. 在 `setup.py` 中新增 `capture_left_handoff_flange_pose` console entry，便于现场直接 `ros2 run`。
  9. 完成静态与构建验证：
     - `python3 -m py_compile` 通过：`tofu_second_cross_cut_workflow.py`、`tofu_second_cross_cut_config.py`、`left_flange_pose_candidates.py`、`left_handoff_pose.py`、`debug_left_handoff.py`、`capture_left_handoff_flange_pose.py`
     - `colcon build --base-paths src/dexbot_middle_layer/CutTofo --packages-select cuttofo_skill_tofu_second_cross_cut` 通过
- Business logic impact:
  - 左臂交接姿态现在已经对齐业务逻辑，来源是左臂候选法兰姿态库，而不是继续错误复用右臂姿态。
  - 正式 workflow 与独立调试脚本现在共享同一套 handoff 目标点和候选姿态筛选逻辑，后续现场验证路径一致。
  - `right_flange_target_offset` 仍保持你之前要求的留空/零值状态，等待你后续现场填写真实拨料 offset。
- Unverified items:
  - `left_flange_pose_candidates.yaml` 当前仍是空库，现场需要先通过新采集脚本录入候选姿态后，左臂交接动作才能进入真机验证。
  - 还未做真机验证来确认候选姿态库中的最优姿态是否足够适合实际拨落动作与避障余量。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/left_flange_pose_candidates.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/tofu_second_cross_cut_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/left_flange_pose_candidates.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/left_handoff_pose.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/debug_left_handoff.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/capture_left_handoff_flange_pose.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/setup.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 先运行 `ros2 run cuttofo_skill_tofu_second_cross_cut capture_left_handoff_flange_pose --once --label ...` 录入左臂候选姿态。
  - 再运行 `ros2 run cuttofo_skill_tofu_second_cross_cut debug_left_handoff --dry-run` 检查目标点、候选 label 和 left flange target 日志是否符合预期。
  - 候选库确认后，再做真机 `debug_left_handoff` 与正式 `second_cross_cut` 联调。

## 2026-06-10 CST

- Objective: 将 `second_cross_cut` 的左右臂交接逻辑从“左臂去容器中心点”修正为“左臂去右臂当前 TCP 交接点”，并补一个只验证这段逻辑的独立测试脚本。
- Work completed:
  1. 将 `left_handoff` 的目标点语义从 `container_target` 改为右臂当前 TCP 在右臂 base 下的位置，再叠加交接 offset 后转换到左臂 base。
  2. 将交接 offset 语义改为右臂法兰坐标系下的偏移：`handoff_point_right = right_tcp + R_right_flange @ right_flange_target_offset`，使 offset 能沿刀面定义，而不再绑定右臂 base 轴向。
  3. 将右臂 base -> 左臂 base 的点变换逻辑内聚到 skill 包内部，新增 `left_handoff_transform.py`，并从 `config/calibration_result_left.yaml` 读取左右臂基座关系，不再依赖外部公共几何 helper。
  4. 将左臂真实 TCP offset `[0.12296, -0.17450, -0.12458]` 写入 `tofu_second_cross_cut_params.yaml` 的 skill-local `left_handoff.tcp_offset`。
  5. 新增独立调试脚本 `debug_left_handoff.py`：
     - 读取右臂当前 TCP
     - 按现有 `left_handoff` 配置换算左臂目标 TCP / 法兰目标
     - 调用左臂 `move_cartesian(...)`
     - 支持 `--dry-run`
  6. 在 `setup.py` 中新增 `debug_left_handoff` console entry，便于现场直接 `ros2 run`。
  7. 完成静态与构建验证：
     - `python3 -m py_compile debug_left_handoff.py` 通过
     - `colcon build --base-paths src/dexbot_middle_layer/CutTofo --packages-select cuttofo_skill_tofu_second_cross_cut` 通过
- Business logic impact:
  - 当前 `second_cross_cut` 与独立测试脚本已经统一采用“右臂当前 TCP 交接点 -> 左臂 base”这套目标点定义，不再错误地把左臂目标绑定到容器中心。
  - 左臂目标姿态当前仍直接复用右臂交接时的法兰姿态，左臂自己的 TCP 仅通过 `tcp_offset` 做平移反算，还没有单独引入左臂独立姿态规划。
  - `right_flange_target_offset` 现在仍可继续留空或保持零值，后续等你现场再填真实拨料 offset 即可。
- Problems encountered:
  1. 第一版 handoff 把左臂目标点错误绑定到了容器中心，这不符合“左臂去右臂刀上拨豆腐条”的物理语义。
  2. 第一版 offset 语义放在右臂 base 坐标系下，不适合描述沿刀面的局部偏移。
- Resolution:
  - 统一改为“右臂当前 TCP + 右法兰坐标系 offset -> 左臂 base 点变换 -> 左臂 TCP/法兰目标反算”的链路，并把左右臂基座变换逻辑封装在 skill 内。
- Verification:
  - `debug_left_handoff.py` 通过 `py_compile`。
  - `cuttofo_skill_tofu_second_cross_cut` 通过 `colcon build`。
- Unverified items:
  - 真机尚未验证当前左臂目标姿态是否足够适合实际拨料动作；目前只确认了目标点计算链路和命令链路打通。
  - `right_flange_target_offset` 仍待现场填写真实值后进一步验证交接接触位置。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/tofu_second_cross_cut_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/left_handoff_transform.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/debug_left_handoff.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/setup.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 现场先用 `debug_left_handoff` 验证当前目标点和目标姿态是否能把左臂放到合适拨料位。
  - 等你补入 `right_flange_target_offset` 后，再收敛最终交接接触点位置。

## 2026-06-10 CST

- Objective: 为 `tofu_workflow_v2` / `tofu_workflow_v2_no_approach` 增加稳定的”命名阶段入口”能力，使 workflow 可在启动时直接从指定业务阶段进入，而不再靠复制多份 YAML 变体或暴露裸 step 下标。

- [2026-06-10 下午] **向后兼容性修复**: `workflow_config.resolve_workflow_entry()` 对缺少 `entry_points` 或 step `id` 的旧 YAML 不再崩溃，优雅降级为默认入口 (step 0)。4 个 YAML 全部通过校验。
- [2026-06-10 下午] **感知自动启动补齐**: 无_approach YAML 的 `tofu_perception_auto_start` 从 `false` → `true`。所有 prepare-entry 入口在 runner tick 中自动启动 tofu_perception 并 resume 到 APPLY_PARAMS。
- [2026-06-10 下午] colcon build 通过（需 `--base-paths src/dexbot_middle_layer/CutTofo`）
- Work completed:
  1. 复查当前 orchestrator 执行模型，确认现有 `workflow_runner.py` 本质是顺序 `steps + _step_index` 的 tick 状态机，因此最稳妥的实现不是重做 phase manager，而是在配置层引入 `workflow_entry -> step_id -> step_index` 的解析。
  2. 在 `workflow_config.py` 中新增 `resolve_workflow_entry(...)`：
     - 强制 `steps[].id` 非空且唯一
     - 强制 `entry_points` 非空
     - 在启动前完成 `workflow_entry` 合法性校验
     - 统一返回 `start_step_id / start_step_index / requires_confirmation / operator_prompt / skip_initial_wait_before`
  3. 在 `tofu_task_orchestrator.py` 中新增 `workflow_entry` 参数声明与入口解析，使 runner 只消费解析后的入口元信息，不再在执行层理解 YAML 别名。
  4. 在 `workflow_runner.py` 中完成运行时接线：
     - workflow 启动时从解析后的 `start_step_index` 起步，而不是固定从 0 开始
     - preflight 只检查“本次入口之后仍会执行到”的 action server，避免中途入口还依赖前序无关 skill ready
     - 对首个进入 step 单独支持入口专属 operator prompt
     - 对 `prepare_second_cut` / `prepare_after_rotation_1` 这类中途入口，支持 `skip_initial_wait_before`，避免沿用“上一阶段刚执行完”的历史 wait 文案
  5. 更新 `tofu_workflow_v2_params.yaml` 与 `tofu_workflow_v2_no_approach_params.yaml`：
     - 为关键 steps 补入稳定 `id`
     - 新增 `default_entry_point`
     - 新增 `entry_points`，当前覆盖 `full / no_approach / second_cut_prepare / second_cross_cut / vertical_cut_prepare`
  6. 更新 launch 接口：
     - `tofu_workflow_execute_v2.launch.py` 新增 `workflow_entry` 参数，默认 `full`
     - `tofu_workflow_execute_v2_no_approach.launch.py` 新增 `workflow_entry` 参数，默认 `no_approach`
  7. 更新 `cuttofo_orchestrator/README.md`，补充命名入口用法与约束说明。
- Business logic impact:
  - 现在 v2 workflow 已具备“像旧版那样手动选择进入哪个阶段”的使用效果，但底层仍保持当前 orchestrator 的 `steps` 模型，没有引入第二套 phase 跳转状态机。
  - 后续现场若已经人工把机械臂和豆腐摆到某个阶段，可直接通过 `workflow_entry:=second_cut_prepare` 或 `workflow_entry:=vertical_cut_prepare` 启动对应调试链路。
- Problems encountered:
  1. 旧框架的期望体验是“按业务阶段名启动”，而当前新框架原本只有固定顺序 `steps`，如果直接暴露数值下标会非常脆弱，且不符合现场操作心智。
- Resolution:
  - 通过“稳定 step id + 命名 entry_points + runner 首 step 特判”的方式把阶段入口能力收敛进现有编排框架内，避免复制旧 phase manager 设计。
- Verification:
  - 待执行：`python3 -m py_compile` 校验 orchestrator 相关 Python 文件。
  - 待执行：`yaml.safe_load` 校验 v2 workflow YAML 新增 `entry_points` 结构。
  - 待执行：root install 环境 `ros2 launch ... --show-args` 校验两个 launch 新增的 `workflow_entry` 参数。
- Unverified items:
  - 尚未做真机入口复测；当前只完成代码与配置接线，后续需要在现场验证 `workflow_entry:=second_cut_prepare` 是否能顺利直入第二次横切 prepare。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/tofu_task_orchestrator.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_runner.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_v2_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_v2_no_approach_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute_v2.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute_v2_no_approach.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/README.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 执行静态验证，确认新入口解析、launch 参数和 YAML 结构都无语法问题。
  - 后续现场优先复测 `workflow_entry:=second_cut_prepare` 与 `workflow_entry:=vertical_cut_prepare` 两条直接入口。

## 2026-06-10 CST

- Objective: 在 `second_cross_cut` 中补齐“右臂转运到容器中心后，把目标点交给左臂，由左臂以自身 TCP 语义移动到该点”的第一版框架，并把左臂 TCP 参数严格收口在 skill 包本地配置里。
- Work completed:
  1. 复查 `XcoreArmAdapter` 的 TCP 语义后，确认左臂这一版不需要改公共 arm adapter，只需要沿用现有“TCP 姿态默认等于法兰姿态、TCP 原点通过 `tcp_offset` 平移定义”的逻辑即可。
  2. 在 `tofu_second_cross_cut_params.yaml` 的 `profiles.round_2` 下新增包内 `left_handoff` 段，集中配置：
     - `enabled`
     - `tcp_offset`
     - `use_right_target_orientation`
     - `move_speed`
     - `timeout_s`
     - `label`
  3. 在 `tofu_second_cross_cut_config.py` 中补齐 `left_handoff` 默认值展开逻辑，使这套左臂 TCP / handoff 参数只在 `second_cross_cut` skill 内可见，不外泄到 `cuttofo_skill_common/config/arms.yaml`。
  4. 在 `tofu_second_cross_cut_workflow.py` 中新增左臂目标换算辅助：
     - `_left_handoff_target(...)`
     - `_left_handoff_pose(...)`
     复用与右臂一致的 TCP->flange 反算语义：`flange = tcp - R @ tcp_offset`。
  5. 在 workflow 初始化阶段接入左臂 adapter：
     - 通过 `get_arm_config("left")` 只读取左臂 namespace / URDF / arm identity
     - 当 `left_handoff.enabled=true` 时，建立左臂 `XcoreArmAdapter`，并完成 connect + enable
  6. 在整条右臂 RT 轨迹执行完成后，新增左臂 handoff 动作：
     - 右臂仍先连续执行 `cut + hook_lift + transfer + return_next_anchor`
     - RT 结束后，以本轮 `container_target` 作为左臂 TCP 目标点
     - 保持右臂转运终点姿态作为左臂目标姿态参考
     - 使用左臂本地 `left_handoff.tcp_offset` 反算左臂法兰目标，并调用 `left_arm.move_cartesian(...)`
  7. 为左臂 handoff 增加源码级日志，直接打印目标 TCP 与反算后的 flange 目标，便于后续现场填真实 offset 时校准。
- Business logic impact:
  - `second_cross_cut` 现在已经具备“右臂把豆腐条送到容器中心后，左臂按自己的 TCP 坐标系去同一点”的第一版控制框架。
  - 左臂 TCP 偏移参数被严格限制在 `cuttofo_skill_tofu_second_cross_cut/config/tofu_second_cross_cut_params.yaml`，没有污染公共 arm config。
  - 当前这一版仍聚焦在“右手转运完成 -> 左手 TCP 过去”，还没有继续扩展左手夹取/承接后的后续动作链。
- Problems encountered:
  1. 左臂 TCP 语义需要和右臂保持一致，但用户明确要求参数不能外泄到 shared/common config，因此不能直接把这批 handoff 参数并入 `arms.yaml`。
- Resolution:
  - 保留 `get_arm_config("left")` 只负责左臂基础身份信息；把 `second_cross_cut` 特有的左臂 TCP offset 与 handoff 速度/超时全部下沉到 skill 本地 profile。
- Verification:
  - `python3 -m py_compile tofu_second_cross_cut_workflow.py tofu_second_cross_cut_config.py` 通过。
  - `colcon build --base-paths src/dexbot_middle_layer/CutTofo --packages-select cuttofo_skill_tofu_second_cross_cut` 通过。
- Unverified items:
  - 左臂 `tcp_offset` 目前仍是占位 `[0.0, 0.0, 0.0]`，需要后续按真机 TCP 定义填入真实值。
  - 还没有做真机联调验证左臂移动到右臂交接点后的物理效果、避障余量和左右臂时序配合。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/tofu_second_cross_cut_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 现场先填入左臂真实 `left_handoff.tcp_offset`，验证左臂 TCP 是否准确到达右臂交接点。
  - 若交接姿态需要与右臂脱钩，再把 `use_right_target_orientation` 从布尔开关扩展为独立的左臂目标姿态配置。

- Work completed:
  1. 复查 `tofu_second_cross_cut_node.py` 当前容器检测回调，确认逐帧中心点日志应直接挂在 `_objects_cb(...)` 的“有效 bowl 候选已筛出且 pose 非空”分支上，这样输出的就是后续会写入 `latest/cached` 的真实消费结果。
  2. 保留源码级开关 `_DEBUG_LOG_CONTAINER_CENTER_EACH_FRAME = False`，并继续通过实例字段 `self._log_container_center_each_frame` 控制，默认关闭，不进入 YAML，避免现场参数面继续膨胀。
  3. 在 `_objects_cb(...)` 中新增逐帧日志：当本帧成功通过 `class keywords + min_confidence + 非零 pose` 过滤后，打印
     - `class`
     - `confidence`
     - `pos=(x, y, z)`
     - `stamp_ns`
  4. 该日志输出放在更新 `latest_container_pose / cached_container_pose` 之后，保证日志内容与当前 node 内部缓存状态一致。
- Business logic impact:
  - 现在只要把 `_DEBUG_LOG_CONTAINER_CENTER_EACH_FRAME` 改成 `True`，`second_cross_cut` 开始容器检测后，每一帧真正命中的 bowl 中心点都会被持续打印出来。
  - 输出的不是原始 `objects_with_pose` 全量杂项，而是经过现有筛选逻辑过滤后的有效容器中心，因此更适合直接拿来对照后续 `container_tcp_offset` 和水平对位问题。
- Problems encountered:
  1. 之前虽然已有 `latest/cached` 缓存，但缺少逐帧可见性，现场只能看到某一时刻的最终目标点，难以判断“容器中心定义漂移”还是“offset 调错”。
- Resolution:
  - 将逐帧中心点调试能力直接下沉到 `TofuSecondCrossCutNode` 的容器订阅回调里，并保持为源码开关，方便快速开关而不污染运行配置。
- Verification:
  - 待执行：`python3 -m py_compile tofu_second_cross_cut_node.py`
- Unverified items:
  - 该日志当前只输出“成功筛出有效 bowl”的帧；若后续需要同时观察未命中帧，再单独补 no-match 调试输出，避免当前日志先被噪声淹没。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_node.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 执行 `py_compile` 确认 node 静态语法无误。
  - 真机需要看逐帧中心点时，直接把 `_DEBUG_LOG_CONTAINER_CENTER_EACH_FRAME` 改为 `True` 后重启该 skill 即可。

## 2026-06-10 CST

- Objective: 在 `second_cross_cut` 中把容器检测结果真正接入右臂下游消费逻辑，使每次 `hook_lift` 后都能连续转运到容器中心，再回下一刀位。
- Work completed:
  1. 复查 `tofu_second_cross_cut_workflow.py` 当前执行链，确认要避免重复上下电，不能在 `hook_lift` 后额外发起独立控制请求，而必须把 `cut_down -> hook_lift -> transfer_to_container -> return_next_anchor` 一次性拼成同一条 RT 路径。
  2. 在 `tofu_second_cross_cut_params.yaml` 的 `round_2/default` profile 下新增 `transfer` 段，集中配置：
     - `container_tcp_offset`
     - `waypoint_count`
  3. 在 `tofu_second_cross_cut_config.py` 中补齐 `transfer` 默认值展开逻辑，使 workflow 后续可直接读取转运 offset 与 waypoint 数量。
  4. 在 `tofu_second_cross_cut_node.py` 中新增 `get_container_target(offset_xyz)`：
     - 优先读取 `latest_container_pose`
     - 若 latest 缺失则回退 `cached_container_pose`
     - 与 `container_tcp_offset` 相加后返回本轮 TCP 目标点，并标记来源是 `latest` 还是 `cached`
  5. 在 `tofu_second_cross_cut_workflow.py` 中接入第一版下游消费：
     - 每一轮 `hook_lift` 结束后只读取一次容器目标
     - 保持 hook_lift 终点姿态不变
     - 以刀刃中心 TCP 原点为平移对象，构造到 `container_center + offset` 的转运 waypoint
     - 用 `flange = tcp - R @ tcp_offset` 反算整段法兰轨迹
     - 将 `cut_down -> hook_lift -> transfer_to_container -> return_next_anchor` 全部拼进单次 `move_rt_cartesian_path(...)`
  6. 为转运终点补入源码级调试钩子：
     - 默认 `_DEBUG_STOP_AFTER_TRANSFER = False`
     - 若手动改为 `True`，skill 会在到达容器中心点后直接结束，右臂停在容器中心位置
     - 不再继续 `return_next_anchor` 和 wait joints
  7. 将 `second_cross_cut` 的容器检测入口从“固定等待 prompt 切换”改成“等待首个有效 bowl 检测结果”后再进入第 1 轮：
     - `tofu_second_cross_cut_workflow.py` 新增 `_wait_for_container_ready(...)`
     - 仅当 `match_count > 0` 且 `cached_pose != None` 时，才允许从 `vision_switch` 进入 `init/cycle 1`
     - `tofu_second_cross_cut_params.yaml` / `tofu_second_cross_cut_config.py` 新增 `vision.ready_timeout_sec` 和 `vision.ready_poll_interval_sec`
     - 若等待超时，会在 `vision_switch` 阶段直接失败，并打印当前 `msgs / matches / cached / class_id`
  8. 清理 `tofu_second_cross_cut_params.yaml` 的重复 profile：
     - 删除重复的 `default` 参数区，仅保留 `profiles.round_2`
     - 将现场正在调试的 `container_tcp_offset: [0.0, 0.16, 0.0]` 并入 `round_2.transfer`
     - 避免后续继续出现“改了 default 但运行走的是 round_2”这类误调
  9. 完成静态验证：
     - `python3 -m py_compile tofu_second_cross_cut_workflow.py tofu_second_cross_cut_node.py tofu_second_cross_cut_config.py` 通过
     - `python3` + `yaml.safe_load` 确认 `transfer.container_tcp_offset` 与 `transfer.waypoint_count` 解析通过
- Business logic impact:
  - `second_cross_cut` 已经不再只是记录容器位姿，而是开始真正消费容器中心结果，驱动右臂在每轮 `hook_lift` 后自动转运到容器区。
  - 本轮实现仍严格保持“每轮入 transfer 前只读一次 latest/cached，运动过程中不重规划”的策略，以优先保证连续性和可控性。
- Problems encountered:
  1. 原先 workflow 只保留了 `cut_down -> hook_lift -> return_next_anchor` 最小链路，没有显式的 TCP 级容器转运段，也没有 offset 配置入口。
- Resolution:
  - 补齐 `transfer` 配置和 node 级目标读取接口，再在 workflow 内按 TCP 语义生成连续 RT waypoint，避免在控制器层面重新起步。
- Verification:
  - `tofu_second_cross_cut_workflow.py`、`tofu_second_cross_cut_node.py`、`tofu_second_cross_cut_config.py` 通过 `py_compile`。
  - `tofu_second_cross_cut_params.yaml` 的 `transfer` 段通过 YAML 结构校验。
- Unverified items:
  - `container_tcp_offset` 当前仍是 `[0.0, 0.0, 0.0]` 占位值，实际落点仍需真机调参。
  - 真机尚未验证 `hook_lift -> transfer_to_container -> return_next_anchor` 连续执行时，是否已经完全消除中间重复上下电/重新起步感。
  - 真机尚未验证容器目标点高度是否足够安全，是否需要在 `container_tcp_offset.z` 中额外增加上方净空。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/tofu_second_cross_cut_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_node.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 真机先验证每轮 `hook_lift` 后右臂是否确实连续转运到容器区，再平滑回到下一刀位。
  - 现场优先收敛 `transfer.container_tcp_offset`，确认刀刃中心 TCP 对容器中心的期望相对落点。
  - 若现场发现容器上方高度不够安全，再优先通过 `container_tcp_offset.z` 做净空修正，而不是先改轨迹结构。

## 2026-06-10 CST

- Objective: 关闭 `tofu_perception_node` 启动后的持续 prompt heartbeat，避免第二次横切容器 prompt 被周期性覆盖回 `ridged_tofu_block`。
- Work completed:
  1. 根据真机日志复盘 prompt 时间线，确认 `second_cross_cut` 已经成功发布 `non-plastic ceramic bowl`，但约 5 秒后又被重写成 `ridged_tofu_block`。
  2. 复查 `tofu_perception_node.py` 后确认，覆盖源头来自豆腐感知节点自身的 startup burst 结束后自动创建 heartbeat timer，并持续调用 `_publish_prompt_once()`。
  3. 将 `tofu_perception_node.py` 改为：
     - 启动阶段仍保留 burst publish
     - burst 结束后只打日志，不再创建 heartbeat timer
  4. 将 `tofu_perception_params.yaml` 的 `heartbeat_interval_sec` 默认值改为 `0.0`，和新的运行语义保持一致。
  5. 已重新执行 `python3 -m py_compile tofu_perception_node.py`，静态编译通过。
- Business logic impact:
  - 豆腐感知节点现在只负责“开机时把默认豆腐 prompt 打上去几秒”，后续不会再持续抢写全局 `/cuttofu/vision/text_prompt`。
  - 第二次横切期间由 `second_cross_cut` skill 发布的容器 prompt 将不再被豆腐感知 heartbeat 覆盖；等第二次横切结束后，再由 skill 自己显式恢复豆腐 prompt。
- Problems encountered:
  1. 第二次横切实测时，`sam3_detector_node` 先正确切到 `non-plastic ceramic bowl`，随后又自动回到 `ridged_tofu_block`，导致容器检测目标无法持续保持。
- Resolution:
  - 停掉 `tofu_perception_node` 的持续 heartbeat prompt，只保留启动 burst，消除和 `second_cross_cut` 的全局 prompt 抢写冲突。
- Verification:
  - `python3 -m py_compile tofu_perception_node.py` 通过
  - 待补：真机复测确认 `second_cross_cut` 期间 `sam3_detector_node` 不再被重置回 `ridged_tofu_block`
- Unverified items:
  - 关闭 heartbeat 后，若后续某条 workflow 单独启动而没有其他 skill 显式恢复 prompt，是否仍满足现场默认行为，需要结合完整启动链再观察一次。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/cuttofo_skill_tofu_perception/tofu_perception_node.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_perception_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 重新启动视觉链，确认启动时仍会 burst 发布豆腐 prompt，但 5 秒后不再继续周期性发 `ridged_tofu_block`。
  - 再次执行到 `second_cross_cut`，观察 `non-plastic ceramic bowl` 是否能持续保持到横切结束。

## 2026-06-10 CST

- Objective: 在 `second_cross_cut` skill 内先落地容器视觉切换与位姿缓存逻辑，但暂不接入基于容器位姿的右臂运动消费。
- Work completed:
  1. 复查 `tofu_second_cross_cut_node.py`、`tofu_second_cross_cut_workflow.py` 和现有感知公共件后，确认当前最稳妥的接法是：由 `second_cross_cut` node 直接订阅 `/cuttofu/perception/objects_with_pose`，并复用公共 `VisionPromptClient` 发布 `/cuttofu/vision/text_prompt`。
  2. 在 `tofu_second_cross_cut_params.yaml` 的 `round_2/default` profile 下新增 `vision` 段，集中收敛：
     - `container_detection_prompt: non-plastic ceramic bowl`
     - `restore_prompt: ridged_tofu_block`
     - `objects_with_pose_topic`
     - `container_class_keywords`
     - `min_confidence`
     - `prompt_settle_sec`
  3. 在 `tofu_second_cross_cut_config.py` 中补齐 `vision` 默认值展开逻辑，使 node 参数声明与 YAML profile 保持一致。
  4. 在 `tofu_second_cross_cut_node.py` 中新增容器视觉状态层：
     - 订阅 `/cuttofu/perception/objects_with_pose`
     - 按 `class_id` 关键词和最小置信度筛选容器候选
     - 将有效容器中心保存为 `latest_container_pose`
     - 同步维护 `cached_container_pose` 作为后续短时丢检 fallback 基础
     - 暴露 `begin_container_tracking()` / `restore_tracking_prompt()` / `get_container_pose_state()` 给 workflow 调用
  5. 在 `tofu_second_cross_cut_workflow.py` 中接入 skill 内视觉流程：
     - 动作开始前切 prompt 到 `non-plastic ceramic bowl`
     - 结束时无论成功/失败/取消统一恢复 `ridged_tofu_block`
     - 当前阶段只记录容器 latest/cached state 日志，不把容器位姿用于任何右臂移动求解
  6. 完成静态验证：
     - `python3 -m py_compile tofu_second_cross_cut_node.py tofu_second_cross_cut_workflow.py tofu_second_cross_cut_config.py` 通过
- Business logic impact:
  - 容器检测提示词切换、位姿订阅、latest/cached 缓存现在已经真正下沉到 `second_cross_cut` skill 包内部，后续右臂每次去容器前都可以直接从 skill 内拿到“最新值 + 上次有效值”。
  - 本轮改动仍严格停留在视觉层，没有开始写“检测到容器后右臂怎么移动”的消费逻辑，因此不会提前耦合 transfer 运动方案。
- Problems encountered:
  1. 现有 `tofu_second_cross_cut` 还没有任何 node 级感知状态，因此必须先在 action server node 自己挂容器 topic 订阅，不能只在 workflow 里临时读一次。
- Resolution:
  - 将容器 prompt 和 pose cache 能力收拢到 `TofuSecondCrossCutNode`，让 workflow 只负责在合适的时机调用开始/恢复接口，并读取缓存状态。
- Verification:
  - `tofu_second_cross_cut_node.py`、`tofu_second_cross_cut_workflow.py`、`tofu_second_cross_cut_config.py` 通过 `py_compile`。
- Unverified items:
  - 真实运行时 `objects_with_pose` 上容器 `class_id` 是否稳定落在当前 `container_class_keywords` 里，仍需现场 topic 回放或真机联调确认。
  - prompt 切到 `non-plastic ceramic bowl` 后，SAM3/pose_estimator 的收敛时间是否只需当前 `prompt_settle_sec=0.35`，仍需实机观察。
  - latest/cached pose 目前只做记录，尚未验证后续 transfer 阶段消费这两个状态时的业务效果。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/tofu_second_cross_cut_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_node.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 先在真机或 topic 回放下确认容器 prompt 切换后，`/cuttofu/perception/objects_with_pose` 能稳定产出 bowl 类别与中心点。
  - 在确认视觉层稳定后，再单独接“右臂每次去容器前优先用 latest、否则 fallback cached”的运动消费逻辑。

## 2026-06-10 CST

- Objective: 将第二次斜切的 prepare 偏移参数从 `first_cut` 共用配置中拆分出来，使第 2 次斜切拥有独立 `target_offset_m` 可调入口。
- Work completed:
  1. 复查 `tofu_prepare_params.yaml` 与各 workflow 配置，确认当前第一、第二次斜切 prepare 都在复用 `profile: first_cut`，因此 `target_offset_m` 无法分开调。
  2. 在 `cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml` 中新增 `profiles.second_cut`，几何参数沿用 `first_cut`：
     - `plane_angle_deg: 135.0`
     - `edge_align: true`
     - `joint_speed` / `candidate_count` / `preview_steps` 等求解参数与 `first_cut` 保持一致
  3. 将第二次斜切独立偏移参数放入 `second_cut.target_offset_m`，作为后续专门给 round_2 prepare 调参的入口。
  4. 将 4 条豆腐 workflow 中“第 2 次斜切前的 prepare step”全部从 `profile: first_cut` 切换为 `profile: second_cut`：
     - `tofu_workflow_params.yaml`
     - `tofu_workflow_no_approach_params.yaml`
     - `tofu_workflow_v2_params.yaml`
     - `tofu_workflow_v2_no_approach_params.yaml`
  5. 完成静态验证：
     - `yaml.safe_load` 成功解析 5 个相关 YAML 文件
     - root install 环境下 `ros2 launch cuttofo_orchestrator tofu_workflow_execute_v2_no_approach.launch.py --show-args` 通过
- Business logic impact:
  - 第一次斜切 prepare 与第二次斜切 prepare 现在已经解耦，后续你可以只改 `second_cut.target_offset_m`，不会再影响第一刀下刀定位。
  - 这次改动只拆 profile 和 workflow 引用，不改变 prepare 求解逻辑本身。
- Problems encountered:
  1. 初始尝试把“第二次斜切独立 offset”直接追加到 `first_cut` 下作为额外字段，这种做法虽然满足“追加在原字段下边”，但 prepare 运行时并不会自动消费该自定义字段，不能真正形成独立 profile。
- Resolution:
  - 改为新增显式 `second_cut` profile，并让 workflow 在第二次斜切前真正引用 `profile: second_cut`，这样独立 offset 才会生效。
- Verification:
  - `tofu_prepare_params.yaml` 以及 4 个 workflow YAML 均完成静态解析校验。
  - `tofu_workflow_execute_v2_no_approach.launch.py --show-args` 仍通过，说明 workflow 接线未破坏启动入口。
- Unverified items:
  - `second_cut.target_offset_m` 的当前数值是否已经达到最佳第二次斜切定位效果，仍需继续真机调参。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_no_approach_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_v2_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_v2_no_approach_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 直接在真机上只调 `second_cut.target_offset_m`，收敛第二次斜切 prepare 的独立定位效果。
  - 若后续第一次斜切也要继续细调，则分别维护 `first_cut.target_offset_m` 与 `second_cut.target_offset_m` 两组参数。

## 2026-06-10 CST

- Objective: 修正第二次横切 `hook_lift` 的转姿参照系，避免“固定法兰原点转姿”导致刀刃中心在豆腐内部扫弧、把豆腐条挂烂。
- Work completed:
  1. 复查 `debug_hook_lift.py` 后确认，当前姿态段的 waypoint 生成是“保持法兰位置不变，只改变姿态”，因此实际被固定的是法兰原点而不是刀刃中心 TCP。
  2. 复用共享臂配置 `arms.yaml` 中的右臂 `tcp_offset`，将当前法兰姿态转换为当前刀刃中心 TCP 原点。
  3. 将 `hook_lift` 的转姿段改为：保持 TCP 原点不变，只改变目标 plane angle；随后根据 `flange_pos = tcp_pos - R_target @ tcp_offset` 反算每个 waypoint 的法兰位置。
  4. 将平移段也统一改为基于 TCP 轨迹构造，再反算对应法兰 waypoint，确保整段 `hook_lift` 都以刀刃中心 TCP 为操作对象。
  5. 将同一套 TCP 中心化 waypoint 逻辑同步作用到：
     - 独立调试入口 `debug_hook_lift.py`
     - workflow 正式链路 `tofu_second_cross_cut_workflow.py`
  6. 增强调试日志，单个 waypoint 同时打印 flange 与 tcp 坐标，便于现场直接观察“法兰在补偿移动、刀刃 TCP 保持稳定”的效果。
  7. 完成静态验证：
     - `python3 -m py_compile debug_hook_lift.py tofu_second_cross_cut_workflow.py` 通过
     - `colcon build --paths cuttofo_skills/cuttofo_skill_tofu_second_cross_cut --symlink-install` 通过
     - root install 环境下 `ros2 launch cuttofo_orchestrator tofu_workflow_execute_v2_no_approach.launch.py --show-args` 通过
- Business logic impact:
  - `hook_lift` 的“先转姿再上挑”现在以刀刃中心 TCP 为真实约束对象，更符合现场业务语义：调整刀面倾角时，刀刃中心不应大幅偏离当前挂条位置。
  - 该修改不改变动作分段顺序，但改变了每个姿态段 waypoint 的空间含义：从“法兰原地转姿”变为“法兰补偿移动以保持 TCP 原地转姿”。
- Problems encountered:
  1. 现场复测发现，虽然连续性问题已解决，但转姿阶段仍会因为法兰原地不动而让刀刃中心扫弧，导致豆腐条被挂烂。
- Resolution:
  - 将 `hook_lift` 的轨迹构造语义下沉到 TCP 层，再由 TCP 目标反算法兰轨迹，优先保证刀刃中心稳定。
- Verification:
  - 更新后的 `debug_hook_lift.py` 与 `tofu_second_cross_cut_workflow.py` 均通过 `py_compile`。
  - `cuttofo_skill_tofu_second_cross_cut` 重新 `--symlink-install` 构建通过。
  - `tofu_workflow_execute_v2_no_approach.launch.py --show-args` 仍通过，说明 workflow 入口未被破坏。
- Unverified items:
  - TCP 中心化后，真机上转姿阶段是否已经足够稳定、不会再把豆腐挂烂，仍需现场复验。
  - 由于法兰会为保持 TCP 稳定而做补偿平移，仍需观察刀背/法兰附近几何是否引入新的碰擦风险。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/debug_hook_lift.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 直接用 `tofu_workflow_execute_v2_no_approach.launch.py` 做真机复测，重点观察转姿阶段刀刃是否稳定、豆腐条是否还会被挂烂。
  - 若刀刃已稳定，再继续微调 `hook_target_plane_angle_deg` 与上挑位移参数；若仍有残余问题，再细查 TCP 偏移标定值是否需要复核。

## 2026-06-10 CST

- Objective: 继续压缩 `second_cross_cut` 第二次横切中的轮次边界顿挫，尝试消除“回到下一个切割点后再重新起动作”的重复上下电体感。
- Work completed:
  1. 复查 `tofu_second_cross_cut_workflow.py` 后确认，上一版虽然已把单轮内部的 `cut_down + hook_lift + return_next_anchor` 合并，但仍然是“每轮一次 RT 请求”，轮次边界仍可能触发控制器重新起步。
  2. 将执行模型进一步改为“整个 `round_2` 全轮次共用一次 `move_rt_cartesian_path(...)` 请求”。
  3. 在进入执行前预构建所有 cycle 的 waypoint：
     - `cut_down`
     - `hook_lift`
     - `return_next_anchor`（最后一轮除外）
  4. 将所有轮次轨迹拼接为单个 `all_waypoints`，只执行一次 `_run_rt(...)`。
  5. 同步修正 `feedback_cb` 的 waypoint 总数统计，改为基于 `len(all_waypoints)`，避免沿用旧的按轮次粗估计数。
  6. 完成静态验证：
     - `python3 -m py_compile cuttofo_skill_tofu_second_cross_cut/.../tofu_second_cross_cut_workflow.py` 通过
     - `colcon build --paths cuttofo_skills/cuttofo_skill_tofu_second_cross_cut --symlink-install` 通过
     - root install 环境下 `ros2 launch cuttofo_orchestrator tofu_workflow_execute_v2_no_approach.launch.py --show-args` 通过
- Business logic impact:
  - `second_cross_cut` 已从“按轮分段请求控制器”改成“整段第二次横切一次性下发连续轨迹”，当前目标是最大化保留 `hook_lift -> return_next_anchor -> 下一刀` 之间的连续性。
  - 这次优化不改变第二次横切的业务步骤顺序，只改变底层 RT 轨迹下发的分段方式。
- Problems encountered:
  1. 第一轮连续性优化后，用户实测仍观察到：一次横切下去、挑上来、回到下一个切割点之后，会再出现一次类似上下电/重新起步感，然后才继续下一次斜切。
- Resolution:
  - 将轮次边界从“多次 RT 请求”进一步压缩为“单次 RT 请求”，优先排除 workflow 层分段调用造成的控制切换感。
- Verification:
  - `tofu_second_cross_cut_workflow.py` 语法通过 `py_compile`。
  - `cuttofo_skill_tofu_second_cross_cut` 重新 `--symlink-install` 构建通过。
  - v2 no-approach workflow 的 launch 解析仍通过。
- Unverified items:
  - 该改动是否已经在真机上彻底消除轮次边界的重复上下电/顿挫感，尚未收到新的硬件反馈。
  - 若仍存在残余现象，则更可能来自 `/arm_r/robot/move_rt_cartesian_path` 底层控制实现，而非当前 workflow 的路径分段。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 直接用 `tofu_workflow_execute_v2_no_approach.launch.py` 做真机复测，重点观察轮次边界是否还会出现重复上下电/重新起步感。
  - 若现象仍在，下一步应下沉排查 `move_rt_cartesian_path` 服务端或控制器内部是否在长路径内部仍存在模式切换。

## 2026-06-10 CST

- Objective: 在保留 v2 第二次横切调试链路的前提下，补一条临时 no-approach 入口，便于只测切豆腐而先跳过拔刀。
- Work completed:
  1. 新增 `tofu_workflow_v2_no_approach_params.yaml`，以现有 no-approach workflow 为骨架，并把第二次横切替换为 `second_cross_cut:round_2`。
  2. 新增 `tofu_skills_bringup_v2_no_approach.launch.py`，在无 `handle_approach` 的 skill 栈中显式拉起 `prepare`、`cut_round`、`second_cross_cut`、`vertical_cut` 及视觉相关节点。
  3. 新增 `tofu_workflow_execute_v2_no_approach.launch.py`，将 orchestrator 指向新的 `tofu_workflow_v2_no_approach_params.yaml`。
  4. 在根工作空间对 `cuttofo_orchestrator` 重新执行 `colcon build --paths ... --symlink-install`，让新增 launch/config 进入 root install。
  5. 完成静态验证：
     - `python3 -m py_compile` 通过
     - `ros2 launch cuttofo_orchestrator tofu_skills_bringup_v2_no_approach.launch.py --show-args` 通过
     - `ros2 launch cuttofo_orchestrator tofu_workflow_execute_v2_no_approach.launch.py --show-args` 通过
- Business logic impact:
  - 现场测试现在可以直接绕过 `handle_approach`，专注验证 `prepare -> round_1 -> second_cross_cut -> vertical_cut` 这条切豆腐链路。
  - 老的 no-approach workflow 与老的带拔刀 workflow 均未被替换，新旧入口可并行对照。
- Problems encountered:
  1. 新增 launch 文件刚写入源码时，root install 侧还不可见，第一次 `ros2 launch ... --show-args` 报 share 目录下找不到文件。
- Resolution:
  - 对 `cuttofo_orchestrator` 重新做 root workspace 的 `--symlink-install` 构建，补齐新 launch 文件在 install/share 下的可见性。
- Verification:
  - `python3 -m py_compile` 新增 v2 no-approach launch 文件通过。
  - root install 环境下 `tofu_skills_bringup_v2_no_approach.launch.py --show-args` 通过。
  - root install 环境下 `tofu_workflow_execute_v2_no_approach.launch.py --show-args` 通过。
- Unverified items:
  - `tofu_workflow_v2_no_approach` 尚未做真机端到端联调。
  - `second_cross_cut` 最小闭环的物理效果仍需继续现场验证。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_v2_no_approach_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_skills_bringup_v2_no_approach.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute_v2_no_approach.launch.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
  - `src/dexbot_middle_layer/CutTofo/启动指令.md`
- Next steps:
  - 用 `tofu_workflow_execute_v2_no_approach.launch.py` 做真机联调，优先观察第二次横切最小闭环是否连续稳定。
  - 等切豆腐链路稳定后，再把 `handle_approach` 接回 v2 调试入口。

## 2026-06-10 CST

- Objective: 在保持现有豆腐 workflow 不受影响的前提下，接入第二次横切新 skill，并新增一条专用于持续调试的新 workflow v2。
- Work completed:
  1. 将 `cuttofo_skill_tofu_second_cross_cut` 从占位包升级为正式 action server，挂载 `/tofu_second_cross_cut/execute`。
  2. 在 `tofu_second_cross_cut_workflow.py` 中实现第一版最小闭环：`cut_down -> hook_lift -> return_next_anchor`。
  3. 复用现有 `cut_round` 几何生成逻辑与当前 `debug_hook_lift` 的两阶段 RT 轨迹构造，避免重新发明第二次横切切割几何。
  4. 在 orchestrator 中新增 `second_cross_cut` skill 类型，补齐 action name 默认值、参数声明、ActionClient 注册与 profile-only goal 构造。
  5. 新增 `tofu_workflow_v2_params.yaml`，仅把标准豆腐 workflow 的第二次横切从 `cut_round:round_2` 替换成 `second_cross_cut:round_2`。
  6. 新增 `skills_bringup_v2.launch.py` 与 `tofu_workflow_execute_v2.launch.py`，让新 workflow 与老 workflow 并行存在，不污染现有启动入口。
  7. 补齐 `tofu_second_cross_cut_params.yaml` 的 workflow profile 结构，使其能直接驱动 `cut` / `hook_lift` / `motion` / `human_wait`。
  8. 将 `cuttofo_skill_tofu_second_cross_cut` 加入 `scripts/build_cuttofo.sh`，打通根工作空间完整构建链。
  9. 完成静态验证：
     - `python3 -m py_compile` 通过
     - workflow YAML 与 second_cross_cut YAML 解析通过
     - `colcon build --paths cuttofo_orchestrator cuttofu_skills/cuttofo_skill_tofu_second_cross_cut --symlink-install` 通过
     - 根工作空间 `build_cuttofo.sh` 完整构建通过
     - root install 环境下 `ros2 launch cuttofo_orchestrator skills_bringup_v2.launch.py --show-args` 通过
     - root install 环境下 `ros2 launch cuttofo_orchestrator tofu_workflow_execute_v2.launch.py --show-args` 通过
- Business logic impact:
  - 第二次横切“人工拨条”替换工作已从单脚本原子动作调试，推进到 workflow 级联调阶段。
  - 新增了一条独立的 `tofu_workflow_v2` 调试路径，可在不影响老 workflow 展示的前提下持续迭代第二次横切自动化逻辑。
- Problems encountered:
  1. 子工作空间 `CutTofo/install/setup.bash` 的 `AMENT_PREFIX_PATH` 只覆盖局部包，无法单独解析 `cuttofu_vision`、`cuttofo_skill_handle_approach` 等完整依赖链。
  2. 根工作空间 install 初始未包含本轮新增的 v2 launch 文件，因此最开始 `ros2 launch ... --show-args` 无法在完整环境下通过。
  3. 根工作空间 `colcon build --packages-select ...` 仍无法直接发现 `CutTofo` 子目录下这些包，当前可用路径仍是进入 `src/dexbot_middle_layer/CutTofo` 后用 `--paths` 显式构建。
- Resolution:
  - 先在 `CutTofo` 子工作空间内完成最小闭环实现与静态验证，保证业务逻辑和局部构建链路先成立。
  - 将 launch / workflow v2 入口并行新增，而不是改写现有标准 workflow，确保可随时回退对照。
  - 把 `cuttofo_skill_tofu_second_cross_cut` 纳入 `build_cuttofo.sh`，再回到根工作空间做完整 install 重建，补齐 root install 侧 launch 可见性。
- Verification:
  - `python3 -m py_compile` 新增 orchestrator / second_cross_cut / v2 launch 文件通过。
  - `yaml.safe_load` 成功解析 `tofu_workflow_params.yaml` 与 `tofu_workflow_v2_params.yaml`。
  - `colcon build --paths cuttofo_orchestrator cuttofu_skills/cuttofo_skill_tofu_second_cross_cut --symlink-install` 通过。
  - `ros2 launch ... --show-args` 在完整根工作空间环境下尚未通过，当前失败原因已定位为 install / 环境装配问题，而非 Python 语法或 YAML 结构问题。
- Unverified items:
  - `tofu_workflow_execute_v2.launch.py` 尚未在完整根工作空间 install 环境中成功展示参数。
  - `second_cross_cut` 最小闭环尚未做真机端到端联调。
  - `cut_down` 目前只显式下发单刀切入段，后续是否需要补充更完整的 round 内部轨迹细化仍需结合真机效果判断。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/tofu_task_orchestrator.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_runner.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_v2_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/skills_bringup_v2.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute_v2.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/**`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 在根工作空间环境下把新增 v2 launch 文件纳入 install，再复验 `ros2 launch ... --show-args`。
  - 在 `tofu_workflow_v2` 上做真机端到端联调，优先验证 `second_cross_cut` 最小闭环。
  - 根据真机效果继续补全 `transfer_to_drop_zone -> left_scrape_drop -> 双臂并行回位`。

## 2026-06-10 CST

- Objective: 为第二次横切新分支搭建独立 skill 包，并把首个原子动作 `hook_lift` 调试到可独立真机执行。
- Work completed:
  1. 新建 `cuttofo_skill_tofu_second_cross_cut` 包骨架，并注册到公共 skill 配置加载链路。
  2. 在包内落地独立调试入口 `debug_hook_lift`，用于从“已切到底”的现场姿态直接执行挑条复合动作。
  3. 修复 ROS service 调试脚本的执行模型：为节点挂载 `MultiThreadedExecutor` 并后台 spin，解决 `enable_arm(True)` 超时问题。
  4. 验证脚本控制路径为 ROS 控制节点而非本地 SDK 直连，当前通过 `/arm_r/robot/*` 服务完成使能、读位姿和 RT 笛卡尔路径执行。
  5. 将 hook-lift 姿态参数语义改为与 `prepare` 完全一致的绝对刀面倾角语义：
     - 移除 `hook_pitch_delta_deg`
     - 改为 `hook_target_plane_angle_deg`
     - 用 `build_rotation_with_edge_dir(...)` 按当前 edge_dir 重建姿态
  6. 将调试脚本全部可调参数集中到文件开头 `DEBUG_CONFIG`，便于现场直接改值。
  7. 完成首轮 dry-run 与真机执行验证，确认 waypoint 生成、日志打印与 `move_rt_cartesian_path` 执行链路均可跑通。
  8. 排查“源码已改 150 度但运行仍是 140 度”的原因，确认是普通 install 拷贝过期；已切换为 `colcon build --symlink-install` 重建。
- Business logic impact:
  - 第二次横切“人工拨条”新分支已进入原子动作实调阶段。
  - 第一块关键动作 `hook_lift` 已从概念讨论进入可独立执行状态，后续可继续在同包内追加 `transfer -> scrape -> return`。
- Problems encountered:
  1. ROS 异步 service future 无执行器处理，导致 `enable_arm(True)` 超时。
  2. 初版姿态参数使用欧拉角增量，不符合 `prepare.plane_angle_deg` 的业务语义。
  3. 普通 `colcon build` 安装副本导致 `ros2 run` 未读取最新源码参数。
- Resolution:
  - 通过后台 spin 的 `MultiThreadedExecutor` 修复 future 处理问题。
  - 用绝对 `plane_angle_deg` 语义替代欧拉角增量语义。
  - 改为 `--symlink-install`，让现场改源码参数后可直接反映到运行时。
- Verification:
  - `python3 -m compileall` / `py_compile` 多次通过。
  - `colcon list` 能识别新包。
  - `colcon build` 与后续 `colcon build --symlink-install` 均通过。
  - `debug_hook_lift --dry-run` 可打印 waypoint。
  - 真机执行返回 `hook_lift execution complete`。
- Unverified items:
  - `hook_target_plane_angle_deg=150` 在切条物理效果上是否优于 `140/145` 仍需继续真机比较。
  - base `+Y` 是否就是最优挑条主平移方向仍需结合现场效果确认。
  - `hook_waypoint_count=2` 和 `3` 的平顺性与带条稳定性仍待比较。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/config/skill_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/**`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 直接复验 `DEBUG_CONFIG["hook_target_plane_angle_deg"] = 150.0` 是否已体现在运行日志中。
  - 继续做 hook-lift 参数收敛，再进入下一原子动作。

## 2026-06-09 CST

- Objective: 重新聚焦 CutTofo 的工作目标，从“流程能跑通”推进到“尽量减少人工介入”，优先解决第二次斜切后人工拨掉豆腐条的问题。
- Work completed:
  1. 重新梳理当前豆腐 workflow 的 3 个人工介入点：第一次斜切后人工旋转案板、第二次斜切后人工拨条、竖切前再次人工旋转豆腐。
  2. 明确新的阶段目标不是单点修 bug，而是强化整个切豆腐 workflow 的端到端效果，尽量由机械臂 + 灵巧手自主完成全链路。
  3. 确定当前第一优先级是消除第 2 个介入点，即让机器人在第二次斜切后自主处理豆腐条条残料。
  4. 初步判断该任务本质更接近“接触式清料 / 拨料” manipulation 子任务，而不是沿用现有 cut_round 语义继续切刀；后续设计重点应放在顺应接触、安全拨离和不破坏已成形锯齿面。
- Business logic impact:
  - CutTofo 的优化目标从“能完成切割流程”升级为“尽量减少 operator intervention”。
  - 后续 skill 设计会围绕新的自动化缺口展开，而不是默认保留 operator wait。
- Problems encountered:
  1. 当前 operator 介入步骤虽然让主流程可运行，但它们掩盖了真实自动化瓶颈，尤其是第二次斜切后的残料处理。
  2. “拨条”步骤同时受接触几何、残料状态和主块保护约束，不能简单复用现有 prepare / cut_round 的动作假设。
- Resolution:
  - 先把“自主拨条”定义为当前阶段的主优化目标，并记录为后续 skill 设计入口。
  - 后续优先做最小真机实验，验证机械臂 + 灵巧手是否能稳定完成拨离动作，再决定放入哪个 workflow 节点。
- Verification:
  - 已与用户对齐新的端到端目标、人工介入清单和当前第一优先级。
- Unverified items:
  - 尚未确定拨条动作由哪只手执行、使用刀还是手指接触、是否需要新增视觉确认。
  - 尚未决定该步骤最终作为独立 skill 还是临时插入现有 workflow。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 定义“拨条”动作的成功标准与几何约束。
  - 调研现有执行器与 skill 是否有足够能力支撑顺应性清料动作。
  - 设计最小实验链路，优先做单阶段真机验证。


- Objective: 为 CutTofo 项目初始化 `.project-log` 工程记录。
- Work completed: 创建了完整的 `.project-log/` 目录结构和初始化文件，包括：
  - `requirements.md` — 项目目标、需求、约束
  - `business-logic/main.md` — 三条主路径（豆腐、黄瓜、抓料倒酱）
  - `business-logic/graph.md` — 节点图和映射
  - `business-logic/nodes.md` — 每个动作节点的状态定义
  - `business-logic/edges.md` — 每个执行链的详细描述
  - `business-logic/open-questions.md` — 4 个待明确问题
  - `business-logic/decision-records.md` — 4 个架构决策记录
  - `business-logic/constraints.md` — 系统、硬件、软件约束
  - `hardware/sdk-mapping.md` — 硬件和 SDK 映射
  - `config/config-schema.md` — 配置参数 schema
  - `architecture/software-architecture.md` — 系统架构概述
  - `debugging/known-issues.md` — 已知问题记录
  - `progress.md` — 初始进度记录
  - `current-session.md` — 当前会话状态
- Business logic impact: 初始化业务逻辑记录（与现有实现对齐）。
- Problems encountered: 无。
- Resolution: N/A。
- Verification: 文件已创建并通过审查。
- Unverified items: 无。
- Files changed: 全部 `.project-log/` 文件。
- Next steps: 根据用户需要继续优化工作。

## 2026-06-06 20:50 Local Time

- Objective: 深入梳理豆腐切割业务流程，重点分析视觉检测管线。
- Work completed:
  1. 完整阅读 orchestrator 工作流编排器（workflow_runner.py、tofu_workflow_params.yaml）
  2. 完整阅读 prepare 技能（tofu_prepare_workflow.py、tofu_prepare_node.py、tofu_prepare_params.yaml）
  3. 完整阅读 cut_round 技能（tofu_cut_round_workflow.py、tofu_cut_round_node.py、tofu_cut_round_params.yaml）
  4. 完整阅读视觉管线（pose_estimator_node.py、vision_params.yaml、vision_bringup.launch.py）
  5. 完整阅读视觉跟踪器（vision_geometry_tracker.py、prepare_vision_state.py）
  6. 完整阅读几何计算（tofu_geometry.py、cut_round_path.py）
  7. 深入分析 PCA OBB 核心算法（vision_utils.py 中 get_pose_from_mask）
  8. 深入分析 `corner_mode: aabb` 导致的顶面角点丢失旋转信息问题
- Business logic impact: 无（仅在代码阅读分析层面）。
- Problems encountered:
  - 当前 `corner_mode: aabb`（vision_params.yaml）导致 geometric_features[8:19] 中的顶面角点是 Base 系轴对齐矩形，不包含豆腐旋转信息。
  - 结果是 `compute_edge_dir()` 始终回退到 `[1,0,0]`（base_X），`edge_align: true` 无法真正对齐棱边。
- Resolution: 待后续讨论优化方案。
- Verification: 代码逻辑追踪确认，与 `vision_params.yaml` 配置一致。
- Unverified items: 无。
- Files changed: 无代码改动。
- Next steps: 与用户讨论视觉检测管线优化方向（aabb → pca_constrained 或其他方案）。

## 2026-06-06 21:30 Local Time

- Objective: 修复 workspace 中所有老旧硬编码路径，完成完整编译验证。
- Work completed:
  1. 清理 workspace 所有编译产物（src/build/, src/install/, src/log/）

- Objective: 在保留 v2 第二次横切调试链路的前提下，补一条临时 no-approach 入口，便于只测切豆腐而先跳过拔刀。
- Work completed:
  1. 新增 `tofu_workflow_v2_no_approach_params.yaml`，以现有 no-approach workflow 为骨架，并把第二次横切替换为 `second_cross_cut:round_2`。
  2. 新增 `tofu_skills_bringup_v2_no_approach.launch.py`，在无 `handle_approach` 的 skill 栈中显式拉起 `prepare`、`cut_round`、`second_cross_cut`、`vertical_cut` 及视觉相关节点。
  3. 新增 `tofu_workflow_execute_v2_no_approach.launch.py`，将 orchestrator 指向新的 `tofu_workflow_v2_no_approach_params.yaml`。
  4. 在根工作空间对 `cuttofo_orchestrator` 重新执行 `colcon build --paths ... --symlink-install`，让新增 launch/config 进入 root install。
  5. 完成静态验证：
     - `python3 -m py_compile` 通过
     - `ros2 launch cuttofo_orchestrator tofu_skills_bringup_v2_no_approach.launch.py --show-args` 通过
     - `ros2 launch cuttofo_orchestrator tofu_workflow_execute_v2_no_approach.launch.py --show-args` 通过
- Business logic impact:
  - 现场测试现在可以直接绕过 `handle_approach`，专注验证 `prepare -> round_1 -> second_cross_cut -> vertical_cut` 这条切豆腐链路。
  - 老的 no-approach workflow 与老的带拔刀 workflow 均未被替换，新旧入口可并行对照。
- Problems encountered:
  1. 新增 launch 文件刚写入源码时，root install 侧还不可见，第一次 `ros2 launch ... --show-args` 报 share 目录下找不到文件。
- Resolution:
  - 对 `cuttofo_orchestrator` 重新做 root workspace 的 `--symlink-install` 构建，补齐新 launch 文件在 install/share 下的可见性。
- Verification:
  - `python3 -m py_compile` 新增 v2 no-approach launch 文件通过。
  - root install 环境下 `tofu_skills_bringup_v2_no_approach.launch.py --show-args` 通过。
  - root install 环境下 `tofu_workflow_execute_v2_no_approach.launch.py --show-args` 通过。
- Unverified items:
  - `tofu_workflow_v2_no_approach` 尚未做真机端到端联调。
  - `second_cross_cut` 最小闭环的物理效果仍需继续现场验证。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_v2_no_approach_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_skills_bringup_v2_no_approach.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute_v2_no_approach.launch.py`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
  - `src/dexbot_middle_layer/CutTofo/启动指令.md`
- Next steps:
  - 用 `tofu_workflow_execute_v2_no_approach.launch.py` 做真机联调，优先观察第二次横切最小闭环是否连续稳定。
  - 等切豆腐链路稳定后，再把 `handle_approach` 接回 v2 调试入口。

## 2026-06-10 CST

- Objective: 在保持现有豆腐 workflow 不受影响的前提下，接入第二次横切新 skill，并新增一条专用于持续调试的新 workflow v2。
- Work completed:
  1. 将 `cuttofo_skill_tofu_second_cross_cut` 从占位包升级为正式 action server，挂载 `/tofu_second_cross_cut/execute`。
  2. 在 `tofu_second_cross_cut_workflow.py` 中实现第一版最小闭环：`cut_down -> hook_lift -> return_next_anchor`。
  3. 复用现有 `cut_round` 几何生成逻辑与当前 `debug_hook_lift` 的两阶段 RT 轨迹构造，避免重新发明第二次横切切割几何。
  4. 在 orchestrator 中新增 `second_cross_cut` skill 类型，补齐 action name 默认值、参数声明、ActionClient 注册与 profile-only goal 构造。
  5. 新增 `tofu_workflow_v2_params.yaml`，仅把标准豆腐 workflow 的第二次横切从 `cut_round:round_2` 替换成 `second_cross_cut:round_2`。
  6. 新增 `skills_bringup_v2.launch.py` 与 `tofu_workflow_execute_v2.launch.py`，让新 workflow 与老 workflow 并行存在，不污染现有启动入口。
  7. 补齐 `tofu_second_cross_cut_params.yaml` 的 workflow profile 结构，使其能直接驱动 `cut` / `hook_lift` / `motion` / `human_wait`。
  8. 将 `cuttofo_skill_tofu_second_cross_cut` 加入 `scripts/build_cuttofo.sh`，打通根工作空间完整构建链。
  9. 完成静态验证：
     - `python3 -m py_compile` 通过
     - workflow YAML 与 second_cross_cut YAML 解析通过
     - `colcon build --paths cuttofo_orchestrator cuttofu_skills/cuttofo_skill_tofu_second_cross_cut --symlink-install` 通过
     - 根工作空间 `build_cuttofo.sh` 完整构建通过
     - root install 环境下 `ros2 launch cuttofo_orchestrator skills_bringup_v2.launch.py --show-args` 通过
     - root install 环境下 `ros2 launch cuttofo_orchestrator tofu_workflow_execute_v2.launch.py --show-args` 通过
- Business logic impact:
  - 第二次横切“人工拨条”替换工作已从单脚本原子动作调试，推进到 workflow 级联调阶段。
  - 新增了一条独立的 `tofu_workflow_v2` 调试路径，可在不影响老 workflow 展示的前提下持续迭代第二次横切自动化逻辑。
- Problems encountered:
  1. 子工作空间 `CutTofo/install/setup.bash` 的 `AMENT_PREFIX_PATH` 只覆盖局部包，无法单独解析 `cuttofu_vision`、`cuttofo_skill_handle_approach` 等完整依赖链。
  2. 根工作空间 install 初始未包含本轮新增的 v2 launch 文件，因此最开始 `ros2 launch ... --show-args` 无法在完整环境下通过。
  3. 根工作空间 `colcon build --packages-select ...` 仍无法直接发现 `CutTofo` 子目录下这些包，当前可用路径仍是进入 `src/dexbot_middle_layer/CutTofo` 后用 `--paths` 显式构建。
- Resolution:
  - 先在 `CutTofo` 子工作空间内完成最小闭环实现与静态验证，保证业务逻辑和局部构建链路先成立。
  - 将 launch / workflow v2 入口并行新增，而不是改写现有标准 workflow，确保可随时回退对照。
  - 把 `cuttofo_skill_tofu_second_cross_cut` 纳入 `build_cuttofo.sh`，再回到根工作空间做完整 install 重建，补齐 root install 侧 launch 可见性。
- Verification:
  - `python3 -m py_compile` 新增 orchestrator / second_cross_cut / v2 launch 文件通过。
  - `yaml.safe_load` 成功解析 `tofu_workflow_params.yaml` 与 `tofu_workflow_v2_params.yaml`。
  - `colcon build --paths cuttofo_orchestrator cuttofu_skills/cuttofo_skill_tofu_second_cross_cut --symlink-install` 通过。
  - `ros2 launch ... --show-args` 在完整根工作空间环境下尚未通过，当前失败原因已定位为 install / 环境装配问题，而非 Python 语法或 YAML 结构问题。
- Unverified items:
  - `tofu_workflow_execute_v2.launch.py` 尚未在完整根工作空间 install 环境中成功展示参数。
  - `second_cross_cut` 最小闭环尚未做真机端到端联调。
  - `cut_down` 目前只显式下发单刀切入段，后续是否需要补充更完整的 round 内部轨迹细化仍需结合真机效果判断。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/tofu_task_orchestrator.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_runner.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_v2_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/skills_bringup_v2.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute_v2.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/**`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 在根工作空间环境下把新增 v2 launch 文件纳入 install，再复验 `ros2 launch ... --show-args`。
  - 在 `tofu_workflow_v2` 上做真机端到端联调，优先验证 `second_cross_cut` 最小闭环。
  - 根据真机效果继续补全 `transfer_to_drop_zone -> left_scrape_drop -> 双臂并行回位`。

## 2026-06-10 CST

- Objective: 为第二次横切新分支搭建独立 skill 包，并把首个原子动作 `hook_lift` 调试到可独立真机执行。
- Work completed:
  1. 新建 `cuttofo_skill_tofu_second_cross_cut` 包骨架，并注册到公共 skill 配置加载链路。
  2. 在包内落地独立调试入口 `debug_hook_lift`，用于从“已切到底”的现场姿态直接执行挑条复合动作。
  3. 修复 ROS service 调试脚本的执行模型：为节点挂载 `MultiThreadedExecutor` 并后台 spin，解决 `enable_arm(True)` 超时问题。
  4. 验证脚本控制路径为 ROS 控制节点而非本地 SDK 直连，当前通过 `/arm_r/robot/*` 服务完成使能、读位姿和 RT 笛卡尔路径执行。
  5. 将 hook-lift 姿态参数语义改为与 `prepare` 完全一致的绝对刀面倾角语义：
     - 移除 `hook_pitch_delta_deg`
     - 改为 `hook_target_plane_angle_deg`
     - 用 `build_rotation_with_edge_dir(...)` 按当前 edge_dir 重建姿态
  6. 将调试脚本全部可调参数集中到文件开头 `DEBUG_CONFIG`，便于现场直接改值。
  7. 完成首轮 dry-run 与真机执行验证，确认 waypoint 生成、日志打印与 `move_rt_cartesian_path` 执行链路均可跑通。
  8. 排查“源码已改 150 度但运行仍是 140 度”的原因，确认是普通 install 拷贝过期；已切换为 `colcon build --symlink-install` 重建。
- Business logic impact:
  - 第二次横切“人工拨条”新分支已进入原子动作实调阶段。
  - 第一块关键动作 `hook_lift` 已从概念讨论进入可独立执行状态，后续可继续在同包内追加 `transfer -> scrape -> return`。
- Problems encountered:
  1. ROS 异步 service future 无执行器处理，导致 `enable_arm(True)` 超时。
  2. 初版姿态参数使用欧拉角增量，不符合 `prepare.plane_angle_deg` 的业务语义。
  3. 普通 `colcon build` 安装副本导致 `ros2 run` 未读取最新源码参数。
- Resolution:
  - 通过后台 spin 的 `MultiThreadedExecutor` 修复 future 处理问题。
  - 用绝对 `plane_angle_deg` 语义替代欧拉角增量语义。
  - 改为 `--symlink-install`，让现场改源码参数后可直接反映到运行时。
- Verification:
  - `python3 -m compileall` / `py_compile` 多次通过。
  - `colcon list` 能识别新包。
  - `colcon build` 与后续 `colcon build --symlink-install` 均通过。
  - `debug_hook_lift --dry-run` 可打印 waypoint。
  - 真机执行返回 `hook_lift execution complete`。
- Unverified items:
  - `hook_target_plane_angle_deg=150` 在切条物理效果上是否优于 `140/145` 仍需继续真机比较。
  - base `+Y` 是否就是最优挑条主平移方向仍需结合现场效果确认。
  - `hook_waypoint_count=2` 和 `3` 的平顺性与带条稳定性仍待比较。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/config/skill_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/**`
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 直接复验 `DEBUG_CONFIG["hook_target_plane_angle_deg"] = 150.0` 是否已体现在运行日志中。
  - 继续做 hook-lift 参数收敛，再进入下一原子动作。

## 2026-06-09 CST

- Objective: 重新聚焦 CutTofo 的工作目标，从“流程能跑通”推进到“尽量减少人工介入”，优先解决第二次斜切后人工拨掉豆腐条的问题。
- Work completed:
  1. 重新梳理当前豆腐 workflow 的 3 个人工介入点：第一次斜切后人工旋转案板、第二次斜切后人工拨条、竖切前再次人工旋转豆腐。
  2. 明确新的阶段目标不是单点修 bug，而是强化整个切豆腐 workflow 的端到端效果，尽量由机械臂 + 灵巧手自主完成全链路。
  3. 确定当前第一优先级是消除第 2 个介入点，即让机器人在第二次斜切后自主处理豆腐条条残料。
  4. 初步判断该任务本质更接近“接触式清料 / 拨料” manipulation 子任务，而不是沿用现有 cut_round 语义继续切刀；后续设计重点应放在顺应接触、安全拨离和不破坏已成形锯齿面。
- Business logic impact:
  - CutTofo 的优化目标从“能完成切割流程”升级为“尽量减少 operator intervention”。
  - 后续 skill 设计会围绕新的自动化缺口展开，而不是默认保留 operator wait。
- Problems encountered:
  1. 当前 operator 介入步骤虽然让主流程可运行，但它们掩盖了真实自动化瓶颈，尤其是第二次斜切后的残料处理。
  2. “拨条”步骤同时受接触几何、残料状态和主块保护约束，不能简单复用现有 prepare / cut_round 的动作假设。
- Resolution:
  - 先把“自主拨条”定义为当前阶段的主优化目标，并记录为后续 skill 设计入口。
  - 后续优先做最小真机实验，验证机械臂 + 灵巧手是否能稳定完成拨离动作，再决定放入哪个 workflow 节点。
- Verification:
  - 已与用户对齐新的端到端目标、人工介入清单和当前第一优先级。
- Unverified items:
  - 尚未确定拨条动作由哪只手执行、使用刀还是手指接触、是否需要新增视觉确认。
  - 尚未决定该步骤最终作为独立 skill 还是临时插入现有 workflow。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/.project-log/current-session.md`
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`
- Next steps:
  - 定义“拨条”动作的成功标准与几何约束。
  - 调研现有执行器与 skill 是否有足够能力支撑顺应性清料动作。
  - 设计最小实验链路，优先做单阶段真机验证。


- Objective: 为 CutTofo 项目初始化 `.project-log` 工程记录。
- Work completed: 创建了完整的 `.project-log/` 目录结构和初始化文件，包括：
  - `requirements.md` — 项目目标、需求、约束
  - `business-logic/main.md` — 三条主路径（豆腐、黄瓜、抓料倒酱）
  - `business-logic/graph.md` — 节点图和映射
  - `business-logic/nodes.md` — 每个动作节点的状态定义
  - `business-logic/edges.md` — 每个执行链的详细描述
  - `business-logic/open-questions.md` — 4 个待明确问题
  - `business-logic/decision-records.md` — 4 个架构决策记录
  - `business-logic/constraints.md` — 系统、硬件、软件约束
  - `hardware/sdk-mapping.md` — 硬件和 SDK 映射
  - `config/config-schema.md` — 配置参数 schema
  - `architecture/software-architecture.md` — 系统架构概述
  - `debugging/known-issues.md` — 已知问题记录
  - `progress.md` — 初始进度记录
  - `current-session.md` — 当前会话状态
- Business logic impact: 初始化业务逻辑记录（与现有实现对齐）。
- Problems encountered: 无。
- Resolution: N/A。
- Verification: 文件已创建并通过审查。
- Unverified items: 无。
- Files changed: 全部 `.project-log/` 文件。
- Next steps: 根据用户需要继续优化工作。

## 2026-06-06 20:50 Local Time

- Objective: 深入梳理豆腐切割业务流程，重点分析视觉检测管线。
- Work completed:
  1. 完整阅读 orchestrator 工作流编排器（workflow_runner.py、tofu_workflow_params.yaml）
  2. 完整阅读 prepare 技能（tofu_prepare_workflow.py、tofu_prepare_node.py、tofu_prepare_params.yaml）
  3. 完整阅读 cut_round 技能（tofu_cut_round_workflow.py、tofu_cut_round_node.py、tofu_cut_round_params.yaml）
  4. 完整阅读视觉管线（pose_estimator_node.py、vision_params.yaml、vision_bringup.launch.py）
  5. 完整阅读视觉跟踪器（vision_geometry_tracker.py、prepare_vision_state.py）
  6. 完整阅读几何计算（tofu_geometry.py、cut_round_path.py）
  7. 深入分析 PCA OBB 核心算法（vision_utils.py 中 get_pose_from_mask）
  8. 深入分析 `corner_mode: aabb` 导致的顶面角点丢失旋转信息问题
- Business logic impact: 无（仅在代码阅读分析层面）。
- Problems encountered:
  - 当前 `corner_mode: aabb`（vision_params.yaml）导致 geometric_features[8:19] 中的顶面角点是 Base 系轴对齐矩形，不包含豆腐旋转信息。
  - 结果是 `compute_edge_dir()` 始终回退到 `[1,0,0]`（base_X），`edge_align: true` 无法真正对齐棱边。
- Resolution: 待后续讨论优化方案。
- Verification: 代码逻辑追踪确认，与 `vision_params.yaml` 配置一致。
- Unverified items: 无。
- Files changed: 无代码改动。
- Next steps: 与用户讨论视觉检测管线优化方向（aabb → pca_constrained 或其他方案）。

## 2026-06-06 21:30 Local Time

- Objective: 修复 workspace 中所有老旧硬编码路径，完成完整编译验证。
- Work completed:
  1. 清理 workspace 所有编译产物（src/build/, src/install/, src/log/）
  2. 完整编译全部 26 个 ROS 包
  3. 全量扫描并修复 30+ 处老旧硬编码路径，涉及：
     - `dexbot_ros2_ws_525`（已删除的旧版）→ 当前 workspace
     - `/home/kim/projects/...`（另一开发者）→ 动态 `find_ws_root()` 或 `os.path.expanduser`
     - `/home/a/Desktop/...` 和 `/home/a/projects/...`（另一开发者）→ 同上
     - SAM3 模型路径 `/home/a/models/sam3` → `/home/tbl/Project/models/sam3`
     - `AR5_dual_scene.xml` 中 16 处硬编码 mesh 路径 → `package://` URI
  4. 修复 README.md / README_CUTTOFU.md / GUI/README.md / cuttofo_graph_check.sh
  5. 修复 `.bashrc` 中旧的 ros workspace source 路径
  6. 修复后完整编译验证通过（26 包，0 错误）
- Business logic impact: 无。
- Problems encountered:
  1. 路径来源复杂：涉及 3 个不同开发者的机器路径和被删除的 `_525` 旧版本
  2. 部分 Python 代码中有 `os.path.expanduser("/home/kim/...")` 形式硬编码，转换为相对路径或 `find_ws_root()` 动态查找
- Resolution: 采用 `find_ws_root()` 动态发现 + `os.path.expanduser("~/Project/cucumber/...")` 统一路径。
- Verification: 完整编译 26 包通过，grep 确认无残留老旧路径。
- Unverified items: 无。
- Files changed: 涉及 dexbot_bottom_layer、dexbot_bringup、dexbot_middle_layer、dexbot_toolbox、cuttofo_xcore、CutTofo 内多个子包，共 20+ 文件。
- Next steps: 等待用户确定下一步优化方向（视觉检测管线优化等）。

## 2026-06-06 23:45 Local Time

- Objective: 真机测试 constrained_obb 视觉管线，排查 SAM3 检测问题。
- Work completed:
  1. 配置 `corner_mode: constrained_obb` 并启动完整视觉管线（RealSense + SAM3 + pose_estimator + camera_viewer）
  2. 排查 SAM3 零检测问题，定位两个根本原因：
     - **QoS 不匹配**：SAM3 用 BEST_EFFORT 订阅 RealSense RGB（实际发布 RELIABLE），DDS 不兼容导致 image_callback 永不触发
     - **代码架构缺陷**：新版 SAM3 节点通过 `camera_backend` 自动检测 + `_setup_color_image_subscription()` 多层间接创建订阅，旧版直接 `create_subscription(Image, topic, cb, 10)` 简单可靠
  3. 修复方案：YAML 显式设置 `image_topic` 跳过自动检测，QoS 改为 RELIABLE
  4. 同学工程 `dexbot_ros2_ws-cut_to_fo_featrue` 复现了完全相同的问题，确认是 skills 架构迁移（commit `951221a6`）时引入的代码问题，非个别环境问题
  5. 完整编译 26 包验证修复
- Business logic impact: 视觉管线 `corner_mode: constrained_obb` 已可用。
- Problems encountered:
  1. SAM3 模型启动后完全不产生检测（话题存在但无消息）
  2. 根因诊断耗时较长（QoS 修改、调试日志插入、对比旧代码）
  3. 同学代码中存在同样问题（git blame 确认来自 commit `951221a6`）
- Resolution:
  - `sam3_detector_node.py`：图像订阅从 `qos_profile_sensor_data`（BEST_EFFORT）改为 RELIABLE QoS
  - `vision_params.yaml`：增加 `image_topic: /camera/camera/color/image_raw` 绕过自动检测分支
- Verification: 重启后确认图像回调触发，SAM3 正常检测。
- Files changed: `sam3_detector_node.py`（QoS）、`vision_params.yaml`（image_topic）
- Next steps: 验证 constrained_obb 顶面角点输出是否包含旋转信息。


## 2026-06-07 02:10 Local Time

- Objective: 创建可视化节点包 cuttofo_skill_visualizer。
- Work completed:
  1. 包目录结构搭建完成
  2. 28 个网格文件已复制（arm_r:8 + arm_l:8 + hand:12）
  3. package.xml / CMakeLists.txt / setup.py / setup.cfg 已完成
  4. 双臂 xacro 已创建（mesh 路径改为自引用 package://cuttofo_skill_visualizer）
  5. hand xacro 已创建（同样自引用 mesh 路径）
  6. viz_hand_joint_bridge.py 已完成（关节名重映射+虚拟手合成）
  7. task_visualizer_node.py 已完成约 70%（一半代码写入，_callback 方法待写入）
- Business logic impact: 无。
- Problems encountered:
  1. Haiku 4.5 工具调用问题持续——Bash/Write/Edit 频繁出现空参数调用，导致写入中断
  2. task_visualizer_node.py 的 _callback 方法和 main() 函数已写到聊天中但未写入文件
  3. 剩余文件未创建：viz_hand_joint_bridge.py、launch、rviz、config
- Resolution: 暂停任务等待工具调用问题修复后继续。
- Verification: N/A。
- Next steps: 解决工具调用问题后继续完成可视化包剩余文件。

## 2026-06-06 16:04 CST

- Objective: 在现有 CutTofo skills 结构下落地新的自足可视化包，并完成构建接入与 live 联调。
- Work completed:
  1. 新增 `cuttofo_skill_scene_visualization` 包，目录位于 `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_scene_visualization`
  2. 完成包骨架与元数据：`package.xml`、`setup.py`、`setup.cfg`、`resource/`、`config/`、`launch/`、`rviz/`、Python package
  3. 迁移并适配旧 `cuttofo_xcore` 可视化代码：`scene_visualization_node.py`、`viz_hand_joint_bridge.py`、`tofu_geometry.py`
  4. 新增配置与 launch 组装逻辑：`scene_visualization_config.py`、`display_launch_helpers.py`、`scene_visualization_node.launch.py`、`scene_visualization_display.launch.py`
  5. vendoring 双臂 AR5 模型、LinkerHand O6 模型、meshes、RViz 配置到新包 `description/` / `rviz/` 下，并把活动资源的 `package://` 路径改为新包自引用
  6. 将新包接入 `CutTofo/scripts/build_skills.sh` 与 `CutTofo/scripts/build_cuttofo.sh` 的显式 `--paths` 构建链
  7. 清理 vendored `.bak` 备份文件，并修复因 setuptools 缓存 `SOURCES.txt` 导致的重建失败
  8. live 联调完成：
     - 使用现场已有 `/cuttofu/perception/objects_with_pose`、相机话题、双臂 joint states
     - 启动 `cuttofo_xcore tofu_state_node` 并 remap 到 `/cuttofu/perception/objects_with_pose`
     - 启动 `cuttofo_skill_scene_visualization scene_visualization_node`
     - 确认 `/tofu_state` 正常发布，`health_state=tracking`
     - 确认 `/tofu_visualization` 正常发布，类型为 `visualization_msgs/msg/MarkerArray`
- Business logic impact: 新增一个纯消费型可视化技能包，不改变现有豆腐/黄瓜/抓料主业务逻辑，仅新增观测与调试能力。
- Problems encountered:
  1. 新包未被 `colcon list` 自动发现，原因是当前 CutTofo skills 依赖 `build_skills.sh` / `build_cuttofo.sh` 的 `--paths` 显式构建机制
  2. vendored `xacro:include` 在批量替换时被写坏，导致 full display launch 初次启动失败
  3. 删除 `.bak` 后首次重建失败，原因是 build 目录里缓存了旧 `SOURCES.txt`
  4. live 抓取 `/tofu_visualization --once` 时拿到过 `DELETEALL` 清空帧，说明启动/丢失状态下有清理逻辑，尚未直接在 RViz 中确认持续 marker 表现
- Resolution:
  - 将新包显式加入两个构建脚本
  - 手工修正 `AR5_dual_W4C1C1.urdf.xacro` 中的 hand include 路径
  - 清理 `build/cuttofo_skill_scene_visualization` 与对应 install 缓存后重建
  - 完成 live 话题级验证，确认 `/tofu_state` 与 `/tofu_visualization` 链路打通
- Verification:
  - `bash src/dexbot_middle_layer/CutTofo/scripts/build_skills.sh --packages-select cuttofo_skill_scene_visualization`
  - `ros2 pkg executables cuttofo_skill_scene_visualization`
  - `ros2 launch cuttofo_skill_scene_visualization scene_visualization_node.launch.py -s`
  - `ros2 launch cuttofo_skill_scene_visualization scene_visualization_display.launch.py -s`
  - `timeout 12s ros2 launch cuttofo_skill_scene_visualization scene_visualization_display.launch.py enable_realsense:=false`
  - `ros2 topic echo /tofu_state --once`
  - `ros2 topic info /tofu_visualization`
- Unverified items:
  - 尚未在 RViz 中人工确认 marker 是否持续稳定显示
  - 尚未完成机器人模型、点云、marker 的空间对齐检查
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_scene_visualization/**`
  - `src/dexbot_middle_layer/CutTofo/scripts/build_skills.sh`
  - `src/dexbot_middle_layer/CutTofo/scripts/build_cuttofo.sh`
- Next steps:
  - 使用“视觉检测管线 + tofu_state_node + scene_visualization_display.launch.py”进行 RViz 真机观察
  - 确认 marker 持续显示是否正常
  - 联调机器人模型、点云、marker 的空间对齐，并针对 calibration / TF / mount pose 做优化

## 2026-06-07 19:56 CST

- Objective: 修复直接启动 `src/gui/main.py` 时的 GUI/ROS2 环境与控制链路问题，恢复 Tkinter GUI 对双臂控制服务的可用性。
- Work completed:
  1. 在 `src/gui/main.py` 的启动引导中补充 `src/dexbot_toolbox` 源码路径，解决 direct run GUI 时 `No module named 'dexbot_toolbox.gui'`。
  2. 修复 `src/dexbot_bottom_layer/dexbot_bottom_layer/xcore_controller_node.py` 中 `RcutilsLogger` 的错误调用方式，把 logging 风格的多参数 `info/warning` 改成单字符串 `f-string`，消除 `RcutilsLogger.info() takes 2 positional arguments but 4 were given`。
  3. 重新构建 `dexbot_bottom_layer`，并确认 `ros2 launch dexbot_bringup dual_xcore_controllers.launch.py` 使用的是 `install/` 中更新后的代码，而非 `src/` 旧副本。
  4. 在 `src/gui/main.py` 中补充对 `install/*/lib/python3.10/site-packages` 与 `install/*/local/lib/python3.10/dist-packages` 的 Python 路径注入，解决 GUI 直接启动时 `No module named 'dexbot_interfaces_low'`。
  5. 继续定位后确认仅补 `sys.path` 不足以支持 `rclpy.create_client()`，因为 ROS2 typesupport 动态库仍依赖完整 runtime 环境；已复现并确认错误为 `Could not load library libdexbot_interfaces_low__rosidl_typesupport_fastrtps_c.so`。
  6. 将 `src/gui/main.py` 改为环境自举入口：若当前进程未带完整工作空间环境，则自动 `source install/setup.bash`，继承补齐后的 `PYTHONPATH` / `AMENT_PREFIX_PATH` / `LD_LIBRARY_PATH` 并 `exec` 自身，避免用户必须手工 source 后再启 GUI。
  7. 用独立 Python 探针验证了问题分层：在完整 `source install/setup.bash` 环境中可成功 `create_client(MoveJoints, ...)`，而仅靠 GUI 手动补 `sys.path` 时会稳定复现 typesupport 动态库加载失败。
- Business logic impact: 无主业务逻辑变更；本轮修改属于 GUI 启动与 ROS2 runtime 集成修复，不改变豆腐主流程或控制语义。
- Problems encountered:
  1. `src/gui/main.py` 直接启动时依次暴露出三层环境问题：缺少 `dexbot_toolbox` 源码路径、缺少 `dexbot_interfaces_low` Python 包路径、缺少 ROS2 typesupport 动态库运行时路径。
  2. `dexbot_bottom_layer` 的 logger 修复首次只改了 `src/`，未重建 `install/`，导致用户重新 source 后仍命中旧代码。
  3. GUI 运行期间持续出现 `Publisher already registered for provided node name`，说明 `RosServiceBridge`/`rclpy.Node` 可能被重复创建；该问题与 typesupport 失败是独立问题。
- Resolution:
  - 逐层补齐 GUI 的源码路径、install Python 包路径与运行时环境自举逻辑。
  - 对 `dexbot_bottom_layer` 重新构建，确保 launch 链路使用已修复的安装产物。
  - 将重复 node 名告警记录为后续待处理项，暂不与当前主故障混淆。
- Verification:
  - `python3 -m py_compile src/gui/main.py` 通过。
  - `python3 -m py_compile src/dexbot_bottom_layer/dexbot_bottom_layer/xcore_controller_node.py` 通过。
  - `colcon build --packages-select dexbot_bottom_layer` 通过。
  - 已用最小探针验证：在完整 sourced shell 中 `Node(...).create_client(MoveJoints, ...)` 成功；未 sourced 但只靠旧 bootstrap 的场景下可稳定复现 typesupport 动态库缺失。
  - 尚未完成用户侧完整重启 GUI 进程后的端到端 service 调用复验。
- Unverified items:
  - 需要用户完整重启 GUI 进程后确认 `arm_execute` / `refresh_state` 是否已恢复正常。
  - `Publisher already registered for provided node name` 的重复 node 创建问题尚未修复。
- Files changed:
  - `src/gui/main.py`
  - `src/dexbot_bottom_layer/dexbot_bottom_layer/xcore_controller_node.py`
- Next steps:
  - 让用户在控制器节点已启动的前提下重新完整启动 GUI，验证 `MoveJoints` / `GetRobotState` client 是否恢复。
  - 若主链路恢复，则继续排查 `RosServiceBridge` 的重复创建与 node name 冲突，消除 rosout 重复 publisher 告警。

## 2026-06-07 16:40 CST

- Objective: 修复豆腐横切结束后的回撤链路，恢复 legacy 的“先清刀再回 wait/prepare”行为。
- Work completed:
  1. 对照 legacy `cuttofo_xcore` 的 `knife_cut_action_server._return_to_prepare_waypoints()`，确认当前 CutTofo 已有等价的 inverse-step 回撤几何。
  2. 将 `tofu_cut_round_params.yaml` 中 `round_1.return.skip_return_anchor` 与 `round_2.return.skip_return_anchor` 改为 `false`，恢复切后 cartesian return。
  3. 在 `cut_round_path.py` 中抽出 `return_to_prepare_offsets()`，让回撤偏移可直接复用并用于诊断。
  4. 在 `tofu_cut_round_workflow.py` 中补充 return 分支日志，打印 cut end pose、offset、extra offset、return target，便于现场判断是否先清刀后再 MoveJ。
  5. 完成 `cuttofo_skill_common` 与 `cuttofo_skill_tofu_cut_round` 定向构建验证。
- Business logic impact:
  - 豆腐横切第 1/2 轮结束后的控制顺序恢复为：切完停左侧末端 -> 先按 inverse-step + extra offset 做右移清刀 -> 再 MoveJ 到 wait pose -> 后续由下一次 prepare 回到 prepare 位。
- Problems encountered:
  1. 当前配置曾因 `setFcCoor(world)` 网络错误把 `skip_return_anchor` 临时设为 `true`，导致整段安全回撤被跳过。
  2. 现场仅凭机械臂运动观察，很难区分“直接回 wait”还是“先做过短回撤再回 wait”。
- Resolution:
  - 恢复 return 分支并补足日志可观测性；若后续 RT return 再触发同类网络错误，后手方案是切换到已有 `use_nrt_cartesian`，而不是再次跳过回撤。
- Verification:
  - `python3 -m py_compile` 覆盖相关 Python 文件通过。
  - `colcon build --base-paths ... --packages-select cuttofo_skill_common cuttofo_skill_tofu_cut_round --symlink-install` 通过。
- Unverified items:
  - 尚未完成真机验证，仍需确认 RT cartesian return 在现场是否稳定。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_cut_round/config/tofu_cut_round_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/trajectory/cut_round_path.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_cut_round/cuttofo_skill_tofu_cut_round/tofu_cut_round_workflow.py`
- Next steps:
  - 真机单阶段执行 `prepare:first_cut -> cut_round:round_1`，确认先右移清刀再回 wait pose。
  - 若 RT return 失败，切到 `return.use_nrt_cartesian: true` 继续验证，而不是回退到 `skip_return_anchor: true`。

## 2026-06-07 17:10 CST

- Objective: 将豆腐阶段 7 竖切逻辑完整迁移到当前 CutTofo vertical-cut skill，对齐 legacy `phase7_third_cut`。
- Work completed:
  1. 梳理 current orchestrator -> `/tofu_vertical_cut/execute` -> `tofu_vertical_cut_workflow.execute_vertical_cut()` 的调用链，确认无需改 action 契约与阶段编排。
  2. 对照 legacy `knife_cut_action_server._execute_phase7_cut()`，将当前 vertical-cut workflow 收紧为四段：`seg1 upper cuts -> mid_push -> seg2 lower cuts + last retract -> tail_push`。
  3. 保留 `build_vertical_cut_waypoints()` 负责基础 `cut -> retract -> next_anchor` 骨架，把中段推刀与尾推继续留在 workflow 层显式下发 RT motion。
  4. 将默认 profile 参数切回 legacy phase7 语义：`force_rt_position: true`、`cycles: 11`、`cut_move: 0.058`、`step_z: -0.005`、`push_lift_speed`、`mid_push_speed`、`push_tail_speed`、`tail_move_cut_speed` 等。
  5. 在 workflow 中补充阶段日志，方便现场区分 seg1 / mid_push / seg2 / tail_push 的执行进度。
  6. 完成 `cuttofo_skill_tofu_vertical_cut` 定向语法检查与构建验证。
- Business logic impact:
  - 豆腐阶段 7 竖切不再维护一套“近似 phase7”的新逻辑，而是正式回到 legacy 语义：上半段竖切、中段推刀、下半段竖切+末次 retract、尾推，且默认全程走 RT Cartesian position 模式。
- Problems encountered:
  1. 当前 vertical-cut 配置字段名与 legacy 存在漂移，容易造成现场调参时“名字相近但语义不一致”。
  2. 原 workflow 的中段/尾推拆分方式与 legacy 不完全一致，存在维护第二套 phase7 语义的风险。
- Resolution:
  - 收紧 workflow 段落顺序并统一默认配置命名/数值，直接以 legacy phase7 为准。
- Verification:
  - `python3 -m py_compile` 检查 `tofu_vertical_cut_workflow.py`、`tofu_vertical_cut_config.py`、`tofu_vertical_cut_node.py` 通过。
  - `colcon build --base-paths ... --packages-select cuttofo_skill_tofu_vertical_cut --symlink-install` 通过。
- Unverified items:
  - 尚未做真机竖切验证，仍需确认 mid push 与 tail push 的现场效果与 legacy 一致。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_vertical_cut/cuttofo_skill_tofu_vertical_cut/tofu_vertical_cut_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_vertical_cut/config/tofu_vertical_cut_params.yaml`
- Next steps:
  - 真机手动执行 `prepare:after_rotation_1 -> vertical_cut:default`，确认阶段 7 的四段动作与 legacy 一致。
  - 若现场仍出现 phase7 行为偏差，优先比较 legacy `_execute_phase7_cut()` 的段落顺序与当前参数，而不是先改 orchestrator。

## 2026-06-07 17:35 CST

- Objective: 迁移 phase6 独立视觉参数覆盖能力，让第三次放刀前的感知参数改为 perception config 驱动而不是 orchestrator 硬编码。
- Work completed:
  1. 在 `tofu_perception_params.yaml` 中新增顶层 `phase6_vision` 配置区，语义对齐 legacy `cutting.phase6_vision`，并注明“未指定字段回退到默认 `tofu_perception_node.ros__parameters`”。
  2. 新增 `tofu_perception_config.py`，集中读取 perception YAML，并提供 `runtime_override("phase6")`，负责默认参数合并与可运行时下发字段过滤。
  3. 改造 `workflow_runner.py` 的 `_begin_perception_override()`，移除 `vision_override == "phase6"` 的硬编码参数列表，改为从 perception config 读取 override 后组装 `SetParameters` 请求。
  4. 将 `tofu_workflow_no_approach_params.yaml` 的第三次放刀 prepare 步骤补齐 `vision_override: phase6`，与默认 workflow 保持一致。
  5. 完成 `python3 -m py_compile` 与 `colcon build --base-paths ... --packages-select cuttofo_skill_tofu_perception cuttofo_orchestrator --symlink-install` 验证。
- Business logic impact:
  - phase6/第三次放刀前的视觉参数切换仍通过 orchestrator 的 `APPLY_PARAMS -> SetParameters(/tofu_perception_node)` 时序执行，但 override 数据源已从 Python 常量迁回 perception YAML。
  - phase1/phase2 继续使用默认 `tofu_perception_node.ros__parameters`；只有 `vision_override: phase6` 的 prepare 步骤会切到独立 phase6 视觉参数集合。
- Problems encountered:
  1. 当前 CutTofo 已有 phase6 override 语义，但来源分散在 orchestrator Python 内，现场调参不可见。
  2. `tofu_perception_params.yaml` 原先没有 phase6 独立参数区，也没有显式 fallback 语义。
- Resolution:
  - 把 phase6 参数维护入口收口到 perception config，并在 orchestrator 侧只保留“读取配置并下发”的职责。
- Verification:
  - `python3 -m py_compile` 覆盖 `workflow_runner.py` 与 `tofu_perception_config.py` 通过。
  - `colcon build --base-paths /home/tbl/Project/cucumber/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo --packages-select cuttofo_skill_tofu_perception cuttofo_orchestrator --symlink-install` 通过。
- Unverified items:
  - 尚未在真机/运行中的 ROS graph 上确认 phase6 prepare 前 `SetParameters` 的实际下发值与 `tofu_perception_node` 当前参数状态完全一致。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_perception_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/cuttofo_skill_tofu_perception/tofu_perception_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_runner.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/config/tofu_workflow_no_approach_params.yaml`
- Next steps:
  - 启动节点栈后执行 phase6 对应的 `prepare:after_rotation_1`，确认日志里显示 config-driven `vision_override='phase6'(... params)`。
  - 用 `ros2 param get /tofu_perception_node ...` 或日志确认 phase6 的 OBB 百分位与 depth/median 等参数已切换。

- Follow-up:
  - 复查 legacy `phase6_prepare` 后，确认 phase6 不只是视觉过滤参数不同，prepare 目标点偏移 `offset_a` / `vertical_offset` 也应一并切换；当前已将这两个字段补入 phase6 override，由 `tofu_perception_node` 运行时更新并驱动 `tcp_target`。
  - 真机全流程启动时发现 `tofu_perception_params.yaml` 被 ROS 2 当作 `--params-file` 直接加载，因此顶层不能混入 `phase6_vision` 这类非节点参数；现已将 override 拆到独立 `tofu_perception_overrides.yaml`，恢复 launch 可解析性。

## 2026-06-07 18:05 CST

- Objective: 把豆腐 phase6 prepare 的本地目标补偿与 perception 几何生成职责拆开，避免 prepare 再次重算 `tcp_target`。
- Work completed:
  1. 对照 legacy `cutting.phase2_prepare` / `phase6_prepare` 与当前 `tofu_prepare_workflow.py`，确认 `offset_a` / `vertical_offset` 本质上属于 perception 侧 `tcp_target` 生成参数，而不是 prepare 内部二次重建目标点的依据。
  2. 清理 `tofu_prepare_workflow.py` 中基于 `top_corners` 调 `compute_tcp_target_from_corners()` 的分支，统一改为直接消费 `vision_tracker.wait_valid()` 返回的 `tofu.tcp_target`。
  3. 保留 cucumber 现有 along-axis + `target_offset_m` 补偿链路，同时在 `tofu_prepare_vision_offset.py` 新增 `apply_tofu_prepare_target_offsets()`，让 tofu profile 也能在 prepare 内追加 profile-local 固定平移。
  4. 将 `tofu_prepare_params.yaml` 中 tofu profile 的 prepare-local 补偿收口为 `target_offset_m`，并去掉容易与 perception 语义混淆的 `offset_a` / `vertical_offset` / `offset_x` prepare 字段。
  5. 对 `tofu_prepare_workflow.py`、`tofu_prepare_vision_offset.py` 进行 `python3 -m py_compile` 验证，并对相关 diff 执行 `git diff --check`。
- Business logic impact:
  - perception 继续独占“根据 corners/OBB 生成原始 `tcp_target`”职责，包括 phase6 的 `offset_a` / `vertical_offset` override。
  - prepare 不再重算 perception 几何，只允许在拿到原始 `tcp_target` 后按 profile 的 `target_offset_m` 做本地控制补偿。
  - 这样 phase6 若还需额外 prepare 偏移，后续只需调 `after_rotation_1.target_offset_m`，不会再污染 perception 或可视化输出。
- Problems encountered:
  1. 当前 prepare 曾同时存在两套目标来源：一套来自 perception 发布的 `tcp_target`，另一套来自 prepare 内 `top_corners + offset_*` 重算，容易造成 phase6 调参时职责边界混乱。
  2. `tofu_prepare_params.yaml` 里曾混有 `offset_a` / `vertical_offset` / `offset_x` 这类名字，它们与 perception 节点的同名字段语义接近但作用层级不同，后续维护风险很高。
- Resolution:
  - 删除 prepare 内二次重算分支，统一以 perception 发布值为基线；prepare-local 额外补偿一律改走 `target_offset_m`。
- Verification:
  - `python3 -m py_compile src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_vision_offset.py` 通过。
  - `git diff --check -- src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_vision_offset.py src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml` 通过。
- Unverified items:
  - 尚未在真机上确认 `after_rotation_1.target_offset_m` 是否需要填写非零值，以及该补偿是否足以覆盖现场 phase6 prepare 的剩余误差。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_vision_offset.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml`
- Next steps:
  - 真机跑到 `prepare:after_rotation_1`，先确认 phase6 perception override 生效，再观察是否还存在仅属于 prepare 的固定偏差。
  - 若存在，再直接填写 `after_rotation_1.target_offset_m`，避免重新引入 prepare 内 `compute_tcp_target_from_corners()` 一类双轨逻辑。

## 2026-06-07 14:35 CST

- Objective: 清理 cucumber 工作区的环境卫生问题，切断旧 tofu 工作区污染，并把运行时 SDK / 模型路径收敛到当前工作区。
- Work completed:
  1. 清理 `~/.bashrc` 中 FishROS 初始化块，删除对 `/home/tbl/Project/tofu/dexbot_ros2_ws/install/setup.bash` 的自动 overlay，只保留 `/opt/ros/humble/setup.bash`。
  2. 在 `dexbot_bottom_layer/ws_paths.py` 新增 `linkerbot_sdk_src_dir()`，作为 linkerbot SDK 源码目录的统一解析入口。
  3. 收紧 `lbot_api.py` 的 `.so` fallback 搜索逻辑，移除从任意 `build/` / `install/` 推导其他工作区源码树的兜底行为，仅保留当前工作区 `ws_paths.lbot_python_dir()`。
  4. 将 `src/gui/main.py`、`dexbot_toolbox/gui/arm_hand_gui.py`、`cuttofo_skill_common/arm/xcore_sdk_paths.py`、`CutTofo/ros/xcore_phase1_paths.py`、`CutTofo/ros/xcore_follow_tcp_chain_node_movej.py` 统一改为复用 `dexbot_bottom_layer.ws_paths` 解析当前工作区内的 linkerbot / xCore SDK 路径。
  5. 将 `sam3_detector_node.py` 的 `model_path` 默认值改为当前工作区内的 `~/Project/cucumber/dexbot_ros2_ws/models/sam3`，并支持 `DEXBOT_SAM3_MODEL_PATH` 显式覆盖。
  6. 将 `cuttofu_vision/config/vision_params.yaml`、`cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml`、`dexbot_bottom_layer/config/perception_params.yaml` 中的 SAM3 模型路径从 `/home/tbl/Project/models/sam3...` 改为当前 cucumber 工作区路径。
  7. 顺手清理 GUI 文档/服务中的旧工作区引用：修正 `src/gui/README.md` 与 `src/gui/web/dexbot-web.service` 中残留的 `/home/tbl/Project/tofu/dexbot_ros2_ws`。
  8. 在纯净 ROS 环境下重新构建 `dexbot_bottom_layer`、`dexbot_middle_layer`、`dexbot_toolbox` 以及 CutTofo skills / orchestrator / vision 相关包，刷新 install/setup 产物。
- Business logic impact: 无主业务逻辑变更；此次修改只影响运行环境与资源解析策略。业务上的含义是：cucumber 工作区恢复为默认不依赖外部 tofu 工作区的自足运行形态。
- Problems encountered:
  1. 直接在当前污染 shell 中重编译时，colcon 会把旧 tofu underlay 链进新的 install/setup 产物，导致即使 `~/.bashrc` 已清理，`source install/setup.bash` 仍继续把 tofu 路径注回环境。
  2. CutTofo skills / orchestrator / vision 这些包不是根工作区自动发现构建，必须继续走 `CutTofo/scripts/build_skills.sh` 与 `build_cuttofo.sh` 的 `--paths` 显式构建链。
- Resolution:
  - 改为在 `env -i` 的纯净 shell 中，只 source `/opt/ros/humble/setup.bash` 后执行重编译，确保新的 install/setup 不再记录 tofu underlay。
  - 对 skills 相关包继续使用仓内已有的显式构建脚本，而不是依赖根级 `--packages-select`。
- Verification:
  - `env -i ... bash --rcfile ~/.bashrc -ic 'source install/setup.bash && ...'` 检查环境变量后，`AMENT_PREFIX_PATH`、`COLCON_PREFIX_PATH`、`CMAKE_PREFIX_PATH`、`PYTHONPATH`、`LD_LIBRARY_PATH` 已不再包含 `/home/tbl/Project/tofu/dexbot_ros2_ws`。
  - `python3` 验证 `dexbot_bottom_layer.__file__`、`linkerbot_sdk_src_dir()`、`xcore_sdk_root()`、`lbot_api.LibraryLoader.get_library_path()` 均命中 cucumber 工作区路径；`liblbot_api.so` 当前从 `cucumber/build/.../liblbot_api.so` 加载，不再来自 tofu。
  - `rg -n "/home/tbl/Project/tofu/dexbot_ros2_ws|/home/tbl/Project/models/sam3" src ~/.bashrc` 已无运行时相关残留；仅剩少量已同步修正的 GUI 文档/服务引用。
  - 纯净环境重建通过：`dexbot_bottom_layer`、`dexbot_middle_layer`、`dexbot_toolbox`、CutTofo skills、`cuttofu_vision`、`cuttofo_orchestrator`。
- Unverified items:
  - 尚未在真机上重新验证 `skills_bringup` / `tofu_perception.launch.py` / `prepare` / `cut_round`，因此还不能确认此前 `setFcCoor(world)` 网络错误是否已因环境收口而消失。
  - 当前默认 SAM3 模型路径已改为工作区内 `models/sam3`；若本地实际模型尚未放入该目录，则运行前仍需显式提供 `DEXBOT_SAM3_MODEL_PATH` 或补齐仓内模型目录。
- Files changed:
  - `/home/tbl/.bashrc`
  - `src/dexbot_bottom_layer/dexbot_bottom_layer/ws_paths.py`
  - `src/dexbot_bottom_layer/dexbot_bottom_layer/lbot_catch/arm_api/Python/lbot/lbot_api.py`
  - `src/dexbot_middle_layer/dexbot_middle_layer/sam3_detector_node.py`
  - `src/dexbot_middle_layer/dexbot_middle_layer/vision/pipeline/sam3_detector.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_vision/config/vision_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml`
  - `src/dexbot_bottom_layer/config/perception_params.yaml`
  - `src/gui/main.py`
  - `src/dexbot_toolbox/dexbot_toolbox/gui/arm_hand_gui.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/arm/xcore_sdk_paths.py`
  - `src/dexbot_middle_layer/CutTofo/ros/xcore_phase1_paths.py`
  - `src/dexbot_middle_layer/CutTofo/ros/xcore_follow_tcp_chain_node_movej.py`
  - `src/gui/README.md`
  - `src/gui/web/dexbot-web.service`
- Next steps:
  - 在新终端中只执行 `source /opt/ros/humble/setup.bash` 和 `source /home/tbl/Project/cucumber/dexbot_ros2_ws/install/setup.bash`，再跑真机链路复验。
  - 优先复测 `skills_bringup`、`tofu_perception.launch.py`、`ExecuteTofuPrepare`、`ExecuteTofuCutRound`，观察 `setFcCoor(world)` 是否仍报连接错误。
  - 若用户坚持“资源自足”包含模型文件本体，则下一步需要决定是否将 `models/sam3` 正式 vendoring 到仓内，或改成统一的外部模型配置入口。

## 2026-06-07 12:43 CST

- Objective: 收敛 CutTofo 豆腐视觉几何职责边界，消除 prepare/visualizer/tracker 对 perception 已发布 tofu 几何的重复计算与重复参数面。
- Work completed:
  1. `tofu_prepare_workflow.py` 改为在 `use_vision=true` 时直接消费 perception 发布的 `tofu.tcp_target`，不再从 `top_corners` 本地重算 tofu TCP。
  2. `VisionGeometryTracker` 去掉 `offset_a`、`vertical_offset`、`offset_x` 的本地几何所有权，`configure()` 仅保留非几何等待/筛选配置；当消息缺失 `tcp_target` 时不再本地补算而是视为无效输入。
  3. `task_visualizer_node.py` 去掉从 corners fallback 重算 TCP 的逻辑，改为缺失 perception TCP 时仅告警并跳过 TCP/edge 相关 marker。
  4. `capture_tofu_sauce_target.py` 中的 `VisionGeometryTracker` 构造移除 tofu 视觉 offset 注入，保持 sauce pour 仅基于豆腐几何派生任务目标。
  5. `tofu_prepare_node.py`、`tofu_prepare_config.py`、`tofu_prepare_params.yaml` 删除 prepare 侧 `vision_offset_a`、`vision_vertical_offset`、`vision_offset_x` 及相关 profile 覆盖，视觉几何参数收敛到 perception 配置。
  6. `ExecuteTofuPrepare.action` 删除 `offset_a`、`vertical_offset` 字段，prepare action 不再暴露豆腐视觉几何覆盖入口。
  7. 清理 `vision_geometry_tracker.py` 中已失效的几何 helper import，并同步修正文档 `启动指令.md` 中旧 prepare action 示例，移除已删除字段。
  8. 重新构建并通过验证以下包：`cuttofo_skill_interfaces`、`cuttofo_skill_tofu_prepare`、`cuttofo_skill_tofu_perception`、`cuttofo_task_visualizer`、`cuttofo_skill_sauce_pour`。
- Business logic impact: 豆腐主链路进一步固化为“通用/独立 vision 输出 -> `tofu_perception_node` 负责 tofu 视觉几何 -> prepare / visualizer / sauce-pour 等下游只消费感知结果或派生任务几何”；prepare 不再是第二个 tofu TCP 几何计算器。
- Problems encountered:
  1. prepare、shared tracker、task visualizer 之间长期存在“消费 perception 输出后再次从 corners 重算 tofu TCP”的职责外泄。
  2. prepare 配置与 action 接口仍保留一套重复的视觉 offset 参数，造成视觉几何来源分裂。
  3. 文档和少量调用示例仍引用旧 action 字段。
- Resolution:
  - 将 tofu 视觉 TCP/edge/corners 的所有权统一收敛到 perception 发布契约；下游只读取，不再重算。
  - 删除 prepare 侧重复视觉 offset 参数和 action 字段，并同步修正文档示例。
- Verification:
  - `bash src/dexbot_middle_layer/CutTofo/scripts/build_skills.sh --paths src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_interfaces src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_task_visualizer src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_sauce_pour`
  - 构建结果：5 个受影响包全部通过。
  - 静态搜索确认 prepare 路径与 task visualizer 路径已不再持有旧的 tofu TCP fallback 入口。
- Unverified items:
  - 尚未做真机/RViz 运行验证，仍需确认 perception 发布的 `tcp_target` 与 prepare / visualizer 实际消费结果完全一致。
  - 尚未继续处理旧 `cuttofo_xcore` 路径中的同类 prepare 重算模式；当前仅完成 CutTofo skills 主链路收敛。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/perception/vision_geometry_tracker.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_node.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_config.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_task_visualizer/cuttofo_task_visualizer/task_visualizer_node.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_sauce_pour/cuttofo_skill_sauce_pour/capture_tofu_sauce_target.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_interfaces/action/ExecuteTofuPrepare.action`
  - `src/dexbot_middle_layer/CutTofo/启动指令.md`
- Next steps:
  - 启动 perception + prepare + visualizer 真机链路，确认下游显示/执行与 perception 发布的 `tcp_target` 完全一致。
  - 如需继续收敛历史路径，再处理 `cuttofo_xcore` 中 prepare 侧同类重算与重复参数问题。
  - 若 GUI 手控继续报错，顺着本地 SDK 继续排查运行时依赖和 CAN/设备层通信。

## 2026-06-07 09:20 CST

- Objective: 对比当前 constrained_obb 与 legacy/xcore 视觉链路，收口参数并排查真机启动后 SAM3 与 tofu marker 不显示的问题。
- Work completed:
  1. 端到端对比当前 workspace 与 legacy/xcore 的豆腐视觉链路，确认两边都在使用 `corner_mode: constrained_obb`，但 constrained_obb 参数存在明显偏差。
  2. 将当前测试链路中的 constrained_obb 参数向 legacy 收口，在 `tofu_perception_params.yaml` 与 `tofu_vision_params.yaml` 中统一修改：
     - `obb_margin: 0.003`
     - `obb_depth_median_frames: 1`
     - `obb_bounds_top_keep_ratio: 0.8`
     - `obb_bounds_u_percentile_low/high: 2.0 / 98.0`
     - `obb_bounds_v_percentile_low/high: 2.0 / 98.0`
  3. 指导用户启动完整链路 `cuttofo_skill_tofu_perception/tofu_perception.launch.py`，并基于现场 `ros2 node list` / `ros2 topic` / `ros2 param` 输出排查为何无检测、无 marker。
  4. 确认 `tofu_perception_node`、`task_visualizer_node`、`sam3_detector_node`、`pose_estimator_node` 都已启动，`/cuttofu/perception/task_visualization` 与 `/cuttofu/perception/tofu_state` 也都存在，但 `tofu_state` 内容为空对象、marker 只在发 `DELETEALL` 清空帧。
  5. 进一步定位根因：`sam3_detector_node` 实际订阅的是 `/camera/color/image_raw`，而现场 RealSense 真正发布的是 `/camera/camera/color/image_raw`；因此 SAM3 拿不到彩色图像，后续 `detected_objects -> tofu_state -> marker` 全链路都为空。
  6. 在 `tofu_vision_params.yaml` 中显式补充 `image_topic: /camera/camera/color/image_raw`，强制绕过错误的旧参数继承/默认分支，避免 SAM3 继续订阅无发布者的话题。
  7. 同时确认现场 prompt 链路状态：`/cuttofu/vision/text_prompt` 上已经是 `ridged_tofu`，但 `sam3_detector_node` 的静态参数仍保留 `text_prompt: cargo truck`；说明提示词动态发布链路是通的，真正阻断点是彩色图订阅错误，而不是 tofu_perception 没发 prompt。
- Business logic impact:
  - 豆腐独立感知测试链路的 constrained_obb 参数已进一步向 legacy 版本收口，便于做同口径真机效果比较。
  - 当前链路仍保持 `cuttofu_vision -> tofu_perception_node -> task_visualizer_node` 的分层；这次排查确认“无检测/无 marker”不是感知层逻辑错误，而是 SAM3 输入彩色图话题配置错误导致上游空转。
- Problems encountered:
  1. 用户启动完整链路后，RViz 中看不到豆腐 marker，主观上认为 SAM3 没有开始检测。
  2. 现场同时存在 `/camera/color/image_raw` 与 `/camera/camera/color/image_raw` 两套命名历史，但当前这次启动里只有后者有 publisher。
  3. `sam3_detector_node` 运行时仍带有旧的 `image_topic: /camera/color/image_raw`，覆盖了 `camera_backend: realsense` 的预期行为，导致 SAM3 订错话题却没有显式崩溃。
- Resolution:
  - 通过 `ros2 node info`、`ros2 topic info -v`、`ros2 param dump/get`、`ros2 topic echo --once` 逐层排查，确认上游空检测是因为 SAM3 未收到 RealSense 彩色图。
  - 在 `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml` 中显式加上 `image_topic: /camera/camera/color/image_raw`，要求重编译并重启链路。
- Verification:
  - 已确认 `/camera/camera/color/image_raw` 有 publisher，而 `/camera/color/image_raw` 无 publisher。
  - 已确认 `/cuttofu/perception/tofu_state` 当前只发布空对象，`/cuttofu/perception/task_visualization` 当前只发布清空 marker，符合“上游无检测”的表现。
  - 已确认 `/cuttofu/vision/text_prompt` 上的动态提示词为 `ridged_tofu`，说明 prompt 发布链路本身正常。
  - 仍待用户按新 `image_topic` 配置重编译、重启后做真机复验。
- Unverified items:
  - 尚未拿到用户在修正 `image_topic` 后的新一轮真机结果，无法确认 marker 是否恢复、角点贴合是否随参数收口而改善。
  - 尚未决定是否要进一步清理 `cargo truck` 这一静态默认 `text_prompt`，避免启动早期短暂误检。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_perception_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml`
- Next steps:
  - 让用户按修正后的 `image_topic` 重新编译并重启完整链路，验证 SAM3 检测、tofu_state、marker 是否恢复。
  - 若恢复后角点仍不理想，继续拆分“参数收口效果”和“双重 constrained_obb 计算影响”两个因素。
  - 根据真机结果，决定是否顺手清理静态 `cargo truck` 默认 prompt，避免启动阶段的类别抖动。

## 2026-06-07 14:35 CST

- Objective: 彻底清理 cucumber 工作区的环境卫生，确保运行时不再依赖外部工作区或硬编码绝对路径，并修复 GUI 直接运行引导。
- Work completed:
  1. 移除 `~/.bashrc` 中 tofu 工作区自动 source，改为按需在当前 shell 手动 source cucumber workspace。
  2. 在 `dexbot_bottom_layer/ws_paths.py` 中新增 `linkerbot_sdk_src_dir()` 共享辅助函数。
  3. 将 `lbot_api.py` 中的 `.so` fallback 搜索逻辑大幅收紧，只保留通过 `dexbot_bottom_layer.ws_paths` 的显式路径，移除广泛扫描 `build/install` 祖先目录导致意外加载 tofu 工作区 `.so` 的漏洞。
  4. 统一 GUI、toolbox、xCore 路径辅助函数，全部改为引用 `dexbot_bottom_layer.ws_paths` 中的 `find_ws_root()`、`xcore_sdk_root()`、`linkerbot_sdk_src_dir()`，移除各处独立实现的重复查找逻辑。
  5. 清理所有 SAM3 模型路径配置，将外部 `/home/tbl/Project/models/sam3` 改为 cucumber 本地 `~/Project/cucumber/dexbot_ros2_ws/models/sam3`，同时新增 `DEXBOT_SAM3_MODEL_PATH` 环境变量显式覆盖路径。
  6. 修复 `src/gui/main.py` 直接运行引导，在导入 `dexbot_bottom_layer.ws_paths` 之前先用 `pathlib.Path` 自举将本地 `src/gui`、`src/dexbot_bottom_layer`、`src/` 加入 `sys.path`，保证 `python3 main.py` 在未 source ROS 环境时也能正常启动。
  7. 修正 `src/gui/web/dexbot-web.service` 与 `src/gui/README.md` 中残留的 tofu 工作区路径，统一改为 cucumber 工作区。
  8. 清理 `cuttofu_phase2.launch.py` 与 `viz_display.launch.py` 中的硬编码左臂标定 fallback 路径 `/home/tbl/Project/dexbot_ros2_ws/...`，改为 `find_ws_root() + "src/config/calib_left/..."`。
  9. 清理 `src/config1/calibration_result.yaml` 与 `src/config1/calibration_result_samples.json` 中残留的异地机器工作区路径 `/home/yishui/Yiping/dexbot_ros2_ws`，改为 cucumber 工作区本地路径。
  10. 清理 `src/gui/services/logger.py` 文档注释中的 tofu 工作区引用。
  11. 在干净 shell（`env -i` + 仅 `/opt/ros/humble/setup.bash` + cucumber `install/setup.bash`）中重新编译 `dexbot_bottom_layer`、`dexbot_middle_layer`、`dexbot_toolbox` 和全部 CutTofo 包，重新生成 `install/setup.bash` 使其不再链接 tofu 工作区。
  12. 验证干净 shell 环境变量 `AMENT_PREFIX_PATH`、`COLCON_PREFIX_PATH`、`CMAKE_PREFIX_PATH`、`PYTHONPATH`、`LD_LIBRARY_PATH` 不再包含 tofu 工作区路径。
  13. 验证 Python import `dexbot_bottom_layer.ws_paths` 与 `liblbot_api.so` 加载均指向 cucumber 本地路径，无 tofu 残留。
  14. 验证 GUI `main.py` 直接 `python3 main.py` 能正常完成全部导入（未启动 Tk 主循环，仅做导入链路验证）。
- Business logic impact: 无，纯环境卫生清理。
- Problems encountered:
  1. 初次在干净 shell 验证环境时，发现 `install/setup.bash` 仍带 tofu underlay 前缀链，根因是之前构建时 shell 已 source 过 tofu 工作区。
  2. GUI `main.py` 在直接源码树执行时，导入 `dexbot_bottom_layer.ws_paths` 失败，需要在导入前自举将工作区 `src/` 加入 `sys.path`。
  3. `cuttofu_phase2.launch.py` 与 `viz_display.launch.py` 中左臂标定文件 fallback 仍有硬编码绝对路径 `/home/tbl/Project/dexbot_ros2_ws/src/config/calib_left/...`。
  4. `src/config1/` 下校准元数据残留异地机器路径 `/home/yishui/Yiping/dexbot_ros2_ws/...`。
- Resolution:
  - 清空当前 shell 的 tofu underlay，在 `env -i` 纯净环境下重新编译 cucumber 工作区。
  - 在 `src/gui/main.py` 最开头加入 `_bootstrap_workspace_sources()` 自举，先把本地 `src/gui`、`src/dexbot_bottom_layer`、`src/` 加入 `sys.path` 再导入 `dexbot_bottom_layer.ws_paths`。
  - 将两个 launch 文件的左臂标定 fallback 改为 `find_ws_root() + "src/config/calib_left/calibration_result_left.yaml"`。
  - 将 `src/config1/` 元数据路径改为 cucumber 本地等效路径。
- Verification:
  - 在干净 shell 执行 `source /opt/ros/humble/setup.bash && source install/setup.bash`，环境变量不再包含 tofu 路径。
  - Python 导入 `dexbot_bottom_layer.ws_paths` 与加载 `liblbot_api.so` 均指向 cucumber 本地路径。
  - `python3 -c 'import runpy; runpy.run_path("src/gui/main.py", run_name="__not_main__"); print("main.py import ok")'` 成功输出 `main.py import ok`。
  - `python3 -m py_compile` 对 `main.py`、`cuttofu_phase2.launch.py`、`viz_display.launch.py` 无语法错误。
  - CutTofo 包重编译成功（13 个包，0 错误）。
- Unverified items:
  - GUI `python3 main.py` 启动完整 Tk 主循环（当前仅验证导入链路）。
  - 真机启动 `skills_bringup`、`tofu_perception.launch.py`、`ExecuteTofuPrepare`、`ExecuteTofuCutRound` 验证 `setFcCoor(world)` 连接错误是否随环境清理而消失。
  - SAM3 模型文件实际位置（若 `~/Project/cucumber/dexbot_ros2_ws/models/sam3` 不存在，需放置模型文件或设置 `DEXBOT_SAM3_MODEL_PATH`）。
- Files changed:
  - `~/.bashrc`
  - `src/dexbot_bottom_layer/dexbot_bottom_layer/ws_paths.py`
  - `src/dexbot_bottom_layer/dexbot_bottom_layer/lbot_catch/arm_api/Python/lbot/lbot_api.py`
  - `src/dexbot_middle_layer/dexbot_middle_layer/sam3_detector_node.py`
  - `src/dexbot_middle_layer/dexbot_middle_layer/vision/pipeline/sam3_detector.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_vision/config/vision_params.yaml`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/config/tofu_vision_params.yaml`
  - `src/dexbot_bottom_layer/config/perception_params.yaml`
  - `src/gui/main.py`
  - `src/gui/web/dexbot-web.service`
  - `src/gui/README.md`
  - `src/gui/services/logger.py`
  - `src/dexbot_toolbox/dexbot_toolbox/gui/arm_hand_gui.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_common/cuttofo_skill_common/arm/xcore_sdk_paths.py`
  - `src/dexbot_middle_layer/CutTofo/ros/xcore_phase1_paths.py`
  - `src/dexbot_middle_layer/CutTofo/ros/xcore_follow_tcp_chain_node_movej.py`
  - `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`
  - `src/cuttofo_xcore/launch/viz_display.launch.py`
  - `src/config1/calibration_result.yaml`
  - `src/config1/calibration_result_samples.json`
## 2026-06-08 当前 CST

- Objective: 全流程切豆腐验证通过，准备将拔刀工作流集成到切豆腐前面。
- Work completed:
  1. 创建 prepare target_offset_m 标定脚本 `calibrate_prepare_target_offset.py`，支持 `step1`（横切）/ `step2`（竖切）双阶段标定。
  2. 创建标定使用文档 `prepare_target_offset_calibration_usage.md`，明确输出为最终推荐值而非增量值。
  3. 在标定脚本中新增 perception override 逻辑：`step2` 标定前自动向 `tofu_perception_node` 下发 `phase6_vision` 覆盖参数（OBB 过滤、prompt 切换为 ridged_tofu 等），保证竖切放刀阶段感知参数与 orchestrator workflow 一致。
  4. 经检查确认标定脚本的偏置计算公式正确：`final_offset = initial_offset + (after_flange_pos - before_flange_pos)`。
  5. 用户实机验证豆腐全流程（prepare → cut_round → vertical_cut）运行稳定无问题。
- Business logic impact: 新增标定工具与文档，不改变现有豆腐主流程；拔刀工作流集成是下一步。
- Problems encountered:
  1. 标定脚本首次运行时不会自动加载 perception override，导致 step2 竖切放刀时感知参数与 orchestrator workflow 不一致。
- Resolution:
  1. 通过复用 `tofu_perception_config.runtime_override("phase6")` 和 `SetParameters` 服务调用的方式，在标定脚本中补充了与 orchestrator 等价的 override 下发逻辑。
- Verification:
  - `python3 -m py_compile calibrate_prepare_target_offset.py` 通过。
  - 数学验证：`final = initial + (after - before)` 在纯平移假设下正确。
- Unverified items:
  - 标定脚本的 perception override 尚未真机验证。
  - 拔刀工作流集成尚未开始。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/scripts/calibrate_prepare_target_offset.py`（新建）
  - `src/dexbot_middle_layer/CutTofo/scripts/prepare_target_offset_calibration_usage.md`（新建）
- Next steps:
  - 将拔刀工作流集成到切豆腐流程前面。

- Objective: 收口豆腐无拔刀工作流的启动职责边界，让 workflow 成为单入口完整装配点，并整理现场可直接执行的测试指令。
- Work completed:
  1. 将 `cuttofu_vision/launch/vision_bringup.launch.py` 收紧为纯 vision 入口，只保留 RealSense、SAM3、pose_estimator、legacy relay、`tofu_state_node`、相机画面，不再内部启动 `task_visualizer`。
  2. 将 `cuttofo_skill_tofu_perception/launch/tofu_perception.launch.py` 收紧为纯 perception 入口，只启动 `tofu_perception_node`，移除其中对 vision、RViz、marker-only visualizer 的嵌套启动职责。
  3. 重组 `cuttofo_orchestrator/launch/tofu_skills_bringup_no_approach.launch.py`，改为显式装配 `vision + tofu_perception + task_visualizer + tofu_prepare + tofu_cut_round + tofu_vertical_cut`，不再通过 perception launch 间接带起上游和可视化。
  4. 更新 `cuttofo_orchestrator/launch/tofu_workflow_execute_no_approach.launch.py` 说明，使其语义明确为“一键装配完整节点栈，并可选自动执行 orchestrator”。
  5. 回退 `tofu_prepare_node.py` 与 `tofu_prepare_workflow.py` 中此前加入的 `use_vision` 自动猜测逻辑，恢复为只按 action goal 显式字段执行，避免 skill server 越权替调用方决定视觉模式。
  6. 更新 `启动指令.md`，只保留两套现场入口：一套一键完整 workflow，一套 `run_orchestrator:=false` 的完整节点栈 + 手动 action 单阶段测试，并在 prepare 示例中显式加入 `use_vision: true`。
  7. 对上述改动执行 `python3 -m py_compile` 语法检查，并重新构建 `cuttofu_vision`、`cuttofo_skill_tofu_perception`、`cuttofo_task_visualizer`、`cuttofo_skill_tofu_prepare`、`cuttofo_orchestrator`，构建通过。
- Business logic impact:
  - 豆腐链路职责边界重新收口为：`vision_bringup` 只管上游视觉与相机画面，`tofu_perception.launch.py` 只管几何感知，`task_visualizer.launch.py` 只管可视化，`tofu_workflow_execute_no_approach.launch.py` / `tofu_skills_bringup_no_approach.launch.py` 作为唯一的整栈装配层。
  - `tofu_prepare` 的视觉使用权重新回到 orchestrator / 手动 action 调用方手中，prepare skill 不再依据 profile 和零位姿隐式改写调用语义。
- Problems encountered:
  1. 之前的中间态改动把 `tofu_perception.launch.py` 变成了 vision/RViz 的嵌套装配点，破坏了“感知节点只做感知”的职责边界。
  2. `tofu_prepare` 内部存在两层 `use_vision` fallback，会在调用方未显式给出 manual pose 时偷偷切回视觉模式，和当前架构目标冲突。
- Resolution:
  - 通过拆分 launch ownership、回退 prepare fallback、把完整装配显式上提到 orchestrator bringup，恢复单一职责边界。
- Verification:
  - `python3 -m py_compile` 已覆盖 6 个改动 Python/launch 文件，语法通过。
  - `colcon build --base-paths ... --packages-select cuttofu_vision cuttofo_skill_tofu_perception cuttofo_task_visualizer cuttofo_skill_tofu_prepare cuttofo_orchestrator --symlink-install` 通过，5 个包全部成功构建。
- Unverified items:
  - 尚未做真机级别的整栈启动验证，尚未确认 `run_orchestrator:=false` 下是否稳定同时出现相机画面、`tofu_perception_node`、`task_visualizer_node`、`rviz2` 与下游 skill servers。
  - 尚未再次执行手动 `prepare` action 验证当前日志是否明确显示 `use_vision=True` 并顺利进入 `waiting_tofu` / `computing_ik`。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_vision/launch/vision_bringup.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_perception/launch/tofu_perception.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_skills_bringup_no_approach.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute_no_approach.launch.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_node.py`
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py`
  - `src/dexbot_middle_layer/CutTofo/启动指令.md`
- Next steps:
  - 在新终端中只 source ROS base + cucumber install，执行 `ros2 launch cuttofo_orchestrator tofu_workflow_execute_no_approach.launch.py run_orchestrator:=false`，确认完整节点栈是否按预期一次性拉起。
  - 手动发送 `prepare` action（显式 `use_vision: true`）验证视觉感知与 IK 链路。
  - 若整栈启动稳定，再执行默认 workflow 入口确认无拔刀全流程可直接复测。

## 2026-06-08 CST

- Objective: 将拔刀（handle_approach）工作流集成到切豆腐流程前面，实现一键启动拔刀+切豆腐全流程。
- Work completed:
  1. 通过 plan mode 规划了集成方案：修改 `tofu_workflow_execute.launch.py` 引入 vision_bringup + task_visualizer + TimerAction，修改 `workflow_runner.py` 扩展 PREFLIGHT 检查。
  2. 修改 `tofu_workflow_execute.launch.py`：
     - 引入 `vision_bringup`（`cuttofu_vision`，`tofu_vision_params.yaml`，`enable_tofu_state:=false`）
     - 引入 `task_visualizer`（`cuttofo_task_visualizer`，连线 `/cuttofu/perception/tofu_state`、`/cuttofu/perception/task_visualization`）
     - orchestrator Node 包装 `TimerAction`（默认 2s），让 skill servers + vision 先就绪
     - 新增 5 个 launch arguments：`show_camera_display`、`rs_color_profile`、`rs_depth_profile`、`depth_qos_reliable`、`orchestrator_startup_delay_sec`
  3. 修改 `workflow_runner.py`：`_tick_preflight()` 中的 `skill_servers` 从硬编码 4 个改为 `self._clients`，动态收集 steps 中引用的所有 skill servers（含 `cut_round`、`vertical_cut`）。
  4. 补充 `启动指令.md`：以 `---` 分割追加带拔刀全流程的一键启动（section 1）与手动 goal 测试（section 2）。
- Business logic impact:
  - 带拔刀变体现在是真正的一键启动：`ros2 launch cuttofo_orchestrator tofu_workflow_execute.launch.py` 即可拉起 vision + skill servers + task_visualizer + orchestrator，自动执行 handle_approach → 切豆腐全流程。
  - PREFLIGHT 现在会检查 workflow 步骤中实际使用的所有 action servers（含 cut_round、vertical_cut），而非之前的 4 个硬编码子集。
  - 无拔刀变体（`tofu_workflow_execute_no_approach.launch.py`）不受影响。
- Problems encountered:
  - Write 工具在大段内容写入时发生参数丢失（`file_path`/`content` 缺失），需要分批次写入。记录为 feedback memory。
  - Session 因上下文超限制被截断，需恢复时从 plan 文件继续。
- Resolution:
  - plan 分 3 批写入（Write + 2 次 Edit append）
  - 实现时用 Edit 而非 Write 逐段修改
- Verification:
  - `python3 -m py_compile` 两个修改文件均通过
  - `ros2 launch cuttofo_orchestrator tofu_workflow_execute.launch.py --show-args` 确认 8 个声明的参数 + 子 launch 继承参数正确显示
- Unverified items:
  - 尚未做真机一键启动验证
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/launch/tofu_workflow_execute.launch.py`（修改）
  - `src/dexbot_middle_layer/CutTofo/cuttofo_orchestrator/cuttofo_orchestrator/workflow_runner.py`（修改）
  - `src/dexbot_middle_layer/CutTofo/启动指令.md`（追记）
- Next steps:
  - 真机验证：`ros2 launch cuttofo_orchestrator tofu_workflow_execute.launch.py` 一键启动拔刀→切豆腐全流程。
  - 若 handle_approach PREFLIGHT 超时，适当增大 `orchestrator_startup_delay_sec`。
  - 若 vision/perception 启动顺序问题，根据现场日志逐层排查。

## 2026-06-10 CST

- Objective: 在 `second_cross_cut` 中落地 hook-lift 关节限位约束 IK 预验证器，并在上挑阶段执行前接入工作流，提前拦截 J7 等关节逼近极限的轨迹。
- Work completed:
  1. 新增 `hook_lift_solver.py`，把上挑求解器独立放进 `cuttofo_skill_tofu_second_cross_cut` 包内，保持“逻辑自足 + 配置自足”。
  2. 求解器复用 `OfflineURDFKinematics + least_squares + make_safe_bounds`：
     - 关节原始限位优先读取 `arms.yaml` 中的 `joint_limits_deg`
     - 叠加 `hook_lift.safety_margin_deg`
     - 逐个 hook waypoint 做带 bounds 的 IK
  3. 增加段间 rollout 验证：
     - 对相邻 hook waypoints 之间做姿态球面插值 + 位置线性插值
     - 对每个中间采样点继续做 IK 检查
     - 这样不只验证 waypoint 本身可达，也验证段间连续过渡时不会提前撞 joint safe bound
  4. 在 `tofu_second_cross_cut_params.yaml` 的 `hook_lift` 段新增：
     - `safety_margin_deg`
     - `rollout_steps`
  5. 在 `tofu_second_cross_cut_workflow.py` 中接线：
     - 生成 `hook_waypoints` 后立即调用求解器
     - 若验证失败，则在 `hook_lift` 阶段直接 fail，避免进入真机 RT 执行后才急停
     - 若验证通过，则继续沿用现有单次 `move_rt_cartesian_path(...)` 连续执行，不改变原来的运动连续性
     - 额外输出每个 hook waypoint 的 `pos_err_mm / rot_err_deg / min_margin_deg` 调试日志
- Business logic impact:
  - `second_cross_cut` 现在在真正上挑前，会先离线验证这段 hook-lift 轨迹是否始终满足安全关节裕度。
  - 执行方式仍然是原来的单次 RT 笛卡尔路径调用，没有改成分段执行，也没有引入运动中停顿。
  - 若某轮上挑的 orientation phase 会把 J7 顶到极限附近，现在会在动作发出前就失败并给出诊断，而不是等真机急停。
- Problems encountered:
  1. `Write` 在较大块写入时再次出现参数丢失，因此本次实现按“小块创建 + 小块追加”的方式完成，避免一次性大段写入。
  2. 当前环境中 `apply_patch` 命令不可用，因此文件增量修改主要通过 `Edit` 和小块 shell append 完成。
- Resolution:
  - 按函数粒度分批写入 `hook_lift_solver.py`，再用 `Edit` 补全关键逻辑和 workflow 接线。
- Verification:
  - `python3 -m py_compile hook_lift_solver.py tofu_second_cross_cut_workflow.py tofu_second_cross_cut_config.py` 通过。
  - `colcon build --base-paths src/dexbot_middle_layer/CutTofo --packages-select cuttofo_skill_tofu_second_cross_cut` 通过。
- Unverified items:
  - 尚未做真机 hook-lift 复测，当前还没有现场确认 `safety_margin_deg=15` 和 `rollout_steps=15` 是否已经足够覆盖 J7 风险边界。
  - 当前求解器验证的是离线 IK 可达性与安全裕度，不直接控制 xCore 内部插补器；若后续仍出现执行侧极限贴边，需要再提高 rollout 密度或增加 hook waypoint 密度。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/hook_lift_solver.py`（新增）
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/cuttofo_skill_tofu_second_cross_cut/tofu_second_cross_cut_workflow.py`（修改）
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/tofu_second_cross_cut_params.yaml`（修改）
- Next steps:
  - 真机优先复测一次最容易触发 J7 逼近限位的上挑姿态，观察 workflow 是否在执行前正确拦截或通过。
  - 若验证失败过于保守，先调 `hook_lift.safety_margin_deg`，再考虑减少 `hook_target_plane_angle_deg` 或增加 orientation waypoint 数量。
  - 若真机仍在执行中出现贴边，再把 rollout 密度从 `15` 往上加，或把 hook 轨迹本身离散得更细。

## 2026-06-10 CST

- Objective: 修复 `second_cross_cut` 在容器检测正常、RT 轨迹仍持续执行时被工作流误判为 `cycle_timeout` 提前终止的问题。
- Work completed:
  1. 结合现场日志复盘，确认报错点不是 hook-lift IK，也不是容器检测失败，而是 `tofu_second_cross_cut_workflow.py` 在等待 `move_rt_cartesian_path` 返回时超时了。
  2. 复查实现链路：
     - `execute_second_cross_cut()` 最终把 `cut + hook + transfer + return_next_anchor` 全部拼成一次 RT 请求
     - `XcoreArmAdapter.move_rt_cartesian_path()` 仅通过 `_wait_node_future(..., timeout_s)` 等待服务 future 完成
     - 当前 `tofu_second_cross_cut_params.yaml` 的 `service_timeout_s` 只有 `120.0`
  3. 对照日志判断这是“等待时间不够”而不是“服务已返回失败”：
     - 任务是在 `restored perception prompt` 之后、orchestrator 立刻报 `cycle_timeout`
     - 说明 action 还卡在等待 xCore RT 服务返回，而不是业务逻辑提前 `_fail`
     - 容器检测日志一直在持续刷新，也说明 node 主线程还活着，只是本轮 RT 调用没在 120s 内结束
  4. 将 `tofu_second_cross_cut_params.yaml` 中的 `service_timeout_s` 从 `120.0` 提高到 `300.0`，给整条 `cut_down -> hook_lift -> transfer -> next_anchor` 的单次 RT 轨迹更充足的等待窗口。
- Business logic impact:
  - `second_cross_cut` 仍保持单次 RT 连续执行，不改变轨迹结构。
  - 现在 workflow 不会因为 120s 等待窗口过短，而把仍在正常执行的长轨迹误判为超时失败。
- Problems encountered:
  1. `second_cross_cut` 当前把多段动作拼成一条 RT 路径，时长天然比单轮 `cut_round` 更长；原先沿用 `120s` 超时窗口偏保守。
- Resolution:
  - 先把 skill 级 `service_timeout_s` 放宽到 `300s`，优先修正“误判超时”这一直接问题。
- Verification:
  - `python3 -m py_compile tofu_second_cross_cut_workflow.py tofu_second_cross_cut_node.py hook_lift_solver.py` 通过。
  - `colcon build --base-paths src/dexbot_middle_layer/CutTofo --packages-select cuttofo_skill_tofu_second_cross_cut` 通过。
- Unverified items:
  - 还没做真机复测，尚未拿到新的 `cycle_resp.success / executed_steps / elapsed_s` 日志确认 300s 窗口已足够。
  - `hand_eye_static_tf_publisher` 在整套 launch 被 orchestrator 主进程拉闸后重复 `rclpy.shutdown()` 的报错是关停阶段的次生噪声，不是这次 `second_cross_cut` 主失败根因。
- Files changed:
  - `src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/tofu_second_cross_cut_params.yaml`（修改）
  - `src/dexbot_middle_layer/CutTofo/.project-log/progress.md`（追记）
- Next steps:
  - 真机立刻复测当前 `round_2`，重点看这次是否不再出现 `TCUT-CYCLE-TIMEOUT`。
  - 若 300s 后仍超时，再把 RT 请求拆出更细的 elapsed 日志，确认究竟是 xCore 服务本身执行过慢，还是某段轨迹卡住未返回。


## 2026-06-11 CST (left handoff — debug_left_handoff 真机测试成功)

- Type: verification | calibration
- Status: complete
- Importance: critical
- Objective: from_euler 修复 + 新采 offset 后，真机复验 debug_left_handoff 是否到位。
- Work completed:
  1. **标定量采成功**：使用修复后的采集脚本重采 5 组 offset 样本。
     - 5 组 `derived_right_flange_target_offset` 均值 `[0.281105, -0.29242, 0.180583]`。
     - 均值已写入 `tofu_second_cross_cut_params.yaml` 的 `right_flange_target_offset`。
     - 用户在此基础上微调 X 值至 `0.286105`，最终运行值为 `[0.286105, -0.29242, 0.180583]`。
  2. **debug_left_handoff 真机测试通过**：左臂成功到达右臂刀面示教点，交接动作到位。
  3. **从均值到运行值的差异说明**：
     - 均值 `0.281105`（5 组样本计算）→ 运行值 `0.286105`（+5mm 微调）。
     - 用户手动微调 X 方向偏移量，推测是基于真机观察到的微小误差做了手动补偿。
- Problems encountered: 无（本次测试流程顺利）。
- Resolution: N/A。
- Verification:
  - `debug_left_handoff` 真机执行回显正常，左臂到达右臂刀面交接点。
- Unverified items:
  - 尚未关闭 `_DEBUG_STOP_AFTER_TRANSFER` 将左臂 handoff 接入完整 workflow。
  - 候选姿态只记录了 5 组，「同刀点、只变姿态」的一致性仍可进一步改善。
- Files changed:
  - `config/tofu_second_cross_cut_params.yaml` — `right_flange_target_offset` 更新
  - `config/left_flange_pose_candidates.yaml` — 5 组新采样本 + 均值
- Next steps:
  1. 确认左臂 handoff 到位稳定后 → `_DEBUG_STOP_AFTER_TRANSFER = False` → 接完整 workflow。
  2. 若后续精度仍不够 → 按「同刀点、只变姿态」重新规范示教流程，再采一批 offset。
  3. workflow 级联调：确认 transfer → reorient → left_handoff 全链路连续。


- Objective: 用户启动 `ros2 launch cuttofo_orchestrator tofu_workflow_execute.launch.py run_orchestrator:=false`，修复 3 个运行时问题。
- Work completed:
  1. **移除 cucumber_hold 残留**：从 `skills_bringup.launch.py` 删除 `cucumber_hold_server` include。cucumber_hold_node 持续发布 "cucumber" 到 `/cuttofu/vision/text_prompt`，与 handle_approach 的 "wooden cleaver handle" 互相覆盖，导致 SAM3 提示词错误。
  2. **修复相机无画面**：`tofu_workflow_execute.launch.py` 中 `show_camera_display` 默认值从 `"false"` 改为 `"true"`，与 vision_bringup 自身默认值一致。
  3. **修复 RealSense 分辨率**：`rs_color_profile` 从 `1280,720,30` 改为 `424x240x15`，`rs_depth_profile` 从 `1280,720,30` 改为 `640x480x15`，匹配 vision_bringup 默认值。
  4. **确认 cucumber_hold 是独立工作流**：cucumber 有自己的 `cucumber_skills_bringup.launch.py` 和 `cucumber_workflow_execute.launch.py`，与豆腐工作流完全独立。豆腐 `skills_bringup.launch.py` 不应包含 cucumber_hold。
- Problems encountered:
  - **colcon 无法发现 CutTofo 包**：`colcon list` 只找到 11 个包，`src/dexbot_middle_layer/CutTofo/` 下 17 个包全部缺失。`build/` 目录有 `COLCON_IGNORE` 标记。绕行方案：项目使用 `--symlink-install` + egg-link 指向 build 目录，手动同步 Python 源码到 build 目录即可生效；launch 文件是 symlink 链（install → build → source），编辑源文件直接生效。
- Files changed:
  - `skills_bringup.launch.py`：移除 cucumber_hold_server include
  - `tofu_workflow_execute.launch.py`：修复 show_camera_display、rs_color_profile、rs_depth_profile 默认值


## 2026-06-11 CST (per-cycle left handoff + 全流程 hook_lift IK 阻塞)

- Type: workflow | fix | bug | config | follow-up
- Status: partial（代码已合入；真机全流程未通过）
- Importance: high
- Reusable: yes
- Objective: 将 `second_cross_cut` 从「8 刀一条 RT、最后才 handoff」改为每轮 cut→hook→transfer 后 live-pose 左臂 handoff + 双臂并行回位；并现场验证 `entry=second_cut_prepare` 全流程。
- Work completed:
  1. **Workflow 按轮执行**（`tofu_second_cross_cut_workflow.py`）：
     - 删除 `all_waypoints` 跨轮累积 + 单次 `_run_rt`。
     - 每轮：`cycle_waypoints = cut + hook + transfer(+reorient)` → `_run_rt` → `_execute_left_handoff_live`（读真机 TCP/法兰）→ `_parallel_cycle_return`。
     - 非末轮并行：左臂 `left_wait_joint_positions` + 右臂 `_next_anchor` RT；末轮并行：左 wait + 右 `human_wait`。
     - `left_handoff` 关闭时：跳过 handoff，仅右臂串行回位。
     - `_DEBUG_STOP_AFTER_TRANSFER` 仍只跑第 1 轮 RT 后返回，不 handoff。
  2. **配置**（`tofu_second_cross_cut_params.yaml`）：
     - 新增 `human_wait.left_wait_joint_positions`（示教 27.9°/21°/-22.4°/60.6°/14.1°/14.5°/15.9° 转弧度）、`left_wait_joint_speed: 0.3`。
     - `hook_lift.safety_margin_deg`：`5.0` → `3.0`（用户要求放宽关节裕度）。
  3. **`workflow_summary`** 增加 `left_handoff`、`parallel_return` stages。
  4. **构建**：`colcon build --symlink-install --paths .../cuttofo_skill_tofu_second_cross_cut` 通过。
- Business logic impact:
  - v2 主路径 `second_cross_cut` 执行语义变更：每刀转运后左臂上刀一次，再双臂并行回位（刮条动作仍跳过）。
  - 与旧记录「整条 RT 连续 cut+hook+transfer+next_anchor」不一致；以当前源码为准。
- Problems encountered:
  1. **全流程真机阻塞于 hook_lift IK 预检**（`entry=second_cut_prepare`，2026-06-11 15:26 日志）：
     - `prepare:second_cut` 成功（`seeds=63 valid=2`）。
     - `second_cross_cut` 在 **cycle 1/8、真机未动** 时失败：
       - 首次（`safety_margin_deg=5`）：`waypoint 2` — `pos_err=7.63mm` `rot_err=6.49deg` `min_margin=0°`。
       - 改裕度 3° 后：`pos_err=2.85mm` `rot_err=2.87deg` `min_margin=0°`（有改善仍失败）。
     - 代码阈值（`hook_lift_solver.py`）：`POS_TOL_M=0.1mm`，`ROT_TOL_RAD≈0.06°`，严于现场误差。
  2. **per-cycle handoff 真机未验证**：IK 预检在前，左臂 handoff / 并行回位尚未跑到。
- Resolution:
  - hook_lift IK：**未解决**；裕度 3° 不足，需调轨迹参数和/或放宽 `POS_TOL`/`ROT_TOL`，或调 `second_cut` prepare offset。
- Verification:
  - 静态：`py_compile` + `colcon build` 通过。
  - 真机：`debug_left_handoff` 此前已通过 ✅；本次 `second_cross_cut:round_2` **失败** ❌（hook_lift IK）。
- Unverified items:
  - 每轮 live-pose handoff + 并行回位（8 次 handoff 日志）。
  - `safety_margin_deg=3` 是否应再降或改 IK 容差。
- Files changed:
  - `cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/.../tofu_second_cross_cut_workflow.py`
  - `cuttofu_skills/cuttofo_skill_tofu_second_cross_cut/config/tofu_second_cross_cut_params.yaml`
- Next steps:
  1. 放宽 `hook_lift_solver.py` 的 `POS_TOL_M`/`ROT_TOL_RAD`，或调 `hook_target_plane_angle_deg` / `hook_dy_m` / `second_cut.target_offset_m`。
  2. prepare 完成后跑 `debug_hook_lift` 定位 orient waypoint 2。
  3. IK 通过后复测 `second_cross_cut`，确认每轮 `left handoff target candidate=` ×8。
