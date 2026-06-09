# Category: architecture

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
