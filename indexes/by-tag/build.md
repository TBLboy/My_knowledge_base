# Tag: build

## ROS2 workspace environment isolation is not automatic

- Path: `workflow/ros2-workspace-environment-isolation.md`
- Rule: When a ROS2 workspace is cloned, moved, or duplicated, always rebuild in a clean shell. Never trust that `install/setup.bash` from a prior build is self-contained — it snapshots the underlay chain of its build environment.
- Tags: ros2, workspace, environment, colcon, build
- Triggers: workspace copied, workspace moved, install/setup.bash contains old paths, build environment contamination, underlay chain leaked
- Updated: 2026-06-09
