# Business Logic Graph

## Main (黄瓜切割)

```text
A -> B -> C -> D -> E
```

A: Idle（视觉 + controller + skill server 就绪）
  ↓ cucumber_hold:default — 左臂感知黄瓜，锁定位姿，移动到位
B: Cucumber Held（左臂按住黄瓜，shared geometry 已发布）
  ↓ prepare:cucumber — 右臂复用 hold 的几何信息，IK 求解切姿，移动到预备位
C: Knife Ready at Cut Pose（右臂就绪，工具坐标系对准黄瓜切割位置）
  ↓ cut_round:cucumber — 右臂 RT 笛卡尔路径竖切，10 刀，深度 8.5mm
D: Cutting Complete（切割完成，右臂回到等待位姿）
  ↓ cucumber_hold:release — 左臂 MoveAbsJ 回到 home 关节角
E: Initial State Restored

## Branches

```text
None yet (黄瓜 workflow 4 步均为 main path)。
```

## Archived

```text
Legacy:
  ROS nodes (ros/ + sdk/) → 被新 skill 架构替代，已归档。
```

## Notes

- 节点是状态快照。
- 边是执行链。
- 豆腐工作流（7 步）为次要路径，图结构见 tofu_workflow_params.yaml。
