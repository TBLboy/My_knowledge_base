# 自采数据 HDF5 落盘规范

> 本 Markdown 由原 PDF 完整转写并结构化，目标是方便 Agent / LLM 直接阅读与解析。内容按原文组织，不主动补充、纠正或推断规范中未给出的信息。

## 1. 原则

1. HDF5 里存时间戳、逐帧 JPEG 和本体状态和 task。
2. 没有的数据就不写。**禁止用全 0 数组占位。** 缺字段可以直接判断出来，写了 0 只会被误当成真实数据。
3. 每个数都要带含义。单位、维度名、坐标系写在 attrs 里。
4. 所有数据共用一条主时间轴 `timestamp`。掉帧不补也不删。
   - 过去有一些断帧的情况，处理方式最好是复制上一帧。或者直接删除整个 ep。
5. 所有本体用同一套字段结构。下游只需要维护一个转换脚本，而不是每个本体一套。

## 2. 目标目录与命名

```text
obs://embodied-data/raw/inhouse/<形态>/<project>/<robot_id>/<task_id>/<batch>/
├── episode_000000_20261019_091232.hdf5
├── episode_000001_20261019_091510.hdf5
├── ...
├── manifest.json
└── _SUCCESS
```

- `<形态>`：`robo_real` / `umi`
- `<project>`：项目名，如 `forge_v1`、`lab_grasping`
- `<robot_id>`：具体机器编号，如 `arx5`、`piper3`。本体型号写在 attrs 里，不靠目录名推断。
- `<task_id>`：任务模板 ID（小写字母、数字、下划线），如 `cover_blocks`，必须在任务模板表里。一个 batch 只采一个 task，开始采集前在采集界面选定；换任务就开新 batch。
- `<batch>`：`YYYYMMDD_NN`，日期 = 这批第一条 episode 的采集日期（北京时间），NN 从 `01` 开始。禁止自由命名（如 `data_test_0922`）。
- 文件名：`episode_<6位补零>_<YYYYMMDD_HHMMSS>.hdf5`，编号在批次内从 0 连续递增，时间是 episode 开始时刻（北京时间）。
- 废弃的 episode：也要上传，只是在 attrs 里标 `discarded=true` 和 `discard_reason`。这样编号不会断档，断档能在清单里查到原因。
- 写入流程：先写 `.hdf5.tmp`，写完 rename 成 `.hdf5`，再上传。上传后计算 md5 写进 manifest。
- `manifest.json`：必须，见 §2.1。
- `_SUCCESS`：最后写；写了就封口，不再往这个 batch 追加。

### 2.1 manifest.json（批次级 batch 清单）

```json
{
  "spec_version": "inhouse-hdf5-v1",
  "project": "forge_v1",
  "robot_id": "arx5",
  "robot_type": "arx",
  "task_id": "cover_blocks",
  "task": "Put the green block on the red drum",
  "batch_id": "20261019_01",
  "operator": "zhangsan",
  "scene": "lab_a_table2",
  "episodes": [
    {
      "file": "episode_000000_20261019_091232.hdf5",
      "episode_id": 0,
      "num_frames": 705,
      "success": true,
      "discarded": false,
      "bytes": 106745520,
      "md5": "a1b2c3..."
    }
  ],
  "n_episodes": 1,
  "n_discarded": 0,
  "created_at": "2026-10-19T18:00:00+08:00"
}
```

- `md5`：采集端上传后算。下游拿 OBS 的 etag 或 md5 对账，能发现漏传和传坏。
- `episodes[]` 必须和目录里的 hdf5 文件一一对应，这是写 `_SUCCESS` 的前提。
- `task_id`：任务模板 ID，用于聚合统计；`task` 是完整的任务文本。

## 3. HDF5 键树（所有本体统一）

```text
/    root attrs（不是 dataset，完整列表见 §4）：
│    task_id, task, robot_type, robot_id, arms, collect_mode, has_action,
│    fps_nominal, num_frames ...
├── timestamp                         (T,)   float64     主时间轴，unix 秒（采集主机 CLOCK_REALTIME）
├── observation/
│   ├── state/
│   │   ├── left/                                      单臂写 main，双臂写 left/right
│   │   │   ├── joint_position        (T,J) float32 rad       attrs: names, unit
│   │   │   ├── joint_velocity        (T,J) float32 rad/s     可选
│   │   │   ├── joint_effort          (T,J) float32 N·m       可选
│   │   │   ├── gripper               (T,1) float32 m         开口宽度，越大越开
│   │   │   └── eef_pose              (T,D) float32           SDK 原样输出，attrs 声明数值约定（§3.1）
│   │   └── right/...
│   └── images/
│       ├── cam_head                  (T,)   vlen uint8        每行一张 JPEG
│       ├── cam_head_dup              (T,)   bool              掉帧后复制上一帧的标 true
│       ├── cam_wrist_left/...
│       ├── cam_wrist_right/...
│       └── cam_ext_<n>/...                                  外置相机，n=1,2,...
├── action/                                                  只有 has_action=true 时才写
│   ├── left/
│   │   ├── joint_position            (T,J) float32
│   │   └── gripper                   (T,1) float32
│   └── right/...
└── language/                                                可选，原始指令素材，语音预计后续不再采集
    ├── audio_pcm                      (N,1) int16             attrs: sample_rate, t0
    └── images/
        └── cam_head                   (M,)   vlen uint8       指令片段 attrs: t0
```

### 3.1 说明

- **禁止全 0 占位**：没有 action 就不写 `action/`；没有速度就不写 `joint_velocity`。
- **相机名固定**：`cam_head`（俯视或前视）、`cam_wrist_left`、`cam_wrist_right`、`cam_ext_<n>`（外置，n 从 1 开始）。
- **每路相机的 attrs 必须写**：`mount`（安装位置）、`serial`（序列号）、`decoded_shape`（解码后形状，如 `[480, 640, 3]`）。有标定就再写 `intrinsics`、`extrinsics`。
- **时间戳**：只有根下的 `timestamp` 一条主时间轴，不写每路相机各自的时间戳。
- **`<cam>_dup`**：掉帧后复制上一帧的标 `true`，用于下游判断是否要插值。
- **`eef_pose`**：末端位姿，转换端只能照 attrs 换算，所以 attrs 必须把数值约定写全：

| attrs | 示例 | 说明 |
|---|---|---|
| `names` | `x,y,z,roll,pitch,yaw` | 每一维的含义 |
| `unit_position` | `m / mm` | 位置单位 |
| `rot` | `euler / quat / rotvec / rotmat` | 旋转表示 |
| `euler_order` | `xyz` | 欧拉角轴序（`rot=euler` 时必填） |
| `euler_type` | `extrinsic / intrinsic` | 外旋还是内旋（`rot=euler` 时必填） |
| `quat_order` | `xyzw / wxyz` | 四元数分量顺序（`rot=quat` 时必填） |
| `unit_angle` | `rad / deg` | 角度单位 |
| `frame` | `base_link` | 参考系名称 |
| `frame_axes` | `x:forward,y:left,z:up` | 参考系轴向相对机器人本体的朝向 |
| `tcp` | `flange / fingertip_center` | 位姿描述的是哪个点 |
| `tcp_offset` | `[0,0,0.152]` | 该点相对法兰的偏移（m），能拿到就写 |
| `source` | `arx_sdk 2.3.1 FK` | SDK 名称、版本，FK 计算还是测量值 |

- 双臂另外在 root attrs 写 `base_extrinsics`（两臂基座之间的相对位姿）。任何一项拿不到就写 `unknown`，**不要猜一个值填上去**。
- `gripper`：开口宽度（m），越大越开。attrs 写 `unit=m`。
- `action/` 的 attrs 写 `source`：`leader`（主臂）/ `policy`（策略输出）/ `command`（外部指令）。

### 3.2 与 ARX schema v2 / Piper 旧版的对应关系

| v2 key | ARX schema v2 | Piper 旧版 ACT |
|---|---|---|
| `timestamp` | `robot/timestamp` | `observations/frame_time` |
| `observation/state/left/joint_position` | `robot/follower_left/position[:, :6]` | `observations/qpos[:, :6]` |
| `observation/state/left/gripper` | `robot/follower_left/gripper` | `observations/qpos[:, 6]` |
| `observation/state/left/eef_pose` | `robot/follower_left/eef[:, :6]` | `observations/eef_pose[:, :7]` |
| `observation/images/cam_head` | `observations/images/cam_high` | `observations/images/cam_high` |
| `action/left/*` | 不写（拖拽，没有 action） | `action[:, :7]`，attrs `source=leader` |
| `language/audio_pcm` | `audio/pcm` | 无 |

## 4. root attrs

> 原文标注：**✅ 必填**。

| key | 示例 | 说明 |
|---|---|---|
| `spec_version` ✅ | `inhouse-hdf5-v1` | 本规范版本 |
| `robot_type` ✅ | `arx` | 本体类型（小写） |
| `robot_model` ✅ | `ARX（方舟无限）` | 本体型号（人类可读） |
| `robot_id` ✅ | `arx5` | 具体机器编号 |
| `arms` ✅ | `left,right` | 逗号分隔；单臂写 `main` |
| `episode_id` ✅ | `76` | 和文件名、manifest 对上 |
| `batch_id` ✅ | `20261019_01` | 和目录名对上 |
| `task` ✅ | `Put the green block on the red drum` | 任务文本（必填） |
| `task_id` ✅ | `cover_blocks` | 任务模板 ID，便于聚合统计 |
| `collect_mode` ✅ | `drag / teleop / policy` | 采集方式（拖拽/遥操作/策略） |
| `has_action` ✅ | `false` | 是否有 `action/` |
| `fps_nominal` ✅ | `30` | 标称帧率；实测帧率由下游从时间戳算 |
| `num_frames` ✅ | `705` |  |
| `operator` ✅ | `zhangsan` | 操作员 |
| `scene` ✅ | `lab_a_table2` | 场景 |
| `success` ✅ | `true` | 是否成功 |
| `discarded` ✅ | `false` | 是否废弃 |
| `discard_reason` ✅ | `""` | 废弃原因（`discarded=true` 时必填） |
| `timezone` ✅ | `Asia/Shanghai` | 时间戳时区 |
| `sensors` ✅ | JSON 字符串 | 每路相机的 model、serial、分辨率、mount |

**task 怎么填：** 开始一个 batch 前，在采集界面从任务模板里选（写入 `task_id + task`），而不是自由输入；整个 batch 的每条 episode 都写同一个值。

**sensors 示例：**

```json
{
  "cam_head": {
    "model": "MV-CA016-10UC",
    "serial": "JE123456",
    "width": 640,
    "height": 480,
    "mount": "head"
  },
  "cam_wrist_left": {
    "model": "...",
    "serial": "...",
    "width": 640,
    "height": 480,
    "mount": "left_wrist"
  }
}
```

## 5. 采集端自检

以下任何一条不通过，拒收该 episode，不能上传。

> 原文备注：需要评估一下具体是否需要格式检查一下自采源数据。

| # | 检查项 | 不通过就 |
|---:|---|---|
| 1 | 所有必填 attrs 都存在且非空 | 拒收 |
| 2 | `task` 非空，`task_id` 在任务模板表里 | 拒收 |
| 3 | `episode_id` 和文件名一致 | 拒收 |
| 4 | `num_frames` 和 `timestamp` 的行数一致 | 拒收 |
| 5 | 任何一个数值 dataset 都不能整列全是 0（`has_action=false` 时不能有 `action/`） | 拒收 |
| 6 | `timestamp` 严格递增，没有重复 | 拒收 |
| 7 | 所有 `observation/state/*/` 下的 dataset 行数和 `timestamp` 一致 | 拒收 |
| 8 | 所有 `observation/images/<cam>` 行数和 `timestamp` 一致 | 拒收 |
| 9 | 每路相机的 attrs 包含 `mount`、`serial`、`decoded_shape` | 拒收 |
| 10 | 每个 JPEG 能解码，解码后形状和 attrs 里的 `decoded_shape` 一致 | 拒收 |
| 11 | 用时间戳算出的实测帧率和 `fps_nominal` 相差 >10%，或者相邻帧间隔 `>3/fps` 的帧占比 >1% | 告警，并写进 manifest 的 `warnings` |
| 12 | 和同批、相邻批次的文件 md5 不重复 | 拒收 |
| 13 | root attrs 的 `task_id`、`task` 与 manifest 批次级字段一致，且 `task_id` 等于所在 `<task_id>/` 目录名 | 拒收 |

**检查 11 说明：** 针对 piper 只有 10–23 fps 的情况，实测帧率不稳定时要告警。

**检查 12 说明：** 针对 `arx1/dual_fix` 整份重复上传的情况，按 md5 查重。

---

**以下内容与采集侧无关。**

## 6. 数据侧 转换

- 转码（JPEG → H.264）。
- 采集侧继续存 JPEG。数据侧拿到 HDF5 后，把图片转成 H.264 mp4，体积降到约 1/5。

### 6.1 转码参数

```bash
# <cam>.mjpeg = 把 observation/images/<cam> 的 T 行 JPEG 字节按顺序直接拼起来
ffmpeg -v error -y -f mjpeg -framerate 30 -i cam_head.mjpeg \
  -c:v libx264 -g 8 -keyint_min 8 -sc_threshold 0 -bf 0 -crf 20 -preset medium \
  -vf scale=in_range=full:out_range=tv -pix_fmt yuv420p -color_range tv \
  -r 30 -movflags +faststart cam_head.mp4
```

- **GOP=8**：`-g 8 -keyint_min 8 -sc_threshold 0` 三个都要给，否则 x264 会在场景切换时自己插 I 帧。
- **无 B 帧（`-bf 0`）**：解码顺序等于显示顺序。
- **crf20 / medium**。
- **像素格式**：`yuv420p` limited range，显式做 full→tv 转换。**禁止只写 `-pix_fmt yuv420p -color_range pc`**（实测画面偏暗、PSNR 掉 12 dB）。
- **帧数**：每个 mp4 的帧数必须等于 T。
- 结束后可做基础测速。

### 6.2 转码后的目录结构

```text
<batch>/
├── episode_000000_20261019_091232.hdf5
├── videos/
│   ├── episode_000000/
│   │   ├── cam_head.mp4
│   │   ├── cam_wrist_left.mp4
│   │   └── cam_wrist_right.mp4
│   └── episode_000001/...
└── manifest.json
```
