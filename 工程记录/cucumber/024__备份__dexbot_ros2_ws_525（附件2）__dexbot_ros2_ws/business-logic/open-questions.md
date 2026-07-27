# Open Business Logic Questions

## Active Questions

### Q-20260530-001

- Related node: A
- Related edge: A→B, B→C, C→D, D→E
- Question: 实际硬件 IP 是否与配置一致？
- Why it matters: 编译后启动流程依赖正确 IP
- Options: 左臂 192.168.2.160，右臂 192.168.2.161（配置默认值）
- Current status: Open
- Answer: Unknown

### Q-20260530-002

- Related node: A
- Related edge: A→B
- Question: O6 手爪 CAN 接口配置是否正确？左臂 can0，右臂 can1？
- Why it matters: xcore_controller_node 启动时需指定 CAN 接口
- Options: 单 CAN 总线时需关闭一侧 enable_internal_hand
- Current status: Open
- Answer: Unknown

### Q-20260530-003

- Related node: A
- Related edge: None
- Question: SAM3 模型路径在目标机器上是否存在？
- Why it matters: vision_bringup.launch.py 启动 sam3_detector_node 需要 model_path
- Options: 默认路径来自 vision_params.yaml
- Current status: Open
- Answer: Unknown

### Q-20260530-004

- Related node: B
- Related edge: A→B
- Question: 手眼标定文件是否已标定？（calibration_result_left.yaml / right.yaml）
- Why it matters: left→right 基座坐标变换需要使用标定结果
- Options: 未标定则使用默认 T [[1,0,0,0],[0,-1,0,0],[0,0,-1,-0.20],[0,0,0,1]]
- Current status: Open
- Answer: Unknown

## Resolved Questions

- None yet.
