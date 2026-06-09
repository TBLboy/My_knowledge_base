# Trigger: cannot-change-mode-while-executing

## Action server setOperateMode fails when previous operation has not released control

- Path: `debugging/action-server-setoperatemode-failed.md`
- Rule: A `setOperateMode(automatic)` call that fails is usually not a configuration problem — it means the action server's internal state machine still holds the previous operation's control. Before retrying the mode switch, ensure the previous action goal has been explicitly cancelled or has reached a terminal state.
- Tags: ros, debugging, action-server, robotics, orchestration
- Triggers: setOperateMode automatic failed, mode switch rejected, action server busy, cannot change mode while executing, previous motion not released
- Updated: 2026-06-09
