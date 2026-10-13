# codex 分支 → opencode 主线（main）移植边界基线

由 TASK-128 产出。依据：`git ls-tree` blob 级内容比对（`main` 133 文件 / `origin/codex` 190 文件，同路径 92 个：13 相同、79 不同；main 独有 41；codex 独有 98）。

**两分支无共同祖先**（`git merge-base main origin/codex` 退出码 1），因此只能内容级移植。

## 归属类别

| 类别 | 含义 | 文件数 |
|---|---|---|
| 替换 | 直接取 main 版（codex 无客户端差异） | 24 |
| 适配 | 取 main 版 + 重贴 codex 客户端差异（人工改写，需留 delta 说明） | 56 |
| 新增 | main 独有且客户端无关，新增到 codex | 12 |
| 保留并适配 | codex 独有交付面，保留并适配到新核心 | 32 |
| 删除 | codex 独有但 main 已退役，删除 | 66 |
| 不引入 | main 独有但属 OpenCode 客户端面，codex 用自身对应物 | 28 |
| 相同 | 逐字节相同 | 13 |

## 替换（24）

| 路径 | 来源 | 说明 |
|---|---|---|
| `.gitattributes` | 同路径不同 | 直接取 main 版 |
| `runtime/project-log-template/current-session.md` | 同路径不同 | 直接取 main 版 |
| `runtime/project-log-template/progress.md` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/framework_info.py` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/init_project.py` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/state_context.py` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/state_evidence.py` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/state_ledger.py` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/state_replay.py` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/state_store.py` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/state_views.py` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/validate_project.py` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/vibe.py` | 同路径不同 | 直接取 main 版 |
| `runtime/scripts/workflow_state.py` | 同路径不同 | 直接取 main 版 |
| `tests/test_align_skill.py` | 同路径不同 | 直接取 main 版 |
| `tests/test_archive_skill.py` | 同路径不同 | 直接取 main 版 |
| `tests/test_ledger_first.py` | 同路径不同 | 直接取 main 版 |
| `tests/test_ledger_recovery.py` | 同路径不同 | 直接取 main 版 |
| `tests/test_project_init.py` | 同路径不同 | 直接取 main 版 |
| `tests/test_project_log_init.py` | 同路径不同 | 直接取 main 版 |
| `tests/test_project_templates.py` | 同路径不同 | 直接取 main 版 |
| `tests/test_state_gates.py` | 同路径不同 | 直接取 main 版 |
| `tests/test_state_ledger.py` | 同路径不同 | 直接取 main 版 |
| `tests/test_state_replay.py` | 同路径不同 | 直接取 main 版 |

## 适配（56）

| 路径 | 来源 | 说明 |
|---|---|---|
| `.github/workflows/tests.yml` | main 独有 | CI 工作流需改跑 codex 分支的套件与安装面 |
| `AI_INSTALL.md` | 同路径不同 | codex 安装指南（CODEX_HOME/global_installer） |
| `AI_UPGRADE.md` | 同路径不同 | codex 升级指南 |
| `README.md` | 同路径不同 | codex 客户端措辞 + main 的结构改进 |
| `docs/RELEASE-NOTES.md` | 同路径不同 | codex 版本说明（0.6.0 对齐） |
| `docs/USAGE.md` | 同路径不同 | codex 用法（含 main 新增的 history/reopen/workspace/verification 面） |
| `runtime/scripts/validate_package.py` | 同路径不同 | 采用 main 的必需项整理，但必须重新加回 codex 资产校验（hooks/agents/mcp/plugin/marketplace/prompts/installer）并去掉 REQUIRED_OPENCODE |
| `runtime/scripts/vibe_python.ps1` | 同路径不同 | 同上（参数歧义检查） |
| `runtime/vibe.ps1` | 同路径不同 | 同上（Windows） |
| `runtime/vibe.sh` | 同路径不同 | 启动器：采用 main 的“从安装位置推断 config home + 无静默回退”，但变量名保持 CODEX_HOME/--codex-home |
| `scripts/bootstrap_vibe_python.py` | 同路径不同 | 采用 main 的 UTF-8 流强制与措辞，命名保持 codex_home/--codex-home |
| `skills/a-architecture-decision/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-business-clarify/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-business-code-align/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-codebase-extraction/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-codebase-onboarding/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-deep-research/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-engineering-landing/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-engineering-spec/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-loop-control/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-operator-distill/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-paper-reading/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-project-context-briefing/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-project-init/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-project-init/scripts/init_project_agents.py` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-project-init/templates/general-rules.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-project-log-align/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-project-log-align/scripts/align.py` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-project-log-archive/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-project-log-archive/scripts/archive.py` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-project-log/REFERENCE.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-project-log/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-requirement-baseline/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-retrospective/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-session-handoff/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-skill-evolution/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-solution-research/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-task-decompose/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-verification/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-work-trace/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/a-workflow-update/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/b-background-task-runner/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/b-concise-communication/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/b-jetson-robot-policy-deployment/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/b-multi-role-ux-audit/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/b-personal-knowledge-distill/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/b-plan-stress-test/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/b-scenario-product-walkthrough/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/b-skill-authoring/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/b-source-code-tutoring/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/b-web-research-tooling/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `skills/vibe-subagent-orchestration/SKILL.md` | 同路径不同 | 取 main 版 + 重贴 codex 客户端措辞（compatibility/CODEX_HOME/Codex 原生 /goal/子代理渲染） |
| `tests/test_command_surface.py` | 同路径不同 | CLI 面断言（新子命令集） |
| `tests/test_cross_platform_surface.py` | 同路径不同 | 启动器/解释器面断言（CODEX_HOME 命名） |
| `tests/test_docs_consistency.py` | 同路径不同 | 断言对象换成 codex 面（保留路径、无 .opencode 死链） |
| `tests/test_release_surface.py` | 同路径不同 | codex 发布面断言 |

## 新增（12）

| 路径 | 来源 | 说明 |
|---|---|---|
| `docs/TERMINOLOGY.md` | main 独有 | 术语契约（TASK-089），客户端无关 |
| `docs/V3-PR-00-BASELINE.md` | main 独有 | V3 PR-00 基线冻结（框架自身门禁的验收基线） |
| `runtime/scripts/verification_runner.py` | main 独有 | 受信验证动作注册表（TASK-085/TASK-102），客户端无关的核心能力 |
| `skills/a-project-log-archive/scripts/git_proxy.conf.example` | main 独有 | 归档 git 代理配置样例 |
| `tests/_platform.py` | main 独有 | 跨平台测试辅助 |
| `tests/test_bootstrap_python.py` | main 独有 | 解释器引导测试（原 codex test_installer 的共享部分） |
| `tests/test_session_recovery.py` | main 独有 | 会话恢复（按 generation）测试 |
| `tests/test_skill_cli_contract.py` | main 独有 | skill CLI 契约测试 |
| `tests/test_task_reopen.py` | main 独有 | 任务重开（新 attempt）测试 |
| `tests/test_upgrade_recovery.py` | main 独有 | 升级恢复测试 |
| `tests/test_verification_runner.py` | main 独有 | 验证运行器测试 |
| `tests/test_workspace_clear.py` | main 独有 | 工作区清理测试 |

## 保留并适配（32）

| 路径 | 来源 | 说明 |
|---|---|---|
| `.agents/plugins/marketplace.json` | codex 独有 | codex 本地 marketplace 定义 |
| `build_release.py` | codex 独有 | codex release ZIP 构建 |
| `cc-switch-common-config-codex.txt` | codex 独有 | cc-switch 公共配置模板 |
| `install.ps1` | codex 独有 | 同上（Windows） |
| `install.sh` | codex 独有 | codex 安装入口（CODEX_HOME） |
| `plugins/vibe-toolbelt/.codex-plugin/plugin.json` | codex 独有 | codex 交付面资产 |
| `plugins/vibe-toolbelt/.mcp.json` | codex 独有 | codex 交付面资产 |
| `prompts/vibe-global-agent.md` | codex 独有 | codex 全局提示词 |
| `runtime/agents/README.md` | codex 独有 | codex 交付面资产 |
| `runtime/agents/alignment-reviewer.md` | codex 独有 | codex 交付面资产 |
| `runtime/agents/business-analyst.md` | codex 独有 | codex 交付面资产 |
| `runtime/agents/codebase-onboarder.md` | codex 独有 | codex 交付面资产 |
| `runtime/agents/implementation-builder.md` | codex 独有 | codex 交付面资产 |
| `runtime/agents/paper-reader.md` | codex 独有 | codex 交付面资产 |
| `runtime/agents/roles.json` | codex 独有 | codex 交付面资产 |
| `runtime/agents/solution-researcher.md` | codex 独有 | codex 交付面资产 |
| `runtime/agents/verification-reviewer.md` | codex 独有 | codex 交付面资产 |
| `runtime/agents/workflow-distiller.md` | codex 独有 | codex 交付面资产 |
| `runtime/hooks/hook_common.py` | codex 独有 | codex 交付面资产 |
| `runtime/hooks/post_tool_use.py` | codex 独有 | codex 交付面资产 |
| `runtime/hooks/pre_compact.py` | codex 独有 | codex 交付面资产 |
| `runtime/hooks/session_start.py` | codex 独有 | codex 交付面资产 |
| `runtime/mcp/optional-mcps.json` | codex 独有 | codex 交付面资产 |
| `runtime/scripts/render_subagent_prompt.py` | codex 独有 | codex 子代理提示渲染（codex 无原生 task 工具） |
| `scripts/generate_cc_switch_config.py` | codex 独有 | 按宿主机生成 cc-switch 配置 |
| `scripts/global_installer.py` | codex 独有 | codex 全局安装器（hooks/MCP/plugin/marketplace/verify） |
| `tests/test_installer.py` | codex 独有 | codex 安装器测试（保留并适配新核心） |
| `tests/test_transactional_hooks.py` | codex 独有 | codex 事务性 hooks 测试（保留并适配新核心） |
| `uninstall.ps1` | codex 独有 | 同上（Windows） |
| `uninstall.sh` | codex 独有 | codex 卸载入口 |
| `update.ps1` | codex 独有 | 同上（Windows） |
| `update.sh` | codex 独有 | codex 更新入口 |

## 删除（66）

| 路径 | 来源 | 说明 |
|---|---|---|
| `runtime/project-log-template/alignment/findings.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/architecture/architecture.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/business-logic/atoms.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/business-logic/clarification.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/business-logic/open-questions.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/business-logic/open-questions.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/decisions/decision-log.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/distill-input/candidate-insights.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/distillation/candidates.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/distillation/proposals/.gitkeep` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/docs/atomic-business-logic.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/docs/decision-authority.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/docs/lifecycle.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/docs/plugin-behavior.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/docs/skill-routing.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/docs/task-planning.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/evals/.gitkeep` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/goals/active-goal.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/loop/active-run.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/loop/events.jsonl` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/loop/evidence-index.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/loop/handoff.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/requirements.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/requirements/baseline.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/research/papers/.gitkeep` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/research/solution-research.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/retrospective/retrospective.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/alignment.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/architecture.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/business-clarification.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/business-logic.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/decision-log.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/distillation.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/loop-active-run.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/loop-evidence-index.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/open-questions.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/project-goal.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/requirement-baseline.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/retrospective.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/solution-research.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/task-list.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/verification-evidence.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/work-trace.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/schemas/workflow.schema.json` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/specs/.gitkeep` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/tasks/task-list.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/tasks/task-list.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/templates/alignment-finding.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/templates/architecture.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/templates/business-logic-atom.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/templates/decision.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/templates/engineering-spec.md` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/templates/open-question.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/templates/requirement-baseline.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/templates/solution-research.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/templates/task.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/templates/work-trace.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/verification/evidence.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/work-trace/trace.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/project-log-template/workflow.yaml` | codex 独有 | format 1 模板随 format 1 退役（main 只保留 current-session/progress/docs-archive） |
| `runtime/scripts/loop_state.py` | codex 独有 | 被新核心 workflow_state.py + vibe 子命令取代（main 已删） |
| `runtime/scripts/loopctl.py` | codex 独有 | 同上；main 用 vibe CLI 取代 loopctl 命令面 |
| `runtime/scripts/state_exchange.py` | codex 独有 | exchange 面退役（TASK-093） |
| `runtime/scripts/state_migrate.py` | codex 独有 | format 1 迁移器随 format 1 退役（TASK-092） |
| `tests/test_loop_core.py` | codex 独有 | loop_state/loopctl 的测试，随模块退役 |
| `tests/test_migration_apply.py` | codex 独有 | format 1 迁移的测试，随迁移器退役 |

## 不引入（28）

| 路径 | 来源 | 说明 |
|---|---|---|
| `docs/OPENCODE-SEED.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/.gitignore` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/AGENTS.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/README.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/agents/alignment-reviewer.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/agents/business-analyst.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/agents/codebase-onboarder.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/agents/implementation-builder.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/agents/paper-reader.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/agents/solution-researcher.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/agents/verification-reviewer.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/agents/vibe-main.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/agents/workflow-distiller.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/bin/vibe-python` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/commands/vibe-implement.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/commands/vibe-plan.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/commands/vibe-resume.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/commands/vibe-retro.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/commands/vibe-start.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/commands/vibe-status.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/commands/vibe-verify.md` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/install.sh` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/opencode.json` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `runtime/opencode/plugins/vibe-workflow.ts` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `scripts/opencode_installer.py` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `tests/test_opencode_installer.py` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `tests/test_opencode_plugin.py` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |
| `tests/test_opencode_surface.py` | main 独有 | OpenCode 客户端面；codex 有自身对应物（另行适配） |

## 相同（13）

| 路径 | 来源 | 说明 |
|---|---|---|
| `.gitignore` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `docs/EXTRACTION.md` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `runtime/project-log-template/docs/archive/README.md` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `runtime/scripts/requirements.txt` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `runtime/scripts/state_gate.py` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `runtime/scripts/state_routing.py` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `runtime/scripts/validate_workflow.py` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `runtime/scripts/vibe_python.sh` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `skills/a-project-log-archive/scripts/kb_path.conf.example` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `skills/b-source-code-tutoring/agents/openai.yaml` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `skills/b-source-code-tutoring/references/teaching-template.md` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `tests/test_state_records.py` | 同路径相同 | 两分支逐字节相同，无需处理 |
| `tests/test_validate_format2.py` | 同路径相同 | 两分支逐字节相同，无需处理 |

## 已知的必须适配点（交付面硬依赖）

- `runtime/hooks/hook_common.py`、`runtime/hooks/post_tool_use.py` → `from loop_state import ...`（模块将被删除）
- `prompts/vibe-global-agent.md` → `loopctl.py restore` / `goal-bind` / `evaluate goal`、`render_subagent_prompt.py`
- `runtime/scripts/validate_package.py` → 必须重新加回 codex 资产校验并去掉 `REQUIRED_OPENCODE`
- `runtime/vibe.sh|ps1`、`scripts/bootstrap_vibe_python.py` → 采用 main 的推断/强制逻辑但保持 `CODEX_HOME` 命名
- 已装 `~/.codex/config.toml` 的 `[marketplaces.vibe-global-toolbox] source` 指向项目根（应为仓库根），现状已坏，需在 TASK-133 修复
