# Recovery

Active Task: franka-robot-capture-integration-20261019 (balanced).

## State

Staged startup is implemented in `robot_capture_franka-franka-feature` and running in the web app (`./run.sh`, `/teleop` HTTP 200). No worker, publisher, or PC Service is running now.

Implemented this session:
- `franka/services.py`: owned PC Service/publisher processes, external-instance refusal, detached-launcher detection (not owned), verified stop.
- `franka/startup.py`: fixed stage checklist, cooperative cancel, cleanup-before-cancel-report, duplicate rejection, restart blocked after cleanup failure.
- `franka/supervisor.py`: staged prepare/cleanup, worker launch/adoption refusal, Pico wait gate, web shutdown cleanup.
- `franka/worker.py` + `release_backend.py`: `start_pico`/`pico_status`, Pico-only status without arm telemetry, held-grip preflight block, control-loop stop verification, backend error surfaced instead of staying "controlling".
- `app/ui_teleop.py`: persistent progress dialog with stage list, Pico detail, cancel, gated enable button.
- Telemetry history now treats an equal sequence from an idle poll as a harmless repeat (this caused constant UI errors before).
- Config: `franka_worker.enabled: true`, local `franka-worker.json`, services block; scalar compliance clips.

Verification: 57 offline tests pass; `py_compile` and `git diff --check` pass. No motion, no real Pico, no gripper validation.

## Open items

1. Worker `control_hz` is 10 while Release validated 30 Hz. Not changed; needs an operator decision.
2. PC Service launcher backgrounds itself, so the workbench reports it as external and does not stop it on cancel. Documented in `docs/franka-staged-startup.md`.
3. Reset still disabled; motion, gripper initialization, and Pico input on real hardware are unvalidated.
4. Web app SIGTERM can hang (pre-existing); SIGKILL fallback was used once. Not investigated.
5. Operator test flow: refresh `/teleop`, click 启动控制服务, open the headset APK during 等待 Pico 连接, then enable control separately.
