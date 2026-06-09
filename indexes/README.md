# Index Overview

This directory is generated from formal knowledge entries.

## Layout

- `by-tag/`: browse entries grouped by normalized tags.
- `by-category/`: browse entries grouped by formal category.
- `by-trigger/`: browse entries grouped by concrete trigger phrases or symptoms.
- `quick-ref/`: generated scene-oriented summaries.
- `manifest.json`: flattened machine-readable metadata for query tools.

## Rules

- Do not treat index files as primary knowledge.
- Do not hand-maintain long-lived content here.
- Rebuild indexes after formal knowledge changes.
- Session-time retrieval rules live in `../config/session-rules.yaml`, not in this generated directory.
