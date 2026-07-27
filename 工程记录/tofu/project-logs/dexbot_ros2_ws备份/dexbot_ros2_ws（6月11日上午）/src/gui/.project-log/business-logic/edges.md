# Business Logic Edges

## Edge Template

```yaml
edge_id: <edge-id>
from: <start-node-id>
to: <target-node-id>
path: main | branch | archived
status: draft | stable | testing | validated | archived
method: <method summary>
execution_chain:
  - <step 1>
  - <step 2>
  - <step 3>
inputs:
  - <input>
outputs:
  - <output>
parameters:
  - name: <parameter-name>
    type: <data-type>
    default: <default-value>
    source: <config/code/user/hardware>
interfaces:
  - <topic/service/API/SDK/protocol>
error_handling:
  - <failure condition and response>
verification:
  - <verification method>
notes:
  - <notes>
```

## Edges

### A->B: Build Arm+Hand Page

```yaml
edge_id: A->B
from: A
to: B
path: main
status: stable
method: Build ArmHandPage with 3-column layout, initialize services, start joint polling
execution_chain:
  - Create ArmHandPage frame
  - Build top bar (side/model/iface/arm_ip/class/Refresh/Stop)
  - Build left column (Arm Ops, State, Joints, World Jog, Arm Presets)
  - Build middle column (Servo Mode, RT Follow, Drag, Comfort)
  - Build right column (Hand, Hand Angles, Hand Poses)
  - Create ArmControlService and HandControlService
  - Rebuild hand sliders based on model DOF
  - Refresh pose list and arm preset list
  - Start joint polling thread (500ms interval)
inputs:
  - ServiceRegistry
  - AppMode
outputs:
  - Fully built ArmHandPage with all controls
parameters:
  - name: side
    type: str
    default: "right"
    source: code
  - name: hand_model
    type: str
    default: "o6"
    source: code
  - name: can_iface
    type: str
    default: "can0"
    source: code
interfaces:
  - services.arm.control.ArmControlService
  - services.hand.control.HandControlService
  - services.registry.ServiceRegistry
error_handling:
  - ServiceRegistry init failure: RuntimeError if workspace root not found
verification:
  - python3 -m py_compile passes
  - GUI renders without errors
notes:
  - Safe buttons (E-Stop, Stop Motion) are never disabled during operations
```

### B->C: Execute Operation

```yaml
edge_id: B->C
from: B
to: C
path: main
status: stable
method: User triggers operation via button click, _run_async dispatches to service layer
execution_chain:
  - User clicks button or changes input
  - _run_async checks _busy flag
  - If busy, return early with "busy" status
  - Set _busy=True, disable all non-safe buttons
  - Start background thread with worker function
  - Worker calls ArmControlService or HandControlService method
  - Service calls ROS service or SDK method
  - Result or exception returned
  - on_success or _finish_error called on main thread
  - Re-enable all buttons, update status
inputs:
  - Button click event
  - Operation parameters from UI variables
outputs:
  - Operation result (success/error)
parameters:
  - name: status_target
    type: str
    default: "service"
    source: code
    valid_range: "service|hand|servo|drag|comfort"
interfaces:
  - ArmControlService.set_enabled
  - ArmControlService.set_estop
  - ArmControlService.clear_errors
  - ArmControlService.stop_motion
  - ArmControlService.set_collision_detection
  - ArmControlService.goto_joint_positions
  - ArmControlService.world_jog
  - ArmControlService.servo_move_segment
  - ArmControlService.rt_follow_start
  - ArmControlService.optimize_joint_comfort
  - HandControlService.connect
  - HandControlService.disconnect
  - HandControlService.apply_angles
  - HandControlService.readback_angles
  - HandControlService.save_pose
  - HandControlService.load_pose
  - HandControlService.delete_pose
  - xCore SDK (drag operations)
error_handling:
  - Service not reachable: RuntimeError with message
  - Service call failed: RuntimeError with service message
  - Exception in worker: _finish_error logs and updates status
  - Safe buttons (E-Stop, Stop Motion) remain enabled during busy state
verification:
  - Status label updates correctly
  - Buttons re-enable after operation
  - Log shows entry/success/failure for each method
notes:
  - _run_async is the central dispatch for all async operations
  - Safe buttons are tracked separately in _safe_buttons list
```

### C->D: Update State

```yaml
edge_id: C->D
from: C
to: D
path: main
status: stable
method: on_success callback updates UI state variables, joint polling continues independently
execution_chain:
  - on_success receives operation result
  - Update relevant status variable (arm_status, hand_status, etc.)
  - If operation was refresh_state, update joints and pose display
  - If operation was record/load/delete, refresh corresponding list
  - Joint polling thread continues at 500ms interval
  - Joint readback labels update with latest /joint_states data
inputs:
  - Operation result
  - Latest joint data from /joint_states
outputs:
  - Updated UI state
parameters:
  - name: poll_interval_ms
    type: int
    default: 500
    source: code
interfaces:
  - /joint_states (via RosServiceBridge.get_latest_joint_deg)
error_handling:
  - Joint polling failure: labels show "-"
  - No fresh data: labels show "-"
verification:
  - Joint readback shows live values when ROS is running
  - Status labels reflect operation outcome
notes:
  - Joint polling is independent of operation execution
```

### D->E: Close Session

```yaml
edge_id: D->E
from: D
to: E
path: main
status: stable
method: WM_DELETE_WINDOW handler calls services.shutdown(), destroys root window
execution_chain:
  - User closes window (WM_DELETE_WINDOW)
  - _on_close called
  - Log "GUI closing"
  - ServiceRegistry.shutdown() called
  - RosServiceBridge.shutdown() releases resources
  - HandControlService.shutdown() disconnects hand if connected
  - root.destroy() called
inputs:
  - WM_DELETE_WINDOW event
outputs:
  - Clean shutdown
interfaces:
  - ServiceRegistry.shutdown
  - RosServiceBridge.shutdown
  - HandControlService.shutdown
error_handling:
  - Shutdown exception: caught and logged, window still destroyed
verification:
  - Log shows "GUI closing" message
  - No orphaned ROS nodes
notes:
  - Hand disconnect is called automatically on shutdown
```

### W0->W1: Login/Register

```yaml
edge_id: W0->W1
from: W0
to: W1
path: main
status: stable
method: User authenticates via username + password, session token created
execution_chain:
  - User enters username + password on login page
  - POST /api/login with {username, password}
  - Server verifies password hash in SQLite
  - If valid: create session token, set httpOnly cookie, redirect with ?token=
  - If invalid: return 401 error
  - Or: user clicks "Register here", fills form, POST /api/register
  - Server creates user in SQLite with SHA256 password hash
  - Redirect to login page
inputs:
  - POST /api/login {username, password}
  - or POST /api/register {username, password, confirm_password}
outputs:
  - Session token (cookie + URL param)
  - Redirect to /settings or /index
parameters:
  - name: COOKIE_MAX_AGE
    type: int
    default: 604800
    source: code
    valid_range: "> 0"
interfaces:
  - POST /api/login
  - POST /api/register
  - SQLite users/sessions tables
error_handling:
  - Missing fields: 400 error
  - Username too short/long: 400 error
  - Password mismatch: 400 error
  - Username exists: 409 error
  - Invalid credentials: 401 error
verification:
  - Cookie present in browser
  - Redirect to correct page
notes:
  - Token passed via URL query param because httpOnly cookies not available in WebSocket handshake
```

### W1->W2: Settings Required

```yaml
edge_id: W1->W2
from: W1
to: W2
path: main
status: stable
method: First-time user redirected to settings page if arm IPs not set
execution_chain:
  - Login handler checks if user has arm_ip_left or arm_ip_right
  - If both empty: redirect to /settings?token=...
  - User fills arm IPs, model, iface, arm_class
  - POST /api/me with settings
  - Server updates SQLite users table
  - Redirect to /index?token=...
inputs:
  - GET /settings
  - POST /api/me {arm_ip_left, arm_ip_right, default_side, model, iface, arm_class}
outputs:
  - Updated user settings in SQLite
  - Redirect to /index
interfaces:
  - GET /settings
  - POST /api/me
  - SQLite users table
error_handling:
  - Auth failed: redirect to /login
  - Update failed: 400 error
verification:
  - Settings saved successfully
  - Redirect to /index
notes:
  - Returning users with IPs set skip this step and go directly to /index
```

### W2->B: WebSocket Connection

```yaml
edge_id: W2->B
from: W2
to: B
path: main
status: stable
method: Browser opens WebSocket connection, server spawns worker subprocess
execution_chain:
  - Browser loads /index with session token in URL
  - JS reads token from URL, stores in sessionStorage
  - JS opens WebSocket: ws://host/ws?token=<token>
  - Server validates token against SQLite sessions table
  - Server loads user settings (arm IPs, side, model, iface, arm_class)
  - If arm_ip empty: close with code 4002
  - Server spawns worker.py subprocess with DEXBOT_ARM_SIDE env var
  - WebSocketBridge connects browser ↔ worker via stdin/stdout
  - JS applies user settings to UI (side, arm_ip, model, iface, arm_class)
  - Page ready for operations (equivalent to node B)
inputs:
  - WebSocket connection with token
  - User settings from SQLite
outputs:
  - Worker subprocess running
  - WebSocket bridge established
  - UI populated with user settings
parameters:
  - name: DEXBOT_ARM_SIDE
    type: str
    default: "right"
    source: user settings
interfaces:
  - WebSocket /ws?token=...
  - subprocess.Popen (worker.py)
  - stdin/stdout JSON relay
error_handling:
  - Invalid token: close code 4001
  - User not found: close code 4001
  - arm_ip not set: close code 4002
  - Worker spawn failure: server logs error
verification:
  - WebSocket connected
  - Worker process running
  - UI shows correct arm IPs and settings
notes:
  - Each WebSocket connection gets its own isolated worker subprocess
  - Worker crash does not affect other users
```

### D->W3: Logout/Disconnect

```yaml
edge_id: D->W3
from: D
to: W3
path: main
status: stable
method: User logs out or disconnects, worker subprocess terminated
execution_chain:
  - User clicks Logout button
  - POST /api/logout
  - Server deletes session token from SQLite
  - Server removes httpOnly cookie
  - Redirect to /login
  - Or: browser closes/navigates away → WebSocket disconnects
  - Server catches WebSocketDisconnect exception
  - Server sends SIGTERM to worker subprocess
  - Worker exits (or SIGKILL after 3s timeout)
  - Server logs worker exit code
inputs:
  - POST /api/logout
  - or WebSocket disconnect event
outputs:
  - Session deleted
  - Worker subprocess terminated
  - Redirect to /login
interfaces:
  - POST /api/logout
  - WebSocket close
  - subprocess.terminate/kill
error_handling:
  - Worker does not exit after SIGTERM: SIGKILL sent
  - No token found: still redirect to /login
verification:
  - Cookie removed
  - Worker process exited
  - Session deleted from SQLite
notes:
  - Worker cleanup is critical to prevent orphaned processes
```
