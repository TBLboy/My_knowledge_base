# Reusable Patterns

## Pattern: perception-owns-shared-task-geometry

- Scope: architecture
- Status: validated
- Rule: When several downstream modules depend on the same interpreted perception geometry, centralize ownership in the perception contract and make downstream modules consume it instead of recomputing local variants.
- When to use: Shared target pose, edge direction, or task geometry is consumed by prepare, visualization, or task execution modules.
- When not to use: Downstream modules need intentionally different derived representations rather than the same canonical task geometry.
- Evidence refs:
  - progress.md entries around 2026-06-07 12:43 CST and 2026-06-07 18:05 CST
  - business-logic/main.md
- Notes:
  - Candidate ID: cuttofo-0001

## Pattern: trace-runtime-consumers-before-tuning

- Scope: config
- Status: validated
- Rule: Do not assume a declared parameter controls behavior; trace where it is read, transformed, and finally consumed at runtime before treating it as a real tuning surface.
- When to use: Behavior depends on YAML config, action-goal profiles, launch-time wiring, or node parameters.
- When not to use: The code path is already directly verified and the parameter-to-behavior link is explicit.
- Evidence refs:
  - progress.md entries around 2026-06-07 17:35 CST, 2026-06-07 18:05 CST, and 2026-06-08 current CST
  - config/config-schema.md
- Notes:
  - Candidate ID: cuttofo-0002

## Pattern: single-purpose-launches-central-orchestration

- Scope: workflow
- Status: validated
- Rule: Keep subsystem launch files single-purpose and move full-stack composition into one explicit orchestration entry point.
- When to use: A ROS stack has separate layers for vision, perception, visualization, skill servers, and workflow execution.
- When not to use: A launch file is intentionally the top-level composition entry point and does not double as a subsystem module.
- Evidence refs:
  - progress.md entry around 2026-06-08 current CST
  - current-session.md
- Notes:
  - Candidate ID: cuttofo-0003
