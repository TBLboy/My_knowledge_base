"""Synthetic future raw-batch schema and fail-closed provenance validator.

This module is deliberately isolated from the live collectors and converters.  It
describes the artifact that a future collector would emit; it does not acquire
hardware data or prescribe control behavior.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


class RawSchemaError(ValueError):
    """Raised when a raw artifact is incomplete, inconsistent, or unsealed."""


_OUTCOMES = {"success", "failure", "timeout", "abort"}
_CAPTURE_MODES = {"aligned_10hz", "video_30hz"}


def _canonical(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _finite(value: Any, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise RawSchemaError(f"{label} must be finite numeric")


def _vector(value: Any, label: str, length: int) -> None:
    if not isinstance(value, list) or len(value) != length:
        raise RawSchemaError(f"{label} must have length {length}")
    for index, item in enumerate(value):
        _finite(item, f"{label}[{index}]")


def synthetic_raw_batch() -> dict[str, Any]:
    """Return a complete, JSON-compatible future raw batch fixture."""
    return {
        "schema_version": "future-raw-v1",
        "batch_id": "synthetic-batch-001",
        "unified_acquisition_start_monotonic": 1000.0,
        "clock_source": "monotonic_ns_host_clock",
        "task_text": "",
        "capture_mode": "video_30hz",
        "reference_sensor": "cam_fixed",
        "virtual_fps": 30,
        "alignment_policy": "symmetric_nearest_neighbor_half_period",
        "camera_mapping": {
            "cam_fixed": "observation.images.cam_ext_0",
            "cam_wrist": "observation.images.cam_wrist_right",
        },
        "sensors": {
            "state": {"sensor_id": "state", "kind": "measured_state", "source": "franka_state_read", "clock_source": "monotonic_ns_host_clock", "units": "SI", "declared_rate_hz": 30.0, "tolerance_s": 1 / 60, "timestamps_s": [0.0, 1 / 30], "sample_refs": ["state-0", "state-1"], "sample_count": 2, "first_timestamp_s": 0.0, "last_timestamp_s": 1 / 30, "valid_interval_s": [0.0, 1 / 30]},
            "cam_fixed": {"sensor_id": "cam_fixed", "kind": "rgb_video", "source": "zed_uvc_fixed", "clock_source": "monotonic_ns_host_clock", "units": "RGB", "media_path": "raw/cam_fixed.mp4", "declared_rate_hz": 30.0, "tolerance_s": 1 / 60, "timestamps_s": [0.0, 1 / 30, 2 / 30], "sample_refs": ["fixed-0", "fixed-1", "fixed-2"], "sample_count": 3, "first_timestamp_s": 0.0, "last_timestamp_s": 2 / 30, "valid_interval_s": [0.0, 2 / 30]},
            "cam_wrist": {"sensor_id": "cam_wrist", "kind": "rgb_video", "source": "zed_uvc_wrist", "clock_source": "monotonic_ns_host_clock", "units": "RGB", "media_path": "raw/cam_wrist.mp4", "declared_rate_hz": 29.0, "tolerance_s": 1 / 58, "timestamps_s": [0.002, 0.036, 0.070], "sample_refs": ["wrist-0", "wrist-1", "wrist-2"], "sample_count": 3, "first_timestamp_s": 0.002, "last_timestamp_s": 0.070, "valid_interval_s": [0.002, 0.070]},
        },
        "episodes": [
            {
            "episode_id": "episode-000",
            "start_timestamp_s": 0.0,
                "task_text": "",
                "steps": [
                    {"timestamp_s": 0.0, "measured_q": [0.0] * 7, "measured_tcp": [0.0] * 7, "measured_gripper": [0.0]},
                    {"timestamp_s": 1 / 30, "measured_q": [0.1] * 7, "measured_tcp": [0.01] * 7, "measured_gripper": [0.2]},
                ],
                "action_samples": [
                    {"timestamp_s": 0.0, "eef_pose": [0.02] * 7, "gripper": [0.2], "source": "final_post_guard_command"},
                    {"timestamp_s": 1 / 30, "eef_pose": [0.02] * 7, "gripper": [0.2], "source": "final_post_guard_command"},
                ],
                "final_post_guard_target": {"timestamp_s": 1 / 30, "eef_pose": [0.02] * 7, "gripper": [0.2], "source": "final_post_guard_command"},
                # Terminal is an exclusive boundary; the final recorded control
                # sample remains strictly before it.
                "terminal": {"outcome": "success", "timestamp_s": 2 / 30, "source": "operator_terminal_event"},
            }
        ],
        "progress": {"completed_episodes": 1, "success_count": 1, "failure_count": 0, "timeout_count": 0, "abort_count": 0, "total_episodes": 1, "advisory": True, "last_update_timestamp_s": 1 / 30},
    }


def validate_raw_batch(batch: Mapping[str, Any], *, require_sealed: bool = True) -> dict[str, Any]:
    """Validate every required contract field; never repair or infer provenance."""
    if not isinstance(batch, Mapping):
        raise RawSchemaError("batch must be an object")
    required = {"schema_version", "batch_id", "unified_acquisition_start_monotonic", "clock_source", "task_text", "capture_mode", "reference_sensor", "camera_mapping", "sensors", "episodes", "progress"}
    missing = required - set(batch)
    if missing:
        raise RawSchemaError(f"missing required fields: {sorted(missing)}")
    if batch["schema_version"] != "future-raw-v1" or not batch["batch_id"]:
        raise RawSchemaError("invalid schema version or batch id")
    _finite(batch["unified_acquisition_start_monotonic"], "unified acquisition start")
    if not isinstance(batch["task_text"], str) or batch["capture_mode"] not in _CAPTURE_MODES:
        raise RawSchemaError("task_text and capture_mode must be strings")
    if batch["clock_source"] != "monotonic_ns_host_clock":
        raise RawSchemaError("clock source must be monotonic")
    if batch.get("virtual_fps") != 30 or batch.get("alignment_policy") != "symmetric_nearest_neighbor_half_period":
        raise RawSchemaError("strict 30Hz alignment policy is required")
    sensors = batch["sensors"]
    if not isinstance(sensors, Mapping) or batch["reference_sensor"] not in sensors:
        raise RawSchemaError("reference sensor is missing from sensor streams")
    for sensor_id, stream in sensors.items():
        if not isinstance(stream, Mapping):
            raise RawSchemaError(f"{sensor_id}: stream must be an object")
        _finite(stream.get("declared_rate_hz"), f"{sensor_id} declared rate")
        _finite(stream.get("tolerance_s"), f"{sensor_id} tolerance")
        if not stream.get("kind") or not stream.get("source"):
            raise RawSchemaError(f"{sensor_id}: kind and source provenance are required")
        if stream.get("sensor_id") != sensor_id or stream.get("clock_source") != "monotonic_ns_host_clock" or not stream.get("units"):
            raise RawSchemaError(f"{sensor_id}: sensor identity/clock/units provenance is required")
        if sensor_id.startswith("cam_") and not stream.get("media_path"):
            raise RawSchemaError(f"{sensor_id}: media path is required")
        if stream["declared_rate_hz"] <= 0 or stream["tolerance_s"] <= 0:
            raise RawSchemaError(f"{sensor_id}: rate and tolerance must be positive")
        timestamps = stream.get("timestamps_s")
        refs = stream.get("sample_refs")
        if not isinstance(timestamps, list) or not timestamps:
            raise RawSchemaError(f"{sensor_id}: timestamps are required")
        if any(not isinstance(value, (int, float)) or not math.isfinite(value) for value in timestamps):
            raise RawSchemaError(f"{sensor_id}: timestamp must be finite")
        if not isinstance(refs, list) or len(refs) != len(timestamps):
            raise RawSchemaError(f"{sensor_id}: sample references are required")
        previous = -math.inf
        for timestamp in timestamps:
            _finite(timestamp, f"{sensor_id} timestamp")
            if timestamp < 0 or timestamp < previous:
                raise RawSchemaError(f"{sensor_id}: timestamps must be finite non-decreasing batch-relative values")
            previous = timestamp
        if stream.get("sample_count") not in (None, len(timestamps)):
            raise RawSchemaError(f"{sensor_id}: sample count mismatch")
        if stream.get("sample_count") != len(timestamps):
            raise RawSchemaError(f"{sensor_id}: sample count mismatch")
        if stream.get("first_timestamp_s") != timestamps[0] or stream.get("last_timestamp_s") != timestamps[-1]:
            raise RawSchemaError(f"{sensor_id}: timestamp interval mismatch")
        interval = stream.get("valid_interval_s")
        if not isinstance(interval, list) or interval != [timestamps[0], timestamps[-1]]:
            raise RawSchemaError(f"{sensor_id}: valid interval mismatch")
        if any(not isinstance(ref, str) or not ref for ref in refs):
            raise RawSchemaError(f"{sensor_id}: sample references must be nonempty strings")
    if not isinstance(batch["camera_mapping"], Mapping) or not batch["camera_mapping"]:
        raise RawSchemaError("camera mapping is required")
    if not isinstance(batch["episodes"], list) or not batch["episodes"]:
        raise RawSchemaError("episodes must be a non-empty list")
    for episode in batch["episodes"]:
        if not isinstance(episode, Mapping) or not episode.get("episode_id"):
            raise RawSchemaError("episode id is required")
        if "start_timestamp_s" not in episode:
            raise RawSchemaError("episode start timestamp is required")
        _finite(episode["start_timestamp_s"], "episode start timestamp")
        if episode["start_timestamp_s"] < 0:
            raise RawSchemaError("episode start timestamp must be nonnegative")
        if not isinstance(episode.get("task_text"), str):
            raise RawSchemaError("episode task text must be preserved")
        steps = episode.get("steps") if isinstance(episode, Mapping) else None
        if not steps:
            raise RawSchemaError("episode steps are required")
        previous_step = -math.inf
        for step in steps:
            _finite(step.get("timestamp_s"), "step timestamp")
            if step["timestamp_s"] < 0:
                raise RawSchemaError("step timestamp must be nonnegative")
            if step["timestamp_s"] < previous_step:
                raise RawSchemaError("episode step timestamps must be non-decreasing")
            previous_step = step["timestamp_s"]
            _vector(step.get("measured_q"), "measured_q", 7)
            _vector(step.get("measured_tcp"), "measured_tcp", 7)
            _vector(step.get("measured_gripper"), "measured_gripper", 1)
        actions = episode.get("action_samples")
        if not isinstance(actions, list) or len(actions) != len(steps):
            raise RawSchemaError("per-step action samples are required")
        terminal = episode.get("terminal")
        if not isinstance(terminal, Mapping) or terminal.get("outcome") not in _OUTCOMES or not terminal.get("source"):
            raise RawSchemaError("terminal outcome must be success/failure/timeout/abort")
        _finite(terminal.get("timestamp_s"), "terminal timestamp")
        if terminal["timestamp_s"] <= episode["start_timestamp_s"] or terminal["timestamp_s"] < steps[-1]["timestamp_s"]:
            raise RawSchemaError("terminal timestamp must bound episode steps")
        previous_action = -math.inf
        for action in actions:
            _finite(action.get("timestamp_s"), "action timestamp")
            if (action["timestamp_s"] < previous_action
                    or action["timestamp_s"] < episode["start_timestamp_s"]
                    or action["timestamp_s"] >= episode["terminal"]["timestamp_s"]):
                raise RawSchemaError("action timestamps must be non-decreasing and within episode bounds")
            previous_action = action["timestamp_s"]
            _vector(action.get("eef_pose"), "action eef_pose", 7)
            _vector(action.get("gripper"), "action gripper", 1)
            if action.get("source") != "final_post_guard_command":
                raise RawSchemaError("action provenance must be final post-guard command")
        target = episode.get("final_post_guard_target")
        if not isinstance(target, Mapping) or target.get("source") != "final_post_guard_command":
            raise RawSchemaError("final post-guard target provenance is required")
        _vector(target.get("eef_pose"), "final target eef_pose", 7)
        _vector(target.get("gripper"), "final target gripper", 1)
        _finite(target.get("timestamp_s"), "final target timestamp")
        if (target["timestamp_s"] < steps[0]["timestamp_s"]
                or target["timestamp_s"] >= episode["terminal"]["timestamp_s"]):
            raise RawSchemaError("final target timestamp must be within episode bounds")
    progress = batch["progress"]
    if not isinstance(progress, Mapping) or progress.get("advisory") is not True:
        raise RawSchemaError("progress must be explicitly advisory")
    for key in ("completed_episodes", "success_count", "failure_count", "timeout_count", "abort_count", "total_episodes"):
        if not isinstance(progress.get(key), int) or progress[key] < 0:
            raise RawSchemaError(f"progress {key} must be nonnegative integer")
    if progress["completed_episodes"] != len(batch["episodes"]):
        raise RawSchemaError("progress completed count mismatch")
    outcomes = [episode["terminal"]["outcome"] for episode in batch["episodes"]]
    expected_counts = {"success_count": outcomes.count("success"), "failure_count": outcomes.count("failure"), "timeout_count": outcomes.count("timeout"), "abort_count": outcomes.count("abort")}
    if any(progress[key] != value for key, value in expected_counts.items()):
        raise RawSchemaError("progress outcome counts mismatch")
    if require_sealed:
        seal = batch.get("seal")
        if not isinstance(seal, Mapping) or seal.get("sealed") is not True:
            raise RawSchemaError("raw artifact is not sealed")
        unsigned = dict(batch)
        unsigned.pop("seal", None)
        expected = hashlib.sha256(_canonical(unsigned)).hexdigest()
        if seal.get("content_sha256") != expected:
            raise RawSchemaError("sealed artifact digest mismatch")
    return copy.deepcopy(dict(batch))


def seal_raw_batch(batch: Mapping[str, Any]) -> dict[str, Any]:
    """Validate, seal, and return an independent artifact copy."""
    candidate = copy.deepcopy(dict(batch))
    candidate.pop("seal", None)
    validate_raw_batch(candidate, require_sealed=False)
    candidate["seal"] = {"sealed": True, "content_sha256": hashlib.sha256(_canonical(candidate)).hexdigest()}
    return candidate


def write_sealed_fixture(path: Path) -> Path:
    """Write a canonical sealed JSON fixture and make the artifact read-only."""
    artifact = seal_raw_batch(synthetic_raw_batch())
    path.write_bytes(_canonical(artifact))
    path.chmod(0o444)
    return path
