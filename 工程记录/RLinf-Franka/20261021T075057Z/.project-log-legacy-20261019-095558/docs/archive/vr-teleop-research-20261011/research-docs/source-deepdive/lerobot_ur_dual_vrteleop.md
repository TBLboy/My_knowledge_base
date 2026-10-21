# 源码深挖 · `scy-v/lerobot_ur_dual_vrteleop`

> **证据级**：**L2（源码可证）**——本地浅克隆逐文件读取。
> **规模**：43 文件 / 10.4 MB（去掉 assets 后代码量很小：`teleop.py` 479 行 + `ur.py` 467 行 + `run_record.py` 355 行）。
> **仓库**：`https://github.com/scy-v/lerobot_ur_dual_vrteleop`（23★，最近提交 2026-03-14）
> **定位**：**这是「分层组合」战略最强的一手证据**——它把 XR 输入层（XRoboToolkit）、核心层（Placo IK）、数据层（LeRobot）、从端（双 UR5e）**拼装**在一起，自己只写了两层胶水。

---

## 1. 一句话

**它证明了「组合」可行，而且给出了两条我们此前没有的关键设计：**

1. **契约 C 被做成了配置项**（`control_space: "joint" | "cartesian" | "force"`）——**不是二选一**；
2. **可组合性的分水岭是「URDF + YAML 配置驱动」还是「硬编码」**——本项目属于前者，`franka-vr-teleop` 属于后者。

---

## 2. 分层切面（源码实证）

```
头显 (PICO 4 Ultra)                      同一台 PC / 双 UR5e
  │                                        │
  │  XRoboToolkit PC Service               │
  ▼                                        │
① 输入层  XrClient  ───────────────────────┐
      from xrobotoolkit_teleop.common.xr_client import XrClient   (teleop.py:27)
                                           │
② 核心层  VRTeleop(Teleoperator)  ← Placo IK + clutch + 坐标变换 + 夹爪
      get_action() → {left_joint_1..6.pos, right_joint_1..6.pos, ee_delta, gripper}
                                           │
③ 适配层  UR(Robot)  → RTDE servoJ（gain/lookahead 可配）
      send_action() 按 control_space 分支
                                           │
数据层    LeRobot LeRobotDataset（3× RealSense @fps）
```

**关键：`②` 与 `③` 之间的接口是「关节角」**（见 §3）。

---

## 3. ★★ 契约 C：它**不选**，它**参数化**

```yaml
# scripts/config/cfg.yaml（robot 段）
control_space: "joint"  # Control space: "joint", "cartesian", or "force". ("force" is experimental)
```

```python
# run_record.py:78
self.control_space: str = robot.get("control_space", "joint")

# ur.py:257
if self.cfg.control_space == "joint":
    joint_positions = [action[f"{arm}_joint_{i+1}.pos"] for arm in ["left","right"] for i in range(6)]
```

**这是 `OQ-001` 的第三条路**：

| 方案 | 谁做 IK | 代表 | 换机器人代价 |
| --- | --- | --- | --- |
| A. 核心层输出**关节角** | 核心层 | **本项目**（Placo + URDF） | 换 URDF |
| B. 核心层输出**末端位姿** | 适配层 | `franka-vr-teleop` | 重写 ③（515 行 C++） |
| **C. 适配层声明能力，核心层按能力选择** | 可配 | **本项目实际做法** | 换 URDF + 改一个配置值 |

> **对我们的直接含义**：`OQ-001` 或许不该问"选 A 还是 B"，而该问"**是否把控制空间做成适配层的显式能力声明**"。本项目用 6 行配置给出了可行性证明。**这是今天最有价值的单条设计输入。**

---

## 4. ★ 可组合性的分水岭：URDF + YAML vs 硬编码

| 维度 | `lerobot_ur_dual_vrteleop` | `franka-vr-teleop` |
| --- | --- | --- |
| **坐标系变换** | **配置**：`R_headset_world: [-90, 0, 90]`（ZYX 欧拉角，度）→ `teleop.py:96` | **硬编码** 3×3 矩阵 + 手性翻转（`vr_to_robot_converter.py:278-282`） |
| **运动学模型** | **URDF 文件**：`assets/ur_urdf/dual_ur5e.urdf` → `placo.RobotWrapper(...)`（`teleop.py:154`） | C++ 内解析式 IK，7 轴写死（`geofik.cpp` 1868 行） |
| **机械臂映射** | **配置字典**：`manipulator_config`（base_link / link_name / pose_source / trigger）→ `teleop.py:40-55` | 无此概念 |
| **运动缩放** | **配置**：`scale_factor: 1`（`teleop.py:384`） | 无 |
| **关节数** | 由 URDF 决定（`state.q[7:13]` / `[13:19]`） | 硬编码 `std::array<double,7>` |
| **换一个机器人** | **换 URDF + 改配置** | **重写适配层** |

**结论**：**"可组合"不是架构图决定的，是"配置化程度"决定的。** 这是本轮最可操作的一条判据。

---

## 5. 契约 B 的实际形态（对比 `franka-vr-teleop` 的正则文本）

它**直接 import XRoboToolkit 的 Python 客户端**，而不是自己解析文本：

```python
# teleop.py:27,31,34
from xrobotoolkit_teleop.common.xr_client import XrClient
from xrobotoolkit_teleop.hardware.interface.universal_robots import CONTROLLER_DEADZONE
from xrobotoolkit_teleop.utils.geometry import apply_delta_pose, quat_diff_as_angle_axis
```

调用面（结构化 API，非正则）：

| 调用 | 用途 | 位置 |
| --- | --- | --- |
| `xr_client.get_pose_by_name("left_controller")` | 取控制器位姿 | `teleop.py:302` |
| `xr_client.get_key_value_by_name("left_grip")` | 取 grip 模拟量 → **clutch 判定** | `teleop.py:265-266` |
| `xr_client.get_key_value_by_name("left_trigger")` | 取扳机 → 夹爪 | `teleop.py:267` |
| `xr_client.get_button_state_by_name("A"/"B"/"X"/"Y"/"left_menu_button")` | **驱动数采状态机** | `run_record.py:117-128` |

> ⚠️ **但它不是浅依赖**：它同时 import 了 `hardware/interface/universal_robots` 的常量与 `utils/geometry` 的工具函数。**这意味着"输入层"与"UR 机型知识"在 XRoboToolkit 里是有耦合的**——替换输入层不是只换一个 client 类。
> **对我们的含义**：若采用 XRoboToolkit，要接受"输入层包 + 机型接口包 + 工具包"三者一起进来；契约 B 的干净边界需要我们自己重新划。

---

## 6. 数据记录层（我们最需要的部分）

`run_record.py` 是**完整的数据采集状态机**，且**完全建立在 LeRobot 之上**：

| 机制 | 实现 | 位置 |
| --- | --- | --- |
| 主循环 | LeRobot `record_loop(...)` | `:266-278` |
| 数据集创建 | `LeRobotDataset.create(repo_id, fps, features, robot_type, use_videos=True, image_writer_threads=4)` | `:234-241` |
| 特征生成 | `hw_to_dataset_features(robot.action_features, "action")` + observation（`use_video=True`） | `:220-222` |
| 处理器 | `make_default_processors()` → teleop/robot action + robot observation | `:250` |
| 相机 | **3× RealSense**（左腕 / 右腕 / 外部），RGB，**`use_depth=False`**，分辨率 424×240 | `:155-177` + `cfg.yaml` |
| 录制帧率 | **15 Hz**（`fps: 15 # dataset and camera frame rate`） | `cfg.yaml` |
| **VR 按键驱动状态机** | **A**=提前结束 / **X**=重录本 episode / **Y**=停止录制 / **左菜单**=中断 | `:114-129` |
| 重录 | `dataset.clear_episode_buffer()` + 回初始位姿 | `:280-286` |
| Episode 间隔流程 | B 键 → 重置录制 → 回初始关节 → B 键 → 下一 episode | `:293-319` |
| 回初始位姿 | `servoStop()` → `moveJ(init_joints)` | `:139-148` |
| 异常清理 | `send2trash`（进回收站，非永久删除） | `:102-112` |
| 续录校验 | `sanity_check_dataset_robot_compatibility(...)` | `:231` |
| 上传 | 可选 `dataset.push_to_hub()` | `:332-333` |

**完整生命周期**：`run_record.py`(355) → `run_replay.py`(69) → `run_visualize.py`(238, rerun) → `check_dataset_info.py`(82)。

> **可直接借鉴的三点**：
> 1. **用头显按键驱动数采状态机**（A/X/Y/菜单）——操作者不用摘头显就能控流程，这是实操关键。
> 2. **异常时进回收站而非删除** + 交互确认。
> 3. **episode 之间强制回初始位姿**，保证数据可比性。

---

## 7. 频率：第三个具体样本

| 环节 | 频率 | 依据 |
| --- | --- | --- |
| 数据集与相机 | **15 Hz** | `cfg.yaml` `fps: 15` |
| UR servo（RTDE `servoJ`） | **≈58.8 Hz** | `servo_time: 0.017`（`1/0.017`） |
| 遥操作更新线程 | 跟随 `fps`（`time.sleep(1/fps - elapsed)`） | `teleop.py:197` |
| XR 输入 | ≈65 Hz（USB）/ ≈20 Hz（WiFi） | 继承 XRoboToolkit 侧 |

**→ 三个频率再次分离**：录制 15 Hz、servo ≈59 Hz、XR ≈20–65 Hz。**而且这里录制帧率(15Hz) 低于 servo(59Hz) 约 4 倍**——数据集的"帧"是采样快照，不是控制周期。**这坐实了「录制帧率 ≠ 控制频率」的结论**（`lbx-Franka-Teach` 是 40Hz/6.6Hz，这里是 15Hz/59Hz，方向相反）。

---

## 8. "UR7e 之谜" —— **已解开**

任务背景里的设备名 **"UR7e" 在 UR 官方产品线中不存在**（只有 UR3e/5e/10e/16e/UR20/UR30），此前列为未确认风险 `R5`。

**源码证据**：

- `cfg.yaml` 中 `left_gripper_port: "/dev/ur7e_left_gripper"`、`right_gripper_port: "/dev/ur7e_right_gripper"` → **`ur7e` 是本机 udev 设备符号链接名，不是机器人型号**
- 运动学模型是 **`assets/ur_urdf/dual_ur5e.urdf`**（该目录下**只有这一个 URDF**，无 ur7e 模型）
- 夹爪设备串口来自 `pyDHgripper` 的 `PGE` 类（`ur.py:12`）

**结论（更新 `R5`）**：该项目实际使用的是 **双 UR5e**；"ur7e" 只是作者给设备起的本地别名。**原始任务说明里的"UR7e"极可能源自此处，应更正为 UR5e（或现场核对铭牌）。**

---

## 9. 许可证实况

| 文件 | 授权声明 |
| --- | --- |
| `lerobot_teleoperator_vr/.../teleop.py` | ✅ **Apache-2.0 头**（`Copyright 2024 The HuggingFace Inc. team`，`:3-15`）——派生自 LeRobot 模板 |
| `lerobot_robot_ur/.../ur.py`（467 行） | ❌ **无任何声明**（`:1` 直接 `import logging`） |
| `scripts/core/run_record.py`（355 行） | ❌ **无任何声明** |
| 仓库根 | ❌ **无 LICENSE 文件** |

→ 与 `license-audit.md` 的 B 类定性一致：**"无许可证文件"，其中 1 个文件（teleop.py）有 Apache-2.0 头**。
→ **判定 `reference-only`**：`run_record.py` 与 `ur.py` 是作者原创且无授权，只能"读懂思路后自己写"。

---

## 10. 安全机制（对比 §franka-vr-teleop）

| 机制 | 本项目 | `franka-vr-teleop` |
| --- | --- | --- |
| **Clutch** | **grip 键**（`active = grip > 1 - CONTROLLER_DEADZONE`，`:266`）；松开时把 IK 目标重置到当前实际位姿（`:330-331`）→ 无跳变 | 左拳握紧；松拳重锚（`:345`） |
| 死区 | `CONTROLLER_DEADZONE`（复用 XRoboToolkit 常量） | 位置 1mm / 姿态 1.7°（自有） |
| 工作空间限制 | ❌ **未见**（无 `max_position_offset` 等价物） | ✅ 75 cm 增量截断 |
| 关节限幅 | 依赖 UR `servoJ` 的 `gain` / `lookahead_time`（UR 控制器内部限速） | ✅ Ruckig 显式限 velocity/accel/jerk |
| IK 失败处理 | 捕获异常 → "Returning last known good joint positions."（`:347-350`） | ✅ 保持上一目标（`:438`） |
| **失联保护** | ❌ **无** | ❌ **无** |
| 调试模式 | ✅ `debug: True` → 机器人不执行动作但夹爪仍可控 | ❌ 无 |
| 启动回位 | ✅ `moveJ(init_joints)` | ✅ 固定起始关节角 |

**两个样本都缺失联保护** → **这必须是我们的增量，且是 P1 的必测项**（结论强化）。
**本项目的独有优点**：`debug` 干跑模式、VR 按键驱动状态机、松 clutch 时重置 IK 目标。

---

## 11. 可复用性判定

| 层 | 判定 | 理由 |
| --- | --- | --- |
| ① 输入层 | **`wrapper-adapter`**（若选 XRoboToolkit） | 已被本项目源码级复用；但注意它连带机型接口与工具包 |
| ② 核心层 | **`reference-only`（高价值）** | **`control_space` 参数化、URDF 驱动 IK、配置化坐标变换、clutch 语义**——四条都该抄；代码本身无授权 |
| ③ UR 适配层 | **`reference-only`** | `send_action` 的 `control_space` 分支结构值得抄；`ur.py` 无授权 |
| 数据记录层 | **`direct-use`（用 LeRobot 本体）+ `reference-only`（抄 `run_record.py` 思路）** | LeRobot 是 Apache-2.0；`run_record.py` 无授权但思路可直接实现 |

---

## 12. 对本项目的四条直接输入

1. **`OQ-001` 的第三选项**：把控制空间做成**适配层能力声明**，而非全局二选一。本项目用 `control_space` 配置证明了可行性。
2. **架构判据**：**"配置化 + URDF 驱动" 才叫可组合**；硬编码坐标系与机型参数的实现，无论多强都不可组合。
3. **数采层**：直接站在 **LeRobot**（Apache-2.0）上，**只自研状态机与安全**；并用**头显按键**驱动采集流程。
4. **必须自研的两项**：**失联保护**（两个样本都没有）与**时间戳/时间同步**（两个样本都没把 XR 时间戳写进数据集）。

---

## 13. 未验证项

- **无 L3/L4 证据**：全部来自源码，未真机运行；`gain=300`/`lookahead_time=0.1`/`fps=15` 均为配置值，未验证实际达成。
- **未读**：`run_replay.py`、`run_visualize.py`、`dataset_utils.py`、`check_dataset_info.py`（已确认存在与行数，未逐行读）。
- **未验证**：`pyDHgripper` 与 `/dev/ur7e_*` 符号链接的实际配置方式（需现场）。
- **未验证**：`assets/ur_urdf/dual_ur5e.urdf` 是否已按作者注释"tool0→tcp 变换需与示教器一致"做过修改。
- **浅克隆限制**：仅默认分支、depth=1。
- **`xrobotoolkit_teleop` 包本体未读**：本项目依赖的 `XrClient` / `CONTROLLER_DEADZONE` / `apply_delta_pose` 定义在 XRoboToolkit 侧，由另一条深挖线覆盖。
