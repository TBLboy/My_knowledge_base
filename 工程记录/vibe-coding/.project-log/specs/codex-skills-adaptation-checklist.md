# codex skills 适配清单（TASK-131）

对每个「同路径但内容不同」的 skills 文件，列出 **codex 独有行**（取 main 版后会丢失的行）。
每条需判定：`重贴`（仍是正确的 codex 客户端措辞）/ `改写`（引用了已退役接口，需换成新核心的等价物）/ `弃用`（已无意义）。

## `skills/a-architecture-decision/SKILL.md`  (1 行 codex 独有)

- `skills/a-architecture-decision/SKILL.md:5`  compatibility: codex

## `skills/a-business-clarify/SKILL.md`  (9 行 codex 独有)

- `skills/a-business-clarify/SKILL.md:5`  compatibility: codex
- `skills/a-business-clarify/SKILL.md:24`  2. `.project-log/requirements.md` and `.project-log/requirements/baseline.yaml`.
- `skills/a-business-clarify/SKILL.md:25`  3. `.project-log/business-logic/atoms.yaml` and `open-questions.yaml`.
- `skills/a-business-clarify/SKILL.md:27`  5. `.project-log/docs/decision-authority.md`.
- `skills/a-business-clarify/SKILL.md:158`  Update:
- `skills/a-business-clarify/SKILL.md:160`  - `.project-log/business-logic/atoms.yaml`;
- `skills/a-business-clarify/SKILL.md:161`  - `.project-log/business-logic/clarification.yaml`;
- `skills/a-business-clarify/SKILL.md:162`  - `.project-log/business-logic/open-questions.yaml`;
- `skills/a-business-clarify/SKILL.md:164`  - `.project-log/tasks/task-list.yaml` for follow-up work;

## `skills/a-business-code-align/SKILL.md`  (1 行 codex 独有)

- `skills/a-business-code-align/SKILL.md:5`  compatibility: codex

## `skills/a-codebase-extraction/SKILL.md`  (1 行 codex 独有)

- `skills/a-codebase-extraction/SKILL.md:5`  compatibility: codex

## `skills/a-codebase-onboarding/SKILL.md`  (1 行 codex 独有)

- `skills/a-codebase-onboarding/SKILL.md:5`  compatibility: codex

## `skills/a-deep-research/SKILL.md`  (1 行 codex 独有)

- `skills/a-deep-research/SKILL.md:5`  compatibility: codex

## `skills/a-engineering-landing/SKILL.md`  (1 行 codex 独有)

- `skills/a-engineering-landing/SKILL.md:5`  compatibility: codex

## `skills/a-engineering-spec/SKILL.md`  (1 行 codex 独有)

- `skills/a-engineering-spec/SKILL.md:5`  compatibility: codex

## `skills/a-loop-control/SKILL.md`  (17 行 codex 独有)

- `skills/a-loop-control/SKILL.md:3`  description: Control a bounded Vibe work loop through durable state restoration, evidence validity, failure attribution, retry contracts, native Codex Goal synchronization, completion evaluation, and handoff.
- `skills/a-loop-control/SKILL.md:5`  compatibility: codex
- `skills/a-loop-control/SKILL.md:15`  Use the installed `loopctl` runtime as the single deterministic controller for Project Goal state, evidence validity, failure attribution, retry limits, native Goal synchronization, and Handoff.
- `skills/a-loop-control/SKILL.md:17`  Codex's native `/goal` is the only thread execution and continuation controller. This Skill must not create a second continuation loop.
- `skills/a-loop-control/SKILL.md:24`  VIBE_RUNTIME="${CODEX_HOME:-$HOME/.codex}/vibe-workflow"
- `skills/a-loop-control/SKILL.md:25`  python3 "$VIBE_RUNTIME/scripts/loopctl.py" --root <project-root> --json restore
- `skills/a-loop-control/SKILL.md:27`  
- `skills/a-loop-control/SKILL.md:28`  On Windows use `py -3`.
- `skills/a-loop-control/SKILL.md:32`  ## Native Goal Bridge
- `skills/a-loop-control/SKILL.md:34`  Generate the objective to bind through Codex's native `/goal`:
- `skills/a-loop-control/SKILL.md:36`  ```bash
- `skills/a-loop-control/SKILL.md:37`  python3 "$VIBE_RUNTIME/scripts/loopctl.py" --root <project-root> --json goal-bind
- `skills/a-loop-control/SKILL.md:38`  ```
- `skills/a-loop-control/SKILL.md:39`  
- `skills/a-loop-control/SKILL.md:40`  Synchronize observed native Goal state with `goal-sync`. Native Goal completion only triggers Project Goal evaluation; it does not bypass required evidence.
- `skills/a-loop-control/SKILL.md:78`  Register evidence with `record-evidence`. Any covered code, config, dependency, requirement, or verification-harness change makes the evidence `stale`; never delete it to hide invalidation.
- `skills/a-loop-control/SKILL.md:85`  python3 "$VIBE_RUNTIME/scripts/loopctl.py" --root <project-root> --json evaluate goal

## `skills/a-operator-distill/SKILL.md`  (1 行 codex 独有)

- `skills/a-operator-distill/SKILL.md:5`  compatibility: codex

## `skills/a-paper-reading/SKILL.md`  (1 行 codex 独有)

- `skills/a-paper-reading/SKILL.md:5`  compatibility: codex

## `skills/a-project-context-briefing/SKILL.md`  (1 行 codex 独有)

- `skills/a-project-context-briefing/SKILL.md:5`  compatibility: codex

## `skills/a-project-init/SKILL.md`  (9 行 codex 独有)

- `skills/a-project-init/SKILL.md:5`  compatibility: codex
- `skills/a-project-init/SKILL.md:22`  用户要求“初始化项目 / 初始化该项目 / 项目初始化”时使用。子文件夹的 `AGENTS.md` 由 Codex 原生机制读取且优先级更高，本 skill 只维护项目根目录文件，不处理子文件夹。
- `skills/a-project-init/SKILL.md:33`  VIBE_RUNTIME="${CODEX_HOME:-$HOME/.codex}/vibe-workflow"
- `skills/a-project-init/SKILL.md:34`  python3 "$VIBE_RUNTIME/scripts/init_project_agents.py" \
- `skills/a-project-init/SKILL.md:41`  5. 记录仓库类型（个人/团队协作）到根目录 `AGENTS.md`，并报告结果：`.project-log` 与 `AGENTS.md` 的状态（created / injected / skipped）、仓库类型、项目级规则是否留空。
- `skills/a-project-init/SKILL.md:47`  - 文件中已存在 `<!-- VIBE-PROJECT-GENERAL:BEGIN -->`：跳过注入，不重复叠加（幂等）。
- `skills/a-project-init/SKILL.md:50`  - 脚本返回 `injected` / `skipped`（文件已存在）时，由 Agent 在“项目级规则”区末尾追加或更新该行；已存在则不重复。
- `skills/a-project-init/SKILL.md:51`  - 已注入的项目不会自动跟随模板更新；修改模板后，对未注入或新建项目生效，已注入项目由用户决定是否手动同步。
- `skills/a-project-init/SKILL.md:56`  - 本 skill 不修改 `.project-log` 创建逻辑，只编排与调用；新建项目默认生成 format 2，存量旧格式通过 `vibe migrate` 显式迁移。

## `skills/a-project-init/scripts/init_project_agents.py`  (4 行 codex 独有)

- `skills/a-project-init/scripts/init_project_agents.py:21`  candidates.append(Path.home() / ".codex" / "vibe-workflow" / "scripts" / "init_project.py")
- `skills/a-project-init/scripts/init_project_agents.py:53`  content = path.read_text(encoding="utf-8")
- `skills/a-project-init/scripts/init_project_agents.py:55`  return "skipped"
- `skills/a-project-init/scripts/init_project_agents.py:62`  path.write_text(new_content, encoding="utf-8")

## `skills/a-project-init/templates/general-rules.md`  (0 行 codex 独有)


## `skills/a-project-log-align/SKILL.md`  (2 行 codex 独有)

- `skills/a-project-log-align/SKILL.md:5`  compatibility: codex
- `skills/a-project-log-align/SKILL.md:54`  python3 ~/.codex/skills/a-project-log-align/scripts/align.py \

## `skills/a-project-log-align/scripts/align.py`  (3 行 codex 独有)

- `skills/a-project-log-align/scripts/align.py:181`  configured = Path.home() / ".codex" / "vibe-python"
- `skills/a-project-log-align/scripts/align.py:193`  codex_home = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
- `skills/a-project-log-align/scripts/align.py:194`  return codex_home / "vibe-workflow"

## `skills/a-project-log-archive/SKILL.md`  (12 行 codex 独有)

- `skills/a-project-log-archive/SKILL.md:3`  description: Archive the current project's .project-log to the centralized knowledge base for later analysis. Use when the user wants to save progress, archive records, or sync project logs.
- `skills/a-project-log-archive/SKILL.md:5`  compatibility: codex
- `skills/a-project-log-archive/SKILL.md:13`  Archive the current project's `.project-log/` into the knowledge base and push the knowledge base to remote.
- `skills/a-project-log-archive/SKILL.md:38`  7. Stage only `工程记录/<project-name>`, verify the staged ledger is byte-identical to the
- `skills/a-project-log-archive/SKILL.md:42`  8. Fail loudly instead of reporting `no-changes` whenever either blob differs from the
- `skills/a-project-log-archive/SKILL.md:47`  9. Fail unless **every** push URL of that remote reports the archived revision after the
- `skills/a-project-log-archive/SKILL.md:48`  push, so a remote hook that rewrites or rejects the ref cannot be mistaken for a
- `skills/a-project-log-archive/SKILL.md:49`  successful archive.
- `skills/a-project-log-archive/SKILL.md:56`  python3 ~/.codex/skills/a-project-log-archive/scripts/archive.py \
- `skills/a-project-log-archive/SKILL.md:67`  - Refuses when the KB `.gitignore` excludes the archived ledger, and prints the matching
- `skills/a-project-log-archive/SKILL.md:68`  rule plus the negation lines to add, so a globally ignored `.project-log/` can never
- `skills/a-project-log-archive/SKILL.md:69`  turn into a silent no-op.

## `skills/a-project-log-archive/scripts/archive.py`  (41 行 codex 独有)

- `skills/a-project-log-archive/scripts/archive.py:174`  """Return the .gitignore rule that excludes ``relative``, or None when it is tracked.
- `skills/a-project-log-archive/scripts/archive.py:176`  ``git check-ignore`` reports a path as ignored even when it is already tracked, so
- `skills/a-project-log-archive/scripts/archive.py:177`  tracking status is checked first: a tracked file reaches the remote regardless of
- `skills/a-project-log-archive/scripts/archive.py:178`  ignore rules, and only genuinely unreachable paths are reported.
- `skills/a-project-log-archive/scripts/archive.py:180`  tracked = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:193`  probe = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:194`  ["git", "-C", str(kb_root), "check-ignore", "-v", "--", relative],
- `skills/a-project-log-archive/scripts/archive.py:197`  if probe.returncode == 1:
- `skills/a-project-log-archive/scripts/archive.py:199`  if probe.returncode != 0:
- `skills/a-project-log-archive/scripts/archive.py:204`  f"{probe.stderr.strip() or 'git check-ignore failed'}"
- `skills/a-project-log-archive/scripts/archive.py:215`  probe = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:226`  probe = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:236`  probe = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:256`  probe = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:286`  return Path(unquote(parsed.path))
- `skills/a-project-log-archive/scripts/archive.py:287`  if parsed.scheme:
- `skills/a-project-log-archive/scripts/archive.py:291`  try:
- `skills/a-project-log-archive/scripts/archive.py:292`  return Path(target).expanduser()
- `skills/a-project-log-archive/scripts/archive.py:293`  except RuntimeError as error:
- `skills/a-project-log-archive/scripts/archive.py:294`  raise ArchiveError(
- `skills/a-project-log-archive/scripts/archive.py:295`  f"the archive target {target!r} starts with '~' but the home directory it "
- `skills/a-project-log-archive/scripts/archive.py:296`  "names cannot be resolved, so the archive cannot prove it is not the "
- `skills/a-project-log-archive/scripts/archive.py:297`  "knowledge base itself; refusing to run. Use an absolute path instead."
- `skills/a-project-log-archive/scripts/archive.py:298`  ) from error
- `skills/a-project-log-archive/scripts/archive.py:344`  if identity is not None and own is not None and identity == own:
- `skills/a-project-log-archive/scripts/archive.py:354`  probe = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:380`  branch = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:408`  probe = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:424`  pushed = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:431`  f"git push {remote} {commit[:12]}:{remote_ref} failed: {detail}"
- `skills/a-project-log-archive/scripts/archive.py:466`  relative = str(Path("工程记录") / project_name)
- `skills/a-project-log-archive/scripts/archive.py:467`  ledger_relative = str(Path("工程记录") / project_name / ".project-log" / LEDGER_RELATIVE)
- `skills/a-project-log-archive/scripts/archive.py:475`  f"  !{Path('工程记录') / project_name}/.project-log/\n"
- `skills/a-project-log-archive/scripts/archive.py:476`  f"  !{Path('工程记录') / project_name}/.project-log/**\n"
- `skills/a-project-log-archive/scripts/archive.py:479`  completed = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:509`  pending = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:535`  committed = subprocess.run(
- `skills/a-project-log-archive/scripts/archive.py:577`  destination = engineering / project_name / ".project-log"
- `skills/a-project-log-archive/scripts/archive.py:596`  ledger_relative = str(
- `skills/a-project-log-archive/scripts/archive.py:598`  )
- `skills/a-project-log-archive/scripts/archive.py:607`  pushed = git_push(kb_root, project_name, source / LEDGER_RELATIVE, target)

## `skills/a-project-log/REFERENCE.md`  (22 行 codex 独有)

- `skills/a-project-log/REFERENCE.md:8`  | legacy YAML files | `loopctl` migration window | Read-only compatibility; migrate explicitly |
- `skills/a-project-log/REFERENCE.md:13`  The legacy table below describes files that remain readable in the migration window:
- `skills/a-project-log/REFERENCE.md:14`  
- `skills/a-project-log/REFERENCE.md:15`  | File | Primary writer | Notes |
- `skills/a-project-log/REFERENCE.md:16`  |---|---|---|
- `skills/a-project-log/REFERENCE.md:17`  | workflow.yaml | vibe-goal | Phase changes require gate evidence |
- `skills/a-project-log/REFERENCE.md:18`  | business-logic/atoms.yaml | business-clarify / vibe-goal | Active semantics cannot be changed from code alone |
- `skills/a-project-log/REFERENCE.md:19`  | requirements/baseline.yaml | requirement-baseline | Versioned; supersede rather than overwrite history |
- `skills/a-project-log/REFERENCE.md:20`  | tasks/task-list.yaml | vibe-goal / task-decompose | Every status change should preserve verification integrity |
- `skills/a-project-log/REFERENCE.md:21`  | decisions/decision-log.yaml | any decision-making Skill | B and C decisions should be recorded |
- `skills/a-project-log/REFERENCE.md:22`  | research/solution-research.yaml | solution-researcher | Evidence date and conditions required |
- `skills/a-project-log/REFERENCE.md:23`  | architecture/architecture.yaml | architecture-decision | Reference supporting business atoms and decisions |
- `skills/a-project-log/REFERENCE.md:24`  | specs/* | engineering-spec | One spec per non-trivial task or coherent group |
- `skills/a-project-log/REFERENCE.md:25`  | alignment/findings.yaml | vibe-goal after read-only audit | Reviewer returns draft; primary decides repair/escalation |
- `skills/a-project-log/REFERENCE.md:26`  | retrospective/retrospective.yaml | retrospective | Evidence-backed improvement only |
- `skills/a-project-log/REFERENCE.md:27`  | distillation/candidates.yaml | operator-distill | Staged promotion; never silently update global assets |
- `skills/a-project-log/REFERENCE.md:48`  ## Large project scaling
- `skills/a-project-log/REFERENCE.md:49`  
- `skills/a-project-log/REFERENCE.md:50`  When a single YAML file becomes difficult to maintain, split by domain while retaining an index file. Do not split prematurely. The validator can later be extended to resolve domain indexes.
- `skills/a-project-log/REFERENCE.md:51`  
- `skills/a-project-log/REFERENCE.md:59`  - Single source of truth: format 2 uses the branch-local state database and generated `handoff.md`; legacy uses `loop/handoff.md` and `loop/active-run.yaml`. The two md files must not contradict them.
- `skills/a-project-log/REFERENCE.md:60`  - Machine-maintained state (format 2 database; legacy `loop/events.jsonl`, `loop/active-run.yaml`, `loop/handoff.md`, `verification/evidence.yaml`) must not be manually reordered or rewritten.

## `skills/a-project-log/SKILL.md`  (11 行 codex 独有)

- `skills/a-project-log/SKILL.md:4`  compatibility: codex
- `skills/a-project-log/SKILL.md:22`  python3 "${CODEX_HOME:-$HOME/.codex}/vibe-workflow/scripts/vibe.py" --root . init
- `skills/a-project-log/SKILL.md:26`  4. 将本轮目标写入 `workflow.yaml`、`current-session.md` 和 `task-list.yaml` 后再推进非琐碎工作。
- `skills/a-project-log/SKILL.md:32`  优先读取 `current-session.md`、`workflow.yaml`、活跃任务以及与当前目标相关的业务原子和决策。不要无目的加载全部历史。
- `skills/a-project-log/SKILL.md:36`  - format 2：`records` 保存业务原子、需求基线、决策、架构、研究、对齐、复盘与蒸馏；`evidence` 保存证据状态、覆盖范围与哈希绑定；`reviews` 保存独立复核；状态库按 Git 分支上下文隔离。
- `skills/a-project-log/SKILL.md:37`  - 旧格式：`business-logic/`、`requirements/`、`research/`、`architecture/`、`tasks/`、`decisions/`、`verification/`、`alignment/`、`work-trace/`、`retrospective/`、`distillation/` 仍按 YAML 分层读取。
- `skills/a-project-log/SKILL.md:38`  - `progress.md`、`current-session.md`、生成的 `handoff.md` 是面向人的摘要；format 2 的精确状态以状态库为单一事实源。
- `skills/a-project-log/SKILL.md:50`  - 原生 `/goal` 管线程执行；Project Goal 与 Loop 状态不得被原生 Goal 临时措辞反向覆盖。
- `skills/a-project-log/SKILL.md:67`  - 精确当前状态与下一步以 `loop/handoff.md`、`loop/active-run.yaml` 为权威状态源。
- `skills/a-project-log/SKILL.md:70`  - 不手工重排或改写 `loop/events.jsonl`、`loop/active-run.yaml`、`loop/handoff.md`、`verification/evidence.yaml`。
- `skills/a-project-log/SKILL.md:73`  详细规范见 `REFERENCE.md`、`.project-log/docs/`、模板和 schemas。

## `skills/a-requirement-baseline/SKILL.md`  (2 行 codex 独有)

- `skills/a-requirement-baseline/SKILL.md:5`  compatibility: codex
- `skills/a-requirement-baseline/SKILL.md:46`  8. Update `workflow.yaml` only after all exit conditions are met.

## `skills/a-retrospective/SKILL.md`  (1 行 codex 独有)

- `skills/a-retrospective/SKILL.md:5`  compatibility: codex

## `skills/a-session-handoff/SKILL.md`  (3 行 codex 独有)

- `skills/a-session-handoff/SKILL.md:5`  compatibility: codex
- `skills/a-session-handoff/SKILL.md:29`  - **单一事实源**：精确下一步以 `loop/active-run.yaml`、`loop/handoff.md` 为准；不手工重排机器维护的结构化状态文件。
- `skills/a-session-handoff/SKILL.md:31`  同时运行 `loopctl handoff` 生成 `.project-log/loop/handoff.md`。原生 Goal 进入 paused、blocked、budget/usage limited、cleared 或 replaced 时，Project Goal 保持不变。

## `skills/a-skill-evolution/SKILL.md`  (1 行 codex 独有)

- `skills/a-skill-evolution/SKILL.md:5`  compatibility: codex

## `skills/a-solution-research/SKILL.md`  (1 行 codex 独有)

- `skills/a-solution-research/SKILL.md:5`  compatibility: codex

## `skills/a-task-decompose/SKILL.md`  (2 行 codex 独有)

- `skills/a-task-decompose/SKILL.md:5`  compatibility: codex
- `skills/a-task-decompose/SKILL.md:79`  Update `.project-log/tasks/task-list.yaml`. Keep task order dependency-aware, not merely chronological.

## `skills/a-verification/SKILL.md`  (2 行 codex 独有)

- `skills/a-verification/SKILL.md:5`  compatibility: codex
- `skills/a-verification/SKILL.md:74`  Register durable evidence in `.project-log/loop/evidence-index.yaml` through `loopctl record-evidence`. Bind it to the current Git commit/diff or covered file hashes. Later changes to covered files, requirements, depende

## `skills/a-work-trace/SKILL.md`  (1 行 codex 独有)

- `skills/a-work-trace/SKILL.md:5`  compatibility: codex

## `skills/a-workflow-update/SKILL.md`  (3 行 codex 独有)

- `skills/a-workflow-update/SKILL.md:5`  compatibility: codex
- `skills/a-workflow-update/SKILL.md:35`  2. Run `scripts/update_workflow.py --dry-run` against the global Codex config directory.
- `skills/a-workflow-update/SKILL.md:38`  5. Confirm the runtime assets and templates exist, then restart Codex to load the update.

## `skills/b-background-task-runner/SKILL.md`  (1 行 codex 独有)

- `skills/b-background-task-runner/SKILL.md:5`  compatibility: codex

## `skills/b-concise-communication/SKILL.md`  (1 行 codex 独有)

- `skills/b-concise-communication/SKILL.md:5`  compatibility: codex

## `skills/b-jetson-robot-policy-deployment/SKILL.md`  (1 行 codex 独有)

- `skills/b-jetson-robot-policy-deployment/SKILL.md:5`  compatibility: codex

## `skills/b-multi-role-ux-audit/SKILL.md`  (1 行 codex 独有)

- `skills/b-multi-role-ux-audit/SKILL.md:5`  compatibility: codex

## `skills/b-personal-knowledge-distill/SKILL.md`  (1 行 codex 独有)

- `skills/b-personal-knowledge-distill/SKILL.md:5`  compatibility: codex

## `skills/b-plan-stress-test/SKILL.md`  (1 行 codex 独有)

- `skills/b-plan-stress-test/SKILL.md:5`  compatibility: codex

## `skills/b-scenario-product-walkthrough/SKILL.md`  (1 行 codex 独有)

- `skills/b-scenario-product-walkthrough/SKILL.md:5`  compatibility: codex

## `skills/b-skill-authoring/SKILL.md`  (4 行 codex 独有)

- `skills/b-skill-authoring/SKILL.md:3`  description: Design and write a focused Codex Skill with clear triggers, progressive disclosure, optional deterministic helpers, and reviewable resource boundaries.
- `skills/b-skill-authoring/SKILL.md:5`  compatibility: codex
- `skills/b-skill-authoring/SKILL.md:27`  3. **Use the Skill as the entry point.** Codex discovers `SKILL.md` directly. Do not require an OpenCode-style same-named command file.
- `skills/b-skill-authoring/SKILL.md:38`  ~/.config/codex/skills/<a-or-b-kebab-case-name>/

## `skills/b-source-code-tutoring/SKILL.md`  (0 行 codex 独有)


## `skills/b-web-research-tooling/SKILL.md`  (1 行 codex 独有)

- `skills/b-web-research-tooling/SKILL.md:5`  compatibility: codex

## `skills/vibe-subagent-orchestration/SKILL.md`  (17 行 codex 独有)

- `skills/vibe-subagent-orchestration/SKILL.md:3`  description: "Dynamically delegate a Vibe Coding lifecycle role to a bounded Codex subagent, preserve main-agent authority, and integrate structured evidence-backed results."
- `skills/vibe-subagent-orchestration/SKILL.md:5`  compatibility: codex
- `skills/vibe-subagent-orchestration/SKILL.md:16`  ## Role templates
- `skills/vibe-subagent-orchestration/SKILL.md:18`  The global Vibe runtime stores role contracts under:
- `skills/vibe-subagent-orchestration/SKILL.md:21`  VIBE_RUNTIME="${CODEX_HOME:-$HOME/.codex}/vibe-workflow"
- `skills/vibe-subagent-orchestration/SKILL.md:22`  ls "$VIBE_RUNTIME/agents"
- `skills/vibe-subagent-orchestration/SKILL.md:36`  Build a task-bound prompt with:
- `skills/vibe-subagent-orchestration/SKILL.md:37`  
- `skills/vibe-subagent-orchestration/SKILL.md:38`  ```bash
- `skills/vibe-subagent-orchestration/SKILL.md:39`  python3 "$VIBE_RUNTIME/scripts/render_subagent_prompt.py" \
- `skills/vibe-subagent-orchestration/SKILL.md:40`  --role <role> \
- `skills/vibe-subagent-orchestration/SKILL.md:41`  --project-root <project-root> \
- `skills/vibe-subagent-orchestration/SKILL.md:42`  --task "<precise delegated outcome>" \
- `skills/vibe-subagent-orchestration/SKILL.md:43`  --scope "<allowed files/modules or read-only boundary>"
- `skills/vibe-subagent-orchestration/SKILL.md:44`  ```
- `skills/vibe-subagent-orchestration/SKILL.md:51`  4. Use Codex's native subagent facility when available. For multiple agents, parallelize only independent work and use disjoint write scopes.
- `skills/vibe-subagent-orchestration/SKILL.md:53`  6. If native subagents are unavailable, perform the role serially and label the result `serial-role-fallback`.
