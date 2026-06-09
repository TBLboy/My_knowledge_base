# Quick Ref: robotics

## Perception should own shared task geometry

- Rule: When several downstream modules depend on the same interpreted perception result, one layer should own that geometry contract and publish it once.
- Path: `architecture/perception-owns-task-geometry.md`
- Applicability: Robotics perception-to-action pipelines with shared geometry consumers.

## Tick-driven state machine is sufficient for predominantly linear robot workflows

- Rule: For robot workflows that are mostly sequential with occasional optional steps, a simple tick-driven state machine (state enum + loop at fixed frequency) is often sufficient. Reserve Behavior Trees for workflows with significant branching, parallel execution, or runtime re-planning.
- Path: `architecture/tick-driven-state-machine-linear-workflows.md`
- Applicability: Linear or mostly-linear multi-step robot task orchestration.

## Action server setOperateMode fails when previous operation has not released control

- Rule: A `setOperateMode(automatic)` call that fails is usually not a configuration problem — it means the action server's internal state machine still holds the previous operation's control. Before retrying the mode switch, ensure the previous action goal has been explicitly cancelled or has reached a terminal state.
- Path: `debugging/action-server-setoperatemode-failed.md`
- Applicability: ROS2 action servers (especially hardware-control actions) that reject mode switches because a prior goal handle is still active or the internal state machine is in a transitional state.

## Use axis-specific control modes for multi-phase manipulation tasks

- Rule: When a manipulation task spans multiple physical directions or phases with different requirements (compliance in one axis, precision in another), use different control modes per phase rather than one global mode. The control strategy should match the physical constraint, not the tool identity.
- Path: `patterns/axis-specific-control-modes.md`
- Applicability: Multi-phase manipulation tasks where physical requirements differ between phases.
