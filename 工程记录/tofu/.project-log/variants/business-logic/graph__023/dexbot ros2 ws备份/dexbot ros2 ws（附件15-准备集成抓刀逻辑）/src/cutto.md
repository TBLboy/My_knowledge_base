# Business Logic Graph

> Aligned with `phase_manager_node.py` as of 2026-05-17

## Main

```text
PHASE_IDLE → PHASE_1_GRAB_KNIFE → PHASE_2_MOVE_TO_PREPARE → PHASE_3_FIRST_CUT
    → PHASE_4_ROTATE_TOFU → PHASE_2_MOVE_TO_PREPARE (re-entry) → PHASE_5_SECOND_CUT
    → PHASE_6_ROTATE_TOFU → PHASE_2_MOVE_TO_PREPARE (re-entry) → PHASE_7_THIRD_CUT
    → PHASE_DONE
```

**Key**: Phase4 and Phase6 both loop back to Phase2 for re-prepare (视觉重新检测+刀重新就位). Phase2's exit target is determined by `ctx.prepare_next_phase`:
- Entry 1 (from Phase1): `prepare_next_phase = PHASE_3_FIRST_CUT`, publishes `/cutting_start`
- Entry 2 (from Phase4): `prepare_next_phase = PHASE_5_SECOND_CUT`, no `/cutting_start`
- Entry 3 (from Phase6): `prepare_next_phase = PHASE_7_THIRD_CUT`, no `/cutting_start`

## Branches

```text
None active.
```

## Archived

```text
None.
```

## Error Transitions

Any phase can transition to `PHASE_ERROR` on:
- Goal send exception (`"*_goal_send_failed"`)
- Goal rejected (`"*_goal_rejected"`)
- Result exception (`"*_result_failed"`)
- `result.success == False` (`"*_failed"`)

There is no automatic recovery from ERROR; manual intervention required via `/phase_jump` topic or `manual_override`.

## Transition Table

| From | To | Condition | Reason String |
|------|----|-----------|---------------|
| PHASE_1 | PHASE_2 | `auto_advance=True` AND `ctx.knife_grabbed==True` | `condition_met` |
| PHASE_2 | `ctx.prepare_next_phase` | Action result `success=True` | `phase2_done` |
| PHASE_3 | PHASE_4 | Action result `success=True` | `phase3_done` |
| PHASE_4 | PHASE_2 (re-entry) | Action result `success=True`; sets `prepare_next_phase=PHASE_5` | `phase4_done_reprepare` |
| PHASE_5 | PHASE_6 | Action result `success=True` | `phase5_done` |
| PHASE_6 | PHASE_2 (re-entry) | Action result `success=True`; sets `prepare_next_phase=PHASE_7` | `phase6_done_reprepare` |
| PHASE_7 | PHASE_DONE | Action result `success=True` | `phase7_done` |
| Any | PHASE_ERROR | Goal/result failure (see above) | `"*_failed"` |

## State Machine Notes

- Phases 3-7 have `can_enter=lambda ctx: False` — transitions are driven **imperatively** by result callbacks
- Only Phase1→Phase2 is **declarative** (via `_advance_if_ready`)
- Phase2 re-enters with different `prepare_next_phase` and uses different config: `phase2_prepare` (entries 1,2) vs `phase6_prepare` (entry 3)
- `publish_cutting_start=True` only for first Phase2→Phase3 transition
- `manual_override=True` with `manual_jump_phase != IDLE` locks the state machine to that phase (evaluated every 0.5s)
