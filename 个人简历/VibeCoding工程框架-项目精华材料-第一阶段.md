# Vibe Coding 工程框架项目精华材料（第一阶段）

- **项目状态：**第一阶段精华材料，非最终简历文案
- **用户确认身份：**个人经验凝练产物
- **主要来源：**
  - `工程记录/vibe-coding/.project-log/current-session.md`
  - `工程记录/vibe-coding/.project-log/business-logic/main.md`
  - `工程记录/vibe-coding/.project-log/requirements.md`
  - `工程记录/vibe-coding/.project-log/progress.md`
  - `工程记录/人物画像/.project-log/business-logic/main.md`
  - `工程记录/人物画像/.project-log/business-logic/constraints.md`

## 1. 项目定位

将个人在机器人、数据平台、模型训练和软件开发中的实践经验，凝练为一套可运行、可恢复、可验证的 AI 辅助工程工作框架。

框架解决的问题不是“让 AI 生成更多代码”，而是让 AI 辅助开发具备：

- 明确目标和业务逻辑。
- 可追溯的需求、架构、任务和决策。
- 可验证的实现与证据。
- 失败归因和有变化的重试。
- 会话恢复和长期项目记忆。
- 经验复盘、知识蒸馏和持续改进。

## 2. 用户负责范围

作为个人经验凝练产物，用户负责：

- 设计整体生命周期和项目记忆边界。
- 设计 `.project-log` 项目事实记录体系。
- 设计 Loop Core、Goal、Run、证据索引和完成裁决机制。
- 设计 Skills/Agent 路由和不同工程角色契约。
- 实现 Hooks、MCP 配置、安装器、归档脚本和验证工具。
- 处理 Windows/Linux、UTF-8、代理、路径、安装布局和插件兼容问题。
- 通过单元测试、包校验、安装验证和 smoke test 迭代框架。

## 3. 生命周期模型

```text
business-intent
 → business-clarification
 → requirement-baseline
 → solution-research
 → architecture-decision
 → task-decomposition
 → engineering-spec
 → implementation
 → verification
 → alignment
 → retrospective
 → distillation
```

核心思想：

- 业务逻辑先于代码。
- 代码、配置和测试是实现与证据，不自动等于需求。
- 未验证的实现不能声称完成。
- 失败需要归因到实现、规格、任务拆解、技术选型、环境或验证工具。
- 重试必须记录可证伪假设、变化量和预期证据。
- Project Log 记录项目事实，个人知识库只保留抽象后的可复用规则。

## 4. 核心模块

### 4.1 Project Log

记录：

- 业务原子逻辑。
- 需求基线。
- 架构和技术决策。
- 任务清单。
- 验证证据。
- 业务/代码/测试对齐问题。
- 工作轨迹、复盘和知识候选。
- 当前会话和精确下一步。

### 4.2 Loop Core

管理：

- active goal / task / phase。
- Run 状态和事件历史。
- 证据有效性、失效和 superseded。
- retry contract。
- 失败计数和循环上限。
- Goal 同步和完成前评估。
- handoff 与恢复视图。

### 4.3 Skills 与动态角色路由

根据任务类型选择：

- 业务澄清。
- 解决方案研究。
- 架构决策。
- 工程实施。
- 验证审查。
- 业务/代码对齐。
- 项目日志维护。
- 复盘和知识蒸馏。

并明确主 Agent、子 Agent、实现者和验证者的职责边界。

### 4.4 Hooks / MCP / Installer

- SessionStart：恢复项目状态并提供上下文。
- PostToolUse：保持项目记录和验证状态同步。
- PreCompact：在上下文压缩前生成恢复信息。
- MCP：接入代码图谱、文档加载和其他工具。
- Installer：安装、更新、校验、回滚和全局运行时同步。
- Archive：将项目日志归档到知识库，避免污染其他项目。

## 5. 关键工程问题与解决方向

| 问题 | 解决方向 |
| --- | --- |
| AI 会话结束后项目状态丢失 | current-session、handoff 和 Loop 状态快照 |
| AI 把猜测写成事实 | 业务逻辑、需求、实现和证据分层 |
| 验证失败后盲目重复执行 | 失败归因、可证伪假设、delta 和 expected evidence |
| 项目日志逐渐漂移 | validate_project、Loop validate 和证据索引 |
| Windows/Linux 路径和编码不一致 | UTF-8 流、动态路径、环境降级显式报告 |
| 插件/Hook/MCP 安装失败难恢复 | Installer backup、校验、回滚和 smoke test |
| 归档脚本误收集其他项目文件 | 收窄 git add 范围并记录归档边界 |
| AI 直接修改项目业务逻辑 | A/B/C 决策权限和用户 C 级问题确认 |

## 6. 记录中的验证与结果

- 已完成框架核心安装和 `global_installer.py verify`。
- Loop/Hook 测试、安装器测试和包校验多次通过。
- 修复过 SessionStart/PreCompact Hook JSON 协议、UTF-8、Windows 权限和异常退出问题。
- 处理过 MCP stderr 非 UTF-8、代理、固定版本、动态宿主路径和安装布局问题。
- 完成 `a-project-init`、项目归档、全局 Skill 同步和安装布局 smoke test。
- 当前框架已服务于个人知识库、机器人项目、数据平台和模型训练项目。

## 7. 可用于简历的价值标签

- AI Agent 工程工作流
- LLM-assisted software engineering
- Project memory / state recovery
- Workflow orchestration
- Skill/Agent routing
- Evidence-driven verification
- CLI / installer / hooks / MCP
- 跨平台开发工具链
- 工程知识管理
- 可恢复自动化

## 8. 第一版简历表达方向（非最终文案）

### 稳健版方向

> 基于机器人和 AI 工程实践，独立设计并实现 Vibe Coding 工程框架，将业务澄清、需求基线、架构设计、任务执行、验证、复盘和知识蒸馏纳入可恢复工作流；构建 Project Log、Loop Core、Hooks、Skills、MCP 和安装归档工具，支持跨项目状态恢复与证据化交付。

### 强表达版方向

> 独立构建面向 AI 辅助软件工程的可验证工作流框架，设计 Project Log/Loop Core 状态与证据系统，完善 Skills/Agent 路由、SessionStart/PreCompact Hooks、MCP 配置、安装器和项目归档链路；通过失败归因、重试契约和完成前评估，将 AI 代码生成升级为可追溯、可恢复的工程交付流程。

## 9. 应届生简历使用建议

- 若投递具身智能/机器人算法岗位，可将其作为“个人工程方法论/工具链”补充项目，不抢主项目篇幅。
- 若投递 AI Agent、平台工程、开发者工具或软件工程岗位，可将其提升为核心个人项目。
- 应避免写成“发明通用 AI 开发框架”或“解决所有 AI 研发问题”，应限定为个人工程实践框架。

## 10. 待用户补充的信息

1. 框架实际代码规模、文件数量、测试数量和使用项目数。
2. 是否有 GitHub/内部仓库或可公开演示的版本。
3. 框架为个人长期维护还是实习期间开发。
4. 具体解决过哪些真实项目问题，节省了多少时间或减少了多少返工。
5. 是否希望在机器人简历中保留该项目，还是另做 AI Agent/软件工程版本。
