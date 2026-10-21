# Copyright 2026 The RLinf Authors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""Offline contracts for experimental test1.0; no transport is opened."""

import subprocess
from pathlib import Path

import numpy as np
import pytest
from rlinf_ext.orientation_filter import OrientationFilter, validate_tau
from scipy.spatial.transform import Rotation as R


@pytest.mark.parametrize(
    "args",
    [
        ["--orientation-tau"],
        ["--orientation-tau", ".2"],
        ["--orientation-filter", "--orientation-tau", "nan"],
        ["--orientation-filter", "--orientation-tau", "0"],
        ["--orientation-filter", "--orientation-tau", "1"],
    ],
)
def test_launcher_rejects_before_preflight(args):
    result = subprocess.run(
        ["bash", str(Path(__file__).with_name("run_pico_session.sh")), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "【0/6】" not in result.stdout


@pytest.mark.parametrize("tau", [0, -1, float("nan"), float("inf"), 0.049, 0.501])
def test_tau_rejected(tau):
    with pytest.raises(ValueError):
        validate_tau(tau)


def test_exponential_release_regrip():
    f = OrientationFilter(0.2)
    np.testing.assert_array_equal(f.update([1, 0, 0], True, 1)[0], [0, 0, 0])
    np.testing.assert_allclose(
        f.update([1, 0, 0], True, 1.1)[0], [1 - np.exp(-0.5), 0, 0]
    )
    assert f.update(None, False, 1.2)[0] is None
    np.testing.assert_array_equal(f.update([2, 0, 0], True, 1.3)[0], [0, 0, 0])


@pytest.mark.parametrize("time", [1, 0.9, 1.301, float("nan")])
def test_bad_clock_requires_release(time):
    f = OrientationFilter()
    f.update([0, 0, 0], True, 1)
    assert f.update([1, 0, 0], True, time)[0] is None
    assert f.update([1, 0, 0], True, 1.4)[0] is None
    f.update(None, False, 1.5)
    assert f.update([1, 0, 0], True, 1.6)[1] == "grip-start"


@pytest.mark.parametrize("raw", [[np.nan, 0, 0], [1, 2], None, "bad"])
def test_invalid_not_passed_through(raw):
    f = OrientationFilter()
    assert f.update(raw, True, 1)[0] is None
    assert f.update([1, 0, 0], True, 1.1)[0] is None


def test_so3_wrap_equivalence_and_reversal():
    a, b = OrientationFilter(), OrientationFilter()
    for i, angle in enumerate([0, 170, 179, -179, -170, 150, 90, 0, -90]):
        raw = np.array([0, 0, np.deg2rad(angle)])
        equivalent = raw + [0, 0, 2 * np.pi]
        x = a.update(raw, True, i * 0.1)[0]
        y = b.update(equivalent, True, i * 0.1)[0]
        assert (R.from_rotvec(x) * R.from_rotvec(y).inv()).magnitude() < 1e-12
    assert x[2] < 1  # reversal follows the short arc, not an Euler wrap


def test_noncommuting_so3_formula():
    f = OrientationFilter()
    f.update([0, 0, 0], True, 0)
    first = R.from_rotvec(f.update([0.8, 0, 0], True, 0.1)[0])
    target = R.from_rotvec([0, 0.7, 0])
    expected = (
        R.from_rotvec((1 - np.exp(-0.5)) * (target * first.inv()).as_rotvec()) * first
    )
    actual = R.from_rotvec(f.update([0, 0.7, 0], True, 0.2)[0])
    assert (actual * expected.inv()).magnitude() < 1e-12


def test_registration_disabled_parity_and_passive_coexistence(monkeypatch):
    from rlinf.robotics.parts.teleop.pico import Pico, PicoDelta, PicoTcp
    from rlinf_ext import orientation_filter as module
    from rlinf_ext import register

    # Restore these global wrappers after this integration test.
    monkeypatch.setattr(PicoDelta, "on_reset", PicoDelta.on_reset)
    monkeypatch.setattr(Pico, "_reported", Pico.__dict__["_reported"])
    monkeypatch.delenv(module.ENABLE_ENV, raising=False)
    monkeypatch.setenv("RLINF_PASSIVE_TELEMETRY", "1")
    register()
    original = PicoDelta.action
    monkeypatch.setattr(PicoDelta, "action", original)
    tcp = PicoTcp.action
    register()
    assert PicoDelta.action is original
    context = {"tcp_pose": [0.5, 0, 0.2, 0, 0, 0, 1], "action_scale": [0.04, 0.3, 1]}
    reading = {
        "held": True,
        "ready": True,
        "position_delta": [0.002, -0.001, 0.003],
        "rotation_delta": [0.1, 0.04, -0.02],
        "gripper_trigger": 0.7,
    }
    base = PicoDelta(continuous_gripper=True)
    expected = original(base, reading, context)
    monkeypatch.setenv(module.ENABLE_ENV, "1")
    register()
    wrapped = PicoDelta.action
    register()
    assert PicoDelta.action is wrapped and PicoTcp.action is tcp
    clock = iter([1.0, 1.1, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1])
    monkeypatch.setattr(module.time, "monotonic", lambda: next(clock))
    device = PicoDelta(continuous_gripper=True)
    result = device.action(reading, context)
    np.testing.assert_array_equal(result.parts["arm"][:3], expected.parts["arm"][:3])
    np.testing.assert_array_equal(
        result.parts["end_effector"], expected.parts["end_effector"]
    )
    np.testing.assert_array_equal(result.parts["arm"][3:], [0, 0, 0])
    result = device.action(reading, context)
    assert result.info["pico_orientation_filter"]["version"] == "test1.0"
    np.testing.assert_array_equal(
        result.info["pico_rotation_delta"], reading["rotation_delta"]
    )
    np.testing.assert_allclose(
        result.info["passive_command_action"], result.parts["arm"]
    )
    assert (
        result.info["passive_pico_target_tcp_pose"][3]
        < R.from_rotvec(reading["rotation_delta"]).as_quat()[0]
    )
    for _ in range(2):
        result = device.action(reading, context)
        np.testing.assert_allclose(result.parts["arm"][3:], 0, atol=1e-7)
        np.testing.assert_array_equal(
            result.parts["arm"][:3], expected.parts["arm"][:3]
        )
    device.on_reset(context)
    result = device.action(reading, context)
    assert result.info["pico_orientation_filter"]["status"] == "await-release"
    device.action({**reading, "held": False, "stale": True}, context)
    result = device.action(reading, context)
    assert result.info["pico_orientation_filter"]["status"] == "grip-start"
    result = device.action({**reading, "invalid_pose": True}, context)
    np.testing.assert_allclose(result.parts["arm"][3:], 0, atol=1e-7)
    assert (
        device.action(reading, context).info["pico_orientation_filter"]["status"]
        == "await-release"
    )
