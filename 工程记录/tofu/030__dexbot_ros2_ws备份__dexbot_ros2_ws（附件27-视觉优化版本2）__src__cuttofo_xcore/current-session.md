# Current Session

## Last Updated

- 2026-05-24 14:30 CST

## Current Objective

- Add U/V coordinate axes visualization in RViz for constrained_obb mode.

## Current Business Logic Position

- Main path: PHASE_1 -> PHASE_2 -> PHASE_3 -> PHASE_4 -> PHASE_2(re-entry) -> PHASE_5 -> PHASE_6 -> PHASE_2(re-entry) -> PHASE_7 -> DONE
- Current node: PHASE_2_MOVE_TO_PREPARE (tested with constrained OBB vision + Phase6 override)
- Active branch: `feature-constrained-obb-vision` (implemented, hardware-validated for Phase6→Phase2 path)
- Active branch purpose: Replace vision pipeline within PHASE_2 with constrained OBB to improve stability and tightness of `top_corners` and `edge_dir`; clarified objective is top-surface ABCD footprint accuracy, not full-body 3D enclosure.

## Completed This Session

- **U/V axes visualization in RViz**: When `corner_mode: constrained_obb`, tofu_visualizer_node now draws red U-axis arrow + "U" label and green V-axis arrow + "V" label from tofu center (4 corners centroid). U = edge_dir (long axis), V = cross(Y_up, U) (short axis), arrow length 0.04m. Controlled by `show_uv_axes` parameter, automatically enabled by launch file when `corner_mode == "constrained_obb"`.
- Hardware test of Phase6 vision override: async 5-step state machine verified working, IK found valid candidates (min_margin=30.59°), no deadlock.
- Fixed Phase2 IK failure caused by `vertical_offset=0.35` (restored to 0.037).
- Relaxed IK joint safety margin from 15° to 10° for both Phase2 and Phase6 prepare.
- Added `tofu_debounce_s: 0.5` config parameter under `cutting.phase2_prepare` — phase_manager waits 0.5s after Phase2 entry before sending prepare goal, allowing tofu marker to stabilize.
- Debounce applies to all Phase2 entry paths: first entry, Phase4→Phase2 re-entry, Phase6→Phase2 re-entry.
- **Bug fix: manual_override path for Phase4/Phase6**: `reason in ("manual_topic_jump", "manual_override")` — previously `manual_override` did not set `skip_return_motion=True`, causing Phase4/Phase6 to auto-send cut goals on parameter-based jumps.
- **Continue file cleanup fix**: Added `os.unlink()` (wrapped in `try/except OSError`) after file detection in both `_tick_phase6_return` and `_tick_phase4_return`, immediately before the phase transition. Prevents stale file from triggering automatic re-jump on subsequent normal Phase6/Phase4 entry.

## Problems And Resolutions

- Phase2 IK failed with 63/63 seeds rejected. Root cause: `vertical_offset=0.35` (35cm) too high. Restored to 0.037.
- Tofu marker unstable at Phase2 entry — resolved with 0.5s debounce buffer before sending prepare goal.
- Manual jump via `phase_manager_node.set_phase` service with `reason="manual_override"` did not skip return motion for Phase4/Phase6 — fixed by extending reason check to include `"manual_override"`.
- Continue file persisted after consumption caused automatic re-jump on subsequent normal Phase entry — fixed by adding `os.unlink()` after file detection in both return tick functions.

## Verification

- Syntax check passed: `python3 -m py_compile` on `tofu_visualizer_node.py`.
- Build passed: `colcon build --packages-select cuttofo_xcore`.

## Files Changed

- `src/cuttofo_xcore/cuttofo_xcore/tofu_visualizer_node.py`
- `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`
- `src/cuttofo_xcore/launch/viz_display.launch.py`
- `.project-log/progress.md`
- `.project-log/current-session.md`

## Current State

- U/V axes visualization: implemented, build-verified. RViz shows red U + green V arrows from tofu center when `corner_mode: constrained_obb`.
- Phase6 vision override: hardware-verified, async state machine functional.
- Phase2 tofu debounce: implemented, build-checked, not yet hardware-validated.
- IK joint margin relaxed to 10° for Phase2/Phase6 prepare.
- manual_override reason bug fixed for Phase4/Phase6 skip_return_motion.
- Continue file cleanup (os.unlink) fixed in both _tick_phase6_return and _tick_phase4_return.
- Full pipeline (Phase1→Phase7) hardware test pending.

## Next Steps

1. Hardware test full pipeline: Phase1 → Phase2 → Phase3 → Phase4 → Phase2(re-prepare) → Phase5 → Phase6 → Phase2(re-prepare) → Phase7.
2. Tune `cutting.phase6_vision` independently for second prepare.
