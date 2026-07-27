# Business Logic Graph

## Application Flow

```
Login
  ├── NetworkConfig (optional)
  ├── MainDashboard(showSelfCheck=true) -> SelfCheck Dialog -> MainDashboard(Dev|User)
  └── Legacy SelfCheck route -> MainDashboard(Dev|User)
```

## Main Path (Per-Session)

```
Login -> NetworkConfig(optional) -> SelfCheck -> A -> B -> C -> D -> E
```

- Login: 账户密码登录
- NetworkConfig: 中层 NODE 地址配置（本地保存 host/port）
- SelfCheck: 系统模块逐项自检（已对接 POST /api/robot/self-check）
- A: APP就绪 — 主控面板渲染完毕，初始化 GET 请求完成
- B: 用户操作已触发 — UiEvent → ViewModel → UseCase
- C: 请求已发送 — RepositoryImpl → RemoteDataSource → Retrofit Api → HTTP
- D: 响应已接收 — DTO → Mapper → Domain Model → UiState
- E: 结果已展示 — StateFlow → Compose recompose

Current partial implementation:

- SelfCheck: `ViewModel -> RobotCookingApi -> ApiClient -> OkHttp -> /api/robot/self-check`
- Dashboard left grasp knife: `ViewModel -> RobotCookingApi -> ApiClient -> OkHttp -> /api/robot/action`
- Start task / pause / resume / cancel / refresh logs: still local mock logic

## Architecture Call Chain

```
Screen (Compose)
  → ViewModel (Hilt, StateFlow)
    → UseCase (domain, 单个业务动作)
      → Repository (interface, domain)
        → RepositoryImpl (data)
          → RemoteDataSource / LocalDataSource
            → Retrofit Api / Room Dao
```

## Dev/User Branch

```
MainDashboard
  ├── workMode == DEVELOPER → DeveloperDashboard (完整功能)
  └── workMode == USER      → UserDashboard (精简功能)
```

## HTTP Interface Mapping

| Action Category | HTTP Interface | Method | Refresh After |
|---|---|---|---|
| Robot Self Check | `/api/robot/self-check` | POST | — |
| Task Start | `/api/task/start` | POST | refreshAll |
| Task Status Query | `/api/task/current` | GET | 轮询 1s |
| Task Control | `/api/task/control` | POST | refreshAll |
| Robot Arm Action | `/api/robot/action` | POST | refreshLogs |
| Logs Query | `/api/logs` | GET | 轮询 2s |

## Feature Module Map (新架构)

```
feature/
├── login/            — LoginScreen, LoginViewModel, LoginUiState
├── networkconfig/    — NetworkConfigScreen, NetworkConfigViewModel, NetworkConfigUiState
├── selfcheck/        — SelfCheckScreen, SelfCheckViewModel, SelfCheckUiState
└── dashboard/        — MainDashboardScreen, MainDashboardViewModel, MainDashboardUiState

core/
└── network/          — ApiClient, ApiEndpointStore, ApiResult, RobotCookingApi
```

## Branches

None yet.

## Archived

- `RobotCookingControlApp/` — 旧版 APP UI 参考实现（MVVM 扁平架构，FakeRepository）
- 归档原因: UI 针对 PAD 固定宽度设计，手机不适配；架构升级为 MVVM + Clean Architecture

## Notes

- 全链路: Android PAD → HTTP RESTful JSON → 中层NODE → ROS
- 统一响应: `{code, message, data}`
- DI: Hilt 统一管理所有依赖注入
- 导航: Navigation Compose
- 每个 feature 独立 UiState / UiEvent / ViewModel / UseCase
