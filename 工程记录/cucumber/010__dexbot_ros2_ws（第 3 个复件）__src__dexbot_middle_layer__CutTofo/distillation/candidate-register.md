# Distillation Candidate Register

| Candidate ID | Title | Category | Status | Suggested Action | Last Seen | Knowledge Target |
|---|---|---|---|---|---|---|
| cuttofo-0001 | Perception should own tofu target geometry; downstream modules should consume, not recompute. | architecture | accepted | add | 2026-06-09T13:25:00 | architecture/perception-owns-task-geometry.md |
| cuttofo-0002 | Config parameters must be traced to real runtime consumers before treating them as effective controls. | config-behavior | accepted | add | 2026-06-09T13:25:00 | config-behavior/trace-runtime-consumers-before-tuning.md |
| cuttofo-0003 | Launch ownership should stay single-purpose; full workflow assembly belongs in the orchestration layer. | workflow | accepted | add | 2026-06-09T13:25:00 | workflow/single-purpose-launches-and-central-orchestration.md |
| cuttofo-0004 | ROS2 workspace environment isolation is not automatic — install/setup.bash bakes in the build underlay chain. | workflow | accepted | add | 2026-06-09T15:30:00 | workflow/ros2-workspace-environment-isolation.md |
| cuttofo-0005 | Python tools embedding rclpy need full ROS2 runtime (LD_LIBRARY_PATH), not just sys.path. | debugging | accepted | add | 2026-06-09T15:30:00 | debugging/rclpy-tools-need-full-ros2-runtime.md |
| cuttofo-0006 | Tick-driven state machine is sufficient for predominantly linear robot workflows. | architecture | accepted | add | 2026-06-09T15:30:00 | architecture/tick-driven-state-machine-linear-workflows.md |
| cuttofo-0007 | Multi-axis tasks benefit from axis-specific control modes rather than one global mode. | patterns | accepted | add | 2026-06-09T15:30:00 | patterns/axis-specific-control-modes.md |

Status values:
- `candidate`
- `accepted`
- `merged`
- `rejected`
- `superseded`
