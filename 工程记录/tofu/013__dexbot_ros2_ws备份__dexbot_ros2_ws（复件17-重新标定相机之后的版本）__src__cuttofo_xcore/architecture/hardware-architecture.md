# Hardware Architecture

> Aligned with code as of 2026-05-17

## Hardware List

| Component | Model | Quantity | Purpose | Notes |
|-----------|-------|----------|---------|-------|
| Robotic Arm | AR5-5_07R-W4C1C1 (right) | 1 | 7-DOF manipulator for knife control | URDF: `ar5_07r_w4c1c1_description` |
| Robotic Arm | AR5-5_07L-W4C1C1 (left) | 1 | 7-DOF manipulator (dual-arm setup, left not used for cutting) | URDF: `ar5_07l_w4c1c1_description` |
| Camera | Intel RealSense D435I | 1 | RGB-D perception for tofu detection and pose estimation | Eye-on-base, external fixed mount |
| End Effector | Custom knife | 1 | Cutting tool mounted on right arm flange | TCP offset calibrated |
| Controller | xCore controller | 1 | Robot arm motion control, impedance/position mode | ROS2 services interface |
| Calibration Board | ArUco/ChArUco | 1 | Hand-eye calibration | Used for T_base_cam computation |

## Robot Arm Specifications

### AR5-5_07R-W4C1C1 (Right Arm - Active)

| Parameter | Value | Notes |
|-----------|-------|-------|
| DOF | 7 | Redundant manipulator |
| Joint limits (raw) | J1: ±178°, J2: ±120°, J3: ±178°, J4: -60°~145°, J5: ±178°, J6: ±55°, J7: ±55° | From URDF |
| Joint limits (safe) | Raw - 15° margin | Enforced during IK solving |
| URDF tip link | `AR5-5_07R-W4C1C1_link7` | Flange frame, IK target |
| URDF base link | `AR5-5_07R-W4C1C1_base` | Robot base frame |
| q_home (deg) | [0, -30, 0, 60, 0, 45, 0] | Default seed for IK |
| Namespace | `/arm_r` | ROS2 service namespace |
| Coordinate frame | X→前(forward), Y↑上(up), Z→右(right) | Base frame convention |

### AR5-5_07L-W4C1C1 (Left Arm - Inactive)

| Parameter | Value | Notes |
|-----------|-------|-------|
| q_home (deg) | [0, 30, 0, -60, 0, -45, 0] | Mirror of right arm |
| Namespace | `/arm_l` | ROS2 service namespace |
| Coordinate frame | X→前(forward), Y↓下(down), Z←左(left) | Mirrored convention |
| tcp_offset | [0, 0, 0] | Not calibrated yet |

## TCP (Tool Center Point)

### Right Arm TCP Offset

```yaml
arms:
  right:
    tcp_offset: [0.008, 0.18, 0.262]  # [dx, dy, dz] in flange frame, meters
```

**Definition**: Translation from flange origin (link7) to knife tip center, expressed in flange coordinate frame.

**Properties**:
- Pure translation, no rotation: TCP frame axes = flange frame axes
- Fixed in flange frame: does not change with arm pose
- In base frame: `tcp_pos = flange_pos + R_flange @ tcp_offset` (rotates with flange)

**Calibration status**: Calibrated value `[0.008, 0.18, 0.262]` m

### TCP Offset Usage

| Location | Usage |
|----------|-------|
| `xcore_arm_adapter.get_pose()` | Returns TCP pose = flange + R @ tcp_offset |
| `xcore_arm_adapter.solve_ik()` | Converts TCP target → flange target: `flange = tcp - R @ tcp_offset` |
| `xcore_arm_adapter.compute_fk()` | Returns TCP pose from joint angles |
| `knife_prepare_action_server` | Computes flange target from vision TCP target |

## Camera Setup

### Intel RealSense D435I

| Parameter | Value | Notes |
|-----------|-------|-------|
| Mount | Eye-on-base (external fixed) | Not on robot arm |
| Color resolution | 1280x720 @ 30Hz | From launch config |
| Depth resolution | 848x480 @ 30Hz | From launch config |
| Point cloud | Enabled | Used for pose estimation |
| Depth alignment | Enabled (aligned_depth_to_color) | Depth registered to color frame |

### Hand-Eye Calibration

| Parameter | File | Notes |
|-----------|------|-------|
| Right arm | `config/calib_right/calibration_result_right.yaml` | Contains `T_base_cam` (4x4 matrix) |
| Left arm | `config/calib_left/calibration_result_left.yaml` | Contains `T_base_cam` (4x4 matrix) |

**T_base_cam**: Transformation from camera optical frame to robot base frame.

**Camera link TF computation** (in launch file):
```
T_world_camlink = T_base_cam @ T_optical_to_link
T_optical_to_link = [[0,-1,0,0], [0,0,-1,0], [1,0,0,0], [0,0,0,1]]
```

Default fallback (if calibration file missing):
```
tx=0.246382, ty=0.184995, tz=-0.173261
qx=-0.51890945, qy=0.47048780, qz=-0.37032558, qw=0.61010915
```

## Coordinate Frame Relationships

```text
world_display ──(static TF)──→ world ──(static TF)──→ camera_link
                                                         │
                                                    RealSense D435I
                                                         │
                                                    T_base_cam (calibration)
                                                         │
                                                    robot_base (AR5-5)
                                                         │
                                                    flange (link7)
                                                         │
                                                    tcp_offset → knife tip (TCP)
```

**Right arm base frame**:
- X+ → forward (away from robot base)
- Y+ → up (vertical)
- Z+ → right (when facing robot)

**Camera frame** (after calibration):
- Transformed to `camera_link` frame for point cloud processing
- Point clouds published in `camera_link` frame, transformed to `world` frame

## Hardware Constraints

| Constraint | Value | Notes |
|------------|-------|-------|
| Joint 6 limit | ±55° raw, ±40° safe | Limits knife tilt angle to ~40-45° from horizontal |
| Joint 7 limit | ±55° raw, ±40° safe | Affects wrist orientation flexibility |
| TCP offset max | Must keep flange within joint limits | Large offsets reduce reachable workspace |
| Camera FOV | D435I: 87°×58° (color), 87°×65° (depth) | Tofu must be within FOV for detection |
| Calibration accuracy | Hand-eye calibration error < 2mm | Affects cutting precision |
| Arm mounting | Right arm at world origin, left arm at [0, 0, -0.158] with 180° roll | From launch config |

## Wiring Notes

- Robot arm connected to xCore controller via proprietary interface
- xCore controller exposes ROS2 services under `/arm_r/robot/*`
- RealSense D435I connected via USB 3.0
- Camera fixed mount: position calibrated via hand-eye calibration procedure
- No external I/O wiring for tofu rotation (manual operation between phases)
