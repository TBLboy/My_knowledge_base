# Progress

> 面向人的阶段进度摘要。维护规则：
> - **最新在最上**：按日期倒序排列，最新阶段段落位于文件顶部，旧段落依次向下。
> - **头部快照**：顶部“当前状态”区块是稳定入口，每次更新时覆盖，不追加旧版本。
> - **超限归档**：文件超过约 50-100 KB 时，把旧段落移动到 `.project-log/docs/archive/`，主文档只保留最近内容。
> - **单一事实源**：本文件是快速摘要；精确当前状态与下一步以 Project Log format 2 状态库、Git 账本与生成的 `handoff.md` 为准。
> - **机器文件不手工重排**：状态库、Git 账本与生成视图由运行时维护，不做手工重排或改写。

## 当前状态

- 当前阶段：solution-research（**第二阶段：重点候选源码深挖**，**已全覆盖**）
- 当前任务：`R-002`（active；第二轮已完成）
- 当前状态：**22 克隆 / 19 达 L2 深挖 / 13 份文档**；报告 **v1.5**（551 行）+ 汇报稿（305 行）；已提交子仓库 `068d136`
- 最近验证：**三轮独立定向复核** `conditional` → `conditional` → **`go`**（`REV-R002-R2-GO`）；证据 `EV-R002-ROUND2` valid；`vibe validate` = `{"errors": []}`
- 下一步：2026-10-12 mentor 汇报（用 `调研汇报提纲.md`）→ 定契约 A/B/C/D → 建 Project Goal → 穿最薄垂直切片

## 2026-10-11 第二阶段深挖全覆盖与报告 v1.5（阶段：solution-research 证据链收口）

- 状态：已完成（任务 `R-002` 第二轮）；复核 `REV-R002-R2-GO` = **`go`**
- **触发**：用户指令「继续深挖全部」——要求把剩余全部项目做源码级深挖（不止主 Agent 建议的 3 个）。
- **范围**：从 11/19 提升到 **19/22**。新增深挖 9 个项目（`xr_teleoperate`、`XRoboToolkit-Unity-Client`（PICO 端）、`XRoboToolkit-Teleop-ROS`、`quest-wrist-tracker`、`quest2ros`、`Quest2ROS2`、`isaac_ros_teleop`、`TeleVision`、`DexTeleGym`）。
- **方法**：并行只读委派 5 个 `codebase-onboarder` 后台子 Agent + 主 Agent 亲自补克隆并精读输入层；**每条关键结论均由主 Agent 用 shell 抽查**（子 Agent 无 `shell`，`FI-002` 再次复现）。
- **★ 关键取证动作**：`xr_teleoperate` 的 XR 输入层是 **submodule，浅克隆后目录为空** → 上一轮所有输入层结论只能停在"调用方视角"。**补克隆 `televuer`（MIT）/ `teleimager`（Apache-2.0）/ `dex-retargeting`（MIT）后，输入层第一次可见。** 克隆数 19 → **22**。
- **★ 五处改变判断的结论（勘误 24–28）**：
  1. **`isaac_ros_teleop` 不是绕过 CloudXR 的路径，而是 CloudXR 的更深封装**（打包层；安装 `isaacteleop[cloudxr]`；launch 暴露 `cloudxr_accept_eula`）→ 与 `IsaacTeleop` 属**同一输入层候选**，① 层独立候选池**减少一个**。
  2. **`xr_teleoperate` 的失联保护是假的**——`motion_data_ready` 是**闩锁**（置 `True` 后全文无复位点）→ `if` 恒真；臂部路径**连检查都没有**；所有 XR 回调被 `except: pass` 包裹 → **实际保护 = 0**。**「看起来有、实际没有」的典型安全陷阱。**
  3. **`televuer` 是 ① 层契约最可读的候选**（**MIT**，**32 字段** dataclass，`wrist_pose` = 4×4 SE(3)，`arm_reference_mode` 坐标帧参数化）→ 与 `PiperPilot` 互相印证「XR 输出 SE3、IK 下沉」；**该分层现有 4 个独立实现印证**。
  4. **`DexTeleGym` 三重许可问题**（**无授权** + 内嵌**禁止再分发**的专有 Isaac Gym + 抹掉上游 Apache-2.0 声明）→ **代码与资产均不可采用**（强于 `reference-only`）。
  5. **`TeleVision` 降级为 `reference-only`**（全仓无 PICO、无 Franka/UR；**原始录制不在仓库**；依赖 2024 快照）。
- **新增文档**：`source-deepdive/` 新增 5 份（`televuer-xr-input.md`、`xr_teleoperate.md`、`isaac_ros_teleop-television.md`、`quest-input-line.md`、`dextelegym.md`）→ 共 **13 份**；`README.md` 索引与候选矩阵全面更新。
- **报告 v1.5**（551 行，勘误 19–28）与**汇报稿**（305 行，新增判断 3b）同步修正；**修正覆盖正文**（§7.1 / §7.5 / §7.6 / §7.7 / §8 路线 B·E / §10 R3·R5·R13–R15 / 附录 A），**不只改摘要**。
- **验证**：三轮独立定向复核。第 1 轮发现 **10 处定量与一致性问题**（含 `TeleData` 字段数 25→**32**、候选池未同步、文件数"54"实为**含 `.git`** 而受控仅 **25**）；第 2 轮发现 4 处残留（含**悬空引用「判断 9」**、深挖文档口径未同步）；**第 3 轮 4 处全部确认修复 + A/B/C 全局扫描通过 → `go`**。
- **未验证项**：无 L3 真机证据；无 L4 我方实测；GitHub 元数据未独立复现；`teleimager` / `dex-retargeting` 仅到「结构 + 许可证」层；补克隆的 submodule 非 superproject pin。

## 2026-10-11 第二阶段源码深挖与报告 v1.4（阶段：solution-research 证据升级）

- 状态：进行中（任务 `R-002`）
- **范围**：19 个本地克隆中 **11 个**达 L2 源码级深挖；新增 4 个克隆（`IsaacTeleop`、`XRoboToolkit` 三仓库）。
- **新产物**：`.project-log/docs/source-deepdive/` **8 份文档**——`README.md`（索引 + **候选矩阵**：层 × 契约 × 候选 × 复用强度 × 许可证 × 证据级）+ 7 个项目深挖（`franka-vr-teleop`、`lerobot_ur_dual_vrteleop`、`isaacteleop`、`xrobotoolkit`、`lbx-Franka-Teach`、`lerobot-plugins`、`piper`）。
- **三项改变原判断的发现**：
  1. **契约 C 从"二选一"变为四条路**；**动作空间必须统一在末端位姿层**（`PiperPilot` 的 `action.arm_eef:7` vs `pico-piper-teleop` 的 `commanded_joint_deg`；关节角在 Franka 7 / Piper 6 / UR 6 自由度不同时数据集不可合并）。
  2. **时间同步不是空白**：`IsaacTeleop` 的 `DeviceDataTimestamp` 双时钟（`sample_time_raw_device_clock` + `sample_time_local_common_clock`）是成熟契约。
  3. **失联保护与急停在所有先例中均缺失或不完整**（`PiperPilot` 的 `emergency_stop()` 是死代码；两个 UR/Franka 先例无 watchdog）→ 必须自研。
- **其它更正**：`lbx-Franka-Teach` 的「DROID 兼容」**不成立**（自定义 `labelbox_robotics` MCAP）；「40Hz/6.6Hz」非设计参数；`XRoboToolkit-Teleop-ROS`「不支持 Quest」措辞过强（Quest 客户端存在但是**功能裁剪分支**）；`quest-wrist-tracker` 元数据补全（265★ / Apache-2.0，**已改名 `hand-tracking-streamer`**）。
- **报告改 v1.4**（461 行，勘误 19–23）；汇报稿同步（268 行，新增**判断 7/8**）。
- **验证**：两轮定向独立复核均 `partial` → 已清零。复核再次抓到**同一类错误**：我只改摘要与附录、**正文表格残留 6 处**（报告一度自相矛盾）；另抓到 PICO 客户端克隆状态三处冲突。
- **★ 证据升级**：PICO 客户端 `XRoboToolkit-Unity-Client` 已克隆（253.7 MB，`fsck` clean），`LICENSE.txt` = **MIT**（© 2025 XR Robotics）→ 许可证证据 **L1 → L2**（勘误 23）。
- 未验证：无 L3 真机证据；无 L4 我方实测；子 Agent 无 `shell` 权限无法算摘要（`FI-002` 再次复现）。

## 2026-10-11 许可证审计与报告 v1.3（阶段：solution-research 证据修正）

- 状态：已完成（任务 `DOC-007`；复核 `REV-DOC007` = `go`）
- **核心发现**：`XR-Robotics/XRoboToolkit-Unity-Client`（**PICO 客户端**）**实为 MIT 许可证**（`LICENSE.txt`，1265 B，© 2025 XR Robotics）→ **撤销 v1.2「整条 PICO 路线存在法务阻断风险」的判断**。误判根因：只探测文件名 `LICENSE`，未试 `LICENSE.txt`（归因 `verification-harness`）。
- **新产物**：`.project-log/docs/license-audit.md`（全树扫描 + GitHub API 双向验证）。分类：**17 宽松 / 8 无许可证文件（3 明确无授权 + 4 自述有授权但文件缺失 + 1 未核实）/ 2 受限（1 禁商用 CC BY-NC-SA、1 专有）/ 1 授权不清晰**。
- **报告改 v1.3**（勘误 14–18 共 5 处修正）；`调研汇报提纲.md` 同步（§0/§5/§7/附录 A/B）。
- **验证**：三轮独立定向复核 `partial` → `partial` → **`go`**。复核独立发现并促成纠正了**我自己新引入的 1 处事实错误**（把 2 个 HuggingFace 头 + 8 个 Franka Robotics `.dae` 合并成"10 个文件"）与 4 处传播残留。
- **方法学教训**：① `NOASSERTION` ≠ 无许可证；② **「无许可证文件」≠「无授权」**（README/源码头可能有声明）；③ 两次错误的共同根因都是「我的探测没找到」→「不存在」的跳跃。
- 未验证：`ZorAttC/franka_vr` 授权内容未核实；复核方无 `shell` 权限（框架问题 `FI-002`）。

## 2026-10-11 组合式路线方法论与汇报材料（阶段：solution-research 前置基建）

- 状态：已完成（任务 `DOC-003` / `DOC-004` / `DOC-005`）
- 完成内容：
  - `.project-log/docs/modularization-strategy.md`（147 行）：按接口契约的组合式方法论，含 4 个契约面、② 先动手的关键纠正、复用强度四档 + 许可证过滤、四步执行顺序、版本锁定实测约束。
  - `VR数采调研/调研汇报提纲.md`（222 行）：**面向 mentor 单独汇报（1v1）**的材料，按「求指正」而非「推销方案」组织——开场三句 / 6 条核心判断 / 路径建议 / 许可证风险 / P0 零机械臂成本验证 / **三个请导师指导的问题（各附我的倾向）** / **主动暴露 5 条可能错误** / 候选速查表 / 可能被追问的 7 问备答。
- 验证与限制：汇报稿关键数字与报告 v1.2 逐项核对一致。
- 证据变更：`EV-DOC004`（混合听众版）因产物重写转为 `stale`，由 `EV-DOC005` 接替。
- 提交留痕（`DOC-006`）：子仓库 `eb8809e`（报告 v1.2，434 insertions）、`d30878e`（mentor 汇报提纲，222 insertions）；工作树 clean。⚠️ **该仓库无远端**，提交仅存于本机。
- 已知风险 `DEC-002`（active）：无远端、无异地副本 → 磁盘故障即全丢。用户决定**汇报后再定**备份方式（知识库归档 or 配置远端）。
- 框架问题（新增）：`FI-007` —— `vibe init` 不建立 Project Goal，但全局规则称其为「唯一完成契约」，本项目已在 `goal_id: null` 下运行 11 个任务而无告警。
- 待办：项目尚无 Project Goal（`vibe status` 显示 `goal_id: null`），正式开工前应建立，作为完成契约。
- 下一步：2026-10-12 开始正式工作。

## 2026-10-11 第一阶段 · 生态普查（阶段：solution-research）

- 状态：已完成（任务 `R-001`，`review_verdict: go`）
- 完成内容：
  - 《第一阶段生态普查报告》v1.2，434 行，覆盖 30+ 项目。
  - 核心结论：公开生态**无** PICO→Franka 专门项目；双端统一输入层 3 候选（`NVIDIA/IsaacTeleop`、`XRoboToolkit`、`xr_teleoperate`）；原第一轮文档**遗漏 `NVIDIA/IsaacTeleop` 与整个 Piper 生态**；Franka 侧全部 Quest-only；`XRoboToolkit` 输入层已被第三方源码级复用；LeRobot 插件模式（`lerobot_robot_*` + `lerobot_teleoperator_*`）可作机器人层骨架。
  - 对第一轮文档给出 **13 条勘误/补充**（含许可证误标、遗漏候选、Limitation 未指出）。
  - `DOC-001`：分层架构模型形成工作共识，落盘 `.project-log/docs/architecture-model.md`（249 行）。
  - `DOC-002`：模型 §7 的 4 个实现层问题按用户决定标记为**保留待确认**，登记 `OQ-001`~`OQ-004`（`deferred`）与 `DEC-001`（`active`）。
- 验证与限制：
  - 两轮 `verification-reviewer` 独立只读复核：一轮 `partial`（证据分级与引用纪律缺陷）→ 修订 → 二轮 `go`。
  - 未验证：GitHub 元数据无独立复现；无 L3/L4 证据；`XRoboToolkit-Unity-Client` 许可证仍为 L1。
- 下一步：等待用户评审。

## 2026-10-11 项目初始化（阶段：project-init）

- 状态：已完成（任务 `INIT-001` / `INIT-002` / `INIT-003` / `INIT-004`）
- 完成内容：
  - 工作区定为纯目录布局；子仓库 `VR数采调研\` 建立；基线提交 `11919e8`。
  - format 2 `.project-log` 创建成功；根 `AGENTS.md` 注入通用规则区块并写入项目级规则。
  - 框架问题清单 `.project-log/docs/framework-issues.md`（FI-001 ~ FI-006）建立。
  - 人读摘要 `current-session.md` / `progress.md` 由模板占位更新为实际状态。
- 验证与限制：
  - 独立 `verification-reviewer` 复核两轮（静态 `partial` → 补运行时证据 `go`）；静态 9 项声称全部证实。
  - 未验证项：`remote_durability`（尚未归档到知识库，属预期）。
- 下一步：进入第一阶段生态普查。

<!--
旧段落按日期倒序向下追加；超过约 50-100 KB 时归档到
`.project-log/docs/archive/`，归档文件按日期可检索。
-->
