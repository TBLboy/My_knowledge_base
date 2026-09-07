# Current Session

## Last Updated

- 2026-08-19 CST（presentation 演示版实现、验证与公网选型）

## Current Objective

- 在 `presentation` 分支制作一个对外公网演示版：用本机本地原始数据集替代 MinIO，保留核心 QC 闭环，AI 助手不纳入演示；公网入口采用免费且网址不变的 Tailscale Funnel。

## Current Status

### 已确认

- 分支：`presentation`
- 数据源：`/mnt/data/gr00t-finetune/datasets/double_linkerhand_qingdao_{1,2,3}_...`
- 数据量：90 / 97 / 100 共 287 条原始 episode，约 54GB；数据留在本机，不提交 git
- 格式：不使用 leRobot 转换格式，直接使用 `processed/episode_XXXX/...`
- 功能范围：登录/角色、工作台、数据总库与数据资产、任务类型与派发、人工 QC、QC 历史/导出、数据集导出、BUG、重检/审批真实可用
- 移除项：MinIO 扫描入口隐藏或禁用；AI 助手不纳入演示
- 公网选型：Tailscale Funnel（免费、网址不变），不购买域名

### 实现完成

- 后端 demo 配置 + `LocalObjectService` 本地对象适配 + 签名媒体 `/api/demo/media`
- `demo_local_import` 本地原始数据导入；`get_minio_service()` demo 模式走本地
- 前端：扫描/AI 设置隐藏、演示文案、AI 助手面板隐藏
- 新增 `tests/test_demo_local_import.py`、`docs/presentation-demo.md`、`scripts/demo_reset.sh`
- 新增公网部署支持：
  - `frontend/vite.config.ts` 增加 `preview` 端口 4173 与 `/api` 代理
  - `scripts/demo_serve.sh`：单端口本地服务（后端 8000 + 前端 4173）
  - `scripts/demo_funnel.sh`：Tailscale up / on / status / off
  - 已确认 `~/.local/bin/tailscale` + `tailscaled`（1.102.2 userspace 模式可用）
  - `scripts/demo_reset.sh` 增加管理员账号创建（要求 `DEMO_ADMIN_PASS`）

### 验证证据

- `EV-DEMO-REAL-IMPORT-001`：真实第 1 List 90 集 / 126516 对象导入成功
- `EV-DEMO-TEST-001`：演示导入单测 6/6 通过
- `EV-BACKEND-TESTS-001`：既有测试 11 + 6 通过，compileall 通过
- `EV-FRONTEND-TSC-001`：`vue-tsc --noEmit` 与 `npm run build` 通过
- 单端口服务端到端验证：4173 页面 + `/api` 代理 + 登录 + session 均可用

## Problems And Resolutions

- 本地文件枚举 `Path` 默认排序与解析器字符串字典序不一致 → 改用对象键字符串排序
- 后端日志默认 `/app/logs` 在本机不可写 → `demo_serve.sh` 设 `LOG_DIR` 到 `/tmp/robot-qc-demo-logs`

## Next Steps

- 用户执行一次性操作：
  1. `DEMO_ADMIN_PASS=<强密码> scripts/demo_reset.sh`（含 287 集完整导入）
  2. `scripts/demo_serve.sh`
  3. `scripts/demo_funnel.sh up`（浏览器登录）+ `on`
- 之后把公网 URL 交给评估者，展示结束后 `scripts/demo_funnel.sh off`
