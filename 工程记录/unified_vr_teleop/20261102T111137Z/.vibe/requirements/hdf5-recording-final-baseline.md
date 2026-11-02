# 统一数据采集与 HDF5 最终业务基线

- **ID**：`hdf5-recording-final-baseline`
- **版本**：1.0
- **状态**：active
- **批准日期**：2026-11-02
- **关联 Task**：`data-collection-business-clarification`
- **前置基线**：`hdf5-recording-format` v1.9、`unified-platform-integration-boundary` v1.6
- **用途**：作为后续数据采集链路实现的唯一业务基线；此前两份基线保留历史记录，后续实现以本文件为准。

## 1. 目标与参与者

目标是让相机、机器人状态、控制参考和任务元数据通过公共采集链路落盘为统一 HDF5；机器人差异由 RobotAdapter、机器人 YAML 配置和采集中间层承载，公共 recorder 不直接访问厂商 SDK，也不按型号分支。

- 操作员：创建/选择/查看/删除任务，选择机器人配置，开始、保存或废弃采集。
- RobotAdapter：访问具体机器人，声明可提供的标准字段，并上报标准数据。
- 采集中间层：提供封闭字段白名单、标准数据接口、校验和时间对齐入口。
- recorder/exporter：只消费中间层数据，按声明创建 HDF5 数据集。
- 下游：按 HDF5、manifest 和 episode 元数据读取数据。

## 2. HDF5 字段基准

字段名、键树、形状、单位和 attrs 以元文档为准；不得由单个构型新增、改名或修改。仅保留已批准的必要统一项：action 的 `eef_pose`、四元数顺序 `quat_order`，以及观测 `eef_pose` 与 action 对齐为 `(T,7)`、四元数 `xyzw`。

### 2.1 Action 白名单

```text
action/<side>/eef_pose       (T,7)  [x,y,z,qx,qy,qz,qw]
action/<side>/joint_position (T,J) float32，rad
action/<side>/gripper        (T,1) float32，m
```

- EEF pose 位置单位为米，四元数顺序为 `xyzw`。
- 机器人适配器可声明 EEF、joint 或两者；声明什么就落盘什么。
- 两者都未声明时，不创建 `/action`，`has_action=false`。
- 不把 EEF 反算为 joint，不把实测状态冒充 action，不用零值占位。
- 松开 Grip 后，若 adapter 仍保持上一实际控制目标，该 action 继续有效；这是 adapter 的持续控制状态，不是 recorder 自行复制。

### 2.2 Observation 白名单

```text
observation/state/<side>/joint_position  (T,J) float32，rad
observation/state/<side>/joint_velocity  (T,J) float32，rad/s，可选
observation/state/<side>/joint_effort    (T,J) float32，N·m，可选
observation/state/<side>/gripper         (T,1) float32，m
observation/state/<side>/eef_pose        (T,7) float32，m + quat xyzw
```

可选观测字段由 adapter 声明；未声明的数据集不创建。观测和 action 的 EEF pose 均需声明坐标系、TCP、TCP offset 和 `quat_order`；相机只写 `mount`、`serial`、`decoded_shape`，本阶段不写内外参。

## 3. 机器人配置与中间层

### 3.1 封闭字段契约

- 中间层提供抽象基类和集中注册的字段白名单。
- 新 adapter 必须继承该基类，只能声明白名单中的字段并按标准名、形状、单位上报。
- 越界字段在启动期失败；不得静默忽略、私自扩展或在 recorder 中推导。
- 字段白名单变更必须修改公共契约并升版本，不能由构型私自改变。
- 采集进程不直接调用 RobotAdapter，只消费中间层。

### 3.2 机器人 YAML 与设置页

- 为每个构型提供机器人配置模板，列出新增构型必须填写的字段。
- `robot_type`、`robot_model`：来自机器人 YAML，设置页只读。
- `robot_id`：来自机器人 YAML，设置页可修改，保存后回写 YAML；它是具体机器编号，不由目录名或型号推断。
- 每个有效臂配置 `frame_axes`：来自机器人 YAML，设置页只读；落盘到该臂 observation/action EEF pose attrs 的 `frame_axes`。
- 其他机器人连接、运动学、关节名、夹爪、TCP、坐标系和数据能力也由对应 YAML/adapter 提供；不得散落到公共页面。

## 4. Root attrs 来源

| attr | 来源 |
| --- | --- |
| `spec_version` | 固定 `inhouse-hdf5-v2` |
| `robot_type` / `robot_model` / `robot_id` | 当前选中机器人 YAML；type/model 只读，id 可修改 |
| `arms` | 当前选择的臂；单臂写 `main`，双臂写 `left/right` |
| `episode_id` / `batch_id` | 录制系统的 episode/batch 编号规则 |
| `task_id` / `task` / `scene` | 当前选中的任务 YAML |
| `collect_mode` | 固定 `teleop` |
| `has_action` | recorder 按实际创建的 action 数据集判断 |
| `fps_nominal` | 视频采集配置 |
| `num_frames` | recorder 实际主时间轴长度 |
| `operator` / `timezone` | 固定 `user` / `Asia/Shanghai` |
| `success` / `discarded` / `discard_reason` | 保留元文档字段；由 episode 保存/废弃结果表达，后续需要时再完善交互来源 |
| `sensors` | 实际相机配置和设备枚举，JSON 字符串 |
| 双臂 `base_extrinsics` | 机器人描述/标定；无法取得时为 `unknown`，不得猜测 |
| `project` | **不写进 HDF5**（元文档未在此定义）；由任务配置提供，只写批次 `manifest.json` |

## 5. 任务配置生命周期

- 采集页“新建任务”弹窗必须填写：任务名称、`task_id`、`task`、`scene`、`project`。
- `task` 是任务描述，使用较大的多行输入框。
- 任务名称只用于人员识别、任务列表和查看，不写入 HDF5 attrs。
- 保存后生成 YAML 任务配置，重启后可继续选择。
- 已保存任务可查看全部信息，但不可修改，只能删除。
- 删除任务配置不改写历史 episode 或 batch。
- 一个 batch 只能使用一套任务元数据；换任务创建新 batch。

## 6. 时间轴与正常数据流

- 主时间轴由真实相机同步帧组驱动，根下只有 `/timestamp`。
- 每个相机同步帧组对齐一行可用机器人状态和已声明 action；30/60Hz 必须由真实采集支撑，不复制、插值或伪造扩帧。
- `cam_dup` 及复制上一帧供插值的机制废弃。
- 缺失数据不补零、不复制、不伪造；真实全零值保留。

## 7. 落盘与 manifest

- episode 先写临时文件，完成写入后原子 rename；保留任务、batch、episode 元数据。
- manifest 按元文档字段；不写 `episodes[].success`、`episodes[].discarded`、`n_discarded`。
- episode 的 `success`、`discarded`、`discard_reason` 只保留在 episode root attrs。
- 本阶段暂不实现采集端自检和拒收逻辑；`_SUCCESS` 的最终封口判据暂不作为本轮实施项。
- 音频、language、action 在真正 hold/暂停/失控后的间歇缺失、不完整候选帧、历史 HDF5 兼容均暂缓。

## 8. 明确实施范围

### 本轮后续实现范围

1. 采集中间层抽象基类、封闭字段注册和 adapter 能力声明。
2. 机器人配置模板、字段权限、`robot_id` 编辑和 `frame_axes` 只读展示/传递。
3. 任务 YAML 的新建、选择、查看、删除和 episode 元数据快照。
4. 公共 recorder 按中间层声明写入统一 observation/action 字段。
5. 新 HDF5 键树、attrs、真实相机主时间轴和 manifest 基础落盘。

### 本轮不实施

- 真实机器人控制算法、限位、增益和安全参数调整。
- 相机内外参、音频、language。
- 采集端自检、拒收、最终 batch `_SUCCESS` 封口规则。
- 真实 hold/暂停/失控期间 action 缺失策略。
- 历史 HDF5 迁移或兼容读取。
- 真机运动验收；真机操作必须另行获得用户确认。

## 9. 变更控制

后续不得直接修改本基线中的字段或语义。新增字段、改名、改变 shape/单位、改变任务生命周期或改变缺失策略，必须形成新的变更候选，说明受影响的 adapter、中间层、recorder、HDF5、测试和历史兼容范围，经确认后升级基线版本。

## 10. 批准记录

- v1.0（2026-11-02）：用户确认最终业务范围，要求先归档和拆分任务，暂不开始代码修改。
