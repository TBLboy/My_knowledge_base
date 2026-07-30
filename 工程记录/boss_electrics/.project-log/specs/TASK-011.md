# Engineering Spec — TASK-011

## Objective

Provide the V1 pan-pour task with an isolated, launch-injected parameter contract and a ROS-independent SE(3) conversion module. The module converts a desired TCP pose expressed in robot-center frame `C` into the left-arm flange pose expressed in left-arm base frame `B`.

## Non-goals

- Do not implement or register `PanPourPolicy` in this task.
- Do not modify `robot_params.yaml`, `toolset.end`, any Driver code, MotionExecutor, or public ROS messages/actions.
- Do not choose numerical TCP, grasp-offset, fixed-pose, speed, or safety-limit values. All current values remain explicitly unconfigured placeholders.
- Do not implement perception-field adaptation, base-motion integration, or relative pour-trajectory replay.

## Related business logic and decisions

- `BL-GRASP-001`: grasp-point offset is evaluated in center frame `C` along the normalized handle PCA axis.
- `BL-PLATING-001`: grasp TCP and pan TCP are distinct task-owned kinematic parameters.
- `DEC-005`: business target points are computed in center frame `C`.
- `DEC-013`: Planner ultimately sends a flange target in left-arm base frame `B` through the existing interfaces.
- `DEC-014`: V1 TCP values are task-local Planner parameters; `toolset.end` remains identity.

## Coordinate contract

`T_A_B` means “pose of frame `B` expressed in frame `A`”, and maps coordinates by `p_A = T_A_B @ p_B`.

For a desired TCP target:

```text
T_C_F = T_C_TCP @ inverse(T_F_TCP)
T_B_F = T_B_C @ T_C_F
```

where:

- `T_C_TCP` is the requested grasp or pan TCP target in center frame `C`;
- `T_F_TCP` is the selected task-local fixed TCP extrinsic from flange `F` to TCP;
- `T_B_C` is the calibrated transform from center frame `C` to left-arm base frame `B`;
- `T_B_F` is the flange target emitted to the existing Planner → Executor path.

The geometry module must preserve this directionality in function and field names. It must use translation in metres and `xyz` roll/pitch/yaw in radians, matching the project calibration script.

## Parameter contract

Add `dexbot_bringup/config/pan_pour/pan_pour_params.yaml`, addressed to `task_planner_node`, with these groups:

- `pan_pour.configured`: explicit execution gate, initially `false`;
- `pan_pour.left_base_from_center.*`: calibrated `T_B_C`;
- `pan_pour.tcp_grasp.flange_to_tcp.*`: `T_F_TCP_grasp`;
- `pan_pour.tcp_pan.flange_to_tcp.*`: `T_F_TCP_pan`;
- `pan_pour.grasp_offset_m` and `pan_pour.pour_offset_center_m`;
- future fixed orientation and pose placeholders.

`TaskPlannerNode` declares and reads these parameters during startup, but only exposes an immutable task-local configuration object. A later PanPourPolicy must call `validate_for_execution()` before it creates a motion target. Therefore a placeholder configuration can never silently produce a real robot target.

## Affected components

- `dexbot_task_planner/entities/pan_pour_kinematics.py`: pure dataclasses, validation and SE(3) functions.
- `dexbot_task_planner/task_planner_node.py`: parameter declarations and configuration loading only.
- `dexbot_bringup/config/pan_pour/pan_pour_params.yaml`: task-local parameter template.
- `dexbot_bringup/launch/dexrob_full.launch.py`: inject the template into `task_planner_node`.
- focused pure Python tests under `dexbot_task_planner/test/`.

## Failure handling and observability

- Invalid vector dimensions, non-finite values, or a zero PCA vector raise `ValueError` in the pure module.
- `configured: false` causes `validate_for_execution()` to raise a clear error; it is not a usable default.
- Loading an unconfigured template must not prevent existing unrelated Planner tasks from starting.
- This task does not decide PanPourPolicy failure/recovery behavior.

## Verification matrix

| Case | Expected evidence |
| --- | --- |
| Identity extrinsics and `T_B_C` | TCP target is returned unchanged as flange target. |
| Non-identity grasp TCP | inverse TCP translation/rotation is applied before base conversion. |
| Non-identity pan TCP | same formula works independently from grasp TCP. |
| PCA offset | offset follows the normalized center-frame PCA direction. |
| Placeholder config | execution validation rejects it. |
| Invalid inputs | module rejects malformed transforms and zero PCA vectors. |
| Launch integration | `task_planner_node` receives `pan_pour_params.yaml`; no global robot config changes. |

Run focused tests, package build, and `git diff --check`. Real Driver and hardware verification remain out of scope.
