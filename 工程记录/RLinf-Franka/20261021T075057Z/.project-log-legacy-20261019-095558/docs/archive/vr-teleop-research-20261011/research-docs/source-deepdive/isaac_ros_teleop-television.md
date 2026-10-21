# 源码深挖 · `isaac_ros_teleop` + `TeleVision`

> **证据级**：**L2（源码可证）**，来源为独立只读子 Agent 报告 **+ 主 Agent 抽查**（见 §6）。
> **为什么这两个放一起**：它们各自被我们记为「IsaacTeleop 的 ROS 薄封装」与「VR 遥操作候选」，**本轮结论是：两个都要降级，但降级原因完全不同。**

---

## 1. 一句话

**`isaac_ros_teleop` 不是绕过 CloudXR 的路径，而是 CloudXR 路径的 ROS 2 外壳**；**`TeleVision` 是唯一不依赖 CloudXR 的纯开源输入层，但已停更且不满足 Franka / PICO / 数采三项需求。**

---

## 2. ★★ `isaac_ros_teleop`：**颠覆性发现 —— 它是 CloudXR 的更深处**

### 2.1 它就是 `IsaacTeleop/examples/teleop_ros2` 的打包层

| 证据 | 原文 | 行 |
| --- | --- | --- |
| `isaac_teleop_core/CMakeLists.txt` | `set(ISAACTELEOP_SRC "${CMAKE_CURRENT_SOURCE_DIR}/IsaacTeleop")` | `:17` |
| 同上 | `set(TELEOP_ROS2_EXAMPLE_DIR "${ISAACTELEOP_SRC}/examples/teleop_ros2")` / `teleop_ros2_node.py` | `:45-48` |
| 同上 | `COMMENT "Building isaacteleop Python wheel from source"` | `:106` |
| `isaac_teleop_core/package.xml` | `<description>This package **wraps IsaacTeleop as a ROS 2 package**, which serves as the backend for Isaac ROS Teleop.</description>` | `:25` |
| `IsaacTeleop/examples/teleop_ros2/AGENTS.md` | *"Supported ROS 2 reference publisher for Isaac Teleop. … **Consumed by Isaac ROS Teleop.**"* | `:9-11` |
| `.gitmodules` | `[submodule "isaac_teleop_core/IsaacTeleop"] url = https://github.com/NVIDIA/IsaacTeleop` | `:1-4` |

**它自身独有的代码只有两处**：`src/pose_reset_node.cpp`（**417 行 C++**）+ launch 封装。

### 2.2 CloudXR 绑定（**4 条独立证据**）

| # | 证据 | 行 |
| --- | --- | --- |
| 1 | `CMakeLists.txt` 安装 **`isaacteleop[cloudxr,retargeters]`** | `:131` |
| 2 | 默认 `-DENABLE_CLOUDXR_BUNDLE_CHECK=ON`；构建需 `ISAACTELEOP_CLOUDXR_SDK` tarball | `:43`；`isaacteleop_cmake_build.sh:28` |
| 3 | launch 直接暴露 **`cloudxr_accept_eula`** / `cloudxr_install_dir` / `cloudxr_setup_oob` / `cloudxr_usb_local`；`scripts/cloudxr_runtime.py:19` `from isaacteleop.cloudxr.__main__ import main` —— **进程内启动 CloudXR runtime** | `launch.py:139, 152, 162` |
| 4 | 上游官方运行方式：`--gpus all` + `-v $HOME/.cloudxr:/root/.cloudxr` + `cloudxr_accept_eula:=true` | `IsaacTeleop/examples/teleop_ros2/README.md:176-181` |

> **唯一的「无 CloudXR」模式是离线回放**（`mcap_replay_path`；证据：`IsaacTeleop/examples/teleop_ros2/AGENTS.md` 明写 *"Replay mode **does not launch CloudXR**, so no GPU/NGC runtime is required"*，以及 `.github/workflows/build-ubuntu.yml` 的 mcap 构建/回放步骤）——**CI 夹具/离线复现，不是实时遥操作输入**。
>
> ⚠️ **引用更正**：早前把该证据引为 `AGENTS.md:10-11` 有误 —— 仓库根的 `AGENTS.md` 讲的是"预读 AGENTS.md"，与 mcap 无关。

### 2.3 输入契约（设备无关 ✅）

| Topic | 类型 | 形态 |
| --- | --- | --- |
| `xr_teleop/ee_poses` | `teleop_ros2_interfaces/NamedPoseArray` | **命名 EE 位姿**（`left`/`right`）—— **末端位姿契约** |
| `xr_teleop/hand` | 同上 | 25 + 25 个 OpenXR 手关节位姿（含 `is_valid`） |
| `xr_teleop/finger_joints` | `sensor_msgs/JointState` | 重定向后的手指关节角 |
| `xr_teleop/controller_data` | `std_msgs/ByteMultiArray` | **msgpack 编码字典**（按键/摇杆） |
| `xr_teleop/head_pose` / `root_pose` / `root_twist` | `PoseStamped` / `TwistStamped` | — |
| `/tf` | `TFMessage` | `world→{left,right}_wrist`、`world→head` |

- **设备无关 ✅**：`README.md:15-17` 明写 *"using the **PICO 4 Ultra** or **Meta Quest 3** headset"*；`IsaacTeleop` 侧 *"works with **any CloudXR / OpenXR-compatible HMD**"*。
- **输入源可切换**：`hand_tracking_provider := native | manus | wuji`；`mode := controller_teleop | hand_teleop | controller_raw | full_body`；`ee_poses_frame := world | head`。

> ★ **`NamedPoseArray` 的 `name` / `pose` / `is_valid` 三元组 + invalid 语义是值得抄的契约设计**（对比 `xr_teleoperate` 的裸 dataclass 与 `XRoboToolkit` 的无 schema）。

### 2.4 无机器人后端 / 无数采

- `grep franka|ur5|piper` → **0 命中**；`package.xml` 无任何臂依赖
- launch 默认关节名是 **Unitree G1 TriHand**（`launch.py:29-38`）→ `pose_reset_node` 是**为类人形设计**的，复用到 Franka 需替换关节名/帧约定
- **无数采节点**（仅 CI 用 MCAP 夹具 + 回放）

### 2.5 成熟度与平台

| 维度 | 事实 |
| --- | --- |
| 测试 | `test_pose_reset_node.cpp`（238 行真实 gtest）+ lint 样板 |
| CI | 仓库内**无 `.github/`**（在组织级仓库） |
| 平台 | **仅 Linux**（`/usr/bin/gcc`、`apt`、`patchelf`、`.so`/`rpath`）；ROS **Jazzy**，*"Humble is no longer supported"* |
| 预编译 | **无** → 必须 `git submodule update --init` + 自建 wheel + 提供 CloudXR SDK |
| 文件数 | **25**（`git ls-files` 实测，受版本控制）；**非 `.git` 工作树文件 24**；**含 `.git` 内部文件共 54** —— 早前记的"54"是**含 `.git` 的总数**，非工作树文件数（复核修正） |
| 构建开关口径 | `-DENABLE_CLOUDXR_BUNDLE_CHECK` 控制的是"**是否把专有 SDK 打进 wheel**"，**不是"能否无 CloudXR 运行"**（`isaacteleop_cmake_build.sh:580` 按 SDK 是否存在自动取反；无 SDK 可构建出不含 CloudXR 的 wheel，但**运行时仍需 CloudXR 才能接收实时 XR 输入**） |

### 2.6 许可证

- 根 `LICENSE` = **Apache-2.0**；三个 `package.xml` 均 `Apache-2.0`
- ⚠️ **但运行时受限**：`isaacteleop[cloudxr]` → 需接受 **NVIDIA CloudXR EULA**；构建需专有 SDK tarball
- → **Apache-2.0 外壳 + 专有运行时**

### 2.7 ★ 结论

**❌ 不能作为「绕过 CloudXR 的 ROS 路径」。它不但不绕过，反而是 CloudXR 路径的更深封装。**

**→ 报告中必须修正**：`isaac_ros_teleop` 与 `IsaacTeleop` 属**同一输入层**（前者是后者的打包），**不应计为两个独立候选** → **候选池实际减少一个**。

---

## 3. `TeleVision`：纯开源无 CloudXR，但已停更

### 3.1 定位

`README.md:1-2` *"Open-TeleVision: Teleoperation with Immersive **Active Visual Feedback**"*；`:34` *"teleoperation and imitation learning"*；CoRL 2024（`arXiv:2407.01512`）。

### 3.2 ★ 输入层：纯 WebXR，**无设备硬编码，也无设备抽象**

| 证据 | 行 |
| --- | --- |
| `from vuer import Vuer` / `from vuer.schemas import …` | `teleop/TeleVision.py:2-4` |
| `add_handler("HAND_MOVE")` / `add_handler("CAMERA_MOVE")` | `:21-22` |
| 共享内存契约：`left/right_hand_shared` = 16 doubles（4×4）；`landmarks` = **75 doubles（25×3）**；`head_matrix` = 16；`aspect` | `:32-38` |
| **全仓 `grep pico|bytedance` → 0 命中** | — |
| `README.md:59` Quest 本地串流；`:61, 107, 114` **AVP** 需自签证书、**Quest 3** 用 `ngrok` 隧道 | — |

→ **架构上不写死任何头显**（浏览器 WebXR），**不违反**硬约束；但 **PICO 零证据**，且**不存在头显抽象层**。

### 3.3 机器人后端：仅 Dynamixel + Isaac Gym 仿真 + Inspire 手

- `grep franka|ur5|ur10|piper|panda|kinova` → **0 命中**
- `teleop/teleop_active_cam.py:14, 22` `from dynamixel.active_cam import DynamixelAgent`（硬编码 `/dev/serial/by-id/usb-FTDI…`）
- `teleop/teleop_hand.py:1-3` `from isaacgym import …`；`:106-113` 加载 **Inspire 手** URDF
- **有「机器人」抽象协议**：`teleop/dynamixel/robot.py:7-51` `class Robot(Protocol)`（`num_dofs` / `get_joint_state` / `command_joint_state` / `get_observations`）
- **无「头显」抽象** ← 与上面形成**不对称**

### 3.4 数据记录：**原始录制不在仓库**

- `grep 'h5py.File(...,'w')'` 全仓 → **仅 `scripts/post_process.py:120`**（**后处理**，非录制）
- `scripts/post_process.py:20, 26` 输入是 **`.svo`（ZED 专有格式）**
- `:106-128` `load_svo` + `load_hdf5` → `match_timestamps` → 写 `processed_{ep}.hdf5`
- `:46` ZED 图像时间戳；`:71` hdf5 时间戳 `*1000`；`:78-88` **毫秒级最近邻匹配**（非硬件同步）
- 原始 hdf5 由**仓库外**的 Isaac Gym 环境产生

### 3.5 ★ 是否已"死"

| 证据 | 事实 |
| --- | --- |
| `glob **/{.github,test,tests,ci,Dockerfile*,*.cfg,*.toml}` | **仅 2 个文件**（`teleop/inspire_hand.yml`、`act/conda_env.yaml`）→ **无 CI、无测试、无 Docker、无包配置** |
| `README.md:39` | `conda create -n tv python=3.8` |
| `requirements.txt:11, 23, 24, 26` | `numpy==1.23.0`、`torch==2.3.0`、`torchvision==0.18.0`、**`vuer==0.0.32rc7`（RC 版钉死）** |
| `teleop/teleop_hand.py:1` | `from isaacgym import …` → **Isaac Gym 已被 NVIDIA 废弃**（转向 Isaac Lab） |
| `README.md:45, 54` | 需 **ZED SDK**（专有）+ **Isaac Gym** |

→ 依赖链（py3.8/3.9、torch 2.0–2.3、Isaac Gym、vuer RC、ZED SDK、CUDA 11.8）**全部是 2024 年快照**。

### 3.6 许可证

- 根 `LICENSE:1-3` = **Apache-2.0** ✅（主 Agent 已在另一轮确认）
- 声明构建于 **ACT（MIT）**、detr、dex-retargeting、vuer
- 受限项：**ZED SDK（专有）**、**Isaac Gym（NVIDIA 专有）**

### 3.7 ★ 结论

**⚠️ 从「可集成候选」移除；降级保留为 `reference-only`（架构参考）。**

**保留为参考的理由（3 条可抄的东西）**：
1. 它是**唯一不依赖 CloudXR 的**，证明「纯开源 WebXR 输入层」路线可行
2. `Preprocessor.py:23-52` 的坐标变换链（`grd_yup2grd_zup` / `hand2inspire` / 腕-头相对化）是**可直接借鉴的数学契约**
3. `constants_vuer.py:3` `tip_indices = [4, 9, 14, 19, 24]` + 25 landmarks 契约 + `inspire_hand.yml` = **手部重定向参考**
4. `post_process.py:78-88` 的**时间戳最近邻对齐**是数采同步的参考实现

---

## 4. 两仓库对照

| 维度 | `isaac_ros_teleop` | `TeleVision` |
| --- | --- | --- |
| 定位 | IsaacTeleop 的 **ROS 2 打包层** | 论文实现：**VR 遥操作 + 主动视觉 + ACT** |
| 输入契约 | ROS topics：**`NamedPoseArray`（含 `is_valid`）** | Python 共享内存：`head_matrix` / `hand` / `landmarks(25×3)` |
| 传输 | **CloudXR**（专有 + GPU + 仅 Linux） | **Vuer / WebXR + WebRTC**（纯开源） |
| 设备无关 | ✅ 明确支持 PICO 4 Ultra + Quest 3 | ⚠️ 架构不限设备，但**仅 Quest3/AVP 有记录，PICO 零证据**；无抽象层 |
| 机器人后端 | ❌ 无 | ⚠️ Dynamixel + Isaac Gym + Inspire；无 Franka/UR/Piper；**有 `Robot` Protocol** |
| 数采 | ❌ 无 | ⚠️ **原始录制不在仓库**；仅 ZED SVO 后处理 |
| 活跃度 | README 载 **2026-09-21** 更新 | **无 CI/测试**；依赖 2024 快照；**Isaac Gym 已废弃** |
| 许可证 | Apache-2.0 外壳 + **CloudXR EULA** | Apache-2.0 + **ZED SDK / Isaac Gym 专有** |
| **复用强度** | **`reference-only`** | **`reference-only`** |

---

## 5. 对本项目的直接输入

1. **候选池修正**：`isaac_ros_teleop` 与 `IsaacTeleop` **合并为同一输入层候选**（前者是后者的 ROS 打包）→ ① 层独立候选**减少一个**。
2. **「用 ROS 绕开 CloudXR」这条假设不成立** —— 若要绕开 CloudXR，必须**换输入层**（浏览器 WebXR / 原生 OpenXR Android 客户端），而不是走这个仓库。
3. **`NamedPoseArray` 的 `is_valid` 语义值得抄** —— 它是本轮见到的**最好的「无效数据显式表达」契约**（对比 `xr_teleoperate` 的 `except: pass` 与 `XRoboToolkit` 的整帧丢弃）。
4. **`TeleVision` 从候选移除**，但其**坐标变换链**与**时间戳最近邻对齐**值得抽取为参考。

---

## 6. 主 Agent 抽查记录

| # | 子 Agent 断言 | 抽查结果 |
| --- | --- | --- |
| 1 | `.gitmodules` 指向 `NVIDIA/IsaacTeleop` | ✅ 确认 |
| 2 | submodule **未 checkout**（目录 0 条目） | ✅ 确认（`isaac_teleop_core/` 6 条目，`IsaacTeleop/` 0 条目） |
| 3 | 安装 `isaacteleop[cloudxr,retargeters]` | ✅ 确认（`CMakeLists.txt:131`；另 `:43` `ENABLE_CLOUDXR_BUNDLE_CHECK=ON`） |
| 4 | launch 暴露 `cloudxr_accept_eula` | ✅ 确认（`launch.py:152`，另 `:139`/`:162`） |
| 5 | `package.xml` 自述 "wraps IsaacTeleop" | ✅ 确认（`:25`） |
| 6 | **本地 23 个文件** | ❌ **子 Agent 计数错误** —— 主 Agent 实测：**受版本控制 25 个**（`git ls-files`）、非 `.git` 工作树 24 个、**含 `.git` 共 54 个** |
| 7 | （复核发现）`mcap_replay_path` 的引用位置 | ❌ **原引用 `AGENTS.md:10-11` 有误** —— 正确位置是 `IsaacTeleop/examples/teleop_ros2/AGENTS.md`（明写 *"Replay mode does not launch CloudXR, so no GPU/NGC runtime is required"*）与 `.github/workflows/build-ubuntu.yml` 的 mcap 构建步骤 |

> 第 6 条说明：**子 Agent 的 `glob` 会漏计**（隐藏文件、深层嵌套），而**"含 `.git`"与"工作树文件"是两个不同口径** —— 两次计数（23 与 54）都不等于"受版本控制的文件数 25"。**涉及计数/体积的事实，必须由有 shell 的一方按明确口径复核。**

---

## 7. 未验证项

| # | 未验证项 |
| --- | --- |
| 1 | `isaac_ros_teleop` 的远端星数 / 最后提交（`verification_capability_missing`） |
| 2 | `TeleVision` 的「2024-09-26 后无提交」（本地 `.git` 在，但我未核） |
| 3 | 两仓库是否在组织级 CI 中有构建矩阵 |
| 4 | **L3 / L4 证据均为零** |
| 5 | `TeleVision` 依赖是否仍可解析（无构建验证） |
