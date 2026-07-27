# Requirements

## Project Summary

- Goal: Provide a dual-mode (Tkinter local + Web browser) GUI for dexbot operators to control xCore robot arms and CAN hands
- Users: dexbot operators using dual-arm hand-eye coordination
- Current stage: Phase 1-5 + Phase W complete; hardware testing pending

## Requirements

- GUI: split presentation code from robot control logic; share service layer between Tkinter and Web modes
- GUI: compact 3-column layout for Arm + Hand page, optimized for maximized windows
- GUI: side selector (Left/Right) binds arm+hand to the same side
- Backend: use xCore via `LbotRobot` facade (`lbot_robot_xcore.py`), not direct SDK calls
- Service layer: zero duplication of robot control logic between Tkinter and Web
- All geometric terms (axes, signs, plane selection) exposed as tunable parameters
- Depend on existing bottom/middle/high-layer packages as much as possible

## Task Scope

- In scope: GUI architecture (Tkinter + Web), arm control (jog/servo/RT/drag/comfort), hand control (CAN angles/poses)
- Out of scope: ROS parameter server stale state investigation (permanently blocked)

## Constraints

- Quaternion/rotation-matrix internal math; Euler only at final API call
- `change_tool_frame` only switches which point is controlled, not coordinate system interpretation
- Python 3.10+, ROS2, Tkinter, FastAPI
- Web: pure HTML/CSS/JS, no frontend framework
- Web session: 7-day httpOnly cookie
- Total users < 50

## Acceptance Criteria

- Phase 1: shell + page separation — completed
- Phase 2: compact "Arm + Hand" unified page with L/R side binding — completed
- Phase 3: hand control + arm presets + joint live readback — completed
- Phase 4: advanced arm controls (Servo/RT/Drag/Comfort) merged into first tab — completed
- Phase 5: all core arm+hand workflows in single layout; Tasks tab for heavy workflows — completed
- Phase W: Web GUI with login, per-user worker isolation, settings sync — completed
- Hardware testing: pending physical robot connection

## Decisions

See `business-logic/decision-records.md`

## Open Questions

See `business-logic/open-questions.md`

## Architecture Reference

See `architecture/software-architecture.md` for module boundaries and deployment design.
See `architecture/communication.md` for ROS2 service/topic mapping.
See `hardware/sdk-mapping.md` for xCore SDK and linkerbot hand SDK details.
