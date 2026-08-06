# Business Logic Constraints

## System Constraints

- Python 3.10+ required
- ROS2 environment must be sourced before GUI start
- Workspace root auto-detected by searching upward for `src/dexbot_toolbox`

## Hardware Constraints

- xMate arm: xCore SDK, 7-DOF, IP-based connection (192.168.2.160/161)
- CAN hand: linkerbot SDK, supports O6 (6 DOF), L25 (16 DOF), L20lite (10 DOF)
- CAN interface: `can0` (configurable), bitrate 1000000

## Software Constraints

- Tkinter for local GUI, no external GUI framework
- FastAPI + vanilla JS for web GUI, no frontend framework
- Service layer shared between Tkinter and Web — zero duplication of robot control logic
- `dexbot_toolbox.gui.arm_hand_gui.RosServiceBridge` is the ROS bridge (lazy loaded)

## Real-Time / Threading Constraints

- Joint polling runs at 500ms interval in a background thread, with UI updates via `after(0, ...)`
- All arm/hand operations run in background threads via `_run_async`
- `_busy` flag prevents concurrent operations (except safe buttons)
- RT Follow and Servo Mode use ROS real-time services (`/robot/start_rt_follow`, `/robot/move_rt_cartesian_segment`)

## Safety Constraints

- E-Stop and Stop Motion buttons must NEVER be disabled during busy state
- Disable does NOT prevent motion at backend level (backend auto-repowers via `_ensure_power_ready()`)
- Collision detection toggle available in Arm Ops

## SDK / API Constraints

- xCore SDK: `setPowerState(False)` disables arm, but motion methods call `setPowerState(True)` internally
- linkerbot hand SDK: requires CAN interface up before connect
- ROS services: all under `/robot/*` namespace, prefixed with `arm_r` or `arm_l`

## Configuration Constraints

- Default IPs: right arm 192.168.2.161, left arm 192.168.2.160
- Default CAN interface: can0
- Default hand model: o6
- Default side: right
- Web session: 7-day httpOnly cookie
