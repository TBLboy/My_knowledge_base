# Trigger: rclpy-create-node-fails

## Python tools embedding rclpy need full ROS2 runtime, not just sys.path

- Path: `debugging/rclpy-tools-need-full-ros2-runtime.md`
- Rule: Python scripts that call `rclpy.create_node()`, `create_client()`, or `create_subscription()` need the full ROS2 runtime environment — not just Python import paths. The typesupport shared libraries are loaded dynamically by the middleware and depend on `AMENT_PREFIX_PATH` + `LD_LIBRARY_PATH`.
- Tags: ros2, rclpy, python, environment, debugging
- Triggers: rclpy.create_client fails, rclpy.create_node fails, typesupport library not found, load library failed rosidl_typesupport, python3 main.py ros2, Could not load library
- Updated: 2026-06-09
