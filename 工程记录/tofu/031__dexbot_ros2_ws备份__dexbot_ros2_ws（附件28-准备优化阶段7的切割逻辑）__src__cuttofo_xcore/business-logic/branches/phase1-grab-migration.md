# Branch: Phase1 Grab-Knife Migration

## Status

- testing

## Purpose

Migrate classmate's verified grab-knife code into cuttofo_xcore as independent nodes with a lifecycle wrapper, enabling one-lifecycle execution: auto-grab → clean resource release → broadcast `/task/phase1_complete` → self-exit → Phase1 monitor launches Phase2.

## Start Node

- PHASE_IDLE (demo entry point)

## Target Node

- PHASE_2_MOVE_TO_PREPARE (after `/task/phase1_complete` received by Phase1 monitor)

## Background

The original Phase1 only waits for an external `/knife_grabbed` signal. The classmate has a complete, verified 3-phase grab-knife system (recognition → 5-waypoint approach → O6 grasp → retract → joint home). We migrate this code into our workspace to enable a fully automated demo: the classmate's code runs independently, completes the grab, cleans up all resources, signals completion, and exits — then our Phase2 takes over.

## Migration Principle

- **Code migration only, zero logic changes**: Classmate's code is already verified working; we only relocate files, not modify behavior
- **Independent runtime environment**: Classmate's nodes run in a subprocess; resource cleanup guaranteed by process exit
- **No topic name changes**: Use classmate's native `/task/phase1_complete` as the completion signal
- **SAM3 prompt handling — NO switching logic**:
  - Classmate's code may internally switch SAM3 prompts during grab execution, but this has zero impact on our Phase2
  - After lifecycle subprocess exits, `cuttofu_phase2.launch.py` launches a **brand-new** `sam3_detector_node` with `text_prompt="豆腐"` (hardcoded in launch file)
  - Process isolation guarantees clean state: subprocess death = all classmate nodes die = no residual prompt state
  - **Do NOT modify classmate's prompt switching**: would break verified code, our SAM3 doesn't support multi-prompt syntax, adds unnecessary settle time

## Architecture: Two Independent Processes

```
┌───────────────────────────────────────┐   ┌───────────────────────────────────────┐
│  Process A: 同学抓刀 (Terminal G)       │   │  Process B: 切豆腐代码 (Terminal M)      │
│                                       │   │                                       │
│  cuttofu_phase1_grab.launch.py        │   │  cuttofu_phase1_monitor.launch.py     │
│    → phase1_grab_lifecycle_node.py    │   │    → phase1_monitor_node              │
│      → subprocess:                    │   │      subscribe /task/phase1_complete  │
│        cuttofu_phase1_grab_internal   │   │                                       │
│        .launch.py (一行启动全部)       │   │                                       │
│        ├─ RealSense camera            │   │                                       │
│        ├─ SAM3 (wooden cleaver)       │   │                                       │
│        ├─ pose_estimator              │   │                                       │
│        ├─ cut_tofu_object_recognition │   │                                       │
│        ├─ xcore_monitor_handle_seq    │   │                                       │
│        └─ xcore_follow_tcp_chain_movej│   │                                       │
│            ↓                          │   │                                       │
│         抓刀完成 → /task/phase1_complete  │   │                                       │
│      → lifecycle wrapper 收到信号       │───→ 收到信号 → buffer 0.5s                │
│      → 杀子进程 (全部节点死光)          │   │    → subprocess:                      │
│      → 广播 /task/phase1_complete ×5s  │   │      ros2 launch                     │
│      → lifecycle wrapper 自杀          │   │      cuttofu_phase2.launch.py         │
│                                       │   │      ├─ xcore_controller_node         │
│  资源: 0 残留 (进程/GPU/CAN全部释放)    │   │      ├─ RealSense camera (new)         │
│                                       │   │      ├─ SAM3 "豆腐" (new)              │
│                                       │   │      ├─ pose_estimator (new)          │
│                                       │   │      ├─ tofu_state_node               │
│                                       │   │      ├─ knife_prepare_action_server   │
│                                       │   │      ├─ knife_cut_action_server       │
│                                       │   │      └─ phase_manager_node            │
│                                       │   │           ↓                          │
│                                       │   │      Phase2→3→4→5→6→7→DONE            │
│                                       │   │                                       │
│  唯一通信: /task/phase1_complete (Bool) │   │  资源: 全新创建，零耦合                 │
└───────────────────────────────────────┘   └───────────────────────────────────────┘
```

### Logic Path (text)

```text
PHASE_IDLE
  → [Terminal G] ros2 launch cuttofo_xcore cuttofu_phase1_grab.launch.py
    → phase1_grab_lifecycle_node.py (wrapper)
      → subprocess: ros2 launch cuttofo_xcore cuttofu_phase1_grab_internal.launch.py
        → RealSense camera
        → SAM3 (wooden cleaver handle)
        → pose_estimator → /objects_with_pose
        → cut_tofu_object_recognition_node → lock handle → /task/handle_goal_body
        → xcore_monitor_handle_sequence_node → 5-waypoint approach → /follow/target_pose
        → xcore_follow_tcp_chain_node_movej → execute move → O6 grasp → retract → joint home
        → Phase1 complete → publish /task/phase1_complete=true
      → Lifecycle wrapper receives signal
      → Kill subprocess (all nodes die: camera + SAM3 + pose_est + rec + mon + follow)
      → Broadcast /task/phase1_complete (1Hz, 5s)
      → Lifecycle wrapper self-exits
  → [Terminal M] ros2 launch cuttofo_xcore cuttofu_phase1_monitor.launch.py
    → phase1_monitor_node subscribes /task/phase1_complete
    → Receives signal → buffers 0.5s
    → Spawns: ros2 launch cuttofo_xcore cuttofu_phase2.launch.py start_phase:=PHASE_2_MOVE_TO_PREPARE
      → xcore_controller_node (arm services: /arm_r/robot/*)
      → RealSense camera (new instance)
      → SAM3 "豆腐" (new instance, fresh prompt)
      → pose_estimator (new instance)
      → tofu_state_node → knife_prepare_action_server → knife_cut_action_server → phase_manager_node
      → Phase2→3→4→5→6→7→DONE
  → PHASE_2_MOVE_TO_PREPARE
```

## Execution Chain

### Step 1: Dependency Preparation

1. Copy `ObstacleBox.msg` and `TableWorkspace.msg` from classmate's `dexbot_interfaces_mid/msg/` to ours
2. Update `dexbot_interfaces_mid/CMakeLists.txt` to include new messages
3. `colcon build --packages-select dexbot_interfaces_mid`
4. Verify: `ros2 interface show dexbot_interfaces_mid/msg/ObstacleBox` succeeds

### Step 2: Code Migration

1. Copy entire `CutTofo/` directory from classmate's `src/dexbot_middle_layer/CutTofo/` to ours
2. Verify file integrity: `diff -r` between source and destination
3. Preserve optimized follow execution logic; apply project-specific compatibility only where required (calibration YAML compatibility, workspace-relative paths, Phase1 parameter chain)

### 2026-05-21 Optimized Follow Replacement

- Previous hash comparison against backup copy was misleading — it was also an old version.
- Full replacement of `xcore_follow_tcp_chain_node_movej.py` with student's actual (1) version.
- Core additions: `sequence_skip_joint_converge_wait`, `target_pose_skip_joint_converge_wait`, `move_abs_joints_skip_joint_converge_wait` → eliminates 5-9s idle delays per waypoint.
- Phase1 cleanup (toolset restore + stop + NrtCommandMode) in disconnect() manually preserved.
- Parameters aligned: `y_before=0.13`, `y_step=0.11`, `O6=0,0,80`, `target_y=-0.02`.
- Verification: Python compile and `colcon build` passed.
- Remaining status: hardware validation pending.

### Step 3: Internal Launch File (Grab Pipeline)

Create `cuttofu_phase1_grab_internal.launch.py`:

All nodes needed for classmate's grab-knife execution in ONE launch file:
1. RealSense camera (rs_launch.py via IncludeLaunchDescription)
2. SAM3 detector (wooden cleaver handle prompt)
3. pose_estimator
4. cut_tofu_object_recognition_node
5. xcore_monitor_handle_sequence_node
6. xcore_follow_tcp_chain_node_movej (embedded xCore SDK, direct TCP to robot)

### Step 4: Lifecycle Wrapper Node

Modify `phase1_grab_lifecycle_node.py`:
1. **Launch phase**: Single subprocess — `ros2 launch cuttofo_xcore cuttofu_phase1_grab_internal.launch.py`
2. **Wait phase**: Subscribe to `/task/phase1_complete`, wait for `Bool(data=true)`
3. **Cleanup phase**: Send SIGTERM to subprocess → all ROS nodes die (camera, SAM3, pose_est, rec, mon, follow → all released)
4. **Broadcast phase**: Publish `/task/phase1_complete` at 1Hz for 5 seconds (lifecycle wrapper is the ONLY node left after subprocess kill)
5. **Exit phase**: `sys.exit(0)`

### Step 5: Launch File (User Entry Point)

`cuttofu_phase1_grab.launch.py` (already exists): launches lifecycle wrapper with all parameters

### Step 6: Phase1 Monitor Update

Modify `phase1_monitor_node.py`:
1. Change subscription from `/knife_grabbed` to `/task/phase1_complete`
2. Keep existing logic: wait → buffer 0.5s → spawn Phase2
3. Phase2 launch includes `xcore_controller_node` (via dual_xcore_controllers.launch.py or inline) for arm service layer

### Step 7: Phase2 Launch Update

Modify `cuttofu_phase2.launch.py`:
1. Add `xcore_controller_node` launch (provides `/arm_r/robot/get_state`, `/arm_r/robot/move_joints`, `/arm_r/robot/move_rt_cartesian_path`, `/arm_r/robot/enable_arm`)
2. Must be in `/arm_r` namespace (XcoreArmAdapter connects to `/arm_r/robot/*`)
3. Parameters: robot_ip, arm_type, xcore_sdk_root, arm_backend:=xcore, auto_confirm:=true
4. Hand settings: enable_internal_hand:=false (user uses external hand CAN bridge)

### Step 8: setup.py Update

Add new entry_points:
- `phase1_grab_lifecycle_node = cuttofo_xcore.phase1_grab_lifecycle_node:main`

### Step 9: Build & Verify

1. `colcon build --packages-select cuttofo_xcore`
2. Verify all nodes start: `ros2 run cuttofo_xcore phase1_grab_lifecycle_node --help`
3. Verify topic: `ros2 topic list | grep phase1_complete`

## Inputs (internal to grab subprocess)

All inputs are produced by nodes INSIDE the grab subprocess (`cuttofu_phase1_grab_internal.launch.py`):
- RealSense camera → `/camera/camera/aligned_depth_to_color/image_raw`, `/camera/camera/color/camera_info`
- SAM3 detector → `/detected_objects`
- pose_estimator → `/objects_with_pose`
- follow node → `/follow/current_tcp_pose`

唯一外部输入: 机械臂与灵巧手通过 TCP/CAN 直连 (xCore SDK + O6 CAN)，不在 ROS 图内

## Outputs

- `/task/phase1_complete` (Bool): Phase1 grab complete signal
- `/follow/target_pose` (PoseStamped): Target waypoints during approach
- `/follow/safety_status` (String): OK/HOLD/STOP
- `/follow/hand_o6_deg` (String): O6 gripper angles
- `/follow/segment_done` (String): Segment completion status

## Assumptions

- Classmate's code is fully functional and tested in their workspace
- xCore SDK and Linkerbot O6 SDK paths are identical between workspaces (verified: xCore SDK binary identical, linkerbot SDK path correct)
- `can0` network interface is configured and up for O6 gripper
- SAM3 model at `/home/tbl/Project/models/sam3` is accessible
- RealSense camera is connected (D435I, USB)
- ROS_DOMAIN_ID=13 is set consistently across all terminals
- Classmate's `_BUNDLED_XCORE_SDK_ROOT` path bug has fallback logic that works
- **Two-process isolation**: Grab subprocess uses embedded xCore SDK (direct TCP to robot at 192.168.10.21). Phase2 uses xcore_controller_node services at arm IP 192.168.2.161. These are SEPARATE TCP connections — no conflict.
- **xcore_controller_node** (Phase2 arm services): started by `cuttofu_phase2.launch.py` or as persistent pre-requisite via `dual_xcore_controllers.launch.py arm_r_robot_ip:=192.168.2.161`

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `_BUNDLED_XCORE_SDK_ROOT` path resolves incorrectly | xCore SDK fails to load | Fallback via `DEXBOT_XCORE_SDK_ROOT` env var or `DEFAULT_XCORE_SDK_ROOT` |
| O6 CAN interface `can0` not available | Gripper control fails | Confirm `sudo ip link set can0 up type can bitrate 1000000` before demo |
| ~~SAM3 multi-prompt incompatibility~~ | ~~Phase2 recognition fails~~ | ~~Phase1 only uses single prompt; Phase2 runs after grab-knife exits with fresh SAM3~~ |
| Process exit leaves残留 resources | GPU/CAN port occupied | Internal launch file subprocess death = all nodes die. Add `psutil` verification and GPU memory check |
| Topic timing race | Phase2 starts before resources freed | 0.5s buffer + 5s broadcast window + subprocess SIGTERM grace period |
| Vision pipeline cleanup | pyrealsense2 or SAM3 CUDA context not freed | Internal launch subprocess SIGTERM → all child processes die, OS reclaims GPU memory. 5s broadcast window ensures buffer before Phase2 starts |
| xcore_controller_node conflict | Two controller nodes connecting to same robot | Phase2 arm IP (192.168.2.161) differs from classmate's follow node IP (192.168.10.21). Separate physical connections — no conflict. Verify IP addresses before demo. |

**SAM3 risk resolved (2026-05-19)**: No prompt switching needed. Phase2 launches a fresh `sam3_detector_node` with `text_prompt="豆腐"` after classmate's lifecycle subprocess exits. Process isolation guarantees clean state. Adding prompt switching logic would introduce unnecessary risk.

## Open Questions

- Q-MIG-002: `_BUNDLED_XCORE_SDK_ROOT` path bug — verify at runtime whether fallback logic works
- Q-MIG-004: O6 CAN interface — confirm `can0` is configured on demo machine
- Q-MIG-005: xcore_controller_node placement — launch inside `cuttofu_phase2.launch.py` or as persistent service before demo? (User commands: `ros2 launch dexbot_bringup dual_xcore_controllers.launch.py arm_r_robot_ip:=192.168.2.161 arm_l_robot_ip:=192.168.2.160 enable_internal_hand:=false`)
- Q-MIG-006: Classmate's follow node robot IP — confirm `xcore_follow_tcp_chain_node_movej.py` uses IP `192.168.10.21` (not `192.168.2.161`). Verify in classmate's config.

## Verification Plan

1. **Offline**: `colcon build` succeeds; all nodes import without errors
2. **Dry run**: Launch lifecycle wrapper without hardware; verify subprocess starts and exits cleanly
3. **Hardware test**: Full demo flow — grab knife → resource cleanup → Phase2 starts → cut tofu
4. **Resource check**: After lifecycle wrapper exits, verify:
   - No残留 Python processes from classmate's nodes
   - `can0` interface is released
   - GPU memory is freed (`nvidia-smi`)

## Verification Result

- ✅ **Offline**: `colcon build --packages-select cuttofo_xcore` succeeds (0.44s)
- ✅ **Launch parsing**: `ros2 launch cuttofu_phase1_grab.launch.py --show-args` parses correctly with all defaults resolved
- ✅ **Entry points**: All 11 registered including `phase1_grab_lifecycle_node`
- ⏳ **Dry run**: Not run yet
- ⏳ **Hardware test**: Not run yet
- ⏳ **Resource check**: Not run yet

## Merge Condition

- Hardware test passes: grab-knife completes → Phase2 starts → full chain executes
- Resource cleanup verified: no残留 processes, CAN released, GPU freed
- All open questions resolved

## Notes

- Classmate's workspace path: `/home/tbl/桌面/dexbot_ros2_ws`
- Migration target path: `/home/tbl/Project/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo/`
- Key files to migrate:
  - `ros/xcore_monitor_handle_sequence_node.py` (1881 lines)
  - `ros/xcore_follow_tcp_chain_node_movej.py` (5887 lines)
  - `ros/cut_tofu_phase3_lib.py` (430 lines)
  - `ros/cut_tofu_object_recognition_node.py` (940 lines)
  - `config/cut_tofu_phase3_sequence.json`
- Missing message types to add: `ObstacleBox.msg`, `TableWorkspace.msg`
- **Design Decision (2026-05-19)**: Grab pipeline launched as single `ros2 launch` subprocess (`cuttofu_phase1_grab_internal.launch.py`) instead of multiple `ros2 run` subprocesses. Reason: (a) includes vision stack (camera + SAM3 + pose_est) that classmate's recognition node needs, (b) one subprocess to kill = all nodes die atomically, (c) launch file handles remapping and parameters reliably.
- **Design Decision (2026-05-19)**: Two processes completely isolated. Zero shared ROS nodes between grab (Process A) and Phase2 (Process B). Communication only via `/task/phase1_complete` Bool topic. Grab process dies completely before Phase2 starts. Phase2 creates brand-new instances of all nodes (camera, SAM3, pose_est, etc.). No coupling, no risk of GPU/CAN/resource conflict.
