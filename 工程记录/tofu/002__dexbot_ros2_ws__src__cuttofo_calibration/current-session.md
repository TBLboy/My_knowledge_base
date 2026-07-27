# Current Session

## Last Updated

- 2026-05-21 19:10 CST

## Current Objective

- ChArUco 标定流水线已实现并验证通过，下一步等待用户把板子装到手背后，执行内参标定和手眼采样。

## Completed This Session

- 完成并验证 ChArUco 标定流水线代码：
  - `charuco_detector.py`
  - `camera_intrinsics_calibrator.py`
  - `charuco_capture_node.py`
  - `charuco_handeye_solver.py`
- 更新 `setup.py` 使新工具可通过 ROS2 console entry points 启动。
- 验证 OpenCV 4.5.4 兼容性和 ChArUco board 检测成功。
- 生成并验证了 4×4 @ 14mm 的手背板，作为当前可执行方案。

## Problems And Resolutions

- 需要用户把打印好的板子固定到手背后才能开始实机采集。
- 4×4 小板对距离比较敏感，手背到相机建议保持在 20-30cm。

## Files Changed

- `cuttofo_calibration/business/charuco_detector.py`
- `cuttofo_calibration/scripts/camera_intrinsics_calibrator.py`
- `cuttofo_calibration/scripts/charuco_capture_node.py`
- `cuttofo_calibration/scripts/charuco_handeye_solver.py`
- `cuttofo_calibration/scripts/__init__.py`
- `config/board.yaml`
- `setup.py`
- `.project-log/current-session.md`
- `.project-log/progress.md`

## Current State

- 代码已就绪，可进入实机采集阶段。

## Next Steps

1. 用户把板子固定到手背并尽量保证平整。
2. 运行 `camera_intrinsics_calibrator` 做 RGB 内参标定。
3. 运行 `charuco_handeye_capture` 采集 20-30 个样本。
4. 运行 `charuco_handeye_solver` 输出 `validation_report.yaml` 和最终外参。

## Current State

- GUI 性能已优化，关节角度零阻塞
- 日志自动保存到 `log/` 目录
