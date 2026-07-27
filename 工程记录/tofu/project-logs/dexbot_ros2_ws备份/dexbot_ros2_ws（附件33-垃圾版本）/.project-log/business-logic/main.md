# Main Business Logic

## Status

- Current main path status: Stable（两条主线并存：GUI 操作 + 代码库重构）

## Main Path

```text
Existing GUI path（保留）:
  DexbotGuiShell -> build_pages -> ArmHandPage / DualArmPage / MigrationPlanPage / LegacyPage

New Refactoring path（新增）:
  CodeBaseCurrentState -> Phase1_Cleanup -> Phase2_ExtractShared -> Phase3_SplitMonoliths -> Phase4_AddTests
```

## GUI Path Summary（现有，保留）

### Dual-Arm Collaboration Tab (implemented 2026-05-26)

A new "Dual Arm" tab has been added to the GUI notebook that provides side-by-side control of both robot arms simultaneously.

**Architecture:**
- `ArmSidePanel` -- reusable `ttk.LabelFrame` component controlling one arm + one hand, parameterized by side, arm IP, and CAN interface
- `DualArmPage` -- top-level `ttk.Frame` with 2-column grid layout hosting left and right `ArmSidePanel` instances

**Left side:** arm_l (192.168.2.160, can1)
**Right side:** arm_r (192.168.2.161, can0)

**Features per panel:**
- State display (joint angles + cartesian pose, 500ms polling)
- Joint J1-J7 input + Apply / Fill From Live
- Arm Presets (Record, Move-To, Run seq, Delete, Save/Load JSON)
- Drag Mode (xCoreSDK): Drag ON/OFF, Rec Start/Stop, Save, Cancel
- Hand: Connect, Disconnect, Open, Close, Apply, Read with torque/timeout/settle/nudge config
- Hand Angles: dynamic sliders per hand model DOF with +/- nudge buttons
- Hand Poses: Save (with note), Refresh, Load, Load+Apply, Delete, seq+Run

**Service layer changes:**
- `ServiceRegistry.get_ros_bridge(side)` now supports dual ROS bridge instances (keyed by "l" / "r")
- `ArmControlService.__init__(services, side)` supports per-side ROS bridge selection via `_bridge()` helper

## Refactoring Path Summary（新增）

### CodeBaseCurrentState

- 540+ Python files, ~131,000 lines
- Multiple backup directories (`gui_backup/`)
- 3+ parallel cut-tofu implementations
- 6 files over 1000 lines (largest: 6268 lines)
- Sparse test coverage
- See `architecture/refactoring-plan.md` for detailed assessment

### Phase1_Cleanup

- Delete `gui_backup/`
- Archive or remove unused `CutTofo/sdk/` scripts
- Archive unused `dexbot_high_layer/` cucumber slicing code
- Consolidate config file directories
- See `business-logic/branches/` for cleanup branch plans

### Phase2_ExtractShared

- Extract `config_loader` into shared package
- Extract cutting trajectory and tofu geometry into shared library
- Unify common parts of 3 cut-tofu implementations
- Keep original files as import-forwarding wrappers until stable

### Phase3_SplitMonoliths

- Split 6000-line `xcore_follow_tcp_chain_node_movej.py`
- Split 3400-line `arm_hand_gui.py`
- Split 2500-line `hand_eye_calibration_node.py`
- Split 1900-line `xcore_controller_node.py`

### Phase4_AddTests

- Add smoke tests for core cuttofo_xcore nodes
- Add unit tests for geometry / trajectory libraries
- Add smoke tests for xcore_arm_adapter

## Implementation Priority

- Current target node: CodeBaseCurrentState
- Current target edge: Phase1_Cleanup (initialization complete, ready to start cleanup)

## Stable Assumptions

- `cuttofo_xcore` is the main cut-tofu implementation
- `src/gui/` is the active GUI (gui_backup/ is not)
- ROS 2 Humble, ament_python builds
- All hardware/SDK/calibration config remains unchanged

## Verification Status

- Not verified yet (CodeBaseCurrentState - no changes made yet)

## Notes

- Refactoring must not change system behavior (pure refactoring)
- Existing GUI business logic records are preserved as-is above
