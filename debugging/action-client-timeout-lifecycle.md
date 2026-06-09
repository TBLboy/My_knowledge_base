---
id: kb-debugging-0003
title: ROS2 action client timeout is often a goal-lifecycle mismatch, not a network issue
category: debugging
tags: [ros, debugging, action-client, timeout, orchestration]
keywords: [action timeout, goal handle, result callback, action client, async send goal, goal response, result timeout]
triggers:
  - action timeout
  - goal not completing
  - wait for result hangs
  - action client no response
aliases:
  - ros2 action timeout
  - goal handle timeout
  - action server not responding
source_projects: [cuttofo]
source_refs:
  - cuttofo:.project-log/progress.md
confidence: medium
applicability: ROS2 systems where orchestrators or skill nodes use action clients to invoke hardware actions and encounter timeout errors.
updated_at: 2026-06-09
---

## Rule

When a ROS2 action client times out waiting for a result, first distinguish between three distinct failure modes: (1) the goal was never accepted by the server (goal response timeout), (2) the goal was accepted but never finished (result timeout), or (3) the goal finished but the result callback was not triggered. Each has a different root cause and fix.

## Why

ROS2 action clients wrap three independent async events — goal acceptance, feedback stream, and result delivery — into a single API. A generic "timeout" error conflates all three. In orchestrated workflows especially, the difference between "the server didn't hear you" and "the server heard you but is still working" determines whether you should retry, wait longer, or cancel and reset.

## When it applies

Use this when:
- An orchestrator or skill node reports a timeout from an action client call
- The timeout is inconsistent (sometimes works, sometimes doesn't)
- You need to decide between increasing the timeout, adding a retry, or re-architecting the call pattern

## Counterexamples

Do not assume goal-lifecycle mismatch if:
- The action server process has genuinely crashed or is not running
- The network between nodes is unreliable or saturated
- The action itself legitimately takes longer than the configured timeout

## Evidence Lineage

- project: `cuttofo`
- source refs: `.project-log/progress.md`
- distillation run: `distillation-ledger/runs/2026-06-09T00-00-00-cuttofo-debugging.md`
