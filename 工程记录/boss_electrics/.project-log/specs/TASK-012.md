# Engineering Spec — TASK-012 (Phase Skeleton)

## Objective

Implement and register one dynamic `PanPourPolicy` that owns V1 Planner phases and produces only existing left-arm `move_cartesian` and `gripper_action` goals. It must retain the task with explicit `WAIT` decisions whenever configuration, handle observation, base completion, plate observation, or the future pour-replay adapter is unavailable.

## Scope of this implementation slice

Implement the following deterministic Policy flow:

```text
waiting_for_configuration
→ waiting_for_handle_detection
→ move_to_grasp
→ close_gripper
→ move_to_pour_ready
→ waiting_for_base_position
→ waiting_for_plate_detection
→ move_to_pour_position
→ waiting_for_pour_replay_adapter
```

`move_to_grasp` uses `tcp_grasp`; `move_to_pour_ready` and `move_to_pour_position` use `tcp_pan`. All desired TCP targets are formed in center frame `C` and converted by `PanPourParameters` to left-arm base frame `B` flange targets before a `PlannedStep` is created.

## External boundaries intentionally left unconnected

- Existing `ScenePerception/ObjectDetection` has no contract for handle grasp point, PCA axis, plate center, source frame, or freshness. The Policy exposes explicit update methods for a future perception adapter; it does not reinterpret generic object poses as these fields.
- The base group has not supplied a ROS 2 action/service contract. The Policy exposes an explicit base-position completion update method; no base client is created.
- The relative flange replay Skill does not exist yet. After reaching the pour position, the Policy returns `WAIT(waiting_for_pour_replay_adapter)` rather than fabricating an unsupported `ExecuteTask.task_type`.
- Actual configuration remains `pan_pour.configured=false`; the launch-installed Policy must wait and must never send robot goals until calibration is approved.

## Policy state and execution contract

- `_phase` is the only V1 business-phase owner.
- `_active_step` stores only the one Action currently or most recently dispatched; it is not a precomputed full trajectory.
- Planner invokes `update_step_status()` from the normal Action result callback. Only `COMPLETED` transitions the Policy to the next phase.
- `FAILED` remains visible as the active step and follows the existing Planner retry/result behavior; no V1-specific retry or recovery is added.
- `clear()` resets phase and dispatched-step state but does not discard the latest externally supplied observations.

## Parameter additions

Add task-local placeholders only:

- `pan_pour.gripper.close_action_name`
- `pan_pour.pour_ready_tcp_pose_in_center.translation/rpy`

They remain empty/zero while `configured=false` and are validated together with the existing execution gate. They do not change `robot_params.yaml` or `toolset.end`.

## Verification

Focused unit tests must cover:

- wait with the launch placeholder configuration;
- wait without handle detection;
- `grasp_point_C + offset * normalize(pca_axis_C)` and `tcp_grasp` flange conversion;
- Action-result-driven phase transitions through close and pour-ready;
- base and plate waits without emitted goals;
- plate center plus `pour_offset_center_m` and `tcp_pan` flange conversion;
- wait at the absent replay-adapter boundary;
- Planner registration of task type `pan_pour`.

No real ROS node, perception model, base group API, RobotDriver, MotionExecutor, gripper action mapping, or hardware is verified in this task.
