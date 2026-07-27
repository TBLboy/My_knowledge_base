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

### D: 第二次横切完成前的交汇切口

```yaml
id: D
name: horizontal_cut_done
status: stable
state:
  - 第一次横切已完成
  - 目前旧流程会进入人工旋转豆腐
  - 新分支计划从这里开始承接第二次横切专用逻辑
inputs:
  - 预备位姿
  - cut_round profile
outputs:
  - 切割完成
  - 可继续进入新的第二次横切分支
related_hardware:
  - 右臂
related_interfaces:
  - /tofu_cut_round/execute
  - /tofu_second_cross_cut/execute
verification:
  - Action 返回 success
  - 可进入新分支或旧人工旋转链路
```

### U: 第二次横切抬刀/挑条完成

```yaml
id: U
name: second_cross_cut_hook_lift_done
status: draft
state:
  - 第二次横切后，刀已通过抬刀/挑条从豆腐主体中脱离
  - 豆腐条已被带离切缝并挂在刀刃附近或处于可转运状态
  - 右臂该阶段工作 TCP 定义为刀刃中心
  - hook_lift 默认采用 translate_only，可切换为 translate_plus_tilt 增强模式
  - 达到 hook_lift_clearance_m 后，才允许切换到转运阶段
inputs:
  - 第二次横切切痕交汇点
  - 抬刀/挑条 profile 参数
outputs:
  - 右臂处于带条安全状态
related_hardware:
  - 右臂
related_interfaces:
  - /tofu_second_cross_cut/execute
verification:
  - 日志确认进入 hook_lift stage
  - 刀未沿原 45 度原路退回
```

### V: 第二次横切转运到拨落区完成

```yaml
id: V
name: second_cross_cut_transfer_done
status: draft
state:
  - 右臂已将挂条移动到桌面容器上方
  - 当前采用单一容器区位姿，不额外拆分等待位与拨落位
  - 容器中心由现有 vision 节点输出直接提供，不新增独立感知节点
  - 容器检测在第一次横切完成、用户继续指令下发且豆腐位置送入 IK 后立即启动
  - 容器位置可持续更新，但每一轮只在生成该轮 transfer 轨迹前读取一次 latest/cached 结果
  - 右臂以刀刃中心 TCP 原点作为平移对象，将 TCP 原点移动到容器中心 + offset 后的目标点
  - 右臂在转运过程中保持 TCP 姿态不变
  - 右臂到达容器上方后先静止，再触发左臂目标转换与拨落
inputs:
  - U 节点输出
outputs:
  - 右臂停在容器上方安全位
  - 可在右臂静止后进行左右臂坐标转换
related_hardware:
  - 右臂
  - RealSense 相机
related_interfaces:
  - /tofu_second_cross_cut/execute
  - /cuttofu/vision/text_prompt
  - existing vision node output
verification:
  - 日志确认进入 transfer_to_drop_zone stage
  - 右臂稳定保持在容器上方
```

### W: 第二次横切拨落完成

```yaml
id: W
name: second_cross_cut_scrape_drop_done
status: draft
state:
  - 左臂 + O6 已将刀刃上的豆腐条拨落
  - 右臂仍保持安全停靠位
  - 左臂工作 TCP 定义为灵巧手手指上的操作点
  - 当前默认由左臂单独执行拨落轨迹，右臂在拨落期间保持静止
  - 左臂实际拨动轨迹暂未固化，后续通过拖动实验确定最合适的方向、路径形状和分段方式
  - 左臂候选姿态当前明确是左臂法兰坐标系姿态候选，手型默认直接使用 O6
  - 左臂法兰姿态通过候选库 + IK 预检选择，并在可达候选中优先选取距离当前目标法兰位置最近者
  - 左臂候选姿态通过右臂先到准备拨落状态、再人工拖动左臂逐个采集的方式建立
inputs:
  - V 节点输出
outputs:
  - 残料已处理完成
related_hardware:
  - 左臂
  - LinkerHand O6
related_interfaces:
  - /tofu_second_cross_cut/execute
verification:
  - 日志确认进入 left_scrape_drop stage
  - 拨落期间右臂保持静止
  - 左手完成拨落并退回安全位
```

### X: 第二次横切回下一刀位完成

```yaml
id: X
name: second_cross_cut_return_done
status: draft
state:
  - 左臂已回到准备位
  - 右臂已回到下一刀起点
  - 左右臂在拨落完成后按并行方式同步撤离与回位
  - 该起点语义复用现有第二次横切 cycle 中“回刀后再步进一次”得到的 next anchor
  - 可继续下一次第二次横切 cycle
  - 默认按单段控制完成回位，但允许未来扩展为多段回位
inputs:
  - W 节点输出
outputs:
  - 下一刀 cycle 的初始状态已准备好
related_hardware:
  - 右臂
related_interfaces:
  - /tofu_second_cross_cut/execute
verification:
  - 日志确认进入 return_to_next_cut_anchor stage
  - 左右臂回位阶段同步启动并完成
  - 下一 cycle 可继续执行
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
