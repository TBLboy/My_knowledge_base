# Business Logic Edges

## GUI Data Flow (existing)

```
User Input (ArmSidePanel)
    │
    ▼
ArmControlService(side)
    │
    ▼
ServiceRegistry.get_ros_bridge(side)
    │
    ├─ "left"  -> RosServiceBridge(node_name="dexbot_gui_lclient", namespace="arm_l")
    │                   │
    │                   ▼
    │              ROS services (move_joints, get_state, enable_arm, etc.)
    │
    └─ "right" -> RosServiceBridge(node_name="dexbot_gui_rclient", namespace="arm_r")
                       │
                       ▼
                  ROS services (move_joints, get_state, enable_arm, etc.)
```

## Joint State Polling (existing, 500ms)

```
ArmSidePanel._poll_joints()
    │
    ├─ bridge = services.get_ros_bridge(self._side)
    │
    └─ bridge.get_latest_joint_deg()
            │
            ▼
        UI update: _joint_reading_vars[i] labels
```

## Refactoring Edges (added)

### Edge: CodeBaseCurrentState -> Phase1_Cleanup

```yaml
edge_id: E-Refactor-Phase1
from: CodeBaseCurrentState
to: CodeBaseCleaned
path: main
status: draft
method: 清理冗余目录和文件，不改变代码逻辑
execution_chain:
  - 删除 gui_backup/ 目录
  - 确认 CutTofo/sdk/ 活跃状态后归档不用的脚本
  - 确认 dexbot_high_layer/ 状态后归档切黄瓜代码
  - 统一散落的配置文件目录
inputs: CodeBaseCurrentState 的所有文件
outputs: gui_backup 已删除，遗留代码已归档，配置目录已统一
parameters:
  - name: delete_backup
    type: bool
    default: true
    source: decision
  - name: archive_cuttofo_sdk
    type: bool
    default: pending
    source: open-question
  - name: archive_dexbot_high_layer
    type: bool
    default: pending
    source: open-question
interfaces: None (只涉及磁盘文件操作)
error_handling:
  - 若删除后发现问题，可从 git 历史恢复
verification:
  - 确认 gui_backup/ 已不存在
  - 确认 colcon build 通过
  - 确认 git status 符合预期
```

### Edge: CodeBaseCleaned -> Phase2_ExtractShared

```yaml
edge_id: E-Refactor-Phase2
from: CodeBaseCleaned
to: SharedAbstractionsReady
path: main
status: draft
method: 提取共享抽象，消除重复代码
execution_chain:
  - 提取 config_loader 到共享包
  - 提取 cut_trajectory 到共享包
  - 提取 tofu_geometry 到共享包
  - 统一 3 份切豆腐逻辑
inputs: CodeBaseCleaned 状态下的所有代码
outputs: 核心逻辑有唯一共享实现
interfaces: 共享包的 API
error_handling:
  - 每个提取步骤后验证 colcon build
  - 原文件保留 import 转发层直到稳定
verification:
  - colcon build 通过
  - compare diff before/after
```

### Edge: SharedAbstractionsReady -> Phase3_SplitMonoliths

```yaml
edge_id: E-Refactor-Phase3
from: SharedAbstractionsReady
to: MonolithsSplit
path: main
status: draft
method: 按职责拆分大文件
execution_chain:
  - 拆分 xcore_follow_tcp_chain_node_movej.py (6268 lines)
  - 拆分 arm_hand_gui.py (3482 lines)
  - 拆分 hand_eye_calibration_node.py (2511 lines)
  - 拆分 xcore_controller_node.py (1939 lines)
inputs: 当前代码
outputs: 各模块拆分到独立文件中
interfaces: 保持对外接口不变
error_handling:
  - 每个文件拆分后立即验证
  - 原文件保留 import 转发
verification:
  - colcon build 通过
  - 新模块的 import 路径正确
```

### Edge: MonolithsSplit -> Phase4_AddTests

```yaml
edge_id: E-Refactor-Phase4
from: MonolithsSplit
to: RefactoringComplete
path: main
status: draft
method: 补充测试覆盖
execution_chain:
  - 为 cuttofo_xcore 核心节点添加冒烟测试
  - 为 tofu_geometry / cut_trajectory 添加单元测试
  - 为 xcore_arm_adapter 添加冒烟测试
inputs: 重构后的代码
outputs: 关键路径有自动化测试覆盖
interfaces: 测试使用 pytest
error_handling:
  - 测试失败时修复后再推进
verification:
  - pytest 通过
  - 测试覆盖关键路径
```
