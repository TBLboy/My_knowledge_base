# VLM 自动标注时间边界持续失败：背景简报（供外部 AI 分析）

## 1. 目标与精确问题

**场景**：LeRobot v3.0 机器人数据集（右手抓取矿泉水瓶，把瓶内物体倒入黑色铁锅，再放回桌面）。已有人工示范 episode 0/1/2（用户手动标注），固定 3 个英文子任务：

1. `Grasp the Nongfu Spring plastic water bottle with the right hand`
2. `Pour the objects inside the bottle into the black round iron pot with a handle`
3. `Put the bottle back on the desktop`

**问题**：2026-08-08 使用新方案（示例边界局部图 + 目标帧编号）重新运行 VLM 自动标注后，episode 51/52/53 的子任务边界“完全和真实情况对不上”，比之前更差。

**需要外部 AI 判断**：
- 为什么模型无法利用人工示范画面学会动作切换点？
- 当前失败更可能来自图像呈现、提示词、示例冲突、模型多图能力、上下文长度，还是评估口径？
- 下一步最小但有效的改动方向是什么？

## 2. 相关系统与项目背景

### 数据流（当前实现）

1. 桌面端 `read_template()` 从 `meta/lerobot_annotations.json` 读取前 5 条示范，检测到 subtask + task_aug 后进入 `fixed` 模式。
2. `run()` 对目标 episode 用 `VideoFrameProvider.video_for_episode()` 按 `sample_interval=0.1` 抽取帧，`sampled_offsets()` 始终包含首末帧。
3. `_demo_visuals()` 对每条示范的每个边界（第 2、3 个子任务开始处）抽取 `-0.2s/-0.1s/+0.1s/+0.2s` 共 4 帧，5 条示范共 40 张局部图。
4. `build_messages()` 组装单条 user 消息：提示词文本 + 每条示范的 contact sheet（标签 `EP{episode}-B{boundary}-{position}`）+ 目标 contact sheet（标签 `FRAME-000` 起，20 帧一页）。
5. `OllamaClient.generate_json()` 通过 OpenAI 兼容接口以多图 base64 JPEG 调用 `gemma3:27b`，要求模型只返回 JSON。
6. `validate_frame_payload()` 校验 `start_frame` 数量、index、单调性、越界、首帧必须为 0。
7. `frame_payload_to_timestamps()` 把 `start_frame` 映射为 `sampled_times[frame]`；`end` 由下一段 `start` 推导，最后一段到末帧。
8. `build_atoms()` 写入 subtask atoms（只保存起始时间戳），`save_annotations()` 原地写回。

### 关键代码位置

- `annotation_workbench/guided_alignment.py`
  - `build_messages()` 约第 333 行（fixed 模式提示词与图片组装）
  - `validate_frame_payload()` 约第 245 行
  - `frame_payload_to_timestamps()` 约第 275 行
  - `_demo_boundary_offsets()`、`_demo_visuals()` 约第 297-331 行
  - `run()` 约第 395 行起（固定模式校验链）
- `annotation_workbench/annotation_core/video_frames.py`
  - `video_for_offsets()`：按任意相对偏移抽帧，偏移归一化后返回
- `annotation_workbench/annotation_core/contact_sheet.py`
  - `to_contact_sheet_blocks()`：支持自定义标签，每帧缩略 224px 宽，左上角黑条打印标签
- `annotation_workbench/annotation_core/vlm_client.py`
  - `OllamaClient.generate_json()`：多图转 base64 JPEG，temperature=0，max_tokens=512

## 3. 期望行为 vs 实际行为

### 期望

- 模型参考示范边界前后画面，识别“抓取结束→倾倒开始”“倾倒结束→放回开始”的视觉变化。
- 在目标 contact sheet 中选择与实际动作切换一致的 `FRAME-xxx` 编号。
- 边界误差应明显小于旧“直接猜秒数”方案。

### 实际

- episode 51/52/53 新结果为：
  - 51：`[0.0, 1.9, 5.8]`（旧备份 `[0.0, 1.667, 4.2]`）
  - 52：`[0.0, 1.9, 5.8]`（旧备份 `[0.0, 1.4, 5.633]`）
  - 53：`[0.0, 1.6, 5.9]`（旧备份 `[0.0, 1.5, 4.2]`）
- 用户判定“完全和真实情况对不上”，且比旧方案更差。
- 51 和 52 输出完全相同（`1.9/5.8`），疑似模型稳定输出某个默认编号而非基于画面判断。

## 4. 复现与精确证据

### 数据集与标注文件

- 数据集：`/mnt/data/gr00t-finetune/datasets/lerobot_dataset_qingdao_pouring_v30 copy/`
  - LeRobot v3.0，287 episodes / 112401 帧，30fps，3 路相机，标注使用 `cam_top`
- 当前标注：同目录 `meta/lerobot_annotations.json`
  - 最后修改：`2026-08-08 11:18:14 +0800`
  - 当前只含 60 个 episode
- 全量备份：同目录 `meta/lerobot_annotations.backup_20260804_174425.json`（287 个 episode）

### 人工示范（用户手动标注，已确认存在）

| Episode | 时长 | 子任务起点 |
|---|---:|---:|
| 0 | 19.133s | `[0.0, 6.0, 11.45]` |
| 1 | 24.800s | `[0.0, 7.0, 10.39]` |
| 2 | 20.000s | `[0.0, 3.6, 7.167]` |
| 3 | 16.400s | `[0.0, 1.667, 6.667]` |
| 4 | 16.100s | `[0.0, 1.633, 7.367]` |

注意：之前有一次检测显示 `free` 模式、示范为空，是检查脚本误把 `meta/` 目录当作数据集根目录导致的假象，不是数据问题。

### 示例边界比例（人工标注本身差异很大）

| Episode | 倾倒开始占比 | 放回开始占比 |
|---|---:|---:|
| 0 | 0.314 | 0.598 |
| 1 | 0.282 | 0.419 |
| 2 | 0.180 | 0.358 |
| 3 | 0.102 | 0.407 |
| 4 | 0.101 | 0.458 |

### 当前提示词（fixed 模式）

```text
You are a temporal annotation assistant. Use the demonstration video boundary crops as the labeling standard.
Task description: ...
Fixed subtasks, in this exact order and exact text:
0: ...
1: ...
2: ...
Demonstration boundary metadata (the following images show the real action before and after each boundary):
[{"episode": 0, "subtasks": [{"text": "...", "start": 0.0}, ...]}, ...]
For the target episode, return ONLY JSON using the numbered target frames:
{"subtasks":[{"index":0,"text":"...","start_frame":0}, ...]}
The text must be copied exactly. Do not add, remove, reorder, or split subtasks.
Return only start_frame for each subtask. start_frame is a zero-based target-frame number, not seconds.
The first start_frame must be 0. Choose the frame where that subtask begins.
Use the demonstration images to recognize the same visual transition in the target contact sheet.
```

### 每次请求的图片构成

- 示范：5 条 × 8 张边界局部图 = 40 张
- 目标：0.1s 采样约 120-190 张（episode 51=131、52=120、53=132）
- 合计约 160-230 张，每张缩略到 224px 宽，contact sheet 每 20 张一页

## 5. 环境、依赖与约束

- 本地 Ollama，`gemma3:27b`（Q4_K_M），API `http://127.0.0.1:11434/v1`，OpenAI 兼容
- 调用参数：`temperature=0`、`max_tokens=512`；单次请求最多 2 次 JSON 解析重试；单个 episode 最多 3 次尝试
- Python 3.11 venv：`annotation_workbench/.venv`；依赖 PyAV、Pillow、httpx、openai
- 桌面端 PySide6 GUI 启动，数据集选择为文件夹对话框
- 约束：不修改 LeRobot GUI；不改变固定子任务数量/顺序/文本；不引入新服务或复杂功能；用户明确不要示例一致性告警等“花哨”功能

## 6. 已尝试方案与结果

| 版本 | 方案 | 结果 |
|---|---|---|
| v0 | 60 帧采样，模型直接输出秒数，吸附最近真实帧 | 87.5% 边界精确等于缩略图秒数（模型照抄读数），但语义边界不可信 |
| v1 | 0.1s 采样，模型输出秒数，吸附最近真实帧 | 仅 42% 边界精确落在 0.1s 网格，其余大多偏 1 帧；用户判定无改善 |
| v1b | 吸附改为 0.1s 网格标签 | 用户判定仍差 |
| v2（当前） | 示例边界局部图 + 目标 `FRAME-xxx` 编号 + 程序转换 | 51/52/53 结果更差，与真实情况不符 |

代码侧验证：`pytest -q annotation_workbench/tests` 为 `23 passed`；`py_compile`、`git diff --check` 通过；真实数据集只读抽帧 smoke 确认示例各 8 张、目标帧编号与时间转换无错位。

## 7. 未知项与请求帮助

### 确认项

- 0/1/2 是用户手动标注，当前仍在 `lerobot_annotations.json` 中。
- 51/52/53 在 08-08 重跑后确实被更新。
- 新方案已生效：51 的 `1.9/5.8` 对应 `sampled_times[19]` 和 `sampled_times[58]`，说明模型确实返回了 `start_frame` 并通过校验，而非旧的秒数路径。

### 未知项

- 用户未提供 51/52/53 的“真实期望边界”具体数值，只有“完全对不上”的定性判断。
- GUI 日志未持久化，无法拿到模型每次的原始输出文本和重试记录。
- `gemma3:27b` 在该次请求下的实际多图上限、有效上下文和图片细节读取能力未知。
- 不确定模型是否真的读取了 contact sheet 上的 `FRAME-xxx` 标签，还是按位置猜测。
- 不确定 40 张示范局部图是帮助还是干扰（示例之间人工边界差异大）。

### 请求帮助的具体产出

1. 判断最可能的根因（提示词/图像呈现/示例冲突/模型能力/上下文/评估口径）。
2. 给出可验证的最小实验设计（例如：单条示范 vs 五条示范、不同标签格式、减少图片数、边界局部图放在目标图之前/之后、改用窗口化逐边界判断等）。
3. 指出当前代码里可能被忽略的缺陷（例如 contact sheet 标签可读性、`start_frame` 映射、模型对多图顺序的敏感性）。
