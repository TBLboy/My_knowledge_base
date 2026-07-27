# Current Session

## Last Updated

- 2026-04-29 13:40 Local Time

## Current Objective

Phase W1/W2/W3 code and deployment configs complete. Cookie+WebSocket auth fully debugged. WebSocket auth flow: cookie (login) → URL ?token= (redirect) → window.WS_TOKEN (HTML) → WebSocket query param. arm_ip must be set in Settings before WebSocket connects. Phase W4 deferred — requires real robot hardware.

## Current Objective

Phase W1/W2/W3 code and deployment configs complete. Cookie+WebSocket auth fixed (httpOnly cookie → URL token → sessionStorage → WebSocket query param). Browser testing in progress. Phase W4 deferred — requires real robot hardware.

## Completed This Session

- Created `.project-log/` directory structure in `/home/tbl/Project/dexbot_ros2_ws/src/gui/`
- Inspected the existing GUI and reusable package boundaries across dexbot bottom/middle/high/toolbox layers
- Added a new standalone GUI shell with mode sidebar, tabbed page area, and a shared service registry
- Reused `dexbot_toolbox.gui.arm_hand_gui.RosServiceBridge` as the initial ROS service adapter for the new shell
- Added an `Arm Control` tab that reuses `RosServiceBridge` for state refresh, enable/disable, clear errors, and estop/recover actions
- Reorganized `src/gui/` into `app/`, `pages/`, `services/`, and `config/` packages
- Removed the explanatory text block from the left mode sidebar so the menu consumes less horizontal space
- Extracted `Arm Control` ROS operations into `services/arm/control.py`
- Expanded `Arm Control` with configurable world-frame jog controls and six jog direction buttons
- Reviewed README documentation and legacy arm_hand_gui.py to plan the unified Arm + Hand tab architecture
- Deleted the `Overview` tab and replaced the first tab with a compact `Arm + Hand` unified page
- Added side-bound hand control to the first tab: connect/disconnect, sliders, apply, readback, torque preset, and hand pose save/load/load+apply
- Added a dedicated `services/hand/control.py` adapter so hand logic stays out of the page layer
- Added a compact `Arm Presets` section to the first tab: record, list, select, prev/next, execute, delete, refresh, and speed control
- Extended `services/arm/control.py` with reusable arm bank load/save/id/record/execute helpers
- Added `_poll_joints()` at 80ms intervals for live joint degree readback
- Hand service extended with `apply_angles` for open (all-0) and close (all-100)
- Added arm joints panel: J1-J7 rad input with live degree readings below each
- Added `Open`/`Close` CAN hand buttons, hand pose sequential execution (seq + Run)
- Added Servo Mode, RT Follow, Drag SDK, Comfort optimization, Collision detection in `advanced_arm.py`
- Added `Tasks` tab with Slice Cycle
- **2026-04-28 20:30 — Redesigned first tab into 3-column compact layout for maximized windows**:
  - Left column: Arm Ops / State / Joints+LiveReadback / World Jog / Arm Presets
  - Middle column: Servo Mode / RT Follow / Drag(xCoreSDK) / Comfort
  - Right column: Hand / Hand Angles / Hand Poses
  - Top bar: side(L/R) / model(o6/l25/l20lite) / iface / arm_ip / robot_class / Refresh / Stop
  - All advanced arm features (Servo/RT/Drag/Comfort/Collision) now live in first tab — no tab switching needed
  - Removed `Advanced Arm` tab from build_pages registration to avoid duplication
  - Added `arm_ip` and `robot class` to top bar (required for Drag xCoreSDK)
  - Added `Stop Motion` button to Arm Ops section
  - 4 separate status variables (service/arm/servo/drag/comfort) all wired to `_run_async` status dispatch
  - `comfort_open_params` window redesigned with 2-column compact grid
  - `_servo_config()` helper method centralized for ServoConfig construction
- **2026-04-29 — Phase W auth decision**: user confirmed username+password+SQLite server-side storage is preferred over browser LocalStorage or config.yaml; Phase W requirements.md fully updated with new auth model (login/logout session cookie, SHA256 password, SQLite users table) and file structure (auth.py, db.py, templates/login.html, templates/settings.html, templates/index.html)
- Updated `current-session.md` Web Access section to reflect SQLite + login decision
- Updated `progress.md` with new Phase W decision entry

## Problems And Resolutions

- Legacy GUI mixes simple service calls with heavier drag/servo flows: migrated only the stable ROS service subset first
- `Arm Control` page was starting to hold too much service-call detail: moved that logic into a dedicated arm service adapter
- A pure service/status page was too limited for actual operator workflows: added world-jog without moving motion logic back into the page layer
- Old tab layout had large descriptive text blocks inside tabs wasting space: removed all description text from tabs
- Reusing hand control directly from the legacy GUI would have dragged monolithic state back into the new page: rebuilt only the minimal stable hand subset behind a new service layer
- Advanced features split across two tabs (Arm+Hand + Advanced Arm) wasted horizontal space in maximized windows: merged all Advanced Arm features back into the first tab using a 3-column block layout

## Verification

- `python3 -m py_compile` on all new files: pass
- Short GUI startup smoke test with new tabs: pass
- Package-reorganized startup smoke test: pass
- Slim-sidebar and arm-service split smoke test: pass
- Expanded arm-control startup smoke test: pass
- Unified `Arm + Hand` startup smoke test: pass
- Arm preset expanded startup smoke test: pass
- Sequence/delete startup smoke test: pass
- All 18 GUI source files compile check: pass
- 3-column compact layout compile check: pass

## Files Changed

- `/home/tbl/Project/dexbot_ros2_ws/src/gui/main.py`: GUI entry point
- `/home/tbl/Project/dexbot_ros2_ws/src/gui/app/shell.py`: main shell layout with sidebar and tabs
- `/home/tbl/Project/dexbot_ros2_ws/src/gui/pages/arm_hand.py`: complete rewrite — 3-column compact layout, all advanced arm features merged in
- `/home/tbl/Project/dexbot_ros2_ws/src/gui/pages/__init__.py`: removed AdvancedArmPage from build_pages
- `/home/tbl/Project/dexbot_ros2_ws/src/gui/pages/advanced_arm.py`: exists but not registered (reference)
- `/home/tbl/Project/dexbot_ros2_ws/src/gui/pages/tasks.py`: Slice Cycle tab
- `/home/tbl/Project/dexbot_ros2_ws/src/gui/services/registry.py`: shared registry for workspace paths and ROS bridge reuse
- `/home/tbl/Project/dexbot_ros2_ws/src/gui/services/arm/control.py`: arm-specific ROS control + ServoConfig/ComfortParams/_parse_seq
- `/home/tbl/Project/dexbot_ros2_ws/src/gui/services/hand/control.py`: hand control adapter
- `/home/tbl/Project/dexbot_ros2_ws/src/gui/config/modes.py`: shared mode definitions
- `/home/tbl/Project/dexbot_ros2_ws/src/gui/.project-log/`: progress.md, current-session.md updated

## Current State

- First tab redesigned into a 3-column compact block layout optimized for maximized windows
- All arm advanced features (Servo/RT Follow/Drag/Comfort/Collision) now live in the first tab — no tab switching required for day-to-day operator workflows
- Layout: Left (arm basics + presets) / Middle (advanced arm motion) / Right (hand + poses)
- `Tasks` tab still has Slice Cycle for heavy workflow use
- Architecture: shell + pages + services layered; logic offloaded to services; page only handles UI state and event wiring
- `advanced_arm.py` exists as reference but is not registered in build_pages

## Next Steps

- Phase W4 deferred — requires real robot hardware and deployed server for full two-browser verification

## Blank Area Inventory (for future features)

The current 3-column layout has natural gaps that can be filled without restructuring:

## Web Access Feature (Phase W)

### What
Serve the GUI as a browser-accessible web application. Users connect from any device (Ubuntu / Windows / iPad / mobile) over LAN. No client install. Each user self-registers with username + password, settings stored server-side in SQLite.

### Architecture
- `server.py` accepts WebSocket + REST connections; each WebSocket spawns a `worker.py` subprocess per user
- `auth.py` — login/logout, httpOnly session cookie, SHA256 password hash
- `db.py` — SQLite user DB (`users` table: username, password_hash, arm_ip_left, arm_ip_right, default_side)
- `templates/login.html` — username + password form, link to register
- `templates/register.html` — username + password + confirm password form
- `templates/settings.html` — view/edit arm IPs and side
- `templates/index.html` — main 3-column GUI (mirrors Tkinter layout)
- Process-per-user isolation: one crash doesn't affect others; no shared state; no Redis

### Self-Registration Flow
1. `/register.html` → user picks username + password
2. POST /api/register → insert into SQLite → redirect to login
3. User logs in → if arm IPs not set, redirect to settings page
4. User fills arm IPs → POST /api/me → saved to SQLite
5. User enters main GUI

### Deployment (20 users, single uvicorn worker)
```bash
# Install dependencies
pip install fastapi uvicorn aiofiles

# systemd service (recommended for production)
sudo cp dexbot-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dexbot-web
sudo systemctl start dexbot-web

# nginx reverse proxy
sudo apt install nginx
sudo cp nginx.conf /etc/nginx/sites-available/dexbot-web
sudo ln -s /etc/nginx/sites-available/dexbot-web /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Client Impact
**Zero.** Clients need only a browser. Nothing to install.

### Status
- Not started. Requirements updated: self-registration page added; 20-user single-worker confirmed.

## Tab Architecture (Current)

1. ✅ `Arm + Hand` (3-column maximized layout): Arm Ops / State / Joints / World Jog / Arm Presets / Servo Mode / RT Follow / Drag / Comfort / Hand / Hand Angles / Hand Poses
2. ✅ `Tasks`: Slice Cycle
3. `Migration Plan`: migration roadmap
4. `Legacy Boundary`: why the legacy GUI is not embedded
