# Progress Log

## 2026-05-06 Local Time

- Objective: Record current working state; understand existing perception pipeline for arm grasping task
- Work completed:
  - Explored cuttofo_xcore package — pure motion control package, no perception/calibration/pose estimation code
  - Explored full dexbot_ros2_ws perception pipeline:
    - sam3_detector_node.py: SAM3 segmentation, publishes /detected_objects (ObjectStateArray with mask), supports image_topic param
    - vision_utils.py: PCA-based OBB 6D pose estimation from mask+depth (placeholder marked with warnings)
    - pose_estimator_node.py: ROS2 wrapper — subscribes /detected_objects + depth + camera_info, publishes /objects_with_pose
    - camera_viewer_node.py: OpenCV visualization with SAM3 mask overlay, supports image_topic param
    - calibration_result.yaml: T_base_cam transformation exists at /home/tbl/Project/dexbot_ros2_ws/src/config/
  - Verified running nodes: only /sam3_detector_node and /hand_monitor active
  - Verified topics: /camera/color/image_raw and /sam3/segmentation_result exist; depth topic absent (camera not running)
  - sam3_detector_node confirmed working with /camera/camera/color/image_raw
  - Fixed sam3_detector_node.py: added declare_parameter("image_topic", "/camera/color/image_raw") and parameterized create_subscription (previous session)
- Problems encountered:
  - RealSense camera NOT running — /camera/depth/image_raw absent
  - pose_estimator_node NOT running
  - Depth topic path likely /camera/camera/depth/image_raw (not /camera/depth/image_raw)
  - vision_utils.py PCA method is placeholder for production use
- Resolution: N/A — investigation only
- Verification: ros2 topic list, ros2 node list, python3 -m py_compile all passed
- Files changed: None (read-only investigation)
- Next steps:
  1. Confirm RealSense startup method (which launch file?)
  2. Fix depth topic path in pose_estimator_node if needed (/camera/camera/depth/image_raw)
  3. Start pose_estimator_node
  4. Test full pipeline: camera → SAM3 → /detected_objects → pose_estimator → /objects_with_pose
  5. Improve vision_utils.py PCA method for textured objects

## 2026-05-06 Local Time (Session 3)

- Objective: Complete full perception pipeline test — SAM3 segmentation + 6D pose estimation
- Work completed:
  - User copied calibration_result.yaml from desktop workspace: `/home/tbl/桌面/dexbot_ros2_ws/src/config/calibration_result.yaml` → `/home/tbl/Project/dexbot_ros2_ws/src/config/`
  - calibration_result.yaml contains T_base_cam transformation: translation=[0.125, -0.006, -0.076]m, rotation RPY=[-16.87°, 88.71°, 39.53°]
  - Desktop workspace (/) contains FULL hand-eye calibration toolchain:
    - hand_eye_calibration_node.py (cv2.calibrateRobotWorldHandEye based)
    - aruco_detector_node.py
    - hand_eye_static_tf_publisher.py
    - calibrate_tool_offset.py
    - calibrate_arm_geometry.py
    - calibration_manual_withUI.launch.py
    - 3 calibration_result.yaml files (28/15/30 samples with varying RMSE)
  - pose_estimator_node requires explicit calibration_file parameter — default paths (install/dexbot_bottom_layer/share/... and /home/kim/...) do not exist
- Problems encountered:
  - Desktop workspace is a SEPARATE copy from Project workspace — different src/ directories
  - Project workspace (/) lacked calibration_result.yaml initially
- Resolution: Copied calibration_result.yaml from desktop workspace to Project workspace src/config/
- Verification:
  - pose_estimator_node launched with params: depth_topic=/camera/camera/depth/image_rect_raw, camera_info_topic=/camera/camera/color/camera_info, calibration_file=/home/tbl/Project/dexbot_ros2_ws/src/config/calibration_result.yaml
  - ros2 topic echo /objects_with_pose --once: SUCCESS — tomato detected with 6D pose in Body_Base_link frame
  - Output verified: class_id=tomato, confidence=0.978, position=[0.279, 0.169, -0.004]m, size=[0.112, 0.056, 0.031]m
- Files changed:
  - `/home/tbl/Project/dexbot_ros2_ws/src/config/calibration_result.yaml` (copied from desktop workspace)
## 2026-05-06 Local Time (Session 4)

- Objective: Add 6D pose visualization overlay to camera_viewer_node; fix mask/depth resolution mismatch
- Work completed:
  1. **camera_viewer_node.py upgrade (FULL version)**:
     - Added ObjectStateArray subscription for /objects_with_pose
     - Added calibration_file parameter (loads T_base_cam, computes T_cam_base inverse)
     - Added auto camera_info subscription (infers from image_topic path)
     - Added _draw_pose_overlay(): draws yellow OBB bounding box (12 edges) + red principal axis arrow + size text
     - Added _project_points(): 3D(base)→2D(image) projection using T_cam_base + K matrix
     - Pose overlay priority: always drawn on top of SAM3/CALIBRATION/RAW images
     - pose_topic parameter (default: /objects_with_pose)
  2. **vision_utils.py mask/depth resolution mismatch fix**:
     - Error: "index 894 is out of bounds for axis 1 with size 848" — RGB 1280x720 vs Depth 848x480
     - Fix: Added auto-resize of mask to match depth image dimensions at get_pose_from_mask() entry
     - 3 lines of code: if shape mismatch, cv2.resize mask to match depth
- Problems encountered:
  - Mask (1280x720) and depth (848x480) resolution mismatch caused index out of bounds
- Resolution: Added cv2.resize in vision_utils.py get_pose_from_mask() entry
- Verification:
  - python3 -m py_compile on camera_viewer_node.py: pass
  - colcon build --packages-select dexbot_toolbox: pass
  - colcon build --packages-select dexbot_middle_layer: pass
- Files changed:
  - `src/dexbot_toolbox/dexbot_toolbox/visualization/camera_viewer_node.py`: full overlay implementation (~200 lines added)
  - `src/dexbot_middle_layer/dexbot_middle_layer/vision/pipeline/vision_utils.py`: mask resize fix
## 2026-05-06 Local Time (Session 5)

- Objective: Fix OBB pose jittering — yellow bounding box fluctuating even when tomato is stationary
- Root cause: RealSense depth noise + SAM3 mask boundary variation → PCA sensitive to point cloud distribution changes
- Observed jitter: position ±2mm, size ±6mm, quaternion angles fluctuating frame-to-frame
- Work completed:
  - Added EMA (Exponential Moving Average) smoothing to pose_estimator_node.py:
    - New parameter: `pose_smoothing_alpha` (default 0.4, range 0.01-1.0)
    - Position: EMA smoothing (alpha * raw + (1-alpha) * old)
    - Rotation: Spherical linear interpolation (slerp) for quaternion smoothing
    - Extents: EMA smoothing
    - Principal axis: recomputed from smoothed quaternion → rotation matrix
    - Per-object smoothing cache: `_smoothed_poses` dict keyed by obj_id
  - New methods: `_smooth_pose()` and `_slerp_quat()`
- Problems encountered:
  - OBB box jittering despite object being stationary (depth noise + mask boundary variation)
- Resolution: Implemented EMA exponential smoothing with slerp for quaternions
- Verification:
  - python3 -m py_compile on pose_estimator_node.py: pass
  - colcon build --packages-select dexbot_middle_layer: pass
- Files changed:
  - `src/dexbot_middle_layer/dexbot_middle_layer/pose_estimator_node.py`: added pose_smoothing_alpha param, _smooth_pose(), _slerp_quat(), EMA smoothing in synced_callback
- Next steps:
  1. Test pose_estimator_node with smoothing — verify OBB stability
  2. Test camera_viewer_node with calibration_file param — verify pose overlay display
  3. Integrate /objects_with_pose with cuttofo_xcore arm grasping control

## 2026-05-06 Local Time (Session 6)

- Objective: Clarify SAM3 text prompt usage for tofu detection
- Work completed:
  - Confirmed: SAM3 supports Chinese text prompts natively (Grounding DINO + SAM3)
  - "豆腐" (tofu) can be used as text_prompt for detecting tofu objects
  - Command example: `text_prompt:=豆腐` to segment tofu blocks
  - Confirmed red arrow = PCA principal axis (longest dimension direction of object)
  - SAM3 can detect: tomato, orange, cup, tofu, and any text-prompted object
- Problems encountered: None
- Resolution: N/A
- Files changed: None
- Next steps:
  1. Test SAM3 with text_prompt:=豆腐 to detect tofu objects
  2. Full pipeline: RealSense → SAM3(tofu) → /detected_objects → pose_estimator → /objects_with_pose
  3. Integrate with cuttofo_xcore arm grasping control

## 2026-05-06 Local Time (Session 7)

- Objective: Understand and document the complete tofu cutting workflow
- Work completed:
  - **Analyzed demo_cut_tofu.py** (1280+ lines): RT motion control for tofu cutting
  - **Documented cutting stages**:
    - Stage 0: 右手拿刀 (assumed complete)
    - Stage 1: 斜着切豆腐 (current focus)
    - Stage 2: 竖着切豆腐 (deferred)
  - **Key geometric relationship**: 法兰 Z轴正方向 ‖ 刀面 (线面平行)
  - **Oblique cutting mode**: `--cut-direction flange_z` — knife moves along flange +Z direction in base frame
  - **Vertical cutting mode**: `--cut-direction base_y` — knife moves along base +Y
  - **Core function**: `_flange_z_unit_in_base(mat16)` extracts flange Z-axis direction from pose matrix
  - **Cutting trajectory**: knife moves along flange Z-axis by `cut_move_mm` (default 25mm)
  - **Step increment**: each cycle moves down by `step_z_mm` (default -3mm)
  - **Critical insight**: knife pose is determined BEFORE running demo_cut_tofu.py; the script only controls cutting motion direction
- Problems encountered: None — analysis phase
- Resolution: N/A
- Files changed: None
- Key findings:
  - demo_cut_tofu.py does NOT calculate knife pose from tofu position
  - Knife pose must be set BEFORE running the script
  - Script assumes knife is already at correct position/orientation
  - Need to build: /objects_with_pose → knife pose calculation → arm movement → demo_cut_tofu.py execution
- Next steps:
  1. Design knife pose calculation algorithm from tofu 6D pose
  2. Determine oblique cutting angle (刀面与案板的面面角)
  3. Determine knife orientation relative to tofu principal axis
  4. Implement knife pose calculation node/script
  5. Integrate with arm control to move knife to calculated pose

## 2026-05-06 Local Time (Session 8)

- Objective: Clarify knife orientation constraint and analyze demo_adjust_knife_pose_xcore.py
- Work completed:
  - **Base坐标系方向澄清**:
    - base X = 左右 (横向)
    - base Y = 上下（数值方向，垂直方向）
    - **base Z = 前后（向前）— 刀脊方向**
  - **Knife orientation constraint (corrected)**:
    - 法兰盘 X轴正方向 · base Z轴正方向 = 1 (点积为1，同向)
    - 法兰 X轴（刀脊）‖ base Z轴（向前）
  - **Analyzed demo_adjust_knife_pose_xcore.py** (797 lines):
    - 完整实现了刀姿态计算的参考脚本
    - `build_target_rotation()` 函数从两个约束构建目标法兰姿态
    - 约束1: 线面角 — 法兰某轴与基准平面的夹角
    - 约束2: 轴平行 — 法兰某轴与base某轴平行
    - 默认参数:
      - `constraint_axis = "z"` (法兰 Z轴参与线面角)
      - `plane_angle_deg = 20.0` (可调)
      - `parallel_flange_axis = "x"` (法兰 X轴)
      - `parallel_base_axis = "z"` (‖ base Z)
    - 刀的位置计算未包含在此脚本中
  - **Tilt rotation axis**: 绕法兰 Y轴（刀刃方向）旋转
- Problems encountered: None
- Resolution: N/A
- Files changed: None
- Key findings:
  - `demo_adjust_knife_pose_xcore.py` 的 `build_target_rotation()` 可直接复用
  - 刀脊方向约束已确认: 法兰 X ‖ base Z
  - 倾斜角度绕法兰 Y轴（刀刃）旋转
  - 刀的位置计算待定
- Next steps:
  1. Design knife position calculation from tofu position + offset
  2. Confirm knife_tilt_angle range (0° ~ 90°)
  3. Implement knife pose calculation node/script
  4. Integrate with arm control to move knife to calculated pose

## 2026-05-06 Local Time (Session 9)

- Objective: Clarify knife position scope and 7-DOF arm redundancy consideration
- Work completed:
  - **Knife orientation status**: Fully determined
    - Spine direction: 法兰 X轴 ‖ base Z轴 (dot=1)
    - Tilt angle:绕法兰 Y轴（刀刃）旋转 0°~90°
    - Reference: `demo_adjust_knife_pose_xcore.py` build_target_rotation()
  - **Knife position**: Only remaining undetermined parameter for knife pose
    - Options: fixed height above tofu / tofu surface / edge / user-defined offset
    - Pending user decision
  - **7-DOF arm redundancy problem identified**:
    - Same flange pose → infinite joint angle solutions
    - Some solutions "natural", others "awkward"
    - Awkward poses cause: joint limit proximity, elbow odd direction, wrist singularities, IK failures
- Problems encountered: None
- Resolution: N/A
- Files changed: None
- Key findings:
  - Knife orientation is COMPLETE — spine direction + tilt angle are determined ✅
  - Knife position is the ONLY remaining parameter to determine
  - 7-DOF redundancy: IK solver must prefer "natural" joint configurations
  - Solution options:
    - Option A: Joint angle cost function optimization (optimal but complex)
    - Option C: Pre-set "good pose" as initial guess (simple and practical)
- Next steps:
  1. Confirm knife position calculation scheme (fixed height / surface / edge / user offset)
  2. Confirm 7-DOF arm IK preference scheme (A or C)
  3. Implement knife pose calculation node/script

## 2026-05-06 Local Time (Session 8)

- Objective: 实现法兰姿态约束下的IK求解，并在RViz中可视化（不连接真实机械臂）

- Work completed:
  1. **创建离线URDF FK模块** `offline_urdf_kinematics.py`:
     - 纯Python + numpy + scipy，不依赖xCore SDK/真实机器人/KDL/DH
     - `OfflineURDFKinematics`类：解析URDF XML，按关节链路做矩阵连乘得到末端位姿
     - 提供 `fk_matrix(q)` → 4x4齐次变换矩阵
     - 提供 `fk_pose_rotvec(q)` → [x,y,z,rx,ry,rz] (rotvec格式)
     - 提供 `fk_pose_euler_xyz(q)` → [x,y,z,rx,ry,rz] (欧拉角格式)

  2. **创建离线IK+RViz发布脚本** `demo_offline_ik_to_rviz.py`:
     - scipy `least_squares` 求解IK：20个随机种子 + 关节限位约束
     - 法兰姿态约束：x_flange‖base_X, z_flange⊥base_XZ平面
     - 发布 `/joint_states` 到RViz显示
     - 参数：`--x`, `--y`, `--z`, `--base-link`, `--tip-link`, `--no-rviz`, `--publish-once`, `--list-joints`

  3. **链路检查结果**:
     ```
     base_link: world (自动)
     tip_link: AR5-5_07R-W4C1C1_link_tcp (自动)
     chain: fixed(world->base) + joint_1~joint_7 + joint_tcp(fixed)
     ```
     显式使用机械臂坐标系时：`--base-link AR5-5_07R-W4C1C1_base`

   4. **离线IK验证** (目标 x=0.35, y=0.10, z=0.40, base=AR5-5_07R-W4C1C1_base):
      ```
      position error: 0.050 mm
      rotation error: 0.022 deg

      x_flange dot base_X = 0.99999995  (约束: = 1) ✅
      z_flange dot base_X = 0.00028      (约束: = 0) ✅
      z_flange dot base_Z = -0.00025     (约束: = 0) ✅
      z_flange dot base_Y = 0.99999993   (约束: = 1, Z轴指向+Y/下方) ✅
      ```

   5. **/joint_states发布测试**: `ros2 topic echo /joint_states --once` 成功收到7个关节角

- 法兰姿态约束（已确认）：
  - 法兰X轴（刀脊）‖ base +X轴（点积≈1）
  - 法兰Z轴（刀面法向量）指向 base +Y方向（= 垂直向下）
  - 旋转矩阵：Roll = -90° (Z轴指向+Y)

- Problems encountered:
  - 之前尝试xCore SDK compute_forward_kinematics(): 需要机器人网络连接 ❌
  - 之前尝试KDL URDF解析: URDF解析卡住 ❌
  - 之前尝试手写DH参数: DH参数不准确，误差187mm ❌
  - 最终方案: 纯XML解析URDF + 矩阵连乘，完全不依赖任何SDK ✅

- Files created:
  - `src/cuttofo_xcore/cuttofo_xcore/offline_urdf_kinematics.py`
  - `src/cuttofo_xcore/cuttofo_xcore/demo_offline_ik_to_rviz.py` (chmod +x)

- 使用方式:
  ```bash
  # 终端1：启动RViz（关闭GUI避免/joint_states冲突）
  ros2 launch ar5_07r_w4c1c1_description display.launch.py use_joint_gui:=false

  # 终端2：运行IK并发布到RViz
  python3 src/cuttofo_xcore/cuttofo_xcore/demo_offline_ik_to_rviz.py \
    --x 0.35 --y 0.10 --z 0.40 --base-link AR5-5_07R-W4C1C1_base
  ```

- Next steps:
  1. 将 `offline_urdf_kinematics.py` 接入 `demo_flange_pose_constraints.py`
  2. 替换掉 `robot.compute_forward_kinematics()` 为 `kin.fk_pose_euler_xyz(q)`
  3. 实现用户指定目标位置的IK求解（替代当前hardcoded值）
  4. 确认刀位置计算方案（fix height / surface / user offset）

## 2026-05-06 Local Time (Session 9)

- Objective: 给 `demo_offline_ik_to_rviz.py` 增加线面夹角参数

- Work completed:
  1. **修改 `build_target_rotation_from_constraints()`**:
     - 原来：固定 Roll=-90°（Z轴指向base +Y/下方）
     - 现在：参数化 `plane_angle_deg`（法兰Z轴与base XZ平面的线面角）
     - 新增 `in_plane_axis_sign` 控制倾斜方向（+Z或-Z）
     - 数学：z_flange = sin(angle)*base_Y + cos(angle)*base_Z，右手系确定y_flange

  2. **新增命令行参数**:
     - `--plane-angle-deg`：法兰Z轴与base XZ平面的线面角，默认90度
     - `--in-plane-axis-sign`：倾斜方向（-1.0或+1.0），默认+1.0（向+Z倾斜）

  3. **新增验证输出**:
     - `z_flange vs base XZ plane angle`：当前法兰Z轴与XZ平面的实际夹角
     - `target line-plane angle`：目标夹角

  4. **90度验证**（法兰Z轴垂直向下）：
     ```
     position error: 0.050 mm
     rotation error: 0.022 deg
     z_flange vs base XZ plane angle = 89.98°
     target line-plane angle = 90.0
     ```
     满足验收标准 ✅

  5. **45度验证**（法兰Z轴向+Z倾斜45°）：
     ```
     position error: 0.045 mm
     rotation error: 0.018 deg
     z_flange dot base_Y = 0.707
     z_flange dot base_Z = 0.707
     z_flange vs base XZ plane angle = 44.99°
     target line-plane angle = 45.0
     ```
     满足验收标准 ✅

- Files modified:
  - `src/cuttofo_xcore/cuttofo_xcore/demo_offline_ik_to_rviz.py`

- Next steps:
  1. 将此离线FK接入 `demo_flange_pose_constraints.py` 替换真实机器人FK
  2. 实现用户指定目标位置的IK求解

## 2026-05-06 Local Time (Session 10)

- Objective: 实现“面向后续切豆腐的准备姿态选择器”

- Work completed:
  1. **新增 `prepare_pose_selector.py`**：
     - 读取 `/joint_states` 获取 `current_joints`
     - 在无话题时使用 `q_home` 作为fallback
     - 构造 `target_prepare_pose`，保持既有法兰姿态构造不变
     - 使用URDF离线FK + scipy `least_squares` 生成多个 `q_prepare` 候选
     - 对每个候选执行一刀下切 preview rollout
     - 按 future cost 评分，选择 `best_q_prepare`
     - 发布 `best_q_prepare` 到 `/joint_states`

  2. **新增评分维度**：
     - `path_cost`: preview总关节运动
     - `jump_cost`: 单步最大跳变
   - `joint1_range_deg`: joint_1 稳定性
   - `limit_cost`: 接近限位的惩罚
   - `wrist_cost`: wrist过度扭转惩罚
   - `current_cost`: 与当前关节角的距离，仅低权重参考

   3. **关节角度格式化输出改进**：
      - 每个关节角度单独一行打印
      - 格式：`AR5-5_07R-W4C1C1_joint_N: XXX.XXX°`
      - 替换原有的numpy数组成员输出

   4. **重要修正**：
      - 15°安全余量是对URDF原始限位的硬约束
      - scoring中的 `min_margin_deg` 改为相对原始限位计算，避免将"safe bounds"重复计算成更严格的30°要求

   5. **验证结果**：
      - `python3 -m py_compile` ✅
      - 离线测试通过：
        - candidate=20, preview_steps=4, plane_angle=45
        - valid prepare candidates: 2
        - preview success: 2
        - best candidate:
          - position error: 0.000008 mm
          - rotation error: 0.000014°
          - min joint margin: 18.924°
          - x_flange dot base_X: 0.9999999999999807
          - actual plane angle: 45.000008°
      - 输出格式验证：
        ```
        q_prepare deg:
          AR5-5_07R-W4C1C1_joint_1: -36.712°
          AR5-5_07R-W4C1C1_joint_2: 88.536°
          ...
        ```

   6. **Files modified**:
      - `src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py`（关节角度格式化输出）

   7. **Next steps**:
      1. 用真实 `/joint_states` 话题替代当前fallback测试
      2. 根据实际切豆腐需求微调 future cost 权重
      3. 第二版再扩展 preview：prepare → down → up

## 2026-05-07 Local Time

- Objective: 为 RViz 机械臂模型添加末端执行器（LinkerHand O6 Right 灵巧手）

- Analysis completed:

  1. **LinkerHand O6 Right URDF 分析**：
     - 文件：`~/Project/dexbot_ros2_ws/linkerhand-urdf-main/o6/right/linkerhand_o6_right.urdf`
     - Robot name: `linker_o6_right_v1.0_urdf`
     - 根 link: `rh_hand_base_link`
     - Link 前缀: `rh_`
     - Joint 前缀: `rh_`
     - 总 joint 数: 16（5指 × 2-3 joint）
     - 无 transmissions，无 gazebo plugins
     - Mesh: `meshes/*.STL`（14个文件，相对路径）

  2. **关节结构**（5指 + 16 joints，含mimic）：
     | Finger | Joint chain |
     |--------|-------------|
     | Thumb  | rh_thumb_cmc_yaw → rh_thumb_cmc_pitch → rh_thumb_ip (mimic: 1.86×) |
     | Index  | rh_index_mcp_pitch → rh_index_dip (mimic: 0.89×) |
     | Middle | rh_middle_mcp_pitch → rh_middle_dip (mimic: 0.89×) |
     | Ring   | rh_ring_mcp_pitch → rh_ring_dip (mimic: 0.89×) |
     | Pinky  | rh_pinky_mcp_pitch → rh_pinky_dip (mimic: 0.89×) |

  3. **机械臂末端连接点**：
     - 右臂 URDF: `src/ar5_07r_w4c1c1_description/urdf/AR5-5_07R-W4C1C1.urdf`
     - 双臂 URDF: `src/ar5_dual_arm_bringup/urdf/AR5_dual_W4C1C1.urdf`
     - 末端 link: `AR5-5_07R-W4C1C1_link_tcp`
     - 前一级: `AR5-5_07R-W4C1C1_link7` + `joint_tcp` (fixed, xyz=0,0,0.097)

  4. **坐标系定义**（用户明确）：
     - **base 坐标系**:
       - Y 轴正方向: 垂直向下
       - Z 轴正方向: 水平向右
       - X 轴正方向: 垂直屏幕向外（向后）
     - **法兰坐标系**（关节归零时与 base 方向完全一致）:
       - Y+ 朝下
       - Z+ 水平向右（法兰超前方向）
       - X+ 向后
     - 法兰 Z 轴指向末端工具方向（径向朝外）
     - 法兰 X 轴指向刀夹/刀具朝前方向

  5. **目标安装姿态**（用户明确）：
     - 核心原则：**同轴挂载**，`rh_hand_base_link` 与 `AR5-5_07R-W4C1C1_link_tcp` 坐标系完全同向
     - `+X_hand → +X_tcp`
     - `+Y_hand → +Y_tcp`
     - `+Z_hand → +Z_tcp`
     - 名义安装旋转：**`rpy="0 0 0"`**（identity，无任何翻转）

  6. **手部 URDF 原始坐标系**：
     - 从 URDF joint 结构分析（finger proximal link 沿 +Z 延伸，thumb 沿 +X）：
       - 手指方向: +Z
       - 掌心法向: +Y（掌心朝上）
       - 拇指方向: +X
     - LinkerHand O6 原始模型手掌朝上（+Y），安装后手掌应朝下（-Y）
     - 但本任务以 link frame 同轴为准，不以 mesh 外观朝向为准
     - mesh 外观朝向属于后续调试项，不在本任务范围内

  7. **当前工程状态**：
     - `src/linkerhand_o6_r_description/` 已创建（见"已完成工作"）
     - `AR5_dual_W4C1C1.urdf` 已有 `xmlns:xacro="http://www.ros.org/wiki/xacro"`
     - `ar5_dual_arm_bringup/CMakeLists.txt` 已安装 `launch urdf rviz`，新增 `.urdf.xacro` 无需改 CMakeLists
     - `ar5_dual_arm_bringup/package.xml` 已增加 `exec_depend linkerhand_o6_r_description`
     - `dual_display.launch.py` 已改造为使用 `xacro.process_file()`，保留 `_set_fixed_joint_origin()` 逻辑

  8. **launch.py 改造要点**：
     - 不能简单替换成 `Command([xacro ...])`，会丢失现有的 `_set_fixed_joint_origin()` 逻辑
     - 推荐：引入 Python `xacro` 库，用 `xacro.process_file()` 展开 xacro，拿到 XML 字符串后再用 `ET.fromstring()` 解析
     - 保留原有 `_set_fixed_joint_origin()` 对 `fixed_left` / `fixed_right` 的修改逻辑
     - 保留 `use_joint_gui`、`joint_state_source`、RealSense、ArUco、hand-eye、world_display 等全部现有功能

  9. **fragment xacro XML 合法性方案**：
     - 不能有多个无 root 的顶层 `<link>` / `<joint>`，非法 XML
     - 推荐：创建 `<robot>` 根节点 + `<xacro:macro name="linkerhand_o6_right">` 包装内容
     - 主 xacro 中 `include` 后通过 macro 调用方式嵌入，不产生 nested robot
     - 文件示例：
       ```xml
       <?xml version="1.0"?>
       <robot xmlns:xacro="http://www.ros.org/wiki/xacro">
         <xacro:macro name="linkerhand_o6_right">
           <!-- 所有 link 和 joint 定义 -->
         </xacro:macro>
       </robot>
       ```
     - 主 xacro 中：
       ```xml
       <xacro:include filename="$(find linkerhand_o6_r_description)/urdf/linkerhand_o6_right.xacro"/>
       <xacro:linkerhand_o6_right/>
       ```

  10. **执行计划**：

     **步骤 1 - 备份**：
     ```
     cp src/ar5_dual_arm_bringup/urdf/AR5_dual_W4C1C1.urdf \
        src/ar5_dual_arm_bringup/urdf/AR5_dual_W4C1C1.urdf.bak
     cp src/ar5_dual_arm_bringup/launch/dual_display.launch.py \
        src/ar5_dual_arm_bringup/launch/dual_display.launch.py.bak
     ```

     **步骤 2 - 创建 package**：
     ```
     cd ~/Project/dexbot_ros2_ws/src
     ros2 pkg create linkerhand_o6_r_description --build-type ament_cmake
     mkdir -p src/linkerhand_o6_r_description/{urdf,meshes}
     ```

     **步骤 3 - 复制 hand 资源**：
     ```
     cp ~/Project/dexbot_ros2_ws/linkerhand-urdf-main/o6/right/linkerhand_o6_right.urdf \
        src/linkerhand_o6_r_description/urdf/
     cp ~/Project/dexbot_ros2_ws/linkerhand-urdf-main/o6/right/meshes/*.STL \
        src/linkerhand_o6_r_description/meshes/
     ```

     **步骤 4 - 修改 hand URDF mesh 路径**：
     ```
     sed -i 's#filename="meshes/#filename="package://linkerhand_o6_r_description/meshes/#g' \
       src/linkerhand_o6_r_description/urdf/linkerhand_o6_right.urdf
     ```

     **步骤 5 - 生成 xacro macro 文件**：
     - 从修改后的 hand URDF 生成 `linkerhand_o6_right.xacro`
     - 在 `<robot>` 根节点内用 `<xacro:macro name="linkerhand_o6_right">` 包装所有 link/joint
     - 删除原始 `<robot name="...">` 中的 name 属性，保留 root `<robot>` 用于 xacro 解析

     **步骤 6 - 配置 package.xml 和 CMakeLists.txt**：
     - `package.xml`: buildtool_depend ament_cmake, exec_depend xacro/robot_state_publisher/joint_state_publisher_gui/rviz2
     - `CMakeLists.txt`: install DIRECTORY urdf meshes to share/

     **步骤 7 - 复制主 URDF 为 xacro**：
     ```
     cp src/ar5_dual_arm_bringup/urdf/AR5_dual_W4C1C1.urdf \
        src/ar5_dual_arm_bringup/urdf/AR5_dual_W4C1C1.urdf.xacro
     ```

     **步骤 8 - 在主 xacro 中 include hand**：
     ```xml
     <xacro:include filename="$(find linkerhand_o6_r_description)/urdf/linkerhand_o6_right.xacro"/>
     <xacro:linkerhand_o6_right/>
     ```

     **步骤 9 - 在主 xacro 中添加安装 frame 参数和 joint**：
     ```xml
     <xacro:arg name="right_hand_mount_xyz" default="0 0 0"/>
     <xacro:arg name="right_hand_mount_roll" default="0"/>
     <xacro:arg name="right_hand_mount_pitch" default="0"/>
     <xacro:arg name="right_hand_mount_yaw" default="0"/>

     <link name="right_hand_mount_link"/>

     <joint name="right_tcp_to_hand_mount" type="fixed">
       <parent link="AR5-5_07R-W4C1C1_link_tcp"/>
       <child link="right_hand_mount_link"/>
       <origin
         xyz="$(arg right_hand_mount_xyz)"
         rpy="$(arg right_hand_mount_roll) $(arg right_hand_mount_pitch) $(arg right_hand_mount_yaw)"/>
     </joint>

     <joint name="right_arm_to_linkerhand_o6_right" type="fixed">
       <parent link="right_hand_mount_link"/>
       <child link="rh_hand_base_link"/>
       <origin xyz="0 0 0" rpy="0 0 0"/>
     </joint>
     ```

     **步骤 10 - 修改 dual_display.launch.py**：
     - `_setup()` 中引入 `xacro`
     - 用 `xacro.process_file()` 展开 `.urdf.xacro`
     - 展开后用 `ET.fromstring()` 解析，保留 `_set_fixed_joint_origin()` 逻辑
     - 添加 `right_hand_mount_*` launch 参数声明
     - 声明默认值全部为 0

     **步骤 11 - 更新 package.xml exec_depend**：
     - 在 `ar5_dual_arm_bringup/package.xml` 增加 `<exec_depend>linkerhand_o6_r_description</exec_depend>`

     **步骤 12 - 编译**：
     ```
     cd ~/Project/dexbot_ros2_ws
     colcon build --packages-select linkerhand_o6_r_description ar5_dual_arm_bringup
     source install/setup.bash
     ```

     **步骤 13 - 验证**：
     ```
     ros2 run xacro xacro \
       src/ar5_dual_arm_bringup/urdf/AR5_dual_W4C1C1.urdf.xacro \
       right_hand_mount_xyz:="0 0 0" \
       right_hand_mount_roll:=0 \
       right_hand_mount_pitch:=0 \
       right_hand_mount_yaw:=0 \
       > /tmp/ar5_dual_with_linkerhand.urdf

     grep -n "rh_hand_base_link" /tmp/ar5_dual_with_linkerhand.urdf
     grep -n "right_arm_to_linkerhand_o6_right" /tmp/ar5_dual_with_linkerhand.urdf
     grep -n "package://linkerhand_o6_r_description/meshes" /tmp/ar5_dual_with_linkerhand.urdf
     check_urdf /tmp/ar5_dual_with_linkerhand.urdf
     ```

     **步骤 14 - RViz 启动**：
     ```
     ros2 launch ar5_dual_arm_bringup dual_display.launch.py \
       right_hand_mount_xyz:="0 0 0" \
       right_hand_mount_roll:=0 \
       right_hand_mount_pitch:=0 \
       right_hand_mount_yaw:=0
     ```
     验证 TF：rh_hand_base_link 的 X(红)/Y(绿)/Z(蓝) 应与 TCP 同向

  11. **禁止事项**：
     - 不要使用 `rpy="0 0 3.1415926"` 或任何 180° 翻转
     - 不要把 `+Y_hand` 翻成 `-Y_tcp`
     - 不要修改 LinkerHand 内部各手指 joint 的 origin
     - 不要删除 mimic joint
     - 不要添加 transmission 或 gazebo plugin
     - 不要把 hand mesh 路径保留成相对路径 `meshes/xxx.STL`
     - 不要把完整 hand URDF 直接嵌套 include 到主 robot 里
     - 不要破坏原有双臂模型和 `joint_state_publisher_gui` 的启动逻辑
     - 不要直接替换 launch 中的 `robot_description` 为纯 `Command([xacro ...])`，会丢失 `_set_fixed_joint_origin()` 逻辑

  12. **核心原则**：
     - 本任务不是调姿态任务，而是同轴挂载任务
     - 右手根坐标系 `rh_hand_base_link` 与右臂 TCP 坐标系完全同向
     - 默认 `rpy` 必须为 `0 0 0`
     - mesh 外观朝向属于后续调试项，不在本任务范围内

## 已完成工作 (2026-05-07)

### 执行结果

| 检查项 | 结果 |
|--------|------|
| colcon build | ✅ 通过 |
| xacro 展开 | ✅ 通过 |
| check_urdf | ✅ 通过 |
| 无 nested robot | ✅ (仅1个 `<robot>` 标签) |
| `rh_hand_base_link` 存在 | ✅ (7处) |
| `right_arm_to_linkerhand_o6_right` 存在 | ✅ (1处) |
| `right_hand_mount_link` 存在 | ✅ (3处) |
| mesh 路径全部 `package://` | ✅ (24处) |
| 链路完整 | ✅ `link_tcp → right_hand_mount_link → rh_hand_base_link → fingers` |
| 默认 rpy | ✅ `0 0 0` (identity) |

### 新增文件

1. **`src/linkerhand_o6_r_description/`** (新 ROS2 package)
   - `package.xml` - 包描述，依赖 xacro/robot_state_publisher/joint_state_publisher_gui/rviz2
   - `CMakeLists.txt` - 安装 urdf/ 和 meshes/ 到 share/
   - `urdf/linkerhand_o6_right.urdf` - 原始 URDF（mesh 路径已改为 package://）
   - `urdf/linkerhand_o6_right.xacro` - xacro macro 文件（`<robot><xacro:macro name="linkerhand_o6_right">...</xacro:macro></robot>`）
   - `meshes/*.STL` - 14个 mesh 文件（从原始目录复制）

2. **`src/ar5_dual_arm_bringup/urdf/AR5_dual_W4C1C1.urdf.xacro`** (新 xacro)
   - 从原 URDF 复制
   - 新增 `<xacro:include>` 引用 hand xacro
   - 新增 `right_hand_mount_xyz/roll/pitch/yaw` 参数（默认值全部为 0）
   - 新增 `right_hand_mount_link` + `right_tcp_to_hand_mount` joint + `right_arm_to_linkerhand_o6_right` joint

3. **`src/ar5_dual_arm_bringup/launch/dual_display.launch.py`** (修改)
   - 新增 `import xacro`
   - `_setup()` 改用 `xacro.process_file()` 展开 URDF，保留 `_set_fixed_joint_origin()` 逻辑
   - 新增 4个 launch 参数声明：`right_hand_mount_xyz`（默认"0 0 0"）、`right_hand_mount_roll/pitch/yaw`（默认0）

4. **`src/ar5_dual_arm_bringup/package.xml`** (修改)
   - 新增 `<exec_depend>linkerhand_o6_r_description</exec_depend>`

### 备份文件

- `src/ar5_dual_arm_bringup/urdf/AR5_dual_W4C1C1.urdf.bak`
- `src/ar5_dual_arm_bringup/launch/dual_display.launch.py.bak`

### 安装链路（URDF tree 验证）

```
AR5-5_07R-W4C1C1_link_tcp
  └── right_hand_mount_link
        └── rh_hand_base_link
              ├── rh_thumb_metacarpals_base2 → ... → rh_thumb_distal
              ├── rh_index_proximal → rh_index_distal
              ├── rh_middle_proximal → rh_middle_distal
              ├── rh_ring_proximal → rh_ring_distal
              └── rh_pinky_proximal → rh_pinky_distal
```

### 安装 joint

| Joint | Parent | Child | xyz | rpy |
|-------|--------|-------|-----|-----|
| `right_tcp_to_hand_mount` | `AR5-5_07R-W4C1C1_link_tcp` | `right_hand_mount_link` | `$(arg right_hand_mount_xyz)` | `$(arg right_hand_mount_roll) $(arg right_hand_mount_pitch) $(arg right_hand_mount_yaw)` |
| `right_arm_to_linkerhand_o6_right` | `right_hand_mount_link` | `rh_hand_base_link` | `0 0 0` | `0 0 0` |

### 默认参数值

| 参数 | 默认值 |
|------|--------|
| `right_hand_mount_xyz` | `"0 0 0"` |
| `right_hand_mount_roll` | `0` |
| `right_hand_mount_pitch` | `0` |
| `right_hand_mount_yaw` | `0` |

### 启动命令

```bash
ros2 launch ar5_dual_arm_bringup dual_display.launch.py \
  use_joint_gui:=true \
  enable_realsense:=false \
  enable_aruco:=false \
  right_hand_mount_xyz:="0 0 0" \
  right_hand_mount_roll:=0 \
  right_hand_mount_pitch:=0 \
  right_hand_mount_yaw:=0
```

### RViz 显示状态确认（2026-05-07 验证）

**正确的启动命令**（如上），此命令下：
- 右臂 base 坐标系 Y 轴正方向**向上**
- 机械手手掌朝向操作者
- 与单臂版本 `display.launch.py` 显示状态一致

**关于 `world_rot_pitch` 参数**：
- 默认值 `world_rot_pitch=3.14159265`（π，180°）会让 RViz 视图里整个机器人翻转 180°
- 表现为：base Y+ 向下，但机械手变成手背朝操作者
- 解决方案：不使用 `world_rot_pitch` 参数（保持默认），或设为其他值
- **确认**：`world_rot_pitch` 改变的是 RViz 的显示视角（通过 `world_display → world` TF），不影响 URDF 模型本身

### 验证命令

```bash
# xacro 展开测试
source install/setup.bash
ros2 run xacro xacro \
  src/ar5_dual_arm_bringup/urdf/AR5_dual_W4C1C1.urdf.xacro \
  right_hand_mount_xyz:="0 0 0" \
  right_hand_mount_roll:=0 \
  right_hand_mount_pitch:=0 \
  right_hand_mount_yaw:=0 \
  > /tmp/ar5_dual_with_linkerhand.urdf

# 检查关键元素
grep -c "rh_hand_base_link" /tmp/ar5_dual_with_linkerhand.urdf  # 应为7
grep -c "right_arm_to_linkerhand_o6_right" /tmp/ar5_dual_with_linkerhand.urdf  # 应为1
grep -c "package://linkerhand_o6_r_description/meshes" /tmp/ar5_dual_with_linkerhand.urdf  # 应为24

# URDF 合法性检查
check_urdf /tmp/ar5_dual_with_linkerhand.urdf
```

- Next steps:
  1. ✅ RViz 启动验证完成：TF 同轴性确认正确
  2. ✅ 显示状态确认：base Y+ 向上，手掌朝操作者，与单臂版本一致
  3. 如需微调手部外观朝向，通过 `right_hand_mount_roll/pitch/yaw` 参数调整（名义默认值仍为 0）

## 2026-05-07 (续) - prepare_pose_selector.py publish topic 适配

### 问题描述

`prepare_pose_selector.py` 脚本在 RViz 双臂启动 (`use_joint_gui:=false`) 下无法控制机器人：

| 配置 | RSP 订阅 topic | 脚本发布 topic | 结果 |
|------|---------------|---------------|------|
| `use_joint_gui:=true` | `/joint_states`（无 remap） | `/joint_states` | ✅ 能收到 |
| `use_joint_gui:=false` | `/joint_states_remapped` | `/joint_states` | ❌ 收不到 |

原因：`use_joint_gui:=false` 时，`robot_state_publisher` 订阅 `/joint_states_remapped`（由 `dual_joint_state_merge.py` 合并左右臂关节状态后发布），而脚本硬编码发布到 `/joint_states`。

### 工程解决方案

修改 `prepare_pose_selector.py`，添加 `--publish-topic` CLI 参数：

**改动内容**（3处）：

1. `StaticJointStatePublisher.__init__`（第348行）：
   ```python
   def __init__(self, joint_names, q, publish_topic="/joint_states"):
   ```
   新增 `publish_topic` 参数，默认 `"/joint_states"`

2. `parse_args()`（第436行）：
   ```python
   parser.add_argument("--publish-topic", type=str, default="/joint_states",
                       help="Topic to publish joint states (default: /joint_states)")
   ```

3. `main()`（第533行）：
   ```python
   node = StaticJointStatePublisher(ACTIVE_JOINT_NAMES, best["q_prepare"], args.publish_topic)
   print(f"Publishing {args.publish_topic}. Open RViz RobotModel to see best_q_prepare.")
   ```

### 正确使用方式

```bash
# 启动双臂 RViz（GUI false，不抢占 topic）
ros2 launch ar5_dual_arm_bringup dual_display.launch.py \
  use_joint_gui:=false \
  enable_realsense:=false \
  enable_aruco:=false \
  right_hand_mount_xyz:="0 0 0" \
  right_hand_mount_roll:=0 \
  right_hand_mount_pitch:=0 \
  right_hand_mount_yaw:=0

# 运行脚本（发布到 RSP 实际订阅的 topic）
python3 src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py \
  --x 0.35 --y 0.10 --z 0.40 \
  --plane-angle-deg 30 \
  --candidate-count 240 \
  --preview-steps 15 \
  --publish-topic /joint_states_remapped
```

### 工作流程

1. `use_joint_gui:=false` → RSP 订阅 `/joint_states_remapped`
2. 脚本 `--publish-topic /joint_states_remapped` → 直接发布到 RSP 订阅的 topic
3. `dual_joint_state_merge.py` 监听 `/arm_r/joint_states` 和 `/arm_l/joint_states`，但无真实机器人时不发布
4. 脚本是 `/joint_states_remapped` 的唯一发布源，无 topic 冲突

### 修改文件

- `src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py`

## 2026-05-07 (续2) - base_y / cut_dir_base 坐标系适配

### 问题描述

`build_target_rotation_from_constraints` 函数按旧单臂版本（Y+ 向下）设计，但当前双臂版本 base Y+ 向上，导致求解后法兰 Z 轴朝上而非朝下。

### 根因

| 设置 | base Y+ 方向 | `base_y=[0,1,0]` 含义 |
|------|-------------|---------------------|
| 单臂（旧，废弃） | 向下 | [0,1,0] = 向下 ✅ |
| 双臂（当前） | 向上 | [0,1,0] = 向上 ❌ |

`plane_angle=30°` 时：`z_axis = sin(30°)*[0,1,0] + cos(30°)*[0,0,1] = [0, 0.5, 0.866]`（Z 朝上，错误）

### 修改内容（3处）

| 行号 | 位置 | 修改前 | 修改后 |
|------|------|--------|--------|
| 60 | `build_target_rotation_from_constraints` | `base_y = np.array([0.0, 1.0, 0.0])` | `base_y = np.array([0.0, -1.0, 0.0])` |
| 229 | `generate_cut_preview_poses` | `cut_dir_base = np.array([0.0, 1.0, 0.0])` | `cut_dir_base = np.array([0.0, -1.0, 0.0])` |
| 388 | `print_final_report` | `base_y = np.array([0.0, 1.0, 0.0])` | `base_y = np.array([0.0, -1.0, 0.0])` |

### 验证

`plane_angle=30°, sign=1.0` 修正后：
```
z_axis = sin(30°)*[0,-1,0] + cos(30°)*[0,0,1] = [0, -0.5, 0.866]
y_axis = cross([0,-0.5,0.866], [1,0,0]) = [0, 0.866, 0.5]
det = 1*(0.866*0.866 - (-0.5)*0.5) = 1.0 ✓
```
Z 轴向下偏右，行列式=1，有效旋转矩阵。

### 备份

- `src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py.bak`

## 2026-05-07 (续3) - 约束条件重写 (线面角 + TCP Y 约束)

### 问题描述

旧约束（`tcp_x · base_x = 1` + `tcp_z · base_y = sin(α)`）不适配双臂版本坐标系（Y+ 向上），导致法兰 Z 轴朝向错误。

### 新约束定义

| # | 约束 | 数学表达 |
|---|------|---------|
| 1 | TCP Y 轴与 Base X 轴同向 | `tcp_y · base_x = 1` → `tcp_y = [1, 0, 0]` |
| 2 | TCP Z 轴与 XZ 平面（水平面）夹角 = plane_angle | `|tcp_z · base_y| = sin(α)` |

### 旋转矩阵推导

```
tcp_y = [1, 0, 0]                             (约束1)
tcp_z = [0, -sin(α), cos(α)]                   (约束2, 向下倾斜)
tcp_x = tcp_y × tcp_z = [0, -cos(α), -sin(α)] (叉积正交)

R = [[0,        1,       0     ],
     [-cos(α),  0,      -sin(α)],
     [-sin(α),  0,       cos(α)]]

det = 1 ✓
```

### 修改内容（5处）

| 行号 | 位置 | 修改内容 |
|------|------|---------|
| 56-63 | `build_target_rotation_from_constraints` | 函数重写：移除 `in_plane_axis_sign` 参数，直接返回推导出的旋转矩阵 |
| 426 | argparse | 移除 `--in-plane-axis-sign` 参数 |
| 456 | `main()` 调用 | `args.in_plane_axis_sign` 移除 |
| 379-384 | `print_final_report` 变量 | `x_axis` → `y_axis`, `base_y` 改为 `[0,1,0]`, 新增 `actual_y_dot_base_x` |
| 410 | `print_final_report` 输出 | `x_flange dot base_X` → `tcp_y dot base_X` |

### 备份

- `src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py.bak2`

## 2026-05-07 (续4) - plane_angle=90° 不可解根因分析

### 问题现象

`plane_angle=90°` 在任何坐标下都报 `RuntimeError: target_prepare has no IK solution inside safe bounds`，且增大 candidate_count 或改变目标坐标均无法解决。

### 根因：关节6限位约束

从 URDF 读取的关节限位：

| Joint | Axis | Raw Limit | Safe Limit (±15°) |
|-------|------|-----------|-------------------|
| joint_6 | Y-axis | ±55° | ±40° |
| joint_7 | X-axis | ±55° | ±40° |

**几何关系**：TCP Z 轴与 link7 Z 轴同向（joint_tcp fixed, xyz=0,0,0.097, rpy=0,0,0）。joint_6 绕 Y 轴旋转决定刀具的上下倾斜。

| plane_angle | tcp_z | joint_6 需旋转 | safe(±40°) |
|:---|:---|:---|:---|
| 30° | [0, -0.5, 0.866] | ~30° | ✅ 可解 |
| 40° | [0, -0.64, 0.77] | ~40° | ✅ 边界可解 |
| 50° | [0, -0.77, 0.64] | ~50° | ❌ 超限 |
| 90° | [0, -1, 0] | ~90° | ❌ 绝对超限 |

**结论**：**plane_angle=90° 在任何位置下都不可解**，这不是位置问题，是关节物理能力问题。joint_6 的 ±40° 安全限位决定了最大可行 plane_angle ≈ 40-45°。

### 验证成功的参数

在 `--plane-angle-deg 40` 时求解成功，配合目标坐标 `--x 0.25 --y 0.0 --z 0.25`。

### 约束验证结果

| 约束 | 理论值 | 实际值 |
|------|--------|--------|
| `tcp_y · base_x` | 1.0 | ≈1.0 |
| `tcp_z` 与 XZ 平面夹角 | 40° | ≈40° |

### 运行命令

```bash
# 启动双臂 RViz
ros2 launch ar5_dual_arm_bringup dual_display.launch.py \
  use_joint_gui:=false \
  enable_realsense:=false \
  enable_aruco:=false \
  right_hand_mount_xyz:="0 0 0" \
  right_hand_mount_roll:=0 \
  right_hand_mount_pitch:=0 \
  right_hand_mount_yaw:=0

# 运行脚本
python3 src/cuttofo_xcore/cuttofo_xcore/prepare_pose_selector.py \
  --x 0.25 --y 0.0 --z 0.25 \
  --plane-angle-deg 40 \
  --candidate-count 240 \
  --preview-steps 15 \
  --publish-topic /joint_states_remapped
```

## 2026-05-07 (续5) - 灵巧手关节发布

### 问题描述

`prepare_pose_selector.py` 只发布 7 个臂关节到 `/joint_states_remapped`。手部 11 个 revolute 关节从未被更新，robot_state_publisher 将其保持在默认值 0，导致手指消失。

### 根因

- 脚本使用单臂 URDF，`ACTIVE_JOINT_NAMES` 仅 7 个臂关节
- 手部 11 个 revolute joints，5 个 mimic joints（RSP 自动计算），6 个非 mimic joints 需显式发布

### 手部关节结构

| 类别 | Joint | 类型 | 默认值 |
|------|-------|------|--------|
| 拇指 | `rh_thumb_cmc_yaw` | 非 mimic | 1.36 (max 张开) |
| 拇指 | `rh_thumb_cmc_pitch` | 非 mimic | 0.58 (max 张开) |
| 拇指 | `rh_thumb_ip` | mimic (1.86×) | RSP 自动计算 |
| 食指 | `rh_index_mcp_pitch` | 非 mimic | 0 (折叠) |
| 食指 | `rh_index_dip` | mimic (0.89×) | RSP 自动计算 |
| 中指 | `rh_middle_mcp_pitch` | 非 mimic | 0 (折叠) |
| 中指 | `rh_middle_dip` | mimic (0.89×) | RSP 自动计算 |
| 无名指 | `rh_ring_mcp_pitch` | 非 mimic | 0 (折叠) |
| 无名指 | `rh_ring_dip` | mimic (0.89×) | RSP 自动计算 |
| 小指 | `rh_pinky_mcp_pitch` | 非 mimic | 0 (折叠) |
| 小指 | `rh_pinky_dip` | mimic (0.89×) | RSP 自动计算 |

### 修改内容（2处）

1. **新增常量**（第47-63行）：`HAND_JOINT_NAMES`（6个非 mimic 关节名称）和 `HAND_JOINT_DEFAULT_POSITIONS`（拇指1.36/0.58 max 张开，四指 0 折叠）

2. **修改 `main()` 发布逻辑**（第545-548行）：
   - 合并臂关节和手关节：`list(ACTIVE_JOINT_NAMES) + HAND_JOINT_NAMES`
   - 合并臂关节位置和手关节默认位置：`np.concatenate([best["q_prepare"], HAND_JOINT_DEFAULT_POSITIONS])`
   - 打印信息更新为 `(7 arm + 6 hand joints)`

### 语法验证

- `python3 -m py_compile` ✅

---

## 下一阶段任务：视觉引导预备姿势（vision_guided_prepare_pose_task.md）

### 目标

在 `prepare_pose_selector.py` 中增加 ROS 视觉输入模式，订阅 `/objects_with_pose`，自动获取豆腐位置并计算 TCP 目标。

### 关键设计决策（已确认）

| 决策项 | 选择 |
|--------|------|
| 代码组织 | 单文件 + 模式切换（不拆分新节点） |
| 高度偏移 | `target_y = tofu_y + extY + 0.05`（上表面 + 5cm） |
| 位置来源 | 订阅 `/objects_with_pose`，取第一个匹配 class_id 的目标 |
| 向后兼容 | 无 `--ros-input` 时保持现有 CLI `--x --y --z` 模式 |

### 新增参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--ros-input` | false | 启用 ROS 视觉输入模式 |
| `--ros-input-topic` | `/objects_with_pose` | ObjectStateArray 订阅 topic |
| `--ros-input-class` | `"tofu"` | 目标类别过滤 |
| `--ros-input-timeout` | 5.0 | 等待目标检测超时 (s) |
| `--ros-input-offset-y` | 0.05 | 豆腐上表面以上安全间距 (m) |

### 预备姿势几何

```
tcp_x = tofu_x
tcp_y = tofu_y + extY + 0.05
tcp_z = tofu_z
```

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `prepare_pose_selector.py` | 新增 `VisionTargetReader` 类、5个 CLI 参数、`main()` ros-input 分支 |

### 详细设计文档

见 `.project-log/vision_guided_prepare_pose_task.md`

---

## 2026-05-07 (续6) - 豆腐上表面4顶点识别方案

### 目标

从 `/objects_with_pose` 已有数据（pose + orientation + extent）获取豆腐顶面4个顶点坐标，用于精确下刀位置计算。

### 已知事实

`get_pose_from_mask` 函数已在 base 坐标系下计算了全部8个 OBB 角点（`vision_utils.py` 第141-148行），但 `pose_estimator_node.py` 第291行调用后**只取用了 `pose_base` 和 `extents_3d`，角点被丢弃**，未发布到 `/objects_with_pose`。

base Y+ 向上，**上表面4个顶点 = 8个角点中 Y 坐标最大的4个**。

### 方案 A（推荐，不改感知管线）

从已发布的 `pose.position` + `pose.orientation` + `geometric_features[5:8]`（extent）重建8个角点：

```python
extent = [e0, e1, e2]   # 全尺寸 = proj_max - proj_min
half = np.array(extent) / 2.0
corners_local = np.array([
    [-half[0], -half[1], -half[2]],  [+half[0], -half[1], -half[2]],
    [+half[0], +half[1], -half[2]],  [-half[0], +half[1], -half[2]],
    [-half[0], -half[1], +half[2]],  [+half[0], -half[1], +half[2]],
    [+half[0], +half[1], +half[2]],  [-half[0], +half[1], +half[2]],
])
R = R.from_quat([ox, oy, oz, ow]).as_matrix()
corners_base = corners_local @ R.T + position  # 8×3 in base
top_vertices = corners_base[np.argsort(corners_base[:,1])[-4:]]
```

- **优点**：零改动感知管线，只改 `prepare_pose_selector.py`
- **前提**：`extent` 与 PCA 轴方向一致（✅ 代码已保证），且 extent 为全尺寸（✅ `proj_max - proj_min`）

### 方案 B（直接，需改感知管线）

修改 `pose_estimator_node.py`，在 ObjectState 消息中把 `bbox_3d` 角点也附加上去（如新增 `corners` 字段或追加到 `geometric_features` 后面）。

- **优点**：直接获取，省去重建
- **前提**：需修改消息定义或字段赋值

### 决策

待定（方案 A 优先）

---

## 2026-05-09 - 手眼标定知识整理

### 什么是手眼标定

手眼标定是求出**机械臂坐标系（base）**和**相机坐标系（cam）**之间相对位置关系的过程。有了 `T_base_cam`，相机中检测到的目标位置就能转换到机械臂坐标系下，用于运动规划。

### 两种类型

| 类型 | 相机位置 | 标定结果 | 适合场景 |
|------|---------|---------|---------|
| **Eye-in-Hand** | 相机固定在机械臂末端（跟着手臂动） | `T_tcp_cam`（TCP→相机） | 手持相机观察工作区 |
| **Eye-to-Hand** | 相机固定在基座/天花板（静止不动） | `T_base_cam`（基座→相机） | 相机俯视工作区 |

本项目采用 **Eye-to-Hand**：相机固定在头部俯视，ArUco 标定板贴在 TCP 上跟着机械臂动。

### 核心数学：AX=XB 方程

```
T_base_tcp_i @ T_tcp_marker = T_base_cam @ T_cam_marker_i
```

- `T_base_tcp_i`：第 i 个pose时，机械臂TCP在base坐标系下的位姿（FK正运动学，**已知**）
- `T_cam_marker_i`：第 i 个pose时，相机看到ArUco标定板在相机坐标系下的位姿（**已知**）
- `T_base_cam`：**要求的目标**（base→相机）
- `T_tcp_marker`：**要求的目标**（TCP→标定板，即工具偏移）

### 每个采样点需要采集的信息

| 数据 | 来源 | 是否已知 |
|------|------|---------|
| `T_base_tcp` | URDF FK 根据关节角度算出 | ✅ 已知 |
| `T_cam_marker` | ArUco相机检测(solvePnP) | ✅ 已知 |

用户只需要准备 ArUco 标定板并移动机械臂，节点自动完成采集和计算。

### OpenCV 标定算法（标准化工具）

```python
# hand_eye_calibration_node.py 第286-288行
methods = [
    cv2.CALIB_ROBOT_WORLD_HAND_EYE_SHAH,   # OpenCV 标准方法
    cv2.CALIB_ROBOT_WORLD_HAND_EYE_LI,     # OpenCV 标准方法
]
```

核心调用 `cv2.calibrateRobotWorldHandEye()`，这是 OpenCV 内置的标准算法，任何项目都可以直接用。

### 自己写的工程化部分

代码 Author: Bryntt, Date: 2026-02，自己写的工程化包装层包括：
- ROS 接口（Service/Topic 通信，键盘监听）
- 机械臂通信（xCore SDK，获取关节角度）
- 自动/手动 pose 生成与采样
- 稳定性检测（ArUco 抖动 < 0.5mm 才采）
- 离群点剔除（Leave-one-out + MAD）
- 加权 LM 优化 + SVD 投影到 SO(3)

### 标准化 vs 差异化

| ✅ 标准化（换硬件不用改） | 🔧 差异化（换硬件需要改） |
|--------------------------|-------------------------|
| AX=XB 数学原理 | 机械臂 SDK 通信（xCore → 其他品牌） |
| OpenCV 求解器 | 相机驱动（realsense2_camera → 其他） |
| ArUco 检测算法 | 相机内参标定文件 |
| 旋转变换数学（Rodrigues/quaternion/SO(3)） | URDF 模型和 TF 坐标名称 |
| 标定流程框架 | ArUco 标定板尺寸 |

### 项目中已有的标定工具链

| 文件 | 用途 |
|------|------|
| `hand_eye_calibration_node.py` | 核心标定节点，支持手动+自动模式 |
| `aruco_detector_node.py` | ArUco 检测，发布 `/aruco/pose` |
| `hand_eye_static_tf_publisher.py` | 读取标定结果，发布 base→camera 静态 TF |
| `calibration_manual_withUI.launch.py` | 完整标定系统启动文件 |
| `calibration_result.yaml` | 已有标定结果（28 samples, RMSE=4.62mm） |

### 执行命令（RealSense + 珞石机械臂）

```bash
ros2 launch dexbot_bringup calibration_manual_withUI.launch.py \
  robot_ip:=192.168.2.84 \
  arm_type:=right \
  launch_realsense:=true \
  enable_camera:=false \
  enable_viewer:=true \
  auto_start:=false \
  marker_length:=0.038 \
  output_file:=/home/tbl/Project/dexbot_ros2_ws/src/config/calibration_result_new.yaml
```

启动后在同一终端输入：
- `s` → 开始标定，开启拖动
- `Enter` → 记录当前 pose
- `d` → 删除最后一条
- `q` → 结束采点，计算结果

### 采点要求

- 最少 10 个，建议 20-30 个
- TCP 姿态要有多样性（旋转方向要有变化）
- ArUco 在相机中稳定时再按 Enter
- 标定板需刚性固定在 TCP 上

---

## 2026-05-11 - Lbot → xCore 迁移分析

### 目标

分析 Lbot Phase 2 框架迁移到 xCore 所需的技术细节，包括坐标系映射、欧拉角约定、ROS 架构差异。

### 核心发现

#### 坐标系映射

| | Lbot (LKRS73-I2) | xCore (AR5) |
|---|---|---|
| 上 | **Z+** | **Y+** |
| 前 | X+ | X+ |
| 左 | Y+ → **Y-** | Z+ → 右, **Z-** → 左 |

Lbot 的 Z 轴 = xCore 的 Y 轴，Lbot 的 Y 轴 = xCore 的 -Z 轴。

映射矩阵: `R_lbot_to_xcore = [[1,0,0],[0,0,-1],[0,1,0]]`

#### 欧拉角约定（关键发现！）

**xCore 使用 XYZ 内旋（= ZYX 外旋），整个代码库完全统一：**

| 证据 | 位置 |
|------|------|
| `xcore_controller_node.py` 所有 quaternion↔euler 转换使用 `from_euler("xyz")` / `as_euler("xyz")` | 多处 |
| `math_utils.py` 明确注释: "LBot API 使用 XYZ 内旋欧拉角（等价于 ZYX 外旋）" | 第 119-121 行 |
| `lbot_robot_xcore.py` `_pose6_to_matrix16`: R = Rz × Ry × Rx | 第 2527-2564 行 |
| 所有 demo 脚本 (`demo_cut_tofu_xcore*.py`) 使用相同的 `rpy_to_rot()` | 标准 RPY |

**LbotEuler 字段映射**:
- `LbotEuler.x` = roll (绕 X 轴)
- `LbotEuler.y` = pitch (绕 Y 轴)
- `LbotEuler.z` = yaw (绕 Z 轴)

**好消息**: xCore 不需要 Lbot 那种 `eul[2], eul[1], eul[0]` 的交换映射！scipy 的 `"xyz"` 直接对应 `LbotEuler(x=rx, y=ry, z=rz)`。

#### 旋转矩阵差异

Lbot (`tofu_geometry.py`):
```python
flange_x = [1, 0, 0]
flange_y = [0, sin(α), cos(α)]
flange_z = [0, -cos(α), sin(α)]
```

xCore (`prepare_pose_selector.py`):
```python
x_axis = [0, -cos(α), -sin(α)]
y_axis = [1, 0, 0]           # 刀脊 = base X
z_axis = [0, -sin(α), cos(α)]
```

#### ROS 控制架构差异

| | Lbot | xCore |
|---|---|---|
| 控制方式 | TCP SDK 直调 | ROS2 Service via `xcore_controller_node` |
| IK | SDK 内置 | URDF + scipy `least_squares` |
| 运动 | SDK 直调 | `/arm_r/robot/move_joints` 等 Service |
| RT 切削 | 无 | `/arm_r/robot/move_rt_cartesian_segment` |

### 输出文档

创建了完整的迁移方案文档：
- `.project-log/xcore_migration_plan.md` — 包含坐标系映射、欧拉角约定、模块迁移分类、文件映射表、实施步骤

### 实施优先级

```
P0: M1(tofu_geometry) → M2(xcore_arm_adapter) → M3(knife_prepare_action_server) → M6(launch)
P1: M4(tofu_state_node) → M5(tofu_cut_coordinator)
P2: 端到端测试
```

### 下一步

等待用户确认迁移方案后，开始按步骤实施。

---

## 2026-05-11 - M1-M6 迁移实施完成

### 工作内容

按照迁移方案 M1→M6 完成了所有代码实现。

### 新增文件

| 文件 | 行数 | 说明 |
|------|------|------|
| `cuttofo_xcore/cuttofo_xcore/tofu_geometry.py` | 113 | xCore Y↑ 坐标系适配版 |
| `cuttofo_xcore/cuttofo_xcore/xcore_arm_adapter.py` | 266 | ROS2 Service 封装 (GetRobotState, MoveJoints) |
| `cuttofo_xcore/cuttofo_xcore/knife_prepare_action_server.py` | 183 | xCore Action Server |
| `cuttofo_xcore/cuttofo_xcore/tofu_state_node.py` | 177 | 豆腐状态节点 xCore 版 |
| `cuttofo_xcore/cuttofo_xcore/tofu_cut_coordinator_node.py` | 141 | Phase 2 协调节点 xCore 版 |
| `cuttofo_xcore/launch/cuttofu_phase2.launch.py` | 157 | 一键启动文件 |

### 修改文件

| 文件 | 修改 |
|------|------|
| `setup.py` | 添加 3 个 console_scripts + launch data_files |
| `package.xml` | 添加依赖: cuttofo_lbot_interfaces, dexbot_interfaces_mid, sensor_msgs, std_msgs |

### 编译与验证

- `colcon build --packages-select cuttofo_xcore`: ✅ 通过
- `python3 -m py_compile`: 5 个文件全部 ✅
- `ros2 launch cuttofo_xcore cuttofu_phase2.launch.py --show-args`: ✅

### 旋转矩阵数学验证

| 测试项 | 结果 |
|--------|------|
| `build_target_rotation_from_constraints(40°)` | det=1.0, ortho err=1.6e-16 ✅ |
| `tcp_y = [1,0,0]` (刀脊 = base X) | ✅ |
| `z_axis vs XZ plane = 40°` | ✅ |
| `build_rotation_with_edge_dir(30°, XZ 45°)` | det=1.0, ortho err=2.2e-16 ✅ |
| `extract_top_corners` Y↑ 正确 | ✅ |

### 下一步

代码审查 (检查逻辑错误和潜在 bug)。

---

## 2026-05-11 - 全面代码审查 (Code Review)

### 发现问题

| # | 严重度 | 文件:行 | 问题 |
|---|--------|---------|------|
| 1 | 严重 | `xcore_arm_adapter.py:89,219` | `self._node.executor.spin_until_future_complete()` — executor 可能为 None，应改为 `rclpy.spin_until_future_complete(self._node, future)` |
| 2 | 严重 | `knife_prepare_action_server.py` | 缺少 `enable_arm` 步骤，机械臂不会运动 |
| 3 | 严重 | `xcore_arm_adapter.py:137` | IK 种子只有 ~23 个（20 random），`prepare_pose_selector.py` 用 80+ |
| 4 | 中等 | `xcore_arm_adapter.py:33-41` | 死代码 `_JOINT_BOUNDS_RAD`，未被使用 |
| 5 | 中等 | `xcore_arm_adapter.py:5` | 未使用导入 `from pathlib import Path` |
| 6 | 轻微 | `xcore_arm_adapter.py:208-211` | `accel` 参数定义但未传入 service request |
| 7 | 轻微 | `tofu_geometry.py:67` | 接近方向 `l_raw[2] > 0` 依赖物理布置，需实机验证 |

### 修复内容

| # | 文件 | 修改 |
|---|------|------|
| 1 | `xcore_arm_adapter.py` | `self._node.executor.spin_until_future_complete()` → `rclpy.spin_until_future_complete(self._node, future)` (3处) |
| 2 | `xcore_arm_adapter.py` + `action_server.py` | 新增 `enable_arm()` 方法 (EnableArm Service) + action server 中调用 |
| 3 | `xcore_arm_adapter.py` | IK 种子数从 `num_retries`(20) 改为 `max(num_retries, 80)` |
| 4 | `xcore_arm_adapter.py` | 移除死代码 `_JOINT_BOUNDS_RAD` |
| 5 | `xcore_arm_adapter.py` | 移除未使用导入 `Path`，添加 `import rclpy` + `EnableArm` |
| 6 | `xcore_arm_adapter.py` + `action_server.py` + `launch.py` | 移除 `accel` 参数（xCore controller 内部自动计算） |
| 7 | `tofu_geometry.py` | 添加注释说明接近方向依赖物理布置 |

编译: `colcon build` ✅ | py_compile: 全部 ✅

---

## 2026-05-11 - 双臂支持 + 配置文件架构

### 新增文件

| 文件 | 说明 |
|------|------|
| `config/cuttofo_config.yaml` | 项目主配置文件（唯一的切换点） |
| `cuttofo_xcore/config_loader.py` | 配置加载 + 左臂镜像变换工具 |

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `tofu_state_node.py` | 从 config 读取 arm_side，左臂时应用 T_mirror=diag([1,-1,-1]) 边界变换 |
| `xcore_arm_adapter.py` | 从 config 读取 URDF 路径、关节名、base_link、tip_link、q_home |
| `knife_prepare_action_server.py` | 从 config 读取 arm_side，左臂时对旋转矩阵做镜像变换 |
| `launch/cuttofu_phase2.launch.py` | 新增 `--arm` 和 `--config_file` launch 参数 |
| `package.xml` | 添加 `python3-yaml` 依赖 |
| `setup.py` | 添加 `config/` 目录安装 |

### 双臂切换方式

```bash
# 方式 1: 修改配置文件
vim config/cuttofo_config.yaml  # active_arm: "left"

# 方式 2: 启动时覆盖
ros2 launch cuttofo_xcore cuttofu_phase2.launch.py arm:=left

# 方式 3: 环境变量
CUTTOFO_ACTIVE_ARM=left ros2 launch cuttofo_xcore cuttofu_phase2.launch.py
```

### 左臂坐标系适配原理

```
左臂 base: X→(前) Y↓(下) Z←(左)
右臂 base: X→(前) Y↑(上) Z→(右)

关系: T_mirror = diag([1, -1, -1])  (绕 X 轴 180°)

适配策略: tofu_geometry.py 完全不动
  1. tofu_state_node: 感知数据(左臂) → T_mirror → 几何计算(右臂惯例) → T_mirror → 输出(左臂)
  2. knife_prepare_action_server: R_target(右臂) → T_mirror@R → IK(左臂 URDF) → joints

验证结果:
  - 左臂旋转矩阵: det=1.0, y_axis=[1,0,0] ✅
  - plane_angle=40°: z_axis=[0,0.643,-0.766], 夹角=40° ✅
  - 镜像往返: pos/rot/corners 全部恢复了 ✅

---

## 2026-05-11 - 双臂支持 + 代码审查

### 第二轮审查发现

| # | 严重度 | 文件:行 | 问题 |
|---|--------|---------|------|
| 1 | **Bug** | `tofu_state_node.py:112` | `pos = mirror_pos(pos)` 将感知的 LEFT 惯例 pos 错误翻成 RIGHT 惯例，导致 EMA 平滑混合两个惯例 |
| 2 | 轻微 | `config_loader.py:4` | 未使用导入 `from pathlib import Path` |
| 3 | 轻微 | `knife_prepare_action_server.py:22` | 未使用导入 `mirror_pos` |

### 修复

| # | 文件 | 修改 |
|---|------|------|
| 1 | `tofu_state_node.py` | 删除 `pos = mirror_pos(pos)` 行 |
| 2 | `config_loader.py` | 删除 `from pathlib import Path` |
| 3 | `knife_prepare_action_server.py` | 删除 `mirror_pos` 导入 |

### 其他验证项 (全部通过)

- `xcore_arm_adapter.py`: config 驱动的 URDF/关节名切换 ✅
- `knife_prepare_action_server.py`: `mirror_rotmat` 在 IK 前正确应用 ✅
- `tofu_geometry.py`: **零改动**，稳定性确认 ✅
- `config_loader.py`: 环境变量 `CUTTOFO_ACTIVE_ARM` / `CUTTOFO_CONFIG` 覆盖逻辑 ✅
- launch 文件: env var 注入节点 ✅
- `colcon build` ✅ | `py_compile` 6/6 ✅
- 集成测试: config 加载、镜像数学、往返一致性 ✅

### 当前项目文件清单

```
cuttofo_xcore/
├── config/
│   └── cuttofo_config.yaml              ← 唯一配置切换点
├── launch/
│   └── cuttofu_phase2.launch.py
├── cuttofo_xcore/
│   ├── __init__.py
│   ├── config_loader.py                 ← 新增: 配置加载+镜像变换
│   ├── tofu_geometry.py                 ← xCore Y↑ 适配 (零改动实现双臂)
│   ├── tofu_state_node.py               ← xCore 版 (含左臂边界变换)
│   ├── xcore_arm_adapter.py             ← ROS2 Service 封装 (config 驱动)
│   ├── knife_prepare_action_server.py   ← Action Server (config 驱动+镜像)
│   ├── tofu_cut_coordinator_node.py     ← 协调节点
│   ├── offline_urdf_kinematics.py       ← 保留: FK 引擎
│   ├── prepare_pose_selector.py         ← 保留: 离线调试
│   └── demo_*.py                        ← 保留: 参考 demo
├── package.xml
├── setup.py
└── .project-log/
```

---

## 2026-05-12 — 新增 execute_prepare_pose 实机执行脚本

### 目标

将 `prepare_pose_selector.py` 的离线 IK 寻优逻辑迁移到真实 xCore 机械臂上执行，支持指定/保持 TCP 位置 + 平面角约束 + 切预览打分 + 自动运动。

### 新增文件

| 文件 | 说明 |
|------|------|
| `cuttofo_xcore/execute_prepare_pose.py` | 实机执行脚本：连 xCore → IK 多候选求解 → 预览评分 → 自动运动 |

### 修改文件

| 文件 | 改动 |
|------|------|
| `setup.py` | 新增 `execute_prepare_pose` entry_point |

### 功能

- `--x --y --z` 指定目标位置；不传则保持当前 TCP 位置（只调姿态）
- `--plane-angle-deg` 平面角约束（默认 40°）
- 完整复用 `prepare_pose_selector.py` 的 IK 多候选 + 切预览打分逻辑
- `--dry-run` 预览而不实际运动
- `--arm-side left\|right` 支持左右臂（默认 right）

### 前置条件

```
Terminal 1: xcore_controller_node
ros2 run dexbot_bottom_layer xcore_controller_node \
  --ros-args -p robot_ip:=192.168.2.161 -p arm_side:=right

Terminal 2: execute_prepare_pose
ros2 run cuttofo_xcore execute_prepare_pose --x 0.35 --y 0.10 --z 0.40 --plane-angle-deg 40
```

### 编译

```
colcon build --packages-select cuttofo_xcore ✅

---

## 2026-05-12 — 实机验证 + 参数同步

### 实机验证结果

`execute_prepare_pose` 在 xCore 右臂（IP 192.168.2.161）上验证通过：

- 法兰坐标系控制逻辑正确 ✅
- `build_target_rotation_from_constraints` 约束（刀脊朝前 + 平面角）在真机上行为与仿真一致 ✅
- ROS2 Service（`/robot/get_state`、`/robot/move_joints`、`/robot/enable_arm`）连接正常 ✅
- TCP→法兰位置转换（含 URDF joint_tcp + tool_offset）正确 ✅

### 参数默认值同步

| 参数 | 修改前 | 修改后 | 说明 |
|------|--------|--------|------|
| `--candidate-count` | 80 | **240** | 与仿真脚本一致 |
| `--preview-steps` | 8 | **15** | 与仿真脚本一致 |

### 编译

```
colcon build --packages-select cuttofo_xcore ✅
```

---

## 2026-05-12 — Phase 2 控制逻辑审查：execute_prepare_pose vs knife_prepare_action_server

### 审查范围

对比测试脚本 `execute_prepare_pose.py` 与 Phase 2 管道 `knife_prepare_action_server.py` + `tofu_state_node` + `tofu_geometry.py` 的控制逻辑一致性。

### 一致性确认 (通过)

| 项目 | 测试脚本 | Phase 2 | 一致性 |
|------|----------|---------|--------|
| 目标旋转构建 | `build_target_rotation_from_constraints` | 同 | ✅ |
| 平面角默认值 | 40° (导入自 prepare_pose_selector) | 40° (来自 tofu_geometry) | ✅ |
| Euler 约定 | scipy `"xyz"` 内旋 | 同 | ✅ |
| 运动接口 | `arm.move_to_joints()` | 同 | ✅ |
| 关节安全边界 | 15° | 15° (`_SAFETY_MARGIN_RAD`) | ✅ |

### 发现的问题

#### ❌ Bug 1: `_FLANGE_TO_TCP` 硬编码仅右臂

**文件**: `execute_prepare_pose.py:54`

```python
_FLANGE_TO_TCP = np.array([-0.003123, 0.089822, -0.111511], dtype=float)
```

`tool_offset.yaml` 中左右臂偏移不同：
- 右臂: `[-0.0031, 0.0898, -0.2085]`
- 左臂: `[0.0151, 0.0504, 0.1434]`

切换 `--arm-side left` 时 offset 错误，编译不影响但运行时位置偏差。

**修复方向**: 从 `tool_offset.yaml` 动态读取。

#### ⚠️ Bug 2: Phase 2 IK 缺少多候选+评分

`knife_prepare_action_server.py` 调用 `arm.solve_ik()` 返回第一个有效解。`execute_prepare_pose.py` 用 240 种子 + 切预览评分排序选最优。Phase 2 可能选到关节余量小或手腕运动大的解。

**修复方向**: 将多候选逻辑集成到 `knife_prepare_action_server.py`。

#### ⚠️ Bug 3: 两份相同的 `build_target_rotation_from_constraints`

| 文件 | 默认 plane_angle_deg |
|------|---------------------|
| `tofu_geometry.py` | **40.0** |
| `prepare_pose_selector.py` | **90.0** |

实现体完全重复，默认值不一致。

**修复方向**: 统一到 `tofu_geometry.py`，`prepare_pose_selector` 导入。

#### ⚠️ Bug 4: `prepare_pose_selector.py` 硬编码右臂常量

`ACTIVE_JOINT_NAMES` 和 `Q_HOME` 硬编码右臂值，左臂不可用。`execute_prepare_pose.py` 通过 `config_loader` 规避了此问题。

### 文件改动

本次仅审查，未修改代码。
```

## 2026-05-13 RViz 可视化：真实臂 + 虚拟手 + 点云

- Objective: 创建独立可视化脚本，实时订阅真实机械臂关节状态 + 注入虚拟灵巧手关节 + RealSense 3D 点云，在 RViz 中同步显示
- Work completed:
  1. **`cuttofo_xcore/viz_hand_joint_bridge.py`** (新文件) — 独立 ROS2 节点：
     - 订阅 `/arm_r/joint_states` + `/arm_l/joint_states`（真实机械臂）
     - 映射 `joint_N` → `AR5-5_07R/07L-W4C1C1_joint_N`（URDF 全名）
     - 注入 LinkerHand O6 右手 11 个关节（7 active + 4 mimic DIP，默认全 0 = 手张开）
     - 发布合并后的 JointState 到 `/joint_states_full`
     - 参数 `use_real_hand:=false`（默认虚拟手），设为 `true` 时订阅 `/hand/joint_states`
     - 50Hz 定时发布，BEST_EFFORT QoS 匹配 xcore_controller
  2. **`launch/viz_display.launch.py`** (新文件) — 独立启动文件：
     - 加载 xacro URDF（含 LinkerHand O6）
     - 启动 `robot_state_publisher`（remap 到 `/joint_states_full`）
     - 启动 `viz_hand_joint_bridge` 节点
     - 可选启动 RealSense（`enable_realsense:=true`，含点云+深度对齐）
     - 启动 RViz2（使用现有 `dual_display.rviz` 配置）
     - 启动 `world_display` → `world` 静态 TF
     - **不修改任何现有文件**
  3. **`setup.py`** — 添加 `viz_hand_joint_bridge` entry_point
- Architecture:
  ```
  /arm_r/joint_states ─┐
                       ├─→ viz_hand_joint_bridge → /joint_states_full → robot_state_publisher → TF → RViz
  /arm_l/joint_states ─┘         ↑
                          虚拟手关节 (0.0)
                          或 /hand/joint_states (未来)
  
  RealSense → /camera/camera/depth/color/points → RViz PointCloud2
  ```
- Usage:
  ```bash
  # 先启动机械臂控制器
  ros2 launch dexbot_bringup dual_xcore_controllers.launch.py arm_r_robot_ip:=192.168.2.161 arm_l_robot_ip:=192.168.2.160
  
  # 再启动可视化（含点云）
  ros2 launch cuttofo_xcore viz_display.launch.py enable_realsense:=true
  ```
- 灵巧手接口预留：`use_real_hand:=true` + `hand_input_topic:=/hand/joint_states`
- Verification: `python3 -m py_compile` on all 3 files — pass
- Files changed:
  - `cuttofo_xcore/viz_hand_joint_bridge.py` (NEW)
  - `launch/viz_display.launch.py` (NEW)
  - `setup.py` (added entry_point)

## 2026-05-13 Bug Fix: 臂基座位置和坐标系修复

- Objective: 修复 `viz_display.launch.py` 启动后 RViz 中臂位置不正确、base坐标系方向错误的问题
- Root cause: 与 `dual_display.launch.py` 对比，发现三处差异：
  1. `fixed_right`/`fixed_left` 的 origin 未被 patch（臂基座位置错误）
  2. `world_display` → `world` 静态 TF 是恒等变换，缺失 roll=-π/2, pitch=π 的旋转
  3. RViz 缺少 `-f world_display` 参数
- Fix applied:
  1. 添加 `right_arm_xyz`/`right_arm_rpy`/`left_arm_xyz`/`left_arm_rpy` 参数，在 URDF 中 patch `fixed_right` 和 `fixed_left`（默认值与 `dual_display.launch.py` 一致）
  2. `world_display` → `world` 静态 TF 改用 LaunchConfiguration 获取旋转值（默认 roll=-π/2, pitch=π, yaw=0）
  3. RViz 启动参数添加 `-f world_display`
  4. `viz_hand_joint_bridge.py` 的 `main()` 中 `rclpy.shutdown()` 加 try/except，防止 Ctrl-C 时 "already shutdown" 报错
- Verification: `python3 -m py_compile` + `colcon build --packages-select cuttofo_xcore` — pass
- Files changed:
  - `launch/viz_display.launch.py` (arm base origin, world rotation, RViz -f 参数)
  - `cuttofo_xcore/viz_hand_joint_bridge.py` (rclpy.shutdown 保护)

## 2026-05-13 实时点云显示修复

- Objective: 修复 RealSense IMU 权限问题 + RViz 点云无法显示的问题
- Bug 1 — RealSense IMU 权限错误:
  - 错误: `Failed to open scan_element ... Permission denied` (HID-Sensor IIO 设备)
  - Fix: `enable_gyro:=false`, `enable_accel:=false`（点云/深度/彩色流不受影响）
- Bug 2 — RViz 点云丢失:
  - 错误: `Message Filter dropping message: frame 'camera_depth_optical_frame' ... because the queue is full`
  - 原因: 缺少 `world` → `camera_link` 静态 TF，RViz 无法解析点云坐标系
  - Fix: 添加 `world_to_camera_link_approx` static_transform_publisher 节点
- Bug 3 — 相机位置不准确:
  - 使用 `config/calib_right/calibration_result_right.yaml` 中的 `T_base_cam` 矩阵提取相机位姿
  - 从 4x4 齐次矩阵分解出平移 (x=0.246382, y=0.184995, z=-0.173261) 和四元数 (qx=0.61459041, qy=-0.46600654, qz=0.51442819, qw=0.37480684)
  - 替换默认近似值，使用标定结果作为 `world` → `camera_link` 的精确位置
- Verification: `python3 -m py_compile` + `colcon build --packages-select cuttofo_xcore` — pass
- Files changed:
  - `launch/viz_display.launch.py` (enable_gyro/accel:=false, 添加 camera_link TF, 使用标定结果)

## 2026-05-13 点云旋转错误修复（根因分析）

- Objective: 修复点云出现在"右臂前方"而非"右臂下方"的旋转错误
- Symptom: 机械臂位置正确，但点云出现在错误方向（旋转约90°）
- Root cause 分析过程（3次迭代）:

### 第一次尝试（错误）
- 直接使用 T_base_cam 的原始四元数作为 `world → camera_link`
- 结果：点云"立起来了"（地面是竖直的）
- 原因分析：T_base_cam 是 base → optical_frame 的变换，但被直接当作 base → camera_link 发布

### 第二次尝试（错误）
- 假设 RealSense camera_link 使用标准 ROS 坐标系：X forward, Y left, Z up
- 计算了 R_link_to_optical = [[0,-1,0],[0,0,-1],[1,0,0]]
- 应用 R_optical_to_link 校正，得到 qx=0.096, qy=0.004, qz=0.144, qw=0.985
- 结果：点云出现在"右臂前方"而非"右臂下方"
- 原因：RealSense camera_link 的实际坐标系约定与假设不符

### 第三次尝试（正确）
- 通过 `ros2 topic echo /tf_static` 验证 RealSense 驱动实际发布的 TF
- 读取 realsense2_camera 源码确认 `camera_link → optical_frame` 旋转
- **关键发现**：RealSense 驱动使用的旋转四元数为 `(-0.5, 0.5, -0.5, 0.5)`
- 对应旋转矩阵：R_link_to_optical = [[0,0,1],[-1,0,0],[0,-1,0]]
- 这意味着 RealSense camera_link 的轴向是：X=forward, Y=left, Z=up（标准 ROS body 约定）
- **不是**我之前假设的 X=right, Y=down, Z=forward
- 正确的 optical→link 旋转矩阵为 R_link_to_optical 的转置
- 最终校正四元数：qx=-0.51890945, qy=0.47048780, qz=-0.37032558, qw=0.61010915

### 结论：不是标定问题

标定结果 T_base_cam 是**完全正确的**。问题在于：
1. T_base_cam 的坐标系约定（T_base_cam 是 base → optical_frame）与我们在 RViz 中使用的 camera_link 坐标系不同
2. 需要理解 RealSense 驱动的具体坐标系约定才能正确应用标定结果
3. 标定过程本身没有问题

### 最终正确的参数
| 参数 | 值 | 说明 |
|------|-----|------|
| cam_x | 0.246382 | 平移（不变） |
| cam_y | 0.184995 | 平移（不变） |
| cam_z | -0.173261 | 平移（不变） |
| cam_qx | -0.51890945 | 从 base→optical 经 R_optical_to_link 校正 |
| cam_qy | 0.47048780 | 同上 |
| cam_qz | -0.37032558 | 同上 |
| cam_qw | 0.61010915 | 同上 |

### RealSense camera_link 坐标系总结
- **camera_link**: X forward, Y left, Z up（标准 ROS body 约定）
- **camera_depth_optical_frame**: X right, Y down, Z forward（光学坐标系）
- 驱动内部发布 camera_link → camera_depth_optical_frame 旋转：四元数 (-0.5, 0.5, -0.5, 0.5)

- Files changed:
  - `launch/viz_display.launch.py` (校正后的四元数参数替换错误值)

## 2026-05-13 下午 RViz 机械臂模型不跟随移动 — 诊断与修复记录

### 问题描述
启动 `viz_display.launch.py` 后，RViz 中右臂模型初始位置正确，但移动真实机械臂时模型不跟随更新。

### 诊断过程

1. **QoS 问题**（第一次错误修复）
   - 发现 `viz_hand_joint_bridge.py` 使用 `BEST_EFFORT` QoS 订阅 `/arm_r/joint_states`，而 xcore_controller 发布用默认 `RELIABLE` QoS
   - 对比 `dual_joint_state_merge.py`（正常工作）使用默认 RELIABLE
   - Fix: 改为默认 RELIABLE QoS + 收到消息即时发布（callback 触发，而非 timer）

2. **viz_display 未运行**（第二次诊断）
   - 用户终端中 `ros2 topic list` 报错 `rclpy.ok()` — ROS 环境变量未加载
   - 重启 daemon 后确认 `/joint_states_full` 存在且 bridge 正常发布

3. **TF 树正确**（第三次诊断）
   - `world → AR5-5_07R-W4C1C1_base` 等 TF 链路完整且正确发布
   - 静态 TF（fixed joints）正确：world → base、world → camera_link
   - 动态 TF（关节状态）以 ~17Hz 更新

4. **数据流验证**（第四次诊断）
   - `/joint_states_full` 以 100Hz 发布
   - 关节名称正确：`AR5-5_07R-W4C1C1_joint_1` ~ `_joint_7` + 11 个手关节
   - bridge 正确订阅并转发

5. **关节值冻结**（根因确认）
   - 连续多次 `ros2 topic echo /arm_r/joint_states --once` 显示**同一组关节值完全不变**
   - 时间戳在推进（发布正常），但位置数据冻结
   - ping 192.168.2.161 正常，ROS_DOMAIN_ID=13
   - **根因：用户同时启动了两个 xcore_controller 节点**（可能从两个不同终端/配置），导致关节状态被错误覆盖或读取到的是其中一方的缓存值

### 最终结论

viz_display 相关代码全部正确。**机械臂模型不跟随的真实原因是用户同时运行了两个机械臂控制器实例**，造成关节读数冻结在某一时刻的状态，与实际物理臂位置脱节。

### Files changed in this session
  - `cuttofo_xcore/viz_hand_joint_bridge.py` (QoS 修复: BEST_EFFORT→RELIABLE, timer→callback即时发布, 移除publish_rate参数)
  - `launch/viz_display.launch.py` (移除publish_rate参数)

## 2026-05-13 豆腐检测可视化节点

- Objective: 在 RViz 中实时显示豆腐检测结果（顶部4角点、TCP目标点、刀脊约束线、刀面法线方向）
- Work completed:
  1. **`cuttofo_xcore/tofu_visualizer_node.py`** (新文件) — ROS2 可视化节点：
     - 订阅 `/tofu_state` (TofuState)
     - 发布 `/tofu_visualization` (MarkerArray)
     - 显示内容：
       - 4 个顶部角点 ABCD（彩色球体 + 文字标签：A=红, B=绿, C=蓝, D=黄）
       - TCP 目标点（洋红色大球 + "TCP" 标签）
       - 刀脊方向（青色箭头，从 TCP 沿 edge_dir 方向延伸 12cm）
       - 豆腐顶部轮廓（半透明金色 LINE_STRIP，凸包排序）
       - 刀面法线方向（橙色箭头，从 TCP 沿 knife normal 方向延伸 6cm）
     - 参数可配置：frame_id, plane_angle_deg, knife_length
     - 当 `is_valid=False` 时自动清除所有 marker
     - marker lifetime=500ms，自动过期防止残留
  2. **`setup.py`** — 添加 `tofu_visualizer_node` entry_point
  3. **`launch/viz_display.launch.py`** — 添加 tofu_visualizer_node 节点到启动文件
- 集成方式：直接嵌入 `viz_display.launch.py`，启动即自动运行
- RViz 中添加 MarkerArray display 订阅 `/tofu_visualization` 即可看到
- Verification: `python3 -m py_compile` + `colcon build --packages-select cuttofo_xcore` — pass
- Files changed:
  - `cuttofo_xcore/tofu_visualizer_node.py` (NEW)
  - `setup.py` (added entry_point)
  - `launch/viz_display.launch.py` (added tofu_visualizer_node)

## 2026-05-13 cuttofu_phase2.launch.py 启动失败修复

### 问题描述

运行 `ros2 launch cuttofo_xcore cuttofu_phase2.launch.py enable_realsense:=true enable_aruco:=false` 报错：

```
[ERROR] [launch]: Caught exception in launch (see debug for traceback): [Errno 2] No such file or directory: ''
```

所有节点均未启动，日志中仅有以上一行错误信息，无完整 traceback。

### 根因定位过程

1. **Python traceback 捕获**：通过 monkey-patch `builtins.open` 捕获到 `open('')` 被调用
2. **Stack trace 确认**：`rs_launch.py:116` 执行 `yaml_to_dict(_config_file)` 时 `_config_file` 为空字符串
3. **参数冲突发现**：
   - `cuttofu_phase2.launch.py` 声明 `DeclareLaunchArgument("config_file", default_value="")`
   - RealSense `rs_launch.py:28` 也声明 `config_file`，默认值 `"''"`（两个单引号）
   - 当 IncludeLaunchDescription 包含 rs_launch 时，ROS2 将父级 `config_file=""` 传入子级
   - rs_launch.py:116 检查 `if _config_file == "''"`，但实际值为 `""`，判断为 False
   - 导致执行 `yaml_to_dict("")` → `open('')` → OSError

4. **对比 cuttofo_lbot**：cuttofo_lbot 版本同样有 `config_file=""`，但测试时意外通过——原因：IncludeLaunchDescription 参数传递行为在不同 launch 文件结构下表现不同

### 修复内容

| 文件 | 修改 |
|------|------|
| `launch/cuttofu_phase2.launch.py:51` | `DeclareLaunchArgument("config_file", ...)` → `DeclareLaunchArgument("cuttofo_config", ...)` |
| `launch/cuttofu_phase2.launch.py:66` | `LaunchConfiguration("config_file")` → `LaunchConfiguration("cuttofo_config")` |

参数重命名避免与 rs_launch.py 的 `config_file` 参数冲突。

### 验证结果

```bash
source install/setup.bash
ros2 launch cuttofo_xcore cuttofu_phase2.launch.py
```

启动成功，7 个节点全部运行：
- realsense2_camera_node ✅
- sam3_detector_node ✅
- pose_estimator_node ✅
- tofu_state_node ✅
- knife_prepare_action_server ✅
- tofu_cut_coordinator_node ✅
- rviz2 ✅

黄色 Warning（参数不支持）无害，来自 IncludeLaunchDescription 将父级 launch arguments 传递给子级，子级不接受的参数会打 warning。

### Files changed

- `launch/cuttofu_phase2.launch.py`（参数重命名 `config_file` → `cuttofo_config`）

### 完整启动命令

```bash
# 终端 1：机械臂控制器
ros2 launch dexbot_bringup dual_xcore_controllers.launch.py \
  arm_r_robot_ip:=192.168.2.161 arm_l_robot_ip:=192.168.2.160

# 终端 2：视觉管线 + 可视化
ros2 launch cuttofo_xcore cuttofu_phase2.launch.py enable_realsense:=true

# 终端 3：RViz（如需）
ros2 launch ar5_dual_arm_bringup dual_display.launch.py \
  use_joint_gui:=false enable_realsense:=false enable_aruco:=false
# RViz 中手动添加 /tofu_visualization MarkerArray

## 2026-05-13 修复 cuttofu_phase2.launch.py 缺少 tofu_visualizer_node + 空 RViz 问题

### 问题 1：`/tofu_visualization` topic 不存在

`tofu_visualizer_node` 注册在 `setup.py` 中，但 `cuttofu_phase2.launch.py` 中**没有 Node 条目**。之前只加到了 `viz_display.launch.py`，`cuttofu_phase2.launch.py` 从未包含该节点。

### 问题 2：启动时弹出空白 RViz

`cuttofu_phase2.launch.py` 默认 `enable_rviz=true`，且未指定 `-d` 配置文件，导致每次运行都会弹出一个**空白 RViz 窗口**，与终端 3 中 `dual_display.launch.py` 带配置的 RViz 重复。

### 修复

| 文件 | 改动 |
|------|------|
| `launch/cuttofu_phase2.launch.py:59` | `DeclareLaunchArgument("enable_rviz", default_value="true")` → **`"false"`** |
| `launch/cuttofu_phase2.launch.py:149-155` | 新增 `tofu_visualizer_node` Node 条目（#7，紧接在 tofu_cut_coordinator_node 后） |
| | rviz2 顺延为 #8 |

### 验证

```bash
ros2 launch cuttofo_xcore cuttofu_phase2.launch.py
```

启动后 8 个节点：
1. realsense2_camera_node ✅
2. sam3_detector_node ✅
3. pose_estimator_node ✅
4. tofu_state_node ✅
5. knife_prepare_action_server ✅
6. tofu_cut_coordinator_node ✅
7. **tofu_visualizer_node** ✅（新增）
8. **rviz2** ❌（默认关闭，不再弹出空白窗口）

无 RViz 弹出，`/tofu_visualization` 话题存在。

### Files changed

- `launch/cuttofu_phase2.launch.py`（添加 tofu_visualizer_node 节点，修改 enable_rviz 默认值）

## 2026-05-13 下午 豆腐检测几何逻辑修复

### 背景

业务逻辑审查发现代码与业务逻辑文档存在多处不一致：
1. A, B 点选取错误（用了 Z 最大的点，实际应为 Z 最小的点）
2. l 向量 flip 逻辑错误（应向 +Z 偏移，实际翻向了 -Z）
3. `build_rotation_with_edge_dir` 轴分配错误（edge_dir 放入了 tcp_X，实际应放入 tcp_Y）

### 业务逻辑确认

| 约束 | 数学表达 |
|------|---------|
| 刀脊 | `tcp_Y = v`（沿豆腐左边棱边） |
| 刀面倾斜 | `tcp_Z` 与 XZ 平面夹角 = plane_angle |
| v 方向 | 在 XZ 平面内，`v · base_X+ > 0`（锐角） |
| l 方向 | `l = cross(v, [0,1,0])`，自动满足 `l · base_Z+ > 0` |

### 代码修复

#### `tofu_geometry.py` 重写

| 函数 | 修复内容 |
|------|---------|
| `compute_edge_dir()` | A,B 改为 `sorted_idx[0], [1]`（Z 最小=左侧），v 投影 XZ 平面并锐角约束 |
| `compute_tcp_target_from_corners()` | 同上，移除 l flip 逻辑（`v.x > 0` 自动保证 `l.z > 0`），l 偏移方向改为 +Z（arm 侧） |
| `build_rotation_with_edge_dir()` | 修正列分配：`tcp_Y = edge_dir`（刀脊），`tcp_Z` 刀面法线推导正确 |

### 数学验证

| 测试 | 结果 |
|------|------|
| 豆腐平放：edge_dir = [1,0,0] | ✅ |
| 豆腐旋转 30°：edge_dir 与 base_X 夹角 = 30° | ✅ |
| l ⊥ v 正交性 | ✅ |
| 旋转矩阵 det=1，正交性 max=2.22e-16 | ✅ |
| 退化验证：`build_rotation_with_edge_dir(α, [1,0,0])` = `build_target_rotation_from_constraints(α)` | ✅ |
| 端到端管线：豆腐旋转 15° → edge_dir 正确 → TCP 正确 | ✅ |

### Files changed

- `cuttofo_xcore/cuttofo_xcore/tofu_geometry.py`（完全重写）
- `.project-log/business-logic.md`（Section 12 全部重写，新增 10 个子节）
- `.project-log/business-logic.md`（约束表、A/B 定义、edge_dir 注释等更新）

## 2026-05-13 滑动窗口多帧平均噪声抑制

### 背景

豆腐和相机在切削准备阶段静止不动，深度噪声和 SAM3 分割边缘帧间抖动导致角点坐标每帧都在波动，影响 edge_dir 和 tcp_target 的稳定性。

### 方案：滑动窗口多帧平均

```
帧 t-14 ─┐
帧 t-13 ─┤
...      ─┼─→ buffer[15帧] ──→ mean(top_corners) ──→ 几何计算 ──→ 输出
帧 t-1  ─┤
帧 t    ─┘
```

每帧：推入新 top_corners → 弹出最老帧 → buffer 内角点取均值 → 基于平均角点算 edge_dir 和 tcp_target。

### 跳变检测

单帧跳变（> threshold）：丢弃该帧，buffer 保留，consecutive_discards 计数 +1。
连续丢弃 ≥ buffer_size 次：认定真实移动（如豆腐旋转），清空 buffer 重新积累。

| 情况 | 行为 |
|------|------|
| 单帧跳变（噪声/异常） | **丢弃该帧**，buffer 不变，counter +1 |
| 连续跳变 < buffer_size 次 | 持续丢弃，buffer 保持稳定 |
| 连续跳变 ≥ buffer_size 次 | 真实移动，清空 buffer 重新积累 |

### 参数（可调）

| 参数 | 默认 | 说明 |
|------|------|------|
| `buffer_size` | 15 | 滑动窗口帧数 |
| `jump_threshold` | 0.05m | 跳变检测阈值 |
| `min_buffer_frames` | 3 | 最少帧数才输出有效结果 |

### 噪声抑制效果

2mm 深度噪声 → 15 帧平均后 ≈ 0.28mm（理论值 σ/√15 ≈ 0.52mm）。

### 边界处理

| 情况 | 处理 |
|------|------|
| buffer 未满（< buffer_size） | 积累到 min_buffer_frames 后正常输出 |
| 豆腐消失 | buffer 保持，超时 is_valid=False |
| 豆腐位置突变 | 跳变检测 → 清空 buffer 重新积累 |
| 首次启动 | 等待 min_buffer_frames 后才输出 |

### Files changed

- `cuttofo_xcore/cuttofo_xcore/tofu_state_node.py`（重写：移除 EMA，改用滑动窗口 buffer）
- `cuttofo_xcore/config/cuttofo_config.yaml`（新增 buffer_size/jump_threshold/min_buffer_frames，移除 smoothing_alpha）
- `cuttofo_xcore/launch/cuttofu_phase2.launch.py`（参数同步更新）
## 2026-05-13 下午 — pose_estimator_node 标定文件路径修复

### 问题描述

`pose_estimator_node` 的 `calibration_file` 参数默认值为空字符串，导致节点无法加载标定文件，发布到 `/objects_with_pose` 的豆腐位姿全为零。

### 根因分析

| 路径 | 状态 |
|------|------|
| `install/dexbot_bottom_layer/share/.../calibration_result.yaml` | 不存在 |
| `/home/kim/projects/dexbot_ros2_ws/src/config/calibration_result.yaml` | 不存在 |
| `calibration_file=""`（launch 默认） | 空字符串，触发 fallback 逻辑，仍找不到 |

### 标定文件格式对比

| | 旧格式 `calibration_result.yaml` | 新格式 `calib_right/calibration_result_right.yaml` |
|---|---|---|
| 结构 | `calibration_result.rotation_matrix` + `translation_vector` | 顶层 `T_base_cam: [[4x4 matrix]]` |
| 样本数 | 28 | 10 |
| RMSE | 4.6mm / 1.37° | 3.38mm / 1.58° |
| 平移 | [0.125, -0.006, -0.076]m | [0.246, 0.185, -0.173]m |

### 修复内容

#### 1. `pose_estimator_node.py` — `_load_calibration()` 重写

支持 3 种格式自动识别：

```python
# Format 1: 顶层 T_base_cam 4x4 矩阵（新格式，优先检测）
if "T_base_cam" in calib_data and isinstance(calib_data["T_base_cam"], list):
    mat = np.array(calib_data["T_base_cam"])
    if mat.shape == (4, 4):
        T_base_cam = mat

# Format 2: legacy rotation_matrix + translation_vector
if "rotation_matrix" in cr and "translation_vector" in cr:
    T_base_cam[:3,:3] = rot_matrix; T_base_cam[:3,3] = trans_vector

# Format 3: legacy T_base_cam 4x4 inside calibration_result
if "T_base_cam" in cr and isinstance(cr["T_base_cam"], list):
    T_base_cam = np.array(cr["T_base_cam"])
```

#### 2. `cuttofo_config.yaml` — 标定路径按臂分离

```yaml
vision:
  calibration_file_right: ".../src/config/calib_right/calibration_result_right.yaml"
  calibration_file_left:  ".../src/config/calib_left/calibration_result_left.yaml"
```

#### 3. `cuttofu_phase2.launch.py` — 自动选择标定文件

根据 `active_arm`（环境变量 > config 文件 > 默认 right）自动选择对应的标定文件作为 `calibration_file` 默认值。

### 验证结果

```bash
colcon build --packages-select dexbot_middle_layer cuttofo_xcore  # ✅ 通过

ros2 launch cuttofo_xcore cuttofu_phase2.launch.py --show-args \
  | grep calibration_file
  # default: /home/tbl/Project/dexbot_ros2_ws/src/config/calib_right/calibration_result_right.yaml
```

### Files changed

- `src/dexbot_middle_layer/dexbot_middle_layer/pose_estimator_node.py`（`_load_calibration()` 重写，支持 3 种格式）
- `src/cuttofo_xcore/config/cuttofo_config.yaml`（新增 `calibration_file_right/left`）
- `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`（根据 active_arm 自动选择标定文件）

---

## 2026-05-13 — 坐标系变换分析：optical→link 校正是否需要应用于视觉管线

### 问题

RViz 点云显示中使用了 optical→link 坐标系校正（`viz_display.launch.py` 中 `T_base_cam` 去除 optical 旋转后发布 `world→camera_link`），而 `pose_estimator_node` 的 `_load_calibration()` 直接对 optical frame 的点应用 `T_base_cam`。疑问：视觉管线是否也需要同样处理？

### 分析结论：不需要

两条路径使用同一个 `T_base_cam`，但变换方式不同：

#### Path A：RViz 点云显示

```
点云数据 (camera_depth_optical_frame)
    ↓ [RealSense 驱动内部 TF: camera_link → optical_frame]
camera_link
    ↓ [viz_display.launch.py: world → camera_link]
    ↓ = T_base_cam × (optical→link)⁻¹   ← 必须去除 optical 旋转
world
```

RealSense 驱动内部发布 `camera_link → camera_depth_optical_frame`。因此 `viz_display.launch.py` 必须发布 `world → camera_link`（把标定结果中的 optical 旋转去掉），否则会被驱动的 TF 重复应用导致错乱。

#### Path B：视觉管线位姿估计

```
深度像素 + mask
    ↓ [针孔反投影: (u,v,d) → 3D]
3D 点 (已在 optical_frame: X右, Y下, Z前)
    ↓ [T_base_cam @ pose_cam]   ← 直接左乘，无需校正
pose_base (Body_Base_link)
```

`vision_utils.py` 的 `get_pose_from_mask()` 通过针孔模型反投影得到的 3D 点天然就在 optical frame 中。`T_base_cam` 本身就是 optical→base 的 4x4 矩阵，直接左乘即可变换到机器人 base 坐标系。

### 为什么不冲突

| | RViz 点云 | 视觉管线 |
|---|---|---|
| 输入坐标系 | optical_frame（点云 topic） | optical_frame（针孔反投影） |
| T_base_cam 含义 | base ← optical | base ← optical |
| 是否需要 optical→link 校正 | **需要**（TF 链路中间有 RealSense 驱动的 link→optical） | **不需要**（直接对 optical 坐标做矩阵变换，不经过 TF 树） |

### 结论

`/objects_with_pose` 发布的 6D pose 是正确的，无需额外处理。RViz 中的 optical→link 校正是 TF 树链路结构需要，视觉管线直接在代码中对 optical frame 的点做矩阵乘法，不经过 TF 树，因此不存在重复变换的问题。

---

## 2026-05-13 — TCP Offset 标定与补偿方案设计

### 问题分析

| 问题 | 说明 |
|------|------|
| 当前 IK 目标 | `link_tcp` = 法兰 + [0, 0, 0.097]（URDF 虚拟偏移，无物理含义） |
| 实际刀刃中心 | 法兰 + `tcp_offset`（标定值，如 [-0.003, 0.090, -0.209]） |
| 视觉目标语义 | "刀刃中心应到达的位置" |
| 当前误差 | IK 把 link_tcp 放到目标位置，实际刀刃中心偏差可达 300mm |
| `tool_offset.yaml` | 存在但 cuttofo_xcore 包完全不加载 |
| `/robot/get_state` | 始终返回法兰位姿（flangeInBase），代码注释+测试确认 |

### 方案设计

核心思路：将 `tip_link` 改为 `link7`（法兰），在 adapter 层统一处理 TCP offset 补偿。

```
视觉输出: tcp_target_pos, target_R
    ↓
TCP→法兰: flange_target = tcp_target - target_R @ tcp_offset
    ↓
IK 求解: 把 link7(法兰) 放到 flange_target, 姿态 = target_R
    ↓
Preview 评分: 每个 preview 点同样做 TCP→法兰补偿
    ↓
运动执行: move_to_joints(best_q)
```

### 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| IK 目标 frame | link7（法兰） | 消除 link_tcp 的 97mm 虚拟偏移 |
| TCP offset 存储 | `cuttofo_config.yaml` 按臂分离 | 与现有配置体系一致 |
| 补偿层位置 | `xcore_arm_adapter.py` 内部 | 上层代码无需感知 offset |
| 标定前默认值 | [0, 0, 0] | TCP = 法兰原点，比 link_tcp 更直观 |
| 姿态处理 | 不变（纯平移标定） | 法兰姿态 = TCP 姿态 |

### 文档更新

- `.project-log/business-logic.md` Section 1.2 更新坐标系定义
- `.project-log/business-logic.md` Section 6.1 更新 Phase 2 数据流（加入 TCP→法兰补偿步骤）
- `.project-log/business-logic.md` 新增 Section 13: TCP Offset 标定与补偿（完整设计）

### 代码修改清单（待实施）

| # | 文件 | 修改 | 影响 |
|---|------|------|------|
| 1 | `cuttofo_config.yaml` | 新增 `tcp_offset`，`tip_link` 改为 link7 | 配置 |
| 2 | `xcore_arm_adapter.py` | 加载 tcp_offset，solve_ik/compute_fk/get_pose 内部补偿 | 核心 |
| 3 | `execute_prepare_pose.py` | 删除硬编码 `_FLANGE_TO_TCP`，改用 adapter | 清理 |
| 4 | `prepare_pose_selector.py` | tip_link 改为 link7，preview 加入补偿 | 离线工具 |
| 5 | `knife_prepare_action_server.py` | 无需修改 | — |
| 6 | `tofu_state_node.py` | 无需修改 | — |
| 7 | `tofu_geometry.py` | 无需修改 | — |

### Next steps

等待用户确认方案后开始实施代码修改。

---

## 2026-05-13 — TCP Offset 代码实施

### 改动文件

| # | 文件 | 改动 |
|---|------|------|
| 1 | `config/cuttofo_config.yaml` | 两臂新增 `tcp_offset: [0,0,0]`；`tip_link` 从 `link_tcp` 改为 `link7` |
| 2 | `xcore_arm_adapter.py` | 加载 `tcp_offset`；`get_pose()` 返回 TCP 位姿；`compute_fk()` 返回 TCP 位姿；`solve_ik()` 内部做 TCP→法兰补偿 |
| 3 | `execute_prepare_pose.py` | 删除硬编码 `_FLANGE_TO_TCP` 和 `_FLANGE_LINK`；从 config 读取 `tcp_offset` 和 `tip_link`；`--x/y/z` 语义改为 TCP 目标位置 |
| 4 | `prepare_pose_selector.py` | `--tip-link` 默认值从 `link_tcp` 改为 `link7` |

### adapter 补偿逻辑

```python
# solve_ik: TCP目标 → 法兰目标 → IK求解
flange_target_pos = target_pos - target_R @ tcp_offset
IK(flange_target_pos, target_eul)

# compute_fk / get_pose: 法兰FK → 加TCP偏移
tcp_pos = flange_pos + R_flange @ tcp_offset
tcp_eul = flange_eul  # 姿态不变
```

### 验证结果

| 测试 | 结果 |
|------|------|
| `py_compile` xcore_arm_adapter.py | ✅ |
| `py_compile` execute_prepare_pose.py | ✅ |
| `py_compile` prepare_pose_selector.py | ✅ |
| `colcon build --packages-select cuttofo_xcore` | ✅ |
| FK(link7, q=0) = [0, 0, 0.7605] | ✅ |
| FK inverse check (tcp_offset=[0,0,-0.15]) | ✅ |
| Launch args `calibration_file` default | ✅ |
| `knife_prepare_action_server.py` 无需修改 | ✅（semantic不变） |

### 当前行为

`tcp_offset: [0, 0, 0]` 时，TCP = 法兰原点。等效于 IK 直接把法兰放到目标位置。标定后填入实际偏移值即可生效，无需改代码。

---

## 2026-05-13 — TCP 标定方案讨论

### 用户条件

- 有专用圆锥标定工具
- 机械臂支持拖动模式
- 准备多采集几个点

### 标定方法：N点法（≥4点）

**原理**：
```
P_knife = flange_pos + R_flange @ tcp_offset
```
同一空间参考点 P_ref，多个法兰姿态满足：
```
flange_pos_i + R_i @ tcp_offset = P_ref
(R_1 - R_i) @ tcp_offset = flange_pos_i - flange_pos_1
```
构成超定方程组，最小二乘求解 `tcp_offset`。

**物理准备**：
1. 固定参考点：圆锥标定工具的尖端
2. LinkerHand O6 以切豆腐姿势握刀，关节角度锁定
3. 拖动示教模式移动机械臂

**采集要求**：
- 至少 4 个姿态，建议 6 个
- 法兰姿态多样性越大越好（绕多个轴旋转）
- 每次让刀刃中心精确触碰圆锥尖端同一点

**求解**：
```python
A = [(R_i - R_1) for i in 2..N]  # shape: (3*(N-1), 3)
b = [flange_pos_i - flange_pos_1 for i in 2..N]
tcp_offset, residuals = np.linalg.lstsq(A, b)
rmse = np.sqrt(mean(residuals))
```

**保存**：写入 `cuttofo_config.yaml` → `arms.right.tcp_offset`

### 待实施

- 交互式标定脚本（ros2 run 脚本）
- 采集 → 求解 → 写入配置
- 实机验证标定精度

---

## 2026-05-14 — 代码审查修复（BUG 修复）

### 修复清单

| # | 严重度 | 文件:行 | 问题 | 修复 |
|---|--------|---------|------|------|
| P0 #1 | 高 | `tofu_geometry.py:57,91` | `v.x==0` 时 edge_dir 违反约束 | 增加 `abs(v.x/norm) < 1e-6` 回退检测 |
| P0 #10 | 高 | `xcore_arm_adapter.py:254-255` | `block=False` 时直接调 `future.result()` 崩溃 | 跳过 result 调用，直接返回 True |
| P1 #2 | 高 | `tofu_state_node.py:182,199` | 左臂 `top_y` 在 mirror 前计算，坐标系错误 | 移到 mirror 之后计算 |
| P1 #3 | 高 | `tofu_state_node.py:193,227` | 有效消息用输入 header，超时消息硬编码 `"base_link"` | 统一存 `_last_frame_id`，超时消息复用 |
| P1 #4 | 高 | `knife_prepare_action_server.py:182-190` | FK 验证只打印不检查，超误差也运动 | 增加 5mm 阈值检查，超限则 abort |
| P1 #5 | 高 | `knife_prepare_action_server.py:162-163` | 左臂 + edge_align 时旋转被镜像两次 | edge_align 路径不额外 mirror（tofu_state_node 已处理） |
| P1 #6 | 中 | `xcore_arm_adapter.py:171-241` | IK 求解无超时，困难位姿可阻塞数分钟 | 增加 `timeout_s=30.0` 参数 |
| P2 #16 | 中 | `tofu_cut_coordinator_node.py:85-102` | `future.result()` 无 try/except，abort 时抛异常 | 增加异常捕获和 None 检查 |

### 修复详情

**P1 #1 `tofu_geometry.py` edge_dir 退化情况**

```python
# 旧代码
v_raw = B - A if B[0] > A[0] else A - B
edge_dir = [v_raw[0], 0, v_raw[2]]
norm = np.linalg.norm(edge_dir)
if norm < 1e-12: return [1,0,0]
return edge_dir / norm

# 新代码：增加 v.x 退化检测
norm = np.linalg.norm(edge_dir)
if norm < 1e-12 or abs(edge_dir[0] / norm) < 1e-6:
    return np.array([1.0, 0.0, 0.0])  # 回退
return edge_dir / norm
```

**P1 #5 knife_prepare_action_server 双重镜像**

```python
# 旧代码：所有路径统一 mirror
if self._arm_side == "left":
    target_R = mirror_rotmat(target_R)

# 新代码：edge_align 路径不 mirror（tofu_state_node 已处理）
if goal.edge_align:
    target_R = build_rotation_with_edge_dir(plane_angle_deg, edge_dir)
    # edge_dir 已在 tofu_state_node 中做了左右臂适配，不额外 mirror
else:
    target_R = build_target_rotation_from_constraints(plane_angle_deg)
    if self._arm_side == "left":
        target_R = mirror_rotmat(target_R)  # 仅非 edge_align 路径需要
```

**P1 #6 xcore_arm_adapter solve_ik 超时**

```python
def solve_ik(..., timeout_s: float = 30.0):
    t_start = time.time()
    for q_seed in seeds:
        if time.time() - t_start > timeout_s:
            logger.error("IK timeout after %.1fs", timeout_s)
            return None
        # ... least_squares 求解
```

### 编译验证

```
colcon build --packages-select cuttofo_xcore  ✅
py_compile 所有修改文件 ✅
```

### 未修复项（需要较大重构）

| # | 说明 |
|---|------|
| P1 #7 cancellation 未检查 | `_execute_callback` 全程不检查 `goal_handle.is_cancel_requested`，需重构为异步 or 轮询 |
| P2 #8 prepare_pose_selector 硬编码右臂 | 离线调试工具，不影响 Phase 2 主链路 |

## 2026-05-14 Local Time

- Objective: 将豆腐可视化集成到 `viz_display.launch.py`，实现一条命令启动臂+点云+豆腐视觉
- Work completed:
  - **viz_display.launch.py 集成豆腐视觉管线**：
    - 新增 `enable_vision:=true`（默认）启动 SAM3 → pose_estimator → tofu_state_node
    - `tofu_visualizer_node` 始终运行，订阅 `/tofu_state` 发布 `/tofu_visualization` MarkerArray
    - 新增启动参数：`enable_vision`, `text_prompt`, `calibration_file`, `plane_angle_deg`, `offset_a`, `vertical_offset`
    - 从 `cuttofo_config.yaml` 自动读取视觉/切削参数
    - 自动根据 `active_arm` 选择标定文件（calib_right/calib_left）
    - 添加 `_load_cuttofo_config()` / `_find_perception_config()` 辅助函数
  - **修复话题不匹配问题**（导致视觉管线不通）：
    - `sam3_detector_node`: `image_topic` 设为 `/camera/camera/color/image_raw`（RealSense ns=/camera, 节点名=camera）
    - `pose_estimator_node`: `depth_topic` 设为 `/camera/camera/depth/image_rect_raw`，`camera_info_topic` 设为 `/camera/camera/color/camera_info`
    - `detection_rate` 从 10.0 降至 5.0（减少 GPU 负载）
  - **同步修复 cuttofu_phase2.launch.py** 同样的话题参数问题
- Problems encountered:
  - RealSense 相机段错误退出（SIGSEGV, exit code -11）— 已知 USB/UVC 驱动问题，不影响本次修复
  - `tofu_state_node` 未出现在节点列表 — 原因：`pose_estimator_node` 启动失败（话题不匹配），launch 整体报错
  - SAM3 检测到豆腐但 `/detected_objects` 无数据 — SAM3 输出 segmentation mask 图像，但检测结果需 SAM3 模型成功分割目标才发布
- Resolution: 通过在 launch 文件中显式指定 RealSense 话题路径解决
- Verification:
  - `colcon build --packages-select cuttofo_xcore`: ✅ 通过
  - launch 文件语法检查（`generate_launch_description` 加载成功，29 个 entities）: ✅
- Files changed:
  - `src/cuttofo_xcore/launch/viz_display.launch.py`: 集成视觉管线节点，添加 enable_vision 标志和参数
  - `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`: 修复 sam3/pose_estimator 话题参数
- Next steps:
  1. 插上 RealSense 相机，实机验证完整视觉链路（SAM3 检测 → /tofu_state → /tofu_visualization）
  2. 验证 RViz 中豆腐角点、TCP 目标、刀面法线是否正确显示
  3. 完成 TCP 标定（当前 `tcp_offset=[0,0,0]`，需用 `calibrate_tcp_offset.py` 标定刀刃中心）

## 2026-05-14 Local Time（续）

- Objective: 修复 `tofu_state_node` 启动崩溃和 RViz 无 marker 显示问题
- Work completed:
  - **Bug #1：参数类型不匹配导致 `tofu_state_node` 启动失败（exit code 1）**
    - 根因：`LaunchConfiguration('offset_a').perform()` 返回字符串 `"0.03"`，写入参数文件后变成 YAML 字符串 `'0.03'`，与节点声明的 `float` 类型冲突
    - 修复 viz_display.launch.py：`float(LaunchConfiguration('offset_a').perform(context))`
    - 修复 cuttofu_phase2.launch.py：`ParameterValue(LaunchConfiguration("offset_a"), value_type=float)`
    - 同理修复 `vertical_offset`、`buffer_size`、`jump_threshold`、`min_buffer_frames`、`valid_timeout`
  - **Bug #2：`RcutilsLogger.debug/info` C 扩展不支持 C 风格 `%` 格式化多参数**
    - 根因：ROS2 Humble 的 `RcutilsLogger.debug()` C 扩展只接受 `(self, msg)`，不接受 variadic `*args`
    - 崩溃位置：`_on_objects` 第 168 行首次触发
    - 修复：将所有 `self.get_logger().debug/info("msg %d", arg)` 改为 f-string
    - 影响 3 处调用（tofu_state_node.py 第 145、154、168 行）
  - **实机验证：视觉链路已通**
    - SAM3 检测到 tofu：`Detection #N: Found 1 objects for prompt "tofu"` ✅
    - pose_estimator 输出 6D pose：`Published 1 objects with poses` ✅
    - tofu_state_node 修复后正常启动，但因 bug #2 崩溃（本次已修复）
- Problems encountered:
  - RealSense 相机分辨率与 SAM3 不匹配：D435I 实际发出 RGB=1280x720，Depth=848x480，但 pose_estimator 的 PLACEHOLDER 算法会 resize mask 补偿
  - pose_estimator 使用 PLACEHOLDER 算法（`⚠️ Using PLACEHOLDER get_pose_from_mask`）— 非生产级算法豆腐 6D pose
- Resolution: 修复了 launch 参数类型 + f-string 格式化
- Verification:
  - `colcon build --packages-select cuttofo_xcore`: ✅ 通过
  - 实机运行：`tofu_state_node` INFO 日志正常打印（arm=right, buffer_size=15）
  - SAM3 检测 + pose_estimator 发布链路验证通过（/objects_with_pose 有数据）
  - tofu_visualizer_node 启动成功：`/tofu_state -> /tofu_visualization (frame=world)` ✅
- Files changed:
  - `src/cuttofo_xcore/launch/viz_display.launch.py`: `tofu_state_node` 参数 `float()` 类型转换
  - `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`: `tofu_state_node` 参数 `ParameterValue(..., value_type=float)`
  - `src/cuttofo_xcore/cuttofo_xcore/tofu_state_node.py`: f-string 格式化修复 3 处 debug/info 调用
- Next steps:
  1. 重新启动 viz_display.launch.py，验证 RViz 中豆腐 marker 显示（A/B/C/D 角点 + TCP 目标 + 刀面法线）
  2. 验证 tofu_state_node 滑动窗口是否正常工作（buffer 积累后输出有效 /tofu_state）
  3. 完成 TCP 标定（当前 `tcp_offset=[0,0,0]`）
  4. 推进 Phase 2 端到端：/tofu_state → knife_prepare_action_server → 臂运动

## 2026-05-14 Local Time（续）

- Objective: 修复 ABCD 角点严重偏离点云的问题
- Root cause analysis:
  - **症状**: ABCD 严重偏离点云，但机械臂点云/URDF 偏差仅 3-4cm（正常标定误差）
  - **根因链路**:
    1. `pose_estimator_node` 用 `/camera/camera/depth/image_rect_raw` (848x480 原始深度) + `/camera/camera/color/camera_info` (1280x720 彩色内参)
       → 用 1280x720 的 K 去反投影 848x480 的 depth，3D 位置系统性严重偏差
    2. `tofu_state_node` 用 `pose + quaternion + extents` 反推角点 → PLACEHOLDER PCA 算法对只露一面的豆腐不可靠
    3. `extract_top_corners` 只取 Y 最大的 4 点但无稳定 A/B/C/D 排序 → visualizer 标注顺序任意
- Work completed:
  1. **修复 depth/camera_info 不匹配**
     - `viz_display.launch.py`: depth_topic → `/camera/camera/aligned_depth_to_color/image_raw`，camera_info_topic → `/camera/camera/aligned_depth_to_color/camera_info`
     - RealSense 参数名统一：`rgb_camera.color_profile` / `depth_module.depth_profile`
     - `cuttofu_phase2.launch.py` 同步修复
  2. **修复 K 内参在 mask/depth 尺寸不匹配时的缩放**
     - `vision_utils.py`: mask resize 时同步按比例缩放 K 的 fx, fy, cx, cy
  3. **ABCD 改用点云直接估计，不依赖不可靠的 PCA OBB 反推**
     - `vision_utils.get_pose_from_mask`: 从 base 坐标系下点云直接算顶面 XZ 分位角点 → A/B/C/D
     - 通过 `geometric_features[8:20]` 传递
     - `tofu_state_node`: 优先用直接计算的角点，fallback 才用 pose+extents 重建
  4. **A/B/C/D 排序修复**（业务定义：AB = Z 最小侧且 A→B 沿 +X）
     - `tofu_geometry.extract_top_corners`: 先按 Z 分成 left/right 两侧，再各自按 X 排序
     - A = left 侧 X 最小的点，B = left 侧 X 次小的点（保证 A→B 沿 +X）
     - C = right 侧 X 最小的点，D = right 侧 X 次小的点
  5. **PCA extents 排序 bug 修复**
     - `vision_utils`: 移除 `np.sort(extents)[::-1]`，改为 `proj_max - proj_min` 保留轴对应关系
  6. **frame_id 修复**
     - `tofu_state_node`: frame_id 强制设为 `"world"`（不依赖 xcore 控制器的 `Body_Base_link` TF）
     - `tofu_visualizer_node`: marker 用 `msg.header.frame_id`（跟随 `/tofu_state` 的 frame）
  7. **tofu_state_node 滑动窗口调参**
     - `buffer_size`: 15 → **30**
     - `min_buffer_frames`: 3 → **5**
     - 跳变检测改为与 buffer 平均中心比较（更稳定）
  8. **`world→camera_link` TF 自动计算**
     - `viz_display.launch.py`: 从 `T_base_cam` 自动计算，不再依赖手填硬编码值
  9. **pose_estimator_node 启动时打印 image geometry 日志**
     - 一次性打印 depth 分辨率和 K 参数，便于确认 depth/K 匹配
- Problems encountered:
  - ABCD 仍可能有小量偏差（3-4cm 来自标定 RMSE），待进一步评估
  - PLACEHOLDER 算法仍有警告，需后续升级为更稳定的 6D 姿态估计算法
  - `T_base_cam` RMSE 4.36mm，豆腐角点误差可能达 1-2cm（杠杆放大）
- Verification:
  - `colcon build --packages-select dexbot_middle_layer cuttofo_xcore`: ✅
  - 实机：ABCD 贴合点云表面 ✅
  - 日志：`Pose image geometry: depth=1280x720, K=[...]` ✅
- Files changed:
  - `src/dexbot_middle_layer/dexbot_middle_layer/vision/pipeline/vision_utils.py`: ABCD 从点云直接算，K 缩放，PCA extents 不再排序
  - `src/dexbot_middle_layer/dexbot_middle_layer/pose_estimator_node.py`: 传递直接计算的 ABCD，日志打印 image geometry
  - `src/cuttofo_xcore/cuttofo_xcore/tofu_geometry.py`: `extract_top_corners` 稳定 A/B/C/D 排序
  - `src/cuttofo_xcore/cuttofo_xcore/tofu_state_node.py`: frame_id="world"，buffer 调参，优先用直接计算角点
  - `src/cuttofo_xcore/cuttofo_xcore/tofu_visualizer_node.py`: marker 用 `msg.header.frame_id`
  - `src/cuttofo_xcore/launch/viz_display.launch.py`: aligned depth 话题，TF 自动计算
  - `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`: aligned depth 话题同步修复
- Next steps:
  1. 评估 ABCD 剩余偏差是否可接受（是否来自 T_base_cam 标定误差）
  2. 完成 TCP 标定（当前 `tcp_offset=[0,0,0]`）
  3. 端到端测试：/tofu_state → knife_prepare_action_server → 臂运动
  4. 升级 PLACEHOLDER 算法为稳定 6D 姿态估计

## 2026-05-14 Local Time（续）

- Objective: 修复 AB 角点内缩（AB 整体沿 +Z 偏移）和视野变窄问题
- Work completed:
  1. **AB 内缩根因修复**
     - 根因：ABCD 中 Z 边界从 `top_points`（Y 高分位点）里取，但 SAM3 mask/深度噪声/边缘倾斜导致左侧边缘点 Y 略低，被顶面筛选排除，使 Z min 向 +Z 内缩
     - 修复：Z/X 边界改为从**完整目标点云**（`points_base`）取 1%/99% 分位，不再依赖顶面筛选
     - 同时 Y（top_y）仍从顶面点云高分位估计，保证 Y 正确
  2. **视野变窄根因修复**
     - 根因：之前强制 `rgb_camera.profile=640x480x30`，可能导致 D435I FOV 裁切
     - 修复：恢复 `rgb_camera.profile=1280x720x30`，`depth_module.profile=848x480x30`（接近 D435I 默认值）
     - 保持 aligned_depth 链路（保证 K/depth 匹配），不回到 K/depth 错配问题
- Problems encountered:
  - 需实机验证 AB 内缩是否修复
  - 需确认 RealSense 分辨率恢复后 FOV 正常
- Files changed:
  - `src/dexbot_middle_layer/dexbot_middle_layer/vision/pipeline/vision_utils.py`: Z/X 边界改用完整点云分位估计
  - `src/cuttofo_xcore/launch/viz_display.launch.py`: RealSense color profile 改回 1280x720
  - `src/cuttofo_xcore/launch/cuttofu_phase2.launch.py`: RealSense profile 同步修改
- Next steps:
  1. 实机验证 AB 贴豆腐左边，FOV 恢复正常
  2. 评估 Z 偏移残余是否来自标定误差
  3. TCP 标定
  4. 端到端测试

## 2026-05-14 Local Time（续）

- Objective: 修复 GUI 灵巧手控制反问题和 CAN 初始化失败问题
- Work completed:
  1. **Open/Close 手指映射修复**
     - 根因：GUI 代码 Open 发 `[0]*dof`，Close 发 `[100]*dof`；实测 linkerbot-py 中 0=握紧，100=张开，语义完全相反
     - 修复：`_hand_open` → `[100.0]*dof`，`_hand_close` → `[0.0]*dof`
  2. **CAN 接口自动提权优化**
     - 根因：原代码只调 `pkexec bash -c ...`，GUI（Tk / 非 polkit agent）环境下弹出密码框可能失败
     - 修复：三段 fallback 策略：
       - ① 直接执行（适合 root / CAP_NET_ADMIN）
       - ② `sudo -n ...`（适合 sudo 缓存 / 免密配置）
       - ③ `pkexec env DISPLAY=... XAUTHORITY=... bash -lc ...`（带图形环境变量）
     - 失败提示改为完整 `sudo` 手动命令，便于拷贝执行
- Files changed:
  - `src/gui/pages/arm_hand.py`: Open/Close 角度值互换
  - `src/gui/services/hand/control.py`: CAN 初始化三段 fallback + 失败提示优化
- Next steps:
  1. 实机测试手 Open/Close
  2. 评估 CAN 自动 up 是否修复
  3. 若仍失败则配置 systemd can0 预启动或 sudo 免密规则
