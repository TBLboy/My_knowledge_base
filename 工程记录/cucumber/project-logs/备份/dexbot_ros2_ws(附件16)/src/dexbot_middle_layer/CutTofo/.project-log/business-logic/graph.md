# Business Logic Graph

## Main

```text
CutTofu 豆腐完整流程：
A -> B -> C -> D -> [E] -> F -> G -> [H] -> I -> J

黄瓜流程：
A -> O -> P -> Q -> R

抓料倒酱流程：
A -> S -> T
```

## Branches

```text
第二次横切新分支（规划中）:
D -> U -> V -> W -> X -> I
```

- 分支约束：容器检测插入在第一次横切完成、用户下发继续指令且豆腐位置已送入 IK 之后；若容器检测成功则切入新分支，若失败则 fallback 到现有老版本第二次横切逻辑。
- 分支约束：新第二次横切分支执行期间持续检测容器位置；每次右臂朝容器区移动都基于最新容器检测结果执行。
- TCP 约束：右臂该阶段工作 TCP = 刀刃中心；左臂该阶段工作 TCP = 灵巧手手指操作点。
- 控制约束：默认按单段动作组织每个阶段，但 graph 对应的各 edge 允许未来细化为两段或多段执行。
- 控制约束：一次拨落完成后，左臂退回准备位与右臂返回 next anchor 同步进行，作为同一收尾阶段完成。
- 返回约束：W -> X 的目标位姿必须复用现有第二次横切 cycle 的 next anchor 语义，即“回刀后按既有步进规则平移一次”得到的下一刀起始位姿。
- 分支收尾：第二次横切整轮结束后切回豆腐检测并恢复 / override Phase6 视觉参数，后续业务链与现有老流程完全一致。

## Archived

```text
暂无已归档逻辑。
```

## Node Key

| Node | Skill | Action Server | Profile |
|---|---|---|---|
| A | 系统就绪 | — | — |
| B | handle_approach | /handle_approach/execute | default |
| C | prepare | /tofu_prepare/execute | first_cut |
| D | cut_round | /tofu_cut_round/execute | round_1 |
| E | （人工旋转豆腐） | operator_wait | — |
| F | prepare | /tofu_prepare/execute | first_cut |
| G | cut_round | /tofu_cut_round/execute | round_2 |
| H | （人工旋转豆腐） | operator_wait | — |
| I | prepare | /tofu_prepare/execute | after_rotation_1 |
| J | vertical_cut | /tofu_vertical_cut/execute | default |
| O | cucumber_hold | /cucumber_hold/execute | default |
| P | prepare | /tofu_prepare/execute | cucumber |
| Q | cut_round | /tofu_cut_round/execute | cucumber |
| R | cucumber_hold | /cucumber_hold/execute | release |
| S | pick_place | /pick_place/execute | default |
| T | sauce_pour | /sauce_pour/execute | default |
| U | second_cross_cut | /tofu_second_cross_cut/execute | round_2 |
| V | second_cross_cut | /tofu_second_cross_cut/execute | round_2 |
| W | second_cross_cut | /tofu_second_cross_cut/execute | round_2 |
| X | second_cross_cut | /tofu_second_cross_cut/execute | round_2 |

## Notes

- Nodes are state snapshots.
- Edges are execution chains.
- `[E]` 和 `[H]` 表示人工介入节点，非 action server 调用。
