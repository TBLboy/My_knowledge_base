# Personal Knowledge Base

## Purpose

This repository stores reusable engineering knowledge distilled from project `.project-log/` records.

It separates:

- formal reusable knowledge
- staged draft updates
- raw project-log archives
- distillation audit history

## Top-Level Structure

- `patterns/`: reusable engineering patterns
- `debugging/`: reusable debugging rules and failure-mode knowledge
- `architecture/`: architecture-level lessons and system-design rules
- `workflow/`: reusable project workflow and execution habits
- `ai-collaboration/`: practices for working effectively with AI agents
- `config-behavior/`: config/runtime mapping lessons
- `anti-patterns/`: traps and bad defaults to avoid
- `config/`: portable runtime configuration such as session hot-load rules
- `staging/`: reviewable draft knowledge from distillation runs
- `source-project-logs/`: synchronized raw `.project-log` archives
- `distillation-ledger/`: cross-project distillation audit trail

## Rules

- Formal knowledge should be portable and evidence-backed.
- Staging content may be revised or rejected.
- Raw project-log archives are evidence, not polished knowledge.
- Every accepted knowledge entry should preserve evidence lineage.
- Session-time automation should prefer repository tools such as `tools/kb.py` and `tools/kb_hotload.py` so behavior can move across machines with the repo.
