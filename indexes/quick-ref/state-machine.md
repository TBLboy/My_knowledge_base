# Quick Ref: state-machine

## Tick-driven state machine is sufficient for predominantly linear robot workflows

- Rule: For robot workflows that are mostly sequential with occasional optional steps, a simple tick-driven state machine (state enum + loop at fixed frequency) is often sufficient. Reserve Behavior Trees for workflows with significant branching, parallel execution, or runtime re-planning.
- Path: `architecture/tick-driven-state-machine-linear-workflows.md`
- Applicability: Linear or mostly-linear multi-step robot task orchestration.
