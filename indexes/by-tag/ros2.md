# Tag: ros2

## Python tools embedding rclpy need full ROS2 runtime, not just sys.path

- Path: `debugging/rclpy-tools-need-full-ros2-runtime.md`
- Rule: Python scripts that call `rclpy.create_node()`, `create_client()`, or `create_subscription()` need the full ROS2 runtime environment — not just Python import paths. The typesupport shared libraries are loaded dynamically by the middleware and depend on `AMENT_PREFIX_PATH` + `LD_LIBRARY_PATH`.
- Tags: ros2, rclpy, python, environment, debugging
- Triggers: rclpy.create_client fails, rclpy.create_node fails, typesupport library not found, load library failed rosidl_typesupport, python3 main.py ros2, Could not load library
- Updated: 2026-06-09

## ROS2 workspace environment isolation is not automatic

- Path: `workflow/ros2-workspace-environment-isolation.md`
- Rule: When a ROS2 workspace is cloned, moved, or duplicated, always rebuild in a clean shell. Never trust that `install/setup.bash` from a prior build is self-contained — it snapshots the underlay chain of its build environment.
- Tags: ros2, workspace, environment, colcon, build
- Triggers: workspace copied, workspace moved, install/setup.bash contains old paths, build environment contamination, underlay chain leaked
- Updated: 2026-06-09
