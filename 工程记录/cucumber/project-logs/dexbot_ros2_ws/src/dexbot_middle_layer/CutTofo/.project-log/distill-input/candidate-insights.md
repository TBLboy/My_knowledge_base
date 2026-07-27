# Candidate Insights

## 2026-06-09 - Perception Owns Shared Task Geometry

- Type: architecture
- Status: validated
- Importance: high
- Reusable: yes
- Summary: Shared tofu target geometry should be produced once by perception and consumed downstream instead of being recomputed in prepare or visualization paths.
- Evidence refs:
  - progress.md entries around 2026-06-07 12:43 CST and 2026-06-07 18:05 CST
  - business-logic/main.md
- Why it may matter later: This prevents geometry drift across modules and makes perception-to-action contracts auditable.
- Next decision: copy to reusable-patterns

## 2026-06-09 - Runtime Consumer Tracing Beats Config Assumptions

- Type: config
- Status: validated
- Importance: high
- Reusable: yes
- Summary: Parameters should only be treated as effective controls after tracing the runtime consumer path through orchestration, profiles, and node-side reads.
- Evidence refs:
  - progress.md entries around 2026-06-07 17:35 CST, 2026-06-07 18:05 CST, and 2026-06-08 current CST
  - config/config-schema.md
- Why it may matter later: This sharply reduces wasted tuning work in layered ROS workflows.
- Next decision: copy to reusable-patterns

## 2026-06-09 - Central Orchestration Should Own Full Bringup Assembly

- Type: workflow
- Status: validated
- Importance: high
- Reusable: yes
- Summary: Subsystem launches should remain single-purpose, while full workflow composition belongs in a dedicated orchestration entry point.
- Evidence refs:
  - progress.md entry around 2026-06-08 current CST
  - current-session.md
- Why it may matter later: This keeps launch boundaries understandable and avoids hidden side effects across workflow bringup.
- Next decision: copy to reusable-patterns
