# Category: workflow

## ROS2 workspace environment isolation is not automatic

- Path: `workflow/ros2-workspace-environment-isolation.md`
- Rule: When a ROS2 workspace is cloned, moved, or duplicated, always rebuild in a clean shell. Never trust that `install/setup.bash` from a prior build is self-contained — it snapshots the underlay chain of its build environment.
- Tags: ros2, workspace, environment, colcon, build
- Triggers: workspace copied, workspace moved, install/setup.bash contains old paths, build environment contamination, underlay chain leaked
- Updated: 2026-06-09

## Keep launches single-purpose and compose full workflows centrally

- Path: `workflow/single-purpose-launches-and-central-orchestration.md`
- Rule: Keep subsystem launch files single-purpose, and assemble the full workflow in one explicit orchestration entry point.
- Tags: workflow, launch, orchestration, ros
- Triggers: nested launch side effects, launch file implicitly starts other subsystems, bringup boundary unclear, full workflow assembly belongs in orchestrator
- Updated: 2026-06-09
