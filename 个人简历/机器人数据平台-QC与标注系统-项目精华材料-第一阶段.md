# 机器人数据平台 / QC / 标注系统项目精华材料（第一阶段）

- **项目状态：**第一阶段精华材料，非最终简历文案
- **用户确认身份：**单独完成
- **主要来源：**
  - `工程记录/data_collect/.project-log/requirements.md`
  - `工程记录/data_collect/.project-log/business-logic/main.md`
  - `工程记录/data_collect/.project-log/current-session.md`
  - `工程记录/data_collect/.project-log/architecture/software-architecture.md`
  - `工程记录/software/.project-log/requirements.md`
  - `工程记录/software/.project-log/business-logic/main.md`
  - `工程记录/force_touch_model/.project-log/current-session.md`

## 1. 项目定位

基于机器人数据采集系统，搭建数据质检、数据资产管理和标注工作平台，覆盖从原始机器人数据发现、索引、状态管理、QC、批次决策、训练数据导出，到 VLM 自动标注和人工复核的完整数据工作流。

项目上游数据来自 Linker Open TeleDex/ROS2 采集系统，包含 MCAP、遥测、关节/动作、视频、深度图、时间戳、相机信息以及可选触觉数据。

## 2. 用户负责范围

用户确认该数据平台由本人单独完成。结合记录，个人交付范围可组织为：

- 负责数据平台整体需求拆解、业务逻辑和系统边界设计。
- 负责 TeleDex 数据格式、MinIO 对象布局和数据质量方法调研。
- 负责 MinIO → PostgreSQL 数据扫描、索引、状态同步和任务队列。
- 负责 QC、批次驳回、数据集管理、导出和训练数据消费逻辑。
- 负责标注任务、人工复核、版本修订、权限、编辑锁和审计能力。
- 负责 VLM 自动标注队列、草稿生成、取消/重试和前端操作界面。
- 负责后端 API、数据库迁移、前端页面、Docker Compose 和 Ollama 联调。
- 负责回归测试、真实 Compose/PostgreSQL/Ollama 验收和问题修复。

## 3. 数据链路与系统架构

```text
ROS2 / MCAP 原始采集数据
  → raw / processed 数据转换
  → MinIO 对象发现与分层扫描
  → PostgreSQL 控制面与资产索引
  → QC / 批次决策 / 数据集管理
  → VLM 候选标注 + 人工复核
  → QUALIFIED 训练数据导出
```

关键架构边界：

- MinIO 只承担原始对象存储，不作为业务查询入口。
- PostgreSQL 作为业务事实源，保存 List、Batch、Episode、对象索引、扫描任务和 QC 状态。
- 前端只通过后端 API 访问数据，不直接耦合 MinIO 路径。
- 复杂扫描采用 coordinator/worker 分离，避免 API 进程承担长任务。
- 批次和任务级资产统计使用可重建的 PostgreSQL 派生投影和持久化重算队列。

## 4. 关键功能模块

### 4.1 TeleDex / MinIO 数据发现与扫描

- 对 bucket、List、Batch、Episode 和 raw/processed 目录结构进行实地分析。
- 采用任意深度 namespace discovery，并对确认的 List 按 prefix 分片扫描。
- 扫描 v3 支持 `smart`、`full`、`manual_prefix` 等模式。
- 通过 SHA-256 fingerprint 判断对象变化。
- 对 List、Batch、Episode、Object 建立业务实体和状态映射。
- raw 与 processed 状态独立维护，支持 missing/recovery。
- 已确认缺失的对象需要二次确认后才改变业务状态，避免短暂存储异常误删。

### 4.2 持久化任务队列与并发控制

- 设计 `scan_jobs`、`scan_shards`、`scan_prefix_states` 等控制面实体。
- 支持 job/shard claim、lease、heartbeat、retry、cancel 和 stale lease 回收。
- 使用数据库行锁/`FOR UPDATE SKIP LOCKED` 领取分片任务。
- worker 使用可终止子进程执行耗时扫描。
- 在 shard 完成、失败重试和业务发布前二次检查取消请求。
- coordinator 负责 discovery 展开、调度、聚合和资产重算。
- 通过 active key、job id 和幂等回退避免重复任务导致的 IntegrityError。

### 4.3 QC、批次驳回与数据集管理

- 将上游采集阶段的 L1 硬性门控与平台侧 L2-L4 质检分离。
- 支持人工质检、按比例抽检、全量派发、批次决策和审计留痕。
- 失败率采用人工失败数/抽检数，而不是批次总数，避免稀释质量问题。
- 训练数据消费使用最终 `QUALIFIED` 状态作为可用性主口径。
- 导出支持 JSONL + items，已完成标注的数据附带标注版本和 payload，未完成标注的合格 Episode 仍可导出。
- 数据集页面逐步从前端全量过滤迁移到服务端分页、筛选和短时缓存。

### 4.4 VLM 自动标注与人工复核

- 建立 annotation task、Sub Goal、draft、occurrence、revision 等数据模型和 migration。
- 实现标注资格判断、任务创建、草稿保存、完成校验、编辑锁和版本修订。
- 使用 VLM 队列生成候选标注，支持排队、取消、失败重试和超时处理。
- 实现前端 VLM 生成任务管理：列表、过滤、入队、取消和重试。
- 采用媒体、视觉和草稿工作台，支持人工复核、修订和保存。
- 设计固定模板、示范轨迹和时间对齐执行器，限制 VLM 自行增删、重排子任务。
- 记录中明确自动标注是候选生成，必须经过人工复核后才能进入正式训练数据。

### 4.5 数据资产统计与可重建投影

- 设计 batch-level 与 task-level asset rollup。
- 通过 `batch_asset_recompute_jobs` 和 worker 进行整批重算，而不是分散增量修补。
- 批次改挂任务时同时 dirty 旧任务和新任务。
- 周期性对账发现漏标记、漏重算和统计漂移。
- 将最终可用性、人工质检状态、待复核状态分开统计，避免混淆。
- 投影层失效只影响展示新鲜度，不改变业务事实源。

## 5. 关键技术问题与解决方向

| 难点 | 解决方向 |
| --- | --- |
| MinIO 对象层级深且无法直接作为业务查询层 | 设计 namespace discovery、List 分片和 PostgreSQL 控制面 |
| 长时间扫描阻塞 API 或无法取消 | coordinator/worker、持久化 shard 队列、lease/heartbeat/cancel |
| 扫描任务重复和幂等困难 | active key、job id 回退查询和状态机序列化 |
| 存储瞬态缺失可能误删业务数据 | fingerprint、二次确认、missing/recovery 状态和 suspect shard |
| QC、标注和最终可用性口径混杂 | 分离 final_dataset_status、manual_qc_status、annotation 状态 |
| VLM 生成子任务数量和边界漂移 | 固定任务模板、示范轨迹、时间对齐和人工复核 |
| 统计结果容易因为增量更新漂移 | PostgreSQL 持久化 dirty 队列、整批重算和周期对账 |
| 历史迁移和真实 Compose 环境不一致 | 新旧迁移分层验证、真实 PostgreSQL/MinIO/Ollama 验收 |

## 6. 工程验证与结果

记录中已有以下验证结果：

- 后端核心服务、API、数据库 migration、前端页面和 Compose 服务均有实施记录。
- `tests/test_annotations.py`、`tests/test_data_assets.py` 等针对性测试通过。
- 后端 `compileall`、前端 `vue-tsc` / `vite build`、`npm run build` 和 `git diff --check` 通过记录。
- 真实 Compose/PostgreSQL 验收中，VLM worker 可调用 Ollama，生成 `annotation_ai_runs`、成功 job 和候选 draft。
- annotation V1 已完成任务、草稿、occurrence、revision、人工工作台和权限等基础闭环。
- 扫描 v3 已完成 smart/full/manual_prefix、扫描状态机、分片进度、取消/重试和 coordinator/worker 集成。
- 已记录历史 SQLite migration drift、在线 PostgreSQL 迁移和部分浏览器/生产验收仍存在边界；不能把“测试通过”泛化为生产系统全部完成。

## 7. 可用于简历的价值标签

- 机器人数据平台
- MinIO / PostgreSQL 数据湖控制面
- 数据扫描、索引和资产治理
- 持久化任务队列与并发控制
- QC / 批次驳回 / 训练数据导出
- VLM 自动标注与人工复核
- FastAPI / Vue / PostgreSQL / Docker Compose
- Ollama 本地模型服务
- 数据状态机、幂等、重试和可重建统计
- 从需求调研到独立工程交付

## 8. 第一版简历表达方向（非最终文案）

### 稳健版方向

> 独立设计并实现机器人数据质检与标注平台，围绕 TeleDex/MinIO 数据结构搭建 PostgreSQL 数据控制面，完成数据扫描、资产索引、QC、批次决策、训练数据导出及 VLM 自动标注—人工复核闭环；通过持久化任务队列、分片扫描、取消/重试和可重建统计机制提升平台可靠性。

### 强表达版方向

> 独立完成机器人数据资产平台从 0 到 1 的设计与落地，打通 MinIO 数据发现、PostgreSQL 控制面、QC/批次驳回、训练数据导出和 VLM 标注工作流；自主实现支持 smart/full/manual_prefix、多进程 worker、lease/heartbeat、取消重试、missing/recovery 和任务级资产重算的扫描与治理系统，并完成 Compose/PostgreSQL/Ollama 联调验收。

强表达版中的“从 0 到 1”与“自主实现全部模块”需要用户确认实际代码范围后再进入最终简历。

## 9. 待用户补充的信息

1. 项目正式名称、实际起止时间和是否属于实习核心交付。
2. 用户是否真的独立完成后端、前端、数据库、部署和模型调用全部模块。
3. 平台实际接入的数据规模：List、Batch、Episode、对象数和用户数。
4. 扫描耗时、并发 worker 数、取消响应时间、重试成功率等指标。
5. 实际 API 数量、页面数量、数据库表/迁移数量。
6. 平台是否被其他成员真实使用，是否完成生产/准生产部署。
7. 哪些内部系统名、数据结构和模型名可以公开到简历。
