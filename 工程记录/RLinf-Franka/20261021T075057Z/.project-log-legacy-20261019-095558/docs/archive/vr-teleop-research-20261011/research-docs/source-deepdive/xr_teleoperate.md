# 源码深挖 · `unitreerobotics/xr_teleoperate`（**1697★，本轮最大候选**）

> **证据级**：**L2（源码可证）**。来源 = 独立只读子 Agent 报告 **+ 主 Agent 补克隆 3 个 submodule 并亲自精读输入层**（见 [`televuer-xr-input.md`](televuer-xr-input.md)）。
> **规模**：435 文件 / 266 MB；浅克隆 HEAD `817fb00`（Apache-2.0，© 2025 Unitree Robotics）。
> **⚠️ 本轮最关键的取证动作**：该仓库的 XR 输入层是 **submodule**，克隆后**目录为空** → 子 Agent 的输入层结论原本只能停留在「调用方视角」。**主 Agent 用 shell 克隆补齐后，输入层才第一次可见。**

---

## 1. 一句话

**它是「Unitree 整机 + XR 遥操作 + 数采」的垂直一体化实现，不是一个分层可插拔框架**——但它的**输入层切法**（XR 只输出 SE3、机器人差异全部下沉到 IK）**正是我们该照搬的架构选择**。

---

## 2. 分层（按目录约定，非按接口契约）

| 层 | 位置 | 证据 |
| --- | --- | --- |
| **XR 输入层** | `teleop/televuer`（**独立 pip 包，MIT**） | `.gitmodules:1-3`；`teleop_hand_and_arm.py:16` `from televuer import TeleVuerWrapper` |
| 图像流层 | `teleop/teleimager`（独立 pip 包，Apache-2.0） | `.gitmodules:7-9`；`:19` `from teleimager.image_client import ImageClient` |
| 手部重定向层 | `teleop/robot_control/hand_retargeting.py` + `dex-retargeting`（**MIT**） | `hand_retargeting.py:1` `from dex_retargeting import RetargetingConfig` |
| IK 层 | `robot_arm_ik.py`（1120+ 行，**7 个 `*_ArmIK` 类**） | `:18, 312, 592, 895, …` |
| 机器人适配层 | `robot_arm.py`（2429 行，7 个 `*_ArmController`） | `:79, 669, 936, 1210, 1418, 1693, 2042` |
| 数据记录层 | `utils/episode_writer.py` | `:13` |
| 应用控制层 | `utils/ipc.py`（ZMQ REQ/REP + PUB/SUB 心跳） | `:56, 194` |

> ⚠️ **没有编排框架**：全部接线是单一入口脚本 `teleop_hand_and_arm.py`（579 行）中的命令式 `if/elif` 链（`:162-186` 选臂、`:189-246` 选末端）。**没有抽象基类、没有注册表、没有插件发现机制。**
> **分层是「按目录约定」而非「按接口契约」** —— 这与 LeRobot 的插件机制（`register_subclass` + 发行版名前缀）形成鲜明对比。

---

## 3. ★ 输入层：可分离，但抽出的是「属性名约定」

**接口形态**（`teleop_hand_and_arm.py`，L2）：

```python
:16   from televuer import TeleVuerWrapper
:128  tv_wrapper = TeleVuerWrapper(use_hand_tracking=…, binocular=…, img_shape=…,
                                   display_mode=…, zmq=…, webrtc=…,
                                   arm_reference_mode="head_yaw")
:317  tele_data = tv_wrapper.get_tele_data()
:278  tv_wrapper.render_to_xr(head_img.bgr)     # ← 显示耦合
```

**可分离性**：
- ✅ **正面**：`robot_control/*` 在**模块级不导入** `televuer`（`grep` 仅命中 `robot_hand_unitree.py:411` 的 `if __name__=="__main__"` 自测块）→ **依赖方向干净**，机器人侧是叶子。
- ⚠️ **负面**：`render_to_xr()` 使输入层与图像层耦合（虽只传 numpy BGR 数组）。

**接口形态判定**：
1. **不是** 消息类型（无 ROS topic / DDS IDL / protobuf）；
2. **不是** 配置文件；
3. **是** 同进程 Python 对象 + **属性名约定**（`TeleData` dataclass，32 字段）。

→ **替换/复用的实际工作量集中在「对齐那 25 个属性名」**。契约内容详见 [`televuer-xr-input.md`](televuer-xr-input.md) §2。

---

## 4. ★ 契约：XR → 核心 = **末端位姿**；IK → 机器人 = 关节角

```python
# teleop_hand_and_arm.py:367
sol_q, sol_tauff = arm_ik.solve_ik(tele_data.left_wrist_pose, tele_data.right_wrist_pose,
                                   current_lr_arm_q, current_lr_arm_dq)
# robot_arm_ik.py:145-146   self.param_tf_l = self.opti.parameter(4, 4)
# robot_arm_ik.py:263-264   self.opti.set_value(self.param_tf_l, left_wrist)   ← 4×4 矩阵
# teleop_hand_and_arm.py:370  arm_ctrl.ctrl_dual_arm(sol_q, sol_tauff)
```

- **XR 层对机器人形态零知识** → 跨机型兼容性完全由 IK 侧承担。
- **无 `control_space` 开关**（`grep` → 0 命中）→ **控制空间硬编码为单一通道**。
- **记录的动作 = 关节角**（`teleop_hand_and_arm.py:431` → `episode_writer` 的 `actions[...].qpos`）。

> ★ **对我们的含义**：**这是与 `PiperPilot`（EEF 动作空间）互相印证的第二份证据。** 两者共同支持「动作空间统一在末端位姿层」。

---

## 5. ★ PICO / Quest 双端：**代码中零设备分支**

| 层面 | 事实 | 证据 |
| --- | --- | --- |
| 文档声明 | 支持 AVP / PICO 4 Ultra Enterprise / Quest 3 / Quest 3s | `README.md:51`；`Device.md:24-27`；`CHANGELOG.md:76`（L0） |
| 代码 | 按**词边界**检索设备名于 `*.py` → **无有效命中**（无 `if device == "pico"` 之类设备分支；`grep -i quest` 会命中 `request` / `request_bgr` 等子串——`teleop/utils/ipc.py:9`、`teleop/teleop_hand_and_arm.py:122`——**不是设备分支**） | L2 |
| 差异所在 | **证书/浏览器**层面：`README.md:156`（PICO/Quest 自签 `openssl`）、`:159-173`（AVP 需 rootCA + AirDrop）、`:326`（PICO 的 websocket 回退） | L0 |
| 客户端 App | **仓库内无**（`glob` 无 apk/ios/unity）；客户端是 **Vuer Web 应用**（头显浏览器打开 `:8012`） | L2 |

> **好消息**：不会写死任何设备（硬约束满足）。
> **坏消息**：**没有原生 App → 无法定制输入采集策略**（原始时间戳、预测、丢帧补偿）——**而这恰是数采闭环最需要的能力**。且「支持质量」由 **Vuer 上游**决定，不在我们可控范围。

---

## 6. 机器人后端：**全部是 Unitree 整机**

- `--arm` 可选：`G1_29 G1_23 H1_2 H1 H2 R1_A5 R1_A7`（`teleop_hand_and_arm.py:79`）
- `--ee` 可选：`dex1 dex1_internal dex3 inspire_ftp inspire_dfx brainco`（`:80`）
- SDK：`unitree_sdk2py`（DDS / CycloneDDS）；话题 `rt/lowcmd` / `rt/arm_sdk` / `rt/lowstate`（`robot_arm.py:6-12, 19-21`）
- **无 Franka / Piper / UR**：`grep -i "franka\|piper\|ur5\|ur10"` → **0 命中**；`assets/` 仅含 Unitree + inspire/brainco 手

**可插拔性：无接口层。** 新增机型需同时改 5 处：① `robot_arm_ik.py` 新 IK 类 ② `robot_arm.py` 新 Controller 类 ③ `teleop_hand_and_arm.py:162-186` 分支 ④ `assets/` URDF ⑤ `*_JointIndex` 枚举 → **「按约定可扩展」而非「按接口可插拔」**。

---

## 7. IK / 重定向

- **IK 在机器人侧**（`robot_arm_ik.py`），**不在输入层**
- 库：**pinocchio + casadi + IPOPT**（`:1-7, 178`）—— **未使用 Placo / Pink / MoveIt**
- 每机型一个类，**代价权重不一致**：`G1_29` rotation_cost = 1（`:158`）、`G1_23` = 0.5（`:436`）、`H1_2` = 1（`:740`）、`H1` = 0.5（`:1047`）→ **不同机型的跟踪特性不同**
- 平滑：`WeightedMovingFilter([0.4,0.3,0.2,0.1])`（`:181, 272-273`）
- ⚠️ **臂长缩放不一致（潜在缺陷）**：`scale_arms()` 定义于 `:245-251`，但 `G1_29`（`:258`）与 `G1_23`（`:537`）的调用**被注释掉**，而 `H1_2`（`:841`）**仍生效** → **同一套人体动作在不同机型上尺度语义不同**（推断，需真机确认）
- 手部：**dex-retargeting（DexPilot）**，`hand_retargeting.py:40-43`；yml 配置（`assets/unitree_hand/unitree_dex3.yml:2` `type: DexPilot`）

---

## 8. 数据记录：自定义格式，**无时间戳、无深度**

- 格式：`episode_XXXX/data.json`（流式追加，`episode_writer.py:115-119`）+ `colors/*.jpg` + `depths/` + `audios/`
- **非 LeRobot / 非 MCAP**；转换到 LeRobot 在**外部仓库** `unitree_IL_lerobot`（`README.md:358`，L0）
- 频率：单一 `--frequency` 默认 **30.0**，**同时用于控制循环与记录**（`:76`）
- 数据结构：`states/actions` 各含 `left_arm/right_arm/left_ee/right_ee/body` 的 `qpos`；**`qvel` 与 `torque` 恒为空列表**（`:469-470`）
- ⚠️ **深度恒为空**：`:433-434` `depths = {}` 且全程未赋值 → 虽 `episode_writer` 支持 depth，**实际不记录**
- **同步方式**：无硬件时间戳，**软同步/同循环配对**（把当轮读取的图像 + 当轮关节角打包成一个 item）
- ⚠️ **item 只有 `idx`，无任何时间戳字段**（`episode_writer.py:133-142`）→ **XR 时间戳未写入数据集**（`grep timestamp` 于 `*.py` 仅命中仿真共享内存与 IPC 心跳）
- 异步写盘：`Queue(-1)` + 工作线程（`:55-59, 146-161`）

---

## 9. 安全机制（逐项，**本轮修正**）

| 机制 | 有/无 | 证据 |
| --- | --- | --- |
| 关节位置限制 | ✅ | IK 内 `opti.subject_to(opti.bounded(lowerPositionLimit, var_q, upperPositionLimit))`，`robot_arm_ik.py:153-157` |
| 速度限幅 | ✅ | `clip_arm_q_target()`，`robot_arm.py:167-172`；默认 `velocity_limit=30.0` rad/s，`control_dt=1/250`（`:95, 250-255`）；**仿真模式跳过限幅**（`:185-188`） |
| 夹爪增量限幅 | ✅ | `DELTA_GRIPPER_CMD = 0.18` rad，`robot_hand_unitree.py:326, 380-382` |
| 退出归位 | ✅ | `finally` → `ctrl_dual_arm_go_home()`（`:535`），最多 5 s |
| DDS 就绪门禁 | ✅ | `wait_for_dds(…, timeout=5.0)`，超时抛 `TimeoutError`（`dds_utils.py:8-17`） |
| 急停 | ⚠️ 仅 motion 模式 | 双摇杆按下 → `loco_wrapper.Damp()`（`:354-355`）；**手部追踪模式无头显内急停** |
| 笛卡尔工作空间盒 | ❌ | `grep workspace` → 0 命中 |
| **离合（clutch）/ 重定位** | ❌ | `grep clutch\|recenter\|dead_zone` → **0 命中** |
| **失联保护（臂）** | ❌ | `:367` **无条件**执行 IK，不检查有效性标志 |
| **失联保护（手）** | ❌ **（本轮修正）** | 见下 |
| 碰撞 / 力限制 | ❌ | 无碰撞约束；`tau` 仅来自 `pin.rnea` 前馈（`robot_arm_ik.py:282`） |

### ★★ 本轮修正：手部「fail-hold」是**假的**

上一轮子 Agent 记为「部分有（fail-hold，保持）」。**读到 `televuer` 源码后修正为：条件恒真 → 无保护。**

```python
# televuer/src/televuer/tv_wrapper.py:197
motion_data_ready: bool = False   # True after the FIRST hand or controller motion data event is received
# televuer/src/televuer/televuer.py:265-266 / :313-314   ← 置 True
# 全文再无任何地方置回 False；且 grep timeout|stale|last_.*time|monotonic|timestamp → 仅 3 处线程调试超时
# xr_teleoperate/teleop/robot_control/robot_hand_unitree.py:191-196
if xr_motion_data_ready:   # ← 一旦收到过任何一帧，永远为 True
    <用当前 tele_data 重新重定向>
```

→ **`motion_data_ready` 是闩锁，不是新鲜度信号** → XR 断流后手部**持续从冻结位姿重新重定向**。
→ **叠加**：所有 XR 回调体被 `except: pass` 包裹（`televuer.py:226-227, 267-268, 315-316`）→ **字段缺失/解析失败静默冻结该通道，无任何信号**。

> **结论**：`xr_teleoperate` 的**失联保护 = 0（臂）+ 语义无效（手）**。这**加强**了本轮的横向结论：**失联保护必须自研**，且它是**最容易做出「看起来有、实际没有」**的一项。

---

## 10. 许可证与依赖

- 根 `LICENSE:3` = **Apache-2.0**（© 2025 Unitree Robotics）
- ⚠️ **受限许可风险**：**`casadi` = LGPL-3.0**（L1 外部知识，待确认）——弱 copyleft，闭源分发需评估
- **依赖声明严重不足**：`requirements.txt` **仅 4 行**（`matplotlib==3.7.5 / rerun-sdk==0.20.1 / meshcat==0.3.2 / sshkeyboard==2.3.1`）；**`logging_mp` 全仓库被导入（10 个文件）但未声明**，本地也无该文件 → 需人工补装（`github.com/unitreerobotics/logging-mp`）
- 末端执行器依赖 3 个**外部独立仓库**：`DFX_inspire_service` / `brainco_hand_service` / `dex1_1_service`（`README.md:431, 457, 461`）——**许可证本地不可验证**
- **无预编译二进制**；`assets/` 全为 URDF/STL/MJCF
- ★ **许可分层的反转**：根仓库 Apache-2.0 但依赖 LGPL 的 `casadi`；而**输入层 `televuer`（MIT）与重定向层 `dex-retargeting`（MIT）反而更干净** → **只取这两层，许可链比取整仓更清爽**

---

## 11. 成熟度

| 维度 | 事实 |
| --- | --- |
| 测试 | **根仓库 0 个**（`glob **/*test*` → 无）；`televuer` 子模块有 `example/test_*.py`（本轮已克隆，未读内容） |
| CI | **无**（`glob .github/**` → 无） |
| 文档 | **高**：4 语言 README + `Device.md` + 双 CHANGELOG + Wiki + DeepWiki 徽章；参数表详尽（`:218-246`）、状态机图示（`:247-253`） |
| 文档漂移 | `Device.md:58` 指向已废弃的 `teleop/image_server`；`Device.md:190-193` 链接的 `hardware/*.STEP` **在仓库中不存在** |
| 仿真后端 | `--sim`（`:87`）→ 但**依赖外部 `unitree_sim_isaaclab`**（`README.md:260`）→ **不是自包含 fake 后端** |
| 无硬件可控性 | ✅ `--ipc` + `--headless`（`:86-88`）支持外部代理驱动启停/录制 |

---

## 12. 可复用性判定（**分层**）

| 层 | 判定 | 理由 |
| --- | --- | --- |
| **XR 输入层（`televuer`）** | **`wrapper-adapter`** ✅ | 独立 pip 包 + **MIT** + 依赖方向干净 + 契约可读（dataclass）。代价：无 IDL/schema、显示耦合、失联保护缺失 |
| **图像流层（`teleimager`）** | **`wrapper-adapter`** ✅ | Apache-2.0；接口窄；基于 ZMQ/WebRTC 标准协议 |
| **手部重定向层（`dex-retargeting`）** | **`direct-use`（条件）** ✅ | **MIT**（含 legacy MIT）；换手型只需换 yml + URDF → **全生态复用价值最高** |
| IK 层 | `reference-only` | 强绑 Unitree URDF；每机型复制 200+ 行类；对 Franka/Piper/UR **零可移植性**，只能作算法参考 |
| 机器人适配层 | `reference-only` | 100% 依赖 `unitree_sdk2py` DDS；仅「250 Hz 独立发布线程 + 关节限速 + 共享缓冲」模式可参考 |
| 数据记录层 | `reference-only` / `custom` | 自研 JSON+JPG；**无时间戳**；深度不落地 |
| 安全机制 | `reference-only` | 缺 clutch / watchdog / 工作空间盒 / 统一急停；**不可作为安全基线** |

---

## 13. 未验证项

| # | 未验证项 | 原因 |
| --- | --- | --- |
| 1 | `casadi` 是否 LGPL-3.0 | 本地未安装 |
| 2 | `scale_arms` 不一致是否导致数据不一致 | 需真机 |
| 3 | 图像-关节同步延迟量级 | 未实测 |
| 4 | `unitree_IL_lerobot` 的转换格式 | 外部仓库，未读 |
| 5 | 三个 submodule 是否与 superproject pin 一致 | 我用 `--depth 1` 取默认分支 HEAD |
| 6 | `--motion` 模式下臂/底盘双通道无仲裁的复合风险 | 推断，未验证 |
| 7 | L3 真机 / L4 我方实测 | 均无 |
| 8 | git 历史与提交频率 | 浅克隆 |

---

## 14. 最重要的 3 个发现

1. **输入层的真实接口是「末端位姿」，不是关节角 —— 这是该架构最有价值的可复用决策。**
   `teleop_hand_and_arm.py:367` 把 4×4 SE3 交给 `robot_arm_ik.py:263-264`，IK 产出关节角后才下发。**XR 层对机器人形态零知识。** 对我们「双端 + 多臂」的目标，**这是应当照搬的分层切法**。

2. **XR 输入层可独立抽出，但抽出的是「属性名约定」而非「协议」；且 `televuer` 是 MIT。**
   机器人侧模块级不依赖它 → 可分离性成立。接口是**同进程 Python dataclass**（32 字段），无 IDL/topic/schema。**它是 ① 输入层三个候选中契约最可读的一个。**

3. **★ 手部「失联保护」是假的（本轮修正）。**
   `motion_data_ready` 是**闩锁**（置 `True` 后永不复位）→ `if xr_motion_data_ready:` 恒真；臂部则连检查都没有。叠加回调 `except: pass` 静默吞异常 → **实际保护 = 0**。**这是「看起来有、实际没有」的典型安全陷阱**，正是我们必须自研的那一项。

---

## 15. 给主 Agent 的下一步建议

1. **把 `televuer` 补进 ① 层候选矩阵**（契约 = 32 字段 dataclass；复用强度 = `wrapper-adapter`；许可证 = **MIT**；限定：无 schema 文件、无失联保护）。
2. **`dex-retargeting`（MIT）单独立项验证** —— 它是全生态唯一可能 `direct-use` 的手部重定向组件，且许可干净。
3. **明确记录**：该仓库对 **Franka / Piper / UR 零直接可复用代码**；**不要**把它当作 Franka 方案的候选实现，只作**架构参考**。
4. **把「失联保护看起来有实际没有」写成我方架构的硬性检查项** —— 验收时必须能证明「断流 N ms 后行为符合预期」，而不是「代码里有 `if xxx_ready`」。
