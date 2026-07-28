# Branch: skill-architecture-v1

## Status

- draft

## Purpose

- 在已存在的 Skills、项目日志和个人知识库基础上，形成一个低维护、可验证、服务于机器人职业成长的 AI 工作架构。

## Start Node

- P1: Evidence And Constraints Collected

## Target Node

- P2: Work Mode Selected

## Logic Path

```text
P1
 -> 盘点当前 Skills、Agent、知识库、项目记录与真实工作任务
 -> 识别重叠、缺口和高摩擦环节
 -> 设计最小角色层与信息流
 -> 选定一个真实任务试运行
 -> P2
```

## Assumptions

- 现有 Skills 已覆盖 project-log、知识蒸馏、调研、上下文交接和代码复盘等主要环节。
- 系统价值来自更好的任务选择、上下文质量、验证和复利，而非 Skill 数量。

## Risks

- 设计过于宏大，无法在秋招前或日常实习中产生实际收益。
- 多个记录系统之间产生重复、冲突或无人维护的文档。
- 过度依赖 AI 生成而忽略真实代码、数据和实机证据。

## Open Questions

- 当前最痛的工作断点是什么？
- 当前个人知识库的实际使用频率、检索效果和维护成本如何？
- 先做统一入口、研究工作流、工程交付闭环，还是秋招学习/面试闭环？

## Verification Plan

- 选取一个真实、在两周内可完成的机器人学习/工程任务。
- 对比引入架构前后的启动时间、上下文遗漏、返工次数、验证覆盖和可复用记录质量。
- 若无法带来可观察改进，缩小或废弃对应组件。

## Merge Condition

- 本人确认优先痛点和工具边界。
- 最小架构在真实任务中试运行并留下可复查证据。
