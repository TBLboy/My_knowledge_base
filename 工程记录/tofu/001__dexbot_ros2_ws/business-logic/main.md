# Business Logic

## GUI Pages

### Dual-Arm Collaboration Tab (implemented 2026-05-26)

A new "Dual Arm" tab has been added to the GUI notebook that provides side-by-side control of both robot arms simultaneously.

**Architecture:**
- `ArmSidePanel` — reusable `ttk.LabelFrame` component controlling one arm + one hand, parameterized by side, arm IP, and CAN interface
- `DualArmPage` — top-level `ttk.Frame` with 2-column grid layout hosting left and right `ArmSidePanel` instances

**Left side:** arm_l (192.168.2.160, can1)
**Right side:** arm_r (192.168.2.161, can0)

**Features per panel:**
- State display (joint angles + cartesian pose, 500ms polling)
- Joint J1-J7 input + Apply / Fill From Live
- Arm Presets (Record, Move-To, Run seq, Delete, Save/Load JSON)
- Drag Mode (xCoreSDK): Drag ON/OFF, Rec Start/Stop, Save, Cancel
- Hand: Connect, Disconnect, Open, Close, Apply, Read with torque/timeout/settle/nudge config
- Hand Angles: dynamic sliders per hand model DOF with ± nudge buttons
- Hand Poses: Save (with note), Refresh, Load, Load+Apply, Delete, seq+Run

**Service layer changes:**
- `ServiceRegistry.get_ros_bridge(side)` now supports dual ROS bridge instances (keyed by "l" / "r")
- `ArmControlService.__init__(services, side)` supports per-side ROS bridge selection via `_bridge()` helper
