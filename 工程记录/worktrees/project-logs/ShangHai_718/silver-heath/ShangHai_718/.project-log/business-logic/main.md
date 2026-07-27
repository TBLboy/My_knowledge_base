# Main Business Logic

## Status

- Current main path status: Draft — 已定义系统通信架构和APP节点序列，等待具体业务逻辑澄清。

## Main Path

```text
A -> B -> C -> D -> E
```

## Path Summary

- **A (APP就绪)**: APP启动完成，主控制界面可见，等待用户操作
- **B (用户操作已触发)**: 用户通过UI触发了一个操作指令，操作意图已明确
- **C (请求已发送)**: HTTP请求已按协议封装并发送到中层NODE
- **D (响应已接收)**: 中层NODE返回的HTTP响应已接收并完成解析
- **E (结果已展示)**: APP界面已根据响应更新，操作结果呈现给用户

## Implementation Priority

- Current target node: A (APP 框架搭建)
- Current target edge: 暂无 — 等待 UI 样式和具体操作列表

## Stable Assumptions

- 通信链路为: APP → HTTP → 中层NODE → 机器人控制接口
- 中层NODE会处理请求并路由到正确的机器人控制接口
- 机器人端ROS程序已可用，提供切黄瓜表演基础能力

## Verification Status

- 未验证 — 等待实现代码后测试。

## Notes

- 等待用户提供APP具体操作列表和UI样式澄清。
