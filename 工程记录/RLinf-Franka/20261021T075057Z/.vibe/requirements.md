# Release Repository Requirements

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
