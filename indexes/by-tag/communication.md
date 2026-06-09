# Tag: communication

## ROS2 subscriber silently receives no messages when QoS mismatches

- Path: `debugging/ros2-subscriber-no-message-qos.md`
- Rule: When a ROS2 subscriber never fires despite the topic being advertised, check QoS compatibility before debugging anything else — a BEST_EFFORT subscriber connected to a RELIABLE publisher silently receives nothing, with no warning from the middleware.
- Tags: ros, debugging, qos, communication
- Triggers: topic exists but no message, subscriber callback not firing, qos mismatch silent failure, best_effort publisher reliable subscriber, no message on topic
- Updated: 2026-06-09
