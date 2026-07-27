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
