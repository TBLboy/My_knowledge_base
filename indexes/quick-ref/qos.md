# Quick Ref: qos

## ROS2 subscriber silently receives no messages when QoS mismatches

- Rule: When a ROS2 subscriber never fires despite the topic being advertised, check QoS compatibility before debugging anything else — a BEST_EFFORT subscriber connected to a RELIABLE publisher silently receives nothing, with no warning from the middleware.
- Path: `debugging/ros2-subscriber-no-message-qos.md`
- Applicability: Any ROS2 system where a subscriber appears to be set up correctly but never receives messages, especially across package boundaries where QoS profiles differ.
