# Staged Knowledge Proposals — CutTofo

**Distillation run**: 2026-06-09T15:30:00
**Project**: CutTofo (cuttofo)
**Source scan**: distillation/runs/2026-06-09T15-30-00.md
**Action**: All 4 candidates proposed as `add` — no existing KB entries cover these topics.

---

## cuttofo-0004: ROS2 workspace environment isolation is not automatic

```yaml
id: cuttofo-0004
title: "ROS2 workspace environment isolation is not automatic"
category: workflow
abstraction_level: operational
confidence: high
reusability: high
status: candidate
source_project: cuttofo
source_refs:
  - progress.md: 2026-06-07 14:35 CST (first hygiene cleanup)
  - progress.md: 2026-06-07 14:35 CST (second deep clean)
evidence_summary: >
  After duplicating a ROS2 workspace (tofu → cucumber), the old workspace's paths
  were silently baked into install/setup.bash because the build shell had sourced
  the old underlay. Environment variables (AMENT_PREFIX_PATH, COLCON_PREFIX_PATH,
  CMAKE_PREFIX_PATH, PYTHONPATH, LD_LIBRARY_PATH) all carried the old workspace
  as a permanent dependency. Fixing ~/.bashrc alone was insufficient — the install
  artifacts themselves were contaminated. Resolution required rebuilding the entire
  workspace in env -i with only /opt/ros/humble/setup.bash.
reusable_rule: >
  When a ROS2 workspace is cloned, moved, or duplicated, always rebuild in a clean
  shell (env -i bash --rcfile <(echo 'source /opt/ros/humble/setup.bash')). Never
  trust that install/setup.bash from a prior build is self-contained — it snapshots
  the underlay chain of its build environment.
applicability: Any ROS2 project that has been moved, copied, or shared across machines.
suggested_action: add
target_kb_path: workflow/ros2-workspace-environment-isolation.md
related_existing_entries:
  - config-behavior/trace-runtime-consumers-before-tuning.md (shared theme: environment state is not what config files alone declare)
tags:
  - ros2
  - workspace
  - environment
  - colcon
  - build
keywords:
  - install/setup.bash underlay pollution
  - AMENT_PREFIX_PATH contamination
  - workspace copy environment leak
  - clean build env -i
  - COLCON_PREFIX_PATH baked paths
triggers:
  - workspace copied
  - workspace moved
  - install/setup.bash
  - build environment
  - underlay chain
aliases:
  - ros2 workspace isolation
  - colcon build clean environment
  - setup.bash contamination
confidence: high
applicability: universal
```

### Comparison with existing KB

| Existing entry | Overlap | Verdict |
|---|---|---|
| `config-behavior/trace-runtime-consumers-before-tuning.md` | Loose thematic (environment vs config surface) | No conflict — different domain |

---

## cuttofo-0005: Python tools embedding rclpy need full ROS2 runtime, not just sys.path

```yaml
id: cuttofo-0005
title: "Python tools embedding rclpy need full ROS2 runtime, not just sys.path"
category: debugging
abstraction_level: operational
confidence: high
reusability: high
status: candidate
source_project: cuttofo
source_refs:
  - progress.md: 2026-06-07 19:56 CST (GUI startup fix)
evidence_summary: >
  A Tkinter GUI directly launching with python3 main.py failed progressively through
  3 layers: (1) missing source package in sys.path, (2) missing ROS2 message Python
  packages, (3) rclpy.create_client() failing with "Could not load library
  libdexbot_interfaces_low__rosidl_typesupport_fastrtps_c.so". Layers 1-2 could be
  fixed with sys.path patching, but layer 3 required the full ROS2 runtime environment
  (LD_LIBRARY_PATH, AMENT_PREFIX_PATH). The final fix auto-sources install/setup.bash
  and exec()s the same script with the enriched environment.
reusable_rule: >
  Python scripts that call rclpy.create_node(), create_client(), or
  create_subscription() need the full ROS2 runtime environment — not just Python
  import paths. The typesupport shared libraries are loaded dynamically and depend
  on AMENT_PREFIX_PATH + LD_LIBRARY_PATH. The robust pattern is: detect missing
  environment → source install/setup.bash → exec yourself.
applicability: Any Python GUI, CLI tool, or standalone script that embeds ROS2 client libraries.
suggested_action: add
target_kb_path: debugging/rclpy-tools-need-full-ros2-runtime.md
related_existing_entries:
  - debugging/ros2-subscriber-no-message-qos.md (shared theme: ROS2 middleware failures are often silent and environmental)
tags:
  - ros2
  - rclpy
  - python
  - environment
  - debugging
keywords:
  - rclpy.create_client failed load library
  - typesupport shared library not found
  - LD_LIBRARY_PATH ROS2 Python
  - AMENT_PREFIX_PATH rclpy
  - exec after source setup.bash
  - GUI ros2 runtime
triggers:
  - rclpy.create_client
  - rclpy.create_node
  - typesupport
  - load library failed
  - python3 main.py ros2
aliases:
  - rclpy runtime environment
  - ros2 python gui setup.bash
  - typesupport .so not found
confidence: high
applicability: universal
```

### Comparison with existing KB

| Existing entry | Overlap | Verdict |
|---|---|---|
| `debugging/ros2-subscriber-no-message-qos.md` | Shared ROS2 silent-failure theme | No conflict — middleware QoS vs runtime linking |
| `debugging/action-server-setoperatemode-failed.md` | Shared debugging category | No conflict — control lifecycle vs runtime environment |
| `debugging/action-client-timeout-lifecycle.md` | Shared debugging category | No conflict — action lifecycle vs runtime environment |

---

## cuttofo-0006: Tick-driven state machine is sufficient for predominantly linear robot workflows

```yaml
id: cuttofo-0006
title: "Tick-driven state machine is sufficient for predominantly linear robot workflows"
category: architecture
abstraction_level: pattern
confidence: medium
reusability: medium
status: candidate
source_project: cuttofo
source_refs:
  - business-logic/decision-records.md (first decision record: Tick-Driven Orchestrator)
evidence_summary: >
  The CutTofo orchestrator uses a simple tick-driven state machine (20Hz loop,
  explicit state enum, one active state at a time) to coordinate 7+ action skills.
  Despite the workflow having conditional branches (handle_approach optional, error
  handling), the tick-driven approach proved adequate and easier to debug than
  Behavior Trees or SMACH. The workflow is predominantly linear: approach → prepare
  → cut_round → prepare → cut_round → prepare → vertical_cut.
reusable_rule: >
  For robot workflows that are mostly sequential with occasional optional steps, a
  simple tick-driven state machine (state enum + loop at fixed frequency) is often
  sufficient. Reserve Behavior Trees for workflows with significant branching,
  parallel execution, or runtime re-planning. The tick-driven approach wins on
  debuggability: a single print(f"[{self._state}]") gives complete visibility.
applicability: Linear or mostly-linear multi-step robot task orchestration.
suggested_action: add
target_kb_path: architecture/tick-driven-state-machine-linear-workflows.md
related_existing_entries:
  - workflow/single-purpose-launches-and-central-orchestration.md (shared theme: keep orchestration explicit and central)
tags:
  - robotics
  - state-machine
  - orchestration
  - architecture
keywords:
  - tick-driven state machine
  - linear robot workflow
  - behavior tree alternative
  - SMACH alternative
  - robot task orchestration
  - state enum loop
triggers:
  - behavior tree
  - SMACH
  - state machine
  - orchestrator
  - workflow engine
  - robot task
aliases:
  - simple state machine vs behavior tree
  - tick-driven orchestrator
  - linear workflow state machine
confidence: medium
applicability: narrow (linear or mostly-linear robot workflows)
```

### Comparison with existing KB

| Existing entry | Overlap | Verdict |
|---|---|---|
| `workflow/single-purpose-launches-and-central-orchestration.md` | Shared orchestration theme | Complementary — launch composition vs control flow pattern |

---

## cuttofo-0007: Multi-axis tasks benefit from axis-specific control modes rather than one global mode

```yaml
id: cuttofo-0007
title: "Multi-axis tasks benefit from axis-specific control modes rather than one global mode"
category: patterns
abstraction_level: pattern
confidence: medium
reusability: medium
status: candidate
source_project: cuttofo
source_refs:
  - business-logic/decision-records.md (third decision record: Impedance vs Position Control)
evidence_summary: >
  The tofu cutting task uses impedance control for horizontal cut_round (force
  compliance to avoid crushing tofu) and position control for vertical_cut (precision
  to ensure complete cut-through). Using the same control mode for both would either
  crush the tofu (all position) or lose vertical precision (all impedance).
reusable_rule: >
  When a manipulation task spans multiple physical directions or phases with different
  requirements (compliance in one axis, precision in another), use different control
  modes per phase rather than one global mode. The control strategy should match the
  physical constraint, not the tool identity.
applicability: Multi-phase manipulation tasks where physical requirements differ between phases.
suggested_action: add
target_kb_path: patterns/axis-specific-control-modes.md
related_existing_entries: []
tags:
  - robotics
  - control
  - impedance-control
  - position-control
  - manipulation
keywords:
  - axis-specific control mode
  - impedance vs position control
  - force compliance horizontal
  - precision vertical cut
  - multi-phase manipulation
  - control strategy per phase
triggers:
  - impedance control
  - position control
  - force control
  - control mode
  - admittance control
  - multi-axis
aliases:
  - per-phase control strategy
  - hybrid control mode selection
  - impedance for compliance position for precision
confidence: medium
applicability: narrow (multi-phase manipulation with differing physical constraints)
```

### Comparison with existing KB

| Existing entry | Overlap | Verdict |
|---|---|---|
| None | — | New topic |

---

## Summary

| Candidate | Action | Target KB path | Confidence |
|---|---|---|---|
| cuttofo-0004 | add | workflow/ros2-workspace-environment-isolation.md | high |
| cuttofo-0005 | add | debugging/rclpy-tools-need-full-ros2-runtime.md | high |
| cuttofo-0006 | add | architecture/tick-driven-state-machine-linear-workflows.md | medium |
| cuttofo-0007 | add | patterns/axis-specific-control-modes.md | medium |

All 4 candidates are net-new with no conflicts against the existing 6 KB entries.
