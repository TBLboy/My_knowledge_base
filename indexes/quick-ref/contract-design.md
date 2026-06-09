# Quick Ref: contract-design

## Perception should own shared task geometry

- Rule: When several downstream modules depend on the same interpreted perception result, one layer should own that geometry contract and publish it once.
- Path: `architecture/perception-owns-task-geometry.md`
- Applicability: Robotics perception-to-action pipelines with shared geometry consumers.
