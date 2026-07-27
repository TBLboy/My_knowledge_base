# SDK Mapping

| Hardware | Model | SDK / Driver | Version | API / Interface | Purpose | Notes |
|---|---|---|---|---|---|---|
| 左臂 xCore | - | xcore_sdk_python (XCoreLbotRobot) | v0.5.1.ar_12 | SDK Python API | 直连 SDK 控制左臂 | dexbot_bottom_layer |
| 右臂 xCore | - | xcore_sdk_python (RobotController) | v0.5.1.ar_12 | ROS services | 通过 controller_node 控制 | dexbot_bottom_layer |
| O6 手爪 | O6 | linkerbot (O6 class) | - | Python API (angle.set_angles) | 手爪控制 | 通过 SDK 或 controller |
| RealSense D435 | D435 | realsense2_camera | ROS2 | ROS topics | RGB-D 图像采集 | 640x480x15 |
| SAM3 | SAM | sam3_detector_node | - | ROS topic | 图像分割 | dexbot_middle_layer |
| 位姿估计 | - | pose_estimator_node | - | ROS topic | 6D 位姿估计 | dexbot_middle_layer |
