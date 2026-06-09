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
---

## Rule

A parameter is not a real control surface until you trace where it is read, transformed, and finally consumed at runtime.

## Why

Multi-layer systems often contain stale, duplicated, or redirected parameters that look configurable in YAML but do not control the live behavior you are trying to tune.

## When it applies

Use this whenever behavior depends on config files, runtime overrides, action goals, or orchestration-mediated parameter application.

## Counterexamples

Do not spend time on deep runtime tracing when the parameter-to-behavior path is already direct, local, and verified by code ownership plus tests.

## Evidence Lineage

- project: `cuttofo`
- source refs:
  - `.project-log/progress.md` (2026-06-07 17:35 CST)
  - `.project-log/progress.md` (2026-06-07 18:05 CST)
  - `.project-log/progress.md` (2026-06-08 current CST)
  - `.project-log/config/config-schema.md`
- distillation run:
  - `distillation-ledger/runs/2026-06-09T13-25-00-cuttofo.md`
