# Debugging Records

## Known Issues

### 2026-06-15 - Colcon 编译嵌套包发现失败（已解决）

- Related: `cuttofo_skill_tofu_prepare` 编译问题
- 症状：`colcon build --packages-select cuttofo_skill_tofu_prepare` 显示 "ignoring unknown package"
- 根因：包嵌套在 `src/dexbot_middle_layer/CutTofo/cuttofu_skills/` 下，顶层 `dexbot_middle_layer/package.xml` 阻止 colcon 递归发现（colcon 找到 package.xml 后停止向下搜索）
- 诊断步骤：
  1. 检查 `colcon list` 输出，确认嵌套包未被发现
  2. 追踪目录结构，发现顶层 package.xml 阻断递归
  3. 检查 install/ 目录发现旧硬拷贝（非 symlink）
- 解决方案：使用 `--paths` 参数显式指定包路径
  ```bash
  colcon build --packages-select cuttofo_skill_tofu_prepare \
    --symlink-install \
    --paths src/dexbot_middle_layer/CutTofo/cuttofu_skills/cuttofo_skill_tofu_prepare
  ```
- 效果：egg-link → build 目录 symlink → source 目录，代码修改即时生效
- 长期建议：
  1. 将 CutTofo 包移到 `src/` 顶层（最干净方案）
  2. 或移除/重命名 `dexbot_middle_layer/package.xml`（破坏性较大）
- 当前状态：**已解决**，使用 --paths workaround

### 2026-06-11 - 左臂交接 handoff 真机不到位（未解决）

- Related: `cuttofo_skill_tofu_second_cross_cut` / `debug_left_handoff`
- 症状：`debug_left_handoff` IK 预检 `TCP err 0.0mm`，但左臂运动后仍不到拖动示教点。
- 已尝试：
  - 修正 IK/move 四元数语义；skill 内 TCP→法兰；`FLANGE::` 跳过控制器 tool offset；绝对 offset 采集公式；`from_euler` 崩溃修复。
- 当前状态：**未解决**；修复 `from_euler` 后未做真机闭环；offset/候选 yaml 可能仍基于旧公式或非标示教。
- 复现：`ros2 run cuttofo_skill_tofu_second_cross_cut debug_left_handoff`（右臂在容器中心）。
- 下一步：见 `.project-log/current-session.md` → Next Steps。

### 2026-06-06 - 整体情况

- Source: 最新 commit 评语 "总体能跑通,但仍需优化"
- 描述：整个流程可以运行完成，但存在多个待优化点。具体优化项尚未明确记录。
- 当前状态：已知但不明确

### 2026-06-06 - 切黄瓜待优化

- Source: commit 92215ac2 "切黄瓜待优化"
- 描述：黄瓜切割流程存在需要优化的问题。
- 当前状态：已知但不明确

## Debugging History

- 暂无详细调试记录。
