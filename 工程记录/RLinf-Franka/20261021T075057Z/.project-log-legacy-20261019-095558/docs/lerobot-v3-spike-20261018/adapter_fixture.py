"""Synthetic raw alignment and LeRobot 0.4.4 adapter fixture."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class SensorStream:
    sensor_id: str
    timestamps_s: np.ndarray
    samples: tuple[Any, ...]
    declared_rate_hz: float

    def __post_init__(self) -> None:
        if not np.isfinite(self.declared_rate_hz) or self.declared_rate_hz <= 0:
            raise AlignmentError(f"{self.sensor_id}: declared rate must be positive")

    @property
    def tolerance_s(self) -> float:
        return 0.5 / self.declared_rate_hz


class AlignmentError(ValueError):
    """Raised when a stream cannot satisfy the alignment contract."""


def align_streams(
    streams: dict[str, SensorStream],
    *,
    duration_s: float | None = None,
    fps: int = 30,
    reference_sensor: str | None = None,
) -> tuple[np.ndarray, dict[str, list[dict[str, Any]]]]:
    """Align streams to a strict virtual grid using symmetric nearest-neighbor."""
    if fps <= 0:
        raise AlignmentError("fps must be positive")
    if reference_sensor is not None:
        if reference_sensor not in streams:
            raise AlignmentError(f"missing reference sensor: {reference_sensor}")
        reference = streams[reference_sensor]
        duration_s = float(reference.timestamps_s[-1])
    if duration_s is None or duration_s <= 0:
        raise AlignmentError("duration_s or a positive reference interval is required")
    count = max(1, int(np.ceil(duration_s * fps - 1e-12)))
    grid = np.arange(count, dtype=np.float64) / fps
    matches: dict[str, list[dict[str, Any]]] = {key: [] for key in streams}
    for stream in streams.values():
        timestamps = np.asarray(stream.timestamps_s, dtype=np.float64)
        if len(timestamps) != len(stream.samples) or len(timestamps) == 0:
            raise AlignmentError(f"{stream.sensor_id}: timestamps/samples mismatch or empty")
        if not np.all(np.isfinite(timestamps)) or np.any(np.diff(timestamps) < 0):
            raise AlignmentError(f"{stream.sensor_id}: timestamps must be finite and non-decreasing")
        for virtual_t in grid:
            distances = np.abs(timestamps - virtual_t)
            minimum = float(distances.min())
            if minimum > stream.tolerance_s + 1e-12:
                raise AlignmentError(
                    f"{stream.sensor_id}: no sample within tolerance at t={virtual_t:.9f}; "
                    f"error={minimum:.9f}, tolerance={stream.tolerance_s:.9f}"
                )
            # Stable tie-break: earlier timestamp, then lower raw index.
            candidates = np.flatnonzero(np.isclose(distances, minimum, rtol=0.0, atol=1e-12))
            index = int(candidates[np.argmin(timestamps[candidates])])
            matches[stream.sensor_id].append(
                {
                    "virtual_timestamp_s": float(virtual_t),
                    "raw_index": index,
                    "raw_timestamp_s": float(timestamps[index]),
                    "signed_offset_s": float(timestamps[index] - virtual_t),
                    "abs_error_s": minimum,
                    "tolerance_s": stream.tolerance_s,
                }
            )
    return grid, matches


def write_project_manifest(
    output: Path,
    *,
    streams: dict[str, SensorStream],
    matches: dict[str, list[dict[str, Any]]],
    reference_sensor: str,
    fps: int,
    source_batch: str = "synthetic-batch-001",
) -> Path:
    """Write project-owned provenance without modifying LeRobot internals."""
    output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "project-v3-spike-1",
        "source_batch": source_batch,
        "reference_sensor": reference_sensor,
        "virtual_fps": fps,
        "timebase": "batch_relative_monotonic_seconds",
        "alignment": {
            "method": "symmetric_nearest_neighbor",
            "virtual_fps": fps,
            "virtual_timeline_count": len(next(iter(matches.values()), [])),
            "tie_break": ["earlier_timestamp", "lower_raw_index"],
            "boundary_extrapolation": False,
            "streams": {
                sensor_id: {
                    "matched": len(records),
                    "reuse_count": len(records) - len({r["raw_index"] for r in records}),
                    "declared_rate_hz": streams[sensor_id].declared_rate_hz,
                    "tolerance_s": records[0]["tolerance_s"],
                    "max_abs_error_s": max(r["abs_error_s"] for r in records),
                    "future_match_count": sum(r["signed_offset_s"] > 0 for r in records),
                    "matches": records,
                }
                for sensor_id, records in matches.items()
            },
        },
        "custom": {
            "action_space": "eef_pose_absolute",
            "camera_key_map": {
                "fixed": "observation.images.cam_ext_0",
                "wrist": "observation.images.cam_wrist_right",
            },
            "required_provenance": {
                "state": "measured_state_v1",
                "action": "final_post_guard_eef_target_v1",
            },
        },
    }
    path = output / "project_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return path


def validate_project_manifest(path: Path) -> dict[str, Any]:
    """Fail closed on the project-owned alignment provenance contract."""
    manifest = json.loads(path.read_text())
    if manifest.get("custom", {}).get("action_space") != "eef_pose_absolute":
        raise AlignmentError("manifest must declare eef_pose_absolute")
    required_provenance = manifest.get("custom", {}).get("required_provenance", {})
    if required_provenance.get("state") != "measured_state_v1":
        raise AlignmentError("manifest is missing measured state provenance")
    if required_provenance.get("action") != "final_post_guard_eef_target_v1":
        raise AlignmentError("manifest is missing final action provenance")
    alignment = manifest.get("alignment", {})
    if alignment.get("method") != "symmetric_nearest_neighbor":
        raise AlignmentError("manifest alignment method is invalid")
    if not manifest.get("reference_sensor"):
        raise AlignmentError("manifest must declare a reference sensor")
    for sensor_id, stream in alignment.get("streams", {}).items():
        records = stream.get("matches")
        if not isinstance(records, list) or stream.get("matched") != len(records):
            raise AlignmentError(f"{sensor_id}: match count is inconsistent")
        if stream.get("matched", 0) <= 0 or stream.get("tolerance_s", 0) <= 0:
            raise AlignmentError(f"{sensor_id}: invalid match/tolerance provenance")
        if stream.get("declared_rate_hz", 0) <= 0:
            raise AlignmentError(f"{sensor_id}: invalid declared rate")
        if stream.get("reuse_count", -1) < 0:
            raise AlignmentError(f"{sensor_id}: invalid reuse count")
        if stream.get("future_match_count", -1) != sum(r.get("signed_offset_s", 0) > 0 for r in records):
            raise AlignmentError(f"{sensor_id}: future count is inconsistent")
        for record in records:
            required = {"virtual_timestamp_s", "raw_index", "raw_timestamp_s", "signed_offset_s", "abs_error_s", "tolerance_s"}
            if not required.issubset(record):
                raise AlignmentError(f"{sensor_id}: incomplete match record")
            if record["abs_error_s"] > record["tolerance_s"] + 1e-12:
                raise AlignmentError(f"{sensor_id}: out-of-tolerance manifest record")
    return manifest


def attach_project_metadata(dataset_root: Path, manifest_path: Path, *, qc: str = "passed") -> Path:
    """Attach project custom metadata to the generated v3 dataset."""
    info_path = dataset_root / "meta" / "info.json"
    info = json.loads(info_path.read_text())
    manifest = validate_project_manifest(manifest_path)
    info["custom"] = manifest["custom"] | {
        "project_manifest": "meta/project_manifest.json",
        "alignment_qc": qc,
    }
    attached = dataset_root / "meta" / "project_manifest.json"
    attached.write_text(manifest_path.read_text())
    info_path.write_text(json.dumps(info, indent=2) + "\n")
    return attached


def make_fixture(output: Path) -> dict[str, Any]:
    """Build alignment provenance and a reloadable 0.4.4 dataset."""
    if output.exists():
        shutil.rmtree(output)
    raw = {
        "fixed": SensorStream("fixed", np.array([0.0, 0.034, 0.067, 0.101]), tuple(range(4)), 30.0),
        "wrist": SensorStream("wrist", np.array([0.008, 0.041, 0.074, 0.108]), tuple(range(4)), 30.0),
        "action": SensorStream("action", np.array([0.012, 0.046, 0.079, 0.112]), tuple(range(4)), 30.0),
        "slow_state": SensorStream("slow_state", np.array([0.0, 2 / 30]), tuple(range(2)), 15.0),
    }
    grid, matches = align_streams(raw, fps=30, reference_sensor="fixed")
    manifest_path = write_project_manifest(
        output / "aligned", streams=raw, matches=matches, reference_sensor="fixed", fps=30
    )
    return {"grid": grid, "matches": matches, "manifest": manifest_path}
