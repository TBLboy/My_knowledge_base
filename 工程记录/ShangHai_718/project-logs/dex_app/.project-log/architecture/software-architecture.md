# Software Architecture

> 架构规范文档: `/home/tbl/Project/ShangHai_718/android_app_architecture_readme.md` — 本文件为工程摘要，以架构规范文档为准。

## System Layers

```
[User/Operator]
      |
      v
[Upper APP] -- this project (Kotlin + Compose + MVVM + Clean Architecture)
      |
      v (HTTP RESTful JSON)
[Middle NODE]
      |
      v (robot control interfaces)
[Robot ROS Program]
      |
      v
[Robot Hardware]
```

## APP Internal Architecture

采用 **MVVM + 简化 Clean Architecture** 三层结构：

```
presentation (UI层)
  ├── Screen         — Compose 页面，只负责渲染和事件转发
  ├── ViewModel      — 页面状态管理，调用 UseCase
  ├── UiState        — 页面状态 data class
  └── navigation     — Navigation Compose 路由

       ↓ 调用

domain (业务层)
  ├── model          — 业务领域模型（Domain Model）
  ├── repository     — Repository 抽象接口
  └── usecase        — 单个业务动作封装

       ↓ 实现

data (数据层)
  ├── remote         — RemoteDataSource + Retrofit Api 接口
  ├── local          — Room Dao + Entity + DataStore
  ├── model          — DTO / Entity / Mapper
  └── RepositoryImpl — 实现 domain 的 Repository 接口

       ↓ 依赖

core (公共基础)
  ├── network        — OkHttpClient / AuthInterceptor / ErrorHandler
  ├── database       — AppDatabase
  ├── datastore      — AppDataStore / UserConfigStore
  ├── security       — SecureStorage / CryptoManager
  ├── image          — Coil 配置
  ├── log            — Timber 配置
  ├── common         — 通用工具 / Constants / Extensions
  └── di             — Hilt Module 定义
```

## Dependency Rules

```
Screen → ViewModel
Screen → UiState
Screen ↗ Retrofit / Room / DataStore / RepositoryImpl  (禁止)

ViewModel → UseCase
ViewModel → StateFlow<UiState>
ViewModel ↗ Retrofit / Room / ApiService / Dao  (禁止)

UseCase → Repository (interface)
UseCase ↗ Retrofit / Room / Context  (禁止)

RepositoryImpl → RemoteDataSource
RepositoryImpl → LocalDataSource
RepositoryImpl → SecureStorage
```

## Tech Stack Detail

| 类型 | 技术选型 | 用途 |
|------|----------|------|
| 开发语言 | Kotlin | Android 首选语言 |
| UI 框架 | Jetpack Compose + Material 3 | 声明式 UI，设计规范 |
| 架构 | MVVM + 简化 Clean Architecture | 分层清晰，职责明确 |
| 异步 | Coroutines + Flow / StateFlow | 网络请求、状态流转、轮询 |
| 依赖注入 | Hilt | 统一管理所有依赖 |
| 网络 | Retrofit + OkHttp | RESTful HTTP 请求 |
| JSON | Kotlinx Serialization | Kotlin 原生 JSON |
| 图片 | Coil | Compose 图片加载 |
| 数据库 | Room | 结构化数据存储 |
| 配置 | DataStore | 轻量键值存储 |
| 安全 | Jetpack Security Crypto | Token/敏感配置加密 |
| 日志 | Timber | 统一日志管理 |
| 导航 | Navigation Compose | 页面路由 |

## Module Boundaries

### Upper APP (this project)
- Platform: Android PAD (横屏优先)
- Tech Stack: 如上表
- Architecture: presentation → domain → data，依赖由 Hilt 注入
- Backend: Retrofit + OkHttp 对接 6 个 HTTP RESTful 接口

### Middle NODE (not in scope)
- HTTP endpoint listener
- Request routing and unpacking
- Robot control interface adapter

### Robot ROS (not in scope)
- Cucumber cutting performance routines
- Motion control
- Sensor feedback

## Communication

- APP to Middle: HTTP RESTful JSON，6 个接口，详见 `robot_cooking_api_protocol.md`
- Middle to Robot: ROS interface (not in scope)
- 轮询策略: 任务状态 1s，系统日志 2s

## Deployment

- APP: runs on Android PAD (Kotlin + Jetpack Compose)
- Middle NODE: runs on robot-side development board
- Robot: robot hardware with ROS
