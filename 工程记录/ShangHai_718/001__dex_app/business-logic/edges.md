# Business Logic Edges

## Call Chain (新架构)

```
Screen (UiEvent)
  → ViewModel (调用 UseCase, 更新 StateFlow<UiState>)
    → UseCase (单个业务动作, 调用 Repository 接口)
      → Repository (interface, domain 层定义)
        → RepositoryImpl (data 层实现, 协调数据来源)
          → RemoteDataSource / LocalDataSource
            → Retrofit Api / Room Dao
              → HTTP Server / SQLite
```

## Edges

---

```yaml
edge_id: E0_LOGIN
from: LOGIN
to: SELF_CHECK
path: main
status: pending (待按新架构重新实现)
method: 用户输入账号密码，点击登录，触发自检流程
execution_chain:
  - LoginScreen: 用户输入账号/密码
  - LoginViewModel: 处理 UiEvent.LoginClicked
  - (无 UseCase，纯本地验证)
  - 导航到 SelfCheckScreen (Navigation Compose navigate)
  - SelfCheckViewModel: 调用 CheckRobotUseCase
  - CheckRobotUseCase → RobotRepository.selfCheck()
  - RobotRepositoryImpl → RobotRemoteDataSource → RobotApi.selfCheck()
  - 轮询 POST /api/robot/self-check (后端逐项检测并返回进度)
  - 全部完成 → navigate to MainDashboard
inputs:
  - loginAccount, loginPassword
outputs:
  - navigate to SELF_CHECK
interfaces:
  - POST /api/robot/self-check (新架构对接真实接口)
notes:
  - 新架构不再使用 FakeRepository 模拟自检
  - 自检进度由后端 API 返回值驱动，前端不做假
```

---

```yaml
edge_id: E1
from: A (APP就绪)
to: B (用户操作已触发)
path: main
status: pending (待按新架构重新实现)
method: 用户通过 Compose UI 触发操作，ViewModel 路由到对应 UseCase
execution_chain:
  - 用户点击 Compose UI 按钮
  - Screen 生成对应 UiEvent，调用 ViewModel 方法
  - ViewModel 调用对应 UseCase:
    
    RecipeSelected(recipeId) → SelectRecipeUseCase:
      - 纯本地操作，更新 UiState.recipes 选中状态
    
    StartCookingClicked → StartTaskUseCase(recipeCode):
      - 调用 TaskRepository.startTask()
      - 成功后刷新任务状态
    
    TaskCommandClicked(command) → ControlTaskUseCase(taskId, command):
      - 调用 TaskRepository.controlTask()
      - 成功后刷新
    
    RobotActionClicked(spec) → RobotActionUseCase(arm, action, target):
      - 调用 RobotRepository.sendAction()
      - 成功后刷新日志
    
    RequestModeSwitch(targetMode) → showPinDialog (本地 UI 状态)
inputs:
  - UiEvent (按 feature 独立定义)
outputs:
  - UseCase 调用已发起
notes:
  - 新架构中 UiEvent 按 feature 拆分，不再是单一大 UiAction
  - 每个 UseCase 只做一个业务动作
  - ViewModel 通过 Hilt 注入 UseCase
```

---

```yaml
edge_id: E2
from: B (用户操作已触发)
to: C (请求已发送)
path: main
status: pending (待按新架构重新实现)
method: RepositoryImpl 封装 HTTP 请求并发送
execution_chain:
  - UseCase 调用 Repository 接口方法
  - RepositoryImpl (data 层):
    - 调用 RemoteDataSource.xxx() 发 HTTP 请求
    - 可选: 先读 local 缓存 → 网络 → 更新 local
  - Retrofit Api 接口定义:
    interface RobotApi {
      @POST("/api/robot/self-check") suspend fun selfCheck(@Body req: SelfCheckRequest): SelfCheckResponse
    }
    interface TaskApi {
      @POST("/api/task/start") suspend fun startTask(@Body req: StartTaskRequest): TaskResponse
      @GET("/api/task/current") suspend fun currentTask(@Query("robotId") robotId: String, @Query("taskId") taskId: String?): TaskStatusResponse
      @POST("/api/task/control") suspend fun controlTask(@Body req: ControlRequest): ControlResponse
    }
  - OkHttp Interceptor 自动添加 header/token/log
  - 返回 NetworkResult<T>
inputs:
  - UseCase 传入的参数
outputs:
  - NetworkResult<T>
interfaces:
  - Retrofit + OkHttp + Kotlinx Serialization
error_handling:
  - OkHttp ErrorHandler: 超时/4xx/5xx/网络错误 → NetworkResult.Error
  - AuthInterceptor: 自动添加 Token
notes:
  - Api 接口定义严格按照 robot_cooking_api_protocol.md
  - DTO 命名: XxxRequestDto / XxxResponseDto，与协议 JSON 字段一致
  - 统一 baseUrl 在 Hilt NetworkModule 中配置
```

---

```yaml
edge_id: E3
from: C (请求已发送)
to: D (响应已接收)
path: main
status: pending (待按新架构重新实现)
method: 解析响应，DTO → Domain Model 转换
execution_chain:
  - RemoteDataSource 接收 Retrofit Response
  - 解析 JSON → DTO (Kotlinx Serialization 自动)
  - Mapper: DTO → Domain Model (Entity → Domain Model)
  - RepositoryImpl 返回 Domain Model 给 UseCase
  - UseCase 返回 Domain Model 给 ViewModel
  - ViewModel: Domain Model → UiState 字段映射
inputs:
  - JSON Response / DTO
outputs:
  - Domain Model (domain 层)
  - 最终: UiState 更新
data_format:
  - DTO (data 层) → Mapper → Domain Model (domain 层) → ViewModel → UiState (presentation 层)
notes:
  - DTO 和 Entity 绝不暴露到 presentation 层
  - Mapper 是唯一的数据转换入口
  - 旧 APP 的 ApiModels.kt 数据结构可作为 DTO 设计参考
```

---

```yaml
edge_id: E4
from: D (响应已接收)
to: E (结果已展示)
path: main
status: pending (待按新架构重新实现)
method: Compose UI 根据 StateFlow 变化自动 recompose
execution_chain:
  - ViewModel 更新 _uiState: MutableStateFlow<XxxUiState>
  - Compose Screen 通过 collectAsState() 订阅
  - UiState 变更触发 recomposition
  - 各 Composable 根据最新 state 渲染
  - 特殊行为:
    - 轮询: ViewModel 中 while(true) + delay 定时拉取
    - 日志自动滚动: LaunchedEffect(logs.size) → animateScrollToItem
    - Dev/User 布局: 根据 UiState.workMode 分支
    - 弹窗/Overlay: 根据 UiState 中的 Boolean 字段
inputs:
  - UiState (各 feature 独立)
outputs:
  - Compose UI recomposition
notes:
  - UI 完全不感知数据来源 (HTTP / Local / Cache)
  - 全部通过 StateFlow 驱动
  - 每个页面一个 UiState data class
  - Navigation Compose 管理页面路由
```
