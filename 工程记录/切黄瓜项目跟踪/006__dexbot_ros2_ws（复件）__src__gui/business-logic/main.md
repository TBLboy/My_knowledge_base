# Main Business Logic

## Status

- Current main path status: Stable (all phases implemented, hardware testing pending)

## Main Path

```text
A (GUI Shell Ready) -> B (Arm+Hand Page Ready) -> C (Operations Executed) -> D (State Updated) -> E (Session Closed)
```

## Path Summary

- A: GUI Shell initialized, mode selected (XCORE/LBOT), Notebook tabs built (Arm+Hand / Tasks / Migration Plan / Legacy Boundary)
- B: Arm + Hand page loaded with 3-column layout, side selected (L/R), ArmControlService + HandControlService created, joint polling started
- C: User operation executed via `_run_async` (arm: enable/disable/estop/jog/servo/RT/drag/comfort/presets; hand: connect/angles/poses)
- D: UI status variables updated, joint readback refreshed at 500ms, pose/preset lists refreshed if needed
- E: Window closed, `ServiceRegistry.shutdown()` called, ROS bridge released, hand disconnected if connected

## Implementation Priority

- Current target node: All nodes implemented
- Current priority: Hardware testing and bug fixes
- Active edge: B -> C (safe-button fix applied 2026-05-18)

## Stable Assumptions

- xCore backend via `LbotRobot` facade (`lbot_robot_xcore.py`)
- ROS2 services under `/robot/*` namespace (prefixed with `arm_r`/`arm_l`)
- CAN hand via `linkerbot` SDK (O6/L25/L20lite)
- Dual-arm support via side selection (left/right) in single process
- Service layer shared between Tkinter and Web — zero duplication
- `_run_async` dispatches all operations to background threads
- Safe buttons (E-Stop, Stop Motion) are never disabled during busy state

## Verification Status

- Tkinter GUI: `python3 -m py_compile` passes on all files; GUI opens with correct tabs; NOT tested with hardware
- Web GUI: `python3 -m py_compile` passes on all files; login/registration flow verified; WebSocket connection verified; NOT tested with hardware
- Hardware testing: pending physical robot connection

## Notes

- Business logic derived from existing codebase analysis (2026-05-18)
- Web GUI follows same main path but with additional auth/settings steps before node B
