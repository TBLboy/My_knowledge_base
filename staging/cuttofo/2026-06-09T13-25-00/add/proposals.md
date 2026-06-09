# Add Proposals

## architecture/perception-owns-task-geometry.md

---
title: Perception should own shared task geometry
tags: [robotics, perception, geometry, contract-design]
confidence: high
source_type: distilled-from-project
updated: 2026-06-09
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
title: Trace runtime consumers before tuning config
tags: [config, runtime-behavior, debugging, orchestration]
confidence: high
source_type: distilled-from-project
updated: 2026-06-09
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
title: Keep launches single-purpose and compose full workflows centrally
tags: [workflow, launch, orchestration, ros]
confidence: high
source_type: distilled-from-project
updated: 2026-06-09
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
