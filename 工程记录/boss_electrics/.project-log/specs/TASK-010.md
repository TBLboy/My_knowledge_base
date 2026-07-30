# Engineering Spec — TASK-010

## Objective

Extend the private TaskPlanner scheduling contract so a dynamic Policy can explicitly report `WAIT`, `EXECUTE`, or `COMPLETE`. This enables V1 to wait for the base motion and post-move plate perception without sending a new arm action or terminating the task.

## Non-goals

- Do not modify `ExecuteTask.action`, `TaskTarget.msg`, RobotDriver services, or MotionExecutor.
- Do not implement the PanPourPolicy, perception-field adaptation, base client, or recovery policy in this task.
- Do not change the meaning of `None` returned by existing Policies.

## Related business logic

- `BL-PLATING-001`: the plate can become visible only after the base moves; the task must wait instead of treating that interval as success.
- `DEC-009`: one dynamic PanPourPolicy owns V1 phases.
- `DEC-015`: waiting and completion have separate internal semantics.

## Current behavior and evidence

`TaskPlannerNode._on_tick()` calls `_generate_goal_by_task_type()`. If that method returns `None`, the node immediately sets `RobotState.SUCCESS`, clears `_active_task_id`, and returns. `_generate_goal_by_task_type()` currently receives `None` from `self._policy.select_next_goal()` for both conceptual cases because `BasePolicy` only permits `PlannedStep | BimanualStep | None`.

Relevant code:

- `kitchen_robot_home/src/dexbot_task_planner/dexbot_task_planner/task_planner_node.py`
- `kitchen_robot_home/src/dexbot_task_planner/dexbot_task_planner/policy/base_policy.py`

## Target behavior

Introduce a private planner-domain result type, for example `PolicyDecision`, with three kinds:

| Kind | Payload | Planner effect |
| --- | --- | --- |
| `EXECUTE` | `PlannedStep` or `BimanualStep` | Reuse existing builder and `_send_execute_task_goal()` path. |
| `WAIT` | phase, reason, optional progress | Keep task and Policy alive; update phase; return from tick without sending an action. |
| `COMPLETE` | optional reason | Use existing completion cleanup path. |

The planner must adapt existing Policy output before routing: an existing `PlannedStep`/`BimanualStep` becomes `EXECUTE`; existing `None` becomes `COMPLETE`. Only a new dynamic Policy may return `PolicyDecision(WAIT, ...)`.

## Affected components

- New private result definition under `dexbot_task_planner/entities/` or `policy/`.
- `BasePolicy` return annotation and documentation.
- `TaskPlannerNode._generate_goal_by_task_type()` and `_on_tick()`.
- Focused tests under `dexbot_task_planner/test/`.

## Interfaces and schemas

No ROS interface changes. `StartTask`, `GetTaskStatus`, `ExecuteTask`, `TaskTarget`, and RobotDriver interfaces remain unchanged.

`GetTaskStatus.current_phase` continues to expose the waiting phase. The implementation should use deterministic phase strings such as `waiting_for_plate` and `waiting_for_base` so a caller can distinguish them from `task_completed`.

## State, concurrency and lifecycle

During `WAIT`:

- `_active_task_id`, `_active_task_type`, `_policy`, and `_goal_epoch` remain unchanged.
- `_pending_goal`, `_left_arm_busy`, and `_right_arm_busy` remain `False`.
- `WorldState.robot_status.state` remains `IDLE`; no Action is in flight.
- each 1-second tick reevaluates the Policy.

During `COMPLETE`, preserve the existing cleanup: set `SUCCESS`, phase `task_completed`, clear `_active_task_id`, and do not send another goal.

## Failure handling

This task does not introduce V1 business retry or recovery. It must avoid a new failure mode: malformed decision objects should be logged and move the planner to its existing `ERROR` state rather than being silently treated as completion. A Policy must not return `WAIT` after it has reported `COMPLETE`.

## Security and privacy

No new external input or control interface is added. The change reduces control risk by preventing synthetic "hold" arm commands during external waits.

## Observability

Log task id, decision kind, phase, and reason each time the decision changes. Do not log unchanged `WAIT` messages every tick at info level; use a transition check or debug-level logging to avoid log flooding.

## Compatibility, migration, rollout and rollback

All existing Policies remain compatible because their output is adapted unchanged. Roll back by removing only the dynamic-decision adapter and any dependent PanPourPolicy code; no deployed ROS interface or configuration migration is required.

## Verification matrix

| Case | Evidence |
| --- | --- |
| Existing Policy returns a step | Builder and Action send path is called once. |
| Existing Policy returns `None` | Existing success cleanup remains unchanged. |
| Dynamic Policy returns `WAIT` twice | No Action sent; active task and Policy remain; phase is queryable. |
| Dynamic Policy returns `WAIT` then `EXECUTE` | Exactly one Action is sent after the state changes. |
| Unknown/malformed decision | Planner exposes an error rather than success. |

Run focused Python tests and the package lint tests available in the workspace. ROS hardware execution is not required for TASK-010.

## Open questions and authority

This is a B-level internal compatibility decision recorded in `DEC-015`. It does not resolve the separate C-level bottom-base interface or the perception message contract. Those are explicit blockers for `TASK-012` and `TASK-014`.
