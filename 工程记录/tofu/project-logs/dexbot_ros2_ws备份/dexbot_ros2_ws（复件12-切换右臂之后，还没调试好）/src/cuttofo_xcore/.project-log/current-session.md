# Current Session

## Last Updated

- 2026-05-17 (Phase7 logic rewrite complete)

## Current Objective

- Phase7 vertical cut logic rewritten and build verified.

## Completed This Session

### Phase7 Vertical Cut — Complete Rewrite

**Problem**: Old Phase7 logic had bugs:
1. Knife went UP first instead of DOWN (press_normal along flange+Z pointing up at prepare pose)
2. Push actions happened at tofu surface (anchor_i level), not at cut depth

**New Phase7 Logic** (per user spec 2026-05-17):

Standard cycle (same as Phase3/5):
1. STAB: knife moves base **Y-** (down into tofu) by `cut_move`
2. RETRACT: knife moves base **Y+** (up, back to anchor)
3. STEP: knife moves base **Z** by `step_z` to next anchor

Mid cycle (ci == cycles // 2, knife still stabbed before retract):
1. STAB (Y- down)
2. PUSH_FORWARD: move base **Z+** by `push_forward_z` → return to stab position (speed: `push_forward_speed`)
3. PUSH_BACKWARD: move base **Z-** by `push_backward_z` → return to stab position (speed: `push_backward_speed`)
4. RETRACT (Y+ up)
5. **Record mid_anchor** for tail push
6. STEP (Z- to next anchor)

Last cycle (ci == last_ci):
1. STAB (Y- down)
2. RETRACT (Y+ up)
3. Move to mid_anchor (recorded earlier)
4. STAB (Y- down)
5. PUSH_TAIL: move base **Z-** by `push_tail_z` (speed: `push_tail_speed`)
6. RETRACT (Y+ up)
7. Done

**Config changes** (`cuttofo_config.yaml` phase7_third_cut):
- Removed: `press_normal`, `push_half_z`, `push_half_back_z`
- Added: `push_forward_z: 0.01`, `push_forward_speed: 0.01`, `push_backward_z: -0.01`, `push_backward_speed: 0.01`, `push_tail_speed: 0.01`
- Kept: `cycles: 9`, `cut_move: 0.05`, `step_z: -0.005`, `push_tail_z: -0.01`

**Code changes**:
- `cut_trajectory.py`: `build_vertical_cut_waypoints()` — now generates flat waypoint list only (cut→retract→[next_anchor per cycle]), no push logic
- `knife_cut_action_server.py`: new `_execute_phase7_cut()` method with 5 execution segments and independent push speeds

### AABB Percentile Parameters (completed earlier)
- 6 new params exposed through config chain: `y_filter_percentile`, `x_percentile_low/high`, `z_percentile_low/high`, `top_y_percentile`
- Files: `vision_utils.py` (signature + body), `pose_estimator_node.py` (declare + pass), `cuttofu_phase2.launch.py` (forward), `cuttofo_config.yaml` (values)

## Current Business Logic Position

- Main path: Phase1 grab → Phase2 prepare → Phase3 cut → Phase4 return+wait+rotate+re-prepare → Phase5 cut → Phase6 return+wait+rotate+re-prepare → Phase7 vertical cut → DONE.
- Phase7 vertical cut: **REWRITTEN** — new logic ready for hardware test.

## Phase7 New Flow (Active — Rewritten 2026-05-17)

```
Phase6 re-prepare success → Phase7

Standard cycle (ci = 0..cycles-1):
  anchor_i → STAB (base Y-, cut_move) → RETRACT (base Y+) → [STEP (base Z, step_z)] → anchor_{i+1}

Mid-cycle (ci == cycles // 2):
  anchor_mid → STAB → [PUSH_FORWARD (base Z+, push_forward_z, push_forward_speed) → return]
                → [PUSH_BACKWARD (base Z-, push_backward_z, push_backward_speed) → return]
                → RETRACT → [STEP]
  Record mid_anchor

Last cycle (ci == cycles - 1):
  anchor_last → STAB → RETRACT → [move to mid_anchor]
                             → STAB (at mid_anchor)
                             → PUSH_TAIL (base Z-, push_tail_z, push_tail_speed)
                             → RETRACT → DONE
```

## Phase6 New Flow (Active)

```
Phase5 done
  → Phase6: return-to-prepare (RT Cartesian)
  → Phase6: move to wait_joint_positions
  → Phase6: wait for /tmp/cuttofo_phase6_continue
  → Phase6: transitions to Phase2
  → Phase2: re-serve tofu (use_vision=True, edge_align=true)
  → Phase2: prepare success
  → Phase6 done → Phase7
```

## Phase4 New Flow (Active)

```
Phase3 done
  → Phase4: return-to-prepare (RT Cartesian)
  → Phase4: move to wait_joint_positions
  → Phase4: BLOCK on terminal input() — "rotate tofu, press Enter"
  → Phase4: transitions to Phase2
  → Phase2: re-serve tofu (use_vision=True, edge_align=true)
  → Phase2: prepare success
  → Phase4 done → Phase5
```

## Problems Encountered

- Phase2 IK `valid=0`: all 263 seeds rejected by strict pos/rot error thresholds. Likely cause is `edge_align=true` + `offset_a=0` making target too constrained.
- Old Phase7 press_normal bug: at prepare pose, flange +Z pointed UP, so +press_normal moved knife 8mm UP instead of DOWN into tofu. Fixed by complete rewrite.
- Old Phase7 push bug: push waypoints computed from anchor_i (surface level) appended AFTER retract. Now push happens INSIDE the mid cycle before retract, using stab position.

## Verification

- `colcon build --packages-select cuttofo_xcore` succeeded (0.46s, no errors).
- `build_vertical_cut_waypoints()` verified via `python3 -c "import ..."` — source confirmed correct.
- Function returns flat list: cut, retract, next_anchor per cycle (3 waypoints each).
- Action server `_execute_phase7_cut()` added with proper segment splitting and push speed overrides.

## Next Steps

### Phase7 hardware test (immediate)
1. Run Phase7 on hardware with new logic.
2. Verify knife goes DOWN first (base Y-) not UP.
3. Verify mid-cycle push happens at cut depth (before retract).
4. Verify tail push at end (move to mid_anchor, stab, push Z-, retract).
5. Tune: `push_forward_speed`, `push_backward_speed`, `push_tail_speed`, `push_forward_z`, `push_backward_z`, `push_tail_z`.
