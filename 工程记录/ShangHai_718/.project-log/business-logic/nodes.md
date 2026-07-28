# Business Logic Nodes

## Architecture Layer Mapping

新架构下，每个业务操作经过以下层级：

```
Screen → ViewModel → UseCase → Repository(interface) → RepositoryImpl → DataSource → Api/Dao
|<-- presentation -->|<-------- domain -------->|<----------- data ------------>|
```

## Application Screen Nodes

---

```yaml
id: LOGIN
name: 登录界面
status: pending (待按新架构重新实现)
state:
  - 登录界面已渲染
  - 账号/密码输入框可用
  - 支持系统键盘输入
inputs:
  - 无（启动入口）
outputs:
  - loginAccount: String
  - loginPassword: String
  - LoginClicked action
data_format:
  - LoginUiState (每个页面独立 UiState)
related_interfaces:
  - 无（纯本地）
notes:
  - 新架构: LoginScreen → LoginViewModel → (暂无业务调用)
```

---

```yaml
id: SELF_CHECK
name: 系统自检界面
status: pending (待按新架构重新实现)
state:
  - 5 个检测项逐项自检: 左臂/右臂/左手/右手/急停
  - 全部通过后自动跳转 MAIN
inputs:
  - selfCheckItems: List<SelfCheckItem>
outputs:
  - selfCheckProgress: Float (0.0-1.0)
  - SelfCheckContinueClicked → navigate to MAIN
data_format:
  - SelfCheckUiState
related_interfaces:
  - POST /api/robot/self-check
notes:
  - 新架构: SelfCheckScreen → SelfCheckViewModel → CheckRobotUseCase → RobotRepository → RobotRemoteDataSource → RobotApi
```

---

```yaml
id: A
name: APP就绪 (主控面板)
status: pending (待按新架构重新实现)
state:
  - 主控面板 Compose UI 已渲染
  - 初始化数据已加载（3 个 GET 接口）
  - 根据 workMode 渲染 Dev/User 不同布局
inputs:
  - 登录 + 自检完成后自动触发
outputs:
  - 完整控制界面
data_format:
  - MainDashboardUiState
related_interfaces:
  - GET /api/task/current
  - GET /api/logs
notes:
  - 新架构: MainDashboardScreen → MainViewModel → GetTaskStatusUseCase + GetLogsUseCase + ...
  - Hilt ViewModel 注入，Repository 由 Hilt 提供
```

---

```yaml
id: B
name: 用户操作已触发
status: pending (待按新架构重新实现)
state:
  - 用户点击了 UI 按钮
  - UiEvent 已分发到 ViewModel
  - ViewModel 调用对应 UseCase
inputs:
  - UiEvent (各功能模块独立定义)
outputs:
  - UseCase 调用已发起
data_format:
  - 每个 feature 独立定义 UiEvent sealed interface
notes:
  - 新架构: 不再是单一大 UiAction，而是每个 feature 独立定义
  - RecipeSelected → SelectRecipeUseCase
  - StartCookingClicked → StartTaskUseCase
  - TaskCommandClicked → ControlTaskUseCase
  - RobotActionClicked → RobotActionUseCase
```

---

```yaml
id: C
name: 请求已发送
status: pending (待按新架构重新实现)
state:
  - RepositoryImpl 调用 RemoteDataSource
  - RemoteDataSource 调用 Retrofit Api
  - HTTP 请求发送到中层NODE
inputs:
  - Api 方法参数 (DTO)
outputs:
  - NetworkResult<T>
data_format:
  - NetworkResult.Success(data) | NetworkResult.Error(code, message) | NetworkResult.Loading
related_interfaces:
  - Retrofit Api 接口 (RobotApi, TaskApi, LogApi)
notes:
  - 新架构使用 Retrofit + OkHttp，不再有 FakeRepository
  - RepositoryImpl 协调 remote/local 数据来源
  - Mapper 负责 DTO → Domain Model 转换
```

---

```yaml
id: D
name: 响应已接收
status: pending (待按新架构重新实现)
state:
  - NetworkResult 已返回
  - RepositoryImpl 通过 Mapper 转换为 Domain Model
  - UseCase 返回 Domain Model 给 ViewModel
inputs:
  - NetworkResult<T> (data 层)
outputs:
  - Domain Model (domain 层)
data_format:
  - DTO → Mapper → Domain Model → UiState
notes:
  - DTO/Entity 绝不暴露到 presentation 层
  - 转换链路: DTO → Domain Model → UiState
```

---

```yaml
id: E
name: 结果已展示 + 选择性刷新
status: pending (待按新架构重新实现)
state:
  - ViewModel 更新 StateFlow<UiState>
  - Compose UI recompose
  - 根据操作类型执行选择性刷新
  - errorMessage 通过 ErrorBanner 展示
inputs:
  - Domain Model 或 error
outputs:
  - Compose UI recomposition
notes:
  - 新架构: 每个页面独立 UiState + StateFlow
  - 轮询: ViewModel 中用 while(true) + delay 实现，通过 StateFlow 暴露
  - navigation 由 Navigation Compose 管理
```

---

## Module Map (新架构 feature 拆分)

| Feature | presentation | domain | data |
|---------|-------------|--------|------|
| login | LoginScreen / LoginViewModel / LoginUiState | (暂无复杂业务) | — |
| selfcheck | SelfCheckScreen / SelfCheckViewModel / SelfCheckUiState | CheckRobotUseCase | RobotRepositoryImpl → RobotRemoteDataSource → RobotApi |
| recipe | RecipeListScreen / RecipeListViewModel / RecipeListUiState | GetRecipeListUseCase | RecipeRepositoryImpl → RecipeLocalDataSource → RecipeDao |
| task | TaskScreen (主面板) | StartTaskUseCase / ControlTaskUseCase / GetTaskStatusUseCase | TaskRepositoryImpl → TaskRemoteDataSource → TaskApi |
| robot | RobotControlScreen (Dev) | RobotActionUseCase / GetRobotStatusUseCase | RobotRepositoryImpl → RobotRemoteDataSource → RobotApi |
| logs | LogPanel (主面板组件) | GetLogsUseCase | LogRepositoryImpl → LogRemoteDataSource → LogApi |
