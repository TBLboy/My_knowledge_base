# LeRobot v3 数据格式约定（用户提供，V1.0）

> **来源与权威性**：用户于 2026-10-16 在本会话提供的完整需求文本。本文是当前 Franka/Pico 数据采集系统最终离线导出、QC 与训练 dataloader 的语义契约。此文件是根据会话中用户粘贴的富文本进行的 Markdown 转录；原文中标为“暂时无法在飞书文档外展示”的可选字段内容并未出现，因而无法在此复原。除该原文不可见部分外，文件保留提供的规则与结构。
>
> **适用范围**：`LeRobot codebase_version = v3.0`。

## 已确认的要点摘录（用于实现前澄清，不替代完整原文）

- 固定的 `data/`、`meta/`、可选 `videos/` 目录布局；视频存在时必须输出 MP4 引用。
- `custom.action_space` 必填，允许值包括：`joint_position_absolute`、`eef_pose_absolute`、`eef_pose_delta_base`、`joint_velocity`。
- `action.eef_pose` / `observation.state.eef_pose` 的定义为单臂 `[x,y,z,qx,qy,qz,qw]`，shape `[7]`；双臂 `[14]`。
- state/action 特征不是全都必填；手持设备可合法缺少 joint_position，且不得补零伪造。
- action/state 特征必须忠实表达实际物理语义；gripper 独立，不可追加到 joint_position。
- 深度、点云等非 RGB 模态转换时跳过。
- 自定义平台信息写 `info.json.custom`；官方 loader 忽略未知 custom 字段。

## 完整需求原文

以下内容根据用户消息转录并按 Markdown 组织；未擅自新增业务规则。

---

### §0 定位与目标

本文档是 LeRobot v3 数据格式的最终规范（主要是对语义进行了更加细粒度的规范），供以下三方使用：

- 数据侧：将各来源原始数据转换为 v3 格式的工具
- 质检侧（QC）：验证数据集合规性
- 训练侧：加载数据进行模型训练的 dataloader

三方对着同一份契约开发，不再需要同时参考草案和调查报告。

### §1 目录结构

```text
{unit}/
├── data/
│   └── chunk-{i:03d}/              # i 从 0 起，每 chunk 最多 chunks_size 个 episode
│       └── file-{j:03d}.parquet    # j 为 chunk 内局部序号，从 000 起
├── meta/
│   ├── info.json                   # 必须，数据集总纲
│   ├── stats.json                  # 必须，归一化统计
│   ├── tasks.parquet               # 必须，任务语言描述表
│   ├── {robot}.urdf                # 可选，机器人 URDF 模型
│   └── episodes/
│       └── chunk-000/
│           └── file-000.parquet
└── videos/
    └── observation.images.{cam_key}/
        └── chunk-{i:03d}/
            └── file-{j:03d}.mp4
```

必须存在：`data/`、`meta/info.json`、`meta/stats.json`、`meta/tasks.parquet`、`meta/episodes/`。有视频时必须存在 `videos/`。

打包上限：`chunks_size=1000` files/chunk；data parquet `100MB`/文件；MP4 `200MB`/文件；单 episode 不跨文件。

### §2 逐文件精确 Schema

#### §2.1 `data/chunk-*/file-*.parquet`

固定列：`timestamp(float32, episode 内从 0 秒起)`、`frame_index(int64)`、`episode_index(int64)`、`index(int64)`、`task_index(int64)`。

State/action 采用 float32 list。标准特征：

| 列 | 单臂 shape | 语义 |
| --- | --- | --- |
| `observation.state.joint_position` | `[DoF]` | rad |
| `observation.state.eef_pose` | `[7]` | m + xyzw quaternion |
| `observation.state.gripper` | `[1]` | 原始物理值 |
| `observation.state.hand_joints` | `[DoF]` | 灵巧手时与 gripper 互斥 |
| `action.joint_position` | `[DoF]` | rad |
| `action.eef_pose` | `[7]` | m + xyzw quaternion |
| `action.gripper` | `[1]` | 原始物理值 |
| `action.hand_joints` | `[DoF]` | 灵巧手时与 gripper 互斥 |

视频列为 `observation.images.{cam_key}`，存 `{path: string, timestamp: float32}` 引用，不存像素。行按 `episode_index ASC, frame_index ASC`。深度、点云及其他非 RGB 特征不写入。

#### §2.2 `meta/episodes/chunk-000/file-000.parquet`

固定列：`episode_index`、`tasks(list[string])`、`length`、`data/chunk_index`、`data/file_index`、`meta/episodes/chunk_index`、`meta/episodes/file_index`、`dataset_from_index`、`dataset_to_index`。视频时每路相机追加 `videos/{full-video-key}/chunk_index`、`file_index`、`from_timestamp`、`to_timestamp`；时间范围为左闭右开，实际 PTS 必须覆盖恰好 `length` 帧。

#### §2.3 `meta/tasks.parquet`

任务文本为 pandas index，index 名称为 `task`；唯一普通列 `task_index:int64`。任务文本去重；`task_index` 连续。

#### §2.4 `meta/info.json`

核心字段：`codebase_version="v3.0"`、`robot_type`、`fps:int`、总 episode/frame/task/chunk 数、`chunks_size`、文件大小上限、`splits`、`data_path`、`video_path`、`features`、`custom`。

5 个隐式 feature key 必须为：`timestamp`、`frame_index`、`episode_index`、`index`、`task_index`。其 `names=null`；其余特征的 `names` 非 null，且长度等于最后一维。

`eef_pose` names 为 `["x","y","z","qx","qy","qz","qw"]`；视频特征为 `[C,H,W]`，names `["channel","height","width"]`，带实际 fps/codec/pix_fmt/`is_depth_map:false` 信息。

`custom` 保存平台扩展；`custom.action_space` 必填，详见 §5。

#### §2.5 / §2.6 / §2.7

`meta/robot.urdf` 可选、单一自包含 URDF；`stats.json` 只统计 `action.*` 与 `observation.state.*`，含 mean/std/min/max/q01/q10/q50/q90/q99/count，统计为 float64。视频保留原 codec；单 episode 不跨 MP4；随机访问平均 <50ms。

### §3 字段语义规范

标准前缀：`observation.state.*`、`observation.images.*`、`action.*`。禁止：将 gripper 追加到 joint_position；拆成 left/right 独立顶级 action feature；使用 `gripper_position` 作为最终字段名。

`joint_position` 使用 rad；`eef_pose` 总是 `[x,y,z,qx,qy,qz,qw]`、位置 m、四元数 xyzw；`gripper` 用原始物理值并由 custom 声明范围/方向/单位；单臂不 padding。

### §4 相机词表

- `cam_head_N`：非鱼眼头部相机。
- `cam_wrist_left` / `cam_wrist_right`：左右腕相机。
- `cam_wrist_fisheye_left` / `cam_wrist_fisheye_right`：腕部鱼眼。
- `cam_ext_N`：外置/非标准挂载；方向优先 `0=front, 1=left, 2=right, 3=top`。
- `cam_aux_N`：位置/用途无法确认。

所有映射转换前必须人工视频核验，最终映射写入 `custom.camera_key_map`；converter 不自动推断。

### §5 custom 扩展字段

`custom.action_space` 必填，枚举：

| 值 | 含义 |
| --- | --- |
| `joint_position_absolute` | action 为关节绝对角度 |
| `eef_pose_absolute` | action 为末端执行器绝对位姿 |
| `eef_pose_delta_base` | action 为相对基座的末端位姿增量 |
| `joint_velocity` | action 为关节速度 |

有 gripper 时 `custom.gripper` 必含：`range:[closed,open]`、`open_direction`、`unit`。`custom.camera_key_map` 可选。UMI 手持设备特殊规则：`robot_type=umi_handheld`、`eef_frame=slam_world`；无 joint_position 合法，禁止填零。

### §6 视频编码规范

保留原始 codec；GOP=2；`info.json` 声明的 fps/codec 必须与实际 MP4 一致；深度视频不写入。

### §7 质量校验清单

数据集必须检查：目录与 JSON、总数与实际一致、feature names/shape/dtype、合法 `custom.action_space`、独立 gripper、stats 统计、任务索引、相机合法槽位与映射、视频 PTS/帧数/随机访问、episode 范围与 data 排序等。完整检查以用户在本会话提供的 §7 清单为准。

### 附录：弃用

弃用 `gripper_position`、`cam_chest`、`is_fisheye`、gripper 拼接 joint_position、left/right 独立顶级 feature、强制 action 转 H264，以及 imu/下肢/depth/point-cloud 等非本契约模态。
