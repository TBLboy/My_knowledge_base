# Franka 控制语义核对（2026-10-30，进行中）

参考为用户确认稳定的 robot_capture_franka 当前本地文件（含既有未提交修改，只读）；目标为 unified_vr_teleop_franka/Dagger_web 清理后版本。仅核对控制，不改录制格式。

## 第一轮结论

- 底层驱动：17 文件归一化 import 后 15 个 AST 相同；Pico、Robotiq 不同。不能由驱动复用推断整链等价。
- Grip 数学：参考 release_backend.py:200,544 与目标 robot/franka/motion.py:21-50 均使用固定实测锚点加累计位移、旋转左乘、固定欧拉窗口；待做数值交叉验证。
- 输入：参考发布器/ZMQ → PicoExpert；目标 RecoveringInput → PoseClutch → PicoExpert 数学，接收/时效并不相同。
- 按键：参考 rig.py:53-59 使用左菜单、右摇杆配对校准、左摇杆开始；目标 runtime.py:81-112 使用所选任一菜单，未传摇杆按键，A 残留接管逻辑，B 保持，左单臂 X 改 A。操作不等价。
- 主动标定：参考 coordinator.py:73-111 验证双方快照并原子应用；目标 motion.py:11-12 禁用 calibration button，未接主动入口。
- 保存复位姿态：参考 coordinator.py:183-219 配对校验并原子保存；目标 worker.py:143-156 仅读 YAML 固定值，无保存入口。
- 复位：参考 release_backend.py:327-368 按配置时长插值、先闭夹爪后开、恢复原循环并要求 Grip 重握；目标 worker.py:68-83,143-156 按距离/角差定时、保持夹爪开度、实测到位判定，runtime.py:113-135 完成后锁定。实质不同。
- Grip 松开：参考 release_backend.py:568-573 不再生产目标/清锚点；目标 runtime.py:148-152 调 hold，经 controller.py:85-92 停止 tracker 并夹爪保持。不能擅自去掉目标版保护。
- 目标版另有 200ms 目标 watchdog、500ms 租约、250ms 反馈检查（worker.py:58-90），恢复语义待核对。
- 夹爪：参考 release_backend.py:26-119 阈值 2mm、读取周期100ms，错误后继续尝试；目标 gripper.py:33-45 阈值0.5mm、20ms等待加I/O、错误后退出。
- 清理回归：目标 runtime X/Y 只锁定 authority，RecordingSession.start 不启动消费线程，真实按键录制事件未贯通。直接调用 handle 的测试通过不能证明此链路正常，后续需修复并验证。
- 工位复位姿态此前左侧 Z 相差约16cm；核对现场配置前禁止自动复制。

## 验证

- 当前 Franka + partial-signals 离线测试 28 passed；不是跨版本等价验证。
- AST 比较15 same / 2 diff；未启动设备，未修改参考工程或业务代码。
- 待完成：输入字段/发布器、参数和退出恢复全链核对、数学数值交叉验证。

## 待确认方向

建议恢复参考版操作语义，同时保留目标版新增超时/租约保护；标定值、复位夹爪行为及重启恢复等安全/操作差异需用户确认后实施。

## 第二轮核对与数值验证

### 已验证一致的部分

- 使用参考 PicoExpert（禁用其 start，不连接 ZMQ）和参考 `_compose_target` 方法，与目标 PoseClutch 对比；随机种子42，双侧各300帧，每25帧释放Grip，包含随机平移/旋转与扳机：576个有效目标一致，最大位姿数值误差约 `1.43e-15`。只证明相同输入/配置/锚点下数学一致，不证明真实接收和标定事件等价。
- `config/franka-worker.json` 的 compliance 8项参数与目标 YAML 全部相同；控制频率均30Hz；底层 FrankyArm AST 相同。
- 合并参考 rig 每侧覆盖后，左右工作空间、朝向中心、IP和串口与目标一致；右臂复位姿态一致。左臂目标版相对参考版 XYZ 增量为 `[0.0055880, 0.0042395, 0.1598462]m`，约16cm高差仍存在。

### 输入与检查差异

- 参考发布器 `pico_bridge/vr_data_publisher.py:101-152` 显式发送双手、头显、8个按键（含两摇杆按下）；目标 SDK snapshot `robot/xr/vendor/.../py_bindings.cpp:527-541` 只有 pose/grip/trigger/primary/secondary/menu/stamp/age。SDK虽提供 axis_click 独立函数，但 receiver未读取，所以两摇杆功能确实断链，不只是页面未显示。
- 目标 receiver.py:56-57 用单调接收年龄与时间戳推进判断150ms新鲜度；参考 PicoExpert快照按ZMQ接收墙钟年龄250ms判定。目标更严格，参考发布器本地继续发旧厂商数据的情况不能由接收年龄单独识别；这是安全实现差异，不建议机械回退。
- 目标只按所选手柄构建菜单与按键；左单臂时右摇杆、右侧A组合本身不可达。参考 rig 的绝对按键即使单臂仍可由双手发布器提供。
- 参考 preflight要求有效已标定输入、松Grip（release_backend.py:290-309）；目标 runtime.py:74只检查fresh与Grip，在实际生成目标时才检查头显标定。这意味着目标版可以预检通过但执行后才暴露头显位姿问题。
- 目标PoseClutch用默认位移/旋转比例1和Grip阈值0.9，与当前参考配置一致，但未从机器人config读取这些Pico参数，后续配置变化会失配。

### 退出、错误与完成确认差异

- 参考 RigBackend.exit→hold（coordinator.py:141-142），ReleaseBackend.exit也是hold；不是返回复位姿态。目标 Web关闭VR调用finish（capture_workflow.py:102-107），manager.close先reset_and_close_control，再停XR（integration.py:381起），会额外运动。这是重大操作语义差异，不能称为相同。
- 目标 runtime.py:129-135 对任何非空reset_result均将reset_exit_complete置为finish_after_reset，不再次检查reached；当前worker成功才生成result，故暂依赖隐含契约。跨层完成确认必须显式验证，后续适配时不得把“有结果”当“到位”。
- 目标 RecordingSession 的延迟结束逻辑缺少旧结果ID、控制进程identity、事件年龄及错误/取消/超时绑定。复位完成时可能误用旧成功结果，或复位失败后一直等待；参考旧完整流程有相应保护。它目前也没有真实事件消费线程，修复应一起补齐，不能只恢复线程。
- 目标 runtime无效单侧输入时按全部所选手柄fresh整体锁定；参考各侧后端独立循环，输入故障会在该侧标error，不等于目标双臂统一保持。配对故障策略需要明确。
- 目标 hold显式停止tracker；参考hold仅停Python生产循环、刷新样本，直到disconnect才释放底层。不能在未真机验证时宣称两者物理制动效果相同。

### 结论

Franka核心坐标数学和驱动控制参数可复用，但当前平台尚未与稳定参考版完成操作/生命周期语义对齐。安全watchdog、tracker停止和时效机制应单列保留/验证，不以“完全复制参考”为由去除。第一任务继续；第二任务不得提前开始。
