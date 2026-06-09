# Trigger: duplicated-geometry-recomputation

## Perception should own shared task geometry

- Path: `architecture/perception-owns-task-geometry.md`
- Rule: When several downstream modules depend on the same interpreted perception result, one layer should own that geometry contract and publish it once.
- Tags: robotics, perception, geometry, contract-design
- Triggers: duplicated geometry recomputation, prepare recomputes target pose, visualizer recomputes perception result, multiple modules derive different target geometry
- Updated: 2026-06-09
