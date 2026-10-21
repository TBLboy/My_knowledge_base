"""Focused offline tests for the future raw schema contract."""

import json
from pathlib import Path

import pytest

from raw_schema_fixture import RawSchemaError, seal_raw_batch, synthetic_raw_batch, validate_raw_batch, write_sealed_fixture


def sealed() -> dict:
    return seal_raw_batch(synthetic_raw_batch())


def test_complete_batch_has_required_provenance() -> None:
    batch = sealed()
    assert validate_raw_batch(batch)["reference_sensor"] == "cam_fixed"
    assert batch["episodes"][0]["final_post_guard_target"]["source"] == "final_post_guard_command"


def test_empty_task_text_and_all_terminal_outcomes_are_supported() -> None:
    for outcome in ("success", "failure", "timeout", "abort"):
        batch = synthetic_raw_batch()
        batch["episodes"][0]["terminal"]["outcome"] = outcome
        for key in ("success_count", "failure_count", "timeout_count", "abort_count"):
            batch["progress"][key] = int(key == f"{outcome}_count")
        assert validate_raw_batch(seal_raw_batch(batch))["task_text"] == ""


def remove_reference(b):
    b.pop("reference_sensor")


def reverse_timestamps(b):
    b["sensors"]["state"]["timestamps_s"] = [0.1, 0.0]


def nan_timestamp(b):
    b["sensors"]["state"]["timestamps_s"] = [float("nan")]


def remove_target(b):
    b["episodes"][0].pop("final_post_guard_target")


def unknown_outcome(b):
    b["episodes"][0]["terminal"]["outcome"] = "unknown"


def non_advisory(b):
    b["progress"]["advisory"] = False


def missing_terminal_source(b):
    b["episodes"][0]["terminal"].pop("source")


def invalid_capture_mode(b):
    b["capture_mode"] = "unknown"


def invalid_progress_count(b):
    b["progress"]["success_count"] = -1


@pytest.mark.parametrize("mutation, message", [
    (remove_reference, "required fields"),
    (reverse_timestamps, "non-decreasing"),
    (nan_timestamp, "finite"),
    (remove_target, "post-guard"),
    (unknown_outcome, "outcome"),
    (non_advisory, "advisory"),
    (missing_terminal_source, "outcome"),
    (invalid_capture_mode, "strings"),
    (invalid_progress_count, "nonnegative"),
])
def test_invalid_or_missing_provenance_fails_closed(mutation, message: str) -> None:
    batch = synthetic_raw_batch()
    mutation(batch)
    with pytest.raises(RawSchemaError, match=message):
        validate_raw_batch(batch, require_sealed=False)


def test_seal_digest_detects_mutation() -> None:
    batch = sealed()
    batch["task_text"] = "changed"
    with pytest.raises(RawSchemaError, match="digest"):
        validate_raw_batch(batch)


def test_writer_emits_sealed_read_only_json(tmp_path: Path) -> None:
    path = write_sealed_fixture(tmp_path / "raw.json")
    assert path.stat().st_mode & 0o222 == 0
    loaded = json.loads(path.read_text())
    assert validate_raw_batch(loaded)["schema_version"] == "future-raw-v1"
