# Progress

> 面向人的阶段进度摘要。维护规则：
> - **最新在最上**：按日期倒序排列，最新阶段段落位于文件顶部，旧段落依次向下。
> - **头部快照**：顶部“当前状态”区块是稳定入口，每次更新时覆盖，不追加旧版本。
> - **超限归档**：文件超过约 50-100 KB 时，把旧段落移动到 `.project-log/docs/archive/`，主文档只保留最近内容。
> - **单一事实源**：本文件是快速摘要；精确当前状态与下一步以状态库、Git 账本与生成的 `handoff.md` 为准。
> - **机器文件不手工重排**：状态库与生成视图由运行时维护，不做手工重排或改写。

## 当前状态

- **IK目标纠偏（D-041）**：用户明确任务是平顺可用的遥操作、解决整臂抖动，不追求零跟踪误差；撤回未获批准的“误差超阈值暂停并重新握持”建议，不新增该门禁。普通跟踪残差仅记录观察；保留现有grip/硬件保护及已批准IK失败不发布策略。离线IK501点全部成功，10项主Agent测试通过，尚未真机。下一步聚焦隔离TCP→连续IK→关节阻抗接通，不把精度扩展成新的阻塞需求。

- **连续IK策略已批准，离线原型开始**：用户同意从实测q初始化、后续以前一有效解求局部连续解；失败/不可达/超时不发布新目标、不积压旧命令。D-040记录；后台实现仅离线model/Jacobian原型，不连接机器人、不改正式遥操作。FK已获静态复核，可作为离线基础但不代表物理精度；数值/限速/超时阈值仍是待验收候选。下一步报告A…E轨迹误差、关节连续性、失败与耗时。

- **主线切换：暂停笛卡尔排查，开始连续IK→关节阻抗（2026-10-18）**：用户明确批准，旧路线未解决/未完成，停止继续其调参与真机诊断；历史下面“下一步”仅作暂停前计划。暂停点及新范围见 docs/requirements/ik-joint-route-start-20261018.md，D-039/T-026。新路线先离线模型/IK只读盘点，再验证连续性/限位/误差/异常契约；不替换正式遥操作，不自动真机。独立进行的T-025 v3活动Run不被本次取消或覆盖。精确下一步：查清FR3模型与TCP匹配、现成IK和离线验证资源后给建议。

- **READ-010负载/坐标系实读**：经用户授权原生只读探针exit0，无运动/恢复/设置写入。Idle、errors=[]；工具m_ee=1kg、附加载荷0、总质心法兰[.05,0,.057]m、TCP法兰z+.16m，NE_T_EE/EE_T_K单位阵。快照在reset_lab/evidence/control-state-20261018.json；success_rate0是在Idle不能推断运动丢包。下一步核实这些配置是否对应实际夹爪/支架/相机，不能据此声称负载错或根因已定。实验台账已更新。

- **RESET009失败：前馈加重整臂抖动**：用户反馈更抖；cartesian-ff-1792305362日志45send/3return后User Stop pressed中止，未完成路线，无自动返程。台账已更新，停止推荐前馈（原默认OFF不变），不自动恢复停止状态。下一步暂停盲目运动调参，先只读核对负载/坐标系及控制器实际阻尼/零空间/时序证据；未改参数或操作硬件。

- **RESET009解析笛卡尔速度前馈已实现**：compare入口新增--velocity-feedforward默认关闭；解析基座线/角速度，非加速度，限幅不一致拒绝、端点零twist，参数/保护不升高。主Agent93项离线测试及无Robot的已安装native引用发布调用通过；独立静态无阻塞，runner缺失。用户报告RESET008仍严重整臂抖，非日志归因。当前无真机前馈结果；下一步操作者小范围同条件对照，注意名义速度与实际时序差异。

- **RESET-008笛卡尔流程对照已实现**：execute_cartesian_compare.py默认1.5s/10Hz，单遍、不重试、延续前次postguard提交参考；原Cartesian参数/无twist不变。主Agent88项离线测试通过，独立静态复核无阻塞、runner缺失，尚未真机。RESET007用户报告快速平稳，但日志各段最大关节误差3–6°级，不能当作准确到位。台账已更新；下一步操作者RESET008并保留日志，无自动硬件动作。

- **RESET-006用户反馈平稳；RESET-007已实现**：关节默认改为original线性/1.5秒/10Hz、15点+零速端点保持，quintic8/50仍可显式调用。段间命令连续，关节原控制参数不动；前馈/力矩变化率/无笛卡尔重试等差异仍在，不声称唯一变量。主Agent82项离线测试通过；独立静态审查行为接受，要求的前馈标签/拒绝超速测试已修，runner缺失。未执行新模式真机。下一步操作者原始节奏关节对照并保留日志。

- **RESET-006关节阻抗对照已实现**：execute_joint_reset.py独立入口，实测q点位、quintic8秒/50Hz、A…E…A、停2秒。段间延续提交目标，解析dq前馈及零速端点保持；不同于原有限差分关节路径，不声称单一控制律对照。主Agent76项离线测试通过、独立静态复核接受，runner缺失；尚未真机。关节路径扫掠不同、现有大跨度点需现场核验。正式环境/笛卡尔脚本未变；下一步操作者小范围对照记录。

- **RESET-005结果：未改善**：用户报告移动仍有整臂震动；quintic8-hz50-1792301730日志实际目标频率约45.01Hz（此前9.81），4800send/6次Reset返回无abort；参数一致，A/D/最终A仍未位置到位。台账已更新；并非严格相同实际时长，不排除全部目标效应，但不再优先盲升频。下一步只读核验负载/EE/K和实时指标，再选择控制层单变量对照；未修改控制。

- **RESET-005已实现待操作者试验**：用户确认移动明显抖、固定停留基本不抖；授权单变量10→50Hz目标更新对照。隔离执行器新增--target-hz10/50（默认10），quintic8/50为400点，阻抗及native不动，停留仍10Hz。主Agent62项离线测试通过，独立静态接受但runner缺失；尚未真机。实际下发间隔需看日志，send后sleep仍叠加开销。试验已执行，结果见顶部RESET-005更新，不再视为待执行。

- **停留试验已分析（RESET-004）**：quintic8-dwell-1792300820日志6次Reset返回、无abort，A/D/最终A仍未满足位置条件；四段停留各20点、目标不变且机器人时间递增。A/B/D采样较安静，C主要继续收敛；10Hz不能排除高频振动。台账已更新。下一步确认用户停留时视觉观察，再定单变量实验；未改控制/未操作硬件。

- **停留期遥测已实现**：--record-dwell默认关闭，在既有中间2秒/启动1秒等待内只读采样、增加插值/重试标记；不新增目标/等待，不改参数。主Agent58项离线测试通过，独立静态复核无阻塞、runner缺失。未真机；下一步操作者重新运行quintic8 force并带record-dwell，分析固定目标下整臂响应。状态缓存新鲜度与实时性尚未证实。

- **Reset实验台账与平滑试验结果（2026-10-18）**：已建立杂项/reset_lab/EXPERIMENT_LOG.md。用户确认quintic仍很抖；日志quintic8-1792299672为episode/force/8s80点，A..E返回后最终返A期间人工中止，A/D三遍后位置未满足原条件；不记为完整成功。原1.5s两份日志核对，original8对照未找到。结论仅该方案未解决整臂抖动；下一步离线分析时序/跟踪再选变量。没有调整控制或操作硬件。

- **T-021平滑Reset对照已实现**：默认original/1.5秒保持，新增--trajectory quintic、--duration 1.5–30秒，ceil到10Hz；参数/驱动不改。主Agent复跑51项离线测试通过，独立静态接受，runner缺失；未真机。杂项已初始化本地Git，忽略环境/vendor/build/points/evidence，尚未commit；修改前source-before.tar.gz在docs/parameter-trials/reset-smooth-baseline-20261018。后续quintic真机反馈见顶部实验台账记录；original8对照尚无证据。

- **Reset执行器免交互（2026-10-18）**：用户明确要求取消文字确认，已移除EXECUTE CLEAR/MOVE及TTY门禁；显式--execute在预检后自动连接并运动，无该开关仍preview。保留FCI1337占用、独占锁、隔离/新日志、异常停止不返程；运动逻辑参数未改。实现者45项离线测试通过，独立静态复核接受，runner缺失；未真机。此条取代旧交接中的二次确认要求。

- **T-020隔离Reset执行器已实现**：杂项/reset_lab/execute_reset.py，独立配置/控制/Python3.10/重建Franky，正式环境未改。主Agent复跑35项离线测试通过；独立静态复核接受（日志耗尽停止证据问题已修复），独立runner缺失。默认preview，episode/startup、可选强制插值、A…E…A、中间2秒、异常不返程。大跨度点位路径及实际停止未真机验证；须操作者阅读EXECUTOR.md并确认扫掠空间。无Ray/新tracker/额外读状态，非时间完全等价。下一步操作者小范围验证并保留日志。

- **独立Reset实验业务澄清**：用户确认两脚本（拖动模式只读回车采点TCP+q；文件顺序A→B→…→A），中间停2秒、最后直接返A结束，异常不返程。启动/episode两模式，默认episode，原样判断或可选强制插值。配置/控制代码/Python/Franky全隔离；日志含版本参数目标与实测状态。已记录RB-019和docs/requirements/reset-lab-v1.md；仅澄清未实现。下一步只读核验采点接口、隔离构建与Reset等价性，再出工程规格。

- **整份配置恢复52cdf9a（2026-10-18）**：用户要求恢复上个检查点配置；single_franka YAML已逐字恢复52cdf9a（blob faf3d971ef311f15ab4cbd0dcd05139b969d112b），包括旧reset及姿态窗口。备份 docs/parameter-trials/restore-52cdf9a-20261018/before.yaml。精确比较/YAML检查通过，独立静态值复核通过、runner缺失。无其他产品/数据修改，无硬件操作；旧咨询简报参数快照仅作历史。下一步操作者新会话加载，注意归位目标改变；整臂抖动未解决。

- **最高优先级现象更正（2026-10-18）**：用户明确指出是整个机械臂抖动，撤回“J7最明显、J1–J6平滑”的虚假描述。今后不得把J7选择性作为事实或根因排序依据；历史q/dq幅度仅为运动量，不是抖动强度。外部简报标题、现象、假设和问题已同步修正，保留旧文件名仅兼容链接。后续分析覆盖七关节与TCP。

- **外部诊断简报（2026-10-18）**：用户反馈小恢复力迟钝仍抖、大恢复力更抖且末端偶尔乱飘；启动和episode reset移动均抖。已保存 docs/franka-j7-reset-vibration-expert-brief-20261018.md，独立静态复核无实质错误；历史数值未独立重算。最新磁盘guards=.2/.5、action_scale=[.2,.5,1]、Kr请求60、旋转clip=.1，已不同于下方官方试验快照；未绑定最新Worker日志。仅整理文档，不改控制。下一步用户外部咨询后带回意见核验。

- **官方阻抗对照试验（2026-10-18）**：用户授权只改刚度与误差clip；请求2000/150，平移正负[.003,.003,.01]，旋转正负[.02]*3。离线实际驱动解析为1200/80、[.005,.005,.01]/[.02]*3，其他参数与修改前备份语义一致；保留现场已有修改，不假定仍完全等于52cdf9a。独立静态复核接受，runner缺失。备份 docs/parameter-trials/official-compliance-20261018/before.yaml；启动构造参数未变。下一步操作者新会话确认Worker日志，小范围测试，未做真机验证。

- **恢复52cdf9a（2026-10-18）**：用户指定回退；RLinf工作树已与52cdf9a逐文件一致（git diff exit0），仅max_step恢复0.08、action_scale恢复[0.04,0.3,1.0]。HEAD仍79a647e，未提交；Franks/数据不动。YAML检查通过，独立静态值复核通过，独立runner缺失。操作者新会话加载；不声称解决抖动。用户补充启动和episode reset移动均抖，复现需求尚在澄清。

- **test1.0已回滚（2026-10-18）**：用户报告实验失败并要求回滚。RLinf-Franks启动脚本与注册文件恢复到滤波前HEAD，4个实验文件移出活动代码并归档至 docs/archive/test1.0-rollback-20261018/。离线遥测回归7项通过，bash语法通过，独立静态复核通过；独立runner缺失。RLinf、杂项、采集数据未改；不再传 orientation-filter/tau 参数。未连接或停止硬件进程；已运行进程需操作者正常结束再启动以加载回滚代码。

- **T-016 独立运动诊断**：用户确认远离限位、场地清空且急停可达，按操作者本地实验开放显式 --execute（逐次同意、逐段确认）；保留限位/时序/误差/clip检查。18项实现者离线测试通过，独立静态复核可接受，独立runner缺失。默认1°/s、上限5°/s；正常返初始q、异常不返程。未连接硬件，物理停止/跟踪/扫掠空间未验证。下一步操作者本地分阶段试验并保留JSONL。

- **v3 业务基线（draft）**：`RB-015-franka-pico-raw-to-lerobot-v3` 已固化并关联 `BA-015`~`BA-023`；完整用户需求转录在 `.project-log/docs/requirements/lerobot-v3-semantic-format-v1.0.md`。因视频源/codec 与时间轴两项仍未定，基线 approval=pending，尚未进入实现。
- **采集/批次**：一次 `run_pico_session.sh` 从启动到操作者结束即一个无数量目标的 raw batch（timestamp run 目录）。`c=success`、计划新增 `f=failure` 均保存并仅提示累计/成功/失败数；`a=abort` 丢弃；timeout raw-only、默认不导出。每 batch 只有一个可为空的 task 文本；换 task 必须新开 batch。
- **后处理/导出**：采集只写 rich raw；离线处理选择一个 batch。模式为 strict `standard-success-only`、strict `standard-all`，以及带明确 outcome 扩展的 `labelled-all`；全部输出均不默认包含 timeout。
- **严格 v3 Franka profile**：state=实测 `joint_position[7]`、base-frame `eef_pose[7 xyzw]`、gripper；action=最终实际送入 Franky、guard/clip 后的 base-frame绝对 `eef_pose[7 xyzw]` + 独立 gripper，`custom.action_space=eef_pose_absolute`，无 `action.joint_position`。历史缺少最终 target/provenance 的 raw batch 不得伪造转换。
- **相机/模态**：ZED 2i=`cam_ext_0`，ZED-M=`cam_wrist_right`；最终 RGB-only，当前 UVC/OpenCV 后端无深度且 `enable_camera_depth=false`，v3 需求也排除 depth/point cloud。raw 图像模式将参数化：`aligned_10hz` 保存控制步 RGB；`video_30hz` 保存每路 MP4 + control→video 关联且不重复 RGB。
- **仍需决策**：OQ-026 最终 MP4 codec/source（含 30Hz 原始视频策略）与 OQ-027 v3 timeline/PTS（标称控制时间还是实测关联）。在它们明确前不得实施或把 draft baseline 激活。

## 2026-10-16 Franky C++ 发布源码审计

- 本机 extension/tracker 与下载 wheel 字节一致；wheel SHA256 与 GitHub digest 一致。成功构建关联源码 `7bdb567`，release tag 指向另一 master 提交，不能拿 tag 直接当 wheel 源码。源码—二进制关联仍非密码学证明。
- 独立静态复核确认：tracking 直接替换姿态，无姿态插值；旋转误差为 quaternion vector（sin(theta/2)），不是 rotvec；阻尼为 2sqrt(K)，无 twist 时目标速度为0；nullspace q_ref固定但投影随J变化。
- 找到实际 arm Worker 日志：K_r=80、K_ns=5、rot_clip=.15；只有启动期两次 tracker 创建。纯轴 .15 clip 对应约17.25°，不是 .15rad；12Nm仅是单轴刚度wrench上限，不含阻尼/其他项，更非总关节力矩限值。
- 7.4Hz离散目标与腕部阻抗相互作用是具体待证机制；不能认定根因，也不能凭此解释roll特异性。未改产品或操作硬件。
- 证据与审计：`.project-log/docs/franky-release-audit/README.md`。独立源码复核通过；数值独立复跑及真机因果仍未验证。
- 下一步需操作者批准诊断范围：设计并离线验证 opt-in 非阻塞高频 reference/q/dq/torque 采集，不动控制参数；现有低频pickle不足以定位周期内振动。T-013保持未完成。

## 2026-10-16 roll 再审：撤回时序/最终目标排除结论

- 用户暂缓滤波；本轮仅离线审计，没有修改产品代码/配置或操作硬件。
- 更正前轮：连续下发入口间隔中位 135.412ms（约7.385Hz），而非8.9Hz；snapshot_age 是快照后处理耗时，不能证明源新鲜；final_franka_target 在 Franky guard 前采样，不能称实际最终目标。
- 三段映射旋转峰值 58.87/49.27/53.51°，不满足原计划5–10°小幅对照。相邻请求姿态变化中位2.46/2.68/2.85°。低频目标更新与腕部阻抗动力学仍是待查组合，未归因。
- 独立源码审计确认每次目标更新不重启 tracker；nullspace 目标保留 tracker 创建时 q。实际 C++ 插值、阻尼、姿态误差与投影尚未核实；不能用 gains smoothing 代替 pose smoothing。
- 质量检查退出1：episode0为空短轨迹，日志grip匹配未完成；episode1可作有限离线分析，不得声称整个batch质检通过。独立数值复跑受 verification runner 缺失阻塞，静态复核支持修正。
- 可复放：`RLinf/.venv/bin/python .project-log/docs/roll-timing-reaudit.py`；数值绑定pickle SHA256 `8fbf4b5d30508bdc79b78e76b826ec7b08ab196bf3e85f0b388e67e3ee1ab1df`。
- 下一步：先定位已安装 franky_control 1.1.3/libfranka0.19 wheel 对应 C++ 源码/构建提交，离线核实控制公式；在此前不建议继续调参或扩大真机动作。T-013未完成。

## 2026-10-16 首轮历史记录（时序/最终目标结论已被上方再审更正）

- 证据：run `20261016-162726` 的 `episode_1_step_487_success.pkl`，164 transitions；有效 grip 分成 3 段（30/22/23 steps），passive Pico/Franka fields 均完整。启动日志确认 `max_step=.10`、`max_step_rad=.20`、realtime enforce；未回显 action_scale/rot_clip，故后两项不由该日志独立确认。
- 输入/时序：外层实际约 8.9Hz（Pico source sample median 139ms）；snapshot age 0.21–0.51ms，phase timing 无尖峰。Pico→requested target 的单步姿态变化 p95 约 .056–.074rad，未见 Euler 分支跳变或 `.20rad` guard 重复饱和。XR/PC 时序、目标构造和 final guard 不再是本次采样下的首要嫌疑。
- 机器人侧：请求—实测姿态误差中位约 .166/.171/.190rad，最大 .254/.231/.258rad；q5/q7 参与明显（各约 .75–.93rad / .68–.83rad 峰峰值，dq 最大约 .63–1.07rad/s）。各段 q 走势主要单调，8.9Hz 的 post-step 采样**不能证明或排除**每 step 内的高频振动。
- 当前裁决：不归因、不改参数；下一安全判别是维持同一参数和 passive telemetry，在一个安全但明显不同的邻近机械臂姿态重复同样小幅正/负 mapped-roll。若现象/q5-q7 模式强烈随姿态变，优先 Jacobian/nullspace/负载/机械；若不变，输入滤波与 controller dynamics 仍需保留。要证明高频振动机制需要更高频 Franky 状态记录。

## 2026-10-16 roll 特异性振动：诊断报告已记录（RS-011 / T-013）

- 现象（操作者报告）：平移稳定；缓慢 roll 时末端显著振动，其他旋转较轻；调整 `action_scale`、目标步进 guard 与力矩尺度未解决。
- 已确认链路：Pico grip-edge 相对 rotvec → 固定轴重映射/yaw 对齐 → PicoDelta 笛卡尔 TCP 目标 → `rotvec→Euler xyz→quat` → Euler 姿态窗口 → Franky Cartesian impedance。没有本项目显式的在线 IK/关节目标生成。
- 假设排序：①未滤波 Pico 旋转/目标噪声；②阻抗闭环或 wrist/nullspace 动力学；③位姿相关 Jacobian/腕部构型；④Euler 表示或窗口分支；⑤Robotiq 工具 payload/COM/线缆；⑥机械摩擦/回差；⑦XR/PC 时序（不足以单独解释 roll 特异性）。
- 决定：先采集观察证据，不改控制参数。`--passive-telemetry` 会保留 Pico 原始/变换姿态、rotation delta、Pico/requested/final target、实测 TCP、pre/post q/dq 和阶段时间。判据：输入先抖→输入/映射；请求先跳→表示/窗口；最终目标才变→guard/clip；目标平滑而 TCP/q/dq 抖→阻抗、构型、载荷或机械。
- 约束：不提高旋转力矩、速度、dynamics factor、力矩变化率或 Desk 限制；不把 T-06 单轴 clip 无效误读为“阻抗无关”。

## 2026-10-16 A-012 复位姿态跨 ±π 分支导致 rx 被夹断

- 现象：13:41 会话按 `y` 同步 reset_ee_pose 后，机械臂 reset 到"非常奇怪的位置"。
- 根因：`clip_euler_to_target_window` 的窗口边界不做 wrap；当窗口被居中到 `target_ee_pose[3:]` 的另一 ±π 分支时，rx 的 delta 窗口整体不可达，`np.clip` 恒取下界 → rx 固定 `+1.117166`（实测 rx 扫描全部输出同值）。
- 缓解（方案 C，`63a8e32`）：恢复 HEAD 的复位姿态与姿态窗口；`E-046` 验证三轴可达、reset 姿态过 clip 不变。
- 仍未修：RLinf 侧 wrap 缺陷与 `sync_reset_pose.py` 自检盲区；`A-012` 保持 open。

## 2026-10-16 T-010 新诊断轨迹绘图

- 新 run `20261016-111731` 有两条 success pickle；选择 episode_1（397 transitions、7 个 b segments），排除 episode_0（3 transitions）。
- 输出 TCP requested-vs-measured 6D 图/CSV 与 measured pre/post q/dq 7-axis 图/CSV；`E-043` 绑定真实 pickle 和产物。
- 绘图显示 q/dq 是真机测量值，控制输入仍是 Cartesian；当前只完成可视化，不根据图直接改变控制参数。

## 2026-10-16 T-009 移除不合理的诊断静止起始门

- 操作者明确指出静止门与既有正常启动语义冲突：`FrankaEnv` 应在采集启动后自动插值到 `reset_ee_pose`，不应要求手动拖回 reset。
- `7d2b480`：删除 `check_stationary_start.py`、launcher/direct collector 两处 gate、相关门禁测试和 runbook 描述；保留 passive telemetry、相机 preflight、现有 reset 警告及 Cartesian 控制语义。
- 证据：focused diagnostics 7 passed，`test_data.py` 121 passed，compile/bash/diff check 通过；`--dry-run --passive-telemetry` 不含 gate 并保留自动 reset 警告（`E-041`）。独立 reviewer 的受控 runner 缺失，`E-042` 为 candidate。

## 2026-10-16 T-008 被动 Franka 七轴状态遥测

- `83a23ba`：在 opt-in `--passive-telemetry` 中复制 Franky state 的 pre-command 与 post-command `q[7]`/`dq[7]` 至 `passive_franka_step`；不引入 IK 或 joint command。
- 新增 root `DATA_COLLECTION_SCHEME.md`：说明原始 pickle、观测/infos 对齐、图像、Pico action、segments、LeRobot 导出与 q/dq/continuous-IK 边界。
- 证据：focused 生命周期 + schema 测试 8 passed，`test_data.py` 121 passed、compile/bash/diff check 通过（`E-039`）。独立静态复核发现无实现缺陷，但受控 runner 缺失，故 `E-040` 仅 candidate；真机 pickle schema 仍待操作者验证。

## 2026-10-16 T-007 被动遥测与静止起始门

- `3865152`：增加 `--passive-telemetry`、逐步被动 Pico/Franka 遥测、`check_stationary_start.py` 及运行手册；诊断只复制 info，未变更控制语义。
- 门禁：canonical launcher 和 direct collector 均在 Ray/采集前检查 reset pose + grip release，读取失败/超时 fail-closed。
- 证据：`E-037` focused tests/compile/shell/regression；`E-038` 独立源码 review。真机端到端遥测有待操作者按 runbook 执行。

## 2026-10-15 数据链路说明

- **数据链路讲解记录**（2026-10-15）：已确认 Pico 原始绝对手柄 pose 经固定轴旋转，再经头显标定（yaw + 平移）成为会话项目世界表达；握 grip 时以手柄与 TCP 的各自锚点计算相对增量，最终由 PicoDelta 形成 TCP 目标误差。该会话世界系不等于 Franka 基座绝对系，实际控制依赖相对增量而非外部绝对标定。下一步：对新轨迹可视化 action 与实际 TCP 跟踪。

## 2026-10-15 T-04/T-05 真机调参 + 检查点提交 + 相机预检 + AGENTS 更新

- **T-04**（`D-024`，操作者批准）：`translational_clip_{x,y,z,neg_*}` `0.01→0.02m`，运行时 `K_t=1200N/m`、`trans_clip=[.02,.02,.02]`，约 24N/轴。操作者确认「进一步提高了」。
- **T-05**（`D-025`，操作者批准）：`rotational_clip_{x,y,z}` `0.15→0.20rad`，运行时 `K_r=80Nm/rad`、`rot_clip=[.20,.20,.20]`，约 16Nm/轴（`K_r` 已是 RLinf cap）。操作者确认「整体情况好了很多」。
- **静态验证**：`E-029`（T-04）、`E-030`（T-05）——用非连接 `FrankyArm` 走同一参数解析路径，确认 cap/floor 后的实际值；`git diff --check` 通过。
- **检查点提交**：RLinf `e7a9a2e feat(embodiment): tune Pico Franka teleoperation`（配置 + `collect_episode.py` 的 `segment_ids` 导出）；扩展 `803ba2a feat(collection): preserve demo segment metadata`（转换器 `segment_ids`→LeRobot `segment_id`）。提交前跑 `tests/unit_tests/test_data.py` 121 passed，并用真实 run `114121` 跑通 pickle→LeRobot（修掉一个 `segment_id` 必须是 `np.ndarray[uint8]` 的自造缺陷）。
- **`A-011` 复发**：14:37 会话里 ZED-M 又只出现 HID（USB 2.0 路径 `1-3.1` speed=12），ZED 2i 视频端正常（`2-3.1.1` speed=5000）。采集在 `DataCollector` 构造期以 `ValueError: invalid literal for int()` 崩掉——fail-closed，未写入无效数据，但白跑约 1 分钟且报错难懂。
- **加固**：`run_pico_session.sh` 新增相机预检（`a79d524`/`E-031`）：读当前配置的 `camera_serials`，逐台核对 `/dev/v4l/by-id`，缺失时打印 USB 3.0 指引并在启动任何服务前中止；已用 `--dry-run` 在真实故障状态下复现拦截。
- **AGENTS.md 更新**：双嵌套仓库结构、当前检查点、采集链路、键盘/数据交付、双相机、已验证参数、真机安全边界、两个待诊断问题与「先诊断不再加参数」约束、相机预检。
- **子 Agent 失败**：两次 `solution-researcher`/`codebase-onboarder` 委派因 `llm-center.modelbest.co` DNS 超时失败，roll 抖动与延迟诊断**尚无结论**，不得视为已完成。
- 下一步：先修 ZED-M 的 USB 3.0 连接；随后诊断 roll 抖动与偶发补执行延迟（优先做被动逐阶段耗时/时序观测，不先改参数）。

## 2026-10-15 T-03：x/y 平移阻抗真机诊断通过

- 保持 `action_scale/max_step=0.04m` 与 x/y `translational_clip=0.01m`，未继续增加速度或刚度。
- run `20261015-114121`：Worker 实际回显 `K_t=1200N/m`、`trans_clip=[0.01,0.01,0.01]`；有效诊断 episode 248 步，`segment_ids=0..6`，六个有 grip 的分段各有 13–17 个 active 帧、相对 TCP 位移 0.096–0.203m。
- 操作者确认前后明显更跟手；日志无 timeout、错误或 Desk 告警，也未报告突跳/振荡。前两个短/空 episode 已排除出诊断证据。
- `E-028` valid；`D-023` 已补充真机结果；`TELEOP_TUNING_LOG.md` 的 T-03 标为通过。下一步：保持参数用于后续任务采集，发现独立问题再做单变量试验。

## 2026-10-14 数据采集链路收尾准备（键盘控制 + 数据链路查证 + 权限 + 相机）

- **操作者决策**：用普通薄膜键盘做 episode 触发（找人帮按）；接受 episode 由键盘决定但要保底最大时长；
  接受录制期一直按 grip；数据两阶段交付（`D-021`：采集期 pickle 信息丰富 → 后处理转标准 LeRobot）
- **数据现状**：今天 15:54 / 16:08 / 17:08 三次运行共 12 条 episode，全部落在 `collected_data/*.pkl`
  （文件名全 `_fail`，因为 reward 恒 0）；实测图像/状态/动作三项齐全，`actions` 字段恒 0（`A-004`）
- **键盘链路**：权限根因是 evdev 的 `list_devices(writable=True)`；`setfacl` 后 0→15 个设备；
  发现 BRLTTY 虚拟键盘导致必须用 `RLINF_KEYBOARD_DEVICE` 钉住真键盘；实测可打开、不钉则报错
- **重大查证**：官方 Pico 配置的键盘注释描述的是另一个包装器（`A-009`）；`segment_id` 被 pickle 丢弃（`A-010`）；
  `states` 19 维布局与 `intervene_action` 在 EE 系（`RS-007`）；保底超时可用扩展实现、不改 RLinf（`RS-007`）
- **相机**（`A-011` 已 resolved）：第二台相机 ZED-M 起初只枚举 HID，根因是它接在 USB 2.0-only 路径上、
  SuperSpeed 无法协商 → 视频端不枚举。换到 USB 3.0 口后两台同时可用；
  用互换端口做对照实验排除了"供电不足"假设（并发各 60/60 帧、~28fps 无丢帧）
- 记录：`A-009`~`A-011`、`RS-007`、`D-021`、`Q-006`、`E-018`



## 2026-10-15 E-025：真机 100 步看门狗验证成功 + timeout provenance 修正

- **真机验证**：会话日志明确回显 `本次录制超时阈值：100 步`；Worker 于 10:22:56 与 10:23:36 两次记录 `[keyboard] timeout`，runner 均打印 `Episode ended (reward=0.00). Discarded.`。两个 `_fail.pkl` 产生、失败不新增 demos；一次按 `c` 产生唯一 success demos，符合机制。
- **发现并修复**：旧 timeout 分支设 `pre_record=True`，被 `CollectEpisode` 跳过终止帧；故旧 `_fail.pkl` 虽已失败落盘，却缺失 `keyboard_event=timeout` 和 `terminated/truncated`。现改为保留 timeout 终止帧（仿照 `c`），下一次 reset 才清 `recording`。
- **回归**：扩展+缓冲集成测试现覆盖 21 项：timeout 会写 `_fail.pkl`，其最后 info 有 `keyboard_event=timeout`，最后 `terminated=True`/`truncated=True`。修后真机 provenance 仍待下次自然 timeout 复核。
- **启动可观测性**：顶层会话、wrapper、Worker 分别回显实际阈值，避免再发生临时变量未带入而误判。

## 2026-10-15 D-022：录制期 5 分钟超时修正

- **独立复核发现并由主 Agent 复现**：旧方案的 `KeyboardStartEndTimeout` 在真实栈中是死代码；`RealWorldEnv.step` 在外层以 `elapsed_steps >= max_episode_steps` 重写内层的 `truncations`。旧配置两个阈值都是 3000，录制步数不可能先于自 reset 的 elapsed 达到超时。
- **操作者选择方案 1**（`D-022`）：看门狗保留 **3000 步（从 `a` 开始，5 分钟）**；外层 `max_episode_steps` 提至 **3600 步（从 reset 开始，6 分钟）**，留 60 秒启动余量。若按 `a` 前空等超过 60 秒，外层仍可能先收尾。
- **拒绝 `manual_episode_control_only: true`**：`start_end` 不写 `manual_done`，而 runner 在该开关下只以 `manual_done` 判定是否写 demos；启用会令按 `c` 的成功轨迹不落 demos。
- 代码修正：看门狗比较从 `>` 改为 `>=`；加 `Pico._reported` 所有权的显式升级错误；自检工具改为日志缺失时 fail-closed；转换器在整条动作全零时发警告。
- 新增临时验证开关：`RLINF_KEYBOARD_TIMEOUT_STEPS=<正整数>`，默认未设即 3000。以 `=100` 跑一次故意不按 `c` 的试验，约 10 秒可验证完整真机栈应产出 `_fail.pkl`、不写 demos 且日志出现 `timeout`。
- 验证：YAML 外层=3600、默认看门狗=3000；组件单测 17/17；覆盖值=7 时实际注册模式第 7 步产生 `timeout`, `terminated=True`, `truncated=True`, reward=0；非法值被拒（`E-023`）。**完整 RealWorldEnv 真机超时路径仍待验证。**

## 2026-10-14 T-005 实现落地（键盘 episode 控制 + 保底超时 + 数据丰富化 + LeRobot 后处理）

- **交付 5 项**：`rlinf_ext/collection.py`（新增，看门狗 + rich PICO info）、`rlinf_ext/__init__.py`、
  配置（`start_end_timeout` / 3000 步 / 双相机）、`run_collect_pico.sh`（自动解析键盘设备）、
  `post_process_to_lerobot.py`（新增，pickle → 标准 LeRobot）
- **验证**：扩展单测 17/17；配置与相机路径；脚本语法 + 解析块；转换器用真实数据跑通
  （与源 pickle 逐像素最大差 0.000000、`actions max|a|=1.3780`）
- **实现期修掉两个自己的 bug**：staticmethod 幂等检查、`c` 之后误计数
- **未验证**：端到端真机（`demos/*.pt` 产出、rich info 落盘、多相机 `extra_view_image`、看门狗真实超时）
- 记录：`E-020`

## 2026-10-14 vr_data_publisher 修复（配置路径 / buffer_size / docstring）

- `pico_software/vr_data_publisher.py`：默认配置路径 `parents[2]`→`parents[0]`（原先静默回退到内置默认值）、
  `buffer_size` 从死键变成真配置、文件头 docstring 去掉上游样例残留。实测日志确认现在能读到正确配置。
- 文档补漏：PC Service 两个端口 —— 63901（头显入站）/ 60061（本机 SDK gRPC），
  `PROJECT_OVERVIEW.md` 原来漏了 60061。
- 实测事实：`xrt.init()` 在服务未监听时也返回成功 → 发布器无法自检设备缺失，必须靠 `pico_probe.py`。
## 2026-10-13 项目复盘文档（T-003）+ 框架摩擦分析

- 状态：T-003 收尾（`E-014` valid）。交付 `PROJECT_OVERVIEW.md`（745 行）与
  `.project-log/docs/brief-overview-doc-structure-for-gpt.md`（124 行，给 GPT 索要结构方案用）
- 写作中发现并修正手册一处误导性指引：6.9 把 `demos/` 写成唯一交付通道，实际它自 `D-016` 起恒空
  → 重写 6.9 + 新增 7.28 + 索引行 + 另 3 处修订（记录 `A-007`，手册现 1854 行）
- 数据交付现状：只有 `collected_data/*.pkl` 有数据，真实动作在 `infos[*].intervene_action`
- 框架摩擦（`A-008` / `VIBE_FRAMEWORK_FRICTION.md`）：55 次调用中仅 2 次在写交付物；
  36% 用于记账，其中 14 次是猜 CLI schema；写入本身只 2 分 59 秒 → 瓶颈是可发现性

## 2026-10-13 A-006 真机确认 + reset_ee_pose 解耦（方案 A）+ 遥操作提速

- 状态：A-006 真机确认修好；方案 A 已实现、静态验证通过；提速已改、待真机手感确认
- 完成内容：
  - 旋转修复真机确认（E-011）：Ray worker 日志 `rot_clip=[0.15 0.15 0.15]`（改动前 0.02 02 02），
    操作者报告「姿势可以旋转」
  - 发现并当场修掉**第二个天花板**：操作者按 `y` 同步位姿后，姿态窗口仍以旧复位姿态为中心，
    复位点到 rz 上沿只剩 5.6°（第一次是 10.7°）—— 现象与 7.26 一模一样，极易误判成"没修好"
  - **方案 A（D-020）**：`sync_reset_pose.py` 成为该不变量的唯一维护者 —— 同步位姿时按现有半宽
    平移居中姿态窗口（只平移、不放宽）；只读检查新增姿态窗口居中判定与位置盒包含性；
    复位点出位置盒**阻断启动**（reset 不走安全盒而 step 每步都裁 → 会无人指令自走）
  - **提速（E-013，candidate）**：position_scale 0.4→0.7、action_scale[0] 0.02→0.03
    （0.2→0.3 m/s，已到 franky max_step 硬上限）；rotation_scale 保持 0.4
- 验证与限制：E-012（valid）覆盖纯逻辑单测、写回行数不变量、端到端 `--apply`（写临时副本、
  含复现真实历史偏心态）；真机手感与 `--apply` 的实际操作体验待操作者
- 文档：新增 7.27，并同步阶段表 / 参数表 / 第 8 章安全参数

## 2026-10-13 旋转迟钝根因定位与修复（A-006 / D-019）+ 一键脚本实测通过

- 状态：修复已实施、静态验证通过；**真机复测待操作者**
- 完成内容：
  - 操作者实测：一键脚本 `run_pico_session.sh` 可正常启动与关闭（E-010 补齐）
  - 定位「末端平移跟手、旋转迟钝」的根因：**不是 IK 问题**（本机无显式 IK，笛卡尔→关节由 franky /
    libfranka 的笛卡尔阻抗控制层完成），而是**笛卡尔阻抗的旋转 `error_clip` 严重不足**：
    实测生效值 `K_r=80 Nm/rad × rot_clip=0.02 rad = 仅 1.6 Nm`，低于腕部重力+摩擦阻力；
    而平移有 6~12 N，所以表现为"平移敏感、旋转迟钝"
  - 第二个独立天花板：姿态安全窗口没有以复位姿态为中心，复位点到 rz 上沿只剩约 10.7°
  - 修复（D-019）：`rotational_clip_x/y/z` 0.02 → 0.15（最大力矩 1.6 → 12 Nm，7.5 倍）；
    姿态窗口重新居中到复位姿态（尺寸不变）；`pico.rotation_scale` 暂保持 0.4
- 重要教训（已写入文档 7.26）：**Hydra 的 `override_cfg` 是合并语义**，基础 env 配置自带的
  `compliance_param` 会静默生效，不能用代码默认值推断；核实必须用 `--cfg job`
- 验证与限制：静态全部通过（组装结果、cap/floor 推算、`FrankaEnvConfig` 构造、窗口余量）；
  真机行为属物理推断，待实测

## 2026-10-13 首次真机闭环遥操作成功 + 启动链路成文

- 状态：里程碑达成（能用手柄驱动真机）；仍未完成（夹爪真机开合、末端最低点、正式采集）
- 完成内容：
  - **操作者按住 grip 后成功驱动真机**：TCP 移动 11.2cm（`[0.5236,0.0888,0.3377]` → `[0.5763,0.0043,0.2865]`），
    `demos/*.pt` 中 124 步有 17 步非零动作，安全盒按预期生效（`E-008`）
  - 修掉启动拦路石：`Unsupported BaseCamera backend 'zed_uvc'` → 官方 `disable_validate: true`（`D-015` / `A-003`）
  - 发现数据保真缺陷：`collected_data/*.pkl` 的 actions 恒为 0（真实动作在 `infos[i]["intervene_action"]`）→ `A-004`，
    交付物改用 `demos/`
  - 放宽安全盒：z 下限 `0.2877` → `0.03`（原因：只允许下降 5cm，末端降不到桌面）；`target_ee_pose` 位置移出可达范围，
    避免"经过目标点即判成功并自动复位"（`D-016`）
  - 确认 `A`/`B` 无效的真因：**按键只在按住 grip 时才被读取**；原始消息探针实测按键通道正常（文档 7.23）
  - 定位"机械臂死活不动"的真因：**发布器不恢复设备断连**，一直推全 0；确立"头显先连 → 发布器 → 验数据 → RLinf"的
    固定顺序，以及"发布器重启后必须重启 RLinf"（文档 7.22）
  - 关闭 `enable_camera_player`（消除 `cv2.imshow` 报错，文档 7.19）
  - **`PICO_FRANKA_SETUP.md` 第 6 章整体重写**为可复制粘贴的完整启动链路：前置检查（含位姿核对与同步脚本）、
    PC Service、头显设置+**站位**+标定、发布器、数据验证、启动采集、操作方式、结束清理、数据位置、失败恢复表、收工关机
- 验证与限制：
  - 已验证：手柄驱动真机、安全盒裁剪、ZMQ 按键通道、干跑全链路
  - **未验证**：夹爪真实开合（按正确姿势）、末端最低点（需实测后收紧安全盒）、episode 结束信号、演示数据质量
- 下一步：见「当前状态」的下一步

## 2026-10-13 全栈干跑打通（软件链路全部验证完毕）

- 状态：已完成（干跑），未完成（机械臂运动 / 闭环遥操作 / 正式采集）
- 完成内容：
  - 干跑前预检：位姿零偏差、首次 reset 不关节复位、`go_to_rest` 不移动、step 不发夹爪指令
  - **干跑第一次失败**：`Unsupported BaseCamera backend 'zed_uvc'` —— RLinf 注册表按进程隔离，
    节点硬件校验所在的 `_RemoteNodeProbe` actor 不加载 `RLINF_EXT_MODULE`（框架缺陷 `A-003`）
  - **解决**：用官方开关 `disable_validate: true` 绕过，**不改 RLinf 源码**（决策 `D-015`）
  - **干跑第二次通过**：Cluster 校验 → Ray worker 内构造环境（franky 真机连接 + `realtime enforce`
    + Robotiq 激活 + `zed_uvc` 相机打开）→ 300 步 @10Hz → pickle 落盘 16 MB / 301 条观测
  - 机械臂**零漂移**（位置 5e-05 m / 姿态 6e-05 rad）
  - 导出落盘图像目视确认：机械臂、工作台、台上物体均在取景内
- 新发现的待办：落盘图像是 128×128 中心正方形（文档 7.20）；episode 判 fail、循环不自停（文档 7.21）
- 下一步：首次真机运动验证（已在后续完成）

## 2026-10-13 环境搭建完成，软件链路全部打通

- 状态：已完成（搭建与联调），未完成（真机运动验证）
- 完成内容：
  - RLinf 主环境装好（Python 3.11.14；franky 1.1.3 / libfranka 0.19.0 / torch 2.11.0+cpu / ray 2.59.0 / lerobot 0.1.0）
  - 机械臂只读链路验证通过（FCI 可用、位姿可读、realtime enforce 生效）
  - **相机阻塞解除**：ZED 2i 的 UVC 裸流 + 自写 `zed_uvc` out-of-tree 后端
  - **Pico VR 链路端到端打通**：头显 APK → PC Service(63901) → xrobotoolkit_sdk → vr_data_publisher(80Hz) → ZMQ → RLinf 订阅
  - 单臂采集配置与启动脚本就位；安全参数全部显式写死
- 关键排障：主机 `ufw` 默认拒绝入站（仅放行 ICMP），导致头显报 socket 连接失败；已按热点网段放行 63901/tcp 与 29888/udp
- 下一步：全栈干跑（已在后续完成）
