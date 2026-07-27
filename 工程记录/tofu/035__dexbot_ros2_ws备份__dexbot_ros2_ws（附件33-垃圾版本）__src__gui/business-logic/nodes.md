# Business Logic Nodes

## Node Template

```yaml
id: <node-id>
name: <node-name>
status: draft | stable | deprecated
state:
  - <what has become true at this node>
inputs:
  - <required input data or signal>
outputs:
  - <available output data or signal>
data_format:
  - <data type, message type, file type, coordinate frame, etc.>
related_hardware:
  - <hardware if any>
related_interfaces:
  - <ROS topic/service/action, API, SDK, protocol, etc.>
verification:
  - <how to confirm this state is reached>
notes:
  - <notes>
```

## Nodes

### A: GUI Shell Ready

```yaml
id: A
name: GUI Shell Ready
status: stable
state:
  - Tkinter root window created
  - DexbotGuiShell initialized
  - ServiceRegistry created with workspace root resolved
  - Mode selected (XCORE or LBOT)
  - Notebook tabs built from build_pages()
inputs:
  - Workspace path (auto-detected from __file__)
  - Mode selection (XCORE/LBOT)
outputs:
  - Shell window with sidebar and notebook
data_format:
  - AppMode key (string)
related_hardware:
  - None
related_interfaces:
  - dexbot_toolbox.gui.arm_hand_gui.RosServiceBridge (lazy init)
verification:
  - python3 -m py_compile passes
  - GUI window opens with correct tabs
notes:
  - Mode determines which pages are available
```

### B: Arm+Hand Page Ready

```yaml
id: B
name: Arm+Hand Page Ready
status: stable
state:
  - ArmHandPage instantiated
  - ArmControlService created
  - HandControlService created
  - UI built (3-column layout: left/middle/right)
  - Top bar: side(L/R), model, iface, arm_ip, class
  - Joint polling thread started (500ms interval)
  - Pose list and arm preset list loaded
inputs:
  - Side selection (left/right)
  - Hand model (o6/l25/l20lite)
  - CAN interface (can0)
  - Robot IP (192.168.2.161/160)
outputs:
  - All UI controls ready
  - Status variables initialized
data_format:
  - HandModel: Literal["o6", "l25", "l20lite"]
  - Side: "left" | "right"
related_hardware:
  - xMate arm (xCore SDK)
  - CAN hand (linkerbot O6/L25/L20lite)
related_interfaces:
  - /robot/get_state
  - /robot/enable_arm
  - /robot/emergency_stop
  - /robot/clear_errors
  - /robot/move_rt_cartesian_segment
  - /robot/move_joints
  - /joint_states
  - linkerbot.hand (O6/L25/L20lite)
verification:
  - Page renders with all sections
  - Joint readback shows "-" or live values
notes:
  - 3-column layout: Arm Ops+Joints+Jog+Presets | Servo+RT+Drag+Comfort | Hand+Angles+Poses
```

### C: Operations Executed

```yaml
id: C
name: Operations Executed
status: stable
state:
  - User action completed (arm/hand operation)
  - Service layer method executed
  - Result or error returned
inputs:
  - User button click or input change
  - Operation parameters (joints, pose, config)
outputs:
  - Operation result (success message or error)
  - Robot state changed
data_format:
  - Result: str | dict | list[float]
related_hardware:
  - xMate arm
  - CAN hand
related_interfaces:
  - All ROS services under /robot/*
  - xCore SDK (drag, record)
  - linkerbot CAN hand SDK
verification:
  - Status label updated
  - Robot responds to command
notes:
  - Operations run in background thread via _run_async
  - Safe buttons (E-Stop, Stop Motion, top-bar Stop) are NEVER disabled during busy state (fixed 2026-05-18)
  - _busy flag prevents concurrent non-safe operations
```

### D: State Updated

```yaml
id: D
name: State Updated
status: stable
state:
  - UI status variables updated
  - Joint readback refreshed
  - Pose/arm preset lists refreshed if needed
inputs:
  - Operation result
  - Latest joint/pose data from /joint_states
outputs:
  - Visual feedback to user
data_format:
  - Joint degrees: list[float] (7 joints)
  - Cartesian pose: list[float] (6 elements: x,y,z,rx,ry,rz)
related_hardware:
  - None
related_interfaces:
  - /joint_states
verification:
  - Status labels show correct values
  - Joint readback updates at 500ms interval
notes:
  - Joint polling runs continuously via after(500, _poll_joints)
```

### E: Session Closed

```yaml
id: E
name: Session Closed
status: stable
state:
  - GUI window closed
  - ServiceRegistry.shutdown() called
  - RosServiceBridge resources released
  - Log file written with shutdown event
inputs:
  - WM_DELETE_WINDOW event
outputs:
  - Clean shutdown
data_format:
  - None
related_hardware:
  - None
related_interfaces:
  - RosServiceBridge.shutdown()
verification:
  - No orphaned ROS nodes
  - Log shows "GUI closing" message
notes:
  - Hand disconnect called on shutdown if connected
```

### W0: Browser Opens

```yaml
id: W0
name: Browser Opens
status: stable
state:
  - Browser loads login page from server
  - No session cookie present
inputs:
  - HTTP GET /login
outputs:
  - Login HTML page rendered
data_format:
  - HTML + CSS + JS
related_hardware:
  - None
related_interfaces:
  - HTTP GET /login
verification:
  - Login page renders with username/password fields
notes:
  - If user has valid session cookie, redirects to /index
```

### W1: Login/Register

```yaml
id: W1
name: Login/Register
status: stable
state:
  - User authenticated via username + password
  - Session token created in SQLite
  - httpOnly cookie set (7-day expiry)
  - Token passed via URL query param for WebSocket auth
inputs:
  - POST /api/login {username, password}
  - or POST /api/register {username, password, confirm_password}
outputs:
  - Session token (cookie + URL param)
  - Redirect to /settings (if IPs not set) or /index
data_format:
  - Session token: random hex string
  - Password hash: SHA256
related_hardware:
  - None
related_interfaces:
  - POST /api/login
  - POST /api/register
  - SQLite users/sessions tables
verification:
  - Cookie present in browser
  - Redirect to correct page
notes:
  - First-time users redirected to /settings to fill arm IPs
```

### W2: Settings: Arm IPs

```yaml
id: W2
name: Settings: Arm IPs
status: stable
state:
  - User arm IPs saved to SQLite
  - User model/iface/arm_class saved
  - Session token available for WebSocket
inputs:
  - POST /api/me {arm_ip_left, arm_ip_right, default_side, model, iface, arm_class}
outputs:
  - Updated user settings in SQLite
  - Redirect to /index with token
data_format:
  - arm_ip_left/right: IPv4 string
  - default_side: "left" | "right"
  - model: "o6" | "l25" | "l20lite"
  - iface: CAN interface name
  - arm_class: robot class name
related_hardware:
  - None
related_interfaces:
  - POST /api/me
  - SQLite users table
verification:
  - Settings saved successfully
  - Redirect to /index with token
notes:
  - Users can update IPs later by logging out and signing in again
```

### W3: Logout/Disconnect

```yaml
id: W3
name: Logout/Disconnect
status: stable
state:
  - Session token deleted from SQLite
  - httpOnly cookie removed
  - Worker subprocess terminated
  - WebSocket connection closed
inputs:
  - POST /api/logout
  - or WebSocket disconnect
outputs:
  - Redirect to /login
  - Worker process cleaned up
data_format:
  - None
related_hardware:
  - None
related_interfaces:
  - POST /api/logout
  - WebSocket close
verification:
  - Cookie removed
  - Worker process exited
notes:
  - Worker subprocess receives SIGTERM, then SIGKILL if not exited within 3s
```
