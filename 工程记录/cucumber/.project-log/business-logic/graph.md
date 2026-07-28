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
暂无活跃分支。
```

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

## Notes

- Nodes are state snapshots.
- Edges are execution chains.
- `[E]` 和 `[H]` 表示人工介入节点，非 action server 调用。
