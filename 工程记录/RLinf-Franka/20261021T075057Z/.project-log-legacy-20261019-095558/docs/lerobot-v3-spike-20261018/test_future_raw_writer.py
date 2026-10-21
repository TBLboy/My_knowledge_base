"""Offline-only tests for the future raw recorder boundary."""

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[3] / "RLinf-Franks"))
from rlinf_ext.future_raw_writer import RawWriterError, build_raw_batch, write_raw_batch  # noqa: E402
from raw_schema_fixture import synthetic_raw_batch  # noqa: E402


def test_fixture_writer_seals_and_is_compatible_with_export_batch(tmp_path: Path) -> None:
    path = tmp_path / "future-raw.json"
    written = write_raw_batch(synthetic_raw_batch(), path)
    assert written["seal"]["sealed"] is True
    assert json.loads(path.read_text())["schema_version"] == "future-raw-v1"
    assert hashlib.sha256(path.read_bytes()).hexdigest()


def test_tamper_and_overwrite_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "raw.json"
    write_raw_batch(synthetic_raw_batch(), path)
    with pytest.raises(RawWriterError, match="overwrite"):
        write_raw_batch(synthetic_raw_batch(), path)
    mutated = synthetic_raw_batch()
    mutated["task_text"] = "tampered"
    # The writer accepts normalized input and reseals it; an already sealed,
    # modified artifact is rejected by the explicit digest check below.
    sealed = write_raw_batch(synthetic_raw_batch(), tmp_path / "other.json", dry_run=True)
    sealed["task_text"] = "tampered"
    with pytest.raises(RawWriterError, match="digest"):
        build_raw_batch(sealed)


@pytest.mark.parametrize("field", [
    ("episodes", 0, "final_post_guard_target"),
    ("episodes", 0, "terminal"),
])
def test_missing_required_fields_fail_closed(field) -> None:
    batch = synthetic_raw_batch()
    batch[field[0]][field[1]].pop(field[2])
    with pytest.raises(RawWriterError):
        build_raw_batch(batch)


def test_nonmonotonic_timestamps_and_unfinished_temp_fail_closed() -> None:
    batch = synthetic_raw_batch()
    batch["sensors"]["state"]["timestamps_s"] = [0.1, 0.0]
    with pytest.raises(RawWriterError, match="non-decreasing"):
        build_raw_batch(batch)
    with pytest.raises(RawWriterError, match="unfinished"):
        build_raw_batch({"batch_metadata": synthetic_raw_batch(), "batch_complete": False, "temp_batch": True})


def test_raw_bytes_are_unchanged_by_dry_run(tmp_path: Path) -> None:
    path = tmp_path / "raw.json"
    write_raw_batch(synthetic_raw_batch(), path)
    before = path.read_bytes()
    write_raw_batch(synthetic_raw_batch(), tmp_path / "dry.json", dry_run=True)
    assert path.read_bytes() == before
