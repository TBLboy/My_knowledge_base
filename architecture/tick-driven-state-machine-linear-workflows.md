---
id: kb-architecture-0002
title: Tick-driven state machine is sufficient for predominantly linear robot workflows
category: architecture
tags: [robotics, state-machine, orchestration, architecture]
keywords: [tick-driven state machine, linear robot workflow, behavior tree alternative, SMACH alternative, robot task orchestration, state enum loop]
triggers:
  - behavior tree
  - SMACH
  - state machine
  - orchestrator pattern
  - workflow engine choice
  - robot task sequencing
aliases:
  - simple state machine vs behavior tree
  - tick-driven orchestrator
  - linear workflow state machine
related:
  - "[[single-purpose-launches-and-central-orchestration]]"
source_projects: [cuttofo]
source_refs:
  - cuttofo:.project-log/business-logic/decision-records.md#tick-driven-orchestrator
confidence: medium
applicability: Linear or mostly-linear multi-step robot task orchestration.
updated_at: 2026-06-09
---

## Rule

For robot workflows that are mostly sequential with occasional optional steps, a simple tick-driven state machine (state enum + loop at fixed frequency) is often sufficient. Reserve Behavior Trees for workflows with significant branching, parallel execution, or runtime re-planning.

## Why

A tick-driven state machine wins on debuggability: a single `print(f"[{self._state}]")` gives complete visibility into what the system is doing. Behavior Trees and SMACH add abstraction layers that obscure control flow during debugging. The CutTofo orchestrator coordinates 7+ action skills at 20Hz with a simple state enum and one active state at a time, handling optional conditional branches (handle_approach) and error recovery without needing a more complex framework.

## When it applies

Use this when:
- The workflow is predominantly linear (A → B → C → D)
- Optional steps are simple branches, not deeply nested decision trees
- Debug visibility is more important than runtime flexibility
- The team wants to avoid framework lock-in

## Counterexamples

Use Behavior Trees or a more complex framework when:
- The workflow has significant parallel execution branches
- Runtime re-planning or dynamic task insertion is needed
- The state space is large and transitions are non-obvious

## Evidence Lineage

- project: `cuttofo`
- source refs: `.project-log/business-logic/decision-records.md` (first decision record)
- distillation run: `distillation-ledger/runs/2026-06-09T15-30-00-cuttofo.md`
