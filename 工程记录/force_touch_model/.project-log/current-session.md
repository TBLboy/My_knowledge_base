# Current Session

- 当前阶段：verification（GR00T 微调链路验证）+ annotation-infrastructure（标注基础设施搭建）
- 当前目标：搭建 LeRobot 数据集 VLM 自动标注 + 人工微调全链路
- 总体进度：
  - GR00T 微调：链路验证完成（EV-034~EV-037），用户已启动正式 30000 steps 训练
  - 标注基础设施：三个核心服务已全部搭建完成
  - VLM 模型：gemma3:27b 下载遇到 TLS 代理问题，需清理后重试

## 2026-07-30 标注基础设施搭建

### 已完成
1. **LeRobot visualizer GUI**（`/home/tbl/Project/force_touch_model/visualize_dataset/`）
   - 含前端（Next.js）+ 后端（FastAPI），支持 v3.1 标注原子
   - 后端持久化到 `<dataset_root>/meta/lerobot_annotations.json`

2. **本地数据集 HTTP 服务器**
   - `serve_local_dataset.py` → 多线程 + Range 请求支持
   - systemd 服务：`dataset-server.service`（端口 8080）

3. **标注后端**
   - `uvicorn app:app` → FastAPI
   - systemd 服务：`annotate-backend.service`（端口 7861）

4. **前端**
   - `npx next dev` → Next.js 15.3.6
   - 环境变量：`NEXT_PUBLIC_DATASET_URL=http://127.0.0.1:8080`
   - 已修改 `versionUtils.ts`：`DATASET_URL` → `NEXT_PUBLIC_DATASET_URL`
   - systemd 服务：`annotate-frontend.service`（端口 3000）

5. **前端验证**
   - `http://localhost:3000/local/my_dataset/episode_0` 可加载
   - 数据集服务器支持 Range 206 Partial Content
   - 视频流式加载正常

### 未完成/阻塞
- **Gemma3:27b 模型下载**：通过 SOCKS5 代理下载时 TLS 超时，下载不完整
  - 已清理所有残留文件：blobs、manifests 均已删除
  - 直连下载或正确配置代理后重试

### 标注持久化说明
- GUI 保存 → 后端写入 `meta/lerobot_annotations.json`
- 导出 → `POST /api/export` 重写 parquet 加入 `language_persistent` / `language_events`
- 数据集当前 7 列，无语言标注列

### 业务需求记录（会议）
- 统一数据集：矿泉水瓶开口 + 倾倒任务
- 测试方式：真机部署，成功率指标
- 语义标注策略：丰富特征描述、子任务标注、多版本描述
- 优化方式：问题导向

