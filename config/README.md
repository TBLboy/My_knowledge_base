# Runtime Configuration

This directory stores portable runtime configuration that should travel with the knowledge-base repository.

## Files

- `session-rules.yaml`: rule-based hot-load triggers for session-time knowledge lookup.

## Rules

- Keep these files portable across machines and sessions.
- Prefer repository-relative consumption from tools under `tools/`.
- User or project Claude settings may call repository tools, but the trigger logic should live here rather than in a skill-private path.
