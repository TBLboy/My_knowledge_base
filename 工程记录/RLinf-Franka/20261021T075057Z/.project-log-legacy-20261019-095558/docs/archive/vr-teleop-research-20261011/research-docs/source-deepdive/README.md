# 第二阶段源码深挖 · 索引与候选矩阵

> **状态**：`R-002` 进行中，2026-10-11（第二轮：用户指令「继续深挖全部」）。
> **性质**：**L2（源码可证）级**的候选评估。**不含 L3/L4**（无真机证据、无我方实测）。
> **覆盖**：**22 个本地克隆**中的 **19 个**做了源码级深挖。
> （`teleimager` / `dex-retargeting` 仅到「结构 + 许可证」层；`televuer` 已逐文件精读。其余 3 个非克隆项见 §5。）

---

## 1. 深挖文档索引

| 文档 | 覆盖项目 | 关键产出 |
| --- | --- | --- |
| [`franka-vr-teleop.md`](franka-vr-teleop.md) | `wengmister/franka-vr-teleop` | **契约 C 的答案 = 末端位姿**；正则文本输入层（反面教材）；9 条安全机制清单 + 缺 watchdog |
| [`lerobot_ur_dual_vrteleop.md`](lerobot_ur_dual_vrteleop.md) | `scy-v/lerobot_ur_dual_vrteleop` | **`control_space` 参数化契约 C**；**URDF + YAML 驱动 = 可组合性的分水岭**；**"UR7e" 之谜解开（实为 UR5e）** |
| [`isaacteleop.md`](isaacteleop.md) | `NVIDIA/IsaacTeleop` | **PICO/Quest 共用同一后端（无厂商分支）**；**双时钟时间戳契约**；代价 = CloudXR 专有 + GPU + Linux |
| [`xrobotoolkit.md`](xrobotoolkit.md) | `XRoboToolkit` 三仓库 | **XR 契约无权威 schema（透传）**；协议内三种时间基准；Quest 客户端是裁剪分支；含 Unity 限制性条款 |
| [`lbx-Franka-Teach.md`](lbx-Franka-Teach.md) | `Labelbox/lbx-Franka-Teach` | **"DROID 兼容"不成立**；40Hz/6.6Hz 真实来源；依赖目录全空；含明文凭据；主机墙钟单点时间戳 |
| [`lerobot-plugins.md`](lerobot-plugins.md) | `lerobot_franka_teleop` + `lerobot_robot_piper` | **LeRobot 契约 = 特征名字典**（不二选一）；**插件注册零改动本体**；franka 是分层反面教材 |
| [`piper.md`](piper.md) | `PiperPilot` + `pico-piper-teleop` | **动作空间必须统一在 EEF 层**；`PiperPilot` = 唯一 MIT 且可直接复用；pico 许可硬阻断 + 关限位风险 |
| **⭐ [`televuer-xr-input.md`](televuer-xr-input.md)** | `unitreerobotics/televuer`（**本轮补克隆**） | **① 层契约最可读的候选**（32 字段 dataclass + MIT）；★ **「失联保护是假的」**（`motion_data_ready` 是闩锁） |
| [`xr_teleoperate.md`](xr_teleoperate.md) | `unitreerobotics/xr_teleoperate` | **XR 只输出 SE3、IK 在机器人侧**（与 `PiperPilot` 互相印证）；无 `control_space`；**手部「fail-hold」修正为「无保护」** |
| [`isaac_ros_teleop-television.md`](isaac_ros_teleop-television.md) | `isaac_ros_teleop` + `OpenTeleVision/TeleVision` | ★ **`isaac_ros_teleop` 不是绕过 CloudXR 的路径，而是 CloudXR 的更深封装**；`TeleVision` 降级 `reference-only` |
| [`quest-input-line.md`](quest-input-line.md) | `quest-wrist-tracker` + `quest2ros` + `Quest2ROS2` | Quest 手部线：**HTS 是更干净的 Quest 手部源**（但只有手、无按钮）；`quest2ros` 无许可证结案 |
| [`dextelegym.md`](dextelegym.md) | `zhourui9813/DexTeleGym` | **三重许可问题**（无授权 + 内嵌专有 Isaac Gym + 抹掉上游 Apache 声明）→ **代码不可采用** |

---

## 2. ★ 改变了原判断的发现

### 2.1 `OQ-001`（契约 C）从「二选一」变成了「四条路」

| 方案 | 契约形态 | 真机先例 | 跨机器人数据集可合并？ |
| --- | --- | --- | --- |
| **A. 输出关节角** | `{arm}_joint_{i}.pos` | `lerobot_ur_dual_vrteleop`（Placo + URDF）、`pico-piper-teleop` | ❌ **自由度不同（Franka 7 / Piper 6 / UR 6）→ 不可合并** |
| **B. 输出末端位姿** | `arm_eef: 7` | `franka-vr-teleop`（IK 在 C++ 侧）、**`PiperPilot`**、**`xr_teleoperate`/`televuer`（4×4 SE3）**、**`IsaacTeleop`（`NamedPoseArray`）** | ✅ **6-DoF 通用** |
| **C. 参数化控制空间** | 配置项 `control_space` | `lerobot_ur_dual_vrteleop`（`joint`/`cartesian`/`force`） | ⚠️ 取决于配置 |
| **D. 声明式契约** | LeRobot 特征名字典（插件自声明） | `lerobot_robot_piper` / `lerobot_franka_teleop` | ⚠️ 取决于各插件声明 |

> **★ 本轮最强架构输入**：**若「面向模型训练的数据采集闭环」是核心目标，动作空间必须落在末端位姿层**（或至少在数据集层面统一到 EEF）。**关节角路线在三种机器人间无法合并数据集**——这是 `PiperPilot`（EEF）与 `pico-piper-teleop`（关节角）的直接对照结论。
> **本轮新增旁证（2 条独立证据）**：
> - `televuer` 的 `TeleData` 直接以 **`left_wrist_pose` / `right_wrist_pose` = (4,4) SE(3)** 为输入契约（`tv_wrapper.py:176-177`）；
> - `IsaacTeleop` 的 ROS 契约以 **`NamedPoseArray`（命名 EE 位姿 + `is_valid`）** 为首要输出（`teleop_ros2`）。
> → **「XR 层输出末端位姿、机器人差异下沉到 IK」已在 4 个独立实现中被工程验证。**
> **推荐组合**：**B（契约在末端位姿层）+ D（用 LeRobot 特征字典做声明式承载）+ C（适配层声明其支持的控制空间）**。

### 2.2 「时间同步」不是空白——`IsaacTeleop` 有成熟契约

`timestamp.fbs:10-27` 的 `DeviceDataTimestamp`：

| 字段 | 用途 |
| --- | --- |
| `sample_time_raw_device_clock` | **设备原始时钟** → 可与相机曝光对齐 |
| `sample_time_local_common_clock` | **本地公共时钟** → 多路融合基准 |
| `available_time_local_common_clock` | 数据可用时刻 |

对比：`lbx-Franka-Teach` 是**主机墙钟单点**；`franka-vr-teleop` **无时间戳字段**；`pico-piper-teleop` 有三个时间戳字段但未与相机硬件对齐。
**本轮新增**：`xr_teleoperate`/`televuer` 的 `TeleData` **完全无时间戳字段**（`tv_wrapper.py:173-225`），其 `episode_writer` 的 item 也只有 `idx`（`episode_writer.py:133-142`）→ **XR 时间戳未写入数据集**。

→ **`OQ` 里"时间同步"这项不再是空白设计，有现成契约可参照。**

### 2.3 「失联保护」在所有先例中都缺失——**必须是我们的增量**（**本轮加强**）

| 项目 | 失联行为 |
| --- | --- |
| `franka-vr-teleop` | **无 watchdog**；持有最后目标 → "fail-hold" |
| `lerobot_ur_dual_vrteleop` | **无 watchdog**；IK 异常返回上一关节角 |
| `PiperPilot` | ✅ 0.25 s 无新位姿 → `_disengage`，但**不再发新指令、固件保持最后目标** |
| `pico-piper-teleop` | ✅ 反馈 0.10 s 超时 → `unsafe_stop` + `raise`，且 **finally 中不回位、不释放扭矩** |
| `XRoboToolkit` | ✅ 20 s 无心跳判离线（但这是**连接层**心跳，非控制层安全） |
| `IsaacTeleop` | 空 handle = 无样本（契约层），但**应用侧安全未提供** |
| **`xr_teleoperate`（本轮）** | ❌ **臂：无条件执行 IK，零检查**；❌ **手：`motion_data_ready` 是闩锁（置 True 后永不复位）→ `if` 恒真 → 语义无效** |

> ★★ **本轮最强安全发现**：`televuer` 的 `motion_data_ready` 注释即写明 *"True after the **first** ... event"*，且 `televuer.py` 全文**无任何复位点、无 stale/timeout 逻辑**；所有 XR 回调体被 `except: pass` 包裹（`:226-227, 267-268, 315-316`）。
> → **`xr_teleoperate` 的失联保护 = 0（臂）+ 语义无效（手）**，是**「看起来有、实际没有」**的典型陷阱。
> → **P1 的"失联保护"通过判据必须我们自己实现**，且需要区分**输入失联**（XR 掉线）与**反馈失联**（机器人无反馈）两类；**验收必须能证明「断流 N ms 后行为符合预期」，而不是「代码里有 `if xxx_ready`」**。

### 2.4 ★★ `isaac_ros_teleop` 不是绕过 CloudXR 的路径——**它是 CloudXR 的更深封装**

| 证据 | 位置 |
| --- | --- |
| submodule 指向 `NVIDIA/IsaacTeleop` | `.gitmodules:1-4` |
| 安装 **`isaacteleop[cloudxr,retargeters]`** | `isaac_teleop_core/CMakeLists.txt:131` |
| 默认 `-DENABLE_CLOUDXR_BUNDLE_CHECK=ON` | 同上 `:43` |
| launch 暴露 **`cloudxr_accept_eula`** | `launch/isaac_ros_teleop.launch.py:152` |
| `package.xml` 自述 *"wraps IsaacTeleop as a ROS 2 package"* | `isaac_teleop_core/package.xml:25` |

→ **「用 ROS 绕开 CloudXR」这条假设不成立**；`isaac_ros_teleop` 与 `IsaacTeleop` 属**同一输入层**（前者是后者的打包），**不应计为两个独立候选** → **① 层独立候选池减少一个**。

### 2.5 ★ ① 层「契约可读性」出现了明显分层（本轮新增判据）

| 候选 | 契约形态 | 可读性 |
| --- | --- | --- |
| **`televuer`** | **可读 dataclass**（32 字段，含单位/轴向注释） | ★★★ **最好** |
| `IsaacTeleop` | FlatBuffers schema（有 IDL，但需工具链） | ★★ 好 |
| `XRoboToolkit` | 透传 JSON（**无 schema 文件**） | ★ 差 |
| `isaac_ros_teleop` | ROS msg（`NamedPoseArray` 含 `is_valid` 语义） | ★★ 好（**但绑定 CloudXR**） |

→ **`televuer` 与 `IsaacTeleop` 是契约质量的两个正面极；`XRoboToolkit` 是反面极。**
→ ★ **值得抄的具体契约设计**：① `NamedPoseArray` 的 `name/pose/is_valid` 三元组（**无效数据显式表达**）；② `televuer` 的 `thumbstickValue` 轴向图注释（front=(0,-1)…）；③ `televuer` 的 `arm_reference_mode`（**坐标帧契约参数化**）。

---

## 3. 候选矩阵（层 × 契约 × 候选 × 复用强度 × 许可证 × 证据级）

### ① XR 输入层

| 候选 | 输出契约 | 复用强度 | 许可证 | 证据级 | 关键依据 / 代价 |
| --- | --- | --- | --- | --- | --- |
| **`NVIDIA/IsaacTeleop`（DeviceIO）** | **FlatBuffers schema**（head/hand/controller/fullbody/se3/joint_state）+ **双时钟** | **`wrapper-adapter`（首选）** | **Apache-2.0**（REUSE 合规） | **L2** | ★ **PICO/Quest 共用同一后端，无厂商分支**；代价：**唯一 live 路径绑定 CloudXR（专有许可 + GPU + 官方仅 Linux）** |
| **`XRoboToolkit`（PC-Service + Pybind + `xr_msgs`）** | 透传 JSON（**无权威 schema**）+ `xr_msgs/Custom`（**仅 head+controller**） | **`wrapper-adapter`** | Apache-2.0 / MIT（⚠️ `THIRD_PARTY_NOTICE` 含 Unity 限制条款；**Qt 许可未声明**） | **L2** | 轻、跨平台、无 GPU；**唯一「单厂商双设备」候选**；代价：契约无 schema、三种时间基准、Quest 客户端功能裁剪 |
| **⭐ `unitreerobotics/televuer`** | **可读 dataclass**：`head_pose` / `left/right_wrist_pose` = **(4,4) SE(3)**、手部 (25,3)、控制器模拟量 | **`wrapper-adapter`** | **MIT** ✅ | **L2** | ★ **契约最可读**；独立 pip 包 + 依赖方向干净；`arm_reference_mode` 坐标帧参数化；**代价**：无 IDL/schema 文件、显示耦合、**无失联保护**、**无原生 App（走 Vuer WebXR，采集策略不可定制）** |
| `wengmister/quest-wrist-tracker`（**HTS**） | Quest 手部：**UTF-8 CSV**（21 关节**腕相对** + 手腕 6DoF + 可选头 6DoF） | **`wrapper-adapter`**（**仅 Quest 手部子路径**） | **Apache-2.0** ✅ | **L2** | ★ 零 PC 依赖、许可证最干净；**代价：完全无按钮/控制器、默认无时间戳、仅 Quest、依赖 Meta 专有 SDK** |
| `isaac_ros_teleop` | ROS `NamedPoseArray`（含 `is_valid`） | **`reference-only`** | Apache-2.0 外壳 + **CloudXR EULA** | **L2** | ❌ **与 `IsaacTeleop` 同一输入层（打包层），不解决 CloudXR** |
| **自研** | 带版本 + 带单位 + 统一时间基准的显式 schema + **`FrameCalibration` 契约** | **`custom`** | — | — | 若要同时摆脱 CloudXR 与"无 schema"两个代价 |

> **取舍轴（本轮扩展为三极）**：
> - `IsaacTeleop` = 契约强（IDL）**但 runtime 最贵**（CloudXR + GPU + Linux）
> - `televuer` = **契约可读 + MIT + 最轻**，**但无原生 App、无失联保护**
> - `XRoboToolkit` = **唯一双设备（PICO+Quest）**，但契约最弱
> **共同结论**：三者都只应作 **wrapper-adapter**——**契约层须自建**。
> **未闭合**：**PICO parity** 目前只有 `XRoboToolkit` 单边证据；`televuer`/`TeleVision` 走 WebXR（架构上不写死设备，但 **PICO 零证据**）。

### ② tele 核心层（映射 / clutch / 滤波 / 坐标变换 / IK 调度）

| 候选 | 输出契约 | 复用强度 | 许可证 | 证据级 |
| --- | --- | --- | --- | --- |
| **（生态无独立实现）** | — | **`custom` 自研** | — | **L2 已证实**：被内嵌在各家 ① 或 ③，切面位置各不相同 |

**参考实现（均 `reference-only`，但机制值得抄）**：

| 参考 | 输出契约 | 许可证 | 证据级 | 可抄什么 / 不可抄什么 |
| --- | --- | --- | --- | --- |
| `franka-vr-teleop` 的 ROS2 节点 | 末端位姿 | 授权不清晰 | L2 | ✅ clutch 重锚、渐进激活、死区、工作空间截断、Slerp 姿态滤波；❌ **坐标变换硬编码**、正则解析输入、**无 watchdog** |
| `lerobot_ur_dual_vrteleop` 的 `VRTeleop` | 关节角 + `ee_delta` | 无文件（1 文件 Apache 头） | L2 | ✅ **URDF + Placo 驱动**、**配置化坐标变换**（`R_headset_world`）、`scale_factor`、**`control_space` 参数化**、clutch 时重置 IK 目标 |
| `lerobot_franka_teleop` 的 `OculusRobot` | `delta_ee_pose` | 无文件（源码头 Apache） | L2 | ❌ **反面教材**：输入层反向依赖机器人层 + **IK 内嵌在输入层** |
| **`PiperPilot` 的 `TeleopController`** | `pose6` | **MIT** | L2 | ✅ **100 Hz + 完整笛卡尔包络 + `LimitTracker`**；⚠️ **急停是死代码** |
| **`televuer` 的 `arm_reference_mode`**（本轮） | 坐标帧选择（`head_position` / `head_yaw`） | **MIT** ✅ | L2 | ✅ **坐标帧契约参数化**（与 `R_headset_world`、`PiperPilot` 锚点标定**互为独立解法**）；✅ `thumbstickValue` 轴向图注释 |
| **`Quest2ROS2` 的 `robot_arm_controller_base.py`**（本轮） | 位姿 + inputs → `target_frame` | **Apache-2.0** | L2 | ✅ clutch/anchor 重锚（`:355-381`）、移动平均滤波（`:166-208`）、`GripperCommand` action；❌ **机器人侧硬编码 kuka/bh_robot → 不可组合** |

> ★ **可组合性的判据**：**「URDF + YAML 配置驱动」才叫可组合；硬编码坐标系与机型参数的实现，无论多强都不可组合。**
> ★ **坐标帧已出现三种独立解法**（`PiperPilot` 持久锚点 + 两点 X 轴标定 / `lerobot_ur_dual_vrteleop` 配置化 `R_headset_world` / `televuer` `arm_reference_mode`）→ **`FrameCalibration` 必须是显式一等公民契约。**

### ③ 机器人输出适配层

| 目标机型 | 候选 | 控制方式 | 复用强度 | 许可证 | 证据级 |
| --- | --- | --- | --- | --- | --- |
| **Piper** | **`PiperPilot` `ArmBase`** | **位姿（`move_p`）或关节（MIT 阻抗）双空间** | **★ `direct-use`** | **MIT** ✅ | L2 |
| Piper | `pico-piper-teleop` | 关节角（宿主 Placo IK） | `reference-only` | ❌ **无许可证** | L2 |
| Franka | `franka-vr-teleop` C++ | 关节速度（1 kHz + Ruckig + GeoFIK） | `reference-only` | 拼贴（Franka Apache 头 + GeoFIK 上游 Apache + 无署名 MIT 文本） | L2 |
| Franka | `lbx-Franka-Teach`（deoxys） | `OSC_POSE` | `reference-only` | 无文件（README 自述 MIT） | L2 |
| Franka | `lerobot_franka_teleop`（Polymetis + zerorpc） | 关节/`delta_ee_pose` | `reference-only` | 无文件 | L2 |
| Franka | **`xr_teleoperate`（本轮）** | ❌ **不适用** —— 全部是 Unitree 整机（G1/H1/H2/R1），`grep franka\|piper\|ur5` = 0 | **`reference-only`（仅架构）** | Apache-2.0（⚠️ 依赖 `casadi` LGPL-3.0，待确认） | L2 |
| UR | `lerobot_ur_dual_vrteleop` `ur.py` | RTDE `servoJ`（按 `control_space` 分支） | `reference-only` | 无文件 | L2 |

> **Piper 是唯一有 `direct-use` 选项的机型**（`PiperPilot` MIT）。**Franka 与 UR 全部只能 `reference-only`。**
> **本轮新增**：`xr_teleoperate` 虽有 1697★，但对 Franka/Piper/UR **零直接可复用代码** → **不得当作 Franka 方案候选**，只作架构参考。
> 这给"垂直切片选型"一个反直觉的提示：**从 Piper 起步的技术成本最低，但从 Franka 起步符合业务优先级** —— 这个矛盾需要在 `OQ` 层面决策。

### ④ 数据记录层

| 候选 | 格式 | 复用强度 | 许可证 | 证据级 | 关键依据 |
| --- | --- | --- | --- | --- | --- |
| **`huggingface/lerobot` 本体** | LeRobot v2.x | **★ `direct-use`** | **Apache-2.0** | L1/L2 | 官方 CLI（`lerobot-record`）可避免钉死 commit |
| **`PiperPilot` `LeRobotWriter`** | **LeRobot v2.0 + GR00T modality + provenance** | **★ `direct-use`** | **MIT** ✅ | L2 | ★ **最完整的可复用数据层**：`modality.json`、**provenance 绑定控制参数**、绝对 EEF 动作、parquet+mp4 同源时间轴 |
| `lerobot_ur_dual_vrteleop` `run_record.py` | LeRobot + **VR 按键驱动状态机** | `reference-only` | 无文件 | L2 | ✅ A/X/Y/菜单键驱动采集流程；✅ 异常进回收站；✅ episode 间强制回位 |
| `lbx-Franka-Teach` `mcap_data_recorder.py` | **自定义 `labelbox_robotics` MCAP** | `reference-only` | 无文件 | L2 | ❌ **"DROID 兼容"不成立**；❌ 主机墙钟单点时间戳；✅ 回读校验、有界队列丢帧策略 |
| `pico-piper-teleop` `validate.py` | episode 质量门禁 | `reference-only` | ❌ 无许可证 | L2 | ★ **门禁阈值值得抄**：未回位确认不入库、关节跟踪 **p95 ≤ 5°**、控制率 **≥ 35 Hz** |
| **`xr_teleoperate` `episode_writer.py`**（本轮） | **自定义 `data.json` + JPG** | **`reference-only`/`custom`** | Apache-2.0 | L2 | ❌ **非 LeRobot/MCAP**；❌ **item 只有 `idx`，无任何时间戳**；❌ **深度恒为空**；✅ 异步写盘 + `Queue(-1)` |
| **`DexTeleGym`**（本轮） | **仅 6 路 MP4** | **❌ 不可采用** | **无授权** + 内嵌专有 Isaac Gym | L2 | ❌ **无动作/状态/时间戳落盘**；❌ **深度/分割是彩化后的有损图**（原始公制深度与 seg ID 均被丢弃）→ **不构成可训练数据集** |
| **`TeleVision`**（本轮） | ZED SVO → hdf5（后处理） | `reference-only` | Apache-2.0（+ ZED SDK 专有） | L2 | ⚠️ **原始录制不在仓库**；✅ 时间戳最近邻对齐（`post_process.py:78-88`）可作参考 |

### 横切关注点

| 关注点 | 最佳参照 | 其余实现状况 |
| --- | --- | --- |
| **时间同步** | **`IsaacTeleop` 双时钟**（唯一成熟契约） | `lbx` 主机墙钟单点；`franka-vr-teleop` 无时间戳；`pico` 有三个时间戳但未与相机硬件对齐；**`xr_teleoperate` 无任何时间戳**；`HTS` 默认无时间戳 |
| **安全包络** | **`PiperPilot`**（工作空间盒 + 线/角速度 + 姿态限 + 目标系留 tether + `LimitTracker`） | 两个 UR/Franka 先例**无 watchdog**；`pico` **主动关闭 SDK 限位**；**`xr_teleoperate` 无工作空间盒、无碰撞约束、仿真模式跳过速度限幅** |
| **急停** | — | **全部不可用**：`PiperPilot` 死代码；`pico` 无扭矩级急停；两个 Franka/UR 先例无急停概念；**`xr_teleoperate` 仅 motion 模式有软急停，手部追踪模式无** |
| **失联保护** | — | **全部缺失或无效**：**`xr_teleoperate` 的 `motion_data_ready` 是闩锁（本轮最强反例）** |
| **坐标帧标定** | `PiperPilot`（持久锚点 + 两点 X 轴标定） | **`televuer` `arm_reference_mode`**（head_yaw 忽略 pitch/roll）；`lerobot_ur_dual_vrteleop` 配置化 `R_headset_world`；`franka-vr-teleop` 硬编码 + README 警告"过原点会镜像" |

---

## 4. 建议的垂直切片（依据本轮证据修订）

| 层 | 选择 | 理由 |
| --- | --- | --- |
| ① 输入层 | **三选一**：`IsaacTeleop` DeviceIO（契约强/代价 CloudXR）· `televuer`（可读 + MIT + 最轻/无原生 App）· `XRoboToolkit`（唯一双设备/契约弱） | **这是一个 C 级决策** |
| ② 核心层 | **自研**（抄 `PiperPilot` 包络 + `lerobot_ur_dual_vrteleop` 的 URDF/配置驱动 + `televuer` 的坐标帧参数化） | 生态无独立实现；**契约落末端位姿层** |
| ③ 适配层 | **Piper 用 `PiperPilot`（MIT，`direct-use`）**；Franka/UR 自研（抄机制） | Piper 是唯一可直接复用的机型；且**技术成本最低** |
| ④ 数据层 | **LeRobot 本体（Apache-2.0）+ 抄 `PiperPilot` 的 modality/provenance 设计** | 直接站在成熟底座上，只自研状态机与安全 |

**必须自研的四项（所有先例都缺）**：
1. **失联保护**（输入失联 + 反馈失联两类，区分语义；**验收要能证明断流行为，不是「代码里有 if」**）
2. **急停真正接线**（所有先例都不可用）
3. **时间同步**（参照 `IsaacTeleop` 双时钟，但落到相机曝光对齐）
4. **显式 `FrameCalibration` 契约**（坐标帧会失效，必须可断言、可持久化）

---

## 5. 未覆盖 / 待深挖

| 项目 | 状态 |
| --- | --- |
| `openarmx_teleop_vr` | **未克隆、未深挖**（且为 **CC BY-NC-SA 4.0 禁商用**） |
| `PICO-Unity-OpenXR-SDK` | 未克隆、未深挖（专有许可） |
| `teleimager` / `dex-retargeting` | ✅ **已克隆**（本轮）；仅到「结构 + 许可证」层，**未逐文件精读**（`televuer` 已精读） |
| `XRoboToolkit-Unity-Client`（**PICO 客户端**） | ✅ **已深挖（本轮）**，见 [`xrobotoolkit.md`](xrobotoolkit.md) → **parity 结论已闭合**：Quest 是**被主动裁剪的降级实现**（删 `Body`/`Motion`、`ExtDev` 全注释、`Hand` 的 `count/scale/s/r` 硬编码、SN 恒为 `"TestDevice"`） |

> ✅ **克隆覆盖已达 22**（19 第三方 + 3 个 submodule 组件）；**① 层、② 层、③ 层、④ 层的候选均已至少 L2 评估。**
> ⚠️ **唯一未闭合**：`openarmx_teleop_vr` 与 `PICO-Unity-OpenXR-SDK`（均因许可/必要性未克隆）。

---

## 6. 待处理的下游动作

1. **报告/汇报稿需要一轮合并修正**（深挖带来的结论变化，**本轮新增 5 条**）：
   - `lbx-Franka-Teach` 的「✅ MCAP/DROID」→ **DROID 兼容不成立**
   - 「40Hz 记录 / 6.6Hz 控制」→ 40Hz 仅性能模式；6.6Hz 是观测延迟
   - 「XRoboToolkit-Teleop-ROS 只支持 PICO 不支持 Quest」→ Quest 客户端存在但是**功能裁剪分支**
   - ★ **新增**：**`isaac_ros_teleop` 不是绕过 CloudXR 的路径**（原表述须删改）→ **① 层候选池减少一个**
   - ★ **新增**：**`xr_teleoperate` 手部失联保护是假的**（`motion_data_ready` 闩锁）
   - ★ **新增**：**`televuer` 是 ① 层契约最可读的候选（MIT）**
   - ★ **新增**：**`DexTeleGym` 三重许可问题 → 代码不可采用**（真身应改为上游 `OpenTeleVision`，但上游也仅 `reference-only`）
   - ★ **新增**：**`TeleVision` 降级为 `reference-only`**
   - `quest-wrist-tracker` 元数据补全（**265★ / Apache-2.0 / 2026-06-07**）
2. **`R5`（"UR7e"）可关闭**：源码证据指向 **UR5e**（`dual_ur5e.urdf`），"ur7e" 只是设备符号链接名。
3. **`lbx-Franka-Teach` 含明文凭据与内网拓扑** → 若归档/分享需先脱敏。
4. ~~补齐 `XRoboToolkit-Unity-Client`（PICO 客户端）克隆，闭合 parity 结论。~~ → **已完成**（克隆 + 源码级深挖）。
5. ★ **新增**：**`OQ-003`（手柄 6DoF vs 裸手追踪）现在有直接证据了** —— HTS 只覆盖**裸手**，`Quest2ROS` 系只覆盖**手柄** → 数采闭环需要**两者并存**（裸手灵巧 + 手柄 clutch/夹爪），但属 C 级，需用户确认。
