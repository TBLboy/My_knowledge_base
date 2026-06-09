# Trigger: force-control

## Use axis-specific control modes for multi-phase manipulation tasks

- Path: `patterns/axis-specific-control-modes.md`
- Rule: When a manipulation task spans multiple physical directions or phases with different requirements (compliance in one axis, precision in another), use different control modes per phase rather than one global mode. The control strategy should match the physical constraint, not the tool identity.
- Tags: robotics, control, impedance-control, position-control, manipulation
- Triggers: impedance control, position control, force control, control mode selection, admittance control, multi-axis manipulation
- Updated: 2026-06-09
