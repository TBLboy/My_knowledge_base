# Franka 适配三方差异

2026-10-29。基准：master/feat-franka 374410f；同事分支 origin/feat/piper-modechange 8807476；原工程以当前本地文件为准（包含既有未提交修改）。只读静态对比，不代表现场验收或历史来源证明。

## 复用证据

对原 `robot_capture_franka/franka/drivers/` 的 17 个 Python 文件与分支 `Dagger_web/robot/franka/drivers/` 比较，归一化 `franka.*` 到 `robot.franka.*` 的 import 路径后，15 个文件 AST 相同，包括 Franky 主驱动、设备占用锁与基础类。另两文件：Pico 增加 autostart 参数以只复用坐标数学、不启动独立接收；Robotiq 修改通信超时和错误处理。这强烈支持代码复用判断，但不能证明作者使用了哪个历史提交。

## 行为差异

| 项目 | 原工程 | 同事分支 | 判断 |
| --- | --- | --- | --- |
| 驱动 | FrankyArm/FCI、Robotiq 串口 | 同一驱动主体；统一 namespace | 核心复用，不是新驱动 |
| 输入 | Pico 发布器 → IPC/ZMQ → 各侧 PicoExpert | 公共 SDK 接收进程 → PoseClutch → PicoExpert 数学 | 接收链路重接，需要实测延迟/重连 |
| 位姿 | Grip 时固定机器人锚点，加手柄累计位移；按固定欧拉窗口裁剪 | 同样锚点组合及窗口裁剪；Grip 必须先释放 | 核心数学一致，不代表整条控制等价 |
| 标定 | 右摇杆按下触发配对标定；RigBackend.calibrate 验证各侧并同时应用 | PoseClutch 禁用标定按键，仅依赖默认初始标定；未见相应主动重标定接口 | 旧操作入口未迁入，不可把驱动内有方法当成已接入 |
| 开始录制 | 左摇杆按下；Y 成功；X 丢弃；A+X 复位 | collect 中 A 开始、Y 保存、X 丢弃；左单臂将 X 映射成开始；DAgger A 接管/B 交回 | 操作习惯改变；左单臂丢弃入口需单独确认 |
| 复位目标保存 | 页面确认设定当前姿态，协调器原子写 rig 配置 | 页面/worker 使用 YAML 固定姿态；worker 操作无 set_reset_pose | 未迁入现场设定位姿工作流 |
| 复位动作 | 按配置时长插值；前关闭夹爪、后打开；可恢复原控制循环 | 按距离/角差计算时长，保持夹爪开度；按反馈距离/姿态判定到位，超时拒绝 | 明确业务差异，不能静默沿用 |
| 故障/超时 | 后端停止生产目标，状态/录制门控，成对复位故障协调 | 独立硬件 owner，目标 200ms/租约 500ms watchdog，显式停止 tracker；故障锁定 | 新增机制存在，但故障下硬停能力仍需真机验收 |
| 夹爪线程 | 发送差值 2mm；反馈约 100ms；Modbus timeout 1s | 差值 0.5mm；线程间隔20ms加IO耗时；timeout50ms、retries0；错误抛出 | 灵敏度与通信容错改变 |
| 单臂相机 | rig.active_cameras：选中侧腕相机+全局，两路；双臂三路 | 固定 left/center/right 三槽，可缺失并黑帧标记 | 文件布局和缺失语义改变 |
| 缺失数据 | 选中侧遥测匹配不到相机时调用故障结束录制 | 保留视频和缺失标记；部分数据允许录制，导出再严格检查 | 不仅 Franka，公共采集规则也变更 |
| 数据动作 | 7关节反馈；每侧 TCP xyzw 7+夹爪1 动作 | 同样区分7关节反馈与8维TCP动作，增加 action_valid/夹爪有效性 | 方向一致，文件契约不完全兼容 |
| DAgger | 所查原控制链为遥操作，无对应统一 Authority/策略/episode 流程 | 对接公共 Authority/Journal/Episodes，规则和远程TCP策略；拒绝Piper关节回放 | 新增平台能力，未验证模型联调 |

## 数据契约不能仅看 schema_version=3

原 app/h5_export.py 多侧 schema v3 使用 `robot/<side>/command_tcp_target`、`command_gripper_target`、`timestamp`；同事 recording.py 使用 `robot/<side>/tcp_target`、`gripper_target`、`sample_wall_ts`，另有 action_valid，标量维度约定也有差异。两者都写 v3 但不是同一个字段契约。现有训练/读取程序是否兼容必须实测，不能直接声称历史数据兼容。

## 工位参数漂移

原当前 rig 左侧 reset xyz = [0.5575695238, -0.1992708666, 0.260377417]；同事 YAML = [0.5631575584, -0.1950313300, 0.4202235937]，Z 相差约16cm。两侧 IP/夹爪串口与 rig 对应。此差异可能是预期调参，也可能是快照漂移，不判断孰对，禁止自动覆盖工位标定。当前原 rig mode 实际为 dual（历史文档曾描述 left，不作为当前事实）。

## 需确认而非立即修改

1. 同事分支的来源快照、真机验证记录、哪些公共行为获团队认可及合主线计划。
2. 统一按键与旧使用习惯的取舍；左单臂如何丢弃，以及保留手动重标定/设定复位位姿与否。
3. 复位夹爪保持还是开合；目标姿态以哪份现场配置为准。
4. 缺相机/遥测时阻止、终止，还是允许录制并标无效；统一平台和训练侧是否接受。
5. HDF5 正式字段、版本、历史兼容及有效性掩码消费规则。

## 验证

运行了标准库 AST/文本差异比较（17个驱动文件）与分支10个Franka模块语法解析；未import设备SDK，未执行控制代码。Franka worktree保持干净。系统Python缺numpy/scipy/yaml/pytest，未运行行为测试或真机；不安装依赖，不执行原目录中的跨平台虚拟环境二进制。以上为代码实现差异，不是缺陷已复现或业务规则已批准。
