"""Isolated LeRobot 0.4.4 writer and fail-closed publishability QC.

This module is a synthetic spike only.  It deliberately imports LeRobot lazily so
the live RLinf environment cannot accidentally become the writer environment.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from adapter_fixture import AlignmentError, attach_project_metadata, make_fixture, validate_project_manifest
from video_qc import VideoQCError, inspect_video


class WriterQCError(ValueError):
    """Output is not publishable under the project v3 spike contract."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest_with_episode(path: Path, outcome: str) -> Path:
    if outcome not in {"success", "failure"}:
        raise WriterQCError("timeout/abort are raw-only and cannot be written to v3")
    payload = json.loads(path.read_text())
    payload["custom"].update({
        "dataset_version": "lerobot-v3",
        "writer_pin": "lerobot==0.4.4",
        "outcome_policy": "success_or_failure_only;timeout_and_abort_raw_only",
        "episode_outcome": outcome,
        "episode_terminal_source": "operator_terminal_event",
        "mp4_reference_policy": "metadata_episode_video_timestamps",
        "gripper": {"range": [0.0, 0.08], "open_direction": "increasing", "unit": "m"},
    })
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def write_synthetic_dataset(output: Path, *, outcome: str = "success", raw_path: Path | None = None) -> Path:
    """Write a semantic, two-camera, three-frame v3 dataset using 0.4.4."""
    if output.exists():
        import shutil
        shutil.rmtree(output)
    aligned = make_fixture(output.parent / "aligned")
    manifest = _manifest_with_episode(aligned["manifest"], outcome)
    # Import only when invoked by the pinned runner.
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    import lerobot
    if getattr(lerobot, "__version__", None) != "0.4.4":
        raise WriterQCError("runtime must use lerobot==0.4.4")
    import numpy as np

    f32 = {"dtype": "float32", "shape": (7,), "names": ["x", "y", "z", "qx", "qy", "qz", "qw"]}
    features = {
        "observation.state.joint_position": {"dtype": "float32", "shape": (7,), "names": [f"joint_{i}" for i in range(7)]},
        "observation.state.eef_pose": f32,
        "observation.state.gripper": {"dtype": "float32", "shape": (1,), "names": ["gripper"]},
        "action.eef_pose": f32,
        "action.gripper": {"dtype": "float32", "shape": (1,), "names": ["gripper"]},
        "observation.images.cam_ext_0": {"dtype": "video", "shape": (3, 8, 8), "names": ["channel", "height", "width"]},
        "observation.images.cam_wrist_right": {"dtype": "video", "shape": (3, 8, 8), "names": ["channel", "height", "width"]},
    }
    ds = LeRobotDataset.create(repo_id="local/t025-v3-spike", root=output, robot_type="franka", fps=30,
                               features=features, vcodec="h264", image_writer_processes=0, image_writer_threads=0)
    aligned_grid = aligned["grid"]
    for i, _ in enumerate(aligned_grid):
        pose = np.array([.1 + i * .01, 0, 0, 0, 0, 0, 1], np.float32)
        frame = {
            "observation.state.joint_position": np.full(7, i, np.float32),
            "observation.state.eef_pose": pose, "observation.state.gripper": np.array([.02], np.float32),
            "action.eef_pose": pose, "action.gripper": np.array([.02], np.float32),
            "observation.images.cam_ext_0": np.full((8, 8, 3), i * 20, np.uint8),
            "observation.images.cam_wrist_right": np.full((8, 8, 3), 100 + i * 20, np.uint8),
            "task": "synthetic v3 task",
        }
        ds.add_frame(frame)
    ds.save_episode(); ds.finalize()
    attach_project_metadata(output, manifest)
    if raw_path is not None:
        raw = Path(raw_path)
        if not raw.is_file():
            raise WriterQCError(f"raw input missing: {raw}")
        info = json.loads((output / "meta/info.json").read_text())
        info["custom"]["raw_batch_sha256"] = _sha256(raw)
        info["custom"]["raw_batch_path"] = str(raw)
        (output / "meta/info.json").write_text(json.dumps(info, indent=2) + "\n")
    return output


def qc_dataset(dataset: Path, *, raw_path: Path | None = None) -> dict[str, Any]:
    """Validate schema, provenance, semantic features, videos and raw immutability."""
    try:
        import lerobot
        if getattr(lerobot, "__version__", None) != "0.4.4":
            raise WriterQCError("runtime must use lerobot==0.4.4")
        info = json.loads((dataset / "meta/info.json").read_text())
        manifest = validate_project_manifest(dataset / "meta/project_manifest.json")
    except (OSError, KeyError, json.JSONDecodeError, AlignmentError) as exc:
        raise WriterQCError(f"metadata/provenance invalid: {exc}") from exc
    if info.get("codebase_version") != "v3.0" or info.get("fps") != 30:
        raise WriterQCError("v3 metadata/fps invalid")
    custom = info.get("custom", {})
    required = {"action_space", "camera_key_map", "required_provenance", "writer_pin", "episode_outcome", "gripper", "raw_batch_sha256"}
    if not required <= custom.keys() or custom["writer_pin"] != "lerobot==0.4.4":
        raise WriterQCError("required custom provenance is missing")
    if custom["episode_outcome"] not in {"success", "failure"}:
        raise WriterQCError("non-publishable episode outcome")
    if custom["action_space"] != "eef_pose_absolute":
        raise WriterQCError("action_space must be eef_pose_absolute")
    if custom["camera_key_map"] != {"fixed": "observation.images.cam_ext_0", "wrist": "observation.images.cam_wrist_right"}:
        raise WriterQCError("camera mapping is invalid")
    if custom["gripper"] != {"range": [0.0, 0.08], "open_direction": "increasing", "unit": "m"}:
        raise WriterQCError("gripper metadata is invalid")
    alignment = manifest.get("alignment", {})
    if alignment.get("virtual_fps") != 30 or alignment.get("virtual_timeline_count") != info.get("total_frames"):
        raise WriterQCError("dataset rows are not bound to aligned virtual timeline")
    for stream in alignment.get("streams", {}).values():
        if stream.get("matched") != info.get("total_frames") or stream.get("reuse_count", -1) < 0:
            raise WriterQCError("alignment manifest does not match dataset length")
    if custom.get("raw_batch_path") is None:
        raise WriterQCError("raw batch provenance is required")
    if raw_path is None or custom.get("raw_batch_sha256") != _sha256(Path(raw_path)):
        raise WriterQCError("raw input changed after writer run")
    features = info.get("features", {})
    expected_features = {
        "observation.state.joint_position": ("float32", [7], [f"joint_{i}" for i in range(7)]),
        "observation.state.eef_pose": ("float32", [7], ["x", "y", "z", "qx", "qy", "qz", "qw"]),
        "observation.state.gripper": ("float32", [1], ["gripper"]),
        "action.eef_pose": ("float32", [7], ["x", "y", "z", "qx", "qy", "qz", "qw"]),
        "action.gripper": ("float32", [1], ["gripper"]),
        "observation.images.cam_ext_0": ("video", [3, 8, 8], ["channel", "height", "width"]),
        "observation.images.cam_wrist_right": ("video", [3, 8, 8], ["channel", "height", "width"]),
    }
    expected_names = set(expected_features) | {"timestamp", "frame_index", "episode_index", "index", "task_index"}
    if set(features) != expected_names:
        raise WriterQCError("feature names do not match strict v3 profile")
    for key, (dtype, shape, names) in expected_features.items():
        actual = features[key]
        if (actual.get("dtype"), actual.get("shape"), actual.get("names")) != (dtype, shape, names):
            raise WriterQCError(f"{key}: feature dtype/shape/names mismatch")
    required_features = {"observation.state.eef_pose", "observation.state.gripper", "action.eef_pose", "action.gripper",
                         "observation.images.cam_ext_0", "observation.images.cam_wrist_right"}
    if not required_features <= features.keys():
        raise WriterQCError("semantic state/action/gripper/camera features missing")
    # Strict boundary: the pinned generic loader must reload the v3 layout; the
    # project-labelled fields above are checked separately and are not inferred.
    try:
        from lerobot.datasets.lerobot_dataset import LeRobotDataset
        loaded = LeRobotDataset(repo_id="local/t025-v3-spike", root=dataset)
        if len(loaded) != info.get("total_frames") or loaded.meta.episodes.num_rows != info.get("total_episodes"):
            raise WriterQCError("strict loader reload count mismatch")
        if len(loaded.meta.tasks) != info.get("total_tasks"):
            raise WriterQCError("strict loader task reload mismatch")
    except WriterQCError:
        raise
    except Exception as exc:
        raise WriterQCError(f"strict loader reload failed: {exc}") from exc
    _qc_parquet_contract(dataset, info, expected_features)
    for key in ("observation.images.cam_ext_0", "observation.images.cam_wrist_right"):
        if features[key].get("dtype") != "video":
            raise WriterQCError(f"{key}: video feature required")
        videos = sorted((dataset / "videos" / key).glob("**/*.mp4"))
        if len(videos) != 1:
            raise WriterQCError(f"{key}: exactly one MP4 reference required")
        try:
            details = inspect_video(videos[0], expected_frames=info["total_frames"], expected_fps=30)
        except (OSError, VideoQCError, ValueError) as exc:
            raise WriterQCError(f"{key}: video QC failed: {exc}") from exc
        reference = _episode_video_reference(dataset, key)
        if details["max_keyframe_gap"] > 2 or abs(details["duration_s"] - (reference["to_timestamp"] - reference["from_timestamp"])) > 1e-6:
            raise WriterQCError(f"{key}: GOP/duration/reference QC failed")
    for rel in ("data/chunk-000/file-000.parquet", "meta/episodes/chunk-000/file-000.parquet", "meta/tasks.parquet", "meta/stats.json"):
        if not (dataset / rel).is_file():
            raise WriterQCError(f"required v3 artifact missing: {rel}")
    if raw_path is not None and custom.get("raw_batch_sha256") != _sha256(Path(raw_path)):
        raise WriterQCError("raw input changed after writer run")
    return {"status": "passed", "frames": info["total_frames"], "manifest": manifest["schema_version"], "outcome": custom["episode_outcome"]}


def _read_table(path: Path):
    try:
        import pyarrow.parquet as pq
        return pq.read_table(path)
    except Exception as exc:
        raise WriterQCError(f"cannot read parquet {path}: {exc}") from exc


def _qc_parquet_contract(dataset: Path, info: dict[str, Any], expected_features: dict[str, tuple[Any, ...]]) -> None:
    data = _read_table(dataset / "data/chunk-000/file-000.parquet")
    episodes = _read_table(dataset / "meta/episodes/chunk-000/file-000.parquet")
    tasks = _read_table(dataset / "meta/tasks.parquet")
    rows = info["total_frames"]
    if data.num_rows != rows or episodes.num_rows != info["total_episodes"] or tasks.num_rows != info["total_tasks"]:
        raise WriterQCError("info totals do not match parquet row counts")
    expected_columns = set(expected_features) - {"observation.images.cam_ext_0", "observation.images.cam_wrist_right"} | {"timestamp", "frame_index", "episode_index", "index", "task_index"}
    if set(data.column_names) != expected_columns:
        raise WriterQCError("data parquet columns do not match strict profile")
    expected_types = {"observation.state.joint_position": "fixed_size_list<element: float>[7]", "observation.state.eef_pose": "fixed_size_list<element: float>[7]", "action.eef_pose": "fixed_size_list<element: float>[7]", "observation.state.gripper": "float", "action.gripper": "float", "timestamp": "float", "frame_index": "int64", "episode_index": "int64", "index": "int64", "task_index": "int64"}
    for name, expected in expected_types.items():
        if str(data.schema.field(name).type) != expected:
            raise WriterQCError(f"{name}: parquet dtype mismatch")
    columns = data.to_pydict()
    if columns["frame_index"] != list(range(rows)) or columns["index"] != list(range(rows)) or columns["episode_index"] != [0] * rows or columns["task_index"] != [0] * rows:
        raise WriterQCError("frame/episode/task/index ranges invalid")
    if any(not isinstance(value, (int, float)) or not __import__("math").isfinite(value) for value in columns["timestamp"]):
        raise WriterQCError("timestamps must be finite")
    if columns["timestamp"] != sorted(columns["timestamp"]):
        raise WriterQCError("timestamps must be monotonic")
    if columns["timestamp"][0] != 0.0 or any(abs(b - a - 1 / 30) > 1e-6 for a, b in zip(columns["timestamp"], columns["timestamp"][1:])):
        raise WriterQCError("timestamps must be strict 30Hz episode-relative grid")
    episode = episodes.to_pydict()
    if episode["episode_index"] != [0] or episode["length"] != [rows] or episode["dataset_from_index"] != [0] or episode["dataset_to_index"] != [rows]:
        raise WriterQCError("episode range/length metadata invalid")
    if tasks.to_pydict().get("task_index") != [0]:
        raise WriterQCError("task index range invalid")
    stats = json.loads((dataset / "meta/stats.json").read_text())
    stat_keys = {"min", "max", "mean", "std", "count", "q01", "q10", "q50", "q90", "q99"}
    for name, feature in expected_features.items():
        if feature[0] in {"video", "image"}:
            continue
        if name not in stats or set(stats[name]) != stat_keys or stats[name]["count"] != [rows]:
            raise WriterQCError(f"{name}: stats required keys/count invalid")
        for key in stat_keys - {"count"}:
            values = stats[name][key]
            if not isinstance(values, list) or not values or any(not isinstance(v, (int, float)) or not __import__("math").isfinite(v) for v in values):
                raise WriterQCError(f"{name}: stats values invalid")


def _episode_video_reference(dataset: Path, key: str) -> dict[str, float]:
    table = _read_table(dataset / "meta/episodes/chunk-000/file-000.parquet").to_pydict()
    try:
        return {"from_timestamp": float(table[f"videos/{key}/from_timestamp"][0]), "to_timestamp": float(table[f"videos/{key}/to_timestamp"][0])}
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise WriterQCError(f"{key}: missing episode video reference") from exc


def loader_boundaries() -> dict[str, str]:
    return {"strict": "pinned LeRobotDataset reload plus schema/layout checks", "labelled": "project manifest, outcome and provenance; never inferred by generic loader"}
