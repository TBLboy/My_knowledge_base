# Current Session

## Last Updated

- 2026-04-28 20:30 Local Time

## Current Objective

Redesign the `Arm + Hand` first tab into a compact 3-column block layout optimized for maximized windows, merging all Advanced Arm features back into the first page

## Completed This Session

- Created `.project-log/` directory structure in `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/`
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

- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/main.py`: GUI entry point
- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/app/shell.py`: main shell layout with sidebar and tabs
- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/pages/arm_hand.py`: complete rewrite — 3-column compact layout, all advanced arm features merged in
- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/pages/__init__.py`: removed AdvancedArmPage from build_pages
- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/pages/advanced_arm.py`: exists but not registered (reference)
- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/pages/tasks.py`: Slice Cycle tab
- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/services/registry.py`: shared registry for workspace paths and ROS bridge reuse
- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/services/arm/control.py`: arm-specific ROS control + ServoConfig/ComfortParams/_parse_seq
- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/services/hand/control.py`: hand control adapter
- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/config/modes.py`: shared mode definitions
- `/home/tbl/Project/cucumber/dexbot_ros2_ws_525/dexbot_ros2_ws/src/gui/.project-log/`: progress.md, current-session.md updated

## Current State

- First tab redesigned into a 3-column compact block layout optimized for maximized windows
- All arm advanced features (Servo/RT Follow/Drag/Comfort/Collision) now live in the first tab — no tab switching required for day-to-day operator workflows
- Layout: Left (arm basics + presets) / Middle (advanced arm motion) / Right (hand + poses)
- `Tasks` tab still has Slice Cycle for heavy workflow use
- Architecture: shell + pages + services layered; logic offloaded to services; page only handles UI state and event wiring
- `advanced_arm.py` exists as reference but is not registered in build_pages

## Next Steps

- Fold Slice Cycle into first tab as a compact bottom block (e.g. below middle column or as a collapsible section)
- Add right-click context menus for arm preset list and hand pose list (delete selected, duplicate, rename)
- Compact the hand angles slider layout for L25 (16 DOF) — current 2-column approach may need a 3-column sub-grid
- Add tooltip labels to major section headers describing each block's purpose
- Consider adding a slim `Arm+Hand+Tasks` combined quick-access toolbar at the very top of the first tab

## Tab Architecture (Current)

1. ✅ `Arm + Hand` (3-column maximized layout): Arm Ops / State / Joints / World Jog / Arm Presets / Servo Mode / RT Follow / Drag / Comfort / Hand / Hand Angles / Hand Poses
2. ✅ `Tasks`: Slice Cycle
3. `Migration Plan`: migration roadmap
4. `Legacy Boundary`: why the legacy GUI is not embedded
