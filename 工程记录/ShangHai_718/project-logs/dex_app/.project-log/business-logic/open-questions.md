# Open Business Logic Questions

## Active Questions

### Q-20260701-004

- Related node: C, D
- Related edge: E2, E3
- Question: 中层NODE 的网络地址和端口是什么？开发环境/展会环境是否不同？
- Why it matters: 需要配置化管理，方便环境切换。
- Options: 等待中层NODE开发者提供。
- Current status: Open
- Answer: 未知

### Q-20260701-005

- Related node: C, D
- Related edge: E2, E3
- Question: 是否需要认证机制（Token/Key）？是否需要加密（HTTPS）？
- Why it matters: 展会环境可能有网络安全需求。
- Options: API 设计中未提及认证，展会内网环境可能不需要。
- Current status: Open
- Answer: 未知

## Resolved Questions

### Q-20260701-001 (resolved)

- 原问题: 这个项目的目标是什么？"ShangHai_718" 的含义是什么？
- Answer: 这是一个机器人展会上控制切黄瓜表演机器人的上位APP项目。
- Resolved: 2026-07-01

### Q-20260701-002 (resolved)

- 原问题: APP 运行平台是什么？
- Answer: Android PAD 端
- Resolved: 2026-07-01

### Q-20260701-003 (resolved)

- 原问题: HTTP 协议采用哪种风格？
- Answer: RESTful JSON API，统一响应格式 `{ code: int, message: string, data: object }`
- Source: `robot_cooking_api_plan.md`
- Resolved: 2026-07-01

### Q-20260701-006 (resolved)

- 原问题: 每个操作的请求/响应数据格式具体是什么？
- Answer: 详见 `robot_cooking_api_plan.md` 第4节，6个HTTP接口的完整请求/响应格式已定义。
- Source: `robot_cooking_api_plan.md`
- Resolved: 2026-07-01

### Q-20260701-007 (resolved)

- 原问题: APP UI 样式和交互设计是什么？
- Answer: 用户将自行用GPT搭建UI样式后提供代码。UI包含4类功能区：当前任务状态、任务控制、单臂动作控制、系统日志。
- Resolved: 2026-07-01

### Q-20260701-008 (resolved)

- 原问题: APP 需要支持哪些具体操作？
- Answer: 已明确，分4类：
  - 系统级：状态查询、模式切换
  - 任务级：开始制作、急停、恢复初始位姿、召唤工作人员、拖拽模式、暂停/继续/取消
  - 机械臂：左手抓/放刀、左臂回位、右手抓/放黄瓜、右臂回位
  - 信息：任务进度、系统日志
- Source: `robot_cooking_api_plan.md`
- Resolved: 2026-07-01

### Q-20260701-009 (resolved)

- 原问题: Android UI 开发用什么技术栈？
- Answer: Kotlin + Jetpack Compose
- Reason: 仅需 Android PAD，原生性能最优
- Resolved: 2026-07-01
