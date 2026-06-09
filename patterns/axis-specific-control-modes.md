---
id: kb-patterns-0001
title: Use axis-specific control modes for multi-phase manipulation tasks
category: patterns
tags: [robotics, control, impedance-control, position-control, manipulation]
keywords: [axis-specific control mode, impedance vs position control, force compliance horizontal, precision vertical cut, multi-phase manipulation, control strategy per phase]
triggers:
  - impedance control
  - position control
  - force control
  - control mode selection
  - admittance control
  - multi-axis manipulation
aliases:
  - per-phase control strategy
  - hybrid control mode selection
  - impedance for compliance position for precision
source_projects: [cuttofo]
source_refs:
  - cuttofo:.project-log/business-logic/decision-records.md#impedance-vs-position-control
confidence: medium
applicability: Multi-phase manipulation tasks where physical requirements differ between phases.
updated_at: 2026-06-09
---

## Rule

When a manipulation task spans multiple physical directions or phases with different requirements (compliance in one axis, precision in another), use different control modes per phase rather than one global mode. The control strategy should match the physical constraint, not the tool identity.

## Why

Using the same control mode for all phases creates a trade-off that hurts at least one phase. All-position control risks crushing delicate objects during contact; all-impedance control loses precision for accurate positioning. The tofu cutting task demonstrates this: impedance control for horizontal cut_round (force compliance to avoid crushing the tofu) and position control for vertical_cut (precision to ensure complete cut-through).

## When it applies

Use this when:
- Different phases of a task have different physical contact requirements
- One axis/phase needs compliance while another needs precision
- The tool is the same but the physical interaction differs

## Counterexamples

Do not over-segment control modes when all phases share the same physical constraints — switching modes adds complexity and transition overhead.

## Evidence Lineage

- project: `cuttofo`
- source refs: `.project-log/business-logic/decision-records.md` (third decision record)
- distillation run: `distillation-ledger/runs/2026-06-09T15-30-00-cuttofo.md`
