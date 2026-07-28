# Business Logic Decision Records

## Decision Template

```markdown
### YYYY-MM-DD - <Decision Title>

- Decision: <what was decided>
- Context: <why this decision was needed>
- Alternatives considered:
  - <alternative 1>
  - <alternative 2>
- Reason: <why this decision was chosen>
- Evidence / Verification: <evidence if any>
- Impacted nodes: <nodes>
- Impacted edges: <edges>
- Status: active | replaced | archived
```

## Decisions

### 2026-07-01 - Android UI 技术栈选型

- Decision: 采用 Kotlin + Jetpack Compose 作为 Android PAD APP 开发技术栈
- Context: APP 需要在 Android PAD 上运行，用于展会现场控制机器人，需要高稳定性和良好响应
- Alternatives considered:
  - Flutter + Dart: 跨平台能力强，但当前只需 Android，引入额外复杂度
  - React Native: JS 生态，适合快速原型，但性能略低于原生
  - Java + XML: 传统 Android 方案，开发效率较低
- Reason: 仅需 Android PAD，不需要跨平台能力；原生方案在稳定性、性能和生态方面最优，适合展会场景
- Evidence / Verification: 无实际验证（开发阶段初期）
- Impacted nodes: A (APP就绪), E (结果已展示)
- Impacted edges: E1 (用户交互), E4 (UI更新)
- Status: active

### 2026-07-01 - HTTP 协议设计决策

- Decision: 采用 RESTful JSON API，6 个 HTTP 接口 + 1 个 WebSocket 可选接口；统一响应格式；核心复用接口 /api/task/control 和 /api/robot/action
- Context: 需要在上层APP和中层NODE间定义通信协议，管理 20+ 种用户操作
- Alternatives considered:
  - 每按钮一接口：接口爆炸，维护成本高
  - JSON-RPC: 过度设计
- Reason: 少接口强复用；两个核心接口覆盖所有操作，后期扩展只需加枚举值
- Evidence / Verification: 方案来源 robot_cooking_api_plan.md
- Impacted nodes: B, C, D
- Impacted edges: E1, E2, E3
- Status: active

### 2026-07-02 - 放弃当前 UI，API 协议作为稳定契约

- Decision: 放弃当前 `RobotCookingControlApp` 的 UI 实现（后期重新开发），但 `robot_cooking_api_protocol.md` 定义的 6 个 HTTP 接口协议和数据结构保持为后期开发的正式规范
- Context: 当前 APP UI 按 PAD 横屏固定宽度设计（侧边栏 264dp + 右侧面板 326dp），在手机等小屏幕设备上布局拥挤无法正常使用。用户决定重新开发 UI，但后端接口协议已经过充分定义和确认，不应因 UI 重做而变动
- Alternatives considered:
  - 为当前 APP 做响应式适配：工作量大，且 UI 本身经多次 GPT 迭代已不够清晰，重构不如重写
  - 保留当前 APP 继续开发直到完善：UI 架构问题会持续影响体验，后期改动成本更高
- Reason: API 协议是业务逻辑的核心产物，独立于 UI 实现，应当作为稳定契约保留。各枚举值、数据结构、错误码已覆盖所有操作场景，新 UI 直接对接即可
- Evidence / Verification: `ApiModels.kt` 和 `RobotCookingRepository.kt` 的数据结构验证了 API 协议与代码层的一致性；协议文档自身包含完整的请求/响应 JSON 示例
- Impacted nodes: A (APP就绪), B (用户操作已触发), C (请求已发送), D (响应已接收)
- Impacted edges: E1 (用户交互), E2 (HTTP请求), E3 (响应解析)
- Status: active

### 2026-07-02 - 采用 MVVM + 简化 Clean Architecture 作为新 APP 架构标准

- Decision: 新 APP 开发以 `android_app_architecture_readme.md` 为架构规范，采用 Kotlin + Jetpack Compose + MVVM + 简化 Clean Architecture + Hilt 依赖注入
- Context: 旧 APP（`RobotCookingControlApp`）已放弃，重新开发时需要一个明确的、AI 友好的架构标准，避免再次出现代码结构混乱、分层不清的问题
- Alternatives considered:
  - 继续使用旧 APP 的扁平 MVVM（单一大 UiState + FakeRepository）：扩展性差，不利于后期对接真实接口和多人协作
  - Flutter 跨平台方案：当前只需 Android PAD，不需要跨平台，引入额外复杂度
- Reason: MVVM + Clean Architecture 分层清晰（presentation/domain/data），职责边界明确，便于 AI 理解和修改，适合后期扩展为多模块工程。Hilt 统一管理依赖注入，Retrofit + OkHttp 标准化网络层
- Key architecture rules:
  - Screen 只负责渲染，不调 Repository/Retrofit/Room
  - ViewModel 只调 UseCase
  - UseCase 只调 Repository 接口
  - RepositoryImpl 协调 RemoteDataSource/LocalDataSource
  - DTO/Entity 绝不暴露到 presentation 层
- Evidence / Verification: `android_app_architecture_readme.md` 提供了完整的分层规则、目录结构模板、AI 开发规则
- Impacted nodes: 全部
- Impacted edges: 全部
- Status: active
