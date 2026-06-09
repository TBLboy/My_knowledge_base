# Quick Ref: build

## ROS2 workspace environment isolation is not automatic

- Rule: When a ROS2 workspace is cloned, moved, or duplicated, always rebuild in a clean shell. Never trust that `install/setup.bash` from a prior build is self-contained — it snapshots the underlay chain of its build environment.
- Path: `workflow/ros2-workspace-environment-isolation.md`
- Applicability: Any ROS2 project that has been moved, copied, or shared across machines.
