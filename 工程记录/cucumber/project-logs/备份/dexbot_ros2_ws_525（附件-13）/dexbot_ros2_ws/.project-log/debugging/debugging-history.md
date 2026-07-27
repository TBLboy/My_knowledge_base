# Debugging History

## 2026-05-31 — 左臂 hold 第二段 MoveL（press）SDK 不执行

### Context

左臂 hold 流程需要两段 NRT 运动：先 MoveL 到 approach 点，再 MoveL 到 press 点（沿 base Y+ 8cm）。第一段运动正常。第二段 SDK 返回 True 但机器人不动。

### Attempt 1: 两段独立 `linear_move_to_pose(block=True)`

- **Status**: Failed
- **Approach**: 使用 executor 现有方法两次调用 SDK `linear_move_to_pose(block=True)`
- **Evidence**:
  - 第一段 approach 正常执行（~24s，日志：`after approach flange` 位置正确）。
  - 第二段 press 0.17s 返回 True，位置完全不变。
- **Failure**: 第二段返回成功但实际未执行。

### Attempt 2: 一次队列两条 MoveLCommand

- **Status**: Failed
- **Fix**: 新增 `move_flange_nrt_pose6_sequence()`，两条 MoveLCommand 一起 `moveAppend` + 一次 `moveStart`。
- **Evidence**:
  - 两条 waypoint 都已 append 成功。
  - 最终位置还是起点（`actual=[0.49548,0.13447,0.43986]`），队列未启动。
- **Failure**: 队列完全没执行，最终误差 439.2mm。

### Attempt 3: `block=False` + 自己轮询真实位置

- **Status**: Failed
- **Fix**: 改成 `block=False`，自己轮询 `get_flange_pose()` 直到到达目标。
- **Evidence**:
  - 第一段正常：7 秒到达，误差日志正确收敛。
  - 第二段 SDK 返回 True，但位置从 80.0mm 到 21 秒后仍是 80.0mm。
- **Failure**: 第二段 SD K `linear_move_to_pose(... block=False)` 发命令后，机器人没动，timer 超时。

### Attempt 4: 增停稳缓冲

- **Status**: Failed
- **Fix**: 在 approach 到达后加 `time.sleep(0.5)`，第二段发命令前再读当前 pose。
- **Evidence**:
  - 第二段仍不动，SDK `setOperateMode(automatic) 失败: 机器人运动中`（第一段还没停稳）。
- **Failure**: 等待不够。

### Attempt 5: 到位后等 `_wait_motion_done()` 停稳

- **Status**: Failed
- **Fix**: 位置进入容差后额外等 SDK `_wait_motion_done()` + 0.2s settle。
- **Evidence**:
  - 第一段正常：
    ```
    MoveL flange position reached, waiting motion settle: err=11.5mm
    MoveL flange settled: err=0.0mm
    ```
  - 第二段仍然不动：
    ```
    MoveL flange command: target=[0.57919,0.33062,0.05602] speed=0.001 dist=80.0mm timeout=60.0s
    MoveL flange waiting: actual=[0.57919,0.25062,0.05602] err=80.0mm elapsed=1.0s
    ... (20+s of same)
    ```
- **Failure**: 第二段 SDK 返回 True 但位置完全不变。

### Attempt 6: `block=True` + 1s settle + position 校验

- **Status**: Failed
- **Fix**: 回退到 SDK `block=True`，两段间加 1s sleep，加 position 校验。
- **Evidence**:
  - 同 Attempt 5 — 第二段完全不动，误差 80.0mm 持续 20+ 秒。
- **Failure**: 同上。

### Summary

| Attempt | Method | First segment | Second segment |
|---|---|---|---|
| 1 | `block=True` two separate calls | ✓ Arrived | ✗ Returned True, didn't move |
| 2 | One queue 2×MoveLCommand | ✗ Queue didn't start | ✗ Queue didn't start |
| 3 | `block=False` + poll 50Hz | ✓ Arrived | ✗ SDK True, didn't move |
| 4 | +0.5s settle after approach | ✓ | ✗ `机器人运动中` error |
| 5 | +`_wait_motion_done` settle | ✓ Arrived+settled | ✗ SDK True, didn't move |
| 6 | `block=True` + 1s settle | ✓ | ✗ SDK True, didn't move |

### Working conclusion

All SDK NRT `linear_move_to_pose()` attempts for the second segment have failed. The first segment (approach, ~400mm away, different pose) works. The second segment (press, 80mm, same orientation, same XZ, only Y+0.08) consistently returns success without moving.

This is not a Python-level issue (not timing, not wrong parameters, not sequence bug). It appears to be an xCore SDK behavior where the second NRT MoveL command in sequence is silently skipped or not dispatched.

### Open questions for next steps

1. Can we use `move_to_pose_target()` (MoveJ, not MoveL) for the press segment?
2. Can we use `move_rt_cartesian_path()` for the press segment?
3. Can a standalone SDK test script (not through ROS) reproduce the issue?
4. Is there a minimum-displacement threshold in SDK MoveL?
5. Is the issue specific to "same flange orientation + only Y translation"?
