# Progress Log

## 2026-05-30 14:00 Local Time

- Objective: 初始化工程 project-log 记录。
- Work completed: 创建 .project-log/ 目录及业务逻辑、硬件、架构、配置、调试文件。
- Business logic impact: 初始化了黄瓜切割 4 步全流程的节点和边定义。
- Problems encountered: None.
- Resolution: Not applicable.
- Verification: 文件创建完成，结构完整。
- Unverified items: 硬件集成测试未执行。
- Files changed: .project-log/ 目录及全部子文件。
- Next steps: 准备黄瓜切割全流程的硬件集成测试。

## 2026-05-30 15:20 Local Time

- Objective: 修复 GUI (dexbot_toolbox) 中 RosServiceBridge 缺少服务类型属性的 bug。
- Work completed: 在 `ros_bridge.py` 的 `RosServiceBridge.__init__()` 中增加了 17 个服务/消息类型作为实例属性。
- Business logic impact: None（GUI 层修复，不影响业务逻辑）
- Problems encountered: RosServiceBridge 从 dexbot_interfaces_low.srv 导入了 MoveJoints 等服务类型，但只在 __init__ 中用作局部变量创建 client，未保存为 self.xxx。GUI 控制代码中 bridge.MoveJoints.Request() 因找不到属性而崩溃。
- Resolution: 添加 self.MoveJoints = MoveJoints 等 17 行实例属性赋值。
- Verification: python3 -c "from dexbot_toolbox.ros_bridge import RosServiceBridge" 导入通过。
- Files changed: ~/Project/dexbot_ros2_ws/src/dexbot_toolbox/dexbot_toolbox/ros_bridge.py
- Next steps: 重新测试 GUI 中左臂/右臂控制功能。

## 2026-05-30 15:00 Local Time

- Objective: 单独测试左臂 cucumber_hold 完整流程（视觉 + 动作 + 释放）。
- Work completed:
  - cucumber_hold:default 成功执行：视觉锁定黄瓜 → SDK 直连左臂 → 移动到按压位姿
  - cucumber_hold:release 成功执行：左臂 MoveAbsJ 回到 home 关节角
- Business logic impact: Edge A→B 和 Edge D→E 验证通过
- Problems encountered: None（一次通过）
- Resolution: Not applicable
- Verification:
  - /cuttofu/perception/objects_with_pose 发布稳定黄瓜位姿
  - 左臂通过 XcoreDirectExecutor 直连 SDK 成功
  - 移动到位后 shared_cucumber_geometry 正常发布
  - release 后左臂回到 home 位姿
- Unverified items: 双手协同未测试（右臂 prepare + cut_round）
- Files changed: 无代码修改
- Next steps: 测试全流程切黄瓜（左臂 hold + 右臂 prepare + cut_round + 左臂 release）

## 2026-05-30 14:30 Local Time

- Objective: 单独测试左臂 cucumber_hold 的视觉管线。
- Work completed:
  - 修复 vision_params.yaml 中 SAM3 model_path（/home/a/models/sam3 → /home/tbl/Project/models/sam3）
  - 启动 vision_bringup.launch.py 验证全视觉链路
- Business logic impact: None（配置修正，业务逻辑不变）
- Problems encountered:
  - SAM3 模型路径错误导致节点启动失败
  - RealSense D435I 接在 USB 2.1 口，有 Depth stream 启动警告和 USB 带宽警告
  - 无 GPU，SAM3 fallback 到 CPU 推理（8311ms warmup，~7s 每帧）
- Resolution:
  - model_path 已修正为 /home/tbl/Project/models/sam3
- Verification:
  - SAM3 loaded successfully from correct model path
  - Pose estimator 成功检测黄瓜：class=cucumber, base_pos=[0.571, -0.394, -0.064] m
  - 连续 3 帧检测位置稳定一致
  - 视觉管线（RealSense → SAM3 → pose_estimator → objects_with_pose）全链路通
- Unverified items:
  - 左臂 SDK 连接未测试（需实际硬件）
  - 手眼标定文件未验证（calibration_result_left.yaml）
  - Depth stream 警告需要进一步观察（USB 2.1 带宽限制）
- Files changed: CutTofo/cuttofu_vision/config/vision_params.yaml
- Next steps:
  - 连接左臂硬件后测试 cucumber_hold action（profile: default）
  - 验证 hand-eye calibration 变换正确
  - 考虑将 RealSense 换到 USB 3.0 口以解决 Depth stream 警告

## 2026-05-30 16:10 Local Time

- Objective: 厘清 CutTofo Skill 框架中 TCP 标定状态和坐标系定义，明确左/右臂 TCP offset 来源。
- Work completed:
  - 定位了全部 4 个 TCP offset 配置文件及其使用方
  - 确认 TCP = flange + 纯平移 offset（姿态相同）
  - 确认控制链：计算 TCP 目标 → 转换为法兰目标 → 控制法兰到达
- Business logic impact:
  - **右臂 prepare/cut_round** 从 `cuttofu_skills/cuttofo_skill_common/config/arms.yaml` 读 `tcp_offset: [0.01089, 0.12506, 0.25620]`
  - **左臂 cucumber_hold** 从 `cucumber_hold_params.yaml` 读 `tool_offset: [0, 0.02, 0.19]`（不读 arms.yaml）
  - `arms.yaml` 为整个 skill 框架提供 URDF、关节名、home 角、TCP offset 等公共配置
  - `src/config/tool_offset.yaml` 是 N-point 标定输出，但 **未被任何代码引用**（孤儿文件）
- Problems encountered:
  - 4 个配置文件分散管理，`arms.yaml` 和 `cuttofo_config.yaml` 值手动同步
  - `tool_offset.yaml` 标定结果未被使用，`arms.yaml` 中的值是人工填入的
  - `cucumber_hold_params.yaml` 中左臂 `tool_offset` 默认 fallback 到了 `tool_offset.yaml` 的 `left` 值（`0.01506, 0.05044, 0.14338`），而非 arms.yaml 的 `[0,0,0]`
  - `cuttofo_xcore` 和 skill 框架两套系统独立维护各自的 TCP offset，值相同但不同源
- Resolution: 梳理清晰了所有 TCP offset 来源和流向，记录到 conversation 中。
- Unverified items:
  - 右臂 prepare + cut_round 完整测试未执行
  - 全流程集成测试未执行
  - 两个 YAML 文件中的偏移值是否与物理工具实际一致未验证
- Files changed: 无代码修改（纯调研）
- Next steps:
  - 启动 `dual_xcore_controllers.launch.py` 测试右臂 ROS services 可达性
  - 单独测试 prepare:cucumber 和 cut_round:cucumber skill
  - 全流程黄瓜切割集成测试
  - 写入 AGENTS.md 记录关键配置文件和启动惯例

## 2026-05-30 16:50 Local Time

- Objective: 调研视觉管线架构，评估替换为新检测逻辑的可行性。
- Work completed:
  - 梳理了视觉全链路：RealSense → SAM3 → pose_estimator → `/cuttofu/perception/objects_with_pose` → `CucumberHoldLock`
  - 定位了 `ObjectState.msg` 接口定义（必须字段：`class_id`, `confidence`, `pose.position`, `principal_axis`, `geometric_features`）
  - 确认 `CucumberHoldLock.compute_hold_point_right_base()` 计算按压点的公式：OBB_center + axis * fraction - press_down
  - 确认视觉仅提供位置（姿态锁当前 TCP 不动）
  - 确认替换方案：新检测节点直接发布 `ObjectStateArray` 到同一 topic 即可
  - 确认需要最小改动的点：`CucumberHoldLock` 加 `skip_compute_hold_point` 开关，跳过 `compute_hold_point_right_base()`，直接使用 `pose.position` 作为锁定点
  - `right_base_point_to_left()` 转换 + `manual_offset_m` 微调流程保持不变
- Files changed: 无代码修改（纯调研）
- Next steps:
  - **实现新视觉检测节点**，输出 `ObjectStateArray` 到 `/cuttofu/perception/objects_with_pose`，`pose.position` 直接填入最终按压点（右基座坐标系）
  - **修改 `CucumberHoldLock`**，加入 `skip_compute_hold_point` 参数
  - 集成测试新检测 + 左臂按压流程

## 2026-05-30 17:30 Local Time

- Objective: 制定详细的视觉检测迁移计划 V2，确认接口兼容性，并完成全部代码实现。
- Work completed:
  - **调研与分析：**
    - 梳理了 cutcucumber_xcore 视觉框架（SAM3 + pose_estimator + detect_cucumber + 可视化）
    - 对比确认现有 dexbot_middle_layer 的 pose_estimator 已在 gf[5:8] 输出 extents、gf[8:20] 输出 ABCD 角点，与新检测兼容，**无需迁移 SAM3/pose_estimator**
    - 追踪完整接口链：`detect_cucumber` → `CucumberHoldLock` → `shared_cucumber_geometry` → `VisionGeometryTracker` → `prepare workflow`
    - 确认左臂 hold 和右臂 prepare 对 ObjectState 字段的具体依赖条件
    - 确认 `len(gf) >= 20` 是向下游透传 ABCD 角点的必要条件
    - 确认 `build_rotation_with_edge_dir()` 姿态推导保留，只替换位置来源
  - **计划文档：**
    - 生成 `docs/视觉检测迁移计划.md`（V2 版，含状态机、Y_board 两阶段策略、接口兼容、不变部分、修改清单）
  - **代码实现：**
    - 新建 `cuttofu_vision/cuttofu_vision/top_face_geometry.py`：`compute_hold_tcp_positions_from_top_face()`、`compute_knife_tcp_from_top_face()`
    - 新建 `cuttofu_vision/cuttofu_vision/detect_cucumber_node.py`：domain 修正 + Y_board + 多帧平均 + ABCD 重排序 + PCA/DC 计算 + 左右手 TCP 输出
    - 新建 `cuttofo_skill_visualization/` 完整 skill 包：`cucumber_visualizer_node.py`（纯渲染，零计算）、`visualization_params.yaml`、`cucumber_visualization.launch.py`
    - 修改 `topics.py`：加 POSE_RAW_TOPIC / CUCUMBER_STATE_TOPIC / Y_BOARD_TOPIC
    - 修改 `vision_params.yaml`：加 detect_cucumber 参数节（案板、多帧、左右手 TCP 偏移）
    - 修改 `vision_bringup.launch.py`：pose_estimator 输出重映射到 POSE_RAW + 加入 detect_cucumber_node
    - 修改 `setup.py` (cuttofu_vision)：注册 detect_cucumber_node 入口
    - 修改 `cucumber_hold_lock.py`：+skip_compute_hold_point 参数，skip 时直接使用 pose.position
    - 修改 `cucumber_hold_node.py`：传 skip_compute_hold_point 到 CucumberHoldLock
    - 修改 `cucumber_hold_config.py`：perception dict 包含 skip_compute_hold_point
    - 修改 `cucumber_hold_params.yaml`：skip_compute_hold_point: true
    - 修改 `vision_geometry_tracker.py`：从 gf[0:3] 读 R_tcp 替代 corner 计算
    - 修改 `tofu_prepare_workflow.py`：删除 `compute_tcp_target_from_corners()` 和 `apply_cucumber_prepare_target_offsets()`，直接用 detect 输出的 R_tcp
    - 清理 `tofu_prepare_workflow.py` 无用 import
- Business logic impact:
  - **左臂 hold**：不再在 CucumberHoldLock 中计算按压点，直接消费 detect_cucumber 输出的 L_tcp（skip_compute）
  - **右臂 prepare**：不再从角点推导 TCP 位置，直接消费 detect_cucumber 输出的 R_tcp（gf[0:3]），姿态推导保留不变
  - **数据流变化**：pose_estimator 输出 → `/cuttofu/perception/pose_raw`（内部）→ detect_cucumber_node → `/cuttofu/perception/objects_with_pose`（控制接口）
  - **可视化**：从 detect_cucumber_node 的 gf[36:42] 读取 L_tcp/R_tcp，零计算，纯渲染
- Problems encountered:
  - detect_cucumber_node 不能同时订阅和发布 `objects_with_pose` 同一 topic → 增加 `POSE_RAW_TOPIC` 内部 topic
  - 控制输出的 gf 数组索引要与下游 VisionGeometryTracker 的期望对齐（gf[5:8] extents, gf[8:20] ABCD）→ 修正 detect_cucumber_node 的 gf 构造逻辑
  - 可视化包的 setup.cfg 从 cucumber_hold 复制后未修改包名 → 修复后重新编译
  - VisionGeometryTracker 的 tcp_target 来自 corner 计算，需改为直接读 gf[0:3] → 修改 `_build_prepare_state_from_object()`
- Resolution: 全部上述问题已修复并通过编译验证。
- Verification:
  - 编译：5 个包全部通过（cuttofu_vision、cuttofo_skill_common、cuttofo_skill_cucumber_hold、cuttofo_skill_tofu_prepare、cuttofo_skill_visualization）
  - 导入：所有 Python 模块 import 正常
  - 可执行文件：`detect_cucumber_node`、`cucumber_visualizer_node`、`cucumber_hold_node`、`tofu_prepare_node` 均注册
  - 算法验证：`compute_hold_tcp_positions_from_top_face()` 和 `compute_knife_tcp_from_top_face()` 数学验证通过
- Files changed: (see full list above — 15+ files added/modified across 3 packages)
- Next steps:
  - 启动 `vision_bringup.launch.py` 验证 detect_cucumber_node 视觉全链路
  - 集成测试左臂 cucumber_hold（skip_compute=True 路径）
  - 集成测试右臂 prepare（R_tcp 路径）
  - 启动可视化 `cucumber_visualization.launch.py` 验证 RViz 渲染

## 2026-05-30 17:00 Local Time

- Objective: 实机测试视觉管线 + 可视化节点。
- Work completed:
  - 启动 `vision_bringup.launch.py`，RealSense D435I 正常连接，`pose_estimator_node` 正常发布位姿
  - 启动 `cucumber_visualization.launch.py`，可视化节点正常启动
  - 确认所有 topic 正确发布：`/cuttofu/perception/pose_raw`、`/cuttofu/perception/objects_with_pose`、`/cuttofu/perception/cucumber_state`、`/cuttofu/perception/segmentation_result`、`/cuttofu/vision/text_prompt`、`/cuttofu/perception/y_board`
  - `detect_cucumber_node` 启动成功，等待 3 帧累积后输出
  - pose_estimator 成功检测黄瓜：`base_pos=[0.473, -0.393, -0.059] m`
- Problems encountered:
  - `detect_cucumber_node` 参数类型错误（int vs double）→ 修 `top_y_percentile` 为 float 型
  - launch 文件给 detect_cucumber_node 传了 pose_estimator 的参数 → 增加 `detect_cuke_params` 独立加载
  - **CUDA 不可用**：RTX 4090 + Driver 580.159.03 + PyTorch 2.11.0+cu130，`cuInit(0)` 返回 999（CUDA_ERROR_UNKNOWN）。CUDA 13.0 pip runtime 与驱动有兼容性问题，尚未解决
  - **PyTorch 被卸载**：尝试安装 CUDA 12.6 版 PyTorch 过程中，torch 被移除，SAM3 因 `No module named 'torch'` 无法启动
  - RealSense USB 2.1 端口导致带宽警告，但不影响功能
  - 僵尸节点占用了摄像头设备 → 通过 `pkill` + 清除 `/dev/shm` 解决
- Resolution:
  - 参数类型错误和 launch 参数问题已修复并编译通过
  - CUDA 问题需重新安装 PyTorch（推荐 CPU 版先保证功能，GPU 后续处理）
- Unverified items:
  - detect_cucumber_node 的首次输出尚未验证（需要 PyTorch 恢复后等 3 帧累积）
  - RViz 可视化渲染尚未实机验证
  - 左臂 cucumber_hold / 右臂 prepare 集成测试未执行
- Files changed: 
  - `cuttofu_vision/cuttofu_vision/detect_cucumber_node.py`: top_y_percentile int→float
  - `cuttofu_vision/config/vision_params.yaml`: top_y_percentile 99→99.0
  - `cuttofu_vision/launch/vision_bringup.launch.py`: 独立加载 detect_cuke_params
- Next steps:
  - **需先修复**：`pip install torch --index-url https://download.pytorch.org/whl/cpu` 恢复 PyTorch，使 SAM3 可加载
  - 重新启动视觉管线 + 可视化，验证 detect_cucumber_node 输出 L_tcp/R_tcp
  - 待 CUDA 13 兼容性问题解决后切换 GPU 推理
  - 集成测试双臂控制流程

## 2026-05-30 17:30 Local Time

- Objective: 修复 CUDA 问题并迁移完整可视化栈到 cuttofo_skill_visualization。
- Work completed:
  - **CUDA 修复**：重新安装 torch 2.12.0+cu126 + torchvision 0.27.0+cu126（从 cu126 统一索引安装，`torchvision::nms` 算子不匹配问题解决）
  - **可视化栈迁移研究**：调研 cutcucumber_xcore 可视化架构（7 个感知 skill），确定需迁移 URDF+Mesh、rviz 配置、robot_state_publisher、viz_hand_joint_bridge（关节合并 + 手 mimic 扩展）、RealSense 点云
  - **确认资源可用**：确认当前 workspace 已安装 linkerhand_o6_r_description 包（含右手模型和 mesh）
  - **复制全部可视化资源**：从 cutcucumber_xcore 复制到 cuttofo_skill_visualization：URDF、双手 STL mesh、双臂 STL mesh、RViz 配置、realsense_camera.launch.py、joint_state_gui.py、viz_hand_joint_bridge.py
  - **创建一键启动 launch**：`cucumber_viz_display.launch.py` — 全栈一键启动（robot_state_publisher + 关节桥 + 手眼 TF + RealSense 点云 + Marker 节点 + RViz2），参数化所有关节主题、安装偏移和相机配置
  - **兼容包装**：`cucumber_visualization.launch.py` 改为 include 上述完整 launch（向下兼容）
  - **包名替换**：所有 `.urdf`/`.xacro`/`.stl`/`.rviz` 文件中的 `cutcucumber_visualization` → `cuttofo_skill_visualization`
  - **setup.py 更新**：添加 `package_tree()` 函数保留嵌套子目录；加入 viz_hand_joint_bridge 和 joint_state_gui 的 console_scripts entry points；删除旧扁平 `package_files()` 函数
  - **package.xml 更新**：添加 sensor_msgs、tf2_ros、robot_state_publisher、rviz2、xacro、joint_state_publisher_gui、dexbot_toolbox、realsense2_camera 依赖
  - **RViz 配置更新**：marker 主题改为 `/cuttofu/perception/cucumber_visualization`
  - **lifetime bug 修复**：cucumber_visualizer_node 中所有 `Duration(sec=float)` → `Duration(sec=int(float))`（13 处）
  - **static_transform_publisher 修复**：world_display 帧显式添加 `--x 0 --y 0 --z 0`，避免新版 tf2_ros 因缺参数导致帧发布失败
  - **静态自我检查通过**：grep 无残留 `cutcucumber_visualization` 引用（仅保留 topic 名 `/cuttofu/perception/cucumber_*`），所有 python 文件编译无错误，xacro 能正常展开出 `rh_hand_base_link`、`lh_hand_base_link` 等左右手 link
  - **编译验证**：`colcon build --packages-select cuttofo_skill_visualization --symlink-install` 成功，`ros2 launch --show-args` 正常展示所有参数
  - **实机确认**：RealSense D435I 已连接（USB 2.1），ROS 环境正常，cuttofu_vision 和 cuttofo_skill_visualization 包均可用
- Business logic impact:
  - 可视化从 cutcucumber_xcore 完全迁移到 cuttofo_skill_visualization，纯消费级（只读检测数据做渲染）
  - `cucumber_viz_display.launch.py` 一条指令启动全栈可视化
  - 左/右手安装偏移可参数化（launch arguments xyz/rpy）
  - 手眼标定自动搜索 workspace 根目录
- Problems encountered:
  - CUDA 13.0 (cu130) pip runtime 与 Driver 580.159.03 兼容 → 改用 cu126 索引统一安装解决
  - `setup.py` 扁平 data_files 无法保留 urdf/hand/ 子目录结构 → 改用 `package_tree()` 递归收集
  - 新版 tf2_ros 的 static_transform_publisher 要求显式 xyz/rpy 参数 → 补 `--x 0 --y 0 --z 0`
- Resolution: 全部上述问题已修复并通过编译验证。
- Verification:
  - 编译成功（colcon build）
  - launch --show-args 参数正常
  - xacro 展开含左右手 link
  - Python import 正常
  - RealSense D435I 硬件在线
  - torch 2.12.0+cu126 / torchvision 0.27.0+cu126 正常
- Unverified items:
  - 完整可视化栈实机运行验证（启动 vision_bringup + cucumber_viz_display，验证点云、模型、Marker 同步显示）
  - detect_cucumber_node 全链路输出 L_tcp/R_tcp（需重新启动 vision_bringup 验证）
  - 左臂 cucumber_hold（skip_compute=True 路径）集成测试
  - 右臂 prepare（R_tcp 路径）集成测试
  - 全流程测试（hold → prepare → cut_round → release）
- Files changed:
  - 新建 `cuttofo_skill_visualization/launch/cucumber_viz_display.launch.py`
  - 新建 `cuttofo_skill_visualization/launch/cucumber_visualization.launch.py`（覆盖旧 wrapper）
  - 新建 `cuttofo_skill_visualization/launch/realsense_camera.launch.py`
  - 新建 `cuttofo_skill_visualization/rviz/cucumber_display.rviz`
  - 新建 `cuttofo_skill_visualization/urdf/AR5_dual_W4C1C1.urdf.xacro`
  - 新建 `cuttofo_skill_visualization/urdf/hand/linkerhand_o6_right.xacro`
  - 新建 `cuttofo_skill_visualization/urdf/hand/linkerhand_o6_left.urdf`
  - 新建 `cuttofo_skill_visualization/urdf/hand/meshes/`（全部 STL）
  - 新建 `cuttofo_skill_visualization/urdf/meshes/`（全部 STL）
  - 新建 `cuttofo_skill_visualization/cuttofo_skill_visualization/viz_hand_joint_bridge.py`
  - 新建 `cuttofo_skill_visualization/cuttofo_skill_visualization/joint_state_gui.py`
  - 修改 `cuttofo_skill_visualization/setup.py`（package_tree + entry_points）
  - 修改 `cuttofo_skill_visualization/package.xml`（完整依赖）
- Next steps:
  - 启动 vision_bringup + cucumber_viz_display 全栈可视化，验证机器人模型、点云、Marker 同步显示
  - 验证 detect_cucumber_node 全链路输出 L_tcp/R_tcp
  - 集成测试左臂 cucumber_hold（skip_compute=True 路径）
  - 集成测试右臂 prepare（R_tcp 路径）
  - 全流程测试（hold → prepare → cut_round → release）

## 2026-05-30 17:50 Local Time

- Objective: 实机验证可视化全栈（点云、机器人模型、Marker），修复发现的问题。
- Work completed:
  - **可视化纯消费修复**：`cucumber_viz_display.launch.py` 中 `enable_realsense` 默认值 `true` → `false`，可视化不再启动 RealSense 相机，避免与 `vision_bringup` 冲突
  - **点云缺失修复**：`vision_bringup.launch.py` 中 RealSense 启动参数添加 `pointcloud.enable:="true"`，因 `rs_launch.py` 默认 `pointcloud.enable=false`，导致只开深度图不开点云
  - **ABCD 角点语义修正（两轮迭代）**：
    - 第一轮：按 Z 分组将 AB 放到左臂侧（min Z），CD 放到右臂侧（max Z）→ 不符合用户对"远/近"的理解
    - 第二轮（最终方案）：改为按 X 分组定义"近/远"，`AB = 大 X（远离基座）`，`CD = 小 X（靠近基座）`，同时保留 `D = 右近角`（max Z, min X）以保证刀参考角在右臂侧
    - 具体排序规则：先按 X 分成 near/far → 每组内按 Z 排序 → `A=far[1](right-far), B=far[0](left-far), C=near[0](left-near), D=near[1](right-near)`
    - 删除了旧的 tiebreaker 逻辑（按边长短判断邻接），因新排序已保证周长一致性
  - **编译验证**：`cuttofu_vision` 和 `cuttofo_skill_visualization` 均编译通过
  - **函数级验证**：ABCD 单元测试通过，`AB_x=0.6(远侧)`，`CD_x=0.2(近侧)`，`D=right-near`
  - **用户实机确认**：效果正确
- Business logic impact:
  - 可视化栈从数据源耦合中解耦，纯消费级
  - 点云可通过 `vision_bringup` 正常输出
  - ABCD 角点语义从"按 Z 分左右"改为"按 X 分近远"，匹配用户预期
  - 左臂 hold TCP 和右臂 knife TCP 的位置推导自动跟随角点修正（因 TCP 计算直接使用 ABCD 坐标）
- Problems encountered:
  - `enable_realsense:=false` 后点云消失 → 根因是 `vision_bringup` 没开 `pointcloud.enable`
  - 第一轮 ABCD 修正误解了用户"远/近"语义（以为是 Z 方向，实际是 X 方向）→ 第二轮按 X 分组修正正确
  - 旧 tiebreaker 与新排序冲突 → 删除，简化逻辑
- Resolution: 全部问题已修复并通过实机验证。
- Verification:
  - 可视化全栈正常：机器人模型 + Marker + 点云同步显示
  - ABCD Marker 角点标签：`A/B` 在远端（大 X），`C/D` 在近端（小 X）
  - 编译通过，函数单元测试通过
- Unverified items:
  - 左臂 cucumber_hold（skip_compute=True 路径）未测试
  - 右臂 prepare（R_tcp 路径）未测试
  - 全流程测试未执行
- Files changed:
  - `cuttofo_skill_visualization/launch/cucumber_viz_display.launch.py`（enable_realsense 默认值）
  - `cuttofu_vision/launch/vision_bringup.launch.py`（加 pointcloud.enable）
  - `cuttofu_vision/cuttofu_vision/detect_cucumber_node.py`（ABCD 重排规则）
- Next steps:
  - 集成测试左臂 cucumber_hold（skip_compute=True 路径）
  - 集成测试右臂 prepare（R_tcp 路径）
  - 全流程测试（hold → prepare → cut_round → release）

## 2026-05-30 19:10 Local Time

- Objective: 集成测试左臂 cucumber_hold release 和 default 流程，修复 workspace 污染导致的 AttributeError。
- Work completed:
  - **cucumber_hold release 测试通过**：左臂成功连接 xCore SDK（192.168.2.160），返回 `release_ok`。手臂未动的原因是已在 home 位置，release 归位到同一位置。
  - **default 流程 AttributeError**：调用 `executor.build_locked_flange_waypoints()` → `flange_pose6_from_tcp_goal()` → `self._robot.tcp_goal_base_to_flange_pose()` 时抛出 `'XCoreLbotRobot' object has no attribute 'tcp_goal_base_to_flange_pose'`
  - **根因分析**：525 workspace 的 `install/setup.bash` 链式载入了 `/home/tbl/Project/cucumber/dexbot_ros2_ws/install`（旧 cucumber workspace）。该 workspace 的 `dexbot_bottom_layer` 是扁平复制（非 egg-link），编译时间早于 `tcp_goal_base_to_flange_pose` 方法的添加。Python 在 PYTHONPATH 中因多 workspace 共存，加载了旧版的 `XCoreLbotRobot`。
  - **修复**：删除旧 workspace 的 stale `dexbot_bottom_layer`：`rm -rf ~/Project/cucumber/dexbot_ros2_ws/install/dexbot_bottom_layer`
  - **验证**：`hasattr(XCoreLbotRobot, 'tcp_goal_base_to_flange_pose')` = True，import 来源为 525 workspace build 目录
- Business logic impact: None（修复了环境问题，业务逻辑不变）
- Problems encountered:
  - 525 workspace `setup.bash` 被 colcon 生成时记录了链式依赖，导致每次 `source install/setup.bash` 都会带入旧 workspace 的 install
  - 旧 workspace 的 `dexbot_bottom_layer` 是扁平复制安装（非 develop/egg-link 模式），编译后不会自动同步源码更新
  - 三个 workspace（525、cucumber、旧 dexbot）的 `dexbot_bottom_layer` 同时在 PYTHONPATH 中，Python 加载了错误的版本
- Resolution: 删除污染源的 `dexbot_bottom_layer` install 目录，使 525 workspace 的 egg-link 成为唯一版本
- Verification:
  - `python3 -c "from dexbot_bottom_layer.lbot_catch.arm_api.Python.lbot.lbot_robot_xcore import XCoreLbotRobot; print('tcp_goal_base_to_flange_pose:', hasattr(XCoreLbotRobot(), 'tcp_goal_base_to_flange_pose'))"` → True
  - 加载来源确认：`...525/.../build/dexbot_bottom_layer/...`
- Unverified items:
  - default 流程执行未验证（AttributeError 修复后尚未重新启动）
  - 右臂 prepare 和 cut_round 未测试
- Files changed: 无代码修改；删除了 `~/Project/cucumber/dexbot_ros2_ws/install/dexbot_bottom_layer`
- Next steps:
  - 重新启动 cucumber_hold_server，发送 default goal 验证左臂按压流程
  - 继续集成测试右臂 prepare（R_tcp 路径）
  - 全流程测试（hold → prepare → cut_round → release）

## 2026-05-30 19:40 Local Time

- Objective: 重构左臂 cucumber_hold 按压控制逻辑，移除“锁当前开始姿态”路径，替换为“config 固定法兰姿态 + approach 调姿 + MoveL 下压”。
- Work completed:
  - **删除旧左手控制逻辑**：移除了 `cucumber_hold_workflow.py` 中 `_nrt_tcp_targets` / `_run_nrt_waypoints` / `_run_nrt_hold` / `_run_rt` 以及 `xcore_direct_executor.py` 中 `_locked_tcp_quat` / `_move_tcp_goal_locked_ori` / `move_position_only` / `move_position_only_sequence` / `build_locked_flange_waypoints`
  - **新控制逻辑落地**：
    - approach 步：`move_to_approach_with_orientation()` 使用 config 中的 `target_flange_quat_xyzw` 做 `move_tcp_fixed_orientation()`
    - press 步：`move_cartesian_press()` 使用当前法兰姿态保持不变，先把目标 TCP 点换算成法兰目标，再调用 `linear_move_to_pose()`（MoveL）
  - **config 同步**：在 `cucumber_hold_params.yaml` 的 `profiles.default` 中加入 `approach_speed`、`press_speed` 和从旧 `cutcucumber_xcore` 复制过来的已标定 `target_flange_quat_xyzw`
  - **新增采集脚本**：`capture_left_flange_pose.py`，可直接读取当前左臂法兰姿态并写回 `cucumber_hold_params.yaml`
  - **入口注册**：新增 `ros2 run cuttofo_skill_cucumber_hold capture_left_flange_pose`
- Business logic impact:
  - 左臂按压从“以开始姿态为姿态约束”改为“以 skill config 中的固定法兰姿态为姿态约束”
  - 左臂 default 流程执行链变为：视觉锁定 TCP → MoveJ 到 approach 并达到目标法兰姿态 → MoveL 直线下压到 press 点
  - 旧 NRT/RT 双路径不再作为左臂 hold 逻辑保留，避免控制逻辑并存和冗余
- Problems encountered:
  - 这些 skill 包不被当前 `colcon list` 自动发现，无法用常规 `colcon build --packages-select` 重新生成 entry point
  - `cuttofo_skill_cucumber_hold` 的安装方式是 `.egg-link -> build/`，因此运行时依赖 build 目录元数据而不是单纯依赖 src/
- Resolution:
  - 代码文件因 src/build 为 hardlink，同步修改后运行时模块已更新
  - 手动补齐了 build 下的 `entry_points.txt` 与 install 下的 wrapper 脚本，使 `capture_left_flange_pose` 可通过 `ros2 run` 调用
- Verification:
  - `python3 -m py_compile` 编译通过：`xcore_direct_executor.py`、`cucumber_hold_workflow.py`、`capture_left_flange_pose.py`
  - source `install/setup.bash` 后 import 正常：`XcoreDirectExecutor`、`execute_cucumber_hold`、`CaptureLeftFlangePose`
  - entry point 校验通过：`distribution('cuttofo-skill-cucumber-hold').entry_points` 中存在 `capture_left_flange_pose`
  - grep 校验通过：旧左手锁姿态控制函数引用已清零
- Unverified items:
  - 真机未跑：`default` profile 的 approach + MoveL press 尚未实机验证
  - 采集脚本未连接真机执行
  - 右臂 prepare / 全流程未测试
- Files changed:
  - `cuttofo_skill_common/cuttofo_skill_common/arm/xcore_direct_executor.py`
  - `cuttofo_skill_cucumber_hold/cuttofo_skill_cucumber_hold/cucumber_hold_workflow.py`
  - `cuttofo_skill_cucumber_hold/cuttofo_skill_cucumber_hold/capture_left_flange_pose.py`（新增）
  - `cuttofo_skill_cucumber_hold/config/cucumber_hold_params.yaml`
  - `cuttofo_skill_cucumber_hold/setup.py`
  - `build/cuttofo_skill_cucumber_hold/cuttofo_skill_cucumber_hold.egg-info/entry_points.txt`
  - `install/cuttofo_skill_cucumber_hold/lib/cuttofo_skill_cucumber_hold/capture_left_flange_pose`（新增 wrapper）
- Next steps:
  - 运行 `ros2 run cuttofo_skill_cucumber_hold capture_left_flange_pose` 采集当前左臂法兰姿态
  - 重启 `cucumber_hold_server`，发送 `default` goal 验证 approach + MoveL press
  - 继续右臂 prepare（R_tcp）与全流程测试

## 2026-05-30 19:55 Local Time

- Objective: 修复 `dual_xcore_controllers.launch.py` 启动时 `xcore_controller_node` 因 `RcutilsLogger.info()` 参数错误而崩溃的问题。
- Work completed:
  - 定位到 `xcore_controller_node.py` 中 `_resolve_xcore_local_ip()` 使用了 `rclpy` logger 的错误调用方式：把标准 `logging` 风格的格式串 + 多位置参数传给了 `RcutilsLogger.info/warning`
  - 将两处调用改成预格式化字符串（f-string），避免在自动探测或校验 `xcore_local_ip` 时启动即抛 `TypeError`
- Business logic impact: None（启动期日志 bug 修复，不改变控制业务逻辑）
- Problems encountered:
  - 节点在机器人连接前就崩溃，表面看起来像“控制节点连不上”，实际是启动期日志 bug
  - 该 bug 只在 `xcore_local_ip` 自动探测 / 非法配置分支触发，因此容易和网络问题混淆
- Resolution: 把多参数 logger 调用改成单字符串 logger 调用
- Verification:
  - `python3 -m py_compile xcore_controller_node.py` 通过
  - 直接调用 `_resolve_xcore_local_ip('', '192.168.2.160', node.get_logger())` 成功输出日志，不再抛 `RcutilsLogger.info() takes 2 positional arguments but 4 were given`
  - AST 扫描 `xcore_controller_node.py`，无剩余多位置参数的 `rclpy` logger 调用
- Unverified items:
  - 未实际重新跑双臂 `dual_xcore_controllers.launch.py` 做整链真机验证
- Files changed:
  - `dexbot_bottom_layer/dexbot_bottom_layer/xcore_controller_node.py`
- Next steps:
  - 重新执行 `ros2 launch dexbot_bringup dual_xcore_controllers.launch.py arm_r_robot_ip:=192.168.2.161 arm_l_robot_ip:=192.168.2.160`
  - 确认 `/arm_l/...`、`/arm_r/...` 控制节点服务和 topic 正常注册

## 2026-05-31 Session — 左臂 hold press 段 SDK NRT 不执行（进入文献记录，暂停修复）

- Objective: 实机验证左臂 hold 第二段（approach → press MoveL 下压）
- Work completed:
  - 多轮 SDK NRT 调用方案实机测试：两段独立 `linear_move_to_pose`、队列 `moveAppend([cmd1,cmd2])`、`block=False`+轮询、`block=True`+停稳校验。
  - 第一段 approach（~400mm, 姿态变化）全部方案正常到达。
  - 第二段 press（8cm, 同姿态, 纯 Y+平移）全部方案 SDK 返回 True 但机器人不运动。
  - 详细问题记录：KI-004 + debugging-history.md
- Business logic impact: None（未改动生产路径，仍在调试阶段）
- Problems encountered:
  - 第二段 press SDK `linear_move_to_pose()` 返回 True 但真实位置完全不变。
  - 所有 6 种 NRT 调用变体均失败。
  - 不是 Python 层问题（日志和目标计算正确），不是等待/时序问题，不是参数不可达问题。
- Resolution: **未解决**。暂停当前 NRT MoveL 方向的调试，进入文献记录。
- Verification:
  - `python3 -m py_compile` 编译通过。
  - 日志确认：press 目标计算正确（approach +0.08m Y），SDK 返回 True 但位置不变。
- Unverified items:
  - 未尝试：`move_to_pose_target()`（MoveJ）做 press 段。
  - 未尝试：RT path `move_rt_cartesian_path()` 做 press 段。
  - 未尝试：独立 SDK 测试脚本（非 ROS）复现。
- Files changed:
  - `cuttofo_skill_common/arm/xcore_direct_executor.py`（多次修改 NRT MoveL 等待逻辑）
  - `cuttofo_skill_cucumber_hold/cucumber_hold_workflow.py`
  - `.project-log/debugging/known-issues.md`（新增 KI-004）
  - `.project-log/debugging/debugging-history.md`（新增完整问题记录）
- Next steps:
  - **暂停**当前左臂 hold press SDK NRT 调试。
  - 下一步可能尝试方向：
    1. 改用 `move_to_pose_target()`（MoveJ）代替 `linear_move_to_pose()`（MoveL）做 press。
    2. 改用 RT path 做 press。
    3. 写独立 SDK 测试脚本排除 ROS 环境干扰。

## 2026-06-01 17:43 Local Time — 制订豆腐切块全流程复活计划

- Objective: 检查豆腐切块完整代码栈，确认缺失项，记录到 project-log 待后续操作。
- Work completed: 梳理现有 tofu 架构状态
  - `tofu_workflow_execute.launch.py` 已存在（3 年前归档），但缺 CUTTOFO_WORKFLOW_CONFIG 环境变量和 vision/perception 集成
  - `skills_bringup.launch.py` 已存在，含全部 5 个 skill server（handle_approach + prepare + cut_round + vertical_cut + cucumber_hold）
  - `tofu_workflow_params.yaml` 已存在，定义 3 阶段 7 步：handle_approach → prepare(first_cut) → cut_round(round_1) → [人工旋转] → prepare(after_rotation_1) → cut_round(round_2) → [人工旋转] → prepare(after_rotation_2) → vertical_cut
  - `handle_approach` 和 `vertical_cut` 的 package 文件完整（setup.py, package.xml, entry points, launch）
- 需要修改:
  1. `tofu_workflow_execute.launch.py` — 加 SetEnvironmentVariable + perception/vision integration
  2. 编译验证 handle_approach + vertical_cut + orchestrator，处理可能的 libexec 缺失
  3. 分步测试各 skill
  4. 全流程测试
- Business logic impact: 豆腐流程无左臂 hold，纯右臂操作；共 2 次人工旋转等待点
- Files changed: 仅 plan 记录到 .project-log，无代码修改
- Next steps: 开始步骤 1 — 修改 tofu_workflow_execute.launch.py

## 2026-06-01 17:50 Local Time — 发现豆腐感知关键缺口：无 `class_id: "tofu"` 发布者

- Objective: 检查豆腐视觉特征计算逻辑是否存在。
- Work completed: 梳理 tofu 视觉管线全链路
  - **关键发现**: 当前 `objects_with_pose` 只有 `cucumber_perception_node` 发布数据，且硬编码 `class_id: "cucumber"`。
  - 下游 `VisionGeometryTracker`（tofu_prepare 使用）默认 `class_filter="tofu"`，永远筛不到数据，超时失败。
  - 无任何节点发布 `class_id: "tofu"` 的感知数据。
  - 无任何 tofu 可视化节点。
  - `handle_approach` 的 `HandlePerceptionLock` 也会收不到数据（除非改 class_filter）。
- 计划: 新建 `cuttofo_skill_tofu_perception` 包，包含 `tofu_perception_node`（多帧平滑 + class_id 重标）+ `tofu_visualizer_node`（RViz 渲染）。
- 当前状态: 已记录完毕，等待开始写代码。
- Files changed: 无代码修改。
- Next steps: 新建 `cuttofo_skill_tofu_perception` 包。

## 2026-06-01 17:00 Local Time — 架构重组：拆分黄瓜感知为独立包 + 全流程 launch 两终端化
- Work completed:
  - 创建 `cuttofo_skill_cucumber_perception` 包（9 个文件）
  - 迁移 `detect_cucumber_node.py` → `cucumber_perception_node.py`，含规范化 shutdown（rclpy.shutdown + executor.shutdown + destroy_node）
  - 迁移 `top_face_geometry.py`（TCP 几何计算）
  - `cuttofu_vision` 精简：移除 `detect_cucumber_node` 入口、launch 节点、params 参数段
  - `detect_cucumber_node.py` 标记 DEPRECATED
  - 创建 `cucumber_perception.launch.py`（自动 include vision_bringup）
  - 更新 `cucumber_workflow_execute.launch.py`：include perception launch，加 `include_perception`/`enable_vision` 参数
  - 更新 `启动指南.md`：全流程变两终端，右臂/左臂测试用 perception launch
- Problems encountered:
  - 新包 `cuttofo_skill_cucumber_perception` 首次编译后 `lib/cuttofo_skill_cucumber_perception/` 目录未生成，ROS 2 launch 因 libexec 缺失抛出异常。setuptools 59.6 + colcon symlink-install 偶发此 bug。手动创建目录并复制 `bin/` wrapper 解决。已在启动指南增加故障排查 5a。
  - realsense2 因嵌套 include 收到所有层级 launch args，大量 Warning 刷屏。移除 `show_camera_display` 跨级传递后恢复。
- Verification:
  - 3 包编译通过（perception + orchestrator + vision），launch 5 节点正常启动
  - `get_package_share_directory('cuttofo_skill_cucumber_perception')` 解析正确
  - `ros2 launch cuttofo_orchestrator cucumber_workflow_execute.launch.py enable_vision:=false` 无 libexec 错误
- Files changed:
  - 新建 `cuttofu_skills/cuttofo_skill_cucumber_perception/`（完整新包，9 文件）
  - 修改 `cuttofu_vision/setup.py`（移除 detect_cucumber_node entry point）
  - 修改 `cuttofu_vision/config/vision_params.yaml`（移除 detect_cucumber 段）
  - 修改 `cuttofu_vision/launch/vision_bringup.launch.py`（移除 detect_cucumber_node）
  - 修改 `cuttofu_vision/cuttofu_vision/detect_cucumber_node.py`（DEPRECATED 标记）
  - 修改 `cuttofo_orchestrator/launch/cucumber_workflow_execute.launch.py`（include perception）
  - 修改 `cuttofo_orchestrator/package.xml`（加 exec_depend）
  - 修改 `启动指南.md`（全流程两终端、故障排查 5a）
- Next steps:
  - 等待用户开始右臂或全流程测试工作。

## 2026-06-01 18:00 Local Time — SAM3 动态 Prompt 重构：感知节点成为 sole prompt publisher

- Objective: 将 vision 的 text_prompt 发布权从 skill 节点统一移到感知节点，消除多对一混乱依赖。
- Work completed:
  - `cucumber_perception_node` 在 `__init__` 末尾发布 prompt（`String(data=self.prompt_val)`）
  - 从 `cucumber_hold_node` 移除 `VisionPromptClient`/`schedule_startup_prompt` 导入及 `_vision_prompt` 初始化/logic/publish_prompt 调用，移除相关参数声明，移除 `time` 导入
  - 从 `tofu_prepare_node` 同样移除全部 prompt 相关代码和参数
  - 从 `handle_approach_node` + `handle_approach_workflow.py` 移除 `vision_prompt` 参数及 `publish_prompt` 调用，移除 `TYPE_CHECKING` 中的 `VisionPromptClient` 导入
  - 各 config YAML + config.py 清理 prompt 字段（text_prompt, publish_text_prompt_on_start, startup_prompt_delay_sec, wait_for_sam_subscriber_sec, prompt_settle_sec）
  - `vision_params.yaml`: text_prompt 默认值从 `cucumber` 改为 `object`
  - 5 包 colcon build 通过，6 模块 Python import 验证成功
- Rationale: 感知节点启动时就知道自己服务什么任务，应该由它（而非 skill 节点）告知 vision 检测什么物体。
- Note: `handle_approach` 暂无专用感知节点，后续需要新建 handle 感知节点来发布 `"wooden cleaver handle"` 等 prompt。
- Files changed:
  - `cuttofo_skill_cucumber_perception/cucumber_perception_node.py` — 加 prompt publish
  - `cuttofo_skill_cucumber_hold/cucumber_hold_node.py` — 移除 VisionPromptClient
  - `cuttofo_skill_cucumber_hold/cucumber_hold_config.py` — 移除 prompt params
  - `cuttofo_skill_cucumber_hold/config/cucumber_hold_params.yaml` — 移除 prompt fields
  - `cuttofo_skill_tofu_prepare/tofu_prepare_node.py` — 移除 VisionPromptClient
  - `cuttofo_skill_tofu_prepare/tofu_prepare_config.py` — 移除 prompt params
  - `cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml` — 移除 prompt fields
  - `cuttofo_skill_handle_approach/handle_approach_node.py` — 移除 VisionPromptClient
  - `cuttofo_skill_handle_approach/handle_approach_workflow.py` — 移除 vision_prompt param + publish_prompt
  - `cuttofo_skill_handle_approach/handle_approach_config.py` — 移除 prompt params
  - `cuttofo_skill_handle_approach/config/handle_approach_params.yaml` — 移除 prompt fields
  - `cuttofu_vision/config/vision_params.yaml` — text_prompt: cucumber → object
- Next steps:
  - 新建 `cuttofo_skill_tofu_perception` 包（豆腐复活关键缺口）
  - 后续补充 handle 感知节点

## 2026-06-01 18:30 Local Time — SAM3 prompt late-joiner 修复：burst publish + 安全默认词

- Problem: `cucumber_perception_node` 在 `__init__` 末尾只发了一次 "cucumber"，但此时 SAM3 的 subscription 还没注册到 DDS，消息丢失。SAM3 一直使用默认 `text_prompt: object`，检测到桌面上的杂乱物体并下发虚假数据，可能让机械臂误动。
  - Root cause: ROS 2 DDS late-joiner — publisher 在 subscriber 注册之前发送，消息永远到不了。
- Fix:
  - `cucumber_perception_node.py`: 替换单次 publish → burst timer（每 0.1s × 5s = 共 50 次），burst 结束后保留 heartbeat（每 5s 一次）。新增 3 个可配置参数：burst_duration_sec, burst_interval_sec, heartbeat_interval_sec。
  - `vision_params.yaml`: 默认 prompt 从 `object` 改为 `__none__`（不合法的物体名，SAM3 检不出任何东西），防止 prompt 未更新时误检测。
  - 对应的 params YAML `cucumber_perception_params.yaml` 添加 burst 参数文档。
- 实测验证成功：SAM3 log 显示 `Updated detection prompts to: ['cucumber']`，不再乱检测。
- Files changed:
  - `cuttofo_skill_cucumber_perception/cucumber_perception_node.py` — 单次 publish → burst timer + heartbeat
  - `cuttofo_skill_cucumber_perception/config/cucumber_perception_params.yaml` — 加 burst 参数段
  - `cuttofu_vision/config/vision_params.yaml` — text_prompt: object → __none__
- Next steps:
  - 黄瓜全流程实物切割测试

## 2026-06-03 16:38 Local Time — 豆腐 TCP offset 拆分：黄瓜/豆腐各用独立参数

- Objective: 为黄瓜和豆腐任务分别使用不同的右臂 TCP offset 参数。
- Work completed:
  - `arms.yaml` 中为右臂新增 `tofu_tcp_offset: [0.03089, 0.21506, 0.28620]`（初始值与 `tcp_offset` 一致，可独立调）
  - `loader.py` 新增 `get_task_tcp_offset(arm_config, task_name)` helper
  - `XcoreArmAdapter.__init__` 新增 `tcp_offset_override` 可选参数
  - `tofu_prepare_workflow.py`：根据 profile 决定使用 `tcp_offset`（cucumber）还是 `tofu_tcp_offset`（tofu）
  - `tofu_cut_round_workflow.py`、`tofu_vertical_cut_workflow.py` 也同步使用 `tofu_tcp_offset`
- Business logic impact: 豆腐全流程（prepare → cut_round → vertical_cut）默认使用 `tofu_tcp_offset`；黄瓜不受影响，继续使用 `tcp_offset`。
- Problems encountered: 无
- Verification: 全部 5 个修改文件 linter 检查通过，无错误。
- Files changed:
  - `cuttofo_skill_common/config/arms.yaml`
  - `cuttofo_skill_common/config/loader.py`
  - `cuttofo_skill_common/arm/xcore_arm_adapter.py`
  - `cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py`
  - `cuttofo_skill_tofu_cut_round/tofu_cut_round_workflow.py`
  - `cuttofo_skill_tofu_vertical_cut/tofu_vertical_cut_workflow.py`
- Next steps:
  - 调优 `tofu_tcp_offset` 参数使豆腐放刀位置正确
  - 黄瓜全流程实物切割测试

## 2026-06-03 17:39 Local Time — Phase6 Vision 参数覆写迁移 + 全流程编排分析

- Objective: 将老版 cuttofo_xcore 中 `cutting.phase6_vision` 的「进入竖切预备前动态切换感知参数」逻辑迁移到新架构。
- Work completed:
  - **配置 (`tofu_prepare_params.yaml`)**：`after_rotation_2` profile 新增 `vision_override` 块（33 个参数，包含 OBB 分位数、buffer、corner_mode 等，对齐老版 `phase6_vision`）
  - **感知节点 (`tofu_perception_node.py`)**：
    - 添加 `add_on_set_parameters_callback(self._on_set_parameters)`：按白名单更新 33 个运行时参数缓存，buffer_size/min_buffer_frames/obb_depth_median_frames 变化时重建 deque
    - 添加 `~/reset_state` (Trigger) 服务：清空 `_corner_buffer`、`_depth_frame_buffer`、`_stable_frames`、health 等运行时状态
  - **通用 helper (`cuttofo_skill_common/perception/tofu_perception_override.py`)**：
    - 定义 37 个可覆写参数的白名单（`VISION_OVERRIDE_TYPES`）
    - `filter_vision_override()` — 过滤白名单
    - `apply_tofu_perception_override()` — 封装 `/tofu_perception_node/set_parameters` + `~/reset_state` 的阻塞调用
  - **prepare workflow (`tofu_prepare_workflow.py`)**：在 `use_vision` 分支插入 `vision_override` 检测 → 推送到感知节点 → reset → 同步 VisionGeometryTracker buffer 参数 → 再进入原有的 `wait_valid()`
  - 补充 `package.xml` 依赖（`rcl_interfaces`、`std_srvs`），更新 `__init__.py` 导出
  - **编译验证**：3 包（cuttofo_skill_common、cuttofo_skill_tofu_perception、cuttofo_skill_tofu_prepare）编译通过，语法检查 0 错误
  - **运行时验证**：
    - `ros2 param set /tofu_perception_node obb_top_y_percentile 90.0` 成功
    - `ros2 param set /tofu_perception_node obb_bounds_u_percentile_low 100.0` 成功
    - `ros2 service call /tofu_perception_node/reset_state std_srvs/srv/Trigger` 返回 success=True
  - 补充前一工作单元：分析第一次全流程编排启动日志，确认 `vision_timeout_s: 5.0` 过短，已改为 15.0；分析 `realsense2_camera_node` 报 `No RealSense devices were found`（USB 问题）、`hand_eye_static_tf_publisher` 等待 camera_link TF、SAM3 初始化后等待彩色图等启动竞态问题
- Business logic impact: `after_rotation_2` (phase6) 预备步骤将使用专用视觉参数（obb_top_y_percentile=90.0, obb_bounds_u_percentile_low=100.0 等主要分位数调整），与老版 cuttofo_xcore 的 phase6_vision 行为一致。
- Problems encountered:
  - colcon build 时 `cuttofo_skill_common` 等包名因 install 目录已在 underlay 中，需加 `--allow-overriding`（已处理）
  - `tofu_perception_override.py` 使用 `node.get_clock().now()` 做超时，后发现 SingleThreadedExecutor 可能不刷新时钟 → 改为 `time.monotonic()` + `time.sleep()`
- Verification:
  - 3 包 colcon build 通过
  - `from cuttofo_skill_tofu_prepare.tofu_prepare_config import get_prepare_profile` 加载 `after_rotation_2` 返回 `vision_override` 33 个参数，`obb_top_y_percentile=90.0`
  - `tofu_perception_node` 启动正常
  - 动态 `ros2 param set` 成功，reset_state 服务返回 success
- Unverified items:
  - 实机 `after_rotation_2` action 测试（需 RealSense + 豆腐在视野内）
  - 全流程编排第 5 步触发 vision override
- Files changed:
  - `cuttofo_skill_tofu_prepare/config/tofu_prepare_params.yaml` — `after_rotation_2` 加 `vision_override`
  - `cuttofo_skill_tofu_perception/tofu_perception_node.py` — 加 `_on_set_parameters` + `_handle_reset_state` + `_reset_runtime_state`
  - `cuttofo_skill_tofu_perception/package.xml` — 加 `rcl_interfaces`、`std_srvs`
  - `cuttofo_skill_common/perception/tofu_perception_override.py` — **新建**，封装覆写客户端
  - `cuttofo_skill_common/perception/__init__.py` — 导出新符号
  - `cuttofo_skill_common/package.xml` — 加 `rcl_interfaces`、`std_srvs`
  - `cuttofo_skill_tofu_prepare/tofu_prepare_workflow.py` — vision override 插入点
  - `cuttofo_orchestrator/config/tofu_workflow_params.yaml` — `vision_timeout_s: 5.0` → `15.0`
- Next steps:
  - 全流程编排启动测试（T1: controllers, T2: `tofu_workflow_execute.launch.py`）
  - 第二阶段 `prepare:after_rotation_1` + `cut_round:round_2` 硬件测试
  - 竖切 `vertical_cut` 硬件测试

## 2026-06-04 09:56 Local Time — 豆腐全流程调试：return-to-prepare 对齐 xcore + 崩溃修復 + Phase7 竖切迁移

- Objective: 把豆腐全流程跑通，修复 bugs，对齐老版 cuttofo_xcore 行为。
- Work completed:
  - **Bug1: 第一次横切完成回 prepare 位置不移动**：原因是新架构把 return 分成了 retract + target 两段 RT，且偏移公式有 `return_retract_m` 预退长度。已完整迁移 xcore 的 `_return_to_prepare_waypoints()` 单路点逻辑，去掉 `return_retract_m` / 分段/`return_to_prepare_segments`。改为 `source_phase: phase3_first_cut` 读取 cut 几何参数计算 `-(cycles-1)*step + return_extra_offset_m`。
  - **Bug2: touch 继续文件后崩溃（cut_round resume timeout）**：orchestrator 检测到 touch 文件后调用 `/tofu_cut_round/resume` 服务，但 action 回调中 `_wait_for_resume` 只等 resume 服务而没监控文件，导致服务 30s 超时。改为在 `_wait_for_resume` 内部直接轮询 `wait_continue_file`（与老版 xcore 一致），resume 服务仅作备用。
  - **Bug3: 继续后 `prepare:after_rotation_1` 发 goal 超时**：`XcoreArmAdapter` 全部用 `rclpy.spin_until_future_complete(self._node, ...)`，这在 action callback 里做嵌套 spin 导致节点变成僵尸（不再处理后续 goal）。已全部替换为 `_wait_future()` 纯睡眠轮询。
  - **Bug4: Phase7 竖切逻辑冗余**：当前竖切用了通用的路点生成 + 分段 push/尾推，和老版 xcore 的 `_execute_phase7_cut()` 结构不一致。已完整迁移：
    - 代码：`tofu_vertical_cut_workflow.py` 重写为 xcore 的分段模式（上半段 → mid-push → 下半段 → tail-push，每段独立 RT 调用）
    - 参数：`tofu_vertical_cut_params.yaml` 改为与 `phase7_third_cut` 一致（cycles=11, cut_move=0.058, push_lift_y=0.024, push_lift_speed=0.05, mid_push_speed=0.020, push_tail_speed=0.040, tail_move_cut_speed=0.10 等）
    - Phase7 固定使用 `use_impedance=False`（force_rt_position），不再尝试阻抗/回退
- Business logic impact:
  - return-to-prepare 恢复为老版单路点 RT 位置移动（无阻抗 fallback），对齐 phase4/6
  - touch 继续文件由 action server 内轮询，不再依赖 orchestrator 调用 resume 服务
  - `XcoreArmAdapter` 不再嵌套 spin，避免阻塞 action server 节点
  - Phase7 竖切与老版 xcore 结构一致，三段推送（mid-push fwd/ret/bwd/ret + tail-push）共 11 次单独 RT 调用
- Problems encountered:
  - 第一次 Phase7 迁移后用户测试证实效果对齐老版（`验证结果确实对齐了`）
- Verification:
  - 4 包编译通过（cuttofo_skill_common, cuttofo_skill_tofu_prepare, cuttofo_skill_tofu_cut_round, cuttofo_orchestrator, cuttofo_skill_tofu_vertical_cut）
  - linter 检查通过，无错误
  - 实机测试：第一次横切 → return-to-prepare → wait pose → touch 继续 → 第二次横切 3 步对齐老版
  - Phase7 竖切用户确认效果对齐老版（`测试下来效果确实对齐了`）
- Unverified items: 下一步全流程通跑（目前到第二次横切后继续崩溃，touch 流程尚未测试）
- Files changed:
  - `cuttofo_skill_tofu_cut_round/.../tofu_cut_round_workflow.py` — return 单路点 + 文件轮询 + source_phase 解析
  - `cuttofo_skill_tofu_cut_round/config/tofu_cut_round_params.yaml` — round_1 round_2 return 去掉 retract_m
  - `cuttofo_skill_common/.../trajectory/cut_round_path.py` — 重写 `return_to_prepare_waypoints()` 匹配 xcore
  - `cuttofo_skill_common/.../arm/xcore_arm_adapter.py` — 去掉 `rclpy.spin_until_future_complete`
  - `cuttofo_orchestrator/.../tofu_task_orchestrator.py` — 去掉 resume 调用 + 双等待
  - `cuttofo_skill_tofu_vertical_cut/.../tofu_vertical_cut_workflow.py` — 重写为 xcore 分段模式
  - `cuttofo_skill_tofu_vertical_cut/config/tofu_vertical_cut_params.yaml` — 对齐老版参数
- Next steps:
  - 用户当前测试到第2次继续文件阶段，等待用户反馈是否继续调通第2次继续 + 竖切
  - 黄瓜全流程切割测试待补
