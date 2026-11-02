# 统一新采集 HDF5 落盘格式

- **ID**：`hdf5-recording-format`
- **版本**：1.1
- **状态**：active
- **目标**：统一新采集数据的 HDF5 键树、字段语义、任务/batch/episode 元数据和封口流程。
- **关联 Task**：`hdf5-requirement-baseline-v1-1`
- **批准日期**：2026-10-29
- **前一版本**：1.0（已 supersede）
- **证据**：用户提供的《Robot Capture HDF5 输出业务基线》与《自采数据 HDF5 落盘规范》，以及后续业务澄清。

## 参与者

- **操作员**：选择任务、开始/结束/废弃采集、发起上传和质检。
- **采集平台**：采集相机、机器人状态和控制参考，生成并校验 episode，维护 batch 清单。
- **下游/存储端**：读取统一键树和 attrs，核对文件、MD5、manifest 与封口状态。

## 范围内规则

### R1. 统一采集语义

不同机械臂共用采集、录制、导出和上传链路；机器人差异由适配层提供标准化状态、实际控制参考和事件。公共 recorder 不直接依赖具体机械臂 SDK。

数据必须区分：机器人实测状态、实际提交给驱动的控制参考、action 来源与有效性。实测 EEF 不得冒充 action。不同关节数量、单臂/双臂布局和设备能力由机器人描述表达，不创建按型号分裂的数据契约。

**验收条件**：不同构型能够向同一 recorder 语义提供数据；Franka 七轴不截断，夹爪不混入关节数组；状态和控制参考可区分。

### R2. 缺失数据与零值

没有采集到的数据不写入 HDF5；禁止用全零数组、复制上一帧或其他伪造值占位。真实采集到的全零状态或 action 必须原样保留，不能依据数值是否为零判断缺失。

**验收条件**：缺失信号不会生成伪造数值；真实全零样本不会被过滤或拒收。

### R3. 主时间轴

根下只有 `/timestamp`，类型为 float64 Unix 秒，来源为采集主机 `CLOCK_REALTIME`。写入的 timestamp 严格递增，状态、图像和 action 的每一行对应同一时间点。

**验收条件**：无重复或伪造 timestamp；所有实际写入的数据行与 timestamp 对齐。

### R4. `cam_dup` 废弃

不实现、不写入、不校验 `<cam>_dup`，也不将其作为验收条件。相机缺帧沿用有效帧同步和质量检查，不得借此伪造机器人状态或 action。

**验收条件**：输出键树不存在 `<cam>_dup`；验证器不要求该字段。

### R5. 机器人与臂别

- `robot_id` 固定为 `Franka Research 3`。
- 单臂使用 `main`，双臂使用 `left` 和 `right`。
- 单臂只写选中侧实际采集到的状态、相机和 action，不伪造未选侧。
- 双臂写两侧实际数据；无法取得基座相对位姿时，`base_extrinsics` 写 `unknown`，不得猜测。

**验收条件**：单臂键树只出现 `main`；双臂只出现实际有效的 `left/right`；不存在未选侧补零实体。

### R6. Action

`action` 使用 EEF 语义，不转换为 joint action。有效侧使用：

```text
action/<side>/eef_pose (T, 7)
action/<side>/gripper  (T, 1)
```

EEF pose 为 `[x, y, z, qx, qy, qz, qw]`；位置单位为米，四元数顺序为 `xyzw`。attrs 必须声明坐标系、TCP、TCP offset、数据来源和单位；`source` 当前遥操作可为 `command`。

**验收条件**：action 键树和 attrs 符合语义；实测状态与控制参考可区分；真实全零 action 保留。

### R7. HDF5 键树与 attrs

新 episode 写入 `/timestamp`、`/observation/state`、`/observation/images`，有 action 才写 `/action`，有实际数据才写 `/language`。每个数值字段写明单位、维度名、坐标系或必要数值约定。每路相机写 `mount`、`serial`、`decoded_shape`；有标定信息时才写 intrinsics/extrinsics。

**验收条件**：必需数据集、字段和 attrs 存在且语义完整；无实际数据的可选节点不创建。

### R8. 根 attrs

写入：`spec_version`、`robot_type`、`robot_model`、`robot_id`、`arms`、`episode_id`、`batch_id`、`task_id`、`task`、`collect_mode`、`has_action`、`fps_nominal`、`num_frames`、`operator`、`scene`、`success`、`discarded`、`discard_reason`、`timezone`、`sensors`。

当前固定约定：`operator=user`、`timezone=Asia/Shanghai`；未知信息不得虚构；`sensors` 为 JSON 字符串，记录实际相机型号、序列号、分辨率和安装位置。

**验收条件**：episode attrs 与任务配置、batch、manifest 和结束结果一致；结果字段不互相矛盾。

### R9. 任务与 batch

开始采集前必须选择任务配置；新建任务填写 `project`、`task_id`、`task`、`scene`，配置可在重启后继续选择。一个 batch 只能使用一套任务元数据；换任务创建新 batch，历史 batch 不被修改影响。

batch 为 `YYYYMMDD_NN`，日期取第一条 episode 开始时刻的北京时间，编号从 `01` 递增；episode 编号从 `0` 连续递增并六位补零。第一条 episode 真正开始采集时才分配 batch ID；未采集任务不占编号；工作台同时只能有一个未结束 batch，手动结束后不可追加。

**验收条件**：编号、目录、文件名、attrs 和 manifest 一致；任务切换不改写历史 batch。

### R10. 原子落盘、manifest 与封口

episode 先写 `.hdf5.tmp`，完成结构和数据校验后原子 rename 为 `.hdf5`。上传后计算并记录 MD5，更新 `manifest.json`；目录文件、清单、远端文件和核对结果全部完成后，最后写 `_SUCCESS`。没有 `_SUCCESS` 不视为 batch 完整交付。

上传失败可重试同一 batch，不新建 batch、不改变编号；成功后保留本地数据。

**验收条件**：异常中断不会产生可误认为完整交付的 `_SUCCESS`；manifest 与目录 HDF5 一一对应，MD5 和文件大小一致。

### R11. Episode 结果

- 正常保存：`success=true`、`discarded=false`。
- 用户确认废弃：`success=false`、`discarded=true`，并填写 `discard_reason`。
- 废弃 episode 保留文件和编号，写入 manifest，不通过删除文件制造编号空洞。
- 异常中断保留残留文件和已分配编号，不自动标记成功；人工确认成功或废弃后才允许上传。
- 自检失败不能由人工按钮绕过。

**验收条件**：HDF5 attrs、manifest 和文件状态一致；废弃与异常数据可追溯。

## 范围外

- 不迁移或重写历史 HDF5。
- 不修改 Franka 控制算法、限位、增益或安全策略。
- 不实现相机 zoom/exposure 配置。
- 不实现 `cam_dup`。
- 不设计真实 operator 账号系统，暂时固定 `operator=user`。
- 不新增 per-frame invalidity-mask 框架。
- 不把 EEF action 转换为 joint action。
- 不以自动测试通过宣称真实机器人或物理同步已经验收。

## 暂缓和未决

### Q1. Action 间歇缺失（暂时没有解决方案）

如果一个 episode 中已经有 action，录制期间因松开 Grip 等原因出现一段时间没有 action，当前基线只确认：不得写零值、不得复制上一帧、不得把实测 EEF 冒充 action；该段如何处理以及时间轴如何处理，暂不解决。

如果整个 episode 都没有 action，则 `has_action=false`，不创建 `/action/`。

**是否阻塞**：阻塞 action 导出规则的最终实现；不阻塞任务配置、batch/episode 状态机、manifest 和非 action 数据链路设计。

### Q2. 具体 HDF5 `spec_version`

业务语义已冻结，但最终字符串版本尚未决定。

**是否阻塞**：阻塞最终格式常量冻结，允许先做内部结构设计。

### Q3. 历史兼容与质检拒收对 batch 封口

历史 HDF5 不自动迁移；旧数据兼容策略，以及质检拒收条目是否阻塞 `_SUCCESS`，另行设计。

**是否阻塞**：不阻塞新数据链路初步实现，但阻塞最终交付流程冻结。

## 约束与假设

- 新格式只服务新采集数据；历史格式保持原样。
- 机器人适配层提供标准化状态和实际控制参考，公共 recorder 不读取厂商 SDK。
- 真实全零值通过采集来源/有效性语义识别，不能用数值启发式识别缺失。

## 变更控制

新业务规则不得直接覆盖 active baseline；应创建变更候选，说明受影响的 HDF5 字段、采集流程、校验、上传、测试和历史兼容范围，确认后递增版本并在本文件保留变更记录。

### 待讨论变更候选：采集时记录相机内外参（2026-10-29）

- **用户提出的需求**：采集数据时记录相机内参和外参。
- **状态**：需求意图已记录，实现可行性和具体业务规则待后续讨论；暂不修改 v1.1 的 R7，不作为当前强制验收项，也不启动代码实现。
- **待确认**：内外参来源；外参所指的参考坐标系及变换方向；与实际图像流、分辨率的对应关系；参数不可获取或未标定时是否允许采集及如何处理。不得猜测参数或用伪造值占位。
- **预期影响范围**：相机参数获取/标定配置、录制元数据传递、HDF5 图像字段与 attrs、校验和测试；上传是否需要额外标定文件待讨论。候选仅面向新数据，不据此修改历史文件。

## 版本历史

### v1.0（已 supersede，2026-10-29）

初版固化 HDF5 落盘规则、缺失数据、EEF action、任务/batch/episode、manifest、MD5、原子落盘和 `_SUCCESS`，并将 action 间歇缺失列为未决项。

### v1.1（当前，2026-10-29）

补充统一采集语义：不同构型共用 recorder 和数据契约，机器人差异由适配层提供标准化状态与控制参考；未改变 HDF5 语义，也未解决 action 间歇缺失。
