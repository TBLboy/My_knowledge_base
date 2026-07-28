# Runtime Config

## Current State

调研项目无运行时服务，无 runtime config。

## DROID Analysis Runtime

分析脚本运行时依赖：

| 依赖 | 获取方式 |
|------|----------|
| Python 3.x | conda 环境 `droid_study` |
| TensorFlow + TFDS | `setup_droid_env.sh` 安装 |
| 本地数据 | `data/droid/droid_100/` 已下载 (~2.1 GB) |
| GPU | 非必须（分析脚本可在 CPU 运行） |

## TeleDex Data Analysis Runtime (Future)

当获取到实际 TeleDex 采集样本后，分析运行时将需要：
- NumPy / SciPy（telemetry.npz 解析）
- OpenCV 或类似库（视频帧分析）
- 可选：ROS2 bag 读取工具（如需分析 raw MCAP）

当前未配置，待 Q-20260616-004 解答后决定。

## Notes

- 本文件在实施阶段应记录 QC 服务的运行时参数（端口、并发、存储路径等）
