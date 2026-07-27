# Business Logic Nodes

## Node Template

```yaml
id: <node-id>
name: <node-name>
status: draft | stable | deprecated
state:
  - <what has become true at this node>
inputs:
  - <required input data or signal>
outputs:
  - <available output data or signal>
data_format:
  - <data type, message type, file type, coordinate frame, etc.>
related_hardware:
  - <hardware if any>
related_interfaces:
  - <ROS topic/service/action, API, SDK, protocol, etc.>
verification:
  - <how to confirm this state is reached>
notes:
  - <notes>
```

## Nodes

---

```yaml
id: A
name: APP就绪
status: draft
state:
  - APP启动完成
  - 主控制界面已渲染，所有操作按钮/控件可见且可交互
  - 中层NODE健康检查已通过（如适用）
inputs:
  - 无（或启动参数）
outputs:
  - 可交互的控制界面
  - 当前系统状态（连接状态、机器人状态等）
data_format:
  - UI控件状态
  - HTTP连接状态
related_hardware:
  - 无（部署在用户终端设备上）
related_interfaces:
  - HTTP Client → 中层NODE
verification:
  - APP成功启动，界面正常显示
  - 与中层NODE的网络连通性确认
notes:
  - 运行平台: Android PAD 端
```

---

```yaml
id: B
name: 用户操作已触发
status: draft
state:
  - 用户点击了某个操作按钮或输入了指令
  - 操作类型和参数已确定
  - 操作请求对象已构建完成
inputs:
  - 用户点击/触摸事件
  - 操作参数（如适用）
outputs:
  - 待发送的操作请求对象（操作类型 + 参数）
data_format:
  - 内部请求对象（操作码、参数键值对）
related_hardware:
  - 无
related_interfaces:
  - 无（内部状态）
verification:
  - 按钮点击后正确触发事件处理函数
  - 请求对象包含正确的操作类型和参数
notes:
  - 具体操作列表待用户澄清
```

---

```yaml
id: C
name: 请求已发送
status: draft
state:
  - HTTP请求已按协议格式序列化
  - 请求已通过HTTP POST/PUT/GET 发送到中层NODE
  - 等待中层NODE响应
inputs:
  - 操作请求对象（操作类型 + 参数）
outputs:
  - 待接收的HTTP响应（异步等待中）
data_format:
  - HTTP请求: 方法、URL、Headers、Body（JSON格式）
related_hardware:
  - 无
related_interfaces:
  - HTTP Client → 中层NODE
verification:
  - HTTP请求成功发出（网络层确认）
  - 请求格式符合协议规范
notes:
  - HTTP方法、URL路由、超时策略等具体协议细节待确认
```

---

```yaml
id: D
name: 响应已接收
status: draft
state:
  - HTTP响应已从网络层返回
  - 响应状态码已检查
  - 响应Body已解析为数据对象
  - 错误情况已识别（网络超时、服务端错误等）
inputs:
  - HTTP Response（状态码、Headers、Body）
outputs:
  - 解析后的响应数据对象
  - 操作结果（成功/失败/错误信息）
data_format:
  - 解析后的JSON对象（操作结果、机器人状态、错误信息等）
related_hardware:
  - 无
related_interfaces:
  - HTTP Response ← 中层NODE
error_handling:
  - 待定义
verification:
  - 正常响应正确解析
  - 异常响应（超时、5xx、格式错误）有适当的错误处理
notes:
  - 响应数据格式是与中层NODE的协议约定，需要双方对齐
```

---

```yaml
id: E
name: 结果已展示
status: draft
state:
  - APP UI已根据响应数据更新
  - 用户可以看到操作结果（成功提示、错误信息、状态变更等）
  - APP回到就绪状态，等待下一次操作
inputs:
  - 解析后的响应数据对象
outputs:
  - 更新后的UI界面
  - 用户可见的结果反馈（文本、图标、动画等）
data_format:
  - UI状态更新（文本变更、颜色变化、弹出提示等）
related_hardware:
  - 无
related_interfaces:
  - 无（UI内部更新）
verification:
  - 成功操作后界面正确显示成功状态
  - 失败操作后界面正确显示错误提示
  - UI在结果展示后恢复可操作状态
notes:
  - UI反馈的具体样式待用户提供UI设计
```
