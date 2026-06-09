---
id: kb-debugging-0002
title: Action server setOperateMode fails when previous operation has not released control
category: debugging
tags: [ros, debugging, action-server, robotics, orchestration]
keywords: [setOperateMode, automatic mode, action server, mode switch, control release, previous motion, startOperate, stopOperate]
triggers:
  - setOperateMode automatic failed
  - mode switch rejected
  - action server busy
  - cannot change mode while executing
  - previous motion not released
aliases:
  - setOperateMode failed
  - action mode switch error
  - cannot set automatic mode
source_projects: [cuttofo]
source_refs:
  - cuttofo:.project-log/progress.md
confidence: high
applicability: ROS2 action servers (especially hardware-control actions) that reject mode switches because a prior goal handle is still active or the internal state machine is in a transitional state.
updated_at: 2026-06-09
---

## Rule

A `setOperateMode(automatic)` call that fails is usually not a configuration problem — it means the action server's internal state machine still holds the previous operation's control. Before retrying the mode switch, ensure the previous action goal has been explicitly cancelled or has reached a terminal state.

## Why

Hardware-facing action servers often use a state machine where `startOperate()` acquires exclusive control and `stopOperate()` (or goal abort/cancel) releases it. If the previous motion was interrupted — due to an error, a partial cancel, or an unhandled transition — the server may still believe it owns the hardware and reject the mode switch.

## When it applies

Use this when:
- `setOperateMode(automatic)` returns an error or times out
- The action server was previously used for a motion that may not have cleanly terminated
- The error is intermittent (works on first run, fails on retry)
- You are calling the action server from a workflow orchestrator that may abort actions on cancellation

## Counterexamples

Do not assume control conflict if:
- The action server has never been started or connected
- The mode switch is rejected due to a parameter or permission check, not a state conflict
- The server is genuinely in an error state that requires a hardware reset, not just a control release

## Evidence Lineage

- project: `cuttofo`
- source refs: `.project-log/progress.md`
- distillation run: `distillation-ledger/runs/2026-06-09T00-00-00-cuttofo-debugging.md`
