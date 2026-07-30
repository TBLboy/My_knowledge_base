# Engineering Spec — TASK-013 (Offline Flange Delta Foundation)

## Scope

Implement only the pure, testable trajectory-asset boundary for V1 pan-pour replay. This slice does not create a ROS Action, MotionExecutor Skill, RobotDriver client, xCore connection, or hardware motion.

## Asset Contract

The parser accepts one YAML mapping with these required fields:

```yaml
schema_version: 1
motion_name: pan_pour_v1
trajectory_semantic: spatial_only
coordinate_system: flangeInBase
translation_unit: m
rotation_unit: rad
rpy_order: xyz
delta_reference: initial_flange
waypoint_count: 2
deltas:
  - index: 0
    delta: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  - index: 1
    delta: [dx, dy, dz, droll, dpitch, dyaw]
```

`delta[0]` must be identity (within numerical tolerance). Each `delta` is a pose6 vector `[x, y, z, roll, pitch, yaw]` in metres and radians. The runtime expansion contract is fixed as:

```text
T_base_flange_waypoint_i = T_base_flange_current @ Delta_initial_flange_i
```

This preserves the recorded motion in the current flange frame after the pan is rigidly grasped. It does not make any claim that the target Driver currently provides a verified flange pose or can safely execute the resulting path.

## Completion Boundary

The offline module is complete after schema validation and SE(3) composition have focused unit tests. `TASK-013` remains blocked until a real V1 trajectory is captured/versioned and the target Driver runtime proves its current-flange query and `MoveCartesian` semantics.
