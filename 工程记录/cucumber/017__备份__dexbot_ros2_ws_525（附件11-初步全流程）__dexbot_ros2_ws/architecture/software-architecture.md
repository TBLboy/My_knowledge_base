# Software Architecture

## 新 Skill 架构

```text
┌─────────────────────────────────────────────────────────────────┐
│                      orchestrator (ActionClient)                │
│  tofu_task_orchestrator.py — 按 YAML 定义顺序调用 skill        │
│  cucumber_workflow: hold → prepare → cut_round → release       │
└─────────────┬──────────────┬──────────────┬────────────────────┘
              │              │              │
     Action   │    Action    │    Action    │  Action
     Client   │    Client    │    Client    │  Client
              ▼              ▼              ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ cucumber_hold │ │    prepare    │ │  cut_round    │ │cucumber_hold  │
│ ActionServer  │ │ ActionServer  │ │ ActionServer  │ │ ActionServer  │
│ left arm SDK  │ │ right arm ROS │ │ right arm ROS │ │ left arm SDK  │
│ 直连          │ │ services      │ │ services      │ │ 直连          │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │                 │
        ▼                 ▼                 ▼                 ▼
  ┌────────────┐   ┌──────────────┐   ┌──────────────┐   ┌────────────┐
  │ 左臂 xCore │   │xcore_contrl  │   │xcore_contrl  │   │ 左臂 xCore │
  │  SDK 直连  │   │  node (右臂) │   │  node (右臂) │   │  SDK 直连  │
  └────────────┘   └──────────────┘   └──────────────┘   └────────────┘
```

## 视觉管线

```text
RealSense D435 → realsense2_camera → /camera/color/image_raw
                                   → /camera/aligned_depth_to_color/image_raw
                                   → /camera/color/camera_info
                                         │
                                         ▼
                                    sam3_detector_node
                                    (SAM3 图像分割)
                                         │
                                         ▼ /cuttofu/perception/detected_objects
                                    pose_estimator_node
                                    (6D 位姿估计)
                                         │
                                         ▼ /cuttofu/perception/objects_with_pose
                                    legacy_topic_relay (optional)
                                         │
                                         ▼ /objects_with_pose (legacy)
```

## ROS 节点部署方案

| 终端 | 节点 | 用途 |
|------|------|------|
| T1 | vision_bringup.launch.py | RealSense + SAM3 + pose_estimator + 可选 viewer |
| T2 | dual_xcore_controllers.launch.py | 双臂 xcore_controller_node（arm_l 和 arm_r 命名空间） |
| T3 | cucumber_workflow_execute.launch.py | orchestrator + skill servers |
