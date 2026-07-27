# Tofu Detection Precision Analysis

> Scene is static (tofu does not move). All analysis focuses on systematic error in a single detection snapshot, not dynamic tracking.

## Error Budget Summary

| Source | Estimated Contribution | Priority |
|--------|----------------------|----------|
| Hand-eye calibration | ~2-3mm translation, ~1-2° rotation | P0 |
| TCP calibration | ~1-3mm (RMSE unknown) | P0 |
| Tofu vertex detection | ~2-5mm per corner | P1 |
| **Total at knife blade** | **~10-30mm** | — |

---

## 1. Hand-Eye Calibration (P0)

### Method
- **Type**: Eye-to-hand (eye-on-base) — camera fixed, ArUco marker on TCP
- **Initialization**: Shah+L1 analytical method
- **Outlier rejection**: MAD 3.5σ threshold
- **Refinement**: Huber loss weighted Levenberg-Marquardt
- **Package**: `cuttofo_calibration/` (custom GUI + Python engine)
- **Reference implementation**: `/home/tbl/Project/dexbot_ros2_ws/src/dexbot_toolbox/dexbot_toolbox/calibration/hand_eye_calibration_node.py`

### Current Result

| Metric | Value | Samples |
|--------|-------|---------|
| Translation RMSE | **2.73 mm** | 8 |
| Rotation RMSE | **2.13°** | 8 |
| Historical best (trans) | ~1.5 mm | 10 |
| Historical best (rot) | ~1.13° | 10 |

### Error Sources
1. **Low sample count** (8 vs target 15+) — convergence not saturated
2. **ArUco marker on TCP** — marker's physical position differs from knife blade TCP by unknown offset (the `T_tcp_marker` output partially accounts for this, but any residual projects as detection error at the blade)
3. **Camera resolution limited by USB 2.1** — lower resolution → corner detection noise → worse calibration

### ROI
- 2.73mm translation error at camera → ~2-3mm at tofu (direct transfer, no amplification)
- 2.13° rotation error → ~3-5mm offset at blade tip (lever arm from wrist to blade ≈ 80-150mm)
- **Estimated total**: 5-8mm at blade

---

## 2. TCP Calibration (P0)

### Method
- **N-point touch calibration**: knife tip touches fixed conical reference point at 6+ arm orientations
- **Solve**: least-squares fitting of `tcp_offset` to minimize position residual across all poses
- **Script**: `calibrate_tcp_offset.py` (in `cuttofo_calibration/`)

### Current Value
```yaml
right_arm:
  tcp_offset: [0.023, 0.15, 0.292]  # metres in flange frame
  tcp_Z == flange_Z  # pure translation, no relative rotation
```

### Known Issues
- **RMSE unknown** — current script does not save RMSE to config; the user has not reported the calibration residual
- **Conical reference point wear/position** — physical reference deviation directly shifts all TCP calibrations
- **Only 6+ poses** — may not fully cover the wrist orientation workspace

### Impact
- 1mm TCP error at flange → 1mm error at blade (1:1 translation, no lever amplification for translation)
- But TCP error combined with hand-eye rotation error → significant blade displacement
- **Estimated**: 1-3mm

---

## 3. Tofu Vertex Detection (P1)

### Pipeline
```
RGB → SAM3 (threshold=0.005) → mask → depth bilateral filter (d=5)
→ MAD outlier removal (3.5σ) → AABB percentile corner extraction
→ pose_estimator EMA (α=0.5) → tofu_state 15-frame sliding window
```

### 3a. SAM3 Threshold: `detection_threshold: 0.005`

| Instance | Threshold | Effect |
|----------|-----------|--------|
| Phase2 (tofu detection) | **0.005** | Extremely low → mask may overflow tofu boundary |
| Phase1 (grab: handle) | **0.3** | Reasonable, tighter |

- `0.005` admits almost any pixel with positive confidence → mask likely oversized by 5-15%
- Oversized mask → percentile X/Z bounds expand → corners shift outward → TCP target shifts

### 3b. AABB Percentile Asymmetry

| Axis | Low Percentile | High Percentile |
|------|---------------|-----------------|
| X (fwd/back) | 0.1% | 99.9% |
| Z (right/left) | 0.001% | **99.0%** |

- Z-high (right edge) trims **1%** of points vs X edges trim only **0.1%**
- This systematically truncates the right edge by ~1mm (asymmetric inward shift)
- Affects the A/B corner (right edge) → TCP target origin shifts

### 3c. Depth Noise & Filtering
- **Bilateral filter**: d=5, σ=20mm — good edge preservation, ~0.5mm smoothing
- **MAD removal**: 3.5σ — removes ~0.1% outliers
- Depth noise floor on D435I at 640×480@15fps: ~2-5mm at 0.5m range
- Filtered residual: ~1-2mm

### 3d. Double Smoothing Latency (~2s)

| Stage | Filter | Lag |
|-------|--------|-----|
| pose_estimator EMA | α=0.5 | ~0.5s |
| tofu_state buffer | 15 frames @ 15fps = ~1.0s | ~1.5s |
| **Total** | — | **~2s** |

- For static scene: no lag-related error, but buffer mean smooths out noise further

### Estimated Vertex Error
- SAM3 mask overflow: 2-5mm per axis
- AABB percentile asymmetry: ~1mm on right edge
- Depth noise (post-filter): 1-2mm
- **Total per corner**: 4-8mm
- **Effect on TCP target**: 5-10mm

---

## Total Uncertainty Budget

| Source | Translation (mm) | Rotation (°) | Blade Offset (mm) |
|--------|-----------------|--------------|-------------------|
| Hand-eye | 2.7 | 2.1 | 5-8 |
| TCP | 1-3 | 0 | 1-3 |
| Vertex detection | 4-8 | ~3 | 5-10 |
| **Total RSS** | **5-9** | **~4** | **10-30** |

Note: **10-30mm** exceeds the tofu cutting margin (blade offset `offset_a=0` places TCP on right edge → blade may miss tofu entirely or scrape incorrectly).

---

## Static Scene Implication

Since the tofu is confirmed static, dynamic tracking precision (smoothing lag, jitter over time) is irrelevant. All optimization should focus on **per-frame absolute accuracy**:
- Reduce mask overflow (SAM3 threshold)
- Fix asymmetric percentile trimming
- Improve calibration RMSE (more samples)
- No need for dynamic improvements (EMA α, buffer size) unless they actively harm accuracy

---

## Proposed Fixes (Priority Order)

### P0 — Redo Hand-Eye Calibration
- Collect **15+ high-quality samples** with good pose coverage
- Target RMSE < **2mm translation, < 1.5° rotation**
- Save result to `hand_eye_calibration.json` and `tf_calibrated.json`

### P0 — Redo TCP Calibration
- Re-run `calibrate_tcp_offset.py` with 6+ good poses
- Confirm RMSE < **2mm** and save RMSE alongside offset in `cuttofo_config.yaml`

### P1 — Fix SAM3 Threshold
- Raise `detection_threshold` from **0.005 → 0.3** (match Phase1 grab value)
- Or add morphological mask cleanup (erosion + dilation)

### P1 — Fix AABB Percentile Asymmetry
- Change `z_percentile_high` from **99.0 → 99.9** (consistent with X edges)
- Or unify all four edges to same percentile

### P2 — Reduce Unnecessary Smoothing
- Change `buffer_size` from **15 → 5** (still >3x oversampled at 15fps)
- Keep EMA α=0.5 (already reasonable; buffer dominates lag)

### P3 — Add TCP Calibration RMSE Tracking
- Modify `calibrate_tcp_offset.py` to auto-save RMSE to `cuttofo_config.yaml`
- Allows runtime confidence check
