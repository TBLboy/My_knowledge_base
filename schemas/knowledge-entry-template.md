# Knowledge Entry Template

```markdown
---
id: kb-<category>-0001
title: Replace with a concise reusable rule title
category: architecture
tags: [tag-a, tag-b]
keywords: [keyword-a, keyword-b]
triggers:
  - exact log/error snippet or recurring symptom
  - alternate phrasing users may search for
related:
  - [[related-entry-slug]]
source_projects: [project-key]
source_refs:
  - project-key:.project-log/progress.md#reference
confidence: high
applicability: Describe where this rule is safe to reuse.
updated_at: 2026-06-09
---

## Rule

State the portable rule in one or two sentences.

## Why

Explain the failure mode, architectural reason, or engineering tradeoff.

## When it applies

Describe the kinds of systems, tasks, or symptoms where the rule is relevant.

## Counterexamples

List the main cases where this rule should not be applied blindly.

## Evidence Lineage

- project: `project-key`
- source refs:
  - `.project-log/...`
- distillation run:
  - `distillation-ledger/runs/<timestamp>-<project-key>.md`
```

## Notes

- `id`, `title`, `category`, `tags`, `keywords`, `triggers`, `source_projects`, `source_refs`, `confidence`, `applicability`, and `updated_at` are required.
- `related` is optional but recommended when the entry strengthens or complements another rule.
- Keep trigger phrases close to real search language or real failure strings.
