# Debugging Lessons

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
