# GR00T 工程理解汇报：研究讨论记录

> 状态：研究记录已完成；正式汇报稿已生成。本文继续作为较完整的证据讨论材料，不替代正式稿。
> 正式产物：`docs/gr00t-engineering-report.md`。

## 1. 问题定义

### 用户目标（已确认）

今晚需要向老师汇报对 GR00T 代码工程的理解。汇报应证明：

1. 已经从“能运行训练脚本但不理解内部”的黑盒状态开始转向白盒理解；
2. 能指出工程关键模块、模块边界、数据与控制流；
3. 能说明后续扩展（例如触觉）应该修改的层级、契约和风险；
4. 训练经历只能作为代码理解的验证案例，不能成为报告主线；
5. 正式汇报文档必须在讨论和研究记录充分后才开始写；该条件已满足，正式稿已于本轮生成。

### 非目标（已确认）

- 不是复述一次 13D 倒水训练的过程；
- 不是按目录罗列文件名；
- 不是逐行讲完全部源码；
- 当前不产出或冻结正式汇报稿。

## 2. 已有事实与证据状态

### 2.1 用户提供的模型基础信息（已确认，待补一手来源）

| 事实 | 当前来源状态 | 后续处理 |
|---|---|---|
| GR00T N1.7 模型总参数量约 2.2B | 用户陈述 | 在正式报告中补官方模型卡或配置证据 |
| 视觉/语言部分约 1.34B 参数 | 用户陈述 | 核对官方资料及可复现参数统计方法 |
| 动作头约 0.8B 参数 | 用户陈述 | 核对模块参数统计方法与包含范围 |
| NVIDIA L40、bf16 下生成一个 16-step action chunk 约 63.9 ms，约 15 Hz | 用户陈述 | 补官方 benchmark 条件、batch、输入分辨率和是否包含预后处理 |
| 预训练覆盖单臂、双臂、人形机器人，以及厨房等多类操作场景 | 用户陈述 | 补官方 README、paper 或模型卡证据 |

### 2.2 已由本地代码/项目证实的事实

| 主题 | 证据 |
|---|---|
| 主模型由 VLM backbone 与 DiT action head 组成 | `gr00t/model/gr00t_n1d7/gr00t_n1d7.py` |
| action head 包含 state encoder、action encoder、DiT、action decoder | 同上，`Gr00tN1d7ActionHead` |
| 训练目标为 flow matching velocity 的 masked MSE | 同上，`Gr00tN1d7ActionHead.forward()` |
| 推理从高斯噪声开始，按预测 velocity 做固定步数积分 | 同上，`get_action_with_features()` |
| data loader 以 step 样本为基本单位，支持 shard | `gr00t/data/dataset/sharded_single_step_dataset.py` |
| Processor 承担 state/action 归一化、模态配置、VLM 输入与反解码 | `gr00t/model/gr00t_n1d7/processing_gr00t_n1d7.py` |
| 模体以 tag 和 projector index 区分 | `processing_gr00t_n1d7.py`、`embodiment_conditioned_mlp.py` |

### 2.3 本次训练仅作为案例证据（已确认）

案例用于验证“工程链路已经被实际走通”，而非报告中心：

- 自定义 right arm 7D + O6 hand 6D 的数据契约；
- 自定义 modality config 与 `NEW_EMBODIMENT`；
- 30k step checkpoint-30000 的训练集 open-loop 结果；
- 从低 pass 失败到约 5.3 pass 有效学习，作为训练配置/数据采样理解的案例。

## 3. 研究主问题（报告应最终回答）

1. **工程分层是什么？** 每层负责什么，输入/输出/依赖是什么？
2. **训练路径如何贯通？** CLI 参数如何到 Config、Dataset、Processor、Model、Trainer、Checkpoint？
3. **推理路径如何贯通？** 观测如何进入 Policy，如何经过 Processor、Backbone、DiT，如何变为机器人动作？
4. **多模体如何实现？** Embodiment tag、modality config、projector index、mask、stats 分别解决什么问题？
5. **模型内部的最小必要解释是什么？** VLM、cross-attention、DiT、flow matching 的连接边界在哪里？
6. **扩展接口在哪里？** 新的数值触觉、触觉图像、新动作空间分别改变哪些模块？
7. **运行与验证边界是什么？** 训练 loss、open-loop、closed-loop、部署性能分别说明什么、不能说明什么？

## 4. 已确认的最终报告结构

> 结构采用深度研究报告风格：问题、证据、分析、结论、边界，而不是演示型口号或训练日记。
> 每一节必须结合本地源码。可以引用文件、类、函数、配置和必要的短代码片段；不得只写抽象概念说明。

1. 执行摘要：本次代码研究的范围、结论和未解决问题；
2. GR00T N1.7 定位与基础能力：模型构成、参数量、预训练覆盖、性能边界；
3. 代码仓与模块地图：包结构、关键入口、依赖方向；
4. 数据系统：LeRobot 契约、episode/step/shard、stats、Processor；
5. 模体适配系统：tag、modality config、projector、state/action mask；
6. 模型系统：Backbone、action head、DiT、flow matching、attention 信息流；
7. 训练系统：launch_finetune、Config 覆盖、model setup、Trainer、checkpoint；
8. 推理与评估系统：Policy、action chunk、RTC、open-loop/closed-loop；
9. 本项目案例：13D 数据如何穿过上述各层，只作为映射案例；
10. 可扩展性分析：数值触觉、触觉图像、独立新模体三种改动面；
11. 风险、未知与下一步代码研究计划；
12. 附录：关键文件、调用图、术语、参数/性能来源。

### 4.1 章节证据标准（已确认）

每个最终章节至少包含：

1. **本节要回答的问题**；
2. **代码证据**：至少一个具体文件和类/函数/配置字段，必要时附不超过理解所需长度的代码片段；
3. **代码行为解释**：输入、处理、输出、依赖方向；
4. **本项目映射**：说明右臂 O6 13D 例子经过此层时实际是什么；
5. **扩展影响**：新增模态/动作/机器人时此层是否要改、怎么验证；
6. **边界或未知**：代码尚未证明什么，或仍需官方资料/实验确认什么。

代码引用格式草案：

```text
证据：`gr00t/model/gr00t_n1d7/gr00t_n1d7.py`，
`Gr00tN1d7ActionHead.forward()`。
结论：该函数将真实 action 与高斯 noise 插值，并监督 `action - noise` 的 velocity。
边界：这证明训练目标；不单独证明真实机器人闭环成功率。
```

## 5. 研究记录规则

后续每条记录必须包含：

- 研究问题；
- 代码或官方资料证据（文件、类、函数、配置或链接）；
- 可验证结论；
- 不确定性、反例或未覆盖范围；
- 对最终报告哪一节有贡献；
- 对扩展操作的影响。

不把下列内容写成结论：未经验证的参数统计、README 营销语、单次训练经验、推断的 API 行为。

### README 审阅补充（2026-07-23）

根 README 是每个后续代码文档的必经证据源，但职责限定为“官方导航与发布/运行约束”，不能取代源码、配置、测试或本项目工件。已审阅 `gr00t_n1/README.md` 并同步至研究草稿与正式稿，提取的高价值信息包括：N1.7 的官方工作流和 checkpoint/tag 范围、relative EEF 的设计路线、LeRobot v2 + `meta/modality.json` 的数据声明、gated Cosmos backbone、torchcodec/FFmpeg 视频依赖、server-client 与 ReplayPolicy 的评估路径、state dropout/随机增强的训练提示、代码/权重的许可证区分及论文引用。

后续规则：每个新模块先读根 README 与对应子目录 README，记录其中的入口命令、依赖、支持边界和上游引用；再到 class/function、config、test、checkpoint 或运行工件中验证。README 的 GA、性能提升、稳定性等发布主张必须保留来源状态，不能自动升级为本项目实验结论。

## 6. 分阶段研究计划

| 阶段 | 对应最终章节 | 研究产物（仅记录，不写正式报告） | 主要证据 |
|---|---|---|---|
| R1 | 3 | 代码仓模块图、依赖方向、训练/推理双调用图 | package tree、import、入口函数 |
| R2 | 2 | 模型定位、参数量、预训练覆盖、性能来源表 | 官方资料 + 本地 config/参数统计 |
| R3 | 4 | 数据系统调用图与数据契约表 | converter、LeRobot loader、shard、stats、processor |
| R4 | 5 | 多模体适配机制与 projector/mask 边界 | tags、modality configs、processor、MLP |
| R5 | 6 | Backbone/DiT/attention/flow matching 的信息流 | model、DiT、backbone modules |
| R6 | 7 | 训练配置到 checkpoint 的调用路径 | shell、CLI、Config、setup、Trainer |
| R7 | 8 | 推理/评估/RTC 与 open-loop/closed-loop 边界 | Policy、eval、deployment |
| R8 | 9–11 | 13D 映射、扩展矩阵、风险和研究结论 | 前述记录 + 项目验证证据 |

### R1 / R2 阶段记录（2026-07-23）

**研究问题。** GR00T 的仓库模块、训练入口与推理入口如何连接；基础模型的定位、参数口径、预训练与性能数字哪些能够被当前代码或官方仓库材料支撑？

**产物。** 已生成研究草稿（不是正式老师汇报）：
`.project-log/research/gr00t-engineering-report-chapters-01-03.md`。草稿包含以下已写章节：

| 章节 | 已沉淀的证据 | 关键结论 |
|---|---|---|
| 1. 执行摘要与研究范围 | 项目目标、训练实例配置、源码阅读范围 | 报告主线固定为工程的责任边界与调用链，13D 训练仅作接口映射案例 |
| 2. 模型定位、参数、预训练覆盖、性能边界 | `README.md`、`policy.md`、硬件指南、checkpoint config/index、模型配置 | 当前证据支持发布口径约 3B；用户给出的 2.2B/63.9ms 不能在未核对条件下写成确定结论；重规划频率不能等同执行频率 |
| 3. 代码仓模块图和依赖方向 | `launch_finetune.py`、`experiment.py`、`setup.py`、`gr00t_n1d7.py`、`gr00t_policy.py`、`open_loop_eval.py` | 训练装配中心是 `Gr00tN1d7Pipeline`，部署边界是 `Gr00tPolicy`，二者经 processor/modality config/checkpoint 工件保持同一数据契约 |

**可复核结论。**

1. 训练链路为 `shell → launch_finetune → Config → experiment.run → MODEL_REGISTRY → Gr00tN1d7Pipeline → Trainer/checkpoint`；完整源码证据已列于草稿第 3.3 节。
2. 推理链路为 `Gr00tPolicy → Processor/collator → Gr00tN1d7.get_action → backbone → action_head → decode_action`；完整源码证据已列于草稿第 3.4 节。
3. checkpoint 保存 processor，故模型权重、modality config 与归一化/反解码不能在部署时任意混配（`experiment.py:254-256`，`gr00t_policy.py:114-166`）。

**不确定性与反例。**

- 本地基础 checkpoint 的 safetensors 索引为 3,144,016,000 parameters；仓库 notebook 曾输出 2,942,124,032，差异尚未复现和解释。用户给出的 2.2B 分解与此冲突，暂列待核对。
- 本地硬件指南列出 L40 在“1 camera、4 denoising steps”下的 7.8 Hz（PyTorch）与 26.0 Hz（TensorRT）；这不能证明也不能否定另一条件下的 63.9 ms / 15 Hz。
- 当前工作树含本地修改：`gr00t/configs/finetune_config.py`、`gr00t/experiment/launch_finetune.py`、`gr00t/model/gr00t_n1d7/gr00t_n1d7.py`。这些改动尚未完成与上游基线的语义审计。

**下一步：R3。** 进入第 4 章数据系统：从 LeRobot 元数据与 parquet/video 开始，追踪 `generate_stats`、`ShardedSingleStepDataset`、`extract_step_data`、Processor 的输入输出，明确 episode、step、action horizon、shard、stats 的关系与失败边界。

### R3 研究设计：第 4 章“数据系统”（待执行）

本章采用“磁盘契约 → 采样单位 → 统计/表示变换 → 模型 batch”的顺序，而不是按文件名罗列。草稿允许保留字段级和函数级细节；正式汇报时再压缩为一张主数据流图、两到三张关键表和必要的代码摘录。

| 子节 | 要回答的问题 | 优先源码/工件 | 预期产出 |
|---|---|---|---|
| 4.1 数据边界与对象层级 | episode、frame、step sample、action chunk、shard、batch 分别是什么，不能互相混称什么？ | `lerobot_episode_loader.py`、`sharded_single_step_dataset.py`、13D `meta/*.json*` | 术语与形状表 |
| 4.2 LeRobot 物理存储契约 | parquet、MP4、`info.json`、`modality.json`、`episodes.jsonl`、`stats.json` 分别保存什么，读取方如何依赖它们？ | `convert_to_lerobot_right_o6.py`、`LeRobotEpisodeLoader`、当前数据集元数据 | 文件—字段—消费者矩阵 |
| 4.3 从 episode 到 step | 某时刻 t 如何根据 `delta_indices` 取历史图像/state、未来 action；边界不足时如何 padding 或剔除？ | `extract_step_data()`、`ShardedSingleStepDataset`、modality config | 带具体 13D/16-step 示例的时间轴图 |
| 4.4 shard 与采样 | shard 是 RAM/IO 与随机采样机制中的什么对象；为什么不是一个训练样本也不是原始文件分块？ | `ShardedSingleStepDataset`、`ShardedMixtureDataset`、`DatasetFactory` | shard 生命周期和 epoch 采样图 |
| 4.5 统计量与归一化 | `generate_stats`、relative stats、processor statistics 各自生成/消费什么；absolute 与 relative action 何时分叉？ | `stats.py`、`processing_gr00t_n1d7.py`、`state_action/**` | stats 来源—用途—风险表 |
| 4.6 Processor 与 collator | 样本如何从 `VLAStepData` 变为带 VLM 内容、mask、张量的 batch；训练与推理哪些步骤相同？ | `processing_gr00t_n1d7.py:159-...`、`data/types.py`、`interfaces.py` | 输入/输出键和张量形状追踪表 |
| 4.7 13D 映射与失效边界 | 当前 3 相机、13D、16-step、task 如何穿过前述每层；哪些错误会被及早发现，哪些会静默污染训练？ | converter、`linkerhand_right_o6_config.py`、本地数据集、已有验证记录 | 案例映射及风险清单 |

首轮只做只读源码与数据元数据检查；不重新训练、不改转换脚本、不改模型代码。对于 stats 的真实数值和一次 batch 的实际 shape，将在完成静态调用图后使用最小只读加载验证，记录运行环境和结果。

### R3 阶段记录：数据系统（2026-07-23）

**研究问题。** 当前训练如何把 LeRobot 数据集中的 episode、parquet、MP4 和 metadata 转为具有固定时间窗口、归一化语义和 mask 的模型 batch？shard 的实际含义及 `episode_sampling_rate=0.1` 的实际行为是什么？

**产物。** 第 4 章的七个小节已追加到研究草稿：
`.project-log/research/gr00t-engineering-report-chapters-01-03.md`。文件名保留为历史名称，但内容已更新为第 1—4 章；仍不是正式老师汇报稿。

**确认事实与证据。**

| 主题 | 证据 | 可复核结论 |
|---|---|---|
| 数据对象 | `sharded_single_step_dataset.py:27-303`；真实 metadata | episode、frame、VLAStepData、action chunk、shard、batch 是不同层次；训练样本是单个决策时刻而非整条 episode |
| 真实数据规模 | 当前 dataset `meta/*`、parquet，shard 实测 | 148 episode、47,250 原始帧、3 路视频共 444 个 MP4、13D state/action、45,030 有效 16-step 起点、44 shard |
| 时间窗口 | `linkerhand_right_o6_config.py`；`extract_step_data()` | observation 使用 `delta=[0]`，action 使用 `0..15`；episode 0 中 t=461 最后有效，t=462 越界；当前 `allow_padding=false` |
| shard | `ShardedSingleStepDataset.shard_dataset()`；实测 shard 总和 | `shard_size=1024` 得到均衡的约 1024-step 逻辑加载组；shard 不是 parquet 物理分块或 batch |
| 0.1 参数语义 | `step_indices[i::num_splits]` 的全部 split 均加入；45,030 总和 | 当前实现没有直接丢弃 90% step；`episode_sampling_rate=0.1` 实际改变子序列/shard 混合粒度，参数名和 docstring 有误导风险 |
| stats / 表示 | `stats.py`、`state_action_processor.py`、最终 `processor_config.json` | 当前 q01/q99 归一化并裁剪；`use_relative_action=true` 但两个 ActionConfig 均为 ABSOLUTE，故无 absolute→relative 转换；sin/cos state encoding 也未启用 |
| 真实 Processor batch | 2026-07-23 最小只读加载，保存的 `processor/` | t=0 输出 state `(1,1,132)`、action `(1,40,132)`、mask 有效元素 `16×13=208`、`input_ids=(1,277)`、`pixel_values=(1056,1536)`、`image_grid_thw=(3,3)`、embodiment id 10 |

**边界与风险。** 代码验证了文件、shape、窗口与归一化契约；尚未证明 action 行与 observation 行在真实控制器中的物理时序严格对齐，也未证明相机标定、遮挡质量、demonstration 覆盖度或触觉同步质量。state/action 内部维度顺序和单位若错误但总 shape 仍为 13，可能静默污染训练；权重与另一个 checkpoint 的 processor/stats 混用也可能在 tensor 形状合法时产生错误控制语义。

**下一步：R4。** 研究第 5 章多模体适配系统：从 `EmbodimentTag.NEW_EMBODIMENT`、动态 modality config 注册和 checkpoint `embodiment_id.json` 出发，追踪 projector index、state/action mask、pretrain/posttrain tag 以及新增触觉应落在数据、Processor 和模型条件通路的哪一层。

### R4—R8 阶段记录：第 5—11 章（2026-07-23）

**产物。** 已将第 5—11 章追加至
`.project-log/research/gr00t-engineering-report-chapters-01-03.md`。该文件现为完整的 11 章研究草稿（约 894 行），仍是供后续压缩的证据素材，尚非正式老师汇报稿。

| 章节 | 已确认结论 | 关键证据与边界 |
|---|---|---|
| 5 多模体 | tag、modality config、Processor、embodiment id/projector 是四层共同契约；当前 `new_embodiment→10` | category-specific state/action encoder/decoder 按 id 取不同参数；新机器人不应仅复用 tag/index |
| 6 模型 | Qwen3-VL 给出 VLM condition；state/action token 作为 DiT query；训练是 masked flow-matching velocity MSE，推理是 4 步 Euler 积分 | 当前 final config：冻结 LLM/visual，训练 projector/DiT/VLLN；32 层 AlternateVLDiT；内部上限 132D/40-step |
| 7 训练 | `experiment.run()` 保存 config、Processor 和 checkpoint；本次达到 30,000 step | batch 1、accumulation 8、bf16、paged AdamW 8-bit；末尾训练 loss 不是成功率；eval strategy=no |
| 8 推理评估 | Policy 负责 validation→Processor→model→decode，不负责真机安全；open-loop 比较离线专家观测下的未归一化 action | 当前未实际运行 open-loop 或闭环；execution horizon 与模型/action horizon 必须分开 |
| 9 13D 映射 | 当前训练已可从 telemetry/MP4 追至 model/Processor/checkpoint | 本地源码有未审计 patch；真机 adapter 和评估仍待实现/验证 |
| 10 扩展 | 触觉应先按低维 state、触觉图、专用时序 encoder 三路线做架构选择 | 推荐先以同步低维触觉建立基线，再决定更复杂融合；这只是工程建议，非已有性能结论 |
| 11 风险结论 | 已将黑盒拆为可操作边界，但系统效果尚未被证明 | P0 是物理时序/单位审计与真机安全 adapter；P1 是评估、config 口径、local patch 审计 |

**文档校验。** 第 1—11 章标题完整；Markdown code fence 为偶数且闭合；无 TODO/TBD/XXX 标记。未修改模型、训练、converter 或数据文件。全部新增内容为研究草稿与项目记录。

**精确下一步。** 在生成正式汇报稿前，优先补齐两项可演示证据：其一，针对固定 episode split 运行/记录 open-loop MSE、MAE 与轨迹图；其二，逐 diff 审计本地修改的 `launch_finetune.py`、`finetune_config.py`、`gr00t_n1d7.py`。若老师汇报时间优先于实验，则将这些作为明确“尚未验证”的下一步，而不是用训练 loss 替代。

### 配置审计补充：`Gr00tN1d7Config`（2026-07-23）

用户要求以 `gr00t/configs/model/gr00t_n1d7.py` 复核草稿模型信息。已逐项比较三份配置：源码 `Gr00tN1d7Config` 默认值、本地基础 checkpoint `checkpoints/gr00t_n1_base/config.json`、本次输出 `experiment_cfg/final_model_config.json`。

**结论。** 草稿原有核心结论（132D state/action 上限、40-step 模型 action horizon、4 个 flow-matching 推理步、32 层最终 DiT、当前冻结 Qwen LLM/visual 且训练 projector/DiT/VLLN）与最终训练/基础 checkpoint 工件一致。发现并已修正一处表述：`select_layer=16` 在 `Qwen3Backbone.__init__()` 中通过循环删除尾部语言层实现，语义是“保留前 16 个 language-model layer 后取最终 hidden state”，不是简单的“取第 16 层”。

**新增边界。** 源码默认与实际 config 不应混称：源码默认 `select_layer=12`、DiT=16 层、state dropout=0.8；基础 checkpoint 为 `select_layer=16`、DiT=32 层、state dropout=0.2；本次 13D final config 为 16、32、0.0。草稿第 2.2 节已加入三份配置对照表，并明确 base checkpoint 中未显式序列化的字段由 config dataclass 默认回填，不能把 JSON 缺键解释为零值。

### 汇报目标重定向：从技术研究报告到代码工程地图（2026-07-23）

**触发。** 用户在完整审阅工程入口材料后重新判断：此前的研究草稿和正式汇报稿过度下沉到数据、参数、训练案例和模型细节，呈现为散点式技术研究；即使各点正确，也不足以证明已掌握整个代码工程的结构。

**确认的业务目标。** 晚间汇报的主产物应是一份面向工程使用者的代码说明书：读者先获得仓库的全局网络/地图，再根据目标任务定位应阅读和修改的目录、文件与调用路径。它不要求逐点解释每个地点的历史或算法细节，而要求明确“这个工程是什么、提供什么功能、每部分负责什么、我要完成某项工作应从哪里进入”。

| 维度 | 不再作为主稿主线 | 新主稿必须回答 |
|---|---|---|
| 叙事视角 | 一次 13D 微调经历、训练结果、模型参数、数据字段 | 从仓库外部描述整体结构、功能和入口 |
| 内容组织 | 按数据/模型/训练细节逐层深挖 | 按目录职责、功能地图和任务路径组织 |
| 读者行为 | 阅读后了解若干技术点 | 阅读后能定位“要做 X 应看哪些目录和文件” |
| 13D 案例 | 作为报告主线 | 仅作为“自定义 embodiment 微调”路径的一个简短实例 |
| 既有文档 | `docs/gr00t-engineering-report.md` 作为正式主稿 | 降为技术附录；研究草稿继续作为证据库 |

**新主产物。** 建议创建 `docs/gr00t-codebase-map.md`，章节为：

```text
工程定位
→ 仓库全景图（目录树、职责、依赖方向）
→ 功能地图（训练、推理、评估、部署、示例）
→ 核心运行链路
→ 微调新机器人路径
→ 推理与真机接入路径
→ 评估路径
→ 部署与性能优化路径
→ 新 embodiment / 新模态扩展地图
→ 推荐代码阅读路线与关键词索引
```

**约束。** 新文档可吸收和补充上游发布/使用材料，但不出现“某说明文件说了什么”的资料摘抄语气。正文以工程事实陈述；每个功能路线必须落到实际目录、入口脚本、核心类/函数和产物；只保留导航必需的代码细节。模型参数、flow matching、13D 数据统计、open-loop 数值等保留在技术附录，除非它们直接决定某条工程路径的使用边界。

**精确下一步。** 先列出顶层目录、各目录职责、依赖方向和六条任务路径的文件锚点，再开始生成主文档；不从已有 11 章研究报告中压缩拼凑，以免重新落入散点式叙事。

### 代码工程地图规划基线（2026-07-23）

**受众与验收。** 文档面向“已经能运行仓库命令、但尚未建立代码结构认知”的接手者。读者完成阅读后，必须能回答：这个工程提供哪些能力；某个目录负责什么；我要完成一个任务应从哪个入口进入、沿哪条路径阅读、会产生什么工件；哪些部分仍由外部机器人系统负责。

**正文组织。** 主文档采用“全景 → 功能 → 路径 → 扩展 → 阅读顺序”的漏斗，而非“数据 → 模型 → 训练”的技术下钻。建议章节如下：

| 章节 | 要解决的问题 | 主要展示形式 | 深度边界 |
|---|---|---|---|
| 1. 使用说明与工程定位 | GR00T 是什么、不是什么；本地图如何使用 | 一张输入—策略—输出边界图 | 不讲模型参数与训练成绩 |
| 2. 仓库全景图 | 顶层目录和关键根文件分别负责什么 | 精简目录树 + 目录职责表 | 只列进入任务路径所需文件 |
| 3. 功能地图与依赖方向 | 工程提供训练、推理、评估、部署等哪些能力，模块如何协作 | 功能矩阵 + 依赖图 | 不展开函数级实现 |
| 4. 统一核心链路 | config、data、model、processor、policy、checkpoint 的关系 | 一张训练/推理共用链路图 | 解释责任，不推导算法 |
| 5. 自定义机器人微调路径 | 数据与配置准备后如何进入训练、保存什么 | 路径卡片 | 13D 只作一行实例 |
| 6. 策略推理与真机接入路径 | 本地 Policy、server/client 与外部控制 adapter 如何分界 | 路径卡片 + 边界表 | 不虚构真机安全实现 |
| 7. 评估路径 | open-loop、replay、仿真 rollout、真机闭环各看哪里 | 分层评估表 + 路径卡片 | 不报告当前实验数值 |
| 8. 部署与性能优化路径 | ONNX/TensorRT、平台脚本与 benchmark 在哪里 | 部署矩阵 + 路径卡片 | 不做性能横向结论 |
| 9. 扩展地图 | 新 embodiment、新 action/state、新触觉各应改哪里 | 需求—影响目录矩阵 | 不预设触觉融合方案 |
| 10. 推荐阅读路线与索引 | 初学者如何从入口走到核心；关键类在哪里 | 分阶段阅读表 + 关键词索引 | 技术细节跳转至附录 |

**路径卡片统一模板。** 第 5—8 章每条任务路线统一写成：`要完成什么 → 从哪里开始 → 主调用/阅读路径 → 关键配置或输入 → 产物/验证入口 → 不由该路径负责什么`。这样读者看到的不是散点文件清单，而是一张可执行的导航路线。

**信息层级。** 每个目录只写三件事：责任、最常进入的文件、依赖/被谁调用；每个文件只在它是任务入口、稳定接口或关键装配点时出现。模型数学、数据字段、参数量、评估数字等内容只在确实界定某条路径的输入输出或边界时提及，并链接至既有技术附录。

**待核对后才能写正文的事实。** 顶层目录的最终职责表；`examples/` 各类案例与核心模块的关系；训练、Policy、open-loop、仿真、server-client、ONNX/TensorRT 的实际入口文件、调用链和输出工件。该核对属于 `task-011`，不需重新训练或修改代码。

### 代码地图可读性诊断：缺少首次接触的叙事入口（2026-07-23）

**用户反馈。** 当前 `docs/gr00t-codebase-map.md` 的地图方向正确，但阅读不顺：文档经常先抛出一个工程问题或术语，再解释答案；首次接触者尚未理解该问题为什么存在、它与整个工程的什么环节有关，因此难以吸收后续内容。

**诊断。** 当前文档更接近“工程师检索手册”，隐含要求读者已知道 `embodiment`、`modality config`、Processor、checkpoint/Policy、open-loop 等概念和它们出现的时机。其章节虽然有“项目名片 → 仓库全景 → 功能 → 核心链路 → 任务路径”的宏观顺序，但中间存在三类认知断裂：

| 断裂 | 当前表现 | 为什么造成阅读困难 |
|---|---|---|
| 问题先于场景 | “两类配置不要混淆”“任务路径卡片”“四层评估”在读者尚未看到一次完整运行故事前出现 | 读者不知道这些概念在什么时候出现，无法判断其重要性 |
| 地图先于主干路线 | 目录职责、功能矩阵一次给出大量平行模块 | 初学者没有中心锚点，只能记文件夹名，无法把模块挂在同一因果链上 |
| 视角频繁切换 | 模型简介 → 目录树 → 功能表 → 技术契约 → 多条任务路线 | 每次切换都要求重建“当前是在解释系统流程、目录结构还是操作步骤”的上下文 |

**关键结论。** 代码地图前半部分需要先讲一个所有人都能跟随的“最小完整旅程”：用户有一批演示数据和一个机器人 → 将其变为数据集与具身定义 → 运行训练 → 生成 checkpoint（含 processor）→ 用 Policy 读取新观测并预测动作 → 用开环、仿真或真机检查结果。只有主线跑完后，再解释每一站对应哪个目录、每个目录还有哪些附属功能。这样问题由旅程自然引出，而不是由作者提前抛给读者。

**后续重构原则（尚未执行）。** 文档应改为“故事主线 → 站点地图 → 分支路线 → 深入索引”：先用一条端到端流程建立 `data / config / train / checkpoint / policy / evaluation` 的必要性；随后在流程图旁标出目录；再将目录职责和微调/推理/评估/部署解释为该主线的分支；术语第一次出现时用一句 plain-language 定义，而不是先给定义表或例外表。

### 代码地图可读性诊断（二）：现有信息架构为何“不好入口”（2026-07-23）

**用户问题。** 地图的方向已经正确，但文档经常先提出一个工程问题并立即解释；如果读者尚未知道该问题在系统流程的哪个时刻出现、为何必须处理，就无法自然理解或记住后面的解释。用户要求识别具体问题，而不是简单增加定义、示例或篇幅。

**结论。** 问题不在信息深度不足，而在于文档采用了“作者已掌握全局后的分类顺序”，没有采用“首次读者逐步建立全局模型的顺序”。当前文档属于可检索的工程手册；老师首次阅读时需要的是先建立一条因果主干、再展开地图的说明书。

| 信息层 | 首次读者在这一层必须先获得的东西 | 当前文档的实际开始方式 | 造成的断裂 |
|---|---|---|---|
| 任务情境 | 谁带着什么输入来使用工程，最终想得到什么结果 | 模型名片后直接给顶层目录树 | 不知道目录中的组件服务于哪一次完整工作 |
| 端到端因果链 | 数据为何需要整理、配置为何需要存在、训练后为何要保存 checkpoint、推理为何还要 Processor | 目录职责、功能矩阵和“配置不要混淆”先行 | 术语先出现，必要性后出现；读者只能被动记名词 |
| 模块定位 | 每个模块在完整链路中处于哪个站点、接收什么、交出什么 | `configs/data/model/experiment/policy/eval` 并列列举 | 目录名称是平行的，读者脑中没有主干来挂接它们 |
| 分支选择 | 在哪一个主干站点后会分出训练、推理、回放、开环、仿真、部署等路线 | 功能表一次性列出八类能力 | 读者尚未掌握主干，就需要理解分支的选择条件与边界 |
| 下钻检索 | 需要改某处时应打开哪些文件和读到什么程度 | 任务卡片、关键词索引和稳定接口 | 这些是有效索引，但应在读者拥有全局参照后再使用 |

**现有正文中的具体症状。**

| 当前位置 | 现在向读者提出的内容 | 隐含前提 | 为什么会读不顺 | 应移动或改写为 |
|---|---|---|---|---|
| 第 2.1—2.2 节 | 目录树与十余个目录的职责表 | 已知一次训练和一次推理分别经过哪些组件 | 读者会把它读成需要背诵的文件夹清单 | 放在完整旅程之后，改成“旅程站点对应的仓库位置” |
| 第 2.3 节 | 三层配置不要混淆 | 已知数据进入训练前至少要回答数据布局、机器人语义、训练方式三类问题 | 读者尚未遇到配置，自然不会知道为什么要区分 | 在旅程到达“告诉系统这台机器人是什么”时引出，再补充为配置分层表 |
| 第 3 节 | 微调、回放、开环、仿真、服务端、部署等八类功能并列 | 已知它们是同一 Policy 主干在不同阶段的分支 | 八个陌生目标同时竞争注意力，无法判断先后和主次 | 先完成一条“数据到动作”的主干；随后按主干末端的验证/部署需求展开分支 |
| 第 4 节 | checkpoint、Processor、modality contract 的共享机制 | 已见过训练产物如何被下一次推理加载 | 解释本身正确，但结论先于生活化的运行过程 | 在旅程中先展示“训练留下一个可部署包”，再解释该包为何不能只复制权重 |
| 第 5—8 节 | 四条任务卡片彼此平行 | 已知道“我现在处于数据准备、训练、推理还是验证/部署” | 每张卡片都从新问题重新起步，造成反复切换上下文 | 作为主干各站点的“岔路详情”，而不是主目录式连续章节 |
| 第 9—10 节 | 扩展矩阵、阅读路线、关键词索引 | 已建立 data/config/processor/model/policy 的边界 | 对初学者是抽象决策表，缺少由一个实际变更请求引出的判断过程 | 在结尾用“若要加入触觉，该沿哪几个站点回查”的回顾式案例承接 |

**更深一层的写作问题。**

1. **名词密度过高，动词链不足。** 当前多为“`data/` 负责什么、`policy/` 负责什么”，但首次读者需要先看到“数据被谁读取、处理成什么、由谁训练、训练产物被谁加载、输出交给谁”。动词链能建立因果，名词表只能用于回查。
2. **缺少“站点到站点”的交接物。** `LeRobot dataset`、`modality config`、`checkpoint + processor`、`observation`、`action chunk` 是读者真正可追踪的对象。当前已有这些信息，但分散在目录表、功能表和核心链路中，未形成一条连续的交接链。
3. **缺少术语的首次、最低成本定义。** 例如 `embodiment`、Processor、Policy、open-loop 都在表格中以专业词出现。首次出现时应以一句与任务有关的自然语言说明其作用；严格的类名和实现文件紧随其后，而不是反过来。
4. **阅读视角跳转太快。** 同一页先从产品/模型视角转到文件系统，再转到能力清单，再转到接口契约。每次转场没有回答“为什么现在要看这一层”，读者必须自行补上转场逻辑。
5. **边界与例外出现得早。** “不要混用”“不等于什么”“不负责什么”对于风险控制很重要，但它们在主干尚未建立时会打断理解。应先讲清正常路径，再在该站点结尾提示最关键的一条边界。

**重构后的阅读机制。** 新版前半部分应只让读者回答一个问题：

```text
如果我有一台新机器人和一批演示数据，GR00T 工程怎样把它们变成可调用的动作策略？
```

该问题依次自然产生六个站点：`数据集` → `机器人说明书（config）` → `训练入口` → `可部署 checkpoint` → `Policy 动作预测` → `验证或接入控制器`。每个站点仅说明四件事：它解决什么上一步遗留的问题、输入是什么、交出什么、代码在哪里。待六站走完后，目录树、功能分支、评估层级、部署和扩展索引才有可依附的共同参照。

**验收标准（待文档重构时验证）。** 一名不理解 `Processor`、`embodiment` 或 open-loop 的读者，在看完整旅程前不需要理解这些术语；完成旅程后，应能不看目录表复述“数据、配置、训练、checkpoint、Policy、评估/控制”的先后关系，并据此说明为什么要进一步阅读某个目录。目录表与关键词索引的作用应从“建立理解”降为“定位实现”。
