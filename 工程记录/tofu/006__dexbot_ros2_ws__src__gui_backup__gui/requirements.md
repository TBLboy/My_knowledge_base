# Requirements

## Project Summary

- Goal: Optimize/refactor the `arm_hand_gui.py` GUI application into a normalized multi-mode architecture
- Users:dexbot operators using dual-arm hand-eye coordination
- Current stage: Phase 1 shell scaffolding in progress

## Requirements

- Create `demo_adjust_knife_pose_xcore.py` knife pose adjustment script for xCore robot
- Design a normalized multi-mode GUI architecture to unify scattered per-task GUI implementations
- Use xCore backend (`DEXBOT_ARM_BACKEND=xcore`), NOT lbot backend
- All geometric terms (axes, signs, plane selection) must be exposed as tunable parameters
- GUI: keep existing Tkinter visual style, split GUI code from logic code
- GUI: left sidebar for Lbot/XCore mode selection, top tab bar for functional pages
- GUI: first tab is "Arm + Hand" unified page; side selector (Left/Right) binds arm+hand to the same side; no large descriptive text inside tabs; compact layout
- Use `LbotRobot` facade (not xcore SDK direct) for the knife pose script
- New GUI development should depend on existing bottom/middle/high-layer packages as much as possible
- New GUI development should depend on existing bottom/middle/high-layer packages as much as possible

## Task Scope

- In scope: Knife pose script, GUI architecture design and refactoring
- Out of scope: ROS parameter server stale state investigation (permanently blocked)

## Constraints

- Quaternion/rotation-matrix internal math; Euler only at final API call
- `change_tool_frame` only switches which point is controlled, not coordinate system interpretation
- "沿工具某轴移动" requires manual vector math: extract tool axis, multiply by distance, add to position
- `project-log` skill not loading in current session

## Acceptance Criteria

- `demo_adjust_knife_pose_xcore.py` passes syntax check and `--dry-run`/`--skip-motion`
- GUI architecture decision documented and approved by user
- Phase 1 (shell + page separation) of GUI refactoring completed
- Phase 2: rebuild first tab into compact "Arm + Hand" unified page with left/right side binding, no long description text, compact layout; delete Overview tab
- Phase 3: first tab also supports minimal hand control, arm preset record/list/select/execute/delete, hand pose save/load/load+apply, hand pose delete, arm preset sequence run, joints panel with live readback, hand open/close, hand sequential execution
- Phase 4: merged with Phase 3 — all advanced arm controls (Servo Mode, RT Follow, Drag SDK, Comfort, Collision) are now in the first tab via a 3-column compact layout optimized for maximized windows
- Phase 5+: first tab now covers all core arm+hand operator workflows (basic + advanced) in a single maximized-friendly layout; Tasks tab holds Slice Cycle for heavy workflows; remaining optional features (remote hand topics, slice broadcast, eye_on_base) are deferred

## Decisions

- xcore backend via `LbotRobot` facade, not lbot backend — confirmed by examining `lbot_robot.py` and `lbot_robot_xcore.py`
- GUI refactoring: shell + pages + controllers/services分层 architecture recommended
- Step 1 will create a standalone GUI shell in `src/gui/` instead of editing the legacy monolith first
- Step 1 reuses `dexbot_toolbox.gui.arm_hand_gui.RosServiceBridge` as the initial shared service adapter
- Single process for dual-arm vs two separate instances: to be confirmed by user
- Lbot/XCore share most pages or have completely separate page sets: to be confirmed by user

## Open Questions

- User confirmation needed: single process for dual-arm vs two separate instances?
- User confirmation needed: Lbot/XCore share most pages or have completely separate page sets?
- `package://ar5_description` RViz error (stale ROS parameter server state) — permanently blocked, not resolvable from workspace
