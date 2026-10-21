# 源码深挖 · Quest 输入设备线（`quest-wrist-tracker` + `quest2ros` + `Quest2ROS2`）

> **证据级**：**L2（源码可证）**，来源为独立只读子 Agent 报告 **+ 主 Agent 抽查**（§7）。
> **为什么单独一条线**：Quest 侧输入层此前只有 `XRoboToolkit-Unity-Client-Quest`（**功能裁剪分支**）与外部依赖 `rail-berkeley/oculus_reader`。**本轮要判断这三仓能否提供更好的 Quest 输入层选项。**

---

## 1. 一句话

**三仓都无法满足「PICO + Quest 双端」硬约束**（全部 PICO 零命中）；**但 `quest-wrist-tracker` 提供了本矩阵 ① 层此前没有的东西：一个许可证干净、零 PC 依赖的 Quest 手部契约**（限定：**只有手，没有按钮**）。

---

## 2. 三仓库横向对照

| 维度 | **`quest-wrist-tracker`（HTS）** | `quest2ros` | `Quest2ROS2` |
| --- | --- | --- | --- |
| **形态** | **Unity 6 头显 App + PC 侧 Python 脚本** | 纯 PC 侧 **ROS1 catkin** 桥 | 纯 PC 侧 **ROS2 Humble (ament_python)** 桥 |
| 头显端是否在仓 | ✅ **在**（Unity 工程 + **预编译 APK**） | ❌ 外部（quest2ros app） | ❌ 外部（**同一个** quest2ros app） |
| **输入内容** | **21 关节（腕相对）+ 手腕 6DoF + 可选头部 6DoF** | 控制器 6DoF + 6 按钮/摇杆/扳机 + 力反馈回传 | 同 quest2ros（+ 机器人侧控制） |
| **★ 有按钮/控制器？** | ⚠️ **完全没有**（仅菜单键停流） | ✅ 有 | ✅ 有 |
| **协议** | **UTF-8 CSV 文本**，UDP 或 TCP | ROS-TCP → ROS1 topic | ROS-TCP → ROS2 topic |
| 默认端口 | UDP `255.255.255.255:9000` 广播 / TCP `127.0.0.1:8000`（`adb reverse`） | TCP 10000 | endpoint.py 内 |
| 频率 | 手 **100 Hz 配置**（文档称实用 ~70 Hz）；头 30 Hz | demo 自旋 1000 Hz（**数据率未知**） | 仿真 30 Hz（真机未知） |
| **时间戳** | ⚠️ **默认完全没有**（仅调试模式含单调 ns） | demo 不填 | 仿真填；真机未知 |
| 坐标系 | Unity 左手系（文档提示翻 Y） | App 侧按键对齐 | 控制器可配 `base_frame_id` |
| **PICO 支持** | ❌ 零命中 | ❌ 零命中 | ❌ 零命中 |
| 抽象层 | 无（`Oculus.Interaction.Input` 直连） | 无 | 无（`mirror` 只是左右互换） |
| **许可证** | ✅ **Apache-2.0** | ❌ **无**（`<license>TODO</license>`） | ✅ **Apache-2.0**（msg 子包标 TODO） |
| **含机器人代码？** | ✅ **无**（接口干净） | ❌ 无（纯桥） | ⚠️ **含**（`robot_arm_controller_base.py` 硬编码 kuka/bh_robot） |
| 活跃度 | 2026（商店在售 + Zenodo DOI） | 2023-12（**3 年停更**） | 2026-03（HRI 2026 论文） |
| **复用强度** | **`wrapper-adapter`** | **`reference-only`** | **`reference-only`** |

---

## 3. ★ `quest-wrist-tracker`（HTS）：契约与边界

### 3.1 改名状态（**引用漂移**）

- `README.md:13, 153` 与 `CITATION.cff:2, 11` **已使用新名 `hand-tracking-streamer`** ✅
- ⚠️ 但 `pyproject.toml:2` `name = "quest-wrist-tracker"` **仍是旧名**，本地目录名也是旧名 → **引用漂移风险仍在**

### 3.2 数据契约（**UTF-8 CSV 文本行**）

| 项 | 内容 | 证据 |
| --- | --- | --- |
| 手腕 | `Right wrist:, x, y, z, qx, qy, qz, qw`（7 floats） | `CONNECTIONS.md:45, 49` |
| 手部 | `Right landmarks:, [x,y,z]×21`（63 floats） | `CONNECTIONS.md:46, 50` |
| 关节选择 | `{1,2,3,4,5, 7,8,9,10, 12,13,14,15, 17,18,19,20, 22,23,24,25}` | `HandLandmarkStreamer.cs:49-55` |
| ★ 关节语义 | `_hand.GetJointPosesFromWrist(...)` → **相对手腕**（非世界系） | `HandLandmarkStreamer.cs:158` |
| 头部位姿 | `Head pose:, x,y,z,qx,qy,qz,qw` | `HeadPoseStreamer.cs:96` |
| 传输模式 | `UDP=0` / `TCP Wired=1` / `TCP WiFi=2` | `HandLandmarkStreamer.cs:216-237` |
| 坐标系 | **Unity 左手系**，文档建议翻转 Y | `CONNECTIONS.md:52-53` |
| **时间戳** | ⚠️ **默认无**；仅 `ShowDebugInfo` 开启时头部含 `t = <monotonicNs>`（`Stopwatch`） | `HandLandmarkStreamer.cs:117, 298-316` |

### 3.3 ⚠️ 没有按钮/控制器

- `grep OVRInput` 在 `Assets/Scripts` **仅 1 处**：`AppManager.cs:134`（菜单键停止流）
- → **无 clutch / gripper / trigger 语义**
- `FistTracking.cs`（`LeftHandFistDetector`）会广播 `Fist: closed/open`，但其 GUID 在 `Scene.unity` **零命中** → **未接线，疑似死代码**（可能误导读者以为有夹爪信号）

### 3.4 其它

- 预编译产物：✅ `hand_tracking_streamer.apk`（仓库根）+ Meta Store + SideQuest
- 官方 SDK：`wengmister/hand-tracking-sdk`（PyPI，**未在工作区**）
- 测试/CI：❌ 全树零命中
- 依赖：`com.meta.xr.sdk.all: 72.0.0`（**Meta 专有 SDK**）→ **与 PICO 路线无法共用同一 App**
- 端口不一致：`CONNECTIONS.md:91` 写 `:9000` vs `AppManager.cs:172` `:8000`

---

## 4. `quest2ros` → `Quest2ROS2`：同一 App + 同一 msg 的 ROS1→ROS2 移植

| 证据 | 内容 |
| --- | --- |
| `quest2ros/README.md:9-11` | 头显端 App 为**外部**：`quest2ros.github.io/q2r-web` + Unity `ROS-TCP-Endpoint` |
| `quest2ros/CMakeLists.txt:10-15` | `find_package(catkin …)` + `rospy` → **ROS1** |
| `Quest2ROS2/README.md:2` | *"Built based on [Quest2ROS]"* → **fork/移植** |
| `Quest2ROS2/README.md:20` | VR 端仍装 **`quest2ros` app**（**同一个**） |
| `Files_for_msg_pkg/msg/*.msg` vs `quest2ros/msg/*.msg` | **逐字相同** |
| `quest2ros/package.xml:16` | `<license>TODO</license>` → **确认「无许可证文件」** |

**消息契约**（`msg/OVR2ROSInputs.msg:1-7`）：`button_upper, button_lower, thumb_stick_horizontal, thumb_stick_vertical, press_index, press_middle`
**力反馈**（`OVR2ROSHapticFeedback.msg:1-2`）：`frequency, amplitude`

### 4.1 缺陷

| 类型 | 内容 |
| --- | --- |
| `implementation-drift` | `Quest2ROS2/q2r2_bringup/ros2quest.py:7` 导入 **`quest2ros2_msg`**，而 `Files_for_msg_pkg/package.xml:4` 生成包名为 `quest2ros` → **命名冲突，节点可能无法导入** |
| `test-drift` | `CheckTCPconnection.py:125` 引用不存在的字段 `press_grip / thumbstick_x / thumbstick_y`（实为 `thumb_stick_horizontal/vertical`）→ 靠 `try/except AttributeError` 兜底 |
| 不可组合 | `robot_arm_controller_base.py:100-101, 127` 硬编码 kuka/bh_robot → **违反「URDF+YAML 配置驱动」判据** |
| 仓库卫生 | `__pycache__` 含**已删除脚本**的 `.pyc`（`Q2R_control_goal*.pyc`、`demo04_testq2r_sub_py.pyc`）→ 暗示**曾有多臂/夹爪控制脚本未公开** |
| 依赖不明 | 要求外部 fork `guguroro/ros_tcp_communication`（**未 vendored，许可未知**） |

---

## 5. ★ 结论：有没有比 `XRoboToolkit-Unity-Client-Quest` 更好的 Quest 输入层？

| 取舍轴 | 谁更好 | 依据 |
| --- | --- | --- |
| ① **满足「PICO + Quest 双端」** | ❌ **三仓全部失败**；`XRoboToolkit` 唯一胜出 | 三仓 PICO 零命中 |
| ② **Quest 裸手追踪契约（可读）** | ✅ **HTS 更好** | HTS 有显式 CSV 契约 + `CONNECTIONS.md` + 独立 Python SDK；`XRoboToolkit` Quest 侧手部只在**无 schema JSON 透传**里 |
| ③ 控制器 6DoF + 按钮 | ⚠️ `Quest2ROS2` 提供（需外部 app）；`XRoboToolkit` 也有 | **HTS 完全没有** |
| ④ **集成重量** | ✅ **HTS 远轻** | HTS = 裸 UDP/TCP 文本，任意语言可解析；`XRoboToolkit` = 必跑 PC-Service（Qt + 预编译 gRPC） |
| ⑤ **许可证清洁度** | ✅ **HTS 更干净** | HTS Apache-2.0 无第三方限制；`XRoboToolkit` 虽 MIT，但 PC-Service `THIRD_PARTY_NOTICE` 含 **Unity 竞争用途禁令 + Qt 许可未声明** |
| ⑥ 时间同步 | ❌ `XRoboToolkit` 略好 | HTS **默认完全没有**时间戳 |
| ⑦ 维护活跃度 | ✅ HTS | 商店在售 + changelog + Zenodo DOI |

> **一句话**：**是的，但只在「Quest 裸手追踪」这一条支线上。**
> **HTS 是比 `XRoboToolkit-Unity-Client-Quest` 更干净、更轻、许可证更明确的 Quest 手部输入源（`wrapper-adapter`）。**
> **但它不发送任何控制器/按钮数据、默认无时间戳、完全不含 PICO** → **不能替代「双端统一输入层」，只能作为 Quest 手部子路径候选，与 `XRoboToolkit` 并存。**
> **`Quest2ROS2` 提供了 HTS 缺失的控制器+按钮+力反馈（Apache-2.0），但输入桥很薄、依赖外部 app 与未 vendored fork、且仓库内混入机器人侧代码 → 不优于 `XRoboToolkit`。**
> **`quest2ros` 无许可证 + ROS1 + 3 年停更 → 不可用。**

---

## 6. 对本项目的直接输入

1. **把 HTS 补进 ① 层候选矩阵**（当前记为「未评估 / L1」）→ 升级为 **L2**：契约 = CSV 文本（21 腕相对关节 + 手腕/头部 6DoF），复用强度 = **`wrapper-adapter`**，许可证 = **Apache-2.0**，**限定为 Quest 手部子路径**。
2. **`quest2ros` 结案**：无许可证 + ROS1 + 停更 → `reference-only`，**不进入交付物**。
3. **`Quest2ROS2` 标 `reference-only`**：可抄 **clutch/anchor 重锚、移动平均滤波、GripperCommand action** 模式；**不可**把其机器人侧代码当可组合件。
4. **★ 落在一个未决问题上**：HTS 只覆盖**裸手**，`Quest2ROS` 系只覆盖**手柄** → 这**正好落在 `OQ-003`（手柄 6DoF vs 裸手追踪）**上。**两者都要**（数采闭环需要「裸手灵巧 + 手柄 clutch/夹爪」并存）是我方倾向，但属 C 级，需用户确认。
5. **PICO parity 仍未由本线闭合** —— 唯一路径是 `XRoboToolkit-Unity-Client`（PICO 客户端，**已克隆并已深挖**，见 [`xrobotoolkit.md`](xrobotoolkit.md)）。

---

## 7. 主 Agent 抽查记录

| # | 断言 | 抽查结果 |
| --- | --- | --- |
| 1 | `quest-wrist-tracker` LICENSE = Apache-2.0 | ✅ 确认（`LICENSE` 头 3 行 = "Apache License / Version 2.0, January 2004"） |
| 2 | `quest2ros` **无 LICENSE 文件** | ✅ 确认（`quest2ros\LICENSE` 不存在） |
| 3 | `Quest2ROS2` LICENSE = Apache-2.0 | ✅ 确认 |
| 4 | 三仓 PICO 零命中 | 采信子 Agent（`grep` 全树） |

---

## 8. 未验证项

| # | 未验证项 | 原因 |
| --- | --- | --- |
| 1 | HTS 实际频率 / UDP 真实时延 | 无 L4 实测 |
| 2 | landmarks **腕相对 vs 世界系** | 源码证据指向腕相对（`GetJointPosesFromWrist`），但 `CONNECTIONS.md:46` 示例数值像世界系 → **文档与代码语义可能不一致**，需真机确认 |
| 3 | `Quest2ROS2` 的 `ros2quest` 节点能否导入 | 未在 ROS2 Humble 环境验证 |
| 4 | 官方 `hand-tracking-sdk` 内容 | 仓库不在工作区（仅 L0） |
| 5 | 提交日期 / 星数 / 文件数 / `.apk` 哈希 | 无 shell 的复核者无法验证；主 Agent 未逐项核 |
