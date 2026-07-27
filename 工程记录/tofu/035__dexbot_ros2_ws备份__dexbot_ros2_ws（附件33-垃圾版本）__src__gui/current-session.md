# Current Session

## Last Updated

- 2026-05-26 ~11:40 CST

## Current Objective

- Implement Dual-Arm Collaboration tab (replaces Tasks tab) in Tkinter GUI

## Current Business Logic Position

- Main path: A -> B -> C -> D -> E (all nodes implemented, stable)
- Main path (dual-arm): A -> DA -> DB -> DC -> DD -> E (new dual-arm nodes added)
- Current node: Dual-arm page nodes (DA, DB, DC, DD) complete
- Active branch: None

## Completed This Session

- **services/registry.py**: `get_ros_bridge()` now accepts optional `side` parameter (default "right"), maintaining two separate ROS bridges in a dict keyed by `"l"` / `"r"` with different node names.
- **services/arm/control.py**: `ArmControlService.__init__` now accepts optional `side="right"` parameter. Added `_bridge()` helper method; all methods now use `self._bridge()` instead of `self._services.get_ros_bridge()` directly.
- **web/worker.py**: Updated to pass `side=side` to `ArmControlService`. Removed `side` param from `ServiceRegistry()` call.
- **Hand Open/Close fix**: Swapped angle values in `pages/arm_hand.py` (Tkinter) and `web/worker.py` (Web GUI) — Open now sends `[100.0]*dof` (extend), Close sends `[0.0]*dof` (flex), matching SDK where 0=closed, 100=open.
- **pages/dual_arm.py** (NEW): `ArmSidePanel` — reusable side panel with State, Joints, Arm Presets, Drag, Hand, Hand Angles, Hand Poses. `DualArmPage` — container with shared model selector, left panel (arm_l/can1/192.168.2.160) and right panel (arm_r/can0/192.168.2.161).
- **pages/__init__.py**: Replaced Tasks tab with Dual Arm tab. Tab order: Arm+Hand / Dual Arm / Migration Plan / Legacy Boundary.
- **Hand pose directories**: Left O6 uses `poses/poses_o6_left/`, right uses `poses/poses_o6_right/` (solves O6 not distinguishing sides).

## Problems And Resolutions

- **`str` object not callable**: `self._hand_model` attribute shadowed `_hand_model()` method. Removed the attribute — hand model is always read from `_hand_model_var`.

## Verification

- `python3 -m py_compile` passes on all 23 Python files.
- GUI opens with correct 4 tabs: Arm+Hand, Dual Arm, Migration Plan, Legacy Boundary.

## Files Changed

- `services/registry.py` (modified)
- `services/arm/control.py` (modified)
- `web/worker.py` (modified — also applied hand Open/Close angle swap)
- `pages/dual_arm.py` (NEW)
- `pages/__init__.py` (modified)
- `pages/arm_hand.py` (modified — hand Open/Close angle swap)
- `.project-log/current-session.md` (rewritten)
- `.project-log/progress.md` (appended)
- `.project-log/business-logic/main.md` (updated)
- `.project-log/business-logic/graph.md` (updated)

## Current State

- Dual-arm collaboration tab implemented and compiles cleanly. Awaits hardware testing.

## Next Steps

1. Hardware test: verify both sides connect to respective arms/hands
2. Create initial arm preset files (`arm_preset/arm_poses_left.json`)
3. Verify drag mode on both arms
