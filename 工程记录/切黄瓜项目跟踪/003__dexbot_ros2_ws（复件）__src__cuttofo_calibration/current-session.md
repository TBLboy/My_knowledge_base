# Current Session

## Last Updated

- 2026-05-12

## Current Objective

- GUI 性能优化 + 日志持久化

## Completed This Session

- **关节角度后台线程化**: SDK `get_joints()` 从主线程移到后台线程（10Hz），主线程只读缓存，GUI 不再冻结
- **工作线程事件驱动**: 移除固定 `time.sleep(0.03)`，有帧立即处理
- **日志持久化**: 启动时在 `log/` 目录创建带时间戳的文件，终端输出同步写入文件
- **Bug 修复**: `_joints_worker` 缺少 `import time` 导致线程崩溃

## Problems And Resolutions

- `_joints_worker` 缺少 `import time` → 添加即可
- 关节角度一旦断开应清缓存 → `else: self._cached_joints = None`

## Files Changed

- `view/control_panel.py` — 关节后台线程；`import time`
- `view/camera_panel.py` — 移除固定 sleep
- `view/calibration_gui.py` — FileHandler 日志持久化
- `.project-log/progress.md`

## Current State

- GUI 性能已优化，关节角度零阻塞
- 日志自动保存到 `log/` 目录
