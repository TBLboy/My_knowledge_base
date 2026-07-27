# Branch: feature-constrained-obb-vision

## Status

- implemented, build-checked, awaiting offline/hardware validation

## Purpose

Replace the current vision pose estimation pipeline (AABB/PCA) with a **constrained oriented bounding box (OBB)** algorithm that is more stable and tightly fits the tofu, under the physical assumption that the tofu's top surface is approximately parallel to the base_xz plane (i.e., the tofu rests flat). This improvement targets the豆腐视觉检测组件 (`pose_estimator_node` + `vision_utils.py`) to output more reliable top_corners and edge_dir for Phase2 prepare computation.

Clarified business objective as of 2026-05-23: the constrained OBB does **not** need to estimate a full physical 3D box enclosing the whole tofu body. The real downstream requirement is accurate and stable localization of the tofu top surface ABCD corners. It is acceptable for the estimated box to truncate the lower portion of the tofu, as long as the top footprint and long-edge direction are reliable for Phase2 prepare and cutting alignment.

---

## Start Node

- PHASE_2_MOVE_TO_PREPARE (existing main-path node)

## Target Node

- PHASE_2_MOVE_TO_PREPARE (improved implementation of the same node)

---

## Logic Path

```text
PHASE_2_MOVE_TO_PREPARE (main) → [vision-replacement: constrained-obb] → PHASE_2_MOVE_TO_PREPARE (improved)
```

**Note**: This branch does not change the node semantics. It changes the internal execution chain of the `edge_2_prepare` (Phase2's prepare computation) by replacing the underlying pose estimation method while preserving input/output contracts (`/tofu_state` fields and their meanings).

---

## Execution Chain (Detailed)

### Current Main Implementation (for comparison)

The current `pose_estimator_node` → `vision_utils.get_pose_from_mask` uses:
- Simple bilateral depth filtering.
- No mask erosion.
- No point cloud cleaning beyond MAD outlier filter.
- PCA-based orientation (full 6DoF), then `compute_object_center` and `reconstruct_corners` → yields 8 corners → `compute_edge_dir` and `compute_tcp_target_from_corners`.

Weaknesses: bounding box may be loose (AABB) or jittery (full PCA); no removal of boundary outliers; no explicit handling of tofu flatness constraint.

### Proposed Constrained OBB Pipeline

**Changes confined to**:
- `dexbot_middle_layer/dexbot_middle_layer/vision/pipeline/vision_utils.py`: replace/augment `get_pose_from_mask` implementation when `corner_mode="constrained_obb"`.
- `dexbot_middle_layer/dexbot_middle_layer/pose_estimator_node.py`: declare new parameters for the OBB algorithm and pass them to `get_pose_from_mask`.

**New execution chain inside `get_pose_from_mask` when `corner_mode="constrained_obb"`**:

1. **Mask preprocessing**:
   - Erode binary mask by `mask_erode_px` (default 5px) to inward shrink and discard boundary outliers.
   
2. **Point cloud generation** (unchanged back-projection from mask + depth + K).

3. **Depth filtering**:
   - Replace simple bilateral filter with a lightweight RealSense-style chain in `pose_estimator_node` / `vision_utils.py`:
     - Decimation proxy (optional image downsample + upsample)
     - Spatial smoothing proxy (bilateral filter)
     - Hole filling proxy (morphological fill of zero-depth gaps)
   - Aggregate multi-frame depth with a median stack in `pose_estimator_node` before geometry when `obb_depth_median_frames > 1`.

4. **Point cloud cleaning** (new):
   - Voxel grid downsample (`voxel_size = 0.002` m).
   - Statistical outlier removal (`nb_neighbors=20`, `std_ratio=1.0`).
   - Radius outlier removal (`radius=0.01`, `nb_points=8`).
   - DBSCAN clustering (`eps=0.01`, `min_points=10`); keep largest cluster.
   - If cluster too small (<30 points), fall back to AABB.

5. **Constrained OBB fitting in 2D (XZ plane)**:
   - Assumption: tofu top surface normal ≈ base_Y (i.e., yaw-only rotation around base Y axis).
   - Problem: Find rotation angle θ ∈ [0°, 180°) that minimizes OBB area in XZ after θ-rotation.
   - Exhaustive search with `angle_step_deg` (default 0.5° → 360 iterations).
   - For each θ:
     - Rotation matrix Rz(θ) about base Y axis.
     - Project points onto XZ: P_xz = P[:, [0,2]] @ [[cosθ, sinθ], [-sinθ, cosθ]] (or equivalent).
     - Compute axis-aligned bounding box in rotated XZ: u_min, u_max, v_min, v_max.
     - Area = (u_max-u_min)*(v_max-v_min). Keep θ with smallest area.
   - After best θ found:
     - Set e1 = [cosθ, 0, sinθ] (major axis in XZ plane).
     - e3 = [-sinθ, 0, cosθ] (minor axis in XZ plane).
     - e2 = [0,1,0] (base Y up).
     - Rotation matrix R = [e1, e2, e3] (columns).
   - Compute Y extent (base Y axis) via percentiles (1%–99%) on points transformed by R.
   - Compute center in base frame: mean of all cleaned points.
   - Extents = [major_len, height, minor_len] + optional margin (e.g., 3mm each side).
   - Generate 8 OBB corners in base frame, then derive top 4 corners (max Y).
   - Compute edge_dir as horizontal right edge direction from top corners (v = right-most two points; normalized; ensure v.x > 0).

6. **Fallback**:
    - If cleaning fails or OBB fitting fails, fall back to existing AABB/PCA mode (preserve `corner_mode="aabb"` behavior).

### Candidate Refinement: Top-Footprint Bounds Filter

Status: candidate idea, recorded for analysis; not yet implemented in runtime code.

Business goal:
- Produce stable tofu top ABCD corners rather than a complete 3D box enclosing all side/bottom points.
- Allow the bottom/lower tofu point cloud to be discarded if it improves top footprint accuracy.
- Keep downstream output contract unchanged (`pose_base`, `top_corners_base`, `extents_3d`, `angle_rad`).

Execution chain refinement:
1. Keep the current yaw estimate source unchanged: eroded-mask points transformed to base frame, then cleaned by voxel/SOR/ROR/DBSCAN.
2. Use the cleaned fit points only to estimate yaw (`best_theta`) by XZ area minimization.
3. For final bounds, start from full-mask `bounds_points_base`, but filter it by base-frame Y because base Y is upward.
4. Sort/filter by Y and keep only the highest portion of points, initially `obb_bounds_top_keep_ratio = 0.8`.
5. Use this top-retained bounds point cloud for XZ/UV min/max to estimate OBB length and width.
6. Estimate top surface height from the top-retained points using `obb_top_y_percentile = 99.0`.
7. Build `top_corners` from the filtered footprint and top height; the lower box height is secondary and does not need to represent the full tofu body.
8. If the Y-filtered bounds set has too few points or becomes unstable, fall back to the current full-mask bounds behavior.

Initial candidate parameters:
- `obb_bounds_top_keep_ratio`: float, default candidate `0.8`, valid range `(0, 1]`; keep the highest 80% of full-mask bounds points by base Y.
- `obb_top_y_percentile`: float, default candidate `99.0`, valid range `0.0-100.0`; estimate top plane height from retained top points.

Important distinction from the rolled-back top-surface robust-bounds experiment:
- Do not use the Y-filtered points to re-estimate yaw.
- Do not introduce UV percentile bounds initially; use min/max on the Y-filtered top footprint first.
- Do not make full 3D point inclusion the success metric. The success metric is top ABCD alignment and `edge_dir` stability.

Risks:
- If top-edge points have lower Y due to depth noise, camera angle, calibration tilt, or tofu surface irregularity, keeping only the highest points can shrink the footprint inward.
- A fixed 80% ratio may not generalize across all masks and camera angles; it must remain configurable.
- If the SAM3 mask mainly covers the true top surface already, filtering may discard useful edge samples unnecessarily.

Verification plan for this refinement:
- RViz: ABCD top corners should align with the visible tofu top surface, not necessarily the full side/bottom cloud.
- Compare current full-mask bounds vs Y-filtered bounds in debug visualization before merging this refinement.
- Check Phase2 prepare target stability over at least 1 second: top-corner position jitter < 3 mm and edge_dir jitter < 0.05 rad.
- Confirm cutting alignment remains safe even if lower tofu geometry is truncated.

**Output** (identical to main path contract):
- `pose_base` (4×4 matrix in base frame)
- `top_corners_base` (4×3)
- `extents_3d` (sorted [major, height, minor] in meters)
- `angle_rad` (yaw angle of major axis from base X)

---

## Inputs

- **Raw**:
  - `/objects_with_pose` (ObjectStateArray) with binary masks and depth-synchronized.
  - `/camera/color/camera_info` (CameraInfo) for K matrix.
  - Calibration file (camera-to-base transform T_base_cam).

- **Parameters** (new):
  - `corner_mode` must be `"constrained_obb"` to activate this branch.
  - `mask_erode_px` (int, default 5)
  - `obb_margin` (float, m, default 0.003)
  - `obb_angle_step_deg` (float, default 0.5)
  - `obb_voxel_size` (float, m, default 0.002)
  - `obb_sor_nb_neighbors` (int, default 20)
  - `obb_sor_std_ratio` (float, default 1.0)
  - `obb_ror_radius` (float, m, default 0.01)
  - `obb_ror_nb_points` (int, default 8)
  - `obb_dbscan_eps` (float, m, default 0.01)
  - `obb_dbscan_min_points` (int, default 10)
  - `obb_depth_decimate_factor` (int, default 1)
  - `obb_depth_spatial_filter_d` (int, default 5)
  - `obb_depth_spatial_sigma_color` (float, default 20.0)
  - `obb_depth_spatial_sigma_space` (float, default 20.0)
  - `obb_depth_hole_fill_kernel` (int, default 3)
  - `obb_depth_median_frames` (int, default 1)

---

## Outputs

- Same as main: `/tofu_state` (TofuState) containing:
  - `pose` (6D)
  - `extents`
  - `top_corners`
  - `edge_dir`
  - `tcp_target`
  - `is_valid`
  - `confidence`
  - `object_id`

No downstream changes required; tofu_state_node and knife_prepare_action_server consume these fields unchanged.

---

## Assumptions

Physical:
- Tofu top surface is roughly parallel to base_xz plane (yaw-only variation allowed; roll/pitch negligible).
- Camera scene static; tofu not moving during perception.
- The support/stool under tofu is either removed from scene or does not interfere with tofu point cloud (or background subtraction is applied separately).

Algorithmic:
- OBB search range [0,180)° covers all reasonable placements.
- Point cloud after cleaning still contains >30 points for OBB fitting.
- `edge_dir` derived from OBB top corners remains stable (consistent with major axis orientation).

Operational:
- RealSense D435I depth noise characteristics as documented.
- Calibration T_base_cam is accurate (< 0.01 m translational error).

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| OBB search too slow (360 iterations × N points) | Frame rate drops below 5 Hz | Use vectorized operations; reduce `angle_step_deg` to 1.0 if needed; precompute trigonometric tables; limit max iterations |
| Point cloud cleaning removes too many points | Pose estimation fails | Tune cleaning parameters conservatively; fallback to AABB if cleaned points <30 |
| tofu not perfectly flat (roll/pitch present) | Constrained OBB fits poorly, extents inaccurate | Allow fallback to free PCA if residual Y deviation > threshold; or extend to full 3D OBB (future) |
| Background stool included in mask | OBB encloses stool, top_corners wrong | Use background subtraction (empty scene depth median) before OBB; or improve SAM3 mask quality |
| Multi-frame median stacking not implemented | Depth noise still affects OBB | Add stacking in tofu_state_node (buffer 20-50 frames) later |
| Open3D dependency unavailable on target robot | Cannot compile/run | Provide pure-numpy fallback for cleaning and OBB (slower but functional) |

---

## Open Questions

- Q1: Multi-frame depth median aggregation is now implemented in `pose_estimator_node`, which owns the synchronized depth stream. Future work can still move or duplicate a higher-level temporal stabilizer in `tofu_state_node` if needed.
- Q2: How to handle background subtraction? If the scene contains a fixed stool, should we compute a static background depth map and subtract? If yes, where to store/load it?
- Q3: What is the acceptable fallback strategy? Should we automatically fall back to `corner_mode="aabb"` on OBB failure, or should we keep the last valid result (with a warning)?
- Q4: Performance budget: Is 200 ms per frame acceptable? Need benchmark on target hardware (TBD): if OBB + cleaning takes >300ms, need to simplify (e.g., use 1° step, reduce point count by further voxel size).

---

## Verification Plan

**Unit tests** (offline with recorded bag files):
1. Run OBB pipeline on a dataset of tofu scenes (different placements, slight rotations).
2. Compare OBB volume vs AABB volume; expect ≥20% reduction.
3. Check `inside_ratio` = fraction of tofu points inside OBB; expect ≥0.98.
4. Check OBB top surface normal dot(base_Y) ≥ 0.995 (θ < 5°).
5. Check `edge_dir` consistency across adjacent frames (EMA smoothing) — jitter < 0.02 rad RMS.

**Integration test** (hardware):
1. Set `corner_mode="constrained_obb"` in Phase2 config.
2. Run system from Phase1 → Phase2 → Phase3.
3. Verify Phase2 prepare still succeeds (IK finds solution within 10 s).
4. Observe RViz: OBB should be tight and rotation matching tofu's long edge.
5. Check tofu_state_node outputs stable `tcp_target` and `edge_dir` (variance < 5 mm over 1 s).
6. Execute Phase3 cut; verify no collision or misalignment.

**Success criteria**:
- Phase2 prepare success rate ≥ 95% over 20 runs.
- No increase in Phase2 timeout failures.
- tofu_state outputs no抖动超出阈值（位置抖动 < 3 mm, 方向抖动 < 0.05 rad）。

---

## Merge Condition

This branch can be merged into main logic when:
1. Unit tests pass on recorded datasets (volume reduction ≥20%, inside_ratio ≥0.98, top surface within 5° of horizontal).
2. Hardware integration test passes at least 5 consecutive runs without collision or IK failure.
3. Performance measured: `get_pose_from_mask` average time < 200 ms on target robot PC.
4. Fallback logic is validated (AABB activation on OBB failure does not crash).
5. All parameters are documented in `config/config-schema.md` and `config/parameter-mapping.md`.
6. Code review: no undefined business logic left as guesses.

Upon merge, replace the `corner_mode` handling in `vision_utils.py` main path with the constrained OBB implementation as default. Keep `"aabb"` and `"pca_constrained"` as legacy options for backward compatibility.

---

## Notes

- This branch is **purely about perception**; it does not change any business logic nodes or edges beyond the internal functioning of the existing `PHASE_2_MOVE_TO_PREPARE` edge.
- The downstream `tofu_state_node` and `knife_prepare_action_server` remain untouched; they will consume the improved `top_corners` and `edge_dir` transparently.
- If the OBB approach proves superior, the main logic's `edge_2_prepare` should be updated to use `corner_mode="constrained_obb"` by default in configuration, and eventually rename `"constrained_obb"` to just `"obb"` with the constraint implied.
- Future improvements may include: background subtraction integration, 3D unconstrained OBB fallback for non-flat objects, GPU-accelerated ROR/DBSCAN, and adaptive angle step based on point count.
