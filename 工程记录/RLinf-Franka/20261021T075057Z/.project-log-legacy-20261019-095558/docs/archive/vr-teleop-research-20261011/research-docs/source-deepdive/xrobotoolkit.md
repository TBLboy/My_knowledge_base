# 源码深挖 · XRoboToolkit 三仓库

> **证据级**：**L2（源码可证）**，来源为**独立只读子 Agent 报告**。
> **范围**：`XRoboToolkit-PC-Service`（C++，Apache-2.0）+ `XRoboToolkit-Teleop-ROS`（ROS1+ROS2，MIT）+ `XRoboToolkit-Unity-Client-Quest`（Unity C#，MIT）。
> **前情**：这是**已被第三方实际复用**的输入层候选（`lerobot_ur_dual_vrteleop` 直接 import 其 Python 客户端）。
> ⚠️ **PICO 客户端（`XRoboToolkit-Unity-Client`）不在工作区** → parity 结论为**单边证据**。

---

## 1. 一句话

**它把"统一 XR 输入层"做成了"透传管道 + 口头 JSON 约定"，而不是"带 schema 的契约"**——这是它最大的架构风险，比许可证问题更实质。

---

## 2. 通信协议（`Manage_global.h`）

**自定义二进制帧 + 内嵌 JSON，走 TCP；服务发现走 UDP 广播。**

```cpp
// Manage_global.h:33-47
#pragma pack(1)
struct TCPMsgHead { unsigned char head; unsigned char cmd; uint32_t length; };
struct TCPMsgTail { uint64_t timeStamp; unsigned char tail; };

// Manage_global.h:13-31
#define DEFAULT_TCP_PORT 63901
#define BROADCAST_UDP_PORT 29888
#define BROADCAST_MEADIA_SERVER_INTERVAL 5000   // ms
#define TCP_CONNECTION_CHECK_INTERVAL 20000     // ms
#define TCP_SERVER_HEAD_CODE       0xCF
#define TCP_CLIENT_MSG_HEAD_CODE   0x3F
#define TCP_CLIENT_MSG_TAIL_CODE   0xA5
#define TCP_CLIENT_MSG_CONNECT        0x19
#define TCP_CLIENT_MSG_DEVICE_STATE_JSON 0x6D
#define TCP_CLIENT_MSG_SEND_BYTES_TO_DEVICE 0x72
```

| 项 | 值 |
| --- | --- |
| TCP 端口 | **63901**（`setting.ini:12-14`） |
| UDP 广播端口 | **29888**，每 **5 s** 通告一次 |
| 心跳 | 客户端每 **10 s** 发 `0x23`（`TcpHandler.cs:272-276`） |
| 离线判定 | 服务端 > **20 s** 无心跳（`tcpserverworker.cpp:260`） |
| Unity 发送频率 | **≈显示帧率 ≈90 Hz**（`UIOperate.cs:99` `systemDisplayFrequency = 90.0f`；README 声明 90Hz/56B 属 L0） |

---

## 3. ⚠️ 最严重的架构风险：**XR 数据契约没有权威定义文件**

**PC-Service 不解析任何 XR 字段，只做透传**：

```cpp
// Business/DeviceManage/devicemanagement.cpp:229-234
case TCP_CLIENT_MSG_DEVICE_STATE_JSON:
    emit recvDeviceMessageSignal(uid, PXREAServerMsgDeviceStateJson, tcpMessage.m_msg);
```

- `PXREAService.proto` 只是 **gRPC 传输外壳**（`SendBytesToDevice` / `WatchServerFeedback` …），**不含 pose / 按钮字段**
- 字段语义**只存在于 README 与消费方代码里** → **没有单一权威 schema 文件**

**同一个协议里存在三种时间基准**：

| 位置 | 实现 | 单位 |
| --- | --- | --- |
| 载荷 `timeStampNs` | `TrackingData.cs:148-149` → `Utils.cs:14-19`（`(UtcNow - epoch).TotalMilliseconds * 1e6`） | **纳秒**（注释误写 "microseconds"） |
| 帧尾（客户端） | `PackageHandle.cs:151` `DateTimeOffset.Now.ToUnixTimeMilliseconds()` | **毫秒** |
| 帧尾（服务端） | `Manage_global.h:84` `QDateTime::currentSecsSinceEpoch()` | **秒** |

**另有第二套时间基准**：`predictTime = Time.unscaledTimeAsDouble * 1e6`（应用相对时间，微秒，`TrackingData.cs:103-104`）。

> **对我们的含义**：若直接复用，等于**把契约押在一份会漂移的 JSON 约定上**，且协议**无版本号**。若要自建统一层，应**重新定义带版本号、带单位、统一时间基准的 schema**。

---

## 4. 与 `xr_msgs` 的一致性：**不一致（有损且更窄）**

`ros2/xr_msgs/msg/`：`Custom.msg` = `timestamp_ns / input / head / left_controller / right_controller`；`Head.msg` = `float32[7] pose / int32 status`；`Controller.msg` = `axis_x, axis_y, axis_click, gripper, trigger, primary_button, secondary_button, menu_button, float32[7] pose, status`。

| 差异 | 证据 |
| --- | --- |
| ROS 消息**只承载 Head + Controller**，**无 Hand / Body / Motion** | `publisher.cpp:184-187` 注释占位 `// hand` `// body` |
| `timestamp_ns` 与 JSON 纳秒一致 | `publisher.cpp:130` |
| **`controller.status` 被硬编码为 `3`** → **丢失真实跟踪状态** | `publisher.cpp:167` |
| 键名映射层一致（`axisX/axisY/axisClick/grip/trigger/primaryButton/secondaryButton/menuButton/pose`） | `publisher.cpp:154-161` |

---

## 5. ★ PICO vs Quest parity：**Quest 是 PICO 的"功能裁剪分支"**

> 单边证据（PICO 客户端不在工作区）。Quest 侧的删除是**源码里明写的**：

**Quest 明确缺失（`[代码]`）**：

| # | 缺失项 | 证据 |
| --- | --- | --- |
| 1 | **Body / Motion 跟踪整体删除** | `TrackingData.cs:141-146`：`// Remove PICO-specific tracking features for now` + `totalData.Remove("Body")` / `Remove("Motion")` |
| 2 | **独立外设透传整段注释掉** | `ExtraDev/ExtDevTracking.cs:12-41,69-81`（`PXR_MotionTracking.ExtDevPassDataAction` 全注释） |
| 3 | **Body 模式 UI 全注释** | `UIOperate.cs:195-239,355-396` |
| 4 | **头部 JSON 缺 `handMode`** | PICO 头部帧含 `handMode`（PC-Service README:359,368），Quest `GetHeadTrackingData()` 只写 `pose` + `status`（`TrackingData.cs:187-206`） |
| 5 | **设备 SN 硬编码** | `UIOperate.cs:68,80` `SetDeviceSN("TestDevice")`；企业服务取 SN 被注释（`:69-71`） |
| 6 | **企业功能缺失** | USB 网络共享 `NetshareTog` 被隐藏（`:62-66,168-178`）；安全围栏/VST 全注释（`Main.cs:14-16,40-71`）；Remote Vision "not available on Quest"（README:30） |
| 7 | 手部半径 `r` 恒为 0 | `TrackingData.cs:347` |

**Quest 保留（`[代码]`）**：头部 6DoF、控制器 6DoF + 按键、**hand tracking 支持**（走 **OVR/Oculus.Interaction**，26 关节，`TrackingData.cs:297-351`）。

**README 与代码冲突（重要）**：

| 类型 | README | 代码 |
| --- | --- | --- |
| `missing-implementation` | `:26` "Body tracking for Quest. **Coming soon**" | 已删除（`TrackingData.cs:141-146`） |
| `conflict` | `:136` "XR Hands (`com.unity.xr.hands`) are **not supported**" | `Packages/manifest.json:11-12` **声明了** `com.unity.xr.hands:1.6.0` + `com.unity.xr.interaction.toolkit:3.2.0` |
| 说明力为零 | — | **`RuntimeActionBindings.json` 是空文件**：`{"InputActionDefinitions": [],"InputActionSets": []}`。真正绑定在 `Assets/InteractionTools/MetaInputActions.inputactions` |

> **对我们的含义**：**"已被第三方复用的统一输入层"目前只覆盖 head + controller + hand；body / tracker 在 Quest 侧不存在。** 我此前报告里"XRoboToolkit-Teleop-ROS 只支持 PICO 不支持 Quest"的表述**需要修正**：Quest 客户端**存在且是 MIT**，但**功能被裁剪**，且 ROS 消息只承载 head+controller。

---

## 6. 可重建性：**纯源码构建不成立**

**仓库内含大量预编译二进制**：

| 类别 | 内容 |
| --- | --- |
| 预编译客户端 SDK | `RoboticsService/SDK/{win/64,linux/64,linux_aarch64/64}/PXREARobotSDK.{dll,lib,so}` |
| 预编译第三方 | `GrpcSDK/lib/release/*.lib`（grpc++/grpc/libprotobuf/absl_*/re2/ssl/zlib/upb/cares/gpr… **100+ 静态库**）；`GrpcSDK/include/`（**仅头文件，无源码**） |
| 预编译可执行 | `Redistributable/win/{RobotDemoQt.exe, RobotDataRecorder.exe, ConsoleDemo.exe, run3D.exe}` |
| PICO 私有 SDK | `SDKDemo/UnityBin/.../Plugins/x86_64/{PicoSpatializer.dll, libpxrplatformloader.dll}` |

- **`PXREARobotSDK` 有源码**（`RoboticsService/PXREARobotSDK/`），但 `CMakeLists.txt:186,294-299` **链接预编译 gRPC/absl/zlib/ssl 静态库**
- **主服务有源码**（`CommonUtils/ DeviceConnectionManager/ Business/ PXREAGRPCServer/ RoboticsServiceProcess/`），但**依赖外部 Qt 6.6.3**（`README.md:129`）
- **gRPC 本身无源码**

**`THIRD_PARTY_NOTICE.txt` 要点**（全文 306 行）：

- `:9-10` `Apache License 2.0 (grpc, OpenSSL)`
- `:196-197` `Unity Companion License`，含 🔴 **`:217-218`**：

> *"No other exercise … may the Software be used for **competitive analysis** or to **develop a competing product**"*

- 🔴 **`:223-242`**：衍生作品 IP **转让给 Unity**
- ⚠️ **未声明 Qt 许可**（Qt 6.6.3 为外部依赖，LGPL/商业双许可未在 NOTICE 中声明）→ **许可链不完整**

---

## 7. 下游接入点

**Python/C++ 下游 = gRPC 客户端 SDK（非 pybind）**：

- 传输：**gRPC over TCP，默认 `127.0.0.1:60061`**（`PXREARobotSDK.cpp:298-312`；服务端 `PXREAGRPCServer.cpp:9-11`）
- 数据入口 = **服务端流 `WatchServerFeedback`**，`ServerFeedback.name == "deviceStateJson"` 携带 `DeviceStateJson{devid, statejson}`（`.proto:167-171`）
- 对外 C API：`PXREAInit / PXREADeinit / PXREADeviceControlJson / PXREASendBytesToDevice`（`PXREARobotSDK.h:91-115`）
- **无 Python binding** → Python 只能自己用 `grpc-python` 连 60061，或经 ROS

**ROS 侧**：

- 节点 `xr_publisher`，topic **`xr_pose`**，类型 **`xr_msgs/Custom`**（`ros2/picoxr/src/publisher.cpp:95-97`；ROS1 同）
- Python 示例经 rclpy 订阅同一 topic（`examples/python/xr_mujuco_ur5e.py:34-38`）
- ⚠️ **构建依赖外部 SDK 路径**：`ros2/picoxr/CMakeLists.txt:38-51` 期望 `/opt/apps/roboticsservice/SDK`，找不到直接 `FATAL_ERROR`；且期望的 `SDK/x64` 与 PC-Service 实际输出 `SDK/linux/64` **不一致**（集成风险，`[推断]`）

---

## 8. 许可证

| 仓库 | 根 LICENSE | 备注 |
| --- | --- | --- |
| `XRoboToolkit-PC-Service` | **Apache-2.0** | 但 `THIRD_PARTY_NOTICE.txt` 含 Unity 限制性条款；**未声明 Qt 许可** |
| `XRoboToolkit-Teleop-ROS` | **MIT** | ⚠️ **内部不一致**：`ros2/picoxr/package.xml:8` 与 `ros1/picoxr/package.xml:7` 写 **Apache-2.0**；`ros2/xr_msgs/package.xml:8` 写 `TODO: License declaration` |
| `XRoboToolkit-Unity-Client-Quest` | **MIT** | 依赖 `com.meta.xr.sdk.interaction.ovr:72.0.0`（**Meta 专有 SDK**，条款未在本仓库声明） |

---

## 9. 可复用性判定

| 组件 | 判定 | 理由 |
| --- | --- | --- |
| **TCP/UDP 帧协议 + 帧码定义** | `reference-only → wrapper-adapter` | 协议简单完整，但**无版本号、无 schema、三种时间基准**；可作参考，**自建建议重定义带版本号 schema** |
| **PXREARobotSDK（gRPC 客户端）** | **`direct-use`（有前提）** | 源码完整、C API 稳定、跨平台。前提：接受 gRPC `127.0.0.1:60061`、接受仓库内预编译 grpc 库、核对 Qt/gRPC 许可 |
| **RoboticsService 主服务** | `direct-use（二进制）` | 源码在但强依赖 Qt 6.6.3 + 预编译 grpc；**自建成本高于直接用发行包** |
| **Teleop-ROS `picoxr` / `xr_msgs`** | `direct-use → wrapper-adapter` | 与 SDK 解耦良好、MIT、topic 清晰；但 msg 只覆盖 Head/Controller，`controller.status` 硬编码 → **需扩展** |
| **Unity Quest 客户端** | **`reference-only`** | 强绑定 Meta XR SDK/OVR/专有 aar；功能被裁剪；SN 硬编码；`RuntimeActionBindings.json` 空。适合作为"如何把 Quest 映射到 PICO JSON 契约"的参考 |
| **"统一 XR 输入层"整体** | **`wrapper-adapter`** | 建议：**保留 PC-Service 与 SDK 作传输层，自建一层显式的、带版本与单位的 XR schema（含 hand/body 与 ns 时间戳），双端适配到该 schema** |

---

## 10. 未验证项

1. **PICO 客户端仓库缺失** → parity 为单边证据
2. **无 shell** → 未编译、未运行、未验证 `Redistributable/win` 是否有服务端 `roboticsservice.exe`（目录中只见 `runService.bat` 与 3 个 demo exe）
3. **二进制内容未核** → `.dll/.so` 是否与仓库 `.cpp` 同版本未知
4. 文件数 1973 / 体积 772 MB 未复核
5. 实际发送频率（90Hz/56B）未实测
6. ROS SDK 路径 `SDK/x64` vs `SDK/linux/64` 未确认
7. Quest 本地录制落盘代码未定位
8. `count=26` 为硬编码，实际场景关节列表长度未验证
9. **Qt / Meta XR SDK 许可条款未声明 → 需法务确认**
10. `handMode` 等 PICO 独有字段缺失是否被下游依赖，未验证

---

## 11. 最重要的 3 个发现

**F1｜"统一输入层"目前没有权威契约文件。**
PC-Service 是透传代理（`devicemanagement.cpp:229-234`），字段语义只存在于 README 与消费方代码。协议无版本号，且**同一协议内 ms/s/ns 三种时间基准**。**任何"统一输入层"若直接复用，等于把契约押在一份会漂移的 JSON 约定上。**

**F2｜Quest 客户端是 PICO 的裁剪分支，README 与代码矛盾。**
源码明写 `Remove PICO-specific tracking`、ExtDev 全注释、Body UI 全注释、SN 硬编码 `"TestDevice"`；README 却写 Body "Coming soon"、XR Hands "not supported"（同时 `manifest.json` 又声明依赖）。**当前"统一输入层"只覆盖 head + controller + hand。**

**F3｜可重建性与许可链都有问题。**
gRPC/protobuf/absl/Qt/PICO SDK 全是预编译；`THIRD_PARTY_NOTICE` 含 Unity 的**竞争用途禁令**与**衍生 IP 转让**条款；Qt 许可未声明。**纯源码构建不成立，且需法务评估。**

---

## 12. 对本项目的直接输入

1. **不要把"统一 XR 输入层"的契约押在 XRoboToolkit 的 JSON 约定上** —— 它是**传输层**（可用），不是**契约层**（须自建）。
2. **若采用它，采用范围应限定为**：PC-Service（发行包二进制）+ PXREARobotSDK（gRPC C API）+ `xr_msgs`（需扩展 hand/body 与 status）。**不要**把 Quest Unity 客户端当统一层核心。
3. **它有一个 `IsaacTeleop` 没有的优点：轻、跨平台、无 GPU 依赖、已被第三方 Python 项目实际 import。** 这是它与 IsaacTeleop（CloudXR + GPU + Linux）之间真正的取舍轴。
