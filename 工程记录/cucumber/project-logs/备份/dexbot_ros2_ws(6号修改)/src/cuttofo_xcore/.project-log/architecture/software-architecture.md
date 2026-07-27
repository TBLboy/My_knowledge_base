# Software Architecture

> Aligned with code as of 2026-05-17

## System Overview

Cuttofo is a ROS2-based tofu cutting demo using a 7-DOF AR5 robotic arm with a knife end-effector. The system performs 3 cuts with 2 manual tofu rotations between them, guided by vision (SAM3 + depth pose estimation).

## Node Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Perception Pipeline (dexbot_middle_layer)             │
│                                                                              │
│  RealSense D435I ──→ sam3_detector_node ──→ /objects_with_pose ──→          │
│                                              pose_estimator_node ──→        │
│                                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ /objects_with_pose (ObjectStateArray)
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Tofu State Processing (cuttofo_xcore)                 │
│                                                                              │
│  tofu_state_node ──→ /tofu_state (TofuState) @ 10Hz                         │
│    - Sliding window buffer (15 frames)                                       │
│    - Jump detection (0.05m threshold)                                        │
│    - Health state: TRACKING / STALE / LOST                                   │
│    - Left-arm mirroring support                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ /tofu_state (TofuState)
┌─────────────────────────────────────────────────────────────────────────────┐
│                        State Machine (cuttofo_xcore)                         │
│                                                                              │
│  phase_manager_node ──→ 7-phase state machine @ 0.5Hz                        │
│    Subscribes: /knife_grabbed (Bool), /tofu_state (TofuState),               │
│                /tofu_rotated (Bool), /phase_jump (String)                    │
│    Publishes:  /phase_state (String), /phase_status (String),                │
│                /cutting_start (Bool)                                         │
│    Action Clients: /move_to_prepare_pose, /execute_knife_cut                 │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌──────────────────────────┐    ┌──────────────────────────────────────────────┐
│  knife_prepare_action_   │    │  knife_cut_action_server                     │
│  server                  │    │                                              │
│                          │    │  /execute_knife_cut (ExecuteKnifeCut)         │
│  /move_to_prepare_pose   │    │  Handles: Phase3, Phase4, Phase5,            │
│  (MoveToPreparePose)     │    │           Phase6, Phase7                     │
│                          │    │  - Phase3/5: flange-Z cut, step base-Z       │
│  - Vision-guided prepare │    │  - Phase4/6: return-to-prepare + wait        │
│  - IK multi-candidate    │    │  - Phase7: vertical cut (base Y-),           │
│  - Cut preview scoring   │    │         mid-cycle push, tail push            │
│  - Joint move + verify   │    │  - Impedance→position fallback               │
│                          │    │  - Per-segment fallback (Phase7)             │
│  Uses: XcoreArmAdapter,  │    │                                              │
│        OfflineURDFKin,   │    │  Uses: XcoreArmAdapter,                      │
│        tofu_geometry     │    │        cut_trajectory                        │
└──────────────────────────┘    └──────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Robot Control Layer (dexbot_interfaces_low)           │
│                                                                              │
│  XcoreArmAdapter ──→ xCore services via ROS2 services:                       │
│    - /arm_r/robot/get_state (GetRobotState)                                  │
│    - /arm_r/robot/move_joints (MoveJoints)                                   │
│    - /arm_r/robot/move_rt_cartesian_path (MoveRtCartesianPath)               │
│    - /arm_r/robot/enable_arm (EnableArm)                                     │
│                                                                              │
│  TCP offset compensation in adapter layer:                                   │
│    - get_pose() returns TCP = flange + R @ tcp_offset                        │
│    - solve_ik() converts TCP target → flange target internally               │
│    - compute_fk() returns TCP pose                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Module Boundaries

### Layer 1: Perception (dexbot_middle_layer)
- **sam3_detector_node**: SAM3-based tofu segmentation, publishes detection masks
- **pose_estimator_node**: Depth + mask → 6D pose estimation, publishes ObjectStateArray
- **Responsibility**: Raw sensor → structured object pose
- **Boundary**: Outputs `/objects_with_pose`, inputs from RealSense topics

### Layer 2: State Processing (cuttofo_xcore)
- **tofu_state_node**: Sliding window filtering, health monitoring, geometry computation
- **tofu_geometry.py**: Corner extraction, edge direction, TCP target computation
- **config_loader.py**: Config loading, left-arm mirroring utilities
- **Responsibility**: Noisy pose → stable tofu state with health tracking
- **Boundary**: Inputs `/objects_with_pose`, outputs `/tofu_state`

### Layer 3: State Machine (cuttofo_xcore)
- **phase_manager_node**: 7-phase state machine, action client orchestration
- **Responsibility**: Phase sequencing, condition checking, error handling
- **Boundary**: Subscribes to state signals, publishes phase state, calls action servers

### Layer 4: Action Servers (cuttofo_xcore)
- **knife_prepare_action_server**: Vision-guided prepare pose (Phase2/Phase6)
- **knife_cut_action_server**: Cutting execution (Phase3/4/5/6/7)
- **Responsibility**: Complex motion sequences with IK, preview, fallback
- **Boundary**: Action goals from phase_manager, robot control via XcoreArmAdapter

### Layer 5: Robot Adapter (cuttofo_xcore)
- **xcore_arm_adapter.py**: ROS2 service client wrapper, TCP offset compensation, IK/FK
- **offline_urdf_kinematics.py**: URDF-based kinematics (offline, no robot connection needed)
- **cut_trajectory.py**: Waypoint generation for cutting trajectories
- **Responsibility**: High-level motion commands → low-level robot service calls
- **Boundary**: Inputs from action servers, outputs to xCore ROS2 services

### Layer 6: Robot Control (dexbot_interfaces_low)
- **xCore services**: GetRobotState, MoveJoints, MoveRtCartesianPath, EnableArm
- **Responsibility**: Direct robot controller communication
- **Boundary**: ROS2 services under `/arm_r/robot/*` or `/arm_l/robot/*`

## Key Design Patterns

### TCP Offset Abstraction
- TCP offset stored in config per arm (`arms.right.tcp_offset`, `arms.left.tcp_offset`)
- All FK/IK operations in `XcoreArmAdapter` automatically compensate
- Upper layers (action servers, vision pipeline) work with TCP coordinates directly
- `knife_prepare_action_server` computes flange target: `flange = tcp - R @ tcp_offset`

### Impedance → Position Fallback
- Cutting phases prefer impedance mode for compliance
- If impedance fails, retry same trajectory in position mode
- Phase7 uses per-segment fallback (not per-phase) to prevent retry-from-wrong-anchor bug
- Fallback is internal to `_move_segment()` in `knife_cut_action_server`

### Cut Preview Scoring
- Phase2 prepare generates IK candidates, then scores each via cut preview
- Preview simulates cutting trajectory in joint space
- Scoring evaluates: joint limit margin, path smoothness, distance from current pose
- Candidates violating safety margin are rejected before execution

### Left-Arm Mirroring
- Coordinate transform: `M = diag(1, -1, -1)` applied to positions, corners, edge directions
- Rotation matrices mirrored: `R_right = M @ R_left`
- Quaternions converted via rotation matrix mirroring
- Applied in `config_loader.py`, `tofu_state_node.py`, `knife_prepare_action_server.py`

### Phase4/6 User Wait Pattern
- Return to prepare anchor → move to wait joint pose → wait for user signal
- Wait signal: terminal Enter (if tty) OR file touch (`/tmp/cuttofo_phase4_continue`)
- After user signal: re-enter Phase2 with different config (`phase6_prepare` for Phase6)

## Data Flow Summary

```text
RealSense → SAM3 → pose_estimator → /objects_with_pose
                                              │
                                    tofu_state_node (buffer, filter, health)
                                              │
                                      /tofu_state (TofuState)
                                              │
                                phase_manager_node (state machine)
                                ┌───────────────┴───────────────┐
                                │                               │
                    /move_to_prepare_pose           /execute_knife_cut
                    (knife_prepare_action_server)   (knife_cut_action_server)
                                │                               │
                                └───────────────┬───────────────┘
                                                │
                                        XcoreArmAdapter
                                                │
                                        xCore ROS2 services
                                                │
                                        AR5-5 Robot Arm
```
