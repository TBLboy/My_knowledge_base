# Internal API

## Scope

本项目无应用内模块 API。此处记录调研工程内部的**数据接口约定**——即各脚本和文档之间共享的数据路径与产物格式。

## Data Paths

| 路径 | 类型 | 消费者 |
|------|------|--------|
| `data/droid/droid_100/` | TFRecord 数据集 | `analyze_droid_local.py`, `visualize_droid_local.py`, `droid_qc_deep_research.py` |
| `analysis/droid_visualization/` | PNG 可视化输出 | 人工审阅 |
| `doc/droid_qc_research/` | 调研报告 + JSON 摘要 | 整合报告、领导交付 |
| `doc/robot_dataset_qc_curation_survey.md` | 综合调研初稿 | 整合报告 |

## Script Interfaces

### analyze_droid_local.py

- 输入：本地 TFDS 数据集（`droid_100/`）
- 输出：stdout 统计信息（episode 结构、长度、action 范围）
- 副作用：无持久化输出

### visualize_droid_local.py

- 输入：本地 TFDS 数据集
- 输出：`analysis/droid_visualization/*.png`
- 功能：三路相机图像、action 曲线、idle/spike 检测

### droid_qc_deep_research.py

- 输入：本地 TFDS 数据集
- 输出：
  - `doc/droid_qc_research/DROID_QC调研报告.md`
  - `doc/droid_qc_research/droid_qc_summary.json`

## Future Linker TeleDex QC API (Not Implemented)

调研阶段不定义。节点 D 完成后可能在方案建议中描述建议的 QC 函数签名，例如：

```python
# 方案建议级别，非当前实现
def compute_qc_metrics(telemetry: np.lib.npyio.NpzFile) -> dict: ...
def classify_episode(metrics: dict) -> str: ...  # accepted | warning | repair | rejected
```

## Notes

- 实施阶段的 internal API 应在 QC 系统开发时单独定义并更新本文件
