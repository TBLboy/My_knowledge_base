# 当前需求摘要

- 当前目标：将 `annotation_workbench/` 交付为 Linux/Ubuntu 上可独立安装和运行的本地 LeRobot v3.0 标注工具包。
- 当前基线：`REQ-002` revision 1，已批准。
- 范围内：包内桌面 GUI、数据集 HTTP 服务、Next.js 可视化前端、FastAPI 标注后端、最小 VLM 对齐实现、安装脚本和独立运行验证。
- 范围外：完整 LeRobot、Ollama/Gemma 权重、Windows/macOS、前端大范围重构、多用户和局域网功能。
- 关键约束：Python 3.11+、Node.js 20 LTS、包内 `.venv`、仅支持 LeRobot v3.0、Ollama 通过环境变量配置、标注原地写入 `meta/lerobot_annotations.json`。
- 阻塞问题：无。外部 `visualize_dataset/`、`lerobot_v1.0/` 和 `serve_local_dataset.py` 保留为备份，但独立包运行时不得读取。

机器可读事实源：`.project-log/requirements/baseline.yaml` 与 `.project-log/business-logic/atoms.yaml`。
