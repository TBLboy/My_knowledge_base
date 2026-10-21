"""Isolated sealed future-raw-v1 -> LeRobot 0.4.4 offline exporter.

This module is intentionally self contained at the project-log spike boundary:
it reads JSON only, never mutates the source artifact, and publishes through a
temporary directory so validation failures cannot leave a usable dataset.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
import math
from pathlib import Path
from typing import Any

import numpy as np

from aligner_fixture import AlignmentError, RawStream, align_raw_streams
from raw_schema_fixture import RawSchemaError, validate_raw_batch
from video_qc import VideoQCError, inspect_video


class ExportError(ValueError):
    """Input, alignment, writer, or QC contract failure."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finite_stats(value: Any) -> bool:
    if isinstance(value, list):
        return all(_finite_stats(item) for item in value)
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _streams(batch: dict[str, Any], episode: dict[str, Any]) -> tuple[dict[str, RawStream], list[float]]:
    steps = episode["steps"]
    times = [float(s["timestamp_s"]) for s in steps]
    start = float(episode.get("start_timestamp_s", times[0]))
    terminal = float(episode["terminal"]["timestamp_s"])
    if not times or terminal <= start:
        raise ExportError("episode must contain a positive-duration timeline")
    if times[0] < start or times[-1] >= terminal:
        raise ExportError("episode steps must lie in [start_timestamp_s, terminal_timestamp_s)")
    streams: dict[str, RawStream] = {
        "state": RawStream("state", times, tuple(steps), 30.0),
        "action": RawStream("action", [float(a["timestamp_s"]) for a in episode["action_samples"]], tuple(episode["action_samples"]), 30.0),
    }
    for sensor_id, sensor in batch["sensors"].items():
        if sensor_id == "state":
            continue
        # Keep future samples: nearest-neighbor matching may legally select a
        # future sample within the declared half-period tolerance.
        timestamps = [float(t) for t in sensor["timestamps_s"]]
        refs = list(sensor["sample_refs"])
        if timestamps:
            streams[sensor_id] = RawStream(sensor_id, timestamps, tuple(refs), float(sensor["declared_rate_hz"]))
    # The fixed camera defines the episode interval.  A future raw batch must
    # provide enough camera samples; this is deliberately not padded/extrapolated.
    reference = batch["reference_sensor"]
    if reference not in streams:
        raise ExportError(f"reference sensor {reference!r} is unavailable")
    return streams, times


def _frame(ref: Any, index: int, *, wrist: bool = False) -> np.ndarray:
    # The sealed fixture carries references, not decoded pixels.  This stable
    # placeholder is only for the synthetic spike; a production collector will
    # provide decoded/encoded media before this boundary.
    digest = hashlib.sha256(str(ref).encode()).digest()[0]
    value = (digest + index * 17 + (100 if wrist else 0)) % 255
    return np.full((8, 8, 3), value, dtype=np.uint8)


def select_episodes(batch: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    modes = {"standard-success-only", "standard-all", "labelled-all"}
    if mode not in modes:
        raise ExportError(f"invalid mode: {mode}")
    if mode == "standard-success-only":
        return [e for e in batch["episodes"] if e["terminal"]["outcome"] == "success"]
    if mode == "standard-all":
        return [e for e in batch["episodes"] if e["terminal"]["outcome"] in {"success", "failure"}]
    # Labels are retained for publishable outcomes only; timeout/abort remain
    # available in the sealed raw artifact and are never silently exported.
    return [e for e in batch["episodes"] if e["terminal"]["outcome"] in {"success", "failure"}]


def _qc_export(dataset: Path, *, raw_path: Path, raw_sha256: str, manifests: list[dict[str, Any]]) -> None:
    """Minimal exporter-owned fail-closed QC, before the atomic publish move."""
    try:
        import pyarrow.parquet as pq
        from lerobot.datasets.lerobot_dataset import LeRobotDataset
        info = json.loads((dataset / "meta/info.json").read_text())
        project = json.loads((dataset / "meta/project_manifest.json").read_text())
        if _sha256(raw_path) != raw_sha256:
            raise ExportError("manifest or raw hash QC failed")
        project_episodes = project.get("episodes")
        if not isinstance(project_episodes, list) or len(project_episodes) != len(manifests):
            raise ExportError("manifest episode QC failed")
        loaded = LeRobotDataset(repo_id="local/future-raw-v1", root=dataset)
        data = pq.read_table(dataset / "data/chunk-000/file-000.parquet").to_pydict()
        episodes = pq.read_table(dataset / "meta/episodes/chunk-000/file-000.parquet").to_pydict()
        tasks = pq.read_table(dataset / "meta/tasks.parquet").to_pydict()
        if len(loaded) != info["total_frames"] or len(data["index"]) != info["total_frames"]:
            raise ExportError("loader/parquet row QC failed")
        if len(episodes["episode_index"]) != len(manifests) or len(tasks["task_index"]) < 1:
            raise ExportError("episode/task range QC failed")
        if data["episode_index"] != sorted(data["episode_index"]) or data["task_index"] != sorted(data["task_index"]):
            raise ExportError("episode/task indices are not monotonic")
        if set(data["episode_index"]) != set(range(len(manifests))) or set(tasks["task_index"]) != set(range(len(tasks["task_index"]))):
            raise ExportError("episode/task index ranges invalid")
        if any(not math.isfinite(float(x)) for x in data["timestamp"]):
            raise ExportError("parquet timestamps/ranges invalid")
        episode_rows = episodes
        for row, expected in enumerate(manifests):
            indices = [i for i, value in enumerate(data["episode_index"]) if value == row]
            if not indices:
                raise ExportError("episode has no data rows")
            start, end = min(indices), max(indices) + 1
            if (episode_rows["dataset_from_index"][row] != start
                    or episode_rows["dataset_to_index"][row] != end
                    or episode_rows["length"][row] != end - start):
                raise ExportError("episode dataset range/length QC failed")
            local_frames = data["frame_index"][start:end]
            local_times = data["timestamp"][start:end]
            if local_frames != list(range(end - start)) or any(
                    abs(float(t) - i / 30) > 1e-6 for i, t in enumerate(local_times)):
                raise ExportError("episode frame/timestamp grid QC failed")
            episode_tasks = episode_rows.get("tasks")
            if not isinstance(episode_tasks, list) or len(episode_tasks[row]) != 1:
                raise ExportError("episode task metadata is missing")
            task_row = int(data["task_index"][indices[0]])
            if any(data["task_index"][i] != task_row for i in indices):
                raise ExportError("episode task index QC failed")
            task_text_column = "task" if "task" in tasks else "__index_level_0__"
            if tasks["task_index"][task_row] != task_row or tasks[task_text_column][task_row] != expected.get("task_text", ""):
                raise ExportError("task index/text consistency QC failed")
            if not isinstance(expected.get("action_matches"), list) or len(expected["action_matches"]) != len(indices):
                raise ExportError("action match records are missing")
        stats = json.loads((dataset / "meta/stats.json").read_text())
        features = info.get("features", {})
        for name, feature in features.items():
            if feature.get("dtype") in {"video", "image"}:
                continue
            entry = stats.get(name)
            if not isinstance(entry, dict):
                raise ExportError(f"missing stats for {name}")
            width = (feature.get("shape") or [1])[0]
            for key in ("min", "max", "mean", "std", "q01", "q10", "q50", "q90", "q99"):
                values = entry.get(key)
                if not isinstance(values, list) or len(values) != width or not _finite_stats(values):
                    raise ExportError(f"stats shape/finite QC failed for {name}")
            if entry.get("count") != [info["total_frames"]]:
                raise ExportError(f"stats count QC failed for {name}")
        for value in stats.values():
            for key in ("min", "max", "mean", "std"):
                if key in value:
                    if not _finite_stats(value[key]):
                        raise ExportError("non-finite stats")
        for key in ("observation.images.cam_ext_0", "observation.images.cam_wrist_right"):
            if not list((dataset / "videos" / key).glob("**/*.mp4")):
                raise ExportError(f"missing video reference: {key}")
            video = next((dataset / "videos" / key).glob("**/*.mp4"))
            try:
                details = inspect_video(video, expected_frames=info["total_frames"], expected_fps=30)
            except (OSError, VideoQCError, ValueError) as exc:
                raise ExportError(f"{key}: video QC failed: {exc}") from exc
            if details["codec"] != "h264" or details["pix_fmt"] != "yuv420p" or details["max_keyframe_gap"] > 2:
                raise ExportError(f"{key}: codec/pixfmt/GOP QC failed")
            reference = episodes
            field = f"videos/{key}/to_timestamp"
            if field not in reference or abs(float(reference[field][-1]) - details["duration_s"]) > 1e-6:
                raise ExportError(f"{key}: duration/reference QC failed")
    except ExportError:
        raise
    except Exception as exc:
        raise ExportError(f"export QC failed: {exc}") from exc


def export_batch(raw_path: Path, output: Path, *, mode: str = "standard-all") -> dict[str, Any]:
    raw_path = Path(raw_path)
    if not raw_path.is_file():
        raise ExportError(f"raw input missing: {raw_path}")
    before = _sha256(raw_path)
    try:
        batch = validate_raw_batch(json.loads(raw_path.read_text()), require_sealed=True)
    except (OSError, json.JSONDecodeError, RawSchemaError) as exc:
        raise ExportError(f"raw validation failed: {exc}") from exc
    publishable = select_episodes(batch, mode)
    if not publishable:
        raise ExportError("batch has no publishable success/failure episodes")
    if output.exists():
        raise ExportError(f"output already exists: {output}")
    parent = output.parent
    parent.mkdir(parents=True, exist_ok=True)
    # 0.4.4's create() owns root.mkdir(exist_ok=False), so reserve a unique
    # name and remove the directory before handing it to the writer.
    temp = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=parent))
    temp.rmdir()
    try:
        from lerobot.datasets.lerobot_dataset import LeRobotDataset
        import lerobot
        if getattr(lerobot, "__version__", None) != "0.4.4":
            raise ExportError("runtime must use lerobot==0.4.4")
        f32 = {"dtype": "float32", "shape": (7,), "names": ["x", "y", "z", "qx", "qy", "qz", "qw"]}
        features = {
            "observation.state.joint_position": {"dtype": "float32", "shape": (7,), "names": [f"joint_{i}" for i in range(7)]},
            "observation.state.eef_pose": f32,
            "observation.state.gripper": {"dtype": "float32", "shape": (1,), "names": ["gripper"]},
            "action.eef_pose": f32, "action.gripper": {"dtype": "float32", "shape": (1,), "names": ["gripper"]},
            "observation.images.cam_ext_0": {"dtype": "video", "shape": (3, 8, 8), "names": ["channel", "height", "width"]},
            "observation.images.cam_wrist_right": {"dtype": "video", "shape": (3, 8, 8), "names": ["channel", "height", "width"]},
        }
        ds = LeRobotDataset.create(repo_id="local/future-raw-v1", root=temp, robot_type="franka", fps=30,
                                   features=features, vcodec="h264", image_writer_processes=0, image_writer_threads=0)
        total = 0
        manifests = []
        for episode in publishable:
            streams, _ = _streams(batch, episode)
            start = float(episode.get("start_timestamp_s", 0.0))
            terminal = float(episode["terminal"]["timestamp_s"])
            grid, matches, manifest = align_raw_streams(
                streams, reference_camera=batch["reference_sensor"],
                reference_interval_s=(start, terminal))
            for i, _ in enumerate(grid):
                state = streams["state"].samples[matches["state"][i]["raw_index"]]
                action = streams["action"].samples[matches["action"][i]["raw_index"]]
                def sample(sensor: str, wrist: bool = False) -> np.ndarray:
                    record = matches[sensor][i]
                    return _frame(streams[sensor].samples[record["raw_index"]], total + i, wrist=wrist)
                ds.add_frame({
                    "observation.state.joint_position": np.asarray(state["measured_q"], np.float32),
                    "observation.state.eef_pose": np.asarray(state["measured_tcp"], np.float32),
                    "observation.state.gripper": np.asarray(state["measured_gripper"], np.float32),
                    "action.eef_pose": np.asarray(action["eef_pose"], np.float32),
                    "action.gripper": np.asarray(action["gripper"], np.float32),
                    "observation.images.cam_ext_0": sample("cam_fixed"),
                    "observation.images.cam_wrist_right": sample("cam_wrist", wrist=True),
                    "task": episode["task_text"] or batch["task_text"],
                })
            ds.save_episode()
            total += len(grid)
            manifest["episode_id"] = episode["episode_id"]
            if mode == "labelled-all":
                manifest["outcome"] = episode["terminal"]["outcome"]
            manifest["task_text"] = episode["task_text"] or batch["task_text"]
            manifest["action_matches"] = matches["action"]
            manifest["episode_interval_batch_s"] = [start, terminal]
            manifest["action_provenance"] = "per_step_final_post_guard_command"
            manifests.append(manifest)
        ds.finalize()
        info_path = temp / "meta" / "info.json"
        info = json.loads(info_path.read_text())
        info["custom"] = {
            "dataset_version": "lerobot-v3", "writer_pin": "lerobot==0.4.4",
            "action_space": "eef_pose_absolute",
            "camera_key_map": {"fixed": "observation.images.cam_ext_0", "wrist": "observation.images.cam_wrist_right"},
            "required_provenance": {"state": "measured_state_v1", "action": "final_post_guard_eef_target_v1"},
            "gripper": {"range": [0.0, 0.08], "open_direction": "increasing", "unit": "m"},
            "raw_batch_sha256": before, "raw_batch_path": str(raw_path),
            "alignment_manifests": "meta/project_manifest.json",
        }
        if mode == "labelled-all":
            info["custom"]["episode_outcomes"] = [e["terminal"]["outcome"] for e in publishable]
        info_path.write_text(json.dumps(info, indent=2) + "\n")
        project_manifest = {"schema_version": "project-v3-offline-export-1", "mode": mode, "episodes": manifests}
        (temp / "meta" / "project_manifest.json").write_text(json.dumps(project_manifest, indent=2) + "\n")
        for item in manifests:
            (temp / "meta" / f"episode-{item['episode_id']}.json").write_text(json.dumps(item, indent=2) + "\n")
        _qc_export(temp, raw_path=raw_path, raw_sha256=before, manifests=manifests)
        if _sha256(raw_path) != before:
            raise ExportError("raw input changed during export")
        shutil.move(str(temp), str(output))
        return {"status": "published", "episodes": len(publishable), "frames": total, "raw_sha256": before}
    except Exception as exc:
        shutil.rmtree(temp, ignore_errors=True)
        if isinstance(exc, ExportError):
            raise
        raise ExportError(str(exc)) from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mode", choices=("standard-success-only", "standard-all", "labelled-all"), default="standard-all")
    args = parser.parse_args()
    print(json.dumps(export_batch(args.raw, args.output, mode=args.mode), sort_keys=True))


if __name__ == "__main__":
    main()
