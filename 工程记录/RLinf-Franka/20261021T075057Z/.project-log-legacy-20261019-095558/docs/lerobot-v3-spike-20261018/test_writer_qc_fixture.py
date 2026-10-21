from pathlib import Path
import json
import pytest

from writer_qc_fixture import WriterQCError, loader_boundaries, qc_dataset, write_synthetic_dataset


def test_writer_and_qc_positive(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    raw = tmp_path / "raw.json"
    raw.write_text('{"synthetic":true}\n')
    out = write_synthetic_dataset(tmp_path / "out", raw_path=raw)
    result = qc_dataset(out, raw_path=raw)
    assert result["status"] == "passed"
    assert result["outcome"] == "success"


def test_failure_outcome_is_publishable(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    raw = tmp_path / "raw.json"
    raw.write_text("raw\n")
    out = write_synthetic_dataset(tmp_path / "out", outcome="failure", raw_path=raw)
    assert qc_dataset(out, raw_path=raw)["outcome"] == "failure"


def test_loader_boundary_is_explicit() -> None:
    boundaries = loader_boundaries()
    assert "pinned LeRobotDataset" in boundaries["strict"]
    assert "never inferred" in boundaries["labelled"]


def test_timeout_is_raw_only(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    with pytest.raises(WriterQCError, match="raw-only"):
        write_synthetic_dataset(tmp_path / "out", outcome="timeout")


def test_qc_rejects_changed_raw(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    raw = tmp_path / "raw.json"
    raw.write_text("raw-a\n")
    out = write_synthetic_dataset(tmp_path / "out", raw_path=raw)
    raw.write_text("raw-b\n")
    with pytest.raises(WriterQCError, match="raw input changed"):
        qc_dataset(out, raw_path=raw)


def test_qc_rejects_missing_provenance(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    out = write_synthetic_dataset(tmp_path / "out")
    info = json.loads((out / "meta/info.json").read_text())
    del info["custom"]["writer_pin"]
    (out / "meta/info.json").write_text(json.dumps(info))
    with pytest.raises(WriterQCError, match="provenance"):
        qc_dataset(out)


def test_qc_rejects_malformed_metadata(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    raw = tmp_path / "raw.json"
    raw.write_text("raw\n")
    out = write_synthetic_dataset(tmp_path / "out", raw_path=raw)
    info = json.loads((out / "meta/info.json").read_text())
    info["total_frames"] = 99
    (out / "meta/info.json").write_text(json.dumps(info))
    with pytest.raises(WriterQCError, match="aligned virtual timeline|totals"):
        qc_dataset(out, raw_path=raw)


def test_qc_rejects_malformed_video(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    raw = tmp_path / "raw.json"
    raw.write_text("raw\n")
    out = write_synthetic_dataset(tmp_path / "out", raw_path=raw)
    video = next((out / "videos/observation.images.cam_ext_0").glob("**/*.mp4"))
    video.write_bytes(video.read_bytes()[:16])
    with pytest.raises(WriterQCError, match="video QC"):
        qc_dataset(out, raw_path=raw)


def test_qc_rejects_alignment_length_mismatch(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    raw = tmp_path / "raw.json"
    raw.write_text("raw\n")
    out = write_synthetic_dataset(tmp_path / "out", raw_path=raw)
    manifest = json.loads((out / "meta/project_manifest.json").read_text())
    manifest["alignment"]["virtual_timeline_count"] = 99
    (out / "meta/project_manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(WriterQCError, match="aligned virtual timeline"):
        qc_dataset(out, raw_path=raw)


def test_abort_is_raw_only(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    with pytest.raises(WriterQCError, match="raw-only"):
        write_synthetic_dataset(tmp_path / "out", outcome="abort")


def test_labelled_boundary_is_not_generic_strict_loader() -> None:
    boundaries = loader_boundaries()
    assert boundaries["strict"] != boundaries["labelled"]
    assert "project manifest" in boundaries["labelled"]
