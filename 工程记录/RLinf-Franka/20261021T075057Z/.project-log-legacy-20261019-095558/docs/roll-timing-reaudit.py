"""Offline audit of retained passive telemetry; never connects to hardware."""
import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

root = Path(__file__).resolve().parents[2]
path = root / 'RLinf/logs/20261016-162726-realworld_collect_data_pico_single_franka/collected_data/rank_0_env_0_episode_1_step_487_success.pkl'
data = pickle.loads(path.read_bytes())  # Trusted, operator-produced local artifact.
infos = data['infos'][1:]
result = {'pickle': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'transitions': len(infos)}
for key in ('env_step_started_monotonic_ns', 'target_send_started_monotonic_ns', 'robot_read_started_monotonic_ns'):
    times = np.array([i['passive_franka_step'][key] for i in infos], dtype=np.int64)
    delta = np.diff(times) / 1e6
    result[key] = {'dt_ms_min_median_p95_max': np.percentile(delta, [0, 50, 95, 100]).tolist(), 'median_hz': float(1000 / np.median(delta))}
result['active_blocks'] = []
for lo, hi in ((24, 54), (79, 101), (121, 144)):
    block = infos[lo:hi]
    assert all(i['pico_active'] for i in block)
    target = np.array([i['passive_requested_franka_target'] for i in block])
    steps = (Rotation.from_quat(target[1:, 3:]) * Rotation.from_quat(target[:-1, 3:]).inv()).magnitude()
    delta = np.array([i['pico_rotation_delta'] for i in block])
    result['active_blocks'].append({'range': [lo, hi], 'target_increment_deg_median_p95_max': np.rad2deg(np.percentile(steps, [50, 95, 100])).tolist(), 'mapped_rotation_max_deg': float(np.rad2deg(np.linalg.norm(delta, axis=1).max()))})
print(json.dumps(result, indent=2))
