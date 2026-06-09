# Trigger: robot-task-sequencing

## Tick-driven state machine is sufficient for predominantly linear robot workflows

- Path: `architecture/tick-driven-state-machine-linear-workflows.md`
- Rule: For robot workflows that are mostly sequential with occasional optional steps, a simple tick-driven state machine (state enum + loop at fixed frequency) is often sufficient. Reserve Behavior Trees for workflows with significant branching, parallel execution, or runtime re-planning.
- Tags: robotics, state-machine, orchestration, architecture
- Triggers: behavior tree, SMACH, state machine, orchestrator pattern, workflow engine choice, robot task sequencing
- Updated: 2026-06-09
