# Quick Ref: debugging

## Trace runtime consumers before tuning config

- Rule: A parameter is not a real control surface until you trace where it is read, transformed, and finally consumed at runtime.
- Path: `config-behavior/trace-runtime-consumers-before-tuning.md`
- Applicability: Multi-layer systems with YAML config, runtime overrides, and orchestration-mediated parameter application.

## ROS2 action client timeout is often a goal-lifecycle mismatch, not a network issue

- Rule: When a ROS2 action client times out waiting for a result, first distinguish between three distinct failure modes: (1) the goal was never accepted by the server (goal response timeout), (2) the goal was accepted but never finished (result timeout), or (3) the goal finished but the result callback was not triggered. Each has a different root cause and fix.
- Path: `debugging/action-client-timeout-lifecycle.md`
- Applicability: ROS2 systems where orchestrators or skill nodes use action clients to invoke hardware actions and encounter timeout errors.

## Action server setOperateMode fails when previous operation has not released control

- Rule: A `setOperateMode(automatic)` call that fails is usually not a configuration problem — it means the action server's internal state machine still holds the previous operation's control. Before retrying the mode switch, ensure the previous action goal has been explicitly cancelled or has reached a terminal state.
- Path: `debugging/action-server-setoperatemode-failed.md`
- Applicability: ROS2 action servers (especially hardware-control actions) that reject mode switches because a prior goal handle is still active or the internal state machine is in a transitional state.

## Python tools embedding rclpy need full ROS2 runtime, not just sys.path

- Rule: Python scripts that call `rclpy.create_node()`, `create_client()`, or `create_subscription()` need the full ROS2 runtime environment — not just Python import paths. The typesupport shared libraries are loaded dynamically by the middleware and depend on `AMENT_PREFIX_PATH` + `LD_LIBRARY_PATH`.
- Path: `debugging/rclpy-tools-need-full-ros2-runtime.md`
- Applicability: Any Python GUI, CLI tool, or standalone script that embeds ROS2 client libraries.

## ROS2 subscriber silently receives no messages when QoS mismatches

- Rule: When a ROS2 subscriber never fires despite the topic being advertised, check QoS compatibility before debugging anything else — a BEST_EFFORT subscriber connected to a RELIABLE publisher silently receives nothing, with no warning from the middleware.
- Path: `debugging/ros2-subscriber-no-message-qos.md`
- Applicability: Any ROS2 system where a subscriber appears to be set up correctly but never receives messages, especially across package boundaries where QoS profiles differ.
