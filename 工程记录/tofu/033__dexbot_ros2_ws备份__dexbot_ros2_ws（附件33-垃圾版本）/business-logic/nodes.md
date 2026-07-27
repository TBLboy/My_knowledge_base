# Business Logic Nodes

## GUI Service Nodes (existing)

| Node | Description | Side | IP | CAN |
|------|-------------|------|----|-----|
| `arm_l` | Left arm ROS bridge | left | 192.168.2.160 | can1 |
| `arm_r` | Right arm ROS bridge | right | 192.168.2.161 | can0 |

## ROS Bridge Nodes (existing, rclpy)

| Node Name | Namespace | Side |
|-----------|-----------|------|
| `dexbot_gui_lclient` | `arm_l` | left |
| `dexbot_gui_rclient` | `arm_r` | right |

## Refactoring Nodes (added)

| Node | Description |
|------|-------------|
| `CodeBaseCurrentState` | 当前代码库状态：540+ 文件、131K+ 行、多份冗余、大文件、低测试覆盖率 |
| `CodeBaseCleaned` | Phase1 完成：gui_backup 已删除，遗留代码已归档，配置目录已统一 |
| `SharedAbstractionsReady` | Phase2 完成：配置加载、切割轨迹、tofu 几何已有共享唯一实现 |
| `MonolithsSplit` | Phase3 完成：所有 >1000 行的大文件已拆分为单一职责模块 |
| `RefactoringComplete` | Phase4 完成：关键路径已有冒烟/单元测试覆盖 |

### Intermediate Cleanup Nodes

| Node | Description |
|------|-------------|
| `Delete_gui_backup` | gui_backup/ 目录已删除 |
| `Archive_CutTofo_sdk` | CutTofo/sdk/ 中不用的脚本已归档 |
| `Archive_dexbot_high_layer` | dexbot_high_layer/ 切黄瓜代码已归档 |
| `Consolidate_config_dirs` | src/config/、src/config1/、arm_preset/、poses/ 已统一 |

### Intermediate Shared Abstraction Nodes

| Node | Description |
|------|-------------|
| `Extract_config_loader_to_shared` | config_loader 已提取到共享包 |
| `Extract_cut_trajectory_to_shared` | 切割轨迹规划已提取到共享包 |
| `Extract_tofu_geometry_to_shared` | tofu 几何计算已提取到共享包 |
| `Unify_cut_tofu_implementations` | 3 份切豆腐逻辑已合并 |

### Intermediate Split Monolith Nodes

| Node | Description |
|------|-------------|
| `Split_follow_tcp_chain` | xcore_follow_tcp_chain_node_movej.py (6268行) 已拆分 |
| `Split_arm_hand_gui` | arm_hand_gui.py (3482行) 已拆分 |
| `Split_hand_eye_calibration` | hand_eye_calibration_node.py (2511行) 已拆分 |
| `Split_xcore_controller` | xcore_controller_node.py (1939行) 已拆分 |

### Intermediate Test Nodes

| Node | Description |
|------|-------------|
| `Add_cuttofo_xcore_smoke_tests` | cuttofo_xcore 核心节点已有冒烟测试 |
| `Add_geometry_unit_tests` | tofu_geometry / cut_trajectory 已有单元测试 |
| `Add_adapter_smoke_tests` | xcore_arm_adapter 已有冒烟测试 |
