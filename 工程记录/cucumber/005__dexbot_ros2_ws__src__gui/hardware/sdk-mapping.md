# SDK Mapping

| Hardware | Model | SDK / Driver | Version | API / Interface | Purpose | Notes |
|---|---|---|---|---|---|---|
| Robot Arm | xMateErProRobot / xMateRobot / xMateCr5Robot | xCore SDK (via LbotRobot facade) | v0.5.1 | `lbot_robot_xcore.py` | Arm motion control | 7-DOF, IP connection |
| Robot Arm | xMateErProRobot / xMateRobot / xMateCr5Robot | ROS2 services | Humble/Iron | `/robot/*` services | High-level arm operations | Namespace: arm_r / arm_l |
| CAN Hand | O6 | linkerbot SDK | - | `linkerbot.O6` | 6-DOF hand control | CAN interface |
| CAN Hand | L25 | linkerbot SDK | - | `linkerbot.L25` | 16-DOF hand control | CAN interface |
| CAN Hand | L20lite | linkerbot SDK | - | `linkerbot.L20lite` | 10-DOF hand control | CAN interface |
| CAN Bus | - | Linux can-utils | - | `ip link set can0` | CAN interface setup | Bitrate 1000000 |

## xCore SDK Details

- SDK path: `src/dexbot_bottom_layer/dexbot_bottom_layer/xcoresdk_python-v0.5.1.ar_12/Release/linux/`
- Module: `Release.linux.xCoreSDK_python`
- Robot classes: `xMateErProRobot`, `xMateRobot`, `xMateCr5Robot`
- Key methods: `setPowerState`, `setOperateMode`, `enableDrag`, `startRecordPath`, `stopRecordPath`, `saveRecordPath`, `cancelRecordPath`

## linkerbot Hand SDK Details

- Package: `linkerbot`
- Hand classes: `O6`, `L25`, `L20lite`
- Key interfaces: `hand.angle.set_angles()`, `hand.angle.get_blocking()`, `hand.torque.set_torques()`, `hand.start_polling()`, `hand.stop_polling()`
- SensorSource events: `SensorSource.ANGLE`

## ROS2 Service Mapping

| Service | Type | Purpose |
|---------|------|---------|
| `/robot/get_state` | GetRobotState | Read joint positions + cartesian pose |
| `/robot/enable_arm` | EnableArm | Enable/disable arm power |
| `/robot/emergency_stop` | EmergencyStop | E-Stop / Recover |
| `/robot/clear_errors` | ClearErrors | Clear error state |
| `/robot/move_joints` | MoveJoints | Joint-space motion |
| `/robot/move_rt_cartesian_segment` | MoveRtCartesianSegment | Real-time Cartesian segment |
| `/robot/move_rt_cartesian_path` | MoveRtCartesianPath | Real-time Cartesian path |
| `/robot/start_rt_follow` | StartRtFollow | Start RT follow mode |
| `/robot/stop_rt_follow` | StopRtFollow | Stop RT follow mode |
| `/robot/stop_motion` | StopMotion | Stop current motion |
| `/robot/set_collision_detection` | SetCollisionDetection | Toggle collision detection |
| `/robot/optimize_joint_comfort` | OptimizeJointComfort | Joint comfort optimization |
