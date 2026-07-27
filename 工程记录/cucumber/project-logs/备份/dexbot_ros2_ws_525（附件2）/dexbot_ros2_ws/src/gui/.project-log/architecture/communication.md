# Communication

## ROS2 Services

| Service | Type | Direction | Namespace | Purpose |
|---------|------|-----------|-----------|---------|
| `/robot/get_state` | GetRobotState | GUI → Controller | arm_r / arm_l | Read joint positions + cartesian pose |
| `/robot/enable_arm` | EnableArm | GUI → Controller | arm_r / arm_l | Enable/disable arm power |
| `/robot/emergency_stop` | EmergencyStop | GUI → Controller | arm_r / arm_l | E-Stop / Recover |
| `/robot/clear_errors` | ClearErrors | GUI → Controller | arm_r / arm_l | Clear error state |
| `/robot/move_joints` | MoveJoints | GUI → Controller | arm_r / arm_l | Joint-space motion |
| `/robot/move_rt_cartesian_segment` | MoveRtCartesianSegment | GUI → Controller | arm_r / arm_l | Real-time Cartesian segment |
| `/robot/move_rt_cartesian_path` | MoveRtCartesianPath | GUI → Controller | arm_r / arm_l | Real-time Cartesian path |
| `/robot/start_rt_follow` | StartRtFollow | GUI → Controller | arm_r / arm_l | Start RT follow mode |
| `/robot/stop_rt_follow` | StopRtFollow | GUI → Controller | arm_r / arm_l | Stop RT follow mode |
| `/robot/stop_motion` | StopMotion | GUI → Controller | arm_r / arm_l | Stop current motion |
| `/robot/set_collision_detection` | SetCollisionDetection | GUI → Controller | arm_r / arm_l | Toggle collision detection |
| `/robot/optimize_joint_comfort` | OptimizeJointComfort | GUI → Controller | arm_r / arm_l | Joint comfort optimization |

## ROS2 Topics

| Topic | Type | Direction | Purpose |
|-------|------|-----------|---------|
| `/joint_states` | sensor_msgs/JointState | Controller → GUI | Joint position feedback (rad) |
| `/cart_pose` | geometry_msgs/PoseStamped | Controller → GUI | Cartesian pose feedback |

## CAN Bus

| Interface | Bitrate | Direction | Purpose |
|-----------|---------|-----------|---------|
| can0 | 1000000 | Bidirectional | Hand angle set/get, torque, polling |

## Web Communication

| Protocol | Endpoint | Direction | Purpose |
|----------|----------|-----------|---------|
| HTTP | /login, /register, /api/* | Browser ↔ Server | Authentication, user settings |
| WebSocket | /ws?token=... | Browser ↔ Worker | Real-time arm/hand control |
| JSON-RPC | stdin/stdout | Server ↔ Worker | Command relay to subprocess |

## Communication Flow

```
Tkinter Mode:
GUI → RosServiceBridge → ROS2 Services → xCore Controller → Arm
GUI → HandControlService → CAN → Hand

Web Mode:
Browser → HTTP → FastAPI → SQLite (auth/settings)
Browser → WebSocket → server.py → worker.py (subprocess)
worker.py → RosServiceBridge → ROS2 Services → Arm
worker.py → HandControlService → CAN → Hand
```
