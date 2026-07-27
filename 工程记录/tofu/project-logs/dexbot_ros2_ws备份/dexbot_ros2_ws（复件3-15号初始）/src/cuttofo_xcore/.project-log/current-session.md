# Current Session

## Last Updated

- 2026-05-14 Local Time

## Current Objective

修复 GUI 灵巧手 Open/Close 反问题和 CAN 初始化失败

## Completed This Session

### Bug 1：Open/Close 手指命令反了
- **根因**: GUI Open 发 `[0]*dof`，Close 发 `[100]*dof`，但 linkerbot-py 中 0=握紧，100=张开
- **修复**: Open → `[100.0]*dof`，Close → `[0.0]*dof`

### Bug 2：CAN 自动 up 失败
- **根因**: 只用 `pkexec bash -c ...`，Tk 下 polkit 弹窗可能无响应
- **修复**: 三段 fallback → 直接执行 → `sudo -n` → `pkexec env DISPLAY=...`

## Files Changed

- `src/gui/pages/arm_hand.py`: Open/Close 角度互换
- `src/gui/services/hand/control.py`: CAN 初始化三段 fallback

## Current State

- 豆腐视觉链路（SAM3 → pose_estimator → tofu_state → tofu_visualizer）稳定运行，ABCD 贴合点云表面
- AB 内缩修复 + FOV 恢复待实机验证
- 灵巧手 Open/Close + CAN 自动 up 待 GUI 实机验证

## Next Steps

1. 实机测试 CAN 自动 up
2. 实机测试 Open/Close 方向
3. TCP 标定
4. 端到端测试 /tofu_state → knife_prepare_action_server → 臂运动
