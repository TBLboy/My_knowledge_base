# Software Architecture

## Overview

Dexbot Arm-Hand GUI provides two modes (Tkinter local, Web browser) sharing a single service layer.

```
┌─────────────────┐     ┌──────────────────┐
│   Tkinter GUI   │     │   Web Browser    │
│   (main.py)     │     │   (index.html)   │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│          services/ (shared)              │
│  arm/control.py  │  hand/control.py      │
│  registry.py     │  logger.py            │
└─────────────────────────────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│  RosService     │     │  worker.py       │
│  Bridge         │     │  (subprocess)    │
│  (toolbox)      │     │  stdin/stdout    │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│          ROS2 + xCore SDK + CAN          │
│  /robot/* services  │  linkerbot hand    │
└─────────────────────────────────────────┘
```

## Module Boundaries

| Module | Responsibility | Location |
|--------|---------------|----------|
| `main.py` | Tkinter entry point | gui/main.py |
| `app/shell.py` | Tkinter shell, mode sidebar, notebook container | gui/app/shell.py |
| `pages/arm_hand.py` | Main control page (3-column layout) | gui/pages/arm_hand.py |
| `pages/tasks.py` | Slice Cycle task page | gui/pages/tasks.py |
| `pages/migration.py` | Migration plan page | gui/pages/migration.py |
| `pages/legacy.py` | Legacy boundary page | gui/pages/legacy.py |
| `services/arm/control.py` | Arm control (jog, servo, RT, drag, comfort) | gui/services/arm/control.py |
| `services/hand/control.py` | CAN hand control (connect, angles, poses) | gui/services/hand/control.py |
| `services/registry.py` | Workspace path resolver, RosServiceBridge lazy loader | gui/services/registry.py |
| `services/logger.py` | Unified logging (TimedRotatingFileHandler) | gui/services/logger.py |
| `config/modes.py` | AppMode definitions (XCORE/LBOT) | gui/config/modes.py |
| `web/server.py` | FastAPI entry point, HTTP + WebSocket | gui/web/server.py |
| `web/worker.py` | Per-user subprocess, stdin/stdout JSON relay | gui/web/worker.py |
| `web/auth.py` | Login/logout, httpOnly session cookie | gui/web/auth.py |
| `web/db.py` | SQLite user database | gui/web/db.py |
| `web/app.js` | WebSocket command routing, DOM updates | gui/web/app.js |

## Threading Model

| Thread | Purpose | Created By |
|--------|---------|-----------|
| Main (Tkinter) | UI event loop, after() callbacks | tkinter.Tk.mainloop() |
| Operation threads | Background arm/hand operations | `_run_async()` via threading.Thread |
| Joint polling | 500ms interval joint state reading in a daemon worker | `_poll_joints()` + `after(0, ...)` |
| Worker subprocess | Per-user web session | subprocess.Popen in server.py |

## GUI / Business Logic Separation

- **GUI code** (`pages/`, `app/shell.py`): handles presentation, user interaction, event triggering
- **Business code** (`services/`): implements robot control logic, ROS service calls, SDK interactions
- **Connection**: GUI calls service methods directly; services return results or raise exceptions
- **Async pattern**: `_run_async()` wraps service calls in background threads, updates UI via `after()`

## Deployment

- **Tkinter**: `python3 src/gui/main.py` (requires ROS2 environment)
- **Web**: `uvicorn web.server:app --host 0.0.0.0 --port 80` (optionally with nginx + systemd)
