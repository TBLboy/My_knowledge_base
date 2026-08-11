# GPT VLM 时间对齐行动指南（外部 AI 分析产物）

> 来源：用户将外部 GPT 分析结果转交，要求先记录再分析。
> 创建：2026-08-08
> 状态：已记录，待主 Agent 分析后由用户确认是否采纳。
> 关联：`context-brief-vlm-temporal-alignment-2026-08-08.md`、DEC-008、DEC-009（proposed）
> 以下为外部 GPT 行动指南的整理记录：核心结论、实验步骤、实现方案和执行顺序均保留；个别段落为清晰起见做了精简表述，原始文本在本次会话消息中。

# VLM 自动标注下一步行动指南

## 一、当前判断

当前 v2 方案的问题，优先不要再从 `start_frame -> timestamp` 映射、JSON 校验或 0.1 s 采样精度上排查。

已有证据表明：

* `start_frame` 已正确映射到 `sampled_times[frame]`
* episode 51 的 1.9 s / 5.8 s 确实来自 frame 19 / 58
* 单元测试、py_compile、smoke test 均未发现时间错位
* 当前失败更像是 VLM 在一次请求中接收过多视觉内容后，无法稳定完成细粒度时序定位

因此下一阶段的核心原则是：

**程序负责 temporal search，VLM 只负责局部 visual decision。**

不要再要求 VLM 一次浏览完整 episode 的 120–190 个目标帧，并直接输出两个精确边界。

## 二、第一阶段任务：先做最小诊断实验，不立刻大改架构

先只测试 episode 51。

暂时不要批量跑 51/52/53，更不要直接重跑整个数据集。

需要完成以下 4 组实验，并保存每次模型原始输出。

### 实验 A：去掉所有 demonstration

目标：

判断模型仅依靠目标画面，是否具备基本动作阶段识别能力。

修改方式：

* 不发送 5 条 demo
* 目标 episode 51 改为约 0.5 s 间隔采样
* 不要使用当前约 0.1 s 的 131 张目标帧
* 目标总帧数控制在约 20–35 张
* contact sheet 每页 8 张，建议 2×4
* 每张图使用简单候选编号，如 C00、C01、C02 ...
* 不使用长格式 `FRAME-000`

分别询问两个边界：

1. Grasp -> Pour
2. Pour -> Put back

两个边界必须分成两个独立 VLM 请求。

不要让一次请求同时预测两个边界。

输出格式例如：

```json
{"candidate": 7}
```

其中 candidate 表示“新子任务首次明显开始”的候选图编号。

记录：

* 模型原始响应
* candidate
* 对应时间
* contact sheet 图片
* 请求中实际发送图片数量

---

### 实验 B：单 demonstration 对比

继续使用 episode 51。

分别运行：

* 无 demo
* 仅 demo episode 0
* 仅 demo episode 3
* 仅 demo episode 4
* 当前 five-demo

除 demo 数量以外，其余条件完全一致。

不要混入其它修改。

目的：

判断 5 条示范是否存在明显干扰。

如果单 demo 明显优于 five-demo，则后续默认不再一次发送 5 条示范。

---

### 实验 C：验证模型是否真的能读标签

选择 episode 51 的一个短窗口，例如连续 8 张图。

制作两版完全相同的 contact sheet。

第一版编号：

```text
A B C D E F G H
```

第二版编号：

```text
FRAME-037
FRAME-038
...
```

让模型分别指出同一个视觉事件对应哪张图片。

目的：

判断复杂的 `FRAME-xxx` 是否造成标签读取问题。

如果字母版本稳定而 FRAME 版本不稳定：

后续视觉请求统一只使用简单局部编号。

程序内部再把局部编号映射回真实 frame index。

---

### 实验 D：验证 ±0.2 s demo 是否视觉差异过小

针对人工 demonstration 边界，生成两套示范图。

当前方案：

```text
-0.2 -0.1 +0.1 +0.2
```

新方案：

```text
-0.6 -0.3 +0.3 +0.6
```

人工直接检查 contact sheet。

重点判断：

* before / after 是否肉眼可区分
* 瓶子角度是否明显变化
* 手的位置是否明显变化
* 是否已能明确判断新动作阶段开始

如果当前 ±0.2 s 四张图几乎一样，后续 demo 默认改宽窗口。

---

## 三、第二阶段任务：实现 coarse-to-fine

完成上述诊断后，开始修改正式流程。

目标不是一次性预测完整 episode，而是每个边界独立进行两阶段定位。

## 四、Coarse 阶段

### 1. 输入

针对目标 episode，以约 0.5 s 间隔抽帧，如 0.0/0.5/1.0/1.5/2.0 ...

不要超过约 30–40 个候选帧。

episode 更长时可自动提高 coarse interval，但目标候选数保持 <= 40。

### 2. 每页 contact sheet

每页最多 8 张，建议 2×4，不要 20 张一页。

### 3. 编号

视觉标签统一使用 C00/C01/C02 ...

不要让模型在视觉阶段读全局真实 frame id。

程序内部维护映射：

```python
candidate_id -> source_sample_index -> timestamp
```

### 4. 每个边界单独请求

边界 1：Grasp -> Pour

边界 2：Pour -> Put back

必须两个请求。

边界 2 的搜索范围可以从边界 1 之后开始，以减少无关图片。

### 5. Prompt 原则

不要继续增加复杂语言。

核心只说明当前上一阶段动作、下一阶段动作、目标（找下一阶段首次明显开始的图片）、只能返回候选编号。

示例语义：

```text
Find the earliest candidate image where the action has clearly transitioned from Grasp ... to Pour ...
Return only: {"candidate": N}
```

不要一次让模型解释原因。

## 五、Fine 阶段

假设 coarse 判断边界位于约 3.5 s，围绕该时间取局部窗口：

```text
coarse_time - 0.6 s 到 coarse_time + 0.6 s
```

按 0.1 s 抽帧，大约只给模型 10–15 张图。

编号使用 F00 F01 F02 ...

询问：

```text
Which is the earliest image where the new subtask has clearly begun?
```

输出：

```json
{"candidate": 6}
```

程序再转换：F06 -> sampled frame index -> sampled_times[index] -> final start timestamp。

最终仍保持约 0.1 s 时间精度。

## 六、边界搜索范围约束

三个固定子任务顺序已确定，可以利用顺序降低搜索难度。

Boundary 1：subtask 0 -> subtask 1，允许前中段。

Boundary 2：subtask 1 -> subtask 2，起点必须 >= Boundary 1，可裁掉边界 1 之前所有候选。

必须保持 start_0 = 0、start_1 < start_2，保留现有 validator。

## 七、demonstration 的新使用方式

暂时不要把 5 条 demonstration 全部塞给模型。

1. 默认无 demo coarse search
2. 若消融实验证明 demo 有效，最多使用 1 条
3. demo 只用于描述视觉 transition
4. 不附带整条 demonstration 的大量 metadata
5. 每个 boundary 最多一组 before / after 图（各 2 张）
6. 不要再每边界 4 帧、5 条共 40 张示范图

## 八、增加必要日志

当前 GUI 日志没有持久化，无法判断模型到底输出了什么。

为每个 episode 创建 debug 记录，至少保存：

```text
episode id / boundary id / mode(coarse|fine) / sample interval
candidate -> timestamp mapping / image count / demo count
raw model response / parsed candidate / final timestamp / retry count
```

建议保存为 JSONL，例如 `debug/vlm_alignment.jsonl`，每次请求一行。

不要只保存最终 annotation，用于判断模型是否总是选固定位置、解析重试、输出重复等。

## 九、debug contact sheet 输出

增加 debug 选项，正式调用 VLM 前把实际发送的 contact sheet 保存到：

```text
debug/episode_51/
boundary1_coarse_01.jpg / boundary1_fine.jpg ...
```

人工确认图片顺序、标签、分辨率、边界附近状态、candidate 与真实 timestamp 一致。

用于排除 contact sheet 视觉顺序与内部下标不一致的问题。

## 十、暂时不要做的事情

当前阶段不要：

* 更换 VLM / 引入新服务 / 修改 LeRobot GUI
* 增加复杂功能（如示范一致性告警）
* 增加更多 prompt 文字 / 增加更多 demonstration
* 改变固定 3 个子任务的文本、数量或顺序
* 删除当前 validator
* 继续让模型直接输出秒数
* 一次请求同时预测两个边界
* 一次给模型 100+ 张目标帧

尤其不要通过 "carefully inspect / please do not guess / pay close attention" 这类文案解决当前问题。

## 十一、建议代码改动位置

重点检查并修改 `annotation_workbench/guided_alignment.py` 中的：

```text
build_messages() / _demo_boundary_offsets() / _demo_visuals() / run()
```

新增逻辑拆成独立函数，例如：

```python
_build_coarse_candidates()
_build_fine_candidates()
_predict_single_boundary()
_candidate_to_timestamp()
_write_alignment_debug_log()
_save_debug_contact_sheets()
```

不要把 coarse-to-fine 全部堆进 `run()`。

## 十二、验收标准

第一轮不以“跑完全部数据集”为成功标准。

先人工标出 episode 51/52/53 的真实 Boundary 1 / Boundary 2，然后对比旧方案、v2、coarse-to-fine 的：

```text
abs(predicted_time - ground_truth_time)
```

共 6 个 boundary。

## 十三、执行优先级

```text
P0: debug 日志 + contact sheet 落盘 + episode 51 无 demo 消融
P1: 每个 boundary 独立请求 + 8 张/页 + 简化候选编号
P2: coarse(0.5s) + fine(±0.6s, 0.1s)
P3: 51/52/53 人工 ground truth 误差对比
```

P0/P1 没有验证清楚前，不批量重跑 287 条。

## 十四、最终目标

将当前“40 张 demo + 120–190 张目标帧 + 一次预测两个 boundary”改为：

Boundary 1：20–35 张 coarse -> 10–15 张 fine

Boundary 2：20–35 张 coarse -> 10–15 张 fine

每次 VLM 只回答一个问题：

```text
新动作最早在哪一张候选图中开始？
```

这是下一版最重要的设计原则。
