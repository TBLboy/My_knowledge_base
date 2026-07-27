# Main Business Logic

## Status

- Current main path status: Stable（总体可执行，仍需优化）

## Main Path

```text
A -> B -> C -> D -> E -> F -> G -> H -> I -> J -> K -> L -> M -> N
```

## Path Summary

- A: 系统启动，所有 Action Server 就绪
- B: 取刀（handle_approach）
- C: 预备切割位姿 1（prepare:first_cut）
- D: 水平切割轮次 1（cut_round:round_1）
- E: 人工旋转豆腐
- F: 预备切割位姿 2（prepare:first_cut）
- G: 水平切割轮次 2（cut_round:round_2）
- H: 人工旋转豆腐
- I: 预备垂直切割位姿（prepare:after_rotation_1）
- J: 垂直切割（vertical_cut）
- K: 等待操作确认
- L: 抓料摆放（pick_place）
- M: 倒酱料（sauce_pour）
- N: 流程结束

## 黄瓜流程（并行主路径）

```text
A -> O -> P -> Q -> R
```

- O: 左臂握持黄瓜（cucumber_hold:default）
- P: 预备黄瓜切割位姿（prepare:cucumber）
- Q: 水平切割黄瓜（cut_round:cucumber）
- R: 左臂释放黄瓜（cucumber_hold:release）

## 抓料倒酱流程（独立主路径）

```text
A -> S -> T -> N
```

- S: 抓料摆放（pick_place:default）
- T: 倒酱料（sauce_pour:default）

## Implementation Priority

- Current target node: 优化阶段，无明确新增目标节点
- Current target edge: 已全部实现，待优化各 edge 的执行稳定性和异常处理

## New Branch Target

- 从第一次横切完成后（D）分叉出一条新的第二次横切业务分支，目标是把“第二次横切后人工拨条”改成机器人自主动作。
- 新分支的预期链路是：第二次横切完成后不再走纯人工介入，而是进入“抬刀 / 挑条 / 运条 / 左手拨落 / 回下一刀位”的复合流程，再继续后续竖切前准备。
- 当前优先级：先把这个新分支写进业务逻辑，再逐步细化 skill 和 orchestrator 设计。
- 该分支当前明确采用串行协同：右臂完成带条并移动到容器上方静止后，左臂再基于右臂目标 TCP 派生拨落目标并执行拨落。
- 右臂在该阶段的工作 TCP 明确定义为刀刃中心；左臂工作 TCP 定义为灵巧手手指上的一个操作点。
- 容器检测当前确定直接复用现有 vision 节点输出，不新增独立感知节点；检测时机插入在第一次横切完成、用户下发继续指令、并已将豆腐位置送入 IK 求解之后，此时立即切换到容器检测。若容器检测成功，则进入新的第二次横切分支；若检测失败，则 fallback 回现有老版本第二次横切逻辑。
- 每个定位阶段都允许单独配置 offset 微调参数：至少包括右臂移动到容器阶段的 offset，以及左臂靠近右臂 TCP 阶段的 offset。
- 动作分段默认采用单段一步到位控制，但 skill 结构需要预留未来扩展为两段或多段控制的框架。
- hook_lift 阶段当前确定保留两种业务模式：默认 `translate_only`，增强模式 `translate_plus_tilt`。
- hook_lift 阶段的两个主参数明确为：`hook_pitch_delta_deg`（或等价目标角度）与 `hook_lift_clearance_m`。
- 右臂只有在达到 `hook_lift_clearance_m`、确认已完成脱离主体后，才切换到朝容器方向的 transfer 阶段；不把“脱离主体”和“转运到容器”混成一条长轨迹。
- 若启用 `translate_plus_tilt`，业务上优先采用短 RT waypoint 复合段来同时实现上抬和平缓姿态变化，而不是先引入复杂连续曲线规划。
- transfer 阶段当前确定采用 RT 笛卡尔平移到容器中心上方，移动过程中保持右臂刀姿不变，优先保证豆腐条在运条过程中不提前脱落。
- 到达容器上方后，第一版不拆分“等待位”和“拨落位”两个右臂显式子位姿；右臂在容器上方静止后，左臂直接基于该同一位姿执行拨落。
- 左臂用于拨落的候选姿态当前明确只约束左臂法兰坐标系姿态，本质上是人工采集左臂法兰候选姿势；手型默认直接使用 O6，不再把手型是否绑定在候选里作为开放问题。
- 新第二次横切分支执行期间，容器位置保持持续检测；右臂每次朝容器区移动都基于最新检测到的容器位置结果执行，而不是只读取一次后整轮复用。
- 左臂实际拨动轨迹暂保留为开放问题，后续通过人工拖动实验来确定最合适的拨动方向、路径形状和分段方式。
- 一次拨落完成后，左臂回准备位与右臂回下一刀起点必须同步进行；不采用“先退左臂、再回右臂”或反过来的串行收尾。
- 右臂返回目标不是本次挑条脱离点，而是严格复用现有第二次横切 cycle 中“回刀后再按既有步进规则平移一次”得到的下一刀起始位姿。

## Stable Assumptions

- 右臂持刀，左臂执行辅助操作（握持/抓料/倒酱）
- 视觉使用 RealSense + SAM3 + pose_estimator
- 手臂控制通过 xCore 直连 SDK 执行
- 所有 skill 通过 ROS 2 Action 接口暴露
- Orchestrator 通过 tick 驱动状态机顺序调用
- 人工介入通过文件 /tmp/cuttofo_operator_wait.json 轮询

## Verification Status

- 全部流程已通过运行测试，但 commit 注明"仍需优化"。
- 已知问题：见 debugging/known-issues.md。

## Notes

- 无。
