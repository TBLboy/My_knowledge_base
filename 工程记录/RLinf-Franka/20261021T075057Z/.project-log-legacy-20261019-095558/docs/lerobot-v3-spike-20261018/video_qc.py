"""Offline video/container checks for the synthetic v3 fixture."""

from __future__ import annotations

from pathlib import Path

class VideoQCError(ValueError):
    """Raised when a video stream disagrees with the v3 manifest."""


def inspect_video(
    path: Path, *, expected_frames: int, expected_fps: int, expected_size: tuple[int, int] = (8, 8)
) -> dict[str, object]:
    """Validate frame count and stream metadata without changing the video."""
    try:
        import av
    except ImportError as exc:
        raise VideoQCError("PyAV is required for video QC") from exc
    container = av.open(str(path))
    if len(container.streams.video) != 1:
        raise VideoQCError(f"{path}: expected one video stream")
    stream = container.streams.video[0]
    frames = list(container.decode(video=0))
    frame_count = len(frames)
    actual_fps = float(stream.average_rate)
    if frame_count != expected_frames:
        raise VideoQCError(f"{path}: frame count {frame_count} != {expected_frames}")
    if abs(actual_fps - expected_fps) > 1e-6:
        raise VideoQCError(f"{path}: fps {actual_fps} != {expected_fps}")
    if (stream.width, stream.height) != expected_size:
        raise VideoQCError(f"{path}: size {(stream.width, stream.height)} != {expected_size}")
    if stream.pix_fmt != "yuv420p":
        raise VideoQCError(f"{path}: pixel format {stream.pix_fmt} != yuv420p")
    if stream.codec_context.name != "h264":
        raise VideoQCError(f"{path}: unsupported codec {stream.codec_context.name}")
    if stream.time_base is None or stream.duration is None:
        raise VideoQCError(f"{path}: missing PTS/time base")
    pts = [frame.pts for frame in frames]
    if any(value is None for value in pts) or any(b <= a for a, b in zip(pts, pts[1:])):
        raise VideoQCError(f"{path}: frame PTS must be present and strictly increasing")
    duration_s = float(stream.duration * stream.time_base)
    expected_duration_s = expected_frames / expected_fps
    if abs(duration_s - expected_duration_s) > 1e-6:
        raise VideoQCError(f"{path}: duration {duration_s} != {expected_duration_s}")
    keyframes = [i for i, frame in enumerate(frames) if frame.key_frame]
    if not keyframes or keyframes[0] != 0:
        raise VideoQCError(f"{path}: first frame must be a keyframe")
    gaps = [b - a for a, b in zip(keyframes, keyframes[1:])]
    return {
        "path": str(path),
        "frames": frame_count,
        "fps": actual_fps,
        "codec": stream.codec_context.name,
        "pix_fmt": stream.pix_fmt,
        "time_base": str(stream.time_base),
        "duration_ticks": int(stream.duration),
        "pts_count": len(pts),
        "pts": pts,
        "duration_s": duration_s,
        "expected_duration_s": expected_duration_s,
        "max_keyframe_gap": max(gaps, default=frame_count),
    }
