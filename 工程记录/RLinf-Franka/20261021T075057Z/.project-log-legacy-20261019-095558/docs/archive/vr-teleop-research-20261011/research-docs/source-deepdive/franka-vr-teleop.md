# 源码深挖 · `wengmister/franka-vr-teleop`

> **证据级**：**L2（源码可证）**——本地浅克隆逐行读取，非 README 推断。
> **规模**：26 文件 / 0.2 MB —— **全库可完整读完**，因此本笔记的覆盖度接近 100%。
> **仓库**：`https://github.com/wengmister/franka-vr-teleop`（61★，最近提交 2025-10-07）
> **论文**：LeVR: *A Modular VR Teleoperation Framework for Imitation Learning in Dexterous Manipulation*，arXiv **2509.14349**（2025）——作者自称"模块化框架"，与我们的分层思路同源。

---

## 1. 一句话

**它同时是我们最值得参考的 ②（核心层）与 ③（Franka 输出适配层）样本**，而且它用代码给出了「契约 C」的答案：**核心层与机器人侧之间的接口是「绝对末端位姿」**。

---

## 2. 实际链路（与 README 图不完全一致）

README 只画了一条线，代码里实际是**两个进程 + 两个网络跳**：

```
头显 App (quest-wrist-tracker)          ROS2 工作站                   实时 PC
  │  文本 UDP 9999¹                      │  文本 UDP 8888                │
  └──────────────────────────────────► vr_to_robot_converter.py ──────► franka_vr_control_client
       "Right wrist:, x,y,z,qx,qy,qz,qw, leftFist: open"   "x y z qx qy qz qw"      │
                                                                          libfranka
                                                                    关节速度 @1kHz
                                                                              ▼
                                                                        Franka (7 DOF)
```

| 环节 | 频率 | 代码位置 |
| --- | --- | --- |
| 头显手部追踪 | ≈65 Hz（USB/adb）／≈20 Hz（WiFi UDP） | `README.md:20-21`（作者自测 Quest 3s） |
| ROS2 节点控制环 | **100 Hz** | `vr_to_robot_converter.py:29` `control_rate = 100.0` |
| 机器人客户端控制环 | **1000 Hz** | `franka_vr_control_client.cpp:96` `CONTROL_CYCLE_TIME = 0.001` |
| C++ 内注释声称的 VR 更新率 | ≈50 Hz | `franka_vr_control_client.cpp:358` |

> ¹ **端口文档与代码不一致（真实缺陷）**：`README.md:120` 说"发送到端口 **9000**"，但代码默认 `vr_udp_port = 9999`（`vr_to_robot_converter.py:25`），而 `scripts/udp_listener.py:14` 又绑定 **8888**（那是机器人客户端用的端口，`franka_vr_control_client.cpp:40`）。**照 README 配端口会连不上。**

**频率解耦是明确的**：VR 输入 ≈50–65 Hz，IK+Ruckig 以 1 kHz 运行。**这印证了"三个频率不可混"的结论**，也说明"低频输入驱动高频控制环"需要显式设计（它靠 Ruckig 的 target-velocity=0 语义实现）。

---

## 3. ★ 契约 C 的答案：**核心层 ↔ 机器人侧 = 绝对末端位姿**

这是本轮最有价值的单条证据，直接影响 `OQ-001`（Q1）：

- ROS2 节点发出去的是 **position(x,y,z) + quaternion(qx,qy,qz,qw)** 的**绝对位姿**：
  `vr_to_robot_converter.py:447-455` `send_robot_command()` → `f"{pos} {quat}"` via UDP
- **IK 发生在机器人侧**，不在 ROS2 节点里：
  `franka_vr_control_client.cpp:406-409` `ik_solver_->solve_q7_optimized(target_pos, target_rot, ...)`
- 机器人侧最终输出的是 **关节速度**：
  `franka_vr_control_client.cpp:472` `return franka::JointVelocities(target_joint_velocities)`

**分层结果**：

| 层 | 谁承担 | 输出契约 |
| --- | --- | --- |
| ① XR 输入层 | 头显 App（`quest-wrist-tracker`） | 文本行（右手位姿 + 左拳状态） |
| ② 遥操作核心层 | **ROS2 节点（Python）**：坐标变换 + 滤波 + clutch | **绝对末端位姿** |
| ③ 输出适配层 | **C++ 客户端（Franka 专属）**：二次滤波 + IK + Ruckig + 限位 | 关节速度 → libfranka |

> **对 `OQ-001` 的意义**：这是「**方案 B**（核心层输出末端位姿，各机器人自解 IK）」的一个**已跑通真机**的实现。它的代价与收益都可直接观察：
> - **收益**：② 完全机器人无关（ROS2 节点只发位姿）；换机器人只需替换 C++ 客户端
> - **代价**：③ 变厚，且**安全与 IK 品质由各机器人侧各自负责**（这里 515 行 C++ 中的大部分都在处理 Franka 的 Q7 限位、碰撞阈值、阻抗）
> - **注意**：③ 的厚度意味着"多机械臂"并不是免费的——**每个机器人要重做一份 ③**，而不是改个配置

---

## 4. ⚠️ 契约 B 的实际形态：**正则解析文本行**（最脆弱的一环）

输入层**不是结构化契约**，而是对一行日志式文本做正则匹配：

```python
# vr_to_robot_converter.py:71
self.wrist_pattern = re.compile(
    r'Right wrist:, ([-\d\.]+), ([-\d\.]+), ([-\d\.]+), '
    r'([-\d\.]+), ([-\d\.]+), ([-\d\.]+), ([-\d\.]+), leftFist: (\w+)')
```

**这意味着**：

1. **只支持右手**（`Right wrist`）——左手只贡献一个 `leftFist` 布尔量用于 clutch。
2. **数据契约与"日志文本格式"绑定**——头显端改一个字符（空格、逗号、大小写），整条链路静默失效。代码里确实有 `_pattern_miss_count` 计数器来兜这个风险（`:308-313`），但这恰恰说明作者也知道它脆。
3. **没有时间戳字段**——`leftFist` 之外没有任何 header/timestamp。**我们做数采时无法从这一路拿到可信时间基准。**

> **对我们的直接含义**：**这个输入层必须整体替换**。它正是"契约 B 需要一个真正的结构化消息"的反面教材——而 `XRoboToolkit-Teleop-ROS/xr_msgs` 那套（Timestamp / head pose / 左右 controller / buttons / gripper / trigger）才是契约 B 应有的形态。

---

## 5. ② 核心层的实现机制（可复用清单）

### 5.1 坐标变换：**硬编码，且带手性翻转**

```python
# vr_to_robot_converter.py:263-285
robot_position = np.array([z, -x, y])            # VR(x右,y上,z前) → Robot(x前,y左,z上)
transform_matrix = np.array([[0,0,1], [-1,0,0], [0,1,0]])   # 含手性翻转
robot_matrix = transform_matrix @ vr_matrix @ transform_matrix.T
```

→ **这就是我此前警告的"组合时最容易炸的地方"的实证**：变换矩阵写死在代码里，不在配置里，且**没有参数化**。换成另一套头显坐标系就得改源码。

### 5.2 双重滤波（两处独立实现，参数还不一致）

| 位置 | 参数 | 实现 |
| --- | --- | --- |
| Python 侧 | `smoothing_factor = 0.7`（默认）；TCP launchfile 用 `0.05` | 位置：指数滑动 `α·prev + (1-α)·new`（`:357-358`）；姿态：**Slerp**，`t = 1-α`（`:371-376`） |
| C++ 侧 | `vr_smoothing = 0.05` | 位置：同式（`:196`）；姿态：**四元数 slerp**（`:197`） |

→ **同一条数据被滤波两次**，且两处 α 语义方向相反（Python 的 `smoothing_factor` 越大越"平滑"，C++ 的 `vr_smoothing` 越小越"响应"）。**这是组合式方案里典型的"参数语义不统一"陷阱。**

### 5.3 死区与工作空间限制（C++ 侧，`:47-52`）

| 机制 | 值 | 作用 |
| --- | --- | --- |
| 位置死区 | `0.001`（1 mm） | 抑制传感器噪声导致的漂移 |
| 姿态死区 | `0.03` rad（≈1.7°） | 同上 |
| 工作空间上限 | `max_position_offset = 0.75`（75 cm） | 相对初始位姿的**增量范数**被截断（`:215-218`） |

### 5.4 Clutch / pause（v1.2 加入）

- **触发**：左拳握紧（`leftFist == 'closed'`）→ `is_paused = True`
- **冻结**：暂停期间持续输出 `paused_vr_pose`（`:349-351`）
- **重锚**：松拳瞬间 `initial_vr_pose = current_vr_pose`（`:345`）——**这是 clutch 的关键动作**：把当前位置设为新参考原点，从而"离手重定位"而不产生跳变
- 需要配套的头显 App 分支（`dex-retargeter` branch，`README.md:30`）

### 5.5 渐进激活（防止接管瞬间猛冲）

```cpp
// franka_vr_control_client.cpp:88-90, 390-393, 431
static constexpr double ACTIVATION_TIME_SEC = 0.5;
activation_factor = min(1.0, elapsed / 0.5);
target_position[i] = current_pos + activation_factor * (ik_target_pos - current_pos);
```
→ 从"当前关节角"用 0.5 s 平滑过渡到 IK 解。**这是接管安全的关键设计**，我们的 P1 必须抄这一条。

### 5.6 关节级约束（Ruckig 输入，`:93-95`）

| 量 | 值（J0–J3 / J4–J6） |
| --- | --- |
| `max_velocity` | 1.8 / 2.0 rad·s⁻¹ |
| `max_acceleration` | 4.0 / 6.0 rad·s⁻² |
| `max_jerk` | 8.0 / 12.0 rad·s⁻³ |

> 注释直言这些值是为了"snappier response"**刻意调高的**（`:93-95` 原文 "Increase for responsiveness"）。**这是可调的安全-响应性权衡点**，不是 Franka 出厂限制。

### 5.7 IK 侧

- `geofik.cpp`（**1868 行**）：Franka **解析式 IK**，来自第三方 `PabloLopezCustodio/GeoFIK`
- `weighted_ik.cpp`（416 行）：多目标加权优化，权重（`:288-305`）
  - 可操作度（Yoshikawa）权重 1.0
  - 偏离中立位姿权重 2.0
  - 偏离当前位姿权重 2.0（**保轨迹连续，作者标注"very important"**）
  - **逐关节权重**：J0=3.0、J1=6.0（**基座稳定，高惩罚**）、其余 1.0–1.5
- **Q7 一维搜索**：在当前 q7 的 ±0.5 rad 内搜索候选（`:78, 402-403`），并用 Brent 法做 1D 优化（v1.1 changelog）

---

## 6. 安全机制清单（可直接作为我们 ② 的验收基线）

| # | 机制 | 位置 | 是否可复用 |
| --- | --- | --- | --- |
| 1 | 渐进激活 0.5 s | `:390-393` | ✅ 必抄 |
| 2 | 位置/姿态死区 | `:204-212` | ✅ 必抄 |
| 3 | 工作空间增量截断 75 cm | `:215-218` | ✅ 必抄 |
| 4 | IK 失败 → **保持上一目标不跳变** | `:438` | ✅ 必抄 |
| 5 | Ruckig 失败 → **零速度** | `:451-455` | ✅ 必抄 |
| 6 | 关节速度/加速度/jerk 限幅 | `:93-95, 313-315` | ✅ 必抄 |
| 7 | Q7 硬件保护限位（BiDexHand） | `:227-229, 436` | ⚠️ 机型相关 |
| 8 | 碰撞行为阈值 + 关节阻抗 | `:267-274` | ⚠️ 机型相关 |
| 9 | 启动前需人工确认 + 提醒急停按钮 | `:259-262` | ✅ 流程必抄 |
| 10 | **失联保护（watchdog）** | — | ❌ **缺失** |

### ⚠️ 缺失项 1：没有失联保护

`current_vr_command_` 在 `networkThread` 收到新包时才更新（`:159-160`）。**若头显掉线，代码不会超时清零**，而是继续持有最后一个位姿——由于 `target_velocity` 恒为 0（`:433`），机器人会"停在原位"而不是急停。

→ **这是"fail-hold"而非"fail-stop"。** 对我们的含义：**P1 的通过判据里"失联保护"必须我们自己实现**，不能指望参考实现提供。这是本轮发现的**明确能力缺口**。

### ⚠️ 缺失项 2：坐标系过原点的镜像陷阱

`README.md:31`（作者加粗警告）：

> "VR world frame has an origin, when crossing the origin while app is open will cause the coordinates to be **mirrored**. Remember to reset world frame by holding down meta menu."

→ **这是只有真机跑过才知道的坑**，任何文档普查都读不到。它直接支持我们"必须有 P0/P1 实测"的判断，也说明**契约 B 必须包含"世界系原点/重置"语义**，而不只是 pose+buttons。

---

## 7. 许可证实况（**补正 `license-audit.md`**）

这个仓库是**拼贴式授权**，逐文件核实后比"授权不清晰"更具体：

| 文件 | 来源 | 授权声明 | 证据 |
| --- | --- | --- | --- |
| 根 `LICENSE`（465 B） | 作者 | **仅免责声明，无任何授权授予** | `LICENSE:1` |
| `src/franka_vr_teleop/LICENSE`（17 行） | 作者 | **MIT 文本但无版权人署名** | 第 1 行即 "Permission is hereby granted" |
| `robot_client/src/franka_vr_control_client.cpp` | **Franka Robotics 官方示例** | **Apache-2.0 头** | `:2-3` "Copyright (c) 2023 Franka Robotics GmbH" |
| `robot_client/src/examples_common.cpp` | **Franka Robotics 官方示例** | **Apache-2.0 头** | `:1-2` |
| `robot_client/src/geofik.cpp`（1868 行） | **`PabloLopezCustodio/GeoFIK`** | **文件内无声明**；上游 **Apache-2.0**（29★，2026-08-02） | `:1-11` 仅作者/日期/版本 |
| `robot_client/src/weighted_ik.cpp` + 两个 `.h` | 作者自研 | 无声明 | `weighted_ik.cpp:1` 直接 `#include` |

**结论（更新 D 类定性）**：**不是"无授权"，而是"署名链断裂"**——实质代码可追溯到 **Apache-2.0**（Franka 示例 + GeoFIK 上游），但 vendored 的 `geofik.cpp` **丢掉了上游许可与署名**，作者自有部分又只有一份无署名 MIT 文本。

→ **对我们最有利的解读**：若要用它的代码，**最干净的路径是"顺着来源去找上游 Apache-2.0 原件"**（Franka 官方示例 + GeoFIK），而不是用这个二手拼贴。
→ 这也让"`reference-only`"的定位更精确：**读思路，然后从上游拿可合规的实现**。

---

## 8. 可复用性判定

| 层 | 判定 | 理由 |
| --- | --- | --- |
| ① 输入层 | **`reference-only`（且不推荐参考）** | 正则解析文本行，无时间戳，仅右手——**是反面教材** |
| ② 核心层 | **`reference-only` → 高价值参考** | 坐标变换/滤波/clutch/渐进激活/死区/工作空间截断，**机制清单完整且安全设计成熟**；但坐标系硬编码、无 watchdog、参数语义不统一，不能直接抄代码 |
| ③ Franka 适配层 | **`reference-only`** | 质量最高（1 kHz + Ruckig + 解析式 IK），但 515 行 C++ 与 Franka 深度绑定，且授权是二手拼贴 |
| 数据记录层 | **无** | 全库无任何数据录制代码（报告已记"数采：无"） |

---

## 9. 对我们决策的三条直接输入

1. **`OQ-001`（契约 C）**：本项目是「**输出末端位姿 + 各机器人自解 IK**」的**已跑通真机**证据。若采用方案 B，**每个机器人要重做一份 ③**（这里 ③ 有 515 行 C++ + 1868 行 IK）；若采用方案 A（核心层统一算 IK），则 ③ 变薄但核心层必须处理 7/6/6 自由度差异。**两个方案的代价现在都有可量化的参照。**
2. **契约 B 必须是结构化消息**：本项目用正则文本行，导致无时间戳、仅右手、改一个字符即静默失效。**我们应采用 `xr_msgs` 那类显式字段契约。**
3. **安全与失联保护要自己写**：参考实现的安全清单很成熟（可抄 9 条），但**失联保护缺失**——这必须是我们的增量，也是 P1 的必测项。

---

## 10. 未验证项

- **无 L3/L4 证据**：本笔记全部来自源码，**没有真机运行、没有实测延迟/丢帧数据**。作者的 65 Hz / 20 Hz 是自测声明（L0）。
- **头显端未深挖**：`wengmister/quest-wrist-tracker`（**265★，Apache-2.0**，2026-06-07）是配套 Quest 手部追踪 App，**尚未读源码**。它的星数比本仓库还高，且许可证清晰——**应作为 Quest 输入层的独立候选单独评估**。
- **浅克隆限制**：仅默认分支、depth=1，无法判断历史与分支状态（如 `dex-retargeter` 分支）。
- **`weighted_ik.cpp` 的算法细节未逐行核对**（416 行已读结构，未验证数值正确性）。
- **未验证真实控制品质**：1 kHz / <1 ms 轨迹计算均为 README 声明，未在代码中找到计时验证。
