# Current Session
## （第三轮：大批量修改收口）

### 本轮修改清单

| 模块 | 改动内容 |
|------|----------|
| 进度条 | 4圆圈→3圆圈，删"展示刀工"；由 `/api/task/current` 的 `recipeCode+status` 驱动点亮规则 |
| 进度条点亮规则 | cucumber+running→前两圈亮；cucumber+finished→三圈全亮；其余全灰 |
| 连接线延长 | 两端从 0 延到 16dp |
| 主状态显示 | 左上角 `taskTitle` 增加 recipeCode 筛选，非 cucumber 统一显示"准备制作" |
| 紧急停止 | 调用接口从 `/api/task/control` 改为 `/api/task/start`，传 `recipeCode:"pause"` |
| 紧急停止 loading key | 右侧大按钮 loading 判定从 `"pause_task"` 修正为 `"emergency_stop"` |
| 急停/PAUSED 状态收口 | 自检、拖拽、机械臂动作等 idle check 均补上 `TaskStatus.EMERGENCY_STOP` 兼容分支 |
| `productionTaskRunning` | 轮询到 PAUSED 时也清零 |
| 右手黄瓜按钮 | 取消任务运行期保留可点击的例外，现与其它按钮一致（任务中置灰） |
| 自检解析 | 从仅 HTTP 200 判定改为真实解析服务端 JSON body，逐项检查 `items[].status` |
| 右手放黄瓜 taskId 缓存 | `PendingTaskCache` 机制就位，pick_cucumber 成功时写入 taskId |
| 按钮灰化 | 缓存有值且 taskName=="右手抓黄瓜" 时灰掉该按钮 |

## Last Updated

- 2026-07-13 (第二轮)
- 2026-07-13 (第三轮)

## Current Objective

- **方案A已实现**：pick_cucumber → place_cucumber 的 task_id 传递链完成。
- 客户端侧缓存机制（PendingTaskCache）就绪，支持同链路内 task_id 流转。
- 第三轮：进度条重做、紧急停止 API 对齐、自检解析对齐服务端、急停+PAUSED 状态统一收口、右手黄瓜按钮任务中置灰。
- 下一步：平板部署验证 pick_cucumber → place_cucumber 链路。

## Key Decisions (Current Context)

| 决策 | 结论 |
|------|------|
| pick_cucumber→place_cucumber task_id 传递方案 | 客户端缓存 PendingTaskCache {taskId, taskName}，pick 成功时写入，place 成功时消费清空 |
| 缓存失效条件 | 右臂初始位置/机器人恢复初始位置/右臂开启拖拽模式/紧急停止 |
| 按钮灰化条件 | 缓存有值且 taskName=="右手抓黄瓜" → "右手抓黄瓜"按钮灰化 |

## 工程状态

```text
dex_app/  ← 当前客户端主工程
├── navigation/AppNavGraph.kt          (startDestination 已恢复为 Login)
├── core/network/ApiEndpointStore.kt   (DEFAULT_HOST 改为 10.0.2.2)
├── core/network/RobotCookingApi.kt    (6 个接口定义)
└── feature/
    ├── login/presentation/            (固定账号 dex001/123456)
    ├── selfcheck/presentation/        (对接 /api/robot/self-check，5 次串行 POST)
    └── dashboard/presentation/        (主控面板；新增 PendingTaskCache，pick_cucumber→place_cucumber 链路就绪)

dexbot_ros2_ws-dev_715_cut_cucumbers/  ← 当前服务端工程
└── src/dexbot_web_api/dexbot_web_api/
    ├── app.py          (7 个 HTTP 端点)
    ├── models.py       (Pydantic 请求/响应模型)
    ├── state_store.py  (线程安全内存状态；save_task_target/get_task_target)
    ├── ros_bridge.py   (ROS2 service/action 调用封装)
    └── web_api_node.py (ROS2 Node + uvicorn 启动入口)
```

## Completed This Session

- **方案A实现** — pick_cucumber → place_cucumber task_id 传递链
  - 新增 `PendingTaskCache` 数据类 + `pendingTaskCache` 变量
  - `requestArmTaskControl` 重写：pick_cucumber成功时从响应体提取taskId缓存，place_cucumber时从缓存取taskId传服务端
  - `afterSuccess` 签名从 `() → Unit` 改为 `(String) → Unit`，回调可拿响应体
  - 4个缓存失效条件：右臂初始位置/机器人恢复初始位姿/右臂开启拖拽/紧急停止
  - 新增 `rightCucumberPicked` 状态字段控制按钮灰化
  - `BUILD SUCCESSFUL`

## Verification

- `./gradlew :app:assembleDebug` → BUILD SUCCESSFUL

## Next Steps

1. 平板部署验证 pick_cucumber → place_cucumber 完整链路。
2. 验证缓存生命周期：抓→放 / 抓→右臂复位→放（应提示错误） / 抓→急停→刮清重新抓取。
3. 后续可扩展 cache 机制用于其他 task_id 依赖场景。

## 2026-07-13

### 修复：左上角状态显示丢失菜名

- **问题**：非 cucumber 任务时（如左手抓刀），左上角状态只显示"准备制作"，未带上菜名
- **根因**：`taskTitle` 函数中，`recipeCode != "cucumber"` 的分支直接 `return "准备制作"`，没有拼接 `recipeName`
- **修复**：改为 `return "准备制作：${task.recipeName}"`
- **commit**: `5865f90`
- **分支**: `dev_dex_app`
- **已推送** ✅
