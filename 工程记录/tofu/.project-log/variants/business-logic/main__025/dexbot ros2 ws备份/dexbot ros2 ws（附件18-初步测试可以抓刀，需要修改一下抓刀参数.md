# Main Business Logic

> Aligned with actual code as of 2026-05-19

## Status

- Current main path status: **Stable** (all 7 phases implemented, hardware-tested)
- Phase7 vertical cut rewritten and verified; impedance fallback bug fixed
- Phase1 grab-knife migration: **In design** (branch logic, not yet merged into main)

## Main Path

```text
PHASE_1_GRAB_KNIFE → PHASE_2_MOVE_TO_PREPARE → PHASE_3_FIRST_CUT
    → PHASE_4_ROTATE_TOFU → PHASE_2(re-entry) → PHASE_5_SECOND_CUT
    → PHASE_6_ROTATE_TOFU → PHASE_2(re-entry) → PHASE_7_THIRD_CUT
    → DONE
```

## Path Summary

- **Phase1**: Waits for external knife-grab signal. Three entry modes:
  - **Standalone**: `cuttofu_phase2.launch.py` → all nodes alive, waits for `/knife_grabbed` → auto-advance to Phase2
  - **Collaboration (legacy)**: `cuttofu_phase1_monitor.launch.py` → only monitor node alive → detects `/knife_grabbed` → spawns `cuttofu_phase2.launch.py start_phase:=PHASE_2_MOVE_TO_PREPARE`
  - **Migration (new)**: `cuttofu_phase1_grab.launch.py` → lifecycle wrapper launches `cuttofu_phase1_grab_internal.launch.py` as single subprocess containing ALL grab resources (RealSense camera + SAM3 wood_cleaver + pose_est + recognition + monitor + follow, all via embedded xCore SDK) → auto-executes 5-waypoint approach + O6 grasp + retract + joint home → publishes `/task/phase1_complete` → lifecycle wrapper kills subprocess (all grab nodes die: camera, SAM3, pose_est, GPU, CAN) → broadcasts `/task/phase1_complete` for 5s → self-exits → Phase1 monitor receives signal → buffers 0.5s → spawns Phase2 with brand-new vision pipeline + xcore_controller_node. Two processes fully isolated, zero shared nodes, single-topic communication.
- **Phase2**: Vision-guided prepare — knife moves to tofu right edge (entered 3 times)
- **Phase3**: First oblique cut — relative flange-Z cutting with step
- **Phase4**: Return to anchor, move to neutral pose, wait for user to rotate tofu, re-prepare. Manual jump mode skips return motion, only waits for continue file
- **Phase5**: Second oblique cut — same cutting script as Phase3, independent config parameters
- **Phase6**: Return to anchor, wait for second user rotation, re-prepare with vertical knife (phase6_prepare config). Manual jump mode skips return motion, only waits for continue file
- **Phase7**: Vertical cut (base Y- down, base Z step), mid-cycle push + tail push; knife lifts (push_lift_y) before each push to reduce friction
- **DONE**: All cuts complete

## Implementation Priority

- Current target edge: Phase7 verified (no pending issues)
- Current target node: PHASE_DONE

## Key Algorithms

### TCP Target Computation (tofu_geometry.py)
```
1. top_y = mean(corners_4[:, 1])                    # average Y of top corners
2. A, B = Z-largest 2 corners                        # right edge endpoints
3. v = AB direction in XZ plane, v.x > 0             # edge direction
4. l = perpendicular to v in XZ, l.z < 0             # left-pointing offset direction
5. D = (A + B) / 2                                  # right edge midpoint
6. D' = D + offset_a * l                            # horizontal offset
7. TCP = [D'.x, top_y + vertical_offset, D'.z]     # final TCP position
```

### Knife Rotation Matrix (tofu_geometry.py)
```
edge_align=true: tcp_Y = edge_dir, tcp_Z tilted by plane_angle_deg from horizontal normal
edge_align=false: tcp_Y = [1,0,0]=base_X, tcp_Z tilted by plane_angle_deg from vertical
```

### Cutting Waypoint Generation (cut_trajectory.py)
```
Phase3/5 (build_cut_waypoints):
  For each cycle: anchor_i → cut(cut_direction, cut_move) → retract → next_anchor(step)

Phase7 (build_vertical_cut_waypoints):
  For each cycle: anchor_i → cut(base Y-, cut_move) → retract → next_anchor(base Z, step_z)
  Push actions handled separately in action server with independent speeds
```

## Stable Assumptions

- Right arm: base X=forward, Y=up, Z=right
- Knife TCP = flange + tcp_offset (pure translation)
- Perception pipeline runs continuously, provides TofuState at 10 Hz
- Camera is eye-on-base (fixed external D435I), calibrated via hand-eye
- SAM3 text prompt "tofu" for auto-detection
- Phase5 intentionally reuses Phase3 trajectory (reuse_phase mechanism)
- **Phase1 migration**: Classmate's code runs in independent `ros2 launch` subprocess (internal launch file); resource cleanup guaranteed by subprocess death; Phase2 creates fresh instances; `/task/phase1_complete` is the sole communication channel; zero shared state between grab and Phase2

## Verification Status

| Phase | Hardware Tested | Notes |
|-------|-----------------|-------|
| Phase1 | ✅ (legacy) | knife_grabbed signal; migration pending |
| Phase2 | ✅ | IK valid, preview scoring |
| Phase3 | ✅ | Oblique cut verified |
| Phase4 | ✅ | Return + user wait |
| Phase5 | ✅ | Reuses Phase3 |
| Phase6 | ✅ | Return + user wait |
| Phase7 | ✅ | Vertical cut with push, 2026-05-17 |
| DONE | ✅ | Full chain completes |
