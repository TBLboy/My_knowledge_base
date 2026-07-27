# Business Logic Edges

> Aligned with actual code as of 2026-05-17.  
> Edges are **atomic execution chains** that move the system from one state node to another.

---

## Edge: Phase1 → Phase2 (Declarative Auto-Advance — Standalone Mode)

```yaml
edge_id: edge_1_to_2
from: PHASE_1_GRAB_KNIFE
to: PHASE_2_MOVE_TO_PREPARE
path: main
status: stable
method: auto_advance check in _advance_if_ready (0.5Hz timer)
execution_chain:
  - PhaseManager's 0.5Hz timer calls _advance_if_ready()
  - If auto_advance=True AND ctx.knife_grabbed==True → _set_phase(PHASE_2)
inputs: /knife_grabbed (Bool) = True, auto_advance = True
outputs: System enters PHASE_2_MOVE_TO_PREPARE
parameters:
  - name: auto_advance / type: bool / default: true / source: phases.auto_advance
interfaces: /knife_grabbed (subscription)
error_handling: If auto_advance=False, system stays in Phase1 indefinitely
verification: PhaseManager logs "Phase transition: PHASE_1_GRAB_KNIFE -> PHASE_2"
notes: Only declarative transition in the system. knife_grabbed is EXTERNAL signal. Used in standalone mode (cuttofu_phase2.launch.py).
```

---

## Edge: Phase1 → Phase2 (Monitor Launch — Collaboration Mode)

```yaml
edge_id: edge_1_monitor_to_2
from: PHASE_1_GRAB_KNIFE
to: PHASE_2_MOVE_TO_PREPARE
path: main
status: stable
method: phase1_monitor_node subscribes to /knife_grabbed, spawns Phase2 launch on signal
execution_chain:
  - 1. User runs: ros2 launch cuttofo_xcore cuttofu_phase1_monitor.launch.py
  - 2. phase1_monitor_node starts (only node alive; no camera/SAM3 resources used)
  - 3. Classmate's knife-grab program runs in separate terminal (uses camera, SAM3, pose_estimator)
  - 4. Classmate's program finishes: publishes /knife_grabbed=true (5-10 frames), then exits all nodes
  - 5. phase1_monitor_node receives /knife_grabbed=true
  - 6. Waits wait_before_launch_s (default 2.0s) for classmate's nodes to fully release resources
  - 7. Monitor calls rclpy.shutdown(), then subprocess.run(ros2 launch cuttofu_phase2.launch.py start_phase:=PHASE_2_MOVE_TO_PREPARE)
  - 8. Phase2 full system launches (RealSense, SAM3, pose_estimator, action servers, PhaseManager)
  - 9. PhaseManager starts at PHASE_2_MOVE_TO_PREPARE (Phase1 skipped)
inputs: /knife_grabbed (Bool) = True from classmate's program
outputs: Full Phase2+ system running in same terminal
parameters:
  - name: wait_before_launch_s / type: float / default: 2.0 / source: param
interfaces: /knife_grabbed (subscription), subprocess ros2 launch
error_handling: If classmate's nodes don't exit cleanly, resource conflicts may occur. Increase wait_before_launch_s.
verification: Monitor logs "Knife grabbed! Waiting 2.0s for resource release..." then "Launching Phase2 full system..."
notes: Collaboration mode. Keeps camera/SAM3/GPU free for classmate's independent framework. Phase2 launch blocks in same terminal until DONE or Ctrl+C.
```

---

## Edge: Phase2 → Phase3/5/7 (Prepare Knife at Tofu Right Edge)

```yaml
edge_id: edge_2_prepare
from: PHASE_2_MOVE_TO_PREPARE
to: ctx.prepare_next_phase (PHASE_3 / PHASE_5 / PHASE_7)
path: main
status: stable
method: Send MoveToPreparePose action goal to knife_prepare_action_server
execution_chain:
  - 1. PhaseManager selects config: phase2_prepare (for Phase3) or phase6_prepare (for Phase7)
  - 2. Sends MoveToPreparePose.Goal with plane_angle_deg, offset_a, vertical_offset, edge_align
  - 3. knife_prepare_action_server pipeline:
       a. Wait for valid /tofu_state (timeout 5.0s)
       b. compute_tcp_target_from_corners(corners_4, offset_a, vertical_offset):
          - top_y = mean(corners[:,1])
          - A, B = Z-largest 2 corners (right edge)
          - v = AB direction in XZ plane, v.x > 0
          - l = perpendicular to v in XZ, l.z < 0 (pointing left/base Z-)
          - D = (A+B)/2, D' = D + offset_a*l
          - TCP = [D'.x, top_y+vertical_offset, D'.z]
       c. Build target rotation:
          - edge_align=true: build_rotation_with_edge_dir(plane_angle_deg, edge_dir)
            tcp_Y = edge_dir (knife spine follows tofu edge)
          - edge_align=false: build_target_rotation_from_constraints(plane_angle_deg)
            tcp_Y = [1,0,0] = base_X
       d. TCP→flange: flange_target = TCP_target - target_R @ tcp_offset
       e. IK solve: candidate_count seeds + random perturbations → scipy least_squares
          Accepted: pos_err < 1e-4m, rot_err < 0.06deg, within safe_bounds (limit ± safety_margin_deg)
       f. Preview scoring: generate cut_preview_poses along tcp_Z, rollout IK chain
          Multi-component score: path_cost, jump_cost, joint1_cost, limit_cost, wrist_cost, current_cost
          Reject if min_margin_deg < safety_margin_deg
       g. Select best candidate → arm.move_to_joints(best_q) → verify_arrival
  - 4. PhaseManager receives result: success → transition to prepare_next_phase
  - 5. First entry only: publish Bool(True) on /cutting_start
inputs: /tofu_state (top_corners, edge_dir), /joint_states
outputs: reached_tcp_pose, reached_joints
parameters:
  plane_angle_deg: 135.0 (phase2) / 90.0 (phase6) / config
  offset_a: -0.005 (phase2) / 0.02 (phase6) / config-goal
  vertical_offset: 0.015 (phase2) / 0.001 (phase6) / config-goal
  edge_align: true / config
  candidate_count: 40 / config
  preview_steps: 15 / config
  cut_depth: 0.017 / config
  safety_margin_deg: 15.0 / config
interfaces: /move_to_prepare_pose (Action), /tofu_state, /joint_states
error_handling: Tofu timeout/IK failure → action aborted → Phase ERROR
verification: Log "Phase2 prepare pose reached: Success"
notes: Phase2 is entered 3 times. tcp_offset handled by adapter layer internally.
```

---

## Edge: Phase3 → Phase4 (First Oblique Cut)

```yaml
edge_id: edge_3_to_4
from: PHASE_3_FIRST_CUT
to: PHASE_4_ROTATE_TOFU
path: main
status: stable
method: Relative Cartesian cutting via ExecuteKnifeCut action
execution_chain:
  - 1. PhaseManager sends ExecuteKnifeCut.Goal(phase_name="PHASE_3_FIRST_CUT")
  - 2. knife_cut_action_server._execute_once():
       a. Gets current flange pose from xCore (anchor_mat)
       b. Loads cutting.phase3_first_cut config → CutTrajectoryConfig
       c. build_cut_waypoints(anchor_mat, cfg):
          For each cycle ci: anchor_i = anchor_0 + ci*[step_x,step_y,step_z]
          cut_i = anchor_i + cut_move along cut_direction (flange_z or base_y)
          retract_i = anchor_i
          next_anchor = anchor_{i+1} or stay
       d. Converts to Pose list, validates first segment sanity
       e. Sends via arm.move_rt_cartesian_path (impedance first, position fallback)
  - 3. On success → PhaseManager transitions to Phase4
inputs: Current flange pose, phase3_first_cut config
outputs: Arm at final step position (anchor_0 + (cycles-1)*step)
parameters: cycles, cut_direction("flange_z"|"base_y"), cut_move, step_*, RT params / config
interfaces: /execute_knife_cut (Action), /arm_r/robot/move_rt_cartesian_path
error_handling: Impedance failure → position retry. Both fail → ERROR.
verification: Log "PHASE_3_FIRST_CUT waypoint sanity: first_dist=X expected_cut=X"
notes: Same pattern reused by Phase5. step_z negative for right-to-left cutting.
```

---

## Edge: Phase4/6 → Phase2 (Return Anchor + User Wait)

### Normal Mode (from Phase3/Phase5)

```yaml
edge_id: edge_4_or_6_reprepare
from: PHASE_4_ROTATE_TOFU or PHASE_6_ROTATE_TOFU
to: PHASE_2_MOVE_TO_PREPARE (re-entry)
path: main
status: stable
method: Reverse accumulated step displacements + move to wait pose + wait for user
execution_chain:
  - 1. PhaseManager sends ExecuteKnifeCut.Goal(phase_name="PHASE_4/6_ROTATE_TOFU")
  - 2. knife_cut_action_server:
       a. Reads source_phase config (phase3_first_cut) → cycles, step_x/y/z
       b. Computes return_offset = -(cycles-1) * [step_x, step_y, step_z]
       c. Single-pose return-to-prepare waypoint → move_rt_cartesian_path
       d. move_to_joints(wait_joint_positions, speed=wait_joint_speed)
       e. Wait for user confirmation:
          - TTY: input("Rotate tofu, then press Enter...")
          - Non-TTY: poll touch file (/tmp/cuttofo_phase4/6_continue)
       f. On confirmation: set prepare_next_phase, transition to Phase2
  - 3. Phase4→Phase2 sets prepare_next_phase=PHASE_5; Phase6→Phase2 sets prepare_next_phase=PHASE_7
inputs: Phase3 config (for reverse), wait_joint_positions, user signal
outputs: Arm at wait pose; triggers Phase2 re-entry
parameters: source_phase, wait_joint_positions(7 floats), wait_joint_speed(0.3), wait_continue_file / config
interfaces: /execute_knife_cut, stdin/touch file
error_handling: Missing wait joints → ValueError; arm motion fail → ERROR
verification: Log "Phase4/6 user confirmed rotation; ready to re-run prepare"
notes: Phase4 and Phase6 share identical code; differ only by config + continue file. Stale file cleared on entry.
```

### Jump Mode (manual /phase_jump or start_phase=PHASE_4/6)

```yaml
edge_id: edge_4_or_6_jump_reprepare
from: PHASE_4_ROTATE_TOFU or PHASE_6_ROTATE_TOFU (via /phase_jump or start_phase)
to: PHASE_2_MOVE_TO_PREPARE (re-entry)
path: main
status: stable
method: PhaseManager polls continue file directly; skips action server entirely
execution_chain:
  - 1. User sends /phase_jump "PHASE_4_ROTATE_TOFU" or "PHASE_6_ROTATE_TOFU"
       OR: launch with start_phase:=PHASE_4_ROTATE_TOFU / PHASE_6_ROTATE_TOFU
  - 2. PhaseManager._set_phase() or __init__() sets ctx.skip_return_motion=True
  - 3. PhaseManager._tick_phase4_return() / _tick_phase6_return() detects skip_return_motion:
       a. Does NOT send ExecuteKnifeCut goal (no return-to-prepare motion)
       b. Does NOT move to wait joint pose
       c. Polls /tmp/cuttofo_phase4_continue or /tmp/cuttofo_phase6_continue
       d. On file detected: sets prepare_next_phase, ctx.tofu_rotated=True
       e. Transitions to PHASE_2_MOVE_TO_PREPARE
  - 4. Phase4 jump: prepare_next_phase=PHASE_5_SECOND_CUT
  - 5. Phase6 jump: prepare_next_phase=PHASE_7_THIRD_CUT
inputs: /tmp/cuttofo_phase4_continue or /tmp/cuttofo_phase6_continue touch file
outputs: Triggers Phase2 re-entry with correct prepare_next_phase
parameters: skip_return_motion (bool, set by /phase_jump handler or __init__ for start_phase)
interfaces: None (no action server call)
error_handling: Continue file missing → stays in Phase4/6 indefinitely
verification: Log "Phase4/6 jump: waiting for continue file" → "Phase4/6 jump continue detected"
notes: Bypasses knife_cut_action_server entirely. No arm motion. User must manually rotate tofu before touching continue file. start_phase=PHASE_4/6 also enters jump mode.
```

---

## Edge: Phase5 → Phase6 (Second Cut — Independent Config)

```yaml
edge_id: edge_5_to_6
from: PHASE_5_SECOND_CUT
to: PHASE_6_ROTATE_TOFU
path: main
status: stable
method: Same cutting script as Phase3 (build_cut_waypoints) but with independent phase5_second_cut config
execution_chain:
  - 1. PhaseManager sends ExecuteKnifeCut.Goal(phase_name="PHASE_5_SECOND_CUT")
  - 2. _current_phase_cfg("PHASE_5_SECOND_CUT"):
       Directly reads phase5_second_cut config section (no reuse_phase inheritance)
  - 3. Same pipeline as Phase3: build_cut_waypoints(anchor_mat, cfg) + move_rt_cartesian_path
  - 4. On success → PhaseManager transitions to Phase6
inputs: Current flange pose, phase5_second_cut config
outputs: Arm at final step position
parameters: cycles(9) / cut_direction(flange_z) / cut_move(0.059) / step_x(0.0) / step_y(0.0) / step_z(-0.0155) / config
interfaces: /execute_knife_cut (Action), move_rt_cartesian_path
error_handling: Impedance→position fallback (same as Phase3)
verification: Log "PHASE_5_SECOND_CUT waypoint sanity"
notes: Shares build_cut_waypoints() script with Phase3 but has own independent parameter set. All params tunable without affecting Phase3.
```

---

## Edge: Phase7 → DONE (Vertical Cut with Push)

```yaml
edge_id: edge_7_to_done
from: PHASE_7_THIRD_CUT
to: PHASE_DONE
path: main
status: stable
method: Dedicated vertical cutting executor with segmented motion + push control
execution_chain:
  - 1. PhaseManager sends ExecuteKnifeCut.Goal(phase_name="PHASE_7_THIRD_CUT")
  - 2. _execute_phase7_cut():
       a. Reads current flange pose (anchor_0 from Phase6 re-prepare)
       b. build_vertical_cut_waypoints(anchor_mat, cfg):
          For ci=0..cycles-1:
            anchor_i = anchor_0 + ci*step_z_m (Z step only)
            cut_i = anchor_i with Y -= cut_move_m (base Y- = down)
            retract_i = anchor_i (back up)
            next_anchor = anchor_{i+1} or stay
          Returns 3*cycles waypoints
       c. Splits into segments:
          seg1: waypoints[:mid_ci*3+1] — cycles 0..mid-1 + mid cut
          seg2: waypoints[mid_ci*3+1 : last_ci*3+1] — mid retract through last cut
          seg3: waypoints[last_ci*3+1 : last_ci*3+2] — last retract
       d. Executes seg1 (cut speed)
        e. Mid-push (cycles>1, at cut depth, before retract):
           lift_up: Y+ push_lift_y → push_forward: Z+ @ push_forward_speed → return to lift → push_backward: Z- @ push_backward_speed → return to lift → drop back to cut depth
           Record mid_anchor position
        f. Executes seg2 (cut speed)
        g. Executes seg3 (cut speed)
        h. Tail-push (cycles>1):
           move to mid_anchor → cut down (Y-) → lift_up (Y+ push_lift_y) → push_tail (Z- @ push_tail_speed) → return to lift → retract to mid_anchor
        i. Per-segment impedance fallback: if impedance fails → retry same segment in position mode
           Sets use_impedance=False for all subsequent segments
inputs: Current flange pose (anchor_0), phase7_third_cut config
outputs: Arm at mid_anchor after tail retract → DONE
parameters:
  cycles: 14 / cut_move: 0.04 / step_z: -0.005 / config
  push_lift_y: 0.005 / config (lift before each push)
  push_forward_z: 0.01 / push_forward_speed: 0.01 / config
  push_backward_z: -0.005 / push_backward_speed: 0.01 / config
  push_tail_z: -0.01 / push_tail_speed: 0.01 / config
interfaces: /execute_knife_cut (Action), move_rt_cartesian_path (per segment)
error_handling: Per-segment fallback prevents retry-from-wrong-anchor bug. cycles==1 skips push+tail.
verification: Log "PHASE_7_THIRD_CUT: cycles=14 mid_ci=7 waypoints=42" + per-segment vel logs
notes: Cut direction HARDCODED base Y-. Step HARDCODED base Z. Push speeds independent. push_lift_y lifts knife before each push to reduce friction.
```

---

## Edge: Perception Pipeline (Continuous, Parallel)

```yaml
edge_id: edge_perception
from: (camera stream)
to: /tofu_state (10 Hz continuous output)
path: main
status: stable
method: Continuous visual perception — runs independently in parallel to all phases
execution_chain:
  - 1. RealSense D435I → color 1280x720 RGB8 + depth 848x480 Z16
  - 2. sam3_detector_node: text prompt (default "tofu"), 5Hz auto detection
  - 3. pose_estimator_node: crop mask → back-project depth → get_pose_from_mask() → /objects_with_pose
  - 4. tofu_state_node:
       Filter class_id → reconstruct 8 corners → extract Y-largest 4 = top_corners
       Sliding window buffer (15 frames, jump_threshold=0.05m, min_buffer_frames=3)
       edge_dir: AB (Z-largest 2 corners) direction in XZ, v.x > 0
       tcp_target: compute_tcp_target_from_corners(corners_4, offset_a, vertical_offset)
       Publish TofuState at 10 Hz
inputs: RealSense camera streams, /detected_objects
outputs: /objects_with_pose, /tofu_state (10Hz)
parameters: text_prompt, detection_threshold(0.30), corner_mode("aabb"), 6 AABB percentile params / config
interfaces: /camera/* (sub), /detected_objects (pub), /objects_with_pose (pub), /tofu_state (pub 10Hz)
error_handling: Detection fail → retry next cycle. Buffer jump → cleared. Timeout → is_valid=False.
verification: TofuState.health_state: HEALTH_TRACKING/STALE/LOST
notes: Runs CONTINUOUSLY. Phase2/6 re-prepare re-reads /tofu_state after rotation.
```

---

## ROS Communication Topology

```
RealSense D435I
  │   color/image_raw ──→ sam3_detector_node ──→ /detected_objects
  │   aligned_depth      ──┐
  │   camera_info         ──┘─→ pose_estimator_node ──→ /objects_with_pose
  │                                                         │
  │                                                   tofu_state_node (10Hz)
  │                                                         │
  │                                                     /tofu_state
  │                                                         │
  │              ┌──────────────────────────────────────────┤
  │              │                                          │
  │    phase_manager_node         knife_prepare_action_server
  │    (state machine)            Action: /move_to_prepare_pose
  │    Action: /execute_knife_cut     Sub: /tofu_state, /joint_states
  │              │
  │    knife_cut_action_server
  │    Service: /arm_r/robot/move_rt_cartesian_path
  │    Service: /arm_r/robot/get_state
  │
  │    tofu_visualizer_node (RViz MarkerArray)
  │    camera_viewer_node (visualization overlay)
```
