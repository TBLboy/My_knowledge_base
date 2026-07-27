# Software Architecture

## Project Type

本项目是**调研工程**，不是可运行的生产系统。软件架构描述的是调研工作流、分析脚本与文档产物的组织方式。

## Directory Layout

```text
data_collect/
├── .project-log/          # 工程记忆与业务逻辑（本 skill 维护）
├── doc/                   # 调研报告与文献综述
├── scripts/droid/         # DROID 数据集分析脚本
├── data/droid/droid_100/  # 本地 DROID 样本数据
└── analysis/              # 分析输出（可视化 PNG 等，按需生成）
```

## Research Workflow Layers

```text
Layer 1: 文献与公开数据集调研
  - 输入：论文、官网文档、公开数据集
  - 输出：调研报告（Markdown）、QC 规则清单

Layer 2: 本地数据集实证分析
  - 输入：下载的 TFRecord / RLDS 数据
  - 工具：scripts/droid/ 下的 Python 脚本
  - 输出：统计 JSON、可视化、可迁移 QC 规则

Layer 3: 平台格式适配分析
  - 输入：Linker TeleDex 数据说明文档
  - 输出：QC 指标适配方案、清洗策略建议

Layer 4: 整合交付
  - 输入：Layer 1-3 成果
  - 输出：完整调研报告
```

## Analysis Scripts (DROID)

| 脚本 | 职责 | 环境 |
|------|------|------|
| `setup_droid_env.sh` | 创建 conda 环境 `droid_study` | bash |
| `download_droid.sh` | 从 GCS 下载 DROID 数据 | bash |
| `analyze_droid_local.py` | 数据结构分析与完整性验证 | `droid_study` |
| `visualize_droid_local.py` | 图像与 action 轨迹可视化、批量 QC | `droid_study` |
| `droid_qc_deep_research.py` | 深度 QC 指标统计与报告生成 | `droid_study` |

## GUI / Business Logic Separation

不适用。本项目无 GUI，调研逻辑与脚本分析分离：
- 调研逻辑以 `.project-log/business-logic/` 为真源
- 分析脚本仅服务于调研验证，不作为最终交付物

## Notes

- 现阶段不开发 Linker TeleDex QC 实施代码
- 分析脚本仅针对 DROID 公开数据集，用于提取可迁移 QC 规则
