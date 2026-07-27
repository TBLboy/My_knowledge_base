# Business Logic Graph

## Main Path (Tofu Workflow)

```text
 ┌─────────────────────────────────────────────────────────┐
 │                    启动前准备                              │
 │  A0: 机械臂上电 + CAN 初始化 → A1: 双臂控制器启动         │
 │  A2: RealSense + SAM3 + 位姿估计启动                      │
 └─────────────────────────────────────────────────────────┘
                          │
                          ▼
 ┌─────────────────────────────────────────────────────────┐
 │  阶段 1（自动连续执行）                                     │
 │  B:  handle_approach (抓刀)                               │
 │  C:  prepare first_cut (预备斜切位姿)                     │
 │  D:  cut_round round_1 (第 1 轮阻抗圆切)                  │
 └─────────────────────────────────────────────────────────┘
                          │
                    [人工转豆腐]
                     wait_before
                          │
                          ▼
 ┌─────────────────────────────────────────────────────────┐
 │  阶段 2                                                  │
 │  E:  prepare first_cut (同上的斜切预备)                   │
 │  F:  cut_round round_2 (第 2 轮阻抗圆切)                  │
 └─────────────────────────────────────────────────────────┘
                          │
                    [人工转豆腐]
                     wait_before
                          │
                          ▼
 ┌─────────────────────────────────────────────────────────┐
 │  阶段 3                                                  │
 │  G:  prepare after_rotation_1 (90° 竖切预备)             │
 │  H:  vertical_cut (垂直位置切割 + 推力段)                 │
 └─────────────────────────────────────────────────────────┘
                          │
                          ▼
                      完成
```

## Branch Path (Cucumber Workflow)

```text
 ┌─────────────────────────────────────────────────────────┐
 │  黄瓜切割                                                │
 │  I:  cucumber_hold default (左臂按住黄瓜)                  │
 │  C': prepare cucumber (右臂预备切刀位姿)                  │
 │  D': cut_round cucumber (右臂圆切)                       │
 │  I': cucumber_hold release (左臂归位)                     │
 └─────────────────────────────────────────────────────────┘
```

## Branch Path (Sauce Pour Workflow)

```text
 ┌─────────────────────────────────────────────────────────┐
 │  左臂浇酱（切豆腐完成后执行）                                  │
 │  J:  示教轨迹采集完成（瓶前就绪）                             │
 │  K:  抓瓶 + 抬升 + 视觉锁豆腐 + 倾倒                        │
 │      K-a: 沿 base Y- 抬升 lift_distance_m                  │
 │      K-b: 视觉锁豆腐 + IK 求倾倒位姿 + MoveJ               │
 │  L:  倾倒位姿到达（瓶口对准豆腐）                              │
 │  M:  灵巧手周期性挤酱完成                                     │
 │  N:  瓶子放回原位 + 松开                                      │
 │  O:  左臂回 home 位姿                                        │
 └─────────────────────────────────────────────────────────┘
```

## Branches

- `sauce-pour` — 左臂浇酱技能包 `cuttofo_skill_sauce_pour`（状态：candidate）

## Archived

- Legacy `cuttofo_xcore` package (pre-migration monolith, replaced by skill packages)
- Legacy `ros/` directory nodes (phase3_lib, object_recognition, etc.)
- Legacy `sdk/` demo scripts (pure SDK, no ROS)
- `cuttofo_lbot_interfaces` package (replaced by `cuttofo_skill_interfaces`)

## Notes

- Nodes are state snapshots (system states), not actions
- Edges are execution chains (described in edges.md)
- Current architecture replaced old monolith `cuttofo_xcore` with modular skill packages
