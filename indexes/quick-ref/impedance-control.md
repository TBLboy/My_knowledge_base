# Quick Ref: impedance-control

## Use axis-specific control modes for multi-phase manipulation tasks

- Rule: When a manipulation task spans multiple physical directions or phases with different requirements (compliance in one axis, precision in another), use different control modes per phase rather than one global mode. The control strategy should match the physical constraint, not the tool identity.
- Path: `patterns/axis-specific-control-modes.md`
- Applicability: Multi-phase manipulation tasks where physical requirements differ between phases.
