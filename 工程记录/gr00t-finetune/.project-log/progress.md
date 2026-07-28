# Progress

> 更新时间：2026-07-23

## 当前状态

当前阶段：**verification / documentation**。30,000-step 重训与训练集 open-loop 验证已完成；代码地图已完成叙事重构和开头结构总览补充；当前没有训练/评估进程。

**当前结论：`implemented-verified`（训练与 open-loop 证据通过），不是整体验收完成。**

## 任务进度

| # | 任务 | 状态 | 结果 |
|---|---|---|---|
| 1 | 搭建 GR00T N1 微调环境 | ✅ 完成 | `gr00t_n1`：PyTorch 2.9.0+cu128、flash-attn 2.8.3、RTX 4090 可用 |
| 2 | 下载并转换训练数据 | ✅ 完成 | 148 个有效 episode、47,250 帧、右臂 + O6 连续 13D、3 路相机 |
| 3 | 下载 GR00T-N1.7-3B 模型 | ✅ 完成 | base model 约 6.5GB，已迁移到 `/mnt/data/gr00t-finetune/models/gr00t_n1_base` |
| 4 | 定义 embodiment 配置 | ✅ 完成 | `linkerhand_right_o6_config.py`，右臂 7D + O6 手 6D |
| 5 | 计算 normalization stats | ✅ 完成 | 13D `stats.json` 已生成并用于训练 |
| 6 | 微调启动/低显存配置 | ✅ 完成 | batch=1、gradient accumulation=8、paged AdamW 8-bit、gradient checkpointing、workers=0 |
| 7 | 30,000-step 正式重训 | ✅ 完成 | constant LR=5e-5、warmup=1500、约 5.3 个全量 pass，final loss 约 0.038 |
| 8 | checkpoint-30000 训练集 open-loop 验证 | ✅ 通过 | 4 条轨迹平均 MSE=23.62、MAE=1.15，显著优于旧 checkpoint 与 current-state baseline |
| 9 | 未见轨迹泛化 / 真机闭环 | ⏳ 待执行 | 这是当前关键未验证项；不自动启动真机或长时间评估 |
| 10 | GR00T 代码工程地图：内容基线 | ✅ 完成 | `docs/gr00t-codebase-map.md`：项目名片、目录职责、功能地图、任务路径、扩展与阅读索引 |
| 11 | GR00T 代码工程地图：首次阅读体验重构 | ✅ 完成 | 主文档已重构为"指南→概览→完整旅程→分支路径→扩展→索引"；20 路径校验通过 |
| 12 | GR00T 代码地图：名称统一 | ✅ 完成 | 主文档及项目记录统一使用“GR00T N1.7 代码地图” |
| 13 | GR00T 代码地图：主流程表述规范化 | ✅ 完成 | 将“完整旅程/第一站”等口语化隐喻改为“端到端主流程”和正式流程阶段名称 |

## 关键证据

- 最终 checkpoint：
  `/mnt/data/gr00t-finetune/outputs/gr00t_n1_right_o6_13d_retrain/gr00t_n1_right_o6_13d_full_20k/checkpoint-30000`
- 保留 checkpoint：`checkpoint-22400`、`checkpoint-28000`、`checkpoint-30000`
- 验证记录：`.project-log/verification/evidence.yaml#verification-013`
- 评估日志/图表：
  `/mnt/data/gr00t-finetune/outputs/gr00t_n1_right_o6_13d_retrain/open_loop_eval/`
- 当前 GPU：约 729 MiB used / 约 23.3 GiB free；无训练进程

## 结果摘要

| 对照 | MSE | 变化 |
|---|---:|---:|
| 旧 20k checkpoint（traj 0） | 717.38 | — |
| current-state baseline（traj 0） | 82.91 | — |
| checkpoint-30000（traj 0） | 13.73 | 相对旧 checkpoint ↓98%，相对 baseline ↓83% |
| checkpoint-30000（4 条轨迹平均） | 23.62 | 当前最佳已验证结果 |

根因判断：此前失败主要来自训练暴露量不足（约 0.44 pass）；本次增加到约 5.3 passes 后，模型已表现出有效动作预测能力。

## 文档交付：GR00T 代码工程地图

主汇报文档：`docs/gr00t-codebase-map.md`。其定位是工程导航说明书，不是本次微调工作报告：读者先获得项目名片，再获得仓库的目录、功能和任务路线地图，最后才按需要进入技术附录。

| 文档层次 | 文件 | 用途 |
|---|---|---|
| 主汇报 | `docs/gr00t-codebase-map.md` | 面向老师展示工程整体结构、已提供能力、入口文件和扩展位置 |
| 技术附录 | `docs/gr00t-engineering-report.md` | 需要进一步解释数据、Processor、模型、训练与评估机制时使用 |
| 证据草稿 | `.project-log/research/gr00t-engineering-report-chapters-01-03.md` | 保留源码、配置、工件和实验事实的可追溯记录 |

主文档当前结构为：

```text
项目名片（模型定位、预训练覆盖、性能/资源边界、系统边界）
→ 仓库全景与目录职责
→ 功能地图与共用核心链路
→ 微调 / 策略与真机 / 评估 / 部署任务路径
→ 新 embodiment、新模态和触觉扩展地图
→ 推荐阅读路线与关键词索引
```

项目名片仅保留建立初印象所需事实：基础 checkpoint 的约 3B 发布口径、VLM + flow-matching DiT 分工、双臂/半人形/人形及 20K 小时 EgoScale 预训练覆盖。性能采用带条件的 L40 基准：1 路相机、4 次去噪时，PyTorch eager 为 128.3 ms / 7.8 Hz，TensorRT 全管线为 38.4 ms / 26.0 Hz；这些数值不替代不同硬件或输入条件下的本机测试。

文档验证证据：主文档已按“阅读指南→仓库结构→工程概览→完整旅程→分支路径→扩展→索引”组织；Markdown fence 成对闭合，源码/示例/部署/使用材料路径存在性检查通过；未出现“README 里说”式资料摘抄表述。系统 Python 的 pytest 收集受 pytest/anyio 插件版本冲突阻断，未把该环境问题表述为仓库测试结果。

### 当前文档重构判断

当前文档的目录、入口和边界事实并非主要问题；问题是先给出了工程师的分类结果（目录树、配置层、功能矩阵、评估层级），而首次读者尚未经历这些概念在一次完整工作中出现的先后关系。因此它更像检索手册，而不是可顺读的说明书。已创建 `task-012`，后续将按“最小完整旅程 → 站点地图 → 分支能力 → 深入索引”重构；在完成前，不应将现有主文档称为已满足首次接触者可读性的最终版本。

结构总览补充后，文档开头现在先回答“仓库有哪些文件夹、每个文件夹做什么”，并明确区分核心模块与数据/产物/环境目录；这些目录随后在完整旅程和分支路径中再次映射到实际调用链。

## 当前风险与边界

- 目前只验证了训练集轨迹 0–3，不能据此宣称未见场景泛化。
- 尚未进行真机 closed-loop；不能据此宣称可直接部署。
- MSE 受 O6 手部 0–100 数值尺度影响，跨动作契约比较需谨慎。
- 扩散采样未固定 seed，单次结果存在采样方差。
- LoRA spike 仍是待选优化项，不是当前训练成功的前置条件。

## 下一步

1. **优先**：评估留出/未见轨迹，固定评估 seed 并比较 checkpoint-22400/28000/30000 收敛趋势。
2. **随后**：在安全条件满足且用户确认后进行真机 closed-loop 测试。
3. **可选**：若泛化不足，再研究数据增强、延长训练或 LoRA/冻结模块等方案。
