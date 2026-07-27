# SDK Mapping

| Hardware | Model | SDK / Driver | Version | API / Interface | Purpose | Notes |
|---|---|---|---|---|---|---|
| 右臂 | xCore AR5-5_07R-W4C1C1 | xCore Direct SDK | 未知 | TCP socket, move_rt_cartesian_path, move_joint | 7-DOF 右臂负责持刀切割 | IP: 192.168.2.161 |
| 左臂 | xCore AR5-5_07L-W4C1C1 | xCore Direct SDK | 未知 | TCP socket, move_rt_cartesian_path, move_joint | 7-DOF 左臂负责辅助操作 | IP: 192.168.2.160 |
| 灵巧手 | LinkerHand (O6) | 未知 | 未知 | CAN 总线 | 夹爪控制（取刀/握持/倒酱） | 通过 CAN 通信 |
| 相机 | RealSense D415/D435 | realsense2_camera | 未知 | ROS 2 topic | RGB-D 视觉输入 | /camera/color, /camera/aligned_depth_to_color |
| 视觉分割 | — | SAM3 (Segment Anything 3) | 未知 | text_prompt → detections | 物体分割与检测 | 通过 ROS topic 调用 |
| 位姿估计 | — | pose_estimator | 未知 | depth + detection → 6D pose | 物体 6D 位姿估计 | 内部节点 |
