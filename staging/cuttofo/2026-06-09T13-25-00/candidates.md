# CutTofo Draft Candidates

- Source project: `cuttofo`
- Run time: `2026-06-09T13-25-00`
- Source path: `/home/tbl/Project/cucumber/dexbot_ros2_ws/src/dexbot_middle_layer/CutTofo/.project-log`

## Candidates

### cuttofo-0001

```yaml
id: cuttofo-0001
title: Perception should own tofu target geometry; downstream modules should consume, not recompute.
category: architecture
abstraction_level: system-pattern
confidence: high
reusability: high
status: candidate
source_project: cuttofo
source_refs:
  - .project-log/progress.md (2026-06-07 12:43 CST)
  - .project-log/progress.md (2026-06-07 18:05 CST)
  - .project-log/business-logic/main.md
evidence_summary: The project explicitly removed duplicated target-geometry recomputation from prepare and visualization paths, converging on a single perception-published `tcp_target` consumed downstream.
reusable_rule: When multiple downstream modules depend on the same interpreted perception geometry, centralize ownership in the perception contract and make downstream modules consume it rather than recomputing local variants.
applicability: Robotics perception-to-action pipelines with shared geometry consumers.
suggested_action: add
target_kb_path: architecture/perception-owns-task-geometry.md
related_existing_entries: []
```

### cuttofo-0002

```yaml
id: cuttofo-0002
title: Config parameters must be traced to real runtime consumers before treating them as effective controls.
category: config-behavior
abstraction_level: engineering-rule
confidence: high
reusability: high
status: candidate
source_project: cuttofo
source_refs:
  - .project-log/progress.md (2026-06-07 17:35 CST)
  - .project-log/progress.md (2026-06-07 18:05 CST)
  - .project-log/progress.md (2026-06-08 current CST)
  - .project-log/config/config-schema.md
evidence_summary: The project repeatedly found that parameters defined in YAML were misleading until runtime ownership and actual consumer code paths were traced, especially across perception, prepare, and orchestration layers.
reusable_rule: Do not assume a declared parameter controls behavior. Trace where it is read, where it is transformed, and which runtime component actually consumes it before treating it as a real tuning surface.
applicability: Multi-layer systems with YAML config, runtime overrides, and orchestration-mediated parameter application.
suggested_action: add
target_kb_path: config-behavior/trace-runtime-consumers-before-tuning.md
related_existing_entries: []
```

### cuttofo-0003

```yaml
id: cuttofo-0003
title: Launch ownership should stay single-purpose; full workflow assembly belongs in the orchestration layer.
category: workflow
abstraction_level: architecture-rule
confidence: high
reusability: medium-high
status: candidate
source_project: cuttofo
source_refs:
  - .project-log/progress.md (2026-06-08 current CST)
  - .project-log/current-session.md
evidence_summary: The project had to undo nested launch ownership where perception launch files implicitly started vision and visualization, then move full-stack assembly into the orchestrator launch layer.
reusable_rule: Keep subsystem launch files single-purpose and move full-stack composition into one explicit orchestration entry point; this reduces hidden side effects and makes bringup/debugging boundaries clearer.
applicability: ROS or multi-service systems with layered bringup, testing, and workflow execution entry points.
suggested_action: add
target_kb_path: workflow/single-purpose-launches-and-central-orchestration.md
related_existing_entries: []
```
