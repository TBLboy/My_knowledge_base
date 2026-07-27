# Current Session

- 当前阶段：research / documentation — GR00T 代码地图已完成结构总览补充
- 当前会话：2026-07-23 GR00T 黑盒转白盒研究
- 活跃目标：完成一份以目录职责、功能入口和任务代码路径为主线的 GR00T 代码工程地图，并保留源码证据与后续扩展边界。

## 已确认
- 形式 A：预计 15 分钟口述 + 可投屏 Markdown。
- 正式汇报稿已生成：`docs/gr00t-engineering-report.md`。此前误产出的 `docs/gr00t-teacher-report.md` 已移除，不作为项目产物。
- 报告主线应是代码工程结构、调用路径、模块边界与可扩展性。
- 本次右臂 O6 13D 训练是映射案例，不是报告主线。
- 用户补充的模型参数量、L40 推理延迟和预训练覆盖已记录为用户提供事实，待官方一手证据核对。
- 最终汇报文档结构已确认为 11 个主体章节：执行摘要、模型定位、代码仓、数据、多模体、模型、训练、推理评估、13D 映射、扩展、风险结论。
- 每一节必须引用具体源码文件、类/函数/配置，必要时摘录短代码；训练经历仅作为映射案例。

## 当前讨论记录与素材
- 讨论记录：`.project-log/research/gr00t-engineering-report-notes.md`
- 学习素材：`docs/gr00t-whitebox-guide.md`、`docs/gr00t-code-deep-dive.md`

## 本会话已新增
- 已完成第 1—11 章的研究草稿：`.project-log/research/gr00t-engineering-report-chapters-01-03.md`（文件名沿用，当前已含完整 11 章）。
- 草稿以源码/权重元数据为主要证据，包含模型定位与参数口径表、仓库模块责任表、训练/推理调用图、13D 案例映射和待核对项。
- 第 4 章已完成数据系统的七个小节：对象层级、LeRobot 存储契约、episode→step 时间窗口、shard/schedule、stats/归一化、Processor/collator、13D 失效边界。
- 完成一次最小只读实测：使用训练输出保存的 `processor/` 和数据集 episode 0 的 `t=0`，生成 `state=(1,1,132)`、`action=(1,40,132)`、`action_mask` 有效元素 208、三图对应的 Qwen inputs；未加载完整模型、未训练、未改动数据。
- 已追加第 5—11 章：多模体适配（tag/config/projector/mask）、Qwen3-VL + flow-matching DiT 模型张量流、训练与 checkpoint、Policy/open-loop/控制边界、13D 端到端映射、触觉扩展路线、风险与研究结论。
- 本轮新增的关键边界：当前训练 `eval_strategy: 'no'` 且 `enable_open_loop_eval: false`，数据工厂也不支持 HF eval set；这表示训练循环不自动评估。训练后已对 checkpoint-30000 在 4 条训练集轨迹运行独立 open-loop（平均 MSE 23.62、MAE 1.15），但尚未进行未见轨迹、仿真闭环或真机闭环评估。训练达到 30,000 step 和末尾 batch loss 不能代替任务成功率证据。
- 已完成 `Gr00tN1d7Config` 源码复核：草稿模型核心参数与 checkpoint/final config 对齐；已补充源码默认、base checkpoint、13D final config 的对照表，并修正 `select_layer=16` 的表述为“保留前 16 个语言层后的最终 hidden state”。
- 研究草稿不是正式老师汇报稿；用户已明确触发，现已由其压缩生成正式稿。

## 本轮正式稿产物与校验
- 正式稿：`docs/gr00t-engineering-report.md`，11 个主体章节 + 证据索引；以调用图、表格、短段落和引用块组织，避免将训练过程作为主线。
- 关键事实均在正文中标注源码、配置或工件位置；Markdown 校验已通过：11 章完整、6 个 fence 成对闭合。
- 已将训练内 `eval_strategy: no` / `enable_open_loop_eval: false` 与训练后独立评估明确区分：前者表示 Trainer 不自动评估；后者已对 `checkpoint-30000` 的训练集轨迹 0–3 运行 open-loop（400 step、horizon 16、4 去噪），平均 MSE 23.62、MAE 1.15，证据为 `.project-log/verification/evidence.yaml#verification-013`。
- 正式稿不将上述训练集 open-loop 结果表述为未见泛化、真机闭环成功率或安全性证据。
- 已完成 `gr00t_n1/README.md` 审阅，并分别更新研究草稿与正式稿：补入官方工作流、LeRobot/Tag 契约、relative EEF 路线、环境前提、server-client/ReplayPolicy 评估路线、许可证和论文引用；同时标明 README 的发布声明不替代代码/工件证据。README License 节的具体口径为代码 Apache 2.0、模型权重 NVIDIA Open Model License。
- 已按用户要求重写草稿与正式稿中的资料摘抄式表述：面向汇报的正文和证据索引均不再出现 `README` 字样，已将其中的信息自然归入工程事实、适用边界和上游发布/使用材料；保留源码、配置、权重和实测工件作为可追溯证据。

## 汇报方向修正：代码工程地图（2026-07-23）

- 用户重新界定老师所需产物：不是本次 13D 微调的工作报告，也不是数据、参数、算法等局部技术点的集合；应是一份让读者从仓库外部快速建立全局认识的**代码说明书/工程地图**。
- 新主文档应整理并补充工程的发布与使用信息，核心内容为：工程定位、顶层目录及子目录职责、模块依赖方向、已提供功能、每类任务的入口文件和推荐阅读路径。
- 新主文档必须回答“我要做某件事该看哪里”：微调新机器人、策略推理与真机接入、开环评估、仿真/闭环评估、服务端运行、ONNX/TensorRT 部署、新 embodiment 或新模态扩展，分别对应哪些目录、入口脚本、核心类和输出工件。
- 细节研究不作废：`docs/gr00t-engineering-report.md` 降级为技术附录/深入研究材料；`.project-log/research/gr00t-engineering-report-chapters-01-03.md` 保留为可追溯证据草稿。二者不再作为晚间汇报的主稿。
- 拟新建面向汇报的主产物：`docs/gr00t-codebase-map.md`。建议结构为：工程定位 → 仓库全景图 → 功能地图 → 核心运行链路 → 微调入口 → 推理/真机入口 → 评估入口 → 部署入口 → 扩展地图 → 推荐阅读路线 → 关键词索引。
- 写作标准：站在地图外部组织信息；目录、文件、类和任务路线优先；只保留支撑导航所需的细节；避免把参数、一次训练结果或单一数据集案例作为叙事主线。

## 代码工程地图已交付（2026-07-23）

- 主文档已创建：`docs/gr00t-codebase-map.md`（417 行）。它取代此前 11 章技术研究报告，作为面向老师汇报的主稿；`docs/gr00t-engineering-report.md` 保留为可下钻的技术附录。
- 地图内容按“全景 → 功能 → 路径 → 扩展 → 阅读索引”组织，覆盖工程定位、顶层目录职责、功能/依赖图、训练与推理共用的 checkpoint/Processor 契约，以及微调、策略/真机、评估、部署、扩展五类工作入口。
- 每条核心工作路径均以统一任务卡片给出：要完成什么、从哪里开始、主调用/阅读路径、输入、产物和责任边界；明确 `Gr00tPolicy` 输出 action chunk，不替代外部 robot adapter 的控制与安全职责。
- 已将本项目 `examples/linkerhand_right_o6_config.py` 标为本地实验性配置，而非上游通用功能，避免将本地改动写入框架地图。
- 文档静态校验已通过：12 个主体二级标题、3 张 Mermaid 图、Markdown fence 成对闭合；31 个引用的源码/示例/部署/使用材料文件存在性检查全部通过；正文未保留资料摘抄式“README 里说”表述。
- 环境限制已记录：系统 `python3 -m pytest --collect-only` 被用户级 anyio 插件与系统 pytest 的版本冲突阻断（`ModuleNotFoundError: _pytest.scope`）。本次并未执行或声称完成仓库测试；文档路径/结构验证不受影响。
- 用户补充“旅游城市”式阅读需求后，已将主文档开头重构为项目概览和完整旅程：先简要说明 VLA 定位、约 3B checkpoint 口径、VLM + flow-matching DiT 组成、预训练覆盖和系统边界，再进入代码地图。随后新增“仓库结构总览”，区分 8 个核心代码/使用目录、4 个数据与产物目录、4 个环境与记录目录，并列出各目录职责和入口。
- 用户确认主文档名称统一为“GR00T N1.7 代码地图”；标题、附录自称和项目记录中的旧名称已同步替换。
- 用户指出“完整旅程/第一站”等表述过于口语化；第 4 章已改为“端到端主流程”，小节改为“数据集准备与格式转换、具身与模态配置、数据统计量生成、模型训练与 checkpoint 生成、策略加载与动作推理、模型评估与系统验证”等正式流程名称。

## 下一步
1. 晚间汇报使用 `docs/gr00t-codebase-map.md`：先以第 2—4 章建立“仓库结构→工程是什么→数据到动作的完整旅程”，再按需要跳转分支路径或附录。
2. 后续新增触觉或真机 adapter 时，先以第 9 章扩展影响矩阵建立变更范围。
3. 如需运行仓库测试，先进入项目 uv/conda 环境，而非系统 Python；修复当前 pytest/anyio 插件版本冲突后再执行相邻测试。
