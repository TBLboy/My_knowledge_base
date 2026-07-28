"""Create a minimal, hard-linked LeRobot v2.1 subset containing episode 0."""
from pathlib import Path
import json
import os
import shutil

SRC = Path("/mnt/data/gr00t-finetune/datasets/lerobot_dataset_right_o6_13d")
DST = Path("/mnt/data/gr00t-finetune/datasets/lerobot_dataset_right_o6_13d_overfit_ep0")
EP = 0

if DST.exists():
    shutil.rmtree(DST)
(DST / "data/chunk-000").mkdir(parents=True)
(DST / "videos/chunk-000").mkdir(parents=True)
(DST / "meta").mkdir()

def link(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.link(src, dst)

link(SRC / f"data/chunk-000/episode_{EP:06d}.parquet", DST / f"data/chunk-000/episode_{EP:06d}.parquet")
for video_dir in (SRC / "videos/chunk-000").iterdir():
    link(video_dir / f"episode_{EP:06d}.mp4", DST / f"videos/chunk-000/{video_dir.name}/episode_{EP:06d}.mp4")

for name in ("tasks.jsonl", "modality.json"):
    shutil.copy2(SRC / "meta" / name, DST / "meta" / name)
episode = json.loads((SRC / "meta/episodes.jsonl").read_text().splitlines()[EP])
(DST / "meta/episodes.jsonl").write_text(json.dumps(episode) + "\n")
info = json.loads((SRC / "meta/info.json").read_text())
info["total_episodes"] = 1
info["total_frames"] = episode["length"]
info["total_videos"] = 3
info["splits"] = {"train": "0:1"}
(DST / "meta/info.json").write_text(json.dumps(info, indent=2) + "\n")
print(DST)
