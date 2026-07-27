# Current Session

## Last Updated

- 2026-05-17 19:40 CST (Phase7 push-mid bug discovered)

## Current Objective

- Fix Phase7 impedance/position mode fallback bug causing mid-push to be skipped on retry.
- Implement SAM3 user-drawn box prompt for manual tofu re-segmentation.

---

## Completed This Session

### Phase7 Vertical Cut — Complete Rewrite (2026-05-17)

**Problem with old Phase7 logic**: Knife went UP before DOWN; push happened at surface level.

**New Phase7 logic** (per user spec):
- Standard cycle: cut (base Y-) → retract (base Y+) → step (base Z)
- Mid cycle (ci == cycles//2): after cut, push forward (Z+) → return → push backward (Z-) → return → retract → record mid_anchor
- Last cycle: cut → retract → move to mid_anchor → cut → push tail (Z-) → retract

**Config parameters** (`phase7_third_cut`):
| Parameter | Value | Meaning |
|-----------|-------|---------|
| cycles | 14 | Total cuts |
| cut_move | 0.04 m | Cut depth along base Y- |
| step_z | -0.005 m | Step per cycle along base Z- |
| push_forward_z | 0.01 m | Mid push forward (base Z+) |
| push_forward_speed | 0.01 m/s | Mid push forward speed |
| push_backward_z | -0.005 m | Mid push backward (base Z-) |
| push_backward_speed | 0.01 m/s | Mid push backward speed |
| push_tail_z | -0.01 m | Tail push (base Z-) |
| push_tail_speed | 0.01 m/s | Tail push speed |

**Files modified**:
- `cuttofo_config.yaml`: New phase7_third_cut parameters (removed press_normal, push_half_z, push_half_back_z)
- `cut_trajectory.py`: `build_vertical_cut_waypoints()` rewritten for new logic
- `knife_cut_action_server.py`: New `_execute_phase7_cut()` method with segmented execution and push speed control

### AABB Percentile Parameters (completed)
- 6 new params exposed: `y_filter_percentile`, `x_percentile_low/high`, `z_percentile_low/high`, `top_y_percentile`
- Chain: `cuttofo_config.yaml` → `cuttofu_phase2.launch.py` → `pose_estimator_node.py` → `vision_utils.py`

### Calibration App Tweaks
- `aruco_monitor.py`: `stability_threshold` 0.002→0.005m, `stability_rot_threshold_deg` 0.5→2.0
- `control_panel.py`: `min_frames` 5→15 for ArUco pose averaging

---

## Phase7 Execution Trace (cycles=14, mid_ci=7, last_ci=13)

```
anchor_0 (Z=0.151) at Phase6 end

Seg1 (22 waypoints, impedance):
  Cycle 0: anchor_0 → cut_0(Y-4cm) → retract_0 → step(Z-5mm) → anchor_1(Z=0.146)
  Cycle 1: anchor_1 → cut_1 → retract_1 → step → anchor_2(Z=0.141)
  ...
  Cycle 6: anchor_6 → cut_6 → retract_6 → step → anchor_7(Z=0.116)
  Cycle 7: anchor_7 → cut_7(Y-4cm) ← knife STOPS HERE at bottom

Mid-push (at cut_7 depth):
  push_forward: Z=0.116 → Z=0.126 (+10mm right)  @ 0.01 m/s
  push_forward_return: back to Z=0.116
  push_backward: Z=0.116 → Z=0.111 (-5mm left)  @ 0.01 m/s
  push_backward_return: back to Z=0.116

Seg2 (18 waypoints):
  Cycle 7 retract → step → Cycle 8...Cycle 13 cut
  Final position: cut_13 at anchor_13(Z=0.086)

Seg3 (1 waypoint):
  retract_13 → anchor_13

Tail-push:
  Move to mid_anchor (Z=0.086 → Z=0.116, right 30mm)
  tail_cut: mid_anchor → Y-4cm (down)
  push_tail: Z=0.116 → Z=0.106 (-10mm left) @ 0.01 m/s
  tail_retract: back to mid_anchor (Y+4cm up)
```

---

## BUG: Phase7 Mid-Push Skipped on Impedance→Position Fallback Retry

**Date discovered**: 2026-05-17

**Symptoms observed**:
1. Knife cuts normally for cycles 0-6
2. At cycle 7 (mid), push does NOT execute
3. Knife retracts, steps, and continues cutting cycles 7-13 normally
4. Push executes at the END (as tail push)

**Root cause**: `_execute_phase7_cut` is NOT idempotent. When impedance mode fails at the push-forward step, the outer `_execute_callback` retries the ENTIRE `_execute_phase7_cut`. But by this point:
1. seg1 has already completed (knife is at cut_7 = Y₀-0.04, stabbed into tofu)
2. Retry reads current flange pose via `arm.get_flange_pose()` — this returns cut_7 position (not original anchor_0)
3. Retry uses this wrong position as new `anchor_mat`, regenerating all waypoints from a shifted origin
4. Retry's seg1 attempts to move from cut_7 position to a new cut_0 position that is 4cm DEEPER than tofu — causing incorrect subsequent motions

**Log evidence**:
```
T+19s: seg1 (22 waypoints, impedance) → completed OK
T+19s: push-forward (impedance) → FAILED "该操作不允许在当前上下电状态下执行"
T+20s: RETRY — _execute_phase7_cut called again, reads flange pose at cut_7
T+20s: seg1 (retry, position) → re-executed from wrong position
       → push/re-tract/step/etc → eventually tail-push all succeed
```

**Affected files**:
- `knife_cut_action_server.py`: `_execute_phase7_cut()` and `_execute_callback()`

**Fix approach**:
- Record initial `anchor_mat` at the START of `_execute_phase7_cut`
- If any segment fails, do NOT re-read flange pose or re-run seg1
- Make impedance→position fallback happen WITHIN `_execute_phase7_cut` for each segment, not retry entire function
- OR: add a `_phase7_state` flag to track completed segments and skip them on retry

**Status**: Bug identified, fix NOT yet implemented

---

## Current Business Logic Position

- Main path: Phase1 grab → Phase2 prepare → Phase3 cut → Phase4 return+wait+rotate+re-prepare → Phase5 cut → Phase6 return+wait+rotate+re-prepare → Phase7 vertical cut → DONE.
- **Active bug**: Phase7 mid-push skipped on impedance→position fallback retry.
- Active edge: Phase7 = cut(Y-) → retract(Y+) → step(Z) × 14 cycles, mid push at cycle 7, tail push at end.
- Active branch: None.

---

## Problems Encountered

- **Phase7 mid-push skipped on retry**: `_execute_phase7_cut` not idempotent; impedance→position fallback re-reads flange pose from wrong position (cut_7 instead of anchor_0), causing incorrect waypoint regeneration.
- Phase2 IK `valid=0`: all 263 seeds rejected by strict pos/rot error thresholds. Likely cause is `edge_align=true` + `offset_a=0` making target too constrained.

---

## Verification

- `colcon build --packages-select cuttofo_xcore` succeeded (0.46s, no errors).
- `build_vertical_cut_waypoints()` verified via Python import test — waypoints correct.
- `_execute_phase7_cut()` method present and properly structured.
- Phase7 hardware run: 49 total motion steps executed successfully (with retry fallback).
- Calibrations: `stability_threshold=0.005m`, `stability_rot_threshold_deg=2.0`, `min_frames=15`.

---

## Next Steps

### Phase7 bug fix (immediate)
1. Make `_execute_phase7_cut` idempotent: record initial `anchor_mat`, skip seg1 on retry
2. OR move impedance→position fallback INTO `_execute_phase7_cut` per-segment
3. Test on hardware to verify mid-push executes correctly on first attempt

### SAM3 point prompt (planned)
1. `camera_viewer_node.py`: `cv2.setMouseCallback` + 坐标映射 + 绿色十字 + 发布 `/sam3/point_prompt`
2. `sam3_detector_node.py`: 推理锁 + 订阅 `/sam3/point_prompt` + bbox扩展 + `segment(image, [bbox])`
3. 验证: 点击豆腐 → 橙色 mask → 下游 tofu_state 更新
