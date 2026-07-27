# Business Logic Constraints

> Aligned with code as of 2026-05-20

## Tool Frame Constraints

- Phase1 grab uses `cut_tofo_tcp` tool frame (offset `0.025, 0.0, 0.08`) for grasp-follow motions
- Phase1 must restore default `tool0/wobj0` before subprocess exits (via `set_toolset_by_name` after `move_abs_joints` success)
- Phase3/Phase5 RT Cartesian path forces `setToolset(tool0, wobj0)` at step 3.5 before entering `RtCommandMode`
- RT Cartesian path interprets target poses in the **active** SDK tool frame; stale tool frame causes instantaneous pose correction jerk
- Phase2 joint-space MoveJ is unaffected by tool frame state

## Return-to-Prepare Safety Constraint

- Phase4/Phase6 return-to-prepare moves knife from left side (final cut position) back to right side (prepare position)
- Pure reverse offset `-(cycles-1) * step` returns knife to exact original prepare pose → risk of blade scraping tofu
- `return_extra_offset_m` (default 0.04m) is added along base Z+ direction to push knife further right, ensuring clearance from tofu
- Effective return: `dz = -(cycles-1) * step_z + return_extra_offset_m`
- Applies to both `phase4_return_to_prepare` and `phase6_return_to_prepare` config sections

## Coordinate Frames

| Frame | X+ | Y+ | Z+ | Notes |
|-------|----|----|----|-------|
| Base | forward | up | right | Robot base, right arm |
| Flange (link7) | forward | up | right | Same as base (at home pose) |
| TCP (knife tip) | forward | up | right | Flange + tcp_offset (pure translation in flange frame) |
| Camera | — | — | — | Transformed to base via T_base_cam (hand-eye calibration) |

**Right arm tcp_offset**: [0.008, 0.18, 0.262] m  
**Coordinate system**: X → 前(forward), Y ↑ 上(up), Z → 右(right)

## Knife Orientation Constraints

| Constraint | Expression | Notes |
|------------|-----------|-------|
| Knife spine (edge_align=false) | tcp_Y = [1,0,0] = base_X | Fixed forward |
| Knife spine (edge_align=true) | tcp_Y = edge_dir | Follows tofu right edge, projected to XZ plane |
| Knife face tilt | tcp_Z angle to XZ plane = plane_angle_deg | Max 40-45° due to joint_6 ±40° limit |
| Edge direction | v in XZ plane, v.x > 0 | v = normalize([AB.x, 0, AB.z]), acute angle with base_X+ |
| Offset direction | l perpendicular to v in XZ, l.z < 0 | l points left/base_Z- from tofu right edge |

## Joint Limits

| Joint | Raw Range | Safe Range | Safety Margin |
|-------|-----------|------------|---------------|
| joint_1 | ±178° | ±163° | 15° |
| joint_2 | ±120° | ±105° | 15° |
| joint_3 | ±178° | ±163° | 15° |
| joint_4 | -60°~145° | -45°~130° | 15° |
| joint_5 | ±178° | ±163° | 15° |
| joint_6 | ±55° | ±40° | 15° |
| joint_7 | ±55° | ±40° | 15° |

Safety margins enforced during IK solving. Candidates closer to limits than safety_margin_deg are rejected.

## Cutting Constraints

| Constraint | Phase3/5 | Phase7 |
|------------|----------|--------|
| Cut direction | Configurable (flange_z or base_y) | Hardcoded base Y- (down) |
| Step axis | Single axis, mutually exclusive | Hardcoded base Z |
| Step sign | step_z < 0 for right-to-left | step_z < 0 for right-to-left |
| Cut mode | RT Cartesian (impedance preferred) | RT Cartesian (segmented) |
| Push axes | None | Base Z+ (right push), Base Z- (left push), Base Y+ (lift before push) |

## Motion Control Constraints

- **Impedance mode**: Preferred for cutting (compliance). Falls back to position mode on failure.
- **Position mode**: Used for free-space travel (Phase4/6 return-to-prepare).
- **Velocity limits**: max_linear_velocity (cut/retract/step), independent push speeds
- **Duration**: duration_s=0 → RT service auto-computes from path length + velocity/acceleration limits

## Real-Time / Threading Constraints

- perception pipeline: continuous, independent ROS nodes
- state machine: 0.5 Hz timer tick
- action servers: callback-based, non-blocking within each phase
- impedance fallback: per-segment (Phase7) or per-phase (Phase3/5)

## Config Constraints

- Config validated via YAML before launch
- phase5_second_cut has own independent parameter set (same structure as phase3_first_cut); both share build_cut_waypoints() script
- phase6_prepare only used when prepare_next_phase == PHASE_7
- All push speeds independently configurable from cutting speed
