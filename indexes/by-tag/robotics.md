# Tag: robotics

## Perception should own shared task geometry

- Path: `architecture/perception-owns-task-geometry.md`
- Rule: When several downstream modules depend on the same interpreted perception result, one layer should own that geometry contract and publish it once.
- Tags: robotics, perception, geometry, contract-design
- Triggers: duplicated geometry recomputation, prepare recomputes target pose, visualizer recomputes perception result, multiple modules derive different target geometry
- Updated: 2026-06-09

## Tick-driven state machine is sufficient for predominantly linear robot workflows

- Path: `architecture/tick-driven-state-machine-linear-workflows.md`
- Rule: For robot workflows that are mostly sequential with occasional optional steps, a simple tick-driven state machine (state enum + loop at fixed frequency) is often sufficient. Reserve Behavior Trees for workflows with significant branching, parallel execution, or runtime re-planning.
- Tags: robotics, state-machine, orchestration, architecture
- Triggers: behavior tree, SMACH, state machine, orchestrator pattern, workflow engine choice, robot task sequencing
- Updated: 2026-06-09

## Action server setOperateMode fails when previous operation has not released control

- Path: `debugging/action-server-setoperatemode-failed.md`
- Rule: A `setOperateMode(automatic)` call that fails is usually not a configuration problem — it means the action server's internal state machine still holds the previous operation's control. Before retrying the mode switch, ensure the previous action goal has been explicitly cancelled or has reached a terminal state.
- Tags: ros, debugging, action-server, robotics, orchestration
- Triggers: setOperateMode automatic failed, mode switch rejected, action server busy, cannot change mode while executing, previous motion not released
- Updated: 2026-06-09

## Use axis-specific control modes for multi-phase manipulation tasks

- Path: `patterns/axis-specific-control-modes.md`
- Rule: When a manipulation task spans multiple physical directions or phases with different requirements (compliance in one axis, precision in another), use different control modes per phase rather than one global mode. The control strategy should match the physical constraint, not the tool identity.
- Tags: robotics, control, impedance-control, position-control, manipulation
- Triggers: impedance control, position control, force control, control mode selection, admittance control, multi-axis manipulation
- Updated: 2026-06-09
