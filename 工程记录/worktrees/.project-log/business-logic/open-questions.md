# Open Business Logic Questions

## Active Questions

### Q-20260701-003

- Related node: C, D
- Related edge: E2, E3
- Question: HTTP 协议采用哪种风格？RESTful API？JSON-RPC？自定格式？
- Why it matters: 决定请求路由设计、Body 结构、错误码规范。
- Options: 推荐 RESTful（资源导向）或 JSON-RPC（操作导向），根据操作类型选择。
- Current status: Open
- Answer: 未知

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
- Options: 展会内网环境可能不需要；等待用户确认安全需求。
- Current status: Open
- Answer: 未知

### Q-20260701-006

- Related node: B, C, D
- Related edge: E1, E2, E3
- Question: 每个操作的请求/响应数据格式具体是什么？
- Why it matters: HTTP 接口定义的直接内容。
- Options: 等待业务逻辑澄清后逐一设计。
- Current status: Open
- Answer: 未知

### Q-20260701-007

- Related node: E
- Related edge: E4
- Question: APP UI 样式和交互设计是什么？
- Why it matters: 决定前端实现。
- Options: 等待用户提供UI设计稿或描述。
- Current status: Open
- Answer: 未知

### Q-20260701-008

- Related node: A
- Related edge: E1, E2
- Question: APP 需要支持哪些具体操作？（如：启动切黄瓜、停止、回零、急停等）
- Why it matters: 操作列表决定 HTTP 接口数量、UI 控件布局、内部请求对象的操作码定义。
- Options: 等待用户提供业务逻辑澄清。
- Current status: Open
- Answer: 未知

## Resolved Questions

### Q-20260701-001 (resolved)

- 原问题: 这个项目的目标是什么？"ShangHai_718" 的含义是什么？
- Answer: 这是一个机器人展会上控制切黄瓜表演机器人的上位APP项目。名称可能代表上海718展会。
- Resolved: 2026-07-01

### Q-20260701-002 (resolved)

- 原问题: APP 运行平台是什么？
- Answer: Android PAD 端
- Resolved: 2026-07-01
