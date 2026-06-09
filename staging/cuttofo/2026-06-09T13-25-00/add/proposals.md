# Add Proposals

## architecture/perception-owns-task-geometry.md

---
id: kb-architecture-0001
title: Perception should own shared task geometry
category: architecture
tags: [robotics, perception, geometry, contract-design]
keywords: [tcp_target, downstream consumer, recompute, shared geometry, target pose]
triggers:
  - duplicated geometry recomputation
  - prepare recomputes target pose
  - visualizer recomputes perception result
  - multiple modules derive different target geometry
related:
  - [[trace-runtime-consumers-before-tuning]]
source_projects: [cuttofo]
source_refs:
  - cuttofo:.project-log/progress.md#2026-06-07-1243
  - cuttofo:.project-log/progress.md#2026-06-07-1805
  - cuttofo:.project-log/business-logic/main.md
confidence: high
applicability: Robotics perception-to-action pipelines with shared geometry consumers.
updated_at: 2026-06-09
source_type: distilled-from-project
---

## Rule

When several downstream modules depend on the same interpreted perception result, one layer should own that geometry contract and publish it once.

## Why

Local recomputation in prepare, visualizers, and task-specific consumers drifts over time and creates silent disagreement about the target.

## When it applies

Use this when multiple modules depend on a shared target pose, edge direction, grasp point, or task geometry derived from the same perception input.

## Evidence Lineage

- project: `cuttofo`
- source refs:
  - `.project-log/progress.md` (2026-06-07 12:43 CST)
  - `.project-log/progress.md` (2026-06-07 18:05 CST)
  - `.project-log/business-logic/main.md`
- distillation run:
  - `distillation-ledger/runs/2026-06-09T13-25-00-cuttofo.md`

## config-behavior/trace-runtime-consumers-before-tuning.md

---
id: kb-config-behavior-0001
title: Trace runtime consumers before tuning config
category: config-behavior
tags: [config, runtime-behavior, debugging, orchestration]
keywords: [yaml parameter, runtime consumer, effective control, parameter tracing, config tuning]
triggers:
  - config not effective
  - yaml changed but behavior unchanged
  - parameter appears configurable but does nothing
  - trace runtime consumer before tuning
related:
  - [[perception-owns-task-geometry]]
source_projects: [cuttofo]
source_refs:
  - cuttofo:.project-log/progress.md#2026-06-07-1735
  - cuttofo:.project-log/progress.md#2026-06-07-1805
  - cuttofo:.project-log/progress.md#2026-06-08-current
  - cuttofo:.project-log/config/config-schema.md
confidence: high
applicability: Multi-layer systems with YAML config, runtime overrides, and orchestration-mediated parameter application.
updated_at: 2026-06-09
source_type: distilled-from-project
---

## Rule

A parameter is not a real control surface until you trace where it is read, transformed, and finally consumed at runtime.

## Why

Multi-layer systems often contain stale, duplicated, or redirected parameters that look configurable in YAML but do not control the live behavior you are trying to tune.

## When it applies

Use this whenever behavior depends on config files, runtime overrides, action goals, or orchestration-mediated parameter application.

## Evidence Lineage

- project: `cuttofo`
- source refs:
  - `.project-log/progress.md` (2026-06-07 17:35 CST)
  - `.project-log/progress.md` (2026-06-07 18:05 CST)
  - `.project-log/progress.md` (2026-06-08 current CST)
  - `.project-log/config/config-schema.md`
- distillation run:
  - `distillation-ledger/runs/2026-06-09T13-25-00-cuttofo.md`

## workflow/single-purpose-launches-and-central-orchestration.md

---
id: kb-workflow-0001
title: Keep launches single-purpose and compose full workflows centrally
category: workflow
tags: [workflow, launch, orchestration, ros]
keywords: [single-purpose launch, central orchestration, bringup boundary, nested launch ownership]
triggers:
  - nested launch side effects
  - launch file implicitly starts other subsystems
  - bringup boundary unclear
  - full workflow assembly belongs in orchestrator
related:
  - [[trace-runtime-consumers-before-tuning]]
source_projects: [cuttofo]
source_refs:
  - cuttofo:.project-log/progress.md#2026-06-08-current
  - cuttofo:.project-log/current-session.md
confidence: high
applicability: ROS or multi-service systems with layered bringup, testing, and workflow execution entry points.
updated_at: 2026-06-09
source_type: distilled-from-project
---

## Rule

Keep subsystem launch files single-purpose, and assemble the full workflow in one explicit orchestration entry point.

## Why

Nested launch ownership hides side effects, makes runtime boundaries unclear, and complicates bringup debugging.

## When it applies

Use this when a system has separate layers for vision, perception, visualization, skill servers, and full workflow execution.

## Evidence Lineage

- project: `cuttofo`
- source refs:
  - `.project-log/progress.md` (2026-06-08 current CST)
  - `.project-log/current-session.md`
- distillation run:
  - `distillation-ledger/runs/2026-06-09T13-25-00-cuttofo.md`
