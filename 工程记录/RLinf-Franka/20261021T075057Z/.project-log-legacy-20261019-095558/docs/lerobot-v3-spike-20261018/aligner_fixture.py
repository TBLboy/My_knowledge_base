"""Isolated, fail-closed virtual 30 Hz alignment fixture.

This module consumes the future raw-schema stream concepts only.  It has no
hardware, collector, or legacy-converter dependencies.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


class AlignmentError(ValueError):
    """The raw streams cannot satisfy the offline alignment contract."""


@dataclass(frozen=True)
class RawStream:
    sensor_id: str
    timestamps_s: Sequence[float]
    samples: Sequence[Any]
    declared_rate_hz: float

    @property
    def tolerance_s(self) -> float:
        return 0.5 / self.declared_rate_hz


def _validate_stream(stream: RawStream) -> None:
    if not stream.sensor_id:
        raise AlignmentError("sensor id is required")
    if (isinstance(stream.declared_rate_hz, bool)
            or not isinstance(stream.declared_rate_hz, (int, float))
            or not math.isfinite(stream.declared_rate_hz)
            or stream.declared_rate_hz <= 0):
        raise AlignmentError(f"{stream.sensor_id}: declared rate must be finite and positive")
    if not stream.timestamps_s or len(stream.timestamps_s) != len(stream.samples):
        raise AlignmentError(f"{stream.sensor_id}: timestamps/samples must be non-empty and equal")
    previous = -math.inf
    for timestamp in stream.timestamps_s:
        if (isinstance(timestamp, bool) or not isinstance(timestamp, (int, float))
                or not math.isfinite(timestamp) or timestamp < 0 or timestamp < previous):
            raise AlignmentError(f"{stream.sensor_id}: timestamps must be finite, nonnegative, non-decreasing")
        previous = timestamp


def align_raw_streams(
    streams: Mapping[str, RawStream],
    *,
    reference_camera: str,
    reference_interval_s: tuple[float, float] | None = None,
    fps: int = 30,
) -> tuple[list[float], dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Create a strict grid and provenance records for every sensor.

    The grid starts at unified acquisition time zero and ends on the last
    reference-camera interval grid point.  Samples are never extrapolated;
    reuse is permitted when the reused sample remains within tolerance.
    """
    if fps != 30:
        raise AlignmentError("this fixture requires strict 30Hz")
    if reference_camera not in streams:
        raise AlignmentError(f"missing reference camera: {reference_camera}")
    if not streams:
        raise AlignmentError("at least one stream is required")
    for stream_id, stream in streams.items():
        if stream_id != stream.sensor_id:
            raise AlignmentError(f"stream key does not match sensor id: {stream_id}")
        _validate_stream(stream)
    reference = streams[reference_camera]
    derived_interval = (float(reference.timestamps_s[0]), float(reference.timestamps_s[-1]))
    interval = derived_interval if reference_interval_s is None else reference_interval_s
    try:
        interval_values = tuple(float(value) for value in interval)
    except (TypeError, ValueError):
        raise AlignmentError("reference-camera interval must be finite and ordered") from None
    if (len(interval_values) != 2 or not all(math.isfinite(x) for x in interval_values)
            or interval_values[0] < 0 or interval_values[1] < interval_values[0]):
        raise AlignmentError("reference-camera interval must be finite and ordered")
    if reference_interval_s is not None and (interval_values[0] < derived_interval[0]
            or interval_values[1] > derived_interval[1]):
        raise AlignmentError("reference-camera interval must equal an interval inside the raw camera valid interval")
    if interval_values[1] < 0:
        raise AlignmentError("reference-camera interval is empty")

    if reference_interval_s is None:
        count = int(math.floor(interval_values[1] * fps + 1e-10)) + 1
        grid = [index / fps for index in range(count)]
        grid_origin = 0.0
    else:
        # Episode intervals are half-open.  The grid is batch-relative for
        # matching, while manifests also expose the episode-relative time.
        duration = interval_values[1] - interval_values[0]
        count = int(math.ceil(duration * fps - 1e-10))
        if count <= 0:
            raise AlignmentError("reference-camera interval must have positive duration")
        grid_origin = interval_values[0]
        grid = [grid_origin + index / fps for index in range(count)]
    matches: dict[str, list[dict[str, Any]]] = {}
    for stream_id, stream in streams.items():
        records: list[dict[str, Any]] = []
        for virtual_t in grid:
            candidates = [
                (abs(float(raw_t) - virtual_t), float(raw_t), index)
                for index, raw_t in enumerate(stream.timestamps_s)
                if abs(float(raw_t) - virtual_t) <= stream.tolerance_s
            ]
            if not candidates:
                raise AlignmentError(
                    f"{stream_id}: no in-range sample at t={virtual_t:.9f}; "
                    f"tolerance={stream.tolerance_s:.9f}"
                )
            # Distance first, then earlier timestamp, then lower raw index.
            _, raw_t, raw_index = min(candidates, key=lambda item: (item[0], item[1], item[2]))
            records.append({
                "virtual_timestamp_s": virtual_t - grid_origin,
                "batch_timestamp_s": virtual_t,
                "raw_index": raw_index,
                "raw_timestamp_s": raw_t,
                "signed_offset_s": raw_t - virtual_t,
                "abs_error_s": abs(raw_t - virtual_t),
                "tolerance_s": stream.tolerance_s,
                "is_future_match": raw_t > virtual_t,
            })
        matches[stream_id] = records

    manifest = {
        "schema_version": "project-v3-virtual-aligner-1",
        "timebase": "episode_relative_grid_with_batch_provenance" if reference_interval_s is not None else "batch_relative_monotonic_seconds",
        "unified_acquisition_start": grid_origin,
        "virtual_fps": 30,
        "virtual_timeline": {"start_s": 0.0, "end_s": (grid[-1] - grid_origin), "count": len(grid),
                             "batch_start_s": grid_origin, "batch_end_exclusive_s": interval_values[1]},
        "reference_camera": reference_camera,
        "reference_camera_interval_s": list(interval),
        "alignment": {
            "method": "symmetric_nearest_neighbor",
            "tolerance_rule": "half_declared_period",
            "tie_break": ["nearest_distance", "earlier_timestamp", "lower_raw_index"],
            "boundary_extrapolation": False,
            "reuse_allowed": True,
            "streams": {},
        },
        "qc": {"status": "passed", "invalid_timestamp_count": 0, "out_of_tolerance_count": 0},
    }
    for stream_id, records in matches.items():
        manifest["alignment"]["streams"][stream_id] = {
            "declared_rate_hz": streams[stream_id].declared_rate_hz,
            "tolerance_s": streams[stream_id].tolerance_s,
            "matched": len(records),
            "reuse_count": len(records) - len({r["raw_index"] for r in records}),
            "future_match_count": sum(r["is_future_match"] for r in records),
            "matches": records,
        }
    return grid, matches, manifest


def write_manifest(path: Path, manifest: Mapping[str, Any]) -> Path:
    """Write JSON provenance; callers only pass a manifest from this module."""
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return path
