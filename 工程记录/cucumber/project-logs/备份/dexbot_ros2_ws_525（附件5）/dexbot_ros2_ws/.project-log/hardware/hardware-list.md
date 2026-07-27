# Hardware List

| Hardware | Model | Purpose | Control Method | IP / Bus | Notes |
|---|---|---|---|---|---|
| 左臂机械臂 | xCore (AR5-5 07L) | 按住黄瓜/豆腐 | SDK 直连 (XCoreLbotRobot) | 192.168.2.160 | IP 来自 cucumber_hold_params.yaml |
| 右臂机械臂 | xCore (AR5-5 07R) | 切割 | ROS services (xcore_controller_node) | 192.168.2.161 | IP 来自 dual_xcore_controllers launch |
| O6 手爪 (左) | O6 | 抓取/按住 | CAN (socketcan) | CAN0 | 通过 xcore_controller_node 或 SDK |
| O6 手爪 (右) | O6 | 抓取 | CAN (socketcan) | CAN1 | 通过 xcore_controller_node |
| RGB-D 相机 | RealSense D435 | 视觉感知 | USB 3.0 | USB | ROS2 realsense2_camera 驱动 |
