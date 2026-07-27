"""Per-dimension open-loop diagnostic for the custom 13D GR00T policy."""
import json
import sys

import numpy as np

sys.path.insert(0, "/home/tbl/Project/gr00t-finetune/gr00t_n1")

from examples.linkerhand_right_o6_config import linkerhand_right_o6_config
from gr00t.data.dataset.lerobot_episode_loader import LeRobotEpisodeLoader
from gr00t.data.dataset.sharded_single_step_dataset import extract_step_data
from gr00t.data.embodiment_tags import EmbodimentTag
from gr00t.data.utils import parse_observation_gr00t
from gr00t.policy.gr00t_policy import Gr00tPolicy

ROOT = "/home/tbl/Project/gr00t-finetune"
CHECKPOINT = sys.argv[1]
DATASET = sys.argv[2] if len(sys.argv) > 2 else f"{ROOT}/lerobot_dataset_right_o6_13d"
N_DENOISING_STEPS = int(sys.argv[3]) if len(sys.argv) > 3 else 4
STEPS = 100
HORIZON = 16
TAG = EmbodimentTag.NEW_EMBODIMENT
KEYS = ["right_arm", "right_o6_hand"]
NAMES = [f"right_arm_{i}" for i in range(7)] + [
    "thumb_flex", "thumb_abd", "index", "middle", "ring", "pinky"
]


def extract(frame, columns):
    return np.concatenate([np.vstack(frame[c].to_numpy()) for c in columns], axis=-1)


policy = Gr00tPolicy(embodiment_tag=TAG, model_path=CHECKPOINT, device="cuda")
policy.model.action_head.num_inference_timesteps = N_DENOISING_STEPS
loader = LeRobotEpisodeLoader(DATASET, linkerhand_right_o6_config)
traj = loader[0]
configs = dict(loader.modality_configs)
configs.pop("action")
pred = []
for step in range(0, STEPS, HORIZON):
    point = extract_step_data(traj, step, configs, TAG)
    obs = {f"state.{k}": v for k, v in point.states.items()}
    obs.update({f"video.{k}": np.array(v) for k, v in point.images.items()})
    for key in loader.modality_configs["language"].modality_keys:
        obs[key] = point.text
    action, _ = policy.get_action(parse_observation_gr00t(obs, loader.modality_configs))
    for j in range(HORIZON):
        pred.append(np.concatenate([np.atleast_1d(action[k][0][j]) for k in KEYS]))

gt = extract(traj, [f"action.{k}" for k in KEYS])[:STEPS]
state = extract(traj, [f"state.{k}" for k in KEYS])[:STEPS]
pred = np.asarray(pred)[:STEPS]
global_mean = np.asarray(json.load(open(f"{DATASET}/meta/stats.json"))["action"]["mean"])

def metrics(label, value):
    err = gt - value
    print(label, json.dumps({
        "mse": float(np.mean(err ** 2)), "mae": float(np.mean(np.abs(err))),
        "arm_mse": float(np.mean(err[:, :7] ** 2)), "arm_mae": float(np.mean(np.abs(err[:, :7]))),
        "hand_mse": float(np.mean(err[:, 7:] ** 2)), "hand_mae": float(np.mean(np.abs(err[:, 7:]))),
        "per_dim_mae": dict(zip(NAMES, np.mean(np.abs(err), axis=0).tolist())),
    }))

metrics("PRED", pred)
metrics("STATE_BASELINE", state)
metrics("GLOBAL_MEAN_BASELINE", np.broadcast_to(global_mean, gt.shape))
print("PRED_MEAN", json.dumps(dict(zip(NAMES, pred.mean(axis=0).tolist()))))
print("GT_MEAN", json.dumps(dict(zip(NAMES, gt.mean(axis=0).tolist()))))
