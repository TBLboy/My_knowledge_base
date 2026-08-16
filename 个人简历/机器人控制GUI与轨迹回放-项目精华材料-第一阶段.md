# 机器人控制 GUI / 轨迹录制回放项目精华材料（第一阶段）

- **项目状态：**第一阶段精华材料，非最终简历文案
- **用户确认身份：**个人作品
- **主要来源：**
  - `工程记录/gui/.project-log/requirements.md`
  - `工程记录/gui/.project-log/architecture/software-architecture.md`
  - `工程记录/gui/.project-log/architecture/communication.md`
  - `工程记录/gui/.project-log/architecture/hardware-architecture.md`
  - `工程记录/gui/.project-log/architecture/threading-model.md`
  - `工程记录/gui/.project-log/current-session.md`
  - `工程记录/gui/.project-log/progress.md`

## 1. 项目定位

面向双臂灵巧手机器人操作员，个人设计并实现一套机器人控制 GUI，支持本地 Tkinter 和浏览器 Web 两种入口，共享统一的机械臂/灵巧手服务层，并扩展轨迹录制、法兰 delta 回放、先进运动控制和多用户访问能力。

## 2. 用户负责范围

用户确认该项目为个人作品。可按完整工程交付口径组织：

- 独立设计 Tkinter + Web 双模式 GUI 架构。
- 独立实现共享 Service Layer，避免两个前端重复编写机器人控制逻辑。
- 实现机械臂控制：关节状态、使能、急停、停止、Jog、Servo、RT Follow、Drag、Comfort 等。
- 实现灵巧手 CAN 连接、角度/姿态控制和左右侧绑定。
- 实现任务页、预设位姿、切割任务和高级运动控制页面。
- 实现 FastAPI、WebSocket、登录、httpOnly session cookie、SQLite 用户和 per-user worker 隔离。
- 实现法兰轨迹录制、清洗、delta 生成、IK 预求解和 MoveAbsJ 批量回放。
- 处理 SDK 阻塞、离线断连、Tkinter 主线程冻结和回放 IK 失败等工程问题。

## 3. 系统架构

```text
Tkinter GUI                    Web Browser
      ↓                              ↓
      └────── shared services ──────┘
             ├─ arm control
             ├─ hand control
             ├─ registry / workspace
             └─ logger
                    ↓
        ROS2 services + xCore SDK + CAN
```

Web 模式额外采用：

```text
Browser → FastAPI/WebSocket → per-user worker subprocess
        → stdin/stdout JSON relay → robot services/SDK
```

核心设计：

- 表现层负责页面和交互。
- Service Layer 负责 ROS2、SDK 和 CAN 调用。
- 操作线程负责耗时机械臂/手部调用。
- Tkinter 主线程通过 `after()` 安全更新 UI。
- Web 用户通过独立 worker 进程隔离操作上下文。

## 4. GUI 功能范围

### 4.1 Arm + Hand 主页面

- 左右侧选择与机械臂/灵巧手绑定。
- 机械臂实时关节状态读取。
- 机械臂使能、急停、停止运动。
- 灵巧手连接、角度和预设姿态控制。
- 预设位姿读取与发送。
- 离线状态、连接失败和受限日志提示。

### 4.2 Advanced Arm 页面

- Servo Move Segment / Path。
- RT Follow。
- Drag 示教、轨迹录制和保存。
- 碰撞检测开关。
- Comfort / 关节舒适度优化参数。
- 运动速度、加速度、最大线速度和角速度等参数配置。

### 4.3 Tasks 页面

- Slice Cycle 切割任务。
- cycle 数、拖动距离、切入深度、步进、切割时长和回撤时长等参数。
- 阻抗控制开关和派生总步进距离显示。

### 4.4 Web 页面

- 登录、注册和用户设置。
- FastAPI + WebSocket 实时控制。
- SQLite 用户和 session 数据。
- httpOnly cookie。
- per-user subprocess 隔离。
- systemd + nginx 部署路径。

## 5. 轨迹录制与 delta 回放

### 5.1 录制和预处理

- 采集原始法兰位姿。
- 过滤离群点和重复点。
- 进行位置滑动平均和旋转矩阵 SVD 姿态平均。
- 按空间弧长重采样轨迹。
- 计算并保存相对当前起点的 delta 轨迹。
- 通过 manifest 记录来源、处理方式和 SHA-256。

### 5.2 回放链路

```text
读取当前 flangeInBase
  → 展开 T_current @ Delta_i
  → 转为 SDK IK 输入
  → 全轨迹 calcIk
  → 关节限位与相邻解连续性检查
  → 复用 MoveAbsJ 批量回放
  → 终点法兰位姿回读确认
```

关键安全设计：

- 不在 IK 全部通过前发送实际运动。
- IK 失败时不触发关节回放。
- 检查关节范围和相邻解跳变。
- 轨迹执行后读取终点位姿，而不是只相信控制器返回的“成功”。
- 识别并记录 delta 轨迹对当前起点、可达性和 IK 分支的依赖。

## 6. 关键工程问题与解决方向

| 问题 | 解决方向 |
| --- | --- |
| SDK 网络调用阻塞 Tkinter 主线程 | 将轮询、Stop、Fill From Live 等操作放入后台线程 |
| 机器人断连时 GUI 启动卡死 | 延迟连接、后台轮询、离线状态提示和锁超时关闭 |
| GUI 与 Web 重复实现控制逻辑 | 抽取共享 Service Layer |
| Web 多用户同时操作风险 | 每用户 worker subprocess 和会话隔离 |
| Delta 首点 IK 失败 | 首点直接使用当前法兰状态，后续点再做 IK |
| 回放显示成功但机械臂未动 | 批量 append、单次 moveStart、等待 moving/结束并回读终点 |
| 离线平滑改变法兰轨迹后真机 IK 失败 | 撤回不安全平滑方案，恢复真机验证基线 |
| 不同起点下 delta 回放不泛化 | 识别为兼容起点回放语义，提出全轨迹多分支 IK 和起点预检方向 |

## 7. 记录中的验证与结果

- GUI Phase 1–5 完成：shell、页面拆分、Arm + Hand、灵巧手、预设位姿、实时读数、高级运动和 Tasks 页面。
- Web Phase W 完成：登录、用户隔离、worker、设置同步和部署文件。
- 多次 `py_compile`、`compileall`、单元测试和离线 smoke test 通过。
- delta 轨迹回放已在真机验证成功过；后续实验进一步识别了任意起点泛化的边界。
- 记录中出现 9/9、12/12 等针对性测试结果；最终简历应根据具体项目版本选择最准确数字。
- 硬件测试状态存在阶段差异：部分旧 GUI 路径已真机验证，完整 Web/全部高级能力的硬件验收仍有边界。

## 8. 可用于简历的价值标签

- Tkinter / FastAPI / WebSocket
- ROS2 / xCore SDK / CAN
- 机器人控制 GUI
- 共享服务层和多前端架构
- 多线程、进程隔离和实时状态回读
- 轨迹录制、滤波、重采样和 delta 回放
- IK 预检、关节限位和安全回退
- 真机调试与硬件异常处理

## 9. 第一版简历表达方向（非最终文案）

### 稳健版方向

> 独立设计并实现双模式机器人控制 GUI，采用 Tkinter/Web 前端共享 Service Layer，接入 ROS2、xCore SDK 与 CAN 灵巧手控制；完成机械臂/灵巧手控制、轨迹录制、法兰 delta 回放、IK 预检和多用户 Web 访问，并通过多线程与进程隔离解决 SDK 阻塞和 GUI 卡顿问题。

### 强表达版方向

> 独立完成机器人控制 GUI 从架构到真机验证，构建 Tkinter + FastAPI/WebSocket 双入口及共享机器人服务层，覆盖双臂灵巧手控制、拖动示教、轨迹清洗、delta 法兰回放和全轨迹 IK 安全预检；针对 SDK 阻塞、断连卡死、回放假成功和 IK 分支不可达等问题完成工程化修复。

## 10. 待用户补充的信息

1. 该个人作品的实际开发时间、是否与切豆腐/老板项目共用代码。
2. GUI 是否实际被团队或现场操作员使用。
3. 真机验证的具体路径、成功次数和机器人型号。
4. Web 模式是否真正部署给多用户使用，还是完成了工程实现但未正式部署。
5. 轨迹录制和 delta 回放是否由你独立设计，还是基于已有底层能力扩展。
