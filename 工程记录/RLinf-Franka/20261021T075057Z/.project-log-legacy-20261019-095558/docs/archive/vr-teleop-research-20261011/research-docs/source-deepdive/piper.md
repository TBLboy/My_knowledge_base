# 源码深挖 · Piper 两个后端（`PiperPilot` + `pico-piper-teleop`）

> **证据级**：**L2（源码可证）**，来源为**独立只读子 Agent 报告**。
> **范围**：`tomakeIT/PiperPilot`（45 py + `quest_app/` C++，1★，MIT）+ `swaaniida/pico-piper-teleop`（12 py，0★，**无许可证**）。
> **为什么重要**：它们是**唯一两个「VR → Piper」的真机先例**，也是我们「多机械臂扩展」的第一个落点。

---

## 1. 一句话

**两个仓库几乎没有共同点，但 `PiperPilot` 已经给出了我们需要的那个抽象**（`ArmBase` 同时覆盖末端位姿与关节两种控制空间），而 `pico-piper-teleop` 的**许可状态是硬阻断**。

---

## 2. 两个仓库的架构对照

```
PiperPilot（Quest 3 → Piper）
  Quest 3 APK（**原生 C++/OpenXR**，Android NativeActivity，非 Unity）
    └─ TCP 8735 换行 JSON（出站：t/mono/frame/state/space/anchor/head/left/right）
    └─ TCP 8736 MJPEG（浮层面板）
    └─ adb forward（**走 USB 线**）→ 127.0.0.1:8735
  QuestReader（线程，自动重连 stall_reconnect_s=6.0）
  TeleopController 100 Hz：one-euro 滤波 → 离合(squeeze 0.7/0.3)
      → 工作空间盒/速度/姿态/系留/步长 钳位 → ArmBase.command_eef(pose6)
  ┌── PiperArm（move_p，固件 IK）
  └── PiperArmMIT（宿主 DLS-IK + move_mit 阻抗，默认）+ gravity_ff + soft_start 0.8s
  └─ pyAgxArm 1.0.0 → SocketCAN(can0, 1Mbps) → Piper
  Recorder 30 Hz → LeRobotWriter（LeRobot v2.0 + GR00T modality + provenance）

pico-piper-teleop（PICO → PiPER + Tracer）
  PICO 4（XRoboToolkit 客户端，**网络**发到 VM IP）
    └─ XRoboToolkit PC Service（/opt/apps/roboticsservice，**闭源安装包**）
        └─ xrobotoolkit_sdk（pybind，同机进程内）
  teleop.py 主循环 **50 Hz**：right_controller_pose(7) → R_HEADSET_WORLD → one-euro
      → 离合(grip 0.8/0.5) → Placo 6D IK（URDF）→ JointCtrl(×1000)
      → MotionCtrl_2(0x01,0x01,speed,0x00) → piper_sdk C_PiperInterface_V2 → SocketCAN
  左轴/右轴 + 左 grip → TracerRosBridge（**子进程**）→ ROS2 /cmd_vel → Tracer Mini
  记录：data/episodes/<id>/{metadata.json, samples.jsonl, camera/, global_camera/}
```

---

## 3. ★★ 决定性发现：**动作空间必须统一在「末端位姿」层**

这条来自两个仓库的**直接对照**：

| | PiperPilot | pico-piper-teleop |
| --- | --- | --- |
| 记录的动作 | **绝对 EEF 位姿**（`action.arm_eef: 7`） | **关节角**（`commanded_joint_deg`） |
| 证据 | `lerobot_writer.py:42-48` `FEATURE_COLUMNS = {"observation.arm_eef":7, "action.arm_eef":7, ...}` | `teleop.py:855` `commanded_joint_deg` |

**推论（对本项目是多机械臂的关键约束）**：

> **关节角路线在 Franka(7) / Piper(6) / UR(6) 自由度不同时无法合并数据集。**
> 而 EEF 位姿是 **6-DoF 通用**的——`PiperPilot` 的 `action.arm_eef: 7`（位置 3 + 四元数 4）在三种机器人上形状一致。

**这给 `OQ-001` 提供了第三种权衡维度**（此前只有「谁做 IK」）：

| 方案 | 契约 | 跨机器人数据集可合并？ |
| --- | --- | --- |
| 关节角（`lerobot_ur_dual_vrteleop` 默认 / `pico-piper-teleop`） | `{arm}_joint_{i}.pos` | ❌ 自由度不同 → 不可合并 |
| **末端位姿（`PiperPilot` / `franka-vr-teleop`）** | `arm_eef: 7` | ✅ 6-DoF 通用 |
| 声明式（LeRobot 特征字典 / `control_space` 配置） | 由插件声明 | ⚠️ 取决于各插件声明什么 |

→ **若「面向模型训练的数据采集闭环」是核心目标，则动作空间必须落在末端位姿层**（或至少在数据集层面统一到 EEF）。**这是本轮最强的架构输入。**

---

## 4. `PiperPilot`：我们最该直接复用的那个（MIT）

### 4.1 从端抽象 `ArmBase`（**可直接采用**）

`piper_arm.py:55-92` 定义 `ArmBase`，`make_arm`（`:522-528`）工厂，三个 backend：

| backend | 控制空间 | 实现 |
| --- | --- | --- |
| `piper_mit`（**默认**） | 关节（MIT 阻抗） | 宿主 **DLS-IK** + 逐关节阻抗 + `gravity_ff` + `soft_start` 0.8 s |
| `piper` | 末端位姿 | `move_p`（**固件 IK**） |
| `fake` | — | **无硬件全链路**（`:466-519`） |

**`describe()`（`:69-71, 175-186`）天然产出数据集的 provenance 字段** —— 这是很聪明的设计：**控制后端/固件/增益被自动写进数据集元数据**。

### 4.2 数据层：LeRobot v2.0 + GR00T modality + provenance

```
├── meta/{info.json, modality.json, episodes.jsonl, tasks.jsonl, stats.json}
├── data/chunk-XXX/episode_XXXXXX.parquet
├── videos/chunk-XXX/<video_key>/episode_XXXXXX.mp4
└── extras/  # 非标准：原始 quest 流 dump（调试）
```

- `codebase_version: "v2.0"`、`fps: 30`（`lerobot_writer.py:377-391`）
- features：`observation.arm_joint:6 / arm_eef:7 / gripper:1`，`action.arm_eef:7 / gripper:1`（`:42-48`）
- **GR00T modality**（`:50-96`）：`(start,end)` 切片 + `original_key` + `dtype` + `rotation_type: "quat_wxyz"` + `absolute: true`
- **provenance 绑定**（`:431-441`）：`control.backend/impedance.kp/kd/t_ff/gravity_ff`、`arm.firmware`、`recording.fps` + **变更告警**（`:474-487`）

> ★ **这条应成为我们的数据层不变量**：`docs/reference/dataset-format.md:165-200` 原文——
> *"a policy trained on this data is implicitly bound to them"*。
> **即：策略隐式绑定于采集时的控制参数。** 这正是我们数采闭环必须记录的东西。

### 4.3 安全：**笛卡尔包络最完整的一个**

`teleop_controller.py` + `configs/default.yaml`：

| 机制 | 值 | 位置 |
| --- | --- | --- |
| 工作空间盒 | `min [0.05,-0.35,0.03]` / `max [0.55,0.35,0.50]` | `default.yaml:40-41` → `teleop_controller.py:280-286` |
| 每 tick 速度上限 | `max_lin_vel: 0.8` / `max_ang_vel: 2.5` | `:42-43` → `:270-279` |
| 姿态硬限 | `pitch_abs_max_deg: 88.0`（避 `move_p` 的 ±90° 硬限） | `:44` → `:298-301` |
| **目标系留（tether）** | `max_cmd_deviation: 0.12` | `:45` → `:288-296` |
| 失联冻结 | `stale_timeout_s: 0.25` → `_disengage("stream stale")` | `:10` → `:176-181` |
| 关节步长 | `max_joint_vel: 3.5`（逐 tick 钳位） | `:93` → `piper_arm.py:242,393,428` |
| 关节限位来源 | **SDK preset ∩ 配置** `joint_limits_deg` | `:103-105` → `piper_arm.py:250-259` |
| 夹爪防堵转 | `open_margin: 0.002` | `:112` → `piper_arm.py:198-207` |

**★ `limits.py:1-9` 的模块哲学值得抄**：

> *"make every silent safety clamp visible"* + `LimitTracker`

→ **每一次安全钳制都被显式计数与上报**，而不是静默发生。**这是可观测性上的正确做法**，我们应直接采用。

### 4.4 ⚠️ 缺陷 1：`emergency_stop()` 是**死代码**

`piper_arm.py:218-219` 实现了 `self.robot.electronic_emergency_stop()`，但**全仓 grep 只有定义、无调用点**。

→ **实际安全完全依赖**「离合松开 + 陈旧超时 + 固件保持最后目标」。**没有扭矩级急停的可用路径。**

### 4.5 成熟度信号（意外地强）

- **11 个测试文件 / 61 个 `def test_`**（含 `test_integration_sim.py:92 test_sim_pipeline` 全链路、`test_video_pts_alignment`、`test_record_session_and_binding_warning`、对真实 pyAgxArm FK 的往返测试）
- **`fake` backend 支持无硬件全链路** → 与我们的 P1「无需真机的仿真闭环」直接对齐
- `LoopWatchdog` 打印全线程栈（`collect_data.py:75-107`）

---

## 5. `pico-piper-teleop`：**许可硬阻断**，但三个脚本值得重写移植

### 5.1 许可状态（**结论：不可复制代码**）

- `glob **/{LICENSE,LICENSE.*,COPYING,NOTICE}*` → **0 命中**
- 全仓 grep `licen[cs]e|copyright|MIT|Apache|BSD|SPDX` → **仅命中 `joint_limit` / `speed limits` 等无关词，无任何版权头**
- `pyproject.toml:1-25` **无 `license` 字段**
- **派生自两个未声明许可的上游**：`teleop.py:4` *"Functional single-arm adaptation of manipulation_pipeline-main"*；`assets/piper_kinematics.urdf:2` 同源声明；另有大量 `reference ZIP` 引用

→ **无许可证 = 默认保留所有权利。代码不可复制进我们的产物。**

### 5.2 ★ `preflight` / `recover` / `validate` 三件套（**值得以重写方式移植**）

| 脚本 | 职责 | 关键设计 |
| --- | --- | --- |
| **`preflight.py`** | **只读**预检，**不产生任何运动** | 逐个 `check_import`（numpy/scipy/placo/cv2/piper_sdk/xrobotoolkit_sdk）；URDF 存在；**PC Service 存在**；`piper_can` 必须 `state UP` + `bitrate 1000000`；腕部相机必须出帧。`--software-only` 跳过硬件段 |
| **`recover.py`** | **受控低速分段回位** | `MAX_WAYPOINT_DELTA = 5000`（5°）、`MOVE_SPEED_PERCENT = 50`、`COMMAND_HZ = 100`；**先以实测姿态进入 CAN 关节模式并等 `EnableArm(7)` 成功才发第一个 waypoint**；每 waypoint 20 s 超时；到位后回 STANDBY + `DisableArm(7)` |
| **`validate.py`** | **episode 质量门禁** → `validation.json` | 见下表 |

**`validate.py` 的判定项**（`:136-172`）：

| 门禁 | 阈值 |
| --- | --- |
| metadata 缺失 / `status != "complete"` | 失败 |
| **未确认回到 episode 初始位姿** | 失败（`:141-142`） |
| PC 时间戳非单调 | 失败 |
| 机器人 `error_code/arm_status` 异常 | 失败 |
| 相机文件缺失 / 引用缺失率 | > 10% 失败 |
| 相机帧率 | < 20 Hz / < 10 Hz 失败 |
| **关节跟踪 p95** | **> 5° 失败**（`:169-170`） |
| **控制采样率** | **< 35 Hz 失败**（`:171-172`） |

跟踪误差的测法很讲究（`:98-111`）：命令与反馈在同一样本内，故用**命令后 ≥100 ms 的反馈**比对，而不是前一条反馈。

> ★ **这几条应直接成为我们的数据准入不变量**：**未回位确认的 episode 不得入库**、**关节跟踪 p95 ≤ 5°**、**控制率 ≥ 35 Hz**。

### 5.3 ★ 多从端模式（**架构形态值得移植**）

- 两个**完全独立的从端通道** + **独立超时归零**
- **跨进程隔离**：`ros_bridge.py:15-56` 子进程建 rclpy node 发布 `/cmd_vel`、订阅 `/tracer_status`；`:11` `COMMAND_TIMEOUT_S = 0.2`，`:50-51` **父进程停更 200 ms 即归零**；退出时补发 10 次零速（`:60-70`）
- 主进程只做 `set_command`，**Piper 控制与 Tracer 控制互不阻塞**

→ **判定：是「天然支持多从端」的架构形态，但不是可扩展的抽象**（左/右控制器角色、CAN id、速度上限全是常量）。

### 5.4 ⚠️ 安全缺陷（**此前未记录的具体风险**）

1. **主动关闭 SDK 限位**：`teleop.py:431` `start_sdk_joint_limit=False, start_sdk_gripper_limit=False`
2. **无笛卡尔安全层**：无工作空间盒、无笛卡尔速度上限、无姿态上限、无关节速度钳位；输出校验仅「形状 + 有限」（`:318-322`）
3. **URDF 限位与固件限位不一致**：URDF 是 j4 ±100° / j5 ±70°，而 `PiperPilot` 记录 `(PIPER_X: j4/j5 are ±89 in SDK!)` → **在 SDK 限位关闭的前提下，IK 会下发固件会钳制的目标** → 正是 `PiperPilot:247-249` 明确规避的失效模式（*"clamped joint fighting the impedance loop buzzes and drifts"*）
4. **无扭矩级急停**：B 键是「guarded hold → 回 start 位姿 → STANDBY → 释放扭矩」

---

## 6. 两个仓库各缺一半，合起来才完整

| 能力 | PiperPilot | pico-piper-teleop |
| --- | --- | --- |
| 从端抽象（位姿+关节双控制空间） | ✅ `ArmBase` | ❌ 仅关节角 |
| 笛卡尔安全包络 | ✅ 完整 | ❌ **无** |
| 限位可见性（`LimitTracker`） | ✅ | ❌ |
| **急停真正接线** | ❌ **死代码** | ❌ 无扭矩级急停 |
| **只读预检** | ❌ | ✅ `preflight.py` |
| **episode 质量门禁** | ❌ | ✅ `validate.py` |
| 数据格式（LeRobot v2.0 + GR00T） | ✅ | ❌ 自定义 JSONL |
| 测试 | ✅ 61 个 | ❌ **0 个** |
| 无硬件全链路（`fake`） | ✅ | ❌ |
| 许可 | ✅ **MIT** | ❌ **无** |

> **最小正确组合**：**`PiperPilot` 的从端抽象 + 数据层 + 安全包络**，**加上 `pico` 式预检与 episode 门禁**，**再补上真正接线的急停**。

---

## 7. 可复用性判定

| 仓库 | 判定 | 依据 |
| --- | --- | --- |
| **`PiperPilot`** | **① `direct-use`（Python 层）**；`quest_app/` 为 ② `wrapper-adapter`/参考移植（需自建 NDK + OpenXR 工具链编译 APK） | MIT（`LICENSE:1-3`）；`ArmBase` 抽象干净；LeRobot v2.0 + GR00T + provenance 完整；61 测试；`fake` backend。⚠️ **pyAgxArm 为 LGPL-3.0 运行时依赖**（pip 安装、非 vendored）→ 闭源分发需评估 LGPL 义务；⚠️ 急停未接线需自行补 |
| **`pico-piper-teleop`** | **② 参考移植**（安全脚本与多从端模式）＋ **③ 仅作参考**（其余代码） | **无许可证 → 代码不可复制**；无测试；硬编码 `JOINTS_START_DEG/JOINTS_INIT_DEG`、`RIGHT_ELBOW_TRACKER_SERIAL`、固件 `S-V1.5-8` 等**与特定机器绑定** |

---

## 8. 输入契约能否统一？（**可以，但坐标帧标定必须独立建模**）

| 维度 | PiperPilot | pico-piper-teleop | 可统一？ |
| --- | --- | --- | --- |
| 位姿表示 | `pos[3] + quat[x,y,z,w]` | `get_right_controller_pose()` → 7 = pos3 + quat xyzw | ✅ **完全一致** |
| 模拟量 | `trigger` / `squeeze`（离合）/ `stick[2]` | `get_right_trigger/grip`、`get_left_axis/right_axis` | ✅ 可映射 |
| 按钮 | `primary(A/X) secondary(B/Y) menu stick_click` | `get_A/B/X_button`（无 menu/stick_click） | ⚠️ 交集可用，需降级建模 |
| 有效性 | `valid` + `tracked` **双标志** | 无，只能由时间戳新鲜度推断 | ⚠️ 需适配层合成 |
| 附加传感器 | 无 | Motion Tracker（肘部，serial 寻址） | ❌ pico 独有 |
| **坐标帧语义** | **头显内持久空间锚点 + 两点 X 轴标定** | **硬编码** `R_HEADSET_WORLD` + 离合锁存相对映射 | ❌ **必须作为独立「标定契约」处理** |
| 时间基准 | `t`(display) + `mono`(CLOCK_MONOTONIC) | `get_time_stamp_ns()` | ⚠️ 需统一到宿主 monotonic |
| 传输 | 自研 TCP JSON（**有线 USB**） | XRoboToolkit 闭源 PC Service（**网络**） | ❌ 传输层不统一 → 在**适配器接口层**统一 |

**统一建议（可落地）**：以 `quest_client.py:19-67` 的 `HandState/QuestState` 作为**规范输入契约**（它已是超集），为 PICO 侧新增 adapter；**并新增显式的 `FrameCalibration` 契约**（`anchor|stage|local` / `R_HEADSET_WORLD` / `yaw_offset_deg` / 两点标定结果），把「坐标帧从哪来、何时失效」变成可断言的对象。

> ⚠️ **这条与 `franka-vr-teleop` 的 README 警告呼应**：*"crossing the origin will cause the coordinates to be mirrored"* —— **坐标帧是会失效的，必须显式建模并可在会话间持久化。**

---

## 9. 未验证项

| # | 未验证项 | 原因 |
| --- | --- | --- |
| U1 | 无法执行任何 shell 命令 | 子 Agent 仅有 read/glob/grep |
| U2 | 本地 commit 是否等于普查 pin（`PiperPilot@9a63c89`、`pico@3b0e3da`） | 无 git |
| U3 | `piper_sdk` 实际版本（README 称 0.6.1） | submodule `src/piper_sdk` **未 checkout** |
| U4 | `xrobotoolkit_sdk` 实际 API / 帧率 / 坐标系 | submodule 未 checkout；PC Service 闭源 |
| U5 | `pyAgxArm` 实际安装版本 | 依赖未安装 |
| U6 | pico 的 `end_pose_0p001` 单位与旋转顺序 | `piper_sdk` 源码不可见 |
| U7 | **pico 的 URDF 限位是否与真实固件限位一致** | 需 SDK preset 或真机读数 |
| U8 | 两仓库真机延迟 / 跟踪误差 | 无硬件；PiperPilot 数字为作者自述 |
| U9 | XRoboToolkit PC Service 是否支持 Quest | 需网络证据 |
| U10 | 两仓库是否有 CI | 文件清单未见 workflow |
| U11 | pico 上游 `manipulation_pipeline-main` / `reference ZIP` 的许可证 | 仓库内完全未记录 |

---

## 10. 最重要的 3 个发现

1. **两个「Piper 后端」在从端抽象层几乎没有共同点，但 `PiperPilot` 已经给出了我们需要的那个抽象。**
   它的 `ArmBase`（`piper_arm.py:55-92`）**同时覆盖末端位姿与关节两种控制空间**，`describe()` 天然产出数据集 provenance。**这是「Piper 作为第二机械臂」最省成本的落点。**

2. **`pico-piper-teleop` 的许可状态是硬阻断，且它的安全性显著弱于 `PiperPilot`。**
   无 LICENSE、无版权头、派生自未声明许可的上游；**主动关闭 SDK 关节/夹爪限位**、无笛卡尔包络、无关节速度钳位，且 **URDF 限位与 PIPER_X 实际固件限位不一致** —— **这是一条此前未被记录的具体安全风险。**

3. **安全与数据准入这两条主线，两个仓库各缺一半，合起来才完整。**
   `PiperPilot` 有强输入层/包络/数据格式/可观测性，但**急停是死代码**、无预检、无 episode 门禁；`pico` 有强预检/受控回位/episode 门禁，但**无扭矩级急停、无笛卡尔安全层、无测试**。
