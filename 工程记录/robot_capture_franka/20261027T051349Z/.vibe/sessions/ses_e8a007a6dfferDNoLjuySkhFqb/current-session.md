# Session recovery — teleop stutter: root cause identified

Status: diagnosis complete. Root cause is the Pico -> PC Service TCP transport (loss/reordering -> RTO head-of-line blocking). No robot was connected or moved; no product code changed.

## Operator symptom

Arm stops tracking while the hand keeps moving, then jumps forward fast and resumes.

## Root cause (measured, zero-robot)

Pico->PC Service TCP stream loses/reorders 5-10% of segments, producing ~19 TCP RTO stalls per 2 minutes. Each stall freezes the whole pose frame (headset + both controllers + vendor timestamp). The worker keeps issuing the last target because freshness uses host arrival time, then the target jumps (up to 7.6 cm) and the arm catches up at up to ~3x normal speed.

## Evidence

1. Archived recordings: 115 target-freeze events in 81/237 episodes; p50 167ms, p90 233ms, max 269ms; jump p50 1.6cm/max 7.6cm; post-jump speed median 3.2x (max 0.77 m/s).
2. Host healthy during stalls: 105/115 had sample gaps <=45ms; 114/115 had camera frame_time continuing at 33ms.
3. Zero-robot SDK probe (80Hz, 120s): loop p99 12.6ms, call max 1.09ms, but 15-18 whole-frame freezes >=120ms (125/150/213/225/238/250/263/275/287/288/300/325/337/338/488ms), all poses+timestamp bit-identical.
4. Pico sender counters over a separate 120s window: RetransSegs +463/OutSegs +10194 (4.5%), TCPTimeouts +19, TCPFastRetrans +442, TCPSackRecovery +372, TCPLostRetransmit +39.
5. PC socket: rto 229ms, rtt 28.7/14.3ms, rcv_ooopack +965/10094 segments (9.6%).
6. Ping 30Hz: 1.9-9% loss, RTT p90 47-59ms, max 127-424ms; per-stall loss not above random baseline, so ICMP is only supporting evidence.
7. Pico Wi-Fi: 5GHz Wi-Fi6, RSSI -38..-43dBm, 286Mbps, single BSSID, no roaming; PC has no wireless NIC; Pico 192.168.7.135/22 and PC 192.168.10.38/24 are different subnets routed via the gateway.

## Artifacts

- Probe: `/tmp/opencode/pico_probe.py` (sdk / subscribe modes, writes CSV with wall clock).
- CSV: `/tmp/opencode/pico_probe_sdk_*.csv`; ping: `/tmp/opencode/ping_sync.txt`; TCP snapshots: `/tmp/opencode/pico_tcp_before.txt` / `_after.txt`.
- Task: `.vibe/tasks/teleop-stall-diagnosis-20261023.json` (completed).

## Open items / constraints

- PC Service was started manually (DISPLAY=:1) for the test and is still running; stop it before a normal `start.sh` if the workbench rejects an existing instance.
- Network fix not applied: put Pico and PC on the same L2/AP, dedicated 5GHz SSID, avoid cross-subnet routing, check AP airtime.
- Software guard (re-anchor on source-timestamp discontinuity, or rate-limit catch-up) NOT implemented; requires separate approval and robot-side validation.
- Do not tune max_step/gains/stop policy as part of this diagnosis.

## USB transport verification (2026-10-26, later)

- Pico USB functions are `mtp,accessory,adb` only -> no RNDIS/USB tethering. USB path = `adb reverse tcp:63901 tcp:63901` + client remote IP `127.0.0.1`.
- A/B, 120s SDK probe each: Wi-Fi 60.9 vendor updates/s, 18 whole-frame freezes >=120ms; USB 79.5 and 79.6/s with 1 freeze each (startup only, ~500ms). "vendor timestamp repeated >=3 cycles" = 0 on USB.
- Client IP is persisted on the headset (now 127.0.0.1). `adb reverse` is volatile: lost on cable unplug / adb restart, and there is no Wi-Fi fallback, so startup must create and verify the tunnel.
- PC Service still running (PID 106802) and was started manually with DISPLAY=:1.
- Not implemented yet: adb reverse setup/health-check in workbench startup; input-discontinuity guard; docs/config update.

## Resolved (operator-confirmed)

Operator confirmed live teleoperation after switching the client remote IP to 127.0.0.1 with `adb reverse tcp:63901 tcp:63901`: stutter gone, motion smooth. Matches A/B probe (USB 79.5-79.6 vendor updates/s, 1 startup-only freeze; Wi-Fi 60.9/s, 18 freezes per 120s).

Current live state: headset client IP persisted as 127.0.0.1; adb reverse active; PC Service started manually (PID 106802). Reverting to Wi-Fi requires setting the client IP back to 192.168.10.38.

Remaining (not implemented, needs separate approval): auto-create/verify adb reverse at workbench startup; runtime tunnel health check surfaced in UI; input-discontinuity protection (re-anchor/hold instead of catch-up jump).
