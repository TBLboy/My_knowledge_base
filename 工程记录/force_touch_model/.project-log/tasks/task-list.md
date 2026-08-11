# Task List

Active goal: 建立统一矿泉水瓶花生倾倒 benchmark，并以真机成功率驱动模型迭代

当前任务链：

- TASK-021：benchmark 数据采集与 LeRobot v3.0 转换（ready）
- TASK-022：语义、子任务和多描述标注规范（pending）
- TASK-023：baseline 真机部署与成功率评测（pending）
- TASK-024：根据真机失败问题设计首轮优化（pending）
- TASK-025：VLM 时间边界诊断实验与 coarse-to-fine 改造（done，技术链路已闭环；诊断实验转 TASK-036）
- TASK-036：VLM 时间边界 P0/P1 诊断与 coarse-to-fine 小批量实验（done，结论：cam_top+gemma3:27b 当前不胜任，不进入 287 条生产）
- TASK-037：新数据集 VLM 标定测试业务要求与范围（cancelled，用户真实测试后 VLM 子任务识别精度仍差，项目暂停）
- TASK-038：VLM 示范 episode 可选择实现（done，两组多选已落地并通过测试）
- TASK-039：Qingdao pouring GR00T 单 pass 训练（done，14051/14051，checkpoint 014051 已保存）

当前建议起点：单 pass 训练已完成，下一步根据用户决定是否进入真机评测或继续调参。
