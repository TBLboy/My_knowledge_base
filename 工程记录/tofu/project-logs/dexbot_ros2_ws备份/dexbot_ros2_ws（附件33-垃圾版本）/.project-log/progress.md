---

## 2026-05-28 16:40 Local Time — BL-004 简化切割逻辑：下切→回刀→偏移→归位

- Objective: 将黄瓜切割逻辑简化为三段式：下切 → 回刀 → 偏移 → 回到 prepare，与 cuttofo 切豆腐流程一致
- Work completed:
  - `SliceCucumber` ActionServer 改成两段 RT 路径：下切到 cut_end → 回到当前 anchor
  - `AdvanceKnife` ActionServer 改成两段 RT 路径：回当前 Z → 沿 X 偏移到下一刀
  - 编排层（orchestrator）传参简化：移除 cut_height/lift_height/return_speed 等不再需要的参数
  - YAML 配置整理：移除旧参数，新增 `cut_direction` 可选 base_z_negative/base_y/base_x
- Business logic impact: 切割循环简化为三段式，与 cuttofo 方案一致
- Problems encountered: 跟踪仓库（切黄瓜项目跟踪）与主仓库通过 symlink 关联，git add 时需要从跟踪仓库执行
- Resolution: 切换到跟踪仓库目录完成 commit
- Verification: python3 -m py_compile 三处修改文件均通过
- Unverified items: 待真机验证切割轨迹
- Files changed:
  - `src/cutcucumber_xcore/cutcucumber_middle/manipulation_skills/slice_cucumber/slice_cucumber/node.py`
  - `src/cutcucumber_xcore/cutcucumber_middle/manipulation_skills/advance_knife/advance_knife/node.py`
  - `src/cutcucumber_xcore/cutcucumber_high/cutcucumber_high/node.py`
  - `src/cutcucumber_xcore/config/cutcucumber_config.yaml`
- Commit: `6797475` (branch: cut_tofu_cucumber, 跟踪仓库)
- Next steps: 待机验证后继续下一步切割逻辑调试

---

## 2026-05-28 17:05 Local Time — 补切割深度参数 + 下切模式改为阻抗优先

- Objective: 修复切割深度不可配置、下切控制模式为位置模式（而非阻抗优先）的问题
- Work completed:
  - YAML 新增 `cut_depth` 独立参数，删除冗余的 `cut_through_overtravel`
  - `plan_cut_pose`：`cut_through_distance = cut_depth`（不再叠加 overtravel）
  - `slice_cucumber`：`cut_through_distance` 优先取 goal 字段，为 0 时回退本地 `cut_depth`
  - `slice_cucumber`：`use_impedance=False` 硬编码 → 改为**阻抗优先 + 位置回退**两轮尝试（参考 cuttofo）
  - YAML 新增 `prefer_rt_impedance` / `fallback_to_rt_position` / `stiffness` 配置
  - 默认下刀方向改为 `base_y`（base Y- 下切）
  - 编排层传参同步更新
- Business logic impact: 切割深度由 `cut_depth` 统一控制；下切 RT 模式可配置
- Problems encountered: None
- Resolution: Not applicable
- Verification: python3 -m py_compile 三个修改文件全部通过
- Unverified items: 需真机验证阻抗 vs 位置模式的切割效果
- Files changed:
  - `src/cutcucumber_xcore/cutcucumber_middle/manipulation_skills/slice_cucumber/slice_cucumber/node.py`
  - `src/cutcucumber_xcore/cutcucumber_middle/planning_skills/plan_cut_pose/plan_cut_pose/node.py`
  - `src/cutcucumber_xcore/cutcucumber_high/cutcucumber_high/node.py`
  - `src/cutcucumber_xcore/config/cutcucumber_config.yaml`
- Next steps: 真机验证后继续下一步任务

---

## 2026-05-28 17:25 Local Time — BL-001 左手按压：固定法兰姿态 + 两阶段垂直下压

- Objective: 调整左手按黄瓜逻辑，使目标法兰姿态来自配置参数，并采用先到上方点、再垂直下压的两阶段策略
- Work completed:
  - 配置新增 `left_hand.target_flange_quat_xyzw`：固定目标法兰姿态，不再使用 prepare 位姿法兰姿态
  - 配置新增 `left_hand.vertical_press_distance`：approach 到 target 的垂直下压距离 a
  - `XCoreArmClient` 加载目标法兰姿态和下压距离参数
  - `move_to_pose` 左手路径改为：wait → approach 点 IK（固定法兰姿态）→ MoveJoints 到 approach → RT Cartesian Segment 沿左臂 base Y+ 直线下压 a
  - 新增 `capture_left_flange_pose` 脚本：连接左臂、读取当前关节、FK 算当前法兰姿态、写入 config 的 `target_flange_quat_xyzw`
- Business logic impact: BL-001 左手按压逻辑更新为固定姿态标定 + 两阶段按压，降低横向推开黄瓜风险
- Problems encountered: None
- Resolution: Not applicable
- Verification: python3 -m py_compile 对修改文件全部通过
- Unverified items: 需真机验证目标姿态采集、approach IK、垂直下压方向/距离
- Files changed:
  - `src/cutcucumber_xcore/config/cutcucumber_config.yaml`
  - `src/cutcucumber_xcore/cutcucumber_middle/motion_skills/move_to_pose/move_to_pose/xcore_arm_client.py`
  - `src/cutcucumber_xcore/cutcucumber_middle/motion_skills/move_to_pose/move_to_pose/node.py`
  - `src/cutcucumber_xcore/cutcucumber_middle/motion_skills/move_to_pose/move_to_pose/capture_left_flange_pose.py`
  - `src/cutcucumber_xcore/cutcucumber_middle/motion_skills/move_to_pose/setup.py`
- Next steps: 运行 `ros2 run cutcucumber_move_to_pose capture_left_flange_pose` 采集姿态，然后真机验证两阶段按压

---

## 2026-05-26 17:00 Local Time — 整体路线图与中层方案归档

- Objective: 将完整路线图、中层 Skills 布局、Resource 管理方案归档为文档
- Work completed:
  - 创建 `docs/REFACTORING_ROADMAP.md` — 完整路线图文档
  - 详细记录 4 个 Phase 的逐步骤执行路径、时间预估、验证标准
  - 明确中层 Resource 管理方案：基于 namespace 的隐式管理，不做 Resource Manager
  - 明确 Skill 实现模式：每个 skill 直接继承 Node + ActionServer（暂不依赖 BaseSkill）
  - 更新 `.project-log/current-session.md`
- Business logic impact: 无
- Files changed:
  - `docs/REFACTORING_ROADMAP.md` (new)
  - `.project-log/current-session.md` (updated)
- Next steps: 等待用户确认后执行 Phase 1
