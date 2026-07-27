# GR00T N1.7 工程理解研究草稿：第 1—4 章

> **文档状态**：研究草稿，2026-07-23。本文是后续正式汇报文档的可追溯素材，不替代最终汇报稿。  
> **研究对象**：本地源码副本 `gr00t_n1`，提交 `9c7e746b2cd37a810070a98ef41d290a07e806c2`（2026-07-08）；上游为 NVIDIA Isaac-GR00T。  
> **证据标记**：**代码已证实**表示可由当前本地源码或权重元数据直接复现；**发布资料已证实**表示由上游发布与使用材料明确陈述；**用户提供，待核对**表示暂不作为确定结论；**待研究**表示需要在后续章节或实验中验证。

---

## 1. 执行摘要与研究范围

### 1.1 研究问题与结论摘要

本研究的目标不是复述一次微调命令如何运行，而是回答一个工程问题：**GR00T N1.7 如何把“带有机器人状态、相机图像和语言指令的时刻”转换成“可执行的连续动作块”，以及新机器人或新模态应当在哪些代码边界上接入。** 因此，研究对象同时包含模型权重、数据契约、配置注册、训练编排、推理 API、评估与部署路径。

截至本草稿，黑盒已经可以被分解为一条具有明确所有权的链路：数据系统负责把演示变成具有时间语义的样本；Processor 负责依据 embodiment（具身形态）契约把样本归一化并构造成 VLM 与动作头的输入；模型系统以 Cosmos-Reason2/Qwen3-VL backbone 提取视觉—语言条件，再以 flow-matching DiT 生成动作块；训练系统仅负责将配置、数据、模型和 Hugging Face Trainer 连接起来；Policy 则在推理端执行相同的预处理和反归一化，并把预测结果交回机器人控制层。该结论由训练入口、模型 pipeline、`Gr00tN1d7.forward()` 与 `Gr00tPolicy._get_action()` 的直接调用关系支持。

本项目的“右臂 7D + O6 手 6D”训练已用于验证这条链路的一个实例：项目配置将三个 RGB 相机、13 维 state、13 维 action、16 步动作窗口注册为 `NEW_EMBODIMENT`。但它并不证明模型已具备可靠的闭环机器人能力；它只证明该实例能通过工程接口进入训练和推理路径。模型质量、真机控制稳定性和触觉扩展的有效性仍需要独立证据。

### 1.2 研究范围、非范围与证据方法

| 维度 | 本研究纳入的内容 | 本阶段不作结论的内容 |
|---|---|---|
| 源码范围 | `gr00t/configs`、`data`、`model`、`experiment`、`policy`、`eval`、`deployment` 及其入口脚本 | 外部仿真依赖的完整内部实现，例如 RoboCasa、LIBERO、SimplerEnv 的所有源码 |
| 模型范围 | N1.7 的 VLM backbone、动作头、DiT、flow matching、动作块接口 | 对每一层网络权重的逐层解释或模型可解释性结论 |
| 数据范围 | LeRobot 读取、step/shard、统计量、processor、modality config | 原始采集系统的传感器驱动、时钟同步和遥操作软件内部实现 |
| 训练与推理 | CLI 到 checkpoint、Policy 到 action chunk、open-loop 的职责边界 | 将 loss 或 open-loop MSE 直接解释成真机成功率 |
| 扩展问题 | 新机器人、新动作维度、新数值触觉或触觉图像的预期接入层 | 未经实现和实验验证的“触觉一定提升性能”结论 |

研究采用“主张—证据—边界”的方式组织。主张优先由函数调用、配置字段、权重索引和可执行路径支撑；上游发布与使用材料用于界定发布版本、预训练覆盖、支持路径、部署入口和运行前提；用户给出的数字保留其来源状态。发布方关于版本成熟度、性能提升或稳定性的声明不替代本项目实测或逐文件代码审计。这样可以避免将一次训练现象、发布描述或代码注释错误地提升为工程事实。

### 1.3 当前白盒化程度

表 1 将当前理解按可追踪程度划分。这里的“已定位”不等于“已完全掌握”，而是指已经能从输入沿源码找到该层的责任边界和输出。

| 工程层 | 当前可回答的问题 | 主要源码证据 | 研究状态 |
|---|---|---|---|
| 运行入口 | 微调参数如何进入统一配置和训练循环？ | `gr00t/experiment/launch_finetune.py:31-145`；`gr00t/experiment/experiment.py:192-371` | 代码已证实 |
| 组件装配 | 谁创建模型、Processor、Dataset、collator？ | `gr00t/model/gr00t_n1d7/setup.py:47-242` | 代码已证实 |
| 模型主干 | 条件特征和动作生成器由谁拥有，训练与推理入口分别是什么？ | `gr00t/model/gr00t_n1d7/gr00t_n1d7.py:518-645` | 代码已证实 |
| 推理 API | 外部观测如何检查、编码、预测和反归一化？ | `gr00t/policy/gr00t_policy.py:70-176, 380-432` | 代码已证实 |
| 数据与模体 | episode、shard、stats、mask、tag 如何协同？ | `gr00t/data/**` 与 `processing_gr00t_n1d7.py` | 后续第 4、5 章 |
| 模型细节 | DiT 条件注入、cross-attention、flow matching 的精确张量流 | `gr00t/model/gr00t_n1d7/**`、`gr00t/model/modules/**` | 后续第 6 章 |
| 训练行为 | 梯度冻结、优化、保存格式、恢复与分布式边界 | `experiment/**`、`trainer.py`、callbacks | 后续第 7 章 |
| 工程效果 | 开环误差、闭环成功率、时延、控制安全 | `eval/**`、部署代码及实测 | 后续第 8、11 章 |

### 1.4 本项目案例在研究中的位置

项目案例不是本报告主线，而是接口是否被实际走通的锚点。当前实例的契约如下：`cam_top`、`cam_left_wrist`、`cam_right_wrist` 三路图像；`right_arm` 七维关节状态/动作；`right_o6_hand` 六维手部状态/动作；`task` 语言；动作预测窗口为 16 步。该契约直接写在 `examples/linkerhand_right_o6_config.py:19-57`，训练封装脚本将其传给 `launch_finetune.py`（`finetune_right_o6_13d.sh:48-72`）。

它在后续各章中只承担两种作用：其一，说明抽象模块在当前系统里对应何种具体输入输出；其二，暴露扩展时需要遵守的实际契约。它不能用来替代对基础模型、预训练覆盖或通用推理性能的论证。

---

## 2. 模型定位、参数、预训练覆盖与性能边界

### 2.1 模型定位：VLA 不是端到端机器人系统的全部

GR00T N1.7 是开放的 vision-language-action（VLA）模型：输入包括语言和图像等多模态观测，输出用于操作任务的连续动作。其发布定位是面向通用人形技能与跨 embodiment 适配，并支持通过后训练适配具体机器人、任务和环境。代码上，这一定位并非停留在概念层：`Gr00tN1d7` 同时持有 `backbone` 与 `action_head`，前者构造条件特征，后者生成动作（`gr00t/model/gr00t_n1d7/gr00t_n1d7.py:547-568`）。

但 VLA 不是完整的真机系统。它没有取代相机采集、状态估计、动作限位、低层控制器、碰撞处理、网络通信和安全状态机。`Gr00tPolicy` 的职责止于验证输入、调用模型并解码 action；它不直接下发关节命令（`gr00t/policy/gr00t_policy.py:70-81, 380-432`）。因此，对老师汇报时应将 GR00T 描述为“上层动作策略模型与参考工程”，而不是“已经包含全栈机器人控制安全系统”。

表 2 给出模型所处系统边界。

| 层级 | GR00T N1.7 已提供的责任 | 机器人集成方仍需负责的责任 |
|---|---|---|
| 语义与感知条件 | 将语言、RGB 图像、状态编码为动作生成条件 | 任务指令来源、相机驱动、相机标定、时间同步 |
| 动作策略 | 预测归一化的连续 action chunk，并根据 stats 解码 | 动作单位/坐标系最终确认、限幅、滤波、控制频率 |
| 数据与适配 | LeRobot 数据读取、stats、modality config、embodiment tag | 采集数据质量、标注语义、遥操作动作含义、数据治理 |
| 评估与部署 | open-loop、仿真接口、Policy API、ONNX/TensorRT 路径 | 真机闭环协议、失效保护、风险验收、现场故障恢复 |

### 2.2 可由代码确认的结构与配置

当前 N1.7 主模型类是 `Gr00tN1d7`，其配置类型为 `Gr00tN1d7Config`。默认 backbone 名称为 `nvidia/Cosmos-Reason2-2B`，对应 Qwen3-VL 架构；代码通过 `get_backbone_cls()` 在本地目录或模型名满足条件时选择 `Qwen3Backbone`（`gr00t/model/gr00t_n1d7/gr00t_n1d7.py:491-515`）。`Gr00tN1d7Config` 的源码默认定义了最大 state/action 宽度 132、动作预测 horizon 40、4 个 flow-matching 推理步、16 层 DiT，以及 0.8 的 state dropout（`gr00t/configs/model/gr00t_n1d7.py:39-123`）。

必须区分三份不同层次的配置：Python dataclass 提供“未传入任何覆盖时”的默认值；基础 checkpoint `config.json` 描述预训练权重应配套的结构/行为；本次训练的 `final_model_config.json` 是 action head 实际构造时保存的模型配置。表 3a 是对这三份工件的逐项核对结果。它说明当前核心尺寸与 flow schedule 基本一致，但基础 checkpoint 和本次训练确实覆盖了源码默认中的若干重要值；解释模型时不能将源码默认直接称为当前权重的结构。

| 字段 | Python 源码默认 | 本地基础 checkpoint | 本次 13D 最终模型配置 | 正确解释 |
|---|---:|---:|---:|---|
| backbone 名称 | `nvidia/Cosmos-Reason2-2B` | 同左 | 本地等价目录 `cosmos_reason2_2b` | 13D 训练以本地路径提供同一类 Qwen3-VL backbone |
| `select_layer` | 12 | 16 | 16 | 当前保留 Qwen language model 的前 16 个 layer 后，取其最后 hidden state；不是“读取第 16 个 token” |
| `backbone_embedding_dim` | 2048 | 2048 | 2048 | VLM condition token 宽度 |
| `max_state_dim` / `max_action_dim` | 132 / 132 | 132 / 132 | 132 / 132 | 统一具身数值宽度上限 |
| `action_horizon` | 40 | 40 | 40 | 模型内部动作轨迹长度上限 |
| `hidden_size` / `input_embedding_dim` | 1024 / 1536 | 1024 / checkpoint 未显式列出 | 1024 / 1536 | action decoder hidden 与 DiT token 宽度；后者也等于 `32×48` |
| DiT `num_layers` | 16 | 32 | 32 | 当前基础与 13D 模型均为 32 层，不能用源码默认 16 层描述它们 |
| DiT heads × head dim | 32 × 48 | 32 × 48 | 32 × 48 | DiT 内宽度为 1536 |
| `use_alternate_vl_dit` | true | true | true | cross-attention 按 image/text token 集合交替的实现被启用 |
| inference steps | 4 | 4 | 4 | 每次 action 采样的 Euler 更新次数 |
| backbone tuning | LLM/visual 均 false | LLM/visual 均 true | LLM/visual 均 false | 基础 checkpoint 配置与 13D 微调的 trainable policy 不同；不能由 base config 推断本次训练冻结状态 |
| `state_dropout_prob` | 0.8 | 0.2 | 0.0 | 当前 13D 不施加随机 state dropout；不能将源码 0.8 当成本次增强 |
| projector / DiT / VLLN tuning | true / true / true | true / true / true | true / true / true | 本次动作侧三个模块均设为可训练 |

因此，解释当前基础模型与本次训练时应以 checkpoint/final config 为准，而不能仅引用 `Gr00tN1d7Config` 的 16 层 DiT、12 layer selection 或 0.8 state dropout 默认值。另一方面，base checkpoint JSON 未显式序列化的字段不能简单按“缺失即为零”解释；`Gr00tN1d7Config.__init__()` 会为未提供的 dataclass 字段填入默认值，最终行为仍需结合加载后的 config 或本次保存的 `final_model_config.json` 判定（`configs/model/gr00t_n1d7.py:125-138`）。

```python
# gr00t/model/gr00t_n1d7/gr00t_n1d7.py:547-568（节选）
self.backbone = backbone_cls(model_name=config.model_name, ...)
self.action_head = Gr00tN1d7ActionHead(config)
self.collator = Gr00tN1d7DataCollator(...)
```

这段装配代码说明了最关键的结构边界：VLM backbone 不是动作头的一部分；collator 虽由模型对象持有，却是将 VLM 内容转换为张量 batch 的数据边界组件。后续要加入触觉时，是否修改 backbone、processor 或 action head，取决于触觉是被视为一个新条件模态、视觉式 token，还是需要改变动作生成目标；不能只在模型 `forward()` 中随意拼接数组。

### 2.3 参数量：当前证据与待核对数字

参数量是本次汇报中最容易出现口径混淆的部分。发布 checkpoint 的名称为 `nvidia/GR00T-N1.7-3B`；本地 checkpoint 的 safetensors 索引元数据记录 `total_parameters: 3,144,016,000`。这两条证据相互一致地支持“约 3B 参数”的发布口径。仓库的推理 notebook 还记录过一次运行统计：总参数 `2,942,124,032`、DiT 参数 `1,091,722,240`（`getting_started/GR00T_inference.ipynb` 的输出单元）。不同数字可能来自 checkpoint/依赖版本、是否纳入外部 backbone、重复共享权重或统计时机，尚不能直接合并为一个精确结论。

| 参数表述 | 数值 | 证据状态 | 能够说明什么 | 不能说明什么 |
|---|---:|---|---|---|
| 发布模型名称 | GR00T-N1.7-3B | 官方资料已证实 | 发布方按约 3B 定位该 checkpoint | 不能给出各子模块精确参数分割 |
| safetensors 索引总参数 | 3,144,016,000 | 代码/权重元数据已证实 | 当前本地权重索引记录的全模型张量规模 | 尚未按 backbone/action head 自动复算 |
| notebook 总参数输出 | 2,942,124,032 | 仓库运行记录已证实 | 某次仓库环境加载后的统计口径 | 与 safetensors 的差异原因待复现 |
| notebook DiT 输出 | 1,091,722,240 | 仓库运行记录已证实 | 某次统计中 DiT 子模块约 1.09B | 不等于整个 action head；不等于所有非 VLM 参数 |
| “总计约 2.2B；视觉头约 1.34B；动作头约 0.8B” | — | 用户提供，待核对 | 可作为待追踪的原始说法 | 与当前 3B/3.14B 证据冲突，当前不宜写成结论 |

正式汇报建议采用保守写法：“N1.7 的公开 checkpoint 命名为 3B；当前本地 safetensors 索引为 3.144B 参数。动作 DiT 的仓库 notebook 样例约为 1.092B。子模块参数量必须用固定 checkpoint、固定加载方式和明确模块边界重新统计。”这样既保留事实，也避免用未经核对的 2.2B 分割误导后续扩展决策。

### 2.4 预训练覆盖与零样本边界

N1.7 的发布训练覆盖双臂、半人形与大规模人形机器人数据，并引入 20,000 小时 EgoScale 人类视频。Policy 使用指南进一步列出基础 checkpoint 内置、可用于 zero-shot 的 embodiment tags：DROID、X-DOF、REAL_G1、R1 Pro Sharpa 的若干变体等（`getting_started/policy.md:49-60`）。这说明“预训练覆盖”在工程上并不是一个抽象标签，而是 checkpoint 的 processor 中实际保存了若干可解释状态/动作键、归一化信息与 tag 的模态配置。

反面边界同样重要。`embodiment_tag` 必须在 checkpoint 的 processor modality config 内存在，否则 `Gr00tPolicy` 在初始化时直接报错（`gr00t/policy/gr00t_policy.py:127-160`）。`NEW_EMBODIMENT` 只能用于带自定义 modality config 的微调；其配置会随训练保存到 checkpoint，并在推理时加载（`getting_started/policy.md:42-45`）。RoboCasa 以厨房操作为评测场景，但不属于 N1.7 的预训练 embodiment 集，需要从基础模型微调。因此，不能把“仓库展示厨房 benchmark”误写为“基础模型在所有厨房机器人上已零样本预训练”。

| 命题 | 证据 | 正确解释 | 不应推出的结论 |
|---|---|---|---|
| N1.7 预训练含人形、半人形和双臂数据 | 上游发布训练覆盖说明 | 训练数据来源具有跨 embodiment 的多样性 | 任意新机械臂都无需微调 |
| N1.7 使用 20k 小时 EgoScale 人类视频 | 上游发布训练覆盖说明 | 发布方将人类视频作为预训练组成，并以相对 EEF 表示支持迁移 | 人类视频本身已直接给出当前机器人关节动作标签 |
| 基础 checkpoint 支持指定 pretrain tags 的零样本推理 | `getting_started/policy.md:42-60` | 这些 tag 的处理契约被 checkpoint 支持 | 所有 `EmbodimentTag` 都可在 base checkpoint 上运行 |
| `NEW_EMBODIMENT` 可用于自定义机器人 | `getting_started/policy.md:42-45` | 新机器人有明确的配置注册和后训练入口 | 只要改 tag 名称就能获得可靠泛化 |
| RoboCasa 为厨房类 benchmark | RoboCasa 场景说明 | 工程中有厨房任务的评测/微调路径 | RoboCasa 是 N1.7 基础 checkpoint 的预训练 embodiment |

### 2.5 推理性能与控制频率：必须说明条件

用户提供的性能说法为：L40、bf16 下生成一个 16-step action chunk 为 63.9 ms，约 15 Hz。该数字目前尚未在本地仓库找到相同条件的一手表格，故保留为**用户提供，待核对**。当前仓库的《Hardware Recommendations》给出的可核对数据是：N1.7、4 个 denoising steps、1 路相机条件下，L40 的模型重规划频率为 PyTorch eager 7.8 Hz、TensorRT 26.0 Hz（`getting_started/hardware_recommendation.md:9-29`）。这与 15 Hz 并不必然矛盾，因为分辨率、相机数、执行后端、计时范围、动作 horizon 与预后处理是否纳入都可能不同；但它们不能被视为同一 benchmark。

更重要的是，仓库明确区分 **模型重规划频率** 和 **机器人动作执行/相机采集频率**：一次推理返回一个多步 action chunk，因此可以借助 chunking 和异步推理，使约 10 Hz 的重规划支撑约 30 FPS 的动作执行（`getting_started/hardware_recommendation.md:31-37`）。Policy 指南亦区分模型预测的 `action_horizon` 与每次重新规划前实际执行的 `execution_horizon`；本地基础 checkpoint 的预测长度是 40，而 open-loop 常用执行长度是 16（`getting_started/policy.md:82-90`）。

| 指标 | 当前可确认条件 | 可确认数值 | 解释时必须附带的边界 |
|---|---|---:|---|
| L40 PyTorch eager 重规划率 | 1 camera、4 denoising steps、N1.7 | 7.8 Hz | 是模型产生 action chunk 的频率，不是机器人关节下发频率 |
| L40 TensorRT 全管线重规划率 | 同上 | 26.0 Hz | 需要 ONNX/TensorRT 导出与 engine；不能直接等同 PyTorch 结果 |
| 基础 checkpoint 预测动作长度 | 当前 `config.json` | 40 steps | 预测长度不等于每次实际执行长度 |
| 本项目配置的动作标签窗口 | `linkerhand_right_o6_config.py:29-45` | 16 steps | 这是本项目监督/接口窗口，需继续核实训练配置与模型 40-step 输出之间的 padding/mask 行为 |
| L40 bf16、16-step、63.9 ms | 用户提供 | 约 15 Hz | 待定位原始 benchmark 的模型版本、相机数、输入大小、去噪步数与计时范围 |

### 2.6 对扩展工作的直接含义

模型定位带来三个工程约束。第一，新的传感器并不自动变成模型可用信息；必须通过数据、Processor 和模型条件接口形成明确张量契约。第二，新的机器人动作空间不只是维度变化，还涉及动作表示（绝对关节、相对 EEF、latent action）、归一化、mask 和执行器语义。第三，性能目标必须拆开测量：数据预处理、backbone、DiT 多步去噪、反归一化、网络传输和机器人控制循环不应被压成单一“Hz”数字。

### 2.7 发布事实、适用边界与口径冲突

N1.7 以 GA（General Availability）版本发布，覆盖预训练权重、参考实现、custom-data fine-tuning、Policy API、ONNX/TensorRT 与 benchmark examples。工程工作流可概括为：LeRobot 数据准备 → 使用预训练 embodiment 的 zero-shot 或微调 checkpoint → fine-tune → open-loop → 仿真或真机 → controller integration。该顺序与本报告的工程分层一致，但不能免除当前项目的物理时序、未见数据泛化和真机安全验证。

| 发布/使用事实 | 可用于本研究的结论 | 与本项目/代码的交叉证据 | 不应作出的推论 |
|---|---|---|---|
| `GR00T-N1.7-3B` base checkpoint | 发布方采用约 3B 的 checkpoint 口径；预训练 tag 才可 zero-shot | 上游 checkpoint 使用约束；本地 safetensors index 为 3,144,016,000 | 任意 `EmbodimentTag` 或任意新机器人可 zero-shot |
| Cosmos-Reason2-2B / Qwen3-VL、flow-matching DiT | N1.7 的结构定位是 VLM + 连续动作去噪头 | `Gr00tN1d7`、`dit.py` 与上游架构说明 | 架构概览图已证明本项目每层参数行为 |
| relative EEF 是 N1.7 的跨 embodiment 主路线 | relative EEF 是重要动作表示，需作为新 embodiment 设计选项审查 | 本项目 `ActionConfig.rep=ABSOLUTE`；上游动作表示说明 | 当前 13D arm/O6 数据已转为 relative EEF，或 relative 必然优于其绝对关节表示 |
| 双臂、半人形、人形与 20K 小时 EgoScale | 可作为预训练覆盖和迁移动机来源 | 上游发布训练覆盖说明 | 人类视频直接提供当前 13D 关节监督，或保证新机器人泛化 |
| 硬件建议 | 推理最低建议为单卡 16 GB+；微调推荐 40 GB+，H100/L40 为优选 | 上游硬件建议；本项目 24 GB 4090 的低显存改动是本地工程折中 | 推荐硬件是硬性门槛，或 4090 训练结果可与 H100/L40 直接比较 |
| 许可说明 | 复用时必须区分代码和权重的许可证 | 上游许可说明 | 将所有模型权重简单称为 Apache 2.0 |

发布概述中“fully commercially licensable under Apache 2.0”的表述与具体 License 节存在张力：具体许可区分为**代码 Apache 2.0，模型权重 NVIDIA Open Model License**。本研究采用更具体的许可口径；任何公开发布、商用或再分发决定仍须以仓库 `LICENSE`、模型卡和适用法律审查为准，而非以本报告替代许可意见。

此外，Cosmos-Reason2-2B 是 gated Hugging Face backbone，首次模型加载需要访问授权；视频解码使用 torchcodec，并受 FFmpeg 版本约束。这两项不是算法问题，却是复现和部署的真实依赖边界。本项目之所以可离线运行，是因为已将 backbone 下载到 `/mnt/data/.../cosmos_reason2_2b`；将来迁移环境时仍应把模型访问权、video backend 和 FFmpeg runtime 纳入 preflight 检查。

---

## 3. 代码仓模块图与依赖方向

### 3.1 代码仓总体结构

本地工程是 Python 3.12 的 `gr00t` 包，使用 PyTorch 2.9、Transformers 4.57.3、Diffusers 0.35.1、Tyro 等依赖；构建与依赖声明位于 `gr00t_n1/pyproject.toml`。目录不是简单按功能平铺，而是可以归纳为四类：**契约层**（configs、data types、embodiment）；**模型层**（model）；**运行编排层**（experiment、policy、eval、deployment）；**集成与证据层**（examples、scripts、tests、getting_started）。

```text
gr00t_n1/
├── gr00t/                         可安装的主包
│   ├── configs/                   配置 dataclass、模型/数据/训练配置与注册
│   ├── data/                      LeRobot 数据读取、stats、step/shard、状态动作变换、tag
│   ├── model/                     模型注册、pipeline、N1.7、backbone、DiT 等模块
│   ├── experiment/                微调 CLI 的运行编排、Trainer、checkpoint callback
│   ├── policy/                    面向机器人/环境的推理 API 与 client/server
│   ├── eval/                      open-loop、rollout、仿真/真机评测入口
│   ├── deployment/                部署脚本共享类型与运行时辅助
│   └── utils/                     分布式、序列化、运行时通用工具
├── examples/                      每个 embodiment 的配置和接入样例
├── scripts/                       转换、导出 ONNX、构建 TensorRT、平台部署脚本
├── getting_started/               参考流程、硬件和 Policy 使用指南
├── tests/                         CPU/GPU、部署与回归测试
└── external_dependencies/         LIBERO、SimplerEnv、RoboCasa 等外部基准依赖
```

表 3 不把目录当成结论，而是给出每层拥有的“唯一责任”和依赖方向。后续代码阅读应沿着这些边界展开，而不需要试图先读完所有文件。

| 模块 | 核心责任 | 对外输出 | 主要依赖 | 不应承担的责任 |
|---|---|---|---|---|
| `configs` | 将模型、数据、训练选项组织为类型化 `Config` | 可验证的配置对象与保存的 YAML | `data.types`、模型配置注册 | 不读取视频或计算 loss |
| `data` | 将 LeRobot episode 变为带模态、时间窗和统计信息的样本 | dataset、step data、stats、tag/动作表示 | pandas/torch/LeRobot 约定 | 不决定网络结构 |
| `model` | 定义 backbone、动作头、processor/collator 与 pipeline 装配 | 可由 HF `AutoModel` 加载的模型；processor | `configs`、`data`、Transformers | 不决定训练循环或机器人硬件调用 |
| `experiment` | 将 CLI/配置转成 trainer、checkpoint 和训练过程 | checkpoint、processor、配置工件 | `configs`、`model`、Transformers Trainer | 不定义数据格式或动作物理含义 |
| `policy` | 将实时观测检查、处理、模型预测、反解码为动作字典 | action chunk | `model`、`data.interfaces/types` | 不直接实现底层伺服与安全控制 |
| `eval` | 定义开环与 rollout 对比、仿真/服务端连接 | MSE/MAE、轨迹图、评测运行 | `data`、`policy` | 不应把开环指标伪装成真机成功率 |
| `deployment` / `scripts` | 将模型导出、编译、放到具体硬件 | ONNX/TRT engine、平台运行入口 | `model`、TensorRT、ONNX | 不改变模型业务语义 |
| `examples` | 提供具身形态的配置与可运行集成示例 | modality config、shell 调用样例 | 主包公开接口 | 不应成为核心模型逻辑的唯一来源 |

### 3.2 配置与注册：工程不是硬编码单一路径

GR00T 用两层注册避免训练入口直接硬编码 N1.7。第一层是模型注册：`gr00t/model/__init__.py:16` 导入 `gr00t_n1d7.setup`，后者在模块尾部执行 `register_model(Gr00tN1d7Config, Gr00tN1d7Pipeline)`（`setup.py:242`）；`MODEL_REGISTRY` 以配置类型为键（`gr00t/model/registry.py:16-22`）。第二层是 embodiment 的 modality config 注册：用户的 Python 配置被动态 import，导入时调用注册函数，使 `NEW_EMBODIMENT` 成为 `Config.validate()` 可识别的数据契约。

这解释了为什么当前项目不是在主仓库模型文件中手改“13D”：项目的 `examples/linkerhand_right_o6_config.py` 在 import 时注册 state/action/video/language 的键与动作语义；`launch_finetune.py` 则在读取参数后显式导入该文件。

```python
# gr00t/experiment/launch_finetune.py:30-41（节选）
def load_modality_config(modality_config_path: str):
    path = Path(modality_config_path)
    if path.exists() and path.suffix == ".py":
        sys.path.append(str(path.parent))
        importlib.import_module(path.stem)
    else:
        raise FileNotFoundError(...)
```

随后 `Config.validate()` 会检查每个 dataset 的 tag 是否存在 modality config；不存在时，报错并明确提示传入 `--modality-config-path`（`gr00t/configs/base_config.py:169-193`）。这是一条重要的扩展边界：**具身差异首先被表达为配置和数据契约，而不是散落在训练循环中的 if/else。**

### 3.3 训练调用图：从项目 shell 到 checkpoint

训练路径中的控制流如下。箭头表示运行时调用或对象构造，括号内是该边的主要输入输出。它回答“训练脚本到底把数据送到哪里”和“checkpoint 为什么包含 processor”两个问题。

```mermaid
flowchart TD
    A[finetune_right_o6_13d.sh\n项目封装参数] --> B[launch_finetune.py\nTyro: FinetuneConfig]
    B --> C[动态 import modality config\n注册 NEW_EMBODIMENT]
    B --> D[get_default_config + load_dict\nConfig(model, data, training)]
    D --> E[experiment.run]
    E --> F[MODEL_REGISTRY\nGr00tN1d7Pipeline]
    F --> G[AutoModel / Gr00tN1d7\nbackbone + action head]
    F --> H[AutoProcessor / Processor\n模态解释与归一化]
    F --> I[DatasetFactory\nSharded*Dataset]
    F --> J[processor.collator]
    G --> K[Gr00tTrainer]
    H --> K
    I --> K
    J --> K
    K --> L[checkpoint + processor/\nexperiment_cfg/]
```

这张图的关键不是组件数，而是每条边的责任：

| 调用边 | 源码证据 | 输入与处理 | 输出与工程含义 |
|---|---|---|---|
| A → B | `finetune_right_o6_13d.sh:48-72` | 传入 base model、dataset、tag、modality config、batch、shard 等 | 项目脚本只提供可复现参数，不含模型训练主体 |
| B → C | `launch_finetune.py:55-57` | 文件路径被动态 import | 自定义 config 的注册副作用发生在此处；导入失败应立即失败 |
| B → D | `launch_finetune.py:59-143` | `FinetuneConfig` 覆盖统一 `Config` 的 data/model/training 字段 | CLI 与内部对象之间的信任边界；应审查这里是否覆盖了预期参数 |
| D → E | `launch_finetune.py:145` | 完整 `Config` | 进入通用训练编排，不再依赖本项目 shell |
| E → F | `experiment.py:247-253` | 按 `type(config.model)` 在 registry 找到 pipeline，调用 `setup()` | N1.7 pipeline 集中创建模型、数据、collator、processor |
| F → G/H/I/J | `setup.py:73-76, 78-239` | checkpoint/config 和 dataset path | 将“模型结构”“数据读取”“预处理”解耦为可替换部件 |
| E/F → L | `experiment.py:254-256, 305-371` | Processor 与 Trainer 都参与保存 | 推理 checkpoint 不能只看模型权重；processor 是归一化和 tag 契约的一部分 |

`experiment.run()` 还承担运行环境而非学习算法本身的责任：校验 GPU 数与 `WORLD_SIZE` 一致、初始化 NCCL、创建输出目录、保存 config 工件、构建 Hugging Face `TrainingArguments`、挂接 checkpoint callback 并调用 `trainer.train()`（`gr00t/experiment/experiment.py:53-69, 192-371`）。该分层使后续更换优化器、分布式策略或保存策略有明确位置，而无需改动模型 forward。

### 3.4 推理调用图：从实时观测到物理单位动作

推理链路与训练共享同一个 checkpoint 中的模型和 processor，但没有 ground-truth action，也没有 Trainer。`Gr00tPolicy` 是机器人/环境集成的正式边界：它加载模型与 processor，验证 embodiment tag，检查观测结构，调用模型生成归一化 action，再按同一 tag 反归一化。

```mermaid
flowchart LR
    A[机器人/仿真观测\nvideo + state + language] --> B[Gr00tPolicy.check_observation]
    B --> C[VLAStepData\nimages/states/text/tag]
    C --> D[Gr00tN1d7Processor]
    D --> E[processor.collator]
    E --> F[Gr00tN1d7.get_action]
    F --> G[Qwen3/Cosmos backbone]
    G --> H[flow-matching action head\nDiT 多步生成]
    H --> I[normalized action_pred]
    I --> J[processor.decode_action]
    J --> K[物理单位 action chunk\n按 key 返回]
    K --> L[调用方的 RTC/控制器/执行器]
```

`Gr00tPolicy.__init__()` 用 `AutoModel.from_pretrained()` 加载模型并以 bf16 放到指定设备，同时从 checkpoint 根目录或 `processor/` 子目录加载 processor；随后检查所选 tag 是否确实存在于 checkpoint 的 modality configs（`gr00t/policy/gr00t_policy.py:100-166`）。这意味着部署期的正确性不只取决于 model weights：若错配 processor、tag 或 state/action key，即使模型权重文件正常加载，策略也应当拒绝运行。

核心推理过程在 `_get_action()` 中，逻辑与图中的箭头一一对应：

```python
# gr00t/policy/gr00t_policy.py:403-426（节选）
processed_inputs.append(self.processor(messages))
collated_inputs = self.collate_fn(processed_inputs)
with torch.inference_mode():
    model_pred = self.model.get_action(**collated_inputs)
normalized_action = model_pred["action_pred"].float()
unnormalized_action = self.processor.decode_action(
    normalized_action.cpu().numpy(), self.embodiment_tag, batched_states
)
```

模型内部的训练/推理分叉也清晰存在：`Gr00tN1d7.forward()` 调用 `action_head(...)` 以产生训练 loss，而 `Gr00tN1d7.get_action()` 调用 `action_head.get_action(...)` 以采样动作（`gr00t/model/gr00t_n1d7/gr00t_n1d7.py:603-632`）。二者都共享 `prepare_input()` 与 backbone，因此图像、语言、state 的条件编码逻辑应尽可能保持一致；差异仅在于训练时有真实 action 监督，推理时从噪声经若干 flow-matching 步生成 action。

### 3.5 评估、部署与控制器的依赖方向

`eval/open_loop_eval.py` 不直接重新实现模型，而是将离线 episode 的 state/image/language 转换为 observation，调用统一的 Policy 接口，将 action chunk 与记录的 ground truth 对齐后计算未归一化 MSE/MAE 并绘图（`gr00t/eval/open_loop_eval.py:136-234`）。这使 open-loop 评估验证的是“离线观测下动作预测是否接近数据动作”，不是“策略执行动作后环境会如何变化”。

部署分支可以把同一个模型导出 ONNX、构建 TensorRT engine，或者通过 server/client 运行；这些路径应依赖 Policy/模型的稳定输入输出契约，而不回写数据或训练逻辑。机器人控制器则位于 GR00T Policy 之后：其接收每次预测的 action chunk，选择其中多少步执行，可能应用 RTC、平滑和安全限幅，然后在下一次重规划时提供新观测。仓库的 `execution_horizon` 定义正是这一边界的证据，而不是模型内部 horizon 的别名（`getting_started/policy.md:82-90`）。

### 3.6 本项目 13D 实例在模块图中的落点

当前项目的路径可以明确映射到上述通用图，而不会污染核心架构：

| 通用模块边界 | 本项目对应物 | 当前已验证的含义 | 后续应继续核对的点 |
|---|---|---|---|
| 原始数据 → LeRobot | `convert_to_lerobot_right_o6.py` | telemetry/video 被转换为数据集工件 | 时间戳、动作相对 state 的时序与单位是否持续正确 |
| embodiment 配置 | `gr00t_n1/examples/linkerhand_right_o6_config.py` | 3 路图像、13D state/action、16-step 标签、`NEW_EMBODIMENT` 已注册 | 16-step 标注与基础模型 40-step action horizon 的 mask/padding 细节 |
| 训练入口 | `finetune_right_o6_13d.sh` | 明确向通用入口传入 dataset、base checkpoint 和 config | shell 参数与最终输出配置是否完全一致 |
| 通用训练主链 | `launch_finetune.py` → `experiment.py` → `Gr00tN1d7Pipeline` | 不需要在模型主干中写“ROKAE/O6 特例” | 当前本地对 upstream 文件的修改需与上游版本隔离和审计 |
| 推理/评估 | `Gr00tPolicy`、`open_loop_eval.py` | checkpoint 可被统一 Policy 路径加载和评估 | 开环指标、动作限幅、真机闭环成功率需要分开验证 |

### 3.7 章节结论与下一步

代码仓的核心架构不是“一个训练脚本调用一个模型”，而是一套通过 config、registry、processor 和 checkpoint 工件连接的可替换系统。训练端的组装中心是 `Gr00tN1d7Pipeline`；推理端的稳定边界是 `Gr00tPolicy`；二者共同依赖同一组 modality config、statistics 和模型配置。该结论给出了后续研究的阅读顺序：先在第 4 章证明数据如何变成 step/shard 与归一化统计量，再在第 5 章解释 tag/mask/projector 如何承载跨 embodiment 差异，最后进入模型与训练细节。

当前未知也必须保留：本项目对上游 `launch_finetune.py`、`finetune_config.py`、`gr00t_n1d7.py` 存在本地修改；这些修改的必要性、兼容性与是否应长期维护，尚未在本章裁定。后续应以“原始上游行为—本地修改—训练需要—验证证据”的方式单独审计，避免把临时环境修复误认为 N1.7 的原生架构。

### 3.8 工程入口与源码阅读的对应关系

工程入口图表明：reference implementation 位于本仓库；LeRobot-native workflow 指向 Hugging Face LeRobot 的 `groot` policy；各 benchmark 具有独立的数据、训练和评估命令；部署路径包括 `Policy API`、server/client、ONNX/TensorRT；新机器人接入由 `finetune_new_embodiment.md` 说明。后续新增一项代码研究时，应先定位该功能声明的入口与前置条件，再沿具体 class/function、config 和真实工件验证它，而不是只按目录名猜测。

运行依赖也应进入工程风险表：仓库依赖 git submodule 与 git-lfs 获取部分 demo parquet；GPU 训练推荐的资源高于本项目 4090；torchcodec/FFmpeg 影响 MP4 数据读取；gated backbone 影响冷启动和可复现性。这些是“代码能否启动”的环境边界，不是 N1.7 模型结构本身，也不应被遗漏。

---

## 参考证据索引（第 1—3 章）

| 编号 | 本地证据 | 用途 |
|---|---|---|
| E1 | 上游发布、模型与使用材料（相应章节） | N1.7 定位、backbone、发布 checkpoint、tag 和版本变化 |
| E2 | `gr00t_n1/getting_started/policy.md:1-112` | Policy、pretrain/posttrain tags、horizon 定义 |
| E3 | `gr00t_n1/getting_started/hardware_recommendation.md:1-75` | L40 重规划频率与 action chunk 边界 |
| E4 | `gr00t_n1/gr00t/configs/model/gr00t_n1d7.py:27-180` | N1.7 默认配置与 DiT/flow 参数 |
| E5 | `gr00t_n1/gr00t/model/gr00t_n1d7/gr00t_n1d7.py:491-645` | backbone 选择、模型装配、forward/get_action |
| E6 | `gr00t_n1/gr00t/model/gr00t_n1d7/setup.py:47-242` | pipeline、模型/processor/dataset/collator 创建、模型注册 |
| E7 | `gr00t_n1/gr00t/experiment/launch_finetune.py:30-145` | CLI、动态 modality config import、配置覆盖 |
| E8 | `gr00t_n1/gr00t/experiment/experiment.py:192-385` | run、Trainer、processor/checkpoint 保存 |
| E9 | `gr00t_n1/gr00t/policy/gr00t_policy.py:70-176, 380-432` | 推理加载、输入检查、处理、模型调用、解码 |
| E10 | `gr00t_n1/gr00t/eval/open_loop_eval.py:136-234` | open-loop 评估的实际含义 |
| E11 | `gr00t_n1/checkpoints/gr00t_n1_base/config.json` 与 `model.safetensors.index.json` | 当前本地 checkpoint 配置与参数索引元数据 |
| E12 | `finetune_right_o6_13d.sh:1-73`；`gr00t_n1/examples/linkerhand_right_o6_config.py:1-57` | 13D 案例映射 |
| E33 | 上游发布与使用材料（版本、数据、训练、评估与许可章节） | 官方发布定位、工作流、依赖、LeRobot schema、server/client、训练/评估路径、许可证与论文引用 |

---

## 4. 数据系统：从 LeRobot 演示到模型 batch

### 4.1 数据边界与对象层级：必须区分六个对象

数据系统并非把一个数据目录直接“喂给模型”。它先把磁盘上的 **episode** 恢复为带时间索引的多模态表，再从中截取一个决策时刻的 **step sample**，最后将多个已处理 step 组织为模型的 **batch**。`ShardedSingleStepDataset` 的名称即说明训练基本样本是 single step，而不是整条 episode（`gr00t/data/dataset/sharded_single_step_dataset.py:82-303`）。

| 对象 | 精确定义 | 当前 13D 实例 | 创建者 / 消费者 | 不是什么 |
|---|---|---|---|---|
| episode | 一次完整演示的时间有序轨迹 | 148 条；每条 251–639 帧；episode 0 为 477 帧 | converter 写入；`LeRobotEpisodeLoader.__getitem__()` 读取 | 不是一个梯度样本或 shard |
| frame / timestep | episode 内一个离散时刻 `t`，当前 30 fps | 13D state、13D action、三路图像对应帧、task 索引 | parquet/video 解码后由 DataFrame 表示 | 不等于一次模型输出 |
| step sample / `VLAStepData` | 围绕一个决策时刻，按各 modality 的 `delta_indices` 截取的原始多模态样本 | `t` 的 state/三图/task，及 `t...t+15` 的 action | `extract_step_data()` 创建；Processor 消费 | 不是整条轨迹，也不含 batch 维 |
| action chunk | 一个 step 对应的未来动作监督序列或推理输出序列 | 原始训练标签为 `16 × 13`；Processor 后 pad 为 `40 × 132` | Processor、action head、Policy | 不等于控制器必须执行的步数 |
| shard | 为加载、内存控制和随机性组织的一组 step 索引 | 目标约 1,024 step；实测 44 个 shard | `ShardedSingleStepDataset` 创建；mixture dataset 调度 | 不是 parquet 的物理 chunk，也不是 batch |
| batch | collator 将多个 Processor 输出样本沿 batch 维堆叠的模型输入 | batch size `B` 时 state 为 `(B,1,132)`、action 为 `(B,40,132)` | `Gr00tN1d7DataCollator` 创建；`forward()` 消费 | 不保证来自同一 episode 或 shard |

当前数据集有 47,250 个原始帧。动作窗口为 16，且训练配置 `allow_padding=false`；于是长度为 `L` 的 episode 只有 `L - 16 + 1 = L - 15` 个合法训练起点。148 条 episode 合计排除尾部 2,220 帧，得到 **45,030 个有效 step**。这是可抽样的监督决策时刻数，而不是视频帧数，也不是一个 epoch 必然恰好消耗的样本数。

```text
episode 0（477 帧）
  t=0    → VLAStepData：obs[0]   + action[0:16]
  t=1    → VLAStepData：obs[1]   + action[1:17]
  ...
  t=461  → VLAStepData：obs[461] + action[461:477]，最后一个有效样本

多个 episode 的有效 t 索引 → shard → VLAStepData → Processor → collator batch
```

这个对象层级也是扩展边界：视频、状态、动作在 `VLAStepData` 前仍按具身形态分组；只有进入 Processor 后才被拼接、归一化和 padding。新增一组状态或动作时，首先要验证元数据切片与 modality config，而不是直接在模型中拼接数组。

### 4.2 LeRobot 物理存储契约：文件即读取协议

当前数据集根目录为 `/mnt/data/gr00t-finetune/datasets/lerobot_dataset_right_o6_13d`，采用“数值轨迹在 parquet、图像在 MP4、结构和语义在 `meta/`”的布局。`convert_to_lerobot_right_o6.py` 因而不仅是格式转换工具：它定义 state/action 单位、episode 行数、相机命名、视频路径模式及 state/action 的分组边界，应与训练 config 一起审计。

该布局是 GR00T 使用的 LeRobot v2 变体：额外的 `meta/modality.json` 用于描述 state/action/video 的结构。这与 loader 实际按 `modality.json` 切分扁平数值、选择 video keys 的行为一致。`NEW_EMBODIMENT` 的 SO100 接入示例说明自定义具身并非旁路功能；但示例能够运行不构成对本项目 13D 单位、时序或质量的验证。

| 工件 | 当前内容 | 生产者 | 消费者 | 缺失或错误时的影响 |
|---|---|---|---|---|
| `data/chunk-000/episode_*.parquet` | 每行一个时刻。episode 0 已验证为 477 行、7 列 | `write_episode()` | `LeRobotEpisodeLoader.__getitem__()` | 数值轨迹无法读取或列/shape 不匹配 |
| `videos/.../observation.images.<camera>/episode_*.mp4` | 三路 RGB 视频；总计 444 个（148 × 3） | converter | loader 按帧索引解码 | 相机缺失、路径模式错误或帧对齐错误 |
| `meta/info.json` | feature schema、fps、data/video path pattern、chunk 信息 | `write_metadata()` | loader 初始化、stats 生成 | 无法正确定位或解释数据 |
| `meta/modality.json` | `observation.state`、`action` 内各 group 的 start/end 和原始键名 | `write_metadata()` | loader 数值切片、stats 切片 | 总维度可正确但组语义被切错 |
| `meta/episodes.jsonl` | 每 episode 的 index、length、tasks 等轨迹级信息 | `write_metadata()` | loader 的长度和语言构造 | 有效 step 数和语言映射错误 |
| `meta/tasks.jsonl` | `task_index → task` 字典 | `write_metadata()` | loader | 无法还原任务文本 |
| `meta/stats.json` | 浮点字段的 mean/std/min/max/q01/q99 | `generate_stats()` | loader、Processor | loader 初始化时直接 assert 失败 |
| `meta/relative_stats.json` | relative action group 的统计及 fingerprint | `generate_rel_stats()` | loader 合并为 `relative_action` | 当前 13D 无有效 relative group |

episode 0 parquet 已实读验证出下列原始列：

```text
observation.state  float32 ndarray [13]
action             float32 ndarray [13]
timestamp          float32 ndarray [1]
frame_index        int64   ndarray [1]
episode_index      int64   ndarray [1]
index              int64   ndarray [1]
task_index         int64   ndarray [1]
```

磁盘上的两个 13D 向量并不天然知道前 7 维是 ROKAE、后 6 维是 O6。这个语义由 `modality.json` 和 `linkerhand_right_o6_config.py` 共同定义为 `right_arm[0:7] + right_o6_hand[7:13]`；loader 依这些范围拆成 `state/action.<group>`（`lerobot_episode_loader.py:305-398, 500-535`）。因此，分组顺序错误属于高风险的静默数据错误。

转换端的 `scan_episodes()` 检查 telemetry 长度、相机 timestamps 单调性和视频帧数一致性；`extract_state_action()` 从 `timestamps/qpos/actions` 取右臂 7D 与 O6 6D，将 O6 原值乘 `100/255`，并检查 `[T,13]` 与有限值（`convert_to_lerobot_right_o6.py:74-144`）。这解释 O6 stats 大致位于 `[0,100]`：它来自 converter 的单位定义，不是模型自动推断的单位。

语言也不是 parquet 中的逐帧人工标注。loader 从 `episodes.jsonl["tasks"]` 随机选择 task 后复制至该 episode 的每个时刻（`lerobot_episode_loader.py:537-563`）。当前每条都只有 `"pouring"`，所以随机性不改变文本；未来若一条轨迹存在多个 task，此处将成为语言增强和语义风险点。

### 4.3 从 episode 到 step：时间窗口与尾部边界

时间采样由 modality config 明确规定，而不是模型自动猜测。当前 config 使用 `video/state/language.delta_indices=[0]`，action 使用 `delta_indices=[0,1,...,15]`（`examples/linkerhand_right_o6_config.py:19-57`）。`extract_step_data()` 对每个 modality 计算 `step_index + delta_index`，从 episode DataFrame 取行；数值项 `np.vstack` 为二维数组，图像和语言保留列表，最终构造 `VLAStepData`（`sharded_single_step_dataset.py:27-79`）。

| episode 0 决策时刻 | state / video / language | action 标签 | 合法训练起点 | 原因 |
|---:|---|---|---|---|
| `t=0` | 第 0 帧 13D state、三路图像、`pouring` | `action[0]...action[15]`，`16 × 13` | 是 | 末端索引 15 有效 |
| `t=461` | 第 461 帧观测 | `action[461]...action[476]` | 是 | 最后完整窗口 |
| `t=462` | 第 462 帧观测 | 需要到 `action[477]` | 否 | 最小实测为 pandas `IndexError` |
| `t=476` | 最后一帧观测 | 只剩一个 action | 否 | 不足完整 16-step window |

```text
0 ─────────────────────────────────────────────────────── 476
t=0:    [obs 0]   [a0  a1  ... a15]
t=461:                   [obs 461] [a461 ... a476]
t=462:                            [obs 462] [a462 ... a477 ✗]
```

`get_effective_episode_length()` 用 `max(0, original_length - action_horizon + 1)` 生成 shard 可用的起点数（`sharded_single_step_dataset.py:230-236`）；当前训练因此主动排除每条尾部 15 帧。`allow_padding=true` 仅会在 `extract_step_data()` 中将越界索引 clamp 到 `[0,len-1]`，并不会使 shard 有效长度自动增加。当前“无尾部 padding”同时由 `allow_padding=false` 与有效长度策略保证。

代码能够检查行数和数组边界，却不能证明动作的物理时间语义。例如 parquet 第 `t` 行 action 是否是与第 `t` 个观测同步的控制目标、是否带控制延迟，必须依 telemetry 时间戳和控制器日志额外审计。这是后续真机闭环前的必要验证，而非数据 shape 检查可以替代的内容。

### 4.4 shard 与采样：内存、I/O 与随机性的逻辑容器

shard 是“一组待 materialize 的 step 索引计划”，不是重新切分 parquet 的物理文件。真实 parquet/MP4 仍按 episode 存储；`get_shard()` 读取该 shard 涉及的完整 episode，再取出其被分配的 step，送入 Processor（`sharded_single_step_dataset.py:264-283`）。这样避免把所有 45,030 个 step 的图像和处理后张量常驻内存，也使一个 shard 内同一 episode 的加载可以复用。

```text
148 个 episode
  → 每条保留 L-15 个有效 t 并打乱
  → 依 0.1 参数拆为 10 个交错子序列
  → 贪心均衡分配
  → 44 个约 1,024-step 的逻辑 shard
  → 训练 schedule 选 shard、预加载、再生成 batch
```

`shard_dataset()` 的实际步骤为：随机排列 episode；打乱每条的有效 step index；以 `i::num_splits` 生成交错子序列；先确保每个 shard 非空，再把其余子序列放入当前最短 shard（`sharded_single_step_dataset.py:145-225`）。当前只读构造验证在 `shard_size=1024`、`episode_sampling_rate=0.1`、seed=42 下得到 **44 个 shard**，step 总和 **45,030**，平均 1023.409，标准差 6.641。

这里需要纠正参数名带来的常见误解。尽管 docstring 将 `episode_sampling_rate=0.1` 描述为使用 10% timestep，代码却做 `num_splits=int(1/rate)`，然后将 `step_indices[i::num_splits]` 的 **全部 10 个 split** 加入 `episode_splits`。静态代码和 45,030 的实测总和都表明：当前实现没有丢弃 90% 有效 step；该参数实际上改变子序列划分和 shard 混合粒度。今后调整此值必须打印 shard 总覆盖量，而不能只按参数名推断。

外层 `ShardedMixtureDataset` 处理多数据集与分布式情形：它合并 statistics，按数据集权重和平均 shard 大小构造 `num_shards_per_epoch` 长度的 schedule；某 child dataset 用尽 shard 时可以重新洗牌循环；之后按 rank/worker 过滤并后台预加载下一个 shard（`sharded_mixture_dataset.py:261-485`）。因此当前 `num_shards_per_epoch: 100000` 表示逻辑 epoch 调度 100,000 个 shard，不表示磁盘上有 100,000 个 shard。对当前仅 44 个 shard 的数据而言，同一有效 step 可以在一个逻辑 epoch 内被反复使用。

### 4.5 统计量与归一化：三类 statistics 的职责

统计量将不同物理范围的状态和动作映射到可训练的数值空间，并在推理时负责反变换回机器人单位。它不是附属描述文件：loader 强制要求 `meta/stats.json`；训练 Processor 使用它；训练产物又把实际使用的 statistics 保存为 checkpoint 的 `processor/statistics.json`。因此权重、Processor、statistics 不能在部署时任意混配。

| 层次 | 源码入口与输入 | 产物 | 当前 13D 含义 |
|---|---|---|---|
| 基础 dataset stats | `calculate_dataset_statistics()` / `generate_stats()` 遍历 parquet float feature | mean/std/min/max/q01/q99，含 schema fingerprint cache | 扁平 13D state 与 action 的全维统计 |
| relative action stats | `generate_rel_stats()`，仅处理 `rep=RELATIVE` group | `relative_stats.json` | 两组 action 均 absolute，当前只有 fingerprint sidecar |
| runtime processor stats | loader 依 metadata 将扁平 stats 切组；`StateActionProcessor.set_statistics()` 保存 | 分组的归一化参数 | right_arm 与 right_o6_hand 各使用自身数值范围 |

基础生成代码位于 `gr00t/data/stats.py:137-180, 251-291`；其 fingerprint 能检测 feature schema 变化后的缓存复用，却无法发现“shape 未变但单位由弧度改成角度”的语义漂移。loader 按 `modality.json` 将扁平 13D stats 切成 `[0:7]` 和 `[7:13]`（`lerobot_episode_loader.py:500-535`）；切片顺序错而总维度仍为 13 时，训练常不会报 shape 错，但归一化含义会完全错误。

最终保存的 Processor 配置为 `use_percentiles=true`、`clip_outliers=true`、`use_mean_std=false`、`apply_sincos_state_encoding=false`、`use_relative_action=true`（输出目录 `processor/processor_config.json:1115-1124`）。因此当前 state/action 使用 q01/q99 范围并裁剪，而不是 mean/std 或 raw min/max（`state_action_processor.py:145-205, 206-268, 333-419`）。其好处是降低极端采集值控制尺度的影响；代价是部署中超出训练分布的值会被压到边界。

`use_relative_action=true` **不等于**当前 13D 数据已转换成相对动作。绝对→相对转换还要求该 group 的 `ActionConfig.rep == RELATIVE`。当前 `right_arm` 与 `right_o6_hand` 都是 `ABSOLUTE`（`linkerhand_right_o6_config.py:31-45`），故不使用 relative stats，仍走 absolute action 归一化路径。类似地，state config 虽标记 `right_arm` 为 sin/cos key，但全局 `apply_sincos_state_encoding=false`，本次并未展开 sin/cos。解释实际训练时应以 checkpoint 保存的 processor config 为准，而非只看候选 modality config。

### 4.6 Processor 与 collator：从 `VLAStepData` 到 `forward()`

`Gr00tN1d7Processor` 负责将一个原始 step 转为模型契约：归一化并 pad 的 state；归一化并 pad 的 action 与 mask；embodiment projector index；以及交给 Qwen3-VL Processor tokenization 的图像/语言内容。随后 `Gr00tN1d7DataCollator` 堆叠数值项，并统一生成文本 token、attention mask 与视觉张量（`processing_gr00t_n1d7.py:159-208, 581-755`）。

```text
VLAStepData
  states:  {right_arm:(1,7), right_o6_hand:(1,6)}
  actions: {right_arm:(16,7), right_o6_hand:(16,6)}
  images:  3 views × 1 frame; text: "pouring"
      ↓ Processor
分组归一化 → 拼接 13D → pad 到 max_state/action_dim=132
16 个动作时刻 → pad 到 max_action_horizon=40；生成有效区 mask
三图变换 + Qwen chat template
      ↓ sample
{state, action, action_mask, embodiment_id, vlm_content}
      ↓ collator
数值 stack；Qwen3VLProcessor tokenization
      ↓ BatchFeature(data={"inputs": ...}) → model.forward(**inputs)
```

表 11 同时记录静态逻辑和一次真实只读执行。验证使用训练输出中保存的 Processor、当前数据集 episode 0 的 `t=0` 和 `NEW_EMBODIMENT`；未加载完整模型、未启动训练、未修改数据。环境为 `/home/tbl/miniforge3/envs/gr00t_n1/bin/python`，并明确令 Processor 处于 eval transform 分支以稳定检查 shape。

| 键 | 单 sample（Processor 输出） | batch size=1（Collator 输出） | 含义 |
|---|---|---|---|
| `state` | `(1,132)`，`float32` | `(1,1,132)`，`float32` | 7D+6D 前 13 维有效，后 119 维零 padding |
| `action` | `(40,132)`，`float32` | `(1,40,132)`，`float32` | 真实 `16 × 13` 标签先按维、再按时间 pad |
| `action_mask` | `(40,132)`，`float32` | `(1,40,132)`，`float32` | 实测和为 208，即 `16 × 13` 个有效监督元素 |
| `embodiment_id` | Python `int=10` | `(1,)`，`int64`，值 10 | `new_embodiment` 的 projector index |
| `vlm_content` | 3 张 RGB PIL 图像，实测每张 `(340,256)`，以及 chat text | 被 tokenized | 单时刻三视角与 `pouring` 共同成为 VLM 条件 |
| `input_ids` / `attention_mask` | collator 创建 | `(1,277)`，`int64` | Qwen chat/text/image 占位 token，长度随输入变化 |
| `pixel_values` | collator 创建 | `(1056,1536)`，`float32` | Qwen3-VL 视觉预处理张量，不应误称为原始 BCHW 图像 |
| `image_grid_thw` | collator 创建 | `(3,3)`，`int64` | 三张图像的视觉 token 网格元数据 |

padding 的目的不是把 13D 伪装为 132D 机器人，而是让统一 checkpoint 容纳不同 embodiment 的宽度与 horizon；`action_mask` 使 loss 忽略 padding。若新增动作维度或 horizon，Processor 会在构造/调用阶段检查上限；`validate_action_horizons()` 会拒绝超过 `max_action_horizon` 的 config（`processing_gr00t_n1d7.py:130-157, 603-641`）。训练模式和推理模式还会选择不同图像 transform；本次只读验证只证明加载和形状契约，不证明训练期随机增强的具体像素效果。

### 4.7 13D 案例映射与失效边界

表 12 将“telemetry + MP4 → loss”对应到可定位代码层。至此，输入侧已经具有磁盘 schema、时间窗口、stats、padding/mask 和实际 batch 的证据，而不再是黑盒。

| 层次 | 当前输入 | 转换与契约 | 输出 | 验证状态 |
|---|---|---|---|---|
| 原始采集 | telemetry `qpos/actions/timestamps` 与三路 MP4 | 选 7D + 6D、O6 乘 `100/255`；扫描帧数/时间戳 | 每 episode `[T,13]` 与视频 | 转换逻辑已查；控制时延待审计 |
| LeRobot | 数值与视频 | parquet 扁平 13D；metadata 定义 `[0:7]+[7:13]`；task 为 pouring | 148 episode、47,250 frame、444 video | metadata/parquet 已实读 |
| loader | 一条 episode 文件组 | metadata 数值切片、按 frame index 解三路视频、填充 task | 带 state/action/video/task 的 DataFrame | episode 0 shape 已验证 |
| step / shard | DataFrame 与 config | `obs[t]` + `action[t:t+16]`；尾部 15 帧排除 | 45,030 step、44 shard | `t=0/461` 可取、`t=462` 越界已验证 |
| Processor / collator | `VLAStepData` | absolute 归一化、13→132、16→40、Qwen tokenization | `forward()` 可用的 batch | 真实 t=0 batch shapes 已验证 |

下表区分早失败和静默污染。后者对后续触觉扩展尤为关键：触觉的采样率、缺失值、坐标系或单位即使 shape 正确，也可能令模型学习错误对应关系。

| 风险 | 通常是否早失败 | 原因 | 扩展前应有的验证 |
|---|---|---|---|
| `stats.json` 缺失 | 是 | loader assert | 数据发布检查中生成并读取 stats |
| action horizon 超过 40 | 是 | Processor horizon 检查 | 训练前单独实例化 Processor |
| episode 尾部缺少完整动作窗 | 是 / 被排除 | 有效长度和索引边界 | 报告有效 step 数和尾部丢弃比例 |
| 视频缺失、帧数与 telemetry 不一致 | 转换阶段通常是 | converter 扫描 | 转换后逐 episode 抽样复核 |
| 13D 内部顺序或单位错误 | 否，静默 | shape/stats 仍可能合法 | 分组范围图、与 telemetry 抽样比对 |
| action 与 observation 存在控制延迟 | 否，静默 | 代码只按行号对齐 | timestamp 与控制日志回放 |
| 将 `sampling_rate=0.1` 误作只用 10% 数据 | 否，解释错误 | 实现仍覆盖全部 step | 改配置后打印 shard 覆盖总量 |
| 将 `use_relative_action=true` 误作已转相对 | 否，配置语义错误 | group 仍是 ABSOLUTE | 联查 ActionConfig、relative stats、decode |
| 部署混用权重与另一个 processor/stats | 常否 | tensor shape 可兼容但语义不兼容 | 总从同一 checkpoint 的 `processor/` 加载 |
| 触觉仅写入 parquet，未定义时间窗、stats、Processor/模型条件路径 | 部分是 | loader 可读不代表模型会消费 | 先定义触觉 representation、同步、mask 和 token/projector 接口 |

本章证明的是当前输入链路已可追踪，并不证明数据质量已足够支撑可靠 pouring 或真机闭环。尚未被证明的包括 telemetry 的物理时序、相机标定和遮挡质量、数据覆盖度，以及新增触觉的同步方式。这些分别进入多模体接口、评估和扩展设计章节。

---

## 参考证据索引（第 4 章）

| 编号 | 本地证据 | 用途 |
|---|---|---|
| E13 | `convert_to_lerobot_right_o6.py:74-221` | telemetry/video 扫描、13D 提取、metadata/parquet/video 写入 |
| E14 | `gr00t/data/dataset/lerobot_episode_loader.py:144-203, 305-398, 400-448, 500-563` | metadata、数值拆分、视频、stats、task |
| E15 | `gr00t/data/dataset/sharded_single_step_dataset.py:27-303` | step、有效长度、shard 构造与加载 |
| E16 | `gr00t/data/dataset/sharded_mixture_dataset.py:261-485` | stats 合并、schedule、分布式过滤、预加载 |
| E17 | `gr00t/data/stats.py:137-180, 251-291, 415-435` | 基础/relative stats 与 fingerprint |
| E18 | `gr00t/data/state_action/state_action_processor.py:112-526` | state/action 正反归一化与 relative 条件 |
| E19 | `gr00t/model/gr00t_n1d7/processing_gr00t_n1d7.py:130-208, 581-755, 811-892` | horizon、collator、Processor、保存/重载 |
| E20 | `gr00t_n1/examples/linkerhand_right_o6_config.py`；输出 `processor/{processor_config,statistics,embodiment_id}.json` | 13D config 与实际保存的 Processor 开关 |
| E21 | 当前 dataset `meta/*`、episode 0 parquet/video；2026-07-23 最小只读加载 | 真实 schema、45,030 step、44 shard、实际 batch shapes |

---

## 5. 多模体适配系统：把“不同机器人”约束为可验证的契约

### 5.1 适配的核心不是 tag 名称，而是四层共同契约

GR00T 对多 embodiment 的处理不等于为每种机器人训练一套独立模型，也不等于仅用一个字符串 tag 区分数据。其实际适配链由四层共同构成：`EmbodimentTag` 给出可识别名称和使用阶段；modality config 声明每个模态的键、时间窗口及动作表示；Processor 根据该契约完成组装、归一化、padding 和 mask；action head 根据 `embodiment_id` 选择 category-specific 参数。缺少任意一层都不能构成有效的“新机器人接入”。

```text
EmbodimentTag.NEW_EMBODIMENT = "new_embodiment"
        ↓ 动态 import 后注册
{video, state, action, language} modality config
        ↓ loader / Processor 解释 key、delta、stats、representation
state/action padded tensors + action_mask + embodiment_id=10
        ↓ action head 的 category-specific encoder / decoder
共享 VLM + 共享 DiT 条件下的本具身动作预测
```

| 层次 | 源码对象 | 负责回答的问题 | 当前 13D 落点 |
|---|---|---|---|
| 名称与阶段 | `EmbodimentTag`、`PRETRAIN_TAGS`、`POSTTRAIN_TAGS`、`FINETUNE_ONLY_TAGS` | 该 tag 能否直接被基础 checkpoint 使用，还是必须微调？ | `NEW_EMBODIMENT` 属于 finetuning-only |
| 数据时间语义 | `ModalityConfig` / `ActionConfig` | 读取哪些 key、哪些时刻；action 是 absolute、relative 还是 EEF？ | 3 RGB、13D state、16-step absolute joint/hand action |
| 数值接口 | `Gr00tN1d7Processor` / `StateActionProcessor` | 每组如何归一化、拼接、padding、反解码？ | 13D → 132D；16 → 40；mask=16×13 |
| 参数选择 | `embodiment_id` 与 `CategorySpecific*` | 哪些 state/action 投影参数由该 embodiment 使用？ | tag 映射为 index 10 |

该设计的优点是把“机器人差异”大部分留在数据、Processor 和动作投影边界，使 VLM backbone 与 DiT 主体可以共享。其限制也必须明确：共享并不表示不同机器人动作语义天然可比较；如果单位、关节顺序、坐标系或 action representation 失配，系统仍能产生形状正确但物理错误的输入。

### 5.2 tag 的生命周期与 checkpoint 约束

`EmbodimentTag` 在源码中显式区分三类：基础 checkpoint 内已支持的 pretrain tags；需要特定微调 checkpoint 的 posttrain tags；用于新机器人接入的 finetuning-only tags（`gr00t/data/embodiment_tags.py:24-259`）。这不是文档层分类。`Gr00tPolicy.__init__()` 从 checkpoint Processor 的 modality configs 中检查 tag；不存在时直接抛错，并针对 posttrain/finetuning tag 给出不同提示（`gr00t/policy/gr00t_policy.py:110-166`）。

| tag 类别 | 代表含义 | Policy 对基础 checkpoint 的行为 | 当前项目的正确使用方式 |
|---|---|---|---|
| pretrain | base checkpoint 已保存该机器人契约及对应统计/投影槽位 | 可在输入满足契约时直接加载 | 不适用当前 ROKAE/O6 |
| posttrain | 仓库支持但需要相应后训练产物 | base model 缺该 tag 时显式拒绝 | 不适用当前实例 |
| finetuning-only | 新机器人接入占位 | base model 上应拒绝；微调 checkpoint 保存配置后可加载 | `NEW_EMBODIMENT` 经过本次微调后可由输出 checkpoint 使用 |

本次保存的 `processor/embodiment_id.json` 将 `new_embodiment` 映射为 **10**。该整数不是机器人硬件 ID，也不是动作维数；它是 action head 中 category-specific 参数表的索引。Processor 在每个 sample 写入该值，collator 将其成为 `(B,)` tensor；模型使用该 tensor 选择 state encoder、action encoder 和 action decoder 中对应类别的权重（`processing_gr00t_n1d7.py:63-101, 292-296, 701-807`；`embodiment_conditioned_mlp.py:60-207`）。

每次 inference 或 finetune 都必须提供 `--embodiment-tag`；tag 决定采用的 modality config（state/action keys 与 normalization），且不区分大小写。源码进一步揭示这一接口背后的 processor id/projector 实现。因此，CLI 约束解释了“为什么必须有 tag”，而源码与 checkpoint 才能证明“当前 tag 映射到哪个 index、用了哪套参数”。

必须避免随意复用 index。源码的 `_PROJECTOR_INDEX_GROUPS` 只允许刻意确认“同一物理 embodiment”的 tag 共享 index，例如数据源或子任务变体；注释明确要求全新 embodiment 使用未占用 index（`processing_gr00t_n1d7.py:57-101`）。当前 `new_embodiment` 与两个 RoboCasa tag 共用 10 是仓库为 finetune placeholder 定义的兼容行为，不能据此推论任意新机器人都应复用 10。若一个新机器人与当前 ROKAE/O6 的 state/action 语义不同，复用该 index 会让它共享同一组输入输出投影参数，属于需要明确架构决策的高风险选择。

### 5.3 modality config 是多模体的可执行 schema

`ModalityConfig` 定义 `delta_indices`、`modality_keys` 和可选的表示设置；`ActionConfig` 再定义每个 action group 的 representation、类型、格式和相对化所依赖的 state key。`__post_init__()` 要求 action config 数量与 action key 数量相等，因而可防止一部分简单的组级错配（`gr00t/data/types.py:25-120`）。配置在 `launch_finetune.py` 动态 import 后进入全局 `MODALITY_CONFIGS`，`Config.validate()` 会剔除未被本次 dataset 使用的 config，并为缺失 action configs 补默认 absolute/non-EEF/default（`base_config.py:169-210`）。

当前 13D schema 可以作为阅读其他 embodiment config 的基准：

| modality | keys | 时间索引 | 特有语义 | 影响的下游层 |
|---|---|---|---|---|
| video | `cam_top`、`cam_left_wrist`、`cam_right_wrist` | `[0]` | 三路当前 RGB | image transform、Qwen 图像 token |
| state | `right_arm`、`right_o6_hand` | `[0]` | 7D rad + 6D `[0,100]`，最终未启用 sin/cos | state stats、state encoder |
| action | 同两组 | `[0..15]` | 两组均 ABSOLUTE / NON_EEF / DEFAULT | action stats、decode、mask、action encoder/decoder |
| language | `task` | `[0]` | 轨迹级 `pouring` 文本 | Qwen chat template |

这张 schema 同时说明新增“数值触觉”与新增“触觉图像”不是同一修改。数值触觉若作为 state group，会受 state 时间窗、统计量、132D state 宽度和 state encoder 约束；若作为独立的新 modality，当前 loader/Processor 只原生处理 `video/state/action/language/mask`，需要定义额外消费通路。触觉图像可在工程上复用 video 键的图像变换和 VLM token 化，但是否应与 RGB 相机同等对待，需要根据分辨率、帧率、接触图案和预训练分布另行验证。

### 5.4 category-specific projector 与 mask 的模型边界

多 embodiment 的数值适配真正发生在 action head 的三个 category-specific 模块：`state_encoder`（state→token）、`MultiEmbodimentActionEncoder`（noised action→token）和 `action_decoder`（DiT hidden→action velocity）。`CategorySpecificLinear` 保存形状为 `[num_categories,input_dim,hidden_dim]` 的独立权重表，并按 batch 内 `cat_ids` 选择权重后执行 batch matrix multiply（`embodiment_conditioned_mlp.py:60-171`）。因此，同一 batch 中不同 tag 可以共享 DiT/VLM，但其 state/action 输入输出投影由各自 index 决定。

```
state (B,1,132) ── category-specific MLP[id] ──► state token
noised action (B,40,132) ── category-specific encoder[id] ──► 40 action tokens
state token + action tokens ── DiT / VLM cross-attention ──► hidden tokens
hidden action tokens ── category-specific decoder[id] ──► velocity (B,40,132)
                                          │
                                          └─ action_mask 仅让 16×13 区域参与本项目 loss
```

这里有两个独立机制，不能混为一谈。**projector index** 决定参数选择；**padding/mask** 决定哪些数值位置在某个样本中真实存在并参与 loss。13D/16-step 能放入 132D/40-step 统一张量，依赖的是 mask；模型能知道该样本应使用哪个动作投影参数，依赖的是 embodiment id。只增加 padding 宽度或只换 tag 都不能完成新机器人适配。

当前 max state/action dim=132、max embodiments=32 是 checkpoint 结构上限（`configs/model/gr00t_n1d7.py:48-112`；最终 `final_model_config.json`）。超过 132 维的数值状态或动作不能仅靠 config 解决；超过既有 projector category 的新 embodiment 也不能只修改 JSON 映射，因为 category-specific 参数表自身需要结构扩展、权重初始化和 checkpoint 兼容性方案。这些属于第 10 章的 C 级架构变更，不应在临时数据脚本中悄然完成。

### 5.5 本章结论：触觉接入前必须先确定“它是什么”

对于扩展，第一问题不是“怎样把触觉数组放进数据集”，而是“触觉在策略条件中扮演何种信息角色”。表 14 给出当前代码边界下的初步分类；这是待后续实验验证的工程建议，不是声称已有触觉支持。

| 触觉形态 | 最可能接入层 | 可复用部分 | 仍需新增或验证的部分 |
|---|---|---|---|
| 低维力/力矩、接触开关、关节电流 | state group 或专门数值 token | stats、时间窗口、state group 拼接 | 单位/坐标系、采样同步、132D 预算、是否需要独立 projector |
| 高分辨率触觉阵列 / tactile image | video-like view 或专门视觉 encoder | 图像增强、Qwen visual token 管线在形状上可复用 | 与 RGB 共用视觉 encoder 是否有意义；域差异、分辨率、标定、token budget |
| 高频触觉序列 | 新的 temporal modality | 数据版本、timestamp、mask 思路 | 当前 Processor 没有通用非视觉时序 encoder；必须设计下采样/聚合/专用 encoder 与融合点 |
| 接触事件、滑移标签 | state、language-like condition 或 auxiliary target | 数据契约、stats/mask | 是作为输入条件、训练辅助监督还是控制安全信号，需要先澄清业务语义 |

---

## 6. 模型系统：视觉语言条件下的 flow-matching DiT 动作生成

### 6.1 模型装配与张量职责

`Gr00tN1d7` 由两个主部件组成：`Qwen3Backbone` 输出视觉—语言条件 token；`Gr00tN1d7ActionHead` 以当前 state 和候选动作轨迹为 query token，经过 DiT 预测动作速度（`gr00t_n1d7.py:518-632`）。训练和推理共享 `prepare_input()`、backbone、state encoder、action encoder、DiT 和 decoder；差异仅在动作轨迹的来源和输出：训练从真实 action 与随机 noise 构造插值轨迹并计算 velocity loss，推理从纯 noise（可选 RTC overlap）经多步 Euler 积分生成 action chunk。

| 部件 | 主要输入 | 主要输出 | 当前 checkpoint 可确认配置 |
|---|---|---|---|
| Qwen3 backbone | `input_ids`、attention mask、`pixel_values`、`image_grid_thw` | `backbone_features`、image/text masks | 本地 Cosmos/Qwen3-VL；保留 language model 前 16 层后取最后 hidden state；embedding dim 2048 |
| state encoder | `(B,1,132)`、embodiment id | 一个 state token，dim 1536 | category-specific MLP |
| action encoder | `(B,40,132)` 候选/noised action、time、id | 40 个 action token，dim 1536 | category-specific encoder + time encoding |
| DiT / AlternateVLDiT | 1+40 个 state-action token，VLM condition token | 同长度 hidden token | 32 层、32 heads × 48 = 1536，AdaLN，交替 self/cross attention |
| action decoder | action token 部分 hidden、id | `(B,40,132)` velocity 或预测 action | category-specific MLP |

这里的 `132` 与 `40` 是统一张量上限，不是当前机器人固有自由度或控制 horizon。当前 13D/16-step 的真实区域通过 Processor mask 限定；模型结构仍按 checkpoint 的 132D/40-step 尺寸创建。

### 6.2 条件信息如何进入 DiT：query、key/value 与注意力方向

在当前标准 DiT 中，state token 和 action tokens 组成 `hidden_states`；VLM backbone tokens 作为 `encoder_hidden_states` 传入 Diffusers `Attention`（`gr00t_n1d7.py:244-270`；`modules/dit.py:107-215, 282-328`）。所以 action-side token 产生 **Query**，视觉—语言 token 产生 **Key/Value**：每个动作时刻的问题可理解为“在当前机器人状态和这条候选动作轨迹下，应从图像/语言证据中读取哪些信息来修正速度”。

这不是“一个 query 只查一个 key”。注意力计算会令每个 query 对所有可见 key 产生权重，再对所有 value 加权求和。若 `q_i` 是第 i 个 action/state token 的投影，`k_j,v_j` 是第 j 个视觉/语言 token 的投影，则输出近似为：

```text
weight(i,j) = softmax_j(q_i · k_j / sqrt(d))
attention_output(i) = Σ_j weight(i,j) · v_j
```

当前 DiT 的普通 cross-attention 没有 causal mask：动作轨迹 token 可以利用完整 VLM context；它不是语言生成器，因而不存在“前面 token 不能看后面 token”的自回归限制。若启用 `interleave_self_attention`，奇数 block 只在 state/action token 内自注意力，其他 block 用 cross-attention 查询 VLM token。checkpoint 配置启用 `use_alternate_vl_dit=true`，其 `AlternateVLDiT` 还会让 cross-attention block 在 image tokens 与 non-image（文本）tokens 之间交替选择可见集合，而 self-attention block 仍让 state/action tokens 彼此交互（`modules/dit.py:339-410`）。

因此，选择谁当 Query 的工程准则是：**谁需要被更新，谁就是 Query；谁提供条件记忆，谁就是 Key/Value。** 当前目标是更新动作轨迹，故动作/状态作为 Query、图像语言作为 K/V。未来若设计触觉 token 融合，至少有三种不同架构语义：将触觉并入 K/V 作为动作生成的条件；将触觉变为与 action/state 同序列的 Query token；或先用独立 encoder 将触觉压缩再交给 cross-attention。三者不是可互换的“拼接方式”，会改变信息流、计算量和训练需求。

### 6.3 Flow matching 训练目标：预测速度而非直接回归 action

训练期 `Gr00tN1d7ActionHead.forward()` 对真实归一化动作 `a` 采样 Gaussian noise `ε` 和标量时间 `t`，构造线性插值轨迹：

```text
x_t = (1 - t) ε + t a
v_target = a - ε
```

模型输入是 `x_t`、离散化后的 `t`、state 以及 VLM condition，输出 `pred_velocity`；loss 为 masked MSE：

```text
loss = Σ [ action_mask ⊙ (pred_velocity - (a - ε))² ] / (Σ action_mask + 1e-6)
```

对应代码在 `gr00t_n1d7.py:227-281`。`sample_time()` 从 Beta(1.5,1.0) 采样并乘 `noise_s=0.999`，随后映射到 1,000 个 time bucket（`gr00t_n1d7.py:171-176`；最终模型配置）。这证明模型学习的是从 noise distribution 指向 data distribution 的局部速度场；它并不是一次性直接最小化“预测 action 与标签 action 的 MSE”。

对于 13D 实例，`action_mask` 令每个训练样本只有前 16×13 个位置贡献该 velocity loss。40×132 其余位置虽经过模型计算，却没有本项目监督。这是统一多 embodiment 形状的代价，也是一个需要监控的效率边界：如果真实维度/时域远小于模型上限，训练计算中存在大量 padding token。

### 6.4 Flow matching 推理：从随机轨迹到 action chunk 的 Euler 积分

推理期 `get_action_with_features()` 先采样 `(B,40,132)` Gaussian noise，然后执行 `num_inference_timesteps=4` 次循环。每次以当前候选轨迹编码 action token，通过相同 DiT 预测速度，并按 Euler 更新：

```text
x ← x + (1 / N) · v_θ(x, t, condition)
```

最后得到的是归一化的 40×132 action 预测，Processor 再只取本 embodiment 的 action groups、配置的 action horizon，并反归一化（`gr00t_n1d7.py:327-445`；`processing_gr00t_n1d7.py:382-404`）。当前 13D Processor 的 action config horizon 是 16，因此对外 decode 的有效 action chunk 是 16×13，尽管模型内部每次仍生成 40×132。

模型还支持 RTC（receding/real-time control）式重规划：若提供上一次 action chunk，前段可用旧预测初始化，并通过 `vel_strength` 冻结或平滑 overlap 部分；这一逻辑位于同一推理函数（`gr00t_n1d7.py:351-397`）。它是动作块连续性的机制，不是底层安全控制器，也不自动处理关节限位或碰撞。

### 6.5 冻结、微调与本项目的实际模型配置

backbone 的 language/visual 分支是否训练由 `tune_llm`、`tune_visual` 和 `tune_top_llm_layers` 控制；action head 的 projector、DiT、VLLN 分别由 `tune_projector`、`tune_diffusion_model`、`tune_vlln` 控制。被冻结模块会在 Trainer 调用 `model.train()` 后被重新置为 eval，以避免 dropout 等训练行为改变冻结 backbone 的推理语义（`qwen3_backbone.py:145-177`；`gr00t_n1d7.py:122-170`）。

本项目保存的 `final_model_config.json` 显示：Qwen backbone `tune_llm=false`、`tune_visual=false`、`tune_top_llm_layers=0`；action projector、DiT、VLLN 均为 true；AlternateVLDiT 为 true，32 个 DiT layer，4 个推理时间步，state dropout=0。由此可下的结论是：本次微调主要更新动作侧模块，而非更新整个视觉语言 backbone。它不能证明视觉特征一定适合 pouring，也不能证明冻结 VLM 对触觉扩展仍合适；恰恰相反，触觉若不能自然投影到既有 VLM token 空间，冻结策略需要重新评估。

模型 dataclass 默认 `state_dropout_prob=0.8`，fine-tune CLI 默认 0.2，benchmark 脚本可按任务覆盖；其目的是降低对 proprioceptive state 的依赖，状态强相关任务应调低该值（`configs/model/gr00t_n1d7.py:118`；`configs/finetune_config.py:61`）。当前项目取 0.0 是面向 13D 状态强相关倒水任务的显式配置选择，不应被误称为 N1.7 默认或 benchmark 标准。上游还提示非确定图像增强可能造成 5–6% run-to-run variance；当前项目没有以多 seed 复现实测，不能将其当作本项目误差条。

---

## 7. 训练系统：配置、可恢复状态与 loss 的工程闭环

### 7.1 从配置到 Trainer 的运行责任

训练运行由 `experiment.run()` 编排，而不是由 shell 直接调用模型。它依次检查 batch/world-size 和恢复兼容性，设置随机种子并校验 config，保存运行配置，创建 pipeline 的 model/dataset/collator/processor，保存部署所需 Processor，构造 Hugging Face `TrainingArguments` 和 `Gr00tTrainer`，最后训练并保存最终模型（`experiment.py:39-385`）。

| 阶段 | 主要代码 | 输入 | 输出或防线 |
|---|---|---|---|
| 启动校验 | `warn_configs()`、`Config.validate()` | GPU/world size、batch、modality config | world size 不一致、dataset tag 未注册等早失败 |
| 可复现实验工件 | `save_run_config_artifacts()` | 统一 Config | `experiment_cfg/config.yaml`、`conf.yaml`、W&B config |
| 装配 | `Gr00tN1d7Pipeline.setup()` | base checkpoint、model/data config | model、Processor、sharded dataset、collator |
| 保存部署语义 | `processor.save_pretrained()` | Processor 中的 config/stats/id map | `processor/`，Policy 推理的必需工件 |
| 优化循环 | HF `TrainingArguments` + `Gr00tTrainer` | batch、loss、optimizer/scheduler | model checkpoints、optimizer/scheduler/RNG/trainer state |
| 收尾 | `trainer.save_model()` | 最终 in-memory model | 顶层权重与 config |

`DatasetFactory` 在构建训练数据前由 rank 0 生成基础/relative stats，然后建立 `ShardedSingleStepDataset` 和 `ShardedMixtureDataset`；它明确断言 `eval_strategy == "no"`，因为这种 sharded iterable path 不支持 HF eval set（`data/dataset/factory.py:24-108`）。所以训练系统内部的“eval”不能被默认想象成每 N step 的验证集 loss。

### 7.2 本项目已保存的训练事实

保存的 `experiment_cfg/config.yaml` 和 `checkpoint-30000/trainer_state.json` 允许把本次训练描述为可复核事实，而不仅是口头“跑通”。

| 项目 | 已保存值 | 工程解释 |
|---|---:|---|
| 起始 checkpoint | `/mnt/data/gr00t-finetune/models/gr00t_n1_base` | 不是从随机初始化训练 |
| 最大/最终 global step | 30,000 / 30,000 | 已达到配置的终止 step |
| global batch | 1 | 每次 forward 的全局样本数为 1（单 GPU） |
| gradient accumulation | 8 | 每 8 次 forward 才进行一次 optimizer step；配置语义上的 accumulated batch 为 8 |
| precision | bf16=true、tf32=true、fp16=false | 模型训练数值与硬件路径条件的一部分 |
| optimizer | `paged_adamw_8bit` | 依赖 bitsandbytes 的内存优化实现 |
| learning rate | `5e-5`，constant | 保存的训练配置口径；warmup_steps=1500 仍需以 HF scheduler 实际行为核对 |
| checkpoint cadence | 每 5,600 step；保留 3 个 | 当前可见 22,400、28,000、30,000 checkpoint |
| eval strategy | `no` | 本次训练未运行 HF eval dataset loop |
| 最末三条记录 loss | 0.0495、0.0511、0.0385 | 仅是训练 batch 的 flow-matching masked loss，不是成功率 |

trainer state 中 `num_train_epochs=9223372036854775807` 不代表真的训练了如此多 epoch，而是 iterable/sharded dataset 下 epoch 不是有意义的“完整遍历一次数据”的度量。因此，本项目应使用 global step、样本/优化步、shard schedule 和明确数据版本描述训练预算，不能仅报告“训练了多少 epoch”。

### 7.3 checkpoint：部署、继续训练与审计的工件不同

当前输出目录同时包含顶层最终模型和可恢复 checkpoint。checkpoint 目录中可见权重 shards、`config.json`、`trainer_state.json`、`optimizer.pt`、`scheduler.pt`、`rng_state.pth`、Processor config/statistics/id map 等；这使其可以用于恢复优化状态。顶层目录保存最终模型权重、模型 config、`processor/` 和 `experiment_cfg/`，用于部署和追溯。`save_only_model=false` 是可恢复训练的前提；`check_resume_compatibility()` 明确拒绝 `save_only_model=true` 与 `resume_from_checkpoint=true` 的组合，避免悄然重置 optimizer/scheduler（`training_config.py:25-168`）。

这里应坚持“checkpoint 不是只有 `.safetensors`”。若只复制权重而遗漏同次训练生成的 Processor、statistics、embodiment mapping 或 model config，Policy 可能无法加载，或更危险地以错误归一化解释动作。对外发布/部署应将模型权重、`config.json`、`processor/`、训练 config、数据版本和 commit 一并作为最小可审计包。

### 7.4 恢复与分布式的边界

恢复训练时 `Gr00tTrainer` 预先读取 `trainer_state.json`，并按 `dataset.seed + global_step` 重置 dataset seed；源码特别要求所有 rank 使用同一 seed，否则 shard schedule 的 rank 分区会导致重复或漏样本（`trainer.py:176-252`）。训练入口还检查 config `num_gpus` 与 launcher `WORLD_SIZE` 一致，避免有效 batch 被静默放大（`experiment.py:42-63`）。

这对当前单 GPU 不构成运行障碍，但对将来的多 GPU 训练和触觉高吞吐数据尤其重要。跨 rank 可复现性、视频/触觉解码 worker 的启动方式、随机图像增强与 checkpoint resume 的一致性，应在扩展前作为专项验证，而不是假设单卡结果可自动外推。

### 7.5 loss 的解释边界与当前配置漂移

模型的实际 loss 已在第 6 章定位为 masked velocity MSE。`Gr00tTrainer.compute_loss()` 对本类连续动作模型主要委托父类获取 `outputs["loss"]`；文件中的 token-level accuracy 分支只有 input 中存在 `labels` 时才会触发，当前 Processor batch 使用 `action/action_mask`，不应将这段通用 token accuracy 逻辑误称为本项目动作准确率（`trainer.py:254-340`）。

还发现一个需保留的工件口径差异：顶层训练 `config.yaml` / 保存的 Processor 显示 `use_relative_action: true`，而 `final_model_config.json` 显示 `use_relative_action: false`。当前 relative conversion 的运行时消费者是 Processor；其保存配置为 true，但两个 action group 都是 ABSOLUTE，所以本次实际仍不转换。`final_model_config.json` 中该字段不被 action head 的 `forward()` / `get_action()` 消费，因而这不是已证实的本次数据路径错误；但它说明不能把任意同名字段都当作同一层的运行事实。未来引入 RELATIVE action 时，应以保存 Processor config、ActionConfig、relative stats 和 decode 回归测试共同判定行为，并在训练前后做 config diff。

---

## 8. 推理与评估系统：模型输出不是机器人执行结果

### 8.1 Policy 是模型与控制器之间的类型化边界

`Gr00tPolicy` 的职责是加载同一 checkpoint 的 model 和 Processor，检查实时 observation，转为 `VLAStepData`，调用 Processor/collator/model，然后 decode 为分组的物理单位 action（`policy/gr00t_policy.py:70-482`）。它不管理相机驱动、机器人通信、动作限幅、碰撞检测、轨迹插补或急停；这些属于 Policy 外的机器人系统。

| Policy 阶段 | 接口契约 | 主要失败方式 | 输出 |
|---|---|---|---|
| load | checkpoint model + `processor/` + requested tag | checkpoint 不含该 tag，直接报错 | `self.model`、`self.processor`、modality configs |
| observation validation | video `(B,T,H,W,3) uint8`；state `(B,T,D) float32`；语言 list 结构 | key、dtype、time horizon、通道数不匹配 | 仅接受符合 config 的实时观测 |
| processing | 每个 batch item 构建 `VLAStepData` | 缺 state/video/language group 或 Processor schema 不匹配 | processed sample |
| inference | collate 后 `model.get_action()`，bf16 inference mode | 模型/显存/后端异常 | normalized action trajectory |
| decode | `decode_action(..., current state)` | stats/representation 不匹配 | `{right_arm:(B,T,7), right_o6_hand:(B,T,6)}` float32 |

对当前 13D deployment，输入三路图像必须是 `uint8` 的 `(B,1,H,W,3)`，两个 state group 必须是 `float32` 的 `(B,1,7)` 和 `(B,1,6)`，语言为包含 `task` 的嵌套 list。Policy 对 shape/dtype 有严格检查，但不检查关节值是否在机器人安全范围内；“通过 Policy 验证”不能等价为“可安全下发”。

### 8.2 预测 horizon、execution horizon 与控制重规划

必须区分三种时间尺度：模型内部最大 action horizon（本 checkpoint 为 40）；当前 embodiment decode 的动作窗口（16）；外部控制器每次执行后重新观测/推理的 execution horizon。`PolicyHorizonSpec` 从 policy modality config 读取实际 action delta，并要求它是从 0 开始的连续窗口；`n_action_steps` 必须位于 `[1, action_horizon]`（`eval/_horizon_contract.py:56-159`）。

```text
一次 Policy 推理
  输入：t 时刻观测
  输出：预测 [a_t, a_(t+1), ..., a_(t+15)]  （当前 13D 对外有效 16 步）
                    │
                    ├─ execution_horizon = 16：整块开环执行后重规划
                    └─ execution_horizon < 16：执行前缀后重新观测、滚动重规划
```

短 execution horizon 通常降低因环境扰动、视觉滞后或动作误差造成的开环漂移，但提高推理频率和系统时延压力；长 horizon 相反。它是控制系统的策略选择，不应与训练 action horizon 或模型 40-step padding 混称。RTC overlap 还可以使相邻预测块平滑衔接，但它仍不是硬件安全机制。

### 8.3 open-loop 评估真正测量什么

`open_loop_eval.py` 读取离线 demonstration，从每个 execution horizon 的起点取真实 state/image/language，调用 policy，取预测 chunk 的前缀，与数据记录的 ground-truth action 在未归一化物理空间计算 MSE/MAE，并画每个动作维度的轨迹（`eval/open_loop_eval.py:104-234`）。这能回答：在**专家轨迹分布上的观测**条件下，模型输出是否贴近专家动作。

它不能回答：预测动作执行后会不会到达相同状态；接触、摩擦、延迟和安全限幅下是否成功；机器人是否会在策略离开 demonstration 分布后恢复。因此 open-loop MSE/MAE 是诊断指标，不是闭环成功率，也不是实际任务完成率。

当前训练 config 为 `eval_strategy: 'no'`、`enable_open_loop_eval: false`，DatasetFactory 也不支持 HF eval dataset；这表示 Trainer 训练循环不会自动执行评估，并不禁止训练后的独立评估。`checkpoint-30000` 已使用 `open_loop_eval.py` 在训练集轨迹 0–3 各运行 400 step（`execution_horizon=16`、4 次去噪），MSE 为 13.73、18.50、29.87、22.50，平均 23.62；MAE 平均 1.15（`.project-log/verification/evidence.yaml#verification-013`）。这证明 checkpoint 在**已见 demonstration 分布**上的 open-loop 动作预测已取得可用证据；仍未证明未见 episode 泛化、仿真闭环或真机闭环。训练 loss 也不能替代这些后续层级的证据。

评估路径可以分为三层：open-loop 将预测动作与 ground truth 比较并绘制 MSE；closed-loop 通过 policy server 与 `PolicyClient` 连接仿真或真实环境；`ReplayPolicy` 可在没有训练模型时回放 dataset action，以隔离环境/通信适配问题。这为本项目后续验证提供了递进路线：先在固定未见 episode 上做 open-loop，再用 replay 检查 adapter 和环境动作契约，最后做受安全约束的闭环 rollout。接口约定与推荐流程不能替代每层的实际结果。

### 8.4 仿真、服务端和真实机器人接口

仓库还提供 `Gr00tSimPolicyWrapper`，用于将仿真环境的扁平键转为 `Gr00tPolicy` 所需嵌套 observation；`rollout_policy.py` 用 `MultiStepWrapper` 将 policy-resolved horizon 绑定到 SimplerEnv、LIBERO、RoboCasa 等 gym 环境（`gr00t_policy.py:494-744`；`eval/rollout_policy.py`）。此外可通过 server/client 运行策略。它们是**适配器**，不是通用物理真实性保证。

因此从本项目走向真机，至少还缺一层明确的 robot adapter：把 decoded `right_arm` 和 `right_o6_hand` 解释为哪个控制模式的命令、加入单位和范围检查、动作速率/加速度限制、通信超时与急停、执行多少预测步、何时重新取相机/state。这个适配层不应隐藏在数据转换或 Policy 内部；它应有独立接口与安全验证。

---

## 9. 本项目 13D 案例映射：一次训练如何贯通工程边界

### 9.1 可复核的端到端实例

表 15 将当前实例从数据到部署的具体文件固定下来。它不是报告的主线，而是验证前述抽象边界确实被实际训练工件使用的锚点。

| 工程边界 | 13D 对应物 | 已确认的输入/输出 | 证据状态 |
|---|---|---|---|
| 原始采集 | `telemetry.npz` + 三路 MP4 | qpos/actions 与相机帧数对齐后进入转换 | converter 代码和产物已查；控制时延未证实 |
| 数据转换 | `convert_to_lerobot_right_o6.py` | 7D ROKAE + 6D O6（O6 ×100/255）→ `[T,13]` | 代码/metadata 已证实 |
| LeRobot 数据 | `lerobot_dataset_right_o6_13d` | 148 episode、47,250 frame、444 MP4、task=`pouring` | 真实 metadata/parquet 已证实 |
| embodiment schema | `examples/linkerhand_right_o6_config.py` | 3 view、state 13D、absolute action 13D、action delta 0..15 | 代码与保存 Processor 已证实 |
| dataset/Processor | `Sharded*Dataset`、`Gr00tN1d7Processor` | 45,030 step → 44 shard；单样本 pad 到 state `(1,132)`、action `(40,132)` | 静态代码和最小实测已证实 |
| 模型 | `Gr00tN1d7` | 冻结 Qwen VLM，训练动作 projector/DiT/VLLN；masked velocity loss | final model config / 代码已证实 |
| 训练 | 输出目录 `...full_20k` | 30,000 global step；bf16；batch 1 × accumulate 8 | config/trainer state 已证实 |
| 推理/执行 | `Gr00tPolicy` + 尚未固化的 robot adapter | 输出分组 action chunk；训练集轨迹 0–3 的 open-loop 平均 MSE 23.62、MAE 1.15 | Policy/open-loop 已证实；未见泛化、真机 adapter/闭环待完成 |

### 9.2 对当前训练结果应作出的最窄结论

本次工作已证明的最窄结论是：当前数据、config、base checkpoint、Processor、action head 和 Trainer 之间的接口可以一致地运行至 30,000 step，并保留了可供重载的 model/Processor/checkpoint 工件；`checkpoint-30000` 已在 4 条**训练集**轨迹的独立 open-loop 中取得平均 MSE 23.62、MAE 1.15，且优于此前 20k checkpoint 与 current-state 基线。训练末尾的 batch flow-matching loss只说明训练目标在样本分布上的优化过程；上述 open-loop 也仍不能直接证明 pouring 的闭环成功率、对未见场景的泛化、动作安全性或触觉扩展有效性。

| 主张 | 当前状态 | 需要的下一份证据 |
|---|---|---|
| 13D 数据接口可训练 | 已证实 | 独立重载/固定样本 forward 回归测试 |
| 模型能在已见离线专家观测预测合理动作 | 范围有限地已证实 | 4 条训练集轨迹：MSE/MAE、轨迹图、20k/current-state 基线对比 |
| 模型能在未见离线轨迹泛化 | 待验证 | 固定未见 episode split 的 MSE/MAE、轨迹可视化和随机种子方差 |
| 模型可完成真实 pouring | 待验证 | 闭环成功率、失败类型、时延与安全日志 |
| 加入触觉可提升性能 | 未研究 | 消融设计、同步数据、相同评测协议 |

### 9.3 当前工程中需要单独审计的本地改动

`gr00t_n1` 工作树不是纯上游基线：`gr00t/configs/finetune_config.py`、`gr00t/experiment/launch_finetune.py`、`gr00t/model/gr00t_n1d7/gr00t_n1d7.py` 有修改，且新增 `examples/linkerhand_right_o6_config.py`、checkpoint 等本地工件。它们可能是使训练运行所必需的兼容修复，也可能引入与上游行为不同的长期维护负担。本草稿没有将其自动判定为缺陷或原生机制。

下一轮白盒化应以 diff 为单位建立“上游基线—本地变更—解决的问题—验证证据—是否应保留”的表，而不是将本地修补混入 GR00T 原始架构叙述。这是后续扩展前必须完成的工程治理工作。

---

## 10. 可扩展性分析：以触觉为例的接入决策和验证路线

### 10.1 扩展不是单点修改，而是跨五层一致变更

任意新模态都必须沿同一条可追踪链路定义：采集与同步 → LeRobot schema → modality/Processor representation → 模型融合点 → 训练/推理/评估。只在其中一层增加字段会产生两类失败：若 key 缺失或 shape 不兼容，系统早失败；若字段存在但未被 Processor 或模型消费，训练仍可运行却没有使用新信息。

| 层 | 新触觉接入需要明确的问题 | 当前可复用资产 | 必须新增的验证 |
|---|---|---|---|
| 采集 | 频率、timestamp、标定、缺失、接触时延、物理单位 | telemetry/video 对齐检查思路 | 触觉与 action/state 的因果时序审计 |
| 数据 schema | parquet 数值组还是图像/文件流；每帧/每步怎样存 | info/modality/stats/episode 元数据 | 数据版本、sample 可视化、NaN/饱和/丢帧统计 |
| Processor | 取哪些 delta；如何归一化、clip、mask、pad | StateActionProcessor、video transform、collator | 单 sample/batch shape、stats/反变换回归测试 |
| 模型 | 将其作为 state、VLM condition，还是新 temporal encoder | VLM cross-attention、state/action projector、DiT | 参数量、token budget、冻结策略、梯度流与消融 |
| 执行与评估 | 是否仅帮助策略，还是还参与安全控制 | Policy/open-loop/rollout 框架 | 接触任务闭环成功、安全、延迟、无触觉基线 |

### 10.2 三条可行路线及其取舍

| 路线 | 修改范围 | 适用条件 | 主要优点 | 主要风险 |
|---|---|---|---|---|
| A. 低维触觉并入 state | converter、metadata、modality config、stats；通常不改主干 | 力/力矩、压力统计、接触标志等维度较小、同步明确 | 最小改动，沿现有数值归一化和 state encoder | state token 被压成一个 token，可能损失高频时序/空间结构；占用 132D 预算 |
| B. 触觉图作为额外 video view | 数据、video key、Processor；可能不改 DiT | 触觉可表达为稳定的图像阵列，且帧率/尺寸可管理 | 重用 image transform、Qwen tokenization、cross-attention 结构 | Qwen 预训练面向自然 RGB，触觉图域差异大；增加视觉 token 与推理时延 |
| C. 专用 tactile encoder/token | data + Processor + 新 encoder + DiT 融合设计 | 高频/空间触觉，现有 A/B 无法保留信息 | 表达能力和时间建模可控 | 架构、checkpoint、训练预算和消融复杂；不再是低风险微调 |

建议的默认顺序是：先用 A 建立严格同步的低维触觉基线，确认额外信息在相同数据/评测协议下确有贡献；若信息确实依赖空间纹理，再评估 B；只有 A/B 明确受限时才进入 C。这样不是因为 A 一定最优，而是它能最小化同时变化的变量，避免把数据质量、融合架构、训练策略和控制器改动混在一次实验中。

### 10.3 可验证的最小扩展切片

若目标是“把触觉接入而不破坏现有 13D 基线”，建议将实施拆为四个可独立验收的纵向切片：

| 切片 | 完成条件 | 必须留下的证据 | 尚不宣称的内容 |
|---|---|---|---|
| 数据切片 | 带 timestamp 的触觉与既有 episode 可重放对齐；schema/stats 生成成功 | 样本图、同步误差统计、metadata diff、stats | 触觉已提高模型性能 |
| Processor 切片 | 一个 step 到 batch 形状、mask、数值范围符合预期；旧 13D path 回归通过 | 单元/最小加载结果、Processor config | 模型已理解触觉 |
| 融合切片 | 明确 token/projector 位置，forward/backward 可运行且参数变化可解释 | 模块图、trainable parameter diff、短跑 loss sanity check | 真机能成功 |
| 评测切片 | 无触觉/有触觉使用同一 episode split、同一控制频率、安全协议 | open-loop + 闭环指标、失败分类、视频日志 | 单次成功代表泛化 |

### 10.4 架构容量与版本兼容风险

当前上限给出明确约束：state/action 各 132D、模型 action horizon 40、projector categories 32、VLM token 长度受图像数/尺寸和 `max_seq_len` 影响。增加低维 state 若总宽度仍不超过 132，技术上可先利用 padding budget；超过该值则会触及 state encoder 的输入维度和 checkpoint 权重形状。增加视觉触觉 view 会直接增加 Qwen 图像 token 和 DiT cross-attention 开销，可能影响实时性。增加独立 encoder 还会改变 checkpoint schema、AutoModel 注册和导出路径。

因此，“可放进当前 tensor”不等于“可无代价扩展”。每次扩展都需要记录：数据 schema version、modality config version、Processor config/statistics、model config、checkpoint compatibility、推理延迟和控制安全策略。缺任一项，未来难以判断模型差异来自触觉本身还是来自处理/配置漂移。

---

## 11. 风险、未知与研究结论

### 11.1 证据状态总览

| 主题 | 当前结论 | 证据等级 | 未覆盖边界 |
|---|---|---|---|
| 代码仓责任与训练/推理主链 | 已从入口追到 model/Processor/Policy | 代码已证实 | 本地改动尚未逐 diff 审计 |
| 数据系统 | 13D LeRobot 到 batch 的 schema、窗口、stats、mask 已定位并部分实测 | 代码 + 真实工件已证实 | 物理控制时延、相机质量、数据覆盖度 |
| 多 embodiment | tag/config/id/projector/mask 的职责已定位 | 代码 + 保存 Processor 已证实 | 新 index 的权重初始化和迁移策略未设计 |
| 模型机制 | Qwen condition、DiT cross-attention、flow matching loss/采样已定位 | 代码 + final model config 已证实 | 每层实际 attention 行为、触觉最优融合方式 |
| 本次训练 | 到 30,000 step 的配置、工件、训练集 open-loop 已确认 | config/trainer state + `verification-013` 已证实 | 独立复现、未见泛化和闭环结果 |
| 评估 | open-loop/sim/Policy 路径已定位；4 条训练集轨迹 open-loop 已执行 | 代码 + 评估工件已证实 | 未见 episode、仿真和真机闭环 |
| 性能 | 官方 L40 条件和用户给出的 63.9 ms 已区分 | 官方/用户来源已区分 | 本项目三相机、13D、当前软件栈的端到端时延 |

### 11.2 需要优先处理的风险

| 优先级 | 风险 | 为什么影响扩展 | 建议动作 |
|---|---|---|---|
| P0 | observation/action 的真实物理时序及单位未被端到端审计 | 会使所有训练目标在物理上错位，且 shape 检查无法发现 | 用 telemetry、控制日志、视频时间戳建立可视化对齐测试 |
| P0 | 真机 action adapter 和安全边界未固化 | Policy 只输出解码动作，不提供限位/急停/执行策略 | 定义独立 adapter、限幅、超时、replan 和安全测试 |
| P1 | 当前 checkpoint 尚未完成未见 episode / closed-loop 评估 | 训练集 open-loop 不能替代泛化或任务能力证据 | 固定未见 episode split，再设计仿真/真机闭环协议 |
| P1 | 同名 relative-action 字段在训练 config、Processor、model config 中存在不同值 | 当前 absolute action 未触发；未来 relative/EEF 扩展中若混淆责任层会直接影响 decode 解释 | 保存前后 config diff，明确 Processor + ActionConfig + stats 才是运行时语义源 |
| P1 | 本地源码修改未与上游逐项对齐 | 后续升级、导出、复现可能出现不可解释差异 | 建立 patch 审计表和最小回归测试 |
| P2 | 触觉融合路线尚未澄清 | 贸然改模型会把数据、架构与控制变量混合 | 先确定触觉类型和最小 A/B 基线，再做消融 |

### 11.3 研究结论：黑盒已被拆成可操作边界，但还不是已验证系统

截至本草稿，GR00T 对本项目已不再是“一个训练脚本加一个大模型”的不可解释黑盒。训练输入侧已被拆为 LeRobot 磁盘契约、episode/step/shard、statistics、Processor/collator；多机器人差异已被拆为 tag、modality config、projector index 和 mask；模型内部已定位为冻结/可调的 Qwen3-VL 条件 backbone 与基于 cross-attention、flow matching 的 DiT action head；训练与推理已分别定位到 `experiment.run()` / `Gr00tTrainer` 和 `Gr00tPolicy` / evaluator 的稳定边界。

但“白盒化”不应被误解为“模型已经被证明有效”。当前有三类仍需通过实验和系统工程回答的问题：数据是否物理正确且覆盖任务；策略在开环和闭环中是否可靠；新增触觉应如何同步、表示、融合并在相同协议下带来可测增益。后续工作应按这些可验证问题推进，而不是继续在模型主干中进行无证据的局部修改。

正式汇报生成前，应基于本草稿压缩为面向老师的版本：保留一张全工程调用图、一张 13D 端到端映射表、一张多 embodiment/触觉扩展决策表，以及“已证实—待验证—下一步实验”的结论表；移除重复函数细节，但保留每项结论的文件级证据索引。

---

## 参考证据索引（第 5—11 章）

| 编号 | 本地证据 | 用途 |
|---|---|---|
| E22 | `gr00t/data/embodiment_tags.py:24-259`；`data/types.py:25-120` | tag 阶段、VLAStepData、modality/action config 类型契约 |
| E23 | `model/gr00t_n1d7/processing_gr00t_n1d7.py:57-101, 292-296, 382-544, 581-892` | projector index、Processor/decode、保存/重载 |
| E24 | `model/modules/embodiment_conditioned_mlp.py:60-207` | category-specific projector 参数与 action encoder |
| E25 | `model/gr00t_n1d7/gr00t_n1d7.py:39-645` | action head、flow matching train/inference、冻结和模型装配 |
| E26 | `model/modules/dit.py:61-410`；`model/modules/qwen3_backbone.py:340-365` | AdaLN、self/cross attention、AlternateVLDiT、Qwen token feature 输出 |
| E27 | `configs/model/gr00t_n1d7.py:27-180`；输出 `experiment_cfg/final_model_config.json` | 模型上限、最终 N1.7 模型配置 |
| E28 | `experiment/experiment.py:39-385`；`model/gr00t_n1d7/setup.py:47-242`；`data/dataset/factory.py:24-108` | pipeline、stats、Trainer、Processor 保存与 eval 限制 |
| E29 | `experiment/trainer.py:152-340`；`configs/training/training_config.py:25-168` | dataloader、resume、loss、checkpoint 兼容性 |
| E30 | 当前输出的 `config.yaml`、`checkpoint-30000/trainer_state.json`、checkpoint 工件目录 | 30k step、训练设置、loss log、保存产物 |
| E31 | `policy/gr00t_policy.py:70-744`；`eval/_horizon_contract.py:56-159` | Policy 输入输出验证、decode、execution horizon 契约 |
| E32 | `eval/open_loop_eval.py:104-234`；`eval/rollout_policy.py` | open-loop MSE/MAE 与仿真 rollout 的实际边界 |
| E33 | 上游发布与使用材料（版本、数据、训练、评估与许可章节） | 官方发布定位、依赖/数据契约、server-client/ReplayPolicy、训练提示、许可证和引用 |
