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
---

## Rule

When several downstream modules depend on the same interpreted perception result, one layer should own that geometry contract and publish it once.

## Why

Local recomputation in prepare, visualizers, and task-specific consumers drifts over time and creates silent disagreement about the target.

## When it applies

Use this when multiple modules depend on a shared target pose, edge direction, grasp point, or task geometry derived from the same perception input.

## Counterexamples

Do not force this pattern when consumers genuinely require different abstractions over the same raw perception data and those abstractions have separate owners.

## Evidence Lineage

- project: `cuttofo`
- source refs:
  - `.project-log/progress.md` (2026-06-07 12:43 CST)
  - `.project-log/progress.md` (2026-06-07 18:05 CST)
  - `.project-log/business-logic/main.md`
- distillation run:
  - `distillation-ledger/runs/2026-06-09T13-25-00-cuttofo.md`
