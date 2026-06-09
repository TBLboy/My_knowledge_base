---
id: kb-workflow-0002
title: ROS2 workspace environment isolation is not automatic
category: workflow
tags: [ros2, workspace, environment, colcon, build]
keywords: [install/setup.bash underlay pollution, AMENT_PREFIX_PATH contamination, workspace copy environment leak, clean build env -i, COLCON_PREFIX_PATH baked paths]
triggers:
  - workspace copied
  - workspace moved
  - install/setup.bash contains old paths
  - build environment contamination
  - underlay chain leaked
aliases:
  - ros2 workspace isolation
  - colcon build clean environment
  - setup.bash contamination
related:
  - "[[trace-runtime-consumers-before-tuning]]"
source_projects: [cuttofo]
source_refs:
  - cuttofo:.project-log/progress.md#2026-06-07-1435
confidence: high
applicability: Any ROS2 project that has been moved, copied, or shared across machines.
updated_at: 2026-06-09
---

## Rule

When a ROS2 workspace is cloned, moved, or duplicated, always rebuild in a clean shell. Never trust that `install/setup.bash` from a prior build is self-contained — it snapshots the underlay chain of its build environment.

## Why

After duplicating a ROS2 workspace, `colcon build` bakes the current shell's environment into `install/setup.bash`. Environment variables — `AMENT_PREFIX_PATH`, `COLCON_PREFIX_PATH`, `CMAKE_PREFIX_PATH`, `PYTHONPATH`, `LD_LIBRARY_PATH` — all inherit the build shell's underlay chain. The old workspace becomes a permanent hidden dependency. Fixing `~/.bashrc` is insufficient because the contamination is in the install artifacts themselves.

## When it applies

Use this when:
- A ROS2 workspace has been copied, moved, or renamed
- `install/setup.bash` references paths from a different or old workspace
- Workspace builds succeed but runtime behavior is wrong due to stale underlay paths
- Setting up a colleague's machine from a copied workspace

## How to fix

Rebuild the entire workspace in a clean environment:
```bash
env -i bash --rcfile <(echo 'source /opt/ros/humble/setup.bash')
colcon build --symlink-install
```

## Counterexamples

Do not rebuild if only source code changed without moving the workspace — incremental builds in the same environment are fine.

## Evidence Lineage

- project: `cuttofo`
- source refs: `.project-log/progress.md` (2026-06-07 14:35 CST, two rounds of hygiene cleanup)
- distillation run: `distillation-ledger/runs/2026-06-09T15-30-00-cuttofo.md`
