# 源码深挖 · LeRobot 插件分层模式（`lerobot_franka_teleop` + `lerobot_robot_piper`）

> **证据级**：**L2（源码可证）**，来源为**独立只读子 Agent 报告**；LeRobot 本体 ABC 通过读取钉死 commit `da5d2f3e…` 的原始文件核实。
> **范围**：`Shenzhaolong1330/lerobot_franka_teleop`（40 py，48★）+ `WeGo-Robotics/lerobot_robot_piper`（17 py，15★）。
> **为什么值得单独一条线**：它们回答的是**机制问题**——「组合式路线」到底用什么**底座**把它拼起来。

---

## 1. 一句话

**LeRobot 的插件机制本身就是"分层组合"的现成底座**：它把「输入层 / 机器人层 / 数据层」拆成独立 pip 包，**通过发行版名前缀 + 装饰器自动注册，零改动 LeRobot 本体**。

---

## 2. ★★ 契约的真正形态：**"特征名字典"**，不是关节角/末端位姿二选一

### 2.1 LeRobot 侧契约（权威来源：`huggingface/lerobot@da5d2f3e`）

`src/lerobot/robots/robot.py`（`class Robot(abc.ABC)`）要求实现：
`observation_features` / `action_features` / `is_connected` / `connect(calibrate=True)` / `is_calibrated` / `calibrate()` / `configure()` / **`get_observation() -> dict`** / **`send_action(action: dict) -> dict`** / `disconnect()`

`src/lerobot/teleoperators/teleoperator.py`（`class Teleoperator(abc.ABC)`）要求实现：
`action_features` / `feedback_features` / **`get_action() -> dict`** / `send_feedback(feedback: dict)` / `connect` / `calibrate` / `configure` / `disconnect`

**关键**：`get_action()` / `send_action()` 的返回值被定义为**扁平 dict，键与 `*_features` 对应** —— **契约载体是"特征名字典"，不是固定向量**。

### 2.2 两个仓库怎么用这个契约

| 仓库 | 声明的特征 | 位置 |
| --- | --- | --- |
| `lerobot_robot_piper` | **纯关节角（归一化）**：`{motor}.pos` | `piper_follower.py:80-81`；`motors/piper_motors_bus.py:185-190` 映射到 `[-100,100]`/`[0,100]` |
| `lerobot_robot_franka` | **随 `control_mode` 变**：`isoteleop` → `joint_{i}.pos`（关节角）；`spacemouse`/`oculus` → `delta_ee_pose.{x..rz}` + `gripper_cmd_bin`（**末端位姿增量**） | `franka.py:176-199` |

> ✅ **这是 `OQ-001` 的第四条路，也是成本最低的一条**：
> **同一套 ABC 既能承载关节角也能承载末端位姿——层边界由插件的 `action_features` 声明决定，而不是框架固定死的。**
> 这意味着我们**不必在 A/B 之间二选一**：让每个机器人插件声明它要什么（关节角 or 末端位姿），核心层按声明产出。**这与 `lerobot_ur_dual_vrteleop` 的 `control_space` 配置项是同一个思路的两种实现。**

---

## 3. 插件注册机制：**不需要改 LeRobot 本体**

### 3.1 机制（`doctor.py` + `import_utils.py` 证据）

```python
# lerobot/utils/import_utils.py:220+
def register_third_party_plugins():
    # 用 importlib.metadata 找 lerobot_robot_ / lerobot_camera_ / ... 前缀的已安装发行版并 import
```

```python
# lerobot_robot_piper/config_piper.py:7
@RobotConfig.register_subclass("piper_follower")
```

```python
# lerobot_robot_piper/config_piper_leader.py:6
@TeleoperatorConfig.register_subclass("piper_leader")
```

**三条规则**：
1. 发行版名**必须以 `lerobot_robot_` / `lerobot_teleoperator_` 开头**
2. 安装后由 `register_third_party_plugins()` **自动 import**
3. import 的**副作用**触发 `@register_subclass` 装饰器完成注册

### 3.2 关键工程细节：**shim 包**（可直接照搬的模板）

`lerobot_robot_wego_piper/__init__.py:1-14` 原文：

> *"LeRobot's `register_third_party_plugins()` imports the module named after the installed DISTRIBUTION (`lerobot_robot_wego_piper`). The real code lives in the `lerobot_robot_piper` package; importing it here runs the `@register_subclass` decorators…"*

→ **当 PyPI 发行版名与 import 包名不一致时，必须放一个 re-export shim**，否则自动发现失败。

`doctor.py:186-190` 会明确诊断这个失败模式：

> *"the installed distribution name must start with `lerobot_robot_`"*

### 3.3 两个仓库的差异

| | `lerobot_franka_teleop` | `lerobot_robot_piper` |
| --- | --- | --- |
| 打包 | 只有 `setup.py`；`install_requires` 用 `file:///` 本地路径 | **`pyproject.toml`**，PyPI 名 `lerobot_robot_wego_piper` |
| entry_points | 只注册 console scripts，**无插件注册 entry point** | `[project.scripts]` 注册 UI 命令 |
| 注册触发 | 靠 `run_record.py:5-12` **手动 import** | 靠 **自动发现**（发行版名前缀） |
| 结论 | ⚠️ 更脆 | ✅ **更规范，值得照搬** |

---

## 4. 数据层耦合

### 4.1 `lerobot_franka_teleop`：直接调用 LeRobot **内部** API

```python
# scripts/core/run_record.py
L15  from lerobot.scripts.lerobot_record import record_loop
L16  from lerobot.processor import make_default_processors
L23  from lerobot.datasets.lerobot_dataset import LeRobotDataset
L24  from lerobot.datasets.utils import hw_to_dataset_features
L25  from lerobot.utils.control_utils import sanity_check_dataset_robot_compatibility
L28  from lerobot.processor.rename_processor import rename_stats
```

- `LeRobotDataset.create(repo_id, fps, features, robot_type, use_videos=True, image_writer_threads=4)`（L291-298）
- `record_loop(robot=..., teleop=..., fps=..., dataset=..., control_time_s=..., single_task=...)`（L344-359）
- **帧率**：`record_cfg.yaml:9` `fps: 15`；相机与数据集同频
- **时间戳/相机同步**：**不在本仓库实现**，完全交给 LeRobot（`image_writer_threads=4` 异步写图）

**★ XR 输入被直接写进数据集 action**：

```python
# L277-279
action_features = hw_to_dataset_features(robot.action_features, "action")
obs_features    = hw_to_dataset_features(robot.observation_features, "observation", use_video=True)
dataset_features = {**action_features, **obs_features}
```

→ `oculus` 模式下 `robot.action_features` = `delta_ee_pose.{x..rz}` + `gripper_cmd_bin` → **Quest 的末端位姿增量直接成为数据集 action**。

> ⚠️ **`traceability-gap`（记录与执行不一致）**：`oculus` 的 `joint_{i}.pos` 在 `action_features` 中被**注释掉**（`franka.py:192-194`），但 `_send_action_oculus_joint`（L414）在 `execute_mode="joint"` 时**会读取**它 → **"记录进数据集的 action 特征"与"执行时消费的 action 键"不一致**。

### 4.2 `lerobot_robot_piper`：**完全委托官方 CLI**（更健康）

```
# teleop_ui.py:162-167
"Record": "lerobot-record --robot.type=piper_follower --robot.port={follower_port} \
           --teleop.type=piper_leader --teleop.port={leader_port} --fps=30 --repo-id=piper_dataset"
```

→ **用官方 CLI 而非内部 API**，是可持续做法（见 §6 改进建议）。

---

## 5. XR 输入层：`lerobot_franka_teleop` 是**反面教材**

### 5.1 它怎么读 Quest

```python
# oculus/oculus_robot.py
L6   from .oculus_reader import OculusReader
L62  self._oculus_reader = OculusReader(ip_address=ip)
L271 transforms, buttons = self._oculus_reader.get_transformations_and_buttons()
L273-274 rg_pressed = buttons.get('RG', False) ; a_pressed = buttons.get('A', False)
L288 if 'r' in transforms: current_transform = transforms['r']   # 右控制器 4×4
```

- `oculus_reader` **未 vendored**（`glob **/oculus_reader*` → 无文件）→ README:173-178 要求**手动 clone** 到 `.../oculus/`
- **`setup.py` 未声明该依赖** → 直接 `pip install -e .` 后 `from .oculus_reader import ...` **会 ImportError**

### 5.2 ⚠️ 两处跨层耦合（**必须避免**）

```python
# oculus_robot.py:94  ← 在"遥操作包"内部
from lerobot_robot_franka.franka_interface_client import FrankaInterfaceClient
```

1. **输入层反向依赖机器人层**（teleop 包 import robot 包）
2. **IK 被内嵌在"输入层"里**：`L90-149 _init_placo_ik` 在同一个类里做 **Placo IK 求解 + 读 Franka 真实关节**（L112、L229、L313-324）

→ **IK 应属于控制/映射层，不属于输入层。** 这是我们划分层次时必须避开的结构。

---

## 6. 版本锁定：**钉死只写在 README 里**

- README.MD L80-85：`git checkout da5d2f3e9187fa4690e6667fe8b294cae49016d6`（LeRobot 0.3.4）
- **代码/配置核实**：该仓库**无** `requirements*.txt` / `pyproject.toml` / `environment*.yml`；根 `setup.py` **也未列 `lerobot`** → **任何打包文件都不强制这个版本**
- **为什么必须钉死**：它深度使用 LeRobot **内部**模块（`lerobot.scripts.*`、`lerobot.processor.*`、`lerobot.datasets.sampler.*`、`lerobot.rl.wandb_utils.*`），跨版本极脆
- **私有 fork 确认**：README.MD L42-46 —— 作者自有 fork `github.com/Shenzhaolong1330/fairo-franka`；`franka_interface_server.py:7-8` `from polymetis import RobotInterface`，`:19` `RobotInterface(enforce_version=False)`；客户端 `franka_interface_client.py:14-15` `zerorpc.Client(heartbeat=20)` → **架构 = NUC 上跑 Polymetis fork + 本机 zerorpc 连 `tcp://0.0.0.0:4242`**

---

## 7. 可复用性判定

| 仓库 | 判定 | 依据 |
| --- | --- | --- |
| `lerobot_franka_teleop` | **`reference-only`** | 硬依赖私有 Polymetis fork + NUC zerorpc；`oculus_reader` 未 vendored；深度耦合 LeRobot 内部 API 且版本无强制；**无自动化测试、无 CI** |
| `lerobot_robot_piper` | **`reference-only`（但注册/打包方式 ≈ `wrapper-adapter` 模板）** | 自包含、PyPI 可装、不改 LeRobot 本体；但硬件是 Piper/`piper_sdk`/CAN |

### ★ 「插件分层方式」本身值得照搬吗？—— **采用其"模式"，不照抄代码**

**可借鉴（3 条）**：
1. **双插件分层**：`Robot` 插件与 `Teleoperator` 插件各自独立 pip 包，`@RobotConfig/@TeleoperatorConfig.register_subclass` 注册，**LeRobot 本体零改动**
2. **发行版名前缀 + shim 做自动发现**（piper 的 `lerobot_robot_wego_piper` shim）—— 这是"插件能被 CLI 自动发现"的关键工程细节
3. **契约是特征字典**：允许关节角或末端位姿 → **正好适配我们"PICO + Quest 双输入 + Franka/Piper/UR 多机械臂"的组合需求**

**必须避免（3 条）**：
1. 不要让输入层反向依赖机器人层或内嵌 IK
2. 不要依赖 LeRobot 内部 API（`lerobot.scripts.*`）→ 用官方 CLI，否则必须钉死 commit
3. 统一输入层应产出**规范化特征字典**，IK/映射放到独立的控制层

---

## 8. 未验证项

1. **无 shell/git**：无法核实本地两个仓库的实际 commit / 分支 / 未提交改动；无法确认本地 lerobot 是否真为 `da5d2f3e`
2. **`oculus_reader` 源码未读**：返回结构仅由调用点推断
3. **LeRobot `record_loop` / `LeRobotDataset` 内部未读**：fps / 时间戳 / 相机同步的**具体实现**未从源码核实
4. **硬件行为未验证**：Polymetis fork、Franka 真机、Piper CAN、Quest 真机均无实测
5. **注册的最终效果未实机验证**
6. **无自动化测试、无 CI**（两仓库均如此）

---

## 9. 最重要的 3 个发现

1. **LeRobot 的"核心层↔机器人层契约"是"特征名字典"，不是关节角/末端位姿二选一。**
   `Robot.send_action(action: dict)` / `Teleoperator.get_action() -> dict` 的语义由插件用 `action_features` 自行声明。**我们的"统一输入层"只需产出一份规范化特征字典即可被核心层消费——分层组合在契约层面天然成立。**

2. **插件接入不需要改 LeRobot 本体：靠"发行版名前缀 + import 副作用 + `register_subclass`"，而 piper 的 shim 是把它做对的关键工程细节。**
   这是**可直接照搬到我们项目的最小注册模板**。

3. **`lerobot_franka_teleop` 是"反面教材"式的分层先例。**
   它验证了分层可行，但也暴露了两个必须避免的耦合：① 输入层反向依赖机器人层并在其中内嵌 IK；② 深度耦合 LeRobot 内部 API 且版本钉死只写在 README。**两个仓库整体判 `reference-only`：分层"模式"值得借鉴，代码不可直接复用。**

---

## 10. 对本项目的直接输入

1. **`OQ-001` 的第四条路（最低成本）**：**让每个机器人插件声明它的 action 特征（关节角 or 末端位姿），核心层按声明产出**。LeRobot 的 ABC 已经天然支持这种"声明式契约"。
2. **数据层可以直接站在 LeRobot（Apache-2.0）上**，且**用官方 CLI 而非内部 API**（`lerobot-record`），这样不必钉死 commit。
3. **插件机制是我们"组合"的现成底座**：输入层与机器人层各自做成独立包，通过前缀注册自动发现——**我们不需要发明一套插件系统**。
