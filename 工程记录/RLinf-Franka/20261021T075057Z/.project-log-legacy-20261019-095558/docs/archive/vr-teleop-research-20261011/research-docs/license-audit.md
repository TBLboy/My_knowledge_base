# 许可证审计（全树级 + API 交叉验证）

> **状态**：`DOC-007` 产出，2026-10-11。
> **用途**：修正 `第一阶段生态普查报告.md` v1.2 中关于许可证的结论，并为候选矩阵提供「许可证」列。
> **性质**：**证据审计，不是法律意见**。分类基于文件内容与 SPDX 标识，最终合规判断需法务确认。

---

## 1. 一句话结论

**报告 v1.2 把许可证风险说反了最要紧的一条**：

> **`XRoboToolkit-Unity-Client`（PICO 客户端）不是"没有许可证"，它是一份标准的 MIT 许可证**（`LICENSE.txt`，1265 B，© 2025 XR Robotics）。
> 因此报告与汇报材料中「PICO 客户端无许可证 → 整条 PICO 路线存在法务阻断风险 → 需联系作者或寻求替代」的判断**不成立，应予撤销**。

---

## 2. 方法（为什么这一版可信）

| 手段 | 说明 |
| --- | --- |
| **全树扫描**（不限根目录） | 对 15 个本地克隆递归查找 `LICENSE*/LICENCE*/COPYING*/NOTICE*`（排除 `.git` / `node_modules`） |
| **读文件内容** | 不依赖文件名或 GitHub 标签，直接读授权文本判定类型与署名 |
| **GitHub API 交叉验证** | 对**未克隆**仓库查 `/repos/{owner}/{repo}/license`，与本地扫描互为独立证据 |
| **双向确认** | 8 个"无授权"仓库：本地全树 0 文件 **且** API 返回 404 |

**v1.2 的方法缺陷（根因）**：

1. **文件名假设** —— 只探测了 `LICENSE`，未探测 `LICENSE.txt` / `LICENSE.md`。PICO 客户端的文件正是 `LICENSE.txt`，于是 `raw.githubusercontent` 返回 404，被误判为"未提供许可证"。
2. **把 `NOASSERTION` 当作"无许可证"** —— `NOASSERTION` 的准确含义是「**存在许可证文件，但不是 SPDX 标准许可证**」，它既可能是自定义宽松许可，也可能是专有或非商业许可。**必须读内容**。本项目里有 3 个仓库属于这种情况，其中 1 个其实是 MIT、1 个是专有、1 个是 CC BY-NC-SA。

---

## 3. 分类结果

### A 类｜宽松许可（Apache-2.0 / MIT）——**17 个**

| 仓库 | 许可证 | 证据 |
| --- | --- | --- |
| `NVIDIA/IsaacTeleop` | Apache-2.0 | API `LICENSE.md` 11348 B |
| `NVIDIA-ISAAC-ROS/isaac_ros_teleop` | Apache-2.0 | 本地 `LICENSE`，© 2026 NVIDIA |
| `huggingface/lerobot` | Apache-2.0 | API `LICENSE` 29977 B |
| `unitreerobotics/xr_teleoperate` | Apache-2.0 | 本地 `LICENSE`，© 2025 Unitree |
| `XR-Robotics/XRoboToolkit-PC-Service` | Apache-2.0 | API `LICENSE` 11358 B |
| `Taokt/Quest2ROS2` | Apache-2.0 | 本地 `LICENSE` |
| `wengmister/quest-wrist-tracker` | Apache-2.0 | 本地 `LICENSE` |
| `OpenTeleVision/TeleVision` | Apache-2.0 | 本地 `LICENSE`，© 2024 Xuxin Cheng 等 |
| `rail-berkeley/oculus_reader` | Apache-2.0 | API `LICENSE` 11357 B |
| **`XR-Robotics/XRoboToolkit-Unity-Client`（PICO 客户端）** | **MIT** | **`LICENSE.txt` 1265 B，© 2025 XR Robotics** ⚠️ **v1.2 误判** |
| `XR-Robotics/XRoboToolkit-Unity-Client-Quest` | MIT | API `LICENSE` 1068 B |
| `XR-Robotics/XRoboToolkit-Teleop-ROS` | MIT | 本地 `LICENSE`，© 2025 XR Robotics |
| `XR-Robotics/XRoboToolkit-Teleop-Sample-Python` | MIT | API `LICENSE` 1068 B |
| `XR-Robotics/XRoboToolkit-Teleop-Sample-Cpp` | MIT | API `LICENSE` 1068 B |
| `aadhithya14/Open-Teach` | MIT | API `LICENSE` 1071 B |
| `jmcoholich/openteach` | MIT | API `LICENSE` 1143 B |
| `tomakeIT/PiperPilot` | MIT | 本地 `LICENSE`，© 2026 PiperPilot contributors |

### B 类｜**无许可证文件** ——**8 个**（本地全树扫描 + API 双向确认）

> ⚠️ **措辞更正（由独立复核发现，见 §6.5）**：本类初版写作"全树无授权"，该措辞**不成立**——其中 **4 个仓库在 README 或源码头中有授权声明**，只是**没有 LICENSE 文件**。
> **「无许可证文件」是文件级事实；「无授权」是法律结论。两者不可混用。**

| 仓库 | 许可证文件 | README / 源码头声明（实测） | 授权状态 |
| --- | --- | --- | --- |
| `Labelbox/lbx-Franka-Teach` | ❌ 无 | ✅ `README.md:347-349`：*"This project is licensed under the MIT License - see the LICENSE file for details."* | ⚠️ **不清晰**（自述 MIT，但所指 LICENSE 文件缺失，属**悬空引用**） |
| `WeGo-Robotics/lerobot_robot_piper` | ❌ 无 | ✅ README 徽章 Apache-2.0 + `## License` 段（L339）；`motors/port_handler.py:4-6` Apache-2.0 头 | ⚠️ **不清晰**（自述 Apache-2.0，文件缺失） |
| `Shenzhaolong1330/lerobot_franka_teleop` | ❌ 无 | ✅ **2 个源文件**（`base_teleop.py:3`、`teleop.py:3`）含 `Copyright 2024 The HuggingFace Inc. team` + Apache-2.0 头（派生自 LeRobot）；另 **8 个 `assets/franka_urdf/meshes/visual/*.dae`** 含 **Franka Robotics GmbH** 的 Apache-2.0 声明（**作者不同，不可合并计数**） | ⚠️ **部分清晰**（派生与资产部分有声明；仓库自有代码不明） |
| `scy-v/lerobot_ur_dual_vrteleop` | ❌ 无 | ✅ 1 个文件含同上 Apache-2.0 头 | ⚠️ **部分清晰**（同上） |
| `zhourui9813/DexTeleGym` | ❌ 无（自有） | 仅含 vendored 的 `issac_gym_python/LICENSE.txt`（NVIDIA Isaac Gym，**明示未经许可禁止使用**） | ❌ **无授权** |
| `swaaniida/pico-piper-teleop` | ❌ 无 | ❌ 全树检索授权声明 **0 命中** | ❌ **无授权** |
| `Quest2ROS/quest2ros` | ❌ 无 | ❌ 0 命中；且 `package.xml:16` 为 `<license>TODO</license>` | ❌ **无授权** |
| `ZorAttC/franka_vr` | ❌ 无（API 404） | 未克隆，未做内容检索 | ❓ **未核实** |

**细分结论**：

- ❌ **明确无授权（3）**：`pico-piper-teleop`、`quest2ros`、`DexTeleGym`
- ⚠️ **自述有授权但缺文件 → 授权不清晰（4）**：`lbx-Franka-Teach`（自述 MIT）、`lerobot_robot_piper`（自述 Apache-2.0）、`lerobot_franka_teleop`、`lerobot_ur_dual_vrteleop`（派生部分 Apache-2.0）
- ❓ **未核实（1）**：`ZorAttC/franka_vr`

→ 全部仍应作 `reference-only`（**保守结论不变**），但**定性必须区分**：不能对自述 Apache-2.0 / MIT 的仓库简单断言"无授权"。

### C 类｜受限 / 非宽松许可 ——**2 个**（v1.2 均标为 `NOASSERTION`，未定性）

| 仓库 | 实际许可证 | 约束 |
| --- | --- | --- |
| `openarmx/openarmx_teleop_vr` | **CC BY-NC-SA 4.0**（© 2026 成都长树机器人） | **禁止商业使用（NonCommercial）** |
| `Pico-Developer/PICO-Unity-OpenXR-SDK` | **专有**（© 2015–2022 PICO Technology） | 明确声明"未经书面许可严格禁止传播"，受专利/商业秘密保护 |

→ **不能进入商业交付物**。注意后者是 **PICO 官方 SDK**，其条款与硬件采购绑定。

### D 类｜授权不清晰 ——**1 个**

| 仓库 | 情况 |
| --- | --- |
| `wengmister/franka-vr-teleop` | 根 `LICENSE`（465 B）**仅免责声明，无任何授权授予**；但 `src/franka_vr_teleop/LICENSE`（17 行）是 **MIT 授权文本且无版权人署名**（"the above copyright notice" 指向一个不存在的 notice） |

→ 不是"没有授权"，而是**没人能说清哪种用法被允许**。危险性更隐蔽。**交付前必须按目录逐项确认或联系作者**。

---

## 4. 对报告 v1.2 的四处实质纠正

| # | 位置 | v1.2 原文 | 更正 |
| --- | --- | --- | --- |
| **1** | L110 / L176 / L308 / L331 | PICO 客户端 `NOASSERTION（根目录未见 LICENSE 文件）`；"整条 PICO 路线存在法务阻断风险"；建议"联系作者/寻求替代" | **实为 MIT**（`LICENSE.txt`）。**法务阻断判断撤销** |
| **2** | L155 | `PICO-Unity-OpenXR-SDK` `NOASSERTION（未见 LICENSE）` | 实为**专有许可**（`LICENSE.md`），**明确禁止未经许可传播** |
| **3** | L143 | `openarmx_teleop_vr` `NOASSERTION` | 实为 **CC BY-NC-SA 4.0，禁止商业使用** |
| **4** | L127 | `franka-vr-teleop` `NOASSERTION（仅免责声明文本）` | 补充：根目录仅免责声明 **+ 子目录无署名 MIT 文本** → 归类为**授权不清晰** |
| **5** | 全文（§3 B 类、报告 §10 R3、勘误 13） | 8 个仓库称"**全树无授权**" | 措辞过宽，改为"**无许可证文件**"，并细分：**3 个明确无授权 / 4 个自述有授权但缺文件（授权不清晰）/ 1 个未核实**。由独立复核指出（`REV-DOC007`） |

---

## 5. 对项目路线的影响（重要）

**PICO 路线的法务定性发生了方向性变化**：

- ❌ 旧理解：我们选的 PICO 客户端**没有许可证** → 整条路线可能不可用
- ✅ 新理解：PICO 客户端**是 MIT**，可自由使用/修改/再分发；**唯一残留约束来自它依赖的 `PICO Integration` 包，而该包受 PICO 自身条款约束**

**关键推论**：残留约束**无法通过换方案规避**——任何使用 PICO 硬件的方案都必然接受 PICO 的 SDK 条款。所以这从「**架构选型障碍**」降级为「**采购/法务条款确认事项**」。

> **但风险没有消失，只是换了位置**：仍需确认 PICO 企业版 SDK 的商用与分发条款。这是采购环节问题，不是选型否决理由。

---

## 6. 方法学教训（可复用）

1. **`NOASSERTION` ≠ 无许可证。** 它是"有文件但非标准 SPDX"，可能是 MIT、专有、或非商业许可——**必须读内容**。本项目 3 个 `NOASSERTION` 分属 3 种截然不同的性质。
2. **探测许可证不能假设文件名。** `LICENSE` / `LICENSE.txt` / `LICENSE.md` / `COPYING` 都要试。一个 404 不足以支撑"未提供许可证"的结论。
3. **只查根目录会漏掉分层授权。** `franka-vr-teleop` 的 MIT 文本藏在子目录里。
4. **失败归因**：本次错误属于 `verification-harness`（验证工具探测方式错误），**不是**内容判断错误。
5. **「无许可证文件」≠「无授权」。** 授权声明可能出现在 **README 或源码文件头**（本项目的 `lerobot_*` 三个插件与 `lbx-Franka-Teach` 都是如此）。只扫文件名会得出**过宽**的结论——**这与 §2 里 v1.2 的错误属于同一类**：从「我的探测没找到」跳到「不存在」。
6. **审计必须做"反向检查"**：不仅要问"有没有许可证文件"，还要问"**有没有授权声明**"。两个方向都查，才配得上"授权审计"这个名字。

---

## 7. 证据与限制

- **证据等级**：本地克隆的全树扫描与文件内容 = **L2（源码可证）**；未克隆仓库的 API 查询与 `raw.githubusercontent` 取原文 = **L1（元数据 + 原文）**。
- **未覆盖**：`openarmx` / `PICO-Unity-OpenXR-SDK` / `franka_vr` / `IsaacTeleop` 等**未做本地克隆**，其结论依赖远程原文，未逐文件复核目录级授权。
- **不做法律判断**：本审计只陈述文件内容与分类，**不构成合规意见**；商用与分发可行性需法务确认。
- **未验证**：各仓库是否在子目录中**另有**授权文件（未克隆者未做全树扫描）。
- **已知措辞缺陷（已更正）**：本审计初版将 B 类称为"全树无授权"，经独立复核（`REV-DOC007`）指出该措辞对 4 个成员不成立，已在 §3 更正为"无许可证文件"并细分。
- **未做**：`franka_vr`、`openarmx`、`PICO-Unity-OpenXR-SDK`、`IsaacTeleop` 等的**目录级/子目录级**授权扫描（无本地克隆）。
- **复核能力缺口**：独立复核方无 `shell` 权限（框架问题 `FI-002`），无法计算文件字节数与摘要，只能做内容级核对 → 属 `verification_capability_missing`，非结论缺陷。
