# Current Session

> 会话恢复入口。维护规则：
> - **头部快照**：顶部“当前状态”区块是稳定入口，每次更新时覆盖，不追加旧版本。
> - **最新在最上**：最新一次会话写在文件最上面的会话区块，旧会话依次向下。
> - **超限归档**：文件超过约 50-100 KB 或会话区块达到约 10 条时，把旧会话区块移动到 `.project-log/docs/archive/`，主文档只保留最近内容。
> - **单一事实源**：精确当前状态与下一步以 Project Log format 2 状态库、Git 账本与生成的 `handoff.md` 为准；不要在多份长文档里维护互相矛盾的“下一步”。
> - **机器文件不手工重排**：状态库、Git 账本与生成视图由运行时维护，不做手工重排或改写。

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

- **v3 工程规格阶段已启动（T-021，2026-10-18）**：业务澄清已覆盖采集批次、episode outcome、相机语义、严格 state/action、独立传感器时间轴、统一采集起点、默认固定相机参考、虚拟严格30Hz、最近邻半周期容差、禁止边界外推、允许合规复用和QC fail-closed。工程规格已形成并经独立静态复核迭代：包含 raw 字段契约、独立时间轴、严格30Hz对齐、最近邻未来 action、QC、任务/进度和 v3 文件约束。剩余是官方 v3/视频技术研究与最终模块落点核对；暂不修改控制代码或操作硬件。

- **Reset执行器免交互（2026-10-18）**：用户明确要求取消文字确认，已移除EXECUTE CLEAR/MOVE及TTY门禁；显式--execute在预检后自动连接并运动，无该开关仍preview。保留FCI1337占用、独占锁、隔离/新日志、异常停止不返程；运动逻辑参数未改。实现者45项离线测试通过，独立静态复核接受，runner缺失；未真机。此条取代旧交接中的二次确认要求。

- **跨传感器时间轴方案已确认（2026-10-18）**：未来正式采集不要求各传感器同频；每个传感器独立保存数据与相对统一采集起点的单调时间轴。后处理默认以外部固定相机为参考，生成从0开始、严格30Hz的虚拟时间轴；每个虚拟时刻从各传感器选择最近时间戳数据，形成LeRobot v3对齐样本。当前历史试验数据不作为正式转换输入。已确认最近邻匹配必须有最大允许时间差，超出则样本无效并由 QC 失败；具体阈值、时间轴边界和重复复用规则已确认；下一步澄清统一采集起点和各传感器时间戳的生成/校验语义。

- **T-020隔离Reset执行器已实现**：杂项/reset_lab/execute_reset.py，独立配置/控制/Python3.10/重建Franky，正式环境未改。主Agent复跑35项离线测试通过；独立静态复核接受（日志耗尽停止证据问题已修复），独立runner缺失。默认preview，episode/startup、可选强制插值、A…E…A、中间2秒、异常不返程。大跨度点位路径及实际停止未真机验证；须操作者阅读EXECUTOR.md并确认扫掠空间。无Ray/新tracker/额外读状态，非时间完全等价。下一步操作者小范围验证并保留日志。

- **独立Reset实验业务澄清**：用户确认两脚本（拖动模式只读回车采点TCP+q；文件顺序A→B→…→A），中间停2秒、最后直接返A结束，异常不返程。启动/episode两模式，默认episode，原样判断或可选强制插值。配置/控制代码/Python/Franky全隔离；日志含版本参数目标与实测状态。已记录RB-019和docs/requirements/reset-lab-v1.md；仅澄清未实现。下一步只读核验采点接口、隔离构建与Reset等价性，再出工程规格。

- **整份配置恢复52cdf9a（2026-10-18）**：用户要求恢复上个检查点配置；single_franka YAML已逐字恢复52cdf9a（blob faf3d971ef311f15ab4cbd0dcd05139b969d112b），包括旧reset及姿态窗口。备份 docs/parameter-trials/restore-52cdf9a-20261018/before.yaml。精确比较/YAML检查通过，独立静态值复核通过、runner缺失。无其他产品/数据修改，无硬件操作；旧咨询简报参数快照仅作历史。下一步操作者新会话加载，注意归位目标改变；整臂抖动未解决。

- **最高优先级现象更正（2026-10-18）**：用户明确指出是整个机械臂抖动，撤回“J7最明显、J1–J6平滑”的虚假描述。今后不得把J7选择性作为事实或根因排序依据；历史q/dq幅度仅为运动量，不是抖动强度。外部简报标题、现象、假设和问题已同步修正，保留旧文件名仅兼容链接。后续分析覆盖七关节与TCP。

- **外部诊断简报（2026-10-18）**：用户反馈小恢复力迟钝仍抖、大恢复力更抖且末端偶尔乱飘；启动和episode reset移动均抖。已保存 docs/franka-j7-reset-vibration-expert-brief-20261018.md，独立静态复核无实质错误；历史数值未独立重算。最新磁盘guards=.2/.5、action_scale=[.2,.5,1]、Kr请求60、旋转clip=.1，已不同于下方官方试验快照；未绑定最新Worker日志。仅整理文档，不改控制。下一步用户外部咨询后带回意见核验。

- **官方阻抗对照试验（2026-10-18）**：用户授权只改刚度与误差clip；请求2000/150，平移正负[.003,.003,.01]，旋转正负[.02]*3。离线实际驱动解析为1200/80、[.005,.005,.01]/[.02]*3，其他参数与修改前备份语义一致；保留现场已有修改，不假定仍完全等于52cdf9a。独立静态复核接受，runner缺失。备份 docs/parameter-trials/official-compliance-20261018/before.yaml；启动构造参数未变。下一步操作者新会话确认Worker日志，小范围测试，未做真机验证。

- **恢复52cdf9a（2026-10-18）**：用户指定回退；RLinf工作树已与52cdf9a逐文件一致（git diff exit0），仅max_step恢复0.08、action_scale恢复[0.04,0.3,1.0]。HEAD仍79a647e，未提交；Franks/数据不动。YAML检查通过，独立静态值复核通过，独立runner缺失。操作者新会话加载；不声称解决抖动。用户补充启动和episode reset移动均抖，复现需求尚在澄清。

- **test1.0已回滚（2026-10-18）**：用户报告实验失败并要求回滚。RLinf-Franks启动脚本与注册文件恢复到滤波前HEAD，4个实验文件移出活动代码并归档至 docs/archive/test1.0-rollback-20261018/。离线遥测回归7项通过，bash语法通过，独立静态复核通过；独立runner缺失。RLinf、杂项、采集数据未改；不再传 orientation-filter/tau 参数。未连接或停止硬件进程；已运行进程需操作者正常结束再启动以加载回滚代码。

- **T-016 独立运动诊断**：用户确认远离限位、场地清空且急停可达，按操作者本地实验开放显式 --execute（逐次同意、逐段确认）；保留限位/时序/误差/clip检查。18项实现者离线测试通过，独立静态复核可接受，独立runner缺失。默认1°/s、上限5°/s；正常返初始q、异常不返程。未连接硬件，物理停止/跟踪/扫掠空间未验证。下一步操作者本地分阶段试验并保留JSONL。

- **v3 业务基线（draft）**：`RB-015-franka-pico-raw-to-lerobot-v3` 已固化并关联 `BA-015`~`BA-023`；完整用户需求转录在 `.project-log/docs/requirements/lerobot-v3-semantic-format-v1.0.md`。因刚确认的跨传感器对齐规则尚未形成完整工程基线，基线 approval=pending，尚未进入实现。
- **采集/批次**：一次 `run_pico_session.sh` 从启动到操作者结束即一个无数量目标的 raw batch（timestamp run 目录）。`c=success`、计划新增 `f=failure` 均保存并仅提示累计/成功/失败数；`a=abort` 丢弃；timeout raw-only、默认不导出。每 batch 只有一个可为空的 task 文本；换 task 必须新开 batch。
- **后处理/导出**：采集只写 rich raw；离线处理选择一个 batch。模式为 strict `standard-success-only`、strict `standard-all`，以及带明确 outcome 扩展的 `labelled-all`；全部输出均不默认包含 timeout。
- **严格 v3 Franka profile**：state=实测 `joint_position[7]`、base-frame `eef_pose[7 xyzw]`、gripper；action=最终实际送入 Franky、guard/clip 后的 base-frame绝对 `eef_pose[7 xyzw]` + 独立 gripper，`custom.action_space=eef_pose_absolute`，无 `action.joint_position`。历史缺少最终 target/provenance 的 raw batch 不得伪造转换。
- **相机/模态**：ZED 2i=`cam_ext_0`，ZED-M=`cam_wrist_right`；最终 RGB-only，当前 UVC/OpenCV 后端无深度且 `enable_camera_depth=false`，v3 需求也排除 depth/point cloud。raw 图像模式将参数化：`aligned_10hz` 保存控制步 RGB；`video_30hz` 保存每路 MP4 + control→video 关联且不重复 RGB。
- **时间轴已确认**：未来正式采集时各传感器独立记录数据和相对统一采集起点的时间轴；后处理以外部固定相机为默认参考，生成严格 30Hz、从 0 开始的虚拟时间轴，并按最近时间戳对齐各传感器。OQ-026 也已确认：离线将 raw RGB 编码为 MP4，原始 raw 不变。下一步澄清最近邻匹配的容差/边界规则，再更新基线。

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

- **数据链路讲解记录**（2026-10-15）：已确认 Pico 原始绝对手柄 pose 经固定轴旋转，再经头显标定（yaw + 平移）成为会话项目世界表达；握 grip 时以手柄与 TCP 的各自锚点计算相对增量，最终由 PicoDelta 形成 TCP 目标误差。该会话世界系不等于 Franka 基座绝对系，实际控制依赖相对增量而非外部绝对标定。下一步：对新轨迹可视化 action 与实际 TCP 跟踪。

## 2026-10-15 T-03：x/y 平移阻抗真机诊断通过

- 保持 `action_scale/max_step=0.04m` 与 x/y `translational_clip=0.01m`，未继续增加速度或刚度。
- run `20261015-114121`：Worker 实际回显 `K_t=1200N/m`、`trans_clip=[0.01,0.01,0.01]`；有效诊断 episode 248 步，`segment_ids=0..6`，六个有 grip 的分段各有 13–17 个 active 帧、相对 TCP 位移 0.096–0.203m。
- 操作者确认前后明显更跟手；日志无 timeout、错误或 Desk 告警，也未报告突跳/振荡。前两个短/空 episode 已排除出诊断证据。
- `E-028` valid；`D-023` 已补充真机结果；`TELEOP_TUNING_LOG.md` 的 T-03 标为通过。下一步：保持参数用于后续任务采集，发现独立问题再做单变量试验。



## 2026-10-15 D-022：录制期 5 分钟超时修正

- **独立复核发现并由主 Agent 复现**：旧方案的 `KeyboardStartEndTimeout` 在真实栈中是死代码；`RealWorldEnv.step` 在外层以 `elapsed_steps >= max_episode_steps` 重写内层的 `truncations`。旧配置两个阈值都是 3000，录制步数不可能先于自 reset 的 elapsed 达到超时。
- **操作者选择方案 1**（`D-022`）：看门狗保留 **3000 步（从 `a` 开始，5 分钟）**；外层 `max_episode_steps` 提至 **3600 步（从 reset 开始，6 分钟）**，留 60 秒启动余量。若按 `a` 前空等超过 60 秒，外层仍可能先收尾。
- **拒绝 `manual_episode_control_only: true`**：`start_end` 不写 `manual_done`，而 runner 在该开关下只以 `manual_done` 判定是否写 demos；启用会令按 `c` 的成功轨迹不落 demos。
- 代码修正：看门狗比较从 `>` 改为 `>=`；加 `Pico._reported` 所有权的显式升级错误；自检工具改为日志缺失时 fail-closed；转换器在整条动作全零时发警告。
- 新增临时验证开关：`RLINF_KEYBOARD_TIMEOUT_STEPS=<正整数>`，默认未设即 3000。以 `=100` 跑一次故意不按 `c` 的试验，约 10 秒可验证完整真机栈应产出 `_fail.pkl`、不写 demos 且日志出现 `timeout`。
- 验证：YAML 外层=3600、默认看门狗=3000；组件单测 17/17；覆盖值=7 时实际注册模式第 7 步产生 `timeout`, `terminated=True`, `truncated=True`, reward=0；非法值被拒（`E-023`）。**完整 RealWorldEnv 真机超时路径仍待验证。**


## 2026-10-15 E-025：真机 100 步看门狗验证成功 + timeout provenance 修正

- **真机验证**：会话日志明确回显 `本次录制超时阈值：100 步`；Worker 于 10:22:56 与 10:23:36 两次记录 `[keyboard] timeout`，runner 均打印 `Episode ended (reward=0.00). Discarded.`。两个 `_fail.pkl` 产生、失败不新增 demos；一次按 `c` 产生唯一 success demos，符合机制。
- **发现并修复**：旧 timeout 分支设 `pre_record=True`，被 `CollectEpisode` 跳过终止帧；故旧 `_fail.pkl` 虽已失败落盘，却缺失 `keyboard_event=timeout` 和 `terminated/truncated`。现改为保留 timeout 终止帧（仿照 `c`），下一次 reset 才清 `recording`。
- **回归**：扩展+缓冲集成测试现覆盖 21 项：timeout 会写 `_fail.pkl`，其最后 info 有 `keyboard_event=timeout`，最后 `terminated=True`/`truncated=True`。修后真机 provenance 仍待下次自然 timeout 复核。
- **启动可观测性**：顶层会话、wrapper、Worker 分别回显实际阈值，避免再发生临时变量未带入而误判。

### 立即下一步（端到端真机验证）

1. 确认机械臂就位、工作区清空、急停在手边
2. 跑一键脚本：`cd /home/modelbest/Project/RLinf-Franka && bash RLinf-Franks/run_pico_session.sh`
   - 第 2 步会只读校验复位点；不一致按提示 `y` 同步
   - 脚本现在会打印 `[信息] KEYBOARD = /dev/input/by-id/...`（自动解析的键盘）
3. 采集时按键盘：**`a` 开始录制** → 按住 grip 做演示 → **`c` 成功结束**（每成功一条计数 +1，共需 20 条）
   - 中途误按 `a` 会中止并丢弃当前缓冲（`a` 是切换键，防抖只有 0.2s）
   - `b` 分段（1.0s 独立防抖）
   - 忘按 `c` 超过 5 分钟会被看门狗自动收尾（该条不给成功奖励、不进 `demos/`）
4. 跑完检查 `demos/` 是否真有 `trajectory_*.pt`，以及 `collected_data/*.pkl` 的 `infos` 里
   是否出现 `pico_position_delta` / `pico_rotation_delta`
5. 转 LeRobot：`RLinf/.venv/bin/python RLinf-Franks/post_process_to_lerobot.py --run-dir <run> --repo-id local/franka-pico-tomato`


### 仍待验证 / 待决定

- **按键端到端**：设备能打开已实测，但真实按键 a/b/c 的抓取还没验证
- **保底超时阈值**：建议 `max_episode_steps: 3000`（5 分钟 @10Hz），需与 `TrajectoryAccumulator(max_episode_length=...)` 一致
- **`num_data_episodes: 20`**：启用键盘后必须按 20 次 `c` 进程才退出
- **安全盒当前等于无保护**（±2 m / ±114.6°）：末端可被指令到桌面以下；z 下限建议收回到 `0.01~0.03`
- **夹爪真实开合**：通道确认是好的，但真机开合尚未在「按住 grip」姿势下验证过
- **末端能降到多低**：需实测「贴桌面位置 + 1cm」再定 `ee_pose_limit_min[2]`
- **相机取景**：落盘 128×128，操作中末端是否始终在画面内未确认
- **是否把腕部相机接进采集**：`camera_serials` 目前只指向 ZED 2i；ZED-M 现可作为第二视角
  （LeRobot 侧对应 `wrist_image` / `extra_view_image-N`）→ 待操作者决定（与 `Q-006` 相关）
- **ZED 2i 的 UVC 报错**：`Non-zero status (-71)` 出现 3 次，时间点与采集启动吻合，低频，暂判无害但需观察
- **E-013 待真机确认**：新速度手感（配置已被操作者进一步改到 1:1）

## 2026-10-14 会话：数据采集链路收尾准备（键盘 episode 控制 + 数据链路全面查证）

- 目标/任务：推进数据采集链路收尾（`T-005`）；操作者选定 B 方案（官方 `start_end` 键盘包装器）并先对齐细节
- **操作者决策**：
  - 触发器用**最普通的薄膜键盘**；旁边找人帮按键
  - **接受 episode 由键盘决定**，但要求**保底最大时长**（防忘记按键）
  - **接受录制期间一直按住 grip**
  - **数据两阶段交付**（`D-021`）：采集期落信息丰富的 pickle → 后处理转**标准 LeRobot**（schema 不变）
- **查证结果**（全部源码实证，见 `RS-007`）：
  1. **官方配置注释与源码不符**（`A-009`）：`realworld_dual_franka_collect_data_pico.yaml:67-70` 的
     `a=failure/-1`、`b=neutral`、`c=success/1` 描述的是 **`single_stage`**，不是 `start_end`。
     `start_end` 实际是 `a`=开始/中止录制、`b`=分段、`c`=成功结束
  2. **`start_end` 无条件覆盖终止标志**（`start_end.py:51-53`）→ `max_episode_steps` 对它无效
  3. **`demos/*.pt` 的 actions 是真实动作**：`collect_real_data.py:137-160` 用 `info["intervene_action"]`
     覆盖；这解释了历史观测到的 `max|a|=0.92`，也说明 B 方案顺带修好了动作字段
  4. **`export_format` 支持 `"lerobot"`**，且 lerobot 分支同样用 `intervene_action` 覆盖 action；
     但 feature schema 封闭（`writer.py` 固定 state/actions/done/is_success/intervene_flag/segment_id/image/extra_view）
  5. **`segment_id` 在 pickle 通道被丢弃**（`A-010`）：缓冲层有 `segment_ids`，但 `_flush_episode` 的
     episode_data 只挑 11 个键 → 现在按 `b` 分段等于没接上
  6. **`states` 19 维之谜解开**：`FrankaEnv.TRANSFORMS=("RelativeFrame","Quat2EulerWrapper")` +
     `real/env.py:283` 按**字母序**拼 `sorted(state)` →
     `gripper_position(1) + tcp_force(3) + tcp_pose(6，相对复位点且已转欧拉) + tcp_torque(3) + tcp_vel(6，EE 系)`。
     实测特征全部吻合（idx0 恒定 = 夹爪没动、idx13-18≈0 = 静止）。**`intervene_action` 也是 EE 系的**
  7. **保底超时可行**：`RLINF_EXT_MODULE` 在每个 Worker 启动时加载（`worker.py:395`），
     `KEYBOARD_MODES` 是模块级可变 dict → 扩展可注册新模式，**不改 RLinf 源码**
  8. **数据丰富化的唯一入口**：`Pico._reported(reading)` 是 pico info 的唯一出口，`CollectEpisode` 原样搬运
     → 加字段即落进 pickle。但 `FrankaEnv.TELEOP` 写死、`Pico.from_config` 硬编码，注册新设备名要动 2 处
- **权限打通**（操作者执行 sudo）：
  - 根因查实：`evdev.list_devices()` 默认 `writable=True`，只返回可读**且**可写的设备 → 权限不足时返回 `[]`
  - `setfacl -m u:modelbest:rw /dev/input/event*` 已生效：**0/15 → 15/15 可读**，`list_devices()` 返回 15 个
  - **发现 2 台键盘类设备**：`event14` = `BRLTTY 6.4 Linux Screen Driver Keyboard`（盲文驱动的虚拟设备）、
    `event9` = `Dell KB216 Wired Keyboard`（真键盘）→ **必须** `RLINF_KEYBOARD_DEVICE` 钉住
  - 实测：钉住 → `KeyboardListener` 打开成功；不钉 → 如预期 `RuntimeError` 并列出两个候选
- **相机**（`A-011`）：
  - `/dev/video0` 与 `/dev/video1` **同属 ZED 2i**（父设备都是 `2-3.2.1:1.0`）；`video1` 无采集格式
    （`Device Caps 0x04a00000` = metadata）→ **不是第二个图像流**
  - **确实有第二台**：`1-8.1  id=2b03:f681  ZED-M Hid Device  序列号=13482374`（与 ZED 2i 的 `OV0001` 不同）
  - 但它**只枚举 HID 接口**（`bNumInterfaces=1`），**视频端 `f680` 从不出现**；
    挂在 `1-8`（`2109:2211 USB2.0 Hub`）→ root hub `usb1`（480 Mbps）
  - 操作者换过口（`1-4.1` → `1-8.1`），**仍在 USB 2.0 hub 下，未解决**
  - 建议：移到 bus 2 的 USB 3.0 口（`2-3.x`，与 ZED 2i 同族）
  - 顺带：ZED 2i 的 UVC 有 3 次 `Non-zero status (-71)`，时间点与采集启动吻合
- **今天的数据产出**：15:54 / 16:08 / 17:08 三次运行共 **12 条 episode**；
  实测 16:08 那批：`main_images` (128,128,3) uint8 非黑像素 92%+、`states` 19 维、
  `intervene_action` 有效步 161/225/264/21（第 4 条基本是废数据）、夹爪动作 0~2 次
- **配置注释更新**：`pico.position_scale/rotation_scale` 的注释已按实际值（1.0/1.0）改写，
  并说明这两项只改灵敏度、不改速度上限（franky `max_step`/`max_step_rad` 才是硬上限）
- 记录：`A-009`、`A-010`、**`A-011`（resolved）**、`RS-007`、`D-021`、`Q-006`、`E-018`；`T-004` 收尾、`T-005` 建立并开始（`R-005`）
- **相机问题已闭环**（`A-011` resolved）：两台相机同时可用，且用互换端口的对照实验**排除了操作者提出的"主机供电跟不上"假设**
- 未完成：修正后的 timeout 终止帧 provenance 需在下次真实超时中复核；安全盒/z 下限、相机取景仍待独立安全与质量确认
- **实现落地（操作者批准后）**：
  1. `rlinf_ext/collection.py`（新增）：`KeyboardStartEndTimeout` 看门狗（3000 步）+ `register_keyboard_timeout_mode()`
     + `install_rich_pico_info()`（包 `Pico._reported`，加 `pico_position_delta` / `pico_rotation_delta`）
  2. `rlinf_ext/__init__.py`：`register()` 三件事一起做
  3. 配置：`keyboard_reward_wrapper=start_end_timeout`、`max_episode_steps` 300→**3000**、
     `max_num_steps` 300→3000、`camera_serials` 加 ZED-M、`camera_names` 加 `wrist`
  4. `run_collect_pico.sh`：自动解析键盘设备（排除 BRLTTY、优先 by-id）并 export `RLINF_KEYBOARD_DEVICE`
  5. `post_process_to_lerobot.py`（新增）：pickle → 标准 LeRobot（复用 RLinf 的 `LeRobotDatasetWriter`）
- **实现期修掉的两个自己的 bug**：
  - `getattr(staticmethod对象, attr)` 不转发到 `__func__` → 幂等检查失效、`register()` 重复调用会重复包装
  - `start_end` 按 `c` 后故意保持 `_recording=True`（为保住终止帧）→ 原实现会在 `c` 之后继续计数、3000 步误触发超时
- **验证证据**（`E-020`）：扩展单元测试 17/17；配置 YAML 解析 + 相机路径存在；脚本 `bash -n` + 解析块实测；
  转换器用 17:08 那批真实数据跑通（1200 帧、逐 episode 300 帧、**与源 pickle 逐像素最大差 0.000000**、
  `actions max|a|=1.3780` 证明取的是 `intervene_action`、LeRobot 官方 API 可加载）
- 仍未验证：端到端真机（`demos/*.pt` 产出、rich info 落盘、多相机 `extra_view_image`、看门狗真实超时）
- 下一步：见上方「立即下一步」

## 2026-10-14 vr_data_publisher 修复 + 独立复核结果回填

- **`pico_software/vr_data_publisher.py` 修 3 处**（该文件在 `pico_software` 仓库里是**已跟踪**文件，改动后仓库变脏）：
  1. **默认配置路径算错**：`parents[2]` → `parents[0]`。原值解析到 `/home/modelbest/Project/configs/vr_bridge.yaml`（不存在），
     会静默回退到内置默认值 —— 即"改 yaml 不生效"。真实路径是 `pico_software/configs/vr_bridge.yaml`。
     **实测确认**：不带 `--config` 运行时日志现在打印 `Loading config from .../pico_software/configs/vr_bridge.yaml`。
  2. **`buffer_size` 是死键**：yaml 里有但代码从不读（`set_hwm(10)` 硬编码）→ 改为读 `config["buffer_size"]`。
  3. **文件头 docstring 是上游样例残留**（写着 Python 3.10 + ROS Master + `robo_avatar.vr_teleop` 模块路径）→ 改写为真实说明。
- **实测顺带发现文档漏项**：PC Service 有**两个**端口 —— `63901/TCP` 给头显从局域网连入，
  `60061/TCP` 仅 127.0.0.1 供本机 SDK 走 gRPC 读数据。`PROJECT_OVERVIEW.md` 原来只写了 63901，已补上 60061。
- **另一条实测事实**：`xrt.init()` 在 PC Service **未监听**时依然返回成功（打印 `VR SDK initialized successfully`），
  之后照常 80 Hz 推全 0 —— 这从机制上解释了为什么"发布器自己发现不了设备没连上"。
- **独立复核结果回填**：复核子 Agent 报告**无 shell 权限**（`Permission denied: shell`），只能静态读文件，
  6 项"无法判定"里有 5 项是本 Agent 已实测过的。它抓到 1 处真错（运行次数 8/10 → 实际 **11**），
  但它自己关于 `demos/` 目录数的结论是错的（称仅 1 个，实为 **10 个**）。
  已记为框架摩擦 **P8**（`VIBE_FRAMEWORK_FRICTION.md` + `A-008`）。
- **框架源码优化已交付并推送**（`A-008` 的 P0-a/P0-b/P1-a/P2-a + skill 文档漂移）：
  仓库 `~/Project/vibe-coding/vibe-coding` 提交 `8db39f7` + `b1876e5`，已 push 到 `origin/opencode-simple`，
  测试 390 全绿（改动前 378），已用 `install.sh update` 安装到本机运行时（安装态与源码字节一致）。
## 2026-10-13 会话（晚四）：A-006 真机确认 + reset_ee_pose 解耦（方案 A）+ 提速

- 目标/任务：① 真机确认旋转修复；② 处理 `reset_ee_pose` 与姿态安全窗口的耦合；③ 提高遥操作速度
- 结果：
  - ① **旋转已修好并真机确认**（`E-011`）：操作者报告「测试成功，现在姿势可以旋转」；
    硬证据是 Ray worker 日志里的 `rot_clip=[0.15 0.15 0.15]`（对照改动前 `[0.02 0.02 0.02]`）
  - ② **方案 A 已实现并静态验证通过**（`D-020` / `E-012`）
  - ③ **提速已改**（`E-013`，candidate）：`position_scale` 0.4→0.7、`action_scale[0]` 0.02→0.03
- 踩到并修掉的问题（详见文档 7.27）：
  1. **姿态窗口静默偏心**：操作者按 `y` 同步位姿后，窗口仍以旧复位姿态为中心 →
     复位点到 rz 上沿**只剩 5.6°**，表现和 7.26 一模一样（**第二次**中招，第一次是 10.7°）。
     当场手工重新居中，随后才动手做方案 A
  2. **`replace_vec` 正则吞空行**：`[.*]\s*$` 里的 `\s*` 会连同换行吃掉字段后的空行。
     原版只写 `reset_ee_pose`（其后紧跟注释行）所以没暴露；重写后写三个字段即被自写的
     行数不变量单测抓到。改为只匹配水平空白
  3. **`describe_window` 签名不一致**：收 3 元复位姿态却收 6 元窗口，测试时踩 `IndexError`；
     统一为三个参数都收 6 元
  4. **居中判定标准不精确**：最初用「余量 ≥ 半宽的一半」这种比例代理；改为直接判
     「窗口中心与复位姿态的偏差 ≤ 0.1 rad」，与 `--apply` 维护的不变量语义一致
- 顺带确认的事实：
  - `move_tcp_pose` 的 `max_step=0.03 m/次`（10Hz → **0.3 m/s**）是平移的**硬上限**，
    故 `action_scale[0]=0.03` 已到顶；要再快须在硬件配置 `compliance:` 段覆盖 ——
    该字段走 `CartesianCompliance.from_config`（接受 dataclass 全字段），
    但**不**走 env 的 `compliance_param`（`reconfigure` 只读刚度/零空间/裁剪）
  - 机械臂 worker 的日志落在 `/tmp/ray/session_latest/logs/worker-*.out`，**不一定**进
    `run_embodiment.log`（后者这次只写到 5833 字节、停于硬件配置段）
  - 复位点跑出位置盒 = **自走风险**：`reset` 不走安全盒（`base.py:271/594`），
    但 `step()` 每步都裁（`base.py:389`）→ 即使不动手柄也会朝盒边界走（受 franky 限速）
- 记录：`A-006`（rev 2）、`D-019`、`D-020`、`E-011`（因配置 hash 变化转 stale）、
  `E-012`（valid）、`E-013`（candidate）；文档新增 **7.27** 并同步阶段表/参数表/第 8 章
- 未完成：新速度的真机手感；真实机械臂上由操作者走一遍 `--apply` 写入路径
- 下一步：见上方「立即下一步」

## 2026-10-13 会话（晚三）：一键脚本实测通过 + 旋转迟钝根因定位与修复

- 目标/任务：① 确认一键脚本；② 排查「末端平移跟手但旋转迟钝」
- 结果：① **操作者实测通过**（`run_pico_session.sh` 可正常启动与关闭，补齐 E-010 未验证项）；
  ② `A-006` 根因定位并修复（`D-019`），静态验证通过，**待真机复测**
- 先回答操作者的两个问题：
  - **不是 IK 问题**：本机**没有显式 IK**。RLinf 只下发笛卡尔设定值，笛卡尔→关节的换算由 `franky` 的
    `CartesianImpedanceTracker`（libfranka 长驻笛卡尔阻抗会话）在控制层内部用机器人模型/雅可比完成；
    1kHz 控制环在 libfranka 侧，RLinf 以 10Hz 更新目标
  - **是 SDK 控制**：RLinf Python → `franky`（libfranka 的 Python 封装）→ FCI → 机器人本体
- 根因：笛卡尔阻抗的 `error_clip`（语义 = *largest error acted on*，`tau = K_r * clamp(error, ±clip)`，**硬上限**）
  在旋转方向严重不足。**实测生效值**（`--cfg job` 组装 + franky 的 cap/floor 规则）：
  - 平移：`K_t=1200 N/m`（yaml 给 2000，被 `stiffness_cap` 截断）、`trans_clip=[0.005, 0.005, 0.01] m`
    （yaml 给 0.003，被 `clip_floor` 抬高）→ **6~12 N**，远超所需
  - 旋转：`K_r=80 Nm/rad`（yaml 给 150，被 `rotational_stiffness_cap` 截断）、`rot_clip=0.02 rad`
    （正好等于 `rotational_clip_floor`）→ **仅 1.6 Nm**，低于腕部重力+摩擦阻力
- **一个重要的自我更正**：最初用 `franky.default_compliance()` 推断（K_r=50 / rot_clip=0.04 / 2 Nm）是**错的**。
  Hydra 的 `override_cfg` 是**合并**语义，基础 env 配置 `env/realworld_franka_sft_env.yaml` 自带的
  `compliance_param` 会静默生效。核实生效值必须用 `--cfg job`。已更正 `A-006`（rev 2）并改写文档 7.26
- 修改（`D-019`，均在 `env.eval.override_cfg` 下）：
  1. `compliance_param`: `rotational_stiffness: 80.0` + `rotational_clip_x/y/z: 0.15`
     → 最大旋转力矩 **1.6 Nm → 12 Nm（7.5 倍）**
  2. `ee_pose_limit_min/max` 的**姿态部分重新居中到复位姿态**（窗口尺寸不变，仍 ±0.5/±0.5/±0.6 rad）。
     原窗口中心是旧的 `target_ee_pose[3:]`，复位点到 rz 上沿只剩 **10.7°**，一转手腕就撞窗 —— 这是第二个独立天花板
  3. `pico.rotation_scale` **故意保持 0.4 未改**：属灵敏度偏好而非缺陷，先隔离变量验证根因
- 静态验证证据：YAML 解析 ✅；`--cfg job` 组装结果正确 ✅；模拟 franky cap/floor 得 12 Nm ✅；
  `FrankaEnvConfig(**override_cfg)` 构造成功 ✅（与 `base.py:202` 同一行）；姿态窗口余量重新对称
  （rx/ry ±28.6°、rz ±34.4°）✅
- 生效判据：启动日志出现
  `Compliance: K_t=1200 (cap 1200), K_r=80.0 (cap 80.0), K_ns=..., trans_clip=[0.005 0.005 0.01], rot_clip=[0.15 0.15 0.15]`
- 记录：`A-006`（更正到 rev 2）、`D-019`；文档新增/改写 7.26 并登记进 7.0 索引
- 未完成：真机复测旋转是否跟手；12 Nm 是否偏大/偏小
- 下一步：见上方「立即下一步」

## 2026-10-13 会话（晚二）：首次真机闭环遥操作 + 启动链路成文

- 目标/任务：让操作者真正能用手柄驱动机械臂
- 结果：**成功**。按住 grip 后机械臂实际移动 11.2cm（`[0.5236,0.0888,0.3377]` → `[0.5763,0.0043,0.2865]`），
  `demos/*.pt` 记录到 124 步中 17 步非零动作，安全盒生效（E-008）
- 期间解决/发现的问题：
  1. **`Unsupported BaseCamera backend 'zed_uvc'`**（Cluster 初始化即失败）→ 用官方 `disable_validate: true` 绕过，不改 RLinf 源码（`D-015` / `A-003`）
  2. **`collected_data/*.pkl` 的 actions 全为 0** → RLinf 包装顺序导致，真实动作在 `infos[i]["intervene_action"]`；已记录 `A-004`，交付改用 `demos/`
  3. **末端只能下降 5cm** → 根因是安全盒 z 下限 `0.2877` 正好卡在起点下方 5cm；已放宽（`D-016`）
  4. **`A`/`B` 按了没反应** → 代码确认按键**只在按住 grip 时**才被读取（`transports/pico.py:293`）；探针实测通道正常（文档 7.23）
  5. **"机械臂死活不动"** → 发布器不恢复设备断连，一直推全 0；已记录为文档 7.22，并明确"发布器重启后必须重启 RLinf"（ZMQ `connect()` 与 socket inode）
  6. `enable_camera_player` 默认 True 导致 `cv2.imshow` 报错 → 置 `false`（文档 7.19）
- 操作者反馈并已处理：希望放宽安全盒（"机械臂速度慢，不会出安全问题"）→ 已放宽并记录 `D-016`
- 交付物：`PICO_FRANKA_SETUP.md` 第 6 章**整体重写**为完整启动链路（含站位/标定、启动顺序、失败恢复表、收工关机），并新增 7.22 / 7.23、更新第 8 章安全参数
- 未完成：夹爪真机开合、末端最低点实测、episode 结束信号方案
- 下一步：见上方「下次开机请按这个顺序」与「仍待验证」

## 2026-10-13 会话（晚）：全栈干跑打通

- 目标/任务：执行第一次全栈干跑（不戴头显），验证除机械臂运动外的整条链路
- 已完成内容：
  1. 干跑前完整预检：机械臂位姿与配置零偏差；确认首次 reset 不触发关节复位、`go_to_rest` 不移动、step 不发夹爪指令（action=0 < 阈值 0.5）
  2. 第一次干跑失败并定位真因：`ValueError: Unsupported BaseCamera backend 'zed_uvc'`。根因是 RLinf 注册表按进程隔离——`RLINF_EXT_MODULE` 只在 Worker 加载，而节点硬件校验跑在独立 actor `_RemoteNodeProbe` 里，该 actor 从不调用扩展加载函数（记录 A-003）
  3. 采用官方 `disable_validate: true` 绕过，**未修改 RLinf 源码**（决策 D-015）
  4. 第二次干跑通过：300 步 @10Hz、pickle 落盘、相机在 worker 内正常出图、机械臂零漂移
  5. 导出落盘图像为 PNG 目视确认取景覆盖机械臂与工作台
  6. 修掉 `cv2.imshow` 异常（`enable_camera_player: false`）
  7. 文档 `PICO_FRANKA_SETUP.md` 增补 7.18~7.21 与 6.8 小节
- 重要决策：D-015（disable_validate）
- 验证与限制：见 E-007
- 下一步：首次真机运动验证（已在晚二场完成）

## 2026-10-13 会话（早）：环境搭建完成

- 目标/任务：把 Pico 遥操作 Franka 单臂数采环境从零搭起并逐段验证
- 已完成内容：
  1. RLinf `main@50f22ad` 克隆与安装（`--use-mirror`），补装 `lerobot 0.1.0`
  2. 机械臂只读验证：libfranka 会话、`is_robot_up`、TCP/关节状态；确认 franky 四元数为 xyzw 顺序
  3. 相机阻塞解除：ZED 2i 的 UVC 裸流 + out-of-tree 扩展 `rlinf_ext.zed_uvc`
  4. 单臂配置 `realworld_collect_data_pico_single_franka.yaml` 定稿
  5. 启动脚本 `run_collect_pico.sh`（自动设置 `RLINF_EXT_MODULE` 与 `PYTHONPATH`）
  6. Pico 侧：PC Service、`xrobotoolkit_sdk`、publisher、头显连接全部打通
  7. 全流程文档 `PICO_FRANKA_SETUP.md`
- 重要决策：D-013、D-014
- 验证与限制：E-003（机械臂只读）、E-004（相机）、E-006（Pico 链路）
- 下一步：全栈干跑（已在晚场完成）


## 2026-10-13 项目复盘文档交付（T-003）+ 框架摩擦分析

- **T-003-project-overview-doc 已收尾**（`E-014` valid）。交付两份文档：
  - `PROJECT_OVERVIEW.md`（745 行，14 章 + 附录）—— 不读代码即可把握项目全貌：
    目录结构、「我们写的 vs RLinf 上游」职责表、主配置逐段解释、六阶段数据流、
    三层限速与笛卡尔阻抗原理、位置盒/姿态窗口安全机制、产物落点、一键脚本 7 阶段、
    决策摘要、缺陷待办、术语表、**事实来源对照表**。
  - `.project-log/docs/brief-overview-doc-structure-for-gpt.md`（124 行）—— 可整段复制给 GPT
    索取「文档结构方案 + 信息采集清单 + Skill 设计方案 + 初稿评审」；后续拟固化为 Skill。
- **写作中发现并修掉一处会误导操作者的错误指引**（`A-007`）：手册 6.9 原写「认准 `demos/` ✅ 用这个」，
  但 `demos/` 自 `D-016`（reward 恒 0）起**永远为空**。已重写 6.9、新增 **7.28**、加 7.0 的 D 组索引行，
  并修订 7.23 / 8.3 / 第 9 章共 4 处。实测依据：10 次运行仅 `D-016` 之前的 `144414` 产出过 1 条轨迹。
- **数据交付现状（重要）**：唯一有数据的是 `collected_data/*.pkl`；其 `actions` 恒 0（`A-004`），
  真实动作在 `infos[i]["intervene_action"]`（实测 `max|a|≈1.0~1.3`，可无损还原）。
  想让 `demos/` 产出需挂 `keyboard_reward_wrapper: "start_end"` **且**解决 evdev 权限
  （当前用户不在 `input` 组，`evdev.list_devices()` 返回 0 个设备）→ **属待决定事项**。
- **框架摩擦分析**（`A-008` + `VIBE_FRAMEWORK_FRICTION.md`）：一次文档任务 55 次工具调用中，
  真正产出交付物的只有 2 次（4%），36% 花在框架记账上，而其中 14 次是逆向猜 CLI 的 JSON schema。
  写入动作本身只花 2 分 59 秒（账本实测）→ **瓶颈是可发现性，不是仪式**。
  已提 7 条改造建议（P0：`--help` 打印 `covers`/`version_binding` schema、`record show` 免 `--kind`）。
  另记录两条 Agent 自身失误：**P6 越权复核**（standard 风险不需要独立复核，我自行升级）、
  **P7 未询问就扩大范围**（9 次调用挖 `demos/` 根因）。
- **独立复核子 Agent 已启动但结论待回**（在操作者提出"复核没必要"之前启动）—— 其结论若指出文档事实错误，
  按 `E-014` 的 file_hashes 判定失效后修订。

