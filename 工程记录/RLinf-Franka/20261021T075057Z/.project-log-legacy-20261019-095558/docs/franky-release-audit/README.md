# Franky release audit — 2026-10-16

Read-only T-013 investigation. No controller changes or hardware operation.

## Provenance

- Installed direct_url points to Brunch-Life/franky release wheels-libfranka-0.19.0, CPython311 manylinux2_28 wheel.
- Downloaded release wheel SHA256: `4301aac4fefae2e1ad81d3902cb37fb0e94765626487e2a3587fcd7b4233362d`, equal to GitHub release asset digest.
- Main-agent ZIP-byte comparison: installed `franky/_franky.cpython-311-x86_64-linux-gnu.so` and `franky/tracker.py` equal wheel entries. Installed extension SHA256: `254c91a24b341955aec139dd26262972902f9f45e22f2adde537e2fa8b791ad1`.
- Release tag points to master `0d4f8196ecf392689a3689cb442625c4b0c2fed2`, NOT the enhanced tracking implementation. Do not inspect this tag as wheel source.
- Release notes specify enhance-impedance-control. Successful release workflow run `25786132748` used `7bdb567df879a771c3095fb5815a8324c94f2ce6` (2026-05-13 07:56 UTC), preceding asset publication at 08:26 UTC. Later runs failed/cancelled. Checkout in reusable build workflow has no alternate ref.
- Archived C++/headers retrieved through GitHub contents API at that immutable commit. This is strong build-history association, NOT cryptographic source-to-binary attestation.
- URLs: https://api.github.com/repos/Brunch-Life/franky/releases/tags/wheels-libfranka-0.19.0 and https://github.com/Brunch-Life/franky/actions/runs/25786132748

## Findings

1. Tracking update copies latest pose directly (`cartesian_impedance_tracking_motion.cpp:66–77`); base consumes it immediately (`cartesian_impedance_base.cpp:63–64`). No pose interpolation in these implementations. Gain smoothing is separate.
2. Rotational error is base-expressed quaternion vector, norm sin(theta/2), not rotvec angle (`base.cpp:89–97`). Header's rad label is misleading. Small-angle angular restoring coefficient is K_r/2, not K_r.
3. Cartesian damping is diagonal 2 sqrt(K); absent twist defaults to zero (`base.cpp:42–50,99–103`). This does not prove critical damping of actual configuration-dependent robot inertia.
4. Nullspace reference q is fixed per tracker lifetime, projector varies with J. P=I-J^T(J^T)^+; SVD hard threshold 1e-6, not damped least squares (`base.cpp:16–24,108–115`). This alone does not prove singularity or oscillation.
5. Worker-arm log (now archived) confirms active K_r=80, K_ns=5, rotational clip .15, translation K_t=1200 and clip .02. Only two tracker creation messages, both at startup. The .15 rotational component clip corresponds to 17.25 degrees for pure-axis error, not 8.59 degrees; K_r*clip=12 Nm only bounds each stiffness-wrench component, NOT damping, total wrench or joint torque.

## Interpretation / next step

Prior capture target-entry cadence ~7.385 Hz and requested orientation increments ~2.46–2.85 degrees median can plausibly produce reference-step excitation with velocity damping. This is a concrete mechanism, NOT an established root cause or a full explanation of roll selectivity. Actual high-rate reference, q/dq, torque and event alignment are missing.

No filter, gain, torque, Desk or hardware change is authorized. Next useful evidence requires a separately approved opt-in passive high-rate Franky logger (without blocking RT callback), or operator-supplied existing high-rate logs. Preserve source timestamps, applied reference and measured state; validate overhead offline before any operator trial. Existing 7.4 Hz pickle cannot recover in-step vibration.

Independent reviewer `ses_ebbe0f084ffeZCYK9BqMEzguR7` verified archived formulas and driver semantics; did not independently recompute wheel hash or inspect original worker log. Numerical/causal validation remains partial; T-013 not complete.
