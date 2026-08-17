# 机器人控制 APP 项目精华材料（第一阶段）

- **项目状态：**第一阶段精华材料，非最终简历文案
- **用户确认身份：**与他人合作开发；主要负责 API 接入和部分 UI 界面构建
- **主要来源：**
  - `工程记录/ShangHai_718/.project-log/requirements.md`
  - `工程记录/ShangHai_718/.project-log/business-logic/main.md`
  - `工程记录/ShangHai_718/.project-log/api/internal-api.md`
  - `工程记录/ShangHai_718/.project-log/architecture/software-architecture.md`
  - `工程记录/ShangHai_718/.project-log/progress.md`
  - `工程记录/ShangHai_718/.project-log/current-session.md`

## 1. 项目定位

面向机器人展会/炒菜机器人操作场景，开发 Android PAD 上层控制 APP，为用户和操作员提供登录、网络配置、系统自检、任务控制、机械臂动作、急停和实时日志等功能。

系统边界为：

```text
Android APP → HTTP REST API → 中层 Node → ROS 机器人控制程序
```

APP 负责上层交互和协议调用，不直接承担底层 ROS 控制和硬件部署。

## 2. 用户贡献确认范围（2026-08-17）

用户确认：与他人合作开发，主要负责 API 接入和部分 UI 界面构建。简历采用“合作开发 + 负责 API/部分 UI”口径，不写为全栈独立交付。

项目记录确认的整体工程内容包括：

- Android Compose UI 和页面导航。
- Login、NetworkConfig、SelfCheck、MainDashboard 页面。
- Developer/User 双模式和 PIN 切换。
- HTTP API 协议、请求/响应数据类和网络访问。
- ViewModel 状态管理和部分真实 HTTP 调用。
- 操作员现场需要的自检、急停、任务互斥和日志反馈。

工程记录中可支持的个人贡献包括：

- 6 类 REST API 的客户端接入、字段/枚举对齐和真实联调修复。
- 登录、网络配置、系统自检、主控制面板、Developer/User 双模式等部分 UI 构建。
- 自检解析、急停最高优先级、任务状态轮询、空闲检查等交互逻辑。
- 现场平板与服务端联调时对齐 taskId、字段名、枚举值和轮询策略。

## 3. 技术栈与架构

- Kotlin。
- Jetpack Compose + Material 3。
- MVVM + 简化 Clean Architecture。
- Hilt 依赖注入。
- Retrofit + OkHttp 网络请求。
- Kotlinx Serialization JSON 解析。
- Coroutines + Flow/StateFlow。
- Room、DataStore、Jetpack Security Crypto。
- Navigation Compose、Coil、Timber。

目标分层：

```text
presentation → domain → data → core
```

记录中的实际网络链路已经开始接入，但 domain/data/repository/use case 尚未完全按目标架构系统化落地，需要后续根据用户实际贡献选择更准确的简历表述。

## 4. 功能模块

### 登录与网络配置

- 用户名/密码登录。
- Remember Me 本地持久化。
- 登录后进入主控制面板。
- 配置中层 Node IPv4 地址和端口。
- 自动读取当前 Wi-Fi/Ethernet IPv4 并预填网段。
- 使用 SharedPreferences 保存 Endpoint。

### 系统自检

- 检查左臂、右臂、左手、右手和急停状态。
- 调用 `POST /api/robot/self-check`。
- 单项失败自动重试一次，最多两次。
- 自检完成后解除主界面阻塞。

### Developer/User 双模式

- Developer 模式提供更多机械臂动作和调试能力。
- User 模式保留简化任务操作界面。
- 模式切换需要 PIN 验证。
- 切换通过 `/api/task/control` 发送命令。
- 急停保持最高优先级，不因模式切换或任务状态被禁用。

### 任务与机器人控制

- 开始制作。
- 查询当前任务状态。
- 暂停、继续、取消。
- 急停。
- 恢复初始位姿。
- 召唤工作人员。
- 拖拽模式。
- 左臂抓刀/放刀/回位。
- 右臂抓黄瓜/放黄瓜/回位。
- 实时系统日志和通知链。

## 5. HTTP API

记录确认的核心接口共 6 类：

| API | 作用 |
| --- | --- |
| `POST /api/robot/self-check` | 机器人连接与自检 |
| `POST /api/task/start` | 开始制作任务 |
| `GET /api/task/current` | 获取当前任务状态 |
| `POST /api/task/control` | 统一任务控制命令 |
| `POST /api/robot/action` | 机器人动作控制 |
| `GET /api/logs` | 系统日志 |

统一响应格式为：

```json
{ "code": 0, "message": "", "data": {} }
```

## 6. 业务和交互难点

| 难点 | 解决方向 |
| --- | --- |
| 用户/操作员需要快速控制机器人 | 设计主面板、模式切换和任务状态反馈 |
| 现场设备可能处于未连接/异常状态 | 加入系统自检、重试、状态显示和日志 |
| 急停必须高优先级 | STOP 按钮不因普通任务状态灰化 |
| Developer 和 User 操作权限不同 | 通过模式视图和 PIN 切换隔离能力 |
| APP 不应耦合 ROS 底层 | 以 HTTP 协议作为 APP 与中层 Node 的边界 |
| 任务状态需要持续刷新 | ViewModel 轮询 `/api/task/current`，集中处理状态流 |

## 7. 记录中的验证与结果

- Login、NetworkConfig、SelfCheck、MainDashboard UI 已接通。
- 部分真实 HTTP 请求已进入 ViewModel。
- 任务状态轮询、taskId 传递、开始按钮空闲检查和状态显示逻辑有修复记录。
- 任务控制接口与服务端协议完成对齐。
- 项目架构规范和 API 协议已形成文档。
- 当前项目仍有部分 Clean Architecture 分层未完全落地，最终简历应根据实际代码提交选择“完成 APP 上层控制端”或“参与 APP 架构与功能实现”。

## 8. 可用于简历的价值标签

- Kotlin / Jetpack Compose
- MVVM / Clean Architecture
- Retrofit / OkHttp / Hilt
- Android PAD
- 机器人上层控制
- HTTP REST API
- 状态管理与任务轮询
- 自检、急停和异常反馈
- 现场操作产品化

## 9. 第一版简历表达方向（非最终文案）

### 稳健版方向

> 参与机器人展会控制 APP 开发，基于 Kotlin/Jetpack Compose 实现登录、网络配置、系统自检、任务控制和日志面板，接入 6 类 HTTP REST API，支持 Developer/User 双模式、急停、任务状态轮询和机械臂动作控制。

### 强表达版方向（需确认个人贡献）

> 负责机器人上层控制 APP 的页面架构与核心交互实现，基于 Kotlin/Jetpack Compose + MVVM 构建 Login、SelfCheck、MainDashboard 和任务控制链路，设计并接入统一 REST API，完善双模式权限、急停优先级、状态轮询和现场异常反馈。

## 10. 待用户补充的信息

1. 你在 APP 中的正式身份和实际负责模块。
2. 是否独立完成 UI、网络层、ViewModel 或 API 协议。
3. APP 是否真正安装在 Android PAD 并现场运行。
4. 是否有真实接口数量、页面数量、测试设备或现场演示信息。
5. 该项目是否与切黄瓜机器人直接关联，是否可以合并为同一段实习项目经历。
