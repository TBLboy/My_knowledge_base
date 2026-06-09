# Quick Ref: python

## Python tools embedding rclpy need full ROS2 runtime, not just sys.path

- Rule: Python scripts that call `rclpy.create_node()`, `create_client()`, or `create_subscription()` need the full ROS2 runtime environment — not just Python import paths. The typesupport shared libraries are loaded dynamically by the middleware and depend on `AMENT_PREFIX_PATH` + `LD_LIBRARY_PATH`.
- Path: `debugging/rclpy-tools-need-full-ros2-runtime.md`
- Applicability: Any Python GUI, CLI tool, or standalone script that embeds ROS2 client libraries.
