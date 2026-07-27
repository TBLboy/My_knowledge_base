# Threading Model

> Aligned with code as of 2026-05-17

## Overview

The system uses ROS2's built-in threading model with `rclpy.spin()` for each node. No explicit thread creation except for threading.Event synchronization in action servers.

## Node Threading

### Single-Threaded Spin (Default)

All nodes use `rclpy.spin(node)` which runs callbacks in a single thread:

| Node | Spin Type | Notes |
|------|-----------|-------|
| `phase_manager_node` | Single-threaded | 0.5Hz timer + subscription callbacks |
| `knife_prepare_action_server` | Single-threaded | Action callbacks + subscription callbacks |
| `knife_cut_action_server` | Single-threaded | Action callbacks (long-running) |
| `tofu_state_node` | Single-threaded | 10Hz timer + subscription callbacks |
| `sam3_detector_node` | Single-threaded | Perception pipeline |
| `pose_estimator_node` | Single-threaded | Perception pipeline |

### Callback Execution Order

Within each node, callbacks are executed sequentially in the spin thread:
1. Timer callbacks (if timer period elapsed)
2. Subscription callbacks (if message available)
3. Action server callbacks (goal, cancel, execute)

**Implication**: Long-running callbacks block other callbacks in the same node.

## Timer Callbacks

| Node | Timer | Period | Callback | Blocking Risk |
|------|-------|--------|----------|---------------|
| `phase_manager_node` | `_timer` | 0.5Hz (2s) | `_publish_state()` → `_tick_current_phase()` → `_advance_if_ready()` | Low: only checks conditions, publishes |
| `tofu_state_node` | `_timer` | 10Hz (0.1s) | `_publish_timer()` → health check + publish | Low: simple state machine |

## Subscription Callbacks

| Node | Subscription | Callback | Blocking Risk |
|------|--------------|----------|---------------|
| `phase_manager_node` | `/knife_grabbed` | `_on_knife_grabbed()` | None: simple flag set |
| `phase_manager_node` | `/tofu_state` | `_on_tofu_state()` | None: simple state copy |
| `phase_manager_node` | `/tofu_rotated` | `_on_tofu_rotated()` | None: simple flag set |
| `phase_manager_node` | `/phase_jump` | `_on_phase_jump()` | Low: phase transition |
| `tofu_state_node` | `/objects_with_pose` | `_on_objects()` | Medium: geometry computation, buffer management |
| `knife_prepare_action_server` | `/tofu_state` | `_on_tofu_state()` | None: simple state copy with lock |

## Action Server Threading

### knife_prepare_action_server

**Execute callback** (`_execute_callback`):
- Runs in action server's callback thread (same as spin thread)
- Long-running operation: IK solving, preview scoring, joint move, arrival verification
- **Duration**: Typically 5-15 seconds
- **Blocking**: Blocks other callbacks in the same node during execution

**Thread synchronization**:
```python
self._tofu_lock = threading.Lock()        # Protects _tofu_state
self._tofu_event = threading.Event()      # Signals tofu state arrival
```

- `_on_tofu_state()` acquires `_tofu_lock` to update `_tofu_state`, then sets `_tofu_event`
- `_wait_for_tofu_state()` waits on `_tofu_event` with timeout, checks `_tofu_state` under lock

### knife_cut_action_server

**Execute callback** (`_execute_callback`):
- Runs in action server's callback thread (same as spin thread)
- Long-running operation: cartesian path execution, user wait (Phase4/6)
- **Duration**: Phase3/5: ~10-20s, Phase4/6: indefinite (waits for user), Phase7: ~30-60s
- **Blocking**: Blocks other callbacks in the same node during execution

**Thread synchronization**:
```python
self._phase4_enter_event = Event()
self._phase6_enter_event = Event()
```

- Events are set after user confirms rotation (Enter or file touch)
- Not currently used for inter-thread signaling (single-threaded spin)

## Real-Time Constraints

| Constraint | Value | Notes |
|------------|-------|-------|
| State machine tick | 0.5Hz (2s period) | Must complete within 2s |
| Tofu state publish | 10Hz (0.1s period) | Must complete within 0.1s |
| Perception pipeline | ~5-10Hz | SAM3 detection + pose estimation |
| Action server response | < 120s timeout | Service timeout for cartesian path |
| Impedance mode | Real-time control | Requires low-latency xCore service response |

## Potential Blocking Scenarios

### 1. Phase4/6 User Wait (Indefinite Block)
```
knife_cut_action_server._execute_callback()
  → _execute_once()
    → wait for user (Enter or file touch)
    → BLOCKS until user signals
```
**Impact**: Action server cannot accept new goals during wait.
**Mitigation**: Separate node for Phase4/6 would allow concurrent operation.

### 2. Long Cartesian Path Execution
```
knife_cut_action_server._execute_callback()
  → arm.move_rt_cartesian_path()
    → rclpy.spin_until_future_complete(timeout_sec=120.0)
    → BLOCKS until path completes or timeout
```
**Impact**: Action server blocked during entire cut execution.
**Mitigation**: Acceptable for current use case (single cut sequence).

### 3. IK Solving (Phase2)
```
knife_prepare_action_server._execute_callback()
  → solve_prepare_candidates()
    → Multiple IK attempts (candidate_count × retry_count)
    → CPU-intensive, blocks spin thread
```
**Impact**: ~1-3 seconds of blocking during IK solving.
**Mitigation**: Acceptable for current use case.

## Thread Safety

### Shared State Protection

| Node | Shared State | Protection | Notes |
|------|--------------|------------|-------|
| `knife_prepare_action_server` | `_tofu_state` | `threading.Lock` | Updated by subscription, read by action callback |
| `tofu_state_node` | `_buffer`, `_latest` | None (single-threaded) | Only accessed in subscription + timer callbacks |
| `phase_manager_node` | `_ctx` | None (single-threaded) | Only accessed in timer + subscription callbacks |

### Cross-Node Communication

All inter-node communication is via ROS2 topics/actions/services:
- Thread-safe by ROS2 middleware
- No shared memory between nodes
- No explicit inter-node synchronization needed

## Executor Model

All nodes use the default `SingleThreadedExecutor` via `rclpy.spin()`.

**Not used**:
- `MultiThreadedExecutor`: Not needed for current workload
- `CallbackGroup`: Not used for callback isolation
- `AsyncioExecutor`: Not used

**Recommendation**: If Phase4/6 user wait becomes problematic, consider:
1. Moving user wait to a separate thread within the action server
2. Using `MultiThreadedExecutor` for the cut action server
3. Splitting Phase4/6 into a separate node
