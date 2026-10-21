# T-021：未来采集与 LeRobot v3 转换工程规格

## 1. 目标与非目标

目标：为未来正式的 Franka/Pico 数据采集建立可实现的 raw 数据契约、独立传感器时间轴、离线跨传感器对齐、LeRobot v3 导出和 fail-closed QC。

非目标：不迁移历史试验数据；不改变 Pico/Franka 控制频率、Cartesian 控制语义、阻抗、Desk 限制、坐标变换或安全逻辑；不在本任务运行真机。

## 2. 业务依据与验收

依据：RB-015；BA-015、BA-016、BA-017、BA-020、BA-021、BA-022、BA-023、BA-024；D-037；用户提供的 `.project-log/docs/requirements/lerobot-v3-semantic-format-v1.0.md`。

核心验收：

- 一次采集运行形成一个不可变 raw batch；采集只写 rich raw，不写最终 v3。
- 每个传感器保存自身样本、单调时间戳及相对统一采集起点的时间轴；传感器可不同频。
- 默认以外部固定相机为参考，离线生成从 0 开始、严格 30Hz 的虚拟时间轴。
- 每个虚拟时刻对每个传感器做最近邻匹配；默认容差为该传感器声明周期的一半。
- 超过容差、缺时间戳、时间轴非法或边界需要外推时，样本/批次 QC 失败，不静默填充。
- 未来正式数据使用实际时间戳；历史试验数据不作为正式 v3 输入。
- v3 action/state 必须忠实表达确认的 Franka 语义，不能用旧 delta action 或推导 IK 冒充绝对 action。

## 3. 当前行为与差距

当前 `RLinf-Franks/post_process_to_lerobot.py` 使用旧 generic `image/state/actions` writer；普通 pickle 的 `states` 为 19 维 reset-relative 向量，`intervene_action` 为 Cartesian delta + gripper，不能直接满足严格 v3 profile。当前采集以控制步快照为主，缺少正式的统一起点和每传感器时间轴契约。故现有转换器是 legacy/过渡工具，不得标记为 v3 实现。

## 4. 目标 raw 契约

batch manifest 至少包含：`schema_version`、`batch_id`、采集源版本/配置、`acquisition_start_monotonic`、时钟源、相机映射、默认 reference sensor、virtual fps、每传感器有效频率和匹配容差、episode 清单。

每个 sensor stream 包含：`sensor_id`、类型/物理语义、数据存储引用、`timestamps_s`（相对于统一起点的 float 秒）、单位、时钟源、实际样本数、首末时间戳、有效区间、声明频率。时间戳必须 finite、非递减；发生时钟重置、负跳变或缺失即 batch invalid。采集起点由采集编排层生成一次，不由各传感器自行定义。

相机：外部固定相机和腕部相机独立保存约 30Hz 原始视频/帧流与每帧时间戳；实际时间戳优先于标称频率。最终编码为 MP4 的具体 codec/库属于 solution-research，不在本规格中偷偷决定。

Franka/夹爪：每控制采样保存实测 joint position[7]、实测 base-frame TCP `[x,y,z,qx,qy,qz,qw]`、实测 gripper；保存所有 guard/clip 后实际送入 Franky 的 base-frame absolute TCP target 和独立 gripper target；保存 control-step 到各传感器流的关联或可重建信息。终止 provenance 必须区分 success、operator failure、timeout、abort。

### 4.1 字段级最小契约

字段名采用以下语义；具体文件格式可以由技术方案选择，但不得改变字段含义：

| 所有者 | 必填字段 | 类型/约束 | 生产时机 |
|---|---|---|---|
| batch | `schema_version`, `batch_id`, `acquisition_start_monotonic`, `clock_source`, `task_text`, `capture_mode` | string/finite scalar；task 可为空；mode 为声明枚举 | batch 创建时一次写入 |
| batch | `reference_sensor`, `virtual_fps`, `sensor_streams`, `episodes` | manifest contract；当前 virtual_fps=30 | batch 封存时补齐 |
| sensor stream | `sensor_id`, `sensor_kind`, `timestamps_s`, `sample_refs`, `declared_rate_hz`, `tolerance_s`, `first_timestamp_s`, `last_timestamp_s` | timestamp 与 sample_refs 一一对应；finite、非递减；tolerance>0 | 传感器启动/封存 |
| camera sample | RGB frame/video reference、`timestamp_s`、source frame index | RGB-only；source frame index 稳定 | 每帧采集 |
| control sample | `timestamp_s`, `measured_joint_position`, `measured_eef_pose`, `measured_gripper`, `final_eef_target`, `gripper_target` | q[7] rad；pose[7] xyz+xyzw；gripper[1]；target 为最终实际发送值 | 每个控制步 |
| episode | `episode_id`, `start_timestamp_s`, `end_timestamp_s`, `terminal_event`, `outcome` | terminal_event ∈ success/failure/timeout/abort；abort 不形成完整 episode | 终止时 |
| alignment manifest | virtual timestamps、每路 matched raw index、signed offset、validity、reuse_count、QC result | 可重放；未来邻居允许且必须可见 | 离线转换 |

传感器队列溢出、视频落盘失败、控制步无法写入或 batch 封存不完整时，batch 标记 incomplete/invalid；不得用空数组、最后一帧或零值补写。原始文件写入采用临时文件后原子封存，转换器只接受已封存且 manifest 完整的 batch。

## 5. 对齐契约

1. 选择外部固定相机作为默认 reference sensor；reference 的有效区间定义 episode 对齐区间。
2. 生成 `t_k = k / 30`，从 0 开始，覆盖 reference 有效区间；不得把真实相机间隔宣称为严格 1/30。
3. 对每个 `t_k` 和每个 sensor，在其自身有效区间内选择时间差绝对值最小的样本。
4. 默认 `tolerance_sensor = 0.5 * declared_period_sensor`；实际生效值写入 manifest。
5. 最近邻超出 tolerance、无候选、时间轴越界或边界外推均使对应 aligned sample invalid，QC fail；不得用首帧/末帧补齐。
6. 同一 raw sample 可被多个虚拟时刻复用，只要每次均满足 tolerance；记录每个 sensor 的 reuse count、最大误差、误差分布和匹配 raw index。
7. 对齐输出必须保存 reference sensor、virtual fps、timeline 起止、每个传感器 tolerance、匹配索引和误差摘要，保证可重放。

## 6. v3 输出映射

输出遵守用户 v3 文档的 `data/`、`meta/`、`videos/` 布局、parquet、stats、tasks、episodes 和 QC 要求。

- `observation.state.joint_position`: measured q[7] rad。
- `observation.state.eef_pose`: measured base-frame `[x,y,z,qx,qy,qz,qw]`。
- `observation.state.gripper`: measured opening[1]，单位和范围写入 custom。
- `action.eef_pose`: final post-guard/clip absolute base-frame target[7]，不是 Pico delta、requested pre-clip target、measured pose 或 IK 结果。
- `action.gripper`: independent target[1]；不拼接到 joint position。
- `custom.action_space = eef_pose_absolute`；不输出 `action.joint_position`。
- ZED 2i → `observation.images.cam_ext_0`；ZED-M → `observation.images.cam_wrist_right`；写入 `custom.camera_key_map`。
- 最终 RGB-only；不输出 depth/point cloud。
- `timestamp` 使用虚拟 30Hz timeline；原始时间戳和对齐事实保存在 provenance/manifest，不被覆盖。

## 7. 导出模式与生命周期

转换器一次只接受一个已完成 raw batch、一个输出目录和一个显式模式；raw 源只读，输出失败时不得伪装成可发布数据。

- `standard-success-only`：仅显式 success，严格 v3。
- `standard-all`：success + operator failure，严格 v3，不加 outcome 字段。
- `labelled-all`：success + operator failure，带明确声明的 outcome 扩展。
- timeout 默认 raw-only；abort 不形成完整可导出 episode。

本增量明确不把 timeout 纳入任何正式 v3 export，包括 `labelled-all`；`labelled-all` 只扩展 success/failure outcome。未来若要导出 timeout，必须另行澄清并定义新的 outcome schema。

缺少 terminal provenance、必需 state/action、时间戳、相机映射或视频关联时 fail-closed。partial output 必须标记 invalid 或写入临时目录，不能作为成功导出。

## 8. 模块边界与技术待研究

- Collector/orchestrator：生成 batch 起点、管理生命周期和 raw manifest。
- Sensor adapters：各自采集并写入数据与相对时间戳；不得互相等待以强行同频。
- Episode recorder：保存 terminal provenance、控制步 state/action 和 sensor association。
- Offline aligner：只读 raw，生成 virtual timeline、匹配索引和 alignment manifest。
- v3 writer：根据已对齐样本写 parquet/MP4/meta，不改变 raw。
- QC：验证 schema、shape、dtype、时间轴、容差、边界、复用、视频、统计和 episode 范围。

需单独 research：官方 LeRobot v3 精确版本/API；MP4 编码库与 codec/GOP/pix_fmt；视频 CFR/PTS 写入方式；高频相机 recorder 的可靠落盘方式。研究结果不得改变已确认业务语义而未重新澄清。

## 9. 错误、并发、幂等与诊断

采集失败应保留 raw failure manifest，并明确 batch incomplete；转换只读取已封存 batch。输出目录使用唯一 converter/version/mode 标识，重复运行不得覆盖 raw 或已发布输出；同一输入 hash + 配置应得到可识别的同一转换版本。日志必须包含 batch id、source hash、reference sensor、virtual fps、tolerances、invalid counts、reuse counts 和 QC verdict。

## 10. 兼容、迁移、回滚

旧 pickle 仅作历史诊断，不迁移、不强行补字段、不进入正式 v3。新 raw schema 通过显式 schema version 和 capture manifest 区分。新转换器与当前 legacy converter 并行存在，直到 v3 QC 和独立验证完成；失败时删除/隔离无效输出即可，raw 永不回滚或覆盖。

## 11. 测试矩阵与证据

- raw schema：多传感器不同频率、统一起点、时间戳单调性、缺失/重置/NaN fail-closed。
- aligner：严格 30Hz 网格、最近邻、半周期 tolerance、恰好阈值、超阈值、首尾越界、复用统计、tie-break 稳定性。
- semantic mapping：q/TCP/gripper/action provenance、四元数顺序、单位、禁止 IK/delta 冒充。
- episode/export：success/failure/timeout/abort 选择、三种模式、raw 不变、重复运行和 partial output。
- v3/QC：目录、parquet schema、stats、tasks、video references/PTS、camera map、custom metadata、排序和范围。
- 端到端离线 fixture：合成不同频率 sensor streams + 固定相机 reference，验证 alignment manifest 与预期索引。
- 硬件验证不由本任务或 Agent 执行；未来由操作者在空载、安全工作区运行并绑定日志和 raw hash。

## 12. 技术研究结论与下一步

研究记录：`RS-022-lerobot-v3-integration-path`。

采用 **spike-first → pinned-release wrapper-adapter**：先用无硬件合成数据比较 `lerobot==0.4.4` 与最新兼容 0.6.x，验证官方 loader、feature schema、episode metadata、tasks、video PTS 和 finalize；候选通过后由项目适配器调用固定版本 API。不得原地改造当前 legacy converter。项目自行拥有 raw provenance、独立时间轴、对齐器、语义映射、outcome、manifest 和 QC；LeRobot 负责可兼容的序列化/最终化。

研究发现的硬约束：官方 v3 从 `lerobot>=0.4.0` 开始；当前 RLinf writer 的 generic `state/actions/image` 不满足本项目语义；上游不同版本的 metadata layout 可能与用户提供的项目契约不同，必须用 synthetic spike 解决，不能仅凭 `v3.0` 宣称兼容。编码器库、codec 和精确 package pin 是技术研究项，不改变已确认业务语义。

## 13. 开放事项与状态

状态：独立静态复核发现规格仍不具备实施条件，不能宣称只剩技术选型。以下补充优先于上文概述；不进入产品实现。

## 13. 独立复核后的补充约束

- 补充依据 BA-018/BA-019：采集无数量目标、无自动停止；c/f 成功持久化后分别累计 success/failure，abort/timeout 不计入该完成计数。batch 仅有一个 task_text，空字符串合法，换任务须新开 batch；转换不得发明任务文本。后续补充文本只生成受审计的新输出，原 raw 保持不变。
- 输出文件规范以用户文档具体章节为强制验收：§1 文件布局与大小限制；§2.1 五个固定索引列及 float32 state/action；§2.2 episode 索引范围、长度与视频左闭右开区间；§2.3 tasks 的 task 索引及连续 task_index；§2.4 info 的计数、paths、splits、features/names；§2.5–2.7 float64 统计及全部分位数。不得只修改 codebase_version 冒充 v3。
- 视频 GOP=2、实际 fps/codec/pix_fmt 与声明一致、episode PTS 恰好覆盖 length 帧、单 episode 不跨 MP4、随机访问平均小于50ms，均需验证。后处理 RGB 编码已获授权，但源视频 codec 保留与重采样/重编码的兼容方案仍待研究，不能擅自豁免。
- 训练 loader 验收必须包括标准模式可读取、任务索引可解析、episode/frame 顺序与数值一致；labelled-all 的扩展必须显式声明，不能声称所有官方 loader 天然支持。
- 最近邻等距时选择较早样本，再以 raw index 决胜（工程默认）；阈值使用声明频率，不从已丢帧数据动态放宽。原始 timestamp、映射时钟方法、接收时间和视频 PTS 分开记录；统一起点不等于硬件时钟已同步，接收时间不可冒充曝光时刻。
- raw manifest/stream 的字段名、类型、存储布局、producer、封存协议、队列溢出及磁盘故障处理还需具体化；相机采样和命令/状态采样必须保持来源可追踪，不复制旧 delta 为 action。

## 14. 必须解决的规格阻塞

1. 起点边界已解决：虚拟 `t=0` 严格等于 batch 统一采集起点；传感器首帧可晚于 `t=0`，仅当其时间差不超过该传感器容差时匹配；不得把各流首帧分别归零或超容差外推。episode 的正式起点事件和 batch 起点关系必须由 raw manifest 记录。
2. 原始 batch 时间轴与 v3 episode-relative 时间轴必须同时保留：raw 使用 batch-relative timestamp，v3 输出使用该 episode 的虚拟 aligned timestamp；转换器必须保存两者映射。正式工程实现仍需明确导出末端网格点/终止事件的包含规则。
3. action 是命令而非传感器测量；按 D-038 允许对 action 做对称最近邻，因此选中的命令可以落在虚拟时刻之后。对齐 manifest 必须保留原始命令时间戳、带符号时间偏移、raw index 和容差，不能把结果描述为过去方向因果配对；实现阶段需用合成 fixture 验证该语义。

最早回退阶段：剩余规格工作集中于官方 v3 依赖/视频技术研究及字段与当前模块的最终落点核对；episode 网格采用 `[start, terminal)`，只有严格早于终止时间的虚拟点进入输出，timeout 仍 raw-only。完成标准仍是另一位工程师无需猜测即可实现；当前已接近但未宣称实施完成。
