# Trigger: action-timeout

## ROS2 action client timeout is often a goal-lifecycle mismatch, not a network issue

- Path: `debugging/action-client-timeout-lifecycle.md`
- Rule: When a ROS2 action client times out waiting for a result, first distinguish between three distinct failure modes: (1) the goal was never accepted by the server (goal response timeout), (2) the goal was accepted but never finished (result timeout), or (3) the goal finished but the result callback was not triggered. Each has a different root cause and fix.
- Tags: ros, debugging, action-client, timeout, orchestration
- Triggers: action timeout, goal not completing, wait for result hangs, action client no response
- Updated: 2026-06-09
