# Business Logic Constraints

## System Constraints

- 重构后系统行为必须与重构前一致（纯重构原则）
- 不得修改现有的 ROS 话题/服务/动作接口名称和消息类型
- 不得修改 launch 文件的公共参数接口

## Hardware Constraints

- 所有硬件依赖保持不变：珞石 xCore AR5、Lbot（备选臂）、Linker 灵巧手、RealSense D435I
- 不修改 xCore SDK、Lbot C API、Linker 灵巧手 SDK 的调用方式
- 不修改手眼标定参数和坐标系关系
- 不修改 CAN 通信配置（can0 @ 1Mbps）

## Software Constraints

- ROS 2 Humble 版本不升级
- Python 依赖（numpy, scipy, opencv, rclpy 等）版本不修改
- 现有包之间的依赖关系（package.xml 中的 `<depend>`）不改变
- 不引入新的外部依赖（除非拆分时确实需要）

## Real-Time / Threading Constraints

- 保持现有节点的线程模型不变
- 不修改 rclpy 节点的 spin/executor 配置

## Safety Constraints

- 任何重构步骤不应影响正在运行中的真机操作
- 重构修改的代码必须能在 colcon build 通过后才算完成

## SDK / API Constraints

- xCore SDK 路径不变：`src/dexbot_bottom_layer/dexbot_bottom_layer/xcoresdk_python-*/`
- SAM3 模型路径不变：`/home/tbl/Project/models/sam3`
- 标定文件路径不变：`src/config/calibration_result.yaml`

## Configuration Constraints

- 现有 `src/config/`、`src/config1/` 下的 YAML 和 JSON 配置文件格式不变
- `arm_preset/`、`poses/` 中的预设位姿文件格式不变
