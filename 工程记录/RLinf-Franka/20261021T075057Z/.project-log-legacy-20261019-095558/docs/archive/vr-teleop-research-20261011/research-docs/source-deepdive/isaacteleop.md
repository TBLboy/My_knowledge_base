# 源码深挖 · `NVIDIA/IsaacTeleop`

> **证据级**：**L2（源码可证）**，来源为**独立只读子 Agent 报告**（标注 `subagent-derived`）。
> **规模**：1539 文件 / 85.7 MB；py=448、cpp=392、cfg=95。
> **仓库**：`https://github.com/NVIDIA/IsaacTeleop`（396★，**最近提交 2026-10-10 —— 每日活跃**）
> **前情**：此前我对它的判断**全部来自 README**（第一轮报告甚至遗漏过它）。**本轮首次源码级核实。**

---

## 1. 一句话

**它同时给出两个我们此前判定"生态里没有"的东西：**

1. **一个真正的分层设备抽象**（`deviceio_base` 接口层完全不依赖 OpenXR）——而且 **PICO 与 Quest 共用同一个后端，没有任何厂商分支**；
2. **一个显式的时间戳契约**（`DeviceDataTimestamp` 含 `sample_time_raw_device_clock` 与 `sample_time_local_common_clock` 双时钟）——**这正是我此前说"生态无独立实现"的时间同步机制**。

**但代价很重**：它把 **CloudXR（NVIDIA 专有许可 + GPU + 官方仅 Linux）** 绑在了唯一被源码验证的 live 路径上。

---

## 2. 分层切面（`src/core/` 是 C++ 设备层）

```
src/core/deviceio_base/       ← 接口层（INTERFACE 库，**禁止** OpenXR 依赖）
src/core/deviceio_trackers/   ← facade 层（用户可见 Tracker 类，configure 期 codegen）
src/core/live_trackers/       ← live 后端（真正调 OpenXR）
src/core/replay_trackers/     ← replay 后端（读 MCAP，**无需 GPU**）
src/core/deviceio_session/    ← 会话与更新循环
src/core/schema/fbs/          ← 数据契约（26 个 FlatBuffers schema）
src/python/isaaccapture/retargeting_engine/   ← retargeting（纯 Python，DAG）
src/python/isaaccapture/retargeters/          ← 内置 retargeter
```

**接口层契约（关键）** `src/core/deviceio_base/cpp/inc/deviceio_base/tracker.hpp:16-66`：

```cpp
class ITrackerImpl   { virtual void update(int64_t monotonic_time_ns) = 0; };          // :16,31
class ITrackerSession{ virtual const ITrackerImpl& get_tracker_impl(const ITracker&) const = 0; }; // :50,54
class ITracker       { virtual std::string_view get_name() const = 0; };               // :60,65
```

`src/core/deviceio_base/AGENTS.md` 明文边界：

> *"**Do not** use `XrTime`, `<openxr/openxr.h>`, or OpenXR link targets in this library. Keep the tracker abstraction runtime-agnostic."*

→ **接口层真的是运行时无关的**，这不是文档吹的，是 AGENTS.md 里的硬约束 + INTERFACE 库类型。

**代码生成**：`deviceio_trackers/trackers.toml`（108 行）声明 schema-based tracker（`se3_tracker`、`joint_state`、`soma_*`、`generic_3axis_pedal`…），由 `codegen/generate_trackers.py` 在 **CMake configure 期**生成 facade/live/replay 三份 `.cpp`。

---

## 3. ★★ 双端接入：**PICO 与 Quest 共用同一后端，无厂商分支**

这是我此前无法证实的核心问题，现在有了源码答案：

**后端分发表** `src/core/live_trackers/cpp/live_deviceio_factory.cpp:154-170`：

| 设备 | live 后端 | 数量 |
| --- | --- | --- |
| `HeadTracker` | `LiveHeadTrackerImpl` | **1 个** |
| `HandTracker` | `LiveHandTrackerImpl` | **1 个** |
| `ControllerTracker` | `LiveControllerTrackerImpl` | **1 个** |
| `FullBodyTracker` | `LiveFullBodyTrackerPicoImpl` / noitom / xsens | 3 个（**唯一 vendored 类型**） |

**`LiveHandTrackerImpl::required_extensions()`**（`live_hand_tracker_impl.cpp:62-65`）= `{XR_EXT_HAND_TRACKING_EXTENSION_NAME, XR_MNDX_XDEV_SPACE_EXTENSION_NAME}` —— **标准/通用 OpenXR 扩展，非厂商专有**。

**头显身份由 CloudXR runtime 决定，不是本项目的后端**：

- `src/python/isaaccapture/cloudxr/env_config.py:18` → `DEFAULT_DEVICE_PROFILE = "Quest3"`
- `docs/source/getting_started/quick_start.rst:83-92` 原文：

> *"The CloudXR runtime uses the `Quest3` device profile by default. The name is narrower than the profile: **`Quest3` serves every WebXR client — Quest, PICO, and the desktop-browser IWER emulator — so PICO users should keep it.** Apple Vision Pro connects natively and needs `auto-native` instead."*

**Quest 体感追踪被映射进 PICO 布局**（`docs/source/device/body_tracking.rst:264-274`）：

> *"in the current version the Quest IOBT skeleton is mapped to the PICO BD 24-joint layout before being sent to the server. This means the server always receives data in the `XR_BD_body_tracking` joint format regardless of the source headset."*

> ✅ **对我们的硬约束（PICO 与 Quest 必须并存、不得写死任一设备）**：**在这个项目里，双端接入不是产品架构问题，而是 runtime 配置问题。**
> ⚠️ **但"支持 PICO/Quest/AVP"这条本身仍是 L0 声明**（`overview/architecture.rst:21`）；源码只证明"OpenXR + CloudXR 客户端"，**未证明对任一具体头显做过端到端验证**。

---

## 4. ★★ 时间戳契约：**双时钟**

`src/core/schema/fbs/timestamp.fbs:10-27`：

```fbs
struct DeviceDataTimestamp {
  available_time_local_common_clock;   // 数据可用时刻（本地公共时钟）
  sample_time_local_common_clock;      // 采样时刻（本地公共时钟）
  sample_time_raw_device_clock;        // 采样时刻（**设备原始时钟**）
}
```

**两级约定**（`docs/source/device/trackers.rst:50-66`）：

```
table Xxx { ... }                                                   // payload
table XxxRecord { data: Xxx; timestamp: DeviceDataTimestamp; }      // MCAP root_type
```

> **这直接改写了我此前的一个判断。** 我在方法论文档里把「时间同步」列为**横切关注点**并判断"生态无独立实现"——**这里有一个成熟的、写进 schema 的双时钟契约**：
> - `raw_device_clock` 保留设备原始时间（**可用于与相机曝光对齐**）
> - `local_common_clock` 提供跨设备公共基准（**可用于多路融合**）
> - 且 MCAP 的 root_type 约定保证**每条记录都带时间戳**
>
> **这是 `lbx-Franka-Teach` 缺失的那一环**（后者只有主机墙钟单点）。

---

## 5. 输出契约：**分层有契约，但没有"统一输出契约"**

| 层 | 输出 | 证据 |
| --- | --- | --- |
| 设备层 | **传感器样本**（pose / 关节值 / 控制器输入） | 见 §3 schema |
| retargeting 层 | **per-embodiment 张量组** | 见下 |

**retargeting 层接口**：`retargeting_engine/interface/base_retargeter.py:40-153` — `BaseRetargeter` 子类实现 `input_spec()` / `output_spec()` / `_compute_fn()`。

**输出形态随 retargeter 而变**：

- **末端位姿**：`retargeters/se3_retargeter.py:7`（absolute/relative）；`retargeters/SO101/clutch_retargeter.py:8-15` 给出 7-D `ee_pose` 公式
- **关节角**：`retargeters/joint_space/joint_state_retargeter.py:4-17` — `mode="joint"` 直通 / `mode="ee_pose"` 用 URDF+pinocchio 做 FK；输出键 `JOINT_TARGETS_KEY` / `EE_POSE_KEY` / `GRIPPER_COMMAND_KEY`（`:49-52`）
- **手指关节**：`dex_hand_retargeter.py`、`G1/trihand_motion_controller.py`
- **locomotion**：`[vel_x, vel_y, rot_vel_z, hip_height]`

**拼成单一 action 张量**：`OutputCombiner("action")` + `TensorReorderer`（`references/retargeting/index.rst:275-287`），并警告：

> *"The `output_order` must match the action space expected by the environment. … **Mismatches will cause silent control errors.**"*（`:353-356`）

**reset 机制**：**没有 `pose_reset`**（全仓 `pose_reset` 0 命中）。reset 是**执行事件**：`retargeting_engine/interface/execution_events.py:10-26` — `ExecutionState{UNKNOWN,STOPPED,PAUSED,RUNNING}` + `ExecutionEvents{reset: bool, execution_state}`。语义：reset 时把 held pose 重新播种到**配置的** home，而非实时臂状态（`SO101/clutch_retargeter.py:38-46`）。

> **`NamedPoseArray` 只存在于 ROS2 示例**（`examples/teleop_ros2/.../CMakeLists.txt:11`），**核心库没有**。

---

## 6. 后端解耦度：**设备侧有真插件，机器人侧必须自研**

**设备侧有完整插件机制**（全仓最成熟的扩展点）：

- `src/plugins/` 17 个插件（manus、oak、haptikos、oglo_tactile、spacemouse、steering_wheel、wuji_glove、noitom_mocap、xsens_full_body、so101_leader、rebot_devarm_leader、vive_se3_tracker、generic_3axis_pedal…）
- 跨进程协议：`SchemaPusher` / `SchemaTracker` + OpenXR 扩展 `XR_NVX1_push_tensor` / `XR_NVX1_tensor_data`
- **官方有"接入新设备"指南**：`docs/source/device/add_device.rst`（283 行，四步：定义 `.fbs` → 写 plugin → 写 tracker → 写 printer 验证），参考实现 `generic_3axis_pedal`

**机器人侧没有 adapter/插件 ABI**：

- `src/python/isaaccapture/` 目录清单中**无** robot / backend / embodiment / adapter 模块
- 输出侧机制只有 `IDeviceIOSink`（`deviceio_source_nodes/sink_interface.py:24-91`），且必须经 **DeviceIO tracker** 写回
- 应用自己写循环消费 `session.step()`（`getting_started/teleop_session.rst:374-386`）

**非 Isaac 后端确实被源码验证**：

- MuJoCo 示例**完全不 import Isaac**：`examples/cloudxr_mujoco_teleop/visualize_poses_mujoco_example.py:48-50`（只 import `isaaccapture.deviceio` / `.oxr` / `.cloudxr`）；`:241-258`（`CloudXRLauncher` + `OpenXRSession` + `DeviceIOSession.run`）；`:266-297`（`session.update()` → `head_tracker.get_head()` → `data.mocap_pos[...]`）。该示例 SPDX 头是 **HTC Corporation**，REUSE.toml:33-37 覆盖为 Apache-2.0。
- ROS 2 发布 `NamedPoseArray` / `JointState` / `tf`（`examples/teleop_ros2/README.md:117-134`）

> ⚠️ **"真机 Franka"不存在**：Franka 只在文档里作为 retargeting 示例出现（`references/retargeting/index.rst:287-289`，改编自 Isaac Lab 的 `stack_ik_abs_env_cfg.py`）。

---

## 7. 依赖与门槛：**不强依赖 Isaac，但强依赖 CloudXR + GPU + Linux**

**不强依赖 Isaac Lab/Sim**（这条推翻了我的预设）：

- 基础依赖极薄：`src/core/python/requirements.txt:1-4` = `numpy` + `pyyaml` + `isaacteleop`
- grep `isaaclab|isaacsim|omni.isaac` 在 `*.py` 中 23 处命中，**全部在 `examples/` 或 `docs/conf.py`，`src/python/` 零处**
- `references/requirements.rst:36-46` 把 "Teleop with Isaac Sim/Lab" 单列为**另一种**用法（需 RTX 工作站）

**GPU 需求来自 CloudXR，而非库本身**：

- `references/requirements.rst:26` 所有用法都写 *"NVIDIA GPU required"*（CUDA 12.8+、驱动 580.95.05+）
- 但 `examples/teleop_ros2/AGENTS.md`：*"**Replay mode does not launch CloudXR, so no GPU/NGC runtime is required.**"*
- `viz` 需 Vulkan + CUDA，但 CMake **自动降级**（`CMakeLists.txt:75-87`，两者都找到才 `BUILD_VIZ=ON`）

**平台**：`CMakeLists.txt:107-116` —— **Windows 不官方支持**，须显式 `-DENABLE_EXPERIMENTAL_WINDOWS_BUILD=ON`；CI 只跑 `ubuntu-22.04` / `ubuntu-22.04-arm`。

**"仅设备输入"的轻量用法存在**：`examples/oxr/python/modular_example.py:36-56` —— 只要 `HandTracker` + `HeadTracker` → `DeviceIOSession.get_required_extensions()` → `oxr.OpenXRSession` → `DeviceIOSession.run()` → `session.update()`。**不需要** retargeting / Isaac / viz。

**但**：唯一被源码验证的 live 路径仍要 CloudXR（`visualize_poses_mujoco_example.py:249-258` 是 `CloudXRLauncher` + `OpenXRSession`）；**不用 CloudXR 只能走 MCAP replay**。

---

## 8. 成熟度：**本库工程治理是全生态最强的一个**

**测试**：`tests/cpp/`（Catch2，覆盖 schema / mcap / plugin_manager / live_trackers / replay / viz）+ `tests/python/`（pytest，**最大的是 retargeting_engine**，含 `test_retargeter_composition` / `_reset` / `_timing` / `test_ee_pose_jump_guard` / `test_se3_retargeter_pose_validity` 等）。

**CI**（`.github/workflows/`）：`build-ubuntu.yml` 的 job 包括

| job | 内容 |
| --- | --- |
| `build-ubuntu` | matrix **Debug/Release × py3.11/3.12/3.13 × x64/arm64**；`ctest --parallel`；coverage |
| `pip-editable-install` | scikit-build-core sdist + `pip install -e .` + import smoke |
| `test-viz-gpu` | self-hosted GPU runner |
| `test-viz-sanitizers` | **ASAN + UBSAN** |
| `test-cloudxr` | Docker + CloudXR runtime |
| `test-teleop-ros2` | Docker；**MCAP replay 9 个场景** + 真 CloudXR 起机 + soak |
| `wheel-gate` / `publish-wheel` / `kitmaker*` | 发布链 |

另有 `pre-commit`、`docs`、`dco`、根 `.gitlab-ci.yml`（SonarQube）。

**面向 AI 的治理面**：根 + 每目录 `AGENTS.md`（强制"改文件前读所有祖先 AGENTS.md"、`Mandatory learning loop`、`clang-format-14` CI 门禁）。

---

## 9. 许可证：**库 Apache-2.0 + REUSE 合规，但 CloudXR 是专有**

- `LICENSES/` = Apache-2.0 / BSD-3-Clause / BSL-1.0 / MIT
- `.reuse/` + `REUSE.toml`（v1）+ 全文件 SPDX 头 + pre-commit `reuse lint-file` → **REUSE 合规**（配置与工具链齐备；未运行 `reuse lint` 验证）
- `docs/source/references/license.rst:12-17` **关键例外**：

> *"Certain headers from the OpenXR SDK … are licensed under the MIT license or Boost Software License 1.0. **CloudXR SDK is NVIDIA's proprietary software, licensed under the NVIDIA CloudXR License**."*

- 依赖许可：OpenXR SDK Apache-2.0、yaml-cpp MIT、pybind11 BSD、GLM MIT、spdlog MIT；**CUDA Toolkit = NVIDIA EULA**
- **首次使用需在终端接受 EULA**（`quick_start.rst:79-81`）

> **合规要点**：库本身干净，但**运行时 CloudXR SDK/runtime 是 NVIDIA 专有**，且需 GPU + Linux。**这是"直接依赖"最需要评估的一项。**

---

## 10. 可复用性判定（分层给结论，因为差异极大）

| 层 | 判定 | 理由 |
| --- | --- | --- |
| **设备输入层**（`deviceio_base` + `deviceio_trackers` + `live_trackers` + `schema` + `oxr`） | **`wrapper-adapter`（推荐）**；条件满足可 `direct-use` | 抽象干净、运行时无关、**双端同一后端**、schema 有 conform 测试、有最小用法。**但 `direct-use` 会拉入 CloudXR（专有 + GPU + Linux）**。→ **建议包在自己的 `IXrInput` 之后，隔离 CloudXR 与 OpenXR 细节。** |
| **retargeting 层** | **`reference-only`**（可选 wrapper） | 设计优秀（DAG + 类型检查），但输出靠 `TensorReorderer.output_order` 匹配环境 action，**不匹配静默出错**；引入它会带进大量非输入层职责 |
| **机器人后端层** | **`custom`（必须自研）** | **库内不存在该层**。可参考 `IDeviceIOSink` 形状与 `EePoseRateLimiter` / `JointRateLimiter` |
| **mcap / plugin_manager** | **`direct-use`** | 独立性强，可直接用 |
| **viz（Televiz）** | `reference-only` | 需 Vulkan + CUDA，可选 |
| **整体框架** | **`reference-only`** | 架构参考价值极高（schema 契约、facade/impl 分层、codegen manifest、AGENTS.md 治理），但直接依赖代价大 |

**一句话建议**：**把 DeviceIO 设备层当作"统一 XR 输入层"的首选候选**（wrapper-adapter 形态：用它的 tracker 抽象与 FlatBuffers schema 作为输入契约，自己包一层，**不让 CloudXR 泄漏到业务层**）；retargeting / viz / 整体框架 = `reference-only`；**机器人后端必须 custom**。

---

## 11. 未验证项

| # | 未验证项 | 原因 |
| --- | --- | --- |
| 1 | 字节大小 / 行数 / 代码行数 | 子 Agent 无 shell |
| 2 | `reuse lint` 是否真的通过 | 无 shell |
| 3 | `ctest` / `pytest` 是否真的绿 | 无构建树 |
| 4 | **PICO / Quest 端到端实测** | 需 CloudXR + GPU + 真头显 |
| 5 | Apple Vision Pro 接入 | 需另建 v3.0.0+ 客户端 |
| 6 | 版本 / 提交 tag | 无 shell（仅确认 `VERSION` 存在） |
| 7 | codegen 产物（`${CMAKE_BINARY_DIR}/generated/trackers/*`） | configure 期生成，仓库内不存在 |
| 8 | **多机械臂扩展（Piper / UR）** | 库内只有 SO-101 / G1 / Sharpa / Wuji 的 retargeter，**无 Piper/UR** |
| 9 | Windows 可用性 | CMake 明示"not officially supported"；**本机为 Windows** |
| 10 | retargeting 层"GPU acceleration ready" | 仅 L0 声明，未找到强制 GPU 的源码证据 |

---

## 12. 对本项目的三条最关键输入

1. **双端并存的架构难题在这个项目里不存在** —— PICO 与 Quest 共用同一 OpenXR 后端（`live_deviceio_factory.cpp:154-170`），差异只在 CloudXR 的 `NV_DEVICE_PROFILE`。**这直接满足我们的硬约束。**
2. **时间同步有了成熟参照** —— `DeviceDataTimestamp` 的**双时钟**（`sample_time_raw_device_clock` + `sample_time_local_common_clock`）+ MCAP root_type 约定。**这是 `lbx-Franka-Teach` 缺失、我们必须自研的那一环的现成契约设计。**
3. **代价必须明算** —— 唯一被源码验证的 live 路径绑定 **CloudXR（NVIDIA 专有许可 + GPU + 官方仅 Linux）**，而**机器人后端层完全不存在（必须 custom）**。所以它不是"拿来即用的输入层"，而是"**一套优秀的契约 + 抽象，附带一个昂贵的传输 runtime**"。
