# Franka FR3：整臂与 Reset 移动抖动——外部诊断咨询材料

> 现象更正（2026-10-18）：操作者明确撤回“J7最明显、J1–J6平滑”的描述，确认是整个机械臂抖动。此前的关节选择性结论无效，不得再作为诊断前提。文件名保留仅为兼容已有链接，不代表J7定位结论。

日期：2026-10-18。用途：可直接提交给 GPT 或控制工程专家。本文只整理问题，不授权自动修改参数或操作硬件。

证据标签：**确认·用户**=操作者描述；**确认·源码**=已定位代码行为；**确认·离线**=已执行的数据分析或配置检查；**假设**=尚未证明的机制；**未知**=缺少证据；**需要帮助**=希望专家回答。

## 1. 目标与精确问题

我们用 RLinf + Franky/libfranka 控制单臂 Franka Research 3，Pico 遥操作。希望定位并解决整个机械臂的抖动，而不是继续盲目调大刚度或放宽限制。

**确认·用户（最新反馈及更正）：**已经多次调整“力矩参数”（涉及误差 clip 等）和 motion/action scale。恢复力较小时，跟踪迟钝，Roll 仍轻微抖；恢复力大一点，Roll 抖动更明显，末端有时感觉乱飘。启动归位和采集结束后的 Reset，在移动过程中也会抖，Roll 成分明显时尤其突出。抖动涉及整个机械臂，不再声称某个关节最突出或其他关节平滑。尚无抖动频率的高频测量。

**用户判断：**问题不在 Pico 输入，应该在控制侧。

**证据边界：**Reset 不依赖 Pico 生成目标，因此 Pico 输入不是抖动出现的必要条件；但 Reset 仍经过 FrankaEnv 的轨迹生成、Ray/驱动与 Franky 控制，不能据此排除整个环境链路，也不能直接认定某一控制公式有错。

**需要帮助：**请基于后面的真实实现和数据，提出可证伪、按优先级排序的根因假设。重点解释整臂抖动、Roll场景的表现，以及为何低恢复力迟钝、高恢复力更抖。不以关节选择性为前提。给出最小诊断实验及必须采集的信号，不要只给通用调参建议。

## 2. 系统背景与控制链路

**确认·项目记录：**FR3，系统镜像5.10.0；Ubuntu22.04.5 PREEMPT_RT；Python3.11，使用 RLinf/.venv；无 ROS，Franky 直连 libfranka0.19.0。末端安装 Robotiq 夹爪及腕部相机，另有外部相机。夹爪走 USB-RS485，图像走 UVC/OpenCV。无 NVIDIA GPU，当前仅采集。

**未知：**当前精确负载/惯量、质心、工具重力补偿是否标定正确，实际 EE/K 坐标系配置、固件状态、实时循环成功率与周期抖动。项目平台记录不是本轮新硬件检测。

### 遥操作目标路径（确认·源码）

```text
Pico transport（grip边沿建立参考，坐标重映射）
→ PicoDelta（grip相对旋转 rotvec + 机器人anchor）
→ 相对实测姿态构造动作、rotvec→Euler增量表达
→ FrankaEnv.step（当前TCP + 增量，姿态窗口裁剪）
→ _move_action（clear_errors + 发送绝对tcp_pose）
→ Ray/robot arm dispatch
→ FrankyArm.move_tcp_pose（相对上一命令目标做单步限幅）
→ CartesianImpedanceTracker.set_target(Affine)
→ C++笛卡尔阻抗力矩控制
```

TCP 表示为基座系 `[x,y,z,qx,qy,qz,qw]`。不是7关节 action；采集中的七关节 q/dq 是实测状态，不能当作目标关节轨迹。没有我们显式调用的在线 IK 来产生逐步 q_target。

## 3. 预期与实际表现

| 项目 | 预期 | 实际及证据等级 |
|---|---|---|
| 手柄Roll | TCP平顺转动，关节无明显跳动 | 用户更正确认为整个机械臂抖动，无有效的关节突出性排序 |
| 启动归位 | 从当前位姿平顺到reset | 用户确认移动中抖，不是单纯到位后保持抖 |
| episode结束归位 | 同上 | 用户确认也抖 |
| 缩小恢复力 | 减少振荡且仍可跟踪 | 用户反馈明显迟钝，但轻微抖仍存在 |
| 增大恢复力 | 提升跟踪 | 用户反馈Roll更抖，末端偶尔乱飘 |

“乱飘”的方向、幅度、是否为旋转耦合平移、是否伴随接触/告警未量化。不同参数试验没有完整统一的运行目录绑定，不能做严格因果统计。

## 4. 复现路径与现有证据

### 4.1 两类 Reset 必须分开（确认·源码）

**A. 构造/首次启动归位：**FrankaEnv构造时连接硬件，直接调用 `_interpolate_move(reset_pose)`，然后等1秒。此时尚未应用环境运行时 compliance_param。启动刚度通常 Kt=1000、Kr=50、Kns=5，平移clip=.008，旋转clip=.04。采集包装器和正常episode记录尚未完整建立，所以普通pickle不保证记录这段归位过程。

**B. episode Reset：**collector在done后调用env.reset；FrankaEnv先应用运行时compliance，随后go_to_rest。一般不做关节复位；默认每20000次reset才进入周期性JointMotion分支。普通reset使用笛卡尔插值。

两类运动共享插值实现：

```python
N = int(1.5 * step_frequency)  # 默认10Hz，N=15
current_pose = read_robot().tcp_pose
positions = linspace(current_xyz, target_xyz, N + 1)
orientations = quat_slerp(current_quat, target_quat, N + 1)
for p, q in zip(positions[1:], orientations[1:]):
    move_action(concatenate(p, q).astype(float32))
    sleep(0.1)
read_robot()
```

- 15个发送目标，不是单点立即下发；位置线性、四元数短弧SLERP。
- 1.5秒只是sleep总和，RPC、clear_errors、调度等耗时另加；未测本次Reset实际频率。
- 不随总位移/转角调整时间；没有起止速度/加速度渐变。
- 循环内不逐点等到位，也不逐点读取状态重规划。
- Reset绕过普通step的action_scale和环境工作空间clip，但保留Franky目标步进guard。
- episode的go_to_rest只比较xyz，不比较姿态；`np.allclose(xyz, target_xyz, 0.02)`的第三个参数是rtol，不是2cm绝对距离。
- 最多尝试3遍插值，未到位也会退出该循环，不因这件事单独抛异常。
- clip改变会停止原tracker，下次命令重建；clip不变时通常复用tracker。每次重建会重新采样零空间q参考。

源码定位：`RLinf/examples/embodiment/collect_real_data.py` done→reset；`RLinf/rlinf/envs/real/franka/base.py` 构造、reset、go_to_rest、_interpolate_move、_move_action；`RLinf/rlinf/envs/real/utils/pose.py` quat_slerp。

### 4.2 已分析的遥操作记录（确认·离线，历史数据，不是最新参数试验）

文件：`RLinf/logs/20261016-183601-realworld_collect_data_pico_single_franka/collected_data/rank_0_env_0_episode_1_step_959_success.pkl`

SHA256：`d6dea8f5c7fc15120929d1e4add719226c4a50a38f540a880f75d2fc50f15dcc`

- 47次transition，48个observation/info；首末下发时间跨度6.422秒。
- 下发间隔中位135.602ms，约7.375Hz；范围124.374～173.862ms。不是C++伺服周期。
- q/dq均有限，未发现NaN/Inf。

| 关节 | 实测位置范围° | 首末差° | 采样峰值绝对dq，°/s |
|---|---:|---:|---:|
| J1 | 8.771～10.003 | −1.200 | 2.160 |
| J2 | 7.105～11.699 | +4.357 | 10.458 |
| J3 | −9.674～−6.813 | +1.041 | 4.391 |
| J4 | −119.605～−112.883 | +6.676 | 7.812 |
| J5 | 2.771～9.881 | −5.379 | 24.278 |
| J6 | 120.492～130.139 | −1.592 | 17.018 |
| J7 | −69.951～−21.557 | +6.760 | 45.637 |

上述数值仅为历史低频采样的运动范围和速度，不是各关节振动幅值或频率。J7的运动跨度较大不能证明它抖得更明显，也不能证明J1–J6平滑。撤回由此产生的关节选择性推断；后续必须同时检查七个关节与TCP。

记录的TCP请求相邻姿态变化最大13.714°，换向附近连续11.81°/13.71°；这是**驱动guard之前的请求**，不是已经证明的C++最终参考。最大请求位置步长约15.2mm。

采集质量工具因缺少日志中的grip事件，无法完成窗口匹配而返回失败；不应把整个批次称为全部质检通过。此限制不否定上述可读取q/dq数值，但限制轨迹语义验证。

### 4.3 独立短程运动脚本（不是原始Reset复现）

`杂项/franka_target_diagnostic.py`：关节7 +10°返回，或基座系纯Roll ±10°并返回。使用同类Franky控制器，但采用五次平滑目标轨迹、标称10Hz，不是原始Reset的15点恒步插值。

已记录结果：
- Roll1°/s两次在终点等待2秒后姿态误差约1.71°、1.99°，旧1°检查触发中止；最大误差约2.45°、2.60°。
- Roll5°/s某次在运动中误差持续上升，最后已记录约2.69°，下一步发送前3°检查中止。
- 后来经授权把笛卡尔运动诊断阈值改为5°、端点3°，不是修改硬件安全阈值；此后没有完整成功对照结果可引用。
- **未知：**关节7直接控制是否明确平稳而Cartesian Roll抖，尚无可定位的操作者对照结论。

另一次报错：
```text
libfranka: Move command rejected: command not possible in the current mode ("User stopped")!
```
它表示机器人当时不接受运动；不是抖动根因证据，不能归咎于滤波或速度。软件tracker started日志不保证异步控制已被机器人接受。

## 5. 控制器、环境、参数及约束

### 5.1 Franky真实实现（确认·源码，二进制关联有边界）

使用Brunch-Life/franky发布的libfranka0.19.0 wheel（项目此前记录包为franky_control1.1.3）。源码审计关联提交：`7bdb567df879a771c3095fb5815a8324c94f2ce6`。此前已核对安装extension/tracker与release wheel字节相同；源码对应关系来自构建历史，不是可复现编译的密码学证明。不能直接拿release tag所指另一个master提交当作wheel源码。

核心行为：
- tracker收到新的pose后直接替换reference；没有连续pose插值。`gains_time_constant=.1`是增益平滑，不是姿态平滑。
- 驱动只传pose，没有twist前馈；C++目标twist默认为0。
- 姿态误差是误差四元数的向量部分并变换到基座系，不是rotvec。
- 纯轴角度误差θ对应模长sin(θ/2)。因此Kr的数值不能直接等同于按θ定义的角刚度；小角度下恢复系数约Kr/2。

简化公式（完整符号、坐标约定见附件源码）：
```text
wrench = -K * clipped_error - D * (J*dq - desired_twist)
tau_task = J^T * wrench
D_t = 2*sqrt(K_t), D_r = 2*sqrt(K_r)
P = I - J^T * pinv(J^T)
tau_ns = P * (K_ns*(q_ref-q) - 2*sqrt(K_ns)*dq)
tau = task + nullspace + optional joint-limit terms + Coriolis
then torque-rate saturation
```

q_ref在tracker创建时采样，生命周期内固定；P随J变化。伪逆SVD硬阈值1e-6，不是阻尼最小二乘。不能因为有伪逆就认定奇异性：任务力矩本身用J转置。

笛卡尔tracker没有独立阻尼调节接口；RLinf配置中的damping=89/7和Ki当前不被这条驱动重配置路径使用。改变K会同时改变D，2sqrt(K)不保证真实构型/负载下临界阻尼。关节阻抗可调阻尼是另一条接口。

### 5.2 当前磁盘参数快照（2026-10-18本次读取）

**重要：已经不同于此前52cdf9a及官方对照组合。** 本文不修改现场参数；不能把当前文件值套到历史日志。注释仍有旧值，应以字段值为准。

| 参数 | 当前磁盘值 | 驱动规则下预计生效/意义 |
|---|---|---|
| hardware.max_step | .2 m | 每次目标位移guard，不是速度 |
| hardware.max_step_rad | .5 rad | 每次目标旋转guard，不是速度 |
| action_scale | [.2,.5,1] | 普通step使用，Reset不使用 |
| 请求Kt/Kr | 2000 / 60 | cap后1200 / 60 |
| 平移正向clip | [.01,.015,.015] | 正负取较大值后[.015,.015,.015] |
| 平移负向clip | [.015,.015,.015] | 同上，对称 |
| 旋转正负clip | [.1,.1,.1] | 四元数误差分量clip |
| nullspace stiffness | 默认5 | 需要运行日志确认 |
| stiffness caps | 默认1200 / 80 | RLinf驱动限制，不是硬件物理极限 |
| clip floors | 平移.005 / 旋转.02 | 不能靠写更小值突破 |
| max_delta_tau / gains_time_constant | 默认.3 / .1 | 分别是力矩变化限制、增益平滑 |

当前reset配置为 `[.492223,.054966,.282786,-3.068279,.011725,-.171270]`（xyz米、Euler xyz弧度）。这不是跨设备可照搬的安全位姿。配置位置盒近乎±2m，不能把它当作有效局部扫掠空间保护。

当前磁盘值的实际Worker生效日志未在本轮绑定；初始化归位仍使用另一组默认刚度/clip。不要仅凭这张表声称最新试验已使用上述全部值。

### 5.3 官方示例与本项目版本

核对过RLinf基线`50f22ad`的单臂Pico/PegInsertion示例：
- 请求Kt2000、Kr150，驱动实际cap为1200/80。
- 平移请求±[.003,.003,.01]，floor后[.005,.005,.01]。
- 旋转请求/生效±[.02,.02,.02]。
- action_scale [.02,.1,1]，默认目标guards .03m/.10rad。
- 示例是PegInsertion任务，包含不同工作区/随机reset/夹爪动作，不能整体切换照搬。

本地RLinf HEAD为79a647e；曾将工作树恢复为52cdf9a内容，但之后有现场参数修改，**当前不能称作纯52cdf9a**。test1.0已回滚。当前无滤波实验在活动代码中。

### 5.4 证据局限与操作约束

- Python/Ray下发节奏不等于libfranka实时回调节奏；高频控制周期、丢包、success_rate尚未测量。
- `final_franka_target`历史字段实际上在驱动guard前采样，不保证是成功提交的最终目标。
- passive pre-command q是缓存状态，不保证是命令发送瞬间新测量；host读取时间不是传感器采样时间。
- 低频pickle不能恢复高频振动，也不能靠它证明没有振动。
- 不关闭/提高Desk SLS-C/SLP-C、碰撞保护，不把力矩变化率限制当作普通输入滤波随意去掉。
- 仅操作者启动真机试验；不自动重试或绕过User stopped；异常时不自动返程。

## 6. 已尝试事项与结果

1. **动作scale、target步进guard、刚度/误差clip多次调整**：用户报告未解决；恢复力小迟钝，恢复力大抖动明显。每次全套实际参数、初始构型和数据未完全绑定，因此不能声称已经排除某一参数机制。
2. **test1.0 Pico姿态低通**：默认关闭的SO(3)输入滤波，tau=.20s，松grip清历史；仅作用PicoDelta输入，无高频reference插值。用户报告失败，已完全回滚，保留历史归档。无法据此否定控制器内部reference插值或高频轨迹整形；不是同一实验。
3. **回退52cdf9a**：曾验证tracked工作树一致，随后继续现场参数试验；不是当前文件的最终描述。
4. **官方刚度/clip对照**：仅运行时compliance请求值对齐，未换任务。离线解析验证1200/80及较小clip。用户最新仍反馈无解决；精确试验日志、当时完整参数未知。
5. **独立roll/joint7脚本**：见4.3；证明存在跟踪误差记录，尚无同起点、同负载、同速度条件下两控制模式的完整对照。
6. **源码审计**：发现reference直接替换、自动阻尼、固定nullspace参考等具体机制；这些是待检验的解释，不是已确认bug。

离线测试/独立静态review验证过部分代码路径，但独立受控测试runner缺失。Fake SDK测试、静态审计和配置解析都不能证明真机稳定。

## 7. 未知项、候选假设与请求专家回答

### 候选机制（全部是假设）

1. 低频阶梯reference加零目标速度阻尼，激发构型相关的整臂动态；Reset的固定15点、无加减速可能同样激励该机制。
2. 笛卡尔姿态阻抗阻尼与有效惯量/四元数误差定义不匹配；单纯增大K改变了K/D关系但未保证阻尼比。
3. 笛卡尔任务力矩与固定q_ref零空间力矩发生耦合，投影随姿态变化；需要七关节力矩分解证明，不能预设J7是主要来源。
4. 负载/重心/EE/K设置不准确，特别是腕部附件重力与惯量；较小clip跟踪困难可能与此有关，但当前未验证。
5. 实时网络/调度、控制周期抖动、力矩速率饱和等非线性影响；尚无高频证据。
6. 姿态表示、控制参考系或实现错误；Reset使用SLERP仍抖，不能只归因Pico的Euler转换，需检查共享的后端控制路径。

### 请按以下格式回答

1. 针对上述实现给出最可能的3–5个机制，说明每项如何解释“整臂抖动、Reset也抖、增大恢复力更抖”。明确置信度与反证，不使用已撤回的J7突出结论。
2. 你认为代码中哪些行为是正常设计、哪些值得怀疑？重点审查四元数误差比例、2sqrt(K)阻尼、零twist、固定nullspace、逐点clear_errors、reference步进。
3. 下一个最小诊断实验应该是什么？只改变一个变量，明确保留哪些配置/初始q/工具负载，记录什么，何种结果支持或否定假设。
4. 若需高频数据，请列出必要信号及采样位置：真正消费的reference、q/dq、TCP/twist、J、q_ref、各项力矩、tau_J_d/实测力矩、裁剪/速率饱和标志、控制周期和success_rate。区分必须项和可选项，并避免在实时回调阻塞写盘。
5. 对比改阻尼、姿态连续插值/速度前馈、nullspace处理、负载校准，各自前提与风险。不要未经证据建议提高刚度上限或关闭保护。
6. 给出停止条件与验证标准；什么证据足以声称问题已解决，而不是仅仅慢到看不出抖动？

### 可提供的补充源码/材料（项目相对路径）

- `RLinf/rlinf/robotics/parts/arms/franky.py`：连接、参数解析、tracker、guard和send路径。
- `RLinf/rlinf/robotics/parts/arms/base.py`：compliance默认及上限。
- `RLinf/rlinf/envs/real/franka/base.py`：Reset和普通step。
- `RLinf/rlinf/envs/real/utils/pose.py`：SLERP与窗口转换。
- `RLinf/rlinf/robotics/parts/teleop/pico.py`：PicoDelta。
- `.project-log/docs/franky-release-audit/cartesian_impedance_base.cpp`。
- `.project-log/docs/franky-release-audit/cartesian_impedance_tracking_motion.cpp`。
- `.project-log/docs/franky-release-audit/README.md`：wheel与源码关联证据。
- `RLinf-Franks/rlinf_ext/collection.py`：遥测边界与字段真实含义。
- `TELEOP_TUNING_LOG.md`：历史参数台账；不是当前配置替代品。
- `.project-log/docs/archive/test1.0-rollback-20261018/`：失败滤波实验。

本文未包含访问凭证、API密钥、机器人网络地址或个人账号。若需要进一步分析，先提供上述必要源码与脱敏日志，不应凭本文缺失项猜测实现。
