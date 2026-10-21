import math

import pytest

from aligner_fixture import AlignmentError, RawStream, align_raw_streams


def stream(name, times, rate=30.0):
    return RawStream(name, times, tuple(range(len(times))), rate)


def test_strict_grid_reference_interval_and_future_action():
    grid, matches, manifest = align_raw_streams(
        {"cam_fixed": stream("cam_fixed", [0.0, 1 / 30, 2 / 30]),
         "action": stream("action", [0.006, 0.039, 0.072])},
        reference_camera="cam_fixed",
    )
    assert grid == [0.0, 1 / 30, 2 / 30]
    assert manifest["reference_camera_interval_s"] == [0.0, 2 / 30]
    assert all(record["is_future_match"] for record in matches["action"])
    assert manifest["alignment"]["streams"]["action"]["future_match_count"] == 3


def test_late_reference_first_sample_can_match_unified_t0_within_tolerance():
    grid, matches, _ = align_raw_streams(
        {"cam_fixed": stream("cam_fixed", [0.01, 0.04333333333333333]),
         "state": stream("state", [0.008, 0.04133333333333333])},
        reference_camera="cam_fixed",
    )
    assert grid[0] == 0.0
    assert matches["cam_fixed"][0]["raw_timestamp_s"] == 0.01


def test_exact_half_period_and_non_grid_reference_end():
    tolerance = 1 / 60
    grid, _, _ = align_raw_streams(
        {"cam_fixed": stream("cam_fixed", [0.0, 1 / 30, 0.05]),
         "sensor": stream("sensor", [0.0, 1 / 30, 1 / 30 + tolerance])},
        reference_camera="cam_fixed",
    )
    assert grid == [0.0, 1 / 30]


def test_just_over_tolerance_fails_and_manifest_records_errors():
    with pytest.raises(AlignmentError, match="no in-range sample"):
        align_raw_streams(
            {"cam_fixed": stream("cam_fixed", [0.0, 1 / 30]),
             "sensor": stream("sensor", [0.0, 1 / 30 + 1 / 60 + 1e-8])},
            reference_camera="cam_fixed",
        )
    _, matches, manifest = align_raw_streams(
        {"cam_fixed": stream("cam_fixed", [0.0, 1 / 30]),
         "action": stream("action", [0.01, 0.04])},
        reference_camera="cam_fixed",
    )
    record = matches["action"][0]
    assert record["signed_offset_s"] == 0.01
    assert record["tolerance_s"] == 1 / 60
    assert manifest["qc"]["status"] == "passed"


def test_tie_breaks_earlier_then_lower_raw_index_and_reuse():
    _, matches, manifest = align_raw_streams(
        {"cam_fixed": stream("cam_fixed", [0.0, 1 / 30]),
         "slow": stream("slow", [0.0, 2 / 30], rate=15.0)},
        reference_camera="cam_fixed",
    )
    assert matches["slow"][1]["raw_index"] == 0  # equal-distance boundary tie
    assert manifest["alignment"]["streams"]["slow"]["reuse_count"] == 1


def test_invalid_timestamps_and_boundary_fail_closed():
    bad = [[math.nan], [-0.1], [0.02, -0.01]]
    for timestamps in bad:
        with pytest.raises(AlignmentError, match="timestamps"):
            align_raw_streams({"cam_fixed": stream("cam_fixed", timestamps)}, reference_camera="cam_fixed")
    with pytest.raises(AlignmentError, match="no in-range sample"):
        align_raw_streams(
            {"cam_fixed": stream("cam_fixed", [0.0, 1 / 30]),
             "wrist": stream("wrist", [0.2])},
            reference_camera="cam_fixed",
        )


def test_reference_interval_is_explicit_and_cannot_be_invented():
    with pytest.raises(AlignmentError, match="must equal"):
        align_raw_streams(
            {"cam_fixed": stream("cam_fixed", [0.0, 1 / 30])},
            reference_camera="cam_fixed",
            reference_interval_s=(0.0, 1.0),
        )
    with pytest.raises(AlignmentError, match="finite"):
        align_raw_streams(
            {"cam_fixed": stream("cam_fixed", [0.0, 1 / 30])},
            reference_camera="cam_fixed", reference_interval_s="bad",
        )


def test_duplicate_timestamp_tie_uses_lower_raw_index():
    _, matches, _ = align_raw_streams(
        {"cam_fixed": stream("cam_fixed", [0.0, 1 / 30]),
         "sensor": stream("sensor", [0.0, 1 / 30])},
        reference_camera="cam_fixed",
    )
    assert matches["sensor"][0]["raw_index"] == 0
