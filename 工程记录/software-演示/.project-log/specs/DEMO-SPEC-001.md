# DEMO-SPEC-001 Presentation 演示版本地数据源改造

## 1. Objective and Non-goals

Objective:

- 在 `presentation` 分支上让 Robot QC 演示版不依赖内网 MinIO，从本机本地原始数据集导入数据。
- manual QC 的 MP4、telemetry 曲线、L3 评分、异常时间线仍然真实可用。
- 保留核心业务闭环，隐藏或禁用 MinIO 扫描入口与 AI 助手。
- 不把 54GB 数据和内网凭据提交进 git。

Non-goals:

- 不实现公网域名/HTTPS 的实际开通（部署项，另行确认）。
- 不做 AI/Ollama 演示。
- 不改 `main` 生产分支的业务语义。
- 不做 raw 到 processed 的转换工具链。

## 2. Business Atoms and Acceptance

Basis: `DEMO-001` 到 `DEMO-005`。

Acceptance summary:

- 本地导入可在无 MinIO 环境下把本地 episode 变成可用的 List/Batch/Episode。
- manual QC 能通过后端读取本地 MP4、metadata 和 telemetry.npz。
- 前端不暴露 MinIO bucket/key 规则；Media URL 由后端生成。
- 仓库扫描不到内网 MinIO 地址、access key、secret key 或 54GB 数据。
- 演示库可重置。

## 3. Existing Behavior and Evidence

- `MinioService` 只暴露 `list_objects`、`get_object`、`presigned_get_object`。
- `list_snapshot.py` 通过该接口完成对象枚举与 manifest 解析。
- `business_resolver.py` 把 `ListSnapshot` 落库并触发资产重算。
- `payloads.py`/`qc.py` 用 presigned URL 提供 manual QC 媒体，用 `get_object` 读 telemetry/metadata。
- 原始数据 `/mnt/data/.../double_linkerhand_qingdao_{1,2,3}` 与 processed 结构一致，共 287 条。

## 4. Target Behavior

Demo 模式由环境变量启用：

```bash
APP_ENV=demo
DEMO_MODE=true
DEMO_DATA_ROOT=/mnt/data/gr00t-finetune/datasets
DEMO_BUCKET=demo
DATABASE_URL=sqlite:///.../robot_qc_demo.db
```

导入命令：

```bash
python -m app.services.demo_local_import --data-root /mnt/data/.../datasets --bucket demo
```

导入后：

- 三个 `double_linkerhand_qingdao_*` 目录分别映射为一个 List。
- object_key 使用数据目录相对路径，例如 `double_linkerhand_qingdao_1/processed/episode_000000/cameras/cam_top.mp4`。
- manual QC 的 `previewUrl` 指向后端签名本地媒体路由。
- telemetry/metadata 由 `LocalObjectService.get_object` 读取。
- 数据库扫描/扫描 worker/扫描 UI 不参与 demo，或保持禁用。

## 5. Files / Modules Affected

- `backend/app/core/config.py`：新增 demo 模式、`DEMO_DATA_ROOT`、`DEMO_BUCKET`、媒体签名 secret。
- `backend/app/services/local_object_service.py`：新增本地对象适配器。
- `backend/app/services/minio_client.py`：增加按模式返回存储服务的工厂。
- `backend/app/services/demo_local_import.py`：新增本地导入 CLI。
- `backend/app/api/routes/demo_media.py`：新增签名本地媒体路由，注册到 `backend/app/main.py`。
- `backend/app/api/routes/qc.py`：修复未定义的 `minio_client` 引用；确保 demo 模式走本地适配器。
- `backend/app/services/payloads.py`：确认媒体 URL 生成走存储服务返回的 URL。
- `backend/app/services/scan_worker.py`/`scan_coordinator.py`：demo 容器不启动，不做生产扫描。
- `frontend/src/pages/database-view.vue`：隐藏/禁用扫描 MinIO 表单。
- `frontend/src/pages/settings.vue`：隐藏/禁用 AI 与扫描 worker 配置。
- `frontend/src/pages/login.vue`、`dashboard.vue`、`components/AppLayout.vue`：替换 MinIO 展示文案。
- `deploy/docker-compose.yml` 或新增 demo compose：不启动 scan-coordinator/worker。
- `docs/presentation-demo.md`：部署说明、演示账号、重置与 CORS/HTTPS 要求。
- `scripts/demo_reset.sh`：重置演示库。
- `tests/`：新增本地对象适配与导入测试。

## 6. Interface and Schema Changes

- 不新增数据库表；沿用 `ListRecord/Batch/Episode/EpisodeInventory/EpisodeObject/ScanJob` 与现有 API contract。
- 新增存储服务抽象：
  - `list_objects(bucket, prefix, recursive)`
  - `get_object(bucket, object_key)`
  - `presigned_get_object(bucket, object_key, expires)`
- demo 模式 `presigned_get_object` 返回：
  `{API_BASE}/api/demo/media?bucket=...&key=...&expires=...&sig=...`
- DemoMediaRoute 只允许 `bucket == DEMO_BUCKET` 且解析后的路径在 `DEMO_DATA_ROOT` 之下。

## 7. State, Concurrency, Lifecycle

- 导入单机顺序执行；每个 List 的 fingerprint 基于 `list_snapshot`，重复导入幂等。
- 导入与重置互斥，通过锁文件或脚本内单实例保护。
- 演示库与正式库分离；`main` 分支不读取 demo 配置。
- 重置流程：备份当前演示库 -> 删除并重建 -> 重新导入。

## 8. Validation, Error Handling, Idempotency

- `DEMO_DATA_ROOT` 不存在或为空：导入失败并给出可读错误。
- 单 episode 缺必要对象：不进入 QC 展示，其余继续导入。
- 媒体文件缺失：DemoMediaRoute 返回 404，manual QC 显示该 object 不可用。
- 非法 bucket/key 或路径穿越：拒绝并记录日志。
- 导入失败后演示库不对外暴露半成品：失败时回滚或标记 `import_failed`。

## 9. Security / Privacy

- demo 模式不读取内网 MinIO 凭据。
- 媒体 URL 使用短时签名令牌，避免公开路径猜测。
- 仓库不提交 54GB 数据、`.env`、内网地址。
- 前端不持有/拼接对象存储路径。
- 公网部署文档要求 HTTPS、CORS 白名单、密钥替换和独立演示账号。

## 10. Logging / Metrics / Diagnostics

- 导入记录开始/结束、导入条数、失败 episode 与耗时。
- demo 模式健康检查仍为 `/api/health`。
- 日志标示 `storage=local`，便于确认未连 MinIO。

## 11. Compatibility, Migration, Rollback

- 只在 `presentation` 分支生效；不回写 `main`。
- 新配置默认关闭 demo，不影响正式行为。
- 回滚：切换回 `main` 分支或关闭 demo 环境变量即可恢复正式路径。

## 12. Test Matrix

- 后端 `compileall`：全量静默通过。
- 本地对象适配：fake MinIO 对象项形状一致。
- 导入测试：在临时本地数据集上执行，验证 List/Batch/Episode 生成且幂等。
- manual QC 媒体/曲线：无 MinIO 时返回本地 URL 与 telemetry。
- 前端 `vue-tsc --noEmit` 与 `vite build` 通过。
- 仓库扫描：确认无 `MINIO_ACCESS_KEY`、内网 endpoint、大文件。

## 13. Open Questions and Authority

- 公网 URL/域名/HTTPS（C，部署后确认，不阻塞）。
- 是否允许公网访客写演示库（默认允许并提供重置，B）。
