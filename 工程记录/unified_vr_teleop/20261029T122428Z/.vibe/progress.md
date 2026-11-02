# 项目进度

## 已确认方向

- 统一平台承载多构型的 VR 遥操作采集、DAgger 等功能；目标是在新工位使用同一版本，通过适配与现场配置运行，不按机械臂维护平台分叉。
- 当前工作对象为 `unified_vr_teleop_franka/` 的 `feat/franka`，基于 master `374410f`；原 `robot_capture_franka/` 为参考，不修改其业务链路。
- 所有子仓库和 worktree 共用本根目录 `.vibe/`。

## 已批准的统一平台标准（2026-10-29）

以下为用户确认的目标标准，不表示当前代码已实现；后续按增量逐步靠拢，不据此直接启动整体重构或修改公共模块。

- **公共流程统一**：PICO → 统一输入层（接收、时间戳、有效性、连接恢复）→ 公共遥操作层（按键、使能、Grip 锚定、人工/策略控制权）→ 机器人适配层 → 驱动通信 → 硬件。公共流程复用；机型/工位参数可以不同。
- **差异集中到适配层与配置**：坐标映射、关节/笛卡尔目标转换、六轴/七轴运动学、限位/工作空间、夹爪、保持、复位及故障恢复由机器人适配实现，不在公共页面、控制权和采集流程中散布机型判断。
- **采集是旁挂链路**：相机/音频、标准化机器人状态、控制参考和事件进入公共同步、录制、回放、导出与上传；采集存储不得成为运动控制关键路径，不直接依赖具体机械臂 SDK。允许读取标准机器人描述，不要求所有机器人硬件能力相同。
- **动作与状态语义明确**：分别表达遥操作/策略请求目标、经约束后实际提交给驱动的控制参考以及硬件实测状态；提交参考不等于物理执行完成确认。记录控制来源、接管事件及数据有效性，不能将反馈冒充控制命令。
- **统一数据契约，而非按机型各建一套**：统一文件结构、字段命名、版本规则、时间戳、单位、坐标系、四元数顺序、状态/动作语义、控制来源、有效性与缺失标记，以及机器人/传感器描述。六轴/七轴、单臂/双臂的数据维度允许不同，由描述信息明确表达；不截断第七轴，不把夹爪混作机械臂关节。
- **尚未冻结具体技术规格**：字段路径、格式版本、历史数据兼容/迁移策略、缺失设备业务规则以及是否统一为 TCP 策略动作，仍需后续分别澄清确认；不能仅凭此标准宣称跨机型策略或历史数据已兼容。

## HDF5 新数据落盘业务基线（2026-10-29）

- 用户提供的《Robot Capture HDF5 输出业务基线》已作为本项目新数据落盘的业务约束；附件《自采数据 HDF5 落盘规范》作为格式参考。只改新采集数据，不自动迁移历史 HDF5；不改 Franka 控制算法、安全参数或 `cam_dup`。
- 新 episode 统一写主时间轴、JPEG、本体状态、EEF action、任务元数据；缺失数据不写、不补零、不伪造，真实零值必须保留。
- Franka `robot_id` 固定为 `Franka Research 3`；单臂使用 `main`，双臂使用 `left/right`；EEF action 为 `action/<side>/eef_pose (T,7)` 与 `gripper (T,1)`，姿态 `[x,y,z,qx,qy,qz,qw]`，不得把实测 EEF 冒充 action。
- HDF5、task、batch、episode、manifest、MD5、原子写入和 `_SUCCESS` 按基线实施；未封口 batch 不视为完整交付。废弃 episode 保留文件和编号，异常 episode 待人工质检后再上传。
- 基线明确覆盖参考规范中的冲突：不实现 `cam_dup`；不使用 joint action；字段具体版本、历史兼容、缺失帧业务处理、质检拒收对 batch 封口的规则仍需技术设计或后续澄清。
- 用户进一步确认：禁止的是用全 0 **伪造/占位**缺失数据，不是禁止真实 action 或状态出现全 0；真实采集到的全 0 必须原样保留，不能用“整列全 0”作为缺失判断。此前关于“每帧必须有有效 action、否则拒收”的建议撤回，不能据此固化业务规则；action 的逐帧缺失语义需基于实际采集流程继续设计。
- 业务基线已按当前框架规则迁移到 `.vibe/requirements/README.md` 与 `.vibe/requirements/hdf5-recording-format.md`；不再使用错误的根级 `.vibe/requirements.md`。当前 baseline v1.1 只保留 HDF5 与统一采集语义，人员分工、实施顺序和完整架构计划不混入业务 baseline。录制期间一段时间无 action 的处理暂不解决；整条 episode 无 action 时 `has_action=false` 且不创建 `/action/`。
- 新增独立 baseline `.vibe/requirements/unified-platform-integration-boundary.md` v1.0，记录柏霖/小航/桉池/姜灏分工、公共设备发现/VR 启动/控制/采集边界、按型号适配连接与控制、config 驱动 Web 页面，以及 VR 到 `rlinf_pipe` 的解耦边界。
- `unified-platform-integration-boundary` 已升级为 v1.1：用户批准 PICO → 统一输入层 → 公共 runtime 输出统一 TeleopTarget → 通用 worker → RobotAdapter → 驱动通信 → 硬件的目标架构。worker 只负责通用执行生命周期/安全协议；运动学、EEF/关节转换、夹爪、限位、复位和故障恢复属于 RobotAdapter。当前 Franka 独立 runtime 明确为过渡实现，后续再收敛，不在当前 Franka 功能适配阶段直接重构公共编排。
- 已确认当前 `unified_vr_teleop*/Dagger_web/` 下没有独立 `runtime/` 代码目录，公共 runtime/worker 代码实际位于 `app/teleop/`。先在 `feat/franka` 分支将 Franka 收敛为公共 `app/teleop` runtime/worker + `robot/franka` adapter + `config/robots/franka.yaml`，再合并 master，其他构型后续按该形态对齐。
- DAgger/推理/评测清理已按清单落地：删除纯策略模块、策略 UI/脚本/测试和策略配置，裁剪公共控制、工作流、页面与 Franka 过渡 runtime；保留普通 VR 采集、录制、上传、采集数据回放质检和机器人控制。清理相关静态引用审计、编译和离线测试已通过。
- `unified-platform-integration-boundary` 升级为 v1.3：每个 `robot/<type>/` 还需提供构型专属设备状态检查逻辑；公共 Web 只提供统一检查入口和结果展示，按 config 选择检查实现，公共页面不得直接访问厂商协议。

## 平台摸底（2026-10-29）

- 主线控制、遥测分派支持 Piper 和 ARX5；UR7e、Franka 被代码门控为待开发。ARX5 配置尚缺型号、URDF、末端、关节名与夹爪标定；不能据源码声称现场可直接使用。
- 公共链路包含 NiceGUI 页面、设备预检、XR 输入、控制进程编排、控制权、episode、相机同步、录制、回放、HDF5 和上传。ARX5 独立实现控制/运动学/映射/复位/恢复，经 ROS2 transport 接入共享六轴采集格式。
- DAgger 有控制权切换和记录实现，本地策略为规则而非训练模型；轨迹执行回放仅 Piper 开放。RL 是流程联调，无训练更新。
- 重要：`origin/feat/piper-modechange`（8807476）不止 Piper 改动，已有 `robot/franka/`、七轴 schema v3、UVC、公共采集改造和 Franka 测试；尚未合入 master。后续应先确认其来源与是否团队认可，避免重复实现。
- `origin/feat/ur7e-rlinf-bridge`（32c4d93）通过独立网页/UNIX socket 对接外部 RLinf，由外部执行端负责控制、采集、DAgger 与数据保存，并非主线 registry 控制器适配。
- 详细依据与下一步建议见 `.vibe/platform-onboarding.md`。本轮只读源码，未运行硬件或测试套件；系统 Python 缺 pytest。

## 已知限制

- 待讨论需求（2026-10-29）：采集数据时记录相机内参和外参，已在 `requirements/hdf5-recording-format.md` 的变更候选中记录。可行性、参数来源、外参参考系和缺失处理尚未确认；不改变 active v1.1、不新增当前强制验收项，暂不实施。

- 三方差异见 `.vibe/franka-adaptation-comparison.md`：归一化导入后17个原驱动文件中15个AST一致；同事适配重接了输入/生命周期/采集。主动重标定与当前姿态设为复位目标的旧入口未接入；按键、复位夹爪行为、缺失数据策略和HDF5字段有差异。左侧复位Z与当前原rig相差约16cm，不自动迁移标定。用户表示代码可能由同事参考原工程完成，待沟通处理，不合并或重复实现。

- Vibe 多仓库记忆根目录解析：Session 移到 `unified_vr_teleop_franka/` 后，在总根目录 `.vibe/tasks/platform-onboarding.json` 写入 Task，再调用 `vibe_task_control(start)`，实际返回 persisted Task file could not be read；期望按根 AGENTS 第 9 条读取共享 Task。涉及根 AGENTS、根 Task 文件及框架 Task 路径解析。临时将 Session 工作目录恢复到总根后 start 成功；业务读取仍明确定位 Franka worktree。未改框架代码，未在子目录建立 .vibe。
- Franka 架构对齐审计见 `.vibe/franka-adaptation-alignment.md`：Franka 的连接/控制代码已配置化并集中在 `robot/franka/`，但通过独立 `robot.franka.runtime` 绕过 Piper/ARX5 使用的公共 `control_runtime`/`control_worker`；公共编排层仍有 Piper 硬编码。UR7e 在 master 仍是 pending。当前总 `.venv` 测试因缺少 scipy 在收集阶段阻塞，未取得通过证据。
- 清理后的完整测试套件收集到 324 项；清理相关选择集为 67 passed、9 subtests passed。完整套件剩余 3 个既有失败：Piper fake 未提供 `MotionCtrl_2`、上传脚本目的路径断言漂移、human 速度上限断言不符；未将其误归因于本次清理。
