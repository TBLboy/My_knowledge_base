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

## 2026-05-09 (续) - cuttofo_lbot 包建立与 Lbot 业务逻辑适配

### 背景

用户从 `cuttofo_xcore` 完整复制出 `cuttofo_lbot` 包，计划基于 Lbot 机械臂（LKRS73-I2）实现切豆腐业务。本次工作：
1. 修正复制包遗留下的命名问题（xcore → lbot）
2. 调研 Lbot 与 xCore 的差异
3. 调整业务逻辑文档适配 Lbot

### 已完成工作

#### 1. 调研分析（3个并行代理）

代理 1：`Lbot 代码库探索`
- Lbot 集成在 `dexbot_bottom_layer/lbot_catch/` 下
- 无独立 URDF，使用 `config.py` 中的关节参数（7 DOF，±170°）
- 通过 `LbotRobot` Python API 控制（TCP 直连 `192.168.10.21`）
- ROS 接口缺失：无 Service、无 Topic，完全是 Python 直调

代理 2：`xCore vs Lbot 接口差异分析`
- xCore 使用 ROS Service（MoveRtCartesianSegment、GetRobotState）
- Lbot 使用阻塞 Python 调用（move_to_joint_target、get_joint_positions）
- Lbot 无 RT 实时 streaming、无阻抗控制
- 核心发现：Lbot 无 URDF → IK 需用 xCore URDF 或 Lbot 自带 IK

代理 3：`lbot_tool 深度分析`
- `lbot_tool/` 是 Tkinter 桌面调试 GUI，非 ROS 节点
- 通过 `RobotSession`（ThreadPoolExecutor）封装 LbotRobot
- 支持：关节运动、笛卡尔PTP/直线运动、手（TCP/CAN）、路点序列
- 与 xCore ROS 控制框架完全独立

#### 2. 包元数据修复

| 文件 | 问题 | 修复 |
|------|------|------|
| `setup.py` | `package_name='cuttofo_xcore'` | → `'cuttofo_lbot'` |
| `package.xml` | `<name>cuttofo_xcore</name>` | → `<name>cuttofo_lbot</name>` |
| `setup.cfg` | `script_dir=$base/lib/cuttofo_xcore` | → `$base/lib/cuttofo_lbot` |
| `resource/cuttofo_xcore` | 目录名不匹配 | → `resource/cuttofo_lbot` |
| `cuttofo_xcore/` 内部目录 | Python 包目录名未改 | → `cuttofo_lbot/` |

#### 3. 业务逻辑文档重写（business-logic.md）

**关键差异对照**：

| 方面 | xCore 版本 | Lbot 版本 |
|------|-----------|----------|
| 机械臂控制 | ROS Service (move_rt_cartesian_segment) | Python API 直调 (LbotRobot) |
| 运动实时性 | 1kHz RT streaming | 阻塞调用 (block=True) |
| 到位确认 | Action result + Service 回调 | 轮询关节角 |
| 切削执行 | 协调节点内置 RT 循环 | **外部脚本实现，本包不负责** |
| 依赖 | dexbot_interfaces_low | dexbot_bottom_layer (Python SDK) |

**状态机 Phase 3 调整**：
- xCore：协调节点内置 RT 切削循环
- Lbot：仅发布 `/cutting_start` 信号，**外部代码实现切削逻辑**

**新增模块 LbotArmAdapter**：
- 封装 `LbotRobot` TCP 连接
- 提供统一接口：`move_to_joints()`、`get_joints()`、`wait_until_arrived()`

**Phase 2 数据流**：
```
/tofu_state (TofuState)
       ↓
knife_prepare_action_server
       ↓ (LbotArmAdapter)
LbotRobot.move_to_joint_target() → TCP → 机械臂
```

#### 4. xCore 专用文件标记待删除

以下文件为 xCore RT 切削专用，不适用于 Lbot 版本：
- `demo_cut_tofu_xcore_ros.py` — ROS Service 调用，删除
- `demo_cut_tofu_xcore.py` — xCore 专用，删除
- `demo_cut_tofu.py` — xCore 专用，删除
- `demo_cut_smooth_pro6.py` — xCore RT，删除

保留参考：
- `demo_adjust_knife_pose_xcore.py` — 刀姿态参考逻辑
- `prepare_pose_selector.py` — 离线调试工具
- `offline_urdf_kinematics.py` — 复用 xCore URDF

### Lbot 适配关键风险

| 风险 | 影响 | 状态 |
|------|------|------|
| Lbot 无 URDF | IK 求解依赖 xCore URDF，需验证关节结构一致性 | 待验证 |
| Lbot 无 RT 实时控制 | 切削（Phase 3）无法做 1kHz 阻抗控制 | 外部脚本处理，本包不涉及 |
| Lbot API 无 ROS 封装 | 所有节点必须直接调用 Python API | 通过 LbotArmAdapter 封装解决 |
| TCP 连接稳定性 | 连接断开则无法控制 | 待实现重连机制 |

### 下一步工作（M0-M8）

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| **M0** | 包重命名：xcore→lbot（元数据+目录+内部引用） | ✅ 已完成 |
| **M1** | 定义 TofuState.msg + MoveToPreparePose.action | P0 |
| **M2** | 实现 `lbot_arm_adapter.py`（Lbot 控制适配器） | P0 |
| **M3** | 抽取共享模块 `ik_utils.py` + `tofu_geometry.py` | P0 |
| **M4** | 实现 `tofu_state_node` | P0 |
| **M5** | 实现 `knife_prepare_action_server` | P0 |
| **M6** | 实现 `tofu_cut_coordinator_node`（简化版） | P1 |
| **M7** | 删除 xCore 专用文件 | P1 | 无 | ✅ 已完成 |
| **M8** | 端到端测试 | P2 | — | — |

### 修改文件清单

- `src/cuttofo_lbot/setup.py` — 包名修复
- `src/cuttofo_lbot/package.xml` — 包名修复
- `src/cuttofo_lbot/setup.cfg` — 脚本路径修复
- `resource/cuttofo_lbot/` — 资源目录重命名
- `cuttofo_lbot/` — Python 包目录重命名
- `.project-log/business-logic.md` — 完整重写适配 Lbot

---

## 2026-05-09 (续2) — Phase 2 业务逻辑细化 + Lbot 内置 IK 决策

### 背景

在完成包重命名+业务逻辑框架后，进一步明确了 **Phase 2 刀预备位的核心实现路径**。关键发现：**约束不需要在 IK 求解器中执行，而是在求解前通过纯数学编码到目标 euler 角中，Lbot 内置 IK 只需做"给定 6D 位姿求关节角"这一件事**。

### Lbot 内置 IK 能力确认

通过 3 个并行探索代理深度分析了 `lbot_catch/` 下所有 SDK 源码，确认：

| 能力 | Lbot SDK IK | WeightedIK (lbot_catch) | 说明 |
|------|-------------|------------------|------|
| 6D 完整位姿 IK | ✅ `compute_inverse_kinematics()` | ✅ `solve()` | Lbot 原生支持目标 6D pos+eul |
| 关节权重 | ❌ 不支持 | ✅ `custom_weights` | — |
| 姿态容差 | ❌ 不支持 | ✅ `ori_tolerance=[rx,ry,rz]` | — |
| 关节限位 | 控制器内置 | ✅ `_clamp_to_joint_limits()` | 两者均有 |
| 笛卡尔运动 | ✅ `linear_move_to_pose()` | N/A | Lbot 直调 |
| **关键约束** | **约束不在 IK 中执行** | **约束通过旋转矩阵预计算到 euler** | Lbot IK 只需接受完整 6D target |
| Euler 约定 | `LbotEuler(rx,ry,rz)` 弧度 | 内旋 XYZ | 待实测验证 |

### Phase 2 核心设计决策

**约束预计算到 euler 角中，Lbot IK 只需接受 6D target**：

```
tofu_state.tcp_target + edge_dir
    ↓ 纯数学
target_R = build_rotation(plane_angle, edge_dir)  (3×3 旋转矩阵)
    ↓ Rotation.as_euler('xyz')
target_eul = [rx, ry, rz]  (弧度)
    ↓ Lbot 内置 IK
joints = robot.compute_inverse_kinematics(arm, pos, eul, seed)
```

**不需要 URDF、不需要 scipy、不需要 preview 评分**。

### 关键风险：Euler 角约定

`Rotation.as_euler('xyz')` 的旋转顺序必须与 Lbot 的约定一致。待实测验证。

### Phase 2 里程碑更新

| 阶段 | 内容 | 优先级 | 依赖 | 状态 |
|------|------|--------|------|------|
| **M0** | 包重命名：xcore→lbot（元数据+目录+内部引用） | P0 | 无 | ✅ 已完成 |
| **M1** | 定义 TofuState.msg + MoveToPreparePose.action | P0 | 无 | 📋 待实现 |
| **M2** | 实现 `tofu_geometry.py`（纯数学：约束→旋转矩阵→euler） | P0 | 无 | 📋 待实现 |
| **M3** | 实现 `lbot_arm_adapter.py`（含 solve_ik / compute_fk / verify_arrival） | P0 | 无 | 📋 待实现 |
| **M4** | 实现 `tofu_state_node`（订阅 /objects_with_pose → 发布 /tofu_state） | P0 | M1 | 📋 待实现 |
| **M5** | 实现 `knife_prepare_action_server`（Action + Lbot IK + 驱动到位） | P0 | M2, M3, M4 | 📋 待实现 |
| **M5.1** | **Lbot IK 实测验证**：确认 euler 约定、IK 收敛性、FK 对比 | P0 | M3 | ✅ 已完成 — Lbot 使用外旋 ZYX |
| **M6** | 实现 `tofu_cut_coordinator_node`（Phase 2 状态机） | P1 | M5 | 📋 待实现 |

### 文件结构更新（相比 xCore 版本）

| 文件 | 处理 | 原因 |
|------|------|------|
| `offline_urdf_kinematics.py` | ❌ 删除 | Lbot 内置 IK 无需 URDF |
| `ik_utils.py` | ❌ 不创建 | 不再使用 scipy least_squares 做 IK |
| `demo_offline_ik_to_rviz.py` | ❌ 删除 | 不再需要离线 IK+RViz 预览 |
| `tofu_geometry.py` | 🆕 新建 | 约束预计算（纯数学） |
| `lbot_arm_adapter.py` | 🆕 新建 | Lbot 控制适配器 |
| `demo_adjust_knife_pose_xcore.py` | ✅ 保留 | 参考逻辑 |
| `demo_cut_smooth_pro6.py` | ✅ 保留（Phase 3 参考） | 切削逻辑参考 |
| `demo_cut_tofu*.py` | ❌ 删除 | xCore 专用 |
| `prepare_pose_selector.py` | ✅ 保留（离线调试） | 几何算法参考 |

### 关键代码改动点

1. **`lbot_arm_adapter.py`**：封装 `compute_inverse_kinematics()`、`compute_forward_kinematics()`、`move_to_joint_target()`、`verify_arrival()`
2. **`tofu_geometry.py`**：抽取 `build_target_rotation_from_constraints()`、`build_rotation_with_edge_dir()`、`compute_tcp_target_from_corners()`、`reconstruct_corners()`、`compute_edge_dir()`
3. **`knife_prepare_action_server.py`**：调用 Lbot 内置 IK，不再用 scipy
4. **删除**：所有 URDF/scipy/offline_IK 引用

### 修改文件清单

- `.project-log/business-logic.md` — 重写（Phase 2 聚焦 + Lbot IK 决策）
- `.project-log/progress.md` — 本次更新

---

## 2026-05-09 (续3) — 代码架构搭建计划

### 整体文件结构

```
cuttofo_lbot/
├── CMakeLists.txt                        # 🆕 新建: rosidl 编译 msg/action
├── msg/
│   └── TofuState.msg                    # 🆕 M1: 豆腐状态消息 (9字段)
├── action/
│   └── MoveToPreparePose.action          # 🆕 M1: 刀预备位 Action (Goal/Result/Feedback)
│
├── cuttofo_lbot/
│   ├── __init__.py                       # 已有
│   ├── tofu_geometry.py                  # 🆕 M2: 纯数学几何计算 (5函数)
│   ├── lbot_arm_adapter.py               # 🆕 M3: Lbot 控制适配器 (6方法)
│   ├── tofu_state_node.py                # 🆕 M4: 豆腐状态节点 (10Hz发布)
│   ├── knife_prepare_action_server.py     # 🆕 M5: 刀预备位 Action Server
│   ├── tofu_cut_coordinator_node.py      # 🆕 M6: Phase 2 状态机协调
│   │
│   ├── lbot_tool/                        # 保留 (Lbot 调试GUI)
│   ├── prepare_pose_selector.py          # 保留 (离线调试)
│   └── demo_adjust_knife_pose_xcore.py   # 保留 (参考)
│
├── test/
│   └── test_tofu_geometry.py             # 🆕 M2: 几何计算单元测试
│
├── setup.py                              # 更新: entry_points + 数据文件
├── package.xml                           # 更新: msg/action 编译依赖
└── .project-log/progress.md              # 本次更新
```

### 分步实施计划

| 里程碑 | 文件 | 说明 | 可离线? |
|--------|------|------|---------|
| **M1** | `CMakeLists.txt`, `msg/TofuState.msg`, `action/MoveToPreparePose.action`, `package.xml`, `setup.py` | 消息/Action 定义 + 编译配置 | ✅ |
| **M2** | `tofu_geometry.py`, `test/test_tofu_geometry.py` | 纯数学 (5函数 + 单测) | ✅ |
| **M3** | `lbot_arm_adapter.py` | Lbot 控制适配器 (IK/FK/驱动) | ✅ |
| **M4** | `tofu_state_node.py` | 豆腐状态节点 | ✅ |
| **M5** | `knife_prepare_action_server.py` | 刀预备位 Action Server (8步) | ✅ |
| **M6** | `tofu_cut_coordinator_node.py` | Phase 2 状态机协调 | ✅ |

### 关键设计决策

| 决策 | 方案 | 理由 |
|------|------|------|
| 编译系统 | **CMakeLists.txt + setup.py 混合** | ROS2 msg/action 必须用 CMake 编译 |
| euler 约定 | 先假设 `as_euler('xyz')`，M5.1 实测后修正 | 唯一需要实机验证的点 |
| IK 多解 | 20 随机种子重试，取首个有效解 | Phase 2 不需要优选 (切削由外部负责) |
| 连接管理 | 每个 Action Goal 建立/断开连接 | 简单可靠，避免长连接状态管理 |
| 几何计算 | 纯数学模块，与机械臂解耦 | 可在无实机时单测验证 |

### M2: tofu_geometry.py 函数清单

1. `reconstruct_corners(pos, quat, extents)` → 8 角点 (base 坐标系)
2. `compute_tcp_target_from_corners(corners_4, offset_a, vertical_offset)` → TCP 目标点 (7步算法)
3. `compute_edge_dir(corners_4)` → 边方向向量 (Y=0, 归一化)
4. `build_target_rotation_from_constraints(plane_angle_deg)` → 3×3 旋转矩阵 (默认约束)
5. `build_rotation_with_edge_dir(plane_angle_deg, edge_dir)` → 3×3 旋转矩阵 (边对齐)

### M3: lbot_arm_adapter.py 方法清单

1. `connect()` / `disconnect()` — 连接管理
2. `solve_ik(pos, eul, seed=None, num_retries=20)` → 7 关节角 or None
3. `compute_fk(joints)` → (pos, eul)
4. `move_to_joints(target_joints, speed, accel, block=True)` → bool
5. `get_joints()` / `get_pose()` — 状态查询
6. `verify_arrival(target_joints, tolerance_deg, timeout_s)` → (arrived, error_deg)

### M4: tofu_state_node.py 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `class_filter` | `"tofu"` | 过滤目标类别 |
| `offset_a` | `0.03` | 水平偏移 (m) |
| `vertical_offset` | `0.03` | 垂直偏移 (m) |
| `publish_rate` | `10.0` | 发布频率 (Hz) |
| `smoothing_alpha` | `0.4` | EMA 平滑系数 |
| `valid_timeout` | `2.0` | 检测超时标记无效 (s) |

### M5: knife_prepare_action_server.py 执行流程

```
Step 1: 连接 Lbot 控制器
Step 2: 等待有效 /tofu_state (use_vision=True)
Step 3: 构建目标姿态 (约束→旋转矩阵→euler)
Step 4: IK 求解 (当前种子 → 20 随机种子重试)
Step 5: (可选) FK 验证
Step 6: 驱动机械臂 (move_to_joint_target, block=True)
Step 7: 到位确认 (轮询 verify_arrival)
Step 8: 返回 Result
```

### M5 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `arm_host` | `"192.168.10.21"` | Lbot 控制器 IP |
| `ik_retry_count` | `20` | 随机种子重试次数 |
| `arrival_tolerance_deg` | `2.0` | 到位容差 |
| `joint_speed` | `0.3` | 关节运动速度 |
| `fk_verify` | `False` | 是否启用 FK 验证 |

### M6: tofu_cut_coordinator_node.py 状态机

```
IDLE → (收到 /knife_grabbed=True) → WAITING_KNIFE → MOVING_TO_PREPARE → PREPARE_DONE / ERROR
```

### 实施顺序

```
M1 → M2(含单测) → M3 → M4 → M5 → M6
```

全部可离线完成。连接实机后只需做 **M5.1** (euler 约定验证)，可能需要改一行 `as_euler('xyz')`。

---

## 2026-05-09 (续4) — 代码架构搭建完成

### 完成状态

| 里程碑 | 状态 | 说明 |
|--------|------|------|
| **M1** | ✅ 已完成 | `cuttofo_lbot_interfaces` 独立包，`TofuState.msg` + `MoveToPreparePose.action` |
| **M2** | ✅ 已完成 | `tofu_geometry.py` (7函数) + 16 个单测全部通过 |
| **M3** | ✅ 已完成 | `lbot_arm_adapter.py` (6方法)，封装 LbotRobot API |
| **M4** | ✅ 已完成 | `tofu_state_node.py`，订阅 `/objects_with_pose` → 发布 `/tofu_state` |
| **M5** | ✅ 已完成 | `knife_prepare_action_server.py`，Action Server 8步执行流程 |
| **M6** | ✅ 已完成 | `tofu_cut_coordinator_node.py`，Phase 2 状态机 |

### 新建文件

| 文件 | 说明 |
|------|------|
| `cuttofo_lbot_interfaces/msg/TofuState.msg` | 豆腐状态消息 (9字段) |
| `cuttofo_lbot_interfaces/action/MoveToPreparePose.action` | 刀预备位 Action |
| `cuttofo_lbot_interfaces/CMakeLists.txt` | 接口包编译配置 |
| `cuttofo_lbot_interfaces/package.xml` | 接口包依赖 |
| `cuttofo_lbot/cuttofo_lbot/tofu_geometry.py` | 纯数学几何计算 (7函数) |
| `cuttofo_lbot/cuttofo_lbot/lbot_arm_adapter.py` | Lbot 机械臂控制适配器 |
| `cuttofo_lbot/cuttofo_lbot/tofu_state_node.py` | 豆腐状态节点 (ROS2) |
| `cuttofo_lbot/cuttofo_lbot/knife_prepare_action_server.py` | 刀预备位 Action Server (ROS2) |
| `cuttofo_lbot/cuttofo_lbot/tofu_cut_coordinator_node.py` | Phase 2 状态机协调 (ROS2) |
| `cuttofo_lbot/test/test_tofu_geometry.py` | 几何计算单元测试 (16测试) |

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `cuttofo_lbot/package.xml` | 添加 `cuttofo_lbot_interfaces` 依赖 |
| `cuttofo_lbot/setup.py` | 添加 3 个 console_scripts 入口 |

### 编译验证

- `cuttofo_lbot_interfaces` — ✅ colcon build 成功
- `cuttofo_lbot` — ✅ colcon build 成功
- `test_tofu_geometry` — ✅ 16/16 通过
- 所有 Python 模块 — ✅ import 验证通过

### 下一步

- **M5.1**: 连接实机验证 euler 约定 (`as_euler('xyz')` 可能需改为 `as_euler('XYZ')` 等)
- **M7**: 实现外部切削脚本 (Phase 3)
- **M8**: Phase 5 重新就位
- **M10**: ✅ 已完成（xCore 专用文件清理）

---

## 2026-05-09 (续5) — M10 完成：xCore 专用文件清理

### 已删除文件（共 10 项）

| 文件 | 类型 |
|------|------|
| `demo_cut_smooth_pro6.py` | xCore RT 切削 |
| `demo_cut_tofu_xcore_ros.py` | xCore ROS demo |
| `demo_cut_tofu_xcore.py` | xCore 专用 |
| `demo_cut_tofu.py` | xCore 专用 |
| `demo_offline_ik_to_rviz.py` | 离线 IK + RViz |
| `prepare_pose_selector copy.py` | 备份副本 |
| `prepare_pose_selector.py.bak` | 备份文件 |
| `prepare_pose_selector.py.bak2` | 备份文件 |
| `__pycache__/` | Python 字节码缓存 |
| `logs/` | 空日志目录 |

### 保留文件

| 文件 | 原因 |
|------|------|
| `prepare_pose_selector.py` | 离线调试工具 |
| `offline_urdf_kinematics.py` | `prepare_pose_selector.py` 依赖 |
| `demo_adjust_knife_pose_xcore.py` | 刀姿态调整参考 |
| `lbot_tool/` | Lbot 调试 GUI |

---

## 2026-05-09 (续6) — Launch 文件完成

### 文件

`cuttofo_lbot/launch/cuttofu_phase2.launch.py`

### 启动方式

```bash
# 标准启动（全部节点）
ros2 launch cuttofo_lbot cuttofu_phase2.launch.py

# 自定义参数
ros2 launch cuttofo_lbot cuttofu_phase2.launch.py \
  arm_host:=192.168.10.21 \
  text_prompt:=豆腐 \
  plane_angle_deg:=35.0

# 不带 RViz
ros2 launch cuttofo_lbot cuttofu_phase2.launch.py \
  enable_rviz:=false

# 自定义日志目录
ros2 launch cuttofo_lbot cuttofu_phase2.launch.py \
  log_dir:=/tmp/cuttofu_logs
```

### 启动节点清单

| 序号 | 节点 | 说明 |
|------|------|------|
| 1 | RealSense D435i | 相机驱动 + 点云 |
| 2 | SAM3 检测 | 视觉分割 → `/detected_objects` |
| 3 | 姿态估计 | 6D姿态 → `/objects_with_pose` |
| 4 | 豆腐状态节点 | `/objects_with_pose` → `/tofu_state` (10Hz) |
| 5 | 刀预备位 Action Server | IK + 机械臂控制 |
| 6 | 协调节点 | Phase 2 状态机 |
| 7 | RViz2 (可选) | 可视化调试 |

### 日志

通过 `ROS_LOG_DIR` 环境变量控制。不设置则使用 ROS2 默认日志目录 `~/.ros/log/`。

### 修改文件

| 文件 | 修改内容 |
|------|---------|
| `launch/cuttofu_phase2.launch.py` | 🆕 新建 |
| `setup.py` | 添加 `launch/*.launch.py` 安装规则 |

---

## 2026-05-09 (续6) — Launch 文件详细设计

### 文件位置

`cuttofo_lbot/launch/cuttofu_phase2.launch.py`

### 日志方案

```python
log_dir = os.path.join(
    os.path.expanduser('~'), '.cuttofu_logs', 
    time.strftime('%Y%m%d_%H%M%S')
)
os.makedirs(log_dir, exist_ok=True)
SetEnvironmentVariable('ROS_LOG_DIR', log_dir)
```

效果：`~/.cuttofu_logs/20260509_150000/<node_name>-<pid>.log`

### 节点启动序列

| 序号 | 节点 | 包 | 方式 | 关键参数 |
|------|------|-----|------|---------|
| 1 | RealSense + TF + RViz | `ar5_dual_arm_bringup` | `Include` | `enable_realsense=true`, `enable_aruco=false` |
| 2 | SAM3 检测 | `dexbot_middle_layer` | `Node` | `text_prompt=豆腐`, `auto_detect=true` |
| 3 | 姿态估计 | `dexbot_middle_layer` | `Node` | `calibration_file=<路径>` |
| 4 | 豆腐状态节点 | `cuttofo_lbot` | `Node` | `class_filter=tofu` |
| 5 | 刀预备位 Action Server | `cuttofo_lbot` | `Node` | `arm_host=192.168.10.21` |
| 6 | 协调节点 | `cuttofo_lbot` | `Node` | `plane_angle_deg=40.0` |

### Launch 参数（用户可覆盖）

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `log_dir` | `""`（自动时间戳） | 日志输出目录 |
| `arm_host` | `192.168.10.21` | Lbot 控制器 IP |
| `text_prompt` | `豆腐` | SAM3 检测提示词 |
| `calibration_file` | `config/calibration_result.yaml` | 手眼标定文件 |
| `plane_angle_deg` | `40.0` | 刀面倾斜角 |
| `edge_align` | `false` | 边对齐 |
| `offset_a` | `0.03` | 水平偏移 |
| `vertical_offset` | `0.03` | 垂直偏移 |
| `enable_rviz` | `true` | 是否启动 RViz |

---

## 2026-05-09 (续7) — Launch 文件测试 + Bug 修复

### 启动测试结果

执行 `ros2 launch cuttofo_lbot cuttofu_phase2.launch.py enable_rviz:=false`：

| 节点 | 状态 | 说明 |
|------|------|------|
| RealSense D435i | ✅ 进程启动 | 无物理相机时正常报错 |
| SAM3 检测器 | ✅ 启动成功 | 模型加载完成，10Hz |
| 姿态估计 | ⚠️ 退出（空校准文件） | 预期行为，标定后自动恢复 |
| `tofu_state_node` | ✅ 启动成功 | 等待 `/objects_with_pose` |
| `knife_prepare_action_server` | ✅ 启动成功 | 等待 Action |
| `tofu_cut_coordinator_node` | ✅ 启动成功 | 等待 `/knife_grabbed` |

### 修复的问题

| 问题 | 原因 | 修复 |
|------|------|------|
| `perception_params.yaml` 找不到 | `dexbot_bottom_layer` 未安装配置文件到 install 目录 | launch 文件加入 `_find_perception_config()` 容错：文件不存在时跳过，仅传内联参数 |
| `tofu_cut_coordinator_node` crash | `run_phase2()` 使用 `rclpy.spin_once()` 但 `rclpy` 只在 `main()` 局部导入 | 将 `import rclpy` 提升到模块级 |
| 黄色 warning 刷屏 | RealSense 节点收到无关参数 | 无害，不影响功能 |

### 修改文件

| 文件 | 修改 |
|------|------|
| `launch/cuttofu_phase2.launch.py` | 添加 `_find_perception_config()` 容错逻辑 |
| `cuttofo_lbot/tofu_cut_coordinator_node.py` | `import rclpy` 提升到文件级 |

---

## 2026-05-09 (续8) — M5.1 验证脚本完成

### 文件

`cuttofo_lbot/cuttofo_lbot/m51_test_euler_convention.py`

### 测试原理

IK-FK 往返验证：

```
当前关节 → FK → Lbot 原生 euler
    ↓ 用假设约定构造旋转矩阵
IK → FK → 对比位姿是否一致
```

### 测试 8 种 euler 约定

| 约定 | 说明 |
|------|------|
| `xyz` (内旋) | scipy.as_euler 默认 |
| `ZYX` (外旋) | 常见机器人约定 |
| `zyx`, `XYZ`, `xzy`, `XZY`, `yxz`, `YXZ` | 其他可能约定 |

### 执行方式

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
export DEXBOT_ARM_BACKEND=lbot
python3 src/cuttofo_lbot/cuttofo_lbot/m51_test_euler_convention.py
```

脚本只调用 IK/FK 计算接口，不会移动机械臂。

### 根据结果的操作

| 匹配约定 | 操作 |
|---------|------|
| `xyz` | 无需改动 |
| 其他 | 改 `tofu_geometry.py:rotation_to_euler()` 的 `'xyz'` |
| 全部不匹配 | 进一步排查 euler 方向/单位 |

---

## 2026-05-09 (续9) — Lbot SDK C 库加载问题修复

### 问题

运行 M5.1 测试脚本时报错 `LbotAPI未正确初始化`，原因是 Lbot 控制器通信依赖的本地 C 库（`liblbot_api.so`）未安装到 `install` 目录。

### 根因

`find_packages()` 只安装 Python 包（含 `__init__.py` 的目录），`libs/` 目录下的 `.so` 文件被忽略。

### 修复

| 范围 | 文件 | 修改 |
|------|------|------|
| **永久修复** | `dexbot_bottom_layer/setup.py` | 添加 `package_data` 配置，自动安装 `.so` 到正确位置 |
| **代码健壮性** | `lbot_arm_adapter.py` | 双路径导入：优先用完整包路径 `dexbot_bottom_layer.lbot_catch...`，fallback 到 `from lbot` |
| **代码健壮性** | `lbot_arm_adapter.py.__init__` | 提前检查 `_LBOT_API_AVAILABLE`，失败时抛出明确错误信息 |

### 验证

```python
# SDK 库加载成功
正在加载库: .../libs/linux/linux_x64/liblbot_api.so
库加载成功
LbotArmAdapter import OK
LbotArmAdapter init OK
SDK fully available
```

### 修改文件清单

| 文件 | 操作 |
|------|------|
| `src/dexbot_bottom_layer/setup.py` | 修改：添加 `package_data` 规则 |
| `src/cuttofo_lbot/cuttofo_lbot/lbot_arm_adapter.py` | 修改：双路径导入 + 错误处理 |

---

## 2026-05-09 (续10) — 坐标系差异：xCore vs Lbot

### 背景

M5.1 验证时，`build_target_rotation_from_constraints()` 构造的旋转矩阵基于 xCore 坐标系（Y↑, Z→），但 Lbot 使用不同坐标系（Z↑, Y←），导致 IK 全部失败。

### 坐标系差异

| 轴 | xCore | Lbot |
|------|------|------|
| X | 前 | 前 |
| Y | **上** | **左** |
| Z | 右 | **上** |

### 约束重述

- **Constraint 1**: flange_X · base_X = 1（刀脊朝前）
- **Constraint 2**: flange_Z 与 base XY 平面（水平面）的线面角 = plane_angle

### 需要修改的代码

| 函数 | 核心改动 |
|------|---------|
| `extract_top_corners` | 按 Z 而不是 Y 取顶面 |
| `compute_edge_dir` | Y/Z 交换，edge_dir 在 XY 平面（Z=0） |
| `compute_tcp_target_from_corners` | 高度用 Z，水平面 cross 用 [0,0,1] |
| `build_target_rotation_from_constraints` | 新旋转矩阵 |
| `build_rotation_with_edge_dir` | 新旋转矩阵 |
| `rotation_to_euler` | 不变 |

**状态：** 待讨论确认后再修改

---

## 2026-05-09 (续11) — 坐标系映射完成

### 完成内容

根据 Lbot 坐标系（Z↑, X←前, Y←左）重写所有几何计算函数：

| 文件 | 函数 | 改动 |
|------|------|------|
| `tofu_geometry.py` | `extract_top_corners` | 按 Z（高度）排序 |
| | `compute_edge_dir` | 按 Y 最大找左边，强制 Z=0 |
| | `compute_tcp_target_from_corners` | 高度=Z，cross 用 [0,0,1]，水平面=XY |
| | `build_target_rotation_from_constraints` | 全新矩阵（flange_X=base_X, Z与XY平面角=α） |
| | `build_rotation_with_edge_dir` | 全新矩阵（edge_dir 在 XY, flange_X=edge_dir） |
| `tofu_state_node.py` | `_on_objects` | top_y → top_z |
| `test/test_tofu_geometry.py` | 16 tests | 全部适配 Lbot 坐标系 |

### 验证

- `colcon build` — ✅ 成功
- `pytest` 16/16 — ✅ 全部通过

---

## 2026-05-09 (续12) — M5.1 Euler 约定验证完成

### 测试过程

| 步骤 | 命令 | 结果 |
|------|------|------|
| 1 | 归零位姿，rpy=15,0,0 | ❌ IK 全部失败（奇异位姿） |
| 2 | 移动 J2≈28.6°，非零位姿 | 到位 |
| 3 | rpy=0,0,0 | ✅ IK 全成功但无区分度 |
| 4 | rpy=5,0,0 | ✅ **仅有 ZYX 成功，其余 7 种全部失败** |

### 结论

**Lbot 使用外旋 ZYX euler 约定**（绕固定世界轴，先 Z 后 Y 后 X）。

scipy 的 `Rotation.from_euler('ZYX', [rz, ry, rx]).as_matrix()` 与此一致。

### 需修改

`tofu_geometry.py:rotation_to_euler()`: `'xyz'` → `'ZYX'`

### 修改文件

| 文件 | 改动 |
|------|------|
| `tofu_geometry.py:108` | `convention="xyz"` → `convention="ZYX"` |

---

## 2026-05-09 (续13) — 代码审查 + Bug 修复

### 审查范围

全部 7 个源文件 + 单测 + launch 文件

### 发现并修复

| # | 位置 | 严重度 | 问题 | 修复 |
|------|------|--------|------|------|
| 1 | `knife_prepare_action_server.py:147` | 🔴 严重 | `rotation_to_euler(target_R, "xyz")` — 传入了已过时的 `"xyz"` 约定，M5.1 确认 Lbot 使用 `ZYX` | 删掉 `"xyz"` 参数，使用默认 `"ZYX"` |
| 2 | `tofu_state_node.py:107` | 🟡 中等 | `state.pose` 使用原始未平滑位姿，EMA 平滑后的 `smoothed_pos` 未写回 | 平滑后对 `state.pose.position` 写入平滑值 |
| 3 | `tofu_state_node.py:115` | 🟡 中等 | `top_y` 字段存储 Z 值（Lbot 下 Z=高度），命名误导 | 加注释说明 |
| 4 | `test_tofu_geometry.py:154-160` | 🟡 中等 | 单测只验证了 `"xyz"` 约定的 roundtrip，未覆盖新的默认 `"ZYX"` | 新增 `test_roundtrip_default_zyx` 测试 |
| 5 | `tofu_cut_coordinator_node.py:128` | 🟢 轻微 | `import rclpy` 在 `main()` 内局部导入，与文件顶部导入重复 | 删除冗余导入 |

### 验证

- `colcon build` — ✅
- `pytest` 17/17 — ✅

---

## 2026-05-09 (续15) — 手眼标定工具分析

### 现有标定工具链

| 组件 | 位置 | 说明 |
|------|------|------|
| 标定主节点 | `dexbot_toolbox/calibration/hand_eye_calibration_node.py` (2511 行) | 手动+自动，AX=YB 求解，结果保存 |
| ArUco 检测 | `dexbot_toolbox/calibration/aruco_detector_node.py` | 检测标定板 → `/aruco/pose` |
| TF 发布 | `dexbot_toolbox/calibration/hand_eye_static_tf_publisher.py` | 读 YAML → 广播 base→camera 静态 TF |
| Launch | `dexbot_bringup/launch/calibration_manual_withUI.launch.py` | 一键启动标定系统 |
| TCP 偏移标定 | `dexbot_toolbox/calibration/calibrate_tool_offset.py` | 已支持 Lbot（`--ip 192.168.10.21`）|

### 兼容性架构

标定节点 → `RobotController`(xcore_controller) → `LbotRobot`(facade) → 分派到 Lbot backend：

```
hand_eye_calibration_node
  → RobotController (xcore_controller)
    → LbotRobot(self.ip)
       ├── DEXBOT_ARM_BACKEND=xcore → XCore backend (旧硬件)
       └── DEXBOT_ARM_BACKEND=lbot  → Lbot backend (当前硬件 ✅)
```

核心算法（ArUco 检测 + AX=YB 求解 + OpenCV + scipy LM 优化）与机械臂类型无关。

### 需要改的参数（仅 3 项）

| 参数 | xCore 值 | Lbot 值 |
|------|---------|--------|
| `robot_ip` | `192.168.2.84` | `192.168.10.21` |
| `DEXBOT_ARM_BACKEND` | `xcore`（默认） | `lbot` |
| `manual_enable_drag` | `true` | `false`（拖拽仅 xCore 支持）|

可选：`robot_base_frame` 改为 `base_link`，运行 `lbot_controller_node` 替代 `xcore_controller_node`。

### 标定命令

```bash
export DEXBOT_ARM_BACKEND=lbot
ros2 launch dexbot_bringup calibration_manual_withUI.launch.py \
  robot_ip:=192.168.10.21 \
  arm_type:=right \
  launch_realsense:=true \
  manual_enable_drag:=false \
  marker_length:=0.038 \
  output_file:=/home/tbl/Project/dexbot_ros2_ws/src/config/calibration_result_lbot.yaml
```

### 标定后 Phase 2 接入

```bash
ros2 launch cuttofo_lbot cuttofu_phase2.launch.py \
  calibration_file:=/home/tbl/Project/dexbot_ros2_ws/src/config/calibration_result_lbot.yaml
```

---## 2026-05-09 (续14) — 多代理全面审查 + 第二轮 Bug 修复

### 审查方式

5 个并行代理分别审查：几何数学、Lbot 适配器、ROS2 节点、Launch 文件、端到端集成

### 新发现并修复

| # | 文件:行 | 严重度 | 问题 | 修复 |
|------|---------|--------|------|------|
| 1 | `knife_prepare_action_server.py:210` | 🔴 | `position_error_mm = error_deg` 把角度值存进 mm 字段 | 改为 `0.0`（到位验证通过即误差接近零） |
| 2 | `knife_prepare_action_server.py:103-217` | 🔴 | `goal_handle.abort()` + `return result` 产生模棱两可状态（abort 后 return result=SUCCEEDED） | 所有失败路径返回 `MoveToPreparePose.Result()` |
| 3 | `knife_prepare_action_server.py:66` | 🟡 | `_wait_for_tofu_state` 先 `clear()` Event 再检查已有状态，每次浪费 500ms | 先检查已有状态，无数据时才 `clear()+wait()` |
| 4 | `lbot_arm_adapter.py:65` | 🟡 | `connect()` 部分失败后 facade 实例未清理 | 用局部变量先连接，成功才赋值 `self._robot` |
| 5 | `lbot_arm_adapter.py:60` | 🟡 | SDK 调用无异常包裹 | 添加 `try/except` 包裹 `robot.connect()` |
| 6 | `tofu_geometry.py:65` | 🟡 | `compute_tcp_target_from_corners` 缺少 `l_raw` 零范数守卫 | 添加 norm 检查，零时 fallback 到 `[0,-1,0]` |
| 7 | `package.xml` | 🟡 | 缺少 `<exec_depend>dexbot_middle_layer</exec_depend>` 和 `realsense2_camera` | 添加两个依赖 |

### 验证

- `colcon build` — ✅
- `pytest` 17/17 — ✅

---

## 2026-05-09 (续16) — 标定 GUI 设计（新包 cuttofo_calibration）

### 目录结构

```
src/cuttofo_calibration/
├── package.xml / setup.py / setup.cfg
├── launch/calibration_gui.launch.py
├── config/default_params.yaml
├── data/                        (采样数据自动保存)
├── calibrator_design.md         (完整设计文档 ~1100 行)
└── cuttofo_calibration/
    ├── business/                 (业务逻辑，无界面依赖)
    │   ├── calibration_client.py  (封装 hand_eye 的 7 个 Service)
    │   ├── camera_stream.py       (订阅 /camera 图像)
    │   ├── aruco_monitor.py       (订阅 /aruco/pose + 稳定判定)
    │   └── sample_manager.py      (采样管理 + CSV + RMSE)
    └── view/                     (界面层，仅依赖 business)
        ├── calibration_gui.py     (主窗口 + ROS spin 线程)
        ├── camera_panel.py        (左侧 75%：实时画面)
        ├── control_panel.py       (右侧 25%：操作面板)
        └── metrics_bar.py         (底部 RMSE 状态栏)
```

### 设计原则

- 业务/界面文件级分离
- 不修改现有标定节点，通过 ROS2 Service/Topic 通信
- Tkinter + OpenCV → PIL → Canvas 渲染
- MultiThreadedExecutor 独立线程 spin
- 75% 画面 : 25% 控件比例

### 详细设计

见 `src/cuttofo_calibration/calibrator_design.md`

---

## 2026-05-09 (续17) — 标定 GUI 包实现完成

- cuttofo_calibration 包：13 源文件 + launch + 设计文档
- 两轮多代理审查（7 代理、累计修复 16 项 BUG）
- 上电/下电按钮控制 Lbot，标定节点 `force_sdk_connect_on_manual_start:=true` 单 SDK 连接
- 详细进度见 `src/cuttofo_calibration/.project-log/`

---

## 2026-05-09 (续18) — 🔴 Euler 分量映射 BUG 修复

### 发现

实机测试 `plane-angle=-80` 理论上绕 X 轴旋转 10°，实际机械臂绕 Z 轴旋转。

### 根因

`lbot_arm_adapter.py` 的 euler 分量映射错误——scipy ZYX 输出 `[rz, ry, rx]`，但 `LbotEuler(eul[0],eul[1],eul[2])` 把 `rz` 当作 roll(绕X)、`rx` 当作 yaw(绕Z)，导致 roll/yaw 互换。

### 修复

| 方法 | 修改 |
|------|------|
| `solve_ik:109` | `_LbotEuler(eul[0],eul[1],eul[2])` → `_LbotEuler(eul[2],eul[1],eul[0])` |
| `compute_fk:149` | `(eul.x,eul.y,eul.z)` → `(eul.z,eul.y,eul.x)` |
| `get_pose:180` | 同上 |

### 验证

实机测试 `plane-angle=-80`：

```
目标旋转矩阵: Rx(10°) — 绕 X 轴转 10°
FK 位置误差: 0.0000 mm ✓
FK 旋转误差: 0.000000 ✓
到位验证: 0.045° ✓
```

物理效果符合预期，修复正确。

---

## 2026-05-11 - Lbot Phase 2 完成 + xCore 迁移分析

### Lbot Phase 2 状态: ✅ 已完成

Lbot 机械臂 Phase 2 框架已完成端到端实测验证。

**完成的功能**:
- `tofu_geometry.py` — 7 个几何函数，17 个单元测试
- `tofu_state_node.py` — 订阅 `/objects_with_pose`，发布 `/tofu_state`，EMA 平滑
- `knife_prepare_action_server.py` — 8 步 Action Server，IK → 移动 → 到位验证
- `tofu_cut_coordinator_node.py` — Phase 2 状态机
- Launch 文件 `cuttofo_phase2.launch.py` — 一键启动所有节点

**关键里程碑**:
- M5.1: 确认 Lbot 使用 ZYX extrinsic 外旋 ✅
- Euler bug 修复: `LbotEuler(eul[2], eul[1], eul[0])` ✅
- 实机端到端 IK/FK 验证 ✅

### xCore 迁移分析: ✅ 已完成

详见 `cuttofo_xcore/.project-log/xcore_migration_plan.md`

**关键差异**:

| 方面 | Lbot | xCore |
|------|------|-------|
| 坐标系 | Z↑, X→, Y← | Y↑, X→, Z→ |
| 欧拉角 | ZYX extrinsic | **XYZ intrinsic（= ZYX extrinsic）** |
| 控制 | SDK 直调 | ROS2 Service |
| IK | SDK 内置 | URDF + scipy |

**重要发现**: xCore 的 XYZ intrinsic 约定比 Lbot 更简单——不需要 swap 映射！scipy `as_euler("xyz")` 直接对应 `LbotEuler(x=rx, y=ry, z=rz)`。

### 下一步

等待用户确认迁移方案后，开始实施 M1 → M2 → M3 → M6 → M4 → M5。
