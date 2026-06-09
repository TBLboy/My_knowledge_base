# Quick Ref: ros

## ROS2 action client timeout is often a goal-lifecycle mismatch, not a network issue

- Rule: When a ROS2 action client times out waiting for a result, first distinguish between three distinct failure modes: (1) the goal was never accepted by the server (goal response timeout), (2) the goal was accepted but never finished (result timeout), or (3) the goal finished but the result callback was not triggered. Each has a different root cause and fix.
- Path: `debugging/action-client-timeout-lifecycle.md`
- Applicability: ROS2 systems where orchestrators or skill nodes use action clients to invoke hardware actions and encounter timeout errors.

## Action server setOperateMode fails when previous operation has not released control

- Rule: A `setOperateMode(automatic)` call that fails is usually not a configuration problem — it means the action server's internal state machine still holds the previous operation's control. Before retrying the mode switch, ensure the previous action goal has been explicitly cancelled or has reached a terminal state.
- Path: `debugging/action-server-setoperatemode-failed.md`
- Applicability: ROS2 action servers (especially hardware-control actions) that reject mode switches because a prior goal handle is still active or the internal state machine is in a transitional state.

## ROS2 subscriber silently receives no messages when QoS mismatches

- Rule: When a ROS2 subscriber never fires despite the topic being advertised, check QoS compatibility before debugging anything else — a BEST_EFFORT subscriber connected to a RELIABLE publisher silently receives nothing, with no warning from the middleware.
- Path: `debugging/ros2-subscriber-no-message-qos.md`
- Applicability: Any ROS2 system where a subscriber appears to be set up correctly but never receives messages, especially across package boundaries where QoS profiles differ.

## Keep launches single-purpose and compose full workflows centrally

- Rule: Keep subsystem launch files single-purpose, and assemble the full workflow in one explicit orchestration entry point.
- Path: `workflow/single-purpose-launches-and-central-orchestration.md`
- Applicability: ROS or multi-service systems with layered bringup, testing, and workflow execution entry points.
