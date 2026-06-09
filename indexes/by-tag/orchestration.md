# Tag: orchestration

## Tick-driven state machine is sufficient for predominantly linear robot workflows

- Path: `architecture/tick-driven-state-machine-linear-workflows.md`
- Rule: For robot workflows that are mostly sequential with occasional optional steps, a simple tick-driven state machine (state enum + loop at fixed frequency) is often sufficient. Reserve Behavior Trees for workflows with significant branching, parallel execution, or runtime re-planning.
- Tags: robotics, state-machine, orchestration, architecture
- Triggers: behavior tree, SMACH, state machine, orchestrator pattern, workflow engine choice, robot task sequencing
- Updated: 2026-06-09

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

## Keep launches single-purpose and compose full workflows centrally

- Path: `workflow/single-purpose-launches-and-central-orchestration.md`
- Rule: Keep subsystem launch files single-purpose, and assemble the full workflow in one explicit orchestration entry point.
- Tags: workflow, launch, orchestration, ros
- Triggers: nested launch side effects, launch file implicitly starts other subsystems, bringup boundary unclear, full workflow assembly belongs in orchestrator
- Updated: 2026-06-09
