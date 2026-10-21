"""No-hardware LeRobot v3 API and video smoke spike."""
from pathlib import Path
import json, shutil
import numpy as np

from lerobot.datasets.lerobot_dataset import LeRobotDataset

from adapter_fixture import attach_project_metadata, make_fixture, validate_project_manifest
from video_qc import inspect_video

ROOT = Path(__file__).parent / "out-044"
fixture = make_fixture(Path(__file__).parent / "fixture-out")
if ROOT.exists(): shutil.rmtree(ROOT)
features = {
    "observation.state.joint_position": {"dtype":"float32", "shape":(7,), "names":["joint_0","joint_1","joint_2","joint_3","joint_4","joint_5","joint_6"]},
    "observation.state.eef_pose": {"dtype":"float32", "shape":(7,), "names":["x","y","z","qx","qy","qz","qw"]},
    "observation.state.gripper": {"dtype":"float32", "shape":(1,), "names":["gripper"]},
    "action.eef_pose": {"dtype":"float32", "shape":(7,), "names":["x","y","z","qx","qy","qz","qw"]},
    "action.gripper": {"dtype":"float32", "shape":(1,), "names":["gripper"]},
    "observation.images.cam_ext_0": {"dtype":"video", "shape":(3,8,8), "names":["channel","height","width"]},
    "observation.images.cam_wrist_right": {"dtype":"video", "shape":(3,8,8), "names":["channel","height","width"]},
}
ds = LeRobotDataset.create(repo_id="local/spike-044", root=ROOT, robot_type="franka", fps=30, features=features, vcodec="h264", image_writer_processes=0, image_writer_threads=0)
for i in range(3):
    z=np.zeros(7,dtype=np.float32); z[0]=i
    ds.add_frame({
        **{"observation.state.joint_position":z, "observation.state.eef_pose":np.array([.1,0,0,0,0,0,1],np.float32), "observation.state.gripper":np.array([.02],np.float32), "action.eef_pose":np.array([.1+i*.01,0,0,0,0,0,1],np.float32), "action.gripper":np.array([.02],np.float32)},
        "observation.images.cam_ext_0":np.full((8,8,3), i*20, np.uint8),
        "observation.images.cam_wrist_right":np.full((8,8,3), 100+i*20, np.uint8),
        "task":"synthetic task",
    })
ds.save_episode()
ds.finalize()
attach_project_metadata(ROOT, fixture["manifest"])
validate_project_manifest(ROOT / "meta" / "project_manifest.json")
video_qc = [
    inspect_video(path, expected_frames=3, expected_fps=30)
    for path in sorted((ROOT / "videos").glob("**/*.mp4"))
]
assert len(video_qc) == 2
print(json.dumps({"root":str(ROOT),"files":sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file())}, indent=2))
opened=LeRobotDataset(repo_id="local/spike-044", root=ROOT)
assert set(opened.meta.features) >= {
    "observation.state.joint_position", "observation.state.eef_pose", "observation.state.gripper",
    "action.eef_pose", "action.gripper", "observation.images.cam_ext_0",
    "observation.images.cam_wrist_right",
}
assert opened.meta.episodes.num_rows == 1
assert len(opened.meta.tasks) == 1
print("opened", len(opened), opened.meta.info.get("codebase_version"), opened.meta.info.get("fps"))
print("features", sorted(opened.meta.features))
print("episodes", opened.meta.episodes)
