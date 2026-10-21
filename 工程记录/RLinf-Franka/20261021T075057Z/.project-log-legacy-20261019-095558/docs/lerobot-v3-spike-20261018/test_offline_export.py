import hashlib
import json
from pathlib import Path

import pytest

from offline_export import ExportError, export_batch
from raw_schema_fixture import seal_raw_batch, synthetic_raw_batch


def _write(path: Path, batch: dict) -> str:
    path.write_text(json.dumps(seal_raw_batch(batch), sort_keys=True, separators=(",", ":")) + "\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_single_episode_export_is_fail_closed_and_preserves_raw(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    raw = tmp_path / "raw.json"
    digest = _write(raw, synthetic_raw_batch())
    result = export_batch(raw, tmp_path / "out")
    assert result["status"] == "published"
    assert result["episodes"] == 1
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == digest
    info = json.loads((tmp_path / "out/meta/info.json").read_text())
    assert info["custom"]["raw_batch_sha256"] == digest


def test_multi_episode_export(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    batch = synthetic_raw_batch()
    second = json.loads(json.dumps(batch["episodes"][0]))
    second["episode_id"] = "episode-001"
    second["terminal"]["outcome"] = "failure"
    batch["episodes"].append(second)
    batch["progress"].update({"completed_episodes": 2, "total_episodes": 2, "success_count": 1, "failure_count": 1})
    raw = tmp_path / "raw.json"
    _write(raw, batch)
    result = export_batch(raw, tmp_path / "out")
    assert result["episodes"] == 2


def test_export_modes_select_publishable_outcomes(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    batch = synthetic_raw_batch()
    second = json.loads(json.dumps(batch["episodes"][0]))
    second["episode_id"] = "episode-001"
    second["terminal"]["outcome"] = "failure"
    batch["episodes"].append(second)
    batch["progress"].update({"completed_episodes": 2, "total_episodes": 2, "success_count": 1, "failure_count": 1})
    raw = tmp_path / "raw.json"
    _write(raw, batch)
    result = export_batch(raw, tmp_path / "success", mode="standard-success-only")
    assert result["episodes"] == 1
    labelled = tmp_path / "labelled"
    result = export_batch(raw, labelled, mode="labelled-all")
    assert result["episodes"] == 2
    manifest = json.loads((labelled / "meta/project_manifest.json").read_text())
    assert [item["outcome"] for item in manifest["episodes"]] == ["success", "failure"]
    assert all(item["action_matches"] for item in manifest["episodes"])
    data = __import__("pyarrow.parquet").parquet.read_table(labelled / "data/chunk-000/file-000.parquet").to_pydict()
    assert data["action.eef_pose"][0] == pytest.approx([0.02] * 7)
    standard = tmp_path / "standard"
    export_batch(raw, standard, mode="standard-all")
    standard_info = json.loads((standard / "meta/info.json").read_text())
    assert "episode_outcomes" not in standard_info["custom"]


def test_nonzero_episode_start_and_terminal_are_preserved(tmp_path: Path) -> None:
    pytest.importorskip("lerobot.datasets.lerobot_dataset")
    batch = synthetic_raw_batch()
    episode = batch["episodes"][0]
    episode["start_timestamp_s"] = 0.0
    episode["terminal"]["timestamp_s"] = 2 / 30
    raw = tmp_path / "raw.json"
    _write(raw, batch)
    result = export_batch(raw, tmp_path / "out")
    assert result["frames"] == 2
    manifest = json.loads((tmp_path / "out/meta/episode-episode-000.json").read_text())
    assert manifest["episode_interval_batch_s"] == [0.0, 2 / 30]
    assert manifest["virtual_timeline"]["end_s"] == 1 / 30


def test_invalid_or_raw_only_batch_publishes_nothing(tmp_path: Path) -> None:
    raw = tmp_path / "raw.json"
    batch = synthetic_raw_batch()
    batch["episodes"][0]["terminal"]["outcome"] = "timeout"
    batch["progress"].update({"success_count": 0, "timeout_count": 1})
    _write(raw, batch)
    with pytest.raises(ExportError, match="no publishable"):
        export_batch(raw, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_tampered_seal_publishes_nothing(tmp_path: Path) -> None:
    raw = tmp_path / "raw.json"
    _write(raw, synthetic_raw_batch())
    payload = json.loads(raw.read_text())
    payload["task_text"] = "tampered"
    raw.write_text(json.dumps(payload))
    with pytest.raises(ExportError, match="raw validation"):
        export_batch(raw, tmp_path / "out")
    assert not (tmp_path / "out").exists()
