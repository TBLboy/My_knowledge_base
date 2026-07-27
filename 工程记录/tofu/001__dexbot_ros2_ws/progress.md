# Progress

## 2026-05-26

### Completed
- [x] Implemented `ServiceRegistry.get_ros_bridge(side)` dual bridge support
- [x] Implemented `ArmControlService.__init__(services, side)` with `_bridge()` helper
- [x] Created `pages/dual_arm.py` with `ArmSidePanel` and `DualArmPage`
- [x] Registered `DualArmPage` in page registry (`pages/__init__.py`)
- [x] Updated project-log documentation

### Dual-Arm Tab Features
- [x] Left/right side panels with independent state display
- [x] Per-side joint control (Apply Joints / Fill From Live)
- [x] Per-side arm presets (Record, Move-To, Run seq, Delete, Save/Load JSON)
- [x] Per-side drag mode via xCoreSDK
- [x] Per-side hand control (Connect, Disconnect, Open, Close, Apply, Read)
- [x] Per-side hand angle sliders with nudge buttons
- [x] Per-side hand poses (Save, Load, Load+Apply, Delete)
- [x] Shared hand model selector across both panels

### Layout Optimizations
- [x] Removed State LabelFrame (redundant with Joints live readback)
- [x] Added joint angle display to DualArmPage top bar (per-side summary)
- [x] Merged Drag ON/OFF buttons into Joints button row (removed standalone drag row)
- [x] Compacted Hand LabelFrame layout (removed status/warning labels, reduced padding)
- [x] Removed Hand seq + Run row from Hand Poses
- [x] Shifted row indices after drag/state removal
- [x] Reduced all LabelFrame `pady` and internal paddings
