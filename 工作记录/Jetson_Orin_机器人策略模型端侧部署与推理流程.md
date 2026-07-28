# Jetson Orin 端侧机器人策略模型部署与推理流程

> 文档用途：用于端侧部署复习、工程实施参考和面试准备  
> 适用场景：生成式行为克隆、ACT、Diffusion Policy、视觉—力触策略等机器人模型  
> 目标设备：NVIDIA Jetson Orin 系列  
> 文档版本：v1.0  
> 更新日期：2026-07-14

---

## 1. 核心认识

机器人策略模型部署到 Jetson Orin，并不是让模型直接控制电机，而是将模型部署成一个“智能目标动作生成器”。

完整链路为：

```text
相机 / 关节状态 / 力觉 / 触觉
                ↓
         Observation Adapter
                ↓
            策略模型
                ↓
        候选目标 Action
                ↓
          Action Adapter
                ↓
      安全检查 / 限位 / 滤波
                ↓
       已有机械臂控制器接口
                ↓
       SDK / 驱动 / 底层控制器
                ↓
              机器人
```

职责划分：

- 模型负责决定“下一步应该做什么”；
- Action Adapter 负责将模型输出转换为控制器可接受的格式；
- 原有控制系统负责逆运动学、轨迹生成、插值、底层控制和安全执行；
- 硬件安全模块负责急停、过载和故障保护。

---

## 2. 端侧部署总体流程

```text
1. 固化模型输入输出协议
        ↓
2. 选择并配置 Jetson Orin 环境
        ↓
3. 在 Orin 上跑通原始 PyTorch 模型
        ↓
4. 主机—端侧数值一致性验证
        ↓
5. 端侧性能 Benchmark
        ↓
6. ONNX / TensorRT / FP16 优化
        ↓
7. 必要时拆分模型计算模块
        ↓
8. 优化输入尺寸、缓存和生成步数
        ↓
9. 实现 Observation Adapter
        ↓
10. 实现 Action Adapter
        ↓
11. 接入已有机械臂控制程序
        ↓
12. 离线回放
        ↓
13. Shadow Mode
        ↓
14. 低速实机测试
        ↓
15. 闭环任务运行和长期监控
```

---

# 3. 第一阶段：固化模型输入输出协议

训练结束后不能只交付一个 `model.pth`。

至少要形成完整模型发布包：

```text
policy_release_v1/
├── model.pth
├── model_config.yaml
├── observation_schema.json
├── action_schema.json
├── normalization_stats.npz
├── camera_config.yaml
├── force_tactile_config.yaml
├── model_metadata.json
└── test_vectors/
    ├── sample_input.npz
    └── expected_output.npz
```

## 3.1 Observation Schema

必须明确模型输入：

- 相机数量和顺序；
- RGB 或 BGR；
- 图像分辨率；
- resize、crop 和归一化方式；
- qpos 顺序；
- 力觉坐标系；
- 触觉数据形状；
- 观测历史长度；
- 不同模态时间对齐方法。

## 3.2 Action Schema

必须明确：

- action 是关节位置、速度还是增量；
- 绝对动作还是相对动作；
- 单位是弧度、角度、米还是毫米；
- 关节维度顺序；
- 动作坐标系；
- Action Chunk 长度；
- 模型输出频率。

动作维度顺序错误是部署过程中风险最高的问题之一。

---

# 4. 第二阶段：端侧 AI 软件栈确认

“确认 CUDA、cuDNN、TensorRT 版本”可以称为：

> 端侧 GPU 推理软件栈确认与兼容性核验。

这些组件都属于 NVIDIA 的软件生态。

## 4.1 软件栈关系

```text
机器人策略应用
        ↓
PyTorch / ONNX Runtime / TensorRT
        ↓
cuDNN / cuBLAS 等加速库
        ↓
CUDA Runtime
        ↓
Jetson Linux / NVIDIA Driver
        ↓
Jetson Orin GPU
```

## 4.2 各组件作用

### CUDA

负责让程序调用 NVIDIA GPU，包括：

- GPU Kernel 执行；
- 显存管理；
- CPU—GPU 数据传输；
- 并行计算基础能力。

### cuDNN

基于 CUDA 的深度学习算子库，主要加速：

- 卷积；
- 池化；
- 归一化；
- 激活函数；
- 部分 Attention 和 RNN 运算。

### TensorRT

用于模型推理优化：

- 读取 ONNX；
- 图优化；
- 算子融合；
- Kernel 选择；
- FP16 / INT8；
- 生成 TensorRT Engine；
- 低延迟推理。

### JetPack

Jetson 的整套基础软件环境，通常包含：

- Jetson Linux；
- Ubuntu；
- NVIDIA 驱动；
- CUDA；
- cuDNN；
- TensorRT；
- VPI；
- 多媒体组件。

在 Orin 上应优先确定 JetPack 版本，再确认与之配套的 CUDA、cuDNN 和 TensorRT，而不是随意单独升级组件。

---

# 5. 第三阶段：环境固化

## 5.1 什么是环境固化

环境固化不是“软件已经安装好了”，而是：

> 将一套已经验证能正确运行模型的软件、硬件、依赖和配置完整记录并封装，使系统重装、换机或长期维护后仍能复现。

环境固化要解决：

```text
今天能跑
重装后还能跑
换一台同型号 Orin 仍能跑
```

## 5.2 需要固化的六层内容

### 第一层：硬件

记录：

- Orin 型号；
- 内存；
- 存储；
- 功耗模式；
- 散热配置。

### 第二层：系统和 JetPack

记录：

- JetPack；
- L4T；
- Ubuntu；
- Kernel；
- CPU 架构。

### 第三层：GPU 软件栈

记录：

- CUDA；
- cuDNN；
- TensorRT；
- cuBLAS 等关键库。

### 第四层：推理运行时

明确采用：

- PyTorch；
- ONNX Runtime GPU；
- TensorRT；
- Torch-TensorRT；
- 自定义 TensorRT Plugin。

### 第五层：Python 和应用依赖

例如：

```text
Python
PyTorch
torchvision
NumPy
OpenCV
transformers
diffusers
einops
onnx
机械臂 SDK
ROS 相关依赖
```

### 第六层：模型业务配置

包括：

- 模型权重；
- ONNX；
- TensorRT Engine；
- normalization stats；
- 相机顺序；
- qpos 顺序；
- action 顺序；
- 安全阈值；
- 推理频率；
- 模型版本。

## 5.3 Docker 的作用

Docker 可以固化：

- Python；
- 模型代码；
- PyTorch；
- ONNX；
- 用户态依赖；
- 模型文件；
- 启动命令。

Docker 不能完全固化：

- JetPack；
- Linux Kernel；
- NVIDIA 驱动；
- 底层相机驱动；
- 硬件设备节点；
- 部分机械臂 SDK Kernel Module；
- Orin 功耗模式。

因此推荐：

```text
宿主机：
JetPack + 驱动 + 硬件 SDK

Docker：
模型代码 + Python 依赖 + 推理服务
```

## 5.4 环境自检

建议制作：

```bash
python3 tools/environment_check.py
```

预期输出：

```text
[PASS] Device: Jetson Orin NX
[PASS] JetPack version
[PASS] CUDA version
[PASS] cuDNN version
[PASS] TensorRT version
[PASS] PyTorch CUDA available
[PASS] Camera available
[PASS] Robot SDK reachable
[PASS] Model checksum correct
[PASS] Test vector passed
```

只有全部通过，策略程序才允许进入可控制状态。

---

# 6. 第四阶段：在 Orin 上跑通原始模型

第一步不要急着转 TensorRT。

先使用与训练端接近的 PyTorch 模型在 Orin 上完成：

```text
模型加载
输入读取
预处理
模型推理
后处理
输出 action
```

检查：

- 模型是否能加载；
- CUDA 是否可用；
- 输出 shape 是否正确；
- 是否出现 NaN 或 Inf；
- 显存是否足够；
- 单次推理耗时；
- 连续运行是否稳定。

---

# 7. 第五阶段：主机—Orin 数值一致性验证

使用相同输入分别在训练主机和 Jetson Orin 上运行模型。

比较：

```text
action_host
action_orin
```

检查指标：

- shape；
- 最大绝对误差；
- 平均绝对误差；
- 相对误差；
- NaN / Inf；
- 多个 Episode 的动作分布；
- 动作平滑性。

生成式模型需要固定：

- 随机种子；
- 初始噪声；
- 采样器；
- 去噪次数；
- 推理模式。

否则两次输出不同不一定说明部署错误。

---

# 8. 第六阶段：端侧 Benchmark

Benchmark 不只看 FPS。

## 8.1 需要测量

- 图像预处理耗时；
- 力触预处理耗时；
- 模型推理耗时；
- 动作后处理耗时；
- 端到端延迟；
- P50；
- P95；
- P99；
- 显存占用；
- CPU 内存；
- GPU 利用率；
- 功耗；
- 温度；
- 是否降频；
- 连续运行稳定性。

## 8.2 为什么 P99 重要

平均延迟达标，不代表闭环稳定。偶发长尾卡顿可能导致：

- Action Chunk 耗尽；
- 使用过期观测；
- 控制目标不连续；
- 接触任务响应延迟。

## 8.3 频率分层

```text
策略推理：5～20 Hz
Action Chunk 更新：10～50 Hz
控制器接口：100 Hz
底层伺服：500～1000 Hz
```

模型不负责高频电机伺服。

---

# 9. 第七阶段：模型格式转换与推理优化

推荐路线：

```text
PyTorch FP32
      ↓
PyTorch FP16
      ↓
ONNX
      ↓
TensorRT FP16
      ↓
必要时尝试 INT8
```

注意是 **FP16**，不是 F12。

## 9.1 FP16

优点：

- 显存占用降低；
- Tensor Core 加速；
- 通常精度损失较小。

第一版端侧部署优先使用 FP16。

## 9.2 INT8

优点：

- 延迟和吞吐可能进一步提升；
- 显存占用降低。

风险：

- 需要校准数据；
- 动作数值可能偏移；
- 生成模型和接触控制模型可能更敏感；
- 必须重新验证闭环成功率。

---

# 10. ONNX 与 TensorRT

## 10.1 ONNX 的作用

ONNX 是中间模型格式，适合：

- 跨框架；
- 模型结构检查；
- TensorRT 构建输入；
- 保留较强可移植性。

## 10.2 TensorRT Engine 的作用

TensorRT Engine 是针对目标设备和具体环境优化的部署产物。

它可能依赖：

- GPU 架构；
- TensorRT 版本；
- CUDA 版本；
- 输入 Shape；
- FP16 / INT8 配置；
- Builder 参数。

因此应保存：

```text
ONNX：可重建的中间模型
Engine：目标 Orin 上生成的部署模型
```

不要只保存 `.engine`。

---

# 11. 是否需要拆分模型

模型不一定必须拆成多个 ONNX。

如果整体模型：

- 可成功导出；
- 算子均支持；
- 性能达标；
- 数值一致；
- 维护方便；

可以保留整体 ONNX。

需要拆分的常见情况：

- 模型存在动态循环；
- ONNX 不支持部分算子；
- 扩散去噪循环难以整体导出；
- 视觉编码重复计算；
- 需要分别优化不同模块；
- 需要缓存中间特征。

## 11.1 Diffusion Policy 的典型拆分

```text
图像编码器
状态编码器
条件融合
去噪网络
Scheduler
动作后处理
```

推荐：

```text
图像编码器 → TensorRT
去噪网络   → TensorRT
Scheduler  → Python 或 C++
动作后处理 → Python 或 C++
```

视觉特征在一次动作生成过程中通常只需计算一次。

---

# 12. 常见端侧优化手段

## 12.1 固定输入 Shape

固定：

- Batch Size；
- 图像尺寸；
- 观测长度；
- Action Horizon；
- 动作维度。

固定 Shape 更容易被 TensorRT 优化。

## 12.2 减少重复计算

- 视觉编码一次；
- 缓存语言 Embedding；
- 缓存固定任务参数；
- 缓存历史视觉特征；
- 避免 CPU—GPU 反复复制；
- 预分配 Buffer；
- GPU 端完成部分预处理。

## 12.3 减少生成迭代次数

例如：

```text
100 步扩散
→ 20 步
→ 10 步
→ 4 步蒸馏模型
```

必须同时评估：

- 延迟；
- 动作误差；
- 动作平滑度；
- 任务成功率；
- 接触任务表现。

## 12.4 轻量化模型

可考虑：

- 降低输入分辨率；
- 更轻视觉编码器；
- 减少 Transformer 层；
- 减少隐藏维度；
- 减少 Action Horizon；
- 模型蒸馏；
- 剪枝；
- 量化。

## 12.5 异步流水线

线程或进程可拆分为：

```text
传感器读取
图像预处理
多模态时间同步
GPU 推理
动作后处理
动作执行
日志记录
```

模型推理不能阻塞底层安全和控制循环。

---

# 13. Observation Adapter

输入适配层负责将真实机器人数据转换成训练时模型看到的数据。

包括：

- 相机顺序；
- RGB / BGR；
- resize；
- crop；
- 图像归一化；
- qpos 排序；
- 力觉零偏；
- 力觉坐标系；
- 触觉 baseline；
- 历史帧组织；
- 时间同步；
- validity mask。

输入对齐错误时，程序可能正常运行，但机器人行为会完全错误。

---

# 14. Action Adapter

Action Adapter 将模型输出转换成现有控制器接口可接受的目标动作。

需要处理：

- 反归一化；
- 动作维度；
- 关节顺序；
- 左右臂映射；
- 角度与弧度；
- 米与毫米；
- 绝对动作和增量动作；
- 坐标系；
- 四元数顺序；
- Action Chunk；
- 插值和平滑。

## 14.1 反归一化

训练时若使用：

```text
a_norm = (a - mean) / std
```

部署时：

```text
a = a_norm × std + mean
```

必须使用训练数据对应的同一组统计量。

## 14.2 增量动作转换

模型输出：

```text
Δq
```

控制器需要绝对关节位置：

```text
q_target = q_current + Δq
```

## 14.3 动作频率转换

模型动作 20 Hz，控制器接口 100 Hz：

```text
20 Hz 模型动作
       ↓
轨迹插值与平滑
       ↓
100 Hz 控制器目标
```

---

# 15. 生成式 Action Chunk 的执行

假设模型一次输出：

```text
[a0, a1, ..., a15]
```

不建议全部盲目执行。

推荐滚动时域：

```text
预测 16 步
只执行前 4 步
重新获取观测
重新预测 16 步
```

需要处理：

- 新旧 Action Chunk 衔接；
- temporal ensemble；
- 动作队列；
- 推理超时；
- 队列耗尽；
- 旧动作过期；
- 平滑切换。

---

# 16. 与现有控制系统的接入

假设已有控制程序接口：

```python
robot_controller.send_target(target_action)
```

模型部署主循环：

```python
while system.is_running():
    raw_observation = sensor_manager.get_latest()

    model_observation = observation_adapter.convert(
        raw_observation
    )

    model_action = policy.predict(
        model_observation
    )

    candidate_action = action_adapter.convert(
        model_action=model_action,
        current_state=raw_observation.robot_state,
    )

    executable_action = safety_supervisor.check_and_limit(
        candidate_action,
        current_state=raw_observation.robot_state,
    )

    robot_controller.send_target(
        executable_action
    )
```

模型输出只能称为“候选目标动作”。经过适配和安全检查后，才是“可执行动作”。

---

# 17. 安全与异常管理

即使已有机械臂安全模块，模型接入层仍应检查：

- 输入数据是否超时；
- 相机是否断流；
- 力触数据是否有效；
- 模型推理是否超时；
- 模型输出是否为 NaN / Inf；
- 动作是否突然跳变；
- Action Chunk 是否耗尽；
- 模型版本是否匹配机器人；
- normalization stats 是否匹配；
- 控制器是否可用。

高频安全保护不能依赖模型：

```text
力触数据 → 策略模型，用于决策
力触数据 → 安全模块，用于立即限力或停止
```

物理急停必须独立于 Orin 和模型进程。

---

# 18. 推荐运行状态机

```text
INITIALIZING
      ↓
WAITING_FOR_SENSORS
      ↓
MODEL_READY
      ↓
SHADOW_MODE
      ↓
ARMED
      ↓
RUNNING
      ↓
FAULT / STOPPED
```

状态说明：

- `INITIALIZING`：初始化环境和依赖；
- `WAITING_FOR_SENSORS`：等待相机、状态、力触；
- `MODEL_READY`：模型已加载；
- `SHADOW_MODE`：模型推理但不执行；
- `ARMED`：等待人工使能；
- `RUNNING`：闭环控制；
- `FAULT`：异常，停止发送动作；
- `STOPPED`：正常停止。

---

# 19. 五级验证流程

## 第一级：主机离线回放

- 读取历史 Episode；
- 运行模型；
- 检查输出范围；
- 检查动作平滑度；
- 不连接机器人。

## 第二级：Orin 离线回放

- 在 Orin 读取同一 Episode；
- 模拟实时传感器输入；
- 验证延迟；
- 验证主机—端侧一致性。

## 第三级：Shadow Mode

- 接真实传感器；
- 模型实时输出；
- 不发送到机械臂；
- 记录模型建议动作。

## 第四级：低速空载实机

- 10% 速度；
- 低力矩限制；
- 空工作区；
- 操作员手持急停；
- 单步或短 Action Chunk 执行。

## 第五级：真实任务闭环

逐步增加：

- 速度；
- 物体变化；
- 初始位置变化；
- 接触任务；
- 力触闭环；
- 连续运行时长。

---

# 20. 部署目录建议

```text
robot_deployment/
├── src/
│   ├── observation_adapter/
│   ├── policy_inference/
│   ├── action_adapter/
│   ├── safety_supervisor/
│   ├── action_executor/
│   └── deployment_monitor/
├── models/
│   └── policy_release_v1/
├── config/
│   ├── sensors.yaml
│   ├── model.yaml
│   ├── robot_mapping.yaml
│   └── safety_limits.yaml
├── tools/
│   ├── environment_check.py
│   ├── test_inference.py
│   ├── compare_outputs.py
│   ├── benchmark.py
│   └── build_tensorrt.py
├── scripts/
│   ├── start_shadow.sh
│   ├── start_policy.sh
│   └── stop_policy.sh
├── docker/
│   └── Dockerfile
├── tests/
│   ├── test_vectors/
│   └── offline_replay/
└── logs/
```

---

# 21. 发布清单

```json
{
  "model_version": "1.0.0",
  "git_commit": "abc1234",
  "training_dataset": "dataset_release_xxx",
  "normalization_version": "stats_v1",
  "observation_schema_version": "obs_v1",
  "action_schema_version": "action_v1",
  "jetpack_version": "actual_version",
  "cuda_version": "actual_version",
  "cudnn_version": "actual_version",
  "tensorrt_version": "actual_version",
  "robot_configuration": "dual_arm_hand_v1",
  "precision": "FP16",
  "model_checksum": "sha256..."
}
```

只要以下任一项变化，就需要重新做一致性验证和 Benchmark：

- JetPack；
- CUDA；
- cuDNN；
- TensorRT；
- PyTorch；
- 模型；
- normalization stats；
- Observation Schema；
- Action Schema；
- 机器人配置。

---

# 22. 面试表述建议

如果确实完成过完整实机部署，可以表述为：

> 我做过机器人策略模型在 Jetson Orin 上的端侧部署。首先固化 JetPack、CUDA、cuDNN、TensorRT 和 PyTorch 环境，然后使用固定测试向量验证训练主机和 Orin 的数值一致性。随后将模型导出为 ONNX，并使用 TensorRT FP16 优化；针对生成式策略，我拆分视觉编码器和去噪网络，缓存视觉特征并减少重复编码，同时评估去噪步数对延迟和闭环成功率的影响。最后实现 Observation Adapter 和 Action Adapter，将模型输出反归一化并完成关节顺序、单位、坐标系和控制频率对齐，再通过现有控制器接口进行 Shadow Mode、低速实机和闭环任务测试。

如果目前主要完成的是方案设计、离线验证或模拟实践，应表述为：

> 我系统梳理并实践过 Jetson Orin 端侧部署流程，包括环境固化、主机—端侧一致性验证、ONNX/TensorRT 推理优化、输入输出适配和控制器接入方案；目前对完整实机上线流程和关键风险点有较完整的工程理解。

不要把仅阅读和方案设计描述成已经完成真实机器人量产部署。面试官通常会继续追问：

- TensorRT Engine 为什么不能随意跨设备使用；
- 为什么关注 P99 延迟；
- FP16 和 INT8 如何选择；
- Diffusion Policy 为什么要拆视觉编码器；
- 输入和输出如何对齐；
- 推理超时怎么处理；
- Shadow Mode 是什么；
- 模型如何接入原控制器；
- 力触断流时怎么办。

---

# 23. 面试快速回答模板

## 问：模型怎样部署到机械臂？

> 模型不会直接控制硬件，而是部署在 Jetson Orin 上作为策略推理模块。它读取相机、机器人状态和力触等观测，输出候选目标 Action。经过输入输出适配、反归一化、关节顺序和坐标系对齐，以及安全检查后，再调用已有机械臂控制器接口，由原控制系统完成轨迹生成和底层执行。

## 问：端侧部署最主要的工作是什么？

> 主要是四部分：第一是固化 JetPack、CUDA、cuDNN、TensorRT 和 Python 依赖；第二是验证主机和 Orin 对相同输入的数值一致性；第三是通过 ONNX、TensorRT、FP16、模型拆分、特征缓存和减少生成迭代完成推理优化；第四是实现 Observation Adapter 和 Action Adapter，将模型正确接入现有控制系统。

## 问：为什么不直接把模型输出发给电机？

> 模型输出只是候选动作，可能存在越界、跳变、超时或 NaN，因此必须经过动作适配和安全监督。电机控制、实时伺服、限位、碰撞和急停仍由原有控制系统和独立安全模块负责。

## 问：为什么需要主机—端侧一致性验证？

> 因为不同硬件、精度和推理运行时可能带来数值差异。通过固定输入、固定随机种子和参考输出，可以确认模型转换和端侧运行没有改变模型语义，并为后续 FP16 或 TensorRT 优化建立基线。

## 问：为什么关注 P99 延迟？

> 机器人闭环控制不仅怕平均速度慢，也怕偶发长尾卡顿。即使平均延迟满足控制频率，偶尔的高延迟也可能导致动作队列耗尽、使用过期观测或控制不连续，所以必须评估 P95、P99 和最长延迟。

---

# 24. 最终总结

端侧模型部署可以总结为：

```text
模型协议固化
→ Orin 环境固化
→ PyTorch 跑通
→ 数值一致性验证
→ 性能 Benchmark
→ ONNX / TensorRT / FP16 优化
→ 模型模块拆分与缓存
→ Observation Adapter
→ Action Adapter
→ 安全检查
→ 接入已有控制器
→ 离线回放
→ Shadow Mode
→ 低速实机
→ 闭环运行
```

核心原则：

> 模型负责生成目标，控制系统负责安全执行。
