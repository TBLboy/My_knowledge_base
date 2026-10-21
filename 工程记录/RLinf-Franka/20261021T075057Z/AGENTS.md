<!-- VIBE-PROJECT-GENERAL:BEGIN -->
<!-- 通用开发规则（由 a-project-init 维护，勿手动删除；修改规则请改本模板后重新初始化） -->
1. 动手前先读取相关代码、配置、测试和根目录 `.vibe/` 中的相关项目状态，再判断和修改。
2. 遵循项目现有代码架构与约定，不引入与现有风格冲突的并行结构。
3. 新增功能优先不修改公共资源；若必须修改公共资源，先向用户说明并取得许可。
4. 最小改动，不做与当前任务无关的重构。
5. 修改前检查 Git 状态，保留用户与其他任务已有的未提交改动，不回滚无关文件。
6. 没有验证证据不声称完成；明确区分已实现、已验证、环境阻塞与未验证。
7. 若当前仓库为团队协作仓库，新增与主业务流程无关的文件（如测试文件、个人功能性脚本、文档等）时，先询问用户是否将这些文件加入 `.git/info/exclude` 不纳入跟踪，避免污染公共仓库提交。
8. 在项目过程中发现 Vibe Coding 框架自身的缺陷、bug 或文档漂移时，及时记录到本项目 `.vibe/` 的适当持久状态中（现象、复现步骤、期望与实际、涉及文件与提交、影响范围），供后续集中修复框架；不要因为"不属于本项目范围"而略过。

### 八荣八耻

1. 以暗猜接口为耻，以认真查阅为荣
2. 以模糊执行为耻，以寻求确认为荣
3. 以盲想业务为耻，以人类确认为荣
4. 以创造接口为耻，以复用现有为荣
5. 以跳过验证为耻，以主动测试为荣
6. 以破坏架构为耻，以遵循规范为荣
7. 以假装理解为耻，以诚实无知为荣
8. 以盲目修改为耻，以谨慎重构为荣
<!-- VIBE-PROJECT-GENERAL:END -->

## 项目级规则

- 仓库类型：个人仓库。父目录 `/home/modelbest/Project/RLinf-Franka` **不是 Git 仓库**，保存 `.vibe/`、本文件与项目文档；嵌套 Git 仓库为 `RLinf/`（分支 `work/pico-single-arm`）和 `RLinf-Franks/`（分支 `dev`）。不得假设两者可以一起提交或回滚。
- 项目状态唯一性：仅根目录 `.vibe/` 是活动 Vibe Coding V2 项目状态根；不得在 `RLinf/`、`RLinf-Franks/` 或其子目录初始化第二个 `.vibe/`。`.project-log-legacy-20261019-095558/` 仅作历史参考；持久 Task、项目进度与会话恢复分别遵循 `.vibe/README.md`。
- 项目定位：基于 RLinf embodied 的单臂 Franka Research 3 真机数据采集——Pico 遥操作采集人类演示，服务 VLA SFT、HG-DAgger 与真机 RL。RLinf/Franky 是唯一硬件控制者；外部工具只可做观测、启动和离线处理，不能直接控制 Franka、Pico 或相机。
- 外部遥操作方案、供应商文档和调研材料不是已验证事实：引用时标明证据层级（文档声明、可定位源码、外部真机证据、我方实测）；未到我方实测的结论不得作为真机行为或安全结论。
- 代码与检查点：RLinf 基线为 `main@50f22ad`，当前项目检查点 `e7a9a2e feat(embodiment): tune Pico Franka teleoperation`；采集扩展检查点为 `803ba2a feat(collection): preserve demo segment metadata`。提交前保留已有用户改动和未跟踪的参考资料，不把缓存、`__pycache__/` 或无关调研资料纳入提交。
- 真机安全：每次参数/控制改动先空载、小范围、工作区清空、急停可达；仅操作者发起真机会话。任何突跳、振荡、意外受力、Desk 告警或机器人错误，立即松 grip 并停止；不得为手感绕过 Desk SLS-C/SLP-C、碰撞行为或提高其阈值。真实硬件手感结论必须和启动日志、运行目录绑定。
- 硬件与环境：Franka Research 3（系统镜像 5.10.0，Shop Floor `172.16.0.2/24`）；主机 `enp3s0=172.16.0.200/24` 已通。后端为 franky + libfranka 0.19.0（无 ROS），Ubuntu 22.04.5 PREEMPT_RT。用 `RLinf/.venv`（Python 3.11.14/uv）运行项目；Vibe 的 conda 环境不能混用。无 NVIDIA GPU，只采集。
- 夹爪与相机：Robotiq 经 USB-RS485 Modbus RTU，使用 `/dev/serial/by-id/` 稳定路径。两台 UVC 相机均已实测：ZED 2i 为工作台视角，ZED-M 为腕部视角；必须接 USB 3.0，`zed_uvc` 是 `RLinf-Franks/rlinf_ext/` 的 out-of-tree 后端，经 `RLINF_EXT_MODULE=rlinf_ext` 注册。UVC 无深度，`enable_camera_depth: false`；不改 RLinf 公共相机注册表。
- 启动与采集：唯一推荐入口是 `bash RLinf-Franks/run_pico_session.sh`；它负责前检（含相机预检）、XRoboToolkit PC Service、Pico 发布器、数据探针、Ray 生命周期及收尾。Ray 只能在该脚本所设 `RLINF_EXT_MODULE` 环境之后启动。录制键位以源码为准：`a` 开始/中止、`b` 分段、`c` 成功结束；录制窗口内必须按住 grip。键盘固定用 `RLINF_KEYBOARD_DEVICE`，避免 BRLTTY 虚拟键盘。前检会逐台解析 `camera_serials`：某台相机只出现 HID、没有 `/dev/v4l/by-id` 视频节点时直接中止并提示换 USB 3.0 口（`A-011` 已复发，2026-10-15）。
- 数据交付（D-021）：采集期保存信息丰富的 `collected_data/*.pkl`，后处理用 `RLinf-Franks/post_process_to_lerobot.py` 导出标准 LeRobot。顶层 pickle `actions` 可能恒 0；真实动作取 `infos[*].intervene_action`。新录制的 pickle 必须保留 `segment_ids`，转换器将其导出为 LeRobot `segment_id`；历史缺失数据只允许以 0 兼容，不得伪造分段。
- 当前采集链路：`start_end_timeout` 已实测，录制期默认 3000 步、外层上限 3600 步；timeout 写 `_fail.pkl`，不计入 demos。rich Pico 字段、双相机、`demos/*.pt`、pickle→LeRobot、键盘权限和 watchdog 已真机验证。运行后用 `RLinf-Franks/check_collection_run.py --run-dir <run>` 做 fail-closed 质量检查。
- 采集环境：使用 `env/realworld_franka_sft_env`（FrankaEnv-v1），不用官方 Pico `PegInsertionEnv`。当前遥操作参数是已验证但仍在调优的安全敏感配置：`position_scale=rotation_scale=1.0`、`action_scale=[0.04,0.3,1.0]`、Franky `max_step=0.04m`；平移运行时 `K_t=1200N/m`、clip `[.02,.02,.02]m`（约24N/轴）；旋转运行时 `K_r=80Nm/rad`、clip `[.20,.20,.20]rad`（约16Nm/轴）。这些值不可凭记忆改动：每次只改一个参数组、先记录 C 级授权、静态解析并让 Worker 日志确认实际生效值。
- 已知调优问题：T-04/T-05 后整体跟手提升；仍待诊断的是手柄 roll 导致机械臂抖动，以及偶发卡顿后执行陈旧命令。不得在未定位原因前继续提高旋转力矩、角速度、全局 dynamics factor、力矩变化率或 Desk 限制。调参事实与试验结果唯一台账为 `TELEOP_TUNING_LOG.md`；历史依据保存在 `.project-log-legacy-20261019-095558/`，当前持久项目状态保存在 `.vibe/`。
- 工作空间：当前应用层 `ee_pose_limit_*` 约为 ±2m / ±2rad，实际近乎无保护；绝不再放宽。修改 reset pose 时必须用 `sync_reset_pose.py` 同步姿态窗口的中心，位置盒不随 reset 漂移。
- 参考材料：`RLinf-Franks/deepseek_markdown_20261012_00b29d.md` 是第三方旧说明，含已证实错误路径和命令，不得作为实现依据；以当前仓库代码、官方教程和项目日志为准。
- 子目录命名注意：`RLinf-Franks` 与父目录 `RLinf-Franka` 拼写不同，保持原样。下载项目依赖默认使用国内镜像环境。
