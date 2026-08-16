# 手眼标定（相机外参）启动问题清单

## 2026-08-16 新机器人/新相机覆盖说明（优先于下方旧记录）

- 当前机器人已更换，旧机器人的左右臂 IP 和旧相机型号记录仅作历史参考，**不要直接套用**。
- 本次标定相机已确认为 `Orbbec Gemini 2`：序列号 `AY3Z33100DJ`，USB PID `2bc5:0670`。
- ArUco 板不变：`DICT_6X6_250`，黑色方格外沿 `0.13 m`。
- 新机器人左臂 IP 已确认为 `192.168.2.160`。
- 新机器人右臂 IP 当前未知，标定前需要现场确认；`robot_params.yaml` 中旧左臂 `192.168.2.159`、旧右臂 `192.168.2.160` 不应继续作为事实使用。
- 当前 `camera_env` 缺少 Gemini 2 所需 `extensions/frameprocessor/libob_frame_processor.so`，深度流验证需要先补该个人环境扩展；机器上已有扩展位于 `/home/tbl/.local/lib/python3.10/orbbec-sdk/extensions/`。
- 相机参数和内参配置尚未更新到新相机，当前不能直接沿用 `camera1_params.yaml` / `camera1_ost.yaml` 跑标定。

## 2026-08-15 实测可用操作手册（优先阅读）

### 运行环境

- 必须从 `kitchen_robot_home` 启动，因为 `robot_driver` 需要读取 `.localconfig` 的 SDK 路径。
- 使用本机相机隔离环境，**不要 `conda activate robot`**：

```bash
cd /home/tbl/Project/boss_electrics/kitchen_robot_home
unset PYTHONPATH
source /home/tbl/camera_env/calibration_env.sh
```

`calibration_env.sh` 已依次加载 ROS Humble、主线 `install/setup.bash`、`camera_env.sh`，包含 `PYTHONNOUSERSITE=1`、系统 `numpy 1.21.5`、`cv2 4.5.4` 和 `pyorbbecsdk 2.7.6`。

### 固定事实

- 位型：相机固定、机械臂末端装 ArUco 标记，eye-to-hand，标定节点自动移动机械臂采样。
- 标定板：6x6 字典，黑色外沿边长 `0.13 m`。
- 左右臂 IP 由 `robot_params.yaml` 提供：左臂 `192.168.2.159`，右臂 `192.168.2.160`。
- 当前标定 launch 走 `/robot_driver/get_arm_pose` 和 `/robot_driver/move_cartesian`，**不再需要手动 `export DEXBOT_ROBOT_IP`**。
- 相机物理位置在左臂、右臂两次标定之间必须保持不变。
- 同一臂标定前必须停止该臂其他控制链，现场保留急停，工作空间清空。

### 左臂启动命令

左臂采样范围沿用历史成功记录；如果当前左臂 TCP 位姿不同，按 launch 日志里的 TCP Pose 调整 `x/y/z`：

```bash
cd /home/tbl/Project/boss_electrics/kitchen_robot_home
unset PYTHONPATH
source /home/tbl/camera_env/calibration_env.sh

ros2 launch dexbot_bringup calibration.launch.py \
  arm_type:=left \
  output_file:=/home/tbl/Project/boss_electrics/kitchen_robot_home/src/dexbot_bringup/config/calibration/left_calibration_result.yaml \
  marker_length:=0.13 \
  x_min:=0.15 \
  x_max:=0.6 \
  y_min:=0.1 \
  y_max:=0.5 \
  z_min:=-0.5 \
  z_max:=0.3 \
  enable_viewer:=true
```

### 右臂启动命令

右臂当前典型 TCP 为 `pos=[0.442, -0.012, 0.010]`，`y` 是负值；launch 默认 `y=[0.1, 0.4]` 会把候选点全部过滤掉，所以右臂必须显式覆盖 `y` 范围：

```bash
cd /home/tbl/Project/boss_electrics/kitchen_robot_home
unset PYTHONPATH
source /home/tbl/camera_env/calibration_env.sh

ros2 launch dexbot_bringup calibration.launch.py \
  arm_type:=right \
  output_file:=/home/tbl/Project/boss_electrics/kitchen_robot_home/src/dexbot_bringup/config/calibration/right_calibration_result.yaml \
  marker_length:=0.13 \
  x_min:=0.2 \
  x_max:=0.7 \
  y_min:=-0.4 \
  y_max:=0.2 \
  z_min:=-0.3 \
  z_max:=0.3 \
  enable_viewer:=true
```

如果右臂当前位姿变化，以日志中的 `TCP Pose (after compensation)` 为准微调范围，确保候选点数大于 10。

### 触发与监控

另开终端，同样使用 `calibration_env.sh`：

```bash
source /home/tbl/camera_env/calibration_env.sh
ros2 service call /calibration/start_calibration std_srvs/srv/Trigger "{}"
```

监控：

```bash
ros2 topic echo /calibration/status
```

启动后先确认：

```bash
ros2 topic list | rg '/camera/color|/aruco|/calibration'
ros2 service list | rg '/robot_driver|/calibration'
```

正常应看到真实相机启动日志 `Camera backend: real device (Orbbec Gemini 335L)`，并能收到 `/aruco/pose`。hand-eye 日志应出现 `生成 N 个笛卡尔候选点`，`N` 至少大于 10。

### 常见问题

- `import cv2` 报 NumPy 2.x 兼容错误：没有使用 `calibration_env.sh`，或手动激活了 robot conda 环境；重新开终端并执行上面的环境命令。
- `GetArmTorques` 导入失败：`install/dexbot_interfaces` 是旧构建产物，需要重建：

```bash
cd /home/tbl/Project/boss_electrics/kitchen_robot_home
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --symlink-install --packages-select dexbot_interfaces --allow-overriding dexbot_interfaces
```

- 相机日志出现 synthetic fallback：没有加载 `/home/tbl/camera_env`，不是相机硬件问题。
- 标定报 `候选点数量偏少: 0/10` / `样本数不足: 0/10`：采样范围没有覆盖当前 TCP；右臂尤其注意 `y` 应为负值范围。
- `No module named 'can'` 和 `SafetyHeartbeat 失联`：当前手眼标定不依赖灵巧手和 safety 节点，可继续；后续全链路启动时再处理。

### 标定结果与下一步

- 左臂结果：`kitchen_robot_home/src/dexbot_bringup/config/calibration/left_calibration_result.yaml`
- 右臂结果：`kitchen_robot_home/src/dexbot_bringup/config/calibration/right_calibration_result.yaml`
- 中心结果：`kitchen_robot_home/src/dexbot_bringup/config/calibration/center_calibration_result.yaml`
- 视觉运行时已在本机 `.localconfig` 启用：`calibration_path` 指向中心结果，`right_calibration_path` 指向右臂结果；左臂结果保留为中心坐标生成源文件。
- 左右各跑完一次且相机位置未移动后，用 `scripts/generate_robot_center_frames.py` 生成中心坐标系文件，再配置感知 `calibration_path` 和 `pan_pour` 参数。

### 2026-08-15 实测结果

- 右臂标定成功：`samples=12`，平移 RMSE `0.001082 m`，旋转 RMSE `0.4482°`，结果已保存到 `right_calibration_result.yaml`。
- 标定过程中部分候选点报 `Motion timeout after 30.0 seconds` 并被跳过，这是单个候选位姿不可达/未收敛，不影响最终结果；`min_samples=10`，本次 12 个有效样本满足要求。
- 标定完成后的“返回起始 TCP 位姿”也可能超时；结果已保存，超时不表示标定失败，但需要人工确认右臂停在安全位后再关闭 launch。
- 左臂历史成功结果：`samples=22`，平移 RMSE `0.001825 m`，旋转 RMSE `0.805°`。
- 如果后续想减少右臂运动超时，可把右臂起始位姿放到更居中的可达区域，并进一步缩小采样范围；当前结果不需要为提升样本数量而强制重跑。

### 2026-08-15 中心坐标系计算完成

左右标定文件质量检查通过后，已用现有脚本计算中心坐标系，结果保存在：

- `kitchen_robot_home/src/dexbot_bringup/config/calibration/center_calibration_result.yaml`
- 生成明细 `center_frames.yaml` 仍保留在 `/home/tbl/Project/boss_electrics/标定结果/`

主要结果：

- 肩宽（Y 轴投影）：`0.188627 m`；自由三维基线长度 `0.189393 m`。
- 左臂 `toolset.ref.trans`：`[0.0, -0.094313551, 0.0]`；右臂：`[0.0, 0.094313551, 0.0]`。
- `T_center_cam` 平移：`[0.1179409, 0.025820205, 0.270310843]`。
- 左右标定推算相机位姿的旋转残差 `2.848°`，位置偏差约 `17 mm`；正式执行前建议用固定点或已知物体坐标验证一次。

视觉运行时 `calibration_path` 已指向 `center_calibration_result.yaml`。中心坐标已落位到 `pan_pour.left_base_from_center`（`translation=[0, 0, -0.094313551]`，`rpy=[pi/2, 0, 0]`）；`robot_params.yaml` 的左右臂 `toolset.end/ref` 保持 identity，避免驱动与 planner 重复换算。`pan_pour.configured` 仍必须保持 `false`，直到 `tcp_pan`、点位和现场验证完成。

## 目标

做一次相机外参（手眼）自动标定，输出 `T_base_cam`，为正式 V1（`pan_pour.configured`）的真机标定与后续中心坐标系统一提供外参。当前进入"逐个解决前置问题"阶段，先冻结问题清单，再逐步推进。

## 手眼位型（已确认的现有实现口径）

- 现有 `calibration.launch.py` + `dexbot_toolbox` 实现是：**相机固定 + 机械臂末端刚性安装 ArUco 标记**，标定节点自动移动机械臂采样。
- 约束方程：`T_base_tcp_i @ T_tcp_marker = T_base_cam @ T_cam_marker_i`，解出 `T_base_cam`（相机到机械臂 base 的外参）。
- 用户描述"手在眼上"对应的是"手上 marker 在固定相机视野内移动、相机不动"，与现有实现一致；不是"相机装在手上"的 eye-in-hand。启动前需再确认物理装法。
- **2026-08-07 用户纠正（最终口径）**：相机实际安装在机器人头部，是 **eye-to-hand（眼在手外）**，不是 eye-in-hand。机械臂末端装 ArUco 标记、相机固定移动臂采样，与现有 `calibration.launch.py` 解 `T_base_cam` 的实现一致。锁死此口径，后续标定按 eye-to-hand 执行。

## 问题清单（按解决顺序编号）

1. **工具包未安装** `CAL-01`（✅ 2026-08-07 完成）：已把 `dexbot_toolbox`（`ros-humble-dexbot-toolbox 1.0.0-0jammy`）加入 `VERSIONS.yaml`，运行 `sudo bash scripts/setup_apt_repos.sh` 安装成功；`verify_versions.sh` 7/7 通过，包位于 `/opt/ros/humble`，含 `aruco_detector_node` / `hand_eye_calibration_node` / `camera_viewer_node`。
2. **话题接线**（CAL-02，✅ 复核确认实际无匹配问题）：基于已安装 1.0.0 源码确认真实契约——`aruco_detector_node` 硬编码订阅绝对话题 `/camera/color/image_raw`、`camera_info_topic` 默认 `/camera/color/camera_info`；`CameraDriverNode` 发布绝对话题 `/camera/color/image_raw`、`/camera/color/camera_info`（`CameraDriverNode.py` 143-145 行）；`camera_viewer_node` 默认 `camera_ns=camera` 订阅 `camera/color/image_raw`。因都是绝对话题（以 `/` 开头），launch 中相机节点 `namespace='camera1'` 不会改变绝对话题名，ArUco/viewer 订阅的 `/camera/color/*` 与相机发布一致，**无需改 launch 话题 remap**。之前按 715 旧版（相对名 `color/image_raw`）推断的不匹配在 1.0.0 上不成立。真机启动后仍用 `ros2 topic list/info` 复核 `/camera/color/image_raw`、`/camera/color/camera_info`、`/aruco/pose` 有数据。
3. **相机内参不一致**：launch 以 `camera1_ost.yaml`（1280x720、fx≈610）作为 `ost_yaml` 内参源，但当前 `camera1_params.yaml` 激活的是 RealSense D435 640x480（fx≈911）。分辨率/内参不匹配会导致 ArUco 位姿算错，需统一。
   - **2026-08-07 实机硬件识别（CAL-03 定案）**：唯一 USB 相机是 **Orbbec Gemini 336L**（VID `2bc5`/PID `0x0807`，SDK 名 `Gemini 336L`，sn `CPCAC53000FP`），不是 RealSense，也不是 335L。`/dev/video0..7` 全部为 `uvcvideo: Orbbec Gemini 336L`。
   - SDK 枚举（pyorbbecsdk）：COLOR 最高 **1280x720**（YUYV/NV12/MJPG，无 1080）；DEPTH 最高 1280x800/1280x720（Y16）。COLOR 640x400 原生内参 fx≈304.5/cx≈321.2/cy≈197.3（换算到 1280 宽 ≈ fx≈609〜611），与 `camera1_ost.yaml`（1280x720，fx≈610.8，cx≈644.6，cy≈359.9）一致 → **OST 就是这台相机 1280x720 的内参**。
   - 结论：`camera1_params.yaml` 应从 `realsense_d435`（640x480、fx≈911）切回 **`camera_type: gemini335l`**（1280x720、`camera_info_source: ost_yaml`、`calibration_file: package://dexbot_bringup/config/cameras/camera1_ost.yaml`），即文件中已注释的 Gemini 块。驱动类名是 `Gemini335LCamera`（.deb 版本）但基于同一套 Orbbec pyorbbecsdk，336L 同样可驱动。
   - **环境问题（2026-08-07 已解决，本地隔离方案，不改仓库）**：`~/.local`（user-site）装有 numpy 2.2.6，与系统 cv2 4.5.4（基于 numpy<2 编译）冲突 → `import cv2` 报 `numpy.core.multiarray failed to import`；而 `pyorbbecsdk` 只在 `~/.local`。
     - 验证：把 `pyorbbecsdk/` 包 + `.so` + `libOrbbecSDK*.so` + `OrbbecSDKConfig.xml` 拷贝到独立目录，用 `PYTHONNOUSERSITE=1` + `PYTHONPATH=<隔离目录>` 跑系统 numpy 1.21.5 + cv2 4.5.4，`import pyorbbecsdk` 正常，实测采到 1280x720 MJPG 真实帧、`cv2.imdecode` 得 BGR(720,1280,3)。
     - 落地：`/home/tbl/camera_env/`（用户目录，不进仓库），含隔离包与两个脚本。用法：`source /home/tbl/camera_env/calibration_env.sh`（sources ROS Humble + 主线 workspace + 相机隔离 env）后按原流程 `ros2 launch dexbot_bringup calibration.launch.py ...`。
     - 相机节点实机验证（`camera_driver_node`，ns `/camera1`）：`Camera backend: real device (Orbbec Gemini 335L)`，1280x720@15，加载 OST 内参（1280x720），发布 `/camera/color/image_raw` `/camera/color/camera_info` `/camera/depth/image_raw`，帧处理 ~13-25ms。
     - 已发现非致命告警：`.deb` 驱动按 `Gemini335LCamera` 尝试加载深度 preset `"Medium Density"`，336L 无该命名 → `Invalid preset name`（仅 WARN，深度仍以默认 preset 出流）。属 `.deb` 驱动内部，黑盒不改。
   - 当前 `dexrob_full.launch.py` 的相机节点（`camera_driver_node`/`camera_viewer`/`perception`）默认**注释未启用**，标定时会由 `calibration.launch.py` 单独拉起相机链路。
4. **标定板参数需确认**：launch 默认 `marker_length=0.13`、`DICT_6X6_250`，必须与实际 ArUco 板边长/字典一致；参考的 715 仓库默认是 0.038 / DICT_4X4_50，不能照抄。项目仓库内无标定板图片/配置，需用户提供实际板的边长（米）与字典（几行）。`dictionary` 在 `calibration.launch.py` 中写死（`cv2.aruco.DICT_6X6_250`），若实际不是 6X6 需改 launch 源码。
   - **2026-08-07 字典检测（CAL-04 定案）**：用户提供标定板照片 `29ab27ed06c7f3f7461dca3e835f4d3c.jpg`（896x867，单块大 ArUco 特写，黑格占满画面）。用 `PYTHONNOUSERSITE=1` + 系统 cv2 4.5.4/numpy 1.21.5 逐字典检测：
     - `DICT_6X6_50`：1 个 marker，id=0，黑色外沿边长均值约 787.8 px（896 宽图）
     - `DICT_6X6_250`：1 个 marker，id=0，黑色外沿边长约 473/787.8 px
     - `4X4/5X5/7X7/ARUCO_ORIGINAL/APRILTAG_*`：0 个
     - 结论：字典为 **6X6**，与 launch 默认 `DICT_6X6_250` 兼容，**launch 的 dictionary 无需修改**；只用按实测黑色方格外沿边长改 `marker_length`。
   - **关键限制**：像素尺寸≠物理尺寸。单块特写无法用图片分辨率换算真实毫米边长，必须由用户用尺/卡尺量黑色方格外沿边长 `L`(mm)，launch `marker_length:=L/1000`。
   - **2026-08-07 用户实测边长（CAL-04 完成）**：用户实际测量，标定板整体为正方形，黑色外沿边长 **13 cm（130 mm）**，与 `calibration.launch.py` 默认 `marker_length=0.13` 完全一致。启动标定时无需再传 `marker_length`（显式传 `marker_length:=0.13` 亦可）。
   - **鲁棒性提示**：当前板疑似单片单标记，单标记姿态估计精度/鲁棒性弱于多标记板；若真是单片，标定时采样姿态覆盖要尽量大（多角度、多位置），并按真实厚度/作业空间设置采样范围。若实际是多标记板，需用户补拍能看到多个标记的照片以确认识别。
5. **机器人 IP（2026-08-07 已确认）**：标定节点连 SDK 的 IP 从 `$DEXBOT_ROBOT_IP` 读取；左臂 `192.168.2.159`、右臂 `192.168.2.160`（本次标定用左臂 → export `DEXBOT_ROBOT_IP=192.168.2.159`）。注意 `calibration.launch.py` 内 `robot_driver_node` 走 `robot_params.yaml` 的 IP，需与上面保持一致；真机标定前应停掉 `dexrob_full` 主链路，避免两条控制链抢同一臂。
6. **结果写入与中心统一链路（2026-08-07 已确认左右+中心可闭环）**：标定输出写 `T_base_cam` / `T_tcp_marker` / RMSE；**可以左右臂各标一次，再把左右结果统一到机器人中心坐标系**。链路已存在并有配套脚本：
   - `reset_robot_params_frames.py --reset-path <robot_params.yaml>`：把左右臂 `base_frame`/`toolset.ref` 重置为旧基座约定（左 `rpy=[-pi/2,0,0]`、右 `[pi/2,0,0]`、`ref.trans=[0,0,0]`）。**标定前必须先跑**，否则 `generate_robot_center_frames.py` 解释 `T_base_cam` 的基线会被现有非零 `ref.trans` 污染。
   - `calibration.launch.py arm_type:=left/right`：左右臂各跑一次，分别输出 `left_calibration_result.yaml` / `right_calibration_result.yaml`。**左右两次之间相机物理位置必须保持不动**（利用“同一相机位置”约束求中心），还需 `export DEXBOT_ROBOT_IP=<对应臂 IP>`。
   - `generate_robot_center_frames.py --left-calibration ... --right-calibration ... --robot-params ...`：输入左右 `T_base_cam`，求左右基座连线中点（默认投影到 Y 轴=肩部中心），把中心偏移写入 `robot_params.yaml` 左右 `toolset.ref.trans`，把 `T_center_cam` 保存到 `dexbot_perception/config/calibration_result.yaml`，并输出旋转残差/肩宽诊断。
   - 完成后按需填 `pan_pour_params.yaml` 的 `left_base_from_center` / `configured`，并把 `pan_pour.configured` 置 `true`。
   - **当前 `robot_params.yaml` 现状（2026-08-07 复查）**：左右 `base_frame.rpy` 已是 `[-pi/2,0,0]`/`[pi/2,0,0]`，但 `toolset.ref.trans` 携带既有肩部偏移（左 `[0,-0.0763,0]`、右 `[0,0.0763,0]`），`pose_frame_rot_x_deg` 为 0 —— 与 reset 目标值（左 `-90`/右 `90`、ref 归零）不一致，**正式标定前需先跑 reset 脚本对齐基准**。
7. **肘部搜索 7-DOF 校验失败（2026-08-07 已定位，待修复）**：双臂、SDK、`get_arm_pose` 全部连接正常后，自动标定 17 个采样姿态**全部运动失败**，报错：
   ```
   Cartesian control with elbow range failed: arm-angle range search requires 7-DOF robot, got 13
   ```
   标定结果为 `0 个有效样本 / 样本数不足: 0/10，标定失败`。
   - **根因（已真机坐实，左臂 `192.168.2.159`）**：`jointPos` 返回 **13 个值 = 7 个真实臂关节 + 6 个外部轴（占位全 0）**。实测：
     ```
     jointPos ec={'ec':0,'message':'success'} len=13
     vals=[0.4086, 1.0454, -0.3098, 1.2922, -0.1901, 0.4047, -0.2947, 0,0,0,0,0,0]
     ```
     即当前 SDK `xCore 0.5.1.ar_12` 配合 Er Pro 机型返回 7+6 格式；而 `ElbowRangeSearcher.initialize()` 用 `len(jointPos)` 当自由度（`self._joint_count = len(self._get_current_joints())`），得到 13，随后 `if self._joint_count != 7: raise RuntimeError(...)` 直接抛错。
   - **结论**：不是脚本逻辑写错，而是"机型 + 当前 SDK 版本"把 `jointPos` 返回成 7+6 格式，脚本的 `len()==7` 校验对该返回格式不兼容。
   - **2026-08-07 用户定性（最终）**：是 xCore SDK 版本用错。应使用 `kitchen_robot_home/src/sdk/xcoresdk_python-v0.7.1.ar_6`，并把所有 SDK 引用路径从 `v0.5.1.ar_12` 切换过去（`.localconfig`、arm_api、robot_motion_executor 两个 util+测试、GUI 五处、README 目录树）；`v0.5.1.ar_12` 目录已从工作区删除（Trash）。
   - 验证：全局 `rg '0\.5\.1\.ar_12' gui boss_electrics` 无残留；新 SDK `xCoreSDK_python.cpython-310-x86_64-linux-gnu.so` python3.10 导入 OK；`test_path_replay.py` 6 passed。尚未真机复跑标定，`getJointPos` 是否返回 7 元待实机确认。
   - 状态：**已换 SDK，未再改动 `.deb` 肘部搜索逻辑（原 A/B 候选不再执行）**；下一步用新 SDK 重跑左臂标定验证。

## 启动命令（README 现网口径，解决上述前置后再执行）

```bash
# 注意：必须先进入 kitchen_robot_home，否则 robot_driver 读不到 .localconfig（SDK 路径）会崩
cd /home/tbl/Project/boss_electrics/kitchen_robot_home
source /opt/ros/humble/setup.bash
source install/setup.bash
source /home/tbl/camera_env/camera_env.sh   # 相机 python 隔离环境（本机），含 PYTHONNOUSERSITE=1
export DEXBOT_ROBOT_IP=192.168.2.159        # 左臂；右臂改为 192.168.2.160

# 标定结果输出目录（2026-08-15 后使用主仓库规范目录）
ros2 launch dexbot_bringup calibration.launch.py \
    arm_type:=left \
    output_file:="/home/tbl/Project/boss_electrics/kitchen_robot_home/src/dexbot_bringup/config/calibration/left_calibration_result.yaml" \
    marker_length:=0.13 \
    auto_vel_scale:=0.25 \
    x_min:=0.15 x_max:=0.6 \
    y_min:=0.1 y_max:=0.5 \
    z_min:=-0.5 z_max:=0.3

ros2 service call /calibration/start_calibration std_srvs/srv/Trigger "{}"
```

进度通过 `/calibration/status`，结果 YAML 同时保存 `T_base_cam`、`T_tcp_marker`、样本数和 RMSE。

## 下一轮需用户提供

- 实际相机型号/分辨率（✅ 2026-08-07：Orbbec Gemini 336L，COLOR 1280x720）
- ArUco 板边长（✅ 2026-08-07：字典 6X6，黑色外沿边长 130 mm / 0.13 m，与 launch 默认一致）
- 机械臂（标定臂）IP（✅ 2026-08-07：左 192.168.2.159 / 右 192.168.2.160）
- 是否确认"相机固定 + 手上 marker"装法（✅ 2026-08-07：眼到手外，机械臂末端装 ArUco，相机固定，与现有实现一致）
