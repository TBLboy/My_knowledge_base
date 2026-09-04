# 当前需求摘要

- 当前目标：GOAL-001：完成语言驱动抓取检测完整工程、2 页 CVPR 英文论文与 GitHub 仓库
- 当前基线：未建立
- 范围内：
  - 加载并解析 Grasp-Anything++
  - 图像 + 语言 prompt 输入，五参数抓取矩形输出
  - 模型、训练、评估、推理、可视化
  - GitHub 代码仓库和 2 页 CVPR 英文论文
- 范围外：
  - SOTA 精度
  - 从零实现全部组件
  - 大规模训练或完整数据训练作为必要条件
  - 通过邮件附件提交代码
- 关键约束：
  - 数据集为 Grasp-Anything++
  - 截止时间为接收任务后一周，GPU 受限可接受
  - 最终论文为英文 CVPR LaTeX 模板，含参考文献不超过 2 页
  - PDF 文件名为 FirstName_LastName.pdf
- 阻塞问题：
  - Grasp-Anything++ 的标注格式、划分、坐标与角度约定、官方指标尚未核实

机器可读事实源：`.project-log/requirements/baseline.yaml` 与 `.project-log/business-logic/atoms.yaml`。
