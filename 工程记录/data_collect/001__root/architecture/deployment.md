# Deployment

## Current Stage

调研阶段，无生产部署。

## Local Analysis Environment

| 组件 | 配置 |
|------|------|
| Conda 环境 | `droid_study`（由 `scripts/droid/setup_droid_env.sh` 创建） |
| 数据目录 | `/home/tbl/Project/data_collect/data/droid/droid_100/` |
| 可视化输出 | `/home/tbl/Project/data_collect/analysis/droid_visualization/` |

## Future Deployment (Out of Scope)

以下属于调研结论中可能建议的方向，**当前不实施**：
- Linker TeleDex 采集端实时 QC 模块
- 后处理流水线自动 QC / 清洗服务
- 数据分层存储（accepted / warning / repair / rejected）

## Notes

调研交付物为 Markdown 文档与方案建议，不包含部署配置。
