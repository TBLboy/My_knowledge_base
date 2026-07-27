# SDK Mapping

| Hardware | Model | SDK / Driver | Version | API / Interface | Purpose | Notes |
|----------|-------|-------------|---------|----------------|---------|-------|
| 左臂 | xCore AR5-5 07L-W4C1C1 | xCore SDK Python | v0.5.1.ar_12 | `XcoreDirectExecutor` (`move_joint`, `move_cartesian`, `set_rt_mode`) | 左臂运动控制（SDK 直连） | 路径: `dexbot_bottom_layer/xcoresdk_python-v0.5.1.ar_12` |
| 右臂 | xCore AR5-5 07R-W4C1C1 | xCore SDK Python | v0.5.1.ar_12 | `XcoreArmAdapter` (ROS service → SDK) | 右臂运动控制（ROS service 封装） | 通过 EnableArm/MoveJoints 等 service |
| 左灵巧手 | LinkerHand O6 | CAN raw frames | — | `can0` / `can1` socket CAN | 手指角度控制 | bitrate 1Mbps, 6 轴控制 |
| 右灵巧手 | LinkerHand O6 | CAN raw frames | — | `can0` / `can1` socket CAN | 手指角度控制 | same as left |
| 深度相机 | Intel RealSense D4xx | librealsense2 ROS | Humble | ROS topics | 彩色/深度图采集 | align_depth:=true |
| SAM3 | Meta SAM3 | `sam3_detector_node` | custom | ROS topic `/cuttofu/perception/detected_objects` | 图像分割 | HuggingFace 格式模型, GPU |
| 位姿估计 | — | `pose_estimator_node` | custom | ROS topic `/cuttofu/perception/objects_with_pose` | 6D 位姿计算 | 含手眼标定变换 |

## Hardware Interface Protocols

| Interface | Protocol | Details |
|-----------|----------|---------|
| 左臂控制 | TCP/IP + xCore SDK | 工控机 → 192.168.2.160: SDK 方法调用 |
| 右臂控制 | TCP/IP + xCore SDK | 工控机 → 192.168.2.161: SDK 方法调用 |
| LinkerHand O6 | CAN 2.0 | socketCAN, frame format: raw bytes per finger position |
| RealSense | USB3 | librealsense2 ROS 驱动 |
