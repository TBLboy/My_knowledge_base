# Experimental orientation lowpass test1.0

Default **OFF**. Offline implementation only, not a validated safety feature or a
J7/roll vibration fix. Operator accepts orientation lag. No gains, torque, Desk,
guards, action scales or control frequency are changed. No new thread, publisher,
driver hook or background motion is added.

Operator-only enable (normal launcher still starts services and resets the robot):

```bash
bash RLinf-Franks/run_pico_session.sh --passive-telemetry --orientation-filter --orientation-tau 0.20
```

Disable: stop the session, then start a **new** session without the filter flag:

```bash
bash RLinf-Franks/run_pico_session.sh --passive-telemetry
```

The launcher clears inherited filter environment variables. Do not toggle it in a
running worker. Direct extension users opt in with
`RLINF_PICO_ORIENTATION_FILTER=1` and `RLINF_PICO_ORIENTATION_TAU=0.20` before Ray
starts. Tau must be finite, 0.05–0.50 seconds; a launcher tau without enable fails
before preflight. The selected version/tau appear in worker startup and each
enabled action's info.

## Boundary and lifecycle

Only `PicoDelta.action` receives a copied reading with filtered mapped
`rotation_delta`. Translation and gripper fields and the position anchor are
unchanged. The original mapping, clipping and downstream controller remain in
charge. `PicoTcp` is untouched. The filter is installed outside existing passive
wrappers, once per process via `rlinf_ext.register`.

For held valid input, `Y = Exp(alpha Log(R Y^-1)) Y`,
`alpha = 1-exp(-dt/tau)`, using shortest SO(3) arcs, not Euler averaging. The first
grip sample starts at identity (zero rotation request at the grip anchor).
Inactive input clears history immediately. No filter update runs between calls.
Reset clears history and requires an observed release before orientation resumes,
because the transport's grip anchor can survive an episode reset.

Nonfinite/malformed rotation, held-not-ready/stale/invalid input, nonpositive
monotonic dt, or dt >0.30s discards history and inhibits orientation until release.
While inhibited, the orientation request is the measured orientation relative to
the existing arm anchor, not the stale target, zero absolute delta or raw input.
Translation/gripper still follow the original mapping; this is **not** a new
whole-arm stale-input safety gate. Transport normally reports stale as inactive.
Source freshness still relies on the existing transport (local monotonic dt does
not prove publisher freshness). A missed release/regrip wholly between samples
cannot be detected at this boundary.

`pico_rotation_delta` remains raw. `pico_orientation_filter` contains `version`,
`tau_s`, `max_gap_s`, `status`, `alpha`, `monotonic_s`, `raw_rotation_delta`, and
`applied_rotation_delta` (null inactive). Applied includes measured-hold fallback.
Existing passive target/command fields describe the filtered call. The existing
`final_franka_target` field is pre-driver-guard, NOT proof of actual final target.

## Offline replay and choice

```bash
RLinf/.venv/bin/python RLinf-Franks/replay_orientation_filter.py \
  RLinf/logs/20261016-162726-realworld_collect_data_pico_single_franka/collected_data/rank_0_env_0_episode_1_step_487_success.pkl
PYTHONPATH=RLinf:RLinf-Franks RLinf/.venv/bin/python -m pytest -q \
  RLinf-Franks/test_orientation_filter.py RLinf-Franks/test_passive_diagnostics.py \
  RLinf-Franks/test_passive_joint_lifecycle.py
```

Only load trusted local pickles. Replay input SHA256:
`8fbf4b5d30508bdc79b78e76b826ec7b08ab196bf3e85f0b388e67e3ee1ab1df`.
164 transitions: 89 inactive, 3 grip starts, 72 filtered; use recorded command
computation monotonic timestamps. Raw adjacent rotation step p95/max 4.076/7.241°.

| tau (s) | filtered step p95/max (°) | raw-to-filter lag p50/p95/max (°) |
|---|---|---|
| 0.10 | 3.841 / 6.133 | 0.809 / 1.313 / 2.179 |
| **0.20** | **3.701 / 5.061** | **2.330 / 3.697 / 5.310** |
| 0.30 | 3.594 / 4.486 | 3.816 / 6.090 / 7.974 |

Choose 0.20s as a conservative experimental compromise: about 30% smaller maximum
sample-to-sample step here, without the larger lag of 0.30s. This is not a robot
stability optimization. At median ~7.4Hz (135ms), alpha ~0.49; constant-input
error decays to ~5% in ~0.6s (sample quantized). Low-frequency discrete delay is
roughly 0.14s plus sampling/transport/controller latency. There is **no continuous
interpolation**: target jumps still occur at ~7.4Hz. Low-rate historical input
replay cannot establish in-step torque behavior, stability or J7 improvement.

Before operator testing: independent review, empty workspace, no contact task,
small slow motions, reachable E-stop. Release grip and stop on increased vibration,
unexpected motion, force or Desk warnings. Confirm release after reset/fault.
Do not raise limits or gains to compensate for lag. Retain raw/filtered telemetry
and startup logs. Hardware behavior and physical stopping remain unverified.
