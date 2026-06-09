# Knowledge Frontmatter Reference

## Required Fields

- `id`
  - Stable identifier. Format: `kb-<category>-NNNN`.
- `title`
  - Human-readable reusable rule title.
- `category`
  - One of: `architecture`, `debugging`, `workflow`, `config-behavior`, `patterns`, `anti-patterns`, `ai-collaboration`.
- `tags`
  - Broad grouping terms for browsing and quick-ref generation.
- `keywords`
  - Search-oriented phrases, subsystem terms, API names, runtime concepts.
- `triggers`
  - Error strings, recurring symptoms, or concrete search phrases likely to surface this entry.
- `source_projects`
  - Project keys that contributed evidence.
- `source_refs`
  - Evidence references back to `.project-log` or archived source logs.
- `confidence`
  - Suggested values: `high`, `medium`, `low`.
- `applicability`
  - Short text describing where reuse is appropriate.
- `updated_at`
  - ISO date for the most recent substantive update.

## Optional Fields

- `related`
  - Wiki-style links to nearby entries.
- `aliases`
  - Alternate titles or abbreviations.
- `counterexamples`
  - Cases where the rule should not be applied.
- `supersedes`
  - Older entries replaced by this one.

## Authoring Rules

- `tags` are for stable browsing dimensions.
- `keywords` are for likely free-text search terms.
- `triggers` are for concrete error/symptom matching and should stay close to the language seen in logs or troubleshooting.
- Keep frontmatter factual; explanatory prose belongs in the body.
- Do not omit evidence lineage just because the rule feels obvious.

## Retrieval Rules

- `kb find` should rank `title`, `keywords`, and `tags` hits.
- `kb related` should heavily weight `triggers` and exact symptom strings.
- quick-ref indexes should prefer `tags` plus short rule summaries.
