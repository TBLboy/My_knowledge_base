# codex skills 最终 delta（TASK-131）

取 main 版后重贴的 codex 客户端差异。每个文件列出 **codex 独有行**（相对 main）。

## `skills/a-architecture-decision/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-business-clarify/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-business-code-align/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-codebase-extraction/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-codebase-onboarding/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-deep-research/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-engineering-landing/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-engineering-spec/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-loop-control/SKILL.md` — 7 行 codex 独有

- compatibility: codex
- Project Goal is the only completion contract. The session-level Goal control surface is Codex's native
- `/goal`; its state is a session control surface and never counts as completion evidence. This Skill must
- not invent or call any other continuation interface. If native Goals are unavailable or disabled,
- continuation falls back to explicit user turns plus the restored `.project-log` state and Handoff.
- VIBE_CONFIG="${CODEX_HOME:-$HOME/.codex}"
- Do not claim automatic continuation, background resumption, or a session Goal binding that the installed Codex version does not provide. When TASK-072 ships a session runner, this section must be updated from the actual 

## `skills/a-operator-distill/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-paper-reading/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-project-context-briefing/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-project-init/scripts/init_project_agents.py` — 4 行 codex 独有

- codex_config = Path(
- os.environ.get("CODEX_HOME")
- or (Path.home() / ".codex")
- candidates.append(codex_config / "vibe-workflow" / "scripts" / "init_project.py")

## `skills/a-project-init/SKILL.md` — 3 行 codex 独有

- compatibility: codex
- 用户要求“初始化项目 / 初始化该项目 / 项目初始化”时使用。子文件夹的 `AGENTS.md` 由 Codex 原生机制读取且优先级更高，本 skill 只维护项目根目录文件，不处理子文件夹。
- VIBE_CONFIG="${CODEX_HOME:-$HOME/.codex}"

## `skills/a-project-log/SKILL.md` — 3 行 codex 独有

- compatibility: codex
- VIBE_CONFIG="${CODEX_HOME:-$HOME/.codex}"
- - Codex 的会话 Goal 由原生 `/goal` 提供，属客户端控制面；Project Goal 与 Loop 状态是唯一权威完成事实，原生 Goal 状态不得作为完成依据。

## `skills/a-project-log-align/scripts/align.py` — 4 行 codex 独有

- os.environ.get("CODEX_HOME")
- or (Path.home() / ".codex")
- os.environ.get("CODEX_HOME")
- or (Path.home() / ".codex")

## `skills/a-project-log-align/SKILL.md` — 2 行 codex 独有

- compatibility: codex
- python3 "${CODEX_HOME:-$HOME/.codex}/skills/a-project-log-align/scripts/align.py" \

## `skills/a-project-log-archive/SKILL.md` — 2 行 codex 独有

- compatibility: codex
- python3 "${CODEX_HOME:-$HOME/.codex}/skills/a-project-log-archive/scripts/archive.py" \

## `skills/a-requirement-baseline/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-retrospective/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-session-handoff/SKILL.md` — 2 行 codex 独有

- compatibility: codex
- 同时运行 `vibe render`（或在 `vibe task handoff --task-id <TASK> --next-action <ACTION>` 后由 `vibe render` 刷新）生成 `.project-log/.state/**/generated/handoff.md`。Handoff 只记录 Project Goal、Task 与 Run 状态；Project Goal 不因会话状态变化而改变。Codex

## `skills/a-skill-evolution/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-solution-research/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-task-decompose/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-verification/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-work-trace/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/a-workflow-update/SKILL.md` — 3 行 codex 独有

- compatibility: codex
- 2. Run `scripts/update_workflow.py --dry-run` against `${CODEX_HOME:-$HOME/.codex}`.
- 5. Confirm the runtime assets and templates exist, then restart Codex to load the update.

## `skills/b-background-task-runner/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/b-concise-communication/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/b-jetson-robot-policy-deployment/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/b-multi-role-ux-audit/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/b-personal-knowledge-distill/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/b-plan-stress-test/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/b-scenario-product-walkthrough/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/b-skill-authoring/SKILL.md` — 4 行 codex 独有

- description: Design and write a focused Codex Skill with clear triggers, progressive disclosure, optional deterministic helpers, and reviewable resource boundaries.
- compatibility: codex
- 3. **Use the Skill as the entry point.** Codex discovers `SKILL.md` directly. Do not require a same-named command file.
- ~/.codex/skills/<a-or-b-kebab-case-name>/

## `skills/b-source-code-tutoring/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/b-web-research-tooling/SKILL.md` — 1 行 codex 独有

- compatibility: codex

## `skills/vibe-subagent-orchestration/SKILL.md` — 21 行 codex 独有

- description: "Dynamically delegate a Vibe Coding lifecycle role to a bounded Codex subagent, preserve main-agent authority, and integrate structured evidence-backed results."
- compatibility: codex
- The Vibe runtime stores role contracts under:
- VIBE_CONFIG="${CODEX_HOME:-$HOME/.codex}"
- VIBE_RUNTIME="${VIBE_RUNTIME:-$VIBE_CONFIG/vibe-workflow}"
- ls "$VIBE_RUNTIME/agents"
- Render the role contract into a bounded prompt and hand the result to the subagent. Put the project
- root, delegated outcome, allowed scope, read/write boundary, required evidence, and stop condition in
- the rendered prompt:
- 
- ```bash
- python3 "$VIBE_RUNTIME/scripts/render_subagent_prompt.py" \
- --role <role> \
- --project-root <project-root> \
- --task "<precise delegated outcome>" \
- --scope "<allowed files/modules or read-only boundary>"
- ```
- 
- The role template and the installed agent configuration enforce the role boundary.
- 4. Use Codex's native subagent facility when available. For multiple agents, parallelize only independent work and use disjoint write scopes.
- 6. If native subagents are unavailable, perform the role serially and label the result `serial-role-fallback`.

## 汇总

- 与 main 逐字节相同：7
- 有 codex 客户端差异：38（其中 27 个仅 `compatibility:` 一行；11 个含额外客户端改写）
- codex 独有文件：0
- main 独有文件：0
- 合计：7 + 38 = 45 个源文件（两树同名集合一致）

### 与 main 逐字节相同的文件

- `skills/a-project-init/templates/general-rules.md`
- `skills/a-project-log/REFERENCE.md`
- `skills/a-project-log-archive/scripts/archive.py`
- `skills/a-project-log-archive/scripts/git_proxy.conf.example`
- `skills/a-project-log-archive/scripts/kb_path.conf.example`
- `skills/b-source-code-tutoring/agents/openai.yaml`
- `skills/b-source-code-tutoring/references/teaching-template.md`
