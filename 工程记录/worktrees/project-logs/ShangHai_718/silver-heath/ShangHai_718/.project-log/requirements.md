# Requirements

## Project Summary

- Goal: 为参加机器人展会的黄瓜切割表演机器人开发一个上层控制 APP，供用户/操作员控制机器人执行各种动作。
- Users / Operators: 展会参观者、操作员
- Current stage: 业务逻辑梳理阶段

## Architecture Overview

```
用户 → 上层APP → HTTP → 中层NODE → 机器人控制接口 → 机器人(ROS)
|<---------------- 本工程负责范围 --------------->|
```

本工程职责：
- 上层 APP 界面与交互
- 上层 APP 到中层 NODE 的 HTTP 协议
- HTTP 消息接口定义（请求/响应数据格式）

不负责：
- 中层 NODE 的实现
- 机器人底层控制接口（由 ROS 程序提供）
- 机器人端硬件部署

## Requirements

- APP 通过 HTTP 向中层 NODE 发送请求，控制机器人执行动作
- APP 需要提供清晰的操作界面，供展会现场使用
- 需要定义完整的 HTTP 消息接口规范

## Task Scope

- In scope:
  - 上层 APP 开发
  - APP → 中层 NODE HTTP 协议设计
  - 消息接口定义及数据格式
  - APP UI 设计
- Out of scope:
  - 中层 NODE 实现
  - 机器人 ROS 控制程序
  - 机器人硬件/嵌入式部署

## Constraints

- 机器人端已有一套 ROS 程序用于切黄瓜表演
- 通信链路: APP(HTTP) → 中层NODE → 机器人控制接口
- 展会现场使用，需考虑操作简便性和稳定性

## Acceptance Criteria

- 待业务逻辑澄清后定义

## Decisions

- 暂无记录。

## Open Questions

- APP 需要支持哪些具体操作？（待用户提供业务逻辑澄清）
- APP 运行平台：Android PAD 端
- HTTP 协议细节？（RESTful / JSON-RPC / 其他？待确认）
