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

## Web Access Feature (Phase W)

### Context

Users access the GUI remotely from their own machines over LAN. Each user controls their own robot arm — not a shared robot. Users borrow the GUI functionality, not a shared robot instance. Less than 50 users total.

### Goal

Deploy the GUI as a **browser-accessible web application** on a server. Users open a URL in their browser and get the full GUI experience (all tabs, all controls, all functionality) without installing any client software.

### Constraints

- Server OS: Ubuntu 22.04
- Client OS: Ubuntu 22/24, Windows, iPad, mobile — browser only
- No plugins, no Java, no WebAssembly — pure HTML/CSS/JS
- Each user has their own isolated session bound to their own robot arm IP
- The Tkinter GUI and the web frontend share the same Python service layer (`services/arm/control.py`, `services/hand/control.py`) — logic is 100% identical
- Total users < 50

### Architecture

```
Client browser (any OS, any device)
    │
    │  HTTP / WebSocket
    ▼
┌──────────────────────────────────────────┐
│         FastAPI + Uvicorn server          │
│         (Ubuntu 22.04 server)             │
│                                          │
│  /ws/{username}   WebSocket (requires    │
│                      session cookie)     │
│  /api/login       POST username+password  │
│  /api/logout      POST                   │
│  /api/me          GET/PUT user settings  │
│                                          │
│  Each WebSocket connection spawns a      │
│  per-user subprocess:                     │
│    worker_{username}.py                 │
│      ├── ArmControlService (isolated)   │
│      ├── HandControlService (isolated)   │
│      └── bound to user's arm IPs         │
└──────────────────────────────────────────┘
    │
    ├── robot A (user A's arm)
    ├── robot B (user B's arm)
    └── robot N (user N's arm)
```

**Process-per-user isolation:** Each WebSocket connection spawns an independent `worker.py` subprocess. Processes do not share state. One crash affects only that user. No locks, no shared memory, no Redis needed.

**Authentication: username + password.** User DB on server (SQLite). User settings (arm IPs, side) stored per-username on server. Users log in from any browser/device and get their own saved config.

### Client Requirements

| Client device | Requirement |
|--------------|-------------|
| Ubuntu 22.04 / 24.04 | Browser (Firefox, Chrome) — zero install |
| Windows 10/11 | Browser — zero install |
| iPad / mobile | Browser — zero install |
| Any device with a browser | Works out of the box |

**Nothing to install on client machines.** User logs in with username + password. Settings stored server-side per user. Changing browser or device preserves all settings.

### File Structure

```
src/gui/
  services/          existing, reused verbatim
    arm/control.py
    hand/control.py
    registry.py

  web/               new
    server.py          FastAPI + WebSocket entry point
    worker.py          per-user subprocess, arm IPs bound to WS connection
    auth.py           login/logout/session cookie/password hash verification
    db.py             SQLite user DB (users table)
    templates/
      login.html        username + password form, link to register
      register.html     username + password + confirm password form
      settings.html     view/edit arm IP settings (left/right)
      index.html        main 3-column GUI mirroring Tkinter layout
    app.js            WebSocket command routing + DOM updates
    style.css
```

### Security Model

- `worker.py` listens on `127.0.0.1` only — not exposed externally
- `server.py` is the only publicly exposed component (port 80/443)
- Firewall: clients only reach server port 80/443
- No inbound access to robot subnets from client machines
- User passwords stored as SHA256 hashes (or bcrypt) in SQLite
- Session token via httpOnly cookie — user cannot inspect/modify token from JS
- Users self-register via `/register.html`; no admin SQL inserts needed
- First-time users: register → login → prompted to fill arm IPs in settings page before connecting to robot

### Service Layer Reuse

All robot logic in `services/arm/control.py` and `services/hand/control.py`. Both Tkinter GUI and web worker subprocess import these directly. **Zero duplication of robot control logic.**

### User Settings (stored server-side per username)

```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    arm_ip_left TEXT NOT NULL,
    arm_ip_right TEXT NOT NULL,
    default_side TEXT NOT NULL DEFAULT 'right',
    updated_at TIMESTAMP
);
```

Login → session cookie → user settings loaded from SQLite → WebSocket routed to user's arm IPs.
First login prompts settings page if IPs not yet set.
User can edit their own IPs from Settings page (POST /api/me).
No config files on client machines. Any browser, any device — same settings.

### Implementation Phases

**Phase W1 (1–2 days)**
- `web/db.py` — SQLite user table init, register/login/update helpers
- `web/auth.py` — login/logout endpoints, password hash verification, session cookie management
- `web/worker.py` — per-user subprocess, binds arm IPs from DB
- `web/server.py` — FastAPI + WebSocket + all templates
- `web/templates/login.html` — username + password form, link to register
- `web/templates/register.html` — username + password + confirm password form
- `web/templates/settings.html` — view/edit arm IP settings (left/right)
- Verify: one user registers, logs in, connects to their arm, issues world jog command, robot responds

**Phase W2 (2–3 days)**
- `web/templates/index.html` — 3-column layout mirroring Tkinter (Arm Ops / Servo/RT/Drag/Comfort / Hand Angles+Poses)
- `web/app.js` — WebSocket command routing, state updates, form submissions
- Verify: all Tkinter sections have HTML equivalents

**Phase W3 (1 day)**
- systemd service file
- nginx reverse proxy (port 80 → uvicorn)
- User guide: self-registration URL, how to change arm IPs in settings page

**Phase W4 (1 day)**
- Two users log in from two browsers, verify process isolation
- Verify: settings page saves IPs to SQLite, workers route to correct arms

### Open Questions

1. ~~Should each user have a login / password, or is config.yaml sufficient?~~ **Resolved: username + password, server-side SQLite per user.**
2. ~~Should the Tkinter GUI remain independently runnable alongside the web server?~~ **Resolved: yes, both runnable, same service layer.**
3. ~~Is there a preferred frontend framework (plain HTML/JS vs React/Vue)?~~ **Resolved: plain HTML + vanilla JS, no framework.**
4. ~~Should the admin UI for user management be a page or direct SQLite edits?~~ **Resolved: self-registration page, users register themselves.**
