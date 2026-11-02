# 统一新采集 HDF5 落盘格式

- **ID**：`hdf5-recording-format`
- **版本**：1.7
- **状态**：active
- **目标**：统一新采集数据的 HDF5 键树、字段语义、任务/batch/episode 元数据和封口流程。
- **关联 Task**：`hdf5-requirement-baseline-v1-1`、`data-collection-business-clarification`
- **当前版本批准日期**：2026-11-01
- **前一版本**：1.6（已 supersede）
- **证据**：用户提供的《Robot Capture HDF5 输出业务基线》与《自采数据 HDF5 落盘规范》，以及后续业务澄清；v1.7 的观测 `eef_pose` 统一为 `(T,7)` 四元数由用户确认。基准为元文档，除 action `eef_pose`、四元数顺序 attrs 与观测 `eef_pose` 维度统一外不增删字段。

## 参与者

- **操作员**：选择任务、开始/结束/废弃采集、发起上传和质检。
- **采集平台**：采集相机、机器人状态和控制参考，生成并校验 episode，维护 batch 清单。
- **下游/存储端**：读取统一键树和 attrs，核对文件、MD5、manifest 与封口状态。

## 范围内规则

### R1. 统一采集语义

不同机械臂共用采集、录制、导出和上传链路；机器人差异由适配层提供标准化状态、实际控制参考和事件。公共 recorder 不直接依赖具体机械臂 SDK，也不直接调用适配器：适配器把声明与数据交给统一的采集中间层，采集层只消费该中间接口。

数据必须区分：机器人实测状态、实际提交给驱动的控制参考、action 来源与有效性。实测 EEF 不得冒充 action。不同关节数量、单臂/双臂布局和设备能力由机器人描述表达，不创建按型号分裂的数据契约。

**验收条件**：不同构型能够向同一 recorder 语义提供数据；Franka 七轴不截断，夹爪不混入关节数组；状态和控制参考可区分；采集层不含任何机型判断。

### R2. 缺失数据与零值

没有采集到的数据不写入 HDF5；禁止用全零数组、复制上一帧或其他伪造值占位。真实采集到的全零状态或 action 必须原样保留，不能依据数值是否为零判断缺失。

R6 规定的“adapter 仍实际保持上一控制目标”不属于 recorder 复制上一帧伪造数据：保持期间重复出现相同 action 值，是持续有效控制参考的正常表达；recorder 不得脱离 adapter 状态自行延续 action。

**验收条件**：缺失信号不会生成伪造数值；真实全零样本不会被过滤或拒收；持续保持的 action 有 adapter 实际控制状态作为来源。

### R3. 主时间轴

根下只有 `/timestamp`，类型为 float64 Unix 秒，来源为采集主机 `CLOCK_REALTIME`。写入的 timestamp 严格递增，状态、图像和 action 的每一行对应同一时间点。

主时间点由实际相机同步帧组产生，每个帧组对齐一行机器人实测状态和 action；不按标称 fps、控制循环或录制器定时器伪造主时间点。采集可配置为 30Hz 或 60Hz，但 60Hz 必须由真实、同步的 60fps 相机采集及足够频率的状态/action 支撑，不得通过复制、插值或伪造 timestamp 扩帧。

**验收条件**：无重复或伪造 timestamp；所有实际写入的数据行与 timestamp 对齐；配置 60Hz 时输出源于真实 60fps 采集，而不是低帧率数据扩容。

### R4. `cam_dup` 废弃

不实现、不写入、不校验 `<cam>_dup`，也不将其作为验收条件。相机缺帧沿用有效帧同步和质量检查，不得借此伪造机器人状态或 action。

用户已明确：原规范中“掉帧后复制上一帧并标 `true`，供下游判断是否插值”的机制整体废弃。

**验收条件**：输出键树不存在 `<cam>_dup`；验证器不要求该字段。

### R5. 机器人与臂别

- `robot_id` 由机器人描述/配置提供，是具体机器编号，不得由目录名或型号推断；`robot_model` 才是型号。
- 单臂使用 `main`，双臂使用 `left` 和 `right`。
- 单臂只写选中侧实际采集到的状态、相机和 action，不伪造未选侧。
- 双臂写两侧实际数据；无法取得基座相对位姿时，`base_extrinsics` 写 `unknown`，不得猜测。

**验收条件**：单臂键树只出现 `main`；双臂只出现实际有效的 `left/right`；不存在未选侧补零实体；`robot_id` 与机器人描述、manifest 一致。

### R6. Action 字段与能力声明

`action` 不使用推导值：关节型驱动记录适配器实际下发的关节目标，笛卡尔驱动记录实际下发的 EEF 目标；不得把 EEF action 反算成 joint action，也不得把实测状态冒充 action。

可记录的 action 字段只有两个，字段名、形状与单位固定：

```text
action/<side>/eef_pose      (T, 7)  位置 m，姿态四元数 xyzw
action/<side>/joint_position(T, J)  弧度，J 由机器人描述给出
```

`gripper (T, 1)` 继续独立表达，不混入机械臂关节数组。

每个机器人适配器必须声明自己能提供哪些字段，采集层按声明落盘：

- 同时声明两者 → 两个数据集都写；
- 只声明其一 → 只写该数据集，另一个不创建；
- 两者都未声明 → `has_action=false`，不创建 `/action`。

未创建的数据集本身即表示该构型不支持该字段，不额外在 attrs 中记录声明清单。

EEF pose 为 `[x, y, z, qx, qy, qz, qw]`，四元数顺序 `xyzw`。attrs 必须声明坐标系、TCP、TCP offset、数据来源和单位；`source` 当前遥操作可为 `command`。

遥操作会话仍有效且 adapter 保持上一目标时，操作员松开 Grip 不使 action 失效：adapter 将上一时刻实际发送的控制参考作为持续保持目标，后续采集帧继续记录该有效 action，直到取得新目标或 adapter 真正进入 hold、暂停、失去控制权等不再保持该目标的状态。重复数值来自持续控制状态，不是 recorder 复制上一帧；不再保持后不得由 recorder 自行沿用。

**验收条件**：action 键树和 attrs 符合语义；只出现适配器声明过的字段；实测状态与控制参考可区分；真实全零 action 保留；松 Grip 且 adapter 持续保持时 action 连续有效，重新跟随取得新目标后替换，真正 hold 后不由 recorder 伪造延续。

### R7. HDF5 键树与 attrs

新 episode 写入 `/timestamp`、`/observation/state`、`/observation/images`，有 action 才写 `/action`，有实际数据才写 `/language`。每个数值字段写明单位、维度名、坐标系或必要数值约定。每路相机写 `mount`、`serial`、`decoded_shape`；本阶段不写 `intrinsics`、`extrinsics`。

`/observation/state/<side>/` 的字段白名单，字段名与形状固定：

```text
joint_position  (T, J)  float32  rad
joint_velocity  (T, J)  float32  rad/s   可选
joint_effort    (T, J)  float32  N·m     可选
gripper         (T, 1)  float32  m
eef_pose        (T, 7)  float32  m + 四元数 xyzw
```

其中 `eef_pose` 由元文档的 `(T, D)`、由 attrs 声明数值约定，统一收敛为 `(T, 7)`、位置米、四元数 `xyzw`，与 action 的 `eef_pose` 保持一致，便于下游用同一套解析。观测侧仍需在 attrs 中声明坐标系、TCP 与 `quat_order`。

**验收条件**：必需数据集、字段和 attrs 存在且语义完整；无实际数据的可选节点不创建；观测 `eef_pose` 为 `(T, 7)` 且四元数顺序为 `xyzw`。

### R8. 根 attrs

写入：`spec_version`、`robot_type`、`robot_model`、`robot_id`、`arms`、`episode_id`、`batch_id`、`task_id`、`task`、`collect_mode`、`has_action`、`fps_nominal`、`num_frames`、`operator`、`scene`、`success`、`discarded`、`discard_reason`、`timezone`、`sensors`。

当前固定约定：

- `spec_version` 统一为 `inhouse-hdf5-v2`，manifest 与 episode 使用同一字符串；
- `operator=user`、`timezone=Asia/Shanghai`；
- `collect_mode` 当前固定为 `teleop`（元文档枚举 drag/teleop/policy，本平台只实现遥操作采集）；
- `project` 只写入批次级 manifest，不写入 episode 根 attrs（元文档 episode attrs 清单中无此字段）；
- 未知信息不得虚构；`sensors` 为 JSON 字符串，记录实际相机型号、序列号、分辨率和安装位置。

**验收条件**：episode attrs 与任务配置、batch、manifest 和结束结果一致；结果字段不互相矛盾。

### R9. 任务与 batch

开始采集前必须选择任务配置；新建任务填写 `project`、`task_id`、`task`、`scene`，配置可在重启后继续选择。一个 batch 只能使用一套任务元数据；换任务创建新 batch，历史 batch 不被修改影响。

batch 为 `YYYYMMDD_NN`，日期取第一条 episode 开始时刻的北京时间，编号从 `01` 递增；episode 编号从 `0` 连续递增并六位补零。第一条 episode 真正开始采集时才分配 batch ID；未采集任务不占编号；工作台同时只能有一个未结束 batch，手动结束后不可追加。

**验收条件**：编号、目录、文件名、attrs 和 manifest 一致；任务切换不改写历史 batch。

### R10. 原子落盘、manifest 与封口

episode 先写 `.hdf5.tmp`，完成结构和数据校验后原子 rename 为 `.hdf5`。上传后计算并记录 MD5，更新 `manifest.json`；目录文件、清单、远端文件和核对结果全部完成后，最后写 `_SUCCESS`。没有 `_SUCCESS` 不视为 batch 完整交付。

`manifest.json` 字段以用户确认的元文档为准：

- 批次级：`spec_version`、`project`、`robot_id`、`robot_type`、`task_id`、`task`、`batch_id`、`operator`、`scene`、`episodes`、`n_episodes`、`created_at`；
- `episodes[]` 每项：`file`、`episode_id`、`num_frames`、`bytes`、`md5`。

用户已明确废弃以下字段，不得写入：`episodes[].success`、`episodes[].discarded`、批次级 `n_discarded`。episode 是否成功、是否废弃只由该 episode 的 HDF5 root attrs 表达，manifest 不做重复记录。

上传失败可重试同一 batch，不新建 batch、不改变编号；成功后保留本地数据。

**验收条件**：异常中断不会产生可误认为完整交付的 `_SUCCESS`；manifest 与目录 HDF5 一一对应，MD5 和文件大小一致；manifest 中不出现已废弃字段。

### R11. Episode 结果

结果只写入 episode 自身的 HDF5 root attrs，不写入 manifest：

- 正常保存：`success=true`、`discarded=false`。
- 用户确认废弃：`success=false`、`discarded=true`，并填写 `discard_reason`。
- 废弃 episode 保留文件和编号，不通过删除文件制造编号空洞。
- 异常中断保留残留文件和已分配编号，不自动标记成功；人工确认成功或废弃后才允许上传。
- 自检失败不能由人工按钮绕过。

**验收条件**：HDF5 attrs 与文件状态一致；废弃与异常数据可追溯；manifest 不含结果字段。

## 范围外

- 不迁移或重写历史 HDF5。
- 不修改 Franka 控制算法、限位、增益或安全策略。
- 不实现相机 zoom/exposure 配置。
- 不实现 `cam_dup`。
- 不设计真实 operator 账号系统，暂时固定 `operator=user`。
- 不新增 per-frame invalidity-mask 框架。
- 不把 EEF action 反算为 joint action，也不把关节 action 正算为 EEF；两者只在适配器实际下发对应目标时记录。
- 不以自动测试通过宣称真实机器人或物理同步已经验收。

## 暂缓和未决

### Q1. 非保持状态下的 Action 间歇缺失（部分解决，剩余暂缓）

v1.2 已解决普通松 Grip 场景：只要 adapter 仍实际保持上一目标，该 action 持续有效，按 R6 记录，不属于缺失。

如果 adapter 真正进入 hold、暂停、失去控制权或其他不再保持目标的状态，导致一个已有 action 的 episode 中途没有 action，当前基线仍只确认：不得写零值、不得由 recorder 复制上一帧、不得把实测 EEF 冒充 action；该段如何处理以及时间轴如何处理，暂不解决。

如果整个 episode 都没有 action，则 `has_action=false`，不创建 `/action/`。

**是否阻塞**：普通松 Grip 的 action 导出已不再阻塞；真正无活动控制参考的间歇缺失仍阻塞对应异常分支的最终导出规则，不阻塞任务配置、batch/episode 状态机、manifest、非 action 数据链路及当前全程保持目标的正常采集设计。

### Q2. `spec_version`（已解决）

统一为 `inhouse-hdf5-v2`，manifest 与 episode 的 root attrs 使用同一字符串。按“取最新”规则裁定元文档中 `inhouse-hdf5-v1` / `inhouse-hdf5-v2` 的示例冲突。

### Q3. 历史兼容与质检拒收对 batch 封口

历史 HDF5 不自动迁移；旧数据兼容策略，以及质检拒收条目是否阻塞 `_SUCCESS`，另行设计。

**是否阻塞**：不阻塞新数据链路初步实现，但阻塞最终交付流程冻结。

## 约束与假设

- 新格式只服务新采集数据；历史格式保持原样。
- 机器人适配层提供标准化状态和实际控制参考，公共 recorder 不读取厂商 SDK。
- 真实全零值通过采集来源/有效性语义识别，不能用数值启发式识别缺失。
- 持续 action 的有效性必须来自 adapter 的实际跟踪/保持状态；recorder 只记录该状态提供的控制参考，不得自行根据上一行推断仍有效。

## 变更控制

新业务规则不得直接覆盖 active baseline；应创建变更候选，说明受影响的 HDF5 字段、采集流程、校验、上传、测试和历史兼容范围，确认后递增版本并在本文件保留变更记录。

### 变更候选：采集时记录相机内外参（2026-10-29 提出，2026-11-01 暂缓）

- **状态**：本阶段不实施、不采集、不写入 HDF5。
- **当前规则**：按元文档“每路相机写 `mount`、`serial`、`decoded_shape`”，不写 `intrinsics`、`extrinsics`；未标定不影响录制。
- **若恢复**：需先确认参数来源、外参参考坐标系与变换方向、与分辨率的绑定关系、未标定时的处理，再递增版本。

## 版本历史

### v1.0（已 supersede，2026-10-29）

初版固化 HDF5 落盘规则、缺失数据、EEF action、任务/batch/episode、manifest、MD5、原子落盘和 `_SUCCESS`，并将 action 间歇缺失列为未决项。

### v1.1（已 supersede，2026-10-29）

补充统一采集语义：不同构型共用 recorder 和数据契约，机器人差异由适配层提供标准化状态与控制参考；未改变 HDF5 语义，也未解决 action 间歇缺失。

### v1.2（已 supersede，2026-11-01）

补充实际相机同步帧组驱动主时间轴及真实 60Hz 配置约束；明确普通松 Grip 时，只要 adapter 仍实际保持上一已发送目标，该 EEF/夹爪 action 持续有效，重复数值不属于 recorder 复制伪造。真正 hold、暂停或失去控制权后的间歇缺失仍暂缓。影响 R2、R3、R6、Q1 及后续 recorder/adapter 契约测试，不改变控制算法或安全参数。

### v1.3（已 supersede，2026-11-01）

action 由单一 EEF 扩展为两个可选字段：`eef_pose` 与 `joint_position`，各构型可按需只提供其一或两者；两者都未提供时 `has_action=false`。新增适配器声明能力、采集层按声明落盘的规则，未创建的数据集即表示该构型不支持该字段，不额外写入声明 attrs。采集层不得直接调用适配器，统一经采集中间层。`robot_id` 由机器人描述提供，不再固定为 Franka 型号。

### v1.4（已 supersede，2026-11-01）

按用户确认的元文档变更收敛 manifest 与掉帧语义：`manifest.json` 不再写入 `episodes[].success`、`episodes[].discarded` 和批次级 `n_discarded`；episode 结果只由自身 HDF5 root attrs 表达。`<cam>_dup` 及其“复制上一帧供下游插值”的用途整体废弃。

### v1.5（已 supersede，2026-11-01）

`spec_version` 按“取最新”裁定为 `inhouse-hdf5-v2`，manifest 与 episode 统一；`collect_mode` 当前固定 `teleop`；`project` 只写 manifest、不写 episode 根 attrs。

### v1.6（已 supersede，2026-11-01）

相机内外参与标定相关 attrs 本阶段不采集、不写入：`/observation/images/<cam>` 只写 `mount`、`serial`、`decoded_shape`；未标定不影响录制。

### v1.7（当前，2026-11-01）

在 R7 明示 `/observation/state/<side>/` 字段白名单；观测 `eef_pose` 由元文档的 `(T, D)` 收敛为 `(T, 7)`、位置米、四元数 `xyzw`，与 action 侧一致。`joint_velocity`、`joint_effort` 保持可选。影响 R7 与采集中间层的白名单内容。
