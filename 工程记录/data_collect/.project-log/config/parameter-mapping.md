# Parameter Mapping

## DROID QC Metrics (Implemented in Scripts)

| 指标 | 计算方法 | 脚本中的实现 | 输出位置 |
|------|----------|--------------|----------|
| idle frame 比例 | action norm 低于阈值连续帧计数 | `visualize_droid_local.py`, `droid_qc_deep_research.py` | 报告 / stdout |
| spike 数量/比例 | action 差分超过 3σ | `droid_qc_deep_research.py` | `droid_qc_summary.json` |
| saturation 比例 | action 绝对值接近 ±π 的比例 | `droid_qc_deep_research.py` | `droid_qc_summary.json` |
| jerk | action 二阶差分 | `droid_qc_deep_research.py` | `droid_qc_summary.json` |
| 语言指令覆盖率 | 非空 language_instruction 比例 | `droid_qc_deep_research.py` | `droid_qc_summary.json` |
| NaN/Inf 检出 | 数组完整性检查 | `droid_qc_deep_research.py` | `droid_qc_summary.json` |

## TeleDex QC Metrics (Proposed Mapping, Not Implemented)

| 指标 | TeleDex 数据源 | 对应 DROID 指标 | 状态 |
|------|----------------|-----------------|------|
| 同步有效性 | `sync_validation_is_valid` | 无直接对应（DROID 隐式保证） | 可直接读取 |
| 同步误差 | `sync_validation_max_diff`, manifest `sync_error` | drop_rate / sync_error | 待定义阈值 |
| 关节 idle | `qvel` 或 `actions` norm | idle frame | 待实现 |
| action spike | `actions` 差分 | spike | 待实现 |
| 关节饱和 | `qpos` / `actions` 范围 | saturation | 待适配（维度不同） |
| 运动平滑性 | `qvel` 或 `actions` 二阶差分 | jerk | 待实现 |
| 标定质量 | `camera_info.json` | calibration_error | 待实现 |
| 任务语义 | metadata 任务描述字段 | language_instruction | 字段名待确认 |

## Quality Score Formula (Draft)

来自 DROID QC 报告，尚未映射到 TeleDex 字段：

```text
Q_total = 0.2*Q_integrity + 0.2*Q_sync + 0.2*Q_visual + 0.2*Q_motion + 0.2*Q_task
```

各子分项与 TeleDex 字段的精确映射在节点 D 完成时确定。

## Notes

- 参数映射是 B->C 和 C->D 的核心交付物之一
- 不猜测未确认的 metadata 字段名
