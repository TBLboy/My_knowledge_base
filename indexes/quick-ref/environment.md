# Quick Ref: environment

## Python tools embedding rclpy need full ROS2 runtime, not just sys.path

- Rule: Python scripts that call `rclpy.create_node()`, `create_client()`, or `create_subscription()` need the full ROS2 runtime environment — not just Python import paths. The typesupport shared libraries are loaded dynamically by the middleware and depend on `AMENT_PREFIX_PATH` + `LD_LIBRARY_PATH`.
- Path: `debugging/rclpy-tools-need-full-ros2-runtime.md`
- Applicability: Any Python GUI, CLI tool, or standalone script that embeds ROS2 client libraries.

## ROS2 workspace environment isolation is not automatic

- Rule: When a ROS2 workspace is cloned, moved, or duplicated, always rebuild in a clean shell. Never trust that `install/setup.bash` from a prior build is self-contained — it snapshots the underlay chain of its build environment.
- Path: `workflow/ros2-workspace-environment-isolation.md`
- Applicability: Any ROS2 project that has been moved, copied, or shared across machines.
