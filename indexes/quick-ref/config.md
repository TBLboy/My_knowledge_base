# Quick Ref: config

## Trace runtime consumers before tuning config

- Rule: A parameter is not a real control surface until you trace where it is read, transformed, and finally consumed at runtime.
- Path: `config-behavior/trace-runtime-consumers-before-tuning.md`
- Applicability: Multi-layer systems with YAML config, runtime overrides, and orchestration-mediated parameter application.
