# Branch: charuco-handeye-precision

## Status

- draft

## Purpose

将手眼标定从单个 38mm ArUco baseline 升级为基于 ChArUco 大板 + RGB 内参重标定 + 多样本 + 原始角点观测保存 + 像素级 bundle adjustment 的高精度方案。

目标：
- Stage 1：translation_rmse_mm <= 1.5, rotation_rmse_deg <= 1.0
- Stage 2：translation_rmse_mm < 1.0, rotation_rmse_deg <= 0.7

不替换求解器本身（Shah/Li + MAD + Huber LM 已是 SOTA），改进重点在观测质量与数据建模。

## Start Node

- 当前手眼标定结果 RMSE 2.73mm / 2.13°（8 samples，单 ArUco 38mm，640×480 USB2.1）

## Target Node

- ChArUco 标定 + 像素级 BA 后稳定达到 Level B（<1.5mm / <1.0°）以上，最终冲 Level A (<1.0mm)

## Logic Path

```text
A: 单 ArUco baseline (rmse 2.73mm / 2.13°)
↓
B: ChArUco 板 + 重新标定 RGB 内参 + 20-30 样本 + 原始角点保存
↓
C: SE(3) Huber baseline 复现（<1.5mm 阶段）
↓
D: 像素级 bundle adjustment（冲 <1.0mm）
↓
E: leave-one-out 验证 + 下游切割误差验证
```

## Execution Chain

### Phase 0：可复现实验框架

1. 在 `cuttofo_calibration` 包下新增 `runs/` 输出目录结构：
   ```
   runs/
     run_YYYYMMDD_HHMMSS/
       config.yaml
       camera_intrinsics.yaml
       board.yaml
       raw_images/
       detections/                # 每帧角点 npz/json
       robot_poses/               # 每帧 T_base_tcp
       observations.json          # 汇总（样本 → 帧 → 角点）
       initial_solution.yaml      # Shah/Li 选优结果
       optimized_solution_se3.yaml
       optimized_solution_ba.yaml
       validation_report.yaml
       residuals.csv
       plots/
   ```
2. 所有结果按时间戳归档，禁止覆盖历史。
3. 内部统一单位：米、SO(3)、4×4 齐次矩阵。

### Phase 1：ChArUco 板配置

1. 新增 `business/board_config.py`：
   - 数据类 `BoardConfig{board_type, squares_x, squares_y, square_length_m, marker_length_m, dictionary, measured_square_length_m, ...}`
   - YAML 加载/保存
   - 提供 OpenCV `cv2.aruco.CharucoBoard` 构造方法
   - 默认配置：7×10, square=0.038m, marker=0.030m, DICT_4X4_50（最低 5×7）
2. 用户可在 `config/board.yaml` 内填实测尺寸（卡尺测量后写回）。

### Phase 2：RGB 相机内参重标定

1. 新增独立 ROS2 entry point `camera_intrinsics_calibrator`：
   - 订阅 `/camera/camera/color/image_raw`
   - 接收手动触发（按键/服务）采集 ChArUco 标定图
   - 累积到目标张数（默认 50）后执行 `cv2.aruco.calibrateCameraCharuco`
   - 输出 `camera_intrinsics.yaml`：fx/fy/cx/cy/dist_coeffs/reprojection_error_px
2. 验收门：reprojection_error_px <= 0.50 才允许进入手眼采集，否则要求重采。
3. 标定时严格使用与手眼采集相同的 RGB 流（640×480、15fps、固定曝光）。

### Phase 3：手眼采样（多帧观测）

1. 改造 `business/aruco_monitor.py` →新增 `business/charuco_observer.py`：
   - 不再发布 `geometry_msgs/PoseStamped`，而是订阅原始 RGB + camera_info
   - 每帧执行 ChArUco 检测、亚像素角点（CORNER_REFINE_SUBPIX）
   - 输出帧级观测 `FrameObservation{timestamp, corner_ids, corner_pixels, num_corners, T_cam_board, pnp_reprojection_error_px}`
   - 帧筛选门：corners >= 12，preferred >= 20；pnp_reprojection_error_px <= 0.60，preferred <= 0.35
2. 改造 `business/sample_manager.py` → 新增 `SampleEnvelope`：
   - 一个样本（一个机器人姿态）保存：
     - `T_base_tcp`
     - `joint_angles`
     - `frames_total`、`frames_used`
     - 每帧 `FrameObservation`
   - 有效样本门：valid_frames_min >= 10（preferred >= 20）
3. 采样稳定性门替换为：
   - 机器人停止后 wait_after_stop_s >= 0.8
   - 角点像素漂移 corner_drift_px <= 0.2（理想）
4. 建议样本数 20-30，覆盖 image regions × orientation groups。

### Phase 4：标定流程

1. SE(3) baseline：
   - 对每个有效样本，从有效帧角点中位/均值 → 单次 solvePnP_IPPE_SQUARE_CHARUCO 估算 `T_cam_board`
   - 复用现有 `solve_hand_eye_with_offset()` 跑 Shah/Li + MAD + Huber LM
   - 报告 used/all samples RMSE
2. 像素级 BA：
   - 优化变量：T_base_cam (6) + T_tcp_board (6)
   - 残差：每个有效帧、每个角点的像素重投影误差
   - 损失：huber 或 soft_l1
   - scipy least_squares，trf method
   - 第一版固定内参；第二版允许内参联合优化（带先验）
3. leave-one-out 验证：移除单样本后重训，统计 LOO RMSE。

### Phase 5：验证

1. 报告 all-samples / used-samples / leave-one-out RMSE 三套指标
2. 下游切割误差测试：用最终 T_base_cam 驱动豆腐切割流程，记录切割对齐误差
3. 验收分级 Level A/B/C/Fail（见总目标文档）

## Inputs

- ChArUco 标定板（实物，需打印并实测尺寸）
- RealSense D435i RGB 流：640×480 @15fps，USB 2.1
- 机器人 TCP 位姿（xCore SDK 或 ROS topic）
- 内参重标定结果

## Outputs

- `final_T_base_cam.yaml`
- `optimized_solution_ba.yaml`
- `validation_report.yaml`
- `residuals.csv`
- 历史 run 目录（可对比）

## Assumptions

- 板会被刚性安装在机械臂末端附近（或已贴在原 ArUco 位置）。
- 板会被打印精度足够，且贴在硬质平整背板上。
- 机器人 TCP 位姿在静止后稳定；时间戳与图像时间戳能对齐到 50ms 内。

## Risks

- 板子翘曲/打印缩放会成为系统偏差（Phase 10.2 排查）。
- 机器人停止后过早采图会引入残余抖动（增大 wait_after_stop_s）。
- 内参联合优化可能过拟合（先固定内参跑 BA）。
- ChArUco 在 640×480 下若板太小或太远，角点数会不足（Phase 4.1 帧筛选会丢帧）。

## Open Questions

- 是否保留单 ArUco 监控通道作为 baseline 对比？（建议：保留只读模式，但不再用作主标定）
- 内参联合 BA 是否纳入 v1？（暂定 v1 固定内参，v2 再开）
- 是否需要在 GUI 中加“run 浏览器”视图来比较历史 run？

## Verification Plan

1. 用合成数据验证 SE(3) baseline 与 BA 实现的正确性（已知 ground truth → 0 噪声 RMSE）
2. 用现有 8 样本 ArUco 数据回放，确认改造后 SE(3) baseline 与原结果一致（避免回归）
3. 实机采集 25 个 ChArUco 样本，跑完整流程，验证 Level B 达成
4. 实机 leave-one-out RMSE <= 2.0mm
5. 下游切割误差测试 < 5mm

## Merge Condition

- Stage 1 验收（Level B）通过即可作为新 main 路径
- Stage 2 验收作为长期目标，不阻塞 main 切换

## Notes

- 保留旧 ArUco 求解管线作为 baseline，新管线挂在 `business/` 下新模块。
- 优先保证“P0：换板 + 重标内参 + 多样本 + 保存原始观测”闭环，再叠加 BA。
- BA 的最大价值在第二阶段（<1.0mm），第一阶段 Shah/Li + LM 通常已够 1.0–1.5mm。
