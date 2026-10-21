# 源码深挖 · `unitreerobotics/televuer`（XR 输入层，**此前完全缺失**）

> **证据级**：**L2（源码可证）**，由**主 Agent 亲自精读**（非子 Agent 转述）。
> **为什么单独一条线**：`xr_teleoperate`（1697★）的 XR 输入层是 **submodule**，本地克隆后**目录为空**（0 条目）→ 上一轮子 Agent 的所有输入层结论都只能停留在「调用方视角」。
> **本轮补齐**：主 Agent 用 shell 克隆了 3 个 submodule → **本地克隆 19 → 22**。
>
> | 仓库 | 许可证 | 文件数 | 大小 |
> | --- | --- | --- | --- |
> | `televuer` | **MIT**（© 2025 Unitree Robotics） | 38 | 0.1 MB |
> | `teleimager` | **Apache-2.0** | 42 | 1.2 MB |
> | `dex-retargeting`（`silencht` fork） | **MIT**（含 DexPilot 原作者 Yuzhe Qin 的 `license_legacy/` MIT） | 45 | 0.2 MB |
>
> 三个 `fsck` 均 clean。

---

## 1. 一句话

**这是本轮唯一一个「XR 输入层被做成独立 pip 包、且契约可读」的实现**——它证明了「XR 层只输出 SE3 位姿 + 手部关键点，机器人差异全部下沉到 IK 侧」这条分层是**被工程验证过**的；但它的**失联保护是假的**（见 §4）。

---

## 2. ★★ 输入层契约：`TeleData`（此前完全不可见）

`televuer/src/televuer/tv_wrapper.py:173-225` —— **一个 32 字段的 dataclass**：

### 2.1 位姿（核心）

```python
@dataclass
class TeleData:
    head_pose: np.ndarray          # (4,4) SE(3) pose of head matrix          :175
    left_wrist_pose: np.ndarray    # (4,4) SE(3) pose of left wrist of arm    :176
    right_wrist_pose: np.ndarray   # (4,4) SE(3) pose of right wrist of arm   :177
```

> **契约形态 = 末端位姿（4×4 齐次 SE3），不是关节角。** 与 `PiperPilot`（`action.arm_eef: 7`）、`franka-vr-teleop`（末端位姿）**同侧**，与 `pico-piper-teleop`、`lerobot_ur_dual_vrteleop`（关节角）**相反**。
> 全仓 `grep control_space` → **0 命中**：这是**硬编码的单一通道**，没有参数化开关。

### 2.2 手部

| 字段 | 形状 | 行 |
| --- | --- | --- |
| `left/right_hand_pos` | **(25,3)** 3D 位置 | `:182-183` |
| `left/right_hand_rot` | **(25,3,3)** 旋转矩阵（需 `return_hand_rot_data=True`） | `:184-185` |
| `left/right_hand_pinch` / `pinchValue` | bool / float（**~15.0 → 0.0**，0 表示完全捏合） | `:187-188, 192-193` |
| `left/right_hand_squeeze` / `squeezeValue` | bool / float（**0.0 → 1.0**） | `:189-190, 194-195` |

> 25 关节 = WebXR hand-input 规范（注释引用 `immersive-web.github.io/webxr-hand-input/`）。

### 2.3 控制器

| 字段 | 语义 | 行 |
| --- | --- | --- |
| `left/right_ctrl_trigger` / `triggerValue` | bool / float（**10.0 → 0.0**，0 = 完全按下） | `:201-202, 218-219` |
| `left/right_ctrl_squeeze` / `squeezeValue` | bool / float（**0.0 → 1.0**）—— **这就是 clutch 的物理输入** | `:203-204, 220-221` |
| `left/right_ctrl_aButton` / `bButton` | bool（左手 A/B，右手 A/B） | `:205-206, 222-223` |
| `left/right_ctrl_thumbstick` | bool（摇杆按下） | `:207, 224` |
| `left/right_ctrl_thumbstickValue` | **(2,)** 归一化向量，**且注释给出精确轴向定义**（front=(0,-1)，back=(0,1)，left=(-1,0)，right=(1,0)） | `:208-217, 225` |

> ★ **`thumbstickValue` 的轴向图注释是「契约写清楚」的正面例子**（`:209-217`）——对比 `XRoboToolkit` 的「无 schema 透传」，这是明显更好的工程实践。

### 2.4 有效性标志

```python
motion_data_ready: bool = False   # True after the first hand or controller motion data event is received  :197
```

> ⚠️ **这一个字段是本条最重要的发现，见 §4。**

---

## 3. 坐标系：显式命名约定 + 可选的腕部参考系

`get_tele_data()` 的 docstring（`tv_wrapper.py:286-300`）给出**完整的坐标系变换约定表**：

```
│left / right│   Bxr (basis) OpenXR  │  Brobot (basis) Robot  │  IPxr (initial pose) OpenXR  │  IPunitree (initial) Unitree  │
│ world / arm / head / waist │ arm / head / hand │   source frame  │  target frame  │
```

> *"All returned data are transformed from the **OpenXR Convention** to the **(Robot & Unitree) Convention**."*

**可选的腕部参考系**（`arm_reference_mode`，`tv_wrapper.py:232, 248-250`）：

| 取值 | 语义 |
| --- | --- |
| `"head_position"` | WORLD → HEAD，仅做平移调整 |
| **`"head_yaw"`（默认）** | WORLD → HEAD，用 `R_Brobot_world_head_yaw^T`，**忽略 pitch/roll** |

> ★ **这是一个真正的「坐标系契约参数化」**——`lerobot_ur_dual_vrteleop` 的 `R_headset_world` 与 `PiperPilot` 的 `FrameCalibration` 是同一问题的另外两种解法。**三者合起来说明：坐标帧是必须显式建模的一等公民。**

---

## 4. ⚠️⚠️ 最重要发现：**失联保护是假的**

### 4.1 `motion_data_ready` 是**闩锁**，不是新鲜度信号

`televuer.py` 中该字段的**全部**出现：

| 行 | 代码 | 说明 |
| --- | --- | --- |
| `:141` | `self.motion_data_ready_shared = Value('b', False, lock=True)` | 初始 `False` |
| `:265-266` | `with ...get_lock(): self.motion_data_ready_shared.value = True` | `on_controller_move` 置 `True` |
| `:313-314` | 同上 | `on_hand_move` 置 `True` |
| `:873-876` | `@property def motion_data_ready(self): ... return self.motion_data_ready_shared.value` | 只读属性 |

→ **`True` 之后再无任何地方置回 `False`。** 且 `televuer.py` 全文 `grep timeout|stale|last_.*time|monotonic|timestamp` → **仅 3 处，全部是线程 join/wait 的调试超时，与控制无关**（`:193, 211, 215`）。

**定义本身也写明了**：*"True after the **first** ... event is received"*。

### 4.2 因此 `xr_teleoperate` 的手部"保护"语义无效

`xr_teleoperate` 的手部路径写的是：

```python
# teleop_hand_and_arm.py:150
xr_motion_data_ready = ...   # 由 tele_data.motion_data_ready 更新
# robot_hand_unitree.py:191-196
if xr_motion_data_ready:     # ← 一旦收到过任何一帧，这里永远为 True
    <用当前 tele_data 重新重定向>
```

→ **一旦收到过任何一帧数据，该条件恒为真** → XR 断流后手部**持续从冻结位姿重新重定向**，而非保持上一目标。

> **修正上一轮子 Agent 的判断**：它把这条记为「部分有（fail-hold，保持）」。**实际是「条件恒真 → 无保护」**。这个差别只有读到 `televuer` 源码才能发现。

### 4.3 臂部路径连假保护都没有

`xr_teleoperate/teleop/teleop_hand_and_arm.py:367` **无条件**调用 `arm_ik.solve_ik(tele_data.left_wrist_pose, ...)`，不检查任何有效性标志。

### 4.4 附带：所有 XR 回调**静默吞异常**

```python
async def on_controller_move(self, event, session, fps=60):
    try:
        ...                                    # televuer.py:229-266
    except:
        pass                                   # :267-268

async def on_hand_move(self, event, session, fps=60):
    try:
        ...                                    # :270-312
    except:
        pass                                   # :315-316

async def on_cam_move(self, event, session, fps=60):
    try:
        ...
    except:
        pass                                   # :226-227
```

→ **字段缺失 / 格式变化 / 解析失败 → 静默冻结该通道，无任何信号**。与 `XRoboToolkit` 的「缺 `timeStampNs` 即整帧丢弃」相比，这是**更隐蔽**的失效模式。

> **结论**：`xr_teleoperate` 的**失联保护 = 0**（臂）**+ 语义无效**（手）。这**加强**了本轮的横向结论：**失联保护必须自研**。

---

## 5. 分层与可组合性

```
televuer（XR 输入，MIT，独立 pip 包）
   └─ 输出 TeleData（32 字段 dataclass，4×4 SE3 + 25×3 手部 + 控制器模拟量）
teleimager（图像流，Apache-2.0，独立 pip 包）
   └─ ImageClient / get_head_frame()（ZMQ / WebRTC）
xr_teleoperate（编排，Apache-2.0）
   ├─ robot_control/robot_arm_ik.py   （pinocchio + casadi + IPOPT，7 个机型类）
   ├─ robot_control/robot_arm.py      （unitree_sdk2py DDS，7 个机型类）
   └─ utils/episode_writer.py         （自定义 JSON+JPG，无时间戳）
dex-retargeting（手部重定向，MIT）
   └─ DexPilot 算法，输入 25 关键点 → 输出手指关节角，yml 配置驱动
```

**可组合性判定**：

| 组件 | 判定 | 依据 |
| --- | --- | --- |
| **`televuer`（输入层）** | **`wrapper-adapter`** ✅ | 独立 pip 包；机器人侧**模块级不依赖它**（`grep` 仅命中 `robot_hand_unitree.py:411` 的 `if __name__=="__main__"` 自测块）→ **依赖方向干净**；契约是**可读的 dataclass**（非私有二进制协议）；MIT 许可证清晰。**代价**：无 IDL/schema 文件、`render_to_xr` 带来显示耦合、失联保护缺失（须自己补） |
| **`teleimager`** | **`wrapper-adapter`** ✅ | Apache-2.0；接口窄（`ImageClient(host, request_bgr)` / `get_head_frame()`）；基于 ZMQ/WebRTC 标准协议 |
| **`dex-retargeting`** | **`direct-use`（条件）** ✅ | **MIT**（含 legacy MIT）；通用库；**换手型只需换 yml + URDF**（`assets/unitree_hand/unitree_dex3.yml`）→ 全生态**复用价值最高**的一块 |
| `robot_arm_ik.py` | `reference-only` | 强绑 Unitree URDF 与关节命名；每机型**复制粘贴一整个 200+ 行类**；对 Franka/Piper/UR **零可移植性**，只能作算法参考（pinocchio+casadi+IPOPT 建模） |
| `robot_arm.py` | `reference-only` | 100% 依赖 `unitree_sdk2py` DDS；可复用点仅「250 Hz 独立发布线程 + 关节限速 clip + 共享缓冲」这套**模式** |
| `episode_writer.py` | `reference-only` / `custom` | 自定义 JSON+JPG；**无时间戳字段**；深度不落地 |

> ★ **注意许可分层的反转**：`xr_teleoperate` 根仓库 Apache-2.0，但它**依赖 `casadi`（LGPL-3.0，待确认）**；而它的输入层 `televuer` 与重定向层 `dex-retargeting` 都是 **MIT**。
> → **若只想取输入层与重定向层，许可链反而比取整个 `xr_teleoperate` 更干净。**

---

## 6. 对本项目的直接输入

1. **`televuer` 是 ① 输入层的第三个 `wrapper-adapter` 候选**，且是三者中**契约最可读**的一个（可读 dataclass vs `IsaacTeleop` 的 FlatBuffers vs `XRoboToolkit` 的无 schema JSON）。
2. **它证明「XR 层输出 SE3 + 机器人差异下沉到 IK」这条分层可行** —— 与 `PiperPilot` 的 EEF 动作空间**互相印证**，共同支持「动作空间统一在末端位姿层」的结论。
3. **`arm_reference_mode` 是「坐标帧契约参数化」的第二个实证**（第三个是 `lerobot_ur_dual_vrteleop` 的 `R_headset_world`）→ **`FrameCalibration` 必须显式建模**。
4. **PICO/Quest 双端在 `televuer` 里是「零成本」的** —— 因为它走 **Vuer WebXR 浏览器**，设备差异只在**证书信任流程**（`xr_teleoperate/README.md:156, 159-173, 326`）。**好消息**：不会写死设备。**坏消息**：**没有原生 App → 无法定制输入采集策略**（原始时间戳、预测、丢帧补偿），而这正是数采闭环最需要的。
5. **必须自研的三项在此再次得到印证**：失联保护（此处为 0/无效）、XR 时间戳入数据集（此处无）、相机-机器人硬同步（此处靠同循环配对）。

---

## 7. 未验证项

| # | 未验证项 | 原因 |
| --- | --- | --- |
| 1 | `televuer` 的实际频率 / 端到端延迟 | 无 L4 实测 |
| 2 | `casadi` 是否为 LGPL-3.0 | 本地未安装，需外部确认 |
| 3 | `Vuer` 上游（`vuer-ai/vuer`）的追踪精度与丢帧行为 | 不在工作区；`televuer` 只做包装 |
| 4 | `teleimager` / `dex-retargeting` 的内部质量 | 本轮只读了结构与 LICENSE，未逐文件精读 |
| 5 | 三个 submodule 是否与 `xr_teleoperate` 的 pin commit 一致 | 我用 `--depth 1` 取的是各自默认分支 HEAD，**不是 submodule pin** |
| 6 | `televuer` 是否有测试 | 目录含 `example/test_televuer.py` / `test_tv_wrapper.py`，未读内容 |
| 7 | 真机表现（L3）/ 我方实测（L4） | 均无 |

> ⚠️ 第 5 条是**本轮引入的新不确定性**：子模块应按 `.gitmodules` + superproject 的 gitlink commit 取，我用 `--depth 1` 取默认分支 HEAD。**用于评估契约与许可证是充分的，用于复现构建则不足。**
