# Branch: Tofu Fall Detection for Phase7 Mid-Push

## Status

- draft

## Purpose

Add visual feedback to Phase7 mid-cycle rightward push: detect when the right-half tofu has fallen over, then stop pushing early. This avoids hardcoded push distance that may not always topple the tofu.

## Start Node

- PHASE_7_THIRD_CUT (during mid-push, after seg1 cut at mid-cycle)

## Target Node

- PHASE_7_THIRD_CUT (continue to push-backward after fall detected)

## Background

Phase7 cuts vertically from right to left. At the mid-cycle point, the knife pushes rightward (base Z+) to topple the right-half tofu, then pushes leftward (base Z-) to support the left half. Currently the push distances are fixed. A visual fall detector lets the push adapt to real tofu behavior.

## Logic Path

```text
PHASE_7_THIRD_CUT (mid-push start)
  → [Current flow: seg1 → push_fwd(fixed distance) → return → push_back → return → seg2]
  → [New flow:      seg1 → push_fwd_visual(fall_detected? stop) → return → push_back → return → seg2]
```

## Execution Chain

### Baseline Capture

When the knife reaches cut depth at mid-cycle (after seg1 completes, before any push):

1. Send a detect-fall request to a visual service / node
2. The service captures a baseline point cloud of the right-half tofu
3. Baseline stored in memory: `x_right_low_0`, `x_right_low_edge_0`, `visible_voxels_0`
4. After baseline captured, start pushing rightward

### Per-Frame Detection (runs at ~5-10Hz during push)

For each frame during rightward push:

1. Get SAM3 mask of tofu
2. Back-project depth to point cloud
3. Transform to base frame
4. Remove: desk plane, knife/hand region, keep only right-half ROI
5. Voxelize at 3mm
6. Compute 5 features against baseline:

| # | Feature | Symbol | Meaning | Threshold |
|---|---------|--------|---------|-----------|
| 1 | Signed tilt angle | `theta_signed` | Is tofu leaning right? | `> 12°` |
| 2 | Right-low occupancy | `right_low_ratio` | Material in right-low area? | `> 0.38` |
| 3 | High residual | `high_ratio` | Is tall upright material gone? | `< 0.30` |
| 4 | Right-low edge expansion | `dx_right_low_edge` | Has material spread rightward? | `> 0.12 * H0` |
| 5 | Visibility ratio | `visible_ratio` | Is point cloud reliable? | `> 0.50` |

7. Combine: `fallen_right = visible_ok AND high_ok AND right_low_ok AND (theta_ok OR edge_ok)`
8. Continuous frame confirmation: 6 out of recent 8 frames meet `fallen_right`
9. When confirmed, signal "fall detected" → stop rightward push, proceed to return

### Fallback

If fall NOT detected and push distance reaches configurable max (e.g. `push_forward_z * 2`), stop anyway (safety limit).

## Inputs

- `/camera/camera/color/image_raw` (for SAM3)
- `/camera/camera/aligned_depth_to_color/image_raw` (for point cloud)
- `/camera/camera/aligned_depth_to_color/camera_info` (intrinsics)
- Phase7 config: `push_forward_z` (max push distance as safety limit)
- Actual push distance feedback from robot (to stop at max)

## Outputs

- "fall detected" signal → return from push → proceed to push-backward

## Assumptions

- SAM3 segmentation and depth projection run at 5-10Hz during push
- Desk plane removal is reliable
- Knife/hand region can be masked out (or is small relative to FOV)
- Tofu right-half ROI is predictable based on knife position + base frame
- H0 (tofu height) available from tofu_state.extents[1]
- z_table (desk height) can be computed from baseline point cloud z_min

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| SAM3 detection loss during push | fall never detected → pushes to max distance | `visible_ratio` tolerance; keep last_valid result for 0.5s; max distance safety limit |
| Knife occludes tofu right half | point cloud missing → false negative | Capture baseline at anchor height (after retract), not at cut depth |
| Desk plane removal inaccurate | point cloud includes desk → wrong features | Use percentile filtering (z_min based) |
| Depth noise from knife surface | spurious points near knife | Ignore region near known knife position |
| H0 from tofu_state may be stale | feature thresholds wrong relative to actual size | H0 from baseline frame's extents, not from earlier Phase2 |

## Open Questions

- (See open-questions.md Q-20260518-001 through Q-20260518-006)

## Verification Plan

1. Offline: record bag file of Phase7 push sequence → replay through fall detector → confirm correct detection
2. Hardware: run Phase7 with fall detector → observe correct stop timing

## Merge Condition

- Verified on hardware: fall detector triggers correctly for real tofu
- False positive rate: < 1 per 10 pushes
- Fallback distance reached only when tofu is too large/stiff to topple

## Notes

- Feature thresholds (12°, 0.38, 0.30, 0.12*H0) are initial values; may need hardware tuning
- Continuous frame window: 6/8 recommended; 5/5 alternative if more responsive behavior needed
- Detection runs AS A SEPARATE NODE, not inside knife_cut_action_server, to avoid blocking the cut action
- Communication: ROS2 service or action from knife_cut_action_server to fall_detector_node
