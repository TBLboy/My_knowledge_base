# Open Business Logic Questions

## Active Questions

### Q-20260517-001: Phase2 IK Validity

- Related edge: edge_2_prepare
- Question: Phase2 IK sometimes returns valid=0 (all 263 seeds rejected). Likely cause: edge_align=true + offset_a=0 making target too constrained. Is this consistently happening or intermittent?
- Why it matters: Blocks Phase2 entry; no manual fallback path in current code.
- Options: Relax POS_TOL_M / ROT_TOL_RAD; increase offset_a; disable edge_align for testing.
- Status: Open

### Q-20260517-002: Impedance Mode Stability

- Related edge: edge_3_to_4, edge_7_to_done
- Question: Impedance mode fails sporadically with "该操作不允许在当前上下电状态下执行". Is this a robot controller firmware bug, power-state issue, or joint limit trigger?
- Why it matters: Causes impedance→position fallback; position mode provides less compliance during cutting.
- Options: Investigate robot power state transitions; check joint limit proximity during extended cuts.
- Status: Open (fallback handles it gracefully)

### Q-20260517-003: Perception Health Recovery

- Related edge: edge_perception
- Question: When perception health is STALE or LOST, does Phase2/6 re-prepare correctly handle it? Is there a manual override for retrying detection?
- Why it matters: If SAM3 loses the tofu after rotation, system is stuck at Phase2.
- Options: Implement manual point-prompt (sam3-point-prompt branch); add timeout + retry logic.
- Status: Open

## Resolved Questions

- ✅ Phase7 vertical cut direction (was fan-ge_Z press, now base Y- cut) — resolved 2026-05-17
- ✅ Phase7 push timing (was at surface, now at cut depth) — resolved 2026-05-17
- ✅ Phase7 impedance fallback idempotency (was outer retry from wrong anchor) — resolved 2026-05-17
- ✅ Phase7 speed control (push speeds independent from cut speed) — resolved 2026-05-17
