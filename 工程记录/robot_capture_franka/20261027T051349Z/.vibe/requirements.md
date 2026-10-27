# Release Repository Requirements

## Approved dual-arm workbench rules — 2026-10-23

Status: approved business baseline, frozen at operator request. These rules concern the current Robot Capture workbench extension, not the historical single-arm Release scope below. Implementation has not started. Remaining deployment input is the physical left/right wrist-camera and gripper mapping, not a separate manual reset-pose identification exercise.

- One Pico controls two Frankas concurrently: left controller/left arm `172.16.0.2`, right controller/right arm `172.16.0.3`. Reuse the working single-arm motion logic; do not retune control gains or bypass safety limits.
- Rig has three camera roles (external/global, left wrist, right wrist) and two grippers. Extend existing capture/playback/export/upload only as necessary for dual-arm data; do not introduce a custom per-frame invalidity-mask framework.
- Fault isolation: pause the affected side only; healthy side can remain operable. A side fault ends the entire current recording and retains error information for quality review; no automatic reset.
- The physical menu button is on the LEFT controller (the previous right-menu assignment is incorrect for this rig). Preserve existing long-release enable / short-release pause semantics. RIGHT joystick click calibrates the selected controller-to-arm mappings. In dual-arm mode these are paired actions; in single-arm mode only the selected arm is affected. Each arm's grip/trigger controls its own motion/gripper, and releasing one grip does not pause the other side.
- Both explicit/manual reset and existing automatic reset after normal trajectory completion act on the selected arms, using each arm's own saved target. Dual-arm reset is a paired operation; hardware scheduling does not promise exact simultaneous physical arrival. Fault handling must not initiate reset. Existing recording start/save/discard/reset key conventions otherwise remain unchanged and apply to the whole selected-mode trajectory.
- Saving reset poses is one operator action: read current poses of all selected arms and persist each as its own target only when all reads succeed; a failed read or save must not partially replace the previous targets. Arms are identified by their configured IP/side automatically. No extra per-arm manual pose mapping is required. This operation is distinct from joystick mapping calibration; retain existing operator confirmation and safety guards.
- Dual-arm enable is all-or-nothing: if either side is not ready, neither arm enters teleoperation. This initial gate is distinct from fault isolation after successful enable.
- Operator can select left-only, right-only, or dual-arm teleoperation. Left-only reuses the proven right-arm control logic with side-specific Pico inputs (including grip/trigger); shared behavior remains unchanged. Mode changes are allowed only after teleoperation exit and recording completion, not live during control or recording. Selected-mode devices must all be ready before enabling; inactive-side hardware is not a prerequisite.
- All shared actions are scoped to the selected arms: left-menu enable/pause, right-joystick calibration, manual/automatic reset, and saving current reset poses affect only the selected arm in single-arm modes and both arms in dual-arm mode. User requests that straightforward consequences of already-selected mode semantics be inferred rather than repeatedly reconfirmed.
- Updated camera/data rule (supersedes earlier always-three-camera proposal): selected teleoperation mode determines the active capture set. Left-only starts/records global and left-wrist cameras plus left robot/gripper state and issued actions; right-only starts/records global and right-wrist cameras plus right robot/gripper state and issued actions; dual-arm starts/records all three cameras and both robots/grippers. Inactive-side hardware/data is ignored, not fabricated.
- Capture UI keeps a fixed spatial order: left wrist, external/global, right wrist. Single-arm mode activates only global and the selected-side wrist view; dual mode activates all three. Inactive views remain placeholders labelled disabled. Playback follows the mode/device set stored in the recording, independent of the current selection, and preserves old single-arm recording compatibility.

### Acceptance boundary

- Left-only and right-only work without the inactive robot, wrist camera or gripper connected; only the global camera and selected-side devices are required and archived.
- Dual mode supports concurrent left/right teleoperation and records three real camera streams plus separately identifiable measured states and issued actions for both arms/grippers, through the existing session/HDF5/playback/upload pipeline.
- Shared controls affect exactly the selected arm set. Dual enable rejects incomplete readiness without leaving one side enabled. A runtime side fault pauses that side and ends the entire recording with existing error information, without automatically resetting either arm.
- One save-reset action updates the selected targets together; resets use their own targets and do not copy the old right-arm pose to the left arm.
- No invented inactive-side data, new per-frame invalidity-mask framework, unrelated capture/upload redesign, new motion algorithm, retuned gains, or weakened safety constraints. True-hardware acceptance remains operator initiated with unloaded small-range tests and accessible emergency stop.

### Confirmed deployment mapping

- Operator isolation and replug checks (2026-10-23): left wrist `/dev/v4l/by-path/pci-0000:00:14.0-usb-0:8.3:1.0-video-index0`, left gripper `/dev/serial/by-id/usb-FTDI_USB_TO_RS-485_DAANTLZD-if00-port0`; right wrist `/dev/v4l/by-path/pci-0000:00:14.0-usb-0:8.4.1:1.0-video-index0`, right gripper `/dev/serial/by-id/usb-FTDI_USB_TO_RS-485_DAASNCGD-if00-port0`. External ZED 2i `/dev/v4l/by-id/usb-Technologies__Inc._ZED_2i_OV0001-video-index0`. Right wrist and DAASNCGD appeared on operator-confirmed right-side replug; left and global paths remained unchanged. Camera by-path bindings require retaining physical port/hub topology. No devices opened or commanded in these checks.

- Left/right wrist cameras: distinguish the two same-name ZED-M devices using stable unique identifiers or confirmed USB physical paths, not ambiguous shared by-id aliases or transient video numbers.
- Left/right grippers: associate each FTDI by-id serial path with its arm by operator-confirmed physical identification. Do not infer side from ttyUSB numbering or command gripper motion to identify it.
- External/global camera: ZED 2i. Physical mapping is now confirmed; no camera/robot/gripper start is authorized merely by freezing this baseline.

### Implementation breakdown — planned, not authorized to execute

Baseline: local checkpoint `f24bcb9` (pre-dual-arm NAS deployment state). Parent Task `dual-arm-workbench-20261023` remains paused. This breakdown is planning only; do not resume implementation automatically. Create/start slice Tasks when execution is authorized, not as active placeholders.

1. **Mode/device contract and integration design.** Define left/right/dual selection, confirmed inventory, mode-to-camera/arm projection, immutable active-mode lifecycle, per-side telemetry/archive identity and legacy compatibility. Resolve one publisher/two arm readers, single dispatch of shared events, initial enable rollback, runtime fault visibility, and transactional reset target persistence in a focused design before wiring hardware owners. Verify via interface examples, state/failure matrix and unit tests when implemented. No runtime behavior change by merely adding inventory.
2. **Mode-scoped single-arm vertical path.** Wire inactive-state mode selection through camera startup, existing worker/backend, recording and playback. Left-only uses left pose/grip/trigger; shared menu and calibration still use left menu/right joystick. Three fixed camera panes, only global+selected wrist active. Handle ZED identification by sysfs for by-path aliases. Include explicit selected-side metadata and export identity while preserving old recordings/NAS settings. Verify left and right independently without inactive hardware (mocks); guards reject mid-session mode changes. Hardware test only by operator.
3. **Dual-arm control lifecycle.** Extend the verified single-arm path to two selected backends with one vendor publisher and nonduplicated shared actions. Both preflights before enable, compensate partial enable failure, independent grip/trigger, paired explicit actions/reset, all-or-nothing saved reset targets. Side faults remain visible and stop only affected-side targets; motion safety not weakened. Offline fault-injection tests for readiness, failure midway through enable, disconnect, reset/save failures, cleanup and event duplication. Dual recording stays unavailable until slice 4 is integrated.
4. **Dual recording/export vertical path.** Reuse recorder/sync/HDF5/quality pipeline for three real camera streams and separately identifiable measured/issued fields for both arms/grippers. Selected-side runtime faults end entire recording once without auto-reset; no fake/missing-side fill. Preserve mode/side identity in archived metadata and verify old single-arm export compatibility. Verify synthetic dual episode through actual recording/export/read, sample dimensions, timestamp precision, active-view sets and injected faults.
5. **Integrated playback and operator workflow.** Show left/global/right spatial order, selected-mode arm viewers and recorded-side telemetry; playback uses archived mode not current UI selection. Recording buttons/Pico controls share existing session actions, normal completion/discard retains approved automatic selected-arm reset. Verify all three modes and legacy data in browser plus reset/fault paths in mocks, no double dispatch/reset.
6. **Deployment/acceptance.** Run full offline suite; verify both distinct camera physical paths, three-camera actual HD720 cadence and CPU/USB pressure, per-arm/gripper mapping, real-time/memlock configuration and NAS behavior. Operator-led unloaded small-range left-only, right-only, dual tests, paired buttons/reset, fault handling, short trajectory playback/export/upload. Never disconnect real hardware in motion for testing; use mocks for unsafe fault scenarios. Commit accepted increments; push only on user request. Automated success alone is not hardware acceptance.

Dependencies: 1 → 2 → 3 → 4 → 5 → 6. Archive field contracts are designed in 1 and minimally implemented in 2, not postponed until UI changes. Existing capture must never silently run a half-integrated dual mode. Each slice preserves user changes and has its own bounded verification; overall completion requires all slices and explicitly scoped operator acceptance.

## Approved business scope

`Release/` is the independent, local Git repository for the stable Franka Research 3 single-arm Pico teleoperation and human-demonstration collection product. It tracks RLinf as its framework upstream and maintains this project's Franka/Pico adaptation layer. RLinf capabilities outside this workflow may be present, but they are not Release support commitments.

## Supported operator workflow

1. Install the documented, reproducible runtime environment with `uv` and the documented non-Python system/vendor dependencies.
2. Run one supported launcher that performs hardware and camera preflight, starts the Pico bridge and collection process, and performs cleanup.
3. Collect raw demonstrations through the documented Pico and keyboard controls.
4. Run the quality check on a completed collection run.
5. Convert a selected completed raw collection run with the legacy pickle-to-LeRobot converter.

The existing legacy converter is included as a supported migration component. The future LeRobot v3 multi-sensor raw schema and aligner are not part of this Release.

## Source and stability rules

- Release starts from committed source only: RLinf `e7a9a2e`, RLinf-Franks `803ba2a`, and the committed Pico software snapshot identified during the migration inventory.
- `upstream` is the RLinf framework remote; `origin` is reserved for the project Release distribution remote. A fetched upstream revision is not supported until the Release compatibility procedure succeeds.
- Current uncommitted code, experimental joint-IK work, diagnostics, one-off tools, historical research, build products, virtual environments, caches, and collected data are excluded.
- Stable automated tests that exercise released behavior are retained or added. Test-only dependencies and tests unrelated to the supported product are excluded.
- Pico software is vendored under Release management with applicable upstream notices and licenses retained.
- Release documents every external component that cannot be safely vendored, including its purpose, source, version or compatibility range, license/status if known, and installation or verification procedure.

## Release architecture

```text
Release/
├── rlinf/                  # RLinf framework subject, tracked from upstream
├── extensions/rig/         # rig-specific RLinf extension (camera and collection hooks)
├── pico_bridge/            # managed Pico-to-ZMQ bridge source and its configuration
├── configs/                # supported single-arm Pico/Franka Hydra configuration
├── scripts/                # stable operator and offline entry points
├── tests/                  # focused Release tests only
├── docs/                   # setup, operation, safety, dependency, and provenance documentation
├── licenses/               # retained upstream licenses and notices
├── pyproject.toml          # Release-owned uv environment definition
└── uv.lock                 # generated only after resolution succeeds on the supported platform
```

`scripts/run_pico_session.sh` is the supported online entry point. It invokes
the RLinf framework subject and managed Pico bridge, but no source outside `Release/`.
`scripts/check_collection_run.py` and `scripts/post_process_to_lerobot.py` are
the supported offline entry points. `core/rlinf/` is vendored intact from the
approved RLinf commit because its real-world collector depends on framework
subsystems beyond a safely maintainable hand-selected file list; Release exposes
only the single-arm Pico workflow and does not document or support unrelated
upstream entry points. Upstream changes are handled through the documented
Release compatibility process, not copied as a second framework.

## Safety and product invariants

- RLinf/Franky remains the sole controller of Franka, Pico, and cameras; auxiliary tools only start, observe, or process offline data.
- Release does not loosen Franka Desk safety constraints, collision behavior, or their thresholds to improve feel.
- Any true-hardware operation remains operator initiated and follows the project safety procedure: clear workspace, reachable emergency stop, unloaded and small-range validation after control changes, immediate stop on unexpected motion, vibration, force, Desk warning, or robot error.
- Release only contains stable, configured Cartesian Pico teleoperation. Experimental joint-IK and other alternate control routes are not release functionality.

## Acceptance criteria

- `Release/` is a clean independent Git repository and contains no nested Git worktrees from the source repositories.
- The repository has one documented layout, stable entry points, configuration, source ownership, tests, and operating documentation for the supported workflow.
- The source and dependency inventories make every included component traceable to an approved baseline or documented external requirement.
- Reproducible environment metadata and dependency instructions are present; no virtual environment or unlicensed binary is silently committed.
- Automated static and focused functional checks pass, or any hardware-only limitation is explicitly documented.
