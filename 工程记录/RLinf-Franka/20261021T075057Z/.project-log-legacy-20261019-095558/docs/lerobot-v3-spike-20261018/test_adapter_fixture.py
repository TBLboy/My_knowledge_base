"""Offline tests for the synthetic alignment contract."""

import json
from pathlib import Path

import numpy as np
import pytest

from adapter_fixture import (
    AlignmentError,
    SensorStream,
    align_streams,
    attach_project_metadata,
    make_fixture,
    validate_project_manifest,
)


def test_alignment_records_reuse_and_future_action(tmp_path: Path) -> None:
    result = make_fixture(tmp_path / "fixture")
    action_matches = result["matches"]["action"]
    assert len(result["grid"]) == 4
    assert all(record["abs_error_s"] <= 1 / 60 + 1e-12 for record in action_matches)
    assert sum(record["signed_offset_s"] > 0 for record in action_matches) == 4
    manifest = json.loads(result["manifest"].read_text())
    assert manifest["alignment"]["streams"]["action"]["future_match_count"] == 4


def test_equal_distance_uses_earlier_sample(tmp_path: Path) -> None:
    stream = SensorStream("tie", np.array([0.0, 2 / 30]), ("early", "late"), 15.0)
    _, matches = align_streams({"tie": stream}, duration_s=2 / 30, fps=30)
    assert matches["tie"][0]["raw_index"] == 0
    assert matches["tie"][1]["raw_index"] == 0


def test_duplicate_timestamp_tie_uses_lower_raw_index() -> None:
    stream = SensorStream("duplicate", np.array([0.0, 0.0]), ("first", "second"), 30.0)
    _, matches = align_streams({"duplicate": stream}, duration_s=1 / 30, fps=30)
    assert matches["duplicate"][0]["raw_index"] == 0


def test_reuse_is_allowed_and_recorded(tmp_path: Path) -> None:
    stream = SensorStream("slow", np.array([0.0, 2 / 30]), ("early", "late"), 15.0)
    _, matches = align_streams({"slow": stream}, duration_s=2 / 30, fps=30)
    assert matches["slow"][1]["raw_index"] == 0
    result = make_fixture(tmp_path / "fixture")
    manifest = json.loads(result["manifest"].read_text())
    assert manifest["alignment"]["streams"]["slow_state"]["reuse_count"] >= 1


def test_out_of_tolerance_and_invalid_timestamps_fail() -> None:
    with pytest.raises(AlignmentError, match="no sample within tolerance"):
        align_streams(
            {"late": SensorStream("late", np.array([0.1]), (1,), 30.0)},
            duration_s=1 / 30,
            fps=30,
        )


def test_boundary_samples_outside_tolerance_fail() -> None:
    for timestamps in (np.array([-0.1]), np.array([0.1])):
        with pytest.raises(AlignmentError, match="no sample within tolerance"):
            align_streams({"edge": SensorStream("edge", timestamps, (1,), 30.0)}, duration_s=1 / 30, fps=30)
    with pytest.raises(AlignmentError, match="non-decreasing"):
        align_streams(
            {"reset": SensorStream("reset", np.array([0.0, -0.01]), (1, 2), 30.0)},
            duration_s=1 / 30,
            fps=30,
        )


def test_boundary_does_not_extrapolate(tmp_path: Path) -> None:
    result = make_fixture(tmp_path / "fixture")
    fixed = result["matches"]["fixed"]
    assert fixed[0]["raw_timestamp_s"] == 0.0
    assert fixed[-1]["virtual_timestamp_s"] < 0.101
    assert np.allclose(np.diff(result["grid"]), 1 / 30)


def test_manifest_is_attached_and_validated(tmp_path: Path) -> None:
    result = make_fixture(tmp_path / "fixture")
    dataset = tmp_path / "dataset"
    (dataset / "meta").mkdir(parents=True)
    (dataset / "meta" / "info.json").write_text("{}")
    attach_project_metadata(dataset, result["manifest"])
    info = json.loads((dataset / "meta" / "info.json").read_text())
    assert info["custom"]["alignment_qc"] == "passed"
    assert validate_project_manifest(dataset / "meta" / "project_manifest.json")["custom"]["action_space"] == "eef_pose_absolute"


def test_missing_provenance_fails_closed(tmp_path: Path) -> None:
    result = make_fixture(tmp_path / "fixture")
    payload = json.loads(result["manifest"].read_text())
    del payload["custom"]["required_provenance"]["action"]
    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps(payload))
    with pytest.raises(AlignmentError, match="final action provenance"):
        validate_project_manifest(broken)


def test_video_qc_rejects_wrong_frame_count(tmp_path: Path) -> None:
    av = pytest.importorskip("av")
    from video_qc import inspect_video
    path = tmp_path / "one.mp4"
    container = av.open(str(path), "w")
    stream = container.add_stream("h264", 30)
    stream.width, stream.height = 8, 8
    stream.pix_fmt = "yuv420p"
    frame = av.VideoFrame(8, 8, "rgb24")
    for packet in stream.encode(frame):
        container.mux(packet)
    for packet in stream.encode():
        container.mux(packet)
    container.close()
    with pytest.raises(ValueError, match="frame count"):
        inspect_video(path, expected_frames=2, expected_fps=30)
