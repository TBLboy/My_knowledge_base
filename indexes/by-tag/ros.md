# Tag: ros

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

## ROS2 subscriber silently receives no messages when QoS mismatches

- Path: `debugging/ros2-subscriber-no-message-qos.md`
- Rule: When a ROS2 subscriber never fires despite the topic being advertised, check QoS compatibility before debugging anything else — a BEST_EFFORT subscriber connected to a RELIABLE publisher silently receives nothing, with no warning from the middleware.
- Tags: ros, debugging, qos, communication
- Triggers: topic exists but no message, subscriber callback not firing, qos mismatch silent failure, best_effort publisher reliable subscriber, no message on topic
- Updated: 2026-06-09

## Keep launches single-purpose and compose full workflows centrally

- Path: `workflow/single-purpose-launches-and-central-orchestration.md`
- Rule: Keep subsystem launch files single-purpose, and assemble the full workflow in one explicit orchestration entry point.
- Tags: workflow, launch, orchestration, ros
- Triggers: nested launch side effects, launch file implicitly starts other subsystems, bringup boundary unclear, full workflow assembly belongs in orchestrator
- Updated: 2026-06-09
