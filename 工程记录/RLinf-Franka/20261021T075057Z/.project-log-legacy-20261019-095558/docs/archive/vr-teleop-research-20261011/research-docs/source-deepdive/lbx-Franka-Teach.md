# 源码深挖 · `Labelbox/lbx-Franka-Teach`

> **证据级**：**L2（源码可证）**，但**来源为独立只读子 Agent 报告 + 主 Agent 抽查复核**（抽查项见 §11）。
> **规模**：123 文件 / 1.5 MB；核心 `mcap_data_recorder.py` 1983 行 + `oculus_vr_server.py` 1849 行。
> **仓库**：`https://github.com/Labelbox/lbx-Franka-Teach`（9★，最近提交 2025-05-30）
> **原定位**：报告称其为「**最好的 MCAP/DROID 数采参考**」——**本轮深挖后该定位被推翻**（见 §2）。

---

## 1. 一句话

**它是一份"读得懂、但用不了、也不能照抄"的架构参考**：记录了真实可用的异步线程拓扑与 MCAP schema 设计，但**没有许可证、依赖目录全空、含明文凭据**，且**"DROID 兼容"名不副实**。

---

## 2. ⚠️ 最重要更正：「DROID 兼容」不成立

| 说法 | 实测 |
| --- | --- |
| 报告 v1.3 / 汇报提纲附录 A：「✅ MCAP/DROID」 | **写的是自定义 `labelbox_robotics` schema 的 MCAP**（`mcap_data_recorder.py:109/190/212`），**不是 DROID 数据集格式** |

**DROID 数据集规范要素的存在性核查（我的抽查）**：

| 要素 | 全树命中 |
| --- | --- |
| `metadata.json`（per-episode 元数据） | **0** |
| `trajectory.h5` | **0** |
| 语言标注（`language` / `instruction` / `annotation`） | **0**（仅命中 tkinter 的 Label 控件与文档措辞） |

→ **DROID 的目录结构（`task/date/episode`）、per-episode meta、语言标注、相机外参布局、`trajectory.h5` 在代码中完全不存在。**
→ README 里的 "DROID-compatible"（`README.md:8,217`）实指**控制参数**兼容（`oculus_vr_server.py:207-221` 注释 "DROID VRPolicy exact parameters"，`:224` 的 `rmat_reorder = [-2,-1,-3,4]`），**不是数据格式兼容**。

> **对我们的含义**：若目标规范定为 **DROID 官方格式**，**这个仓库不能作为依据**，必须回到 DROID 官方规范自行实现。这是一个需要用户决策的岔路（见 §12 建议 1）。

---

## 3. ⚠️ 第二处更正：`40Hz / 6.6Hz` 的真实来源

汇报提纲 §3 判断 6 曾写「`lbx-Franka-Teach` 自述：**40Hz 记录数据，但机器人控制只有 6.6Hz**」。**两个数字都不是设计参数**：

**「40Hz」= 性能模式下的 2 倍硬编码**（我的抽查确认）：

```python
# frankateach/constants.py:39-42
VR_FREQ = 20 ; CONTROL_FREQ = 20 ; STATE_FREQ = 100 ; CAM_FPS = 30

# oculus_vr_server.py:441-443
if self.enable_performance_mode:
    self.control_hz = CONTROL_FREQ * 2   # Double the frequency for faster response
# :497
self.recording_hz = self.control_hz      # Record at same rate as control target
```

- `run_server.sh:51,55` **总是带 `--performance`** → 所以"40Hz"只在用该脚本启动时成立
- **`python oculus_vr_server.py` 直启 = 20Hz**（记录频率跟随控制频率）
- 代码里还有运行时实测打印（`:1439`）`📊 Recording frequency: {actual_freq:.1f}Hz (target: {self.recording_hz}Hz)` → **作者自己也知道这是"目标值"而非保证值**

**「6.6Hz」= 观测值，代码里不存在**（我的抽查确认：`.py/.yaml/.sh` 全树 `6.6` **0 命中**）：

- 仅出现在文档（`README.md:250`、`ASYNC_ARCHITECTURE_README.md:87,128`）
- 唯一代码线索是 `oculus_vr_server.py:1481-1483` 打印 `📡 Avg robot comm: {avg_comm_time*1000:.1f}ms`
- 机器人通信是**同步 REQ/REP**（`:1472-1474`）→ **6.6Hz ≈ 1/149ms，是"硬件往返延迟的倒数"，是测量结果**

> **结论（结论本身不变、但表述要改）**：「**录制帧率 ≠ 控制频率**」这一判断**反而被强化**——默认配置下是 **20Hz 记录 vs 149ms 同步往返**；`--performance` 下是 40Hz vs 同样 149ms。**同步阻塞的机器人通信是真正的瓶颈**，且它无法通过提高记录频率改善。

---

## 4. ⚠️ 第三处更正：依赖目录全部为空

我此前的结构普查把这些目录当成"有内容"，**实测全部为 `entries=0`**（未初始化的 gitlink / submodule 占位）：

| 目录 | 实测 |
| --- | --- |
| `deoxys_control/` | **0 entries** |
| `mcap/` | **0 entries** |
| `oculus_reader_app/` | **0 entries** |
| `franka_description/` | **0 entries** |
| `lbx-droid-franka-robots/` | **0 entries** |
| `simulation/` | 8 entries（非空） |

且**无 `.gitmodules`**。`auto_arm.sh:1` 内容是一行文本 `deoxys_control/deoxys/auto_scripts/auto_arm.sh` —— **符号链接在 Windows 下被 git 拍平成文本文件**（`.git/config:6 symlinks = false`）。

> **仓库在 Windows 上克隆后无法运行**，且**关键依赖（deoxys / oculus_reader / franka_description）全部缺失**。

---

## 5. 数据记录层：真实可用的部分（**这是它的价值所在**）

### 5.1 单文件 MCAP + schema 注册

- 写入：`mcap_data_recorder.py:27-28`（`import mcap` / `from mcap.writer import Writer`）、`:401-402`（`Writer(...)` / `.start("labelbox_robotics", library="frankateach")`）
- 文件生命周期：先落 `~/recordings/failure/`，成功后 rename 到 `success/`（`:399`、`:834-835`）

### 5.2 一条 episode 的通道

| channel | 内容 | 位置 |
| --- | --- | --- |
| `/robot_state` | joint pos/vel/effort、cartesian_position、gripper pos/vel | `:1127-1142` |
| `/action` | 7 维 `[lin3, ang3, gripper]` | `:1235-1244` |
| `/vr_controller` | poses（4×4 展平为 16）、buttons、movement_enabled、controller_on、success/failure | `:1257-1310` |
| `/joint_states` | ROS2 JointState（仅可视化） | `:1155-1166` |
| `/tf`, `/tf_static` | 由关节角**手算**的 FR3 链 | `:1531-1810` |
| `/camera/{id}/compressed` | JPEG q90 base64 | `:1324-1344` |
| `/camera/{id}/depth` | uint16 mm base64 | `:1358-1396` |
| `/camera/{id}/camera_info` | K/R/P/D 齐全 | `:1411-1465` |
| `/robot_description` | URDF 字符串 | `:493-514` |

### 5.3 异步拓扑（**最值得抄的部分**）

四线程 + 有界队列：

| 线程 | 队列 | 满时策略 |
| --- | --- | --- |
| `_data_recording_worker`（节流 `:1389`） | `mcap_queue = Queue(maxsize=1000)`（`:487`） | **丢帧**并打印 `⚠️ MCAP queue full, dropping frame`（`:1430-1431`） |
| `_camera_recording_worker` | `buffer_size=5`（`camera_manager.py:536-543`） | 丢最旧 |
| 机器人指令 / 响应 | `maxsize=2` / `maxsize=2`（`:501-502`, `:1622-1630`） | 丢最旧 |
| writer | `_data_queue`（`mcap_data_recorder.py:89`）→ 消费线程 `:987-1042` | — |

### 5.4 时间戳：**单点主机墙钟**（⚠️ 这是它的核心缺陷）

- 记录线程取 `timestamp = time.time()`（`oculus_vr_server.py:1419`）
- 组装为 `read_start` / `read_end` **同一个值**（`:1272-1273`）
- writer 取 ns：`mcap_data_recorder.py:1067`
- 该 ns 被同一 timestep 的 robot_state / joint_states / tf / action / vr_controller **共用**（`:1147-1148, 1227-1228, 1249-1250, 1315-1316, 1789-1790`）
- **相机帧用各自 `time.time()`**（`camera_manager.py:218`），**不在 timestep 内**、独立线程写入

> ⚠️ **相机与机器人仅靠主机墙钟对齐**，**没有硬件触发、没有曝光时间戳、没有时钟同步**。对我们的数采质量目标而言，**这是必须替换的部分**（正是 `OQ` 里未决的"时间同步横切关注点"）。

### 5.5 ⚠️ 会污染训练数据的两个坑（**必须避开**）

1. **伪造关节角**：`_write_joint_state_for_visualization`（`:1175-1200`）在无关节数据时**用笛卡尔反推或默认 home 位置伪造**，该通道**不可用于训练**。
2. **预测状态入录**：`oculus_vr_server.py:1659-1666` 的"预测控制"用**目标位姿顶替真实状态**记入数据 → **不可照抄**。

---

## 6. 机器人后端：走 deoxys，不是 libfranka

```
franka_server.py:7-13   from deoxys.utils import YamlConfig; from deoxys.franka_interface import FrankaInterface
franka_server.py:82-90  class Robot(FrankaInterface)  # control_freq=CONTROL_FREQ, has_gripper=True
franka_server.py:133-137 self.control(controller_type="OSC_POSE", action=..., controller_cfg=...)
```

- **代码内无任何直接 libfranka 调用**；libfranka 仅经 deoxys 间接使用
- `deoxys_control/` **为空** → 非 vendored；需用户单独 clone 安装（`README.md:62-75`），上游应为 `NYU-robot-learning/deoxys_control`
- ⚠️ 报告曾记其依赖 `UT-Austin-RPL/deoxys_control` 的 1★ fork；**本轮无法比对**（无源码）

---

## 7. XR 输入：两套并存，契约互不兼容

**现代路径**：`oculus_reader` Python API（`oculus_vr_server.py:52,290-293,567`）

由使用点反推的返回结构（**未与官方源码核对**）：

- `poses`：`dict[str, 4×4 np.ndarray]`，键 `"l"` / `"r"`
- `buttons`：`dict`，键含 `A/B/X/Y`、`RG/LG`（握持）、`RJ/LJ`（摇杆）、`rightTrig/leftTrig`（取 `[0]` 为 float）

**旧路径**：TCP 文本协议（`frankateach/oculus_stick.py:20-22` 订阅 `192.168.1.54:5555`；`frankateach/utils.py:39-75` 按 `"|"` 分左右、`";"` 分段解析）

> **可确定的替换缝很窄**：统一输入层只需实现 `get_transformations_and_buttons() -> (poses, buttons)` 即可整体替换现代路径。**但两套路径互不兼容**，替换时须明确选一。
> **XRoboToolkit 兼容性：本仓库零引用，无法在此验证**（未验证项）。

---

## 8. 可复用性判定

| 范围 | 档位 | 理由 |
| --- | --- | --- |
| 整个仓库 | **`reference-only`** | 无许可证；依赖目录全空；硬编码内网 IP 与开发机路径；含明文凭据 |
| `mcap_data_recorder.py`（1983 行） | **`reference-only` → `custom`** | schema 设计、队列/线程模型、成功失败生命周期、相机标定映射**可作设计参照**；代码本身不可抄 |
| `mcap_verifier.py`（455 行，回读校验） | **`reference-only`**（移植成本最低） | 逻辑通用，依赖仅 `mcap` + `numpy` |
| 异步线程拓扑（`oculus_vr_server.py`） | **`reference-only`** | 拓扑可借鉴；但须剔除"预测状态入录" |
| `camera_manager.py`（630 行） | **`reference-only`** | `CameraFrame` dataclass + 采集线程 + 丢帧策略，RealSense/ZED/USB 三实现 |
| `direct-use` / `wrapper-adapter` | **均不成立** | 无法直接运行（依赖缺失 + 路径硬编码），也无授权做适配分发 |

---

## 9. 安全与合规（**重要**）

- 🔴 **明文凭据**：`README.md:146-147` 含 `Username` / `Password`（**内容不在此转录**）
- 🔴 **内网拓扑与 SSH 主机**：`README.md:126-130`（`HostName 10.19.248.70` / `User robot-lab`）、`README.md:58,110,144-145`、`oculus_control_readme.md:10,178`
- 🟠 **开发机绝对路径**：`apply_hand_offset.py:23,96,118`
- 🟡 **相机序列号**：`configs/cameras_intel.yaml:6,24`
- 未发现密钥 / token / `.env`

> **行动项**：若本项目要做归档或分享，**这些内容必须先脱敏**。另：`~/` 目录（字面名 `~`）是 `Path("~/...")` 未 `expanduser` 的 bug 产物，内含 4 个二进制 MCAP 测试录制（2 个 0 秒、2 个 2 秒）。

---

## 10. 对本项目的直接输入

1. **DROID 兼容性不能靠它** —— 若目标规范选 DROID，须回到官方规范；若选"自定义 MCAP + Foxglove schema"，则它的 schema 设计可直接参考（且 §5.2 的通道划分是合理起点）。
2. **可移植的三个设计点**：① `mcap_verifier.py` 的**回读校验**思路（频率统计、通道完整性、字段尺寸、范围检查）；② **记录/控制/通信三线程 + 有界队列丢帧**策略；③ **每 timestep 单时间戳贯穿多通道**的 schema 设计。
3. **必须替换的三处**：① 时间戳改为**硬件/曝光对齐**（现在是主机墙钟单点）；② 剔除**伪造关节角**通道；③ 剔除**预测状态入录**。
4. **它的"预测控制"值得单独研究**：用目标位姿顶替真实状态是为了压低延迟，但对训练数据有害——**这是一个"响应性 vs 数据真实性"的真实权衡案例**。

---

## 11. 主 Agent 抽查复核记录

以下 4 条由我独立复跑命令确认（不盲信子 Agent 报告）：

| # | 断言 | 抽查结果 |
| --- | --- | --- |
| 1 | 依赖目录为空 | ✅ 确认（5 个目录 `entries=0`） |
| 2 | `40Hz = CONTROL_FREQ(20) × 2`，仅 `--performance` | ✅ 确认（`constants.py:40` + `oculus_vr_server.py:443`） |
| 3 | `6.6` 不出现在代码/配置 | ✅ 确认（`.py/.yaml/.sh` 全树 0 命中） |
| 4 | DROID 规范要素缺失 | ✅ 确认（`metadata.json` / `trajectory.h5` / 语言标注 均 0 命中） |

其余内容来自独立只读子 Agent 报告，**未逐条复跑**（标记为 `subagent-derived`）。

---

## 12. 未验证项

- **`verification_capability_missing`（子 Agent 侧）**：无 `shell` 权限 → 无法 `git status/log/submodule`，"空目录 = 未初始化 submodule"与"`~` 目录是否已被上游提交"均为**推断**。
- **二进制不可读**：4 个 `.mcap` 的真实通道/字段/时间戳未解析。
- **无法比对 deoxys 上游**：`deoxys_control/` 为空；`FrankaInterface.control_freq` / `num_steps` / OSC_POSE 内部 IK 行为未验证。
- **`OculusReader.get_transformations_and_buttons()` 的精确返回结构**仅从使用点反推，**未与官方源码核对**。
- **文档漂移未穷尽**：`MCAP_RECORDING_README.md:202,163` 引用的 `mcap_data_reader.py` / `test_joint_recording.py` **在仓库中不存在**（`missing-implementation`），是否在其他分支存在未验证。
- **无 L3/L4**：未真机运行。
- **浅克隆**：仅默认分支、depth=1。
