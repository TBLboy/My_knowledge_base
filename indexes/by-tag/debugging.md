# Tag: debugging

## Trace runtime consumers before tuning config

- Path: `config-behavior/trace-runtime-consumers-before-tuning.md`
- Rule: A parameter is not a real control surface until you trace where it is read, transformed, and finally consumed at runtime.
- Tags: config, runtime-behavior, debugging, orchestration
- Triggers: config not effective, yaml changed but behavior unchanged, parameter appears configurable but does nothing, trace runtime consumer before tuning
- Updated: 2026-06-09

## ROS2 action client timeout is often a goal-lifecycle mismatch, not a network issue

- Path: `debugging/action-client-timeout-lifecycle.md`
- Rule: When a ROS2 action client times out waiting for a result, first distinguish between three distinct failure modes: (1) the goal was never accepted by the server (goal response timeout), (2) the goal was accepted but never finished (result timeout), or (3) the goal finished but the result callback was not triggered. Each has a different root cause and fix.
- Tags: ros, debugging, action-client, timeout, orchestration
- Triggers: action timeout, goal not completing, wait for result hangs, action client no response
- Updated: 2026-06-09

## Action server setOperateMode fails when previous operation has not released control

- Path: `debugging/action-server-setoperatemode-failed.md`
- Rule: A `setOperateMode(automatic)` call that fails is usually not a configuration problem — it means the action server's internal state machine still holds the previous operation's control. Before retrying the mode switch, ensure the previous action goal has been explicitly cancelled or has reached a terminal state.
- Tags: ros, debugging, action-server, robotics, orchestration
- Triggers: setOperateMode automatic failed, mode switch rejected, action server busy, cannot change mode while executing, previous motion not released
- Updated: 2026-06-09

## Python tools embedding rclpy need full ROS2 runtime, not just sys.path

- Path: `debugging/rclpy-tools-need-full-ros2-runtime.md`
- Rule: Python scripts that call `rclpy.create_node()`, `create_client()`, or `create_subscription()` need the full ROS2 runtime environment — not just Python import paths. The typesupport shared libraries are loaded dynamically by the middleware and depend on `AMENT_PREFIX_PATH` + `LD_LIBRARY_PATH`.
- Tags: ros2, rclpy, python, environment, debugging
- Triggers: rclpy.create_client fails, rclpy.create_node fails, typesupport library not found, load library failed rosidl_typesupport, python3 main.py ros2, Could not load library
- Updated: 2026-06-09

## ROS2 subscriber silently receives no messages when QoS mismatches

- Path: `debugging/ros2-subscriber-no-message-qos.md`
- Rule: When a ROS2 subscriber never fires despite the topic being advertised, check QoS compatibility before debugging anything else — a BEST_EFFORT subscriber connected to a RELIABLE publisher silently receives nothing, with no warning from the middleware.
- Tags: ros, debugging, qos, communication
- Triggers: topic exists but no message, subscriber callback not firing, qos mismatch silent failure, best_effort publisher reliable subscriber, no message on topic
- Updated: 2026-06-09
