# Copyright 2026 The RLinf Authors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Offline trusted-local-pickle replay, not robot prediction or control."""

import argparse
import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
from rlinf_ext.orientation_filter import OrientationFilter
from scipy.spatial.transform import Rotation as R


def replay(path):
    payload = Path(path).read_bytes()
    infos = pickle.loads(payload)["infos"][1:]  # Only trusted operator-created input.
    results = {"sha256": hashlib.sha256(payload).hexdigest(), "candidates": []}
    for tau in (0.1, 0.2, 0.3):
        f = OrientationFilter(tau)
        errors, raw_steps, filtered_steps = [], [], []
        previous = None
        statuses = {}
        for info in infos:
            now = info["passive_command_computed_monotonic_ns"] / 1e9
            raw = info["pico_rotation_delta"]
            active = bool(info["pico_active"])
            out, status, _ = f.update(
                raw,
                active,
                now,
                not (info.get("pico_stale") or info.get("pico_invalid_pose")),
            )
            statuses[status] = statuses.get(status, 0) + 1
            if out is None:
                previous = None
                continue
            r, y = R.from_rotvec(raw), R.from_rotvec(out)
            errors.append((r * y.inv()).magnitude())
            if previous is not None:
                raw_steps.append((r * previous[0].inv()).magnitude())
                filtered_steps.append((y * previous[1].inv()).magnitude())
            previous = r, y
        results["candidates"].append(
            {
                "tau_s": tau,
                "statuses": statuses,
                "raw_step_deg_p50_p95_max": np.rad2deg(
                    np.percentile(raw_steps, [50, 95, 100])
                ).tolist(),
                "filtered_step_deg_p50_p95_max": np.rad2deg(
                    np.percentile(filtered_steps, [50, 95, 100])
                ).tolist(),
                "tracking_lag_deg_p50_p95_max": np.rad2deg(
                    np.percentile(errors, [50, 95, 100])
                ).tolist(),
            }
        )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trusted_pickle")
    print(json.dumps(replay(parser.parse_args().trusted_pickle), indent=2))
