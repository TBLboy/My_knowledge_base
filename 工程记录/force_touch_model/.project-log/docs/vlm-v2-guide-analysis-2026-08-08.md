# VLM V2 精度优先自动标注改造指南分析

日期：2026-08-08
来源：用户转交 `/home/tbl/下载/VLM_LeRobot_v3_精度优先自动标注改造指南.md`
状态：已分析与记录，进入业务逻辑澄清

## 结论

指南的最终方向符合当前产品目标：解决 VLM 自动标注无法可靠识别固定子任务 `start/end` 范围的问题。

推荐采纳其核心架构，但不一次改完：

- 人工 Task Template 冻结 task/subtask 语义；
- VLM 只判断局部时刻处于 before/after/uncertain；
- 程序负责 coarse -> fine -> micro -> verify；
- demo reference 按 boundary 分开；
- 重要结果先写 v2 sidecar，再适配 GUI；
- 未通过确定性质量门的结果进入人工复核。

## 证据和事实

### 与当前代码一致

1. 当前 `guided_alignment.py` 支持固定 subtask 文本，但要求 VLM 一次输出所有 `start_frame`，不符合精度优先目标。
2. 当前 `guided_probe.py` 已实现单 boundary、coarse/fine，但仍要求模型从候选图中选择 `C00/F00`。
3. `vlm_client.py` 存在图文顺序 Bug：先收集全部 text，再 append 全部 image，破坏 demo/target 上下文。
4. `dataset_reader.py` 当前只读取 `episode_index` 和 `timestamp`；真实数据集的 `data/*.parquet` 已包含 `frame_index` 和 `task_index`。
5. 当前 GUI 写 `meta/lerobot_annotations.json`，subtask 只保存 `timestamp` 开始时间，没有显式 `end`/`frame_index`/证据字段。

### 真实数据确认

- `meta/info.json`：LeRobot v3.0，fps=30。
- 当前 Qingdao 数据 subtask 文本为 Grasp / Pour / Put back，指南示例与真实文本一致。
- 当前没有人工 ground truth；51/52/53 只是已有参考边界，不能直接当最终验收。

## 推荐边界

建议按指南的 V2 边界：

- subtask A=[0, B1)
- subtask B=[B1, B2)
- subtask C=[B2, last_frame)
- boundary frame 归属新 subtask

## 实施顺序

先做 P0/P1，不直接跑 51/52/53 VLM 推理：

1. 修 `vlm_client.py` 图文顺序。
2. 新增 Task Template。
3. 扩展 `dataset_reader.py` 读取 frame_index/task_index。
4. 实现 Reference Bank 和 Target Temporal Panel。
5. 人工确认 demo panel 表达真实边界。
6. 再做单 candidate classifier 和 leave-one-out。
7. 通过后才跑 51/52/53。

## 待澄清业务点

- 边界验收标准（demo leave-one-out 门禁、时间误差阈值）。
- 当前 0~4 人工 demo 是否可冻结为人工标准。
- 自动接受和 manual review 的规则。
- task/subtask 是否完全使用 canonical 或保留多描述版本。
- 输出是 sidecar 还是先写现有 annotations。

## 2026-08-08 后续范围更新

用户明确暂停当前 Qingdao 数据集：不再继续现有数据的标定实验。

后续标定测试改用新的数据集，输入和人工标准待用户提供；结果质量由用户评价，不再以当前 51/52/53 参考边界作为验收基准。

上一版分析仍可保留为 V2 架构参考，但重新实施时必须先随新数据集重定义 Task Template、边界 policy 和人工真值。
