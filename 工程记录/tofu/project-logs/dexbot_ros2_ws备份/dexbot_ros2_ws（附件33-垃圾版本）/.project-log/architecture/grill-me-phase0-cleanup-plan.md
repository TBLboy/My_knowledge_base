# Phase 0: 清理计划（精确清单）

> 状态：grill-me 讨论产物，已确认
> 日期：2026-05-26

---

## 原则

- 只保留切豆腐（cuttofo_xcore）项目及其直接依赖
- 清理后 `colcon build` 必须通过
- 清理后切豆腐（抓刀 + Phase2切割）行为完全不变
- 底层原子控制器（`dexbot_bottom_layer`）保持稳定，只删明确不用的 Lbot 旧控制器

---

## Step 0: 先做 git commit 保存当前状态

```bash
git add -A && git commit -m "pre-cleanup: snapshot before Phase 0 cleanup"
```

---

## Step 1: 删除整个包/目录

| # | 路径 | 原因 | 风险评估 |
|---|------|------|----------|
| 1.1 | `src/cuttofo_lbot/` | 旧 Lbot 版切豆腐，已被 `cuttofo_xcore` 取代，无任何 import 引用 | ✅ 安全 — grep 确认 cuttofo_xcore 不 import cuttofo_lbot |
| 1.2 | `src/dexbot_high_layer/` | 切黄瓜遗留代码，与切豆腐无关 | ✅ 安全 — 无切豆腐代码引用 |
| 1.3 | `src/gui_backup/` | 两份旧 GUI 备份，未被任何构建系统引用 | ✅ 安全 — 独立目录，无引用 |
| 1.4 | `src/config1/` | 旧版标定结果，已被 `src/config/` 取代 | ✅ 安全 — 无代码引用 |

---

## Step 2: 删除 CutTofo 死代码（保留 3+1 个活跃文件）

### 2.1 删除整个 `CutTofo/sdk/` 目录

路径：`src/dexbot_middle_layer/CutTofo/sdk/`

包含 11 个旧版 SDK 脚本（全部未被 cuttofo_xcore 引用）：
- `demo_cut_smooth_pro.py` (3339 行)
- `xcore_cut_tofu_vertical.py` (1466 行)
- `demo_cut_smooth_up.py`
- `xcore_cut_tofu_vertical_only.py`
- `xcore_cut_tofu.py` (1317 行)
- `demo_cut_move.py`
- `demo_cut_move_linear.py`
- `demo_flange_then_base_loop.py`
- `demo_right_arm_points.py`
- `demo_set_angle.py`
- `demo_set_angle_and_distance.py`
- `demo_tool_frame_offset_move.py`
- `xocre_move_base_z_only.py`

### 2.2 删除 `CutTofo/ros/` 中死源文件

保留 4 个活跃文件：
- `xcore_follow_tcp_chain_node_movej.py` — 被 `cuttofu_phase1_motion.launch.py` 启动
- `xcore_monitor_handle_sequence_node.py` — 被 `cuttofu_phase1_motion.launch.py` 启动
- `cut_tofu_object_recognition_node.py` — 被 `cuttofu_phase1_motion.launch.py` 启动
- `cut_tofu_phase3_lib.py` — 被前两个 import

删除死源文件（对应 setup.py 中 15 个死 entry point）：
- `demo_follow_tcp_node.py`
- `demo_monitor_node.py`
- `demo_xcore_movel.py`
- `demo_xcore_movej.py`
- `demo_xcore_rotate_pos_y_tcp.py`
- `demo_xcore_rotate_elbow_range.py`
- `read_xcore_current_pose_6d.py`
- `demo_ar5_left_tcp_y_ground_angle.py`
- `xcore_follow_tcp_node.py`
- `xcore_follow_tcp_chain_node.py`
- `xcore_follow_tcp_chain_node_new.py`
- `xcore_follow_tcp_chain_node_parallel.py`
- `xcore_monitor_node.py`
- `xcore_monitor_handle_sequence_node_parallel.py`

### 2.3 从 `dexbot_middle_layer/setup.py` 中删除死 entry points

需要删除的 console_scripts（保留 3 个 + SAM3/pose_estimator）：
```python
# DELETE these:
"object_follow_tcp_node = CutTofo.ros.demo_follow_tcp_node:main",
"xcore_follow_tcp_node = CutTofo.ros.xcore_follow_tcp_node:main",
"xcore_follow_tcp_chain_node = CutTofo.ros.xcore_follow_tcp_chain_node:main",
"xcore_follow_tcp_chain_node_new = CutTofo.ros.xcore_follow_tcp_chain_node_new:main",
"xcore_follow_tcp_chain_node_parallel = CutTofo.ros.xcore_follow_tcp_chain_node_parallel:main",
"object_monitor_node = CutTofo.ros.demo_monitor_node:main",
"xcore_monitor_node = CutTofo.ros.xcore_monitor_node:main",
"xcore_monitor_handle_chain_node = CutTofo.ros.xcore_monitor_node:main",
"xcore_monitor_handle_sequence_node_parallel = CutTofo.ros.xcore_monitor_handle_sequence_node_parallel:main",
"demo_xcore_movel = CutTofo.ros.demo_xcore_movel:main",
"demo_xcore_movej = CutTofo.ros.demo_xcore_movej:main",
"demo_xcore_rotate_pos_y_tcp = CutTofo.ros.demo_xcore_rotate_pos_y_tcp:main",
"demo_xcore_rotate_elbow_range = CutTofo.ros.demo_xcore_rotate_elbow_range:main",
"read_xcore_current_pose_6d = CutTofo.ros.read_xcore_current_pose_6d:main",
"demo_ar5_left_tcp_y_ground_angle = CutTofo.ros.demo_ar5_left_tcp_y_ground_angle:main",
```

### 2.4 从 `dexbot_middle_layer/setup.py` 中删除死 Python import (packages)

先检查 `setup.py` 的 `packages=find_packages()` 是否还在发现 CutTofo 子包，确认删除源文件后不再报错。

---

## Step 3: 删除 dexbot_middle_layer 中其他死代码

| # | 文件 | 原因 |
|---|------|------|
| 3.1 | `dexbot_middle_layer/pick_place_action_server.py` | 旧抓取 action server，不用 |
| 3.2 | `dexbot_middle_layer/motion/skills/pick_and_place.py` | 被上面的 server 引用，server 删了就没用了 |
| 3.3 | `dexbot_middle_layer/planning/policy/orange_heart_policy.py` | 死策略文件 |
| 3.4 | `dexbot_middle_layer/setup.py` 中 `pick_place_action_server` entry point | 对应删除 |

---

## Step 4: 删除 dexbot_bottom_layer 中旧 Lbot 控制器

| # | 路径 | 原因 |
|---|------|------|
| 4.1 | `dexbot_bottom_layer/lbot_controller/` | 旧 Lbot 控制器，cuttofo_xcore 不 import |
| 4.2 | `dexbot_bottom_layer/lbot_catch/` | Lbot motion/IK 工具库 |
| 4.3 | `dexbot_bottom_layer/setup.py` 中 `lbot_controller_node` entry point | 对应删除 |

**保留的 SDK 目录（不动）**：
- `xcoresdk_python-v0.5.1.ar_12/` — xCore SDK, cuttofo_xcore 依赖
- `linkerbot-python-sdk/` — Linkerbot SDK, 手部控制依赖

---

## Step 5: 删除 dexbot_bringup 中无关 launch 文件

| # | 文件 | 原因 |
|---|------|------|
| 5.1 | `dexbot_bringup/launch/dexrob_full.launch.py` | 水果抓取系统（pick-and-place with SAM3 "orange"），与切豆腐无关 |
| 5.2 | `dexbot_bringup/launch/dexrob_hand_only.launch.py` | 独立手部测试，与切豆腐无关 |

**保留**：
- `dual_xcore_controllers.launch.py` — 被 `phase1_monitor_node.py` 以子进程启动
- `calibration_manual_withUI.launch.py` — 手眼标定，标定结果被切豆腐使用

---

## Step 6: 清理 dexbot_toolbox 旧 GUI

| # | 内容 | 原因 |
|---|------|------|
| 6.1 | `dexbot_toolbox/gui/arm_hand_gui.py` (3482 行) | 旧单体 GUI，已被 `src/gui/` 取代 |
| 6.2 | `dexbot_toolbox/gui/hand_eye_replay_gui.py` | 旧标定回放 GUI |
| 6.3 | `dexbot_toolbox/setup.py` 中对应的 entry points | 对应删除 |

---

## Step 7: 验证

```bash
# 1. 确认无残留 import 引用
grep -r "cuttofo_lbot[^_]" src/ --include="*.py" --include="*.launch.py"
grep -r "dexbot_high_layer" src/ --include="*.py" --include="*.launch.py"
grep -r "from CutTofo\|import CutTofo" src/cuttofo_xcore/ --include="*.py"
grep -r "demo_cut_smooth_pro\|xcore_cut_tofu_vertical\|xcore_cut_tofu[^_]" src/cuttofo_xcore/ --include="*.py"

# 2. colcon build 验证
colcon build --symlink-install

# 3. 确认受影响的包都可 build
colcon build --packages-select dexbot_middle_layer dexbot_bottom_layer dexbot_bringup cuttofo_xcore

# 4. git commit
git add -A && git commit -m "Phase 0: remove legacy/dead code, keep only cuttofo tofu cutting project"
```

---

## 预计效果

| 指标 | 清理前 | 清理后 | 减少 |
|------|--------|--------|------|
| ROS2 包 | 17 | ~12 | ~30% |
| Python 文件 | ~310 | ~230 | ~26% |
| 代码行数 | ~95,000 | ~70,000 | ~26% |
| >1000 行文件 | 6+ | ~4 | ~33% |
| 死 entry point | 未知 | 0 (22+ 删除) | — |
| 备份目录 | 3 | 0 | 100% |

---

## 删除汇总对照

| 类别 | 项目 | 说明 |
|------|------|------|
| 整包删除 | `cuttofo_lbot/` | 旧 Lbot 切豆腐 |
| 整包删除 | `dexbot_high_layer/` | 切黄瓜 |
| 目录删除 | `gui_backup/` | 两份 GUI 备份 |
| 目录删除 | `config1/` | 旧标定结果 |
| SDK 删除 | `CutTofo/sdk/` | 11 个旧 SDK 脚本 |
| ROS 死代码 | `CutTofo/ros/` (14 文件) | 15 个死 entry point 对应源文件 |
| 死代码 | `dexbot_middle_layer/` (3 文件) | pick_place server + skill + policy |
| 旧控制器 | `dexbot_bottom_layer/lbot_controller/` + `lbot_catch/` | 旧 Lbot |
| Launch 删除 | `dexrob_full.launch.py` + `dexrob_hand_only.launch.py` | 无关系统 |
| 旧 GUI | `dexbot_toolbox/gui/arm_hand_gui.py` + `hand_eye_replay_gui.py` | 旧单体 GUI |
