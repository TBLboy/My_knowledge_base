# 平台操作体验重构分析（2026-10-30，基于 Franka 真机首测反馈）

来源：用户真机测试反馈 + 源码核对（`unified_vr_teleop_franka/Dagger_web`，feat/franka@2e29e35 + 远端未提交环境改动）。

## 1. 现状问题与证据

### 1.1 信息架构混乱（三个设置入口）
- 导航：`record / teleop / playback / stats / events / devices / settings`（`main.py:626`）。
- 与"设置"相关的页面有三个：`ui_settings.py`（机型选择、相机绑定、检测硬件）、`ui_devices.py`（Franka 走 `app/ui/franka.py::devices`：检测硬件、连接/断开 Franka、相机配置文本）、`ui_teleop.py`/`franka.py::teleop`（左右臂选择、XR 面板、检查手柄/FCI/预检/结束检查/执行/复位/保存复位姿态/标定/暂停）。
- 采集页 `ui_record.py` 又有"连接 Franka / 断开 Franka"（`can_start/can_stop` 映射 `franka_connect`）、相机启动、交换 CAN 映射等按钮。
- 重复：硬件检测在设置页与设备页各一份；Franka 连接在设备页与采集页各一份；相机绑定在设置页，相机配置又在设备页只读展示。
- 暴露了本应自动化的内部步骤：检查手柄(input)、检查 FCI 反馈(check)、运控预检(preview)、结束检查(stop)、启动执行(execute) 五个按钮本质上是 supervisor 的内部状态机动作。

### 1.2 启动流程非一键（Franka 真机证据）
- 事件日志仅有 `control.check → control.stop → control.input`，没有 `preview/execute`；"连接 Franka"只启动 adapter worker（`FrankaArmManager.start → Client.ensure`），"检查手柄"只进入 input 模式，二者都不会进入执行。
- 还需手动：启动 XR 服务（`service.start`）、检查有线连接(adb)、结束检查、预检、执行、确认交接对话框，共 6 次以上点击，且分散在 2–3 个页面。
- supervisor 规则：`current.running and mode != preview → "已有遥操任务运行"`，导致 input 模式运行时点预检会被拒绝，操作员需要知道先点"结束检查"。
- 参考版（robot_capture_franka `ui_teleop.py`）是单按钮"启动控制服务"+分阶段进度对话框（环境检查 → 启动 PC 服务 → 等待 Pico → 连接机械臂），然后长按菜单使能。目标形态应与之对齐并由 adapter 提供各构型差异阶段。

### 1.3 显示未与机型绑定（MVVM 缺失）
- `app/static/js/arm_viewer.mjs` 默认 `URDF_URL = piper_description.urdf`，首次 `makeViewer` 固定 piper，只有收到带 `robot_type` 的状态才重建 viewer；页面构建时不知道当前机型，所以首帧/无数据时就是 Piper 模型。
- 采集页机械臂预览固定渲染 `left/right` 两个 pane（`ui_record.py:781`），不读取 `controlled_arms`；Franka 单臂模式仍显示两臂；回放页同理。
- 文案适配靠字符串替换 `translator()`（CAN→FCI 等，`app/ui/franka.py:9`），不是数据驱动。
- 状态字段仍是 Piper 语义（`left_can/right_can/can_states`），Franka 用 `FrankaArmManager.can_states()` 伪装成 CAN UP/DOWN。

### 1.4 检测项冗余
- 遥操页 Franka：检查手柄 / 检查 FCI 反馈 / 运控预检 / 结束检查 / 重新标定 / 暂停 / 保存复位姿态 / 返回复位 / 保持并结束。其中前四项应内聚进一键启动的自动阶段；标定由右摇杆触发，页面入口可保留在"高级"折叠区。
- 设置页"检测当前机型硬件"与设备页"检测 Franka 硬件"重复；Franka 诊断里 ping/串口权限等应在启动阶段自动执行并只在失败时提示。

### 1.5 A+X 复位后 "VR 数据超时/停止读取，VR 锁定"（已定位根因，待真机确认）
- `robot/franka/adapter.py::_reset` 调 `controller.gripper_close()/gripper_open()` → `GripperIO.exclusive()` 在持锁状态下执行阻塞的 Robotiq `close()/open()`（串口往返通常 >250ms）。
- 期间 `GripperIO._run` 无法更新 `updated_at`；worker 主循环 `tick → adapter.feedback → controller.feedback` 判定 `夹爪反馈超过 250ms 未更新` 抛错 → `worker.error` 置位并 `hold()` → `hold()` 对正在复位的流程 `reset_cancel.set()`。
- runtime 下一次 heartbeat 收到 `error` → `raise RuntimeError` 退出/或 Authority 失去 VR；UI 表现为 VR 超时并锁定、复位被取消。
- 参考版在复位期间 `_gripper_runner.stop()`，且无 250ms 夹爪新鲜度判定，所以无此问题。
- 修复方向（归属 Franka adapter）：复位期间暂停夹爪新鲜度判定（或用 `reset_running` 旁路），夹爪阻塞操作不在持锁下长时间阻塞 feedback；worker `hold()` 在复位进行中不应因夹爪新鲜度误判而取消复位。

## 2. 目标形态（建议）

1. 导航收敛为：采集（含遥操作状态与一键启动）、回放、统计、事件、设置。删除独立"设备""遥操设置"页。
2. 设置页单页分区：机型与左右臂选择 → 该机型连接参数（由 adapter 描述驱动：IP/串口 或 CAN 或 ROS2）→ 相机绑定 → 存储/上传 → 高级（复位姿态保存、手动标定、诊断）。
3. 一键启动（采集页一个按钮 + 阶段进度）：`XR 服务 → 头显有线/adb → 机械臂连接(adapter) → 输入与反馈就绪(自动预检) → 进入执行(需一次安全确认) → 提示长按菜单使能`。各阶段由公共 `StartupOrchestrator` 驱动，机型差异由 `RobotAdapter.startup_stages()` 提供；失败即停并给出单条可执行提示。
4. 显示绑定：后端提供 `robot_view_model`（机型、URDF 资源 URL、选中臂、传输类型文案、关节数），采集/回放/遥操视图订阅该模型；viewer 以机型初始化而非默认 Piper；pane 数量按选中臂。
5. 删除/折叠冗余检测；保留自动阶段失败时的诊断输出。
6. 先修 A+X 复位夹爪新鲜度缺陷（安全相关），再做启动编排，再做设置合并与显示绑定。

## 3. 需用户决策
- 一键启动中"进入执行"是否保留一次确认（控制权交接/区域清空）？建议保留一次。
- 是否将 Piper/ARX 的 CAN 专属 UI 也迁移为 adapter 描述驱动（范围变大但一致）？
- 设备页、遥操设置页是否直接删除（而非隐藏）？
