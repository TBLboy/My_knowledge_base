# Transformer–Koopman Vibe V2 项目进展

## 当前状态

- 2026-11-09 全文公式版式审稿：按“对齐基准数/悬挂续行/跨行断式/标点一致性”扫描 68 个显示公式，只改版式不改内容。修复 (35)(42) 在 LHS 后硬断行导致 `≤` 失对齐、(40) `&\quad+` 续行、(38) 句末缺句号；附录 C 三处 `&\quad+` 与 (57) `\quad(i\ge2)` 同步统一。两次编译 exit0，0 Overfull，10 页，61 个公式编号不变（源码 SHA256 `B5FA8EF6…CFC1`，PDF `F38CAA22…1966`）。未提交推送。
- 2026-11-09 (31) 版式重构：目标函数合并为一行，`W_k=` 移出显示式改为正文定义，`min`/`s.t.` 右对齐共享一列，目标与三条约束共用同一左边缘；消除原来的三左边缘阶梯与 `+β` 悬挂缩进。两次编译 exit0，0 Overfull，10 页，61 个公式编号不变（源码 SHA256 `EC156111…D85F`，PDF `DB55E385…B247`）。未提交推送。
- 2026-11-09 (31) 决策变量修正：`\min` 由 `U,p_{1|k},...,p_{N|k}` 改为仅 `U`，保留初值/递推/输入约束三条；随后段落改为“递推约束由 U 确定预测状态，消去后得 condensed QP”。数学等价（每个 U 的预测状态唯一），编号/定理不变。两次编译 exit0，0 Overfull，10 页；源码 SHA256 `12B4CEEA…099B`。**Main.pdf 被阅读器占用未能写回**，构建产物见 `opencode/eq31-argmin-20261109/Main.pdf`。未提交推送。
- 2026-11-09 (29) 版式微调：改为 `align` + `\intertext{where}`——首行并排初值与递推并带编号，`where` 独立续句行，次行 `M_{i|k}` 3×3 矩阵与 `D_{i|k}` 并排且不编号；块高由四行降至“一行主式 + 一行系数”。两次编译 exit0，0 Overfull，5 Underfull，10 页，61 个公式编号不变（源码 SHA256 `D3A82D8A…36A3`，PDF `C51BD27F…7A30`）。未提交推送。
- 2026-11-09 (28) 版式微调：将两行 `aligned` 的标称 rollout 改为单行 `\bar q_{0|k}=q_k^E,\ \bar q_{i+1|k}=F(...),\ 0\le i<N`，与 (29) 矩阵块形成紧凑对照；源码其余部分与附件逐字一致，61 个公式编号不变。两次编译 exit0，0 Overfull，5 Underfull，页数 11→10（原末页仅剩参考文献 [26]，现已并入第 10 页），PDF 已写回（源码 SHA256 `D531936F…DB35`，PDF SHA256 `7D59BDB6…6BB0`）。未提交推送。
- 2026-11-09 第四章 IV-A/IV-B 应用用户外部精修稿 `Main(10)_Eq28-29_refined.tex`（用户明确要求完全按附件覆盖）：Eq (28)(29) 改为逐行 aligned 版式，Algorithm 1 改 `[!t]`，IV-A 各段压缩、IV-B 开头合并为一段，并删除上一轮的 direct full-model MPC 基准段。84 个 label、61 个 eq 标签与编号不变，引用全部可解析（新增 `eq:tail_decrease` 在附录已存在）。两次编译 exit0，0 fatal/undefined/Overfull/缺字、6 Underfull，11 页，PDF 已写回（源码 SHA256 `BA955A45…2E69`，PDF SHA256 `67F41BC2…0034`）。替换前稿备份在 opencode 临时目录；未提交推送。
- 2026-11-09 第四章 IV-A 叙事追加精修：在 single-freeze 方案前增加不编号的 direct full-model MPC 基准优化问题，先展示直接使用完整 history-conditioned predictor 的自然控制图景，再用 However 说明候选输入同时改变预测状态/历史调度矩阵导致非线性，最后用 To retain 引出 single-freeze；随后接现有 nominal rollout、冻结模型、(28)–(31) 和算法。前轮蓝色已恢复黑色，仅本轮新增内容重新标蓝；第三章、IV-B、附录、代码、实验和图片未改。两次编译 exit0，0 fatal/undefined/Overfull/缺字、5 Underfull，61 个公式编号不变，PDF 已写回。记录见 `.vibe/docs/chapter4-revision-log-20261109.md`，Task `20261109-iv-a-direct-mpc-structure` 完成，未提交推送。
- 2026-11-09 第四章第三轮（按用户新精修指南）：先按匹配分组清除全稿42处蓝色（文字/公式/引用保真），再只改Section IV并重新标蓝。IV-A开头承接第三章预测器→说明直接优化非线性→引入single-freeze；bar U_k一次交代为冻结系数来源而非决策变量；参考与代价分两段；保留完整约束问题(31)并一句定义J_k^fr(U;bar U)、U_k^*、W_k；凸性压缩为两句但仍以输入缓存机制论证；删除N=1与"唯一来源"重复；Algorithm 1拆Given/Initialize、保留双层循环与单次QP。IV-B开头改为跨采样重冻结的比较论证；Assumption 1前补统一界动机、其后精简解读；Assumption 2去掉悬空where从句并保留四条件；终端权重按三步逻辑并一句过渡到附录预算。仅(38)去掉句末句号，61个编号与标签不变；第三章及之前、第五章/结论/附录/导言区逐字未改。两次编译exit0，0undefined/Overfull/缺字、5Underfull，PDF已写回。修改记录：.vibe/docs/chapter4-revision-log-20261109.md；Task 20261109-chapter4-guide-revision完成；未提交推送。
- 2026-11-09 第四章第二轮精修（按IV-A任务书审核后执行）：IV.A把(31)改写为含U与p决策变量的完整有限时域问题，显式给出初值/冻结动力学/输入约束，并说明消元等价、U_k^*/W_k/J_k^fr(U;\bar U_k)分工、标称精确复现p_{i|k}(\bar U_k)=\bar q_{i|k}、非一阶线性化、输入缓存驱动的严格凸性机制与Q为分析域；Algorithm 1加预测时域内层循环并置于[!b]。IV.B仅做五处精确化（W_k指(31)最优值、冻结半径指bar_eta、冻结映射来源、可行性对应(31)约束集、J第二自变量）。明确未采纳“参考精确可实现”“Pi>0推出凸性”“新增终端集合”等建议。控制律/代价/误差界与61个公式编号不变，前文/实验/图片/代码/附录A/C未改，新改标蓝。两次编译exit0，0undefined/Overfull/缺字、5Underfull，PDF已写回。Task：20261109-ieee-control-refinement完成；非数值/硬件认证，未提交推送。
- 2026-11-09 第四章第一轮精修：IV.A按名义rollout→冻结模型→参考/成本→QP→施加/移位组织，U/Ez/Eprev就地定义，u^r_-1补为给定参考初始化数据，删除占位图不存在分支的描述；IV.B压缩动机、理顺假设与证明，以投影推论证明收尾。N=1、空和及精确参考尾部权重说明迁至附录B三处句子。
- 2026-11-09 用户要求将当前稿全部蓝色恢复黑色，19处匹配分组已清除，文字/公式/引用及61个公式编号保真；两次编译exit0，0undefined/Overfull/缺字、6Underfull，Main.pdf已更新。第四章只读优化方案见`.vibe/docs/chapter4-edit-plan-20261109.md`，控制正文尚未优化；特别记录参考序列定义始于t=0但(30)/(37)使用未明确给定的u^r_{-1}，以及空白总览图与IV.A“lower branch”指向不符。后续按用户确认方案局部改写，不自行改变控制律/理论条件或选择参考初始值。Task：20261109-black-baseline-control-plan完成，未提交推送。
- 2026-11-09 按用户后续决定取消集中符号表：Main.tex删除Notation与表I，仅在II.A/III.A/III.B/IV.A就地补充col、diag、二范数、Pi加权范数、R/S二次型及Kronecker积说明；保留两阶段训练和统一预算。所有独立公式及61个eq标签编号不变。重新编译两次exit0，0undefined/Overfull/缺字、6Underfull，Main.pdf已写回（SHA256=7877606935F8FD0041A24BE257D317DEE10BF77E3FE4E93DD74E9A6FE9C66634）。Task 20261109-inline-notation完成，未提交推送。
- 2026-11-09 用户批准的III.B训练协议已写入Main.tex：两个损失删除sg、编码器两侧联合求导；阶段一学习Schur A0/B0及lift，阶段二固定A0/B0/M0/Pi及gA/gB，训练lift/context/factors/heads并维持列范数<=1、统一bar_kappa/bar_Lc预算。附录A同步kF与统一界证明；最终残差与实测初始化入域仍独立。引言末尾新增分组符号表（PDF第3页），Ez定义移至IV.A；旧蓝转黑，新改标蓝。第二章、模型F、控制律/闭环定理、附录B/C、实验图片代码未改。最终两次编译exit0，0undefined/Overfull/缺字，7Underfull，PDF已写回并核看版面。Task：20261109-training-notation-budget。仅论文协议落地，不是数值认证或训练完成；代码后续对齐，未提交推送。
- 2026-11-09 按用户批准的理论先行方案，Main.tex II.B预测任务H_p统一为MPC时域N>=1；III.B保留训练长度H_R并明确H_R=N；调度分支索引H改为chi（含通用导数界下标），IV.A沿用II.B时域。新增修改标蓝，P_h、p、公式标签和证明不变。两次Tectonic离线编译exit0，0undefined/Overfull/缺字、6Underfull，PDF已写回。暂时代码未改，需理论定稿后对齐；本轮未提交推送。
- 2026-10-22 Introduction按用户完整指定文本替换（实际差异为历史调度定位段及本文方法概述段）；引言外全文和所有cite命令保持不变。改前稿归档至论文/新版本/杂项/历史版本/20261022-before-intro-user-version/。两次Tectonic编译exit0、0undefined/Overfull/缺字、7Underfull，Main.pdf已更新；strict审查ses_e9d0a33f4ffe8vuG3iyQCnUEUU为go。
- 2026-10-22 现行Main.tex的III.A已按老版本4.1（Temporal Lifting and Low-Rank Transition，源253–344行）恢复逐段及独立公式顺序，保留现行B(x)调度、列向量历史、q/F/w接口；本轮III.A外源码逐字未变，图片/实验/代码未动。改前Main.tex/PDF归档至论文/新版本/杂项/历史版本/20261022-before-3a-old41/。两次Tectonic离线编译exit0，0undefined/Overfull/缺字、7Underfull，PDF已更新；strict审查ses_e9d2246a6ffe3KNlwLny6mwvlH为go。非模型实例或实验认证。
- 2026-10-19 已切换到 Vibe V2 项目控制面；当前正式项目记忆为本目录 `.vibe/`，不再使用旧 `.project-log` 活动写入。
- 旧 `.project-log` 已保留为 `.project-log.backup-20261019-141848/`；备份清单与哈希在 `.vibe/backups/20261019-141848/manifest.json`。
- 真实代码仓库为内层 `Transformer-Koopman/`，当前分支 `paper`，最近已推送提交 `d6af529`。论文、代码、实验、图片未因本次初始化被修改。
- 当前理论：原 B1 与收缩型 Frozen-QP V2 都是研究性候选；V2 经过条件静态审查但尚未采纳、实施或认证当前模型/plant。P5 STOP。
- 2026-10-19 V3理论先行设计研究完成：`V3_Theory/V3_Executive_Gate_Report.md`集中导航七份产物，A阶段双独立审查go，B/C/D最终strict审查go（`ses_eacf51648ffeDU2niyRWBLWus5`，一轮LaTeX依赖修补后无required finding）。给出可构造非零历史调度模型类、单次Frozen-QP契约、条件闭环值下降/实际指数跟踪和误差半径。
- V3总GO仅表示条件理论可作后续实施依据：不认证当前checkpoint、真实plant、现有controller或实时性，不改变原B1 OPEN/旧P5 STOP；Main.tex、代码、实验/图片和历史报告未改。无TeX编译器，仅静态语法/标签环境检查，候选片段未编译。
- 2026-10-19 用户另行授权六章论文重写，独立候选已完成：`Transformer-Koopman/论文/新版本/Main_SixSection_TheoryRewritten.tex`及同名9页PDF，另有`Paper_Rewrite_Change_Summary.md`与`Paper_Consistency_Check.md`。正文六章、II/III/IV各两小节，III.B收缩构造命题、IV.B实际single-freeze条件闭环定理，三附录；不覆盖Main.tex或修改V3/训练/控制/实验。
- 本轮找到PATH外已有Tectonic0.17.0并用only-cached真实编译成功，最终日志无undefined/overfull/缺字；7条underfull及Fontconfig/缓存算法包注释UTF8警告保留。此前V3片段未编译是历史事实，本次编译对象是新完整候选。最终strict审稿`ses_eac689f66ffezKbn9tgSrnIwTq`返回go、无required finding；reviewer未独立复编/复算哈希。
- 2026-10-19 按多维审稿意见完成独立 R2：同目录 `Main_SixSection_TheoryRewritten_R2.tex/pdf` 与 `R2_Revision_Summary.md`。强化双重历史作用及学习约束/独立残差接口，IV.B 定理前源码98→53行，常数移至Proof/附录而核心值下降链保留；三占位合并成实际源内原理图，DeepKoopFormer更新为官方2026期刊记录。真实首版无附件所述批量转义损坏且复编成功；Main/首版/V3/代码/实验不变。
- R2最终源连续两次Tectonic离线编译退出0，9页，0undefined/Overfull/缺字/字体加载失败，10条Underfull及原环境警告保留；独立strict reviewer `ses_eac2a250bffe0tja2HcQC5lELo` 返回go、findings=[]。reviewer静态复核，编译/版面/哈希和外部元数据采用主Agent实际证据；条件理论边界和第V章无实验结果不变。
- 2026-10-19 R2审稿后的独立R3精修完成：同目录 `Main_SixSection_TheoryRewritten_R3.tex/pdf`、`R3_Revision_Summary.md`。去掉内部证明命名和元叙述，显式给出 `norm(e)^2<=W<=Xi` 及输入推论价值连接，epsilon/比较常数统一附录入口，示例特征系数改alpha_d；六章/控制律/假设不变。最终源两次Tectonic编译exit0、9页，0undefined/Overfull/缺字/字体失败，9 Underfull；模拟Termes缺失的最终源系统Times/Arial回退也编译成功。独立strict审稿 `ses_eabedc5cbffeKrd13cN71e0tcC` go、findings=[]，其构建/版面等采用主Agent证据。仅Tectonic实际测试、Heros未测、系统字体依赖与环境警告仍保留；Main/旧候选/V3/代码/实验不变。
- 2026-10-19 用户确认附件 `Main_SixSection_TheoryRewritten_R3_Refined.tex` 为最终稿，已定稿写入 `论文/新版本/Main.tex`，并生成同目录 `Main.pdf`。原Main、R1/R2/R3候选、审计记录和支持资料未删除，已移至 `论文/新版本/杂项/历史版本/`；根目录仅留最终Main.tex/PDF、IEEEtran.cls和定稿记录。为当前Tectonic/XeTeX补两段pdfLaTeX无操作的条件字体兼容层，正文未改；最终Main两次Tectonic编译exit0、10页，0undefined/Overfull/缺字/字体失败、7 Underfull。strict审稿 `ses_eaba7b750ffexnLxp22qqaCfkV` go、findings=[]；reviewer采用主Agent编译/版面/哈希证据，未独立复跑。

## 稳定约束

- 2026-10-19 用户要求修复引言整体逻辑，已实际读Korda–Mezić/Koopa/MamKO/DeepKoopFormer原引言，重写活跃Main的Introduction为“MPC双需求→Koopman结构/有限近似与输入建模分层→历史信息→递归调度→冻结QP→跨轮tracking→本文设计”链。未改摘要、图及II章起后续全文；阅读/取舍和可审计修改见论文目录`杂项/Introduction_Rewrite_Analysis_20261019.md`，旧Main/PDF已归档。两次Tectonic编译exit0、10页，0undefined/Overfull/缺字/字体失败、6 Underfull；strict审查`ses_eab6dd116ffeBpxBdRJiz8HAVU` go，无finding，外部阅读/构建等采用主Agent证据。最新Main SHA256=db5e665dd642ec9ff00170a3252c517dd301d2090186c804b37b8933ca9e72d1。

- 论文、实验、图片范围按用户明确授权；未授权时默认跳过实验和图片。
- 外部理论设计不得自动改写 `Main.tex`、训练代码、控制器或模型语义。
- 论文写作规则继续保留在根 `AGENTS.md`，其中包括符号、物理/测量/提升状态区分、理论证据边界和实验冻结规则。
- 新任务使用 Vibe V2 Task JSON；不创建旧 Goal、Run、ledger、Evidence 或 SQLite 状态。

## 下一步

- V3理论已整合进独立六章论文候选，当前审阅版为R3；下一步等待用户审阅或指示是否替换正式母稿。未获另行批准不覆盖现行Main.tex、不实施训练/控制代码、不开始真实模型认证或实验。
- 若继续理论，使用现有备份报告作为只读背景，并将新结论写入 `.vibe` 或项目源文档，不恢复旧日志系统。
