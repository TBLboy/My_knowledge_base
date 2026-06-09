---
id: kb-debugging-0004
title: Python tools embedding rclpy need full ROS2 runtime, not just sys.path
category: debugging
tags: [ros2, rclpy, python, environment, debugging]
keywords: [rclpy.create_client failed load library, typesupport shared library not found, LD_LIBRARY_PATH ROS2 Python, AMENT_PREFIX_PATH rclpy, exec after source setup.bash, GUI ros2 runtime]
triggers:
  - rclpy.create_client fails
  - rclpy.create_node fails
  - typesupport library not found
  - load library failed rosidl_typesupport
  - python3 main.py ros2
  - Could not load library
aliases:
  - rclpy runtime environment
  - ros2 python gui setup.bash
  - typesupport .so not found
  - ros2 python tool environment
related:
  - "[[ros2-subscriber-no-message-qos]]"
source_projects: [cuttofo]
source_refs:
  - cuttofo:.project-log/progress.md#2026-06-07-1956
confidence: high
applicability: Any Python GUI, CLI tool, or standalone script that embeds ROS2 client libraries.
updated_at: 2026-06-09
---

## Rule

Python scripts that call `rclpy.create_node()`, `create_client()`, or `create_subscription()` need the full ROS2 runtime environment — not just Python import paths. The typesupport shared libraries are loaded dynamically by the middleware and depend on `AMENT_PREFIX_PATH` + `LD_LIBRARY_PATH`.

## Why

The failure comes in 3 layers:
1. Missing source package in `sys.path` — easy to fix with `sys.path.append()`
2. Missing ROS2 message Python packages — still fixable with path patching
3. `rclpy.create_client()` fails with "Could not load library lib*__rosidl_typesupport_fastrtps_c.so" — this requires `LD_LIBRARY_PATH` and `AMENT_PREFIX_PATH`, which only `install/setup.bash` provides correctly

The robust pattern: detect missing environment → `source install/setup.bash` → `exec` yourself with the enriched environment.

## When it applies

Use this when:
- A standalone Python script (GUI, CLI, tool) imports `rclpy` and creates nodes/clients/subscribers
- Running with `python3 script.py` fails with library loading errors
- `sys.path` patching alone doesn't fix it
- The same script works when launched via `ros2 run`

## Counterexamples

Do not use this pattern for scripts that only import ROS2 message definitions without creating any ROS2 entities — those only need `sys.path`.

## Evidence Lineage

- project: `cuttofo`
- source refs: `.project-log/progress.md` (2026-06-07 19:56 CST, Tkinter GUI startup debugging)
- distillation run: `distillation-ledger/runs/2026-06-09T15-30-00-cuttofo.md`
