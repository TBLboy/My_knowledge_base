# Config Schema

## Research Project Config

本项目调研阶段无运行时配置文件。以下为**已知的固定路径与环境参数**。

| Parameter | Type | Default | Valid Range | Runtime Mapping | Used By | Requires Restart | Notes |
|-----------|------|---------|-------------|-----------------|---------|------------------|-------|
| `DROID_DATA_DIR` | path | `data/droid/droid_100/` | 存在的目录 | 脚本硬编码或相对路径 | DROID 分析脚本 | N/A | 未抽象为配置项 |
| `DROID_VIS_OUTPUT` | path | `analysis/droid_visualization/` | 可写目录 | 脚本硬编码 | `visualize_droid_local.py` | N/A | 未抽象为配置项 |
| `CONDA_ENV` | string | `droid_study` | 已创建的环境名 | `conda run -n droid_study` | 所有 DROID 脚本 | N/A | 由 setup 脚本创建 |

## Proposed QC Thresholds (Research Draft, Not Config)

以下来自 DROID 调研的**建议阈值**，尚未实施为配置文件：

| Parameter | Type | Suggested Default | Source | Status |
|-----------|------|-------------------|--------|--------|
| `idle_frame_threshold` | int | 10 帧 | DROID QC 报告 | draft |
| `spike_sigma` | float | 3.0 | DROID QC 报告 | draft |
| `saturation_warning_ratio` | float | 0.15 (15%) | DROID QC 报告 | draft |
| `min_episode_length` | int | 87 帧（DROID 参考） | DROID 样本统计 | draft |
| `max_episode_length` | int | 600 帧（DROID 参考） | DROID 样本统计 | draft |
| `sync_error_max` | float | Unknown | TeleDex manifest | open |

## Notes

- 实施阶段应将 QC 阈值抽象为独立配置文件（如 `qc_config.yaml`）
- 当前不创建配置文件，避免暗示已进入实施阶段
