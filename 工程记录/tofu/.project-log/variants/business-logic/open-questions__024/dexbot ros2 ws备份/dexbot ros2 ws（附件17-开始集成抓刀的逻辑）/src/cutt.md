# Open Business Logic Questions

## Active Questions

### Q-20260517-001: Phase2 IK Validity

- Related edge: edge_2_prepare
- Question: Phase2 IK sometimes returns valid=0 (all 263 seeds rejected). Likely cause: edge_align=true + offset_a=0 making target too constrained. Is this consistently happening or intermittent?
- Why it matters: Blocks Phase2 entry; no manual fallback path in current code.
- Options: Relax POS_TOL_M / ROT_TOL_RAD; increase offset_a; disable edge_align for testing.
- Status: Open

### Q-20260517-002: Impedance Mode Stability

- Related edge: edge_3_to_4, edge_7_to_done
- Question: Impedance mode fails sporadically with "该操作不允许在当前上下电状态下执行". Is this a robot controller firmware bug, power-state issue, or joint limit trigger?
- Why it matters: Causes impedance→position fallback; position mode provides less compliance during cutting.
- Options: Investigate robot power state transitions; check joint limit proximity during extended cuts.
- Status: Open (fallback handles it gracefully)

### Q-20260517-003: Perception Health Recovery

- Related edge: edge_perception
- Question: When perception health is STALE or LOST, does Phase2/6 re-prepare correctly handle it? Is there a manual override for retrying detection?
- Why it matters: If SAM3 loses the tofu after rotation, system is stuck at Phase2.
- Options: Implement manual point-prompt (sam3-point-prompt branch); add timeout + retry logic.
- Status: Open

### Q-20260518-001: SAM3 Detection Reliability During Push

- Related branch: tofu-fall-detection
- Question: During Phase7 mid-cycle rightward push, the knife is moving at cut depth and partially occludes the tofu. Will SAM3 maintain stable detection at 5-10Hz?
- Why it matters: Fall detector relies on SAM3 mask for every frame; lost detection means no fall signal.
- Options: (a) Capture baseline at anchor height (before cut, less occlusion); (b) Add 0.5s result hold when detection drops; (c) Use max push distance safety limit as fallback.
- Status: To be discussed

### Q-20260518-002: Desk Plane and Knife Region Removal

- Related branch: tofu-fall-detection
- Question: What is the most robust method to remove desk plane and knife/hand region from point cloud? Desk removal via plane fitting (RANSAC) or percentile z_min? Knife removal via known knife pose or geometric ROI?
- Why it matters: Desk points pollute right_low_ratio and high_ratio; knife points add spurious geometry.
- Options: (a) For desk: percentile-based z_min from baseline frame (fitting tofu edge); (b) For knife: fixed ROI around known knife TCP position.
- Status: To be discussed

### Q-20260518-003: Fall Detector Communication Architecture

- Related branch: tofu-fall-detection
- Question: Should the fall detector run as a separate ROS node or integrate into knife_cut_action_server?
- Why it matters: If integrated into action server, blocking detection loop blocks the cut action; if separate, need service/action interface.
- Options: (a) Separate node: knife_cut_action_server calls a ROS2 service, waits for response, then stops push; (b) Integrated node: async detection loop + flag variable.
- Status: To be discussed

### Q-20260518-004: Feature Thresholds Tuning

- Related branch: tofu-fall-detection
- Question: Are the proposed thresholds (theta_signed > 12°, right_low_ratio > 0.38, high_ratio < 0.30, dx_right_low_edge > 0.12*H0) appropriate for real tofu sizes (typical 300g block)?
- Why it matters: Wrong thresholds cause false positives (stop pushing too early) or false negatives (push to max distance every time).
- Options: (a) Test offline with recorded bag data; (b) Make thresholds configurable; (c) Automatically calibrate from baseline frame statistics.
- Status: To be discussed

### Q-20260518-005: Continuous Frame Confirmation Window

- Related branch: tofu-fall-detection
- Question: Which confirmation strategy is more reliable — 5 consecutive frames or 6 of recent 8 frames?
- Why it matters: 5 consecutive is more conservative but more reactive to frame drops; 6/8 is more anti-jitter but slightly slower.
- Options: (a) 6/8 sliding window (recommended in design); (b) 5 consecutive; (c) Configurable.
- Status: To be discussed

### Q-20260518-006: Base Frame Transform

- Related branch: tofu-fall-detection
- Question: All point cloud processing assumes coordinates in robot base frame. The camera outputs in camera_link frame. The transform T_base_cam comes from hand-eye calibration. Is this transform accurate enough (after calibration drift) for sub-centimeter fall detection?
- Why it matters: Transform error shifts x_right_low_edge and theta_signed computations.
- Options: (a) Use calibration as-is; (b) Check calibration quality before Phase7; (c) Use tofu_state (already in base frame) instead of raw point clouds.
- Status: To be discussed

## Resolved Questions

- ✅ Phase7 vertical cut direction (was fan-ge_Z press, now base Y- cut) — resolved 2026-05-17
- ✅ Phase7 push timing (was at surface, now at cut depth) — resolved 2026-05-17
- ✅ Phase7 impedance fallback idempotency (was outer retry from wrong anchor) — resolved 2026-05-17
- ✅ Phase7 speed control (push speeds independent from cut speed) — resolved 2026-05-17
