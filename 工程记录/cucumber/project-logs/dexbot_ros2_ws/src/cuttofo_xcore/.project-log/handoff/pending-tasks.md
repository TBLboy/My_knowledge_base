# Pending Tasks

## Phase 2 (Business Logic Verification)

- [ ] Check `business-logic.md` content against current code for accuracy
- [ ] Verify Phase7 logic is correctly documented
- [ ] Verify Phase3/5 cutting logic matches current implementation
- [ ] Verify Phase2 prepare geometry matches `tofu_geometry.py`

## Phase 7

- [x] Phase7 implementation complete (2026-05-17)
- [x] Impedance fallback bug fixed (2026-05-17)
- [ ] Tune Phase7 config parameters (speeds, distances) on hardware

## SAM3 Point Prompt

- [ ] Implement user-drawn box feature in `camera_viewer_node.py`
- [ ] Implement `sam3_detector_node.py` box prompt handling
- [ ] Test: click on tofu → orange mask → updated /tofu_state

## Calibration

- [x] stability_threshold relaxed to 5mm
- [x] stability_rot_threshold_deg relaxed to 2°
- [x] min_frames increased to 15
- [ ] Regular hand-eye calibration quality check
