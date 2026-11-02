# 当前 Session 恢复信息

## 状态

- 当前工作目录：`unified_vr_teleop_franka/`
- 分支：`feat/franka`
- Task：`franka-adaptation`，仍为 active，当前阶段为 verify。
- DAgger、推理、策略执行、策略回放、评测/RL 功能清理已完成；Franka adapter/runtime 架构改造尚未开始。

## 已验证

- `compileall` 覆盖 `app`、`robot`、`main.py`、测试：通过。
- 清理相关离线测试：67 passed，9 subtests passed。
- 测试收集：324 项。
- 清理范围静态引用审计：未发现已删除策略模块、策略命令或 DAgger 模块路径残留。

## 已知限制

- 完整测试套件仍有 3 个与本次清理无关的既有失败：Piper fake 缺少 `MotionCtrl_2`、上传脚本目的路径断言漂移、human 速度上限断言不匹配。
- 未运行真实机械臂或任何会导致机械臂运动的操作。

## 下一步

- 用户要求后再开始 Franka adapter/runtime 架构实现。
- 开始真实硬件联调前，必须先获得用户明确确认，并遵循项目文档中的分阶段启动流程。
