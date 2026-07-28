# Business Logic Nodes

> Aligned with actual implementation as of 2026-05-17.  
> Nodes are **system state snapshots**, not ROS nodes.

---

## State Nodes (Phase States)

```yaml
id: PHASE_1_GRAB_KNIFE
name: "等待拿刀"
status: stable
state:
  - System initialized, all ROS nodes alive
  - Camera streaming, SAM3 + pose_estimator running
  - Mechanical arm connected, not yet holding knife
inputs:
  - /knife_grabbed (Bool): external signal that knife is grasped
outputs:
  - None (auto-advances to Phase2 on knife_grabbed=True)
data_format:
  - Bool topic, 10 Hz publish rate
related_interfaces:
  - /knife_grabbed (subscription)
verification:
  - PhaseManager logs "Entered PHASE_1_GRAB_KNIFE"
  - Phase1 transitions to Phase2 when ctx.knife_grabbed==True
notes:
  - External human/script action; system does not control knife grasp
  - Default start_phase in config
---

id: PHASE_2_MOVE_TO_PREPARE
name: "刀移刀到预备位"
status: stable
state:
  - Tofu detected via SAM3 + pose_estimator
  - /tofu_state topic publishing valid corner data
  - IK solver selected a valid joint-space candidate
  - Arm has moved to the computed prepare pose
inputs:
  - /tofu_state (TofuState): tofu corner points, edge direction, precomputed TCP target
  - /joint_states (JointState): current joint angles for IK seeding
outputs:
  - /move_to_prepare_pose action result: reached TCP pose + joint angles
  - /cutting_start (Bool): published once after first Phase2→Phase3 transition
data_format:
  - TofuState custom message (top_corners, edge_dir, tcp_target, top_y, is_valid)
  - MoveToPreparePose.action (goal: plane_angle_deg, offset_a, vertical_offset, edge_align)
related_interfaces:
  - /move_to_prepare_pose (Action Server)
  - /tofu_state (subscription, timeout=5.0s)
  - /joint_states (subscription)
  - /cutting_start (publisher, once on first Phase2→Phase3)
related_hardware:
  - RealSense D435I camera
  - AR5 7-DOF robot arm (right or left)
verification:
  - PhaseManager logs "Phase2 prepare pose reached: Success"
  - Action result contains reached TCP pose and joint positions
notes:
  - Reused 3 times: Phase1→Phase2, Phase4→Phase2, Phase6→Phase2
  - Phase2 config selected by _prepare_cfg_for_current_step:
    - First entry: cutting.phase2_prepare (plane=135°, offset_a=-0.005, vertical_offset=0.015)
    - Phase6 re-entry: cutting.phase6_prepare (plane=90°, offset_a=0.02, vertical_offset=0.001)
  - Prepares knife at tofu right edge, offset by offset_a along l direction (base Z-)
---

id: PHASE_3_FIRST_CUT
name: "第一次切割"
status: stable
state:
  - Knife is at prepare pose from Phase2
  - Cutting has executed N cycles of cut→retract→step
inputs:
  - Current flange pose (via xCore get_state)
outputs:
  - Arm moved through cut trajectory; arm at final step position
data_format:
  - CutTrajectoryConfig (cycles, cut_direction, cut_move_m, step_x/y/z_m)
  - waypoints: list of Pose messages
related_interfaces:
  - /execute_knife_cut (Action Server, phase_name="PHASE_3_FIRST_CUT")
  - /arm_r/robot/move_rt_cartesian_path (RT Cartesian path service)
related_hardware:
  - AR5 7-DOF robot arm
verification:
  - Waypoint sanity log: first_delta, first_dist, first_rot_delta
  - Phase3 success → transition to Phase4
notes:
  - Cut direction: configurable (base_y or flange_z)
  - Step axis: single axis (x, y, or z), mutually exclusive
  - Uses impedance mode first, then position mode fallback
  - Phase5 reuses Phase3 trajectory parameters via reuse_phase mechanism
---

id: PHASE_4_ROTATE_TOFU
name: "第一次旋转豆腐"
status: stable
state:
  - Phase3 cutting completed; knife at final cut position
  - Arm has returned to original prepare anchor (reversing step displacements)
  - Arm has moved to user-rotation wait joint pose
  - System is waiting for user to rotate tofu and confirm
inputs:
  - None (waits for user signal via terminal input() or touch file)
outputs:
  - Arm at wait joint pose, ready for tofu rotation
  - Triggers Phase4→Phase2 re-entry on user confirmation
data_format:
  - phase4_return_to_prepare config (source_phase, wait_joint_positions, wait_joint_speed)
  - Return-to-prepare is single-pose Cartesian move
  - Wait pose: move_to_joints(7 joints, speed=0.3)
related_interfaces:
  - /execute_knife_cut (Action Server, phase_name="PHASE_4_ROTATE_TOFU")
  - /tmp/cuttofo_phase4_continue (touch file for non-TTY mode)
  - Terminal input() for interactive mode
related_hardware:
  - AR5 7-DOF robot arm (moves to neutral wait pose)
verification:
  - PhaseManager logs "Phase4 ready: rotate tofu manually"
  - Phase4→Phase2 re-entry happens on Enter/touch
notes:
  - Phase4 AND Phase6 share the same code branch in knife_cut_action_server
  - Uses source_phase (defaults to phase3_first_cut) to compute reverse displacement
  - User rotation is a MANUAL step; arm waits at neutral pose
---

id: PHASE_5_SECOND_CUT
name: "第二次切割"
status: stable
state:
  - Tofu has been rotated by user
  - Knife re-prepared to new tofu position via Phase2 re-entry
  - Second cutting pass executes same trajectory pattern as Phase3
inputs:
  - Current flange pose (via xCore get_state)
outputs:
  - Arm moved through cut trajectory; arm at final step position
data_format:
  - Reuses Phase3's CutTrajectoryConfig (cycles, cut_direction, cut_move, step_*)
  - Only impedance/stiffness params can be overridden
related_interfaces:
  - /execute_knife_cut (Action Server, phase_name="PHASE_5_SECOND_CUT")
  - /arm_r/robot/move_rt_cartesian_path
verification:
  - Phase5 logs "PHASE_5_SECOND_CUT waypoint sanity"
  - Phase5 success → transition to Phase6
notes:
  - Phase5 is a DEAD-SCRIPT clone of Phase3 by design
  - reuse_phase: phase3_first_cut config key ensures parameter reuse
  - Only prefer_rt_impedance, fallback_to_rt_position, stiffness can differ from Phase3
---

id: PHASE_6_ROTATE_TOFU
name: "第二次旋转豆腐"
status: stable
state:
  - Phase5 cutting completed; knife returned to prepare anchor
  - Arm at user-rotation wait pose (may differ from Phase4 wait pose)
  - Waiting for user to rotate tofu and confirm
inputs:
  - None (user signal)
outputs:
  - Triggers Phase6→Phase2 re-entry, which transitions to Phase7
data_format:
  - phase6_return_to_prepare config (source_phase, wait_joint_positions, wait_joint_speed)
  - Uses /tmp/cuttofo_phase6_continue file (different from Phase4)
related_interfaces:
  - /execute_knife_cut (Action Server, phase_name="PHASE_6_ROTATE_TOFU")
  - /tmp/cuttofo_phase6_continue
verification:
  - PhaseManager logs "Phase6 ready: rotate tofu"
notes:
  - Identical structure to Phase4, different config section
  - Sets prepare_next_phase = PHASE_7_THIRD_CUT on success
---

id: PHASE_7_THIRD_CUT
name: "第三次垂直切割"
status: stable
state:
  - Knife is vertical at tofu right edge (from Phase6 re-prepare)
  - Vertical cutting with mid-cycle push and tail push
  - 14 cycles of cut(Y-)→retract(Y+)→step(Z-)
  - Push forward/backward at cycle 7 (mid)
  - Tail push at end: return to mid-anchor, cut down, push left
inputs:
  - Current flange pose (via xCore get_state)
outputs:
  - Phase7 complete → DONE
data_format:
  - phase7_third_cut config (cycles, cut_move, step_z, push_*)
  - Segmented execution: seg1→push→seg2→seg3→tail-push
related_interfaces:
  - /execute_knife_cut (Action Server, phase_name="PHASE_7_THIRD_CUT")
  - /arm_r/robot/move_rt_cartesian_path (per-segment calls with speed overrides)
verification:
  - Phase7 logs "PHASE_7_THIRD_CUT: cycles=14 mid_ci=7 last_ci=13 waypoints=42"
  - Each segment logs waypoint count and velocity
  - Per-segment impedance fallback (internal to _move_segment)
notes:
  - Cut direction is HARDCODED base Y- (down); step is HARDCODED base Z
  - Push speeds are independent from cut speeds
  - Implements internal per-segment impedance→position fallback (no outer retry)
---

id: PHASE_DONE
name: "切割完成"
status: stable
state:
  - All 3 cutting passes completed
  - System idle, ready for shutdown
inputs:
  - None
outputs:
  - None
data_format:
  - N/A
verification:
  - PhaseManager logs "Phase transition: PHASE_7_THIRD_CUT -> DONE"
---

id: PHASE_ERROR
name: "错误状态"
status: stable
state:
  - Something failed (goal send, goal reject, action result failure)
  - System halted; requires manual intervention
inputs:
  - None (manual reset via /phase_jump or manual_override)
outputs:
  - None
data_format:
  - N/A
verification:
  - PhaseManager logs transition reason (e.g. "phase3_failed")
notes:
  - No automatic recovery path from ERROR
  - Can be manually redirected via /phase_jump topic (String message to any valid phase) or config param manual_override
```

---

## ROS Node Architecture

| Node | Package | Topic/Service/Action | Status |
|------|---------|---------------------|--------|
| `sam3_detector_node` | dexbot_middle_layer | Sub: /camera/color/image_raw; Pub: /detected_objects | ✅ Stable |
| `pose_estimator_node` | dexbot_middle_layer | Sub: depth+camera_info, /detected_objects; Pub: /objects_with_pose | ✅ Stable |
| `tofu_state_node` | cuttofo_xcore | Sub: /objects_with_pose; Pub: /tofu_state (10Hz) | ✅ Stable |
| `phase_manager_node` | cuttofo_xcore | Sub: /knife_grabbed, /tofu_state, /phase_jump; Pub: /phase_state, /cutting_start | ✅ Stable |
| `knife_prepare_action_server` | cuttofo_xcore | Action: /move_to_prepare_pose; Sub: /tofu_state, /joint_states | ✅ Stable |
| `knife_cut_action_server` | cuttofo_xcore | Action: /execute_knife_cut; Client: /arm_r/robot/move_rt_cartesian_path | ✅ Stable |
| `tofu_visualizer_node` | cuttofo_xcore | Sub: /tofu_state; Pub: /tofu_visualization (MarkerArray) | ✅ Stable |
| `camera_viewer_node` | dexbot_toolbox | Sub: /camera/color/image_raw; visualization overlay | ✅ Stable |
| `xcore_controller_node` | dexbot_bottom_layer | Service: /arm_r/robot/move_rt_cartesian_path, get_state; Pub: /joint_states | ✅ Stable |
