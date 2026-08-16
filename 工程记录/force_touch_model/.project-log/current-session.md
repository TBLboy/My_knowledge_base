# Current Session

## 2026-08-03 独立 annotation_workbench 交付完成

### 结果
- `annotation_workbench/` 现自带桌面端、可视化前端、FastAPI 标注后端、Range 本地数据服务和最小 LeRobot v3/VLM 适配层；运行时不读取 `lerobot_v1.0/`、外部 `visualize_dataset/` 或 `serve_local_dataset.py`。
- 生产前端通过同源 `/api/workbench-config` 读取本次桌面端选择的数据集和后端地址，因此用户切换数据集不需要重建 Next.js。
- 为避免 Gemma 图像中四舍五入后的结束时间略超 episode 末帧，VLM 边界先吸附到真实帧时间戳，再按固定子任务文本、顺序和完整覆盖规则校验。

### 验证证据
1. `npm run type-check`、`npm run build` 和 Python 测试通过（`10 passed`）。
2. 隔离数据集：GUI 页面、运行时配置、后端保存/读回和 JSON 持久化均通过；停止后自建三服务已回收。
3. 外部 Ollama `gemma3:27b`：对隔离副本 episode 1 自动标注成功，写入 4 个 atoms，GUI 后端可读回。
4. 仅复制 `annotation_workbench/` 的隔离目录：`./install.sh`、前端生产构建和 `QT_QPA_PLATFORM=offscreen python -m annotation_workbench` 均通过。

### 使用入口
```bash
cd /home/tbl/Project/force_touch_model/annotation_workbench
./run.sh
```

### 边界与下一步
- Ollama/Gemma 仍是外部前置条件，不自动下载或打包。
- 已确认当前 X11 环境缺少 `libxcb-cursor0` 且用户没有免密 sudo；该库已放入 `annotation_workbench/.system-libs`，`./run.sh` 和模块入口会自动加载。两种入口均在 `DISPLAY=:1` 实测通过，不再出现 xcb 核心转储。
- 已修复本地 GUI 的 `Failed to fetch dataset info: 401`：服务端数据访问从构建期 `NEXT_PUBLIC_DATASET_URL` 改为启动时 `DATASET_URL`；隔离 v3 数据集页面验证通过。已启动的旧桌面实例需关闭并重新运行后才会加载新构建。
- 进一步发现浏览器客户端仍可能绕过该修复访问 Hugging Face；已新增同源 `/api/local-dataset/[...path]` 代理，客户端的 info、stats、parquet 和视频请求统一走本地数据服务。Chrome headless 实际加载页面并出现 Episodes、Annotations、Frames，401 问题消失。
- 本次证明技术闭环，不等价于 VLM 语义/时间边界质量通过；下一步应从真实任务中抽样，在 GUI 人工复核 VLM 结果。

## 2026-08-03 独立 annotation_workbench 改造：架构与实施准备

### 当前目标
- 交付只保留 `annotation_workbench/` 也能独立安装、启动和运行的 Linux/Ubuntu 本地 LeRobot v3.0 标注工具包（`REQ-002` revision 1）。

### 本轮已完成
1. 恢复 Project Log，并确认旧 Loop 指向历史 `TASK-021`；当前独立包工作链已单独建立。
2. 核对现有耦合：`desktop_app.py` 依赖项目外 `visualize_dataset/`、`serve_local_dataset.py`、`lerobot_v1.0/src`；`guided_alignment.py` 仅实际使用外部管线中的 episode 读取、视频帧、联系表和 Ollama 客户端能力。
3. 写入 `ARCH-001`：包内桌面壳、服务管理器、数据服务、保留式 Next.js/后端、最小 v3/VLM 适配层、安装器的职责、接口、数据流、故障边界与隔离约束。
4. 写入 `DEC-007`：迁移既有前端/后端、只提取最小 LeRobot v3 适配层；不复制完整 LeRobot，不重写前端。
5. 建立 `TASK-031` 至 `TASK-035`，并写入实施说明 `.project-log/specs/annotation-workbench-standalone.md`。
6. 修复 Project Log schema 漂移：新架构状态、决策状态、任务 owner 和近期 verification result 已对齐当前 schema。

### 当前进行中
- `TASK-032`：迁移本地数据服务、Next.js GUI 与 FastAPI 标注后端到独立包内部。

### 新增实施结果
1. `TASK-031` 已完成：新增 `pyproject.toml`、`install.sh`、`run.sh`、`__main__.py` 和 `.gitignore`；Python 包要求为 3.11+。
2. 已实际使用系统 `Python 3.11.15` 执行 `annotation_workbench/install.sh`：包内 `.venv` 创建、Python 依赖安装、editable 包安装、锁定前端 `npm install` 和 `npm run build` 全部成功。
3. 当前 Node.js 为 `22.23.1`，满足 Node.js 20 LTS 最低约束。Ollama 未启动，安装脚本给出非阻塞明确提示，未自动下载模型。
4. 已将 `visualize_dataset` 前端和 FastAPI 后端源码复制至 `annotation_workbench/visualize_dataset/`，明确排除了 `.git`、`node_modules`、`.next` 和 Python 缓存；已新增包内 `local_dataset_server.py`。

### 已确认约束
- 仅 Linux/Ubuntu、Python 3.11+、Node.js 20 LTS、LeRobot v3.0。
- `.venv` 位于 `annotation_workbench/.venv`；不再绑定现有 Conda/Miniforge 环境。
- 前端保留并在包内迁移，安装时 `npm install` + `npm run build`，运行时 `next start`。
- Ollama 与模型权重是外部前置条件；默认 `OLLAMA_API_BASE=http://127.0.0.1:11434/v1`、`OLLAMA_MODEL=gemma3:27b`，可覆盖；不得自动下载模型。
- 标注直接写入所选数据集的 `meta/lerobot_annotations.json`；外部旧目录只保留备份，独立包运行时不得读取。

### 精确下一步
1. 完成 `TASK-032`：接入迁入的后端与生产 `next start`，移除桌面端对外部 GUI/数据服务路径的引用。
2. 推进 `TASK-033`：实现包内 v3 reader、视频抽帧、联系表和 Ollama 客户端，移除 `guided_alignment.py` 对 `lerobot_v1.0` 的依赖。

---

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


## 2026-07-30 工作流漂移修复 + 项目归档

### 已完成
1. **工作流漂移对齐** — 修复 `.project-log/tasks/task-list.yaml` 和 `.project-log/verification/evidence.yaml` 中所有 `/home/tbl/Project/lerobot_v1.0` → `/home/tbl/Project/force_touch_model/lerobot_v1.0` 路径引用。
2. **项目归档** — `.project-log/` 62 个文件已归档至 `My_knowledge_base/工程记录/force_touch_model/.project-log/`，并推送至 GitHub 远端。

## 2026-07-30 工作流漂移修复 + 项目归档

### 已完成
1. **工作流漂移对齐** — 修复 `task-list.yaml` 和 `evidence.yaml` 中所有 `/home/tbl/Project/lerobot_v1.0` → `/home/tbl/Project/force_touch_model/lerobot_v1.0` 路径引用。
2. **项目归档** — `.project-log/` 62 个文件已归档至 `My_knowledge_base/工程记录/force_touch_model/`，并推送至 GitHub。

## 2026-07-31 Gemma + LeRobot 自动标注端到端验证

### 验证范围
- 模型：Ollama `gemma3:27b`，`Q4_K_M`，约 17.4 GB。
- 数据：LeRobot v3.0 数据集，148 episodes / 47250 frames / 3 路相机。
- 测试方式：使用 hardlink 视频、独立 Parquet 的隔离副本，仅处理 episode 0；未修改正式数据集。

### 结果
1. `lerobot-annotate` 通过 Ollama OpenAI 兼容接口 `http://127.0.0.1:11434/v1` 成功完成 `plan`、`interjections`、`vqa` 三个阶段。
2. CLI validator：`checked=1 errors=0 warnings=0`；成功写入 `language_persistent` 和 `language_events`。
3. GUI 后端成功加载标注，保存 41 个 atoms，并持久化到 `meta/lerobot_annotations.json`。
4. GUI 导出成功生成独立数据集；导出统计为 14 个 persistent rows、27 个 event rows。
5. 导出数据可由 `LeRobotDatasetMetadata` 和 `LeRobotDataset` 读取，148 episodes / 47250 frames 保持一致。

### 依赖与偏离
- 首次真实 CLI 执行暴露 `lerobot` 环境缺少 `openai`；已安装 `openai==1.109.1`，这是 `lerobot[annotations]` 声明的运行依赖。
- `--only_episodes` 需要传入 `[0]`，单个整数会触发 draccus tuple 解析错误。
- 用户补充确认：本次使用的是旧数据集，真实任务描述为“用右手抓起视野中右侧的圆形金属盆子，将其中的物体倾倒在视野左侧的黑色带把手的铁锅当中”；矿泉水瓶倾倒花生任务尚未采集。
- 执行闭环通过，但 Gemma 生成的语义与当前旧数据任务仍存在明显偏差（将任务描述为拿起深色物体、放到图案表面），因此只能判定为 `pipeline-pass / semantic-quality-fail-needs-review`，不能直接用于全量训练。

### 清理边界
- 验证结束后删除隔离测试副本、导出副本和临时日志；保留模型、正式数据集和本记录。

## 2026-07-31 五 episode 标注质量校准

### 实验设置
- 样本：episode 0、20、50、100、140。
- 视角：`observation.images.cam_top`。
- 固定任务：使用右手抓取视野右侧圆形金属盆，移动至视野左侧黑色带把手铁锅上方，倾斜金属盆将内容物倒入铁锅。
- 配置：`derive_task_from_video=off`、1 FPS、关闭 VQA 和 interjections，仅验证 plan/subtask/memory。

### 结果
- 5/5 episode 完成，validator `errors=0 warnings=0`。
- 5/5 episode 都识别出金属盆、左侧黑色铁锅和倾倒动作；未再出现此前的 `dark object` / `patterned surface` 语义漂移。
- 任务改写均保留右手、盆、铁锅、左右位置和倾倒目标，满足当前任务语义约束。
- 子任务顺序整体正确，但粒度不稳定：部分 episode 将“抬高盆子”单独作为子任务，其他 episode 将其合并到移动；episode 100 还出现释放盆和收回机械臂等尾部动作。

### 结论
- 固定完整任务描述 + 顶视角 + 关闭视频任务推断，已解决主要对象/任务语义漂移问题。
- 当前可进入 20 episode 小批量验证，但应先统一子任务粒度规则：核心标注固定为“抓取 → 移动到铁锅上方 → 倾倒”；抬高、释放、收回等动作只在确实构成独立业务状态时保留。
- 不能只根据格式 validator 判定质量；仍需人工抽检时间边界和倾倒是否真实发生。

### 清理
- 五 episode 校准副本和临时日志已在验证后清理；正式数据集未写入语言列。

## 2026-07-31 二十 episode 标注基线验证

### 实验设置
- 样本：episode `1,5,10,15,20,25,30,35,40,45,55,60,65,70,75,80,90,110,120,130`。
- 使用实体复制的 `meta/` 和 `data/`，视频只读 hardlink；正式数据集未参与写入。
- 视角：`observation.images.cam_top`；固定完整任务描述；`derive_task_from_video=off`。
- 采样：1 FPS；关闭 VQA 和 interjections；只运行 plan/subtask/memory。

### 结果
- 20/20 episode 完成；validator `checked=20 errors=0 warnings=0`。
- 盆子识别：20/20；铁锅识别：20/20；倾倒/contents 语义：20/20。
- 每个 episode 都生成了抓取、移动/定位、倾倒的核心动作链，核心任务语义通过率为 20/20（100%）。
- 子任务数量：5 个为 3 段，15 个为 4 段。
- 12/20 episode 额外生成了抬高、释放、收回、空盆停留、重复倾倒等尾部或粒度不一致动作；额外子任务比例为 60%。

### 结论
- 当前固定任务描述 + `cam_top` 已经解决主要对象和任务语义漂移，Gemma 可用于生成候选标注。
- 子任务粒度仍不稳定，尤其是倾倒后的动作；不能直接把当前结果作为最终训练标签，也不建议现在全量导出。
- 下一步应增加任务专属的“核心三阶段优先、尾部动作默认不标注”的约束，重新验证 20 个 episode；重点比较额外子任务比例是否从 60% 降至不超过 20%。

### 清理
- 20 episode 测试副本、分析脚本输出和临时日志已清理；正式数据集仍为原始 `pouring` 任务且无语言标注列。

## 2026-07-31 任务专属约束实现与 A/B 验证

### 实现
- 在 `lerobot_v1.0/src/lerobot/annotations/steerable_pipeline/config.py` 增加可选的 `subtask_labeling_guidance`，默认空值，不改变其他任务行为。
- 在子任务提示词中注入该指导字段；当前旧任务指导为“核心三阶段：抓取 → 移动到铁锅上方 → 倾倒”，并要求默认合并抬高、旋转、释放、收回和空盆停留等尾部动作。
- 新增 `lerobot.annotations.steerable_pipeline.quality`，只输出可审计质量指标，不重写 VLM 原始标签；新增针对性单测。

### 验证
- 标注模块回归：`12 passed`。
- 约束版 20 episode CLI：20/20 完成，validator `errors=0`；因实验关闭 `plan`，产生 20 个预期 warning。
- 但该批样本并非同一个任务：生成结果中出现 kettle、mug、container 等多个倾倒任务；正式数据的 `meta/tasks.parquet` 只有一个笼统 `task_index=0`，无法按任务过滤。
- 因此本次 A/B 不能作为“金属盆→铁锅”任务质量结论；指标仅用于暴露数据分层问题，未写入正式数据。

### 结论与下一步
- 根因优先级高于提示词：必须先按真实任务建立 episode 级任务清单/标签，再在同任务样本上重跑约束验证。
- 当前自动标注仍只能作为候选生成，不进入全量训练；需要先得到纯同任务样本，并人工抽检时间边界。
- 临时测试副本和日志已清理；正式数据、模型和 GUI 服务未修改。

### 用户人工复核后的纠正
- 用户已检查本批可疑 episode，确认所有数据属于同一个操作场景，视频中没有 kettle、mug、container 等其他任务对象。
- 因此此前“数据集混入多个任务”的判断撤销；`kettle/mug/container` 只是 Gemma 的视觉对象误识别，不能作为数据混合证据。
- 当前主要问题重新归类为 `technical-selection` / `implementation`：Gemma3:27b 在当前顶视角和采样配置下，对容器类别、目标物体和子任务边界识别不稳定。
- 后续不能仅依赖关键词统计判断质量；应先针对同一真实任务做小样本 prompt/采样对比，并人工复核对象和时间边界。

## 2026-07-31 三 episode GUI 人工复核测试副本

### 已完成
- 从正式数据抽取 episode `0、20、45`，建立隔离副本 `/mnt/data/gr00t-finetune/gui_annotation_test_3ep`，测试 episode 重编号为 `0、1、2`。
- 使用 Gemma3:27b 对三个 episode 完成自动标注；validator 为 `checked=3 errors=0 warnings=3`，warning 来自本次关闭 plan 输出的预期配置。
- 标注写入测试副本的 `language_persistent` / `language_events`，正式数据集未修改。
- 标注后端成功读取三个 episode；临时修改一条 atom 后成功保存并读回，随后恢复为自动标注内容。
- 独立数据服务运行在 `8081`，独立 GUI 前端运行在 `3001`，三个 episode 页面均返回 HTTP 200。
- 为支持本地路径写回，GUI 的 `EpisodeBootstrap` 已支持 `NEXT_PUBLIC_LOCAL_DATASET_PATH`，独立前端使用该变量绑定测试副本。

### 当前人工检查入口
- `http://127.0.0.1:3001/local/gui_annotation_test_3ep/episode_0`
- `http://127.0.0.1:3001/local/gui_annotation_test_3ep/episode_1`
- `http://127.0.0.1:3001/local/gui_annotation_test_3ep/episode_2`

### 注意
- 这批结果的 GUI 读写链路已验证，但 Gemma 对象命名跨 episode 不稳定：`object/cylinder`、`kettle/mug`、`container/mug`。因此当前标注是人工复核候选，不能直接作为最终训练标签。
- 测试副本需要保留到用户完成浏览和微调；确认后再决定是否导出或清理。

### GUI 快速添加修复
- 用户点击 `task augmentation` 的 `+ Add at frame` 时，空输入会触发 `label.trim()` 的运行时异常。
- 根因是快速添加状态初始为 `{}`，某些字段在未输入时为 `undefined`，而构建器直接调用 `.trim()`。
- 在 `visualize_dataset/src/components/annotations-panel.tsx` 增加统一的空值安全文本清理；空输入现在直接忽略，不再崩溃。
- 验证：`npm run lint` 通过（仅保留 3 个既有 Hook 警告）；`npm run type-check` 通过；episode 页面返回 HTTP 200。

### 本轮结论
- VLM 自动标注结果能够被 LeRobot 可视化界面识别。
- 用户已验证可以在 GUI 中对 `task augmentation` 和 `subtask` 等标注进行人工微调。
- 标注修改可以通过 `Save episode` 持久化到测试副本；正式数据集仍未修改。
- 当前 GUI 闭环已经具备“自动生成候选标注 → 人工复核/修订 → 保存”的可用基础。

### 下一步建议
1. 先人工完成一个 episode 的高质量示范标注，固定任务描述、子任务文本和时间边界。
2. 基于这条示范标注设计 demonstration-guided temporal alignment：后续 VLM 只预测固定子任务的时间范围，不再自由新增或改写子任务。
3. 在 3 个测试 episode 上验证对齐结果，比较人工修订量、对象误识别率和时间边界准确性。
4. 通过小批量人工验收后，再考虑扩展到更多 episode；暂不对正式数据集执行全量导出。

## 2026-07-31 Web 标注应用业务澄清草案

### 用户提出的目标流程
- 本机部署一个可被局域网访问的 Web 应用。
- 用户选择本地 LeRobot v3.0 数据集后，在 GUI 中完成人工示范标注。
- 人工阶段标注 1-5 条精细轨迹；同一轨迹允许添加 2-4 条不同细粒度的 task augmentation 描述。
- 人工建立固定 subtask 集合；VLM 后续只复用固定标签并预测帧范围，不自由新增或改写 subtask。
- 保存人工标注后启动 VLM；完成后重新打开 GUI 抽样检查和微调。
- 通过中间编排组件统一选择数据集、打开 GUI、检查示范状态和启动 VLM，避免手工修改环境变量。

### 当前建议
- 第一版每个 subtask 使用一个标准描述；语言多样性放在 task augmentation，不放在 subtask。
- 这样可以固定 subtask 的数量、顺序和语义，避免 VLM 改写标签或造成训练样本重复加权。
- 可以增加辅助参考标注，但应与模型最终输出分离，例如：对象类别/位置、目标容器、关键帧提示、遮挡/视角质量、人工置信度和边界说明。VLM 可读取这些信息，但不负责重新生成它们。
- VLM 自动标注建议默认输出到隔离的新目录或版本，不直接覆盖用户选择的原始数据集。
- 局域网访问的登录、只读/编辑权限和并发编辑规则仍未确定。

### 记录位置
- 详细事实、推断、缺口和最高优先级问题：`.project-log/business-logic/clarification-2026-07-31-web-annotation.yaml`

### 已确认决策
- 用户确认：第一版每个 `subtask` 只保留一个固定标准描述，不做同一子任务的多措辞版本。
- 因此 VLM 输出契约固定为：复用既有 subtask 文本，只预测对应时间范围。
- 下一待确认问题：同一轨迹的多条 `task augmentation` 是否全部用于 baseline 训练，还是只指定一条主描述，其余作为参考/增强候选。
- 用户确认：每条轨迹只指定一条主 `task augmentation` 进入 baseline 训练，其余描述保留为 VLM 参考和后续增强实验候选。
- 用户确认：辅助参考标注不是第一版必需项，可以标注，也可以不标注；第一版只要求完成 `task augmentation` 和固定 `subtask` 标注，辅助信息后续再讨论。
- 用户确认：人工阶段允许直接标注 1–5 条示范轨迹，不要求先完成单条示范再扩展。
- 用户确认：VLM 默认跳过并保护 1–5 条人工示范轨迹，也保护所有已有人工标注；只有显式覆盖操作才允许重标。
- 用户确认：VLM 输出位置作为可选项，用户可以选择原地写入或输出到新目录；原地写入需要明确路径和二次确认。
- 用户澄清：A 电脑部署应用和模型，B 电脑通过局域网访问时，应选择并处理 B 自己电脑上的数据集；不能把 B 的路径当成 A 的本地路径。
- 该需求可以实现，但浏览器安全策略意味着 A 不能直接读取 B 的本地目录。需要在“浏览器上传/同步到 A”与“B 部署轻量本地代理、A 提供 Web UI 和模型服务”之间选择。
- 用户决定分两个版本实施：第一版只支持本机安装、本机使用，不考虑网络访问；第一版稳定后再升级为局域网客户端无需安装、浏览器直接访问并处理客户端本地数据。
- 第一版范围：本机选择单个 LeRobot v3.0 数据集，完成人工 `task augmentation`/固定 `subtask` 标注，检查示范后启动 VLM，再回到 GUI 复核和保存。
- 用户确认：第一版一次只处理一个本地数据集文件夹，完成或关闭当前会话后再切换其他数据集。
- 用户确认：第一版持久化数据集路径、示范轨迹列表、当前阶段、最近一次 VLM 运行状态和输出路径，应用重启后恢复会话。
- 用户确认：VLM 支持断点恢复，默认跳过人工示范和已有有效结果，只处理失败或未完成 episode；另提供显式全量重跑选项。
- 用户确认：示范轨迹直接复用 GUI 左侧 episode 列表；默认取前 5 条，用户可以从列表改选任意 1–5 条，不新增复杂示范选择器。
- 用户确认：启动 VLM 前增加示范完整性检查；每个选中的示范 episode 必须有 `task augmentation` 和固定 `subtask`，辅助标注不参与阻止条件。
- 用户确认：完整性检查通过后，系统自动汇总并展示 `task augmentation` 和 `subtask` 模板，用户确认后才启动 VLM。
- 用户确认：多个示范的 `subtask` 数量、顺序或文本不一致时阻止 VLM，必须回到 GUI 统一后重新检查。
- 用户确认：多个示范的 `task augmentation` 全部汇总保留，由用户选择一条主描述供 baseline/VLM 使用，其余作为参考候选。
- 用户确认：VLM 默认只处理完全没有有效标注的 episode；已有人工或自动标注的 episode 都跳过；显式重跑时才允许覆盖并要求二次确认。
- 用户确认：episode 只有在固定 subtask 集合完整、文本/顺序一致、时间范围有效且通过校验后才算 VLM 完成；否则标记为失败或待人工复核。
- 用户确认：GUI 保存人工修改后，episode 标记为人工已确认并保护；后续 VLM 默认跳过，只有显式解除保护并重跑才允许覆盖。
- 范围纠正：不修改现有 LeRobot GUI，不新增 `Confirm episode` 按钮或复杂标注功能；中间件只负责启动 GUI、检查已有标注、选择示范、启动/恢复 VLM 和记录流程状态。
- 用户指出：当前目标是用中间件把 VLM 和人工标注 GUI 串起来，不应扩展为修改 GUI 产品。
- 下一待确认问题：中间件是否只复用现有 GUI 的保存结果，并在中间件内部记录示范/保护状态。

## 2026-08-03 固定模板时间对齐执行器实现

### 已完成
- 新增 `annotation_workbench/guided_alignment.py`，独立于 LeRobot 原生自由子任务生成流程。
- `/api/vlm` 已切换到该执行器；执行器读取固定 subtask 模板，只请求目标 episode 的时间边界。
- 增加数量、索引顺序、文本、时间范围、重叠、首尾覆盖校验。
- 支持默认跳过已经通过固定模板校验的 episode，支持逐 episode 写回和中途恢复。
- 写回 `meta/lerobot_annotations.json` 时保留其他已有 atom，并保留人工示范中的 task augmentation 候选。
- 未修改 `visualize_dataset` GUI 的标注功能。

### 验证
- `pytest -q annotation_workbench/tests`：6 passed。
- `py_compile annotation_workbench/app.py annotation_workbench/guided_alignment.py`：通过。
- guided alignment smoke：通过。
- 项目 YAML 记录校验：通过。

### 当前限制
- 当前默认 Ollama 服务实际指向 `/home/tbl/Project/models/Qwen3-VL-32B-Thinking`，因此默认端口 `11434` 只列出 `qwen3-vl-thinking:32b`。
- `gemma3:27b` 实际存在于 `/mnt/data/models`，使用 `OLLAMA_MODELS=/mnt/data/models` 在独立端口 `11435` 启动后已成功识别，模型大小约 17.4GB。
- 现有 `/mnt/data/gr00t-finetune/gui_annotation_test_3ep` 测试副本的旧示范 subtask 文本不一致，不能直接作为固定模板真实验收数据。
- 因此当前只证明执行器和边界校验实现正确，尚未证明真实 VLM 时间边界质量；下一步应将默认 Ollama 服务切换到 `/mnt/data/models`，准备 1–5 条人工统一标注的示范 episode，再运行真实小批量测试。
- 第二版范围：局域网客户端浏览器无需安装，客户端本地数据读写，服务端提供 VLM 推理；具体文件访问和传输方案后续单独澄清。

## 2026-08-03 桌面中间件产品重澄清

- 用户否定此前网页工作台产品形态；此前实现只是启动器，不能作为新产品交互基线。
- 新产品是本机单用户的 PySide6 桌面 GUI，运行在 lerobot 虚拟环境中；允许为此安装依赖。
- 用户通过系统文件夹选择框选择数据集，不手工输入路径。
- 桌面端自动拉起/复用本地数据集服务、LeRobot 标注后端和前端；点击后打开原有 LeRobot 可视化 GUI。
- 用户在原有 GUI 中手工标注前五条 episode，随后点击桌面端 VLM 自动标注；桌面端自动读取前五条人工标注作为固定模板。
- VLM 结果直接写入当前选择的数据集；用户再次打开原有 GUI 复核和微调。
- 不做网页端、多用户、局域网、独立模板编辑器、复杂示范选择器或 LeRobot GUI 修改。
- 新业务澄清文件：`.project-log/business-logic/clarification-2026-08-03-desktop-annotation-middleware.yaml`。

## 2026-08-03 PySide6 桌面中间件实现

- 已在 lerobot 环境安装 `PySide6==6.11.1`。
- 新增 `annotation_workbench/desktop_app.py`：系统文件夹选择、数据集校验、自动服务管理、浏览器打开原有 GUI、前五条模板读取、原地 VLM 自动标注、日志与失败状态展示。
- 服务使用动态本地端口，避免旧 GUI/数据服务的固定端口冲突；桌面端关闭时停止自己拉起的服务。
- 已停止旧网页工作台及其遗留的 3002/7861/8082/9000 服务，避免产品形态混淆。
- 验证：8 tests passed；离屏桌面窗口 smoke 通过；隔离端口三服务启动并访问原有 GUI 返回 HTTP 200。
- 待用户在可见桌面环境中选择真实数据集，手工完成前五条一致示范后，实际运行 Gemma 自动标注并在 GUI 中验收。

## 2026-08-03 Qt xcb 启动修复

- 用户实际启动桌面端时出现 `libxcb-cursor.so.0` 缺失导致 Qt xcb platform plugin 崩溃。
- 已在 lerobot Conda 环境安装 `xcb-util-cursor`，并在 `desktop_app.py` 增加启动时自动补齐 Conda `lib` 目录到 `LD_LIBRARY_PATH` 后重启自身。
- 已使用用户原始启动命令在 `DISPLAY=:1`、X11 环境实际运行验证，无 xcb 错误或核心转储。
- `inotify_add_watch` 的 IBus 提示仍可能出现，但不影响 Qt 窗口创建，未纳入本任务处理范围。

## 2026-08-03 示范数量规则修复

- 根因：桌面端错误地要求前五条 episode 全部完成标注，导致用户只完成 `episode 0` 时在 `episode 1` 处被阻止。
- 修复：前五条中至少一条同时包含 `task_aug` 和 `subtask` 即可启动 VLM。
- 多条已完成示范之间仍必须保持 subtask 数量、顺序和文本一致。
- 自动标注目标改为所有未选作完整示范的 episode；未完成的前五条不再被错误跳过。
- 当前真实数据集验证结果：示范 episode 为 `[0]`，固定 subtask 为 3 条，task augmentation 候选为 3 条。
- 针对性测试结果：`9 passed`；`desktop_app.py` 和 `guided_alignment.py` 语法检查通过。

## 2026-07-31 示范轨迹驱动的固定子任务对齐方案

### 方案记录
- 用户提出新的泛化方案：先人工标注一条示范 episode，明确任务描述、固定子任务文本和每个子任务的时间范围；后续 episode 不再由 VLM 自由创建或改写子任务，只根据示范对齐已有子任务的时间范围。
- 目标输出固定为示范中的子任务数量、顺序和文本，VLM 只预测每个子任务在目标 episode 中的 `start/end`；禁止新增、删除、重排或自行改变粒度。
- 示范可适当提供多种语言表述，但子任务结构保持固定；若目标 episode 无法确认某阶段，应输出待人工复核状态，不能静默伪造标签。

### 当前框架判断
- 方案可行，但现有 `subtask_seeded_relabel` 不能直接满足要求：它只在自由分段后修正文本，仍允许模型自行决定子任务数量和边界。
- 需要新增独立的 demonstration-guided temporal alignment 模式：读取人工示范视频/标注，向 VLM 提供示范片段和目标 episode，只接受固定索引的时间范围输出，再由验证器检查数量、顺序、越界、重叠和缺失阶段。
- 当前先不实现该模式；本轮优先验证现有自动标注结果是否能被 GUI 识别、人工修改、保存并再次读取。

## 2026-07-31 第一版本机标注工作台实现

### 已完成
- 新增独立中间件目录 `annotation_workbench/`，不修改 LeRobot GUI 的标注业务功能。
- 支持选择并校验单个本地 LeRobot v3.0 数据集。
- 默认示范 episode 为前 5 条，可改选 1–5 条。
- 支持检查示范是否包含 `task augmentation` 和 `subtask`，并检查多个示范的 subtask 数量、顺序和文本一致性。
- 支持汇总 task augmentation 候选和固定 subtask 模板，由用户选择主 task augmentation。
- 支持启动现有 GUI，并持久化本机会话状态。
- 增加静态操作页、README 和 2 个最小测试。

### 当前明确未完成
- `/api/vlm` 目前仍调用原生 `lerobot-annotate`；它仍可能自由生成 subtask，不能作为已实现的 demonstration-guided temporal alignment。
- 因此 TASK-030 状态为 `implemented-unverified`，下一步应实现独立固定模板时间对齐执行器，再做真实数据集端到端验证。

### 验证
- `pytest -q annotation_workbench/tests`：2 passed。
- `python3 -m py_compile annotation_workbench/app.py`：通过。
- 静态页面 smoke check：通过。

## 2026-08-03 VLM 结果未显示问题排查

- 用户反馈：VLM 运行后重新打开 LeRobot GUI，未看到自动标注结果。
- 检查确认：VLM 已成功写入 `/mnt/data/gr00t-finetune/datasets/lerobot_dataset_right_o6_13d_v30 copy/meta/lerobot_annotations.json`；文件包含 28 个 episode，每个已处理 episode 包含 3 个 `task_aug` 和 3 个 `subtask` 原子。
- 根因：机器上残留了 3 个旧 Next.js 前端实例，但它们对应的动态标注后端和数据服务已经退出；因此打开旧前端时只能看到视频，不能从后端读取 `lerobot_annotations.json`。
- 修复：桌面中间件的三个服务现在各自以独立进程组启动，退出时按进程组回收，避免前端残留；已清理当前 3 套失效前端。
- 验证：完整启动一套当前数据集服务后，请求标注后端的 episode 4 返回 HTTP 200、6 个 atoms（3 个 `task_aug` + 3 个 `subtask`），服务停止后无残留；回归测试 `9 passed`。
- 用户下一步必须重新启动桌面中间件，并点击其“打开 LeRobot GUI 标注”按钮，不要使用之前浏览器中保存的旧端口地址。

## 2026-08-03 子任务解释与 GUI 清理策略确认

- 已向用户解释固定的三个子任务：抓取右侧金属盆、将盆移动到左侧铁锅上方、倾斜盆子完成倾倒。
- 当前桌面中间件已在正常退出、切换数据集和重新启动 GUI 时，按独立进程组清理自己启动的数据服务、标注后端和 Next.js 前端。
- 不增加按端口或进程名的全局无差别清理，避免误杀其他项目的服务。
- 当前剩余边界：如果桌面程序被强制杀死或系统异常关机，旧服务可能残留；再次启动时应优先通过已记录的服务归属进行定向清理，而不是扫描后直接杀进程。

## 2026-08-03 annotation_workbench 独立包需求澄清

- 用户要求最终只保留 `annotation_workbench/` 目录即可运行完整流程。
- `annotation_workbench` 应成为独立 Python 包，内置 `requirements.txt`，用户创建虚拟环境并安装依赖后即可使用。
- 独立包必须包含桌面 GUI、本地 LeRobot v3.0 数据集访问、VLM 自动标注和可视化标注界面所需的资源与逻辑。
- 允许继续依赖外部 Ollama 服务和用户自行下载、配置的 Gemma 模型。
- 用户确认可以安装 Node.js/npm，不要求大范围重构现有前端；优先通过自动安装脚本检查环境并安装前端依赖。
- 方案调整为：保留现有 Next.js 可视化界面，将其前端、后端和本地数据服务迁移到 `annotation_workbench/` 内部，由安装脚本统一准备 Python 和 Node 运行环境。
- 用户确认第一版只支持 Linux/Ubuntu，不考虑 Windows 或 macOS 兼容。
- 用户同意推荐的安装策略：Python 依赖自动安装到虚拟环境；Node.js/npm 缺失时先提示，用户确认后才使用 `sudo apt` 安装。
- 用户确认同时提供 `./run.sh` 和 `python -m annotation_workbench` 两个启动入口。
- 用户确认保留外部 `visualize_dataset/` 和 `lerobot_v1.0/` 代码作为备份。
- 独立包运行时不得依赖这些外部目录；迁移期间它们只用于回退、对照和必要的代码提取。
- 用户确认安装脚本在 `annotation_workbench/.venv` 内创建独立 Python 虚拟环境。
- 独立包不绑定现有 `lerobot` Conda 环境；下一项待确认是系统缺少合适 Python 版本时，安装脚本是否允许提示用户后使用 `sudo apt` 安装 Python。
- 用户确认：系统缺少合适 Python 版本时，先提示并在用户确认后使用 `sudo apt` 安装 `python3`、`python3-venv` 和 `python3-pip`。
- 用户确认其余独立包方案全部按推荐执行：Python 3.11+、Node.js 20 LTS、安装时构建前端、运行时使用 Next.js production、迁移现有前后端而不重构界面、只提取最小 LeRobot 模块、只支持 v3.0、外部 Ollama 配置、不自动下载模型、原地写入标注、保留断点恢复。
- 需求澄清阶段完成，下一步进入需求基线、架构拆分和实施计划阶段。
# 2026-08-03 安装与配置指南

- 新增项目根目录 `agents_guide.md`，面向后续 AI 和用户说明 `annotation_workbench` 的安装、启动、Ollama 配置、模型下载、数据集要求和常见故障排查。
- 明确工作台安装入口为 `annotation_workbench/install.sh`，运行入口为 `annotation_workbench/run.sh`；工作台自带 Python 虚拟环境和前端依赖安装流程。
- 明确 Ollama 是外部可选依赖，仅 VLM 自动标注需要；安装脚本只检查 Ollama 和模型，不自动拉取模型。
- 记录默认配置：`OLLAMA_API_BASE=http://127.0.0.1:11434/v1`、`OLLAMA_MODEL=gemma3:27b`，以及将模型存储到 `/mnt/data/models` 的配置示例。
- 记录用户操作流程、LeRobot v3.0 数据集最低结构、人工示范要求和 401/Qt/端口/Ollama 故障处理方式。
# 2026-08-03 VLM 按 episode 选择与自由标注模式

- 用户确认：首次没有人工示范时允许 VLM 从零自由生成 task augmentation 和 subtask，漂移交由用户在 GUI 中精修；只有前 5 条已有完整示范时才严格复用模板。
- 新增 VLM episode 选择对话框：每次点击 VLM 自动标注时显示全部 episode，默认选中前 5 条，支持选中前 5 条、全选、清空和任意多选。
- 新增三种运行模式：`fixed`（完整示范存在，固定任务和子任务）、`task_only`（仅有 task augmentation，子任务自由生成）、`free`（无示范，任务和子任务均自由生成）。
- 自由模式仍校验输出结构、文本非空、时间范围、顺序、连续覆盖和全 episode 覆盖；结果原地写入 `meta/lerobot_annotations.json`。
- 固定模式保留原有断点恢复和已完成结果跳过逻辑；用户可以先 VLM 初标前 1–5 条，GUI 精修后再次选择剩余 episode，自动切换到固定模板模式。
- 更新 `annotation_workbench/README.md` 和新增测试；验证结果：`14 passed`，Python 语法检查通过。
# 2026-08-03 VLM 单 episode 失败重试

- 用户反馈个别 episode 出现 `输出必须是包含 subtasks 数组的 JSON 对象` 后流程继续，但没有自动重试。
- 已在 `annotation_workbench/guided_alignment.py` 增加单 episode 最多 3 次尝试：模型输出解析失败、结构校验失败或时间范围校验失败均触发重试。
- 前两次失败输出 `status=retrying`、下一次尝试编号和错误；第三次仍失败输出 `status=skipped`、`attempts=3`，不写入错误标注并继续后续 episode。
- 已更新 `annotation_workbench/README.md`；回归测试 `14 passed`，Python 语法检查通过。
# 2026-08-03 连接数据标注远程仓库

- 用户明确要求：只将独立目录 `annotation_workbench/` 连接到 `https://github.com/TBLboy/data_engine.git`，不连接工程根目录，不推送代码，不覆盖当前工作台文件。
- 已在 `annotation_workbench/` 初始化本地 Git 仓库并添加 `origin`。
- 已从远端抓取 `main` 和 `data_label` 两个分支，远程引用分别为 `origin/main` 和 `origin/data_label`。
- 当前仅完成远程连接和 fetch；没有执行 merge、reset、pull、checkout 或 push，现有 `annotation_workbench` 文件保持原样。
- 远端 `data_label` 分支包含数据标注相关项目代码，但与当前工作台不是同一提交历史，因此暂不合并。
# 2026-08-03 annotation_workbench 分支提交

- 在 `annotation_workbench/` 内创建新分支 `annotation-workbench`。
- 将独立工作台源码、内置可视化前端源码、测试、安装脚本和配置提交到该分支。
- 提交：`02e5c64 feat: add standalone annotation workbench`。
- `.venv`、`node_modules`、`.next`、`.system-libs`、缓存和构建产物均未提交；已补充 `.gitignore` 忽略 `.system-libs/`。
- 当前只完成本地 commit，没有执行 `git push`。
# 2026-08-03 推送 annotation_workbench 分支

- 直连 `git push` 因网络等待后被中断，未确认完成。
- 使用 `http_proxy=http://127.0.0.1:10808`、`https_proxy=http://127.0.0.1:10808` 和 Git 代理配置重新推送成功。
- 远程分支：`origin/annotation-workbench`。
- 远程提交：`02e5c643fa410114700372926dd884aab694560c`，与本地提交 `feat: add standalone annotation workbench` 一致。
- 本地 `annotation-workbench` 已设置跟踪远程同名分支；未执行其他分支推送。

# 2026-08-04 MinIO CSV 下载脚本

- 新增 `download_qualified_episodes.py`，按 CSV（`episode_id`/`batch_id`/`batch_name`）从 MinIO 下载 episode 到本地目录。
- 配置通过环境变量或 `--env-file` 读取，密钥不写入代码、日志或输出；支持初始化 MinIO 客户端连接超时和重试。
- 支持批量 CSV、`--prefix-root`/`--prefix-mapping`、`--scope auto|raw|processed`、`--limit`、`--workers`、`--retries`、`--dry-run`。
- 已存在且大小一致的文件自动跳过；下载写入 `.part` 临时文件后原子改名，失败自动重试。
- 输出目录结构：`<output-dir>/<batch_name>/<relative-path-under-batch-prefix>`。
- 离线验证：`py_compile` 通过；解析当前 CSV 共 287 条 episode、3 个 batch；用假 MinIO 客户端验证下载/跳过/大小校验与原子改名正常。
- 当前 `.env` 记录 MinIO endpoint 为 `192.168.21.95:9190`、bucket `yaocao`，但本机路由当前不可达；待内网恢复后再连接执行，建议先 `--limit 1` 单条验证。

# 2026-08-04 MinIO 下载脚本 episode 路径修复

- 用户首次运行时脚本把 `batch_xxx_episode_000000` 错误解析为 `000000`，实际对象目录应为 `episode_000000`。
- 已修复 `derive_episode_name()`，现在保留完整 episode 目录名；离线断言验证通过。
- 修复后使用 `--limit 1 --timeout 5 --retries 0` 真实连接测试，错误已明确变为 `192.168.21.95:9190` 连接超时，说明当前阻塞点是网络/内网可达性，不再是 CSV 或 episode 路径解析。

# 2026-08-04 MinIO 全量下载完成并验证

- 用户连接内网后执行全量下载（去掉 `--limit 1`，`--workers 4`），脚本逐条从 MinIO 拉取 287 条 episode。
- 对 `/mnt/data/gr00t-finetune/datasets` 做了与 CSV（`qualified_episodes_task_type_倾倒 (1).csv`，287 条）逐条对照验证：
  - `double_linkerhand_qingdao_1_2026-07-31_09-54-25`：期望 90，实际 90；126,516 文件 / 20.76 GB。
  - `double_linkerhand_qingdao_2_2026-07-31_11-39-48`：期望 97，实际 97；105,634 文件 / 17.51 GB。
  - `double_linkerhand_qingdao_3_2026-07-31_15-01-20`：期望 100，实际 100；109,645 文件 / 17.80 GB。
  - 总计 287/287，341,795 文件，56.07 GB；缺失 0、空目录 0、`.part` 残留 0。
- 抽查 episode 内部结构完整：`camera_info.json`、`metadata.json`、`telemetry.npz`、`cameras/` 下多路相机 mp4、timestamps.npy、depth 帧目录均存在。
- 结论：下载完整，无需重跑；脚本可断点续传，后续新 CSV 可直接复用 `download_qualified_episodes.py`。

# 2026-08-04 三个 batch 合并转换为 LeRobot v3.0

- 新增 `convert_telemetry_to_lerobot_v30.py`，将原始 `telemetry.npz + 3 路 MP4` 的 batch 数据直接写成 LeRobot v3.0 数据集（使用 lerobot 0.6.1 `LeRobotDataset.create/add_frame/save_episode/finalize` 官方 API，保证 info.json、episodes parquet、stats、chunks 格式与既有 `lerobot_dataset_right_o6_13d_v30` 一致）。
- 数据布局核对：三个 batch 均为**右侧单臂倾倒**——左臂/左手 qpos 完全静止（std≈0），右臂/右手运动；因此采用与既有 v30 参考数据集一致的 13 维布局：
  - `observation.state` / `action` = `qpos[7:14]`（右臂 7 关节）+ `qpos[20:26] * (100/255)`（右手 O6 6 关节）。
  - 3 路 RGB 相机 `cam_top / cam_left_wrist / cam_right_wrist`，h264 crf 23 g 30，与参考数据集编码一致。
  - `robot_type=rokae_right_arm_o6`，`fps=30`，`task=pouring`（可用 `--task` 覆盖）。
- 扫描阶段校验：telemetry 26 维、时间戳严格递增、每路视频帧数与 telemetry 帧数一致；缺失文件直接报错。
- 输出：`/mnt/data/gr00t-finetune/datasets/lerobot_dataset_qingdao_pouring_v30`，共 287 episodes / 112,401 帧 / 3×2 个合并视频文件 / 784MB。
- 验证证据：`LeRobotDataset("local/lerobot_dataset_qingdao_pouring_v30", root=<数据集目录>)` 读取成功，`num_episodes=287`、`num_frames=112401`；ep0 三路图像 (3,480,640)、state/action (13,) float32、task=pouring 均正常。
- 注意事项：读取本地数据集时 `root` 必须传**数据集目录本身**，且 `repo_id` 用 `local/<name>`；传父目录会触发 Hub 拉取并挂起。
- 速度参考：默认编码约 10-12 秒/条（瓶颈为逐帧 Python 循环与 h264 编码，`--encoder-preset veryfast` 无明显加速），287 条约 45 分钟。

# 2026-08-04 示教质量改造：示例局部画面驱动的帧序号对齐

- 用户确认当前“示例秒数 + 目标整段视频”不能形成有效示教，要求按示例视频驱动方案修改代码。
- 用户明确删去示例一致性警告、复杂示例选择器和其他非核心功能，优先提高边界标注质量。
- 已记录 `DEC-008`：固定子任务和 0.1 秒目标采样保留；示例边界附近提取局部画面；目标联系表显示稳定帧编号；VLM 只输出目标 `start_frame`；程序负责把帧编号映射为采样时间并校验单调性和完整覆盖。
- 当前状态：实现进行中，尚未完成真实 VLM 复核。
- 已完成：`video_for_offsets()` 指定偏移抽帧；固定模式示例边界局部图；目标联系表 `FRAME-xxx` 标签；`start_frame` 校验与时间戳转换；自由模式保持旧路径。
- 验证：`pytest -q annotation_workbench/tests` 为 `23 passed`；`py_compile` 和 `git diff --check` 通过；真实数据集只读 smoke 确认 5 条示例各 8 张局部图，目标 episode 0.1 秒帧编号与时间转换无错位。
- 未验证：尚未用 Ollama 对 51/52/53 重新生成并人工比较质量，因此当前状态为 `implemented-unverified`。

# 2026-08-08 记录 GPT VLM 时间对齐行动指南并分析

- 用户将外部 GPT 分析给出的行动指南转交，要求先记录再分析；指南整理记录已存档：`.project-log/briefs/gpt-vlm-alignment-action-guide-2026-08-08.md`。
- 指南核心判断：问题不在 `start_frame -> timestamp` 映射、JSON 校验或 0.1s 采样精度，而在于单次请求给模型 160–230 张目标/示范画面并要求一次预测两个边界；应改为“程序负责 temporal search、VLM 只做局部 visual decision”，每边界独立请求、粗定位→精定位、contact sheet 每页 ≤8 张、简单候选编号（C00/F00），并配套持久化 debug 日志与 contact sheet 落盘。
- 指南还给出：第一阶段 4 组最小诊断实验（无 demo 粗采样 / 单 demo 消融 / 标签可读性 A/B 对比 / ±0.2s 窗口目视检查）；第二阶段 coarse-to-fine；第三阶段人工 ground truth 对 51/52/53 做 6 个边界误差对比；P0/P1 未验证前不重跑 287 条。
- 主 Agent 分析结论（详见回复）：
  - 方向成立，与代码证据一致：51/52 完全相同边界且落在 0.1s 网格帧号 19/58 上，更符合“固定位置/比例选择”而非逐集视觉判别。
  - 补充发现：当前 fixed 提示词仍把五条示范的 `start` 秒数作为文本（`json.dumps(demos)`）发给模型，与示范图像一起构成数字锚定源，实现时应移除示范秒数文本、只保留视觉 before/after。
  - 实验 A/B/C/D 必须依赖 P0 的 JSONL 日志和 contact sheet 落盘才有解释力，因此 P0 顺序正确。
  - 风险点：fine 窗口 ±0.6s 若 coarse 误差超出则失效；`{"candidate": N}` 需要新的解析与重试校验；若 coarse 阶段本身不收敛，应接受“cam_top + gemma3:27b 无法可靠识别该 transition”的退出判定，而不是继续调参。
- 已登记 `DEC-009`（status=proposed, user_approval=pending）：未获用户确认前不改代码。
- 下一步：等用户确认采纳指南，然后先落 P0（debug JSONL + contact sheet 落盘 + episode 51 消融），同时请用户提供 51/52/53 的真实边界作为验收基准。

# 2026-08-08 P0 实跑补录、用户批准与 P1 启动

- 对齐当前工作区时发现 P0 探针已实际运行，但项目记录未同步：`guided_probe.py`、`tests/test_guided_probe.py`、`debug_dryrun/`、`debug_run1/` 与 `annotation_core/vlm_client.py` 修改均未记录。
- P0 结果：10/10 请求可解析；episode 51 参考 GT=`[0,3.5,7]` 时 boundary 1 误差 `0.5–2.0s`，boundary 2 全部预测 `8.5s`、误差 `1.5s`；`debug_run1/vlm_alignment.jsonl` 共 10 行。
- 当前 51/52/53 的 `meta/lerobot_annotations.json` 已有参考边界：51=`[0,3.53,7.0]`、52=`[0,1.9,5.8]`、53=`[0,1.6,5.9]`；它们来自此前自动标注，不能直接当作人工 ground truth。
- 用户同意继续改代码并推进实验/分析。已将 `DEC-009` 转为 `active+approved`，新建 `TASK-036`，Loop 当前任务同步切到 `TASK-036`。

# 2026-08-08 P1 fine 实跑完成：coarse-to-fine 不能救离群误差

## 实现与验证

- 在 `annotation_workbench/guided_probe.py` 新增 `fine_offsets()`、`candidate_label(..., prefix="F")`、`load_coarse_rows()` 与 `run_fine_probe()`；`--fine` 会读取 coarse JSONL，按 coarse candidate 生成 `±0.6s / 0.1s` fine 候选并逐边界独立请求。
- `annotation_core/vlm_client.py` 已修复误用 `final_timestamp` 的字段读取问题；`tests/test_guided_probe.py` 覆盖 fine 候选、前缀解析、粗结果加载和汇总。
- 测试：`pytest -q annotation_workbench/tests` 为 `33 passed`；`py_compile` 与 `git diff --check` 通过。

## 真实实验

### P0 coarse（51）

- 数据集：`/mnt/data/gr00t-finetune/datasets/lerobot_dataset_qingdao_pouring_v30 copy`
- GT 使用 `[0,3.5,7]`，`debug_run1/vlm_alignment.jsonl` 共 10 行。
- b1 误差：none 2.0s、single0 1.0s、single3 1.0s、single4 0.5s、all 2.0s。
- b2 全部预测 8.5s，GT 7.0s，误差 1.5s。

### P1 fine（51）

- 输出：`debug_run1_fine/vlm_alignment.jsonl`，10/10 可解析。
- b1 仅 single4 从 coarse 0.5s 降到 fine 0.4s，其余未改善。
- b2 从 coarse 1.5s 大多恶化为 1.7–2.1s。

### P0 coarse / P1 fine（52、53）

- 52 coarse：none b1 5.5s/GT1.9s err 3.6s；none b2 9.5s/GT5.8s err 3.7s；single4 b1 5.5s err 3.6s；single4 b2 8.0s err 2.2s。
- 53 coarse：none b1 5.5s/GT1.6s err 3.9s；none b2 13.033s/GT5.9s err 7.133s；single4 b1 6.0s err 4.4s；single4 b2 13.033s err 7.133s。
- fine 后误差基本未降低；52/53 的 3.6–4.6s 与 7.13s 离群误差保留。

## 结论

- fine 阶段只能微调 coarse 已接近的候选，无法修正 coarse 完全偏离真实边界的情况。
- `gemma3:27b + cam_top + 局部 contact sheet` 在当前 51/52/53 时间定位上不可靠，不能据此进入 287 条全量自动标注。
- 当前下一步是 C 级路线选择：更换视角/模型、获取人工 GT 重新验收，或接受当前组合不胜任并退出该方向。
- 实验 contact sheets 与 JSONL 作为诊断证据保留在 `annotation_workbench/debug_*`，暂不清理。

# 2026-08-08 整理 VLM 问题包供外部 GPT 优化

- 用户要求把当前问题和 VLM 自动标注相关代码整理到 `/home/tbl/Project/force_touch_model/代码`。
- 已在 `代码/` 创建独立整理包：`README.md`、`目标与问题说明.md`、`给GPT的提示词.md`、`代码/annotation_workbench/`、`实验/`、`参考/`。
- `目标与问题说明.md` 以“VLM 自动标注子任务 start/end 范围”为主轴，P0/P1 只作为已有尝试证据。
- 实验目录只复制真实 JSONL、控制台日志和代表 contact sheet；未复制完整 287 条数据集或前端/venv，包大小约 1.3MB。
- 用户反馈原整理过于聚焦 P0/P1 失败；已按用户意见重排材料主线和 prompt：新增 `目标与问题说明.md`、`给GPT的提示词.md`，将 P0/P1 降为“已有尝试证据”，主轴改为“解决 VLM 自动标注子任务 start/end 范围”。
- 用户反馈包内看不到 VLM 代码；检查确认之前 `代码/代码/` 子目录已不在包内，已重新把源码平铺复制到 `代码/annotation_workbench/`，包含 VLM 客户端、视频抽帧、contact sheet、guided alignment/probe 和相关测试。

# 2026-08-08 分析外部 GPT 精度优先自动标注改造指南

- 用户转来外部文档 `/home/tbl/下载/VLM_LeRobot_v3_精度优先自动标注改造指南.md`，要求判断是否贴合当前目标和框架。
- 已对照当前 `annotation_workbench` 代码、真实数据集 schema 和 0~4/51~53 现有 subtask 边界完成分析。
- 结论：指南与“解决 VLM 自动标注子任务 start/end 范围”的目标一致，核心方向成立，建议按其 P0~P5 分阶段实施；但不建议原样一步改完。
- 需要当前框架适配的点：新增 Task Template、扩展 dataset_reader 读取 frame_index/task_index、修复 vlm_client 图文顺序、实现 per-candidate before/after/uncertain、边界 bracket 搜索、quality gate/leave-one-out、sidecar 暂存与 GUI adapter。
- 当前真实数据集已包含 `frame_index` 和 `task_index`，指南的可实现性成立；现有 subtask 文本与指南示例的 Grasp/Pour/Put back 一致。
- 已新建 `TASK-037`，Loop 已返回 `business-clarification` 阶段，当前澄清域为 `functional-business-logic`，下一动作是确认 V2 边界验收标准与人工 demo 真值。
- 分析文档已存入 `.project-log/docs/vlm-v2-guide-analysis-2026-08-08.md`；`clarification.yaml` 已改为 open 并列出待确认项。
- 用户回答“不要冻结”当前 0~4 demo 时间点；已记录为不可直接作为 V2 人工标准，后续必须先建立人工复核后的真值。
- 用户明确暂停当前 Qingdao 数据集的进一步标定实验：不再继续在现有数据上浪费时间。后续将使用新的数据集重新做一次标定测试，标定结果好坏由用户自己评价。
- 当前分析、P0/P1 实验记录继续保留，但不再作为 V2 标定验收基准；新数据集的输入、任务、GT 与评价方式待用户后续补充。
- 用户提出第一个新要求：示范数据集不能固定为前 5 条；需要支持用户选择哪些 episode 作为示范数据集，以适配“可能只人工标注其中若干条”的实际工作流。
- 已落地 TASK-038：`EpisodeSelectionDialog` 拆成“示范 episode”和“自动标注 episode”两组多选；示范组仅允许已完整标注的 episode，模板读取只基于用户选择的 demo_episodes。
- 验证：`37 passed`、`py_compile`、`git diff --check`、offscreen dialog smoke 均通过；已记录 `EV-064`。等待用户在真实桌面端验证。

# 2026-08-08 用户真实测试与项目暂停

- 用户已在真实桌面端测试选择示范/自动标注的功能；选择交互本身可用，但 VLM 子任务识别精度仍然很差。
- 用户决定当前项目先到此为止，不再继续推进实验和功能开发。
- 当前记录保留，后续如果用户决定恢复，应从“VLM 子任务边界准确率”方向重新开始，而不是继续调整当前选择逻辑。

# 2026-08-08 正式数据集任务描述复制

- 用户要求把实验数据集的已标注任务描述复制到正式数据集，只复制任务描述，不复制子任务。
- 实际源目录为 `/mnt/data/gr00t-finetune/datasets/lerobot_dataset_qingdao_pouring_v30 copy`；用户消息中的 `_copy` 路径不存在。
- 实验集 `lerobot_annotations.json` 覆盖 63 条 episode，每条都有相同的 4 条 `task_aug` 任务描述。
- 正式集已写入全部 287 条 episode，`task_aug` 总数 1148，`subtask` 未复制。
- 已用 `LeRobotDataset` 读回验证：`287 episodes / 112401 frames`，任务描述文件可读。

# 2026-08-08 正式集 canonical task 写入 meta/tasks.parquet

- 用户要求主 Agent 自行确认一条 canonical 任务描述并写入正式集 `meta/tasks.parquet`，暂不开始训练。
- 选择的第一条 canonical：`Pick up the Nongfu Spring plastic mineral water bottle seen in front of you with your right hand, pour the objects inside it into the black round iron pot with a handle, then place the bottle back onto the desktop`。
- 已将 `task_index=0` 的 task 文本从 `pouring` 改为该描述，并保留备份 `meta/tasks.parquet.before_canonical`。
- `LeRobotDataset[0]["task"]` 已确认返回完整描述；`language_persistent` 仍未导出，当前 GR00T 默认读 `task`，因此直接训练会使用该 canonical 描述。

# 2026-08-08 训练准备：数据集替换与样本/资源预算

- GR00T 训练脚本确认已接入：`lerobot_v1.0/examples/groot/finetune_right_o6_13d_lerobot.sh`。
- 正式 Qingdao 数据集：`len(LeRobotDataset)=112401`，`effective batch=8`（batch_size=1 x grad_accum=8）。
- 按当前参数：1 pass ≈ 14051 优化步；旧数据集 47250 帧时原 30000 步约 5.08 pass；同一 30000 步换到现数据集约 2.14 pass；5-pass 对齐约 70255 步。
- 已把训练脚本默认切到 `/mnt/data/gr00t-finetune/datasets/lerobot_dataset_qingdao_pouring_v30`、新 W&B/输出/任务名；首轮 `TOTAL_STEPS=30000`、`SAVE_FREQ=10000` 作为快速检查点。
- 资源现状：RTX 4090 24.5GB、Ollama 当前占约 4.5GB；旧训练峰值 14.24GB；本机 32 CPU、31GB RAM、/mnt/data 可用约 54GB；旧 6 个 checkpoint 已占约 71GB。训练前应停止 Ollama 和较重 GUI 进程，并为 checkpoint 磁盘留下空间。

# 2026-08-08 最小训练-保存闭环

- 用户要求先跑 100 步最小训练闭环，验证训练-保存链路正常后清理测试残留。
- 首次运行因 Ollama 子进程占用约 18GB 显存 OOM；Ollama 子进程释放后重跑成功。
- 最小运行：`TOTAL_STEPS=100`、`SAVE_FREQ=100`、`WANDB_ENABLE=false`、输出到 `/tmp/lerobot_gr00t_smoke_100_20260808_162914`。
- 结果：100/100 steps 完成，loss 约 `1.068`，`mem_gb=14.38`；`checkpoints/000100` 包含 `pretrained_model/model.safetensors`、optimizer/scheduler/rng 和 `training_step.json`（step=100）。
- 已确认训练-保存链路正常，随后清理 `/tmp/lerobot_gr00t_smoke_100_20260808_162914`，无测试残留。

# 2026-08-08 三 pass 正式训练参数与 Ollama 清理

- 用户要求训练三个完整 pass，并给出训练启动指令，同时确认后台 Ollama 已停止。
- `TOTAL_STEPS` 已从 `30000` 改为 `42153`（3 pass）；`SAVE_FREQ` 改为 `14051`，按 pass 保存 checkpoint。
- 已 kill `ollama serve` PID `16512`；确认 `ollama` 与 `llama-server` 均无进程，显存已释放。

# 2026-08-08 学习率调度实现：warmup + constant + linear decay

- 用户要求把学习率调度从 `constant_with_warmup` 改成 `warmup -> 固定 LR -> 线性衰减`。
- 已在 `lerobot_v1.0/src/lerobot/optim/schedulers.py` 新增 `constant_linear_decay_with_warmup`，并在 `lerobot_v1.0/src/lerobot/optim/__init__.py` 导出。
- 已把 `examples/groot/finetune_right_o6_13d_lerobot.sh` 切换为 `--scheduler.type=constant_linear_decay_with_warmup`。
- 已增加 scheduler 单测；`tests/optim` 通过 `21 passed`，`py_compile` 通过。
- `TOTAL_STEPS/SAVE_FREQ` 仍保留当前值待用户后续确定最终轮次参数，本次未跑正式训练。

# 2026-08-08 单 pass 训练参数确定

- 用户确认改为只训练 1 个完整 pass。
- 脚本参数更新：`TOTAL_STEPS=14051`、`SAVE_FREQ=7000`、`num_warmup_steps=703`、`min_lr_ratio=0.0`。
- `constant_linear_decay_with_warmup`：warmup 703 步升到 5e-5，随后线性衰减到最后一步 0。

# 2026-08-08 中断训练清理

- 用户手动停止了已启动的正式训练，要求检查并清理训练残留。
- 检查确认无 `lerobot-train` 进程残留；GPU 显存已释放；Ollama/llama-server 均无进程。
- 残留目录 `/mnt/data/gr00t-finetune/outputs/lerobot_qingdao_pouring_gr00t_n1_7_v1` 仅含一个 W&B run（约 1.2MB），无 checkpoint。
- 已删除该输出目录；当前可直接重新启动训练，不会因输出目录已存在而失败。

# 2026-08-09 单 pass 正式训练完成检查

- 用户报告训练结束并要求检查；已核对 `output.log`、W&B summary 和全部 checkpoint。
- 训练日志最后显示 `Training: 100% 14051/14051`、`Checkpoint policy after step 14051` 和 `End of training`；训练约耗时 4 小时 13 分钟。
- `checkpoints/007000`、`checkpoints/014000`、`checkpoints/014051` 均存在，`checkpoints/last` 指向 `014051`；三个 checkpoint 的 `training_state/training_step.json` 分别为 7000、14000、14051。
- W&B run：`nrea7gvg`，https://wandb.ai/026itaciya-11/lerobot-gr00t-qingdao-pouring/runs/nrea7gvg
- W&B summary 最终值：`loss=0.0347`、`grad_norm=0.1304`、`lr=2.39e-08`、`gpu_mem_gb=14.38`、`samples_per_s=56.40`、`epochs=0.125`。
- 输出目录总量约 36GB；每个 checkpoint 约 12GB。
- 已完成 `TASK-039` 检查与 `EV-066` 记录；`validate_project.py` 校验通过。
- 尚未做真机 rollout；loss 只代表训练完成，不等于真机成功率。下一步待用户决定部署与评测方式。

# 2026-08-09 真机部署链路只读盘点

- 为准备下一步部署，只读检查了 LeRobot 的 `lerobot-rollout` 与 `async_inference` 部署入口。
- `lerobot-rollout` 和 `async_inference` 已支持 `groot` policy；最终 checkpoint `014051` 在目录结构上是标准 LeRobot `pretrained_model + preprocessor/postprocessor` 产物。
- 当前 LeRobot 内置 robot registry 没有 `rokae_right_arm_o6`；`lerobot-rollout` 的可用 robot type 集合与 `make_robot_from_config()` 也没有目标机型驱动。
- 因此“模型可加载”不等于“真机可部署”。在连接真机前，需要用户提供 ROKAE 的 Python 驱动/SDK，或确认已有独立真机控制与策略推理桥接程序；否则不能直接运行 `lerobot-rollout --robot.type=...`。
- 真机评测前应另开一个受控任务：接入 ROKAE 驱动、映射 13D action/state、配置 3 路相机，并先在校准/静态环境下验证动作安全，再执行成功率测试。

# 2026-08-09 最终 checkpoint 严格加载与推理 chunk 验证

- 使用最终 checkpoint 的 `config.json` 自动加载：`base_model_path=/mnt/data/gr00t-finetune/models/gr00t_n1_base`，与训练配置一致。
- `GrootPolicy.from_pretrained(checkpoint/014051/pretrained_model, strict=True)` 通过，无 missing/unexpected key；模型在 CUDA 上可读，`dtype=float32`。
- 对 Qingdao 正式集首帧执行完整 preprocess -> `predict_action_chunk` -> postprocess：输出 `(1,40,13)`，数值所有值有限。
- 确认相对 action 模式下不能用 `select_action()`，会显式报错；部署执行必须使用 `predict_action_chunk` 后整段 postprocess，或走 rollout 的 RTC/chunked 推理路径。
- 发现原 `examples/groot/smoke_test_right_o6_13d_lerobot.py` 对“微调后 LeRobot checkpoint”直接把它当作 `base_model_path` 使用，会造成大量 UNEXPECTED/MISSING 加载报告，不宜作为最终 checkpoint 的加载验证；本次已用正确分别加载方式重新验证。
- 真机 rollout 仍缺 ROKAE robot 驱动接入；模型层加载和推理 chunk 已具备证据。

# 2026-08-09 Loop 阻断记录：等待 ROKAE 真机接入输入

- 单 pass 训练、checkpoint 保存、严格加载和推理 chunk 均已验证；剩余核心缺口是 ROKAE SDK/驱动或现有桥接程序。
- 多轮自动继续后没有新用户输入，也没有外部 ROKAE SDK/真机状态变化；无法继续推进真机成功率评测。
- Loop 状态已标记为 blocked：当前等待用户提供 ROKAE Python 驱动/SDK、现有桥接入口或明确的新部署路线。

# 2026-08-09 训练中间产物清理

- 用户要求只保留最终部署 checkpoint，已删除 `checkpoints/007000`、`checkpoints/014000` 和本地 `wandb/` 残留。
- 保留 `checkpoints/014051`，`checkpoints/last` 仍指向 `014051`，`training_step.json` 为 step=14051。
- 输出目录由约 36GB 降到约 12GB，`/mnt/data` 可用空间从约 19GB 提升到约 42GB。

# 2026-08-09 DexBot 部署框架只读盘点

- 用户提供 `~/Project/dexbot_ros2_ws-dex_vla` 作为部署框架；本轮只读检查，未修改任何代码。
- 框架采用 artifact sidecar -> policy service -> worker -> ActionAdapter -> SafetyGate -> robot driver 的链路；模型事实从 `dexbot_policy_artifact.json` 读取。
- 当前框架已接 LeRobot ACT/Pi0.5/InDex 和 OpenPI，但没有 GR00T 特化 backend；`backend/policy_backends/lerobot_backend.py` 依赖目标机 `lerobot.dexbot.eval.policy_backend.LinkerPolicyBackend`，当前本机 `/home/tbl/Project/lerobot` 与工作区都没有该模块。
- 最终 checkpoint 已确认是 LeRobot GR00T N1.7 `use_relative_actions=true`、13D state/action、三相机 `cam_top/cam_left_wrist/cam_right_wrist`、chunk 40；其 preprocessor/postprocessor sidecar 自带 raw stats，不依赖训练数据集即可加载。
- 离线探针确认 `predict_action_chunk + postprocessor` 输出为 absolute 13D，训练帧上 arm 预测接近 ground truth，hand 有误差但量纲一致。
- 下一步接入需要新增 GR00T backend、生成 `dexbot_policy_artifact.json`、注册 model profile 与 observation schema/camera key map，并先做坐标和推理延迟验证。

# 2026-08-09 GR00T 两相机训练配置调整

- 用户确认 Qingdao pouring 只使用右手，左腕相机不作为输入，因此 GR00T 改为只消费 `cam_top + cam_right_wrist`。
- 原三相机数据集不修改；在训练配置里通过 `--policy.input_features` 显式声明 `observation.state + cam_top + cam_right_wrist`。
- 已用 `steps=0` 配置级 smoke 验证：LeRobot 训练入口成功创建两相机 GrootPolicy，仍从原 287 episodes / 112401 frames 数据集读取，左腕相机不进入 `input_features`。
- 已修改 `lerobot_v1.0/examples/groot/finetune_right_o6_13d_lerobot.sh`，输出目录改为 `/mnt/data/gr00t-finetune/outputs/lerobot_qingdao_pouring_gr00t_n1_7_v2_2cam`，job/W&B notes 更新为 v2 两相机。
- 其余训练参数不变：1 pass、14051 steps、effective batch 8、lr=5e-5、warmup 703、constant_linear_decay、bf16、checkpoint 7000。

# 2026-08-09 旧训练输出清理

- 用户决定旧模型全部不再保留，为两相机重新训练释放磁盘。
- 已删除 `/mnt/data/gr00t-finetune/outputs` 下全部历史训练输出：
  - `gr00t_n1_right_o6_13d_retrain`（约 15GB）
  - `lerobot_qingdao_pouring_gr00t_n1_7_v1`（约 12GB，含旧最终 checkpoint 014051）
  - `lerobot_right_o6_13d_from_official_n1_7`（约 71GB）
- 保留 `/mnt/data/gr00t-finetune/models/gr00t_n1_base`、`cosmos_reason2_2b` 和 Qingdao v30 数据集。
- 清理后 `/mnt/data` 可用空间约 139GB，新训练输出目录 `..._v2_2cam` 尚未创建，可直接启动。

# 2026-08-09 两相机 GR00T 正式训练已启动

- 用户在 `lerobot_v1.0` 执行 `RUN_TRAINING=1 bash examples/groot/finetune_right_o6_13d_lerobot.sh`，训练进程 PID `1409573` 已正常开始。
- `input_features` 确认为 `observation.state + cam_top + cam_right_wrist`，没有 `cam_left_wrist`。
- W&B run：`ua9kp69v`，https://wandb.ai/026itaciya-11/lerobot-gr00t-qingdao-pouring/runs/ua9kp69v
- 训练启动阶段 loss 约 1.06~1.08，GPU 显存约 14.38GB；日志显示 `Effective batch size 1 x 8 x 1 = 8`、`steps=14051`。
- “Unrecognized GR00T N1.7 backbone model name” 是既有兼容提示，回退到 Qwen3-VL 路径，不影响训练启动。

# 2026-08-10 两相机 GR00T 训练完成检查

- 日志最后为 `14051/14051`、`Checkpoint policy after step 14051`、`End of training`，无训练进程残留。
- checkpoints 包含 `007000`、`014000`、`014051`，`last -> 014051`；training_step 分别为 7000、14000、14051。
- W&B run `ua9kp69v` 最终 summary：loss=0.03498、grad_norm=0.12998、lr=2.39e-08、gpu_mem=14.38GB、runtime=15250s。
- 输出目录当前约 36GB；尚未做真机 rollout，loss 不代表真机成功率。

# 2026-08-10 两相机训练中间产物清理

- 已删除 `checkpoints/007000`、`checkpoints/014000` 和本地 `wandb/`，保留 `checkpoints/014051` 与 `last -> 014051`。
- 输出目录从约 36GB 降到约 12GB；`/mnt/data` 可用约 128GB。
- W&B 线上 run `ua9kp69v` 仍保留，最终 checkpoint 用于后续部署。

# 2026-08-11 统一工作区与工程记录合并

- 用户要求后续只在 `/home/tbl/Project/force_touch_model` 一个工作目录下工作，并把 DexBot VLA 工程完整迁入。
- 已按工作区现有模式将 `dexbot_ros2_ws-dex_vla` 整仓移动为 `/home/tbl/Project/force_touch_model/dexbot_ros2_ws-dex_vla`，保留独立 `.git`、`dex_vla` 分支和原 remote。
- DexBot 历史工程记录已整体并入根 `.project-log/subprojects/dexbot_ros2_ws-dex_vla/`，作为子工程命名空间保留完整原记录。
- 已更新源码配置、VS Code 配置、迁移后的子工程记录和工作区 AGENTS 中的旧绝对路径；根日志新增 `TASK-040`、`DEC-010`、`TRACE-014`、`EV-068`。
- 验证：根 Project Log 校验通过；DexBot 聚焦测试 `60 passed, 2 deselected`；源码/运行时配置已指向新路径，老的 `/home/tbl/Project/dexbot_ros2_ws-dex_vla` 顶层路径已不存在。
- 后续 VLA 相关代码、测试和 ROS 相关工作统一在 `/home/tbl/Project/force_touch_model/dexbot_ros2_ws-dex_vla` 内执行。

# 2026-08-11 统一工程归档

- 已把合并后的 `/home/tbl/Project/force_touch_model/.project-log` 归档到 `/home/tbl/Project/My_knowledge_base/工程记录/force_touch_model/.project-log`。
- 归档包含根 Project Log 和 `subprojects/dexbot_ros2_ws-dex_vla/` 完整 DexBot 历史记录。
- 已只提交 `force_touch_model` 对应目录并推送，未用 `git add -A` 带入知识库中其他未跟踪文件。

# 2026-08-13 GR00T 远端部署准备

- DexBot 子工程已把 GR00T 模型服务切为远端推理模式，并提交推送 `dex_vla` 分支：`c35ca8a..b067c56`。
- 关键配置：`groot_qingdao_pouring_014051_local` 使用 `192.168.97.184:18083`、`artifact_residency=service_host`。
- 验证：GR00T 聚焦测试 `60 passed, 2 deselected`；runtime bundle 在 service_host 模式下不读本地权重。
- 详细记录见 `.project-log/subprojects/dexbot_ros2_ws-dex_vla/current-session.md`。
- 已新增并推送远端部署手册 `docs/GR00T_REMOTE_DEPLOYMENT.md`，提交 `feee740`。
- 按用户指定将 GR00T 模型服务地址改为 `192.168.20.147`，已推送提交 `06edc9d`。
