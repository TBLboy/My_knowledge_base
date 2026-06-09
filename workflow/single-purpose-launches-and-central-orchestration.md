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
---

## Rule

Keep subsystem launch files single-purpose, and assemble the full workflow in one explicit orchestration entry point.

## Why

Nested launch ownership hides side effects, makes runtime boundaries unclear, and complicates bringup debugging.

## When it applies

Use this when a system has separate layers for vision, perception, visualization, skill servers, and full workflow execution.

## Counterexamples

Do not split out tiny launches just for purity when a subsystem is truly inseparable and always deployed as one atomic unit.

## Evidence Lineage

- project: `cuttofo`
- source refs:
  - `.project-log/progress.md` (2026-06-08 current CST)
  - `.project-log/current-session.md`
- distillation run:
  - `distillation-ledger/runs/2026-06-09T13-25-00-cuttofo.md`
