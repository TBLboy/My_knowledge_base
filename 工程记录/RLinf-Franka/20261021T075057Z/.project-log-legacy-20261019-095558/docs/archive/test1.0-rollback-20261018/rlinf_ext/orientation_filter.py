# Copyright 2026 The RLinf Authors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Experimental test1.0 grip-gated mapped orientation filtering (no hardware I/O)."""

import math
import os
import time
from copy import deepcopy

import numpy as np
from scipy.spatial.transform import Rotation as R

VERSION = "test1.0"
ENABLE_ENV = "RLINF_PICO_ORIENTATION_FILTER"
TAU_ENV = "RLINF_PICO_ORIENTATION_TAU"
DEFAULT_TAU = 0.20
MAX_GAP = 0.30


def validate_tau(value):
    tau = float(value)
    if not math.isfinite(tau) or not 0.05 <= tau <= 0.5:
        raise ValueError("orientation tau must be finite and in [0.05, 0.5] seconds")
    return tau


class OrientationFilter:
    """SO(3) exponential lowpass; faults inhibit rotation until observed release."""

    def __init__(self, tau=DEFAULT_TAU):
        self.tau = validate_tau(tau)
        self.clear()

    def clear(self, require_release=False):
        self.rotation = R.identity()
        self.last_time = None
        self.blocked = require_release

    def update(self, raw, active, now, valid=True):
        if not active:
            self.clear()
            return None, "inactive", 0.0
        try:
            vector = np.asarray(raw, dtype=float)
            valid = valid and vector.shape == (3,) and np.isfinite(vector).all()
        except (ValueError, TypeError):
            valid = False
        if not valid or not math.isfinite(now):
            self.clear(require_release=True)
            return None, "invalid-await-release", 0.0
        if self.blocked:
            return None, "await-release", 0.0
        if self.last_time is None:
            self.last_time = now
            return self.rotation.as_rotvec(), "grip-start", 0.0
        dt = now - self.last_time
        if not 0 < dt <= MAX_GAP:
            self.clear(require_release=True)
            return None, "gap-await-release", 0.0
        alpha = -math.expm1(-dt / self.tau)
        target = R.from_rotvec(vector)
        self.rotation = (
            R.from_rotvec(alpha * (target * self.rotation.inv()).as_rotvec())
            * self.rotation
        )
        self.last_time = now
        return self.rotation.as_rotvec(), "filtered", alpha


def install_orientation_filter():
    """Wrap PicoDelta only, outside passive telemetry, once per worker process."""
    if os.getenv(ENABLE_ENV, "0") != "1":
        return
    tau = validate_tau(os.getenv(TAU_ENV, DEFAULT_TAU))
    from rlinf.robotics.parts.teleop.pico import PicoDelta
    from rlinf.utils.logging import get_logger

    if getattr(PicoDelta.action, "_orientation_filter_test1", False):
        return
    original = PicoDelta.action
    reset_original = PicoDelta.on_reset

    def action(self, reading, context):
        filt = getattr(self, "_orientation_filter", None)
        if filt is None:
            filt = self._orientation_filter = OrientationFilter(tau)
        raw = reading.get("rotation_delta")
        held = bool(reading.get("held", False))
        valid = bool(reading.get("ready", False)) and not (
            reading.get("stale", False) or reading.get("invalid_pose", False)
        )
        now = time.monotonic()
        filtered, status, alpha = filt.update(raw, held, now, valid)
        mapped = dict(reading)
        if held:
            if filtered is None:
                # Hold measured orientation, not a queued target. Do not disturb
                # the position anchor or gripper, including during fault inhibition.
                current = R.from_quat(self._measured_pose(context)[3:7])
                anchor = self._held_from[1] if self._held_from is not None else current
                filtered = (current * anchor.inv()).as_rotvec()
            mapped["rotation_delta"] = filtered
        result = original(self, mapped, context)
        # Keep the existing rich field RAW; passive target/command fields describe
        # the filtered call passed to PicoDelta, not the operator's raw target.
        result.info["pico_rotation_delta"] = deepcopy(raw)
        result.info["pico_orientation_filter"] = {
            "version": VERSION,
            "tau_s": tau,
            "max_gap_s": MAX_GAP,
            "status": status,
            "alpha": alpha,
            "monotonic_s": now,
            "raw_rotation_delta": raw.tolist()
            if isinstance(raw, np.ndarray)
            else deepcopy(raw),
            "applied_rotation_delta": filtered.tolist() if held else None,
        }
        return result

    def on_reset(self, *args, **kwargs):
        # Transport may still be held across an episode reset: require a release
        # rather than reusing its previous grip-relative delta at the new anchor.
        self._orientation_filter = OrientationFilter(tau)
        self._orientation_filter.clear(require_release=True)
        return reset_original(self, *args, **kwargs)

    action._orientation_filter_test1 = True
    PicoDelta.action = action
    PicoDelta.on_reset = on_reset
    get_logger().warning(
        "Experimental Pico orientation filter %s: tau=%ss gap=%ss",
        VERSION,
        tau,
        MAX_GAP,
    )
