# Current Session

## Last Updated

- 2026-06-15 CST (下午)

## Current Objective

- **Online IK 多候选求解 — 方案 C 实现与测试** — 解决 `move_cartesian` 刮豆腐问题，Phase 1：单次 `compute_ik` + `move_to_joints` 执行

## Current Business Logic Position

- Main path: `tofu_prepare` prepare 阶段 online IK 优化中
- Active branch: `cut_to_fo_featrue`

## Work in Progress

### 方案 C 实现步骤

**问题：**
1. 放刀时刀刮蹭豆腐表面（下刀挂层）
2. 手动回等待位置时碰倒豆腐

**根因：**
- 层面 1：`move_cartesian` 笛卡尔直线运动穿过豆腐表面
- 层面 2：单次 IK 解关节构型可能肘/腕离豆腐太近

**方案 C 设计：**
- 在线路径改用：`compute_ik`（获取关节解） → `move_to_joints`（关节空间弧线运动）
- 使用 `motion_planner_node` 的 `/dexbot/motion/compute_ik` 服务（单次调用，10-15s）
- 控制器硬件标定运动学保证 IK 精度，关节空间运动避免刮蹭

**实现完成：**

1. **xcore_arm_adapter.py** ✓：
   - 新增 `ComputeIK` 导入
   - 新增 `_compute_ik_cli` 客户端（连接 `/dexbot/motion/compute_ik`）
   - `connect()` 中添加 `compute_ik_ok` 检查
   - 新增 `compute_ik(target_pos, target_R, seed_joints)` 方法

2. **tofu_prepare_workflow.py** ✓：
   - 在线路径重构（lines 142-198）
   - 替换为：`compute_ik` → `move_to_joints` → `verify_arrival` → TCP 验证
   - 失败时仍 fallback 到离线 URDF IK（现有逻辑保留）

3. **编译** ✓：`colcon build --packages-select cuttofo_skill_tofu_prepare --symlink-install --paths ...` 成功（0.65s）

**状态：** 代码实现完成，编译成功，等待真机测试

**计划文档：** `/home/tbl/.claude/plans/online-ik-urdf-ik-sharded-sparkle.md`

---

## Previous Work Completed (2026-06-15 CST 上午)

## Current Objective

- **Prepare 阶段 Online IK（move_cartesian 方法）** — 使用控制器硬件标定运动学直接做笛卡尔运动，绕过 URDF — **已实现并真机验证通过**

## Current Business Logic Position

- Main path: `tofu_prepare` prepare 阶段在线 IK 已跑通
- Active branch: `cut_to_fo_featrue`

## Completed This Session

### Online IK via move_cartesian（核心改动）

- **设计转变**：放弃之前的 `motion_planner_node` + `WeightedIK` 方案（从未实际实现），改用 `move_cartesian(target_is_flange=True)` 直接调用控制器内部 IK
- **核心优势**：控制器使用硬件标定运动学做 IK，无 URDF 偏差，无网络延迟瓶颈
- **已有成功案例**：`tofu_second_cross_cut_workflow.py` line 898 已使用相同模式

### 实现细节

- **tofu_prepare_params.yaml**：新增 `ik_mode: online`（默认）、`cartesian_speed`、`cartesian_timeout_s`、`online_position_tolerance_mm`
- **tofu_prepare_workflow.py**：
  - 在线路径：计算 flange_target_pos → 构造 Pose → `arm.move_cartesian(target_is_flange=True)` → 验证 TCP 位姿误差
  - 成功时直接 return，跳过离线 URDF IK
  - 失败时自动回退到现有离线多候选 URDF IK（代码完全保留）
- **TCP offset 逻辑**：`flange_target_pos = target_pos - target_R @ tcp_offset`，TCP 姿态=法兰姿态（仅平移偏移）
- **导入修复**：添加 `from scipy.spatial.transform import Rotation as R`

### 编译问题修复

- **根因**：`cuttofo_skill_tofu_prepare` 包嵌套在 `src/dexbot_middle_layer/CutTofo/` 下，顶层 `dexbot_middle_layer/package.xml` 遮蔽了 colcon 递归发现
- **修复**：使用 `colcon build --packages-select cuttofo_skill_tofu_prepare --symlink-install --paths src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare` 编译
- **效果**：egg-link → symlink 到源码目录，修改即时生效

## Key Files Changed

- `cuttofu_skills/cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml` — 新增 ik_mode 等参数
- `cuttofu_skills/cuttofo_skill_tofu_prepare/cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py` — 在线路径 + fallback 逻辑

## Verification

- `colcon build` ✓（需 `--paths` 指定嵌套路径）
- Python 语法检查 ✓
- ROS2 环境导入 ✓
- **真机全流程测试 ✓** — 在线 IK 跑通

## Next Steps

1. 观察在线 IK 位姿精度（`position_error_mm` 日志）
2. 如果精度不够，调整 `online_position_tolerance_mm` 或检查 vision 目标
3. 考虑整理目录结构（CutTofo 包移到 `src/` 顶层）解决 colcon 发现问题

## Additional Work Completed

### 编译问题文档化

- **位置**：`.project-log/debugging/known-issues.md`
- **内容**：添加"Colcon 编译嵌套包发现失败（已解决）"条目
- **覆盖**：根因分析、诊断步骤、解决方案命令、symlink-install 效果、长期建议
- **目的**：方便后续遇到相同问题快速查阅解决

### 启动偶发崩溃（未解决）

- **症状**：`tofu_prepare_node` 启动时立即 exit code -11（SIGSEGV）
- **状态**：偶发，用户判断可能无需立即处理
- **记录时间**：2026-06-15 14:53 CST
- **备注**：退出码 -11 通常为内存访问错误或底层库 crash，暂不深入排查
