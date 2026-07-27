# Known Issues

## Active

### KI-001 — rosidl 适配器中文路径 bug

- Symptom: `rosidl_generate_interfaces` cmake 函数报错
  `list index: 1 out of range (-1, 0)`，生成的 .idl 文件不识别。
- Cause: ROS2 Humble `rosidl_adapter` 对含中文字符的 build 路径解析失败。
- Workaround: 工作空间路径必须为纯 ASCII 英文。
- Status: 已修复（迁移到 /home/tbl/Project/cucumber/）

### KI-002 — colcon 不自动发现 CutTofo 嵌套包

- Symptom: `cuttofu_vision`, `cuttofo_skill_*` 等包不在 colcon list 中。
- Cause: `src/dexbot_middle_layer/` 是一个已发现包，colcon 不递归寻找其内部嵌套包。
- Workaround: 用 `colcon build --paths src/dexbot_middle_layer/CutTofo/...` 显式指定。
- Status: 已解决（指南中已包含 --paths 步骤）

### KI-003 — 未连接硬件时启动报错

- Symptom: vision_bringup.launch.py 找不到 RealSense，xcore_controller 连接超时。
- Cause: 无实际硬件。
- Status: 预期行为，联机时自动解决。
