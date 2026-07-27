# Debugging Lessons

## Lesson: hook_lift-ik-margin-vs-pose-tolerance

- Symptom: `second_cross_cut` aborts before any arm motion with `hook_lift_ik_failed_cycle_1: waypoint 2`.
- Root cause: `hook_lift_solver` fails when `pos_err > 0.1mm` or `rot_err > 0.06°`, independent of `safety_margin_deg`. Lowering margin 5°→3° shrinks errors (7.6mm→2.9mm) but may still fail the hard tolerance.
- Failed attempts:
  - Only changing `safety_margin_deg` expecting full pass.
- Final resolution: Unresolved; need relax `POS_TOL`/`ROT_TOL` and/or tune `hook_target_plane_angle_deg`, `hook_dy_m`, `second_cut.target_offset_m`.
- Verification: Two field runs 2026-06-11 with orchestrator log `TCUT-HOOK_LIFT-IK`.
- Reusable lesson: Distinguish joint-limit margin tuning from IK pose convergence tolerance; read both numbers in the error line.
- Evidence refs:
  - progress.md 2026-06-11 (per-cycle handoff entry)
  - debugging/known-issues.md hook_lift IK section

## Lesson: config-surface-is-not-runtime-behavior

- Symptom: A parameter appears in config and looks like the obvious tuning knob, but changing it does not reliably explain or control runtime behavior.
- Root cause: Runtime ownership is split across YAML, launch files, action-goal propagation, profile resolution, and node-side reads, so the visible config surface is only part of the real control path.
- Failed attempts:
  - Starting from YAML declarations alone.
  - Inferring behavior from parameter names without tracing final consumers.
- Final resolution: Trace the parameter end to end from declaration to runtime consumer and verify behavior at the actual execution path.
- Verification: Multiple CutTofo investigations converged only after walking the consumer chain across orchestrator, prepare, and cut execution layers.
- Reusable lesson: In layered robotics systems, config debugging should start with ownership tracing, not with blind tuning.
- Evidence refs:
  - progress.md entries around 2026-06-07 17:35 CST, 2026-06-07 18:05 CST, and 2026-06-08 current CST
  - config/config-schema.md
