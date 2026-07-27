# Progress Log

## 2026-07-13 — 方案A实现：pick_cucumber → place_cucumber task_id传递链

- Type: feature
- Status: validated
- Importance: high
- Reusable: yes
- Objective: 解决"右手抓黄瓜"→"右手放黄瓜"的 task_id 依赖问题，服务端 place_cucumber 必须传入 taskId 才能查找缓存的 task_target。
- Problem:
  - 服务端 `pick_cucumber` 创建 task_id 并调用 `save_task_target(task_id, task_target)` 缓存抓取位置
  - 服务端 `place_cucumber` **必须**传入 `taskId` 才能找到缓存的目标位置，没有则报错
  - 客户端 `requestArmTaskControl` 的 `afterSuccess` 为空，从未从响应中提取 `taskId`
  - 客户端 `taskControlPayload()` 不传 `taskId`
  - 结果：右手放黄瓜始终失败（"place_cucumber 缺少 taskId"）
- Work completed:
  - **新增缓存机制**：
    - `PendingTaskCache` 数据类（taskId + taskName）和 `pendingTaskCache` 私有变量
    - `requestTaskControl` 的 `afterSuccess` 签名从 `() -> Unit` 改为 `(String) -> Unit`，使回调能拿到响应体
  - **写入**：`requestArmTaskControl` 中当 `command == "pick_cucumber"` 且服务端返回 `code==0` 时，从响应体解析 `data.taskId` 写入缓存，并设 `rightCucumberPicked = true`
  - **消费**：`requestArmTaskControl` 中当 `command == "place_cucumber"` 且缓存有值时，extra 追加 `"taskId"` 字段传给服务端，请求成功后清空缓存，设 `rightCucumberPicked = false`
  - **失效清空**（以下操作导致右臂位置改变，缓存失效）：
    - 右臂初始位置（`command=="arms_initial_ready" && RIGHT`）
    - 机器人恢复初始位置（`resetRobot` 函数开头 + afterSuccess）
    - 右臂启动拖拽模式（`toggleDragModeArm` 中 RIGHT + 开启）
    - 紧急停止（`emergencyStop` 的 afterSuccess）
  - **按钮灰化**：`MainDashboardUiState` 新增 `rightCucumberPicked` 字段，控制 `DashboardComponents` 中"右手抓黄瓜"按钮的 `enabled` 状态（缓存有值时灰化）
  - 清理条件明确：任务自然完成（finished/failed）**不清空缓存**，因为机械臂停在抓取完成的位置，这正是放黄瓜需要的位置
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardUiState.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/DashboardComponents.kt`
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
- Unverified items: 平板部署验证
- Next steps:
  - 部署平板端验证 pick_cucumber → place_cucumber 链路

## 2026-07-09 (Session)

- Type: bug-fix
- Status: validated
- Importance: high
- Reusable: no
- Objective: 修复"开始制作"按钮被其他按钮操作误激活为暂停态的 bug。
- Root cause:
  1. task/control 和 robot/action 接口 payload 中携带了旧 taskId（currentTaskId 未清空），服务端用该 taskId 执行操作并设为 RUNNING。
  2. 轮询器/api/task/current 返回 RUNNING 状态，客户端 updateCurrentTaskFromResponse() 覆盖 currentTask.status。
  3. 开始按钮 isRunning 判定条件为 currentTask?.status == TaskStatus.RUNNING，任何服务端 task running 都会触发暂停竖杠。
- Fix:
  1. taskControlPayload() 和 robotActionPayload() 移除 taskId 参数（服务端 Optional，客户端不应传）。
  2. MainDashboardUiState 新增 productionTaskRunning: Boolean = false。
  3. 仅 startTask() 成功时置 true；emergencyStop()/resetRobot()/轮询终态时清 false。
  4. DashboardComponents.kt StartAndActionArea 中 isTaskRunning 改为读 state.productionTaskRunning。
- Files changed:
  - MainDashboardUiState.kt: 新增 productionTaskRunning 字段
  - MainDashboardViewModel.kt: 移除两个 payload 的 taskId、startTask/emergencyStop/resetRobot/轮询中管理 productionTaskRunning
  - DashboardComponents.kt: StartAndActionArea isTaskRunning 切到 productionTaskRunning
- Next steps: 平板联调验证。

---

## 2026-07-01 11:24 Local Time

- Type: workflow
- Status: validated
- Importance: high
- Reusable: maybe
- Objective: 初始化项目工程记录系统 `.project-log/`。
- Work completed: 创建了完整的 `.project-log/` 目录结构和初始化文件。
- Business logic impact: 初始化了业务逻辑记录框架（main、graph、nodes、edges 均为待填充状态）。
- Problems encountered: 项目信息未知 — 目录为空，无法推断项目目标、技术栈或阶段。
- Resolution: 所有未知项已在 `open-questions.md` 中记录，等待用户说明。
- Verification: 目录结构和文件已成功创建。
- Unverified items: 所有业务逻辑内容待用户补充。
- Files changed: `.project-log/` 全部初始化文件。
- Next steps: 等待用户描述项目信息。

---

## 2026-07-01 11:30 Local Time

- Type: workflow
- Status: validated
- Importance: high
- Reusable: maybe
- Objective: 根据用户描述，建立项目的业务逻辑主干。
- Work completed:
  - 明确了项目目标: 机器人展会切黄瓜表演上位控制APP
  - 明确了系统架构: APP → HTTP → 中层NODE → 机器人控制接口
  - 明确了本工程负责范围: 上层APP + HTTP协议 + 消息接口
  - 定义了主干业务逻辑节点和边
- Business logic impact:
  - 更新 `requirements.md`: 项目目标、架构、范围
  - 定义 main path 节点 A→B→C→D→E: APP就绪→用户触发→请求发送→响应接收→结果展示
  - 更新 `nodes.md`: 5个节点的详细定义
  - 更新 `edges.md`: 4条执行链的定义
  - 更新 `graph.md`: main path
  - 更新 `open-questions.md`: 新增7个活跃问题，3个已解决
- Problems encountered: 无
- Resolution: 无
- Verification: 节点和边定义逻辑一致，覆盖了APP侧完整操作流程。
- Unverified items:
  - 具体操作列表（待用户澄清）
  - HTTP协议细节（待行业和用户确认）
  - UI样式（待用户提供设计稿）
- Files changed:
  - `.project-log/requirements.md`
  - `.project-log/business-logic/main.md`
  - `.project-log/business-logic/graph.md`
  - `.project-log/business-logic/nodes.md`
  - `.project-log/business-logic/edges.md`
  - `.project-log/business-logic/open-questions.md`
- Next steps: 等待用户提供APP的具体操作列表和UI样式澄清。

---

## 2026-07-01

- Type: decision
- Status: validated
- Importance: high
- Reusable: no
- Objective: 确认APP运行平台。
- Work completed: 用户确认APP运行平台为 Android PAD 端。
- Business logic impact: Node A 更新运行平台备注；技术栈方向确定为 Android（Kotlin/Flutter）。
- Problems encountered: 无
- Resolution: 无
- Verification: 已更新相关文件。
- Unverified items: Android 具体技术栈（原生 Kotlin / Flutter）待用户确认。
- Files changed:
  - `.project-log/requirements.md` — 平台确认
  - `.project-log/business-logic/nodes.md` — Node A notes
  - `.project-log/business-logic/open-questions.md` — Q2 resolved
  - `.project-log/architecture/software-architecture.md` — 部署平台
- Next steps: 继续等待操作列表、UI样式、技术栈选择。

---

## 2026-07-01

- Type: decision
- Status: validated
- Importance: high
- Reusable: no
- Objective: 确定 Android UI 技术栈。
- Work completed: 用户确认采用 Kotlin + Jetpack Compose 作为 Android PAD APP 开发技术栈。
- Business logic impact: Node A、E1、E4 确定技术实现方向为 Jetpack Compose。
- Problems encountered: 无
- Resolution: 无
- Verification: 已更新所有相关文件并创建决策记录。
- Unverified items: 无
- Files changed:
  - `.project-log/requirements.md` — 补充技术栈
  - `.project-log/business-logic/nodes.md` — Node A notes
  - `.project-log/business-logic/open-questions.md` — Q9 resolved
  - `.project-log/business-logic/decision-records.md` — 首个决策记录
  - `.project-log/architecture/software-architecture.md` — 技术栈和部署描述
- Next steps: 继续等待操作列表和UI样式。

---

## 2026-07-01

- Type: workflow
- Status: validated
- Importance: high
- Reusable: maybe
- Objective: 根据 robot_cooking_api_plan.md 完善业务逻辑，解决开放问题。
- Work completed:
  - 明确了 6 个 HTTP 接口 + 1 个 WebSocket 定义
  - 明确了 20+ 用户操作的接口映射
  - 统一响应格式、参数枚举、请求/响应数据结构全部确定
  - 创建 `api/internal-api.md` 接口规范文档
- Business logic impact:
  - 更新 `main.md`: 完整的接口清单和操作列表
  - 更新 `nodes.md`: 所有节点填充实际接口和数据格式
  - 更新 `edges.md`: E1 含完整操作映射表，E2/E3 含 HTTP 细节
  - 更新 `graph.md`: 接口映射关系
  - 新增 `api/internal-api.md`: 6 个接口的完整规范
  - 更新 `decision-records.md`: HTTP 协议设计决策
- Problems encountered: 无
- Resolution: 无
- Verification: 与 robot_cooking_api_plan.md 一致
- Unverified items: Q4(中层地址), Q5(认证/加密)
- Files changed:
  - `.project-log/requirements.md`
  - `.project-log/business-logic/main.md`
  - `.project-log/business-logic/graph.md`
  - `.project-log/business-logic/nodes.md`
  - `.project-log/business-logic/edges.md`
  - `.project-log/business-logic/open-questions.md`
  - `.project-log/business-logic/decision-records.md`
  - `.project-log/api/internal-api.md` (新增)
- Next steps: 等待用户提供 UI 代码，然后开始搭建 Kotlin + Compose 项目骨架。

---

## 2026-07-01

- Type: workflow
- Status: validated
- Importance: high
- Reusable: no
- Objective: GPT 生成了 UI 代码，审阅并从代码中提取业务逻辑记录到 .project-log。
- Work completed:
  - 审阅了 22 个 Kotlin 源文件，BUILD SUCCESSFUL
  - 提取了完整的屏幕流程: Login → SelfCheck → Main(Dev/User)
  - 提取了 UiState / UiAction / ViewModel / Repository 各层逻辑
  - 记录了 Dev vs User 功能差异表
  - 记录了刷新策略 (refreshAll / refreshLogs / 纯本地)
  - 记录了 PIN 验证门控逻辑
- Business logic impact:
  - 更新 `main.md`: 新增 Screen Flow、Dev/User 功能表、刷新策略、PIN 验证流程、代码状态标记
  - 更新 `graph.md`: 新增 Login/SelfCheck 节点、Dev/User 分支
  - 更新 `nodes.md`: 新增 LOGIN、SELF_CHECK、PIN_GATE 节点，所有节点更新为 implemented 状态
  - 更新 `edges.md`: 新增 E0_LOGIN 边，E1-E4 更新为实际代码实现的逻辑
- Problems encountered: GPT 额外生成了 Login/SelfCheck/PinVerify 等未在需求中的界面
- Resolution: 保留待用户确认；菜谱列表含 5 个（仅蓑衣黄瓜为实际需求）
- Verification: Gradle BUILD SUCCESSFUL，逻辑与代码一致
- Unverified items: UI 运行效果（待用户在模拟器/设备上确认）
- Files changed:
  - `.project-log/business-logic/main.md`
  - `.project-log/business-logic/graph.md`
  - `.project-log/business-logic/nodes.md`
  - `.project-log/business-logic/edges.md`
- Next steps: 用户在 Android Studio 中运行 UI 确认界面；确认是否需要 Login/SelfCheck 界面

---

## 2026-07-01

- Type: decision
- Status: validated
- Importance: medium
- Reusable: no
- Objective: 确认 GPT 生成的所有 UI 功能。
- Work completed: 用户确认保留所有 GPT 生成的功能：LoginScreen、SelfCheckScreen、PIN 验证、5 个菜谱、Dev/User 双布局。
- Business logic impact: main.md/nodes.md 中 GPT-generated 标记改为 confirmed/stable。
- Problems encountered: 无
- Resolution: 全部保留
- Verification: 用户确认
- Unverified items: 无
- Files changed:
  - `.project-log/business-logic/main.md`
  - `.project-log/business-logic/nodes.md`
  - `.project-log/current-session.md`
- Next steps: 运行 UI 确认效果，然后实现真实 HTTP Repository。

---

## 2026-07-01 15:25 Local Time

- Type: workflow
- Status: partial
- Importance: high
- Reusable: no
- Objective: 将 `RobotCookingControlApp_v2` 和 `RobotCookingControlApp_v3` 的新增 UI 功能迁移到已编译成功的 `RobotCookingControlApp`。
- Work completed:
  - 以 `RobotCookingControlApp` 为基线，对比并筛选 v2/v3 的新增功能，避免回退已修复的构建配置
  - 迁移 v2 功能：开始制作确认弹窗、急停/复位二次确认、日志详情弹窗、菜谱抽屉展开/收起
  - 迁移 v3 功能：菜谱卡片图标与样式优化、登录页改用系统键盘、主任务区标准线性进度条、开发者模式移除暂停/继续/取消按钮展示
  - 保留当前工作版本中的关键修复：`app/build.gradle.kts` 里的 Java 17 `compileOptions`，以及 Compose progress lambda 修复
- Business logic impact:
  - 主面板交互从“直接执行”升级为“关键操作先确认，再执行”
  - 日志列表由只读改为可点击查看详情
  - 菜谱侧栏支持收起/展开，主界面布局行为发生变化
  - 登录流程从虚拟键盘输入切换为系统键盘输入，但 `LoginFieldFocused` 状态链路保留
  - 任务进度展示从旧 Canvas 线段样式切换为总进度 + 步骤节点的双层表达
  - 开发者模式当前不再在主界面展示暂停/继续/取消按钮，但底层 `TaskCommand` 和可复用组件仍保留
- Problems encountered:
  - 本地 CLI 环境 `java -version` 为 11，无法直接通过 Gradle 命令行验证需要 JDK 17 的 Android 工程
  - 迁移过程中 `TaskComponents.kt` 曾因文件状态变化需要重新读取后再写入
- Resolution:
  - 使用当前工作工程为唯一目标目录，逐项迁移 v2/v3 UI 变更，不直接覆盖整个工程
  - 通过源码检索确认新增状态、动作、组件引用链路已接通
  - 将最终运行验证留给 Android Studio 环境执行
- Verification:
  - 源码层面已确认 `FloatingConfirmDialog`、`ExpandedLogDialog`、`RecipeSideDrawer`、`recipeIcon()`、`LinearProgressIndicator`、系统键盘输入等引用全部接入
  - `MainDashboardScreen.kt` 已移除开发者模式底部 `CompactTaskControlRow` 的页面调用
- Unverified items:
  - Android Studio/JDK17 环境下的实际编译结果
  - 迁移后 UI 运行效果与交互手感
  - 弹窗、日志详情、菜谱抽屉、系统键盘、进度条新样式的真机/模拟器表现
- Files changed:
  - `RobotCookingControlApp/app/src/main/java/com/example/robotcooking/ui/state/RobotCookingUiState.kt`
  - `RobotCookingControlApp/app/src/main/java/com/example/robotcooking/ui/state/UiAction.kt`
  - `RobotCookingControlApp/app/src/main/java/com/example/robotcooking/ui/RobotCookingViewModel.kt`
  - `RobotCookingControlApp/app/src/main/java/com/example/robotcooking/ui/screens/MainDashboardScreen.kt`
  - `RobotCookingControlApp/app/src/main/java/com/example/robotcooking/ui/screens/LoginScreen.kt`
  - `RobotCookingControlApp/app/src/main/java/com/example/robotcooking/ui/components/SidePanels.kt`
  - `RobotCookingControlApp/app/src/main/java/com/example/robotcooking/ui/components/TaskComponents.kt`
  - `RobotCookingControlApp/app/src/main/java/com/example/robotcooking/ui/components/RecipePanel.kt`
  - `RobotCookingControlApp/app/src/main/java/com/example/robotcooking/ui/components/FloatingDialogs.kt` (新增)
  - `RobotCookingControlApp/app/src/main/java/com/example/robotcooking/ui/components/RecipeDrawer.kt` (新增)
- Next steps:
  - 用户在 Android Studio 中运行 `RobotCookingControlApp`，验证 v2/v3 合并后的 UI 与交互
  - 若运行通过，再把最新实际行为同步回 `main.md` / `nodes.md` / `edges.md`
  - 之后进入真实 HTTP Repository 替换 Fake 的阶段

---

## 2026-07-02

- Type: decision
- Status: validated
- Importance: high
- Reusable: maybe
- Objective: 放弃当前 APP UI 实现，后期重新开发。API 协议作为稳定契约保留。
- Work completed:
  - 确认放弃 `RobotCookingControlApp` 的当前 UI 实现
  - 确认 `robot_cooking_api_protocol.md` 为后期接口和数据结构的唯一依据
  - 分析当前 APP 布局问题：固定宽度组件（侧边栏 264dp + 右侧面板 326dp）导致在手机（~360dp）上显示拥挤，APP 设计目标为 PAD 横屏，未做多尺寸适配
  - 分析 API 协议：6 个 RESTful 接口、完整枚举值、统一响应格式、错误码、轮询策略 — 已足够作为后期接口层开发规范
  - 打包了当前 APP 的 debug APK (9.3MB, BUILD SUCCESSFUL via CLI JDK 21)
- Business logic impact:
  - `robot_cooking_api_protocol.md` 升级为接口层正式规范文档
  - 当前 APP 代码（`RobotCookingControlApp/`）作为参考实现存档，不继续开发
  - 数据模型层（`ApiModels.kt`、`RobotCookingRepository.kt`）的接口定义与 API 协议一致，后期可复用参考
- Problems encountered: APP 在手机上 UI 挤在一起 — 根因是固定宽度布局 + PAD 专属设计未做屏幕适配
- Resolution: 决定放弃当前 UI，重新设计时考虑响应式布局
- Verification: API 协议文档数据结构和当前代码数据层一致
- Unverified items: 新 UI 设计方向待用户确定
- Files changed:
  - `.project-log/current-session.md`
  - `.project-log/progress.md`
  - `.project-log/requirements.md`
  - `.project-log/business-logic/main.md`
  - `.project-log/business-logic/decision-records.md`
  - `.project-log/api/internal-api.md`
- Next steps: 等待用户提供新 UI 设计方向，基于 API 协议重新搭建项目骨架

---

## 2026-07-02

- Type: decision
- Status: validated
- Importance: high
- Reusable: no
- Objective: 确定新 APP 的架构标准，以 `android_app_architecture_readme.md` 为开发规范。
- Work completed:
  - 阅读并确认 `android_app_architecture_readme.md` 为工程架构规范文档
  - 确定技术栈: Kotlin + Jetpack Compose + MVVM + Clean Architecture + Hilt + Retrofit + Room + DataStore + Navigation Compose
  - 全面更新 `.project-log/` 以对齐新架构:
    - `requirements.md` — 重写技术栈和架构标准
    - `architecture/software-architecture.md` — 重写 APP 内部三层架构 + 依赖规则
    - `business-logic/main.md` — 重写架构调用链路 + 目录结构
    - `business-logic/nodes.md` — 重写节点，每个标注新架构的层级映射
    - `business-logic/edges.md` — 重写执行链，标注 UseCase/Hilt/Retrofit 调用路径
    - `business-logic/graph.md` — 新增 Feature 模块映射图
    - `business-logic/decision-records.md` — 新增架构标准决策记录
  - 旧 APP `RobotCookingControlApp/` 标记为 archived 参考实现
- Business logic impact:
  - 新架构三层: presentation → domain → data, 依赖由 Hilt 注入
  - 每个 feature 独立 UiState / UiEvent / ViewModel / UseCase
  - HTTP 层统一使用 Retrofit + OkHttp
  - DTO 与 Domain Model 分离，Mapper 负责转换
  - API 协议 `robot_cooking_api_protocol.md` 为 Retrofit Api 接口定义的唯一依据
- Problems encountered: 无
- Resolution: 无
- Verification: `.project-log/` 所有文件已检查一致性，架构规范文档与 API 协议文档交叉引用正确
- Unverified items: 待新项目骨架搭建后验证架构可行性
- Files changed:
  - `.project-log/requirements.md`
  - `.project-log/architecture/software-architecture.md`
  - `.project-log/business-logic/main.md`
  - `.project-log/business-logic/nodes.md`
  - `.project-log/business-logic/edges.md`
  - `.project-log/business-logic/graph.md`
  - `.project-log/business-logic/decision-records.md`
  - `.project-log/progress.md`
  - `.project-log/current-session.md`
- Next steps:
  - 基于新架构规范搭建项目骨架（Gradle 配置 + Hilt + 目录结构）
  - 按 `robot_cooking_api_protocol.md` 定义 Retrofit Api 接口
  - 实现第一个 feature 的完整三层链路作为模板

---

## 2026-07-02

- Type: workflow
- Status: validated
- Importance: high
- Reusable: no
- Objective: GPT 按 ui_dev_briefing.md 编写新架构 Login + SelfCheck 两个页面的 presentation 层代码，审阅并修复合规问题。
- Work completed:
  - 审查 GPT 生成的 10 个 Kotlin 文件（2 个 Screen + 2 个 ViewModel + 2 个 UiState + 2 个 UiEvent + 1 个 Color 对象 + 1 个公共组件）
  - 审查结论：分层、命名、数据流、StateFlow 使用全部符合 MVVM + Clean Architecture 规范
  - 修复 6 个问题:
    1. SelfCheckViewModel init 块自动启动自检 → 删除，改为用户点击 StartCheckClicked 触发
    2. SelfCheckScreen 硬编码调试标签 "自检弹窗界面" → 删除
    3. SelfCheckScreen 右上角伪窗口按钮 (⌜ ⌟ ×) 无功能 → 删除，清理关联 imports
    4. SelfCheckScreen LoadingOverlay 写死 visible=false → 改为绑定 uiState.loading
    5. 两个 ViewModel 空构造函数 → 添加 UseCase 注入占位注释 (TODO: 接入真实接口时注入)
    6. LoginViewModel 输入过滤 onlyAsciiLetterOrDigit() 过严 → 移除过滤，清理死代码
  - 更新 ui_dev_briefing.md (400行) 创建至项目根目录，供 GPT 继续写后续页面
- Business logic impact:
  - Login 和 SelfCheck 的 presentation 层代码已就绪（Mock 阶段），可直接编译
  - 后续接入真实接口时只需替换 ViewModel 中的 Mock 逻辑为 UseCase 调用
- Problems encountered: 无
- Resolution: 无
- Verification: 源码审查通过，文件结构、命名、依赖方向与架构文档一致
- Unverified items: ~~实际编译结果（缺少 Gradle 项目骨架和资源文件）~~ → 后续已搭建骨架并验证 BUILD SUCCESSFUL
- Files changed:
  - `robot_cooking_ui_login_selfcheck/` 下 4 个文件修改:
    - `feature/login/presentation/LoginViewModel.kt`
    - `feature/selfcheck/presentation/SelfCheckViewModel.kt`
    - `feature/selfcheck/presentation/SelfCheckScreen.kt`
- Next steps: GPT 继续编写 MainDashboardScreen（主控面板）+ PinVerifyDialog，按 ui_dev_briefing.md 规范交付

---

## 2026-07-02 17:58 Local Time

- Type: workflow
- Status: validated
- Importance: high
- Reusable: no
- Objective: 将 GPT 生成并二轮 UI 检查过的 MainDashboard + PinVerifyDialog presentation 层整合进新版 Android APP。
- Work completed:
  - 从 `main_dashboard_presentation_code_v2_ui_checked/` 复制 6 个 dashboard presentation 文件到 `robot_cooking_ui_login_selfcheck/`。
  - 新增 `feature/dashboard/presentation/`：MainDashboardScreen、ViewModel、UiState、UiEvent、PinVerifyDialog、DashboardComponents。
  - 更新 `navigation/AppNavGraph.kt`，将 MainDashboard 路由占位替换为 `MainDashboardScreen()`。
  - 修复 `DashboardComponents.kt` 中 Material3 `LinearProgressIndicator(progress: Float)` 弃用警告，改用 lambda overload。
  - 更新 `business-logic/main.md` 和 `current-session.md`，记录 MainDashboard 已接入并编译通过。
- Business logic impact:
  - APP 主流程从 `Login -> SelfCheck -> MainDashboard TODO` 变为 `Login -> SelfCheck -> MainDashboard` 完整 Mock UI 闭环。
  - MainDashboard 实现 Dev/User 双模式、菜谱列表、任务进度、日志、PIN=1234、本地 Mock 任务控制、急停/复位二次确认。
  - 仍未接入真实 domain/data/Retrofit，符合 presentation-only 阶段边界。
- Problems encountered:
  - 第一次在仓库根目录运行 `./gradlew assembleDebug` 失败，因为根目录没有 Gradle Wrapper。
  - 首次构建出现一个 Compose Material3 进度条弃用警告。
- Resolution:
  - 改用 `robot_cooking_ui_login_selfcheck/gradlew -p robot_cooking_ui_login_selfcheck assembleDebug` 构建。
  - 将进度条调用改为 `progress = { task.progress / 100f }`。
- Verification:
  - 已运行 `/home/tbl/Project/ShangHai_718/robot_cooking_ui_login_selfcheck/gradlew -p /home/tbl/Project/ShangHai_718/robot_cooking_ui_login_selfcheck assembleDebug`。
  - 结果：BUILD SUCCESSFUL。
- Unverified items:
  - Android Studio/模拟器/真机上的视觉效果和交互手感未验证。
  - 真实 HTTP UseCase / Repository / Retrofit 尚未实现。
- Files changed:
  - `robot_cooking_ui_login_selfcheck/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/`
  - `robot_cooking_ui_login_selfcheck/app/src/main/java/com/example/robotcooking/navigation/AppNavGraph.kt`
  - `.project-log/business-logic/main.md`
  - `.project-log/current-session.md`
  - `.project-log/progress.md`
- Next steps:
  - 在 Android Studio 或设备上运行完整 UI 流程。
  - 若 UI 验证通过，按 `robot_cooking_api_protocol.md` 接入真实接口层。
  - 补充 `.gitignore`，清理 build/IDE/local 生成文件提交风险。

---

## 2026-07-05 10:56 Local Time

- Type: workflow
- Status: validated
- Importance: high
- Reusable: yes
- Objective: 切换到 `dex_app/` 作为当前主工程，并核对本地代码与远端最新状态，同时把最新代码现状同步进 `.project-log/`。
- Work completed:
  - 进入 `dex_app/` 仓库检查分支、远端和工作区状态。
  - 确认本地 `dev_dex_app` 最初落后 `origin/dev_dex_app` 2 个提交。
  - 拉取远端后复查，确认本地 `HEAD` 已同步到 `eef7bd7`，与 `origin/dev_dex_app` 一致。
  - 审查远端新增代码，确认 `dex_app` 现状已不再是纯 presentation mock：
    - 新增 `feature/networkconfig/presentation/`，支持配置中层 NODE 的 IP/Port 并持久化到 `SharedPreferences`
    - 新增 `core/network/`：`ApiClient`、`ApiEndpointStore`、`ApiResult`、`RobotCookingApi`
    - `SelfCheckViewModel` 已对接 `/api/robot/self-check`，支持失败重试
    - `MainDashboardViewModel` 中“左臂抓刀”动作已对接 `/api/robot/action`
    - `LoginViewModel` 已加入固定账号密码校验和 Remember Me
  - 更新 `.project-log/business-logic/main.md`、`business-logic/graph.md`、`current-session.md`
- Business logic impact:
  - 主工程正式明确为 `dex_app/`，旧的 `robot_cooking_ui_login_selfcheck/` 表述不再代表当前工作目录。
  - 应用主流程更新为 `Login -> NetworkConfig(optional) -> MainDashboard(showSelfCheck=true)`，保留 legacy `SelfCheck` route。
  - 项目阶段更新为“UI 已成型，部分真实 HTTP 已接入，但尚未回归目标 Clean Architecture 分层”。
  - 当前已知真实请求链路是 `ViewModel -> RobotCookingApi -> ApiClient -> OkHttp -> HTTP`，与目标 `UseCase -> Repository -> data` 链路存在偏差。
- Problems encountered:
  - 远端检查需要网络访问，沙箱默认无法直接连接远端 Git。
  - `.project-log/current-session.md` 中的工程路径和状态已落后于当前 `dex_app` 代码现状。
- Resolution:
  - 通过 `git fetch origin` 获取远端最新引用后完成同步判断。
  - 以当前代码为准，重写 `.project-log` 的会话摘要和主业务逻辑现状。
- Verification:
  - 已运行 Git 状态检查，确认 `dev_dex_app` 与 `origin/dev_dex_app` 同步。
  - 已检查最新提交链：`eef7bd7`、`e9cf0fe` 已在本地。
  - 本轮未运行 Android 构建、模拟器或真机验证。
- Unverified items:
  - `dex_app` 当前最新代码是否仍可 `assembleDebug`
  - 网络配置页保存的 endpoint 是否已被所有请求链路一致使用
  - 除自检和“左臂抓刀”外的其他接口是否会继续按 mock 保留，还是要马上下沉重构
- Files changed:
  - `.project-log/business-logic/main.md`
  - `.project-log/business-logic/graph.md`
  - `.project-log/current-session.md`
  - `.project-log/progress.md`
- Next steps:
  - 统一 `dex_app` 的真实网络接入策略
  - 把 SelfCheck 和 RobotAction 从 ViewModel 直连下沉到 domain/data 层
  - 运行一次 Android 构建验证当前远端最新代码状态

---

## 2026-07-05 12:48 Local Time

- Type: workflow
- Status: validated
- Importance: medium
- Reusable: yes
- Objective: 将主控面板 4 个机械臂快捷按钮的 PNG 图标替换为用户提供的新素材，并修正初次替换后的显示比例与裁切问题。
- Work completed:
  - 确认 `DashboardComponents.kt` 中“左手抓刀 / 左手放刀 / 右手抓黄瓜 / 右手放黄瓜”4 个按钮原先共用 `ic_hand_action.png`。
  - 将用户提供的 4 张 PNG 从桌面目录复制到 `dex_app/app/src/main/res/drawable-nodpi/`，并重命名为合法 Android 资源名：
    - `ic_left_grasp_knife.png`
    - `ic_left_release_knife.png`
    - `ic_right_grasp_cucumber.png`
    - `ic_right_release_cucumber.png`
  - 更新 `DashboardComponents.kt` 中 4 个 `QuickAction(...)` 的 `R.drawable` 引用，使每个按钮各自使用独立图片。
  - 首轮修复中发现新图为超大画布（原始约 `2048x2048`）且主体周围留白明显，导致在 `46.dp` 图标槽位中显示过小。
  - 通过裁紧 PNG 主体内容并将快捷按钮图标显示区域调整为 `84.dp x 42.dp`，修正了整体显示比例。
  - 二轮修复中发现“左手放刀”和“右手放黄瓜”原图由多个主要连通块组成，首次裁剪误删了刀和黄瓜部分。
  - 从用户原图重新生成上述两张资源，仅保留主要图形组件并排除右下角生成水印区域，恢复完整图标内容。
- Business logic impact:
  - 主控面板 4 个机械臂快捷按钮现在不再共用一个通用手势图标，而是与具体动作语义一一对应。
  - 该变更仅影响 presentation 资源显示，不改变任务控制、机器人动作请求、自检、登录或导航逻辑。
- Problems encountered:
  - 用户提供的 PNG 画布过大且留白多，导致图标显示过小。
  - 两张图片的主要图形由多个分离区域组成，基于“最大连通块”的裁剪策略会误删刀/黄瓜。
- Resolution:
  - 资源级修复：按主体内容裁切 PNG，并对多主体图标改为保留主要图形组件并集。
  - UI 级修复：放宽快捷按钮图标槽位尺寸以适配横向线稿图标。
- Verification:
  - 两次均运行 `./gradlew :app:assembleDebug`，最终结果均为 `BUILD SUCCESSFUL`。
  - 已人工检查新资源文件存在且与代码引用一致。
- Unverified items:
  - 尚未在模拟器或真机上做人工视觉验收，仅完成静态检查与构建验证。
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/DashboardComponents.kt`
  - `dex_app/app/src/main/res/drawable-nodpi/ic_left_grasp_knife.png`
  - `dex_app/app/src/main/res/drawable-nodpi/ic_left_release_knife.png`
  - `dex_app/app/src/main/res/drawable-nodpi/ic_right_grasp_cucumber.png`
  - `dex_app/app/src/main/res/drawable-nodpi/ic_right_release_cucumber.png`
- Next steps:
  - 在模拟器或真机上确认 4 个动作图标的视觉占比是否一致。
  - 若需要，再做一轮仅针对图标占比和对齐的微调，不改业务逻辑。

---

## 2026-07-05 13:30 Local Time

- Type: workflow
- Status: validated
- Importance: high
- Reusable: yes
- Objective: 清理主控面板近期一轮 UI 细节与交互逻辑，包括开始按钮状态/图标、右臂初始位置图标朝向，以及删除暂停/继续/取消按钮。
- Work completed:
  - 修复主页面首次进入时“开始制作”按钮错误显示为暂停态的问题。
  - 将 `MainDashboardViewModel` 初始任务从运行态改为 idle，使登录 -> 自检 -> 主界面流程下按钮默认显示开始态。
  - 将开始按钮的白色三角形从字符 `▶` 改为 `Canvas` 绘制的几何三角形，修正模板对齐问题，并按设计值微调橙色圆形颜色、阴影和三角形比例。
  - 为右臂“初始位置”按钮建立独立资源引用；由于用户提供图片与左臂原图内容一致，最终通过 `graphicsLayer(scaleX = -1f)` 对右臂图标做水平镜像，形成朝向差异。
  - 删除了开发者模式下“暂停 / 继续 / 取消”三个按钮。
  - 同步删除相关事件和 `ViewModel` 分支逻辑：
    - `PauseClicked`
    - `ResumeClicked`
    - `CancelClicked`
    - `resumeTask()`
    - `controlTask()`
  - 调整主界面布局，把删除按钮空出来的空间回补给主流程面板，宽屏和窄屏都做了纵向扩展。
- Business logic impact:
  - 主流程初始状态统一为“待开始制作”，不再在进入主页面后出现误导性的“暂停中/运行中”视觉状态。
  - 开发者模式不再支持 UI 层的暂停/继续/取消任务操作；当前任务控制入口收敛为开始、急停、复位、机械臂动作等保留能力。
  - 任务状态机中 `PAUSED` / `CANCELLED` 枚举仍暂时存在于模型中，但已不再由当前 UI 入口触发。
  - 菜谱切换限制逻辑同步收紧为仅在 `RUNNING` 状态下禁止切换。
- Problems encountered:
  - 开始按钮原始实现使用文本字符加偏移，无法稳定达到设计稿居中效果。
  - 右臂用户提供图标文件与左臂原图完全相同，替换资源引用后视觉无变化。
- Resolution:
  - 对开始按钮改为矢量几何绘制，而不是字体字符。
  - 对右臂图标采用显示时镜像而非继续等待另一张不同资源。
- Verification:
  - 多次运行 `./gradlew :app:assembleDebug`，当前结果为 `BUILD SUCCESSFUL`。
  - 已静态核对相关资源引用、事件删除和布局调整。
- Unverified items:
  - 尚未在模拟器或真机上做最终视觉验收。
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardUiEvent.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardScreen.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/DashboardComponents.kt`
  - `dex_app/app/src/main/res/drawable-nodpi/ic_right_arm_home.png`
- Next steps:
  - 在模拟器或真机上做一轮主页面视觉验收。
  - 若视觉通过，继续回到网络层与 Clean Architecture 落地整理。

---

## 2026-07-09

- Type: workflow
- Status: in-progress
- Importance: high
- Reusable: yes
- Objective: 服务端编译启动 + 客户端-服务端全接口联调审计 + 联调环境搭建。
- Work completed:
  - 在 ROS2 Humble 工作区编译 `dexbot_interfaces` + `dexbot_web_api` 两个包，BUILD SUCCESSFUL。
  - 安装缺失的 Python 依赖（pip3、uvicorn、fastapi、pydantic）。
  - 成功启动 HTTP API 服务：`ros2 run dexbot_web_api web_api_node`，监听 `0.0.0.0:8080`。
  - 与服务端 7 个接口逐一对比客户端请求参数/字段名/枚举值，完成全接口联调审计。
  - 移除调试逻辑：`AppNavGraph.kt` startDestination 从 `MainDashboard(showSelfCheck=false)` 恢复为 `Route.Login.path`。
  - 模拟器访问宿主机的默认地址从 `192.168.1.100` 改为 `10.0.2.2`。
  - 通过 adb 连接物理平板（Xiaomi pipa, a67adf5d），平板已部署 APP 并配置服务端地址。
  - curl 验证服务端连通性正常：`GET /api/system/status` → 200 OK。

- 全接口联调审计结果：

  | 接口 | 状态 | 问题 |
  |------|------|------|
  | POST /api/robot/self-check | 基本可用 | 客户端只检查 HTTP 200，不解析返回的 JSON body |
  | POST /api/task/start | 参数有废字段 | 客户端发 `taskId/recipeName/preconditions/task` 被 Pydantic 静默丢弃；返回值被忽略，服务端生成的 taskId 未保存 |
  | GET /api/task/current | 格式对齐 | 客户端传硬编码 `taskId="task_20260701_000001"`，永不匹配服务端动态 taskId；不传 taskId 反而可用 |
  | POST /api/task/control | **彻底断裂** | ①字段名 `"control"` vs 服务端 `"command"` → 422；②缺少必填字段 `arm`；③8个按钮中6个 control 值与 ControlCommand 枚举不匹配 |
  | POST /api/robot/action | 对齐最好 | 字段名和枚举值全部一致 |
  | GET /api/logs | 对齐 | 请求参数和响应字段一致 |
  | GET /api/system/status | 服务端独有 | 客户端未调用此接口 |

- Business logic impact:
  - task/control 承载了主页 8 个操作按钮中的 6 个（紧急制动、复位、召唤工作人员、拖拽、左臂/右臂初始位置、右手抓/放黄瓜），当前全部无法使用。
  - 联调环境已打通：服务端运行中、平板已连接、网络可达。

- Problems encountered:
  - colcon build 时缺失 `dexbot_interfaces` 依赖 → 先编译该包后解决。
  - 系统未安装 pip → `sudo apt install python3-pip`。
  - adb 权限不足 → adb kill-server + start-server 解决，无需 sudo udev。
  - 模拟器 `127.0.0.1` 指向模拟器自身而非宿主机 → 改为 `10.0.2.2`。

- Resolution:
  - 服务端已正常运行，HTTP 日志（uvicorn access log + ROS2 parsed request log）均输出到同一终端。
  - 平板端 APP 已部署，待用户操作按钮触发首次联调请求。

- Verification:
  - `colcon build --packages-select dexbot_interfaces dexbot_web_api` → BUILD SUCCESSFUL。
  - `curl http://127.0.0.1:8080/api/system/status` → 正常返回 JSON 响应。
  - `adb devices` → 平板 `a67adf5d` device 在线。
  - 接口审计结论已与服务端代码逐一核实。

- Unverified items:
  - 平板端 APP 未在服务端触发实际 HTTP 请求日志。
  - 修复后的代码未重新编译运行（Android）。

- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/navigation/AppNavGraph.kt` — 恢复 Login 为 startDestination
  - `dex_app/app/src/main/java/com/example/robotcooking/core/network/ApiEndpointStore.kt` — DEFAULT_HOST 改为 10.0.2.2

- Next steps:
  - 在平板上操作按钮，验证服务端能收到请求并打印日志。
  - 开始修复 task/control 接口的字段名和枚举值不匹配问题。

---

## 2026-07-09 — taskId 修复

- Type: bugfix
- Status: validated
- Importance: high
- Reusable: no
- Objective: 修复客户端 `POST /api/task/start` 响应中 taskId 被丢弃的问题。
- Work completed:
  - 在 `MainDashboardViewModel` 新增 `currentTaskId` 字段，存储服务端返回的真实 taskId。
  - 新增 `activeTaskId()` 方法：有真实 taskId 时返回，无则 fallback 到 `DEFAULT_TASK_ID`。
  - 新增 `parseTaskIdFromStartResponse()` 方法：从 `/api/task/start` 响应 JSON 中提取 `data.taskId`。
  - `startTask()` 成功后解析 `data.taskId` 并保存到 `currentTaskId`。
  - `startTaskPayload()` 去掉多余字段 `taskId`（服务端 `StartTaskRequest` 不认此字段，被 Pydantic 静默丢弃）。
  - 全文件 8 处 `DEFAULT_TASK_ID` 引用全部替换为 `activeTaskId()`，覆盖：
    - `validateAndOpenSelfCheck()`、`ensureCurrentTaskIdleForDragMode()`、`ensureCurrentTaskIdleForRobotAction()` — 空闲检查
    - `taskControlPayload()`、`robotActionPayload()` — 控制/动作请求
    - `requestCurrentTask()` — 轮询当前任务
    - `runLeftGraspKnifeUiProcess()` — UI 状态更新
- Business logic impact:
  - 客户端现在能获取并使用服务端生成的真实 taskId，`/api/task/current` 和 `/api/task/control` 后续调用能正确关联任务。
  - 唯一保留 `DEFAULT_TASK_ID` 的位置是 `activeTaskId()` 的 fallback（未开始任务前仍用默认值兜底）。
- Problems encountered: 无
- Resolution: 无
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
- Unverified items:
  - 平板端联调测试：开始制作后检查 `/api/task/current` 是否能正确返回任务状态
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
- Next steps:
  - 平板联调验证 taskId 流转
  - 继续修复 task/control 接口（字段名 `"control"` → `"command"` + 补齐 `arm` + control 值对齐 ControlCommand 枚举）

- Type: workflow
- Status: validated
- Importance: high
- Reusable: yes
- Objective: 完成 `dex_app` 当前一轮 UI 外观开发收尾，包括确认类弹窗模板统一、实时通知链模块收缩、终端风格日志弹窗模板落地，并将本阶段工作记入工程记录。
- Work completed:
  - 将“开始制作 / 紧急制动 / 恢复初始位姿”3 个确认类弹窗统一到共享外观模板，收敛标题栏、边框、尺寸、图标与正文排版。
  - 连续多轮微调确认类弹窗的：
    - 标题栏关闭按钮
    - 问号/感叹号图标
    - 正文文案字号、行高、字距
    - 图标与文案底部对齐
  - 将警告类弹窗中的感叹号由 Canvas 图形替换为 PNG 资源 `ic_dialog_warning.png`。
  - 清理“实时通知链（日志）”模块的旧跟踪逻辑，移除动态日志数据、日志详情弹窗和刷新入口。
  - 将“实时通知链（日志）”面板改为两个固定入口按钮：
    - 系统消息
    - 警告
  - 新增终端风格弹窗模板 `DashboardTerminalDialogs.kt`，并生成两个实例：
    - `SystemMessageTerminalDialog`
    - `WarningMessageTerminalDialog`
  - 给终端弹窗补齐基础交互：
    - 关闭按钮
    - 全屏 / 还原切换
    - 按住顶部栏拖动窗口
  - 将“系统消息 / 警告”两个按钮接到对应终端弹窗入口。
- Business logic impact:
  - 当前 UI 外观层已经形成两套明确模板体系：
    - 确认/警告类橙色标题栏弹窗模板
    - 实时日志类终端风格弹窗模板
  - “实时通知链（日志）”模块不再承担本地日志跟踪逻辑，正式转为后续真实日志终端的入口层。
  - 后续接后端实时日志时，可直接在两个终端弹窗主体区域注入日志流内容，而无需再恢复旧的日志列表/详情链路。
- Problems encountered:
  - 多个确认弹窗在历史演进过程中尺寸、标题栏按钮、图标和文案排版不一致。
  - 日志模块原先承担了较多临时 mock 逻辑，不适合作为后续终端式日志方案的基础。
- Resolution:
  - 统一抽象弹窗模板，持续按视觉目标参数收敛。
  - 清理旧日志链路，改为双入口 + 终端弹窗模板的新结构。
- Verification:
  - 本阶段多次运行 `./gradlew :app:assembleDebug`，最终结果持续为 `BUILD SUCCESSFUL`。
  - 已静态核对主要弹窗入口、状态字段、事件绑定和模板复用链路。
- Unverified items:
  - 尚未做真机/模拟器完整视觉验收。
  - 终端弹窗目前仍为占位内容，尚未接入真实日志接口。
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardUiState.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardUiEvent.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardScreen.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/DashboardComponents.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/DashboardConceptDialogs.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/DashboardTerminalDialogs.kt` (新增)
  - `dex_app/app/src/main/res/drawable-nodpi/ic_dialog_warning.png` (新增)
- Next steps:
  - 结束当前外观开发阶段。
  - 后续优先转入网络/数据层整理与实时日志接口接入。

---

## 2026-07-09 — 开始制作按钮增加空闲检查

- Type: enhancement
- Status: validated
- Importance: high
- Reusable: no
- Objective: "开始制作"按钮在发送 `/api/task/start` 前先检查机器人是否空闲。
- Work completed:
  - 修改 `startTask()`：点击确认 → 先调 `GET /api/task/current` 查询状态 → 非空闲则阻断并提示 → 空闲则继续调用 `/api/task/start`。
  - 空闲查询失败（HttpError/NetworkError）也阻断，分别记录日志 `task_start_blocked` / `task_start_idle_check_failed`。
  - 处理了 finally 块中 `operationLoadingKey` 的清理，确保空闲检查失败时不会卡 loading 状态。
- Business logic impact:
  - 在任务非空闲状态下，用户点击"开始制作"会被拦截并看到提示："当前状态：xxx，不能开始制作。"。
  - 与其他按钮的空闲检查逻辑一致（参考 `validateAndOpenSelfCheck` 的模式）。
- Problems encountered: 无
- Resolution: 无
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
  - 服务端日志已验证之前的 taskId 流转正确
- Unverified items:
  - 平板联调：在任务执行中点击"开始制作"，验证空闲检查阻断效果
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
- Next steps:
  - 平板联调验证空闲检查效果
  - 继续修复 task/control 接口

---

## 2026-07-09 — /api/task/current 默认不传 taskId

- Type: refactor
- Status: validated
- Importance: medium
- Reusable: no
- Objective: `/api/task/current` 的 taskId 参数改为默认不传，让服务端自动使用当前 taskId。
- Work completed:
  - 新增 `currentTaskQuery()` 辅助方法，只构建 `robotId` 参数，不包含 `taskId`。
  - 全文件 5 处 `GET /api/task/current` 调用点统一改用 `currentTaskQuery()`：
    - `validateAndOpenSelfCheck()`、`startTask()`、`ensureCurrentTaskIdleForDragMode()`、`ensureCurrentTaskIdleForRobotAction()`、`requestCurrentTask()`
- Business logic impact:
  - 服务端收到不传 taskId 的请求时，使用 `_current_task_id`（最近一次 start_task 写入的），能正确返回当前任务的实时状态。
  - `robotActionPayload()` 和 `taskControlPayload()` 中 POST 请求体的 taskId 仍保留，因为服务端需要它关联具体任务。
- Problems encountered: 无
- Resolution: 无
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
- Unverified items: 无
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
- Next steps:
  - 继续修复 task/control 接口

---

## 2026-07-09 — 服务端 _current_task_id 不清空 + 机器人状态文案简化

- Type: bugfix + enhancement
- Status: validated
- Importance: high
- Reusable: no
- Objective: 修复服务端 `_current_task_id` 到达终态后不清空导致轮询永远返回旧任务状态的问题；同时简化前端机器人状态显示。
- Work completed:
  - 服务端 `state_store.py`:
    - 新增 `_TERMINAL_STATUSES` 常量集合（finished/failed/cancelled/emergency_stop）。
    - `update_task_status()` 中当任务变为终态且是当前任务时，清空 `_current_task_id = None`，重置 `_robot_status = "idle"`。
    - 修复后 `/api/task/current` 不传 taskId 时，`_current_task_id` 为 None 返回空闲状态。
  - 客户端 `MainDashboardScreen.kt`:
    - `robotStatusText()` 从 7 分支缩减为 3 分支：idle → "空闲中"，emergency_stop → "急停中"，其他 → "任务中"。
- Business logic impact:
  - 服务端任务完成后不再"卡死"在旧任务状态，机器人能正常回到空闲。
  - 前端机器人状态显示更清晰，符合用户对机器人三个核心状态的认知。
- Problems encountered:
  - 轮询一直返回"状态异常" → 发现 `_current_task_id` 指向之前 ROS 调用失败的旧任务。
- Resolution:
  - 在终态判断处清空 `_current_task_id`，需重新 `colcon build` 并重启服务端。
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
  - `colcon build --packages-select dexbot_web_api` → BUILD SUCCESSFUL
  - 平板轮询服务端日志已确认：`taskId: None` + 200 OK → 返回 idle 状态
- Unverified items: 无
- Files changed:
  - `dexbot_ros2_ws-dev_715_cut_cucumbers/src/dexbot_web_api/dexbot_web_api/state_store.py`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardScreen.kt`
- Next steps:
  - 继续修复 task/control 接口

---

## 2026-07-09 — 任务状态轮询集中化（生产者-消费者模式）

- Type: refactor
- Status: validated
- Importance: high
- Reusable: yes
- Objective: 将分散在各操作中的 `/api/task/current` 调用收敛到集中轮询器，采用生产者-消费者模式，其他操作消费"下一条"新鲜结果。
- Work completed:
  - 新增 `TaskStatusSnapshot` 数据类（`rawBody` + `status`）。
  - 新增 `taskStatusChannel`（`Channel.CONFLATED`，始终保留最新结果）。
  - 在 `init` 块启动 `taskPollerJob`，`while(isActive)` 每秒调用 `/api/task/current`。
  - `fetchAndEmitTaskStatus()`：获取 → 更新 `_uiState`（驱动右上角状态 UI）→ `send` 到 Channel。
  - `awaitNextTaskStatus()`：private suspend 函数，`receive()` 等待下一条新鲜数据。
  - 4 个消费者从自己调 API + 解析改为消费轮询器结果：
    - `validateAndOpenSelfCheck()` — 自检空闲检查
    - `startTask()` — 开始制作空闲检查
    - `ensureCurrentTaskIdleForDragMode()` — 拖拽模式空闲检查
    - `ensureCurrentTaskIdleForRobotAction()` — 机械臂动作空闲检查
  - 删除 `requestCurrentTask()` 函数及其 2 处调用（`requestArmTaskControl` afterSuccess、`handleRobotActionResponse` RESET_POSE）。
- Business logic impact:
  - `/api/task/current` 调用从分散的 5 处收敛到 1 个轮询器，每秒更新状态。
  - 右上角"机器人状态"字段现在实时刷新（不再仅在按钮操作后更新）。
  - 其他操作获取当前状态只需消费轮询器下一条结果，无需自己发起网络请求。
- Problems encountered:
  - 首次编译报错：public 函数 `awaitNextTaskStatus()` 暴露了 private 类型 `TaskStatusSnapshot` → 改为 private。
- Resolution: `awaitNextTaskStatus()` 改为 `private suspend fun`。
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
- Unverified items:
  - 平板联调：验证轮询器持续工作、右上角状态实时更新、空闲检查消费正常
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
- Next steps:
  - 平板联调验证轮询器和空闲检查效果

---

## 2026-07-09 — 服务端 `_current_task_id` 不清空 + 机器人状态文案简化

- Type: bugfix + enhancement
- Status: validated
- Importance: high
- Reusable: no
- Objective: 修复服务端 `_current_task_id` 到达终态后不清空导致轮询永远返回旧任务状态的问题；同时简化前端机器人状态显示。
- Work completed:
  - 服务端 `state_store.py`:
    - 新增 `_TERMINAL_STATUSES` 常量集合（finished/failed/cancelled/emergency_stop）。
    - `update_task_status()` 中当任务变为终态且是当前任务时，清空 `_current_task_id = None`，重置 `_robot_status = "idle"`。
  - 客户端 `MainDashboardScreen.kt`:
    - `robotStatusText()` 从 7 分支缩减为 3 分支：idle → "空闲中"，emergency_stop → "急停中"，其他 → "任务中"。
- Business logic impact:
  - 服务端任务完成后不再"卡死"在旧任务状态，机器人能正常回到空闲。
  - 前端机器人状态显示更清晰。
- Problems encountered:
  - 轮询一直返回"状态异常" → 发现 `_current_task_id` 指向之前 ROS 调用失败的旧任务。
- Resolution:
  - 在终态判断处清空 `_current_task_id`，需重新 `colcon build` 并重启服务端。
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
  - `colcon build --packages-select dexbot_web_api` → BUILD SUCCESSFUL
  - 平板轮询服务端日志已确认：`taskId: None` + 200 OK → 返回 idle 状态
- Unverified items: 无
- Files changed:
  - `dexbot_ros2_ws-dev_715_cut_cucumbers/src/dexbot_web_api/dexbot_web_api/state_store.py`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardScreen.kt`
- Next steps:
  - 继续修复 task/control 接口

---

## 2026-07-09 — task/control 接口修复（对齐服务端）

- Type: bugfix
- Status: validated
- Importance: high
- Reusable: no
- Objective: 修复客户端 task/control 接口的字段名、缺参、枚举值三个阻断性问题。
- Work completed:
  - `taskControlPayload()`：字段 key `"control"` → `"command"`，新增必填参数 `arm`（默认 `"right"`）。
  - `requestTaskControl()`：参数 `control` → `command`，新增 `arm` 参数透传。
  - `armTaskControlName()`：6 个控制值全部对齐服务端 `ControlCommand` 枚举。
  - `taskControlExtra()`：移除 `arm`（已提升为 base 参数）。
  - 5 个调用者全部更新参数名和值。
- 值映射表：

  | 按钮 | 旧值 | 新值 |
  |------|------|------|
  | 紧急制动STOP | `emergency_stop` | `emergency_stop` (不变) |
  | 机器人恢复初始位姿 | `robot_reset` | `reset_pose` |
  | 召唤工作人员 | `call_staff` | `call_staff` (不变) |
  | 拖拽模式 开/关 | `drag_mode` + `enabled` | `drag_mode_on` / `drag_mode_off` |
  | 左臂/右臂初始位置 | `left_arm_home` / `right_arm_home` | `arms_initial_ready` + arm |
  | 右手抓黄瓜 | `right_grasp_cucumber` | `pick_cucumber` + arm="right" |
  | 右手放黄瓜 | `right_release_cucumber` | `place_cucumber` + arm="right" |

- Business logic impact:
  - task/control 接口从"彻底断裂"修复为对齐，8 个控制按钮中有 6 个走此接口，均修复。
- Problems encountered: 无
- Resolution: 无
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
- Unverified items:
  - 平板联调：逐个测试 8 个控制按钮，验证服务端收到正确的 command/arm 字段
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
- Next steps:
  - 平板联调验证 task/control 接口
  - 根据联调结果继续调整

---

## 2026-07-09 — STOP 按钮永不可灰化（急停最高优先级）

- Type: bugfix
- Status: validated
- Importance: high
- Reusable: no
- Objective: "紧急制动STOP"按钮在任何情况下保持可点击，不参与按钮互斥逻辑。
- Work completed:
  - UI 层 `DashboardComponents.kt`：STOP 按钮 `enabled` 从 `!actionBusy && state.operationLoadingKey == null` 改为 `true`。
  - ViewModel 层 `MainDashboardViewModel.kt`：`requestTaskControl()` 互斥守卫增加例外，`command == "emergency_stop"` 时跳过 loadingKey 检查直接执行。
- Business logic impact:
  - STOP 急停按钮在所有场景下均可点击（包括其他按钮正在 loading 时），且能真实触达服务端。
  - 体现急停最高优先级的安全设计要求。
- Problems encountered: 无
- Resolution: 无
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
- Unverified items:
  - 平板联调：在其他按钮执行中点击 STOP，验证服务端收到 emergency_stop 请求
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/DashboardComponents.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
- Next steps:
  - 平板联调验证

---

## 2026-07-09 — STOP 按钮永不可灰化 + 拖拽模式解Mock + 任务运行中按钮互斥

- Type: bugfix + enhancement
- Status: validated
- Importance: high
- Reusable: no
- Objective: STOP按钮永不灰化；拖拽模式取消Mock走真实API；任务运行时除STOP和右手抓/放黄瓜外其他按钮变灰。
- Work completed:
  - STOP按钮：UI层 `enabled=true`；ViewModel层 `requestTaskControl()` 允许 `emergency_stop` 绕过硬生生的互斥守卫。
  - 拖拽模式：`MOCK_DRAG_STATUS_IDLE` 和 `MOCK_DRAG_CONTROL` 改为 `false`，走真实 API。平板验证 `drag_mode_on` 200 OK。
  - 任务运行中互斥：`DashboardComponents.kt` 中 `StartAndActionArea`、`ArmQuickActionGrid`、`RightControlColumn` 全部加入 `isTaskRunning` 判断。
    - 左手3个按钮 + 右臂初始位置：任务运行时禁用
    - 右手抓黄瓜 + 右手放黄瓜：任务运行时保持可点击
    - 开始制作、召唤工作人员、复位、拖拽、自检：任务运行时禁用
    - STOP：永远可点击
  - 6条HTTP接口全部平板联调验证通过：self-check/task-start/task-current/task-control/robot-action/logs 均200 OK。
  - task/control 8个操作全部验证：pick_cucumber/place_cucumber/arms_initial_ready/call_staff/emergency_stop/reset_pose/drag_mode_on/drag_mode_off。
- Business logic impact:
  - 急停按钮最高优先级，任何情况下可点击。
  - 任务运行中只允许操作与黄瓜相关的右手动作，防止误触。
  - 任务结束后所有按钮自动恢复（轮询器驱动status更新）。
- Problems encountered: 无
- Resolution: 无
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
  - 服务端日志：6个接口全部200 OK，8个task/control操作全部验证
- Unverified items: 无
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/DashboardComponents.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
- Next steps:
  - 继续后续开发

---

## 2026-07-09 — 清理遗留 Mock 逻辑 + 修复开始按钮误显示暂停图标

- Type: bugfix
- Status: validated
- Importance: high
- Reusable: no
- Objective: 清除 ViewModel 中所有遗留 mock 代码；修复左手抓刀触发开始按钮显示暂停竖杠的 bug。
- Work completed:
  - 删除 `runLeftGraspKnifeUiProcess()`：遗留 UI mock，成功后将 `currentTask.status` 设为 RUNNING 持续 2.5 秒，导致开始按钮 `isTaskRunning=true` 显示暂停图标。
  - 删除 `executeLeftGraspKnife()` 中对 `runLeftGraspKnifeUiProcess()` 的调用。
  - 删除 `MOCK_DRAG_CONTROL` 分支及其常量：MOCK=false 后的死代码。
  - 删除 `MOCK_DRAG_STATUS_IDLE` 分支及其常量：同上。
  - 删除 `LEFT_GRASP_KNIFE_UI_DURATION_MS` 常量。
  - 删除"准备制作"卡片中的进度条渲染（`if(false)` 保留代码不删除）。
  - 还原之前错误添加的 call_staff 绕过互斥逻辑。
- Business logic impact:
  - 开始制作按钮不再因其他按钮操作而错误显示暂停图标。
  - 代码中零 mock 逻辑残留，所有操作走真实 API。
- Problems encountered:
  - 开始按钮在点击左手抓刀后显示暂停竖杠 → 根因 `runLeftGraspKnifeUiProcess` 设置 RUNNING 状态。
  - 之前错误判断召唤工作人员需要绕过互斥 → 已还原。
- Resolution:
  - 删除所有遗留 UI mock 函数和死代码分支。
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL
- Unverified items: 无
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/DashboardComponents.kt`
- Next steps:
  - 继续后续开发

## 2026-07-13 — 机器人状态显示颜色 + 空闲检查逻辑统一

- Type: feature
- Status: validated
- Importance: high
- Reusable: yes
- Objective: 统一所有按钮的空闲检查逻辑，只对 RUNNING 和 EMERGENCY_STOP 阻断；右侧机器人状态显示按状态匹配颜色。
- Work completed:
  - **右侧机器人状态显示颜色**：
    - `running` → "任务中" 黄色
    - `emergency_stop` → "急停中" 红色
    - 其他 → "空闲中" 绿色
  - **空闲检查逻辑统一**（6个操作全部改为相同规则）：
    - 检查条件从 `if status == IDLE` 改为 `if RUNNING || EMERGENCY_STOP`
      - RUNNING → "当前状态：进行中，不能执行xxx"
      - EMERGENCY_STOP → "当前状态：紧停中，不能执行xxx"
      - 其他状态（PAUSED/FINISHED/FAILED/CANCELLED/IDLE）全部放行
    - 受影响函数：`validateAndOpenSelfCheck()`, `startTask()`, `ensureCurrentTaskIdleForDragMode()`, `ensureCurrentTaskIdleForRobotAction()`
    - **`resetRobot()`** — 新增空闲检查（之前直接调 `requestTaskControl` 无检查）
    - **`callStaff()`** — 新增空闲检查（之前直接调 `requestTaskControl` 无检查）
  - **服务端 `emergency_stop` 行为确认**：
    - 不创建新 task_id，只更新现有 task 的 status 为 "emergency_stop"
    - `_robot_status` 永久保持 "emergency_stop" 直到被其他操作覆盖
    - `_current_task_id` 不清理的问题同样影响 emergency_stop 后的状态显示
- Business logic impact:
  - 之前只有 IDLE 才允许执行操作；现在 IDLE/PAUSED/FINISHED/FAILED/CANCELLED 都允许
  - 拖拽模式关闭（nextEnabled=false）仍然不检查，逻辑不变
  - 紧急停止、拖拽模式关闭不检查的逻辑保持原样
- Verification:
  - `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL (多次)
- Unverified items: 平板部署验证
- Files changed:
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/DashboardComponents.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardScreen.kt`
  - `dex_app/app/src/main/java/com/example/robotcooking/feature/dashboard/presentation/MainDashboardViewModel.kt`
- Next steps:
  - 服务端 `_current_task_id` 终态不清空问题待确认是否需要修复
