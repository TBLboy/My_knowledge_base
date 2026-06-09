# Quick Ref: action-client

## ROS2 action client timeout is often a goal-lifecycle mismatch, not a network issue

- Rule: When a ROS2 action client times out waiting for a result, first distinguish between three distinct failure modes: (1) the goal was never accepted by the server (goal response timeout), (2) the goal was accepted but never finished (result timeout), or (3) the goal finished but the result callback was not triggered. Each has a different root cause and fix.
- Path: `debugging/action-client-timeout-lifecycle.md`
- Applicability: ROS2 systems where orchestrators or skill nodes use action clients to invoke hardware actions and encounter timeout errors.
