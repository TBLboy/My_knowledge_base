---
id: kb-debugging-0001
title: ROS2 subscriber silently receives no messages when QoS mismatches
category: debugging
tags: [ros, debugging, qos, communication]
keywords: [qos mismatch, no message, topic not found, subscriber silent, best_effort vs reliable, image_callback never fires, dds compatibility]
triggers:
  - topic exists but no message
  - subscriber callback not firing
  - qos mismatch silent failure
  - best_effort publisher reliable subscriber
  - no message on topic
aliases:
  - ros2 topic no message
  - topic advertised but no data
  - subscriber callback never triggered
source_projects: [cuttofo]
source_refs:
  - cuttofo:.project-log/progress.md#2026-06-06-2345
confidence: high
applicability: Any ROS2 system where a subscriber appears to be set up correctly but never receives messages, especially across package boundaries where QoS profiles differ.
updated_at: 2026-06-09
---

## Rule

When a ROS2 subscriber never fires despite the topic being advertised, check QoS compatibility before debugging anything else — a BEST_EFFORT subscriber connected to a RELIABLE publisher silently receives nothing, with no warning from the middleware.

## Why

DDS discovery succeeds regardless of QoS, so `ros2 topic list` and `ros2 topic info` show the connection as active. But if the subscriber offers BEST_EFFORT and the publisher offers RELIABLE (or vice versa), the DDS middleware will not deliver any messages. There is no ROS2-level diagnostic for this — the topic simply stays silent.

## When it applies

Use this when:
- A topic appears in `ros2 topic list` and `ros2 topic info` shows the correct type
- `ros2 topic echo` works (because echo adapts its QoS)
- But the node's subscriber callback never fires
- The subscriber and publisher were developed by different teams or copied from different codebases

## Counterexamples

Do not assume QoS mismatch if:
- The topic genuinely has no publisher at the moment
- The node is not spinning or the executor is blocked
- The callback is registered on a different topic name

## Evidence Lineage

- project: `cuttofo`
- source refs: `.project-log/progress.md` (2026-06-06 23:45 CST)
- distillation run: `distillation-ledger/runs/2026-06-09T00-00-00-cuttofo-debugging.md`
