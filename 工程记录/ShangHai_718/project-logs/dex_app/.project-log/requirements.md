# Requirements

## Project Summary

- Goal: 为参加机器人展会的黄瓜切割表演机器人开发一个上层控制 APP，供用户/操作员控制机器人执行各种动作。
- Users / Operators: 展会参观者、操作员
- Current stage: 架构规范已确定，待按新架构重新搭建项目骨架

## Architecture Overview

```
用户 → 上层APP(Android PAD, Kotlin/Compose) → HTTP(JSON RESTful) → 中层NODE → 机器人控制接口 → 机器人(ROS)
|<---------------------------- 本工程负责范围 -------------------------->|
```

本工程职责：
- 上层 APP 界面与交互 (Kotlin + Jetpack Compose + Material 3)
- 上层 APP 到中层 NODE 的 HTTP 协议 (6 RESTful接口，统一 `{code, message, data}` 格式)
- HTTP 消息接口定义（请求/响应数据格式）

不负责：
- 中层 NODE 的实现
- 机器人底层控制接口（由 ROS 程序提供）
- 机器人端硬件部署

## Requirements

- APP 通过 HTTP 向中层 NODE 发送请求，控制机器人执行动作
- APP 提供以下操作界面：
  - 系统状态：机器人状态、工作模式、急停状态
  - 任务控制：开始制作、急停、恢复初始位姿、召唤工作人员、拖拽模式、暂停/继续/取消
  - 机械臂动作：左臂抓刀/放刀/回位、右臂抓黄瓜/放黄瓜/回位
  - 系统日志：实时通知链、警告、错误
- HTTP 接口规范：6个接口，统一 JSON 响应格式 `{code, message, data}`
- 接口协议以 `/home/tbl/Project/ShangHai_718/robot_cooking_api_protocol.md` 为正式规范

## Architecture Standard

项目采用 **Kotlin + Jetpack Compose + MVVM + 简化 Clean Architecture**，以 `/home/tbl/Project/ShangHai_718/android_app_architecture_readme.md` 为架构规范文档。

完整技术栈：

| 类型 | 技术选型 |
|------|----------|
| 开发语言 | Kotlin |
| UI 框架 | Jetpack Compose + Material 3 |
| 架构模式 | MVVM + 简化 Clean Architecture |
| 异步处理 | Coroutines + Flow / StateFlow |
| 依赖注入 | Hilt |
| 网络请求 | Retrofit + OkHttp |
| JSON 解析 | Kotlinx Serialization |
| 图片加载 | Coil |
| 本地数据库 | Room |
| 轻量配置 | DataStore |
| 安全存储 | Jetpack Security Crypto |
| 日志 | Timber |
| 页面导航 | Navigation Compose |

分层结构：
```
UI 层 (presentation) → Screen / ViewModel / UiState
       ↓
业务层 (domain) → UseCase / Repository Interface / Domain Model
       ↓
数据层 (data) → RepositoryImpl / RemoteDataSource / LocalDataSource / DTO / Entity / Mapper
```

## Task Scope

- In scope:
  - 上层 APP 开发 (Kotlin + Jetpack Compose, target Android PAD)
  - 6 个 HTTP 接口的客户端实现
  - 6 个接口的请求/响应数据类定义
  - APP UI 实现
- Out of scope:
  - 中层 NODE 实现
  - 机器人 ROS 控制程序
  - 机器人硬件/嵌入式部署

## Constraints

- 机器人端已有一套 ROS 程序用于切黄瓜表演
- 通信链路: APP(HTTP) → 中层NODE → 机器人控制接口
- 展会现场使用，需考虑操作简便性和稳定性
- HTTP 协议风格: RESTful JSON，统一响应格式

## Acceptance Criteria

- 待 UI 就绪后定义

## Decisions

- Kotlin + Jetpack Compose + MVVM + 简化 Clean Architecture 作为 APP 架构
- Hilt 统一管理依赖注入
- HTTP 采用 Retrofit + OkHttp + Kotlinx Serialization，6 个接口，统一 `{code, message, data}` 响应
- API 接口协议以 `robot_cooking_api_protocol.md` 为正式规范文档
- 架构设计以 `android_app_architecture_readme.md` 为工程规范文档
- 当前 APP（`RobotCookingControlApp/`）已放弃，作为参考实现存档

## Open Questions

- Q4: 中层NODE 网络地址和端口
- Q5: 是否需要认证/加密
