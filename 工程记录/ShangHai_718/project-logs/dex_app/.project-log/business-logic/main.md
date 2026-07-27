# Main Business Logic

## Status

- Current main path status: **`dex_app/` 已成为当前主工程，并已同步到 `origin/dev_dex_app` 最新状态；Login + NetworkConfig + SelfCheck + MainDashboard UI 已接通，且部分真实 HTTP 调用已接入 ViewModel。**

## Important References

- **架构规范**: `/home/tbl/Project/ShangHai_718/android_app_architecture_readme.md`
- **API 协议**: `/home/tbl/Project/ShangHai_718/robot_cooking_api_protocol.md`
- 后期所有开发以这两个文档为准

## Application Screen Flow

```text
Login
  -> NetworkConfig (可选，配置中层 NODE IP/Port)
  -> MainDashboard(showSelfCheck=true)
       -> SelfCheck Dialog / Flow
       -> Main (Dev/User 双布局)

Legacy route kept:
Login -> SelfCheck -> MainDashboard
```

## Architecture Call Chain

```
Screen (Compose)
  → ViewModel (Hilt)
    → UseCase (domain)
      → Repository (interface, domain)
        → RepositoryImpl (data)
          → RemoteDataSource / LocalDataSource
            → Retrofit Api / Room Dao
```

## Current Implementation Gap

- 目标架构仍然是 `presentation -> domain -> data -> core`。
- 但当前 `dex_app` 的真实网络接入尚未走完整 Clean Architecture 链路。
- 已存在的真实请求路径主要是：

```text
Screen (Compose)
  -> ViewModel (Hilt)
    -> RobotCookingApi
      -> ApiClient
        -> OkHttp
          -> HTTP RESTful API
```

- 这意味着当前项目处于“UI 已成型，网络层开始接入，但 domain/data/Repository/UseCase 尚未系统化落地”的阶段。

## HTTP 接口清单（6）

| # | 接口 | 方法 | 作用 |
|---|------|------|------|
| 1 | `/api/robot/self-check` | POST | 机器人连接与自检 |
| 2 | `/api/task/start` | POST | 开始制作任务 |
| 3 | `/api/task/current` | GET | 获取当前任务状态（轮询 1s） |
| 4 | `/api/task/control` | POST | 任务控制（1接口通吃8种命令） |
| 5 | `/api/robot/action` | POST | 机器人动作控制 |
| 6 | `/api/logs` | GET | 获取系统日志（轮询 2s） |

## Dev vs User Mode

| 功能 | Developer | User |
|------|-----------|------|
| 菜谱选择 | ✓ | ✓ |
| 任务进度 | ✓ | ✓ |
| 开始制作 | ✓ | ✓ |
| 机械臂动作网格 (6按钮) | ✓ | ✗ |
| 暂停/继续/取消 | ✓ | ✗ |
| 召唤工作人员 | ✓ | ✗ |
| 拖拽模式开关 | ✓ | ✗ |
| 急停 | ✓ | ✓ |
| 恢复初始位姿 | ✓ | ✓ |
| 进度环 | ✗ | ✓ |
| 日志面板 | ✓ | ✓ |

## Mode Switch Flow

```
RequestModeSwitch(targetMode)
  -> Show PIN dialog (4-digit admin PIN)
  -> Verify: PIN == "1234"
  -> Success: POST /api/task/control { command: switch_xxx_mode }
  -> Fail: show error, stay on current mode
```

## 项目目录结构（按架构规范）

```
app/src/main/java/com/example/robotcooking/
├── App.kt
├── MainActivity.kt
├── core/
│   ├── network/        — ApiClient, NetworkResult, AuthInterceptor, ErrorHandler
│   ├── database/       — AppDatabase, dao
│   ├── datastore/      — AppDataStore, UserConfigStore
│   ├── security/       — SecureStorage, CryptoManager
│   ├── image/          — Coil 配置
│   ├── log/            — Timber 配置
│   ├── common/         — Constants, AppException, Extensions
│   └── di/             — Hilt Modules (Network, Database, DataStore, Security, Repository)
├── feature/
│   ├── recipe/          — data/domain/presentation
│   ├── robot/           — data/domain/presentation
│   ├── task/            — data/domain/presentation
│   └── login/           — data/domain/presentation
└── navigation/
    ├── AppNavGraph.kt
    └── Route.kt
```

## 操作列表

### 登录级
- 用户名/密码输入
- 固定账号密码校验（当前代码内置 `dex001 / 123456`）
- Remember Me 本地持久化
- 登录后进入 MainDashboard，并可带 `showSelfCheck=true`

### 网络配置级
- 配置中层 NODE IPv4 地址与端口
- 自动读取当前 Wi-Fi / Ethernet IPv4，预填前三段
- 保存 Endpoint 到本地 `SharedPreferences`

### 自检级
- 逐项系统自检（5项: 左臂/右臂/左手/右手/急停）
- 当前实现已对接 `POST /api/robot/self-check`
- 单项失败时重试 1 次，总计最多 2 次
- 自检完成后进入主控面板 / 解除自检阻塞

### 系统级
- 查询系统状态
- 切换开发者模式 / 用户模式（需 PIN 验证）

### 任务级（复用 /api/task/control）
- 开始制作
- 急停
- 恢复初始位姿
- 召唤工作人员（仅 Dev）
- 拖拽模式开关（仅 Dev）
- 暂停 / 继续 / 取消（仅 Dev）

### 机械臂动作（复用 /api/robot/action，仅 Dev）
- 左臂/右臂/双臂 × 抓取/放置/回位/移动/停止/开夹爪/合夹爪
- 当前仅“左臂抓刀”动作已直接接入真实 HTTP 请求与响应解析
- 其他机械臂动作当前仍为本地日志 / Mock 交互

### 信息展示
- 当前任务状态（进度条、步骤节点）
- 系统日志 / 实时通知
- 菜谱列表

## Stable Assumptions

- 通信链路: APP → HTTP → 中层NODE → 机器人控制接口
- HTTP 协议: RESTful JSON，统一响应 `{code, message, data}`
- 管理员 PIN: 1234（本地验证）
- DI 框架: Hilt
- 网络: 当前实际调用路径为 `RobotCookingApi + ApiClient + OkHttp`；`Retrofit` 依赖和 Provider 已保留，但尚未成为主调用入口
- 中层地址与端口已支持本地可配置保存
- 每个页面独立 UiState，通过 StateFlow 暴露

## Verification Status

- 尚未在本轮核查中运行构建或真机验证
- 仅完成代码结构检查与本地/远端分支同步确认

## Notes

- API 协议来源: `robot_cooking_api_protocol.md`
- 架构规范来源: `android_app_architecture_readme.md`
- 旧 APP（`RobotCookingControlApp/`）的 `ApiModels.kt` 数据模型可复用为 DTO 参考
- 初期使用单 `:app` module，按 feature 分包；后期可拆分为多 module
- 当前主分支: `dex_app/dev_dex_app`
