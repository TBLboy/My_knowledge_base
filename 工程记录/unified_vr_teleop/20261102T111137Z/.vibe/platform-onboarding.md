# 统一平台摸底

日期：2026-10-29。范围：Franka worktree 主线快照 374410f，远端 Piper 8807476、UR7e 32c4d93。已 fetch 核对引用；仅静态调查，不代表真机验收。

## 功能与实现边界

| 模块 | 源码实现程度 | 主要依据（相对 Dagger_web） |
| --- | --- | --- |
| 工作台 | 采集、遥操、设备、回放、统计、事件、设置页面及 API 已组装 | main.py、app/ui/ |
| 设备/配置 | 机型选择、配置校验、设备枚举、预检失效、安全连接门控；不是无标定自动识别 | robot/core/profiles.py、discovery.py、app/teleop/integration.py |
| XR | PICO 省电版 Unity 应用和 PC SDK 输入、连接恢复、按键处理 | PICO_XR_Link_PowerSave、robot/xr/、app/teleop/xr_link.py |
| VR 采集 | 手柄映射/IK/设备写入与相机录制分离，经遥测关联命令、时间对齐、写盘 | app/teleop/control_runtime.py、control_worker.py、app/capture/、app/storage/recorder.py |
| DAgger | 策略/人工/hold 仲裁、接管与交回、step journal、轨迹结果、复位结束逻辑已有代码 | app/teleop/dagger/input.py、episodes.py、control_runtime.py |
| 策略 | 本地规则进程、Piper 关节轨迹回放、外部 RemotePolicy 接口；不内置已训练模型 | app/inference/rule.py、app/teleop/dagger/{local_policy,replay,remote}.py |
| RL/评测 | episode 模式与标签逻辑存在；RL 明示无训练更新；采集页 workflow 启动仅 collect/dagger | app/teleop/dagger/episodes.py、app/teleop/capture_workflow.py |
| 数据处理 | 视频/数组/meta/spec、SQLite、回放质检、HDF5、NAS/SSH 上传队列 | app/storage/、app/ui/ui_playback.py |
| 安装 | Linux 工位依赖、XR 服务、分环境、运维脚本已存在；仍需地址/绑定/标定及硬件依赖 | tools/deploy/、config/robots/ |

## Piper / ARX5 适配

Piper 通过 SDK/CAN；ARX5 通过 ROS2 RobotStatus/RobotCmd（位置模式 5）。registry 创建各自 controller、IK、motion、reset、recovery、速度参数。ARX 控制类不继承 Piper，但同名机型文件拥有独立实现，不是只添加一个 SDK 包装。

两者复用页面、流程编排、XR 接收、Authority/Buttons、策略/episode、相机同步、数据写盘和上传。ARX 的 ArxArmManager 继承共享 DeviceArmManager，transport 转换反馈到统一格式，并将发出的参考指令写入命令日志供采集；命令不是执行完成 ACK。

主线 schema 假设每侧 6 关节+夹爪，共 7 维，双侧 qpos/action 14 维。依据 robot/common/samples.py、app/teleop/recording.py、app/storage/h5_export.py。Franka 7 关节+夹爪不能直接塞入该格式；控制循环、策略校验与输入仲裁也存在 [:6] 和第 6 项夹爪假设。

ARX 已接到共享 DAgger 控制路径，并非只有 VR 录制代码；但配置大量空值，未见本轮可确认的现场验收。规则策略可走公共 IK 路径，Piper 录制轨迹的真机执行回放明确拒绝非 Piper。远程模型对 ARX 的可用性还取决于外部适配包，不应宣称已完成模型联调。

## feature 分支的重要差异

### Piper 分支

origin/master 到 origin/feat/piper-modechange 为 0/2 提交差距，但改动远超两条标题：含目录清理、公共采集逻辑改造、UVC、Franka 控制和 schema v3。Franka 的 runtime 复用 Supervisor 协议、ControlServer、Authority/Buttons、Journal、LocalPolicy 和公共 Episodes；独立 worker 持有设备及租约，通过 FrankyArm/Robotiq 执行 TCP 目标。提供专用遥测、录制/导出、可视化、远程 TCP 策略协议；拒绝 Piper 关节轨迹执行回放。

依据：该分支 robot/franka/{runtime,worker,controller,manager,recording,policy}.py，app/teleop/integration.py 与 tools/tests/test_franka.py。测试文件覆盖模拟设备超时、故障、七轴录制/HDF5等，但本轮未执行，不能推断真机通过。该分支也改变缺失设备录制行为，不能未经确认直接整体合并。

### UR7e 分支

origin/master 到 origin/feat/ur7e-rlinf-bridge 为 0/7。main.py 后端开关选择独立操作台，RLinfUR7eClient 只发送状态/命令/预览请求，不打开机器人、不发关节目标。外部 RLinf 负责双 UR7e、相机、采集、人工接管和模型执行以及 LeRobot/HDF5 保存；本仓库负责网页与 PICO 原始输入发布。主线 UR7e RTDE 原型门控仍未解除。

依据：分支 docs/ur7e.md、app/teleop/rlinf_ur7e.py、app/ui/ui_ur7e.py、app/ur7e_main.py。外部 RLinf 仓库与验收记录未在本轮核查，文档描述的运行能力不等于本轮验证结果。

## Franka 下一步（建议，未批准实施）

1. 先确认 Piper 分支现有 Franka 适配是谁的工作、是否采用、合主线计划及真机状态；避免从 master 重复开发。
2. 确认第一阶段范围：VR 采集或同时 DAgger；明确相机/单侧双侧/夹爪/动作与数据契约，尤其缺失设备能否录制。
3. 再针对原 robot_capture_franka 的驱动、控制生命周期、坐标映射、遥测和已有现场结果，与上述 Franka 实现逐项差分；不整体搬运 UI 或并行重建采集上传系统。
4. 确定七轴与 TCP 动作的正式公共扩展边界，列明需许可的公共文件变更，保留 Piper/ARX 数据兼容。
5. 分阶段验证：离线契约/模拟 → 无控制设备反馈和相机 → 用户确认后的单臂低风险联调 → 采集回放导出 → DAgger（若纳入范围）。

## 验证限制

- 已交叉阅读入口、分派、transport、共享数据格式、控制仲裁/episode及 feature 实现；Git 引用与祖先差距已核对。
- 系统 Python import pytest 失败，未安装依赖、未运行 pytest；无硬件、未启动服务或执行运动。
- Franka worktree git status 保持干净；原 Franka 仓库有大量既有未提交修改，本轮仅只读参考，不将其认定为已提交或已验收版本。
