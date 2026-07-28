"""Measure state/action temporal alignment across the final 13D dataset."""
from pathlib import Path
import json
import numpy as np
import pyarrow.parquet as pq

ROOT = Path("/mnt/data/gr00t-finetune/datasets/lerobot_dataset_right_o6_13d")
paths = sorted((ROOT / "data").glob("**/*.parquet"))

totals = {k: [] for k in ("action_minus_state", "action_t_plus_1_minus_state_t")}
for path in paths:
    t = pq.read_table(path, columns=["action", "observation.state"])
    action = np.vstack(t["action"].to_numpy())
    state = np.vstack(t["observation.state"].to_numpy())
    totals["action_minus_state"].append(action - state)
    totals["action_t_plus_1_minus_state_t"].append(action[1:] - state[:-1])

for label, chunks in totals.items():
    diff = np.concatenate(chunks)
    result = {
        "samples": len(diff),
        "total_mse": float(np.mean(diff**2)),
        "total_mae": float(np.mean(np.abs(diff))),
        "arm_mse": float(np.mean(diff[:, :7] ** 2)),
        "arm_mae": float(np.mean(np.abs(diff[:, :7]))),
        "hand_mse": float(np.mean(diff[:, 7:] ** 2)),
        "hand_mae": float(np.mean(np.abs(diff[:, 7:]))),
        "per_dim_mae": np.mean(np.abs(diff), axis=0).tolist(),
    }
    print(label, json.dumps(result))
