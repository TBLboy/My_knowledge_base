# Reusable Patterns

## Pattern: project-log-initialization

- Scope: workflow
- Status: provisional
- Rule: 新项目开始时，先初始化 `.project-log/` 记录系统，将所有未知项显式标记为待补充，避免 AI 猜测项目信息。
- When to use: 启动任何需要 AI 辅助的新工程时。
- When not to use: 已有完善工程记录系统的项目。
- Evidence refs:
  - `.project-log/progress.md`
- Notes: 尚未在此项目中验证其实际效果，需要在后续开发中检验。
