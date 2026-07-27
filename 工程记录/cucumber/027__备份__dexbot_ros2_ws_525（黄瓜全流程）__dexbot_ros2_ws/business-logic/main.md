# Main Business Logic

## Status

- Current main path status: Stable (黄瓜切割)

## Main Path

```text
A -> B -> C -> D -> E
```

## Path Summary

- A: Idle — 系统就绪，所有节点运行中
- B: Cucumber Held — 左臂已按住黄瓜（右臂基坐标系下的黄瓜位姿已锁定）
- C: Knife Ready at Cut Pose — 右臂已就位切姿
- D: Cutting Complete — 右臂竖切完成
- E: Initial State Restored — 左臂归位，回到初始状态

## Implementation Priority

- Current target node: E（已实现全流程）
- Current target edge: 全流程 4 步已实现

## Stable Assumptions

- 视觉使用 SAM3 + pose_estimator_node，topic 名称按 cuttofu 命名空间
- 左臂 SDK 直连（IP 192.168.2.160），不依赖 ROS 控制节点
- 右臂通过 xcore_controller_node 的 ROS service 接口控制
- 左右臂坐标变换通过手眼标定文件 `calibration_result_left.yaml` 实现
- 黄瓜切割不涉及人力等待（skip_human_wait: true）

## Verification Status

- 编译通过（20 包全部成功）
- 运行前需 source install/setup.bash
- 实际硬件集成测试待执行

## Notes

- 豆腐工作流为次要路径，含 7 步（含 handle_approach 和 operator 等待），当前未做主要测试
