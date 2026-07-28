# Business Logic Decision Records

## 2026-04-28 - GUI Architecture: Shell + Pages + Services

- Decision: Create standalone GUI shell in `src/gui/` with shell/pages/services/config package split, instead of editing the legacy monolith first.
- Context: Legacy `arm_hand_gui.py` was 3477 lines, mixing UI and logic. Needed clean separation.
- Alternatives considered:
  - Refactor in-place in legacy file
  - Create parallel new GUI and migrate gradually
- Reason: Parallel new GUI allows incremental migration without breaking existing functionality.
- Evidence / Verification: `python3 -m py_compile` on all new files passes; GUI opens with correct tabs.
- Impacted nodes: A, B
- Impacted edges: A->B
- Status: active

## 2026-04-28 - Service Layer: Reuse RosServiceBridge from dexbot_toolbox

- Decision: Reuse `dexbot_toolbox.gui.arm_hand_gui.RosServiceBridge` as the initial shared service adapter via lazy loading in ServiceRegistry.
- Context: Need ROS service access without duplicating connection logic.
- Alternatives considered:
  - Write new ROS bridge from scratch
  - Use rclpy directly in each page
- Reason: Existing RosServiceBridge already handles service creation, waiting, and calling.
- Evidence / Verification: Service calls work in GUI tests.
- Impacted nodes: A, B
- Impacted edges: A->B, B->C
- Status: active

## 2026-04-28 - xCore Backend via LbotRobot Facade

- Decision: Use xCore backend via `LbotRobot` facade (`lbot_robot_xcore.py`), not direct xCore SDK calls.
- Context: Need consistent API across different arm backends.
- Alternatives considered:
  - Direct xCore SDK calls
  - lbot backend
- Reason: LbotRobot facade provides unified interface, handles SDK quirks internally.
- Evidence / Verification: Examined `lbot_robot.py` and `lbot_robot_xcore.py` source.
- Impacted nodes: B, C
- Impacted edges: B->C
- Status: active

## 2026-04-28 - 3-Column Compact Layout for Arm+Hand Page

- Decision: Merge all arm+hand controls (basic + advanced) into a single 3-column compact layout optimized for maximized windows.
- Context: Previous design had separate tabs for advanced controls, requiring tab switching during operation.
- Alternatives considered:
  - Separate Advanced Arm tab
  - Collapsible sections
- Reason: Single layout reduces tab switching, maximizes visible controls at once.
- Evidence / Verification: GUI renders correctly in maximized window.
- Impacted nodes: B
- Impacted edges: A->B
- Status: active

## 2026-04-29 - Web GUI: Process-per-User Isolation

- Decision: Each WebSocket connection spawns an independent `worker.py` subprocess. Single uvicorn process (--workers 1).
- Context: Need multi-user web access with isolation.
- Alternatives considered:
  - Shared state with locks
  - Multiple uvicorn workers
  - Redis-based message queue
- Reason: Process isolation is simplest, one crash doesn't affect others, no locks needed.
- Evidence / Verification: Worker subprocess model verified in code.
- Impacted nodes: A, B
- Impacted edges: A->B
- Status: active

## 2026-04-29 - Web GUI: Self-Registration with SQLite

- Decision: Users self-register via web interface, settings stored in SQLite per user.
- Context: Need user management for <50 users.
- Alternatives considered:
  - Admin creates users via SQL
  - LDAP/OAuth integration
  - config.yaml per user
- Reason: Self-registration is simplest for small user base, no admin overhead.
- Evidence / Verification: Registration flow implemented and tested.
- Impacted nodes: A
- Impacted edges: A->B
- Status: active

## 2026-05-18 - Safe Buttons: E-Stop and Stop Motion Never Disabled

- Decision: E-Stop and Stop Motion buttons are marked as `safe=True` and are never disabled during `_run_async` busy state.
- Context: During World Jog or any motion operation, all buttons were disabled including E-Stop — critical safety bug.
- Alternatives considered:
  - Separate E-Stop thread that bypasses busy check
  - Global keyboard shortcut for E-Stop
- Reason: Separating safe buttons into `_safe_buttons` list is cleanest, minimal code change.
- Evidence / Verification: `python3 -m py_compile` passes; code review confirms safe buttons excluded from disable loop.
- Impacted nodes: B, C
- Impacted edges: B->C
- Status: active
