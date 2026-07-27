# SDK Mapping

## Robot Arm

| Hardware | Model | SDK / Driver | Version | API / Interface | Purpose | Notes |
|---|---|---|---|---|---|---|
| Robot Arm | 珞石 xCore (右臂) | xCoreSDK_python | v0.5.1.ar_12 | `moveReset`, `moveAppend`, `moveStart`, `jointPos`, `MoveJCommand`, `MoveAbsJCommand` | NRT direct control | Binary at `dexbot_bottom_layer/dexbot_bottom_layer/xcoresdk_python-v0.5.1.ar_12/Release/linux/xCoreSDK_python.cpython-310-x86_64-linux-gnu.so` |
| Robot Arm | 珞石 xCore (右臂) | xCore NRT (内嵌) | Same as above | `_XCoreNrtDirect` class in `xcore_follow_tcp_chain_node_movej.py` | MoveJ Cartesian path | 内嵌在follow节点中，不经过LbotRobot模块 |

## Gripper

| Hardware | Model | SDK / Driver | Version | API / Interface | Purpose | Notes |
|---|---|---|---|---|---|---|
| Gripper | Linkerbot O6 | linkerbot-python-sdk | N/A | `angle.set_angles([0-100]*6)`, `close()` | 6-finger gripper control | CAN interface `can0`; arbitration_id: 0x27 (right), 0x28 (left) |

## Camera

| Hardware | Model | SDK / Driver | Version | API / Interface | Purpose | Notes |
|---|---|---|---|---|---|---|
| Camera | RealSense D435I | realsense2_camera (ROS2) | Humble | `/camera/camera/aligned_depth_to_color/image_raw`, `/camera/camera/color/image_raw`, `/camera/camera/color/camera_info` | RGB-D perception | Eye-to-hand mount; calibrated via hand-eye |

## Vision

| Hardware | Model | SDK / Driver | Version | API / Interface | Purpose | Notes |
|---|---|---|---|---|---|---|
| GPU | NVIDIA (CUDA) | SAM3 (Segment Anything 3) | N/A | `/sam3/text_prompt` → `/detected_objects` | Object segmentation | Model at `/home/tbl/Project/models/sam3`; supports Chinese prompts |
| Vision | - | pose_estimator_node | N/A | `/detected_objects` + depth → `/objects_with_pose` | 6D pose estimation | PCA-based OBB from mask + depth |

## Interface Protocols

| Protocol | Interface | Baud/Bitrate | Notes |
|---|---|---|---|
| CAN | can0 | 1000000 (1Mbps) | O6 gripper; must run `sudo ip link set can0 up type can bitrate 1000000` before use |
| TCP | 127.0.0.1:PORT | N/A | xCore NRT controller connection |
| ROS2 DDS | ROS_DOMAIN_ID=13 | N/A | All nodes must share same domain ID |

## SDK Path Notes

- **xCore SDK**: `_BUNDLED_XCORE_SDK_ROOT` has a path bug (`../../../../` missing one `../`), but fallback logic exists via `DEFAULT_XCORE_SDK_ROOT` and env var `DEXBOT_XCORE_SDK_ROOT`
- **Linkerbot SDK**: Path `../../../dexbot_bottom_layer/dexbot_bottom_layer/linkerbot-python-sdk/src` is correct in both workspaces
- **User's linkerbot SDK has better CAN error handling**: `SEND_TIMEOUT_S = 0.1` + retry logic for TX back-pressure (classmate's version lacks this)
