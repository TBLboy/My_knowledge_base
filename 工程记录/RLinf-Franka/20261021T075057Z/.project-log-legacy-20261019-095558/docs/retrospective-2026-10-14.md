# 全工程复盘 — 2026-10-14

> 任务：T-004-project-retrospective（quick / docs-only）
> 依据：Project Log format 2 状态库 rev 83（D-001~D-020、RS-001~RS-006、A-001~A-008、E-001~E-014、Q-001~Q-005）
> 性质：结论性复盘；不含新增实现。精确状态以状态库与生成的 handoff.md 为准。

## 1. 目标与当前定位

- 项目定位：基于 RLinf 的真机数据采集 —— Pico VR 遥操作 Franka Research 3 单臂，
  采集人类演示轨迹，服务 VLA 监督微调（SFT）、HG-DAgger 在线干预与真机 RL 部署。
- 当前阶段：implementation。
- 一句话结论：**软件链路已全线打通并首次真机闭环成功；但"能产出可用数据集"这一目标尚未成立。**

## 2. 事实基线（已核实）

- 代码：RLinf `main` 固定提交 `50f22ad`；franky + libfranka 0.19.0，免 ROS；仅单臂。
- 硬件：FR3；系统镜像 5.10.0；Shop Floor `172.16.0.2/24`；本机 `enp3s0=172.16.0.200/24`（可 ping）。
- 夹爪：Robotiq，USB-RS485 + Modbus RTU，by-id 路径已固定。
- 相机：ZED 2i 的 UVC 裸流 + out-of-tree `zed_uvc` 后端（免 ZED SDK、免 NVIDIA GPU）。
- 环境：`RLinf/.venv`（uv，Python 3.11.14）；Ray 必须在激活 `.venv` 之后启动。

## 3. 决策链（20 条 active）

| 主题 | 决策 |
|---|---|
| 形态与仓库 | D-001 普通工作目录 / D-002 个人仓库 / D-004 main 留白、工作在 dev |
| 技术选型 | D-005 RLinf main@50f22ad、D-006 libfranka 0.19.0、D-007 无 GPU 只做采集、D-009 uv + Robotiq、D-011 国内镜像、D-012 realtime enforce、D-013 FrankaEnv-v1、D-014 ZED UVC 后端、D-015 disable_validate |
| 安全 | D-016 放宽安全盒 + `target_ee_pose` 移出可达范围 |
| 交互体验 | D-019 旋转力矩权限 1.6→12 Nm、D-020 姿态窗口居中不变量 + 提速 |
| 工程化 | D-017 卸载 v2rayn 恢复 apt、D-018 一键脚本 + 文档重整 |

## 4. 失败与返工（诚实清单）

1. **同一个"旋转迟钝"被修了三次**（A-006 → D-019 → D-020）。根因不是 IK，而是笛卡尔阻抗
   旋转 `error_clip` 过紧（1.6 Nm < 腕部重力+摩擦）。第一次只调力矩；第二次发现姿态窗口没有
   以复位姿态为中心；第三次发现"同步位姿后窗口又偏离"。→ **教训：修一个现象时，必须同时修"维持该现象不再出现的不变量"，否则同类问题会以新面貌反复出现。**
2. 自造缺陷 3 个（D-018 记录，已修）。
3. 文档误导：6.9 曾把 `demos/` 写成唯一交付通道，而它自 D-016 起恒空 → 已重写（A-007 相关）。
4. 安装受阻：A-002 `lerobot` git clone 被代理中断，`set -e` 导致收尾步骤未执行。
5. 框架缺陷 4 条：A-001（`--dry-run` 谎报成功）、A-003（`_RemoteNodeProbe` 不加载扩展模块）、
   A-004（CollectEpisode 记录 pre-teleop 动作）、A-008（记录类 CLI schema 不可发现）。

## 5. 验证质量

- valid：E-001~E-009、E-011、E-012、E-014
- candidate：E-013（提速待真机手感确认）
- stale：E-010（被 E-012 承接）
- **缺口：没有任何一条证据能证明"采集产物可用于训练"。** 这是当前最大的验证空洞。

## 6. 未验证 / 未决

未验证：夹爪真实开合（正确姿势下）· 末端最低点（需实测后收紧安全盒 z 下限）·
episode 结束/成功信号（应加 `keyboard_reward_wrapper: "start_end"`）· 相机取景是否覆盖末端（128×128 中心裁剪）。

未决问题：Q-001 RLinf 获取方式/仓库落点 · Q-002 硬件拓扑与部署形态 · Q-003 Project Goal 未建立 ·
Q-005 相机硬前置的最终选型。

## 7. 本次复盘的核心新结论：**"能遥操作" ≠ "能采集"**

逐段核对 `collect_real_data.py` 与 `CollectEpisode` 后确认：

1. **动作落盘恒为 0**（A-004）：`CollectEpisode` 位于 teleop 包装器**外层**，
   它 `_record_step` 记录的是调用方传入的 `action`（`collect_real_data.py` 里是
   `np.zeros((1, action_dim))`）；真实的遥操作动作由更内层的 teleop 包装器写进
   `info["intervene_action"]`。因此 `collected_data/*.pkl` 的 `actions` 全零。
2. **`demos/` 通道恒空**（A-007）：`collect_real_data.py` 只在
   `save_episode = (r_val >= 0.5 or manual_done)` 时才写入 ReplayBuffer；D-016 把
   `target_ee_pose` 移出可达范围后 reward 恒 0，配置里又没有 keyboard 包装器，
   `manual_done` 永远为 False → **永远不会保存任何 episode**。
3. 结果：**当前没有任何一条通道直接产出"动作正确"的数据**；真实动作只以原始形式保存在
   `collected_data/*.pkl` 的 `infos[*]["intervene_action"]` 内（未被消费）。

⇒ 结论：采集线路"链路通"但"不产出"。正式采集前必须修复，这是 T-006 的范围。

## 8. 框架摩擦（A-008）

一次文档任务 55 次调用中约 36% 用于记账，其中 14 次花在猜测记录类 CLI 的 schema；
而实际写入只有 2 分 59 秒。**瓶颈是可发现性，不是工作量。**

## 9. 精确下一步

1. **T-006（最高优先）**：修复"产出可用数据" —— 需用户在三选一方案中拍板（见下）。
2. **T-005**：参数微调（安全盒 z 下限、灵敏度）—— 可与 T-006 并行，但改动属 strict/安全级。
3. **真机**：新速度手感 + 第 2 步三项判定（操作者在场）。
4. **归档**：知识库路径未配置 → 远程持久化 unknown（用户已明确暂缓）。
