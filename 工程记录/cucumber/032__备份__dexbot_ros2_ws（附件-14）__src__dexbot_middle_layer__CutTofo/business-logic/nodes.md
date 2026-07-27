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

### A: 系统就绪

```yaml
id: A
name: system_ready
status: stable
state:
  - 所有 Action Server 已启动并就绪
  - 手臂已使能
  - 视觉管线已启动
inputs: []
outputs:
  - 系统状态正常
related_hardware:
  - xCore 左右臂
  - LinkerHand（如需要）
  - RealSense 相机
related_interfaces:
  - /handle_approach/execute
  - /tofu_prepare/execute
  - /tofu_cut_round/execute
  - /tofu_vertical_cut/execute
  - /cucumber_hold/execute
  - /pick_place/execute
  - /sauce_pour/execute
  - /cuttofu/vision/*
verification:
  - Action server 可用性通过 preflight 检测
  - EnableArm 服务可用
```

### B: 取刀完成

```yaml
id: B
name: knife_grabbed
status: stable
state:
  - 刀已从刀架取出
  - 右臂持刀，处于 home 位姿
inputs:
  - 刀柄视觉锁定目标
outputs:
  - 手爪闭合持刀
related_hardware:
  - 右臂
  - LinkerHand O6 夹爪
related_interfaces:
  - /handle_approach/execute
  - /cuttofu/perception/objects_with_pose
verification:
  - Action 返回 success
  - 视觉确认刀不在刀架
```

### C: 预备切割位姿（对刀）

```yaml
id: C
name: prepare_pose_reached
status: stable
state:
  - 右臂末端已到达切割预备位姿
  - 刀锋对准目标物切割平面
inputs:
  - 视觉检测到的目标物位姿
  - prepare profile 参数（角度、偏移等）
outputs:
  - 右臂在预备位姿
related_hardware:
  - 右臂
  - RealSense 相机
related_interfaces:
  - /tofu_prepare/execute
  - /cuttofu/perception/objects_with_pose
  - /cuttofu/vision/text_prompt
verification:
  - Action 返回 success
  - IK 求解成功
  - 预览验证通过
```

### D: 水平切割完成

```yaml
id: D
name: horizontal_cut_done
status: stable
state:
  - N 次阻抗控制切割循环已完成
  - 右臂回到 wait 位姿
inputs:
  - 预备位姿
  - cut_round profile（cycle数、步进、刚度、速度等）
outputs: []
related_hardware:
  - 右臂
related_interfaces:
  - /tofu_cut_round/execute
  - /tofu_cut_round/resume
verification:
  - Action 返回 success
  - 每次 cycle 反馈正常
```

### E: 人工旋转豆腐

```yaml
id: E
name: operator_rotated_tofu
status: stable
state:
  - 操作人员已旋转豆腐
  - operator continue 已触发
inputs:
  - /tmp/cuttofo_phase_after_round*_continue 文件
  - 或 /cuttofo_operator/continue 服务调用
  - 或终端 Enter
outputs:
  - continue 信号已发出
related_interfaces:
  - /cuttofo_operator/continue
  - /tmp/cuttofo_operator_wait.json
verification:
  - ResumeTofuCutRound 服务调用成功
  - cut_round 返回 success
```

### O: 黄瓜握持就绪

```yaml
id: O
name: cucumber_held
status: stable
state:
  - 左臂已视觉锁定黄瓜
  - 阻抗控制握持中
inputs:
  - 视觉黄瓜检测位姿
outputs:
  - 左臂握持黄瓜
related_hardware:
  - 左臂
related_interfaces:
  - /cucumber_hold/execute
  - /cuttofu/perception/objects_with_pose
verification:
  - Action 返回 success
  - /cucumber_hold/execute goal 发送
```

### J: 垂直切割完成

```yaml
id: J
name: vertical_cut_done
status: stable
state:
  - 垂直切割完成（含 mid-cycle + tail push）
inputs:
  - 垂直切割预备位姿
  - 垂直切割参数（move 指令参数等）
outputs: []
related_hardware:
  - 右臂
related_interfaces:
  - /tofu_vertical_cut/execute
verification:
  - Action 返回 success
```

### S: 抓料完成

```yaml
id: S
name: pick_place_done
status: stable
state:
  - 小料已抓取并摆放到目标位置
inputs:
  - 视觉检测的小料位姿
outputs: []
related_hardware:
  - 左臂
related_interfaces:
  - /pick_place/execute
  - /cuttofu/perception/objects_with_pose
verification:
  - Action 返回 success
```

### T: 倒酱完成

```yaml
id: T
name: sauce_poured
status: stable
state:
  - 酱料已倾斜倒出
  - 已挤压瓶身
  - 酱瓶已放回
inputs:
  - 预先标定的 flange pose 候选
  - （可选）视觉目标位姿
outputs: []
related_hardware:
  - 左臂
related_interfaces:
  - /sauce_pour/execute
verification:
  - Action 返回 success
```
