# Main Business Logic

> Aligned with actual code as of 2026-05-17

## Status

- Current main path status: **Stable** (all 7 phases implemented, hardware-tested)
- Phase7 vertical cut rewritten and verified; impedance fallback bug fixed

## Main Path

```text
PHASE_1_GRAB_KNIFE → PHASE_2_MOVE_TO_PREPARE → PHASE_3_FIRST_CUT
    → PHASE_4_ROTATE_TOFU → PHASE_2(re-entry) → PHASE_5_SECOND_CUT
    → PHASE_6_ROTATE_TOFU → PHASE_2(re-entry) → PHASE_7_THIRD_CUT
    → DONE
```

## Path Summary

- **Phase1**: Waits for external knife-grab signal. Two launch modes: standalone (all nodes alive, waits for /knife_grabbed) or collaboration (monitor only, leaves camera/SAM3 free for classmate's grab-knife program)
- **Phase2**: Vision-guided prepare — knife moves to tofu right edge (entered 3 times)
- **Phase3**: First oblique cut — relative flange-Z cutting with step
- **Phase4**: Return to anchor, move to neutral pose, wait for user to rotate tofu, re-prepare. Manual jump mode skips return motion, only waits for continue file
- **Phase5**: Second oblique cut — same cutting script as Phase3, independent config parameters
- **Phase6**: Return to anchor, wait for second user rotation, re-prepare with vertical knife (phase6_prepare config). Manual jump mode skips return motion, only waits for continue file
- **Phase7**: Vertical cut (base Y- down, base Z step), mid-cycle push + tail push
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

## Verification Status

| Phase | Hardware Tested | Notes |
|-------|-----------------|-------|
| Phase1 | ✅ | knife_grabbed signal |
| Phase2 | ✅ | IK valid, preview scoring |
| Phase3 | ✅ | Oblique cut verified |
| Phase4 | ✅ | Return + user wait |
| Phase5 | ✅ | Reuses Phase3 |
| Phase6 | ✅ | Return + user wait |
| Phase7 | ✅ | Vertical cut with push, 2026-05-17 |
| DONE | ✅ | Full chain completes |
